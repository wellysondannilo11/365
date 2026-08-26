from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class SettlementProbabilities:
    win: float
    half_win: float
    push: float
    half_loss: float
    loss: float

    def validate(self) -> None:
        vals = [self.win, self.half_win, self.push, self.half_loss, self.loss]
        if any((not isfinite(x) or x < 0) for x in vals) or abs(sum(vals) - 1.0) > 1e-8:
            raise ValueError('INVALID_SETTLEMENT_PROBABILITIES')


def expected_value(odds: float, p: SettlementProbabilities) -> float:
    if not isfinite(odds) or odds <= 1:
        raise ValueError('INVALID_ODDS')
    p.validate()
    win_equivalent = p.win + 0.5 * p.half_win
    loss_equivalent = p.loss + 0.5 * p.half_loss
    return win_equivalent * (odds - 1.0) - loss_equivalent


def fair_odds(p: SettlementProbabilities) -> float | None:
    p.validate()
    win_equivalent = p.win + 0.5 * p.half_win
    loss_equivalent = p.loss + 0.5 * p.half_loss
    if win_equivalent <= 0:
        return None
    return 1.0 + loss_equivalent / win_equivalent
