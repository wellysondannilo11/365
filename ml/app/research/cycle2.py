from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .calibration import OOSCalibrator, calibration_report


ODDS_BUCKETS = [
    ("<1.50", 0.0, 1.50),
    ("1.50–1.65", 1.50, 1.65),
    ("1.66–1.99", 1.65, 1.99),
    ("2.00–2.49", 1.99, 2.49),
    ("2.50–2.99", 2.49, 2.99),
    ("3.00–4.00", 2.99, 4.00),
    (">4.00", 4.00, np.inf),
]

BASE_FEATURES = [
    "prior_home_goals_for", "prior_home_goals_against",
    "prior_away_goals_for", "prior_away_goals_against",
    "home_form5", "away_form5", "elo_delta", "rest_delta",
]
MARKET_FEATURES = ["market_home_prob", "market_over25_prob"]
SHOTS_FEATURES = ["prior_home_shots", "prior_away_shots", "prior_home_sot", "prior_away_sot"]
CORNERS_FEATURES = ["prior_home_corners", "prior_away_corners"]
CARDS_FEATURES = ["prior_home_cards", "prior_away_cards"]
MOMENTUM_FEATURES = ["home_matches_7d", "away_matches_7d", "home_matches_14d", "away_matches_14d"]


def _clean_teams(x):
    return str(x).strip()


def normalize_market_probabilities(odds_home: float, odds_draw: float, odds_away: float) -> dict[str, float]:
    vals = np.asarray([odds_home, odds_draw, odds_away], dtype=float)
    if np.any(~np.isfinite(vals)) or np.any(vals <= 1.0):
        raise ValueError("INVALID_1X2_ODDS")
    inv = 1.0 / vals
    inv /= inv.sum()
    return {"home": float(inv[0]), "draw": float(inv[1]), "away": float(inv[2])}


def normalize_two_way(odds_a: float, odds_b: float) -> tuple[float, float]:
    vals = np.asarray([odds_a, odds_b], dtype=float)
    if np.any(~np.isfinite(vals)) or np.any(vals <= 1.0):
        raise ValueError("INVALID_TWO_WAY_ODDS")
    inv = 1.0 / vals
    inv /= inv.sum()
    return float(inv[0]), float(inv[1])


def research_metric_status(pit_count: int) -> str:
    return "PIT_ELIGIBLE_RESEARCH" if int(pit_count) > 0 else "RESEARCH_ONLY_NON_PIT"


def build_target(df: pd.DataFrame, target: str) -> pd.Series:
    if target == "home_win":
        return (df.home_goals > df.away_goals).astype(int)
    if target == "over_2_5":
        return ((df.home_goals + df.away_goals) > 2.5).astype(int)
    if target == "btts":
        return ((df.home_goals > 0) & (df.away_goals > 0)).astype(int)
    if target == "cards_high":
        return ((df.home_cards + df.away_cards) >= 5).astype(int)
    if target == "corners_high":
        return ((df.home_corners + df.away_corners) >= 10).astype(int)
    if target == "shots_high":
        return ((df.home_shots + df.away_shots) >= 23).astype(int)
    if target == "sot_high":
        return ((df.home_sot + df.away_sot) >= 9).astype(int)
    raise ValueError(f"UNKNOWN_TARGET:{target}")


