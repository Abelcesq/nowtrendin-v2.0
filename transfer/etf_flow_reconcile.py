"""
etf_flow_reconcile.py — the RECONCILIATION HARNESS (spec §8 gate 4 / amendment A1.5+F7).
HELD-OUT VERIFIER: feeds no score, no ledger verdict — it checks OUR derived share-flow
against the ISSUERS' published daily flows, continuously, with the pass band and the
materiality floor PRE-DECLARED before the first comparison ever ran (Bernstein rule):

  • MATERIALITY FLOOR (F7, fixed 2026-08-05 at n=0): a fund-day is direction-tested only
    when |published net flow| > max($10M, 0.05% of the fund's AUM).
  • BAND: on material days the DIRECTION must match; magnitude within ±25% or ±$20M,
    whichever is more forgiving. A persistent one-direction bias FAILS even inside the
    band (≥5 consecutive material comparisons with the same error sign).
  • The disclosed ±1-day UTC smear means day-boundary slippage is an expected artifact
    class; so is a strike whose values repeat exactly (Guardian note, A1.6-F2).

COMPARATOR: Farside Investors' daily aggregation of the issuers' own published flows
(farside.co.uk — free, fetched with our DECLARED UA, verified accessible 2026-08-05).
§16 role: held-out REFEREE, never a data source feeding any score — the no-aggregators
rule (§15) governs scoring inputs, not verifiers. Coverage: BTC / ETH / SOL pages exist;
XRP has NO published comparator page → its funds carry the honest "no_comparator" state,
never a fabricated pass (Expansionist condition: adapter-per-source registry, so a new
issuer/venue page is one entry, not a rewrite).

Derived side: Δshares between consecutive VALUE-DISTINCT strikes × the newer strike's
NAV. These display-dollars live ONLY in the reconcile log, which nothing in scoring or
the ledgers reads (Guardian condition).
"""
from __future__ import annotations

import os
import re
from datetime import date, datetime, timedelta, timezone
from urllib.request import Request, urlopen

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
_UA = os.getenv("RECONCILE_UA", "NowTrendIn/2.0 (data verification)")

# F7 — pre-declared, fixed at zero comparisons. Changing after data exists = new spec id.
FLOOR_ABS_USD = float(os.getenv("RECONCILE_FLOOR_ABS_USD", str(10e6)))
FLOOR_AUM_FRAC = float(os.getenv("RECONCILE_FLOOR_AUM_FRAC", "0.0005"))
BAND_REL = float(os.getenv("RECONCILE_BAND_REL", "0.25"))
BAND_ABS_USD = float(os.getenv("RECONCILE_BAND_ABS_USD", str(20e6)))
BIAS_RUN = int(os.getenv("RECONCILE_BIAS_RUN", "5"))

#: Adapter registry — source → coin → URL. A new comparator (a non-US venue, a direct
#: issuer page) is ONE entry + optionally its own parser. XRP deliberately absent
#: (verified 404, 2026-08-05): honest no-comparator, never implied coverage.
_SOURCES = {
    "farside": {
        "BTC": "https://farside.co.uk/btc/",
        "ETH": "https://farside.co.uk/eth/",
        "SOL": "https://farside.co.uk/sol/",
    },
}


def _connect(db_path: str = DB_PATH):
    conn = db_compat.connect(db_path)
    if not db_compat.USE_PG:
        try:
            import sqlite3
            conn.row_factory = sqlite3.Row
        except Exception:
            pass
    return conn


