from pathlib import Path
import json, hashlib, zipfile, shutil, subprocess, sys
from datetime import datetime
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/real_day_prematch'
DATA=ROOT/'data/real_day_prematch'
for p in (OUT,DATA): p.mkdir(parents=True,exist_ok=True)
now='2026-08-20T13:45:18-03:00'
# Web-confirmed current-day fixture evidence. These are external references, not local materialized datasets.
matches=[
 {'id':'CONMEBOL-SUD-2026-MACARA-SANTOS','date':'2026-08-20','kickoff':'19:00','timezone':'America/Sao_Paulo','competition':'CONMEBOL Sudamericana','stage':'Round of 16','home':'Macará','away':'Santos','status':'FIXTURE','aggregate':'1-2','aggregate_status':'SUPPORTED_BY_MULTIPLE_SOURCES','odds':{'home':3.10,'draw':3.50,'away':2.48},'odds_source':'Oddschecker','odds_pit':'NON_PIT','context':['Macará needs a two-goal win for direct qualification; Santos advances with draw or one-goal win.','Santos reported to rotate/preserve key players; Neymar and Gabigol reported rested, Escobar suspended.','Ambato altitude reported at ~2,580m.'],'sources':['turn3news36','turn3news39','turn3search1']},
 {'id':'CONMEBOL-SUD-2026-OLIMPIA-VASCO','date':'2026-08-20','kickoff':'19:00','timezone':'America/Sao_Paulo','competition':'CONMEBOL Sudamericana','stage':'Round of 16','home':'Olimpia','away':'Vasco','status':'FIXTURE','aggregate':'0-0','aggregate_status':'SUPPORTED','odds':{'home':2.45,'draw':3.30,'away':3.15},'odds_source':'Oddschecker','odds_pit':'NON_PIT','context':['First leg ended 0-0; tie open.','Vasco must win to advance in normal time; draw sends tie to penalties.'],'sources':['turn1news39','turn1search0']},
 {'id':'CONMEBOL-LIB-2026-LDU-MIRASSOL','date':'2026-08-20','kickoff':'19:00','timezone':'America/Sao_Paulo','competition':'CONMEBOL Libertadores','stage':'Round of 16','home':'LDU Quito','away':'Mirassol','status':'FIXTURE','aggregate':'1-1','aggregate_status':'SUPPORTED','odds':{'home':1.70,'draw':3.55,'away':5.25},'odds_source':'Oddschecker','odds_pit':'NON_PIT','context':['First leg ended 1-1; any draw leads to penalties.','Quito altitude reported around 2,850m.','External preview reports LDU 3W/1D/1L in last five and Mirassol 3L/2D.'],'sources':['turn3news38','turn3search5','turn3search9']},
 {'id':'CONMEBOL-LIB-2026-CORINTHIANS-ROSARIO','date':'2026-08-20','kickoff':'21:30','timezone':'America/Sao_Paulo','competition':'CONMEBOL Libertadores','stage':'Round of 16','home':'Corinthians','away':'Rosario Central','status':'FIXTURE','aggregate':'0-0','aggregate_status':'SUPPORTED','odds':{'home':1.90,'draw':3.12,'away':4.80},'odds_source':'Oddschecker','odds_pit':'NON_PIT','context':['First leg ended 0-0; any draw leads to penalties.','External report says Memphis Depay may return; physical condition is a pre-match uncertainty.'],'sources':['turn1news37','turn1search1','turn1search8']},
 {'id':'CONMEBOL-SUD-2026-BOTAFOGO-CIENCIANO','date':'2026-08-20','kickoff':'21:30','timezone':'America/Sao_Paulo','competition':'CONMEBOL Sudamericana','stage':'Round of 16','home':'Botafogo','away':'Cienciano','status':'FIXTURE','aggregate':'UNKNOWN','aggregate_status':'SOURCE_CONFLICT','odds':{'home':1.27,'draw':8.50,'away':23.0},'odds_source':'Oddschecker','odds_pit':'NON_PIT','context':['Multiple current sources report first leg Cienciano 6-1 Botafogo; Botafogo would need six-goal win for direct qualification and five to force penalties.','Official CONMEBOL fixture page currently displays aggregate 0-0, creating a source conflict.','Do not use aggregate as a model feature until conflict is resolved.'],'sources':['turn3news37','turn3news40','turn2search1','turn2search3']}
]
# These were listed as 20 Aug in a broad agenda but had already kicked off before the decision timestamp in Brazil.
completed=[
 {'id':'CONMEBOL-SUD-2026-TORQUE-TIGRE','home':'Torque','away':'Tigre','kickoff':'00:30','status':'COMPLETED_BEFORE_DECISION','source':'turn2search9'},
 {'id':'CONMEBOL-SUD-2026-SANTA-FE-RIVER','home':'Santa Fe','away':'River Plate','kickoff':'00:30','status':'COMPLETED_BEFORE_DECISION','source':'turn2search9'}
]
# Market implied probabilities only; no model probability is fabricated.
for m in matches:
    o=m['odds']; s=sum(1/v for v in o.values()); m['market_implied_raw']={k:round(1/v,6) for k,v in o.items()}; m['market_vig']=round(s-1,6)
    m['model_probability']='NOT_AVAILABLE'
    m['fair_odds']='NOT_AVAILABLE'; m['edge']='NOT_AVAILABLE'; m['EV']='NOT_AVAILABLE'
    m['scientific_status']='INSUFFICIENT_DATA'
    m['experimental_signal']='CONTEXT_ONLY'
    m['decision']='WAIT'
    m['reason']='Current package has no materialized PIT-valid odds and the historical model feature coverage does not contain sufficient current-team observations for an honest model probability.'

