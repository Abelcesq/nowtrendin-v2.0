# ADVISORY BOARD — ROUND 4: historical corpus, crash physics, and a market-trend panel
**Convened:** 2026-07-25 by the Chairman · **Five archetypes, independent, no cross-visibility**
**Questions:** (1) the Chairman's read-only historical reference layer resolving D1 · (2) crash
physics — Mandelbrot / Sornette / Bouchaud & Potters · (3) a separate market-trend scoring panel.

Prior record: `BOARD_market-crypto-signal` (R1) · `BOARD_money-movement-build` (R2) ·
`BOARD_mechanisms-and-tools` (R3) · `SYNTHESIS_money-movement` · `R7_dark_pos_weight_evidence`.

---

## 1. VERDICT TABLE

| | Q1 read-only corpus | Q2 crash physics | Q3 market-trend panel |
|---|---|---|---|
| **Challenger** | APPROVE — distinction sound, safeguard as stated unenforceable | Mandelbrot ACCEPT · Bouchaud ACCEPT · **LPPL REJECT as a shipped estimator** | Not a score — a **stage label**, and only with its own ledger |
| **Guardian** | APPROVE under 5 conditions | **LPPL-on-price REJECTED outright** · mechanism port PERMITTED under 7 conditions · Mandelbrot **do first** | **Stage**, not Kindleberger's affect words · name must change |
| **Economist** | APPROVE — but the unit is **episodes (n≈10)**, not rows | Mandelbrot ACCEPT (our estimator is misspecified) · Sornette **Stage-1 only, non-price** · RMT **not implementable yet** | **STAGE**, ordinal · reject "N" |
| **Outsider** | Worth ~1 week **as a diligence exhibit**, not a feature | **REJECT the panel** · mechanism port = research track only, never named crash prediction | **Would not demo it** at any point |
| **Executioner** | CUT to one source, after Phase 2 | **CUT LPPL outright** — benchmarked infeasible | **DEFER** until `report()` returns `publishable: true` |

**Unanimous:** the Chairman's read-only/ledger distinction is *sound*; **LPPL fitted to price is
rejected**; Mandelbrot is accepted — not as a forecasting tool but as a **critique of our own
statistics**; the panel is a **stage label, never a score**; and **"N" cannot be reused.**

---

## 2. Q1 — THE READ-ONLY CORPUS: sound distinction, wrong safeguard

All five agree the Chairman's cut is correct in principle — a corpus and a ledger differ in
*time-order*, not permissions. But all five independently landed on the same objection:

> **The leak is not the data path. It is the analyst.**
> **Outsider:** *"Schema markers and read-only flags stop writes. They do not stop the actual
> hazard, which is a human looking at 2008 and choosing `ARRIVAL_VOL_MULT = 3.0` instead of 2.5.
> Specification shopping happens in the engineer's head, and no column stops it."*
> **Guardian:** *"The operative boundary is not read-only vs. writable, it is **pre-committed vs.
> inspected**."*

**The enforceable control (converged across four memos):**
1. **Pre-registration BEFORE inspection** — the SHA-locked `flow_prereg` machinery already built.
   *Challenger:* corpus reads are permitted only while an active prereg hash exists.
2. **An access log** `(caller, ts, query_sha)` so the ordering is auditable after the fact. The
   only auditable form of "not chosen after seeing the history" is the inequality
   `prereg.registered_at < first_corpus_read(observable)`.
3. **A `corpus_derived` taint stamp** on any parameter whose derivation touched the corpus —
   research/display only until confirmed forward on data postdating its registration.
4. **Point-in-time or nothing** (Guardian, Economist): if a source cannot say what it said *on
   that date*, it does not enter. Use **ALFRED vintages, not current FRED** — a revised series is
   not the series a 2008 observer saw. Backfilled series stamped `vintage='revised'` or they are
   "a lookahead corpus wearing a history costume."
5. **Import firewall with a contract test**, in the `referee_wikipedia` style — held-out is a
   *test*, not a comment.

