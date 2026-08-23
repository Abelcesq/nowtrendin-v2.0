"""
test_probability_agents.py — tests AND tripwires for the Base Rate agents.

THE RULE THIS FILE OBEYS
------------------------
Every enforcer must be shown to FAIL on a fixture that violates its claim.

A test that only passes on correct code proves nothing: `total <= 3` is
satisfied maximally by an instrument that enrolls nothing, and a determinism
check that compares two empty dicts is vacuously green.  So each invariant here
has a matching `_tripwire` test that constructs a violating fixture and asserts
the check actually catches it.  If a tripwire ever passes without the guard
firing, the guard is decoration.

Run:  python3 test_probability_agents.py
"""

from __future__ import annotations

import datetime as _dt
import os
import re
import sqlite3
import sys
import traceback
from typing import List, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from probability_core import (  # noqa: E402
    Measured, Reading, State, absent, brier_skill_score, buhlmann_straub,
    classify_measured, kaplan_meier, km_arrival_probability,
    murphy_decomposition, not_applicable,
)
from trend_probability_agent import TrendProbabilityAgent  # noqa: E402
from market_flow_probability_agent import (  # noqa: E402
    MacroContext, MarketFlowProbabilityAgent, classify_credit, classify_rates,
)
from crypto_flow_probability_agent import (  # noqa: E402
    COT_CONTRACT_CODES, CryptoFlowProbabilityAgent, cot_knowable_at,
)

_FAILS: List[str] = []
_PASSES = 0


def check(name: str, fn) -> None:
    global _PASSES
    try:
        fn()
        _PASSES += 1
        print(f"  PASS  {name}")
    except Exception as exc:  # noqa: BLE001
        _FAILS.append(f"{name}: {exc}")
        print(f"  FAIL  {name}: {exc}")
        traceback.print_exc(limit=2)


