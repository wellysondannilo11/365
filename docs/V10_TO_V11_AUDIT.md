# V10 → V11 audit

V10 archive contained 68 entries, but 18 of those were cache artifacts under `.pytest_cache`/`__pycache__`.
Therefore V10 had 50 functional files. The apparent reduction to 58 V11 entries was not a loss of ten
functional files; it was caused by cache cleanup, path normalization and replacement of some files.

V11 is rebuilt from the V10 functional base rather than from the weaker interim scaffold. Existing V10
adapters, models, live engine, risk, ledger, Telegram, DB, frontend, tests and training scripts are retained.
V11 adds migrations, frontend Docker build, performance dashboard endpoint, explicit champion/challenger gate,
ranking helper, and audit documentation.
