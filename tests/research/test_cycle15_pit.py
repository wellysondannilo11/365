import hashlib
from ml.app.research.cycle15.pit import classify_observation

def base():
    raw=b'provider-payload'
    return {
        'event_id':'e1','kickoff_timestamp':'2026-08-24T20:00:00Z',
        'provider_timestamp':'2026-08-24T18:00:00Z','decision_timestamp':'2026-08-24T19:00:00Z',
        'bookmaker':'book','market':'1X2','selection':'home','odds':2.1,
        'source':'sharpapi','raw_hash':hashlib.sha256(raw).hexdigest(),'provenance':'provider:snapshot-1'
    }

def test_exact_pit_requires_provider_time_before_decision_and_kickoff():
    r=classify_observation(base())
    assert r.status=='EXACT_PIT'

def test_provider_time_after_decision_is_invalid():
    x=base(); x['provider_timestamp']='2026-08-24T19:30:00Z'
    assert classify_observation(x).status=='PIT_INVALID'

def test_missing_raw_hash_is_invalid():
    x=base(); x['raw_hash']=''
    assert classify_observation(x).status=='PIT_INVALID'

def test_date_level_source_is_non_pit():
    x=base(); x['temporal_evidence']='DATE_LEVEL'
    assert classify_observation(x).status=='NON_PIT'
