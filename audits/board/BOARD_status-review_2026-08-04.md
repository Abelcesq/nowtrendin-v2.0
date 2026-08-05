# ADVISORY BOARD — STATUS REVIEW + RECENT UPDATES
**Convened:** 2026-08-04 · **Six archetypes, fully independent** (parallel agents, no memo saw another)
**Evidence pack:** `EVIDENCE_PACK_status_2026-08-04.md` · Every archetype independently verified the
pack against the actual code (insider_flow / etf_flow / crypto_signals / flow_enrollment /
flow_ledger / crypto_money_gradient / the spec) before writing.

**Items:** U1 INSIDER_FLOW live · U2 liveness false-RED fix · U3 crypto ETF share-flow Stage 1
dark · U4 steady-state items · F1 FLOW_ENROLL flip · F2 CRYPTO_ETF_FLOW flip (~Aug 10) · §5
outstanding-work prioritization.

---

## VERDICT TABLE

| Item | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist |
|---|---|---|---|---|---|---|
| U1 insider panel live | AWC | APPROVE | APPROVE | APPROVE | SHIP | APPROVE |
| U2 false-RED fix | AWC | APPROVE | APPROVE | APPROVE | SHIP (1 gap) | APPROVE |
| U3 crypto flow Stage 1 | AWC | APPROVE | APPROVE | APPROVE | SHIP | APPROVE |
| U4 steady-state | APPROVE | APPROVE | APPROVE | APPROVE | SHIP | APPROVE |
| F1 FLOW_ENROLL | AWC (**harder conditions**) | AWC | AWC | AWC | SHIP-LATER (days) | AWC |
| F2 CRYPTO_ETF_FLOW ~Aug 10 | **REJECT** | **REJECT** | AWC (gates, not date) | **REJECT** (as scheduled) | SHIP-LATER (hard block) | **REJECT** (as of today) |

AWC = approve-with-conditions. **F2 is effectively unanimous: do not flip on the calendar — three
of six pre-declared spec §8 gates (reconciliation harness, venue_diffusion freeze, latency stamps)
do not exist yet. Every memo gave the same re-approval path: build the gates, then flip whenever
that is.** Executioner + Challenger independently verified venue_diffusion is a LIVE 0.25-weight
component of crypto Market Confirmation — the freeze is score integrity, not paperwork.

---

## THE MEMOS (faithful, condensed)

### 1. THE CHALLENGER (accuracy attacks; deepest code verification — 21 tool uses)

**Provenance defect on the pack itself:** header says "verified LIVE 2026-08-04 UTC 02:00–02:40,"
but the U2 commit is authored 2026-08-05 02:19 UTC and the code comment says "first observed
2026-08-05" — local date stamped onto a UTC claim. Internally impossible timestamp; the first
thing opposing counsel reads aloud. Fix the stamps.

- **U1 AWC — strongest attack: actor-identity fragmentation can fabricate the enrollment trigger.**
  `actor_id()` hashes the exact lowercased name string; nothing normalizes variants ("John Smith" /
  "John A. Smith" / "SMITH JOHN A" = three buyers). The F1 qualifier counts DISTINCT hashes ≥3 —
  two real buyers + one respelling = a qualifying cluster. Same defect class B4 killed, one layer
  down. Also: the ~200-row source cap is watermarked but the qualifier never consults it.
  *Evidence to change mind:* duplicate-name audit over the 397-event panel (normalized grouping,
  zero 2→3 boundary crossings) + evidence Finviz owner strings are byte-stable.
- **U2 AWC — three attacks:** (1) "regression proven both directions" is NOT in the repo — f1e97af
  changed no tests; the proof ran once in a session. Must be a committed, re-runnable self-test.
  (2) The fix counts survivors of ALL gates (materiality, dates), not parse survivors — a live feed
  dominated by sub-$100K rows still reads <8 → the false-RED class recurs in a new costume; and the
  watermark now permanently disagrees with collector_health's denominator (81 raw-parsed vs
  survived-gates). (3) `insider_coverage.distinct_tickers` changed meaning mid-series with no
  version marker — a future auditor reads the 61→4→4 era as a real collapse.
