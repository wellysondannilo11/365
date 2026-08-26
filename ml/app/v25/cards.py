from __future__ import annotations
"""Card-market extension for V25 architecture.

This module is deliberately provider-agnostic. It never fabricates referee/team
statistics: missing or insufficient observations produce UNKNOWN/NO BET.
Default weights are an auditable baseline heuristic, not empirical truth; they
must be calibrated against real observations before scientific promotion.
"""
from dataclasses import dataclass, asdict
from math import exp, lgamma
from statistics import mean, median, variance
from datetime import datetime, timezone

CARD_TOTALS = "CARD_TOTALS"
CARD_HOME = "CARD_HOME"
CARD_AWAY = "CARD_AWAY"
CARD_MARKETS = {CARD_TOTALS, CARD_HOME, CARD_AWAY}

@dataclass(frozen=True)
class CardFeature:
    value: float | None
    confidence: float
    sample_size: int
    source: str | None
    source_timestamp: str | None
    captured_at: str
    quality: str
    version: str = "cards-baseline-1"

    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class CardModelResult:
    market: str
    selection: str
    line: float
    expected: float
    distribution: str
    fair_probability: float | None
    fair_odds: float | None
    edge: float | None
    ev: float | None
    uncertainty: float
    confidence: float
    decision: str
    reason: str | None
    target_odds: float | None
    model: str
    model_version: str

    def to_dict(self): return asdict(self)

def _now(): return datetime.now(timezone.utc).isoformat()

def _feature(v, n, source=None, source_timestamp=None, captured_at=None, quality=None):
    n=int(n or 0); v=float(v) if v is not None else None
    conf=min(1.0, n/30.0) if n else 0.0
    if quality == "STALE": conf=0.0
    return CardFeature(v, conf, n, source, source_timestamp, captured_at or _now(), quality or ("OK" if v is not None else "UNKNOWN"))

def _mean_feature(values, source="observed"):
    vals=[float(x) for x in values if x is not None]
    return _feature(mean(vals), len(vals), source=source) if vals else _feature(None,0,source=source,quality="UNKNOWN")

def _poisson_pmf(k, mu):
    if k < 0 or mu < 0: return 0.0
    if mu == 0: return 1.0 if k == 0 else 0.0
    return exp(-mu + k*__import__('math').log(mu) - lgamma(k+1))

def _nb_pmf(k, mu, variance):
    if k < 0 or mu <= 0: return 0.0
    if variance <= mu: return _poisson_pmf(k,mu)
    r=mu*mu/(variance-mu); p=r/(r+mu)
    return exp(lgamma(k+r)-lgamma(r)-lgamma(k+1)+r*__import__('math').log(p)+k*__import__('math').log1p(-p))

def _parts(line: float):
    x=round(float(line)*4)/4
    if abs(x-round(x))<1e-9: return (x,)
    if abs((x*2)-round(x*2))<1e-9: return (x,)
    return (x-0.25,x+0.25)

def _leg(total, line, selection):
    if selection == "OVER": return "WIN" if total>line else "PUSH" if total==line else "LOSS"
    return "WIN" if total<line else "PUSH" if total==line else "LOSS"

def settlement_probs(observed_or_final: int | float, line: float, selection: str):
    """Settlement for a realized card count, including quarter lines."""
    out={k:0.0 for k in ("WIN","HALF_WIN","PUSH","HALF_LOSS","LOSS")}
    legs=_parts(line); results=[_leg(float(observed_or_final),x,selection.upper()) for x in legs]
    if len(results)==1: out[results[0]]=1.0; return out
    a,b=results
    if a==b: out[a]=1.0
    elif {a,b}=={"WIN","PUSH"}: out["HALF_WIN"]=1.0
    elif {a,b}=={"LOSS","PUSH"}: out["HALF_LOSS"]=1.0
    elif {a,b}=={"WIN","LOSS"}: out["PUSH"]=1.0
    elif "WIN" in {a,b} and "HALF_LOSS" in {a,b}: out["HALF_LOSS"]=1.0
    else: out["PUSH"]=1.0
    return out

def _prob_distribution(mu, variance_=None, max_cards=30):
    mu=max(0.0,float(mu)); var=float(variance_ if variance_ is not None else mu)
    model="NEGATIVE_BINOMIAL" if var>mu*1.05 and mu>0 else "POISSON"
    probs=[(_nb_pmf(k,mu,var) if model=="NEGATIVE_BINOMIAL" else _poisson_pmf(k,mu)) for k in range(max_cards+1)]
    s=sum(probs)
    return model,[p/s for p in probs] if s else [1.0]+[0.0]*max_cards

def _settlement_probability(probs, line, selection):
    p={k:0.0 for k in ("WIN","HALF_WIN","PUSH","HALF_LOSS","LOSS")}
    for k,pk in enumerate(probs):
        sp=settlement_probs(k,line,selection)
        for key,val in sp.items(): p[key]+=pk*val
    return p

