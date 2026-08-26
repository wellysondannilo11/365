"""V24 production-readiness and empirical observation layer.

V24 preserves the V20-V23 engines and adds a stricter operational boundary:
real provider -> PIT quality -> market baseline/pricing -> selective decision ->
paper/shadow -> immutable empirical dataset -> replay/analytics.
Real-money execution is intentionally unavailable.
"""
VERSION="24.0.0"
REAL_MONEY_ENABLED=False
