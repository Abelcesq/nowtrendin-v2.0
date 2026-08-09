# CRYPTO FLOW SPEC — AMENDMENT A2 (Chairman-ruled 2026-08-05 PT, late)

Pre-declared and committed BEFORE any A2-scored reconciliation pass runs. Amends
`CRYPTO_FLOW_SPEC_v1_2026-08-02.md` + `CRYPTO_FLOW_SPEC_A1_AMENDMENT_2026-08-05.md`.
Board basis: `BOARD_gate4-fail_2026-08-05.md` (six memos). Chairman rulings verbatim in
§A2.0. FLOOR/BAND constants (F7) are UNTOUCHED — byte-identical to A1.6-F7.

## A2.0 — CHAIRMAN'S RULINGS (2026-08-05 PT) + the development-phase statement

Rulings, in the Chairman's words (condensed faithfully):
- **(a)** "Yes, it should be fixed... proceed with A2 amendment. We can keep old verdicts
  and stamp the new verdict with a date stamp of the day and time of the revised updated
  verdict per the [A2] amendment."
- **(b)** "If FMP is not proving to be an accurate source of data then we need to replace
  it with the CoinGecko or CoinMarketCap API. I agree to get the daily shares from the
  funds directly. We can keep [FMP] pulling silently for comparison and re-evaluate in
  30 days whether to drop completely."
- **(c)** "Let's go with 5 comparisons."
- **(d)** "Accept the fail and implement #1 and #2" (= the NO_DERIVED published-side
  sweep + the history-keeping verdict log).

**THE DEVELOPMENT-PHASE STATEMENT (Chairman-ordered; the Board is directed to
understand and adopt this framing):** the entire application is in DEVELOPMENT phase.
Verifying and updating the system BEFORE taking it to the public is exactly what this
phase is for. There is no "manipulation" in amending a verifier found defective in
development — this is correcting errors to ensure accuracy. The board's
goalpost-moving concern is honored through the mechanics below (pre-declaration, new
spec id, preserved first-pass record) — not by refusing to fix known defects. All
future board reviews shall weigh findings in this development-phase context: the
standard is "did we find and fix it before the public ever saw it," and on Gate 4 the
answer was yes.

## A2.1 — The join rule (mechanism-derived; supersedes the exact-calendar-date join)

The A1.5 harness joined derived Δshares to the published flow of the SAME calendar date.
That was never the declared intent (the ±1-day UTC smear was a declared artifact class)
and is now proven wrong by capture-time mechanics. The A2 rule, derived from mechanism
(capture instants + T+1 settlement), fixed BEFORE any A2-scored pass, no per-row freedom:

1. **Effective settled-through trade date T(strike):** convert `captured_at` (UTC) to US
   Eastern; if the ET time is before 06:00, the effective ET date is the PRIOR calendar
   day; T(strike) = the previous US trading day of the effective ET date. (Mechanics: a
   count captured evening-ET on day D reflects creations/redemptions TRADED through D−1,
   settled T+1 and published to the count during D.) Weekend/holiday effective dates roll
   back to the last trading day. This is one deterministic function of the capture
   instant — never a per-row "nearest matching day" search.
2. **Interval (cumulative-primary) comparison:** for each pair of consecutive
   VALUE-DISTINCT strikes a→b of a fund, derived flow = Δshares(a→b) × NAV(b), covering
   published TRADE dates in the interval (T(a), T(b)]. Compare derived vs the SUM of the
   issuer-published flows over that interval. This is lag-invariant within the interval
   and drains the 16/34 weekend NO_PUBLISHED leak (weekend-dated strikes now fold into
   trading-day intervals). Materiality floor and band per F7, applied to the published
   SUM, unchanged: floor max($10M, 0.05% AUM); direction mandatory on material
   intervals; magnitude ±25% or ±$20M; ≥5 consecutive same-sign errors fail in-band.
3. **Still-moving edge:** the interval ending at a fund's LATEST strike is recorded
   `PENDING_FINAL` and not scored until a later strike (or a later same-value capture
   confirming finality) exists. The comparator's most recent published day is likewise
   not scored until a subsequent published row exists (issuer numbers post over the
   evening).
