from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from math import isfinite

class MatchState(str, Enum):
    EARLY_1H='EARLY_1H'; MID_1H='MID_1H'; LATE_1H='LATE_1H'; HALFTIME='HALFTIME'
    EARLY_2H='EARLY_2H'; MID_2H='MID_2H'; LATE_2H='LATE_2H'; EXTRA_TIME='EXTRA_TIME'; UNKNOWN='UNKNOWN'

@dataclass(frozen=True)
class LiveSnapshot:
    event_id: str
    source: str
    source_timestamp: datetime
    captured_at: datetime
    minute: int
    score_home: int
    score_away: int
    shots_home: int | None = None
    shots_away: int | None = None
    shots_on_target_home: int | None = None
    shots_on_target_away: int | None = None
    xg_home: float | None = None
    xg_away: float | None = None
    possession_home: float | None = None
    dangerous_attacks_home: int | None = None
    dangerous_attacks_away: int | None = None
    corners_home: int | None = None
    corners_away: int | None = None
    cards_home: int | None = None
    cards_away: int | None = None
    red_home: int | None = None
    red_away: int | None = None
    substitutions_home: int | None = None
    substitutions_away: int | None = None
    big_chances_home: int | None = None
    big_chances_away: int | None = None
    halftime: bool = False

    def as_dict(self): return asdict(self)

class LiveIntelligenceEngine:
    def __init__(self, stale_seconds: int = 90):
        self.stale_seconds = stale_seconds
        self.history: dict[str, list[LiveSnapshot]] = {}

    @staticmethod
    def state(minute: int, halftime: bool = False) -> MatchState:
        if halftime: return MatchState.HALFTIME
        if minute < 0 or minute > 130: return MatchState.UNKNOWN
        if minute <= 15: return MatchState.EARLY_1H
        if minute <= 30: return MatchState.MID_1H
        if minute <= 45: return MatchState.LATE_1H
        if minute <= 60: return MatchState.EARLY_2H
        if minute <= 75: return MatchState.MID_2H
        if minute <= 90: return MatchState.LATE_2H
        return MatchState.EXTRA_TIME

    def ingest(self, snapshot: LiveSnapshot, now: datetime | None = None) -> dict:
        now = now or datetime.now(timezone.utc)
        errors=[]
        if snapshot.source_timestamp.tzinfo is None or snapshot.captured_at.tzinfo is None: errors.append('TIMESTAMP_MUST_BE_TIMEZONE_AWARE')
        if snapshot.source_timestamp > now or snapshot.captured_at > now: errors.append('FUTURE_TIMESTAMP')
        if (now-snapshot.source_timestamp).total_seconds() > self.stale_seconds: errors.append('STALE_SOURCE')
        if snapshot.minute < 0 or snapshot.minute > 130: errors.append('INVALID_MINUTE')
        if min(snapshot.score_home, snapshot.score_away) < 0: errors.append('NEGATIVE_SCORE')
        for a,b in [('shots_home','shots_on_target_home'),('shots_away','shots_on_target_away')]:
            va,vb=getattr(snapshot,a),getattr(snapshot,b)
            if va is not None and vb is not None and vb>va: errors.append(f'{b.upper()}_GT_{a.upper()}')
        if snapshot.possession_home is not None and not 0 <= snapshot.possession_home <= 100: errors.append('INVALID_POSSESSION')
        if errors: return {'status':'BLOCK','errors':errors}
        rows=self.history.setdefault(snapshot.event_id,[])
        if rows and snapshot.source_timestamp < rows[-1].source_timestamp: errors.append('OUT_OF_ORDER_SOURCE_TIMESTAMP')
        if rows and snapshot.source_timestamp == rows[-1].source_timestamp: errors.append('DUPLICATE_SOURCE_TIMESTAMP')
        if errors: return {'status':'BLOCK','errors':errors}
        rows.append(snapshot)
        return {'status':'PASS','state':self.state(snapshot.minute,snapshot.halftime),'snapshot':snapshot.as_dict()}

    def dynamics(self, event_id: str) -> dict:
        rows=self.history.get(event_id,[])
        if not rows: return {'status':'NOT_DETERMINED'}
        cur=rows[-1]
        prev=rows[-2] if len(rows)>1 else None
        def rate(a,b,minutes):
            if a is None or b is None or minutes<=0:return None
            return (a-b)/minutes*90
        minutes=max(1,(cur.minute-(prev.minute if prev else 0)))
        total_shots=(cur.shots_home or 0)+(cur.shots_away or 0)
        total_sot=(cur.shots_on_target_home or 0)+(cur.shots_on_target_away or 0)
        total_xg=(cur.xg_home or 0)+(cur.xg_away or 0)
        pressure_home=0.; pressure_away=0.
        if cur.dangerous_attacks_home is not None and cur.dangerous_attacks_away is not None:
            den=max(1,cur.dangerous_attacks_home+cur.dangerous_attacks_away); pressure_home += cur.dangerous_attacks_home/den; pressure_away += cur.dangerous_attacks_away/den
        if cur.xg_home is not None and cur.xg_away is not None:
            den=max(1e-9,total_xg); pressure_home=.5*pressure_home+.5*cur.xg_home/den; pressure_away=.5*pressure_away+.5*cur.xg_away/den
        if total_xg/minutes*90 >= 2.4 or total_sot/minutes*90 >= 7: tempo='VERY_HIGH'
        elif total_xg/minutes*90 >= 1.5 or total_shots/minutes*90 >= 18: tempo='HIGH'
        elif total_shots/minutes*90 >= 10: tempo='MEDIUM'
        elif total_shots: tempo='LOW'
        else: tempo='UNKNOWN'
        return {'status':'OK','match_state':self.state(cur.minute,cur.halftime).value,'game_tempo':tempo,'pressure_home':round(pressure_home,4),'pressure_away':round(pressure_away,4),'shot_rate_90':round(total_shots/minutes*90,4),'sot_rate_90':round(total_sot/minutes*90,4),'xg_rate_90':round(total_xg/minutes*90,4),'score':(cur.score_home,cur.score_away),'minute':cur.minute,'snapshot_count':len(rows)}
