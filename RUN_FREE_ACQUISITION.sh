#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python scripts/global/run_free_data_enrichment.py
python scripts/global/free_source_audit.py
python scripts/global/verify_snapshot_integrity.py
