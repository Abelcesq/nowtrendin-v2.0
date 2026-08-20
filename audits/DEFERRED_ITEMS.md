# DEFERRED ITEMS — gated work with written reactivation triggers

> Purpose: an un-triggered shelf is how a documented defect becomes furniture (Guardian,
> D8 board 2026-07-19). Every deferral here carries WRITTEN reactivation triggers so it
> reopens by rule, not by memory. Load-bearing invariants are recorded so the next
> regression can't ship silently.

---

## D8 — score-side exclusion of degenerate positioning components (T1 SHIPPED; fuller exclusion DEFERRED)

> **STATE RECONCILIATION (2026-07-23):** D8's narrowed-spec **T1 SHIPPED** 2026-07-20 under the
> founder truth-ruling — `D8_MM_EXCLUDE=1` is LIVE: serve `money_movement: null` when ALL money
> components are absent/degenerate (206/300 equity + all 12 coins serve the honest absent state).
> The ONLY remaining unbuilt scope is the renormalized-survivor composite exclusion, which stays
> DEFERRED. **T2 fired 2026-07-23** (covered-lane `unmeasured_fraction` 0.524→0.362, majority-
> measured) → reopen backtest REVIEWED (`audits/ledger-research/D8_REOPEN_REVIEW_2026-07-23.md`):
> **DEFER STANDS** — the Δ=0 shield is intact (ledgers still never read mm; T3 not fired; market
> ledger unchanged at 12 resolved / regime 6-of-11), so the fuller exclusion still has zero ledger
> effect and the renormalized-survivor recipe stays rejected (recipe-drift). T2 will keep firing
> while <0.5; that is expected, NOT a ship signal. The real reactivation is T3.

**What it is:** exclude degenerate (zero-variance, constant-mean) positioning components
from the Money Movement *composite* so the served number equals the honest-absence display
(D7 shipped the display half; E1 shipped the composite disclosure; T1 shipped the null-when-
ALL-absent half).

**Why deferred (board-unanimous):** the market/crypto accuracy ledgers NEVER read
money_movement (enrollment gates on positioning flow + intensity; verdicts are realized
price direction). The held-out backtest
(`audits/ledger-research/D8_DEGENERATE_EXCLUSION_BACKTEST_2026-07-19.md`) proved
Δ(enrollments)=0, Δ(verdicts)=0 exactly, at every n — **zero accuracy payoff by mechanism**,
while the change would blank money_movement on 188 flow-neutral instruments + all 12 coins
and flip 95 ROUTINE→DORMANT (all structurally unenrollable). Spending score-surface risk +
a 95-row communication burden for zero ledger effect is the wrong trade until data (not
absence) gives the exclusion something to bind on.

**REACTIVATION TRIGGERS (any one reopens D8; T3 makes it MANDATORY-before):**
- **T1 — founder truth-ruling:** the founder rules that served money_movement / tier must
  equal the displayed honest-absence state.
- **T2 — coverage conversion (H2b recalibration, founder-ruled 2026-07-20):** watch the
  COVERED LANE's **`unmeasured_fraction`** on `/monitor/degenerate-census` → `by_lane` fall
  **below 0.5** (i.e. the majority of covered-lane components become MEASURED). The trigger
  fires there — a genuine maturation event — and reopens D8's held-out backtest for review
  (reopen ≠ ship). Evaluated on cadence by `/monitor/deferred-triggers` (H6).
  - **Why NOT `fully_degenerate_fraction` (the original H2 metric, superseded):** it counts
    instruments where EVERY component is degenerate, which is structurally ~0 for large caps
    (they almost always carry ≥1 measured component). It sat below 0.5 from the BASELINE state
    and fired on the FIRST live read (2026-07-20) — crying wolf, not signalling conversion.
    `unmeasured_fraction` starts near 1.0 cold and falls as component history accrues, so it
    crosses 0.5 only when the lane has genuinely matured (live 2026-07-20: 0.524 → HOLDS).
  - **Why NOT the global `any_unmeasured` count (the pre-H2 metric):** saturated ~299/300 and
    stays high FOREVER by the permanent-frontier rule (E5/§16a) — un-fireable in the FIRE
    direction even as a mature cohort fully converts.
- **T3 — enrollment rewiring (MANDATORY):** ANY proposal to make ledger enrollment, a
  verdict, or any downstream consumer read money_movement or tier. This VOIDS the Δ=0
  shield — D8's ledger-neutrality is a property of *today's* wiring, not permanent
  (backtest §6.6). If enrollment ever reads mm/tier, D8 must be re-backtested BEFORE that
  ships.

