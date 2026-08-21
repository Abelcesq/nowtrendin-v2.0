# -*- coding: utf-8 -*-
"""ENFORCER for the two panel invariants (claims C-R1-PARTICIPATION, C-R2-REFLEXIVITY).

Both rules already existed as prose and one had already been crossed. The Base Rate
Panel design specified its second surface as "Market Signal (realized EOD direction)",
which `market_accuracy_ledger` grades on close direction — a return forecast — while the
R1 ruling forbidding exactly that sat, verbatim, in `arrival_clock.py`. Nothing enforced
it. This file is the thing that fails when either rule stops holding.

Every test here asserts the refusal actually happened (a raised exception with the right
type), never merely that "nothing went wrong" — per L4: a control that cannot show it
perturbed the system is not a control.

Run: python test_panel_invariants.py   (or via tools/run_tests.py)
"""
from __future__ import annotations

import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import panel_invariants as pi   # noqa: E402

_passed, _failed = 0, 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}  {detail}")


def raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
    except exc:
        return True
    except Exception:
        return False
    return False


def main() -> int:
    print("PANEL INVARIANTS — R1 participation clock, R2 reflexivity")
    print("=" * 70)

    # ── R1 ───────────────────────────────────────────────────────────────────────
    # t1 is the exact surface the round-5 design proposed. It must be refused.
    check("t1 market surface on the price ledger is REFUSED",
          raises(pi.R1Violation, pi.assert_participation_clock,
                 "market", "market_accuracy_ledger", "abnormal_volume"),
          "the design's own surface #2 was accepted — R1 is not enforced")

    check("t2 crypto surface on the price ledger is REFUSED",
          raises(pi.R1Violation, pi.assert_participation_clock,
                 "crypto", "crypto_accuracy_ledger", "abnormal_volume"))

    # t3 — a payoff event smuggled in under an approved-looking ledger name.
    check("t3 unknown/payoff arrival event is REFUSED",
          raises(pi.R1Violation, pi.assert_participation_clock,
                 "market", "some_new_ledger", "eod_price_direction"))

    # t4 — THE CONTROL ON THE CONTROL. A legitimate participation surface must PASS,
    # or the gate is just "refuse everything", which enforces nothing.
    ok = True
    try:
        pi.assert_participation_clock("trend", "accuracy_ledger_enhanced",
                                      "google_trends_breakout")
    except Exception as e:
        ok = False
        print(f"        (raised: {e})")
    check("t4 legitimate trend surface is ALLOWED", ok,
          "the gate refuses valid surfaces too — it is a wall, not a rule")

    check("t5 volume clock on a non-payoff ledger is ALLOWED",
          not raises(Exception, pi.assert_participation_clock,
                     "flow", "flow_ledger", "abnormal_volume"))

    # ── R2 ───────────────────────────────────────────────────────────────────────
    below = pi.reflexivity_status(audience_count=5, displayed_before_arrival=0,
                                  total_rows=100)
    check("t6 below the trip -> publishable, uncontaminated",
          below["publishable"] and not below["contaminated"], str(below))

    part = pi.reflexivity_status(audience_count=5000,
                                 displayed_before_arrival=40, total_rows=100)
    check("t7 above the trip -> publishable but EXCLUDES displayed rows",
          part["publishable"] and part["contaminated"] and part["clean_rows"] == 60,
          str(part))

    gone = pi.reflexivity_status(audience_count=5000,
                                 displayed_before_arrival=100, total_rows=100)
    check("t8 above the trip with no clean rows -> ABSENT, not a number",
          (not gone["publishable"]) and "ABSENT" in gone["note"], str(gone))
    check("t9 the fully-contaminated case RAISES rather than returning a rate",
          raises(pi.R2Violation, pi.assert_not_reflexive, 5000, 100, 100))

    # t10 — the trip must be a sealed literal. If it can be raised from the environment,
    # the reflexivity control can be switched off by whoever benefits from switching it
    # off, with no commit and no trace — the SHADOW_PATIENCE_DAYS lesson.
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "panel_invariants.py"), encoding="utf-8").read()
    line = [l for l in src.splitlines()
            if l.startswith("REFLEXIVITY_AUDIENCE_TRIP")]
    check("t10 the reflexivity trip is a literal, not env-readable",
          bool(line) and "getenv" not in line[0],
          "a threshold readable from the environment is one the beneficiary can retune")

    # t11 — held out: this module must not import anything from the scoring path.
    check("t11 panel_invariants imports nothing from scoring",
          not any(tok in src for tok in ("import gravitational_anomaly_detector",
                                         "import calibration_engine",
                                         "from gravitational_anomaly_detector")),
          "the invariants module reaches into the scorer")

    print("=" * 70)
    print(f"{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
