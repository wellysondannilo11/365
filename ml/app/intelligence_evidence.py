from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

class EvidenceClass(str, Enum):
    HISTORICAL_REAL = 'HISTORICAL_REAL'
    HISTORICAL_REAL_NON_PIT = 'HISTORICAL_REAL_NON_PIT'
    LIVE_REAL = 'LIVE_REAL'
    LIVE_REAL_UNVERIFIED = 'LIVE_REAL_UNVERIFIED'
    DEMO = 'DEMO'
    MOCK = 'MOCK'
    SYNTHETIC = 'SYNTHETIC'
    UNKNOWN = 'UNKNOWN'

class PITStatus(str, Enum):
    KNOWN_BEFORE_DECISION = 'KNOWN_BEFORE_DECISION'
    UNKNOWN = 'UNKNOWN'
    UNKNOWN_TIMESTAMP = 'UNKNOWN_TIMESTAMP'
    POSSIBLE_LEAKAGE = 'POSSIBLE_LEAKAGE'
    NOT_APPLICABLE = 'NOT_APPLICABLE'

REAL_EVIDENCE = {EvidenceClass.HISTORICAL_REAL, EvidenceClass.HISTORICAL_REAL_NON_PIT, EvidenceClass.LIVE_REAL}
NON_EVIDENCE = {EvidenceClass.DEMO, EvidenceClass.MOCK, EvidenceClass.SYNTHETIC}

@dataclass(frozen=True)
class Provenance:
    source: str
    source_url: str | None
    evidence_class: EvidenceClass
    source_timestamp: datetime | None
    captured_at: datetime | None
    available_at: datetime | None
    decision_time: datetime | None
    source_record_id: str | None = None
    raw_hash: str | None = None

    @staticmethod
    def parse_dt(value: Any) -> datetime | None:
        if value in (None, ''):
            return None
        try:
            x = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
            return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            return None

    def pit_status(self) -> PITStatus:
        if self.evidence_class in NON_EVIDENCE:
            return PITStatus.POSSIBLE_LEAKAGE
        if self.evidence_class == EvidenceClass.LIVE_REAL_UNVERIFIED:
            return PITStatus.UNKNOWN
        if self.decision_time is None:
            return PITStatus.UNKNOWN_TIMESTAMP
        available = self.available_at or self.source_timestamp or self.captured_at
        if available is None:
            return PITStatus.UNKNOWN_TIMESTAMP
        return PITStatus.KNOWN_BEFORE_DECISION if available <= self.decision_time else PITStatus.POSSIBLE_LEAKAGE

    def is_empirical(self) -> bool:
        return self.evidence_class in REAL_EVIDENCE

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.evidence_class == EvidenceClass.LIVE_REAL and self.source_timestamp is None:
            errors.append('LIVE_REAL_REQUIRES_SOURCE_TIMESTAMP')
        if self.captured_at and self.source_timestamp and self.captured_at < self.source_timestamp:
            errors.append('CAPTURED_BEFORE_SOURCE')
        if self.available_at and self.decision_time and self.available_at > self.decision_time:
            errors.append('AVAILABLE_AFTER_DECISION')
        if self.source_timestamp and self.decision_time and self.source_timestamp > self.decision_time:
            errors.append('SOURCE_AFTER_DECISION')
        if self.pit_status() == PITStatus.POSSIBLE_LEAKAGE:
            errors.append('PIT_VIOLATION')
        return errors

def classify_source(source: str | None, live: bool = False, synthetic: bool = False, mock: bool = False, demo: bool = False, pit_known: bool = False) -> EvidenceClass:
    if synthetic: return EvidenceClass.SYNTHETIC
    if mock: return EvidenceClass.MOCK
    if demo: return EvidenceClass.DEMO
    if live: return EvidenceClass.LIVE_REAL if pit_known else EvidenceClass.LIVE_REAL_UNVERIFIED
    if pit_known: return EvidenceClass.HISTORICAL_REAL
    if source: return EvidenceClass.HISTORICAL_REAL_NON_PIT
    return EvidenceClass.UNKNOWN

def quality_gate(*, data_quality: float, pit_status: PITStatus, odds_verified: bool, model_validated: bool, sample_size: int, min_sample: int = 30, min_quality: float = .70) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if data_quality < min_quality: reasons.append('DATA_QUALITY_BELOW_GATE')
    if pit_status != PITStatus.KNOWN_BEFORE_DECISION: reasons.append('PIT_NOT_PROVEN')
    if not odds_verified: reasons.append('ODDS_NOT_VERIFIED')
    if not model_validated: reasons.append('MODEL_NOT_VALIDATED')
    if sample_size < min_sample: reasons.append('SAMPLE_BELOW_GATE')
    return (not reasons, reasons)
