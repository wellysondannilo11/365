from datetime import datetime,timezone,timedelta
import pandas as pd, pytest
from ml.app.pit_store.pit import validate_frame,dataset_hash
from ml.app.research.market import consensus
from ml.app.research.calibration import calibration_report
from ml.app.research.validation import nested_walk_forward,assert_no_event_overlap
from ml.app.research.statistics import block_bootstrap,holm
from ml.app.holdout_lock import HoldoutGuard
from ml.app.market import clv

def pit_rows(n=20):
 now=datetime(2025,1,1,tzinfo=timezone.utc)
 return pd.DataFrame([{'event_id':str(i),'event_time':now+timedelta(days=i),'source_time':now+timedelta(days=i),'available_at':now+timedelta(days=i),'ingested_at':now+timedelta(days=i),'decision_time':now+timedelta(days=i)} for i in range(n)])
def test_pit_rejects_future():
 d=pit_rows(1);d.loc[0,'available_at']=d.loc[0,'decision_time']+timedelta(seconds=1)
 with pytest.raises(ValueError):validate_frame(d)
def test_hash_deterministic():assert dataset_hash(pit_rows())==dataset_hash(pit_rows())
def test_clv_direction():assert clv(2.5,2.0)>0 and clv(2.0,2.5)<0
def test_consensus_requires_valid_price():
 rows=[{'event_id':'e','market':'totals','line':2.5,'selection':'Over','price':2.5,'bookmaker':'a','captured_at':'2025-01-01T00:00:00Z'},{'event_id':'e','market':'totals','line':2.5,'selection':'Under','price':1.6,'bookmaker':'a','captured_at':'2025-01-01T00:00:00Z'}]
 assert len(consensus(rows))==2
def test_calibration_report():
 r=calibration_report([0,0,1,1],[.1,.2,.8,.9]);assert r['brier']<.1 and 'reliability' in r
def test_walkforward_keeps_holdout():
 d=pit_rows(40);d['label']=[i%2 for i in range(40)];folds,research,hold=nested_walk_forward(d,min_train=10,validation=5,test=5,holdout=.2);assert len(hold)==8;assert set(research.event_id).isdisjoint(set(hold.event_id))
def test_overlap_guard():
 d=pit_rows(2)
 with pytest.raises(ValueError):assert_no_event_overlap({'a':d,'b':d})
def test_bootstrap_ci():
 r=block_bootstrap([1,1,-1,-1],iterations=100,seed=1);assert r['ci_low']<=r['estimate']<=r['ci_high']
def test_holm_monotonic():
 r=holm([.001,.02,.2]);assert all(0<=x<=1 for x in r)
def test_holdout_lock():
 g=HoldoutGuard();g.freeze();g.lock();
 with pytest.raises(RuntimeError):g.assert_research_access()
