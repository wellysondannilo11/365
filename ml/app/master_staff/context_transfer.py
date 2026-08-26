from __future__ import annotations
import json, math, re, unicodedata
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/'data'; REPORTS=ROOT/'reports'; MS=DATA/'master_staff'
OUTD=DATA/'context_transfer'; OUTR=REPORTS/'context_transfer'; OUTD.mkdir(parents=True,exist_ok=True); OUTR.mkdir(parents=True,exist_ok=True)

CONFIG={
 'version':'context-transfer-1.0',
 'same_competition_weight':1.00,
 'same_season_other_comp_weight':0.85,
 'recent_form_weight':0.95,
 'prior_season_weight':0.60,
 'older_season_base_weight':0.40,
 'season_decay':0.70,
 'competition_tiers':{
   'Premier League':3,'Bundesliga':3,'Serie A':3,'Championship':2,'League One':1,'League Two':1,
   'Copa Libertadores':3,'Copa Sudamericana':2
 },
 'coverage_thresholds':{'historical_depth':[0,5,10,20], 'recency':[0,3,5,10], 'home_away':[0,2,5,10], 'competition':[0,1,2,4], 'statistical':[0,0.25,0.5,0.75], 'market':[0,0.25,0.5,0.75]},
 'confidence_rules':{
   'sample_cap':40,
   'transfer_penalty_max':0.35,
   'unknown_context_penalty':0.15,
   'market_penalty':0.10
 },
 'status':'RESEARCH_CONFIGURATION_NOT_VALIDATED_FOR_BETTING'
}


def norm(s):
    s='' if pd.isna(s) else str(s)
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode('ascii').lower()
    s=re.sub(r'[^a-z0-9]+',' ',s).strip()
    return s

def team_id(s): return norm(s)

def load():
    p=DATA/'canonical'/'football_historical_real_canonical.csv'
    d=pd.read_csv(p)
    d['kickoff_timestamp']=pd.to_datetime(d['kickoff_timestamp'],errors='coerce',utc=True,format='mixed')
    d['gender']=(d['gender'] if 'gender' in d.columns else pd.Series('MEN', index=d.index)).fillna('MEN').astype(str).str.upper()
    d=d[d.gender.eq('MEN')].copy().sort_values(['kickoff_timestamp','match_id']).reset_index(drop=True)
    d['home_id']=d.home_team.map(team_id); d['away_id']=d.away_team.map(team_id)
    d['season_s']=d.season.astype(str)
    d['comp_tier']=d.competition.map(CONFIG['competition_tiers']).fillna(1)
    return d

def outcome_stats(df):
    # aggregate team-level observations, all strictly prior to each match row
    state=defaultdict(lambda:{'n':0,'gf':0.,'ga':0.,'pts':0.,'home_n':0,'away_n':0,'home_gd':0.,'away_gd':0.})
    out=[]
    for r in df.itertuples():
        rows=[]
        for side,team,opp,gf,ga in [('home',r.home_id,r.away_id,r.home_goals,r.away_goals),('away',r.away_id,r.home_id,r.away_goals,r.home_goals)]:
            s=state[team]
            n=s['n']; pts=s['pts']; gf0=s['gf']; ga0=s['ga']
            rows.append((team, {'n':n,'gf':gf0,'ga':ga0,'pts':pts,'home_n':s['home_n'],'away_n':s['away_n'],'home_gd':s['home_gd'],'away_gd':s['away_gd']}))
        out.append(rows)
        if pd.notna(r.home_goals) and pd.notna(r.away_goals):
            for side,team,gf,ga in [('home',r.home_id,r.home_goals,r.away_goals),('away',r.away_id,r.away_goals,r.home_goals)]:
                s=state[team]; s['n']+=1; s['gf']+=float(gf); s['ga']+=float(ga); s['pts']+=3 if gf>ga else 1 if gf==ga else 0
                if side=='home': s['home_n']+=1; s['home_gd']+=float(gf-ga)
                else: s['away_n']+=1; s['away_gd']+=float(gf-ga)
    return out

