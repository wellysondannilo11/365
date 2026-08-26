# V21 REGRESSION AUDIT

## Test execution

| Check | Status | Evidence |
|---|---|---|
| Full Python pytest suite | PASS | **96 tests passed** |
| V20 regression tests | PASS | Existing V20 tests included in full suite |
| V21 tests | PASS | Feed, quality, controls, ledger, notifications, service, API, live monitor |
| Python compileall | PASS | `python -m compileall -q ml scripts tests` |
| Existing self-test | PASS | `python scripts/self_test.py` |
| Existing V19 security scan | PASS | no findings |
| Controlled end-to-end PAPER flow | PASS | decision -> immutable events -> settlement -> CLV -> performance -> XLSX |
| Frontend npm test | NOT EXECUTED AS QUALITY EVIDENCE | command exits 0 but discovers 0 tests |
| Frontend production build | BLOCKED BY ENVIRONMENT | `vite: not found` |
| Maven/backend test | BLOCKED BY ENVIRONMENT | `mvn: command not found` |
| Docker config/build | BLOCKED BY ENVIRONMENT | `docker: command not found` |
| Real feed smoke test | NOT EXECUTED | provider credentials not configured |

## Regression conclusion

No Python regression was detected. The original V20 suite remains green after V21 changes.
