# EVIDENCE PACK — Current Status + Recent Updates (2026-08-04)

**What is being decided:** The Chairman asks the board to (a) assess the platform's current
status as verified by the 2026-08-04 full health check, (b) judge the recent updates shipped
since the last board sessions, and (c) recommend on the two pending founder flips and the
prioritization of the outstanding build items. Nothing here is pre-approved; the board informs,
the Chairman rules.

All facts below were verified LIVE against the deployed engine on 2026-08-04 (UTC 02:00-02:40),
not quoted from documentation.

## 1. SERVICES + FLEET (verified live)

- Engine v2 UP (release **v309**, deployed this session) · Django backend UP · web terminal
  (GitHub Pages) 200 · web build clean (3.3s).
- Monitor fleet (9 read-only agents): 7 ok, 2 warn —
  (w1) pipeline_integrity B3: "60,879 served risk rows predate the newest display guard" —
  KNOWN over-count: the census counts ALL historical risk_scores rows, not latest-row-per-topic;
  denominator fix is an open task.
  (w2) cost_sentinel B7: TOTAL $592.81 = 85% of the $700/mo cap (DOWN from $718.82 — the Apify
  clock-slot fixes landed; trajectory improving).
- Collectors: **18 HEALTHY / 0 down / 2 DISABLED** (finnhub_congress deliberately retired;
  reddit deferred by founder). finviz_insider HEALTHY (170 signals, 81 distinct tickers, 28m
  fresh); finnhub_insider HEALTHY.
- Serve-time category maps warm from live refresh (60,146 context entries). Prewarm fresh.

## 2. LEDGERS (the moat) — verified live

- **Trend (attention) ledger:** intake ALIVE after the July dead era — last cycle ok, 45
  enrolled in window; completeness honestly reads 46.9% (15 ok / 17 failed cycles; the 17 are
  the pre-fix dead era, kept in the denominator). pending=1134; blended hitRate 11.7 stamped
  `hitRateProvisional: true` (referee corroboration outstanding: ledCorroborated=0).
- **Market (money) ledger:** 25 resolved / 6 pending; published rate **withheld** —
  clean-cohort-only under MARKET_MIN_PUBLISH_N=30, with the dead-parser era quarantined in a
  `dead_parser_era` block (affects_prior_reads disclosed).
- **Crypto ledger:** 1 resolved / 1 pending; rate withheld under the same n=30 floor.

## 3. RECENT UPDATES UNDER REVIEW (shipped since the last board sessions)

**U1 — S7: INSIDER_FLOW=1 (v308, 2026-08-01).** Hourly market-wide Form-4 ingestion into the
append-only insider_events panel. Pre-flight gates were all green (parser fix live, actor salt
set, prereg 2d65eac796c28476 active, term_drift []). Panel now: 397 events, 244-ticker
universe, 3+ days accrual. FLOW_ENROLL remains 0 — nothing enrolls until the founder fires it.

**U2 — Liveness false-RED found + fixed during the health check (f1e97af, deployed v309).**
The insider panel's coverage watermark counted distinct tickers only for newly-INSERTED rows;
every steady-state hourly ingest of the slow-moving feed (~100% idempotent duplicates)
collapsed to "170 raw → 4 distinct" and fired the dead-parser RED on a HEALTHY source
(collector_health parsed 81 distinct from the same pull; the first ingest's 61 masked the
defect because the panel was empty). Fix: coverage counts every ticker that survives the
reject gates, BEFORE the duplicate check. Regression proven both directions (all-duplicate
pass reads full coverage GREEN; a genuinely dead parser still fires RED). The stored RED
clears at the first post-v309 hourly ingest.

