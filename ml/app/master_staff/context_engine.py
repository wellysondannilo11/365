from __future__ import annotations
from collections import defaultdict
import pandas as pd
import numpy as np


def build_h2h_temporal(d: pd.DataFrame, windows=(3,5,10,20)) -> pd.DataFrame:
    d=d.sort_values(['kickoff_timestamp','canonical_match_id']).reset_index(drop=True)
    hist=defaultdict(list); rows=[]
    for r in d.itertuples(index=False):
        key=tuple(sorted((str(r.home_team),str(r.away_team))))
        prior=hist[key]
        vals={}
        for n in windows:
            h=prior[-n:]
            vals[f'h2h_n{n}']=len(h)
            vals[f'h2h_goals{n}']=float(np.mean([x['hg']+x['ag'] for x in h])) if h else np.nan
            vals[f'h2h_btts{n}']=float(np.mean([x['hg']>0 and x['ag']>0 for x in h])) if h else np.nan
            vals[f'h2h_draw_rate{n}']=float(np.mean([x['winner']=='DRAW' for x in h])) if h else np.nan
            vals[f'h2h_home_team_win_rate{n}']=float(np.mean([x['winner']==r.home_team for x in h])) if h else np.nan
        rows.append(vals)
        if pd.notna(r.home_goals) and pd.notna(r.away_goals):
            winner=r.home_team if r.home_goals>r.away_goals else r.away_team if r.away_goals>r.home_goals else 'DRAW'
            hist[key].append({'hg':float(r.home_goals),'ag':float(r.away_goals),'winner':winner})
    return pd.DataFrame(rows)


def build_rest_features(d: pd.DataFrame) -> pd.DataFrame:
    d=d.sort_values(['kickoff_timestamp','canonical_match_id']).reset_index(drop=True)
    last={}; games=defaultdict(list); out=[]
    for r in d.itertuples(index=False):
        row={}
        for side,team in [('home',r.home_team),('away',r.away_team)]:
            t=r.kickoff_timestamp
            row[f'{side}_rest_days']=(t-last[team]).total_seconds()/86400 if team in last and pd.notna(t) else np.nan
            for n in (3,5,7,14,21):
                cutoff=t-pd.Timedelta(days=n) if pd.notna(t) else None
                row[f'{side}_matches_last_{n}d']=sum(1 for x in games[team] if cutoff is not None and x>=cutoff)
        row['rest_advantage']=row['home_rest_days']-row['away_rest_days'] if pd.notna(row['home_rest_days']) and pd.notna(row['away_rest_days']) else np.nan
        out.append(row)
        if pd.notna(r.kickoff_timestamp):
            for team in (r.home_team,r.away_team):
                last[team]=r.kickoff_timestamp; games[team].append(r.kickoff_timestamp)
    return pd.DataFrame(out)


def build_context(d: pd.DataFrame) -> pd.DataFrame:
    d=d.copy(); d['kickoff_timestamp']=pd.to_datetime(d['kickoff_timestamp'],errors='coerce')
    h2h=build_h2h_temporal(d)
    rest=build_rest_features(d)
    out=pd.concat([h2h,rest],axis=1)
    out['rivalry_status']='UNKNOWN'
    out['rivalry_effect_status']='INSUFFICIENT_DATA'
    out['importance_status']=np.where(d['round'].astype(str).str.contains('final|semi|quarter|knockout|playoff',case=False,regex=True,na=False),'STAGE_CONTEXT_ONLY','UNKNOWN')
    out['aggregate_state']='UNKNOWN'
    out['player_context_status']='NOT_MATERIALIZED'
    out['injury_context_status']='NOT_MATERIALIZED'
    out['lineup_context_status']='NOT_MATERIALIZED'
    out['live_context_status']='NOT_MATERIALIZED'
    return out
