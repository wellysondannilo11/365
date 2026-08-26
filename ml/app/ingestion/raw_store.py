from __future__ import annotations
from pathlib import Path
import json, hashlib
from datetime import datetime, timezone


def payload_hash(payload) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str, separators=(',', ':')).encode()).hexdigest()


def immutable_record(source, source_id, payload, *, event_timestamp=None, source_timestamp=None,
                     available_at=None, schema_version='v16.0', dataset_version='v16.0',
                     provider=None, endpoint=None):
    now = datetime.now(timezone.utc).isoformat()
    return {
        'source': source,
        'source_id': str(source_id),
        'provider': provider or source,
        'endpoint': endpoint,
        'ingestion_timestamp': now,
        'event_timestamp': event_timestamp,
        'source_timestamp': source_timestamp,
        'available_at': available_at,
        'payload': payload,
        'raw_hash': payload_hash(payload),
        'schema_version': schema_version,
        'dataset_version': dataset_version,
    }


def append_jsonl(path, records):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    existing = set()
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            if not line:
                continue
            row = json.loads(line)
            existing.add(row['raw_hash'])
    added = 0
    with p.open('a', encoding='utf-8') as f:
        for r in records:
            h = r['raw_hash']
            if h in existing:
                continue
            f.write(json.dumps(r, ensure_ascii=False, default=str, sort_keys=True) + '\n')
            existing.add(h); added += 1
    return {'added': added, 'duplicates': len(records) - added, 'total_unique': len(existing)}
