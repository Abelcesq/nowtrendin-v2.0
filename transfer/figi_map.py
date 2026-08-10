"""
figi_map.py — row-level security-identifier mapping (OpenFIGI), buyer roadmap Phase 1.

FISD identifier standard: instrument-keyed data should carry an accepted security
identifier per row (ticker, ISIN, FIGI, ...). FIGI via OpenFIGI is free, MIT-licensed,
and FIGIs are never reused or changed — the right fit for a vendor register.

SCOPE (deliberate): the INSTRUMENT-KEYED legs only — the equity watchlist, the ETF
proxy roster, and the crypto proxy equities. The attention product's unit is TOPICS;
imposing instrument identifiers there would misdescribe the data (an App Annie
hazard), so topics are explicitly out of scope.

Mechanics: build_figi_map() assembles the roster, batch-maps via the keyless OpenFIGI
v3 API (jobs of 10, paced for the keyless rate limit), and caches into the `figi_map`
table (ticker PK). Fail-closed: an unmapped ticker is recorded status='unmapped' —
never guessed, never blocking. Reads are served from the cache only (get_figi /
figi_report); the live API is touched only by an explicit build call (internal
endpoint), never on the serve path. DISPLAY/EXPORT metadata only — nothing in
scoring reads this table.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")
_OPENFIGI_URL = "https://api.openfigi.com/v3/mapping"
_BATCH = 10                      # keyless job limit per request is higher; stay modest
_PAUSE_S = float(os.getenv("FIGI_BATCH_PAUSE_S", "7"))   # keyless ~25 req/min cap


def _connect(db_path: str = DB_PATH):
    return db_compat.connect(db_path)


def init_figi_db(db_path: str = DB_PATH):
    c = _connect(db_path)
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS figi_map (
                ticker TEXT PRIMARY KEY,
                figi TEXT,                 -- NULL when unmapped (declared absence)
                name TEXT,
                exch_code TEXT,
                status TEXT,               -- 'mapped' | 'unmapped'
                mapped_at TEXT
            )
        """)
        c.commit()
    finally:
        c.close()


def roster(db_path: str = DB_PATH) -> list:
    """Distinct instrument tickers across the instrument-keyed legs."""
    out, seen = [], set()

    def _add(t):
        t = (t or "").strip().upper()
        if t and t not in seen:
            seen.add(t)
            out.append(t)

    try:
        from financial_risk_gradient import WATCHLIST_TICKERS
        for t in WATCHLIST_TICKERS.values():
            _add(t)
    except Exception:
        pass
    try:
        from etf_flow import ETF_PROXIES
        for t in ETF_PROXIES:
            _add(t)
    except Exception:
        pass
    try:
        import crypto_signals as _cs
        for cfg in _cs.COIN_UNIVERSE.values():
            for pr in (cfg.get("proxies") or []):
                _add(pr.get("ticker"))
    except Exception:
        pass
    return out


def build_figi_map(db_path: str = DB_PATH) -> dict:
    """Map the roster via OpenFIGI and cache. Idempotent upsert; safe to re-run."""
    import requests
    init_figi_db(db_path)
    tickers = roster(db_path)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    mapped, unmapped, errors = 0, 0, 0
    c = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        for i in range(0, len(tickers), _BATCH):
            batch = tickers[i:i + _BATCH]
            jobs = [{"idType": "TICKER", "idValue": t, "exchCode": "US"}
                    for t in batch]
            try:
                r = requests.post(_OPENFIGI_URL, json=jobs, timeout=30,
                                  headers={"Content-Type": "application/json"})
                if r.status_code != 200:
                    print(f"[figi] HTTP {r.status_code}: {r.text[:120]}")
                    errors += len(batch)
                    time.sleep(_PAUSE_S)
                    continue
                results = r.json()
            except Exception as e:
                print(f"[figi] batch error: {e}")
                errors += len(batch)
                time.sleep(_PAUSE_S)
                continue
            for t, res in zip(batch, results):
                data = (res or {}).get("data") or []
                if data:
                    d0 = data[0]
                    c.execute(
                        f"INSERT INTO figi_map (ticker,figi,name,exch_code,status,mapped_at) "
                        f"VALUES ({ph},{ph},{ph},{ph},{ph},{ph}) "
                        f"ON CONFLICT (ticker) DO UPDATE SET figi=EXCLUDED.figi, "
                        f"name=EXCLUDED.name, exch_code=EXCLUDED.exch_code, "
                        f"status=EXCLUDED.status, mapped_at=EXCLUDED.mapped_at",
                        (t, d0.get("figi"), d0.get("name"), d0.get("exchCode"),
                         "mapped", now))
                    mapped += 1
                else:
                    c.execute(
                        f"INSERT INTO figi_map (ticker,figi,name,exch_code,status,mapped_at) "
                        f"VALUES ({ph},NULL,NULL,NULL,{ph},{ph}) "
                        f"ON CONFLICT (ticker) DO UPDATE SET status=EXCLUDED.status, "
                        f"mapped_at=EXCLUDED.mapped_at",
                        (t, "unmapped", now))
                    unmapped += 1
            if i + _BATCH < len(tickers):
                time.sleep(_PAUSE_S)
        c.commit()
    finally:
        c.close()
    out = {"roster": len(tickers), "mapped": mapped, "unmapped": unmapped,
           "errors": errors, "at": now}
    print(f"[figi] build: {json.dumps(out)}")
    return out


def figi_report(db_path: str = DB_PATH) -> dict:
    """Cached mapping state — served by the internal diag endpoint."""
    init_figi_db(db_path)
    c = _connect(db_path)
    try:
        # PG rows are dict-like, sqlite rows are tuples (the codebase idiom).
        cols = ("ticker", "figi", "name", "status", "mapped_at")
        raw = c.execute(
            "SELECT ticker, figi, name, status, mapped_at FROM figi_map "
            "ORDER BY ticker").fetchall()
        rows = [dict(r) if hasattr(r, "keys") else dict(zip(cols, r)) for r in raw]
    except Exception as e:
        return {"available": False, "reason": str(e)[:120]}
    finally:
        c.close()
    return {"available": True, "rows": rows,
            "mapped": sum(1 for r in rows if r["status"] == "mapped"),
            "unmapped": [r["ticker"] for r in rows if r["status"] != "mapped"],
            "roster_now": len(roster(db_path)),
            "note": "FIGI = display/export metadata for instrument-keyed legs only; "
                    "topics carry no instrument identifier by design."}
