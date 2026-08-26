import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKER=ROOT/'scripts/global/data_acquisition_worker.py'
MATERIALIZER=ROOT/'scripts/global/local_materializer.py'

def test_local_worker_download_checksum_and_resume(tmp_path):
    src=tmp_path/'source.csv'; src.write_text('Date,HomeTeam,AwayTeam,FTHG,FTAG\n2026-01-01,A,B,1,0\n',encoding='utf-8')
    cfg=tmp_path/'cfg.json'; man=tmp_path/'manifest.json'; raw=tmp_path/'raw'
    cfg.write_text(json.dumps({'raw_root':str(raw),'manifest':str(man),'sources':[]}),encoding='utf-8')
    cmd=[sys.executable,str(WORKER),'--config',str(cfg),'--path',str(src),'--name','a.csv']
    subprocess.run(cmd,check=True,capture_output=True,text=True)
    first=json.loads(man.read_text())['execution_log'][-1]
    assert first['downloaded'] and first['accessible'] and first['state']=='CHECKSUM_VALIDATED'
    digest=hashlib.sha256((raw/'a.csv').read_bytes()).hexdigest(); assert digest==first['raw_file_hash']
    subprocess.run(cmd,check=True,capture_output=True,text=True)
    second=json.loads(man.read_text())['execution_log'][-1]
    assert second.get('reused_existing') is True

def test_materializer_promotes_only_valid_schema(tmp_path):
    # Exercise materializer through the existing project manifest using a known local football-data artifact.
    artifact=ROOT/'data/raw/global_acquisition/football_data/2122_E0.csv'
    assert artifact.exists()
    subprocess.run([sys.executable,str(WORKER),'--path',str(artifact),'--name','pytest_2122_E0.csv'],check=True,capture_output=True,text=True)
    subprocess.run([sys.executable,str(MATERIALIZER)],check=True,capture_output=True,text=True)
    man=json.loads((ROOT/'data/global_dataset/registry/DATA_ACQUISITION_MANIFEST.json').read_text())
    rec=[r for r in man['execution_log'] if r.get('artifact')=='pytest_2122_E0.csv'][-1]
    assert rec['materialized'] is True and rec['validated'] is True and rec['processed'] is True

def test_remote_failure_is_explicit_not_success():
    cfg=ROOT/'config/data_acquisition_local.json'
    out=subprocess.run([sys.executable,str(WORKER),'--config',str(cfg),'--url','https://invalid.example.invalid/test.csv','--timeout','1','--retries','1'],capture_output=True,text=True)
    assert out.returncode==0
    payload=json.loads(out.stdout)
    assert payload[-1]['state'] in {'BLOCKED','FAILED'}
