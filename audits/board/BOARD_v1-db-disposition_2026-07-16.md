# BOARD REVIEW — 1.0 Database Disposition (integrity of data + scoring analysis)
**Date:** 2026-07-16 · **Convened by:** founder (Chairman) · **Trigger:** disposition of the
frozen 1.0 Postgres (essential-2, $20/mo, 10.8 GB, preserved since 2026-07-02) — transfer vs
archive+delete, judged for integrity of data and scoring analysis.

Six independent archetype memos, identical evidence pack
(scratchpad board_pack_v1db.md = audits/infra/V1_DB_ASSESSMENT_2026-07-16.md + neutral
option space A–E + live context facts), no cross-contamination. Full memo bodies embedded
verbatim below (fixing the extraction gap of the 2026-07-15 board file).

## DECISION TABLE

| Option | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist |
|---|---|---|---|---|---|---|
| **A — archive (verified dump) + delete** | AWC | AWC | AWC | AWC | **SHIP** | AWC |
| B — archive + keep paying | AWC (dominated by A) | APPROVE (dominated; needs review date) | REJECT | REJECT (≤30-day bridge only) | CUT | REJECT |
| C — selective transfer into v2 | REJECT | REJECT | REJECT | REJECT | CUT | REJECT |
| D — full transfer into v2 | REJECT | REJECT | REJECT | REJECT | CUT | REJECT |
| E — status quo | REJECT | REJECT | REJECT | REJECT | CUT | REJECT |

**Unanimous:** A approved (with conditions) · C, D, E rejected outright.
**Split:** only B's framing (two members tolerate it as a dominated holding pattern; four reject).

## MID-REVIEW EMPIRICAL FINDING (Challenger + Outsider attack CONFIRMED by reconciliation)

Both adversarial memos attacked the assessment's "v2 already has everything durable" claim.
The reconciliation queries (run during the session, read-only, both DBs) proved them right:
- 1.0 holds **934,203** pre-split velocity rows; v2 retains **265,863 (~28%)**; PK lineage
  sample: only **282/1000** pre-split 1.0 ids exist verbatim in v2.
- The "one second apart" MIN offset was divergence, not identity.
- 1.0's row explosion began 06-13 (330k/day → ~500k/day) — most pre-split bulk is the
  48-hours-before-split junk explosion; most probable (unverified) cause of v2's smaller
  retained set is the 06-15→06-24 junk/fragment purge era, before the never-delete rule
  hardened on 06-24.
- CONSEQUENCE: the 1.0 DB is the ONLY complete original of the pre-split record → the
  verified-archive-before-delete conditions are LOAD-BEARING, not ceremony. The assessment
  doc was corrected in place (audits/infra/V1_DB_ASSESSMENT_2026-07-16.md ⚠ CORRECTION).

## CONVERGENT CONDITIONS ON A (reached independently by ≥4 memos)
1. **Verified test-restore BEFORE any deletion** — capture → download → SHA-256 → restore
   to a scratch DB → row counts must match a pre-capture manifest exactly (all six).
2. **Two copies, two failure domains, both checksummed** — a single OneDrive-adjacent copy
   is not custody (five memos).
3. **Reconcile the pre-split row-count discrepancy in writing first** (Challenger,
   Outsider) — ✅ done mid-review; counts documented, cause honestly marked inferential.
4. **Epoch-stamp the 06-15 engine boundary inside v2** (metadata-only): v2's pre-split
   rows + the 06-02→06-15 ledger/pending cohort were 1.0-engine-scored and sit in the live
   365-day window until mid-2027 — never publish blended rates spanning the boundary
   unsegmented (Challenger, Economist).
5. **Archive manifest + frozen provenance README + signed disposition record in the repo**
   (Expansionist, Outsider, Economist, Guardian).
6. **Standing ban on importing dump rows into v2** — any forensic use or two-engine A/B
   runs on a SCRATCH restore, never by import (Guardian, Challenger, Outsider, Economist).
7. **Founder personally executes the destroy** (flag-never-force) (Guardian, Executioner).
8. **Generalize into a datastore-retirement runbook** — the enterprise-DDQ asset
   (Expansionist).
