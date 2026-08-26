import pandas as pd
from ml.app.research.cycle15.h005 import evaluate_h005

def test_h005_freezes_two_percent_rule_and_accepts_pit_only():
    df=pd.DataFrame([
      {'event_id':'e1','kickoff_timestamp':'2026-08-25T20:00:00Z','decision_timestamp':'2026-08-25T18:00:00Z','provider_timestamp':'2026-08-25T17:00:00Z','bookmaker':'bet365','selection':'home','odds':2.10,'reference_odds':2.00,'pit_status':'EXACT_PIT','result':'WIN'},
      {'event_id':'e2','kickoff_timestamp':'2026-08-25T20:00:00Z','decision_timestamp':'2026-08-25T18:00:00Z','provider_timestamp':'2026-08-25T17:00:00Z','bookmaker':'bet365','selection':'home','odds':2.01,'reference_odds':2.00,'pit_status':'EXACT_PIT','result':'LOSS'},
      {'event_id':'e3','kickoff_timestamp':'2026-08-25T20:00:00Z','decision_timestamp':'2026-08-25T18:00:00Z','provider_timestamp':'2026-08-25T17:00:00Z','bookmaker':'bet365','selection':'home','odds':2.20,'reference_odds':2.00,'pit_status':'NON_PIT','result':'WIN'},
    ])
    out=evaluate_h005(df,threshold=0.02)
    assert out['eligible_bets']==1
    assert out['frozen_threshold']==0.02
    assert out['status']=='INSUFFICIENT_SAMPLE'