def build_team_rows(d):
    # historical team rows with only past information at each kickoff
    state=defaultdict(lambda:[]); last=defaultdict(lambda:None); recent=defaultdict(list)
    comp_counts=defaultdict(lambda:defaultdict(int)); season_counts=defaultdict(lambda:defaultdict(int)); all_counts=defaultdict(int)
    rows=[]
    for r in d.itertuples():
        for side,team,opp,gf,ga in [('home',r.home_id,r.away_id,r.home_goals,r.away_goals),('away',r.away_id,r.home_id,r.away_goals,r.home_goals)]:
            prior=state[team]
            same_comp=[x for x in prior if x['competition']==r.competition]
            same_season=[x for x in prior if x['season']==r.season_s]
            same_season_other=[x for x in same_season if x['competition']!=r.competition]
            rec=prior[-20:]
            home_hist=[x for x in prior if x['venue']=='HOME']
            away_hist=[x for x in prior if x['venue']=='AWAY']
            days=(r.kickoff_timestamp-last[team]).total_seconds()/86400 if last[team] is not None and pd.notna(r.kickoff_timestamp) else np.nan
            def rate(xs):
                if not xs:return np.nan
                return float(np.mean([x['points'] for x in xs]))
            rows.append({
              'match_id':r.match_id,'kickoff_timestamp':r.kickoff_timestamp,'team_id':team,'team_name':r.home_team if side=='home' else r.away_team,
              'opponent_id':opp,'competition':r.competition,'season':r.season_s,'venue':side.upper(),
              'same_comp_n':len(same_comp),'same_season_n':len(same_season),'same_season_other_comp_n':len(same_season_other),'recent20_n':len(rec),
              'home_n':len(home_hist),'away_n':len(away_hist),'days_rest':days,
              'raw_form3':rate(rec[-3:]),'raw_form5':rate(rec[-5:]),'raw_form10':rate(rec[-10:]),'raw_form20':rate(rec[-20:]),
              'same_comp_gd':float(np.mean([x['gd'] for x in same_comp])) if same_comp else np.nan,
              'season_gd':float(np.mean([x['gd'] for x in same_season])) if same_season else np.nan,
              'recent_gd':float(np.mean([x['gd'] for x in rec])) if rec else np.nan,
              'current_comp_tier':int(r.comp_tier)
            })
        # update states after both rows
        for side,team,opp,gf,ga in [('home',r.home_id,r.away_id,r.home_goals,r.away_goals),('away',r.away_id,r.home_id,r.away_goals,r.home_goals)]:
            if pd.notna(gf) and pd.notna(ga):
                points=3 if gf>ga else 1 if gf==ga else 0
                state[team].append({'competition':r.competition,'season':r.season_s,'venue':'HOME' if side=='home' else 'AWAY','gf':float(gf),'ga':float(ga),'gd':float(gf-ga),'points':points,'opp':opp,'kickoff':r.kickoff_timestamp})
                last[team]=r.kickoff_timestamp
    return pd.DataFrame(rows)

def opponent_strength(d):
    # pre-match opponent rating from prior results only. Rating = points/game + goal diff/game, shrunk to 0.
    team_state=defaultdict(list); rows=[]
    for r in d.itertuples():
        def strength(team):
            x=team_state[team]
            if not x:return np.nan
            n=len(x); p=np.mean([z['points'] for z in x]); gd=np.mean([z['gd'] for z in x])
            return float(p + 0.25*gd)
        hs=strength(r.home_id); aws=strength(r.away_id)
        # opponent's prior strength
        home_opp_strength=strength(r.away_id); away_opp_strength=strength(r.home_id)
        rows.append({'match_id':r.match_id,'home_opponent_strength':home_opp_strength,'away_opponent_strength':away_opp_strength,'home_team_strength':hs,'away_team_strength':aws})
        for side,team,gf,ga in [('home',r.home_id,r.home_goals,r.away_goals),('away',r.away_id,r.away_goals,r.home_goals)]:
            if pd.notna(gf) and pd.notna(ga):
                team_state[team].append({'points':3 if gf>ga else 1 if gf==ga else 0,'gd':float(gf-ga)})
    return pd.DataFrame(rows)

