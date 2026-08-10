"""
HELD-OUT FIREWALL REGISTRY — the R1/R2 firewalls as a MECHANISM, not a memo.

Board round 4 (First-Principles Guardian), verified: the `HELD_OUT_ARRIVAL_INPUTS`
registry promised in round 2 existed **once in the whole repository — as prose, inside a
board document**. No Python defined it, and the contract test promised in the same sentence
("greps the resolution path for any price-return import") did not exist either. His words:

    "My R2 firewall is currently a memo, not a mechanism."

This module makes it real. It declares which modules are HELD OUT from scoring, and
provides an AST-based audit that fails when a scoring module imports one. The precedent is
`referee_wikipedia.py`, which has always been held out by convention — convention is what
this replaces.

TWO FIREWALLS ARE ENFORCED HERE
───────────────────────────────
**R1 — the PAYOFF firewall.** No realized price return may be a ledger verdict, a published
headline, or a weight-fitting target. Price may act as a normalizer (e.g. dollar value) and
as non-headline context; it may never be the thing a verdict is scored against. This is what
keeps "we detected it early" a *timing* claim rather than a trading record with the P&L
column hidden.

**R2 — the ARRIVAL firewall.** The ground truth a detection is judged against must be
independent of the thing being judged. Our attention engine may never be the money ledger's
ground truth, and the arrival clock may never become a scoring input. A validator that
shares inputs with what it validates is not a validator.

MEASUREMENT ONLY. This module imports nothing from the project, so it can be safely imported
by anything (including the auditor) without creating the very coupling it polices.
"""
from __future__ import annotations

import ast
import os
from typing import Iterable, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))

# ── The registry ────────────────────────────────────────────────────────────────────────

#: Modules whose outputs are GROUND TRUTH or MEASUREMENT. Nothing that computes a score may
#: import these — doing so would let the thing being measured see its own referee.
HELD_OUT_ARRIVAL_INPUTS = {
    "arrival_clock":       "mainstream-arrival ground truth (abnormal share volume)",
    "flow_ledger":         "the disclosure-to-participation latency register",
    "ledger_survival":     "survival/interval math over ledger outcomes",
    "referee_wikipedia":   "held-out attention referee (pre-existing precedent)",
    "accuracy_ledger_enhanced": "attention accuracy ledger",
    "market_accuracy_ledger":   "market accuracy ledger",
    "crypto_accuracy_ledger":   "crypto accuracy ledger",
    "signal_analysis":     "per-item narrative; measurement-only, never an input",
    "flow_enrollment":     "the enrollment driver — the detector's ONLY doorway into the flow program",
    "insider_flow":        "the append-only Form-4 panel + universe promotion",
    "coinapi_derivs":      "crypto derivatives positioning accumulation (funding/OI) — "
                           "held-out baseline; wiring requires backtest + board",
}

#: Modules that PRODUCE OR CALIBRATE A SCORE. These must never import the held-out set.
#: Keep this list conservative — a false positive here is cheap, a false negative is the
#: whole point of the firewall.
SCORING_MODULES = {
    "market_signal_engine",
    "signal_calibration_integration",
    "calibration_engine",
    "scoring_weights",
    "dual_pathway",
    "community_tiers",
    "crypto_money_gradient",
    "positioning_intel",
    "enterprise_intel",
    # ⚠ ADDED after the Board accountability review (Guardian). Omitting these two made the
    # audit green by scoping it away from the only files where scoring and measurement share
    # a namespace — "the firewall is blind at the one point where the breach will actually
    # occur." `gravitational_anomaly_detector` contains score_topic /
    # compute_nowtrendin_score / apply_calibration AND the API surface, so it necessarily
    # imports ledgers to serve endpoints. Those imports are declared below as ACKNOWLEDGED
    # exceptions rather than hidden by omission — the exception list is now the thing under
    # review, which is the point.
    "gravitational_anomaly_detector",
    "financial_risk_gradient",
}