4. **NO_DERIVED sweep (d#1, Executioner):** any MATERIAL published trading day that is
   covered by NO derived interval after a grace of 2 trading days (settlement + capture
   latency) is logged verdict `NO_DERIVED` and counts toward gate failure. A frozen
   source reads as FAILURE, never as silence.

## A2.2 — Verdict log (d#2 + ruling a)

- The first-pass log is FROZEN: `etf_reconcile_log` receives no further writes; its 34
  rows are archived verbatim in `ETF_RECONCILE_FIRSTPASS_LOG_2026-08-05.json`
  (2 PASS / 4 FAIL / 12 IMMATERIAL / 16 NO_PUBLISHED; gate FAIL). Old verdicts are KEPT.
- A2 verdicts write to a new table `etf_reconcile_log2` keyed
  (interval_end_date, ticker, rule_version), each row stamped `rule_version='A2'` and
  `verdict_at` = the full date+time of the (re)computed verdict, per the Chairman's
  ruling. Re-computation within A2 updates the row and refreshes `verdict_at`; a future
  rule change writes NEW rows under its own rule_version — cross-rule history is never
  overwritten.
- `/diag/etf-reconcile` + the `etf_reconcile_watch` monitor read A2 rows; the first-pass
  record remains readable for audit.

## A2.3 — Derived-leg source (ruling b)

- **Primary source: the issuers' own product pages** (daily shares outstanding —
  official, direct, §15-compliant). Full §16 five-gate onboarding PER issuer page;
  TEST-first survey in `audits/source-onboarding/` before any adapter is wired. Adapters
  fail CLOSED to declared absence, never to a stale value.
- **FMP `etf/info` is disqualified as a flip basis** (frozen IBIT ≥4 days through ~$282M
  of published inflow; FBTC flapping; and `shares` is COMPUTED as AUM÷NAV — vendor field
  desync fabricates flow). FMP keeps pulling SILENTLY for comparison; **re-evaluation
  2026-09-05 (30 days)** on whether to drop it completely.
- **The §8.1 "CURRENCY PASSED 2026-08-02" verdict is formally REVOKED** for this source:
  `currency_report()` tested movement, not correctness. The precondition re-earns on the
  issuer-page source.
- **Where FMP is proven inaccurate elsewhere, CoinGecko/CoinMarketCap replace it** (per
  the Chairman): first case = `supply_facts` circulating supply (display-only C1/C2 —
  our served BTC supply is ~94k coins / ~7 months of issuance below CoinGecko's;
  verify-before-fix on the exact mechanism precedes the code change). CG/CMC additionally
  onboard as the held-out PRICE/SUPPLY REFEREE with divergence + staleness alarms
  (`COINGECKO_CMC_KEYLESS_REVIEW_2026-08-05.md` — approved). Volume is NEVER flow
  (C5/C6 prohibition stands).
- **Source provenance + splice rule:** `etf_share_snapshots`/`etf_share_observations`
  gain a `src` column; Δshares is NEVER computed across a source seam (a cutover step
  otherwise fabricates one phantom flow under the 20%/day guard). Cross-source disagreement
  is logged, never averaged.

## A2.4 — Re-arm standard (ruling c: 5 comparisons)

`CRYPTO_ETF_FLOW=1` re-arms ONLY when, on the ISSUER-PAGE source under the A2 rule:
- ≥ **5 material in-band interval comparisons**, spanning ≥2 funds and ≥3 distinct
  trading days, with **zero open FAILs, zero bias flags, zero un-graced NO_DERIVED**
  in the rolling 21-day window (the Chairman selected the 5-comparison standard; the
  proposed redemption-day and $100M-day extras were NOT adopted);
- every observation/shadow clock RESTARTED on the new source (§8 preconditions #1–#3
  re-earned per fund; no FMP-era row counts toward any gate);
- `test_crypto_flow_a1.py` green.
The flip remains the F3 three-stamp atomic config change: `CRYPTO_ETF_FLOW=1` +
`CRYPTO_LEDGER_CLEAN_COHORT_START=<flip date>` + `CRYPTO_SERIES_EPOCH=e1-flowleg-issuer-<date>`
(epoch names the SOURCE lineage). The ~08-10 calendar target is void; the gate binds on
evidence count, not dates (realistic earliest ~08-14–17).

