"""
probability_core.py — shared statistical core for the Base Rate agents.

=============================================================================
HELD OUT.  Nothing in this module, and nothing that imports it, may write to
`velocity_scores`, `serve_payload`, or any other scoring table.  These agents
MEASURE; they never SCORE.  Non-circularity (master CLAUDE.md §13) is the
reason this file contains no writer of any kind.
=============================================================================

WHAT THIS IS
------------
A frequency instrument, not a forecaster.  It answers:

    "Of the items that historically looked like this one at the same point in
     their lifecycle, what fraction subsequently moved, and when?"

It does NOT answer "will this one move?"  The FIFA World Cup case study
settled that guessing is speculative; stating the frequency in a risk class is
what insurers actually do, and it is measurable from the ledgers we already
hold.

THE FIVE INVARIANTS (each has a tripwire test that fails if it is broken)
------------------------------------------------------------------------
I1  A non-MEASURED Reading carries value=None.  Never 0.0.
    Origin: `compute_dark_matter` returned 0.0 for "could not read" while its
    own docstring called 0 "the neutral value".  On a 0-100 scale 0 is the
    FLOOR, not neutral (§15a-A3).  Enforced structurally in Reading.

I2  Measurement status is TRI-state, not boolean.
    YES / BLIND / UNKNOWN.  Origin: `d_measured` was added by migration with no
    backfill, so historical rows hold NULL; `None != 0` is True and
    `None == 0` is False, so a two-branch reader silently narrates NULL rows as
    measured-and-quiet.  See classify_measured().

I3  Zero observed events => ABSENT, never 0%.
    Kaplan-Meier on a cohort with no events returns S(t)=1 for all t, so
    F(t)=0.  That zero is the same fabricated floor as I1 wearing a survival
    curve.

I4  Censoring is handled by Kaplan-Meier, never by dropping or by coding
    pending as non-events.  Those two shortcuts bias in OPPOSITE directions and
    neither is consistent.

I5  Sparse cohorts are handled by credibility, never by a suppression
    threshold.  If the rating factors do not separate outcomes, VHM -> 0,
    Z -> 0, and the estimate correctly collapses to the portfolio base rate
    instead of producing a confident number from twelve observations.

Author: Now TrendIn engine.  Python 3.9+, stdlib only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

__all__ = [
    "State",
    "Measured",
    "classify_measured",
    "Reading",
    "absent",
    "not_applicable",
    "KMPoint",
    "kaplan_meier",
    "km_arrival_probability",
    "buhlmann_straub",
    "CredibilityResult",
    "murphy_decomposition",
    "MurphyTerms",
    "brier_skill_score",
    "Fetch",
    "Z_95",
]

# 95% two-sided normal quantile.
Z_95 = 1.959963984540054

# A read-only query callable.  Must accept (sql, params) with `?` placeholders
# and return a list of dict-like rows.  Wire it to db_compat at the call site;
# db_compat translates `?` -> `%s` for Postgres.
Fetch = Callable[[str, Sequence], List[dict]]


# ---------------------------------------------------------------------------
# I1 / I2 — states
# ---------------------------------------------------------------------------

class State(str, Enum):
    """Serving state of a Reading."""

    MEASURED = "MEASURED"          # a real number, computed from real events
    ABSENT = "ABSENT"              # could be measured, but the data is not there
    NOT_APPLICABLE = "NOT_APPLICABLE"  # cannot be measured — no such input exists
    # Round-7 board (three seats independently): a broken query must NEVER wear the
    # honest-absence badge. Every fetch was `except: return []`, so invalid SQL served
    # "no comparable history for this cohort" — a fabricated reason on an instrument
    # fault. On deploy day the schema mismatch would have served ABSENT everywhere and
    # nobody would have known it was an outage. ABSENT is a fact about the WORLD;
    # INSTRUMENT_ERROR is a fact about US, and the two must never share a costume.
    INSTRUMENT_ERROR = "INSTRUMENT_ERROR"

    def __str__(self) -> str:  # keeps f-strings readable in payloads
        return self.value


class Measured(str, Enum):
    """
    I2 — the tri-state.  Collapsing this to a boolean is the `d_measured IS
    NULL` defect: a two-branch reader narrates never-measured rows as
    measured-and-quiet.
    """

    YES = "yes"          # measured, a reading exists
    BLIND = "blind"      # measured, nothing was there
    UNKNOWN = "unknown"  # never measured (NULL / pre-migration / not stamped)

    def __str__(self) -> str:
        return self.value


def classify_measured(raw: object) -> Measured:
    """
    Map a raw DB value to the tri-state.

    NULL/None       -> UNKNOWN   (never measured; NOT the same as "measured 0")
    0 / False / "0" -> BLIND
    anything else   -> YES

    >>> classify_measured(None) is Measured.UNKNOWN
    True
    >>> classify_measured(0) is Measured.BLIND
    True
    >>> classify_measured(1) is Measured.YES
    True
    """
    if raw is None:
        return Measured.UNKNOWN
    if isinstance(raw, bool):
        return Measured.YES if raw else Measured.BLIND
    if isinstance(raw, (int, float)):
        return Measured.BLIND if raw == 0 else Measured.YES
    if isinstance(raw, str):
        s = raw.strip().lower()
        if s in ("", "null", "none"):
            return Measured.UNKNOWN
        if s in ("0", "false", "f", "no"):
            return Measured.BLIND
        return Measured.YES
    return Measured.YES


@dataclass(frozen=True)
class Reading:
    """
    One served probability, or an honest statement that there isn't one.

    I1 is enforced in __post_init__: if state is not MEASURED, `value`,
    `ci_low`, `ci_high` and `credibility` must all be None.  Constructing
    Reading(state=ABSENT, value=0.0) raises.  That is the whole point — the
    defect it prevents shipped to production once already.
    """

    state: State
    cohort: str
    horizon_days: int
    value: Optional[float] = None        # P(event within horizon), 0..1
    ci_low: Optional[float] = None
    ci_high: Optional[float] = None
    n_cohort: int = 0                    # members of the cohort
    n_events: int = 0                    # OBSERVED events — the credibility unit
    exposure: float = 0.0                # member-days at risk
    credibility: Optional[float] = None  # Buhlmann-Straub Z, 0..1
    raw_rate: Optional[float] = None     # cell's own rate before credibility blend
    base_rate: Optional[float] = None    # portfolio rate blended toward
    reason: Optional[str] = None         # required when not MEASURED
    as_of: Optional[str] = None          # point-in-time stamp (ISO date)

    def __post_init__(self) -> None:
        if self.state is State.MEASURED:
            if self.value is None:
                raise ValueError("MEASURED Reading must carry a value (I1)")
            if not (0.0 <= self.value <= 1.0):
                raise ValueError(f"probability out of range: {self.value}")
            if self.n_events <= 0:
                # I3 — a curve with no events yields F(t)=0, which is the
                # fabricated floor, not a measurement.
                raise ValueError("MEASURED Reading requires n_events > 0 (I3)")
        else:
            # A2 (round-7 Forecaster): the original guard covered only value/ci/
            # credibility, so an ABSENT Reading could carry raw_rate=0.42 and
            # base_rate=0.87 straight into the payload — numbers beside a
            # non-MEASURED state, the 2026-08-20 incident class through a side door.
            for field_name in ("value", "ci_low", "ci_high", "credibility",
                               "raw_rate", "base_rate"):
                if getattr(self, field_name) is not None:
                    raise ValueError(
                        f"{self.state} Reading must carry {field_name}=None, "
                        f"got {getattr(self, field_name)!r} (I1/A2)"
                    )
            if not self.reason:
                raise ValueError(f"{self.state} Reading must carry a reason")

    # -- serving ------------------------------------------------------------

    def to_payload(self) -> dict:
        """
        The dict served to the API.  Note there is no branch that can emit a
        number in a non-MEASURED state: `value` is already None by invariant,
        so the payload cannot contradict its own state field.  (The production
        incident of 2026-08-20 was two fields in one payload disagreeing.)
        """
        return {
            "state": str(self.state),
            "cohort": self.cohort,
            "horizon_days": self.horizon_days,
            "probability": self.value,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "n_cohort": self.n_cohort,
            "n_events": self.n_events,
            "credibility": self.credibility,
            "raw_rate": self.raw_rate,
            "base_rate": self.base_rate,
            "reason": self.reason,
            "as_of": self.as_of,
            "note": self.plain_english(),
        }

    def plain_english(self) -> str:
        # ROUND-7, FOUR SEATS INDEPENDENTLY: the old sentence read "Of N items that
        # matched this profile, X% moved" where X was the BLENDED value — mostly the
        # portfolio rate at any realistic Z. The grammar attributed a mostly-
        # climatology number entirely to the cohort: those N items did NOT move at
        # that rate; raw_rate did. The reference class must be the subject of the
        # sentence AND the number's provenance must be part of the subject. The
        # cohort's number is now the cohort's; the blend is labeled as a blend.
        # The old band was also printed as "95% CI", which the mixture is not.
        if self.state is State.MEASURED:
            raw = 100.0 * (self.raw_rate if self.raw_rate is not None
                           else (self.value or 0.0))
            served = 100.0 * (self.value or 0.0)
            base = 100.0 * (self.base_rate if self.base_rate is not None else 0.0)
            z = self.credibility if self.credibility is not None else 0.0
            return (
                f"Of {self.n_cohort} enrolled items in this class, {raw:.0f}% moved "
                f"within {self.horizon_days} days ({self.n_events} observed moves). "
                f"Served estimate {served:.0f}% after blending with the portfolio "
                f"rate {base:.0f}% at credibility {z:.2f}"
                + (" — this cohort is too thin to separate; the served figure is "
                   "mostly the portfolio rate" if z < 0.30 else "")
                + ". Historical frequency of our own enrolled set, not a forecast."
            )
        return f"{self.state} — {self.reason}"


def absent(cohort: str, horizon_days: int, reason: str, *,
           n_cohort: int = 0, n_events: int = 0, as_of: Optional[str] = None) -> Reading:
    """Honest absence: the measurement is possible but the data is not there."""
    return Reading(
        state=State.ABSENT, cohort=cohort, horizon_days=horizon_days,
        n_cohort=n_cohort, n_events=n_events, reason=reason, as_of=as_of,
    )


def instrument_error(cohort: str, horizon_days: int, reason: str,
                     *, as_of: Optional[str] = None) -> Reading:
    """
    The instrument failed — a query errored, a schema mismatched, a provider threw.
    This is a fact about US, never about the world, and it must not be narrated as
    "no data exists". Round-7 origin: every fetch was `except: return []`, so twelve
    invalid queries would have served plausible honest-absence reasons on production
    and the outage would have been invisible.
    """
    return Reading(
        state=State.INSTRUMENT_ERROR, cohort=cohort, horizon_days=horizon_days,
        reason=reason, as_of=as_of,
    )


def z_cap(z: float, n_events: int) -> float:
    """
    Limited-fluctuation cap on the credibility weight: Z may never exceed
    sqrt(events / 1082) — the classical full-credibility standard (p=90%, k=5%).

    Round-7 origin, quantified through this very module: EPV estimated from the same
    tiny sample that generates the between-cell spread lets noise-driven separation
    manufacture its own credibility — Z = 0.996 was produced on TWO events, a 23x
    violation of this cap, and the behavior was bimodal junk (~0 or ~0.99 on a
    noise coin-flip). The cap binds Z to information content regardless of which
    exposure convention or EPV estimate produced it, which is why it is the fix
    rather than any re-definition of exposure.
    """
    if n_events <= 0:
        return 0.0
    return min(max(z, 0.0), math.sqrt(n_events / 1082.0))


def not_applicable(cohort: str, horizon_days: int, reason: str,
                   *, as_of: Optional[str] = None) -> Reading:
    """
    Structurally unmeasurable — no input of this kind exists anywhere in the
    stack.  Distinct from ABSENT: ABSENT means "not today", NOT_APPLICABLE
    means "not ever, with the sources we have".  Collapsing the two is defect
    D1 from the crypto panel review.
    """
    return Reading(
        state=State.NOT_APPLICABLE, cohort=cohort, horizon_days=horizon_days,
        reason=reason, as_of=as_of,
    )


# ---------------------------------------------------------------------------
# I4 — Kaplan-Meier with Greenwood variance and log-log confidence limits
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class KMPoint:
    t: float          # time of the event
    n_risk: int       # at risk immediately before t
    n_events: int     # events at t
    survival: float   # S(t)
    var_sum: float    # running sum d/(n(n-d)) — Greenwood's inner term


def kaplan_meier(durations: Sequence[float],
                 events: Sequence[int]) -> List[KMPoint]:
    """
    Kaplan-Meier estimator of S(t) = P(no event by t).

    durations: observed time to event, or to censoring
    events:    1 if the event was observed, 0 if right-censored

    Censoring is the whole reason this function exists.  Coding pending rows as
    non-events is INCONSISTENT (more data does not fix it); dropping them
    conditions the sample on having resolved and biases arrival upward.  KM
    uses each row for exactly as long as it was actually observed.
    """
    if len(durations) != len(events):
        raise ValueError("durations and events must be the same length")
    if not durations:
        return []

    order = sorted(range(len(durations)), key=lambda i: (durations[i], -events[i]))
    n = len(durations)
    out: List[KMPoint] = []
    surv = 1.0
    var_sum = 0.0
    i = 0
    at_risk = n

    while i < n:
        t = durations[order[i]]
        d = 0  # events at t
        c = 0  # total records at t (events + censorings)
        j = i
        while j < n and durations[order[j]] == t:
            d += 1 if events[order[j]] else 0
            c += 1
            j += 1

        if d > 0:
            if at_risk - d < 0:
                raise ValueError("more events than at risk — inconsistent input")
            surv *= (1.0 - d / at_risk)
            if at_risk > d:
                var_sum += d / (at_risk * (at_risk - d))
            else:
                # S(t) has hit 0; Greenwood's term is undefined. Carry the last
                # finite value and let the CI widen rather than divide by zero.
                var_sum = float("inf")
            out.append(KMPoint(t=t, n_risk=at_risk, n_events=d,
                               survival=surv, var_sum=var_sum))

        at_risk -= c
        i = j

    return out


def _survival_at(points: Sequence[KMPoint], t: float) -> Tuple[float, float]:
    """Step-function lookup: returns (S(t), Greenwood var_sum at t)."""
    surv, vs = 1.0, 0.0
    for p in points:
        if p.t <= t:
            surv, vs = p.survival, p.var_sum
        else:
            break
    return surv, vs


def km_arrival_probability(durations: Sequence[float],
                           events: Sequence[int],
                           horizon: float,
                           z: float = Z_95) -> Tuple[Optional[float], Optional[float], Optional[float], int]:
    """
    F(horizon) = 1 - S(horizon) with LOG-LOG transformed confidence limits.

    Returns (F, ci_low, ci_high, n_observed_events).  Returns (None, None,
    None, 0) when the cohort has no observed events — I3.  A cohort with no
    events yields S=1 everywhere, so returning 0.0 here would be a fabricated
    floor, indistinguishable in the payload from a real "nothing ever moves".

    Log-log, not linear: the plain Greenwood interval can fall outside (0,1)
    and has poor coverage in the tail, and the far right of our curve is
    exactly where the risk set has collapsed.

        theta      = log(-log S)
        se(theta)  = sqrt(var_sum) / |log S|
        S_lower    = S ** exp(+z*se)
        S_upper    = S ** exp(-z*se)
        F          = 1 - S ; the CI bounds swap on the flip.
    """
    points = kaplan_meier(durations, events)
    # Round-7 Statistician, Defect A: n_events used to count ALL events in the cohort,
    # so a cell with 2 events at days 200 and 340 served F(30)=0.000 as MEASURED —
    # it passed the I3 check on events that lie beyond the horizon. A served structural
    # zero is the §15a-A3 floor-end defect wearing a survival curve. Events are counted
    # AT OR BEFORE the horizon: zero events by the horizon => (None, ..., 0) => the
    # caller serves ABSENT-at-this-horizon, never a measured 0%.
    n_events = sum(p.n_events for p in points if p.t <= horizon)
    if n_events == 0:
        return None, None, None, 0

    surv, var_sum = _survival_at(points, horizon)
    F = 1.0 - surv

    if surv >= 1.0 or surv <= 0.0 or not math.isfinite(var_sum) or var_sum <= 0.0:
        # Degenerate: no information for an interval. Report the point estimate
        # with a maximally honest [0,1] band rather than a fake tight one.
        return F, 0.0, 1.0, n_events

    se_theta = math.sqrt(var_sum) / abs(math.log(surv))
    s_lower = surv ** math.exp(z * se_theta)
    s_upper = surv ** math.exp(-z * se_theta)
    lo = min(max(1.0 - s_upper, 0.0), 1.0)
    hi = min(max(1.0 - s_lower, 0.0), 1.0)
    return F, lo, hi, n_events


# ---------------------------------------------------------------------------
# I5 — Buhlmann-Straub credibility
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CredibilityResult:
    mu: float                  # exposure-weighted portfolio base rate
    epv: float                 # expected process variance  (v)
    vhm: float                 # variance of hypothetical means (a)
    k: Optional[float]         # v / a ; None when a <= 0 (=> Z = 0)
    z: Dict[str, float]        # per-cell credibility
    blended: Dict[str, float]  # per-cell credibility-weighted rate
    degenerate: bool           # True when the rating factors do not separate


def buhlmann_straub(cell_events: Dict[str, float],
                    cell_exposure: Dict[str, float]) -> CredibilityResult:
    """
    Buhlmann-Straub credibility over cells with unequal exposure.

        mu  = sum(events) / sum(exposure)                    (portfolio rate)
        v   = mu(1 - mu)                                     (process variance
                                                              of a rate)
        a   = [ sum m_i (X_i - mu)^2 - v(r-1) ] / [ m - sum m_i^2 / m ]
        K   = v / a
        Z_i = m_i / (m_i + K)
        X^_i = Z_i X_i + (1 - Z_i) mu

    Exposure is member-DAYS at risk, not member count.  A topic watched 20 days
    and one watched 340 days do not contribute equally to the same cell, which
    is exactly what the *Straub* extension is for.

    THE IMPORTANT PROPERTY: if the rating factors do not actually separate
    outcome rates, the estimated VHM goes to zero (or negative), K -> infinity,
    Z -> 0, and every cell correctly collapses to the portfolio base rate.  The
    model degrades to honesty rather than to confident nonsense.  Negative
    VHM is a normal finite-sample outcome on noisy data, NOT an error — it is
    floored at zero here and reported via `degenerate`.
    """
    cells = [c for c in cell_exposure if cell_exposure[c] > 0]
    if not cells:
        return CredibilityResult(mu=0.0, epv=0.0, vhm=0.0, k=None, z={},
                                 blended={}, degenerate=True)

    m = {c: float(cell_exposure[c]) for c in cells}
    x = {c: float(cell_events.get(c, 0.0)) / m[c] for c in cells}
    m_tot = sum(m.values())
    ev_tot = sum(float(cell_events.get(c, 0.0)) for c in cells)
    mu = ev_tot / m_tot if m_tot > 0 else 0.0

    v = max(mu * (1.0 - mu), 0.0)
    r = len(cells)

    if r < 2 or m_tot <= 0:
        z = {c: 0.0 for c in cells}
        return CredibilityResult(mu=mu, epv=v, vhm=0.0, k=None, z=z,
                                 blended={c: mu for c in cells}, degenerate=True)

    weighted_ss = sum(m[c] * (x[c] - mu) ** 2 for c in cells)
    denom = m_tot - sum(mm ** 2 for mm in m.values()) / m_tot
    a_hat = ((weighted_ss - v * (r - 1)) / denom) if denom > 0 else 0.0

    if a_hat <= 0 or v <= 0:
        z = {c: 0.0 for c in cells}
        return CredibilityResult(mu=mu, epv=v, vhm=max(a_hat, 0.0), k=None, z=z,
                                 blended={c: mu for c in cells}, degenerate=True)

    k = v / a_hat
    z = {c: m[c] / (m[c] + k) for c in cells}
    blended = {c: z[c] * x[c] + (1.0 - z[c]) * mu for c in cells}
    return CredibilityResult(mu=mu, epv=v, vhm=a_hat, k=k, z=z,
                             blended=blended, degenerate=False)


# ---------------------------------------------------------------------------
# Calibration — Murphy decomposition of the Brier score
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MurphyTerms:
    brier: float         # Brier score of the RAW forecasts
    reliability: float   # REL — lower better. Pure calibration/honesty term.
    resolution: float    # RES — higher better. The only term knowledge improves.
    uncertainty: float   # UNC — fixed by the world; also climatology's Brier.
    within_bin: float    # the binning artifact — see below
    n: int
    base_rate: float

    @property
    def brier_binned(self) -> float:
        """Brier score of the bin-mean forecasts. REL - RES + UNC equals THIS."""
        return self.reliability - self.resolution + self.uncertainty

    def identity_residual(self) -> float:
        """
        BS_raw - (REL - RES + UNC + within_bin).  Exactly 0 by construction.

        The three-term identity BS = REL - RES + UNC is exact only for a
        forecast that takes finitely many distinct values binned by EXACT
        value.  Bin continuous forecasts and the gap is the within-bin scatter
        — verified numerically to the last digit.  Reporting that gap as a
        fourth term makes the binning choice visible; loosening a tolerance
        until the test passes would hide a free parameter inside a metric.

        A LARGE `within_bin` relative to `brier` means the bins are too wide
        for the spread of forecasts in them.
        """
        return self.brier - (self.reliability - self.resolution
                             + self.uncertainty + self.within_bin)


def murphy_decomposition(forecasts: Sequence[float],
                         outcomes: Sequence[int],
                         n_bins: int = 10) -> MurphyTerms:
    """
    BS = REL - RES + UNC   (Murphy 1973)

    Why this matters more than the Brier score itself: a forecast can have
    REL = 0 (perfectly calibrated) and RES = 0 (no discrimination at all), so
    BS = UNC.  That forecast is perfectly honest and completely uninformative
    — the climatological forecast.  It is not fraudulent; it is calibrated and
    carries no information.  A base-rate product in that state is a legitimate
    v1 and should be described in exactly those words.

    NEVER publish a bare Brier score: a LOWER Brier can mean a WORSE-calibrated
    model with more discriminatory power.  Publish all three terms.

    NOTE ON BIAS: these are the plug-in estimators.  They are biased —
    reliability systematically over-estimated, uncertainty under-estimated.
    Bias correction (Ferro & Fricker) is negligible above n>60; the plug-in
    needs n>300.  `n` is returned so the caller can decide.
    """
    if len(forecasts) != len(outcomes):
        raise ValueError("forecasts and outcomes must be the same length")
    n = len(forecasts)
    if n == 0:
        return MurphyTerms(0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0)

    brier = sum((p - o) ** 2 for p, o in zip(forecasts, outcomes)) / n
    base = sum(outcomes) / n
    unc = base * (1.0 - base)

    bins: Dict[int, List[Tuple[float, int]]] = {}
    for p, o in zip(forecasts, outcomes):
        idx = min(int(p * n_bins), n_bins - 1)
        bins.setdefault(idx, []).append((float(p), int(o)))

    rel = 0.0
    res = 0.0
    brier_binned = 0.0
    for members in bins.values():
        nk = len(members)
        pk = sum(p for p, _ in members) / nk       # mean forecast in bin
        ok = sum(o for _, o in members) / nk       # observed frequency in bin
        rel += (nk / n) * (pk - ok) ** 2
        res += (nk / n) * (ok - base) ** 2
        brier_binned += sum((pk - o) ** 2 for _, o in members) / n

    return MurphyTerms(brier=brier, reliability=rel, resolution=res,
                       uncertainty=unc, within_bin=brier - brier_binned,
                       n=n, base_rate=base)


def brier_skill_score(terms: MurphyTerms) -> Optional[float]:
    """
    BSS = 1 - BS/BS_ref  with climatology as reference, which for the Brier
    score is exactly UNC.  Substituting the decomposition:

        BSS = (RES - REL) / UNC

    Read the numerator.  Positive skill requires resolution to EXCEED
    miscalibration.  Three honest readings, and the caller should pre-commit
    to which one it will report:

      BSS ~ 0, REL ~ 0, RES ~ 0 : calibrated, no skill against the base rate.
      BSS ~ 0, REL > 0, RES > 0 : discrimination exists, miscalibration is
                                  cancelling it — FIXABLE by recalibration
                                  (resolution is invariant to monotone
                                  recalibration; reliability is not).
      BSS < 0                   : worse than the base rate. Withdraw.

    Returns None when UNC == 0 (a degenerate all-one-outcome sample), because
    a skill score against a reference with zero error is undefined, not zero.

    IMPLEMENTATION NOTE — this returns 1 - BS_raw/UNC, NOT (RES-REL)/UNC.
    They differ by the binning term.  (RES-REL)/UNC is the decomposed form and
    moves when you change `n_bins`; 1 - BS_raw/UNC does not.  A headline skill
    number must not depend on a free parameter chosen by the party reporting
    it, so the binning-independent form is the one served.  Use
    `terms.brier_binned` if you specifically want the decomposed version.
    """
    if terms.uncertainty <= 0:
        return None
    return 1.0 - (terms.brier / terms.uncertainty)
