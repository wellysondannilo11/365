from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

CODE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CODE_ROOT))

from app.research.cycle2 import (
    build_chronological_features, build_target, dataset_fingerprint, run_logistic_ablation,
    market_only_oos, normalize_market_probabilities, normalize_two_way,
    odds_bucket, pricing_research, run_benchmark, simulate_sizing, write_jsonl,
    _feature_sets, _folds, _safe_metrics,
)

BASELINE_SHA = "608f587b628b8d09c961519e9ca3ec5a664dd68e3091de4c0371937a2adcd967"
CANDIDATE_SHA = "c1b8b0ef76be571f5be479871cb6d385325e5546e7030a013f11c6dd7ea3db66"


def oos_divergence(d, target, feature_set="FULL", min_train=1200, validation=400, test=400, holdout_fraction=.15):
    x = d.sort_values(["kickoff_timestamp", "match_id"], kind="stable").reset_index(drop=True).copy()
    x["target"] = build_target(x, target)
    features = _feature_sets(x.columns)[feature_set]
    x = x.dropna(subset=features + ["target"]).reset_index(drop=True)
    folds, _, _ = _folds(x.match_id.nunique(), min_train, validation, test, holdout_fraction)
    rows=[]
    for fi,(tr_end,va_end,_,te_end) in enumerate(folds):
        tr=x.iloc[:tr_end]; te=x.iloc[va_end:te_end]
        model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=42))
        model.fit(tr[features],tr.target)
        p=model.predict_proba(te[features])[:,1]
        market_col = "market_home_prob" if target=="home_win" else "market_over25_prob" if target=="over_2_5" else None
        if market_col is None: continue
        m=te[market_col].to_numpy(float)
        valid=np.isfinite(m)
        for idx,(pp,mm,yy,od) in enumerate(zip(p,m,te.target.to_numpy(),te.odds_1.to_numpy())):
            if not np.isfinite(mm): continue
            rows.append({"target":target,"fold":fi,"model_probability":float(pp),"market_probability":float(mm),"divergence":float(pp-mm),"abs_divergence":float(abs(pp-mm)),"outcome":int(yy),"odds":float(od) if np.isfinite(od) else np.nan,"market_bucket":odds_bucket(od) if np.isfinite(od) else "NOT_AVAILABLE","scientific_status":"PREDICTIVE_DIVERGENCE_NON_PIT"})
    return pd.DataFrame(rows)


