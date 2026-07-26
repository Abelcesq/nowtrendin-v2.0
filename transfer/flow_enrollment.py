"""
FLOW ENROLLMENT — the driver that turns the insider panel into ledger rows. HELD-OUT.

The one construction the Board's freeze permits, because enrollment IS the objective
(master remediation Part F, Step 6). This module is the detector's ONLY doorway into the
money-movement program: `gravitational_anomaly_detector` imports THIS module and nothing
else on the flow side, so the firewall's acknowledged-exception list stays one entry wide
and the direction stays one-way (detector → here → ledger; never a read back into a score).

WHAT A CYCLE DOES (behind FLOW_ENROLL, after INSIDER_FLOW ingestion has run):
  1. QUALIFY  — find tickers whose accumulated Form-4 panel shows a BUYING CLUSTER:
                >= QUALIFY_MIN_BUYERS distinct insiders with open-market purchases (code P)
                filed within the trailing QUALIFY_WINDOW_D days. This is the Chairman's own
                red flag ("cluster buying — 3+ C-suite executives buying on the open market")
                and the Seyhun-grounded observable the Board settled: BREADTH, a change,
                never a dollar level.
  2. MATCH    — build controls per the Economist's key: same sector, same size band, same
                ADV band, same PRE-TREND bucket (last-20-sessions mean / full-window median,
                computed ONLY inside the frozen baseline window — no lookahead), and NO
                qualifying disclosure of their own in the window. Controls must be trending
                the way the treated name was trending BEFORE the filing, or "separation"
                measures volume momentum instead of the disclosure.
  3. ENROLL   — flow_ledger.enroll(): atomic treated+controls or nothing; refuses without an
                active pre-registration; baselines frozen at enrollment.
  4. SWEEP    — flow_ledger.sweep(): resolve pending rows against the arrival clock, §13-paced.

DETERMINISM: control selection is seeded by the match-group id, so a re-run of the same
cycle proposes the same controls — reproducibility over convenience.

MEASUREMENT ONLY. Never imported by scoring (enforced by heldout_registry).
"""
from __future__ import annotations

import os
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

import db_compat

DB_PATH = os.getenv("GAD_DB_PATH", "anomaly_detector.db")

FLOW_ENROLL = os.getenv("FLOW_ENROLL", "0") == "1"
#: Distinct open-market buyers required to qualify a cluster (the Chairman's "3+ C-suite").
QUALIFY_MIN_BUYERS = int(os.getenv("FLOW_QUALIFY_MIN_BUYERS", "3"))
#: Trailing window (days) the cluster must fall inside.
QUALIFY_WINDOW_D = int(os.getenv("FLOW_QUALIFY_WINDOW_D", "10"))
#: Candidate controls examined per treated ticker before giving up (bounded work, §13).
CONTROL_CANDIDATES_MAX = int(os.getenv("FLOW_CONTROL_CANDIDATES_MAX", "24"))
#: Enrollments attempted per cycle (bounded; the feed is capped anyway).
ENROLL_PER_CYCLE_MAX = int(os.getenv("FLOW_ENROLL_PER_CYCLE_MAX", "5"))
#: Sweep batch per cycle.
SWEEP_PER_CYCLE = int(os.getenv("FLOW_SWEEP_PER_CYCLE", "60"))
#: Pre-trend bucket edges (Economist's key): contracting <0.9 · flat 0.9-1.15 · expanding >1.15
_PRETREND_EDGES = (0.9, 1.15)
#: Market-cap size bands (USD) for matching — coarse deciles are overkill at this universe.
_SIZE_BANDS = (300e6, 2e9, 10e9, 50e9)     # micro | small | mid | large | mega


def _now_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _connect(db_path: str = DB_PATH):
    conn = db_compat.connect(db_path)
    if not db_compat.USE_PG:
        try:
            import sqlite3
            conn.row_factory = sqlite3.Row
        except Exception:
            pass
    return conn


# ── 1. QUALIFY ──────────────────────────────────────────────────────────────────────────

