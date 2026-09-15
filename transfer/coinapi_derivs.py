"""
coinapi_derivs.py — crypto DERIVATIVES POSITIONING accumulation (CoinAPI, §16-onboarded
2026-08-10, Chairman-ordered build). HELD-OUT, RECORD-ONLY: writes its own table,
feeds NO score, NO ledger, NO served value. The purpose is BASELINE ACCUMULATION so
a future board + backtest can judge wiring it into the crypto money leg on data.

WHY (the founder's money-movement order, integrity-compliant): trading volume is
NEVER flow (C5/C6, board-unanimous) — and (K7 correction, board 2026-09-14,
`BOARD_divergence_2026-09-14.md`) neither is this: what these two series measure is
**LEVERAGE POSITIONING**, never money movement —
  • FUNDING RATE = the price of leverage (positive → longs pay shorts → long pressure);
    price-DERIVED (perp−spot basis), so it is permanently disqualified as a
    mania-independent leg and may serve only as a conditioner/null (sealed prereg
    `DIVERGENCE_PREREG_2026-09-14.md` §2).
  • OPEN INTEREST = outstanding derivative contracts in BASE-COIN UNITS (perps are
    zero-sum: every long has a short — NO money enters a coin when OI rises). ΔOI in
    coin units is a QUANTITY the mania cannot move without positions actually changing;
    ΔOI in USD notional would be OI×price and is forbidden (circular with M).
Both live-verified via CoinAPI 2026-08-10 (BTC perp funding 0.00005584, OI 105,683.596
BTC) and available for ALL 12 roster coins via Binance USDT perpetuals — the first
positioning-class source with full-roster coverage (ETF flow covers 2–3 coins; insider
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

K12 3-OFFSET TIMING CAPTURE (board 2026-09-15 D3, 9/9 convergence — the sealed
prereg's only unstarted clock; `DIVERGENCE_PREREG_2026-09-14.md` §5: "3 fixed
intra-day offsets, ≥30 days, ≥1 coin — REQUIRED BEFORE GRADUATION; the collector's
`captured_at` stamp is its input"): `snapshot_derivs_offsets()` captures funding +
open interest for BTC and ETH ONLY at three FIXED UTC slots (00:10 / 08:10 / 16:10)
into the separate append-only `coinapi_derivs_offsets` table (PK coin+date+slot,
INSERT-or-ignore, same fail-closed posture). Pins the capture slot the Statistician's
17-hour intra-day jitter finding called for. ~12 extra pay-per-use requests/day —
cents; the full roster is NOT needed for the timing audit. COLLECTION-ONLY: feeds NO
score, NO serve path; the data's only consumer is the K12 timing audit in
`tools/divergence_research.py`. Flag `COINAPI_OFFSET_CAPTURE` (default ON, "1", so
the ≥30-day clock starts on deploy; set "0" to reverse). The PRIMARY daily capture
above is UNCHANGED (series continuity).
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
                units TEXT,                       -- K14: 'coin' — the independence claim, recorded per row
                suspect INTEGER DEFAULT 0,        -- K14: >10x OI step vs trailing median → unit/spec break
                PRIMARY KEY (coin, signal_date)
            )
        """)
        # K14 (board 2026-09-14): additive columns for pre-existing tables — the
        # accuracy_ledger boot-guard idiom (duplicate-column errors are the no-op path).
        for _ddl in ("ALTER TABLE coinapi_derivs ADD COLUMN units TEXT",
                     "ALTER TABLE coinapi_derivs ADD COLUMN suspect INTEGER DEFAULT 0"):
            try:
                c.execute(_ddl)
            except Exception:
                try:
                    c.rollback()
                except Exception:
                    pass
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
        # K8/MNAR fix (board 2026-09-14, Executioner order): coins already written
        # today are SKIPPED, so the all-roster catch-up gate below retries ONLY the
        # missing coins later in the day — 429-day gaps shrink instead of becoming
        # permanent holes clustered on exactly the volatile days the series is
        # supposed to read. Idempotent and cost-bounded: no re-fetch of done coins.
        done_today = set()
        try:
            for r in c.execute(f"SELECT coin FROM coinapi_derivs WHERE signal_date = {ph}",
                               (today,)).fetchall():
                done_today.add(r["coin"] if hasattr(r, "keys") else r[0])
        except Exception:
            pass
        first = True
        for coin, sym in PERP_SYMBOLS.items():
            if coin in done_today:
                out["coins"][coin] = {"skipped": "already recorded today"}
                continue
            if not first:
                time.sleep(_PAUSE_S)               # batch pacing (§13)
            first = False
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
            # K14 unit guard: a >10x day-over-day OI step vs the trailing median is a
            # unit/contract-spec break, not a market move (a USD-notional flip is ~×60k
            # on BTC). The row is kept but marked suspect=1 — the series BREAKS visibly
            # instead of silently becoming price-multiplied.
            suspect = 0
            try:
                if oi is not None:
                    med_rows = c.execute(
                        f"SELECT open_interest FROM coinapi_derivs WHERE coin = {ph} "
                        f"AND open_interest IS NOT NULL ORDER BY signal_date DESC LIMIT 14",
                        (coin,)).fetchall()
                    vals = sorted(float(r["open_interest"] if hasattr(r, "keys") else r[0])
                                  for r in med_rows)
                    if vals:
                        med = vals[len(vals) // 2]
                        if med > 0 and (oi > 10 * med or oi < med / 10):
                            suspect = 1
                            print(f"[coinapi] {coin}: OI {oi} vs trailing median {med} — "
                                  f"marked SUSPECT (unit/spec break, K14)")
            except Exception:
                pass
            c.execute(
                f"INSERT INTO coinapi_derivs (coin, signal_date, symbol_id, "
                f"funding_rate, open_interest, source_time, signal_time, "
                f"captured_at, src, units, suspect) VALUES ({','.join([ph]*11)}) "
                f"ON CONFLICT (coin, signal_date) DO NOTHING",
                (coin, today, sym, fr, oi, src_t, sig_time, now_iso, "coinapi",
                 "coin", suspect))
            out["written"] += 1
            out["coins"][coin] = {"funding_rate": fr, "open_interest": oi,
                                  **({"suspect": True} if suspect else {})}
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
    """Daily catch-up gate. K8/MNAR fix (board 2026-09-14): the old ANY-coin check let
    one successful coin mask eleven 429'd ones, and those gaps clustered on volatile
    days (missing-not-at-random — the exact state the series exists to read). Now the
    day counts as done only when the FULL roster is recorded; snapshot_derivs skips
    already-written coins, so intra-day retries touch only the stragglers."""
    try:
        import date_utils
        today = date_utils.to_iso_date(datetime.now(timezone.utc).isoformat())
    except Exception:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    init_derivs_db(db_path)
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        row = c.execute(f"SELECT COUNT(DISTINCT coin) AS n FROM coinapi_derivs "
                        f"WHERE signal_date = {ph}", (today,)).fetchone()
        n = row["n"] if hasattr(row, "keys") else row[0]
        return int(n or 0) >= len(PERP_SYMBOLS)
    except Exception:
        return False
    finally:
        c.close()


# ---------------------------------------------------------------------------
# K12 3-offset timing capture (board 2026-09-15 D3) — see module docstring.
# ---------------------------------------------------------------------------

#: BTC/ETH only — prereg §5 requires ≥1 coin; two give a cross-check at ~cents/day.
OFFSET_COINS = ("BTC", "ETH")
#: slot label → scheduled minute-of-day, UTC. THREE FIXED intra-day offsets; :10
#: keeps the slot clear of exchange top-of-hour funding resets / API congestion.
OFFSET_SLOTS = {"t00": 0 * 60 + 10, "t08": 8 * 60 + 10, "t16": 16 * 60 + 10}


def init_offsets_db(db_path: str = DB_PATH):
    c = _connect(db_path)
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS coinapi_derivs_offsets (
                coin TEXT NOT NULL,
                signal_date TEXT NOT NULL,      -- canonical YYYY-MM-DD (§14), the slot's UTC day
                slot TEXT NOT NULL,             -- 't00' | 't08' | 't16' (INTENDED fixed offset)
                funding REAL,                   -- NULL = that metric absent (declared)
                open_interest REAL,
                source_time TEXT,               -- source's own entry_time HH:MM:SS (§14)
                signal_time TEXT,               -- our fetch HH:MM:SS (§14)
                captured_at TEXT,               -- full UTC instant — THE K12 audit measurement
                src TEXT,                       -- 'coinapi'
                units TEXT,                     -- K14: 'coin', recorded per row
                PRIMARY KEY (coin, signal_date, slot)
            )
        """)
        c.commit()
    finally:
        c.close()


def snapshot_derivs_offsets(db_path: str = DB_PATH) -> dict:
    """K12 3-offset intra-day capture (board 2026-09-15 D3; sealed prereg
    `DIVERGENCE_PREREG_2026-09-14.md` §5). COLLECTION-ONLY — feeds NO score, NO
    serve path; the data's only consumer is the K12 timing audit in
    `tools/divergence_research.py`. Flag `COINAPI_OFFSET_CAPTURE` (default ON "1"
    so the ≥30-day graduation clock starts on deploy; "0" reverses — Executioner).

    CATCH-UP semantics (matches the module's daily style): on each scheduler pass,
    every slot whose UTC time has passed today and whose (coin, date, slot) row is
    absent is captured NOW — `captured_at` records the TRUE capture instant, which
    is exactly what the audit measures (a late catch-up shows up as jitter, never
    as a fabricated on-time stamp). When several slots are pending for one coin
    (downtime catch-up), ONE fetch fills them all with the SAME captured_at — the
    duplication is visible to the audit by construction, and paying for identical
    re-reads seconds apart would add cost, not information.

    FAIL-CLOSED like the primary: both metrics unfetchable → NO row, logged.
    Append-only, forward-only (PK coin+date+slot, insert-or-ignore) — never
    rewritten. Idempotent: a pass with nothing pending does no fetch, no write.
    """
    out = {"date": None, "written": 0, "missing": [], "slots": {}}
    if os.getenv("COINAPI_OFFSET_CAPTURE", "1") != "1":
        out["disabled"] = True
        return out
    api_key = os.getenv("COINAPI_KEY", "")
    if os.getenv("COINAPI_DERIVS", "1") != "1" or not api_key:
        out["disabled"] = True
        return out
    now = datetime.now(timezone.utc)
    try:
        import date_utils
        today = date_utils.to_iso_date(now.isoformat())
    except Exception:
        today = now.strftime("%Y-%m-%d")
    out["date"] = today
    due = [s for s, m in OFFSET_SLOTS.items() if (now.hour * 60 + now.minute) >= m]
    if not due:
        return out
    init_offsets_db(db_path)
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    attempted = False
    try:
        have = set()
        try:
            for r in c.execute(
                    f"SELECT coin, slot FROM coinapi_derivs_offsets "
                    f"WHERE signal_date = {ph}", (today,)).fetchall():
                have.add((r["coin"], r["slot"]) if hasattr(r, "keys")
                         else (r[0], r[1]))
        except Exception:
            pass
        pending = [(coin, slot) for slot in due for coin in OFFSET_COINS
                   if (coin, slot) not in have]
        if not pending:
            return out
        attempted = True
        fetched = {}         # coin → (funding, oi, source_time, captured_at, sig_time)
        first = True
        for coin in OFFSET_COINS:
            if not any(p == coin for p, _ in pending):
                continue
            if not first:
                time.sleep(_PAUSE_S)               # batch pacing (§13)
            first = False
            fr, fr_t = _fetch_metric(api_key, PERP_SYMBOLS[coin],
                                     _METRICS["funding_rate"])
            time.sleep(_PAUSE_S)
            oi, oi_t = _fetch_metric(api_key, PERP_SYMBOLS[coin],
                                     _METRICS["open_interest"])
            if fr is None and oi is None:
                out["missing"].append(coin)        # declared absence, no row
                continue
            src_t = ""
            try:
                import date_utils
                src_t = date_utils.iso_time_of(fr_t or oi_t or "") or ""
            except Exception:
                pass
            cap = datetime.now(timezone.utc)       # per-coin TRUE capture instant
            fetched[coin] = (fr, oi, src_t,
                             cap.isoformat(timespec="seconds"),
                             cap.strftime("%H:%M:%S"))
        for coin, slot in pending:
            if coin not in fetched:
                continue
            fr, oi, src_t, cap_iso, sig_time = fetched[coin]
            c.execute(
                f"INSERT INTO coinapi_derivs_offsets (coin, signal_date, slot, "
                f"funding, open_interest, source_time, signal_time, captured_at, "
                f"src, units) VALUES ({','.join([ph]*10)}) "
                f"ON CONFLICT (coin, signal_date, slot) DO NOTHING",
                (coin, today, slot, fr, oi, src_t, sig_time, cap_iso,
                 "coinapi", "coin"))
            out["written"] += 1
            out["slots"].setdefault(slot, []).append(coin)
        c.commit()
    finally:
        c.close()
    if attempted:
        try:
            import collector_health as _ch
            _ch.log_collector_run("coinapi_derivs_offsets", out["written"],
                                  "success" if out["written"] else "failure",
                                  db_path=db_path,
                                  distinct_keys=len(fetched))
        except Exception:
            pass
        print(f"[coinapi] K12 offsets {today}: wrote {out['written']} rows "
              f"{out['slots']} (missing: {out['missing']})")
    return out


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
    # K12 3-offset capture status (board 2026-09-15 D3) — the ≥30-day graduation
    # clock is watched here. Fail-open: absence of the table reads as 0 coverage.
    offsets = {"enabled": os.getenv("COINAPI_OFFSET_CAPTURE", "1") == "1",
               "coins": []}
    try:
        init_offsets_db(db_path)
        c = _connect(db_path)
        try:
            rows = c.execute(
                "SELECT coin, COUNT(DISTINCT signal_date) AS days_covered, "
                "COUNT(*) AS slot_rows, MAX(captured_at) AS latest_capture "
                "FROM coinapi_derivs_offsets GROUP BY coin ORDER BY coin").fetchall()
            offsets["coins"] = [
                dict(r) if hasattr(r, "keys") else
                dict(zip(("coin", "days_covered", "slot_rows", "latest_capture"), r))
                for r in rows]
        finally:
            c.close()
    except Exception as e:
        offsets["reason"] = str(e)[:120]
    return {"available": True, "held_out": True,
            "note": "Baseline accumulation only — feeds no score; wiring into the "
                    "crypto money leg requires backtest-before-ship + board + "
                    "Chairman flip.",
            "coins": out_rows,
            "k12_offsets": offsets}
