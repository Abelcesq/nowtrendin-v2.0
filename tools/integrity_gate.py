# -*- coding: utf-8 -*-
"""THE INTEGRITY GATE — Layers 2 and 3 of the Guardian's remedy.

The board's central finding (2026-08-20): every defect that day was the same shape — an
integrity claim written in one register and enforced in a weaker one. The guard documented
as covering a lane it did not cover. The sealed window described as sealed, implemented as
an env var. The honest-absence field announced as "disclosed", implemented as a column no
surface reads. The firewall described as a build failure, implemented as a function nobody
ran. The remedy: EVERY INTEGRITY CLAIM SHIPS WITH THE MECHANICAL THING THAT FAILS WHEN THE
CLAIM STOPS BEING TRUE.

LAYER 2 — THE CLAIM REGISTER (below). Every claim we assert carries a named ENFORCER, and
this tool verifies the enforcer EXISTS. A claim asserted with a missing or fictional
enforcer fails the build. That inverts today's default: a claim without a guard becomes
the defect, instead of being invisible.

  status ASSERTED — we state this publicly/in code. Enforcer must exist. Missing → FAIL.
  status OPEN     — known NOT yet true, deliberately recorded (e.g. the board found the
                    claim false). Listed every run so it cannot fade; never blocks.
                    An OPEN row is a promise with a witness, not a TODO in a drawer.

LAYER 3 — THREE LINTS, one per defect shape actually observed:
  L1 SEALED-CONSTANT-FROM-ENV   a constant declared sealed must be a literal, never
                                os.getenv (the shadow window; SHADOW_PATIENCE_DAYS=90 was
                                one config var away from re-imposing a demo calendar).
  L2 PHANTOM-FIXTURE            a comment citing a test by name must resolve to a test
                                that exists (monitoring_agents cited `test_feed_tripwire`
                                and no such file existed).
  L3 STORED-NEVER-SERVED        a field we describe as served/disclosed must appear on a
                                surface (`d_measured` is stored and shown nowhere).

Usage:  python tools/integrity_gate.py [--verbose]
Exit 0 = every ASSERTED claim has a live enforcer and all lints pass.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSFER = os.path.join(ROOT, "transfer")
TOOLS = os.path.join(ROOT, "tools")
SURFACES = [os.path.join(ROOT, "web-terminal", "src"),
            os.path.join(ROOT, "frontend")]

# ══════════════════════════════════════════════════════════════════════════════════
# LAYER 2 — THE CLAIM REGISTER
# (id, claim, stated_in, status, enforcer_kind, enforcer_ref)
#   kind "test"     -> transfer/<file>.py must exist and contain <marker>
#   kind "audit"    -> module.function must import and return ok
#   kind "hookgate" -> the marker text must appear in .githooks/commit-msg
#   kind "lint"     -> a lint id implemented in this file
# ══════════════════════════════════════════════════════════════════════════════════
CLAIMS = [
    ("C-GUARD-BLOG",
     "The cold-start guard withholds first-timer credit on the BLOG lane until a "
     "community is D_COMMUNITY_MIN_AGE_DAYS old",
     "SHADOW_TRIAL_PREREG §7 (via ERRATUM 01); blog_collectors._first_timer docstring",
     "ASSERTED", "test", "test_d_plumbing.py::C-GUARD-BLOG"),

    ("C-GUARD-DET",
     "The same guard exists on the detector's first-timer path",
     "gravitational_anomaly_detector.check_author_is_first_timer",
     "ASSERTED", "test", "test_d_plumbing.py::C-GUARD-DET"),

    ("C-DMEASURED",
     "d_measured is keyed on RESOLVED AUTHORS, not platform membership — a D of 0 with "
     "d_measured=0 means COULD NOT READ, never 'read quiet'",
     "docs/D_UNIVERSE_STATEMENT.md; compute_dark_matter",
     "ASSERTED", "test", "test_d_plumbing.py::C-DMEASURED"),

    ("C-MASTHEAD",
     "An author identical to its venue (RSS masthead fallback) is never credited as a "
     "person, in either the first-timer path or the indicators",
     "blog_collectors.collect_medium/collect_ghost; darkmatter_indicators",
     "ASSERTED", "test", "test_d_plumbing.py::C-MASTHEAD"),

    ("C-TRIPWIRE-FIRES",
     "The per-feed zero-row tripwire fires on a silent feed, exempts a live one, and "
     "alarms when the tripwire itself breaks",
     "monitoring_agents._feed_silence_tripwire",
     "ASSERTED", "test", "test_feed_tripwire.py::t6"),

    ("C-FIREWALL",
     "A scoring module importing a held-out module fails the build",
     "heldout_registry docstring; shadow_ledger docstring",
     "ASSERTED", "audit", "heldout_registry.audit_firewall"),

    ("C-FIREWALL-GATE",
     "The firewall audit actually RUNS on every commit touching transfer/",
     ".githooks/commit-msg",
     "ASSERTED", "hookgate", "HELD-OUT FIREWALL VIOLATION"),

    ("C-TESTS-RUN",
     "The test suite runs and refuses the commit on failure",
     ".githooks/commit-msg; tools/run_tests.py",
     "ASSERTED", "hookgate", "TEST GATE FAILED"),

    ("C-SEALED-CONSTANTS",
     "The shadow trial's sealed calendar constants are code literals, not env-readable",
     "shadow_ledger docstring; SHADOW_TRIAL_PREREG §7",
     "ASSERTED", "lint", "L1"),

    ("C-NO-PHANTOM-FIXTURE",
     "A comment citing a test by name resolves to a test that exists",
     "the 2026-08-20 board finding (test_feed_tripwire was cited and absent)",
     "ASSERTED", "lint", "L2"),

    # ── CLOSED 2026-08-20 (evening+): all three were OPEN for one working session. ──
    # SCOPE NARROWED 2026-08-20 (late), and the narrowing is the finding. This row read
    # "d_measured is SURFACED to users" and was enforced by L3 — a SOURCE lint. Both were
    # green while production served, for hours, a stored serve_payload written between the
    # commit that added d_measured and the commit that added the plain_english guard: the
    # live object said d_measured=false AND "No dark matter signatures. Signal appears to
    # originate publicly." A claim about PRODUCTION STATE enforced by a check on SOURCE
    # TEXT is the board's pattern inside the register built to end it. A lint cannot see a
    # stale blob, so the claim now says only what the lint proves, and the production half
    # is a separate claim with its own enforcer (C-PAYLOAD-REBUILD).
    ("C-DMEASURED-SERVED",
     "the d_measured UNMEASURED state is WIRED to every surface in source — no surface "
     "renders firstTimerRatio ?? 0 on topics we could not measure. Scope: source wiring "
     "only; this enforcer cannot and does not attest to what production is serving",
     "engine D_dark_matter payload; Screener.tsx; DarkMatterPanel.tsx. Production "
     "verified once, 2026-08-20, engine v370 after a /precompute rebuild, on the blind "
     "row 'хапоэль_беэршева_сабах': d_measured=false, first_timer_ratio=null, "
     "plain_english=UNMEASURED. A dated observation, not a standing guarantee.",
     "ASSERTED", "lint", "L3"),

    # The production half of the claim above. It cannot be verified by a hook either —
    # what a hook CAN do is refuse to let a payload-shape change land while its author
    # believes deploying was sufficient. INV-1 serves stored blobs verbatim past
    # SERVE_LIVECAL_MAX_AGE_H, so a shipped payload change is invisible until rebuilt,
    # and a half-old blob carries new fields beside old prose — a contradiction inside a
    # single served object, which reads to a buyer as fabrication rather than as cache.
    ("C-PAYLOAD-REBUILD",
     "a change to a serve-payload builder cannot land claiming to be live: the commit is "
     "refused unless it asserts [payload-rebuilt], i.e. /precompute was POSTed after the "
     "deploy and a row exercising the changed branch was re-probed",
     ".githooks/commit-msg SERVE-PAYLOAD GATE; endpoint POST /precompute",
     "ASSERTED", "hookgate", "SERVE-PAYLOAD GATE"),

    # Added board round 5. The `sealed` enforcer used to be a substring test; the
    # Forecaster mutated every binding number in the kill criterion and it stayed GREEN.
    # It now recomputes the published text_sha256 over a recorded byte-exact boundary.
    ("C-SEAL-RECOMPUTED",
     "a sealed document's enforcer RECOMPUTES its published text_sha256 over a recorded "
     "byte-exact extraction recipe — editing any binding term turns the gate RED, and "
     "appending errata below the seal boundary does not",
     "tools/integrity_gate.py _enforcer_live(kind='sealed'); the recipe block appended "
     "to D_KILL_CRITERION_2026-08-20.md on 2026-08-21",
     "ASSERTED", "test", "test_seal_enforcer.py::t3"),

    ("C-KILL-CRITERION",
     "D has a pre-committed kill-or-pivot criterion — a stated result, threshold and date "
     "that demote it from a scored component, sealed before any result was knowable",
     "audits/forecasts/D_KILL_CRITERION_2026-08-20.md (PIT caf62911..)",
     "ASSERTED", "sealed", "audits/forecasts/D_KILL_CRITERION_2026-08-20.md::2027-02-28"),

    ("C-SHADOW-SELECTOR",
     "The shadow trial's arm-selection code exists and enforces cross-arm exclusivity, a "
     "deterministic null draw, and the calibrating stamp",
     "transfer/shadow_enroll.py; SHADOW_TRIAL_PREREG §3",
     "ASSERTED", "test", "test_shadow_enroll.py::t1"),

    ("C-NULL-DETERMINISM",
     "The null_random draw is reproducible from the sealed prereg hash + cycle date — a "
     "null a human can re-roll is not a null",
     "shadow_enroll._cycle_seed",
     "ASSERTED", "test", "test_shadow_enroll.py::t2"),
]

# L1 — constants that MUST be literals (module, name)
SEALED_CONSTANTS = [
    ("transfer/shadow_ledger.py", "SHADOW_PATIENCE_DAYS"),
    ("transfer/shadow_ledger.py", "ENROLL_OPEN"),
    ("transfer/shadow_ledger.py", "ENROLL_CLOSE"),
    ("transfer/shadow_ledger.py", "SEALED_FEED_SETS"),
    ("transfer/gravitational_anomaly_detector.py", "REFEREE_FLOOR_PCT"),
    ("transfer/gravitational_anomaly_detector.py", "REFEREE_FLOOR_MIN_N"),
]

# L3 — (field, human description). Must appear on at least one surface.
SERVED_FIELDS = [("d_measured", "the D honest-absence flag")]

_fail: list = []
_note: list = []


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except Exception:
        return ""


# ── LAYER 2 verification ─────────────────────────────────────────────────────────

def verify_claims(verbose: bool) -> None:
    print("LAYER 2 — CLAIM REGISTER")
    print("-" * 72)
    asserted = [c for c in CLAIMS if c[3] == "ASSERTED"]
    open_ = [c for c in CLAIMS if c[3] == "OPEN"]
    for cid, claim, stated, status, kind, ref in asserted:
        ok, why = _enforcer_live(kind, ref)
        if ok:
            if verbose:
                print(f"  OK    {cid:22} -> {kind}:{ref}")
        else:
            _fail.append(f"{cid}: ASSERTED claim has no live enforcer ({why})")
            print(f"  FAIL  {cid:22} -> {why}")
    bad_ids = {f.split(":")[0] for f in _fail}
    enforced = sum(1 for c in asserted if c[0] not in bad_ids)
    print(f"  {enforced} of {len(asserted)} asserted claims enforced")
    if open_:
        print(f"\n  OPEN claims ({len(open_)}) — known not yet true, recorded on purpose:")
        for cid, claim, stated, status, kind, ref in open_:
            print(f"    · {cid:22} {claim[:74]}")


def _enforcer_live(kind: str, ref: str):
    if kind == "none" or not ref:
        return False, "no enforcer named"
    if kind == "test":
        fname, _, marker = ref.partition("::")
        path = os.path.join(TRANSFER, fname)
        if not os.path.exists(path):
            return False, f"test file missing: {fname}"
        if marker and marker not in _read(path):
            return False, f"{fname} does not contain marker {marker!r}"
        return True, ""
    if kind == "audit":
        mod, _, fn = ref.partition(".")
        sys.path.insert(0, TRANSFER)
        try:
            m = __import__(mod)
            r = getattr(m, fn)()
            return (bool(r.get("ok")), "" if r.get("ok") else "audit returns ok=False")
        except Exception as exc:                                # noqa: BLE001
            return False, f"audit failed to run: {str(exc)[:60]}"
    if kind == "hookgate":
        hook = _read(os.path.join(ROOT, ".githooks", "commit-msg"))
        return (ref in hook, "" if ref in hook else "gate text absent from commit-msg")
    if kind == "sealed":
        # RECOMPUTES THE HASH (board round 5, 2026-08-21). It did not before, and the
        # Forecaster produced the receipt: he mutated EVERY binding number in
        # D_KILL_CRITERION — N>=20 -> N>=120, >=10 points -> >=40, >=3 days -> >=30, i.e.
        # the exact Part A substitution — and this branch returned GREEN. Only deleting
        # the literal marker string turned it red. One token of a four-parameter
        # criterion was enforced, so a superseding criterion could have been installed
        # INSIDE the sealed document and nothing would have noticed.
        #
        # THE EXTRACTION RECIPE IS NOW PART OF THE CHECK, not folklore. The same round
        # produced a second receipt for why: two seats disagreed on whether the seal was
        # even reproducible. The Economist reproduced it (round 4); the Forecaster could
        # not, across 36 decode/encode/whitespace recipes. Both were competent; the
        # Forecaster's recipes simply never tried CRLF->LF normalization, which on a
        # Windows checkout is the whole difference. Resolved 2026-08-21 by exhaustive
        # brute force over every prefix length: the seal IS intact, at 4100 bytes of the
        # LF-normalized body (== 4065 CHARACTERS — the em-dashes are 3 bytes each, which
        # is what made the two seats' numbers look incompatible).
        #
        # The lesson is not "the seal was fine." It is that a seal whose extraction
        # recipe is unrecorded is verifiable in principle and unverifiable in practice —
        # which is indistinguishable, to a third party, from a broken seal.
        path, _, marker = ref.partition("::")
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            return False, f"sealed doc missing: {path}"
        body = _read(full)
        if "PIT SEAL" not in body:
            return False, f"{path} carries no PIT seal block"
        if marker and marker not in body:
            return False, f"{path} does not contain {marker!r}"

        raw = open(full, "rb").read().replace(b"\r\n", b"\n")   # canonical: LF
        m = re.search(rb"text_sha256\s*`?([0-9a-f]{64})`?", raw)
        if not m:
            return False, (f"{path} publishes no text_sha256 — a seal that states no "
                           "hash cannot be verified by anyone, including us")
        claimed = m.group(1).decode()

        # The sealed body is everything ABOVE the '---' that opens the PIT SEAL block.
        cut = raw.find(b"\n---\n**PIT SEAL:**")
        if cut < 0:
            return False, (f"{path} has no '---' + '**PIT SEAL:**' boundary; the "
                           "extraction recipe cannot be applied (F5-a1 requires the "
                           "byte-exact boundary be recorded, not inferred)")
        actual = hashlib.sha256(raw[:cut + 1]).hexdigest()
        if actual != claimed:
            return False, (f"{path} SEAL BROKEN — the sealed body no longer hashes to "
                           f"its published text_sha256 (claims {claimed[:16]}.., "
                           f"computes {actual[:16]}..). Either the document was edited "
                           "after sealing, or the recorded boundary is wrong. Do NOT "
                           "re-seal to make this pass: a seal that is silently refreshed "
                           "on edit is a timestamp, not a commitment.")
        return True, ""
    if kind == "lint":
        return (ref in ("L1", "L2", "L3"), "" if ref in ("L1", "L2", "L3")
                else f"unknown lint id {ref}")
    return False, f"unknown enforcer kind {kind}"


# ── LAYER 3 — the three lints ────────────────────────────────────────────────────

def lint_L1_sealed_constants() -> None:
    """A constant declared sealed must be a literal. os.getenv makes it flippable with
    no commit and no trace — the standard this codebase already applied to the referee
    constants, now applied to the trial's own calendar."""
    print("\nLAYER 3 — L1 sealed constants are literals")
    print("-" * 72)
    for rel, name in SEALED_CONSTANTS:
        src = _read(os.path.join(ROOT, rel))
        if not src:
            _fail.append(f"L1: cannot read {rel}")
            print(f"  FAIL  {rel} unreadable")
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            _fail.append(f"L1: {rel} does not parse ({e})")
            continue
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == name:
                        found = True
                        if _calls_getenv(node.value):
                            _fail.append(
                                f"L1: {rel}:{name} is declared SEALED but reads os.getenv")
                            print(f"  FAIL  {name} in {os.path.basename(rel)} reads env")
                        else:
                            print(f"  OK    {name} is a literal")
        if not found:
            _fail.append(f"L1: {rel}:{name} not found (renamed or deleted?)")
            print(f"  FAIL  {name} not found in {os.path.basename(rel)}")