- **U3 AWC — strongest attack: "measured-quiet" is not proven measured.** Shares are derived from
  FMP AUM÷NAV; `snapshot()` records nothing about FMP's own as-of. If FMP serves a stale field 3
  days, we write 3 "fresh" identical snapshots and vote 0.0 "measured quiet" — D1/D2's forbidden
  move recommitted one level down. Mirror image: async AUM/NAV refresh makes the quotient wiggle
  with price — the banned circularity leaking back as noise; the CURRENCY criterion (|Δ|>0.01%,
  ≥2 movers) is weak enough to pass on that artifact. FBTC already pins the vote cap (−1.47%/day vs
  1.0% scale) — the Board's own bridge-constant finding confirmed. *Evidence:* the reconciliation
  harness (≥5 days, pre-stated tolerance) + store FMP lastUpdated per snapshot + an intraday
  double-pull showing share count stable while price moves.
- **U4 APPROVE** — spot-checks passed; honest denominators real. Attack: blended 11.7 is published
  with ledCorroborated=0; the `hitRateProvisional` stamp only defends if EVERY surface rendering
  the rate renders the stamp (3-platform render check).
- **F1 AWC — conditions load-bearing; do NOT flip on the pack's trigger.** Left-censored
  qualification window: prereg window is 10 sessions, panel is 3–4 days old. Controls "with no
  qualifying disclosure of their own in the window" pass on unverifiable cleanliness; first-era
  rows are measured under different information conditions under the SAME prereg SHA. "One clean
  GREEN ingest" tests plumbing, not window sufficiency. *Conditions (any one):* (a) hold flip until
  the panel spans the full 10-session window (~Aug 14), or (b) code a window floor —
  qualification refuses until `window_start >= panel_start`, or (c) stamp first-era rows a
  left-censored sub-cohort excluded from published rates. Plus the U1 fragmentation audit clean.
- **F2 REJECT** — gates 4/5/6 don't exist; gate 4 is the only thing standing between "11/15 show
  real movement" and "11/15 show FMP artifacts." The date is the defect, not the build.
- **§5 order:** 1 referee corroboration (the ON number with zero backing) · 2 reconciliation
  harness · 3 venue freeze · 4 latency stamps · 5 S6 census · 6 topic_maturity coverage-0 (biases
  the enrollment cohort) · 7 D9 · 8 topic_current · 9 COT/13F (behind gates — "new legs before
  existing gates close is how the insider path shipped") · 10 S8 · 11 ops.

### 2. FIRST-PRINCIPLES GUARDIAN (moat + ledger)

- **U1 APPROVE** — append-only panel accruing while enrollment stays closed is the purest form of
  the moat; prereg locked before data could tempt the terms. No drift.
- **U2 APPROVE** — alarm honesty in both directions; the fewer-alarms direction always deserves
  suspicion, so verified: dead-parser path still fires. §10a honored. Nit: comment date 08-05 vs
  pack 08-04 — in a shop whose product is time-stamps, fix the comment.
- **U3 APPROVE** — shares=AUM÷NAV divides the price out; spec SHA-committed pre-flip; quantization
  funds barred; 7 coins honest-structural. Invariant to state: shadow votes must remain provably
  non-serving while the flag is 0.
- **U4 APPROVE** — honesty compounding (17 dead cycles kept in the denominator; dead-parser era
  quarantined with affects_prior_reads).
- **F1 AWC** — first principles favor flipping PROMPTLY once liveness is trustworthy: every day
  enrollment stays dark after gates are green is detection history NOT being time-stamped, and you
  cannot backdate it later. Conditions: clean GREEN ingest OBSERVED (not projected — the pack was
  written before it existed); RED clears by real ingest, never manual reset; term_drift [] re-read
  at flip time; success check verified post-flip with willingness to close enrollment if controls
  don't materialize.
- **F2 REJECT as of today** — a pre-registered spec is a promise made so it cannot be renegotiated
  when the data looks tempting. Gate 4 = accuracy-above-all; gate 5 = score inflation by roster;
  gate 6 = never claim lead you don't have. "~Aug 10" is calendar-driven drift: if the harness
  lands Aug 6, flip Aug 6; if Aug 20, flip Aug 20.
- **§5 order:** 1 referee corroboration (nothing outranks proving your flagship number) · 2
  reconciliation harness · 3 venue freeze · 4 latency stamps · 5 S6 census · 6 topic_maturity
  coverage-0 (could be silently distorting scores today) · 7 key rotations (immediately regardless
  of rank) · 8 topic_current · 9 D9 (until restarted, no prior D9 output may be cited) · 10 COT/13F
  · 11 S8 · 12 trims (confirm nothing in the frozen DB is ledger history before deletion).
- **System-wide:** the period's pattern is right (pre-register → dark → accrue → verify → founder
  flips). Both drift risks are calendar-shaped. Dates are not evidence.

