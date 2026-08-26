import argparse,json
from pathlib import Path
from ml.app.research.replay import decision_hash
p=argparse.ArgumentParser();p.add_argument('snapshot');a=p.parse_args();data=json.loads(Path(a.snapshot).read_text());print(json.dumps({'decision_id':data.get('decision_id'),'replay_hash':decision_hash(data)},indent=2))
