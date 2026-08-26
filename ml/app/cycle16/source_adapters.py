from __future__ import annotations
import hashlib,json
from typing import Any
import pandas as pd

def _iso(v):
    t=pd.to_datetime(v,utc=True,errors='coerce'); return None if pd.isna(t) else t.isoformat()

def _raw_hash(row):
    return hashlib.sha256(json.dumps(dict(sorted(row.items())),sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()

def normalize_sharpapi_row(row:dict[str,Any], source='sharpapi')->dict[str,Any]:
    event_id=str(row.get('event_id') or '').strip()
    return {'event_id':event_id,'kickoff_timestamp':_iso(row.get('event_start_time') or row.get('commence_time') or row.get('event_start')),
            'provider_timestamp':_iso(row.get('timestamp')),'decision_timestamp':_iso(row.get('decision_timestamp') or row.get('timestamp')),
            'bookmaker':row.get('sportsbook') or row.get('bookmaker'),'market':row.get('market_type') or row.get('market'),
            'selection':row.get('selection') or row.get('name'),'odds':row.get('odds_decimal') if row.get('odds_decimal') is not None else row.get('price') or row.get('odds'),
            'source':source,'provenance':row.get('source_record_id') or row.get('id') or f'{source}:{event_id}',
            'raw_hash':row.get('raw_hash') or _raw_hash(row),'temporal_evidence':'PROVIDER_NATIVE_SNAPSHOT',
            'opening_semantics':row.get('opening_semantics','UNKNOWN')}

def normalize_beatthebookie_row(row:dict[str,Any])->dict[str,Any]:
    event_id=str(row.get('ID') or row.get('id') or '').strip()
    result={'1':'home','2':'draw','3':'away','H':'home','D':'draw','A':'away'}.get(str(row.get('result')),
                                                                    row.get('result'))
    return {'event_id':event_id,'kickoff_timestamp':_iso(row.get('date')),'provider_timestamp':_iso(row.get('odds_datetime')),
            'decision_timestamp':_iso(row.get('decision_timestamp') or row.get('odds_datetime')),'bookmaker':row.get('bookmaker'),
            'market':row.get('bettype'),'selection':result,'odds':row.get('odds'),'source':'beatthebookie',
            'provenance':row.get('source_record_id') or row.get('source_file') or f'beatthebookie:{event_id}',
            'raw_hash':row.get('raw_hash') or _raw_hash(row),'temporal_evidence':'PROVIDER_NATIVE_SERIES',
            'opening_semantics':'EXPLICIT_OPENING' if str(row.get('opening_closing','')).strip()=='0' and str(row.get('is_opening','')).lower()=='true' else row.get('opening_semantics','UNKNOWN')}

def normalize_sharpapi(df:pd.DataFrame, source='sharpapi')->pd.DataFrame:
    return pd.DataFrame([normalize_sharpapi_row(r,source) for r in df.to_dict('records')])

def normalize_btb(df:pd.DataFrame)->pd.DataFrame:
    return pd.DataFrame([normalize_beatthebookie_row(r) for r in df.to_dict('records')])
