from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from .pricing import derived_market_probabilities, poisson_scoreline_distribution


class PricingEngine:
    """Single pricing core usable by prematch and live state providers.

    The engine consumes a temporal state and expected-goal rates supplied by an
    upstream feature/model layer. It does not manufacture missing live state.
    """

    version = '19.0.0'

    def price(
        self,
        *,
        event_id: str,
        decision_time: datetime,
        home_expected_goals: float,
        away_expected_goals: float,
        market_state: str = 'PRE',
        dixon_coles_rho: float | None = None,
        max_goals: int = 10,
    ) -> dict:
        distribution = poisson_scoreline_distribution(
            home_expected_goals,
            away_expected_goals,
            max_goals=max_goals,
            dixon_coles_rho=dixon_coles_rho,
        )
        markets = [asdict(x) for x in derived_market_probabilities(distribution)]
        return {
            'event_id': event_id,
            'decision_time': decision_time.isoformat(),
            'market_state': market_state,
            'pricing_engine_version': self.version,
            'expected_goals': {'home': home_expected_goals, 'away': away_expected_goals},
            'distribution': [asdict(x) for x in distribution],
            'markets': markets,
        }
