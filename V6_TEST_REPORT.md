# V6 TEST REPORT

- compileall: PASS
- snapshot integrity: PASS
- pytest: TIMEOUT (the suite reached 100% progress but did not emit its final summary before the execution timeout; therefore not promoted to PASS)
- source checksum validation: PASS for all 3 newly downloaded artifacts
- entity resolution: PASS for 59 roster entities
- temporal validation: PASS for the new roster layer classification; no roster data injected into prematch snapshots
- PIT audit: PASS / no Exact PIT promotion
- leakage audit: PASS for new layer
- provenance validation: PASS for new artifacts
- gender separation: PASS / new data is men's Brazil Série A 2024 only
- security scan: NOT_RUN (no dedicated scanner dependency available in the runtime)
- unzip -t: PENDING final ZIP generation
