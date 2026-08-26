from __future__ import annotations
import argparse,json,sys,time,os,signal
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,'ml')
from app.v25.session import V25Session

STATE=Path(os.getenv('V25_OBSERVATION_STATE','artifacts/observation/v25_state.json'))
STOP=Path(os.getenv('V25_OBSERVATION_STOP','artifacts/observation/STOP'))

def write_state(**extra):
    STATE.parent.mkdir(parents=True,exist_ok=True)
    state={'updated_at':datetime.now(timezone.utc).isoformat(),**extra}
    STATE.write_text(json.dumps(state,indent=2,default=str),encoding='utf-8')
    return state

def status():
    if not STATE.exists(): return {'status':'STOPPED','reason':'NO_STATE'}
    try:return json.loads(STATE.read_text(encoding='utf-8'))
    except Exception:return {'status':'UNKNOWN','reason':'INVALID_STATE_FILE'}

def run(mode,interval,iterations):
    STOP.unlink(missing_ok=True)
    s=V25Session()
    if not s.provider.configured:
        write_state(status='BLOCKED',mode=mode,reason='CREDENTIALS_UNAVAILABLE',provider=s.provider.name)
        print(json.dumps({'status':'BLOCKED','reason':'CREDENTIALS_UNAVAILABLE'},indent=2)); return 2
    write_state(status='RUNNING',mode=mode,provider=s.provider.name,session_id=s.session_id,pid=os.getpid(),interval=interval)
    count=0
    try:
        while iterations==0 or count<iterations:
            if STOP.exists():
                write_state(status='STOPPED',mode=mode,session_id=s.session_id,reason='STOP_FILE')
                return 0
            try:
                feed=s.poll(); result=s.scan(feed,mode)
                write_state(status='RUNNING',mode=mode,session_id=s.session_id,provider=s.provider.name,
                            last_health=feed.get('health'),iterations=count+1,observability=result.get('observability'))
                print(json.dumps({'iteration':count+1,'health':feed.get('health'),'selected':len(result.get('selected',[])),'no_bet':result.get('no_bet_count',0)},default=str))
            except Exception as e:
                write_state(status='DEGRADED',mode=mode,session_id=s.session_id,error=type(e).__name__,message=str(e))
                print(json.dumps({'status':'DEGRADED','error':type(e).__name__,'message':str(e)}))
            count+=1
            if iterations==0 or count<iterations: time.sleep(max(1,interval))
    except KeyboardInterrupt:
        write_state(status='STOPPED',mode=mode,session_id=s.session_id,reason='KEYBOARD_INTERRUPT')
        return 0
    write_state(status='STOPPED',mode=mode,session_id=s.session_id,reason='ITERATION_LIMIT')
    return 0

p=argparse.ArgumentParser(description='V25 real-provider PAPER/SHADOW observation runner')
p.add_argument('command',choices=['run','start','stop','status','health'])
p.add_argument('--mode',default='SHADOW',choices=['PAPER','SHADOW'])
p.add_argument('--interval',type=int,default=30)
p.add_argument('--iterations',type=int,default=0,help='0 = continuous')
a=p.parse_args()
if a.command in {'run','start'}: raise SystemExit(run(a.mode,a.interval,a.iterations))
if a.command=='stop':
    STOP.parent.mkdir(parents=True,exist_ok=True); STOP.write_text(datetime.now(timezone.utc).isoformat()); print(json.dumps({'status':'STOP_REQUESTED','state':status()},indent=2)); raise SystemExit(0)
if a.command=='status': print(json.dumps(status(),indent=2,default=str)); raise SystemExit(0)
if a.command=='health':
    s=V25Session(); print(json.dumps({'provider':s.provider.name,'configured':s.provider.configured,'health':s.health.status.value,'status_file':status()},indent=2)); raise SystemExit(0)
