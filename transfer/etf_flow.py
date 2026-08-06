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
from datetime import datetime, timedelta, timezone
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
        # SPEC AMENDMENT A1 (Chairman-ruled 2026-08-05 PT): every pull is RECORDED as an
        # observation (4h cadence → up to 6/day), so the day's NAV strike is captured
        # within hours of the provider posting it instead of up to 24h late. HONESTY
        # BOUNDARY, stated so it can never be narrated otherwise: NAV strikes ONCE per
        # trading day — six observations are six looks at at most ONE genuine flow
        # point, never six flow points. Intraday AUM wiggle is the coin's own price
        # moving (the banned circularity), which is exactly why the daily row updates
        # ONLY when the NAV itself changes (a real strike), never on AUM alone.
        c.execute("""
            CREATE TABLE IF NOT EXISTS etf_share_observations (
                ticker TEXT NOT NULL,
                captured_at TEXT NOT NULL,        -- full instant, UTC (§14 operational)
                shares REAL, aum REAL, nav REAL,
                PRIMARY KEY (ticker, captured_at)
            )
        """)
        try:
            c.execute("CREATE INDEX IF NOT EXISTS idx_etf_obs_t "
                      "ON etf_share_observations(captured_at)")
        except Exception:
            pass
        # A2.3 (Chairman 2026-08-05): SOURCE PROVENANCE — every row names the source
        # that produced it ('fmp' | an issuer-page adapter id). Δshares is NEVER
        # computed across a src seam (a provider cutover's step offset would read as
        # flow under the 20%/day guard — the splice rule). Additive, NULL≡'fmp'.
        for tbl in ("etf_share_snapshots", "etf_share_observations"):
            try:
                c.execute(f"ALTER TABLE {tbl} ADD COLUMN src TEXT")
                c.commit()
            except Exception:
                try:
                    c.rollback()
                except Exception:
                    pass
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

    out = {"date": today, "written": 0, "strikes_updated": 0, "missing": [], "tickers": {}}
    init_etf_db(db_path)
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
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
                # Every pull is an observation (A1: 4h cadence, 6 looks/day).
                c.execute(
                    f"INSERT INTO etf_share_observations (ticker,captured_at,shares,aum,nav,src) "
                    f"VALUES ({ph},{ph},{ph},{ph},{ph},{ph}) ON CONFLICT DO NOTHING",
                    (t, now_iso, info["shares"], info["aum"], info["nav"], "fmp"))
                # Daily row: insert on first sight; UPDATE only when the NAV itself moved
                # (a genuine later strike) — never on AUM alone (that is price noise).
                row = c.execute(
                    f"SELECT nav FROM etf_share_snapshots WHERE ticker={ph} "
                    f"AND snapshot_date={ph}", (t, today)).fetchone()
                if row is None:
                    c.execute(
                        f"INSERT INTO etf_share_snapshots "
                        f"(ticker,snapshot_date,shares,aum,nav,captured_at,src) "
                        f"VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph}) "
                        f"ON CONFLICT (ticker,snapshot_date) DO NOTHING",
                        (t, today, info["shares"], info["aum"], info["nav"], now_iso,
                         "fmp"))
                    out["written"] += 1
                else:
                    old_nav = (row["nav"] if hasattr(row, "keys") else row[0]) or 0.0
                    new_nav = info.get("nav") or 0.0
                    if old_nav and new_nav and abs(new_nav - old_nav) / old_nav > 1e-9:
                        c.execute(
                            f"UPDATE etf_share_snapshots SET shares={ph}, aum={ph}, "
                            f"nav={ph}, captured_at={ph}, src={ph} WHERE ticker={ph} "
                            f"AND snapshot_date={ph}",
                            (info["shares"], info["aum"], new_nav, now_iso, "fmp",
                             t, today))
                        out["strikes_updated"] += 1
                out["tickers"][t] = round(info["shares"])
            except Exception as e:
                print(f"[etf-flow] {t} write: {e}")
        c.commit()
    finally:
        c.close()
    return out


def intraday_report(db_path: str = DB_PATH, hours: float = 24.0) -> dict:
    """A1 (Chairman 2026-08-05): the 24h observation cycle — per fund, how many looks we
    took, whether the day's NAV strike has landed yet, and when. READ-ONLY. This is a
    TIMELINESS report; the flow measurement itself stays one genuine point per trading
    day (latest_delta), detected within ~4h instead of up to 24."""
    from datetime import timedelta
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat(timespec="seconds")
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        rows = [dict(r) if hasattr(r, "keys") else
                {"ticker": r[0], "captured_at": r[1], "nav": r[2]}
                for r in c.execute(
                    f"SELECT ticker, captured_at, nav FROM etf_share_observations "
                    f"WHERE captured_at >= {ph} ORDER BY ticker, captured_at",
                    (since,)).fetchall()]
    except Exception as e:
        return {"available": False, "reason": str(e)[:120]}
    finally:
        c.close()
    by = {}
    for r in rows:
        by.setdefault(r["ticker"], []).append(r)
    out = {"available": True, "window_hours": hours, "tickers": {}}
    for t, rs in by.items():
        navs = [r["nav"] for r in rs if r.get("nav")]
        distinct = len({round(n, 6) for n in navs})
        strike_at = None
        for a, b in zip(rs, rs[1:]):
            if a.get("nav") and b.get("nav") and \
                    abs(b["nav"] - a["nav"]) / a["nav"] > 1e-9:
                strike_at = b["captured_at"]
        out["tickers"][t] = {"observations": len(rs), "distinct_navs": distinct,
                             "strike_detected_at": strike_at,
                             "note": ("strike captured this window" if strike_at else
                                      "no NAV change observed this window")}
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

