from __future__ import annotations
import hashlib, json, os, platform, subprocess, sys
from pathlib import Path

def _git_hash(root='.'):
    try:return subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:return 'NOT_AVAILABLE'

def manifest(*,dataset_hash,feature_hash=None,config=None,seed=42,model_version=None,calibrator_version=None,root='.'):
    cfg_hash=hashlib.sha256(json.dumps(config or {},sort_keys=True,default=str).encode()).hexdigest()
    return {'python_version':platform.python_version(),'platform':platform.platform(),'dataset_hash':dataset_hash,'feature_hash':feature_hash,'config_hash':cfg_hash,'code_hash':_git_hash(root),'random_seed':seed,'model_version':model_version,'calibrator_version':calibrator_version}

def save(path, payload):
    Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8');return path
