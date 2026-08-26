# ROBO DA BET V15 Release

## Release status

**V15.0.0 — research infrastructure hardening release**

The V15 release preserves the existing application and adds quantitative/engineering controls. It does not claim real profitability because the supplied project still lacks a sufficient real historical PIT dataset.

## Validation

- Python tests: 44 passed.
- Python compileall: passed.
- Self-test: passed.
- Controlled walk-forward: passed.
- Event-group isolation: passed.
- Negative PIT/leakage tests: passed.
- Historical odds timestamp normalizer tests: passed.

## Known environment limitations

- Maven executable unavailable in the execution environment.
- Docker executable unavailable in the execution environment.
- Frontend dependency installation/build was not completed in this environment.

The backend Dockerfile was nevertheless corrected to use a reproducible multi-stage Maven build and the V15 artifact.

## Evidence level

**LEVEL 1 — infrastructure complete without real historical evidence.**
