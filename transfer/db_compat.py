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
    import psycopg2
    import psycopg2.extras
    import psycopg2.pool

    # Connection pool — reuses a small number of connections so the serve
    # path doesn't open a fresh SSL connection per row (which both blows the
    # ~20-connection cap on small Heroku Postgres plans and is slow).
    _pool = None
    _pool_lock = threading.Lock()

    def _get_pool():
        global _pool
        if _pool is None:
            with _pool_lock:
                if _pool is None:
                    # Cap at 8 per dyno: web(8) + worker(8) = 16, leaving headroom
                    # under essential-0's hard 20-connection ceiling so a burst on
                    # one dyno can't starve the other (was 10+10=20 = exactly the cap).
                    _pool = psycopg2.pool.ThreadedConnectionPool(
                        1, int(os.getenv("PG_POOL_MAX", "8")), DATABASE_URL, sslmode="require"
                    )
        return _pool

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
    def __init__(self, cur):
        self._c = cur

    def execute(self, sql, params=None):
        if _is_pragma(sql):
            return self
        self._c.execute(_translate(sql), params)
        return self

    def executemany(self, sql, seq):
        self._c.executemany(_translate(sql), seq)
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
    def __init__(self, conn):
        object.__setattr__(self, "_conn", conn)

    def cursor(self):
        return _Cur(self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor))

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
        # Return the connection to the pool instead of closing it.
        try:
            self._conn.rollback()  # clear any open/aborted transaction
            _get_pool().putconn(self._conn)
        except Exception:
            try:
                _get_pool().putconn(self._conn, close=True)
            except Exception:
                pass

    def __setattr__(self, key, value):
        if key == "row_factory":
            return  # ignored — Postgres path always uses a dict cursor
        object.__setattr__(self, key, value)

    def __getattr__(self, name):
        return getattr(self._conn, name)


def connect(path=None, **kwargs):
    """Drop-in replacement for sqlite3.connect()."""
    if USE_PG:
        conn = _get_pool().getconn()
        return _Conn(conn)
    return sqlite3.connect(path, **kwargs)
