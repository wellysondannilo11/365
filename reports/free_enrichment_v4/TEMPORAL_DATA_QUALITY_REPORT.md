# TEMPORAL DATA QUALITY REPORT V4

The canonical dataset currently has date-level historical source timing for the local Football-Data-derived statistics. These records are not promoted to Exact PIT.

Rules enforced by the V4 pipeline:
- feature_timestamp <= decision_timestamp for pre-match use;
- post-kickoff evidence is POSTMATCH_ONLY;
- publication/retrieval timestamps are preserved separately;
- missing timestamps never become synthetic timestamps;
- DATE_LEVEL is never promoted to EXACT_PIT.

Current Exact PIT: 0.
Current Date-level PIT: 30.
Current non-PIT: 6,368.