def approx(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


# ===========================================================================
# I1 — a non-MEASURED Reading can never carry a number
# ===========================================================================

def t_i1_absent_has_no_value():
    r = absent("cohort", 30, "no data")
    assert r.value is None
    assert r.state is State.ABSENT
    assert r.to_payload()["probability"] is None


def t_i1_TRIPWIRE_absent_with_zero_is_rejected():
    """
    The defect this prevents shipped once: compute_dark_matter returned 0.0 for
    'could not read' while its docstring called 0 'the neutral value'. On a
    0-100 scale 0 is the FLOOR. If this tripwire stops raising, the guard is gone.
    """
    raised = False
    try:
        Reading(state=State.ABSENT, cohort="c", horizon_days=30,
                value=0.0, reason="no data")
    except ValueError:
        raised = True
    assert raised, "Reading accepted value=0.0 in ABSENT state — I1 guard is dead"


def t_i1_TRIPWIRE_measured_without_value_is_rejected():
    raised = False
    try:
        Reading(state=State.MEASURED, cohort="c", horizon_days=30, n_events=5)
    except ValueError:
        raised = True
    assert raised, "MEASURED Reading accepted value=None"


def t_i1_TRIPWIRE_absent_without_reason_is_rejected():
    raised = False
    try:
        Reading(state=State.ABSENT, cohort="c", horizon_days=30)
    except ValueError:
        raised = True
    assert raised, "ABSENT Reading accepted an empty reason"


# ===========================================================================
# I2 — the tri-state
# ===========================================================================

def t_i2_three_distinct_states():
    assert classify_measured(None) is Measured.UNKNOWN
    assert classify_measured(0) is Measured.BLIND
    assert classify_measured(False) is Measured.BLIND
    assert classify_measured(1) is Measured.YES
    assert classify_measured(True) is Measured.YES
    assert classify_measured(0.42) is Measured.YES


def t_i2_TRIPWIRE_null_is_not_blind():
    """
    The `d_measured IS NULL` defect: a two-branch reader treats NULL as
    measured-and-quiet because `None != 0` is True. These must not collapse.
    """
    assert classify_measured(None) is not classify_measured(0), \
        "NULL and 0 collapsed to the same state — the tri-state is a boolean again"


def t_i2_TRIPWIRE_string_nulls():
    assert classify_measured("") is Measured.UNKNOWN
    assert classify_measured("null") is Measured.UNKNOWN
    assert classify_measured("0") is Measured.BLIND


# ===========================================================================
# I3 / I4 — Kaplan-Meier and censoring
# ===========================================================================

def t_i4_km_matches_binomial_without_censoring():
    """With no censoring, 1 - S(t) must equal the naive proportion exactly."""
    durations = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    events = [1, 1, 1, 0 if False else 1, 1, 1, 1, 1, 1, 1]  # all events
    F, _, _, n_ev = km_arrival_probability(durations, events, horizon=10)
    assert n_ev == 10
    assert approx(F, 1.0, 1e-12), f"expected F=1.0, got {F}"

    d2 = [1, 2, 3, 4, 5]
    e2 = [1, 1, 0, 0, 0]   # censored at 3,4,5 — but all AFTER the horizon
    F2, _, _, _ = km_arrival_probability(d2, e2, horizon=2)
    assert approx(F2, 2 / 5, 1e-12), f"expected 0.4, got {F2}"


def t_i4_TRIPWIRE_censoring_changes_the_answer():
    """
    Proves censoring is genuinely handled rather than ignored. If KM ever
    equals the naive 'pending == non-event' proportion under heavy censoring,
    the estimator has silently degenerated.

    NOTE ON THIS FIXTURE. The first version of this test censored 8 rows at
    t=3 with both events at t=1 and t=2 — and it FAILED, because both events
    occurred while all 10 rows were still at risk, so KM must equal the naive
    proportion there. The estimator was right and the fixture was vacuous: it
    never exercised the property it claimed to test. Censoring only changes the
    answer when it removes rows from the risk set BEFORE later events. Kept as
    a comment because a tripwire that catches its own author is the point.
    """
    # 5 rows censored at t=1, then 2 events at t=5 and t=6 among the survivors.
    durations = [1, 1, 1, 1, 1, 5, 6, 30, 30, 30]
    events = [0, 0, 0, 0, 0, 1, 1, 0, 0, 0]
    F, _, _, _ = km_arrival_probability(durations, events, horizon=30)
    naive = 2 / 10          # what "pending == non-event" would report
    assert F is not None
    assert not approx(F, naive, 1e-6), (
        f"KM ({F:.6f}) equals the naive proportion ({naive:.6f}) under "
        f"censoring that precedes the events — the estimator is not handling "
        f"censoring"
    )
    # Direction matters: coding pending rows as non-events UNDERSTATES arrival.
    assert F > naive, f"expected KM > naive under censoring, got {F} vs {naive}"
    assert approx(F, 0.4, 1e-9), f"expected exactly 0.4, got {F}"


def t_i3_zero_events_returns_none_not_zero():
    """A cohort with no observed events yields S=1 everywhere -> F=0."""
    durations = [10, 20, 30, 40]
    events = [0, 0, 0, 0]
    F, lo, hi, n_ev = km_arrival_probability(durations, events, horizon=30)
    assert F is None, f"expected None for a zero-event cohort, got {F}"
    assert n_ev == 0


def t_i3_TRIPWIRE_zero_event_cohort_cannot_become_a_measured_reading():
    """
    F=0.0 from an empty curve is indistinguishable in a payload from a real
    'nothing ever moves'. Reading must refuse to wear the measured badge.
    """
    raised = False
    try:
        Reading(state=State.MEASURED, cohort="c", horizon_days=30,
                value=0.0, n_events=0)
    except ValueError:
        raised = True
    assert raised, "MEASURED Reading accepted n_events=0 — I3 guard is dead"


def t_km_survival_is_monotone():
    durations = [1, 2, 2, 3, 5, 8, 8, 13]
    events = [1, 1, 0, 1, 0, 1, 1, 0]
    pts = kaplan_meier(durations, events)
    survs = [p.survival for p in pts]
    assert all(survs[i] >= survs[i + 1] for i in range(len(survs) - 1)), survs


def t_km_ci_brackets_the_estimate():
    durations = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    events = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    F, lo, hi, _ = km_arrival_probability(durations, events, horizon=14)
    assert F is not None and lo is not None and hi is not None
    assert 0.0 <= lo <= F <= hi <= 1.0, f"CI does not bracket: {lo} {F} {hi}"


# ===========================================================================
# I5 — credibility
# ===========================================================================

def t_i5_credibility_collapses_when_cells_do_not_separate():
    """
    All cells share the same underlying rate -> VHM ~ 0 -> K -> inf -> Z -> 0,
    and every cell must read the portfolio base rate. This is the graceful
    degradation that replaces a suppression threshold.
    """
    exposure = {f"c{i}": 1000.0 for i in range(8)}
    events = {f"c{i}": 100.0 for i in range(8)}      # identical 10% everywhere
    res = buhlmann_straub(events, exposure)
    assert res.degenerate, "identical cells did not register as degenerate"
    assert all(abs(z) < 1e-9 for z in res.z.values()), res.z
    assert all(approx(v, res.mu, 1e-9) for v in res.blended.values())


def t_i5_TRIPWIRE_credibility_is_not_always_zero():
    """
    If Z were always 0 the collapse test above would pass vacuously — exactly
    the `total <= 3` failure mode. Well-separated, well-exposed cells must
    produce substantial credibility.
    """
    exposure = {"a": 50000.0, "b": 50000.0, "c": 50000.0, "d": 50000.0}
    events = {"a": 500.0, "b": 5000.0, "c": 12500.0, "d": 25000.0}  # 1%..50%
    res = buhlmann_straub(events, exposure)
    assert not res.degenerate, "well-separated cells registered as degenerate"
    assert max(res.z.values()) > 0.5, f"Z never rose above 0.5: {res.z}"


def t_i5_negative_vhm_is_handled_not_raised():
    """Negative VHM is a normal finite-sample outcome on noisy data."""
    exposure = {"a": 10.0, "b": 10.0}
    events = {"a": 5.0, "b": 5.0}
    res = buhlmann_straub(events, exposure)
    assert res.vhm >= 0.0
    assert res.k is None or res.k > 0


def t_i5_empty_input_does_not_crash():
    res = buhlmann_straub({}, {})
    assert res.degenerate and res.z == {}


# ===========================================================================
# Calibration — Murphy decomposition
# ===========================================================================

def t_murphy_identity_holds():
    """
    BS = REL - RES + UNC + within_bin, exactly.

    The three-term form is exact only for forecasts binned by exact value. The
    first version of this test asserted the three-term identity on continuous
    forecasts and failed by -0.00126 — which turned out to equal BS_raw minus
    BS_binned to the last digit. The gap is the binning artifact, so it is
    reported as a fourth term rather than absorbed by a wider tolerance.
    """
    import random
    random.seed(7)
    fc = [random.random() for _ in range(500)]
    ob = [1 if random.random() < p else 0 for p in fc]
    t = murphy_decomposition(fc, ob, n_bins=10)
    assert abs(t.identity_residual()) < 1e-12, t.identity_residual()
    assert abs(t.within_bin) > 1e-6, (
        "within_bin is ~0 on continuous forecasts — the binning term is not "
        "being computed"
    )


def t_murphy_TRIPWIRE_binning_term_vanishes_on_discrete_forecasts():
    """
    The complement: when every forecast already sits at a bin centre there is
    no within-bin scatter, so the classical three-term identity must hold
    exactly. If within_bin were hard-coded non-zero this would fail.
    """
    fc = [0.05] * 100 + [0.95] * 100
    ob = [1] * 5 + [0] * 95 + [1] * 95 + [0] * 5
    t = murphy_decomposition(fc, ob, n_bins=10)
    assert abs(t.within_bin) < 1e-12, t.within_bin
    assert abs(t.brier - t.brier_binned) < 1e-12


def t_murphy_TRIPWIRE_bss_does_not_move_with_bin_count():
    """
    The served skill number must not depend on a free parameter chosen by the
    party reporting it. 1 - BS/UNC is binning-independent; (RES-REL)/UNC is not.
    """
    import random
    random.seed(11)
    fc = [random.random() for _ in range(400)]
    ob = [1 if random.random() < p else 0 for p in fc]
    scores = {b: brier_skill_score(murphy_decomposition(fc, ob, n_bins=b))
              for b in (4, 10, 20, 50)}
    vals = list(scores.values())
    assert all(v is not None for v in vals)
    assert max(vals) - min(vals) < 1e-12, f"BSS moved with bin count: {scores}"


def t_murphy_calibrated_but_useless_is_representable():
    """
    The central claim of the design: a forecast can be perfectly calibrated and
    carry no information. REL ~ 0, RES ~ 0, BS ~ UNC. That state is honest, not
    fraudulent, and the instrument must be able to say so.
    """
    base = 0.2
    n = 1000
    fc = [base] * n
    ob = [1] * int(base * n) + [0] * (n - int(base * n))
    t = murphy_decomposition(fc, ob, n_bins=10)
    assert approx(t.reliability, 0.0, 1e-9), t.reliability
    assert approx(t.resolution, 0.0, 1e-9), t.resolution
    assert approx(t.brier, t.uncertainty, 1e-9)
    bss = brier_skill_score(t)
    assert bss is not None and approx(bss, 0.0, 1e-9), bss


def t_murphy_TRIPWIRE_discriminating_forecast_scores_skill():
    """If BSS were always ~0 the test above would be vacuous."""
    fc = [0.9] * 100 + [0.1] * 100
    ob = [1] * 90 + [0] * 10 + [1] * 10 + [0] * 90
    t = murphy_decomposition(fc, ob, n_bins=10)
    bss = brier_skill_score(t)
    assert bss is not None and bss > 0.5, f"expected real skill, got BSS={bss}"


def t_brier_skill_undefined_when_uncertainty_zero():
    t = murphy_decomposition([0.5] * 10, [1] * 10)
    assert brier_skill_score(t) is None, "BSS must be None, not 0, when UNC=0"


# ===========================================================================
# Non-circularity — and a tripwire on the scanner itself
# ===========================================================================

_WRITE_RE = re.compile(
    r"\b(INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|DROP\s+TABLE|"
    r"TRUNCATE|CREATE\s+TABLE|ALTER\s+TABLE)\b",
    re.IGNORECASE,
)

_AGENT_FILES = (
    "probability_core.py",
    "trend_probability_agent.py",
    "market_flow_probability_agent.py",
    "crypto_flow_probability_agent.py",
)


def _scan_for_writes(text: str) -> List[str]:
    """Return every write-shaped statement found outside comments."""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if _WRITE_RE.search(line):
            hits.append(f"line {i}: {stripped[:80]}")
    return hits


def t_noncircularity_agents_contain_no_writes():
    here = os.path.dirname(os.path.abspath(__file__))
    for fname in _AGENT_FILES:
        with open(os.path.join(here, fname), "r", encoding="utf-8") as fh:
            hits = _scan_for_writes(fh.read())
        assert not hits, f"{fname} contains write statements: {hits}"


def t_noncircularity_TRIPWIRE_scanner_catches_a_planted_write():
    """
    The tripwire on the tripwire. A grep-based enforcer that cannot be shown to
    fail is not an enforcer — that is the exact lesson from the register review,
    where a claim passed because its own name appeared in a comment.
    """
    fixture = "x = 1\nsql = 'INSERT INTO velocity_scores VALUES (1)'\n"
    hits = _scan_for_writes(fixture)
    assert hits, "scanner did not catch a planted INSERT — the guard is decoration"

    fixture2 = "sql = 'UPDATE velocity_scores SET detection = 99'\n"
    assert _scan_for_writes(fixture2), "scanner missed a planted UPDATE"

    # And it must NOT fire on a comment, or it would be unusable.
    fixture3 = "# we never INSERT INTO anything here\n"
    assert not _scan_for_writes(fixture3), "scanner fired on a comment"


# ===========================================================================
# CFTC COT knowable_at rule
# ===========================================================================

def t_cot_tuesday_maps_to_friday():
    assert cot_knowable_at(_dt.date(2026, 8, 18)) == _dt.date(2026, 8, 21)


def t_cot_TRIPWIRE_non_tuesday_is_refused():
    """
    Refusing is the point. Guessing a publication date back-dates knowledge by
    up to three days and contaminates every point-in-time read downstream.
    """
    for bad in (_dt.date(2026, 8, 17), _dt.date(2026, 8, 21)):  # Mon, Fri
        raised = False
        try:
            cot_knowable_at(bad)
        except ValueError:
            raised = True
        assert raised, f"accepted a non-Tuesday as-of date: {bad}"


def t_cot_row_validation_rejects_backdated_knowable_at():
    agent = CryptoFlowProbabilityAgent(fetch=lambda *_: [])
    good = {"report_date_as_yyyy_mm_dd": "2026-08-18", "knowable_at": "2026-08-21"}
    bad = {"report_date_as_yyyy_mm_dd": "2026-08-18", "knowable_at": "2026-08-18"}
    assert agent._cot_row_is_knowable(good, "2026-08-25")
    assert not agent._cot_row_is_knowable(bad, "2026-08-25"), \
        "accepted a Tuesday-stamped knowable_at — the back-dating guard is dead"
    # Also must reject a row not yet knowable as of the requested date.
    assert not agent._cot_row_is_knowable(good, "2026-08-20")


# ===========================================================================
# Crypto — the money leg is NOT_APPLICABLE by construction
# ===========================================================================

def t_crypto_money_leg_is_not_applicable_by_default():
    agent = CryptoFlowProbabilityAgent(fetch=lambda *_: [])
    r = agent.score("BTC", as_of="2026-08-21")
    assert r.money_inflow.state is State.NOT_APPLICABLE
    assert r.money_outflow.state is State.NOT_APPLICABLE
    assert r.money_inflow.value is None
    p = r.to_payload()
    assert p["money_leg_available"] is False
    assert "attention" in p["conditioned_on"]
    assert "cftc_cot_positioning" not in p["conditioned_on"]


def t_crypto_TRIPWIRE_money_leg_cannot_be_enabled_without_a_provider():
    """enable_cot=True with no provider must NOT flip the leg on."""
    agent = CryptoFlowProbabilityAgent(fetch=lambda *_: [], enable_cot=True)
    assert agent.enable_cot is False, \
        "COT enabled with no provider — a flag alone turned on a source"
    r = agent.score("BTC", as_of="2026-08-21")
    assert r.money_inflow.state is State.NOT_APPLICABLE


def t_crypto_unmapped_coin_is_not_applicable_even_with_cot():
    agent = CryptoFlowProbabilityAgent(
        fetch=lambda *_: [], cot_provider=lambda c, a: None, enable_cot=True)
    r = agent.score("DOGE", as_of="2026-08-21")
    assert r.money_inflow.state is State.NOT_APPLICABLE
    assert "no CME futures contract" in (r.money_inflow.reason or "")


def t_crypto_contract_codes_present():
    assert COT_CONTRACT_CODES["BTC"] == "133741"
    assert COT_CONTRACT_CODES["ETH"] == "146021"


# ===========================================================================
# Market — R7 exclusion and macro degradation
# ===========================================================================

def t_market_r7_exclusions_are_declared():
    agent = MarketFlowProbabilityAgent(fetch=lambda *_: [])
    r = agent.score("Technology", as_of="2026-08-21")
    excl = r.to_payload()["excluded_by_ruling"]
    assert any("R7" in e for e in excl)
    assert any("congress" in e.lower() for e in excl)
    assert any("13f" in e.lower() for e in excl)


def t_market_TRIPWIRE_congress_never_enters_a_cohort_key():
    """R7 set DARK_POS_WEIGHT=0. Nothing here may resurrect that blend."""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "market_flow_probability_agent.py"),
              encoding="utf-8") as fh:
        src = fh.read()
    # Find the cohort key construction and prove congress/13F are absent from it.
    key_region = src[src.index("class MarketCohort"):src.index("def insider_band")]
    for banned in ("congress", "quiver", "13f", "whalewisdom"):
        assert banned not in key_region.lower(), \
            f"'{banned}' appears in the cohort key region — R7 has been reversed"


