from __future__ import annotations

from dataclasses import dataclass, asdict
from math import exp, factorial, isfinite
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Scoreline:
    home_goals: int
    away_goals: int
    probability: float


@dataclass(frozen=True)
class MarketProbability:
    market: str
    selection: str
    line: float | None
    probability: float
    fair_odds: float | None
    settlement: str = "BINARY"


@dataclass(frozen=True)
class Dislocation:
    market: str
    selection: str
    line: float | None
    model_probability: float
    market_probability: float
    market_odds: float
    fair_odds: float | None
    probability_edge: float
    odds_ratio: float | None
    ev: float | None
    source: str | None = None


def _poisson_pmf(k: int, lam: float) -> float:
    if k < 0 or lam < 0:
        return 0.0
    return exp(-lam) * (lam ** k) / factorial(k)


def poisson_scoreline_distribution(
    home_lambda: float,
    away_lambda: float,
    max_goals: int = 10,
    dixon_coles_rho: float | None = None,
) -> list[Scoreline]:
    if home_lambda < 0 or away_lambda < 0:
        raise ValueError("EXPECTED_GOALS_MUST_BE_NON_NEGATIVE")
    if max_goals < 1:
        raise ValueError("MAX_GOALS_MUST_BE_POSITIVE")
    raw: list[Scoreline] = []
    for h in range(max_goals + 1):
        ph = _poisson_pmf(h, home_lambda)
        for a in range(max_goals + 1):
            p = ph * _poisson_pmf(a, away_lambda)
            if dixon_coles_rho is not None:
                rho = float(dixon_coles_rho)
                if h == 0 and a == 0:
                    p *= 1 - rho
                elif h == 0 and a == 1:
                    p *= 1 + rho
                elif h == 1 and a == 0:
                    p *= 1 + rho
                elif h == 1 and a == 1:
                    p *= 1 - rho
            raw.append(Scoreline(h, a, p))
    total = sum(x.probability for x in raw)
    if not isfinite(total) or total <= 0:
        raise ValueError("INVALID_SCORELINE_MASS")
    return [Scoreline(x.home_goals, x.away_goals, x.probability / total) for x in raw]


def distribution_matrix(distribution: Iterable[Scoreline]) -> dict[tuple[int, int], float]:
    return {(x.home_goals, x.away_goals): float(x.probability) for x in distribution}


def _validate_probability(p: float) -> float:
    p = float(p)
    if not isfinite(p) or p < 0 or p > 1:
        raise ValueError("PROBABILITY_OUT_OF_RANGE")
    return p


def fair_odds_from_probability(probability: float) -> float | None:
    p = _validate_probability(probability)
    if p <= 0:
        return None
    return 1.0 / p


def _total_goals(x: Scoreline) -> int:
    return x.home_goals + x.away_goals


def derived_market_probabilities(
    distribution: Iterable[Scoreline],
    total_lines: Iterable[float] = (0.5, 1.5, 2.5, 3.5, 4.5),
    handicap_lines: Iterable[float] = (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5),
) -> list[MarketProbability]:
    d = list(distribution)
    if not d:
        raise ValueError("EMPTY_SCORELINE_DISTRIBUTION")
    if abs(sum(x.probability for x in d) - 1.0) > 1e-8:
        raise ValueError("SCORELINE_DISTRIBUTION_NOT_NORMALIZED")
    out: list[MarketProbability] = []

    def add(market: str, selection: str, p: float, line: float | None = None, settlement: str = "BINARY"):
        p = _validate_probability(p)
        out.append(MarketProbability(market, selection, line, p, fair_odds_from_probability(p), settlement))

    home = sum(x.probability for x in d if x.home_goals > x.away_goals)
    draw = sum(x.probability for x in d if x.home_goals == x.away_goals)
    away = sum(x.probability for x in d if x.home_goals < x.away_goals)
    add("1X2", "Home", home)
    add("1X2", "Draw", draw)
    add("1X2", "Away", away)
    add("DOUBLE_CHANCE", "1X", home + draw)
    add("DOUBLE_CHANCE", "X2", draw + away)
    add("DOUBLE_CHANCE", "12", home + away)

    btts = sum(x.probability for x in d if x.home_goals > 0 and x.away_goals > 0)
    add("BTTS", "Yes", btts)
    add("BTTS", "No", 1 - btts)

    for line in total_lines:
        over = sum(x.probability for x in d if _total_goals(x) > line)
        add("TOTAL", "Over", over, float(line))
        add("TOTAL", "Under", 1 - over, float(line))

    # Asian handicap probability decomposition is represented by a separate helper;
    # binary fair odds are only emitted for half-goal lines where no push exists.
    for line in handicap_lines:
        home_out = asian_handicap_outcomes(d, float(line), side="HOME")
        away_out = asian_handicap_outcomes(d, float(-line), side="AWAY")
        for side, outcomes in (("Home", home_out), ("Away", away_out)):
            q = outcomes["win"] + 0.5 * outcomes["half_win"]
            l = outcomes["loss"] + 0.5 * outcomes["half_loss"]
            fair = 1 + l / q if q > 0 else None
            out.append(MarketProbability("ASIAN_HANDICAP", side, float(line), q, fair, "ASIAN"))
    return out