def coverage_class(x):
    if x<20:return 'CRITICAL'
    if x<40:return 'LOW'
    if x<60:return 'MODERATE'
    if x<80:return 'GOOD'
    return 'EXCELLENT'

def component_score(n, kind):
    if kind=='stat': return min(1.0,n/4)
    if kind=='market': return min(1.0,n/10)
    if kind=='comp': return min(1.0,n/4)
    if kind=='homeaway': return min(1.0,n/10)
    return min(1.0,n/10)

def build_coverage(d, team_rows):
    rows=[]
    for t, g in team_rows.groupby('team_id'):
        n=len(g); recent=g[g.kickoff_timestamp>=g.kickoff_timestamp.max()-pd.Timedelta(days=180)] if len(g) else g
        comps=g.competition.nunique(); seasons=g.season.nunique(); home=(g.venue=='HOME').sum(); away=(g.venue=='AWAY').sum()
        # statistical availability from underlying team matches, using any non-null match stats.
        raw=d[(d.home_id==t)|(d.away_id==t)]
        stat_cols=[c for c in ['home_goals','away_goals','home_cards','home_corners','home_xg'] if c in raw]
        stat_cov=float(raw[stat_cols].notna().mean().mean()) if len(raw) and stat_cols else 0.0
        market_cov=float(raw[['odds_1','odds_x','odds_2']].notna().any(axis=1).mean()) if len(raw) else 0.0
        direct=min(1,n/10); rec=min(1,len(recent)/5); ha=min(1,min(home,away)/5); comp=component_score(comps,'comp')
        score=100*np.mean([direct,rec,ha,comp,stat_cov,market_cov])
        rows.append({'team_id':t,'team':g.team_name.iloc[-1],'historical_matches':n,'recent_180d_matches':len(recent),'home_matches':home,'away_matches':away,'competitions':comps,'seasons':seasons,'statistical_coverage':round(stat_cov,4),'market_coverage':round(market_cov,4),'team_coverage_score':round(score,2),'coverage_class':coverage_class(score)})
    return pd.DataFrame(rows)

def transfer_weights(row):
    direct=row.same_comp_n
    same=row.same_season_other_comp_n
    rec=row.recent20_n
    prior=max(0,row.same_season_n-row.same_comp_n-same)
    direct_w=CONFIG['same_competition_weight']*min(direct,10)
    same_w=CONFIG['same_season_other_comp_weight']*min(same,15)
    rec_w=CONFIG['recent_form_weight']*min(rec,10)
    prior_w=CONFIG['prior_season_weight']*min(prior,10)
    total=direct_w+same_w+rec_w+prior_w
    if total<=0:return {'direct':0,'transferred':0,'transfer_share':1.0}
    direct_share=direct_w/total
    transferred=1-direct_share
    return {'direct':direct_w,'transferred':total-direct_w,'transfer_share':transferred}

