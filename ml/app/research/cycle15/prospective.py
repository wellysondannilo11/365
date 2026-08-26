from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import requests

def collect_once(url: str, out_dir: str | Path, timeout: int=15) -> dict:
    if not os.getenv('SHARPAPI_API_KEY'):
        return {'status':'BLOCKED_AUTH','reason':'SHARPAPI_API_KEY_MISSING','rows':0}
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    try:
        r=requests.get(url,headers={'Authorization':f"Bearer {os.environ['SHARPAPI_API_KEY']}"},timeout=timeout)
        r.raise_for_status(); raw=r.content
        digest=hashlib.sha256(raw).hexdigest()
        p=out/f'raw_{digest}.json'; p.write_bytes(raw)
        return {'status':'ACQUIRED','rows':len(r.json()) if isinstance(r.json(),list) else None,'raw_hash':digest,'path':str(p)}
    except Exception as exc:
        return {'status':'BLOCKED_NETWORK','reason':type(exc).__name__+': '+str(exc),'rows':0}
