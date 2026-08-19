# BOARD COLLATION — Engineering Review of the 2026-08-18 Ships (U1–U4)
### Nine seats, convened 2026-08-18 (second convening of the day) · Chairman-requested review of the four deployed updates

**Items:** **U1** A2.2 as-of-keyed ETF reconcile (deployed v345) · **U2** bitemporal PIT store
(ruling (b) executed) · **U3** NTI-SD50 frozen-rule index (ruling (c) executed) · **U4** forecast
register + dual-anchor PIT sealing (standing consequence 3 executed).

All nine seats received the identical evidence pack and convened independently; every seat read
the shipped code directly, and four seats (Outsider, Guardian, Challenger, Executioner)
independently re-ran all four test suites locally — **all pass as claimed (33/33, 14/14, 17/17,
13/13)**. Two seats verified in git that register r1 and the index code shipped in the same
commit (148487d), proving freeze-before-first-value. This is a collation, not a blend.

---

## VERDICT TABLE

| Seat | U1 A2.2 | U2 PIT store | U3 NTI-SD50 | U4 Forecast register |
|---|---|---|---|---|
| Challenger | A-w-C (regime-dependent re-arm power; basis N=4/N=2) | A-w-C (completeness unwatched; no external anchor; midnight grace) | A-w-C (duplicate-day race; NULL→0.0 in universe_count) | A-w-C (F1–F4 bands violate the register's own Brier rule) |
| Guardian | A-w-C (within-A2.2 verdict mutability — log transitions) | A-w-C (external seal anchor; accrual monitor) | A-w-C (RC4 trigger not executed — absent from DEFERRED_ITEMS) | A-w-C (dual anchor is attestation, not verification — machine-check the text hash) |
| Expansionist | A-w-C (US-market hard-codes; Labor-Day watch; basis dict → registry at scale) | A-w-C (midnight seal/write race → false tamper alarm; unique constraint; batched writes at 100×) | A-w-C (TOCTOU one-value-per-day race; index inherits Anglophone roster bias — never imply "global") | APPROVE (manual register correct at this cadence) |
| Outsider | A-w-C (holiday calendar BEFORE 2026-09-07; basis small-N; watch item to account) | A-w-C (self-anchored chain = the gap a security reviewer finds in hour one; PIT-silence alarm; index the table now) | A-w-C (unique constraint; RC4 into DEFERRED_ITEMS; loop-liveness check) | APPROVE (permanency-gate asset; when does the Chairman ruling on F5 conditions land?) |
| Executioner | ACCEPT (fix-fwd: finalized-verdict overwrite protection; re-arm bias term counts FMP rows — filter by src) | ACCEPT (PIT_STORE flag gates only the sealer, not writes; unique constraint pre-scale-out; external anchor) | ACCEPT (RC4/RC3 into DEFERRED_ITEMS this week — the only concrete miss) | ACCEPT (no forecast_resolution code path yet — defer, log it; run the one-time text-hash verify) |
| Economist | A-w-C (basis-drift monitor that ALARMS; promote Bitwise; Labor Day) | APPROVE (completeness auditor = highest priority; anchor the chain; event_date semantics note) | A-w-C (level ≠ returns; universe-size confound; **stamp param_version into the payload — no silent splices**; RC4 now while baseline is free) | APPROVE (F1–F4 point convention now; anchor verifier) |
| Operator | DURABLE-provisional (deployed, UNPROVEN — dated check: zero asof-scored intervals by 08-21 EOD = defect, not cold start) | DURABLE conditional on S1/S2 (**tamper-evident ≠ loss-evident; one DB, no scheduled backup found, no off-box seal copy — anchor this week**) | DURABLE (cleanest of the four; unique index; RC4 gate armed) | DURABLE (extend the anchor file to all forecast hashes) |
| Statistician | SOUND impl, OVERFIT-RISK on basis table (3rd join-rule revision — disclose; per-FUND ≥10-day stamp+value test before re-arm is acted on) | SOUND — **confers grade B, not A, until the seal head is externally anchored; every unanchored day is unrecoverable** | SOUND impl (constants are conventions — demand the "no variant was peeked" attestation; ΔLevel confounds four things; param_version stamp) | SOUND (F1–F4 not Brier-scorable; forecast-census rule vs file-drawer sealing) |
| Forecaster | WELL-SCORED (**defect: "fires forever" is not implemented — the 21-day window ages bad rows out of the gate**; add prior-rule tally) | WELL-SCORED (counted fail-open — failure counter in status(); external anchor; ~24h unsealed window stated in DDQ language) | WELL-SCORED (**R8 reproducibility defect: payload stores 1dp constituents but the level is computed on unrounded values — sealed 75.45 may recompute 75.44**; fix full-precision forward + register erratum) | WELL-SCORED (no material drift F5 register vs authored text; record text_sha256 + byte boundaries in register — close the anchor loop in both directions) |

**Bottom line: 36/36 seat-item verdicts are approvals** (with conditions). No REJECT, no CUT, no
MIS-SCORED. Every seat independently confirmed the implementations faithfully execute the rulings
that ordered them, the held-out walls hold (nothing reads any new store into scoring; the accuracy
ledgers are byte-untouched), and errors are consistently pushed toward conservative states
(gate FAIL, ABSENT, covered-not-scored, unresolved=NO).

---

## THE CONVERGED FINDING (the strongest cross-seat signal — 8 of 9 seats independently)

**The seal chain is self-anchored: every integrity artifact shipped today lives in, and is
verified from, the one database it attests.** The chain is *tamper-evident* (proven by tests)
but not *loss-evident* (Operator): a restore-from-backup would silently truncate the record and
re-verify clean; a DB-privileged actor could rewrite and re-seal the entire chain; and the
Operator could find **no scheduled backup for the engine DB anywhere in the audits**. The
Statistician's formulation: as deployed the PIT store confers provenance **grade B, not A** — and
since the epoch accrues toward A only from the day anchoring starts, **every day without an
external anchor is an epoch-day that can never be upgraded retroactively.** The fix every seat
converged on is the pattern U4 already uses: automatically export each day's `seal_sha256` to a
git-committed append-only file. Cost ≈ one small job; the Operator's deadline: **this week.**

## CONSOLIDATED CONDITIONS (deduplicated, ranked by seat-count × severity)

**P0 — this week, all cheap, none score-affecting:**
1. **External seal anchoring** (8 seats): daily append of `seal_date|row_count|seal_sha256` to a
   git-committed audits file; extend the same file to forecast row hashes (Operator). Plus: a
   verified `pg:backups` schedule on the engine DB + a storage-growth plan (Operator,
   Expansionist — the PIT table is never-pruned by design on a plan §13 already calls tight).
2. **PIT completeness monitor** (7 seats): pipeline_integrity parity check — velocity_scores rows
   written today vs `trend_score` PIT rows (and market/crypto cycles vs their kinds); plus a
   monotonic write-failure counter surfaced in `status()` (Forecaster). Fail-open must never be
   fail-silent; the chain proves integrity, not completeness.
3. **Partial unique index** on `pit_observations(kind, item_key, event_date)` for
   `kind='index_value'` (5 seats): the one-value-per-day invariant is currently a check-then-write
   race, and a duplicate in an append-only store is a permanent blemish. An index is additive —
   append-only survives intact. Do it before any dyno/worker scale-out.
4. **RC4 (+ RC3, + the future forecast_resolution path) into `audits/DEFERRED_ITEMS.md`**
   (7 seats): register r1 itself ordered the RC4 entry and it was never added —
   `/monitor/deferred-triggers` cannot walk a shelf that isn't written down (§16a's own lesson).
   Five minutes.
