import csv, json, re, hashlib, shutil
from pathlib import Path
from datetime import datetime
import pandas as pd

ROOT=Path('/mnt/data/robo_work')
RAW=ROOT/'data/raw'; CAN=ROOT/'data/canonical'; PROC=ROOT/'data/processed'; MAN=ROOT/'data/manifests'; REPORT=ROOT/'reports'
PROC.mkdir(parents=True,exist_ok=True); MAN.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)

CANON=CAN/'football_historical_real_canonical.csv'
cols=['match_id','country','competition','division','season','round','kickoff_timestamp','home_team','away_team','home_goals','away_goals','referee','home_cards','away_cards','total_cards','home_corners','away_corners','total_corners','home_xg','away_xg','odds_1','odds_x','odds_2','over_2_5','under_2_5','btts_yes','btts_no','asian_handicap','bookmaker','odds_timestamp','feature_timestamp','decision_timestamp','source','source_url','provenance_file','pit_status','data_type']

existing=pd.read_csv(CANON) if CANON.exists() else pd.DataFrame(columns=cols)
existing['match_key']=existing.apply(lambda r:f"{r.get('season','')}|{r.get('country','')}|{r.get('competition','')}|{r.get('home_team','')}|{r.get('away_team','')}|{str(r.get('kickoff_timestamp',''))[:10]}",axis=1)
existing_keys=set(existing['match_key'].astype(str))
rows=[]; odds=[]; manifests=[]; row_keys=set()

def num(v):
    try:
        if pd.isna(v) or v=='': return None
        return float(v)
    except: return None

def normteam(s):
    return re.sub(r'[^a-z0-9]+',' ',str(s).lower()).strip()

def add_row(country,comp,div,season,round_,dt,home,away,hg,ag,ref,stats,source,url,prov,oddsvals=None):
    key=f'{season}|{country}|{comp}|{home}|{away}|{dt[:10]}'
    if key in existing_keys or key in row_keys: return False
    r={c:'' for c in cols}; r['match_id']=hashlib.sha256(key.encode()).hexdigest()[:20]; r.update({'country':country,'competition':comp,'division':div,'season':season,'round':round_,'kickoff_timestamp':dt,'home_team':home,'away_team':away,'home_goals':hg,'away_goals':ag,'referee':ref or '', 'source':source,'source_url':url,'provenance_file':prov,'pit_status':'NON_PIT','data_type':'HISTORICAL_REAL_NON_PIT'})
    r.update(stats or {})
    if oddsvals:
        for k,v in oddsvals.items(): r[k]=v
    r['match_key']=key; rows.append(r); row_keys.add(key); return True