#: (scoring_module, held_out_module) pairs that are KNOWN and JUSTIFIED. Each needs a reason.
#: An acknowledged exception is auditable; an omitted module is invisible. Adding a pair here
#: is a deliberate act that shows up in review — which is exactly the property the Guardian
#: asked for when he said not to delete the entry once it goes red.
ACKNOWLEDGED_EXCEPTIONS = {
    ("gravitational_anomaly_detector", "accuracy_ledger_enhanced"):
        "serves GET /accuracy/ledger; ledger is DB-driven and read-only from the API path",
    ("gravitational_anomaly_detector", "market_accuracy_ledger"):
        "serves GET /market/accuracy + the deferred-trigger read; read-only",
    ("gravitational_anomaly_detector", "crypto_accuracy_ledger"):
        "serves the crypto ledger endpoint; read-only",
    ("gravitational_anomaly_detector", "signal_analysis"):
        "serves POST /analysis/{kind}; held-out narrative, never an input to a score",
    # Found by widening the audit — a REAL violation the narrow list could not see, then
    # verified safe on DIRECTION. financial_risk_gradient imports the ledger at :2597 for
    # exactly one call, `record_market_detection` (:2600): the scorer WRITES a detection
    # INTO the held-out ledger and never reads an outcome back. That direction is correct —
    # the ledger observes the score; the score must never observe the ledger.
    # ⚠ WHAT THE EXCEPTION REVIEW MUST RE-CHECK: that this stays WRITE-ONLY. The day a read
    # appears here (a hit-rate consulted while scoring), it is circular and the exception
    # must be revoked rather than widened.
    ("financial_risk_gradient", "market_accuracy_ledger"):
        "WRITE-ONLY enrollment: calls record_market_detection only; never reads a verdict",
    # The money-movement wiring (master remediation Step 6, the one construction the freeze
    # permits). The detector's scheduler drives ingestion/enrollment/sweep and its endpoints
    # serve the reports — all through flow_enrollment's wrappers, ONE module wide, so the
    # exception surface stays reviewable. Direction: detector -> flow program, WRITE + serve.
    # ⚠ THE REVIEW MUST RE-CHECK: no flow-ledger VERDICT, arrival, or rate may ever be read
    # back into a score. The day one is, this exception is revoked, not widened.
    ("gravitational_anomaly_detector", "flow_enrollment"):
        "scheduler driver + serve endpoints (/flow/*): write + read-only reports; "
        "never a verdict into a score",
}

#: Identifiers that signal a REALIZED-RETURN computation. Their presence inside a module
#: that resolves an arrival verdict is an R1 breach: the verdict would be scored on payoff.
PAYOFF_TOKENS = ("price_change_pct", "excess_return", "forward_return", "realized_return",
                 "pnl", "sharpe")


# ── The audit ───────────────────────────────────────────────────────────────────────────

