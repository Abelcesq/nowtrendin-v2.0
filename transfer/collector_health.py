"""
NOW TRENDIN — COLLECTOR HEALTH MONITOR (engine-native, db_compat)

The operational safety net. Records every collector run and surfaces a health
report so we know — before trusting any score — whether the data behind it is
complete. Half-blind collection (only some sources reporting) silently produced
bad scores on SpaceX, Nvidia, and software-development; this is the guard.

Adapted to our LIVE stack:
  - Uses db_compat (Postgres on Heroku), not raw sqlite3.
  - `critical` reflects only the collectors we actually run AND are licensed to
    use. Reddit (needs written commercial approval) and GDELT (429s from cloud)
    are intentionally NOT critical, so should_trust_scores() isn't stuck on NO.

Integration: each collector calls log_collector_run(name, n, status) after it
runs. GET /health serves the report; should_trust_scores() gates the dashboard.
"""
import os
from datetime import datetime, timezone, timedelta

try:
    import db_compat
except Exception:  # pragma: no cover
    db_compat = None

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# max_gap_minutes = how long since last success before "stale".
# critical = its absence makes the scores half-blind (only enabled+licensed ones).
COLLECTOR_EXPECTATIONS = {
    # Main collect cycle runs every COLLECT_INTERVAL_MIN (default 360 = 6h), so a
    # collector's freshness window MUST exceed the cadence + margin or it flaps
    # STALE between cycles. 7h (420m) = 6h cadence + 1h margin. (Earlier 120m
    # windows assumed a ~30-min cadence that no longer exists — the cause of the
    # false "STALE" on news/github/etc.)
    "github":        {"max_gap_minutes": 420, "mode": "attention", "critical": True},
    "hackernews":    {"max_gap_minutes": 420, "mode": "attention", "critical": True},
    "blogs":         {"max_gap_minutes": 420, "mode": "attention", "critical": False},
    "newsapi_org":   {"max_gap_minutes": 420, "mode": "attention", "critical": False},
    "newsapi_ai":    {"max_gap_minutes": 420, "mode": "attention", "critical": False},
    "newsdata_io":   {"max_gap_minutes": 420, "mode": "attention", "critical": False},
    # yahoo_finance REMOVED 2026-06-24 — RapidAPI 429/quota exhausted, 0 signals; collectors
    # disabled (YAHOO_FINANCE_ENABLED=0). Re-add this row if the source is ever restored.
    # Social/open-network collectors (keyless) — niche early-chatter tier.
    "bluesky":       {"max_gap_minutes": 420, "mode": "attention", "critical": False},
    "lemmy":         {"max_gap_minutes": 420, "mode": "attention", "critical": False},
    "mastodon":      {"max_gap_minutes": 420, "mode": "attention", "critical": False},
    # Discovery + mainstream (every 6 h)
    "google_trends": {"max_gap_minutes": 8 * 60,  "mode": "attention", "critical": True},
    "youtube":       {"max_gap_minutes": 8 * 60,  "mode": "attention", "critical": False},
    "gdelt":         {"max_gap_minutes": 8 * 60,  "mode": "attention", "critical": False},
    "creators":      {"max_gap_minutes": 8 * 60,  "mode": "attention", "critical": False},
    "broadcast":     {"max_gap_minutes": 8 * 60,  "mode": "attention", "critical": False},
    # Risk runs inside the main collect phase — every 6h (COLLECT_INTERVAL_MIN=360)
    "risk":          {"max_gap_minutes": 420, "mode": "risk", "critical": True},
    # Alpha Vantage retail/news coverage (free tier 25 req/day; supplementary)
    "alphavantage":  {"max_gap_minutes": 8 * 60, "mode": "risk", "critical": False},
    # ── S2 (Board 2026-07-28): sub-sources that can fail INDEPENDENTLY of their parent ──
    # The rule this encodes: any external endpoint that can fail on its own gets its own row
    # here and one log_collector_run() call at its call site. Both of these died unwatched
    # because `risk` stayed HEALTHY on its other sub-sources while these returned nothing —
    # the Finviz insider parser for ~30 days, Finnhub congressional on a repeated 403.
    # `min_distinct` is the dead-parser floor: rows arriving while distinct entities collapse.
    # Both start critical: False — a quiet source must DEGRADE, never block should_trust_scores.
    "finviz_insider": {"max_gap_minutes": 420, "mode": "risk", "critical": False,
                       "min_distinct": 8},
    # ⚠ ONE ROW PER INDEPENDENTLY-FAILING ENDPOINT. A single "finnhub" row was wrong: the
    # insider endpoint works while stock/congressional-trading 403s, so the combined row read
    # HEALTHY (409 stage-1) in the same cycle that logged four 403s — the sub-source failure
    # hidden by aggregation, exactly what this registry exists to expose. Verified live.
    "finnhub_insider":  {"max_gap_minutes": 420, "mode": "risk", "critical": False},
    # Issuer-page daily shares outstanding (A2.3 primary strike source, §16 survey
    # 2026-08-05, wired 2026-08-08). Runs with the 4h ETF snapshot loop → 240m + margin.
    # min_distinct guards the dead-parser mode (pages up but only 1-2 funds parsing).
    "issuer_shares": {"max_gap_minutes": 360, "mode": "risk", "critical": False,
                      "min_distinct": 5},
    # PER-FAMILY rows (board Q5, unanimous, Chairman-approved 2026-08-09 — the S2
    # one-row-per-independently-failing-endpoint rule): four issuers fail
    # independently (Grayscale's bot-wall proves the class); under the aggregate
    # alone, an entire family — including iShares/IBIT — could die while 5+ other
    # funds kept the row green. min_distinct = family size.
    "issuer_ishares":  {"max_gap_minutes": 360, "mode": "risk", "critical": False,
                        "min_distinct": 2},
    "issuer_bitwise":  {"max_gap_minutes": 360, "mode": "risk", "critical": False,
                        "min_distinct": 3},
    "issuer_21shares": {"max_gap_minutes": 360, "mode": "risk", "critical": False,
                        "min_distinct": 3},
    "issuer_canary":   {"max_gap_minutes": 360, "mode": "risk", "critical": False,
                        "min_distinct": 1},
    # RETIRED 2026-07-29: Finnhub's congressional endpoint is premium-gated on our plan and
    # returned 403 on every call, contributing zero rows. The call site is removed; this row is
    # marked disabled rather than DELETED so the failure history stays readable and it reports
    # DISABLED instead of a DOWN nobody should act on. Congress data now comes solely from
    # QUIVER (positioning_intel._build_congress), verified live at retirement.
    "finnhub_congress": {"max_gap_minutes": 420, "mode": "risk", "critical": False,
                         "disabled": True},
    # Socialcrawl rising-query discovery (§16 2026-08-07, armed 2026-08-08): runs on
    # 2 of the 4 daily 6h slots (00/12 UTC families) → 12h cadence + margin = 900m.
    # DISABLED-pattern while the flag is off so an intentional off-switch never
    # reads as a fault (the reddit lesson below).
    "socialcrawl":   {"max_gap_minutes": 900, "mode": "attention", "critical": False,
                      "disabled": os.getenv("SOCIALCRAWL_RISING", "0") != "1"},
    # Intentionally OFF (licensing) — DISABLED, not DEGRADED. It was reporting
    # "ran Nm ago but 0 signals" forever: a standing false amber on a source we chose to
    # switch off. A deliberate off-switch is not a fault.
    "reddit":        {"max_gap_minutes": 9999999, "mode": "attention", "critical": False,
                      "disabled": True},
}


