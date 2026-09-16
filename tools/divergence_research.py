#!/usr/bin/env python3
"""
tools/divergence_research.py — READ-ONLY divergence research runner.

Implements items 2, 3, 4 and 6 of the Chairman's divergence order
(`audits/board/BOARD_divergence_2026-09-14.md`, convergent next steps), under the
SEALED pre-registration `audits/board/DIVERGENCE_PREREG_2026-09-14.md`:

  Section 0 — SEAL CHECK: sha256(prereg) must equal divergence.PARAM_VERSION
              (the sibling core module `transfer/divergence.py`). Exit 1 on mismatch.
  Section 1 — COT BACKFILL (item 3, grade-A leg): CFTC Socrata TFF futures-only,
              CME BITCOIN + ETHER contracts, full history, knowable_at = report
              Tuesday + 3 days. -> COT_CME_BTC.csv / COT_CME_ETH.csv
  Section 2 — INSTRUMENT AUDITS (item 2; prereg SS5 exemption: audits test the
              thermometer, not the forecast, and may use pre-seal spec-development
              rows): (a) K8/K12 missingness-vs-|return|, (b) K12 timing jitter from
              stored stamps, (c) Operator cross-leg rho (funding_z vs dlnOI_z, raw
              and momentum-orthogonalized; plus COT weekly cross if Section 1 ran).
  Section 3 — RESIDUAL PREVIEW (item 4): the SS2 D series for all 12 coins on
              research prices. SPEC-DEVELOPMENT DATA (K16) — instrument preview
              only, never scored. NO outcome/ledger/forward join anywhere (SS8).
  Section 4 — EQUITY-FIRST (item 6, Chairman-ruled GO): the same SS2 residual at
              SS7 cadence on FINRA short interest vs FMP/stooq prices, per
              WATCHLIST_TICKERS. Research-only.

HARD CONTRACT (prereg SS8):
  * SELECT-only against the database — asserted at import time over every SQL
    string this module owns; the connection itself is opened READ-ONLY.
  * No forward-looking join: no query touches any outcome, ledger, or
    subsequent-return column; price/return joins are contemporaneous or backward.
  * The SS2 core statistic is NOT reimplemented here — it is imported from the
    sibling module `transfer/divergence.py` and its functions are used via a thin
    signature-tolerant adapter. This file only orchestrates, fetches public data,
    and writes research CSV/JSON to OUT_DIR.

Degradation: every section that cannot run (missing table/env/API blocked) prints
a clear SKIPPED reason and the run continues. Exit code is 0 unless the SEAL
CHECK fails.

Env: DATABASE_URL (Heroku PG, used read-only; unset -> DB sections skip),
     OUT_DIR (default audits/divergence), FINRA_API_KEY (equity leg),
     COINGECKO_PAUSE_S (default 15), FMP_API_KEY (primary equity research price).

Research-only labeling: CoinGecko dailies and stooq EOD closes are RESEARCH
PRICES, not the sealed price source; nothing here is scored, served, or enrolled.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# --------------------------------------------------------------------------- paths
REPO = Path(__file__).resolve().parent.parent
TRANSFER_DIR = REPO / "transfer"  # fixed — the sealed core loads from here only
PREREG_PATH = REPO / "audits" / "board" / "DIVERGENCE_PREREG_2026-09-14.md"
OUT_DIR = Path(os.getenv("OUT_DIR", str(REPO / "audits" / "divergence")))

if str(TRANSFER_DIR) not in sys.path:
    sys.path.insert(0, str(TRANSFER_DIR))

COINGECKO_IDS = {  # roster order = coinapi_derivs.PERP_SYMBOLS roster (12 coins)
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "XRP": "ripple",
    "BNB": "binancecoin", "DOGE": "dogecoin", "ADA": "cardano",
    "AVAX": "avalanche-2", "LINK": "chainlink", "DOT": "polkadot",
    "LTC": "litecoin", "BCH": "bitcoin-cash",
}
CG_PAUSE_S = float(os.getenv("COINGECKO_PAUSE_S", "15"))
CG_RETRY_S = float(os.getenv("COINGECKO_RETRY_S", "65"))  # public 429 window
RESEARCH_PRICE_CAVEAT = ("CoinGecko/FMP/stooq dailies are RESEARCH-ONLY prices, "
                         "not the sealed price source.")

# ------------------------------------------------------------------ SQL (SELECT only)
SQL = {
    "cols": ("SELECT column_name FROM information_schema.columns "
             "WHERE table_name = 'coinapi_derivs'"),
    # {cols} is filled from the discovered column list — never user input.
    "derivs": "SELECT {cols} FROM coinapi_derivs ORDER BY coin, signal_date",
}
_FORBIDDEN_SQL = ("insert", "update", "delete", "drop", "alter", "truncate",
                  "create", "grant", "copy", "merge")


def _assert_select_only() -> None:
    """SS8 contract: every SQL string this module owns is a bare SELECT."""
    for name, q in SQL.items():
        ql = q.strip().lower()
        if not ql.startswith("select"):
            raise AssertionError(f"SQL '{name}' is not SELECT-only")
        toks = set(re.findall(r"[a-z_]+", ql))
        bad = toks & set(_FORBIDDEN_SQL)
        if bad:
            raise AssertionError(f"SQL '{name}' contains forbidden verb(s): {bad}")


_assert_select_only()

# --------------------------------------------------------------------- tiny stats
# (Generic descriptive statistics only. The SS2 sealed statistic — robust z,
#  Theil–Sen, the D residual — is NEVER computed here; it comes from the core.)

def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def _median(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def _var(xs):
    if len(xs) < 2:
        return None
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def _welch_t(a, b):
    """Two-sample Welch t statistic (a vs b); None when undefined."""
    if len(a) < 2 or len(b) < 2:
        return None
    va, vb = _var(a), _var(b)
    denom = math.sqrt(va / len(a) + vb / len(b))
    if denom == 0:
        return None
    return (_mean(a) - _mean(b)) / denom


def _rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = _mean(x), _mean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def _spearman(x, y):
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 3:
        return None, len(pairs)
    xs, ys = zip(*pairs)
    return _pearson(_rank(list(xs)), _rank(list(ys))), len(pairs)


def _r(x, nd=4):
    return None if x is None else round(x, nd)


# ----------------------------------------------------------------------- HTTP
def _http_get(url: str, timeout: int = 60, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, headers=dict({"User-Agent":
        "nowtrendin-divergence-research/1.0 (read-only research; SS8 sealed)"},
        **(headers or {})))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        # Self-diagnosing failures (2026-09-14 first run: a bare "HTTP 400"
        # from Socrata left the cause untraceable from the sandbox) — attach
        # the response body so the run's own output IS the diagnosis.
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")[:300]
        except Exception:  # noqa: BLE001
            pass
        raise urllib.error.HTTPError(
            e.url, e.code, f"{e.reason} — body: {body!r}", e.headers, None
        ) from None


# ------------------------------------------------------- core module + adapter
class CoreUnavailable(RuntimeError):
    pass


def _import_core():
    try:
        import divergence  # transfer/divergence.py — the sealed SS2 core
        return divergence, None
    except Exception as e:  # noqa: BLE001 — report, don't crash
        return None, f"{type(e).__name__}: {e}"


class CoreAdapter:
    """Thin wrapper over transfer/divergence.py — the sealed SS2 core.

    Uses the core's own functions directly and NEVER reimplements the sealed
    arithmetic: `robust_z(window, x)` (point-wise, median/MAD, honest-absence on
    MAD==0), `theil_sen(xs, ys) -> (alpha, beta)`, `divergence_series(dates,
    q_raw, p_raw, ...)` (the full SS2 residual over raw LEVEL series, strict
    full-window warm-up = honest absence), and `equity_divergence(...)` (the SS7
    cadence-scaled instantiation). A synthetic self-check at construction guards
    against signature drift in the parallel build; a failed check raises
    CoreUnavailable and every core-dependent section SKIPs with the reason.
    """

    REQUIRED = ("robust_z", "theil_sen", "divergence_series")

    def __init__(self, mod):
        self.mod = mod
        self.notes = []
        missing = [n for n in self.REQUIRED if not callable(getattr(mod, n, None))]
        if missing:
            raise CoreUnavailable(f"core lacks required function(s): {missing}")
        a, b = mod.theil_sen([float(i) for i in range(12)],
                             [5.0 + 2.0 * i for i in range(12)])
        if a is None or b is None or abs(a - 5.0) > 1e-6 or abs(b - 2.0) > 1e-6:
            raise CoreUnavailable(
                f"core theil_sen failed synthetic check y=5+2x -> ({a}, {b})")
        self.notes.append("core self-check OK: theil_sen(xs, ys) -> (alpha, beta)")

    # ---- audit-scale robust z (SS5 instrument-audit exemption) ----
    def z_audit(self, vals, window=90, min_obs=10):
        """Trailing robust z built from core robust_z arithmetic, TOLERANT of
        gaps and short history (>= min_obs non-None values in the window).
        Instrument-audit tooling only (prereg SS5 exemption: audits test the
        thermometer) — NOT the sealed strict-90 statistic; divergence_series
        computes that one."""
        out = []
        for i, x in enumerate(vals):
            if x is None:
                out.append(None)
                continue
            win = [v for v in vals[max(0, i - window + 1):i + 1] if v is not None]
            out.append(self.mod.robust_z(win, x) if len(win) >= min_obs else None)
        return out

    def fit(self, xs, ys):
        a, b = self.mod.theil_sen(xs, ys)
        if a is None or b is None:
            raise CoreUnavailable("core theil_sen returned (None, None) "
                                  "(no informative pair)")
        return a, b

    def orthogonalize(self, series, momentum):
        """Residual of series after a core Theil–Sen fit on momentum (Operator 2c)."""
        pairs = [(m, s) for m, s in zip(momentum, series)
                 if m is not None and s is not None]
        if len(pairs) < 5:
            return [None] * len(series)
        try:
            a, b = self.fit([m for m, _ in pairs], [s for _, s in pairs])
        except CoreUnavailable:
            return [None] * len(series)
        return [None if (s is None or m is None) else s - (a + b * m)
                for s, m in zip(series, momentum)]


# ------------------------------------------------------------------- utilities
def _out(name: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR / name


def _write_csv(path: Path, header: list, rows: list, comment: str | None = None):
    with open(path, "w", newline="", encoding="utf-8") as f:
        if comment:
            f.write(comment.rstrip("\n") + "\n")
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def _write_json(path: Path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)


def _banner(title: str):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def _skip(section: str, reason: str) -> dict:
    print(f"[{section}] SKIPPED — {reason}")
    return {"status": "SKIPPED", "reason": reason}


def _daterange(d0: date, d1: date):
    d = d0
    while d <= d1:
        yield d
        d += timedelta(days=1)


def _iso(d) -> date | None:
    try:
        return date.fromisoformat(str(d)[:10])
    except (TypeError, ValueError):
        return None


def _dln_7d(by_date: dict, dates: list) -> dict:
    """7-calendar-day Δln of a positive series keyed by date (SS2 window)."""
    out = {}
    for d in dates:
        v1 = by_date.get(d)
        v0 = by_date.get(d - timedelta(days=7))
        if v1 and v0 and v1 > 0 and v0 > 0:
            out[d] = math.log(v1 / v0)
    return out


# =========================================================== SECTION 0 — SEAL
def section0_seal(core_mod, core_err) -> dict:
    _banner("SECTION 0 — SEAL CHECK (prereg sha256 vs divergence.PARAM_VERSION)")
    if not PREREG_PATH.exists():
        print(f"SEAL CHECK FAILED: prereg file missing at {PREREG_PATH}")
        return {"status": "FAILED", "reason": "prereg file missing"}
    sha = hashlib.sha256(PREREG_PATH.read_bytes()).hexdigest()
    print(f"prereg sha256      = {sha}")
    if core_mod is None:
        print(f"SEAL CHECK FAILED: core module transfer/divergence.py not importable "
              f"({core_err}) — PARAM_VERSION cannot be verified.")
        return {"status": "FAILED", "reason": f"core import failed: {core_err}",
                "prereg_sha256": sha}
    pv = getattr(core_mod, "PARAM_VERSION", None)
    print(f"core PARAM_VERSION = {pv}")
    if pv != sha:
        print("SEAL CHECK FAILED: PARAM_VERSION != sha256(prereg). "
              "A sealed-section edit mints a NEW param_version — quiet retuning "
              "is the forbidden path (prereg preamble). Refusing to run.")
        return {"status": "FAILED", "reason": "param_version mismatch",
                "prereg_sha256": sha, "param_version": pv}
    print("SEAL CHECK OK.")
    return {"status": "OK", "param_version": sha}


# ===================================================== SECTION 1 — COT BACKFILL
# Run 2 (2026-09-14) self-diagnosed the 400: resource 6dca-aqww is the LEGACY
# COT schema (market_and_exchange_names, no lev_money_* columns). The
# leveraged-funds fields live in the TFF datasets, so instead of hardcoding a
# dataset id, probe one row per candidate and keep the first whose schema
# carries a market-name column AND the lev_money long/short pair.
COT_CANDIDATE_DATASETS = ["gpe5-46if", "6dca-aqww"]  # TFF futures-only first
COT_NAME_COLS = ("contract_market_name", "market_and_exchange_names")
COT_FIELDS = ["report_date_as_yyyy_mm_dd", "contract_market_name",
              "open_interest_all", "lev_money_positions_long_all",
              "lev_money_positions_short_all", "asset_mgr_positions_long_all",
              "asset_mgr_positions_short_all"]


def _cot_resolve_dataset() -> tuple:
    """(base_url, name_col, field_map) from a 1-row schema probe, or raises
    with every candidate's reason so the run output is the diagnosis."""
    reasons = []
    for ds in COT_CANDIDATE_DATASETS:
        base = f"https://publicreporting.cftc.gov/resource/{ds}.json"
        try:
            probe = json.loads(_http_get(f"{base}?$limit=1", timeout=60)
                               .decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            reasons.append(f"{ds}: probe failed: {e}")
            continue
        keys = set(probe[0].keys()) if probe else set()
        name_col = next((c for c in COT_NAME_COLS if c in keys), None)

        def _match(want):
            if want in keys:
                return want
            stem = want[:-len("_all")] if want.endswith("_all") else want
            return next((k for k in sorted(keys) if k.startswith(stem)), None)

        fmap = {f: (name_col if f == "contract_market_name" else _match(f))
                for f in COT_FIELDS}
        missing = [f for f, k in fmap.items() if k is None]
        if name_col and not any("lev_money" in f for f in missing):
            return base, name_col, fmap
        reasons.append(f"{ds}: schema lacks {missing or 'a market-name column'}")
    raise RuntimeError("no COT dataset matched: " + "; ".join(reasons))


def _cot_fetch(needle: str) -> list:
    base, name_col, fmap = _cot_resolve_dataset()
    select_fields = sorted({k for k in fmap.values() if k})
    rows, offset, limit = [], 0, 5000
    while True:
        qs = urllib.parse.urlencode({
            "$select": ",".join(select_fields),
            "$where": f"upper({name_col}) like '%{needle}%'",
            "$order": fmap["report_date_as_yyyy_mm_dd"],
            "$limit": str(limit), "$offset": str(offset),
        })
        page = json.loads(_http_get(f"{base}?{qs}", timeout=90).decode("utf-8"))
        for r0 in page:
            for want, have in fmap.items():
                if have and have != want:
                    r0[want] = r0.get(have, "")
        rows.extend(page)
        if len(page) < limit:
            return rows
        offset += limit


def section1_cot() -> dict:
    _banner("SECTION 1 — COT BACKFILL (CFTC TFF futures-only, CME BITCOIN/ETHER)")
    summary = {"status": "OK", "files": {}}
    for coin, needle in (("BTC", "BITCOIN"), ("ETH", "ETHER")):
        try:
            raw = _cot_fetch(needle)
        except Exception as e:  # noqa: BLE001 — proxy/API down must degrade
            summary["files"][coin] = {"status": "SKIPPED",
                                      "reason": f"CFTC fetch failed: {e}"}
            print(f"[cot:{coin}] SKIPPED — CFTC Socrata fetch failed: {e}")
            summary["status"] = "PARTIAL"
            continue
        out_rows = []
        for r0 in raw:
            rd = _iso(r0.get("report_date_as_yyyy_mm_dd"))
            if rd is None:
                continue
            lng = r0.get("lev_money_positions_long_all")
            sht = r0.get("lev_money_positions_short_all")
            try:
                lev_net = float(lng) - float(sht)
            except (TypeError, ValueError):
                lev_net = ""
            out_rows.append([
                rd.isoformat(), r0.get("contract_market_name", ""),
                r0.get("open_interest_all", ""), lng or "", sht or "",
                r0.get("asset_mgr_positions_long_all", ""),
                r0.get("asset_mgr_positions_short_all", ""), lev_net,
                (rd + timedelta(days=3)).isoformat(),  # knowable_at (Tue + 3d = Fri)
            ])
        out_rows.sort(key=lambda r: (r[0], r[1]))
        path = _out(f"COT_CME_{coin}.csv")
        _write_csv(path, ["report_date", "contract_market_name", "open_interest_all",
                          "lev_money_long", "lev_money_short", "asset_mgr_long",
                          "asset_mgr_short", "lev_money_net", "knowable_at"],
                   out_rows,
                   comment="# CFTC public record (grade-A leg, board 2026-09-14); "
                           "knowable_at = report Tuesday + 3 days (point-in-time rule).")
        info = {"status": "OK", "rows": len(out_rows),
                "date_range": [out_rows[0][0], out_rows[-1][0]] if out_rows else None}
        summary["files"][coin] = info
        print(f"[cot:{coin}] {len(out_rows)} rows -> {path.name} "
              f"(range {info['date_range']})")
    if all(v.get("status") == "SKIPPED" for v in summary["files"].values()):
        summary["status"] = "SKIPPED"
    _write_json(_out("cot_summary.json"), summary)
    return summary


# =================================================== DB LOAD (coinapi_derivs)
def _connect_db():
    dsn = os.getenv("DATABASE_URL", "").strip()
    if not dsn:
        return None, "DATABASE_URL unset"
    try:
        import psycopg2
    except ImportError:
        return None, "psycopg2 not installed"
    try:
        conn = psycopg2.connect(dsn, sslmode="require")
        conn.set_session(readonly=True, autocommit=True)  # hard read-only session
        return conn, None
    except Exception as e:  # noqa: BLE001
        return None, f"connect failed: {e}"


def load_derivs(conn):
    """All coinapi_derivs rows as dicts, tolerating absent late-added columns."""
    with conn.cursor() as cur:
        cur.execute(SQL["cols"])
        have = {r[0] for r in cur.fetchall()}
    if not have:
        raise LookupError("table coinapi_derivs not found")
    want = ["coin", "signal_date", "funding_rate", "open_interest",
            "signal_time", "captured_at", "units", "suspect"]
    cols = [c for c in want if c in have]
    missing = [c for c in want if c not in have]
    with conn.cursor() as cur:
        cur.execute(SQL["derivs"].format(cols=", ".join(cols)))
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return rows, cols, missing


# =================================================== RESEARCH PRICES (cached)
def _price_cache_load(path: Path) -> dict:
    out = {}
    if not path.exists():
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or line.startswith("coin,"):
                continue
            parts = line.strip().split(",")
            if len(parts) != 3:
                continue
            coin, d, px = parts
            dd = _iso(d)
            if dd is None:
                continue
            try:
                out.setdefault(coin, {})[dd] = float(px)
            except ValueError:
                continue
    return out


def fetch_research_prices(coins: list) -> tuple:
    """coin -> {date: close}; CoinGecko daily, cached. Returns (prices, errors)."""
    cache_path = _out("prices_coingecko.csv")
    prices = _price_cache_load(cache_path)
    errors = {}
    to_fetch = [c for c in coins if c not in prices]
    for i, coin in enumerate(to_fetch):
        cid = COINGECKO_IDS.get(coin)
        if not cid:
            errors[coin] = "no CoinGecko id mapping"
            continue
        url = (f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart"
               f"?vs_currency=usd&days=60&interval=daily")
        try:
            # First run: 6 of 12 coins 429'd at 2.5s pacing (public CG limit
            # is ~5-15 req/min) — retry with a long backoff instead of losing
            # the leg; ETH was among the losses.
            data = None
            for attempt in range(3):
                try:
                    data = json.loads(_http_get(url, timeout=60).decode("utf-8"))
                    break
                except urllib.error.HTTPError as he:
                    if he.code != 429 or attempt == 2:
                        raise
                    time.sleep(CG_RETRY_S)
            series = {}
            for ms, px in data.get("prices", []):
                d = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).date()
                series[d] = float(px)  # last value per UTC date wins
            if series:
                prices[coin] = series
            else:
                errors[coin] = "empty price series"
        except Exception as e:  # noqa: BLE001
            errors[coin] = f"{type(e).__name__}: {e}"
        if i < len(to_fetch) - 1:
            time.sleep(CG_PAUSE_S)  # public-API pacing
    rows = [[c, d.isoformat(), px] for c in sorted(prices)
            for d, px in sorted(prices[c].items())]
    _write_csv(cache_path, ["coin", "date", "price_usd"], rows,
               comment=f"# RESEARCH-ONLY price cache — {RESEARCH_PRICE_CAVEAT}")
    return prices, errors


