"""Behavior tests for pit_store.py (sqlite; the PG path shares all logic —
only DDL dialect differs and is live-verified at deploy via /diag/pit).

Run:  python test_pit_store.py
"""
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pit_store  # noqa: E402

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def fresh_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.unlink(path)
    # reset module init latch so each test db gets its own schema
    pit_store._init_done = False
    return path


def raw(path):
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c


def t1_record_and_hash():
    print("t1: record() writes an append-only row with correct hashes")
    db = fresh_db()
    sha = pit_store.record("trend_score", "test topic", "2026-08-18",
                           {"overall": 61.2, "detection": 70.0}, db_path=db)
    check("record returns a sha", bool(sha) and len(sha) == 64)
    c = raw(db)
    row = c.execute("SELECT * FROM pit_observations").fetchone()
    check("one row stored", row is not None)
    check("knowable_at stamped by the store (not caller)",
          row["knowable_at"].startswith(row["knowable_day"]))
    expect = pit_store._sha(
        f"trend_score|test topic|2026-08-18|{row['knowable_at']}|{row['payload_sha256']}")
    check("row_sha256 recomputes", row["row_sha256"] == expect == sha)
    c.close()


def t2_append_only_triggers():
    print("t2: UPDATE and DELETE are trigger-blocked in the DB itself")
    db = fresh_db()
    pit_store.record("trend_score", "k", "2026-08-18", {"v": 1}, db_path=db)
    c = raw(db)
    blocked_u = blocked_d = False
    try:
        c.execute("UPDATE pit_observations SET payload='tampered'")
        c.commit()
    except sqlite3.IntegrityError:
        blocked_u = True
    try:
        c.execute("DELETE FROM pit_observations")
        c.commit()
    except sqlite3.IntegrityError:
        blocked_d = True
    check("UPDATE blocked", blocked_u)
    check("DELETE blocked", blocked_d)
    c.rollback()
    c.close()
    # seals table too
    pit_store.seal_day("2026-08-01", db_path=db)
    c = raw(db)
    blocked_s = False
    try:
        c.execute("UPDATE pit_seals SET seal_sha256='x'")
        c.commit()
    except sqlite3.IntegrityError:
        blocked_s = True
    check("seal UPDATE blocked", blocked_s)
    c.close()


def _backdate_insert(db, day, key, payload_sha="p", n=1):
    """Simulate rows written on an earlier day (INSERT is allowed; only
    mutation is blocked). Hashes built the same way record() builds them."""
    c = raw(db)
    for i in range(n):
        ka = f"{day}T12:00:{i:02d}.000+00:00"
        row_sha = pit_store._sha(f"trend_score|{key}{i}|{day}|{ka}|{payload_sha}")
        c.execute(
            "INSERT INTO pit_observations (kind,item_key,event_date,knowable_at,"
            "knowable_day,payload,payload_sha256,row_sha256) VALUES (?,?,?,?,?,?,?,?)",
            ("trend_score", f"{key}{i}", day, ka, day, "{}", payload_sha, row_sha))
    c.commit()
    c.close()


def t3_seal_chain_and_gaps():
    print("t3: seal_pending seals every day incl. gap days; chain links")
    db = fresh_db()
    pit_store._ensure_init(db)
    _backdate_insert(db, "2026-08-14", "a", n=3)
    _backdate_insert(db, "2026-08-16", "b", n=2)   # 08-15 is a gap day
    r = pit_store.seal_pending(db_path=db)
    sealed_days = [s["seal_date"] for s in r["sealed"]]
    check("seals from first obs day through yesterday",
          sealed_days[0] == "2026-08-14" and "2026-08-15" in sealed_days
          and "2026-08-16" in sealed_days, str(sealed_days))
    c = raw(db)
    seals = {s["seal_date"]: dict(s) for s in
             c.execute("SELECT * FROM pit_seals").fetchall()}
    check("gap day sealed as EMPTY",
          seals["2026-08-15"]["row_count"] == 0 and
          seals["2026-08-15"]["rows_sha256"] == pit_store._sha(pit_store.EMPTY_DAY))
    check("first seal links to GENESIS",
          seals["2026-08-14"]["prev_seal_sha256"] == pit_store.GENESIS)
    check("chain links day to day",
          seals["2026-08-15"]["prev_seal_sha256"] == seals["2026-08-14"]["seal_sha256"]
          and seals["2026-08-16"]["prev_seal_sha256"] == seals["2026-08-15"]["seal_sha256"])
    c.close()
    r2 = pit_store.seal_day("2026-08-14", db_path=db)
    check("re-seal is idempotent (existed, never rewritten)", r2["existed"])


def t4_verify_detects_tampering():
    print("t4: verify() passes clean, fails on tampering")
    db = fresh_db()
    pit_store._ensure_init(db)
    _backdate_insert(db, "2026-08-14", "a", n=3)
    pit_store.seal_pending(db_path=db)
    v = pit_store.verify(days=60, db_path=db)
    check("clean chain verifies", v["ok"] and v["days_checked"] >= 1)
    # simulate an attacker with DB access who drops the trigger first
    c = raw(db)
    c.execute("DROP TRIGGER pit_obs_no_update")
    c.execute("UPDATE pit_observations SET row_sha256='deadbeef' WHERE item_key='a0'")
    c.commit()
    c.close()
    v2 = pit_store.verify(days=60, db_path=db)
    check("tampered row breaks verification", not v2["ok"])
    bad = [d for d in v2["days"] if not d["ok"]]
    check("failure localized to the tampered day",
          len(bad) >= 1 and bad[0]["seal_date"] == "2026-08-14")


def t5_status_and_failopen():
    print("t5: status() reports; record() is fail-open on a broken path")
    db = fresh_db()
    pit_store.record("index_value", "nti-attention-v0", "2026-08-18",
                     {"value": 100.0}, db_path=db)
    s = pit_store.status(db_path=db)
    check("status counts observations", s["observations"] == 1
          and s["by_kind"].get("index_value") == 1)
    bad = os.path.join(tempfile.gettempdir(),
                       "definitely", "missing", "dir", "x.db")
    pit_store._init_done = False
    r = pit_store.record("trend_score", "k", "2026-08-18", {"v": 1}, db_path=bad)
    check("record on broken path returns None, no raise", r is None)


if __name__ == "__main__":
    t1_record_and_hash()
    t2_append_only_triggers()
    t3_seal_chain_and_gaps()
    t4_verify_detects_tampering()
    t5_status_and_failopen()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