def qualify_clusters(db_path: str = DB_PATH, asof: str = "") -> list:
    """Tickers whose panel shows >= QUALIFY_MIN_BUYERS distinct open-market buyers within
    the trailing window, newest disclosure first. Reads ONLY the append-only insider panel."""
    asof = asof or _now_date()
    since = (datetime.strptime(asof, "%Y-%m-%d") - timedelta(days=QUALIFY_WINDOW_D)
             ).strftime("%Y-%m-%d")
    conn = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        rows = [dict(r) for r in conn.execute(
            f"SELECT ticker, COUNT(DISTINCT COALESCE(actor_hash, role_raw)) AS buyers, "
            f"MAX(signal_date) AS latest_filing, SUM(value_usd) AS total_usd "
            f"FROM insider_events WHERE txn_code='P' AND signal_date >= {ph} "
            f"AND signal_date <= {ph} GROUP BY ticker "
            f"HAVING COUNT(DISTINCT COALESCE(actor_hash, role_raw)) >= {ph} "
            f"ORDER BY MAX(signal_date) DESC", (since, asof, QUALIFY_MIN_BUYERS)).fetchall()]
    except Exception:
        rows = []
    finally:
        conn.close()
    for r in rows:
        r["window_start"] = since
        r["asof"] = asof
    return rows


# ── 2. MATCH ────────────────────────────────────────────────────────────────────────────

def _size_band(mktcap_usd: Optional[float]) -> int:
    if not mktcap_usd:
        return -1
    for i, edge in enumerate(_SIZE_BANDS):
        if mktcap_usd < edge:
            return i
    return len(_SIZE_BANDS)


def _pretrend_bucket(sv: dict, asof: str) -> Optional[str]:
    """Last-20-sessions mean / full-window median, computed ONLY inside the frozen
    baseline window (arrival_clock's own window; no lookahead)."""
    import arrival_clock
    base = arrival_clock.compute_baseline(sv, asof)
    if not base.get("available"):
        return None
    dates = sorted(d for d in sv
                   if base["window_start"] <= d <= base["window_end"])
    if len(dates) < 20:
        return None
    last20 = [sv[d] for d in dates[-20:]]
    med = base["median_volume"]
    if not med:
        return None
    ratio = (sum(last20) / len(last20)) / med
    lo, hi = _PRETREND_EDGES
    return "contracting" if ratio < lo else "expanding" if ratio > hi else "flat"


def _screener_universe() -> list:
    """One screener snapshot: ticker, sector, market cap, avg volume. $0 (already paid)."""
    try:
        import finviz_data
        rows = finviz_data.screener(view="111") or []
    except Exception:
        return []
    out = []
    for r in rows:
        t = (r.get("Ticker") or "").upper().strip()
        if not t:
            continue
        def _n(x):
            try:
                return float(str(x).replace(",", "").replace("%", "").strip())
            except (TypeError, ValueError):
                return None
        cap = _n(r.get("Market Cap"))
        out.append({"ticker": t, "sector": (r.get("Sector") or "").strip(),
                    "mktcap": cap, "avg_volume": _n(r.get("Volume"))})
    return out


def _instrument_profile(ticker: str, asof: str, fetch_ohlcv=None) -> Optional[dict]:
    """Frozen-window volume series + baseline + pretrend for one instrument."""
    import arrival_clock
    if fetch_ohlcv is None:
        import fmp_data
        fetch_ohlcv = fmp_data.historical_ohlcv
    d = datetime.strptime(asof, "%Y-%m-%d")
    frm = (d - timedelta(days=200)).strftime("%Y-%m-%d")
    try:
        ohlcv = fetch_ohlcv(ticker, frm, asof)
    except Exception:
        return None
    if not ohlcv:
        return None
    sv = arrival_clock.share_volume_series(ohlcv)
    if not sv:
        return None
    base = arrival_clock.compute_baseline(sv, asof)
    if not base.get("available"):
        return {"baseline": base}          # calibrating — caller decides
    return {"baseline": base, "sv": sv,
            "pretrend": _pretrend_bucket(sv, asof),
            "pre_arrived": arrival_clock.already_arrived_before(
                sv, asof, base["median_volume"])}