def _abs_returns(series: dict) -> dict:
    out = {}
    ds = sorted(series)
    for prev, cur in zip(ds, ds[1:]):
        if (cur - prev).days == 1 and series[prev] > 0 and series[cur] > 0:
            out[cur] = abs(math.log(series[cur] / series[prev]))
    return out


# ============================================ SECTION 2 — INSTRUMENT AUDITS
def section2_audits(rows, cols, missing_cols, prices, price_errors,
                    core, core_reason: str | None, cot_summary: dict) -> dict:
    _banner("SECTION 2 — INSTRUMENT AUDITS (K8/K12 missingness, K12 timing, "
            "Operator cross-leg rho)")
    print(f"prereg SS5 exemption applies: audits test the thermometer, not the "
          f"forecast — pre-seal spec-development rows included by design.")
    print(f"CAVEAT: {RESEARCH_PRICE_CAVEAT}")
    by_coin = {}
    for r0 in rows:
        d = _iso(r0.get("signal_date"))
        if d is not None:
            by_coin.setdefault(r0["coin"], {})[d] = r0
    summary = {"status": "OK", "coins": sorted(by_coin), "row_count": len(rows),
               "missing_columns": missing_cols, "price_errors": price_errors,
               "research_price_caveat": RESEARCH_PRICE_CAVEAT}

    # -- 2d RETROACTIVE UNIT BACKSCAN (board 2026-09-15 D10, Chairman-ruled) ---
    # The K14 unit guard only stamps rows written after deploy f60fad8, so the
    # earlier accrual has zero operational unit-guard history. Apply the SAME
    # >10x day-over-day OI discontinuity test to EVERY accrued row, read-only.
    # Chairman ruling (disagreement 2): pre-seal rows may serve as D-display
    # warm-up CONTEXT only if this backscan is clean; flagged spans are severed
    # from any baseline, exactly as a live suspect stamp would sever them.
    back_rows, back_flags = [], 0
    for coin in sorted(by_coin):
        days = sorted(by_coin[coin])
        prev = None
        for d in days:
            oi = by_coin[coin][d].get("open_interest")
            try:
                oi = float(oi) if oi is not None else None
            except (TypeError, ValueError):
                oi = None
            if oi is not None and prev is not None and prev > 0:
                if oi > 10 * prev or oi < prev / 10:
                    back_rows.append([coin, d.isoformat(), prev, oi,
                                      _r(oi / prev, 4)])
                    back_flags += 1
            if oi is not None:
                prev = oi
    _write_csv(_out("unit_backscan.csv"),
               ["coin", "signal_date", "prev_oi", "oi", "ratio"], back_rows,
               comment=("# D10 retroactive unit backscan — >10x day-over-day OI "
                        "discontinuities over ALL accrued rows (read-only; a flag "
                        "severs the span from any baseline)"))
    summary["unit_backscan"] = {
        "rows_scanned": sum(len(v) for v in by_coin.values()),
        "discontinuities_flagged": back_flags,
        "verdict": ("CLEAN — pre-seal rows usable as disclosed warm-up context "
                    "per the 2026-09-15 Chairman ruling" if back_flags == 0 else
                    "FLAGGED — listed spans are severed; see unit_backscan.csv"),
    }
    print(f"[2d backscan] {summary['unit_backscan']['rows_scanned']} rows, "
          f"{back_flags} discontinuity flag(s) — "
          f"{summary['unit_backscan']['verdict']}")

    # -- 2a missingness vs |return| ------------------------------------------
    miss_rows, pooled_miss, pooled_pres = [], [], []
    counts = {"missing_days": 0, "present_days": 0,
              "missing_with_ret": 0, "present_with_ret": 0}
    for coin in sorted(by_coin):
        days = sorted(by_coin[coin])
        rets = _abs_returns(prices.get(coin, {}))
        span = list(_daterange(days[0], days[-1]))
        miss_r, pres_r = [], []
        n_miss = 0
        for d in span:
            missing = d not in by_coin[coin]
            n_miss += missing
            ret = rets.get(d)
            if ret is None:
                continue
            (miss_r if missing else pres_r).append(ret)
        counts["missing_days"] += n_miss
        counts["present_days"] += len(span) - n_miss
        counts["missing_with_ret"] += len(miss_r)
        counts["present_with_ret"] += len(pres_r)
        pooled_miss.extend(miss_r)
        pooled_pres.extend(pres_r)
        miss_rows.append([coin, span[0].isoformat(), span[-1].isoformat(),
                          len(span), n_miss, len(miss_r), len(pres_r),
                          _r(_mean(miss_r)), _r(_mean(pres_r)),
                          _r(_welch_t(miss_r, pres_r))])
    t_pooled = _welch_t(pooled_miss, pooled_pres)
    miss_rows.append(["POOLED", "", "", counts["missing_days"] + counts["present_days"],
                      counts["missing_days"], len(pooled_miss), len(pooled_pres),
                      _r(_mean(pooled_miss)), _r(_mean(pooled_pres)), _r(t_pooled)])
    _write_csv(_out("missingness_audit.csv"),
               ["coin", "span_start", "span_end", "span_days", "missing_days",
                "n_missing_with_ret", "n_present_with_ret",
                "mean_absret_missing", "mean_absret_present", "welch_t"],
               miss_rows,
               comment="# K8/K12 missingness-vs-volatility instrument audit — "
                       "research prices; a significant t DISQUALIFIES the leg "
                       "until the collector is fixed (prereg SS5).")
    summary["missingness"] = {
        "counts": counts, "pooled_mean_absret_missing": _r(_mean(pooled_miss)),
        "pooled_mean_absret_present": _r(_mean(pooled_pres)),
        "pooled_welch_t": _r(t_pooled),
        "note": ("insufficient missing-day observations for a stable t"
                 if len(pooled_miss) < 5 else None)}
    print(f"[2a missingness] {counts['missing_days']} missing / "
          f"{counts['present_days']} present coin-days; pooled mean |ret| "
          f"missing={_r(_mean(pooled_miss))} vs present={_r(_mean(pooled_pres))}; "
          f"Welch t={_r(t_pooled)} -> missingness_audit.csv")

    # -- 2b timing jitter ----------------------------------------------------
    def _minutes(ts):
        try:
            hh, mm, ss = str(ts).split(":")
            return int(hh) * 60 + int(mm) + int(ss) / 60.0
        except (ValueError, AttributeError):
            return None

    timing_rows, delays, delay_rets = [], [], []
    delay_days = []  # day-cluster tracking: same-day rows co-move (Challenger R2, board 2026-09-15)
    for coin in sorted(by_coin):
        rets = _abs_returns(prices.get(coin, {}))
        mins = []
        for d, r0 in sorted(by_coin[coin].items()):
            m = _minutes(r0.get("signal_time"))
            if m is None:
                continue
            mins.append(m)
            ret = rets.get(d)
            if ret is not None:
                delays.append(m)      # minutes after 00:00 UTC (the 12:01AM cadence)
                delay_rets.append(ret)
                delay_days.append(d)
        if mins:
            timing_rows.append([coin, len(mins), _r(min(mins), 2),
                                _r(_median(mins), 2), _r(max(mins), 2),
                                _r(max(mins) - min(mins), 2)])
        else:
            timing_rows.append([coin, 0, "", "", "", ""])
    rho_delay, n_delay = _spearman(delays, delay_rets)
    # Effective N is DAY-CLUSTERS, not pooled pairs: coins sharing a day share the market
    # move, so pooled n overstates independence ~12x (n=432 -> n_eff~36; Challenger R2,
    # BOARD_24h-review_2026-09-15). Never cite pooled n without n_days_eff beside it.
    n_days_eff = len(set(delay_days))
    _write_csv(_out("timing_audit.csv"),
               ["coin", "n_stamped_rows", "min_minutes_after_utc_midnight",
                "median_minutes", "max_minutes", "spread_minutes"],
               timing_rows,
               comment="# K12 timing-jitter audit (stored signal_time stamps). "
                       "PARTIAL: the sealed 3-offset instrument-error test needs "
                       "future fixed-offset collection; this reports what stored "
                       "stamps show.")
    summary["timing"] = {"pooled_spearman_delay_vs_absret": _r(rho_delay),
                         "n_pairs": n_delay,
                         "n_days_eff": n_days_eff,
                         "n_caveat": "pooled pairs are pseudo-replicated across coins "
                                     "sharing a day; cite n_days_eff, never pooled n "
                                     "alone (Challenger R2, board 2026-09-15)",
                         "note": "full 3-offset test is future collection (SS5)"}
    print(f"[2b timing] per-coin stamp spread written; pooled Spearman("
          f"capture-delay, same-day |ret|) = {_r(rho_delay)} on n={n_delay} pairs "
          f"(n_eff={n_days_eff} day-clusters; pooled n is pseudo-replicated) "
          f"-> timing_audit.csv")

    # -- 2c cross-leg rho ----------------------------------------------------
    cross_rows = []
    pooled = {"fz": [], "qz": [], "fo": [], "qo": []}
    try:
        if core is None:
            raise CoreUnavailable(core_reason or "core module unavailable")
        for coin in sorted(by_coin):
            days = sorted(by_coin[coin])
            oi = {d: by_coin[coin][d].get("open_interest") for d in days
                  if by_coin[coin][d].get("open_interest")}
            fund = [by_coin[coin][d].get("funding_rate") for d in days]
            fund = [float(f) if f is not None else None for f in fund]
            q_map = _dln_7d({d: float(v) for d, v in oi.items()}, days)
            q = [q_map.get(d) for d in days]
            p_map = _dln_7d(prices.get(coin, {}), days)
            p = [p_map.get(d) for d in days]
            fz = core.z_audit(fund, 90)
            qz = core.z_audit(q, 90)
            pz = core.z_audit(p, 90)
            rho_raw, n_raw = _spearman(fz, qz)
            fo = core.orthogonalize(fz, pz)
            qo = core.orthogonalize(qz, pz)
            rho_orth, n_orth = _spearman(fo, qo)
            cross_rows.append([coin, n_raw, _r(rho_raw), n_orth, _r(rho_orth)])
            for k, s in (("fz", fz), ("qz", qz), ("fo", fo), ("qo", qo)):
                pooled[k].extend(s)
        rho_p_raw, n_p_raw = _spearman(pooled["fz"], pooled["qz"])
        rho_p_orth, n_p_orth = _spearman(pooled["fo"], pooled["qo"])
        cross_rows.append(["POOLED", n_p_raw, _r(rho_p_raw), n_p_orth, _r(rho_p_orth)])
        summary["cross_leg"] = {"pooled_rho_raw": _r(rho_p_raw),
                                "pooled_rho_orthogonalized": _r(rho_p_orth),
                                "n_raw": n_p_raw, "n_orth": n_p_orth}
        print(f"[2c cross-leg] pooled Spearman funding_z~dlnOI_z raw={_r(rho_p_raw)} "
              f"(n={n_p_raw}), momentum-orthogonalized={_r(rho_p_orth)} (n={n_p_orth})")
    except CoreUnavailable as e:
        summary["cross_leg"] = {"status": "SKIPPED", "reason": str(e)}
        print(f"[2c cross-leg] SKIPPED — core function unavailable: {e}")
    _write_csv(_out("cross_leg_rho.csv"),
               ["coin", "n_raw", "spearman_funding_z_vs_dlnOI_z",
                "n_orth", "spearman_after_momentum_orthogonalization"],
               cross_rows,
               comment="# Operator cross-leg audit — funding is a DISQUALIFIED "
                       "leg (price-derived, prereg SS2); this measures how much "
                       "of the OI leg it duplicates. Research prices. z is the "
                       "AUDIT-scale robust z (core arithmetic, gap-tolerant "
                       "window) — not the sealed strict-90 statistic.")

    # -- 2c-bis COT weekly cross (if section 1 produced files) ---------------
    cot_rows = []
    for coin in ("BTC", "ETH"):
        path = OUT_DIR / f"COT_CME_{coin}.csv"
        if core is None:
            cot_rows.append([coin, "", "", f"core unavailable: {core_reason}"])
            continue
        if not path.exists() or coin not in by_coin:
            cot_rows.append([coin, 0, "", "COT csv or coinapi rows unavailable"])
            continue
        try:
            weekly = {}
            with open(path, encoding="utf-8") as f:
                for r0 in csv.DictReader(l for l in f if not l.startswith("#")):
                    d = _iso(r0.get("report_date"))
                    try:
                        net = float(r0["lev_money_net"])
                    except (TypeError, ValueError, KeyError):
                        continue
                    if d:
                        weekly[d] = weekly.get(d, 0.0) + net  # sum across contracts
            wdates = sorted(weekly)
            dnet, dlnoi, used = [], [], []
            oi_days = {d: float(v["open_interest"]) for d, v in by_coin[coin].items()
                       if v.get("open_interest")}
            def _oi_at(dd):
                for back in range(0, 5):
                    v = oi_days.get(dd - timedelta(days=back))
                    if v and v > 0:
                        return v
                return None
            for prev, cur in zip(wdates, wdates[1:]):
                o1, o0 = _oi_at(cur), _oi_at(prev)
                if o1 and o0:
                    dnet.append(weekly[cur] - weekly[prev])
                    dlnoi.append(math.log(o1 / o0))
                    used.append(cur)
            if len(dnet) >= 3:
                znet = core.z_audit(dnet, 90, min_obs=3)
                zoi = core.z_audit(dlnoi, 90, min_obs=3)
                rho, n = _spearman(znet, zoi)
                cot_rows.append([coin, n, _r(rho),
                                 f"weeks {used[0]}..{used[-1]}"])
            else:
                cot_rows.append([coin, len(dnet), "",
                                 "too few overlapping COT/OI weeks"])
        except CoreUnavailable as e:
            cot_rows.append([coin, "", "", f"core unavailable: {e}"])
        except Exception as e:  # noqa: BLE001
            cot_rows.append([coin, "", "", f"error: {e}"])
    _write_csv(_out("cot_cross_leg.csv"),
               ["coin", "n_weeks", "spearman_dLevNet_z_vs_dlnOI_z", "note"],
               cot_rows,
               comment="# Weekly Delta(lev_money net long) z vs weekly Delta ln(OI) z "
                       "(COT report dates; OI at nearest stored day <= report date).")
    summary["cot_cross_leg"] = [dict(zip(["coin", "n", "rho", "note"], r))
                                for r in cot_rows]
    for r0 in cot_rows:
        print(f"[2c COT cross] {r0[0]}: n={r0[1]} rho={r0[2]} {r0[3]}")
    _write_json(_out("instrument_audits.json"), summary)
    return summary


