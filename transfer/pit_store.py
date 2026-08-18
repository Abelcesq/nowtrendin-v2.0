"""
pit_store.py â€” the bitemporal POINT-IN-TIME store. Chairman ruling (b), 2026-08-18.

WHY THIS EXISTS
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
Three board seats independently found (BOARD_1M-month_2026-08-18.md, convergence 2)
that the bitemporal `knowable_at` archive our buyer-diligence paper claimed
"delivers by construction" existed ONLY in planning documents â€” not in this
engine's code. Chairman ruling (b) (METER_DECISION_MINUTE_2026-08-18.md):
build the store IN THIS ENGINE before any external claim references it.
This module is that build. Until the day it shipped, no sales/DDQ/regulatory
language may assert the archive; from the day it shipped, the claim is exactly
what this file does and nothing more.

WHAT IT IS
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
An append-only, hash-chain-sealed record of every served score (and, once the
frozen-rule index calculation starts, every index value):

  event_date   â€” canonical YYYY-MM-DD the value is ABOUT (Â§14 date canon)
  knowable_at  â€” the full UTC instant the value became knowable to the system
                 (stamped HERE at write time; never supplied by a caller, so it
                 can never be backdated)
  payload      â€” compact canonical JSON of the served numbers (sorted keys)
  row_sha256   â€” sha256 over kind|item_key|event_date|knowable_at|payload_sha256

Append-only is TRIGGER-ENFORCED in the database itself (UPDATE/DELETE â€” and on
Postgres TRUNCATE â€” raise), not promised in application code. A daily seal job
folds each UTC day's row hashes (ordered by id) into a chain hash and links it
to the previous day's seal: tampering with any historical row, or removing one,
breaks every seal from that day forward. An issuer starting later cannot
manufacture earlier knowable_at stamps: the seals for those days are already
fixed and chained.

WHAT IT IS NOT
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
HELD-OUT and WRITE-ONLY from the score sinks: nothing in scoring, calibration,
or serving ever READS this store (no circularity, no score impact). It is not a
backup (it stores served numbers, not inputs), and it is not retroactive â€” the
record begins the day this module deployed, which is the point: the value of a
point-in-time archive is precisely that it cannot be back-filled ("pre-sealed-
epoch scores are hindsight-mutable" â€” Statistician). NEVER prune this table.

FAIL-OPEN: a PIT write failure logs and returns; it can never break scoring.
Each write uses its OWN pooled connection so a failure cannot poison a scoring
transaction (Postgres aborts a txn on any statement error).
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

GENESIS = "PIT-GENESIS"          # prev-seal value for the first sealed day
EMPTY_DAY = "PIT-EMPTY"          # rows-hash for a day with zero observations

_init_done = False
_init_lock = threading.Lock()
_last_err_log = 0.0              # rate-limit failure logging (fail-open, not silent)


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _connect(db_path):
    """db_compat.connect with dict-style rows on BOTH dialects (the PG shim
    always uses a dict cursor and ignores row_factory; sqlite needs it set)."""
    conn = db_compat.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# â”€â”€ Schema + append-only triggers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_TABLES_SQLITE = """
CREATE TABLE IF NOT EXISTS pit_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    item_key TEXT NOT NULL,
    event_date TEXT NOT NULL,
    knowable_at TEXT NOT NULL,
    knowable_day TEXT NOT NULL,
    payload TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    row_sha256 TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pit_obs_day ON pit_observations (knowable_day);
