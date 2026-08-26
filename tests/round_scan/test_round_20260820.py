from pathlib import Path
import pandas as pd
BASE=Path(__file__).resolve().parents[2]/"reports"/"rounds"/"2026-08-20"
def test_five_games_confirmed():
 df=pd.read_csv(BASE/"ROUND_2026-08-20_MATCH_REGISTRY.csv")
 assert len(df)==5
 assert (df.competition.str.contains("Libertadores")).sum()==2
 assert (df.competition.str.contains("Sudamericana")).sum()==3
def test_no_pit_odds_promoted():
 df=pd.read_csv(BASE/"ROUND_2026-08-20_MARKET_REFERENCES.csv")
 assert not (df.pit_status=="VALID_PIT").any()
def test_real_money_disabled():
 import json
 s=json.loads((BASE/"ROUND_2026-08-20_SUMMARY.json").read_text())
 assert s["real_money"] is False
