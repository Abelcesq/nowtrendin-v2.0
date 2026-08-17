"""
coinmetrics_onchain.py — crypto ON-CHAIN ACTIVITY accumulation (CoinMetrics Community
API v4, §16-onboarded 2026-08-16, Chairman-ordered build; access-tested PASS 2026-08-10).
HELD-OUT, RECORD-ONLY: writes its own table, feeds NO score, NO ledger, NO served
value. Purpose is BASELINE ACCUMULATION so a future board + backtest can judge wiring
on-chain activity into the crypto leg on data — the genuine $0 on-chain path the
Chairman ruled for after Glassnode was priced out.

WHAT IT TAKES (community tier, live-verified 2026-08-16):
  • AdrActCnt = distinct active addresses that day (network usage by PEOPLE)
  • TxCnt     = settled transactions that day (network usage by ACTIVITY)
Both are genuine on-chain facts from the public ledger — not exchange volume (which
C5/C6 prohibit as an on-chain proxy) and not attention data.

WHAT THE FREE TIER DOES **NOT** SERVE (probed metric-by-metric 2026-08-16; recorded
so the temptation is pre-refused): TxTfrValAdjUSD (the C5/NVT denominator), FeeTotUSD,
CapRealUSD (the C6 realized cap), NVTAdj — all HTTP 403 = paid tier. Therefore the
C5/C6 shelf triggers (audits/DEFERRED_ITEMS.md) DO NOT FIRE on this onboarding; they
require the specific fields, and substituting activity counts for value transferred
would be a different metric wearing the name.

COVERAGE (probed per-asset 2026-08-16 — declared absence, never guessed):
  CURRENT (9): btc eth xrp doge ada link ltc bch + avax via the 'avaxc' C-Chain id.
  ABSENT  (3): SOL (community catalog has NO free on-chain metrics — only reference
  rates + reported spot volume, which C5 prohibits); BNB (community series is the
  dead BEP2 chain, frozen 2019 — the live BSC chain is paid); DOT (series frozen
  2022-06). These serve NO row: absent, not zero.

STALENESS GUARD (the BNB gotcha): a 200 response can carry a years-old row. Any
metric row older than CM_MAX_AGE_DAYS (7) is treated as declared absence, not data.

§16 gate record: TYPE = on-chain network activity (reference/positioning-adjacent,
NOT attention, NOT price) ✓ · ENGINE = held-out accumulation now; any score wiring
only after backtest-before-ship + board + Chairman flip ✓ · FORMAT = source serves
ISO-8601 day timestamps → canonical signal_date via date_utils; integers ✓ ·
CURRENCY+ACCESS = keyless community endpoint, HTTP 200, data through yesterday,
per-coin probes archived in SESSION_LOG 2026-08-16 ✓ · TEST→LINK→DEPLOY = this
module, live-sampled before wiring ✓.

CADENCE: once daily, catch-up semantics (piggybacks the coinapi/coinbase daily loop).
CoinMetrics finalizes a UTC day ~a few hours after it closes, so each pull asks for
YESTERDAY's completed day. 9 keyless requests/day. FAIL-CLOSED: a coin whose fetch
fails, returns empty, or returns stale gets NO row. Forward-only, append-only
(PK coin+signal_date, ON CONFLICT DO NOTHING); rows are never rewritten.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone, timedelta

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
_BASE = "https://community-api.coinmetrics.io/v4"
_PAUSE_S = float(os.getenv("COINMETRICS_PAUSE_S", "1.0"))
_MAX_AGE_DAYS = int(os.getenv("CM_MAX_AGE_DAYS", "7"))

#: roster coin → CoinMetrics community asset id. None = declared absence (see header).
ASSET_IDS = {
    "BTC": "btc",   "ETH": "eth",  "SOL": None,     "XRP": "xrp",
    "BNB": None,    "DOGE": "doge", "ADA": "ada",   "AVAX": "avaxc",
    "LINK": "link", "DOT": None,   "LTC": "ltc",    "BCH": "bch",
}
_METRICS = "AdrActCnt,TxCnt"


def _connect(db_path: str = DB_PATH):
    return db_compat.connect(db_path)


def init_onchain_db(db_path: str = DB_PATH):
    c = _connect(db_path)
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS coinmetrics_onchain (
                coin TEXT NOT NULL,
                signal_date TEXT NOT NULL,        -- canonical YYYY-MM-DD (§14) = the METRIC's own completed UTC day
                asset_id TEXT,
                adr_act_cnt REAL,                 -- NULL = that metric absent for the day (declared)
                tx_cnt REAL,
                source_time TEXT,                 -- source is date-only → '' (§14)
                signal_time TEXT,                 -- our fetch HH:MM:SS (§14)
                captured_at TEXT,                 -- full UTC instant
                src TEXT,                         -- 'coinmetrics_community'
                PRIMARY KEY (coin, signal_date)
            )
        """)
        c.commit()
    finally:
        c.close()


