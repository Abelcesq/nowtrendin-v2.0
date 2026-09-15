# EVIDENCE PACK — 24-hour review + the two data questions (board round 4 of this session)

**Prepared 2026-09-15 for the nine-seat board. Chairman's order:** "reconvene the Board and
have the board review all updates implemented in the last 24 hours. Also have the board
provide a solution on what we need to obtain data for the 'positioning v price' column and
the 'tier' column."

**What is being decided:** (A) verdicts on the six update groups R1–R6 below (all shipped or
in flight in the last 24 h); (B) for Q1 and Q2, each seat's assessment of the candidate
solution paths for getting REAL data into the two columns that today honestly read
NOT MEASURED — with any conditions, orderings, or rejections.

Primary artifacts (read as needed): `audits/board/DIVERGENCE_PREREG_2026-09-14.md` (sealed),
`audits/divergence/TEST_REPORT_2026-09-14.md` + `run_summary.json`,
`audits/frontend/ALLPAGES_AUDIT_2026-09-14.md`, `docs/buyer-diligence/RIGHTS_REGISTER.md` §F,
`docs/buyer-diligence/tos-snapshots/coinapi_legal_2026-09-14.txt`,
`docs/buyer-diligence/COINAPI_RIGHTS_REQUEST_draft.md`, SESSION_LOG.md addenda 8–10,
`transfer/divergence.py`, `transfer/coinapi_derivs.py`, `transfer/crypto_money_gradient.py`,
`web-terminal/src/views/Crypto.tsx`. Git range: `b7f06c1..HEAD` on main.

---

## R1 — Divergence tool built under the sealed prereg (branch-isolated, then merged)

Sealed prereg (SHA-256 = param_version `bd6e3649…c022877b`, commit b7f06c1 strictly before
any analysis code). `transfer/divergence.py`: D = zq − (α̂+β̂·zp); Δln over 7 obs;
robust median/MAD z, trailing 90 obs, forward-only, MAD≈0 → None (honest absence);
deterministic Theil–Sen refit weekly; warm-up rows measured:false (no short-window value
wearing the sealed badge); suspect=1 rows excluded; equity adapter at §7 cadence (windows 24).
`test_divergence.py` 18/18 including a SEAL-BINDING test (any edit to the sealed prereg fails
the build). `/diag/divergence` internal-gated (verified 403 in production). Held-out registry
declares the module; firewall audit clean. Research runner `tools/divergence_research.py`:
SELECT-only asserted at import, §8 no-forward-join (no outcome/ledger table named), exit-1
only on seal mismatch. All engine gates: run_tests 19/19, integrity gate PASSED.

## R2 — Real-data test program (3 GitHub-Actions runs; run 3 all sections OK)

- Seal verified independently on the runner (hash == PARAM_VERSION).
- CFTC COT backfill: BTC 1,020 weekly rows (2017-12-19 → 2026-09-08 — the full CME era),
  ETH 740 rows; `knowable_at = report + 3d` stamped per row; non-enrolling (context only).
- Instrument audits on 432 live collector rows (12 coins × 36 days): missingness — ZERO
  missing coin-days (no MNAR bias testable; collector perfectly regular); timing — pooled
  Spearman(capture delay, same-day |ret|) = −0.10, n=432 (labeled PARTIAL; the sealed
  3-offset test needs future collection); cross-leg — funding vs ΔlnOI ρ = 0.17 raw / 0.16
  momentum-orthogonalized (n≈200): related, not redundant.
- D preview: all 12 coins aligned 35–36 days; every D honestly None (first measured D needs
  ~186 aligned daily obs: 7 dln + 90 z + 90 fit). K16 stamp on every row (spec-development).
- Equity leg: 16/16 tickers ran (FINRA SI × FMP research prices), 11 settlements each —
  honest warm-up (~48 aligned settlements ≈ 2 years needed for first D at bi-monthly cadence).
- Defects found BY the test and fixed per §10a: wrong CFTC dataset (legacy 6dca-aqww has no
  lev_money columns → schema-probing resolver now picks the TFF dataset), CoinGecko 429s
  (15 s pacing + 65 s retry), stooq cloud-IP blocks (FMP is now the primary equity research
  price). All fetch errors now carry response bodies (self-diagnosing runs).

