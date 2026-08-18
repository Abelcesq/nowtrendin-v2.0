# Coinbase Cross-Venue Premium — 5-Day Value Review (Chairman-ordered)

**Review date:** 2026-08-18 (ordered due 2026-08-15; run on the 9-day banked series)
**Scope:** READ-ONLY. Held-out accumulator `transfer/coinbase_premium.py`, table `coinbase_premium`
(`price_class='coinbase_retail_spot'`), 12 coins, Coinbase `/v2/prices/{COIN}-USD/spot` vs FMP
`{COIN}USD` reference. Feeds no score, no display. Nothing was modified.
**Question ordered at build (2026-08-10):** does the cross-venue premium show enough VARIANCE and
DIRECTIONALITY to justify a full §16 workup as a US-institutional/retail-demand proxy?

## 1. Data retrieved

No engine endpoint serves the rows (`premium_report()` exists in the module but is not wired to any
route; `/openapi.json` has no `/diag/coinbase`). Rows were obtained by a direct **read-only** Postgres
SELECT against the engine DB (session set `readonly=True`; single short-lived connection; the
Heroku-CLI `pg:psql` path is broken on this box, `config:get` + psycopg2 worked).

- **108 rows = 12 coins × 9 days**, 2026-08-10 → 2026-08-18, no gaps. PK integrity clean.
- Collector `coinbase_premium` HEALTHY (12 signals/day, 12 distinct) per `/health/collectors`;
  `/schema` confirms the table and columns exactly as coded.
- Capture time: day 1 at 22:06 UTC (deploy day), thereafter ~00:02–00:23 UTC daily.

## 2. Findings

### 2.1 Variance — the series is a noise band, not a spread
- All-rows premium: **mean −0.0137%, stdev 0.0411%, min −0.113%, max +0.285%**.
- **98.1% of all readings sit inside ±0.10%**; 99.1% inside ±0.25%. The single outlier is DOT
  +0.285% on 2026-08-13 (one day, one coin).
- Per-coin stdev ranges 0.011% (DOGE) to 0.100% (DOT — driven by that one outlier); majors
  (BTC 0.022%, ETH 0.023%) are at the bottom of the range.

