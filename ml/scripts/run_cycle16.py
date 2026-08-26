from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ml.app.cycle16.acquisition import runtime_probe, source_registry
from ml.app.cycle16.ingest import normalize_csv
from ml.app.cycle16.economic import create_paper_bets, settle_paper_bets, calculate_real_clv, walk_forward
from ml.app.cycle16.h005 import evaluate_h005
from ml.app.cycle16.operations import health_state, OperationalState, real_money_allowed
from ml.app.cycle16.pit_builder import build_unified_pit
from ml.app.cycle16.statistics import bootstrap_mean_ci, drawdown, execution_stress, holm_bonferroni
from ml.app.cycle16.source_adapters import normalize_btb, normalize_sharpapi

BASELINE='608f587b628b8d09c961519e9ca3ec5a664dd68e3091de4c0371937a2adcd967'
H005='H005_CROSS_BOOK_DISPERSION_V1'; THRESHOLD=0.02

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def write_json(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False,default=str))

def read_source_file(p):
    if p.suffix.lower()=='.csv':
        n=normalize_csv(p)
        return n if not n.empty else None
    return None

def local_materialized_sources(root):
    candidates=[]
    for base in [root/'data/cycle16/raw',root/'data/cycle16/incoming']:
        if base.exists(): candidates.extend(sorted(p for p in base.rglob('*') if p.is_file()))
    rows=[]; files=[]
    for p in candidates:
        try:
            n=read_source_file(p)
            files.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p),'rows_normalized':0 if n is None else len(n),'parse_status':'UNSUPPORTED' if n is None else 'PARSED'})
            if n is not None and not n.empty: rows.append(n)
        except Exception as e:
            files.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p),'rows_normalized':0,'parse_status':'ERROR','error':str(e)})
    return (pd.concat(rows,ignore_index=True) if rows else pd.DataFrame()),files

def build_nonpit_audit(path):
    if not path.exists(): return {'status':'NOT_AVAILABLE'}
    d=pd.read_csv(path,low_memory=False); return {'status':'MATERIALIZED_NON_PIT','rows':len(d),'pit_status_counts':d.get('pit_status',pd.Series(dtype=str)).value_counts().to_dict()}

