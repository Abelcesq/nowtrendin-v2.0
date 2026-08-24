"""
crypto_flow_probability_agent.py — Base Rate agent for the CRYPTO section.

HELD OUT.  Read-only.  No INSERT/UPDATE/DELETE, ever.

READ THIS BEFORE ANYTHING ELSE
------------------------------
    THE MONEY LEG DOES NOT EXIST.

As established 2026-08-01 and unchanged since: no source anywhere in the stack
delivers data on large crypto purchases or sales — not for any coin, at any
volume.  Every money-side feed we hold is an EQUITIES instrument:

    Finviz Elite Form-4     US equities            no per-coin read
    WhaleWisdom 13F         US equities            no per-coin read
    QuiverQuant congress    US equities + zeroed by R7
    Databento               equities/futures, referee-only
    crypto-exposure names   COIN, MSTR, MARA…      STRUCTURALLY cannot resolve
                                                    to a coin

Knowing an insider bought MicroStrategy tells you nothing about who bought
Bitcoin.  Therefore this agent returns NOT_APPLICABLE for the money leg — not
ABSENT, and never a number.  The distinction is contractual: ABSENT means "not
today"; NOT_APPLICABLE means "not ever, with the sources we hold."  Collapsing
them is defect D1 from the crypto panel review, and serving a number here would
be defect D2 ("ABSENT — balanced money read"), which asserted an observed-and-
netted neutral flow three lines under a header saying the data was absent.

WHAT THIS AGENT CAN HONESTLY MEASURE TODAY
------------------------------------------
    P(price move +8% within 45 days | attention cohort)
    P(price move -8% within 45 days | attention cohort)

conditioned on ATTENTION-side cohort factors and macro regime only.  That is a
real, defensible measurement.  It is NOT a money-flow measurement, and the
payload says so in a field the UI cannot drop.

    crypto_accuracy_ledger has been grading a signal with ZERO money input.
    Nothing here fixes that; this agent exposes it rather than papering over it.

THE FIX, PRE-WIRED AND DISABLED
-------------------------------
CFTC Commitments of Traders is free, regulated, primary-source, and carries the
exact institutional split the thesis requires (Traders in Financial Futures:
Dealer/Intermediary, Asset Manager/Institutional, Leveraged Funds, Other,
Nonreportable).  Its trader-COUNT columns are a direct Seyhun cluster-buying
analogue inside a regulated crypto instrument.

    https://publicreporting.cftc.gov/resource/gpe5-46if.json
      ?cftc_contract_market_code=133741&$limit=52
      &$order=report_date_as_yyyy_mm_dd desc

    133741  Bitcoin CME            133742  Micro Bitcoin
    146021  Ether cash-settled     146022  Micro Ether

HARD RULE if COT is ever enabled (see COT_KNOWABLE_AT_RULE below): stamp
knowable_at to the FRIDAY 15:30 ET PUBLICATION, never the Tuesday as-of date.
Getting that backwards back-dates knowledge by three days and contaminates
every ledger downstream.  The gate in this file refuses COT rows that violate
it rather than trusting the caller.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
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

__all__ = ["CryptoFlowProbabilityAgent", "CryptoCohort", "CryptoReadout",
           "COT_CONTRACT_CODES", "cot_knowable_at"]

DEFAULT_HORIZON_DAYS = 45      # matches crypto_accuracy_ledger's 8% / 45d rule
MOVE_THRESHOLD = 0.08

COT_CONTRACT_CODES = {
    "BTC": "133741",        # Bitcoin CME
    "BTC_MICRO": "133742",  # Micro Bitcoin
    "ETH": "146021",        # Ether cash-settled
    "ETH_MICRO": "146022",  # Micro Ether
}

MONEY_LEG_REASON = (
    "No source in the stack delivers per-coin money movement. Every money-side "
    "feed we hold is an equities instrument; crypto-exposure equities "
    "(COIN/MSTR/MARA) structurally cannot resolve to a coin. This is not a "
    "gap in today's data — it is a gap in the source set."
)


def cot_knowable_at(report_date_as_of: _dt.date) -> _dt.date:
    """
    COT_KNOWABLE_AT_RULE.

    The CFTC report is AS-OF the preceding Tuesday but is PUBLISHED Friday
    15:30 ET.  knowable_at must be the Friday.  Stamping the Tuesday back-dates
    knowledge by three days and silently contaminates every point-in-time read
    built on it.

    >>> cot_knowable_at(_dt.date(2026, 8, 18)).isoformat()   # a Tuesday
    '2026-08-21'
    """
    if report_date_as_of.weekday() != 1:  # 1 == Tuesday
        raise ValueError(
            f"COT as-of date must be a Tuesday, got {report_date_as_of} "
            f"(weekday {report_date_as_of.weekday()}). Refusing rather than "
            f"guessing the publication date."
        )
    return report_date_as_of + _dt.timedelta(days=3)


# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CryptoCohort:
    coin: str
    attention_band: str      # QUIET | RISING | ELEVATED
    volatility_band: str     # LOW | MID | HIGH (trailing realised vol pctile)
    macro: str               # rates/credit regime key, or UNKNOWN

    @property
    def key(self) -> str:
        return f"{self.coin}|{self.attention_band}|{self.volatility_band}|{self.macro}"

    def label(self) -> str:
        return (f"{self.coin} · attention {self.attention_band.lower()} · "
                f"vol {self.volatility_band.lower()} · macro {self.macro}")


def attention_band(detection_score: Optional[float]) -> str:
    if detection_score is None:
        return "unknown"
    if detection_score >= 70:
        return "ELEVATED"
    if detection_score >= 40:
        return "RISING"
    return "QUIET"


def volatility_band(percentile: Optional[float]) -> str:
    if percentile is None:
        return "unknown"
    if percentile >= 0.70:
        return "HIGH"
    if percentile <= 0.30:
        return "LOW"
    return "MID"


@dataclass
class CryptoReadout:
    coin: str
    cohort: Optional[CryptoCohort]
    as_of: str
    up_move: Reading          # attention-conditioned, honest
    down_move: Reading        # attention-conditioned, honest
    money_inflow: Reading     # NOT_APPLICABLE by construction
    money_outflow: Reading    # NOT_APPLICABLE by construction
    cot_enabled: bool = False
    dropped_undated: int = 0    # rows with unparseable/impossible dates (counted, round 8)
    calibration: Optional[dict] = None

    def to_payload(self) -> dict:
        return {
            "coin": self.coin,
            "cohort": self.cohort.label() if self.cohort else None,
            "cohort_key": self.cohort.key if self.cohort else None,
            "as_of": self.as_of,
            "dropped_undated": self.dropped_undated,
            "price_move_up": self.up_move.to_payload(),
            "price_move_down": self.down_move.to_payload(),
            "money_inflow": self.money_inflow.to_payload(),
            "money_outflow": self.money_outflow.to_payload(),
            # This field exists so a UI cannot render the price legs as if they
            # were money legs. It is not decoration.
            # A5 FIX (round 7, Forecaster + Buyer's Desk independently): this
            # used to flip on the CONSTRUCTOR FLAG (`cot_enabled`) while the
            # legs themselves read ABSENT/NOT_APPLICABLE — two fields in one
            # payload disagreeing, the 2026-08-20 incident class verbatim. It
            # is now DERIVED from the actual leg states: available means a
            # money leg actually MEASURED something, nothing else.
            "money_leg_available": (
                self.money_inflow.state is State.MEASURED
                or self.money_outflow.state is State.MEASURED
            ),
            # A5 FIX, second half: COT never enters any cohort key anywhere in
            # this module (a wired-and-valid COT row produces at most a future
            # cohort FACTOR, and that stratification does not exist yet), so
            # listing "cftc_cot_positioning" under conditioned_on was a claim
            # the code does not implement. The list states what the cohort key
            # actually contains — and nothing else.
            "conditioned_on": ["attention", "volatility", "macro"],
            "cot_wired": self.cot_enabled,   # instrumentation status, NOT a conditioning claim
            "ledger_warning": (
                "crypto_accuracy_ledger grades a signal with no money input. "
                "The price legs below are attention-conditioned only."
            ),
            "calibration": self.calibration,
            "disclaimer": (
                "Historical frequency for a matched cohort. Measurement only — "
                "not financial, investment, or legal advice."
            ),
        }


# ---------------------------------------------------------------------------

class CryptoFlowProbabilityAgent:
    """
        agent = CryptoFlowProbabilityAgent(fetch=db_compat.fetch_all)
        readout = agent.score("BTC", as_of="2026-08-21")

    COT wiring is present and OFF.  Turning it on is a source-onboarding event
    under §16 (five gates) and a cold-start event under §16a, not a flag flip:

        agent = CryptoFlowProbabilityAgent(
            fetch=..., cot_provider=my_cot_reader, enable_cot=True)

    `cot_provider(coin, as_of) -> dict | None` must return rows already stamped
    with a Friday `knowable_at`. The agent re-checks and REFUSES rows that fail
    the rule rather than trusting the caller.
    """

    #: must return: coin, detection_score, vol_percentile
    #:
    #: ROUND-8 HONESTY NOTE: `crypto_signal_state` does not exist anywhere in
    #: the codebase yet — the declared interface for the forward-only
    #: PIT-stamped state layer.  Until it is built this query THROWS and the
    #: agent serves INSTRUMENT_ERROR (a fact about us), never a fabricated
    #: "no signal state".
    SQL_COIN_STATE = """
        SELECT coin, detection_score, vol_percentile
          FROM crypto_signal_state
         WHERE coin         = ?
           AND signal_date <= ?
         ORDER BY signal_date DESC
         LIMIT 1
    """

    #: cohort population. must return: coin, detection_date, move_date,
    #: direction, detection_score, vol_percentile, rates_regime, credit_regime
    #: cohort population: resolved rows UNION pending rows, against the REAL
    #: schema (crypto_accuracy_ledger.init_crypto_ledger_db).  Takes TWO bind
    #: parameters, both = as_of.
    #:
    #: ROUND-8 SCHEMA FIX (fixture-circularity): the old query selected
    #: direction / detection_score / vol_percentile / rates_regime /
    #: credit_regime — none of which exist in the real table (it has coin,
    #: flow, money_movement, verdict, move_date...).  Realized direction is
    #: derived in Python from flow x verdict, exactly as in the market agent.
    #: The cohort covariates (attention band, volatility band, macro) await
    #: forward-only PIT stamping; until then historical rows band "unknown"
    #: and a real-banded target cohort is honestly ABSENT.  money_movement is
    #: deliberately NOT aliased onto detection_score — they are different
    #: quantities, and a rename is not a measurement.
    SQL_COHORT = """
        SELECT c.coin,
               c.detection_date,
               c.move_date,
               c.flow,
               c.verdict,
               0 AS is_pending
          FROM crypto_accuracy_ledger c
         WHERE c.detection_date <= ?
        UNION ALL
        SELECT p.coin,
               p.detection_date,
               NULL AS move_date,
               p.flow,
               'PENDING' AS verdict,
               1 AS is_pending
          FROM crypto_pending_detections p
         WHERE p.detection_date <= ?
           AND p.status = 'pending'
    """

    SQL_CALIBRATION = """
        SELECT served_probability, observed_outcome
          FROM base_rate_calibration_log
         WHERE kind = 'crypto'
           AND resolved_at <= ?
    """

    def __init__(self, fetch: Fetch,
                 macro_provider: Optional[Callable[[str], object]] = None,
                 cot_provider: Optional[Callable[[str, str], Optional[dict]]] = None,
                 *, horizon_days: int = DEFAULT_HORIZON_DAYS,
                 enable_cot: bool = False, min_cohort: int = 1):
        self.fetch = fetch
        self.macro_provider = macro_provider
        self.cot_provider = cot_provider
        self.horizon_days = horizon_days
        self.min_cohort = max(1, min_cohort)
        # Default OFF. A source that has not passed §16's five gates does not
        # get to enter a cohort because a constructor argument said so.
        self.enable_cot = bool(enable_cot and cot_provider is not None)

    # -- public -------------------------------------------------------------

    def score(self, coin: str, *, as_of: Optional[str] = None,
              horizon_days: Optional[int] = None) -> CryptoReadout:
        as_of = as_of or _dt.date.today().isoformat()
        horizon = horizon_days or self.horizon_days
        coin = coin.upper()

        # The money legs. These are NOT_APPLICABLE unless COT is genuinely
        # wired AND its rows pass the knowable_at rule. There is no branch in
        # this method that can produce a money number otherwise.
        money_in, money_out = self._money_legs(coin, as_of, horizon)

        macro_key = self._macro_key(as_of)
        cohort, cohort_err = self._cohort_for(coin, as_of, macro_key)
        if cohort is None:
            if cohort_err:
                # INSTRUMENT_ERROR ≠ ABSENT (round 7): a thrown query is a fact
                # about US, never "no signal state for this coin".
                r = instrument_error(coin, horizon, cohort_err, as_of=as_of)
                return CryptoReadout(
                    coin=coin, cohort=None, as_of=as_of,
                    up_move=r, down_move=r,
                    money_inflow=money_in, money_outflow=money_out,
                    cot_enabled=self.enable_cot,
                )
            reason = "no crypto signal state for this coin as of this date"
            return CryptoReadout(
                coin=coin, cohort=None, as_of=as_of,
                up_move=absent(coin, horizon, reason, as_of=as_of),
                down_move=absent(coin, horizon, reason, as_of=as_of),
                money_inflow=money_in, money_outflow=money_out,
                cot_enabled=self.enable_cot,
            )

        rows, rows_err = self._cohort_rows(as_of)
        if rows_err:
            r = instrument_error(cohort.label(), horizon, rows_err, as_of=as_of)
            return CryptoReadout(
                coin=coin, cohort=cohort, as_of=as_of,
                up_move=r, down_move=r,
                money_inflow=money_in, money_outflow=money_out,
                cot_enabled=self.enable_cot,
            )
        up, undated = self._reading(rows, cohort, as_of, horizon, direction="up")
        down, _ = self._reading(rows, cohort, as_of, horizon, direction="down")

        return CryptoReadout(
            coin=coin, cohort=cohort, as_of=as_of,
            up_move=up, down_move=down,
            money_inflow=money_in, money_outflow=money_out,
            cot_enabled=self.enable_cot,
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
            "scope_warning": ("graded against coin price direction only; the "
                              "cohort carries no money-side input"),
        }

    # -- money legs ---------------------------------------------------------

    def _money_legs(self, coin: str, as_of: str, horizon: int):
        """
        Returns (inflow, outflow). NOT_APPLICABLE unless COT is wired AND the
        rows pass the knowable_at rule.
        """
        if not self.enable_cot:
            return (not_applicable(coin, horizon, MONEY_LEG_REASON, as_of=as_of),
                    not_applicable(coin, horizon, MONEY_LEG_REASON, as_of=as_of))

        if coin not in COT_CONTRACT_CODES:
            reason = (f"no CME futures contract maps to {coin}; CFTC COT covers "
                      f"{', '.join(sorted(COT_CONTRACT_CODES))} only")
            return (not_applicable(coin, horizon, reason, as_of=as_of),
                    not_applicable(coin, horizon, reason, as_of=as_of))

        try:
            row = self.cot_provider(coin, as_of)  # type: ignore[misc]
        except Exception:
            row = None

        if not row:
            reason = "CFTC COT wired but returned no report knowable as of this date"
            return (absent(coin, horizon, reason, as_of=as_of),
                    absent(coin, horizon, reason, as_of=as_of))

        # Enforce COT_KNOWABLE_AT_RULE here rather than trusting the provider.
        if not self._cot_row_is_knowable(row, as_of):
            reason = ("CFTC COT row rejected: knowable_at is not the Friday "
                      "publication date, or is later than the requested as_of. "
                      "Refusing a back-dated row.")
            return (absent(coin, horizon, reason, as_of=as_of),
                    absent(coin, horizon, reason, as_of=as_of))

        # A wired-and-valid COT row still does not by itself produce a
        # frequency: it produces a cohort FACTOR. Until the crypto ledger has
        # resolved rows stratified by that factor, the money leg is ABSENT, not
        # measured. This is deliberately conservative — a positioning reading is
        # not a probability.
        reason = ("CFTC COT positioning is available and valid, but the crypto "
                  "ledger has no resolved rows stratified by it yet — a "
                  "positioning reading is not a frequency")
        return (absent(coin, horizon, reason, as_of=as_of),
                absent(coin, horizon, reason, as_of=as_of))

    @staticmethod
    def _cot_row_is_knowable(row: dict, as_of: str) -> bool:
        try:
            rep_d = _parse(row.get("report_date_as_yyyy_mm_dd")
                           or row.get("report_date"))
            declared_d = _parse(row.get("knowable_at"))
            if rep_d is None or declared_d is None:
                return False
            expected = cot_knowable_at(rep_d)
            asd = _parse(as_of)
            if asd is None:
                return False
            return declared_d == expected and declared_d <= asd
        except Exception:
            return False

    # -- internals ----------------------------------------------------------

    def _macro_key(self, as_of: str) -> str:
        if self.macro_provider is None:
            return "UNKNOWN/UNKNOWN"
        try:
            m = self.macro_provider(as_of)
            return getattr(m, "key", "UNKNOWN/UNKNOWN")
        except Exception:
            return "UNKNOWN/UNKNOWN"

    def _cohort_for(self, coin: str, as_of: str, macro_key: str):
        """Returns (cohort_or_None, error_message_or_None) — round-7 discipline:
        a thrown query surfaces as an instrument fault, never as missing data."""
        try:
            rows = self.fetch(self.SQL_COIN_STATE, (coin, as_of))
        except Exception as exc:
            return None, f"coin-state query failed: {type(exc).__name__}: {exc}"
        if not rows:
            return None, None
        r = rows[0]
        det = r.get("detection_score")
        vol = r.get("vol_percentile")
        if det is None and vol is None:
            return None, None
        return CryptoCohort(
            coin=coin,
            attention_band=attention_band(None if det is None else float(det)),
            volatility_band=volatility_band(None if vol is None else float(vol)),
            macro=macro_key,
        ), None

    def _cohort_rows(self, as_of: str):
        """Returns (rows, error_message_or_None). Two bind parameters: the
        resolved arm and the pending arm of the UNION."""
        try:
            return list(self.fetch(self.SQL_COHORT, (as_of, as_of))), None
        except Exception as exc:
            return [], f"crypto ledger query failed: {type(exc).__name__}: {exc}"

    def _reading(self, rows: List[dict], cohort: CryptoCohort, as_of: str,
                 horizon: int, *, direction: str) -> tuple:
        """Returns (Reading, dropped_undated). Every row either enters a risk
        set or is counted — no uncounted exit doors (round 8)."""
        durations: Dict[str, List[float]] = {}
        events: Dict[str, List[int]] = {}
        dropped_undated = 0

        for r in rows:
            # Bands read the row's stamps; the real ledger carries none yet
            # (forward-only PIT stamping pending), so bands are honestly
            # "unknown" — never recomputed from current state.
            cell = CryptoCohort(
                coin=(r.get("coin") or "unknown").upper(),
                attention_band=attention_band(
                    None if r.get("detection_score") is None
                    else float(r["detection_score"])),
                volatility_band=volatility_band(
                    None if r.get("vol_percentile") is None
                    else float(r["vol_percentile"])),
                macro=f"{r.get('rates_regime') or 'UNKNOWN'}/"
                      f"{r.get('credit_regime') or 'UNKNOWN'}",
            ).key

            det = _parse(r.get("detection_date"))
            if det is None:
                dropped_undated += 1
                continue
            move = _parse(r.get("move_date"))
            # Realized direction from flow x verdict (no direction column
            # exists): CONFIRMED moved WITH the flow, NOT_CONFIRMED crossed
            # the OPPOSITE threshold first; NO_MOVE / PENDING are censored.
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
                           "no comparable coin-windows in this cohort as of this date",
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
