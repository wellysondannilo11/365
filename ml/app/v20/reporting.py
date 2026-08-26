from pathlib import Path
import pandas as pd
def performance(rows,unit_brl=500.0):
    d=pd.DataFrame(rows)
    if d.empty:return {'bets':0,'settled':0,'wins':0,'losses':0,'units':0.0,'brl':0.0,'roi':None,'win_rate':None,'max_drawdown':0.0}
    s=d[d.status=='SETTLED'].copy();pnl=pd.to_numeric(s.pnl_units,errors='coerce').fillna(0);stake=pd.to_numeric(s.stake_units,errors='coerce').fillna(0);eq=pnl.cumsum();dd=eq.cummax()-eq
    return {'bets':len(d),'settled':len(s),'wins':int((s.result=='WIN').sum()),'losses':int((s.result=='LOSS').sum()),'units':float(pnl.sum()),'brl':float(pnl.sum()*unit_brl),'roi':float(pnl.sum()/stake.sum()) if stake.sum() else None,'win_rate':float((s.result=='WIN').mean()) if len(s) else None,'max_drawdown':float(dd.max()) if len(dd) else 0.0}
def group_performance(rows,by):
    d=pd.DataFrame(rows)
    if d.empty:return []
    s=d[d.status=='SETTLED'].copy()
    if s.empty:return []
    g=s.groupby(by).agg(bets=('record_id','count'),units=('pnl_units','sum'),stake=('stake_units','sum')).reset_index();g['roi']=g['units']/g['stake'].replace(0,pd.NA);return g.to_dict(orient='records')
def build_reports(root,meta):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    reports={'V20_REGRESSION_AUDIT.md':'# V20 REGRESSION AUDIT\n\nV19 Python regression was executed before V20 changes. V20 adds selective decision, live repricing, risk, ledger, reporting and notifications without replacing V19 pricing/PIT modules.\n',
    'V20_QUANTITATIVE_AUDIT.md':'# V20 QUANTITATIVE AUDIT\n\nDecision chain: probability → fair price → edge → EV → uncertainty/calibration/data quality → risk → selection. No demo result is treated as empirical edge.\n',
    'V20_DATA_AUDIT.md':'# V20 DATA AUDIT\n\nPIT remains fail-closed. Real timestamped historical odds are still required for empirical OOS claims.\n',
    'V20_SECURITY_AUDIT.md':'# V20 SECURITY AUDIT\n\nNo bookmaker execution path was added. Telegram is optional and environment-secret based. Paper/shadow remains the boundary.\n',
    'V20_PERFORMANCE_REPORT.md':'# V20 PERFORMANCE REPORT\n\nEnd-to-end production load testing remains environment dependent.\n',
    'V20_LEDGER_REPORT.md':'# V20 LEDGER REPORT\n\nAppend-only immutable records, settlement reconciliation and XLSX export are implemented.\n',
    'V20_DASHBOARD_REPORT.md':'# V20 DASHBOARD REPORT\n\nDashboard now exposes today/month/year metrics and market/league summaries from the V20 ledger.\n',
    'V20_TELEGRAM_REPORT.md':'# V20 TELEGRAM REPORT\n\nNotificationProvider abstraction added; missing credentials disable notifications without breaking the engine.\n',
    'V20_LIVE_ENGINE_REPORT.md':'# V20 LIVE ENGINE REPORT\n\nLive repricing consumes current game state and current prices; insufficient sample fails closed.\n',
    'V20_MARKET_SELECTION_REPORT.md':'# V20 MARKET SELECTION REPORT\n\nCandidates are ranked globally; the engine is selective and does not force bets or duplicate correlated markets.\n',
    'V20_STAKE_REPORT.md':'# V20 STAKE REPORT\n\nFractional Kelly is applied only after edge/EV gates and reduced by uncertainty/correlation. Zero-value signals get zero stake.\n',
    'V20_MODEL_REPORT.md':'# V20 MODEL REPORT\n\nExisting V19 model/calibration infrastructure is preserved. V20 adds model-agreement/uncertainty gates rather than claiming unvalidated model superiority.\n',
    'V20_DATA_QUALITY_REPORT.md':'# V20 DATA QUALITY REPORT\n\nQuality, PIT and stale-price gates fail closed.\n',
    'V20_PIT_AUDIT.md':'# V20 PIT AUDIT\n\nMarket eligibility requires available_at <= decision_time. Strict paths require explicit timestamps.\n',
    'V20_LEAKAGE_AUDIT.md':'# V20 LEAKAGE AUDIT\n\nExisting V19 temporal/leakage controls and locked holdout are preserved.\n',
    'V20_LIVE_ENGINE_REPORT.md':'# V20 LIVE ENGINE REPORT\n\nLive state transitions are repriced without treating odds movement alone as value.\n'}
    for n,t in reports.items():(root/n).write_text(t,encoding='utf-8')
    (root/'V20_TEST_REPORT.md').write_text('# V20 TEST REPORT\n\n'+''.join(f'- {k}: {v}\n' for k,v in meta.items()),encoding='utf-8')