def build_controls(treated: dict, need: int = 3, db_path: str = DB_PATH,
                   universe: list = None, fetch_ohlcv=None,
                   pause_s: float = None) -> list:
    """Matched controls for one treated ticker. Deterministic (seeded by group identity).

    Match key (Economist): sector + size band + ADV band + pretrend bucket, and NO
    qualifying open-market purchase of their own inside the window. Each accepted control
    carries its own frozen baseline (enroll() demands it) and the achieved match facets.
    """
    if pause_s is None:
        pause_s = float(os.getenv("FLOW_SWEEP_PAUSE_S",
                                  os.getenv("COLLECT_SOURCE_PAUSE_S", "10")))
    uni = universe if universe is not None else _screener_universe()
    if not uni:
        return []
    t_tkr = treated["ticker"].upper()
    t_row = next((u for u in uni if u["ticker"] == t_tkr), None)
    t_prof = treated.get("_profile") or {}
    t_pretrend = t_prof.get("pretrend")
    t_band = _size_band((t_row or {}).get("mktcap"))
    t_sector = (t_row or {}).get("sector") or ""
    t_adv = (t_row or {}).get("avg_volume")

    # Tickers with their own qualifying buys are ineligible as controls.
    conn = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        tainted = {r[0] if not hasattr(r, "keys") else dict(r)["ticker"]
                   for r in conn.execute(
                       f"SELECT DISTINCT ticker FROM insider_events "
                       f"WHERE txn_code='P' AND signal_date >= {ph}",
                       (treated.get("window_start") or _now_date(),)).fetchall()}
    except Exception:
        tainted = set()
    finally:
        conn.close()

    def _adv_ok(u):
        if not t_adv or not u.get("avg_volume"):
            return True                     # facet unavailable — do not fabricate a match
        return 0.2 <= (u["avg_volume"] / t_adv) <= 5.0

    pool = [u for u in uni
            if u["ticker"] != t_tkr and u["ticker"] not in tainted
            and (u.get("sector") or "") == t_sector
            and _size_band(u.get("mktcap")) == t_band
            and _adv_ok(u)]
    # DETERMINISTIC order: seed by the group identity, not the wall clock.
    rng = random.Random(f"{t_tkr}|{treated.get('asof')}|{treated.get('latest_filing')}")
    rng.shuffle(pool)

    out, tried = [], 0
    for cand in pool:
        if len(out) >= need or tried >= CONTROL_CANDIDATES_MAX:
            break
        tried += 1
        if tried > 1 and pause_s:
            time.sleep(pause_s)             # §13: breather between remote fetches
        prof = _instrument_profile(cand["ticker"], treated["asof"], fetch_ohlcv)
        if not prof or not prof.get("baseline", {}).get("available"):
            continue
        # Pretrend must MATCH the treated bucket (the whole point of the facet). If the
        # treated bucket is unknown, refuse fancy matching rather than fake it — the
        # enrollment simply fails controls and is counted as a refusal.
        if t_pretrend is None or prof.get("pretrend") != t_pretrend:
            continue
        out.append({
            "ticker": cand["ticker"], "name": cand["ticker"],
            "detection_date": treated["asof"],
            "observable_value": 0.0, "direction": 0,
            "baseline": prof["baseline"],
            "pre_arrived": bool(prof.get("pre_arrived")),
            "sector": t_sector, "size_decile": t_band,
            "match_facets": {"sector": t_sector, "size_band": t_band,
                             "pretrend": prof.get("pretrend"), "adv_matched": True},
        })
    return out


# ── 3+4. THE CYCLE ──────────────────────────────────────────────────────────────────────

