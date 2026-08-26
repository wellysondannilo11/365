# V25 AI / ML Audit

**Scientific status: NOT DETERMINED.**

The project retains existing ML infrastructure and V25 accepts either:

1. an explicitly supplied scoreline distribution; or
2. an explicitly supplied `model_probability`.

If neither is present, V25 uses the market-only baseline. It does not fabricate ML probabilities.

Temporal/OOS/holdout infrastructure from previous versions remains preserved. No real-data retraining was performed because there is no qualifying real PIT dataset in this runtime.

**Conclusion:** ML infrastructure exists, but V25 real observation is correctly classified as **baseline-first unless a validated model is supplied**.