9. **Non-destructive steps run NOW regardless of the final ruling** — zero backups
   currently exist; status quo is one incident from unrecoverable loss (Executioner,
   Guardian's E-rejection).

## KEY DISAGREEMENTS (signal, not noise)
1. **The two-engine natural experiment.** Challenger: calling the 06-15→07-02 overlap
   "zero analytical gain" is overreach — it is the only two-engine A/B dataset in
   existence. Economist: legitimate but low-power (17 days); pre-register the question if
   ever run. Guardian: importation is the gravest threat in the option space. ALL agree:
   if ever run, via scratch restore only.
2. **Option B.** Guardian/Challenger tolerate it as strictly dominated; Expansionist/
   Outsider/Executioner/Economist reject it (zombie-store precedent, epoch-mixing
   invitation, $240/yr for a story).
3. **How bad the assessment's error was.** Outsider: a number that "smells managed" and
   would fail DD verbatim. Guardian: the correction process itself is the integrity
   system working.

## ARCHETYPE MEMOS (verbatim)

---

# CHALLENGER MEMO — 1.0 Database Disposition (Board Review 2026-07-16)

**Role:** Attack the material on accuracy grounds only. I do not care about the $20/mo.
**Sources examined:** the evidence pack (`board_pack_v1db.md`) AND the two inspection
scripts that generated its numbers (`inspect_v1_db.py`, `inspect_v2_db.py`). The scripts
matter: they show exactly what was — and was not — measured.

---

## ATTACK 1 — "v2 already has everything durable" is FALSIFIED BY THE PACK'S OWN NUMBERS

The claim rests on two measurements (per `inspect_v2_db.py`): a single MIN(scored_at)
comparison (1.0 `…:03:01` vs v2 `…:03:02`) and one count (`265,863` v2 rows before
2026-06-15). Neither supports the sentence "Everything durable that 1.0 ever produced up
to the split lives in v2 today." Three independent problems:

### 1a. The pre-split row count contradicts the claim — and nobody ran the control query.
1.0 holds 9,718,671 velocity rows over 06-04→07-02 (~28 days, ~347k/day average). The
pre-split window (06-04→06-15) at anything near that rate is **millions of rows**. v2
retains **265,863** — well under 10% of the plausible inherited set. So at least one of
the following is true, and the assessment establishes none of them:
- v2 deleted the bulk of the inherited pre-split rows after the copy (fragment-gate
  prunes are permitted under §13, but §13 also hard-forbids quality-judgement deletes of
  `velocity_scores` within 365 days — which bucket were these in? No log, no accounting);
- the 1.0 engine's write rate ramped so steeply that almost all 9.7M rows are post-06-15
  (possible, unmeasured);
- the pg:copy story is inaccurate in some respect.

The decisive control is ONE line — `SELECT COUNT(*) FROM velocity_scores WHERE
scored_at < '2026-06-15'` **run on the 1.0 DB** — and it was never run. The v2 side of
the comparison was counted; the 1.0 side was not. An auditor will notice that asymmetry
immediately. Until that number exists and reconciles against 265,863 (with any delta
attributed row-class by row-class to the §13 fragment allowance), the headline claim is
an assertion, not a finding.

### 1b. The one-second offset is evidence of DIVERGENCE, spun as evidence of identity.
A faithful `pg:copy` yields an identical MIN. `…:01` vs `…:02` means v2's earliest
surviving row is a *different row* than 1.0's earliest — i.e., v2's copy of the first
row(s) is gone (consistent with 1a's prunes) or the sets never matched. The pack presents
"one second after" as confirmation of "the same inherited row set." That is the single
weakest sentence in the document and the first thing opposing counsel would read aloud.
A MIN() on one column proves overlap at one endpoint; it proves nothing about set
equality across 265k (let alone millions of) rows. No per-day histogram, no checksum, no
row-level spot-check of even ten rows was performed.

### 1c. "Retained" rows are not "preserved" rows — v2 mutates in place.
Project memory is explicit: after any calibration change, `velocity_scores.serve_payload`
is REGENERATED (serve-payload cache gotcha), and v2's calibration changed repeatedly
post-split (dual-pathway, INV-1, date canon). So v2's inherited pre-split rows are, in
part, **rewritten** — they no longer carry the as-scored-at-the-time values. The 1.0 DB
is the only remaining as-scored original for 06-04→06-15. "v2 has the rows" and "v2 has
the evidence" are different claims; the pack conflates them.

### 1d. Coverage gaps in the side-by-side.
1.0 has 28 tables; the side-by-side compares 5. `anomaly_log` (1.1M rows), `risk_scores`
(26k), `market_signal_history` (139k), registry/lifecycle/queries/author (~330k) were
sized but never compared to v2 — even their date ranges are "—" in the pack's own table.
And `pending_detections`: 1.0 = 1,841 (from 06-02), v2 = 1,684 (from 06-02). v2 is short
≥157 rows against a table whose start dates are identical, with no decomposition of the
gap by split date. "Everything durable" was concluded without inspecting most of the
inventory.

---

## ATTACK 2 — "Importing the tail pollutes the ledger": HALF TRUE, and internally INCONSISTENT

The pollution argument holds only for an **unstamped merge into live tables**. Within
NowTrendIn's own rules it collapses for the stamped variant the pack itself lists under
Option C and then never engages:

1. **v2 already tolerates mixed-era enrollments by segmentation, not deletion.** The
   ledger's own history contains v2's leaderboard-era enrollments; the 2026-07-07 fix was
   report-time splitting (pre-broken / tracked-race), not purging. `param_version`
   stamping exists precisely for this. If report-time segmentation makes v2's own retired
   enrollment logic honest, the identical mechanism handles 1.0-era rows. You cannot argue
   "pollution" for the tail while shipping segmentation for the head.
2. **Worse — the pollution is already in v2's published numbers.** v2's ledger/pending
   rows dated 06-02→06-15 were created by the **1.0 engine** and inherited at the copy.
   The published honest hit-rate already blends predecessor-engine detections, unstamped.
   The assessment's logic, applied consistently, indicts v2's current headline figure. The
   fix is engine-epoch provenance stamps on pre-06-15 ledger/pending rows — a condition I
   attach to every verdict below.
3. **"Zero analytical gain" is overreach.** The 06-15→07-02 parallel tail is the only
   natural experiment in existence where two engine generations scored the same weeks on
   the same sources. That is a legitimate held-out A/B baseline (did v2's calibration
   actually beat 1.0 on the overlap?). The correct home for that analysis is a **scratch
   restore of the archive**, not the live DB — but "nothing left worth selecting" is
   false as an analytical statement, and publishing it invites a competent critic to ask
   why the only inter-engine comparison dataset was characterized as worthless.

So: the pollution claim is *convenient* in its strong form. Its defensible core is
narrower: "do not merge unstamped rows into live serving tables" — which nobody proposed.

---

## ATTACK 3 — Can deleting the 1.0 DB leave a published v2 figure undefendable? YES, in three ways (all curable before deletion)

1. **Provenance of inherited rows.** Every published figure resting on pre-split data —
   ledger entries dated 06-05→06-13, pendings from 06-02, any baseline or history chart
   reaching back to 06-04 — traces to the pg:copy. Because v2 mutates serve_payload
   (1c) and has apparently shed most inherited rows (1a), the only independent witness
   that v2's inherited rows were not altered-with-effect is the 1.0 original. Delete it
   without a verified archive and the answer to "produce the original source of these
   rows" becomes "we destroyed it." A *verified* dump answers this — an *unverified*
   dump does not.
2. **The unexplained discrepancies die with the DB.** The :01/:02 offset and the
   265,863-vs-millions gap are currently answerable only by querying 1.0. Delete first,
   and any future auditor question about them is permanently unanswerable — the worst
   posture for a company whose thesis is "a number we can't defend is worse than no
   number."
3. **Chain of custody of the archive itself.** The pack's archive plan is "capture, then
   download locally." A single logical dump on a founder laptop under OneDrive, with no
   published checksum, no test restore, and no second location is not an audit-grade
   archive; it is a hope. `pg:backups` logical dumps also occasionally fail silently on
   large tables — "restorable to a scratch DB at any time" is asserted in the pack, never
   demonstrated. Restore-verify BEFORE delete, or the archive is theater.

Additional small findings:
- **"6 rows — ALL LAGGED — nothing":** n=6 supports no conclusion in either direction.
  Fine as a reason not to import; never cite it (or "90 resolved vs 6") as evidence v2
  outperforms 1.0 — different enrollment logic, different runtimes, classic denominator
  game.
- **Freeze-doc correction:** "any earlier prototype data lived elsewhere and is not
  here" is an inference from add-on creation date (06-01) + earliest row (06-04). It is a
  reasonable inference; label it as one.
- **Quotability:** the sentence "the transfer already happened" must not appear in any
  external or investor-facing material until Attack 1's reconciliation exists. As written
  it is falsifiable from the pack's own table.

---

## VERDICTS

### A. Archive + delete — **APPROVE-WITH-CONDITIONS**
Right destination, wrong sequencing as written. Conditions (all BEFORE deletion):
1. **Reconciliation report:** run the pre-06-15 per-table counts on the 1.0 DB
   (velocity_scores, pending_detections, accuracy_ledger, pull_history, anomaly_log,
   risk_scores, market_signal_history), compare to v2's retained counts, and explain the
   velocity gap and the :01/:02 offset in writing, attributing any v2 deletions to the
   §13 fragment allowance explicitly.
2. **Verified restore:** restore the dump to a scratch Postgres, match per-table row
   counts to the capture, THEN delete.
3. **Audit-grade custody:** SHA-256 of the dump recorded in the repo; two independent
   storage locations (OneDrive alone is a single point of failure).
4. **Epoch stamping in v2:** stamp pre-06-15 ledger/pending rows with engine-epoch
   provenance so published rates are segmentable (fixes Attack 2.2 regardless of
   disposition).
*Strongest attack:* delete-before-reconcile permanently destroys the only witness to two
open discrepancies. *What changes my mind to plain APPROVE:* the four conditions done.

### B. Archive + keep — **APPROVE-WITH-CONDITIONS**
Accuracy-safest posture, but inert: hot access has answered zero of the open questions in
six weeks and Heroku gives no immortality guarantee to an add-on — the dump must be
captured and verified anyway. Same conditions 1–4. *Strongest attack:* B becomes a
standing excuse never to do the reconciliation. *What changes my mind:* nothing — B is
acceptable but strictly dominated by a conditioned A once the archive is verified.

### C. Selective transfer — **REJECT**
Unstamped: breaks reproducibility (Principle 2) — indefensible. Stamped: not polluting
(see Attack 2), but still wrong, because importing frozen evidence into a live DB that
regenerates serve_payload and prunes each cycle **destroys its evidentiary value** — the
one thing the tail is good for (the parallel-engine A/B) is served better by a scratch
restore of the archive. *Strongest attack:* you would be converting the only immutable
record of the overlap window into mutable rows. *What changes my mind:* a concrete,
recurring analysis requiring hot joins against live v2 tables that a scratch restore
demonstrably cannot serve — none has been named.

### D. Full transfer — **REJECT**
Physically impossible today (10.8 GB into ~6.75 GB free), and the accuracy case is worse
than C at scale: 9.7M rows of a different calibration epoch inside the serving DB, all
subject to v2's live mutation and pruning. Maximum epoch-mixing, zero gain. *What changes
my mind:* nothing while v2 mutates rows in place.

### E. Status quo — **REJECT**
The only option with zero accuracy upside. No dump exists; a single Heroku add-on
incident deletes the original evidence with no archive; the discrepancies stay
undocumented; $20/mo buys availability, not preservation. "Decide nothing" is itself a
decision to leave two falsifiable claims and one unarchived original in play. *What
changes my mind:* nothing — E is inferior to B on every accuracy axis.

---

## BOTTOM LINE
The recommendation (archive, then delete) is directionally right; the EVIDENCE offered
for it is not yet audit-grade. Do not let the disposition proceed on the strength of a
one-row MIN() comparison and an uncontrolled row count. Reconcile → verify-restore →
checksum+dual-store → stamp → then delete.

— The Challenger

---

# FIRST-PRINCIPLES GUARDIAN — MEMO ON 1.0 DATABASE DISPOSITION
**Board review 2026-07-16 · Evidence pack: board_pack_v1db.md · Written in isolation**

---

## 0. The single test I applied

The product's one irreducible claim: **it measures where human attention is moving BEFORE it
arrives, and proves it with a falsifiable, held-out, never-deleted accuracy ledger.** The moat is
the time-stamped detection history. Every option below is judged against that claim only: does it
strengthen or dilute the moat, and does it keep measurement honest and the ledger untouchable?

---

## 1. The three questions the Chairman asked me directly

### 1.1 Does deleting the 1.0 database violate the spirit of "history is never deleted"?

**No — provided the archive conditions in §3 are met.** But the reasoning matters more than the
answer, because this is exactly where principle-drift starts.

"History is never deleted" is not a rule about bytes; it is a rule about **falsifiability**. Its
purpose (§13/§14 of CLAUDE.md, the 365-day retention, the held-out ledger) is that NowTrendIn can
never be accused of curating its own track record — every detection we ever time-stamped remains
available to be judged a hit or a miss. The rule therefore protects:

1. The **live system's accuracy ledger** — every row, forever within policy.
2. The **live system's scored history** (velocity_scores, 365 days) — the raw material for
   calibration and ledger validation.

Apply that to the 1.0 add-on, using the pack's verified facts:

- Everything 1.0 produced **up to the 2026-06-15 split is already inside v2** (pg:copy; v2's
  earliest velocity row is one second after 1.0's; 265,863 pre-split rows retained under v2's own
  365-day rule). The 1.0 add-on is a **redundant copy** of that history, not the history itself.
- 1.0's accuracy_ledger holds **6 rows, all dated 06-05 → 06-13 — before the split** — so they too
  were inherited into v2 by the pg:copy. Nothing in the moat lives only in 1.0. (Condition: this
  must be *spot-verified in v2*, not assumed — see §3.)
- The only unique content is the **06-15 → 07-02 parallel tail** written by a retired engine
  epoch. That tail is not part of v2's detection history; it is the exhaust of a frozen system
  that made no claims we are still defending. Preserving it as a verified offline dump satisfies
  the spirit fully.

**The drift I am guarding against, in both directions:**
- Drift A — *"never delete history" hardens into "no database may ever be deprovisioned."* That
  turns an integrity principle into indiscriminate hoarding, and worse, it dilutes the principle:
  if everything is sacred, the ledger is no longer specially sacred. The rule's power comes from
  its precision.
- Drift B — *the $20/mo saving (Cost Sentinel at $531.90/$700) becomes the real reason and
  integrity the retrofit.* The decision must stand on integrity grounds alone. Here it does: the
  delete is permissible because the history is duplicated and archived, not because it is cheap.
  If the archive conditions cannot be met, the $20/mo continues — the budget never outranks the
  moat.

Note also: even the 6 all-LAGGED ledger rows are protected history. A losing record is still the
record — deleting *those* (from v2 or from the archive) would be genuine curation of the track
record and is forbidden. Nothing in Option A touches them.

### 1.2 Is a downloadable dump sufficient preservation of provenance for the rows v2 inherited?

**Yes for the inherited rows — because the dump is not their primary provenance; v2 is.** The
inherited rows live on inside v2 under v2's own retention rules, time-stamped and queryable. The
dump's role is narrower and different: it is the **forensic witness** — an independent artifact
proving what the 1.0 database contained at freeze, so that if anyone ever challenges the
continuity claim ("v2 inherited 1.0's record intact, one second offset"), we can restore the dump
to a scratch DB and demonstrate it row-by-row. Reproducibility of the *claim of continuity*, not
of the scores.

But a dump is only sufficient if it actually functions as evidence. An unverified single-copy
file on one Windows laptop is a hope, not an archive. Sufficiency requires (all folded into §3):
**(a)** the download completes and a **test-restore to a scratch Postgres succeeds** before
deletion (Heroku-side backups vanish with the add-on — there is no second chance); **(b)** a
recorded **checksum + row-count manifest** for at least velocity_scores, pending_detections, and
accuracy_ledger; **(c)** **two copies in two places**; **(d)** a short provenance note stored with
the dump — including the pack's own correction that the "pre-April-2026 data" freeze-doc lore is
wrong (the DB contains nothing before 2026-06-04). An archive whose accompanying documentation
misdescribes it is itself an integrity hazard; fix the record now, while the facts are verifiable.

### 1.3 Would importing rows scored by a different engine epoch corrupt reproducibility?

**Yes — categorically, and this is the sharpest edge in the whole pack.** Two distinct
corruptions, one per import class:

- **Velocity rows (epoch mixing).** v2's calibration moved substantially after the split
  (dual-pathway changes, INV-1 serve-stored, date canon). A 1.0-scored row for the same
  topic-week as a v2-scored row is not a second observation — it is a number the current engine
  **cannot reproduce and cannot defend**. "A number we can't defend is worse than no number" is
  the first foundational principle; importing 9.7M of them (or any subset) manufactures exactly
  that. Epoch/provenance stamping mitigates but does not cure: once inside the same table, the
  rows are one query-writer's mistake away from entering a baseline, a trajectory, or a
  calibration read. The safe quarantine for a foreign epoch is a **separate database** — which is
  precisely what the dump-restorable-to-scratch-DB already provides, for free.
- **1.0's pending_detections (ledger contamination — the worst one).** These were enrolled by the
  leaderboard-era logic v2 retired on 2026-07-07 *specifically because it was structurally
  LAGGED*. Importing them into the held-out ledger pipeline injects another engine's detections
  into our honest denominators — the one table whose purity IS the moat. This is not a
  reproducibility nuance; it is direct tampering with the falsifiable record, indistinguishable
  from the outside from denominator management. No stamping scheme makes it acceptable.

---

## 2. Per-option verdicts

### Option A — Archive + delete → **APPROVE-WITH-CONDITIONS**
- **Principle at stake:** history-never-deleted (spirit), reproducibility of the continuity claim.
- Strengthens the moat's *defensibility* at zero cost to its content: the live record stays in
  v2 untouched, the frozen record gains a verifiable offline witness, and $20/mo of Cost Sentinel
  headroom returns. Conditions are the archive-integrity gate in §3 — every one is
  condition-precedent to the delete, none is optional.
- **Drift watch:** do not let the cost saving be cited as a justification anywhere the decision
  is recorded; record it as integrity-cleared first, cost-beneficial second.

### Option B — Archive + keep → **APPROVE (permissible but dominated)**
- **Principle at stake:** none violated. Keeping a redundant hot copy breaks no rule.
- But be honest about what the $20/mo buys: *queryability of a record whose canonical copy is
  already queryable in v2*, plus a tail nobody should ever query into scoring. It adds zero
  accuracy and zero falsifiability. If chosen, it must be a deliberate holding pattern with a
  review date — otherwise it decays into Option E wearing a decision's clothes.

### Option C — Selective transfer → **REJECT**
- **Principle at stake:** no-circular/no-contaminated metrics; ledger held-out and untouchable;
  reproducibility.
- The pending_detections import is a direct write into the moat by a retired enrollment logic —
  the closest thing to ledger tampering in the entire option space. The velocity-tail import
  mixes engine epochs for, by the pack's own inventory, **zero analytical gain** (v2 scored the
  same weeks itself). "With provenance stamping" does not rescue it — quarantine by table flag is
  weaker than quarantine by database, and the scratch-restorable dump already provides the latter.
- **Hidden drift:** "more data is more moat." False. The moat is the *purity* of the time-stamped
  record, not its row count. C trades purity for bulk.

### Option D — Full transfer → **REJECT**
- Everything wrong with C, at 10.8 GB scale, plus it physically cannot fit and would force a
  Postgres tier upgrade — spending real money to *inject* an epoch-incompatible record into the
  live system. This inverts every priority the platform has. The standing tier-upgrade item exists
  to hold v2's own 365-day tail, not a foreign engine's exhaust.

### Option E — Status quo (decide nothing) → **REJECT**
- **Principle at stake:** history-never-deleted — violated *by inaction*, which is the
  counter-intuitive finding. Today the frozen June record exists in exactly one place, behind one
  Heroku add-on, with **no downloaded dump**. Heroku-side backups vanish with the add-on; an
  accidental deprovision, billing lapse, or platform incident erases the forensic witness with no
  recourse. "Preserve everything" without an archive is not preservation — it is unmanaged risk
  billed monthly.
- Minimum irreducible action regardless of the keep/delete ruling: **capture + download + verify
  the dump now.** That step is common to A and B and should not wait for the disposition decision.

---

## 3. Conditions (Option A gate — all condition-precedent, flag-never-force)

1. `heroku pg:backups:capture -a nowtrendin` → download via `pg:backups:url`. **No delete until
   the local file exists.**
2. **Test-restore** the dump to a scratch Postgres and verify row counts match the live
   inspection (velocity_scores ≈ 9,718,671; pending_detections 1,841; accuracy_ledger 6).
3. Record a **checksum + manifest** (file hash, table row counts, date ranges) alongside the dump.
4. **Two copies, two locations** (e.g., local disk + one offsite/cloud copy).
5. **Spot-verify in v2** before deletion: the 6 accuracy_ledger rows (06-05→06-13) and the
   pre-split velocity boundary rows are present in v2 — confirm the inheritance claim empirically,
   don't inherit it from the pack.
6. **Correct the freeze-doc lore** (ENGINE_AND_REPO_FREEZE.md "pre-April-2026" phrasing) and file
   the provenance note with the dump.
7. **Founder rules the delete explicitly** after 1–6 are green (flag-never-force). The add-on
   deletion is the founder's click, not an agent's.
8. Standing prohibition, independent of disposition: **no row from the dump is ever imported into
   v2's scoring tables or ledger pipeline.** Restore-to-scratch for forensics is the only
   sanctioned use.

## 4. One-line synthesis

The moat is v2's untouched, time-stamped record — it is not in the 1.0 add-on, and the gravest
threat in this pack is not deletion but **importation** (C/D). Archive verifiably, then delete
(A); and note that doing nothing (E) is the only option that currently leaves the frozen record
one accident away from true, spirit-violating loss.

— First-Principles Guardian

---

# BOARD MEMO — The Expansionist
**Re:** Disposition of the frozen 1.0 Postgres (essential-2, $20/mo, 10.8 GB)
**Date:** 2026-07-16
**Lens:** Pure scale. Enterprise clients on every continent within three years. Every decision today is a precedent that gets photocopied at 100×.

---

## The framing that matters at scale

This is not a $20/mo decision. It is the FIRST retired-data-store decision this company has ever made, and at institutional scale it will not be the last — a global data platform accumulates retired stores the way it accumulates deprecated engines: dozens of them, one per major calibration epoch, per region, per acquired dataset, per regulatory jurisdiction. Enterprise due-diligence questionnaires (DDQs) from hedge funds, banks, and their counsel ask *exactly* this question, verbatim: **"Describe your data-lifecycle policy for decommissioned data stores. Provide evidence of the archival procedure and restoration test."** Today we get to write the answer as a runbook instead of an apology.

Three scale tests I applied to each option:

1. **Precedent test** — does this disposition generalize into a written data-lifecycle policy an enterprise diligence team can read and check off?
2. **Drag test** — at 100× (dozens of retired stores), does this disposition compound into operational drag: standing cost, standing attack/audit surface, standing "what is this?" questions in every SOC-2 / vendor-security review?
3. **Legibility test** — does it make the product MORE sellable: one canonical live database, one held-out ledger, one archive shelf with an index, nothing ambiguous?

The evidence pack makes the analytical question easy: v2 was pg:copied FROM 1.0 at the split, the 265,863 pre-split rows are already inside v2 under the 365-day retention rule, and the only unique 1.0 content is a parallel-run tail produced by a retired engine under retired enrollment logic. Nothing in 1.0 is load-bearing. So the entire decision IS the precedent.

---

## Option-by-option

### A. Archive + delete — **APPROVE-WITH-CONDITIONS**

This is the correct institutional pattern and the one every serious data company converges on: **snapshot → verify → index → retire**. It answers the DDQ question with a document instead of a shrug, it removes a dead store from the standing cost and audit surface, and — critically — it respects the foundational rules exactly as written: the 365-day retention and never-delete-ledger rules govern the LIVE v2 store; an offline, restorable logical dump of a frozen parallel-epoch database is archival, not deletion of history. The June record survives, forensically restorable, forever.

**Conditions (all four, non-negotiable, and this is also where I flag the hard-coded manual steps):**

1. **Restore-verify before delete.** A dump you never restored is a hope, not an archive. Restore to a scratch Postgres, run row-count + date-range checks against the evidence-pack inventory (9,718,671 velocity rows, 06-04→07-02, 28 tables), record the output. Enterprise diligence teams ask for restoration-test evidence by name.
2. **Checksums + redundancy.** SHA-256 the dump; store it in at least two locations, and at least one NOT on the founder's laptop/OneDrive alone. A single local copy of the company's only archived epoch is a bus-factor artifact, not an institutional archive.
3. **Archive manifest.** One page, checked into the repo: what the store was, epoch dates, why retired, dump location(s), checksum, restore command, restore-test date + result, approving authority (founder), date. This page is the DDQ answer.
4. **Promote the runbook to policy.** Generalize the steps into `RUNBOOK_datastore-retirement.md` (or a §18 in CLAUDE.md): every future retired store follows snapshot → restore-verify → checksum → manifest → founder sign-off → delete. That converts a one-off chore into a sellable control.

**Hard-coded manual steps flagged:** `pg:backups:capture` → `pg:backups:url` → *download by hand* is three manual steps with a silent failure mode the pack itself names — **Heroku-side backups vanish with the add-on**. If the download step is skipped or the file is lost and the add-on is deleted, the archive never existed. At 100× stores this manual chain WILL drop a store. The runbook must make download + checksum + restore-verify explicit, ordered, and evidenced (command transcript saved into the manifest) — and the eventual automation target is a scripted retire pipeline, not a human remembering `pg:backups:url`. Also note this repo's own environment memo: the Heroku CLI is broken on this Windows box (`C:\Program` bug) — the runbook should state where the capture/download is actually executed so the manual step doesn't silently fail here specifically.

**Biggest scale opportunity:** this is the founding artifact of the company's data-lifecycle policy — the difference between "we have dozens of mystery databases" and "we have a retirement runbook with manifests" in every future vendor-security review. That document sells.

### B. Archive + keep ($20/mo hot) — **REJECT**

The worst precedent in the pack. It establishes "we archive AND keep paying," which at 100× is dozens of zombie stores: linear standing cost, but worse, a compounding **audit surface** — every retired-but-live database is a line item in every SOC-2 scope, every pen-test scope, every DDQ ("who has access to this? why is it up? when was it last patched?"), forever. A frozen database nobody queries is pure liability with zero optionality that the offline dump doesn't already provide (the dump restores to a scratch DB "at any time" — that IS the hot-access story, on demand, at $0 standing). Cost Sentinel is at $531.90/$700; dead spend crowds out live sources. Keeping it hot also quietly signals internally that retirement decisions don't have to be finished — the exact cultural drag a scaling data company can't afford.

**Biggest scale blocker:** normalizes zombie infrastructure; at dozens of stores it's a permanent tax on cost, security scope, and diligence bandwidth.

### C. Selective transfer, then delete — **REJECT**

Even set aside that the pack shows nothing worth selecting, the PRECEDENT is the poison: it establishes that retired-epoch data may be merged into the live canonical store. At scale that is how a data company destroys its single most sellable property — **one engine, one calibration epoch, one reproducible history**. Cross-epoch velocity rows break reproducibility; importing leaderboard-era pending detections pollutes the held-out ledger's honest denominators (§14) — the moat itself. An enterprise diligence team that finds mixed-epoch rows in the accuracy ledger's substrate will discount the whole ledger, and the ledger is the product. Even "with provenance stamping" it fails: you'd be defending an asterisk in every client conversation for zero analytical gain. The archive dump (Option A) already preserves the tail for any future forensic backtest, held out where it belongs.

**Biggest scale blocker:** contaminates the accuracy ledger's honest denominators — the one asset that cannot be rebuilt and the one every enterprise client is actually buying.

### D. Full transfer — **REJECT**

Everything wrong with C, plus it physically cannot fit (10.8 GB into a 10 GB tier at 32.5% used), so it forces a paid tier upgrade to import 9.7M redundant-or-epoch-hazardous rows — spending money to make the canonical store LESS legible. It also sets the catastrophic precedent that the live database is the archive: at 100×, the production store becomes a landfill of every retired epoch, and every query, backup, restore-test, and diligence answer gets slower and murkier. Institutional data companies separate hot canonical from cold archive absolutely; this fuses them.

**Biggest scale blocker:** makes "what is in your production database?" — the first question in every enterprise diligence — unanswerable in one sentence.

### E. Status quo (decide nothing) — **REJECT**

Strictly worse than B: the same $20/mo zombie and the same audit surface, WITHOUT even a documented decision. At scale, "undecided" is the most expensive disposition of all — dozens of stores in limbo means nobody can answer the DDQ lifecycle question at all, which reads to diligence as "no data governance." Indecision is itself a precedent, and it's the one that kills enterprise deals: not the cost, the illegibility. The evidence pack is complete and verified; there is nothing left to wait for.

**Biggest scale blocker:** institutionalizes limbo — the one answer ("we haven't decided") that fails every due-diligence questionnaire outright.

---

## Bottom line

**A, with the four conditions — and condition 4 (the generalized retirement runbook) is where the enterprise value actually lives.** The $20/mo is noise; the precedent is the product. A global institutional data platform is sellable exactly to the degree that its data estate is legible: one live canonical DB, one held-out ledger, and an archive shelf with manifests. Option A builds that shelf; B and E rot it; C and D burn down the thing on it worth the most.

Within the foundational rules: nothing here touches scoring, the ledger stays held-out and untouched, retention rules govern the live store as written, and the final delete is flag-never-force — founder pulls the trigger only after the restore-verify evidence is in the manifest.

— The Expansionist

---

# BOARD MEMO — THE OUTSIDER (VC / former hedge-fund banker)
## Re: Disposition of the retired v1.0 Postgres database
**Date:** 2026-07-16 · **Reviewer status:** first exposure to this company today · **Basis:** evidence pack `board_pack_v1db.md` only

---

## 1. Framing — what this decision actually is

This is not a $20/mo cost question. This is a **chain-of-custody question** about the only
frozen, engine-untouched record of what the v1 system produced. The company's own stated
principles (accuracy above all, reproducibility, held-out ledger, no deletion of ledger
history) make legacy data disposition a *diligence artifact*, not an ops chore. If I were
running technical DD on this company for a term sheet, the way they handle this database
would tell me more about their integrity culture than any pitch slide. The good news: the
assessment is unusually honest for founder-commissioned work (it *corrects* its own
freeze-doc lore, it recommends the cheap option against the sunk-cost instinct). The bad
news: two of its load-bearing numbers do not survive first contact with a DD team.

---

## 2. What my DD team would demand on legacy data (the standard)

For any acquired/inherited dataset a competent technical DD checklist requires:

1. **Chain of custody for the inherited rows.** A written record of the pg:copy event:
   date, operator, source snapshot identity, row counts per table AT COPY TIME, and a
   post-copy reconciliation (source count = destination count, per table). The pack cites
   ENGINE_AND_REPO_FREEZE.md but shows no copy-time reconciliation. Timestamp adjacency
   is offered instead (see §3.1) — that is not custody, that is coincidence-as-evidence.
2. **Reproducibility of historical claims.** If any user-facing or investor-facing claim
   ever rested on pre-split scores (June 2026 detections, early accuracy numbers), the
   company must be able to re-derive it. Today that requires either the 1.0 DB or a
   verified archive. Note the pack's own correction: the freeze-doc said "pre-April-2026
   data" and the DB contains **nothing before 2026-06-04**. So documentation and data
   already disagree once. Where did the pre-June prototype data go, and does any historical
   claim rest on it? If yes, that claim is currently unreproducible.
3. **A written deletion record.** Every deletion of legacy data needs a memo: what was
   deleted, row counts, why, who approved, when, and where the archive lives. "Founder
   ruled it in a chat session" does not survive diligence. The 365-day retention rule is
   written down; the *disposal* side has no equivalent written instrument yet.
4. **A tested restore, not a theoretical one.** "Dump restorable to a scratch DB at any
   time" is an assertion. DD accepts a restore *log*: dump captured, SHA-256 recorded,
   restored to scratch, row counts reconciled against the live DB, spot-queries matched.
   Until that log exists, the archive is Schrödinger's backup.
5. **Two custody locations.** A single downloaded dump on a founder laptop (this
   environment syncs the desktop through OneDrive, a consumer sync folder) is one
   ransomware event or one sync conflict away from zero. Off-site copy + checksum, or it
   doesn't count.

---

## 3. Do the numbers make sense, or smell managed?

Mostly honest, with two exceptions I would put on the table in the first meeting.

### 3.1 "One second apart, therefore same inherited row set" — NOT ACCEPTED
v2's earliest velocity row is `2026-06-04T23:03:02` vs 1.0's `...:01`, and the assessment
treats this as confirmation that v2 is a copy of 1.0. No DD team accepts timestamp
adjacency as lineage proof. Two engines polling the same sources on the same cadence
produce adjacent timestamps *without* shared rows. Lineage is proven cheaply and properly:
sample 1,000 pre-split rows from 1.0 by primary key, fetch the same keys from v2, hash and
compare content. An afternoon of work, and it converts an anecdote into evidence. Until
then, "the transfer already happened" is an inference, not a finding.

### 3.2 The 265,863 pre-split rows — the number that doesn't reconcile
This is my biggest issue with the pack. 1.0 wrote ~9.7M velocity rows over 28 days
(06-04→07-02), i.e. roughly **340k rows/day**. The pre-split window (06-04→06-15) is ~11
days, so 1.0 produced on the order of **3.5–4M rows before the split** — all of which the
pg:copy should have handed to v2. Yet v2 retains **265,863** pre-split rows under a rule
that says velocity rows are *never deleted within 365 days*. That is ~7% survival. Either:
- (a) the copy was partial (custody problem),
- (b) v2's quality/fragment pruning deleted ~93% of the inherited rows (defensible on
  quality grounds, but then the claim "everything durable that 1.0 ever produced up to the
  split lives in v2 today" is doing its work through the word *durable*, and the deletions
  happened with **no written deletion record** — which is exactly what item §2.3 exists
  for; it also sits uneasily next to the company's own hard rule against quality-based
  deletion of scored rows), or
