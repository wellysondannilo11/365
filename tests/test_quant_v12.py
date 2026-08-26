from datetime import datetime,timezone,timedelta
import pandas as pd,pytest
from ml.app.schemas import MatchSnapshot,OddsSnapshot
from ml.app.features import build_features
from ml.app.consensus import consensus_snapshots
from ml.app.leakage import validate_temporal_dataset
from ml.app.uncertainty import ensemble_uncertainty

def test_point_in_time_feature_lineage():
 now=datetime.now(timezone.utc);m=MatchSnapshot(event_id='e',league='L',home='A',away='B',kickoff=now+timedelta(hours=1),captured_at=now,available_at=now)
 f=build_features(m,now);assert all(x.available_at<=x.as_of for x in f.lineage)

def test_future_feature_rejected():
 now=datetime.now(timezone.utc);df=pd.DataFrame([{'event_id':'e','event_time':now,'source_time':now,'available_at':now+timedelta(minutes=1),'ingested_at':now,'decision_time':now}])
 with pytest.raises(ValueError):validate_temporal_dataset(df)

def test_consensus_and_best_price():
 now=datetime.now(timezone.utc);o=[OddsSnapshot(event_id='e',market='totals',selection='Over 2.5',odds=2.5,bookmaker='a',captured_at=now),OddsSnapshot(event_id='e',market='totals',selection='Over 2.5',odds=2.2,bookmaker='b',captured_at=now)]
 c=consensus_snapshots(o)[0];assert c.best_price==2.5 and c.bookmaker_count==2 and 0<c.consensus_probability<1

def test_uncertainty():
 u,c=ensemble_uncertainty([.5,.52,.48]);assert u>0 and 0<c<=1