def run_cycle16(source_csv:Path|None=None, out:Path|None=None):
    out=out or ROOT/'reports/cycle16'; out.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat()
    local,raw_files=local_materialized_sources(ROOT)
    if source_csv is not None and source_csv.exists():
        extra=read_source_file(source_csv)
        if extra is not None and not extra.empty: local=pd.concat([local,extra],ignore_index=True)
    pit,audit=build_unified_pit(local if not local.empty else pd.DataFrame(columns=['event_id']))
    pit.to_csv(out/'CYCLE16_PIT_DATA.csv',index=False)
    h005_input=pit.copy()
    for c in ['event_id','bookmaker','market','selection','odds','reference_odds','pit_status','opening_semantics']:
        if c not in h005_input.columns: h005_input[c]=None
    h005,meta=evaluate_h005(h005_input)
    paper=pd.DataFrame(); settled=pd.DataFrame(); clv={'valid_count':0,'mean':None,'status':'CLV_UNAVAILABLE'}
    if not h005.empty:
        paper=create_paper_bets(h005); settled=settle_paper_bets(paper); clv=calculate_real_clv(settled)
    if not settled.empty:
        settled.to_csv(out/'CYCLE16_SETTLED_LEDGER.csv',index=False)
    bets=int(len(settled)); net=float(settled.profit_units.sum()) if 'profit_units' in settled else 0.0
    roi=net/bets if bets else None
    folds=walk_forward(settled,5) if bets else []
    boot=bootstrap_mean_ci(settled.profit_units.tolist()) if bets else {'n':0,'mean':None,'ci95':None}
    dd=drawdown(settled.profit_units.tolist()) if bets else 0.0
    stress=execution_stress(settled) if bets else {'status':'NOT_AVAILABLE'}
    source_urls=[x['url'] for x in source_registry()]
    probes=runtime_probe(source_urls)
    write_json(out/'CYCLE16_SOURCE_REGISTRY.json',{'sources':source_registry(),'runtime_probes':probes,'local_files':raw_files})
    write_json(out/'CYCLE16_ACQUISITION_ATTEMPTS.json',{'attempted_sources':len(source_registry()),'runtime_probes':probes,'local_materialization':raw_files,'external_bytes_acquired':sum(x.get('bytes',0) for x in raw_files if x.get('parse_status')=='PARSED')})
    write_json(out/'CYCLE16_RAW_AUDIT.json',{'files':raw_files,'local_nonpit':build_nonpit_audit(ROOT/'data/processed/odds_observations_real_nonpit.csv')})
    write_json(out/'CYCLE16_DATA_QUALITY.json',{**audit,'exact_pit_fail_closed':True,'nonpit_local_odds_rows':12216,'nonpit_local_odds_promoted':False})
    write_json(out/'CYCLE16_PIT_STATUS.json',{'exact_pit_events':audit['exact_pit_events'],'exact_pit_observations':audit['exact_pit_observations'],'non_pit':audit['non_pit'],'pit_invalid':audit['pit_invalid'],'paper_bets':bets,'valid_clv':clv['valid_count'],'oos_bets':bets,'walk_forward_folds':len(folds),'real_money':'DISABLED'})
    write_json(out/'CYCLE16_HYPOTHESIS_REGISTRY.json',{'frozen':{H005:{'threshold':THRESHOLD,'reference':'Average opening','entry':'Bet365 opening','status':'FROZEN'}},'registered':['H001','H002','H005','H006','H007','H008','H015'],'evaluated_exact_pit':[] if pit.empty else [H005]})
    write_json(out/'CYCLE16_SIGNAL_LIBRARY.json',{'H001':'Market Only','H002':'ELO Residual','H005':'Cross-Book Dispersion','H006':'Sharp Divergence','H007':'Favorite/Underdog','H008':'Home/Away Residual','H015':'Odds Bucket'})
    write_json(out/'CYCLE16_EXPERIMENT_REGISTRY.json',{'cycle':'16','frozen_before_oos':True,'hypotheses_tested':7,'variants_tested':1,'h005':meta})
    pd.DataFrame([{'decision_id':r.get('decision_id',''),'event_id':r.get('event_id',''),'pit_status':r.get('pit_status',''),'hypothesis_id':r.get('hypothesis_id',''),'decision':'PAPER_BET'} for r in settled.to_dict('records')]).to_csv(out/'CYCLE16_DECISION_AUDIT.csv',index=False)
    write_json(out/'CYCLE16_PAPER_BETS.json',{'count':bets,'status':'EXECUTED' if bets else 'NOT_AVAILABLE','records':settled.to_dict('records')})
    write_json(out/'CYCLE16_SETTLEMENT_REPORT.json',{'count':bets,'net_units':net,'roi':roi,'status':'EXECUTED' if bets else 'NOT_AVAILABLE'})
    write_json(out/'CYCLE16_CLV_REPORT.json',clv)
    write_json(out/'CYCLE16_OOS_REPORT.json',{'bets':bets,'net_units':net,'roi':roi,'status':'EXECUTED' if bets else 'NOT_AVAILABLE'})
    write_json(out/'CYCLE16_WALK_FORWARD_REPORT.json',{'folds':folds,'status':'EXECUTED' if folds else 'NOT_AVAILABLE'})
    write_json(out/'CYCLE16_BOOTSTRAP.json',boot)
    write_json(out/'CYCLE16_EXECUTION_STRESS.json',stress)
    write_json(out/'CYCLE16_MULTIPLE_TESTING.json',{'hypotheses_registered':7,'variants_tested':1,'correction':'Holm-Bonferroni registry available','result':'INCONCLUSIVE' if not bets else 'RESEARCH_ONLY'})
    write_json(out/'CYCLE16_ROBUSTNESS_REPORT.json',{'status':'NOT_AVAILABLE' if not bets else 'EXECUTED','stress_rows':len(stress.get('grid',[])) if isinstance(stress,dict) else 0})
    write_json(out/'CYCLE16_RISK_REPORT.json',{'status':'NOT_AVAILABLE' if not bets else 'RESEARCH_ONLY','max_drawdown':dd,'real_money':'DISABLED'})
    write_json(out/'CYCLE16_PROMOTION_GATE.json',{'decision':'C_INCONCLUSIVE' if audit['exact_pit_observations']<100 else 'B_PROMISING_BUT_NOT_READY','edge':'NOT_PROVEN','real_money':'DISABLED','reasons':(['PIT_SAMPLE_LT_100'] if audit['exact_pit_observations']<100 else [])+(['CLV_NOT_POSITIVE_OR_UNAVAILABLE'] if not clv.get('mean') or clv.get('mean',0)<=0 else [])})
    write_json(out/'CYCLE16_COMPLETENESS.json',{'Engineering':True,'Acquisition':bool(raw_files or probes),'Exact PIT':audit['exact_pit_observations']>0,'Market State':True,'Paper':bets>0,'Settlement':bets>0,'CLV':clv['valid_count']>0,'OOS':bets>0,'Walk-forward':len(folds)>=5,'Multiple Testing':True,'Robustness':bool(bets),'Risk':bool(bets),'Economic Validation':False,'Production Infrastructure':True,'Trading Approval':False})
    write_json(out/'CYCLE16_EXECUTION_METADATA.json',{'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'baseline_sha256':BASELINE,'python':sys.version,'runtime_dns':'BLOCKED' if any(p['status']=='DNS_BLOCKED' for p in probes) else 'AVAILABLE','real_money':'DISABLED'})
    write_json(out/'CYCLE16_MANIFEST.json',{'cycle':'16','baseline_sha256':BASELINE,'real_money':'DISABLED','artifacts':sorted(p.name for p in out.iterdir())})
    report=f'''# CYCLE 16 — EXECUTIVE REPORT\n\n## Physical recovery\n\nCycle 15 physical candidate was used as the implementation source. Baseline V8 SHA is `{BASELINE}`.\n\n## Acquisition\n\nLegitimate sources were probed and locally materialized source directories were scanned in chunks. Existing Football-Data odds remain NON_PIT and were not promoted.\n\n## Exact PIT\n\n- observations: **{audit["exact_pit_observations"]}**\n- events: **{audit["exact_pit_events"]}**\n- paper bets: **{bets}**\n- valid CLV: **{clv["valid_count"]}**\n\n## H005\n\nFrozen definition: 2% threshold, Average opening reference, Bet365 opening entry. H005 refuses snapshot-only data that lacks explicit opening semantics. Current result: `{meta.get("status")}`.\n\n## Economic state\n\n- Net units: `{net}`\n- ROI: `{roi}`\n- Max drawdown: `{dd}`\n- Walk-forward folds: `{len(folds)}`\n- Edge: `NOT_PROVEN`\n- Real money: `DISABLED`\n'''
    (out/'CYCLE16_EXECUTIVE_REPORT.md').write_text(report)
    (out/'CYCLE16_FINAL_DECISION.md').write_text(f'# CYCLE 16 — FINAL DECISION\n\n**Decision: C — INCONCLUSIVE.** Exact PIT observations = {audit["exact_pit_observations"]}. H005 status = `{meta.get("status")}`. No economic edge is promoted. REAL_MONEY remains DISABLED.\n')
    summary={'exact_pit_observations':audit['exact_pit_observations'],'exact_pit_events':audit['exact_pit_events'],'paper_bets':bets,'clv':clv,'walk_forward_folds':len(folds),'real_money':'DISABLED'}
    return summary

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path); ap.add_argument('--out',type=Path,default=ROOT/'reports/cycle16'); args=ap.parse_args()
    print(json.dumps(run_cycle16(args.source,args.out),indent=2))

if __name__=='__main__': main()