snapshot={
 'prediction_timestamp':now,'decision_timestamp':now,'date':'2026-08-20','timezone':'America/Sao_Paulo',
 'input_zip':'ROBO_DA_BET_MASTER_STAFF_VALUE_PRICING_COMPLETE.zip','input_sha256':'71c475b3e5d12a99ea8826f82464127420342042ae741531e5b7fa2a1e685c3d',
 'historical_matches_before':4864,'today_fixture_discovery_total':7,'future_matches_at_decision':5,
 'completed_before_decision':2,'predictions_created':5,'model_probability_available':0,'experimental_signals':5,'value_bets':0,'paper_candidates':0,'watches':0,'no_bets':0,'insufficient_data':5,
 'real_money':'DISABLED','matches':matches,'completed_before_decision':completed,
 'immutability':'This snapshot is an append-only prospective record. No post-kickoff result is included.'
}
(DATA/'REAL_DAY_PREMATCH_SNAPSHOT.json').write_text(json.dumps(snapshot,indent=2,ensure_ascii=False),encoding='utf-8')
rows=[]
for m in matches:
    for sel,o in [('HOME',m['odds']['home']),('DRAW',m['odds']['draw']),('AWAY',m['odds']['away'])]:
        rows.append({'match_id':m['id'],'home':m['home'],'away':m['away'],'market':'1X2','selection':sel,'market_odds':o,'market_implied_probability':1/o,'model_probability':'NOT_AVAILABLE','fair_odds':'NOT_AVAILABLE','edge':'NOT_AVAILABLE','EV':'NOT_AVAILABLE','pit_status':m['odds_pit'],'decision':'WAIT','scientific_status':m['scientific_status']})
pd.DataFrame(rows).to_csv(DATA/'REAL_DAY_MARKET_ANALYSIS.csv',index=False)
pd.DataFrame([{'match_id':m['id'],'home':m['home'],'away':m['away'],'context':'; '.join(m['context']),'data_quality':'PARTIAL_EXTERNAL_REFERENCE','model_features_available':'INSUFFICIENT','lineup_status':'EXTERNAL_REFERENCE_ONLY','injury_status':'EXTERNAL_REFERENCE_ONLY','aggregate_status':m['aggregate_status'],'rivalry':'UNKNOWN','h2h':'NOT_MATERIALIZED_CURRENTLY','rest':'NOT_MATERIALIZED_CURRENTLY'} for m in matches]).to_csv(DATA/'REAL_DAY_FEATURES.csv',index=False)
pd.DataFrame([{'match_id':m['id'],'fixture_evidence':'WEB_REFERENCE','odds_evidence':'WEB_REFERENCE_NON_PIT','model_data':'INSUFFICIENT','pit_status':m['odds_pit'],'source_conflict':m['aggregate_status']=='SOURCE_CONFLICT','overall':'INSUFFICIENT_DATA'} for m in matches]).to_csv(DATA/'REAL_DAY_DATA_QUALITY.csv',index=False)
prov=[]
for m in matches: prov.append({'match_id':m['id'],'sources':m['sources'],'retrieval_state':'FOUND_ONLY','downloaded':False,'materialized':False,'processed':False,'pit_validated':False})
(DATA/'REAL_DAY_PROVENANCE.json').write_text(json.dumps({'retrieval_timestamp':now,'state':'FOUND_ONLY','records':prov},indent=2,ensure_ascii=False),encoding='utf-8')
# top signals are contextual, explicitly not model value bets.
top=[
 ('Macará x Santos','CONTEXTO_AGREGADO + DESFALQUES','Santos has aggregate advantage, but key-player rotation/suspension changes the uncertainty materially.'),
 ('LDU Quito x Mirassol','ALTITUDE + AGREGADO_ABERTO','LDU has home/altitude context and tie is level; external form signal exists but is not materialized in the local model.'),
 ('Botafogo x Cienciano','AGREGADO_EXTREMO + SOURCE_CONFLICT','Reported 6-1 first leg creates a strong contextual scenario, but official fixture data conflicts and blocks scientific promotion.'),
 ('Corinthians x Rosario Central','AGREGADO_ABERTO + MANDO','0-0 first leg; home side priced shorter, but current-team model coverage is insufficient.'),
 ('Olimpia x Vasco','AGREGADO_ABERTO','0-0 first leg; both qualification paths remain open, but no validated model probability is available.')]