CREATE TABLE IF NOT EXISTS pit_seals (
    seal_date TEXT PRIMARY KEY,
    first_id INTEGER,
    last_id INTEGER,
    row_count INTEGER NOT NULL,
    rows_sha256 TEXT NOT NULL,
    prev_seal_sha256 TEXT NOT NULL,
    seal_sha256 TEXT NOT NULL,
    sealed_at TEXT NOT NULL
);
"""

_TRIGGERS_SQLITE = """
CREATE TRIGGER IF NOT EXISTS pit_obs_no_update BEFORE UPDATE ON pit_observations
BEGIN SELECT RAISE(ABORT, 'PIT store is append-only'); END;
CREATE TRIGGER IF NOT EXISTS pit_obs_no_delete BEFORE DELETE ON pit_observations
BEGIN SELECT RAISE(ABORT, 'PIT store is append-only'); END;
CREATE TRIGGER IF NOT EXISTS pit_seal_no_update BEFORE UPDATE ON pit_seals
BEGIN SELECT RAISE(ABORT, 'PIT seals are append-only'); END;
CREATE TRIGGER IF NOT EXISTS pit_seal_no_delete BEFORE DELETE ON pit_seals
BEGIN SELECT RAISE(ABORT, 'PIT seals are append-only'); END;
"""

_TABLES_PG = """
CREATE TABLE IF NOT EXISTS pit_observations (
    id BIGSERIAL PRIMARY KEY,
    kind TEXT NOT NULL,
    item_key TEXT NOT NULL,
    event_date TEXT NOT NULL,
    knowable_at TEXT NOT NULL,
    knowable_day TEXT NOT NULL,
    payload TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    row_sha256 TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pit_obs_day ON pit_observations (knowable_day);
CREATE TABLE IF NOT EXISTS pit_seals (
    seal_date TEXT PRIMARY KEY,
    first_id BIGINT,
    last_id BIGINT,
    row_count INTEGER NOT NULL,
    rows_sha256 TEXT NOT NULL,
    prev_seal_sha256 TEXT NOT NULL,
    seal_sha256 TEXT NOT NULL,
    sealed_at TEXT NOT NULL
);
"""

_TRIGGER_FN_PG = """
CREATE OR REPLACE FUNCTION pit_append_only() RETURNS trigger AS $pitfn$
BEGIN
    RAISE EXCEPTION 'PIT store is append-only';
END $pitfn$ LANGUAGE plpgsql;
"""

# DROP+CREATE inside a guard block so re-running init is idempotent. TRUNCATE
# is a Postgres-only mutation path the row triggers don't cover â€” guard it too.
_TRIGGERS_PG = """
DO $pitdo$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'pit_obs_no_mutate') THEN
        CREATE TRIGGER pit_obs_no_mutate BEFORE UPDATE OR DELETE ON pit_observations
            FOR EACH ROW EXECUTE FUNCTION pit_append_only();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'pit_obs_no_truncate') THEN
        CREATE TRIGGER pit_obs_no_truncate BEFORE TRUNCATE ON pit_observations
            FOR EACH STATEMENT EXECUTE FUNCTION pit_append_only();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'pit_seal_no_mutate') THEN
        CREATE TRIGGER pit_seal_no_mutate BEFORE UPDATE OR DELETE ON pit_seals
            FOR EACH ROW EXECUTE FUNCTION pit_append_only();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'pit_seal_no_truncate') THEN
        CREATE TRIGGER pit_seal_no_truncate BEFORE TRUNCATE ON pit_seals
            FOR EACH STATEMENT EXECUTE FUNCTION pit_append_only();
    END IF;
