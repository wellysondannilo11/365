from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import time
from typing import Iterable
import urllib.error
import urllib.request


@dataclass(frozen=True)
class SourceAttempt:
    source_id: str
    url: str
    status: str
    bytes_written: int
    sha256: str | None
    error: str | None
    started_at_utc: str
    finished_at_utc: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_streaming(
    source_id: str,
    url: str,
    output: Path,
    *,
    timeout: int = 30,
    retries: int = 2,
    backoff_seconds: float = 1.0,
) -> SourceAttempt:
    """Download bytes incrementally; never synthesize timestamps or data."""
    output.parent.mkdir(parents=True, exist_ok=True)
    last_error: str | None = None
    started = datetime.now(timezone.utc).isoformat()
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "RoboDaBet-Cycle18/1.0", "Accept": "*/*"},
            )
            with urllib.request.urlopen(request, timeout=timeout) as response, output.open("wb") as target:
                while True:
                    chunk = response.read(4 * 1024 * 1024)
                    if not chunk:
                        break
                    target.write(chunk)
            digest = sha256_file(output)
            return SourceAttempt(
                source_id, url, "MATERIALIZED", output.stat().st_size, digest,
                None, started, datetime.now(timezone.utc).isoformat(),
            )
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if output.exists():
                output.unlink()
            if attempt < retries:
                time.sleep(backoff_seconds * (2**attempt))
    return SourceAttempt(
        source_id, url, "FAILED", 0, None, last_error, started,
        datetime.now(timezone.utc).isoformat(),
    )


def source_registry() -> list[dict[str, object]]:
    return [
        {
            "source_id": "BEATTHEBOOKIE_ODDS_SERIES",
            "url": "https://github.com/Lisandro79/BeatTheBookie",
            "status": "PUBLIC_DATA_LINKED_BUT_BYTES_NOT_PRESENT",
            "timestamp_field": "odds_datetime",
            "match_time_field": "matches.date",
            "bookmaker_field": "odds_history.bookmaker",
            "notes": "Repository documents odds_series and odds_series_b SQL/series downloads; data files are external to the repo.",
        },
        {
            "source_id": "HF_FABUL0US_MATCH_ODDS",
            "url": "https://huggingface.co/datasets/fabul0us/football_odds_2023-24",
            "status": "PUBLIC_DATASET_TIMESTAMPED_BUT_BOOKMAKER_SCHEMA_UNCONFIRMED",
            "timestamp_fields": ["1X2 timestamp", "DC timestamp", "G/NG timestamp", "U/O 2.5 timestamp"],
            "notes": "Dataset card documents repeated pre-match collection; the published viewer also reports schema inconsistency across files.",
        },
        {
            "source_id": "SHARPAPI_PUBLIC_SAMPLE",
            "url": "https://raw.githubusercontent.com/Sharp-API/sports-odds-sample-data/main/data/worldcup_2026_odds_snapshot.csv",
            "status": "STATIC_SAMPLE",
            "notes": "Not sufficient for H005 unless both Bet365 and Average are present for the same event/market/time state.",
        },
        {
            "source_id": "THE_ODDS_API_HISTORICAL",
            "url": "https://the-odds-api.com/historical-odds-data.html",
            "status": "CREDENTIAL_DEPENDENT",
            "notes": "Historical endpoint requires account/API access; no credentials are stored by this cycle.",
        },
        {
            "source_id": "BETFAIR_HISTORICAL",
            "url": "https://historicdata.betfair.com/",
            "status": "CREDENTIAL_DEPENDENT",
            "notes": "Historical data access is account/licence dependent.",
        },
    ]


def attempts_to_json(attempts: Iterable[SourceAttempt]) -> list[dict[str, object]]:
    return [asdict(item) for item in attempts]
