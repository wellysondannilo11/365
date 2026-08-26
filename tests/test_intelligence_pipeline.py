from datetime import datetime, timezone, timedelta
from app.intelligence.pipeline import FootballIntelligencePipeline
from app.intelligence_evidence import Provenance, EvidenceClass

def test_pipeline_blocks_unproven_pit():
    t=datetime.now(timezone.utc)
    p=Provenance('other',None,EvidenceClass.LIVE_REAL_UNVERIFIED,t,t,None,t+timedelta(seconds=1))
    r=FootballIntelligencePipeline().evaluate_market({'market':'TOTAL','selection':'OVER','line':2.5,'odds':2.0},model_probability=.6,uncertainty=.05,provenance=p,data_quality=.95,sample_size=100,model_validated=True)
    assert r.decision=='WAIT'

def test_pipeline_allows_validated_market_only():
    t=datetime.now(timezone.utc)
    p=Provenance('other',None,EvidenceClass.LIVE_REAL,t,t,t,t+timedelta(seconds=1))
    r=FootballIntelligencePipeline(min_edge=.03,min_ev=.03).evaluate_market({'market':'TOTAL','selection':'OVER','line':2.5,'odds':2.0},model_probability=.6,uncertainty=.05,provenance=p,data_quality=.95,sample_size=100,model_validated=True)
    assert r.decision=='BET' and r.ev==.19999999999999996
