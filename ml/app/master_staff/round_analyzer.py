from __future__ import annotations
import json, math
from pathlib import Path
import pandas as pd

REQUIRED_STATUS = {"EXACT_PIT", "VALID_PIT"}

def load_round(path: Path) -> pd.DataFrame:
    raw=json.loads(Path(path).read_text(encoding='utf-8'))
    rows=[]
    for m in raw['matches']:
        rows.append({
            'competition':m['competition'],'season':m['season'],'stage':m['stage'],'round':m['round'],'leg':m['leg'],
            'home_team':m['home_team'],'away_team':m['away_team'],'kickoff_local':m['kickoff_local'],'venue':m['venue'],'country':m['country'],
            'first_leg':m['first_leg'],'aggregate':m['aggregate'],'home_needs':m['home_needs'],'away_needs':m['away_needs'],
            'source_url':m['source_url'],'odds_source_url':m['odds_source_url'],'odds_recorded_date':m['odds_recorded_date'],
            'odds_recorded_time':m['odds_recorded_time'],'odds_timezone':m['odds_timezone'],'odds_bookmaker':m['odds_bookmaker'],
            'home_odds':m['home_odds'],'draw_odds':m['draw_odds'],'away_odds':m['away_odds'],
            'odds_pit_status':m['odds_pit_status'],'altitude_m':m['context'].get('altitude_m'),
            'aggregate_pressure':m['context'].get('aggregate_pressure'),'known_absence_status':m['context'].get('known_absence_status')
        })
    return pd.DataFrame(rows)

def implied(o): return 1.0/o if pd.notna(o) and float(o)>1 else math.nan

def add_market_math(df: pd.DataFrame) -> pd.DataFrame:
    out=df.copy()
    for side in ('home','draw','away'):
        out[f'{side}_implied']=out[f'{side}_odds'].map(implied)
    total=out[['home_implied','draw_implied','away_implied']].sum(axis=1)
    for side in ('home','draw','away'):
        out[f'{side}_market_fair_prob']=out[f'{side}_implied']/total
        out[f'{side}_vig_component']=out[f'{side}_implied']-out[f'{side}_market_fair_prob']
    out['market_pit_eligible']=out.odds_pit_status.isin(REQUIRED_STATUS)
    out['value_gate']='NO_BET'
    out['value_reason']='PIT_NOT_EXACT_OR_VALID'
    out['model_status']='INSUFFICIENT_DATA'
    out['edge_status']='EDGE_NOT_DETERMINED'
    return out

def run_round(canonical: pd.DataFrame, round_df: pd.DataFrame) -> pd.DataFrame:
    out=add_market_math(round_df)
    # Independent historical support is intentionally conservative: require >=5 prior canonical matches for both teams.
    hist=canonical.copy()
    hist['kickoff_timestamp']=pd.to_datetime(hist['kickoff_timestamp'],errors='coerce')
    support=[]
    for r in out.itertuples():
        for team in (r.home_team,r.away_team):
            h=hist[(hist.home_team==team)|(hist.away_team==team)]
            support.append((r.home_team,r.away_team,team,len(h)))
    counts=pd.DataFrame(support,columns=['home_team','away_team','team','prior_matches'])
    pivot=counts.pivot_table(index=['home_team','away_team'],columns='team',values='prior_matches',aggfunc='max').reset_index()
    pivot['min_prior_support']=pivot.drop(columns=['home_team','away_team']).min(axis=1)
    out=out.merge(pivot[['home_team','away_team','min_prior_support']],on=['home_team','away_team'],how='left')
    out['model_status']=out['min_prior_support'].apply(lambda x:'RESEARCH_BASELINE_AVAILABLE' if pd.notna(x) and x>=5 else 'INSUFFICIENT_DATA')
    # No market edge can pass without exact/valid PIT odds and a separately validated model.
    out.loc[out['model_status']!='RESEARCH_BASELINE_AVAILABLE','value_reason']='INSUFFICIENT_HISTORICAL_TEAM_SUPPORT'
    return out
