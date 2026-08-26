import math,statistics
def implied(odds):return 1/odds if odds>1 else 0.0
def devig(probs):
 s=sum(probs);return [p/s for p in probs] if s>0 else probs
def fair_odds(prob):return math.inf if prob<=0 else 1/prob
def edge(prob,odds):return prob-implied(odds)
def ev(prob,odds):return prob*odds-1
def overround(odds):return sum(implied(o) for o in odds if o>1)-1
def conservative_probability(model_prob,market_prob,weight=.65):return weight*model_prob+(1-weight)*market_prob
def price_anomaly(odds,fair,consensus=None):
 if consensus and consensus>1:return abs(odds-consensus)/consensus
 return abs(odds-fair)/fair if math.isfinite(fair) else 0
def clv(entry,closing):
 # Positive when the entry price is better than the later closing price.
 if entry<=1 or closing<=1:return None
 return entry/closing-1
def market_quality(odds):
 valid=[o for o in odds if o>1]
 if not valid:return {'overround':None,'dispersion':None,'best':None,'quality':0}
 probs=[implied(o) for o in valid];return {'overround':sum(probs)-1,'dispersion':statistics.pstdev(probs) if len(probs)>1 else 0.,'best':max(valid),'quality':min(100,40+len(valid)*10)}
