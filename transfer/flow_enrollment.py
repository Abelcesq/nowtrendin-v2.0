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
#: ⚠ B2 (Board review 2, ALL FIVE): this env is a DEFAULT, never the authority. `run_cycle`
#: takes the threshold from the ACTIVE PRE-REGISTRATION and REFUSES when the env disagrees.
#: Before the fix, setting this to 2 on one dyno silently redefined the cohort under an
#: unchanged SHA — the D2 failure class, one level up, in the module written after D2.
QUALIFY_MIN_BUYERS = int(os.getenv("FLOW_QUALIFY_MIN_BUYERS", "3"))
#: Trailing window the cluster must fall inside, in TRADING SESSIONS.
#: ⚠ B3 (Challenger): the registration said "10 trading days"; the code subtracted 10
#: CALENDAR days (~7 sessions — a ~30% tighter window than the one registered). Sessions are
#: now counted as WEEKDAYS walked back from `asof` (deterministic, dependency-free). US market
#: holidays are NOT excluded, so a holiday lengthens the effective calendar span by one day;
#: that exact wording is now inside the SHA rather than implied by the word "trading".
QUALIFY_WINDOW_SESSIONS = int(os.getenv("FLOW_QUALIFY_WINDOW_SESSIONS", "10"))
#: Candidate controls examined per treated ticker before giving up (bounded work, §13).
CONTROL_CANDIDATES_MAX = int(os.getenv("FLOW_CONTROL_CANDIDATES_MAX", "24"))
#: Enrollments attempted per cycle (bounded; the feed is capped anyway).
#: ⚠ Board review 2 (Executioner) measured the worst case at 5 treated x 24 candidates x a
#: 10s §13 pause ~= 25-30 min INSIDE `_collect_phase`, plus ~12 min of sweep — against only
#: ~20 min of headroom before the 420-min risk-stale window. Deferring a cluster is nearly
#: free (the trailing window re-qualifies it next cycle, and a later detection_date only
#: SHRINKS measured lead — the conservative direction), so the default is 3.
ENROLL_PER_CYCLE_MAX = int(os.getenv("FLOW_ENROLL_PER_CYCLE_MAX", "3"))
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

def window_start(asof: str, sessions: int = None) -> str:
    """Walk back `sessions` WEEKDAYS from `asof` — the registered window's exact semantics.

    B3: "10 trading days" is now counted, not approximated by a calendar subtraction. US
    market holidays are deliberately NOT excluded (no market-calendar dependency); the
    registration says so, so the code and the SHA describe the same window.
    """
    sessions = QUALIFY_WINDOW_SESSIONS if sessions is None else int(sessions)
    d = datetime.strptime(asof, "%Y-%m-%d")
    walked = 0
    while walked < sessions:
        d -= timedelta(days=1)
        if d.weekday() < 5:              # Mon-Fri
            walked += 1
    return d.strftime("%Y-%m-%d")


def panel_first_date(db_path: str = DB_PATH) -> str:
    """The panel's birth certificate: the date of the first coverage watermark. Empty
    string while the panel has never ingested."""
    conn = _connect(db_path)
    try:
        row = conn.execute("SELECT MIN(ingest_at) AS f FROM insider_coverage").fetchone()
        v = (dict(row) if row else {}).get("f") or ""
    except Exception:
        v = ""
    finally:
        conn.close()
    if not v:
        return ""
    try:
        from date_utils import to_iso_date
        return to_iso_date(str(v)) or ""
    except Exception:
        return ""


def qualification_floor(db_path: str = DB_PATH, asof: str = "",
                        window_sessions: int = None) -> dict:
    """AMENDMENT A1 (Board 2026-08-04, the Challenger; founder-ruled same day,
    pre-enrollment — zero rows enrolled at adoption): qualification REFUSES any window
    that extends before the panel existed. A 10-session window evaluated over a 3-day
    panel is LEFT-CENSORED: treated-side censoring is merely conservative, but controls
    "with no qualifying disclosure of their own in the window" would pass on
    UNVERIFIABLE cleanliness — first-era rows measured under different information
    conditions than every later row, under the same prereg SHA. The floor makes the flip
    safe to fire early: enrollment simply does not begin until window_start >=
    panel_start, with no human remembering required."""
    asof = asof or _now_date()
    ws = window_start(asof, window_sessions)
    ps = panel_first_date(db_path)
    return {"asof": asof, "window_start": ws, "panel_start": ps or None,
            "spanned": bool(ps) and ws >= ps,
            "rule": "window_start >= panel_start (prereg amendment A1, 2026-08-04 PT)"}


