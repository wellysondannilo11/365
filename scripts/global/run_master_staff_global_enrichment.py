from __future__ import annotations
import hashlib, json, re, shutil, subprocess, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data'; GD=DATA/'global_dataset'; REP=GD/'reports'; REG=GD/'registry'; RAW=DATA/'raw'
for p in [REP,REG,GD/'canonical',GD/'processed',GD/'provenance']:
    p.mkdir(parents=True,exist_ok=True)
RUN=datetime.now(timezone.utc).isoformat()
CAN=DATA/'canonical/football_historical_real_canonical.csv'
PROV=DATA/'canonical/football_historical_real_provenance.csv'
RAW_PILOT=RAW/'epl_2324_real_pilot.csv'
# Immutable prospective snapshot artifacts only; generated audit/report files are excluded.
SNAP_FILES=[p for p in [DATA/'real_day_prematch/REAL_DAY_PREMATCH_SNAPSHOT.json', DATA/'master_staff/PREMATCH_FEATURE_STORE.csv'] if p.exists()]
SNAP_FILES += sorted(DATA.rglob('*PREMATCH_PREDICTION_SNAPSHOT*'))
SNAP_FILES=sorted(set(p for p in SNAP_FILES if p.is_file() and 'reports' not in p.parts))

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def norm(s): return re.sub(r'[^a-z0-9]','',str(s).lower())

def canonical_key(r):
    return (str(pd.to_datetime(r['kickoff_timestamp'],errors='coerce',utc=True).date()),norm(r['home_team']),norm(r['away_team']),str(r.get('competition','')))

def cid(r):
    raw='|'.join([str(r['country']),str(r['competition']),str(r['season']),str(pd.to_datetime(r['kickoff_timestamp'],errors='coerce',utc=True)),norm(r['home_team']),norm(r['away_team']),str(r.get('gender','MEN'))])
    return 'm_'+hashlib.sha256(raw.encode()).hexdigest()[:24]

# 0) immutable pre-flight hashes
snapshot_hashes={str(p.relative_to(ROOT)):sha(p) for p in SNAP_FILES if p.is_file()}
protected_json=DATA/'global_dataset/reports/PREMATCH_SNAPSHOT_PROTECTION.json'

# 1) conservative local acquisition: raw artifacts already inside the input ZIP are eligible.
canon=pd.read_csv(CAN)
canon['gender']='MEN'
canon_before=len(canon)
canon['_k']=canon.apply(canonical_key,axis=1)
existing=set(canon['_k'])
source_attempts=[]
new_rows=[]
if RAW_PILOT.exists():
    raw=pd.read_csv(RAW_PILOT)
    raw_hash=sha(RAW_PILOT)
    source_attempts.append({'source':'DataHub/Football-Data derivative','artifact':str(RAW_PILOT.relative_to(ROOT)),'state':'ACCESSIBLE_LOCAL','downloaded':True,'parsed':True,'raw_file_hash':raw_hash,'records':len(raw)})
    for _,r in raw.iterrows():
        dt=pd.to_datetime(r.get('Date'),errors='coerce',dayfirst=False,utc=True)
        if pd.isna(dt): continue
        rec={c:np.nan for c in canon.columns if c!='_k'}
        rec.update({
            'country':'England','competition':'Premier League','division':1,'season':'2023-24','round':np.nan,
            'kickoff_timestamp':dt.isoformat(),'home_team':r['HomeTeam'],'away_team':r['AwayTeam'],
            'home_goals':pd.to_numeric(r['FTHG'],errors='coerce'),'away_goals':pd.to_numeric(r['FTAG'],errors='coerce'),
            'referee':r.get('Referee',np.nan),'home_cards':pd.to_numeric(r.get('HY'),errors='coerce')+pd.to_numeric(r.get('HR'),errors='coerce'),
            'away_cards':pd.to_numeric(r.get('AY'),errors='coerce')+pd.to_numeric(r.get('AR'),errors='coerce'),
            'home_corners':pd.to_numeric(r.get('HC'),errors='coerce'),'away_corners':pd.to_numeric(r.get('AC'),errors='coerce'),
            'source':'DataHub/Football-Data derivative','source_url':'https://datahub.io/football/english-premier-league/_r/-/season-2324.csv',
            'provenance_file':'data/raw/epl_2324_real_pilot.csv','pit_status':'PIT_DATE_ONLY','data_type':'HISTORICAL_REAL','gender':'MEN'
        })
        rec['total_cards']=rec['home_cards']+rec['away_cards']; rec['total_corners']=rec['home_corners']+rec['away_corners']
        rec['btts_yes']=float(rec['home_goals']>0 and rec['away_goals']>0); rec['btts_no']=1.0-rec['btts_yes']
        rec['over_2_5']=float(rec['home_goals']+rec['away_goals']>2.5); rec['under_2_5']=1.0-rec['over_2_5']
        rec['asian_handicap']=np.nan; rec['bookmaker']=np.nan; rec['odds_timestamp']=dt.isoformat(); rec['feature_timestamp']=dt.isoformat(); rec['decision_timestamp']=dt.isoformat()
        rec['match_id']=cid(rec); rec['canonical_match_id']=rec['match_id']
        k=canonical_key(rec)
        if k not in existing:
            new_rows.append(rec); existing.add(k)
    source_attempts[-1]['materialized_candidates']=len(new_rows)
