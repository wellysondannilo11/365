import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
from datetime import datetime,timezone,timedelta
import pandas as pd
from app.risk import RiskEngine
from app.market import fair_odds,ev,clv
from app.live import live_signal
from app.schemas import MatchSnapshot
from app.features import build_features
from app.leakage import validate_temporal_dataset
from app.pit_store.pit import validate_frame
from app.research.holdout import HoldoutGuard
assert abs(fair_odds(.5)-2)<1e-9 and abs(ev(.5,2.5)-.25)<1e-9 and clv(2.5,2.0)>0
r=RiskEngine();now=datetime.now(timezone.utc)
for _ in range(3):r.settle(-.5,now)
assert not r.allowed(now)
m=MatchSnapshot(event_id='x',league='demo',home='A',away='B',kickoff=now+timedelta(hours=1),captured_at=now,minute=60,xg_home=1.4,xg_away=.8,shots=18,shots_on_target=7,big_chances=3,dangerous_attacks=50,box_entries=14)
f=build_features(m,now);assert 'sot_rate' in f.values
assert live_signal(m,2.5,'OVER')['eligible']
df=pd.DataFrame([{'event_id':'1','event_time':now,'source_time':now,'available_at':now,'ingested_at':now,'decision_time':now}]);validate_temporal_dataset(df);validate_frame(df)
g=HoldoutGuard();g.freeze();g.lock();
try:g.assert_research_access();raise AssertionError('HOLDOUT_GUARD_FAILED')
except RuntimeError:pass
print('ROBO DA BET V16 SELF TEST OK')
