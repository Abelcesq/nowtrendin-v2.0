# Advisory Board Review — Warm/Cold Override-Map Refresh (2026-07-10)

**Convened at the Chairman's request:** review + research + recommend the best approach to the warm/cold refresh issue, for **accuracy of data and scoring**.
**Mechanics:** six independent archetype agents, identical code-grounded evidence pack, no cross-talk. Collation only — the Chairman rules.

## What is being decided

Serve-time category `_category_for` reads two in-memory maps (`_SITUATION_CAT`, `_CONTEXT_CAT`) that reset **empty on every process restart** and rebuild via a background daemon (context map ~4–5 min post-boot, ~69k entries). Cold → bare-lexicon fallback → the catch-all metric reads ~68% vs the warm ~33%. Proven live: two deploys swung the auditor **33.6 → 68.5 → 33.4** within an hour. Question: what is the best approach, and does it touch data/scoring accuracy?

## Research pack (code-grounded, established BEFORE convening)

An independent inventory agent (file:line-cited) swept every cold-start in-memory surface. **Bottom line: scoring and all three ledgers are INSULATED.** `/scores` serves stored `serve_payload`; stale rows serve stored values verbatim (INV-1); the scoring-admission gate `_passes_corroboration` deliberately uses the **stateless import-time bare lexicon** (`_topic_category`), NOT the cold `_category_for` maps (the documented non-circular design); all three ledgers are DB-driven and restart-safe. Other cold state = TTL read-caches rebuilt from stored DB rows (cold → honest 503 "warming", never a wrong value). The confound is confined to **display category + the catch-all metric**. The Challenger independently **resolved the market/crypto "unconfirmed" gap**: those engines have zero `_category_for` refs and zero mutable module globals — not exposed.

## The six memos (condensed)

### 1. The Challenger — **found the exposure the inventory missed** (decisive)
The metric is guarded in the READER (`catchall_attribution`) but **NOT in the WRITER**: `catchall_auditor` (`monitoring_agents.py:711`) persists a row to `catchall_floor_log` every run (`:868`) with **no warmth guard**. A cold-window run writes a **~68% row into the permanent trajectory**, and `single_source_leak` computed over the cold-inflated catch-all set can trip `leak_delta > 10` → **`floor_trend = "WORSENING"`** = a **false floor-integrity alarm** (§13: WORSENING "signals floor disabled or junk bypassing corroboration"). `fragment_category_auditor` (`:525`) is likewise unguarded (cold ≥70% alert). Also: category-**filtered** trend views change row-set membership warm vs cold (`gad.py:9425-9426` — scores right, the *list* differs). Market/crypto resolved (not exposed). **Verdicts:** A APPROVE-**WITH-CONDITIONS** (extend the guard to the writer — mandatory), B/C APPROVE-COND (stale-but-specific < bare-lexicon; stamp age), D REJECT, **E APPROVE (best structural fit) hard-gated by the writer-guard**, F REJECT (do-nothing to the writer is not acceptable). Recommends **E gated by the writer-guard precondition**.

### 2. First-Principles Guardian — honesty is the fix; name the drift
The moat (score + ledger) is provably insulated → the confound touches it **not at all**; this is a **display-honesty + metric-honesty matter, not scoring accuracy**. The real fix: **never publish catch-all % as an accuracy KPI; stamp warmth** (= A). Names the drift: *fixing a cosmetic operational metric dressed up as "protecting scoring accuracy"* can license unbounded complexity (B/C/D) against a target that was never the moat. **Verdicts:** A APPROVE, F APPROVE (A and F are one position), E APPROVE-COND (ops latency, not accuracy), B/C APPROVE-COND **display-quality only** under 4 conditions + a firewall (never wired into scoring; never replaces the honest-503 on data caches), **D REJECT** (trades real availability for a cosmetic).

### 3. The Expansionist — the lone dissent: C is the scale answer
The mechanism is a **per-dyno, in-memory, full-recompute** artifact — hard-codes single-process AND single-region. At a multi-region fleet the "General" window degrades from a transient into a **standing per-dyno inconsistency** (two users, same topic, different category, same second), and the 200k-row rebuild × dynos × boots is a growing DB cost center. **Verdicts:** **C APPROVE (the scale answer** — persist + serve-last-known-good + **incremental**, fleet-shared); B APPROVE-COND (must be incremental+shared, else you only moved the scan); A/F REJECT as *end states* (perpetuate the single-process assumption); D REJECT (cutover drag × regions); E APPROVE-COND (freshness layer only). B/C also create the clean producer/consumer seam the eventual multilingual/entity-resolution rebuild needs.

