from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "cycle18"
RAW = ROOT / "raw" / "cycle18"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(name: str, payload: object) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from ml.app.research.cycle18.acquisition import source_registry

    write_json("CYCLE18_SOURCE_REGISTRY.json", {"sources": source_registry()})
    write_json("CYCLE18_PIT_STATUS.json", {
        "exact_pit_events": 0,
        "exact_pit_observations": 0,
        "status": "NO_NEW_PROVIDER_TIMESTAMPED_BYTES_MATERIALIZED",
        "contract": "provider_timestamp <= decision_timestamp < kickoff_timestamp",
        "forbidden_fallbacks": ["received_at", "download_time", "filesystem_time", "file_time", "date-level"],
    })
    write_json("CYCLE18_H005_REPORT.json", {
        "hypothesis_id": "H005_CROSS_BOOK_DISPERSION_V1",
        "threshold": 0.02,
        "entry": "Bet365 opening",
        "reference": "Average opening",
        "status": "NOT_RUN",
        "reason": "No eligible Exact PIT observations with confirmed opening evidence.",
    })
    write_json("CYCLE18_GITHUB_STATUS.json", {
        "repository": "wellysondannilo11/365",
        "public_observed_branch": "master",
        "write_status": "NOT_AVAILABLE_IN_EXECUTION_ENVIRONMENT",
        "note": "The repository is publicly inspectable, but the current runtime has no authenticated GitHub write connector and direct git network access failed at DNS resolution.",
    })
    write_json("CYCLE18_COMPLETENESS.json", {
        "code_audit": "EXECUTED",
        "tests": "EXECUTED",
        "historical_exact_pit": "NOT_AVAILABLE",
        "economic_validation": "NOT_RUN",
        "real_money": "DISABLED",
    })
    (REPORTS / "CYCLE18_FINAL_DECISION.md").write_text(
        "# CYCLE 18 FINAL DECISION\n\n"
        "C — INCONCLUSIVE.\n\n"
        "GitHub was audited as the public source of continuity; the visible repository currently exposes a single legacy Java/Spring commit and does not contain the Cycle 17 Python tree. "
        "The C17 physical candidate was audited locally. No new provider-timestamped historical bytes were materialized in this runtime, so Exact PIT and economic validation were not run. H005 remains frozen at 2%. REAL_MONEY = DISABLED.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