### 3. THE EXPANSIONIST (global scale)

Standing observation: the whole Money Gradient stack reads one jurisdiction (US regulatory
artifacts) — not a defect today, it is the roadmap; the architectures generalize even where first
instances are parochial.

- **U1 APPROVE** — every major market has a Form-4 analog (UK/EU MAR PDMR, Canada SEDI, Japan).
  **Structural ask: add a jurisdiction/market column NOW, defaulted 'US', while the panel is 397
  rows old** — retrofitting an append-only panel after a year is the migration you never run.
- **U2 APPROVE** — most scale-important small item: at 100–200 sources, false-REDs teach ops to
  ignore the fleet. Extract the corrected semantics into a shared liveness contract every future
  collector inherits — the defect existed because the logic was bespoke.
- **U3 APPROVE** — best-designed item: roster derived from config; **shares-flow is
  currency-invariant** (works unmodified on EUR/CHF ETPs). The 7 "structural" coins are only
  structurally absent IN THE US — 21Shares/WisdomTree/CoinShares run spot ETPs on Xetra/SIX/
  Euronext covering SOL, DOT, ADA, AVAX, LINK, LTC today: the natural first internationalization
  beachhead when the $0 directive lifts. Keep copy saying "no US spot fund," never "no spot fund."
- **U4 APPROVE** — keep buy/sell comparisons currency-normalized the day a second jurisdiction lands.
- **F1 AWC** — conditions: the clean-ingest gate + stamp market/jurisdiction on enrollment rows
  from row one. The prereg design (clinical-trial idiom) is the most sellable methodological
  artifact the platform will own; keep the runbook-per-flip pattern mandatory.
- **F2 AWC — flip on gate completion, never the calendar.** The two unbuilt gates are the two most
  scale-critical builds in the pack: the venue freeze is the generic cold-start guard EVERY future
  universe expansion needs (build it generic, not crypto-special); the reconciliation harness is
  the external-truth check diligence asks for by name (design per-issuer adapters — European
  issuers publish flows in different formats/currencies).
- **§5 order:** 1 venue freeze (generic) · 2 reconciliation harness · 3 latency stamps · 4
  topic_current (the literal 100×-breakage class) · 5 referee corroboration (no global sales deck
  carries a provisional rate) · 6 S6 census · 7 COT/13F (deepen US, don't broaden — fine) · 8 S8
  (prewarm > plain-English relabel [jargon is its own parochialism] > momentum > naming) · 9
  maturity/D9 · 10 ops.

### 4. THE OUTSIDER (VC / hedge-fund banker, first look)

One-sentence: "An early-warning instrument that watches where attention and institutional money
are STARTING to move — news breadth, niche sources, insider Form-4 buying, ETF share creations —
scores each topic or ticker before the move shows up in Google Trends or price, and keeps a
locked, tamper-evident scorecard of whether each call was actually early."

Overall: "I came in expecting managed numbers. I found the opposite problem: the numbers are so
honestly handled they're almost unsellable today… nobody fakes numbers this bad. That is
diligence-positive." The risk is TIMING: honest denominators fill slowly (365-day patience, 1,134
pending) — the company could run out of story before the ledger earns its first defensible
headline. And the vocabulary (Dark Matter, catch-all, LED, prewarm, N, Gradient Score) loses a
client in five minutes — **the plain-English relabel is a revenue item, not cosmetic.**