**IF EVER BUILT — the narrowed spec (board-ruled, not the original):**
- Serve `money_movement: null` ONLY when ALL money-movement components are absent/degenerate
  (macro-theme n/a serialization class). **NO renormalized-survivor composites** — recomputing
  mm from one thin surviving component is a price whose recipe drifts row to row (Economist,
  Friedman & Schwartz inconsistent-series). Never a fabricated number.
- Crypto: the D ring goes to null on all 12 coins → M-only score. **Product decision required**
  before ship: label it market-confirmation-only, do NOT headline a "Money Gradient" with no
  money data (Outsider).
- Flag-gated (default off), founder sign-off, fresh backtest at then-current n, same-deploy
  explaining copy on all 3 platforms, serve_payload regeneration, hysteresis on tier
  transitions (no ROUTINE↔DORMANT flapping from cycle-sensitive components).

**LOAD-BEARING INVARIANT (do not violate):** ledger enrollment must NEVER read
money_movement or tier. This is what makes the score and its own validator independent;
coupling them manufactures circularity. Undocumented, it is how the next regression ships.

---

## S1 — asymmetric outflow gate (PRINCIPLE ARM CLOSED 2026-07-20; n-arm remains)

> **UPDATE 2026-07-20 (founder ruled "run the degeneracy test"; board Economist synthesis).**
> The principle-reopen path was EXERCISED and **RESOLVED: REJECT parity (board branch S1-4).**
> The ledger-independent degeneracy test
> (`audits/ledger-research/S1_CONGRESS_NET_DEGENERACY_TEST_2026-07-20.md`) measured the distribution
> of congress `net(buys−sells)` across the served universe: **7 net-BUY / 7 net-SELL, mean ≈ 0**
> (clean net-buyers like 3/0, 5/0 present) — congress net **DISCRIMINATES**; it is NOT the
> structurally-sell-dominated degenerate class insider net was (~15/15 all-sell). **The insider
> parity does NOT transfer**, so the blanket accumulation-only asymmetry on the congress base flow
> is NOT justified. `positioning_intel.py` L118 stays UNCHANGED. This CLOSES the PRINCIPLE arm of the
> trigger below. The **n-arm remains open**: the outflow question is settled by DATA (n≥15 resolved
> EPISODES or 0-for-10), never the parity shortcut and never the regime-confounded small-n rate.
> Spin-off noted but NOT acted on: the 4 outflow mega-caps are two-sided (e.g. 6 buys / 14 sells) yet
> fire "outflow" at saturated intensity 1.0 — a *conviction/intensity* calibration question, a NEW
> item with its own investigation + backtest if pursued, NOT S1.

**What it is:** the market-signal "outflow" flow claim is built (with `AV_DARKPOS_ENABLED`
effectively off in production) purely from congress net-selling (`positioning_intel` L118:
`flow='outflow' if congress net(buys−sells) < −1`). This is the SAME degenerate-net class
ruled *noise* for insiders on 2026-06-26 (routine selling ≈ noise; buying is the signal) —
the insider path got the accumulation-only asymmetric fix at L160; the congress base flow
never did. S1 = give outflow the same asymmetry (routine net-sell → neutral unless
corroborated). Full evidence:
`audits/ledger-research/OUTFLOW_FLOWLOGIC_INVESTIGATION_2026-07-19.md`.

**Why gated / NOT implemented:** the outflow lane is 0-for-5 resolved, BUT the regime control
(run first, per the Challenger) found these names rallied +8–19% in-window, giving an 18.8%
outflow-confirm base rate and P(0-for-5 | regime) = 0.35 — **the failures are fully consistent
with market regime alone at n=5**; both lanes are the same rally bet pointed opposite ways.
Episode-collapsed the lane is 0-for-3. Tuning a score to a 5-row, regime-confounded, losing
lane is exactly the Goodhart / score-inflation the board forbids.

**REACTIVATION TRIGGER — n-ARM ONLY (the PRINCIPLE arm was tested and REJECTED 2026-07-20).**
~~PRINCIPLE: insider-parity governs~~ — **CLOSED:** the degeneracy test rejected parity (congress net
discriminates, see the update box above). The principle path does NOT reopen S1. The one live arm:
- **n:** the outflow lane reaches **n≥15 resolved EPISODES** (H5 — the unit is EPISODES, the
  declared honest n, not rows; rows run ~3× faster and would fire prematurely), OR **0-for-10
  EPISODES** (immediate). Evaluated on cadence by `/monitor/deferred-triggers` (H6).