# ========================================== SECTION 3 — RESIDUAL PREVIEW (D)
def section3_preview(rows, prices, core, core_reason, param_version: str) -> dict:
    _banner("SECTION 3 — RESIDUAL PREVIEW (SS2 D series via core "
            "divergence_series, 12 coins, research prices)")
    if core is None:
        _write_json(_out("preview_summary.json"),
                    {"status": "SKIPPED", "reason": core_reason})
        return _skip("3 preview", f"core unavailable: {core_reason}")
    by_coin = {}
    suspect_dropped = 0
    for r0 in rows:
        d = _iso(r0.get("signal_date"))
        if d is None:
            continue
        if r0.get("suspect"):
            suspect_dropped += 1  # K14: a suspect row breaks the series, never converts it
            continue
        if r0.get("open_interest"):
            by_coin.setdefault(r0["coin"], {})[d] = float(r0["open_interest"])
    flag_coins = set(getattr(core.mod, "FLAG_COINS", ("BTC", "ETH")))
    theta = getattr(core.mod, "THETA", 1.5)
    out_rows, per_coin = [], {}
    try:
        for coin in sorted(by_coin):
            # Aligned raw LEVEL series on dates present in both legs — the same
            # alignment core.crypto_divergence uses (that helper reads via
            # db_compat, which this runner is barred from; the arithmetic below
            # is entirely core divergence_series).
            px = prices.get(coin, {})
            days = [d for d in sorted(by_coin[coin]) if d in px]
            series = core.mod.divergence_series(
                [d.isoformat() for d in days],
                [by_coin[coin][d] for d in days],
                [px[d] for d in days],
                flag_theta=(theta if coin in flag_coins else None))
            latest = None
            n_obs = 0
            for row in series:
                out_rows.append([coin, row["date"], _r(row["q_chg"], 6),
                                 _r(row["p_chg"], 6), _r(row["zq"]), _r(row["zp"]),
                                 _r(row["D"]), row["measured"],
                                 bool(row.get("flag", False))])
                if row["D"] is not None:
                    n_obs += 1
                    latest = (row["date"], _r(row["D"]))
            per_coin[coin] = {"aligned_days": len(days), "d_obs": n_obs,
                              "latest_D": latest[1] if latest else None,
                              "latest_date": latest[0] if latest else None}
            latest_txt = (str(latest) if latest else
                          "n/a — honest-absence warm-up (strict 90-obs window "
                          "not yet filled)")
            print(f"[3 preview] {coin}: aligned days={len(days)} measured D obs="
                  f"{n_obs} latest={latest_txt}")
    except (CoreUnavailable, TypeError, KeyError) as e:
        _write_json(_out("preview_summary.json"),
                    {"status": "SKIPPED", "reason": f"core call failed: {e}"})
        return _skip("3 preview", f"core call failed: {e}")
    comment = (f"# SPEC-DEVELOPMENT DATA (pre-seal rows, K16) — instrument preview "
               f"only, never scored, param_version={param_version}\n"
               f"# NO outcome/ledger/forward join (prereg SS8). {RESEARCH_PRICE_CAVEAT}"
               f" flag column is internal/shadow (BTC/ETH theta-rule) — resolves "
               f"nothing, publishes nothing.")
    _write_csv(_out("divergence_preview.csv"),
               ["coin", "signal_date", "q_dlnOI_7d", "p_dlnPrice_7d",
                "zq", "zp", "D", "measured", "flag"],
               out_rows, comment=comment)
    summary = {"status": "OK", "per_coin": per_coin, "rows": len(out_rows),
               "suspect_rows_excluded": suspect_dropped,
               "param_version": param_version,
               "label": "spec-development preview (K16); never scored",
               "warmup_note": ("D is None until the core's strict full windows "
                               "fill: 7-obs dln lag + 90-obs z + 90-obs fit -> "
                               "first measured D at ~186 aligned days — honest "
                               "absence, not a defect")}
    _write_json(_out("preview_summary.json"), summary)
    print(f"[3 preview] {len(out_rows)} rows -> divergence_preview.csv "
          f"({suspect_dropped} suspect rows excluded)")
    return summary


