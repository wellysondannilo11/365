import argparse, json
from pathlib import Path
from app.research.acquisition import acquire_first_available
from app.ingestion.raw_store import immutable_record, append_jsonl

p = argparse.ArgumentParser()
p.add_argument('--season', action='append', required=True)
p.add_argument('--league', default='E0')
p.add_argument('--out', default='data/raw/football_data')
a = p.parse_args()

out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
manifest = []
for season in a.season:
    try:
        df, attempts = acquire_first_available(season, a.league, out_dir=out)
        path = out / f'{a.league}_{season}.csv'
        rec = immutable_record(
            attempts[-1].source if attempts else 'UNKNOWN',
            f'{a.league}:{season}',
            {'url': str(df['_source_url'].iloc[0]) if len(df) and '_source_url' in df.columns else ''},
            schema_version='v16.0',
            dataset_version=f'football-data-{season}',
        )
        append_jsonl(out / 'raw_records.jsonl', [rec])
        manifest.append({
            'season': season,
            'league': a.league,
            'rows': len(df),
            'file': str(path),
            'status': 'ACQUIRED',
            'attempts': [x.__dict__ for x in attempts],
        })
    except Exception as exc:
        manifest.append({
            'season': season,
            'league': a.league,
            'rows': 0,
            'status': 'BLOCKED',
            'error': type(exc).__name__ + ': ' + str(exc),
        })

(out / 'acquisition_manifest.json').write_text(json.dumps(manifest, indent=2, default=str), encoding='utf-8')
print(json.dumps(manifest, indent=2, default=str))