### 4. The Outsider (VC/banker) — cosmetic label flicker; don't burn a sprint
Score + track record confirmed unaffected → **worth unchanged**. **Verdicts:** A APPROVE (the floor, and the part that mattered — a lying dashboard fools *you*); **B/C REJECT** as gold-plating; **D REJECT-hard** (degrade real availability for a label?); E APPROVE-COND (only if near-zero effort on existing rails); F APPROVE as acceptable minimum. Wants **A + E-if-cheap, budget a day not a sprint**. Point-blank ask: *"Show me an automated test that fails the build if the cold-window score ≠ the warm-window score — does it exist and is it green?"* (a guard-test, not an assertion).

### 5. The Economist — a metric that reads 33 or 68 on the same population is **not yet a series**
*Friedman & Schwartz:* a value that depends on observation conditions is an instrument with the calibration left off. **Verdicts:** A APPROVE (but **cold = REFUSE, not flag** — a cold reading measures a *different quantity*, bare lexicon; emit no number), F APPROVE (A+F are the substance), E APPROVE-COND (cheap hygiene only), **B REJECT** (trades known-bounded for unknown-stale — worse measurement property), **C REJECT** for the metric (hides the warmth state), **D REJECT** (fat-tail outage risk vs the 6.3h wedged-prewarm precedent). **Prescriptions:** (1) cold = refuse+store-nothing; (2) **fixed frozen panel as the series-of-record** (kills the moving-denominator confound B–E ignore) — *already built this session*; (3) condition-stamp every reading {warm, map_entries, param_version, cycle_phase, denominator_id}; (4) a **build-test that fails if the auditor reads the bare lexicon**; (5) level ± dispersion over ≥k warm reads — ban single-point baselines; (6) **demote catch-all below the ledger on the page**; (7) no serve-path engineering (insulated); (8) generalize the audit to every rebuildable-map/read-cache metric.

### 6. The Executioner — code correction kills E; A+F now, B only if justified
**Correction:** `_situation_category_loop` **already fires `_refresh_*` on its first iteration at boot** (`:311-319`) — the cold window is **compute-bound** (the 200k-row scan), NOT trigger-bound. So E "moves nothing earlier"; it just adds a second heavy caller to the thread with a prior wedge history. **Verdicts:** A SHIP (done — the only piece with real downside), F SHIP (document; the honest baseline), **B SHIP-LATER** (cheap: new snapshot table + flag-gated boot loader `CATEGORY_SNAPSHOT_LOAD`, config-only rollback) **only if the pre-ship mis-tag count proves the window is user-visible**; **C fold into B** (implementation detail, not a separate ticket); **D CUT** (readiness gate = the wedged-prewarm failure class → outage worse than a cold label); **E CUT** (no latency captured). Demands a **pre-ship test**: measure the true cold-window duration + diff `_category_for` cold vs warm over the working set (how many topics mis-tag).

## Live measurement (the Executioner's pre-ship test — already in hand)

From the live cold/warm runs: cold = 4108/6000 catch-all, warm = 2005/6000 → **~2,100 topics (~35% of the feed) flip to "General" during each ~5-min cold window**. By the Executioner's own bar, that is large enough that B is **not** gold-plating on user-visibility grounds (though Guardian/Economist still weigh the stale-snapshot risk against it).

## Live evidence — the Challenger's writer finding, CONFIRMED (and self-inflicted)