def _calls_getenv(node) -> bool:
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute) and f.attr in ("getenv", "environ"):
                return True
            if isinstance(f, ast.Name) and f.id == "getenv":
                return True
        if isinstance(n, ast.Subscript):
            v = n.value
            if isinstance(v, ast.Attribute) and v.attr == "environ":
                return True
    return False


_CITE = re.compile(r"\b(test_[a-z0-9_]{3,})\b")


def lint_L2_phantom_fixture() -> None:
    """A comment that cites a test by name must resolve to a test that exists. The
    verification may well have been run once, inline — which proves nothing tomorrow."""
    print("\nLAYER 3 — L2 cited fixtures exist")
    print("-" * 72)
    existing = {f[:-3] for f in os.listdir(TRANSFER)
                if f.startswith("test_") and f.endswith(".py")}
    checked = 0
    for folder in (TRANSFER, TOOLS):
        for fname in sorted(os.listdir(folder)):
            if not fname.endswith(".py") or fname.startswith("test_"):
                continue
            for i, line in enumerate(_read(os.path.join(folder, fname)).splitlines(), 1):
                stripped = line.strip()
                if not (stripped.startswith("#") or '"""' in line or "'''" in line
                        or stripped.startswith("*")):
                    continue
                for m in _CITE.finditer(line):
                    cited = m.group(1)
                    checked += 1
                    if cited not in existing:
                        _fail.append(f"L2: {fname}:{i} cites {cited} which does not exist")
                        print(f"  FAIL  {fname}:{i} cites missing fixture {cited}")
    print(f"  OK    {checked} fixture citation(s) all resolve"
          if not any(f.startswith("L2:") for f in _fail) else "")


