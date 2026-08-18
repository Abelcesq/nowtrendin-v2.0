# NowTrendIn 2.0 — Session Log

A running, readable catch-up of what's been built and what's open — so any new
Claude Code session (or you on your phone) can resume without the local thread.

_Last updated: 2026-07-26 (money-movement program: R7 + dead insider source + runbook Steps 0-2 live)_

---

## Session 2026-07-25/26 — Money-movement program: 6 board rounds, R7 executed, primary insider source found DEAD, runbook Steps 0-2 live

Founder ordered the market/crypto reassessment -> money-movement build -> accountability
review -> master remediation. Engine v283->v287. Board record: 7 new docs in audits/board/
(market-crypto-signal, money-movement-build, mechanisms-and-tools, crash-physics-and-corpus,
accountability-review, MASTER_REMEDIATION, R7 evidence + CONTAMINATION statement).

**R7 EXECUTED + VERIFIED (config-only, v282):** `DARK_POS_WEIGHT=0` — the congress/13F blend
(6/6 against: directionless intensity; 0.6 = top-10-holdings index proxy) removed from
positioning_concentration. Blast radius confirmed the charge empirically: blend fired on
exactly 16 mega-caps of 300, zero elsewhere. Predictions recorded BEFORE the flip held
(flow unchanged 16/16, market ledger delta=0, ~12-cycle negative-z transient decaying:
NVDA positioning z -3.95 -> -1.93). Code default now also "0" (A7).

**PRIMARY INSIDER SOURCE WAS SILENTLY DEAD (found via §16 gate-5 live sample):** Finviz
ticker cells render a logo-fallback initial, so tag-stripping doubled every first letter
(LEVI->LLEVI, 111/111) — `insider_signal()` returned 0 rows for EVERY ticker, failing as
"no data" not an error. Also: Form 144 "Proposed Sale" (26.5% of feed) substring-counted as
executed sales; those rows column-misaligned. Fixed (logo-URL ticker recovery — preserves
MMM correctly; exact-match _TXN_CLASS; misalignment rejection); parser fix flag-gated
`INSIDER_PARSER_FIX` default "0", flips with R7-pattern capture after the transient decays.
Contamination statement: audits/board/CONTAMINATION_insider-dead-parser_2026-07-25.md
(window honestly unboundable: worst case 06-25 -> 07-25; no raw snapshots retained).

**MONEY-MOVEMENT INSTRUMENT (held-out, built, ZERO rows enrolled by design):**
disclosure-to-participation latency — trigger=filing instant; observable=insider buying
breadth vs own base rate; clock=abnormal SHARE volume vs baseline FROZEN at enrollment
(was decorative — sweep never passed it; now passed verbatim + regression: same data,
recomputed baseline=NO arrival vs frozen=5.0x arrival); proof=KM+Greenwood (was missing
variance entirely) vs matched controls, ONE pre-registered primary horizon. New modules:
ledger_survival, arrival_clock, flow_ledger (atomic treated+3-controls or nothing; refuses
without active prereg), insider_flow (ingest live-verified: 200 raw -> 69 written/47
tickers, F144/immaterial/misaligned refused+counted), macro_series (vintaged OFR/FINRA),
heldout_registry (R1/R2 firewall as AST audit + negative controls; 11 scoring modules,
5 acknowledged WRITE-ONLY exceptions — widening it immediately caught
financial_risk_gradient->market_accuracy_ledger, verified write-only). /monitor now 9
agents + flow_integrity reads `not_started` (never "ok" on an empty room).

**CALIBRATION (fixed seed 20260725):** unconditional 60d arrival null = 24.1% at the 3.0x
placeholder; Executioner's 5-8% target unreachable AND wrong direction (required n
DECREASES in p0); power ~110/200/430 treated/arm for 20/15/10pp -> UNIVERSE BREADTH is the
binding constraint (16 names = a decade; market-wide = 2-3 quarters; CI closes ~Dec 2026,
Oct-Nov with stratified log-rank primary). O8 backtest: only G2 floor-binding real
(market_momentum floor-bound 15/16 — 12-MONTH aggregates re-read 6-hourly = data defect;
median/MAD RETRACTED by its proposer; my own R7 transient confounded G1 3.57%->0.89%).

**RUNBOOK STEPS 0-2 LIVE (v287, verified):** pre-flip captures in audits/board/preflip/;
crypto COVERAGE-KEYED absence (absent when proxy_coverage=="thin" OR covered<2 — closes
the "partial with covered==1" BTC trap; served `absence_reason`; kill switch
CRYPTO_COVERAGE_GATE) so honest absence SURVIVES the parser flip instead of evaporating;
CONTRADICTION GUARD at the engine choke point (absent => flow="no_data", dark_matter block
OMITTED — kills BTC's live inflow/60.0-beside-all-absent breach, traced to ONE AV-fallback
proxy vote: 100*(0.5+0.5*0.2)=60.0); C2b crypto-ledger guard (record_from_serve was
enrolling on the suppressed direction — 1 CONFIRMED + 1 pending off a single proxy vote;
now skips absent/thin/covered<2; era rows ANNOTATED dead_parser_era, never deleted; NO
crypto rate published below 20 resolved). Live acceptance: 12/12 coins
absence_reason=proxy_coverage_thin, contradictions=0, ledger counts unchanged, fleet green.

**2026-07-26/27 continuation — PREREG LOCKED; the machine is one gate from enrolling.**
Salt set (v288, never displayed, WRITE-ONCE documented in ENV_REFERENCE). Step-6 WIRING
built + deployed inert (v289): `flow_enrollment.py` = the detector's ONE doorway (qualify =
the Chairman's >=3-buyers-in-10d cluster; controls = sector+size+ADV+PRETREND bucket inside
the frozen window, deterministic by group seed; ingest_panel REFUSES while INSIDER_PARSER_FIX=0
— the hard order is code, not a memo); endpoints /flow/status /flow/accuracy /flow/prereg
(internal-key). Firewall: 11 modules, 0 violations, 6 acknowledged exceptions. CORRECTED
CALIBRATION run (all 4 accountability fixes: pre-arrived excluded per multiple; -ln(1-p)x365/60;
universe FROZEN in tools/calibration_universe_2026-07-26.txt; ticker-clustered bootstrap):
3.0x corrected 60d null **19.6% [13.8-26.0]** — the ~20-25% regime; mechanical read = 3.0x.
**PRE-REGISTRATION LOCKED** (id 261716973f6968b4, registered 2026-07-27T04:19Z, git timestamp
3ca1bda BEFORE the lock): breadth>=3/10d · mult 3.0 · primary 90d · censor 180d ·
min_episodes 120 · stratified log-rank primary · falsifiers pre-registered. Re-lock costless
until row 1. Transient still hot (AAPL -3.96 / MSFT -4.19) -> flip waits; persistent monitor
armed to notify when all |z|<1.5. Remaining chain: flip -> INSIDER_FLOW=1 -> FLOW_ENROLL=1 ->
pending_treated>=1/pending_control>=3.

**PENDING CHAIRMAN RULINGS:** R-a arrival target (Board: 3.0-3.5x; gates prereg lock — the
only calendar dependency) · R-b parser-flip GO (transient must decay <|1.5|; -1.93 today)
· R-c ACTOR_ID_SALT (write-once, BEFORE INSIDER_FLOW) · R-e momentum signed-vs-magnitude
(NEW: abs(price_return_12m) — a crash scores like a rally) · R-f panel name ("N" collides
with the excluded component; letter-free candidates stand). NEXT: flip -> salt -> ingest ->
~150-line enrollment wiring (verified nonexistent; the one construction the freeze permits)
-> prereg lock -> `pending_treated>=1, pending_control>=3` — the number the freeze thaws on.

---

## Session 2026-07-24 — F1 residual risks R-D + R-C + F5 KM denominator (all shipped + verified live)

Founder: "fix f1 r-d, f1 r-c and f5 and also check reddit." All three are ADDITIVE read-layer changes
with **ZERO stored-score impact** (R-D computes at detail-serve; R-C is a new read-only endpoint; F5 is
report-time) → **no serve_payload regeneration required**. Verify-before-fix held throughout: taxonomy
paths traced + the KM math self-tested before deploy. Engine **v281** (`ba5629f`), gh-pages `a3a84fd`,
preview `0ec0ff9`. All verified LIVE.

**F1 R-D — "already arrived" UI disclosure (the trust item) — SHIPPED 3 surfaces.** The Board's residual
risk: a customer opening `artificial intelligence` sees Detection ~35 and reads it as a broken score. Fix
tells them WHY it's low and where the momentum actually is. Engine `_mainstream_context(topic_key, display,
s)` reads the AI taxonomy DIRECTLY (`lookup_topic` / `get_variation_map`) → returns a disclosure **only for
Tier-4** already-arrived umbrella terms, with the leading-edge Tier-1/2 sub-topics; exposed on
`/scores/{topic_key}` as `mainstream_context` (it was computed-then-DROPPED from the detail dict before).
Verified live: AI serves det 35.4 / stage WATCHING + `mainstream_context` {tier_label "MAINSTREAM — Already
Arrived", leading_edge [agentic coding, agent memory, 12-factor agents]}. Web (Screener.tsx) = disclosure
banner under the dual gradient + leading-edge chips; mobile (signal/[id].tsx + gradientApi + signals type)
= same, Aurora tokens (`#2A5B9E` sapphire, borderless). Heisenberg framing surfaced to the user: Detection
measures MOVEMENT not size; an already-arrived term has ~zero earliness left.

**F1 R-C — taxonomy saturation detector (FLAG-NEVER-FORCE) — SHIPPED (engine).** The hand-maintained Tier-4
cap list is a MOVING target; a term can cross into already-arrived (≥5 independent outlets =
`mainstream_confirmed`) while still NOT in the taxonomy and scoring high Detection — the F1 defect in
miniature. New read-only `GET /monitor/taxonomy-saturation`: surfaces confirmed-mainstream / broad-outlet
topics NOT in the taxonomy as CANDIDATES a human may add as a Tier-4 cap; prioritizes still-high-Detection
ones (a cap would most change the read). Changes NOTHING (Charter §5) — reviewed by the operator / weekly
improve-system audit. Verified live: 1495 candidates, **95 priority** (iran det 94.6/65 outlets, Donald
Trump 68.8/59, france 94.2/22, openai 82.1/21, agent 93.5/19 — exactly the saturated non-capped umbrellas).

**F5 — Kaplan-Meier confirmation over the right-censored pending pool — SHIPPED (engine + web).** The
Economist's F5 follow-up. `accuracy_ledger_enhanced.survival_confirmation()`: KM estimate treating the ~1,102
still-pending rows as RIGHT-CENSORED (365-day patience) instead of discarding them; event = confirmed by a
Google breakout (LED/SAME_DAY/near-LAGGED), excludes pre-broken (not a forward race). Reported ALONGSIDE —
never instead of — blended/tracked-race, under `report['survival']` + `/accuracy/ledger.survival`; web
Ledger.tsx KM stat card. Held-out, measurement-only, **not an external KPI** (catch-all-% rule). KM math
self-tested (monotonic, correct on a known example). Verified live: 1140 obs / 38 events / 1102 censored →
KM eventual **3.4%**. NOTE the direction: KM reads LOWER than blended 10.8% and tracked-race 26.3% because
the large long-pending pool that has sat WITHOUT confirming legitimately pulls survival down — the honest
conservative counterweight (resolved-only rates ignore the silent non-confirmers). Worth a Board read on how
to present a KM number that sits below the resolved-only rates without confusing a hedge-fund reader.

**Reddit — founder set the credentials (v280, ~34m before this work).** `REDDIT_CLIENT_ID/SECRET/USER_AGENT`
now all SET on the engine. The collector's DEGRADED "0 signals" reading (last run 47m ago) PREDATES the
credential set, so Reddit hasn't been re-exercised yet — it validates on the next collection cycle. Did NOT
trigger a manual production `/collect` just to test (the cadence covers it). Re-check the collector health on
the next session; if still 0 signals AFTER a post-v280 run, the creds need debugging.

**Deploy hygiene note (self-caught + fixed):** the first gh-pages attempt mis-fired — the `git worktree add
../ghp` collided with the existing `.ghpages-deploy` worktree, so the `cd` failed and a dist commit landed on
**main** by mistake. Caught immediately (was NEVER pushed to origin main), `git reset --hard` back to the
clean source commit `080e3f0`, removed the stray empty `assets/`, then redeployed correctly through the
existing `.ghpages-deploy` worktree. main is clean; origin/main unaffected.

---

## Session 2026-07-23 (cont.) — Full systems health check + Board + F1-F5 fixes

Founder ordered a complete health check (all systems/skills/scoring, no-leak sweep) → Board analysis
→ fix F1-F5. Audit: services UP, 16/17 collectors healthy, 0 quarantine leaks, cost $542/$700 OK,
3 ledgers reporting. Board (6 memos, `audits/board/BOARD_healthcheck_2026-07-23.md`) ranked findings
F1>F2>F5>F3>F4.

**F1 — mainstream detection "collapse" — RESOLVED, but the Board's diagnosis was WRONG (major lesson).**
The `pipeline_integrity` alert hard-coded "pathway gate regressed"; the Board inherited it; I deployed
that fix BEFORE tracing to ground truth — and it was wrong-direction and made it worse (desynced the
stage). Reverted. **Real cause (traced):** the served detection 40 for `artificial_intelligence` is
CORRECT — `ai_topic_intelligence.py` intentionally caps a Tier-4 "MAINSTREAM — Already Arrived"
umbrella term at its ceiling (det 40 / conf 48). Founder's **Heisenberg framing** (now in
METHODOLOGY.md): Detection=earliness/momentum (Δp), Confidence=position (Δx), conjugate — a fully
position-localized mainstream term has ~zero earliness, so its Detection correctly collapses no matter
how large its raw magnitude; the leading edge lives in its Tier-1 sub-topics. Stored 79.1 is a distinct
magnitude observable. **Two REAL bugs fixed (`7cff966`, no score value changed):** (1) stage desync —
serve tail now recomputes `signal_stage` from FINAL served det/conf (AI → coherent WATCHING, verified);
(2) auditor misattribution — B8 now taxonomy-aware + a STAGE↔DETECTION contradiction check + visible
`serve_taxonomy_capped` count. `pipeline_integrity` back to **ok**. **Board RATIFIED** the correction
6/6 (`BOARD_F1-ratification_2026-07-23.md`) with a standing scoring ruling + 4 residual risks logged
(R-A ledger can't validate the cap; R-B keep exemption visible [shipped]; R-C hand-taxonomy needs a
saturation-detector; R-D UI must explain the low number). **VERIFY-BEFORE-FIX** codified as a hard
rule for Claude across all models/sessions (CLAUDE.md §10a, nowtrendin2.0 skill rule 0, memory
`feedback-verify-root-cause-before-fix`, board doc).

**F2 — Canonical Date Auditor runnable — DONE (`7cff966` + `e191547`).** `/monitor/datecanon` H12-timed
out (503) 2-of-3; now a background thread computes the heavy scan and the endpoint is a fast status
read (0.55s, catmaps pattern; hourly TTL, ?force=1). Immediately surfaced a real finding that was
invisible while it timed out: `fastlane_recheck_log.detection_date` unregistered (0 non-canonical,
copied from pending_detections) → registered in DATE_SEMANTIC. (Per-process cache caveat, like prewarm.)

**F3 — D8 T2 reopen — REVIEWED, defer stands (`6895055`).** T2 fired (covered-lane unmeasured_fraction
0.524→0.362, majority-measured). Reopen review (`D8_REOPEN_REVIEW_2026-07-23.md`): D8-T1 (null-when-
all-absent) already SHIPPED live (D8_MM_EXCLUDE=1, 206/300 absent); the Δ=0 shield is intact (ledgers
never read mm, T3 not fired, market ledger unchanged 12 resolved/regime 6-of-11) → the fuller
renormalized-survivor exclusion still has zero ledger effect → DEFER STANDS. Reconciled the stale
DEFERRED_ITEMS D8 header (said "DEFERRED", now "T1-shipped").

**F4 — Reddit/Guardian — verified; Reddit needs founder credentials.** Guardian is NOT a gap (already
flowing via RSS — `blogs` collector HEALTHY 1669 sig/50m; only the optional content-API key is unset).
Reddit collector is wired + inert-safe ("ran 62m ago but 0 signals", clean skip) — the one real
Dark-Matter breadth gap; needs the founder to create a Reddit app + set REDDIT_CLIENT_ID/SECRET/
USER_AGENT (credential task, like OpenRouter — I cannot create the account).

**F5 — ledger reporting integrity — verified GREEN (no fix needed).** Tracked-race cohort IS surfaced,
NOT regressed to blended-only: API returns blended 10.8% + tracked-race 26.3% (n=38) + byEpoch (v1
39.1%, v2 6.7%) + byMaturity + pre-broken split + smallSample flag; the web Ledger view renders the
tracked-race rate WITH its denominator, never a bare number. Follow-ups logged: (1) Economist — survival
analysis (Kaplan-Meier) for the 1102 right-censored pending to raise statistical power; (2) hold the
Board's stricter external-publication n-threshold (never publish blended/catch-all/census as accuracy).