# Football-Data CSVs: real results/stats/odds, but no provider-native timestamp in row => NON_PIT.
fd_specs=[('E0','England','Premier League','1','2024-25'),('E1','England','Championship','2','2024-25'),('E2','England','League One','3','2024-25'),('E3','England','League Two','4','2024-25')]
for code,country,comp,div,season in fd_specs:
    p=RAW/f'football_data_{code.lower()}_2425.csv'
    if not p.exists(): continue
    df=pd.read_csv(p,encoding='latin1')
    for _,x in df.iterrows():
        if pd.isna(x.get('FTHG')) or pd.isna(x.get('FTAG')): continue
        date=pd.to_datetime(str(x['Date']),dayfirst=True,errors='coerce')
        if pd.isna(date): continue
        t=str(x.get('Time','')).strip()
        dt=f"{date.strftime('%Y-%m-%d')}T{t}:00" if re.match(r'^\d\d:\d\d$',t) else date.strftime('%Y-%m-%dT00:00:00')
        stats={'home_cards':num(x.get('HY')),'away_cards':num(x.get('AY')),'total_cards':sum(v for v in [num(x.get('HY')),num(x.get('AY'))] if v is not None) if (num(x.get('HY')) is not None or num(x.get('AY')) is not None) else None,'home_corners':num(x.get('HC')),'away_corners':num(x.get('AC')),'total_corners':sum(v for v in [num(x.get('HC')),num(x.get('AC'))] if v is not None) if (num(x.get('HC')) is not None or num(x.get('AC')) is not None) else None}
        # Preserve a primary bookmaker price and closing price in the odds table; canonical keeps opening-like Bet365.
        ov={'odds_1':num(x.get('B365H')),'odds_x':num(x.get('B365D')),'odds_2':num(x.get('B365A')),'over_2_5':num(x.get('B365>2.5')),'under_2_5':num(x.get('B365<2.5')),'asian_handicap':num(x.get('AHh')),'bookmaker':'Bet365'}
        added=add_row(country,comp,div,season,'',dt,str(x['HomeTeam']),str(x['AwayTeam']),num(x['FTHG']),num(x['FTAG']),str(x.get('Referee','')),stats,'Football-Data.co.uk',f'https://www.football-data.co.uk/mmz4281/2425/{code}.csv',str(p.relative_to(ROOT)),ov)
        if added:
            mid=rows[-1]['match_id']
            for kind,prefix in [('OPENING','B365'),('CLOSING','B365C')]:
                h=num(x.get(prefix+'H')); d=num(x.get(prefix+'D')); a=num(x.get(prefix+'A'))
                if h is not None or d is not None or a is not None:
                    odds.append({'match_id':mid,'country':country,'competition':comp,'season':season,'market':'1X2','selection_home':h,'selection_draw':d,'selection_away':a,'bookmaker':'Bet365','snapshot_type':kind,'odds_timestamp':'','pit_status':'NON_PIT','evidence_class':'HISTORICAL_REAL_NON_PIT','source':'Football-Data.co.uk','source_url':f'https://www.football-data.co.uk/mmz4281/2425/{code}.csv'})
            for kind,prefix in [('OPENING','B365'),('CLOSING','B365C')]:
                o=num(x.get(prefix+'>2.5')); u=num(x.get(prefix+'<2.5'))
                if o is not None or u is not None:
                    odds.append({'match_id':mid,'country':country,'competition':comp,'season':season,'market':'O/U 2.5','over':o,'under':u,'bookmaker':'Bet365','snapshot_type':kind,'odds_timestamp':'','pit_status':'NON_PIT','evidence_class':'HISTORICAL_REAL_NON_PIT','source':'Football-Data.co.uk','source_url':f'https://www.football-data.co.uk/mmz4281/2425/{code}.csv'})
            for kind,prefix in [('OPENING','Avg'),('CLOSING','AvgC')]:
                h=num(x.get(prefix+'H')); d=num(x.get(prefix+'D')); a=num(x.get(prefix+'A'))
                if h is not None or d is not None or a is not None:
                    odds.append({'match_id':mid,'country':country,'competition':comp,'season':season,'market':'1X2','selection_home':h,'selection_draw':d,'selection_away':a,'bookmaker':'Average','snapshot_type':kind,'odds_timestamp':'','pit_status':'NON_PIT','evidence_class':'HISTORICAL_REAL_NON_PIT','source':'Football-Data.co.uk','source_url':f'https://www.football-data.co.uk/mmz4281/2425/{code}.csv'})

# GitHub mirror EPL 2025/26: real stats, no odds/timestamps.
p=RAW/'epl_2526_github_real.csv'
if p.exists():
    df=pd.read_csv(p)
    for _,x in df.iterrows():
        add_row('England','Premier League','1','2025-26', '', pd.to_datetime(x['Date']).strftime('%Y-%m-%dT00:00:00'), str(x['HomeTeam']),str(x['AwayTeam']),num(x['FTHG']),num(x['FTAG']),str(x.get('Referee','')),
                {'home_cards':num(x.get('HY')),'away_cards':num(x.get('AY')),'total_cards':(num(x.get('HY')) or 0)+(num(x.get('AY')) or 0),'home_corners':num(x.get('HC')),'away_corners':num(x.get('AC')),'total_corners':(num(x.get('HC')) or 0)+(num(x.get('AC')) or 0)},
                'GitHub/datasets/football-datasets','https://raw.githubusercontent.com/datasets/football-datasets/main/datasets/premier-league/season-2526.csv',str(p.relative_to(ROOT)))

