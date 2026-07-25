"""
INSIDER FLOW — market-wide Form-4 ingestion + the money-movement observable. HELD-OUT.

Phase 2 of the Board's build sequence. Turns on the market-wide Finviz insider feed (which
we already pay for and which was dead code, reachable only under `__main__`) and accumulates
it into a proprietary panel — the series that, per the Economist, "exists only if you were
watching that day" and therefore cannot be bought later.

§16 GATE 5 FINDINGS — TESTED ON A LIVE SAMPLE BEFORE WIRING, AND IT MATTERED
────────────────────────────────────────────────────────────────────────────
200 live rows were run through the gate before a line of this module was written. Four
defects surfaced; all four are handled here rather than downstream:

**A. 26.5% of the feed is NOT Form 4.** 53 of 200 rows were `Proposed Sale` — a **Form 144
   notice of intent to sell**, not an executed transaction. The incumbent classifier is a
   substring test (`_SELL = {"sale", "sell"}`), and "Proposed Sale" contains "sale", so an
   *intention* was being counted as a completed insider sale.

**B. Those same 53 rows are COLUMN-MISALIGNED.** Form 144 rows carry a different cell count,
   and `_parse_insider` drops empty cells then takes `cells[:10]` — so every field shifts
   left. Observed: `shares_total='Jul 24 08:40 PM'` and `filed=None`. Any consumer reading
   those fields reads the wrong column. A and B are the same 53 rows: one root cause.

**C. The transaction date is not the public date.** The feed's `date` is when the insider
   traded; a live sample carried transactions as old as 2025-03-07 inside today's filings.
   Detection MUST be stamped on the FILED date — using the trade date would manufacture ~30+
   days of "lead" from information nobody had. (Board round 3, the Challenger: "the single
   most tempting and most invisible lie in the design.")

**D. The source caps at ~200 rows.** Asking for 500 returned 200 across 111 tickers. On a
   heavy filing day that silently truncates, and the dropped rows are exactly the cluster
   events the observable exists to detect. Every ingest writes a coverage watermark so a
   truncated day is visible rather than assumed complete.

⚠ NOTE FOR THE CHAIRMAN: defect A/B also affects the LIVE product. `finviz_data.insider_signal`
is the PRIMARY insider source, and its `flow` (inflow/outflow) is what the market accuracy
ledger enrolls on — so Form 144 intentions are currently contaminating live `flow`. That is a
separate fix to `finviz_data.py` and is NOT made here; this module simply refuses the rows.

PERSONAL DATA (day-one schema decision, Board round 3 — Expansionist)
─────────────────────────────────────────────────────────────────────
Form 4 names natural persons, and EU/UK equivalents (PDMR, MAR Art.19) will too. Identity is
needed to COUNT distinct insiders, not to display them. So `insider_events` stores only a
salted hash; names live in a separately-keyed `actor_reference` table with its own retention
clock, so an erasure request never has to touch the ledger — which by its own rule is never
deleted.

MEASUREMENT ONLY. Held out from scoring; see heldout_registry.
"""
from __future__ import annotations

import os
import re
import hashlib
from datetime import datetime, timezone
from typing import Optional

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
INSIDER_FLOW = os.getenv("INSIDER_FLOW", "0") == "1"

# Salt for actor pseudonymisation. MUST be set in production; a default salt is not a
# pseudonym. Ingest refuses to store identities without it rather than storing a
# trivially-reversible hash.
ACTOR_SALT = os.getenv("ACTOR_ID_SALT", "")

# Materiality floor. Deliberately separate from finviz_data.MIN_USD: the Board wants a
# float-relative floor eventually (an absolute dollar floor is size-biased and filters out
# precisely the small caps where the literature locates the signal). Absolute for now,
# flagged as a known limitation.
MIN_USD = float(os.getenv("INSIDER_FLOW_MIN_USD", "100000"))

_TS_LIKE = re.compile(r"^[A-Z][a-z]{2}\s+\d{1,2}\s+\d{1,2}:\d{2}\s*(AM|PM)$")


