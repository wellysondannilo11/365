from app.v25.market_expression import _market_key

def test_card_market_keys_are_shared_with_market_expression():
    assert _market_key('CARD_TOTALS') == 'CARD_TOTALS'
    assert _market_key('CARD_HOME') == 'CARD_HOME'
    assert _market_key('CARD_AWAY') == 'CARD_AWAY'