This is the expected signature of comparing two **mid-market** composites. The retail spread the
thesis targets (~0.5–2.0% per the founder's fee comparison) is **structurally absent** from
`/v2/prices/{pair}/spot` — the build note itself anticipated this ("Note /spot is mid-market; the
retail SPREAD signal would use `/v2/prices/{pair}/buy`"). The banked series never measured the
candidate signal; it measured cross-venue mid-price dispersion.

### 2.2 Measurement noise dominates
Premium magnitudes (±0.02–0.10%) are the same order as the price movement crypto exhibits over the
seconds-to-minutes of timestamp skew between the Coinbase fetch and the FMP quote (legs are fetched
sequentially with a 1s pause per coin, and FMP's quote timestamp is uncontrolled). At this magnitude
the daily reading is substantially **asynchronous-sampling noise**, so per-day signs and levels are
not individually meaningful.

### 2.3 Directionality — a weak, not-significant negative basis
- Day-factor (cross-coin mean per day): negative **7/9 days**, mean −0.0137%, sd 0.0222%,
  **t ≈ −1.9 (n=9)** — suggestive of a small persistent Coinbase-below-FMP basis, **not significant**
  at this sample size, and small enough to be an FMP-composite-construction artifact.
- Sign persistence per coin: BTC/ETH flip sign 4×/9 days (noise); only BNB (0/9 positive — but see
  2.5) and DOGE (0/9) are persistently one-sided.

### 2.4 Cross-coin structure — one venue factor for majors, noise for the rest
- Mean pairwise correlation of premium levels: **r = 0.39** (median 0.42, range −0.12…0.88).
- Majors cluster: r(BTC,ETH)=0.85, r(BTC,SOL)=0.78, r(BTC,XRP)=0.64 → a **common venue/USD factor**
  among liquid majors; smaller coins are mostly coin-specific noise. Variance decomposition:
  day-factor sd 0.022% vs coin-residual sd 0.035% — the common factor explains a minority of variance.
- Caveat: with n=9 days every correlation carries a ±~0.6 confidence band.

### 2.5 Relation to known moves — none demonstrable
r(premium_t, same-day ref return) and r(premium_t, next-day return) are scattered in sign across
coins (e.g., DOGE lead +0.49 but BNB −0.21, LINK −0.36) with n=8 pairs — pure noise; no
directionality claim can be supported or refuted from this window.

### 2.6 Data-integrity flag — BNB rows exist and should not
The module documents "BNB is not listed on Coinbase — expected declared absence, never an error,"
yet **BNB has 9/9 rows** (persistently −0.05%). Coinbase's `/v2/prices` returns **synthetic exchange
rates** for assets not listed for trading — so the BNB "venue price" is not an order-book price, and
the same caveat applies to any coin unless listing status is verified per coin at workup. The
fail-closed assumption held at the HTTP level but not at the semantic level.

## 3. Verdict — (c) SHELVE the /spot-premium AS-IS, with a specific trigger

Against the ordered options:
- **(a) Proceed to full §16 workup — NO.** Observed variance (±0.1% band, 98% of readings) and
  directionality (t≈−1.9, sign-flipping) do not clear the bar, and the series is
  measurement-noise-dominated.
- **(b) Extend accumulation as-is — NO.** More days of a mid-market-vs-mid-market comparison
  cannot surface a retail-demand spread that the endpoint structurally does not carry.
- **(c) SHELVE WITH TRIGGER — YES.** The thesis is **not disproven — it was never measured.**

**Trigger (Chairman approval required; score-affecting path stays §16-gated):** amend the
accumulator to also capture `/v2/prices/{pair}/buy` and `/sell` legs (same table pattern, same
`price_class` discipline, fail-closed), verify per-coin Coinbase listing status (drop or flag
synthetic-rate coins incl. BNB), and where feasible timestamp both legs; then accumulate **7–10
days** and re-run this exact review on the **buy-spread series** (buy−spot and buy−ref), where the
0.5–2% retail spread — and its *variation*, the actual demand proxy — would live.

Secondary housekeeping (non-blocking, flagged only): `premium_report()` is dead code until wired to
a `/diag/coinbase` route mirroring `/diag/coinapi`; would have made this review endpoint-only.

## 4. Appendix — per-coin stats (premium_pct, n=9 days)

| coin | mean | stdev | min | max | range | days pos | sign flips |
|------|-------|-------|--------|--------|-------|----------|-----------|
| ADA  | −0.0308 | 0.0362 | −0.1133 | +0.0082 | 0.1215 | 1/9 | 2 |
| AVAX | −0.0131 | 0.0234 | −0.0623 | +0.0159 | 0.0782 | 2/9 | 4 |
| BCH  | −0.0142 | 0.0218 | −0.0494 | +0.0268 | 0.0762 | 2/9 | 1 |
| BNB* | −0.0493 | 0.0267 | −0.0908 | −0.0050 | 0.0858 | 0/9 | 0 |
| BTC  | −0.0036 | 0.0216 | −0.0381 | +0.0315 | 0.0696 | 4/9 | 4 |
| DOGE | −0.0158 | 0.0105 | −0.0288 | 0.0000 | 0.0288 | 0/9 | 0 |
| DOT  | +0.0246 | 0.1003 | −0.0460 | +0.2849 | 0.3309 | 5/9 | 5 |
| ETH  | −0.0103 | 0.0233 | −0.0607 | +0.0184 | 0.0791 | 2/9 | 4 |
| LINK | −0.0085 | 0.0260 | −0.0367 | +0.0481 | 0.0848 | 2/9 | 4 |
| LTC  | −0.0238 | 0.0437 | −0.0800 | +0.0781 | 0.1581 | 1/9 | 2 |
| SOL  | −0.0080 | 0.0257 | −0.0460 | +0.0265 | 0.0725 | 5/9 | 3 |
| XRP  | −0.0120 | 0.0367 | −0.0941 | +0.0151 | 0.1092 | 5/9 | 2 |

\* BNB = synthetic exchange rate, not an order-book venue price (§2.6).

Day-factor (cross-coin mean): 08-10 −0.038 · 08-11 −0.031 · 08-12 −0.036 · 08-13 +0.029 ·
08-14 −0.001 · 08-15 −0.014 · 08-16 −0.024 · 08-17 +0.006 · 08-18 −0.015.

*Method: read-only SELECT of all 108 `coinbase_premium` rows; stats computed offline
(scratchpad); no engine writes, no table changes, no config changes.*
