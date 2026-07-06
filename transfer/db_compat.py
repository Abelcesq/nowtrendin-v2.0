"""
SQLite / Postgres compatibility shim for the Gradient Score engine.

If DATABASE_URL is set (Heroku Postgres), connections go to Postgres via
psycopg2 with on-the-fly SQL translation so the existing SQLite-flavoured
SQL keeps working. If DATABASE_URL is absent, behaves exactly like sqlite3.

Usage: replace `sqlite3.connect(path)` with `db_compat.connect(path)`.
Row access stays dict-style: `dict(row)`, `row["col"]`, `row.get("col")`.
"""
import os
import re
import sqlite3
import threading

DATABASE_URL = os.getenv("DATABASE_URL")
USE_PG = bool(DATABASE_URL)

if USE_PG:
    import time as _time
    import psycopg2
    import psycopg2.extras
    import psycopg2.pool

    # Connection pool — reuses a small number of connections so the serve
    # path doesn't open a fresh SSL connection per row (which both blows the
    # ~20-connection cap on small Heroku Postgres plans and is slow).
    #
    # SELF-HEALING (2026-07-06, the /scores outage lesson): psycopg2's pool has
    # NO reclamation — a checked-out connection whose caller errors before
    # close() is a slot lost FOREVER, and getconn() happily hands out
    # connections that were killed server-side (pg:killall / restarts), whose
    # first use raises and (at call sites without try/finally) orphans the
    # slot. After PG_POOL_MAX such events every request raises PoolError while
    # the SERVER sits at 2/20 connections. Four defenses below:
    #   1. checkout VALIDATION  — a dead conn is discarded + replaced, never
    #      handed to a caller (see connect()).
    #   2. broken-marking       — a conn whose query dies mid-use is discarded
    #      on close(), not recycled (_Cur/_Conn "_broken").
    #   3. bounded DIRECT fallback — while the pool is exhausted, serve from a
    #      few non-pooled connections instead of 500ing (PG_DIRECT_MAX).
    #   4. pool REBUILD         — exhaustion that persists past
    #      PG_POOL_REBUILD_AFTER_S seconds is a poisoned pool (leaked slots),
    #      not a burst: swap in a fresh pool, close the old one's IDLE conns.
    _pool = None
    _pool_lock = threading.Lock()
    _exhausted_since = None     # first PoolError of the current outage (None = healthy)
    _last_rebuild = 0.0
    _direct_sem = threading.BoundedSemaphore(int(os.getenv("PG_DIRECT_MAX", "4")))
    POOL_REBUILD_AFTER_S = int(os.getenv("PG_POOL_REBUILD_AFTER_S", "90"))
    POOL_REBUILD_COOLDOWN_S = int(os.getenv("PG_POOL_REBUILD_COOLDOWN_S", "120"))

    def _new_pool():
        # Default 8/dyno: web(8) + worker(8) = 16 < the essential-tier
        # 20-connection ceiling (PG_POOL_MAX to tune; 12 on the web-only
        # engine). PG_DIRECT_MAX direct fallbacks stay inside the remainder.
        return psycopg2.pool.ThreadedConnectionPool(
            1, int(os.getenv("PG_POOL_MAX", "8")), DATABASE_URL, sslmode="require"
        )

    def _get_pool():
        global _pool
        if _pool is None:
            with _pool_lock:
                if _pool is None:
                    _pool = _new_pool()
        return _pool

    def _rebuild_pool():
        """Swap a poisoned pool (leaked slots — exhausted while the server is
        near-idle) for a fresh one. Cooldown-guarded so a genuine long burst
        can't thrash. Old IDLE connections are closed to free server slots;
        old CHECKED-OUT connections are left to their holders — their close()
        falls through to a hard conn.close() (the putconn will fail on the
        replaced pool), so nothing leaks server-side."""
        global _pool, _last_rebuild, _exhausted_since
        with _pool_lock:
            if _time.time() - _last_rebuild < POOL_REBUILD_COOLDOWN_S:
                return
            old = _pool
            _pool = _new_pool()
            _last_rebuild = _time.time()
            _exhausted_since = None
            print("[db_compat] POOL REBUILT — exhaustion persisted "
                  f">{POOL_REBUILD_AFTER_S}s (leaked slots); fresh pool swapped in")
            if old is not None:
                try:
                    for _c in list(getattr(old, "_pool", []) or []):  # idle conns only
                        try:
                            _c.close()
                        except Exception:
                            pass
                except Exception:
                    pass

    def _probe_ok(conn) -> bool:
        """Cheap liveness check — a server-killed conn looks open client-side
        until first use; one SELECT 1 round-trip exposes it before a caller
        can crash on it (and leak the slot)."""
        try:
            if conn.closed:
                return False
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
            conn.rollback()
            return True
        except Exception:
            return False

    def _direct_conn():
        """Bounded non-pooled fallback so reads keep serving while the pool is
        wedged. The semaphore caps concurrent directs (PG_DIRECT_MAX, default
        4) to respect the server's connection ceiling."""
        if not _direct_sem.acquire(blocking=False):
            raise psycopg2.pool.PoolError(
                "connection pool exhausted (direct-fallback cap reached)")
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        except Exception:
            _direct_sem.release()
            raise
        print("[db_compat] pool exhausted → DIRECT connection fallback")
        return _Conn(conn, pooled=False)

