from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class PointInTime:
    event_time: datetime
    source_time: datetime | None
    available_at: datetime
    ingested_at: datetime
    decision_time: datetime

    def is_usable(self) -> bool:
        return self.available_at <= self.decision_time

def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def assert_point_in_time(available_at: datetime, decision_time: datetime) -> None:
    if ensure_utc(available_at) > ensure_utc(decision_time):
        raise ValueError(f'POINT_IN_TIME_VIOLATION available_at={available_at} decision_time={decision_time}')