def lint_L3_stored_never_served() -> None:
    """A field described as served/disclosed must appear on a surface. Disclosed to a
    database column is not disclosed. NOTE: registered OPEN today — the board found this
    claim false, so this lint REPORTS rather than blocks until the UI lands."""
    print("\nLAYER 3 — L3 fields claimed 'served' reach a surface")
    print("-" * 72)
    for field, desc in SERVED_FIELDS:
        hit = None
        for surface in SURFACES:
            if not os.path.isdir(surface):
                continue
            for dirpath, _dirs, files in os.walk(surface):
                if "node_modules" in dirpath:
                    continue
                for f in files:
                    if f.endswith((".ts", ".tsx", ".js", ".jsx")):
                        if field in _read(os.path.join(dirpath, f)):
                            hit = os.path.join(dirpath, f)
                            break
                if hit:
                    break
            if hit:
                break
        if hit:
            print(f"  OK    {field} appears on a surface ({os.path.basename(hit)})")
        else:
            _fail.append(f"L3: {field} ({desc}) is stored but reaches NO surface — "
                         f"disclosed to a database column is not disclosed")
            print(f"  FAIL  {field} stored but on no surface")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    print("=" * 72)
    print("INTEGRITY GATE — every claim ships with the thing that fails when it stops")
    print("being true.  (board 2026-08-20)")
    print("=" * 72)
    verify_claims(args.verbose)
    lint_L1_sealed_constants()
    lint_L2_phantom_fixture()
    lint_L3_stored_never_served()
    print("\n" + "=" * 72)
    if _note:
        print("RECORDED (non-blocking, OPEN claims):")
        for n in _note:
            print(f"  · {n}")
    if _fail:
        print(f"INTEGRITY GATE FAILED — {len(_fail)} problem(s):")
        for f in _fail:
            print(f"  ✗ {f}")
        return 1
    print("INTEGRITY GATE PASSED — every ASSERTED claim has a live enforcer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
