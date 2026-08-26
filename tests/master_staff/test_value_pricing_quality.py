from ml.app.master_staff.value_pricing import implied_probability, no_vig_probabilities, price_market

def test_pricing_math():
    assert abs(implied_probability(2.0)-.5)<1e-9
    p=no_vig_probabilities([2.0,4.0,4.0]); assert abs(sum(p)-1)<1e-9

def test_date_level_never_becomes_value_bet():
    r=price_market(market='1X2',selection='HOME',odds=2.0,model_probability=.60,
                   pit_status='DATE_LEVEL_PIT',model_validated=True,sample_size=1000,data_quality=.95)
    assert r.decision=='WATCH'
    assert 'PIT_NOT_EXACT_OR_VALID' in r.reason

def test_exact_pit_can_pass_gate_only_with_all_conditions():
    r=price_market(market='1X2',selection='HOME',odds=2.0,model_probability=.60,
                   pit_status='EXACT_PIT',model_validated=True,sample_size=1000,data_quality=.95)
    assert r.decision=='VALUE_BET'
