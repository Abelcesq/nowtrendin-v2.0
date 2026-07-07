# Scoring Integrity Assessment + Dark Matter Review (2026-07-07)

Read-only assessment. Sources: live `/accuracy/ledger` + `/market/accuracy`, code-level sweep of
`gravitational_anomaly_detector.py` / `scoring_weights.py` / `dual_pathway.py` /
`market_signal_engine.py`, `docs/METHODOLOGY.md`, `audits/ledger-research/LED_FEATURE_MINING_2026-07-07.md`.

## 1. What is verifiably SOUND (checked in code, not asserted)

1. **N non-circularity holds.** N appears in NO weight vector (`scoring_weights.py` has no N key;
   `scoring_contract` marks `in_composite: False`). The one thing the platform must never do —
   validate its score with its own engagement — is structurally prevented.
2. **The accuracy ledger is held out.** Calibration modules carry zero ledger references; the sweep
   cannot touch a score. Verdicts are measurement only.
3. **Dual pathway + Mainstream v2** (≥5 INDEPENDENT outlets, syndication-collapsed
   `min(outlets, distinct titles)`, else dark-matter TRIGGER) is implemented as documented.
4. **Weights single-sourced + renormalized** (`scoring_weights.py`); Detection is G(37.5%)+D(21.6%)-led,
   Confidence is I(27.8%)+P(26.7%)+M(22.2%)-led — coherent with the earliness/precision duality.
5. **Serve integrity**: INV-1 (stale rows serve stored values), calibration failures now logged +
   stamped, canonical dates gated + audited, forward-only retention.

## 2. Integrity concerns / improvement areas (ranked)

- **A. D's weighting contradicts its empirical timing (see §3).** D carries 21.6% of Detection but is
  0 at first sighting for winners AND near-misses; it fires late. The Detection weight buys little
  earliness today.
- **B. Corroboration-floor exemptions are moat-based** (`hasx` expert/niche-origin marker + high
  magnitude + tracked calls bypass the floor). The research-feed extractor closed one junk path, but
  the exemption is structural: ANY expert-tier source's fragments bypass corroboration. Candidate
  hardening: require exempted single-source topics to also pass a stricter quality bar, or expire the
  exemption after N cycles without a second source.
- **C. N ranking loop (display-side only).** Viewing a topic logs a query → N rises → the
  "Now TrendIn" view ranks by N → more views. N never touches the score (verified) and the metric
  honestly measures "how often surfaced," but the ranking view has a rich-get-richer dynamic with no
  per-viewer dedup (only /scores first-page-only guard). Options: per-session dedup on
  `_log_topic_query`, ranking-side recency dampening, or accept + document. Founder decision.
- **D. Ledger denominator caveats to keep publishing loudly**: 0 false positives exists ONLY because
  no row has reached the 365-day timeout yet (first possible mid-2027); the EMERGING cohort headline
  (2.3% of 44) rests on the sustained-days fallback for ~97% of rows — populate `topic_maturity`
  properly before leaning on the cohort split.
- **E. Sweep feedback latency**: 898 pending at 32 checks/day (rotation oldest-first). Honest but
  slow. Operational option (no integrity cost): split each sweep 6 oldest + 2 newest so the new
  first-crossing cohort produces early readout.
- **F. Stage definition duplication**: scoring stores `signal_stage` from OVERALL thresholds
  (85/70/55/35) while UI stage chips key off DETECTION (`stageOf`). Two stage vocabularies for one
  concept — reconcile or document which is authoritative where.
- **G. Market Signal open items**: positioning floor-pin (no-coverage instruments read "ROUTINE 30.0"
  as if measured — §17 violation in spirit; backtest-gated fix queued). Market ledger asymmetry
  (inflow 3/3 confirmed vs outflow 0/3) — treat outflow reads as low-confidence until sample grows;
  consistent with the insider-selling-is-degenerate finding.

## 3. Dark Matter — what it IS, what the data showed, and the confirmation question

**What D actually measures (trend side; code-verified):** NOT source tier. D is a *behavioral*
inference: 65% first-timer ratio (new authors entering the topic) + 35% engagement asymmetry
(comments ≫ upvotes), scaled by organic quality (`compute_dark_matter`). Platform tier feeds G
(niche-vs-mainstream concentration) and M (spread + tier-span bonus) — not D directly.
**Market-side D (Money Movement):** Finviz insider Form-4 BUYING (primary; AV fallback), 13F
institutional change, Congress trades (Quiver), OFR funding stress.