END $pitdo$;
"""


# sqlite trigger bodies contain ';' inside BEGIN..END, so a naive split-on-';'
# would break them â€” statements are separated on the END; boundary instead.
def _sqlite_statements() -> list:
    stmts = [s.strip() for s in _TABLES_SQLITE.split(";") if s.strip()]
    trig = [s.strip() + " END;" for s in _TRIGGERS_SQLITE.split("END;") if s.strip()]
    return stmts + trig


def _init_sqlite(conn) -> None:
    cur = conn.cursor()
    for stmt in _sqlite_statements():
        cur.execute(stmt)
    conn.commit()


def _ensure_init(db_path: str = DB_PATH) -> None:
    global _init_done
    if _init_done:
        return
    with _init_lock:
        if _init_done:
            return
        conn = _connect(db_path)
        try:
            if db_compat.USE_PG:
                cur = conn.cursor()
                cur.execute(_TABLES_PG)
                cur.execute(_TRIGGER_FN_PG)
                cur.execute(_TRIGGERS_PG)
                conn.commit()
            else:
                _init_sqlite(conn)
            _init_done = True
        finally:
            conn.close()


# â”€â”€ Write path (fail-open, own connection) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def record(kind: str, item_key: str, event_date: str, payload: dict,
           db_path: str = DB_PATH) -> Optional[str]:
    """Append one observation. Returns row_sha256, or None on failure.

    knowable_at is stamped HERE â€” callers cannot supply it (no backdating).
    Fail-open: any error logs (rate-limited) and returns None; a PIT failure
    must never break a scoring or collection cycle.
    """
    global _last_err_log
    try:
        _ensure_init(db_path)
        now = _utcnow()
        knowable_at = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+00:00"
        knowable_day = now.strftime("%Y-%m-%d")
        pj = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=False, default=str)
        p_sha = _sha(pj)
        row_sha = _sha(f"{kind}|{item_key}|{event_date}|{knowable_at}|{p_sha}")
        conn = _connect(db_path)
        try:
            conn.execute(
                "INSERT INTO pit_observations "
                "(kind, item_key, event_date, knowable_at, knowable_day, "
                " payload, payload_sha256, row_sha256) VALUES (?,?,?,?,?,?,?,?)",
                (kind, item_key, event_date or "", knowable_at, knowable_day,
                 pj, p_sha, row_sha))
            conn.commit()
        finally:
            conn.close()
        return row_sha
    except Exception as e:
        if time.time() - _last_err_log > 300:   # one log line per 5 min max
            _last_err_log = time.time()
            print(f"[pit_store] record failed (fail-open): {e}")
        return None


# â”€â”€ Daily seal (hash chain) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _day_rows_hash(conn, day: str):
    """Fold the day's row hashes (ordered by id) into one chain hash."""
    rows = conn.execute(
        "SELECT id, row_sha256 FROM pit_observations "
        "WHERE knowable_day = ? ORDER BY id", (day,)).fetchall()
    if not rows:
        return _sha(EMPTY_DAY), None, None, 0
    h = _sha(GENESIS)
    for r in rows:
        h = _sha(h + r["row_sha256"])
    return h, rows[0]["id"], rows[-1]["id"], len(rows)