def build_chronological_features(df: pd.DataFrame) -> pd.DataFrame:
    """Research-only feature construction from strictly prior events.

    No current-event outcome/stat is used in predictors. Rows are ordered by kickoff
    and the current match is emitted before its outcome enters either team's history.
    """
    required = {"match_id", "kickoff_timestamp", "home_team", "away_team", "home_goals", "away_goals"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"MISSING_COLUMNS:{sorted(missing)}")
    d = df.copy()
    d["kickoff_timestamp"] = pd.to_datetime(d.kickoff_timestamp, utc=True, errors="coerce", format="mixed")
    if d.kickoff_timestamp.isna().any():
        raise ValueError("INVALID_KICKOFF_TIMESTAMP")
    d = d.sort_values(["kickoff_timestamp", "match_id"], kind="stable").reset_index(drop=True)
    numeric_cols = [
        "home_goals", "away_goals", "home_shots", "away_shots", "home_sot", "away_sot",
        "home_corners", "away_corners", "home_cards", "away_cards"
    ]
    for c in numeric_cols:
        if c not in d:
            d[c] = np.nan
        d[c] = pd.to_numeric(d[c], errors="coerce")

    states: dict[str, dict] = {}
    rows = []
    for _, r in d.iterrows():
        home, away = _clean_teams(r.home_team), _clean_teams(r.away_team)
        hs = states.setdefault(home, {"elo": 1500.0, "history": [], "last": None})
        aas = states.setdefault(away, {"elo": 1500.0, "history": [], "last": None})

        def recent(state, key, n=5):
            vals = [x[key] for x in state["history"][-n:] if pd.notna(x.get(key))]
            return float(np.mean(vals)) if vals else np.nan

        def form(state, n=5):
            vals = state["history"][-n:]
            if not vals:
                return np.nan
            pts = [3 if x["gf"] > x["ga"] else 1 if x["gf"] == x["ga"] else 0 for x in vals]
            return float(np.mean(pts))

        def matches_within(state, days):
            if not state["last"]:
                return 0
            cutoff = r.kickoff_timestamp - pd.Timedelta(days=days)
            return sum(pd.Timestamp(x["event_time"]) >= cutoff for x in state["history"])

        rest_h = (r.kickoff_timestamp - hs["last"]).total_seconds() / 86400 if hs["last"] is not None else np.nan
        rest_a = (r.kickoff_timestamp - aas["last"]).total_seconds() / 86400 if aas["last"] is not None else np.nan
        row = r.to_dict()
        row.update({
            "prior_home_goals_for": recent(hs, "gf"),
            "prior_home_goals_against": recent(hs, "ga"),
            "prior_away_goals_for": recent(aas, "gf"),
            "prior_away_goals_against": recent(aas, "ga"),
            "home_form5": form(hs), "away_form5": form(aas),
            "elo_home": hs["elo"], "elo_away": aas["elo"], "elo_delta": hs["elo"] - aas["elo"],
            "rest_home": rest_h, "rest_away": rest_a,
            "rest_delta": (rest_h - rest_a) if pd.notna(rest_h) and pd.notna(rest_a) else np.nan,
            "prior_home_shots": recent(hs, "shots"), "prior_away_shots": recent(aas, "shots"),
            "prior_home_sot": recent(hs, "sot"), "prior_away_sot": recent(aas, "sot"),
            "prior_home_corners": recent(hs, "corners"), "prior_away_corners": recent(aas, "corners"),
            "prior_home_cards": recent(hs, "cards"), "prior_away_cards": recent(aas, "cards"),
            "home_matches_7d": matches_within(hs, 7), "away_matches_7d": matches_within(aas, 7),
            "home_matches_14d": matches_within(hs, 14), "away_matches_14d": matches_within(aas, 14),
        })
        try:
            mp = normalize_market_probabilities(r.odds_1, r.odds_x, r.odds_2)
            row.update({"market_home_prob": mp["home"], "market_draw_prob": mp["draw"], "market_away_prob": mp["away"]})
        except (ValueError, TypeError):
            row.update({"market_home_prob": np.nan, "market_draw_prob": np.nan, "market_away_prob": np.nan})
        try:
            over, _ = normalize_two_way(r.over_2_5, r.under_2_5)
            row["market_over25_prob"] = over
        except (ValueError, TypeError, AttributeError):
            row["market_over25_prob"] = np.nan
        rows.append(row)

        # Outcome becomes usable only after the current event; it is never used in its own row.
        hg, ag = float(r.home_goals), float(r.away_goals)
        expected = 1.0 / (1.0 + 10 ** ((aas["elo"] - hs["elo"]) / 400.0))
        score = 1.0 if hg > ag else 0.5 if hg == ag else 0.0
        hs["elo"] += 20.0 * (score - expected)
        aas["elo"] += 20.0 * ((1.0 - score) - (1.0 - expected))
        hs["history"].append({"event_time": r.kickoff_timestamp, "gf": hg, "ga": ag,
                               "shots": r.home_shots, "sot": r.home_sot, "corners": r.home_corners, "cards": r.home_cards})
        aas["history"].append({"event_time": r.kickoff_timestamp, "gf": ag, "ga": hg,
                                "shots": r.away_shots, "sot": r.away_sot, "corners": r.away_corners, "cards": r.away_cards})
        hs["last"] = r.kickoff_timestamp; aas["last"] = r.kickoff_timestamp
    return pd.DataFrame(rows)