def fair_odds_from_probs(p):
    # Fair odds for non-binary settlement are based on expected net return.
    win=p["WIN"]+.5*p["HALF_WIN"]; loss=p["LOSS"]+.5*p["HALF_LOSS"]
    if win<=0: return None
    return 1.0 + loss/win

def expected_value(odds,p):
    return p["WIN"]*(odds-1)+p["HALF_WIN"]*(odds-1)/2-p["HALF_LOSS"]/2-p["LOSS"]

def fair_probability(p):
    win=p["WIN"]+.5*p["HALF_WIN"]; loss=p["LOSS"]+.5*p["HALF_LOSS"]
    return win/(win+loss) if win+loss else None

def feature_bundle(payload):
    """Build auditable card features from supplied observations only."""
    now=payload.get("captured_at") or _now()
    ref=_feature(payload.get("referee_cards_avg"),payload.get("referee_sample_size",0),payload.get("referee_source"),payload.get("referee_source_timestamp"),now,payload.get("referee_quality"))
    home=_feature(payload.get("home_cards_avg"),payload.get("home_sample_size",0),payload.get("team_source"),payload.get("team_source_timestamp"),now,payload.get("team_quality"))
    away=_feature(payload.get("away_cards_avg"),payload.get("away_sample_size",0),payload.get("team_source"),payload.get("team_source_timestamp"),now,payload.get("team_quality"))
    h2h=_feature(payload.get("h2h_cards_avg"),payload.get("h2h_sample_size",0),payload.get("h2h_source"),payload.get("h2h_source_timestamp"),now,payload.get("h2h_quality"))
    importance=payload.get("match_importance")
    if importance is not None: importance=float(importance); iq=1.0
    else: importance=None; iq=0.0
    vals=[x.value for x in (ref,home,away,h2h) if x.value is not None]
    samples=[x.sample_size for x in (ref,home,away,h2h) if x.value is not None]
    if not vals: quality="UNKNOWN"; conf=0.0
    else:
        quality="OK" if all(x.quality=="OK" for x in (ref,home,away,h2h) if x.value is not None) else "DEGRADED"
        conf=min([x.confidence for x in (ref,home,away,h2h) if x.value is not None] + ([iq] if importance is not None else [1.0]))
    return {"referee":ref,"home":home,"away":away,"h2h":h2h,"match_importance":importance,"confidence":conf,"quality":quality,"sample_size":sum(samples)}

def _market_expected_cards(features, market, payload):
    """Return a market-specific expectation without mixing home/away totals.

    CARD_HOME/CARD_AWAY require side-specific evidence. CARD_TOTALS prefers the
    sum of the two side-specific estimates and falls back to a referee/H2H total
    only when side-specific data are unavailable. This avoids the previous bug
    where all three card markets shared one total-card expectation.
    """
    market=str(market or CARD_TOTALS).upper()
    ref=features.get("referee")
    home=features.get("home")
    away=features.get("away")
    h2h=features.get("h2h")

    def usable(f):
        return isinstance(f, CardFeature) and f.value is not None and f.quality not in {"STALE", "INVALID"}

    if market == CARD_HOME:
        if not usable(home):
            return None, "UNKNOWN", 0.0, None
        mu=float(home.value)
        conf=float(home.confidence)
        var=payload.get("home_variance")
    elif market == CARD_AWAY:
        if not usable(away):
            return None, "UNKNOWN", 0.0, None
        mu=float(away.value)
        conf=float(away.confidence)
        var=payload.get("away_variance")
    elif market == CARD_TOTALS:
        if usable(home) and usable(away):
            mu=float(home.value)+float(away.value)
            conf=min(float(home.confidence), float(away.confidence))
            var=payload.get("total_variance")
        elif usable(ref):
            mu=float(ref.value)
            conf=float(ref.confidence)
            var=payload.get("total_variance", payload.get("variance"))
        elif usable(h2h):
            mu=float(h2h.value)
            conf=float(h2h.confidence)
            var=payload.get("total_variance", payload.get("variance"))
        else:
            return None, "UNKNOWN", 0.0, None
    else:
        return None, "UNKNOWN", 0.0, None

    intensity=payload.get("match_intensity", features.get("match_intensity"))
    if intensity is not None:
        mu*=max(0.75,min(1.25,1+0.05*(float(intensity)-0.5)))
        conf=min(conf, float(features.get("confidence", conf)))
    model,_=_prob_distribution(mu, var)
    return mu, model, min(conf,1.0), var

def _pit_valid(payload, features):
    decision=payload.get("decision_time")
    if not decision: return True
    try: dt=datetime.fromisoformat(str(decision).replace("Z","+00:00"))
    except Exception: return False
    if dt.tzinfo is None: return False
    for key in ("referee","home","away","h2h"):
        f=features.get(key)
        if not isinstance(f,CardFeature):
            continue
        for ts in (f.source_timestamp, f.captured_at):
            if not ts: continue
            try:
                st=datetime.fromisoformat(str(ts).replace("Z","+00:00"))
                if st.tzinfo is None or st > dt: return False
            except Exception: return False
    return dt <= datetime.now(timezone.utc)

