from fastapi.testclient import TestClient
from ml.app.api import app

client = TestClient(app)


def test_v19_pricing_endpoint():
    r = client.post('/pricing', json={
        'event_id':'e1','decision_time':'2026-01-01T10:00:00Z',
        'home_expected_goals':1.3,'away_expected_goals':1.0,'market_state':'PRE'
    })
    assert r.status_code == 200
    body = r.json()
    assert body['pricing_engine_version'] == '19.0.0'
    assert len(body['distribution']) > 50
    assert len(body['markets']) > 10


def test_v19_pricing_rejects_naive_decision_time():
    r = client.post('/pricing', json={
        'event_id':'e1','decision_time':'2026-01-01T10:00:00',
        'home_expected_goals':1.3,'away_expected_goals':1.0
    })
    assert r.status_code == 422


def test_v19_dislocation_endpoint_enforces_pit():
    payload = {
        'strict_pit': True,
        'decision_time': '2026-01-01T11:00:00Z',
        'model_rows': [{'event_id':'e1','market':'1X2','selection':'Home','line':None,'probability':0.30}],
        'market_rows': [
            {'event_id':'e1','bookmaker':'bk','market':'1X2','selection':'Home','line':None,'odds':4.0,'available_at':'2026-01-01T10:00:00Z','source_timestamp':'2026-01-01T10:00:00Z'},
            {'event_id':'e1','bookmaker':'bk','market':'1X2','selection':'Home','line':None,'odds':2.0,'available_at':'2026-01-01T12:00:00Z','source_timestamp':'2026-01-01T12:00:00Z'},
        ]
    }
    r = client.post('/dislocations', json=payload)
    assert r.status_code == 200
    assert r.json()['opportunities'][0]['market_odds'] == 4.0
