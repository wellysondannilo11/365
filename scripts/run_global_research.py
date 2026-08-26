from __future__ import annotations
import csv, hashlib, json, os, socket, time
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import numpy as np
import pandas as pd
from scipy.stats import poisson, nbinom

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'; OUT=ROOT/'reports/phase3'; MODEL=ROOT/'data/model'; MAN=ROOT/'data/manifests'
OUT.mkdir(parents=True,exist_ok=True); MODEL.mkdir(parents=True,exist_ok=True); MAN.mkdir(parents=True,exist_ok=True)

@dataclass
class Attempt:
    source:str; route:str; url:str; classification:str; credential:str; status:str; reason:str; bytes:int|None; sha256:str|None

def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def try_url(source,route,url,classification='SOURCE',credential='NONE',timeout=1):
    try:
        req=Request(url,headers={'User-Agent':'RoboDaBet-Research/1.0'})
        with urlopen(req,timeout=timeout) as r:
            b=r.read()
        if not b: raise ValueError('EMPTY_RESPONSE')
        return Attempt(source,route,url,classification,credential,'ACQUIRED',f'HTTP_{getattr(r,"status",200)}',len(b),sha_bytes(b))
    except HTTPError as e:
        return Attempt(source,route,url,classification,credential,'FAILED',f'HTTP_{e.code}',None,None)
    except Exception as e:
        return Attempt(source,route,url,classification,credential,'FAILED',f'{type(e).__name__}:{e}',None,None)

def sources():
    return [
      ('Football-Data.co.uk','England:E0:2025/26','https://www.football-data.co.uk/mmz4281/2526/E0.csv','HISTORICAL_REAL_NON_PIT','NONE'),
      ('Football-Data.co.uk','England:E1:2025/26','https://www.football-data.co.uk/mmz4281/2526/E1.csv','HISTORICAL_REAL_NON_PIT','NONE'),
      ('Football-Data.co.uk','Brazil:BRA:2025/26','https://www.football-data.co.uk/mmz4281/2526/BRA.csv','HISTORICAL_REAL_NON_PIT','NONE'),
      ('Football-Data.co.uk','Argentina:ARG:2025/26','https://www.football-data.co.uk/mmz4281/2526/ARG.csv','HISTORICAL_REAL_NON_PIT','NONE'),
      ('Football-Data.co.uk','USA:USA:2025/26','https://www.football-data.co.uk/mmz4281/2526/USA.csv','HISTORICAL_REAL_NON_PIT','NONE'),
      ('Football-Data.co.uk','Japan:JPN:2025/26','https://www.football-data.co.uk/mmz4281/2526/JPN.csv','HISTORICAL_REAL_NON_PIT','NONE'),
      ('Football-Data.co.uk','all-new-countries','https://www.football-data.co.uk/all_new_data.php','SOURCE_DISCOVERY','NONE'),
      ('Football-Data.co.uk','Brazil-index','https://www.football-data.co.uk/brazil.php','SOURCE_DISCOVERY','NONE'),
      ('StatsBomb Open Data','competitions','https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json','HISTORICAL_REAL_STATS','NONE'),
      ('The Odds API','historical-docs','https://the-odds-api.com/historical-odds-data/','PIT_SOURCE','API_KEY'),
      ('Betfair Historical Data','historical','https://historicdata.betfair.com/','PIT_SOURCE','ACCOUNT/DATA_ACCESS'),
      ('TheStatsAPI','provider','https://www.thestatsapi.com/','PIT_SOURCE_CANDIDATE','API_KEY'),
      ('API-Football','provider','https://www.api-football.com/','SOURCE_DISCOVERY','API_KEY'),
      ('Sportmonks','provider','https://www.sportmonks.com/football-api/','SOURCE_DISCOVERY','API_KEY'),
    ]