# ── Transaction classification (explicit, never substring) ──────────────────────────────

#: Exact-match classification. Substring matching is what let "Proposed Sale" become a sale.
_TXN_CLASS = {
    "buy": "P",                    # open-market purchase (Form 4 code P)
    "purchase": "P",
    "sale": "S",                   # open-market sale (Form 4 code S)
    "sell": "S",
    "option exercise": "M",        # derivative exercise — compensation, NOT money movement
    "proposed sale": "F144",       # Form 144 notice of INTENT — not an executed transaction
    "gift": "G",
    "award": "A",
}

#: Only these enter the observable. P is the signal (insider BUYING); S is retained for the
#: signed observable but is baselined, never treated as bearish on its own.
_SCORABLE = {"P", "S"}


def classify_transaction(raw: str) -> str:
    """Map a feed transaction string to a Form-4-style code. Unknown -> 'UNKNOWN' (counted,
    never silently bucketed) — an unrecognised string is a parser-drift signal, not a sale."""
    k = (raw or "").strip().lower()
    if k in _TXN_CLASS:
        return _TXN_CLASS[k]
    # Fall back conservatively: an exact phrase we do not know is UNKNOWN, not a guess.
    return "UNKNOWN"


def row_is_aligned(row: dict) -> bool:
    """Defect B: reject rows whose columns have shifted. A timestamp in `shares_total`, or a
    missing `filed`, means the parser mis-split this row and every field after the shift is
    the wrong column."""
    st = (row.get("shares_total") or "").strip()
    if _TS_LIKE.match(st):
        return False
    if not (row.get("filed") or "").strip():
        return False
    return True


def _num(v) -> Optional[float]:
    try:
        return float(str(v).replace(",", "").replace("$", "").strip())
    except (TypeError, ValueError):
        return None


def _canon(v) -> Optional[str]:
    try:
        from date_utils import to_iso_date
        return to_iso_date(v)
    except Exception:
        return None


def _filed_to_iso(filed: str, fallback_year: str = "") -> Optional[str]:
    """The feed's `filed` looks like 'Jul 24 09:42 PM' — no year. Resolve against today,
    rolling back a year if that would put the filing in the future (a Dec filing read in
    January). Routed through §14 canonicalization, never a raw slice."""
    s = (filed or "").strip()
    if not s:
        return None
    now = datetime.now(timezone.utc)
    for year in (now.year, now.year - 1):
        try:
            dt = datetime.strptime(f"{s} {year}", "%b %d %I:%M %p %Y")
        except ValueError:
            continue
        if dt.replace(tzinfo=timezone.utc) <= now:
            return _canon(dt.strftime("%Y-%m-%d"))
    return None


def actor_id(name: str) -> Optional[str]:
    """Salted hash of an insider's name. Returns None when no salt is configured — we store
    no identity at all rather than a reversible one."""
    if not ACTOR_SALT:
        return None
    return hashlib.sha256(f"{ACTOR_SALT}|{(name or '').strip().lower()}"
                          .encode()).hexdigest()[:24]


# ── Schema ──────────────────────────────────────────────────────────────────────────────

