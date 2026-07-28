"""
finviz_data.py — Finviz Elite connector (HELD-OUT / flag-gated; imported by nothing in scoring yet).

Onboarded per §16 as a paid ($30/mo) market + Dark-Matter source. Two capabilities:

  • insider_feed()      — MARKET-WIDE SEC Form-4 insider transactions (insidertrading.ashx). The Dark-Matter
                          goldmine: ~100 most-recent insider buys/sells across ALL tickers in ONE call,
                          continuously refreshed, with $ values — NO per-ticker cap (vs Alpha Vantage 25/day).
  • insider_signal(t)   — per-ticker net insider $ flow + direction. Returns the SAME shape as
                          av_dark_positioning.insider_signal() so it can be a drop-in PRIMARY insider source.
  • screener()          — equity market data via the CSV export (export/screener): price, change, market cap,
                          P/E, volume (+ more via view/columns). MARKET (M) breadth in one call.

NOTE on crypto: Finviz crypto is DISPLAY-ONLY (not screenable/exportable) — crypto prices stay on FMP.
Finviz's value here is INSIDER (D) + EQUITY MARKET (M), not crypto.

Reads FINVIZ_API_KEY. A FACT from SEC filings / market data — never advice. Held-out until
backtest-before-ship wires it into any score. Dates normalize through date_utils at integration time (§14).
"""
from __future__ import annotations
import os
import re
import csv
import io
import time
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from typing import Optional

FINVIZ_API_KEY = os.getenv("FINVIZ_API_KEY", "")
_BASE = "https://elite.finviz.com"
_UA = {"User-Agent": "Mozilla/5.0 (NowTrendIn/2.0 research)"}
MIN_USD = float(os.getenv("FINVIZ_INSIDER_MIN_USD", "250000"))      # materiality floor (match AV)
INSIDER_WINDOW_DAYS = int(os.getenv("FINVIZ_INSIDER_WINDOW_DAYS", "90"))
_TTL = float(os.getenv("FINVIZ_TTL_SEC", "3600"))                   # 1h cache (insider refreshes intraday)
_MIN_INTERVAL = float(os.getenv("FINVIZ_MIN_INTERVAL_SEC", "1.0"))  # gentle self-throttle (fair use)
_CACHE: dict = {}
_last_call = [0.0]

# Form-4 transaction → direction. Open-market conviction trades only; comp/derivative noise excluded.
_BUY = {"buy", "purchase"}
_SELL = {"sale", "sell"}
# "Option Exercise", "Gift", "Conversion", etc. → excluded (not an open-market conviction trade).


def available() -> bool:
    return bool(FINVIZ_API_KEY)


def _throttle():
    wait = _MIN_INTERVAL - (time.time() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    _last_call[0] = time.time()


def _fetch(path: str, params: dict) -> Optional[str]:
    if not FINVIZ_API_KEY:
        return None
    _throttle()
    qs = urlencode({**params, "auth": FINVIZ_API_KEY})
    url = f"{_BASE}/{path}?{qs}"
    try:
        with urlopen(Request(url, headers=_UA), timeout=25) as r:   # urllib follows the 301 on legacy paths
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"[finviz] {path}: {e}")
        return None


def _cached(key: str, fn):
    ent = _CACHE.get(key)
    if ent and time.time() - ent["ts"] < _TTL:
        return ent["data"]
    data = fn()
    _CACHE[key] = {"data": data, "ts": time.time()}
    return data


