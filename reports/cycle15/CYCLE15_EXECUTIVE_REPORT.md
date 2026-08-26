# CYCLE 15 — EXECUTIVE REPORT

## Engineering

- Candidate used: V16 Cycle 4 physical archive.
- Candidate SHA-256: `5b864b50be953fe873b85cf08ed062b482f2efdc511732e2258fb3badb9933be`.
- V8 baseline preserved: `608f587b628b8d09c961519e9ca3ec5a664dd68e3091de4c0371937a2adcd967`.
- Exact-PIT contract, SharpAPI/BeatTheBookie adapters, H005 evaluator, prospective collector and production lock implemented.

## Economic evidence

- Exact PIT events: **0**
- Exact PIT observations: **0**
- Real paper bets: **0**
- Valid CLV: **0**
- Edge: **NOT_PROVEN**

The local 12,216 historical odds rows remain NON_PIT. A separate research-only H005 run is recorded without promotion.

## H005 research-only

{
  "status": "NON_PIT_RESEARCH_ONLY",
  "hypothesis_id": "H005_CROSS_BOOK_DISPERSION_V1",
  "frozen_threshold": 0.02,
  "bets": 1037,
  "events": 1008,
  "net_units": 41.49999999999999,
  "roi": 0.040019286403085816,
  "clv_proxy_mean": 0.019429898902219685,
  "max_drawdown": 32.11,
  "bootstrap_ci95": [
    -0.0652430086788814,
    0.15030183220829302
  ],
  "walk_forward": [
    {
      "fold": 1,
      "bets": 208,
      "net_units": -17.97,
      "roi": -0.08639423076923076
    },
    {
      "fold": 2,
      "bets": 208,
      "net_units": 31.319999999999993,
      "roi": 0.15057692307692305
    },
    {
      "fold": 3,
      "bets": 207,
      "net_units": 21.31,
      "roi": 0.10294685990338164
    },
    {
      "fold": 4,
      "bets": 207,
      "net_units": -1.6800000000000015,
      "roi": -0.008115942028985515
    },
    {
      "fold": 5,
      "bets": 207,
      "net_units": 8.52,
      "roi": 0.04115942028985507
    }
  ]
}

These figures are **NON_PIT_RESEARCH_ONLY** and do not count as economic validation.

## Acquisition

The runtime cannot resolve external DNS, so provider-native bytes could not be downloaded. The system now has explicit adapters for SharpAPI point-in-time snapshots and the BeatTheBookie odds-series format, plus a fail-closed prospective collector. SharpAPI's public dataset documents 6,132 World Cup rows captured at a provider timestamp across 20 sources, while BeatTheBookie documents continuous odds series with `odds_datetime`; both are recorded as legitimate ingestion routes, not as locally materialized evidence.

## Decision

`EDGE = NOT_PROVEN`
`REAL_MONEY = DISABLED`
`PRODUCTION_TRADING_APPROVED = FALSE`
