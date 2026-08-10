"""
coinbase_premium.py — Coinbase RETAIL-SPOT premium accumulation (Chairman-ordered
2026-08-10; 5-day value review set for 2026-08-15). HELD-OUT, RECORD-ONLY.

WHAT + WHY: Coinbase's public retail spot rate embeds a retail spread (~0.5–2.0%
per the founder's fee comparison) over order-book/global prices — so its GAP vs a
reference price (the "Coinbase premium") is a recognized US-retail/institutional
DEMAND proxy, while the price itself is NOT a market price and must NEVER be
blended with market price data. Per the Chairman's explicit categorization order,
every row is labeled `price_class='coinbase_retail_spot'` — a SEPARATE category
from market prices, structurally (its own table; nothing joins it to price legs).

Mechanics: once daily (piggybacks the crypto daily-accumulation loop), keyless
public endpoint GET api.coinbase.com/v2/prices/{COIN}-USD/spot vs the FMP
reference quote ({COIN}USD). premium_pct = (coinbase - ref) / ref × 100.
BNB is not listed on Coinbase — expected declared absence, never an error.
Fail-closed: both legs present or no row. Forward-only; PK (coin, date).

5-DAY REVIEW (2026-08-15): does the premium series show variance/directionality
worth a full §16 workup as a demand signal? Until then: accumulation only; feeds
no score, no display.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
_PAUSE_S = float(os.getenv("COINBASE_PAUSE_S", "1.0"))
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX",
         "LINK", "DOT", "LTC", "BCH"]


def _connect(db_path: str = DB_PATH):
    return db_compat.connect(db_path)


def init_premium_db(db_path: str = DB_PATH):
    c = _connect(db_path)
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS coinbase_premium (
                coin TEXT NOT NULL,
                signal_date TEXT NOT NULL,        -- canonical YYYY-MM-DD (§14)
                coinbase_spot REAL,               -- RETAIL spot (embeds spread)
                reference_price REAL,             -- market reference (FMP quote)
                reference_src TEXT,               -- 'fmp'
                premium_pct REAL,                 -- (coinbase-ref)/ref*100
                price_class TEXT,                 -- 'coinbase_retail_spot' — NEVER a market price
                signal_time TEXT,
                captured_at TEXT,
                PRIMARY KEY (coin, signal_date)
            )
        """)
        c.commit()
    finally:
        c.close()


def snapshot_premium(db_path: str = DB_PATH) -> dict:
    """Daily premium accumulation. Idempotent per (coin, date)."""
    import requests
    out = {"written": 0, "missing": [], "coins": {}}
    if os.getenv("COINBASE_PREMIUM", "1") != "1":
        out["disabled"] = True
        return out
    fmp_key = os.getenv("FMP_API_KEY", "")
    try:
        import date_utils
        today = date_utils.to_iso_date(datetime.now(timezone.utc).isoformat())
    except Exception:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    init_premium_db(db_path)
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    now = datetime.now(timezone.utc)
    try:
        for i, coin in enumerate(COINS):
            if i:
                time.sleep(_PAUSE_S)
            cb = ref = None
            try:
                r = requests.get(
                    f"https://api.coinbase.com/v2/prices/{coin}-USD/spot",
                    timeout=20)
                if r.status_code == 200:
                    cb = float(((r.json() or {}).get("data") or {}).get("amount"))
            except Exception as e:
                print(f"[cb-premium] {coin} coinbase: {e}")
            if cb is not None and fmp_key:
                try:
                    r2 = requests.get(
                        f"https://financialmodelingprep.com/stable/quote-short",
                        params={"symbol": f"{coin}USD", "apikey": fmp_key},
                        timeout=20)
                    rows = r2.json() if r2.status_code == 200 else []
                    if rows:
                        ref = float(rows[0].get("price"))
                except Exception as e:
                    print(f"[cb-premium] {coin} fmp ref: {e}")
            if cb is None or ref is None or not ref:
                out["missing"].append(coin)       # declared absence (BNB expected)
                continue
            prem = round((cb - ref) / ref * 100.0, 4)
            c.execute(
                f"INSERT INTO coinbase_premium (coin, signal_date, coinbase_spot, "
                f"reference_price, reference_src, premium_pct, price_class, "
                f"signal_time, captured_at) VALUES ({','.join([ph]*9)}) "
                f"ON CONFLICT (coin, signal_date) DO NOTHING",
                (coin, today, cb, ref, "fmp", prem, "coinbase_retail_spot",
                 now.strftime("%H:%M:%S"), now.isoformat(timespec="seconds")))
            out["written"] += 1
            out["coins"][coin] = {"coinbase": cb, "ref": ref, "premium_pct": prem}
        c.commit()
    finally:
        c.close()
    try:
        import collector_health as _ch
        _ch.log_collector_run("coinbase_premium", out["written"],
                              "success" if out["written"] else "failure",
                              db_path=db_path, distinct_keys=out["written"])
    except Exception:
        pass
    print(f"[cb-premium] {today}: {out['written']}/{len(COINS)} coins "
          f"(missing {out['missing']})")
    return out


def has_row_for_today(db_path: str = DB_PATH) -> bool:
    try:
        import date_utils
        today = date_utils.to_iso_date(datetime.now(timezone.utc).isoformat())
    except Exception:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    init_premium_db(db_path)
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        row = c.execute(f"SELECT COUNT(*) AS n FROM coinbase_premium "
                        f"WHERE signal_date = {ph}", (today,)).fetchone()
        return bool(row["n"] if hasattr(row, "keys") else row[0])
    except Exception:
        return False
    finally:
        c.close()


def premium_report(db_path: str = DB_PATH) -> dict:
    """Read-only accumulation report (the 2026-08-15 review reads this)."""
    init_premium_db(db_path)
    c = _connect(db_path)
    try:
        rows = c.execute(
            "SELECT coin, COUNT(*) AS days, MIN(premium_pct) AS min_prem, "
            "MAX(premium_pct) AS max_prem, MAX(signal_date) AS latest "
            "FROM coinbase_premium GROUP BY coin ORDER BY coin").fetchall()
        cols = ("coin", "days", "min_prem", "max_prem", "latest")
        out_rows = [dict(r) if hasattr(r, "keys") else dict(zip(cols, r))
                    for r in rows]
    except Exception as e:
        return {"available": False, "reason": str(e)[:120]}
    finally:
        c.close()
    return {"available": True, "held_out": True,
            "price_class": "coinbase_retail_spot — NEVER a market price; the "
                           "PREMIUM (demand proxy) is the candidate signal",
            "review_due": "2026-08-15 (5-day value determination, Chairman-set)",
            "coins": out_rows}
