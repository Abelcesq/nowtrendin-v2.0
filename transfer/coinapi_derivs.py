"""
coinapi_derivs.py — crypto DERIVATIVES POSITIONING accumulation (CoinAPI, §16-onboarded
2026-08-10, Chairman-ordered build). HELD-OUT, RECORD-ONLY: writes its own table,
feeds NO score, NO ledger, NO served value. The purpose is BASELINE ACCUMULATION so
a future board + backtest can judge wiring it into the crypto money leg on data.

WHY (the founder's money-movement order, integrity-compliant): trading volume is
NEVER flow (C5/C6, board-unanimous) — but derivatives POSITIONING is money data:
  • FUNDING RATE = the price of leverage (positive → longs pay shorts → long pressure)
  • OPEN INTEREST = capital committed to derivatives; its Δ = money entering/leaving
Both live-verified via CoinAPI 2026-08-10 (BTC perp funding 0.00005584, OI 105,683.596
BTC) and available for ALL 12 roster coins via Binance USDT perpetuals — the first
money-class source with full-roster coverage (ETF flow covers 2–3 coins; insider
proxies are sparse). Echoes the equity Money Gradient's leverage/positioning inputs.

§16 gate record: TYPE = market positioning (money) ✓ · ENGINE = held-out accumulation
now; crypto money leg ONLY after backtest-before-ship + board + Chairman flip ·
FORMAT = ISO-8601 instants, canonical dates via date_utils ✓ · CURRENCY+ACCESS =
pay-per-use Tier-1 account live-tested 200 ✓ · TEST→LINK→DEPLOY = this module.

CADENCE (founder-specified): once daily — the first opportunity after 00:00 UTC
(the "12:01 AM" pull), catch-up semantics (fires on the first check of each new UTC
day; a missed day is logged, never silently skipped). ~24 REST requests/day
(2 metrics × 12 coins), pay-per-use — cents.

FAIL-CLOSED: a coin whose metrics cannot be fetched gets NO row (declared absence,
logged) — never a fabricated or partial-guessed value. Forward-only, append-only
(PK coin+date, INSERT OR IGNORE); rows are never rewritten.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
_BASE = "https://rest.coinapi.io/v1"
_PAUSE_S = float(os.getenv("COINAPI_PAUSE_S", "2.5"))   # 429s observed at 1.0s (gate-5 test)

#: coin → CoinAPI perpetual symbol id (Binance USDT perps cover the full roster).
PERP_SYMBOLS = {
    "BTC": "BINANCEFTS_PERP_BTC_USDT",  "ETH": "BINANCEFTS_PERP_ETH_USDT",
    "SOL": "BINANCEFTS_PERP_SOL_USDT",  "XRP": "BINANCEFTS_PERP_XRP_USDT",
    "BNB": "BINANCEFTS_PERP_BNB_USDT",  "DOGE": "BINANCEFTS_PERP_DOGE_USDT",
    "ADA": "BINANCEFTS_PERP_ADA_USDT",  "AVAX": "BINANCEFTS_PERP_AVAX_USDT",
    "LINK": "BINANCEFTS_PERP_LINK_USDT", "DOT": "BINANCEFTS_PERP_DOT_USDT",
    "LTC": "BINANCEFTS_PERP_LTC_USDT",  "BCH": "BINANCEFTS_PERP_BCH_USDT",
}
_METRICS = {"funding_rate": "DERIVATIVES_FUNDING_RATE_CURRENT",
            "open_interest": "DERIVATIVES_OPEN_INTEREST"}


def _connect(db_path: str = DB_PATH):
    return db_compat.connect(db_path)


def init_derivs_db(db_path: str = DB_PATH):
    c = _connect(db_path)
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS coinapi_derivs (
                coin TEXT NOT NULL,
                signal_date TEXT NOT NULL,        -- canonical YYYY-MM-DD (§14), our capture day
                symbol_id TEXT,
                funding_rate REAL,                -- NULL = that metric was absent (declared)
                open_interest REAL,
                source_time TEXT,                 -- source's own entry_time HH:MM:SS (§14)
                signal_time TEXT,                 -- our fetch HH:MM:SS (§14)
                captured_at TEXT,                 -- full UTC instant
                src TEXT,                         -- 'coinapi'
                PRIMARY KEY (coin, signal_date)
            )
        """)
        c.commit()
    finally:
        c.close()


