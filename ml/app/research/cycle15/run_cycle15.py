from __future__ import annotations
import json, hashlib, shutil
from pathlib import Path
import pandas as pd, numpy as np
from .pit import classify_observation
from .sources import source_registry, raw_sha256
from .h005 import evaluate_h005
from .production import promotion_gate

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'reports/cycle15'; DATA=ROOT/'data/cycle15'; INCOMING=DATA/'incoming'; RAW=DATA/'raw'
for p in (OUT,DATA,INCOMING,RAW): p.mkdir(parents=True,exist_ok=True)

BASELINE='608f587b628b8d09c961519e9ca3ec5a664dd68e3091de4c0371937a2adcd967'

def write_json(name,obj):
    p=OUT/name; p.write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str)); return p

def sha(path):
    h=hashlib.sha256();
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def exact_pit_from_incoming():
    rows=[]
    for p in INCOMING.glob('*.csv'):
        try:
            df=pd.read_csv(p)
        except Exception: continue
        cols={c.lower() for c in df.columns}
        if {'event_id','timestamp','event_start_time','sportsbook','market_type','selection','odds_decimal'} <= cols:
            from .sources import normalize_sharpapi
            n=normalize_sharpapi(df)
        elif {'id','odds_datetime','bookmaker','bettype','team1','team2','date','odds'} <= cols:
            from .sources import normalize_btb
            n=normalize_btb(df)
        else: continue
        n['decision_timestamp']=n['provider_timestamp']
        n['provenance']='file:'+p.name
        n['raw_hash']=sha(p)
        for r in n.to_dict('records'):
            # For a provider snapshot, decision at snapshot is admissible; downstream users can choose a later decision.
            rows.append(r)
    out=[]
    for r in rows:
        out.append({**r,**classify_observation(r).__dict__})
    return pd.DataFrame(out)

def _bootstrap(values, n=2000, seed=15):
    if len(values)<2: return None
    rng=np.random.default_rng(seed); means=rng.choice(values,size=(n,len(values)),replace=True).mean(axis=1)
    return [float(np.quantile(means,.025)),float(np.quantile(means,.975))]

def _walk_forward(d, folds=5):
    if len(d)<folds: return []
    x=d.sort_values('event_id').reset_index(drop=True); out=[]
    for i,part in enumerate(np.array_split(x,folds),1):
        net=float(part.profit_units.sum()); out.append({'fold':i,'bets':int(len(part)),'net_units':net,'roi':net/len(part)})
    return out

def nonpit_h005():
    p=ROOT/'data/processed/odds_observations_real_nonpit.csv'
    if not p.exists(): return {'status':'NO_LOCAL_DATA'}
    od=pd.read_csv(p); canon=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv',low_memory=False)[['match_id','home_goals','away_goals']]
    op=od[(od.market=='1X2')&(od.snapshot_type=='OPENING')].copy(); cl=od[(od.market=='1X2')&(od.snapshot_type=='CLOSING')].copy()
    b=op[op.bookmaker=='Bet365'].set_index('match_id'); a=op[op.bookmaker=='Average'].set_index('match_id'); bc=cl[cl.bookmaker=='Bet365'].set_index('match_id')
    rows=[]
    for mid in b.index.intersection(a.index):
        if mid not in bc.index: continue
        rr=canon[canon.match_id==mid]
        if rr.empty: continue
        hg,ag=rr.iloc[0].home_goals,rr.iloc[0].away_goals; result='home' if hg>ag else 'away' if ag>hg else 'draw'
        for sel,col in [('home','selection_home'),('draw','selection_draw'),('away','selection_away')]:
            bo,ro,co=b.loc[mid,col],a.loc[mid,col],bc.loc[mid,col]
            if pd.notna(bo) and pd.notna(ro) and pd.notna(co) and bo/ro-1>=.02:
                rows.append({'event_id':mid,'selection':sel,'entry_odds':float(bo),'reference_odds':float(ro),'closing_odds':float(co),'result':result,'profit_units':float(bo-1 if sel==result else -1),'clv_proxy':float(bo/co-1)})
    d=pd.DataFrame(rows)
    if d.empty: return {'status':'NO_ELIGIBLE_NONPIT'}
    d.to_csv(DATA/'CYCLE15_NONPIT_H005_RESEARCH.csv',index=False)
    net=float(d.profit_units.sum()); roi=net/len(d); clv=float(d.clv_proxy.mean())
    return {'status':'NON_PIT_RESEARCH_ONLY','hypothesis_id':'H005_CROSS_BOOK_DISPERSION_V1','frozen_threshold':0.02,'bets':int(len(d)),'events':int(d.event_id.nunique()),'net_units':net,'roi':roi,'clv_proxy_mean':clv,'max_drawdown':float(max(0,(-d.profit_units.cumsum()).max())),'bootstrap_ci95':_bootstrap(d.profit_units.to_numpy()) ,'walk_forward':_walk_forward(d)}

