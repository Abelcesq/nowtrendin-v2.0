# AGENT CHARTER — Now TrendIn 2.0

**The governing specification for every autonomous agent in the platform.**
Companion to `DATA_BUILDING_BLOCKS.md` (the data-pipeline invariants the agents
police) and `CLAUDE.md` (the build rules). Every agent listed here is bound by the
Shared Mandate in Part 0 *and* by its own 7-point spec.

*Last updated: 2026-06-18*

---

## PART 0 — THE SHARED MANDATE (binds every agent)

### 0.1 Mission

> **Now TrendIn exists to provide the most accurate possible read of where human
> attention is moving — the Gradient Score and the Market Signal — so the company
> keeps its credibility. An agent's job is to protect that accuracy. A number we
> cannot defend with real data is worse than no number at all.**

The product's one irreplaceable asset is trust in the score. Every agent is a
guardian of that trust, not a feature. If an agent's output would let an
indefensible number reach a user, the agent has failed even if its code ran
perfectly.

### 0.2 The Integrity Standard (non-negotiable, applies to all agents)

Every agent — without exception — obeys these hard rules. They override
convenience, speed, and any individual spec below.

1. **Data-backed only.** Every result, alert, and recommendation an agent emits
   must be derived from clear, verifiable data the agent actually read. No agent
   asserts, infers, or estimates anything it cannot point to a source for. If the
   data is missing, the agent says *"insufficient data"* — it does not guess.
2. **Measurement, not advice.** Agents report what the data shows. They never
   issue investment, trading, or financial advice, and never editorialize a score
   into a recommendation to act.
3. **No circular metrics.** The on-platform demand signal **N** (`nowtrendin_score`)
   is NEVER folded into the Gradient Score or used to validate it. Any validator
   uses inputs independent of what it validates. (See `feedback-no-circular-metrics`.)
4. **Reputable, licensed sources only.** Agents credit and corroborate only vetted
   publishers/sources. Unvetted firehose content is quarantined, never scored.
5. **Flag, never force.** Monitoring/diagnostic agents are **read-only by default**:
   they write nothing to scores and change no universe. Anything that alters what a
   user sees — adding a ticker, changing a weight, publishing a hit-rate — is
   surfaced as a *recommendation for human confirmation*, never auto-applied. A
   wrong auto-action is a credibility event; a flagged candidate is not.
6. **Verify-before-ship / backtest-before-ship.** No scoring change ships on an
   agent's say-so alone. Agents inform the decision; a human verifies against live
   data (and backtests, for scoring-logic changes) before deploy.

### 0.3 Common conventions (so the fleet is legible)

- **Alert grammar.** Every alert is `{level, block, msg}` (optionally `source`).
  `level ∈ {info, warn, critical}`. `block` is the `DATA_BUILDING_BLOCKS.md`
  invariant it maps to (`B1`–`B8`).
- **Status roll-up.** Every agent returns `status ∈ {ok, warn, critical}` =
  worst level among its alerts. `run_all` overall status = worst agent status.
- **Two tiers of run.** *Fleet agents* run together in `monitoring_agents.run_all`
  (cheap, safe to poll). *On-demand agents* (costly external calls) run on their
  own endpoint or a schedule and are explicitly **excluded** from `run_all`.
- **Honesty over green.** An agent that cannot read its data returns `warn` with
  the reason — it never returns a false `ok`.

### 0.4 The fleet at a glance

| # | Agent | Endpoint | In `run_all`? | Block(s) |
|---|-------|----------|:---:|---|
| 1 | Market Signal Diagnostic | `/diagnostic/market/{symbol}` | no (on-demand) | B4/B5 |
| 2 | Trend Signal Diagnostic | `/diagnostic/trend/{topic}`, `/diagnostic/trend-distribution` | no (on-demand) | B4/B5 |
| 3 | Source Watchdog | `/monitor/sources` | ✅ | B1, B2 |
| 4 | Pipeline Integrity | `/monitor/pipeline` | ✅ | B3, B4, B8 |
| 5 | Topic Quality Auditor | `/monitor/quality` | ✅ | B3 |
| 6 | Catch-All Auditor | `/monitor/catchall` | ✅ | B3 |
| 7 | Calibration Auditor | `/monitor/calibration` | ✅ | B5 |
| 8 | Market Universe Coverage | `/monitor/market-coverage` | no (Finnhub cost) | B1 |
| 9 | Cost Sentinel | `/monitor/cost` | ✅ | B7 |
| 10 | Data Subscriptions | `/monitor/subscriptions` | ✅ | B7 |
| 11 | Grade Agent | `/grade` | n/a (request-time) | B4 |
| 12 | Frontend Consistency | `/frontend-consistency` (skill) | n/a (manual/CI) | B8 |
| 13 | Terminal Deploy Parity | `/terminal-deploy-parity` (skill) | n/a (manual/CI) | B8 |

