"""
etf_issuer_pages.py — ISSUER-PAGE daily shares outstanding (A2.3 primary source).
HELD-OUT, RECORD-ONLY: writes etf_share_observations / etf_share_snapshots with
src='issuer_<family>'; feeds no score, no ledger. The A2 reconciliation harness
(etf_flow_reconcile.reconcile_a2) scores these rows; re-arm (A2.4) counts ONLY them.

WHY (Chairman ruling b, 2026-08-05): FMP `etf/info` shares outstanding failed §16
CURRENCY at Gate 4 — IBIT frozen 4+ days through ~$282M of published inflow, FBTC
zigzagging ±$150–290M phantom swings. The issuers' own product pages publish the
real daily figure (official, direct, §15-compliant). FMP keeps pulling SILENTLY
into etf_share_observations for the 30-day comparison (re-eval 2026-09-05); the
scored daily STRIKE series (etf_share_snapshots) is issuer-sourced from the
takeover onward. §16 survey: audits/source-onboarding/ISSUER_PAGES_SURVEY_2026-08-05.md.

FAIL-CLOSED (A2.3): an adapter that cannot parse BOTH shares AND nav from the live
page returns nothing — declared absence, never a stale or guessed value. A frozen
issuer page then surfaces as NO_DERIVED in the harness (failure, never silence).

DATE RULE (AMENDED under A2.2, Chairman-approved 2026-08-18 — root-cause trace
audits/board/A2_SIGNFLIP_TRACE_2026-08-18.md): the page's OWN as-of stamp is now
CAPTURED (canonicalized via date_utils.to_iso_date → `page_asof` on observations +
snapshots) and is the A2.2 reconcile join key for families with a VERIFIED
share-count basis (etf_flow_reconcile.ASOF_BASIS — iShares settled / 21Shares
trade). The original rule ("we do NOT interpret their stamps"; capture-instant
t_of) mislabeled issuer intervals by ±1 trading day, because page rollover latency
varies by fund AND by day (IBIT posted as-of-D at T+1 ~16:30 ET on 08-11..15 but
T+0 ~22:49 ET on 08-17) — only the stamp names its own day. The stamp was already
trusted for the staleness guard; A2.2 extends that trust to labeling. Families
without a stamp+value-verified basis (Bitwise) keep the capture-instant fallback.

SPLICE (A2.3): the first issuer row after an FMP row is a source seam — the
harness and latest_delta never compute Δshares across it; the issuer series
re-earns its own history (clocks restarted, A2.4).

COVERAGE, stated honestly (wave 1+2 of the survey's build order):
  ishares   IBIT ETHA        — product page JSON blob (browser-grade UA; 403 bare)
  bitwise   BITB ETHW BSOL   — server-rendered fundDetails JSON (T-1 stamps)
  21shares  ARKB TSOL TOXR   — server-rendered ki4/nav data elements (same-day)
REMOVED (Chairman order 2026-08-11):
  canary    XRPC             — wpDataTables adapter worked, but the page itself sat
                               frozen at as-of 2026-07-31 (>3 tdays; 0 production
                               successes) — the staleness guard held it in declared
                               absence permanently. Roster row deleted; XRP proxy
                               exposure via ticker XRPC in crypto_signals is a
                               DIFFERENT usage (Finviz data, not the issuer page)
                               and is unaffected.
NOT covered this wave (fail-closed absence; wave 3 per the survey):
  grayscale GBTC ETHE GSOL   — 429 bot-wall to plain fetch (needs UA/session work)
  vaneck    HODL             — redirect loop headless; direct field unconfirmed
  fidelity  FBTC FETH        — derived-precise (coin-in-fund ÷ coin-per-share);
                               dashboard is JS-hydrated, no plain-fetch path proven
"""
from __future__ import annotations

import os
import re
import time
from datetime import datetime, timedelta, timezone

import db_compat

try:
    from zoneinfo import ZoneInfo
    _ET = ZoneInfo("America/New_York")
