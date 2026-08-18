# D-EARLY DESIGN — pre-registration (operator proposal, for board assessment)
### 2026-08-17 · flag-gated OFF · backtest-before-ship · board + Chairman before any flip

## 1. The problem, mechanically verified (not a hypothesis)

**Claim under repair:** "Dark Matter detects attention BEFORE it arrives." Today it does not.

**Root cause traced to code** (`gravitational_anomaly_detector.compute_dark_matter`, ~L4301):
D has exactly two evidence inputs — first-timer ratio and engagement asymmetry — and both
are STRUCTURALLY ZERO at first sighting:
- First-timer ratio requires `MIN_FT_SAMPLE = 3` author-resolving signals. A topic at first
  sighting has 1–3 signals, and news/research/ghost items are AUTHORLESS (excluded from the
  denominator) → ratio gated to 0.
- Engagement asymmetry requires `comments > upvotes × 0.30` with `upvotes > 5` on ≥2 posts.
  News, research feeds, and GAL items carry `ups=0, comments=0` → asymmetry impossible.
So D can only rise after a topic has accumulated community history — i.e., after attention
has begun arriving. **Late-confirmation is not a tuning problem; it is the input set.**

**Empirical confirmation (M0 baseline, `/diag/dark-early`, run live 2026-08-17, n=122):**

| cohort | n | first-sighting D median | % zero |
|---|---|---|---|
| LED (won the race) | 15 | **0.0** | 53% |
| near-miss (lost by ≤7d) | 31 | **0.0** | 71% |
| same-day | 10 | **0.0** | 80% |
| **pre-broken (entered late)** | 66 | **14.3** | 44% |

The inversion: D is HIGHEST on the cohort that was already mainstream and near-zero on
genuine races. Corroborating: tail-capture (2026-08-17) — of the top-decile surges we raced
12/12 but LED only 1/12; 4 near-misses lost by 1–2 days. Prior art: 2026-07-07 feature
mining (same finding on the July pool); Guardian seat 2026-08-09 ("the D leg is where
before-it-arrives is won or lost").

## 2. Proposed levers (each independent, flag-gated, separately assessable)

**Lever A — First-sighting provenance term (`D_EARLY` flag; score-affecting, the core).**
Add an earliness input D can read at sighting #1, from evidence that EXISTS at sighting #1:
- venue-class of first surfacing: expert/niche tier (GHOST research feeds, GitHub, HN,
  socialcrawl rising lane) vs mainstream discovery — the D-vs-M router (`platform_tier`)
  already tags this; today D ignores WHERE a topic first appeared;
- source novelty: topic never before seen in the corpus AND surfaced on the expert tier
  (topic_lifecycle first-sighting is already maintained);
- NOT volume, NOT engagement, NOT N (circularity ban), NOT any ledger read.
Blend: earliness evidence only when community evidence (ft/asym) is absent — a floor-in-D₀
that decays as real community evidence accrues, never a multiplier on it. Exact weights are
the BACKTEST's output, not this document's.

**Lever B — Fast-lane recheck (cadence, not score; the 1–2-day near-miss flips).**
New first-crossers get a FREE-source rescore (RSS/HN/GitHub/Wikipedia — zero Apify, zero
paid) at +2h and +6h after enrollment instead of waiting for the next 6h cycle. 5 of 15
July near-misses and 4 of today's top-decile misses lost by 1–2 days; the sweep cadence is
part of the loss. Cost: ~0$; batch-paced; capped at N=20 recheck slots/day.

**Lever C — Socialcrawl rising-lane as a D input (currently discovery-only).**
Rising queries are the earliest external attention derivative we license. Today they only
seed topic discovery; Lever A's venue-class input would read "surfaced via rising-lane" as
expert-tier-equivalent earliness evidence. No new spend (lane already funded).

**Lever D — M/D reweighting part 1 (reputable ½-weight; the standing §15 design).**
1 reputable outlet = ½ mainstream weight; full weight at ≥2 DISTINCT reputable sources.
Already designed; folds into this program so the D-side and M-side ship as one assessed
package, not two drifting changes.

## 3. Measurement plan (pre-registered BEFORE any build)

- **Stamp at enrollment:** every new pending_detection stamps `d_at_enroll` (and arm) —
  the M0 caveat (retention erosion of "first retained row") disappears for new rows.
- **A/B by `enroll_arm`** (D9 infrastructure already in the schema): arm labels only;
  scoring of arms identical until the flip — the arm records what D-early WOULD have said.
  DARK phase first: Lever A computed and logged per enrollment, feeding NOTHING.
- **Success criteria (register entry H16; Bonferroni per the 2026-08-17 register):**
  on post-change enrollments only — (i) first-sighting D median > 0 on the subsequently-
  confirmed cohort while pre-broken D does NOT rise in lockstep (the inversion must
  FLIP, not inflate globally); (ii) tracked-race rate on new-epoch rows beats the 50%
  null at the corrected threshold; (iii) tail-capture led% improves vs today's 1/12
  baseline. Trial ≥ 90 days or ≥ 50 resolved new-epoch races, whichever LATER.
- **Kill criteria:** global D inflation (pre-broken first-sighting D rising ≥ as fast as
  race-cohort D), OR fragment/junk topics entering via the expert-tier floor (topic-quality
  auditor fragment count guardrail), OR any circularity finding.

## 4. Integrity constraints (inherited, restated as binding)

No N input anywhere. No ledger verdict/rate read into any score (heldout firewall).
Fabricate nothing: earliness evidence is recorded provenance, not inferred intent.
Flag-gated OFF; serve_payload regeneration on flip; three-platform copy in the same
deploy; §16a cold-start statement not required (no universe expansion). Every cohort cut
this trial introduces is appended to the multiple-comparisons register on introduction.

*Operator note: this document is an input to the 2026-08-17 nine-seat board, not a decision.*