The combined fleet is reachable at **`/monitor`** (`run_all`). Agents 1–2 and 8 are
the deliberately-excluded on-demand specialists.

### 0.5 Operational invariants & gotchas (hard rules, learned the hard way)

These are non-negotiable invariants the platform must hold. Each names the agent that
**owns** detecting a breach. Adding code that can violate one without the owning agent
catching it is itself a defect.

- **INV-1 — One score per topic, everywhere.** The same topic must serve the **same**
  Detection/Confidence/Stage on `/topics`, `/scores`, and `/scores/{key}` (and thus on
  website, app, and desktop). All three read the precomputed `serve_payload` as the
  single source of truth. **If the scores don't match, there is a problem.**
  *Owner: Pipeline Integrity (B8).*

- **GOTCHA G1 — Regenerate `serve_payload` after ANY scoring/calibration change.**
  `/scores` + detail + `/topics` read the precomputed `velocity_scores.serve_payload`
  via a fast path; they only live-calibrate when it's NULL. So a change to
  `apply_calibration` / `_calibrate_score_fields` / the scoring formula is **invisible
  until the payload is regenerated** — `python -c "import gravitational_anomaly_detector
  as g; g._precompute_serve_payloads(600)"` (it clears all first, then rebuilds), or a
  full re-score. Symptom: `score-history` (live-calibrates) shows the new value while
  `/scores` shows the old. Also: the web dyno's in-memory `_cache` clears on deploy
  restart or `/score-all`; use a novel `?limit=` to bypass when verifying.
  *Owner: Pipeline Integrity (B8) flags a stale payload automatically.*

- **GOTCHA G2 — The live `apply_calibration` is in `signal_calibration_integration.py`,
  NOT `calibration_engine.py`.** The engine imports it from the former
  (`gravitational_anomaly_detector.py:199`); the same-named function in
  `calibration_engine.py` is dead. Edit the wrong one and nothing changes.

- **INV-2 — Pathway discipline.** The expert G·I·M·D·C recompute applies ONLY to
  expert/niche topics; mainstream/blended topics keep their dual-pathway headline.
  Violating this collapses every mainstream topic to ~27 (unrankable).
  *Owners: Pipeline Integrity (B8 mainstream-collapse alarm) + Trend Signal Diagnostic
  (N-discipline / pathway gate).*

- **INV-3 — N never feeds the Gradient** (no circular metric); see Integrity Standard #3.
  *Owner: Trend Signal Diagnostic.*

When a new accuracy/consistency trap is discovered, add it here with its owning agent —
the Charter is the durable home for these, mirrored in the `serve-payload-cache-gotcha`
project memory.

---

# PART I — THE DEVOTED SCORING DIAGNOSTICS

*The two agents you specifically commissioned to keep the scores defensible.*

## AGENT 1 — MARKET SIGNAL DIAGNOSTIC

**1. Identity.** `market_signal_diagnostic.py` · `run(symbol)` ·
`/diagnostic/market/{symbol}`. The devoted instrument for **Market Signal scoring
calibration**.

**2. Definition & scope.** A read-only harness that makes the engine *explain
itself* for one instrument. For a given symbol it reports: how much baseline
history each of the **7 components** actually used (`dark_positioning`,
`positioning_concentration`, `analyst_signal`, `fundamental_confirmation`,
`market_momentum`, `cross_market_diffusion`, `signal_freshness`); whether the
0.05 stdev floor is doing the work; which component inputs are real vs absent; and
whether the "unusual deviation" flag contradicts the reported tier. It uses the
engine's **real** `DETECTION_WEIGHTS` / `CONFIDENCE_WEIGHTS` pulled live from
`market_signal_engine` (no hardcoded guesses). Verdicts: **VALID ·
INSUFFICIENT_HISTORY · DATA_GAP · CONTRADICTION**.

