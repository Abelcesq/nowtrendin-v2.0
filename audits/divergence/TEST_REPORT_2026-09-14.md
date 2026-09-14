# Divergence tool — branch test report (2026-09-14)

**Branch:** `feature/divergence-tool` · **Sealed spec:** `audits/board/DIVERGENCE_PREREG_2026-09-14.md`
(`param_version bd6e36498ef6…c022877b`) · **Verdict: WORKS AS SPECIFIED.** All six Chairman-ordered
items executed; the full research program ran against real accrued data on GitHub's runners
(Actions runs 34876297477 → 34877026388) and committed its evidence to this directory.

## What was built (all committed on this branch)

| Piece | File(s) | Verification |
|---|---|---|
| Sealed engine core (the D residual) | `transfer/divergence.py` | `transfer/test_divergence.py` 18/18 — incl. a **seal-binding test**: the build FAILS if anyone edits the sealed prereg |
| Internal status route | `/diag/divergence` in the engine | internal-gated exactly like `/diag/coinapi`; no public serve path touched |
| Held-out declaration | `transfer/heldout_registry.py` | firewall self-audit LIVE TREE CLEAN |
| Web display (NOT yet served) | `Crypto.tsx` "Positioning vs Price" column + Register panel | build clean; forbidden-words grep clean; C1 absence states intact |
| Research runner | `tools/divergence_research.py` | SELECT-only asserted at import; no outcome/ledger table named (§8); exit-1 only on seal mismatch |
| Collector instrument patch | `transfer/coinapi_derivs.py` | units + suspect guard (K14); deploys with the next engine release |
| Full gates | — | `run_tests.py` 19/19 · `integrity_gate.py` PASSED · web build ✓ |

## Real-data results (run 3, all sections OK)

- **§0 Seal** — verified independently on the runner: prereg hash == core `PARAM_VERSION`.
- **§1 COT backfill (item ③)** — CFTC leveraged-funds positioning, CME **BTC: 1,020 weekly rows
  back to 2017-12-19** (the first CME bitcoin futures week), **ETH: 740 rows from 2021-04-06**;
  `knowable_at = report + 3d` point-in-time stamped. Non-enrolling: training/context only (§5).
- **§2 Instrument audits (item ②)** — *Missingness:* **0 missing coin-days in 432** — no
  missingness-vs-volatility bias is even testable yet; collector perfectly regular. *Timing:*
  pooled Spearman(capture delay, |return|) = **−0.10** (n=432) — no evidence captures run late on
  volatile days; the sealed 3-offset test still awaits its own collection. *Cross-leg:* funding vs
  ΔlnOI **ρ=0.17 raw / 0.16 momentum-orthogonalized** (n≈200) — related but far from redundant,
  supporting funding-as-conditioner-only. *COT cross-leg:* only 2 overlapping weeks — accrues.
- **§3 D preview (item ④, K16 spec-development stamp on every row)** — all 12 coins, 35–36 aligned
  days each; **every D honestly `None`**: the sealed strict windows need ~186 aligned days
  (7-obs Δln + 90-obs z + 90-obs fit) and the collector has accrued ~36. This is the spec
  refusing to fabricate a number — correct behavior, not a defect.
- **§4 Equity-first (item ⑥)** — all 16 watchlist tickers OK (FINRA short interest × FMP prices,
  11 settlements each); D in honest warm-up until ~48 aligned settlements (~2 years of bi-monthly
  FINRA data). The machinery runs; the windows fill on their own.
- Items ① (seal, commit `b7f06c1`) and ⑤ (collector patch, `cab0d90`) were completed before the runs.

## Defects found by testing and fixed (each root-caused per §10a)

1. Socrata resource `6dca-aqww` is the **legacy** COT schema (no leveraged-funds columns) — the
   fetch now schema-probes candidate datasets and proceeds only with one carrying the
   lev_money pair. Found via the new self-diagnosing HTTP errors (response body captured).
2. CoinGecko public rate limit 429'd 6 of 12 coins at 2.5 s pacing → 15 s pacing + 65 s retry.
3. stooq returned message pages (no closes) to the runner → **FMP** (the paid source already
   serving the market ledger's ground-truth prices) is now the primary equity research price,
   stooq fallback. All prices remain labeled RESEARCH-ONLY.

## Standing gates before the merge phase (unchanged, per the sealed prereg §6 and board rulings)

- **Crypto user-facing display** requires: rights evidence for CoinAPI redistribution
  (RIGHTS_REGISTER **OPEN item 9** — founder/counsel), instrument audits passed (timing 3-offset
  still accruing), board note, Chairman sign-off. The web column/panel is built and tested but
  ships "NOT MEASURED" until those clear.
- **Equity legs** are rights-clean (FINRA/CFTC public records; FMP paid) but stay research-only
  under this seal until their own board note (§7).
- Mobile has no crypto screen — documented N/A for the crypto surface.
- No ledger data is deleted at any point; the register replaces *presentation* only.
