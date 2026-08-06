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
from datetime import datetime, timedelta, timezone
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
        "no_comparator": ["XRP funds (XRPC/TOXR) — no published-flow page exists; "
                          "honest absence, never implied covered"],
        "band": {"floor": "max($10M, 0.05% AUM)", "direction": "mandatory on material "
                 "days", "magnitude": "±25% or ±$20M (more forgiving)",
                 "bias_rule": f"≥{BIAS_RUN} consecutive same-sign errors fail"},
        "gate_status": gate,
        "note": "Held-out verifier (spec §8 gate 4 / A1.5): derived Δshares×NAV vs the "
                "issuers' published daily flows. Nothing here feeds any score or ledger "
                "verdict.",
    }


if __name__ == "__main__":
    import json
    print("=== etf_flow_reconcile — one live pass ===")
    print(json.dumps(reconcile(), indent=1)[:1200])
    print("\n--- report ---")
    print(json.dumps(report(), indent=1)[:2000])
