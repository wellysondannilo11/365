from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def run(cmd, cwd=ROOT, timeout=180):
    try:
        p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=timeout)
        return {'status':'PASS' if p.returncode==0 else 'FAIL','returncode':p.returncode,'stdout':p.stdout[-5000:],'stderr':p.stderr[-5000:]}
    except subprocess.TimeoutExpired as e:
        return {'status':'FAIL','returncode':124,'stdout':str(e.stdout or '')[-5000:],'stderr':'TIMEOUT'}


def available(cmd): return shutil.which(cmd) is not None


def main():
    results=[]
    results.append({'component':'Python compileall',**run([sys.executable,'-m','compileall','-q','ml','scripts','tests'])})
    results.append({'component':'Python full test suite',**run([sys.executable,'-m','pytest','-q'])})
    results.append({'component':'V16 self-test',**run([sys.executable,'scripts/self_test.py'])})
    if Path('scripts/v19/security_scan.py').exists():
        results.append({'component':'V19 security scan',**run([sys.executable,'scripts/v19/security_scan.py'])})
    else:
        results.append({'component':'V19 security scan','status':'NOT EXECUTED','reason':'script not present'})
    if available('node'):
        results.append({'component':'Frontend npm test',**run(['npm','test','--','--test-reporter=spec'],ROOT/'frontend')})
        results.append({'component':'Frontend production build',**run(['npm','run','build'],ROOT/'frontend')})
    else:
        results.extend([{'component':'Frontend npm test','status':'NOT AVAILABLE','reason':'node unavailable'},{'component':'Frontend production build','status':'NOT AVAILABLE','reason':'node unavailable'}])
    if available('mvn'):
        results.append({'component':'Backend Maven tests',**run(['mvn','clean','test'],ROOT/'backend')})
        results.append({'component':'Backend Maven package',**run(['mvn','package','-DskipTests'],ROOT/'backend')})
    else:
        results.extend([{'component':'Backend Maven tests','status':'NOT AVAILABLE','reason':'maven unavailable'},{'component':'Backend Maven package','status':'NOT AVAILABLE','reason':'maven unavailable'}])
    if available('docker'):
        results.append({'component':'Docker compose config',**run(['docker','compose','config'])})
        results.append({'component':'Docker compose build',**run(['docker','compose','build'],timeout=600)})
    else:
        results.extend([{'component':'Docker compose config','status':'NOT AVAILABLE','reason':'docker unavailable'},{'component':'Docker compose build','status':'NOT AVAILABLE','reason':'docker unavailable'}])
    Path('reports/v19/V19_FULL_SYSTEM_VALIDATION.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps(results,indent=2))

if __name__=='__main__': main()
