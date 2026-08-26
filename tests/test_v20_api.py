from fastapi.testclient import TestClient
from ml.app.api import app

def test_v20_status_and_select():
    c=TestClient(app)
    s=c.get('/v20/status');assert s.status_code==200 and s.json()['version']=='20.0.0'
    r=c.post('/v20/select',json={'candidates':[{'event_id':'e1','market':'ML','selection':'Home','odds':2.2,'probability':.55,'data_quality':95,'calibration':.9,'uncertainty':.03,'model_agreement':.9}]})
    assert r.status_code==200
    assert 'opportunities' in r.json()