def init_reconcile_db(db_path: str = DB_PATH):
    c = _connect(db_path)
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS etf_reconcile_log (
                snapshot_date TEXT NOT NULL,          -- canonical YYYY-MM-DD (§14)
                ticker TEXT NOT NULL,
                derived_usd REAL, published_usd REAL,
                material INTEGER, direction_match INTEGER, within_band INTEGER,
                verdict TEXT, source TEXT, checked_at TEXT,
                PRIMARY KEY (snapshot_date, ticker)
            )
        """)
        c.commit()
    finally:
        c.close()


def _iso(d: str):
    """'04 Aug 2026' → '2026-08-04', through §14 canonicalization first."""
    try:
        from date_utils import to_iso_date
        v = to_iso_date(d)
        if v:
            return v
    except Exception:
        pass
    try:
        return datetime.strptime(d.strip(), "%d %b %Y").strftime("%Y-%m-%d")
    except Exception:
        return None


def _num(cell: str):
    """Farside cell → signed dollars. '(14.7)' = -$14.7M; '-' = not yet published (None);
    '0.0' = a MEASURED zero flow day (stays 0.0 — information, not absence)."""
    s = (cell or "").replace(",", "").replace("&nbsp;", "").strip()
    if s in ("", "-", "–"):
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        v = float(s) * 1e6
    except ValueError:
        return None
    return -v if neg else v


def fetch_published(coin: str, source: str = "farside") -> dict:
    """{iso_date: {TICKER: usd}} from the comparator's daily table. Honest states:
    no page for the coin → available False / reason no_comparator."""
    url = (_SOURCES.get(source) or {}).get(coin.upper())
    if not url:
        return {"available": False, "reason": "no_comparator",
                "note": f"no published-flow comparator registered for {coin} "
                        f"(XRP verified absent 2026-08-05) — never implied covered"}
    try:
        req = Request(url, headers={"User-Agent": _UA})
        with urlopen(req, timeout=25) as r:
            html = r.read().decode("utf-8", "ignore")
    except Exception as e:
        return {"available": False, "reason": f"fetch failed: {str(e)[:80]}"}

    tables = re.findall(r"<table[^>]*>(.*?)</table>", html, re.S)
    for t in tables:
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S)
        header, by_date = None, {}
        for r in rows:
            cells = [re.sub(r"<[^>]+>", "", x).replace("&nbsp;", " ").strip()
                     for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
            if not cells:
                continue
            if header is None:
                # the ticker header row names ≥2 known fund tickers
                if sum(1 for c in cells if re.fullmatch(r"[A-Z]{3,5}", c)) >= 2:
                    header = cells
                continue
            d = _iso(cells[0])
            if not d:
                continue                      # Fee/Total/Average/Min/Max rows
            vals = {}
            for i, cell in enumerate(cells[1:], start=1):
                if i < len(header) and re.fullmatch(r"[A-Z]{3,5}", header[i] or ""):
                    v = _num(cell)
                    if v is not None:
                        vals[header[i]] = v
            if vals:
                by_date[d] = vals
        if by_date:
            return {"available": True, "source": source, "url": url,
                    "by_date": by_date, "days": len(by_date)}
    return {"available": False, "reason": "table shape not recognized — comparator "
                                          "format changed; harness fails CLOSED"}


def _derived_by_date(ticker: str, db_path: str = DB_PATH) -> dict:
    """{strike_date: {'usd': Δshares × NAV, 'aum': ...}} over VALUE-DISTINCT strikes
    (same dedupe rule as latest_delta — one strike, one observation)."""
    c = _connect(db_path)
    try:
        rows = [dict(r) for r in c.execute(
            "SELECT snapshot_date, shares, aum, nav FROM etf_share_snapshots "
            "WHERE ticker = ? ORDER BY snapshot_date ASC", (ticker.upper(),)).fetchall()]
    except Exception:
        rows = []
    finally:
        c.close()
    distinct = []
    for r in rows:
        if not r.get("shares"):
            continue
        if distinct:
            p = distinct[-1]
            if (abs((p["shares"] or 0) - (r["shares"] or 0)) < 1e-9 and
                    abs((p.get("nav") or 0) - (r.get("nav") or 0)) < 1e-9):
                continue                      # pre-strike copy of the same strike
        distinct.append(r)
    out = {}
    for a, b in zip(distinct, distinct[1:]):
        try:
            out[b["snapshot_date"]] = {
                "usd": (b["shares"] - a["shares"]) * (b.get("nav") or 0.0),
                "aum": b.get("aum") or 0.0}
        except Exception:
            continue
    return out


def reconcile(db_path: str = DB_PATH, coins=None, source: str = "farside") -> dict:
    """One harness pass: compare every derived strike-day against the published table,
    upsert verdicts into etf_reconcile_log. Idempotent; runs daily."""
    import crypto_signals as cs
    init_reconcile_db(db_path)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = {"checked": 0, "pass": 0, "fail": 0, "immaterial": 0,
               "no_published": 0, "no_comparator_coins": [], "at": now}
    conn = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        for coin, cfg in cs.COIN_UNIVERSE.items():
            if coins and coin not in coins:
                continue
            etfs = [p["ticker"] for p in cfg.get("proxies", []) if p.get("kind") == "etf"]
            if not etfs:
                continue
            pub = fetch_published(coin, source)
            if not pub.get("available"):
                if pub.get("reason") == "no_comparator":
                    summary["no_comparator_coins"].append(coin)
                else:
                    summary.setdefault("fetch_errors", []).append(
                        {"coin": coin, "reason": pub.get("reason")})
                continue
            for tkr in etfs:
                derived = _derived_by_date(tkr, db_path)
                for d, dv in derived.items():
                    pv = (pub["by_date"].get(d) or {}).get(tkr)
                    if pv is None:
                        verdict, material, dirm, band = "NO_PUBLISHED", None, None, None
                        summary["no_published"] += 1
                    else:
                        floor = max(FLOOR_ABS_USD, FLOOR_AUM_FRAC * (dv["aum"] or 0.0))
                        material = abs(pv) > floor
                        if not material:
                            verdict, dirm, band = "IMMATERIAL", None, None
                            summary["immaterial"] += 1
                        else:
                            dirm = (dv["usd"] > 0) == (pv > 0)
                            band = abs(dv["usd"] - pv) <= max(BAND_REL * abs(pv),
                                                              BAND_ABS_USD)
                            verdict = "PASS" if (dirm and band) else "FAIL"
                            summary["pass" if verdict == "PASS" else "fail"] += 1
                    conn.execute(
                        f"INSERT INTO etf_reconcile_log (snapshot_date,ticker,"
                        f"derived_usd,published_usd,material,direction_match,"
                        f"within_band,verdict,source,checked_at) "
                        f"VALUES ({','.join([ph]*10)}) "
                        f"ON CONFLICT (snapshot_date,ticker) DO UPDATE SET "
                        f"derived_usd=EXCLUDED.derived_usd, "
                        f"published_usd=EXCLUDED.published_usd, "
                        f"material=EXCLUDED.material, "
                        f"direction_match=EXCLUDED.direction_match, "
                        f"within_band=EXCLUDED.within_band, "
                        f"verdict=EXCLUDED.verdict, source=EXCLUDED.source, "
                        f"checked_at=EXCLUDED.checked_at",
                        (d, tkr, round(dv["usd"], 2), pv,
                         None if material is None else int(material),
                         None if dirm is None else int(bool(dirm)),
                         None if band is None else int(bool(band)),
                         verdict, source, now))
                    summary["checked"] += 1
        conn.commit()
    finally:
        conn.close()
    return summary


def report(db_path: str = DB_PATH, days: int = 21) -> dict:
    """The gate-4 evidence: per-fund verdicts, open failures, persistent-bias check,
    and the honest coverage statement. Read by /diag/etf-reconcile + the monitor."""
    init_reconcile_db(db_path)
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        rows = [dict(r) for r in c.execute(
            f"SELECT * FROM etf_reconcile_log WHERE snapshot_date >= {ph} "
            f"ORDER BY ticker, snapshot_date", (since,)).fetchall()]
    except Exception as e:
        return {"available": False, "reason": str(e)[:120]}
    finally:
        c.close()
    if not rows:
        return {"available": False, "reason": "harness has not run yet",
                "gate_status": "NOT_RUN"}
    by, fails = {}, []
    for r in rows:
        t = by.setdefault(r["ticker"], {"pass": 0, "fail": 0, "immaterial": 0,
                                        "no_published": 0, "errors": []})
        v = r.get("verdict")
        if v == "PASS":
            t["pass"] += 1
        elif v == "FAIL":
            t["fail"] += 1
            fails.append({k: r[k] for k in ("snapshot_date", "ticker", "derived_usd",
                                            "published_usd")})
        elif v == "IMMATERIAL":
            t["immaterial"] += 1
        elif v == "NO_PUBLISHED":
            t["no_published"] += 1
        if r.get("material") and r.get("published_usd") is not None:
            t["errors"].append(1 if (r["derived_usd"] or 0) > r["published_usd"] else -1)
    bias = []
    for t, d in by.items():
        errs = d.pop("errors")
        # Longest run of same-sign (derived − published) errors across material days.
        run, prev, worst = 0, 0, 0
        for e in errs:
            run = run + 1 if e == prev else 1
            prev = e
            worst = max(worst, run)
        if worst >= BIAS_RUN:
            bias.append({"ticker": t, "consecutive_same_sign_error": worst,
                         "note": "persistent one-direction bias FAILS even inside the "
                                 "band (F7)"})
    material_total = sum(d["pass"] + d["fail"] for d in by.values())
    gate = ("FAIL" if fails or bias else
            "PASS" if material_total >= 1 else "NO_MATERIAL_DAYS_YET")
    return {
        "available": True, "window_days": days, "funds": by,
        "material_comparisons": material_total,
        "open_failures": fails or None, "bias_flags": bias or None,
        "no_comparator": ["XRP fund (TOXR) — no published-flow page exists; honest "
                          "absence, never implied covered. (XRPC removed from the "
                          "roster 2026-08-11, Chairman order — frozen issuer page)"],
        "band": {"floor": "max($10M, 0.05% AUM)", "direction": "mandatory on material "
                 "days", "magnitude": "±25% or ±$20M (more forgiving)",
                 "bias_rule": f"≥{BIAS_RUN} consecutive same-sign errors fail"},
        "gate_status": gate,
        "note": "Held-out verifier (spec §8 gate 4 / A1.5): derived Δshares×NAV vs the "
                "issuers' published daily flows. Nothing here feeds any score or ledger "
                "verdict.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# AMENDMENT A2 (Chairman-ruled 2026-08-05 PT; spec CRYPTO_FLOW_SPEC_A2_AMENDMENT_
# 2026-08-05.md, pre-declared at commit 51adb9d BEFORE any A2-scored pass).
# The A1.5 exact-calendar-date join above is FROZEN with its first-pass log
# (archived: audits/board/ETF_RECONCILE_FIRSTPASS_LOG_2026-08-05.json) — old
# verdicts are kept, never rewritten. A2 verdicts live in etf_reconcile_log2,
# each stamped rule_version + verdict_at (the date+time of the revised verdict).
#
# A2 join, derived from MECHANISM (never fitted per-row):
#   T(strike) = settled-through trade date: captured_at → US/Eastern; ET time
#   before 06:00 belongs to the prior ET date; weekends roll back to the last
#   trading day; T = the previous trading day of that effective date. Each pair
#   of consecutive VALUE-DISTINCT strikes a→b covers published trade dates in
#   (T(a), T(b)] and is compared CUMULATIVELY against their sum (lag-invariant;
#   drains the weekend NO_PUBLISHED leak). F7 floor/band UNTOUCHED.
# Honest states: PENDING_FINAL (still-moving edge, not scored) · EMPTY_INTERVAL
#   (material derived flow over zero covered trade days — phantom flow, fails) ·
#   NO_DERIVED (material published day with no derived coverage after a
#   2-trading-day grace — a frozen source reads as FAILURE, never silence).
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# AMENDMENT A2.2 (Chairman-approved 2026-08-18; root-cause trace
# audits/board/A2_SIGNFLIP_TRACE_2026-08-18.md; sub-versioned per annex N1.2).
# The A2.1 capture-instant t_of mislabeled issuer-source intervals by ±1 trading
# day: iShares counts are SETTLED-basis (as-of D = traded through D−1) with page
# rollover latency that varies by fund AND by day (IBIT posted as-of-D at T+1
# ~16:30 ET on 08-11..15 but T+0 ~22:49 ET on 08-17); 21Shares counts are
# TRADE-basis (as-of D includes D's own trades). Every 08-10..08-13 sign-flip
# FAIL was a CORRECT dollar value compared against the neighboring day's
# published flow. A2.2 keys T on the page's OWN as-of stamp (persisted as
# page_asof, §14-canonical) with a per-family mechanism-declared basis
# (ASOF_BASIS below). FORWARD-ONLY RE-VERDICT: rule_version bumps to 'A2.2';
# A2 rows are never rewritten or deleted; report_a2 + the A2.4 re-arm read
# RULE_VERSION rows exclusively, so the re-arm clocks restart at zero on deploy
# (pass_comparisons AND open_bad both reset; ≥5 material in-band issuer
# comparisons re-earned from scratch on correctly-labeled rows). Issuer strikes
# WITHOUT a stamp (pre-A2.2 rows, or a stamp that stops parsing) are NEVER
# guessed (§14): their intervals are not scored under A2.2 — their verdicts
# stand on the preserved A2 record — but their days still count as COVERED so
# the NO_DERIVED sweep cannot retro-blame a source for days it watched (the
# 953c31c era-attribution defect class); each skip is counted in the summary
# (asof_unlabelable), never silent.
# ═══════════════════════════════════════════════════════════════════════════════

RULE_VERSION = "A2.2"
NO_DERIVED_GRACE_TDAYS = int(os.getenv("RECONCILE_NO_DERIVED_GRACE", "2"))

#: A2.2 — per-family share-count BASIS for the issuer page's as-of stamp. A basis
#: is a DECLARED MECHANISM FACT verified from stamp+value pairs against the
#: issuers' own published flows (trace §3-§4), never fitted per-row:
#:   'settled' — count as-of D holds shares SETTLED through D = traded through the
#:               PREVIOUS trading day (T+1 creation settlement). iShares: Δ(as-of
#:               D − as-of D−1) reproduced the published flow of D−1 exactly on
#:               four consecutive IBIT rows (−53.6 / +50.2 / −14.3 / −55.5 $M).
#:   'trade'   — count as-of D already includes D's own creations. 21Shares:
#:               Δ(as-of D − as-of D−1) reproduced the published flow of D exactly
#:               (ARKB −11.5 / −58.8 $M).
#:   (absent)  — basis not yet verified from stamps (Bitwise: empirically aligned
#:               under the capture-instant mapping) → legacy t_of(captured_at)
#:               fallback until a §16 stamp+value re-test promotes it.
ASOF_BASIS = {
    "issuer_ishares": "settled",
    "issuer_ishares_r1": "settled",     # ETHA post-split epoch — same page mechanics
    "issuer_21shares": "trade",
}

try:
    from zoneinfo import ZoneInfo
    _ET = ZoneInfo("America/New_York")
except Exception:                                   # tzdata-less fallback (dev boxes)
    # Month-band DST approximation (board fix 2026-08-18): the old fixed −4 was
    # wrong half the year (EST is −5) — a dev box reproducing verdicts in
    # January would mislabel evening captures. Approximate, dev-only; dynos
    # always take the zoneinfo path.
    _ET = None

def _to_et(dt):
    if _ET is not None:
        return dt.astimezone(_ET)
    off = -4 if 3 <= dt.astimezone(timezone.utc).month <= 10 else -5
    return dt.astimezone(timezone(timedelta(hours=off)))


#: NYSE full-closure holidays, FROZEN LIST 2026–2027 (board P1 fix 2026-08-18 —
#: Labor Day 2026-09-07 lands inside the A2.4 re-arm accrual window; a trading-
#: day model that counts it would label T on a closed session and poison the
#: interval join with a NO_PUBLISHED day). Weekend-observed shifts applied
#: (2026-07-03 for Jul-4-Sat; 2027-06-18, 2027-07-05, 2027-12-24). Dates beyond
#: 2027 fall back to the weekends-only model until the list is extended —
#: extend it BEFORE 2028-01-01 (declared, visible: _holiday_coverage_note).
_US_MARKET_HOLIDAYS = {
    # 2026
    date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16), date(2026, 4, 3),
    date(2026, 5, 25), date(2026, 6, 19), date(2026, 7, 3), date(2026, 9, 7),
    date(2026, 11, 26), date(2026, 12, 25),
    # 2027
    date(2027, 1, 1), date(2027, 1, 18), date(2027, 2, 15), date(2027, 3, 26),
    date(2027, 5, 31), date(2027, 6, 18), date(2027, 7, 5), date(2027, 9, 6),
    date(2027, 11, 25), date(2027, 12, 24),
}
_HOLIDAY_YEARS = (2026, 2027)


def _last_bday(d):
    while d.weekday() >= 5 or d in _US_MARKET_HOLIDAYS:
        d -= timedelta(days=1)
    return d


def _prev_bday(d):
    return _last_bday(d - timedelta(days=1))


def _tdays_range(d_from_excl, d_to_incl):
    """Trading days in (d_from_excl, d_to_incl] — Mon–Fri excluding NYSE
    holidays (frozen 2026–2027 list; board P1 fix 2026-08-18 — was
    holidays-not-excluded, which would have gone live wrong on Labor Day)."""
    out, d = [], d_from_excl
    while d < d_to_incl:
        d += timedelta(days=1)
        if d.weekday() < 5 and d not in _US_MARKET_HOLIDAYS:
            out.append(d)
    return out


def t_of(captured_at: str):
    """A2.1: the settled-through TRADE date a share-count capture reflects.
    A2.2 note: retained as the FALLBACK mapping (FMP rows; families without a
    verified ASOF_BASIS). For basis-verified issuer families the strike label
    comes from t_of_strike (the page's own as-of stamp), because this
    capture-instant model mislabels those intervals ±1 trading day (trace §4)."""
    try:
        dt = datetime.fromisoformat(str(captured_at).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        et = _to_et(dt)
        eff = et.date()
        if et.hour < 6:                             # pre-dawn ET = prior evening's book
            eff -= timedelta(days=1)
        return _prev_bday(_last_bday(eff))
    except Exception:
        return None


def t_of_strike(row: dict):
    """A2.2 label for ONE strike row → (T, mode).

    mode 'asof'         — src family has a verified basis and the row carries a
                          parseable page_asof: T is derived from the stamp
                          (settled: previous trading day of as-of; trade: the
                          as-of trading day itself). Weekend-stamped as-ofs roll
                          back to the last session first.
    mode 'capture'      — no verified basis for this src (FMP, Bitwise): legacy
                          capture-instant t_of.
    mode 'missing_asof' — basis-verified family but NO parseable stamp on the row
                          (pre-A2.2 capture, or stamp format drift): T is None —
                          an honest label cannot be produced and is never guessed
                          (§14). Caller skips scoring but keeps coverage.
    Dates go through date_utils.to_iso_date (§14) — no raw slicing."""
    src = (row.get("src") or "fmp")
    basis = ASOF_BASIS.get(src)
    if basis is None:
        return t_of(row.get("captured_at")), "capture"
    asof = row.get("page_asof")
    iso = None
    if asof:
        try:
            from date_utils import to_iso_date
            iso = to_iso_date(str(asof))
        except Exception:
            iso = None
    if not iso:
        return None, "missing_asof"
    try:
        d = _last_bday(datetime.strptime(iso, "%Y-%m-%d").date())
    except Exception:
        return None, "missing_asof"
    return (_prev_bday(d) if basis == "settled" else d), "asof"


def init_reconcile_db2(db_path: str = DB_PATH):
    c = _connect(db_path)
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS etf_reconcile_log2 (
                interval_end_date TEXT NOT NULL,      -- canonical YYYY-MM-DD (§14)
                ticker TEXT NOT NULL,
                rule_version TEXT NOT NULL,
                interval_start_date TEXT,
                derived_usd REAL, published_usd REAL,
                material INTEGER, direction_match INTEGER, within_band INTEGER,
                verdict TEXT, src TEXT, comparator TEXT,
                verdict_at TEXT,                      -- Chairman ruling a: date+time stamp
                PRIMARY KEY (interval_end_date, ticker, rule_version)
            )
        """)
        # Board P1 fix (2026-08-18, Guardian/Executioner): within a rule_version
        # the daily upsert can revise a FINALIZED verdict when the comparator
        # restates a published number. "A divergence fires forever" must be true
        # by construction — every finalized-verdict change is LOGGED here,
        # append-only, and surfaced in report_a2. PENDING_FINAL → final is the
        # normal path and is not a transition.
        c.execute("""
            CREATE TABLE IF NOT EXISTS etf_verdict_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interval_end_date TEXT NOT NULL, ticker TEXT NOT NULL,
                rule_version TEXT NOT NULL,
                old_verdict TEXT, new_verdict TEXT,
                old_verdict_at TEXT, new_verdict_at TEXT,
                old_published_usd REAL, new_published_usd REAL
            )
        """)
        # Board P1 fix (2026-08-18, Economist/Challenger/Statistician): the
        # STANDING basis monitor. Sign-flip FAILs only discriminate when flows
        # alternate; the regime-independent detector of an ASOF_BASIS break is
        # the stamp+value identity itself — single-trading-day as-of intervals
        # must keep reproducing the issuer's published flow. Recomputed from
        # scratch each run (idempotent), per fund.
        c.execute("""
            CREATE TABLE IF NOT EXISTS etf_basis_check (
                ticker TEXT PRIMARY KEY, family TEXT,
                checked INTEGER, matched INTEGER, consec_mismatch INTEGER,
                last_interval_end TEXT, updated_at TEXT
            )
        """)
        c.commit()
    finally:
        c.close()


