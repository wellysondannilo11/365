import pytest
from ml.app.v16.decision_replay import ReplayError, assert_reproducible, replay_decision


def test_replay_is_reproducible():
    s={'decision_id':'d1','decision_time':'2025-01-01T12:00:00Z','dataset_version':'ds1','feature_version':'f1','model_version':'m1','x':2}
    out=assert_reproducible(s, lambda snap,t: {'x':snap['x']}, lambda f: {'probability':0.5})
    assert out['decision_id']=='d1'
    assert out['replay_hash']


def test_replay_requires_versions():
    s={'decision_id':'d1','decision_time':'2025-01-01T12:00:00Z'}
    with pytest.raises(ReplayError, match='REPLAY_MISSING_METADATA'):
        replay_decision(s, lambda a,b: {}, lambda f: {})