except Exception:                                   # tzdata-less fallback (dev boxes)
    _ET = timezone(timedelta(hours=-4))

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

# Board conditions (BOARD_a2-fix_2026-08-08, Chairman-approved 2026-08-09):
#  IDENTITY CHECK — the pages themselves publish shares, NAV, AND AUM; shares×NAV
#  must reconcile to AUM within tolerance or the parse is rejected (fail-closed).
#  Converts most MIS-parse modes (regex repointed at a plausible wrong number) into
#  declared absence. Tolerance is loose (15%) because NAV/AUM as-of stamps can lag
#  each other by a day (Bitwise) and crypto moves — mis-parses miss by magnitudes.
_IDENTITY_TOL = float(os.getenv("ISSUER_IDENTITY_TOL", "0.15"))
#  STALENESS GUARD — a page that keeps PARSING a frozen value is invisible to
#  fail-closed (the XRPC 9-day-stale as-of in the first live capture). If the
#  page's own as-of stamp parses and is older than N trading days, the fund reads
#  declared absence. An unparseable stamp logs a notice but does not reject (the
#  identity check still guards values; date-format drift must not dark a family).
_ASOF_MAX_TDAYS = int(os.getenv("ISSUER_ASOF_MAX_TDAYS", "3"))

#: SCHEDULED SERIES BREAKS (pre-declared per A2 annex 2026-08-09 — never ad hoc).
#: A known corporate action gets a fund-scoped src EPOCH effective on its date: the
#: splice rule then voids Δshares across the seam and era attribution assigns the
#: boundary day to the prior epoch — zero new comparison logic, one stamp. The
#: epoch names the SOURCE LINEAGE (same issuer, re-denominated instrument): the
#: fund's Δ-clock restarts; the source's earned standing does NOT reset.
SCHEDULED_BREAKS = {
    "ETHA": {"effective": "2026-10-06", "epoch_src": "issuer_ishares_r1",
             "reason": "iShares ETHA reverse split (survey hazard 1; pre-declared "
                       "2026-08-09, board-unanimous)"},
}

