from __future__ import annotations
import os, json
from pathlib import Path
from urllib.parse import quote_plus
from datetime import datetime, timezone

def database_url_from_env():
    """Build a SQLAlchemy URL from explicit POSTGRES_* variables when DATABASE_URL is absent."""
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    host, port, db, user, password = (os.getenv(k) for k in ("POSTGRES_HOST","POSTGRES_PORT","POSTGRES_DB","POSTGRES_USER","POSTGRES_PASSWORD"))
    if all((host, port, db, user, password)):
        return f"postgresql+psycopg://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{db}"
    return None


class PostgreSQLV25Store:
    """Optional PostgreSQL primary store for V25 empirical rows.

    The JSONL dataset remains an append-only local mirror/forensic backup. When
    PostgreSQL is configured and reachable, reads/writes use this store first.
    """
    def __init__(self,url=None):
        self.url=url or database_url_from_env()
        self.available=False; self.error=None; self.engine=None
        self._Session=None
    def connect(self):
        if not self.url:
            self.error='DATABASE_URL_UNSET'; return False
        try:
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            self.engine=create_engine(self.url,pool_pre_ping=True,future=True)
            self.engine.connect().close()
            self._Session=sessionmaker(bind=self.engine,expire_on_commit=False)
            self.available=True; self.error=None
            return True
        except Exception as e:
            self.available=False; self.error=f'{type(e).__name__}:{e}'; return False
    def ensure_schema(self):
        if not self.available and not self.connect(): return False
        try:
            from sqlalchemy import text
            with self.engine.begin() as conn:
                conn.execute(text('''
                    CREATE TABLE IF NOT EXISTS v25_dataset_rows (
                        observation_id TEXT PRIMARY KEY,
                        event_id TEXT,
                        mode TEXT NOT NULL CHECK(mode IN ('PAPER','SHADOW')),
                        decision TEXT NOT NULL,
                        decision_time TIMESTAMPTZ,
                        created_at TIMESTAMPTZ NOT NULL,
                        row_hash TEXT NOT NULL UNIQUE,
                        previous_hash TEXT,
                        payload JSONB NOT NULL
                    )
                '''))
                conn.execute(text('CREATE INDEX IF NOT EXISTS idx_v25_dataset_event_time ON v25_dataset_rows(event_id, created_at)'))
                conn.execute(text('CREATE INDEX IF NOT EXISTS idx_v25_dataset_decision ON v25_dataset_rows(decision, created_at)'))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS v25_observation_snapshots (
                        snapshot_id TEXT PRIMARY KEY,
                        event_id TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        bookmaker TEXT,
                        market TEXT,
                        selection TEXT,
                        line NUMERIC,
                        odds DOUBLE PRECISION NOT NULL CHECK (odds > 1),
                        source_timestamp TIMESTAMPTZ NOT NULL,
                        captured_at TIMESTAMPTZ NOT NULL,
                        received_at TIMESTAMPTZ NOT NULL,
                        mode TEXT NOT NULL CHECK(mode IN ('PRE','LIVE')),
                        payload JSONB NOT NULL,
                        row_hash TEXT NOT NULL
                    )
                """))
                conn.execute(text('CREATE INDEX IF NOT EXISTS idx_v25_snapshots_event_time ON v25_observation_snapshots(event_id,source_timestamp)'))
                conn.execute(text('CREATE INDEX IF NOT EXISTS idx_v25_snapshots_captured ON v25_observation_snapshots(captured_at)'))
            return True
        except Exception as e:
            self.error=f'{type(e).__name__}:{e}'; self.available=False; return False
    def append_row(self,row):
        if not self.ensure_schema(): return None
        from sqlalchemy import text
        with self.engine.begin() as conn:
            existing=conn.execute(text('SELECT payload FROM v25_dataset_rows WHERE observation_id=:id'),{'id':row['observation_id']}).fetchone()
            if existing:
                return dict(existing[0])
            conn.execute(text('''INSERT INTO v25_dataset_rows
                (observation_id,event_id,mode,decision,decision_time,created_at,row_hash,previous_hash,payload)
                VALUES (:observation_id,:event_id,:mode,:decision,:decision_time,:created_at,:row_hash,:previous_hash,CAST(:payload AS JSONB))'''),
                {
                    'observation_id':row['observation_id'],'event_id':row.get('event_id'),'mode':row['mode'],
                    'decision':row['decision'],'decision_time':row.get('decision_time'),'created_at':row['created_at'],
                    'row_hash':row['row_hash'],'previous_hash':row.get('previous_hash'),'payload':json.dumps(row,sort_keys=True,default=str)
                })
        return row
    def rows(self):
        if not self.available and not self.connect(): return None
        from sqlalchemy import text
        try:
            with self.engine.connect() as conn:
                data=conn.execute(text('SELECT payload FROM v25_dataset_rows ORDER BY created_at, observation_id')).fetchall()
            return [dict(x[0]) if isinstance(x[0],dict) else json.loads(x[0]) for x in data]
        except Exception as e:
            self.error=f'{type(e).__name__}:{e}'; return None
    def append_snapshot(self, row):
        if not self.ensure_schema():
            return None
        from sqlalchemy import text
        payload = json.dumps(row, sort_keys=True, default=str)
        with self.engine.begin() as conn:
            existing = conn.execute(text('SELECT payload FROM v25_observation_snapshots WHERE snapshot_id=:id'), {'id': row['snapshot_id']}).fetchone()
            if existing:
                return dict(existing[0]) if isinstance(existing[0], dict) else json.loads(existing[0])
            conn.execute(text("""INSERT INTO v25_observation_snapshots
                (snapshot_id,event_id,provider,bookmaker,market,selection,line,odds,source_timestamp,captured_at,received_at,mode,payload,row_hash)
                VALUES (:snapshot_id,:event_id,:provider,:bookmaker,:market,:selection,:line,:odds,:source_timestamp,:captured_at,:received_at,:mode,CAST(:payload AS JSONB),:row_hash)"""), {
                'snapshot_id': row['snapshot_id'], 'event_id': row.get('event_id'), 'provider': row.get('source') or row.get('provider'),
                'bookmaker': row.get('bookmaker'), 'market': row.get('market'), 'selection': row.get('selection'), 'line': row.get('line'),
                'odds': row.get('odds'), 'source_timestamp': row.get('source_timestamp'), 'captured_at': row.get('captured_at'),
                'received_at': row.get('received_at') or row.get('captured_at'), 'mode': row.get('mode') or 'PRE', 'payload': payload,
                'row_hash': row.get('raw_hash') or row.get('row_hash')
            })
        return row

    def snapshots(self):
        if not self.available and not self.connect():
            return None
        from sqlalchemy import text
        try:
            with self.engine.connect() as conn:
                data = conn.execute(text('SELECT payload FROM v25_observation_snapshots ORDER BY captured_at, snapshot_id')).fetchall()
            return [dict(x[0]) if isinstance(x[0], dict) else json.loads(x[0]) for x in data]
        except Exception as e:
            self.error = f'{type(e).__name__}:{e}'
            return None

    def head_hash(self):
        if not self.available and not self.connect(): return None
        from sqlalchemy import text
        try:
            with self.engine.connect() as conn:
                row=conn.execute(text('SELECT row_hash FROM v25_dataset_rows ORDER BY created_at DESC, observation_id DESC LIMIT 1')).fetchone()
            return row[0] if row else None
        except Exception:
            return None
    def health(self):
        return {'configured':bool(self.url),'available':self.available,'error':self.error,'primary':self.available}

class RedisV25Store:
    def __init__(self,url=None):self.url=url or os.getenv('REDIS_URL');self.available=False;self.error=None;self.client=None
    def connect(self):
        if not self.url:self.error='REDIS_URL_UNSET';return False
        try:
            import redis
            self.client=redis.Redis.from_url(self.url,decode_responses=True);self.client.ping();self.available=True;self.error=None;return True
        except Exception as e:self.available=False;self.error=f'{type(e).__name__}:{e}';return False
    def health(self):return {'configured':bool(self.url),'available':self.available,'error':self.error,'role':'CACHE/EPHEMERAL_ONLY'}


class V25SnapshotStore:
    """Persistent raw observation store. PostgreSQL is primary; JSONL is forensic fallback."""
    def __init__(self, persistence=None, path='data/research/robo_bet_snapshots_v25.jsonl'):
        self.persistence = persistence
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _local_rows(self):
        if not self.path.exists(): return []
        return [json.loads(x) for x in self.path.read_text(encoding='utf-8').splitlines() if x.strip()]

    def append(self, row):
        row = dict(row); sid = str(row['snapshot_id'])
        if self.persistence is not None and self.persistence.available:
            stored = self.persistence.append_snapshot(row)
            if stored is None: raise RuntimeError('SNAPSHOT_PERSISTENCE_FAILED')
            row = stored
        existing = next((x for x in self._local_rows() if str(x.get('snapshot_id')) == sid), None)
        if existing: return existing
        with self.path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, sort_keys=True, separators=(",", ":"), default=str) + "\n")
        return row

    def rows(self):
        if self.persistence is not None and self.persistence.available:
            rows = self.persistence.snapshots()
            if rows is not None: return rows
        return self._local_rows()