- (c) the numbers are measured differently (distinct topics vs raw rows, deduplication at
  copy time).
Any of these may be innocent. But an assessment that presents 265,863 as *support* for
"v2 already has everything" — when the naive expectation is 15× that — without addressing
the gap, would get flagged by a first-year associate. **The gap must be explained in
writing before the delete button exists.** This is the single condition I will not waive.

### 3.3 Numbers I find credible
- The "bulk, not history" characterization of 9.7M rows (30-min scoring, no pruning) is
  plausible and consistent with the stated 1.0 architecture.
- The refusal to import 1.0's pending detections into a held-out ledger with different
  enrollment logic is *correct* and shows the team understands denominator integrity.
  One optics note for the record: 1.0's ledger is 6 rows, ALL LAGGED. Declining to merge
  it is right on methodology — but the honest disclosure is to say so out loud: the v1
  epoch's measurable record was 0-for-6, it is archived, and it is never blended into v2's
  headline rate in either direction. Archive it as human-readable CSV alongside the dump.
- The physical-fit constraint (10.8 GB into a 10 GB tier at 32.5% used) is arithmetic; fine.
- Recommending the −$20/mo option against sunk cost is the honest direction of travel.

### 3.4 Small hygiene flags
- The pack is dated 2026-07-16; today is 2026-07-15. Sloppy, and in a document whose whole
  subject is date discipline (§14 canon), dates should be exact.
