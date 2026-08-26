"""Resumable, provenance-first local acquisition worker.

No access-control bypassing. Supports HTTP(S) and local-file acquisition, checksum
caching, atomic downloads, resumable execution at artifact level, and explicit
state transitions. Parsing/materialization remains a separate auditable stage.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CFG = ROOT / "config" / "data_acquisition_local.json"
DEFAULT_MAN = ROOT / "data/global_dataset/registry/DATA_ACQUISITION_MANIFEST.json"
STATES = ["FOUND","ACCESSIBLE","DOWNLOAD_STARTED","DOWNLOADED","CHECKSUM_VALIDATED","MATERIALIZED","NORMALIZED","VALIDATED","PROCESSED","USED_IN_MODEL","FAILED","BLOCKED"]


def now(): return datetime.now(timezone.utc).isoformat()

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_json(path, default):
    if path.exists():
        try: return json.loads(path.read_text(encoding="utf-8"))
        except Exception: pass
    return default

def atomic_copy(src: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    shutil.copyfile(src, tmp)
    os.replace(tmp, dest)

def download_http(url, dest, timeout, retries, backoff):
    last = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers={"User-Agent":"RoboDaBet-DataAcquisitionWorker/2.0"})
            with urlopen(req, timeout=timeout) as r, dest.with_name(dest.name+".part").open("wb") as out:
                while True:
                    chunk = r.read(1024*1024)
                    if not chunk: break
                    out.write(chunk)
            os.replace(dest.with_name(dest.name+".part"), dest)
            return True, None, attempt
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            part = dest.with_name(dest.name+".part")
            if part.exists(): part.unlink()
            if attempt < retries: time.sleep(min(backoff ** attempt, 30))
    return False, last, retries

def acquire_one(source, raw_root, timeout, retries, expected_hash=None):
    name = source.get("artifact") or Path(source.get("url") or source.get("path") or "artifact.bin").name
    dest = raw_root / name
    rec = {"source_id": source.get("source_id", name), "source_url": source.get("url"),
           "local_path": source.get("path"), "artifact": name, "retrieval_timestamp": now(),
           "state_history": ["FOUND"], "accessible": False, "downloaded": False,
           "materialized": False, "validated": False, "processed": False, "used_in_model": False}
    try:
        if source.get("path"):
            src = Path(source["path"]).expanduser().resolve()
            if not src.exists(): raise FileNotFoundError(str(src))
            rec["state_history"].append("ACCESSIBLE"); rec["accessible"] = True
            if dest.exists() and sha256(dest) == sha256(src):
                rec.update({"reused_existing": True, "downloaded": True, "state":"CHECKSUM_VALIDATED"})
                rec["state_history"] += ["DOWNLOAD_STARTED","DOWNLOADED","CHECKSUM_VALIDATED"]
            else:
                rec["state_history"].append("DOWNLOAD_STARTED"); atomic_copy(src,dest)
                rec["state_history"].append("DOWNLOADED"); rec["downloaded"] = True
        else:
            url = source.get("url")
            if not url: raise ValueError("source requires url or path")
            # ACCESSIBLE is only promoted after a real HTTP response; DNS/connection failure stays BLOCKED.
            rec["state_history"].append("DOWNLOAD_STARTED")
            ok, err, attempts = download_http(url,dest,timeout,retries,2)
            rec["attempts"] = attempts
            if not ok: raise ConnectionError(err)
            rec["downloaded"] = True; rec["accessible"] = True; rec["state_history"].append("ACCESSIBLE"); rec["state_history"].append("DOWNLOADED")
        digest = sha256(dest); rec["raw_file_hash"] = digest
        if expected_hash and digest.lower() != expected_hash.lower():
            rec["state_history"].append("FAILED"); rec["state"]="FAILED"; rec["error"]="checksum mismatch"; return rec
        rec["state_history"].append("CHECKSUM_VALIDATED"); rec["state"]="CHECKSUM_VALIDATED"; rec["raw_path"] = str(dest)
        return rec
    except Exception as exc:
        rec["state_history"].append("BLOCKED" if isinstance(exc,(ConnectionError,TimeoutError)) else "FAILED")
        rec["state"] = rec["state_history"][-1]; rec["error"] = f"{type(exc).__name__}: {exc}"
        return rec

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config", default=str(DEFAULT_CFG)); ap.add_argument("--url", action="append")
    ap.add_argument("--path", action="append"); ap.add_argument("--name", action="append", default=[])
    ap.add_argument("--timeout", type=int, default=None); ap.add_argument("--retries", type=int, default=None)
    args=ap.parse_args()
    cfg=load_json(Path(args.config), {})
    raw_root=Path(cfg.get("raw_root", ROOT/"data/raw/acquisition_worker")); raw_root.mkdir(parents=True,exist_ok=True)
    man_path=Path(cfg.get("manifest", DEFAULT_MAN)); man=load_json(man_path, {"schema_version":"2.0","execution_log":[],"real_money":"DISABLED"})
    if not isinstance(man.get("execution_log"), list): man["execution_log"] = []
    man.setdefault("schema_version", "2.0"); man.setdefault("real_money", "DISABLED")
    sources=[]
    for i,u in enumerate(args.url or []): sources.append({"source_id":f"cli-url-{i+1}","url":u,"artifact":(args.name[i] if i<len(args.name) else Path(u).name)})
    for i,p in enumerate(args.path or []): sources.append({"source_id":f"cli-local-{i+1}","path":p,"artifact":(args.name[i] if i<len(args.name) else Path(p).name)})
    for s in cfg.get("sources",[]): sources.append(s)
    if not sources: ap.error("provide --url/--path or sources in config")
    timeout=args.timeout or int(cfg.get("timeout_seconds",30)); retries=args.retries or int(cfg.get("retries",3))
    for s in sources:
        rec=acquire_one(s,raw_root,timeout,retries,s.get("sha256")); man["execution_log"].append(rec)
    man["updated_at_utc"]=now(); man_path.parent.mkdir(parents=True,exist_ok=True); man_path.write_text(json.dumps(man,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(man["execution_log"][-len(sources):],indent=2,ensure_ascii=False))

if __name__=="__main__": main()
