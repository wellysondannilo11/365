# V22 AI/ML Audit

The V21 codebase contains statistical/ML components including logistic regression, random forest, gradient boosting, calibration and Dixon-Coles/Poisson-style pricing. These remain distinguishable from heuristics.

V22 does not falsely label the new feed scan as AI. The real-feed scan currently uses an explicit `MARKET_ONLY_BASELINE` probability derived from same-market de-vigging. This exists to provide a measurable baseline and operational plumbing; it is **not evidence of Robo edge**.

Model registry, dataset hashes, PIT and calibration infrastructure from V21 remain available. No production auto-training from every new result was introduced.
