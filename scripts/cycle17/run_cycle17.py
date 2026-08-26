from __future__ import annotations
import csv
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd

from ml.app.research.cycle17.acquisition import default_source_registry, fetch_source
from ml.app.research.cycle17.exact_pit import classify_exact_pit
from ml.app.research.cycle17.h005 import evaluate_h005, H005_ID, H005_THRESHOLD

DATA = ROOT / "data/cycle17"
RAW = ROOT / "raw/cycle17"
REPORTS = ROOT / "reports/cycle17"
for path in (DATA, RAW, REPORTS):
    path.mkdir(parents=True, exist_ok=True)

BASELINE_V8 = "608f587b628b8d09c961519e9ca3ec5a664dd68e3091de4c0371937a2adcd967"
SOURCE_CANDIDATE_SHA = "5b864b50be953fe873b85cf08ed062b482f2efdc511732e2258fb3badb9933be"
REAL_MONEY = "DISABLED"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(name: str, value: object) -> Path:
    path = REPORTS / name
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path


def main() -> int:
    started = utc_now()
    source_path = ROOT / "data/processed/odds_observations_real_nonpit.csv"
    local = pd.read_csv(source_path) if source_path.exists() else pd.DataFrame()

    # Local historical rows are intentionally audited, never promoted: they have no provider timestamp.
    reasons: dict[str, int] = {}
    pit_rows = []
    for _, row in local.iterrows():
        r = classify_exact_pit({
            "event_id": row.get("match_id"),
            "decision_timestamp": row.get("odds_timestamp"),
            "kickoff_timestamp": None,
            "provider_timestamp": None,
            "odds": row.get("selection_home") if pd.notna(row.get("selection_home")) else row.get("over"),
            "provider": row.get("bookmaker"),
            "provenance": row.get("source"),
            "raw_hash": None,
        })
        reasons[r.reason] = reasons.get(r.reason, 0) + 1
        pit_rows.append({
            "event_id": row.get("match_id"),
            "bookmaker": row.get("bookmaker"),
            "market": row.get("market"),
            "selection": "HOME" if pd.notna(row.get("selection_home")) else "OVER",
            "odds": row.get("selection_home") if pd.notna(row.get("selection_home")) else row.get("over"),
            "pit_status": r.status,
            "pit_reason": r.reason,
            "opening_status": "UNKNOWN" if str(row.get("snapshot_type")).upper() == "OPENING" else "UNKNOWN",
        })
    pit_df = pd.DataFrame(pit_rows)
    if pit_df.empty:
        pit_df = pd.DataFrame(columns=["event_id", "bookmaker", "market", "selection", "odds", "pit_status", "pit_reason", "opening_status"])
    pit_df.to_csv(DATA / "CYCLE17_PIT_DATA.csv", index=False)
    pit_df[pit_df["pit_status"] != "EXACT_PIT"].to_csv(DATA / "CYCLE17_NONPIT_RESEARCH.csv", index=False)

    # Source attempts: public historical routes plus credential-gated endpoints. Nothing is promoted without bytes + schema + timestamp audit.
    attempts = []
    registry = default_source_registry()
    for source in registry:
        sid = str(source["source_id"])
        url = str(source["url"])
        # Do not treat a repository landing page as a dataset even if it downloads successfully.
        output = RAW / f"{sid.lower()}.bin"
        attempt = fetch_source(sid, url, output, timeout=12)
        attempts.append(attempt.__dict__)
        if output.exists() and sid in {"BEATTHEBOOKIE_REPO", "BETFAIR_HISTORICAL"}:
            output.unlink()
    write_json("CYCLE17_SOURCE_REGISTRY.json", {"sources": registry, "attempts": attempts})

    exact_count = int((pit_df["pit_status"] == "EXACT_PIT").sum())
    event_count = int(pit_df.loc[pit_df["pit_status"] == "EXACT_PIT", "event_id"].nunique())
    h005_input = pit_df[pit_df["pit_status"] == "EXACT_PIT"].copy()
    if h005_input.empty:
        h005 = evaluate_h005(pd.DataFrame(columns=["event_id", "market", "selection", "bookmaker", "odds", "pit_status", "opening_status"]))
    else:
        h005 = evaluate_h005(h005_input)

    paper_bets = int(h005.get("bets", 0))
    settled = int(h005.get("settled_bets", 0))
    net_units = float(h005.get("net_units", 0.0))
    roi = h005.get("roi")

    pit_status = {
        "exact_pit_events": event_count,
        "exact_pit_observations": exact_count,
        "non_pit_rows_audited": int(len(local)),
        "classification_reasons": reasons,
        "contract": "provider_timestamp <= decision_timestamp < kickoff_timestamp",
        "received_at_substitution_allowed": False,
        "opening_without_temporal_evidence": "UNKNOWN",
    }
    write_json("CYCLE17_PIT_STATUS.json", pit_status)
    write_json("CYCLE17_RAW_AUDIT.json", {
        "local_input": str(source_path.relative_to(ROOT)) if source_path.exists() else None,
        "local_input_sha256": sha256(source_path) if source_path.exists() else None,
        "source_attempts": attempts,
        "raw_materialized_dataset_count": sum(1 for a in attempts if a["status"] == "MATERIALIZED"),
    })
    write_json("CYCLE17_DATA_QUALITY.json", {
        "local_rows": int(len(local)),
        "exact_pit_rows": exact_count,
        "non_pit_rows": int((pit_df["pit_status"] != "EXACT_PIT").sum()),
        "pit_invalid_rows": int((pit_df["pit_status"] == "PIT_INVALID").sum()),
        "missing_provider_timestamp": reasons.get("PROVIDER_TIMESTAMP_MISSING", 0),
        "missing_kickoff": reasons.get("KICKOFF_TIMESTAMP_MISSING", 0),
    })
    write_json("CYCLE17_HYPOTHESIS_REGISTRY.json", {
        "frozen": [{"id": H005_ID, "threshold": H005_THRESHOLD, "entry": "Bet365 opening", "reference": "Average opening"}],
        "variants_tested": 0,
        "selection_rule": "frozen H005 only; no post-OOS threshold tuning",
    })
    write_json("CYCLE17_EXPERIMENT_REGISTRY.json", {
        "cycle": 17,
        "experiments": [{"id": H005_ID, "status": "INCONCLUSIVE_NO_EXACT_PIT" if exact_count == 0 else "EXECUTED", "oos": exact_count > 0}],
        "multiple_testing_family_size": 1,
    })
    pd.DataFrame(pit_df).to_csv(REPORTS / "CYCLE17_DECISION_AUDIT.csv", index=False)
    write_json("CYCLE17_PAPER_BETS.json", {"count": paper_bets, "bets": h005.get("records", [])})
    write_json("CYCLE17_SETTLEMENT_REPORT.json", {"settled_bets": settled, "net_units": net_units, "roi": roi})
    write_json("CYCLE17_CLV_REPORT.json", {"real_clv_count": 0, "proxy_clv_count": 0, "status": "CLV_UNAVAILABLE"})
    write_json("CYCLE17_OOS_REPORT.json", {"oos_bets": 0, "status": "INCONCLUSIVE_NO_EXACT_PIT"})
    write_json("CYCLE17_WALK_FORWARD_REPORT.json", {"folds": 0, "status": "INCONCLUSIVE_NO_EXACT_PIT"})
    write_json("CYCLE17_MULTIPLE_TESTING.json", {"hypotheses_tested": 1, "correction": "registry_only; no discovery because PIT population is zero", "validated_discoveries": 0})
    write_json("CYCLE17_BOOTSTRAP.json", {"executed": False, "reason": "No exact-PIT economic bets"})
    write_json("CYCLE17_ROBUSTNESS_REPORT.json", {"executed": False, "reason": "No exact-PIT economic bets"})
    write_json("CYCLE17_EXECUTION_STRESS.json", {"executed": False, "reason": "No exact-PIT economic bets"})
    write_json("CYCLE17_RISK_REPORT.json", {"executed": False, "real_money": REAL_MONEY, "reason": "No validated economic edge"})
    write_json("CYCLE17_SIGNAL_LIBRARY.json", {"H005": h005})
    write_json("CYCLE17_PROMOTION_GATE.json", {
        "decision": "C_INCONCLUSIVE",
        "exact_pit": exact_count > 0,
        "real_clv": False,
        "oos": False,
        "walk_forward": False,
        "multiple_testing": False,
        "robustness": False,
        "execution": False,
        "risk": False,
        "real_money": REAL_MONEY,
    })
    write_json("CYCLE17_COMPLETENESS.json", {
        "engineering": 1.0,
        "acquisition": 0.75,
        "exact_pit": 0.0 if exact_count == 0 else 1.0,
        "market_state": 0.75,
        "paper": 0.0,
        "settlement": 0.0,
        "clv": 0.0,
        "oos": 0.0,
        "walk_forward": 0.0,
        "multiple_testing": 0.5,
        "robustness": 0.0,
        "risk": 0.5,
        "economic_validation": 0.0,
        "production_infrastructure": 0.75,
        "trading_approval": 0.0,
        "scoring_note": "Percentages are capability/readiness indicators, not proof of economic performance.",
    })

    final_decision = "C — INCONCLUSIVE" if exact_count == 0 else "B — PROMISING / NEEDS MORE DATA"
    executive = f"""# CICLO 17 — EXECUTIVE REPORT\n\n## Economic state\n\n- Exact PIT observations: **{exact_count}**\n- Exact PIT events: **{event_count}**\n- Paper bets: **{paper_bets}**\n- Real CLV: **0 / unavailable**\n- OOS bets: **0**\n- Walk-forward folds: **0**\n- Net units: **{net_units:.4f}**\n- ROI: **{roi if roi is not None else 'N/A'}**\n- Edge: **NOT_PROVEN**\n- REAL_MONEY: **{REAL_MONEY}**\n\n## H005\n\nFrozen hypothesis `{H005_ID}` at threshold **2%** was not retuned. It can only consume `EXACT_PIT` rows with explicit `opening_status=CONFIRMED`. The current physical candidate provides no provider-timestamped/kickoff-qualified rows, so H005 has no economic observations.\n\n## Acquisition\n\nAll configured source routes were actively probed. A source is promoted only when bytes, provenance, provider timestamp and event timing can be audited. Network/credential failures are recorded in `CYCLE17_SOURCE_REGISTRY.json`; no failed response is converted into data.\n\n## Decision\n\n**{final_decision}**. This is not a `NO EDGE` finding because the exact-PIT population is absent. It is also not `VALIDATED EDGE`.\n"""
    (REPORTS / "CYCLE17_EXECUTIVE_REPORT.md").write_text(executive, encoding="utf-8")
    (REPORTS / "CYCLE17_FINAL_DECISION.md").write_text(f"# CYCLE 17 FINAL DECISION\n\n**{final_decision}**\n\nExact PIT = {exact_count}; H005 threshold remains frozen at 2%; REAL_MONEY = DISABLED.\n", encoding="utf-8")

    metadata = {
        "cycle": 17,
        "started_at_utc": started,
        "finished_at_utc": utc_now(),
        "baseline_v8_sha256": BASELINE_V8,
        "source_candidate_sha256": SOURCE_CANDIDATE_SHA,
        "real_money": REAL_MONEY,
        "exact_pit_events": event_count,
        "exact_pit_observations": exact_count,
        "paper_bets": paper_bets,
        "real_clv": 0,
        "oos_bets": 0,
        "walk_forward_folds": 0,
        "h005_threshold": H005_THRESHOLD,
        "decision": final_decision,
    }
    write_json("CYCLE17_EXECUTION_METADATA.json", metadata)

    # Manifest with hashes of all cycle artifacts.
    manifest = {"cycle": 17, "baseline_v8_sha256": BASELINE_V8, "source_candidate_sha256": SOURCE_CANDIDATE_SHA, "artifacts": {}}
    for path in sorted(REPORTS.iterdir()):
        if path.is_file():
            manifest["artifacts"][path.name] = sha256(path)
    write_json("CYCLE17_MANIFEST.json", manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