@dataclass
class FoldMetrics:
    target: str
    model: str
    calibration: str
    fold: int
    train_events: int
    validation_events: int
    test_events: int
    accuracy: float
    log_loss: float
    brier: float
    ece: float
    mce: float
    roc_auc: float | None


def _safe_metrics(y, p):
    p = np.clip(np.asarray(p, float), 1e-9, 1 - 1e-9)
    y = np.asarray(y, int)
    rep = calibration_report(y, p)
    if len(np.unique(y)) < 2:
        auc = None
    else:
        auc = float(roc_auc_score(y, p))
    return {
        "accuracy": float(accuracy_score(y, (p >= 0.5).astype(int))),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "brier": float(brier_score_loss(y, p)),
        "ece": float(rep["ece"]), "mce": float(rep["mce"]), "roc_auc": auc,
    }


def _models(seed=42):
    return {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed)),
        "random_forest": RandomForestClassifier(n_estimators=60, min_samples_leaf=8, random_state=seed, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=100, max_depth=2, random_state=seed),
        "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=15, random_state=seed),
    }


def _folds(n_events: int, min_train=800, validation=400, test=400, holdout_fraction=0.15):
    holdout = max(1, int(n_events * holdout_fraction))
    research = n_events - holdout
    out = []
    cursor = min_train
    while cursor + validation + test <= research:
        out.append((cursor, cursor + validation, cursor + validation, cursor + validation + test))
        cursor += test
    return out, research, holdout


def _feature_sets(columns):
    groups = {
        "BASELINE": BASE_FEATURES,
        "MARKET": BASE_FEATURES + [x for x in MARKET_FEATURES if x in columns],
        "SHOTS_SOT": BASE_FEATURES + [x for x in SHOTS_FEATURES if x in columns],
        "CORNERS": BASE_FEATURES + [x for x in CORNERS_FEATURES if x in columns],
        "CARDS": BASE_FEATURES + [x for x in CARDS_FEATURES if x in columns],
        "MOMENTUM": BASE_FEATURES + [x for x in MOMENTUM_FEATURES if x in columns],
        "MARKET_INTELLIGENCE": BASE_FEATURES + [x for x in MARKET_FEATURES if x in columns] + ["elo_delta", "rest_delta"],
        "FULL": BASE_FEATURES + [x for x in MARKET_FEATURES + SHOTS_FEATURES + CORNERS_FEATURES + CARDS_FEATURES + MOMENTUM_FEATURES if x in columns],
    }
    return {k: list(dict.fromkeys(v)) for k, v in groups.items()}


def _fit_predict(model, x_train, y_train, x_pred):
    model.fit(x_train, y_train)
    return model.predict_proba(x_pred)[:, 1]


def _calibrate(validation_p, validation_y, test_p, method):
    if method == "raw":
        return test_p
    if len(validation_y) < 30 or len(np.unique(validation_y)) < 2:
        return test_p
    cal = OOSCalibrator("isotonic" if method == "isotonic" else "platt")
    cal.fit(validation_p, validation_y)
    return cal.predict(test_p)


