import json
from ml.app.research.cycle15.prospective import collect_once
from ml.app.research.cycle15.production import promotion_gate

def test_missing_provider_key_fails_closed(monkeypatch,tmp_path):
    monkeypatch.delenv('SHARPAPI_API_KEY',raising=False)
    out=collect_once('https://example.invalid',tmp_path)
    assert out['status']=='BLOCKED_AUTH'

def test_production_gate_keeps_real_money_disabled():
    g=promotion_gate({'pit_events':100,'oos_bets':100,'clv_mean':0.01,'walk_forward_folds':5,'robustness':'PASS'})
    assert g['real_money']=='DISABLED'
    assert g['trading_approved'] is False