def _conn(db_path, conn):
    if conn is not None:
        return conn, False
    return db_compat.connect(db_path), True


def init_health_db(db_path: str = DB_PATH, conn=None):
    c, own = _conn(db_path, conn)
    c.execute("""
        CREATE TABLE IF NOT EXISTS collector_health (
            collector TEXT PRIMARY KEY,
            last_success_at TEXT,
            last_run_at TEXT,
            last_signal_count INTEGER,
            consecutive_failures INTEGER DEFAULT 0,
            total_runs INTEGER DEFAULT 0,
            total_signals INTEGER DEFAULT 0,
            -- S2 (Board 2026-07-28): distinct entity keys seen on the last run. This is the
            -- ONE field that catches the dead-parser class — rows keep arriving and parse
            -- "successfully", but the distinct tickers/entities collapse to a handful. Row
            -- counts alone stayed green through a 30-day outage of the primary insider
            -- source; distinct keys would not have.
            last_distinct_keys INTEGER
        )
    """)
    for _ddl in ("ALTER TABLE collector_health ADD COLUMN last_distinct_keys INTEGER",
                 # S3-d: when we first became responsible for watching this collector. Without
                 # it, UNKNOWN has no expiry — and an UNKNOWN that never expires is a false
                 # GREEN hiding a corpse, the same defect facing the other way.
                 "ALTER TABLE collector_health ADD COLUMN registered_at TEXT"):
        try:
            c.execute(_ddl)
            c.commit()
        except Exception:
            try:
                c.rollback()  # PG: a failed ALTER aborts the txn; the registered_at stamps
            except Exception:  # below would otherwise silently fail every boot after the first
                pass
    # Stamp registration for every declared collector that has no row yet, so the grace
    # window is measured from when WE started watching, not from process start (a dyno
    # restart must not reset the clock).
    _now = datetime.now(timezone.utc).isoformat()
    for _name in COLLECTOR_EXPECTATIONS:
        try:
            c.execute("INSERT INTO collector_health (collector, registered_at) VALUES (?,?) "
                      "ON CONFLICT(collector) DO UPDATE SET "
                      "registered_at = COALESCE(collector_health.registered_at, excluded.registered_at)",
                      (_name, _now))
        except Exception:
            pass
    # Per-source, per-day API CALL counter (monitor usage/cost of every pull).
    c.execute("""
        CREATE TABLE IF NOT EXISTS api_usage (
            source TEXT NOT NULL,
            day TEXT NOT NULL,
            calls INTEGER DEFAULT 0,
            last_call_at TEXT,
            PRIMARY KEY (source, day)
        )
    """)
    c.commit()
    if own:
        c.close()