def run_benchmark(df: pd.DataFrame, target: str, feature_set: str = "FULL", seed: int = 42,
                  min_train: int = 800, validation: int = 400, test: int = 400, holdout_fraction: float = 0.15):
    d = df.sort_values(["kickoff_timestamp", "match_id"], kind="stable").reset_index(drop=True).copy()
    d["target"] = build_target(d, target)
    features = _feature_sets(d.columns)[feature_set]
    usable = d.dropna(subset=features + ["target"]).reset_index(drop=True)
    folds, research_n, holdout_n = _folds(usable.match_id.nunique(), min_train, validation, test, holdout_fraction)
    if not folds:
        raise ValueError("INSUFFICIENT_DATA_FOR_CYCLE2")
    # Event rows are one per match in the canonical source; preserve event boundaries explicitly.
    results = []
    selections = []
    model_factories = _models(seed)
    for fi, (tr_end, va_end, _, te_end) in enumerate(folds):
        tr = usable.iloc[:tr_end]
        va = usable.iloc[tr_end:va_end]
        te = usable.iloc[va_end:te_end]
        val_scores = []
        fitted = {}
        for name, model in model_factories.items():
            try:
                pv = _fit_predict(model, tr[features], tr.target, va[features])
                score = log_loss(va.target, np.clip(pv, 1e-9, 1 - 1e-9), labels=[0, 1])
                val_scores.append((float(score), name, model, pv))
            except Exception:
                continue
        if not val_scores:
            continue
        val_scores.sort(key=lambda x: (x[0], x[1]))
        _, champion_name, champion, pv = val_scores[0]
        pt = champion.predict_proba(te[features])[:, 1]
        for cal in ("raw", "platt", "isotonic"):
            pc = _calibrate(pv, va.target.to_numpy(), pt, cal)
            m = _safe_metrics(te.target, pc)
            results.append(FoldMetrics(target, champion_name, cal, fi, len(tr), len(va), len(te), **m))
        # Standalone candidates are also measured on the same OOS fold for ranking.
        ensemble_probs = []
        for name, model in model_factories.items():
            try:
                ptest = model.predict_proba(te[features])[:, 1]
                ensemble_probs.append(ptest)
                m = _safe_metrics(te.target, ptest)
                results.append(FoldMetrics(target, name, "raw_standalone", fi, len(tr), len(va), len(te), **m))
            except Exception:
                pass
        if len(ensemble_probs) >= 2:
            pe = np.mean(ensemble_probs, axis=0)
            m = _safe_metrics(te.target, pe)
            results.append(FoldMetrics(target, "ensemble", "raw", fi, len(tr), len(va), len(te), **m))
        selections.append({"fold":fi,"champion":champion_name,"validation_log_loss":float(val_scores[0][0])})
    out = pd.DataFrame([asdict(x) for x in results])
    return out, selections, {"research_events": int(research_n), "holdout_events": int(holdout_n), "holdout_locked": True, "features": features}


def ensemble_oos(models, x, y):
    probs = []
    for model in models:
        probs.append(model.predict_proba(x)[:, 1])
    p = np.mean(probs, axis=0)
    return p, _safe_metrics(y, p)


def pricing_research(probability: pd.Series, odds: pd.Series, uncertainty: pd.Series | None = None) -> pd.DataFrame:
    p = pd.to_numeric(probability, errors="coerce").reset_index(drop=True)
    o = pd.to_numeric(odds, errors="coerce").reset_index(drop=True)
    if len(p) != len(o):
        raise ValueError("PROBABILITY_ODDS_LENGTH_MISMATCH")
    out = pd.DataFrame({"probability": p, "odds": o})
    out["fair_odds"] = 1.0 / p.where(p > 0)
    out["raw_ev"] = p * (o - 1.0) - (1.0 - p)
    out["realistic_ev"] = out["raw_ev"]
    if uncertainty is not None:
        u = pd.to_numeric(uncertainty, errors="coerce").fillna(0.0).clip(lower=0.0)
        out["uncertainty_adjusted_ev"] = out["raw_ev"] - u
    else:
        out["uncertainty_adjusted_ev"] = out["raw_ev"]
    out["scientific_status"] = "RESEARCH_ONLY_NON_PIT"
    return out


def odds_bucket(odds: float) -> str:
    for name, lo, hi in ODDS_BUCKETS:
        if lo <= float(odds) < hi or (name == ">4.00" and float(odds) > 4.0):
            return name
    return "NOT_AVAILABLE"


def simulate_sizing(probabilities: Iterable[float], odds: Iterable[float], outcomes: Iterable[int], unit_sizes=(0.25, 0.5, 1.0, 1.5, 2.0)) -> pd.DataFrame:
    p = np.asarray(list(probabilities), float); o = np.asarray(list(odds), float); y = np.asarray(list(outcomes), int)
    rows = []
    for unit in unit_sizes:
        valid = np.isfinite(p) & np.isfinite(o) & (o > 1) & np.isfinite(y)
        if not valid.any():
            rows.append({"stake_u": unit, "bets": 0, "units": 0.0, "roi": np.nan, "max_drawdown_u": 0.0, "status": "NOT_DETERMINED"})
            continue
        pnl = np.where(y[valid] == 1, unit * (o[valid] - 1), -unit)
        equity = np.cumsum(pnl); peak = np.maximum.accumulate(equity); dd = peak - equity
        rows.append({"stake_u": unit, "bets": int(valid.sum()), "units": float(pnl.sum()), "roi": float(pnl.sum()/(unit*valid.sum())), "max_drawdown_u": float(dd.max()), "status": "THEORETICAL_NON_PIT"})
    return pd.DataFrame(rows)


