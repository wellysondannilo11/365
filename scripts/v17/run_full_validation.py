from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import json
from ml.app.v17.system_validation import validate
root=ROOT
result=validate(root)
out=root/'reports/v17/V17_FULL_SYSTEM_VALIDATION.json'; out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
for r in result: print(r['component'], r['status'])
