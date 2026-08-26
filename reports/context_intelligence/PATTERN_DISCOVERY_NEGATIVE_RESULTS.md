| topic                   | status            | reason                                                                                             |
|:------------------------|:------------------|:---------------------------------------------------------------------------------------------------|
| Player impact           | INSUFFICIENT_DATA | No real player-level minutes/xG/xA/injury/suspension dataset materialized in current ZIP.          |
| Injury return effect    | INSUFFICIENT_DATA | No timestamped player injury/return records.                                                       |
| Motivation/must-win     | INSUFFICIENT_DATA | No pre-match standings/qualification-state dataset sufficient to reconstruct objective motivation. |
| Derby/rivalry           | INSUFFICIENT_DATA | No auditable rivalry registry/source materialized; conservative classifier remains UNKNOWN.        |
| LIVE pattern validation | INSUFFICIENT_DATA | No historical LIVE snapshot dataset with ordered timestamps is materialized.                       |
| PIT edge                | NOT_DETERMINED    | Current odds are NON_PIT or PIT_DATE_ONLY; no exact decision-time odds.                            |
| xG patterns             | INSUFFICIENT_DATA | Canonical xG fields are fully missing in current materialized dataset.                             |