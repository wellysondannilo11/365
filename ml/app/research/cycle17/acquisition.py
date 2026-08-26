from __future__ import annotations
import hashlib
import json
import os
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AcquisitionAttempt:
    source_id: str
    url: str
    status: str
    bytes_written: int
    sha256: str | None
    error: str | None
    started_at_utc: str
    finished_at_utc: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_source(source_id: str, url: str, output: Path, timeout: int = 20) -> AcquisitionAttempt:
    from datetime import datetime, timezone
    start = datetime.now(timezone.utc).isoformat()
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "RoboDaBet-Cycle17/1.0"})
        with urllib.request.urlopen(request, timeout=timeout) as response, output.open("wb") as target:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                target.write(chunk)
        digest = _sha256(output)
        end = datetime.now(timezone.utc).isoformat()
        return AcquisitionAttempt(source_id, url, "MATERIALIZED", output.stat().st_size, digest, None, start, end)
    except Exception as exc:
        if output.exists():
            output.unlink()
        end = datetime.now(timezone.utc).isoformat()
        return AcquisitionAttempt(source_id, url, "FAILED", 0, None, f"{type(exc).__name__}: {exc}", start, end)


def default_source_registry() -> list[dict[str, object]]:
    return [
        {"source_id": "HF_FABUL0US_MATCH_ODDS", "url": "https://huggingface.co/datasets/fabul0us/football_odds_2023-24/resolve/main/match_odds.csv", "requires_credentials": False, "timestamp_fields": ["1X2 timestamp", "DC timestamp", "G/NG timestamp", "U/O 2.5 timestamp"]},
        {"source_id": "SHARPAPI_SAMPLE_WORLDCUP", "url": "https://raw.githubusercontent.com/Sharp-API/sports-odds-sample-data/main/data/worldcup_2026_odds_snapshot.csv", "requires_credentials": False, "timestamp_fields": ["timestamp"], "event_time_field": "event_start_time", "note": "Static public snapshot; exact-PIT candidate for events whose event_start_time is after timestamp. Not a time-series history and not sufficient by itself for H005 unless Bet365+Average opening are both present."},
        {"source_id": "SHARPAPI_LIVE_API", "url": "https://api.sharpapi.io/api/v1/odds?league=soccer", "requires_credentials": True, "timestamp_fields": ["timestamp"], "event_time_field": "event_start_time"},
        {"source_id": "SPORTMONKS_HISTORICAL_ODDS", "url": "https://api.sportmonks.com/v3/football/odds/premium/history", "requires_credentials": True, "timestamp_fields": ["bookmaker_update"], "event_time_field": "starting_at"},
        {"source_id": "BEATTHEBOOKIE_REPO", "url": "https://github.com/Lisandro79/BeatTheBookie", "requires_credentials": False, "timestamp_fields": ["odds_datetime"]},
        {"source_id": "BEATTHEBOOKIE_DATA_SERVICE", "url": "https://data-service.beatthebookie.blog/data", "requires_credentials": True, "timestamp_fields": []},
        {"source_id": "THE_ODDS_API_HISTORICAL", "url": "https://api.the-odds-api.com/v4/historical/sports/soccer_epl/odds", "requires_credentials": True, "timestamp_fields": ["timestamp"]},
        {"source_id": "BETFAIR_HISTORICAL", "url": "https://historicdata.betfair.com/", "requires_credentials": True, "timestamp_fields": ["publishTime"]},
    ]


def registry_json() -> str:
    return json.dumps(default_source_registry(), indent=2, ensure_ascii=False)
