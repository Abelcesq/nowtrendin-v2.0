# NowTrendIn — Scoped Accuracy Figures (the ONE answer per ledger)
**Version 1.0 · figures as of 2026-08-09 (live reads) · param_version `calib-params-v3|patience365|lead365|match30|preb7|estmin14`**

> **The rule this document enforces (App Annie / Statistician / Two-Poles M-4):** one
> scoped, reproducible, N-carrying answer per ledger; never averaged across ledgers,
> asset classes, or horizons; every citation carries its as-of date and param_version;
> anything not reproducible from the retained ledgers is not citable. The live
> endpoints are the ONLY source of truth — every figure in any document (including
> this one) is a dated snapshot that goes stale as the pending pool resolves.

## 1. The canonical per-ledger answers (as of 2026-08-09)

### Attention ledger (`GET /accuracy/ledger`) — the only ledger with a citable rate today

> **ORDER REVERSED 2026-08-21 (board round 4, Buyer's Desk; Chairman-ruled).** This section
> previously LED with 27.1% / 48 races and carried the current-engine number in a subordinate
> clause. Everything was disclosed — but a headline about a system we no longer run, with the
> live number below it, is the shape *SEC v. App Annie* (2021) penalised: the enforcement was
> for MISDESCRIBING methodology and controls to buyers, not for bad data. Emphasis is part of
> a description. The figures below are unchanged; only which one leads has changed.

- **CURRENT ENGINE — the number to quote: 5.0% tracked-race hit rate (n = 20).**
  Blended honest rate 2.9%. Races still young and maturing under the 365-day window.
  **This is the engine that is running today. It is the only rate that describes the
  product a buyer would be licensing.**
- **RETIRED v1 ENGINE — history, not performance: 42.9% tracked (n = 28), 15.8% blended.**
  Cite only as prior-epoch history, always named as retired.
- **POOLED ACROSS BOTH EPOCHS: 27.1% tracked (N = 48 races), 11.7% blended (N = 111
  resolved, of which 63 were pre-existing breakouts that were never races).** **Do NOT lead
  with this figure.** 76 of the 111 resolved rows come from the retired engine, so the
  pooled number mostly measures a system that no longer exists. 1,195 detections pending.
- **Mandatory qualifications on ANY citation:**
  - **PROVISIONAL, AND THIS IS THE MOST MATERIAL LINE IN THE DOCUMENT** — **0 of the 13 LED
    wins are corroborated by the independent Wikipedia-pageviews referee**, and 10 of them
    sit on ambiguous single-word queries. The early-detection claim is the entire moat, and
    it is currently *unverified by any independent instrument*. This belongs in the first
    breath of any accuracy conversation, not in a footnote. The API itself stamps the rate
    "served for transparency, not citation."
  - **Epoch split** — see above. Quoting 27.1% without the split mostly quotes the retired
    engine.
  - Kaplan-Meier eventual-confirmation estimate 4.0% (1,243 observations, 1,195
    censored) is a held-out COMPANION read, never a substitute.
  - Enrollment completeness 69.6% (39/56 cycles) — intake gaps are disclosed, not
    hidden.

### Market (equity Money Gradient) ledger (`GET /market/accuracy`)
- **No published rate — by design.** `confirm_rate_pct` is withheld until the clean
  post-parser-fix cohort reaches 30 resolved (today: 4 clean; 22 dead-parser-era
  rows are excluded from every rate as "not defensible at any n"). The record, not
  the rate: 15 confirmed / 11 not confirmed / 0 no-move; 6 pending.
- **A buyer must NOT divide 15/26 (=57.7%)** — that blends the excluded era; the
  displayed counts are the record, the withheld rate is the discipline.

### Crypto Money Gradient ledger (`GET /crypto/accuracy`)
- **No published rate.** 1 resolved (dead-parser era, excluded), 0 clean, 1 pending.
  `small_sample: true`. Nothing citable exists.

### Flow/arrival ledger (`GET /flow/accuracy`, pre-registered)
- **`publishable: false`** — 0 episodes against a sealed pre-registration
  (min 120 episodes, falsifiers declared, prereg id `2d65eac796c28476`).

## 2. Figures that are NOT citable (and why)

- **Every point-in-time figure in CLAUDE.md / SESSION_LOG / audit memos**
  (26.9%, 10%, 10.8/26.3, 24.2% "anchored", KM 3.4%, v1 35.0/v2 7.7, 2.1%
  "artifact"): historical snapshots under superseded param_versions; the pending
  pool has since resolved further; they cannot be regenerated from current state.
  They are audit history, never sales material.
- **`byMaturity.emerging` 11.7%**: equals blended because maturity coverage is 0 —
  the API already withholds `earlyDetectionHitRate` for exactly this reason
  ("a segmentation label without a segmentation").
- **`naiveHitRate`**: currently duplicates `hitRate`; carries no information.
- **The catch-all %** (~33–70%): a congestion gauge, warmth-sensitive, ruled NEVER
  an accuracy KPI (CLAUDE.md §17 footer rule).
- **Pre-2026-07-28 market figures**: possibly measuring the dead parser, per the
  payload's own flag.

## 3. Defects found by this review (dispositions pending founder go — display-only)

1. **The provisional caveat is API-only**: web `Ledger.tsx` and mobile `accuracy.tsx`
   render "Honest hit rate 11.7%" as a clean stat card without
   `hitRateProvisional`/`hitRateCaveat` or the epoch split. RECOMMEND: render both
   (display-only change, all platforms; §12 parity).
2. **Mobile lacks the KM survival card** the web shows (§12 parity gap).
3. **`signal_analysis._track_trend`** frames the 111 resolved rows as the
   "emerging-topic" cohort in prose — the same segmentation-without-a-segmentation
   the API refuses to serve numerically. RECOMMEND: align the prose with the API's
   withholding.
4. **`Methodology.tsx` says "two ledgers"** — there are three live plus the
   pre-registered flow ledger. RECOMMEND: correct the count.
5. **The bare `/accuracy` endpoint** returns predictions with no accuracy rate —
   name collision inviting misreading. RECOMMEND: rename or annotate.
6. **Stale figures inside CLAUDE.md body text** should be annotated "(as-of snapshots,
   superseded — live endpoint is authoritative)" at next CLAUDE.md edit.

