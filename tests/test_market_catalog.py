from app.intelligence.market_catalog import supported_market_keys, market_requirements

def test_catalog_contains_required_market_families():
    keys=set(supported_market_keys())
    for k in ['H2H','TOTAL','AH','BTTS','CARD_TOTALS','CORNER_TOTAL','NEXT_GOAL','PLAYER_SHOTS']:
        assert k in keys

def test_live_requirements_are_explicit():
    assert 'minute' in market_requirements('TOTAL')
    assert 'source_timestamp' in market_requirements('NEXT_GOAL')
