from ml.app.cycle16.operations import OperationalState, health_state, real_money_allowed

def test_operational_health_and_lock():
    s=health_state(collector_ok=True,pit_ok=True,ledger_ok=True)
    assert s['status']=='SAFE'
    assert real_money_allowed(OperationalState(True,True,False)) is False
