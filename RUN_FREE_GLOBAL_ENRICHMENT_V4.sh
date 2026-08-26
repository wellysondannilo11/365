#!/usr/bin/env bash
set -euo pipefail
python scripts/global/run_free_global_enrichment_v4.py
python scripts/global/run_free_data_enrichment.py || true
python -m pytest -q
python -m compileall -q .
python scripts/global/verify_snapshot_integrity.py
