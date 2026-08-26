# V18 — V17 → V18 REGRESSION AUDIT

## Result

**NO KNOWN CORRECTABLE REGRESSION FOUND IN THE EXECUTABLE PYTHON REGRESSION SURFACE.**

Final V18 Python suite: **54 passed**.

V16 self-test: PASS.

Python compileall: PASS.

## Quantitative regression

Validated again:

- PIT guard
- leakage controls
- event atomicity
- temporal validation
- holdout lock
- calibration implementation
- cluster bootstrap implementation
- ROI semantics
- historical odds timestamp separation
- empirical runner
- benchmark/robustness modules
- paper ledger modules

## V18 fixes applied

1. Strict PIT odds mode now refuses to infer `available_at` when absent.
2. Strict PIT rejects source records explicitly marked as having no exact timestamp.
3. Football-Data event identity generation was made deterministic using date/time/home/away instead of a mutable row index.
4. `PITRecord.validate()` no longer dereferences `source_time=None`.
5. V18 acquisition and full-system validation artifacts were added.
6. API/backend/frontend version labels were advanced to 18.0.0 where applicable.

## Software limitations

- Maven unavailable in runtime.
- Docker unavailable in runtime.
- Frontend has zero discovered Node tests and Vite is not installed, so production build was not executed.

These limitations are explicitly not marked PASS.