def init_insider_db(db_path: str = DB_PATH):
    conn = db_compat.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS insider_events (
            id TEXT PRIMARY KEY,
            ticker TEXT, signal_date TEXT, txn_date TEXT,
            actor_hash TEXT, role_raw TEXT, role_class TEXT,
            txn_code TEXT, value_usd REAL, shares REAL, price REAL,
            source TEXT, ingested_at TEXT)
    """)
    # Identity lives apart from the event, with its own retention clock (GDPR Art. 6/17).
    conn.execute("""
        CREATE TABLE IF NOT EXISTS actor_reference (
            actor_hash TEXT PRIMARY KEY, display_name TEXT, first_seen TEXT, last_seen TEXT)
    """)
    # Defect D: a truncated day must be visible, never assumed complete.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS insider_coverage (
            ingest_at TEXT PRIMARY KEY, rows_returned INTEGER, rows_requested INTEGER,
            distinct_tickers INTEGER, truncated INTEGER,
            rejected_misaligned INTEGER, rejected_form144 INTEGER, rejected_unknown INTEGER)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_universe (
            ticker TEXT PRIMARY KEY, first_seen TEXT, last_event_date TEXT,
            events_seen INTEGER DEFAULT 0, state TEXT DEFAULT 'candidate',
            admit_reason TEXT, promoted_at TEXT)
    """)
    for ddl in (
        "CREATE INDEX IF NOT EXISTS idx_ie_ticker ON insider_events(ticker)",
        "CREATE INDEX IF NOT EXISTS idx_ie_date ON insider_events(signal_date)",
        "CREATE INDEX IF NOT EXISTS idx_mu_state ON market_universe(state)",
    ):
        try:
            conn.execute(ddl)
        except Exception:
            pass
    conn.commit()
    conn.close()


# ── Ingest ──────────────────────────────────────────────────────────────────────────────

def ingest(db_path: str = DB_PATH, feed_fn=None, limit: int = 500) -> dict:
    """Pull the market-wide feed and accumulate it. Idempotent: the row id is a hash of the
    transaction's identifying fields, so re-ingesting the same feed writes nothing new.

    Returns a summary INCLUDING every rejection reason — what we refuse is part of the
    record, not an implementation detail.
    """
    if not INSIDER_FLOW:
        return {"ingested": False, "reason": "INSIDER_FLOW is not enabled"}

    if feed_fn is None:
        try:
            import finviz_data
            feed_fn = finviz_data.insider_feed
        except Exception as e:
            return {"ingested": False, "reason": f"feed unavailable ({e})"}

    try:
        rows = feed_fn(limit=limit) or []
    except Exception as e:
        return {"ingested": False, "reason": f"fetch failed ({e})"}

    now = datetime.now(timezone.utc).isoformat()
    stats = {"returned": len(rows), "requested": limit, "written": 0,
             "rejected_misaligned": 0, "rejected_form144": 0, "rejected_unknown": 0,
             "rejected_nonscorable": 0, "rejected_immaterial": 0, "rejected_nodate": 0,
             "tickers": set()}

    conn = db_compat.connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        for r in rows:
            code = classify_transaction(r.get("transaction"))
            # Defect A: Form 144 is an INTENT, not a transaction. Refuse it explicitly and
            # count it — it is 26.5% of the feed, so a silent drop would look like a
            # collection failure later.
            if code == "F144":
                stats["rejected_form144"] += 1
                continue
            # Defect B: column-shifted rows read the wrong fields. Refuse rather than ingest
            # a plausible-looking wrong number.
            if not row_is_aligned(r):
                stats["rejected_misaligned"] += 1
                continue
            if code == "UNKNOWN":
                stats["rejected_unknown"] += 1
                continue
            if code not in _SCORABLE:
                stats["rejected_nonscorable"] += 1      # M/A/G — compensation, not movement
                continue

            val = _num(r.get("value_usd"))
            if val is None or val < MIN_USD:
                stats["rejected_immaterial"] += 1
                continue

            # Defect C: stamp on the FILED date — when it became public.
            filed_iso = _filed_to_iso(r.get("filed"))
            if not filed_iso:
                stats["rejected_nodate"] += 1
                continue
            try:
                import finviz_data as _fv
                txn_iso = _canon(_fv._parse_finviz_date(r.get("date")))
            except Exception:
                txn_iso = None

            tkr = (r.get("ticker") or "").upper().strip()
            name = r.get("owner") or ""
            ah = actor_id(name)
            rid = hashlib.md5(
                f"{tkr}|{txn_iso}|{filed_iso}|{name}|{code}|{val}".encode()).hexdigest()[:16]
            role_raw = (r.get("relationship") or "").strip()

            # ⚠ Count ACTUAL inserts via rowcount, never loop iterations. Incrementing a
            # counter next to `ON CONFLICT DO NOTHING` is exactly the defect the Board found
            # in flow_ledger.enroll() (round 4, D1), where it made a swallowed insert look
            # like a successful write. Same shape, same fix.
            cur = conn.execute(
                f"INSERT INTO insider_events (id,ticker,signal_date,txn_date,actor_hash,"
                f"role_raw,role_class,txn_code,value_usd,shares,price,source,ingested_at) "
                f"VALUES ({','.join([ph]*13)}) ON CONFLICT (id) DO NOTHING",
                (rid, tkr, filed_iso, txn_iso, ah, role_raw, _role_class(role_raw), code,
                 val, _num(r.get("shares")), _num(r.get("cost")), "finviz", now))
            try:
                inserted = cur is not None and cur.rowcount != 0
            except Exception:
                inserted = True
            if not inserted:
                stats["duplicates"] = stats.get("duplicates", 0) + 1
                continue
            if ah:
                conn.execute(
                    f"INSERT INTO actor_reference (actor_hash,display_name,first_seen,"
                    f"last_seen) VALUES ({ph},{ph},{ph},{ph}) "
                    f"ON CONFLICT (actor_hash) DO UPDATE SET last_seen=EXCLUDED.last_seen",
                    (ah, name, now, now))
            conn.execute(
                f"INSERT INTO market_universe (ticker,first_seen,last_event_date,"
                f"events_seen,state,admit_reason) VALUES ({ph},{ph},{ph},1,'candidate',"
                f"'insider filing') ON CONFLICT (ticker) DO UPDATE SET "
                f"last_event_date=EXCLUDED.last_event_date, "
                f"events_seen=market_universe.events_seen+1",
                (tkr, now, filed_iso))
            stats["written"] += 1
            stats["tickers"].add(tkr)

        # Defect D: judge truncation on the SOURCE's raw row count, not on what survived
        # parsing — dropping malformed rows would otherwise make a capped day look uncapped.
        raw_rows = len(rows)
        try:
            import finviz_data as _fv
            raw_rows = max(raw_rows, _fv.last_feed_raw_rows())
        except Exception:
            pass
        truncated = 1 if raw_rows >= 200 else 0      # observed source cap
        conn.execute(
            f"INSERT INTO insider_coverage (ingest_at,rows_returned,rows_requested,"
            f"distinct_tickers,truncated,rejected_misaligned,rejected_form144,"
            f"rejected_unknown) VALUES ({','.join([ph]*8)}) "
            f"ON CONFLICT (ingest_at) DO NOTHING",
            (now, len(rows), limit, len(stats["tickers"]), truncated,
             stats["rejected_misaligned"], stats["rejected_form144"],
             stats["rejected_unknown"]))
        conn.commit()
    finally:
        conn.close()

    stats["tickers"] = len(stats["tickers"])
    stats["ingested"] = True
    stats["source_raw_rows"] = raw_rows
    stats["truncated"] = bool(truncated)
    stats["actor_identities_stored"] = bool(ACTOR_SALT)
    return stats