**Nice provenance note (Challenger):** the sealed-envelope protocol is **Sornette's own** — his
2009–10 Financial Bubble Experiment published SHA-256-sealed ex-ante forecasts, revealed later.
*"That protocol is the transferable asset from his programme."*

**Committee alignment stays dead** — unanimous. A current-roster join to old trades is
lookahead, and a read-only label does not decontaminate it. The corpus may *host the anatomy*;
it may never yield a rate.

**What to ingest (free), merged:** FRED/ALFRED vintaged (`USREC` 1854, `UNRATE` 1948, `T10Y2Y`
1976, `VIXCLS` 1990, `BAMLH0A0HYM2` 1996) · OFR STFM (already wired) · CFTC COT to 1986 ·
EDGAR forward-only.
**⚠ The Economist surfaced the item nobody else did:** **HackerNews Algolia, 2007–present**
(`research_history.py`, free, already coded) — *"a nineteen-year **attention** panel, the substrate
our product actually runs on, and no amount of price data substitutes for it"* — plus **Wikipedia
pageviews 2015–** as the cleanest long non-price participation series.

**The number that governs everything here:** daily data back to 1976 is ~12,000 rows but only
**eight to twelve independent crisis episodes.** *"The unit of observation is the episode. n ≈ 10.
Say that on the face of every corpus-derived finding, or the row count will be mistaken for
power."* The Outsider is blunter: *"That is not a sample. Any model fit to it is fit to anecdote,
and I will say so in diligence."*

---

## 3. Q2 — CRASH PHYSICS

### 3a. Mandelbrot — ACCEPTED UNANIMOUSLY, and he indicts our own engine

Not a model to build; a **critique of our estimator**. The Economist verified the specifics, and
one of them falsifies a premise in my own board pack:

> **⚠ "We already use median/MAD in places" is FALSE.** Grep across `transfer/`: **zero**
> occurrences of MAD. Median appears three times, none as a scale estimator.

What the code actually does (`market_signal_engine.py`):
- `get_market_baselines(lookback=12)` — `statistics.mean` / `statistics.stdev` over **12 cycles**,
  floored at 0.05 on write and again on read.
- `_z_to_unit` is **piecewise linear and saturates at z ≈ 3.18** — so **z = 3.2 and z = 32 return
  the identical number.** *"In Extremistan the observations carrying essentially all the
  information are compressed to a constant. This is not tail-robustness failure; it is tail
  deletion."*
- **The detector self-blinds during cascades — verified.** `baseline_cycles = cycles[1:lookback+1]`
  means a spike enters its own subsequent baseline, inflating the denominator and suppressing the
  *next* reading. Mandelbrot's long memory says large changes cluster — *"so the machinery goes
  deaf precisely in the regime the crash panel exists to detect."*

