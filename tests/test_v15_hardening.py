from datetime import datetime, timezone, timedelta
import pandas as pd
import pytest
from ml.app.research.validation import nested_walk_forward, split_by_event_groups
from ml.app.research.odds import normalize_odds
from ml.app.leakage import validate_temporal_dataset
from ml.app.research.statistics import cluster_bootstrap
from ml.app.backtest_engine import simulate
from ml.app.adapters.odds import TheOddsAPI

BASE=datetime(2025,1,1,tzinfo=timezone.utc)

def multirow_events(n=20, rows_per=3):
    rows=[]
    for i in range(n):
        t=BASE+timedelta(days=i)
        for j in range(rows_per):
            rows.append({'event_id':f'e{i}','event_time':t,'source_time':t,'available_at':t,'ingested_at':t,'decision_time':t,'label':(i+j)%2})
    return pd.DataFrame(rows)

def test_walkforward_uses_event_units_and_never_splits_event():
    d=multirow_events(20,3)
    folds,research,hold=nested_walk_forward(d,min_train=5,validation=3,test=2,holdout=.2)
    assert len(hold)==4*3
    for f in folds:
        parts=[research.iloc[:f.train_end_idx],research.iloc[f.validation_start_idx:f.validation_end_idx],research.iloc[f.test_start_idx:f.test_end_idx],hold]
        ids=[set(x.event_id.astype(str)) for x in parts]
        assert not (ids[0]&ids[1] or ids[0]&ids[2] or ids[1]&ids[2])
        assert all(len(x)==len(x.event_id.astype(str).unique())*3 for x in parts)

def test_split_rejects_event_id_with_multiple_times():
    d=multirow_events(3,2)
    d.loc[d.index[d.event_id=='e1'][0],'event_time']=BASE+timedelta(days=99)
    with pytest.raises(ValueError,match='MULTIPLE_EVENT_TIMES'):
        split_by_event_groups(d,BASE+timedelta(days=1),BASE+timedelta(days=2),BASE+timedelta(days=3))

def test_row_level_odds_are_valid_with_single_availability_clock():
    d=pd.DataFrame([{'event_id':'e','event_time':BASE,'source_time':BASE,'available_at':BASE,'ingested_at':BASE,'decision_time':BASE,'bookmaker':'A','market':'1X2','selection':'Home','price':2.0}])
    validate_temporal_dataset(d)

def test_cluster_bootstrap_preserves_event_grouping():
    d=pd.DataFrame([{'event_id':'a','pnl':1.0,'stake':1.0},{'event_id':'a','pnl':-1.0,'stake':1.0},{'event_id':'b','pnl':2.0,'stake':1.0}])
    r=cluster_bootstrap(d,iterations=100,seed=7)
    assert r['events']==2 and r['roi_ci']['low']<=r['estimate']<=r['roi_ci']['high']

def test_betting_roi_is_profit_over_total_stake():
    d=pd.DataFrame([{'event_id':'a','decision_time':BASE,'odds':2.0,'probability':.6,'result':1},{'event_id':'b','decision_time':BASE+timedelta(days=1),'odds':2.0,'probability':.6,'result':0}])
    r=simulate(d,min_edge=.05,unit=1,bankroll=10)
    assert r['profit']==0 and r['roi']==0 and r['bankroll_return']==0

def test_the_odds_api_normalizer_requires_provider_snapshot_timestamp():
    with pytest.raises(ValueError,match='SNAPSHOT_TIMESTAMP'):
        TheOddsAPI.normalize_historical_response({'data':[]})

def test_the_odds_api_normalizer_preserves_snapshot_time():
    payload={'timestamp':'2025-01-01T01:00:00Z','data':[{'id':'e1','bookmakers':[{'key':'book','markets':[{'key':'h2h','outcomes':[{'name':'Home','price':2.1}]}]}]}]}
    d=TheOddsAPI.normalize_historical_response(payload)
    assert len(d)==1 and d.iloc[0].available_at==pd.Timestamp('2025-01-01T01:00:00Z')