## 4. The DDQ sentence (verbatim, safe to give a buyer today)

> **SUPERSEDED 2026-08-21.** The prior sentence led with 27.1% / 48 races and placed the
> current engine in a trailing clause. Preserved verbatim below the replacement, per the
> ratchet rule: an amended claim keeps its old wording and the reason it changed, so the
> amendment is auditable rather than invisible.

**CURRENT (use this):**

"Our attention-detection ledger, on the engine we run today, shows a tracked-race hit rate
of 5.0% across 20 resolved races (blended 2.9%), with those races still young under a
365-day resolution window and 1,195 detections pending. This figure is PROVISIONAL in a
specific and material way: none of our 13 recorded early-detection wins has yet been
corroborated by an independent referee, and most rest on ambiguous single-word queries, so
we do not present the early-detection claim as verified. A retired prior engine recorded
42.9% tracked (n=28); pooling both epochs gives 27.1% across 48 races, but 76 of the 111
pooled rows come from the retired engine, so we do not lead with the pooled number and
advise against citing it. Our market and crypto money-flow ledgers withhold rates by design
until their clean cohorts reach pre-declared minimums (4/30 and 0/30 respectively). All
figures are recomputed from never-deleted, held-out ledgers and are reproducible on request
as of any stated date."

**PRIOR (do not use — retained for audit):**

"Our attention-detection ledger currently shows a tracked-race hit rate of 27.1%
across 48 resolved races (blended 11.7% across 111 resolved detections including
pre-existing breakouts), provisional pending independent referee corroboration, with
the current-engine cohort still maturing (5.0% tracked, n=20) and 1,195 detections
pending under a 365-day resolution window; our market and crypto money-flow ledgers
withhold rates by design until their clean cohorts reach pre-declared minimums
(4/30 and 0/30 respectively); all figures are recomputed from never-deleted,
held-out ledgers and are reproducible on request as of any stated date."

**Why the replacement is longer and worse-sounding, stated so nobody quietly reverts it:**
it is. A 5.0% that a buyer can reproduce, offered alongside an unverified moat we name
ourselves, survives diligence. A 27.1% they later discover is 76/111 retired-engine rows
does not — and under the App Annie rule the exposure is the description, not the data.
