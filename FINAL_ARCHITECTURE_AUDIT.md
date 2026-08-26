# FINAL ARCHITECTURE AUDIT — V26–V28 Consolidated

The V25 architecture was preserved and consolidated rather than recreated.

### Core flow
REAL PROVIDER → INGESTION → NORMALIZATION → EVENT IDENTITY → TIMESTAMP/PIT → QUALITY → SNAPSHOT → FEATURES/BASELINE → FAIR PRICE → MARKET EXPRESSION → VALUE/RISK → BET/NO BET/WATCH → PAPER/SHADOW → LIVE REPRICE → POSITION MANAGEMENT → SETTLEMENT → DATASET → ANALYTICS/DASHBOARD.

### Corrections in final pass
- PostgreSQL primary empirical dataset path added.
- JSONL retained as forensic mirror/fallback.
- Deterministic observation identity added.
- Portfolio risk limits integrated into V25 decision path.
- WATCH/target-price path added.
- Session lifecycle and observation runner added.

External runtime remains unverified where services/credentials were unavailable.
