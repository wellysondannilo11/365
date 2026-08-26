import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_snapshot_unchanged_and_present():
    p=ROOT/'data/real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json'
    d=json.loads(p.read_text(encoding='utf8'))
    assert d['predictions_created']==5
    assert len(d['matches'])==5

def test_postmatch_never_invents_results_before_settlement():
    p=ROOT/'data/post_match_pilot/POST_MATCH_PILOT_RESULTS.csv'
    assert p.exists()
    text=p.read_text(encoding='utf8')
    assert 'NOT_COMPLETED_AT_AUDIT' in text
    assert 'UNKNOWN' in text
