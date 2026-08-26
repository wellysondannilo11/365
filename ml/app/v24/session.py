from __future__ import annotations
from datetime import datetime, timezone
import os, uuid
from .baseline import enrich
from .quality import gate
from .dataset import EmpiricalDatasetV24
from ..v22.providers import OddsAPIProvider, normalize_odds_api
from ..v21.realtime import FeedHealth
from ..v20.selection import Candidate, rank_candidates
from ..v20.stake import StakePolicy

class KillSwitch:
    def __init__(self): self.enabled=False; self.reason=None
    def engage(self,reason): self.enabled=True;self.reason=reason
    def clear(self): self.enabled=False;self.reason=None

class V24Session:
    def __init__(self,provider=None,dataset=None):
        self.provider=provider or OddsAPIProvider()
        self.dataset=dataset or EmpiricalDatasetV24()
        self.health=FeedHealth(self.provider.name,max_age_seconds=float(os.getenv("FEED_STALE_SECONDS","30")),delayed_after_seconds=float(os.getenv("FEED_DELAYED_SECONDS","10")))
        self.kill=KillSwitch()
        self.session_id=str(uuid.uuid4())
        self.policy=StakePolicy(float(os.getenv("FRACTIONAL_KELLY","0.25")),float(os.getenv("MAX_STAKE_UNITS","1")),float(os.getenv("MIN_STAKE_UNITS","0.10")),float(os.getenv("BANKROLL_UNITS","50")))
        self.max_per_event=float(os.getenv("MAX_EVENT_EXPOSURE","1"))
        self.open_positions={}
    def poll(self):
        if self.kill.enabled: return {"status":"KILL_SWITCH","reason":self.kill.reason,"events":[],"odds":[]}
        if not self.provider.configured: raise RuntimeError("CREDENTIALS_UNAVAILABLE")
        events,meta=self.provider.fetch_events_odds()
        captured=datetime.now(timezone.utc)
        rows=normalize_odds_api(events,captured)
        # Provider timestamp is the source clock. captured_at is local ingestion time.
        source_times=[]
        for r in rows:
            try: source_times.append(datetime.fromisoformat(r["source_timestamp"].replace("Z","+00:00")))
            except Exception: pass
        newest=max(source_times) if source_times else None
        if newest is None:
            self.health.status=self.health.status.BLOCKED
        else:
            self.health.observe(newest,captured)
        status=self.health.status.value
        if status!="FEED_ONLINE":
            self.kill.engage("FEED_NOT_HEALTHY") if status in {"FEED_STALE","DATA_QUALITY_BLOCK"} else None
        for r in rows:
            r["snapshot_id"]=__import__("hashlib").sha256(f"{r['event_id']}|{r['source_timestamp']}|{r['bookmaker']}|{r['market']}|{r['selection']}|{r['odds']}".encode()).hexdigest()[:32]
        return {"session_id":self.session_id,"captured_at":captured.isoformat(),"events":events,"odds":rows,"health":status,"meta":meta}
    def decide(self,feed,mode="SHADOW"):
        mode=mode.upper()
        if mode not in {"PAPER","SHADOW"}: raise ValueError("MODE_MUST_BE_PAPER_OR_SHADOW")
        now=datetime.now(timezone.utc)
        if feed.get("health")!="FEED_ONLINE": return {"decision_id":None,"opportunities":[],"no_bet_count":0,"reason":"FEED_NOT_HEALTHY"}
        rows=enrich(feed["odds"])
        candidates=[];blocked=[]
        for r in rows:
            q=gate(r,now,max_age_seconds=float(os.getenv("FEED_STALE_SECONDS","30")),live=bool(r.get("live")))
            if q.status!="PASS":
                blocked.append(self._record(r,mode,now,"NO BET",0,q.reasons,0,None,None))
                continue
            if r.get("probability") is None: continue
            c=Candidate(str(r["event_id"]),str(r["market"]),str(r["selection"]),float(r["odds"]),float(r["probability"]),
                data_quality=100,calibration=1,uncertainty=.05,liquidity=1,market_quality=1,robustness=1,model_agreement=1,
                live=bool(r.get("live")),pit_ok=True,sample_size=max(30,int(r.get("sample_size",0))))
            candidates.append((r,c))
        ranked=rank_candidates([c for _,c in candidates],min_odds=float(os.getenv("MIN_ODDS","1.50")),preferred_odds=float(os.getenv("PREFERRED_ODDS","1.66")),
            min_edge=float(os.getenv("MIN_EDGE","0.05")),min_ev=float(os.getenv("MIN_EV","0.05")),min_data_quality=80,max_uncertainty=.12,min_market_quality=.4,policy=self.policy)
        # Select the single best expression per event, while keeping all observations in the dataset.
        approved_events=set(); out=blocked
        bykey={(str(r["event_id"]),str(r["market"]),str(r["selection"]),r.get("line")):r for r,c in candidates}
        for item in ranked:
            src=next((r for r,c in candidates if str(c.event_id)==item["event_id"] and c.market==item["market"] and c.selection==item["selection"]),{})
            decision=item["decision"]
            reason=item.get("no_bet_reason")
            if decision=="BET" and item["event_id"] in approved_events: decision="NO BET"; reason="BEST_EXPRESSION_ALREADY_SELECTED"
            if decision=="BET": approved_events.add(item["event_id"])
            out.append(self._record(src,mode,now,decision,float(item.get("stake") or 0),reason,item.get("fair_probability"),item.get("fair_odds"),item.get("edge"),item.get("ev"),score=item.get("score"),item=item))
        return {"session_id":self.session_id,"decision_id":str(uuid.uuid4()),"opportunities":out,"no_bet_count":sum(x.get("decision")=="NO BET" for x in out),"model":"MARKET_ONLY_BASELINE","scientific_status":"BASELINE_ONLY_NOT_EDGE_EVIDENCE"}
    def _record(self,r,mode,now,decision,stake,reason,fair_probability=None,fair_odds=None,edge=None,ev=None,score=None,item=None):
        did=str(uuid.uuid4()); snapshot=r.get("snapshot_id"); 
        row={**r,"decision_id":did,"decision":decision,"decision_time":now.isoformat(),"mode":mode,"stake_units":stake,
             "fair_probability":fair_probability,"fair_odds":fair_odds,"edge":edge,"ev":ev,"score":score,
             "model_version":"MARKET_ONLY_BASELINE","feature_version":"v24-feed","pricing_version":"market-consensus-devig",
             "reason":reason,"result":None,"pnl_units":None,"clv":None,"session_id":self.session_id}
        return self.dataset.append(row)

if __name__=="__main__":
    import json
    mode=os.getenv("ROBO_V24_MODE","SHADOW").upper()
    if mode not in {"PAPER","SHADOW"}: raise SystemExit("ROBO_V24_MODE must be PAPER or SHADOW")
    sess=V24Session()
    feed=sess.poll()
    print(json.dumps({"feed":feed.get("health"),"result":sess.decide(feed,mode)},default=str))