- **U1 APPROVE.** Point-blank: "At ≥3 buyers/10 sessions, how many qualifying clusters does 3 days
  of accrual project per month — what calendar date do you hit 30 resolved episodes? If 'next
  summer,' what do you show a paying client meanwhile?"
- **U2 APPROVE.** Point-blank: "This is the SECOND insert-vs-parse counting defect (flow_ledger
  .enroll had the same shape). Have you swept every liveness/coverage monitor for the pattern, or
  are we finding them one false alarm at a time?"
- **U3 APPROVE** — best document in the pack; pre-registers the exact objection I'd raise (flows
  chase momentum). Point-blank: "Who owns the ≥30-day per-fund null study, what date is it on the
  calendar, and what stops the bridge constants from quietly becoming permanent?"
- **U4 APPROVE.** Point-blank: "Confirm no figure anywhere — including cached pages and old
  screenshots in decks — still includes the contaminated dead-parser era."
- **F1 AWC** — conditions as proposed + written verification of the success check within days.
  Point-blank: "Walk me through control selection, and how you'd answer a fund's quant who asks
  whether controls were picked after seeing the treated names."
- **F2 REJECT as scheduled** — "a pre-declared spec that bends to a target date is worth nothing
  in diligence; one that moves the date is worth a lot." Point-blank: "Does Aug 10 move, or do the
  gates? And when the harness disagrees with an issuer beyond rounding, which number wins?"
- **§5 order:** 1 F2 gate work (harness → freeze → stamps) · 2 key rotation (the one item that can
  hurt you TODAY; there is prior leak history) · 3 referee corroboration (until then the moat is a
  claim, not evidence) · 4 S6 census · 5 **pull plain-English relabel + N naming FORWARD out of S8**
  · 6 COT/13F · 7 topic_current + maturity · 8 momentum (own backtest) · 9 D9 · 10 trims (decide in
  one sitting, stop carrying it on lists).

### 5. THE EXECUTIONER (delivery + sequencing; verified flag-gating in code)

- **U1 SHIP** (live; keep live). Verified flag-gates, rowcount-counted inserts, salt refusal;
  FLOW_ENROLL independently 0. Cleanest rollback surface in the pack (unset flag; panel retained).
  Ongoing verify: liveness OK daily; panel monotone accrual; FLOW_ENROLL still 0 until F1 fired.
- **U2 SHIP, one gap:** "regression proven both directions" is proven by code structure + a
  synthetic coverage-row insert, but **no committed self-test runs an actual all-duplicate
  re-ingest and asserts the coverage row equals full survivor count** — the exact path that broke.
  Cheap; add it. Do not mark U2 done until the first post-v309 ingest clears the stored RED live.
  Fix the 08-05 comment date. Rollback safe (fail-noisy direction).
- **U3 SHIP** — dark deploy correct: flag defaults 0, vote path gated, circularity ban structural,
  stale/discontinuity guards in. While dark: daily /diag/etf-flow (zero discontinuity stamps, GBTC
  measured-not-pinned); snapshot idempotency; grep served payloads for zero etf-flow refs.
- **U4 SHIP** — commit log corroborates; covered by weekly run_all.
- **F1 SHIP-LATER (days, not weeks).** Machinery verified: refuses without prereg, HALTs on term
  drift, deterministic seeded controls, atomic enroll. Conditions: (1) one clean GREEN ingest
  observed; (2) at flip: prereg active, drift [], flag currently 0; (3) first cycle: success check
  verified, **halt if strata come back null** (the known D-round failure shape). Rollback genuine
  (flag off; enrolled rows stay — correct, enrolled under prereg). **Sequence: F1 before F2.**
