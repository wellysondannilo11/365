from __future__ import annotations
from collections import defaultdict
from statistics import median
from ..market import devig

def market_consensus(rows):
    """De-vig each bookmaker independently, then take a median probability per selection.

    This avoids the V23 error mode of de-vigging duplicated selections from different
    bookmakers as though they were one book.
    """
    books=defaultdict(list)
    for r in rows:
        try:
            price=float(r["odds"])
            if price>1: books[(str(r.get("event_id")),str(r.get("market")),r.get("line"),str(r.get("bookmaker")))].append(r)
        except Exception: pass
    probs=defaultdict(list)
    for key,grp in books.items():
        prices=[float(x["odds"]) for x in grp]
        if len(prices)<2: continue
        fair=devig(prices)
        for r,p in zip(grp,fair):
            probs[(key[0],key[1],key[2],str(r.get("selection"))) if False else (key[0],key[1],key[2],str(r.get("selection")))].append(float(p))
    out={}
    for key,vals in probs.items():
        out[key]=float(median(vals))
    return out

def enrich(rows):
    consensus=market_consensus(rows)
    out=[]
    for r in rows:
        key=(str(r.get("event_id")),str(r.get("market")),r.get("line"),str(r.get("selection")))
        p=consensus.get(key)
        x=dict(r)
        x["market_probability"]=1/float(r["odds"]) if float(r["odds"])>1 else None
        x["probability"]=p
        x["model_type"]="MARKET_ONLY_BASELINE"
        x["fair_probability"]=p
        x["fair_odds"]=1/p if p and p>0 else None
        x["data_quality"]=100
        x["calibration"]=1.0
        x["uncertainty"]=0.05 if p is not None else 1.0
        x["market_quality"]=1.0 if p is not None else 0.0
        x["robustness"]=1.0
        x["model_agreement"]=1.0
        x["pit_ok"]=p is not None
        x["sample_size"]=len([z for z in rows if str(z.get("event_id"))==str(r.get("event_id")) and str(z.get("market"))==str(r.get("market"))])
        out.append(x)
    return out
