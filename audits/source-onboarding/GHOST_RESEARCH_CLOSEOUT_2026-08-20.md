# GHOST_RESEARCH_FEEDS — trial close-out (overdue; window unmeasurable)
### 2026-08-20 · read-only · A4-SEQ step 4 · Board-ordered precondition for the shadow trial
### Flag: `GHOST_RESEARCH_FEEDS=1`, live since 2026-07-15 (founder-ordered flip). Advertised trial: two weeks, ≈ 2026-07-15 → 2026-07-29. Readout owed ~07-29; delivered 2026-08-20.

---

## 1. THE HEADLINE FINDING IS ABOUT PROCESS, NOT THE FEEDS

**The advertised evaluation window cannot be measured anymore.** `raw_signals` /
`topic_signals` run on a short rolling retention; the oldest row in production is
**2026-08-13 06:30 UTC**. Every research-feed row from 07-15 → 07-29 — the entire frozen
trial window — has been pruned. The Forecaster's warning at the board ("the delay itself
lengthens the window until the readout flatters") understated the failure mode: **a readout
delayed past the raw-data retention horizon is not late, it is destroyed.** No amount of
diligence today can reconstruct the window this trial promised to score.

Standing rule proposed from this (for the Chairman): **every monitored trial's close-out
date must sit INSIDE the retention horizon of the data it needs, and the close-out
obligation goes on the dated-trigger cadence (`/monitor/deferred-triggers`) at flip time** —
not in prose. This close-out is the second consequence of un-dated readouts (the board found
the first: flags flipping while verdicts sat unwritten).

## 2. WHAT CAN BE MEASURED HONESTLY (the observable 08-13 → 08-20 week)

| Source | Items | Topic rows | Distinct topics |
|---|---|---|---|
| War on the Rocks | 85 | 114 | — |
| Global Issues | 23 | 28 | — |
| Rest of World | 8 | 10 | — |
| RAND (blog) | 10 | 11 | — |
| **Total** | **126** | **163** | **136** |

**Quality — the extractor is doing its job.** Of 136 distinct topics, **1** fails the
serve-time quality gate (`american` — an inflected common word) and **0** are 3+-word junk
fragments. Sample output is entity-grade: `dr congo`, `hormuz`, `pentagon`, `nairobi
biodiversity`, `pakistan crackdown`, `fedorov`. The §16 FORMAT-gate concern that justified
the entity-anchored extractor (junk entering the corroboration-exempt expert tier) has
**not materialized** in the observable week. No topic-quality or catch-all auditor alarm
attributable to these feeds is on record for the flag's whole life.

**Volume.** ~126 items/week across four outlets (~2.5% of Dark-Matter-tier volume) —
low-frequency publishers, as expected at onboarding. Cost: $0 (free RSS, production UA).

## 3. LEDGER CONTACT — none attributable

Naive topic-key matching finds 5 ledger rows and 21 pending rows sharing topics with the
research feeds (`iran`, `china`, `mexico`, `england`…) — **all of them enrolled from June
detections, BEFORE the 07-15 flip, on topics also carried by many other sources. Zero
enrollments are attributable to the research feeds.** No claim of research-fed earliness can
be made, in either direction. Two structural reasons no D-side effect was possible
regardless: (i) the board-verified writer defect — `_write_topics` hardcoded
`is_first_timer=0` for every ghost/research topic row, so these feeds could never move D's
numerator; (ii) expert-pathway G is where they route, and G attribution needs the shadow
instrument that does not exist yet. The feeds have been supplying the expert pathway while
the component this trial hoped to inform was unplugged — the board's finding, confirmed
here at close-out.

## 4. VERDICT OPTIONS FOR THE CHAIRMAN

- **KEEP (recommended by the evidence above):** extraction precision clean over everything
  observable, zero cost, zero auditor alarms ever, §16 five-gate PASS on record
  (2026-07-07), and the roster is the only proven entity-anchored expert-tier supply — the
  exact class the shadow trial needs as candidates. The trial's advertised QUESTION ("do
  research feeds surface topics before mainstream?") remains **UNANSWERED — not failed** —
  and transfers to the shadow trial, which is the instrument actually capable of answering
  it (sealed races, control arms, D plumbing repaired).
- **ROLLBACK:** defensible only on process grounds (the trial that justified the flip was
  never scored). It would remove clean, free, §16-passed supply and answer nothing.

**This close-out discharges A4-SEQ step 4 and the Guardian's freeze condition** ("no further
D-side coverage flags until the readout lands") — the readout has landed, with its failure
honestly stated.

## 5. LESSONS SEALED INTO THE NEXT TRIAL'S PREREGISTRATION

1. Close-out date INSIDE the data-retention horizon; readout obligation on the dated cadence.
2. Snapshot-at-enrollment (the shadow ledger persists its own rows — never dependent on
   short-retention operational tables for its evidence).
3. "UNANSWERED" is a written verdict option, distinct from failed (this document is the
   precedent).

**RULED — Chairman, 2026-08-20, same day: KEEP.** The research feeds are permanent roster;
the unanswered trial question transfers to the sealed shadow trial (prereg PIT `e90af6df..`).