def _strikes_with_capture(ticker: str, db_path: str = DB_PATH):
    """Value-distinct strikes with captured_at + src (splice-aware: a src seam ends
    the comparable series — no Δ across it, per A2.3)."""
    c = _connect(db_path)
    try:
        try:
            rows = [dict(r) for r in c.execute(
                "SELECT snapshot_date, shares, aum, nav, captured_at, src, page_asof "
                "FROM etf_share_snapshots WHERE ticker = ? ORDER BY snapshot_date ASC",
                (ticker.upper(),)).fetchall()]
        except Exception:                            # pre-A2.2 schema (no page_asof)
            try:
                rows = [dict(r) for r in c.execute(
                    "SELECT snapshot_date, shares, aum, nav, captured_at, src "
                    "FROM etf_share_snapshots WHERE ticker = ? "
                    "ORDER BY snapshot_date ASC", (ticker.upper(),)).fetchall()]
            except Exception:                        # pre-src schema
                rows = [dict(r) for r in c.execute(
                    "SELECT snapshot_date, shares, aum, nav, captured_at "
                    "FROM etf_share_snapshots WHERE ticker = ? "
                    "ORDER BY snapshot_date ASC", (ticker.upper(),)).fetchall()]
    except Exception:
        rows = []
    finally:
        c.close()
    distinct = []
    for r in rows:
        if not r.get("shares") or not r.get("captured_at"):
            continue
        r.setdefault("src", None)
        r.setdefault("page_asof", None)
        if distinct:
            p = distinct[-1]
            # SRC-AWARE dedupe (board/Challenger, 2026-08-09): identical values
            # across a src seam are NOT the same strike seen again — swallowing
            # the seam strike would shift the new era's start later and blame
            # its uncovered days on the prior source (pro-readiness bias).
            if (abs((p["shares"] or 0) - (r["shares"] or 0)) < 1e-9 and
                    abs((p.get("nav") or 0) - (r.get("nav") or 0)) < 1e-9 and
                    (p.get("src") or "fmp") == (r.get("src") or "fmp")):
                continue
        distinct.append(r)
    return distinct


