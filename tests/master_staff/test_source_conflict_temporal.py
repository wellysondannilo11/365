from ml.app.master_staff.source_conflict import Evidence, temporal_conflict

def test_future_source_is_blocked():
    r=temporal_conflict([Evidence('A',1,'2026-08-20T10:00:00Z'),Evidence('B',2,'2026-08-20T12:00:00Z')],'2026-08-20T11:00:00Z')
    assert r['status']=='LEAKAGE'
    assert r['feature_blocked'] is True
