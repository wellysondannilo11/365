from pathlib import Path
import re,json
root=Path('.')
patterns=[re.compile(r'(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*["\'](?!CHANGE_ME|$)[^"\']{12,}["\']')]
findings=[]
for p in root.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in ['.git','node_modules','__pycache__']): continue
    try:s=p.read_text(errors='ignore')
    except:continue
    for i,line in enumerate(s.splitlines(),1):
        if any(rx.search(line) for rx in patterns): findings.append({'file':str(p),'line':i,'text':'REDACTED'})
out={'status':'PASS' if not findings else 'FAIL','findings':findings,'env_example_present':Path('.env.example').exists()}
Path('reports/v19/V19_SECURITY_SCAN.json').parent.mkdir(parents=True,exist_ok=True)
Path('reports/v19/V19_SECURITY_SCAN.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
if findings: raise SystemExit(1)