def _module_imports(path: str) -> set:
    """Top-level module names imported by a file, via AST (not grep — a grep hit inside a
    docstring or comment is not an import, and treating it as one trains people to ignore
    the alarm)."""
    out = set()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError):
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.add((a.name or "").split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                out.add(node.module.split(".")[0])
    return out


def audit_firewall(root: str = _HERE,
                   scoring: Optional[Iterable[str]] = None,
                   held_out: Optional[Iterable[str]] = None) -> dict:
    """Assert that no scoring module imports a held-out module.

    Returns {ok, violations[], checked, missing[]}. `missing` lists declared modules with no
    file on disk — a registry that drifts from reality is a registry nobody trusts.
    """
    scoring = set(scoring or SCORING_MODULES)
    held = set(held_out or HELD_OUT_ARRIVAL_INPUTS)
    violations, checked, missing = [], 0, []

    for mod in sorted(scoring | held):
        if not os.path.exists(os.path.join(root, f"{mod}.py")):
            missing.append(mod)

    acknowledged = []
    for mod in sorted(scoring):
        path = os.path.join(root, f"{mod}.py")
        if not os.path.exists(path):
            continue
        checked += 1
        for imported in sorted(_module_imports(path) & held):
            entry = {
                "scoring_module": mod,
                "imports_held_out": imported,
                "why_held_out": HELD_OUT_ARRIVAL_INPUTS.get(imported, "held out"),
                "rule": "R2 arrival firewall — a scorer may not see its own referee",
            }
            reason = ACKNOWLEDGED_EXCEPTIONS.get((mod, imported))
            if reason:
                entry["acknowledged_because"] = reason
                acknowledged.append(entry)
            else:
                violations.append(entry)

    return {"ok": not violations, "violations": violations,
            "acknowledged_exceptions": acknowledged,
            "scoring_modules_checked": checked, "held_out_declared": len(held),
            "missing_files": missing}


def audit_payoff_firewall(root: str = _HERE,
                          resolvers: Iterable[str] = ("arrival_clock", "flow_ledger")) -> dict:
    """R1: the modules that RESOLVE an arrival verdict must contain no realized-return
    computation. Deliberately narrow — it polices the *verdict path*, not the whole repo.

    NOTE (Board round 4, O2): `market_accuracy_ledger` legitimately resolves on realized
    price DIRECTION by its own design, and is therefore NOT in `resolvers`. That is the
    older ledger's stated contract. What the Board flagged there is separate and narrower:
    its `_regime_adjusted` excess-return figure must not be PUBLISHED. See that module.
    """
    findings = []
    for mod in resolvers:
        path = os.path.join(root, f"{mod}.py")
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
        except (OSError, SyntaxError):
            continue
        # Walk NAMES only — a mention in a docstring explaining the rule is not a breach.
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        for tok in PAYOFF_TOKENS:
            if tok in names:
                findings.append({"module": mod, "token": tok,
                                 "rule": "R1 payoff firewall — a verdict may not be "
                                         "scored on realized return"})
    return {"ok": not findings, "violations": findings}


def status() -> dict:
    """Combined status for the monitoring fleet (`/monitor` run_all)."""
    a, p = audit_firewall(), audit_payoff_firewall()
    ok = a["ok"] and p["ok"]
    return {
        "agent": "heldout_firewall",
        "status": "ok" if ok else "CRITICAL",
        "arrival_firewall": a,
        "payoff_firewall": p,
        "note": ("Held-out modules are ground truth or measurement. A scoring module that "
                 "imports one lets the measured see its referee; a verdict scored on "
                 "realized return is a trading record wearing a measurement label."),
    }


if __name__ == "__main__":
    import json
    print("=== held-out firewall audit ===\n")
    s = status()
    print(json.dumps(s, indent=1)[:2000])
    print()

    # Self-test: the audit must actually DETECT a violation, not just report ok on a
    # codebase that happens to be clean. A green light from an audit that cannot go red is
    # worse than no audit.
    import tempfile
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "fake_scorer.py"), "w", encoding="utf-8") as fh:
        fh.write("import arrival_clock\ndef score():\n    return 1\n")
    with open(os.path.join(tmp, "arrival_clock.py"), "w", encoding="utf-8") as fh:
        fh.write("X = 1\n")
    bad = audit_firewall(root=tmp, scoring={"fake_scorer"}, held_out={"arrival_clock"})
    assert not bad["ok"] and bad["violations"][0]["imports_held_out"] == "arrival_clock", bad
    print("negative control: a planted violation IS detected  OK")

    # And a clean tree must pass.
    with open(os.path.join(tmp, "clean_scorer.py"), "w", encoding="utf-8") as fh:
        fh.write("import math\ndef score():\n    return math.pi\n")
    good = audit_firewall(root=tmp, scoring={"clean_scorer"}, held_out={"arrival_clock"})
    assert good["ok"], good
    print("positive control: a clean module passes  OK")

    # A held-out name mentioned only in a docstring must NOT count as an import.
    with open(os.path.join(tmp, "doc_scorer.py"), "w", encoding="utf-8") as fh:
        fh.write('"""Never import arrival_clock here."""\nimport math\n')
    doc = audit_firewall(root=tmp, scoring={"doc_scorer"}, held_out={"arrival_clock"})
    assert doc["ok"], "a docstring mention must not be flagged as an import"
    print("docstring mention is not an import (AST, not grep)  OK")

    # ⚠ NEGATIVE CONTROL FOR THE PAYOFF AUDIT (Board accountability review, Guardian).
    # Previously only audit_firewall had one, so there was no evidence in the repo that the
    # R1 half could EVER return red — "an audit with no proof it can fail is decoration",
    # and my claim that the firewall can go red was true of one of the two audits.
    with open(os.path.join(tmp, "bad_resolver.py"), "w", encoding="utf-8") as fh:
        fh.write("def resolve(r):\n    excess_return = r['a'] - r['b']\n"
                 "    return excess_return\n")
    badp = audit_payoff_firewall(root=tmp, resolvers=("bad_resolver",))
    assert not badp["ok"] and badp["violations"][0]["token"] == "excess_return", badp
    print("negative control: payoff audit DETECTS a realized-return token  OK")

    with open(os.path.join(tmp, "good_resolver.py"), "w", encoding="utf-8") as fh:
        fh.write('"""Mentions excess_return only in prose."""\n'
                 "def resolve(r):\n    return r['volume'] > r['baseline']\n")
    goodp = audit_payoff_firewall(root=tmp, resolvers=("good_resolver",))
    assert goodp["ok"], goodp
    print("payoff audit: prose mention is not a violation  OK")

    print(f"\nLIVE TREE: {'CLEAN' if s['status'] == 'ok' else 'VIOLATIONS PRESENT'}")
    if not s["arrival_firewall"]["ok"]:
        for v in s["arrival_firewall"]["violations"]:
            print(f"  {v['scoring_module']} imports {v['imports_held_out']}")
    if s["arrival_firewall"]["missing_files"]:
        print(f"  (declared but absent: {s['arrival_firewall']['missing_files']})")
