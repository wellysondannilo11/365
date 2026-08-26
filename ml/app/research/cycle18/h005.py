from __future__ import annotations

import pandas as pd

H005_ID = "H005_CROSS_BOOK_DISPERSION_V1"
H005_THRESHOLD = 0.02
ENTRY_BOOKMAKER = "Bet365"
REFERENCE_BOOKMAKER = "Average"


def evaluate_h005_frozen(df: pd.DataFrame) -> dict[str, object]:
    required = {"event_id", "market", "selection", "bookmaker", "odds", "pit_status", "opening_status"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"H005_MISSING_COLUMNS:{missing}")
    exact = df[(df["pit_status"] == "EXACT_PIT") & (df["opening_status"] == "CONFIRMED")].copy()
    if exact.empty:
        return {
            "hypothesis_id": H005_ID,
            "threshold": H005_THRESHOLD,
            "entry": ENTRY_BOOKMAKER,
            "reference": REFERENCE_BOOKMAKER,
            "bets": 0,
            "status": "NO_ELIGIBLE_EXACT_PIT",
        }
    records: list[dict[str, object]] = []
    for key, group in exact.groupby(["event_id", "market", "selection"], dropna=False):
        bet365 = group[group["bookmaker"].astype(str).str.casefold() == ENTRY_BOOKMAKER.casefold()]
        average = group[group["bookmaker"].astype(str).str.casefold() == REFERENCE_BOOKMAKER.casefold()]
        if bet365.empty or average.empty:
            continue
        entry = float(bet365.iloc[0]["odds"])
        reference = float(average.iloc[0]["odds"])
        if reference <= 1.0:
            continue
        dispersion = entry / reference - 1.0
        if dispersion >= H005_THRESHOLD:
            records.append({
                "event_id": key[0], "market": key[1], "selection": key[2],
                "entry_odds": entry, "reference_odds": reference,
                "dispersion": dispersion,
            })
    return {
        "hypothesis_id": H005_ID,
        "threshold": H005_THRESHOLD,
        "entry": ENTRY_BOOKMAKER,
        "reference": REFERENCE_BOOKMAKER,
        "bets": len(records),
        "status": "EVALUATED",
        "records": records,
    }