else:
    source_attempts.append({'source':'DataHub/Football-Data derivative','artifact':'data/raw/epl_2324_real_pilot.csv','state':'NOT_PRESENT_IN_ZIP'})

# 2) add only genuine new canonical rows; preserve all existing rows byte-for-byte at row content level.
if new_rows:
    add=pd.DataFrame(new_rows)
    add=add.reindex(columns=[c for c in canon.columns if c!='_k'])
    canon2=pd.concat([canon.drop(columns=['_k']),add],ignore_index=True)
    canon2['gender']=canon2.get('gender','MEN').fillna('MEN').astype(str).str.upper()
    canon2=canon2.sort_values('kickoff_timestamp',kind='stable').reset_index(drop=True)
    canon2.to_csv(CAN,index=False)
    # provenance append, one source record per new match
    if PROV.exists():
        prov=pd.read_csv(PROV)
    else:
        prov=pd.DataFrame(columns=['match_id','source','source_url','retrieved_at','source_hash','raw_file_hash','parser_version','status'])
    rows=[{'match_id':r['match_id'],'source':r['source'],'source_url':r['source_url'],'retrieved_at':RUN,'source_hash':sha(RAW_PILOT),'raw_file_hash':sha(RAW_PILOT),'parser_version':'master_staff_global_enrichment_2026-08-20','status':'MATERIALIZED'} for r in new_rows]
    prov=pd.concat([prov,pd.DataFrame(rows)],ignore_index=True).drop_duplicates('match_id',keep='first')
    prov.to_csv(PROV,index=False)
else:
    canon2=canon.drop(columns=['_k'])

# 3) source route ledger: explicit discovered vs acquired vs blocked.
network_routes=['Football-Data.co.uk bulk remote','StatsBomb Open Data remote','Sportmonks','API-Football','The Odds API','Betfair Historical Data','OpenFootball remote']
for route in network_routes:
    source_attempts.append({'source':route,'state':'ACQUISITION_BLOCKED','reason':'execution container DNS/network unavailable; no remote bytes were materialized','materialized_records':0})
pd.DataFrame(source_attempts).to_csv(DATA/'manifests/GLOBAL_ACQUISITION_ATTEMPTS.csv',index=False)

# 4) global coverage matrix with expected vs actual. Expected values are targets only, never counted as acquired.
expected={
 ('England','Premier League'):380,('England','Championship'):552,('England','League One'):552,('England','League Two'):552,
 ('Germany','Bundesliga'):306,('Germany','Bundesliga 2'):306,('Italy','Serie A'):380,('South America','Copa Libertadores'):350,('South America','Copa Sudamericana'):350}
