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

DATE RULE (survey hazard 2): issuers stamp mixed conventions (iShares/21Shares
same-day; Bitwise/Canary T-1). We do NOT interpret their stamps — the A2
t_of/settled-through mapping keys on OUR capture instant (captured_at), per the
pre-declared spec. The page's own as-of date is logged for the eyeball only.

SPLICE (A2.3): the first issuer row after an FMP row is a source seam — the
harness and latest_delta never compute Δshares across it; the issuer series
re-earns its own history (clocks restarted, A2.4).

COVERAGE, stated honestly (wave 1+2 of the survey's build order):
  ishares   IBIT ETHA        — product page JSON blob (browser-grade UA; 403 bare)
  bitwise   BITB ETHW BSOL   — server-rendered fundDetails JSON (T-1 stamps)
  21shares  ARKB TSOL TOXR   — server-rendered ki4/nav data elements (same-day)
  canary    XRPC             — wpDataTables daily history table (T-1)
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
from datetime import datetime, timezone

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

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
    am = re.search(r'data-element="nav-aum".{0,400}?\$([\d,\.]+)\s*([MB]?)', html, re.S)
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


def _parse_canary(html: str) -> dict | None:
    """Canary XRPC: wpDataTables daily history rendered server-side. Rows carry
    [Fund Name, Ticker, CUSIP, Net Assets, Shares Outstanding, NAV, ..., Rate Date].
    Take the newest dated row; T-1 stamps are fine (capture-instant rule)."""
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S)
    best = None            # (date_iso, shares, nav, aum)
    for r in rows:
        cells = [re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if len(cells) < 7 or "XRPC" not in cells[:3]:
            continue
        nums = {}
        try:
            aum = _f(cells[3])
            shares = _f(cells[4])
            nav = _f(cells[5])
        except Exception:
            continue
        date_iso = None
        for c in reversed(cells):
            try:
                from date_utils import to_iso_date
                date_iso = to_iso_date(c)
            except Exception:
                date_iso = None
            if date_iso:
                break
        if not (shares and nav and date_iso):
            continue
        if best is None or date_iso > best[0]:
            best = (date_iso, shares, nav, aum)
    if not best:
        return None
    return {"shares": best[1], "nav": best[2], "aum": best[3], "asof": best[0]}


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
    "XRPC": ("issuer_canary", "https://canaryetfs.com/xrpc", _parse_canary),
}

#: Tickers whose daily STRIKE row is issuer-sourced — etf_flow.snapshot() (FMP)
#: demotes to observations-only for these when ETF_ISSUER_PRIMARY=1.
COVERED = frozenset(ADAPTERS.keys())


def fetch_one(ticker: str) -> dict | None:
    """Live fetch+parse for one fund. None = declared absence (fail-closed)."""
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
    if out:
        out["src"] = src
        out["url"] = url
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
            src = info["src"]
            try:
                c.execute(
                    f"INSERT INTO etf_share_observations "
                    f"(ticker,captured_at,shares,aum,nav,src) "
                    f"VALUES ({ph},{ph},{ph},{ph},{ph},{ph}) ON CONFLICT DO NOTHING",
                    (t, now_iso, info["shares"], info.get("aum"), info["nav"], src))
                row = c.execute(
                    f"SELECT shares, nav, src FROM etf_share_snapshots "
                    f"WHERE ticker={ph} AND snapshot_date={ph}", (t, today)).fetchone()
                if row is None:
                    c.execute(
                        f"INSERT INTO etf_share_snapshots "
                        f"(ticker,snapshot_date,shares,aum,nav,captured_at,src) "
                        f"VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph}) "
                        f"ON CONFLICT (ticker,snapshot_date) DO NOTHING",
                        (t, today, info["shares"], info.get("aum"), info["nav"],
                         now_iso, src))
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
                            f"nav={ph}, captured_at={ph}, src={ph} "
                            f"WHERE ticker={ph} AND snapshot_date={ph}",
                            (info["shares"], info.get("aum"), info["nav"], now_iso,
                             src, t, today))
                        out["takeovers"] += 1
                    elif changed:
                        c.execute(
                            f"UPDATE etf_share_snapshots SET shares={ph}, aum={ph}, "
                            f"nav={ph}, captured_at={ph} "
                            f"WHERE ticker={ph} AND snapshot_date={ph}",
                            (info["shares"], info.get("aum"), info["nav"], now_iso,
                             t, today))
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
        _ch.log_collector_run("issuer_shares", len(out["tickers"]),
                              "success" if out["tickers"] else "failure",
                              db_path=db_path,
                              distinct_keys=len(out["tickers"]))
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
