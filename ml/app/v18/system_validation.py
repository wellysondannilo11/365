from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path

def run(cmd,cwd):
    try:
        p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=180)
        return {'status':'PASS' if p.returncode==0 else 'FAIL','returncode':p.returncode,'stdout':p.stdout[-5000:],'stderr':p.stderr[-5000:]}
    except subprocess.TimeoutExpired as exc:
        return {'status':'FAIL','returncode':124,'stdout':str(exc.stdout)[-5000:] if exc.stdout else '','stderr':'TIMEOUT'}

def available(cmd): return shutil.which(cmd) is not None

def validate(root='.'):
    root=str(Path(root).resolve()); out=[]
    out.append({'component':'Python compileall',**run([sys.executable,'-m','compileall','-q','ml','scripts','tests'],root)})
    out.append({'component':'Python full test suite',**run([sys.executable,'-m','pytest','-q'],root)})
    out.append({'component':'V16 self test',**run([sys.executable,'scripts/self_test.py'],root)})
    if available('node'):
        out.append({'component':'Frontend node syntax/runtime tests',**run(['npm','test','--','--test-reporter=spec'],str(Path(root)/'frontend'))})
    else: out.append({'component':'Frontend node tests','status':'NOT AVAILABLE','reason':'node unavailable'})
    if available('mvn'): out.append({'component':'Backend Maven tests',**run(['mvn','clean','test'],str(Path(root)/'backend'))})
    else: out.append({'component':'Backend Maven tests','status':'NOT AVAILABLE','reason':'maven unavailable'})
    if available('docker'):
        out.append({'component':'Docker compose config',**run(['docker','compose','config'],root)})
    else: out.append({'component':'Docker','status':'NOT AVAILABLE','reason':'docker unavailable'})
    return out

def save(results,path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(results,indent=2),encoding='utf-8')
