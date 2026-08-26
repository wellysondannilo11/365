from __future__ import annotations
from datetime import datetime, timezone
import hashlib, json, os
from sqlalchemy import create_engine, text
try:
    import redis
except Exception: redis=None
class V22Persistence:
    def __init__(self,url=None,redis_url=None):
        self.url=url or os.getenv('DATABASE_URL',''); self.engine=create_engine(self.url,pool_pre_ping=True) if self.url else None
        ru=redis_url or os.getenv('REDIS_URL',''); self.redis=redis.from_url(ru,decode_responses=True) if (ru and redis) else None
    @property
    def configured(self): return self.engine is not None
    def _write(self,sql,params):
        if not self.engine:return False
        with self.engine.begin() as c:c.execute(text(sql),params)
        return True
    def record_event(self,event_id,captured_at,payload,source='unknown',sequence=None):
        raw=json.dumps(payload,sort_keys=True,separators=(',',':'),default=str); h=hashlib.sha256(raw.encode()).hexdigest()
        return self._write('INSERT INTO v22_events(event_id,event_time,captured_at,source,sequence,payload_hash,payload) VALUES (:event_id,:event_time,:captured_at,:source,:sequence,:hash,:payload) ON CONFLICT DO NOTHING',{'event_id':str(event_id),'event_time':payload.get('commence_time'),'captured_at':captured_at,'source':source,'sequence':sequence,'hash':h,'payload':json.dumps(payload,default=str)})
    def record_odds(self,row):
        return self._write('INSERT INTO v22_odds_snapshots(event_id,bookmaker,market,selection,line,price,captured_at,source_timestamp,available_at,source,raw_hash) VALUES (:event_id,:bookmaker,:market,:selection,:line,:price,:captured_at,:source_timestamp,:available_at,:source,:raw_hash) ON CONFLICT DO NOTHING',row)
    def record_trace(self,trace):
        return self._write('INSERT INTO v22_decision_trace(trace_id,event_id,decision,why,created_at,model_version,feature_version,pricing_version,config_version,data_snapshot_id,pit_status,inputs,outputs,reasons) VALUES (:trace_id,:event_id,:decision,:why,:created_at,:model_version,:feature_version,:pricing_version,:config_version,:data_snapshot_id,:pit_status,:inputs,:outputs,:reasons) ON CONFLICT DO NOTHING',{**trace,'inputs':json.dumps(trace.get('inputs',{}),default=str),'outputs':json.dumps(trace.get('outputs',{}),default=str),'reasons':json.dumps(trace.get('reasons',[]))})
    def record_dataset(self,row):
        rid=row.get('row_hash') or hashlib.sha256(json.dumps(row,sort_keys=True,default=str).encode()).hexdigest()
        return self._write('INSERT INTO v22_dataset_rows(row_id,event_id,decision,mode,decision_time,outcome,row_hash,payload,created_at) VALUES (:row_id,:event_id,:decision,:mode,:decision_time,:outcome,:row_hash,:payload,:created_at) ON CONFLICT DO NOTHING',{'row_id':rid,'event_id':row.get('event_id'),'decision':row.get('decision'),'mode':row.get('mode'),'decision_time':row.get('decision_time'),'outcome':row.get('result'),'row_hash':rid,'payload':json.dumps(row,default=str),'created_at':row.get('created_at',datetime.now(timezone.utc))})
    def cache_health(self):
        if not self.redis:return {'configured':False,'status':'NOT_CONFIGURED'}
        try:self.redis.setex('robo:v23:heartbeat',30,datetime.now(timezone.utc).isoformat()); return {'configured':True,'status':'ONLINE'}
        except Exception as e:return {'configured':True,'status':'OFFLINE','error':type(e).__name__}
    def health(self):
        if not self.engine: db={'configured':False,'status':'NOT_CONFIGURED'}
        else:
            try:
                with self.engine.connect() as c:c.execute(text('SELECT 1')); db={'configured':True,'status':'ONLINE'}
            except Exception as e: db={'configured':True,'status':'OFFLINE','error':type(e).__name__}
        return {'postgres':db,'redis':self.cache_health()}