def analyze_cards(payload):
    features=feature_bundle(payload)
    if payload.get("match_intensity") is not None: features["match_intensity"]=float(payload["match_intensity"])
    rows=payload.get("markets") or []
    results=[]
    if not _pit_valid(payload,features):
        for r in rows:
            results.append(CardModelResult(str(r.get("market")),str(r.get("selection")),float(r.get("line")),0.0,"UNKNOWN",None,None,None,None,1.0,0.0,"NO BET","PIT_INVALID",None,"CARD_BASELINE","cards-baseline-1").to_dict())
        return {"features":{k:(v.to_dict() if isinstance(v,CardFeature) else v) for k,v in features.items()},"expected_cards":None,"results":results}

    min_confidence=float(payload.get("min_confidence",0.20))
    for r in rows:
        market=str(r.get("market") or "").upper()
        if market not in CARD_MARKETS:
            continue
        mu,dist_model,confidence,var=_market_expected_cards(features,market,payload)
        if mu is None or confidence < min_confidence:
            results.append(CardModelResult(market,str(r.get("selection")),float(r.get("line")),0.0,"UNKNOWN",None,None,None,None,1.0,confidence,"NO BET","INSUFFICIENT_CARD_DATA",None,"CARD_BASELINE","cards-baseline-1").to_dict())
            continue

        live=bool(payload.get("phase","PRE").upper()=="LIVE")
        observed_total=int(payload.get("cards_observed",0) or 0)
        if market==CARD_HOME:
            observed=int(payload.get("home_cards_observed",0) or 0)
        elif market==CARD_AWAY:
            observed=int(payload.get("away_cards_observed",0) or 0)
        else:
            observed=observed_total
        minute=int(payload.get("minute",0) or 0)
        remaining_expected=None
        final_expected=mu
        if live:
            if minute < 0 or minute > 130: raise ValueError("INVALID_CARD_LIVE_MINUTE")
            remaining_fraction=max(0.0,(90.0-minute)/90.0)
            remaining_expected=max(0.0,mu*remaining_fraction)
            final_expected=observed+remaining_expected
            mu=final_expected
            # LIVE observations are part of the point-in-time state; no future
            # card events are used. Rebuild the distribution from current state.
            var=payload.get("live_variance",var)
            dist_model,_=_prob_distribution(mu,var)

        selection=str(r.get("selection") or "OVER").upper(); line=float(r.get("line")); odds=float(r.get("odds"))
        if odds<=1: continue
        _,probs=_prob_distribution(mu,var)
        pset=_settlement_probability(probs,line,selection)
        fp=fair_probability(pset); fair=fair_odds_from_probs(pset); ev=expected_value(odds,pset); edge=(fp-1/odds) if fp is not None else None
        uncertainty=max(0.0,1-confidence)
        min_edge=float(payload.get("min_edge",0.05)); min_ev=float(payload.get("min_ev",0.05)); min_odds=float(payload.get("min_odds",1.50)); preferred=float(payload.get("preferred_odds",1.66)); max_unc=float(payload.get("max_uncertainty",0.12))
        decision="NO BET"; reason=None; target=None
        if odds<min_odds: reason="ODDS_BELOW_MINIMUM"
        elif uncertainty>max_unc: reason="HIGH_UNCERTAINTY"
        elif edge is None: reason="NO_FAIR_PRICE"
        elif edge<min_edge:
            reason="INSUFFICIENT_EDGE"
            if fair and fair>odds and odds>=min_odds: decision="WAIT_FOR_PRICE";target=max(preferred,fair);reason="WAIT_FOR_PRICE"
        elif ev<min_ev:
            reason="INSUFFICIENT_EV"
            if fair and fair>odds and odds>=min_odds: decision="WAIT_FOR_PRICE";target=max(preferred,fair);reason="WAIT_FOR_PRICE"
        elif odds<preferred and (edge < float(payload.get("exception_edge",0.10)) or ev < float(payload.get("exception_edge",0.10))): reason="ODDS_IN_EXCEPTION_BAND"
        else: decision="BET"
        results.append(CardModelResult(market,selection,line,mu,dist_model,fp,fair,edge,ev,uncertainty,confidence,decision,reason,target,"CARD_BASELINE","cards-baseline-1").to_dict())

    live=bool(payload.get("phase","PRE").upper()=="LIVE")
    sorted_results=sorted(results,key=lambda x:(x["decision"]=="BET",x.get("ev") or -999),reverse=True)
    by_market={r["market"]:r.get("expected") for r in sorted_results if r.get("expected") is not None and r.get("expected")>0}
    return {"features":{k:(v.to_dict() if isinstance(v,CardFeature) else v) for k,v in features.items()},"expected_cards":next(iter(by_market.values()),None),"expected_cards_by_market":by_market,"phase":"LIVE" if live else "PRE","cards_observed":observed_total if live else None,"cards_remaining_expected":(max(0.0,next(iter(by_market.values()))-observed_total) if live and by_market else None),"final_expected_cards":(next(iter(by_market.values()),None) if live else None),"results":sorted_results}

