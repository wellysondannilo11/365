from datetime import datetime, timezone, timedelta
import pandas as pd, pytest
from ml.app.ingestion.schema import validate_schema
from ml.app.ingestion.raw_store import immutable_record, payload_hash
from ml.app.research.datasets import build_point_in_time_dataset
from ml.app.research.odds import normalize_odds, snapshot_at_or_before
from ml.app.research.baselines import implied_baseline, historical_frequency
from ml.app.research.validation import split_by_event_groups
from ml.app.leakage import audit_point_in_time, validate_temporal_dataset, validate_feature_lineage
from ml.app.research.features import HistoricalFeatureBuilder
from ml.app.research.market import consensus
from ml.app.backtest_engine import simulate

BASE=datetime(2025,1,1,tzinfo=timezone.utc)
def rows(n=20):
 out=[]
 for i in range(n):
  t=BASE+timedelta(days=i)
  out.append({'event_id':str(i),'event_time':t,'source_time':t,'available_at':t,'ingested_at':t,'decision_time':t,'label':i%2})
 return pd.DataFrame(out)

def test_ingestion_schema(): validate_schema(pd.DataFrame([{'event_id':'e','event_time':BASE}]),'matches')
def test_raw_hash_and_record_deterministic():
 assert payload_hash({'b':2,'a':1})==payload_hash({'a':1,'b':2}); r=immutable_record('x','1',{'a':1}); assert r['raw_hash']==payload_hash({'a':1})
def test_dataset_manifest_reproducible():
 d=rows(); a,ma=build_point_in_time_dataset(d); b,mb=build_point_in_time_dataset(d); assert ma.dataset_hash==mb.dataset_hash and ma.records==20

def test_feature_level_leakage_rejected():
 d=rows(1); d['future']=1; d['future__available_at']=d.decision_time+pd.Timedelta(seconds=1)
 assert len(audit_point_in_time(d))>0
 with pytest.raises(ValueError): validate_temporal_dataset(d)

def test_missing_feature_availability_rejected():
 d=rows(1); d['xg_feature']=1.0
 with pytest.raises(ValueError,match='FEATURE_LEVEL_LEAKAGE'): validate_temporal_dataset(d)

def test_lineage_validation():
 x=pd.DataFrame([{'feature_name':'elo','event_id':'e','as_of':BASE,'available_at':BASE,'source_record_ids':['r1']}]); validate_feature_lineage(x)
 x.loc[0,'available_at']=BASE+timedelta(hours=1)
 with pytest.raises(ValueError): validate_feature_lineage(x)

def test_odds_snapshot_is_point_in_time():
 d=pd.DataFrame([{'event_id':'e','bookmaker':'a','market':'ou','selection':'Over','line':2.5,'price':2.1,'captured_at':'2025-01-01T00:00:00Z','available_at':'2025-01-01T00:00:00Z'},{'event_id':'e','bookmaker':'a','market':'ou','selection':'Over','line':2.5,'price':2.3,'captured_at':'2025-01-01T02:00:00Z','available_at':'2025-01-01T02:00:00Z'}])
 x=snapshot_at_or_before(d,'e','2025-01-01T01:00:00Z'); assert float(x.iloc[0].price)==2.1

def test_invalid_odds_rejected():
 with pytest.raises(ValueError): normalize_odds(pd.DataFrame([{'event_id':'e','bookmaker':'a','market':'x','selection':'y','price':1,'captured_at':BASE}]))
def test_baselines(): assert implied_baseline(2)==.5 and historical_frequency([0,1,1])==2/3

def test_temporal_group_split():
 d=rows(30); tr,va,te,ho=split_by_event_groups(d,BASE+timedelta(days=9),BASE+timedelta(days=19),BASE+timedelta(days=24)); assert len(tr)==10 and len(va)==10 and len(te)==5 and len(ho)==5

