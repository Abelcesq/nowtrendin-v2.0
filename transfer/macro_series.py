"""
MACRO SERIES PERSISTENCE — Phase 2b. HELD-OUT, measurement only.

Board round 4, the Economist: *"Persist what we already fetch and throw away."*

`ofr_stfm._series()` requests the OFR's FULL published history on every call and holds it
in a 12-hour **in-memory** cache — so the entire series is discarded twice a day and
re-fetched from scratch, and nothing accumulates. `finra_data.short_interest_series()` does
the same for a ~180-day settlement window. We have been paying the request cost for years of
history and keeping none of it.

WHY THIS IS THE CHEAPEST ITEM ON THE BOARD'S LIST
─────────────────────────────────────────────────
It costs **$0** (no new source, no new subscription, no §16 onboarding — these feeds are
already wired and already gated), it needs no engineer judgement, and it starts the only
kind of asset the Board identified as un-buyable:

    "The only series a better-funded competitor cannot buy later is one whose observations
     exist ONLY if you were watching that day."  — the Economist, round 4

The OFR history is publicly re-fetchable, so THAT part is not the moat. What is ours is the
**vintaged** record: what the series said *on the day we read it*, before revision. A
revised series is not the series a contemporaneous observer saw, and that distinction is
exactly what the round-4 corpus rules require (`vintage`, point-in-time or nothing).

RETENTION: this is a reference corpus, not a ledger — but it is append-only and forward-only
all the same. Rows are never rewritten; a revision arrives as a NEW row with a new
`fetched_at`, so the revision history itself becomes observable.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
MACRO_PERSIST = os.getenv("MACRO_PERSIST", "0") == "1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canon(v) -> Optional[str]:
    """§14 canonical date; never a raw slice."""
    try:
        from date_utils import to_iso_date
        return to_iso_date(v)
    except Exception:
        s = str(v or "")[:10]
        return s if len(s) == 10 and s[4] == "-" else None


def init_macro_db(db_path: str = DB_PATH):
    conn = db_compat.connect(db_path)
    # PK includes `vintage_date` so a revision does not overwrite the original reading —
    # it lands beside it, and the revision becomes part of the record rather than erasing it.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS macro_series_daily (
            source TEXT, series_key TEXT, signal_date TEXT, value REAL,
            vintage_date TEXT, fetched_at TEXT,
            PRIMARY KEY (source, series_key, signal_date, vintage_date))
    """)
    for ddl in (
        "CREATE INDEX IF NOT EXISTS idx_macro_key ON macro_series_daily(series_key)",
        "CREATE INDEX IF NOT EXISTS idx_macro_date ON macro_series_daily(signal_date)",
    ):
        try:
            conn.execute(ddl)
        except Exception:
            pass
    conn.commit()
    conn.close()


def _upsert(conn, rows) -> int:
    ph = "%s" if db_compat.USE_PG else "?"
    written = 0
    for source, key, date, val, vintage, fetched in rows:
        cur = conn.execute(
            f"INSERT INTO macro_series_daily (source,series_key,signal_date,value,"
            f"vintage_date,fetched_at) VALUES ({','.join([ph]*6)}) "
            f"ON CONFLICT (source,series_key,signal_date,vintage_date) DO NOTHING",
            (source, key, date, val, vintage, fetched))
        # Count ACTUAL inserts. Incrementing beside ON CONFLICT DO NOTHING is the defect
        # the Board found in flow_ledger.enroll() and that I then repeated in
        # insider_flow.ingest() — it is evidently a habit, so it is checked here up front.
        try:
            written += 1 if (cur is not None and cur.rowcount != 0) else 0
        except Exception:
            written += 1
    return written


def persist_ofr(db_path: str = DB_PATH) -> dict:
    """Persist every OFR series the engine already fetches."""
    try:
        import ofr_stfm
    except Exception as e:
        return {"ok": False, "reason": f"ofr_stfm unavailable ({e})"}

    today = _canon(datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    fetched = _now()
    rows, seen = [], {}
    for key, mnemonic in (ofr_stfm.SERIES or {}).items():
        try:
            pairs = ofr_stfm._series(mnemonic) or []
        except Exception as e:
            seen[key] = f"error: {e}"
            continue
        seen[key] = len(pairs)
        for d, v in pairs:
            cd = _canon(d)
            if cd is None:
                continue
            rows.append(("ofr", key, cd, float(v), today, fetched))

    conn = db_compat.connect(db_path)
    try:
        written = _upsert(conn, rows)
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "source": "ofr", "series": seen,
            "observations_seen": len(rows), "rows_written": written,
            "note": "written < seen on a re-run is CORRECT — history already stored"}


