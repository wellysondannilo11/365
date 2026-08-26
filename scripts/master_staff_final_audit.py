from pathlib import Path
import json, hashlib, subprocess, sys, zipfile
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
canon=pd.read_csv(ROOT/'data/canonical/football_historical_real_canonical.csv')
round_df=pd.read_csv(ROOT/'data/processed/round_2026-08-20/ROUND_2026-08-20_INTELLIGENCE.csv')

def nfile(p):
    try:return len(pd.read_csv(p))
    except:return 0
counts={
 'REAL_MATCHES_BEFORE':4864,'REAL_MATCHES_NEW_COMPLETED':0,'REAL_MATCHES_TOTAL':len(canon),
 'NEW_REAL_STRUCTURED_FIXTURE_CONTEXT':len(round_df),'NEW_REAL_ODDS_OBSERVATIONS':int(len(round_df)*3),
 'COUNTRIES':int(canon.country.nunique()),'COMPETITIONS':int(canon.competition.nunique()),'SEASONS':int(canon.season.nunique()),
 'MEN_MATCHES':int((canon['gender'].astype(str).str.upper()=='MEN').sum()) if 'gender' in canon.columns else len(canon),'WOMEN_MATCHES':0,
 'H2H_RECORDS':nfile(ROOT/'data/master_staff/H2H_INTELLIGENCE.csv'),'RIVALRY_RECORDS':nfile(ROOT/'data/master_staff/RIVALRY_REGISTRY.csv'),
 'IMPORTANCE_RECORDS':nfile(ROOT/'data/master_staff/IMPORTANCE_CONTEXT_2026-08-20.csv'),'PLAYER_RECORDS':nfile(ROOT/'data/master_staff/PLAYER_RECORDS.csv'),
 'INJURY_RECORDS':nfile(ROOT/'data/master_staff/INJURY_RECORDS.csv'),'LINEUPS':nfile(ROOT/'data/master_staff/LINEUP_RECORDS.csv'),
 'LIVE_SNAPSHOTS':nfile(ROOT/'data/master_staff/LIVE_SNAPSHOTS.csv'),'SETTLEMENTS':nfile(ROOT/'data/master_staff/SETTLEMENTS.csv'),
 'PAPER_BETS':nfile(ROOT/'data/master_staff/PAPER_DECISIONS.csv'),
 'ODDS_ROWS_CANONICAL':int(canon[['odds_1','odds_x','odds_2']].notna().all(axis=1).sum()),
 'TIMESTAMPED_ODDS_CANONICAL':int(canon.odds_timestamp.notna().sum()),'PIT_VALIDATED_CANONICAL':int(canon.pit_status.astype(str).eq('PIT_VALIDATED').sum()),
 'XG_ROWS':int(canon[['home_xg','away_xg']].notna().all(axis=1).sum()),'CARDS_ROWS':int(canon[['home_cards','away_cards']].notna().all(axis=1).sum()),
 'CORNERS_ROWS':int(canon[['home_corners','away_corners']].notna().all(axis=1).sum()),'REFEREE_ROWS':int(canon.referee.notna().sum()),
 'SHOTS_ROWS':0,'SOT_ROWS':0,'EVENT_ROWS':0,'INJURY_ROWS':0,'SUSPENSION_ROWS':0,
 'ROUND_PIT_EXACT_OR_VALID':int(round_df.market_pit_eligible.sum()),'ROUND_VALUE_BETS':0,'ROUND_PAPER_CANDIDATES':0
}
(ROOT/'DATASET_FINAL_COUNTS.json').write_text(json.dumps(counts,indent=2,ensure_ascii=False))
# Acquisition manifest with strict state separation.
acq={
 'execution':'MASTER_STAFF_2026-08-20',
 'input_zip_sha256':hashlib.sha256((ROOT.parent/'round_work/ROBO_DA_BET_CONMEBOL_ROUND_2026-08-20.zip').read_bytes()).hexdigest() if (ROOT.parent/'round_work/ROBO_DA_BET_CONMEBOL_ROUND_2026-08-20.zip').exists() else 'UNAVAILABLE',
 'network_runtime':'CONTAINER_DNS_BLOCKED_FOR_DIRECT_DOWNLOAD',
 'states':{'FOUND':5,'DOWNLOADED_BYTES':0,'ACQUIRED_BYTES':0,'MATERIALIZED_STRUCTURED_RECORDS':5,'PROCESSED_STRUCTURED_RECORDS':5,'PIT_VALIDATED_EXACT_OR_VALID':0,'USED_IN_MODEL':0},
 'round_structured_sources':[{'home':r.home_team,'away':r.away_team,'fixture_source':r.source_url,'odds_source':r.odds_source_url,'fixture_status':'MATERIALIZED_STRUCTURED','odds_status':r.odds_pit_status} for r in round_df.itertuples()],
 'historical_expansion':{'new_real_completed_matches_materialized':0,'reason':'Direct network acquisition unavailable; existing historical data preserved.'},
 'real_money':'DISABLED'
}
(ROOT/'ACQUISITION_MANIFEST_FINAL.json').write_text(json.dumps(acq,indent=2,ensure_ascii=False))
# scientific status
status='''# SCIENTIFIC STATUS FINAL\n\nENGINEERING_STATUS: EXPANDED_ON_REAL_INPUT_ZIP\nEMPIRICAL_DATA_STATUS: EXISTING_4864_REAL_COMPLETED_MATCHES_PRESERVED; 5 NEW_STRUCTURED_CURRENT_ROUND_FIXTURE_CONTEXT_RECORDS_MATERIALIZED\nHISTORICAL_EXPANSION_STATUS: ACQUISITION_BLOCKED_FOR_NEW_BULK_BYTES_IN_CONTAINER\nPREDICTIVE_STATUS: EXPERIMENTAL_OOS_HOLDOUT_WALK_FORWARD\nMARKET_STATUS: DATE_LEVEL_PIT_ONLY_FOR_CURRENT_ROUND; 0 EXACT_OR_VALID_PIT_ROWS\nLIVE_STATUS: NOT_HISTORICALLY_VALIDATED\nPAPER_TRADING_STATUS: INFRASTRUCTURE_ONLY; 0 NEW_PAPER_CANDIDATES\nEDGE_STATUS: EDGE_NOT_DETERMINED\nROUND_STATUS: INSUFFICIENT_DATA\nREAL_MONEY: DISABLED\n\n## Integrity rule\nFOUND != DOWNLOADED != ACQUIRED != MATERIALIZED != PROCESSED != PIT_VALIDATED != USED_IN_MODEL.\nNo current-round odds were promoted to exact/valid PIT. No market edge was promoted to PAPER_CANDIDATE.\n'''
(ROOT/'SCIENTIFIC_STATUS_FINAL.md').write_text(status)
# final delivery summary
summary=f'''# FINAL DELIVERY SUMMARY\n\nInput: ROBO_DA_BET_CONMEBOL_ROUND_2026-08-20.zip\nInput SHA-256: {acq['input_zip_sha256']}\n\n## Changes\n- Preserved the full existing project and 4,864 real completed canonical match rows.\n- Added a structured, web-verified 2026-08-20 CONMEBOL round dataset covering all 5 verified target fixtures.\n- Added 15 structured 1X2 market observations (3 per match) from sources that recorded odds on 2026-08-18. These are DATE_LEVEL_PIT only because exact timezone/capture timestamp is not independently proven.\n- Added strict round analyzer and tests; no value bet can pass without exact/valid PIT and validated model support.\n- Fixed gender handling so an existing gender field is preserved instead of being overwritten.\n- Added rivalry registry and explicit knockout importance context.\n\n## New empirical evidence\nNEW REAL COMPLETED MATCHES MATERIALIZED = 0\nNEW REAL STRUCTURED FIXTURE/CONTEXT RECORDS = 5\nNEW STRUCTURED ODDS OBSERVATIONS = 15\nNEW EXACT/VALID PIT ODDS = 0\n\n## Round verdict\nAll 5 CONMEBOL matches were verified. No market opportunity passed the scientific gate.\nStatus: INSUFFICIENT_DATA / EDGE_NOT_DETERMINED / REAL_MONEY=DISABLED\n\n## Limitations\nBulk historical acquisition remained blocked by runtime network/DNS restrictions. Player, lineup, injury, suspension, event, shots, SOT, historical LIVE and exact PIT odds remain unavailable or insufficient in the package.\n'''
(ROOT/'FINAL_DELIVERY_SUMMARY.md').write_text(summary)
# Round report refresh
rpt=ROOT/'reports/rounds/2026-08-20/ROUND_2026-08-20_MASTER_STAFF_REPORT.md'
text=rpt.read_text()
text += '\n## Quantitative market observations\n\nAll 15 structured 1X2 observations are DATE_LEVEL_PIT only. Because exact timestamp and timezone are not proven, they are not eligible for PIT value calculation. Therefore TOP_VALUE_BET = NONE and PAPER_CANDIDATES = 0.\n'
rpt.write_text(text)
print(json.dumps(counts,indent=2))