def test_historical_feature_builder_is_prior_only():
 data=[]
 for i in range(6):
  t=BASE+timedelta(days=i); data.append({'event_id':str(i),'event_time':t,'decision_time':t,'available_at':t,'outcome_available_at':t+timedelta(hours=2),'source_time':t,'ingested_at':t,'home_team':'A','away_team':'B','home_goals':i%2,'away_goals':(i+1)%2})
 out,lineage=HistoricalFeatureBuilder().build(pd.DataFrame(data))
 assert not pd.isna(out.iloc[0]['elo_delta'])
 assert all(pd.Timestamp(x.available_at)<=pd.Timestamp(x.as_of) for x in lineage)
 assert float(out.iloc[-1]['elo_home_prior'])!=1500.0

def test_historical_feature_builder_requires_explicit_outcome_availability():
 data=[{'event_id':'1','event_time':BASE,'decision_time':BASE,'available_at':BASE,'home_team':'A','away_team':'B','home_goals':1,'away_goals':0}]
 out,_=HistoricalFeatureBuilder().build(pd.DataFrame(data))
 assert pd.isna(out.iloc[0]['home_goals_for_ewma5'])

def test_market_consensus_devigs_per_bookmaker():
 rows=[]
 for book,base in [('A',2.0),('B',2.2)]:
  rows += [{'event_id':'e','bookmaker':book,'market':'1X2','selection':'Home','line':None,'price':base,'captured_at':'2025-01-01T00:00:00Z','available_at':'2025-01-01T00:00:00Z'}, {'event_id':'e','bookmaker':book,'market':'1X2','selection':'Draw','line':None,'price':3.5,'captured_at':'2025-01-01T00:00:00Z','available_at':'2025-01-01T00:00:00Z'}, {'event_id':'e','bookmaker':book,'market':'1X2','selection':'Away','line':None,'price':4.0,'captured_at':'2025-01-01T00:00:00Z','available_at':'2025-01-01T00:00:00Z'}]
 c=consensus(rows,decision_time='2025-01-01T00:02:00Z'); assert len(c)==3; assert all(x.bookmaker_count==2 for x in c)

def test_backtest_records_real_fields():
 d=pd.DataFrame([{'event_id':'1','decision_time':BASE,'odds':2.0,'probability':.6,'result':1,'closing_odds':1.8,'market':'1X2','selection':'Home','bookmaker':'A'},{'event_id':'2','decision_time':BASE+timedelta(days=1),'odds':2.0,'probability':.6,'result':0,'closing_odds':2.1,'market':'1X2','selection':'Home','bookmaker':'A'}])
 r=simulate(d,min_edge=.05,unit=1,bankroll=10); assert r['bets']==2 and r['clv'] is not None and 'max_drawdown' in r

def test_football_data_adapter_normalization_is_explicit_about_availability():
    from ml.app.adapters.football_data import FootballDataAdapter
    raw=pd.DataFrame([{'Date':'01/08/24','Time':'15:00','HomeTeam':'A','AwayTeam':'B','FTHG':2,'FTAG':1,'B365H':2.0,'B365D':3.5,'B365A':4.0}])
    m=FootballDataAdapter.normalize_matches(raw); assert m.iloc[0].availability_evidence=='EVENT_LEVEL_SOURCE_ONLY'; assert pd.isna(m.iloc[0].available_at)
    o=FootballDataAdapter.odds_long(raw); assert len(o)==3; assert o.availability_evidence.iloc[0]=='PREMATCH_ODDS_SET_NO_EXACT_TIMESTAMP'

def test_research_pipeline_selects_on_validation_only():
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from ml.app.research.pipeline import ResearchPipeline
    class P(ResearchPipeline):
        def candidates(self):
            return {'logistic': LogisticRegression(max_iter=500, random_state=42)}
    n=150; base=BASE
    rng=np.random.default_rng(7); x=rng.normal(size=n); y=(x+rng.normal(scale=.4,size=n)>0).astype(int)
    d=pd.DataFrame({'event_id':[str(i) for i in range(n)],'event_time':[base+timedelta(days=i) for i in range(n)],'x':x,'label':y})
    r=P().run(d,['x'],'label',min_train=60,validation=20,test=20,holdout=.2)
    assert r['selections']
    assert all(s['champion']=='logistic' for s in r['selections'])
    assert all(s['test_rows']==20 for s in r['selections'])
    assert r['holdout_locked'] is True
