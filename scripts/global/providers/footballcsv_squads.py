from __future__ import annotations
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib, json

BASE='https://raw.githubusercontent.com/footballcsv/cache.footballsquads/master/'
TEAMS={
 'flamengo':'brazil/2024/seriea/flamengo.txt',
 'palmeiras':'brazil/2024/seriea/palmeir.txt',
}

def download_team(team, dest):
    rel=TEAMS[team]; url=BASE+rel
    req=Request(url,headers={'User-Agent':'RoboDaBet-FreeAcquisition/6.0'})
    with urlopen(req,timeout=30) as r: data=r.read()
    p=Path(dest); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
    return {'team':team,'url':url,'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'state':'DOWNLOADED'}