5. **Sealer midnight grace** (2 seats): never seal day D until minutes past D+1 00:00 UTC — a
   straggler write to a just-sealed day would produce a PERMANENT false tamper alarm, the one
   failure that damages the evidentiary claim itself.

**P1 — before the re-arm gate is acted on / before 2026-09-07:**
6. **U1 "fires forever" contradiction** (Forecaster): `report_a2` claims a divergence fires
   forever but the gate scans only a 21-day window — bad rows age out by calendar. Unwindow the
   gate's bad-row scan (or register the window as a declared rule and amend the docstring).
7. **U1 finalized-verdict overwrite protection** (Guardian, Executioner): within A2.2 the daily
   upsert can silently flip a FAIL to PASS on a comparator revision — log verdict transitions or
   refuse unlogged FAIL→PASS.
8. **U1 re-arm bias term filters src** (Executioner): the bias run currently includes FMP rows,
   contradicting "FMP rows never count" — latent gate blocker.
9. **US holiday calendar in the trading-day math** (4 seats, dated): Labor Day 2026-09-07 lands
   inside the re-arm accrual window; `_prev_bday` can label T on a closed session. Fix or
   explicitly accept before then. (Also: the tzdata-less `_ET = UTC−4` fallback is wrong half the
   year — dev-box footgun.)
10. **Standing basis monitor** (Economist, Challenger, Statistician): make the stamp+value
    identity check (Δas-of vs published flow) a periodic per-FUND monitor that ALARMS on basis
    drift (the only regime-independent detector — the Challenger proved the re-arm gate has no
    discriminating power in trending-flow regimes); Statistician's bar: ≥10 trading days per fund
    before `re_arm.ready` is acted on; promote Bitwise off the capture-instant fallback via the
    same test.

**P2 — register hygiene (append-only entries, before any horizon nears):**
11. **Stamp the scoring `param_version` into each daily index payload** (Economist's strongest
    finding, Statistician concurring): the rules are frozen but the instrument beneath them is a
    living calibrated model — an unrecorded recalibration is a silent splice into the sealed
    series. Payload-field addition, register-annotated, forward-only.
