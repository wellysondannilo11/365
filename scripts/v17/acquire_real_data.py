from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import json, os
from ml.app.v17.acquisition import SOURCES, network_probe, attempt_provider, save_manifest
root=ROOT
probe=network_probe()
attempts=[]
attempts.append(attempt_provider('The Odds API','historical football odds','A','https://api.the-odds-api.com/v4/sports/soccer_epl/odds', 'ROBO_ODDS_API_KEY'))
attempts.append(attempt_provider('Betfair Historical Data','exchange historical data','A'))
attempts.append(attempt_provider('Football-Data.co.uk','historical football CSV','B/C','https://www.football-data.co.uk/data.php'))
attempts.append(attempt_provider('StatsBomb Open Data','selected open football data','C/D','https://github.com/statsbomb/open-data'))
attempts.append(attempt_provider('Flashscore','complementary context','D'))
payload={'sources':SOURCES,'network_probe':probe,'attempts':[a.__dict__ for a in attempts], 'credentials_present':{'ROBO_ODDS_API_KEY':bool(os.getenv('ROBO_ODDS_API_KEY'))}}
save_manifest(root/'data/manifests/V17_ACQUISITION_ATTEMPTS.json',payload)
print(json.dumps(payload,indent=2))
