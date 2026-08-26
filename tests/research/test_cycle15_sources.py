import io
import pandas as pd
from ml.app.research.cycle15.sources import normalize_sharpapi, normalize_btb

def test_sharpapi_normalizes_snapshot_fields():
    df=pd.DataFrame([{
      'id':'p1','sportsbook':'bet365','event_id':'e1','sport':'soccer','league':'x',
      'home_team':'A','away_team':'B','market_type':'moneyline','selection':'A','selection_type':'side',
      'odds_decimal':2.2,'event_start_time':'2026-08-24T20:00:00Z','timestamp':'2026-08-24T18:00:00Z','is_live':False
    }])
    out=normalize_sharpapi(df, source='sharpapi')
    assert out.loc[0,'provider_timestamp']=='2026-08-24T18:00:00+00:00'
    assert out.loc[0,'kickoff_timestamp']=='2026-08-24T20:00:00+00:00'
    assert out.loc[0,'bookmaker']=='bet365'

def test_beat_the_bookie_long_form_normalizes_odds_datetime():
    df=pd.DataFrame([{
      'ID':1,'league':'EPL','team1':'A','team2':'B','date':'2026-08-24 20:00:00',
      'bookmaker':'bet365','bettype':'1x2','result':'1','odds_datetime':'2026-08-24 18:00:00','odds':'2.2'
    }])
    out=normalize_btb(df)
    assert out.loc[0,'provider_timestamp'].startswith('2026-08-24T18:00:00')
    assert out.loc[0,'selection']=='home'