Reopening means: open the held-out backtest — it does NOT mean ship. Until then: **keep enrolling
the outflow lane UNCHANGED — never throttle the losing lane** (Taleb's cemetery — the losing rows
ARE the evidence that will settle it).

**IF REOPENED — ship gate (unchanged):** S1 is a SCORE_AFFECTING item behind its own held-out,
**regime-adjusted** (vs benchmark — now available in `market_accuracy_ledger.report().regime_adjusted`),
precision-AND-recall backtest + founder sign-off. It must NOT be tuned against the ledger it is
measured by. Even the principle-reopen path passes this backtest before shipping.

**TRIGGER UNIT (H5):** all S1 counts are EPISODES (distinct ticker×flow), read from
`/market/accuracy` → `episodes` / `regime_adjusted.episodes`. The `/monitor/deferred-triggers`
endpoint evaluates this on cadence (H6).

---

## R1 — SYMMETRY RULING (Chairman-adopted 2026-07-20; standing, not deferred)
Neither market-ledger lane is validated at the current n. The absolute ±5% confirm rates are
regime-BLENDED in BOTH directions: in a broad rally, inflow confirms and outflow fails
MECHANICALLY, with zero skill either way ("the same coin landing heads because the market went
up"). A high inflow rate (6/7 rows, 3/3 episodes) is as regime-flattered as the low outflow
rate (0/5 rows, 0/3 episodes). **RULES:** (a) never cite either absolute lane rate as evidence
the Money Gradient works — cite `report().regime_adjusted` (excess return vs benchmark); (b)
never publish any market-ledger confirm rate OR the degenerate-census % on any external surface
(pitch / demo / marketing) while `small_sample`/`episode_small_sample` is true — the payload
flags protect the payload, not a slide.

## Standing reporting/monitoring hardenings SHIPPED — recorded here for the trail
**E4 (2026-07-19):** episode-collapse; gate-reject counter; `/monitor/degenerate-census`;
witness-corruption fix (absent → NULL).
**Hardenings review fixes (2026-07-20, this session):**
- **H1** census cold cache (equity + crypto) → `available:false`/unknown, never a false 0.
- **H2** census T2 = per-LANE fraction (trendable), global is saturated-by-design.
  **H2b** (founder-ruled, same day): the per-lane metric is covered-lane `unmeasured_fraction`
  (< 0.5 = majority-measured = reopen), NOT `fully_degenerate_fraction` — the latter is ~0 at
  baseline for large caps and fired on the first live read (a mis-calibrated tripwire).
- **H3** episode confirm-rate served as a RANGE [strict, any] + majority; never headline the
  optimistic ANY-rule (a MAX operator that only inflates the winning lane).
- **H4** gate-reject counter is now DURABLE + fleet-global (`market_gate_rejects` table,
  flushed on any enrollment/sweep/report conn); a 0 with no history still = UNKNOWN.
- **H7** the witness NULL behavior is guarded by `transfer/test_market_ledger_witness.py`
  (the test is the mechanism, not the comment); the tautology no-op was deleted.
- **P1** `report().regime_adjusted` — excess return vs benchmark (SPY), de-confounds BOTH lanes.
- **R1** symmetry ruling above; `regime_caveat` in the payload.

## SCHEDULED READER (H6 — so triggers fire by rule, not memory)
`/monitor/deferred-triggers` evaluates every trigger here (D8 T2 via the census covered-lane
fraction; S1 via the market-ledger EPISODE counts) and returns FIRE/HOLD per item. The weekly
**improve-system** audit reads it each run (checklist item) and surfaces any FIRE. An
un-scheduled shelf becomes furniture — this endpoint + the weekly read is the walk.

---

## S8 — DISPOSITION (Chairman-ruled 2026-08-05 PT; resolves the Executioner-vs-Outsider board split)

The 2026-08-04 board split: the Executioner CUT the S8 batch from the flip window (score-
affecting changes and flag flips must never share a deploy window — when a number moves you
must know which change moved it); the Outsider PULLED the plain-English relabel FORWARD (the
internal vocabulary — "Dark Matter", "LED", "catch-all", "N" — loses an institutional client
in the first meeting; a revenue item, not cosmetics). Ruling splits S8 by what each piece
actually touches:

1. **Signed momentum — DEFERRED as its own project** (score-affecting; owes its own design +
   backtest-before-ship). REACTIVATION TRIGGERS: (a) the F2 flip (`CRYPTO_ETF_FLOW=1`) has
   been live ≥ 1 week with no open incident, AND (b) no other flag flip is scheduled inside
   the same deploy window. Never rides another change's deploy.
2. **Plain-English relabel — QUEUED, display-only** (moves no number; the Executioner's
   deploy-window rule does not bind it). SEQUENCE GATES: (a) the founder's **"N" naming
   ruling** lands FIRST (so surfaces are relabeled once, not twice — earlier candidate:
   "N Market Analysis"); (b) ships AFTER the F2 flip settles (~days, not weeks), BEFORE any
   sales/demo push; (c) three-platform parity pass (`/frontend-consistency`) in the same
   change — a relabel that diverges across surfaces is worse than the jargon.
3. **Incremental prewarm — UNBLOCKED, low priority** (pure serve-path performance; may ride
   any quiet window).

Logged by rule so the split never re-litigates: momentum waits on triggers, the relabel waits
only on the N ruling + flip settling, prewarm waits on nothing.

---

## C5/C6 — NVT metric + realized-cap corrective (Chairman-ruled shelf, 2026-08-05 PT)

**One shelf entry, one trigger, two riders.** Both require on-chain data that no free or
already-licensed source provides today ($0 directive binding). Both were REJECTED as build
items and APPROVED as shelved — the board (6/6) recorded that refusing to fake them is the
deliverable.

**REACTIVATION TRIGGER (necessary AND sufficient together):** a free or licensed on-chain
data source passes ALL FIVE §16 gates, AND a validation study of the specific field passes:
- **C5 (NVT = network value ÷ on-chain transaction volume):** the denominator must be
  GENUINE on-chain transaction volume. **PROHIBITED PROXY (written here so the temptation
  is pre-refused):** FMP/exchange trading volume is NOT on-chain volume — an "NVT" computed
  from it is a different metric wearing the book's name, a fabricated read with a citation
  for cover. Also validate against L2 drain (L2s remove transactions from the L1
  denominator → NVT drifts on ecosystem maturation, not valuation).
- **C6 (realized cap = Σ coins at price-when-last-moved):** requires FULL-coverage UTXO /
  account history. **PROHIBITED PROXY:** no sampled approximation, no price-history-only
  reconstruction — partial coverage fabricates the metric.

Walked by `/monitor/deferred-triggers` + the weekly improve-system read, like every shelf
entry. C5 ships before C6 when the trigger fires (higher ceiling; C6 rides the same source).

## C8 — attention-flow divergence detector (Chairman-approved; gated build)

Design pre-registered in `audits/board/DIVERGENCE_DETECTOR_PREREG_2026-08-05.md`. Build
begins only after: CRYPTO_ETF_FLOW flip + ≥30 trading days of live measured flow. Hard
conditions (board, 6/6): divergence display hard-gated on flow being MEASURABLE (reuses
`absence_class` — on structurally-blind coins the mania signature is instrument blindness);
thresholds pre-registered BEFORE first render; held-out with its own ledger before anything
score-adjacent; user copy says "attention-flow divergence", never "mania"/"bubble".

## IDX-RC4 — index self-influence monitor (PUBLICATION GATE; register r1 obligation)

Register r1 (`audits/index/INDEX_RULEBOOK_REGISTER.md`, RC4) pre-registers the
self-influence null: H0 = NTI-SD50 constituency has no effect on a topic's subsequent
attention. Design (sealed in r1): pair each day's constituents with nearest-Detection
non-constituents (ranks 51–100); compare 7-day forward change in `detection_score`.
While the index is UNPUBLISHED, that distribution IS the null baseline — measurable only
now, at AUM=0/zero-readership; every unpublished day without the monitor is baseline
forgone (Economist: implement early, not at the gate).

**HARD GATE:** the monitor must be IMPLEMENTED and its baseline RECORDED before any
publication of index values, internal-newsletter included. **Reactivation trigger:** any
proposal to publish, license, display, or market any NTI-SD50 value → this item becomes
MANDATORY-before, and the §16a stage discipline applies. Read-only, held-out, never feeds
any score.

## IDX-RC3 — index capacity/AUM-share cap parameter (PRE-LICENSE GATE; register r1 obligation)

RC3's COMMITMENT is structural (r1); its NUMBER is a placeholder. **Reactivation trigger:**
before the FIRST license of any index-linked product is signed, the numeric cap must be
frozen as a register entry (r-note), based on capacity data existing then — never chosen
mid-negotiation, never after signature.

## FCAST-RESOLUTION — forecast_resolution PIT path (FIRST-RESOLUTION GATE)

`FORECAST_REGISTER.md` resolution mechanics require a `kind='forecast_resolution'` PIT row
citing the original entry's `row_sha256`. No code path exists yet (the sealing endpoint
hardcodes `kind='forecast'`) — deliberate deferral (Executioner: build at need, log the
shelf). **Reactivation trigger:** the first forecast resolution event (earliest plausible:
F1 horizon 2027-08-31, or an early F5 YES). Build the resolution path + evidence-hash
recording BEFORE the resolution is recorded, never retrofit after.

