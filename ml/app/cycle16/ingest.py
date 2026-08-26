from __future__ import annotations
import hashlib, json, zipfile
from pathlib import Path
import pandas as pd
from .source_adapters import normalize_btb, normalize_sharpapi

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def normalize_csv(path:Path,chunksize=50000):
    raw_hash=sha256_file(path); rows=[]
    for chunk in pd.read_csv(path,chunksize=chunksize,low_memory=False):
        cols={c.lower() for c in chunk.columns}
        if {'timestamp','event_start_time','sportsbook','market_type','selection','odds_decimal','event_id'}<=cols: n=normalize_sharpapi(chunk)
        elif {'odds_datetime','bookmaker','bettype','date','odds'}<=cols and ('ID' in chunk.columns or 'id' in chunk.columns): n=normalize_btb(chunk)
        else: continue
        n['raw_hash']=raw_hash; n['provenance']=n['provenance'].astype(str).map(lambda x:f'file:{path.name}:{x}')
        rows.append(n)
    return pd.concat(rows,ignore_index=True) if rows else pd.DataFrame()

def inspect_zip(path:Path):
    with zipfile.ZipFile(path) as z:
        return [{'name':i.filename,'bytes':i.file_size,'compressed':i.compress_size} for i in z.infolist() if not i.is_dir()]