**U3 — Crypto ETF share-flow leg, Stage 1 DEPLOYED DARK (v309; CRYPTO_ETF_FLOW=0).**
Built per BOARD_crypto-flow-design_2026-08-01.md and the pre-declared spec
audits/board/CRYPTO_FLOW_SPEC_v1_2026-08-02.md (SHA c3bf3eeb8e1a2201, committed BEFORE any
flip). Shares = AUM ÷ NAV (never AUM — circularity ban). CURRENCY PASSED day 5 and holds at
day 8: 11/15 ETFs show real day-over-day share movement. Shadow votes verified live on
/diag/etf-flow through the REAL _etf_flow_vote: FBTC −1.0 (capped, −1.47%/day redemption),
GBTC −0.618 (measured, not pinned), BITB +0.12, quiet funds 0.0 measured-quiet, zero
discontinuity stamps. All 15/15 tickers now have ≥5 observations. Coverage at $0: BTC, ETH,
SOL, XRP; seven coins remain honest-structural (no US spot fund exists).

**U4 — Prior-session items now in steady state:** trend-intake resurrection (fast path,
equivalence-gated 300/300); PG txn-abort ALTER fix (3 sites); D1/D2 display honesty (absence
never wears a measured word); Finnhub congressional endpoint retired; insider dominance rule
(accumulation requires buy_usd > sell_usd); AI-context stored-refusal purge.

## 4. PENDING FOUNDER FLIPS (the board is asked to recommend)

**F1 — FLOW_ENROLL=1** (opens flow-ledger enrollment under prereg 2d65eac796c28476: ≥3 distinct
open-market Form-4 buyers / 10 trading days, matched controls, share-volume arrival clock,
stratified log-rank primary). Panel has 3+ days accrual; the only liveness noise was U2's
false RED. Proposed readiness: one clean GREEN ingest on v309, then flip. Success check:
pending_treated ≥ 1, pending_control ≥ 3, treated rows carrying sector+size strata.

**F2 — CRYPTO_ETF_FLOW=1** (~Aug 10 target). Spec §8 preconditions: (1) currency PASS ✅;
(2) ≥5 snapshot days each new ticker ✅ (15/15); (3) shadow votes sane ✅ so far, accruing
daily; (4) **reconciliation harness vs issuers' published flows — NOT BUILT**; (5)
**venue_diffusion freeze for crypto — designed, NOT CODED** (coverage jumping 1→6 must not
mechanically move Market Confirmation); (6) latency stamps (flow_basis/signal_latency_days)
on payload+ledger rows — NOT DONE; CRYPTO_LEDGER_CLEAN_COHORT_START moves in the same config
change as the flip.

## 5. OUTSTANDING BUILD ITEMS (board asked to prioritize)

- Reconciliation harness (F2 gate 4) · venue_diffusion freeze (F2 gate 5) · latency stamps.
- S6 census denominator fix (latest-row-per-topic; clears monitor warn w1).
- Trend-ledger referee corroboration (rates stay provisional until done).
- S8 batch: signed momentum (own design+backtest), "N" naming (founder ruling pending),
  incremental prewarm, plain-English relabel.
- Falsered-board leftovers: topic_current head table (O(N-history) class, ~15 sites),
  topic_maturity coverage-0 investigation, D9 restart with real randomization.
- COT §16 onboarding (free; bitemporal knowable_at = Friday publication) + 13F-of-IBIT via
  WhaleWisdom (already paid) — next $0 crypto legs; stablecoin issuance later.
- Ops: QUIVER_API_KEY + FMP_API_KEY rotation recommended; frozen-1.0 Postgres $20/mo and
  nowtrendin-web mirror $7/mo trim candidates (founder decision).

## 6. STANDING CONSTRAINTS

$0 directive on new data costs (founder-ordered 2026-08-01). Flag-never-force. Clean-cohort
rates only, n≥30 publication floors. The accuracy ledgers are held-out and never deleted.
Verify-before-fix (§10a). Reference docs for deep dive: CLAUDE.md §13–§17,
audits/board/CRYPTO_FLOW_SPEC_v1_2026-08-02.md, BOARD_crypto-flow-design_2026-08-01.md,
BOARD_postflip-findings_2026-07-28.md, audits/DEFERRED_ITEMS.md, SESSION_LOG.md (tail).