# ── SQL translation (Postgres path only) ──────────────────────────────
_DT        = re.compile(r"datetime\(\s*'now'\s*\)", re.I)
_AUTOINC   = re.compile(r"INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT", re.I)
_OR_IGNORE = re.compile(r"INSERT\s+OR\s+IGNORE\s+INTO", re.I)
_OR_REPLACE = re.compile(r"INSERT\s+OR\s+REPLACE\s+INTO", re.I)


def _translate(sql: str) -> str:
    s = sql
    had_ignore = bool(_OR_IGNORE.search(s))
    s = _OR_IGNORE.sub("INSERT INTO", s)
    # Remaining OR REPLACE statements are ones with no real PK conflict
    # (e.g. velocity_scores uses a fresh uuid id each run) → plain INSERT.
    s = _OR_REPLACE.sub("INSERT INTO", s)
    s = _DT.sub("(now())::text", s)
    s = _AUTOINC.sub("SERIAL PRIMARY KEY", s)
    s = s.replace("?", "%s")
    if had_ignore and "ON CONFLICT" not in s.upper():
        s = s.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"
    return s


def _is_pragma(sql: str) -> bool:
    return sql.lstrip().upper().startswith("PRAGMA")


class _Cur:
    def __init__(self, cur, owner=None):
        self._c = cur
        self._owner = owner   # the _Conn, so a dead-connection error marks it broken

    def _mark_broken(self):
        if self._owner is not None:
            object.__setattr__(self._owner, "_broken", True)

    def execute(self, sql, params=None):
        if _is_pragma(sql):
            return self
        try:
            self._c.execute(_translate(sql), params)
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            # The CONNECTION is dead (killed server-side / dropped), not just
            # the query — flag it so close() discards instead of recycling a
            # corpse into the pool.
            self._mark_broken()
            raise
        return self

    def executemany(self, sql, seq):
        try:
            self._c.executemany(_translate(sql), seq)
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            self._mark_broken()
            raise
        return self

    def fetchone(self):
        return self._c.fetchone()

    def fetchall(self):
        return self._c.fetchall()

    def fetchmany(self, size=None):
        return self._c.fetchmany(size) if size is not None else self._c.fetchmany()

    def __iter__(self):
        return iter(self._c)

    def __getattr__(self, name):
        return getattr(self._c, name)


# Schemas already created this process (avoid re-running heavy DDL per connection)
_ran_scripts = set()


class _Conn:
    def __init__(self, conn, pooled=True):
        object.__setattr__(self, "_conn", conn)
        object.__setattr__(self, "_pooled", pooled)
        object.__setattr__(self, "_broken", False)

    def cursor(self):
        return _Cur(self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor),
                    owner=self)

    def execute(self, sql, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def executemany(self, sql, seq):
        # Mirror sqlite3 Connection.executemany (psycopg2 only exposes it on the
        # cursor). Translates `?`→`%s` and runs the batch via a cursor.
        cur = self._conn.cursor()
        cur.executemany(_translate(sql), list(seq))
        return cur

    def executescript(self, script):
        key = hash(script)
        if key in _ran_scripts:
            return self
        c = self._conn.cursor()
        c.execute(_translate(script))
        self._conn.commit()
        _ran_scripts.add(key)
        return self

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        # DIRECT (non-pooled fallback) connections really close + free their
        # semaphore slot; pooled ones return to the pool — or are DISCARDED
        # (putconn close=True) when broken/dead so the pool replaces them.
        if not self._pooled:
            try:
                self._conn.close()
            except Exception:
                pass
            try:
                _direct_sem.release()
            except Exception:
                pass
            return
        try:
            if self._broken or self._conn.closed:
                _get_pool().putconn(self._conn, close=True)
            else:
                self._conn.rollback()  # clear any open/aborted transaction
                _get_pool().putconn(self._conn)
        except Exception:
            try:
                _get_pool().putconn(self._conn, close=True)
            except Exception:
                # putconn can refuse a conn from a REPLACED (rebuilt) pool —
                # hard-close so the server slot is freed regardless.
                try:
                    self._conn.close()
                except Exception:
                    pass

    def __setattr__(self, key, value):
        if key == "row_factory":
            return  # ignored — Postgres path always uses a dict cursor
        object.__setattr__(self, key, value)

    def __getattr__(self, name):
        return getattr(self._conn, name)


def connect(path=None, **kwargs):
    """Drop-in replacement for sqlite3.connect().

    PG path is SELF-HEALING (see the pool notes above): checkouts are
    liveness-probed (dead conns discarded + replaced, never handed out);
    exhaustion falls back to a bounded direct connection so serving
    continues; exhaustion persisting past PG_POOL_REBUILD_AFTER_S swaps in
    a fresh pool (leaked-slot recovery)."""
    if not USE_PG:
        return sqlite3.connect(path, **kwargs)
    global _exhausted_since
    pool = _get_pool()
    attempts = int(os.getenv("PG_POOL_MAX", "8")) + 1
    for _ in range(attempts):
        try:
            conn = pool.getconn()
        except psycopg2.pool.PoolError:
            now = _time.time()
            if _exhausted_since is None:
                _exhausted_since = now
            if now - _exhausted_since >= POOL_REBUILD_AFTER_S:
                _rebuild_pool()
                pool = _get_pool()
                continue          # retry on the fresh pool
            return _direct_conn() # burst window — keep serving, bounded
        _exhausted_since = None   # a successful checkout ends the outage clock
        if _probe_ok(conn):
            return _Conn(conn, pooled=True)
        try:
            pool.putconn(conn, close=True)  # dead conn — discard; pool replaces it
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
    # The pool kept handing back dead connections — serve direct as a last resort.
    return _direct_conn()