**How D is used in discovery today:** #2 Detection weight (21.6%); thin credible media stays a
D-side TRIGGER under Mainstream v2 until quorum. The thesis: informed/niche chatter precedes crowds.

**What the ledger mining showed (2026-07-07, read-only):** at FIRST sighting D=0 for LED winners AND
near-miss losers alike; D=40 for pre-broken (already-big) topics. Mechanically sensible: first-timer
ratio and asymmetry need engagement volume to be measurable — a 4-mention day-one topic can't
produce them. **Empirically, today's D behaves as CONFIRMATION (informed attention arriving after
the story is real), not discovery.** Wins were led by M-breadth at first sighting (median 80 vs 50).

**Assessment of "use D as confirmation" (founder's revised framing): SUPPORTED — with precision.**
Two moves, both integrity-clean (D is external data; no circularity), properly sequenced:
1. **Fix D's earliness on the input side** (keep the thesis): the research-outlet feeds are built +
  flag-gated (`GHOST_RESEARCH_FEEDS`); X first-timer pulls and more niche communities extend this.
2. **Additionally use D's ARRIVAL as confirmation**: a topic detected early on M/G whose D
  subsequently rises has been confirmed by informed attention. Natural homes: (a) a DISPLAY-ONLY
  "informed-attention confirmed" marker + ledger annotation (measurement, shippable without
  backtest), (b) a re-weighting experiment (raise D in Confidence above today's 4.4%, trim its
  Detection share) — SCORE-AFFECTING, so it requires the held-out what-if backtest first: recompute
  the resolved cohort's scores under shifted weights and test whether winners separate better.
  Recommended next build.

## 4. Yesterday's accuracy-ledger changes — plain-language record

What changed (all measurement-side; NO stored rows edited; ledger still held-out; blended honest
rate still counts everything):
1. **Enrollment (forward-looking fix):** the ledger used to enroll the CURRENT LEADERBOARD TOP-N —
   topics already big, which Google had usually already broken out on → verdicts defaulted to
   LAGGED and the ledger measured discovery latency, not the race. Now it enrolls FIRST-CROSSERS
   (first seen ≤14 days ago, crossing the detection floor, ESTABLISHED/MONITORING excluded).
2. **Pre-broken split (report-time relabeling):** among the 59 old "LAGGED" rows, 44 had their
   Google breakout MORE THAN 7 DAYS BEFORE our first sighting — races over before the engine ever
   saw the topic (June-13 bulk enrollments lagging May breakouts). They stay fully counted in the
   blended 10%; the new **tracked-race rate (26.9% = 7 LED of 26 races actually run)** reports the
   claim-relevant subset. Both rates always published together.
3. **Match validity:** every new resolution records the exact query matched + an ambiguity flag
   (bare geo/single words like "mexico" = weak evidence); LED/SAME_DAY wins get an independent
   Wikipedia-pageviews referee (±14d). Old wins honestly read "referee unchecked."
4. **Surfaces:** chips/stat cards on web + mobile + desktop; click/tap a row → the deterministic
   Ledger Entry Analysis panel (method of tracking + verdict meaning + match validity).

**"Dark matter updates on the accuracy ledger": there were NONE.** No D code changed, and the
ledger has no D coupling. What happened: the ledger's resolved rows were READ (read-only mining)
and joined to each topic's first score to ask "what did winners look like at detection?" — that
analysis produced the D-is-late-confirmation finding above. The only D-related change shipped is
the flag-gated research feeds (input side), currently OFF awaiting the founder's flip.

## 5. Recommended next actions (priority order)

1. Flip `GHOST_RESEARCH_FEEDS=1` for the monitored 2-week trial (input-side D earliness).
2. Build the held-out D-weight what-if backtest on the resolved cohort (gates any reweighting).
3. Ship the display-only "informed-attention confirmed" marker (measurement, no score change).
4. Populate `topic_maturity` so the EMERGING cohort headline stands on real classification.
5. Harden the corroboration exemption (quality bar or expiry on single-source moat topics).
6. Decide the N-ranking loop treatment (dedup / dampen / document).
7. Sweep rotation: 6 oldest + 2 newest per run for early first-crossing readout.
8. Reconcile the stored-stage (overall) vs UI-stage (detection) duplication.
