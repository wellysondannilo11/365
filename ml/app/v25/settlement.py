from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

STATUSES = ("WIN", "HALF_WIN", "PUSH", "HALF_LOSS", "LOSS")


def _parts(line: float) -> tuple[float, ...]:
    line = float(line)
    if abs(line * 4 - round(line * 4)) > 1e-9:
        raise ValueError("INVALID_ASIAN_LINE")
    q = round(line * 4) / 4
    if abs(q * 2 - round(q * 2)) < 1e-9:
        return (q,)
    lo = (int(q * 4) // 2) / 2
    return (lo, lo + 0.5)


def _leg(diff: float, line: float) -> str:
    x = diff + line
    return "WIN" if x > 0 else "PUSH" if abs(x) < 1e-12 else "LOSS"


def combine_legs(legs: Iterable[str]) -> str:
    legs = list(legs)
    if any(x not in {"WIN", "PUSH", "LOSS"} for x in legs):
        raise ValueError("INVALID_SETTLEMENT_LEG")
    if len(legs) == 1:
        return legs[0]
    if legs.count("WIN") == 2: return "WIN"
    if legs.count("LOSS") == 2: return "LOSS"
    if legs.count("PUSH") == 2: return "PUSH"
    if "WIN" in legs and "PUSH" in legs: return "HALF_WIN"
    if "LOSS" in legs and "PUSH" in legs: return "HALF_LOSS"
    raise ValueError("UNEXPECTED_ASIAN_SETTLEMENT")


def asian_settlement(home_goals: int, away_goals: int, line: float, side: str = "HOME") -> str:
    side = side.upper()
    if side not in {"HOME", "AWAY"}: raise ValueError("INVALID_HANDICAP_SIDE")
    diff = home_goals - away_goals if side == "HOME" else away_goals - home_goals
    return combine_legs(_leg(diff, p) for p in _parts(line))


def total_settlement(home_goals: int, away_goals: int, line: float, side: str = "OVER") -> str:
    side = side.upper()
    if side not in {"OVER", "UNDER"}: raise ValueError("INVALID_TOTAL_SIDE")
    total = home_goals + away_goals
    if side == "OVER":
        legs = ("WIN" if total > p else "PUSH" if total == p else "LOSS" for p in _parts(line))
    else:
        legs = ("WIN" if total < p else "PUSH" if total == p else "LOSS" for p in _parts(line))
    return combine_legs(legs)


def fair_odds_from_settlement_probabilities(p: dict[str, float]) -> float | None:
    vals = {k: float(p.get(k, 0.0)) for k in STATUSES}
    if any(v < 0 for v in vals.values()) or abs(sum(vals.values()) - 1.0) > 1e-8:
        raise ValueError("INVALID_SETTLEMENT_PROBABILITIES")
    win_equiv = vals["WIN"] + 0.5 * vals["HALF_WIN"]
    loss_equiv = vals["LOSS"] + 0.5 * vals["HALF_LOSS"]
    return 1.0 + loss_equiv / win_equiv if win_equiv > 0 else None


def expected_value_from_settlement_probabilities(odds: float, p: dict[str, float]) -> float:
    odds=float(odds)
    if odds<=1: raise ValueError("INVALID_ODDS")
    vals={k:float(p.get(k,0.0)) for k in STATUSES}
    if any(v<0 for v in vals.values()) or abs(sum(vals.values())-1.0)>1e-8: raise ValueError("INVALID_SETTLEMENT_PROBABILITIES")
    return vals["WIN"]*(odds-1.0)+vals["HALF_WIN"]*0.5*(odds-1.0)-vals["LOSS"]-vals["HALF_LOSS"]*0.5


@dataclass(frozen=True)
class SettlementRule:
    provider: str
    market: str
    rule: str


class SettlementRuleRegistry:
    def __init__(self): self._rules: dict[tuple[str, str], SettlementRule] = {}
    def register(self, provider: str, market: str, rule: str) -> None:
        self._rules[(provider.lower(), market.lower())] = SettlementRule(provider, market, rule)
    def resolve(self, provider: str, market: str) -> SettlementRule:
        return self._rules.get((provider.lower(), market.lower()), SettlementRule(provider, market, "STANDARD_FOOTBALL"))


def settlement_result(*, market: str, selection: str, line: float | None, home_goals: int, away_goals: int, provider: str = "default", home_team: str | None = None, away_team: str | None = None) -> str:
    m = market.upper()
    if m in {"ASIAN_HANDICAP", "SPREAD", "AH"}:
        side = "HOME" if selection.upper() in {"HOME", "1"} else "AWAY"
        if line is None: raise ValueError("HANDICAP_LINE_REQUIRED")
        return asian_settlement(home_goals, away_goals, float(line), side)
    if m in {"TOTAL", "TOTALS", "OVER_UNDER"}:
        if line is None: raise ValueError("TOTAL_LINE_REQUIRED")
        return total_settlement(home_goals, away_goals, float(line), selection)
    if m in {"1X2", "H2H", "MONEYLINE"}:
        s = selection.upper()
        if home_team and s == str(home_team).upper(): s = "HOME"
        elif away_team and s == str(away_team).upper(): s = "AWAY"
        if s in {"HOME", "1"}: return "WIN" if home_goals > away_goals else "LOSS"
        if s in {"DRAW", "X"}: return "WIN" if home_goals == away_goals else "LOSS"
        if s in {"AWAY", "2"}: return "WIN" if away_goals > home_goals else "LOSS"
    if m == "BTTS":
        yes = home_goals > 0 and away_goals > 0
        return "WIN" if (selection.upper() == "YES") == yes else "LOSS"
    if m == "DOUBLE_CHANCE":
        result = "1" if home_goals > away_goals else "X" if home_goals == away_goals else "2"
        return "WIN" if result in selection.upper().replace("X", "X") else "LOSS"
    raise ValueError(f"UNSUPPORTED_SETTLEMENT_MARKET:{market}")