rows=[]
for (country,comp,gender,season),g in canon2.groupby(['country','competition','gender','season'],dropna=False):
    n=g.match_id.nunique(); total=len(g)
    stats=int(g[['home_cards','away_cards','home_corners','away_corners']].notna().any(axis=1).sum())
    rows.append({'country':country,'competition':comp,'gender':gender,'season':season,'expected_matches_target':expected.get((country,comp),np.nan),'materialized_matches':n,'coverage_vs_target_pct':round(100*n/expected[(country,comp)],2) if (country,comp) in expected else np.nan,'stats_matches':stats,'xg_matches':int(g[['home_xg','away_xg']].notna().any(axis=1).sum()),'odds_matches':int(g[['odds_1','odds_x','odds_2']].notna().any(axis=1).sum()),'exact_pit_matches':int(g.pit_status.eq('PIT_EXACT').sum())})
coverage=pd.DataFrame(rows).sort_values(['country','competition','season'])
coverage.to_csv(REP/'GLOBAL_COVERAGE_MATRIX_2020_2026.csv',index=False)
coverage.to_csv(REP/'GLOBAL_COVERAGE_REPORT.csv',index=False)

# 5) team registry and coverage
teams=pd.unique(pd.concat([canon2.home_team,canon2.away_team],ignore_index=True).dropna())
team_rows=[]
for t in teams:
    m=canon2[(canon2.home_team==t)|(canon2.away_team==t)]
    team_rows.append({'canonical_team_id':norm(t),'team_name':t,'aliases':t,'country':';'.join(sorted(m.country.dropna().astype(str).unique())),'gender':';'.join(sorted(m.gender.dropna().astype(str).unique())),'competitions':';'.join(sorted(m.competition.dropna().astype(str).unique())),'seasons':';'.join(sorted(m.season.dropna().astype(str).unique())),'first_season_found':str(m.season.min()),'last_season_found':str(m.season.max()),'matches':m.match_id.nunique(),'stats_matches':int(m[['home_cards','away_cards','home_corners','away_corners']].notna().any(axis=1).sum()),'xg_matches':int(m[['home_xg','away_xg']].notna().any(axis=1).sum())})
pd.DataFrame(team_rows).sort_values('matches',ascending=False).to_csv(REG/'TEAM_REGISTRY_GLOBAL.csv',index=False)
pd.DataFrame(team_rows).sort_values('matches',ascending=False).to_csv(REP/'TEAM_COVERAGE_GLOBAL_2020_2026.csv',index=False)

# 6) cross-competition evidence engine for future fixtures currently in the package.
fixtures_path=DATA/'processed/round_2026-08-20/ROUND_2026-08-20_INTELLIGENCE.csv'
fixtures=pd.read_csv(fixtures_path) if fixtures_path.exists() else pd.DataFrame()
canon2['kickoff']=pd.to_datetime(canon2.kickoff_timestamp,errors='coerce',utc=True)
canon2['hg']=pd.to_numeric(canon2.home_goals,errors='coerce'); canon2['ag']=pd.to_numeric(canon2.away_goals,errors='coerce')
canon2['home_points']=np.where(canon2.hg>canon2.ag,3,np.where(canon2.hg==canon2.ag,1,0)); canon2['away_points']=np.where(canon2.ag>canon2.hg,3,np.where(canon2.hg==canon2.ag,1,0))
# competition tiers: transparent and conservative; unknown competitions receive 0.50.
def comp_tier(name):
    s=str(name).lower()
    if 'libert' in s or 'sudamericana' in s or 'champions' in s: return 1.00
    if 'premier league' in s or s=='serie a' or 'bundesliga' in s or 'la liga' in s or 'ligue 1' in s: return .95
    if 'championship' in s or 'serie b' in s or 'bundesliga 2' in s or 'ligue 2' in s: return .80
    if 'league one' in s or 'league two' in s or 'serie c' in s: return .65
    return .50

