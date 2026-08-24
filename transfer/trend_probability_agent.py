"""
trend_probability_agent.py — Base Rate agent for the TREND section.

HELD OUT.  Read-only.  This module contains no INSERT, UPDATE or DELETE and
must never acquire one.  It reads the ledgers and reports frequencies; it does
not touch the Gradient Score.

WHAT IT ANSWERS
---------------
Two-sided, and they are NOT complements:

    P(RISE)  = P(the topic reaches mainstream arrival within H days)
    P(DECAY) = P(the topic falls to DECAY/MONITORING within H days)
    P(FLAT)  = 1 - P(RISE) - P(DECAY)     (residual, reported for completeness)

This is a COMPETING RISKS setup: a topic can rise, decay, or do neither, and
the third outcome is common.  Reporting only "probability of trending" and
implying its complement is decay would be wrong on the data.

WHAT IT DOES NOT ANSWER
-----------------------
"Will THIS topic trend?"  The World Cup case study established that guessing is
speculative and outside the product's principles.  What is returned is the
historical frequency in a matched risk class — the same thing an actuary does
when they decline to predict whether YOUR house burns down and instead state
the frequency in your class.

COHORT (rating cells)
---------------------
  maturity        NEW | EMERGING | ESTABLISHED     (topic_lifecycle)
  corroboration   1 | 2-4 | 5+ distinct outlets    (Mainstream v2 threshold)
  provenance      expert_niche | mainstream        (platform_tier — the D/M router)

Cells are NOT suppressed when thin.  Credibility (Z) is computed and displayed;
a thin cell blends toward the portfolio base rate and says so.

GROUND TRUTH (ROUND-8 SCHEMA FIX — the fixture-circularity defect, corrected)
------------
TWO real tables, exactly as `accuracy_ledger_enhanced.init_pending_db` creates
them.  The earlier version selected from a table named `accuracy_ledger_enhanced`
— which is the MODULE's name, not a table; the only CREATE for it lived in this
agent's own test fixture.  Against production the query threw
("relation does not exist"), every call was INSTRUMENT_ERROR, and the suite was
green because the fixture was written to match the SELECT — the exact circular-
fixture defect six board seats named.  Now:

  accuracy_ledger      resolved races.  Verdicts:
    LED / SAME_DAY          -> RISE observed
    LAGGED (near-miss)      -> RISE observed (late, but it arrived)
    pre_broken              -> EXCLUDED: never a race (§14); including it would
                               measure coverage latency, not the thesis
    FALSE_POSITIVE/TIMEOUT  -> no rise within window (censored through horizon)
  pending_detections   status='pending' rows, RIGHT-CENSORED at
                       min(as_of - detection, 365).  These live in their OWN
                       table; the old single-table read never saw them, so the
                       survival curve was fit on RESOLVED ROWS ONLY and the
                       docstring's "pending are censored" was aspirational
                       fiction (modelled inflation 6-19x depending on time at
                       risk).  The UNION below is the fix.

COHORT COVARIATES — STAMPS, NEVER RECOMPUTATION (round-7 convergent cond. 2)
  corroboration   read from `corroboration_at_enroll` ONLY.  Round 6 DISABLED
                  the stamp writer (it computed a different quantity wearing
                  §15a's name), so today every row reads NULL -> band "unknown"
                  and cohorts that need a corroboration band are honestly
                  ABSENT.  That is the board-predicted state ("the trend panel
                  will honestly read ABSENT for months — ship that state as-is
                  or do not ship").  Recomputing from raw_signals is FORBIDDEN
                  here: no syndication collapse, no tier filter, and after the
                  30-day prune it returns 0 — cohort membership would be a
                  function of the prune horizon (the Challenger's finding).
  provenance      derived from surviving raw_signals rows when any exist
                  (mainstream if ANY pre-detection row is mainstream-tier — an
                  explicit CASE, never MAX(platform_tier), which routed D/M by
                  string collation: 'niche' > 'mainstream' alphabetically);
                  NULL -> "unknown" when the signals have pruned.

D-COMPONENT SAFETY (I2 — SCOPE CORRECTED, round 7)
--------------------------------------------------
I2 governs whether a D-DERIVED value may be USED, never whether a row may
enter a non-D cohort.  The current cohort key (maturity x corroboration x
provenance) contains NO Dark-Matter factor, so d_measured status does NOT
gate membership here — the earlier version gated it anyway, which was a
category error: it discarded 100% of usable history (the live stamp
`d_measured_at_enroll` is NULL on all resolved races) for an estimand that
never consults D.  What remains is COVERAGE ACCOUNTING: UNKNOWN rows are
counted in `excluded_unmeasured` (the name is kept for payload stability;
they are counted, not excluded) so that the day a D factor enters the key,
the I2 exclusion switches back on against known coverage.  If a D-derived
cohort factor is ever added, rows that are UNKNOWN must then be excluded
from that stratification — `compute_dark_matter` returns a structural 0.0
on the blind path, so a D-stratified cohort would silently mix "no signal"
with "never looked".  (An earlier draft cited ">90% NULL" for the historical
stratum; that figure was retracted — measured coverage is position-dependent,
~14.5% NULL top-of-feed and 63-70% deep.)
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from probability_core import (
    Fetch,
    Measured,
    Reading,
    State,
    absent,
    buhlmann_straub,
    classify_measured,
    instrument_error,
    km_arrival_probability,
    murphy_decomposition,
    brier_skill_score,
    z_cap,
)

__all__ = ["TrendProbabilityAgent", "TrendCohort", "TrendReadout"]

DEFAULT_HORIZONS = (7, 30, 90)

# Verdicts that count as an observed RISE.  pre_broken is deliberately absent.
RISE_VERDICTS = ("LED", "SAME_DAY", "LAGGED")
# Verdicts that resolve the race without a rise.
NO_RISE_VERDICTS = ("FALSE_POSITIVE", "TIMEOUT", "EXPIRED")


# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TrendCohort:
    maturity: str
    corroboration: str
    provenance: str

    @property
    def key(self) -> str:
        return f"{self.maturity}|{self.corroboration}|{self.provenance}"

    def label(self) -> str:
        return (f"{self.maturity} · {self.corroboration} outlets · "
                f"{self.provenance.replace('_', '-')}")


def provenance_of(platform_tier) -> str:
    """mainstream / expert_niche from an explicit stamp or derived flag; a row
    with NO surviving signal evidence is 'unknown', never defaulted to a tier —
    a defaulted tier is a fabricated input wearing a measured badge (§16a)."""
    if platform_tier is None or str(platform_tier).strip() == "":
        return "unknown"
    return ("mainstream" if str(platform_tier).lower() == "mainstream"
            else "expert_niche")


def corroboration_band(distinct_outlets: Optional[int]) -> str:
    if distinct_outlets is None:
        return "unknown"
    if distinct_outlets <= 1:
        return "1"
    if distinct_outlets <= 4:
        return "2-4"
    return "5+"


@dataclass
class TrendReadout:
    """What the panel renders. Every field is honest-absence capable."""
    topic_key: str
    cohort: Optional[TrendCohort]
    as_of: str
    rise: Reading
    decay: Reading
    flat_estimate: Optional[float] = None
    excluded_unmeasured: int = 0     # rows whose D-measurement status is UNKNOWN (coverage, not exclusion)
    lagged_excluded: int = 0         # near-miss LAGGED rows outside the risk set (counted, round 7)
    dropped_undated: int = 0         # rows with an unparseable/impossible date (counted, round 8)
    coherence_violated: bool = False  # rise+decay > 1 under the two-marginal estimator
    calibration: Optional[dict] = None

    def to_payload(self) -> dict:
        return {
            "topic_key": self.topic_key,
            "cohort": self.cohort.label() if self.cohort else None,
            "cohort_key": self.cohort.key if self.cohort else None,
            "as_of": self.as_of,
            "rise": self.rise.to_payload(),
            "decay": self.decay.to_payload(),
            "flat_estimate": self.flat_estimate,
            "excluded_unmeasured": self.excluded_unmeasured,
            "lagged_excluded": self.lagged_excluded,
            # Round-8: the last uncounted exit door. A row with an unparseable
            # detection_date leaves the risk set as a COUNTED data fault; zero
            # here means every fetched row was either used or counted elsewhere.
            "dropped_undated": self.dropped_undated,
            # ROUND-7 COHERENCE GUARD. rise and decay are estimated as two marginal
            # 1-KM curves; under competing risks each overstates its cumulative
            # incidence and their sum can exceed 1 (constructed: 2.0). The old code
            # clamped flat at 0, HIDING the violation. Until the Aalen-Johansen
            # rebuild (Chairman-gated), incoherence is SERVED as a fact: when the
            # sum exceeds 1, flat_estimate is None and this flag is true, so no
            # renderer can present the three numbers as a coherent distribution.
            "coherence_violated": self.coherence_violated,
            "calibration": self.calibration,
            "disclaimer": (
                "Historical frequency for a matched cohort. Not a forecast, "
                "not investment advice."
            ),
        }


# ---------------------------------------------------------------------------

class TrendProbabilityAgent:
    """
    Usage:
        agent = TrendProbabilityAgent(fetch=db_compat.fetch_all)
        readout = agent.score("agentic coding", as_of="2026-08-21", horizon_days=30)
        payload = readout.to_payload()

    `fetch(sql, params) -> list[dict]` must be READ-ONLY.  Wire it to a
    read-only connection if one is available; db_compat translates the `?`
    placeholders for Postgres.

    The SQL lives in overridable class attributes because column names differ
    between the local SQLite schema and Heroku Postgres.  Each query documents
    the columns it must return.  Override rather than editing in place.
    """

    # -- queries (override to match the live schema) ------------------------

    #: must return: topic_key, maturity_class, first_seen
    SQL_LIFECYCLE = """
        SELECT topic_key, maturity_class, first_seen
          FROM topic_lifecycle
         WHERE topic_key = ?
    """

    #: must return: distinct_outlets, distinct_titles, platform_tier
    #: distinct_outlets/titles are TIER-FILTERED to mainstream and the band is
    #: min(outlets, titles) — the §15a syndication collapse (one wire story
    #: through forty mastheads is one voice). The old query counted every
    #: platform (five subreddits read as five outlets) with no collapse, and
    #: MAX(platform_tier) routed D/M by string collation ('niche' >
    #: 'mainstream' alphabetically) — both round-7 board findings.
    SQL_PROVENANCE = """
        SELECT COUNT(DISTINCT CASE WHEN platform_tier = 'mainstream'
                                   THEN source_name END) AS distinct_outlets,
               COUNT(DISTINCT CASE WHEN platform_tier = 'mainstream'
                                   THEN title END)       AS distinct_titles,
               CASE WHEN COUNT(*) = 0 THEN NULL
                    WHEN MAX(CASE WHEN platform_tier = 'mainstream'
                                  THEN 1 ELSE 0 END) = 1 THEN 'mainstream'
                    ELSE 'expert_niche' END              AS platform_tier
          FROM raw_signals
         WHERE topic_key  = ?
           AND signal_date <= ?
    """

    #: cohort population: resolved races UNION pending races, one row per
    #: enrolled topic, against the REAL two-table schema
    #: (accuracy_ledger_enhanced.init_pending_db).  must return: topic_key,
    #: detection_date, breakout_date, verdict, maturity_class,
    #: corroboration_at_enroll, platform_tier, d_measured, is_pending.
    #: Takes TWO parameters, both = as_of.
    #:
    #: corroboration comes from the ENROLLMENT STAMP only — round-7 convergent
    #: condition 2 forbids recomputation (the old subquery counted raw
    #: source_name with no syndication collapse, no tier filter, and returned
    #: 0 after the prune).  The stamp is NULL today (round-6 disabled its
    #: writer until the definition is canonical) — that reads as band
    #: "unknown", which is the honest state, not a defect of this query.
    #:
    #: pending rows carry verdict 'PENDING' (not a RISE_VERDICT), so the
    #: reader right-censors them at min(as_of - detection, 365) — the patience
    #: window finally reaching the estimator instead of living in a docstring.
    SQL_COHORT_LEDGER = """
        SELECT l.topic_key,
               l.detection_date,
               l.breakout_date,
               l.verdict,
               tl.maturity_class,
               l.corroboration_at_enroll,
               (SELECT CASE WHEN COUNT(*) = 0 THEN NULL
                            WHEN MAX(CASE WHEN rs.platform_tier = 'mainstream'
                                          THEN 1 ELSE 0 END) = 1
                            THEN 'mainstream' ELSE 'expert_niche' END
                  FROM raw_signals rs
                 WHERE rs.topic_key = l.topic_key
                   AND rs.signal_date <= l.detection_date) AS platform_tier,
               l.d_measured_at_enroll AS d_measured,
               0 AS is_pending
          FROM accuracy_ledger l
          LEFT JOIN topic_lifecycle tl ON tl.topic_key = l.topic_key
         WHERE l.detection_date <= ?
           AND COALESCE(l.pre_broken, 0) = 0
        UNION ALL
        SELECT p.topic_key,
               p.detection_date,
               NULL AS breakout_date,
               'PENDING' AS verdict,
               tl.maturity_class,
               p.corroboration_at_enroll,
               (SELECT CASE WHEN COUNT(*) = 0 THEN NULL
                            WHEN MAX(CASE WHEN rs.platform_tier = 'mainstream'
                                          THEN 1 ELSE 0 END) = 1
                            THEN 'mainstream' ELSE 'expert_niche' END
                  FROM raw_signals rs
                 WHERE rs.topic_key = p.topic_key
                   AND rs.signal_date <= p.detection_date) AS platform_tier,
               p.d_measured_at_enroll AS d_measured,
               1 AS is_pending
          FROM pending_detections p
          LEFT JOIN topic_lifecycle tl ON tl.topic_key = p.topic_key
         WHERE p.detection_date <= ?
           AND p.status = 'pending'
    """

    #: decay observations. must return: topic_key, decay_date (first date the
    #: topic's stage fell to DECAY/MONITORING), detection_date
    SQL_COHORT_DECAY = """
        SELECT topic_key,
               MIN(signal_date) AS decay_date
          FROM velocity_scores
         WHERE signal_date <= ?
           AND stage IN ('DECAY', 'MONITORING')
         GROUP BY topic_key
    """

    #: resolved rows for the calibration block: served probability + outcome
    SQL_CALIBRATION = """
        SELECT served_probability, observed_outcome
          FROM base_rate_calibration_log
         WHERE kind = 'trend'
           AND resolved_at <= ?
    """

    def __init__(self, fetch: Fetch, *, horizons: Sequence[int] = DEFAULT_HORIZONS,
                 min_cohort: int = 1):
        self.fetch = fetch
        self.horizons = tuple(horizons)
        # Deliberately NOT a suppression threshold. Credibility handles thin
        # cells (I5). This only guards against an empty cohort, which cannot
        # produce a curve at all.
        self.min_cohort = max(1, min_cohort)

    # -- public -------------------------------------------------------------

    def score(self, topic_key: str, *, as_of: Optional[str] = None,
              horizon_days: int = 30) -> TrendReadout:
        as_of = as_of or _dt.date.today().isoformat()

        cohort, cohort_err = self._cohort_for(topic_key, as_of)
        if cohort is None:
            if cohort_err:
                # INSTRUMENT_ERROR, never ABSENT (round 7, three seats): a broken
                # query is a fact about US. The old path served "no lifecycle
                # record" on a schema mismatch — a fabricated reason, and an
                # invisible outage (error-to-ABSENT laundering).
                r = instrument_error("unknown", horizon_days, cohort_err, as_of=as_of)
                return TrendReadout(topic_key=topic_key, cohort=None, as_of=as_of,
                                    rise=r, decay=r)
            reason = "topic has no lifecycle or provenance record as of this date"
            return TrendReadout(
                topic_key=topic_key, cohort=None, as_of=as_of,
                rise=absent("unknown", horizon_days, reason, as_of=as_of),
                decay=absent("unknown", horizon_days, reason, as_of=as_of),
            )

        rows, rows_err = self._cohort_rows(as_of)
        if rows_err:
            r = instrument_error(cohort.label(), horizon_days, rows_err, as_of=as_of)
            return TrendReadout(topic_key=topic_key, cohort=cohort, as_of=as_of,
                                rise=r, decay=r)
        decay_map = self._decay_map(as_of)

        rise, excluded, lagged, undated = self._reading(
            rows, cohort, as_of, horizon_days, outcome="rise", decay_map=decay_map)
        decay, _, _, _ = self._reading(
            rows, cohort, as_of, horizon_days, outcome="decay", decay_map=decay_map)

        flat = None
        coherence_violated = False
        if rise.state is State.MEASURED and decay.state is State.MEASURED:
            total = (rise.value or 0.0) + (decay.value or 0.0)
            if total > 1.0:
                # Two marginal 1-KM curves exceeding unity: the estimator's known
                # competing-risks bias, SERVED as a violation instead of clamped
                # invisible. flat stays None — there is no coherent residual.
                coherence_violated = True
            else:
                flat = 1.0 - total

        return TrendReadout(
            topic_key=topic_key, cohort=cohort, as_of=as_of,
            rise=rise, decay=decay, flat_estimate=flat,
            excluded_unmeasured=excluded, lagged_excluded=lagged,
            dropped_undated=undated,
            coherence_violated=coherence_violated,
            calibration=self.calibration(as_of),
        )

    def calibration(self, as_of: Optional[str] = None) -> Optional[dict]:
        """
        The accountability loop: how did our past statements actually hold up?
        Returns all three Murphy terms and the skill score against climatology.
        Never a bare Brier score — a lower Brier can mean a WORSE-calibrated
        model with more discriminatory power.
        """
        as_of = as_of or _dt.date.today().isoformat()
        try:
            rows = self.fetch(self.SQL_CALIBRATION, (as_of,))
        except Exception:
            return None  # fail-open: a missing calibration log is not an outage
        if not rows:
            return None

        fc = [float(r["served_probability"]) for r in rows
              if r.get("served_probability") is not None]
        ob = [int(r["observed_outcome"]) for r in rows
              if r.get("served_probability") is not None]
        if not fc:
            return None

        terms = murphy_decomposition(fc, ob)
        return {
            "n": terms.n,
            "brier": round(terms.brier, 5),
            "reliability": round(terms.reliability, 5),
            "resolution": round(terms.resolution, 5),
            "uncertainty": round(terms.uncertainty, 5),
            "brier_skill_score": (None if brier_skill_score(terms) is None
                                  else round(brier_skill_score(terms), 4)),
            "base_rate": round(terms.base_rate, 4),
            "bias_note": ("plug-in estimators; reliability is over-estimated and "
                          "uncertainty under-estimated below n≈300"),
        }

    # -- internals ----------------------------------------------------------

    def _cohort_for(self, topic_key: str, as_of: str):
        """Returns (cohort_or_None, error_message_or_None). A thrown query is an
        INSTRUMENT fault and must never be narrated as missing data (round 7)."""
        try:
            life = self.fetch(self.SQL_LIFECYCLE, (topic_key,))
            prov = self.fetch(self.SQL_PROVENANCE, (topic_key, as_of))
        except Exception as exc:
            return None, f"cohort query failed: {type(exc).__name__}: {exc}"
        if not life or not prov:
            return None, None
        maturity = (life[0].get("maturity_class") or "unknown").upper()
        # §15a syndication collapse: one wire story through many mastheads is
        # one voice — the band is min(distinct outlets, distinct titles).
        outlets = prov[0].get("distinct_outlets")
        titles = prov[0].get("distinct_titles")
        collapsed = (None if outlets is None
                     else (int(outlets) if titles is None
                           else min(int(outlets), int(titles))))
        provenance = provenance_of(prov[0].get("platform_tier"))
        if provenance == "unknown" and collapsed in (None, 0):
            return None, None
        return TrendCohort(maturity=maturity,
                           corroboration=corroboration_band(collapsed),
                           provenance=provenance), None

    def _cohort_rows(self, as_of: str):
        """Returns (rows, error_message_or_None) — same round-7 discipline.
        Two bind parameters: the resolved arm and the pending arm of the UNION."""
        try:
            return list(self.fetch(self.SQL_COHORT_LEDGER, (as_of, as_of))), None
        except Exception as exc:
            return [], f"cohort ledger query failed: {type(exc).__name__}: {exc}"

    def _decay_map(self, as_of: str) -> Dict[str, str]:
        try:
            rows = self.fetch(self.SQL_COHORT_DECAY, (as_of,))
        except Exception:
            return {}
        return {r["topic_key"]: r["decay_date"] for r in rows if r.get("decay_date")}

    def _reading(self, rows: List[dict], cohort: TrendCohort, as_of: str,
                 horizon: int, *, outcome: str,
                 decay_map: Dict[str, str]) -> tuple:
        """
        Build one Reading. Returns (Reading, excluded_unmeasured_count).

        The cohort is assembled with FULL censoring bookkeeping: every enrolled
        topic contributes exactly the time it was actually observed, and
        unresolved rows are censored at min(as_of, detection + patience).
        """
        durations_by_cell: Dict[str, List[float]] = {}
        events_by_cell: Dict[str, List[int]] = {}
        excluded_unmeasured = 0
        lagged_excluded = 0
        dropped_undated = 0

        for r in rows:
            # I2 SCOPE FIX (round 7, conceded in full): the gate below used to EXCLUDE
            # every d_measured-UNKNOWN row from this cohort — but the cohort key is
            # maturity x corroboration x provenance and contains NO D-derived factor,
            # so the gate was a category error: it discarded 100% of usable history
            # (the live stamp is NULL on all resolved races) for an estimand that never
            # consults D, and if NULL correlates with enrollment date it INDUCED
            # selection bias rather than removing it. I2 governs whether a D-DERIVED
            # value may be used, never whether a row may enter a non-D cohort. The
            # machinery stays, armed: coverage is COUNTED and reported so the day a
            # D factor enters the key, the exclusion switches back on with data.
            if classify_measured(r.get("d_measured")) is Measured.UNKNOWN:
                excluded_unmeasured += 1     # counted as UNSTAMPED coverage, not excluded

            cell = TrendCohort(
                maturity=(r.get("maturity_class") or "unknown").upper(),
                # STAMP ONLY (round-7 cond. 2): NULL stamp -> "unknown" band,
                # never a recomputation from prunable raw_signals.
                corroboration=corroboration_band(
                    None if r.get("corroboration_at_enroll") is None
                    else int(r["corroboration_at_enroll"])),
                provenance=provenance_of(r.get("platform_tier")),
            ).key

            det = _parse(r.get("detection_date"))
            if det is None:
                # COUNTED (round-8): an unparseable detection_date is a data
                # fault, and a row leaving through an uncounted door is the
                # silent-drop class round 7 closed for LAGGED. Same rule here.
                dropped_undated += 1
                continue

            if outcome == "rise":
                end = _parse(r.get("breakout_date"))
                verdict = (r.get("verdict") or "").upper()
                observed = 1 if (verdict in RISE_VERDICTS and end is not None) else 0
            else:
                end = _parse(decay_map.get(r.get("topic_key")))
                observed = 1 if end is not None else 0

            if observed and end is not None:
                dur = (end - det).days
                if dur < 0:
                    # ROUND-7 FIX: this is NOT "a data fault" — it is every near-miss
                    # LAGGED row, by the verdict's own definition (breakout BEFORE
                    # detection). The old silent `continue` made RISE_VERDICTS'
                    # "LAGGED" entry dead code and deleted exactly the fast-arrival
                    # topics from both sides of the fraction — informative deletion,
                    # uncounted. They are left-truncation casualties: still excluded
                    # from this curve (a negative duration cannot enter a KM risk
                    # set), but COUNTED and served, so the served n_cohort can be
                    # reconciled with the published ledger denominators.
                    lagged_excluded += 1
                    continue
            else:
                # Right-censored at the earlier of today and the patience limit.
                # This branch now actually carries the PENDING stratum (verdict
                # 'PENDING' from the pending_detections arm of the UNION) — the
                # rows whose absence inflated every resolved-only curve.
                asd = _parse(as_of)
                dur = (asd - det).days if asd else 0
                dur = min(dur, 365)
                if dur < 0:
                    # detection after as_of should be impossible (the SQL bounds
                    # detection_date <= as_of); if it happens it is a parse or
                    # data fault and is COUNTED, not silently dropped.
                    dropped_undated += 1
                    continue

            durations_by_cell.setdefault(cell, []).append(float(dur))
            events_by_cell.setdefault(cell, []).append(observed)

        key = cohort.key
        if key not in durations_by_cell or len(durations_by_cell[key]) < self.min_cohort:
            return (absent(cohort.label(), horizon,
                           "no comparable history for this cohort as of this date",
                           as_of=as_of), excluded_unmeasured, lagged_excluded, dropped_undated)

        # --- I4: Kaplan-Meier on the target cell -----------------------------
        F, lo, hi, n_ev = km_arrival_probability(
            durations_by_cell[key], events_by_cell[key], horizon)

        if F is None or n_ev == 0:
            # I3 — a cohort with no observed events yields F=0. That is a
            # fabricated floor, not a measurement.
            return (absent(cohort.label(), horizon,
                           f"cohort of {len(durations_by_cell[key])} carries no "
                           f"observed {outcome} events — a rate cannot be measured",
                           n_cohort=len(durations_by_cell[key]), n_events=0,
                           as_of=as_of), excluded_unmeasured, lagged_excluded, dropped_undated)

        # --- I5: credibility across all cells --------------------------------
        cell_events = {c: float(sum(evs)) for c, evs in events_by_cell.items()}
        cell_exposure = {c: float(sum(ds)) for c, ds in durations_by_cell.items()}
        cred = buhlmann_straub(cell_events, cell_exposure)
        # Z-CAP (round 7): the uncapped Z hit 0.996 on TWO events on a realistic
        # fixture — noise-driven separation manufacturing its own credibility. The
        # limited-fluctuation cap binds Z to information content: sqrt(events/1082).
        z = z_cap(cred.z.get(key, 0.0), n_ev)

        # Blend the cell's own KM estimate toward the portfolio KM estimate,
        # weighted by credibility. The portfolio estimate is the pooled curve.
        all_d = [d for ds in durations_by_cell.values() for d in ds]
        all_e = [e for es in events_by_cell.values() for e in es]
        F_port, _, _, _ = km_arrival_probability(all_d, all_e, horizon)
        F_port = F_port if F_port is not None else F

        blended = z * F + (1.0 - z) * F_port
        blended = min(max(blended, 0.0), 1.0)

        # Widen the interval by the same blend so a thin cell cannot present a
        # tight band borrowed from a cell it barely belongs to.
        lo_b = min(max(z * (lo or 0.0) + (1 - z) * 0.0, 0.0), 1.0)
        hi_b = min(max(z * (hi or 1.0) + (1 - z) * 1.0, 0.0), 1.0)
        if lo_b > blended:
            lo_b = blended
        if hi_b < blended:
            hi_b = blended

        return (Reading(
            state=State.MEASURED,
            cohort=cohort.label(),
            horizon_days=horizon,
            value=round(blended, 4),
            ci_low=round(lo_b, 4),
            ci_high=round(hi_b, 4),
            n_cohort=len(durations_by_cell[key]),
            n_events=n_ev,
            exposure=cell_exposure[key],
            credibility=round(z, 3),
            raw_rate=round(F, 4),
            base_rate=round(F_port, 4),
            as_of=as_of,
        ), excluded_unmeasured, lagged_excluded, dropped_undated)


def _parse(value) -> Optional[_dt.date]:
    """Canonical-date parse. Whole-string formats only — never a naive split,
    never a raw [:10] slice (§14)."""
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    s = str(value).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d %B %Y", "%B %d, %Y"):
        try:
            return _dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    try:
        return _dt.datetime.fromisoformat(s).date()
    except ValueError:
        return None