def _role_class(role_raw: str) -> str:
    """Coarse role bucket for the Seyhun-grounded weighting (officers > directors > 10%)."""
    r = (role_raw or "").lower()
    if any(k in r for k in ("ceo", "chief executive", "president")):
        return "ceo"
    if any(k in r for k in ("cfo", "chief financial", "fin.")):
        return "cfo"
    if "10%" in r:
        return "ten_pct"
    if "director" in r or "board" in r:
        return "director"
    if "officer" in r or "chief" in r or "svp" in r or "evp" in r or "vp" in r:
        return "officer"
    return "other"


def status(db_path: str = DB_PATH) -> dict:
    """Read-only health for the monitoring fleet."""
    conn = db_compat.connect(db_path)
    try:
        def one(q):
            try:
                r = conn.execute(q).fetchone()
                return (dict(r) if hasattr(r, "keys") else {"n": r[0]}) if r else {}
            except Exception:
                return {}
        ev = one("SELECT COUNT(*) AS n FROM insider_events")
        uni = one("SELECT COUNT(*) AS n FROM market_universe")
        cov = one("SELECT * FROM insider_coverage ORDER BY ingest_at DESC LIMIT 1")
        return {"enabled": INSIDER_FLOW, "events": ev.get("n"),
                "universe": uni.get("n"), "last_coverage": cov,
                "identities_stored": bool(ACTOR_SALT)}
    finally:
        conn.close()


