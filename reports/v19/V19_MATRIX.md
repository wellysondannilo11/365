# V19 — FINAL MATRIX

| Area | Status | Evidence | Limitation |
|---|---|---|---|
| Scoreline Distribution | PASS | 70 tests | No real calibration |
| Fair Probability | PASS | unit/API tests | No real OOS |
| Fair Odds | PASS | sanity + settlement tests | Market-specific settlement coverage must grow with source coverage |
| Derived Markets | PASS | totals/BTTS/handicap tests | No real feed |
| Market Dislocation | PASS | PIT-aware API test | No real study |
| Price Movement | PASS | timeline test | No real timeline |
| CLV | PASS software | helper test | No valid provider close |
| Paper Trading | PASS | immutable ledger test | Paper/shadow only |
| PIT | PASS controlled | V18/V19 guards | No real provider dataset |
| OOS | NOT AVAILABLE | holdout untouched | Data absent |
| Real Backtest | NOT AVAILABLE | strict gate | Data absent |
| ROI / Edge | NOT AVAILABLE | no claims | Data absent |
| Frontend | PARTIAL | source updated, npm test 0 tests | Build blocked by Vite dependency |
| Backend | NOT EXECUTED | Maven unavailable | Runtime limitation |
| Docker | NOT AVAILABLE | command absent | Runtime limitation |
| Security | PASS | scan clean | External secret manager unavailable |
| Performance | PASS | 1,000 pricing calls / 8.08s | Not end-to-end production load |
