from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
import math

PIT_EXACT = {'EXACT_PIT', 'VALID_PIT', 'PIT_VALIDATED', 'KNOWN_BEFORE_DECISION'}

@dataclass(frozen=True)
class PricingResult:
    market: str
    selection: str
    odds: Optional[float]
    model_probability: Optional[float]
    fair_odds: Optional[float]
    implied_probability: Optional[float]
    edge_raw: Optional[float]
    ev: Optional[float]
    pit_status: str
    decision: str
    reason: str
    confidence: str


def implied_probability(odds: float | None) -> float | None:
    try:
        o = float(odds)
        return 1.0 / o if o > 1.0 and math.isfinite(o) else None
    except (TypeError, ValueError):
        return None


def no_vig_probabilities(odds: list[float | None]) -> list[float | None]:
    probs = [implied_probability(x) for x in odds]
    total = sum(p for p in probs if p is not None)
    return [p / total if p is not None and total > 0 else None for p in probs]


def price_market(*, market: str, selection: str, odds: float | None,
                 model_probability: float | None, pit_status: str,
                 model_validated: bool, sample_size: int,
                 data_quality: float, min_edge: float = .05,
                 min_ev: float = .05, min_sample: int = 100,
                 min_quality: float = .70, confidence: str = 'LOW') -> PricingResult:
    imp = implied_probability(odds)
    fair = 1.0 / model_probability if model_probability and 0 < model_probability < 1 else None
    edge = model_probability - imp if model_probability is not None and imp is not None else None
    ev = model_probability * float(odds) - 1 if model_probability is not None and odds is not None and float(odds) > 1 else None
    reasons=[]
    if pit_status not in PIT_EXACT: reasons.append('PIT_NOT_EXACT_OR_VALID')
    if not model_validated: reasons.append('MODEL_NOT_VALIDATED')
    if sample_size < min_sample: reasons.append('SAMPLE_BELOW_GATE')
    if data_quality < min_quality: reasons.append('DATA_QUALITY_BELOW_GATE')
    if edge is None or ev is None: reasons.append('PRICE_OR_PROBABILITY_MISSING')
    if edge is not None and edge < min_edge: reasons.append('EDGE_BELOW_GATE')
    if ev is not None and ev < min_ev: reasons.append('EV_BELOW_GATE')
    if reasons:
        decision = 'WATCH' if pit_status not in PIT_EXACT and edge is not None else 'NO_BET'
    else:
        decision = 'VALUE_BET'
    return PricingResult(market, selection, odds, model_probability, fair, imp, edge, ev,
                         pit_status, decision, ';'.join(reasons) if reasons else 'QUALITY_GATE_PASSED', confidence)
