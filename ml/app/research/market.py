from __future__ import annotations
from dataclasses import dataclass
import statistics
from collections import defaultdict
import pandas as pd

@dataclass(frozen=True)
class Consensus:
    event_id: str; market: str; line: float|None; selection: str
    median_probability: float; weighted_probability: float; consensus_probability: float
    dispersion: float; best_price: float; overround: float; bookmaker_count: int; captured_at: str|None
    completeness: str = 'COMPLETE'

def implied(price):
    price = float(price)
    if price <= 1: raise ValueError('INVALID_ODDS')
    return 1.0 / price

def devig_probs(prices):
    p = [implied(x) for x in prices]
    s = sum(p)
    if s <= 0: raise ValueError('INVALID_OVERROUND')
    return [x/s for x in p]

def _market_family(market: str):
    m = str(market).lower()
    if m in {'1x2','h2h','match','match_result'}: return 3
    if 'btts' in m: return 2
    if 'total' in m or 'over' in m or 'under' in m: return 2
    return None

def consensus(snapshots, quality=None, stale_seconds=300, decision_time=None):
    d = pd.DataFrame(snapshots) if not isinstance(snapshots, pd.DataFrame) else snapshots.copy()
    if d.empty: return []
    from .odds import normalize_odds, snapshot_at_or_before
    d = normalize_odds(d)
    if decision_time is not None:
        d = d[d.available_at <= pd.Timestamp(decision_time, tz='UTC')]
        if d.empty: return []
        d = d.sort_values('captured_at').groupby(['event_id','bookmaker','market','line','selection'], dropna=False).tail(1)
    if stale_seconds is not None and decision_time is not None:
        t = pd.Timestamp(decision_time, tz='UTC')
        d = d[(t-d.captured_at).dt.total_seconds() <= stale_seconds]
    # First de-vig inside each bookmaker + event + market + line + timestamp snapshot.
    d['_line_key'] = d.line.where(d.line.notna(), '__NO_LINE__')
    d['snapshot_key'] = list(zip(d.event_id, d.bookmaker, d.market, d['_line_key'], d.captured_at))
    per_book = []
    for _, g in d.groupby('snapshot_key', dropna=False):
        expected = _market_family(g.market.iloc[0])
        complete = expected is None or g.selection.nunique() >= expected
        if complete and len(g) >= 2:
            probs = devig_probs(g.price.tolist())
            gg = g.copy(); gg['probability'] = probs; gg['overround'] = sum(implied(x) for x in g.price) - 1
            per_book.append(gg)
        elif len(g) == 1:
            gg = g.copy(); gg['probability'] = [implied(g.price.iloc[0])]; gg['overround'] = None; gg['completeness'] = 'INCOMPLETE'
            per_book.append(gg)
    if not per_book: return []
    x = pd.concat(per_book, ignore_index=True)
    x['completeness'] = x.get('completeness', 'COMPLETE')
    logical=[]
    for (event,market,line,selection),g in x.groupby(['event_id','market','line','selection'], dropna=False):
        # one logical observation per bookmaker: the most recent usable snapshot.
        g=g.sort_values('captured_at').groupby('bookmaker',dropna=False).tail(1)
        probs=g.probability.astype(float).tolist()
        weights=[float((quality or {}).get(str(b),1.0)) for b in g.bookmaker]
        z=sum(weights) or 1.0
        weighted=sum(p*w for p,w in zip(probs,weights))/z
        median=statistics.median(probs)
        best=float(g.price.max())
        overrounds=[float(v) for v in g.overround.dropna().tolist()]
        logical.append(Consensus(str(event),str(market),None if pd.isna(line) else float(line),str(selection),median,weighted,(median+weighted)/2,statistics.pstdev(probs) if len(probs)>1 else 0.0,best,float(sum(overrounds)/len(overrounds)) if overrounds else 0.0,int(len(g)),str(g.captured_at.max()) if len(g) else None,'COMPLETE' if all(g.completeness.fillna('COMPLETE')=='COMPLETE') else 'INCOMPLETE'))
    return logical
