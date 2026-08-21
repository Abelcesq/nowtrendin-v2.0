# -*- coding: utf-8 -*-
"""ENFORCER for the sealed-document enforcer (claim C-KILL-CRITERION).

WHY THIS FILE EXISTS. Board round 5, 2026-08-21. The Forecaster mutated EVERY binding
number in `D_KILL_CRITERION_2026-08-20.md` — N>=20 -> N>=120, >=10 points -> >=40,
>=3 days -> >=30, i.e. the exact substitution the rejected "Part A" proposed — and
`integrity_gate._enforcer_live('sealed', ...)` returned GREEN. Only deleting the literal
marker string turned it red. One token of a four-parameter criterion was enforced, so a
superseding criterion could have been installed INSIDE the sealed document and no gate
would have noticed. The enforcer now recomputes the hash. This file is the thing that
fails if it ever stops.

AND THE SECOND LESSON, which is the more transferable one. The first negative control
written for this fix REPORTED TWO ENFORCER FAILURES THAT DID NOT EXIST. It mutated
b"is DEMOTED" and b"0.50" — neither string is in the document (it reads "is demoted",
lowercase) — so `bytes.replace()` matched nothing, the file was never modified, the seal
correctly verified, and the test printed "ENFORCER BROKEN" twice. A test that mutates
nothing and concludes from the absence of a failure is the L2 phantom-fixture defect
wearing a negative control's clothes.

  ==> EVERY mutation test in this file ASSERTS THE BYTES ACTUALLY CHANGED, and asserts
      the change landed INSIDE the sealed boundary, BEFORE drawing any conclusion from
      the enforcer's verdict. A negative control that cannot prove it perturbed the
      system is not a control.

Run: python test_seal_enforcer.py   (or via tools/run_tests.py)
"""
from __future__ import annotations

import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

SEAL_DOC = os.path.join("audits", "forecasts", "D_KILL_CRITERION_2026-08-20.md")
REF = SEAL_DOC.replace(os.sep, "/") + "::2027-02-28"

_passed, _failed = 0, 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}  {detail}")


def main() -> int:
    print("SEALED-DOCUMENT ENFORCER — hash recomputation, not substring presence")
    print("=" * 70)
    import integrity_gate as g
    # integrity_gate rebinds sys.stdout to its own TextIOWrapper over the same buffer on
    # import, which invalidates ours mid-run. Re-establish afterwards, or every print()
    # below dies with "I/O operation on closed file" — and a test harness that cannot
    # print cannot report a failure, which is its own small instance of the pattern.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    path = os.path.join(_ROOT, SEAL_DOC)
    if not os.path.exists(path):
        check("sealed doc present", False, SEAL_DOC)
        print("=" * 70)
        return 1
    orig = open(path, "rb").read()

    # The sealed body is everything above the '---' opening the PIT SEAL block.
    lf = orig.replace(b"\r\n", b"\n")
    cut = lf.find(b"\n---\n**PIT SEAL:**") + 1
    check("t1 sealed boundary is locatable", cut > 0,
          "no '---' + '**PIT SEAL:**' marker; the extraction recipe cannot be applied")

    ok, msg = g._enforcer_live("sealed", REF)
    check("t2 unmutated document verifies", ok, msg)

    def mutate(label, mutated, expect_red=True):
        """Apply a mutation, ASSERTING it perturbed the sealed body first."""
        if mutated == orig:
            check(f"{label} [mutation is real]", False,
                  "replace() matched NOTHING — this is the phantom-fixture defect; "
                  "the test would have drawn a conclusion from an unmodified file")
            return
        touched_body = mutated.replace(b"\r\n", b"\n")[:cut] != lf[:cut]
        if not touched_body:
            check(f"{label} [inside sealed body]", False,
                  "edit landed BELOW the boundary; it cannot test the hash")
            return
        try:
            open(path, "wb").write(mutated)
            got_ok, _ = g._enforcer_live("sealed", REF)
        finally:
            open(path, "wb").write(orig)
        check(label, (not got_ok) if expect_red else got_ok,
              "enforcer stayed GREEN on a real change inside the sealed body — it is "
              "checking presence, not content")

    # t3 — THE EXACT SUBSTITUTION THE FORECASTER RAN. This is the regression that matters.
    mutate("t3 Part A number substitution -> RED",
           orig.replace("N ≥ 20".encode("utf-8"), "N ≥ 120".encode("utf-8"))
               .replace(b"10 points", b"40 points"))

    # t4 — the consequence reversed. Case matters; the document says "is demoted".
    mutate("t4 'is demoted' -> 'is promoted' -> RED",
           orig.replace(b"is demoted", b"is promoted"))

    # t5 — a single byte. A hash check must catch this or it is not a hash check.
    mutate("t5 one inserted space -> RED", orig[:200] + b" " + orig[200:])

    # t6 — THE CONTROL ON THE CONTROL. Appending BELOW the boundary must stay GREEN,
    # or nobody can ever add an extraction recipe / errata without breaking the seal.
    mutated = orig + b"\n\nAppended below the seal block; must not affect the hash.\n"
    try:
        open(path, "wb").write(mutated)
        ok_below, msg_below = g._enforcer_live("sealed", REF)
    finally:
        open(path, "wb").write(orig)
    check("t6 append BELOW the boundary stays GREEN", ok_below, msg_below)

    # t7 — the enforcer must refuse a document that publishes no hash at all.
    stripped = orig.replace(b"text_sha256", b"text_removed")
    try:
        open(path, "wb").write(stripped)
        ok_nohash, _ = g._enforcer_live("sealed", REF)
    finally:
        open(path, "wb").write(orig)
    check("t7 a seal with no published hash is REFUSED", not ok_nohash,
          "a document claiming to be sealed while publishing no digest passed")

    ok, msg = g._enforcer_live("sealed", REF)
    check("t8 document restored intact", ok, msg)

    print("=" * 70)
    print(f"{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
