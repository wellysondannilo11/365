from datetime import datetime, timezone, timedelta
from ml.app.v21.service import DecisionServiceV21

def row(now, **kw):
    d={'event_id':'e1','market':'h2h','selection':'A','odds':2.0,'probability':0.60,'available_at':(now-timedelta(seconds=1)).isoformat(),'league':'L','data_quality':100,'calibration':.9,'uncertainty':.03,'sample_size':100}
    d.update(kw);return d

def test_no_bet_is_recorded(tmp_path,monkeypatch):
    monkeypatch.setenv('MIN_EDGE','0.50')
    monkeypatch.setenv('MIN_EV','0.50')
    s=DecisionServiceV21();s.ledger.path=tmp_path/'ledger.jsonl';s.research.path=tmp_path/'research.jsonl'
    now=datetime.now(timezone.utc)
    out=s.select([row(now,probability=.51)],now,'SHADOW')
    assert out['no_bet_count']==1
    assert any(e['event_type']=='SIGNAL_REJECTED' for e in s.ledger.events())

def test_best_market_per_event_is_selected(tmp_path,monkeypatch):
    monkeypatch.setenv('MIN_EDGE','0.03');monkeypatch.setenv('MIN_EV','0.03')
    s=DecisionServiceV21();s.ledger.path=tmp_path/'ledger.jsonl';s.research.path=tmp_path/'research.jsonl'
    now=datetime.now(timezone.utc)
    rows=[row(now,market='h2h',selection='A',odds=2.0,probability=.62),row(now,market='ah',selection='A+0.5',odds=1.9,probability=.61)]
    out=s.select(rows,now,'PAPER')
    assert len(out['approved'])==1

def test_kill_switch_blocks_new_signal(tmp_path):
    s=DecisionServiceV21();s.ledger.path=tmp_path/'ledger.jsonl';s.research.path=tmp_path/'research.jsonl';s.risk.set_kill_switch(True)
    now=datetime.now(timezone.utc)
    out=s.select([row(now)],now,'SHADOW')
    assert out['approved']==[]
    assert any('GLOBAL_KILL_SWITCH' in str(e['payload'].get('no_bet_reason')) for e in s.ledger.events())
