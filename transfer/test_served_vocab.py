# -*- coding: utf-8 -*-
"""test_served_vocab.py — the SERVED-LAYER forbidden-vocabulary gate (board D6, 2026-09-15).

Board finding (Statistician R4/R6; Buyer's Desk; Operator S5): the unit of audit must equal
the unit of exposure. The forbidden-words check grepped CLIENT BUNDLES and passed while the
pixels the Chairman screenshotted ("money absent", "No proxy money-positioning data for this
coin this cycle") came from ENGINE strings — vocabulary lives in two layers and the gate
watched the wrong one. This test scans the ENGINE SOURCE that produces served crypto strings.

What it checks: every USER-FACING string literal in the scanned files (crypto_money_gradient.py,
and divergence.py read-only) is free of the retired "money" vocabulary. Comments never reach
the wire and docstrings are documentation — both are ALLOWED to keep their history. Identifier-
like literals that are PAYLOAD CONTRACT (enum values such as 'money_absent', dict keys such as
'money_movement', the model-version id) are explicitly allowlisted — the board's hard rule is
that the enum stays stable while the display vocabulary retires.

Mechanics: ast-parse the source; collect every string constant (f-string text segments
included; Python folds adjacent literals into one constant, so multi-line prose is scanned
whole); drop docstrings and exact-match allowlisted literals; normalize hyphens/whitespace and
lowercase; flag any forbidden phrase. A built-in negative fixture proves the scanner CAN fail
(a test that cannot fail is not evidence — board rule).

Standalone: exit 0 on pass, 1 on any violation. Discovered by tools/run_tests.py (test_*.py
in transfer/, subprocess, exit code is the product). Read-only — imports nothing from the
engine and touches no data.
"""
from __future__ import annotations

import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Files whose string literals serve (or could serve) user-facing crypto prose.
# divergence.py is scanned READ-ONLY — owned elsewhere; this gate only reads it.
SCAN_FILES = ["crypto_money_gradient.py", "divergence.py"]

# Retired vocabulary (board D6). Matching is done on normalized text (lowercase,
# hyphens/whitespace collapsed to single spaces), so "money-positioning" and
# "informed-money" are caught by their space-normalized forms.
FORBIDDEN_PHRASES = [
    "money movement",
    "money positioning",     # catches "money-positioning" after normalization
    "money read",
    "money absent",
    "informed money",        # catches "informed-money" after normalization
    "money gradient",
]

# Exact raw literals that are PAYLOAD CONTRACT (enum values / dict keys / model ids) —
# never rendered as prose; renaming them is forbidden by the board (D6 hard constraint).
ALLOWED_LITERALS = {
    "money_absent",              # gap_state enum value
    "money_movement",            # payload field name / components.feeds value
    "money_data_absent",         # payload field name
    "money_floor_required",      # payload field name
    "crypto-money-gradient-v1",  # model-version identifier
    "crypto_money_gradient",     # module name in log prefixes
    "MONEY_MOVEMENT_EXCLUDE",    # env-flag attribute name (getattr), never rendered
}


def _normalize(text: str) -> str:
    text = text.lower().replace("—", " ").replace("–", " ")
    text = re.sub(r"[-_/]+", " ", text)   # hyphenated compounds → spaced phrases
    return re.sub(r"\s+", " ", text)


_FORBIDDEN_NORM = [_normalize(p) for p in FORBIDDEN_PHRASES]


def _docstring_nodes(tree: ast.AST) -> set:
    """ids of Constant nodes that are docstrings (module / class / function firsts)."""
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and \
               isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                out.add(id(body[0].value))
    return out


def scan_source(source: str, fname: str) -> list:
    """Return [(lineno, phrase, snippet)] violations in user-facing string literals."""
    tree = ast.parse(source, filename=fname)
    docstrings = _docstring_nodes(tree)
    violations = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if id(node) in docstrings:
            continue                       # documentation, never served
        raw = node.value
        # Exact contract literals, plus identifier-like log prefixes ("[crypto_money_gradient] ").
        if raw in ALLOWED_LITERALS or raw.strip().strip("[]():") in ALLOWED_LITERALS:
            continue                       # payload contract — key/enum/id, not prose
        norm = _normalize(raw)
        for phrase in _FORBIDDEN_NORM:
            if phrase in norm:
                snippet = raw.strip().replace("\n", " ")
                violations.append((node.lineno, phrase, snippet[:90]))
                break
    return violations


def main() -> int:
    failures = 0

    # 0) The scanner must itself be falsifiable: prove it flags a reintroduction.
    bad_fixture = 'x = {"gap_state": "money_absent", "text": "No proxy money-positioning data"}\n'
    good_fixture = 'x = {"gap_state": "money_absent", "text": "No positioning source reported"}\n'
    if not scan_source(bad_fixture, "<fixture-bad>"):
        print("FAIL  self-check: scanner did NOT flag a known-bad served string")
        failures += 1
    else:
        print("ok    self-check: scanner flags a reintroduced forbidden phrase")
    if scan_source(good_fixture, "<fixture-good>"):
        print("FAIL  self-check: scanner flagged the allowlisted enum value 'money_absent'")
        failures += 1
    else:
        print("ok    self-check: enum-value literal 'money_absent' stays allowed")

    # 1) The engine files.
    for fname in SCAN_FILES:
        path = os.path.join(HERE, fname)
        if not os.path.exists(path):
            print(f"FAIL  {fname}: file not found (scan roster is stale)")
            failures += 1
            continue
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        vio = scan_source(source, fname)
        if vio:
            failures += 1
            print(f"FAIL  {fname}: {len(vio)} retired-vocabulary string(s) in served-layer source")
            for lineno, phrase, snippet in vio:
                print(f"      line {lineno}: contains \"{phrase}\" — {snippet!r}")
        else:
            print(f"ok    {fname}: no retired vocabulary in user-facing string literals")

    if failures:
        print(f"\ntest_served_vocab: FAILED ({failures} check(s))")
        return 1
    print("\ntest_served_vocab: PASSED — served-layer vocabulary clean; enum contract intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
