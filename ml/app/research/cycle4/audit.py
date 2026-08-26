from __future__ import annotations
import json, os, socket
from pathlib import Path

def network_probe(host='api.the-odds-api.com'):
    try:
        ip=socket.gethostbyname(host)
        return {'host':host,'status':'RESOLVED','ip':ip}
    except Exception as e:
        return {'host':host,'status':'BLOCKED_EXTERNAL','error':type(e).__name__+':'+str(e)}

def source_audit(root):
    root=Path(root); out=[]
    configs=list(root.glob('config/free_source_registry*.json'))
    seen={}
    for f in configs:
        try: data=json.loads(f.read_text())
        except Exception: continue
        for s in data.get('sources',[]):
            sid=s.get('source_id') or s.get('id') or s.get('name')
            if not sid: continue
            seen[sid]=s
    for sid,s in sorted(seen.items()):
        name=s.get('name') or s.get('source') or sid
        if sid in {'the-odds-api','the_odds_api'} or 'Odds API' in name:
            adapter=(root/'ml/app/adapters/odds.py').exists()
            local=any(root.glob('**/*historical*odds*.json')) or any(root.glob('data/**/*odds*.json'))
            status='PHYSICALLY_AVAILABLE' if adapter and local else 'BLOCKED_EXTERNAL' if adapter else 'DOCUMENTATION_ONLY'
        else:
            lname=name.lower()
            if 'football-data' in lname or 'football_data' in sid:
                local=any(root.glob('data/raw/**/*football*data*.csv')) or any(root.glob('data/canonical/*football*.csv'))
            elif 'statsbomb' in lname:
                local=any(root.glob('data/**/*statsbomb*'))
            else:
                local=False
            status='PHYSICALLY_AVAILABLE' if local else 'BLOCKED_EXTERNAL'
        out.append({'source_id':sid,'source':name,'api':s.get('url'),'historical_access':s.get('historical') or s.get('capabilities'), 'auth_required':s.get('auth'),'local_data_available':local,'status':status})
    return out
