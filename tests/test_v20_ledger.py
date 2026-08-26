from ml.app.v20.ledger import LedgerV20,LedgerRecord
from pathlib import Path

def rec(i):
    return LedgerRecord(i,'e','2026-08-19T12:00:00+00:00','League','BR','2026','ML','Home',2.0,.5,250,None,0,.6,1.6667,.1,.2,None,'20','fp','PASS','BET')

def test_immutable_ledger_and_export(tmp_path):
    l=LedgerV20(tmp_path/'ledger.jsonl')
    l.append(rec('x'))
    try:l.append(rec('x'));assert False
    except ValueError:pass
    l.settle('x','WIN',1.8)
    assert l.rows()[0]['pnl_units']==.5
    out=l.export_xlsx(tmp_path/'results.xlsx')
    assert Path(out).exists()