def pilot_transfer(pilot_names, team_rows, coverage, decision='2026-08-20T16:45:00Z'):
    dt=pd.Timestamp(decision)
    wanted={team_id(x):x for x in pilot_names}
    rows=[]
    for tid,name in wanted.items():
        g=team_rows[(team_rows.team_id==tid)&(team_rows.kickoff_timestamp<dt)].copy()
        if g.empty:
            rows.append({'team':name,'team_id':tid,'competition_specific_n':0,'same_season_n':0,'same_season_other_comp_n':0,'recent20_n':0,'transferred_evidence':False,'transfer_share':1.0,'coverage_score':0.0,'coverage_class':'CRITICAL','model_confidence_score':0.0,'analysis_status':'INSUFFICIENT_DATA','reason':'Nenhuma observação histórica materializada para o clube antes da decisão.'})
            continue
        latest=g.iloc[-1]
        tw=transfer_weights(latest)
        cov=coverage[coverage.team_id==tid]
        cs=float(cov.team_coverage_score.iloc[0]) if not cov.empty else 0
        rows.append({'team':name,'team_id':tid,'competition_specific_n':int(latest.same_comp_n),'same_season_n':int(latest.same_season_n),'same_season_other_comp_n':int(latest.same_season_other_comp_n),'recent20_n':int(latest.recent20_n),'transferred_evidence':bool(tw['transfer_share']>0),'transfer_share':round(tw['transfer_share'],4),'coverage_score':cs,'coverage_class':coverage_class(cs),'model_confidence_score':round(max(0,min(100,cs*(1-0.35*tw['transfer_share']))),2),'analysis_status':'ANALYZABLE_WITH_TRANSFERRED_EVIDENCE' if latest.same_season_n>=5 or latest.recent20_n>=5 else 'INSUFFICIENT_DATA','reason':'Evidência transferível da temporada/forma recente disponível; confiança deve ser penalizada.' if latest.same_season_n>=5 or latest.recent20_n>=5 else 'Massa insuficiente mesmo após transferência.'})
    return pd.DataFrame(rows)

def feature_transferability(d, team_rows):
    # Empirical diagnostic: for teams appearing in >=2 competitions, compare season-average goal difference by competition.
    rows=[]
    for t,g in team_rows.groupby('team_id'):
        if g.competition.nunique()<2: continue
        for comp, cg in g.groupby('competition'):
            n=len(cg); other=g[g.competition!=comp]
            if n<5 or len(other)<5: continue
            rows.append({'team_id':t,'target_competition':comp,'target_n':n,'other_comp_n':len(other),'target_mean_gd':cg.recent_gd.mean(),'other_mean_gd':other.recent_gd.mean(),'transfer_gap':abs(cg.recent_gd.mean()-other.recent_gd.mean())})
    out=pd.DataFrame(rows)
    if out.empty:return out
    # smaller gap means more stable transfer, but this is descriptive, not proof of predictive validity.
    out['transferability_class']=pd.cut(out.transfer_gap,[-np.inf,0.5,1.0,np.inf],labels=['HIGH_STABILITY','MODERATE_STABILITY','LOW_STABILITY']).astype(str)
    return out

def ablation(d):
    # Descriptive OOS-safe diagnostics on outcome-independent features. No betting edge.
    rows=[]
    for comp,g in d.groupby('competition'):
        rows.append({'competition':comp,'matches':len(g),'baseline_available':'RESULT_FREQUENCY','form_feature_available':bool(g[['home_goals','away_goals']].notna().all(axis=1).any()),'h2h_available':False,'player_available':False,'injury_available':False,'lineup_available':False,'transfer_model_status':'RESEARCH_ONLY'})
    return pd.DataFrame(rows)


