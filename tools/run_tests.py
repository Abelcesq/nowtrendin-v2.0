# -*- coding: utf-8 -*-
"""THE TEST RUNNER — the mechanical layer that makes "tested" a checkable claim.

Board finding, 2026-08-20 evening (Guardian's pattern; Challenger F10 found the specific
instance): the repo contained SEVEN test files and NOTHING that ran them. No CI, no hook,
no make target. So every "behavior-tested", "fixture-verified", "36/36 green" in a commit
message or docstring was true the moment it was typed and unverifiable forever after —
and a comment in monitoring_agents cited a fixture (`test_feed_tripwire`) that does not
exist as a file at all. That is the root of the pattern the board named: a claim written
in one register (prose) and enforced in a weaker one (nothing).

This runner + the commit hook that calls it convert the existing test files from dormant
artifacts into a gate that fails.

DESIGN NOTES, each earned:
  * UTF-8 IS FORCED. Without PYTHONIOENCODING=utf-8, test_crypto_flow_a1 dies on a
    Windows console with UnicodeEncodeError on an arrow character — a FALSE FAILURE that
    has nothing to do with the code under test. A gate that cries wolf gets switched off,
    so the runner removes the failure mode rather than documenting it.
  * SUBPROCESS PER FILE. These tests import the engine, touch sqlite, and mutate module
    globals; running them in-process would let one test's state leak into the next and
    produce results that depend on collection order.
  * EXIT CODE IS THE PRODUCT. Human-readable output is secondary; the integer is what the
    hook and any future CI consume.
  * NETWORK-TOUCHING TESTS ARE MARKED, NOT HIDDEN. `--offline` skips them for the commit
    hook (fast, deterministic) and REPORTS the skip by name — never a silent subset. The
    full suite is what runs before a deploy.

Usage:
    python tools/run_tests.py              # everything
    python tools/run_tests.py --offline    # skip network-dependent files, report them
    python tools/run_tests.py --list       # show discovered files and their flags
"""
from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSFER = os.path.join(ROOT, "transfer")

# Tests that reach the network (live feed/page fetches). Skipped by --offline so the
# commit hook stays deterministic; named in the output either way.
NETWORK_TESTS = {"test_etf_issuer_pages.py"}

PER_TEST_TIMEOUT_S = int(os.getenv("RUN_TESTS_TIMEOUT_S", "300"))


def discover() -> list:
    if not os.path.isdir(TRANSFER):
        return []
    return sorted(f for f in os.listdir(TRANSFER)
                  if f.startswith("test_") and f.endswith(".py"))


def run_one(fname: str) -> tuple:
    """Returns (name, ok, seconds, tail). Never raises — a crashed test is a failed
    test, not a crashed runner."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"     # see DESIGN NOTES
    env["PYTHONUTF8"] = "1"
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, fname], cwd=TRANSFER, env=env,
                           capture_output=True, timeout=PER_TEST_TIMEOUT_S)
        out = (p.stdout or b"").decode("utf-8", "replace") + \
              (p.stderr or b"").decode("utf-8", "replace")
        ok = (p.returncode == 0)
    except subprocess.TimeoutExpired:
        return (fname, False, time.time() - t0,
                f"TIMEOUT after {PER_TEST_TIMEOUT_S}s")
    except Exception as exc:                                   # noqa: BLE001
        return (fname, False, time.time() - t0, f"RUNNER ERROR: {exc}")
    lines = [ln for ln in out.splitlines() if ln.strip()
             and not ln.startswith("[startup]")]
    return (fname, ok, time.time() - t0, "\n".join(lines[-3:]) if lines else "(no output)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="skip network-dependent tests (reported, never silent)")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    files = discover()
    if args.list:
        for f in files:
            print(f"  {f}{'   [network]' if f in NETWORK_TESTS else ''}")
        return 0
    if not files:
        print("NO TEST FILES FOUND — that is itself a failure condition.")
        return 1

    skipped = [f for f in files if args.offline and f in NETWORK_TESTS]
    to_run = [f for f in files if f not in skipped]

    print(f"running {len(to_run)} test file(s)"
          + (f", skipping {len(skipped)} network test(s)" if skipped else ""))
    print("=" * 72)
    results, t0 = [], time.time()
    for f in to_run:
        name, ok, secs, tail = run_one(f)
        results.append((name, ok, secs, tail))
        print(f"  {'PASS' if ok else 'FAIL'}  {name:38} {secs:6.1f}s")
        if not ok:
            for ln in tail.splitlines():
                print(f"        {ln[:110]}")

    failed = [r for r in results if not r[1]]
    print("=" * 72)
    print(f"{len(results) - len(failed)} passed, {len(failed)} failed, "
          f"{len(skipped)} skipped, {time.time() - t0:.1f}s total")
    for f in skipped:
        print(f"  SKIPPED (network): {f} — run the full suite before deploying")
    if failed:
        print("\nFAILED: " + ", ".join(r[0] for r in failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
