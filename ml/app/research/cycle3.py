from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
import pandas as pd

EV_BUCKETS = [
    ("EV < 0", -np.inf, 0.0),
    ("0–2%", 0.0, 0.02),
    ("2–5%", 0.02, 0.05),
    ("5–10%", 0.05, 0.10),
    ("10–15%", 0.10, 0.15),
    ("15–20%", 0.15, 0.20),
    (">20%", 0.20, np.inf),
]
DIVERGENCE_BUCKETS = [
    ("0–2pp", 0.0, 0.02), ("2–5pp", 0.02, 0.05), ("5–10pp", 0.05, 0.10),
    ("10–15pp", 0.10, 0.15), (">15pp", 0.15, np.inf),
]


def fair_odds(probability: float) -> float:
    p = float(probability)
    return 1.0 / p if 0.0 < p < 1.0 else math.nan


def compute_pricing(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["model_probability"] = pd.to_numeric(out["probability"], errors="coerce")
    out["market_odds"] = pd.to_numeric(out["odds"], errors="coerce")
    out["market_probability"] = 1.0 / out["market_odds"]
    out["fair_odds"] = 1.0 / out["model_probability"]
    out["edge"] = out["model_probability"] - out["market_probability"]
    out["raw_ev"] = out["model_probability"] * out["market_odds"] - 1.0
    u = out["uncertainty"] if "uncertainty" in out.columns else pd.Series(0.0, index=out.index)
    out["uncertainty_adjusted_ev"] = out["raw_ev"] - pd.to_numeric(u, errors="coerce").fillna(0.0)
    return out


def assign_selection(df: pd.DataFrame, ev_threshold: float = 0.0, divergence_threshold: float = 0.0) -> pd.DataFrame:
    out = compute_pricing(df)
    div = pd.to_numeric(out["divergence"] if "divergence" in out.columns else pd.Series(0.0, index=out.index), errors="coerce").abs().fillna(0.0)
    ok = out["raw_ev"].ge(ev_threshold) & div.ge(divergence_threshold)
    out["selection_status"] = np.where(ok, "APPROVED_RESEARCH", "REJECT")
    out.loc[out["raw_ev"].ge(0.0) & ~ok, "selection_status"] = "WATCH"
    pit = out.get("pit_status", pd.Series("NON_PIT", index=out.index)).astype(str)
    out["scientific_status"] = np.where(pit.eq("KNOWN_BEFORE_DECISION"), "PIT_ELIGIBLE_RESEARCH", "COUNTERFACTUAL_NON_PIT")
    return out


def assign_stake(probability: float, odds: float, *, uncertainty: float, data_quality: float, edge: float, correlation_penalty: float = 0.0) -> float:
    p, o = float(probability), float(odds)
    if not (0.0 < p < 1.0 and o > 1.0 and edge > 0):
        return 0.0
    confidence = max(0.0, min(1.0, 1.0 - float(uncertainty)))
    quality = max(0.0, min(1.0, float(data_quality)))
    corr = max(0.0, min(1.0, 1.0 - float(correlation_penalty)))
    kelly = max(0.0, ((o - 1.0) * p - (1.0 - p)) / (o - 1.0))
    raw = 4.0 * kelly * confidence * quality * corr
    if raw <= 0.0:
        return 0.0
    if confidence < 0.25 or quality < 0.50:
        return 0.25
    if raw < 0.50:
        return 0.25
    if raw < 1.00:
        return 0.50
    if raw < 1.50:
        return 1.00
    if raw < 2.00:
        return 1.50
    return 2.00


def assign_stakes(df: pd.DataFrame, mode: str = "dynamic") -> pd.DataFrame:
    out = df.copy()
    if mode.startswith("flat_"):
        stake = float(mode.split("_", 1)[1])
        out["stake"] = np.where(out["selection_status"].eq("APPROVED_RESEARCH"), stake, 0.0)
        return out
    out["stake"] = [assign_stake(p, o, uncertainty=u, data_quality=q, edge=e)
                    if s == "APPROVED_RESEARCH" else 0.0
                    for p, o, u, q, e, s in zip(
                        out["model_probability"], out["market_odds"],
                        out.get("uncertainty", pd.Series(0.0, index=out.index)),
                        out.get("data_quality", pd.Series(1.0, index=out.index)),
                        out["edge"], out["selection_status"])]
    return out


def simulate_portfolio(df: pd.DataFrame) -> dict:
    x = df.copy()
    valid = x["odds"].notna() & x["outcome"].notna() & x["stake"].gt(0) & x["odds"].gt(1)
    x = x.loc[valid].copy()
    if x.empty:
        return {"bets": 0, "units": 0.0, "roi": math.nan, "max_drawdown_u": 0.0, "profit_factor": math.nan,
                "win_rate": math.nan, "avg_odds": math.nan, "scientific_status": "COUNTERFACTUAL_NON_PIT"}
    pnl = np.where(x["outcome"].astype(int).to_numpy() == 1,
                   x["stake"].to_numpy(float) * (x["odds"].to_numpy(float) - 1.0),
                   -x["stake"].to_numpy(float))
    equity = np.cumsum(pnl); peak = np.maximum.accumulate(equity); dd = peak - equity
    wins = pnl[pnl > 0].sum(); losses = -pnl[pnl < 0].sum()
    return {
        "bets": int(len(x)), "units": float(pnl.sum()), "roi": float(pnl.sum() / x["stake"].sum()),
        "max_drawdown_u": float(dd.max()), "profit_factor": float(wins / losses) if losses > 0 else math.inf,
        "win_rate": float(x["outcome"].mean()), "avg_odds": float(x["odds"].mean()),
        "longest_losing_streak": longest_losing_streak(x["outcome"].astype(int).to_numpy()),
        "volatility": float(np.std(pnl, ddof=1)) if len(pnl) > 1 else 0.0,
        "scientific_status": "COUNTERFACTUAL_NON_PIT",
    }


def longest_losing_streak(outcomes: np.ndarray) -> int:
    best = cur = 0
    for y in outcomes:
        cur = cur + 1 if int(y) == 0 else 0
        best = max(best, cur)
    return int(best)


def summarize_ev_buckets(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, lo, hi in EV_BUCKETS:
        mask = df["raw_ev"].ge(lo) & df["raw_ev"].lt(hi)
        x = df.loc[mask]
        if x.empty:
            continue
        rows.append({
            "ev_bucket": label, "n": len(x), "win_rate": float(x["outcome"].mean()),
            "mean_ev": float(x["raw_ev"].mean()), "median_ev": float(x["raw_ev"].median()),
            "mean_odds": float(x["odds"].mean()), "theoretical_status": "COUNTERFACTUAL_NON_PIT",
        })
    return pd.DataFrame(rows)


def summarize_divergence(df: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    a=df["abs_divergence"].astype(float)
    for label,lo,hi in DIVERGENCE_BUCKETS:
        x=df.loc[a.ge(lo) & a.lt(hi)]
        if x.empty: continue
        rows.append({"divergence_bucket":label,"n":len(x),"win_rate":float(x.outcome.mean()),
                     "mean_divergence":float(x.divergence.mean()),"mean_odds":float(x.odds.mean()),
                     "status":"PREDICTIVE_DIVERGENCE_NON_PIT"})
    return pd.DataFrame(rows)
