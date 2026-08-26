from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import hashlib, json, time
from typing import Any, Callable, Protocol

class FeedStatus(str, Enum):
    ONLINE='FEED_ONLINE'; DELAYED='FEED_DELAYED'; STALE='FEED_STALE'; OFFLINE='FEED_OFFLINE'; BLOCKED='DATA_QUALITY_BLOCK'

@dataclass(frozen=True)
class FeedSnapshot:
    source: str
    event_id: str
    captured_at: datetime
    received_at: datetime
    payload_hash: str
    sequence: int | None = None
    status: FeedStatus = FeedStatus.ONLINE

    @property
    def age_seconds(self) -> float:
        return max(0.0, (self.received_at - self.captured_at).total_seconds())

@dataclass
class FeedHealth:
    source: str
    max_age_seconds: float = 20.0
    delayed_after_seconds: float = 5.0
    last_received_at: datetime | None = None
    last_captured_at: datetime | None = None
    consecutive_failures: int = 0
    status: FeedStatus = FeedStatus.OFFLINE

    def observe(self, captured_at: datetime, received_at: datetime | None = None) -> FeedStatus:
        received_at = received_at or datetime.now(timezone.utc)
        if captured_at.tzinfo is None or received_at.tzinfo is None:
            self.status = FeedStatus.BLOCKED
            return self.status
        age = max(0.0, (received_at - captured_at).total_seconds())
        self.last_received_at, self.last_captured_at = received_at, captured_at
        self.consecutive_failures = 0
        self.status = FeedStatus.STALE if age > self.max_age_seconds else FeedStatus.DELAYED if age > self.delayed_after_seconds else FeedStatus.ONLINE
        return self.status

    def fail(self) -> FeedStatus:
        self.consecutive_failures += 1
        self.status = FeedStatus.OFFLINE
        return self.status

    def can_decide(self) -> bool:
        return self.status == FeedStatus.ONLINE

class SportsDataProvider(Protocol):
    name: str
    def fetch(self, event_id: str) -> dict[str, Any]: ...

class OddsProvider(Protocol):
    name: str
    def fetch_odds(self, event_id: str) -> list[dict[str, Any]]: ...

class LiveEventProvider(Protocol):
    name: str
    def fetch_live(self, event_id: str) -> dict[str, Any]: ...

class ResultsProvider(Protocol):
    name: str
    def fetch_result(self, event_id: str) -> dict[str, Any]: ...

class ResilientPoller:
    def __init__(self, *, retries: int = 3, base_delay: float = 0.25, max_delay: float = 4.0):
        self.retries, self.base_delay, self.max_delay = retries, base_delay, max_delay

    def call(self, fn: Callable[[], Any]) -> Any:
        last = None
        for attempt in range(self.retries + 1):
            try:
                return fn()
            except Exception as exc:
                last = exc
                if attempt >= self.retries:
                    raise
                time.sleep(min(self.max_delay, self.base_delay * (2 ** attempt)))
        raise last  # pragma: no cover

def canonical_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str).encode()
    return hashlib.sha256(raw).hexdigest()

def validate_live_snapshot(payload: dict[str, Any], decision_time: datetime) -> tuple[bool, list[str]]:
    reasons=[]
    if decision_time.tzinfo is None: reasons.append('DECISION_TIME_NOT_TZ_AWARE')
    for key in ('event_id','captured_at'):
        if not payload.get(key): reasons.append(f'MISSING_{key.upper()}')
    try: captured=datetime.fromisoformat(str(payload['captured_at']).replace('Z','+00:00'))
    except Exception: captured=None
    if captured is None or captured.tzinfo is None: reasons.append('INVALID_CAPTURED_AT')
    elif decision_time.tzinfo and captured > decision_time: reasons.append('FUTURE_DATA')
    if payload.get('sequence') is not None and int(payload['sequence']) < 0: reasons.append('INVALID_SEQUENCE')
    return not reasons, reasons
