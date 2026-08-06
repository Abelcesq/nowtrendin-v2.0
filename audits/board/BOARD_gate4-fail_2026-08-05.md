# BOARD REVIEW — Gate 4 first-pass FAIL, CRYPTO_ETF_FLOW flip blocked (2026-08-05 PT)

Evidence pack: `EVIDENCE_PACK_gate4-fail_2026-08-05.md`. Six independent archetype memos,
prepared in isolation (no memo saw another). Each seat read the pack AND independently
verified its claims against `etf_flow_reconcile.py`, `etf_flow.py`, `crypto_signals.py`,
and both specs. This document is a COLLATION, not a blend — memos condensed for length
only; every verdict and every named condition preserved. Decision table + disagreements
at the end. The Chairman decides.

Items: **(a)** harness join fix · **(b)** derived-leg source (FMP fails CURRENCY) ·
**(c)** flip timeline / re-arm standard · **(d)** the first-pass FAIL itself.

---

## 1. THE CHALLENGER — a: APPROVE-W-C · b: REJECT interim / A-W-C issuer · c: A-W-C · d: FAIL APPROVE, harness A-W-C

**New finding the pack missed (reframes item b):** `shares` is NOT a vendor field — we
compute it as `assetsUnderManagement ÷ nav` inside `fmp_data.etf_info` (fmp_data.py:252-263).
If FMP updates AUM and NAV asynchronously (different vintages on one pull), the quotient
FABRICATES a share change with no creation behind it. Complete mechanical explanation for
the FBTC zigzag (including a +5.2M-share "creation" dated Saturday 08-02, when nothing
settles). The derived leg's failures are not just staleness — the construction itself
manufactures phantom flow whenever the vendor's two fields desynchronize.

**(a)** Rejects the "completing the declared spec" framing: the declared artifact class is
**±1 day**; the lag re-tests that rescue rows use a **2-trading-day** lag — a rule wider
than the declaration, discovered after the FAIL, is textbook goalpost-moving unless
handled as a NEW SPEC ID. Conditions: (1) A2 pre-declared BEFORE the next scored pass;
(2) rule must be **mechanism-derived, not lag-searched** — deterministically map each
strike to the trading day whose NAV it carries (capture 00:00–06:00 UTC = prior US
session; weekend strike dates roll back), one fixed rule, no per-row lag freedom;
(3) weekend strikes folded into adjacent trading days — currently 16/34 checks INCLUDING
THE LARGEST DERIVED MOVES (08-01/08-02) are structurally never tested; (4) exclude the
still-moving latest day; (5) `etf_reconcile_log` has NO spec-version column and upserts
`ON CONFLICT DO UPDATE` — re-running under A2 silently overwrites first-pass verdicts;
add `spec_id`, make re-scores append/version; (6) re-score the ENTIRE log, not just fails.
Mind-changer: a capture-time analysis from `etf_share_observations` proving the mapping is
genuinely ±1 and deterministic.

**(b)** REJECT the "FMP + freshness proof" interim as a flip basis: freshness is necessary
but NOT sufficient — FBTC moves every day (fresh by any change test) and is wrong ~5×
cumulatively; the AUM÷NAV construction can be perfectly fresh and still fabricate flow.
Retroactive damage: §8 precondition #1 "CURRENCY PASSED 2026-08-02" rests on
`currency_report()` passing the WHOLE CLASS if any 2 of 15 funds move (etf_flow.py:262-266)
— IBIT frozen 5 days through $282M would pass it today; the currency gate must become
per-fund and accuracy-aware or #1's green is indefensible. Issuer pages: correct direction,
full 5 gates PER issuer page (iShares ≠ Fidelity — each its own source); prefer a
published shares-outstanding field over ANY AUM÷NAV derivation; state honestly that
post-swap PASSes verify PIPELINE FIDELITY, not independent measurement (Farside aggregates
issuer publications). Mind-changer on FMP: vendor proof AUM+NAV are stamped atomically from
one strike, plus 10+ consecutive in-band trading days per fund under A2.

