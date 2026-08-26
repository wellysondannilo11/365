import pandas as pd
from ml.app.research.cycle4.pit import classify_pit, validate_decision_snapshot
from ml.app.research.cycle4.clv import calculate_clv
from ml.app.research.cycle4.settlement import settle_decimal

def test_exact_pit_requires_price_at_or_before_decision_and_provenance():
    r=classify_pit({'event_id':'e1','decision_time':'2026-01-01T12:00:00Z','entry_timestamp':'2026-01-01T11:55:00Z','entry_price':2.1,'source':'provider','source_record_id':'r1'})
    assert r.pit_status=='EXACT_PIT' and r.scientific_status=='SCIENTIFICALLY_ELIGIBLE'

def test_future_price_is_not_pit():
    r=classify_pit({'event_id':'e1','decision_time':'2026-01-01T12:00:00Z','entry_timestamp':'2026-01-01T12:01:00Z','entry_price':2.1,'source':'provider','source_record_id':'r1'})
    assert r.pit_status=='PIT_INVALID'

def test_date_only_evidence_is_non_pit():
    r=classify_pit({'event_id':'e1','decision_time':'2026-01-01T12:00:00Z','entry_timestamp':'2026-01-01T11:55:00Z','entry_price':2.1,'source':'football-data','source_record_id':'r1','availability_evidence':'DATE_ONLY'})
    assert r.pit_status=='NON_PIT'

def test_clv_semantics_and_settlement():
    v,status=calculate_clv(2.5,2.0,'2026-01-01T10:00:00Z','2026-01-01T12:00:00Z')
    assert status=='CLV_AVAILABLE' and v>0
    s=settle_decimal(2.5,1.0,'WIN')
    assert s['profit_units']==1.5 and s['roi']==1.5

def test_decision_snapshot_required_fields():
    assert 'entry_price' in validate_decision_snapshot({'event_id':'e1'})
