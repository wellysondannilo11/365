from ml.app.v21.notifications import NullProvider, format_signal

def test_missing_telegram_is_nonfatal():
    n=NullProvider();assert not n.enabled;assert n.send('x') is False

def test_signal_format_contains_quant_fields():
    s=format_signal({'event_id':'e','league':'L','market':'AH','selection':'A','odds':1.8,'fair_odds':1.6,'edge':.1,'ev':.12,'stake':1})
    assert 'Odd: 1.80' in s and 'Edge: +10.0%' in s and 'Stake: 1.00u' in s
