import json, hashlib
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')
errors=[]; warnings=[]
if df['match_id'].duplicated().any(): errors.append(f"duplicate match_id={int(df.match_id.duplicated().sum())}")
prov_a=pd.read_csv(ROOT/'data/canonical/football_historical_real_provenance.csv')
prov_b=pd.read_csv(ROOT/'data/provenance/expanded_real_provenance.csv') if (ROOT/'data/provenance/expanded_real_provenance.csv').exists() else pd.DataFrame(columns=['match_id'])
prov=pd.concat([prov_a,prov_b],ignore_index=True).drop_duplicates('match_id')
if set(df.match_id)-set(prov.match_id): errors.append(f"missing provenance rows={len(set(df.match_id)-set(prov.match_id))}")
# PIT ordering
for c in ['odds_timestamp','feature_timestamp','decision_timestamp','kickoff_timestamp']:
    if c in df: df[c]=pd.to_datetime(df[c],errors='coerce',utc=True)
if 'odds_timestamp' in df and 'decision_timestamp' in df:
    bad=(df.odds_timestamp.notna()&df.decision_timestamp.notna()&(df.odds_timestamp>df.decision_timestamp)).sum()
    if bad: errors.append(f"future odds timestamps={int(bad)}")
# feature timestamps must not be after kickoff
if 'feature_timestamp' in df:
    bad=(df.feature_timestamp.notna()&df.kickoff_timestamp.notna()&(df.feature_timestamp>df.kickoff_timestamp)).sum()
    if bad: errors.append(f"future feature timestamps={int(bad)}")
# forbidden evidence classes
for col in ['data_type','pit_status']:
    if col in df and df[col].astype(str).str.contains('MOCK|DEMO|SYNTHETIC',case=False,regex=True).any(): errors.append(f"forbidden evidence in {col}")
# provenance hashes present
if 'source_hash' in prov and prov.source_hash.isna().any(): warnings.append(f"provenance rows without source hash={int(prov.source_hash.isna().sum())}; expanded provenance links to source files but may not carry row-level hash")
status={'status':'PASS' if not errors else 'FAIL','errors':errors,'warnings':warnings,'matches':len(df),'provenance_rows':len(prov),'canonical_provenance_rows':len(prov_a),'expanded_provenance_rows':len(prov_b)}
(ROOT/'reports/context_intelligence/FINAL_VALIDATION.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
print(json.dumps(status,indent=2))
raise SystemExit(0 if not errors else 1)