The persistent `catchall_floor_log` trajectory now contains **two cold-poisoned rows**, written when the auditor was called during the cold windows after this session's deploys:
| logged_at | pct | rows | state |
|---|---|---|---|
| 2026-07-11T05:36 | 33.6% | 2015/6000 | warm (today's report) |
| **2026-07-11T06:28** | **68.5%** | 4108/6000 | **COLD-poisoned** (post-v228) |
| 2026-07-11T06:31 | 33.4% | 2005/6000 | warm |
| **2026-07-11T06:43** | **68.5%** | 4110/6000 | **COLD-poisoned** (post-v229) |

The whipsaw is now permanent in the moat's own monitoring history. This is the concrete, live proof that the writer-guard is mandatory — and an honest disclosure that this session's repeated cold auditor calls caused it.

## DISAGREEMENTS (signal, not noise)

1. **B/C — the central split.** Expansionist: **C is the scale-correct end state** (persist + serve-last-known-good + incremental + fleet-shared). Executioner: **B (C folded in) only if justified** — and the ~2,100 mis-tag count justifies it by his own bar. Guardian: B/C **display-quality only**, under conditions + firewall. Challenger: B/C reduce total wrongness, approve-cond with staleness stamp. **Outsider + Economist: REJECT** B/C — gold-plating (Outsider) / worse measurement property (Economist). → 1 strong-pro-scale, 3 conditional-yes, 2 no.
2. **E — factual dispute.** Challenger recommends E as the structural fix; Guardian/Outsider/Economist/Expansionist approve it conditionally as cheap hygiene; **Executioner CUTS it with a code correction** (daemon already refreshes on boot → E captures no latency). The code fact favors the Executioner: E does not shrink the compute-bound window.
3. **Cold handling — flag vs refuse.** Most say *flag/stamp* warmth (A as shipped). **Economist + Challenger go further: REFUSE** — the writer must **not persist** a cold row at all. The live poisoned rows prove the stronger position.
4. **Framing.** Guardian/Outsider/Economist: display + metric honesty, insulated from the moat → minimal. Expansionist: a scale-architecture liability. Challenger: a live false-alarm bug in the monitoring layer.

## Decision table — Chairman rules per item

| Item | Challenger | Guardian | Expansionist | Outsider | Economist | Executioner |
|---|---|---|---|---|---|---|
| **Writer-guard** (auditor/fragment skip the cold write) | **MANDATORY** | (implied by honesty) | — | (implied) | **REFUSE cold** | (part of A) |
| A — metric warmth guard (shipped) | APPR-COND (extend to writer) | APPROVE | REJECT as end-state | APPROVE | APPROVE (refuse) | SHIP (done) |
| B — persist + load-on-boot | APPR-COND | APPR-COND (display-only) | APPR-COND (incremental) | REJECT | REJECT | SHIP-LATER (if justified) |
| C — serve-last-known-good | APPR-COND (weaker than B) | APPR-COND (firewall) | **APPROVE (scale)** | REJECT | REJECT (metric) | fold into B |
| D — readiness gate | REJECT | REJECT | REJECT | REJECT-hard | REJECT | CUT |
| E — prewarm-synchronize | APPROVE (gated) | APPR-COND | APPR-COND | APPR-COND | APPR-COND | **CUT (no latency)** |
| F — do-nothing serve path + document | REJECT (not the writer) | APPROVE | REJECT as end-state | APPROVE (min) | APPROVE | SHIP (baseline) |
| Never publish catch-all % externally | YES | YES | — | — | YES (demote) | — |

### Board-consensus recommendations to the Chairman (informational — you decide)
1. **Writer-guard — near-unanimous, mandatory, cheap, fixes a LIVE false alarm.** Extend the same `_CONTEXT_CAT < warm_min` guard to `catchall_auditor` (skip the `catchall_floor_log` write when cold) and to `fragment_category_auditor`'s alert. Optionally delete the 2 cold-poisoned rows (06:28, 06:43) — a targeted cleanup, not a history rewrite (they are corrupt instrument readings, not data).
2. **Reject D** (readiness gate — reintroduces the wedged-prewarm outage class). **Cut E** (the daemon already refreshes on boot; E captures no latency — Executioner's code correction).
3. **A + F are the substance** for the serve path: honesty + leave the insulated path alone. The moat is not at risk.
4. **B/C is the open strategic call.** Not needed for accuracy (insulated), but the live ~2,100-topic/35% cold-window mis-tag is a real display inconsistency that becomes a standing per-dyno issue at fleet scale (Expansionist). If pursued, do it as **display-quality only**, snapshot-age-stamped, never wired into scoring, never replacing the honest-503 on data caches (Guardian's firewall) — and prefer **B's synchronous boot-load** over a separate C.
5. **Economist's series discipline (orthogonal, high-value):** make the catch-all a real series — refuse-when-cold, the **fixed frozen panel** (already built) as the series-of-record, condition-stamp every reading, a **build-test that fails if the auditor reads the bare lexicon**, level±dispersion (no single-point baselines), **demote below the ledger on the page**, and generalize the warmth audit to all rebuildable-map metrics.
6. **Never publish the catch-all % externally as a quality/accuracy claim** (Challenger, Guardian, Economist).

**Chairman — your decision per item.**