def qualify_clusters(db_path: str = DB_PATH, asof: str = "",
                     min_buyers: int = None, window_sessions: int = None) -> list:
    """Tickers whose panel shows >= `min_buyers` distinct open-market buyers within the
    trailing window, newest disclosure first. Reads ONLY the append-only insider panel.

    `min_buyers` / `window_sessions` are passed by `run_cycle` FROM THE ACTIVE
    PRE-REGISTRATION (B2). They fall back to the module envs only for offline/self-test use.

    DISTINCT-BUYER COUNTING (B4, Challenger + Guardian): the count keys on `actor_hash` and
    falls back to `role_raw` only for rows written before a salt existed. Mixed-salt eras
    would let ONE person appear as both a hash and a role string and count TWICE — enough to
    fabricate the 3-buyer trigger itself. `insider_flow.ingest()` now REFUSES to write
    unsalted rows, so the fallback is a reader for legacy rows, never a live path.

    IDENTITY RESOLUTION (Board 2026-08-04, Challenger U1; founder-ordered): the count is
    over CANONICAL identities — context-confirmed name variants of the same person on the
    same ticker collapse to one buyer (insider_flow.identity_map; conflicting-role groups
    are never auto-merged). Name-formatting noise must not be able to fabricate the
    3-buyer trigger. Applied at COUNTING time only; the append-only panel is untouched.

    WINDOW FLOOR (amendment A1): refuses until the window is fully inside the panel's
    lifetime — see qualification_floor().
    """
    asof = asof or _now_date()
    min_buyers = QUALIFY_MIN_BUYERS if min_buyers is None else int(min_buyers)
    since = window_start(asof, window_sessions)

    floor = qualification_floor(db_path, asof, window_sessions)
    if not floor["spanned"]:
        return []                        # left-censored window: refuse, never approximate

    try:
        import insider_flow as _iflow
        idmap = _iflow.identity_map(db_path, since, asof)
    except Exception:
        idmap = {}

    conn = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        raw = [dict(r) for r in conn.execute(
            f"SELECT ticker, actor_hash, role_raw, signal_date, value_usd "
            f"FROM insider_events WHERE txn_code='P' AND signal_date >= {ph} "
            f"AND signal_date <= {ph}", (since, asof)).fetchall()]
    except Exception:
        raw = []
    finally:
        conn.close()

    per = {}
    for r in raw:
        rid = r.get("actor_hash") or r.get("role_raw") or ""
        canon = idmap.get(r.get("actor_hash") or "", rid)
        d = per.setdefault(r["ticker"], {"buyers": set(), "latest": "", "usd": 0.0})
        d["buyers"].add(canon)
        d["latest"] = max(d["latest"], r.get("signal_date") or "")
        d["usd"] += float(r.get("value_usd") or 0)

    rows = [{"ticker": t, "buyers": len(d["buyers"]), "latest_filing": d["latest"],
             "total_usd": round(d["usd"], 2)}
            for t, d in per.items() if len(d["buyers"]) >= min_buyers]
    rows.sort(key=lambda r: r["latest_filing"], reverse=True)
    for r in rows:
        r["window_start"] = since
        r["asof"] = asof
        r["min_buyers"] = min_buyers
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
    """One screener snapshot: ticker, sector, market cap. $0 (already paid).

    ⚠ B6 (Executioner): this snapshot's "Volume" column is the CURRENT SESSION's volume, not
    ADV — and a treated name mid-attention-spike has an inflated one, which biased which
    controls were allowed to match. Session volume is no longer a match facet at all. The ADV
    facet is now the FROZEN 60-session baseline median that both arms already carry (see
    `_adv_ratio`) — a real average, computed inside the frozen window, no lookahead, no extra
    fetch. The screener is used only for sector + market cap, which it reports correctly.
    """
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
        out.append({"ticker": t, "sector": (r.get("Sector") or "").strip(),
                    "mktcap": _n(r.get("Market Cap"))})
    return out