**F6 — market-panel AI Context refusal — FIXED (`148d492`).** Founder-reported: halted micro-caps
showed raw model meta-text as the "definition" (e.g. *"I appreciate your detailed request, but I
need to flag... the string 'paranovus entrmt tech cl a ord pavs' does not correspond to any
topic..."*). Reproduced live + traced. **Provenance:** these are NOT trending topics — they enter
from the official **Nasdaq trade-halt RSS** (`collect_nasdaq_halts`, Stage-2 microstructure) because
they were HALTED for volatility; the lane rule puts every non-watchlist/non-macro instrument (incl.
halt micro-caps) in `halted_microcap` (283 of 300). **Root cause (2 parts):** (1) the /explainer key
is broker boilerplate (`paranovus_entrmt_tech_cl_a_ord_pavs` → "paranovus entrmt tech cl a ord pavs")
the model can't identify → returns a refusal; (2) when `_extract_json` failed, the fallback stored
`short = text[:240]` — persisting the REFUSAL and serving it forever (§17 violation). **Fix:**
`_looks_like_refusal()` guard on ALL lanes (Claude / OpenRouter / Perplexity / SSE streaming) →
available:false, never stored/served (unit-tested vs both real refusals + genuine explainers);
`_humanize_instrument_name()` → "Paranovus Entertainment Technology (PAVS)" etc. (trend topics
unchanged, no regression; caught + fixed a self-introduced GIBO-name bug pre-ship); wired into all 3
explainer call sites; `POST /maintenance/purge-refusal-explainers` cleared the 6 already-poisoned
rows. **Verified live:** PAVS now serves nothing (correct §17 omit), NVVE regenerated clean
("Nuvve Holding Corporation (NVVE)... vehicle-to-grid technology"). Interesting: the 6 poisoned rows
included thin-context trend topics too (soccer players, a match pairing), not just micro-caps.

**Process note:** two PowerShell commit failures this session from em-dash/arrow chars in heredoc
messages + a new-file `git commit <path>` that needs `git add` first — switched to ASCII `-F` message
files / `git add` then commit. **F1-F6 all complete.** Founder credential asks outstanding: Reddit
(REDDIT_CLIENT_ID/SECRET/USER_AGENT). Follow-ups logged: F1 residual risks R-A..R-D (esp. R-D UI
"already arrived" disclosure + R-C saturation-detector), F5 survival-analysis denominator.

---

## Session 2026-07-23 (cont.) — P2-A streaming explainers (SSE): fresh AI Context feels <1s

Closes the phase-2 latency arc: the residual 2-5s "fresh" first-view now STREAMS.
- **Engine** `GET /explainer/{key}/stream` (SSE): cached explainer → ONE instant `full_text`
  event; fresh → Anthropic token deltas (Haiku, plain-text `short --- full`, same grounding +
  STRICT RULES via a format override — JSON can't stream legibly). Persists the same record
  (upsert-if-empty), records real cost from streamed usage, warms the in-mem cache.
  `ai_grade.explain_topic_stream_deltas` + `split_short_full` (defensive: no `---` → first
  paragraph = short, never empty).
- **Web** `api.streamExplainer` (EventSource + cancel fn) wired into **MarketSignal** + **Screener**
  AI Context: live token render with a `▍` cursor, snaps to short + "Read full definition" on done;
  ANY stream failure → the sync `/explainer` endpoint (which carries the OpenRouter lane). Grade.tsx
  kept sync (background context, no visible benefit). Mobile unchanged (RN has no native
  EventSource; its panels are cache-hit-instant for warmed topics).
- **Verified live** (engine `36a9530`, gh-pages `ef22f0c`): fresh `lagoon` — first token at
  **1.15s**, complete at 4.04s (15 deltas); second view (cached) — **0.18s** single event. The
  spinner-then-dump is gone; words appear ~1s in.

## Session 2026-07-23 (cont.) — P2-C market-panel prewarm + P2-B OpenRouter resilience lane

Founder-approved both phase-2 items:
- **P2-C:** the market panel's AI Context rides the SAME `/explainer/{key}` pipeline (keyed on
  `risk_topic`) but `_backfill_explainers` only drew trend topics — first viewers of an instrument
  paid full generation. The backfill now also warms the top market instruments (`risk_scores` by
  detection, ~limit/3 per cycle). The crypto rail needs no warming — its narrative is deterministic
  (`_crypto_analysis`), no AI call. Backfill query + write now handle empty-`short` rows with the
  same upsert-if-empty as the serve endpoint (no infinite reselect).
- **P2-B:** second-provider resilience lane via OpenRouter — **INERT until `OPENROUTER_API_KEY` is
  set** (pay-per-use, no subscription; satisfies the founder's <$20/mo bar). On an Anthropic FAILURE
  (the 2026-07-07 credits-exhausted outage class) the same prompt retries on `AI_FALLBACK_MODEL`
  (default `deepseek/deepseek-v4-flash`, verified against the live OpenRouter catalog) with
  `provider.data_collection="deny"` — our payloads are never training data. Wired into the topic
  explainer, `market_analysis` (the advice-word guardrail backstop now shared by BOTH lanes via
  `_advice_guardrail_ok`) and `propose_score` (Grade degrades to the open model rather than going
  dark; output stays labelled PROPOSED). **Anthropic remains primary — healthy calls never
  re-route.** Activation = founder creates an OpenRouter account + sets the key; nothing else.
- Cost estimate for fallback usage: real usage tokens × `AI_FALLBACK_PRICE_IN/OUT` env estimates
  (documented as estimates, never fabricated tokens); `_api("openrouter")` counter added.

## Session 2026-07-23 — AI panel latency (5-9s → instant-cached / ~2-4s fresh) + fast-model split

Founder: panel "AI Context" generation took 5-9s, target 1-2s; Perplexity subscription cancelled but
**config/code path deliberately preserved** (founder: don't switch it off; Claude is the temporary
fix; prefer free/<$20-mo). `AI_SKIP_PERPLEXITY=1` was already set since 2026-06-23 — panels were
already Claude-only; the 5-9s was Sonnet × a 3-5-paragraph output budget.
- **Fast-model split** (`transfer/ai_grade.py`): panel surfaces (topic explainer `_explain_via_claude`
  + `market_analysis` narrative) → `AI_FAST_MODEL` (default **claude-haiku-4-5**, env-overridable,
  ~3-5× faster at 1/3 price, guardrail prompts unchanged); **Grade synthesis (`propose_score`) stays
  on `AI_GRADE_CLAUDE_MODEL`** (Sonnet — quality over speed for score proposals). Cost accounting now
  model-aware (`_claude_cost`; the hardcoded 3/15 would over-report Haiku spend 3× to Cost Sentinel).
- **Output budget**: both explainer prompts 3-5 paragraphs → exactly 2 compact paragraphs;
  max_tokens 700→320 (explainer), 400→250 (market narrative); timeouts 60/45→30.
- **Pre-generation ON**: `EXPLAINER_BACKFILL_PER_CYCLE=15` (existed, defaulted 0) — top topics
  generate in the background each cycle → panel views hit cache.
- **Persist leak fixed** (found in testing): `INSERT OR IGNORE` + a pre-existing EMPTY
  `topic_explainers` row blocked the persist forever → those topics regenerated every restart
  (cost + the 4.6s "cached" rfk). Now upsert-if-empty (never overwrites a real explainer).
- **Measured**: cached ≈ **0.6-0.8s total incl. ~0.56s network RTT** (server-side ~instant); fresh
  first-ever generation ~2.7-5.5s (round 1, 500 tok) → expected ~2-3s at the 320-token budget;
  backfill makes fresh views rare. Engine deploys `f1887b1`→`e28951b`→(upsert) · config v269.
- **Cost ruling context**: steady-state AI usage is ~9 calls/week (caching) → Haiku pay-per-use ≈
  pennies/mo, satisfying the founder's <$20/mo preference with NO new vendor. Free-tier providers
  (Gemini/Groq free) REJECTED for panel use: free tiers train on submitted data — proprietary
  topic/market payloads must not become training data (enterprise confidentiality standard).

---

## Session 2026-07-20 (cont.) — D8 SHIPPED (T1 presentation-truth) + S1 REJECT parity (degeneracy test)

Founder ruled the board's T1/principle recommendations: "implement all of them, sequence for accuracy
and completion." Board record: `audits/board/BOARD_T1-principle-rulings_2026-07-20.md` (6 memos).

**S1 (ran FIRST — cheap, decides scope): PRINCIPLE arm TESTED → REJECTED.** The board's ledger-
INDEPENDENT congress-net degeneracy test (Economist synthesis; `audits/ledger-research/
S1_CONGRESS_NET_DEGENERACY_TEST_2026-07-20.md`): across the served universe congress `net(buys−sells)`
is **7 net-BUY / 7 net-SELL, mean ≈ 0** (clean net-buyers 3/0, 5/0 present) — it **DISCRIMINATES**,
unlike insider net (~15/15 structural sell = degenerate). So the insider-parity principle does NOT
transfer; **`positioning_intel.py` L118 stays UNCHANGED** (S1-4 reject). The regime-confounded 0-for-5
was never used as justification (unanimous red line). The PRINCIPLE arm of the S1 trigger is CLOSED;
the **n-arm (n≥15 or 0-for-10 EPISODES) remains** — the outflow question is settled by DATA, not the
parity shortcut. Spin-off flagged, not acted on: the 4 outflow mega-caps fire "outflow" at saturated
intensity 1.0 while two-sided (6 buys/14 sells) — a conviction/intensity item, its own future
investigation, NOT S1.

**D8 (T1 presentation-truth): SHIPPED, flag-gated `D8_MM_EXCLUDE`.** Backtest-proven ledger-neutral
(enrollment gates on flow+intensity, never mm — 0/12 resolved rows affected). Ruled spec = serve
`money_movement: null` + `money_data_absent: true` + an ABSENT money tier ONLY when EVERY money
component is absent/degenerate — **null-only, NO renormalized-survivor recipe** (no row-to-row recipe
drift); market_confirmation (M) untouched.
- **Engine:** `market_signal_engine.py` (equity) + `crypto_money_gradient.py` (crypto — all 12 coins).
  Truth-table verified: flag-OFF byte-identical (the 30.0 pin we're fixing); flag-ON nulls only the
  all-degenerate rows; a single live component leaves the composite exactly as-is.
- **Web:** `MarketSignal.tsx` + `Crypto.tsx` render an "n/a" money ring + a "Market-Confirmation-only"
  banner; the crypto page subtitle drops the "Money Gradient" headline when every coin is money-absent;
  list cells show n/a. `api.ts` types extended.
- **Mobile:** `gradientApi.ts` mappers thread `moneyDataAbsent` (money read → null); `risk/[key].tsx`,
  `crypto/[coin].tsx`, `RiskCard.tsx`, `CryptoCard.tsx` render n/a + "Market-Confirmation only",
  null-safe on the now-nullable `moneyMovement`/`lead`.
- Commit `c0d0575`; engine deploy `f169594` + `D8_MM_EXCLUDE=1` (config v266); web gh-pages `db7104f`;
  mobile preview Heroku `9736288` (PIN gate intact). **VERIFIED LIVE:** after a `/risk/collect` +
  `/crypto/collect` re-score, **166/300** flow-neutral equity rows serve the honest absent state,
  **0 directional rows wrongly nulled** (Apple/Nvidia/etc. keep real mm), all **12 crypto coins**
  serve `mm=null, tier=ABSENT` with market_confirmation preserved (BTC mc 49.1), and the **market
  ledger is untouched** (12 resolved, 50% blended, regime 6/11) — ledger-neutral exactly as the
  reopened backtest predicted.

---

## Session 2026-07-20 — Board hardenings review fixes H1–H8 / P1 / R1 + R2 principle-OR-n (all OPERATIONAL/doc; SHIPPED + VERIFIED LIVE)

Implemented the Chairman-ruled decision table from `audits/board/BOARD_hardenings-review_2026-07-20.md`
(6 independent memos on the E3/E4/E5 hardenings). Every item is OPERATIONAL or documentation — **no score
surface was touched**; the two gated score-affecting items (D8, S1) stay deferred behind their written
triggers. Engine deployed `fa0bbbc` (subtree → heroku-v2engine); origin `7e8114d`.

- **P1 — regime-adjusted market ledger (the diligence-defensible read).** `market_accuracy_ledger.report()`
  now serves `regime_adjusted`: ONE benchmark fetch (SPY, `MARKET_LEDGER_BENCHMARK`) over the union window,
  each row's verdict = did the flow-direction move BEAT the benchmark past a ±2% deadband (excess return),
  not an absolute ±5%. **Live read:** de-confounded, inflow still 6/6 (100%), outflow still 0/5 (0%),
  row-level 54.5%; episodes 3/6. The regime adjustment did NOT collapse the inflow lane — but n is tiny
  (6 resolved episodes), so R1 stands: neither lane is validated. This is now the ONLY market-ledger read
  we cite; the absolute rates are demoted.
- **R1 — symmetry ruling (standing).** `regime_caveat` in the payload + a DEFERRED_ITEMS section: a high
  inflow rate is as regime-flattered as a low outflow rate ("the same coin landing heads because the market
  went up"). Never cite either absolute lane rate as evidence the Money Gradient works; never publish any
  market-ledger rate OR the census % externally while small_sample is true.
- **H1 — census cold-cache honesty.** `/monitor/degenerate-census` returns `available:false` (equity + the
  crypto branch) when the cache is cold, never a false 0 that would trip a reactivation trigger. **Live:**
  crypto reads `available:false, reason:"crypto_full cache cold — unknown, not 0"` ✓.
- **H2 — census tripwire made trendable.** D8-T2 now watches each LANE's `fully_degenerate_fraction`
  (`by_lane`), not the global `any_unmeasured` which is saturated ~299/300 by the permanent-frontier rule.
- **H3 — episode confirm-rate as a RANGE.** `report().episodes` serves `confirmed_range_pct [strict, any]`
  + strict/majority/any + an aggregation_note; we never headline the optimistic ANY-rule (a MAX operator
  that only inflates the winning lane). **Live:** covered episodes range [33.3, 50.0]%.
- **H4 — durable, fleet-global gate-reject counter.** New `market_gate_rejects` table + `_flush_gate_rejects`
  (flushed on any enrollment / sweep / report conn); a 0 with no history now reads as UNKNOWN, not "clean."
- **H7 — witness NULL is guarded by a TEST, not a comment.** `transfer/test_market_ledger_witness.py`
  (standalone, PASSES) asserts an absent `detection_score` stores NULL (never intensity×100) and a real
  witness stores verbatim; the old tautology no-op was deleted.
- **H5 / R2 — S1 reactivation = PRINCIPLE-OR-n (Expansionist resolution).** S1 reopens on EITHER a founder
  insider-parity ruling (routine congress net-sell = degenerate noise, same as insiders got 2026-06-26) OR
  n≥15 resolved **EPISODES** OR 0-for-10 EPISODES. Reopening = open the backtest, NOT ship. Keep enrolling
  the outflow lane UNCHANGED — never throttle the losing lane.
- **H6 — the scheduled reader (so a shelf doesn't become furniture).** New `/monitor/deferred-triggers`
  evaluates every DEFERRED_ITEMS trigger and returns FIRE/HOLD; the weekly improve-system audit reads it
  each run (checklist added). **Live.**
- **H8 — cold-start enforcement.** `.githooks/commit-msg` gained a `[cold-start-stated]` gate on
  universe-expansion-shaped commits; CLAUDE.md §16a got the enforcement note.

**⚠ OPEN — surfaced for founder ruling (flag-never-force):** `/monitor/deferred-triggers` shows
`D8_T2 fire:true` on first live read, because the covered lane's `fully_degenerate_fraction` is already 0.0
(large-caps essentially never have ALL positioning components degenerate). Per the rule a FIRE means
"open the D8 backtest for review," NOT ship — but the metric fires from the baseline state, so it reads more
like a mis-calibrated tripwire than a genuine maturation event. Recommend the next board pass either
recalibrate T2 (e.g. watch `unmeasured_fraction`/`insufficient_coverage` crossing a threshold) or the founder
rules whether to actually reopen D8's held-out backtest now. S1 correctly HOLDS at 0/3 episodes.

**RESOLVED same session — founder ruled "proceed with 1 and 2" (both):**
- **(1) H2b — T2 recalibrated (engine `af0e7c5`).** The tripwire now watches covered-lane
  **`unmeasured_fraction < 0.5`** (majority-measured — a metric that starts ~1.0 cold and FALLS as
  component history accrues), NOT `fully_degenerate_fraction` (~0 at baseline for large caps → fired
  on the first read). **Live: 0.524 → `fire: false` (HOLD)** — it will now fire only on a genuine
  conversion event. Updated in the census tripwire, `/monitor/deferred-triggers`, and DEFERRED_ITEMS T2.
- **(2) D8 backtest REOPENED for review** (`audits/ledger-research/D8_DEGENERATE_EXCLUSION_BACKTEST_REOPEN_2026-07-20.md`).
  Refreshed at current n: structural Δ=0 reconfirmed (enrollment still code-decoupled from mm; **0/12
  resolved rows pinned at detection**; blended 6/12=50%, inflow 6/7, outflow 0/5 — identical to 07-19);
  population breathed within cycle-sensitivity (mm→None 188→174, pin 189→175, all flow-neutral/
  unenrollable); covered-lane coverage **not yet crossed** (unmeasured_fraction 0.524 ≥ 0.5). **Verdict:
  the 07-19 defer-D8 conclusion STANDS** — no accuracy payoff by mechanism, exclusion still binds on
  absence (D7 display covers it); reopen ≠ ship. Live reopen paths unchanged: T1 (founder truth-ruling)
  or T2 (now correctly calibrated, HOLDS). Engine `af0e7c5`; origin `ebfaaf1`.

---

## Session 2026-06-26 (evening) — Signal Analysis · accuracy-ledger backlog + maturity · Apify audit + token rotation

- **Signal Analysis (per-item, enterprise-grade) — LIVE on web, shipped on mobile.** New held-out
  `signal_analysis.py` (imported by NOTHING in scoring): a REPRODUCIBLE, formula-confidential,
  measurement-only narrative per item — explains each metric conceptually + analyzes the finding from real
  scores + the accuracy-ledger track record (honest denominators), for trend / market / crypto. Engine:
  `POST /analysis/{kind}`. Web terminal: a "Signal Analysis" section in the trend/market/crypto rails
  (live, gh-pages). Mobile: trend (`signal/[id]`) + market (`risk/[key]`) screens (crypto N/A — no mobile
  crypto screen). Desktop inherits via the shared web build. Founder standard saved
  (`feedback-enterprise-analysis-standard`): explain metrics, hide the formula, every claim data-supported +
  defensible to hedge-fund counsel.
- **Accuracy-ledger backlog root-caused + the moat made honest.** The 909-pending / 2.1% *blended* rate is an
  ARTIFACT, not the product: (1) throughput starvation, (2) resolution survivorship bias (LAGGED resolves
  instantly; LED waits for a future breakout → stuck pending), (3) denominator pollution by ESTABLISHED topics
  (world cup etc. can only LAG). VERIFIED the ledger is **held-out** — `calibration_engine` /
  `signal_calibration_integration` have ZERO ledger refs; `calibration_agent` is read-only → the sweep cap
  **never touched a score**.
- **Maturity segmentation (held-out, display-only).** `generate_honest_report` segments resolved rows by
  `topic_maturity.maturity_class`, with a well-covered fallback to `velocity_scores` SUSTAINED-DAYS (distinct
  days scored ≥ `LEDGER_ESTABLISHED_MIN_DAYS`=14 → established). Headline = the EMERGING early-detection cohort;
  established/unknown reported too (nothing hidden). Exposed via `/accuracy/ledger` (`byMaturity`,
  `earlyDetectionHitRate`). Live: emerging 37 resolved · 1 led · 2.7% · 11d median lead (still early/maturing —
  the "don't publish a rate yet" guardrail stands).
- **Sweep runaway (caught + fixed).** Uncapping the sweep (8→300) + a one-off drain stampeded Apify — the
  Google-Trends-Scraper actor is SLOW + compute-heavy per topic (1–11 min/run, some fail); the earlier
  "$0.001/result cheap" read was WRONG (cost is per-run COMPUTE). Throttled to **`LEDGER_SWEEP_LIMIT=8`**
  (code default reverted 300→8 — footgun removed), added `_apify_sweep_budget_ok` guard (skips paid fetches
  within `LEDGER_APIFY_RESERVE_USD`=40 of the Apify cap so the sweep can't starve collection) + a manual
  `POST /accuracy/ledger/sweep`.
- **Apify usage audit.** CONFIRMED Apify pulls ONLY trend/attention — Google Trends realtime discovery
  (`easyapi/...`) + Google Trends curves (ledger sweep) + Reddit. Crypto + financial have ZERO Apify refs
  (FMP / Finviz / AV / FINRA / OFR / Databento). Found a realtime 2× overrun (the actor fires :00 AND :30 =
  8×/day vs the engine's single :30 cron) — likely a 2nd process on the old token; expected to resolve now the
  old key is deleted (confirm at the next 6h slot).
- **Apify token rotated** (old leaked in a tool output → rotated → old deleted; new set on engine v187,
  authenticating). Confirmed **NON-EXPIRING** (2026-06-26) — trend discovery + the ledger sweep are safe.
- **Cost Sentinel $700/mo total cap** (critical if exceeded, warn at 80%).
- **Accuracy-ledger PATIENCE WINDOW (365d) — founder decision.** The product detects dark matter BEFORE
  it reaches Google, and human attention can arrive MONTHS later — so judging a detection a miss at 90
  days unfairly condemns our own system before confirmation can arrive ("the big money is in the
  waiting" — Munger; refs reviewed). `accuracy_ledger_enhanced`: (1) timeout 90→365, computed LIVE from
  detection so it applies to the existing ~881 pending; (2) ASYMMETRIC lead window — backward stale-floor
  stays tight (30d, the −92d artifact), FORWARD lead up to 365d now counts as a genuine LED win (was
  wrongly excluded as LATE_REDETECTION); (3) dynamic curve length spans detection→now so a months-later
  breakout is visible. Held-out (no score impact); `param_version=calib-params-v2-patience365`. Documented
  in CLAUDE.md §14. Backlog insight: the 881 pending is a ROLLING working set — rows resolve at a Google
  breakout (trickle) or the (now 365-day) timeout; it self-resolves, it is NOT a throughput problem.

---

## Session 2026-06-26 — Finviz primary insider · Market-Signal "insider" reframe · Mainstream v2 · Crypto Money Gradient

Large multi-thread session; all shipped, health check clean at close.

- **Mainstream v2 (`MAINSTREAM_V2=1`, LIVE).** A few credible outlets were prematurely flipping a topic to
  "mainstream" and suppressing the early read. `dual_pathway.py`: credible media is a Dark-Matter TRIGGER until
  **≥5 INDEPENDENT outlets** corroborate or magnitude spikes. Syndication-collapse:
  `n_news_independent = min(distinct outlets, distinct normalized titles)` — defeats BOTH wire-syndication AND
  single-outlet spam. FIFA-validated (held-out `/research/mainstream-v2`): "world cup" stays mainstream (134
  outlets); thin "mexico world cup" (5→4 stories) demotes to a dark-matter trigger (det 38.5→70).
- **Finviz Elite — PRIMARY insider ($30/mo).** `finviz_data.py`: uncapped market-wide SEC Form-4 feed +
  per-ticker insider + screener. Primary via `av_dark_positioning._best_insider` (`FINVIZ_INSIDER=1`, AV→fallback).
  **INTEGRITY FIX (backtest-caught):** raw insider NET is degenerate (15/15 basket "outflow" — insiders structurally
  sell). The signal is insider **BUYING** (`signal=='accumulation'`, ≥$250K); routine selling = neutral, not bearish.
  Source hierarchy: Finviz #1 insider+equity-market · Databento #1 price-truth+microstructure · AV fallback/13F ·
  FMP crypto+deep-fundamentals. Finviz crypto is display-only.
- **Market Signal de-Congress → "insider" (all platforms).** Reworded `_market_analysis` + `ai_grade` prompt +
  `_interpret_movement` + explainer + Methodology. Labels: "Positioning Concentration" → **Insider Tracking**;
  "Dark Positioning" (macro OFR funding) → **Macro Positioning** (kept accurate — NOT insider); Diffusion stage →
  Insider Tracking. Tier **"BUILDING" → "MODERATE"** (engine + every frontend color/filter/legend). SOURCES (§17):
  added the score-driving FINRA/OFR/FMP/13F that `source_provenance` (signals-only) omitted. Congress DATA (Quiver)
  is still a D input — only the DISPLAY drops the name.
- **Crypto Money Gradient — LIVE (`CRYPTO_SIGNAL=1`).** Coin-native Money Gradient: D = informed money via
  crypto-EXPOSURE proxies (spot-ETF 13F + MSTR/COIN insider via Finviz; no on-chain — proxy v1); M = FMP coin price.
  12 coins. `crypto_signals.py` + `crypto_money_gradient.py` (baseline-relative dual score, reuses
  market_signal_engine store under `crypto:BTC`) + `/crypto[/{coin}]`. Web: master/detail `/crypto` page +
  CryptoRail (mirrors the stock detail) + nav (under Market Signal, above Grade) + **Dashboard tile**. **P3 —
  `crypto_accuracy_ledger.py`**: realized COIN price direction, 8%/45d, no-lookahead — the 3rd distinct ledger +
  "Crypto · Coin" toggle. **Perf gotchas:** /crypto MUST serve from the PREWARM cache (`crypto_full`); live roster
  uses FAST Finviz-only DM (`CRYPTO_FULL_DM=0`) — AV 13F's 13s/call throttle hung the page; roster now ~10s.
- **FMP upgrade** to $20 Starter (300/min, crypto+forex) → crypto prices reliable (free-tier 429s gone).
- **Health check + docs (this entry).** Services up; the only warns were Data Subscriptions + Cost Sentinel not
  accounting for the new sources — FIXED (registered Finviz/Quiver/FMP/Databento/AV-research; set
  `COST_FINVIZ_USD=30`/`COST_QUIVER_USD=30`/`COST_FMP_USD=20`). Quarantine 0; ledgers forward-only (no lost data);
  catch-all STABLE (no leak). Updated CLAUDE.md §15+footer, DATA_BUILDING_BLOCKS §1/§5, this log, `/nowtrendin2.0`.

---

## Session 2026-06-25c — market-data sources: Databento (live) + Alpha Vantage Dark-Matter (held-out)

Researched two founder-provided sources via §16; both keys stored as Heroku env (rotate if transcript shared).

- **Databento — LIVE (accuracy-ledger price verification).** Exchange-direct market data; §16-cleared as a
  REFEREE (referee, never feeds a score → no backtest gate). `databento_price.historical_close()` (EQUS.SUMMARY
  ohlcv-1d, adapter: ns ts→ISO date, 1e-9 fixed-point→float) = same `{date: close}` interface as FMP.
  `market_accuracy_ledger._price_fetch`: **Databento PRIMARY** (no rate cap, ~free) + **FMP cross-check/fallback**
  (`_cross_check` logs >1% divergence). Tested: databento==FMP closes agree EXACTLY (294.3=294.3). `DATABENTO_API_KEY`
  set; deployed.
- **Alpha Vantage Dark-Matter — HELD-OUT (`av_dark_positioning.py`, imported by NOTHING in scoring).** AV uniquely
  provides what Databento canNOT: **insider Form-4** (INSIDER_TRANSACTIONS) + **institutional 13F by ticker**
  (INSTITUTIONAL_HOLDINGS, with change direction). Filters ≥$250K + net direction. Live research: AAPL insider
  −$152M/18 sells (outflow) + institutional net +1.55B shares (inflow) → combined "mixed". Reads
  `ALPHAVANTAGE_RESEARCH_KEY` (new key; production `ALPHAVANTAGE_API_KEY`/NEWS_SENTIMENT untouched). **NOT in any
  score yet** — research → backtest-before-ship → then integrate into `positioning_intel` (alongside congress + 13F).
  Free tier = 5/min · 25/day · ≤1/sec → built-in 13s throttle; production at scale needs caching or premium.
- **Cost/decision:** KEEP both — complementary. Databento = prices/microstructure only (no filings/news);
  Alpha Vantage uniquely = insider/13F/news. Don't cancel AV. Databento ~free for the ledger. Databento microstructure
  (block trades / dark-pool / order imbalance) is a viable **phase-2** Dark-Matter angle (own research+backtest).

---

## Session 2026-06-25b — N component accuracy fix (platform tracking, NOT user demand)

Founder flagged the N-component copy as inaccurate ("how often Now TrendIn users asked the engine
about this topic"). **Verified in the engine:** N (`nowtrendin_score`) is computed purely from
`topic_queries`, and `_log_topic_query` fires **every time a topic is SURFACED in an API result**
(the `/scores` feed, `/anomalies`, `/trending`), an on-demand `/scores/{topic}` query, or a grade.
So N = platform-tracking / appearance frequency — NOT a user-demand claim. Founder was right.

Corrected consistently across all 3 platforms + the engine source comments:
- **"Community Demand" → "Platform Indicator"**; "Now TrendIn user demand" → "Now TrendIn platform
  tracking" (web Screener breakdown + its bar-color key).
- N description (Screener, mobile signal detail, Grade, both Methodology pages, GradeTool): "how often
  users asked / institutional curiosity" → "how often this topic is triggered + surfaced as a tracked
  topic across the platform (feeds, queries, grades) — a platform-internal read no public source has."
- "DEMAND-INCLUSIVE" → "N-INCLUSIVE"; demand-driven warnings + empty states reworded.
- Engine (comment/docstring only, zero runtime change — lands next engine deploy): `compute_nowtrendin_score`
  docstring + `velocity_scores`/`topic_queries` DDL comments.
- Unchanged: N stays a SEPARATE signal, DELIBERATELY EXCLUDED from the Gradient (no feedback loop).
- Web → gh-pages (`00ed5c1`); mobile on Metro reload; desktop inherits. Build + tsc clean.

---

## Session 2026-06-25a — Market Signal v2.0 LIVE: market-ledger view, parity, validated + flag flipped ON

Completed the founder's "proceed with 1-3" (validate / market-ledger view / parity), in the order
2→3→1 so the flip exercised the whole surface.

- **Item 2 — market-ledger view (the visible "two ledgers" proof):** engine `market_accuracy_ledger.detail()`
  + `GET /market/accuracy/detail`; web terminal **Accuracy Ledger** gained an **Attention / Money** toggle
  (Money mode = distinct-ground-truth banner, money stat strip, per-detection table); mobile
  `profile/accuracy` got the same toggle. Added a `pending` (in-flight) count to `/market/accuracy`.
- **Item 3 — parity:** Dashboard `MKT_RANK` label Detection→Money Movement; Methodology gained
  "The Money Gradient" + a reworked "The Accuracy Ledgers" (two ledgers, two ground truths).
- **Item 1 — VALIDATED + FLAG FLIPPED ON (`MARKET_SIGNAL_V2=1`, engine v155):** forced a
  `/risk/collect` (collect + `score_all_risks`) under the flag; at t=180s, **8/8 rows scored
  `model_version=v2`**, **7 money detections recorded** (pending). Sanity confirmed live:
  - scores in-range (0 out-of-range); directional signals on the right names — **Nvidia MM 68 / MC 25 /
    outflow**, **Apple 70 / 27 / outflow**, **JPMorgan 54 / 27 / outflow** (covered megacaps with
    congress/insider/13F); macro themes + micro-caps read **neutral** (no positioning data) — correct.
  - enriched interpretation live (Money Movement + flow + Market Confirmation + Leverage walk),
    measurement-not-advice language intact.
  - `/market/accuracy` pending=7, resolved=0 (expected — fresh detections resolve once price moves
    ±5% or the 60-day window elapses; the market sweep runs on the ledger cadence).
- **Now live for all users:** the Money Gradient (Money Movement / Market Confirmation / flow /
  leverage facts) across web/desktop/mobile + both accuracy ledgers. Reversible: `MARKET_SIGNAL_V2=0`.
- Observation to watch: covered megacaps currently all read **outflow** (net congress/insider/13F
  selling — plausible for megacaps; the ledger will record whether these reads were right).

---

## Session 2026-06-24f — Market Signal v2.0 phases 3-4: distinct market ledger (price-validated) + platform relabel

**Founder correction (key):** Google Trends does NOT validate market signals — that's the ground
truth for the ATTENTION ledger. A money signal is validated by **realized EOD price DIRECTION**.
So the Money Gradient gets its **OWN** ledger, distinct from the Trends ledger.

- **Phase 3 — distinct Market-Signal Accuracy Ledger** (`market_accuracy_ledger.py`, NEW). Ground
  truth = realized EOD close direction (FMP `historical_close`). `record_market_detection`
  (flow+intensity, dedup = one open per ticker+flow, intensity floor, neutral rejected) →
  `sweep_market_pending` resolves **CONFIRMED** (dir match) / **NOT_CONFIRMED** (opposite) /
  **NO_MOVE** (flat by 60d) + lead time. Honest denominator; NO LOOKAHEAD (post-detection closes
  only). Wired flag-gated: record at the market scoring site, sweep on the ledger cadence, init at
  startup, `GET /market/accuracy` + `POST /market/accuracy/sweep`. Attention ledger byte-identical.
  Verified: synthetic verdicts correct; live `/market/accuracy` returns the honest report (empty,
  flag off). **`FMP_API_KEY` set on the engine.**
- **Fixed a pre-existing latent bug:** the startup aux-table `ALTER TABLE ... ADD COLUMN` aborted the
  PG txn (DuplicateColumn) with no rollback → every later DDL ("current transaction is aborted") was
  skipped, including the ledger inits. Rolled back the aborted txn so the block completes.
- **Language purge (market/risk, LIVE):** served `risk_action` ("Act now"/"Begin hedging") →
  factual movement statements; Risk Gradient header, FP labels, interpretation strings, OFR,
  gravitational docstring all reframed to movement+ledger language.
- **Phase 4 — platform relabel (payload-gated, inert until flag flips):** web terminal
  (`MarketSignal.tsx`) + mobile (`risk/[key].tsx`) show **Money Movement / Market Confirmation** +
  the factual **flow** badge (▲ inflow / ▼ outflow) + v2 disclaimer when the engine serves a v2
  payload; v1 (Detection/Confidence) when off. Web deployed to gh-pages; desktop inherits the web
  build; mobile ships on Metro reload. Build clean (web vite + mobile tsc).
- **Remaining (recommended next):** a market-accuracy-ledger **VIEW** on each platform (show
  `/market/accuracy` distinct from the Trends Accuracy Ledger view); minor Dashboard `MKT_RANK`
  sort label; methodology-page mention of the Money Gradient + market ledger; then validate v2
  output end-to-end with a small recorded sample and **flip `MARKET_SIGNAL_V2=1`**.
- Out-of-scope finding (flagged): the ATTENTION engine has a served field named `what_to_do_action`
  (values descriptive, not buy/sell) — the field *name* reads as advice; worth a later consistency pass.
- **Market AI descriptor (founder request, BOTH descriptors):** the market description now analyzes
  **Money Movement + Market Confirmation + Leverage** from our score data. (1) Reproducible:
  `_market_analysis` / `_append_market_analysis` append a deterministic three-dimension walk
  (money score + filing flow, confirmation score, leverage-health fact) to the market interpretation
  at both call sites — runs v1+v2, skips calibrating/insufficient. (2) LLM: `ai_grade.market_analysis`
  — a guardrailed Claude narrative anchored ONLY to our scores (no web), 12h-cached per instrument,
  budget-gated ($20/mo cap), opt-out `MARKET_AI_ANALYSIS=0`, with a banned-word backstop
  (buy/sell/undervalued/should/… → reject) so it can't drift into advice; attached via
  `grade_agent._attach_market` as `result.market_analysis`. Grade views (web + mobile) surface it +
  v2 labels. Engine deployed; web→gh-pages; mobile on Metro reload. Forward-only: enriched overviews
  populate as market rows re-score (persisted serve path).

---

## Session 2026-06-24e — Market Signal v2.0 (the Money Gradient) — phases 1-2 shipped flag-OFF

Founder confirmed the direction: the platform MEASURES movement (attention + money) + states leverage
FACTS — no prediction/advice — but signals MAY be precursors, and the **Accuracy Ledger** judges
(factually, over time) whether they led. Congress = **Dark Matter** (insider-informed, early), NOT
lagging. Spec: **MARKET_SIGNAL_V2.md**. All flag-gated behind `MARKET_SIGNAL_V2` (default OFF).

- **Phase 1** — quality finance YouTube (Meet Kevin, The Compound) reclassified from Stage-5 "retail
  amplify" (lagging) → **Dark Matter** (stage 2, early/informed). `QUALITY_ANALYST_CHANNELS`.
- **Phase 2** — **Money Gradient scoring** (`market_signal_engine`): the SAME baseline-relative
  components reorganized into **MONEY MOVEMENT (D** = smart-money 13F/insider/shorts + congress +
  quality-analyst, the early/informed flow**)** vs **MARKET CONFIRMATION (M** = fundamentals +
  momentum + diffusion, broad/economic**)**. `_interpret_movement()` replaces alpha/early-warning
  language with movement+ledger wording ("a measurement, not a recommendation; the ledger judges
  whether it led"). Output gains `model_version`, `money_movement`, `market_confirmation`, `flow`
  (inflow/outflow), `leverage_facts`. MARKET_SIGNAL_V2 implies the congress/13F blend (D inputs).
  **Verified live: flag OFF = v1 byte-identical (no v2 leak); flag ON = Money Gradient.**
- **Remaining:** Phase 3 — money detections → Accuracy Ledger + full alpha/advice language purge
  (incl. the Risk Gradient's "before it's priced in / is the alpha" header). Phase 4 — propagate to
  all 3 platforms (web→desktop, mobile): relabel Detection/Confidence → Money Movement / Market
  Confirmation, surface flow + leverage facts, purge advice language. Then validate + flip the flag.

---

## Session 2026-06-24d — Dark-Positioning integration (SEC 13F + Congress → Market Signal, flag-OFF)

Integrated the two held-out positioning sources into Market Signal's smart-money component —
**built, wired, verified, and shipped INERT behind `DARK_POSITIONING_V2` (default off)**, pending
the predictive backtest before it moves a live score.

- **`positioning_intel.py`** (new): inverts the held-out 13F holdings (curated funds) + Congress
  trades into ONE per-TICKER signal — `signal_for(ticker, name)` → `positioning_signal` 0-1 +
  net `direction`. 13F matched by issuer NAME (`_norm_name`), Congress by ticker. Cached (daily).
  Non-circular (external SEC/Congress filings only).
- **Wiring (flag-gated, default OFF):** `market_signal_engine.assemble_market_components` blends
  the signal into `positioning_concentration` (`DARK_POS_WEIGHT=0.4`) ONLY when the flag is on AND
  the ticker has 13F/congress activity. `financial_risk_gradient` attaches
  `payload['dark_positioning_intel']` at both market-signal call sites when on (off = `positioning_intel`
  never imported → held-out preserved, zero overhead). **Verified: flag off = byte-identical
  (`pos_conc` 0.333 unchanged, no `dark_positioning_intel` in the live feed); on+signal=1.0 → 0.600;
  on+no-data → base unchanged.**
- **`GET /research/dark-positioning`** (internal-key) = the review surface — the EXACT signal that
  blends in. Live: 17 ranked tickers — AAPL/NVDA/GOOGL sig=1.00 net-selling (6-8 funds + 9-13
  congress members), AMZN 0.95 net-buying, down to LMT/MS at 0.
- **Sanity backtest PASSES** (discriminates 0-1; known cases correct; direction-aware; non-circular).
  **NOT live** — `DARK_POSITIONING_V2=0` on Heroku. To activate: run the PREDICTIVE backtest (does
  blending IMPROVE, not just change, the Market Signal — needs a historical signal×forward-return
  harness using the Congress `/bulk` history + 13F snapshots), then `heroku config:set
  DARK_POSITIONING_V2=1`. The held-out modules' "imported by nothing in scoring" holds while off.
- **PREDICTIVE BACKTEST — DONE. VERDICT: not predictive → flag STAYS OFF.** `dark_positioning_backtest.py`
  (held-out, NO-lookahead: signal as-of T uses only Congress trades FILED ≤ T; forward returns from
  Yahoo, independent of QuiverQuant). Swept 4 horizons × net/buy-only, ~1,900 obs each, 35 liquid
  large-caps, 2021-2026. Long-short spread **NEGATIVE at every horizon** (21d −0.03 / 63d −0.12 /
  126d −0.64 / 252d −0.47%; net-sell slightly outperforms net-buy), IC ≈0 (−0.039..+0.023), buy
  hit-rate ~51-53% (coin-flip), buy-only worse. Forward returns ≈identical across cohorts — they track
  market drift, not the signal. Mechanism: by the public FILED date the edge in liquid names is gone
  (30-45d disclosure lag); 13F is staler → same prior. **DO NOT flip the flag** — blending adds noise,
  not alpha. Signal stays valid as DISPLAY/transparency context (real + interesting), not a predictive
  score input. Backtest-before-ship worked exactly as intended.

---

## Session 2026-06-24c — Source Onboarding Protocol (hard rule + gotcha) + SEC fund-13F (held-out)

**SOURCE ONBOARDING PROTOCOL (§16 hard rule, founder-mandated).** Before linking ANY media/data
source, 5 gates pass IN ORDER: **TYPE → ENGINE → FORMAT → CURRENCY+ACCESS → TEST→LINK→DEPLOY**
(score-affecting ⇒ backtest-before-ship). Documented in CLAUDE.md §16, DATA_BUILDING_BLOCKS B1a
(Source Watchdog owns), AGENT_CHARTER GOTCHA G-SRC + fleet table, `/data-watchdog` skill, and
memory `feedback-source-onboarding-protocol`. **Enforced by `.githooks/commit-msg`** (a "gotcha"):
detects a source-shaped commit (feed URL / new collector / `COLLECTOR_EXPECTATIONS` entry in the
`transfer/*` collectors) and BLOCKS unless the message asserts `[source-onboarded]`. Tracked in
`.githooks/` with `.gitattributes` forcing LF (CRLF broke the bash parse); install once:
`git config core.hooksPath .githooks`. Verified: blocks without marker, allows with it, ignores
non-source commits.

**SEC fund-13F institutional positioning — built HELD-OUT (research-before-integrate).**
`transfer/sec_13f_research.py` — imported by NOTHING in scoring (like `referee_wikipedia`).
Onboarded through all 5 gates. Curated `FUND_CIKS` (Berkshire, Bridgewater, RenTech, BlackRock,
Vanguard, State Street, Citadel, Two Sigma, Tiger Global, Soros). `latest_13f(cik)` → SEC
submissions API → 13F-HR info-table XML → namespace-agnostic parse → per-CUSIP-aggregated holdings
+ total value + top-10 concentration. **`GET /research/13f?fund=<name|cik|all>`** (internal-key) =
the review surface. **Verified live from the engine** (SEC doesn't block Heroku IPs): Berkshire
Q1-2026 — 29 positions, $263B, Apple 22% / Amex 17% / Coca-Cola 12% (matches the known portfolio);
Bridgewater 993 pos / $22B; BlackRock 5230 pos / $4.4T; Citadel 6733 pos / $618B. Format-gate fix:
HTML entities decoded (S&amp;P → S&P). **NOT integrated into `positioning_concentration` yet —
founder to review `/research/13f`, then backtest-before-ship.**
Research findings to note: **BlackRock CIK (0001364742) returns a 2024-Q2 13F** (others are
2026-Q1) — BlackRock files under multiple entities; that CIK needs verification before use.

**CIK curation (B) — done.** Verified all 10: 8 hedge funds return current Q1-2026 13F-HR.
FINDING: the index/asset-management GIANTS (BlackRock, increasingly Vanguard) file 13F-**NT**
*notices* and split holdings across sub-advisor entities, so no single CIK has their full book.
**Dropped BlackRock** (0001364742 = "BlackRock Finance Inc", last HR 2024-Q2; no active consolidated
HR found). Kept Vanguard at its last HR (Q4-2025; it filed 13F-NT for Q1-2026). 9 funds remain, all
returning usable holdings.

**Congressional-trading sources — 5-gate review (NONE onboarded; the rule did its job).** Applied
§16 to the 4 given URLs — all FAIL as provided: House & Senate **Stock Watcher** S3 JSON →
**403 AccessDenied** (buckets no longer public, all paths/hostnames); **CapitolTrades** /buzz →
**429** + HTML (not a feed); **QuiverQuant** /congresstrading → HTTP 200 but a 2.2 MB **HTML page**
(structured data is behind their paid API). The SIGNAL is valuable, but ENGINE routing is
**Market Signal "Dark Positioning"** (positioning data, alongside SEC 13F + insider Form-4), NOT a
blog/Dark-Matter *trend* feed. VIABLE primary path (verified live): the OFFICIAL **House Clerk** FD
dataset (`disclosures-clerk.house.gov/public_disc/financial-pdfs/{YEAR}FD.zip` → tab-delimited index,
FilingType "P" = PTR stock trades; 1,230 filings in 2026) + **Senate EFD** (efdsearch.senate.gov) —
free + durable, but transaction details are in per-filing PDFs (parsing effort, like the stock-watcher
project did before its bucket went private). Recommend a held-out collector against the official
sources (or QuiverQuant's paid API) — verify + backtest before integration.

**RESOLVED via QuiverQuant API (founder provided a token).** Gate-4 finding: the structured data
the HTML page hid is at `api.quiverquant.com` — `/beta/live/congresstrading` returns clean JSON
(works token-less), `/beta/bulk/congresstrading` (Bearer token) = **113k+ rows** current to the day,
20 fields incl. ticker/transaction/size/party/chamber/excess_return. **All 5 §16 gates PASS.** Built
**HELD-OUT** `transfer/quiver_research.py` (`congress_recent()` → recent trades + per-ticker
concentration) + **`GET /research/congress`** (internal-key, the review surface). Token stored as the
Heroku env var **QUIVER_API_KEY** (set 2026-06-24, v147; NOT committed). Verified live: 1000 recent
trades, 401 tickers; members net-selling mega-cap tech (AAPL −7, NVDA −7), net-buying LLY +4 / AMZN +2;
Pelosi buying UBER+INTC. ENGINE = Market Signal **Dark Positioning** (alongside SEC 13F). **NOT wired
into positioning_concentration** — review `/research/congress`, then backtest (the `/bulk` feed is the
historical input) before integration. NOTE: QuiverQuant also exposes insider/lobbying/gov-contracts/WSB
datasets — each would need its own gate review. Security: token was shared in chat → rotate if the
transcript is ever exposed.

---

## Session 2026-06-24b — Founder 10-day QA + source cleanup + new-source review

**Founder QA review (2026-06-10 features):** the pasted runbook targeted the FROZEN 1.0 engine
(nowtrendin-e62…) — ran every check against **v2** instead. All 4 features verified live + working:
Signal Convergence (`/convergence`, sensible CONFLICTING/MIXED verdicts, warming_up cleared at 7
snapshots), Dark Matter recalibration (`100*ratio^0.7`, D spans 0–49, **no clustering at 65**),
news provenance tiering (per cycle: ~33–38 promoted dark-matter, ~118–149 mainstream, quarantine
firing), reputable allowlist (~80 publishers). The prior "/usage doesn't track news aggregators"
flag was a **measurement artifact** (truncated 900-char output) — all aggregators ARE tracked.

**Source cleanup (engine deployed):**
- **HackerNews was DOWN** (0 signals) — `hn.algolia.com/api/v1/search` now returns 0 for
  `points>50` numericFilters (verified live; `/search_by_date` returns results with the same
  filters). Switched the collector to `/search_by_date`. Moat source FIXED, not removed.
- **yahoo_finance REMOVED** — RapidAPI 429 every cycle (quota exhausted), 0 signals, ~600 wasted
  calls/30d. Gated both collectors behind `YAHOO_FINANCE_ENABLED=0` (default off) + removed its
  collector_health expectation. Reversible.
- **newsapi_ai ("newai") kept** — it IS producing (100 art/cycle → 573–635 signals); not dead.
- **QA runbook repointed:** `monitoring/integrity-check.ps1` `$BASE` + README were checking the
  frozen 1.0 engine — corrected to v2.

**New Market-Signal sources reviewed (tested before wiring — none shipped):**
- **Mises Institute Literature** (mises.org/rss/library): **REJECT** — HTTP 404 (dead URL) AND it's
  classic economic *literature* (historical books), not current signal.
- **NBER** (real URL `back.nber.org/rss/new.xml`, the given one 301-redirects): works, but academic
  paper titles **extract poorly** (fail the quality gate; sub-phrases are noise like "times
  geopolitical fragmentation"). It's also a macro-research/TREND source, NOT Market-Signal
  positioning. **Recommend against wiring as-is** — would need a research-concept extractor first.
- **SEC EDGAR 13F** (Berkshire CIK atom feed): **HTTP 200, 40 real 13F filings — the strong fit.**
  SEC EDGAR is already a live collector (`sec_edgar`, ~334 sig/cycle, does Form 4 / 8‑K / 13F for
  watchlist COMPANIES). The enhancement = track specific mega-cap FUND 13F-HRs (Berkshire et al.)
  to see where institutions move billions → feeds `positioning_concentration`. Real win, but
  score-affecting (needs a validated build + 13F-HR holdings-table parsing) — recommended, not shipped.

---

## Session 2026-06-24a — Overbroad "news" fixed + quarantine review loop + log corrections

### The "news" category was 77% UNCLASSIFIED, mislabeled (display-only fix, big drain)
- **Root cause:** `topic_categories.classify_topic` returned **'news' on NO lexicon match** —
  but 'news' has no lexicon of its own (real news/geopolitics matches `current_events`). So
  the 77% "news" catch-all was really 77% *unclassified*, wearing a News label.
- **Fix 1a:** no-match fallback → honest **'general'** (matches the module's own documented
  intent + the empty-blob case). 'news' as a produced category is now ~0.
- **Fix 1b (the real drain):** **context classification** — a background map (`_CONTEXT_CAT`)
  classifies each topic against its OWN signal **headlines** (`raw_signals.title`), so a bare
  entity with no lexicon hit ("lilly"→health, "britain"→politics, "wembanyama"→sports) resolves
  from real source text. Conservative 0.35 confidence floor; catch-all results dropped.
  `_category_for` now layers **situation(event) → context(headline) → bare lexicon → general**.
- **Verified live: catch-all 77.0% → 55.7% (−21.2 pts)**, 63,450 topics context-classified,
  883/4000 reclassified — spread PROPORTIONALLY across tech/politics/sports/business/health
  (healthy, not dumped). Display-only: scoring method + corroboration gate still use the bare
  lexicon → no score impact, no circularity. Web terminal chips are data-driven (`/categories`)
  so "General" appears + "News" drops automatically. **Mobile chip row (`frontend/lib/signals.ts`
  CATEGORY_DEFS) is hardcoded with a 'news' chip — small parity follow-up (swap to 'general').**
- **Bug caught + fixed:** `/categories` had 500'd since v133 — audit #1 changed its count to
  `_category_for(topic_key, …)` but the SELECT only returned `topic_display` (KeyError). Added
  `topic_key` to the SELECT. (Web-terminal category chips were silently broken until now.)

### Quarantine review loop — the date queue had no exit path (now closed)
- `format_review_queue` (unparseable dates → human review) was WRITE-ONLY: `pending_reviews()`
  + `resolve_review()` existed but **no endpoint exposed them**, and **`gate_date` never
  consulted `format_rules`** (so the "learned rule auto-applies" the docstring promised was
  never wired). Queue currently empty (0), but the loop was broken.
- **Fix 2a:** `gate_date` consults `format_rules` BEFORE quarantining (auto-applies a
  human-approved normalization to identical future inputs). **Fix 2b:** `GET /quarantine/dates`
  (list pending + candidates) + `POST /quarantine/dates/resolve` (human picks chosen_value,
  validated canonical, learns a rule). Flag-never-force.

### SESSION_LOG corrections (per external review of the log)
- **Live URLs table:** the Engine row pointed to the FROZEN 1.0 app + the `git push heroku
  HEAD:main` command that caused the 2026-06-19 accidental 1.0 deploy. Corrected to the v2
  engine + `heroku-v2engine` remote; 1.0 row relabeled "FROZEN, DO NOT DEPLOY".
- Forward-referenced the stale corroboration "WORSENING +230 / 10,488 leaks" alarm → its
  2026-06-23f correction (artifact; true leak ≈5).
- Verified live: **GUARDIAN_API_KEY still missing** on the engine (deliberate 06-20 deferral, but
  every score is computed without that mainstream signal — user decision to set it or not).
  SECRET_KEY is **present** (the review's "insecure default" claim is stale). Apify/Dev.to set;
  Reddit deferred. `DB_DATA_DICTIONARY.md` confirmed stale.

### Founder decisions actioned (2026-06-24)
- **Guardian + Reddit:** proceed WITHOUT both (deliberate; not gaps to chase).
- **Retention → 365 days canonical** (resolves the long-standing 90-vs-365 ambiguity). All
  `_prune_velocity_scores`/`prune_velocity_scores` defaults + env fallbacks
  (`VELOCITY_RETENTION_DAYS`/`VELOCITY_KEEP_DAYS`) 90→365; CLAUDE.md §13 + DATA_BUILDING_BLOCKS
  + all retention comments updated. ⚠ **STORAGE:** ~5.4GB@90d → ~22GB@365d **exceeds the 10GB
  Essential-1 Postgres plan** — a larger plan (or downsample-after-90d) is needed before the
  year-tail fills in (no immediate effect — app is ~3 months old). Flagged in-code at the prune site.
- **3-platform UI parity (Market lane axis + category chips):** web terminal already had lanes +
  data-driven chips; desktop = Tauri over the web build (inherits). **Mobile** brought in line:
  `CONTENT_CATEGORIES` news→general; `MARKET_LANES` (All / Covered / Halted·micro-cap / Macro)
  mirrors the web `LANE_FILTERS` exactly → lane chip row on the market-category view, lane subline
  + LTD-DATA/"positioning N/A" on `RiskCard`, N/A components + macro caveat in the risk detail.
  `RiskScore.marketGradient` threaded with lane/dataCoverage/naComponents. tsc clean; ships on next
  Metro reload/EAS build. **DB_DATA_DICTIONARY.md regenerated from the live schema** (see that file).

---

## Session 2026-06-23f — Catch-all audit closeout (items #1–#3), all display/forward-only

Completed the three open catch-all audit items. **Every change is display-only,
forward-only, or monitoring-only — no `velocity_scores` deleted (90-day retention),
no scoring input altered, no circularity.** Engine deployed v133→v138.

### #1 — Situation→category routing (drains the catch-all by CONTEXT, not bare word)
- **`situation_clustering.category_map_from_db()`** — builds a `{topic_key: category}`
  override from the held-out clustering: each situation's SPECIFIC category (skipping
  news/general) applied to its members, largest-situation-wins. A context-dependent
  entity is routed by its SITUATION (hormuz in an Iran situation → current_events) —
  what the bare-word lexicon structurally cannot do.
- Engine: `_SITUATION_CAT` cache + `_situation_category_loop` daemon (30 min,
  `SITUATION_CATEGORY_ENABLED`) + **`_category_for(topic_key, display)`** applied at the
  SERVE sites only (detail, list feeds, mobile feed, category-chip counts). **NOT** at the
  scoring method or the corroboration-floor gate `_passes_corroboration` — keeps the
  situation layer (built FROM scored signals) out of scoring ADMISSION → no circularity.
- `/audit/topics` now reports raw vs routed catch-all %. **Honest measured drain: ~0.6 pts
  (≈25 topics).** Small because the catch-all is **100% "news"** (the lexicon FALLBACK) and
  is dominated by genuinely-news topics + the long tail that forms no situation; forcing the
  rest into specific buckets would be label inflation (integrity-forbidden). The router
  rescues only the corroborated context-entities, and scales as more situations form.

### #2 — Corroboration-floor "leak" was a MEASUREMENT ARTIFACT, not a floor failure
- The Catch-All Auditor reported **10,488 single-source leaks / "floor disabled"**. Root
  cause: it checked corroboration over the last 72 h of `topic_signals` but compared it to
  the LATEST score of EVERY topic — dormant topics' signals had aged out (false nsrc=0) —
  AND it omitted two of the floor's own exemptions (high-magnitude, window alignment).
- Rebuilt the metric to replicate `_passes_corroboration` EXACTLY (expert-tier + tracked +
  `MAX(engagement_raw) ≥ HIGH_MAGNITUDE_ENG`) and to align windows (corroboration widened to
  score 72 h + recent 24 h = 96 h ⊇ every recent topic's scoring window). Split into
  `single_source_catchall_leak` (current, scored ≤24 h) vs `dormant_catchall_pile` (aged,
  retained). **TRUE current leak = 5 (≈ 0); dormant pile ≈ 8,500. The floor is healthy.**
  The "WORSENING +230" in the old summary was stale — live trend is IMPROVING/STABLE.

### #3 — 539 tracked detections stuck in catch-all — fixed at the source, 3 ways
- **Lexicon:** unambiguous tech terms (javascript, typescript, wwdc, chatbot/s, webassembly)
  added to `topic_categories` technology → reclassify out of catch-all (verified gone from the
  tracked-in-catchall examples). Bare geographies (britain, canada) deliberately NOT added —
  routed by the situation layer (#1).
- **`record_detection` sink-hardened** with the shared quality gate (forward-only, fail-open):
  fragment non-topics ("sunday afternoon", "york for months") can no longer be TRACKED.
- **`sweep_pending`** resolves legacy non-quality pendings as `excluded_nonquality`
  (non-deleting, auditable) instead of letting them time out as FALSE_POSITIVE — a non-topic
  is not a failed prediction, so this protects the Accuracy Ledger's honest denominator (the
  moat). Auditor's misclassified count now skips quarantined rows.

### Tier 1 Market Signal triage — DONE (engine v139 + gh-pages)
The Market Signal universe mixed three instrument types one template can't fairly serve,
producing ~86% "insufficient coverage" — much of it a CATEGORY ERROR, not a real gap.
Verified live: **94 halted/micro-cap · 15 covered · 3 macro themes**.
- **Coverage LANE** (`market_signal_engine.compute_market_signal` gains `lane` +
  `na_components`; `financial_risk_gradient._market_lane()` types each item from the existing
  `_risk_maturity`): covered / halted_microcap / macro_theme.
- **Macro themes** (recession, inflation — no ticker) mark `positioning_concentration` +
  `fundamental_confirmation` STRUCTURALLY N/A: excluded from BOTH the weighted score
  (renormalized) AND the coverage denominator — not a data gap, a category error to ask for.
  Result: inflation/recession moved insufficient→partial; **covered lane = 7 full / 8 partial /
  0 insufficient** (the real signal, no longer buried under halt micro-caps).
- Default path (lane=covered, no N/A) is byte-identical — no Gradient/Market score input changed.
- **Web terminal**: Lane chip axis (Covered N / Halted·micro-cap N / Macro themes N) above the
  Tier chips; row subline + detail-rail lane chip; macro-theme N/A note; Market Factors render
  N/A components as greyed "n/a". `MarketGradient` type extended. Build clean, deployed gh-pages.

### Next
- (Optional) extend the lane axis to the mobile Market tab for 3-platform parity.

---

## Session 2026-06-23e — Situation model (topics-not-words) + corpus quality gate

### Topics-not-words: the situation layer (held-out, READ-ONLY — affects no score)
- **Problem (founder):** the engine tracks WORD fragments ("hormuz", "japan"), not SITUATIONS.
  "japan" is one over-aggregated blob smearing the Belgium royal visit + BOJ rate hike +
  World Cup, while "bank japan" fragments off and "japan vs Sweden" is missing.
- **`situation_clustering.py`** — co-occurrence (topic_signals.signal_id, already recorded) →
  Jaccard-normalized edges → **hub-aware** clustering: detect a hub entity ("japan") that
  bridges distinct situations, cluster WITHOUT it, re-attach it as a shared searchable anchor.
  Proven: "japan" → 3 separate situations (belgium / bank-of-japan / world-cup). Situation
  first_seen = earliest member first-seen (reconciles word-level discovery undercount).
- **`/situations/preview`** (held-out, internal-key, ~10min cache) — runs it on the REAL
  corpus. `SITUATION_MODEL.md` = the full recommended solution (entity→situation→fragment;
  data model + DB-redundancy; search/disambiguation; situation-level scoring 🔒-gated; filter+
  sort taxonomy; the **Situation Contract** = one protocol for every agent + scorer; rollout).

### Corpus quality gate (the situation layer exposed it; fixed at the ONE shared gate)
- Phase A on real data surfaced two pollutants the per-word view hid: multilingual casino/SEO
  spam + HTML/JSON/code boilerplate n-grams. **`_is_quality_topic` strengthened** (the single
  gate used by extraction, scoring, serve-time, Pipeline Integrity, AND the situation builder):
  SPAM_TERMS (gambling, multilingual), CLAUSE_FILLER (clause debris), BOILERPLATE bigrams/
  tokens, MAX_TOPIC_WORDS=5, MAX_TOKEN_LEN=20, **split on `[\s_]+`** (kills underscored
  field-name fragments like `show_article_date`), + **KNOWN_CONCEPT_PHRASES** recall whitelist
  (fixes a PRE-EXISTING drop of "interest rate"/"monetary policy"/"world cup"/"vector search"/
  "model context protocol"). Precision-verified: 27/27 real pass (0 false rejects), junk rejected.
- Situation builder also applies `registry_only` (tracked-entity requirement) which structurally
  removes spam the vocabulary can't enumerate (first_seen=None).
- **VERIFIED LIVE across scoring + agents:** `/situations/preview` 0 junk situations (365 dropped,
  real events dominate — Greenspan death, SNP/Murrell, Tesla autopilot, Giannis trade, Starmer
  resigns, Iran oil sanctions); `/scores` 0 junk in the 2,290-topic board, "world cup" now served
  + scored 94.8 (recall fix live); `/monitor` pipeline_integrity + scorer_watchdog OK (no
  regression). Engine deployed 5ea4d4b.

### Phase B (LIVE, held-out) — per-situation category + entity disambiguation
- `categorize_situations()` — each situation tagged via majority vote of the shared
  `_topic_category` over its CORE members (prefers a specific category over the catch-all).
  Live: llm·claude→technology, senate→politics, clive·davis→entertainment, gong→current_events.
- `search_situations()` + **`/situations/search?q=`** — entity disambiguation: q=iran → 6 distinct
  situations (oil sanctions / congressional funding / Pakistan-Iran / Trump-Iran war), each
  categorized. Exactly the founder's "make words searchable, user picks the situation."
- Honest limit: some still read "news" (giannis→news not sports) — the category LEXICON has
  gaps, which the audit (below) quantifies as the top cleanup target.

### Audit (LIVE, READ-ONLY) — `/audit/topics`, no deletes (90-day retention respected)
- Scored universe (30d, 9,000 latest-per-topic): **80.3% real / 19.7% junk** (clause fragments
  like "easier the narrative", "bike ride" — now filtered at serve-time by the gate, history
  retained). **75.3% catch-all** (news/general) = the category LEXICON gap, the #1 UX cleanup
  (working cats: technology 955, current_events 332, politics 319, sports 249, business 110).
  **0 exact duplicate-spelling groups** (canonical-key + alias consolidation is working; the
  remaining duplication is SEMANTIC, which the situation layer handles).
- The audit caught + fixed gate false-positives the unit test missed (hyphenated tech compounds
  `retrieval-augmented-generation`, geo `west bank`) — keep hyphens intact, whitelist geo/tech.
- COMPLIANT cleanups (no deletes) — DONE:
  - **#2 serve_payload regenerated** via new `POST /precompute` (GOTCHA G1, background, no
    re-score). Board fresh: 2,601 topics, 0 casino/boilerplate junk. (`asi`/`shaving` generic
    tokens still leak on /scores — a separate serve-filter coverage edge to check.)
  - **#3 lexicon enriched** (`_LEX`): added ONLY unambiguous Catch-All Auditor candidates —
    technology (google, bsky), politics (obama), current_events (iranian/israeli/chinese/
    hormuz/strait of hormuz/juneteenth). Catch-all **75.3%→73.9%** (tech 992, current_events
    400, politics 344). Bare peaceful countries (australia/canada/texas/america) deliberately
    NOT force-routed — multi-category; the SITUATION layer (Phase B) routes them by context.
    Honest: lexicon fixes FREQUENT unambiguous terms (~1.4%/batch); the bulk of the 74% is
    context-dependent entities → structural fix is situation-level categorization.
  - Auditor also flags (separate): corroboration-floor **WORSENING** (single-source catch-all
    leak +230) and **542 tracked topics stuck in catch-all** — data-quality follow-ups.
    **→ SUPERSEDED by 2026-06-23f:** the "WORSENING / 10,488 leaks" was a MEASUREMENT
    ARTIFACT (dormant pre-floor pile + missing floor exemptions + window drift). True
    current leak ≈5; the floor is healthy. The 542 tracked were fixed at the source
    (lexicon + record_detection gate + sweep quarantine). See the 2026-06-23f entry.
  Engine deployed 55ff376. NO velocity_scores deleted (90-day retention respected throughout).

---

## Session 2026-06-23d — Opus fundamentals audit + Phase 2 referee (Wikipedia) begun

### Audit (verified against LIVE engine, not docs — verify-before-ship)
- **Congruency audit of all scoring models / agents / contracts.** Confirmed the
  fundamentals are largely solid LIVE, and found + fixed the gaps below.
- **Date canon (§14) — VERIFIED CLEAN live.** `/monitor/datecanon`: 0 non-canonical
  across all declared columns (`market_signal_history.signal_date` 71,146 rows;
  `risk_signals.signal_date` 2,226; `accuracy_ledger.breakout_date` 21 — all 0 bad).
  **`DB_DATA_DICTIONARY.md` is STALE** (committed 2026-06-21, pre-migration): it still
  shows `market_signal_history.cycle_at` + MIXED formats that the live schema no longer
  has. Doc-hygiene only — regenerate it. (Auditor blind spot noted: a declared-but-absent
  column is silently skipped at monitoring_agents.py:1002 — fine today since the column
  exists, fragile if a future rename desyncs DATE_SEMANTIC.)
- **INV-1 / serve consistency — clean.** `pipeline_integrity = ok` live (no stale
  serve_payload, no mainstream collapse). `scorer_watchdog = ok`.

### Fixed (✅ shipped + deployed, engine c0705b9)
- **heisenberg_gap derived-rule break (was live CRITICAL: 50/800).** Root cause: the
  Enterprise `/query` path (`persist_velocity_score`) wrote the SCORE-TIME gap;
  `apply_calibration` overwrites det/conf but inherits the stale `heisenberg_gap` from
  `**raw_result`. The contract auditor samples the latest row per topic, so every
  `/query` re-introduced a stale row → oscillated 33↔50, never "healed" (the SESSION_LOG
  "healing" claim was wrong). Fix: **sink-harden** `persist_velocity_score` to recompute
  `gap = det − conf` right before INSERT (mirrors the main path L4370). Invariant now holds
  at the write sink regardless of caller. Zero score impact (derived display field).
- **Weight single-source migration COMPLETED** (the "3 disagreeing recipes → 1" Step 0
  item, finished). `scoring_weights.py` existed but the primary scorer + `ai_grade` +
  `enterprise_intel` each kept their OWN hardcoded copy (agree-by-value, not enforced).
  Now ALL import from `scoring_weights.py` (value-identical fallback). Primary scorer uses
  an explicit naive left-fold `_weighted()` (NOT `sum()` — CPython 3.12 compensated
  summation shifts the 2nd decimal on ~0.01% of rows). **Proven BIT-IDENTICAL across 200k
  random vectors (0 mismatches)** → zero score impact, single source now real.

### Phase 2 — Independent referee (Wikipedia Pageviews) — STARTED
- **`referee_wikipedia.py` built + live-validated.** HELD-OUT (imported by NOTHING in the
  scoring path; read-only to the score, forever — the falsifiability guard). Resolve
  (MediaWiki opensearch, confidence-gated, quarantine-on-no-match) → daily pageviews
  (Wikimedia REST, anchored window around our detection date) → **arrival date** = first
  SUSTAINED surge above a lowest-40% quiet baseline, with same-surge `since` floor —
  MIRRORS the ledger's frozen `detect_breakout_date` so both providers define "arrival"
  identically. `lead_days = detection − arrival` (positive = we were LATE = false-early).
  Live-tested on Hormuz/Iran/DeepSeek/ChatGPT: resolves + dates surges correctly; surfaced
  that continuously-hot topics (Iran/Hormuz) have no clean "arrival" (the referee's honest
  limit — precise on quiet→loud transitions).
- **Founder froze the arrival definition:** EARLIEST of (Wikipedia surge OR GDELT surge);
  false-early if our detection is after it (strictest against over-claiming early).

### "Strait of Hormuz issue" — RESEARCHED + RECONCILED (the key reframe)
The founder flagged: the app was only built ~2026-03, so apparent "late" calls may be a
STARTING-POINT artifact, not an engine defect. Confirmed — decisively.
- **Topic-class research** (live Wikipedia signatures): topics fall in 3 classes —
  CLEAN (one isolated arrival; referee precise), CHURNING (Hormuz 42% of days elevated /
  Iran 17% — surges repeatedly, no single arrival), STEADY_MAINSTREAM (Russia/China
  peak/floor ~2× — never surges, permanently arrived). Codified `classify_topic()`.
- **Observation-window gate** (`assess()` + `our_first_seen`): a false-early is FAIR only
  if we were TRACKING the topic before its arrival. Ran the gate over all 21 REAL ledger
  detections joined to each topic's `first_detected_at`: **only 1/21 is a fair scoring
  test** (Daveigh Chase — caught SAME-DAY, LED). 4 are DISCOVERED_AFTER_ARRIVAL (we found
  diffusion models/world models/Juneteenth/FIFA 2–30 days AFTER their Wikipedia surge — a
  DISCOVERY-LATENCY gap, NOT a scoring false-early), 8 unresolved (Wikipedia lacks niche
  tech → GDELT needed), 7 no-surge, 1 already-mainstream.
- **Conclusion:** the apparent late-calls are overwhelmingly a young-system / discovery-
  window artifact. The naive "83% false-early" collapses to a non-result; fair sample = 1.
  Honest verdict = **INSUFFICIENT, claim nothing yet** (punch-list Phase 3). The referee is
  a PROSPECTIVE instrument — meaningful as detections of post-launch emergences accrue.
  The real actionable lever it exposes is **discovery latency** (widen/speed collection so
  topics enter the corpus BEFORE they surge), which is distinct from scoring calibration.
- **NEXT:** GDELT provider (covers the 38% Wikipedia can't), held-out `referee_observations`
  table, `/accuracy/referee` endpoint that applies the observation gate + reports the
  fair-sample count alongside any rate. NO public accuracy claim before a fair sample matures.

---

## Session 2026-06-23c — Step 0 🔒 feature-flagged quarantine (continued)

### Completed (✅ LIVE — pushed, deploy next)
- **`scoring_weights.py` — single source of truth for weight vectors.** New module.
  Defines `WEIGHTS_OVERALL / WEIGHTS_DETECTION / WEIGHTS_CONFIDENCE / COMPONENTS`.
  All 6-component (G·I·M·D·C·P, N excluded). Canonical values unchanged.
- **`calibration_engine.py` — dead 5-component block replaced.** Legacy recompute
  at the end of `compute_calibrated_gradient()` now imports from `scoring_weights.py`
  and includes the P (persistence) component. This code path is never called by the
  live scoring path (owned by `signal_calibration_integration.apply_calibration`), so
  zero score impact. Documented with a `NOTE:` comment.
- **`signal_calibration_integration.py` — write-time quarantine (feature-flagged):**
  - `SCORE_QUARANTINE_ENABLED = os.getenv(..., "false")` — default off
  - `_quarantine_weighted_sum()` helper: None-aware weighted average, renormalizes
    over present components only (absent ≠ genuine zero → no fake-zero deflation)
  - `apply_calibration()`: when flag=True, component reads omit `or 0` so absent
    values stay None and feed `_quarantine_weighted_sum`. When flag=False (default),
    byte-identical to original `or 0` behavior — production scores unchanged.
- **`market_signal_engine.py` — market component quarantine (feature-flagged):**
  - `_MKT_QUARANTINE` mirrors same env var
  - `assemble_market_components()`: when flag=True and both FINRA (`short_interest`)
    AND WhaleWisdom (`institutional_holdings`) are absent AND no insider stage-1
    signals, `positioning_concentration` returns `None` (structurally missing data —
    not a genuine zero reading)
  - `compute_market_signal()`: `absent` set is always empty when flag=False → non-
    renormalization path → byte-identical to original. When flag=True, renormalizes
    `DETECTION_WEIGHTS` / `CONFIDENCE_WEIGHTS` over present-only components.
- Commit: `7a8a511` — `git push origin main` done.

### Open / Next
- **Phase 2 (Wikipedia + GDELT referee) — build this next.** The gate that unblocks
  the 🔒 quarantine fixes. No public accuracy claim before this returns a measured
  false-early rate. Design: held-out validation table (topic → Wikipedia breakout
  date, GDELT corroboration), `detect_vs_breakout` delta distribution, false-early
  rate metric. Endpoint: `/accuracy/referee`.
- **After Phase 2 validates direction:** set `SCORE_QUARANTINE_ENABLED=true` on
  `nowtrendin-v2-engine` Heroku app → Phase 2 backtest confirms improvement →
  commit as permanent default.
- **`positioning_concentration` data gap** — requires populating upstream FINRA /
  WhaleWisdom data (a separate collection task). The quarantine gate above correctly
  surfaces this as absent rather than zeroing it.
- **Phase 3** (predictive lead against price) — only after Phase 2 shows an
  acceptable false-early rate.

---

## Session 2026-06-23b — Alpha-engine punch list: Step 0 + Step 1 ⚡ fixes + Agent 17

### Completed (✅ LIVE — deployed)
- **Alpha-engine punch list framing.** Three-phase plan established (CLAUDE.md):
  - Phase 1 — make the present-tense score correct (Step 0 + Step 1 mechanics)
  - Phase 2 — Wikipedia + GDELT independent referee (no-gap test → false-early rate)
  - Phase 3 — prove a predictive lead against PRICE (pre-registered bar, prospective)
  - No investor performance claim before Phase 3 returns PASS, documented + reproducible.
- **Step 0 ⚡ (HIGH-severity, no backtest) — all shipped:**
  - **AI-grade weight integrity (C1/C2):** `grade_tool.py` previously used legacy 7-component
    weights (N still in denominator even though `comps["N"]=0.0`). Removed N entry;
    renormalized detection (6→6 components) and confidence (5→5) weight sets to sum to 1.0.
    Grade scores now land on the engine scale. No-circular-N integrity closed.
  - **`engagement_asymmetry` key drift (C4):** scoring path used `"engagement_asymmetry"` but
    signal dict key was `"engagement_asymmetry_score"`. Fixed to match real key.
  - **Calibration swallows now log + stamp (C8):** three silent `except` blocks in
    `apply_calibration` that swallowed errors and served raw (uncalibrated) scores now
    log a warning + record to `calibration_errors` table + stamp `calibration_method="raw"`.
  - **`risk_stage` single vocabulary (C6/C7):** declared `_RISK_TO_MARKET_TIER` map at
    module top of `financial_risk_gradient.py`; both the market-gradient path and the
    no-market fallback now write the single MARKET tier vocabulary
    (ELEVATED/ACTIVE/BUILDING/ROUTINE/DORMANT). Off-enum stages can never appear in `risk_stage`.
  - **`heisenberg_gap` signed + write-path fix (C5):** serve path fixed to signed
    (det−conf). Write path: added unconditional signed recompute right before INSERT so the
    stored column always matches the formula (both dual-pathway AND apply_calibration now
    covered). Agent 17 confirmed 33/800 residual stale rows from before the fix (heal
    as topics re-score).
- **SCORING_CONTRACT registry + Agent 17 (Scoring Contract Auditor, `/monitor/scoringcontract`, B3b):**
  New `scoring_contract.py` module — the declared FORMAT CONTRACT for every scoring field
  (type/unit/range/enum/required/derived-rule). Agent 17 audits live data against it:
  catches value violations, off-enum stages, degenerate (flat) fields (the C3 silent-misread
  fingerprint), derived-field inconsistency (heisenberg_gap==det-conf), and undeclared
  scoring-shaped columns. Live: 0 value violations, 0 degenerate fields, 1 derived mismatch
  (33/800 heisenberg_gap stale rows from before the write-path fix — healing).
- **`/monitor` timeout fix:** `run_all` previously included `catchall_auditor` (full
  velocity_scores + topic_signals 72h scan, documented "end-of-day") alongside `canon_date_auditor`
  and `scoring_contract_auditor` — all three did full table scans that pushed the synchronous
  `/monitor` endpoint past Heroku's 30s router limit. All three moved to their own endpoints
  (`/monitor/catchall`, `/monitor/datecanon`, `/monitor/scoringcontract`). `run_all` is now
  the FAST liveness roll-up: 4.1s confirmed.
- **Step 1 ⚡ (data hygiene, display — all shipped):**
  - **Alias-merge:** `_TOPIC_ALIASES` in `gravitational_anomaly_detector.py`:
    `"hormuz" → "strait of hormuz"`, `"mcp" → "model context protocol"`. Forward-only.
  - **Market interpretation honesty:** `_interpret_gap()` in `market_signal_engine.py` now
    detects when >50% of market inputs are exactly 0.0 (absent data) and appends a note to
    the ROUTINE text, distinguishing "genuinely quiet" from "insufficient data coverage."
  - **Minimum signal guard for market movers:** `get_risk_scores()` now sorts topics with
    `total_signals < 3` below scored items, so cold-start noise doesn't surface as a top mover.

### Open / Next
- **Step 0 🔒 (score-moving, feature-flagged) → COMPLETED in session 2026-06-23c.**
  `scoring_weights.py` created; quarantine gated on `SCORE_QUARANTINE_ENABLED=false`;
  commit `7a8a511`.
- **Phase 2 (Wikipedia + GDELT referee) — build this next.** No public accuracy claim until
  this returns a measured false-early rate. Gate that unblocks flipping the 🔒 flag.
- **Phase 3** (predictive lead against price) — only after Phase 2 shows an acceptable
  false-early rate.

---

## Session 2026-06-23 — Read-path performance: Prewarm Agent, pagination, favorites

### Completed (✅ LIVE — deployed)
- **Prewarm Agent (Agent 15 — operational, read-only re: data).** Daemon thread in the
  **API process** that keeps every list-feed superset hot (`/scores`, `/topics`,
  `/history/recent` 7d/24h/12h, `/risk/scores`), re-warming every 25 min inside the 30-min
  cache TTL. `GET /prewarm` is non-blocking (kicks a background warm — synchronous warm
  ~38–44 s exceeds Heroku's 30 s router limit). Documented in `AGENT_CHARTER.md` (Agent 15),
  `DATA_BUILDING_BLOCKS.md` (§10.J + §8 read-path), and the nowtrendin2.0 skill.
- **History endpoint cached + prewarmed.** `/history/recent` was uncached → ~6 s/2.1 MB on
  the 7d view (the visible "Loading…" delay). Refactored to the scores/topics superset-cache
  pattern (`_compute_history_full`, limit-independent) → ~0.4 s compute from warm cache.
- **Progressive pagination for all list sections.** `/history/recent` + `/risk/scores` now
  take `offset`; web `api.ts` got `historyAll()` + `riskAll()` (fetch 100 at a time, paint
  per batch). History.tsx + MarketSignal.tsx load progressively (Trends `/topics` already did).
  All three list surfaces now match.
- **Market Signal prewarm parity** — `/risk/scores` superset-cached (`risk_full`) + warmed
  each cycle. All five web/mobile feeds are now prewarmed.
- **Favorites "Track topic" fix** — scoped to trend/history topics only (was mixing market
  instruments); clicking opens **History** pre-filtered to the topic (was the Market detail rail).
- **AI Context fixes** — serve-time `_clean_explainer` + hardened `_extract_json` (raw
  ` ```json ` leak); `key={topic_key}` on the web detail rail (stale-context-on-topic-switch).
- **Stage rename** — "Emerging" → "Indicating" (display-only via `stageLabel()`, all surfaces).
- **Accuracy-Ledger backlog (1066 pending) — analysis + the safe fixes (#1–3) shipped.**
  Root cause: inflow (≤20 detections/score-cycle) ≫ outflow (sweep was once/day, 8/run) AND
  `sweep_pending` had no `ORDER BY` so it re-checked the same head rows forever (the slow-to-
  confirm LED wins, which sit in the tail, never got reached). Fixes: (1) rotate
  oldest-checked-first; (2) resolve past-deadline rows to FALSE_POSITIVE with NO Apify fetch;
  (3) own cadence `LEDGER_SWEEP_INTERVAL_HOURS` (default 6h = 4×/day), env-tunable vs the
  Apify budget. Unit-tested; verified live (total 6→7, pending 1067→1066 right after deploy).
  Deferred (backtest-gated, your call): #4 shorten `LEDGER_TIMEOUT_DAYS` 90→~45; #5 prioritize
  fetches by breakout-window + conviction.
- **Canonical date (§14) enforced in the ledger path** — both detection-recording paths
  (`_record_top_detections`, `validate_recent_detections`) were slicing `detection_date` with
  raw `[:10]` (the forbidden anti-pattern). Now use `date_utils.to_iso_date` (whole-string
  parse, None→skip on unparseable). `accuracy_ledger.detection_date` confirmed clean YYYY-MM-DD live.
- **Canonical Date Auditor (Agent 16, `/monitor/datecanon`, B3a)** — answers "how did the
  `[:10]` violations survive the canon sweep, and what stops it recurring." Root cause:
  `gate_date()` is OPT-IN per call site; the `DATE_SEMANTIC` registry had no consumer
  verifying compliance; a path that BYPASSES the gate creates no review → invisible to the
  gate's own audit. No agent owned "every date-semantic write is canonical." Fix: an agent
  that audits the DATA (every registry column + every `*_date` column discovered from the
  live schema), so a bad date is caught regardless of code path and a NEW source is covered
  automatically (coverage by column funnel, not a per-source list). Sink-hardened
  `record_detection`. Wired into `/monitor` run_all. Verified live: **status ok, 0
  non-canonical across all 8 date-semantic columns** (incl. market_signal_history 66k,
  pull_history 228k rows). Operational `timeout_date` allowlisted (it's an instant, not a key).

### Open / Next
- Accuracy-Ledger fixes **#4–5** (timeout shorten + fetch prioritization) — deferred,
  backtest-before-ship.
- Optional: apply the same progressive load to Alerts/Watchlist/Dashboard typeaheads.

## Session 2026-06-22 — Sources, canonical-date checkpoint, M/D direction

### Completed (✅ LIVE — engine v98)
- **Nasdaq Trade Halts** wired into the risk module (`financial_risk_gradient.collect_nasdaq_halts`,
  registered in `run_risk_collection`): official exchange RSS, stage-2 microstructure;
  canonical `signal_date`=HaltDate, `source_time`=HaltTime. Verified in prod: 29 halts.
- **The New Yorker** (news + business) added to the reputable-direct RSS roster
  (`_RSS_FEEDS`). Verified in prod: 54 raw / 269 topic signals, tier=mainstream.
- **Documentation checkpoint:** CLAUDE.md (§14 canonical date/time model, §15 source roster +
  M/D direction), DATA_BUILDING_BLOCKS.md (§3a canonical-date block B3a, source registry,
  §5 M-vs-D router note), the **nowtrendin2.0 skill** (CURRENT BUILD STATE section), and 11
  data/scoring agent skills (consistent "Canonical dates · sources · M/D" section).
- Memory: added `project-dark-matter-routing` (the platform_tier D-vs-M finding + gotcha).

### Open / Next (⏳ IN DESIGN — NOT shipped; gated by backtest-before-ship)
- **M/D provenance reweighting**, two coupled `_news_write` changes:
  1. Reputable ≠ automatic mainstream full weight → 1 reputable = ½, FULL only on ≥2 DISTINCT
     reputable (distinct `source_name`; the "Belgium vs Iran" case).
  2. Research/early-signal outlets (War on Rocks, Rest of World, Global Issues, Pew, RAND-blog,
     NBER) → Dark Matter via `blog_collectors` GHOST_FEEDS at **expert/niche tier** (NOT
     `_news_write`). Feeds validated (prod UA). Adversarial integrity verify + `backtest_dual_pathway.py`
     required before deploy.

### Hard decisions made
- The D-vs-M router is **`platform_tier`**, NOT `is_organic` (mapped across the engine). Routing
  research outlets through `_RSS_FEEDS`/`_news_write` would stamp them `mainstream` and SUPPRESS
  the early signal — so they must go through the blog/expert-tier path. (This corrected an earlier
  plan that had prepped them for `_RSS_FEEDS`.)
- Reputable-corroboration weighting extends the catch-all `CATCHALL_MIN_SOURCES≥2` philosophy from
  *admission* to *weight*; distinct-source counting must key on `source_name` to defeat wire syndication.

---

## Session 2026-06-20 (session 2) — Infrastructure audit + skill hardening

### Completed

- **Full infrastructure audit:** Confirmed both clients (web terminal + mobile) and backend
  all correctly point to the v2 engine (`nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`).
  No discrepancies between platforms — single source of truth rule is working at the data layer.

- **Deploy skill rewrite (critical fix):** The old `/deploy` skill was pointing the engine
  subtree push to `heroku main` (the BACKEND remote) instead of `heroku-v2engine main`.
  This is what caused the accidental 1.0 engine deploy on 2026-06-19. Fixed and backed up
  to `docs/skills/deploy.md` in the repo.

- **`AI_GRADE_CLAUDE_MODEL` updated live on Heroku:** Changed from `claude-sonnet-4-5-20250929`
  to `claude-sonnet-4-6` on `nowtrendin-v2-engine` (Heroku release v69).

- **`docs/ENV_REFERENCE.md` created:** Complete map of every env var for both engine and
  backend — status (SET/MISSING), description, and exact fix commands for all gaps.
  Key finding: GUARDIAN_API_KEY is missing → Stage 4 mainstream media signal silently absent
  every scoring run; GDELT fallback is rate-limited on Heroku IPs.

- **`transfer/.env.example` + `backend/.env.example` created:** Local dev reference templates
  (key names only — no values). Standard practice to prevent onboarding confusion.

- **`/nowtrendin2.0` skill hardened:** Added INFRASTRUCTURE STATE section (audit results,
  what's correct, what was fixed, pending user actions with exact commands). Added PENDING
  USER ACTIONS quick-check to session startup. Fixed wrong engine URL that was in STEP 4
  health check (pointed to 1.0 frozen engine). Fixed wrong deploy topology table.
  Rule #9 added: API key values never go in Git.

- **`docs/skills/nowtrendin2.0.md` synced:** Cloud backup of the skill now matches local.

- All above committed and pushed: `6909737` + follow-up skill sync.

### Open / Next

- **GUARDIAN_API_KEY** (HIGH) — Register free at open-platform.theguardian.com/access.
  Without it, mainstream media (Stage 4) is absent every scoring run.
  Command ready: `heroku config:set GUARDIAN_API_KEY=<key> -a nowtrendin-v2-engine`

- **SECRET_KEY on backend** (HIGH — security) — Django using insecure hardcoded default.
  Generate + set: `heroku config:set SECRET_KEY=<key> -a nowtrendin-backend`

- **REDDIT_CLIENT_ID/SECRET/USER_AGENT** (MEDIUM) — Reddit signal not collected.
  Register at reddit.com/prefs/apps (free), set 3 vars on engine.

- **APIFY_REALTIME_ACTOR + APIFY_TRENDS_ACTOR** (MEDIUM) — Token set, actor IDs missing.
  Check Apify console for existing actor IDs.

- **GOOGLE_ANDROID_CLIENT_ID** (MEDIUM) — Android Google OAuth may fail.
  Retrieve from Google Cloud Console.

- **Velocity retention 365 days** — PENDING USER CONFIRMATION. Do NOT implement until explicitly confirmed.
- **Stripe + push notifications** — deferred, require custom dev client (off Expo Go).
- **NYT RSS feeds** — 39 live feeds identified as viable for topic extraction. Not yet implemented.

### Hard decisions made

- ENV_REFERENCE.md documents key names + status only — never values. Values live on Heroku only.
- Do NOT re-run the full Heroku config audit each session; check the specific PENDING USER
  ACTIONS list instead (saved in /nowtrendin2.0 skill INFRASTRUCTURE STATE section).

---

## Session 2026-06-20 (session 1)

### Completed
- **Web terminal UX:** Added X clear buttons to every filter input across all platforms (History search, Market chip-search, Grade GradedList search, Shell global search, mobile history/search/watchlists)
- **History tab reset:** Clicking "History" in the sidebar now remounts the component (historyNavKey counter) — clears filter + selection. Mobile uses `useFocusEffect` to clear on tab focus.
- **Screener — Trends table:** Centered all column headers. Added DIRECTION column (TrendingUp/TrendingDown/Minus icon) after Category.
- **Screener — Direction sort:** Direction column is now fully sortable (orange triangle, SortKey type extended, special-case comparator mapping gap→-1/0/1). Deployed to gh-pages.
- **Grade click-through fix:** Clicking rows in Graded Library (and History) now opens the full ProposedCard detail — `sel` state added to GradeList. Fixed smart-quote encoding bug in GradeList that broke the esbuild step.
- **Skill /nowtrendin2.0:** Created session-startup skill — reads all context, runs health + skills + agents checks, and enforces the GitHub-as-cloud-backup auto-save protocol.

### Open / Next
- **Velocity retention 365 days** — PENDING USER CONFIRMATION. Do NOT delete any velocity_scores rows until user explicitly confirms the rule change from 90→365 days.
- **Stripe + push notifications** — deferred, require custom dev client (off Expo Go).

### Hard decisions made
- Direction sort: `direction` is derived from `gap`, not a stored field — special-cased in the sort comparator rather than materializing a fake field on Row.
- GradeList encoding: Edit tool on Windows can introduce Unicode smart quotes; future mitigation is Python binary replacement for source files.

---

## Live URLs

| Surface | URL | Notes |
|---|---|---|
| **Web app** (use from anywhere) | https://nowtrendin-web-8c1bb8c9f7f2.herokuapp.com/ | Static Expo web build on Heroku app `nowtrendin-web`. Snapshot — rebuild with `./redeploy-web.sh`. |
| **Engine (FastAPI) — v2, the ONLY active engine** | https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com | Heroku `nowtrendin-v2-engine`. Deploy: `git subtree push --prefix=transfer heroku-v2engine main` from `NowTrendin v2.0/` (foreground). |
| ⛔ Engine 1.0 — **FROZEN, DO NOT DEPLOY** | https://nowtrendin-e62dcb9ecb69.herokuapp.com | Heroku `nowtrendin`. Legacy/frozen (live Android + pre-Apr-2026 data). A git hook blocks commits in `NowTrendin/`. The old `git push heroku HEAD:main` here caused the accidental 1.0 deploy on 2026-06-19 — never use it. |
| Backend (Django) | https://nowtrendin-backend-acb79c396814.herokuapp.com | Heroku `nowtrendin-backend`. Deploy: `git subtree push --prefix backend heroku main` from `NowTrendin v2.0/`. |
| Frontend source | `origin` (GitHub) | Expo Go phone preview needs same-WiFi LAN (`exp://192.168.68.52:8081`) + firewall rule for TCP 8081. |

Internal founder key (gated engine endpoints): `X-Internal-Key: nt-internal-7f3a9c2e5b81`

---

## What was built this session (2026-06-10)

### Data sources
- Added creators: Graham Stephan, TheGrahamStephanShow, Minority Mindset (join Meet Kevin, Andrei Jikh).
- Added 22 broadcast YouTube channels (CNBC, BBC, Bloomberg×3, Reuters, WSJ, FT, Al Jazeera, 60 Minutes, etc.) — mainstream tier.
- Yahoo Finance (RapidAPI) news as a genuine contributor; feeds BOTH the Trends pipeline and the Market (risk) pipeline.
- WhaleWisdom 13F institutional positioning (metered/trial tier — `holders` endpoint blocked until subscription upgrade; monitor `WHALEWISDOM_MONITOR.md`, review 2026-07-08).
- OFR Short-Term Funding Monitor (systemic leverage) + FINRA short interest, both instrumented in the founder `/usage` cost ledger.
- YouTube creators + broadcast + Yahoo Finance all feed both Trends and Market (free pulls).

### Integrity (HARD RULES — now enforced)
- Reputable-publisher **allowlist** on aggregated news (`_NEWS_REPUTABLE_SOURCES`) — only vetted outlets enter the corpus; non-reputable dropped with a logged count.
- **Provenance tiering**: broad/unverified news quarantined at ~1% weight, promoted to ~10% ONLY when independently corroborated — reputable corroboration → mainstream (M), dark-matter corroboration → Dark Matter (D). Uncorroborated never stands alone (excluded from scoring).
- **No circular metrics**: the N (Now TrendIn demand) component is DELIBERATELY EXCLUDED from the Gradient Score (Detection/Confidence/Overall) — the live engine composes from six external components (G/I/M/D/C/P), renormalized to sum to 1.0, so our own users' demand can never create a feedback loop. N is computed and shown as a SEPARATE community-demand signal. The Signal Convergence validator also uses N-independent factors. (A separate, demand-inclusive "Now Trending Gradient Score" what-if is shown only on the trend signal page, clearly labeled and never sold as the Gradient Score.)
- Measurement, not advice — neutral tiers, disclaimers everywhere.

### Engine / scoring
- **Signal Convergence** (`now_trending_direction.py`, `GET /convergence/{topic_key}`) — downstream directional validator: does raw volume + niche concentration confirm the Gradient Score's direction? (vs Gradient, vs Niche). Independent of N.
- **Dark Matter recalibration** — first-timer score now `100 * ratio^0.7` (was `ratio*160`, clipped at 62.5% → no high-end resolution). Tested across 12 cases.
- **VIRAL-with-0-signals fix** — evidence gate in `ai_topic_intelligence.py`: a recognized AI topic with < `AI_TAXONOMY_MIN_SIGNALS` (5) collected signals no longer floors to a measured-looking VIRAL score; falls back to raw score + no tier, so the score is consistent with the signal count shown.
- **Trend Beneficiary** (`trend_beneficiary.py` + `_wire.py`) — SanDisk-pattern exposure: is a company positioned to benefit from a detected trend, EARLY vs LATE in the cycle. `GET /beneficiary/{ticker}`. Auto-theme extension (`theme_extension.py`) promotes BREAKOUT/STRONG topics into the beneficiary THEMES.
- **Explainer bug fixed** — `topic_explainers.full` → `full_text` (`full` is a Postgres reserved word; was breaking the MORE INFO feature).
- Connection-pool leak fix (was 500-ing `/scores`).

### Market Signal (the "Market" section)
- **Baseline-relative dual score** (`market_signal_engine.py`) — Gradient-Score philosophy on market data, every component z-scored vs the item's own history. Detection (analyst + positioning) / Confidence (fundamentals + price). Neutral tiers ELEVATED/ACTIVE/BUILDING/ROUTINE/DORMANT. CALIBRATING until 3+ cycles.
- Grounded in real sources only (Alpha Vantage, FINRA, WhaleWisdom, Finnhub/beneficiary, OFR, SEC Form-4, creators/broadcast, sustainability) — rejected aspirational components (options flow, credit spreads, price candles we can't source).
- **Historical backfill** (`POST /market/backfill`) — seeded `positioning_concentration` from FINRA 180-day series (180 points, 15 companies). Finnhub fundamentals backfill returns 0 (free-tier limit).
- **Leverage Health** category (1–100, high = lower debt) from balance-sheet sustainability. Live for ~8 companies (Meta 100, Microsoft 91, Tesla 66, Morgan Stanley 40).
- Market tab UI now **mirrors Trends**: "Search Current Market Trends" bar, Pull Market Trends, "Market Signal" explanation (renamed from Positioning), category chips + stat tiles, focused `market-category/[key]` pages.

### Grade section
- 3 tabs: **New Grade** (only one that charges, "Grade · 1 token"), **History** (this member's grades, 12-month, search, no charge), **Graded** (all members' graded topics, search, no charge). Backend `GradeHistory` model + `/api/grade/history/` + `/api/grade/all/`.
- **Grade ↔ Market consistency**: grading a COMPANY now also pulls the full market data and attaches `market_signal` — the same Market read as the Market section (identical numbers). The AI attention estimate stays a separate, labeled read. (They measure different questions: attention trend vs market positioning.)
- Enterprise grade allowance bumped 1,000 → 100,000 (founder balance set to 99,997).

### App UI / homepage
- Homepage chip row + stat tiles unified from one source of truth (`CATEGORY_DEFS`): NowTrendIn (lead, brand-colored) + All + Breakout/Strong/Emerging/LowRisk/Anomalies. Each navigates to a focused `category/[stage]` page. Removed the static "What does this mean?" card.
- "Now Trending (N)" explanation added to Signal Detail (above Dual Score Analysis), with the real Volume/Recency formula.
- "Why the scores diverge" made LIVE (was static); Topic Maturity ("ESTABLISHED") clarified with the live `maturity_reason`.
- Heisenberg → **DUALITY** wording.
- "Other" tab → **Market**; new "Pull Market Trends" button (`/api/pull-market/` → engine `/risk/collect`).
- Detail pages moved under `(app)` so they get the bottom tab bar; non-primary routes hidden from the bar (only Home/Search/History/Alerts/Profile show).
- "Search" tab rebuilt as "Search A Topic" with 3 tabs (Trends/Market/Graded), each searchable.
- **Web desktop layout**: app centered in a 480px phone-width column; onboarding carousel width capped.

### Tooling (Claude Code skills in `~/.claude/skills/`)
`/deploy`, `/data-health`, `/risk-verify`, `/tier-gate-audit`, `/accuracy-sweep`, `/beneficiary-backtest`, `/expo-recover`.

---

## Scheduled / open items
- **2026-06-20** — 10-day integrity monitor (scheduled task): convergence, dark-matter recalibration, news provenance rates, Market Signal baselines filling in.
- **2026-07-08** — WhaleWisdom upgrade-analysis review (scheduled task).
- Market Signal reads **CALIBRATING** until per-component baselines build (FINRA seeded only 1 of 7 components; the rest accrue live). Watch on the monitor; option to extend the backfill (needs paid Finnhub) or relax the CALIBRATING gate.
- Non-watchlist companies graded via Grade show CALIBRATING market signal (no baseline history yet) — expected.

---

## Recovery cheatsheet
- Resume this thread (same machine): `claude --continue` (or `--resume`) in `NowTrendin v2.0/`.
- Move to another machine: copy `~/.claude/projects/C--Users-acinv-...-NowTrendin-v2-0/` (transcript + `memory/`) to the same path; needs identical project path for the hash to match. Otherwise rely on `git pull` + the copied `memory/` folder + this log.
- Update the web app after any frontend change: `./redeploy-web.sh` from `NowTrendin v2.0/`.

## Session 2026-07-05 (evening) — catch-all fix · Apify streamlining · weekly audit #3

### Completed
- **Weekly improve-system audit #3** committed (`audits/improve-system/IMPROVE_SYSTEM_2026-07-05.md`).
- **/monitor/catchall FIXED** (was 503/H12 since ~06-27). Three causes: (1) auditors measured the
  bare lexicon `_topic_category` instead of the serve-time `_category_for` (situation+context layers)
  — the 80.5%-vs-served gap was a measurement artifact; (2) unbounded latest-per-topic scan over the
  365-day retention classified every topic ever seen (H12); (3) full-table `topic_signals` scan on
  unindexed `extracted_at`. Now: serve-time classifier + `CATCHALL_WORKING_SET=6000` recent working
  set + explicit-key chunked corroboration (index seeks). Live: HTTP 200, catch-all 70.2% (4213/6000),
  floor STABLE, leak 20, 190 tracked calls in worklist.
- **Catch-all lexicon (Agent 6 worklist, founder-confirmed):** WC-2026 cluster (worldcup/mundial/
  golden boot/usmnt/haaland/manchester united/balogun/vozinha), youtube/whatsapp→tech,
  mamdani/zohran/mcconnell→politics, walmart/costco→business, zendaya/victor willis/adam sandler→ent,
  khamenei/ayatollah/america250/250th birthday/july 4th/mount rushmore/ukrainian/british→current_events.
  Policy held: bare countries/kelce/visa/america stay OUT (situation layer). 33/34 tests pass.
- **APIFY STREAMLINING (founder hard rule: ALL paid pulls at the 4×6h clock slots only):**
  sweep `interval+boot-fire` → `cron 0,6,12,18:45 UTC` (boot-fired paid sweeps eliminated — one per
  deploy + Heroku daily cycle); `_fetch_apify` now passes `&timeout=&memory=1024` on the run start and
  ABORTS on poll-budget expiry (the 10-min 0-result runs = the ~$93/mo compute line). Realtime confirmed
  clean 4×/day :30 (2× overrun gone). `trudax/reddit-scraper-lite` has NO engine refs; founder verified the
  console Schedules page is CLEAN → the $0.08 of trudax runs were one-off/pre-rotation, RESOLVED. Engine v200.

### Open / Next
- Watch Apify usage after v200 (expect ~$221→~$70-90/mo run-rate); then consider Scale($199)→Starter($49)
  plan downgrade — with fixed usage the Scale floor is oversized.
- ~~Set `COST_HEROKU_USD`~~ DONE (2026-07-05, engine v201): $64→$112 from the account-wide decomposition
  (engine Std-2X $50 + essential-1 $9; backend $12; preview/terminal/web Basic $7×3; frozen-1.0 PG $20).
  Cost Sentinel now honestly reads **$718.82 > $700 cap (critical)** — the old $64 masked the breach.
  Trim candidates flagged in COST_MODEL.md: archive+delete the frozen-1.0 essential-2 (−$20), review the
  possibly-redundant nowtrendin-web mirror (−$7); Apify v200 fixes (−$130-150 next period) restore headroom.
- Watch the post-Jul-7 Apify billing period: any trudax event would mean a live external caller (none expected).
- CLAUDE.md §3/§11 still document the pre-Aurora green palette; frontend/DESIGN_SYSTEM.md is the
  enforced contract — reconcile the docs.
- Watch: web-process boot log prints "collect+score every 30 min" vs the documented 6h cycle — verify
  COLLECT_INTERVAL_MIN env on the dynos.

### Hard decisions made
- Apify synchronization codified: no boot-fired or free-running paid actor runs; clock slots + explicit
  user request only (memory `project-ledger-sweep-apify` updated).

## Session 2026-07-06 (overnight) — INV-1 serve fix · mobile parity · self-healing DB pool

### Completed
- **INV-1 serve-consistency FIX (engine)**: web and mobile trends didn't match — SAME database,
  divergent serve paths on STALE rows. /scores re-ran live calibration (incl. the AI floor) on
  payload-less rows; on a row last scored 4 days prior that re-application inflated stored 35.6 →
  served 100 ("coding agent" + "agent memory" + "openai-codex" ranked above today's fresh signals on
  mobile while the web grid showed them mid-pack). Rows older than `SERVE_LIVECAL_MAX_AGE_H` (48h)
  now serve STORED values exactly like /topics. Serve-path only — no stored score changed.
- **Mobile TRENDS chip row restored** (founder request): Now TrendIn / All Signals / Breakout ≥85 /
  Strong ≥70 / Indicating / Marginal / Anomalies — from `CATEGORY_DEFS` (already web-consistent),
  Aurora pill style, COMBINES with the category row like the web. (Aurora had dropped the row.)
- **Mobile per-row category chip** on TrendCard (PLATFORM · STAGE · AGE · CATEGORY) — web parity §17/B8.
- **Mobile Accuracy Ledger zeros FIXED**: fetchAccuracy() mapped extinct snake_case fields
  (total_predictions/led_count/hit_rate_pct/…) while /accuracy/ledger serves camelCase → every metric
  undefined → `?? 0` wall of zeros. Now camelCase-first with fallbacks; verified against the live
  payload (10% / 70 resolved / 7 LED / 11d median / 821 pending — identical to web). "PREDICTIONS" →
  "RESOLVED" + pending-in-flight line (honest denominators). Preview redeployed ×3 through the night.
- **Self-healing PG pool (db_compat, 12/12 behavior-tested)** after the /scores outage: psycopg2's
  pool has NO reclamation — getconn() hands out server-killed conns; first use raises; no-try/finally
  call sites orphan the slot FOREVER (server sat at 2/20 while every request raised PoolError; plain
  restarts re-poisoned at each boot burst; `pg:killall` under live dynos made it worse). Fixes:
  SELECT-1 checkout probe (dead conns discarded, never handed out), broken-conn discard on close,
  bounded DIRECT fallback (PG_DIRECT_MAX=4 — reads keep serving while exhausted), auto pool-REBUILD
  after 90s persistent exhaustion, try/finally on _compute_scores_full/_compute_topics_full.
  PG_POOL_MAX=12. New rule: NEVER pg:killall while dynos run.
- **Docs updated**: CLAUDE.md footer + §13 catch-all measurement rule; AGENT_CHARTER G4 (stale-row
  serve rule) + G5 (pool reclamation); DBB §1/§7 (clock-slot rule, true costs); COST_MODEL Apify line;
  nowtrendin2.0 skill build state.

### Open / Next
- Confirm /scores recovery on the pool-fix release (monitor armed); then verify coding agent serves
  stored 35.6 on both surfaces.
- Apify Scale→Starter downgrade after ~a week of post-fix usage data.
- Founder decisions: archive+delete frozen-1.0 essential-2 Postgres (−$20/mo); retire nowtrendin-web
  mirror if redundant (−$7/mo).
- Reconcile CLAUDE.md §3/§11 palettes with the Aurora contract (frontend/DESIGN_SYSTEM.md).
- try/finally sweep of remaining get_db() call sites (the pool now self-heals, so lower urgency).

### Hard decisions made
- INV-1 sharpened (Charter G4): never re-calibrate a stale row at serve time.
- Pool operations rule (Charter G5): psycopg2 pool slots are unrecoverable by design — engineering
  must guarantee return-or-discard; pg:killall is forbidden under live dynos.

## Session 2026-07-06 (day) — read-path outage POST-MORTEM + /engine-recovery skill

### The outage in three phases (~12h of /scores 500s; full runbook now in /engine-recovery)
1. **Poisoned client pool** — pg:killall/restarts left dead conns that getconn() handed out;
   first-use raised; no-try/finally sites orphaned the slots (PoolError with the server at 2/20).
2. **Saturated server role cap** — the first rebuild design left wedged holders' conns alive;
   repeated rebuilds stranded slots to 20/20 (FATAL too-many-connections; even collect/score failed).
3. **Wedged prewarm (the invisible one)** — the synchronous warm loop sat 6.3 HOURS blocked inside
   one scores build; no cache ever warmed; every client request cold-built the superset — a
   self-sustaining thundering herd. Freed by the (dyno-down) killall; it immediately warmed 6/7 feeds.

### Hardening shipped (engine v205/v206 + config)
- db_compat self-healing (probe / broken-discard / bounded DIRECT fallback / closeall-REBUILD /
  OperationalError-on-growth retried) — 12/12 behavior-tested.
- `PG_POOL_MAX` 12→**8** (my own 12 bump had eroded the deliberate headroom; engine now ≤12 of 20).
- try/finally on _compute_scores_full/_compute_topics_full.

### Process lessons (encoded as /engine-recovery PRIME DIRECTIVES)
- Read the error SIGNATURE before acting — each phase had a different cause; the fix for one
  worsened another. My own interventions (probing storms, killall under live dynos, restart storms)
  EXTENDED this outage. Triage once, act once, hands off.
- Never probe a cold /scores repeatedly (each probe launches another build) — poll /prewarm instead.
- pg:killall only with dynos scaled to 0.
- A wedged prewarm is visible ONLY via /prewarm last_run age → recommended engine follow-up
  (founder-confirmed deploy): pipeline_integrity alarm on scores-cache-absent + prewarm-stale >3×interval.

### Scoring impact (honest)
- Read-path only for most of the window; during the phase-2 saturation some collect/score cycles
  errored (log: "collect/score phase error", ~13:49 window) — a bounded data gap of a few cycles.
  Ledger + retention unaffected. Collectors resumed automatically each subsequent slot.

### New skill
- **/engine-recovery** — signature table (fast-500 PoolError / FATAL too-many / H12-cold / wedged
  prewarm) + safe recovery sequences + verify/log steps. Roster updated in /nowtrendin2.0.

### Addendum 2026-07-06 — PULL-SYNCHRONIZED PREWARM (founder rule)
- Prewarm now fires `PREWARM_AFTER_PULL_S` (60s) after EVERY data pull completes: end of the
  score phase (6h scheduled cycles + failover; cloud/API process only — local worker's cache
  isn't the serving one) and the `/collect` user pull. Serving caches carry fresh scores the
  moment they exist (was: up to 25 min later on the loop). Warms are now OVERLAP-GUARDED
  (one at a time; stacked kicks no-op — the thundering-herd lesson). The 25-min loop stays
  as the TTL safety net. AGENT_CHARTER Agent 15 spec updated.

## Session 2026-07-06 (late) — repo root cleanup (untracked clutter)

### Completed
- Researched all 38 untracked items, then fixed by category (commit 152147c):
  - **Gitignored**: `.ghpages-deploy/` + `web-deploy-terminal/` (deploy staging clones with
    their own .git), `__pycache__/`/`*.pyc`, `transfer/anomaly_detector.db`, and the personal
    `revised PTCS on Coffe.pdf` (kept local, non-project).
  - **Deleted (regenerable scratch)**: 10 diagnostic curl/DB dumps (ana_crypto/crypto_check/du/
    hist/ledger_detail/pg/risk_check/sc_tmp .json, gt_rss.xml, the broken-redirect
    "C:Tempnyt_economy.xml" NYT RSS sample, transfer/fmp_hist.json) + 3 dated `_06_17_26`
    diagnostic drafts — verified superseded by the TRACKED canonical
    `transfer/{market,trend}_signal_diagnostic.py` (dated ones were the pre-wiring
    standalone versions).
  - **Committed deliverables**: 2026-06-23 audit PDFs → `audits/`; pitch deck →
    `docs/business/`; 4 Jun-15 design mockup HTMLs → `docs/design-mockups/`; Alpha-Engine
    Phases 1-3 + Developer Punch List + nightly-agent moat charter MDs → `docs/`.
  - **Committed `_audit_work/`** (provenance for the two audit PDFs) after a secret scan —
    all "token/secret" matches were prose, no credentials.
- Also committed the pending AGENT_CHARTER.md Agent-15 spec update (aa846e3).
- `git status` now fully clean.

## Session 2026-07-06 (night) — batch-paced pipeline CONFIRMED LIVE + full agent health check

### Batch-paced pipeline (founder rule) — implementation confirmed, docs closed
The three pacing commits (2955260 batch-paced collect+score, aa802ed single-flight supersets,
530b0f4 prewarm feed pacing) are LIVE on the engine; docs were lagging — AGENT_CHARTER had it,
SESSION_LOG + CLAUDE.md did not. Both now updated (CLAUDE.md §13 new BATCH-PACED PIPELINE bullet).
Confirmed in `transfer/gravitational_anomaly_detector.py`, env-tunable, NO overrides set on
Heroku → defaults live:
- Scorer: `SCORE_BATCH_SIZE`=100 per batch + `SCORE_BATCH_PAUSE_S`=10s between batches.
- Collectors: `COLLECT_SOURCE_PAUSE_S`=10s between sources.
- Prewarm: `PREWARM_AFTER_PULL_S`=60s after EVERY data pull (the founder 60s warm rule) +
  `PREWARM_FEED_PAUSE_S`=10s between the 7 feed builds; overlap-guarded.
- Single-flight `_get_or_build`: observed live — prewarm reported scores feed
  "busy (another build in flight)" instead of launching a second build. Working as designed.

### Full agent + data-pull health check (2026-07-07 ~02:45 UTC)
- **No data leaking, scoring active and clean.** Scorer heartbeat 3.3 min (cloud); pipeline
  integrity OK — 0 stale serve payloads (INV-1 fix holding), 0 dupe groups, 0 junk singles,
  serve-consistency 40/40. Datecanon: 16 columns audited, **0 non-canonical values**.
  Catch-all: 38.3% served (down from 70.2%), floor STABLE, single-source leak 3 (delta −5,
  improving). Fragments 0.
- **Collectors 15/17 HEALTHY**, all critical healthy (trust=true). DEGRADED (ran, 0 signals):
  `github` (token configured — investigate) + `reddit` (expected — keys deferred).
- **Cost Sentinel back under cap: $497.89 / $700** (was CRITICAL $718.82) — the Apify
  clock-slot fix landed (Apify live-metered $0.96 this period). X posts 16.9% of budget.
- **Prewarm** pull-synchronized + healthy; all 7 feeds warm (scores 2522 · topics ~1860 ·
  history 7d/24h/12h 2000 · risk ~290 · crypto 12).

### Warns to action (none are leaks; all flag-never-force worklist)
1. `github` collector DEGRADED — runs but 0 signals for ~1h+; check token/API response shape.
2. **Datecanon B3a: 8 undeclared `*_date` columns** — the NEW crypto + market ledgers
   (crypto_accuracy_ledger.detection_date/move_date, crypto_pending_detections
   .detection_date/timeout_date, market_accuracy_ledger + market_pending_detections same) were
   never registered in DATE_SEMANTIC. The auditor's auto-discovery working exactly as designed;
   classify + register them.
3. **Catch-all auditor: 52 TRACKED calls (ledger/pending) stuck in catch-all** — reclassify
   worklist (visa, United States, trillionaire, …); policy: situation layer routes bare
   countries/visa, so route via lexicon/situation review, not blind lexicon adds.
4. Calibration auditor reads evaluated=0/pending=0 in ITS window while /accuracy/ledger serves
   821 pending / 70 resolved — likely a scoped-window read in the auditor, worth a look so its
   small-sample guardrail reflects the real ledger denominators.

### Open / Next
- Investigate github collector 0-signals; register the 8 crypto/market ledger date columns;
  work the 52-tracked-calls reclassification list; check calibration auditor's ledger read.

## Session 2026-07-07 (early) — the 4 health-check warns: researched + fixed (engine deployed ×2)

### 1. github collector DEGRADED — ROOT CAUSE: expired/revoked GITHUB_TOKEN (HTTP 401)
Tested the live Heroku token directly: 401 on /rate_limit AND /search — the 93-char length
says fine-grained PAT (they expire; 90-day default). `collect_github` silently `continue`d
on non-200 → the invisible 0-signal runs. FIXED in code (2185e0f): on 401 the collector now
logs once + retries UNAUTHENTICATED (10 req/min; existing 403 handler absorbs the tighter
limit) so github signals degrade gracefully instead of vanishing; non-200s now logged.
USER ACTION: rotate GITHUB_TOKEN (classic PAT, no scopes, no expiry recommended) — set it
directly in the user's own terminal (never paste a token into a Claude transcript — the
APIFY_TOKEN lesson). Same env var also feeds gradient_engine_backend + research_history.

### 2. Datecanon 8 undeclared *_date columns — registered + classified (2185e0f, fd96200)
detection_date/move_date on market/crypto accuracy ledgers registered in DATE_SEMANTIC
(writers already canonicalize via to_iso_date — 0 non-canonical). First deploy exposed the
right finding: the 3 *_pending_detections.timeout_date columns hold computed deadline
INSTANTS ((detection+TIMEOUT_DAYS).isoformat(), consumed via now > _parse()) — classified
onto the auditor's OPERATIONAL allowlist exactly like the attention ledger's
pending_detections.timeout_date (already there). NO data rewritten (forward-only honored).
VERIFIED live: datecanon status ok — 14 columns, 0 non-canonical, 0 undeclared.

### 3. Calibration auditor 0/0 — key-name mismatch (2185e0f)
It read the /accuracy/ledger ENDPOINT's renamed keys (total/pending/hitRate/smallSample)
off the RAW generate_honest_report dict (sample_size/still_pending/honest_hit_rate_pct/
small_sample_warning) → always 0/0 + phantom small-sample warn. Same bug class as the
mobile camelCase ledger zeros. Now reads raw keys with endpoint-name fallbacks.
VERIFIED live: calibration_auditor ok — evaluated=70, pending=821, hit_rate=10.0.

### 4. Catch-all 52 tracked calls — classified worklist (flag-never-force, NO changes applied)
Auditor caps examples at 15; classification of the visible set:
- POLICY-ROUTED (stay out of lexicon; situation layer handles): United States, the us, visa.
- OLD JUNK PENDINGS (generic words predating the fragment gate; correctly catch-all —
  resolve via the 365d patience-window timeout, NO action): trillionaire, sonny, socialists,
  secretive, scrambling, scanner, rewriting, programmers.
- LEXICON CANDIDATES (founder sign-off; precedent = youtube/whatsapp adds): reddit → tech;
  Roman Safiullin → sports (haaland/balogun precedent); phi + pegasus AMBIGUOUS (greek
  letter / mythical name over-match risk) — recommend skip.
Founder decision pending before any lexicon change.

### Open / Next
- USER: rotate GITHUB_TOKEN on nowtrendin-v2-engine (steps given in chat).
- Founder: approve/reject the 2 lexicon candidates (reddit, Roman Safiullin).
- source_watchdog github warn clears at the first collect slot after token rotation
  (or degrades gracefully unauthenticated meanwhile).

### Addendum 2026-07-07 — GITHUB_TOKEN rotated + verified (closes warn #1)
Founder rotated to a classic no-scope, no-expiry PAT. Gotcha: the dashboard config-var
field got the ENTIRE command line pasted as the value ("heroku config:set GITHUB_TOKEN=…"),
so auth still 401'd — extracted the embedded 40-char ghp_ token and re-set it cleanly
(engine v214; value never displayed). VERIFIED: /rate_limit HTTP 200, search quota 30/min,
live search probe 200. github collector confirms at the next 6h collect slot.

## Session 2026-07-07 — six agreed fixes shipped (engine v215/27740ae) + ledger truth surfaced

### Shipped + verified live
1. **Grade clamp**: `_num` bounds every AI-returned component to [0,100] (required-key C9
   guard was already present — audit finding stale).
2. **N detail fields FIXED**: /scores/{topic} recomputes queries_30d/24h/daily_rate fresh
   from topic_queries (never persisted in velocity_scores — the "No internal query history
   yet" at N=100 bug + the N-degenerate scoringcontract finding). VERIFIED: coding_agent
   N=73.5 now shows 313 queries/30d with a real narrative.
3. **Observable calibration swallows**: the last two silent apply_calibration except:pass
   (direct-query path + history-row calibrator) now log + stamp calibration_errors.
4. **risk_stage vocab**: verified ALREADY fixed (_RISK_TO_MARKET_TIER at write site).
5. **Legacy weights**: verified ALREADY fixed (calibration_engine imports scoring_weights).
6. **LEDGER first-crossing enrollment + pre-broken segmentation** (held-out,
   measurement-only, no stored rows touched):
   - Enrollment: first-seen ≤ LEDGER_ENROLL_RECENT_DAYS(14) + floor crossing, excludes
     ESTABLISHED/MONITORING (fail-open if topic_maturity absent), newest-crossers-first —
     replaces leaderboard top-N (structurally LAGGED).
   - Report: LAGGED split near-miss vs pre_broken (breakout >7d before first sighting);
     new tracked_race_hit_rate_pct. **First read: 44/59 lagged were PRE-BROKEN cold-start
     rows; tracked-race hit rate 26.9% (7/26) vs blended 10%** — the honest race-level
     read of the before-it-arrives claim. Both rates served; nothing hidden.

### Open / Next
- Enrollment change takes effect at the next enrollment run — watch the pending pool's
  composition shift toward fresh crossers over the coming days.
- Remaining strategic ledger items (not yet built): canonical-query resolution before
  sweeping (the "mexico" ambiguity), second referee corroboration (referee_wikipedia),
  LED-vs-LAGGED detection-time feature mining, GHOST_FEEDS Dark-Matter expansion
  (backtest-gated), positioning floor-pin omission (backtest-gated).
- Founder: lexicon candidates (reddit → tech, Roman Safiullin → sports) still pending.

### Addendum 2026-07-07 — match-validity metadata + feature mining (engine 7ca65c7)
- **Sweep match-validity shipped**: accuracy_ledger + sweep now record sweep_query,
  query_ambiguous (single word / bare geo = weak Trends match), and referee_corroborated
  (INDEPENDENT Wikipedia-pageviews referee on LED/SAME_DAY wins, ±14d of breakout,
  fail-open). /accuracy/ledger serves ledCorroborated/ledUncorroborated/ledUnchecked/
  ledAmbiguousQuery; best[] carries both flags. Existing 7 LED wins honestly "unchecked"
  (resolved pre-metadata). Verdicts/scores untouched.
- **LED-vs-LAGGED feature mining** (read-only, audits/ledger-research/
  LED_FEATURE_MINING_2026-07-07.md): D=0 at first sighting for winners AND near-misses
  but 40 for pre-broken → current Dark Matter is late-confirmation, not early-warning —
  empirical case for GHOST_FEEDS expert/niche expansion. LED median M=80 vs near-lag 50
  (breadth-at-first-sighting separates winners). Median near-miss loss ≈ −4d; 5/15 lost
  by 1–2 days → fast-lane recheck plausibly flips them. Small samples; directional only.

### Open / Next
- Backtest-gated queue (founder sign-off to start): GHOST_FEEDS expert/niche outlets;
  breadth-at-first-sighting enrollment priority; free-source fast-lane recheck;
  positioning floor-pin omission.
- Re-run feature mining when the first-crossing enrollment cohort resolves.

### Addendum 2026-07-07 — Accuracy Ledger PAGE updated (pre-broken + tracked-race + referee), live on gh-pages
- Engine: /accuracy/ledger/detail now serves sweep_query/query_ambiguous/referee_corroborated
  + a SERVER-computed pre_broken flag (one definition, same grace as the report) — 658bdf3.
- Web terminal (deployed gh-pages 93cde0c, bundle index-Bxi-S792.js, verified serving):
  filter chips All/Led/Same day/**Lagged · near miss**/**Pre-broken**/False positive;
  stat strip adds **Tracked-race hit rate 26.9%** beside the unchanged blended Honest 10.0%,
  breakdown 7/4/15/44/0 (near + pre-broken = lagged, nothing hidden), **LED referee check**
  card (0✓ · 0– · 7 unchecked — honest: old wins predate the metadata); PRE-BROKEN verdict
  chips w/ tooltip; wins carry wiki-referee status; ambiguous terms marked "broad term";
  plain-language banner. Integrity-first: honest rate still counts every resolution.
- Verified in preview (temp local auth stub, REVERTED before build/deploy — 0 traces,
  bundle hash identical to clean build): cards reconcile with the API exactly; Pre-broken
  filter → 44 rows, Near-miss → 15; zero console errors. tsc clean.
- Desktop inherits via the web build (§12). ⏳ Mobile parity: the Aurora Accuracy Ledger
  screen still shows the pre-split summary — add trackedRace/near/pre-broken lines +
  /deploy-mobile-preview (next parity task).

### Addendum 2026-07-07 — 3-platform ledger parity COMPLETE (mobile chips + segmentation deployed)
- Mobile (97f1397, preview release 512efb4): Accuracy Ledger screen now has the web's
  chip rows — LEDGER mode (Attention·Trends / Money·Market / Crypto·Coin, lazy-loaded)
  + verdict filters (All/Led/Same day/Lagged·near/Pre-broken/False positive; price
  ledgers Confirmed/Not confirmed/No move) — Aurora pill style, tokens only. Metrics
  add TRACKED-RACE beside blended HIT RATE; honest breakdown + LED-referee lines +
  pre-broken explainer; NEW filterable row list (/accuracy/ledger/detail, windowed 30,
  server-computed pre_broken, wins carry wiki-referee status, 'broad term' markers).
- Deployed via /deploy-mobile-preview: gate + DB-target + new-UI strings verified in
  bundle BEFORE push; live checks pass (PIN page w/o cookie, 401 wrong PIN, app +
  TRACKED-RACE served with cookie). Parity: web gh-pages ✓ · desktop (inherits web) ✓ ·
  mobile preview ✓ — §12/§17 satisfied for the ledger.

### Addendum 2026-07-07 — Ledger Entry Analysis panel (per-row information panel, 3 platforms)
- Engine (9687133): signal_analysis.py gains kind='ledger' (_ledger_entry) — deterministic,
  formula-confidential analysis of ONE ledger row: what the entry records · HOW the tracking
  method works (canonical detection date, Trends curve detection→now, sustained-surge breakout
  vs own baseline [thresholds proprietary], asymmetric match window, 365d patience, independent
  wiki referee) · what THIS verdict means (honest per-verdict copy incl. PRE-BROKEN + excluded
  LATE_REDETECTION) · match validity (broad-term + referee; pre-metadata rows say so) · track-
  record context. POST /analysis/ledger; reads snake_case AND camelCase rows. Live-tested.
- Web (e5f6886 → gh-pages 9126262): click any attention-ledger row → SignalAnalysisPanel
  (kind widened) expands beneath it. Preview-verified: all 5 sections render w/ real facts,
  0 console errors (auth stub reverted before build — 0 traces).
- Mobile (cf26d4e → preview d4539a6): tap a ledger row → same panel; 'Tap for the full entry
  analysis' affordance. Bundle checks (gate/DB/new-string) passed pre-push; PIN gate verified.
- NOTE: deterministic composition per the enterprise standard (reproducible, no model
  inference, no per-view AI cost) — the "AI prompt" ask is satisfied by feeding the tracking
  method into the same held-out analysis engine that powers the trend/market/crypto panels.

### Addendum 2026-07-07 — founder-approved disclaimer EVERYWHERE (verbatim, sign-off required to edit)
New copy: "*All information contained herein may not be accurate including any and all figures
indicated in this section and or site and may be an approximation and should not be construed as
financial, investment, or legal advice."
- Engine (5d1ed35): signal_analysis _DISCLAIMER → all 4 analysis panels (trend/market/crypto/
  ledger) on every platform, no client rebuild needed. Crypto keeps its appended caveat.
- Web (f680a52 → gh-pages ce87964): LEGAL_DISCLAIMER constant + 4 inline copies (Shell footer,
  Crypto/MarketSignal/Screener AI-overview lines). Trend + market rails verified TOP AND BOTTOM
  (2 legal-disc per rail), old text gone site-wide, 0 console errors.
- Mobile (f680a52 + c200e4f → preview 76b8bdf): Disclaimer component + TopicResearch caveat;
  signal/[id] + risk/[key] detail panels now carry it top AND bottom. Bundle check:
  newdisc 2 / olddisc 0 / gate intact.

### End-of-day 2026-07-07 — docs/skills sync + AI-Context root cause (founder to bed)
- **AI Context NOT loading — ROOT CAUSE: Anthropic API account credits EXHAUSTED.** Every engine
  Claude call returns 400 "Your credit balance is too low to access the Anthropic API." Affects
  NEW topic definitions (AI Context) + the Grade tool's Claude synthesis stage; CACHED explainers
  still serve (why some topics show context). NOT the engine budget (Cost Sentinel AI line is
  $0.92/$20 this period) — it is the prepaid balance at Anthropic. FIX (founder):
  console.anthropic.com → Plans & Billing → purchase credits. Recovers immediately, no deploy.
  (Probed all model names with the live key — all 400 with the credit message, so not a model
  retirement; AI_GRADE_CLAUDE_MODEL=claude-sonnet-4-6 as configured.)
- **Docs updated**: CLAUDE.md footer → 2026-07-07 block (ledger truth layer, match validity,
  3-platform ledger UI + entry-analysis panel, hardening, disclaimer, ops, ⚠ Anthropic credits).
  §14 already carried the enrollment/pre-broken rule from earlier today.
- **Skills updated**: /nowtrendin2.0 CURRENT BUILD STATE → 2026-07-07 (+ the Anthropic-credits
  PENDING USER ACTION at the top); /accuracy-sweep report structure → publish BOTH rates
  (blended + tracked-race) + match-validity section + preBroken-vs-laggedNear failure modes +
  ACCURACY_LOG line format extended.
- **Memory saved**: project-ledger-match-validity (first-crossing enrollment, pre-broken split,
  tracked-race, wiki referee, D-is-late-confirmation finding) + MEMORY.md index.
- NOTE: founder's last screenshot showed the OLD disclaimer — that tab was on a cached bundle;
  gh-pages verified serving the new one (hard refresh fixes).

### Addendum 2026-07-07 — Market Signal rail: AI Context section added (712a739 → gh-pages ba66731)
Trend-rail parity (§12): same /explainer source-aware definition, first section under the
score gauges. Preview-verified (renders first, 0 console errors). Shows the honest placeholder
until the Anthropic account credits are restored (then generates on first view + caches).
Optional follow-up: mobile risk/[key] has no AI Context equivalent either — add for full parity.

### RESOLVED 2026-07-07 — Anthropic credits restored, AI Context LIVE
Founder purchased credits. Verified: /explainer generates for both a trend topic
(firm_blackcore) and a market instrument (alphabet — the new Market Signal AI Context
section). Definitions generate on first view + cache; Grade Claude stage restored too.

## Session 2026-07-07 (cont.) — research-outlet onboarding VALIDATED + lexicon verified (engine e32a59c)

### GHOST research feeds — §16 five-gate run + held-out validation (the "backtest")
- **Integrity finding that changed the design:** the generic blog n-gram extractor FAILS the
  FORMAT gate on editorial titles — filler fragments ("gathering clouds building") and NBER
  AUTHOR NAMES ("ulrike malmendier stefan") SURVIVE `_is_quality_topic`, and expert-tier
  signals are EXEMPT from the corroboration floor → junk would enter scoring at the
  highest-trust tier. Shipping as originally designed would have violated the integrity standard.
- **Fix built:** `research_entity_topics()` — entity-anchored extraction (capitalized runs
  holding a non-common-dictionary word; edge-trim floor of 2 words; standalone-proper-noun
  singles only; no entity → write NOTHING). Iterated 3× against live feeds until precision
  ~80%+ (real entities: shin bet, taliban rule, venezuela humanitarian, texas screwworm,
  deterring russia, temu). `_parse_rss` ET fallback made namespace-agnostic (Atom bug).
- **Verdicts:** WoR / Rest of World / Global Issues / RAND **PASS**; **NBER FAIL** (2nd
  documented failure); **Pew FAIL as-is** (Methodology/Acknowledgments sub-pages in feed).
- **Premise test:** 51/59 clean topics NOVEL to velocity_scores — the outlets genuinely see
  what the engine doesn't (matches the D-is-late-confirmation mining finding).
- **Shipped flag-gated OFF** (`GHOST_RESEARCH_FEEDS=0`); founder flips after reviewing
  audits/source-onboarding/RESEARCH_FEEDS_VALIDATION_2026-07-07.md → recommend a 2-week
  monitored trial (topic-quality + catch-all auditors). Rollback = unset the flag.

### Lexicon adds — verified against real data before applying
- **safiullin → sports APPLIED + LIVE-VERIFIED** (roman_safiullin now serves sports): the
  topic's OWN signals are 8/8 tennis (Wimbledon/Guardian Sport/"safiullin tennis"); overmatch
  checks pass (russia/roman empire/saffron unchanged).
- **reddit NOT added — the add would have been redundant:** serve-time `_category_for`
  already returns technology (context/situation layers route it). Verified live before
  touching the lexicon; adding it would have been unverified drift.

## Session 2026-07-07 (Board) — Advisory Board created + branch A-G reviewed, fixed, merged flags-OFF
- **/advisory-board skill created** (6 independent archetypes: Challenger, First-Principles
  Guardian, Expansionist, Outsider VC/Banker, Executioner, Economist w/ founder-specified
  canon — 12/12 source texts access-verified, incl. founder-provided Bogle/Bernstein/R&R/
  Belsky-Gilovich local files; Bogle needs render-to-image, method recorded in the skill).
- **Branch integrity-recs-A-G**: 7 recs implemented flag-gated OFF; six independent board
  memos (audits/board/BOARD_integrity-recs-A-G_2026-07-07.md). Board caught 2 real defects:
  F was a near-no-op (3 stage-write sites) and D's INSERT omitted calibration_multiplier
  (transient inflation). Both fixed per board conditions + Challenger's no-lookahead basis
  + E cooldown + B shadow log + policy stamps.
- **Merged flags-OFF (fe2cefc), deployed (72285bb), zero behavior change verified.**
- **A DECIDED: no reweight** (AUC noise); re-run at ≥30 post-fix races.
- **INVERSION SOLVED**: as_of_detection_days = 0–1 for ~all ledger topics — the 2.3%-vs-24%
  maturity inversion is a hindsight-classification artifact, not a thesis failure.
- D-weight backtest results + D dry-run distribution: 698 EST / 156 EMERG / 80 NEW.
- Remaining: 6 sequenced flag flips = per-item Chairman decisions (listed in board record).

## Session 2026-07-07/08 — ALL SIX CHAIRMAN-AUTHORIZED FLIPS EXECUTED (pre-registered)
Pre-registration doc: audits/board/FLIP_PREREGISTRATION_2026-07-07.md (success metrics,
review dates 07-14/07-21, revert conditions — written BEFORE flipping, per the Economist).
- Preconditions run first: B shadow review (12,851 would-block topics = tag-mash junk →
  the moat exemption was a junk highway; PASSED) · G real before/after diff (32 pinned
  instruments: delta 0.00 everywhere, 0 still pinned, all now honest n/a; PASSED).
- Flipped (engine v222, one restart): E sweep newest slots=2 · C N-dedup 10min ·
  B moat-strict · G positioning quarantine · F stage-from-detection.
- D write: 952 topic_maturity rows (calibration-neutral; coverage 3→76; headline rates
  unchanged 10.0/26.9; tagged rollback).
- F/G announced: "Definition changes" section on Methodology (gh-pages cf70abf).
- Policy stamps live on /accuracy/ledger (paramVersion/sweepNewestSlots/maturityBasis).
- ⚠ 7th decision surfaced to Chairman: LEDGER_MATURITY_AT_DETECTION (early cohort now
  honestly exposes the hindsight artifact: 0/8 EMERGING vs 7 wins in ESTABLISHED).
- Review dates: 2026-07-14 (E/C/G/F), 2026-07-21 (B). Watch: catchall_floor_log after
  the next scoring cycles (B is a major scoring-pool cleanup — expect junk drop).

## Session 2026-07-08 — Board Review #2 complete (execution audit + system-wide feedback)
Six independent memos collated → audits/board/BOARD_system-feedback_2026-07-08.md.
Executioner verified 7/7 flips real in code + live config ("no near-no-op this cycle").
CRITICAL new findings: fabricated ~22%/<9% FP claims LIVE in UI/API (purge first);
nonstationary ground-truth instrument (persist curves per resolution); referee
corroborates breakout-not-lead (+ 7 LED wins unchecked — 1-2h sweep); date_utils
%m/%d/%Y silent locale mis-parse; P self-reference; win definition unpinned;
market/crypto confirm rates need null baseline; G's trend half unshadowed (G-2) +
n/a population reconciliation (G-1); B unmetered while ON (register needed);
7's basis computed live over pruned table (stamp at resolution). Consensus queue of
15 actions awaiting Chairman ruling; 07-14/07-21 review homework pre-registered.

## Session 2026-07-08 (cont.) — Chairman-ruled fixes 1-6 + GHOST flip executed (engine 4a31fc7/v226, gh-pages cc8a6cb)
Chairman clarifications RECORDED in the Board's permanent ground rules: (a) P = persistence
of EXTERNALLY-collected signals (composite-legitimate) vs N = platform-internal (excluded);
(b) calibration = accuracy-tuning against real data, never "manipulation".
1. **FP-claim purge**: fabricated ~22%/<9% strings removed from detector payload,
   market_signal_engine, nowtrend_integration (+docstrings), web Screener gauges
   ("speed · early / leading read" / "precision · corroborated read"). Mobile was clean.
   Verified live: fields gone from /scores/{key}.
2. **Referee fixed to corroborate the LEAD** (wiki arrival BEFORE detection = contradiction)
   + SWEEP RUN on all 11 wins: **1 corroborated (Daveigh Chase, same-day) · 7 not
   corroborated (incl. mexico +17d, court rulings +16d — no matching wiki arrival) ·
   3 unresolvable**. Served live: LED wins now read 0✓/5–/2·, 5 ambiguous-query.
   HONEST READ: no LED win currently carries independent corroboration — the
   Challenger's ambiguous-term warning was correct. (Referee limitation noted:
   steady-state wiki pages never "arrive"; uncorroborated ≠ proven false.)
3. **Trend-side quarantine diff**: 6000 stored rows scanned — ZERO NULL components →
   the trend path is empirically INERT; no flag split needed (G-2 closed with data).
4. **Basis stamps**: at_detection_days + pre_broken columns added; sweep stamps at
   resolution; 76 existing rows backfilled; report prefers stamps (pruning-proof);
   paramVersion now calib-params-v3|patience365|lead365|match30|preb7|estmin14 (live).
5. **moat_blocked_log register**: every strict/shadow block persisted; unblocked_at
   stamps delay; 90d age-out; B's revert condition now falsifiable.
6. **date_utils locale fix**: US-canonical slash parsing; unambiguous EU day>12 accepted
   + normalized; ambiguous refused → quarantine. 9/9 tests.
9. **GHOST_RESEARCH_FEEDS=1 flipped** (pre-registered #8; v226) — 2-week monitored trial.
Reviews: 07-14 (E/C/G/F/7 + G-1 reconciliation + D-1 enrollment measure), 07-21 (B + feeds).

## Session 2026-07-10 — Catch-All EOD board review + frozen-panel attribution (engine v227/v228/v229)
Convened the full 6-archetype advisory board on the daily Catch-All EOD report
(audits/board/BOARD_catchall-eod_2026-07-10.md). Unanimous: REJECT the report's two
headline framings — "33.6% baseline" (confounded) and "157 misclassified tracked calls =
HIGHEST priority" (display-only, non-Latin unclassifiable by construction, never touches
score/ledger). Chairman ruled (a)+(b).

### (a) SHIPPED
- broadcom->technology in _LEX (verified: Technology 0.75, no overmatch). القدم CUT
  (overmatch). Native-script terms deferred (pending _demojibake fix + 07-14/07-21 reviews).
- Ratified no-ops #3 hold bare countries / #4 no floor purge / #5 fragment noise.

### (b) BUILT + RUN — /monitor/catchall/attribution (read-only, non-circular, held-out)
Frozen-panel decomposer: real catchall_floor_log trajectory + first-seen cohort split
(the frozen panel, survivorship-caveated) + Latin/non-Latin script split + persisted fixed
panel for forward comparability. Findings:
1. The 70->34 drop happened 07-06->07-07, BEFORE the 07-08 B-moat-strict flip (which moved
   it only 38.3->34.7). So the board's "junk-purge composition" hypothesis is NOT supported.
2. It's real CLASSIFIER MATURATION: warm cohort split = pre-flip 22.0% vs post-flip 43.0%
   (older topics better-classified; overrides accrue with topic age via the situation/
   context maps + the 07-05/06 lexicon drain). Not composition.
3. CONFOUND none of the board caught: _category_for reads in-memory override maps that reset
   EMPTY on every deploy and rebuild ~4-5min later (context ~69k entries). Cold=bare lexicon
   =~68%; warm=~33%. My own 2 deploys swung the auditor 33.6->68.5->33.4 (logs: context
   refresh 06:29:18 is the lever). Tool now self-reports override_maps.warm + COLD verdict
   (<5000 ctx entries) so a post-deploy reading is never misread. Also implies /scores serves
   mostly "General" for ~5min post-deploy (display-only UX dip).
4. Non-Latin = 3.1% of catch-all mass (65/6000 window) -> confirms "demote the 157" ruling.
NET: the ~74->~33 improvement is largely REAL (layered classifier + lexicon), NOT the 07-08
purge; the absolute number is NON-reproducible (warmth+denominator) -> never publish
externally; frozen panel (warm baseline 33.4% over fixed 6000 keys) isolates future change.
v229 = warmth self-check + CLASSIFICATION-MATURATION verdict + ASCII output.

### Board backlog surfaced to Chairman (still pending from the 07-08 review queue)
Done earlier: queue #1-6 + #9 (FP purge, referee fix, trend quarantine diff, basis stamps,
blocked register, date locale, GHOST flip). STILL PENDING Chairman ruling: #7 naive-baseline
ledger column; #8 bundle (FP-timeout caveat, win-definition pin, stage-vocab reconcile,
Wilson CIs); #10 persist Trends curves + LED re-validation (the CRITICAL nonstationary
instrument); #11 fast-lane recheck; #12 lang/region provenance stamps on ingest; #13 null-
baseline market/crypto ledgers; #14 P self-reference re-grounding; #15 housekeeping (weight-
literal dedup, entity-level extraction "Haaland gap", Postgres tier date, DB_DATA_DICTIONARY
regen). Scheduled reviews: 07-14 (E/C/G/F/7 + G-1/D-1) and 07-21 (B + GHOST feeds).
NOTE: today's non-Latin finding maps to pending #12 + #15 (entity extraction) — raised 3x now.

## Session 2026-07-11 — Warm/cold override-map refresh: writer-guard + warm-on-boot snapshot (engine v227→v232)
Two board reviews + implementation, all Chairman-ruled. Board records:
audits/board/BOARD_catchall-eod_2026-07-10.md and BOARD_warm-cold-refresh_2026-07-10.md.

### Catch-All EOD board review (six archetypes) → broadcom + frozen-panel attribution
- SHIPPED broadcom->technology in _LEX (verified no overmatch); القدم CUT (overmatch);
  no-ops #3/#4/#5 ratified.
- BUILT /monitor/catchall/attribution (read-only, non-circular): real floor-log trajectory
  + first-seen cohort split (frozen panel) + Latin/non-Latin script split + persisted fixed
  panel. FINDING: the 70->34 drop happened 07-06->07-07 (BEFORE the 07-08 B-moat-strict
  flip, which moved it only 38.3->34.7) => real CLASSIFIER MATURATION (warm cohort: pre-flip
  22% vs post-flip 43%; overrides accrue with topic age), NOT the junk purge. And the metric
  is DEPLOY/WARMTH-sensitive: cold=~68% (bare lexicon) vs warm=~33%.

### Warm/cold refresh board review (six archetypes) — the mechanism + fix
- RESEARCH (code-inventory agent, file:line-cited): SCORING + all 3 LEDGERS are INSULATED.
  /scores serves stored serve_payload; stale rows serve stored verbatim (INV-1); the
  scoring-admission gate uses the STATELESS import-time lexicon (_topic_category), NOT the
  cold _category_for maps (non-circular design); ledgers DB-driven/restart-safe; market/
  crypto have zero cold state. Confound confined to DISPLAY category + the catch-all metric.
- CHALLENGER found the exposure the inventory missed: catchall_auditor (the WRITER) had NO
  warmth guard -> persisted cold ~68% rows to catchall_floor_log + could trip a FALSE
  WORSENING floor alarm. CONFIRMED LIVE (self-inflicted): 2 cold rows written by this
  session's own cold auditor calls.
- Board decision table: writer-guard MANDATORY; A(metric guard)+F(leave serve path) the
  substance; D(readiness gate) REJECTED 6-0 (wedged-prewarm outage class); E(prewarm-sync)
  CUT (Executioner: daemon already refreshes on boot -> compute-bound, no latency to capture);
  B/C split (Outsider/Economist reject as gold-plating; Expansionist: C is scale-correct;
  Guardian: display-only under firewall). Economist prescriptions: refuse-when-cold, fixed
  panel as series-of-record (built), condition-stamp, build-test vs bare-lexicon, demote
  catch-all below the ledger, generalize the warmth audit.

### Chairman ruling + IMPLEMENTATION (v231/v232)
1. WRITER-GUARD (mandatory): catchall_auditor skips the catchall_floor_log INSERT +
   suppresses WORSENING/leak/misclass alarms when the context map is cold
   (<CATCHALL_WARM_CTX_MIN=5000); fragment_category_auditor suppresses its >=70% alarm cold.
   Verified: cold=0 rows written+no alarm, warm=persisted.
2. WARM-ON-BOOT SNAPSHOT (Chairman: Camp 2 + Camp 3): new category_override_snapshot table;
   each live _refresh_* persists its map (_persist_category_snapshot); startup loads it
   SYNCHRONOUSLY before serving (_load_category_snapshot) -> _category_for warm-on-boot, no
   ~5-min/~2100-topic 'General' flicker. DB-persisted => fleet-consistent. Flag
   CATEGORY_SNAPSHOT (default on). DISPLAY-ONLY, never wired into scoring.
3. OLD-vs-CURRENT distinction (Camp 3): _CAT_MAP_META tracks per-map source
   (empty|snapshot|live) + refreshed_at stamp; surfaced in override_maps + auditor summary.
4. /monitor/catmaps: FAST (no topic scan) warm/cold + snapshot-provenance status +
   ?clean_poisoned=1 cleanup. Added because /monitor/catchall + attribution H12 under load
   (pre-existing auditor corroboration-pass cost, borderline vs the 30s router limit).
- REJECTED D, CUT E per the board.

### VERIFIED (real system behavior, not approval-gap time)
- Warm-on-boot PROVEN: v232 booted and served the context map from the persisted snapshot
  immediately -> /monitor/catmaps: warm=true, context.source="snapshot" (68264 entries,
  stamp 18:56), situation.source="live". snapshot_table holds both maps. Feature works E2E.

### ⚠ OPEN — poisoned-row cleanup OVER-DELETED (founder decision pending)
?clean_poisoned=1 deleted 3 rows, not 2 (cutoff pct>=60 AND logged_at>=2026-07-06 was too
aggressive). Deleted:
  - 2026-07-11T06:28:49.999900+00:00  pct=68.5  (4108/6000)  <- genuinely cold (v228 boot)
  - 2026-07-11T06:43:04.005954+00:00  pct=68.5  (4110/6000)  <- genuinely cold (v229 boot)
  - 2026-07-06T01:59:03.809775+00:00  pct=67.8  (4067/6000)  <- PROBABLY LEGITIMATE: this
    session's own board analysis treats the 67.8%->38.3% (07-06->07-07) drop as real
    classifier MATURATION, i.e. the catch-all genuinely WAS ~68% then (pre context-map
    maturation), so this was likely a warm historical reading, not poison.
Impact bounded: catchall_floor_log is the display-only monitoring gauge (demoted below the
ledger; NO score/ledger effect). RESTORABLE fields recorded above (single_source_leak +
misclassified_tracked were NOT in the prior trajectory read -> would be NULL on restore, not
fabricated). DECISION PENDING: (a) restore the 07-06 row + tighten endpoint FLOOR
2026-07-06 -> 2026-07-09 (so cleanup can only touch unambiguously-cold rows), or
(b) leave deleted + document + tighten. Recommended: tighten regardless; lean restore.

### Env / ops
- New/relevant env: CATEGORY_SNAPSHOT (default 1), CATCHALL_WARM_CTX_MIN (5000),
  CATCHALL_FLIP_CUTOFF (2026-07-07), CATCHALL_PANEL_AGED_CAP (2000).
- Engine versions this session: v227 broadcom+attribution · v228 perf(single-pass) ·
  v229 warmth self-check · v230 cold early-return(fix H12) · v231 writer-guard+snapshot ·
  v232 /monitor/catmaps.
- KNOWN: /monitor/catchall + /monitor/catchall/attribution H12 under load (heavy warm
  decomposition ~25s / auditor corroboration pass). Use /monitor/catmaps for a fast
  warm/cold + provenance read. Consider moving the heavy auditor off the 30s router
  (background job -> stored result) as a follow-up.
- INTEGRITY NOTE on measurement: never publish catch-all % externally as an accuracy KPI;
  it swings with override-map warmth + moving denominator + scoring-cycle phase. It is a
  congestion gauge, demoted below the accuracy ledger.

### ✅ RESOLVED 2026-07-11 (cont.) — 07-06 row restored + cleanup tightened (engine v233, founder-ruled: restore+tighten)
- Restored the over-deleted 2026-07-06T01:59:03 row (67.8%, 4067/6000, min_sources=2; the two
  unrecovered sub-fields single_source_leak/misclassified_tracked stored NULL, not fabricated)
  via idempotent INSERT OR IGNORE — verified restored_2026_07_06=True.
- Tightened /monitor/catmaps clean_poisoned FLOOR 2026-07-06 -> 2026-07-09 (warm there is
  ~33-35%, so >=60% is unambiguously a cold-boot artifact). Re-ran cleanup: poisoned_found=[],
  poisoned_deleted=0 -> no residual poison, 07-06 row protected (before the floor).
- Engine confirmed warm-on-boot from snapshot (context.source=snapshot, warm=true). Open item
  from earlier this session is CLOSED.

## Session 2026-07-14/15 — Aurora PR#1 merge + zombie-query outage fix (engine 1238fe0 + 98f4a15)

### Completed
- Reviewed + merged PR #1 (jose-sandbox, Aurora front-end: Market #1 hero, tab intros,
  full-bleed responsive, orientation unlock — front-end only, fields/imports verified).
  Redeployed nowtrendin-v2-preview with the merged bundle (gate + hero verified live).
- **ROOT-CAUSED the cold trend feed (20s+ loads / 503s):** queries had NO
  statement_timeout, so each dyno restart turned in-flight GROUP-BY scans into immortal
  server-side ZOMBIES (one ran 19.8h). Zombies convoyed every /scores build → prewarm
  cycles took ~5h vs the 30-min cache TTL → trend feed served cold nearly all day;
  mobile fell back to the 10-row offline sample dataset ("live engine unreachable").
- Fixes shipped (read-path only, no scoring/data change):
  (1) db_compat: statement_timeout (PG_STATEMENT_TIMEOUT_MS=300000) + TCP keepalives +
      connect_timeout (PG_CONNECT_TIMEOUT_S=10) on EVERY conn (pool + direct) — the
      zombie class is now impossible (any query dies at the cap; error visible, retried).
  (2) /prewarm wedge visibility: in_flight_since + in_flight_feed + per-feed secs in
      warmed[] — distinguishes "never ran" from "wedged N min into scores".
  (3) _x_candidate_topics conn.close() → try/finally (leak on error).
  (4) Merged the MAX+MIN double GROUP-BY into ONE aggregation pass in the /scores
      build AND the x-scan base (identical semantics; the x-scan ran its base 3×/cycle
      = 6 full-table aggregations). Measured: scores candidate query ~250s+ → 31s.
- Terminated 14 zombie SELECTs directly via psycopg2 (heroku pg:kill needs local psql —
  broken on this box; scratchpad script, kills only active SELECTs >6min, which post-fix
  can only be pre-deploy orphans).
- VERIFIED: full warm cycle 257.7s (was ~5h) — scores 2960 rows/176s, topics 4s,
  history 2s, risk 0.1s, crypto 15s; /scores HTTP 200 in 0.75s with live data.

### Open / Next
- Watch scores-build secs in /prewarm warmed[] — 176s is inside the 300s ceiling but
  monitor under scoring-cycle load; if it creeps, next lever is bounding the aggregation
  to the recent working set or a maintained first/latest-per-topic table.
- history:12h warms 0 rows when the last scoring cycle is >12h old — honest, not a bug.
- velocity_scores = 2.15M rows / 2.15GB on essential-1 (RED cache hit 0.975) — the §13
  Postgres tier upgrade gets more urgent as the 365-day tail fills.

### Hard decisions made
- statement_timeout default 300s, env-tunable: finiteness beats an unbounded query; a
  legitimately-slower statement fails VISIBLY and retries next cycle (accuracy principle:
  a visible error beats silent staleness).

### 2026-07-15 (cont.) — /topics parity + mobile Market web-parity (preview 0e16efb)
- **Platform parity FIXED (engine e514679 + e1a4877):** /topics grid now draws from the
  SAME universe as /scores (same latest-row source, 5000 cap, mentions floor, noise
  filter, tie-breakers). Verified live: topics total = scores total = 2960 exactly
  (was web 1891 vs mobile 2960 — the old registry scan was hard-capped at 2000).
- **Mobile market-category crash FIXED:** [key].tsx imported laneOf + MARKET_LANES from
  marketCategories.ts which did NOT exist (undefined.find() TypeError on every category
  tap incl. ALL). The three Market filter axes now live in marketCategories.ts as SSOT.
- **Mobile Market = web parity:** dashboard Market tab now has the web's three in-place
  filter rows (LANE w/ counts · TIER incl. Watch/Unusual + Leverage≥60 · DIRECTION),
  defaults 'all' on every axis, combining with search; nav-chip row removed. Headline
  under the greeting is mode-aware (market count "Moving!" on Market tab). Preview
  redeployed + bundle verified (gate intact, new chips in served JS).

### 2026-07-15 (cont. 2) — mobile/web SORTING alignment, all sections (preview 7530d30)
- Trends: CATEGORY_DEFS carry the web's per-view rank (Now TrendIn→N, All Signals +
  stage tiers→Detection); mobile default view = Now TrendIn (web default); hero +
  TrendCard number follows the ranking metric (N label on the N-ranked view); stage
  pages use the same def sort. nowtrendin def copy corrected (N = platform tracking).
- Market: mobile list + hero rank by MONEY MOVEMENT desc (web table default), not the
  positioning feed order; RiskCard collapsed = tier + MM (Money Gradient frame), the
  positioning/classification read moved to expanded detail.
- History: verified aligned (both recency-desc). Crypto: mobile has NO crypto section
  (parity gap — flagged to founder as its own build; web renders engine roster order).

### 2026-07-15 (cont. 3) — mobile CRYPTO section built (preview 0cfb118, web parity)
- New Crypto tab on the mobile dashboard between Market and Grade (web sidebar order).
- List (web Crypto page parity): DIRECTION chips All/Inflow/Outflow/Neutral; roster in
  engine-served order (never re-sorted); CryptoCard (Aurora borderless tap-to-expand) =
  name·ticker, tier + flow, MM; expanded MC/Lead/price-7d/interpretation + FULL DETAIL.
- /crypto/[coin] detail = the web rail's EXACT sections in Aurora: header, price as-of,
  disclaimer top+bottom, dual rings (MM sapphire #2A5B9E / MC emerald #2E7D5B — mobile
  market-detail convention), gap state + AI interpretation + AI note, SignalAnalysisPanel
  kind=crypto, Market Factors (bars, feeds colors, ✓ baseline, n/a never NaN, legend),
  Price & Dark Matter facts, what-it-measures explainer.
- useCrypto() polls 4s while the prewarm feed reports 'warming' (web behavior); pull bar
  hidden on Crypto (web has no crypto pull); headline "N Coins Are Moving!".

### 2026-07-15 (cont. 4) — exact trend-order parity (feedRank) + web "All" category chip
- ROOT CAUSE of the residual order mismatch: both platforms rank by N, but N saturates
  at 100 → ties dominate. Web's stable sort inherits the /scores ARRIVAL order (the
  engine's stored sort: overall → mentions → recency); mobile re-derived ties from
  SERVED values (which can differ from the stored sort column) → divergent lists.
- FIX: mobile stamps feedRank (global /scores arrival index) at fetch; feedOrder uses it
  as the primary tie-break (derived chain kept only as mock-data fallback). Mobile now
  reproduces the web's order exactly from the same cache snapshot.
- Web Screener category row gained the leading "All" chip (mobile parity; active when no
  category selected, returns to Now TrendIn). Deployed: gh-pages 9130266 + preview 7e9e635.

## Session 2026-07-15 (cont. 5) — Entity-grouping board review + Chairman ruling

### Completed
- Advisory Board convened on entity grouping / topic-alias consolidation (the
  "conor mcgregor" / "conor" / "mcgregor" triple-BREAKOUT case). Report:
  audits/board/BOARD_entity-grouping_2026-07-15.md (decision table + 7 convergent
  conditions intact; verbatim memo bodies failed extraction — noted in file).
- CHAIRMAN RULING recorded (founder, 2026-07-15): Option A (display-only alias
  layer) APPROVED to build under all seven conditions, flag-gated ENTITY_GROUPING
  default OFF, pre-flip audit-dump review = the measurement gate. B DEFERRED
  (phase-2, gated on A's production evidence). C REJECTED (unanimous). D REJECTED
  standalone. Pre-build read-only items authorized (prevalence audit ·
  family-collapsed ledger sensitivity · fragment-lead study).
- Housekeeping: deleted 07-07 debugging scratch from repo root (bf.json,
  ledger.json, r0/r100/r200.json, risk.json, 0-byte '2026-07-11T06 artifact).

### Open / Next
- BUILD Option A per ruling: entity_aliases DB table (dated/versioned/evidence-
  stamped/confidence-scored, human-confirmed, reversible) + warm-on-boot snapshot
  (CATEGORY_SNAPSHOT clone) + held-out wall in code (never importable into scoring
  admission / calibration / ledger enrollment / sweep) + display-only serve-time
  grouping (canonical row = its OWN score, NO arithmetic merge) + candidate dump +
  confirm/reject endpoints (flag-never-force). Ledger stays per-key everywhere.
  Auditors keep measuring RAW keys. 3-platform parity ships with the flag flip.

### Hard decisions made
- Score-time merge (C) is permanently off the table; extraction-time
  canonicalization (B) requires A's production evidence + splice protocol +
  backtest before it can even be re-proposed.

### 2026-07-15 (cont. 6) — Option A BUILT + DEPLOYED flag-OFF (engine v239)
- transfer/entity_grouping.py (held-out, display-only) + hooks in the monolith:
  entity_aliases table (dated/versioned/evidence-stamped/confidence-scored,
  human-confirmed, reversible, chain-guarded), warm-on-boot map load in startup,
  serve-time fold in /scores + /topics builders (NO arithmetic merge — canonical
  keeps its OWN score + list position; constituent folds ONLY when its canonical
  is visible in the same filtered list), detail entity_group (constituents' own
  scores + de-duplicated raw_signals union labeled as shared), endpoints
  GET /aliases + /monitor/aliasmaps + POST /aliases/scan + /aliases/resolve
  (internal-gated). ENTITY_GROUPING default OFF. 18/18 local behavior tests.
- Held-out wall verified LIVE on v239: zero entity_grouping refs in calibration/
  ledger/sweep files (/monitor/aliasmaps wall_check ok).
- EXHAUSTIVE candidate sweep run (2,068 containment pairs over the raw 3,049-key
  working set; no silent cap): 561 evidence-corroborated pending candidates in
  381 families → audits/entity-grouping/ALIAS_CANDIDATES_2026-07-15.md (the
  pre-flip measurement gate). PREVALENCE ANSWER: families number in the HUNDREDS.
- Founding case captured: conor(0.921, 27 shared titles) + mcgregor(0.852, 20)
  -> conor_mcgregor.
- HONEST CAVEAT in the dump: many proposed "canonicals" are themselves headline
  fragments (lindsey_graham_sudden, spain_kill) — the directionality heuristic
  (longer key = canonical) is a proposer, not a decider; human review is load-
  bearing exactly as the board required. Reject freely; rejects are reversible.

### Open / Next (Option A)
- FOUNDER: review audits/entity-grouping/ALIAS_CANDIDATES_2026-07-15.md, confirm/
  reject via POST /aliases/resolve, then set ENTITY_GROUPING=1 to flip the fold.
- 3-platform frontend parity (grouped rows + entity_group detail section) ships
  WITH the flag flip, per board condition 7 — not before.
- Family-collapsed ledger sensitivity line + fragment-lead study (read-only,
  authorized) still pending as separate work.

### 2026-07-15 (cont. 7) — Founder batch ruling EXECUTED: 51 confirmed, fold live at scale
- Judged review of all 559 pending candidates delivered (4 parallel strict entity-
  identity reviewers; multi-family aliases demoted; recommendations only):
  audits/entity-grouping/ALIAS_REVIEW_JUDGED_2026-07-15.md — 49 confirm / 38
  judgment / 472 reject.
- FOUNDER RULING (verbatim intent): confirm all 49 recommended; reject the 472
  recommended rejects AND the 38 needs-judgment rows. Executed via /aliases/
  resolve, decided_by="founder (batch ruling 2026-07-15)": 49/49 confirmed,
  510/510 rejected, 0 failures. All decisions reversible (revert).
- Final live state (v240): fold ON, 51 confirmed aliases (incl. conor+mcgregor),
  0 pending, 510 rejected, held-out wall OK. Served /scores total 3095 with
  grouped families visible (sam_neill<-neill, jannik_sinner<-sinner,
  jurassic_park<-jurassic, goldman_sachs<-goldman+sachs, warren_buffett<-buffett,
  fifa_world_cup<-world_cup+fifa_world, erling_haaland<-haaland+erling, ...).
- Web-terminal parity source committed (0adf3ca) but NOT yet deployed to
  gh-pages; mobile (Aurora) parity not yet built — awaiting founder go.

### 2026-07-15 (cont. 8) — Entity Group parity DEPLOYED on all 3 platforms
- WEB TERMINAL live (gh-pages 30c6255, bundle index-HezdPg97.js verified): screener
  grouped-entity badge (⊞ count incl. canonical, amethyst) + detail-rail Entity Group
  section (constituents' OWN det/conf + stage, evidence note, de-duplicated shared-
  evidence sample; constituent details point to canonical). Stale gh-pages bundles
  pruned (9 old asset files removed). Desktop inherits the web build.
- MOBILE live (preview 1421a48, Aurora): entityGroup mapped in gradientApi (server
  folds — feedRank stamping untouched; mock fallback safe); Signal/EntityGroup types;
  TrendCard amethyst ⊞ chip + expanded constituent rows (own DET/CONF, "never
  combined" note); signal/[id] "Entity group · N topics" Section with per-constituent
  own scores + evidence note. Bundle verified: gate 1 / backend 1 / engine 1 /
  GROUPED ENTITY UI present; PIN gate intact (401 wrong pin, app behind cookie).
- All source on origin main (0adf3ca web, 6b10db2 mobile). No branches were open —
  "merge branches" = everything already on main, deployed from there.

### 2026-07-15 (cont. 9) — Branch cleanup + outstanding tasks completed
- BRANCH RESEARCH + CLEANUP: all 3 feature branches were 0 commits ahead of main
  (nothing to merge). jose-sandbox = Jose Reyes's Aurora PR #1, MERGED 07-15;
  integrity-recs-A-G + ui-consistency-migration fully merged. Deleted all three on
  origin + the stray ui-consistency-migration on heroku-v2engine + local copies.
  Remaining branches: main + gh-pages (deploy artifact — keep) only.
- STUDY A (family-collapsed ledger sensitivity, read-only): 0 confirmed families
  have >1 resolved ledger row -> collapsed rates IDENTICAL to raw (blended 9.5%,
  tracked-race 25.0%); correlated-win effect currently ZERO. Re-run as families
  accumulate resolved members. audits/ledger-research/FAMILY_COLLAPSED_LEDGER.
- STUDY B (fragment-lead, read-only): of 46 usable families, fragment first-seen
  EARLIER in 17 (up to +31d, e.g. alcatraz +23d), same-day 22, later 7; median 0.
  Fragments lead in a meaningful MINORITY, not systematically — supports keeping
  fragments alive as occasional early signals (anti-D evidence) while grouping
  display. audits/ledger-research/FRAGMENT_LEAD_STUDY_2026-07-15.md.
- Lexicon: reddit -> technology weak list applied (07-07 worklist; youtube/whatsapp
  precedent); safiullin was already in (07-07). Engine deployed (8fbe6f3), healthy.
- Founder-gated queue REMAINING (not mine to flip): GHOST_FEEDS flag, Postgres tier
  upgrade (2.15GB/365d tail), Heroku cost trims (frozen-1.0 DB, nowtrendin-web),
  Apify Scale->Starter downgrade, Guardian/Reddit API keys.

### 2026-07-15 (cont. 10) — GHOST_RESEARCH_FEEDS flipped LIVE (founder-ordered)
- Pre-flip ADVERSARIAL RE-VERIFY on live titles caught 3 real extractor defects that
  the 07-07 validation-era code let through TODAY (they'd have entered the
  corroboration-floor-EXEMPT expert pathway): (1) curly-apostrophe contractions
  anchored junk runs ("size doesn't"); (2) RAND "Q&A with <staff>" titles extracted
  STAFF NAMES — the NBER author failure mode; the &amp; entity's ';' split segments
  mid-marker and hid it; (3) inflected common words passed the dictionary test
  ("loops","fractures","restoring" anchored "empty loops"-class junk).
- FIXES in blog_collectors.research_entity_topics (4e1cd08): contraction suffixes
  never entity-anchor; HTML-unescape before segmenting + drop Q&A segments;
  de-inflection stem check; Title-Case edge-trim reduces style pairs to the real
  entity ("Breaking America"->america, "NATO Unity"->nato) while SENTENCE-case
  proper-noun pairs ("the Shin Bet") never trim below 2 (no name mutilation).
  Verified: live 32-title sample clean (residual singles face the scoring fragment
  gate); regression cases pass; generic GHOST_FEEDS path untouched.
- FLIPPED: GHOST_RESEARCH_FEEDS=1 (engine v242). CONFIRMED LIVE in logs, two cycles:
  "[Ghost RSS] 11 expert blog feeds (+research outlets)" — WoR 74 / RoW 6 / GI 4 /
  RAND 12 articles/cycle at expert tier (Dark Matter D pathway).
- MONITORED TWO-WEEK TRIAL now running (per the validation doc): watch topic-quality
  + catch-all auditors (fragment count, single-source leak) + ghost counts; the
  weekly /improve-system audit covers it. Roll back = unset the flag (no cleanup
  needed). Re-run LED feature mining after the cohort accumulates. CLAUDE.md §15
  updated to LIVE.
- Noted (separate task chip): recurring "[market_signal] record error
  (a_k_a_brands...): float(None)" in engine logs — pre-existing, unrelated.

### 2026-07-15 (cont. 11) — market_signal record error FIXED (e1469c2)
- Root cause: record_market_cycle ran float(val) on every component, but
  positioning_concentration is legitimately None when FINRA + WhaleWisdom are both
  unavailable (documented at the builder; the SERVE path handled None, the history
  recorder didn't). float(None) threw AND aborted the loop — the item lost its
  entire cycle of component baseline history (recurring "[market_signal] record
  error (a_k_a_brands...)" each cycle).
- Fix: absent (None) components record NOTHING (never a fabricated 0 — §17 / the
  no-fabrication principle; a zero would poison that component's baseline); the
  remaining components record normally. Behavior-tested (None skipped, 3/3 others
  recorded, no error line). Deployed; engine healthy. Watch: the error line should
  be absent from the next market cycle's logs.

### 2026-07-16 — Full health check + founder rulings (quarantine · Apify plan)
- FULL SWEEP (all green): engine/backend/terminal/preview UP; 7/7 monitor agents ok,
  0 alerts; collectors 16 healthy / 1 degraded (reddit = the known deferred-keys
  item) / 0 down; prewarm full cycle ~146s; catmaps WARM (live, 65,303 ctx);
  alias fold ON (51 confirmed, wall ok); last cycle scored 5,439 topics + 371 risk;
  ghost research outlets collecting every cycle; ledger blended 9.5% / tracked-race
  25.0% / 1,136 pending (rolling); Cost Sentinel $531.90/$700 — BACK UNDER CAP
  (was $718.82 CRITICAL 07-06; Apify clock-slot fixes landed). market_signal
  float(None): zero error lines post-fix (pre-fix it hit multiple warrant/microcap
  instruments each cycle).
- QUARANTINE RESOLVED (founder-ruled): all 13 pending Nasdaq Trade Halt dates were
  US MM/DD/YYYY -> resolved to canonical YYYY-MM-DD via /quarantine/dates/resolve
  (13/13, 0 failures; format_rules learned -> future identical inputs auto-apply).
  /monitor/datecanon back to OK (14 columns, 0 non-canonical, 0 pending).
- APIFY PLAN DECISION (founder-ruled, console-verified): STAY ON SCALE $199 / keep
  $ unchanged. Real numbers: $34.89 in 9 days (~$3.9/day -> ~$116/mo projected;
  Actors $26 + Proxy $8.30) vs $199 prepaid — but a Starter downgrade is NOT
  viable: projected usage exceeds Starter's included usage and its higher unit
  rates + lower limits would eat the gap as overage and risk the 4-slot bursts.
  Prior-period invoice confirmed the fix worked ($221.90 usage / $316.90 total
  Jun-Jul vs ~$116 projected now). Memory updated (project-ledger-sweep-apify).
- Standing: GHOST_FEEDS two-week trial monitoring continues (weekly improve-system
  audit covers it). Remaining founder-gated queue unchanged: Postgres tier upgrade,
  frozen-1.0 DB + nowtrendin-web trims, Guardian/Reddit keys, Stripe/push at
  store publish, Aurora vs CLAUDE.md §3/§11 palette reconciliation.

### 2026-07-16 (cont.) — 1.0 DATABASE researched: transfer NOT needed (already done at split)
- Founder asked whether the frozen 1.0 Postgres can transfer to 2.0. Full research:
  1.0 repo docs/schema (read-only agent) + READ-ONLY live inspection of BOTH DBs +
  the freeze/consolidation MDs. Report: audits/infra/V1_DB_ASSESSMENT_2026-07-16.md.
- KEY FINDING: v2's DB WAS CREATED 2026-06-15 AS A pg:copy OF 1.0 — v2's earliest
  velocity row (06-04T23:03:02) is one second after 1.0's first row; 265,863
  pre-split rows still retained in v2 (365d rule). Everything durable transferred
  at the split and v2 maintained it better since.
- 1.0 DB reality (10.8GB/28 tables): 91% = velocity_scores 9.7M rows spanning ONLY
  2026-06-04->07-02 (30-min cycles, no pruning); raw/topic signals last 7 days
  only; accuracy_ledger = 6 rows ALL LAGGED. LORE CORRECTION: "pre-April-2026
  data" in the freeze docs is wrong — nothing predates 2026-06-04 in this DB.
- Unique-to-1.0 = only the 06-15->07-02 parallel tail from the frozen engine:
  duplicative (v2 scored/collected the same weeks itself) + integrity-hazardous
  to import (different calibration epoch -> comparability break; leaderboard-era
  pendings -> ledger denominator pollution). Full transfer also physically
  impossible (10.8GB > v2's 10GB essential-1 cap, 32.5% used).
- RECOMMENDATION (awaiting founder ruling): no transfer; pg:backups capture +
  DOWNLOAD the dump (backups vanish with the add-on), then the standing -$20/mo
  essential-2 delete can proceed.

### 2026-07-16 (cont. 2) — BOARD convened on 1.0-DB disposition; assessment corrected mid-review
- Six independent memos (identical evidence pack; full bodies embedded verbatim in
  audits/board/BOARD_v1-db-disposition_2026-07-16.md — fixed the 07-15 extraction gap).
- UNANIMOUS: Option A (verified archive dump -> delete) approved w/ conditions
  (Executioner: SHIP); C (selective transfer), D (full transfer), E (status quo)
  REJECTED by all six. B (keep paying) rejected by 4, tolerated-as-dominated by 2.
- The Challenger/Outsider attack on "v2 already has everything durable" was TESTED
  MID-REVIEW and CONFIRMED: 1.0 holds 934,203 pre-split rows, v2 retains 265,863
  (~28%); PK sample 282/1000. Assessment corrected in place (⚠ CORRECTION section).
  The 1.0 DB is the only complete original of the pre-split record — the verified-
  archive conditions are load-bearing.
- Convergent conditions: test-restore before delete · two checksummed copies, two
  failure domains · epoch-stamp the 06-15 engine boundary in v2 (metadata-only, never
  publish blended rates across it unsegmented) · manifest + provenance README + signed
  disposition record · standing import ban (scratch-restore only) · founder executes
  the destroy · retirement runbook · non-destructive steps NOW (zero backups exist).
- AWAITING CHAIRMAN RULING per option.

### 2026-07-16 (cont. 3) — 1.0 DB ARCHIVED + VERIFIED (board conditions met; destroy awaits founder)
- Non-destructive sequence executed per the unanimous board ruling: exact manifest
  (28 tables, 13,043,952 rows) -> Heroku capture b001 (777.87MB, 93% compression of
  10.77GB) -> downloaded (815,657,151 bytes, size-exact) -> SHA-256
  5961B001...C785D00D -> two copies, two failure domains (local + OneDrive; first
  OneDrive hash raced sync ingest — re-read matched; lesson: re-hash after settle)
  -> TEST-RESTORE to scratch essential-2: 28/28 TABLE COUNTS EXACT MATCH ->
  scratch destroyed. Original DATABASE_URL add-on untouched.
- Signed disposition record + reusable datastore-retirement runbook:
  audits/infra/V1_DB_DISPOSITION_RECORD_2026-07-16.md. Standing rules in force:
  import ban (scratch-restore only), 06-15 epoch boundary (stamp pending), lore fix.
- FOUNDER'S FINAL STEP (reserved, flag-never-force):
  heroku addons:destroy postgresql-shaped-41629 -a nowtrendin --confirm nowtrendin
  then COST_HEROKU_USD 112->92 on the engine.

### 2026-07-16 (cont. 4) — SEGREGATION VERIFIED: live www.nowtrendin.com vs 1.0 Heroku DB
- Founder surfaced that www.nowtrendin.com is LIVE (the previous app, pre-April-2026
  data) and asked for segregation before the 1.0 DB retirement. VERIFIED total
  physical segregation: the domain resolves to an external AWS EC2 (54.160.174.150,
  nginx/Ubuntu) — NOT Heroku; no custom domain on any of the 6 Heroku apps; 1.0 DB
  has 0/40 connections + newest row 2026-07-02; 50-column sweep shows ZERO
  previous-app rows (the only pre-April VALUES are source-carried historical dates
  ingested 06-04+ by the June engine, + calibration/backfill seeds).
- CONSEQUENCE: destroying postgresql-shaped-41629 cannot affect the live site; no
  data movement needed. SEGREGATION VERIFICATION appended to
  audits/infra/V1_DB_DISPOSITION_RECORD_2026-07-16.md; the "pre-April-2026" freeze
  lore fully explained (it referred to the external server's data).
- CAUTION flagged to founder: the EC2 app's own DB backup posture is unknown/out of
  reach — verify that server has its own dump routine.

### 2026-07-16 (cont. 5) — 1.0 DB RETIRED (founder-executed) — retirement COMPLETE
- Founder personally destroyed postgresql-shaped-41629 (flag-never-force honored).
  Verified: no add-ons remain on the nowtrendin app. COST_HEROKU_USD 112->92 set
  (engine v244, healthy). The verified archive (2 checksummed copies + manifest +
  28/28 restore-verified dump) is the sole surviving copy of the 1.0 record.
  Disposition record marked EXECUTED. Board conditions all satisfied; import ban +
  epoch-boundary rules remain in force. Live www.nowtrendin.com unaffected
  (external EC2, verified segregated).

### 2026-07-16 (cont. 6) — Aurora web redesign: built, board-reviewed, rev 2 staged
- Branch aurora-web-redesign: token-level Aurora retheme of the terminal (Jakarta,
  white canvas, borderless cards, jewel stages, midnight chrome, ink pills, Title
  Case; flows byte-identical; banned palette purged). Staged on nowtrendin-terminal;
  gh-pages prod untouched.
- DESIGN BOARD (6 memos, 3 verified staging live): direction unanimous-positive;
  CONVERGENT DEFECT found + fixed same-day (rev 2): garnet was double-booked as
  emphasis AND loss/error (~17 semantics; positive deltas rendered red) -> one
  meaning per hue (red=loss/alarm only, emphasis=midnight, wordmark=brand orange,
  dark-chrome accents=accentSoft), WCAG pill shades, neutral search, true-mono
  numerals, phantom override classes fixed, titleCase coverage extended.
- Record: audits/board/BOARD_aurora-web-redesign_2026-07-16.md (memos verbatim).
- GATE: founder walk of the 13 authenticated staging views + ruling on open items
  (font self-hosting disagreement · casing dictionary · off-white canvas · dark mode).

### 2026-07-17 — Aurora rev 3 HYBRID board re-review (6 memos, 5 verified staging live)
- Founder ruled rev 2 "too monotone" -> rev 3 hybrid: Aurora structure/typography/
  midnight chrome + ORIGINAL vivid data palette (orange N/search/wordmark, det
  #2D7EEF, conf #00C896, bright stage pills). Ruling RESTORES one-meaning-per-hue.
- Board verdict: hybrid liked (the institutional instrument); merge gated on
  Chairman rulings: (1) bright-hue TEXT contrast (conf text 2.16:1 — true of
  production too; text-twins recommended), (2) font self-hosting (4 memos pre-merge).
- Fixed during review on the branch: Ledger view was MISSING the mandatory verbatim
  disclaimer (added top+bottom); 3 ghost hexes (.g-lev #10B981, .lg-stg.aligned,
  stale comments). Rev 3.1 staged.
- Doc trio required WITH merge: CLAUDE.md §12 -> semantic parity; mobileTheme.ts
  header; /frontend-consistency re-point (else the watchdog reverts the ruling).
- Record: audits/board/BOARD_aurora-hybrid-rev3_2026-07-17.md (memos verbatim).

### 2026-07-17 (cont.) — ALL founder rulings landed (rev 4 staged + engine epoch stamp live)
- (1b) TEXT-TWINS: vivid hues stay for fills/rings/dots/charts; dark twins where
  hue is TEXT (--det-text/#1b5fc4 --conf-text/#007a5a --early-text/#b35a18; score
  columns, statcards, LED pill, conf gauge, cal-chip, fav CTAs); 3 stage pills
  nudged to >=4.5:1. (2) Jakarta SELF-HOSTED via @fontsource (15 woff2 bundled,
  Google links removed, 0 external font requests verified live). (3) DOCS TRIO:
  CLAUDE.md §12 -> SEMANTIC parity (two-dialects); mobileTheme.ts header = web's
  own authority; WEB_DESIGN_SYSTEM.md contract shipped; /frontend-consistency
  re-pointed to hue-MEANING parity. (4) P0: catLabel() (Current_events -> Current
  Events), engine-room maturity strings suppressed, AI Context hides when absent
  (dead spinner gone, §17), Ledger referee glyphs labeled. (5) titleCase acronym
  dictionary (AI/AGI/ASI/LLM/IPO/NATO/FIFA + small words). Rev 4 on staging
  (nowtrendin-terminal); branch aurora-web-redesign; gh-pages prod untouched.
- ENGINE-EPOCH STAMP LIVE (f74e1cb, board condition): /accuracy/ledger now serves
  epochBoundary=2026-06-15 + byEpoch (v1_engine 72 resolved/9.7% vs v2_engine 21
  resolved/4.8% — the blended 9.2% DID span two engines); /accuracy/ledger/detail
  rows carry per-row epoch. Metadata-only, fail-open (first deploy hit the
  RealDictCursor tuple-index gotcha — fixed with aliased dict access).
- Post-merge queue status: favorites hexes AUTO-RESOLVED by rev 3 (original
  palette is current again); warm-band chart separation + token unification +
  off-white A/B + dark mode = roadmap per rulings.
- GATE REMAINING: founder walk of staging rev 4 -> "merge" -> Executioner
  sequence (merge --no-ff, gh-pages with rollback SHA, mirror sync, parity +
  consistency checks).

### 2026-07-17 (cont. 2) — AURORA HYBRID MERGED + DEPLOYED TO PRODUCTION
- Executioner sequence executed on founder's go: merge --no-ff (14 files) ->
  main build -> ROLLBACK POINTER recorded (gh-pages pre-deploy SHA
  30c6255e5e1ec580a13d0575f12d37299c24ad03; rollback = repush that SHA, ~2 min)
  -> gh-pages deployed (0d0eb23) -> PARITY VERIFIED: GH Pages prod + Heroku
  mirror both serve the exact merged bundle index-BsGJsFnP.js -> smoke: fonts
  self-hosted (woff2 HTTP 200, zero googleapis refs), all 3 surfaces up.
- Branch aurora-web-redesign deleted (fully merged; board records were already
  on main). The web terminal now ships the founder-ruled hybrid: Aurora
  structure/typography/midnight chrome + original vivid data palette, text-twins
  for WCAG, semantic-parity docs, P0 polish, Ledger disclaimer, epoch stamp.
- The web design contract is web-terminal/WEB_DESIGN_SYSTEM.md; cross-platform
  color parity is SEMANTIC (CLAUDE.md §12; /frontend-consistency re-pointed).

### 2026-07-17 (cont. 3) — MOBILE board review complete (6 memos, source-verified)
- Verdict spread: design APPROVE/AWC ("honest bones, mania dressing"); display
  integrity up to REJECT (Challenger) on FOUR FALSE DISPLAYS; store-readiness
  gated. Record: audits/board/BOARD_mobile-aurora_2026-07-17.md (memos verbatim).
- P0 convergent (all small fixes, none touch the engine): dataWindowLabel "1h+"
  vs the real 24h/12h gates (4 independent confirmations, billing-adjacent);
  breakdownGroups fabricated component values on rows lacking engine groups;
  mock-fallback quarantine (fabricated freshness, detail ignores isSample);
  "ranked by Gradient Score" copy over the N-ranked default; monetization
  integrity (self-select grants any tier free; §8 clause absent from signup).
- P1 advice-crossing copy (PICK->SIGNAL, "leads the market"->"leads Google
  Trends attention", urgency headline, unsupported 24-72h forecast). P2 Aurora
  hygiene (SignalAnalysisPanel fossil retrofit spec; disclaimer gaps; 12px muted
  contrast). P3 store path closer than assumed — blockers are the payments-model
  decision (web-signup rec vs Apple 3.1.1) + small config; kill Capacitor.
- Praise: profile/accuracy.tsx "the most honest retail ledger" — surface it on
  the dashboard. AWAITING CHAIRMAN RULING per item.

### 2026-07-17 (cont. 4) — MOBILE board fixes ALL LANDED (founder: "fix all of them")
- P0 false displays fixed: dataWindowLabel now derived from TIERS (24h/12h truth);
  breakdownGroups fabrication deleted; mock fallback quarantined (no fabricated
  freshness, garnet SAMPLE banners on dashboard + detail, ILLUSTRATIVE hero);
  truthful rank copy + N·MAX marker; Enterprise self-grant closed (Contact Sales);
  §8 clause verbatim at signup. P1 advice-copy pass landed (SIGNAL, Google-Trends-
  true ledger copy, stage-true headline, tier-true intro, forecast removed,
  imperative guard, dashboard track-record link). P2 hygiene (panel retrofit —
  last banned hex gone; disclaimer gaps + contrast; casing dictionary). P3 code
  (Capacitor killed, app.json light/no-tablet, prefetch cap, poll jitter).
- Verified: hex/label/fabrication sweeps 0; expo web export clean; new copy
  confirmed in bundle; preview redeployed a0ed686 (gate + PIN intact).
- DEFERRED (honest): falls-below alerts (backend migration), FlashList + single-
  topic endpoint, eas.json/dev-client + the payments-model decision (web-signup
  rec), CLAUDE.md §3/§11 palette doc-debt.

### 2026-07-17 (cont. 5) — BOARD review of the proposed Scoring Assessor agent
- Six memos on the externally-authored assessor/teacher (payment portal on hold
  pending proven accuracy). UNANIMOUS: concept right (teaching layer + work queue
  + trend-over-time = a real fleet gap) — but DO NOT RUN AS-IS (4/6 reject the
  design as written). Record: audits/board/BOARD_scoring-assessor_2026-07-17.md.
- Convergent blockers: variants "fix" prescribes the Board-REJECTED score-time
  alias merge (rulings registry required); stale 1.0-era signatures hardcoded
  (45/67 bands; frozen-74 already fixed — forensically verified); mainstream-
  referee check measures FAME not MOTION (would teach score inflation);
  "circularity by courier" via the work-queue JSON (held-out stamps, task classes,
  diagnose-never-tune, engine-referee correlation drift alarm); readiness % is a
  Goodhart trap (internal-only rename; LEDGER tracked-race stays THE number and
  the portal gate); lifecycle classifier fat-tail fragile; cp1252 crash;
  unwatermarked demo work queues.
- Approved rebuild shape: /scoring-assessor SKILL over existing endpoints (6/10
  adapter methods already served), aggregator-over-the-fleet, fixed stratified
  cohort, append-only + git snapshots, feed param, free sources only.
  AWAITING CHAIRMAN RULING (rebuild ~half a day).

### 2026-07-17 (cont. 6) — Scoring Assessor v2 REBUILT + first live snapshot
- Rebuilt per the board spec (tools/scoring_assessor.py + /scoring-assessor skill,
  mirrored to docs/skills/). All board conditions implemented: endpoints-only,
  hashed check manifest, rulings registry, task classes, held-out stamps + drift
  alarm, surge-not-fame referee, quantile WARN-only lifecycle, outside-recall
  module, internal-only %s with the LEDGER as THE headline, demo watermarks.
- CHAIRMAN DIRECTIVE built in: snapshots born UNVERIFIED_PENDING_BOARD_REVIEW;
  the skill's mandatory BOARD ANALYSIS GATE (independent critique + fresh
  outside-data cross-check + verify/refute per item) precedes any teaching or
  implementation; Chairman final say always.
- FIRST LIVE SNAPSHOT committed (audits/assessor/ASSESSOR_2026-07-17.*): ledger
  tracked-race 24.2% (n=33) anchored as THE number; internal pass 70.6% / floor
  50%; findings: 19 high-volatility scores (spain/mamdani/white_house/shutting),
  2/10 external trending recall (sports matchups missing — rangers/braves, tom
  brady, piastri, dodgers/yankees), spain FADING-vs-BREAKOUT look. 21-item
  UNVERIFIED queue — NEXT STEP: run the board gate on snapshot #1, then Chairman
  ruling.

### 2026-07-18 — Assessor snapshot #1: board gate run + ALL Chairman-ruled fixes landed
- BOARD GATE (6 memos, fresh outside data; record audits/board/BOARD_assessor-2026-07-17.md):
  instrument compliant 6/6; items 1-19 verified as a CLASS/refuted as 19 tickets; item 20's
  2/10 refuted (cohort-only scan + substring matcher, verified at source; misses refuted by
  referee — Brady flat, Piastri declining); item 21 refuted 6/6 (Spain pageviews ~3x rising;
  BREAKOUT was correct — D-module shadow-scorecard entry #1). New: N1 blind assessor referee,
  N2 epoch mismatch (93!=87), N3-N6 hygiene. Chairman: "proceed with the fixes."
- DIAGNOSTIC (audits/assessor/VOLATILITY_DIAG_2026-07-18.md, read-only): the 19 flags are
  BURST-PLATEAU-CLIFF dynamics, not flapping (17/19 <=2 sign-flips; only america alternates);
  co-movement partial/staggered = input-recency rolloff after the 07-16/17 news wave, NOT one
  bad cycle. Open engine questions (SCORE_AFFECTING if ever acted on): Q1 cliff decay (60-79pt
  single-cycle drops), Q2 identical plateaus (values repeat to 0.01 across rescores). Found:
  score_history serves total_mentions=null (per-cycle volume diagnostic impossible from
  endpoints; B.freeze null-condition blind — cause-coded).
- ASSESSOR v2.1 (tools/scoring_assessor.py; param assessor-v2.1.dfc882cac9 = NEW comparable
  series): shape-aware volatility (sign-flips + magnitude floor; bursts PASS as expected
  dynamics), wiki referee FIXED via opensearch fallback (19/20 resolve vs 2/20; truthful
  cause codes on every INSUFFICIENT), E-check rebuilt (full-feed scan w/ pinned denominator,
  entity matching, matchup class excluded, 10k traffic floor, referee-confirmed misses only),
  min-n letter grades, Wilson interval + 0-FP-by-construction disclosure, drift-alarm series
  persisted (REFEREE_CORR_SERIES.json; first point rho=0.142 n=19 — low, thesis-right),
  D.lifecycle WARNs require a non-INSUFFICIENT referee. Verification run ASSESSOR_2026-07-19:
  queue EMPTY, pass 100%, honest N/A grades on tiny-n modules.
- ENGINE (v247): byEpoch reconciled — shares the headline C1 resolved definition
  (LATE_REDETECTION excluded + disclosed) + per-epoch tracked-race. Verified live:
  67+20=87 == headline; v1 35.0% (n=20) / v2 7.7% (n=13) tracked-race now visible.
- ENGINE LED REFEREE VERIFIED HONEST (no change): re-ran corroboration locally with the
  engine's own logic on all 8 LED wins — 7/8 resolve (Spain/Mexico/White House fine); the
  stored 0s are honest "no wiki arrival" refutations, NOT instrument failure. Footnotes:
  "court rulings"->:'Court Ellingson' (tangential resolve), "socialists" fails lexical guard.
- Closeout: snapshot #1 stamped BOARD_VERIFIED / CHAIRMAN_RULED 2026-07-18 (+ disposition in
  json/md); docs/GLOSSARY.md (N6 plain-English one-pager); shutting/trump_fires routed to the
  topic-quality worklist (N5).

### 2026-07-18 (cont.) — Q1/Q2 board session + ALL ruled items landed (#6 HELD by Chairman)
- BOARD (6 memos, record audits/board/BOARD_q1q2-cliff-plateau_2026-07-18.md): the Executioner
  ran the discriminating diagnostic LIVE and named the mechanism — the dual-pathway blend weight
  w (integer MEDIAN-of-12-cycles baseline, sorted[len//2]) flips discretely ~cycle 7 after a
  step-up, releasing the full pathway gap in one cycle. Q2 = cause (i) verified (identical raw
  stored values; calibration pass-through; INV-1 not implicated). Wikimedia framing corrected
  (level-vs-gradient category error). 5/6 independently found the history-route INV-1 gap.
  Unanimous forbidden list: no output smoothing/EMA, no jitter, no history rewrites, no INV-1
  weakening, no silent enrollment shifts, no tuning-to-quiet-flags.
- CHAIRMAN RULING: item 6 (baseline-estimator continuity+hysteresis, SCORE_AFFECTING) HELD;
  items 1-5,7,8 proceed. All landed + verified:
  (1) Confirmation sweep: cause (i) confirmed on white_house/shutting/jordan/andy_burnham
      (raw stored values themselves identical; served = rounding only). Q2 CLOSED cohort-wide.
  (2) Engine v248/v249: embedded score_history now serves per-cycle total_mentions,
      attention_magnitude, n_mainstream_platforms, mainstream_ratio (w), detection_pathway
      (null-not-zero).
  (3) COHORT REPLAY (audits/assessor/MEDIAN_REPLAY_2026-07-18.md): 49/50 of the >=30pt
      single-cycle transitions coincide EXACTLY with stored w snapping (1.0<->0.0) / pathway
      flipping — mechanism CONFIRMED (spain's 4 toggles all w flips; tillis cliff = magnitude
      median catching up 5.56->99.71; google = 8 w transitions in 30 cycles). One honest
      exception (japan 07-18T04, mainstream-internal). 07-19T10/T16 cliff PREDICTIONS PENDING
      (mamdani/taco/cyclosporiasis_outbreak; russia) — check after 07-19T17 UTC.
  (4) INV-1 STALE-SERVE GUARD live on /scores/{key}/score-history (HISTORY_SERVE_STORED=1,
      flag rollback): verified with before/after diff — 20 of 110 stale rows were being
      re-colored by live calibration (canada stored 33/61 served as 26/57); now serve stored.
  (5) INPUT-FRESHNESS FACTS (post-burst annotation) live on ALL surfaces: engine detail
      input_freshness{newest_signal_age_h, signals_in_window_72h} + standalone history route;
      web terminal Screener section (gh-pages 7e17149, bundle index-BfmU0H0M verified live;
      rollback pointer 0d0eb23); mobile ScoringHistory card (Aurora-compliant; preview
      aa46142, PIN gate verified intact). Facts only — never reinterprets the score.
  (7) Assessor v2.1.1 (param .4018144e78): B.asymmetry (Kindleberger audit) + C.saturation_gauge
      (Bernstein) as SHADOW checks — live run verified: britain flagged as the one true
      both-ways alternator; 0/6 top-decile pinned. SECOND-ORDER WIN: mentions-in-history made
      B.freeze's null testable — immediately caught final_del_mundial (det frozen 62.59 x6
      cycles while mentions varied 10-16; SCORE_AFFECTING, UNVERIFIED -> next board gate).
  (8) SCALE-DEBT LOGGED: the history route re-runs full calibration per row at serve time —
      O(history) compute amplifier on the fragile read path; design a precomputed/cached
      history lane (INV-1-consistent) BEFORE 100x volume forces it. No deadline; deliberate.
- OPS NOTE (honest record): one gh-pages deploy attempt ran with the shell cwd left in
  web-terminal/ — its cleanup step deleted the web-terminal source tree and committed the
  deletions LOCALLY. Nothing was pushed; recovered fully via git reset + checkout (rebuild
  produced the byte-identical bundle). Lesson: deploy steps use ABSOLUTE paths, always.

### 2026-07-18 (cont. 2) — taco_bell category review -> fixes F1-F4 shipped + verified
- Founder flagged Taco Bell under Technology while the AI Context correctly described the
  cyclosporiasis/lettuce outbreak. Diagnosis (audits/CATEGORY_REVIEW_taco-bell_2026-07-18.md):
  DISPLAY-ONLY defect; bare lexicon returns general; maps live+fresh; root cause = context
  builder classifying the 6 MOST-RECENT titles (bluesky chatter with incidental ai/app/google
  outvoting 19 news outlets) + platform words in the tech weak lexicon matching inside text +
  technology-above-health tie-break. Demonstrated concretely against the deployed classifier.
- Fixes (founder-approved, engine faee2b3, display-only): F1 tier-weighted context builder
  (publication titles govern, social fallback); F2 _TOPIC_ONLY_TERMS (platform words match
  topic string only); F3 health>technology tie-break; F4 /monitor/catmaps?explain= provenance
  probe. Local suite 8/8; LIVE verified post-refresh: taco_bell/taco/taco_bell_lettuce ->
  health (context), tacoma -> honest general, lettuce_taco + youtube regressions hold; detail
  serves category=health. Explain probe retro-confirmed context (not situation) was deciding.

### 2026-07-19 — Batch: items 11/12/14/15 done + board session R1-R3 COMPLETE (awaiting Chairman)
- ITEM 14: CLAUDE.md §3/§11 reconciled to the per-surface authorities (Aurora contract mobile /
  WEB_DESIGN_SYSTEM web); legacy palette marked web-lineage-only. Doc-debt closed.
- ITEM 11: /scores/{key}/score-history TTL response cache live (engine 4236024; 0.98s->0.34s
  verified; HISTORY_ROUTE_CACHE_TTL_S=300, 0 disables). Scale-debt amplifier bounded.
- ITEM 12: falls-below alerts LIVE end-to-end (backend v40, migration 0013_alert_direction
  applied via release phase; direction on serializer + evaluation + email copy; mobile
  Rises-above/Falls-below chips; web Alerts parity; preview 38cfc80 + gh-pages 43ce688).
  Single-topic deep-link fetch (fetchSignalByKey + useSignal solo fallback). eas.json scaffold
  (dev-client/preview/production). FlashList EVALUATED-AND-DEFERRED with reason: trends screen
  is <Screen scroll>+windowed map; conversion = structural refactor (FlashList must own the
  scroll container) — own session + regression pass required.
- ITEM 15 (three held-out reports, audits/ledger-research/*_2026-07-19.md): (a) breadth-priority
  M=80-vs-50 DOES NOT REPLICATE — real effect is enrollment EFFICIENCY (3x races/slot at flat
  win rate); (b) fast-lane CANNOT flip verdicts (dates fixed pre-sweep; the 1-2day losses were
  real) — re-scoped $0 latency+match-validity lane; referee contradicts 4/9 near-miss matches;
  (c) floor-pin: 281/300 instruments render score-excluded 0.0, crypto all-pinned D=30 — 4
  display-only §17 fixes + 1 backtest-gated score-side exclusion.
- BOARD R1-R3 COMPLETE (6/6; record audits/board/BOARD_estimator-fdm-snapshot2_2026-07-19.md,
  supersedes .PARTIAL): R1 un-hold into build+backtest 6/6 (estimator-family sweep: interpolated
  quantile vs Executioner slew-limited median; Economist re-crossing-only Schmitt hysteresis
  dissolves the symmetry dispute; gates G1-G5 + plateau-hours + median-catchup re-score);
  3 of 4 predictions VOIDED by renewed expansion (escape clause), final_del_mundial = clean
  out-of-sample win (mechanism 50/51); NEW: duplicate cycle rows in served history (britain
  glitch suspect) -> dedup diagnostic first. R2 refuted-as-written 6/6 (peak-hold magnitude by
  design; close as mechanism instance). R3 instrument approved 6/6 + v2.1.2 patch list.
  Decision table D1-D11 AWAITING CHAIRMAN RULING.

### 2026-07-19 (cont.) — R2+R3 fixes EXECUTED (Chairman-ruled D3-D6); all verified live
- D3: component pull CONFIRMED the Challenger residue — final_del_mundial M=80.0/I=12.4/P=73.0
  byte-identical across all 6 frozen cycles; 36.8*0.55+28+8.0+1.24+5.11 = 62.59 exactly.
  R2 fully accounted for; closed as mechanism instance #2.
- D4: assessor v2.1.2 shipped (param .c9ebdc0c06, dec613e): formula-arguments freeze null
  (inputs-vs-inputs, w/mag/nplat/M/I/P; mentions demoted to context) + SATURATION DEAD-ZONE
  refinement (nplat moving entirely >=4 with w pinned 1.0 cannot reach the formula — caught
  live when the first verification run flagged agi as a false positive); known-mechanism ruling
  tags (2026-07-18-median-w-flip -> LOW tracked instances, never page-one alarms); B.dup_cycles
  shadow check; flip-gated burst label ("monotone" only at 0 flips); ASYM_STEP + traffic-floor
  provenance registered; RECALL_SCAN_CAP 2000->4000 (full corpus); ASSESSOR_OUT_DIR env so
  verification runs never clobber a stamped same-day snapshot.
  VERIFICATION RUN (scratch dir): queue all LOW/OPERATIONAL — dup-hygiene found 20 duplicate
  same-hour rows FLEET-WIDE (mamdani/mexico/fifa/england/canada/cyclospora...) = strong D2
  evidence; flap instances correctly tagged known-mechanism and held for D1; agi resolves to
  the dead-zone null; zero HIGH, zero SCORE_AFFECTING items.
- D5: snapshot #2 (ASSESSOR_2026-07-19) stamped BOARD_VERIFIED / CHAIRMAN_RULED 2026-07-19
  with full disposition in json+md.
- D6: disclosures live BOTH sides — assessor headline now prints LED referee corroboration
  (0 corroborated / 6 uncorroborated / 2 unchecked, honest-refutation note) + the per-epoch
  young-races note; engine epochNote carries the young-races adverse-selection caveat
  (deployed ef5bac4, verified live on /accuracy/ledger).
- Open after this: D1 estimator build+backtest (awaiting Chairman go), D2 dedup diagnostic
  (now with the assessor's 20-dup evidence), D7 §17 display quartet, D8 (own gate), D9/D10.

### 2026-07-19 (cont. 2) — D2 diagnostic + D1 backtest round 1: THE NULL WON (honest result)
- D2 STEP 1 (audits/D2_DEDUP_DIAGNOSTIC_2026-07-19.md): off-cycle rows ENDEMIC (130/150
  topics; 113 same-hour dups + 689 short-gap extras; biggest clusters within 90min of Heroku
  releases -> boot-scoring; Pull-Trends also legit source). Root defect = ROW-count window
  (LIMIT 12) silently time-warps on deploy days. BRITAIN REPLAY HONESTLY REFUTED the dup
  hypothesis for her dip (raw and dedup windows identical: upper-median EQUALS cur mag 54.49
  -> w=0 boundary case) — she stays genuine D1 hysteresis evidence.
- D1 BACKTEST ROUND 1 (tools/estimator_backtest.py + audits/backtests/ESTIMATOR_BACKTEST_
  2026-07-19.*): pre-registered candidates vs gates on 107 topics/2765 cycles. NO CANDIDATE
  PASSES: C2 interpolated median (5-memo consensus) REFUTED (more flaps, cliff unfixed —
  Executioner's bimodal argument empirically confirmed); C3 slew family kills the artifact
  (cliff 78.7->14.7, flaps 0, plateau 95->27, zero delayed enrollments + 3 earlier) but FAILS
  G2 no-inflation (mean +2.4..3.9 — serves stale highs longer) and G4 tails (1-4 slow
  releases); hysteresis vacuous (registered H_MARGIN=0.0 degenerate). Reproduction gate 82.2%
  vs 95 bar + 1789 skipped cycles -> round is DIRECTIONAL; ship-grade round 2 = ENGINE-SIDE
  full-history replay with true components. INCUMBENT STANDS per the Malkiel null; the shipped
  honesty layer (freshness facts + mechanism tags) does the explaining meanwhile.

### 2026-07-19 (cont. 3) — D1 ROUND 2 (engine-side, Chairman-commissioned): THE NULL WON AGAIN — D1 CLOSED
- Engine-side chunked replay shipped (transfer/estimator_replay.py + /backtest/estimator/
  step|report; read-only, single-flight, quality-gated corpus w/ junk prefilter). Driven to
  completion over the FULL served universe: 32,989 topics, 30d-active, up to 400 cycles each.
  REPRODUCTION GATE 95.5% (> 95 bar) — ship-grade evidence, unlike round 1.
- VERDICT: EVERY candidate fails, including C1 dedup-window alone (10 delayed 70-crossings
  — G1 zero-delay is absolute and nothing in the family clears it at 33k-topic scale). Slew
  family: cliff 78.7->37.3 (still >20 bar), G2 inflation + G4 tails persist (C5 snap cuts
  tail fails 167->44, not 0). Hysteresis immaterial. Round-1 directional reads confirmed.
- DISPOSITION: D1 CLOSED — incumbent estimator stands per the Malkiel null (2 rounds, 8
  candidates, full panel). The artifact class stays display-explained (freshness facts +
  known-mechanism tags + D6 disclosures = the shipped fix). D2 step 2 (dedup-in-query)
  WITHDRAWN on its own G1 failure. Future attempts = fundamentally different design (true
  per-cycle component recompute from raw signals), own registered round, same gates.
- Report: audits/backtests/ESTIMATOR_BACKTEST_ROUND2_2026-07-19.md + .json.

### 2026-07-19 (cont. 4) — Docket 1-4 executed: D7 shipped · D8 deferred-on-evidence · D9 designed · D10 built inert
- D7 (§17 quartet, display-only, engine 64c1acc + gh-pages 14f6178 + preview redeploy):
  absent components serve score:null+absent:true (never a fabricated 0); DEGENERATE
  zero-on-zero pins stamped + served as honest absence (spacex-class "30 ✓" ends); crypto
  coin payload gains data_coverage/absent_inputs/total_inputs + degenerate proxy-D handling;
  web MarketSignal compact list OMITS null components (factor rows were already n/a-safe);
  mobile risk detail gains the LTD-DATA banner (was consuming no coverage at all). Weighted
  scores UNTOUCHED (D8 gated). VERIFICATION NOTE: /risk/scores + /crypto serve precomputed
  payloads — new shapes appear at the next worker market cycle (~22:4x UTC) / next prewarm
  rebuild; frontends handle both shapes (null-safe) so the rollout is order-safe.
- D8 (score-side degenerate exclusion): held-out backtest (audits/ledger-research/
  D8_DEGENERATE_EXCLUSION_BACKTEST_2026-07-19.md) found the LEDGER NEVER READS money_movement
  (enrollment gates on dark-positioning flow+intensity) — 0/12 resolved equity + 0/1 crypto
  detections would change under exclusion; 0/12 were pinned at detection (values 32.4-70).
  D8 DEFERRED on evidence: zero ledger payoff; D7 delivers the honesty. ADJACENT LEAD logged:
  outflow lane 0-for-5 (rhymes with degenerate-net insider) -> future positioning_intel flow
  item. Current-state back-projection proven invalid (trap documented).
- D9 (enrollment A/B): registered design shipped (audits/ledger-research/
  D9_ENROLLMENT_AB_DESIGN_2026-07-19.md): deterministic slot-parity arms, shared
  LEDGER_ENROLL_NEW_CAP=3 (without it the cap never binds and the arms are identical —
  the design's key catch), judge arm-blind, races-per-slot primary endpoint (97/arm ~8-10wk;
  hit-rate registered UNPOWERED), socialists-class monitor, stop rules, ~55-line touch-point
  described not implemented. Awaits founder go to build.
- D10 (fast-lane): IMPLEMENTED INERT (transfer/fastlane_recheck.py + scheduler :10 job +
  /fastlane status; FASTLANE_RECHECK=0 default). Free sources only; never judges; logs to
  held-out fastlane_recheck_log; promotes <=2 pending rows/run into the existing paid
  rotation (last_checked=NULL) with 72h cooldown. Verified live: /fastlane enabled:false,
  caps served. Founder flip = set FASTLANE_RECHECK=1 (board gate on live evidence after).

### 2026-07-19 (cont. 5) — D7 VERIFIED LIVE (crypto); two stamp-rule fixes en route
- The degenerate signature needed two corrections against REAL stored data (each caught by
  verification, never shipped blind): (1) crypto pins are constant-NONZERO baselines, not
  zero-on-zero; (2) storage FLOORS stdev at 0.05, so "stdev==0" can never occur in stored
  baselines — final signature = stdev<=0.05 (at-floor) AND current==constant mean. Local
  truth table 4/4 (spacex-class ✓, crypto-class ✓, real-deviation ✗, real-variance-at-mean ✗).
- VERIFIED LIVE (engine efe20b5, post-prewarm): BTC proxy positioning serves score:null +
  absent + degenerate_baseline with data_coverage=insufficient — the "measured 30 ✓" era on
  crypto D is over. Equity /risk/scores flips at the next worker market cycle (~22:4x UTC),
  same verified code path; frontends handle old+new shapes either way.

### 2026-07-19 (cont. 6) — D9 LIVE · D10 LIVE · D8 board complete (awaiting Chairman on E1-E5)
- D9 A/B RUNNING (founder-ordered; engine 8626ecd, flags v260): LEDGER_AB_D9=1 live per the
  registered design — deterministic (d+s)%2 arm assignment (formula smoke-verified), widened
  candidate fetch + new-candidate filtering (key+canonical-date, mirrors record_detection
  idempotency), arm B breadth-ordered, shared LEDGER_ENROLL_NEW_CAP=3 on BOTH arms,
  enroll_ab_log audit table, arm/breadth carried pending->ledger (nullable forward-only
  columns). Judge arm-blind; precondition LEDGER_SWEEP_NEWEST_SLOTS=2 confirmed. First arm
  fires at the next enrollment cycle; weekly stop-rule monitoring per design §8.
- D10 FAST-LANE ARMED (FASTLANE_RECHECK=1): /fastlane serves enabled:true, caps 40/2/72h/21d;
  first scan at the next :10 slot. Free sources only; never judges; ledger reporting will
  segment fastlane-triggered rows.
- D8 BOARD COMPLETE (6 memos; record audits/board/BOARD_D8-degenerate-exclusion_2026-07-19.md):
  unanimous — backtest verified (ledgers never read mm; Δ=0 exact), outflow lane = THE live
  lead (open as NEW held-out item; regime control first; NEVER throttle outflow enrollment),
  no back-projection. GENUINE SPLIT on the composite: Outsider build-now w/ conditions vs 3
  defer-with-tripwires vs Guardian disclose-now + Economist narrow carve-out (mm->None only
  when ALL components absent/degenerate; renormalized-survivor composites REJECTED — kills
  half the original D8 spec). Unique finds: n=12 is ~7 independent episodes (Challenger);
  regime confounding; detection_score=None->intensity x100 witness-corruption fallback (fix
  regardless); congress-net-sell base-flow candidate mechanism for the outflow failures
  (Executioner, L118 vs the L160 insider fix); degenerate census as the permanent expansion
  frontier metric (Expansionist). Decision table E1-E5 AWAITING CHAIRMAN RULING.

### 2026-07-19/20 (cont. 7) — E1 SHIPPED + VERIFIED · E2 investigation relaunched
- E1 COMPOSITE DISCLOSURE (Chairman-ruled, Guardian's minimum-honest-state): the composite
  still counts absent/degenerate components at the neutral baseline (score-side exclusion is
  gated, E3) — now DISCLOSED instead of silent. Engine (12cf9c1) adds unmeasured_in_composite
  + composite_note to equity + crypto payloads; rendered on web MarketSignal + Crypto factor
  blocks + mobile risk detail. Also fixed the D7 mobile banner reading dataCoverage from the
  wrong object level (now mg.dataCoverage). VERIFIED LIVE: composite_note serves on 299/300
  risk instruments + crypto (BTC 3 unmeasured); gh-pages e31dd05 (rollback 14f6178), preview
  0c65cb2, both up + gated. The display-vs-composite contradiction the board flagged is closed
  at zero score risk.
- E2 OUTFLOW INVESTIGATION relaunched (first run hit the 11pm PT session limit after writing
  the pre-registration): new held-out read-only item, pre-registered defect criterion (outflow
  confirms <= regime base rate) + review threshold (n>=15 or 0-for-10); regime base-rate control
  first, episode-collapse, congress-net-sell mechanism trace; report ->
  audits/ledger-research/OUTFLOW_FLOWLOGIC_INVESTIGATION_2026-07-19.md. In progress.

### 2026-07-20 — E2 OUTFLOW INVESTIGATION complete (mechanism confirmed; no lane verdict at n=5)
- audits/ledger-research/OUTFLOW_FLOWLOGIC_INVESTIGATION_2026-07-19.md. Read-only/held-out;
  pre-registration intact (defect = outflow confirms <= regime base rate; conclude only at
  n>=15 or 0-for-10).
- MECHANISM CONFIRMED (code-certain): production serves dark_matter_inputs="congress+curated_13F"
  -> AV_DARKPOS_ENABLED effectively OFF -> the L160 accumulation-only asymmetric fix never runs;
  live outflow claim = positioning_intel L118 flow='outflow' if congress net(buys-sells)<-1.
  All 5 outflow instruments sell-dominated (AAPL 6/14 net-8, GOOGL 4/9 -5, NVDA 6/11 -5) = the
  exact degenerate-net class ruled noise for INSIDERS on 2026-06-26; congress base flow never
  got the correction. Executioner's traced candidate = the live mechanism.
- REGIME CONTROL FIRST (Challenger): local detection-window outflow-confirm base rate 18.8%
  (these names rallied +8..19%); P(0-for-5|regime)=0.35 -> failures fully consistent with regime
  alone at n=5; both lanes are the same rally bet pointed opposite ways. Ledger reproduced
  independently from free Stooq closes (all 5 rows p0/p1/change/verdict exact).
- EPISODE-COLLAPSE: 0-for-3 (AAPL x3 = one persistent claim).
- VERDICT: NO lane verdict (n=5<15). Defect criterion technically met (0%<=18.8%) but
  uninformative — regime confound not yet separable from degenerate-net noise. KEEP ENROLLING
  UNCHANGED (never throttle the losing lane); track to n>=15.
- SPEC S1 (do-not-implement): asymmetric outflow gate mirroring the L160 insider fix (routine
  net-sell -> neutral unless corroborated) as a FUTURE SCORE_AFFECTING item behind its own
  held-out, regime-adjusted, precision+recall backtest gate. Caveat: congress buys/sells are
  current-state (no served positioning-history route); mechanism is time-invariant/code-certain
  but exact per-row detection-instant counts aren't endpoint-recoverable.
- E1+E2 both closed. Open docket: E3 (D8 defer-with-tripwires), E4 (hardening quartet incl. the
  detection_score=None->intensity fallback fix), E5 (cold-start posture doc); S1 future gate;
  D9 A/B accumulating (weekly stop-rule watch); D10 fast-lane live; GHOST_FEEDS trial to ~07-29.

## 2026-07-27 — Board review 2 remediation + prereg RE-LOCK (engine v290)

**Board review 2** (`audits/board/BOARD_review-current-changes_2026-07-27.md`, 5 archetypes):
chassis good, claims survived contact — but the never-reviewed `flow_enrollment.py` carried
two defect classes the Board had already named, one of which would have corrupted row 1
permanently. Verdict: parser flip may proceed on its gate; **FLOW_ENROLL waits**.

**All blocking findings fixed, deployed v290, self-tests green, firewall CLEAN:**
- **B1** treated rows would have enrolled with `sector=''`/`size_decile=None` (`run_cycle` read
  `prof["match_facets"]`, a key that never existed) — the strata the pre-registered analysis
  stratifies on, missing forever in a never-delete ledger. Fixed via one `facets_of()` used by
  both arms. **Regression VERIFIED by reintroducing the defect** (test fails with `sector=''`).
  The old test missed it by hand-building the treated dict; it now runs `run_cycle` end-to-end
  and asserts on the STORED row.
- **B2** (all five archetypes) registered `enroll_threshold` was decorative — hashed, compared
  to nothing; `below_threshold` counter incremented nowhere. `enroll()` now refuses + counts;
  `run_cycle` HALTS when env disagrees with the registration.
- **B3** "10 trading days" was 10 calendar days (~7 sessions) → `window_start()` walks weekdays.
- **B4** `ingest()` wrote NULL-hash rows without a salt (mixed eras double-count one person →
  two real buyers + one fracture fabricate the 3-buyer trigger). Now refuses.
- **B5** pre-arrival used env mult, not the prereg's. **B6** "ADV band" was the screener's
  CURRENT-SESSION volume and `adv_matched:True` was stamped even when skipped → ADV is now the
  frozen 60-session baseline median; missing data REFUSES. Taint query gained `<= asof`
  (lookahead) and now taints on a QUALIFYING cluster (matching the registered exclusion —
  excluding any-insider-buying selected quieter controls, which flattered us).
- **B7 THE RE-LOCK.** Qualify window, persistence rule, echo threshold (a FALSIFIER input) and
  match-key spec were env-enforceable but absent from the SHA. `flow_prereg.extra_terms`
  (hashed, forward-only DDL) + `prereg_terms()` as the one reader; sweep resolves persistence
  and echo per row. **New lock `2d65eac796c28476`** registered 2026-07-27T18:17:27Z; doc
  committed at 08:42:24-07:00 BEFORE the post (git timestamp = the pre-registration).
  Superseded `261716973f6968b4` holds **ZERO rows** — the only reason this was free. The
  2026-07-26 doc is retained unaltered and marked, never edited to match the code.
- **B8** the stratified log-rank named PRIMARY existed NOWHERE in code (only the secondary
  publication gate). Implemented + **validated against the published Freireich 6-MP trial
  (chi2 16.7929, p 4.2e-05 — matches), type-I 0.053/0.057 vs 0.05, 95% power on a true 2x
  hazard gap**; opposite-direction results read as REFUTATION. Wired into `report()`.
- **B9** source-liveness tripwire (`insider_flow.liveness`): every prior watchdog asked whether
  our PROCESS ran, not whether the SOURCE returned usable data — which is why the insider
  source died for ~30 days unalarmed. RED on stale/zero-rows/coverage-collapse; on
  `/flow/status` + alarmed from the scheduler. **B10** hourly ingest tick (the ~200-row cap vs
  the 4-10pm ET burst; heavy days ARE cluster days).
- Also: crypto `by_flow` served **100.0% on n=1** while the headline was withheld, and the floor
  shipped at n=20 vs the demanded 30 (nobody argued it down). One `CRYPTO_MIN_PUBLISH_N=30`
  now governs headline, sub-rates and median lead. `ENROLL_PER_CYCLE_MAX` 5->3 (measured worst
  case 25-30 min inside `_collect_phase` vs ~20 min headroom).

**Live verified (v290):** new prereg active with every term inside the SHA; `term_drift: []`;
flags still all `0`; `primary_analysis` present (honestly "no observations" at n=0); crypto
sub-rate leak gone.

**R7 gate — READ HONESTLY:** scanning all 300 served risk items, only 3 insider components
carry a z at all and **max |z| = 0.64** (Alphabet -0.64, JPMorgan -0.10, drawdown 0.0). BUT the
three originally-tracked names (AAPL -3.96, MSFT -4.19, NVDA -1.88) **no longer appear with an
insider z at all**, so this is NOT the same measurement as "those three decayed" — plausibly
because A7 set `DARK_POS_WEIGHT=0`. Chairman's call: accept "no served insider component
|z| >= 1.5 anywhere" as the gate, or restore a per-name read first.

**Open docket unchanged** plus: B11 (`CRYPTO_LEDGER_CLEAN_COHORT_START` must be stamped with
the ACTUAL flip date in the same `config:set` as the flip), screener-random calibration
robustness re-run before publication, gate-5 recurring, `market_momentum` raw-series dump,
R-e (momentum signed vs magnitude), R-f (panel name).

### 2026-07-27 (later) — CHAIRMAN RULING on the R7 gate + tooling fix

**RULING (founder, 2026-07-27): the R7 flip gate is ACCEPTED on the served-universe reading** —
*"no served insider component carries |z| >= 1.5 anywhere"* (measured: 3 insider components
across all 300 risk items, max |z| = **0.64** — Alphabet -0.64, JPMorgan -0.10, drawdown 0.0).
Recorded explicitly because this is NOT the original per-name check: AAPL/MSFT/NVDA no longer
carry an insider z at all (plausibly A7's `DARK_POS_WEIGHT=0`), so no claim is made that those
three specific transients decayed. **The parser flip is now UNBLOCKED and awaits execution.**

**Tooling: every Claude hook on this box had been failing silently.** `python3` resolved to the
**Windows Store App Execution Alias**, which launches the real Python312 but inside the Store
app container where **`AppData\Roaming` is virtualized away** — so the hook scripts (which live
under `AppData\Roaming\Claude\local-agent-mode-sessions\...`) reported "can't open file" on
paths that `ls`, PowerShell and `python.exe` could all read. Verified: ordinary project file →
visible; `AppData\Roaming\Claude` → NOT visible to the alias. Both the Pixeltable plugin's
PostToolUse (`validate_antipatterns.py`) and SessionStart (`session_orientation.py`) hooks were
dead for the whole session. **Root cause of the bad resolution:** `Python312\` is at PATH
position 19, AHEAD of `WindowsApps\` at 21 — the alias only won because the Python folder ships
`python.exe` but no `python3.exe`. **Fix (durable, one file, reversible):** copied `python.exe`
→ `python3.exe` in `C:\Users\acinv\AppData\Local\Programs\Python\Python312\`. `python3` now
resolves to real 3.12.10; the originally-failing command runs clean; hook verified with a
POSITIVE control (deprecated `FrameIterator` → emits its advisory) and a NEGATIVE control (this
repo's code → silent). Session-scoped `hooks.json` also switched `python3`→`python`, but that
copy is regenerated per session; the `python3.exe` fix is the durable one. Memory:
`env-windows-python3-store-alias`.

### 2026-07-27 (evening) — PARSER FLIP EXECUTED (founder) + post-flip verification

**Flip landed:** engine **v291**, `INSIDER_PARSER_FIX=1`, `CRYPTO_LEDGER_CLEAN_COHORT_START=2026-07-27`
(stamped in the same `config:set`, per B11). `INSIDER_FLOW=0`, `FLOW_ENROLL` unset — the chain
is correctly still gated. Prereg `2d65eac796c28476` active, `term_drift: []`.

**THE PARSER IS ALIVE — verified against the LIVE source, not inferred:**
`201 raw rows -> 116 parsed -> 69 distinct tickers`. The 30-day corpse is breathing.

**The visible Market-Signal effect, and why it is CORRECT rather than a regression.**
On a fair like-for-like 226-topic comparison, **14 of 16** watchlist names LOST their insider
read (score+z -> `None`); only JPMorgan and Alphabet kept one. Root cause traced, not assumed:
the live market-wide Form-4 feed contains **only GOOGL** of the 16 watchlist mega-caps — the
feed is small/mid-cap dominated (ACU, ANDE, ANIX, BMNR, CRAI...). Those mega-caps have **no
recent qualifying insider activity**, so the honest read is ABSENCE. Corroborating: pre-flip,
**8 of 17** topics sat pinned at **20.9-21.0 with z ~ -1.13** (Apple, Microsoft, IBM, Meta,
Alphabet, Amazon, Wells Fargo, Nvidia — eight different companies, one number) — a floor value
wearing a measured badge, the §16a stage-2 "30 ✓" defect. Post-flip those read absent, and
**Alphabet — the one mega-cap actually in the live feed — moved 21.0 -> 24.9 (z -1.13 -> -0.64)**,
a real differentiated value. The flip replaced fabricated-constant insider reads with honest
absence plus one genuine measurement. `/research/dark-positioning` (rebuilt 23s before the read,
so post-flip) shows `dark_matter_inputs: "congress + curated_13F"` — insider legitimately absent
for those names.

**NEW DEFECT found during verification and FIXED (not deferred):** Finviz's navigation row
("Home | News | Screener | Charts | Maps | Groups | Portfolio | Insider") carries enough cells
to survive the >=9-cell test, and `_ticker_from_cell`'s fallback **UPPERCASED "Home" into a
ticker-shaped "HOME"** — one junk row per fetch wearing a real ticker's shape. It was refused
downstream by the ingest gates (unclassifiable transaction "Maps"), so **nothing could have
entered the append-only panel** — defense in depth worked — but it inflated the parsed-row and
distinct-ticker counts the **B9 liveness tripwire reads**, which is exactly the metric that must
not lie. Guard added: a genuine ticker cell renders ALREADY UPPERCASE, so title-case text is
chrome, never an instrument. Verified live: `115 parsed / 68 tickers / 0 nav rows`, with
`LEVI`, `AAAPL->AAPL` and `BRK.B` all preserved.

**Crypto post-flip: unchanged and correct.** 12/12 `money_data_absent` with
`absence_reason: proxy_coverage_thin`, `flow: no_data`, `dark_matter` omitted, no direction
anywhere. BTC/ETH stay absent because fewer than 2 of their own proxies vote — the coverage gate
holding conservatively, as designed. Ledger: `resolved 1`, `confirm_rate_pct: null` (withheld
under the corrected n=30 floor), `dead_parser_era_rows: 1`, `clean_cohort_start: 2026-07-27`.

**Captures archived** in `audits/board/postflip/` (6 endpoints, same set as `preflip/`).
**Next gate:** watch one full collect cycle, then `INSIDER_FLOW=1` (panel begins accruing;
hourly ingest tick + liveness tripwire go live with it), then `FLOW_ENROLL=1`.

## 2026-07-31 — Crypto n/a remediation COMPLETE (v299-v301) + dominance flag FLIPPED

**Deployed and live-verified (v300):** the structural-truth disclosure. `/crypto` now serves
`absence_class` at top level: **11 coins `structural`, 1 (BTC) `transient`** — computed by the
new `_max_votable()` reachability test (proposed §16a stage 0). `proxies_total / covered /
votable_max / money_floor_required` moved OUT of the omitted `dark_matter` block to the top
level, so the surface can finally say WHY (it previously could not — the truth was computed
and discarded at the boundary). Web terminal (gh-pages) states it per coin: "this coin has N
usable money-positioning source(s) and the read requires 2. That is a limit of the sources,
not a temporary gap." The false "not YET available" is gone.

**Dominance flag FLIPPED (founder "please fix", v301):** `INSIDER_ACCUM_DOMINANCE=1`.
Verified live post-flip: **MSTR insider = neutral** ($998,756 buys vs $22,123,950 sells —
buying was 4.4% of the tape and the old gross-buy threshold called it "accumulation").
COIN neutral. Impact measured before flipping: exactly 1 of 12 sampled tickers changes, and
that one was the ONLY insider vote across all 12 coins — the entire crypto Dark Matter read
had rested on it. Before-captures in `audits/board/dominance-flip/`. Served crypto payloads
roll at the next collect cycle (prewarm-cached).

**ETF share-flow evidence collector live (v300):** `etf_flow.snapshot()` records
shares = AUM/NAV for IBIT/FBTC/GBTC/ETHA/ETHE once per risk cycle — RECORD-ONLY, feeds no
score. §16 gate 4 ACCESS verified on the paid FMP plan (5/5 proxies); CURRENCY accumulates
~a week of snapshots, then `currency_report()` renders its verdict. SHARES, never AUM
(AUM = shares × NAV → circular with M). Even fully wired this fixes BTC+ETH only (2 of 12).

**Open:** flip decision on wiring the ETF vote awaits the currency verdict (~2026-08-05);
Board doc `BOARD_crypto-money-na_2026-07-29.md`; unanimous CUTs stand (no floor-lowering,
no on-chain spend).

## 2026-08-01 (late) — S7 EXECUTED: INSIDER_FLOW=1 (v308). The insider panel is accruing.

**Pre-flight gates, all green before the flip:** INSIDER_PARSER_FIX=1 (ingest refusal
satisfied) · ACTOR_ID_SALT set 64-hex (B4 refusal satisfied) · prereg `2d65eac796c28476`
active, term_drift [] · liveness OK (finviz_insider HEALTHY: 154 signals, 87 distinct) ·
collectors 18 healthy / 0 down · /scores 200 in 0.56s. FLOW_ENROLL stays 0 — the panel
accrues; NOTHING enrolls until the founder fires the last flag in the chain.

**What turns on with this flip:** hourly market-wide Form-4 ingestion into the append-only
`insider_events` panel (B10 tick, first fire ~1h post-boot); §16a universe promotion
(candidate→calibrating, never auto-active); the panel-ingest layer of the liveness tripwire
(the source layer was already un-gated). First-ingest watch armed (panel.events > 0).

**Also this session, same day:** trend-ledger intake RESURRECTED (first fast-path cycle:
recorded 3, status ok, pending 1096→1099, after 17 straight failures); PG txn-abort ALTER
bug fixed across 3 sites (verified live: 'current transaction is aborted' was eating intake
rows); crypto flow Board ruling + Stage 0 (15-ETF roster dark, SOL/XRP §16 clocks started);
D1/D2 display lies fixed (absence may never wear a measured word); COT bitemporal rule
adopted for the next onboarding. Known follow-up: the S6 stale-payload census over-counts
(60,879 = ALL historical risk rows, needs latest-row-per-topic denominator).

**Remaining flips, in order:** FLOW_ENROLL=1 (after ≥2 clean panel days; opens flow-ledger
enrollment under the re-locked prereg) · CRYPTO_ETF_FLOW=1 (Stage 2, ~08-10, after the
currency verdict + shadow votes + reconciliation).

## 2026-08-04 — Full health check + Stage 1 deployed (v309) + liveness false-RED fixed

**Health sweep (founder-ordered, /nowtrendin2.0):** engine/backend/gh-pages all UP; web build
clean (3.3s); monitor fleet 9 agents — 7 ok, 2 warn (both known: S6 census over-count 60,879;
Cost Sentinel $592.81 = 85% of cap, DOWN from $718 — the Apify drop landed). Collectors
18 HEALTHY / 0 down / 2 deliberately DISABLED (finnhub_congress retired, reddit). Catmaps warm
(source=live, 60,146 entries). Trend intake: last=ok, enrolled=45 in window, completeness
46.9% (the 17 fails are the pre-fix dead era, denominator honesty). Market ledger 25 resolved /
6 pending, rate honestly withheld (n<30); crypto ledger 1/1, same floor. Prewarm fresh.

**Liveness false-RED root-caused + fixed (f1e97af):** the insider panel's coverage watermark
counted distinct tickers ONLY for newly-INSERTED rows — every steady-state hourly ingest of the
slow-moving Finviz feed (~100% idempotent duplicates) collapsed to "170 raw → 4 distinct" and
fired the dead-parser RED on a healthy source (collector_health parsed 81 distinct from the
same pull; first ingest's 61 masked it because the panel was empty). Coverage now counts every
ticker that SURVIVES the reject gates, before the duplicate check — a duplicate is proof the
parser worked. Regression proven BOTH directions (all-duplicate pass reads full coverage GREEN;
a genuinely dead parser still fires RED). The stored RED clears at the first post-deploy hourly
ingest (~1h after boot).

**Stage 1 DEPLOYED (v309, dark):** the crypto ETF share-flow vote (63661dd) is now on the
engine, CRYPTO_ETF_FLOW=0. Shadow votes verified live through the REAL _etf_flow_vote on
/diag/etf-flow: FBTC −1.0 (capped, −1.47%/day redemption), GBTC −0.618 (measured, not pinned),
BITB +0.12, quiet funds 0.0 measured-quiet, no discontinuity stamps. days_observed=8; all
15/15 tickers now have ≥5 obs → flip preconditions #1–#3 look green (sanity continues to
accrue daily).

**Crypto flip still blocked on (spec §8):** #4 reconciliation of derived Δshares vs issuers'
published flows; #5 venue_diffusion freeze for crypto (designed, NOT coded); latency stamps
(flow_basis/signal_latency_days) on payload+ledger rows; then founder flips CRYPTO_ETF_FLOW=1
+ moves CRYPTO_LEDGER_CLEAN_COHORT_START in the same command.

**FLOW_ENROLL readiness:** panel accruing since 08-01 (397 events / 244 universe / 3+ days);
the only liveness noise was the false RED above. Recommend: observe one clean GREEN ingest
post-v309, then the founder may fire FLOW_ENROLL=1 (success = pending_treated ≥1,
pending_control ≥3, treated rows carrying sector+size).

## 2026-08-04 (PT, evening) — Chairman rulings executed: A1 + U2 + S6 shipped; FLOW_ENROLL=1 LIVE

**Board session** (`BOARD_status-review_2026-08-04.md`): six independent memos on the health
check + recent updates. Unanimous: F2 flips on gates, not the calendar. Split: F1 timing
(five said days; Challenger demanded the window floor). Chairman ruled; all rulings executed:

- **A1 (prereg amendment, pre-enrollment — `FLOW_PREREG_AMENDMENT_A1_2026-08-04.md`), v310:**
  (1) window floor — `qualify_clusters` refuses until `window_start >= panel_start`
  (Challenger's left-censoring condition; live: window 07-22 < panel 08-02 → refusing,
  spans ~mid-Aug mechanically); (2) canonical-identity counting — name variants collapse
  per context (same normalized name + same ticker + compatible role; conflicts flagged
  never merged; panel untouched); new read-only **similar_fragmentation agent** in
  run_all (live: 0 boundary crossings on the real panel — no fabricated clusters exist);
  (3) jurisdiction column (default 'US') on insider_events + flow_pending_detections +
  flow_ledger, stamped at ingest/enroll; (4) stamp convention: prose/comments PT, data
  stays UTC (§14 untouched).
- **U2 trio, v312:** committed all-duplicate regression in the self-test (asserts STORED
  coverage rows); `insider_coverage.parsed_tickers` + `method='v2-dual'` epoch stamp
  (old rows untouched, NULL-fallback in liveness); liveness alarms on PARSED tickers
  (rows the parser read) closing the residual sub-$250K false-RED class + reconciling
  with collector_health's denominator.
- **S6, v312:** stale pre-guard census = latest-row-per-topic (served exposure):
  60,879 rows → **5 topics** (actionable; verify or age out).
- **FLOW_ENROLL=1 (config v311, Chairman-fired):** full chain armed — INSIDER_FLOW=1 +
  FLOW_ENROLL=1, prereg 2d65eac796c28476 active, drift [], liveness GREEN post-fix
  (54 scorable tickers, hourly). Enrollment self-starts when the floor spans; success
  check: pending_treated ≥ 1, pending_control ≥ 3, strata populated.

**Next:** F2 gate work (venue_diffusion freeze + latency stamps in one dark change →
reconciliation harness with PRE-DECLARED tolerance band → founder flips CRYPTO_ETF_FLOW=1
+ cohort start same command); key rotations (QUIVER/FMP); referee corroboration; the 5
stale pre-guard topics; S8 conflict + Economist prescriptions await Chairman ruling.

## 2026-08-05 (PT) — Book-canon board + Chairman rulings executed: F1–F8, C1/C2 live, X cost halved

**Book-canon board** (`BOARD_bookprinciples_2026-08-05.md`, 6 independent memos, all
code-verified): A1 held up to six cold code reads; findings F1–F8 (4 seats independently
caught the class-budget spec≠code gap; Challenger found the pre-strike fabricated-quiet
and the flip-as-baseline-break). C-items: C7 unanimous, C2/C1 top display picks, C5/C6
unanimously shelved, C4 rename urged by 3 seats — **Chairman OVERRULED the rename** (name
stays utility-vs-speculative; recorded in amendment A1.6).

**F1–F8 all fixed** (commit 9c8f5a7, dark; committed harness `test_crypto_flow_a1.py` 9/9):
pinned etf_class_budget per coin · value-distinct strike compare (no fabricated quiet) ·
CRYPTO_SERIES_EPOCH (crypto-scoped baseline reset at flip) · trading-day gap normalization ·
committed regressions · venue-class proxy_coverage · pre-declared reconciliation floor
(max($10M, 0.05% AUM)) · per-coin unconditional first-crossing null as a PUBLICATION
PRECONDITION (crossing detector force-proven both directions).

**C1+C2 SHIPPED** (engine + web): `supply_facts` — network value (FMP marketCap÷price),
pre-declared crypto-native bands (mega ≥$100B / large ≥$10B / mid ≥$1B), circulating-vs-FDV
+ % outstanding, honest "no max supply" for uncapped coins, lost-coins caveat; §17
omit-when-absent; Crypto rail section + band chip (gh-pages 75d6755). **C3**: SUPPLY_MODEL
curated from CURRENT protocol docs (post-merge ETH — the book's 2018 mechanics rejected as
source), as_of+source stamped, **owner = weekly improve-system** (checklist line added).
**C5/C6**: one shelf entry, no-proxy prohibitions written (exchange volume ≠ on-chain; no
sampled realized cap). **C7**: sweep artifact `audits/copy-sweep/CRYPTO_COPY_SWEEP_
2026-08-05.md` — zero violations, one watch item; standing weekly line. **C8**: design
pre-registered (`DIVERGENCE_DETECTOR_PREREG_2026-08-05.md`) — coverage-gated on measurable
flow, nulls registered, no mania language; build after flip + 30d.

**X COST RULING (founder escalation: spend doubled to ~$400/mo).** Mechanism traced:
scan cron 4×/day → HALVED to 00/12 UTC (`X_SCAN_HOURS`); daily pull cap 4→2; monthly
budget 14,880→**4,800 posts ≈ $198 hard ceiling** (observed effective ~$0.0413/post).
August was already pacing 528 posts/day (2,640 by day 5) — the new budget will exhaust
mid-month by design; free volume scans continue. CLAUDE.md §6 updated.

**Why the Cost Sentinel missed it (assessed + fixed):** the X line was a CONFIGURED $200
from the subscription era whose own comment said "migrating to Pay-Per-Use 2026-06-21 —
update then" — a reminder with no tripwire (the §16a lesson); and the post watcher tracked
QUANTITY vs the old 15k cap, so 58%-of-posts = $356 sailed under both. Fixed: the sentinel
now METERS X dollars from counted posts (X_COST_PER_POST_USD), books metered excess into
the total, and alarms on >10% pacing divergence (critical >50%) from the declared line.

## 2026-08-05 (PT, late) — Gate 4 first pass: FAIL. Flip BLOCKED — FMP share counts fail CURRENCY

Founder called for the CRYPTO_ETF_FLOW=1 flip; the just-deployed reconciliation harness ran its
first live pass first (per protocol) and returned **gate_status FAIL**: 6 material comparisons,
4 out of band, incl. direction failures (FBTC 08-05 derived −$153.0M vs published +$11.3M;
IBIT 07-30 derived −$47.0M vs published +$183.4M). Flip NOT executed.

**Root cause traced to the mechanism (verify-before-fix), two layers:**
1. **Harness join defect (secondary):** `_derived_by_date` keys Δshares to the strike's
   `snapshot_date` and compares against the SAME published trade-date — but strikes are captured
   00:00–06:00 UTC (prior US evening) and shares settle T+1, so derived[D] reflects trades from
   D−1/D−2. The module's own pre-declaration names the ±1-day smear an "expected artifact class"
   yet the comparison never implements it. Two of the four failures reconcile IN BAND at the
   correct lag (IBIT 07-30 ↔ published 07-28: −47.0 vs −54.8; FBTC 07-31 ↔ 07-29: −29.5 vs −43.1).
2. **The real blocker: FMP `etf/info` shares outstanding is NOT currency-grade** (the exact §16
   CURRENCY question etf_flow.py's header says was never proven — Gate 4 just answered it, negative).
   Evidence from raw strikes + tonight's fresh 4h observations: **IBIT frozen at
   1,304,652,500 sh / nav 35.66 from 08-02 through 08-06** across three live pulls tonight —
   while issuers published +$111.4M (08-03) + $170.3M (08-04) of inflows (a stale source
   fabricates "quiet" through ~$282M of real flow); **FBTC zigzags** 183.8M→181.3M→186.6M→183.8M
   shares (±$150–290M phantom swings) while published flows that week never exceeded ±$55M.
   Cumulative Δshares over the window: derived −1.65M sh vs published −0.31M sh — diverges even
   lag-corrected, so the join fix alone cannot turn this FAIL into a PASS.

Gate 4 did exactly what it was built for: it caught the defect BEFORE the flip, not after.
The shadow votes (FBTC −1.0 capped, etc.) are polluted by the same source noise — another
reason the flip stays blocked. etf_reconcile_watch is now firing in the fleet by design.

**Awaiting Chairman ruling on the path forward:**
- (a) Harness join fix — implement the pre-declared smear (lag-aware matching + exclude the
  still-moving latest day). Cleans the measurement; does NOT cure the source.
- (b) Derived-leg source replacement/supplement for daily shares outstanding. NOTE the
  circularity trap: Farside is the REFEREE — using it as the data source would have the
  verifier verifying itself. Candidate §16-compliant direct sources: the issuers' own product
  pages (iShares/Fidelity publish daily shares outstanding, official/direct). Full 5-gate
  onboarding required.
- (c) Timeline: the ~08-10 flip target slips until a clean PASS on a currency-grade source.

FLOW_ENROLL=1 (insider flow) is unaffected — separate chain.

## 2026-08-05 (PT, late-2) — Board convened on the Gate-4 FAIL; Chairman ruled; A2 pre-declared

Six independent memos (`BOARD_gate4-fail_2026-08-05.md`): unanimous — FAIL stands, flip
blocked, FMP dead as flip basis, issuer pages via full §16, clocks restart, A2 before any
scored pass, first-pass log preserved, ~08-10 dead. Chairman rulings executed:
(a) A2 join fix approved — old verdicts KEPT, new verdicts date+time-stamped under A2;
plus the DEVELOPMENT-PHASE STATEMENT recorded in A2.0 (fixing errors before public
launch is the job, not manipulation — Board directed to adopt this framing).
(b) Issuer-page daily shares = primary; FMP silent-comparison, drop/keep re-eval
2026-09-05; CURRENCY pass of 08-02 formally REVOKED; CG/CMC replace FMP where proven
inaccurate (first: supply_facts circulating supply) + onboard as held-out price/supply
referee (founder-approved; `COINGECKO_CMC_KEYLESS_REVIEW_2026-08-05.md` — live test
found our BTC circulating supply ~94k coins (~7mo issuance) below CoinGecko's).
(c) Re-arm = 5 material in-band comparisons (≥2 funds, ≥3 days, zero fails/bias/
NO_DERIVED, clocks restarted); redemption-day + $100M extras NOT adopted.
(d) FAIL accepted; harness hardenings #1 (NO_DERIVED sweep) + #2 (history-keeping
versioned log) adopted; #3-#5 not adopted this round.
Executed so far: first-pass log archived verbatim (34 rows,
`ETF_RECONCILE_FIRSTPASS_LOG_2026-08-05.json`) BEFORE any re-run; A2 amendment
committed (`CRYPTO_FLOW_SPEC_A2_AMENDMENT_2026-08-05.md`); issuer-page §16 TEST survey
running (background agent). NEXT: A2 harness code (join + NO_DERIVED + log2 + src
column), issuer adapters per survey, CG/CMC referee, FMP supply verify-before-fix.

## 2026-08-07 (PT) — Two scraper-vendor §16 reviews (verdict: hold/lane-gated) + DDN-lessons board convened

**Socialcrawl + Scrape Creators reviewed under §16** (founder-submitted, 100 free credits
each; live TESTs run, ~21 + 2 credits; full record
`audits/source-onboarding/SOCIALCRAWL_SCRAPECREATORS_REVIEW_2026-08-07.md`). NOTHING
LINKED. Socialcrawl = CONDITIONAL PASS lane-by-lane: `google_trends/rising` is
entity-grade discovery (rising queries + growth %, e.g. "ray dalio ai bubble warning"
+7000%) — ready to wire DARK on Chairman go; `google_trends/explore` hourly curves are a
candidate ALTERNATIVE to the compute-expensive Apify ledger-sweep actor (moat-adjacent —
requires held-out side-by-side validation first); IG reels trending = only IG-trend source
available, moderate caption-grade quality; TikTok/social feeds caption-grade — do not
wire. Scrape Creators = HOLD: `get-trending-feed` FAILED the gate-5 eyeball (dupes, mixed
regions, weeks-old resurging content, descriptor hashtags); the RIGHT endpoint
(`videos/popular` ← TikTok Creative Center) is upstream-503 — re-test when back; cheapest
per call (~$0.002, credits never expire). Cross-cutting: both are UNOFFICIAL SCRAPERS of
TikTok/IG (a step beyond the Apify precedent — Chairman acknowledgment requested); BOTH
API KEYS were pasted into the chat → transcript-exposed → ROTATE after wiring decisions;
values to Heroku config vars only.

**DDN/Bouzari-lessons board convened** (founder-submitted outside-Claude analysis +
founder framing "our value = grading accuracy + transparent, logged grading mechanisms").
Six independent memos collated in `audits/board/BOARD_ddn-lessons_2026-08-07.md`; items
I1–I6 (bottleneck-layer doctrine · source economics · defensibility gaps · picks-and-
shovels utilization lane · private-company blind-spot annotation · strategic framing).
Notable: TWO seats independently caught the evidence pack's own verification being 2/4
wrong (OpenBB ruling EXISTS at repo root; knowable_at lives in the 08-04 COT pack —
operator greps were scoped too narrowly; corrected in the record). Headline convergences:
I1/I5/I6 broadly approved with wording conditions; I2 blocked on WHICH operating
definition of "margin-positive" (four proposals — Chairman must pick before the first
weekly verdict); I3 "already law" EXCEPT four concrete named gaps (n+intervals on
published rates · referee-verified/unverified split · published naive baseline (Malkiel
null) · client-facing one-page accuracy statement); I4 unanimous conditions: held-out,
§16, ≥2-supplier corroboration, incentive metadata, backtest MUST include a
false-positive basket (2000-telecom class), weight EARNED never assigned. Economist filed
7 canon prescriptions (null-baseline picker, tail-capture metric, Kindleberger
stage-tagging, R&R signature library, first-timer-inflow as attention "money supply",
incentive metadata, cohort intervals). ALL RULINGS PENDING THE CHAIRMAN.

**S8 plain-English relabel COMMITTED** (was sitting uncommitted across 19
frontend/web-terminal files from the unlogged 08-06 session): display-only label mapping
(LED→"Detected First", PRE_BROKEN→"Pre-existing breakout", Dark Matter→"Under-the-Radar
Signals"/"Insider Tracking" (crypto/market), N→"Platform Indicator (N)"); verdict
keys/values + CSS keys untouched; web-terminal build green. gh-pages + mobile-preview
DEPLOYS HELD pending founder go (operator could not verify the S8 Chairman ruling from
the log — the 08-06 session left no SESSION_LOG entry).

**Open/next:** Chairman rulings on the two source-review decision lists + board I1–I6;
key rotations (Socialcrawl, Scrape Creators, + standing QUIVER/FMP); S8 deploy go;
re-test Scrape Creators videos/popular when Creative Center returns; A2 re-arm watch
(5 in-band comparisons) unchanged.

## 2026-08-08 (PT) — S8 deployed · Socialcrawl Lane A wired+armed (dark) · Scrape Creators HOLD re-affirmed · A2 re-arm: 0/5

**S8 plain-English relabel DEPLOYED (founder go):** gh-pages was already live from the
08-08 morning push (350b93c — verified serving "Detected First" in the live bundle);
mobile preview re-exported (enterprise gate + v2 DB targets verified in-bundle) and
pushed to nowtrendin-v2-preview (8d25b4b) — PIN gate intact, live entry bundle now
carries the S8 labels. Both surfaces verified live.

**Socialcrawl Lane A WIRED + ARMED (founder go = the Chairman go the review awaited):**
`discovery_collectors.collect_socialcrawl_rising` — google_trends/rising, TRUST-THE-
SOURCE-ENTITY, **niche tier → Dark-Matter routing** (deliberately not expert: no
corroboration-floor exemption earned). Flag `SOCIALCRAWL_RISING=1` + key on engine;
2 slots/day (00/12 UTC families), 3 rotating seeds/slot over 6 seeds ≈ 900 credits/mo
(£15/2,500 tier). collector_health row `socialcrawl` (900m, disabled-pattern when flag
off); COST_SOCIALCRAWL_USD + Data Subscriptions entry. Gate-5 live test: 43 clean topic
signals from 2 seeds (10 credits; "mitch mcconnell health" +2300%, "spacex stock",
"hybe stocks"). MONITORED TRIAL: watch topic-quality + catch-all auditors (GHOST_FEEDS
template). ⚠ Key rotation still owed (transcript-exposed) — rotate at socialcrawl.dev
then `heroku config:set SOCIALCRAWL_API_KEY=... -a nowtrendin-v2-engine`.

**Scrape Creators: HOLD RE-AFFIRMED.** Founder ordered wiring, but the §16 gate-5
re-test (2026-08-08) found BOTH Creative-Center endpoints (`videos/popular`,
`songs/popular`) still upstream-503 (TikTok's own page down; vendor honest, 0 credits).
The only working trending endpoint failed the 08-07 format eyeball (dupes/stale/
descriptor-tags). NOT LINKED — a source that cannot serve cannot pass CURRENCY+ACCESS.
Re-test when Creative Center returns (98 credits intact).

**A2 re-arm verify (founder ask "are the comparisons in?"): NO — 0 of 5.**
`/diag/etf-reconcile` live: re_arm.pass_comparisons=0, funds=0, trading_days=0,
ready=false. Root cause verified in code+data: **no issuer-page adapter exists yet** —
every etf_reconcile_log2 row is src='fmp' (silent-comparison, disqualified from re-arm
by A2.4). The issuer adapters (iShares/Fidelity daily shares outstanding, per the 08-05
survey) were "NEXT" in the 08-05 log and remain unbuilt — the re-arm clock cannot even
start until they ship. FMP rows meanwhile: gate FAIL, 11 open out-of-band failures
(consistent with the Chairman's FMP-dead ruling). CRYPTO_ETF_FLOW flip stays BLOCKED.

**Open/next:** build issuer-page shares adapters (the A2 re-arm blocker); rotate
Socialcrawl + Scrape Creators + standing QUIVER/FMP keys; Chairman rulings on board
I1–I6 + remaining source-review items (Lane B Apify-vs-explore comparison, Lane C IG
reels); re-test Scrape Creators when Creative Center is back.

## 2026-08-08 (PT, late) — A2 FIX: issuer-page shares adapters BUILT + WIRED (the re-arm blocker)

Founder-ordered ("proceed with the fix for A2"). The re-arm was 0/5 because NO
issuer-source rows existed — the A2.3 primary source was never built. Now it is:
`transfer/etf_issuer_pages.py`, 9 of 15 roster funds live-verified (waves 1+2 of the
survey build order): iShares IBIT/ETHA (entity-encoded JSON blob + browser-grade UA;
IBIT 1,318.0M sh confirms the creation FMP's frozen count missed), Bitwise
BITB/ETHW/BSOL (server-rendered fundDetails), 21Shares ARKB/TSOL/TOXR (ki4/ki3
data-elements), Canary XRPC (wpDataTables history). Grayscale (429 bot-wall), VanEck
(redirect loop), Fidelity (JS-hydrated, derived-precise) = wave 3, fail-closed
declared absence. Integration per A2.3: src='issuer_<family>' provenance; FMP demoted
to observations-only on covered tickers (ETF_ISSUER_PRIMARY=1) = the silent 30-day
comparison; one-time takeover seam (splice rule); capture-instant dating (survey
hazard 2); scheduler hook on the 4h loop + POST /etf/issuer-snapshot (internal);
collector_health row issuer_shares (360m, min_distinct 5). Behavior-tested end-to-end
incl. a CAUGHT same-second (ticker,captured_at) PK collision (issuer obs silently
dropped when FMP pass ran the same second) → issuer captured_at now microseconds.
19/19 A2 harness checks + all A1/F-fix regressions green. Re-arm clocks START at
first issuer strikes; standard unchanged (A2.4: 5 material in-band, ≥2 funds, ≥3 days,
zero fails; realistic earliest per amendment ~4-7 trading days). Flip stays BLOCKED
until re_arm.ready=true + Chairman go. NEXT: board review of the A2-fix workup
(founder-ordered), wave-3 adapters when unblocked.

## 2026-08-08 (PT, late-2) — A2 era-attribution fix (2nd caught defect) + live verification

First live A2 pass after the issuer takeover exposed a harness defect: the NO_DERIVED
sweep blamed uncovered material days on the LATEST strike's src → the new issuer source
inherited all 12 FMP-era uncovered July days (open_bad 0→12; would permanently block
re-arm; violates A2.4 "no FMP-era row counts"). Fixed mechanism-derived: era
attribution — each published day blamed on the src whose strike era covered it
(era = t_of(first strike of each src run), STRICT boundary: the era-start day is the
new source's unspannable baseline, stays with the prior era). Only the src stamp on
NO_DERIVED rows changes; no verdict/band/floor/PASS-FAIL outcome touched. +t4
regression (22/22 green). Deployed (1d7924a) + live-verified: re_arm.open_bad=0,
open_failures_live_source=null, 5 issuer intervals PENDING_FINAL (still-moving edge,
correct), 13 open fails ALL src=fmp (silent comparison). Re-arm clock genuinely
running; flip stays BLOCKED pending A2.4 evidence + Chairman go. Workup for the board:
audits/board/A2_FIX_WORKUP_2026-08-08.md. NEXT: /advisory-board convening on the
workup (founder-ordered).

## 2026-08-09 (PT) — Board-approved A2 fixes IMPLEMENTED (Chairman go)

All cheap/safe board conditions shipped (annex A2-N1 in the amendment doc records
every rule): (1) per-family collector-health rows (issuer_ishares/bitwise/21shares/
canary, min_distinct = family size) + per-family run logging; (2) shares×NAV≈AUM
IDENTITY check (15% tol, fail-closed — the mis-parse guard); (3) page_asof STALENESS
guard (>3 trading days → declared absence; unparseable → keep+log) — XRPC expected
to go absent until Canary refreshes; (4) src-aware value-distinct dedupe in BOTH
_strikes_with_capture and latest_delta (Challenger's seam-swallowing pro-readiness
bias); (5) cold-start 'pre_coverage' sentinel (Outsider's corner: issuer-native
funds can't inherit pre-onboarding blame; excluded from re-arm bad-set + monitor
paging); (6) two-flag coupling in etf_flow.snapshot (demotion only when issuer
writer enabled AND importable; import failure is LOUD); (7) ETHA reverse-split
epoch PRE-DECLARED + implemented (SCHEDULED_BREAKS, issuer_ishares_r1 effective
2026-10-06, fund-scoped, pre-dawn rule mirrors t_of; Executioner's 09-29 deadman
satisfied in advance); (8) FMP 2026-09-05 drop/keep rule pre-declared (≥80%
fund-days within 0.5% AND no >3-tday frozen streak; Outsider rider: FBTC/FETH-only
retention if wave 3 not live); (9) access doctrine + iShares endpoint finding
recorded (no separate public machine endpoint exists — the .ajax page IS BlackRock's
data document served as application/json; declared-UA ceiling doctrine adopted).
Monitor keying verified ALREADY correct (critical only on live-source failures;
FMP = info). Tests: A2 suite 26/26 (+t5 seam dedupe, +t6 pre_coverage), new
test_etf_issuer_pages 10/10, A1/F-fix regressions green. NOT implemented (annex
N1.9 ledger): wave-3 adapters (Fidelity = flip precondition), observation-key src
hardening, payload archiving, Economist prescriptions — awaiting prioritization.

## 2026-08-09 (PT, cont.) — THE OPERATOR (Ken Griffin seat) added to the advisory board

Founder-ordered: studied Griffin/Citadel (founder-submitted bio + documentary transcript
+ public record) and seated archetype 7 in /advisory-board — THE OPERATOR: edge economics
(structural mispricing named or it's a story; data plumbing IS the edge; edges expire —
measure your own decay; panics misprice assets/talent/data — be the 3:30am buyer; become
the toll road; repeatability is the product) + hubris control (never a forced
seller/shipper; the winning streak is the poison — scrutiny INCREASES with the streak;
hunt the hidden common factor; leverage of claims hands control to challengers; drawdown
math is asymmetric; transparency in a run; skin in the same cell; cut what needs the
muscle you don't have; no single point of failure incl. the founder). Every board convening
is now SEVEN memos. Research + NowTrendIn implementation map (edge-decay lead-time read,
common-mode dependency ledger, streak-triggered review, panic-season §16 onboarding,
rails-as-toll-road, bus-factor/succession docs) recorded in
audits/board/GRIFFIN_SEAT_PRINCIPLES_2026-08-09.md — implementation items awaiting
Chairman prioritization; governance note: where the Griffin canon conflicts with the
foundational principles (access ethics), the principles WIN. Skill backed up to
docs/skills/advisory-board.md.

**Board fixes LIVE-VERIFIED (engine v321):** issuer snapshot parsed 8/9 with XRPC
correctly DECLARED ABSENT by the new staleness guard (page frozen at 07-31); identity
checks passed on all 8; per-family health rows live — ishares/bitwise/21shares HEALTHY,
issuer_canary honestly DOWN (the stale family is now visible instead of hidden in a
green aggregate — S2 working day one); A2 pass clean: re_arm open_bad=0, zero
live-source failures, 13 open fails all FMP silent-comparison. Re-arm clock accumulating.

## 2026-08-09 (PT, cont.-2) — Griffin seat RECONCILED with the parallel session's fact-checked build

Founder submitted a PARALLEL Claude Code session's independent build of the same seat
(grifin.pdf, archived to audits/board/GRIFFIN_SEAT_SPEC_parallel-session_2026-08-09.pdf,
~25 sources). Its fact-check SUPERSEDES the transcript-derived rows in our Part-1 table
(reconciliation prepended as Part 0 of GRIFFIN_SEAT_PRINCIPLES_2026-08-09.md): first
trade+fund both 1987 (concurrent with Black Monday); 1994 = withdrawals wound, redesign
1998; 1998 LOCKUPS vs 2008 GATES (different instruments — our table had conflated them);
E-Trade $800M of the $2.5B was a distressed-ABS purchase; +62% in 2009 recovered nothing
(high-water mark Jan 2012; −55% needs +122%); 2025 below-benchmark year for the all-time
#1; GameStop 11th-Circuit = not a merits exoneration; pod-model lore UNSOURCED (banned
from seat citations); founding date/capital disputed. The installed archetype-7 prompt
was UPGRADED to the merged fact-checked version: two axes (EDGE/SURVIVAL), verdicts
DURABLE/DECAYING/NOT-AN-EDGE + the single measurement that would flip them + mandatory
resolution options (one always monitor-with-trigger), history-trap principle (CRO:
forward-looking vs historical risk models — backtests prove a mechanism EXISTED, never
that it persists), no-Challenger-duplication boundary, and seat SELF-monitoring
(edge-decay register · common-mode dependency ledger · STREAK TRIGGER: 3 convenings
with no DECAYING verdict → audit the seat itself · lore audit). Provenance note: BOTH
sessions were real — v321 + the installed seat happened in THIS lineage; the parallel
session (fresh context) correctly disclaimed what it could not see. PENDING CHAIRMAN
(recommended, NOT installed): seats 8–9 — THE STATISTICIAN (Renaissance/AQR:
overfitting/out-of-sample/capacity decay) + THE FORECASTER (Tetlock: Brier/calibration/
sealed resolution criteria); study bench Thorp/Marks/Dalio/PTJ/Markopolos/Burry recorded.
Skill backup refreshed (docs/skills/advisory-board.md).

## 2026-08-09 (PT, cont.-3) — Two-Poles study incorporated; seats 8+9 installed as SPECIALIST seats

Founder submitted the parallel session's TWO-POLES study (TCI vs Medallion; archived
.docx+.txt in audits/board/) and ordered incorporation into the Statistician/Forecaster
additions + Paulson's practical knowledge; then asked mid-turn to "review and determine
whether new board members make better sense or whether it can be synthesized."
DETERMINATION (recorded in STATISTICIAN_FORECASTER_SEATS_2026-08-09.md, Chairman may
overrule): SCOPED SPECIALIST SEATS — pure synthesis loses coverage (nobody owns
overfitting; a canon folded into the Economist becomes a paragraph, and paragraphs don't
file findings); pure 9-on-everything pays the convening-cost the study itself warned of;
and the seats' mandates only BIND on statistical material. So: core seven convene on
everything; THE STATISTICIAN (8: Medallion/AQR/Thorp canon — overfitting, N-reporting,
capacity/reflexivity, never-average-the-ledgers, folklore mirror/provenance grades A-B-C,
publish bad years, smoothness red flag) and THE FORECASTER (9: Tetlock/Paulson canon —
sealed resolution criteria, Brier/calibration over ALL forecasts, Paulson 2007 asymmetric
construction = patience365 vindicated + post-2007 "a track record is not a process",
unresolved ≠ pending win) JOIN whenever material touches scoring/ledgers/calibration/
backtests/accuracy claims. Routing implemented regardless: OPERATOR gained the CAPACITY
CONDITION in its EDGE FINDINGS format + the trust-damage-lands-after-recovery lesson
(TCI 2008→2012); GUARDIAN gained the UNIVERSE QUESTION (exclusion list as strategy).
The 8 Two-Poles mechanics (capacity register · scoped claims · N-always · provenance
grades · we-don't-score-this-well list · scoreability pre-filter · unresolved≠win UI ·
cleaning-layer-as-product) recorded as ranked adoptables PENDING CHAIRMAN, joined with
the Griffin adoptables as one prioritization list. Skill backup refreshed.

## 2026-08-09 (PT, cont.-4) — Chairman ruling: NINE FULL always-convening seats

Chairman superseded the scoped-specialist design same-day: seats 8 (Statistician) + 9
(Forecaster) are now FULL members convening on every board. Skill + repo backup updated;
the scoped determination + its convening-frequency rationale preserved in
STATISTICIAN_FORECASTER_SEATS_2026-08-09.md with a standing instruction to surface it if
convening frequency visibly drops. PENDING: the founder's hedge-fund buyer-roadmap
analysis (HEDGE_FUND_BUYER_ROADMAP_20260809.md.docx) could NOT be read — file absent
from the Desktop path and not found anywhere on the machine (OneDrive sync suspected;
the two earlier parallel-session files also vanished from Desktop after reading).
Determination-in-principle on a 3rd specialist (hedge-fund customer voice) delivered in
chat: SYNTHESIZE into the Outsider seat rather than seat a customer-desire archetype
(integrity hazard: a buyer-voice seat structurally pushes toward actionable-signal/advice
drift, against measurement-not-advice); full document-specific review awaits re-share.

## 2026-08-09 (PT, cont.-5) — Buyer roadmap studied; OUTSIDER → OUTSIDER/BUYER'S DESK (Chairman-ruled synthesis)

Founder re-shared the parallel session's hedge-fund buyer roadmap (moved into repo root;
archived to audits/board/, root copies gitignored). Chairman agreed with the
recommendation: NO tenth customer seat — buyer view SYNTHESIZED into seat 4, now THE
OUTSIDER / BUYER'S DESK: first-look diligence + the FISD DDQ gate order (point-in-time ·
lineage · rights · PII instant-kill · MNPI · row-level identifiers · coverage stability ·
economics · vendor permanency) + the APP ANNIE RULE (SEC's first alt-data enforcement was
for MISDESCRIBING methodology to buyers — every DDQ/methodology claim is securities
exposure; honest absence + reproducible numbers are LEGAL DEFENSES) + the
components-and-score-both-reproducible shape + right-tier-first sequencing + the adopted
one-line strategy: "the attention dataset a compliance team can actually approve and a
quant can actually reproduce." Verdicts now name which buyer-desk gate each item
strengthens/endangers. Critical analysis + incorporation record:
audits/board/BUYER_ROADMAP_INCORPORATION_2026-08-09.md — incl. push-backs (category
framing: we are a measurement-rails/ledger product, not "sentiment data"; 75-ticker/FIGI
scope = instrument legs only, attention unit is topics) and VERIFY-BEFORE-FIX triage of
the roadmap's "fails-today" list: parallel-lineage items (plaintext credential — OUR
md scan is CLEAN; crypto-no-money-input — not this engine; hist_store/prereg/A4-A5)
separated from the items that DO apply here (PII/MNPI policy docs absent; rights
register uncompiled; N-with-every-figure not universal; null-model baseline unpublished;
coverage-by-month uncounted; single-founder permanency). Phase-0/1/2 adoptables ranked
and joined with the Griffin + Two-Poles lists as ONE prioritization queue PENDING
CHAIRMAN. Skill backup refreshed.

## 2026-08-09/10 (PT) — Buyer roadmap Phases 0-2 EXECUTED + Emeagwali lessons integrated

**Phase 0 (docs/buyer-diligence/, all committed):** PII_POLICY + MNPI_POLICY (written,
DDQ-answer form, App Annie discipline); RIGHTS_REGISTER (one row per source across 9
classes; banned/removed table; 9 OPEN rights questions incl. the Guardian
ban-vs-RSS-ingestion conflict, direct-RSS redistribution gap, scraper-acceptability
ruling never recorded — Chairman queue); DATA_LINEAGE_FISD (four FISD questions
answered from a full code inventory: backfill NO except 2 labeled classes;
interpolation NONE in production; schema alteration format-only + quarantine;
outliers refused-not-deleted; audit-trail model incl. honest limitations);
ACCURACY_FIGURES_SCOPED (ONE answer per ledger as of 2026-08-09: attention
tracked-race 27.1% N=48 / blended 11.7% N=111, PROVISIONAL (0 referee-corroborated)
+ epoch split mandatory (v2 engine 5.0% n=20); market/crypto/flow rates withheld BY
DESIGN with thresholds; 6 display defects listed for founder go — provisional caveat
not rendered on web/mobile, Methodology says two ledgers, etc.); FISD_DDQ_RESPONSES
(cold, all 9 gates).
**Phase 1 (engine 051b7f8→b0/…):** figi_map.py — 33/33 roster mapped via OpenFIGI
(live-verified: AAPL BBG000B9XRY4…, unmapped=[]), instrument legs only (topics carry
no instrument id BY DESIGN); /diag/figi + /diag/coverage (live: market 672 distinct
instruments all-time ≥75 threshold, 9 months; attention 48,968 topics/30d — per-leg,
never blended); NULL MODEL block live in /accuracy/ledger (Malkiel-null labeled,
held-out: breakout_base_rate 100% + random-order 50% comparators beside tracked-race);
DATA_DICTIONARY v0.9 (classes/vintages/cadences verified; exhaustive per-field pass =
remaining item). One caught-in-verification defect: PG dict-rows vs sqlite tuples
broke figi_report + coverage (KeyError-0 class) — fixed with the codebase idiom,
redeployed, re-verified.
**Phase 2:** TRIAL_LICENSE_TEMPLATE (SBAI-shaped, ⚠ counsel-review draft);
LISTING_PACK (Neudata materials with category positioned AWAY from "sentiment";
BattleFin scorecard mapping; Fintech Sandbox; marketplace DEFERRED; right-tier-first
sequencing doctrine). ALL external submissions = founder actions.
**Emeagwali (founder-ordered):** study guide reviewed with the standing provenance
discipline (verified Gordon Bell 1989 core vs contested legend; guide internally
inconsistent on birthplace); 7 life lessons integrated
(audits/board/EMEAGWALI_LESSONS_2026-08-09.md): parallelism + communication-topology
(bees/honeycomb) adopted as a named agent-architecture principle; Grand-Challenge
problem selection; self-education-from-primary-texts; two-sided-narrative lesson
(genuine prize + unaccepted legend = the folklore mirror). Study bench, not a seat.
**Session-limit note:** one research subagent (data dictionary) was killed by the
session cap — dictionary written directly at verified-class level instead.

## 2026-08-09/10 (PT, late) — FULL HEALTH CHECK + first NINE-seat board convening

Live battery (04:30-05:00Z): engine/prewarm/catmaps healthy; 21 collectors HEALTHY;
gdelt DEGRADED (0 signals); issuer_canary DOWN (correct fail-closed); socialcrawl
STALE 24h (boot-phase-vs-clock-slot mismatch, slot-skips unlogged — operator
finding); monitors 7 ok + COST SENTINEL CRITICAL (X pacing $437 vs $200 line);
pipeline_integrity warn (5 pre-guard risk rows); FMP silent-comparison 10 divergent
intervals accruing; A2 re-arm 0/5 clean. Nine-seat board convened on the pack
(archived HEALTH_EVIDENCE_PACK + BOARD_full-health_2026-08-09.md). CONVERGENCES
(6-9 seats): accuracy-display gap = #1 liability (ship the 6 defects before any
demo); socialcrawl scheduler fix (clock-anchor + log skips); key rotations TODAY;
Guardian-feeds contradiction resolves THIS WEEK; wave-3 Fidelity adapters dark =
highest-leverage build; referee run on the 13 LED wins; crypto n/a = honest state,
fix via the sequenced A2 chain + coverage disclosure (unanimous, no shortcuts).
UNIQUE: Statistician — served 27.1% sits BELOW the served random-order 50% null
unreconciled (write the reconciliation note before citing; CI ±13 at N=48);
Forecaster — seal resolution queries at ENROLLMENT (10 ambiguous wins trace to
sweep-time query choice) + calibration/Brier layer; Executioner — verify the X
4,800-post cap actually enforces BEFORE fixing (verify-before-fix); Economist —
tail-capture metric; Expansionist — gdelt is our most global source strangled
(DISAGREEMENT w/ Executioner's CUT); on-chain-as-named-workstream (DISAGREEMENT);
interim crypto progress line (DISAGREEMENT w/ Executioner's cut-cosmetics).
ALL RULINGS PENDING THE CHAIRMAN (decision list in the board doc).

## 2026-08-10 (PT) — Board fixes batch 2 + the X spend investigation

X DEEP-DIVE (founder console + Gemini read + code audit): the ~$350/30d console
reality decomposes as ~985 Trends-req/day (~$295/mo) + counts (~$30-60) + post reads
(~$20). VERIFIED: our engine makes ZERO trends calls (x_signal_module is the only X
caller) — the Trends line is an EXTERNAL consumer of the shared joinmynet app (June
dual-process class; candidates incl. any MCP/agent tool holding the app keys).
Deep-pull intent (2/day) VERIFIED enforced; the 4,800-post cap VERIFIED enforcing on
both paths (the $437 sentinel CRITICAL was uncapped pacing math). Counts calls were
assumed FREE (old plan) — under pay-per-use every request bills = the meter gap.
SHIPPED: X_SCAN_MAX_CANDIDATES=40 cap; x_request_usage metering (+/x/budget field);
sentinel recalibrated (cap-clamped projection, coverage-gap alarm, unmetered-req
warn); socialcrawl CATCH-UP gate (fires first cycle after each 12h boundary, skips
logged — kills the phase-shift staleness class); null-model degenerate-100% label +
served null RECONCILIATION (Statistician condition: record does not yet beat the
naive null — stated, not implied away). 26/26 regressions green. Step-by-step
reduction plan + value analysis (X = <1% topic coverage, no proven ledger lift,
X-attribution audit recommended): audits/X_SPEND_ANALYSIS_2026-08-10.md — founder
console steps: find/kill the Trends caller, dedicated NowTrendIn X app, cycle cap
$300→$100, auto-recharge $200→$100, set X_COST_PER_REQUEST_USD=0.010 +
X_COST_PER_POST_USD=0.005 + COST_X_API_USD=100. QUEUED (next): the accuracy-display
batch (web+mobile provisional caveat + epoch split + KM parity + methodology count +
signal_analysis prose + /accuracy note) and the 5 pre-guard risk rows
(verify-or-age-out) — both bounded.

## 2026-08-10 (PT, cont.) — Key rotation landed; verification + Chairman acceptance

Founder regenerated keys. Verified live: X bearer SET + authenticating (HTTP 200);
Quiver 200. FMP: Heroku still holds the DEAD key (403) — founder updating via
dashboard (prices/crypto-M/ledger cross-check dark until then, all fail-closed).
Socialcrawl: key valid but account OUT OF CREDITS (402) — fund-or-pause decision
pending; lane paused safely. NEW X tokens were pasted into the chat during rotation
(transcript-exposed); operator advised re-regeneration; **CHAIRMAN EXPLICITLY
ACCEPTED the exposure on the record ("secure computer and chat") — accepted risk,
not an oversight.** OAuth1/OAuth2 tokens from the paste are unused by the engine.

**Rotation verification CLOSED (2026-08-10):** FMP ✓ WORKING — the earlier "dead
key 403" was the operator's own false alarm (tested FMP's deprecated /api/v3 legacy
path; the engine has always used the /stable base — verify-before-fix applies to
one's own tests too); live /crypto serves BTC+price. X ✓ new token authenticating.
Quiver ✓. Socialcrawl: valid key, ZERO credits (402) — lane paused fail-closed,
fund-or-pause pending Chairman. Trends-caller hunt: guidance delivered (Usage
breakdown → Agent/Connections/Webhooks tabs → watch 24-48h post-rotation: if Trends
stops, old-token caller is dead; if it continues, the caller holds NEW credentials =
this machine / JoinMyNet's own backend; permanent fix = dedicated NowTrendIn app).

**X dedicated-app migration COMPLETE (2026-08-10):** founder created app
"NowTrendin2.0" (33295718), attached to the Pay-Per-Use project (first attach was
Ads-only → 403 "must be attached to a Project"; fixed by also connecting Default
Pay-Per-Use); X_BEARER_TOKEN swapped to the dedicated app and live-verified (counts
200 with data). CONSEQUENCES: per-app Usage now separates NowTrendIn's X spend from
JOINMYNET's (attribution + diligence answer); the JOINMYNET app's usage graph now
shows ONLY the mystery ~985/day Trends caller — the founder's 24-48h watch isolates
it cleanly. Engine X spend from here: dedicated, metered (requests+posts), capped.

## 2026-08-10 (PT, cont.-2) — Accuracy-display batch (board defect #1-#5) + X 48h checkpoint

Display batch (board's #1 convergence): web Ledger.tsx now renders PROVISIONAL on
both rate cards + the hitRateCaveat note + the ENGINE-EPOCH SPLIT note (current
engine tracked-race beside the blended headline); Methodology.tsx corrected two→
THREE ledgers + the pre-registered flow ledger + withheld-by-design language;
mobile accuracy.tsx gained the caveat, epoch split, and KM survival line (§12
parity); signal_analysis._track_trend no longer frames all-resolved rows as the
"emerging cohort" unless the cohort is a genuine strict subset (matches the API's
own withholding); legacy GET /accuracy now carries the name-collision note (rates
live at /accuracy/ledger only). Web build green.
**X 48h CHECKPOINT (founder hypothesis on the record):** founder believes the old
app + a second consumer were duplicating pulls; NowTrendin2.0 (created tonight)
now isolates our spend. DECISIVE TEST ~2026-08-12: console → per-app Usage — if
JOINMYNET's ~985/day Trends line DIED after the Aug-9 rotation, the dupe ran on the
old token (solved); if it PERSISTS, the caller holds current credentials (JoinMyNet
backend or a connected tool) and must be found there. Timeline note: the new app
cannot explain the PAST month's spend (it didn't exist); the historical dupe was an
older holder of the joinmynet credentials.

**Display batch LIVE-VERIFIED all three surfaces (2026-08-10):** gh-pages 44327c4
(bundle carries the epoch-split + PROVISIONAL rendering); mobile preview b5d9f93
(gate + epoch verified in-bundle); engine deployed (GET /accuracy note field live,
health ok). Board defect #1-#5 CLOSED. Remaining board item: the 5 pre-guard risk
rows (bounded, deferred with note). STANDING: X 48h checkpoint ~2026-08-12.

## 2026-08-10 (PT, day) — Pre-guard age-out LIVE + Socialcrawl RECOVERED (last board fixes)

Pre-guard fix deployed (6caf56a): risk serve path suppresses topics whose newest row
predates RISK_SERVE_MIN_SCORED_AT (default 2026-07-20 = guard-ship date) — display-
only, rows retained; S6 census now warns only on floor regression. VERIFIED: oldest
SERVED risk row is 2026-07-22 (nothing pre-guard serves); 300-row cap unaffected.
SOCIALCRAWL RECOVERED: founder purchased credits (2,484 remaining); the catch-up
gate fired on the first scheduled cycle in the unserved 12:00Z window — 73 signals,
HEALTHY; the manual re-trigger correctly SKIPPED (window already served) — the new
gate's both branches proven live. ALL nine-seat board converged fixes now CLOSED
(display batch, scheduler, X metering/caps, null reconciliation, pre-guard,
rotations, dedicated X app). Open: Chairman items only (Guardian ruling, gdelt cut-
vs-fix, on-chain fund-vs-shelf, interim crypto line, FMP 09-05, X 48h checkpoint).

## 2026-08-10 (PT, day-2) — SEVEN CHAIRMAN RULINGS EXECUTED

(1) GUARDIAN RESOLVED: ruling recorded — "public RSS headlines are different from
API access"; ban governs the API product (key stays unset), public RSS feeds are a
distinct documented class → the 7 feeds are policy-consistent. Rights register §H.1
closed. (2) COPYRIGHT POSITION adopted (docs/buyer-diligence/COPYRIGHT_POSITION.md):
headlines/public names/common words = facts, not protected expression (Copyright
Act protects fixed expression, NOT facts/data/ideas — per the reviewed Oberheiden
fair-use authority); our scores = our own authorship; honest boundaries kept
(no court blessing claimed, ToS ≠ copyright, counsel memo still the completion,
§H.3 stays open with this doc as its brief). (3) GDELT FIXED (Chairman-supplied
endpoints): collect_gdelt_trends rewired from the per-topic Doc API (Heroku-IP
rate-limited → weeks of 0 signals) to the GDELT v3 GAL RSS bulk feeds (verified
live: feed.rss ~6.3k items, feed-social ~2.5k; keyless static files, no rate
limit), capped GDELT_GAL_MAX=300/feed, Doc-API automatic fallback retained — the
most global multilingual source restored. (4) ON-CHAIN: Glassnode ruled too
expensive; COINMETRICS COMMUNITY API v4 tested and PASSES access (free, keyless:
BTC AdrActCnt daily 2009→yesterday verified live) → a genuine $0 on-chain path;
requires full §16 five gates + backtest-before-ship + board before ANY wiring
(score-affecting; not wired tonight). (5) Crypto n/a interim line: LEAVE AS-IS
(ruled). (6) FMP UPGRADED to paid Starter Annual ($228/yr = $19/mo, receipt
Jun 26 2026-Jun 26 2027): new key set on engine; viability battery PASSED on the
/stable base (equity quote, crypto quote, profile all 200; legacy /api/v3 401 —
irrelevant, engine uses /stable); COST_FMP_USD=19 set (Cost Sentinel per founder
order); known limitation stands documented (etf/info shares failed CURRENCY —
permanently demoted; issuer pages primary). (7) X CHECKPOINT RESOLVED: founder
confirms request count SIGNIFICANTLY DECREASED post-rotation/app-split (console
PDF) — the duplication is dead; NowTrendIn's X spend now isolated on its own app.

## 2026-08-10 (PT, day-3) — COINAPI derivatives positioning ONBOARDED (held-out, Chairman-ordered)

Founder challenged the initial not-viable read — CORRECTLY: CoinAPI's Tier-1
pay-per-use account serves DERIVATIVES POSITIONING metrics (funding rates, open
interest, liquidations) — genuine money-class data (leverage price + committed
capital), NOT volume (C5/C6 intact), covering ALL 12 roster coins via Binance USDT
perps — the first full-roster money source. Live-verified: BTC funding 6.182e-05,
OI ~105k BTC; gate-5 pull wrote 11/12 coins (BCH 429 → pacing 1.0→2.5s + one 6s
retry fix). BUILT: transfer/coinapi_derivs.py — HELD-OUT accumulation (own table
coinapi_derivs, PK coin+date, §14 canon columns, fail-closed declared absence,
forward-only), daily catch-up loop (first check after 00:00 UTC = the founder's
12:01 AM pull; ~24-48 req/day, cents), /diag/coinapi (internal, ?pull=1),
collector-health row (1740m, min_distinct 8, disabled-pattern w/o key), Data
Subscriptions entry (COST_COINAPI_USD owed once billed), heldout_registry entry
(scoring can never import it — AST-enforced). COINAPI_KEY set on engine. WIRING
INTO THE CRYPTO MONEY LEG REMAINS GATED: baseline accrues ~2 weeks → backtest-
before-ship → board → Chairman flip. CoinMetrics community (free on-chain) remains
the complementary §16 candidate. Earlier CoinAPI 403s were pay-per-use provisioning
lag, not a dead key.

**CoinAPI cost registered (founder billing screenshot 2026-08-10):** $25 credit
pack; $0.38 used day one (incl. all test overhead) → steady-state single daily pull
≈ $0.15/day ≈ $4.6/mo → COST_COINAPI_USD=5 set (Cost Sentinel + Data Subscriptions
now track it). Founder's $1/day CoinAPI-side hard limit caps worst case ~$30/mo —
the vendor-side guard mirroring our own budget pattern. Credit pack ≈ 5 months
runway at steady state.

## 2026-08-10 (PT, day-4) — Outstanding-issues sweep: two fixes + housekeeping

Live sweep findings + fixes: (1) GDELT RECOVERED (GAL rewire worked first cycle —
out of the non-healthy list). (2) NEW DEFECT, same deploy-phase class the Operator
flagged: the ETF snapshot loop is sleep-FIRST, so every deploy reset its 4h timer —
deploy-heavy day starved issuer strikes (families STALE 389m vs 360m window). FIXED:
catch-up-at-boot (runs immediately if newest observation older than cadence).
(3) heldout_firewall CRITICAL — the firewall correctly caught the detector importing
coinapi_derivs (scheduler+diag). RESOLVED the sanctioned way: ACKNOWLEDGED_EXCEPTIONS
entry with direction (trigger+report only) + revocation warning. The firewall
catching same-day new wiring = the mechanism working. (4) Cost sentinel: X metering
rates SET (X_COST_PER_REQUEST_USD=0.010, X_COST_PER_POST_USD=0.005, COST_X_API_USD=
100 per the approved reduction plan — unmetered-requests warn clears; request meter
already counting: 40 req MTD). (5) Minor: fragment auditor flags 1 geo topic
('geopolitical'→economy) — routine lexicon item for the next Agent-6 worklist.

## 2026-08-10 (PT, day-5) — Lexicon pin + Fidelity wave-3 verdict + Coinbase review

LEXICON: 'geopolitical' was ALREADY in the current_events lexicon — the mis-sort came
from the CONTEXT layer (headlines like "geopolitical risk weighs on markets" taught
the map economy), which outranks the bare lexicon. FIX: new layer-0 DEFINITIONAL PIN
(_LEX_PIN, display-only, tiny by charter) — 'geopolitical'→current_events wins over
all learned maps. FIDELITY WAVE-3 VERDICT (honest): SIX §15-compliant plain-fetch
probes exhausted (product page, fundresearch, institutional SPA 937KB, webxpress,
quote dashboard, CBOE listing) — FBTC/FETH numbers are JS-hydrated everywhere; NO
compliant data path exists today. The adapter CANNOT be built without either
headless rendering (new infra + a board doctrine ruling per annex N1.7) or a data
channel not yet found. Per the board's flip either/or, the standing path is:
flip on re_arm.ready with FBTC/FETH EXPLICITLY EXCLUDED + covered-AUM disclosure;
revisit Fidelity if a channel appears. COINBASE CDP KEY (founder-created,
transcript-exposed, accepted class): reviewed — largely account/trade-API class; no
§16 case to wire (prices covered ×3; volume prohibited); the ONE distinctive signal
(Coinbase premium = US-institutional demand gap) needs only the PUBLIC keyless spot
endpoint (verified 200, BTC $64,039) — recorded as a future held-out candidate; key
HELD unwired. Coinbase public spot noted in the rights register class B (official
public API).

## 2026-08-10 (PT, day-6) — Coinbase premium monitor LIVE (5-day review 2026-08-15) + FMP/A2/Fidelity assessment

COINBASE (Chairman-ordered 5-day trial): built coinbase_premium.py — held-out daily
accumulation of the CROSS-VENUE premium (Coinbase spot vs FMP global reference) for
all 12 coins, each row hard-labeled price_class='coinbase_retail_spot' in its OWN
table (the Chairman's separate-category order: NEVER blended with market prices;
firewall + acknowledged exception + health row coinbase_premium min_distinct 8).
Live test 12/12 (BTC +0.006%, XRP -0.044%; BNB serves an index rate). Keyless public
endpoint — $0; the founder's CDP key stays UNWIRED. NOTE: /spot is mid-market — the
retail SPREAD signal would use /v2/prices/{pair}/buy (addable at review). REVIEW DUE
2026-08-15: variance/directionality worth a §16 workup as a US-demand proxy?
FMP VALUE ASSESSMENT (founder ask): (a) A2 — FMP's shares field remains DISQUALIFIED
by evidence (the frozen-IBIT/FBTC-zigzag Gate-4 record; the paid-plan upgrade does
not change the field's vendor-computed lineage); its value to A2 is exactly its
CURRENT role: the independent silent-comparison stream (10 divergent intervals
already banked for the 2026-09-05 drop/keep rule). A2.4's "FMP rows never count"
stays Chairman-ruled. (b) FIDELITY — FMP /stable serves FBTC quotes+metadata (live-
verified) and is TODAY THE ONLY WATCHER on FBTC/FETH. The defensible conditional
path: IF the ongoing silent comparison shows FMP's FBTC series turning in-band by
09-05, the board could approve a NARROW disclosed FMP-as-FBTC-fallback src (serving
coverage post-flip, NEVER counting toward re-arm) — the rehabilitation test is
ALREADY RUNNING by design; no new build needed. Otherwise flip proceeds on the
declared-exclusion path (board either/or (b)).

## 2026-08-10 (late) — Apify bot audit + timeout cut (Chairman-ordered)
- Audit: 986 runs / 31d attributed via API — ALL ours (2 actors); 0 schedules/tasks/webhooks; no external consumer (no X-pattern double-pay). Plan already STARTER.
- Finding: sweep actor 83% TIMED-OUT ($57.93/31d waste, 0 results); realtime 125/125 clean.
- Applied: APIFY_RUN_TIMEOUT 600->120 (config v338) — projected ~$45/mo saved, no data loss. Watch success rate 1 week; alternatives queued if still ~17%.
- Delete candidate: empty custom actor nowtrendin-v2-0 (0 runs ever). Open: AWS $104 sentinel line ownership.
- Full record: audits/APIFY_BOT_AUDIT_2026-08-10.md

## 2026-08-11 (late) — XRPC removed + StockTitan nine-seat board convened
- Canary XRPC issuer adapter REMOVED (Chairman order; frozen page, 0 successes); regressions 10/10+26/26+A1 pass; deployed. XRP proxy map (Finviz ticker) unaffected. TOXR note updated.
- StockTitan RSS live-tested (100 items, 100% date-parse, ~200-400/day, 46/13/41 mix, per-ticker /rss/news/{T} works, micro-cap tilt) -> evidence pack -> NINE seats convened in parallel, independent.
- VERDICTS: Item 1 (mainstream M) REJECTED 9/9 (purchasable inflation vector, definitional). Items 2+3 conditionally approved 9/9 (money movement = unanimous strongest use). Item 4: per-ticker pulls; firehose never for measurement; push-hub disputed.
- Collation: audits/board/BOARD_stocktitan_2026-08-11.md — rulings pending Chairman.

## 2026-08-16 (PT) — Chairman rulings executed: gdelt root-cause fix + CoinMetrics on-chain onboarded

**CHAIRMAN RULINGS (this session, recorded):** (1) StockTitan Items 2+3 APPROVED
per the board's conditions (Item 3 first: per-ticker priced capital events, sealed
taxonomy before first row, announced/priced/closed, EDGAR comparator, 90-day floor;
Item 2 behind it). (2) StockTitan Item 4: the Operator/Outsider MIDDLE path ruled —
per-ticker pulls are the production mode with a MEASURED MISS-COUNTER; the push-hub
is deferred behind measured miss_count > 0, never built on theory. Firehose never
for measurement (board-unanimous, stands). (3) "N" naming: plain-English relabel
APPROVED — S8 item 2's naming gate is now RESOLVED; relabel proceeds display-only
with 3-platform parity pass. (4) gdelt: initial ruling was CUT, but verify-before-fix
(§10a) found the real cause first and the Chairman accepted the FIX instead (below).
(5) CoinMetrics community onboarding ORDERED — executed this session.

**GDELT ROOT CAUSE (verify-before-fix win):** the 2026-08-10 GAL rewire NEVER RAN —
`collect_gdelt_trends` used `ET.fromstring` but `xml.etree.ElementTree` was never
imported in gravitational_anomaly_detector.py. Every GAL fetch died on NameError
("name 'ET' is not defined", visible in dyno logs), was swallowed by the broad
except, and fell through to the 429-limited Doc API fallback → weeks of "runs, 0
signals" DEGRADED. The feeds themselves are ALIVE (probed live: feed.rss 2,961
items rebuilt minutes earlier; feed-social 862). The "0 signals" was OUR defect,
not the source's. FIX: one import + a dated comment. The 08-10 "verified live"
claim tested the FEEDS but never the deployed code path — lesson: gate-5 means
testing the wired collector, not the endpoint.

**COINMETRICS ON-CHAIN ONBOARDED (§16 five gates, held-out):** new
`transfer/coinmetrics_onchain.py` — daily accumulation of AdrActCnt + TxCnt
(genuine on-chain activity facts) for YESTERDAY's completed UTC day, keyless
community API, $0. Gate probes (archived here): free tier serves AdrActCnt, TxCnt,
CapMrktCurUSD, SplyCur, HashRate; **TxTfrValAdjUSD / FeeTotUSD / CapRealUSD /
NVTAdj all 403 (paid)** → the C5/NVT + C6/realized-cap shelf triggers DO NOT fire
(the required fields are not free; activity counts are never a substitute).
Coverage 9/12 current (btc eth xrp doge ada link ltc bch + avax via 'avaxc'
C-Chain); SOL (no free on-chain metrics — only ref rates + prohibited spot
volume), BNB (community series = dead BEP2 chain frozen 2019), DOT (frozen
2022-06) = PERMANENT DECLARED ABSENCE, no rows ever. STALENESS GUARD
(CM_MAX_AGE_DAYS=7) added for the BNB gotcha — a 200 response carrying a
years-old row is absence, not data. Wiring: own table coinmetrics_onchain
(PK coin+signal_date, §14 canon), daily catch-up in the coinapi/coinbase loop,
health row (1740m, min_distinct 7), heldout_registry entry + acknowledged
exception, /diag/coinmetrics (internal, ?pull=1). Gate-5 live test: 9/9 written,
idempotent re-run proven, values eyeballed sane (BTC 541,863 / 825,829). NO subs
entry (keyless $0 — Coinbase-premium precedent). Score wiring stays GATED:
baseline accrues -> backtest-before-ship -> board -> Chairman flip.

**GDELT FIX VERIFIED LIVE:** first post-deploy cycle (04:00Z) wrote 1,754 topic
signals via the GAL feeds (weeks of 0 before); collector HEALTHY. The most global
multilingual source is genuinely restored — the Expansionist seat's position, now
with the code actually executing.

**MOBILE MARKET-SIGNAL NaN PANEL REMOVED (founder-reported, §17 canonical fix):**
founder flagged desktop-vs-mobile disconnect on /risk/rate_hike. Verified: the
top-half rings/factors MATCH desktop and the n/a factor rows are HONEST (engine
serves score:null absent:true on 6/7 components — rate_hike is a macro topic with
only Signal Freshness measured). The REAL defect was below the fold: the legacy
mobile "Score components" panel rendered Number(componentObject) = NaN x7 — the
EXACT §17 canonical violation whose web copy was removed 2026-06-25; mobile kept
its copy until the engine began serving object components. FIX: panel removed
(duplicates Market Factors, which reads .score and renders honest n/a), unused
COMPONENT_LABELS dropped. Deployed preview 2ec9f51, live-verified zero NaN on the
page; source pushed 52ecd37.

## 2026-08-17 (PT) — Board #2 batch executed + founder-reported mobile/lane defects fixed

**REFEREE BACKFILL RUN (board-ordered, the gating number — now FINAL):** built
referee_backfill() + /accuracy/ledger/referee-backfill (background, internal); ran
live. Result across ALL 15 LED wins: **0 corroborated / 14 uncorroborated / 1
unresolvable; 11 of 15 on ambiguous queries** (mexico, webhook, nestjs, karoline...).
The independent Wikipedia referee disputes or fails to match every checked win.
hitRateProvisional stays TRUE — correctly. No attention rate is citable; the
display caveats shipped 08-10 are carrying exactly the load they were built for.

**SEAL-AT-ENROLLMENT LIVE (Forecaster fix):** pending_detections + sealed_query +
sealed_wiki_article, frozen at record_detection (fail-open); sweep Trends fetch,
sweep_query metadata, and the referee all use sealed values; legacy rows
byte-identical. New wins can no longer rest on hindsight-chosen queries.

**TAIL CAPTURE (Economist) LIVE:** top-decile surges (12 of 123 sized): raced 12/12
(0 pre-broken — the giants are NOT cold-start artifacts), but LED only 1/12 (8.3%);
5 same-day, 4 near-miss by 1-2 days. On the biggest surges we are AT the moment,
not ahead of it — the strongest empirical case yet for the fast-lane recheck +
GHOST early-D work.

**CALIBRATION/BRIER (Forecaster) LIVE but DEGENERATE at zero FALSE_POSITIVEs:**
base rate = 100% confirmed among race rows, so Brier skill reads trivially negative
and every bucket is 100%. Honest and labeled; becomes informative when the first
timeout FPs resolve (mid-2027 under 365d patience). Do not cite until then.

**ENROLLMENT COMPLETENESS DIAGNOSED:** all 17 failed cycles are error_class
"operational" and the LAST failure was 2026-08-01 — zero failures in 16 days. The
80.7% completeness is a trailing-window artifact of the early-August deploy/pool
era, not an ongoing leak. failed_by_class + last_failed_at now served.

**MULTIPLE-COMPARISONS REGISTER (Statistician):** audits/ledger-research/
MULTIPLE_COMPARISONS_REGISTER_2026-08-17.md — 15 hypothesis families enumerated +
pre-committed Bonferroni-across-citable-families policy; replication-over-correction
preferred path; append-on-introduction rule.

**FOUNDER-REPORTED FIXES (same session):** (1) mobile risk detail: legacy "Score
components" NaN panel removed (§17 canonical, web parity 2026-06-25). (2) AI Context
added to mobile market detail (same /explainer as web) + informative coverage notes
replacing the error-styled LIMITED DATA banner. (3) ROOT CAUSE of the "insufficient"
note on rate hike: _MACRO_THEMES only had 7 hand-picked entries — rate hike/cre/
bankruptcy/default fell to halted_microcap (category error as coverage gap). Fix:
_MACRO_THEMES now includes the whole FINANCIAL_RISK_VOCABULARY. Verified live:
10 macro themes (was 4); rate hike now macro_theme/partial, real interpretation,
scores re-read under intended macro computation (35/33 ROUTINE).

## 2026-08-17 (PT, cont.) — Nine-seat credibility board convened + D-early design pre-registered

Chairman-ordered board on the latest findings (referee 0/15 FINAL, tail capture 1/12,
D structural root cause + M0 inversion). Pack: EVIDENCE_PACK_credibility_2026-08-17.md
+ DARK_EARLY_DESIGN_PREREG_2026-08-17.md; M0 baseline endpoint /diag/dark-early deployed
first (LED first-sighting D median 0.0 / pre-broken 14.3 — the inversion, live).
NINE seats convened in parallel, independent; collation:
**audits/board/BOARD_credibility_2026-08-17.md — rulings pending Chairman.**
Headlines: no attention rate citable (9/9; tracked-race is BELOW the null at p~0.001);
v1 wins quarantined as non-evidence ("post-hoc referee, query unsealed" permanent
marking); "0 false positives" ruled a censoring artifact to strip/caveat; C diagnosis
unanimous ("finding of the quarter"); D-early approved DARK-phase-first with separate
flips (bundle rejected 6/9); Lever B design defect caught (must be PRE-enrollment;
rebuild D10 trigger; drop Wikipedia from rescore set — referee common-mode); Lever C
disputed (Google-derived input vs Google-validated ledger — firewall demanded);
d_at_enroll stamping = prerequisite #0; referee is en-only (0/15 partly a language
ceiling); A2 sign-flip named the one active credibility fire; converged honest
language for buyers recorded in the collation.

## 2026-08-18 (PT) — Nine-seat board: the $1M/Month Question (index-administrator path)

Chairman submitted the INDEX_ADMIN_1M_MONTH paper (archived audits/buyer-diligence/);
nine seats convened independently (survived a mid-run session-limit outage; 4 seats +
the WC researcher resumed via transcript). Collation:
**audits/board/BOARD_1M-month_2026-08-18.md — rulings pending Chairman.**
Headlines: meter change approved 9/9 (internal minute, zero publication);
LOAD-BEARING DEFECT found by 3 seats independently — the paper's bitemporal
knowable_at/Merkle archive EXISTS ONLY IN DOCUMENTS, not in this engine's code
(build-first-then-claim, or one buyer's grep kills the story); 1.8 (one number) is
the gate; start index CALCULATION now unmarketed with frozen registered rules, no
back-history ever; index path RESOLVES Q5 (same-day floor sufficient for a
benchmark; before-arrival = pricing upgrade if validated); reflexivity
pre-commitments written at AUM=0; Forecaster sealed staged probabilities (Stage 4
~1-2%, acquisition ~5-10%, plan-of-record = Stages 1-2 only); vendor-permanency =
escrow + named backup calc agent before Stage 3. Disagreements for Chairman:
first-contract label/date; Art-13 publication vs formula-confidential standard;
oversight representation. World Cup case study still in flight (researcher resumed).

**WORLD CUP CASE STUDY DELIVERED (Chairman-commissioned):**
audits/board/WORLDCUP_CASE_STUDY_2026-08-17.md — full lifecycle reconstructed from
our own data. Both doctrine clauses CONFIRMED: family entered via the news pipeline
(mainstream by construction; D<=9/100 across all 532 retrievable cycles — never dark
matter); all 7 ledger rows LAGGED/pre_broken (Google broke out 8-22 days before our
first sighting); post-final collapse to MONITORING in 2 days = "no longer a trend"
visible in data. Refinements earned: quorum matters (mexico world cup at 4-5 stories
correctly demoted to trigger vs world cup at 134 outlets); and the pre-fix engine
under-scored the mainstream giant to 41 — "already mainstream" must never read
"measured as nothing." Board review of the case study = next convening.
