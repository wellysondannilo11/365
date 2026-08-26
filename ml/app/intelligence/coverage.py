from __future__ import annotations
from pathlib import Path
import csv

# Registry is a coverage plan, not evidence. A row only becomes empirical after bytes are materialized and validated.
GROUPS={
'Brazil':['Brasileirão Série A','Brasileirão Série B','Brasileirão Série C','Brasileirão Série D','Copa do Brasil','Copa do Nordeste','Copa Verde','Paulista','Paulista Série A2','Paulista Série A3','Paulista Série A4','Carioca','Carioca A2','Carioca A3','Mineiro','Mineiro Módulo II','Gaúcho','Gaúcho Série A2','Paranaense','Paranaense 2ª divisão','Pernambucano','Cearense','Baiano','Paraibano','Alagoano','Potiguar','Sergipano','Catarinense','Goiano','Mato-Grossense','Paraense','Maranhense','Piauiense'],
'South America':['Argentina Primera División','Argentina Primera Nacional','Argentina Primera B Metropolitana','Argentina Primera C','Chile Primera División','Chile Primera B','Colombia Primera A','Colombia Primera B','Uruguay Primera División','Uruguay Segunda División','Paraguay Primera División','Paraguay División Intermedia','Ecuador LigaPro','Ecuador Serie B','Peru Liga 1','Peru Liga 2','Bolivia Primera División','Venezuela Primera División'],
'North/Central America':['MLS','USL','MLS Next Pro','Liga MX','Liga de Expansión','Costa Rica Primera División','Guatemala Liga Nacional','Honduras Liga Nacional','El Salvador Primera División','Panama Liga LPF'],
'Europe':['Premier League','Championship','League One','League Two','National League','Bundesliga','2. Bundesliga','3. Liga','La Liga','Segunda División','Primera Federación','Primera División RFEF','Serie A','Serie B','Serie C','Ligue 1','Ligue 2','National','Primeira Liga','Liga Portugal 2','Liga 3','Campeonato de Portugal','Eredivisie','Belgian Pro League','Scottish Premiership','Turkey Süper Lig','Greece Super League','Austria Bundesliga','Swiss Super League','Denmark Superliga','Sweden Allsvenskan','Norway Eliteserien','Finland Veikkausliiga','Poland Ekstraklasa','Czech First League','Slovakia Niké Liga','Croatia HNL','Serbia SuperLiga','Romania Liga I','Bulgaria First League','Hungary NB I','Slovenia PrvaLiga','Ireland Premier Division','Northern Ireland Premiership','Iceland Besta deild','Ukraine Premier League','Russia Premier League'],
'Asia':['Japan J1','Japan J2','Japan J3','K League 1','K League 2','China Super League','A-League','Saudi Pro League','Saudi First Division','UAE Pro League','Qatar Stars League','Thailand League 1','Indonesia Liga 1','Malaysia Super League','India Super League'],
'Africa':['South Africa Premiership','Egypt Premier League','Morocco Botola','Tunisia Ligue 1','Algeria Ligue 1','Nigeria NPFL'],
'Oceania':['A-League','New Zealand National League'],
'International':['Libertadores','Sudamericana','Champions League','Europa League','Conference League','Club World Cup','Copa America','Euro','World Cup','World Cup Qualifiers','Nations League']}

def build_global_coverage(out_csv:Path):
    out_csv.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    for region, comps in GROUPS.items():
        for comp in comps:
            rows.append({'region':region,'competition':comp,'coverage_plan':'TARGET','materialized':False,'processed':False,'pit_validated':False,'used_in_model':False,'odds_coverage':'UNKNOWN','live_coverage':'UNKNOWN','xg_coverage':'UNKNOWN','cards_coverage':'UNKNOWN','corners_coverage':'UNKNOWN'})
    with out_csv.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return rows
