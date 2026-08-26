from __future__ import annotations
from collections import Counter
from time import perf_counter
from statistics import mean

REQUIRED_METRICS = (
    "events_seen","events_valid","events_rejected","snapshots_received",
    "snapshots_rejected","signals_created","signals_rejected","no_bet",
    "bets_selected","positions_open","positions_closed","reversals",
    "provider_errors","stale_feed","PIT_rejections","model_latency",
    "pricing_latency","decision_latency",
)

class V25Observability:
    def __init__(self):
        self.counters=Counter()
        self.latencies={k:[] for k in ("provider_latency","model_latency","pricing_latency","decision_latency")}
    def inc(self,name,n=1):
        self.counters[name]+=int(n)
    def observe_ms(self,name,elapsed_seconds):
        if name in self.latencies:self.latencies[name].append(round(elapsed_seconds*1000,3))
    def timer(self,name):
        start=perf_counter()
        class _Timer:
            def __enter__(_): return _
            def __exit__(_,exc_type,exc,tb):
                self.observe_ms(name,perf_counter()-start)
        return _Timer()
    def snapshot(self):
        out={k:int(self.counters.get(k,0)) for k in REQUIRED_METRICS}
        out.update({k:({"count":len(v),"avg_ms":mean(v) if v else None,"max_ms":max(v) if v else None}) for k,v in self.latencies.items()})
        return out
