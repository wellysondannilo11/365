# V16 V15→V16 FINAL MATRIX

| Area | V15 | V16 | Status | Evidence |
|---|---|---|---|---|
| Real Data | Ready | Acquisition/quality layer | BLOCKED | No credentials/network |
| Data Quality | V15 gates | Expanded fail-closed profiler | PASS | 49 tests |
| Event Identity | Atomic temporal unit | Preserved | PASS | regression tests |
| PIT | Strict | Provider snapshot + feature lineage | PASS | negative tests |
| Leakage | Controlled | Preserved + real-data gate | PASS | tests |
| Features | Historical | Expanded form/context features | PASS | feature tests |
| Historical Odds | Normalizer | Snapshot/inner-clock separation | PASS | adapter tests |
| Models | Candidates | Empirical runner | PASS | controlled fixture |
| Calibration | Binary | Preserved | PASS | calibration tests |
| Walk Forward | Event-aware | Preserved | PASS | tests |
| OOS | Prepared | Runner ready | NOT AVAILABLE | no real data |
| Holdout | Locked | Preserved | PASS | tests |
| Backtest | Prepared | Preserved | NOT AVAILABLE | no real PIT odds |
| ROI | Stake-based | Preserved | PASS | tests |
| CLV | Conditional | Conditional | NOT AVAILABLE | no real closing line |
| Bootstrap | Event cluster | Preserved | PASS | tests |
| Benchmarks | Framework | Framework | NOT AVAILABLE | no real sample |
| Robustness | Limited | Group/sensitivity utilities | PASS | unit tests |
| Paper Trading | Architecture | Signal ledger | READY | no real live execution |
| Backend | V15 | V16 + optional API key | NOT EXECUTED | Maven unavailable |
| Frontend | V15 | V16 label/version | NOT EXECUTED | npm install timeout |
| Docker | V15 | Compose syntax fixed | PARTIALLY VALIDATED | YAML parse only |
| Tests | 44 | 49 | PASS | pytest |
| Security | Gate identified | Optional API-key gate | PASS by static inspection | runtime build unavailable |
| Reproducibility | Registry | Fingerprinting + registry | PASS | code/tests |