- "Read-only inspection, verified live" — by whom, with what queries? Attach the query log
  to the disposition record. Verification without a trail is testimony.

---

## 4. Where my diligence would dig

1. **Reconcile the 265k-vs-~3.8M pre-split gap** (see 3.2). Written explanation, signed.
2. **Row-level lineage sample** (see 3.1): 1,000-key hash comparison 1.0↔v2.
3. **Restore test with a log**: capture → SHA-256 → scratch restore → per-table count
   reconciliation → spot queries. File the log with the dump.
4. **Pre-June data provenance**: the freeze-doc referenced data that does not exist in
   this DB. Chase where it lived, whether anything cited it, and correct the doc in place.
5. **Deletion instrument**: a one-page written disposition record (what/why/when/who/
   where-archived) that a future acquirer's DD team can read in five minutes.
6. **Second archive location + encryption**: not the OneDrive desktop alone.

---

## 5. Verdicts on Options A–E

### A. Archive + delete — **APPROVE-WITH-CONDITIONS**
Right destination, wrong to execute today. Conditions precedent, all cheap:
(1) explain the 265,863-vs-expected pre-split row gap in writing; (2) run the 1,000-row
lineage hash sample; (3) tested restore with logged checksums and per-table counts;
(4) two storage locations for the dump; (5) export accuracy_ledger + pending_detections
as human-readable CSV alongside the binary dump; (6) file a signed disposition record.
Then delete and take the $20/mo. **Point-blank question:** *"If an acquirer's DD team
asks you in 2027 to reproduce a June-2026 detection claim, walk me through the exact
steps — which file, which checksum, which restore log?" If you can't answer in one
breath, you're not ready to delete.*

