from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json

class HashChain:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def _rows(self):
        if not self.path.exists(): return []
        return [json.loads(x) for x in self.path.read_text(encoding="utf-8").splitlines() if x.strip()]
    def append(self,row):
        row=dict(row); row.setdefault("created_at",datetime.now(timezone.utc).isoformat())
        prior=self._rows()
        row["previous_hash"]=prior[-1]["row_hash"] if prior else None
        canonical=json.dumps(row,sort_keys=True,separators=(",",":"),default=str)
        row["row_hash"]=hashlib.sha256(canonical.encode()).hexdigest()
        with self.path.open("a",encoding="utf-8") as f:f.write(json.dumps(row,sort_keys=True,separators=(",",":"),default=str)+"\n")
        return row
    def rows(self): return self._rows()
    def verify(self):
        prev=None
        for i,row in enumerate(self._rows()):
            if row.get("previous_hash")!=prev: return {"valid":False,"index":i,"reason":"BROKEN_PREVIOUS_HASH"}
            check=dict(row); check.pop("row_hash",None)
            canonical=json.dumps(check,sort_keys=True,separators=(",",":"),default=str)
            if hashlib.sha256(canonical.encode()).hexdigest()!=row.get("row_hash"):
                return {"valid":False,"index":i,"reason":"ROW_HASH_MISMATCH"}
            prev=row["row_hash"]
        return {"valid":True,"rows":len(self._rows()),"head":prev}
    def fingerprint(self):
        return hashlib.sha256(self.path.read_bytes()).hexdigest() if self.path.exists() else None
