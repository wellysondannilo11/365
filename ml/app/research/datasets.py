from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib, json
import pandas as pd
from ..pit_store.pit import validate_frame, dataset_hash
from ..ingestion.schema import read_source, validate_schema, canonicalize

@dataclass(frozen=True)
class DatasetManifest:
    dataset_id:str; version:str; created_at:str; source_hashes:tuple[str,...]; schema_version:str
    feature_version:str; cutoff_policy:str; time_start:str|None; time_end:str|None; records:int; dataset_hash:str
    status:str='VALIDATED'; source:str='UNKNOWN'

def _source_hash(df):
    payload=df.sort_index(axis=1).to_json(orient='records',date_format='iso',default_handler=str)
    return hashlib.sha256(payload.encode()).hexdigest()

def build_point_in_time_dataset(source, dataset_type='matches', version='v16.0', feature_version='v16.0', decision_cutoff=None, source_name='UNKNOWN'):
    df=canonicalize(read_source(source) if isinstance(source,(str,Path)) else source.copy())
    validate_schema(df,dataset_type)
    if dataset_type in ('matches','stats','events'):
        if not {'available_at','decision_time'}.issubset(df.columns):
            raise ValueError('REAL_POINT_IN_TIME_DATASET_REQUIRES_AVAILABLE_AT_AND_DECISION_TIME')
        validate_frame(df)
    if decision_cutoff is not None:
        cutoff=pd.Timestamp(decision_cutoff)
        if cutoff.tzinfo is None: cutoff=cutoff.tz_localize('UTC')
        else: cutoff=cutoff.tz_convert('UTC')
        df=df[df.decision_time<=cutoff].copy()
    h=dataset_hash(df); sh=_source_hash(df)
    manifest=DatasetManifest(dataset_id=h[:20],version=version,created_at=pd.Timestamp.now(tz='UTC').isoformat(),source_hashes=(sh,),schema_version='v16.0',feature_version=feature_version,cutoff_policy='available_at <= decision_time',time_start=str(df.event_time.min()) if len(df) else None,time_end=str(df.event_time.max()) if len(df) else None,records=len(df),dataset_hash=h,source=source_name)
    return df,manifest

def save_manifest(manifest,path): Path(path).write_text(json.dumps(asdict(manifest),indent=2,default=str),encoding='utf-8')