**3. Will NOT.** It is instrumentation, never a scorer — it writes nothing and
changes no score. It does not add instruments to the universe (that is Agent 8).
It does not invent a baseline for a cold-start name, and it never reports a
confident ROUTINE/DORMANT tier for an instrument whose history can't support one.

**4. How it supports accuracy & UX.** It is the direct defense against the failure
that worried you most: a young instrument (e.g. SPCX, public since 2026-06-12)
being scored as a confident "routine" read off two days of data. By exposing thin
baselines it forces the honest **CALIBRATING** state, so users never see a Market
Signal the data can't back. (This pairs with the `MARKET_MIN_BASELINE=10` cold-start
guard already in `score_component`.)

**5. Success looks like.** Every Market Signal a user sees is either VALID
(adequate history, real inputs, tier consistent) or honestly labeled
INSUFFICIENT_HISTORY/CALIBRATING. Zero instances of a confident tier on a thin
baseline. CONTRADICTION verdicts trend to zero over time as calibration tightens.

**6. Problem signaling & resolution.** Returns a per-component verdict dict naming
the exact failure: INSUFFICIENT_HISTORY → cohort still forming, hold at CALIBRATING
(no action, or lower `MARKET_MIN_BASELINE` only with evidence); DATA_GAP → a feed
(Finnhub/analyst/positioning) is missing — hand to Source Watchdog; CONTRADICTION →
the deviation flag disagrees with the tier — a calibration bug to fix before ship.

**7. Ongoing monitoring.** On-demand per symbol via `/diagnostic/market/{symbol}`.
Run on any instrument that looks "off," on every newly-added ticker before trusting
its tier, and as the verification step after any `market_signal_engine` change.
Exposed as the `/market-signal-diagnostic` skill.

## AGENT 2 — TREND SIGNAL DIAGNOSTIC

**1. Identity.** `trend_signal_diagnostic.py` · `run(topic)` + `run_distribution()`
· `/diagnostic/trend/{topic}`, `/diagnostic/trend-distribution`. The twin of Agent 1,
devoted to the **Gradient Score**.

**2. Definition & scope.** Read-only. Makes the engine explain one topic, and the
distribution across topics, on the real failure modes the live view surfaces:
- **SCORE SATURATION** — top topics pinned at Detection ~100, so #1 can't be ranked
  against #2.
- **N-DISCIPLINE** — the headline Detection/Overall must reconcile to the five
  EXTERNAL components only (G gradient_strength, I inertia, M medium_sequence,
  D dark_matter, C confidence_decay); **N must never feed the headline**. The
  reconcile check is **gated to the expert pathway** (mainstream/blended topics use
  the dual-pathway magnitude formula, so a G/I/M/D/C recompute legitimately doesn't
  apply — not flagging them avoids false "leak" alarms).
- **WHAT-IF-N INVERSION** — the separate demand-inclusive read must not move DOWN
  when demand (N) is high.
- **CROSS-TOPIC DISTRIBUTION** — is Confidence actually separating topics or
  collapsing many onto one value?

Verdicts: **VALID · SATURATED · FROZEN · UNDOCUMENTED_INPUT · WHATIF_N_INVERTED ·
DATA_GAP**.