def ablation_decision(df):
    if df.empty: return pd.DataFrame()
    agg=df.groupby(["target","model","calibration"],as_index=False).agg(n=("test_events","sum"),log_loss=("log_loss","mean"),brier=("brier","mean"),ece=("ece","mean"),accuracy=("accuracy","mean"),roc_auc=("roc_auc","mean"))
    return agg.sort_values(["target","log_loss","brier"])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default=str(PROJECT_ROOT/"data/enrichment/free_data/FOOTBALL_CANONICAL_ENRICHED_FREE.csv"))
    ap.add_argument("--output",default=str(PROJECT_ROOT/"reports/cycle2"))
    ap.add_argument("--seed",type=int,default=42)
    ap.add_argument("--min-train",type=int,default=1500)
    ap.add_argument("--validation",type=int,default=300)
    ap.add_argument("--test",type=int,default=500)
    ap.add_argument("--holdout-fraction",type=float,default=.15)
    args=ap.parse_args()
    out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(args.input)
    d=build_chronological_features(raw)
    fp=dataset_fingerprint(args.input)
    d.to_csv(out/"CYCLE2_RESEARCH_FEATURES.csv",index=False)

    targets=["home_win","over_2_5","btts","cards_high","corners_high","shots_high","sot_high"]
    model_frames=[]
    for target in ("home_win","over_2_5"):
        try:
            res, selections, meta=run_benchmark(d,target,feature_set="FULL",seed=args.seed,min_train=args.min_train,validation=args.validation,test=args.test,holdout_fraction=args.holdout_fraction)
            res["feature_set"]="FULL"; model_frames.append(res)
        except Exception as exc:
            (out/f"{target}_ERROR.txt").write_text(f"{type(exc).__name__}: {exc}\n",encoding="utf-8")
    # Other markets are benchmarked with a single transparent logistic research model to keep the cycle reproducible and computationally bounded.
    for target in ("btts","cards_high","corners_high","shots_high","sot_high"):
        try:
            rr=run_logistic_ablation(d,target,{"BASELINE":_feature_sets(d.columns)["BASELINE"]},min_train=args.min_train,validation=args.validation,test=args.test,holdout_fraction=args.holdout_fraction,seed=args.seed)
            rr=rr.rename(columns={"feature_set":"model_feature_set"}); rr["model"]="logistic"; rr["calibration"]="raw"; model_frames.append(rr)
        except Exception as exc:
            (out/f"{target}_ERROR.txt").write_text(f"{type(exc).__name__}: {exc}\n",encoding="utf-8")

    ablation_feature_sets=_feature_sets(d.columns)
    ablation=run_logistic_ablation(d,"home_win",ablation_feature_sets,min_train=args.min_train,validation=args.validation,test=args.test,holdout_fraction=args.holdout_fraction,seed=args.seed)
    ablation["feature_set_status"]=ablation["status"]
    ablation["calibration"]="raw"
    models=pd.concat(model_frames,ignore_index=True) if model_frames else pd.DataFrame()
    models.to_csv(out/"CYCLE2_MODEL_RESULTS.csv",index=False)
    ablation.to_csv(out/"CYCLE2_ABLATION_RESULTS.csv",index=False)
    ablation_decision(ablation).to_csv(out/"CYCLE2_ABLATION_SUMMARY.csv",index=False)

    market_frames=[]
    for target in ("home_win","over_2_5"):
        try: market_frames.append(market_only_oos(d,target,min_train=1000,validation=300,test=500,holdout_fraction=args.holdout_fraction))
        except Exception as exc: print("MARKET_ONLY_ERROR",target,type(exc).__name__,exc)
    market=pd.concat(market_frames,ignore_index=True) if market_frames else pd.DataFrame()
    market.to_csv(out/"CYCLE2_MARKET_ONLY_RESULTS.csv",index=False)

    divergence_frames=[]
    for target in ("home_win","over_2_5"):
        try: divergence_frames.append(oos_divergence(d,target,min_train=1000,validation=300,test=500,holdout_fraction=args.holdout_fraction))
        except Exception as exc: print("DIVERGENCE_ERROR",target,type(exc).__name__,exc)
    divergence=pd.concat(divergence_frames,ignore_index=True) if divergence_frames else pd.DataFrame()
    divergence.to_csv(out/"CYCLE2_MARKET_DIVERGENCE.csv",index=False)

    if not divergence.empty:
        div_summary=(divergence.assign(divergence_bucket=pd.cut(divergence.abs_divergence,[0,.03,.08,1],labels=["SMALL","MEDIUM","LARGE"],include_lowest=True)).groupby(["target","divergence_bucket"],observed=False).agg(n=("outcome","size"),mean_model_prob=("model_probability","mean"),mean_market_prob=("market_probability","mean"),actual_rate=("outcome","mean"),mean_divergence=("divergence","mean"),mean_abs_divergence=("abs_divergence","mean")).reset_index())
        div_summary.to_csv(out/"CYCLE2_MARKET_DIVERGENCE_SUMMARY.csv",index=False)

    # Research-only pricing and odds buckets from observed non-PIT prices.
    price_rows=[]
    home=d.dropna(subset=["market_home_prob","odds_1"]).copy()
    pr=pricing_research(home.market_home_prob,home.odds_1)
    pr["target"]="home_win"; pr["odds_bucket"]=home.odds_1.map(odds_bucket); pr.to_csv(out/"CYCLE2_PRICING_HOME.csv",index=False)
    price_rows.append(pr)
    if "market_over25_prob" in d and "over_2_5" in d:
        ov=d.dropna(subset=["market_over25_prob","over_2_5"]).copy(); po=pricing_research(ov.market_over25_prob,ov.over_2_5); po["target"]="over_2_5"; po["odds_bucket"]=ov.over_2_5.map(odds_bucket); po.to_csv(out/"CYCLE2_PRICING_OVER25.csv",index=False); price_rows.append(po)
    pricing=pd.concat(price_rows,ignore_index=True) if price_rows else pd.DataFrame()
    if not pricing.empty:
        pricing.groupby(["target","odds_bucket"],as_index=False).agg(n=("raw_ev","size"),mean_raw_ev=("raw_ev","mean"),median_raw_ev=("raw_ev","median"),mean_fair_odds=("fair_odds","mean")).to_csv(out/"CYCLE2_ODDS_BUCKETS.csv",index=False)

    # Theoretical sizing uses market probabilities as a counterfactual signal and outcomes only to describe hypothetical payout distributions.
    sizing_rows=[]
    if not home.empty:
        s=simulate_sizing(home.market_home_prob,home.odds_1,(home.home_goals>home.away_goals).astype(int))
        s["target"]="home_win"; sizing_rows.append(s)
    sizing=pd.concat(sizing_rows,ignore_index=True) if sizing_rows else pd.DataFrame()
    if not sizing.empty: sizing.to_csv(out/"CYCLE2_SIZING_SIMULATION.csv",index=False)

    registry={"experiment_id":"V16_CYCLE2_2026-08-24","dataset":str(args.input),"dataset_sha256":fp,"baseline_sha256":BASELINE_SHA,"candidate_start_sha256":CANDIDATE_SHA,"targets":targets,"seed":args.seed,"holdout_fraction":args.holdout_fraction,"exact_pit_count":0,"real_money":"DISABLED","betting_status":"NOT_VALIDATED","created_at":pd.Timestamp.now(tz="UTC").isoformat()}
    write_jsonl([registry],out/"CYCLE2_EXPERIMENT_REGISTRY.jsonl")

    # Executive report: only claims supported by these research artifacts.
    lines=["# ROBO DA BET V16+ — CYCLE 2 EXECUTIVE QUANT REPORT","",f"Dataset SHA-256: `{fp}`",f"Baseline SHA: `{BASELINE_SHA}`",f"Candidate start SHA: `{CANDIDATE_SHA}`","",f"Rows: {len(d):,}","Exact PIT: 0","REAL_MONEY: DISABLED","Betting ROI/units/CLV: NOT_VALIDATED","", "## Scientific interpretation", "All model metrics below are chronological research/OOS metrics. Prices are non-PIT research inputs and cannot establish real betting edge, ROI or CLV.",""]
    if not models.empty:
        summary=models.groupby(["target","model","calibration"],as_index=False).agg(n=("test_events","sum"),accuracy=("accuracy","mean"),log_loss=("log_loss","mean"),brier=("brier","mean"),ece=("ece","mean"),mce=("mce","mean"),roc_auc=("roc_auc","mean")).sort_values(["target","log_loss","brier"])
        summary.to_csv(out/"CYCLE2_MODEL_SUMMARY.csv",index=False)
        for target in summary.target.unique():
            lines.append(f"## {target}")
            lines.append(summary[summary.target==target].head(8).to_markdown(index=False))
            lines.append("")
    if not ablation.empty:
        a=ablation.groupby(["feature_set","model","calibration"],as_index=False).agg(log_loss=("log_loss","mean"),brier=("brier","mean"),ece=("ece","mean"),accuracy=("accuracy","mean"),n=("test_events","sum")).sort_values("log_loss")
        lines.append("## Home-win feature ablation")
        lines.append(a.head(15).to_markdown(index=False)); lines.append("")
    if not market.empty:
        lines.append("## Market-only benchmark")
        lines.append(market.groupby("target").agg(n=("test_events","sum"),accuracy=("accuracy","mean"),log_loss=("log_loss","mean"),brier=("brier","mean"),ece=("ece","mean")).reset_index().to_markdown(index=False)); lines.append("")
    lines += ["## Official status", "`EDGE = NOT_PROVEN`", "`ROI_OOS = NOT_DETERMINED`", "`UNITS_OOS = NOT_DETERMINED`", "`CLV = NOT_AVAILABLE`", "`EXACT_PIT = 0`", "`REAL_MONEY = DISABLED`"]
    (out/"CYCLE2_EXECUTIVE_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(out),"rows":len(d),"models_rows":len(models),"ablation_rows":len(ablation),"market_rows":len(market),"divergence_rows":len(divergence)},indent=2))

if __name__ == "__main__": main()
