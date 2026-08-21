# EVIDENCE PACK — the Guardian's remedy, built in three layers; and the three OPEN claims, closed
### Prepared 2026-08-20 (late) for the nine-seat review. Commits: 25def08, c13b055, a650e18.
### Material: everything built since the evening assessment collation (`BOARD_updates-assessment_2026-08-20B.md`).

The evening board's central finding was a PATTERN, not a bug list: *every defect that day
was an integrity claim written in one register and enforced in a weaker one.* The Guardian's
remedy: **every integrity claim ships with the mechanical thing that fails when the claim
stops being true.** The Chairman ordered it built. This is what was built, and what it found.

---

## LAYER 1 — the test runner and gate (`25def08`)

**The root instance.** The repo held SEVEN test files and NOTHING that ran them: no CI, no
hook, no make target. Every "behavior-tested" / "fixture-verified" / "36/36 green" in a
commit message or docstring was true when typed and unverifiable ever after.

- `tools/run_tests.py` — full suite in ~5s, exit code is the product. UTF-8 forced (without
  it `test_crypto_flow_a1` dies on a Windows console with a FALSE failure — a gate that
  cries wolf gets switched off); subprocess per file (these tests mutate module globals);
  network tests skipped BY NAME and reported, never a silent subset.
- **The phantom fixture is now real.** `monitoring_agents` cited `test_feed_tripwire`; no
  such file existed (Challenger F10). `transfer/test_feed_tripwire.py`, 8/8 — including
  **t6: a BROKEN tripwire alarms rather than returning an empty list that reads identically
  to "everything healthy."**
- **THE DEFECT THIS EXPOSED.** Testing whether the new gate fires revealed it did not —
  because **every gate in `commit-msg` used `exit 0` to mean "nothing to say", which ended
  the whole hook.** Cold-start, the firewall gate, and the test gate only ran when a
  collector file happened to be touched, and **any commit carrying `[source-onboarded]`
  bypassed all of them.** Restructured to fall-through; verified on three paths (clean
  passes / failing test refuses EVEN WITH the marker / `TESTS_SKIP=1` bypasses and says so).

## LAYER 2 — the claim register (`c13b055`)

`tools/integrity_gate.py`. Every claim carries a NAMED ENFORCER the gate verifies EXISTS
(test+marker, audit returning ok, hook-gate string, lint id, or sealed doc with a PIT
block). A claim with a missing or fictional enforcer FAILS THE BUILD — inverting the
default under which a claim with nothing behind it was invisible.

Status: **14 of 14 ASSERTED claims enforced, 0 OPEN.**

## LAYER 3 — three lints, each PROVEN to fire (`c13b055`)

| Lint | Defect shape it kills | Fixture result |
|---|---|---|
| L1 sealed constant must be a literal (AST) | `SHADOW_PATIENCE_DAYS` was env-readable — the Forecaster's "90-day calendar quietly re-imposing itself" was one config var away | made it read getenv → **FAIL** |
| L2 a cited test must exist | the `test_feed_tripwire` phantom | cited an imaginary fixture → **FAIL**; register row pointing at a missing file → **FAIL** |
| L3 a field claimed "served" must reach a surface | `d_measured` stored and shown nowhere | now **BLOCKS** (flipped from report when its claim closed) |

## THE THREE OPEN CLAIMS, NOW CLOSED (`a650e18`)

**C-DMEASURED-SERVED.** Engine serves `d_measured` in `D_dark_matter` **and serves
`first_timer_ratio` as NULL when `d_measured=0`**, so a non-contributing input cannot be
rendered as a value (§17) and a floor value cannot wear a measured badge (§16a stage 2).
Web detail row reads **UNMEASURED** with an honest note (not silently dropped); list-row
`ftPct` suppresses. Mobile: `signal.firstTimerRatio ?? 0` — the exact line the Challenger
flagged, which rendered "0%" beside copy asserting it meant something — now renders
`Unmeasured`. `dMeasured` added to the Signal type and the mapper.

**C-KILL-CRITERION.** `audits/forecasts/D_KILL_CRITERION_2026-08-20.md`, sealed
(PIT `caf62911..`, text `403b6a7e..`) BEFORE the window opens and before any result is
knowable. **If at the 2027-02-28 interim the candidate arm has not beaten BOTH nulls at
N ≥ 20 per compared arm, D is DEMOTED** from a scored component to a held-out research
indicator. Every term fixed in advance. Two traps closed explicitly: **UNSCORABLE IS NOT A
PASS** (it defers; a still-UNSCORABLE FINAL readout demotes anyway), and an amendment is
void unless sealed BEFORE the readout that would test it. Also corrects — outside the
sealed body — the Economist's finding that §4 set a threshold for `null_volume` and none
for `null_random`.

**C-SHADOW-SELECTOR.** `transfer/shadow_enroll.py`, written BEFORE the window so the seal
governs the code rather than the reverse. Enforces **cross-arm exclusivity** (candidate and
null_random draw from the same feeds; shared rows would bias the very difference the trial
measures toward zero), a **deterministic null draw** seeded from the sealed prereg hash +
cycle date (a null a human can re-roll is not a null), first-crossing enrollment mirroring
the real ledger, and the `calibrating` stamp from venue age. `enroll()` now writes the
sealed-rule fields and stamps the operative calendar on each row. New claim
**C-NULL-DETERMINISM** added and enforced.

New enforcers: `test_shadow_enroll.py` 11/11 (t6 refuses an unsealed `feed_set`; t7 proves
`instrument_epoch` is derived from LIVE flag state, not the caller's string) and
`test_d_plumbing.py` 10/10 (the cold-start guard finally has a test — including that it
withholds credit on a day-0 community, still RECORDS the author so history accrues, and
DOES credit on a mature one, because a guard that never expires is as broken as one that
never fires).

**Suite: 10 files, 9 run offline, 0 failures, ~5s.** (CORRECTED — the pack first said 11/10. A prose count of its own mechanical artifact, wrong, in the document arguing prose counts must be mechanical; `run_tests.py --list` is the authority.)

## WHAT REMAINS OPEN (not claimed done)

The **paired A/B recompute before 2026-08-27** (retention deadline — after it, today's five
overlapping changes become permanently unattributable); wiki-v3 + GDELT referee arm;
candidate feeds sealed but NOT WIRED (gates 1–3 + acceptance harness per feed, and ERRATUM
01 binds Marca/Kicker behind ES/DE fixtures and an arbiter-locale declaration); rights rows
+ jurisdiction annex; the three corrected figures restated; forecast B5 unresolvable as
sealed; tail accounting still without a disposition; D-REMINE dated 09-30.

## THE QUESTION FOR THE BOARD

Does this actually close the pattern, or does it reproduce it one level up? Specifically:
**is the claim register itself a claim written in a register stronger than its enforcement?**
Attack it. Also assess whether the kill criterion is real or theatre, whether the selector's
determinism survives contact with production, and what the pattern's NEXT costume will be.

## FILES

`tools/run_tests.py` · `tools/integrity_gate.py` · `.githooks/commit-msg` ·
`transfer/shadow_enroll.py` · `transfer/test_feed_tripwire.py` ·
`transfer/test_d_plumbing.py` · `transfer/test_shadow_enroll.py` ·
`audits/forecasts/D_KILL_CRITERION_2026-08-20.md` ·
`audits/forecasts/SHADOW_TRIAL_PREREG_ERRATUM_01_2026-08-20.md` ·
`web-terminal/src/views/Screener.tsx` · `frontend/components/trends/DarkMatterPanel.tsx` ·
prior collation `audits/board/BOARD_updates-assessment_2026-08-20B.md`.
