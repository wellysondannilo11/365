# V19 — SYSTEM AUDIT

| Component | Status | Evidence | Limitation |
|---|---|---|---|
| Pricing engine | PASS | 70-test suite + API tests | No real empirical validation |
| Scoreline distribution | PASS | normalization/Dixon-Coles tests | No real calibration |
| Fair probability | PASS | derived-market tests | No real OOS |
| Fair odds | PASS | sanity tests | Exotic settlement requires market-specific rules |
| Derived markets | PASS | totals/BTTS/handicap tests | Market availability depends on source |
| Market normalization | PASS | unit tests | No live provider feed |
| De-vig | PASS | mathematical tests | Consensus is descriptive, not truth |
| Market dislocation | PASS | PIT-aware API tests | No real market study |
| Price movement | PASS | timeline tests | No real snapshot series |
| CLV | PASS (software) | helper tests | No provider-native closing series |
| Paper ledger | PASS | immutable dataclass + persistence test | Paper only |
| PIT | PASS (controlled) | V18 + V19 tests | No real provider dataset |
| Leakage | PASS (controlled) | existing V18 regression suite | No real study |
| OOS | NOT AVAILABLE | holdout stayed locked | No real data |
| Holdout | PASS / LOCKED | existing contract | Not evaluated |
| Real backtest | NOT AVAILABLE | strict gate | No real odds |
| ROI/edge evidence | NOT AVAILABLE | deliberately not fabricated | No real sample |
| Backend | NOT EXECUTED | Maven unavailable | Runtime limitation |
| Frontend tests | PASS, 0 tests | npm command executed | No actual test cases |
| Frontend build | NOT EXECUTED | Vite absent | npm install timed out |
| PostgreSQL | NOT AVAILABLE | Docker absent | Runtime limitation |
| Redis | NOT AVAILABLE | Docker absent | Runtime limitation |
| Docker | NOT AVAILABLE | command absent | Runtime limitation |
| Security | PASS | secret scan + env example | External secret manager not testable |
| Performance | PASS | 1,000 pricing runs | Real end-to-end load not measured |
| Reproducibility | PASS (software) | deterministic tests/fingerprints | No real experiment |
