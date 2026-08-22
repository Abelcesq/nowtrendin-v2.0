# -*- coding: utf-8 -*-
"""PANEL INVARIANTS — the two rules a base-rate panel may never violate, in code.

HELD OUT. Reads nothing, scores nothing, is imported by nothing in the scoring path.
Its only job is to REFUSE, so that two doctrines that currently exist as prose can fail
a build instead of being re-argued every time someone opens a design document.

────────────────────────────────────────────────────────────────────────────────────
R1 — THE ARRIVAL CLOCK IS NEVER PRICE
────────────────────────────────────────────────────────────────────────────────────
Board round 2 (2026-07-25), restated verbatim in `arrival_clock.py`, in the
First-Principles Guardian's own voice:

    "NOT PRICE. If the confirming event were a price move, then 'we detected it early'
     would mean 'we were early to the move' — a trading record with the P&L column
     hidden. Volume is participation, not payoff. It fires identically on up and down
     moves, so it cannot be quietly converted into a return test."

Round 5 (2026-08-21) found the proposed Base Rate Panel's SECOND SURFACE specified as
"Market Signal (realized EOD direction)". `market_accuracy_ledger` grades on EOD close
direction, so a probability published over it reads:

    P(price moves the way we signalled)

That is a return forecast wearing a frequency's clothes, and it is the one thing this
board has already ruled out BY NAME. The ruling existed; nothing enforced it; the design
crossed it without anyone noticing until a seat went and read the file.

The rule is not "be careful with the market surface." It is: **a panel surface's arrival
event must be participation (volume/breadth), never payoff (price/return).**

────────────────────────────────────────────────────────────────────────────────────
R2 — REFLEXIVITY: THE DISPLAY MAY NEVER FEED THE OUTCOME THAT VALIDATES IT
────────────────────────────────────────────────────────────────────────────────────
The standing circularity invariant is *N never feeds or validates the Gradient Score*.
The Economist found that a displayed arrival probability opens a DIFFERENT loop through
a different door: if showing "38% of topics like this arrived" causes subscriber
attention that feeds back into Google Trends, then subsequent arrivals are partly
ENDOGENOUS and the base rate is measuring its own footprint. The existing invariant does
not cover it, because nothing about N is involved.

Reflexivity scales with audience, so this control is SCALE-TRIGGERED, not decided once.
At five enterprise seats the effect is nil; at API-licensing volume it is the whole
problem. The threshold is fixed NOW, while the audience is small and the answer is
disinterested — which is the only honest moment to fix it (the same reasoning that put a
kill criterion in writing before the trial).

Mechanism:
  1. every rendered rate stamps `panel_displayed_at` for its item;
  2. at each readout, arrival hazard is compared between displayed and never-displayed
     items — the measurement that tells us whether the loop is live;
  3. above `REFLEXIVITY_AUDIENCE_TRIP`, rows whose topic was displayed BEFORE arrival are
     excluded from the base rate, and the panel says so.

Step 2 is the honest part: we do not assume the loop is absent, we measure it.
"""
from __future__ import annotations

# ── SEALED CONSTANTS (literals, guarded by integrity_gate L1) ────────────────────────
# Fixed while the audience is five seats and nobody has an interest in the answer.
REFLEXIVITY_AUDIENCE_TRIP = 5001      # distinct API/UI consumers in a 30-day window
REFLEXIVITY_MIN_PAIRS = 30           # min displayed/not-displayed pairs before judging

# Ledgers whose arrival event is a PAYOFF, not participation. A panel surface may never
# be built on one of these. Kept as data so the refusal is checkable, not editorial.
PAYOFF_LEDGERS = {
    "market_accuracy_ledger": "grades on realized EOD close DIRECTION (payoff)",
    "crypto_accuracy_ledger": "grades on realized coin price direction (payoff)",
}