# OpenFootball text sources: real match results; no odds/stats, timestamps preserved when present but source has no timezone. NON_PIT.
text_specs=[('England','Championship','2','2025-26',RAW/'openfootball_england_championship_2526.txt','https://raw.githubusercontent.com/openfootball/england/master/2025-26/2-championship.txt'),('Germany','Bundesliga','1','2025-26',RAW/'openfootball_germany_bundesliga_2526.txt','https://raw.githubusercontent.com/openfootball/deutschland/master/2025-26/1-bundesliga.txt'),('Italy','Serie A','1','2025-26',RAW/'openfootball_italy_seriea_2526.txt','https://raw.githubusercontent.com/openfootball/italy/master/2025-26/1-seriea.txt')]
pat_v=re.compile(r'^\s*(?:(\d{1,2}:\d{2})\s+)?(.+?)\s+v\s+(.+?)\s+(\d+)\s*-\s*(\d+)(?:\s*\((\d+)\s*-\s*(\d+)\))?\s*$')
pat_score=re.compile(r'^\s*(?:(\d{1,2}:\d{2})\s+)?(.+?)\s+(\d+)\s*-\s*(\d+)\s*(?:\((\d+)\s*-\s*(\d+)\))?\s+(.+?)\s*$')
for country,comp,div,season,p,url in text_specs:
    if not p.exists(): continue
    current_date=''; current_round=''
    for line in p.read_text(encoding='utf-8',errors='replace').splitlines():
        s=line.rstrip()
        # Date headers may include year only on the first date in a block.
        mdate=re.search(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([A-Z][a-z]{2})\s+(\d{1,2})(?:\s+(\d{4}))?',s)
        if mdate:
            year=mdate.group(3) or (current_date[:4] if current_date else season[:4])
            current_date=datetime.strptime(f"{mdate.group(1)} {mdate.group(2)} {year}",'%b %d %Y').strftime('%Y-%m-%d')
        mr=re.match(r'^\s*▪\s*(.+)$',s)
        if mr: current_round=mr.group(1).strip()
        mm=pat_v.match(s)
        if mm and current_date:
            tm,home,away,hg,ag,_,_=mm.groups(); dt=current_date+'T'+(tm+':00' if tm else '00:00:00')
            add_row(country,comp,div,season,current_round,dt,home.strip(),away.strip(),float(hg),float(ag),'',{},'openfootball',url,str(p.relative_to(ROOT)))
            continue
        mm2=pat_score.match(s)
        if mm2 and current_date:
            tm,home,hg,ag,_,_,away=mm2.groups(); dt=current_date+'T'+(tm+':00' if tm else '00:00:00')
            # Ignore scorer/event continuation lines: they do not start with a time and contain no team-v-team structure.
            if not s.strip().startswith('(') and len(home.strip())>1 and len(away.strip())>1:
                add_row(country,comp,div,season,current_round,dt,home.strip(),away.strip(),float(hg),float(ag),'',{},'openfootball',url,str(p.relative_to(ROOT)))

# Save accumulated canonical and odds.
new=pd.DataFrame(rows)
if len(new):
    out=pd.concat([existing.drop(columns=['match_key']),new.drop(columns=['match_key'])],ignore_index=True)
else: out=existing.drop(columns=['match_key'])
out=out[cols]
out.to_csv(CANON,index=False)

odds_path=PROC/'odds_observations_real_nonpit.csv'
if odds:
    odf=pd.DataFrame(odds)
    if odds_path.exists():
        old=pd.read_csv(odds_path)
        odf=pd.concat([old,odf],ignore_index=True).drop_duplicates()
    odf.to_csv(odds_path,index=False)

# Materialized source manifest.
for p in sorted(RAW.iterdir()):
    if p.is_file() and p.name in {'epl_2526_github_real.csv','football_data_e0_2425.csv','football_data_e1_2425.csv','football_data_e2_2425.csv','football_data_e3_2425.csv','openfootball_england_championship_2526.txt','openfootball_germany_bundesliga_2526.txt','openfootball_italy_seriea_2526.txt'}:
        b=p.read_bytes(); manifests.append({'source_file':p.name,'status':'MATERIALIZED','bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'retrieval_timestamp':datetime.utcnow().isoformat()+'Z'})
json.dump(manifests,open(MAN/'REAL_MATERIALIZED_SOURCES.json','w'),indent=2)

# Coverage + quality.
allm=out.copy(); allm['date']=allm.kickoff_timestamp.astype(str).str[:10]
coverage=allm.groupby(['country','competition','division','season']).size().reset_index(name='matches').sort_values('matches',ascending=False)
coverage.to_csv(ROOT/'data/model/global_real_materialized_coverage.csv',index=False)
quality={'total_real_rows':int(len(allm)),'new_rows':int(len(new)),'new_unique_matches':int(len(new)),'countries':int(allm.country.nunique()),'competitions':int(allm.competition.nunique()),'seasons':int(allm.season.nunique()),'odds_rows':int(len(pd.read_csv(odds_path)) if odds_path.exists() else 0),'timestamped_odds_rows':0,'pit_validated_rows':0,'pit_unknown_or_nonpit_rows':int(len(allm)),'duplicates_by_key':int(allm.assign(k=allm.season.astype(str)+'|'+allm.country.astype(str)+'|'+allm.competition.astype(str)+'|'+allm.home_team.astype(str)+'|'+allm.away_team.astype(str)+'|'+allm.date).duplicated().sum())}
json.dump(quality,open(REPORT/'EXPANSION_REAL_DATA_QUALITY.json','w'),indent=2)
print(json.dumps(quality,indent=2))
print('\nNEW BY COMPETITION')
print(new.groupby(['country','competition','season']).size().to_string() if len(new) else 'NONE')
