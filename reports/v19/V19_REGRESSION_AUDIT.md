# V19 — V18 → V19 REGRESSION AUDIT

## Result

**NO KNOWN CORRECTABLE REGRESSION FOUND IN THE EXECUTABLE PYTHON SURFACE.**

V18's reported baseline was 54 Python tests. The V19 suite executes **70 tests**, including the original V18 hardening tests plus new pricing, settlement, PIT dislocation, API and paper-ledger tests.

## Passed controls

- PIT timestamp rejection
- undefined availability rejection
- event/temporal controls from V18
- holdout lock
- calibration implementation
- bootstrap implementation
- historical odds normalization
- V19 scoreline normalization
- fair odds
- settlement-aware EV
- market de-vig
- decision-time filtering
- immutable paper signal

## Environment limitations carried forward

- Maven unavailable.
- Docker unavailable.
- Frontend dependencies unavailable.
- Frontend npm test command discovers zero tests.
- Frontend production build cannot execute because Vite is not installed; an attempted `npm install` timed out under the runtime network restriction and was cleaned up.

These are execution limitations, not silently marked PASS.
