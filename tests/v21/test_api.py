from fastapi.testclient import TestClient
from ml.app.api import app

def test_v21_status():
    c=TestClient(app);r=c.get('/v21/status');assert r.status_code==200;assert r.json()['version']=='21.0.0'

def test_v21_select_pit_block():
    c=TestClient(app)
    payload={'decision_time':'2026-08-19T20:00:00+00:00','mode':'SHADOW','candidates':[{'event_id':'e','market':'h2h','selection':'A','odds':2,'probability':.6,'available_at':'2026-08-19T20:01:00+00:00'}]}
    r=c.post('/v21/select',json=payload);assert r.status_code==200;assert r.json()['no_bet_count']==1
