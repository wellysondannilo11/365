from __future__ import annotations
from fastapi import APIRouter, HTTPException
from .session import V24Session
from .dataset import EmpiricalDatasetV24
from .analytics import bootstrap_mean, clv
from .live import LiveStateEngine
from .replay import deterministic_fingerprint
import os

router=APIRouter(prefix="/v24",tags=["v24"])
dataset=EmpiricalDatasetV24(os.getenv("V24_DATASET_PATH","data/research/robo_bet_dataset_v24.jsonl"))
session=V24Session(dataset=dataset)
live_engine=LiveStateEngine(float(os.getenv("LIVE_MAX_AGE_SECONDS","20")))

@router.get("/status")
def status():
    return {"version":"24.0.0","real_money_execution":False,"session_id":session.session_id,
            "feed":{"provider":session.provider.name,"configured":session.provider.configured,
                    "status":session.health.status.value},
            "dataset":dataset.stats(),"kill_switch":{"enabled":session.kill.enabled,"reason":session.kill.reason}}

@router.get("/dataset")
def dataset_status(limit:int=500):
    rows=dataset.rows()
    return {"stats":dataset.stats(),"rows":rows[-max(1,min(limit,5000)):],"performance":dataset.performance(),
            "paper":dataset.performance("PAPER"),"shadow":dataset.performance("SHADOW")}

@router.get("/analytics")
def analytics():
    rows=[r for r in dataset.rows() if r.get("result") in {"WIN","LOSS"}]
    return {"status":"NOT_DETERMINED" if len(rows)<100 else "EMPIRICAL_REVIEW",
            "n":len(rows),"bootstrap_pnl":bootstrap_mean([r.get("pnl_units") for r in rows]),
            "by_market":dataset.breakdown("market"),"by_league":dataset.breakdown("league"),
            "by_model":dataset.breakdown("model_version")}

@router.post("/export/xlsx")
def export_xlsx(): return {"path":dataset.export_xlsx()}

@router.get("/hash-chain")
def hash_chain(): return dataset.verify()

@router.post("/feed/poll")
def feed_poll():
    try:return session.poll()
    except RuntimeError as e: raise HTTPException(503,f"BLOCKED_EXTERNAL_DEPENDENCY:{e}") from e
    except Exception as e: raise HTTPException(502,f"FEED_PROVIDER_ERROR:{type(e).__name__}") from e

@router.post("/session/scan")
def scan(mode:str="SHADOW"):
    mode=mode.upper()
    if mode not in {"PAPER","SHADOW"}: raise HTTPException(422,"MODE_MUST_BE_PAPER_OR_SHADOW")
    try:
        feed=session.poll()
        return session.decide(feed,mode)
    except RuntimeError as e: raise HTTPException(503,f"BLOCKED_EXTERNAL_DEPENDENCY:{e}") from e
    except ValueError as e: raise HTTPException(422,str(e)) from e

@router.post("/kill-switch")
def kill_switch(enabled:bool=True,reason:str="MANUAL"):
    if enabled: session.kill.engage(reason)
    else: session.kill.clear()
    return {"enabled":session.kill.enabled,"reason":session.kill.reason}

@router.post("/live/snapshot")
def live_snapshot(payload:dict):
    return live_engine.ingest(payload)

@router.get("/live/{event_id}")
def live_history(event_id:str): return {"event_id":event_id,"snapshots":live_engine.snapshots(event_id)}

@router.post("/replay/compare")
def replay_compare(payload:dict):
    expected=payload.get("expected");actual=payload.get("actual")
    if expected is None or actual is None: raise HTTPException(422,"EXPECTED_AND_ACTUAL_REQUIRED")
    return {"match":deterministic_fingerprint(expected)==deterministic_fingerprint(actual),
            "expected_hash":deterministic_fingerprint(expected),"actual_hash":deterministic_fingerprint(actual)}

@router.post("/clv")
def clv_endpoint(entry_odds:float,closing_odds:float): return {"clv":clv(entry_odds,closing_odds)}
