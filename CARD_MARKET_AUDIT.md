# CARD MARKET AUDIT

## Scope
Card Markets are integrated into the existing V25 architecture.

Supported identifiers: `CARD_TOTALS`, `CARD_HOME`, `CARD_AWAY`.
Selections: OVER / UNDER.
Lines: integer / half / quarter when supplied.

## Quantitative correction
The prior implementation incorrectly reused one total-card expectation for all three markets. The final package now uses:
- CARD_HOME: home-side evidence;
- CARD_AWAY: away-side evidence;
- CARD_TOTALS: home + away when both are available, with referee/H2H total fallback only when side-specific evidence is unavailable.

LIVE also distinguishes `home_cards_observed`, `away_cards_observed` and total `cards_observed`.

## PIT
Both source timestamp and capture timestamp are checked against decision time. Future timestamps are blocked.

## Model
Poisson / Negative Binomial selection remains a configurable engineering mechanism. No empirical claim of superiority is made.

## Provider
The provider-neutral `CardDataProvider` and API-Football adapter remain optional. The adapter labels timestamp evidence `CAPTURED_AT_ONLY` and does not manufacture historical publication timestamps.

## Scientific evidence
No real card observations were available in the audit runtime. Therefore referee value, team-card value, H2H value, importance, intensity, LIVE value, ROI, CLV and edge are all `NOT DETERMINED`.