def log_api_call(source: str, n: int = 1, db_path: str = DB_PATH, conn=None):
    """Increment the API-call counter for an external data source (today).
    Best-effort — never breaks a collection path."""
    c, own = _conn(db_path, conn)
    now = datetime.now(timezone.utc)
    day = now.strftime("%Y-%m-%d")
    try:
        c.execute("""
            INSERT INTO api_usage (source, day, calls, last_call_at)
            VALUES (?,?,?,?)
            ON CONFLICT(source, day) DO UPDATE SET
                calls = api_usage.calls + excluded.calls,
                last_call_at = excluded.last_call_at
        """, (source, day, int(n), now.isoformat()))
        c.commit()
    except Exception as e:
        print(f"  api_usage log error ({source}): {e}")
    finally:
        if own:
            c.close()


def get_api_usage(db_path: str = DB_PATH, conn=None) -> dict:
    """Per-source API-call usage: today / last 7d / last 30d / all-time."""
    c, own = _conn(db_path, conn)
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    d7 = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    d30 = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    try:
        rows = c.execute("SELECT source, day, calls, last_call_at FROM api_usage").fetchall()
    except Exception:
        rows = []
    if own:
        c.close()
    agg: dict = {}
    for r in rows:
        s = r["source"]
        a = agg.setdefault(s, {"today": 0, "last_7d": 0, "last_30d": 0, "all_time": 0, "last_call_at": None})
        cd = r["calls"] or 0
        a["all_time"] += cd
        if r["day"] >= d30: a["last_30d"] += cd
        if r["day"] >= d7:  a["last_7d"] += cd
        if r["day"] == today: a["today"] += cd
        if not a["last_call_at"] or (r["last_call_at"] or "") > a["last_call_at"]:
            a["last_call_at"] = r["last_call_at"]
    total_today = sum(a["today"] for a in agg.values())
    total_30d = sum(a["last_30d"] for a in agg.values())
    return {"sources": dict(sorted(agg.items(), key=lambda kv: kv[1]["last_30d"], reverse=True)),
            "total_today": total_today, "total_last_30d": total_30d,
            "checked_at": now.isoformat()}