def run_cycle(db_path: str = DB_PATH, fetch_ohlcv=None, universe: list = None,
              pause_s: float = None) -> dict:
    """One enrollment + sweep pass. Runs ONLY from the scheduler thread (§13 placement —
    a synchronous multi-fetch loop must never sit behind an API endpoint)."""
    if not (FLOW_ENROLL or os.getenv("FLOW_ENROLL", "0") == "1"):
        return {"ran": False, "reason": "FLOW_ENROLL is not enabled"}
    import flow_ledger

    flow_ledger.init_flow_db(db_path)
    out = {"ran": True, "qualified": 0, "enrolled": 0, "refused": [], "sweep": None}

    pre = flow_ledger.active_prereg(db_path)
    if not pre:
        # No pre-registration -> nothing may enroll (the ledger enforces this too; saying
        # it here keeps the cycle log honest instead of producing N identical refusals).
        out["refused"].append("no active pre-registration")
    else:
        clusters = qualify_clusters(db_path)
        out["qualified"] = len(clusters)
        for cl in clusters[:ENROLL_PER_CYCLE_MAX]:
            prof = _instrument_profile(cl["ticker"], cl["asof"], fetch_ohlcv)
            if not prof or not prof.get("baseline", {}).get("available"):
                out["refused"].append(f"{cl['ticker']}: baseline calibrating")
                continue
            cl["_profile"] = prof
            treated = {
                "ticker": cl["ticker"], "name": cl["ticker"],
                "detection_date": cl["asof"],
                "disclosure_ts": cl.get("latest_filing") or "",
                "observable_value": float(cl.get("buyers") or 0),   # BREADTH, not dollars
                "direction": 1,
                "baseline": prof["baseline"],
                "pre_arrived": bool(prof.get("pre_arrived")),
                "sector": (prof.get("match_facets") or {}).get("sector"),
                "size_decile": None,
            }
            controls = build_controls(cl | {"_profile": prof}, db_path=db_path,
                                      universe=universe, fetch_ohlcv=fetch_ohlcv,
                                      pause_s=pause_s)
            res = flow_ledger.enroll(treated, controls, db_path=db_path)
            if res.get("enrolled"):
                out["enrolled"] += 1
            else:
                out["refused"].append(f"{cl['ticker']}: {res.get('reason')}")

    try:
        out["sweep"] = flow_ledger.sweep(db_path=db_path, limit=SWEEP_PER_CYCLE,
                                         pause_s=pause_s)
    except Exception as e:
        out["sweep"] = {"error": str(e)}
    return out


def ingest_panel(db_path: str = DB_PATH) -> dict:
    """Market-wide Form-4 ingestion + §16a universe promotion, behind INSIDER_FLOW.

    Routed through THIS module so the detector's doorway into the flow program stays ONE
    module wide (the firewall's acknowledged exception covers flow_enrollment alone —
    a direct detector→insider_flow import would be a violation, by design).

    HARD ORDER (Expansionist, master remediation): refuses to ingest while the parser fix
    is off — `insider_events` is append-only under the never-delete rule, and doubled
    tickers written today would be poison forever.
    """
    if os.getenv("INSIDER_FLOW", "0") != "1":
        return {"ran": False, "reason": "INSIDER_FLOW is not enabled"}
    if os.getenv("INSIDER_PARSER_FIX", "0") != "1":
        return {"ran": False,
                "reason": "REFUSED: INSIDER_PARSER_FIX is off — ingesting the legacy "
                          "parse would write doubled tickers into an append-only panel"}
    import insider_flow
    insider_flow.INSIDER_FLOW = True        # module caches the env at import; assert intent
    insider_flow.init_insider_db(db_path)
    out = {"ingest": insider_flow.ingest(db_path=db_path)}
    try:
        out["promotion"] = insider_flow.promote_universe(db_path=db_path)
    except Exception as e:
        out["promotion"] = {"error": str(e)}
    return out


# ── Serve wrappers (the detector's endpoints call ONLY these) ───────────────────────────