## PIT-STORAGE — capacity plan for the never-pruned archive

`pit_observations` accrues one row per served score per cycle, forever (the product).
§13 already flags the 365-day retention straining the 10GB plan. **Reactivation trigger:**
engine Postgres usage ≥70% of plan (check via Heroku dashboard on the weekly
improve-system read) → write the storage tier plan (larger plan vs partition/export
strategy) BEFORE the disk forces one. Never prune; never let disk-full be the first alarm.

## ACC-Q — quarterly benchmark scoring (DATED; Chairman ruling 2026-08-18)

The founder's standing instruction: we must CONTINUOUSLY test whether the system actually
tracks human attention in trends, money markets and crypto — the accuracy ledger is what
answers that, so its gates get scored on a short clock, not a two-year one.
`audits/forecasts/FORECAST_REGISTER.md` **F7** seals seven Q1 benchmarks (B1–B7) with a
horizon of **2026-11-30**.

**Reactivation trigger — DATE: 2026-11-30.** On that date: score all seven with Brier from
the live instruments, record the set's Brier score, seal Q2, and have the Chairman sign the
scoring minute. Benchmarks are never revised, dropped, or reinterpreted after their seal — a
badly-posed one is scored as sealed and replaced in the next quarter. Missing the date does
not void the quarter; it resolves the set as sealed (unresolved = NO) and is itself a finding.

