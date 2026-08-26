import hashlib
from ml.app.cycle16.exact_pit import classify_observation


def row(**overrides):
    r={
        'event_id':'e1','kickoff_timestamp':'2026-08-25T20:00:00Z',
        'provider_timestamp':'2026-08-25T17:00:00Z','decision_timestamp':'2026-08-25T18:00:00Z',
        'bookmaker':'bet365','market':'1X2','selection':'home','odds':2.1,
        'source':'sharpapi','provenance':'file:raw.csv','raw_hash':hashlib.sha256(b'raw').hexdigest(),
        'temporal_evidence':'PROVIDER_NATIVE_SNAPSHOT'
    }
    r.update(overrides); return r


def test_missing_provider_timestamp_is_non_pit():
    assert classify_observation(row(provider_timestamp='')).status == 'NON_PIT'


def test_missing_provenance_is_invalid_not_exact():
    assert classify_observation(row(provenance='')).status == 'PIT_INVALID'


def test_short_hash_is_invalid_not_exact():
    assert classify_observation(row(raw_hash='abc')).status == 'PIT_INVALID'


def test_provider_after_decision_is_invalid():
    assert classify_observation(row(provider_timestamp='2026-08-25T19:00:00Z')).status == 'PIT_INVALID'


def test_decision_at_kickoff_is_invalid():
    assert classify_observation(row(decision_timestamp='2026-08-25T20:00:00Z')).status == 'PIT_INVALID'
