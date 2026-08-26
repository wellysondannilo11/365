from datetime import datetime,timezone
from ml.app.market import *
from ml.app.risk import RiskEngine
from ml.app.selection import select
from ml.app.schemas import MatchSnapshot
from ml.app.live import live_signal

def test_value(): assert fair_odds(.5)==2 and round(ev(.5,2.5),2)==.25
def test_low_odds_rejected():
 r=RiskEngine();x=select(1.59,.7,95,.9,.02,80,r,datetime.now(timezone.utc));assert x['decision']=='NO BET' and 'ODDS_TOO_LOW' in x['reason']
def test_three_losses_cooldown():
 r=RiskEngine();now=datetime.now(timezone.utc)
 for _ in range(3):r.settle(-1,now)
 assert not r.allowed(now)
def test_daily_stop():
 r=RiskEngine();now=datetime.now(timezone.utc);r.settle(-4,now);assert not r.allowed(now)
def test_live_hot_over():
 m=MatchSnapshot(event_id='1',league='L',home='A',away='B',kickoff=datetime.now(timezone.utc),captured_at=datetime.now(timezone.utc),minute=60,xg_home=1.6,xg_away=.9,shots=20,shots_on_target=8,big_chances=3,dangerous_attacks=60,box_entries=15,corners=7)
 assert live_signal(m,2.5,'OVER')['eligible']
