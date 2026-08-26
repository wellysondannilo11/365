from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


@dataclass(frozen=True)
class AcquisitionAttempt:
    source: str
    url: str
    status: str
    error: str | None = None
    bytes: int = 0
    sha256: str | None = None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def candidate_urls(season_code: str, league_code: str = "E0") -> list[tuple[str, str]]:
    """Return ordered public football routes.

    The DataHub route is a mirror of football-data.co.uk match statistics/results.
    It is intentionally a fallback: source provenance remains explicit and the
    caller must not label rows REAL until the bytes are actually loaded and
    quality/PIT gates pass.
    """
    season_code = str(season_code)
    league_code = str(league_code)
    urls = [
        (
            "football-data.co.uk",
            f"https://www.football-data.co.uk/mmz4281/{season_code}/{league_code}.csv",
        ),
    ]
    if league_code.upper() == "E0":
        urls.append(
            (
                "datahub-football-data-mirror",
                f"https://datahub.io/football/english-premier-league/_r/-/season-{season_code}.csv",
            )
        )
    return urls


def acquire_first_available(
    season_code: str,
    league_code: str = "E0",
    timeout: int = 30,
    out_dir: str | Path = "data/raw/football_data",
) -> tuple[pd.DataFrame, list[AcquisitionAttempt]]:
    """Try public historical football routes until real bytes are obtained.

    No synthetic fallback is permitted. A failure across all candidates raises
    RuntimeError and returns the complete attempt log in the exception text.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    attempts: list[AcquisitionAttempt] = []
    headers = {"User-Agent": "RoboDaBet/EmpiricalResearch"}

    for source, url in candidate_urls(season_code, league_code):
        try:
            r = requests.get(url, timeout=timeout, headers=headers)
            r.raise_for_status()
            content = bytes(r.content)
            if not content.strip():
                raise ValueError("EMPTY_RESPONSE")
            digest = _sha256(content)
            attempts.append(AcquisitionAttempt(source, url, "ACQUIRED", bytes=len(content), sha256=digest))
            target = out / f"{league_code}_{season_code}.csv"
            target.write_bytes(content)
            df = pd.read_csv(io.BytesIO(content), encoding_errors="replace")
            df["_source_url"] = url
            df["_source"] = source
            df["_source_sha256"] = digest
            df["_season_code"] = season_code
            df["_league_code"] = league_code
            return df, attempts
        except Exception as exc:
            attempts.append(AcquisitionAttempt(source, url, "FAILED", type(exc).__name__ + ": " + str(exc)))

    raise RuntimeError("ALL_HISTORICAL_ACQUISITION_ROUTES_FAILED: " + repr([asdict(a) for a in attempts]))