### B. Archive + keep — **REJECT** (acceptable only as a ≤30-day bridge while A's conditions clear)
Once a *verified* archive exists, the hot copy buys nothing and creates risk: a live,
queryable, wrong-epoch database is an invitation for some future analysis to quietly mix
calibration epochs. Cold storage is not just cheaper — it is *safer* for reproducibility.
**Point-blank question:** *"Name one query you would run against the hot 1.0 DB in the
next 12 months that a scratch-restore of the dump couldn't answer in an hour."*

### C. Selective transfer — **REJECT**
The 06-15→07-02 tail was written by a different engine under retired enrollment logic and
a different calibration epoch. Importing it — even provenance-stamped — puts foreign rows
adjacent to v2's held-out ledger and its honest denominators for zero analytical gain the
archive doesn't already provide. Epoch mixing is precisely how "no circular metrics" and
"reproducibility" die by a thousand cuts. If a future backtest wants that tail, restore
the dump to a scratch DB and run the analysis *there*, held-out, forever. **Point-blank
question:** *"What analysis do you believe requires these rows to live INSIDE v2 rather
than beside it in a scratch restore — and why isn't that analysis just epoch-mixing with
extra steps?"*

### D. Full transfer — **REJECT**
Physically impossible without a tier upgrade, and strategically backwards: you would pay
more money to inject 9.7M bulk rows from a retired engine into the production database
whose comparability you have hard rules to protect. This option exists on the sheet only
for completeness. **Point-blank question:** *"You have a written rule that mixing epochs
breaks reproducibility — under what theory would importing an entire retired epoch not be
the maximal violation of it?"*

