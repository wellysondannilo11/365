from .market import fair_odds,edge,ev
from .risk import RiskEngine
from .config import settings

def select(odds,prob,dq,calibration,model_disagreement,temperature_score,risk:RiskEngine,now,live=False,market_quality_score=70):
    reasons=[];e=edge(prob,odds);v=ev(prob,odds)
    if odds<max(settings.min_odds,1.60): reasons.append('ODDS_TOO_LOW')
    if dq<settings.min_dq: reasons.append('DATA_QUALITY_LOW')
    if model_disagreement>.18: reasons.append('MODEL_DISAGREEMENT')
    if calibration<.70: reasons.append('CALIBRATION_BAD')
    if e<settings.min_edge: reasons.append('EDGE_TOO_LOW')
    if v<settings.min_ev: reasons.append('EV_TOO_LOW')
    if market_quality_score<40: reasons.append('MARKET_QUALITY_LOW')
    if live and temperature_score<45: reasons.append('LIVE_SIGNAL_UNSTABLE')
    if not risk.allowed(now): reasons.append('RISK_BLOCK')
    uncertainty_penalty=max(0,model_disagreement/.18); score=max(0,min(100,100*(.30*max(e,0)/.15+.25*max(v,0)/.30+.15*dq/100+.15*calibration+.10*market_quality_score/100+.05*(1-uncertainty_penalty))))
    if reasons:return {'decision':'NO BET','stake':0,'reason':'|'.join(reasons),'score':round(score,2),'edge':e,'ev':v,'fair_odds':fair_odds(prob)}
    stake=min(settings.max_stake,risk.stake(prob,odds))
    return {'decision':'BET' if stake>0 else 'NO BET','stake':stake,'reason':'VALUE_CONFIRMED' if stake>0 else 'NO_STAKE','score':round(score,2),'edge':e,'ev':v,'fair_odds':fair_odds(prob)}
