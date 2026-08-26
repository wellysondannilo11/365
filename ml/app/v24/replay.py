from __future__ import annotations
import json,hashlib

def deterministic_fingerprint(record):
    return hashlib.sha256(json.dumps(record,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def compare(expected,actual):
    return {"match":deterministic_fingerprint(expected)==deterministic_fingerprint(actual),
            "expected_hash":deterministic_fingerprint(expected),"actual_hash":deterministic_fingerprint(actual)}
