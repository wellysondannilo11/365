from datetime import datetime,timezone
from app.v22.providers import normalize_odds_api
from app.v22.dataset import ResearchDataset

def test_provider_does_not_fake_source_timestamp(tmp_path):
    events=[{'id':'e','sport_key':'soccer_x','home_team':'A','away_team':'B','commence_time':'2026-08-20T20:00:00Z','bookmakers':[{'key':'x','markets':[{'key':'h2h','outcomes':[{'name':'A','price':2.0}]}]}]}]
    assert normalize_odds_api(events,datetime.now(timezone.utc))==[]

def test_dataset_hash_chain(tmp_path):
    d=ResearchDataset(str(tmp_path/'d.jsonl')); a=d.append({'event_id':'e','decision':'NO BET','mode':'SHADOW'}); b=d.append({'event_id':'e','decision':'BET','mode':'PAPER'}); assert a['prev_hash'] is None and b['prev_hash']==a['row_hash']

def test_modes_are_distinct():
    from app.v22.api_ext import scan
    import pytest
    with pytest.raises(Exception): scan('LIVE')