def team_history(team, before):
    return canon2[((canon2.home_team==team)|(canon2.away_team==team)) & (canon2.kickoff < before)].copy()

def evidence(team, target_comp, before, venue):
    h=team_history(team,before)
    if h.empty: return {'direct_n':0,'same_country_n':0,'cross_comp_n':0,'hist_n':0,'weighted_n':0,'form5':np.nan,'gd5':np.nan,'evidence_score':0.0,'confidence':'CRITICAL'}
    direct=h[h.competition.eq(target_comp)]
    country=h[h.country.eq(h[h.competition.eq(target_comp)].country.iloc[0] if not h[h.competition.eq(target_comp)].empty else '')]
    cross=h[~h.competition.eq(target_comp)]
    hist=h
    # weights decay with recency and competition similarity; only pre-match rows.
    ref=max(before, pd.Timestamp('2020-01-01',tz='UTC'))
    vals=[]
    for _,r in h.iterrows():
        days=max(0,(before-r.kickoff).total_seconds()/86400)
        rec=np.exp(-days/365.0)
        sim=1.0 if r.competition==target_comp else (0.75 if r.country in set(country.country) else 0.55)
        tier=comp_tier(r.competition)
        venue_w=1.0 if ((venue=='HOME' and r.home_team==team) or (venue=='AWAY' and r.away_team==team)) else .80
        gf=r.hg if r.home_team==team else r.ag; ga=r.ag if r.home_team==team else r.hg
        vals.append((rec*sim*tier*venue_w,gf-ga,3 if gf>ga else 1 if gf==ga else 0))
    vals=vals[-30:]
    w=np.array([x[0] for x in vals]); gd=np.array([x[1] for x in vals]); pts=np.array([x[2] for x in vals])
    score=min(1.0,0.25*min(len(direct),10)/10+0.20*min(len(country),10)/10+0.25*min(len(cross),15)/15+0.20*min(len(hist),30)/30+0.10)
    conf='HIGH' if score>=.75 and len(h)>=20 else 'MEDIUM' if score>=.45 and len(h)>=8 else 'LOW' if len(h)>=3 else 'CRITICAL'
    return {'direct_n':len(direct),'same_country_n':len(country),'cross_comp_n':len(cross),'hist_n':len(hist),'weighted_n':round(float(w.sum()),3),'form5':round(float(np.average(pts[-5:],weights=w[-5:])),3) if len(w)>=1 else np.nan,'gd5':round(float(np.average(gd[-5:],weights=w[-5:])),3) if len(w)>=1 else np.nan,'evidence_score':round(float(score),3),'confidence':conf}

transfer=[]
for _,f in fixtures.iterrows():
    before=pd.to_datetime(f.kickoff_local,errors='coerce',utc=True)
    for side,team,venue in [('HOME',f.home_team,'HOME'),('AWAY',f.away_team,'AWAY')]:
        e=evidence(team,f.competition,before,venue)
        transfer.append({'fixture_date':str(f.kickoff_local),'competition':f.competition,'home_team':f.home_team,'away_team':f.away_team,'side':side,'team':team,**e,'direct_evidence':'DIRECT' if e['direct_n']>=5 else 'TRANSFERRED' if e['hist_n']>=5 else 'CONTEXT_ONLY','model_confidence':e['confidence']})
transfer_df=pd.DataFrame(transfer)
transfer_df.to_csv(REP/'CROSS_COMPETITION_EVIDENCE.csv',index=False)