### E. Status quo — **REJECT**
Indecision is the worst custody posture: paying monthly for data with no archive, no
restore test, no disposition record, and a freeze-doc already proven wrong once. Every
month of drift makes the eventual DD conversation worse. **Point-blank question:** *"If
Heroku loses the essential-2 add-on tomorrow, what exactly do you still have — and can
you show me the file?"*

---

## 6. Bottom line

The recommendation's direction (no transfer; archive; then delete) is the one I would
have written. But the assessment currently *asserts* custody ("the transfer already
happened") on a one-second timestamp coincidence, and its strongest exhibit — 265,863
retained pre-split rows — is, on the arithmetic the pack itself supplies, ~7% of what the
copy should have delivered, unexplained, inside a company whose hard rule is that such
rows are never deleted. Close those two gaps in writing, log a tested restore, file a
disposition record, and Option A is a clean approve. Delete nothing until then. The $20/mo
is the cheapest insurance this company buys; the reputational cost of an unreproducible
historical claim is not.

*— The Outsider*

---

# BOARD MEMO — The Executioner
## 1.0 database disposition (board review 2026-07-16, memo filed 2026-07-15)

Mandate: executability only — exact ship steps, verification before/after each, rollback
paths. Judged within the foundational principles (accuracy, reproducibility, no epoch
mixing, held-out ledger, flag-never-force).

## Live executability probes I ran on this box (2026-07-15, read-only)

| Probe | Result | Consequence |
|---|---|---|
| `heroku --version` + `heroku pg:backups -a nowtrendin` | CLI 11.8.0; command WORKS; **"No backups"** | The `C:\Program` CLI bug does NOT hit `pg:backups:*` (pure API calls, no local binary spawn — the bug only affects `heroku run`/`pg:psql`). And: **nothing is archived today** — the 1.0 DB is a single copy living at Heroku's mercy. |
| Free disk on C: | **1,675 GB** | A 10.8 GB DB's compressed custom-format dump (est. 1–4 GB) fits trivially, twice over. |
| `pg_restore`/`pg_dump`/Docker | **NOT installed** | Local `pg_restore --list` verification needs a one-time client-tools install (winget), OR we verify via a Heroku-side scratch restore (my recommended gold check — it also dodges local tooling entirely). |
| psycopg2 | 2.9.12, works | All SQL verification (row-count manifests, restore diff) goes through direct psycopg2 connections — never `pg:psql`. |

Key mechanics facts that shape every sequence below:
- Heroku-side backups are deleted WITH the add-on, and add-on destruction on essential
  tier is FINAL (no continuous protection / no undelete). Therefore: **every verification
  happens BEFORE `addons:destroy`, and destroy is founder-gated.**
- `pg:backups:url` presigned links expire (~hours). Download immediately after minting;
  regenerate + `curl -C -` resume if interrupted.
- The 1.0 app is at 0 dynos — capture runs against an idle DB, no load risk.
- A restore-test scratch DB must be **essential-2** (essential-0's 1 GB cap cannot hold
  10.8 GB). Prorated-to-the-second: a few hours ≈ well under $1.

---

## VERDICTS

### A. Archive + delete — **SHIP** (this is the one; everything else is worse or waiting)

The only option that ends the $20/mo burn while preserving the frozen June record
byte-for-byte, restorable forever. Operational surface is small, every step is
independently verifiable, and the whole path avoids both broken CLI commands.

**Ship-and-verify sequence (in order; each step gates the next):**

0. **Ground-truth manifest (BEFORE capture).** Via direct psycopg2 to
   `heroku config:get DATABASE_URL -a nowtrendin`: per-table row counts for all 28
   tables + min/max of the date columns on the big five (velocity_scores 9,718,671
   expected; pending_detections 1,841; accuracy_ledger 6). Write
   `audits/archive/NOWTRENDIN10_DB_ARCHIVE_MANIFEST.md`. The DB is frozen — these
   numbers must match EXACTLY at every later check.
1. **Capture.** `heroku pg:backups:capture -a nowtrendin`. Poll
   `heroku pg:backups -a nowtrendin` until `Completed`; record backup ID (b001) and
   the **processed size** from `heroku pg:backups:info b001 -a nowtrendin` into the
   manifest. Verify: status Completed, no warnings.
2. **Download.** `heroku pg:backups:url b001 -a nowtrendin` →
   `curl.exe -o nowtrendin10_2026-07-16.dump -C - "<url>"` into a local archive dir.
   Verify: downloaded byte size == processed size from step 1 (partial-download check).
3. **Checksum.** `Get-FileHash -Algorithm SHA256` → record in manifest.
4. **TOC inventory.** One-time `winget install PostgreSQL.PostgreSQL.17` (client tools),
   then `pg_restore --list nowtrendin10_2026-07-16.dump`. Verify: readable TOC, all 28
   tables present, no error. (Catches a corrupt-but-right-sized dump.)
5. **GOLD test-restore (do it — costs <$1, converts "probably fine" into "proven").**
   `heroku addons:create heroku-postgresql:essential-2 -a nowtrendin` (a SECOND
   attachment on the frozen app — NEVER on nowtrendin-v2-engine, and NEVER targeting
   the original DATABASE_URL). Then
   `heroku pg:backups:restore b001 <NEW_ATTACHMENT>_URL -a nowtrendin --confirm nowtrendin`.
   Verify via psycopg2 against the scratch DB: per-table row counts == step-0 manifest,
   exact. Then `heroku addons:destroy <scratch-addon> -a nowtrendin`.
6. **Offsite copy.** Second copy into the OneDrive-synced archive folder (Desktop tree
   auto-syncs) or external drive; re-hash the COPY and compare to step 3; on OneDrive,
   mark "Always keep on this device" (Files-on-Demand dehydration would silently hollow
   the local copy). Two verified copies, two locations, before anything is deleted.
7. **Commit the manifest** (never the dump) to the repo — capture ID, sizes, SHA256,
   table inventory, row counts, file locations.
8. **FOUNDER GATE (flag-never-force).** Present the manifest + both hashes. Only on an
   explicit "delete": `heroku addons:destroy <1.0-pg-addon> -a nowtrendin --confirm
   nowtrendin`.
9. **Post-verify + cost bookkeeping.** `heroku addons -a nowtrendin` shows no Postgres;
   update `COST_HEROKU_USD` 112→92 on the engine so Cost Sentinel reads honestly
   ($531.90 → ~$511.90 vs the $700 cap); note it in the Data Subscriptions agent's view.

**Who verifies:** Claude executes and produces evidence; the FOUNDER verifies (reads the
manifest, sees matching hashes/counts) and personally rules the destroy. No deletion on
agent judgement alone.

**What could go wrong / mitigations:** corrupt dump → steps 4+5 catch it before any
delete; partial download → size match + `-C -` resume + hash; URL expiry mid-download →
regenerate, resume; Heroku backup vanishing with add-on → all verification precedes
destroy, destroy is last and gated; CLI bug → sequence uses only `pg:backups:*`/`config`/
`addons` (API-only, probe-verified) + psycopg2, never `pg:psql`/`heroku run`; restore
aimed at wrong DB → explicit attachment names, v2 app never touched; OneDrive dehydration
→ pin + re-hash.

**Rollback:** the dump IS the rollback. To resurrect: create a fresh essential-2, then
either `pg:backups:restore` from an HTTPS URL of the dump (re-upload) or — simpler on
this box — local `pg_restore -d "<new DATABASE_URL>" nowtrendin10_2026-07-16.dump` using
the step-4 client tools (direct connection, no CLI bug exposure). Hot access returns in
under an hour, forever, for $0 standing cost.

### B. Archive + keep — **CUT**

Steps 0–7 of A, then keep paying $20/mo for hot access nothing queries. There is no
scheduled forensic backtest naming this data; all live research (ledger feature-mining,
GHOST_FEEDS case) runs on v2. A's rollback restores hot access in <1h whenever a real
need appears — $240/yr is a bad price for saving one hour, someday, maybe. If the board
wants a hedge: A with a 30-day founder-side delay before step 8 gets you B's optionality
free (Heroku only bills while it lives — but then just rule step 8 on schedule).

### C. Selective transfer — **CUT** (integrity, not just effort)

The only unique rows are the 06-15→07-02 parallel tail from a DIFFERENT engine +
calibration epoch. Importing velocity rows mixes epochs (breaks reproducibility,
Principle 2); importing 1.0's leaderboard-era pending_detections pollutes the held-out
ledger's honest denominators (§14) — the exact class v2 just retired as structurally
LAGGED. Even executed perfectly (epoch stamps, dedupe against the 265,863 pre-split rows
v2 already holds), the end state is worse than not doing it. Operational surface
(custom psycopg2 ETL, dedupe keys, provenance columns, backfill verification) is real
work purchasing negative value. The dump from A preserves the tail for any future
held-out READ — which is the only legitimate use it has.

### D. Full transfer — **CUT** (physically blocked, and C's flaws at 10× scale)

10.8 GB does not fit essential-1 (10 GB, 32.5% used) — requires paying for a v2 tier
upgrade FIRST to import 9.7M redundant 30-minute-cadence rows into the serve path
(prewarm/superset builds now scan a ~5× velocity table for zero analytical gain, on the
engine whose pool outage we just recovered from). Every integrity objection from C
applies. There is no verify step that makes this good; the pre-check fails it.

### E. Status quo — **CUT** (it is B minus the archive)

Pays B's $20/mo AND keeps the record as a single unarchived copy (probe-confirmed: zero
backups exist right now) exposed to fat-finger deletion or account mishap. "Decide
nothing" is the only option with an unbounded downside and no upside. If the founder is
not ready to rule on deletion, execute A steps 0–7 THIS WEEK anyway — the archive is
correct under every future ruling, including reverting to B.

