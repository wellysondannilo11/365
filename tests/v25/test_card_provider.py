from app.adapters.card_data import APIFootballCardProvider

def test_card_provider_is_fail_closed_without_credentials():
    p=APIFootballCardProvider(key='')
    assert not p.configured
    try: p.match_card_snapshot('1')
    except RuntimeError as e: assert str(e)=='CREDENTIALS_UNAVAILABLE'
    else: raise AssertionError('provider must fail closed')
