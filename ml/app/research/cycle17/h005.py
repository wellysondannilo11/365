from __future__ import annotations
import math
from typing import Any
import pandas as pd

H005_ID = "H005_CROSS_BOOK_DISPERSION_V1"
H005_THRESHOLD = 0.02
ENTRY_BOOKMAKER = "Bet365"
REFERENCE_BOOKMAKER = "Average"


def _same_key(df: pd.DataFrame) -> list[str]:
    keys = ["event_id", "market", "selection"]
    return [k for k in keys if k in df.columns]


def evaluate_h005(df: pd.DataFrame) -> dict[str, Any]:
    required = {"event_id", "market", "selection", "bookmaker", "odds", "pit_status", "opening_status"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"H005_MISSING_COLUMNS:{missing}")
    exact = df[df["pit_status"].eq("EXACT_PIT") & df["opening_status"].eq("CONFIRMED")].copy()
    if exact.empty:
        return {"hypothesis_id": H005_ID, "threshold": H005_THRESHOLD, "eligible_events": 0, "bets": 0, "wins": 0, "losses": 0, "net_units": 0.0, "roi": None}

    exact["odds"] = pd.to_numeric(exact["odds"], errors="coerce")
    exact = exact[exact["odds"] > 1]
    records = []
    for key, group in exact.groupby(_same_key(exact), dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        row_key = dict(zip(_same_key(exact), key))
        bet365 = group[group["bookmaker"].astype(str).str.casefold().eq(ENTRY_BOOKMAKER.casefold())]
        reference = group[group["bookmaker"].astype(str).str.casefold().eq(REFERENCE_BOOKMAKER.casefold())]
        if bet365.empty or reference.empty:
            continue
        entry = float(bet365.iloc[0]["odds"])
        ref = float(reference.iloc[0]["odds"])
        if ref <= 1:
            continue
        dispersion = (entry / ref) - 1.0
        if dispersion < H005_THRESHOLD:
            continue
        result = str(bet365.iloc[0].get("result") or "").upper()
        profit = None
        if result == "WIN":
            profit = entry - 1.0
        elif result in {"LOSS", "LOSE"}:
            profit = -1.0
        records.append({**row_key, "entry_odds": entry, "reference_odds": ref, "dispersion": dispersion, "result": result, "profit_units": profit})

    bets = len(records)
    settled = [r for r in records if r["profit_units"] is not None]
    net = float(sum(r["profit_units"] for r in settled))
    wins = sum(r["profit_units"] > 0 for r in settled)
    losses = sum(r["profit_units"] < 0 for r in settled)
    return {
        "hypothesis_id": H005_ID,
        "threshold": H005_THRESHOLD,
        "eligible_events": bets,
        "bets": bets,
        "wins": wins,
        "losses": losses,
        "settled_bets": len(settled),
        "net_units": net,
        "roi": (net / bets) if bets else None,
        "records": records,
    }