if __name__ == "__main__":
    import json, tempfile
    print("=== insider_flow self-test (sqlite temp db, synthetic feed) ===\n")

    # Classification must be EXACT — this is the defect-A regression.
    assert classify_transaction("Buy") == "P"
    assert classify_transaction("Sale") == "S"
    assert classify_transaction("Proposed Sale") == "F144", "Form 144 must NOT be a sale"
    assert classify_transaction("Option Exercise") == "M"
    assert classify_transaction("Something New") == "UNKNOWN", "unknown must not be guessed"
    print("classification: 'Proposed Sale' -> F144 (NOT S)  OK")

    # Alignment must reject the shifted rows — defect B.
    assert not row_is_aligned({"shares_total": "Jul 24 08:40 PM", "filed": None})
    assert row_is_aligned({"shares_total": "501,648", "filed": "Jul 24 09:42 PM"})
    print("alignment: timestamp-in-shares_total row rejected  OK")

    tmp = os.path.join(tempfile.gettempdir(), "insider_flow_selftest.db")
    if os.path.exists(tmp):
        os.remove(tmp)
    init_insider_db(tmp)

    feed = [
        {"ticker": "AAA", "owner": "Jane Doe", "relationship": "Chief Executive Officer",
         "date": "Jul 23 '26", "transaction": "Buy", "cost": "10.00", "shares": "50,000",
         "value_usd": "500,000", "shares_total": "100,000", "filed": "Jul 24 09:42 PM"},
        {"ticker": "BBB", "owner": "John Roe", "relationship": "10% Owner",
         "date": "Jul 22 '26", "transaction": "Proposed Sale", "cost": "21.25",
         "shares": "325,000", "value_usd": "6,906,250",
         "shares_total": "Jul 24 08:40 PM", "filed": None},          # F144 + misaligned
        {"ticker": "CCC", "owner": "Ann Poe", "relationship": "Director",
         "date": "Jul 21 '26", "transaction": "Option Exercise", "cost": "5.00",
         "shares": "1,000", "value_usd": "5,000,000", "shares_total": "9,000",
         "filed": "Jul 24 07:00 PM"},                                 # compensation
        {"ticker": "DDD", "owner": "Tim Foe", "relationship": "Officer",
         "date": "Jul 20 '26", "transaction": "Buy", "cost": "2.00", "shares": "100",
         "value_usd": "200", "shares_total": "900", "filed": "Jul 24 06:00 PM"},  # immaterial
    ]
    os.environ["INSIDER_FLOW"] = "1"
    import importlib, sys as _s
    _m = _s.modules[__name__]
    _m.INSIDER_FLOW = True

    out = ingest(db_path=tmp, feed_fn=lambda limit=500: feed)
    print(f"\ningest: {json.dumps({k: v for k, v in out.items() if k != 'tickers'})}")
    assert out["written"] == 1, out
    assert out["rejected_form144"] == 1, out
    assert out["rejected_nonscorable"] == 1, out
    assert out["rejected_immaterial"] == 1, out
    print("  1 written (the real buy); F144, option-exercise and immaterial all refused  OK")

    # Idempotent
    out2 = ingest(db_path=tmp, feed_fn=lambda limit=500: feed)
    assert out2["written"] == 0, out2
    print("  re-ingest writes 0 (idempotent)  OK")

    # No salt configured -> no identity stored
    assert actor_id("Jane Doe") is None or ACTOR_SALT
    print(f"  identities stored: {bool(ACTOR_SALT)} (no salt -> no identity, by design)  OK")

    print(f"\nstatus: {json.dumps(status(tmp))}")
    print("\nAll self-tests passed.")
