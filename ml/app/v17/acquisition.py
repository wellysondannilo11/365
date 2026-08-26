from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib, json, os, socket, urllib.request
from pathlib import Path

@dataclass
class AcquisitionAttempt:
    source: str
    classification: str
    target: str
    status: str
    reason: str
    started_at: str
    ended_at: str

SOURCES = [
    {"source":"The Odds API","classification":"A","target":"historical timestamped bookmaker snapshots","requires":"ROBO_ODDS_API_KEY"},
    {"source":"Betfair Historical Data","classification":"A","target":"timestamped exchange price/market data","requires":"purchased historical data / credentials"},
    {"source":"Football-Data.co.uk","classification":"B/C","target":"historical results, stats and opening/closing odds","requires":"network only"},
    {"source":"StatsBomb Open Data","classification":"C/D","target":"selected football event/lineup data","requires":"network only"},
    {"source":"Flashscore","classification":"D","target":"complementary live/result/stat context","requires":"legally permitted access; no scraping bypass"},
]

def fingerprint_file(path: str) -> dict:
    p=Path(path); h=hashlib.sha256(); size=0
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            size += len(chunk); h.update(chunk)
    return {"path":str(p),"sha256":h.hexdigest(),"size_bytes":size}

def network_probe(url='https://www.football-data.co.uk/data.php', timeout=8):
    started=datetime.now(timezone.utc).isoformat()
    try:
        urllib.request.urlopen(url,timeout=timeout).read(64)
        return {"status":"PASS","reason":"NETWORK_REACHABLE","started_at":started,"ended_at":datetime.now(timezone.utc).isoformat()}
    except Exception as exc:
        return {"status":"FAIL","reason":f"{type(exc).__name__}:{exc}","started_at":started,"ended_at":datetime.now(timezone.utc).isoformat()}

def attempt_provider(source: str, target: str, classification: str, url: str | None = None, env_key: str | None = None) -> AcquisitionAttempt:
    started=datetime.now(timezone.utc).isoformat(); reason=''
    if env_key and not os.getenv(env_key):
        return AcquisitionAttempt(source,classification,target,'NOT_AVAILABLE',f'MISSING_CREDENTIAL:{env_key}',started,datetime.now(timezone.utc).isoformat())
    if not url:
        return AcquisitionAttempt(source,classification,target,'NOT_AVAILABLE','NO_SAFE_AUTOMATED_ENDPOINT_CONFIGURED',started,datetime.now(timezone.utc).isoformat())
    try:
        urllib.request.urlopen(url,timeout=8).read(64)
        status='PASS'; reason='SOURCE_REACHABLE_BUT_NO_DATA_COMMITTED_WITHOUT_SCHEMA_VALIDATION'
    except Exception as exc:
        status='NOT_EXECUTED'; reason=f'{type(exc).__name__}:{exc}'
    return AcquisitionAttempt(source,classification,target,status,reason,started,datetime.now(timezone.utc).isoformat())

def save_manifest(path: str, payload: dict):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(payload,indent=2,sort_keys=True,default=str),encoding='utf-8')
    return str(p)
