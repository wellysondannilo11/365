import importlib, pytest
m=importlib.import_module('scripts.global.source_state')

def test_states_are_monotonic():
    assert m.promote('DISCOVERED','ACCESSIBLE') == 'ACCESSIBLE'
    assert m.promote('ACCESSIBLE','DOWNLOADED') == 'DOWNLOADED'
    assert m.promote('DOWNLOADED','MATERIALIZED') == 'MATERIALIZED'
    assert m.promote('MATERIALIZED','VALIDATED') == 'VALIDATED'

def test_cannot_skip_backward():
    with pytest.raises(ValueError): m.promote('VALIDATED','DOWNLOADED')

def test_blocked_is_not_acquired():
    assert not m.is_materialized({'state':'BLOCKED','materialized':False})
    assert not m.is_materialized({'state':'DISCOVERED','materialized':True})
    assert m.is_materialized({'state':'VALIDATED','materialized':True})
