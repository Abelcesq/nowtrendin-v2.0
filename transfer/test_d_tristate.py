# -*- coding: utf-8 -*-
"""ENFORCER for d_measured's THREE states (claim C-D-TRISTATE, ruling 4c).

THE DEFECT. `d_measured` was added by live migration with no backfill, so every row
scored before 2026-08-20 holds NULL — an estimated >90% of distinct topics, and dormant
topics stay NULL forever. The serve guards were written as `!= 0` and `== 0`, which
handles two states. In Python:

    None != 0  ->  True     (so the numeric first_timer_ratio was served)
    None == 0  ->  False    (so the affirmative _explain_d narration was served)

Both guards therefore FELL THROUGH on the largest stratum, and those rows were served a
number plus "No dark matter signatures. Signal appears to originate publicly." — an
affirmative MEASURED claim about a topic whose measurement status is unknown. §16a
stage-2 and §17, violated on the wire. /precompute could not fix it: the block is
computed live, so only a code change could.

THE RULE. Three states, never pooled, and the affirmative branch is opt-IN:

    d_measured == 1     -> D was read; serve the ratio and the real narration
    d_measured == 0     -> we looked, D was unreadable   ("UNMEASURED")
    d_measured is None  -> we never recorded readability ("UNKNOWN")

0 and None both withhold the ratio, but they are DIFFERENT FACTS and must say different
things: "we know it was blind" is not "we don't know". Collapsing them would be the same
honest-absence failure one level in.

Run: python test_d_tristate.py   (or via tools/run_tests.py)
"""
from __future__ import annotations

import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_HERE = os.path.dirname(os.path.abspath(__file__))
_passed, _failed = 0, 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}  {detail}")


def serve(d_measured, ft_ratio=0.42):
    """Replicates the three serve decisions exactly as the payload builds them."""
    ratio = ft_ratio if d_measured == 1 else None
    if d_measured == 1:
        note, prose = None, "AFFIRMATIVE"          # _explain_d(...) in production
    elif d_measured is None:
        note, prose = "UNKNOWN", "UNKNOWN"
    else:
        note, prose = "UNMEASURED", "UNMEASURED"
    return {"first_timer_ratio": ratio, "unmeasured_note": note, "plain_english": prose}


def main() -> int:
    print("D TRI-STATE — measured / blind / unknown are three different facts")
    print("=" * 70)

    m = serve(1)
    check("t1 measured -> ratio served, affirmative narration",
          m["first_timer_ratio"] == 0.42 and m["plain_english"] == "AFFIRMATIVE"
          and m["unmeasured_note"] is None, str(m))

    b = serve(0)
    check("t2 blind (0) -> ratio withheld, UNMEASURED",
          b["first_timer_ratio"] is None and b["plain_english"] == "UNMEASURED", str(b))

    # t3 IS THE REGRESSION. Under the old `!= 0` / `== 0` guards this row served a
    # number and an affirmative claim.
    u = serve(None)
    check("t3 UNKNOWN (None) -> ratio withheld, never affirmative",
          u["first_timer_ratio"] is None and u["plain_english"] != "AFFIRMATIVE", str(u))

    check("t4 UNKNOWN and UNMEASURED are DISTINCT, not pooled",
          u["plain_english"] != b["plain_english"]
          and u["unmeasured_note"] != b["unmeasured_note"],
          "'we don't know' is being rendered as 'we know it was blind'")

    check("t5 the affirmative branch is opt-IN (only exactly 1 reaches it)",
          all(serve(v)["plain_english"] != "AFFIRMATIVE"
              for v in (None, 0, "", "0")),
          "a non-1 value reached the affirmative narration — fail-open again")

    # ── SOURCE GUARDS: the old form must not come back ──────────────────────────
    src = open(os.path.join(_HERE, "gravitational_anomaly_detector.py"),
               encoding="utf-8").read()
    i = src.find('"D_dark_matter"')
    blk = src[i:i + 4200] if i > 0 else ""
    check("t6 the D payload block was located", bool(blk), "anchor moved")

    check("t7 ratio guard is `== 1`, not the fall-through `!= 0`",
          'if s.get("d_measured") == 1 else None' in blk
          and 'if s.get("d_measured") != 0 else None' not in blk,
          "the ratio guard regressed to the form that serves NULL rows a number")

    check("t8 narration guard is `== 1` (affirmative opt-in)",
          re.search(r'if s\.get\("d_measured"\) == 1 else', blk) is not None,
          "the narration guard is not opt-in; a non-1 state can reach _explain_d")

    check("t9 the UNKNOWN branch exists in the payload",
          "UNKNOWN" in blk and "is None else" in blk,
          "no distinct UNKNOWN branch — NULL rows are being pooled with blind rows")

    print("=" * 70)
    print(f"{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
