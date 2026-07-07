# LED vs LAGGED — Detection-Time Feature Mining (2026-07-07)

**Read-only research.** Mined from `accuracy_ledger` joined to each topic's FIRST
`velocity_scores` row (read-only SELECT against the live engine DB). No score, threshold,
or ledger change follows from this note without founder sign-off + backtest (flag-never-force).

**Samples are small (7 / 15 / 43) — every finding below is DIRECTIONAL, not conclusive.**

## Cohort medians at first score

| Cohort | n | Det | Conf | D (dark) | M (breadth) | G | I | P | Mentions |
|---|---|---|---|---|---|---|---|---|---|
| LED (won the race) | 7 | 23.4 | 50.0 | **0.0** | **80.0** | 17.0 | 9.8 | 100.0¹ | 4 |
| NEAR-LAG (lost by ≤7d) | 15 | 24.8 | 45.6 | **0.0** | 50.0 | 0.0 | 9.8 | 0.0 | 4 |
| PRE-BROKEN (never a race) | 43 | 28.5 | 42.5 | **40.0** | 50.0 | 44.8 | 9.7 | 30.0 | 3 |

¹ P=100 at "first score" for LED rows is suspect — a first sighting should have low
persistence. Likely the stored first row postdates true first detection (bulk-enrollment
era) or reflects a re-score. Treat P here as unreliable metadata, not signal.

## Findings (directional)

1. **Dark Matter (D) is not currently an early-warning input — it is a late-confirmation
   input.** D was 0 at first sighting for BOTH the winners and the near-misses; it was 40
   for the pre-broken cohort (already-big stories where insider/positioning data exists).
   The races we win are won on breadth-of-first-appearance (M), not on D. This is direct
   empirical support for the §15 GHOST_FEEDS expert/niche expansion: the D that should fire
   *early* (research outlets, expert blogs, first-timer authors) largely doesn't exist in
   these rows yet. The designed M/D provenance reweighting targets exactly this gap.

2. **Early cross-platform breadth separates winners from near-misses.** LED median M = 80
   vs near-lag M = 50 at first score. When a topic shows up on many platforms *at first
   sighting*, we tend to beat Google; single-lane first sightings tend to lose by days.
   (Candidate for a backtest-gated enrollment/priority feature — NOT a score change.)

3. **The near-misses are close enough that latency fixes matter.** Median near-miss loss ≈
   −4 days; 5 of 15 lost by only 1–2 days, and 6 of the 15 are tech/AI topics (ai_agents,
   model_context_protocol, kimi, claude_mythos, world_models, access_to_fable) — the
   fastest-moving category. A Dark-Matter-triggered fast-lane recheck (free sources only,
   recommendation G from the 2026-07-07 analysis) plausibly flips the 1–2-day losses.

4. **Pre-broken rows look exactly like what they are** — topics that arrived at the engine
   already big (higher G 44.8, D 40, P 30 at "first" score). Their exclusion from the
   tracked-race view (2026-07-07 segmentation) is validated by their feature profile.

## Recommended next steps (all gated)

- Ship GHOST_FEEDS expert/niche outlets (backtest first) — directly addresses finding 1.
- Prototype a "breadth-at-first-sighting" enrollment priority (measurement-side only;
  backtest against this same cohort before any use beyond enrollment ordering).
- Build the free-source fast-lane recheck for D/M-triggered candidates — finding 3.
- Re-run this mining when the first-crossing enrollment cohort resolves (the current rows
  are all pre-fix enrollments; the new population is the real test).
