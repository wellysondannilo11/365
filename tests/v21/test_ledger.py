from pathlib import Path
from ml.app.v21.ledger import ImmutableEventLedger

def test_event_ledger_chain_and_settlement(tmp_path):
    l=ImmutableEventLedger(tmp_path/'ledger.jsonl',unit_brl=500)
    agg='e|AH|A'
    l.append('SIGNAL_CREATED',agg,{'decision':'BET','event_id':'e','market':'AH','selection':'A','odds':2.0,'stake_units':1.0,'league':'L'})
    assert l.verify_chain()['valid']
    l.append('RESULT_SETTLED',agg,{'status':'SETTLED','result':'WIN','pnl_units':1.0})
    assert l.performance()['units']==1.0
    assert l.verify_chain()['valid']

def test_duplicate_event_id_rejected(tmp_path):
    l=ImmutableEventLedger(tmp_path/'ledger.jsonl')
    l.append('SIGNAL_REJECTED','a',{'decision':'NO BET'},event_id='same')
    try:l.append('SIGNAL_REJECTED','a',{'decision':'NO BET'},event_id='same')
    except ValueError as e:assert str(e)=='DUPLICATE_EVENT_ID'
    else:raise AssertionError('expected duplicate rejection')