## ACC-LC — recurring lifecycle case study (Chairman ruling 2026-08-18: "learn from past events")

The World Cup study proved the format: reconstruct one topic family end-to-end from our own
sealed data, state the gaps honestly, and let the ledger say where we were late. One study is
an anecdote; a series is evidence (Friedman & Schwartz discipline — the panel settles what one
episode cannot). **Cadence: one study per quarter, delivered with the ACC-Q scoring.**

Queue, in order, each chosen to test a DIFFERENT failure mode than the last:
1. **An unscheduled shock** (geopolitical/market) — the WC was a scheduled mania with a
   printed calendar, the easiest possible class; the thesis lives or dies on unscheduled ones.
2. **A failed trend / graveyard study** — topics that crossed the same early thresholds and
   went nowhere. Until this exists, every lifecycle finding is survivorship-conditioned
   (Taleb's silent evidence). Costs nothing to collect now, unobtainable retroactively.
3. **A LED-win study** — a family the engine actually led on, same template. One loss study
   alone is a confession; loss + win is a diligence pack.

**Immediate predecessor task (blocks nothing but should go first — Operator finding):** the
read-only post-mortem on why Guardian Football / ESPN Soccer / Football365 (niche tier, live
since 2026-06-12) produced ~zero niche mentions and D≤9/100 across 532 world-cup cycles.
Three candidate mechanisms — sports-headline extraction failure, the first-timer numerator
reading 0 on already-seen topics, or collector under-delivery — imply three different builds
at three different costs, and backtesting new feeds through the same silent failure would read
"no lift" as "no edge."

## A3-CEILING / A3-ECHO / A3-TRIPWIRE — completion items for the "never measured as nothing" invariant (Chairman-adopted 2026-08-19, CLAUDE.md §15a)

The invariant is adopted; these are the three open ends the board attached to it. Each is
read-only or display-side and touches no score.

- **A3-CEILING** — the `_soft_cap` hard pin. FIFA and "obama" both pinned at 100 and were
  UNRANKABLE; the order-preserving soft ceiling (knee 85) exists, so what remains is a
  regression fixture proving BOTH ends at once: the 777K-views→41 floor case and
  ceiling separation between two saturated topics. **Trigger:** any new pathway or
  magnitude term shipping, or the next scoring-contract audit — whichever is first.
- **A3-ECHO** — the converse defect the Challenger and Operator both flagged: "aftermath echo"
  BREAKOUTs of 93–95 on 90–194 mentions AFTER a ~97% mention collapse. The same
  honest-absolute-magnitude pathway that cures the floor case appears to over-reward relative
  moves off a collapsed base. **Order (§10a): a read-only DIAGNOSTIC of the mainstream-pathway
  acceleration term on post-peak topics FIRST — no fix ships on the hypothesis.**
  **Trigger:** a second event family showing an aftermath echo at ≥ its true-peak stage on <30%
  of peak mentions.
- **A3-TRIPWIRE** — the standing detector so this class can never again be found by a case study:
  flag any topic carrying external magnitude ≥ `MAG_MAINSTREAM_V2` whose served detection sits
  below a floor for ≥N cycles. Read-only, alarm-only; verify on a synthetic plateau fixture
  before trusting it. **Trigger:** ship with the next monitoring-agent change.

## A4-SEQ — the GHOST_FEEDS remedy sequence (Chairman-RULED 2026-08-19; execute in this order)

The gap statement is adopted (in any domain whose first pipe is Google Trends + news, the engine
is structurally 1–3 weeks late). The remedy sequence is ruled:

**1 → shadow trial vs retro backtest** (decide the instrument, prefer the prospective shadow trial:
candidate feeds held-out, first sightings enrolled in a SHADOW ledger under the same sealed rules,
2026-09-01→11-30 on the sealed-epoch clock — it manufactures real sealed races, which a retro
backtest can never do).
**2 → pre-registered PIT-sealed backtest** (hypothesis, success threshold, holdout window, minimum
N, AND a log of every feed-set variant tried, sealed to the PIT store BEFORE the run).
**3 → football-feed post-mortem** (why Guardian Football / ESPN Soccer / Football365 — niche tier,
live since 2026-06-12 — produced ~zero niche mentions and D≤9/100 across 532 world-cup cycles).
**4 → GHOST_RESEARCH_FEEDS trial close-out** (live 2026-07-15, two-week window elapsed ~07-29,
readout overdue).

> ⚠ **RECORDED RISK on this ordering (Operator, dissenting; ruling followed).** The Operator's
> case was that step 3 must come FIRST, because if the extraction / first-timer / delivery defect
> that silenced the three existing football feeds is still live, a shadow trial runs new feeds
> through the SAME silent failure and its null reads as "no edge" when it is actually "no
> measurement." **Mitigation adopted so the ruling stands without carrying that risk:** the
> post-mortem is READ-ONLY and cheap, so run it in PARALLEL with step 1 rather than after it —
> it does not gate the shadow trial, but its answer must be in hand BEFORE step 1's result is
> interpreted. A null from step 1 may not be read as "no edge" until step 3 has ruled out silent
> non-measurement.

## D-REMINE — LED feature-mining re-run on the repaired instrument (DATED; board 2026-08-20)

The 2026-07-07 mining ("D=0 at first sighting") was measured through the disconnected
instrument (ft=0 writers, Reddit dark, diluted denominator — all verified,
`BOARD_darkmatter_2026-08-20.md`); the doctrine sentence is re-scoped accordingly and the
numbers must never be quoted unqualified. **Triggers (either):** DATE **2026-09-30** — re-run
over whatever first-crossing cohort has resolved, on the then-current regime, citing the
REGIME_LEDGER rows spanning the window; and AGAIN at each shadow-trial readout
(11-30 interim, then per the prereg schedule). Compare against the sealed M0 baseline
(`/diag/dark-early`, snapshot pre-09-01 per the prereg §9). Read-only, held-out.

## D-RIGHTS — per-source rights file for the D roster (board 2026-08-20, Buyer gate 3)

"Five onboarding gates for format and access, none for a written redistribution right —
'it's public RSS' is not a license schedule." **Trigger:** before ANY external licensing
conversation (structure-f API licensee, index licensee, DDQ response), a one-page-per-source
rights register (what is pulled, under what terms, redistribution posture) must exist for
every source feeding a licensed output — extend `docs/buyer-diligence/RIGHTS_REGISTER.md`
to cover the blog/newsletter/socialcrawl/firecrawl D roster. Never blocks collection;
blocks LICENSING.