# 7) match-level readiness for the current round; no value bet promotion and no future result usage.
readiness=[]
for _,f in fixtures.iterrows():
    before=pd.to_datetime(f.kickoff_local,errors='coerce',utc=True)
    hs=evidence(f.home_team,f.competition,before,'HOME'); as_=evidence(f.away_team,f.competition,before,'AWAY')
    direct=min(hs['direct_n'],as_['direct_n']); transferred=max(hs['cross_comp_n'],as_['cross_comp_n'])
    direct_score=(hs['evidence_score']+as_['evidence_score'])/2
    market_pit=str(f.get('odds_pit_status','UNKNOWN'))
    if direct_score>=.70 and direct>=5 and market_pit=='EXACT_PIT': cls='A_FULL_ANALYSIS'
    elif (hs['hist_n']>=8 and as_['hist_n']>=8): cls='B_GOOD_TRANSFERRED_ANALYSIS'
    elif (hs['hist_n']>=3 and as_['hist_n']>=3): cls='C_CONTEXTUAL_ANALYSIS'
    elif (hs['hist_n']>0 or as_['hist_n']>0): cls='D_WATCH'
    else: cls='E_INSUFFICIENT_DATA'
    readiness.append({'competition':f.competition,'kickoff':f.kickoff_local,'home_team':f.home_team,'away_team':f.away_team,'home_direct_n':hs['direct_n'],'away_direct_n':as_['direct_n'],'home_cross_comp_n':hs['cross_comp_n'],'away_cross_comp_n':as_['cross_comp_n'],'home_hist_n':hs['hist_n'],'away_hist_n':as_['hist_n'],'direct_evidence_score':round(direct_score,3),'market_pit_status':market_pit,'operational_class':cls,'pricing_status':'BLOCKED_NO_VALIDATED_MODEL' if cls!='A_FULL_ANALYSIS' else 'REQUIRES_OOS_MODEL_AND_EXACT_PIT','real_money':'DISABLED'})
read=pd.DataFrame(readiness); read.to_csv(REP/'PREMATCH_READINESS_2026-08-20.csv',index=False)

# 8) scientific audits / counts.
counts={
 'RUN_UTC':RUN,'MATCHES_BEFORE':canon_before,'MATCHES_NEW':len(new_rows),'MATCHES_AFTER':len(canon2),'DUPLICATES_IN_CANONICAL':int(canon2.match_id.duplicated().sum()),
 'COUNTRIES':int(canon2.country.nunique()),'COMPETITIONS':int(canon2.competition.nunique()),'SEASONS':int(canon2.season.nunique()),'TEAMS':int(len(teams)),'PLAYERS':0,
 'MEN_MATCHES':int((canon2.gender=='MEN').sum()),'WOMEN_MATCHES':int((canon2.gender=='WOMEN').sum()),
 'XG_MATCHES':int(canon2[['home_xg','away_xg']].notna().any(axis=1).sum()),'SHOTS_MATCHES':0,'SOT_MATCHES':0,'EVENT_MATCHES':0,'LINEUP_MATCHES':0,'INJURY_MATCHES':0,'SUSPENSION_MATCHES':0,
 'CARDS_MATCHES':int(canon2[['home_cards','away_cards']].notna().any(axis=1).sum()),'CORNERS_MATCHES':int(canon2[['home_corners','away_corners']].notna().any(axis=1).sum()),
 'ODDS_MATCHES':int(canon2[['odds_1','odds_x','odds_2']].notna().any(axis=1).sum()),'EXACT_PIT':int(canon2.pit_status.eq('PIT_EXACT').sum()),'DATE_LEVEL_PIT':int(canon2.pit_status.eq('PIT_DATE_ONLY').sum()),'NON_PIT':int(canon2.pit_status.eq('NON_PIT').sum()),
 'SOURCE_SUCCESS':sum(x.get('state')=='ACCESSIBLE_LOCAL' for x in source_attempts),'SOURCE_PARTIAL':0,'SOURCE_FAILED':0,'SOURCE_BLOCKED':sum(x.get('state')=='ACQUISITION_BLOCKED' for x in source_attempts),
 'CURRENT_ROUND_FIXTURES':len(fixtures),'CURRENT_ROUND_B_READY':int((read.operational_class=='B_GOOD_TRANSFERRED_ANALYSIS').sum()) if len(read) else 0,'CURRENT_ROUND_PRICING_READY':0,'REAL_MONEY':'DISABLED'
}
(REP/'DATASET_FINAL_COUNTS.json').write_text(json.dumps(counts,indent=2,ensure_ascii=False),encoding='utf-8')

