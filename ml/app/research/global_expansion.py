from __future__ import annotations
import csv, hashlib, json, os, socket, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

EVIDENCE_CLASSES = {
    'HISTORICAL_REAL','HISTORICAL_REAL_NON_PIT','LIVE_REAL','LIVE_REAL_UNVERIFIED',
    'DEMO','MOCK','SYNTHETIC','UNKNOWN'
}
EMPIRICAL_CLASSES = {'HISTORICAL_REAL','HISTORICAL_REAL_NON_PIT','LIVE_REAL'}
PIT_STATUSES = {'EXACT_PIT','VALID_PIT','DATE_LEVEL_PIT','NON_PIT','UNKNOWN','PIT_INVALID'}
ACQ_STATES = {'FOUND','ACQUIRED','DOWNLOADED','MATERIALIZED','PROCESSED','PIT_VALIDATED','USED_IN_MODEL','BLOCKED','FAILED','FOUND_ONLY'}

# Public Football-Data country/league codes. This registry is intentionally a plan/route registry;
# rows only become evidence after bytes are actually materialized and hashed.
FOOTBALL_DATA_CODES = {
    'England':['E0','E1','E2','E3','EC'], 'Scotland':['SC0','SC1','SC2','SC3'],
    'Germany':['D1','D2','D3'], 'Italy':['I1','I2','I3'], 'Spain':['SP1','SP2','SP3'],
    'France':['F1','F2'], 'Netherlands':['N1','N2'], 'Belgium':['B1'], 'Portugal':['P1','P2'],
    'Turkey':['T1'], 'Greece':['G1'], 'Austria':['AUT'], 'Switzerland':['SWZ'],
    'Denmark':['DNK'], 'Sweden':['SWE'], 'Norway':['NOR'], 'Finland':['FIN'],
    'Poland':['POL'], 'Romania':['ROU'], 'Russia':['RUS'], 'Brazil':['BRA'],
    'Argentina':['ARG'], 'USA':['USA'], 'Mexico':['MEX'], 'Japan':['JPN'], 'China':['CHN'],
    'Ireland':['IRL'], 'South Africa':['SAF']
}

SEASON_CODES = [f'{y%100:02d}{(y+1)%100:02d}' for y in range(2019, 2027)]

@dataclass(frozen=True)
class AcquisitionRecord:
    source: str
    target: str
    url: str
    classification: str
    credential: str
    status: str
    attempted_at: str
    http_status: int | None = None
    bytes: int | None = None
    rows: int | None = None
    sha256: str | None = None
    materialized: bool = False
    processed: bool = False
    pit_validated: bool = False
    used_in_model: bool = False
    reason: str | None = None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_route_registry() -> list[dict]:
    rows = []
    for country, leagues in FOOTBALL_DATA_CODES.items():
        for season in SEASON_CODES:
            for league in leagues:
                rows.append({
                    'source':'Football-Data.co.uk', 'country':country, 'season':season,
                    'league_code':league,
                    'url':f'https://www.football-data.co.uk/mmz4281/{season}/{league}.csv',
                    'classification':'HISTORICAL_REAL_NON_PIT', 'credential':'NONE',
                    'target':'results_stats_odds'
                })
    # StatsBomb open data is a separate event/lineup route. It is selective by competition.
    rows += [
        {'source':'StatsBomb Open Data','country':'GLOBAL','season':'ALL','league_code':'competitions',
         'url':'https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json',
         'classification':'HISTORICAL_REAL','credential':'NONE','target':'competitions'},
        {'source':'The Odds API','country':'GLOBAL','season':'ALL','league_code':'historical',
         'url':'https://api.the-odds-api.com/v4/historical/sports/{sport}/odds',
         'classification':'HISTORICAL_REAL','credential':'THE_ODDS_API_KEY','target':'timestamped_odds'},
        {'source':'Betfair Historical Data','country':'GLOBAL','season':'ALL','league_code':'historical',
         'url':'https://historicdata.betfair.com/',
         'classification':'HISTORICAL_REAL','credential':'BETFAIR_ACCESS','target':'exchange_timestamped_odds'},
        {'source':'API-Football','country':'GLOBAL','season':'ALL','league_code':'fixtures',
         'url':'https://v3.football.api-sports.io/fixtures',
         'classification':'LIVE_REAL','credential':'API_FOOTBALL_KEY','target':'fixtures_events_stats'},
        {'source':'Sportmonks','country':'GLOBAL','season':'ALL','league_code':'livescores',
         'url':'https://api.sportmonks.com/v3/football/livescores',
         'classification':'LIVE_REAL','credential':'SPORTMONKS_API_TOKEN','target':'livescores_events_stats'},
    ]
    return rows


def dns_preflight(hosts: Iterable[str]) -> dict[str, str]:
    out={}
    for host in sorted(set(hosts)):
        try:
            socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
            out[host]='RESOLVED'
        except Exception as e:
            out[host]=f'FAILED:{type(e).__name__}:{e}'
    return out


