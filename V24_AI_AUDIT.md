# V24 AI Audit

V24 deliberately does not fabricate a new ML model.

Existing V19–V21 model/ML governance is preserved. V24's real-feed scan uses an explicit `MARKET_ONLY_BASELINE`.

The baseline:
- de-vigs each bookmaker independently;
- computes a median consensus probability by selection;
- prices the offered market against that consensus;
- records fair probability, fair odds, edge and EV.

This is a research baseline, not evidence that AI is superior.

Real training/OOS/calibration/promotion remains dependent on sufficient real PIT data and is therefore **NOT DETERMINED**.
