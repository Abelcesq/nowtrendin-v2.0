"""
etf_flow.py — spot-crypto ETF CREATION/REDEMPTION flow. HELD-OUT, RECORD-ONLY.

WHY THIS EXISTS
───────────────
The crypto Money Movement leg reads insider Form-4 filings on crypto-exposure equities. The
Board's unanimous finding (2026-07-29): five of the seven proxies — IBIT, FBTC, GBTC, ETHA,
ETHE — are ETFs and trusts, which have NO insiders and file no Form 4s, ever. The instrument
was pointed at the right tickers and reading a document that does not exist for them. Measured
consequence: 11 of 12 coins can NEVER produce a money read.

The field that DOES exist on those tickers, daily and publicly, is the one a desk actually
watches: net creations and redemptions. Shares outstanding rising = dollars in; falling =
dollars out. That is institutional crypto flow as the market defines it, it is two-sided
(unlike the accumulation-only insider vote, which can express nothing but inflow), and it is
already covered by a subscription we pay for.

⚠ SHARES, NEVER AUM — THE CIRCULARITY TRAP (Executioner)
────────────────────────────────────────────────────────
`AUM = shares x NAV`, and NAV tracks the coin. An AUM-delta "money movement" would therefore be
driven by the very price series that drives Market Confirmation — a circular metric, which the
integrity standard bans outright. Dividing AUM by NAV removes the price and leaves the pure
quantity. This module records `shares`; anything downstream must use it, never `aum`.

WHAT THIS MODULE DOES *NOT* DO
──────────────────────────────
It does not vote, score, or feed any served value. §16 gate 4 has passed on ACCESS (verified
2026-07-29: etf/info returns AUM + NAV for all five proxies on the paid plan) but NOT on
CURRENCY — nobody has yet shown these share counts actually move day to day at a usable
resolution. That takes ~a week of observation, which is what this module starts. Wiring a vote
before that evidence exists would repeat the mistake it was built to correct.

Scope, stated honestly: even fully wired, this fixes BTC (3 votable proxies) and ETH (2). The
ten COIN-only coins remain structurally unreadable. This is 2 of 12, not a crypto fix.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

#: The spot-crypto ETF roster. DERIVED from crypto_signals.COIN_UNIVERSE (kind=="etf") so a
#: proxy added there starts its §16 gate-4 CURRENCY clock automatically — the Challenger
#: caught this list still hard-coded to the original five while the Board was being asked to
#: flip SOL/XRP on evidence that was never being collected for them. One source of truth;
#: the tuple below survives only as the fallback if the import ever fails.
_FALLBACK_PROXIES = ("IBIT", "FBTC", "GBTC", "ETHA", "ETHE")


def _roster() -> tuple:
    try:
        import crypto_signals as _cs
        out, seen = [], set()
        for c in _cs.COIN_UNIVERSE.values():
            for pr in (c.get("proxies") or []):
                tk = pr.get("ticker")
                if pr.get("kind") == "etf" and tk and tk not in seen:
                    seen.add(tk)
                    out.append(tk)
        return tuple(out) if out else _FALLBACK_PROXIES
    except Exception:
        return _FALLBACK_PROXIES


ETF_PROXIES = _roster()


def _connect(db_path: str = DB_PATH):
    conn = db_compat.connect(db_path)
    if not db_compat.USE_PG:
        try:
            import sqlite3
            conn.row_factory = sqlite3.Row
        except Exception:
            pass
    return conn


def init_etf_db(db_path: str = DB_PATH, conn=None):
    """Additive, forward-only DDL. Safe to call repeatedly."""
    c = conn or _connect(db_path)
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS etf_share_snapshots (
                ticker TEXT NOT NULL,
                snapshot_date TEXT NOT NULL,      -- canonical YYYY-MM-DD (§14)
                shares REAL,                      -- AUM / NAV — the price-independent quantity
                aum REAL,                         -- context only; NEVER the flow signal
                nav REAL,
                captured_at TEXT,
                PRIMARY KEY (ticker, snapshot_date)
            )
        """)
        c.commit()
    finally:
        if conn is None:
            c.close()