def reconcile_a2(db_path: str = DB_PATH, coins=None, source: str = "farside") -> dict:
    """One A2.2 harness pass: interval comparisons + the NO_DERIVED sweep, upserted
    into etf_reconcile_log2 under RULE_VERSION with a fresh verdict_at. Idempotent,
    daily. A2.2: interval labels come from t_of_strike (as-of-keyed for
    basis-verified issuer families); stamp-less issuer strikes are covered-not-
    scored (summary['asof_unlabelable'])."""
    import crypto_signals as cs
    init_reconcile_db2(db_path)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    today_t = _prev_bday(_last_bday(datetime.now(_ET).date()))
    summary = {"rule_version": RULE_VERSION, "checked": 0, "pass": 0, "fail": 0,
               "immaterial": 0, "pending_final": 0, "empty_interval": 0,
               "no_derived": 0, "no_published": 0, "asof_unlabelable": 0,
               "no_comparator_coins": [], "at": now}
    conn = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"

    basis_stats = {}   # ticker -> [(interval_end_date, matched_bool)] (asof 1-tday pairs)

    def _upsert(end_d, tkr, start_d, dusd, pusd, material, dirm, band, verdict, src):
        # Finalized-verdict transition guard (board P1, 2026-08-18): a comparator
        # restatement must never silently flip a stored FAIL — log the transition.
        try:
            old = conn.execute(
                f"SELECT verdict, verdict_at, published_usd FROM etf_reconcile_log2 "
                f"WHERE interval_end_date = {ph} AND ticker = {ph} "
                f"AND rule_version = {ph}", (end_d, tkr, RULE_VERSION)).fetchone()
            if (old and old["verdict"] and old["verdict"] != "PENDING_FINAL"
                    and old["verdict"] != verdict):
                conn.execute(
                    f"INSERT INTO etf_verdict_transitions (interval_end_date, ticker, "
                    f"rule_version, old_verdict, new_verdict, old_verdict_at, "
                    f"new_verdict_at, old_published_usd, new_published_usd) "
                    f"VALUES ({','.join([ph]*9)})",
                    (end_d, tkr, RULE_VERSION, old["verdict"], verdict,
                     old["verdict_at"], now, old["published_usd"], pusd))
                print(f"[ALERT][etf-reconcile] finalized verdict TRANSITION "
                      f"{tkr} {end_d}: {old['verdict']} -> {verdict} "
                      f"(comparator restatement? logged, never silent)")
        except Exception as _vte:
            print(f"[etf-reconcile] transition guard error ({tkr} {end_d}): {_vte}")
        conn.execute(
            f"INSERT INTO etf_reconcile_log2 (interval_end_date,ticker,rule_version,"
            f"interval_start_date,derived_usd,published_usd,material,direction_match,"
            f"within_band,verdict,src,comparator,verdict_at) "
            f"VALUES ({','.join([ph]*13)}) "
            f"ON CONFLICT (interval_end_date,ticker,rule_version) DO UPDATE SET "
            f"interval_start_date=EXCLUDED.interval_start_date, "
            f"derived_usd=EXCLUDED.derived_usd, published_usd=EXCLUDED.published_usd, "
            f"material=EXCLUDED.material, direction_match=EXCLUDED.direction_match, "
            f"within_band=EXCLUDED.within_band, verdict=EXCLUDED.verdict, "
            f"src=EXCLUDED.src, comparator=EXCLUDED.comparator, "
            f"verdict_at=EXCLUDED.verdict_at",
            (end_d, tkr, RULE_VERSION, start_d,
             None if dusd is None else round(dusd, 2), pusd,
             None if material is None else int(bool(material)),
             None if dirm is None else int(bool(dirm)),
             None if band is None else int(bool(band)),
             verdict, src or "fmp", source, now))
        summary["checked"] += 1

    try:
        for coin, cfg in cs.COIN_UNIVERSE.items():
            if coins and coin not in coins:
                continue
            etfs = [p["ticker"] for p in cfg.get("proxies", []) if p.get("kind") == "etf"]
            if not etfs:
                continue
            pub = fetch_published(coin, source)
            if not pub.get("available"):
                if pub.get("reason") == "no_comparator":
                    summary["no_comparator_coins"].append(coin)
                else:
                    summary.setdefault("fetch_errors", []).append(
                        {"coin": coin, "reason": pub.get("reason")})
                continue
            by_date = pub["by_date"]
            pub_dates = sorted(datetime.strptime(d, "%Y-%m-%d").date() for d in by_date)
            max_pub = pub_dates[-1] if pub_dates else None
            for tkr in etfs:
                strikes = _strikes_with_capture(tkr, db_path)
                covered = set()
                aum_latest = (strikes[-1].get("aum") if strikes else 0.0) or 0.0
                for i, (a, b) in enumerate(zip(strikes, strikes[1:])):
                    # A2.2: strike labels come from the page's own as-of stamp
                    # for basis-verified families; capture-instant fallback else.
                    ta, ma = t_of_strike(a)
                    tb, mb = t_of_strike(b)
                    if "missing_asof" in (ma, mb):
                        # Pre-A2.2 issuer strike (or a stamp that stopped
                        # parsing): the interval cannot be honestly labeled and
                        # is never guessed (§14). Its verdicts stand on the
                        # preserved A2 record; its days still count as COVERED
                        # (under the legacy labels) so the NO_DERIVED sweep does
                        # not retro-blame the source for days it watched (the
                        # 953c31c era class). Counted, never silent.
                        if (a.get("src") or "fmp") == (b.get("src") or "fmp"):
                            fa = t_of(a.get("captured_at"))
                            fb = t_of(b.get("captured_at"))
                            if fa and fb and fb > fa:
                                covered.update(_tdays_range(fa, fb))
                        summary["asof_unlabelable"] += 1
                        continue
                    if not ta or not tb or tb <= ta:
                        continue
                    if (a.get("src") or "fmp") != (b.get("src") or "fmp"):
                        continue                     # A2.3 splice rule: no Δ across seam
                    days = _tdays_range(ta, tb)
                    covered.update(days)
                    end_d, start_d = tb.isoformat(), ta.isoformat()
                    dusd = (b["shares"] - a["shares"]) * (b.get("nav") or 0.0)
                    is_latest = (i == len(strikes) - 2)
                    still_moving = is_latest or (max_pub and tb >= max_pub)
                    vals = [(by_date.get(d.isoformat()) or {}).get(tkr) for d in days]
                    if still_moving:
                        _upsert(end_d, tkr, start_d, dusd, None, None, None, None,
                                "PENDING_FINAL", b.get("src"))
                        summary["pending_final"] += 1
                        continue
                    floor = max(FLOOR_ABS_USD, FLOOR_AUM_FRAC * ((b.get("aum") or 0.0)))
                    if not days:
                        continue
                    if any(v is None for v in vals):
                        _upsert(end_d, tkr, start_d, dusd, None, None, None, None,
                                "NO_PUBLISHED", b.get("src"))
                        summary["no_published"] += 1
                        continue
                    psum = float(sum(vals))
                    # Standing basis monitor (board P1): a single-trading-day
                    # as-of interval IS the stamp+value identity check — under a
                    # correct ASOF_BASIS its derived Δ must keep reproducing the
                    # issuer's published flow, in every regime.
                    if ma == mb == "asof" and len(days) == 1:
                        _m = abs(dusd - psum) <= max(0.05 * abs(psum), 2_000_000)
                        basis_stats.setdefault(tkr, []).append(
                            (end_d, bool(_m), b.get("src") or "fmp"))
                    material = abs(psum) > floor
                    if not material and abs(dusd) > floor:
                        # Material derived flow the issuer says never happened —
                        # phantom flow (the FBTC weekend zigzag class). FAILS.
                        _upsert(end_d, tkr, start_d, dusd, psum, 1, 0, 0,
                                "EMPTY_INTERVAL", b.get("src"))
                        summary["empty_interval"] += 1
                        continue
                    if not material:
                        _upsert(end_d, tkr, start_d, dusd, psum, 0, None, None,
                                "IMMATERIAL", b.get("src"))
                        summary["immaterial"] += 1
                        continue
                    dirm = (dusd > 0) == (psum > 0)
                    band = abs(dusd - psum) <= max(BAND_REL * abs(psum), BAND_ABS_USD)
                    verdict = "PASS" if (dirm and band) else "FAIL"
                    _upsert(end_d, tkr, start_d, dusd, psum, 1, dirm, band, verdict,
                            b.get("src"))
                    summary["pass" if verdict == "PASS" else "fail"] += 1
                # A2.1.4 — NO_DERIVED sweep: material published days we never covered.
                # ERA ATTRIBUTION (2026-08-08, the source-swap defect): a day is blamed
                # on the source whose strike ERA covered it — never on the latest src.
                # Blaming src_latest made the new issuer source inherit every FMP-era
                # uncovered day at takeover (open_bad=12 on rows the issuer series is
                # STRUCTURALLY unable to cover — its first strike postdates them),
                # violating A2.4's "no FMP-era row counts toward any gate" and
                # permanently blocking re-arm. Era = t_of(first strike of each src run);
                # days before the first era belong to the first source ever seen.
                floor_nd = max(FLOOR_ABS_USD, FLOOR_AUM_FRAC * aum_latest)
                eras = []                            # [(era_start_T, src)] in order
                for s in strikes:
                    s_src = s.get("src") or "fmp"
                    # A2.2: era boundaries use the same per-strike label; a
                    # missing-asof strike still needs a boundary date, so it
                    # falls back to the capture-instant mapping (attribution
                    # only — such strikes are never SCORED under A2.2).
                    s_t, _sm = t_of_strike(s)
                    if s_t is None:
                        s_t = t_of(s.get("captured_at"))
                    if s_t and (not eras or eras[-1][1] != s_src):
                        eras.append((s_t, s_src))

                def _src_for_day(d):
                    # STRICT inequality: the boundary day d == era_start is the new
                    # source's baseline (its first strike settles THROUGH d — no
                    # interval can ever span it), so it stays with the prior era.
                    # COLD-START CORNER (board/Outsider, 2026-08-09): days at/before
                    # the FIRST era's start predate ALL coverage capability. For a
                    # legacy fund that era is FMP (blame stands, harmless to the
                    # gate); for a fund onboarded issuer-FIRST, blaming the issuer
                    # for pre-onboarding days would wrongly count against re-arm —
                    # they stamp the sentinel 'pre_coverage' instead (excluded from
                    # the re-arm bad-set like FMP; still visible as NO_DERIVED).
                    if not eras:
                        return "fmp"
                    if d <= eras[0][0]:
                        return eras[0][1] if eras[0][1] == "fmp" else "pre_coverage"
                    owner = eras[0][1]
                    for e_t, e_src in eras:
                        if e_t < d:
                            owner = e_src
                        else:
                            break
                    return owner

                for d in pub_dates:
                    if max_pub and d >= max_pub:
                        continue                     # comparator's edge not final
                    if len(_tdays_range(d, today_t)) < NO_DERIVED_GRACE_TDAYS:
                        continue                     # inside settlement/capture grace
                    if d in covered:
                        continue
                    v = (by_date.get(d.isoformat()) or {}).get(tkr)
                    if v is None or abs(v) <= floor_nd:
                        continue
                    _upsert(d.isoformat(), tkr, None, None, float(v), 1, None, None,
                            "NO_DERIVED", _src_for_day(d))
                    summary["no_derived"] += 1
        # Flush the standing basis monitor (recomputed from scratch — idempotent).
        for tkr, seq in basis_stats.items():
            seq.sort(key=lambda t: t[0])
            checked = len(seq)
            matched = sum(1 for _, m, _s in seq if m)
            consec = 0
            for _, m, _s in reversed(seq):
                if m:
                    break
                consec += 1
            fam = seq[-1][2]
            conn.execute(
                f"INSERT INTO etf_basis_check (ticker, family, checked, matched, "
                f"consec_mismatch, last_interval_end, updated_at) "
                f"VALUES ({','.join([ph]*7)}) "
                f"ON CONFLICT (ticker) DO UPDATE SET family=EXCLUDED.family, "
                f"checked=EXCLUDED.checked, matched=EXCLUDED.matched, "
                f"consec_mismatch=EXCLUDED.consec_mismatch, "
                f"last_interval_end=EXCLUDED.last_interval_end, "
                f"updated_at=EXCLUDED.updated_at",
                (tkr, fam, checked, matched, consec, seq[-1][0], now))
            if consec >= 2:
                print(f"[ALERT][etf-reconcile] BASIS DRIFT {tkr} ({fam}): "
                      f"{consec} consecutive single-day stamp+value mismatches — "
                      f"the declared ASOF_BASIS may have broken (issuer page "
                      f"semantics change); re-verify per §16 before trusting "
                      f"re-arm progress")
        summary["basis_checked_funds"] = len(basis_stats)
        conn.commit()
    finally:
        conn.close()
    return summary


