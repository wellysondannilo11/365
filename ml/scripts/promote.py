import json,sys
from pathlib import Path
p=Path('artifacts/registry/challenger.json')
if not p.exists(): raise SystemExit('challenger not found')
d=json.loads(p.read_text())
if d.get('oos_logloss',999)>d.get('max_allowed_logloss',1): raise SystemExit('promotion gate failed: logloss')
if d.get('oos_brier',999)>d.get('max_allowed_brier',.25): raise SystemExit('promotion gate failed: brier')
Path('artifacts/registry/champion.json').write_text(json.dumps({**d,'status':'CHAMPION'},indent=2));print('PROMOTED')