## A2.5 — Explicitly NOT adopted (for the record)

- The redemption-day and >$100M-tail-day re-arm extras (Challenger/Economist) — noted as
  future candidates, not required for this flip.
- The comparator-side materiality floor (d#4), the SOURCE_STALE distinct alarm state
  (d#5) beyond the CG/CMC referee alarms, and the `material_total >= 1` report threshold
  change (d#3) — the re-arm check (A2.4) supersedes the report threshold for flip
  purposes; report() semantics otherwise unchanged this amendment.
- Farside remains REFEREE ONLY. Post-swap PASSes are pipeline-fidelity evidence, not
  independent confirmation, and shall be described as such (Guardian/Economist/Outsider
  disclosure condition — adopted as a wording rule).

---

# ANNEX A2-N1 (2026-08-09) — post-swap rules, pre-declared and board-reviewed

Basis: `BOARD_a2-fix_2026-08-08.md` (six memos, unanimous approve/ratify) +
Chairman approval to implement ("go ahead and implement fixes", 2026-08-09). This
annex records rules that previously lived only in code comments, and pre-declares
the decisions with future effective dates. Nothing here alters F7 floor/band, any
verdict semantics, or the A2.4 evidence standard.

## N1.1 — NO_DERIVED era attribution (formalizing the 2026-08-08 fix; Guardian C-2)

A material published trading day with no derived coverage is blamed on **the source
whose strike ERA covered that day** — never on the latest source. Era boundaries
fall at `t_of(first strike of each src run)`, in strike order; ownership transfers
STRICTLY AFTER the boundary day (the era-start day is the new source's baseline,
unspannable by any interval of that source, so it stays with the prior era).
Days at or before the FIRST era's start predate all coverage capability: they stamp
`'fmp'` when the first era is FMP (legacy semantics), else the sentinel
**`'pre_coverage'`** (cold-start corner, Outsider). `'fmp'` and `'pre_coverage'`
rows never count toward the A2.4 re-arm bad-set; both remain visible as NO_DERIVED
in the report and the ALARM gate's record. Regressions: t4/t6.

## N1.2 — Sub-versioning standing rule (Guardian C-3 / Challenger)

Any future change to attribution or stamping SEMANTICS on rows that already exist
under a rule_version MUST either (a) write new rows under a bumped sub-version
(A2.x), or (b) archive the pre-change rows/report verbatim in `audits/` BEFORE the
change deploys — as was done for the A1.5 first pass and the 2026-08-08 era fix
(`A2_FIX_EVIDENCE_PACK_2026-08-08.md`, the 0→12→0 record). Narrative-only
preservation is not sufficient.

## N1.3 — Value-distinct dedupe is src-aware (Challenger)

Two consecutive snapshot rows with identical (shares, nav) but different `src` are
NEVER the same strike seen again: the seam strike survives dedupe in both the
harness (`_strikes_with_capture`) and `latest_delta`. Prevents the seam-swallowing
pro-readiness bias. Regression: t5.

## N1.4 — Adapter fail-closed extensions (Challenger / Executioner)

Issuer adapters additionally read as DECLARED ABSENCE when:
- **Identity check:** the page's own AUM is present and shares × NAV deviates from
  it by more than `ISSUER_IDENTITY_TOL` (default 15%) — the mis-parse guard; or
- **Staleness:** the page's own as-of stamp parses to a date older than
  `ISSUER_ASOF_MAX_TDAYS` (default 3) trading days — the frozen-page guard (the
  XRPC 2026-07-31 case). An unparseable stamp logs a notice but does not reject.
Both are verifier-side data-quality gates; neither touches any score.

## N1.5 — SCHEDULED SERIES BREAKS + the ETHA reverse split (pre-declared NOW)

A known corporate action is handled by a pre-declared, fund-scoped src EPOCH —
never ad hoc on the day. The registry is `etf_issuer_pages.SCHEDULED_BREAKS`.
**Entry 1 — ETHA reverse split, effective 2026-10-06:**
- Captures whose effective ET date (pre-dawn = prior day, mirroring t_of) is on or
  after 2026-10-06 stamp `src='issuer_ishares_r1'` — ETHA only; IBIT's series is
  untouched (fund-scoped epoch, Expansionist).
- The existing splice rule voids Δshares across the seam; era attribution assigns
  the boundary day to the prior epoch (N1.1). The boundary interval is a seam —
  VOID/PENDING semantics, never FAIL, never EMPTY_INTERVAL, never flow.
- ETHA's Δ-clock and §8 per-fund preconditions restart on r1; the SOURCE's earned
  standing does NOT reset (the instrument re-denominated; the source did not fail)
  (Economist).
- The official ratio is recorded from the issuer's announcement at the event for a
  one-time RATIO CONTINUITY review (post-split shares × ratio ≈ pre-split within
  the 20%-guard's spirit); the ratio is NEVER used to synthesize a ratio-adjusted
  continuous series, and historical rows are NEVER rewritten (Guardian/Challenger).
- The 20%/day discontinuity guard is satisfied via the epoch seam only; its
  threshold is not widened (Guardian).
- Re-arm planning note: ETHA's clocks restart at the break — evidence near that
  date should lean on IBIT + Bitwise/21Shares (Executioner). The epoch stamp and
  its regression (test_etf_issuer_pages t3) shipped 2026-08-09, satisfying the
  Executioner's 2026-09-29 deadman in advance.

## N1.6 — FMP 30-day silent comparison: the pre-declared 2026-09-05 rule (Challenger)

Declared before the comparison data exists. FMP is DROPPED as a data source unless,
over 2026-08-09 → 2026-09-05, on issuer-covered funds, read-only from
`etf_share_observations` by src:
1. on ≥80% of fund-days where BOTH sources report, FMP's shares agree with the
   issuer strike within 0.5%; AND
2. FMP shows NO frozen streak longer than 3 trading days while the issuer strike
   moved (the Gate-4 failure mode).
Either criterion failing → drop (subject to the Outsider's rider: if the Fidelity
adapter is not yet live on 2026-09-05, FMP is retained for FBTC/FETH ONLY —
observations-only, never strikes for covered funds — until wave 3 lands, because it
is currently the only watcher on those funds).

## N1.7 — Access doctrine + the iShares endpoint finding (Q1, recorded)

Doctrine (Guardian/Executioner, board-convergent): a declared browser-grade UA
carrying the `NowTrendIn/2.0` token against a PUBLIC issuer page is honest
identification and the CEILING of acceptable posture; headless-browser or
session-forging escalation past an ACTIVE wall (the Grayscale 429 class) is
circumvention and requires its own board ruling before anyone builds it.
Endpoint migration attempt (2026-08-09): BlackRock serves the product page itself
as `application/json` from the documented `.ajax` resource — the page IS the data
document; the product-screener API rejects without an internal config name. No
separate public machine endpoint was found. The current parser therefore already
reads BlackRock's own data payload. Standing source-preference ORDER adopted
(Expansionist): official data endpoint → server-rendered JSON → rendered-HTML regex
(last resort, migration ticket open). Counsel eyeball of site terms remains open
per the Outsider (flip-adjacent, not code).

## N1.8 — Locale boundary on the join rule (Expansionist, §16a-style statement)

The A2.1 `t_of` settled-through mapping is US-only BY CONSTRUCTION (US Eastern
clock, US trading days). No non-US-listed fund may enter this universe until the
join rule's timezone + trading-calendar is parameterized per listing venue. Any
universe expansion violating this is a cold-start-posture violation (§16a).

## N1.9 — Recorded open items (not implemented this round, on the ledger)

- Wave-3 adapters: Fidelity FBTC/FETH derived-precise (HIGH; a flip precondition
  per the board's either/or), Grayscale (blocked on doctrine N1.7), VanEck.
- Observation-key hardening: add `src` to the `etf_share_observations` uniqueness
  key before a third writer per fund exists (Expansionist/Challenger/Outsider).
- Raw-payload archiving per capture (Challenger A-4).
- Economist prescriptions 1–4, 6, 8 (null-baseline comparator, tail-weighted
  report, coverage-% metric, persisted source ledger, latest-wins sweep, lead/lag
  study) — awaiting Chairman prioritization.
- NO_DERIVED materiality floor uses latest AUM for historical days (known
  approximation, Challenger #3 — biases toward FEWER material flags on old days).
