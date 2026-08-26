from datetime import datetime,timezone
from .market import clv
class Ledger:
    def __init__(self):self.bets=[]
    def add(self,bet): self.bets.append(dict(bet,created_at=datetime.now(timezone.utc).isoformat()));return self.bets[-1]
    def settle(self,bet_id,result,closing_odds=None):
        for b in self.bets:
            if b['id']==bet_id:
                b['status']=result;b['closing_odds']=closing_odds;b['clv']=clv(b['odds'],closing_odds) if closing_odds else None
                b['pnl']=b['stake']*(b['odds']-1) if result=='WIN' else -b['stake'] if result=='LOSS' else 0;return b
        raise KeyError(bet_id)
