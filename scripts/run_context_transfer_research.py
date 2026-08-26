from pathlib import Path
import json, math, sys
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from ml.app.master_staff.context_transfer import load, build_team_rows, build_coverage, feature_transferability

OUTD=ROOT/'data/context_transfer'; OUTR=ROOT/'reports/context_transfer'; OUTD.mkdir(exist_ok=True); OUTR.mkdir(exist_ok=True)

def multiclass_brier(y, p, classes):
    yy=np.zeros_like(p)
    for i,v in enumerate(y): yy[i, list(classes).index(v)]=1
    return float(np.mean(np.sum((p-yy)**2,axis=1)))

def main():
    d=load(); tr=build_team_rows(d)
    h=tr[tr.venue=='HOME'].copy(); a=tr[tr.venue=='AWAY'].copy()
    h=h.rename(columns={c:f'h_{c}' for c in h.columns if c not in ['match_id']})
    a=a.rename(columns={c:f'a_{c}' for c in a.columns if c not in ['match_id']})
    x=h.merge(a,on='match_id',how='inner')
    m=d[['match_id','home_goals','away_goals','kickoff_timestamp','competition']].copy().merge(x,on='match_id',how='inner').sort_values('kickoff_timestamp')
    m['target']=np.where(m.home_goals>m.away_goals,'H',np.where(m.home_goals<m.away_goals,'A','D'))
    m['direct_diff']=m.h_same_comp_gd.fillna(0)-m.a_same_comp_gd.fillna(0)
    m['transfer_diff']=m.h_recent_gd.fillna(0)-m.a_recent_gd.fillna(0)
    m['season_diff']=m.h_season_gd.fillna(0)-m.a_season_gd.fillna(0)
    m['rest_diff']=m.h_days_rest.fillna(0)-m.a_days_rest.fillna(0)
    cut=int(len(m)*0.70); train=m.iloc[:cut]; test=m.iloc[cut:]
    classes=np.array(['A','D','H'])
    rows=[]
    # Frequency baseline
    probs=np.array([(train.target==c).mean() for c in classes]); P=np.tile(probs,(len(test),1))
    rows.append({'modelo':'Frequência histórica','treino':len(train),'teste':len(test),'brier':multiclass_brier(test.target.to_numpy(),P,classes),'log_loss':log_loss(test.target,P,labels=classes),'status':'OOS_DESCRITIVO'})
    for name,cols in [('Direto_competicao',['direct_diff']),('Transferencia_contextual',['direct_diff','transfer_diff','season_diff','rest_diff'])]:
        trn=train.dropna(subset=cols); tst=test.dropna(subset=cols)
        if len(trn)<100 or tst.empty or trn.target.nunique()<3:
            rows.append({'modelo':name,'treino':len(trn),'teste':len(tst),'brier':'INSUFFICIENT_DATA','log_loss':'INSUFFICIENT_DATA','status':'INSUFFICIENT_DATA'})
            continue
        model=LogisticRegression(max_iter=1000).fit(trn[cols],trn.target)
        p=model.predict_proba(tst[cols]); cl=model.classes_
        rows.append({'modelo':name,'treino':len(trn),'teste':len(tst),'brier':multiclass_brier(tst.target.to_numpy(),p,cl),'log_loss':log_loss(tst.target,p,labels=cl),'status':'OOS_DESCRITIVO'})
    comp_transfer=feature_transferability(d,tr)
    comp_status='NOT_VALIDATED'
    if len(comp_transfer)>=100 and comp_transfer.target_competition.nunique()>=2: comp_status='EXPLORATORY'
    comparison=pd.DataFrame(rows); comparison.to_csv(OUTD/'MODEL_COMPARISON.csv',index=False)
    result={'baseline_comparison':rows,'cross_competition_transfer_status':comp_status,'cross_competition_transfer_rows':len(comp_transfer),'scientific_interpretation':'Nenhum ganho é promovido sem validação OOS/walk-forward e amostra suficiente.','real_money':'DISABLED'}
    (OUTD/'MODEL_COMPARISON.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    ab=[]
    configs=[('BASELINE_DIRETO',['direct_diff']),('DIRETO+FORMA',['direct_diff','transfer_diff']),('DIRETO+FORMA+TEMPORADA',['direct_diff','transfer_diff','season_diff']),('DIRETO+FORMA+TEMPORADA+DESCANSO',['direct_diff','transfer_diff','season_diff','rest_diff'])]
    for name,cols in configs:
        trn=train.dropna(subset=cols); tst=test.dropna(subset=cols)
        if len(trn)<100 or tst.empty or trn.target.nunique()<3:
            ab.append({'configuracao':name,'treino':len(trn),'teste':len(tst),'brier':'INSUFFICIENT_DATA','log_loss':'INSUFFICIENT_DATA','status':'INSUFFICIENT_DATA'})
            continue
        model=LogisticRegression(max_iter=1000).fit(trn[cols],trn.target)
        p=model.predict_proba(tst[cols]); cl=model.classes_
        ab.append({'configuracao':name,'treino':len(trn),'teste':len(tst),'brier':multiclass_brier(tst.target.to_numpy(),p,cl),'log_loss':log_loss(tst.target,p,labels=cl),'status':'OOS_DESCRITIVO'})
    pd.DataFrame(ab).to_csv(OUTD/'FEATURE_ABLATION_REPORT.csv',index=False)
    sources=[
      ('The Odds API','GLOBAL','historical_odds',100,100,80,20,'ALTO','PIT histórico timestampado; acesso pago necessário'),
      ('Betfair Historical Data','GLOBAL','exchange_odds',95,90,95,15,'ALTO','mercado de exchange timestampado; compra/acesso necessário'),
      ('TheStatsAPI','GLOBAL','stats_xg_odds',90,85,70,30,'MÉDIO-ALTO','boa amplitude, PIT precisa de POC'),
      ('StatsBomb Open Data','SELECIONADO','events_lineups',80,55,90,0,'ALTO','eventos/escalações; sem odds'),
      ('Football-Data.co.uk','EUROPA+OUTROS','results_stats_odds',85,95,45,0,'ALTO','grande histórico; timestamps de odds não são PIT exato'),
      ('Sportmonks','GLOBAL','fixtures_stats_xg',90,85,70,30,'MÉDIO-ALTO','amplitude ampla; plano/credencial'),
      ('API-Football','GLOBAL','fixtures_stats_odds',85,80,60,25,'MÉDIO','cobertura ampla; validar histórico de odds')]
    pr=pd.DataFrame(sources,columns=['fonte','cobertura','alvo','valor_cientifico','volume','qualidade','custo_acesso','prioridade','motivo'])
    pr['score_prioridade']=(0.30*pr.valor_cientifico+0.25*pr.volume+0.25*pr.qualidade+0.20*(100-pr.custo_acesso)).round(2)
    pr=pr.sort_values('score_prioridade',ascending=False); pr.to_csv(OUTD/'ACQUISITION_PRIORITY.csv',index=False)
    (OUTR/'FEATURE_ABLATION_REPORT.md').write_text('# ABLATION — TRANSFERÊNCIA DE CONTEXTO\n\nA execução temporal separa treino e teste. O resultado é descritivo e não habilita apostas. Features só são promovidas após OOS/walk-forward consistente.\n\nVeja `data/context_transfer/MODEL_COMPARISON.csv`.\n',encoding='utf-8')
    (OUTR/'MODEL_COMPARISON.md').write_text('# COMPARAÇÃO DE MODELOS\n\nAmostra histórica de 4.864 jogos, com divisão temporal 70/30. O modelo de transferência é uma referência de pesquisa para verificar se forma/temporada/descanso carregam informação além do sinal direto da competição.\n\nA transferência entre competições específicas permanece `NOT_VALIDATED` porque apenas 5 clubes materializados aparecem em mais de uma competição no conjunto atual.\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
