from datetime import datetime, timezone, timedelta
import pandas as pd
import pytest
from ml.app.adapters.odds import TheOddsAPI
from ml.app.research.data_quality_v16 import profile
from ml.app.research.raw import immutable_record
from ml.app.research.features import HistoricalFeatureBuilder

BASE=datetime(2020,1,1,tzinfo=timezone.utc)

def test_v16_quality_blocks_future_availability():
    d=pd.DataFrame([{'event_id':'e','event_time':BASE,'source_time':BASE,'available_at':BASE+timedelta(minutes=1),'ingested_at':BASE+timedelta(minutes=2),'decision_time':BASE}])
    r=profile(d)
    assert r['status']=='FAIL' and 'pit_violations' in r['blocking_failures']

def test_v16_raw_record_never_infers_timestamp():
    with pytest.raises(ValueError,match='REQUIRES_PROVIDER_TIMESTAMPS'):
        immutable_record('x','/x',{'a':1})

def test_v16_odds_preserves_snapshot_and_inner_updates():
    payload={'timestamp':'2025-01-01T01:00:00Z','data':[{'id':'e1','commence_time':'2025-01-01T03:00:00Z','bookmakers':[{'key':'book','last_update':'2025-01-01T00:59:00Z','markets':[{'key':'h2h','last_update':'2025-01-01T00:59:30Z','outcomes':[{'name':'Home','price':2.1}]}]}]}]}
    d=TheOddsAPI.normalize_historical_response(payload)
    assert d.iloc[0].available_at==pd.Timestamp('2025-01-01T01:00:00Z')
    assert d.iloc[0].market_last_update==pd.Timestamp('2025-01-01T00:59:30Z')

def test_v16_features_only_use_prior_outcomes():
    rows=[]
    for i in range(6):
        t=BASE+timedelta(days=i*3)
        rows.append({'event_id':f'e{i}','event_time':t,'decision_time':t,'available_at':t,'outcome_available_at':t+timedelta(hours=2),'home_team':'A','away_team':'B','home_goals':1 if i%2==0 else 0,'away_goals':0 if i%2==0 else 1,'home_xg':1.2,'away_xg':.8})
    d=pd.DataFrame(rows)
    f,_=HistoricalFeatureBuilder().build(d)
    assert f.iloc[0].elo_home_prior==1500
    assert f.iloc[-1].home_points_per_match5==1.8

def test_v16_empirical_runner_is_executable_on_controlled_fixture_only():
    from ml.app.research.empirical import run_real_research
    rows=[]
    for i in range(180):
        t=BASE+timedelta(days=i)
        rows.append({'event_id':f'x{i}','event_time':t,'decision_time':t,'available_at':t,'source_time':t,'ingested_at':t,'label':1 if i%3 else 0,'elo_delta':(i%11)-5})
    r=run_real_research(pd.DataFrame(rows),['elo_delta'],min_train=80,validation=20,test=20,holdout=.15)
    assert r.evidence_type=='REAL_DATA_RESEARCH' and r.events==180 and r.limitations