**3. Will NOT.** Writes nothing, scores nothing. It does not hardcode the Confidence
weight vector — that vector is left `None` on purpose because the live blend is
ambiguous between two documented vectors, and the agent will not assert a number it
cannot verify (Integrity Standard #1). It does not flag a G/I/M/D/C reconcile gap on
non-expert pathways.

**4. How it supports accuracy & UX.** It protects the two things that make the
ranking trustworthy: that the leaderboard can actually *rank* (no saturation pile-up
at 100), and that the headline score is a clean, N-free read of external attention
(no demand feedback loop). This is what lets "before it arrives" stay defensible.

**5. Success looks like.** Top topics are rankable (Detection separates at the top,
not pinned at 100). Every expert-pathway headline reconciles to G/I/M/D/C within
tolerance. The what-if-N read is monotonic (never inverts on high demand —
**verified healthy 06/17**: Musk det 78 + N 95 → 80, moves up). Confidence spreads
across topics rather than collapsing.

**6. Problem signaling & resolution.** Per-topic verdict names the failure:
SATURATED → apply/adjust the soft-cap knee so the top decompresses (already
implemented via `_soft_cap` in `dual_pathway`); UNDOCUMENTED_INPUT → an input is
feeding the headline that shouldn't (investigate the N-leak); WHATIF_N_INVERTED →
the demand-inclusive formula regressed — fix before ship; DATA_GAP → component
inputs missing for the topic.

**7. Ongoing monitoring.** On-demand per topic; `run_distribution()` for a
cross-topic sweep. Run after any `dual_pathway` / `compute_gradient_score` change,
and on the distribution periodically to watch saturation/confidence spread. Exposed
as the `/trend-signal-diagnostic` skill.

---

# PART II — PIPELINE & DATA-QUALITY MONITORS

## AGENT 3 — SOURCE WATCHDOG

**1. Identity.** `monitoring_agents.source_watchdog` · `/monitor/sources` · blocks
B1 (source registry/SLA) + B2 (collection health). In `run_all`.

**2. Definition & scope.** Asks one question: *are our sources pulling within their
SLA?* Reads `collector_health.get_health_report` and raises an alert per collector
that is **DOWN**, **STALE**, or **DEGRADED** (ran but returned 0 signals). A
critical collector being down or stale is `critical`; a non-critical one is `warn`.
Respects `_OFF_SOURCES` — collectors intentionally turned off never alarm.

**3. Will NOT.** It does not restart collectors or change source config; it reports
status only. It will not alarm on sources we deliberately disabled (no alert noise).
It does not judge *content* quality (that is Agents 4–6) — only whether data arrived.

**4. How it supports accuracy & UX.** A score computed while a major source is dark
is half-blind. The Watchdog is the early-warning that the inputs feeding every
Gradient/Market score are actually flowing, so we never publish scores off a
silently-degraded feed.

**5. Success looks like.** All critical collectors GREEN within SLA; any outage
surfaced within one cycle with the specific source and the detail string; zero
false alarms on intentionally-off sources.

**6. Problem signaling & resolution.** Alerts name the source + state (`DOWN —
{detail}`). Resolution options: check the source's API key/quota (hand to Cost
Sentinel / Data Subscriptions if it's a billing/quota stop), inspect the collector,
or — if the source is being retired — add it to `_OFF_SOURCES` so the alarm stops
honestly.

**7. Ongoing monitoring.** Runs every `/monitor` poll via `run_all`; also directly
at `/monitor/sources`. Surfaced by the `/data-watchdog` skill.

## AGENT 4 — PIPELINE INTEGRITY MONITOR

**1. Identity.** `monitoring_agents.pipeline_integrity` · `/monitor/pipeline` ·
blocks B3 (extraction) + B4 (scoring) + B8 (serve). Sample 300. In `run_all`.

**2. Definition & scope.** Verifies the pipeline from scoring to serve. (a) **B4
freshness** — the latest `velocity_scores.scored_at` must be recent; >7h = `warn`
(a 6h cycle missed), >12h = `critical` (stalled), none ever = `critical`. (b) **B3
extraction** — samples the top scored topics and flags single-word common-word junk
(via the engine's own `_is_quality_topic`) and unconsolidated canonical duplicate
groups (via `_topic_key`). (c) **B8 serve consistency — THE OWNER of cross-surface
score agreement.** Checks scored rows carry the `detection_pathway` audit field
**and** — on a sub-sample — that the **same topic serves the same score on every
surface**. `/scores`, `/scores/{key}` and `/topics` all read the precomputed
`serve_payload` (single source of truth); this agent re-runs `_calibrate_score_fields`
live and (i) flags a **STALE serve_payload** (payload drifted from a fresh calibration
— the signature of a scoring change shipped without regenerating the payload, see
Gotcha G1) and (ii) flags a **MAINSTREAM COLLAPSE** (a mainstream topic served far
below its stored dual-pathway detection — the pathway-gate regression of 2026-06-18).
**If the served scores don't match, that is the alarm.**

**3. Will NOT.** It does not re-score, prune, or deduplicate — it reports that those
are needed. Multi-word "junk" is surfaced as **review-only**, never a hard alert,
because the lowercase filter can't distinguish a proper-noun name ("Michael
Chandler") from generic phrasing — the agent refuses to over-claim.

**4. How it supports accuracy & UX.** It catches a stalled scorer (stale scores are
the worst silent failure), keeps junk/duplicate topics out of the served leaderboard,
and ensures the dual-pathway audit field is present so web/desktop/mobile show
identical data.

**5. Success looks like.** Scores always < 7h old; near-zero single-word junk in the
top sample; zero duplicate groups; `detection_pathway` present on essentially all
scored rows; **`serve_stale_payload` = 0 and `serve_mainstream_collapse` = 0** (every
surface serves the same score).

**6. Problem signaling & resolution.** Freshness critical → the score cycle stalled,
check the worker / scheduler. Junk/dupes → run the quality gate at scoring time and
prune old rows. Missing pathway → a re-score is needed. **STALE payload (`warn`) →
regenerate `_precompute_serve_payloads` (Gotcha G1). MAINSTREAM COLLAPSE (`critical`)
→ the pathway gate in `apply_calibration` (`signal_calibration_integration.py`)
regressed; fix and re-score (Gotcha G2).**

**7. Ongoing monitoring.** Every `/monitor` poll via `run_all`; directly at
`/monitor/pipeline`.

## AGENT 5 — TOPIC QUALITY AUDITOR

**1. Identity.** `monitoring_agents.fragment_category_auditor` · `/monitor/quality`
· block B3 (deep). Sample 400. In `run_all`. Surfaced by `/topic-quality-audit`.

**2. Definition & scope.** Watches the failure modes that make category views messy
and sources unclear. (1) **News-filler / headline fragments** — multi-word topics
anchored by a filler token (via the engine's own `NEWS_FILLER`), e.g. "iran deal",
"leaders meet". (2) **Geo mis-sort** — country/conflict terms sorted into
Business/Economy when they belong in current-events/politics (the "iran deal →
Business" bug class). (3) **Catch-all pressure** — the share of sampled topics
landing in `news`/`general`/empty category. Uses the engine's own `_topic_category`
so the audit matches the live pipeline exactly.

**3. Will NOT.** It does not edit the classifier or `NEWS_FILLER` — it reports the
specific fragments and mis-sorts so a human tightens the lists. It reports a single
headline `news_catchall_pct`; the *diagnosis* of that number is delegated to Agent 6
(no overlap, no double-claiming).

**4. How it supports accuracy & UX.** Fragments and mis-sorted geo topics are what
make the category browse experience look unreliable. Keeping them out protects the
UX credibility of every category view.

**5. Success looks like.** Few/zero served fragments; zero geo topics in
Business/Economy; catch-all % trending down over time.

**6. Problem signaling & resolution.** Alerts list example offenders. Resolution:
tighten `NEWS_FILLER` (fragments), extend the category lexicon (geo mis-sorts),
re-score to flush.

**7. Ongoing monitoring.** Every `/monitor` poll via `run_all`; directly at
`/monitor/quality`.

## AGENT 6 — CATCH-ALL AUDITOR

**1. Identity.** `monitoring_agents.catchall_auditor` · `/monitor/catchall` · block
B3 (specialised). In `run_all`. Built to run **end-of-day**; surfaced by
`/catchall-audit`.

**2. Definition & scope.** The specialist that *diagnoses* the news/general
catch-all congestion Agent 5 only measures. It reports four things: the catch-all
**% + counts** (tracked daily for trend); **FLOOR HEALTH** — single-source catch-all
topics that leaked past the `CATCHALL_MIN_SOURCES` corroboration floor (should be
~0; a climb means the floor is disabled or a purge is overdue); **MISCLASSIFIED
TRACKED CALLS** — accuracy-ledger/pending detections stuck in the catch-all (real
signals the thin lexicon mis-sorted — highest priority); and **LEXICON CANDIDATES**
— the most frequent meaningful tokens across catch-all topics, i.e. the exact terms
to add to `topic_categories._LEX` to drain the catch-all. Its summary is a
**worklist**, not just a number.

**3. Will NOT.** It does not auto-edit the lexicon or auto-purge — it produces the
ranked worklist for a human. It does not treat the corroboration floor as a raw
post-volume floor (which would break the "before it arrives" thesis) — it only flags
*single-source* leaks past the floor.

**4. How it supports accuracy & UX.** The catch-all is where real early signals go
to hide. Draining it (via the lexicon candidates) moves topics to their true
category, and the misclassified-tracked check rescues genuine detections that the
classifier dropped into the bucket — directly protecting the accuracy ledger.

**5. Success looks like.** Catch-all % declining; single-source leak ~0; **zero**
tracked calls stuck in the catch-all; a steadily-shrinking lexicon-candidate list.

**6. Problem signaling & resolution.** Misclassified tracked calls → reclassify
first (highest priority). Catch-all ≥70% → add the top lexicon candidates to `_LEX`.
Floor leak >50 → the floor is disabled or a purge is overdue.

**7. Ongoing monitoring.** Every `/monitor` poll via `run_all`; directly at
`/monitor/catchall`; intended for a daily EOD report.

---

# PART III — CALIBRATION & ACCURACY HONESTY

## AGENT 7 — CALIBRATION AUDITOR

**1. Identity.** `monitoring_agents.calibration_auditor` · `/monitor/calibration` ·
block B5. In `run_all`. Surfaced by `/accuracy-sweep`.

**2. Definition & scope.** Guards the honesty of the **Accuracy Ledger**. Reads
`ledger_plus.generate_honest_report` and checks the hit-rate is denominator-backed:
if fewer than 30 detections have been *evaluated* (or the ledger itself flags
small-sample), it raises a `warn` that **no hit-rate may be published yet**
(guardrail 5). Reports evaluated/pending counts and the current hit-rate.

**3. Will NOT.** It does not compute or "improve" the hit-rate, and it is **not** the
backtest-before-ship gate (that is a separate deploy step, not a runtime poll). It
will not let a flattering small-sample number out the door.

**4. How it supports accuracy & UX.** The published hit-rate is the single most
credibility-sensitive number on the platform. This agent ensures we never advertise
an accuracy figure we can't statistically defend — the difference between
trustworthy and embarrassing.

**5. Success looks like.** No hit-rate published while small-sample; once the
denominator is adequate, the figure is shown with its evaluated/pending counts;
pending backlog shrinks as detections mature.

**6. Problem signaling & resolution.** Small-sample → hold publication, keep
accruing evaluations. Ledger read failure → investigate `ledger_plus`.

**7. Ongoing monitoring.** Every `/monitor` poll via `run_all`; directly at
`/monitor/calibration`.

---

# PART IV — COVERAGE & COMPLETENESS

## AGENT 8 — MARKET UNIVERSE COVERAGE

**1. Identity.** `monitoring_agents.market_universe_coverage` ·
`/monitor/market-coverage` · block B1. **NOT in `run_all`** (per-candidate Finnhub
calls are too costly to poll). Scheduled **Mon–Fri 3pm PST**. Surfaced by
`/market-coverage`.

**2. Definition & scope.** Catches the **"SpaceX problem"**: a real publicly-traded
company trending in the attention data but **missing from the curated Market Signal
universe** (`WATCHLIST_TICKERS`) — e.g. a fresh IPO the static list never got. It
scans top business/economy/technology trending topics, and for any capitalized
(proper-noun) topic not already tracked, asks the Finnhub Common-Stock resolver
whether it's a real public company. Real ticker + trending + untracked = a coverage
**gap**.

**3. Will NOT.** It **never auto-adds** a ticker (a wrong/ambiguous resolve must not
silently enter the universe) and never force-injects a score. Private companies
(Anthropic, etc.) don't resolve to a Common Stock, so they're correctly not flagged.
Lowercase/non-proper-noun topics are skipped to limit Finnhub spend.

**4. How it supports accuracy & UX.** The Market Signal is only as good as its
universe. This agent makes the universe self-healing against the one gap a static
list can't catch — newly public companies — so a name that's clearly trending isn't
mysteriously absent.

**5. Success looks like.** Zero standing coverage gaps; every newly-trending public
company surfaced within a day or two of trending, with its resolved ticker ready for
one-click human confirmation.

**6. Problem signaling & resolution.** Each gap is reported as
`{topic, ticker, resolved_as, mentions}`. Resolution: confirm the ticker, add to
`financial_risk_gradient.WATCHLIST_TICKERS` (+ `_TICKER_SECTOR`), run a risk
collection. (This is exactly how SPCX was added.)

**7. Ongoing monitoring.** Scheduled cron Mon–Fri 3pm PST; directly at
`/monitor/market-coverage`.

---

# PART V — COST & SUBSCRIPTIONS

## AGENT 9 — COST SENTINEL

**1. Identity.** `monitoring_agents.cost_sentinel` · `/monitor/cost` · block B7. In
`run_all`. Surfaced by `/data-health`.

**2. Definition & scope.** Tracks the **total monthly cost** of running Now TrendIn
against budgets. Live-metered: **AI** (Perplexity+Anthropic vs the $20/mo cap) and
**Apify** (platform usage via its API vs the cap). Configured (env, set to actuals):
**Heroku** dynos, **X Developer API** fee, **AWS**, **Data API subscriptions** (fed
by Agent 10), **GitHub**. Plus the **X post budget** (operational posts, not $).
Alerts at 80% (`warn`) and exhausted (`critical`) on each metered line, and on an
optional grand `COST_TOTAL_MONTHLY_CAP`.

**3. Will NOT.** It does not stop spending or change plans — it warns. It does not
double-count: metered APIs (AI/Apify/X) are on their own lines and excluded from the
subscriptions sum.

**4. How it supports accuracy & UX.** Financial viability *is* an accuracy concern —
an exhausted AI or Apify budget silently degrades the data feeding the scores. The
Sentinel is the early warning before a budget stop starves the pipeline.

**5. Success looks like.** No metered line crosses its cap unexpectedly; total
monthly cost visible and within the grand cap; budget-stop-driven data gaps avoided.

**6. Problem signaling & resolution.** AI/Apify ≥80% → throttle or raise the cap; X
posts ≥80% → ration deep pulls. **Pending action: X Basic → Pay-Per-Use on
2026-06-21** — update `COST_X_API_USD` then (a one-time reminder is scheduled).

**7. Ongoing monitoring.** Every `/monitor` poll via `run_all`; directly at
`/monitor/cost`.

## AGENT 10 — DATA SUBSCRIPTIONS

**1. Identity.** `monitoring_agents.data_subscriptions` · `/monitor/subscriptions` ·
block B7. In `run_all`. Surfaced by `/data-subscriptions`.

**2. Definition & scope.** The itemized inventory of every external data API:
name, key env var, whether it's **configured** (key present), billing class
(**paid / free / metered**), cost env var, and a note. `data_subscriptions_total()`
sums the paid lines and feeds the Cost Sentinel's "Data API subscriptions" line. It
alerts when a **paid** API is configured but has **no tracked cost** (untracked
spend). Currents (the new free news aggregator, daily-capped) is tracked here.

**3. Will NOT.** It does not set costs or cancel subscriptions — it surfaces which
need a `COST_*_USD` value. Metered APIs (AI/Apify/X) are listed but excluded from the
paid total to avoid double-counting with Agent 9.

**4. How it supports accuracy & UX.** Prevents silent untracked spend and gives a
single source of truth for which data feeds are live — the dependency map behind
every score.

**5. Success looks like.** Every paid API has a tracked cost (no "untracked spend"
warning); the inventory matches the collectors actually running; free/metered
sources clearly separated.

**6. Problem signaling & resolution.** "N paid APIs with no tracked cost" → set each
`COST_*_USD`. A configured key for a retired source → remove it.

**7. Ongoing monitoring.** Every `/monitor` poll via `run_all`; directly at
`/monitor/subscriptions`.

---

# PART VI — SCORING-SUPPORT & DELIVERY

## AGENT 11 — GRADE AGENT

**1. Identity.** `grade_agent.py` · `/grade` (one endpoint, all 3 platforms) · block
B4. Surfaced by `/grade-agent`.

**2. Definition & scope.** **Pool-first** topic grading. On any grade request it
searches the live data pool FIRST: if the topic is already measured, it returns the
engine's **MEASURED** Gradient Score + N — no AI call, no grade-credit burn. If not
in the pool, it runs the AI grade (Perplexity+Claude, a **PROPOSED** score with
citations) and attaches the live N. Either way it returns both a Gradient Score
(detection + confidence + overall + stage) and an N score, plus `source`
(`measured` | `ai_proposed`), `in_data_pool`, and `charge_token`.

**3. Will NOT.** It does not spend an AI call or charge a grade credit when the
answer is already measured (`charge_token=False`). It never folds N into the Gradient
(no demand feedback loop). It never presents an AI estimate as a measured fact —
`ai_proposed` is explicitly labeled.

**4. How it supports accuracy & UX.** A measured return is the engine's own
objective score, not an estimate — strictly more credible and free. Pool-first
saves cost *and* raises answer quality, and the consistent `/grade` contract keeps
web/desktop/mobile identical.

**5. Success looks like.** In-pool topics return measured scores at zero AI cost;
out-of-pool topics return clearly-flagged AI proposals with citations; N always the
separate demand signal; the source label always honest.

**6. Problem signaling & resolution.** If a topic that *should* be in-pool returns
`ai_proposed`, that's a pool-coverage/entity-resolution gap → investigate the pool
lookup. AI-cost spikes → Cost Sentinel.

**7. Ongoing monitoring.** Request-time at `/grade`; spend visible at `/grade/costs`
and via Cost Sentinel.

## AGENT 12 — FRONTEND CONSISTENCY

**1. Identity.** `/frontend-consistency` (skill) · block B8. Read-only.

**2. Definition & scope.** The **3-platform UI-parity** monitor. Confirms the trend
signal pages and the market-analysis pages present the SAME labels, filters, detail
sections, data points, and **mobile color scheme** across mobile (`frontend/`), web
terminal (`web-terminal/`), and desktop (`tauri-desktop/`), and that the deployed
sites are up. The web terminal may add MORE (denser filters, extra columns) but must
not DIVERGE on shared elements.

**3. Will NOT.** Read-only audit — it does not edit components or deploy. It does not
demand the terminal be a pixel clone (additive density is allowed); it flags
*divergence* on shared labels/filters/sections/colors only.

**4. How it supports accuracy & UX.** A score that looks different on three surfaces
reads as three different products. Parity is what makes the institutional surfaces
feel like one trustworthy instrument.

**5. Success looks like.** Shared labels/filters/sections/colors identical across
all three; canonical sites up; divergences caught the moment a filter/label/color
changes on any surface.

**6. Problem signaling & resolution.** Reports the specific diverging element + the
surfaces. Resolution: align the lagging surface to the shared spec (mobile colors in
`web-terminal/src/lib/mobileTheme.ts`).

**7. Ongoing monitoring.** Run on demand and after any filter/label/section/color
change on any surface (manual or CI). Read-only.

## AGENT 13 — TERMINAL DEPLOY PARITY

**1. Identity.** `/terminal-deploy-parity` (skill) · block B8. Read-only.

**2. Definition & scope.** Confirms the web terminal build is actually **on the
GitHub repo** and that every deploy target serves the **same** build. Compares the
**GitHub Pages live site (canonical — what the user sees)**, the **`gh-pages`
branch** in the repo, and the **Heroku mirror** by bundle hash, so a stale/forgotten
deploy is caught immediately.

**3. Will NOT.** Read-only — it does not deploy or push. It does not treat the Heroku
mirror as canonical (the canonical user-facing site is GitHub Pages — see
`deploy-terminal-ghpages`).

**4. How it supports accuracy & UX.** It exists because the targets drifted once —
Heroku was updated but GitHub Pages was stale, so fixes "didn't work" because they
never reached the page. This agent guarantees a fix the user is told shipped
actually reached the surface they're looking at.

**5. Success looks like.** All three targets serve the same bundle hash; a stale
target is flagged immediately after deploy; "did my change deploy?" is answerable in
one check.

**6. Problem signaling & resolution.** Hash mismatch → names the stale target.
Resolution: redeploy the lagging target (gh-pages worktree push for the canonical
site).

**7. Ongoing monitoring.** Run on demand and after every terminal deploy (manual or
CI). Read-only.

---

## APPENDIX — Governance

- **Adding an agent.** A new agent is not "done" until it has a 7-point entry here,
  obeys Part 0, returns the standard `{status, alerts[], summary}` shape, and is
  wired to either `run_all` (cheap) or its own endpoint/schedule (costly). Update the
  Part 0.4 table.
- **Block mapping.** Every agent maps to one or more `DATA_BUILDING_BLOCKS.md`
  invariants (B1–B8); that file is the spec for *what* is being protected, this file
  is the spec for *who* protects it.
- **The line that governs all of them.** *If the data can't support it, the agent
  says so. We protect the score's credibility above all else.*
