import pandas as pd
import pytest
from ml.app.research.odds import normalize_odds
from ml.app.v18.guards import require_strict_pit_odds, assert_no_future
from ml.app.v18.lineage import fingerprint_dataframe


def base_odds():
    return pd.DataFrame([{
        'event_id':'e1','bookmaker':'bk','market':'1X2','selection':'Home','price':2.1,
        'captured_at':'2026-01-01T10:00:00Z','available_at':'2026-01-01T10:00:00Z',
        'source_timestamp':'2026-01-01T10:00:00Z','source':'provider','availability_evidence':'PROVIDER_SNAPSHOT'
    }])


def test_v18_strict_pit_requires_explicit_availability():
    d=base_odds().drop(columns=['available_at'])
    with pytest.raises(ValueError, match='STRICT_PIT_ODDS_REQUIRES_AVAILABLE_AT'):
        normalize_odds(d, strict_pit=True)


def test_v18_strict_pit_rejects_undefined_availability():
    d=base_odds(); d['availability_evidence']='PREMATCH_ODDS_SET_NO_EXACT_TIMESTAMP'
    with pytest.raises(ValueError, match='STRICT_PIT_UNDEFENDED_AVAILABILITY'):
        normalize_odds(d, strict_pit=True)


def test_v18_future_timestamp_rejected():
    d=base_odds(); d['decision_time']='2025-12-31T23:00:00Z'
    with pytest.raises(ValueError, match='POINT_IN_TIME_VIOLATION'):
        assert_no_future(d)


def test_v18_fingerprint_reproducible():
    d=base_odds(); assert fingerprint_dataframe(d)==fingerprint_dataframe(d.copy())


def test_v18_strict_pit_accepts_provider_snapshot():
    require_strict_pit_odds(base_odds())
