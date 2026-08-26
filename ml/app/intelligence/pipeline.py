from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from ..intelligence_evidence import EvidenceClass, PITStatus, Provenance, quality_gate
from .live import LiveIntelligenceEngine, LiveSnapshot
from .pricing import LiveMarketPricer

@dataclass
class IntelligenceResult:
    decision: str
    reason: str
    data_quality: float
    pit_status: str
    evidence_class: str
    model_probability: float | None = None
    fair_odds: float | None = None
    edge: float | None = None
    ev: float | None = None

class FootballIntelligencePipeline:
    """Fail-closed orchestration layer for pre-match and LIVE research.

    It deliberately does not manufacture a probability. The caller must provide
    a validated model probability and provenance; otherwise the result is WAIT
    or NO BET rather than a synthetic edge.
    """
    def __init__(self, min_edge=.05, min_ev=.05):
        self.live=LiveIntelligenceEngine(); self.pricer=LiveMarketPricer(min_edge=min_edge,min_ev=min_ev)

    def evaluate_market(self, row: dict[str,Any], *, model_probability: float|None, uncertainty: float, provenance: Provenance, data_quality: float, sample_size: int, model_validated: bool) -> IntelligenceResult:
        pit=provenance.pit_status()
        ok,reasons=quality_gate(data_quality=data_quality,pit_status=pit,odds_verified=float(row.get('odds',0))>1,model_validated=model_validated,sample_size=sample_size)
        if not ok:
            return IntelligenceResult('WAIT' if 'PIT_NOT_PROVEN' in reasons or 'ODDS_NOT_VERIFIED' in reasons else 'NO BET','|'.join(reasons),data_quality,pit.value,provenance.evidence_class.value,model_probability)
        a=self.pricer.assess(row,model_probability,uncertainty,pit.value,model_validated)
        return IntelligenceResult(a['status'],a['reason'],data_quality,pit.value,provenance.evidence_class.value,a['robo_probability'],a['fair_odds'],a['edge'],a['ev'])