## R3 — Merge to all platforms + live verification + the stage-2 closure

Merge 70119d4 (engine 5 files, web 2, mobile 0). Engine auto-deployed via CI (tests +
integrity gate in the pipeline; slug 5614877 → f60fad8; /health 200). Web deployed to
gh-pages (PvP column, register panel, then the explainers + vocabulary retirement below).
Post-merge platform verify (read-only probes from a runner): first run 7/8 with /crypto
empty → correctly attributed to the prewarm warming window (NOT concluded a defect, §10a);
re-probe after warm: 8/8 ALL PASS (12 coins serving, no stale signal_freshness leak, both
ledgers serving, /diag/divergence 403, live bundle carries the new column).
Stage-2 closure in the same deploy's release diagnostics: velocity_scores last_vacuum
2026-09-14 17:30 UTC (4.169M live rows), and the scores-build PLAN flipped from the 4.1 GB
seq-scan + disk hash (the 503 mechanism) to Parallel Index Only Scan.

## R4 — All-pages audit (Chairman-ordered) + fixes shipped on BOTH platforms

`ALLPAGES_AUDIT_2026-09-14.md`: 22 DEFECTS / 9 NITs / 8 OK-BY-DESIGN. PREMISE CORRECTION:
mobile HAS crypto screens (added 148487d, 2026-08-18, during the founder absence) — the
session's earlier "mobile N/A for crypto" claim was stale and is recorded as corrected.
Clean passes: zero forbidden words in the divergence renderings; no live NaN path; §17
gating present; divergence merge touched 0 mobile files. Fixes shipped (web 60242ee →
gh-pages 97533e7; mobile 33ba1db, tsc 0 errors): web Dashboard crypto tile stopped
rendering money-absent coins as a measured 0 and retired "money movement" from its title
(absent coins: em-dash + hollow chip, excluded from the positioning ranking, ordering
labeled); Ledger crypto-mode vocabulary; History founder disclaimer restored
byte-identical; K17 sign-blind class closed on both platforms (10 files; mobile root fix
at the data layer — gap is now signed; negative gaps no longer captioned with early-stage
prose anywhere); mobile crypto full positioning parity (explainers + register + NOT
MEASURED slot, Aurora tokens, zero banned hexes); tier fabrications removed
(`tier ?? 'ROUTINE'`, `tier || 'DORMANT'` → honest absence + hollow NotMeasuredChip);
mobile DarkMatterPanel/WhyScoresDiverge 4c tri-state (UNKNOWN vs UNMEASURED, never a
numeric ratio for either); BUILDING→MODERATE legend per MARKET_LEVELS.

## R5 — RIGHTS item 9 (CoinAPI) determined against captured text (Chairman-ordered)

New `ops-fetch-legal.yml` archives dated plain-text snapshots of vendor terms
(CoinAPI + CoinMetrics + Coinbase, 2026-09-14) to docs/buyer-diligence/tos-snapshots/.
Determination recorded in RIGHTS_REGISTER citing the snapshot: (a) internal/research use
CLEARED under §3.1 ("install and use … for your own business purposes"; §6 restricts only
rent/lease/sub-license/modify of the Services); (b) end-user DISPLAY of the derived
residual NOT cleared — the agreement is SILENT on derived-data display, and silence is not
a written grant → written-confirmation request drafted
(COINAPI_RIGHTS_REQUEST_draft.md) for the founder to send; (c) the Data Sources
pass-through clause ("solely responsible for any use of the external Data Sources…")
flags Binance's own market-data terms for counsel review before any display.

## R6 — In flight / residuals (context, not yet done)

- Mobile SignalAnalysisPanel (never actually implemented despite CLAUDE.md recording it
  live — git-verified) + the market-detail N/Platform-Indicator card: Chairman ordered both
  built; a worker is building them now (port of the web panel, POST /analysis/{kind};
  N plumbed through the mobile mapper, §17 omit-when-absent).
