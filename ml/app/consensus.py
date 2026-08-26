from __future__ import annotations
from dataclasses import dataclass
import math, statistics
from collections import defaultdict
from .market import implied, devig

@dataclass
class ConsensusResult:
    market: str
    selection: str
    median_probability: float
    weighted_probability: float
    consensus_probability: float
    dispersion: float
    best_price: float
    bookmaker_count: int
    overround: float
    captured_at: str | None


def consensus_snapshots(snapshots, target_market=None, target_selection=None, quality_weights=None):
    grouped=defaultdict(list)
    for s in snapshots:
        if target_market and s.market!=target_market: continue
        if target_selection and s.selection!=target_selection: continue
        if s.odds<=1: continue
        grouped[(s.market,s.selection)].append(s)
    out=[]
    for (market,selection),items in grouped.items():
        raw=[implied(x.odds) for x in items]
        probs=devig(raw)
        weights=[]
        for x in items:
            weights.append((quality_weights or {}).get(x.bookmaker,1.0))
        z=sum(weights) or 1
        weighted=sum(p*w for p,w in zip(probs,weights))/z
        median=statistics.median(probs)
        consensus=(median+weighted)/2
        dispersion=statistics.pstdev(probs) if len(probs)>1 else 0.0
        best=max(x.odds for x in items)
        overround=max(0.0,sum(raw)-1)
        ts=max((x.captured_at for x in items),default=None)
        out.append(ConsensusResult(market,selection,median,weighted,consensus,dispersion,best,len(items),overround,ts.isoformat() if ts else None))
    return out
