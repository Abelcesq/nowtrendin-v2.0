# D — PRE-COMMITTED KILL-OR-PIVOT CRITERION
### Sealed 2026-08-20, BEFORE the shadow trial opens (2026-09-01) and before any result is knowable.
### Cause: Buyer's Desk, nine-seat board 2026-08-20 — *"What result would make you stop? If there is no such result, you are not running a trial, you are running a demo with a long calendar."*
### Cites: `SHADOW_TRIAL_PREREG_2026-08-20.md` (PIT `e90af6df..`) and `ERRATUM_01` (PIT `6f9ed05f..`).

---

## Why this document exists

D has, until now, had a structure in which **no result changes anything.** The prereg
correctly forbids the trial from touching any score (§10), and a third repair has always
been available — the instrument was disconnected, then the guard was on the wrong lane,
then the denominator, then the extractor. Each diagnosis was true. But an indefinite
supply of true diagnoses is exactly how a component becomes furniture, and how a buyer
reads an unfalsifiable line item.

The Forecaster's framing is the one that binds: *a track record is not a process.* A
criterion written **after** seeing the result is not a criterion. This is written while
the answer is genuinely unknown.

## THE CRITERION (binding)

**If, at the 2027-02-28 interim readout, the `candidate` arm has not beaten BOTH null
arms — at N ≥ 20 resolved races per compared arm, pooled across domains — then D is
DEMOTED: removed as a scored component of the Gradient Score and retained as a held-out
research indicator, pending a NEW sealed hypothesis.**

Definitions, each fixed here so none can be chosen later:

- **"Beaten"** = the H-B comparison sealed in prereg §4: candidate race rate exceeds
  `null_volume` race rate by ≥ 10 points, denominator = topics ENROLLED per arm; AND the
  H-A comparison: median lead-time of resolved candidate races ≥ 3 days earlier than
  control, denominator = resolved races per arm with pre-broken and `calibrating` rows
  excluded.
- **"Both null arms"** = `null_volume` AND `null_random`. Erratum note: prereg §4 sealed a
  threshold only for `null_volume`; for this criterion `null_random` is judged on the same
  10-point race-rate margin. (The prereg's silence on `null_random` was a drafting defect
  the Economist found; it is corrected here rather than in the sealed body.)
- **"N ≥ 20 per compared arm"** — if any compared arm is under N, the comparison reads
  **UNSCORABLE** per prereg §4 and the criterion does not fire. **UNSCORABLE IS NOT A
  PASS.** It defers the decision to the next scheduled readout (2027-05-31, then
  2027-11-30 final) and the deferral is recorded. If the FINAL readout is still
  UNSCORABLE, D is demoted anyway — a component that cannot be measured after fifteen
  months of a purpose-built trial has failed a different way, and "we never got enough
  data" is not a result that earns a place in a score.

## What DEMOTION means, precisely

1. D's weight is removed from the Gradient Score composite; remaining weights renormalise
   under a backtested, board-reviewed change (a score-affecting change like any other —
   demotion does not get a fast path).
2. `darkmatter_indicators` and the D machinery remain, held out, computed and stored.
3. No published accuracy figure may thereafter cite D as a contributing component.
4. The demotion, its date, and the numbers that triggered it are recorded in
   `REGIME_LEDGER.md` and reported alongside any subsequent D claim, permanently — the
   AQR discipline: **publish the bad years.**

## What this criterion does NOT do

It does not fire on a single bad readout, an unwelcome interim, or a null with the
extractor acceptance harness unrun on the affected roster (prereg §10 already rules that
null UNINTERPRETABLE). It does not require anyone to defend D — the criterion is
mechanical, and its trigger is a comparison, not a judgement.

## Amendment rule

This criterion may be amended ONLY by a superseding sealed entry that cites this row, made
**before** the readout that would test it. An amendment made after a readout is void by
construction — that is the whole point of sealing it now.

---
**PIT SEAL:** `kind='forecast'`, `item_key=D-KILL-CRITERION-2026-08-20`,
`row_sha256 caf62911f2f35d8c0c046788ca3f873a3562c7b76f78dc6a420f21936263c235`,
`text_sha256 403b6a7e86fb20794c8637ecdcc25d57c97be3fcc1a94f45d78407ebf6f4c448` (body above
this block). Cites prereg `e90af6df..` and erratum `6f9ed05f..`. Sealed **before the trial
window opens and before any result is knowable**. Enforced by claim `C-KILL-CRITERION` in
`tools/integrity_gate.py`.


---
**EXTRACTION RECIPE (added 2026-08-21, BELOW the sealed boundary — this block is not
part of the hashed body and does not alter it).** Recorded because board round 5 proved
the seal was verifiable in principle and unverifiable in practice: two competent seats
disagreed on whether it reproduced at all. One had it; the other ran 36 decode/encode/
whitespace recipes and failed, because none tried CRLF->LF normalization — which on a
Windows checkout is the entire difference. A seal a third party cannot reproduce is,
to that third party, indistinguishable from a broken one. Per the F5-a1 standard:

    file      : audits/forecasts/D_KILL_CRITERION_2026-08-20.md
    read      : bytes
    normalize : replace CR-LF byte pairs with a single LF byte (canonical LF; this
                repository checks out CRLF on Windows, which is the single reason a
                competent third party ran 36 recipes and could not reproduce this seal)
                in Python:  raw = raw.replace(b"\r\n", b"\n")
    boundary  : everything up to and INCLUDING the newline that precedes the line
                '---' which opens the '**PIT SEAL:**' block
                in Python:  raw[: raw.find(b"\n---\n**PIT SEAL:**") + 1]
                (the marker is: LF, three hyphens, LF, then the literal text
                 '**PIT SEAL:**' — spelled out here because the escape form of this
                 very line was mangled once already, see the note below)
    length    : 4100 bytes == 4065 characters (they differ because the em-dashes are
                3 bytes each in UTF-8 — this is what made two seats' numbers look
                incompatible when both were right)
    digest    : sha256 -> 403b6a7e86fb20794c8637ecdcc25d57c97be3fcc1a94f45d78407ebf6f4c448

Verified 2026-08-21 by exhaustive brute force over EVERY prefix length in three
line-ending variants. `tools/integrity_gate.py` now recomputes this on every run and
refuses the build if the body no longer matches. Do NOT re-seal to make a failure pass:
a seal silently refreshed on edit is a timestamp, not a commitment.