---

## Bottom line

Ship A. Run steps 0–7 immediately (no destructive action, ~1 afternoon, <$1 in scratch
DB proration); park at the founder gate. B/C/D/E all lose to "verified dump in two
places, then −$20/mo": B on cost, C and D on the foundational principles themselves,
E on both. The one non-negotiable in the sequence: **nothing is destroyed until the
test-restore row counts match the pre-capture manifest exactly and both copies hash
identical.**

---

# BOARD MEMO — The Economist
## Re: Disposition of the frozen 1.0 Postgres (options A–E) · 2026-07-16

**Position in one sentence:** preserve the record, refuse the splice — Option A with archival
conditions; every transfer option is a regime-splicing error dressed up as thrift or completeness.

---

## 1. The framing question: what IS this data, economically?

Before choosing a disposition, classify the asset. The 1.0 database is **not** a long time
series. It is a 28-day June window (2026-06-04 → 07-02), of which everything before 06-15
already lives inside v2 (the pg:copy; v2 retains 265,863 pre-split rows under the 365-day
rule). The genuinely unique residue is a **17-day parallel tail** (06-15 → 07-02) scored by
a *different measurement instrument* — the frozen engine, pre-dating v2's dual-pathway
changes, INV-1 serve-stored rule, first-crossing ledger enrollment, and the date canon.