def _fetch_metric(api_key: str, symbol_id: str, metric_id: str):
    """One current-value read. Returns (value, entry_time_iso) or (None, None)."""
    import requests
    try:
        r = requests.get(f"{_BASE}/metrics/symbol/current",
                         params={"metric_id": metric_id, "symbol_id": symbol_id},
                         headers={"X-CoinAPI-Key": api_key}, timeout=25)
        if r.status_code == 429:                    # one paced retry (gate-5 finding)
            time.sleep(6)
            r = requests.get(f"{_BASE}/metrics/symbol/current",
                             params={"metric_id": metric_id, "symbol_id": symbol_id},
                             headers={"X-CoinAPI-Key": api_key}, timeout=25)
        if r.status_code != 200:
            print(f"[coinapi] {symbol_id} {metric_id}: HTTP {r.status_code}")
            return None, None
        rows = r.json() or []
        if not rows:
            return None, None
        v = rows[0].get("value_decimal")
        return (float(v) if v is not None else None), rows[0].get("entry_time")
    except Exception as e:
        print(f"[coinapi] {symbol_id} {metric_id}: {e}")
        return None, None


def snapshot_derivs(db_path: str = DB_PATH) -> dict:
    """One daily accumulation pass. Idempotent per (coin, date) — a second run on
    the same UTC day is a no-op per coin (ON CONFLICT DO NOTHING)."""
    api_key = os.getenv("COINAPI_KEY", "")
    out = {"date": None, "written": 0, "missing": [], "coins": {}}
    if os.getenv("COINAPI_DERIVS", "1") != "1" or not api_key:
        out["disabled"] = True
        return out
    try:
        import date_utils
        today = date_utils.to_iso_date(datetime.now(timezone.utc).isoformat())
    except Exception:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out["date"] = today
    init_derivs_db(db_path)
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat(timespec="seconds")
    sig_time = now.strftime("%H:%M:%S")
    try:
        for i, (coin, sym) in enumerate(PERP_SYMBOLS.items()):
            if i:
                time.sleep(_PAUSE_S)               # batch pacing (§13)
            fr, fr_t = _fetch_metric(api_key, sym, _METRICS["funding_rate"])
            time.sleep(_PAUSE_S)
            oi, oi_t = _fetch_metric(api_key, sym, _METRICS["open_interest"])
            if fr is None and oi is None:
                out["missing"].append(coin)        # declared absence, no row
                continue
            src_t = ""
            try:
                import date_utils
                src_t = date_utils.iso_time_of(fr_t or oi_t or "") or ""
            except Exception:
                pass
            c.execute(
                f"INSERT INTO coinapi_derivs (coin, signal_date, symbol_id, "
                f"funding_rate, open_interest, source_time, signal_time, "
                f"captured_at, src) VALUES ({','.join([ph]*9)}) "
                f"ON CONFLICT (coin, signal_date) DO NOTHING",
                (coin, today, sym, fr, oi, src_t, sig_time, now_iso, "coinapi"))
            out["written"] += 1
            out["coins"][coin] = {"funding_rate": fr, "open_interest": oi}
        c.commit()
    finally:
        c.close()
    try:
        import collector_health as _ch
        _ch.log_collector_run("coinapi_derivs", out["written"],
                              "success" if out["written"] else "failure",
                              db_path=db_path, distinct_keys=out["written"])
    except Exception:
        pass
    print(f"[coinapi] {today}: wrote {out['written']}/{len(PERP_SYMBOLS)} coins "
          f"(missing: {out['missing']})")
    return out


def has_row_for_today(db_path: str = DB_PATH) -> bool:
    """Daily catch-up gate: has ANY coin been recorded for the current UTC day?"""
    try:
        import date_utils
        today = date_utils.to_iso_date(datetime.now(timezone.utc).isoformat())
    except Exception:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    init_derivs_db(db_path)
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        row = c.execute(f"SELECT COUNT(*) AS n FROM coinapi_derivs "
                        f"WHERE signal_date = {ph}", (today,)).fetchone()
        n = row["n"] if hasattr(row, "keys") else row[0]
        return bool(n)
    except Exception:
        return False
    finally:
        c.close()


def derivs_report(db_path: str = DB_PATH, days: int = 14) -> dict:
    """Read-only accumulation report for /diag/coinapi — days covered per coin,
    latest values. Nothing else reads this table (held-out)."""
    init_derivs_db(db_path)
    c = _connect(db_path)
    try:
        rows = c.execute(
            "SELECT coin, COUNT(*) AS days_covered, MAX(signal_date) AS latest "
            "FROM coinapi_derivs GROUP BY coin ORDER BY coin").fetchall()
        out_rows = [dict(r) if hasattr(r, "keys") else
                    dict(zip(("coin", "days_covered", "latest"), r)) for r in rows]
    except Exception as e:
        return {"available": False, "reason": str(e)[:120]}
    finally:
        c.close()
    return {"available": True, "held_out": True,
            "note": "Baseline accumulation only — feeds no score; wiring into the "
                    "crypto money leg requires backtest-before-ship + board + "
                    "Chairman flip.",
            "coins": out_rows}
