from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class StakePolicy:
    fractional_kelly: float=0.25
    max_stake_units: float=1.0
    min_stake_units: float=0.10
    bankroll_units: float=50.0
def kelly_fraction(probability, odds):
    if not 0 < probability < 1 or odds <= 1: return 0.0
    b=odds-1.0
    return max(0.0,(b*probability-(1-probability))/b)
def size_stake(probability, odds, *, policy, edge=0.0, uncertainty=0.0, correlation_penalty=0.0):
    if edge <= 0 or probability <= 0 or odds <= 1: return 0.0
    raw=kelly_fraction(probability,odds)*policy.fractional_kelly*policy.bankroll_units
    confidence=max(0.0,1.0-uncertainty)*max(0.0,1.0-correlation_penalty)
    sized=min(policy.max_stake_units,raw*confidence)
    return round(sized,4) if sized >= policy.min_stake_units else 0.0