(OUT/'REAL_DAY_TOP_SIGNALS.md').write_text('# TOP SINAIS EXPERIMENTAIS — 20/08/2026\n\nEstes sinais são contextuais e **não são VALUE_BET**.\n\n'+''.join(f'## {i+1}. {a}\n{b}\n{c}\n\n' for i,(a,b,c) in enumerate(top)),encoding='utf-8')
md=['# REAL-DAY PREMATCH PILOT — 20/08/2026','',f'- Entrada: `ROBO_DA_BET_MASTER_STAFF_VALUE_PRICING_COMPLETE.zip`',f'- SHA-256 entrada: `71c475b3e5d12a99ea8826f82464127420342042ae741531e5b7fa2a1e685c3d`',f'- Decision timestamp: `{now}`', '- Jogos futuros analisáveis no momento da decisão: **5**', '- Jogos encontrados na agenda do dia: **7** (2 já haviam começado antes da decisão)', '', '## Regra científica', 'Nenhum jogo recebeu probabilidade do modelo quando a massa local não sustentava uma previsão honesta. Odds web foram tratadas como referência `NON_PIT`, não como prova de value.', '', '## Jogos']
for m in matches:
    md += [f"### {m['home']} x {m['away']}",f"- Competição: {m['competition']}",f"- Horário: {m['kickoff']} BRT",f"- Agregado: {m['aggregate']} ({m['aggregate_status']})",f"- Odds de referência: {m['odds']}",f"- PIT: {m['odds_pit']}",f"- Probabilidade do modelo: NOT_AVAILABLE",f"- Fair odds: NOT_AVAILABLE",f"- Edge/EV: NOT_AVAILABLE",f"- Decisão: WAIT / INSUFFICIENT_DATA",f"- Sinal experimental: CONTEXT_ONLY",f"- Motivo: {m['reason']}",""]
md += ['## Conclusão','', '`VALUE_BETS=0`', '', '`EXPERIMENTAL_SIGNALS=5`', '', '`REAL_MONEY=DISABLED`', '', 'A amostra prospectiva foi registrada antes do início dos cinco jogos ainda futuros. Nenhum resultado posterior foi usado para alterar este snapshot.']
(OUT/'REAL_DAY_PREMATCH_REPORT.md').write_text('\n'.join(md),encoding='utf-8')
(OUT/'REAL_DAY_LIMITATIONS.md').write_text('''# Limitações\n\n- A base local possui 4.864 partidas, mas não contém observações suficientes para todos os clubes da rodada.\n- Odds atuais encontradas na web não possuem timestamp PIT confiável para esta execução; portanto são `NON_PIT`/referência.\n- Não há xG, shots, SOT, players, injuries, suspensions ou lineups materializados no pacote.\n- O site oficial da CONMEBOL apresentou conflito de agregado para Botafogo x Cienciano em relação a múltiplas fontes atuais; o agregado foi bloqueado para uso científico.\n- Os sinais experimentais são contextuais, não probabilidades produzidas pelo modelo.\n''',encoding='utf-8')
# Preserve existing files and add only pilot artifacts + script.
# Tests against the current package.
checks=[]
for name,cmd in [('pytest',[sys.executable,'-m','pytest','-q']),('compileall',[sys.executable,'-m','compileall','-q','.']),('self_test',[sys.executable,'scripts/self_test.py'])]:
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True); checks.append({'test':name,'returncode':p.returncode,'status':'PASS' if p.returncode==0 else 'FAIL','stdout_tail':p.stdout[-2000:],'stderr_tail':p.stderr[-1000:]})
# unzip integrity after final packaging will be done after zip.
summary={'INPUT_ZIP':'ROBO_DA_BET_MASTER_STAFF_VALUE_PRICING_COMPLETE.zip','INPUT_SHA256':'71c475b3e5d12a99ea8826f82464127420342042ae741531e5b7fa2a1e685c3d','HISTORICAL_MATCHES':4864,'TODAY_MATCHES_FOUND':7,'TODAY_MATCHES_ANALYZED':5,'MARKETS_ANALYZED':15,'PREDICTIONS_CREATED':5,'EXPERIMENTAL_SIGNALS':5,'VALUE_BETS':0,'PAPER_CANDIDATES':0,'WATCHES':0,'NO_BETS':0,'INSUFFICIENT_DATA':5,'SCIENTIFIC_STATUS':'EDGE_NOT_DETERMINED','DATA_STATUS':'PRESERVED','ACQUISITION_STATUS':'WEB_REFERENCE_ONLY; NO_LOCAL_MATERIALIZATION','PIT_STATUS':'NON_PIT','MODEL_STATUS':'INSUFFICIENT_CURRENT_TEAM_COVERAGE','MARKET_STATUS':'REFERENCE_ONLY','PREDICTION_STATUS':'PROSPECTIVE_SNAPSHOT_CREATED','EXPERIMENTAL_SIGNAL_STATUS':'CONTEXT_ONLY','VALUE_BET_STATUS':'0; BLOCKED_BY_QUALITY_GATE','REAL_MONEY_STATUS':'DISABLED','TESTS':checks}
(OUT/'REAL_DAY_EXECUTION_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(summary,indent=2,ensure_ascii=False))