def facets_of(ticker: str, universe: list) -> dict:
    """Sector + size band for one ticker, read from the screener snapshot.

    ⚠ B1 (Executioner F1 / Challenger F7 / Guardian): `run_cycle` used to read the treated
    row's facets from `prof.get("match_facets")` — a key `_instrument_profile` has never
    returned — so EVERY treated row would have enrolled with sector None and size_decile
    hardcoded None, while its controls carried both. The pre-registered analysis stratifies
    on those facets, and flow rows are never deleted, so row 1 would have been permanently
    unanalysable. Treated and control facets now come from the SAME function.
    """
    row = next((u for u in (universe or []) if u.get("ticker") == (ticker or "").upper()),
               None)
    return {"sector": (row or {}).get("sector") or "",
            "size_band": _size_band((row or {}).get("mktcap")),
            "in_universe": row is not None}


def _instrument_profile(ticker: str, asof: str, fetch_ohlcv=None,
                        mult: float = None) -> Optional[dict]:
    """Frozen-window volume series + baseline + pretrend for one instrument.

    ⚠ B5 (Challenger F8 / Economist): `mult` is the ACTIVE PRE-REGISTRATION's `arrival_mult`,
    passed by the caller. It used to be omitted, so the pre-arrival screen resolved from the
    `ARRIVAL_VOL_MULT` env instead — meaning an env edit would silently change WHO is excluded
    from the lead denominator, on rows already enrolled under a fixed SHA. D2 again.
    """
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
    kw = {"mult": float(mult)} if mult else {}
    return {"baseline": base, "sv": sv,
            "pretrend": _pretrend_bucket(sv, asof),
            "pre_arrived": arrival_clock.already_arrived_before(
                sv, asof, base["median_volume"], **kw)}


#: ADV band: a control's frozen baseline median must sit inside this ratio of the treated's.
_ADV_BAND = (0.2, 5.0)


def _tainted_tickers(db_path: str, since: str, until: str, min_buyers: int) -> set:
    """Tickers that ran their OWN qualifying cluster in the window — ineligible as controls.

    ⚠ B6 (Challenger F6), two fixes:
      • BOUNDED: the query had no upper bound, so any run with `asof` in the past (a backfill,
        a delayed cycle) excluded controls using purchases filed AFTER the detection date —
        lookahead in control selection.
      • QUALIFYING, not ANY: one lone purchase used to taint a candidate, while the
        registration excludes controls with no *qualifying* disclosure. Excluding every name
        with any insider buying selects systematically QUIETER controls, which flatters the
        treated arm — a bias in our own favour, and undisclosed. The taint now matches the
        registered exclusion exactly: a control is ineligible only if it would itself qualify.
    """
    conn = _connect(db_path)
    ph = "%s" if db_compat.USE_PG else "?"
    try:
        return {(r[0] if not hasattr(r, "keys") else dict(r)["ticker"])
                for r in conn.execute(
                    f"SELECT ticker FROM insider_events "
                    f"WHERE txn_code='P' AND signal_date >= {ph} AND signal_date <= {ph} "
                    f"GROUP BY ticker "
                    f"HAVING COUNT(DISTINCT COALESCE(actor_hash, role_raw)) >= {ph}",
                    (since, until, min_buyers)).fetchall()}
    except Exception:
        return set()
    finally:
        conn.close()