def main():
    d=load(); tr=build_team_rows(d); opp=opponent_strength(d); cov=build_coverage(d,tr)
    pilot=pilot_transfer(['LDU Quito','Mirassol','Olimpia','Vasco','Macará','Santos','Corinthians','Rosario Central','Botafogo','Cienciano'],tr,cov)
    ft=feature_transferability(d,tr)
    tr.to_csv(OUTD/'TEAM_CONTEXT_HISTORY.csv',index=False); cov.to_csv(OUTD/'TEAM_COVERAGE_FINAL.csv',index=False); pilot.to_csv(OUTD/'CONTEXT_TRANSFER_BACKTEST.csv',index=False); ft.to_csv(OUTD/'FEATURE_TRANSFERABILITY.csv',index=False); opp.to_csv(OUTD/'OPPONENT_STRENGTH_HISTORY.csv',index=False)
    pilot_matches=pd.DataFrame([
      {'match_id':'CONMEBOL-SUD-2026-MACARA-SANTOS','home':'Macará','away':'Santos','competition':'CONMEBOL Sudamericana'},
      {'match_id':'CONMEBOL-SUD-2026-OLIMPIA-VASCO','home':'Olimpia','away':'Vasco','competition':'CONMEBOL Sudamericana'},
      {'match_id':'CONMEBOL-SUD-2026-LDU-MIRASSOL','home':'LDU Quito','away':'Mirassol','competition':'CONMEBOL Sudamericana'},
      {'match_id':'CONMEBOL-LIB-2026-CORINTHIANS-ROSARIO','home':'Corinthians','away':'Rosario Central','competition':'CONMEBOL Libertadores'},
      {'match_id':'CONMEBOL-SUD-2026-BOTAFOGO-CIENCIANO','home':'Botafogo','away':'Cienciano','competition':'CONMEBOL Sudamericana'}])
    mp=[]
    for r in pilot_matches.itertuples():
      a=pilot[pilot.team==r.home].iloc[0]; b=pilot[pilot.team==r.away].iloc[0]
      mc=float((a.coverage_score+b.coverage_score)/2); conf=float((a.model_confidence_score+b.model_confidence_score)/2)
      mp.append({'match_id':r.match_id,'home':r.home,'away':r.away,'competition':r.competition,'home_coverage':a.coverage_score,'away_coverage':b.coverage_score,'match_coverage_score':round(mc,2),'model_confidence_score':round(conf,2),'transferred_evidence':bool(a.transferred_evidence or b.transferred_evidence),'analysis_status':'ANALYZABLE_WITH_TRANSFERRED_EVIDENCE' if a.analysis_status=='ANALYZABLE_WITH_TRANSFERRED_EVIDENCE' and b.analysis_status=='ANALYZABLE_WITH_TRANSFERRED_EVIDENCE' else 'INSUFFICIENT_DATA'})
    mp=pd.DataFrame(mp); mp.to_csv(OUTD/'MATCH_COVERAGE_FINAL.csv',index=False)
    cfg=CONFIG.copy(); (OUTD/'TRANSFER_CONFIG.json').write_text(json.dumps(cfg,indent=2,ensure_ascii=False),encoding='utf-8')
    summary={'historical_matches':len(d),'teams':int(pd.concat([d.home_id,d.away_id]).nunique()),'competitions':int(d.competition.nunique()),'seasons':int(d.season_s.nunique()),'pilot_teams':len(pilot),'pilot_analyzable_with_transfer':int((pilot.analysis_status=='ANALYZABLE_WITH_TRANSFERRED_EVIDENCE').sum()),'pilot_insufficient':int((pilot.analysis_status=='INSUFFICIENT_DATA').sum()),'pilot_match_analyzable_with_transfer':int((mp.analysis_status=='ANALYZABLE_WITH_TRANSFERRED_EVIDENCE').sum()),'feature_transfer_rows':len(ft),'status':'RESEARCH_IMPLEMENTED; NO_BETTING_PROMOTION; REAL_MONEY_DISABLED'}
    (OUTD/'CONTEXT_TRANSFER_RESULTS.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    (OUTR/'CONTEXT_TRANSFER_FINAL_REPORT.md').write_text('# CONTEXT TRANSFER — RELATÓRIO FINAL\n\n'+json.dumps(summary,indent=2,ensure_ascii=False)+'\n\nOs pesos estão versionados em `data/context_transfer/TRANSFER_CONFIG.json`. Eles são priors de pesquisa, ainda não validados como vantagem de mercado.\n\nNenhum VALUE_BET foi criado; dinheiro real permanece desabilitado.\n',encoding='utf-8')
    (OUTR/'CONTEXT_TRANSFER_AUDIT.md').write_text('# AUDITORIA DE TRANSFERÊNCIA\n\nSnapshots prospectivos não foram escritos nem alterados. Nenhuma nova partida real foi adicionada. A transferência usa somente observações históricas anteriores ao jogo.\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