def classify_pit(decision_time, odds_time, feature_time=None) -> str:
    if decision_time is None or odds_time is None:
        return 'UNKNOWN'
    try:
        d=pd.Timestamp(decision_time); o=pd.Timestamp(odds_time)
        if pd.isna(d) or pd.isna(o): return 'UNKNOWN'
        if o > d: return 'PIT_INVALID'
        delta=(d-o).total_seconds()
        return 'EXACT_PIT' if delta == 0 else 'VALID_PIT'
    except Exception:
        return 'UNKNOWN'


def canonical_match_key(date, home, away, competition='', season='') -> str:
    def norm(x):
        return ''.join(ch.lower() for ch in str(x or '').strip() if ch.isalnum())
    return '|'.join([str(pd.Timestamp(date).date()) if pd.notna(pd.Timestamp(date)) else '',norm(home),norm(away),norm(competition),norm(season)])


def entity_alias_key(name: str) -> str:
    return ''.join(ch.lower() for ch in str(name or '').strip() if ch.isalnum())


def deduplicate_matches(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df.copy()
    x=df.copy()
    x['_canonical_key']=[canonical_match_key(r.get('date') or r.get('kickoff_timestamp'),r.get('home_team'),r.get('away_team'),r.get('competition',''),r.get('season','')) for _,r in x.iterrows()]
    return x.drop_duplicates('_canonical_key',keep='first').drop(columns=['_canonical_key'])


def inventory_local_real(root: Path) -> dict:
    canonical=root/'data/canonical/football_historical_real_canonical.csv'
    if not canonical.exists(): return {'matches':0,'countries':0,'competitions':0,'seasons':0,'odds_rows':0,'pit_validated':0,'live_matches':0,'events':0,'cards':0,'corners':0,'xg':0,'lineups':0,'referees':0,'settlements':0}
    x=pd.read_csv(canonical)
    return {
        'matches':int(len(x)), 'countries':int(x['country'].nunique(dropna=True)),
        'competitions':int(x['competition'].nunique(dropna=True)), 'seasons':int(x['season'].nunique(dropna=True)),
        'odds_rows':int(x[['odds_1','odds_x','odds_2']].notna().any(axis=1).sum()),
        'odds_snapshots':int(x['odds_timestamp'].notna().sum()),
        'pit_validated':int(x['pit_status'].isin(['PIT_EXACT','PIT_VALID','EXACT_PIT','VALID_PIT']).sum()),
        'live_matches':0,'live_snapshots':0,'events':0,
        'cards':int(x[['home_cards','away_cards']].notna().any(axis=1).sum()),
        'corners':int(x[['home_corners','away_corners']].notna().any(axis=1).sum()),
        'xg':int(x[['home_xg','away_xg']].notna().any(axis=1).sum()),
        'lineups':0,'referees':int(x['referee'].notna().sum()),'settlements':0,
    }


def build_coverage(root: Path, registry: list[dict]) -> pd.DataFrame:
    local=root/'data/canonical/football_historical_real_canonical.csv'
    if local.exists():
        x=pd.read_csv(local)
        existing={(str(r.country),str(r.competition),str(r.season)) for r in x.itertuples()}
    else: existing=set()
    rows=[]
    for r in registry:
        if r['source']=='Football-Data.co.uk':
            # competition code is a route identifier, not a claim that a dataset exists locally.
            materialized=any(k[0]==r['country'] and r['league_code'].lower() in k[1].lower() and k[2]==r['season'] for k in existing)
        else: materialized=False
        rows.append({**r,'materialized':materialized,'processed':materialized,'pit_validated':False,'used_in_model':False})
    return pd.DataFrame(rows)


def _fetch_public_bytes(url: str, timeout: int = 12) -> tuple[bytes,int]:
    req=Request(url,headers={'User-Agent':'RoboDaBet/MassExpansion/1.0'})
    with urlopen(req,timeout=timeout) as r:
        data=r.read()
        return data,int(getattr(r,'status',200))


def attempt_registry(root: Path, registry: list[dict]) -> tuple[pd.DataFrame,dict]:
    now=pd.Timestamp.utcnow().isoformat()
    hosts=[urlparse(r['url'].replace('{sport}','soccer_epl')).hostname for r in registry if urlparse(r['url'].replace('{sport}','soccer_epl')).hostname]
    dns=dns_preflight(hosts)
    records=[]
    raw_dir=root/'data/raw/global_expansion'; raw_dir.mkdir(parents=True,exist_ok=True)
    global_blocked=all(v.startswith('FAILED:') for v in dns.values()) if dns else True
    for r in registry:
        host=urlparse(r['url'].replace('{sport}','soccer_epl')).hostname
        credential=r['credential']
        status='BLOCKED'; reason=None; nbytes=None; digest=None; rows=None; materialized=False; processed=False
        if credential!='NONE' and not os.getenv(credential):
            reason=f'MISSING_CREDENTIAL:{credential}'
        elif global_blocked:
            reason=f'RUNTIME_DNS_BLOCKED:{dns.get(host)}'
        elif r['source'] in {'Football-Data.co.uk','StatsBomb Open Data'}:
            try:
                data,http_status=_fetch_public_bytes(r['url'])
                if not data.strip(): raise ValueError('EMPTY_RESPONSE')
                digest=sha256_bytes(data); nbytes=len(data); materialized=True; status='MATERIALIZED'
                safe=(r['country']+'_'+r['season']+'_'+r['league_code']).replace('/','_')
                target=raw_dir/f'{safe}.bin'; target.write_bytes(data)
                try:
                    if r['url'].lower().endswith('.csv'):
                        import io
                        rows=len(pd.read_csv(io.BytesIO(data),encoding_errors='replace'))
                    elif r['url'].lower().endswith('.json'):
                        obj=json.loads(data); rows=len(obj) if isinstance(obj,list) else None
                except Exception:
                    rows=None
                processed=True if rows is not None else False
                if processed: status='PROCESSED'
            except Exception as e:
                reason=f'{type(e).__name__}:{e}'; status='FAILED'
        else:
            reason='CREDENTIAL_CONFIGURED_BUT_PROVIDER_ADAPTER_EXECUTION_IS_SEPARATE'
        records.append(AcquisitionRecord(r['source'],r.get('target',r.get('league_code','')),r['url'],r['classification'],credential,status,now,bytes=nbytes,rows=rows,sha256=digest,materialized=materialized,processed=processed,reason=reason))
    return pd.DataFrame([asdict(x) for x in records]), {'dns':dns,'global_blocked':global_blocked}


def write_outputs(root: Path, attempts: pd.DataFrame, coverage: pd.DataFrame, before: dict, web_verified_sources: list[dict]) -> dict:
    out=root/'reports/expansion'; out.mkdir(parents=True,exist_ok=True)
    man=root/'data/manifests'; man.mkdir(parents=True,exist_ok=True)
    reg=root/'data/registry'; reg.mkdir(parents=True,exist_ok=True)
    attempts.to_csv(man/'MASS_EXPANSION_ACQUISITION.csv',index=False)
    attempts.to_json(man/'MASS_EXPANSION_ACQUISITION.json',orient='records',indent=2)
    coverage.to_csv(reg/'GLOBAL_ROUTE_COVERAGE.csv',index=False)
    stats=inventory_local_real(root)
    after=stats.copy()
    summary={'before':before,'after':after,'delta':{k:after.get(k,0)-before.get(k,0) for k in set(before)|set(after)},'registry_routes':len(coverage),'attempts':len(attempts),'blocked':int((attempts.status=='BLOCKED').sum()),'acquired_bytes':int(pd.to_numeric(attempts.bytes,errors='coerce').fillna(0).sum()),'new_rows_materialized':0,'web_verified_source_discoveries':web_verified_sources,'scientific_rule':'Only bytes materialized and hashed locally count as empirical evidence.','real_money':'DISABLED'}
    (out/'EXPANSION_EXECUTION.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    (out/'DATA_ACQUISITION_REPORT.md').write_text('# MASSIVE DATA EXPANSION REPORT\n\n'+json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'BLOCKED_SOURCES.md').write_text('# BLOCKED SOURCES\n\n'+attempts[attempts.status=='BLOCKED'].to_markdown(index=False)+'\n',encoding='utf-8')
    (out/'MATERIALIZED_SOURCES.md').write_text('# MATERIALIZED SOURCES\n\n'+attempts[attempts.materialized==True].to_markdown(index=False)+'\n',encoding='utf-8')
    (out/'BEFORE_VS_AFTER.md').write_text('# BEFORE VS AFTER\n\n| Metric | Before | After | Delta |\n|---|---:|---:|---:|\n'+'\n'.join(f'| {k} | {before.get(k,0)} | {after.get(k,0)} | {after.get(k,0)-before.get(k,0)} |' for k in sorted(set(before)|set(after)))+'\n',encoding='utf-8')
    schema={
      'match':['canonical_match_id','country','competition','season','round','stage','kickoff_timestamp','home_team','away_team'],
      'odds':['canonical_match_id','market','selection','line','bookmaker','odd','odds_timestamp','decision_timestamp','pit_status','source','source_hash'],
      'live':['canonical_match_id','snapshot_timestamp','match_minute','period','home_score','away_score','home_xg','away_xg','home_shots','away_shots','home_sot','away_sot','home_corners','away_corners','home_cards','away_cards','home_pressure','away_pressure'],
      'provenance':['source','source_url','source_type','retrieval_timestamp','original_timestamp','provider','dataset_version','hash','evidence_class','pit_status'],
      'settlement':['canonical_match_id','market','selection','line','settlement','settlement_timestamp','source']
    }
    (root/'data/schemas/EXPANSION_SCHEMAS.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
    return summary
