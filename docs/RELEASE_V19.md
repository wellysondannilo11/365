# Release V19 — Fair Pricing & Market Intelligence

## Scope

V19 adds a reusable sports market pricing core on top of the V18 research/PIT architecture.

## Main additions

- Scoreline distribution.
- Optional Dixon-Coles adjustment.
- Fair probability and fair odds.
- Derived totals/BTTS/double-chance/handicap markets.
- Settlement-aware EV/fair odds.
- Market normalization and de-vig.
- Consensus and market dislocation.
- Price movement and CLV helpers.
- Immutable paper/shadow signal ledger.
- PRE/LIVE-compatible pricing engine interface.
- V19 API endpoints.
- Market Intelligence frontend surface.
- V19 validation, acquisition, security and performance evidence.

## Scientific status

The system remains **LEVEL 1** because no real PIT historical bookmaker dataset was available. V19 does not claim sustainable betting edge.

## Production status

**SAFE WITH LIMITATIONS.** Python research/pricing layer is validated. Full Spring/Docker/frontend production validation remains blocked by runtime tooling/dependency availability.

## Live status

Real-money execution remains disabled. V19 only prepares the pricing core and paper/shadow interfaces.