def log_collector_run(collector: str, signal_count: int = 0,
                      status: str = "success", db_path: str = DB_PATH, conn=None,
                      distinct_keys: int = None):
    """Record a collector run. Call at the end of every collector.
    status: 'success' (ran) | 'failure' (errored).

    `distinct_keys` (S2): how many DISTINCT entities the run actually covered — tickers,
    symbols, feeds. Optional, but pass it wherever it is meaningful: it is the only signal
    that separates "the source is quiet" from "the source is returning rows we can no longer
    parse", which is how the primary insider source stayed green for ~30 days while dead.
    """
    c, own = _conn(db_path, conn)
    now = datetime.now(timezone.utc).isoformat()
    try:
        row = c.execute(
            "SELECT consecutive_failures, last_success_at FROM collector_health WHERE collector = ?",
            (collector,)).fetchone()
        cons_fail = (row["consecutive_failures"] if row else 0) or 0
        prev_success = (row["last_success_at"] if row else None)
        if status == "success":
            new_fail, last_success = 0, now
        else:
            new_fail, last_success = cons_fail + 1, prev_success
        c.execute("""
            INSERT INTO collector_health
                (collector, last_success_at, last_run_at, last_signal_count,
                 consecutive_failures, total_runs, total_signals, last_distinct_keys)
            VALUES (?,?,?,?,?,?,?,?)
            ON CONFLICT(collector) DO UPDATE SET
                last_success_at = excluded.last_success_at,
                last_run_at = excluded.last_run_at,
                last_signal_count = excluded.last_signal_count,
                consecutive_failures = excluded.consecutive_failures,
                total_runs = collector_health.total_runs + 1,
                total_signals = collector_health.total_signals + excluded.last_signal_count,
                last_distinct_keys = excluded.last_distinct_keys
        """, (collector, last_success, now, signal_count, new_fail, 1, signal_count,
              distinct_keys))
        c.commit()
    except Exception as e:
        print(f"  collector_health log error ({collector}): {e}")
    finally:
        if own:
            c.close()


def _minutes_since(iso_str):
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 60
    except Exception:
        return None


