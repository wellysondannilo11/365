# MASTER STAFF FINAL REPORT

## 1. Input / preservation
- Input ZIP: `ROBO_DA_BET_CONMEBOL_ROUND_2026-08-20.zip`
- Existing completed real canonical matches preserved: 4,864
- New completed historical matches materialized: 0
- Real money: `DISABLED`

## 2. Evidence state
- FOUND: 5 current-round structured source sets
- DOWNLOADED_BYTES: 0 (container network/DNS blocked)
- ACQUIRED_BYTES: 0
- MATERIALIZED_STRUCTURED_FIXTURE_CONTEXT: 5
- STRUCTURED_ODDS_OBSERVATIONS: 15
- PROCESSED_STRUCTURED_FIXTURE_CONTEXT: 5
- EXACT/VALID PIT: 0
- USED_IN_MODEL: 0
- Rule enforced: FOUND != DOWNLOADED != ACQUIRED != MATERIALIZED != PROCESSED != PIT_VALIDATED != USED_IN_MODEL

## 3. Historical dataset

- Countries: 4
- Competitions: 8
- Seasons: 9
- MEN matches: 4864
- WOMEN matches: 0
- H2H records: 4864
- Cards rows: 2441
- Corners rows: 2441
- Referee rows: 2441
- Canonical odds rows: 2046
- Timestamped canonical odds: 0
- Canonical PIT validated: 0

## 4. Current CONMEBOL round — 20/08/2026

- Games discovered and verified: 5
- Libertadores: 2
- Sudamericana: 3

### LDU Quito x Mirassol
- Competition: CONMEBOL Libertadores
- Aggregate: 1-1
- Needs: WIN / WIN
- Odds KTO recorded 18/08: 1.66 / 3.60 / 5.30
- PIT: DATE_LEVEL_PIT
- Model status: INSUFFICIENT_DATA
- Decision: NO_BET / WAIT

### Corinthians x Rosario Central
- Competition: CONMEBOL Libertadores
- Aggregate: 0-0
- Needs: WIN_OR_DRAW / WIN
- Odds KTO recorded 18/08: 1.90 / 3.00 / 4.75
- PIT: DATE_LEVEL_PIT
- Model status: INSUFFICIENT_DATA
- Decision: NO_BET / WAIT

### Olimpia x Vasco da Gama
- Competition: CONMEBOL Sudamericana
- Aggregate: 0-0
- Needs: WIN / WIN_OR_DRAW
- Odds KTO recorded 18/08: 2.28 / 3.15 / 3.20
- PIT: DATE_LEVEL_PIT
- Model status: INSUFFICIENT_DATA
- Decision: NO_BET / WAIT

### Macará x Santos
- Competition: CONMEBOL Sudamericana
- Aggregate: 1-2 Santos
- Needs: WIN_BY_2_FOR_DIRECT_QUALIFICATION / DRAW_OR_WIN
- Odds KTO recorded 18/08: 2.75 / 3.20 / 2.50
- PIT: DATE_LEVEL_PIT
- Model status: INSUFFICIENT_DATA
- Decision: NO_BET / WAIT

### Botafogo x Cienciano
- Competition: CONMEBOL Sudamericana
- Aggregate: 1-6 Cienciano
- Needs: WIN_BY_6_FOR_DIRECT_QUALIFICATION / LOSE_BY_4_OR_LESS_TO_ADVANCE
- Odds KTO recorded 18/08: 1.10 / 9.50 / 19.00
- PIT: DATE_LEVEL_PIT
- Model status: INSUFFICIENT_DATA
- Decision: NO_BET / WAIT

## 5. Market / value gate

- Current-round odds are date-level only. Exact capture timestamp and timezone were not proven.
- Therefore no odds row is eligible for exact/valid PIT value assessment.
- No model-vs-market edge was promoted.
- TOP_VALUE_BET: `NONE`
- PAPER_CANDIDATES: 0
- EDGE_STATUS: `EDGE_NOT_DETERMINED`

## 6. Model validation

{
  "status": "CALCULATED",
  "n": 3604,
  "train_n": 2522,
  "validation_n": 541,
  "holdout_n": 541,
  "validation": {
    "log_loss": 0.6673840347182913,
    "brier": 0.23733201583081237,
    "roc_auc": 0.5949498346505241
  },
  "holdout": {
    "log_loss": 0.6645880768964111,
    "brier": 0.23610349916921494,
    "roc_auc": 0.5869287357627745
  },
  "walk_forward": [
    {
      "train_n": 200,
      "test_n": 851,
      "log_loss": 0.6835215220109488,
      "brier": 0.24518611511693814,
      "roc_auc": 0.5233309606932629
    },
    {
      "train_n": 1051,
      "test_n": 851,
      "log_loss": 0.6739040475636839,
      "brier": 0.24054544413719225,
      "roc_auc": 0.5854919368432882
    },
    {
      "train_n": 1902,
      "test_n": 851,
      "log_loss": 0.6669136725461599,
      "brier": 0.2370768611557364,
      "roc_auc": 0.6045218096246088
    },
    {
      "train_n": 2753,
      "test_n": 851,
      "log_loss": 0.659521489285191,
      "brier": 0.23360315181487773,
      "roc_auc": 0.6041925931047198
    }
  ]
}

These are predictive research metrics only. They do not establish market edge or ROI.

## 7. Context intelligence status

- Knockout/aggregate context was materialized for all five current-round fixtures.
- H2H historical feature engine is temporal and only uses prior canonical observations.
- Rivalry registry is empty rather than fabricated.
- Player, injury, lineup and suspension datasets remain unavailable in the historical canonical package.
- Altitude was explicitly recorded for Macará–Santos as a sourced context observation; no causal effect was promoted.

## 8. Negative findings / limitations

- Bulk 2020–2026 acquisition was blocked by runtime network/DNS restrictions; no fake coverage was added.
- 2026 current completed-match history is not materialized in the canonical historical dataset.
- Exact timestamped PIT odds are absent.
- Historical LIVE snapshots are absent.
- xG/shots/SOT/events/player/lineup/injury/suspension history is absent or insufficient.
- Women data are insufficient and no women rows were mixed into the men model.
- Rivalry effects remain unvalidated.

## 9. Tests

- `python -m compileall -q ml scripts tests`: PASS
- `pytest -q`: PASS (all collected tests)
- `scripts/master_staff_validation.py`: PASS
- security scan: PASS
- self-test: PASS
- `unzip -t` final package: required and executed before delivery
- SHA-256: generated for final package

## 10. Scientific status

ENGINEERING_STATUS: COMPLETE_ON_INPUT_PACKAGE
EMPIRICAL_DATA_STATUS: PRESERVED + 5 NEW STRUCTURED CURRENT-ROUND CONTEXT RECORDS
PREDICTIVE_STATUS: OOS/HOLDOUT/WALK-FORWARD EXPERIMENTAL
MARKET_STATUS: DATE_LEVEL_PIT_ONLY / NOT MARKET VALIDATED
LIVE_STATUS: NOT HISTORICALLY VALIDATED
PAPER_TRADING_STATUS: 0 NEW CANDIDATES
EDGE_STATUS: `EDGE_NOT_DETERMINED`
ROUND_STATUS: `INSUFFICIENT_DATA`
REAL_MONEY: `DISABLED`