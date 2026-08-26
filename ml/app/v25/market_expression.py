from __future__ import annotations
from dataclasses import dataclass, asdict
from math import isfinite
from collections import defaultdict
from statistics import median
from ..v19.pricing import Scoreline, poisson_scoreline_distribution
from .settlement import _parts, _leg, combine_legs, fair_odds_from_settlement_probabilities, expected_value_from_settlement_probabilities

@dataclass(frozen=True)
class Expression:
    event_id: str
    bookmaker: str
    market: str
    selection: str
    line: float | None
    odds: float
    probability: float | None
    fair_odds: float | None
    edge: float | None
    ev: float | None
    uncertainty: float
    market_quality: float
    score: float
    decision: str
    reason: str | None
    target_odds: float | None = None

    def to_dict(self): return asdict(self)


def _market_key(m: str) -> str:
    x=str(m).upper().replace("-", "_")
    if x in {"H2H", "MONEYLINE", "1X2"}: return "H2H"
    if x in {"SPREAD", "SPREADS", "ASIAN_HANDICAP", "AH"}: return "AH"
    if x in {"TOTAL", "TOTALS"}: return "TOTAL"
    if x in {"BTTS", "BOTH_TEAMS_TO_SCORE"}: return "BTTS"
    if x in {"DOUBLE_CHANCE", "DOUBLECHANCE"}: return "DOUBLE_CHANCE"
    if x in {"DNB", "DRAW_NO_BET"}: return "DNB"
    if x in {"CARD_TOTALS", "CARDS_TOTAL", "TOTAL_CARDS", "CARD_TOTAL"}: return "CARD_TOTALS"
    if x in {"CARD_HOME", "HOME_CARDS", "HOME_TEAM_CARDS"}: return "CARD_HOME"
    if x in {"CARD_AWAY", "AWAY_CARDS", "AWAY_TEAM_CARDS"}: return "CARD_AWAY"
    return x


def _resolve_side(selection: str, row: dict) -> str:
    """Resolve provider selection labels (team names or HOME/AWAY/1/2) without guessing."""
    sel = str(selection).strip().upper()
    if sel in {"HOME", "1"}: return "HOME"
    if sel in {"AWAY", "2"}: return "AWAY"
    if sel in {"DRAW", "X"}: return "DRAW"
    home = str(row.get("home_team") or row.get("home") or "").strip().upper()
    away = str(row.get("away_team") or row.get("away") or "").strip().upper()
    if home and sel == home: return "HOME"
    if away and sel == away: return "AWAY"
    return sel

def _settlement_probs(d: list[Scoreline], market: str, selection: str, line: float | None, side: str | None = None, row: dict | None = None) -> dict[str, float]:
    m=_market_key(market); p={k:0.0 for k in ("WIN","HALF_WIN","PUSH","HALF_LOSS","LOSS")}
    for s in d:
        if m=="H2H":
            sel=_resolve_side(selection, row or {})
            result="WIN" if (sel=="HOME" and s.home_goals>s.away_goals) or (sel=="DRAW" and s.home_goals==s.away_goals) or (sel=="AWAY" and s.away_goals>s.home_goals) else "LOSS"
        elif m=="DNB":
            sel=_resolve_side(selection, row or {})
            result="WIN" if (sel=="HOME" and s.home_goals>s.away_goals) or (sel=="AWAY" and s.away_goals>s.home_goals) else "PUSH" if s.home_goals==s.away_goals else "LOSS"
        elif m=="DOUBLE_CHANCE":
            result_code="1" if s.home_goals>s.away_goals else "X" if s.home_goals==s.away_goals else "2"
            result="WIN" if result_code in selection.upper() else "LOSS"
        elif m=="BTTS":
            yes=s.home_goals>0 and s.away_goals>0; result="WIN" if (selection.upper()=="YES")==yes else "LOSS"
        elif m=="AH":
            if line is None: continue
            resolved = _resolve_side(str(side or selection), row or {})
            diff=s.home_goals-s.away_goals if resolved=="HOME" else s.away_goals-s.home_goals
            result=combine_legs(_leg(diff,x) for x in _parts(float(line)))
        elif m=="TOTAL":
            if line is None: continue
            total=s.home_goals+s.away_goals
            result=combine_legs(("WIN" if total>x else "PUSH" if total==x else "LOSS") if selection.upper()=="OVER" else ("WIN" if total<x else "PUSH" if total==x else "LOSS") for x in _parts(float(line)))
        else: continue
        p[result]+=s.probability
    return p


def price_distribution(distribution, row):
    p=_settlement_probs(list(distribution),row.get("market",""),str(row.get("selection","")),row.get("line"),row.get("side"),row)
    fair=fair_odds_from_settlement_probabilities(p)
    return p, fair, expected_value_from_settlement_probabilities(float(row["odds"]),p)