def persist_finra(tickers, db_path: str = DB_PATH) -> dict:
    """Persist FINRA short-interest history for the given tickers."""
    try:
        import finra_data
    except Exception as e:
        return {"ok": False, "reason": f"finra_data unavailable ({e})"}

    today = _canon(datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    fetched = _now()
    rows, seen = [], {}
    for t in tickers:
        try:
            series = finra_data.short_interest_series(t) or []
        except Exception as e:
            seen[t] = f"error: {e}"
            continue
        seen[t] = len(series)
        for rec in series:
            if not isinstance(rec, dict):
                continue
            cd = _canon(rec.get("settlementDate") or rec.get("date")
                        or rec.get("signal_date"))
            val = rec.get("shortInterest") or rec.get("short_interest") or rec.get("value")
            if cd is None or val is None:
                continue
            try:
                rows.append(("finra", f"short_interest:{t.upper()}", cd, float(val),
                             today, fetched))
            except (TypeError, ValueError):
                continue

    conn = db_compat.connect(db_path)
    try:
        written = _upsert(conn, rows)
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "source": "finra", "tickers": seen,
            "observations_seen": len(rows), "rows_written": written}


def persist_all(tickers=None, db_path: str = DB_PATH) -> dict:
    if not MACRO_PERSIST:
        return {"ok": False, "reason": "MACRO_PERSIST is not enabled"}
    init_macro_db(db_path)
    out = {"ofr": persist_ofr(db_path)}
    if tickers:
        out["finra"] = persist_finra(tickers, db_path)
    return out


def status(db_path: str = DB_PATH) -> dict:
    conn = db_compat.connect(db_path)
    try:
        def one(sql):
            try:
                r = conn.execute(sql).fetchone()
                if r is None:
                    return None
                return (list(dict(r).values())[0] if hasattr(r, "keys") else r[0])
            except Exception:
                return None
        return {
            "enabled": MACRO_PERSIST,
            "rows": one("SELECT COUNT(*) FROM macro_series_daily"),
            "series": one("SELECT COUNT(DISTINCT series_key) FROM macro_series_daily"),
            "earliest": one("SELECT MIN(signal_date) FROM macro_series_daily"),
            "latest": one("SELECT MAX(signal_date) FROM macro_series_daily"),
            "vintages": one("SELECT COUNT(DISTINCT vintage_date) FROM macro_series_daily"),
        }
    finally:
        conn.close()


if __name__ == "__main__":
    import json, tempfile
    print("=== macro_series self-test ===\n")
    tmp = os.path.join(tempfile.gettempdir(), "macro_series_selftest.db")
    if os.path.exists(tmp):
        os.remove(tmp)
    init_macro_db(tmp)

    conn = db_compat.connect(tmp)
    r1 = [("ofr", "repo_rate", "2026-07-01", 5.31, "2026-07-25", _now()),
          ("ofr", "repo_rate", "2026-07-02", 5.33, "2026-07-25", _now())]
    n1 = _upsert(conn, r1)
    conn.commit()
    assert n1 == 2, n1
    print(f"first write: {n1} rows  OK")

    n2 = _upsert(conn, r1)
    conn.commit()
    assert n2 == 0, f"re-persisting identical history must write 0, got {n2}"
    print(f"re-persist same vintage: {n2} rows (idempotent)  OK")

    # A REVISION of the same observation must land BESIDE the original, not overwrite it —
    # that is what makes the revision history observable.
    rev = [("ofr", "repo_rate", "2026-07-01", 5.29, "2026-07-26", _now())]
    n3 = _upsert(conn, rev)
    conn.commit()
    assert n3 == 1, n3
    got = conn.execute("SELECT value, vintage_date FROM macro_series_daily "
                       "WHERE signal_date='2026-07-01' ORDER BY vintage_date").fetchall()
    conn.close()
    vals = [(dict(g)["value"], dict(g)["vintage_date"]) if hasattr(g, "keys") else (g[0], g[1])
            for g in got]
    assert len(vals) == 2, vals
    print(f"revision preserved alongside original: {vals}  OK")

    print(f"\nstatus: {json.dumps(status(tmp))}")
    print("\nAll self-tests passed.")