def _trading_days_between(d_old, d_new) -> int:
    """Weekday count in (d_old, d_new] — Mon–Fri, US holidays deliberately not excluded
    (same declared basis as the flow-ledger window; no market-calendar dependency)."""
    days, d = 0, d_old
    while d < d_new:
        d += timedelta(days=1)
        if d.weekday() < 5:
            days += 1
    return days


def latest_delta(ticker: str, db_path: str = DB_PATH) -> dict:
    """Share-count change for one ETF — the raw material of a flow vote.

    F2 FIX (Board 2026-08-05, the Challenger; Chairman-ordered): the daily row is
    inserted at FIRST SIGHT after UTC midnight carrying the PRIOR day's strike values,
    so a naive newest-two-dates compare read delta = 0.0 for the ~13–21h before the
    day's NAV strike landed — and all weekend — fabricating "measured quiet" votes and
    shadowing the genuine flow point. The compare now runs over VALUE-DISTINCT days:
    consecutive rows with identical (shares, nav) are one observation (the same strike
    seen again), so the genuine latest flow point keeps serving until a NEW strike
    actually lands. A real strike that repeats values exactly is a known, disclosed
    artifact class for the reconciliation harness (Guardian note), not handled here.

    F4 FIX (same ruling): the delta is normalized by TRADING days in the gap, not
    calendar days — Monday's one-session flow was being read at 1/3 strength.

    Rules retained (Board 2026-08-01): trading-gap > 5 = STALE, no vote; |delta| >
    20%/day = DISCONTINUITY, no vote. Shares-based numbers ONLY; `aum_latest` rides
    along for the ELIGIBILITY floor, never for the signal (the circularity rule).
    """
    c = _connect(db_path)
    try:
        try:
            rows = [dict(r) for r in c.execute(
                "SELECT snapshot_date, shares, aum, nav, src FROM etf_share_snapshots "
                "WHERE ticker = ? ORDER BY snapshot_date DESC LIMIT 12",
                (ticker.upper(),)).fetchall()]
        except Exception:                            # pre-src schema
            rows = [dict(r) for r in c.execute(
                "SELECT snapshot_date, shares, aum, nav FROM etf_share_snapshots "
                "WHERE ticker = ? ORDER BY snapshot_date DESC LIMIT 12",
                (ticker.upper(),)).fetchall()]
    except Exception as e:
        return {"available": False, "reason": str(e)[:100]}
    finally:
        c.close()
    seen, by_date = set(), []
    for r in rows:
        if r["snapshot_date"] not in seen and r.get("shares"):
            seen.add(r["snapshot_date"])
            by_date.append(r)
    # Collapse value-identical consecutive days: one strike = one observation.
    distinct = []
    for r in by_date:                        # newest → oldest
        if distinct:
            prev = distinct[-1]
            same = (abs((prev["shares"] or 0) - (r["shares"] or 0)) < 1e-9 and
                    abs((prev.get("nav") or 0) - (r.get("nav") or 0)) < 1e-9)
            if same:
                # keep the OLDER date for the strike (it happened then; the newer row
                # is the pre-strike copy) — replace so from/to dates stay truthful.
                distinct[-1] = r
                continue
        distinct.append(r)
    if len(distinct) < 2:
        return {"available": False, "reason": "fewer than 2 value-distinct snapshot days"}
    b, a = distinct[0], distinct[1]          # newest strike, previous strike
    # A2.3 SPLICE RULE (Chairman 2026-08-05): never compute a delta across a source
    # seam — a provider cutover's level restatement would read as flow (and at ~1-2%
    # would sail UNDER the 20%/day discontinuity guard). NULL src ≡ 'fmp' (pre-A2 rows).
    if (b.get("src") or "fmp") != (a.get("src") or "fmp"):
        return {"available": False, "splice": True,
                "reason": f"source seam: {a.get('src') or 'fmp'} → "
                          f"{b.get('src') or 'fmp'} — no delta across src boundary; "
                          "the new source re-earns its own history"}
    try:
        d_new = datetime.strptime(b["snapshot_date"], "%Y-%m-%d")
        d_old = datetime.strptime(a["snapshot_date"], "%Y-%m-%d")
        gap = max(1, _trading_days_between(d_old, d_new))
    except Exception:
        gap = 1
    if gap > 5:
        return {"available": False, "reason": f"stale: {gap} trading-day gap between "
                "strikes", "stale": True, "gap_days": gap}
    pct_per_day = round(100.0 * (b["shares"] - a["shares"]) / a["shares"] / gap, 4)
    if abs(pct_per_day) > 20.0:
        return {"available": False, "reason": f"discontinuity: {pct_per_day}%/day "
                "(split/closure-scale step, not flow)", "discontinuity": True,
                "delta_pct_per_day": pct_per_day, "gap_days": gap}
    return {"available": True, "delta_pct_per_day": pct_per_day, "gap_days": gap,
            "gap_basis": "trading_days", "from_date": a["snapshot_date"],
            "to_date": b["snapshot_date"], "shares_from": a["shares"],
            "shares_to": b["shares"], "aum_latest": b.get("aum")}
