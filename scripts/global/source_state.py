from __future__ import annotations
VALID = ('DISCOVERED','ACCESSIBLE','DOWNLOADED','MATERIALIZED','VALIDATED','PROCESSED','USED_IN_MODEL','BLOCKED','FAILED')
ORDER = {s:i for i,s in enumerate(('DISCOVERED','ACCESSIBLE','DOWNLOADED','MATERIALIZED','VALIDATED','PROCESSED','USED_IN_MODEL'))}

def promote(current: str, target: str) -> str:
    if current not in VALID or target not in VALID:
        raise ValueError('invalid source state')
    if target in ('BLOCKED','FAILED'):
        return target
    if current in ('BLOCKED','FAILED'):
        raise ValueError(f'cannot promote terminal state {current}')
    if ORDER[target] < ORDER[current]:
        raise ValueError(f'non-monotonic state transition {current}->{target}')
    return target

def is_materialized(record: dict) -> bool:
    return record.get('state') in {'MATERIALIZED','VALIDATED','PROCESSED','USED_IN_MODEL'} and bool(record.get('materialized'))