**(c)** A1.5's literal re-arm bar ("first comparison completed inside the band") is n=1 —
near a coin flip dressed as a gate. Conditions: ALL clocks restart on source change (#2's
≥5 obs and #3's shadow sanity re-earn from zero; no FMP-era observation counts); #1 re-run
per-fund on the new source with the fixed verdict; gate-4 re-arm = **≥10 material in-band
fund-days, across ≥3 funds, spanning ≥5 distinct published trading days, zero open
failures, zero bias flags, AND ≥1 material redemption-direction day** (an all-inflow streak
proves nothing about two-sidedness — the point of this leg). F3 three stamps stand; epoch
must reflect the SOURCE identity. **The cutover trap nobody named:** `etf_share_snapshots`
has no `source` column — issuer data written into the same table makes `latest_delta`
compute an FMP-stale→issuer-true step (~+1-2% for IBIT) that sails UNDER the 20%/day
discontinuity guard and would vote. Add a source column / hard epoch cut; forbid deltas
across source boundaries. Mind-changer: a pre-registered power analysis showing a smaller
n clears a stated luck threshold.

**(d)** The FAIL: APPROVE — the cumulative test (−1,648,270 derived vs ≈−313,000
published-implied shares, ~5×) survives the harness's own strongest defense; publish it
without embarrassment. "Behaved as designed": A-W-C with four asterisks — (1) declared
smear never implemented, so part of the fail count is join artifact (the report should say
which failures are which); (2) destructive upsert + missing spec column; (3) **the
materiality floor reads `dv["aum"]` — FMP's AUM, the impugned source** — for IBIT that
moves which days get tested; floor should read AUM from the comparator or new source;
(4) `report()` grants PASS at `material_total >= 1`. Mind-changer on the FAIL: nothing
plausible (would require Farside itself proven wrong — the issuer onboarding incidentally
tests this).

---

## 2. THE FIRST-PRINCIPLES GUARDIAN — a: A-W-C (new spec id, never "completion") · b: REJECT FMP / A-W-C issuer · c: A-W-C · d: APPROVE

Axiom: the referee's rules are fixed before the match; when the referee catches us, we
never re-rule the match.

**(a)** Legitimate and necessary, but a methodology change made after data exists — a new
spec identity, NOT mere completion, for three verified reasons: the join rule itself was
never pre-declared (only the artifact CLASS); the declared artifact is ±1 day while the
rescuing lag is 2 trading days; F7's principle controls anything verdict-affecting — the
join determines which rows the floor and band even see. Conditions: A2 pre-declared in
writing from MECHANISM (capture timestamps → prior US trading date; T+1), never from the
failed rows — "if the mechanistic rule happens to match the diagnostic re-tests, good; if
not, the diagnostics lose." Recommended form: map strikes to trading dates deterministically
and compare **cumulatively between consecutive value-distinct strikes** vs the sum of
published flows over the covered interval (cures the 16/34 weekend leak where the largest
derived flows sat outside the denominator). Prior-spec log rows RETAINED AND LABELED as the
prior-spec cohort — never deleted, never counted toward A2. **Hidden drift: the ±1-day
smear is being spent twice** — once to justify the forgiving band, again to justify the
re-join. One disclosed artifact cannot excuse two independent loosenings; A2 must state
which one it pays for (recommend: the join; band stays). The fix cannot convert FAIL→PASS
(FBTC ~5× lag-corrected) — which removes the goalpost-moving suspicion and is exactly why
to do it cleanly now.

**(b)** REJECT FMP at daily flow resolution — "no fabricated data" in its most dangerous
costume: stale data wearing the measured badge (IBIT = fabricated "measured quiet" through
~$282M; FBTC not merely stale but FLAPPING — inventing flow). The 5-trading-day stale
threshold is too slow for this failure mode. Issuer pages: APPROVE-W-C — the correct
source on first principles (official, direct, primary record), full five gates, CURRENCY
run at **per-fund value-change resolution**. Farside as source: REJECT (the referee
verifying its own input = death of the harness). Interim: FMP observation-only with
per-fund-day freshness proof (frozen fund reads "no read — source stale," never 0.0) —
but freshness cannot detect flapping, and an interim under which IBIT is chronically
absent can never be flip-qualifying. **Two drifts to record:** (1) the 2026-08-02 CURRENCY
pass now stands **FALSIFIED — record it in the spec lineage**; the gate criterion must
become per-fund distinct-strike counting. (2) Moving to issuer pages quietly changes what
the reconciliation IS — source and referee share ultimate origin, so the harness degrades
from independent-source cross-check to internal-consistency check of our derivation. Still
real (catches staleness/parsing/derivation — most of what just failed), but weaker
independence that must be STATED in A2, never discovered later.

**(c)** The flip date is an output of the evidence, never an input; schedule gravity is
the hidden pressure in this file — the ~08-10 target expressly demoted from plan to hope.
(1) Shadow clocks restart on source change, unambiguously — contaminated evidence does not
carry; (2) full §16 onboarding before new-source data counts toward anything; (3) re-arm =
standing daily harness under A2 on the new source, rolling-window gate PASS with **≥5
material comparisons spanning ≥2 funds**, zero open failures, no bias flags (keeps the
Chairman's continuous-cadence ruling while fixing the `material_total >= 1` hole);
(4) F3 three-stamp flip unchanged; the pre-flip swap needs no epoch BUT needs a
**source-provenance column with deltas never computed across the seam** — a provider
switch's step offset sails under the 20%/day guard (phantom flow fabricated at the seam).
**Drift:** early PASSes on the new source will look suspiciously clean (shared origin) —
disclose in A2 that a new-source PASS is a derivation-integrity check; the bias rule and
freeze/flap detection carry the load there, not magnitude agreement.

**(d)** APPROVE — the FAIL stands; the harness earned its keep, and caught something
bigger than its assignment: precondition #1's pass and the green shadow votes were
contaminated. A blocked flip on true information is the moat working. Four defects (none
overturning; all belong in A2): the spec-to-code join gap (per-day rows are a mix of
genuine defect and artifact; the cumulative FBTC divergence and IBIT freeze are
join-independent, so the verdict survives); `material_total >= 1`; the NO_PUBLISHED bucket
absorbing the window's largest derived flows; and `snapshot_date` = capture UTC date, not
the strike's US trading date — a §14-adjacent drift the A2 mapping resolves.

---

## 3. THE EXPANSIONIST — a: A-W-C · b: REJECT FMP sole-source / APPROVE issuer · c: A-W-C · d: APPROVE

Verified independently: the exact-calendar join (line 225) vs the declared smear
(lines 12-13); the cumulative FBTC arithmetic (~5× divergence — "the pack is honest about
its own most convenient escape hatch"); the IBIT freeze isolated to FMP by the same-night
observation pulls.

**(a)** Legitimate completion BUT pre-declare as amendment A2 with a new spec SHA — F7's
letter was about constants; honor its spirit (join semantics change what counts as a
comparison); the SHA costs nothing and preserves the defensibility that is the point.
Rule: (1) **fixed, per-source declared trading-day lag** chosen once from settlement
mechanics — a per-row "nearest matching day" search is exactly the goalpost-shopping F7
forbids; (2) exclude the still-moving latest day; (3) mandatory multi-day cumulative-window
check — timezone-, calendar-, and settlement-invariant, and the check FMP still fails at
5×, so it closes the "lag fix launders a bad source" loophole. Log needs a
pass-version/spec-SHA column (first-pass FAIL must remain auditable). **Scale condition:
the lag and calendar must live PER ADAPTER in the `_SOURCES` registry** — a single ±1-day
assumption dies on the second continent (T+2 CET ETPs, Sun–Thu Gulf markets, 7-day
crypto-native venues); extend the registry promise now, while there is one entry.

**(b)** REJECT FMP-as-sole-source (frozen 4+ days through ~$282M; 5× cumulative divergence
no alignment explains; a stale source fabricating measured quiet is the worst failure class
— it wears the measured badge). APPROVE issuer-page onboarding — and it is the MORE GLOBAL
architecture, not a reluctant fallback: issuers everywhere publish shares outstanding as
regulatory disclosure; an aggregator's coverage is its US-centric roadmap. Cost stated
honestly: ~7 hand-maintained parsers that break on redesigns — accepted ON CONDITION every
adapter fails CLOSED to declared absence, never to a stale value. Interim: **the per-fund-day
value-change freshness proof (from `etf_share_observations`) should become a PERMANENT,
source-agnostic gate**, not an interim hack — at 100× instruments the silent-staleness class
scales silently and this is the only defense that scales with it. Circularity clarified for
the record: issuer-shares (source) vs Farside-flows (referee) is NOT circular — two
separately published disclosures, arithmetic-consistency checked = reconciliation, not
self-verification; Farside on both sides stays banned. Flag: the referee itself is one
UK hobbyist-grade site covering US funds only (XRP already an honest 404) — at global scale
the referee needs per-region redundancy in the same registry or `no_comparator` becomes the
dominant state of the book.

**(c)** The ~08-10 target is dead and should be declared dead. (1) Shadow-vote clock
RESTARTS on source change — evidence derived from a disqualified source is not evidence.
(2) Re-arm standard pre-declared in A2, **counted in material comparisons, not calendar
days** (quiet markets shouldn't stall the flip; low-flow non-US funds would otherwise never
re-arm): ≥5 material in-band fund-days across ≥3 funds and **≥2 coins**, zero open FAILs,
no bias flag, cumulative-window check green. Supporting code defect found: `report()` line
316 grants PASS at `material_total >= 1` — a single material comparison can green a flip
gate; fix in A2. (3) Epoch handling unchanged (swap happens pre-flip at zero cohort rows);
flip remains the F3 three-stamp atomic change with A2's SHA in the `param_version` lineage.
**Scale condition: write the re-arm standard as a REUSABLE source-agnostic template** —
this ceremony will run dozens of times (European/Asian ETPs, new comparators); a standard
requiring a board per source is a manual step that does not scale.

**(d)** APPROVE — verified in code: honest-absence states real (XRP verified-404
no_comparator; fail-closed on format change), band applied exactly as pre-declared at n=0,
bias logic correct, log idempotent, monitor continuous. The FAIL is over-determined
(direction misses AND 5× cumulative) and caught a bad source BEFORE it entered any score,
on the first live pass. **"Our own verifier blocked our own launch, here is the log" is
what diligence-grade looks like — do not let anyone frame the FAIL as an embarrassment; it
is the demo.** Legibility caveats before adapter #2 (none change the verdict): English
month parsing, `[A-Z]{3,5}` US-shaped tickers, parens-negative $M convention, USD-absolute
floors/bands need per-currency declaration, Mon–Fri no-holiday calendar is US-parochial,
and the weekend NO_PUBLISHED noise scales linearly with the roster until A2 drains it.

---

## 4. THE OUTSIDER (VC / hedge-fund banker, first look) — a: A-W-C · b: REJECT FMP / APPROVE issuer · c: A-W-C · d: APPROVE

One-sentence read for partners: "They measure where attention and money are STARTING to
move — before Google Trends or price — and grade their own predictions on a ledger they
don't let themselves edit; today their own pre-registered harness caught their data vendor
serving stale numbers, so they blocked their own launch."

**Do the numbers smell managed? No — checked by hand:** the report's totals reconcile
(2+4+12+16=34; material=6); all four FAIL verdicts re-derived from the raw tables against
the coded band and all four are correct applications of the pre-declared rule; band
constants in code match A1.6-F7 exactly; and the pack VOLUNTEERS the evidence against its
own easiest exit (the 5× cumulative test — "a team massaging numbers buries that line;
this team led with it"). Caution: never cite the 2 passes (BITB, ETHA) as anything — six
material comparisons is not a sample. This pack RAISED the prior on the rest of the shop.

**Jargon that loses a client in minute one:** strike, smear, shadow votes, gate 4, F7,
measured quiet, no_comparator, held-out, cohort. Demand a one-page client glossary before
any of this is shown externally (plain-English mappings provided in the full memo).

**Diligence digs:** (1) `currency_report()` tests whether values CHANGE, not whether they
are CORRECT — a stale-then-jumping source passes it; the §16 CURRENCY gate must never
again accept "moves" as "moves correctly." (2) The exact-date join orphaned 16/34 checks
including the biggest deltas — half the evidence never got tested. (3) Common-mode risk:
issuer-sourced shares vs Farside (issuer-aggregated flows) means "independent referee"
does not survive the source change unmodified — say so explicitly.

**(a)** APPROVE-W-C. The docstring declared the slippage and the code ignored its own
declaration (confirmed: no lag tolerance anywhere in the join); the lag re-tests show the
artifact is real and systematic; and the decisive fact is the fix does NOT rescue the
result. Conditions: new spec id anyway (cheap insurance against the one accusation that
can kill a data company); rule = relabel each strike to the trading day its NAV reflects,
compare at the T+1 settlement lag, exclude the still-moving day, add the cumulative
cross-check as a standing band term; NO scored pass until A2 is committed. **Point-blank:
"Your verifier declared the one-day slippage in writing and then didn't implement it —
who reviewed the harness before it ran, and why didn't review catch a spec-versus-code gap
in a 340-line file whose whole job is exactness?"**

**(b)** REJECT FMP for this leg (the observations table is dispositive; a stale source
FABRICATES measured quiet — worse than absence under this company's own rules; FBTC looks
like inconsistent vintages). APPROVE issuer pages, full five gates. Interim: dark
observation ONLY — freshness-proof detects staleness but cannot repair flapping (deltas
become multi-day aggregates misattributed to single days). **Point-blank: "You wrote on
July 29 that nobody had proven these share counts move at usable resolution — then marked
CURRENCY 'PASSED' on August 2 on a test that only checks whether values change. Who signed
the pass, and what stops the next gate from being graded on the same curve?"**

**(c)** APPROVE-W-C — flip stays dark until every clock restarts on the new source
(green computed from bad data is not green). Re-arm keys on EVIDENCE COUNT, not calendar
(cadence-consistent with the settled A1.5 ruling; it just refuses to arm on a sample of
one): gate PASS over the full 21-day window with **≥10 material comparisons across ≥3
funds, zero open failures, zero bias flags**, on the new source under pre-declared A2.
Log scoping, not deletion: FMP-era FAIL rows stay (house ethos) but the gate window scopes
to the new epoch — note the existing `source` column records the COMPARATOR, not the
derived leg; it needs a sibling. Three-stamp flip stands; **let the 08-10 date die
publicly — a date is not evidence.** **Point-blank: "If the new source's first three weeks
produce another FAIL, what is your pre-committed answer — written down BEFORE the data
arrives, the way you wrote down the band?"**

**(d)** APPROVE — verified: verdict logic by hand; honest-absence states in the code, not
just the pack; held-out discipline (no reconcile import anywhere near the vote path —
`_etf_flow_vote` reads only recorded snapshots); monitor continuous per spec. **As a
first-time diligence reader: this is the single best page in the room.** The modal
behavior when a founder orders a launch and the numbers wobble is to ship and reconcile
later; here a pre-registered, held-out verifier stopped a founder-ordered flip on its
first live pass, the failure was published raw including the analysis showing the
convenient fix wouldn't save it, and the vendor defect was isolated with a controlled
experiment. A functioning control environment is rarer and more valuable than any single
signal — it also means the accuracy claims elsewhere were earned under gates that bite.
The watch item: the response must always be to fix the DATA and re-earn the pass, never to
soften the TEST. **Point-blank: "When a customer-facing deadline and a red gate collide a
year from now at ten times the revenue pressure — who besides you has the authority to
hold the gate, and is that written down anywhere?"**

---

## 5. THE EXECUTIONER — a: SHIP (as A2) · b: SHIP issuer dark / CUT FMP-as-flip-basis · c: SHIP-LATER (earliest ~08-14, realistic 08-17) · d: FAIL stands + 2 hardenings

**(a) SHIP as amendment A2, pre-declared before the next scored pass.** The pack poses a
false dichotomy — implementing the smear IS completing the harness to its own spec AND the
F7-clean path is a new spec id; take the clean path, it costs one document. Recomputed the
cumulative test independently (published FBTC 07-29→08-05 ≈ −326K shares vs derived
−1,648,270): the fix CANNOT convert FAIL→PASS — "we are amending the ruler while the FAIL
stands; that is the opposite of goalpost-moving, and A2 should say so." **The exact rule
(pre-declare all five; band/floor untouched):** (1) fixed trading-day lag L=2, never
per-row best-of (per-row nearest-day always picks the friendlier day and inflates the pass
rate); (2) weekend/calendar mapping to the adjacent session (eliminates most of the 16/34
holes — currently the LARGEST deltas escape testing, which is worse than the failures it
caught); (3) rolling 5-trading-day cumulative band — the lag-invariant backstop no smear
can defeat, and the check FBTC fails at 5×; (4) exclude the latest still-moving strike
day; (5) **NEW — published-side sweep: any material published day with NO mapped derived
strike gets verdict `NO_DERIVED` and counts toward gate failure after a 2-trading-day
grace. A frozen source must read as FAILURE, not silence.** Rollback: revert commit +
re-run; lossless PROVIDED the first-pass log is archived first (mandatory).

**(b) SHIP issuer-page onboarding (dark, full §16); CUT "FMP + freshness" as a flip
basis.** Verified: IBIT's NAV not striking daily on a live fund proves the ENDPOINT is
stale by construction (NAV strikes daily). **Gate-hygiene finding for the record: the
harness's FAIL retroactively REVOKES §8 precondition #1's "CURRENCY PASSED 2026-08-02"** —
`currency_report()` tests movement, not correctness; record the revocation so the
precondition checklist can never again be read as 4-of-5 green. Onboarding: TYPE = market
positioning; ENGINE = `etf_flow.snapshot()` second-source adapter (FMP retained as
cross-check leg); FORMAT = per-issuer parsers in an adapter registry mirroring `_SOURCES`,
dates through `gate_date()`; CURRENCY+ACCESS = per-issuer daily-update confirmation,
declared UA, fail-CLOSED on format change (the harness's own posture, applied to source
adapters); TEST→LINK→DEPLOY on a live sample; score-affecting-when-flipped so
backtest-before-ship applies — **the A2 harness IS the backtest instrument: run the new
source dark through it.** Farside nuance stated plainly: issuer-shares vs Farside-flows is
two published FIELDS from the same disclosing entity checked for arithmetic consistency
through OUR pipeline — reconciliation, not independence; correct and honest, but never
claim independent confirmation. Interim: SHIP the per-fund freshness guard (NAV frozen
>1 trading session while markets open → STALE / honest absence, no vote — verify it fires
on the CURRENT IBIT freeze) but CUT it as a flip basis: freshness cures freezing, not
flapping. Rollback: adapters additive and dark; revert commit; FMP pipeline unchanged.

**(c) SHIP-LATER on this sequenced plan; ~08-10 is dead:**
1. **Now, dark — preserve evidence:** archive first-pass `etf_reconcile_log` verbatim to
   `audits/board/` (JSON; row count must match checked=34); add `rule_version` stamp to
   future writes. (The upsert otherwise silently rewrites first-pass verdicts.)
2. **Commit A2** (new SHA): join rule, re-arm numbers, source decision, the #1-revocation
   record, the Farside-nuance disclosure. Verify band/floor constants byte-identical to F7.
3. **Onboard issuer pages** per §16 as a parallel adapter (dark, record-only); ship the
   FMP freshness guard. Verify: live-sample eyeball per issuer; `gate_date()` on every
   date; both sources landing in observations; guard fires on the current IBIT freeze.
4. **Deploy the A2 harness; scored passes daily on the new source.** FMP-derived rows
   never count toward re-arm. Verify: source-tagged rows on `/diag/etf-reconcile`;
   `etf_reconcile_watch` still armed.
5. **Accumulate:** ≥5 value-distinct strikes per votable fund on the new source; shadow
   votes on `/diag/etf-flow` recomputed from it, sane (no discontinuity stamps; GBTC's
   negative baseline behaving).
6. **Pre-flip:** `test_crypto_flow_a1.py` (F5, 9 checks) green; §8 preconditions #1–#5 on
   new-source evidence ONLY; re-arm standard met: gate PASS, zero open failures, zero bias
   flags, zero un-graced NO_DERIVED, **≥5 material comparisons spanning ≥2 funds and ≥3
   distinct trading days** (setting the count now, at n=0 on the new source, is F7-clean
   and respects the A1.5 continuous-cadence ruling).
7. **Founder flips the three stamps in ONE config change** (`CRYPTO_ETF_FLOW=1` +
   `CRYPTO_LEDGER_CLEAN_COHORT_START` + `CRYPTO_SERIES_EPOCH=e1-flowleg-<date>`;
   `param_version` = A2 SHA lineage). Post-flip verify: `flow_basis`/`signal_latency_days`
   on payloads; venue-class diffusion active (6 funds ≠ coverage jump — kinds-based code
   confirmed); F1 pinned budgets folding; ledger cohort starting clean.
8. **Rollback:** unset `CRYPTO_ETF_FLOW` (flag-off = byte-identical legacy, asserted by
   F5); epoch/cohort stamps documented, not reverted; harness + monitor keep running.
   No data deletion anywhere at any step.
Timeline honestly: onboarding+deploy ~1-2 days; ≥5 strikes needs ≥5 trading sessions;
**earliest defensible flip ~08-14, realistically 08-17.**

**(d)** FAIL stands on three independent legs (pre-declared-band direction failures; the
5× cumulative divergence; the observation-proven IBIT freeze). Re-derived every verdict:
all correct, floors check out (FBTC ~$10.2B → $10M floor; HODL ~$1.06B → $10M).
**The HODL fail is a FEATURE:** derived +$0.08M through a published −$14.7M day is exactly
the "measured quiet through real flow" failure mode the gate exists to catch — do NOT add
a derived-side materiality floor in A2; it would blind the gate to frozen sources.
Passes (BITB/ETHA) = weak evidence, treat as nothing. **Two defects the pack does not
name:** (1) **derived-side-only iteration lets a frozen source escape judgment** —
`reconcile()` loops over OUR strikes, so IBIT's freeze produced NO rows for two material
published days; a source frozen from day one would read `NO_MATERIAL_DAYS_YET`, arguably
pending-green; the freshness cross-check that caught it was a manual query OUTSIDE the
harness. The `NO_DERIVED` published-side sweep closes this — **the most important fix in
this memo.** (2) The upsert erases audit history — archive first, stamp `rule_version`.
The correct reading of this FAIL: not "gate 4 needs fixing until it passes" — "gate 4
just paid for itself."

---

## 6. THE ECONOMIST — a: A-W-C · b: REJECT FMP / APPROVE issuer · c: REJECT calendar target, standard adopted · d: APPROVE — plus PRESCRIPTIONS

**(a)** APPROVE-W-C (Bernstein: pre-declaration is the whole defense; disciplined by
Taleb's narrative fallacy). Legitimate completion, not goalpost-moving, because BOTH:
the smear was declared before any comparison ran, AND the fix cannot rescue the verdict —
"an amendment adopted while it still leaves the gate at FAIL cannot be accused of being
fitted to produce a PASS." The lag story explaining 2 of 4 failures neatly is exactly the
narrative fallacy — only the side-by-side re-run proves what the amendment changed.
Conditions: mint A2 anyway (a spec SHA is cheap; an argument with hedge-fund counsel about
whether "logic" is a "constant" is not); the rule derived from mechanism: **lag fixed at
1 trading day by settlement mechanics** (T+1 + 00:00–06:00 UTC capture), weekend strikes
map to the preceding trading day, exclude the still-moving latest day, add a **rolling
5-trading-day cumulative band** (lag-invariant by construction — immune to the entire
artifact class the daily join is amended for, and the check that actually convicted FBTC);
zero scored comparisons under the new rule before the commit timestamp; **publish both
verdicts once — old-rule and new-rule side by side over the frozen first-pass data, so the
amendment's effect is measured, never narrated.**

**(b)** REJECT FMP `etf/info` as the daily-flow source (Adam Smith: a stale price is a
DISTORTED information signal — it coordinates strangers into the wrong belief; worse than
no quote). §8.1's "CURRENCY PASSED 2026-08-02" was a 4/15-funds movement verdict on a thin
window, now falsified at daily resolution — the earlier caution (the 07-29 header) was
right and the later optimism was not; Reinhart-Rogoff: the four most dangerous words were,
in effect, "the access gate passed." Issuer pages: APPROVE, full 5 gates (FORMAT matters —
scraped pages change shape; the fail-closed posture is the right model). Circularity
stated precisely: Farside-as-source = the verifier verifying itself, banned; issuer pages
as source is NOT that trap but adjacent — the reconciliation degrades from "two
independent measurements agree" to "our pipeline faithfully reproduces the issuer's
ledger"; still valuable (parse errors, staleness, splice defects), but **the harness's
`note` field should say which of the two claims it is making** (Bernstein: know what your
measurement can and cannot certify). Interim: FMP shadow-observation only with
honest-absence masking; insufficient to re-arm — a freshness test cannot catch a flapping
source, only a frozen one.

**(c)** REJECT the ~08-10 calendar target; re-arm is evidence-conditioned (Friedman &
Schwartz: a spliced series fabricates movements unless the splice is marked; Taleb:
calendar quiet proves nothing). (1) Shadow clock restarts at the source change — a track
record built on a defective instrument is not a track record (silent evidence). (2)
**Splice discipline, non-negotiable:** epoch-mark the snapshot series at the source
boundary; no Δshares ever computed across it — the splice, not the data, generates the
phantom movement; `latest_delta` and `_derived_by_date` refuse straddling pairs. (3)
Re-arm evidence counted in material comparisons: **zero material FAILs and no bias flags
across ≥10 material fund-day comparisons spanning ≥3 funds and ≥2 coins, including at
least one fund-day above $100M** — the verifier must be tested where the tails live; a
harness that has only ever passed quiet days is unproven exactly where the vote matters
(Taleb). Roughly 7–10 trading days at recent volumes, but the count binds, not the
calendar — "the big money is in the waiting." (4) F3 three-stamp stands; the epoch string
names the SOURCE lineage (e.g. `e1-flowleg-issuerpages-<date>`) so the cohort's
`param_version` records that no FMP-era row informs it.

**(d)** APPROVE (Malkiel's null honored): the gate refused to believe the derived series
until it beat a naive external check, and the derived series lost. Honest-absence states
worked; band/floor/bias logic match F7 as pre-declared; monitor continuous. The FAIL is
ROBUSTLY right — it does not depend on the defective join. Two demerits: the harness
under-implemented its own declaration (a verifier's spec-to-code gap is exactly the risk
Bernstein warns remains after you think you've measured); and once A2 lands, the 21-day
window must re-verdict superseded-rule rows or it holds the gate hostage to pre-A2
artifacts. Deepest thing proven: the harness discovered the other three greens were
painted — "a system that can discover its own greens were painted is doing the one thing
most detection systems cannot."

**PRESCRIPTIONS (each tied to canon):**
1. **Cumulative-window reconciliation as a standing band** (F&S): rolling 5- and
   20-trading-day cumulative share-delta bands inside `report()`, pre-declared in A2.
2. **Tail-weighted verification** (Taleb): track the harness's record specifically on
   top-decile |published| fund-days; judge the live leg on catching the rare huge
   creation waves, not mean hit rate.
3. **Staleness-as-null CURRENCY test** (Malkiel): per-fund, continuous, against the null
   "today = yesterday's value"; a series indistinguishable from a stale copy fails by
   construction — run it on the new source too.
4. **A distinct SOURCE_STALE alarm** (Smith): fund frozen ≥3 trading days while the
   comparator shows material flow = a dead vendor quote, categorically different from a
   divergence; separate state in `etf_reconcile_watch` so triage never conflates them.
5. **Splice registry** (R&R / F&S): a permanent registry of series splices (source, date,
   epoch string) consulted by `latest_delta`, the harness, and the ledger cohort logic;
   refuse any delta across an entry. "Every vendor migration believes its splice is
   harmless — this time is never different."
6. **Measured amendments, never narrated** (Taleb): standing rule for every verifier
   amendment — re-run old and new logic over the same frozen data, publish both verdicts.
7. **Kindleberger stage honesty:** ETF creations are the credit/attention-expansion
   channel of the regulated wrapper — the "monetary conditions" of institutional crypto
   attention; when live, serve flow beside the pre-registered momentum null and only earn
   the word "signal" past n≥30 vs Null A, exactly as the spec commits.

---

## DISAGREEMENTS (signal, not noise)

1. **Is the join fix "completion" or "methodology change"?** Economist, Executioner, and
   Outsider: legitimate completion (the smear was pre-declared; the fix can't rescue the
   verdict). Challenger and Guardian: NOT completion — the declared artifact is ±1 day and
   the rescuing lag is 2 trading days, and the join rule itself was never declared.
   **All six nonetheless converge on the same disposition: new spec id A2, pre-declared
   and committed before the next scored pass.** The disagreement is about the record's
   framing, and the Guardian/Challenger framing is the conservative one.
2. **The exact lag constant.** Economist: L=1 trading day (from T+1 mechanics).
   Executioner: L=2 (from the empirical re-tests). Challenger/Guardian/Outsider:
   no fixed L — deterministically map each strike to its trading day from `captured_at`,
   then compare (Guardian goes further: make the strike-to-strike CUMULATIVE interval the
   primary comparison, not any daily join). This is a genuine open design question for A2;
   all agree it must be derived from capture-time mechanism and fixed BEFORE the next
   scored pass, never fitted per-row.
3. **Re-arm evidence count.** ≥5 material comparisons (Guardian: ≥2 funds; Executioner:
   ≥2 funds, ≥3 trading days; Expansionist: ≥3 funds, ≥2 coins + cumulative green) vs ≥10
   (Challenger: ≥3 funds, ≥5 published days, +≥1 material REDEMPTION day; Outsider: ≥3
   funds; Economist: ≥3 funds, ≥2 coins, +≥1 fund-day >$100M). Extra required evidence
   classes differ: two-sidedness (Challenger) vs tail exposure (Economist) vs
   template-reusability (Expansionist).
4. **The FMP freshness guard's status.** Expansionist: make it a PERMANENT source-agnostic
   gate. Executioner: ship it as the honest-absence guard now. Guardian/Economist/Outsider:
   acceptable for shadow observation only. Challenger: rejects the interim framing
   entirely (freshness is necessary-not-sufficient; the AUM÷NAV construction can be fresh
   and wrong). **Unanimous within this: no flip ever re-arms on FMP share data.**
5. **Unique findings no other seat surfaced:** Challenger — `shares` is COMPUTED
   (AUM÷NAV) in `fmp_data.etf_info`, so vendor field desync fabricates flow (the FBTC
   zigzag mechanism), and the materiality floor reads the impugned FMP AUM; Executioner —
   the published-side `NO_DERIVED` sweep (a frozen source currently escapes as silence)
   and the audit-history-erasing upsert (Challenger also caught the upsert); Guardian —
   the smear "spent twice" (band + join) and `snapshot_date` ≠ trading date as §14-adjacent
   drift; Economist — SOURCE_STALE as a distinct alarm state + the permanent splice
   registry; Expansionist — per-adapter lag/calendar in `_SOURCES` + referee per-region
   redundancy; Outsider — the governance question (who besides the founder can hold the
   gate, in writing).

## DECISION TABLE

| Item | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist |
|---|---|---|---|---|---|---|
| (a) Join fix as A2, pre-declared | APPROVE-W-C (A2 mandatory; mechanism-derived; append-only log) | APPROVE-W-C (new spec id, never "completion"; cumulative-primary) | APPROVE-W-C (A2 SHA; per-adapter lag; cumulative mandatory) | APPROVE-W-C (A2 anyway; no scored pass till committed) | SHIP (as A2; 5-point rule incl. NO_DERIVED sweep) | APPROVE-W-C (A2 anyway; L=1; both verdicts published side-by-side) |
| (b) FMP → issuer pages | REJECT interim / A-W-C issuer (kill AUM÷NAV construction) | REJECT FMP / A-W-C issuer (per-fund CURRENCY; falsification recorded) | REJECT sole-source / APPROVE issuer (freshness gate permanent) | REJECT / APPROVE issuer (interim = dark observation only) | SHIP issuer dark / CUT FMP-as-flip-basis (revoke #1 pass) | REJECT / APPROVE issuer (shadow-only interim) |
| (c) Re-arm standard + timeline | A-W-C (≥10 material, ≥3 funds, ≥5 days, +redemption day; source column; clocks restart) | A-W-C (≥5 material ≥2 funds; provenance column; no cross-seam deltas) | A-W-C (≥5 material ≥3 funds ≥2 coins; reusable template) | A-W-C (≥10 material ≥3 funds; epoch-scoped log; pre-commit second-FAIL answer) | SHIP-LATER (8-step plan; ≥5 material ≥2 funds ≥3 days; earliest ~08-14) | REJECT calendar (≥10 material ≥3 funds ≥2 coins +$100M day; splice discipline) |
| (d) The first-pass FAIL | APPROVE FAIL / A-W-C harness (4 asterisks incl. FMP-AUM floor) | APPROVE (4 defects to A2) | APPROVE ("the FAIL is the demo") | APPROVE ("best page in the room") | FAIL stands (+NO_DERIVED sweep, archive-first) | APPROVE (re-verdict superseded rows post-A2) |

**Unanimous across all six seats:** the FAIL verdict stands and is publishable; the flip
stays blocked; FMP `etf/info` is dead as a flip basis (no re-arm on FMP share data,
ever); issuer product pages onboard through the FULL §16 five gates; every observation/
shadow clock restarts on the source change (the 08-02 CURRENCY pass and the green
preconditions #1–#3 are contaminated/falsified); A2 is pre-declared and committed BEFORE
the next scored pass; the first-pass log is preserved (archive/append-only — never
overwritten); the F3 three-stamp flip command is unchanged; the ~08-10 date is dead.

---

**Chairman — your decision per item:**
- **(a)** the A2 join rule (and WHICH matching mechanism: fixed L=1, fixed L=2,
  deterministic strike→trading-day mapping, or Guardian's cumulative-primary), with the
  log hardenings (spec/rule-version column, archive-first, append-only);
- **(b)** the derived-leg source ruling (issuer-page onboarding; FMP's interim status:
  shadow-only vs permanent freshness gate; whether to kill the AUM÷NAV construction in
  favor of a published shares field; formally recording the CURRENCY-pass revocation);
- **(c)** the re-arm standard's numbers (5 vs 10 material comparisons; funds/coins/days
  spans; the Challenger's redemption-day and the Economist's $100M-tail-day requirements;
  the source-provenance column / splice rule; the timeline);
- **(d)** acceptance of the first-pass FAIL record + which harness hardenings ship in A2
  (NO_DERIVED sweep, comparator-side floor, SOURCE_STALE alarm, re-verdict of superseded
  rows, material_total threshold).
