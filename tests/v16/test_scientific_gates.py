import pandas as pd
import pytest
from ml.app.v16.odds_verification import verify_odds
from ml.app.v16.decision_dataset import build_decision_record
from ml.app.v16.experiment_registry import ExperimentRegistry


def test_non_pit_opening_closing_is_not_scientifically_eligible():
    r=verify_odds({"price":1.80,"source":"Football-Data.co.uk","source_record_id":"x","availability_evidence":"DATE_ONLY"}, decision_time="2025-01-01T12:00:00Z")
    assert r.odds_exists and r.odds_numerically_valid and r.odds_source_verified
    assert not r.odds_pit_verified
    assert not r.odds_scientifically_eligible
    assert r.reason == "PIT_NOT_VERIFIED"


def test_exact_pit_requires_available_and_source_before_decision():
    r=verify_odds({"price":2.10,"source":"provider","source_record_id":"x","available_at":"2025-01-01T11:00:00Z","source_timestamp":"2025-01-01T11:00:00Z"}, decision_time="2025-01-01T12:00:00Z")
    assert r.odds_scientifically_eligible


def test_future_price_is_blocked():
    r=verify_odds({"price":2.10,"source":"provider","source_record_id":"x","available_at":"2025-01-01T13:00:00Z","source_timestamp":"2025-01-01T13:00:00Z"}, decision_time="2025-01-01T12:00:00Z")
    assert not r.odds_scientifically_eligible
    assert r.reason == "PIT_NOT_VERIFIED"


def test_decision_record_contains_explicit_gates():
    d=build_decision_record(event_id='e1',event_time='2025-01-01T14:00:00Z',decision_time='2025-01-01T12:00:00Z',market='TOTAL',selection='OVER 2.5',bookmaker='x',price=2.2,source='provider',source_timestamp='2025-01-01T11:00:00Z',features={'x':1},feature_version='f1',model_version='m1',probability=.5,confidence='HIGH',stake=1,decision='APPROVED')
    assert d.all_gates['odds_scientifically_eligible'] is True
    assert d.fair_price == 2.0
    assert round(d.EV,6) == .1


def test_experiment_registry_writes_record(tmp_path):
    reg=ExperimentRegistry(tmp_path/'experiments.jsonl')
    x=reg.record(experiment_id='E1',hypothesis='h',baseline='b',change='c',dataset='d')
    assert x['promotion_status']=='RESEARCH_ONLY'
    assert (tmp_path/'experiments.jsonl').exists()