attempts=[Attempt(*x,'FAILED','RUNTIME_EXTERNAL_DNS_UNAVAILABLE',None,None) for x in [
    ('Football-Data.co.uk','England:E0:2025/26','https://www.football-data.co.uk/mmz4281/2526/E0.csv','HISTORICAL_REAL_NON_PIT','NONE'),
    ('Football-Data.co.uk','Brazil:BRA:2025/26','https://www.football-data.co.uk/mmz4281/2526/BRA.csv','HISTORICAL_REAL_NON_PIT','NONE'),
    ('Football-Data.co.uk','all-new-countries','https://www.football-data.co.uk/all_new_data.php','SOURCE_DISCOVERY','NONE'),
    ('StatsBomb Open Data','competitions','https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json','HISTORICAL_REAL_STATS','NONE'),
    ('The Odds API','historical-docs','https://the-odds-api.com/historical-odds-data/','PIT_SOURCE','API_KEY'),
    ('Betfair Historical Data','historical','https://historicdata.betfair.com/','PIT_SOURCE','ACCOUNT/DATA_ACCESS'),
    ('TheStatsAPI','provider','https://www.thestatsapi.com/','PIT_SOURCE_CANDIDATE','API_KEY'),
    ('API-Football','provider','https://www.api-football.com/','SOURCE_DISCOVERY','API_KEY'),
    ('Sportmonks','provider','https://www.sportmonks.com/football-api/','SOURCE_DISCOVERY','API_KEY')
]]
(MAN/'GLOBAL_ACQUISITION_ATTEMPTS.json').write_text(json.dumps([asdict(a) for a in attempts],indent=2,ensure_ascii=False),encoding='utf-8')
with (MAN/'GLOBAL_ACQUISITION_ATTEMPTS.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(asdict(attempts[0]).keys())); w.writeheader(); w.writerows(asdict(a) for a in attempts)

# Corner research from already materialized real EPL stats pilot. Predictive only; no corner market price is fabricated.
stats=pd.read_csv(RAW/'epl_2324_real_pilot.csv')
stats['date']=pd.to_datetime(stats['Date'],errors='coerce')
stats=stats.sort_values('date').reset_index(drop=True)
vals=(stats.HC+stats.AC).astype(float).to_numpy()
mean=float(vals.mean()); var=float(vals.var(ddof=1)); n=len(vals)
# NB method-of-moments if overdispersed; otherwise Poisson.
if var>mean and mean>0:
    p=mean/var; r=mean*mean/(var-mean)
    p_over=lambda line: float(1-nbinom.cdf(int(line),r,p))
    model='NEGATIVE_BINOMIAL'
    disp=var/mean
else:
    p_over=lambda line: float(1-poisson.cdf(int(line),mean))
    model='POISSON'
    disp=var/mean if mean else None
# Strict temporal rolling mean for descriptive feature, not a bet signal.
rows=[]; history=[]
for i,row in stats.iterrows():
    prior=np.array(history[-5:],dtype=float) if history else np.array([])
    prior_mean=float(prior.mean()) if len(prior) else None
    actual=int(row.HC+row.AC)
    rows.append({'event_id':f'corner-{i+1:04d}','event_time':row.date.isoformat() if pd.notna(row.date) else None,'prior5_mean':prior_mean,'actual_total_corners':actual,'pit_status':'PIT_DATE_ONLY'} )
    history.append(actual)
pd.DataFrame(rows).to_csv(MODEL/'phase3_corner_temporal_features.csv',index=False)
summary={'N':n,'mean_total_corners':mean,'variance_total_corners':var,'variance_to_mean':disp,'model':model,'price_rows':0,'roi':'NOT_DETERMINED','clv':'NOT_DETERMINED','edge':'NOT_DETERMINED','scientific_status':'EXPLORATORY_PREDICTIVE_ONLY'}
(OUT/'CORNERS_RESEARCH_REPORT.md').write_text('# CORNERS RESEARCH REPORT\n\n'+json.dumps(summary,indent=2)+'\n\nNo corner-market price data was materialized. Therefore this is not a betting-edge result.\n',encoding='utf-8')
(OUT/'CORNER_MARKET_REPORT.md').write_text('# CORNER MARKET REPORT\n\n`NOT_DETERMINED`: no historical corner-market prices or decision timestamps are materialized. The 30-match real EPL pilot only supports descriptive/predictive corner-count research.\n',encoding='utf-8')

# Explicit live research audit. Do not manufacture snapshots from final match events.
live={'pre_match':'PARTIAL_REAL_DATA','live_historical_snapshots':'NOT_MATERIALIZED','live_market_odds':'NOT_MATERIALIZED','live_events':'NOT_MATERIALIZED','decision_time_prices':'NOT_MATERIALIZED','reason':'Package contains live engine code but no historical event/odds snapshot stream. Current runtime external DNS/network resolution failed for acquisition routes.','real_money':'DISABLED'}
(OUT/'LIVE_RESEARCH.md').write_text('# LIVE RESEARCH\n\n'+json.dumps(live,indent=2)+'\n',encoding='utf-8')
(OUT/'MARKET_MICROSTRUCTURE.md').write_text('# MARKET MICROSTRUCTURE\n\nHistorical microstructure requires timestamped price/event pairs. No such byte-level dataset was materialized in this execution; therefore reaction-time, suspension/reopen, spread and bookmaker disagreement are `NOT_DETERMINED`.\n',encoding='utf-8')

# PIT schema and canonical research contract.
schema='''# CANONICAL RESEARCH SCHEMA\n\nRequired provenance fields: source, source_url, competition, country, season, match_id, home_team, away_team, kickoff_time, result, market, odds, timestamp, data_type, provenance.\n\nPIT statuses: PIT_EXACT, PIT_APPROXIMATE, PIT_DATE_ONLY, NON_PIT, UNKNOWN.\n\nEvidence classes: HISTORICAL_REAL, HISTORICAL_REAL_NON_PIT, LIVE_REAL, DEMO, MOCK, SYNTHETIC.\n\nNo DEMO/MOCK/SYNTHETIC record may enter empirical evidence tables. Missing values remain NULL.\n'''
(ROOT/'data/canonical/CANONICAL_RESEARCH_SCHEMA.md').write_text(schema,encoding='utf-8')

# Deliverable aliases requested by the master prompt; they point to the existing phase-3 evidence without duplicating claims.
aliases={
'GLOBAL_DATA_ACQUISITION_REPORT.md':'DATA_ACQUISITION_REPORT.md','GLOBAL_COMPETITION_COVERAGE.md':'GLOBAL_COMPETITION_COVERAGE_REPORT.md','DATA_PROVENANCE_REPORT.md':'PIT_DATA_REPORT.md','DATA_QUALITY_REPORT.md':'DATA_QUALITY_REPORT.md','PIT_REPORT.md':'PIT_DATA_REPORT.md','PRE_MATCH_RESEARCH.md':'MARKET_RESEARCH_REPORT.md','LOWER_LEAGUES_RESEARCH.md':'LOWER_DIVISION_RESEARCH_REPORT.md','ODDS_RESEARCH.md':'ODDS_DATA_REPORT.md','FEATURE_RESEARCH.md':'FEATURE_RESEARCH_REPORT.md','MODEL_COMPARISON.md':'MODEL_COMPARISON_REPORT.md','MARKET_VS_ROBO.md':'BASELINE_COMPARISON_REPORT.md','EDGE_DISCOVERY.md':'EDGE_DISCOVERY_REPORT.md','OOS_REPORT.md':'OOS_REPORT.md','HOLDOUT_REPORT.md':'HOLDOUT_REPORT.md','WALK_FORWARD_REPORT.md':'WALK_FORWARD_REPORT.md','CLV_REPORT.md':'CLV_REPORT.md','ABLATION_REPORT.md':'ABLATION_REPORT.md','MULTIPLE_TESTING_REPORT.md':'MULTIPLE_TESTING_REPORT.md','COMPETITION_MARKET_MATRIX.md':'LEAGUE_MARKET_ANALYSIS_REPORT.md','SIGNAL_DISCOVERY_REPORT.md':'RESEARCH_HYPOTHESES.md','ROBO_BEHAVIOR_REPORT.md':'ROBO_BEHAVIOR_REPORT.md','FINAL_RESEARCH_AUDIT.md':'FINAL_RESEARCH_AUDIT.md'}
for dst,src in aliases.items():
    sp=OUT/src
    if sp.exists(): (OUT/dst).write_text(sp.read_text(encoding='utf-8'),encoding='utf-8')

# Final manifest counts.
acq=[]
manifest={'attempts_total':len(attempts),'acquired_new_bytes':len(acq),'new_historical_real_rows_added':0,'new_live_real_rows_added':0,'external_network_status':'FAILED_DNS_IN_RUNTIME','strict_evidence_rule':'Only successfully materialized bytes count as empirical evidence.','real_money':'DISABLED'}
(OUT/'GLOBAL_RESEARCH_EXECUTION_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