def asian_handicap_outcomes(
    distribution: Iterable[Scoreline], line: float, side: str = "HOME"
) -> dict[str, float]:
    side = side.upper()
    if side not in {"HOME", "AWAY"}:
        raise ValueError("INVALID_HANDICAP_SIDE")
    # Quarter lines are settled as two adjacent half/whole lines.
    if abs(line * 4 - round(line * 4)) > 1e-9:
        raise ValueError("INVALID_HANDICAP_LINE")
    parts = [line]
    if abs(line * 2 - round(line * 2)) > 1e-9:
        low = (int(round(line * 4)) // 2) / 2
        parts = [low, low + 0.5]
    result = {"win": 0.0, "half_win": 0.0, "push": 0.0, "half_loss": 0.0, "loss": 0.0}
    d = list(distribution)
    for x in d:
        dif = x.home_goals - x.away_goals if side == "HOME" else x.away_goals - x.home_goals
        statuses = []
        for part in parts:
            adj = dif + part
            statuses.append("win" if adj > 0 else "push" if adj == 0 else "loss")
        if len(statuses) == 1:
            result[statuses[0]] += x.probability
        elif statuses.count("win") == 2:
            result["win"] += x.probability
        elif statuses.count("loss") == 2:
            result["loss"] += x.probability
        elif "win" in statuses and "push" in statuses:
            result["half_win"] += x.probability
        elif "loss" in statuses and "push" in statuses:
            result["half_loss"] += x.probability
        else:
            result["push"] += x.probability
    return result


def market_probability_map(distribution: Iterable[Scoreline]) -> dict[str, float]:
    """Convenience map using canonical keys for API consumers."""
    items = derived_market_probabilities(distribution)
    return {f"{x.market}:{x.selection}:{x.line if x.line is not None else ''}": x.probability for x in items}


def market_dislocation(
    model_probability: float,
    market_odds: float,
    market_probability: float | None = None,
    market: str = "UNKNOWN",
    selection: str = "UNKNOWN",
    line: float | None = None,
    source: str | None = None,
) -> Dislocation:
    p = _validate_probability(model_probability)
    o = float(market_odds)
    if not isfinite(o) or o <= 1:
        raise ValueError("INVALID_MARKET_ODDS")
    mp = (1 / o) if market_probability is None else _validate_probability(market_probability)
    fair = fair_odds_from_probability(p)
    return Dislocation(
        market=market,
        selection=selection,
        line=line,
        model_probability=p,
        market_probability=mp,
        market_odds=o,
        fair_odds=fair,
        probability_edge=p - mp,
        odds_ratio=(o / fair) if fair else None,
        ev=p * o - 1,
        source=source,
    )


def rank_dislocations(rows: Iterable[Dislocation]) -> list[dict]:
    return [asdict(x) for x in sorted(rows, key=lambda x: (x.ev if x.ev is not None else float('-inf')), reverse=True)]
