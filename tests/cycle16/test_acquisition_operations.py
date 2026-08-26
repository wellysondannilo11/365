from pathlib import Path
from ml.app.cycle16.acquisition import source_registry, runtime_probe
from ml.app.cycle16.operations import OperationalState, real_money_allowed


def test_source_registry_contains_priority_routes():
    names={x['name'] for x in source_registry()}
    assert {'sharpapi','beatthebookie','fabul0us_football_odds_2023_24','the_odds_api_historical','betfair_historical'} <= names


def test_runtime_probe_is_honest_when_dns_is_blocked():
    out=runtime_probe(['https://example.invalid'])
    assert out and out[0]['status'] in {'DNS_BLOCKED','HTTPS_BLOCKED','UNAVAILABLE'}


def test_real_money_is_always_locked():
    state=OperationalState(real_money_configured=True, economic_gate_passed=True)
    assert real_money_allowed(state) is False