**Prescription:** median/MAD×1.4826 as interim scale; exclude a spike from its own subsequent
baseline; **remove the z≈3.18 saturation**; and make the *served* statistic an **exceedance rank
with a Wilson interval** ("this reading exceeds all but k of the last N of this instrument's own
history") — distribution-free, needs no variance, survives fat tails. Demote z to a diagnostic.

### 3b. Sornette / LPPL — rejected as a price fitter; a narrow non-price port survives

**On the price version, no dissent.** The Guardian was categorical: *"It is a price forecast with
a date attached, and it fails my own test outright: the natural next sentence after 't_c is
mid-September' is 'so sell before then.' The Chairman's endorsement does not change the physics of
that sentence, and this memo exists precisely for the case where a good idea arrives with
authority."*

**The replication record, honestly assembled:** Feigenbaum (2001) found log-periodic precursors
statistically weak under proper testing; Chang & Feigenbaum (2006, Bayesian) found LPPL does not
beat simpler nulls once model flexibility is priced; Bree & Joseph (2013) and Bree/Challet/Peirano
established that LPPL is a **sloppy** model — a multi-modal objective where the confidence interval
on `t_c` is often **wider than the horizon being forecast**. Seven-plus free parameters against
fewer than ten usable events. *Outsider: "Parameters ≥ events. The first question in any quant
diligence is 'how many pre-registered, out-of-sample t_c calls have you made, and what is your
false-positive rate?' If the answer is 'Sornette's', the answer is 'then I'll buy Sornette's.'"*

**The split on the non-price port is precise and worth preserving** (Challenger): the
**finite-time-singularity** term (positive feedback → hyperbolic blowup) is substrate-general and
defensible on attention. The **log-periodic** term derives from *discrete scale invariance*, and
nobody has demonstrated DSI in an attention substrate — *"fitting ω and φ to our series is
cargo-culting until DSI is independently shown."*

And a decisive semantic point: **on attention, `t_c` is a peak, not a crash.** Attention peaks
constantly with no crash. So the honest object is a **peak-timing estimator** — price-free,
firewall intact, scoreable against a ledger we already own.

**Two archetypes would permit Stage-1 only** (super-exponential detection, 3 parameters, `t_c`
reported with a bootstrap interval and served as "not identified" whenever the interval exceeds
the horizon), against an **IAAFT/phase-randomised surrogate null** plus the placebo cohort, with a
**false-alarm rate published before the first live alarm.**

**Two would not build it at all.** The Executioner benchmarked rather than argued: LPPL with linear
parameters subordinated, 4 nonlinear free, 750 points, scipy LM = **14.9 ms/restart** on a laptop;
a modest 50-window × 100-restart protocol is ~3 min of pinned CPU per instrument per day →
**~17 CPU-hours/day at 300 instruments** on a dyno with 24, already running collectors, scorer,
prewarm and the serve path. §13 exists for exactly this; the 2026-07-06 outage is the precedent.
He adds the data objection: LPPL needs long, dense, accelerating series, and *"the topics we exist
to catch are by construction the ones with almost no history (§16a)."*

**The Guardian's conditions, if the Chairman proceeds with Stage-1 anyway:** the
`HELD_OUT_ARRIVAL_INPUTS` registry and its contract test must exist **first**; the fitting path
reads **zero** price series (grep-enforced); **the null test precedes the first real fit** — fit
the model to a synthetic series generated from our own 6-hourly collection schedule and to
phase-shuffled surrogates, and *"if it fits those, the instrument is measuring us and the work
stops there"*; and **`t_c` may never leave the process** — not an API field, not a log a customer
can see. *"A date is the exact payload that converts measurement into a countdown."*

### 3c. Bouchaud & Potters — accept the hygiene, defer the machinery

Robust scale + rank normalisation (~1 day, no new data). **Hill tail-index as a diagnostic, not a
display** — used for one decision only: *does a variance exist here?* If α ≤ 2, mark that
component's z meaningless rather than serve it.
**RMT correlation cleaning is not implementable and the reason is on the record:** 300 instruments
over 12 baseline cycles gives q = N/T = **25**; under Marchenko–Pastur essentially the entire
eigenvalue spectrum is noise. *"You cannot clean what was never estimated."* Register the trigger
at **T ≥ 4N**; build nothing now.

---

## 4. Q3 — THE PANEL, AND THE NAME

**Unanimous: a stage label, not a score.** A 0–100 asserts euphoria is 1.6× expansion — a claim no
theory makes and ~10 episodes could never calibrate; a number invites a ranking, and a ranking
invites a trade.

**The name.** Verified in code: `enterprise_intel.py:55` — `COMPONENTS = ["G","I","M","D","C","P","N"]`,
and `W_OVERALL = {**_SW_O, "N": 0.0}`. **That zero weight is the non-circularity guarantee.**
So "N Market Score" *and* "N Market Analysis" both collide — the problem is the letter, not the
noun. *Guardian: "Nor a new letter — letters accumulate into a private alphabet nobody outside can
audit."* Proposals: **Participation Regime** (Guardian, Outsider) · **Market Regime Stage**
(Economist) · **Flow Register** (Executioner).

**Vocabulary matters** (Guardian): reject Kindleberger's affect words on a surface — "euphoria",
"distress", "panic" read as counsel. Use measurement vocabulary over the participation observable:
**Quiet / Broadening / Accelerating / Concentrated / Unwinding.**

**May state:** named observables with value, date, provenance; each observable's percentile against
**its own** history with the history length shown; a stage from a published, pre-registered rule;
`CALIBRATING` per §16a; honest absence per §17; corpus analogues **labelled as analogues, never as
probabilities**.
**May never state:** a crash probability · a date or `t_c` · "elevated risk" without a denominator ·
anything per-instrument · any composite mixing attention with money · **any backfilled stage
presented as if emitted live.**

**The guard nobody else stated** (Challenger): if we publish stages we will be judged on them, and
without a resolution record we will remember only the hits. Resolution must be a **non-price**
observable. And the base rate is brutal — *"the honest headline for a long time is **'0 resolved
episodes since inception'**."*

**Ship timing** (Executioner): §17 + §16a mean that on ship day the panel renders honest absence on
every row, because the flow ledger has zero events and `publishable` is `False` by design. *"A
panel whose only truthful content is 'insufficient evidence' is not a panel."*

---

## 5. THE COMMERCIAL VERDICT (Outsider, standing alone and worth reading in full)

> *"Crash calling has **negative expected commercial value**: the loss case is attributable, the
> win case is not. Client de-risks on your signal and the market rallies 14% — that loss appears in
> their attribution report with your name on it, and it ends the relationship and the referral
> chain. Client de-risks and the crash happens — nobody pays a premium for having been right once,
> because they cannot distinguish you from the forty other people who also called it."*
>
> *"Sornette's Financial Crisis Observatory has published ex-ante calls since 2008. Eighteen years
> later it is not an institutional standard and no allocator I know pays for it. That fact IS the
> diligence datum: if it worked at the claimed strength, the market for it would exist."*
>
> *"'Measurement not advice' is a posture, not a shield. A crash-risk gauge on an enterprise screen
> that a client acted on is advice in front of a plaintiff's lawyer, and your disclaimer
> top-and-bottom will be read to the jury as evidence you knew."*
>
> **On R7, as a buyer:** *"Sixteen of three hundred, every one a mega-cap, ordered Apple > Nvidia >
> Microsoft. That is not a flow signal, it is a **famousness ranker with a flow label**, and it was
> live in production... Does it change my diligence posture? Yes — in both directions. Worse on
> maturity: nothing you have published about market signal is citable to me today. **Better on
> integrity:** the team found it, captured a before-state, wrote falsifiable predictions in
> advance, flipped config-only with a one-command rollback, and pre-annotated the expected
> transient. That is better process hygiene than most Series A companies I sit on."*
>
> **The sequencing red flag:** *"You just discovered your first market panel was structurally
> broken, and the proposal on the table is a second, more dangerous market panel. That ordering is
> the actual red flag — bigger than the defect."*

---

## 6. SIX DEFECTS FOUND IN THIS SESSION'S OWN CODE — ALL REPRODUCED AND FIXED

Each was independently reproduced by probe before any change (§10a), then pinned with a regression
test. Committed in `77515f1`.

| # | Defect | Severity |
|---|---|---|
| **D1** | **`enroll()` could write a LONE TREATED ROW while reporting success.** Control ids omitted `match_group`, so two treated tickers on the same date sharing a control collided; `ON CONFLICT DO NOTHING` swallowed the insert while `written` counted *iterations* not inserts, so the all-or-nothing parity check passed. Reproduced: enroll B returned `{'enrolled': True, 'controls': 3}` having written **one row**. **The module's headline guarantee — the Board's #1 constraint that the control arm can never be retrofitted — was false.** My own suite missed it because it never enrolled two treated rows on one date; controls are matched on sector + size + liquidity, so overlap is the NORMAL case on a heavy filing day. | **CRITICAL** |
| **D2** | `sweep()` used module/env thresholds, so a dyno config change would silently re-resolve **already-enrolled** rows under a different definition — the exact failure the module exists to prevent. Now read from the row's own `prereg_id`. | HIGH |
| **D3** | `report()` pooled rows across pre-registrations while the banner came from the active one — enroll under A, dislike the trend, re-register as B, and B's terms displayed over A+B's rows with no reader able to see A existed. *"Specification shopping, shipped, inside the module built to prevent it."* Now cohort-scoped, with `prereg_history` surfaced and `publishable=False` while a superseded cohort holds rows. | HIGH |
| **D4** | `_flush_rejects` ran only on the success path — so in the regime where refusals carry the most information, nothing flushed and the counters died with the dyno. | MEDIUM |
| **D5** | `already_arrived_before` counted 2 hits anywhere in a 10-session lookback while `find_arrival` required 2 within 5 — still shrinking the lead denominator flatteringly. | MEDIUM |
| **D6** | A key named `dollar_volume` held **share** volume, in the module rewritten to end that confusion. | LOW |

---

## 7. STILL OPEN — findings from round 4 not yet actioned

| # | Finding | Source | Recommendation |
|---|---|---|---|
| **O1** | **The `HELD_OUT_ARRIVAL_INPUTS` registry does not exist.** It appears once in the repo — as *prose*, in a board doc. No Python defines it; the promised contract test does not exist. *"My R2 firewall is currently a memo, not a mechanism."* | Guardian | Build the registry + contract test **before** any further arrival work |
| **O2** | **Live R1 breach.** `market_accuracy_ledger._regime_adjusted` computes **excess return vs SPY** with a `confirm_rate_pct` — a hit rate on beating the market — served in the report payload. A "do not publish externally" comment is **not a control**. | Guardian (R3 + R4) | Gate behind an env flag defaulting **off**; preserve rows; mark internal. **Chairman ruling needed** |
| **O3** | `compare_arms` sets `separated = any horizon disjoint` across 30/90/180 — **three chances at the null**. | Challenger | Pre-register **one** primary horizon; others descriptive |
| **O4** | Control tickers reused across match groups → non-independent observations; KM assumes independence, so the control interval is **too narrow, in our favour**. | Executioner | Sample without replacement across open episodes, or state the clustering and widen |
| **O5** | `sweep()` issues one `arrival_for` per row with **no §13 pacing**; must run in the scheduler thread, never behind an endpoint. | Executioner | Fix before enrollment |
| **O6** | New `*_date` columns need §14 datecanon registration; `flow_pending_detections.timeout_date` belongs on the operational allowlist, as its three siblings do. | Executioner | Register before B3a auto-discovers and flags them |
| **O7** | **Nothing is wired.** Zero imports of `flow_ledger` / `arrival_clock` / `ledger_survival` outside those three files. No endpoint, no scheduler hook, no `flow_integrity` agent, no pre-registration row. `insider_feed()` still `__main__`-only. | Executioner | This *is* Phase 2 |
| **O8** | The estimator defects in §3a (no MAD, z-saturation at 3.18, spike-in-own-baseline). Score-affecting → backtest-before-ship. | Economist | Highest-value free accuracy work available |

---

## 8. THE EXECUTIONER'S SEQUENCING FINDING

> *"Zero rows are enrolled. Phase 1 is built but inert, Phases 2 and 3 untouched. The ledger's
> value is monotonic in **elapsed calendar time**, not in engineer effort — every round that adds
> questions before enrollment pushes the first interpretable read out one-for-one. Four rounds in,
> the instrument that was supposed to start ticking has not started. That is the finding."*

**What he cuts:** LPPL outright (keep the fat-tail consequence, drop the fitter) · the panel until
`report()` is publishable · the corpus to one source, after Phase 2 · **nothing from Phases 1–3.**

---

**Chairman — decisions requested:** the panel NAME (letter-free); whether Stage-1 non-price
critical-point work proceeds as research or is cut; **O2** (the live excess-return breach); how
much corpus to build now vs after Phase 2; and confirmation that Phase 2 (enrollment) is the next
build.