# Browser-grade UA (iShares 403s bare fetches) carrying our declared token — honest
# identification without tripping the CDN's bare-client wall. Env-overridable.
_UA = os.getenv("ISSUER_UA",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 NowTrendIn/2.0")
_FETCH_PAUSE_S = float(os.getenv("ISSUER_FETCH_PAUSE_S", "2"))
_TIMEOUT_S = float(os.getenv("ISSUER_FETCH_TIMEOUT_S", "30"))


def _get(url: str) -> str | None:
    try:
        import requests
        r = requests.get(url, timeout=_TIMEOUT_S, headers={"User-Agent": _UA})
        if r.status_code != 200 or not r.text:
            print(f"[issuer-pages] {url}: HTTP {r.status_code}")
            return None
        return r.text
    except Exception as e:
        print(f"[issuer-pages] {url}: {e}")
        return None


def _f(s) -> float | None:
    try:
        v = float(str(s).replace(",", "").replace("$", "").strip())
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


# ── Per-family parsers — each returns {"shares","nav","aum","asof"} or None ──────

def _parse_ishares(html: str) -> dict | None:
    """BlackRock product page: key-fund-facts JSON blob is server-rendered but
    HTML-entity-encoded (&quot;) on the live page (verified 2026-08-08) — unescape
    first, then the blob reads ..."formattedValue":"1,318,000,000",...,
    "formattedAsOfDate":"Aug 07, 2026","name":"sharesOutstanding"... Fallback:
    the rendered span webqc-datapoint="keyFundFacts-sharesOutstanding">N</span>."""
    page = html.replace("&quot;", '"')
    m = re.search(r'"formattedValue":"([\d,]+)"[^{}]*?"name":"sharesOutstanding"', page)
    shares = _f(m.group(1)) if m else None
    asof = None
    if m:
        d = re.search(r'"formattedAsOfDate":"([^"]+)"', m.group(0))
        asof = d.group(1) if d else None
    if not shares:
        m2 = re.search(r'webqc-datapoint="keyFundFacts-sharesOutstanding">([\d,]+)<',
                       page)
        shares = _f(m2.group(1)) if m2 else None
        if shares and not asof:
            d2 = re.search(r'keyFundFacts-sharesOutstanding-asOf">as of(?:<!-- -->'
                           r'|\s)*([A-Z][a-z]+ \d{1,2}, \d{4})', page)
            asof = d2.group(1) if d2 else None
    nav_m = re.search(r'"navAmount":\{[^{}]*?"value":([\d.]+)', page)
    nav = _f(nav_m.group(1)) if nav_m else None
    aum_m = re.search(r'"formattedValue":"([\d,]+)"[^{}]*?"name":"totalNetAssetsFundLevel"',
                      page)
    aum = _f(aum_m.group(1)) if aum_m else None
    if not (shares and nav):
        return None
    return {"shares": shares, "nav": nav, "aum": aum, "asof": asof}


def _parse_bitwise(html: str) -> dict | None:
    """Bitwise fund sites: server-rendered fundData blob. Shape (verified live):
    "fundDetails":{..."netAssets":2407727121.99,"sharesOutstanding":68380000,...,
    "asOfDate":"2026-08-07"} plus "navAndMarketPrice":{"nav":34.94."""
    m = re.search(r'"fundDetails":\{[^{}]*?"netAssets":([\d.]+),"sharesOutstanding":(\d+)'
                  r'[^{}]*?"asOfDate":"(\d{4}-\d{2}-\d{2})"', html)
    if not m:
        return None
    aum, shares, asof = _f(m.group(1)), _f(m.group(2)), m.group(3)
    nav_m = re.search(r'"navAndMarketPrice":\{"nav":([\d.]+)', html)
    nav = _f(nav_m.group(1)) if nav_m else None
    if not (shares and nav):
        return None
    return {"shares": shares, "nav": nav, "aum": aum, "asof": asof}


def _parse_21shares(html: str) -> dict | None:
    """21Shares product pages: data-element blocks. Shape (verified live):
    data-element="ki4-shares-outstanding"...>SHARES OUTSTANDING</div><div ...>103460000<
    NAV per unit under ki3-nav-per-unit; page-level 'as of Aug 07, 2026'."""
    m = re.search(r'ki4-shares-outstanding.{0,300}?sans-body-copy-2b">([\d,\.]+)<',
                  html, re.S)
    shares = _f(m.group(1)) if m else None
    nav = None
    for pat in (r'ki3-nav-per-unit.{0,300}?sans-body-copy-2b">\$?([\d,\.]+)<',
                r'data-element="nav-nav".{0,400}?\$([\d,]+\.\d+)'):
        nm = re.search(pat, html, re.S)
        if nm:
            nav = _f(nm.group(1))
            if nav:
                break
    aum = None
    # 2026-08-18 template (A2 sign-flip trace §7): the "$" and the value sit in
    # SIBLING divs under data-element="nav-aum" — the old adjacent "$1.9B" pattern
    # went silently inert, which left the shares×NAV≈AUM identity check dead for
    # the whole family. New split-div patterns first; legacy suffixed form kept
    # as fallback for the old template. Never guessed: no match → aum stays None
    # and fetch_one fails CLOSED for this family (_AUM_REQUIRED).
    for pat in (r'data-element="nav-aum".{0,300}?>\$</div><div[^>]*>([\d,\.]+)<',
                r'data-element="ki3-aum".{0,400}?>\$</div><div[^>]*>([\d,\.]+)<'):
        am = re.search(pat, html, re.S)
        if am:
            aum = _f(am.group(1))
            if aum:
                break
    if not aum:
        am = re.search(r'data-element="nav-aum".{0,400}?\$([\d,\.]+)\s*([MB]?)',
                       html, re.S)
        if am:
            aum = _f(am.group(1))
            if aum and am.group(2) == "M":
                aum *= 1e6
            elif aum and am.group(2) == "B":
                aum *= 1e9
    dm = re.search(r'as of ([A-Z][a-z]+ \d{1,2}, \d{4})', html)
    asof = dm.group(1) if dm else None
    if not (shares and nav):
        return None
    return {"shares": shares, "nav": nav, "aum": aum, "asof": asof}


#: ticker → (src id, url, parser). One entry per fund; a new issuer is one row +
#: (at most) one parser. Order = fetch order (family-grouped, batch-paced).
ADAPTERS = {
    "IBIT": ("issuer_ishares",
             "https://www.blackrock.com/us/individual/products/333011/"
             "ishares-bitcoin-trust-etf", _parse_ishares),
    "ETHA": ("issuer_ishares",
             "https://www.blackrock.com/us/individual/products/337614/"
             "ishares-ethereum-trust-etf", _parse_ishares),
    "BITB": ("issuer_bitwise", "https://bitbetf.com/", _parse_bitwise),
    "ETHW": ("issuer_bitwise", "https://ethwetf.com/", _parse_bitwise),
    "BSOL": ("issuer_bitwise", "https://bsoletf.com/", _parse_bitwise),
    "ARKB": ("issuer_21shares",
             "https://www.21shares.com/en-us/products-us/arkb", _parse_21shares),
    "TSOL": ("issuer_21shares",
             "https://www.21shares.com/en-us/products-us/tsol", _parse_21shares),
    "TOXR": ("issuer_21shares",
             "https://www.21shares.com/en-us/products-us/toxr", _parse_21shares),
}

#: Tickers whose daily STRIKE row is issuer-sourced — etf_flow.snapshot() (FMP)
#: demotes to observations-only for these when ETF_ISSUER_PRIMARY=1.
COVERED = frozenset(ADAPTERS.keys())

#: Families whose pages ALWAYS publish AUM: a missing/unparseable AUM there means
#: the PARSE broke, so the shares×NAV≈AUM identity check would run silently inert
#: (the 2026-08-18 A2 sign-flip trace found exactly that on 21Shares — check dead,
#: NO_DERIVED floor collapsed to flat $10M, shadow votes reading "AUM $0"). These
#: families fail CLOSED to declared absence on missing AUM — never a value the
#: identity check could not guard, never a guessed AUM. Families NOT listed keep
#: the N1.4 contract (genuinely-no-AUM funds unaffected — regression t1).
_AUM_REQUIRED = frozenset({"issuer_21shares"})


def _tdays_ago(iso_date: str) -> int | None:
    """Trading days (Mon–Fri, holidays not excluded — same declared basis as the
    harness) between iso_date and today UTC. None if unparseable."""
    try:
        d = datetime.strptime(iso_date, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None
    today = datetime.now(timezone.utc).date()
    n, cur = 0, d
    while cur < today:
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            n += 1
    return n


def _epoch_src(ticker: str, src: str, now_utc: datetime) -> str:
    """Apply a pre-declared scheduled series break: captures whose effective ET
    date (pre-dawn belongs to the prior day, mirroring t_of) is on/after the
    break's effective date carry the epoch src. Deterministic, fund-scoped."""
    b = SCHEDULED_BREAKS.get(ticker.upper())
    if not b:
        return src
    et = now_utc.astimezone(_ET)
    eff = et.date()
    if et.hour < 6:
        eff -= timedelta(days=1)
    return b["epoch_src"] if eff.isoformat() >= b["effective"] else src


def fetch_one(ticker: str) -> dict | None:
    """Live fetch+parse for one fund. None = declared absence (fail-closed):
    no page, no parse, stale as-of, or shares×NAV≉AUM all read as absence."""
    ent = ADAPTERS.get(ticker.upper())
    if not ent:
        return None
    src, url, parser = ent
    html = _get(url)
    if not html:
        return None
    try:
        out = parser(html)
    except Exception as e:
        print(f"[issuer-pages] {ticker} parse error: {e}")
        return None
    if not out:
        return None
    # AUM-REQUIRED FAIL-CLOSED (A2.2 hardening, 2026-08-18 trace §7): on a family
    # whose page always publishes AUM, a missing AUM means the parse broke and the
    # identity check below would silently not run — declared absence instead.
    if not out.get("aum") and src in _AUM_REQUIRED:
        print(f"[issuer-pages] {ticker} AUM unparseable on an AUM-publishing family "
              f"({src}) — identity check cannot run; declared absence (fail-closed)")
        return None
    # STALENESS GUARD (board A-2/Executioner-2): canonicalize the page's own as-of.
    asof_iso = None
    if out.get("asof"):
        try:
            from date_utils import to_iso_date
            asof_iso = to_iso_date(out["asof"])
        except Exception:
            asof_iso = None
        if asof_iso:
            age = _tdays_ago(asof_iso)
            if age is not None and age > _ASOF_MAX_TDAYS:
                print(f"[issuer-pages] {ticker} STALE page as-of {asof_iso} "
                      f"({age} trading days old > {_ASOF_MAX_TDAYS}) — declared absence")
                return None
        else:
            print(f"[issuer-pages] {ticker} as-of stamp unparseable "
                  f"({out['asof']!r}) — value kept; identity check still guards")
    # IDENTITY CHECK (board/Challenger A-1): shares × NAV ≈ AUM or reject.
    aum = out.get("aum")
    if aum:
        implied = out["shares"] * out["nav"]
        dev = abs(implied - aum) / aum
        if dev > _IDENTITY_TOL:
            print(f"[issuer-pages] {ticker} IDENTITY FAIL: shares×NAV "
                  f"${implied/1e6:.1f}M vs AUM ${aum/1e6:.1f}M ({dev:.1%} > "
                  f"{_IDENTITY_TOL:.0%}) — probable mis-parse, declared absence")
            return None
    out["src"] = src
    out["url"] = url
    if asof_iso:
        out["asof_iso"] = asof_iso
    return out


def snapshot_issuer(db_path: str = DB_PATH, tickers=None) -> dict:
    """Record today's issuer-page share counts. Idempotent; same table conventions
    as etf_flow.snapshot() but src='issuer_<family>' and the strike-update rule
    keys on the (shares, nav) PAIR changing (the issuer field of record is shares;
    NAV alone is price noise, shares alone without a NAV strike still counts)."""
    import etf_flow
    try:
        import date_utils
        today = date_utils.to_iso_date(datetime.now(timezone.utc).isoformat()) or \
            datetime.now(timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = {"date": today, "written": 0, "strikes_updated": 0, "takeovers": 0,
           "missing": [], "tickers": {}}
    if os.getenv("ETF_ISSUER_PAGES", "1") != "1":
        out["disabled"] = True
        return out
    etf_flow.init_etf_db(db_path)
    c = etf_flow._connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    # Microsecond precision: the FMP pass stamps captured_at at SECOND resolution and
    # runs back-to-back with this one — a same-second issuer observation would collide
    # on the (ticker, captured_at) PK and silently drop (caught in the 2026-08-08
    # behavior test). t_of() parses either resolution identically.
    now_iso = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    roster = [t for t in (tickers or etf_flow.ETF_PROXIES) if t in COVERED]
    try:
        for i, t in enumerate(roster):
            if i:
                time.sleep(_FETCH_PAUSE_S)          # batch-paced (founder rule §13)
            info = fetch_one(t)
            if not info:
                out["missing"].append(t)
                continue
            # Pre-declared scheduled break (ETHA 2026-10-06): fund-scoped epoch src.
            src = _epoch_src(t, info["src"], datetime.now(timezone.utc))
            # A2.2: persist the page's own §14-canonical as-of stamp (asof_iso from
            # fetch_one; None when the stamp did not parse — never guessed).
            asof_iso = info.get("asof_iso")
            try:
                c.execute(
                    f"INSERT INTO etf_share_observations "
                    f"(ticker,captured_at,shares,aum,nav,src,page_asof) "
                    f"VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph}) "
                    f"ON CONFLICT DO NOTHING",
                    (t, now_iso, info["shares"], info.get("aum"), info["nav"], src,
                     asof_iso))
                row = c.execute(
                    f"SELECT shares, nav, src FROM etf_share_snapshots "
                    f"WHERE ticker={ph} AND snapshot_date={ph}", (t, today)).fetchone()
                if row is None:
                    c.execute(
                        f"INSERT INTO etf_share_snapshots "
                        f"(ticker,snapshot_date,shares,aum,nav,captured_at,src,"
                        f"page_asof) "
                        f"VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph}) "
                        f"ON CONFLICT (ticker,snapshot_date) DO NOTHING",
                        (t, today, info["shares"], info.get("aum"), info["nav"],
                         now_iso, src, asof_iso))
                    out["written"] += 1
                else:
                    r = dict(row) if hasattr(row, "keys") else \
                        {"shares": row[0], "nav": row[1], "src": row[2]}
                    old_src = r.get("src") or "fmp"
                    changed = (abs((r.get("shares") or 0) - info["shares"]) > 1e-9 or
                               abs((r.get("nav") or 0) - info["nav"]) > 1e-9)
                    if old_src != src:
                        # One-time takeover of the day's strike row from FMP —
                        # the seam; splice rule voids deltas across it downstream.
                        c.execute(
                            f"UPDATE etf_share_snapshots SET shares={ph}, aum={ph}, "
                            f"nav={ph}, captured_at={ph}, src={ph}, page_asof={ph} "
                            f"WHERE ticker={ph} AND snapshot_date={ph}",
                            (info["shares"], info.get("aum"), info["nav"], now_iso,
                             src, asof_iso, t, today))
                        out["takeovers"] += 1
                    elif changed:
                        c.execute(
                            f"UPDATE etf_share_snapshots SET shares={ph}, aum={ph}, "
                            f"nav={ph}, captured_at={ph}, page_asof={ph} "
                            f"WHERE ticker={ph} AND snapshot_date={ph}",
                            (info["shares"], info.get("aum"), info["nav"], now_iso,
                             asof_iso, t, today))
                        out["strikes_updated"] += 1
                out["tickers"][t] = {"shares": round(info["shares"]),
                                     "nav": info["nav"], "src": src,
                                     "page_asof": info.get("asof")}
            except Exception as e:
                print(f"[issuer-pages] {t} write: {e}")
        c.commit()
    finally:
        c.close()
    try:
        import collector_health as _ch
        # Aggregate row + one row PER FAMILY (board Q5, unanimous — the S2 rule:
        # families fail independently; aggregation hid the finnhub sub-source
        # failure). Family = the adapter's base src id, never the epoch variant.
        _ch.log_collector_run("issuer_shares", len(out["tickers"]),
                              "success" if out["tickers"] else "failure",
                              db_path=db_path,
                              distinct_keys=len(out["tickers"]))
        fam_total, fam_ok = {}, {}
        for t in roster:
            fam = ADAPTERS[t][0]
            fam_total[fam] = fam_total.get(fam, 0) + 1
            if t in out["tickers"]:
                fam_ok[fam] = fam_ok.get(fam, 0) + 1
        for fam, total in fam_total.items():
            n = fam_ok.get(fam, 0)
            _ch.log_collector_run(fam, n, "success" if n else "failure",
                                  db_path=db_path, distinct_keys=n)
    except Exception:
        pass
    print(f"[issuer-pages] {today}: parsed={len(out['tickers'])} new={out['written']} "
          f"strikes={out['strikes_updated']} takeovers={out['takeovers']} "
          f"missing={out['missing']}")
    return out


if __name__ == "__main__":
    import json
    print("=== etf_issuer_pages live parse test (no DB writes) ===\n")
    for t in ADAPTERS:
        info = fetch_one(t)
        print(f"{t}: {json.dumps(info) if info else 'ABSENT (fail-closed)'}")
        time.sleep(_FETCH_PAUSE_S)
