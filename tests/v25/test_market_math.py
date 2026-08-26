from app.v25.settlement import expected_value_from_settlement_probabilities,fair_odds_from_settlement_probabilities
from app.v25.market_expression import MarketExpressionEngine
from app.v19.pricing import poisson_scoreline_distribution

def test_asian_ev_uses_settlement_distribution_not_binary_shortcut():
    p={'WIN':.25,'HALF_WIN':.25,'PUSH':.25,'HALF_LOSS':.0,'LOSS':.25}
    ev=expected_value_from_settlement_probabilities(2.0,p)
    assert abs(ev-(.25*1+.25*.5-.25))<1e-9
    assert abs(fair_odds_from_settlement_probabilities(p)-1.6666666666666667)<1e-9

def test_distribution_prices_quarter_handicap():
    d=poisson_scoreline_distribution(1.8,.8)
    row={'event_id':'e','market':'spreads','selection':'Home','line':-0.25,'bookmaker':'b','odds':2.0}
    x=MarketExpressionEngine(min_edge=-1,min_ev=-1).analyze([row],d)[0]
    assert x['fair_odds'] and x['ev'] is not None


def test_distribution_uses_provider_team_names():
    d=poisson_scoreline_distribution(2.0,.5)
    rows=[{'event_id':'e','market':'h2h','selection':'LDU','home_team':'LDU','away_team':'Mirassol','bookmaker':'b','odds':1.70}]
    x=MarketExpressionEngine(min_edge=-1,min_ev=-1).analyze(rows,d)[0]
    assert x['probability'] is not None and x['probability'] > 0.5

def test_v19_quarter_lines_are_supported_for_negative_and_positive_lines():
    d=poisson_scoreline_distribution(1.5,1.0)
    from app.v19.pricing import asian_handicap_outcomes
    assert asian_handicap_outcomes(d,-0.25,'HOME')['half_loss'] >= 0
    assert asian_handicap_outcomes(d,0.75,'HOME')['half_win'] >= 0
