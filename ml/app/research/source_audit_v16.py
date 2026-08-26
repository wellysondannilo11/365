from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class SourceAudit:
    source:str
    real_data:str
    historical_odds:str
    timestamp_granularity:str
    pit_capability:str
    access:str
    cost:str
    role:str
    caveat:str

SOURCES=(
    SourceAudit('Football-Data.co.uk','YES','YES, but opening/pre-closing/closing sets rather than exact publication timestamps','No exact odds publication timestamp in CSV','NOT SUFFICIENT ALONE for strict odds PIT','CSV/Excel public download','Free','results/stats/historical cross-check','Use for historical outcomes and features; do not treat opening odds as exact decision-time availability.'),
    SourceAudit('The Odds API','YES','YES, timestamped snapshots','10-minute snapshots historically; 5-minute snapshots from Sep 2022 for relevant historical markets','YES, snapshot <= requested time','Paid historical endpoint','Paid','primary PIT bookmaker-odds candidate','Requires paid access/API key; coverage begins when the sport/bookmaker/market was covered.'),
    SourceAudit('TheStatsAPI','YES','YES, stored opening/last-seen; movement history on Growth+','Provider fields must be inspected in POC before claiming exact PIT','PARTIAL until provider response fields are verified','REST API/trial/paid','From $50/month; 7-day trial','football context + odds complement','Public docs advertise opening/last-seen and movement; exact decision-time reconstruction must be verified with real responses.'),
    SourceAudit('Betfair Historical Data','YES','YES, Exchange market/price/settlement history','Time-stamped historical data','YES for exchange feed','Purchased download + Historical Data API','Paid/purchased datasets','exchange validation / microstructure','Not equivalent to retail bookmaker odds; back/lay/volume/suspension semantics must be preserved.'),
    SourceAudit('StatsBomb Open Data','YES, selected competitions/seasons','NO bookmaker odds','Collection/update timestamps are not odds availability timestamps','NO for betting odds PIT','Public research data','Free under provider terms','football event/lineup feature complement','Selected competitions only; attribution requirements apply.'),
    SourceAudit('Flashscore','YES, broad public coverage','Odds comparison visible; historical PIT series not established here','Exact historical odds availability not established','NO as a critical PIT source in current architecture','Public web product; terms govern access','N/A','optional complementary reference only','Do not rely on scraping/bypass; absence of a reproducible timestamped history prevents use as primary PIT odds source.'),
)

def as_rows(): return [asdict(x) for x in SOURCES]
