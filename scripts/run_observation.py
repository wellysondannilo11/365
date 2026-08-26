#!/usr/bin/env python3
"""Run authorized real-provider observation in PAPER or SHADOW only.

Fails closed when the provider is unavailable or data quality is not acceptable.
No real-money execution exists in this runner.
"""
from __future__ import annotations
import argparse, os, signal, time, json
from datetime import datetime, timezone
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ml"))
from app.v25.session import V25Session
from app.v25.persistence import PostgreSQLV25Store, RedisV25Store, V25SnapshotStore
from app.v25.dataset import V25Dataset

STOP=False
def _stop(signum, frame):
    global STOP
    STOP=True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("PAPER","SHADOW"), default=os.getenv("ROBO_MODE","SHADOW"))
    ap.add_argument("--interval", type=float, default=float(os.getenv("OBSERVATION_INTERVAL_SECONDS","30")))
    ap.add_argument("--duration", type=float, default=float(os.getenv("OBSERVATION_DURATION_SECONDS","0")), help="0 = run until stopped")
    ap.add_argument("--max-cycles", type=int, default=0, help="0 = unlimited")
    ap.add_argument("--status-file", default=os.getenv("OBSERVATION_STATUS_FILE","artifacts/paper_trading/observation_status.json"))
    args=ap.parse_args(); mode=args.mode.upper()
    if args.interval <= 0: raise SystemExit("interval must be > 0")
    pg=PostgreSQLV25Store()
    pg.connect()
    pg.ensure_schema()
    redis=RedisV25Store()
    redis.connect()
    dataset=V25Dataset(os.getenv("V25_DATASET_PATH","data/research/robo_bet_dataset_v25.jsonl"),persistence=pg if pg.available else None)
    snapshots=V25SnapshotStore(pg if pg.available else None,os.getenv("V25_SNAPSHOT_PATH","data/research/robo_bet_snapshots_v25.jsonl"))
    session=V25Session(dataset=dataset,persistence=pg if pg.available else None,snapshot_store=snapshots)
    started=time.monotonic(); cycles=0
    Path(args.status_file).parent.mkdir(parents=True, exist_ok=True)
    if not pg.available or not redis.available:
        reason = "POSTGRES_UNAVAILABLE" if not pg.available else "REDIS_UNAVAILABLE"
        payload={"state":"BLOCKED","mode":mode,"reason":reason,"database":pg.health(),"redis":redis.health(),"provider":{"name":session.provider.name,"configured":session.provider.configured}}
        Path(args.status_file).write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
        print(json.dumps(payload,sort_keys=True),flush=True)
        return 2
    signal.signal(signal.SIGINT,_stop); signal.signal(signal.SIGTERM,_stop)
    def status(state, **extra):
        payload={"state":state,"mode":mode,"session_id":session.session_id,"updated_at":datetime.now(timezone.utc).isoformat(),"provider":session.provider.name,"configured":session.provider.configured,"health":session.health.status.value,"database":pg.health(),"redis":redis.health(),"dataset":session.dataset.stats(),"snapshots":len(session.snapshot_store.rows()),"observability":session.observability.snapshot(),**extra}
        Path(args.status_file).write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
        print(json.dumps(payload,sort_keys=True),flush=True)
    status("STARTING")
    while not STOP:
        if args.duration and time.monotonic()-started >= args.duration: break
        if args.max_cycles and cycles >= args.max_cycles: break
        cycles += 1
        try:
            feed=session.poll()
            result=session.scan(feed,mode=mode)
            status("RUNNING",cycle=cycles,last_decision=result.get("decision"),selected=len(result.get("selected",[])))
        except RuntimeError as exc:
            status("BLOCKED",cycle=cycles,error=str(exc))
            # Credential/configuration errors should fail closed instead of spinning.
            if str(exc) == "CREDENTIALS_UNAVAILABLE": break
        except Exception as exc:
            status("ERROR",cycle=cycles,error=f"{type(exc).__name__}:{exc}")
        if STOP: break
        time.sleep(args.interval)
    session.kill=True; session.kill_reason="RUNNER_STOPPED"
    status("STOPPED",cycle=cycles)
    return 0

if __name__ == "__main__": raise SystemExit(main())