def _consensus(rows):
    groups=defaultdict(list)
    for r in rows:
        try:
            o=float(r["odds"])
            if o>1: groups[(str(r.get("event_id")),_market_key(r.get("market")),r.get("line"),str(r.get("selection")))].append(o)
        except Exception: pass
    # For binary markets, median inverse probability is used after bookmaker-level de-vig.
    out={}
    bybook=defaultdict(list)
    for r in rows:
        try: bybook[(str(r.get("event_id")),_market_key(r.get("market")),r.get("line"),str(r.get("bookmaker")))].append(r)
        except Exception: pass
    for key,grp in bybook.items():
        prices=[]
        for r in grp:
            try: prices.append(float(r["odds"]))
            except Exception: pass
        if len(prices)<2: continue
        inv=[1/x for x in prices]; total=sum(inv)
        for r,x in zip(grp,inv):
            k=(key[0],key[1],key[2],str(r.get("selection")))
            out.setdefault(k,[]).append(x/total)
    return {k:median(v) for k,v in out.items()}


class MarketExpressionEngine:
    version="25.0.0"
    def __init__(self,min_odds=1.50,preferred_odds=1.66,min_edge=.05,min_ev=.05,max_uncertainty=.12,exception_edge=.10):
        self.min_odds=min_odds; self.preferred_odds=preferred_odds; self.min_edge=min_edge; self.min_ev=min_ev; self.max_uncertainty=max_uncertainty; self.exception_edge=exception_edge

    def analyze(self, rows, distribution=None):
        rows=list(rows); consensus=_consensus(rows); out=[]
        for r in rows:
            try: odds=float(r["odds"])
            except Exception: continue
            if odds<=1: continue
            key=(str(r.get("event_id")),_market_key(r.get("market")),r.get("line"),str(r.get("selection")))
            p=None; fair=None
            if distribution is not None:
                pset,fair,settlement_ev=price_distribution(distribution,r)
                win_eq=pset["WIN"]+.5*pset["HALF_WIN"]; loss_eq=pset["LOSS"]+.5*pset["HALF_LOSS"]
                p=win_eq/(win_eq+loss_eq) if win_eq+loss_eq>0 else None
            elif r.get("model_probability") is not None:
                p=float(r["model_probability"]); fair=1/p if p>0 else None
            else:
                p=consensus.get(key); fair=1/p if p else None
            edge=p-1/odds if p is not None else None
            ev=settlement_ev if distribution is not None else (p*odds-1 if p is not None else None)
            uncertainty=float(r.get("uncertainty",0.05 if p is not None else 1.0))
            quality=float(r.get("market_quality",1.0 if p is not None else 0.0))
            reasons=[]
            decision="NO BET"
            target_odds=None
            if odds<self.min_odds: reasons.append("ODDS_BELOW_MINIMUM")
            elif p is None: reasons.append("NO_PIT_MODEL_OR_MARKET_BASELINE")
            elif uncertainty>self.max_uncertainty: reasons.append("HIGH_UNCERTAINTY")
            elif quality<.4: reasons.append("LOW_MARKET_QUALITY")
            elif odds<self.preferred_odds and (edge<self.exception_edge or ev<self.exception_edge): reasons.append("ODDS_IN_EXCEPTION_BAND")
            elif edge<self.min_edge:
                reasons.append("INSUFFICIENT_EDGE")
                if fair is not None and fair > odds and odds >= self.min_odds:
                    decision="WATCH"; target_odds=round(max(self.preferred_odds, fair),4); reasons=["WAIT_FOR_PRICE"]
            elif ev<self.min_ev:
                reasons.append("INSUFFICIENT_EV")
                if fair is not None and fair > odds and odds >= self.min_odds:
                    decision="WATCH"; target_odds=round(max(self.preferred_odds, fair),4); reasons=["WAIT_FOR_PRICE"]
            else: decision="BET"
            pref_bonus=.04 if odds>=self.preferred_odds else 0
            score=max(0,min(100,100*((max(edge or 0,0)/.15)*.35+(max(ev or 0,0)/.30)*.35+(1-uncertainty)*.15+quality*.15)+pref_bonus))
            out.append(Expression(str(r.get("event_id")),str(r.get("bookmaker","")),_market_key(r.get("market")),str(r.get("selection")),r.get("line"),odds,p,fair,edge,ev,uncertainty,quality,score,decision,"|".join(reasons) if reasons else None,target_odds).to_dict())
        return sorted(out,key=lambda x:(x["decision"]=="BET",x["score"],x["ev"] or -999),reverse=True)

    def select(self, rows, distribution=None, max_per_event=1):
        ranked=self.analyze(rows,distribution); selected=[]; seen={}
        for x in ranked:
            e=x["event_id"]
            if x["decision"]!="BET": continue
            if seen.get(e,0)>=max_per_event: continue
            selected.append(x); seen[e]=seen.get(e,0)+1
        selected_keys={(x["event_id"],x["bookmaker"],x["market"],x["selection"],x.get("line")) for x in selected}
        for x in ranked:
            if x["decision"]=="BET" and (x["event_id"],x["bookmaker"],x["market"],x["selection"],x.get("line")) not in selected_keys:
                x["decision"]="NO BET"; x["reason"]="BEST_EXPRESSION_ALREADY_SELECTED"
        return ranked,selected