def dataset_fingerprint(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_jsonl(rows: Iterable[dict], path: str | Path):
    Path(path).write_text("\n".join(json.dumps(r, sort_keys=True, default=str) for r in rows) + "\n", encoding="utf-8")

def market_only_oos(df: pd.DataFrame, target: str, min_train=800, validation=400, test=400, holdout_fraction=0.15) -> pd.DataFrame:
    d = df.sort_values(["kickoff_timestamp", "match_id"], kind="stable").reset_index(drop=True).copy()
    d["target"] = build_target(d, target)
    if target == "home_win":
        prob_col = "market_home_prob"
    elif target == "over_2_5":
        prob_col = "market_over25_prob"
    else:
        return pd.DataFrame(columns=["target", "model", "fold", "test_events", "accuracy", "log_loss", "brier", "ece", "mce", "roc_auc"])
    if prob_col not in d.columns:
        if target == "home_win" and {"odds_1", "odds_x", "odds_2"}.issubset(d.columns):
            probs = d.apply(lambda r: normalize_market_probabilities(r.odds_1, r.odds_x, r.odds_2)["home"] if pd.notna(r.odds_1) and pd.notna(r.odds_x) and pd.notna(r.odds_2) else np.nan, axis=1)
            d[prob_col] = probs
        elif target == "over_2_5" and {"over_2_5", "under_2_5"}.issubset(d.columns):
            d[prob_col] = d.apply(lambda r: normalize_two_way(r.over_2_5, r.under_2_5)[0] if pd.notna(r.over_2_5) and pd.notna(r.under_2_5) else np.nan, axis=1)
        else:
            return pd.DataFrame(columns=["target", "model", "fold", "test_events", "accuracy", "log_loss", "brier", "ece", "mce", "roc_auc"])
    d = d.dropna(subset=[prob_col, "target"]).reset_index(drop=True)
    folds, _, _ = _folds(d.match_id.nunique(), min_train, validation, test, holdout_fraction)
    rows = []
    for fi, (tr_end, va_end, _, te_end) in enumerate(folds):
        te = d.iloc[va_end:te_end]
        if te.empty:
            continue
        m = _safe_metrics(te.target, te[prob_col])
        rows.append({"target": target, "model": "market_only", "fold": fi, "test_events": len(te), **m})
    return pd.DataFrame(rows)


def run_logistic_ablation(df: pd.DataFrame, target: str, feature_sets: dict[str,list[str]], min_train=1500, validation=300, test=500, holdout_fraction=.15, seed=42):
    d=df.sort_values(["kickoff_timestamp","match_id"],kind="stable").reset_index(drop=True).copy(); d["target"]=build_target(d,target)
    required_common=sorted(set(sum(feature_sets.values(),[])))
    common=d.dropna(subset=[f for f in required_common if f in d.columns]+["target"]).reset_index(drop=True)
    rows=[]
    for name,features in feature_sets.items():
        present=[f for f in features if f in common.columns]
        if len(present)!=len(features):
            rows.append({"target":target,"feature_set":name,"model":"logistic","status":"NOT_ELIGIBLE","comparison_sample_events":int(common.match_id.nunique())}); continue
        u=common.dropna(subset=present+["target"]).reset_index(drop=True)
        folds,_,_= _folds(u.match_id.nunique(),min_train,validation,test,holdout_fraction)
        if not folds:
            rows.append({"target":target,"feature_set":name,"model":"logistic","status":"INSUFFICIENT_DATA","comparison_sample_events":int(common.match_id.nunique())}); continue
        for fi,(tr_end,va_end,_,te_end) in enumerate(folds):
            tr=u.iloc[:tr_end]; te=u.iloc[va_end:te_end]
            m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=seed)); m.fit(tr[present],tr.target); p=m.predict_proba(te[present])[:,1]; met=_safe_metrics(te.target,p)
            rows.append({"target":target,"feature_set":name,"model":"logistic","fold":fi,"status":"OOS","test_events":len(te),"comparison_sample_events":int(common.match_id.nunique()),**met})
    return pd.DataFrame(rows)
