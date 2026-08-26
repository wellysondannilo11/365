# V17 — DATA SNOOPING AUDIT

## Selection controls

- Walk-forward temporal ordering is preserved.
- Candidate model selection is validation-only in the existing research pipeline.
- Test windows are not used for model selection.
- Holdout remains locked.
- Existing event atomicity prevents splitting one event across folds.

## Experiment count in this execution

No real betting model experiment was promoted to evidence because the real-data gate was blocked. The V17 execution therefore avoids selecting a profitable-looking configuration from the demo fixture.

## Risk still requiring future audit

When real data arrives, the registry must record every candidate model, feature set, threshold and market tested before any final claim. Multiple-testing correction must be applied to the family of hypotheses rather than only the winning result.
