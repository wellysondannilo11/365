from datetime import datetime, timedelta, timezone
from app.intelligence_evidence import Provenance, EvidenceClass, PITStatus, classify_source, quality_gate
from app.intelligence.live import LiveIntelligenceEngine, LiveSnapshot, MatchState
from app.intelligence.pricing import LiveMarketPricer

def now(): return datetime.now(timezone.utc)

def snap(**kw):
    t=now(); base=dict(event_id='e',source='real',source_timestamp=t,captured_at=t,minute=20,score_home=0,score_away=0,shots_home=5,shots_away=3,shots_on_target_home=2,shots_on_target_away=1,xg_home=.4,xg_away=.2)
    base.update(kw); return LiveSnapshot(**base)

def test_evidence_never_promotes_synthetic():
    assert classify_source('x',synthetic=True)==EvidenceClass.SYNTHETIC
    p=Provenance('x',None,EvidenceClass.SYNTHETIC,None,None,None,None)
    assert not p.is_empirical() and p.pit_status()==PITStatus.POSSIBLE_LEAKAGE

def test_pit_exact_before_decision():
    t=now(); p=Provenance('x',None,EvidenceClass.HISTORICAL_REAL,t,t,t,t+timedelta(seconds=1))
    assert p.pit_status()==PITStatus.KNOWN_BEFORE_DECISION

def test_live_state_machine():
    assert LiveIntelligenceEngine.state(10)==MatchState.EARLY_1H
    assert LiveIntelligenceEngine.state(45)==MatchState.LATE_1H
    assert LiveIntelligenceEngine.state(46)==MatchState.EARLY_2H
    assert LiveIntelligenceEngine.state(75)==MatchState.MID_2H
    assert LiveIntelligenceEngine.state(90)==MatchState.LATE_2H

def test_live_engine_rejects_out_of_order():
    e=LiveIntelligenceEngine(stale_seconds=120)
    t=now(); a=snap(source_timestamp=t-timedelta(seconds=1),captured_at=t-timedelta(seconds=1),minute=30)
    b=snap(source_timestamp=t-timedelta(seconds=2),captured_at=t-timedelta(seconds=2),minute=29)
    assert e.ingest(a)['status']=='PASS'
    assert e.ingest(b)['status']=='BLOCK'

def test_live_dynamics_is_observation_only():
    e=LiveIntelligenceEngine(stale_seconds=120); t=now()
    assert e.ingest(snap(source_timestamp=t-timedelta(seconds=1),captured_at=t-timedelta(seconds=1),minute=20))['status']=='PASS'
    d=e.dynamics('e'); assert d['status']=='OK' and d['match_state']=='MID_1H'

def test_quality_gate_requires_all_critical_inputs():
    ok,reasons=quality_gate(data_quality=.95,pit_status=PITStatus.KNOWN_BEFORE_DECISION,odds_verified=True,model_validated=True,sample_size=100)
    assert ok and not reasons
    ok,reasons=quality_gate(data_quality=.95,pit_status=PITStatus.UNKNOWN,odds_verified=True,model_validated=True,sample_size=100)
    assert not ok and 'PIT_NOT_PROVEN' in reasons

def test_live_pricer_fails_closed_without_validated_model():
    p=LiveMarketPricer()
    r=p.assess({'market':'TOTAL','selection':'OVER','line':2.5,'odds':2.2,'source':'other'},.55,model_validated=False)
    assert r['status']=='NO BET' and r['reason']=='MODEL_NOT_VALIDATED'