- NEW FINDING from the Chairman's 2026-09-15 screenshot: the crypto rail still shows
  "money absent" (bold heading) and "No proxy money-positioning data for this coin this
  cycle" — these are ENGINE-SERVED strings (`gap_state='money_absent'` rendered with
  underscores replaced, and the served `interpretation` text from
  transfer/crypto_money_gradient.py), not web copy. The client-side vocabulary retirement
  cannot reach them; an engine-side display-string pass (display-only, no scoring change)
  is the candidate fix. Board may condition/verdict this.
- Mobile changes reach devices only on the next Expo publish from the founder's machine.

---

## Q1 — What do we need to obtain DATA for the "Positioning vs Price" column?

Current state: the column renders honest NOT MEASURED; the engine serves no divergence
block. The sealed prereg (§5/§6) + register impose these gates. Candidate path (assess,
condition, reorder, or reject; add alternatives):

1. **Rights** — CoinAPI written derived-data-display confirmation (draft letter ready;
   founder sends) AND counsel review of the Binance pass-through. [blocking for display]
2. **Instrument audits** — missingness (currently passing trivially: zero missing days);
   unit guard (shipped with the merge: units + suspect marking — note prod columns exist
   only since deploy f60fad8); the K12 **3-offset timing test** requires a COLLECTOR CHANGE
   (capture at 3 fixed intra-day offsets, ≥30 days, ≥1 coin) that is NOT yet built.
3. **History** — first displayable D needs ~186 aligned daily obs per coin (collector
   accruing since 2026-08-10 → earliest ~2027-02, uninterrupted); the SCORED window (§5,
   K16) starts at the first post-seal row (2026-09-14) and needs ≥90 post-seal obs before
   any forecast correlation (~2026-12-14 earliest); no rate published below 30 resolved
   flags (§6). Historical venue dumps/licensed panels are NON-ENROLLING (context only).
4. **Sealed price source** — the D display requires an independent, §16-onboarded price
   series stored by us (divergence.py docstring); today's prices are research-only
   (CoinGecko/FMP). A §16 six-gate onboarding decision is needed for the price leg (FMP is
   already paid + serving the market ledger's ground truth — candidate).
5. Then: board note + Chairman sign-off (prereg §6) before any number renders.

## Q2 — What do we need to obtain DATA for the "Tier" column?

Current state: tier = _level((money_movement + market_confirmation)/2), served ABSENT
whenever the money/positioning leg is absent — which today is ALL 12 coins (the composite
requires ≥2 votable positioning sources per coin; most coins structurally have <2 — the
"source limit" case; the rest transient). M (market confirmation) is measured for all 12.
Candidate options (assess/condition/reject; add alternatives):

- **(a) Wire the CoinAPI OI leg into the crypto positioning composite** — the only
  positioning-class source with FULL 12-coin coverage (that was its build purpose). Gates:
  it is SCORE-AFFECTING → backtest-before-ship + board + Chairman flip (§16 gate 6); its
  own rights posture is INTERNAL-USE-CLEARED (R5) — note the tier chip would then be
  derived from CoinAPI data, so the derived-display rights question may apply to the tier
  too (seats should opine).
- **(b) Add more proxy positioning sources** to clear the ≥2 floor per coin: CoinMetrics
  (RIGHTS item 10 open — community tier presumed non-commercial), Coinbase premium leg
  (item 11, shelved as noise 2026-08-18), spot-ETF flow (covers only 2–3 coins). Each must
  pass §16 six gates.
- **(c) Re-define the tier display when D is absent** — e.g., an explicitly-labeled
  "M-only tier" (confidence_level already exists and is measured for all 12). Risk: a tier
  from half the inputs wearing the full-tier badge; any such change is display-semantics +
  potentially §15a/§16a territory.
- **(d) Status quo** — honest ABSENT until (a) or (b) lands. The current chips are
  truthful; the cost is a column of NOT MEASURED on the flagship crypto page.

*Both Q1 and Q2 answers should state: the concrete sequence, who acts (founder / counsel /
engineering / a future board), the earliest honest date data can appear, and what must
NEVER be done to shortcut it.*
