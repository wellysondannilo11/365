from __future__ import annotations
from dataclasses import dataclass
import math
from datetime import datetime
from .schemas import MatchSnapshot
from .lineage import FeatureLineage
from .temporal import assert_point_in_time

@dataclass
class FeatureVector:
    values: dict
    lineage: list[FeatureLineage]


def ewma(values, alpha):
    if not values: return 0.0
    x=float(values[0])
    for v in values[1:]: x=alpha*float(v)+(1-alpha)*x
    return x

def build_features(m: MatchSnapshot, as_of: datetime, history: dict | None=None) -> FeatureVector:
    assert_point_in_time(m.available_at, as_of)
    history=history or {}
    total_xg=m.xg_home+m.xg_away
    shots=max(m.shots,1)
    minute=max(m.minute,1)
    values={
      'minute':m.minute,'score_diff':m.home_goals-m.away_goals,'total_xg':total_xg,
      'shots':m.shots,'shots_on_target':m.shots_on_target,'sot_rate':m.shots_on_target/shots,
      'big_chances':m.big_chances,'dangerous_attacks':m.dangerous_attacks,'dangerous_per_min':m.dangerous_attacks/minute,
      'box_entries':m.box_entries,'box_per_min':m.box_entries/minute,'field_tilt':(m.possession_home-50)/50,
      'ppda_home':m.ppda_home,'corners':m.corners,'red_cards':m.red_cards,
      'xg_for_ewma':history.get('xg_for_ewma',0.0),'xg_against_ewma':history.get('xg_against_ewma',0.0),
      'xgd':history.get('xgd',0.0),'elo_overall':history.get('elo_overall',0.0),'elo_delta':history.get('elo_delta',0.0),
      'attack_strength':history.get('attack_strength',0.0),'defense_strength':history.get('defense_strength',0.0),
      'opponent_adjusted_form':history.get('opponent_adjusted_form',0.0),
      'days_since_last_match':history.get('days_since_last_match',0.0),'matches_last_7d':history.get('matches_last_7d',0.0),
      'matches_last_14d':history.get('matches_last_14d',0.0),'coach_tenure':history.get('coach_tenure',0.0),
      'days_since_manager_change':history.get('days_since_manager_change',0.0),'coach_change_flag':history.get('coach_change_flag',0.0),
      'starter_strength':history.get('starter_strength',0.0),'missing_attack_strength':history.get('missing_attack_strength',0.0),
      'missing_defense_strength':history.get('missing_defense_strength',0.0),'lineup_continuity':history.get('lineup_continuity',0.0),
      'expected_minutes_lost':history.get('expected_minutes_lost',0.0),'injury_impact':history.get('injury_impact',0.0),
      'opening_price':history.get('opening_price',0.0),'current_price':history.get('current_price',0.0),
      'market_dispersion':history.get('market_dispersion',0.0), 'overround':history.get('overround',0.0),
    }
    lineage=[FeatureLineage(k,'v1','match',m.event_id,as_of,m.available_at,m.source,f'{m.source}:{m.event_id}') for k in values]
    for l in lineage:l.validate()
    return FeatureVector(values,lineage)

def temperature(m:MatchSnapshot):
    minute=max(m.minute,1); rate_xg=(m.xg_home+m.xg_away)/max(minute/90,.25)
    score=30*min(rate_xg,4)/4
    score+=20*min(m.shots_on_target/6,1); score+=15*min(m.big_chances/3,1)
    score+=15*min(m.dangerous_attacks/max(minute*1.2,1),1)
    score+=10*min(m.box_entries/max(minute*.35,1),1); score+=10*min(m.corners/7,1)
    return round(max(0,min(100,score)),2)
