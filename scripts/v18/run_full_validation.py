from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'ml'))
from app.v18.system_validation import validate, save
results=validate(ROOT)
out=ROOT/'reports/v18/V18_FULL_SYSTEM_VALIDATION.json'; save(results,out)
print(json.dumps(results,indent=2))
print('saved',out)