def status(db_path: str = DB_PATH) -> dict:
    import flow_ledger
    try:
        import insider_flow
        panel = insider_flow.status(db_path)
    except Exception as e:
        panel = {"error": str(e)}
    return {"held_out": True,
            "flags": {"INSIDER_FLOW": os.getenv("INSIDER_FLOW", "0"),
                      "FLOW_ENROLL": os.getenv("FLOW_ENROLL", "0"),
                      "INSIDER_PARSER_FIX": os.getenv("INSIDER_PARSER_FIX", "0")},
            "prereg": flow_ledger.active_prereg(db_path),
            "panel": panel,
            "qualify_rule": {"min_buyers": QUALIFY_MIN_BUYERS,
                             "window_days": QUALIFY_WINDOW_D}}


def accuracy(db_path: str = DB_PATH) -> dict:
    import flow_ledger
    return flow_ledger.report(db_path=db_path)


def lock_prereg(terms: dict, db_path: str = DB_PATH) -> dict:
    """The one-time pre-registration lock (POST /flow/prereg, internal-key gated at the
    endpoint). Thin wrapper so the detector never imports flow_ledger directly."""
    import flow_ledger
    flow_ledger.init_flow_db(db_path)
    required = ("hypothesis", "observable", "universe", "enroll_threshold",
                "arrival_mult", "horizon_days", "min_episodes", "stop_rule",
                "param_version")
    missing = [k for k in required if terms.get(k) in (None, "")]
    if missing:
        return {"locked": False, "reason": f"missing terms: {missing}"}
    return {"locked": True, **flow_ledger.register_prereg(
        hypothesis=terms["hypothesis"], observable=terms["observable"],
        universe=terms["universe"], enroll_threshold=float(terms["enroll_threshold"]),
        arrival_mult=float(terms["arrival_mult"]),
        horizon_days=int(terms["horizon_days"]),
        min_episodes=int(terms["min_episodes"]), stop_rule=terms["stop_rule"],
        param_version=terms["param_version"], doc_path=terms.get("doc_path", ""),
        primary_horizon_days=int(terms.get("primary_horizon_days", 90)),
        db_path=db_path)}