def _num(x) -> Optional[float]:
    try:
        return float(str(x).replace(",", "").replace("$", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


# ── MARKET (M): screener CSV export ─────────────────────────────────────────────────────────
def screener(filters: str = "", view: str = "111", columns: str = "", tickers: str = "") -> list:
    """Equity market data as a list of dicts. `filters` = Finviz f= string (e.g. 'cap_mega,sec_technology');
    `view` = v= code; `columns` = c= numeric column list; `tickers` = comma list (t=). One call, many rows."""
    params = {"v": view}
    if filters:
        params["f"] = filters
    if columns:
        params["c"] = columns
    if tickers:
        params["t"] = tickers
    key = f"scr:{view}:{filters}:{columns}:{tickers}"
    txt = _cached(key, lambda: _fetch("export/screener", params))
    if not txt or txt.lstrip().startswith("<"):       # HTML = auth/path error, not CSV
        return []
    try:
        return list(csv.DictReader(io.StringIO(txt)))
    except Exception as e:
        print(f"[finviz] screener parse: {e}")
        return []


# ── DARK MATTER (D): SEC Form-4 insider transactions ────────────────────────────────────────
_INSIDER_COLS = ["ticker", "owner", "relationship", "date", "transaction",
                 "cost", "shares", "value_usd", "shares_total", "filed"]


#: The ticker cell renders a one-letter logo-FALLBACK INITIAL before the ticker text, so
#: naive tag-stripping concatenates them ("L" + "LEVI" -> "LLEVI"). The real ticker is
#: carried unambiguously in the logo URL and the img alt, so prefer those.
_LOGO_TICKER = re.compile(r"logo\.finviz\.com/([A-Z][A-Z0-9.\-]{0,9})\.svg", re.I)
_ALT_TICKER = re.compile(r'alt="([A-Z][A-Z0-9.\-]{0,9})\s+logo"', re.I)
#: A Finviz filing timestamp, e.g. 'Jul 24 09:42 PM'. Used to detect column misalignment.
_TS_LIKE = re.compile(r"^[A-Z][a-z]{2}\s+\d{1,2}\s+\d{1,2}:\d{2}\s*(AM|PM)$")


#: Serialization flag for the parser correctness fix (2026-07-25).
#: The fix takes the primary insider source from "returns nothing" to "returns real data",
#: which moves `positioning_concentration` — the component inside the R7 baseline transient.
#: Two score-affecting changes landing together would make neither attributable, so it flips
#: explicitly, with before/after capture (the R7 pattern) and instant rollback.
#:
#: ⚠ DEFAULT IS "0" (corrected by the Board accountability review). It previously defaulted
#: to "1" while production held it OFF via an unversioned Heroku config var — so the OFF
#: state existed on exactly one server, and every other context (fresh dyno, review app,
#: local run, anything under tools/) silently got the changed behaviour. Four archetypes
#: flagged it independently; the Outsider's phrasing was "a flag that is ON everywhere
#: except one server." Code must equal intent, so the safe state is the default and the
#: change is opt-in.
#: NOTE: the Form-144 classification fix (`classify_transaction`) is deliberately NOT gated —
#: counting a notice of intent as an executed sale is wrong on both branches.
INSIDER_PARSER_FIX = os.getenv("INSIDER_PARSER_FIX", "0") == "1"


def _ticker_from_cell(raw_cell: str, stripped: str) -> str:
    """Recover the true ticker from a Finviz ticker cell.

    ⚠ LIVE DEFECT FIXED 2026-07-25 (§16 gate-5 sweep, Phase 2). Every ticker parsed from
    this feed had its FIRST LETTER DOUBLED — verified on live data: 111 of 111 distinct
    tickers (LEVI->LLEVI, NOC->NNOC, AAPL->AAAPL). Because `insider_signal()` filters rows
    with `row["ticker"].upper() != only`, that filter NEVER MATCHED and the function
    returned ZERO ROWS FOR EVERY TICKER — silently, as `available: False` rather than an
    error anyone would notice. Finviz is the PRIMARY insider source (CLAUDE.md §15), so the
    primary Dark-Matter insider input has been inert.

    Order of preference:
      1. the logo URL (logo.finviz.com/LEVI.svg) — unambiguous
      2. the img alt  (alt="LEVI logo")          — unambiguous
      3. de-duplicating the leading fallback initial — AMBIGUOUS by construction ("AAA" is
         either Alcoa "AA" behind an "A" initial, or a genuine "AAA"), so it is a last
         resort and never overrides 1 or 2.
    """
    m = _LOGO_TICKER.search(raw_cell or "") or _ALT_TICKER.search(raw_cell or "")
    if m:
        return m.group(1).upper()
    s = (stripped or "").strip()
    # ⚠ NAV-BAR GUARD (found 2026-07-27 during post-flip verification). The page's navigation
    # row ("Home | News | Screener | Charts | Maps | Groups | Portfolio | Insider") carries
    # enough cells to survive the >=9-cell test, and this fallback UPPERCASED "Home" into a
    # ticker-shaped "HOME" that passed the ticker regex — one junk row per fetch, wearing a
    # real ticker's shape. A genuine ticker cell renders ALREADY UPPERCASE; title-case text is
    # chrome, never an instrument. (The row was refused downstream by the ingest gates on an
    # unclassifiable transaction, so nothing entered the append-only panel — but it inflated
    # the parsed-row and distinct-ticker counts that the liveness tripwire reads.)
    if s and s != s.upper():
        return ""
    s = s.upper()
    if len(s) >= 2 and s[0] == s[1]:
        return s[1:]
    return s


def _parse_insider(html: str, only_ticker: str = "") -> list:
    """Extract Form-4 rows from an insidertrading.ashx page. Each data row is 10 cells:
    Ticker, Owner, Relationship, Date, Transaction, Cost, #Shares, Value($), #Shares Total,
    SEC Form 4.

    ⚠ Rows whose columns MISALIGN are dropped rather than returned. Form 144 "Proposed Sale"
    entries carry a different cell count, so dropping empty cells and zipping shifted every
    field left (observed live: `shares_total` holding a timestamp, `filed` empty). A shifted
    row yields plausible-looking WRONG numbers, which is worse than no row at all.
    """
    out = []
    only = only_ticker.upper().strip()
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        raw_cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
        stripped = [re.sub(r"<[^>]+>", "", c).strip() for c in raw_cells]
        keep = [(rc, c) for rc, c in zip(raw_cells, stripped) if c != ""]
        if len(keep) < 9:
            continue                                  # skip nav / non-data rows
        texts = [c for _, c in keep]

        if not INSIDER_PARSER_FIX:
            # LEGACY path, retained ONLY so the fix can ship inert while the R7 transient
            # resolves. It parses the ticker with its first letter doubled (LEVI->LLEVI),
            # so `only_ticker` never matches and per-ticker reads return zero rows. Do not
            # "clean this up" — deleting it removes the ability to serialize the rollout.
            if not re.match(r"^[A-Z]{1,5}$", texts[0]):
                continue
            row = dict(zip(_INSIDER_COLS, texts[:10]))
            if only and row["ticker"].upper() != only:
                continue
            out.append(row)
            continue

        tkr = _ticker_from_cell(keep[0][0], texts[0])
        if not re.match(r"^[A-Z][A-Z0-9.\-]{0,9}$", tkr):
            continue
        row = dict(zip(_INSIDER_COLS, texts[:10]))
        row["ticker"] = tkr
        # Alignment check: `filed` must carry a timestamp and `shares_total` must not.
        # Either condition failing means the columns shifted for this row.
        if _TS_LIKE.match((row.get("shares_total") or "").strip()):
            continue
        if not (row.get("filed") or "").strip():
            continue
        if only and row["ticker"].upper() != only:
            continue
        out.append(row)
    return out


#: CANONICAL transaction classification — the single source of truth for this feed.
#: EXACT match, never substring. Substring matching is what let "Proposed Sale" be counted
#: as an executed sale, because it contains "sale".
_TXN_CLASS = {
    "buy": "P", "purchase": "P",          # open-market purchase — the conviction signal
    "sale": "S", "sell": "S",             # open-market sale (executed)
    "option exercise": "M",               # derivative exercise — compensation, not movement
    "proposed sale": "F144",              # Form 144 NOTICE OF INTENT — not an executed trade
    "gift": "G", "award": "A",
}


def classify_transaction(raw: str) -> str:
    """Feed transaction string -> Form-4-style code. Unknown strings return 'UNKNOWN' and
    are counted, never bucketed as a sale — an unrecognised string is parser drift, not a
    trade. Live sample (2026-07-25): Sale 86, Proposed Sale 53, Option Exercise 38, Buy 23."""
    return _TXN_CLASS.get((raw or "").strip().lower(), "UNKNOWN")


def insider_feed(limit: int = 500) -> list:
    """Market-wide recent insider Form-4 transactions (all tickers), newest first.

    One call. NOTE the SOURCE caps at ~200 rows (verified: asking 500 returned 200 across
    111 tickers), so a heavy filing day truncates — and the dropped rows are exactly the
    cluster events an insider observable most wants. Callers should record a coverage
    watermark; see insider_flow.ingest.
    """
    global _LAST_FEED_RAW_ROWS
    html = _cached("insider:feed", lambda: _fetch("insidertrading.ashx", {}))
    # Count the RAW data rows the source returned, before parsing drops misaligned ones.
    # Truncation must be judged on what the SOURCE sent, not on what survived parsing —
    # otherwise dropping 52 malformed rows makes a capped day look uncapped.
    _LAST_FEED_RAW_ROWS = len([1 for r in re.findall(r"<tr[^>]*>(.*?)</tr>", html or "", re.S)
                               if len(re.findall(r"<td[^>]*>", r)) >= 9])
    rows = _parse_insider(html or "")
    # ⚠ S2 (Board 2026-07-28) — SOURCE liveness, recorded at the one place that sees the raw
    # source. This feed was DEAD for up to 30 days and nothing alarmed, because every watchdog
    # asked whether our PROCESS ran, not whether the SOURCE returned usable data. Logged here
    # rather than at a caller so it is observed regardless of INSIDER_FLOW — the earlier
    # tripwire lived behind that flag and therefore watched nothing while the flag was off.
    # Fires only on a real fetch (the result is 1h-cached), and never breaks the read path.
    try:
        import collector_health as _ch
        _tk = len({(r.get("ticker") or "").upper() for r in rows if r.get("ticker")})
        _ch.log_collector_run("finviz_insider", len(rows),
                              "success" if rows else "failure", distinct_keys=_tk)
    except Exception:
        pass
    return rows[:limit]


#: Raw data-row count from the most recent insider_feed() call (see the truncation note).
_LAST_FEED_RAW_ROWS = 0


def last_feed_raw_rows() -> int:
    """Raw data rows the source returned on the last insider_feed() call, pre-parse."""
    return _LAST_FEED_RAW_ROWS


def _parse_finviz_date(s: str) -> Optional[str]:
    """'Jun 23 \\'26' → ISO 'YYYY-MM-DD' (held-out local parse; integration routes through date_utils §14)."""
    s = (s or "").replace("'", "").strip()
    for fmt in ("%b %d %y", "%b %d %Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def insider_signal(ticker: str, name: str = "") -> dict:
    """Per-ticker net insider money movement over the window — open-market conviction trades only
    (Buy/Sale ≥ $250K; option exercises / gifts excluded). SAME shape as av_dark_positioning.insider_signal
    so Finviz can be the PRIMARY insider source with AV as fallback."""
    tkr = ticker.upper().strip()
    html = _cached(f"insider:{tkr}", lambda: _fetch("insidertrading.ashx", {"t": tkr}))
    rows = _parse_insider(html or "", only_ticker=tkr)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=INSIDER_WINDOW_DAYS)).date().isoformat()
    buy_usd = sell_usd = 0.0
    buy_n = sell_n = 0
    skipped = {"F144": 0, "M": 0, "UNKNOWN": 0}
    for r in rows:
        # CANONICAL classification (2026-07-25). Previously a substring test over
        # _BUY/_SELL, which counted Form 144 "Proposed Sale" — a NOTICE OF INTENT, 26.5% of
        # the live feed — as an executed insider sale, because the string contains "sale".
        # That fed `flow`, and `flow` is what the market accuracy ledger ENROLLS ON.
        code = classify_transaction(r.get("transaction"))
        iso = _parse_finviz_date(r.get("date"))
        if iso and iso < cutoff:
            continue
        val = _num(r.get("value_usd"))
        if not val or val < MIN_USD:
            continue
        if code == "P":
            buy_usd += val; buy_n += 1
        elif code == "S":
            sell_usd += val; sell_n += 1
        elif code in skipped:
            skipped[code] += 1
    net = buy_usd - sell_usd
    flow = "inflow" if net > MIN_USD else "outflow" if net < -MIN_USD else "neutral"
    # Interpreted Dark-Matter read: insider BUYING is the rare, high-conviction signal. Routine net
    # selling is structurally dominant (stock comp / diversification / 10b5-1) and low-information, so
    # it is NOT treated as bearish — only material BUYING flags accumulation. (Unusual-selling-vs-
    # baseline detection is a future enhancement.) `flow`/`net_usd` are kept as factual context.
    signal = "accumulation" if buy_usd >= MIN_USD else "neutral"
    return {"available": bool(rows), "source": "finviz", "window_days": INSIDER_WINDOW_DAYS,
            "buy_usd": round(buy_usd), "sell_usd": round(sell_usd), "net_usd": round(net),
            "buys": buy_n, "sells": sell_n, "flow": flow, "signal": signal,
            "rows_seen": len(rows),
            # What we REFUSED is part of the record, not an implementation detail.
            "excluded": {"form144_intent": skipped["F144"], "option_exercise": skipped["M"],
                         "unrecognised": skipped["UNKNOWN"]}}


if __name__ == "__main__":
    import sys, json
    print("available:", available())
    if "--feed" in sys.argv:
        feed = insider_feed(limit=12)
        print(f"\nMARKET-WIDE INSIDER FEED ({len(feed)} shown):")
        for r in feed:
            print(f"  {r['ticker']:5} {r['transaction']:16} ${r['value_usd']:>14} "
                  f"{r['date']:12} {r['relationship'][:28]:28} {r['owner'][:24]}")
    tks = [a for a in sys.argv[1:] if not a.startswith("--")] or ["MSTR", "COIN", "NVDA"]
    print("\nPER-TICKER INSIDER SIGNAL:")
    for t in tks:
        s = insider_signal(t)
        print(f"  {t:5} flow={s['flow']:8} net=${s['net_usd']:>14,.0f} "
              f"({s['buys']}b/{s['sells']}s, {s['rows_seen']} rows)")
