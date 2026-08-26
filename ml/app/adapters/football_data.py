from __future__ import annotations
import io
import requests
import pandas as pd

class FootballDataAdapter:
    """Real historical results/stats/odds adapter for football-data.co.uk.

    The provider exposes an opening/pre-closing odds set and, for newer seasons,
    a closing set. The CSVs do NOT contain exact odds publication timestamps.
    Therefore imported opening odds are marked PREMATCH_BOUNDED, not exact PIT.
    """
    name='football-data'
    base='https://www.football-data.co.uk/mmz4281'
    def __init__(self, timeout=30): self.timeout=timeout
    def fetch_season(self, season_code, league_code='E0'):
        url=f'{self.base}/{season_code}/{league_code}.csv'
        r=requests.get(url,timeout=self.timeout,headers={'User-Agent':'RoboDaBet/V18'})
        r.raise_for_status(); df=pd.read_csv(io.BytesIO(r.content))
        df['_source_url']=url; df['_source']='football-data.co.uk'; df['_season_code']=season_code; df['_league_code']=league_code
        return df
    @staticmethod
    def normalize_matches(df):
        d=df.copy(); d['event_id']=[f"football-data:{r.get('Date')}:{r.get('HomeTeam')}:{r.get('AwayTeam')}:{i}" for i,(_,r) in enumerate(d.iterrows())]
        time_series=d['Time'].fillna('00:00').astype(str) if 'Time' in d.columns else pd.Series(['00:00']*len(d),index=d.index)
        d['event_time']=pd.to_datetime(d['Date'].astype(str)+' '+time_series,dayfirst=True,errors='coerce',utc=True)
        d['home_team']=d['HomeTeam'].astype(str); d['away_team']=d['AwayTeam'].astype(str)
        d['home_goals']=pd.to_numeric(d.get('FTHG'),errors='coerce'); d['away_goals']=pd.to_numeric(d.get('FTAG'),errors='coerce')
        d['available_at']=pd.NaT; d['decision_time']=d['event_time']; d['source_time']=pd.NaT; d['ingested_at']=pd.Timestamp.now(tz='UTC')
        d['availability_evidence']='EVENT_LEVEL_SOURCE_ONLY'; d['source']='football-data.co.uk'
        return d
    @staticmethod
    def odds_long(df, bookmaker_prefixes=None):
        d=df.copy(); prefixes=bookmaker_prefixes or ['B365','BW','IW','PS','WH','VC','LB','SJ','BS','SO','SB','Max','Avg']
        rows=[]
        for _,r in d.iterrows():
            event_id=f"football-data:{r.get('Date')}:{r.get('Time','00:00')}:{r.get('HomeTeam')}:{r.get('AwayTeam')}"
            captured=pd.to_datetime(str(r.get('Date')),dayfirst=True,errors='coerce',utc=True)
            for prefix in prefixes:
                cols={'Home':f'{prefix}H','Draw':f'{prefix}D','Away':f'{prefix}A'}
                if not all(c in d.columns for c in cols.values()): continue
                for sel,col in cols.items():
                    price=pd.to_numeric(r.get(col),errors='coerce')
                    if pd.notna(price) and float(price)>1:
                        rows.append({'event_id':event_id,'bookmaker':prefix,'market':'1X2','selection':sel,'line':None,'price':float(price),'captured_at':captured,'available_at':pd.NaT,'source_timestamp':pd.NaT,'source':'football-data.co.uk','availability_evidence':'PREMATCH_ODDS_SET_NO_EXACT_TIMESTAMP'})
        return pd.DataFrame(rows)
