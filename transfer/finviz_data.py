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


def _parse_insider(html: str, only_ticker: str = "") -> list:
    """Extract Form-4 rows from an insidertrading.ashx page. Each data row is 10 cells:
    Ticker, Owner, Relationship, Date, Transaction, Cost, #Shares, Value($), #Shares Total, SEC Form 4."""
    out = []
    only = only_ticker.upper().strip()
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        cells = [c for c in cells if c != ""]
        if len(cells) < 9 or not re.match(r"^[A-Z]{1,5}$", cells[0]):
            continue                                  # skip nav / non-data rows
        row = dict(zip(_INSIDER_COLS, cells[:10]))
        if only and row["ticker"].upper() != only:
            continue
        out.append(row)
    return out


def insider_feed(limit: int = 100) -> list:
    """Market-wide recent insider Form-4 transactions (all tickers), newest first. One call, no cap."""
    html = _cached("insider:feed", lambda: _fetch("insidertrading.ashx", {}))
    rows = _parse_insider(html or "")
    return rows[:limit]


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
    for r in rows:
        kind = (r.get("transaction") or "").lower()
        iso = _parse_finviz_date(r.get("date"))
        if iso and iso < cutoff:
            continue
        val = _num(r.get("value_usd"))
        if not val or val < MIN_USD:
            continue
        if any(k in kind for k in _BUY):
            buy_usd += val; buy_n += 1
        elif any(k in kind for k in _SELL):
            sell_usd += val; sell_n += 1
    net = buy_usd - sell_usd
    flow = "inflow" if net > MIN_USD else "outflow" if net < -MIN_USD else "neutral"
    # Interpreted Dark-Matter read: insider BUYING is the rare, high-conviction signal. Routine net
    # selling is structurally dominant (stock comp / diversification / 10b5-1) and low-information, so
    # it is NOT treated as bearish — only material BUYING flags accumulation. (Unusual-selling-vs-
    # baseline detection is a future enhancement.) `flow`/`net_usd` are kept as factual context.
    signal = "accumulation" if buy_usd >= MIN_USD else "neutral"
    return {"available": bool(rows), "source": "finviz", "window_days": INSIDER_WINDOW_DAYS,
            "buy_usd": round(buy_usd), "sell_usd": round(sell_usd), "net_usd": round(net),
            "buys": buy_n, "sells": sell_n, "flow": flow, "signal": signal, "rows_seen": len(rows)}


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
