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
