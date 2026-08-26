import pandas as pd
from ml.app.master_staff.context_engine import build_h2h_temporal, build_rest_features

def sample():
    return pd.DataFrame([
      {'canonical_match_id':'1','kickoff_timestamp':'2024-01-01','home_team':'A','away_team':'B','home_goals':1,'away_goals':0},
      {'canonical_match_id':'2','kickoff_timestamp':'2024-02-01','home_team':'A','away_team':'B','home_goals':0,'away_goals':2},
      {'canonical_match_id':'3','kickoff_timestamp':'2024-03-01','home_team':'A','away_team':'B','home_goals':1,'away_goals':1},
    ])

def test_h2h_is_prior_only():
    d=sample(); d['kickoff_timestamp']=pd.to_datetime(d.kickoff_timestamp); d['canonical_match_id']=d.canonical_match_id.astype(str)
    x=build_h2h_temporal(d); assert x.iloc[0].h2h_n3==0; assert x.iloc[2].h2h_n3==2

def test_rest_is_prior_only():
    d=sample(); d['kickoff_timestamp']=pd.to_datetime(d.kickoff_timestamp); d['canonical_match_id']=d.canonical_match_id.astype(str)
    x=build_rest_features(d); assert pd.isna(x.iloc[0].home_rest_days); assert x.iloc[1].home_rest_days>30
