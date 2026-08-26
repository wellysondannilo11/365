from __future__ import annotations
import json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'ml'))
from app.v18.acquisition import network_probe, acquire_football_data, write_manifest, SourceAttempt

raw=ROOT/'data/raw/v19'; raw.mkdir(parents=True, exist_ok=True)
net=network_probe(); attempts=[]
if net['status']=='PASS':
    attempts += acquire_football_data(['2324','2425','2526'], ['E0'], raw)
else:
    attempts.append(SourceAttempt('Football-Data.co.uk','B/C','historical results/stats/pre-closing+closing odds','NOT_EXECUTED',net['reason'],net['started_at'],net['ended_at']))
key=os.getenv('THE_ODDS_API_KEY') or os.getenv('ROBO_ODDS_API_KEY')
if not key:
    attempts.append(SourceAttempt('The Odds API','A','provider timestamped historical bookmaker snapshots','NOT_AVAILABLE','MISSING_CREDENTIAL:THE_ODDS_API_KEY',net['started_at'],net['ended_at']))
else:
    attempts.append(SourceAttempt('The Odds API','A','provider timestamped historical bookmaker snapshots','NOT_EXECUTED','Historical endpoint requires explicit configured study/entitlement; no fabricated query performed',net['started_at'],net['ended_at']))
if net['status']!='PASS':
    attempts.extend([
        SourceAttempt('Betfair Historical Data','A','timestamped Exchange back/lay/volume','NOT_EXECUTED','NETWORK_UNAVAILABLE_AND_NO_LOCAL_PURCHASED_PACKAGE',net['started_at'],net['ended_at']),
        SourceAttempt('StatsBomb Open Data','C/D','event/lineup football features','NOT_EXECUTED','NETWORK_UNAVAILABLE',net['started_at'],net['ended_at']),
    ])
manifest={'version':'V19','acquisition':True,'network_probe':net,'attempts':[a.__dict__ for a in attempts], 'fail_closed_policy':'No NON-PIT odds may enter strict scientific betting evaluation.'}
path=ROOT/'data/manifests/V19_ACQUISITION_ATTEMPTS.json'; path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