- **F2 SHIP-LATER (hard block).** Gates 1–3 pass (11/15-moving vs 4/15-at-verdict is consistent
  accrual, not contradiction). Gates 4/5/6 unbuilt. **Verified: venue_diffusion is a live
  0.25-weight component of crypto Market Confirmation** — flipping unfrozen = score inflation by
  plumbing. Sequence to make the flip real: (1) freeze + latency stamps in ONE change, test dark;
  (2) harness, run ≥2 consecutive days vs issuers pre-flip — disagreement beyond tolerance moves
  the date, no exceptions; (3) flip + cohort stamp in the SAME config change (spec §8.6); (4)
  post-flip: shadow-vs-live parity first cycle; 7 coins still structural; lead 0–1 never "early."
- **§5 ship order:** 1 key rotations (30 min, today) · 2 S6 census (permanently-yellow monitors
  train people to ignore yellow) · 3 **F1 flip** (starts a calendar clock — start it early) · 4
  freeze+stamps (one PR, dark) · 5 harness → F2 flip if it passes · 6 referee corroboration
  (highest-value non-flip item) · 7 COT/13F (don't let free-but-new queue-jump flip gates) · 8
  falsered leftovers (D9 after F1 data accrues — it needs the panel anyway) · 9 founder $ decisions
  (put a decision date on the Chairman's desk, stop carrying in the build list).
- **CUTS:** S8 signed momentum — out of this cycle entirely (score-affecting changes and flag
  flips must not share a deploy window: when a number moves you must know which change moved it).
  S8 prewarm + relabel — out of this cycle. "N" naming — off the engineering queue until ruled.

### 6. THE ECONOMIST (founder's canon)

Preliminary: the two ledgers withholding rates under n≥30, and 17 dead cycles kept in the
completeness denominator forever, are "the most economically literate facts in this pack" —
Reinhart & Rogoff is a catalogue of institutions that quietly dropped their bad years; you did not.

- **U1 APPROVE** (Friedman & Schwartz: a series cannot be backfilled; every day the panel wasn't
  accruing was history destroyed at the source; hash-before-data is Malkiel done properly).
- **U2 APPROVE** (Bernstein: instrument-error, not data error — the watermark measured "novelty"
  when the alarm's question was "is the parser alive." Verified quiet wasn't bought by blinding
  the alarm. The masked first-ingest is textbook silent evidence: a test that passes on an empty
  panel has tested nothing).
- **U3 APPROVE** (Smith: engagement prices can be distorted; QUANTITIES are harder to fake. AUM
  would smuggle the coin's price back into a signal meant to predict it).
- **U4 APPROVE** (Belsky/Gilovich/Zweig: the builders' biases are the second failure mode; nothing
  here inflates).
- **F1 AWC** (Malkiel: the null-hypothesis machine being switched on). Conditions: clean GREEN
  ingest; first-week success-check verification — if controls fail to match, STOP and diagnose,
  never loosen the matcher; **no interim peeking at outcome direction** — the hash protects you
  from the data only if you also protect the data from yourselves.
- **F2 REJECT as of today** (Malkiel + Bernstein): flipping without the harness is believing a
  signal never asked to beat reality; the venue jump is a manufactured Kindleberger
  "credit-expansion" phase-signal with no human behavior behind it. **Pre-declare the
  reconciliation tolerance band BEFORE running the comparison** — decide what discrepancy you'll
  accept while still ignorant. Then approval is unconditional.
- **PRESCRIPTIONS (top methods, source-tied):**
  1. **Tail-weighted ledger reporting** (Taleb): report capture rate on the top decile of realized
     surges by magnitude — "of the N largest attention events, how many did we catch, with what
     lead?" A blended 11.7% is Extremistan-blind. Measurement-only, data already in the ledger.
  2. **Silent-evidence audit** (Taleb): quarterly, sample external breakouts that never entered
     the pending pool at all; classify why (never collected / under floor / fragment-rejected).
     The graveyard of never-enrolled topics is where the real miss rate hides.
  3. **Naive-baseline twins** (Malkiel): pair the tracked-race rate with a mechanical baseline run
     through the identical sweep; publish signal-minus-baseline.
  4. **Attention-vs-flow divergence detector** (Kindleberger): the canonical pre-crash signature
     is attention still expanding while informed flow reverses — both axes now exist in-house.
     Held-out first, own ledger, measured flag never advice. "The single highest-value new
     instrument the current data supports at $0."
  5. **Pre-declared tolerance bands as house rule** (Bernstein): every future harness/referee/
     backtest states its pass band ex ante.
  6. **Intake liveness alarms for every ledger** (Friedman & Schwartz): the July dead era cost 17
     cycles of the one asset competitors cannot replicate; gaps in the series never heal.
  7. **Quantities-over-prices doctrine** (Smith): write "extract the quantity from quantity×price"
     into §16 FORMAT (stablecoin Δtokens, COT contracts) so the next builder inherits the rule.
  8. **A peeking log** (Zweig): append-only record of every read of an in-flight preregistered
     outcome — converts "we didn't data-mine" from assertion to record.
- **§5 order:** 1 harness · 2 referee corroboration · 3 venue freeze · 4 latency stamps · 5 S6
  census · 6 key rotation · 7 COT/13F (series value compounds — start soon, believe later) · 8
  falsered leftovers · 9 S8 · 10 trims.

---

## DISAGREEMENTS (signal, not noise)

1. **F1 flip timing — the sharpest split on the board.** Five archetypes: flip within days once
   one clean GREEN ingest is observed (Guardian: waiting has an integrity COST — undated detections
   can't be backdated; Executioner: the flip starts a calendar clock, start it early). The
   **Challenger alone** says that trigger tests plumbing, not window sufficiency — the 10-session
   qualification window is left-censored over a 3–4-day panel (controls pass on unverifiable
   cleanliness) — and demands one of: hold to ~Aug 14, code a window floor
   (`window_start >= panel_start`), or stamp first-era rows a left-censored sub-cohort.
2. **What goes first in §5.** Referee corroboration first (Challenger, Guardian); reconciliation
   harness first (Economist, Outsider-adjacent); venue freeze first (Expansionist); key rotation +
   S6 census first as same-day hygiene, then the F1 flip itself third (Executioner). No archetype
   put COT/13F, S8, or the trims anywhere but the tail.
3. **S8 plain-English relabel:** Outsider pulls it FORWARD (a revenue item — the vocabulary loses
   clients); Executioner CUTS it from this cycle (no flip depends on it). Both agree signed
   momentum stays out of the flip window.
4. **U2 severity:** Guardian/Economist/Outsider/Expansionist approve clean; Challenger +
   Executioner both independently found the committed-regression-test gap ("proven" ran once in a
   session, nothing in the repo re-runs it), and the Challenger adds the unstamped semantic break
   in the stored `insider_coverage` series + the survivors-of-which-gates denominator question.
5. **U1:** only the Challenger attacks the name-variant fragmentation of the 3-buyer trigger; only
   the Expansionist demands the jurisdiction column before history accrues. Neither contradicts
   the other — both are pre-F1/pre-scale hardening asks on an item everyone approves.

## CONSENSUS WORTH RECORDING (arrived at independently six times)

- **F2 does not flip on a date.** Build gates 4/5/6; the flip date is whenever the last gate
  closes, verified. (6/6.)
- The pack's honesty (withheld rates, dead cycles in denominators, quarantined eras) is the
  product's strongest asset — and the referee corroboration is the debt on the one number
  currently published (11.7 provisional, ledCorroborated=0). (5/6 ranked it top-3 in §5.)
- The date-stamp discrepancy (08-04 pack vs 08-05 UTC commit/comment) was independently flagged by
  four archetypes. Fix the stamps; a provenance shop cannot carry an internally impossible date.

---

**Chairman — your decision per item:** U1 conditions (fragmentation audit · jurisdiction column) ·
U2 conditions (committed regression test · coverage-series epoch marker · denominator definition) ·
U3 conditions (FMP as-of capture · the ≥30-day null study ownership/date) · F1 (flip trigger: the
five-archetype clean-ingest bar vs the Challenger's window-floor/censor-stamp) · F2 (gate-driven
flip; pre-declared reconciliation tolerance) · §5 order (the four orderings above) · the
Executioner's S8 cuts vs the Outsider's relabel pull-forward · the Economist's prescriptions
(each is its own flag-never-force proposal).