def snapshot(db_path: str = DB_PATH, tickers=None) -> dict:
    """Record today's share count for each ETF proxy. Idempotent per (ticker, date).

    Called once per collect cycle. One cheap read per ETF against a source we already pay for.
    RECORD-ONLY: nothing here is served or scored.
    """
    import fmp_data
    try:
        import date_utils
        today = date_utils.to_iso_date(datetime.now(timezone.utc).isoformat()) or \
            datetime.now(timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    out = {"date": today, "written": 0, "missing": [], "tickers": {}}
    init_etf_db(db_path)
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        for t in (tickers or ETF_PROXIES):
            info = None
            try:
                info = fmp_data.etf_info(t)
            except Exception as e:
                print(f"[etf-flow] {t}: {e}")
            if not info or not info.get("shares"):
                out["missing"].append(t)
                continue
            try:
                c.execute(
                    f"INSERT INTO etf_share_snapshots "
                    f"(ticker,snapshot_date,shares,aum,nav,captured_at) "
                    f"VALUES ({ph},{ph},{ph},{ph},{ph},{ph}) "
                    f"ON CONFLICT (ticker,snapshot_date) DO NOTHING",
                    (t, today, info["shares"], info["aum"], info["nav"],
                     datetime.now(timezone.utc).isoformat(timespec="seconds")))
                out["written"] += 1
                out["tickers"][t] = round(info["shares"])
            except Exception as e:
                print(f"[etf-flow] {t} write: {e}")
        c.commit()
    finally:
        c.close()
    return out


def currency_report(db_path: str = DB_PATH) -> dict:
    """§16 GATE 4 (CURRENCY) EVIDENCE — do these share counts actually MOVE?

    Access is proven; currency is not. A field that is published but static is useless as a
    flow signal, and assuming otherwise is how the insider path shipped in the first place.
    This reports, per ETF, how many distinct daily values we have observed and the largest
    day-over-day change — the evidence a human needs before anyone wires a vote.
    """
    c = _connect(db_path)
    try:
        rows = [dict(r) for r in c.execute(
            "SELECT ticker, snapshot_date, shares FROM etf_share_snapshots "
            "ORDER BY ticker, snapshot_date").fetchall()]
    except Exception as e:
        return {"available": False, "reason": str(e)[:120]}
    finally:
        c.close()
    by = {}
    for r in rows:
        by.setdefault(r["ticker"], []).append(r)
    out = {"available": bool(rows), "days_observed": len({r["snapshot_date"] for r in rows}),
           "tickers": {}, "verdict": "insufficient observations"}
    movers = 0
    for t, rs in by.items():
        vals = [r["shares"] for r in rs if r["shares"]]
        deltas = [round(100.0 * (b - a) / a, 3)
                  for a, b in zip(vals, vals[1:]) if a]
        moved = any(abs(d) > 0.01 for d in deltas)
        movers += 1 if moved else 0
        out["tickers"][t] = {"observations": len(vals), "distinct_values": len(set(vals)),
                             "pct_changes": deltas[-5:], "moves": moved}
    if out["days_observed"] >= 5:
        out["verdict"] = (f"CURRENCY PASSES — {movers}/{len(by)} ETFs show real day-over-day "
                          f"share movement" if movers >= 2 else
                          "CURRENCY FAILS — share counts are not moving at a usable resolution; "
                          "do NOT wire a vote on this field")
    return out


if __name__ == "__main__":
    import json
    print("=== etf_flow self-test (record-only; no scoring) ===\n")
    print(json.dumps(snapshot(), indent=1))
    print("\n--- currency evidence so far ---")
    print(json.dumps(currency_report(), indent=1))