def get_health_report(db_path: str = DB_PATH, conn=None) -> dict:
    c, own = _conn(db_path, conn)
    try:
        rows = {r["collector"]: dict(r) for r in
                c.execute("SELECT * FROM collector_health").fetchall()}
    except Exception:
        rows = {}
    if own:
        c.close()

    report = {}
    healthy = degraded = stale = down = unknown = disabled = 0
    critical_problems = []
    for name, exp in COLLECTOR_EXPECTATIONS.items():
        max_gap = exp["max_gap_minutes"]
        rec = rows.get(name)
        # ⚠ S3-d (Board 2026-07-28) — THE STATE MODEL, keyed on RUN EVIDENCE, not on success.
        # Two defects fixed here:
        #  (1) FALSE RED: a collector registered but not yet observed reported DOWN, identical
        #      to a genuinely dead one. Live proof: finnhub_insider (healthy) and
        #      finnhub_congress (403 x4/cycle) served the SAME text. §16a already forbids this
        #      for SCORES — a monitor with no observation must say UNKNOWN, exactly as a score
        #      with no baseline says absent.
        #  (2) UNREACHABLE ESCALATION: `elif fails >= 3` sat BELOW this branch, so a collector
        #      that ran many times and failed EVERY time could never escalate — it reported
        #      "never recorded a successful run", which is factually false. A source dead from
        #      birth was structurally un-escalatable. That is finnhub_congress exactly.
        # UNKNOWN is TIME-BOXED and can never be reached once a run has been observed, so
        # "I don't know" can never become a hiding place for a corpse.
        _ran = bool(rec and rec.get("last_run_at"))
        _fails = int((rec or {}).get("consecutive_failures") or 0)
        if exp.get("disabled"):
            status, detail = "DISABLED", "intentionally off — reported, never alarmed"
        elif not rec or not rec.get("last_success_at"):
            if _ran:
                status, detail = "DOWN", (
                    f"ran {int(_minutes_since(rec.get('last_run_at')) or 0)}m ago but has "
                    f"NEVER succeeded ({_fails} consecutive failures)")
            else:
                _reg_age = _minutes_since((rec or {}).get("registered_at") or "")
                if _reg_age is None or _reg_age <= 2 * max_gap:
                    status, detail = "UNKNOWN", (
                        "registered, no run observed yet — not an outage, not a pass")
                else:
                    status, detail = "DOWN", (
                        f"registered {int(_reg_age)}m ago; no run ever observed "
                        f"(instrumentation gap or dead call site)")
        else:
            mins = _minutes_since(rec["last_success_at"])
            sigs = rec.get("last_signal_count", 0) or 0
            fails = rec.get("consecutive_failures", 0) or 0
            if mins is None:
                status, detail = "DOWN", "unparseable timestamp"
            elif fails >= 3:
                status, detail = "DOWN", f"{fails} consecutive failures"
            elif mins > max_gap * 3:
                status, detail = "DOWN", f"last success {int(mins)}m ago"
            elif mins > max_gap:
                status, detail = "STALE", f"last success {int(mins)}m ago (window {max_gap}m)"
            elif sigs == 0:
                status, detail = "DEGRADED", f"ran {int(mins)}m ago but 0 signals"
            elif (exp.get("min_distinct") is not None
                  and rec.get("last_distinct_keys") is not None
                  and rec["last_distinct_keys"] < exp["min_distinct"]):
                # S2 — THE DEAD-PARSER SIGNATURE, generically. Rows arrive and parse
                # "successfully", but the distinct entities they cover collapse. This is the
                # one shape a row count cannot see, and it is exactly how the primary insider
                # source read HEALTHY for ~30 days while returning nothing usable.
                status, detail = "DEGRADED", (
                    f"coverage collapse: {sigs} rows but only {rec['last_distinct_keys']} "
                    f"distinct keys (floor {exp['min_distinct']}) — parse may be broken")
            else:
                status, detail = "HEALTHY", (
                    f"{sigs} signals {int(mins)}m ago"
                    + (f", {rec['last_distinct_keys']} distinct"
                       if rec.get("last_distinct_keys") is not None else ""))
        report[name] = {"status": status, "detail": detail,
                        "mode": exp["mode"], "critical": exp["critical"]}
        healthy += status == "HEALTHY"
        degraded += status == "DEGRADED"
        stale += status == "STALE"
        down += status == "DOWN"
        unknown += status == "UNKNOWN"
        disabled += status == "DISABLED"
        # UNKNOWN and DISABLED are NEVER critical: we do not page on absence of observation,
        # nor on a source we deliberately turned off. Criticality is earned by a first
        # successful observation.
        if exp["critical"] and status in ("STALE", "DOWN"):
            critical_problems.append(f"{name} ({status}: {detail})")

    return {
        "collectors": report,
        "summary": {"healthy": healthy, "degraded": degraded, "stale": stale,
                    "down": down, "unknown": unknown, "disabled": disabled,
                    "total": len(COLLECTOR_EXPECTATIONS)},
        "critical_problems": critical_problems,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def should_trust_scores(db_path: str = DB_PATH, conn=None) -> dict:
    report = get_health_report(db_path, conn=conn)
    problems = report["critical_problems"]
    trust = len(problems) == 0
    return {
        "trust": trust,
        "reason": ("All critical collectors healthy."
                   if trust else
                   "Critical collectors degraded — scores may be half-blind: "
                   + "; ".join(problems)),
        "summary": report["summary"],
    }
