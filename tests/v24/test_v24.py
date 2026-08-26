from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import pytest

from app.v24.quality import gate
from app.v24.dataset import EmpiricalDatasetV24
from app.v24.baseline import market_consensus,enrich
from app.v24.session import V24Session
from app.v24.replay import compare

def ts(dt): return dt.isoformat()

def row(book,sel,odds,src):
    return {"event_id":"e1","market":"h2h","selection":sel,"bookmaker":book,"odds":odds,
            "source_timestamp":ts(src),"captured_at":ts(src+timedelta(seconds=1))}

def test_quality_blocks_missing_source_and_future():
    now=datetime.now(timezone.utc)
    assert gate({"event_id":"e","market":"h2h","selection":"A","odds":2,"captured_at":ts(now)},now).status=="BLOCK"
    assert "SOURCE_TIMESTAMP_IN_FUTURE" in gate({**row("b","A",2,now+timedelta(minutes=1))},now).reasons

def test_quality_blocks_stale_live():
    now=datetime.now(timezone.utc)
    r=row("b","A",2,now-timedelta(seconds=60))
    assert "STALE_SOURCE" in gate(r,now,max_age_seconds=20,live=True).reasons

def test_consensus_is_bookmaker_aware():
    now=datetime.now(timezone.utc)
    rows=[row("b1","A",2.0,now),row("b1","B",2.0,now),row("b2","A",2.2,now),row("b2","B",1.9,now)]
    c=market_consensus(rows)
    assert set(c)=={("e1","h2h",None,"A"),("e1","h2h",None,"B")}
    assert 0<c[("e1","h2h",None,"A")]<1

def test_hash_chain_detects_tamper(tmp_path):
    d=EmpiricalDatasetV24(tmp_path/"d.jsonl")
    d.append({"event_id":"e","snapshot_id":"s","decision_id":"d1","mode":"SHADOW","decision":"NO BET"})
    d.append({"event_id":"e","snapshot_id":"s2","decision_id":"d2","mode":"SHADOW","decision":"NO BET"})
    assert d.verify()["valid"]
    lines=(tmp_path/"d.jsonl").read_text().splitlines()
    x=json.loads(lines[0]);x["decision"]="BET";(tmp_path/"d.jsonl").write_text(json.dumps(x)+"\n"+lines[1]+"\n")
    assert not d.verify()["valid"]

def test_real_money_mode_forbidden(tmp_path):
    d=EmpiricalDatasetV24(tmp_path/"d.jsonl")
    with pytest.raises(ValueError): d.append({"mode":"LIVE","event_id":"e"})

def test_replay_is_deterministic():
    x={"event_id":"e","decision":"NO BET","edge":0.0}
    assert compare(x,dict(x))["match"]

def test_v24_session_rejects_live_mode(tmp_path):
    s=V24Session(dataset=EmpiricalDatasetV24(tmp_path/"d.jsonl"))
    with pytest.raises(ValueError): s.decide({"health":"FEED_ONLINE","odds":[]}, "LIVE")

class FakeProvider:
    name="fake"
    configured=True
    def fetch_events_odds(self):
        now=datetime.now(timezone.utc)
        ts0=now-timedelta(seconds=1)
        events=[{"id":"e2","sport_key":"soccer_test","home_team":"A","away_team":"B",
                 "commence_time":ts(now+timedelta(hours=1)),
                 "bookmakers":[
                   {"key":"b1","markets":[{"key":"h2h","last_update":ts(ts0),"outcomes":[{"name":"A","price":2.1},{"name":"B","price":2.1}]}]},
                   {"key":"b2","markets":[{"key":"h2h","last_update":ts(ts0),"outcomes":[{"name":"A","price":2.2},{"name":"B","price":2.0}]}]}
                 ]}]
        return events,{"request_remaining":"100"}
def test_fake_provider_real_path_builds_empirical_observations(tmp_path):
    ds=EmpiricalDatasetV24(tmp_path/"d.jsonl")
    s=V24Session(provider=FakeProvider(),dataset=ds)
    feed=s.poll()
    assert feed["health"]=="FEED_ONLINE"
    out=s.decide(feed,"SHADOW")
    assert out["decision_id"] and out["no_bet_count"]>=0
    assert ds.stats()["rows"]==len(out["opportunities"])
    assert ds.verify()["valid"]

class FakeResponse:
    def __init__(self,status,headers=None,text="x"): self.status_code=status; self.headers=headers or {}; self.text=text
    def json(self): return []

class FakeHTTP:
    def __init__(self,responses): self.responses=list(responses); self.calls=0
    def get(self,*a,**k):
        self.calls+=1; return self.responses.pop(0)

def test_provider_does_not_retry_auth_errors():
    from app.v22.providers import OddsAPIProvider,ProviderError
    h=FakeHTTP([FakeResponse(401)])
    p=OddsAPIProvider(api_key="x",session=h,min_interval=0)
    with pytest.raises(ProviderError): p._get("/x",{})
    assert h.calls==1

def test_provider_retries_transient_errors():
    from app.v22.providers import OddsAPIProvider
    h=FakeHTTP([FakeResponse(500),FakeResponse(200,{"x-requests-remaining":"9"})])
    p=OddsAPIProvider(api_key="x",session=h,min_interval=0)
    r=p._get("/x",{})
    assert r.status_code==200 and h.calls==2

def test_live_snapshot_requires_pit_source():
    from app.v24.live import LiveStateEngine
    e=LiveStateEngine()
    now=datetime.now(timezone.utc)
    payload={"event_id":"e","captured_at":ts(now),"minute":20,"home_goals":0,"away_goals":0,"home_xg":.2,"away_xg":.1}
    assert e.ingest(payload)["status"]=="BLOCK"
    payload["source_timestamp"]=ts(now)
    assert e.ingest(payload)["status"]=="PASS"
    assert len(e.snapshots("e"))==1
