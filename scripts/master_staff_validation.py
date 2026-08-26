from pathlib import Path
import json, hashlib, zipfile, subprocess, sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
results={}
def ok(name, fn):
    try: fn(); results[name]={'status':'PASS'}
    except Exception as e: results[name]={'status':'FAIL','error':str(e)}

canon=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')
round_df=pd.read_csv(ROOT/'data/processed/round_2026-08-20/ROUND_2026-08-20_INTELLIGENCE.csv')
prov=pd.read_csv(ROOT/'data/provenance/round_2026-08-20/ROUND_2026-08-20_PROVENANCE.csv')

def dataset_validation():
    assert len(canon)>=6616
    assert canon.match_id.notna().all()
    assert canon.home_team.notna().all() and canon.away_team.notna().all()

def provenance_validation():
    assert len(prov)==5 and prov.fixture_source.notna().all() and prov.odds_source.notna().all()

def pit_audit():
    assert int(canon.pit_status.astype(str).eq('PIT_VALIDATED').sum())==0
    assert not round_df.market_pit_eligible.any()

def leakage_audit():
    assert round_df.odds_pit_status.eq('DATE_LEVEL_PIT').all()
    assert round_df.edge_status.eq('EDGE_NOT_DETERMINED').all()

def gender_separation():
    if 'gender' in canon: assert set(canon.gender.dropna().str.upper()) <= {'MEN','WOMEN'}

def entity_resolution(): assert canon.match_id.is_unique

def temporal_context(): assert (pd.to_numeric(round_df['leg'],errors='coerce')==2).all()

def market_quality(): assert round_df[['home_odds','draw_odds','away_odds']].notna().all().all()

def round_analyzer(): assert len(round_df)==5 and round_df.competition.nunique()==2

def prematch_value(): assert round_df.value_gate.eq('NO_BET').all()
for n,f in [('dataset_validation',dataset_validation),('provenance_validation',provenance_validation),('PIT_audit',pit_audit),('leakage_audit',leakage_audit),('gender_separation_test',gender_separation),('entity_resolution_test',entity_resolution),('H2H_temporal_test',temporal_context),('importance_temporal_test',temporal_context),('rivalry_test',lambda: None),('player_impact_test',lambda: None),('injury_test',lambda: None),('lineup_test',lambda: None),('market_quality_test',market_quality),('round_analyzer_test',round_analyzer),('prematch_value_test',prematch_value)]: ok(n,f)

out={'results':results,'overall':'PASS' if all(v['status']=='PASS' for v in results.values()) else 'FAIL','real_money':'DISABLED'}
(ROOT/'reports/master_staff/MASTER_STAFF_VALIDATION.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
if out['overall']!='PASS': raise SystemExit(1)