def seal_day(day: str, db_path: str = DB_PATH, conn=None) -> dict:
    """Seal one UTC day (idempotent â€” an existing seal is returned, never
    rewritten). Links to the previous seal by date order."""
    _ensure_init(db_path)
    own = conn is None
    c = conn or _connect(db_path)
    try:
        ex = c.execute("SELECT * FROM pit_seals WHERE seal_date = ?",
                       (day,)).fetchone()
        if ex:
            return {"seal_date": day, "existed": True,
                    "seal_sha256": ex["seal_sha256"]}
        prev = c.execute(
            "SELECT seal_sha256 FROM pit_seals WHERE seal_date < ? "
            "ORDER BY seal_date DESC LIMIT 1", (day,)).fetchone()
        prev_sha = prev["seal_sha256"] if prev else GENESIS
        rows_sha, first_id, last_id, n = _day_rows_hash(c, day)
        seal_sha = _sha(f"{day}|{n}|{rows_sha}|{prev_sha}")
        c.execute(
            "INSERT INTO pit_seals (seal_date, first_id, last_id, row_count, "
            "rows_sha256, prev_seal_sha256, seal_sha256, sealed_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (day, first_id, last_id, n, rows_sha, prev_sha, seal_sha,
             _utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")))
        c.commit()
        return {"seal_date": day, "existed": False, "row_count": n,
                "seal_sha256": seal_sha}
    finally:
        if own:
            c.close()


def seal_pending(db_path: str = DB_PATH) -> dict:
    """Seal every complete UTC day from the first observation (or the day
    after the last seal) through yesterday. Gap days seal too (EMPTY_DAY),
    so the chain has no holes."""
    _ensure_init(db_path)
    conn = _connect(db_path)
    try:
        today = _utcnow().strftime("%Y-%m-%d")
        last = conn.execute(
            "SELECT seal_date FROM pit_seals ORDER BY seal_date DESC LIMIT 1"
        ).fetchone()
        if last:
            start = (datetime.strptime(last["seal_date"], "%Y-%m-%d")
                     + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            first = conn.execute(
                "SELECT MIN(knowable_day) AS d FROM pit_observations").fetchone()
            if not first or not first["d"]:
                return {"sealed": [], "note": "no observations yet"}
            start = first["d"]
        sealed = []
        d = datetime.strptime(start, "%Y-%m-%d")
        while d.strftime("%Y-%m-%d") < today:
            day = d.strftime("%Y-%m-%d")
            sealed.append(seal_day(day, db_path=db_path, conn=conn))
            d += timedelta(days=1)
        return {"sealed": sealed, "through": (d - timedelta(days=1)).strftime("%Y-%m-%d")
                if sealed else None}
    finally:
        conn.close()


# â”€â”€ Verification (read-only) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def verify(days: int = 14, db_path: str = DB_PATH) -> dict:
    """Recompute the chain for the last N sealed days and check (a) each day's
    rows still fold to the sealed rows_sha256, (b) each seal_sha256 recomputes,
    (c) the prev-links match. Any mismatch = tampering or data loss."""
    _ensure_init(db_path)
    conn = _connect(db_path)
    try:
        seals = conn.execute(
            "SELECT * FROM pit_seals ORDER BY seal_date DESC LIMIT ?",
            (days,)).fetchall()
        seals = sorted((dict(s) for s in seals), key=lambda s: s["seal_date"])
        out, ok = [], True
        for s in seals:
            day = s["seal_date"]
            rows_sha, _f, _l, n = _day_rows_hash(conn, day)
            recomputed = _sha(f"{day}|{n}|{rows_sha}|{s['prev_seal_sha256']}")
            prev = conn.execute(
                "SELECT seal_sha256 FROM pit_seals WHERE seal_date < ? "
                "ORDER BY seal_date DESC LIMIT 1", (day,)).fetchone()
            prev_expect = prev["seal_sha256"] if prev else GENESIS
            day_ok = (rows_sha == s["rows_sha256"] and n == s["row_count"]
                      and recomputed == s["seal_sha256"]
                      and s["prev_seal_sha256"] == prev_expect)
            ok = ok and day_ok
            out.append({"seal_date": day, "ok": day_ok, "row_count": n,
                        "sealed_count": s["row_count"],
                        "rows_match": rows_sha == s["rows_sha256"],
                        "link_match": s["prev_seal_sha256"] == prev_expect})
        return {"ok": ok, "days_checked": len(out), "days": out}
    finally:
        conn.close()


def status(db_path: str = DB_PATH) -> dict:
    _ensure_init(db_path)
    conn = _connect(db_path)
    try:
        obs = conn.execute(
            "SELECT COUNT(*) AS n, MIN(knowable_day) AS first_day, "
            "MAX(knowable_day) AS last_day FROM pit_observations").fetchone()
        kinds = conn.execute(
            "SELECT kind, COUNT(*) AS n FROM pit_observations GROUP BY kind"
        ).fetchall()
        last_seal = conn.execute(
            "SELECT seal_date, row_count, seal_sha256, sealed_at FROM pit_seals "
            "ORDER BY seal_date DESC LIMIT 1").fetchone()
        n_seals = conn.execute("SELECT COUNT(*) AS n FROM pit_seals").fetchone()
        return {
            "store": "bitemporal PIT (event_date/knowable_at), append-only "
                     "trigger-enforced, daily hash-chain sealed",
            "observations": obs["n"] if obs else 0,
            "first_day": obs["first_day"] if obs else None,
            "last_day": obs["last_day"] if obs else None,
            "by_kind": {k["kind"]: k["n"] for k in kinds},
            "seals": n_seals["n"] if n_seals else 0,
            "last_seal": dict(last_seal) if last_seal else None,
        }
    finally:
        conn.close()


# â”€â”€ Daemon loop (hourly; seals complete days) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def seal_loop(stop_event: Optional[threading.Event] = None,
              interval_s: int = 3600, db_path: str = DB_PATH) -> None:
    """Hourly: seal any pending complete UTC days. First run also inits the
    schema so the store exists from boot even before the first score write."""
    time.sleep(20)   # let the app boot before touching the DB
    while True:
        try:
            r = seal_pending(db_path)
            newly = [s for s in (r.get("sealed") or []) if not s.get("existed")]
            if newly:
                print(f"[pit_store] sealed {len(newly)} day(s): "
                      f"{', '.join(s['seal_date'] for s in newly)}")
        except Exception as e:
            print(f"[pit_store] seal loop error: {e}")
        if stop_event is not None and stop_event.wait(interval_s):
            return
        if stop_event is None:
            time.sleep(interval_s)

