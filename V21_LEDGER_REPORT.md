# V21 LEDGER REPORT

V21 uses an append-only event ledger with a SHA-256 hash chain.

Event types include:

- `SIGNAL_CREATED`
- `SIGNAL_REJECTED`
- `POSITION_UPDATED`
- `POSITION_EXITED`
- `RESULT_SETTLED`

The original decision event is never mutated during settlement; settlement is a new event. Chain verification was tested and passed.

The ledger supports CSV-compatible data structures through XLSX export and exposes result, market, league and NO BET views.
