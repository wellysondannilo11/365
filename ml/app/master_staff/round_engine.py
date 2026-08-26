from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
from .value_pricing import price_market


def discover_round(canonical: pd.DataFrame, target_date: str, competitions: list[str] | None = None) -> pd.DataFrame:
    d=canonical.copy(); d['kickoff_timestamp']=pd.to_datetime(d['kickoff_timestamp'],errors='coerce')
    day=d[d.kickoff_timestamp.dt.strftime('%Y-%m-%d').eq(target_date)].copy()
    if competitions:
        day=day[day.competition.isin(competitions)]
    return day


def analyze_market(*, market: str, selection: str, odds, pit_status: str,
                   model_probability=None, model_validated=False, sample_size=0,
                   data_quality=0.0):
    return price_market(market=market,selection=selection,odds=odds,
                        model_probability=model_probability,pit_status=pit_status,
                        model_validated=model_validated,sample_size=sample_size,
                        data_quality=data_quality). __dict__
