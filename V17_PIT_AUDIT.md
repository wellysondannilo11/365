# V17 — PIT AUDIT

## Controls preserved

The V16 PIT rule remains:

`available_at <= decision_time`

The V16 suite was rerun after V17 changes and passed.

## Negative controls

Existing tests cover future availability rejection and future-feature protections. Event atomicity and holdout isolation also remain protected.

## V17 acquisition policy

The acquisition layer does not infer provider availability from kickoff, ingestion time or local execution time. Provider-native timestamps are required for strict raw-record ingestion.

## Limitation

A real PIT betting dataset could not be constructed because no historical provider snapshot data was available in the execution environment.
