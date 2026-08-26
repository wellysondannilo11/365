from __future__ import annotations
import os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'ml'))
from app.v18.acquisition import network_probe, acquire_football_data, write_manifest, SourceAttempt

raw=ROOT/'data/raw/v18'
net=network_probe()
attempts=[]
# Public secondary source: useful for real result/odds acquisition, but never promoted to strict PIT betting evidence.
if net['status']=='PASS':
    attempts += acquire_football_data(['2324','2425','2526'], ['E0'], raw)
else:
    attempts.append(SourceAttempt('Football-Data.co.uk','B/C','historical results/stats/pre-closing+closing odds','NOT_EXECUTED',net['reason'],net['started_at'],net['ended_at']))
# A-class source requires explicit key and is queried only by the dedicated adapter once configured.
key=os.getenv('THE_ODDS_API_KEY') or os.getenv('ROBO_ODDS_API_KEY')
if not key:
    attempts.append(SourceAttempt('The Odds API','A','provider timestamped historical bookmaker snapshots','NOT_AVAILABLE','MISSING_CREDENTIAL:THE_ODDS_API_KEY',net['started_at'],net['ended_at']))
else:
    attempts.append(SourceAttempt('The Odds API','A','provider timestamped historical bookmaker snapshots','NOT_EXECUTED','Credential present; historical query requires explicit study configuration and paid quota',net['started_at'],net['ended_at']))
# Other sources are recorded explicitly even when the runtime cannot reach them.
if net['status'] != 'PASS':
    attempts.extend([
        SourceAttempt('Betfair Historical Data','A','timestamped Exchange back/lay/volume','NOT_EXECUTED','NETWORK_UNAVAILABLE_AND_NO_LOCAL_PURCHASED_PACKAGE',net['started_at'],net['ended_at']),
        SourceAttempt('StatsBomb Open Data','C/D','event/lineup football features','NOT_EXECUTED','NETWORK_UNAVAILABLE',net['started_at'],net['ended_at']),
        SourceAttempt('Flashscore','D','complementary context','NOT_AVAILABLE','NO_REPRODUCIBLE_PIT_ENDPOINT; NO_BYPASS_ATTEMPTED',net['started_at'],net['ended_at']),
    ])
write_manifest(ROOT/'data/manifests/V18_ACQUISITION_ATTEMPTS.json',attempts,net)
print('V18 acquisition attempts written:',ROOT/'data/manifests/V18_ACQUISITION_ATTEMPTS.json')