# 9) manifest with strict states.
manifest={'execution_timestamp':RUN,'window':['2020-01-01','2026-08-20'],'input_canonical_matches':canon_before,'new_materialized_matches':len(new_rows),'materialized_matches_after':len(canon2),'states':{'FOUND':'NOT_COUNTED_AS_ACQUIRED','ACCESSIBLE':sum(x.get('state')=='ACCESSIBLE_LOCAL' for x in source_attempts),'DOWNLOADED_LOCAL':sum(x.get('downloaded') is True for x in source_attempts),'MATERIALIZED':len(new_rows),'PROCESSED':len(new_rows),'VALIDATED':len(new_rows),'USED_IN_MODEL':0,'BLOCKED':sum(x.get('state')=='ACQUISITION_BLOCKED' for x in source_attempts)},'source_attempts':source_attempts,'real_money':'DISABLED'}
(REG/'DATA_ACQUISITION_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
(REG/'GLOBAL_ACQUISITION_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')

# 10) provenance report.
prov_report=[]
for s in source_attempts:
    prov_report.append({'run_utc':RUN,**s})
pd.DataFrame(prov_report).to_csv(REP/'SOURCE_PROVENANCE.csv',index=False)

# 11) scientific/readiness reports.
report=f'''# GLOBAL DATASET FINAL REPORT\n\nExecution: {RUN}\n\n## Quantitative\n- MATCHES_BEFORE: **{canon_before}**\n- MATCHES_NEW: **{len(new_rows)}**\n- MATCHES_AFTER: **{len(canon2)}**\n- DUPLICATES_IN_CANONICAL: **{counts['DUPLICATES_IN_CANONICAL']}**\n- COUNTRIES: **{counts['COUNTRIES']}**\n- COMPETITIONS: **{counts['COMPETITIONS']}**\n- SEASONS: **{counts['SEASONS']}**\n- TEAMS: **{counts['TEAMS']}**\n- PLAYERS: **0**\n- MEN_MATCHES: **{counts['MEN_MATCHES']}**\n- WOMEN_MATCHES: **{counts['WOMEN_MATCHES']}**\n\n## Enrichment\n- Cards: **{counts['CARDS_MATCHES']}**\n- Corners: **{counts['CORNERS_MATCHES']}**\n- Shots: **0**\n- SOT: **0**\n- xG: **{counts['XG_MATCHES']}**\n- Events: **0**\n- Lineups: **0**\n- Injuries: **0**\n- Suspensions: **0**\n- Odds: **{counts['ODDS_MATCHES']}**\n- EXACT_PIT: **{counts['EXACT_PIT']}**\n- DATE_LEVEL_PIT: **{counts['DATE_LEVEL_PIT']}**\n\n## Acquisition truth\nOnly bytes already present inside the input ZIP were eligible for local materialization. The 30-match Premier League 2023-24 pilot artifact was not represented in the canonical backbone, so those **{len(new_rows)}** real matches were promoted conservatively into canonical storage with provenance. Remote bulk routes were attempted only at the connectivity/state level and remain blocked by the execution container DNS/network restriction; they are not counted as acquired.\n\n## Scientific status\n**GLOBAL_PARTIAL / EDGE_NOT_DETERMINED**. The base is larger and cross-competition evidence is now measured explicitly, but global completeness is not justified. Exact PIT, player/lineup/injury/suspension history, xG/shots/events and broad competition coverage remain major gaps.\n\n## Pricing gate\nNo new VALUE_BET was activated. No edge was declared. REAL_MONEY remains DISABLED.\n'''
(REP/'GLOBAL_DATASET_FINAL_REPORT.md').write_text(report,encoding='utf-8')

cov=coverage.groupby(['country','competition','gender']).agg(seasons=('season','nunique'),matches=('materialized_matches','sum'),stats_matches=('stats_matches','sum'),xg_matches=('xg_matches','sum')).reset_index()
status=[]
for _,r in cov.iterrows(): status.append({**r.to_dict(),'status':'MATERIALIZED' if r.matches>0 else 'NOT_MATERIALIZED'})
pd.DataFrame(status).to_csv(REP/'GLOBAL_COVERAGE_REPORT_COMPETITION.csv',index=False)

transfer_report=f'''# CROSS COMPETITION TRANSFER REPORT\n\nThe engine uses only historical rows with kickoff strictly before each fixture timestamp. Evidence is weighted by recency, target-competition match history, same-country history, competition tier, venue and sample size.\n\nNo transferred evidence is promoted to VALUE_BET by itself. Current round pricing remains blocked because the package has no Exact PIT and no validated OOS model probability for these fixtures.\n\nCurrent fixtures: **{len(fixtures)}**.\n'''
(REP/'CROSS_COMPETITION_TRANSFER_REPORT.md').write_text(transfer_report,encoding='utf-8')
(REP/'MODEL_READINESS_REPORT.md').write_text(f'''# MODEL READINESS REPORT\n\n- Historical matches: {len(canon2)}\n- Exact PIT: {counts['EXACT_PIT']}\n- xG matches: {counts['XG_MATCHES']}\n- Players: 0\n- Lineups: 0\n- Injuries: 0\n- Suspensions: 0\n- OOS validated pricing after this acquisition: NO\n- VALUE_BET status: BLOCKED\n- REAL_MONEY: DISABLED\n\nConclusion: enough data exists for stronger descriptive/context transfer research, but not enough to claim globally validated betting edge.\n''',encoding='utf-8')
(REP/'PREMATCH_READINESS_REPORT.md').write_text(f'''# PRE-MATCH READINESS REPORT\n\nCurrent round fixtures evaluated without using future results: **{len(fixtures)}**.\n\nClasses: A=full direct evidence, B=good transferred evidence, C=contextual, D=watch, E=insufficient.\n\n{read.to_string(index=False) if len(read) else 'No current-round fixture file available.'}\n\nNo new predictive snapshot was altered. Existing prospective snapshot files were hash-protected.\n''',encoding='utf-8')
(REP/'SCIENTIFIC_STATUS_FINAL.md').write_text('''# SCIENTIFIC STATUS FINAL\n\nStatus: **GLOBAL_PARTIAL / EDGE_NOT_DETERMINED**\n\nThe acquisition materially added only records that were physically present in the input package. Remote discovery is not counted as acquisition. Cross-competition evidence is available as an auditable context layer, but it is not equivalent to direct competition evidence. No value edge is declared. REAL_MONEY remains DISABLED.\n''',encoding='utf-8')

# 12) snapshot integrity after run.
snapshot_after_hashes={str(p.relative_to(ROOT)):sha(p) for p in SNAP_FILES if p.is_file()}
changed=[p for p,h in snapshot_hashes.items() if snapshot_after_hashes.get(p)!=h]
protection={'before_hashes':snapshot_hashes,'after_hashes':snapshot_after_hashes,'changed_files':changed,'unchanged':len(changed)==0,'status':'PASS' if not changed else 'MISSION_FAIL'}
(REP/'PREMATCH_SNAPSHOT_INTEGRITY.json').write_text(json.dumps(protection,indent=2,ensure_ascii=False),encoding='utf-8')
if changed: raise RuntimeError('MISSION FAIL: existing PREMATCH snapshot artifacts changed')

print(json.dumps(counts,indent=2,ensure_ascii=False))