# ============================================= SECTION 4 — EQUITY-FIRST (SS7)
FALLBACK_WATCHLIST = {  # verbatim fallback copy of financial_risk_gradient.WATCHLIST_TICKERS
    "Apple": "AAPL", "Microsoft": "MSFT", "Tesla": "TSLA", "Nvidia": "NVDA",
    "Meta": "META", "Alphabet": "GOOGL", "Amazon": "AMZN", "JPMorgan": "JPM",
    "Wells Fargo": "WFC", "Citigroup": "C", "Morgan Stanley": "MS", "IBM": "IBM",
    "Ford": "F", "Chevron": "CVX", "Lockheed Martin": "LMT", "SpaceX": "SPCX",
}


def _load_watchlist() -> tuple:
    """WATCHLIST_TICKERS via ast parse of financial_risk_gradient.py (no heavy
    import chain); falls back to the hardcoded copy above."""
    src_path = REPO / "transfer" / "financial_risk_gradient.py"
    try:
        tree = ast.parse(src_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == "WATCHLIST_TICKERS":
                        return ast.literal_eval(node.value), "ast-parsed"
    except Exception as e:  # noqa: BLE001
        return FALLBACK_WATCHLIST, f"fallback (ast parse failed: {e})"
    return FALLBACK_WATCHLIST, "fallback (assignment not found)"


def _stooq_closes(ticker: str) -> dict:
    url = f"https://stooq.com/q/d/l/?s={ticker.lower()}.us&i=d"
    text = _http_get(url, timeout=60).decode("utf-8", "replace")
    out = {}
    for r0 in csv.DictReader(io.StringIO(text)):
        d = _iso(r0.get("Date"))
        try:
            px = float(r0.get("Close", ""))
        except (TypeError, ValueError):
            continue
        if d and px > 0:
            out[d] = px
    if not out:
        # First run: every ticker parsed to zero closes with the body unseen
        # (stooq throttles/blocks many cloud IPs with a 200 + message page) —
        # surface what it actually said.
        raise RuntimeError(f"stooq body yielded no closes; body head: "
                           f"{text[:120]!r}")
    return out


def _fmp_closes(ticker: str) -> dict:
    """FMP EOD light closes — the project's PAID price source (already the
    market ledger's ground-truth series in transfer/fmp_data.py); used here
    as the primary research price when FMP_API_KEY is present, internal
    research use only."""
    key = os.getenv("FMP_API_KEY", "")
    if not key:
        raise RuntimeError("FMP_API_KEY unset")
    qs = urllib.parse.urlencode({"symbol": ticker.upper(), "apikey": key})
    raw = json.loads(_http_get(
        f"https://financialmodelingprep.com/stable/historical-price-eod/light?{qs}",
        timeout=60).decode("utf-8"))
    out = {}
    for r0 in raw if isinstance(raw, list) else []:
        d = _iso((r0.get("date") or "")[:10])
        px = r0.get("price", r0.get("close"))
        try:
            px = float(px)
        except (TypeError, ValueError):
            continue
        if d and px > 0:
            out[d] = px
    if not out:
        raise RuntimeError("FMP returned no usable closes")
    return out


def _equity_closes(ticker: str) -> tuple:
    """(closes, source) — FMP (paid, primary) then stooq (public fallback)."""
    errs = []
    for src, fn in (("fmp", _fmp_closes), ("stooq", _stooq_closes)):
        try:
            return fn(ticker), src
        except Exception as e:  # noqa: BLE001
            errs.append(f"{src}: {e}")
    raise RuntimeError("; ".join(errs))


def section4_equity(core, core_reason, param_version: str) -> dict:
    _banner("SECTION 4 — EQUITY-FIRST residual (SS7 cadence: FINRA short interest "
            "vs price, research-only)")
    if core is None or not callable(getattr(core.mod, "equity_divergence", None)):
        reason = (core_reason if core is None
                  else "core has no equity_divergence function")
        _write_json(_out("equity_summary.json"),
                    {"status": "SKIPPED", "reason": reason})
        return _skip("4 equity", f"core unavailable: {reason}")
    try:
        import finra_data
    except Exception as e:  # noqa: BLE001
        _write_json(_out("equity_summary.json"),
                    {"status": "SKIPPED", "reason": f"finra_data import failed: {e}"})
        return _skip("4 equity", f"finra_data import failed: {e}")
    if not os.getenv("FINRA_API_KEY", ""):
        _write_json(_out("equity_summary.json"),
                    {"status": "SKIPPED",
                     "reason": "FINRA_API_KEY unset (short_interest_series needs it)"})
        return _skip("4 equity", "FINRA_API_KEY unset — "
                                 "finra_data.short_interest_series returns empty")
    watch, watch_src = _load_watchlist()
    print(f"watchlist: {len(watch)} tickers ({watch_src})")
    out_rows, per_ticker = [], {}
    status = "OK"
    for name, ticker in sorted(watch.items(), key=lambda kv: kv[1]):
        try:
            series = finra_data.short_interest_series(ticker)
        except Exception as e:  # noqa: BLE001
            per_ticker[ticker] = {"status": "SKIPPED", "reason": f"FINRA error: {e}"}
            continue
        pts = [(_iso(r0.get("settlement_date")), r0.get("short_position"))
               for r0 in series]
        pts = [(d, float(v)) for d, v in pts if d and v and float(v) > 0]
        if len(pts) < 3:
            per_ticker[ticker] = {"status": "SKIPPED",
                                  "reason": f"short-interest series too short "
                                            f"(n={len(pts)})"}
            continue
        try:
            closes, price_src = _equity_closes(ticker)
        except Exception as e:  # noqa: BLE001
            per_ticker[ticker] = {"status": "SKIPPED",
                                  "reason": f"price fetch failed: {e}"}
            continue

        def _px_at(dd):  # nearest trading close on/before the settlement date
            for back in range(0, 7):
                v = closes.get(dd - timedelta(days=back))
                if v:
                    return v
            return None
        # SS7: si_series and price_series on the SAME settlement dates; the core
        # equity_divergence applies the cadence-scaled windows (dln 1, z 24,
        # Theil–Sen 24, refit every observation) itself.
        si_series = {d.isoformat(): s for d, s in pts}
        price_series = {}
        for d, _s in pts:
            px = _px_at(d)
            if px:
                price_series[d.isoformat()] = px
        try:
            res = core.mod.equity_divergence(ticker, si_series, price_series)
        except Exception as e:  # noqa: BLE001
            per_ticker[ticker] = {"status": "SKIPPED",
                                  "reason": f"core equity_divergence failed: {e}"}
            continue
        latest = None
        n_obs = 0
        for row in res.get("series", []):
            out_rows.append([ticker, row["date"], _r(row["q_chg"], 6),
                             _r(row["p_chg"], 6), _r(row["zq"]), _r(row["zp"]),
                             _r(row["D"]), row["measured"]])
            if row["D"] is not None:
                n_obs += 1
                latest = (row["date"], _r(row["D"]))
        per_ticker[ticker] = {
            "status": "OK", "price_source": price_src, "si_points": len(pts),
            "aligned_obs": res.get("days"), "d_obs": n_obs,
            "latest_D": latest[1] if latest else None,
            "latest_date": latest[0] if latest else None,
            "caveat": (None if n_obs > 0 else
                       "honest-absence warm-up: SS7 strict windows (1-obs dln + "
                       "24-obs z + 24-obs fit) need ~48 aligned settlements "
                       "(~2 years of FINRA bi-monthly data) before the first "
                       "measured D")}
        print(f"[4 equity] {ticker}: SI points={len(pts)} aligned="
              f"{res.get('days')} measured D obs={n_obs} "
              f"latest={latest if latest else 'n/a (honest-absence warm-up)'}")
        time.sleep(1.0)  # pace the public price endpoints politely
    _write_csv(_out("equity_divergence.csv"),
               ["ticker", "settlement_date", "q_dlnShortInterest",
                "p_dlnPrice_matching_window", "zq", "zp", "D", "measured"],
               out_rows,
               comment=f"# SPEC-DEVELOPMENT DATA (pre-seal rows, K16) — instrument "
                       f"preview only, never scored, param_version={param_version}\n"
                       f"# SS7 equity-first instantiation; research-only under the "
                       f"seal until its own board note. {RESEARCH_PRICE_CAVEAT}")
    ok = [t for t, v in per_ticker.items() if v.get("status") == "OK"]
    if not ok:
        status = "SKIPPED" if per_ticker else "SKIPPED"
    summary = {"status": status, "tickers_ok": len(ok),
               "per_ticker": per_ticker, "rows": len(out_rows),
               "watchlist_source": watch_src}
    _write_json(_out("equity_summary.json"), summary)
    print(f"[4 equity] {len(out_rows)} rows across {len(ok)} tickers "
          f"-> equity_divergence.csv")
    return summary


# ---------------------------------------------------------------------- main
def main() -> int:
    print("divergence_research.py — READ-ONLY research runner "
          "(prereg DIVERGENCE_PREREG_2026-09-14.md; SS8 SELECT-only contract "
          "asserted at import)")
    print(f"OUT_DIR = {OUT_DIR}")
    run = {"started_utc": datetime.now(timezone.utc).isoformat(),
           "sections": {}}

    core_mod, core_err = _import_core()
    seal = section0_seal(core_mod, core_err)
    run["sections"]["0_seal"] = seal
    if seal["status"] != "OK":
        _write_json(_out("run_summary.json"), run)
        print("\nEXIT 1 — seal check failed (the only failing exit).")
        return 1
    param_version = seal["param_version"]
    core, core_reason = None, None
    try:
        core = CoreAdapter(core_mod)
    except CoreUnavailable as e:
        core_reason = str(e)
        print(f"[core] WARNING — core adapter unusable, core-dependent sections "
              f"will SKIP: {core_reason}")

    # Section 1 — COT backfill (no DB, no core needed)
    run["sections"]["1_cot"] = section1_cot()

    # DB-dependent sections
    conn, db_err = _connect_db()
    rows, cols, missing_cols = [], [], []
    if conn is None:
        reason = f"database unavailable: {db_err}"
        run["sections"]["2_instrument_audits"] = _skip("2 audits", reason)
        run["sections"]["3_preview"] = _skip("3 preview", reason)
    else:
        try:
            rows, cols, missing_cols = load_derivs(conn)
            print(f"\ncoinapi_derivs: {len(rows)} rows loaded "
                  f"(columns: {cols}; absent late-added columns: {missing_cols})")
        except Exception as e:  # noqa: BLE001
            reason = f"coinapi_derivs unreadable: {e}"
            run["sections"]["2_instrument_audits"] = _skip("2 audits", reason)
            run["sections"]["3_preview"] = _skip("3 preview", reason)
            rows = []
        finally:
            try:
                conn.close()
            except Exception:  # noqa: BLE001
                pass
        if rows:
            coins = sorted({r0["coin"] for r0 in rows})
            prices, price_errors = fetch_research_prices(coins)
            if price_errors:
                print(f"[prices] research-price fetch issues: {price_errors}")
            try:
                run["sections"]["2_instrument_audits"] = section2_audits(
                    rows, cols, missing_cols, prices, price_errors, core,
                    core_reason, run["sections"]["1_cot"])
            except Exception as e:  # noqa: BLE001
                run["sections"]["2_instrument_audits"] = _skip(
                    "2 audits", f"unexpected error: {type(e).__name__}: {e}")
            try:
                run["sections"]["3_preview"] = section3_preview(
                    rows, prices, core, core_reason, param_version)
            except Exception as e:  # noqa: BLE001
                run["sections"]["3_preview"] = _skip(
                    "3 preview", f"unexpected error: {type(e).__name__}: {e}")
        elif "2_instrument_audits" not in run["sections"]:
            reason = "coinapi_derivs returned zero rows"
            run["sections"]["2_instrument_audits"] = _skip("2 audits", reason)
            run["sections"]["3_preview"] = _skip("3 preview", reason)

    # Section 4 — equity-first (DB-free; FINRA + stooq public endpoints)
    try:
        run["sections"]["4_equity"] = section4_equity(core, core_reason,
                                                      param_version)
    except Exception as e:  # noqa: BLE001
        run["sections"]["4_equity"] = _skip(
            "4 equity", f"unexpected error: {type(e).__name__}: {e}")

    run["finished_utc"] = datetime.now(timezone.utc).isoformat()
    if core is not None and core.notes:
        run["core_adapter_notes"] = core.notes
    _write_json(_out("run_summary.json"), run)
    _banner("RUN SUMMARY")
    for k, v in run["sections"].items():
        print(f"  {k}: {v.get('status')}"
              + (f" — {v.get('reason')}" if v.get("reason") else ""))
    print(f"\nAll outputs in {OUT_DIR} (run_summary.json has the full record).")
    print("Exit 0 — seal verified; skipped sections degrade, never fail the run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
