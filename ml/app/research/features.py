from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import math
import pandas as pd
import numpy as np

@dataclass(frozen=True)
class FeatureValue:
    name: str; value: float; as_of: pd.Timestamp; available_at: pd.Timestamp; source: str; lineage: tuple[str,...]; version: str='v16.0'

class HistoricalFeatureBuilder:
    """Builds pre-match features strictly from records whose available_at <= decision_time.

    The current event is never inserted into a team's history until its features have been emitted.
    """
    def __init__(self, decay=0.15, elo_k=20.0, max_history=20):
        self.decay=decay; self.elo_k=elo_k; self.max_history=max_history

    @staticmethod
    def _ewma(values, alpha):
        if not values: return np.nan
        x=float(values[0])
        for v in values[1:]: x=alpha*float(v)+(1-alpha)*x
        return x

    def _team_state(self):
        return defaultdict(lambda: {'elo':1500.0,'matches':deque(maxlen=self.max_history), 'last_event':None})

    def build(self, df: pd.DataFrame, decision_col='decision_time', source='historical'):
        d=df.copy()
        required={'event_id','event_time',decision_col,'home_team','away_team'}
        missing=required-set(d.columns)
        if missing: raise ValueError(f'MISSING_FEATURE_COLUMNS:{sorted(missing)}')
        for c in ('event_time',decision_col,'available_at','outcome_available_at','result_available_at','stats_available_at'):
            if c in d: d[c]=pd.to_datetime(d[c],utc=True,errors='coerce')
        if d[decision_col].isna().any(): raise ValueError('INVALID_DECISION_TIME')
        if 'available_at' not in d: d['available_at']=d[decision_col]
        if (d.available_at>d[decision_col]).any(): raise ValueError('POINT_IN_TIME_VIOLATION')
        # A pre-match row's availability and its eventual outcome availability are
        # different clocks. Never infer the latter from event_time or ingestion time.
        outcome_col=next((c for c in ('outcome_available_at','result_available_at','stats_available_at') if c in d.columns),None)
        d=d.sort_values(['event_time','event_id'],kind='stable').reset_index(drop=True)
        states=self._team_state(); rows=[]; lineage=[]
        def usable_history(team, decision):
            st=states[team]
            return [h for h in st['matches'] if pd.Timestamp(h['available_at']) <= decision]
        def val(hist,key): return [h[key] for h in hist if h.get(key) is not None and pd.notna(h.get(key))]
        for _,r in d.iterrows():
            decision=pd.Timestamp(r[decision_col]); home=str(r.home_team); away=str(r.away_team)
            hh=usable_history(home,decision); ah=usable_history(away,decision)
            rh=states[home]['elo']; ra=states[away]['elo']
            def avg(team_hist,key,n=5):
                z=val(team_hist,key)[-n:]
                return float(np.mean(z)) if z else np.nan
            def ew(team_hist,key,n=5):
                z=val(team_hist,key)[-n:]
                return self._ewma(z,2/(n+1)) if z else np.nan
            days_h=(decision-pd.Timestamp(states[home]['last_event'])).total_seconds()/86400 if states[home]['last_event'] else np.nan
            days_a=(decision-pd.Timestamp(states[away]['last_event'])).total_seconds()/86400 if states[away]['last_event'] else np.nan
            def points(hist,n=5):
                z=hist[-n:]; return float(np.mean([3 if h['gf']>h['ga'] else 1 if h['gf']==h['ga'] else 0 for h in z])) if z else np.nan
            def rate(hist,fn,n=5):
                z=hist[-n:]; return float(np.mean([1.0 if fn(h) else 0.0 for h in z])) if z else np.nan
            vals={
                'elo_home_prior':rh,'elo_away_prior':ra,'elo_delta':rh-ra,
                'home_goals_for_ewma5':ew(hh,'gf',5),'home_goals_against_ewma5':ew(hh,'ga',5),
                'away_goals_for_ewma5':ew(ah,'gf',5),'away_goals_against_ewma5':ew(ah,'ga',5),
                'home_xg_for_ewma5':ew(hh,'xgf',5),'home_xg_against_ewma5':ew(hh,'xga',5),
                'away_xg_for_ewma5':ew(ah,'xgf',5),'away_xg_against_ewma5':ew(ah,'xga',5),
                'home_xgd_ewma5':(ew(hh,'xgf',5)-ew(hh,'xga',5)) if hh else np.nan,
                'away_xgd_ewma5':(ew(ah,'xgf',5)-ew(ah,'xga',5)) if ah else np.nan,
                'home_shots_ewma5':ew(hh,'shots',5),'away_shots_ewma5':ew(ah,'shots',5),
                'home_sot_ewma5':ew(hh,'sot',5),'away_sot_ewma5':ew(ah,'sot',5),
                'home_points_per_match5':points(hh,5),'away_points_per_match5':points(ah,5),
                'home_win_rate5':rate(hh,lambda h:h['gf']>h['ga'],5),'away_win_rate5':rate(ah,lambda h:h['gf']>h['ga'],5),
                'home_btts_rate5':rate(hh,lambda h:h['gf']>0 and h['ga']>0,5),'away_btts_rate5':rate(ah,lambda h:h['gf']>0 and h['ga']>0,5),
                'home_over25_rate5':rate(hh,lambda h:(h['gf']+h['ga'])>2,5),'away_over25_rate5':rate(ah,lambda h:(h['gf']+h['ga'])>2,5),
                'home_days_since_last_match':days_h,'away_days_since_last_match':days_a,
                'home_matches_last_7d':sum(1 for h in hh if (decision-pd.Timestamp(h['event_time'])).total_seconds()<=7*86400),
                'away_matches_last_7d':sum(1 for h in ah if (decision-pd.Timestamp(h['event_time'])).total_seconds()<=7*86400),
                'home_matches_last_14d':sum(1 for h in hh if (decision-pd.Timestamp(h['event_time'])).total_seconds()<=14*86400),
                'away_matches_last_14d':sum(1 for h in ah if (decision-pd.Timestamp(h['event_time'])).total_seconds()<=14*86400),
            }
            row={'event_id':str(r.event_id),'decision_time':decision,'event_time':pd.Timestamp(r.event_time),'feature_version':'v16.0'}; row.update(vals); rows.append(row)
            for name,v in vals.items():
                # lineage only points to actually usable prior event ids.
                srcids=[]
                team=home if name.startswith('home_') or name.startswith('elo_home') else away
                for h in (hh if team==home else ah)[-5:]: srcids.append(str(h['event_id']))
                src_hist=(hh if team==home else ah)[-5:]
                available=max((pd.Timestamp(h['available_at']) for h in src_hist), default=decision)
                lineage.append(FeatureValue(name,float(v) if pd.notna(v) else np.nan,decision,available,source,tuple(srcids)))
            # Only after emitting features do we add the current event to history, and only if its outcome data is available.
            if outcome_col and 'home_goals' in r and 'away_goals' in r and pd.notna(r.home_goals) and pd.notna(r.away_goals):
                outcome_available=pd.Timestamp(r[outcome_col]) if pd.notna(r[outcome_col]) else pd.NaT
                if pd.isna(outcome_available):
                    raise ValueError('INVALID_OUTCOME_AVAILABILITY')
                hg=float(r.home_goals); ag=float(r.away_goals)
                expected=1/(1+10**((ra-rh)/400)); score=1 if hg>ag else .5 if hg==ag else 0
                states[home]['elo']=rh+self.elo_k*(score-expected); states[away]['elo']=ra+self.elo_k*((1-score)-(1-expected))
                event_avail=outcome_available
                states[home]['matches'].append({'event_id':r.event_id,'event_time':r.event_time,'available_at':event_avail,'gf':hg,'ga':ag,'xgf':r.get('home_xg',np.nan),'xga':r.get('away_xg',np.nan),'shots':r.get('home_shots',np.nan),'sot':r.get('home_sot',np.nan)})
                states[away]['matches'].append({'event_id':r.event_id,'event_time':r.event_time,'available_at':event_avail,'gf':ag,'ga':hg,'xgf':r.get('away_xg',np.nan),'xga':r.get('home_xg',np.nan),'shots':r.get('away_shots',np.nan),'sot':r.get('away_sot',np.nan)})
                states[home]['last_event']=r.event_time; states[away]['last_event']=r.event_time
        return pd.DataFrame(rows), lineage
