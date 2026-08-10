# BOARD REVIEW — Full health check (agents · data · scoring · crypto n/a) — 2026-08-09/10

First NINE-seat convening (all full members, per the Chairman's 2026-08-09 ruling).
Identical evidence pack (`HEALTH_EVIDENCE_PACK_2026-08-09.md`, archived beside this
file: live battery 2026-08-10 ~04:30–05:00 UTC + CLAUDE.md + SESSION_LOG since 08-05
+ DEFERRED_ITEMS + scoped accuracy figures + rights register §H). No seat saw
another's output; memos were capped at 700 words. Items: **A** agents · **B** data ·
**C** scoring models per product · **D** the crypto "n/a / ABSENT" fix path
(Chairman-flagged). This is a COLLATION; no operator recommendation is embedded.
The nine full memos are preserved verbatim in the session transcript; condensed
faithfully below.

## HEALTH BATTERY SUMMARY (the facts all seats reviewed)
Engine operational · prewarm healthy (4,025-row scores superset) · category maps
warm. Collectors: 21 HEALTHY (incl. all issuer families but Canary), gdelt DEGRADED
(runs, 0 signals), issuer_canary DOWN (correct fail-closed), **socialcrawl STALE 24h**
(suspected boot-phase-vs-clock-slot mismatch; slot-skips unlogged). Monitors: 7 ok;
source_watchdog + pipeline_integrity warn (the above + 5 pre-guard risk rows);
**cost_sentinel CRITICAL: X pacing $437/mo vs $200 line**; etf_reconcile info (FMP
silent-comparison 10 divergent intervals → 09-05 evidence); crypto_price_referee
info (FMP SOL supply 3.10% / XRP 2.97% off CoinGecko). Ledgers: attention
tracked-race 27.1% (N=48) / blended 11.7% (N=111), PROVISIONAL, 0/13
referee-corroborated, epochs v1 42.9% (n=28) vs v2 5.0% (n=20), pending 1,195,
enrollment completeness 69.6%; market withheld (4/30 clean); crypto withheld (0
clean); flow 0/120 sealed; A2 re-arm 0/5 accumulating cleanly (open_bad 0).

## VERDICT TABLE
| Item | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist | Operator | Statistician | Forecaster |
|---|---|---|---|---|---|---|---|---|---|
| A agents | APPR-W/C | APPR-W/C | APPR-W/C | APPR-W/C | SHIP 3 fixes / CUT gdelt | APPR-W/C | DURABLE-w/defect | SOUND, 2 defects | MIS-SCORED (socialcrawl) |
| B data | APPR-W/C | APPR-W/C | APPR-W/C | APPR-W/C + REJECT Guardian-state | rotations SHIP-NOW; Guardian decide-or-disable | APPR-W/C | DECAYING on rights | mechanics SOUND; rights UNSUPPORTED | WELL-SCORED, referee debt |
| C scoring | APPR-W/C (load-bearing) | trend APPR-W/C; rest APPR | trend APPR-W/C; crypto = beachhead | APPR discipline + display conditions | SHIP display batch + referee run | trend APPR-W/C; rest APPR | attention DECAYING; rest NOT-AN-EDGE-yet | attention OVERFIT-RISK on citation form; rest SOUND | attention MIS-SCORED at margin; market WELL; crypto UNSCORABLE-honestly |
| D crypto n/a | APPR-W/C | APPR path / REJECT shortcuts | APPR-W/C + on-chain workstream | APPR path, 2 conditions | SHIP-in-order; CUT cosmetics | APPR absence; REJECT interim fill | DURABLE path | SOUND, 3 conditions | WELL-SCORED path; defend it |

## STRONG CONVERGENCES (6+ seats independently)
1. **The accuracy-display gap is the #1 liability (9/9).** Web + mobile render
   "11.7%" as a clean stat while the API stamps it PROVISIONAL/not-citation, and the
   27.1% headline is dominated by the retired v1 engine (current epoch 5.0%, n=20).
   Ship the six display defects (caveat + epoch split on every surface) as one
   display-only deploy with a parity pass, BEFORE any demo. Multiple seats name it
   an App Annie exposure ("your API is honest; your screens misdescribe by
   omission" — Outsider).
2. **Socialcrawl scheduler defect (9/9):** anchor collect cycles to wall-clock slots
   (never boot phase) and LOG every slot decision — a skip must be a logged
   decision, not silence. The Statistician's framing: today the watchdog cannot
   distinguish "didn't run" from "ran and failed."
3. **Key rotations ship TODAY (7 seats):** Socialcrawl, ScrapeCreators, QUIVER, FMP
   — transcript-exposed, five minutes each, "the cheapest, most overdue item on the
   docket" (Executioner). Founder action (vendor dashboards).
4. **The Guardian-feeds contradiction must resolve THIS WEEK (7 seats):** seven
   feeds ingest against the written ban. Outsider: "if a DDQ asks 'do you ingest
   anything your own policy prohibits?' the honest answer today is yes" — REJECT as
   it stands. Executioner: dated deadline, approve-or-remove.
5. **Wave-3 Fidelity adapters = the highest-leverage build (7 seats):** build DARK
   now, in parallel with the re-arm (they don't touch the clock, they widen the
   flip's coverage disclosure). The Economist ranks it the single highest-leverage
   item in the whole review (BTC/ETH are the fat tail).
6. **Referee corroboration run on the 13 LED wins (7 seats):** 0/13 corroborated is
   the number gating whether ANY attention rate is citable. Read-only, held-out.
   Guardian: "the highest-leverage moat work in the company — above any new source."
7. **Crypto n/a: unanimous.** The absent state is CORRECT — every seat rejects
   shortcuts (no floor-lowering, no volume-as-flow, no proxy inflation). The fix is
   the sequenced chain already in flight: wave-3 adapters → A2.4 5/5 →
   Chairman-flipped CRYPTO_ETF_FLOW with coverage disclosure ("money leg measured
   for k of 12 coins, from these sources") + market-confirmation-only labeling
   while D is null. XRP stays honest no_comparator.

## UNIQUE HIGH-VALUE FINDINGS (single seats)
- **Statistician (the sharpest catch):** the served tracked-race 27.1% sits BELOW
  the random-order 50% null being served beside it, unreconciled — "a rate served
  beside a null it loses to, without comment, hands the arXiv-challenge paper its
  abstract." Also: the CI at N=48 is ~±13 points; the searched-hypothesis count
  (D9, fastlane, enrollment redesigns) is undisclosed — write the
  multiple-comparisons correction BEFORE a cohort clears a threshold.
- **Forecaster (highest-leverage process fix):** resolution queries are chosen at
  SWEEP time, not sealed at ENROLLMENT (hence 10 ambiguous-query wins). Seal
  `sweep_query` + referee query at enrollment, immutably. Also: build the
  calibration-curve/Brier layer (Detection 0–100 is a graded forecast being scored
  binary); the "breakout base rate 100%" null is degenerate — label it.
- **Executioner (verify-before-fix on X):** before touching the collector, VERIFY
  the 4,800-post ceiling actually halts pulls — if it enforces, the $437 alarm is
  early-month pacing math (recalibrate the alarm); if not, it's a live $237/mo leak.
- **Economist (tail-capture prescription):** add magnitude-weighted capture to the
  attention ledger — of the top-decile realized surges, what fraction did we
  detect, at what lead? "A 5% average that catches the giants is a business; a 27%
  average that misses them is not."
- **Expansionist:** gdelt is the platform's most-global source strangled by a
  parochial IP limit; the attention schema is already locale-free — the
  parochialism is entirely in the source roster; crypto done right is the global
  beachhead product.
- **Operator:** deploy cadence is the hidden common factor (one shipping event
  phase-shifts collectors, resets maps, has poisoned pools); the capacity question
  on the attention edge is unanswered (10× audience acting on detections CAUSES
  the breakouts the ledger scores — reflexive self-confirmation outside the
  N-exclusion's sight).
- **Guardian:** the rights overhang collides with the never-delete retention rule —
  a ledger row built on an input later removed puts the moat's permanence in
  tension with its provenance; also Dark Matter still behaves as
  late-confirmation, not early-warning — the D leg is where before-it-arrives is
  won or lost.

## DISAGREEMENTS (signal)
1. **gdelt:** Executioner: CUT/park (0 yield, nonzero surface). Expansionist: FIX
   (dedicated egress/mirror — it's the most global source we have). Others note it
   as a silent coverage hole without taking a side.
2. **On-chain crypto data:** Expansionist: fund the §16 on-chain source search as a
   NAMED workstream (the only locale-free every-coin money read — the scale
   unlock). Executioner/Economist/Operator: cut/no spend, keep the shelf triggers.
3. **Interim crypto display:** Executioner: CUT cosmetics (the absence copy already
   tells the truth). Forecaster/Expansionist/Guardian/Operator: add ONE honest
   progress/roadmap line ("money-flow source in verification: 0/5 comparisons" /
   per-coin coverage class) — absence as a resolving forecast, nothing numeric.
4. **Citability bar for the attention rate:** Statistician sets the strictest bar
   (not citable until the null reconciliation note exists), stricter than the
   caveat+split conditions of the other seats.

## THE IMPROVEMENT ANALYSIS THE CHAIRMAN ASKED FOR (per product, collated)
**TRENDS:** the citable record must become the CURRENT engine's: run the referee on
the 13 wins; seal resolution queries at enrollment; close enrollment completeness
(69.6%); ship the display caveats; reconcile the null; add tail-capture; make the
D leg genuinely early (GHOST/rising lanes) — Dark Matter is still late-confirmation.
**MARKET:** nothing to build — patience IS the finding (4/30 clean; let the
pre-declared cohort fill; verify FLOW_ENROLL self-start mid-Aug; keep R1/R2
firewalls).
**CRYPTO:** wave-3 Fidelity adapters dark now → A2.4 5/5 → Chairman flip with
coverage disclosure + market-confirmation-only labeling; on-chain question to the
Chairman (disagreement 2); XRP honest forever.

**Chairman — your decision per item.**
