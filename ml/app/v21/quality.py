from __future__ import annotations
from datetime import datetime, timezone

def validate_market_snapshot(row: dict, decision_time: datetime, *, max_age_seconds: float=20.0):
    reasons=[]
    if decision_time.tzinfo is None: reasons.append('DECISION_TIME_NOT_TZ_AWARE')
    for key in ('event_id','market','selection','odds','available_at'):
        if key not in row or row[key] in (None,''): reasons.append(f'MISSING_{key.upper()}')
    try: odds=float(row.get('odds'))
    except Exception: odds=None
    if odds is None or odds<=1: reasons.append('INVALID_ODDS')
    try: available=datetime.fromisoformat(str(row['available_at']).replace('Z','+00:00'))
    except Exception: available=None
    if available is None or available.tzinfo is None: reasons.append('INVALID_AVAILABLE_AT')
    elif decision_time.tzinfo and available>decision_time: reasons.append('POINT_IN_TIME_VIOLATION')
    elif decision_time.tzinfo and (decision_time-available).total_seconds()>max_age_seconds and row.get('live',False): reasons.append('STALE_ODDS')
    if row.get('data_quality') is not None and float(row['data_quality'])<80: reasons.append('LOW_DATA_QUALITY')
    return {'ok':not reasons,'reasons':reasons}

def validate_live_state(state: dict, decision_time: datetime, *, max_age_seconds=20):
    reasons=[]
    for key in ('event_id','captured_at','minute','home_goals','away_goals','home_xg','away_xg'):
        if key not in state: reasons.append(f'MISSING_{key.upper()}')
    try: captured=datetime.fromisoformat(str(state.get('captured_at')).replace('Z','+00:00'))
    except Exception: captured=None
    if captured is None or captured.tzinfo is None: reasons.append('INVALID_CAPTURED_AT')
    elif decision_time.tzinfo and captured>decision_time: reasons.append('FUTURE_DATA')
    elif decision_time.tzinfo and (decision_time-captured).total_seconds()>max_age_seconds: reasons.append('STALE_LIVE_FEED')
    return {'ok':not reasons,'reasons':reasons}