def t_market_macro_failure_degrades_not_fabricates():
    def boom(_as_of):
        raise RuntimeError("FRED unreachable")

    agent = MarketFlowProbabilityAgent(fetch=lambda *_: [], macro_provider=boom)
    r = agent.score("Technology", as_of="2026-08-21")
    assert r.macro.rates_regime is None, "a macro outage fabricated a regime"
    assert r.macro.complete is False
    assert r.macro.key == "UNKNOWN/UNKNOWN"


def t_market_macro_classifiers():
    assert classify_rates(0.40) == "RISING"
    assert classify_rates(-0.40) == "FALLING"
    assert classify_rates(0.0) == "FLAT"
    assert classify_rates(None) is None
    assert classify_credit(0.9) == "WIDE"
    assert classify_credit(0.1) == "TIGHT"
    assert classify_credit(0.5) == "NORMAL"
    assert classify_credit(None) is None


# ===========================================================================
# End-to-end on an in-memory SQLite fixture
# ===========================================================================

def _make_trend_db() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE topic_lifecycle (topic_key TEXT, maturity_class TEXT,
                                      first_seen TEXT);
        CREATE TABLE raw_signals (topic_key TEXT, source_name TEXT,
                                  platform_tier TEXT, signal_date TEXT);
        CREATE TABLE accuracy_ledger_enhanced (
            topic_key TEXT, detection_date TEXT, breakout_date TEXT,
            verdict TEXT, pre_broken INTEGER, d_measured INTEGER);
        CREATE TABLE velocity_scores (topic_key TEXT, signal_date TEXT,
                                      stage TEXT);
        """
    )
    # target topic
    cur.execute("INSERT INTO topic_lifecycle VALUES ('agentic coding','EMERGING','2026-06-01')")
    for src in ("github", "hn", "devto"):
        cur.execute("INSERT INTO raw_signals VALUES ('agentic coding',?,'expert','2026-07-01')",
                    (src,))
    # cohort: 12 comparable topics, 5 arrived, 7 still pending
    for i in range(12):
        tk = f"peer{i}"
        cur.execute("INSERT INTO topic_lifecycle VALUES (?,'EMERGING','2026-05-01')", (tk,))
        for src in ("a", "b", "c"):
            cur.execute("INSERT INTO raw_signals VALUES (?,?,'expert','2026-06-01')", (tk, src))
        if i < 5:
            cur.execute(
                "INSERT INTO accuracy_ledger_enhanced VALUES (?,?,?,?,0,1)",
                (tk, "2026-06-01", f"2026-06-{10 + i:02d}", "LED"))
        else:
            cur.execute(
                "INSERT INTO accuracy_ledger_enhanced VALUES (?,?,NULL,'PENDING',0,1)",
                (tk, "2026-06-01"))
    # one UNKNOWN-measurement row that must be excluded, not treated as blind
    cur.execute("INSERT INTO topic_lifecycle VALUES ('ghost','EMERGING','2026-05-01')")
    for src in ("a", "b", "c"):
        cur.execute("INSERT INTO raw_signals VALUES ('ghost',?,'expert','2026-06-01')", (src,))
    cur.execute("INSERT INTO accuracy_ledger_enhanced VALUES "
                "('ghost','2026-06-01','2026-06-05','LED',0,NULL)")
    con.commit()
    return con


def _fetch_for(con: sqlite3.Connection):
    def fetch(sql: str, params: Sequence):
        cur = con.cursor()
        cur.execute(sql, tuple(params))
        return [dict(r) for r in cur.fetchall()]
    return fetch


def t_e2e_trend_returns_measured_reading():
    con = _make_trend_db()
    agent = TrendProbabilityAgent(fetch=_fetch_for(con))
    out = agent.score("agentic coding", as_of="2026-08-21", horizon_days=30)
    assert out.cohort is not None, "cohort not resolved"
    assert out.rise.state is State.MEASURED, out.rise.reason
    assert out.rise.value is not None and 0.0 < out.rise.value <= 1.0
    # 6, not 5: the 'ghost' row (d_measured NULL) now ENTERS the cohort —
    # the round-7 I2 scope fix. The key has no D factor, so D-measurement
    # status cannot gate membership.
    assert out.rise.n_events == 6, out.rise.n_events
    p = out.to_payload()
    assert p["rise"]["probability"] is not None
    assert "historical frequency" in p["rise"]["note"].lower()


def t_e2e_TRIPWIRE_unknown_rows_counted_not_excluded():
    """ROUND-7 REVERSAL of the original tripwire (the conceded I2 category
    error). The 'ghost' row has d_measured NULL and an arrival. The cohort key
    (maturity x corroboration x provenance) contains NO D-derived factor, so
    the row must ENTER the cohort — excluding it discarded 100% of usable
    history (the live stamp is NULL on every resolved race) for an estimand
    that never consults D. What survives is COVERAGE ACCOUNTING: the UNKNOWN
    row is counted in excluded_unmeasured so that if a D factor ever enters
    the key, the exclusion re-arms against known coverage."""
    con = _make_trend_db()
    agent = TrendProbabilityAgent(fetch=_fetch_for(con))
    out = agent.score("agentic coding", as_of="2026-08-21", horizon_days=30)
    assert out.excluded_unmeasured == 1, (
        f"expected 1 UNKNOWN row counted, got {out.excluded_unmeasured} — "
        f"coverage accounting is not firing"
    )
    assert out.rise.n_events == 6, (
        "the UNKNOWN row was excluded from a cohort with no D factor — "
        "the I2 category error has been reintroduced"
    )
    assert out.to_payload()["excluded_unmeasured"] == 1


def t_e2e_trend_decay_leg_is_absent_when_no_decay_observed():
    con = _make_trend_db()   # no velocity_scores rows at all
    agent = TrendProbabilityAgent(fetch=_fetch_for(con))
    out = agent.score("agentic coding", as_of="2026-08-21", horizon_days=30)
    assert out.decay.state is State.ABSENT
    assert out.decay.value is None
    assert "no observed" in (out.decay.reason or "").lower()


def t_e2e_trend_unknown_topic_is_absent_not_zero():
    con = _make_trend_db()
    agent = TrendProbabilityAgent(fetch=_fetch_for(con))
    out = agent.score("never seen before", as_of="2026-08-21")
    assert out.rise.state is State.ABSENT and out.rise.value is None
    assert out.cohort is None


def t_e2e_payload_has_no_contradictory_pair():
    """
    The 2026-08-20 production incident was one payload asserting d_measured
    false beside prose saying the signal originates publicly. Structurally
    impossible here: `probability` derives from the same object as `state`.
    """
    con = _make_trend_db()
    agent = TrendProbabilityAgent(fetch=_fetch_for(con))
    for topic in ("agentic coding", "never seen before"):
        p = agent.score(topic, as_of="2026-08-21").to_payload()
        for leg in ("rise", "decay"):
            block = p[leg]
            if block["state"] != "MEASURED":
                assert block["probability"] is None, (
                    f"{leg} is {block['state']} but carries "
                    f"probability={block['probability']}")
                assert block["reason"], f"{leg} is {block['state']} with no reason"
            else:
                assert block["probability"] is not None
                assert block["n_events"] > 0


# ===========================================================================
# ROUND 7 — the ratified fixes, each with a violating fixture
# ===========================================================================

def t_r7_TRIPWIRE_z_cap_binds_to_information():
    """Uncapped member-day Z read 0.996 on TWO events — 23x over the
    limited-fluctuation bound sqrt(events/1082). The cap must bind."""
    import math
    from probability_core import z_cap
    capped = z_cap(0.996, 2)
    assert approx(capped, math.sqrt(2 / 1082.0), 1e-12), capped
    assert z_cap(0.5, 0) == 0.0, "zero events must yield zero credibility"
    assert z_cap(0.01, 5000) == 0.01, "the cap must not bind below it"
    assert z_cap(-0.3, 100) == 0.0, "negative Z must floor at 0"


def t_r7_TRIPWIRE_horizon_capped_event_count():
    """Two events at t=40,50 with horizon 30: the old n_events counted them
    and let a MEASURED F(30)=0.000 serve. They are beyond the horizon —
    n_events must be 0 so the agent path reads ABSENT, not zero."""
    F, lo, hi, n_ev = km_arrival_probability([40.0, 50.0], [1, 1], 30)
    assert n_ev == 0, (
        f"n_events={n_ev}: beyond-horizon events counted — the I3 defeat "
        f"(MEASURED 0.000 on late events) is back"
    )


def t_r7_TRIPWIRE_a2_side_fields_guarded():
    """An ABSENT Reading once served raw_rate=0.42, base_rate=0.87 — only
    value/ci/credibility were guarded. The side channels must raise too."""
    for field_name, val in (("raw_rate", 0.42), ("base_rate", 0.87)):
        raised = False
        try:
            Reading(state=State.ABSENT, cohort="c", horizon_days=30,
                    reason="no data", **{field_name: val})
        except ValueError:
            raised = True
        assert raised, f"ABSENT Reading accepted {field_name}={val} — A2 leak"


def t_r7_TRIPWIRE_lagged_rows_counted_not_silently_dropped():
    """A LAGGED row (breakout BEFORE detection) used to hit `continue` with no
    counter — RISE_VERDICTS' 'LAGGED' entry was dead code and the fast-arrival
    topics vanished from both sides of the fraction. It stays outside the risk
    set (negative duration) but must be COUNTED and served."""
    con = _make_trend_db()
    cur = con.cursor()
    cur.execute("INSERT INTO topic_lifecycle VALUES ('nearmiss','EMERGING','2026-05-01')")
    for src in ("a", "b", "c"):
        cur.execute("INSERT INTO raw_signals VALUES ('nearmiss',?,'expert','2026-06-01')", (src,))
    # breakout two days BEFORE detection — the near-miss shape
    cur.execute("INSERT INTO accuracy_ledger_enhanced VALUES "
                "('nearmiss','2026-06-10','2026-06-08','LAGGED',0,1)")
    con.commit()
    agent = TrendProbabilityAgent(fetch=_fetch_for(con))
    out = agent.score("agentic coding", as_of="2026-08-21", horizon_days=30)
    assert out.lagged_excluded == 1, (
        f"lagged_excluded={out.lagged_excluded}: the LAGGED row was dropped "
        f"through the uncounted door again"
    )
    assert out.to_payload()["lagged_excluded"] == 1


def t_r7_TRIPWIRE_coherence_violation_served_not_clamped():
    """rise and decay are two marginal 1-KM curves; their sum can exceed 1.
    The old code clamped flat at 0, HIDING it. When the sum exceeds 1 the
    readout must flag coherence_violated and refuse a flat estimate."""
    con = _make_trend_db()
    cur = con.cursor()
    # every enrolled topic decays fast -> P(DECAY|30) ~ 1.0 while 6 of 13 rise
    for i in range(12):
        cur.execute("INSERT INTO velocity_scores VALUES (?,?,'DECAY')",
                    (f"peer{i}", "2026-06-06"))
    cur.execute("INSERT INTO velocity_scores VALUES ('ghost','2026-06-06','DECAY')")
    con.commit()
    agent = TrendProbabilityAgent(fetch=_fetch_for(con))
    out = agent.score("agentic coding", as_of="2026-08-21", horizon_days=30)
    assert out.rise.state is State.MEASURED and out.decay.state is State.MEASURED
    total = (out.rise.value or 0) + (out.decay.value or 0)
    assert total > 1.0, f"fixture failed to construct incoherence (sum={total})"
    assert out.coherence_violated is True, (
        "rise+decay > 1 rendered without the coherence flag — the clamp is "
        "hiding the competing-risks bias again"
    )
    assert out.flat_estimate is None, "a flat residual was fabricated from an incoherent pair"
    assert out.to_payload()["coherence_violated"] is True


def t_r7_TRIPWIRE_instrument_error_is_not_absent():
    """Error-to-ABSENT laundering (three seats): a broken query used to serve
    'no comparable history' — a fabricated reason on an instrument fault, an
    invisible outage. All three agents must serve INSTRUMENT_ERROR instead."""
    def broken_fetch(sql, params):
        raise RuntimeError("no such column: totally_missing")

    t = TrendProbabilityAgent(fetch=broken_fetch).score("x", as_of="2026-08-21")
    assert t.rise.state is State.INSTRUMENT_ERROR, t.rise.state
    assert "failed" in (t.rise.reason or ""), t.rise.reason

    m = MarketFlowProbabilityAgent(fetch=broken_fetch).score(
        "Technology", as_of="2026-08-21")
    assert m.inflow_move.state is State.INSTRUMENT_ERROR, m.inflow_move.state

    c = CryptoFlowProbabilityAgent(fetch=broken_fetch).score(
        "BTC", as_of="2026-08-21")
    assert c.up_move.state is State.INSTRUMENT_ERROR, c.up_move.state
    # the money legs remain NOT_APPLICABLE — the source-set fact is unchanged
    # by our query being broken
    assert c.money_inflow.state is State.NOT_APPLICABLE


def t_r7_TRIPWIRE_a5_money_leg_available_derives_from_leg_states():
    """money_leg_available used to flip on the CONSTRUCTOR FLAG while the legs
    read ABSENT/NOT_APPLICABLE — two fields in one payload disagreeing (the
    2026-08-20 incident class). It must derive from the actual leg states, and
    conditioned_on must never list COT (it enters no cohort key anywhere)."""
    def cot_provider(coin, as_of):
        return {"report_date_as_yyyy_mm_dd": "2026-08-18",   # a Tuesday
                "knowable_at": "2026-08-21"}                 # its Friday

    agent = CryptoFlowProbabilityAgent(
        fetch=lambda *_: [], cot_provider=cot_provider, enable_cot=True)
    p = agent.score("BTC", as_of="2026-08-21").to_payload()
    assert p["money_inflow"]["state"] != "MEASURED"
    assert p["money_leg_available"] is False, (
        "money_leg_available=True while the money legs measured nothing — "
        "the A5 contradiction is back"
    )
    assert "cftc_cot_positioning" not in p["conditioned_on"], (
        "conditioned_on claims COT, which enters no cohort key in this module"
    )
    assert p["cot_wired"] is True   # instrumentation status stays visible


def t_r7_TRIPWIRE_a10_sources_omitted_when_nothing_contributed():
    """§17: an ABSENT reading must not sit above a list naming
    Finviz/FINRA/OFR/FMP — nothing contributed to a read that does not exist."""
    agent = MarketFlowProbabilityAgent(fetch=lambda *_: [])
    r = agent.score("Technology", as_of="2026-08-21")
    assert r.inflow_move.state is State.ABSENT
    assert r.money_leg_sources == [], (
        f"ABSENT reading served sources {r.money_leg_sources} — §17 violation"
    )


def t_r7_plain_english_denominator_is_the_cohorts():
    """Four seats: 'Of N items, X% moved' where X was the BLEND attributed a
    mostly-portfolio number to the cohort. The cohort's number must be
    raw_rate; the blend must be labeled as a blend."""
    r = Reading(state=State.MEASURED, cohort="c", horizon_days=30,
                value=0.30, ci_low=0.1, ci_high=0.6, n_cohort=8, n_events=2,
                credibility=0.04, raw_rate=0.25, base_rate=0.31)
    s = r.plain_english()
    assert "25% moved" in s, s                       # the cohort owns raw_rate
    assert "Served estimate 30%" in s, s             # the blend labeled as blend
    assert "portfolio rate 31%" in s, s
    assert "95%" not in s, "the mixture band is being mislabeled a 95% CI again"
    assert "too thin" in s, "z<0.30 must carry the thin-cohort warning"


# ===========================================================================

def main() -> int:
    print("\nprobability agents — tests and tripwires\n" + "=" * 60)
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("t_") and callable(f)]
    for name, fn in tests:
        check(name, fn)

    print("=" * 60)
    trip = sum(1 for n, _ in tests if "TRIPWIRE" in n)
    print(f"{_PASSES} passed, {len(_FAILS)} failed "
          f"({len(tests)} total, {trip} tripwires)")
    if _FAILS:
        print("\nFAILURES:")
        for f in _FAILS:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