def build_controls(treated: dict, need: int = 3, db_path: str = DB_PATH,
                   universe: list = None, fetch_ohlcv=None,
                   pause_s: float = None, min_buyers: int = None,
                   mult: float = None) -> list:
    """Matched controls for one treated ticker. Deterministic (seeded by group identity).

    Match key (Economist): sector + size band + ADV band + pretrend bucket, and no
    qualifying open-market cluster of their own inside the window. Each accepted control
    carries its own frozen baseline (enroll() demands it) and the achieved match facets.

    DETERMINISM (B-should-fix, Challenger F9): reproducible GIVEN THE SCREENER SNAPSHOT. The
    seed fixes the shuffle, not the pool — the pool is a live snapshot, so a re-run on a
    later day may propose different candidates. Stated rather than implied.
    """
    if pause_s is None:
        pause_s = float(os.getenv("FLOW_SWEEP_PAUSE_S",
                                  os.getenv("COLLECT_SOURCE_PAUSE_S", "10")))
    uni = universe if universe is not None else _screener_universe()
    if not uni:
        return []
    t_tkr = treated["ticker"].upper()
    t_prof = treated.get("_profile") or {}
    t_pretrend = t_prof.get("pretrend")
    t_adv = ((t_prof.get("baseline") or {}).get("median_volume")) or 0.0
    t_facets = facets_of(t_tkr, uni)
    t_band, t_sector = t_facets["size_band"], t_facets["sector"]

    # ⚠ Should-fix (Executioner): short-circuit BEFORE the fetch loop. An unknown treated
    # pretrend refuses every candidate by construction, so walking 24 of them — each an FMP
    # fetch behind a 10s §13 pause — burned ~4-5 minutes for a predetermined refusal.
    if t_pretrend is None:
        return []
    # A treated name absent from the screener has no real facets; matching it would mean
    # matching "" to "" and -1 to -1. Refuse rather than fabricate a match key.
    if not t_facets["in_universe"] or not t_sector:
        return []

    tainted = _tainted_tickers(
        db_path, treated.get("window_start") or _now_date(),
        treated.get("asof") or _now_date(),
        QUALIFY_MIN_BUYERS if min_buyers is None else int(min_buyers))

    pool = [u for u in uni
            if u["ticker"] != t_tkr and u["ticker"] not in tainted
            and (u.get("sector") or "") == t_sector
            and _size_band(u.get("mktcap")) == t_band]
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
        prof = _instrument_profile(cand["ticker"], treated["asof"], fetch_ohlcv, mult=mult)
        if not prof or not prof.get("baseline", {}).get("available"):
            continue
        # Pretrend must MATCH the treated bucket (the whole point of the facet).
        if prof.get("pretrend") != t_pretrend:
            continue
        # ADV band on the FROZEN baseline medians — a real 60-session average on both sides,
        # not the screener's current-session volume (B6). When either side is missing we
        # REFUSE the candidate; the old code passed it and then stamped `adv_matched: True`,
        # which is the decorative-baseline pattern in miniature: the disclosure said matched,
        # the code had not matched.
        c_adv = (prof.get("baseline") or {}).get("median_volume") or 0.0
        if not t_adv or not c_adv:
            continue
        ratio = c_adv / t_adv
        if not (_ADV_BAND[0] <= ratio <= _ADV_BAND[1]):
            continue
        out.append({
            "ticker": cand["ticker"], "name": cand["ticker"],
            "detection_date": treated["asof"],
            "observable_value": 0.0, "direction": 0,
            "baseline": prof["baseline"],
            "pre_arrived": bool(prof.get("pre_arrived")),
            "sector": t_sector, "size_decile": t_band,
            "match_facets": {"sector": t_sector, "size_band": t_band,
                             "pretrend": prof.get("pretrend"),
                             "adv_matched": True, "adv_ratio": round(ratio, 3),
                             "adv_source": "frozen_baseline_median"},
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
        # ⚠ B2 (Board review 2, unanimous): every enrollment term is read FROM THE ACTIVE
        # REGISTRATION, and a disagreeing env HALTS the cycle rather than quietly winning.
        # Before this, qualification ran on `FLOW_QUALIFY_MIN_BUYERS` while the SHA said 3:
        # one dyno env-set would have redefined the cohort under an unchanged hash, forever,
        # in a ledger that never deletes.
        terms = flow_ledger.prereg_terms(pre)
        p_buyers, p_window = terms["enroll_threshold"], terms["qualify_window_sessions"]
        p_mult = terms["arrival_mult"]
        drift = []
        if int(p_buyers) != QUALIFY_MIN_BUYERS:
            drift.append(f"min_buyers env={QUALIFY_MIN_BUYERS} vs prereg={int(p_buyers)}")
        if int(p_window) != QUALIFY_WINDOW_SESSIONS:
            drift.append(f"window env={QUALIFY_WINDOW_SESSIONS} vs prereg={int(p_window)}")
        if drift:
            out["refused"].append(
                "HALTED: environment disagrees with the active pre-registration "
                f"({'; '.join(drift)}) — enrolling would silently redefine cohort "
                f"{pre.get('id')}. Fix the env or mint a new registration.")
            out["term_drift"] = drift
            clusters = []
        else:
            clusters = qualify_clusters(db_path, min_buyers=int(p_buyers),
                                        window_sessions=int(p_window))
        out["qualified"] = len(clusters)
        out["terms"] = {"prereg_id": pre.get("id"), "min_buyers": int(p_buyers),
                        "window_sessions": int(p_window), "arrival_mult": p_mult}
        # ONE screener snapshot per cycle, shared by every treated row and its controls —
        # treated and control facets must come from the same snapshot or the match key is
        # comparing two different worlds.
        uni = universe if universe is not None else _screener_universe()
        deferred = max(0, len(clusters) - ENROLL_PER_CYCLE_MAX)
        if deferred:
            # No silent caps: a deferred cluster re-qualifies next cycle (the window is
            # trailing), but the count is logged rather than dropped on the floor.
            out["deferred_to_next_cycle"] = deferred
        for cl in clusters[:ENROLL_PER_CYCLE_MAX]:
            prof = _instrument_profile(cl["ticker"], cl["asof"], fetch_ohlcv, mult=p_mult)
            if not prof or not prof.get("baseline", {}).get("available"):
                out["refused"].append(f"{cl['ticker']}: baseline calibrating")
                continue
            cl["_profile"] = prof
            # B1: treated facets from the SAME function the controls use.
            t_facets = facets_of(cl["ticker"], uni)
            treated = {
                "ticker": cl["ticker"], "name": cl["ticker"],
                "detection_date": cl["asof"],
                "disclosure_ts": cl.get("latest_filing") or "",
                "observable_value": float(cl.get("buyers") or 0),   # BREADTH, not dollars
                "direction": 1,
                "baseline": prof["baseline"],
                "pre_arrived": bool(prof.get("pre_arrived")),
                "sector": t_facets["sector"],
                "size_decile": t_facets["size_band"],
            }
            controls = build_controls(cl | {"_profile": prof}, db_path=db_path,
                                      universe=uni, fetch_ohlcv=fetch_ohlcv,
                                      pause_s=pause_s, min_buyers=int(p_buyers),
                                      mult=p_mult)
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
        live = insider_flow.liveness(db_path)      # B9 source-liveness tripwire
    except Exception as e:
        panel = {"error": str(e)}
        live = {"status": "UNKNOWN", "detail": str(e)}
    pre = flow_ledger.active_prereg(db_path)
    terms = flow_ledger.prereg_terms(pre) if pre else {}
    # The env is reported BESIDE the registered terms, and any divergence is named. A reader
    # must be able to see, without reading code, whether the running config still matches the
    # registration that defines the cohort (B2).
    drift = []
    if terms:
        if int(terms.get("enroll_threshold") or 0) != QUALIFY_MIN_BUYERS:
            drift.append("enroll_threshold")
        if int(terms.get("qualify_window_sessions") or 0) != QUALIFY_WINDOW_SESSIONS:
            drift.append("qualify_window_sessions")
    return {"held_out": True,
            "flags": {"INSIDER_FLOW": os.getenv("INSIDER_FLOW", "0"),
                      "FLOW_ENROLL": os.getenv("FLOW_ENROLL", "0"),
                      "INSIDER_PARSER_FIX": os.getenv("INSIDER_PARSER_FIX", "0")},
            "prereg": pre,
            "registered_terms": terms,
            "panel": panel,
            "source_liveness": live,
            "qualify_rule": {"min_buyers": QUALIFY_MIN_BUYERS,
                             "window_sessions": QUALIFY_WINDOW_SESSIONS,
                             "window_basis": "weekdays; US market holidays not excluded"},
            "qualification_floor": qualification_floor(db_path),
            "term_drift": drift,
            "enrollment_halted": bool(drift)}


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
    # B7: everything the code enforces travels INSIDE the hash. Defaults are the values this
    # build actually runs with, so a term omitted by a caller is still registered honestly
    # rather than left to drift with the environment.
    extra = dict(terms.get("extra_terms") or {})
    extra.setdefault("qualify_window_sessions",
                     int(terms.get("qualify_window_sessions", QUALIFY_WINDOW_SESSIONS)))
    extra.setdefault("qualify_window_basis", "weekdays_walked_back_holidays_not_excluded")
    extra.setdefault("echo_sessions", int(os.getenv("FLOW_ECHO_SESSIONS", "3")))
    extra.setdefault("arrival_hits_required", int(os.getenv("ARRIVAL_HITS_REQUIRED", "2")))
    extra.setdefault("arrival_window_sessions",
                     int(os.getenv("ARRIVAL_WINDOW_SESSIONS", "5")))
    extra.setdefault("baseline_sessions", int(os.getenv("ARRIVAL_BASELINE_SESSIONS", "60")))
    extra.setdefault("baseline_gap_sessions", int(os.getenv("ARRIVAL_BASELINE_GAP", "5")))
    extra.setdefault("match_key", {
        "facets": ["sector", "size_band", "adv_band", "pretrend_bucket"],
        "size_bands_usd": list(_SIZE_BANDS),
        "pretrend_edges": list(_PRETREND_EDGES),
        "adv_band": list(_ADV_BAND),
        "adv_source": "frozen_baseline_median_share_volume",
        "control_exclusion": "no qualifying cluster of its own inside the same window",
    })
    return {"locked": True, **flow_ledger.register_prereg(
        hypothesis=terms["hypothesis"], observable=terms["observable"],
        universe=terms["universe"], enroll_threshold=float(terms["enroll_threshold"]),
        arrival_mult=float(terms["arrival_mult"]),
        horizon_days=int(terms["horizon_days"]),
        min_episodes=int(terms["min_episodes"]), stop_rule=terms["stop_rule"],
        param_version=terms["param_version"], doc_path=terms.get("doc_path", ""),
        primary_horizon_days=int(terms.get("primary_horizon_days", 90)),
        extra_terms=extra, db_path=db_path)}


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

    q2 = qualify_clusters(db_path=tmp)
    for row in q2: row["asof"] = asof
    prof = _instrument_profile("AAA", asof, fetch, mult=3.0)
    assert prof and prof["baseline"]["available"] and prof["pretrend"] == "flat", prof
    ctrls = build_controls(q2[0] | {"_profile": prof}, db_path=tmp,
                           universe=uni, fetch_ohlcv=fetch, pause_s=0, mult=3.0)
    assert len(ctrls) == 3 and all(c["ticker"].startswith("CCC") for c in ctrls), \
        [c["ticker"] for c in ctrls]
    assert all(c["match_facets"]["adv_source"] == "frozen_baseline_median" for c in ctrls)
    print(f"controls: 3 matched ({[c['ticker'] for c in ctrls]}), DDD (wrong sector) "
          f"and AAA (treated) excluded; ADV from the FROZEN baseline  OK")
    ctrls2 = build_controls(q2[0] | {"_profile": prof}, db_path=tmp,
                            universe=uni, fetch_ohlcv=fetch, pause_s=0, mult=3.0)
    assert [c["ticker"] for c in ctrls] == [c["ticker"] for c in ctrls2]
    print("control selection is deterministic, GIVEN the snapshot (seeded by group id)  OK")

    # ── B1 REGRESSION: the whole cycle, THROUGH run_cycle ────────────────────────────────
    # The old self-test hand-built the treated dict and so never executed the line that
    # actually writes it — which is exactly why `prof.get("match_facets")` (a key that has
    # never existed) survived review. Enrollment now runs end-to-end, and the STORED row is
    # inspected. This test fails on the shipped-then-fixed defect.
    import flow_ledger as FL
    _orig_qualify = globals()["qualify_clusters"]
    globals()["qualify_clusters"] = lambda db_path=DB_PATH, asof="", min_buyers=None, \
        window_sessions=None: [dict(r, min_buyers=min_buyers) for r in q2]
    try:
        rc = run_cycle(db_path=tmp, fetch_ohlcv=fetch, universe=uni, pause_s=0)
    finally:
        globals()["qualify_clusters"] = _orig_qualify
    assert rc["enrolled"] == 1, rc
    conn = _connect(tmp)
    trow = dict(conn.execute(
        "SELECT sector, size_decile, observable_value FROM flow_pending_detections "
        "WHERE cohort='treated'").fetchone())
    crow = dict(conn.execute(
        "SELECT sector, size_decile FROM flow_pending_detections "
        "WHERE cohort='control' LIMIT 1").fetchone())
    conn.close()
    assert trow["sector"] == "tech", f"B1: treated row lost its sector -> {trow}"
    assert trow["size_decile"] is not None, f"B1: treated row lost its size band -> {trow}"
    assert trow["sector"] == crow["sector"] and trow["size_decile"] == crow["size_decile"], \
        f"B1: treated and control facets disagree -> {trow} vs {crow}"
    assert trow["observable_value"] == 3.0, trow
    print(f"run_cycle enrolled 1 treated + controls; STORED treated row carries "
          f"sector={trow['sector']!r} size_decile={trow['size_decile']}  OK  (B1)")

    # ── B2 REGRESSION: an env that disagrees with the registration HALTS the cycle ───────
    _saved = globals()["QUALIFY_MIN_BUYERS"]
    globals()["QUALIFY_MIN_BUYERS"] = 2
    try:
        rc2 = run_cycle(db_path=tmp, fetch_ohlcv=fetch, universe=uni, pause_s=0)
    finally:
        globals()["QUALIFY_MIN_BUYERS"] = _saved
    assert rc2["enrolled"] == 0 and rc2.get("term_drift"), rc2
    assert any("HALTED" in r for r in rc2["refused"]), rc2
    print("env threshold 2 vs registered 3 -> cycle HALTS, enrolls nothing  OK  (B2)")

    # ── B2 REGRESSION (ledger door): below-threshold never enrolls, and is COUNTED ───────
    weak = {"ticker": "WEAK", "name": "WEAK", "detection_date": asof,
            "observable_value": 1.0, "direction": 1, "baseline": prof["baseline"],
            "pre_arrived": False, "sector": "tech", "size_decile": 1}
    r_weak = FL.enroll(weak, ctrls, db_path=tmp)
    assert not r_weak["enrolled"] and "below the pre-registered" in r_weak["reason"], r_weak
    conn = _connect(tmp)
    bt = conn.execute("SELECT count FROM flow_gate_rejects WHERE reason='below_threshold'"
                      ).fetchone()
    conn.close()
    assert bt and (dict(bt)["count"] if hasattr(bt, "keys") else bt[0]) >= 1, \
        "the refusal must be COUNTED, not merely returned"
    print("observable below the registered threshold -> refused AND counted  OK  (B2)")

    # ── B3 REGRESSION: the window is TRADING sessions, not calendar days ─────────────────
    ws = window_start("2026-07-27", 10)     # Monday; 10 weekdays back = Mon 2026-07-13
    assert ws == "2026-07-13", ws
    assert (datetime.strptime("2026-07-27", "%Y-%m-%d")
            - datetime.strptime(ws, "%Y-%m-%d")).days == 14, ws
    print(f"qualify window = 10 trading sessions -> {ws} (14 calendar days)  OK  (B3)")

    # ── B7 REGRESSION: the previously-unhashed terms are INSIDE the SHA ──────────────────
    t2 = FL.prereg_terms(FL.active_prereg(tmp))
    for k in ("qualify_window_sessions", "echo_sessions", "arrival_hits_required",
              "arrival_window_sessions", "match_key"):
        assert t2.get(k) is not None, f"{k} missing from the registered terms"
    a = FL.register_prereg("h", "o", "u", 3, 3.0, 180, 120, "s", "v",
                           extra_terms={"echo_sessions": 3}, db_path=tmp)["prereg_id"]
    b = FL.register_prereg("h", "o", "u", 3, 3.0, 180, 120, "s", "v",
                           extra_terms={"echo_sessions": 4}, db_path=tmp)["prereg_id"]
    assert a != b, "changing the echo threshold MUST mint a different registration"
    print(f"extra terms are hashed: echo 3 -> {a}, echo 4 -> {b} (different cohorts)  OK  (B7)")

    st = status(db_path=tmp)
    assert st["prereg"] and st["registered_terms"]
    print(f"status + accuracy wrappers serve  OK")
    print("\nAll self-tests passed.")