# Arrival events that satisfy R1: participation, fires identically up and down.
PARTICIPATION_EVENTS = {
    "google_trends_breakout": "search participation vs the topic's own baseline",
    "abnormal_volume": "exchange-reported volume vs the instrument's own baseline",
    "wikipedia_pageviews": "readership participation (held-out referee)",
}


class R1Violation(ValueError):
    """Raised when a panel surface would publish a probability over a payoff event."""


class R2Violation(ValueError):
    """Raised when a base rate would be computed over reflexively-contaminated rows."""


def assert_participation_clock(surface: str, ledger: str, arrival_event: str) -> None:
    """R1 GATE. Refuse a panel surface whose arrival event is a price/return move.

    Call this at panel-surface construction. It raises rather than warns: a warning is a
    thing you read past, and this ruling has already been crossed once in a design
    document while the rule sat in a file nobody opened.
    """
    if ledger in PAYOFF_LEDGERS:
        raise R1Violation(
            f"R1 VIOLATION — surface {surface!r} would publish a probability over "
            f"{ledger!r}, which {PAYOFF_LEDGERS[ledger]}. A probability over a payoff "
            "event is 'P(price moves the way we signalled)' — a return forecast, not a "
            "measurement, and this board ruled it out by name (arrival_clock.py, R1 "
            "firewall). Rebuild the surface on a participation clock "
            f"({', '.join(sorted(PARTICIPATION_EVENTS))}) or do not build it.")
    if arrival_event not in PARTICIPATION_EVENTS:
        raise R1Violation(
            f"R1 VIOLATION — surface {surface!r} declares arrival event "
            f"{arrival_event!r}, which is not a known participation event. R1 requires "
            "an event that fires identically on up and down moves, so it cannot be "
            "quietly converted into a return test. Add it to PARTICIPATION_EVENTS with "
            "a written independence argument, or use one that is already there.")


def reflexivity_status(audience_count: int, displayed_before_arrival: int,
                       total_rows: int, pairs_available: int = 0) -> dict:
    """R2 GATE. Decide whether the base rate may be published, and in what form.

    Returns a dict rather than a bool, because the three states are genuinely different
    and collapsing them is how honest absence turns into a silent number:

      publishable=True,  contaminated=False -> below the trip; publish normally
      publishable=True,  contaminated=True  -> above the trip; publish EXCLUDING
                                               displayed-before-arrival rows, disclosed
      publishable=False                     -> above the trip and the exclusion would
                                               empty the denominator: serve ABSENT
    """
    above = audience_count >= REFLEXIVITY_AUDIENCE_TRIP
    clean = max(0, total_rows - displayed_before_arrival)
    out = {
        "audience_count": audience_count,
        "trip": REFLEXIVITY_AUDIENCE_TRIP,
        "above_trip": above,
        "displayed_before_arrival": displayed_before_arrival,
        "total_rows": total_rows,
        "clean_rows": clean,
        "hazard_comparison_available": pairs_available >= REFLEXIVITY_MIN_PAIRS,
    }
    if not above:
        out.update(publishable=True, contaminated=False,
                   note="Audience below the reflexivity trip; the panel's own display "
                        "cannot plausibly move the outcome it measures.")
        return out
    if clean == 0:
        out.update(publishable=False, contaminated=True,
                   note="ABSENT — above the reflexivity trip and every row in this cell "
                        "was displayed before it arrived, so the base rate would be "
                        "measuring its own footprint. Honest absence, not a number.")
        return out
    out.update(publishable=True, contaminated=True,
               note=f"Above the reflexivity trip: {displayed_before_arrival} of "
                    f"{total_rows} rows were displayed before arrival and are EXCLUDED. "
                    "Rate computed on the remaining rows; exclusion disclosed on the "
                    "panel, not in a methodology page.")
    return out


def assert_not_reflexive(audience_count: int, displayed_before_arrival: int,
                         total_rows: int) -> dict:
    """Raise if a rate would be published over reflexively-contaminated rows."""
    st = reflexivity_status(audience_count, displayed_before_arrival, total_rows)
    if not st["publishable"]:
        raise R2Violation(st["note"])
    return st