def main():
    exact=exact_pit_from_incoming()
    if exact.empty:
        exact=pd.DataFrame(columns=['event_id','pit_status','observation_id','provider_timestamp','decision_timestamp','kickoff_timestamp'])
    exact.to_csv(DATA/'CYCLE15_PIT_DATA.csv',index=False)
    status_counts=exact['pit_status'].value_counts().to_dict() if 'pit_status' in exact else {}
    exact_events=int(exact.loc[exact.pit_status=='EXACT_PIT','event_id'].nunique()) if not exact.empty else 0
    exact_obs=int((exact.pit_status=='EXACT_PIT').sum()) if not exact.empty else 0
    nonpit=nonpit_h005()
    artifacts={
      'CYCLE15_MANIFEST.json':{'cycle':'15','baseline_sha256':BASELINE,'candidate_archive_sha256':'5b864b50be953fe873b85cf08ed062b482f2efdc511732e2258fb3badb9933be','real_money':'DISABLED'},
      'CYCLE15_EXECUTION_METADATA.json':{'python':__import__('sys').version,'runner':'ml.app.research.cycle15.run_cycle15','network_status':'BLOCKED_DNS_IN_RUNTIME'},
      'CYCLE15_SOURCE_REGISTRY.json':source_registry(),
      'CYCLE15_PIT_STATUS.json':{'exact_pit_events':exact_events,'exact_pit_observations':exact_obs,'status_counts':status_counts,'real_paper_bets':0,'valid_clv':0},
      'CYCLE15_RAW_AUDIT.json':{'incoming_files':[{ 'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in INCOMING.glob('*') if p.is_file()]},
      'CYCLE15_DATA_QUALITY.json':{'exact_pit_gate':'FAIL_CLOSED','nonpit_local_odds_rows':12216,'exact_pit_promoted':exact_obs},
      'CYCLE15_SIGNAL_LIBRARY.json':{'hypotheses':['H001','H002','H003','H004','H005','H006','H007','H008','H009','H010']},
      'CYCLE15_HYPOTHESIS_REGISTRY.json':{'H005':{'status':'FROZEN','threshold':0.02,'rationale':'cross-book price dislocation'}},
      'CYCLE15_EXPERIMENT_REGISTRY.json':{'discovery':'temporal','confirmation':'temporal','oos':'temporal','selection_rule':'frozen H005 >= 2%'},
      'CYCLE15_DECISION_AUDIT.csv':[],
      'CYCLE15_PAPER_BETS.json':{'real_pit_bets':0,'status':'NO_ELIGIBLE_EXACT_PIT'},
      'CYCLE15_SETTLEMENT_REPORT.json':{'settlements':0,'status':'NO_REAL_PIT_BETS'},
      'CYCLE15_CLV_REPORT.json':{'valid_clv':0,'clv_proxy':nonpit.get('clv_proxy_mean') if isinstance(nonpit,dict) else None,'proxy_status':'NON_PIT_ONLY'},
      'CYCLE15_OOS_REPORT.json':{'exact_pit_oos_bets':0,'nonpit_research':nonpit},
      'CYCLE15_WALK_FORWARD_REPORT.json':{'exact_pit_folds':0,'status':'BLOCKED_BY_EXACT_PIT_SAMPLE','nonpit_research_folds':len(nonpit.get('walk_forward',[])) if isinstance(nonpit,dict) else 0,'nonpit_research':nonpit.get('walk_forward') if isinstance(nonpit,dict) else []},
      'CYCLE15_MULTIPLE_TESTING.json':{'hypotheses_registered':10,'validated':0,'promoted':0},
      'CYCLE15_BOOTSTRAP.json':{'exact_pit':None,'status':'INSUFFICIENT_EXACT_PIT','nonpit_h005_ci95':nonpit.get('bootstrap_ci95') if isinstance(nonpit,dict) else None},
      'CYCLE15_ROBUSTNESS_REPORT.json':{'exact_pit':'BLOCKED_BY_SAMPLE','nonpit_h005':'RESEARCH_ONLY'},
      'CYCLE15_EXECUTION_STRESS.json':{'status':'NOT_APPLICABLE_WITHOUT_EXACT_PIT_EXECUTION_TIMESTAMPS'},
      'CYCLE15_RISK_REPORT.json':{'status':'NO_PROMOTION','real_money':'DISABLED'},
      'CYCLE15_PROMOTION_GATE.json':promotion_gate({'pit_events':exact_events,'oos_bets':0,'clv_mean':0,'walk_forward_folds':0,'robustness':'BLOCKED'}),
      'CYCLE15_COMPLETENESS.json':{'code_implemented':True,'exact_pit_data_materialized':exact_obs>0,'economic_edge_proven':False,'real_money':'DISABLED'},
    }
    for n,o in artifacts.items():
        if n.endswith('.csv'):
            pd.DataFrame(o).to_csv(OUT/n,index=False)
        else: write_json(n,o)
    write_json('CYCLE15_SOURCE_REGISTRY.json',source_registry())
    report=f'''# CYCLE 15 — EXECUTIVE REPORT\n\n## Engineering\n\n- Candidate used: V16 Cycle 4 physical archive.\n- Candidate SHA-256: `5b864b50be953fe873b85cf08ed062b482f2efdc511732e2258fb3badb9933be`.\n- V8 baseline preserved: `{BASELINE}`.\n- Exact-PIT contract, SharpAPI/BeatTheBookie adapters, H005 evaluator, prospective collector and production lock implemented.\n\n## Economic evidence\n\n- Exact PIT events: **{exact_events}**\n- Exact PIT observations: **{exact_obs}**\n- Real paper bets: **0**\n- Valid CLV: **0**\n- Edge: **NOT_PROVEN**\n\nThe local 12,216 historical odds rows remain NON_PIT. A separate research-only H005 run is recorded without promotion.\n\n## H005 research-only\n\n{json.dumps(nonpit,indent=2)}\n\nThese figures are **NON_PIT_RESEARCH_ONLY** and do not count as economic validation.\n\n## Acquisition\n\nThe runtime cannot resolve external DNS, so provider-native bytes could not be downloaded. The system now has explicit adapters for SharpAPI point-in-time snapshots and the BeatTheBookie odds-series format, plus a fail-closed prospective collector. SharpAPI's public dataset documents 6,132 World Cup rows captured at a provider timestamp across 20 sources, while BeatTheBookie documents continuous odds series with `odds_datetime`; both are recorded as legitimate ingestion routes, not as locally materialized evidence.\n\n## Decision\n\n`EDGE = NOT_PROVEN`\n`REAL_MONEY = DISABLED`\n`PRODUCTION_TRADING_APPROVED = FALSE`\n'''
    (OUT/'CYCLE15_EXECUTIVE_REPORT.md').write_text(report)
    (OUT/'CYCLE15_FINAL_DECISION.md').write_text('# CYCLE 15 — FINAL DECISION\n\n**INCONCLUSIVE / EDGE NOT PROVEN.** Exact-PIT promotion remained fail-closed because no new provider-native snapshot bytes were materialized in the runtime. The cycle materially improved the ingestion/economic code path and preserved a segregated NON_PIT H005 research result. Real money remains disabled.\n')
    print(json.dumps({'exact_pit_events':exact_events,'exact_pit_observations':exact_obs,'nonpit_h005':nonpit},indent=2))

if __name__=='__main__': main()