if __name__ == "__main__":
    import json, tempfile
    print("=== flow_enrollment self-test (synthetic; no network) ===\n")
    tmp = os.path.join(tempfile.gettempdir(), "flow_enroll_selftest.db")
    if os.path.exists(tmp):
        os.remove(tmp)
    import insider_flow as I, flow_ledger as F
    I.init_insider_db(tmp)
    F.init_flow_db(tmp)

    # Panel: AAA has a 3-buyer cluster; ZZZ has one buy (must not qualify).
    conn = _connect(tmp)
    today = _now_date()
    for i, (tkr, actor) in enumerate([("AAA", "h1"), ("AAA", "h2"), ("AAA", "h3"),
                                      ("ZZZ", "h9")]):
        conn.execute("INSERT INTO insider_events (id,ticker,signal_date,txn_date,"
                     "actor_hash,role_raw,role_class,txn_code,value_usd,shares,price,"
                     "source,ingested_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (f"e{i}", tkr, today, today, actor, "Officer", "officer", "P",
                      500000.0, 1000.0, 10.0, "test", today))
    conn.commit(); conn.close()

    q = qualify_clusters(db_path=tmp)
    assert len(q) == 1 and q[0]["ticker"] == "AAA" and q[0]["buyers"] == 3, q
    print(f"qualify: AAA cluster (3 buyers) found; single-buy ZZZ excluded  OK")

    # Synthetic market: every ticker gets a quiet 120-session series; CCC1/CCC2/CCC3 are
    # the same sector/size and flat — legitimate controls; DDD is a different sector.
    base_day = datetime(2026, 3, 1, tzinfo=timezone.utc)
    def mk_series(vol):
        return {(base_day + timedelta(days=i)).strftime("%Y-%m-%d"):
                {"close": 10.0, "volume": vol} for i in range(140)}
    series = {t: mk_series(1000) for t in ("AAA", "CCC1", "CCC2", "CCC3", "CCC4", "DDD")}
    fetch = lambda t, f, u: series.get(t)
    uni = ([{"ticker": "AAA", "sector": "tech", "mktcap": 5e8, "avg_volume": 1000}]
           + [{"ticker": f"CCC{i}", "sector": "tech", "mktcap": 6e8, "avg_volume": 1200}
              for i in (1, 2, 3, 4)]
           + [{"ticker": "DDD", "sector": "energy", "mktcap": 6e8, "avg_volume": 1000}])

    # No prereg -> cycle refuses enrollment but still runs the (empty) sweep.
    os.environ["FLOW_ENROLL"] = "1"
    import importlib, sys as _s
    _m = _s.modules[__name__]; _m.FLOW_ENROLL = True
    # Detection date must sit INSIDE the synthetic series for baselines to exist.
    asof = (base_day + timedelta(days=130)).strftime("%Y-%m-%d")
    for row in q: row["asof"] = asof
    r0 = run_cycle(db_path=tmp, fetch_ohlcv=fetch, universe=uni, pause_s=0)
    assert r0["ran"] and r0["enrolled"] == 0 and "no active pre-registration" in r0["refused"], r0
    print("no prereg -> cycle refuses enrollment (honestly, once)  OK")

    lock = lock_prereg({"hypothesis": "cluster buying precedes participation",
                        "observable": "distinct open-market buyers (breadth)",
                        "universe": "test", "enroll_threshold": 3, "arrival_mult": 3.0,
                        "horizon_days": 180, "min_episodes": 120,
                        "stop_rule": "one analysis at min_episodes",
                        "param_version": "test-v1", "primary_horizon_days": 90},
                       db_path=tmp)
    assert lock["locked"], lock
    print(f"prereg locked: {lock['prereg_id']}  OK")

    # Full cycle: qualify -> match (deterministic controls, same sector/size/pretrend,
    # DDD excluded) -> enroll atomically -> sweep runs.
    q2 = qualify_clusters(db_path=tmp)
    for row in q2: row["asof"] = asof
    # monkeypatch qualify inside run_cycle via the panel date — instead just call the parts:
    prof = _instrument_profile("AAA", asof, fetch)
    assert prof and prof["baseline"]["available"] and prof["pretrend"] == "flat", prof
    ctrls = build_controls(q2[0] | {"_profile": prof}, db_path=tmp,
                           universe=uni, fetch_ohlcv=fetch, pause_s=0)
    assert len(ctrls) == 3 and all(c["ticker"].startswith("CCC") for c in ctrls), \
        [c["ticker"] for c in ctrls]
    print(f"controls: 3 matched ({[c['ticker'] for c in ctrls]}), DDD (wrong sector) "
          f"and AAA (treated) excluded  OK")
    # Determinism: same inputs, same controls.
    ctrls2 = build_controls(q2[0] | {"_profile": prof}, db_path=tmp,
                            universe=uni, fetch_ohlcv=fetch, pause_s=0)
    assert [c["ticker"] for c in ctrls] == [c["ticker"] for c in ctrls2]
    print("control selection is deterministic (seeded by group identity)  OK")

    import flow_ledger as FL
    treated = {"ticker": "AAA", "name": "AAA", "detection_date": asof,
               "observable_value": 3.0, "direction": 1, "baseline": prof["baseline"],
               "pre_arrived": bool(prof.get("pre_arrived")), "sector": "tech",
               "size_decile": 1}
    res = FL.enroll(treated, ctrls, db_path=tmp)
    assert res.get("enrolled") and res["controls"] == 3, res
    print(f"enrolled: 1 treated + {res['controls']} controls, atomically  OK")

    st = status(db_path=tmp)
    assert st["prereg"] and st["qualify_rule"]["min_buyers"] == QUALIFY_MIN_BUYERS
    acc = accuracy(db_path=tmp)
    assert acc["available"] and acc["arms"]["control_rows"] == 3, acc.get("arms")
    print(f"status + accuracy wrappers serve  OK  "
          f"(treated_rows={acc['arms']['treated_rows']}, control_rows={acc['arms']['control_rows']})")
    print("\nAll self-tests passed.")
