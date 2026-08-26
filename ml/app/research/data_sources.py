from dataclasses import dataclass

@dataclass(frozen=True)
class SourceAssessment:
    name:str; coverage:str; historical_odds:str; timestamps:str; access:str; cost:str; status:str; notes:str

SOURCES=(
    SourceAssessment('Football-Data.co.uk','Many seasons; major European and additional leagues','Opening/pre-closing and closing sets for supported seasons','No exact odds publication timestamp in CSV; opening set is prematch-bounded','Public CSV/Excel','Free','REAL_SOURCE_AVAILABLE','Useful for historical results, match stats and opening/closing odds; strict exact PIT requires timestamp enrichment.'),
    SourceAssessment('The Odds API','Historical snapshots from supported coverage','Historical snapshots','Exact snapshot timestamps; closest snapshot at or before requested time','Paid historical endpoint','Paid plan','EXTERNAL_DEPENDENCY','Strong candidate for exact PIT odds when credentials and quota are available.'),
    SourceAssessment('TheStatsAPI','1,000+ advertised football competitions; plan-dependent history','Historical/opening/last-seen odds advertised; exact PIT semantics require POC','Provider response timestamps must be mapped and validated; do not infer availability','API/trial/paid plan','Paid/trial depending plan','EXTERNAL_DEPENDENCY','Sports/statistics/xG/odds complement; verify exact timestamp fields before strict PIT.'),
    SourceAssessment('StatsBomb Open Data','Selected competitions/seasons; event and lineup JSON','No bookmaker odds','Event-level collection timestamps are not equivalent to odds availability timestamps','Public GitHub JSON under provider terms','Free for selected data','REAL_SOURCE_AVAILABLE','Strong for football event/lineup feature research; not an odds source and requires source attribution.'),
    SourceAssessment('Flashscore','Broad football coverage','Not selected as a historical odds source','Exact PIT odds availability not established for this architecture','Public web product; access governed by provider terms','N/A','COMPLEMENT_ONLY','Use only legitimate supported access; no scraping bypass, CAPTCHA bypass or rate-limit circumvention.'),
    SourceAssessment('Betfair Historical Data','Exchange historical data from May 2015','Timestamped exchange market data','Timestamped feed','Purchase/download','Paid','EXTERNAL_DEPENDENCY','Strong candidate for exact exchange-price research and market microstructure.'),
)
