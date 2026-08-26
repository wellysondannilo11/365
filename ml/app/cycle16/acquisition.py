from __future__ import annotations
import socket, urllib.parse, urllib.request
from pathlib import Path
import hashlib, shutil, time

def source_registry():
    return [
      {'name':'sharpapi','type':'timestamped_snapshot','url':'https://github.com/Sharp-API/sports-odds-sample-data','status':'DISCOVERED_PUBLIC'},
      {'name':'beatthebookie','type':'continuous_odds_series','url':'https://github.com/Lisandro79/BeatTheBookie','status':'DISCOVERED_PUBLIC'},
      {'name':'fabul0us_football_odds_2023_24','type':'multisnapshot','url':'https://huggingface.co/datasets/fabul0us/football_odds_2023-24','status':'DISCOVERED_PUBLIC'},
      {'name':'the_odds_api_historical','type':'historical_snapshot_api','url':'https://the-odds-api.com','status':'CREDENTIAL_AND_NETWORK_REQUIRED'},
      {'name':'betfair_historical','type':'exchange_historical','url':'https://historicdata.betfair.com/','status':'ACCOUNT_OR_DOWNLOAD_REQUIRED'},
    ]

def runtime_probe(urls):
    out=[]
    for u in urls:
        host=urllib.parse.urlparse(u).hostname
        try: socket.gethostbyname(host)
        except OSError as e: out.append({'url':u,'status':'DNS_BLOCKED','error':str(e)}); continue
        try:
            req=urllib.request.Request(u,method='HEAD',headers={'User-Agent':'robo-da-bet-cycle16/1.0'})
            with urllib.request.urlopen(req,timeout=5) as r: out.append({'url':u,'status':'HTTPS_OK','http_status':r.status})
        except Exception as e: out.append({'url':u,'status':'HTTPS_BLOCKED','error':str(e)})
    return out

def persist_raw(src:Path,dst:Path):
    dst.parent.mkdir(parents=True,exist_ok=True); tmp=dst.with_suffix(dst.suffix+'.tmp'); shutil.copyfile(src,tmp); tmp.replace(dst)
    h=hashlib.sha256(dst.read_bytes()).hexdigest(); return {'path':str(dst),'bytes':dst.stat().st_size,'sha256':h}