Friedman & Schwartz spent decades building *A Monetary History* precisely because long,
consistent, painstakingly assembled series settle arguments theory cannot. But their method
had two halves, and both matter here: (1) never discard primary records; (2) never splice
series measured under different definitions without explicit, documented adjustment. When
the Fed redefines M1/M2, you do not pour the old series into the new column and pretend the
panel is homogeneous — you keep both, document the break, and bridge explicitly or not at
all. The 1.0 tail is an old-definition series. The accuracy ledger — this product's
monetary-history project — is only a moat if its panel is internally consistent.

## 2. The Taleb question: is there silent evidence in deleting?

Yes — *if deletion meant destruction*. Two engines scoring the same weeks is a genuine
natural experiment: an out-of-sample comparison set that could one day answer "did the v2
calibration changes actually improve early detection, or is the improvement narrative?"
Discarding it unexamined would be silent evidence in its purest form — the graveyard of the
alternative engine's record removed before anyone counted its bodies.

But the honest sizing of that experiment, against the null hypothesis (Malkiel): 17 days;
a noisy 30-minute-cadence scorer with no effective pruning; and 1.0's own ledger contains
**six rows, all LAGGED** — the frozen engine barely kept its own score-sheet. Any future
comparison would have to be reconstructed from raw velocity rows, and 17 days of fat-tailed
attention data has almost no statistical power. The correct response to "low power but
nonzero option value" is not $240/year of hot storage — it is a **verified, restorable
archive**. The dump preserves the natural experiment at ~zero carrying cost. Silent
evidence is answered by archiving, not by paying rent on a corpse.

One more Taleb point, uncomfortable but necessary: judge this detection system on whether it
catches the rare huge surges. Nothing in the 1.0 tail helps with that judgment — the v2
ledger (90 resolved, held-out, patience-windowed) is the only instrument that can, and none
of options A–E touches it. That is as it should be.

## 3. The splice already exists — and nobody has stamped it

The sharpest finding in the pack is one the assessment states but does not press: **v2's own
panel already contains a regime splice.** The 265,863 pre-split rows retained in v2 were
scored by the 1.0 engine. The epoch boundary (2026-06-15) sits *inside* the live 365-day
window today and will remain there until mid-2027. Deleting the 1.0 add-on neither creates
nor cures this; but any cross-boundary analysis (calibration backtests, trajectory reads,
blended rates) that treats the panel as homogeneous is quietly committing the M1/M2 error
right now. This is fixable with a stamp, not a purge — see Prescription 4. Reinhart &
Rogoff's whole enterprise depended on knowing exactly when a series' definition changed;
give your future selves the same courtesy.

## 4. Verdicts

### A. Archive + delete — **APPROVE-WITH-CONDITIONS**
*Frameworks: Friedman & Schwartz (preserve the primary record; the archive IS the series) +
Taleb (silent evidence answered by a restorable dump) + Malkiel (the null hypothesis says
$240/yr buys no statistical power).*
Conditions (all precede deletion):
1. **Verify the dump restores** — restore to a scratch Postgres and reconcile row counts
   against the table inventory in this pack (9,718,671 velocity rows, 1,841 pending, 6
   ledger rows). An unverified backup is not an archive; it is a hope. Bernstein: risk is
   what remains after you think you've measured — "we captured a dump" is not "we can read
   it back."
2. **Two copies, one off the local machine** (local + cloud object storage), with checksums
   recorded. A single local copy of an irreplaceable record is a fat-tail exposure (disk
   death, ransomware, the OneDrive folder it would otherwise live in).
3. **A frozen provenance README beside the dump** (see Prescription 3).

### B. Archive + keep hot ($20/mo) — **REJECT**
*Framework: Malkiel + Bernstein.* Hot queryable access is a payment for optionality you
will not exercise: no pipeline reads it, no analysis is scheduled against it, and any future
forensic question is served identically by restoring the dump to a scratch DB for an
afternoon. Under the null hypothesis, "we might want to query it someday" is a story, not a
use case — and Cost Sentinel is at $531.90/$700 with a v2 Postgres tier upgrade already
queued as the 365-day tail fills. Spend the $20 where the moat is.

### C. Selective transfer (the 06-15→07-02 tail into v2) — **REJECT**
*Framework: Friedman & Schwartz (the regime-splice/M1-M2 error) + the no-circularity and
honest-denominator principles.* This is the actively dangerous option. Importing 1.0
velocity rows for weeks v2 already scored puts two instruments' readings in one column —
even epoch-stamped, every downstream aggregate must now remember to filter, and one
forgotten WHERE clause corrupts a backtest silently. Worse: 1.0's 1,841 pending detections
were enrolled by the leaderboard-era logic v2 *retired as structurally LAGGED* on
2026-07-07. Importing them injects a known-biased cohort into the held-out ledger's
denominators — the precise survivorship-adjacent distortion §14 was built to purge, now
reintroduced voluntarily. Zero analytical gain, nonzero probability of corrupting the one
asset (the ledger) that cannot be rebuilt. If the parallel tail is ever wanted for the
natural experiment, restore the dump to a *scratch* DB and compare across databases — never
merge the panels.

### D. Full transfer — **REJECT**
*Framework: Bernstein (uncompensated risk) + arithmetic.* All of C's splice hazards, plus
it is physically impossible without first paying for a v2 tier upgrade (10.8 GB into a
10 GB cap already 32.5% used) — i.e., pay money to *increase* integrity risk. Nine million
of those rows are 30-minute-cadence bulk from an engine with no pruning: volume
masquerading as history. Friedman & Schwartz's series were long *and consistent*; this
would make v2's merely large and inconsistent.

### E. Status quo — **REJECT**
*Framework: Belsky & Gilovich / Zweig.* This is not an option; it is status-quo bias with a
$20/mo invoice. Deciding nothing is choosing B without B's (already rejected) rationale.
The behavioral literature is unambiguous: inertia is the default failure mode of exactly
this kind of small-recurring-cost decision. Rule on it.

## 5. PRESCRIPTIONS

1. **Restore-verify before delete** *(Bernstein — risk is what remains after you think
   you've measured).* Capture → download → restore to scratch → reconcile row counts and a
   sample of date ranges against this pack's inventory → only then delete the add-on.
2. **Geographic/logical redundancy for the archive** *(Taleb — fat tails apply to storage,
   not just markets).* Two copies, different failure domains, checksums logged. The archive
   is now the ONLY copy of the frozen engine's record; treat it accordingly.
3. **Provenance README frozen with the dump** *(Reinhart & Rogoff — a long panel is only as
   good as its regime documentation).* Contents: engine epoch and what it lacked (no
   dual-pathway v2 changes, no INV-1, leaderboard enrollment, pre-date-canon), exact date
   ranges per table, the known defects (6-row all-LAGGED ledger; 30-min unpruned cadence),
   and the correction that this DB contains nothing before 2026-06-04. A future researcher
   who misreads this dump as comparable-to-v2 data does more damage than deleting it would.
4. **Stamp the 2026-06-15 epoch boundary inside v2** *(Friedman & Schwartz — document the
   splice you already own).* The 265k pre-split rows in v2 are 1.0-scored; add an
   engine-epoch marker (a `param_version`-style stamp or a documented boundary constant) so
   no cross-boundary aggregate is ever computed unsegmented. Display/metadata only — no
   score impact, no row rewrites, consistent with forward-only rules.
5. **If the natural experiment is ever run, pre-register it** *(Taleb — narrative fallacy;
   Malkiel — the null).* Before restoring the dump for a two-engine comparison, write down
   the question and the acceptance criterion first, state the power limitation (17 days),
   and compare across scratch-vs-live databases — never by import. Otherwise the exercise
   will produce a story, not a finding.
6. **Never publish cross-epoch blended rates** *(Friedman & Schwartz + the existing
   blended-vs-tracked-race discipline).* Any headline metric whose window spans 06-15 must
   either exclude pre-split rows or disclose the segmentation — same rule already applied,
   correctly, to the catch-all % and the tracked-race split.

— The Economist

---

**Chairman — your decision per item.**
