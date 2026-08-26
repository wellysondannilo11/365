from __future__ import annotations
import json, os, shutil, subprocess, sys
from pathlib import Path

def run(cmd, cwd):
    p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
    return {"status":"PASS" if p.returncode==0 else "FAIL","returncode":p.returncode,"stdout":p.stdout[-4000:],"stderr":p.stderr[-4000:]}

def validate(root='.'): 
    root=str(Path(root).resolve()); out=[]
    out.append({"component":"Python compileall",**run([sys.executable,'-m','compileall','-q','ml/app'],root)})
    out.append({"component":"Python pytest",**run([sys.executable,'-m','pytest','-q'],root)})
    out.append({"component":"V16 self test",**run([sys.executable,'scripts/self_test.py'],root)})
    out.append({"component":"Docker", "status":"NOT AVAILABLE" if not shutil.which('docker') else "NOT EXECUTED"})
    out.append({"component":"Maven", "status":"NOT AVAILABLE" if not shutil.which('mvn') else "NOT EXECUTED"})
    out.append({"component":"Frontend dependencies", "status":"NOT EXECUTED", "reason":"No node_modules vendored; network install must be run in a network-enabled environment"})
    return out
