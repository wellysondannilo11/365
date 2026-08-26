from datetime import datetime,timezone
from .selection import rank_candidates
from .stake import StakePolicy
from .risk import PortfolioRisk
from .ledger import LedgerV20,LedgerRecord
from .notifications import provider_from_env
from .live_engine import LiveRepricingEngine
from .reporting import performance,group_performance
class DecisionServiceV20:
    def __init__(self):
        import os
        self.policy=StakePolicy(fractional_kelly=float(os.getenv('FRACTIONAL_KELLY','0.25')),max_stake_units=float(os.getenv('MAX_STAKE_UNITS','1.0')),min_stake_units=float(os.getenv('MIN_STAKE_UNITS','0.10')),bankroll_units=float(os.getenv('BANKROLL_UNITS','50')))
        self.risk=PortfolioRisk();self.ledger=LedgerV20(unit_brl=float(os.getenv('UNIT_BRL','500')));self.notify=provider_from_env();self.live=LiveRepricingEngine()
    def rank(self,candidates,**kwargs): return rank_candidates(candidates,policy=self.policy,**kwargs)
    def record(self,item,*,league='',country='',season='',feature_snapshot='',pit_status='PASS',entry_minute=None,scoreline=None):
        if item.get('decision')!='BET': return None
        now=datetime.now(timezone.utc).isoformat();rid=f"{item['event_id']}|{item['market']}|{item['selection']}|{now}";stake=float(item['stake'])
        rec=LedgerRecord(rid,item['event_id'],now,league,country,season,item['market'],item['selection'],float(item['odds']),stake,stake*self.ledger.unit_brl,None,0.0,float(item['fair_probability']),item.get('fair_odds'),float(item['edge']),float(item['ev']),None,'20.0.0',feature_snapshot,pit_status,'BET',entry_minute,scoreline)
        out=self.ledger.append(rec);self.risk.open(item['event_id'],stake);return out
    def summary(self):
        rows=self.ledger.rows();from datetime import datetime,timezone
        now=datetime.now(timezone.utc);return {'today':performance([r for r in rows if r.get('timestamp','')[:10]==now.date().isoformat()],self.ledger.unit_brl),'month':performance([r for r in rows if r.get('timestamp','')[:7]==now.strftime('%Y-%m')],self.ledger.unit_brl),'all':performance(rows,self.ledger.unit_brl),'markets':group_performance(rows,'market'),'leagues':group_performance(rows,'league'),'risk':self.risk.state.__dict__,'telegram_enabled':getattr(self.notify,'enabled',False)}
