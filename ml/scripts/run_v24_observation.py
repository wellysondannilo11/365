from __future__ import annotations
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.v24.session import V24Session
from app.v24.dataset import EmpiricalDatasetV24

def main():
    ap=argparse.ArgumentParser(description="Robo da Bet V24 real-feed PAPER/SHADOW observation session")
    ap.add_argument("--mode",choices=["PAPER","SHADOW"],default="SHADOW")
    ap.add_argument("--once",action="store_true")
    args=ap.parse_args()
    session=V24Session()
    feed=session.poll()
    result=session.decide(feed,args.mode)
    print(json.dumps({"feed":feed["health"],"mode":args.mode,"result":result,"dataset":session.dataset.stats()},default=str))
if __name__=="__main__": main()