def report_a2(db_path: str = DB_PATH, days: int = 21) -> dict:
    """A2 gate evidence. FIRES-FOREVER (board P1 fix 2026-08-18, Forecaster
    finding): the GATE, bias runs, and the A2.4 re-arm bad-set are computed over
    ALL rule_version rows UNWINDOWED — a bad row can never age out of the gate
    by calendar. The `days` window scopes only the per-fund DISPLAY tallies.
    Bias (board P1, Executioner): computed on issuer-source rows only — FMP is
    silent-comparison and per A2.4 never counts toward any flip decision.
    re_arm = flip-readiness per A2.4, non-FMP src rows only (re-eval 2026-09-05)."""
    init_reconcile_db2(db_path)
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        rows = [dict(r) for r in c.execute(
            f"SELECT * FROM etf_reconcile_log2 WHERE rule_version = {ph} "
            f"ORDER BY ticker, interval_end_date", (RULE_VERSION,)).fetchall()]
        prior = {r["verdict"]: r["n"] for r in c.execute(
            f"SELECT verdict, COUNT(*) AS n FROM etf_reconcile_log2 "
            f"WHERE rule_version = {ph} GROUP BY verdict", ("A2",)).fetchall()}
        basis_rows = [dict(r) for r in c.execute(
            "SELECT * FROM etf_basis_check ORDER BY ticker").fetchall()]
        trans = [dict(r) for r in c.execute(
            f"SELECT * FROM etf_verdict_transitions WHERE rule_version = {ph} "
            f"ORDER BY id DESC LIMIT 10", (RULE_VERSION,)).fetchall()]
    except Exception as e:
        return {"available": False, "reason": str(e)[:120]}
    finally:
        c.close()
    if not rows:
        return {"available": False, "reason": "A2 harness has not run yet",
                "rule_version": RULE_VERSION, "gate_status": "NOT_RUN"}
    by, fails, no_derived = {}, [], []
    errors_by = {}                      # issuer-src material PASS/FAIL sign errors
    for r in rows:
        in_window = (r["interval_end_date"] or "") >= since
        if in_window:
            t = by.setdefault(r["ticker"], {"pass": 0, "fail": 0, "immaterial": 0,
                                            "pending_final": 0, "empty_interval": 0,
                                            "no_derived": 0, "no_published": 0})
        v = r.get("verdict")
        if in_window:
            key = {"PASS": "pass", "FAIL": "fail", "IMMATERIAL": "immaterial",
                   "PENDING_FINAL": "pending_final", "EMPTY_INTERVAL": "empty_interval",
                   "NO_DERIVED": "no_derived", "NO_PUBLISHED": "no_published"}.get(v)
            if key:
                t[key] += 1
        rec = {k: r.get(k) for k in ("interval_end_date", "interval_start_date",
                                     "ticker", "derived_usd", "published_usd",
                                     "src", "verdict", "verdict_at")}
        if v in ("FAIL", "EMPTY_INTERVAL"):
            fails.append(rec)                     # ALL rows — fires forever
        elif v == "NO_DERIVED":
            no_derived.append(rec)                # ALL rows — fires forever
        if (r.get("material") and r.get("published_usd") is not None
                and r.get("derived_usd") is not None and v in ("PASS", "FAIL")
                and (r.get("src") or "fmp") not in ("fmp", "pre_coverage")):
            errors_by.setdefault(r["ticker"], []).append(
                1 if r["derived_usd"] > r["published_usd"] else -1)
    bias = []
    for t, errs in errors_by.items():
        run, prev, worst = 0, 0, 0
        for e in errs:
            run = run + 1 if e == prev else 1
            prev = e
            worst = max(worst, run)
        if worst >= BIAS_RUN:
            bias.append({"ticker": t, "consecutive_same_sign_error": worst})
    material_total = sum(
        1 for r in rows if r.get("verdict") in ("PASS", "FAIL"))
    basis_drift = [b for b in basis_rows if (b.get("consec_mismatch") or 0) >= 2]
    gate = ("FAIL" if fails or bias or no_derived or basis_drift else
            "PASS" if material_total >= 1 else "NO_MATERIAL_DAYS_YET")
    # A2.4 re-arm: non-FMP src only (issuer-page source), Chairman standard = 5.
    # 'pre_coverage' rows (days predating a fund's first-ever source era — the
    # cold-start sentinel) are likewise excluded from the bad-set: no source that
    # counts toward the gate was on duty for them. They can never be PASS rows.
    np_rows = [r for r in rows
               if (r.get("src") or "fmp") not in ("fmp", "pre_coverage")]
    np_pass = [r for r in np_rows if r.get("verdict") == "PASS" and r.get("material")]
    np_bad = [r for r in np_rows if r.get("verdict") in
              ("FAIL", "EMPTY_INTERVAL", "NO_DERIVED")]
    re_arm = {
        "standard": "A2.4: >=5 material in-band comparisons on the issuer-page source, "
                    ">=2 funds, >=3 distinct trading days, zero FAIL/EMPTY_INTERVAL/"
                    "NO_DERIVED, zero bias; clocks restarted; FMP rows never count",
        "pass_comparisons": len(np_pass),
        "funds": len({r["ticker"] for r in np_pass}),
        "trading_days": len({r["interval_end_date"] for r in np_pass}),
        "open_bad": len(np_bad),
        "ready": (len(np_pass) >= 5 and len({r["ticker"] for r in np_pass}) >= 2 and
                  len({r["interval_end_date"] for r in np_pass}) >= 3 and
                  not np_bad and not bias),
    }
    fmp_fails = [f for f in fails if (f.get("src") or "fmp") == "fmp"]
    live_fails = [f for f in fails if (f.get("src") or "fmp") != "fmp"]
    return {
        "available": True, "rule_version": RULE_VERSION,
        "window_days": days,
        "window_note": "the window scopes DISPLAY tallies only; gate/bias/"
                       "re-arm/fail lists are computed over ALL rows — a bad "
                       "row never ages out (fires-forever, board P1 2026-08-18)",
        "funds": by, "material_comparisons": material_total,
        # Prior-rule visibility (board P1, Forecaster): the superseded A2-era
        # record, so a clean A2.2 sheet is never mistaken for a clean history.
        "superseded_a2_rows": prior or None,
        "basis_verification": {
            "standard": "single-trading-day as-of intervals must reproduce the "
                        "issuer's published flow (tolerance max(5%, $2M)); >=2 "
                        "consecutive mismatches = declared-basis drift alarm "
                        "(fails the gate; re-verify per §16)",
            "funds": basis_rows or None,
            "drift": basis_drift or None,
        },
        "verdict_transitions_recent": trans or None,
        "open_failures": fails or None,
        "open_failures_fmp": len(fmp_fails),
        "open_failures_live_source": live_fails or None,
        "no_derived": no_derived or None, "bias_flags": bias or None,
        "re_arm": re_arm,
        "no_comparator": ["XRP fund (TOXR) — no published-flow page exists; honest "
                          "absence, never implied covered. (XRPC removed from the "
                          "roster 2026-08-11, Chairman order — frozen issuer page)"],
        "band": {"floor": "max($10M, 0.05% AUM)", "direction": "mandatory on material "
                 "intervals", "magnitude": "±25% or ±$20M (more forgiving)",
                 "bias_rule": f">={BIAS_RUN} consecutive same-sign errors fail",
                 "join": "A2.2 interval-cumulative, as-of-keyed (T from the issuer "
                         "page's own stamp + per-family basis; capture-instant t_of "
                         "fallback for FMP / unverified families)"},
        "gate_status": gate,
        "note": "Held-out verifier under amendment A2.2 (Chairman-approved 2026-08-18; "
                "trace A2_SIGNFLIP_TRACE_2026-08-18.md). A2 + A1.5 records preserved, "
                "never rewritten; this report reads A2.2 rows only, so the A2.4 re-arm "
                "clocks restarted at deploy. FMP rows are silent-comparison only "
                "(re-eval 2026-09-05); re-arm counts issuer-source rows exclusively. "
                "Post-swap PASSes verify pipeline fidelity, not independent "
                "confirmation.",
    }


if __name__ == "__main__":
    import json
    print("=== etf_flow_reconcile — one live A2 pass ===")
    print(json.dumps(reconcile_a2(), indent=1)[:1400])
    print("\n--- A2 report ---")
    print(json.dumps(report_a2(), indent=1)[:2400])
