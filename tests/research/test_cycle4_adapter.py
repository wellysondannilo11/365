import pandas as pd
from ml.app.adapters.odds import TheOddsAPI

def test_historical_snapshot_clock_is_distinct_from_nested_update_clocks():
    payload={
      'timestamp':'2023-11-29T22:40:39Z',
      'data':[{'id':'e1','commence_time':'2023-11-30T00:10:00Z','bookmakers':[{'key':'book','last_update':'2023-11-29T22:40:09Z','markets':[{'key':'h2h','last_update':'2023-11-29T22:40:55Z','outcomes':[{'name':'Home','price':2.5}]}]}]}]
    }
    d=TheOddsAPI.normalize_historical_response(payload)
    assert len(d)==1
    r=d.iloc[0]
    assert r['snapshot_timestamp']==pd.Timestamp('2023-11-29T22:40:39Z')
    assert r['market_last_update']==pd.Timestamp('2023-11-29T22:40:55Z')
    assert r['source_timestamp']==r['snapshot_timestamp']
    assert r['available_at']==r['snapshot_timestamp']
