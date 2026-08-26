from __future__ import annotations
import hashlib
import pandas as pd


def _iso(v):
    t=pd.to_datetime(v,utc=True,errors='coerce')
    return None if pd.isna(t) else t.isoformat()


def normalize_sharpapi(df: pd.DataFrame, source='sharpapi') -> pd.DataFrame:
    out=pd.DataFrame({
      'source':source,'source_record_id':df.get('id'),'event_id':df.get('event_id'),
      'kickoff_timestamp':df.get('event_start_time').map(_iso),'provider_timestamp':df.get('timestamp').map(_iso),
      'bookmaker':df.get('sportsbook'),'market':df.get('market_type'),'selection':df.get('selection'),
      'selection_type':df.get('selection_type'),'odds':pd.to_numeric(df.get('odds_decimal'),errors='coerce'),
      'line':df.get('line'),'home_team':df.get('home_team'),'away_team':df.get('away_team'),
      'is_live':df.get('is_live',False)
    })
    return out


def normalize_btb(df: pd.DataFrame, source='beat_the_bookie') -> pd.DataFrame:
    result=df['result'].astype(str).map({'1':'home','2':'draw','3':'away','H':'home','D':'draw','A':'away'}).fillna(df['result'].astype(str))
    return pd.DataFrame({
      'source':source,'source_record_id':df['ID'].astype(str),'event_id':df['ID'].astype(str),
      'kickoff_timestamp':df['date'].map(_iso),'provider_timestamp':df['odds_datetime'].map(_iso),
      'bookmaker':df['bookmaker'],'market':df['bettype'],'selection':result,
      'selection_type':'side','odds':pd.to_numeric(df['odds'],errors='coerce'),
      'line':None,'home_team':df['team1'],'away_team':df['team2'],'is_live':False
    })


def raw_sha256(path: str) -> str:
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def source_registry() -> list[dict]:
    return [
      {'source':'sharpapi_sample','type':'historical_snapshot','temporal_semantics':'provider capture timestamp','license':'CC BY 4.0','status':'AVAILABLE_PUBLIC_SOURCE','url':'https://github.com/Sharp-API/sports-odds-sample-data'},
      {'source':'fabul0us_football_odds_2023_24','type':'historical_multisnapshot','temporal_semantics':'collection timestamps','license':'CC','status':'AVAILABLE_PUBLIC_SOURCE','url':'https://huggingface.co/datasets/fabul0us/football_odds_2023-24'},
      {'source':'beat_the_bookie','type':'historical_odds_series','temporal_semantics':'odds_datetime','license':'repository license','status':'EXTERNAL_DATASET_NOT_MATERIALIZED','url':'https://github.com/Lisandro79/BeatTheBookie'},
      {'source':'the_odds_api_historical','type':'historical_snapshot_api','temporal_semantics':'provider snapshot timestamp','status':'REQUIRES_CREDENTIALS_AND_NETWORK','url':'https://the-odds-api.com'}
    ]