def _fetch_asset_day(asset_id: str, day_iso: str):
    """Fetch AdrActCnt+TxCnt for one asset for one completed UTC day.
    Returns (adr_act_cnt, tx_cnt, metric_day_iso) or (None, None, None)."""
    import requests
    try:
        r = requests.get(f"{_BASE}/timeseries/asset-metrics",
                         params={"assets": asset_id, "metrics": _METRICS,
                                 "frequency": "1d", "page_size": 3,
                                 "start_time": day_iso, "end_time": day_iso},
                         headers={"User-Agent": "NowTrendIn/2.0 (+onchain)"},
                         timeout=25)
        if r.status_code == 429:                    # one paced retry
            time.sleep(6)
            r = requests.get(f"{_BASE}/timeseries/asset-metrics",
                             params={"assets": asset_id, "metrics": _METRICS,
                                     "frequency": "1d", "page_size": 3,
                                     "start_time": day_iso, "end_time": day_iso},
                             headers={"User-Agent": "NowTrendIn/2.0 (+onchain)"},
                             timeout=25)
        if r.status_code != 200:
            print(f"[coinmetrics] {asset_id}: HTTP {r.status_code}")
            return None, None, None
        rows = (r.json() or {}).get("data") or []
        if not rows:
            return None, None, None
        row = rows[-1]
        t = str(row.get("time") or "")[:10]
        adr = row.get("AdrActCnt")
        tx = row.get("TxCnt")
        return (float(adr) if adr is not None else None,
                float(tx) if tx is not None else None, t or None)
    except Exception as e:
        print(f"[coinmetrics] {asset_id}: {e}")
        return None, None, None


def snapshot_onchain(db_path: str = DB_PATH) -> dict:
    """One daily accumulation pass for YESTERDAY's completed UTC day. Idempotent
    per (coin, metric-day) — a second run on the same day is a no-op per coin."""
    out = {"date": None, "written": 0, "missing": [], "absent_by_design": [],
           "coins": {}}
    if os.getenv("COINMETRICS_ONCHAIN", "1") != "1":
        out["disabled"] = True
        return out
    now = datetime.now(timezone.utc)
    target = now - timedelta(days=1)
    try:
        import date_utils
        day = date_utils.to_iso_date(target.isoformat())
    except Exception:
        day = target.strftime("%Y-%m-%d")
    out["date"] = day
    floor = (now - timedelta(days=_MAX_AGE_DAYS)).strftime("%Y-%m-%d")
    init_onchain_db(db_path)
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    now_iso = now.isoformat(timespec="seconds")
    sig_time = now.strftime("%H:%M:%S")
    try:
        req_i = 0
        for coin, asset_id in ASSET_IDS.items():
            if asset_id is None:
                out["absent_by_design"].append(coin)   # SOL/BNB/DOT — no row, ever
                continue
            if req_i:
                time.sleep(_PAUSE_S)                   # batch pacing (§13)
            req_i += 1
            adr, tx, metric_day = _fetch_asset_day(asset_id, day)
            if (adr is None and tx is None) or not metric_day:
                out["missing"].append(coin)            # declared absence, no row
                continue
            if metric_day < floor:                     # the BNB stale-series gotcha
                print(f"[coinmetrics] {coin}: stale series ({metric_day}) — absent")
                out["missing"].append(coin)
                continue
            try:
                import date_utils
                sd = date_utils.to_iso_date(metric_day) or metric_day
            except Exception:
                sd = metric_day
            c.execute(
                f"INSERT INTO coinmetrics_onchain (coin, signal_date, asset_id, "
                f"adr_act_cnt, tx_cnt, source_time, signal_time, captured_at, src) "
                f"VALUES ({','.join([ph]*9)}) "
                f"ON CONFLICT (coin, signal_date) DO NOTHING",
                (coin, sd, asset_id, adr, tx, "", sig_time, now_iso,
                 "coinmetrics_community"))
            out["written"] += 1
            out["coins"][coin] = {"adr_act_cnt": adr, "tx_cnt": tx, "day": sd}
        c.commit()
    finally:
        c.close()
    try:
        import collector_health as _ch
        _ch.log_collector_run("coinmetrics_onchain", out["written"],
                              "success" if out["written"] else "failure",
                              db_path=db_path, distinct_keys=out["written"])
    except Exception:
        pass
    print(f"[coinmetrics] {day}: wrote {out['written']}/9 covered coins "
          f"(missing: {out['missing']}; absent-by-design: {out['absent_by_design']})")
    return out


def has_row_for_day(db_path: str = DB_PATH) -> bool:
    """Daily catch-up gate: do we already hold YESTERDAY's completed day?"""
    target = datetime.now(timezone.utc) - timedelta(days=1)
    try:
        import date_utils
        day = date_utils.to_iso_date(target.isoformat())
    except Exception:
        day = target.strftime("%Y-%m-%d")
    init_onchain_db(db_path)
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        row = c.execute(f"SELECT COUNT(*) AS n FROM coinmetrics_onchain "
                        f"WHERE signal_date = {ph}", (day,)).fetchone()
        n = row["n"] if hasattr(row, "keys") else row[0]
        return bool(n)
    except Exception:
        return False
    finally:
        c.close()


def onchain_report(db_path: str = DB_PATH) -> dict:
    """Read-only accumulation report for /diag/coinmetrics — days covered per coin,
    latest values. Nothing else reads this table (held-out)."""
    init_onchain_db(db_path)
    c = _connect(db_path)
    try:
        rows = c.execute(
            "SELECT coin, COUNT(*) AS days_covered, MAX(signal_date) AS latest "
            "FROM coinmetrics_onchain GROUP BY coin ORDER BY coin").fetchall()
        out_rows = [dict(r) if hasattr(r, "keys") else
                    dict(zip(("coin", "days_covered", "latest"), r)) for r in rows]
    except Exception as e:
        return {"available": False, "reason": str(e)[:120]}
    finally:
        c.close()
    return {"available": True, "held_out": True,
            "note": "On-chain activity baseline accumulation only (AdrActCnt/TxCnt, "
                    "CoinMetrics community) — feeds no score; any wiring requires "
                    "backtest-before-ship + board + Chairman flip. SOL/BNB/DOT are "
                    "absent by design (no free current on-chain series).",
            "absent_by_design": ["SOL", "BNB", "DOT"],
            "coins": out_rows}
