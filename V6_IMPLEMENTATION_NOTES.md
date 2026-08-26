# V6 implementation notes

This V6 layer extends the existing V5 without replacing it. It adds real roster acquisition from the public footballcsv/cache.footballsquads dataset, source artifact manifests, V6 coverage/gap reports, and a resumable provider entry point. It intentionally does not infer lineups, injuries, player-match statistics, xG or PIT from roster data.

Run from project root:

```bash
python scripts/global/run_free_global_enrichment_v6.py
pytest -q
python -m compileall scripts ml
unzip -t GLOBAL_DATASET_V6_COMPLETE.zip
```
