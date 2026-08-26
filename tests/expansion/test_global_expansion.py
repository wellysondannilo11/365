import pandas as pd
from ml.app.research.global_expansion import build_route_registry, classify_pit, canonical_match_key, deduplicate_matches, EVIDENCE_CLASSES, EMPIRICAL_CLASSES

def test_registry_has_global_routes():
    r=build_route_registry()
    assert len(r)>300
    countries={x.get('country') for x in r if x.get('country')!='GLOBAL'}
    assert {'Brazil','Argentina','England','Japan','USA','Mexico'}.issubset(countries)

def test_pit_is_temporal_and_fail_closed():
    assert classify_pit('2026-08-20T18:00:00Z','2026-08-20T17:59:00Z')=='VALID_PIT'
    assert classify_pit('2026-08-20T18:00:00Z','2026-08-20T18:01:00Z')=='PIT_INVALID'
    assert classify_pit(None,'2026-08-20T17:59:00Z')=='UNKNOWN'

def test_dedup_canonical_match():
    x=pd.DataFrame([{'date':'2026-01-01','home_team':'A','away_team':'B','competition':'X','season':'2026'}, {'date':'2026-01-01','home_team':'A','away_team':'B','competition':'X','season':'2026'}])
    assert len(deduplicate_matches(x))==1

def test_evidence_classes_fail_closed():
    assert EMPIRICAL_CLASSES.isdisjoint({'DEMO','MOCK','SYNTHETIC'})
    assert EVIDENCE_CLASSES.issuperset(EMPIRICAL_CLASSES)
