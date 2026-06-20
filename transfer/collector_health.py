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
    "yahoo_finance": {"max_gap_minutes": 420, "mode": "attention", "critical": False},
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
    # Intentionally OFF (licensing) — tracked but never critical
    "reddit":        {"max_gap_minutes": 9999999, "mode": "attention", "critical": False},
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
            total_signals INTEGER DEFAULT 0
        )
    """)
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
                      status: str = "success", db_path: str = DB_PATH, conn=None):
    """Record a collector run. Call at the end of every collector.
    status: 'success' (ran) | 'failure' (errored)."""
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
                 consecutive_failures, total_runs, total_signals)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(collector) DO UPDATE SET
                last_success_at = excluded.last_success_at,
                last_run_at = excluded.last_run_at,
                last_signal_count = excluded.last_signal_count,
                consecutive_failures = excluded.consecutive_failures,
                total_runs = collector_health.total_runs + 1,
                total_signals = collector_health.total_signals + excluded.last_signal_count
        """, (collector, last_success, now, signal_count, new_fail, 1, signal_count))
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
    healthy = degraded = stale = down = 0
    critical_problems = []
    for name, exp in COLLECTOR_EXPECTATIONS.items():
        max_gap = exp["max_gap_minutes"]
        rec = rows.get(name)
        if not rec or not rec.get("last_success_at"):
            status, detail = "DOWN", "never recorded a successful run"
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
            else:
                status, detail = "HEALTHY", f"{sigs} signals {int(mins)}m ago"
        report[name] = {"status": status, "detail": detail,
                        "mode": exp["mode"], "critical": exp["critical"]}
        healthy += status == "HEALTHY"
        degraded += status == "DEGRADED"
        stale += status == "STALE"
        down += status == "DOWN"
        if exp["critical"] and status in ("STALE", "DOWN"):
            critical_problems.append(f"{name} ({status}: {detail})")

    return {
        "collectors": report,
        "summary": {"healthy": healthy, "degraded": degraded, "stale": stale,
                    "down": down, "total": len(COLLECTOR_EXPECTATIONS)},
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
