from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, os, socket, urllib.request

@dataclass
class SourceAttempt:
    source: str
    classification: str
    target: str
    status: str
    reason: str
    started_at: str
    ended_at: str
    artifact: str | None = None
    sha256: str | None = None
    bytes: int | None = None

SOURCE_MATRIX = [
    {"source": "The Odds API", "classification": "A", "target": "provider timestamped historical bookmaker snapshots", "requirement": "paid historical access + API key"},
    {"source": "Betfair Historical Data", "classification": "A", "target": "timestamped exchange back/lay/volume data", "requirement": "purchased historical package"},
    {"source": "Football-Data.co.uk", "classification": "B/C", "target": "historical results/stats + pre-closing/closing odds", "requirement": "network; odds timestamps are bounded, not provider-native PIT"},
    {"source": "StatsBomb Open Data", "classification": "C/D", "target": "football event/lineup features", "requirement": "public dataset"},
    {"source": "Flashscore", "classification": "D", "target": "complementary context", "requirement": "lawful reproducible access; no bypass"},
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: str | Path) -> tuple[str, int]:
    h = hashlib.sha256(); size = 0
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            size += len(chunk); h.update(chunk)
    return h.hexdigest(), size


def network_probe(url='https://www.football-data.co.uk/data.php', timeout=8):
    started = utc_now()
    try:
        urllib.request.urlopen(url, timeout=timeout).read(64)
        return {"status": "PASS", "reason": "NETWORK_REACHABLE", "started_at": started, "ended_at": utc_now()}
    except Exception as exc:
        return {"status": "FAIL", "reason": f"{type(exc).__name__}:{exc}", "started_at": started, "ended_at": utc_now()}


def _download(url: str, destination: Path, timeout=30, headers=None):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'RoboDaBet/V18'})
    with urllib.request.urlopen(req, timeout=timeout) as r, destination.open('wb') as f:
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk: break
            f.write(chunk)


def acquire_url(source, classification, target, url, destination, timeout=30, env_key=None) -> SourceAttempt:
    started = utc_now(); destination = Path(destination); destination.parent.mkdir(parents=True, exist_ok=True)
    if env_key and not os.getenv(env_key):
        return SourceAttempt(source, classification, target, 'NOT_AVAILABLE', f'MISSING_CREDENTIAL:{env_key}', started, utc_now())
    try:
        _download(url, destination, timeout=timeout)
        digest, size = sha256_file(destination)
        return SourceAttempt(source, classification, target, 'PASS', 'DOWNLOADED_RAW_ARTIFACT', started, utc_now(), str(destination), digest, size)
    except Exception as exc:
        return SourceAttempt(source, classification, target, 'NOT_EXECUTED', f'{type(exc).__name__}:{exc}', started, utc_now())


def acquire_football_data(season_codes, league_codes, raw_dir):
    attempts=[]; raw=Path(raw_dir); raw.mkdir(parents=True, exist_ok=True)
    for season in season_codes:
        for league in league_codes:
            url=f'https://www.football-data.co.uk/mmz4281/{season}/{league}.csv'
            dest=raw / f'football_data_{season}_{league}.csv'
            attempts.append(acquire_url('Football-Data.co.uk','B/C','historical results/stats/pre-closing+closing odds',url,dest))
    return attempts


def write_manifest(path, attempts, network=None):
    payload={
        'version':'V18', 'created_at':utc_now(), 'network_probe':network,
        'source_matrix':SOURCE_MATRIX,
        'attempts':[asdict(a) for a in attempts],
        'fail_closed_policy':'Only class A provider-native timestamped odds may enter strict PIT betting research. B/C odds remain secondary unless independently timestamped.',
    }
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8'); return p