12. **Full-precision constituent detections in the sealed payload** (Forecaster): R8 claims the
    value reproduces from its own record, but 1dp-rounded constituents can recompute 75.44
    against a sealed 75.45 — impeaching the reproducibility claim on a rounding choice. Fix
    forward + register erratum entry.
13. **F1–F4 point-probability convention** (Challenger, Economist, Statistician): bands are not
    Brier-scorable and the register promises Brier — append point estimates (or the midpoint
    convention) NOW while every horizon is distant; add F1–F3 resolution criteria to the F5
    standard; split F4's compound (Stage-4 vs acquisition) into separately scorable entries;
    PIT-seal F1–F4 so the dual anchor is uniform.
14. **Close the F5 anchor loop in both directions** (Forecaster, Guardian, Economist,
    Executioner): record `text_sha256` + the exact extraction byte-boundaries in the register
    (row_sha256 alone is not offline-recomputable); run and record the one-time recompute; make
    it standing practice per seal. Add the Statistician's census rule: any `kind='forecast'` PIT
    row not reflected in the register within 7 days is void (anti-file-drawer).
15. **Statistician's freeze attestation**: append one sentence to register r1 — whether any
    rejected variant was computed on stored data before the freeze (and if so, which, with
    results). The difference between a clean freeze and an unfalsifiable one.

**Watch items (dated):**
- **By 2026-08-21 EOD** (Operator's tripwire): ≥1 issuer-source interval scored under
  `mode='asof'` — zero after ~3 snapshot cycles is a DEFECT (page_asof persistence), not cold
  start, and is indistinguishable from patience unless checked.
- **~2026-08-19 00:xx UTC**: first PIT day-seal lands; `/diag/pit?verify=7` ok:true; by_kind
  covers trend/market/crypto/index after the first scoring cycle.
- **First 60 days** (Economist/Statistician): index ceiling-compression + ΔLevel-vs-universe_count
  dependence; never read day-over-day differences as returns; smooth level + volatile universe =
  saturation tell.
- **Documentation notes**: PIT_STORE flag gates only the sealer (Executioner); event_date ≈
  write-day for market/crypto kinds — bitemporality doesn't yet separate in current data, so
  external language says "append-only, knowable_at-stamped" not "bitemporal" until the axes
  genuinely diverge (Statistician); ~24h unsealed window before the daily fold (Forecaster) —
  state it in DDQ language rather than letting a buyer find it.

## DISAGREEMENTS (minimal this convening — signal in itself)

1. **What the index level means**: the Economist ("approved as an unmarketed record-accruer; NOT
   yet, as constructed, a publishable index level" — the level confounds attention with universe
   size and calibration regime) and Statistician ("'gauge of attention intensity' is a name, not
   an established property") vs the other seats' acceptance of the register's own framing. No
   seat proposes changing r1; the dispute is what may ever be SAID about the series — resolved in
   practice by the unmarketed status plus conditions 11 and the 60-day decomposition test.
2. **U1 confidence**: the Operator alone withholds "proven" ("deployed, unproven — the fix's
   actual purpose has produced zero rows"), demanding the dated 08-21 check where others accept
   cold-start as expected. Composes with, rather than contradicts, the watch item.
3. **Sealing-endpoint generality**: Guardian/Statistician want guardrails on
   `/diag/pit/forecast` (junk sealed is junk forever; census rule); Expansionist/Executioner
   accept it at one-founder cadence. Chairman's call on timing, not substance.

## WHAT THE BOARD AFFIRMED (for the record)

- **Faithful execution, 4/4**: each update does what its ruling ordered — verified in code, not
  taken from the material. The A2/A1.5 record is physically unrewritable (PK includes
  rule_version); knowable_at cannot be caller-supplied; the freeze preceded the first value
  (git-proven); F5's register text matches what the Forecaster seat authored (drift-checked).
- **Held-out walls hold**: nothing reads the PIT store, the index, or the reconcile log into
  scoring; the three accuracy ledgers are byte-untouched by today's commits.
- **The through-line** (multiple seats independently): everywhere the system lacks data it says
  so — NO_DERIVED, ABSENT, missing_asof, covered-not-scored, cold-start zeros — instead of
  manufacturing a number. The conditions above are about making the integrity claims as strong
  against a privileged insider and against silent loss as they already are against bugs.

---

**Chairman — your decisions:** (1) order the P0 batch (external anchoring + backup schedule,
completeness monitor, unique index, DEFERRED_ITEMS entries, midnight grace) — the board is
unanimous and the anchoring clock is running; (2) order the P1 reconcile fixes before the re-arm
gate is trusted (fires-forever, verdict-transition log, bias src filter, holiday calendar by
09-07, standing basis monitor); (3) rule on the P2 register entries (param_version stamp,
payload precision, F1–F4 point convention, F5 text-hash annotation, freeze attestation);
(4) note the dated tripwire — if no issuer interval has scored under mode='asof' by 08-21 EOD,
it is a defect investigation, not patience.
