# V18 — FINAL MATRIX

| Área | Status | Evidência | Limitação |
|---|---|---|---|
| Dados reais | NOT AVAILABLE | acquisition attempts recorded | no external data |
| Historical Odds | NOT AVAILABLE | strict adapters/guards | no provider snapshots |
| Event Identity | PASS / PARTIAL | deterministic event identity | no cross-source real join |
| Data Quality | PASS (demo/control) | tests + gate | real dataset absent |
| PIT | PASS (controlled) | strict negative tests | real provider absent |
| Leakage | PASS (controlled) | regression suite | real sample absent |
| Features | PARTIAL | temporal feature modules | no real experiment |
| Models | PARTIAL | model suite | no champion |
| Calibration | PARTIAL | implementation | no OOS study |
| Walk Forward | PASS (controlled) | tests | insufficient real data |
| OOS | NOT AVAILABLE | no real OOS | data absent |
| Holdout | PASS / LOCKED | guard | not opened |
| Backtest | NOT AVAILABLE | engine present | no PIT odds |
| ROI | NOT AVAILABLE | no real ledger | data absent |
| CLV | NOT AVAILABLE | no valid close | data absent |
| Bootstrap | PASS (controlled) | cluster tests | no real sample |
| Benchmarks | NOT AVAILABLE | engine present | no real sample |
| Robustness | NOT AVAILABLE | modules present | no real sample |
| Paper Trading | PARTIAL | ledger present | no real stream |
| Backend | NOT EXECUTED | Java 21 | Maven absent |
| Frontend | PARTIAL | npm test executes with 0 tests | Vite/build unavailable |
| PostgreSQL | NOT AVAILABLE | migrations/compose | Docker absent |
| Redis | NOT AVAILABLE | compose | Docker absent |
| Docker | NOT AVAILABLE | command absent | runtime |
| Security | PASS | no secrets bundled | external secret manager not tested |
| Reproducibility | PASS (software level) | fingerprint/registry | no real experiment |
