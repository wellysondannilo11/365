from __future__ import annotations
import hashlib,json
def fingerprint(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def replay_decision(expected,actual):return {'match':fingerprint(expected)==fingerprint(actual),'expected_hash':fingerprint(expected),'actual_hash':fingerprint(actual)}
