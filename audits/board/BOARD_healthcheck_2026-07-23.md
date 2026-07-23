# BOARD REVIEW — Full Systems Health Check (2026-07-23, engine 36a9530)

**Convened:** founder requested a complete health check of all systems + skills + scoring, confirming
data is cataloged / logged / itemized / scored with nothing leaking, then a Board analysis with
recommendations. Six independent archetype memos (Challenger, Engineer, Economist, Fiduciary,
Data-Collection, Outsider), identical evidence pack (live endpoint sweep this date). Advisory only —
the Chairman rules. No code shipped from this review.

## 1. Audit result — what is HEALTHY (confirmed live)
Services all UP · git clean · 16/17 collectors HEALTHY · catch-all maps WARM (live, 68,251 entries)
· canonical-date quarantine 0 pending · Cost Sentinel **$542/$700 OK** (Apify down to $65 post
clock-slot-fix; AI $1.29 post Haiku-split) · all 3 ledgers reporting · scorer + prewarm fresh ·
S1 gate correctly HOLDS. The pipeline is cataloging, logging, itemizing and scoring; no data leak
was found (quarantine 0, no stale-payload, no dupes, no junk, no missing-pathway rows).

## 2. Findings + Board consensus (priority order F1 > F2 > F5 > F3 > F4)

### F1 — [CRITICAL, live] Mainstream detection collapse on `artificial_intelligence` — UNANIMOUS #1
`pipeline_integrity` CRITICAL: AI serves detection **40.0** in detail vs **79.1** stored dual-pathway
— a 39-pt serve-consistency break (the INV-1 covenant: one number everywhere). **The Engineer traced
the root cause in code:** at SCORING time the stored row is self-consistent (`apply_calibration`
runs, then the dual-pathway block overwrites detection→79.1 and stamps `detection_pathway='mainstream'`).
The break is at SERVE time — the detail path re-runs `apply_calibration`, and the pathway gate
(`signal_calibration_integration.py:~1216`) preserves the mainstream headline ONLY if it reads
`detection_pathway`; on a **missing/None tag it defaults to `'expert'`**, whose recompute
structurally collapses mainstream topics to ~25–40 (the FIFA-27.6 / Trump-25.8 behavior the code
comment warns of). List/prewarm serve the stored 79.1; the live-recompute detail path collapses to 40.
- **Severity:** unanimous stop-ship for any demo touching AI (Outsider/Fiduciary: reputational — the
  flagship query contradicts itself; a buyer who sees two truths trusts no number). "Only 1 flagged"
  is **not** proof of isolation (Challenger/Economist): the auditor samples; a gate regression is a
  *class* defect — the conspicuous topic got caught, quieter mainstream topics collapsing to 40 pass
  unnoticed.
- **Disciplined fix (Board-agreed):** (a) two-part code fix — make the gate **fail-safe** (preserve the
  headline when the pathway tag is absent/unknown, never collapse on ambiguity) AND surface
  `detection_pathway` in every serve read; prefer serving the stored `serve_payload` on the detail path
  per the serve-stale rule; (b) run a **corpus-wide** served==stored detection check across /topics,
  /scores, /scores/{key} to measure blast radius (not a sample); (c) held-out backtest across all
  mainstream topics; (d) regenerate serve_payload; (e) founder sign-off. **Never hand-patch the row.**

### F2 — [OPERATIONAL] The Canonical-Date Auditor (Agent 16) can't reliably run
`/monitor/datecanon` 503s at the 30s router 2-of-3 times (succeeded once at 27s). A monitor that times
out is not monitoring → §14 date-canon compliance is only intermittently verifiable. Blind-spot, NOT a
confirmed leak (quarantine backlog 0 when it does run). **Fix = architectural, not a timeout bump
(unanimous):** move the heavy full-schema audit off the web router to an async/scheduled worker that
writes a status row, and make `/monitor/datecanon` a fast read of the last run — the exact
`/monitor/catmaps` pattern already proven. Audit other >20s monitors for the same router risk.

### F5 — [REPORTING integrity] The ledger cannot yet support ANY accuracy claim
Attention ledger: 93 evaluated / 1,102 pending / 10.8% blended. **Board is emphatic:** the 1,102
pending are **right-censored, not failures** — a naive blended proportion is biased downward and is
statistically empty at n=93 (Economist: 95% CI ≈ [6%, 19%], wider than any competitor's claimed edge).
(1) NEVER publish blended 10.8% / catch-all % / census % as accuracy externally (customer should never
see bare 10.8% — reads as failure via survivorship). (2) Surface the **tracked-race EMERGING cohort
rate WITH its denominator**, or nothing — and CONFIRM that reporting hasn't silently regressed to
blended-only. (3) Economist's highest-leverage accuracy idea: model time-to-breakout with
**survival analysis (Kaplan-Meier)** so censored rows contribute correctly — raises statistical power
with zero new detections. Threshold: n ≥ ~200 resolved in one cohort before any external statement.

### F3 — [REOPEN by rule, HOLD ship] D8_T2 tripwire firing legitimately — UNANIMOUS: review-only
Covered-lane `unmeasured_fraction` fell 0.524→0.362 (majority-MEASURED); the H2b-recalibrated tripwire
fired as designed. Per rule: **reopen D8's held-out backtest for REVIEW; do NOT reclassify to accuracy
or ship.** D8 stays presentation-truth — ledger-neutral by mechanism. Majority-measured makes exclusion
*bind on data rather than absence* (the precondition to look), not proof it moves a realized hit-rate.
Ship only if the reopened backtest shows a ledger delta + founder sign-off.

### F4 — [KNOWN/DEFERRED] Reddit collector DEGRADED (+ Guardian absent)
Real Dark-Matter breadth gaps. Most of the Board: **restore Reddit** (cheapest early-signal breadth;
"before it arrives" lives there; `REDDIT_CLIENT_ID` is mostly a config task). Data-Collection dissent:
**Guardian first** — single-config reputable RSS that clears the §16 5 gates cleanly (mainstream-M
breadth), queue Reddit second (OAuth + noise → needs the full backtest-before-ship). Neither ships
without all 5 onboarding gates + backtest.

## 3. Highest-leverage recommendations (consolidated)
- **ACCURACY:** fix F1 (served==stored, one number everywhere) — a wrong served score outweighs any
  collection gap; then surface tracked-race cohort alongside blended; then the survival-denominator.
- **SYSTEMS:** add a permanent **INV-1 serve-consistency gate** to the deploy pipeline (corpus-wide
  served==stored across the three endpoints) so an F1-class break blocks the ship, not the next audit;
  and make datecanon runnable (async + cached status).
- **DATA COLLECTION:** restore Reddit breadth (config) and/or onboard Guardian (clean 5-gate) — both
  through §16 gates + backtest; do not skip.

## 4. Red lines (unanimous)
No score change without founder sign-off + held-out backtest + serve_payload regen · never hand-patch
the F1 row · don't bump the router timeout · don't uncap the sweep · never publish blended /
catch-all / census % as accuracy KPIs · ledgers stay held-out · 5-gate + backtest before any source.

## 5. Chairman decision block (to be filled)
- **F1:** ☐ fix now (gate fail-safe + serve-stored detail + corpus scope check + backtest + regen) ☐ defer
- **F2:** ☐ async-worker + cached status ☐ defer
- **F5:** ☐ audit reporting (tracked-race surfaced? survival denominator) ☐ defer
- **F3:** ☐ reopen D8 backtest for review ☐ hold
- **F4:** ☐ restore Reddit ☐ onboard Guardian ☐ both ☐ hold
