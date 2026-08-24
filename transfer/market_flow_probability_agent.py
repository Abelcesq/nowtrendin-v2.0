"""
market_flow_probability_agent.py — Base Rate agent for the MARKET SIGNAL section.

HELD OUT.  Read-only.  No INSERT/UPDATE/DELETE, ever.

WHAT IT ANSWERS
---------------
    P(INFLOW-consistent move)  = P(sector price moves +5% within H days)
    P(OUTFLOW-consistent move) = P(sector price moves -5% within H days)

conditioned on a cohort defined by observed money-side positioning AND macro
regime.  Again a competing-risks pair, not complements: most sector-windows do
neither inside the horizon, and reporting only one side implies its complement
is the other, which is false on the data.

MEASUREMENT, NOT ADVICE.  A frequency in a matched risk class.  Nothing here is
a recommendation, a target, or a forecast for any specific sector.

MONEY-SIDE INPUTS (what actually feeds the cohort)
--------------------------------------------------
  Finviz Elite Form-4      PRIMARY insider leg since 2026-06-26.  The signal is
                           insider BUYING (accumulation, >= $250K).  Insider NET
                           is degenerate — it is almost always sell-dominated —
                           so routine selling is NEUTRAL here, never bearish.
  FINRA short interest     positioning band.
  OFR STFM                 macro funding / "Macro Positioning" (NOT insider —
                           the label distinction is contractual, §15).
  FMP                      prices, for outcome realisation only.

DELIBERATELY NOT BLENDED
------------------------
  QuiverQuant congress + WhaleWisdom 13F.  R7 (2026-07-25) set
  DARK_POS_WEIGHT = 0 after a 6/6 board finding: directionless intensity, and a
  0.6 loading that behaved as a top-10-holdings index proxy.  The blend fired on
  exactly 16 mega-caps of 300 and nowhere else.  This agent does not resurrect
  it.  13F is read for DISPLAY provenance only and never enters a cohort key.
  If that ruling is ever reversed, reversing it here is a separate, gated change.

ECONOMIC FACTORS
----------------
Macro enters as a REGIME TAG on the cohort, not as a continuous covariate.
Discrete cells are auditable and do not overfit; a continuous macro term on a
few hundred sector-windows would.

  rates_regime    RISING | FLAT | FALLING   from the 90-day change in DGS10
  credit_regime   TIGHT  | NORMAL | WIDE    from the HY OAS percentile
  turbulence      CALM   | ELEVATED        from the N Market Score TURBULENCE
                                            reading, when one is available

Macro is OPTIONAL by construction.  When no macro reading is knowable as of the
requested date, the cohort degrades to `macro=UNKNOWN` and the agent says so —
it does not substitute a default regime, because a defaulted regime is a
fabricated input wearing a measured badge.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence

from probability_core import (
    Fetch,
    Reading,
    State,
    absent,
    brier_skill_score,
    buhlmann_straub,
    instrument_error,
    km_arrival_probability,
    murphy_decomposition,
    not_applicable,
    z_cap,
)

__all__ = ["MarketFlowProbabilityAgent", "MarketCohort", "MacroContext",
           "MarketReadout"]

DEFAULT_HORIZON_DAYS = 60      # matches market_accuracy_ledger's ±5% / 60d rule
MOVE_THRESHOLD = 0.05


# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MacroContext:
    """
    Macro regime as of a date.  Every field is Optional; UNKNOWN is a first-
    class value and never silently becomes a default.
    """
    rates_regime: Optional[str] = None      # RISING | FLAT | FALLING
    credit_regime: Optional[str] = None     # TIGHT | NORMAL | WIDE
    turbulence: Optional[str] = None        # CALM | ELEVATED
    as_of: Optional[str] = None

    @property
    def key(self) -> str:
        r = self.rates_regime or "UNKNOWN"
        c = self.credit_regime or "UNKNOWN"
        return f"{r}/{c}"

    @property
    def complete(self) -> bool:
        return self.rates_regime is not None and self.credit_regime is not None


def classify_rates(dgs10_change_90d: Optional[float]) -> Optional[str]:
    """FRED DGS10, 90-day change in percentage points."""
    if dgs10_change_90d is None:
        return None
    if dgs10_change_90d >= 0.25:
        return "RISING"
    if dgs10_change_90d <= -0.25:
        return "FALLING"
    return "FLAT"


def classify_credit(hy_oas_percentile: Optional[float]) -> Optional[str]:
    """FRED BAMLH0A0HYM2 (high-yield OAS) as a trailing percentile, 0..1."""
    if hy_oas_percentile is None:
        return None
    if hy_oas_percentile >= 0.75:
        return "WIDE"
    if hy_oas_percentile <= 0.25:
        return "TIGHT"
    return "NORMAL"


@dataclass(frozen=True)
class MarketCohort:
    sector: str
    insider_band: str      # NONE | LIGHT | BROAD  (accumulation breadth)
    short_band: str        # LOW | MID | HIGH      (short interest percentile)
    macro: str             # MacroContext.key

    @property
    def key(self) -> str:
        return f"{self.sector}|{self.insider_band}|{self.short_band}|{self.macro}"

    def label(self) -> str:
        return (f"{self.sector} · insider {self.insider_band.lower()} · "
                f"short {self.short_band.lower()} · macro {self.macro}")


def insider_band(accumulation_filings: Optional[int]) -> str:
    """
    Band of insider BUYING activity, not net flow — and, ROUND-7 CORRECTION
    (Economist): the input is a count of accumulation FILINGS, not distinct
    persons.  The SQL is `SUM(CASE WHEN signal='accumulation' ...)`, so one
    insider filing three Form-4s reads as 3.  Seyhun's cluster-buying result
    is a distinct-PERSONS breadth result; until a distinct-persons query
    exists, this band measures filing intensity and must never be narrated
    as "several insiders buying".  (Renamed from `distinct_buyers`, which
    claimed a quantity the query does not compute.)
    """
    if accumulation_filings is None:
        return "unknown"
    if accumulation_filings <= 0:
        return "NONE"
    if accumulation_filings <= 2:
        return "LIGHT"
    return "BROAD"


def short_band(percentile: Optional[float]) -> str:
    if percentile is None:
        return "unknown"
    if percentile >= 0.70:
        return "HIGH"
    if percentile <= 0.30:
        return "LOW"
    return "MID"


@dataclass
class MarketReadout:
    sector: str
    cohort: Optional[MarketCohort]
    as_of: str
    inflow_move: Reading
    outflow_move: Reading
    macro: MacroContext
    money_leg_sources: List[str]
    dropped_undated: int = 0    # rows with unparseable/impossible dates (counted, round 8)
    calibration: Optional[dict] = None

    def to_payload(self) -> dict:
        return {
            "sector": self.sector,
            "cohort": self.cohort.label() if self.cohort else None,
            "cohort_key": self.cohort.key if self.cohort else None,
            "as_of": self.as_of,
            "inflow_move": self.inflow_move.to_payload(),
            "outflow_move": self.outflow_move.to_payload(),
            "dropped_undated": self.dropped_undated,
            "macro": {
                "rates_regime": self.macro.rates_regime,
                "credit_regime": self.macro.credit_regime,
                "turbulence": self.macro.turbulence,
                "complete": self.macro.complete,
                "as_of": self.macro.as_of,
            },
            "money_leg_sources": self.money_leg_sources,
            "excluded_by_ruling": [
                "QuiverQuant congress (R7: DARK_POS_WEIGHT=0)",
                "WhaleWisdom 13F blend (R7: DARK_POS_WEIGHT=0)",
            ],
            "calibration": self.calibration,
            "disclaimer": (
                "Historical frequency for a matched cohort. Measurement only — "
                "not financial, investment, or legal advice."
            ),
        }


# ---------------------------------------------------------------------------

class MarketFlowProbabilityAgent:
    """
        agent = MarketFlowProbabilityAgent(fetch=db_compat.fetch_all,
                                           macro_provider=my_fred_reader)
        readout = agent.score("Technology", as_of="2026-08-21")

    `macro_provider(as_of) -> MacroContext` is injected so the agent is
    testable without network access and so a FRED outage degrades the cohort to
    macro=UNKNOWN rather than taking the panel down.
    """

    #: must return: sector, accumulation_filings, short_percentile
    #: (alias renamed round 7 — this SUM counts FILINGS, not distinct persons)
    #:
    #: ROUND-8 HONESTY NOTE: `market_positioning` does not exist anywhere in
    #: the codebase yet — it is this agent's declared interface for the
    #: forward-only PIT-stamped positioning layer (round-7 Executioner item 7).
    #: Until that layer is built, this query THROWS in production and the agent
    #: serves INSTRUMENT_ERROR — deliberately: the data layer's absence is a
    #: fact about us, never narrated as "no positioning observed".  The
    #: real-DDL tripwire asserts this exact behavior.
    SQL_SECTOR_STATE = """
        SELECT sector,
               SUM(CASE WHEN signal = 'accumulation' AND value_usd >= 250000
                        THEN 1 ELSE 0 END) AS accumulation_filings,
               AVG(short_percentile)       AS short_percentile
          FROM market_positioning
         WHERE sector       = ?
           AND signal_date <= ?
           AND signal_date  > date(?, '-30 day')
         GROUP BY sector
    """

    #: cohort population: resolved rows UNION pending rows, against the REAL
    #: schema (market_accuracy_ledger.init_market_ledger_db).  Takes TWO bind
    #: parameters, both = as_of.
    #:
    #: ROUND-8 SCHEMA FIX (fixture-circularity): the old query selected
    #: sector / direction / distinct_buyers / short_percentile / rates_regime /
    #: credit_regime — NONE of which exist in the real table (it has ticker,
    #: flow, verdict, move_date...).  The only place those columns existed was
    #: this agent's own test fixture, so the suite was green while every
    #: production call threw.  Realized DIRECTION is not stored either; it is
    #: derived in Python from flow x verdict (CONFIRMED = moved with the flow,
    #: NOT_CONFIRMED = crossed the opposite threshold first, NO_MOVE = neither
    #: within the window — market_accuracy_ledger._evaluate's contract).
    #:
    #: The cohort covariates (sector, insider band, short band, macro regimes)
    #: are NOT selected because they are not in the ledger: they await the
    #: forward-only PIT covariate stamping (round-7 Executioner item 7 — "the
    #: probability project's real first commit").  Until those stamps exist,
    #: every historical row banding reads "unknown" and a target cohort with
    #: real bands is honestly ABSENT — never backfilled from current state,
    #: which would be hindsight wearing a measured badge.
    SQL_COHORT = """
        SELECT m.ticker,
               m.detection_date,
               m.move_date,
               m.flow,
               m.verdict,
               0 AS is_pending
          FROM market_accuracy_ledger m
         WHERE m.detection_date <= ?
        UNION ALL
        SELECT p.ticker,
               p.detection_date,
               NULL AS move_date,
               p.flow,
               'PENDING' AS verdict,
               1 AS is_pending
          FROM market_pending_detections p
         WHERE p.detection_date <= ?
           AND p.status = 'pending'
    """

    SQL_CALIBRATION = """
        SELECT served_probability, observed_outcome
          FROM base_rate_calibration_log
         WHERE kind = 'market'
           AND resolved_at <= ?
    """

    def __init__(self, fetch: Fetch,
                 macro_provider: Optional[Callable[[str], MacroContext]] = None,
                 *, horizon_days: int = DEFAULT_HORIZON_DAYS,
                 min_cohort: int = 1):
        self.fetch = fetch
        self.macro_provider = macro_provider
        self.horizon_days = horizon_days
        self.min_cohort = max(1, min_cohort)

    # -- public -------------------------------------------------------------

    def score(self, sector: str, *, as_of: Optional[str] = None,
              horizon_days: Optional[int] = None) -> MarketReadout:
        as_of = as_of or _dt.date.today().isoformat()
        horizon = horizon_days or self.horizon_days

        macro = self._macro(as_of)
        cohort, cohort_err = self._cohort_for(sector, as_of, macro)

        if cohort is None:
            if cohort_err:
                # INSTRUMENT_ERROR ≠ ABSENT (round 7): a thrown positioning query
                # must never be narrated as "no positioning observed" — that is a
                # fabricated reason on an instrument fault, and it hides the outage.
                r = instrument_error(sector, horizon, cohort_err, as_of=as_of)
                return MarketReadout(sector=sector, cohort=None, as_of=as_of,
                                     macro=macro, money_leg_sources=[],
                                     inflow_move=r, outflow_move=r)
            reason = ("no money-side positioning observed for this sector in the "
                      "trailing 30 days as of this date")
            return MarketReadout(
                sector=sector, cohort=None, as_of=as_of, macro=macro,
                # A10 (§17, round 7): when nothing contributed, the sources list
                # is EMPTY — naming Finviz/FINRA/OFR/FMP under an ABSENT reading
                # implies they informed a read that does not exist.
                money_leg_sources=[],
                inflow_move=absent(sector, horizon, reason, as_of=as_of),
                outflow_move=absent(sector, horizon, reason, as_of=as_of),
            )

        rows, rows_err = self._cohort_rows(as_of)
        if rows_err:
            r = instrument_error(cohort.label(), horizon, rows_err, as_of=as_of)
            return MarketReadout(sector=sector, cohort=cohort, as_of=as_of,
                                 macro=macro, money_leg_sources=[],
                                 inflow_move=r, outflow_move=r)
        up, undated = self._reading(rows, cohort, as_of, horizon, direction="up")
        down, _ = self._reading(rows, cohort, as_of, horizon, direction="down")

        return MarketReadout(
            sector=sector, cohort=cohort, as_of=as_of, macro=macro,
            money_leg_sources=self._sources(),
            inflow_move=up, outflow_move=down,
            dropped_undated=undated,
            calibration=self.calibration(as_of),
        )

    def calibration(self, as_of: Optional[str] = None) -> Optional[dict]:
        as_of = as_of or _dt.date.today().isoformat()
        try:
            rows = self.fetch(self.SQL_CALIBRATION, (as_of,))
        except Exception:
            return None
        if not rows:
            return None
        fc = [float(r["served_probability"]) for r in rows
              if r.get("served_probability") is not None]
        ob = [int(r["observed_outcome"]) for r in rows
              if r.get("served_probability") is not None]
        if not fc:
            return None
        t = murphy_decomposition(fc, ob)
        bss = brier_skill_score(t)
        return {
            "n": t.n,
            "brier": round(t.brier, 5),
            "reliability": round(t.reliability, 5),
            "resolution": round(t.resolution, 5),
            "uncertainty": round(t.uncertainty, 5),
            "brier_skill_score": None if bss is None else round(bss, 4),
            "base_rate": round(t.base_rate, 4),
        }

    # -- internals ----------------------------------------------------------

    def _sources(self) -> List[str]:
        return ["Finviz Elite Form-4 (insider buying, primary)",
                "FINRA short interest",
                "OFR Short-Term Funding Monitor (macro positioning)",
                "FMP (price realisation)"]

    def _macro(self, as_of: str) -> MacroContext:
        if self.macro_provider is None:
            return MacroContext(as_of=as_of)
        try:
            m = self.macro_provider(as_of)
            return m if isinstance(m, MacroContext) else MacroContext(as_of=as_of)
        except Exception:
            # A macro outage degrades the cohort; it does not fabricate a regime.
            return MacroContext(as_of=as_of)

    def _cohort_for(self, sector: str, as_of: str, macro: MacroContext):
        """Returns (cohort_or_None, error_message_or_None) — round-7 discipline:
        a thrown query surfaces as an instrument fault, never as missing data."""
        try:
            rows = self.fetch(self.SQL_SECTOR_STATE, (sector, as_of, as_of))
        except Exception as exc:
            return None, f"sector-state query failed: {type(exc).__name__}: {exc}"
        if not rows:
            return None, None
        r = rows[0]
        filings = r.get("accumulation_filings")
        pct = r.get("short_percentile")
        if filings is None and pct is None:
            return None, None
        return MarketCohort(
            sector=sector,
            insider_band=insider_band(None if filings is None else int(filings)),
            short_band=short_band(None if pct is None else float(pct)),
            macro=macro.key,
        ), None

    def _cohort_rows(self, as_of: str):
        """Returns (rows, error_message_or_None). Two bind parameters: the
        resolved arm and the pending arm of the UNION."""
        try:
            return list(self.fetch(self.SQL_COHORT, (as_of, as_of))), None
        except Exception as exc:
            return [], f"market ledger query failed: {type(exc).__name__}: {exc}"

    def _reading(self, rows: List[dict], cohort: MarketCohort, as_of: str,
                 horizon: int, *, direction: str) -> tuple:
        """Returns (Reading, dropped_undated). Every row either enters a risk
        set or is counted — no uncounted exit doors (round 8)."""
        durations: Dict[str, List[float]] = {}
        events: Dict[str, List[int]] = {}
        dropped_undated = 0

        for r in rows:
            # Covariate bands read the row's stamps. The real ledger carries
            # none yet (they await forward-only PIT stamping), so every band is
            # honestly "unknown" — never recomputed from current positioning,
            # which would be hindsight.
            cell = MarketCohort(
                sector=r.get("sector") or "unknown",
                insider_band=insider_band(
                    None if r.get("accumulation_filings") is None
                    else int(r["accumulation_filings"])),
                short_band=short_band(
                    None if r.get("short_percentile") is None
                    else float(r["short_percentile"])),
                macro=f"{r.get('rates_regime') or 'UNKNOWN'}/"
                      f"{r.get('credit_regime') or 'UNKNOWN'}",
            ).key

            det = _parse(r.get("detection_date"))
            if det is None:
                dropped_undated += 1
                continue
            move = _parse(r.get("move_date"))
            # Realized direction from flow x verdict (the ledger stores no
            # direction column): CONFIRMED moved WITH the flow, NOT_CONFIRMED
            # crossed the OPPOSITE threshold first. NO_MOVE and PENDING have no
            # directional event and are censored below.
            flow = (r.get("flow") or "").lower()
            verdict = (r.get("verdict") or "").upper()
            realized = None
            if flow in ("inflow", "outflow") and verdict in ("CONFIRMED",
                                                             "NOT_CONFIRMED"):
                with_flow = "up" if flow == "inflow" else "down"
                against = "down" if flow == "inflow" else "up"
                realized = with_flow if verdict == "CONFIRMED" else against
            observed = 1 if (move is not None and realized == direction) else 0

            if observed and move is not None:
                dur = (move - det).days
                if dur < 0:
                    dropped_undated += 1
                    continue
            else:
                asd = _parse(as_of)
                dur = min((asd - det).days, horizon) if asd else 0
                if dur < 0:
                    dropped_undated += 1
                    continue

            durations.setdefault(cell, []).append(float(dur))
            events.setdefault(cell, []).append(observed)

        key = cohort.key
        if key not in durations or len(durations[key]) < self.min_cohort:
            return (absent(cohort.label(), horizon,
                           "no comparable sector-windows in this cohort as of this date",
                           as_of=as_of), dropped_undated)

        F, lo, hi, n_ev = km_arrival_probability(durations[key], events[key], horizon)
        if F is None or n_ev == 0:
            return (absent(cohort.label(), horizon,
                           f"cohort of {len(durations[key])} carries no observed "
                           f"{direction}-moves — a rate cannot be measured",
                           n_cohort=len(durations[key]), n_events=0, as_of=as_of),
                    dropped_undated)

        cred = buhlmann_straub(
            {c: float(sum(e)) for c, e in events.items()},
            {c: float(sum(d)) for c, d in durations.items()})
        # Z-CAP (round 7): limited-fluctuation bound √(events/1082) — the uncapped
        # member-day Z read 0.996 on two events (23× over the round-5 cap).
        z = z_cap(cred.z.get(key, 0.0), n_ev)

        all_d = [d for ds in durations.values() for d in ds]
        all_e = [e for es in events.values() for e in es]
        F_port, _, _, _ = km_arrival_probability(all_d, all_e, horizon)
        F_port = F_port if F_port is not None else F

        blended = min(max(z * F + (1 - z) * F_port, 0.0), 1.0)
        lo_b = min(max(z * (lo or 0.0), 0.0), blended)
        hi_b = min(max(z * (hi or 1.0) + (1 - z) * 1.0, blended), 1.0)

        return (Reading(
            state=State.MEASURED, cohort=cohort.label(), horizon_days=horizon,
            value=round(blended, 4), ci_low=round(lo_b, 4), ci_high=round(hi_b, 4),
            n_cohort=len(durations[key]), n_events=n_ev,
            exposure=float(sum(durations[key])), credibility=round(z, 3),
            raw_rate=round(F, 4), base_rate=round(F_port, 4), as_of=as_of,
        ), dropped_undated)


def _parse(value) -> Optional[_dt.date]:
    """Whole-string parse only — §14 forbids raw [:10] date slicing."""
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    s = str(value).strip()
    if not s:
        return None
    try:
        return _dt.date.fromisoformat(s)
    except ValueError:
        pass
    try:
        return _dt.datetime.fromisoformat(s).date()
    except ValueError:
        return None
