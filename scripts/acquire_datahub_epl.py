#!/usr/bin/env python3
"""Acquire real EPL historical CSVs from DataHub's stable resource URLs.

This downloader is fail-closed: it never converts demo/mock/fixture data into
historical evidence. Each successfully downloaded file receives a SHA-256.
"""
from __future__ import annotations
import hashlib, json, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/datahub_epl'; RAW.mkdir(parents=True, exist_ok=True)
SEASONS=['0001','0102','0203','0304','0405','0506','0607','0708','0809','0910','1011','1112','1213','1314','1415','1516','1617','1718','1819','1920','2021','2122','2223','2324','2425','2526','9394','9495','9596','9697','9798','9899','9900']
BASE='https://datahub.io/football/english-premier-league/_r/-/season-{}.csv'

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

attempts=[]
# Fast network probe: do not spend 30s x 33 seasons when the runtime has no DNS.
try:
    req=urllib.request.Request(BASE.format('2324'),headers={'User-Agent':'RoboDaBet/football-research'})
    with urllib.request.urlopen(req,timeout=8) as r: r.read(16)
    network_ok=True
except Exception as exc:
    network_ok=False
    attempts.append({'season_code':'*','url':BASE.format('2324'),'status':'NETWORK_BLOCKED','reason':f'{type(exc).__name__}:{exc}'})
if not network_ok:
    manifest={'source':'DataHub English Premier League','source_url':'https://datahub.io/football/english-premier-league','seasons_requested':SEASONS,'attempts':attempts,'success_count':0,'created_at':datetime.now(timezone.utc).isoformat(),'classification':'HISTORICAL_REAL_ONLY'}
    (ROOT/'data/manifests/DATAHUB_EPL_ACQUISITION.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))
    raise SystemExit(2)
for season in SEASONS:
    url=BASE.format(season); dest=RAW/f'season-{season}.csv'; started=datetime.now(timezone.utc).isoformat()
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'RoboDaBet/football-research'})
        with urllib.request.urlopen(req,timeout=30) as r, dest.open('wb') as out:
            while True:
                chunk=r.read(1024*1024)
                if not chunk: break
                out.write(chunk)
        attempts.append({'season_code':season,'url':url,'status':'PASS','bytes':dest.stat().st_size,'sha256':sha256(dest),'started_at':started,'ended_at':datetime.now(timezone.utc).isoformat()})
    except Exception as exc:
        if dest.exists(): dest.unlink()
        attempts.append({'season_code':season,'url':url,'status':'BLOCKED','reason':f'{type(exc).__name__}:{exc}','started_at':started,'ended_at':datetime.now(timezone.utc).isoformat()})

manifest={'source':'DataHub English Premier League','source_url':'https://datahub.io/football/english-premier-league','seasons_requested':SEASONS,'attempts':attempts,'success_count':sum(a['status']=='PASS' for a in attempts),'created_at':datetime.now(timezone.utc).isoformat(),'classification':'HISTORICAL_REAL_ONLY'}
(ROOT/'data/manifests/DATAHUB_EPL_ACQUISITION.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(manifest,indent=2,ensure_ascii=False))
