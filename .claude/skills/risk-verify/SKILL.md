---
name: risk-verify
description: Spot-check a company's risk payload in NowTrendIn — confirms every signal layer (FINRA short interest, OFR macro leverage, WhaleWisdom 13F, creator coverage, broadcast coverage, Alpha Vantage news, Trend Beneficiary) is populated and fresh. Flags missing or stale fields. Good before demoing to an investor or after deploying. Use when the user says "verify <ticker>", "check the risk page for <X>", "is the data complete for <Y>", or names a watchlist company to inspect.
---

# /risk-verify — Company risk payload integrity check

You verify that ALL signal layers in NowTrendIn's per-company risk payload are populated for a given ticker.

**Engine URL**: `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`

## Steps

1. **Get the ticker** from the user. If they give a company name, look up the ticker from `WATCHLIST_TICKERS` in `financial_risk_gradient.py`. If still unclear, ask.

2. **Pull the full risk scores feed** (v2 schema: `{count, results:[…]}`, keyed by
   `risk_topic`/`risk_display` — there is NO `ticker` field on these rows):
   ```bash
   curl -s --max-time 30 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/risk/scores | python -c "import sys,json; d=json.load(sys.stdin); rows=d.get('results',[]); r=[x for x in rows if '<COMPANY>'.lower() in (x.get('risk_display','') or '').lower() or (x.get('risk_topic','') or '').lower()=='<TICKER>'.lower()][:1]; print(json.dumps(r[0] if r else {'error':'not found','samples':[x.get('risk_display') for x in rows[:8]]},indent=2)[:2000])"
   ```

3. **Check each v2 signal layer** (now TOP-LEVEL fields on the row, not a
   `positioning_json` string) and report present/missing/stale:

   | Layer | v2 field path | Source |
   |---|---|---|
   | Detection / confidence | `detection_score`, `confidence_score`, `risk_stage` | engine |
   | Components | `components` (G/I/M/D/C/P breakdown) | engine |
   | Macro leverage | `macro_leverage` | OFR repo |
   | Market gradient | `market_gradient` | market data |
   | Provenance | `source_provenance` | reputable-source tiering |
   | Baseline maturity | `maturity`, `baseline_cycles`, `abnormality` | calibration |
   | Trend Beneficiary | **pull `/beneficiary/{ticker}` directly** (step 4) | trend_beneficiary engine |

   NOTE: FINRA short-interest / WhaleWisdom 13F / Alpha-Vantage layers from the v1
   `positioning_json` are not surfaced on the v2 `/risk/scores` row. For a per-layer
   FINRA/13F audit use the dedicated risk collectors / `/risk/{topic}`.

4. **For Trend Beneficiary specifically**, also pull `/beneficiary/{ticker}` directly and report:
   - exposure_score (0-100)
   - cycle_stage (EARLY / MID / LATE / REALIZED / UNKNOWN)
   - theme matched
   - live_inputs (price_return_12m, valuation_rerating, theme_attention)

5. **Report** with a clear PASS / PARTIAL / FAIL verdict:
   - ✅ All 7 layers populated → PASS
   - ⚠ 1-2 missing or stale → PARTIAL (list which)
   - ❌ 3+ missing or critical (FINRA + Beneficiary both missing) → FAIL

6. **If any layer is missing**, name the most likely cause (key not set in Heroku config, rate limit, collector down) and suggest a one-line check the user can run.

## Output style

Concise. Investor-demo readiness check, not an essay.

## Canonical dates · sources · M/D — updated 2026-06-22

> Cross-cutting updates every data/scoring skill should know. Authoritative specs:
> `CLAUDE.md` §14–15, `DATA_BUILDING_BLOCKS.md` §3a + §5.

- **Canonical date model (✅ LIVE):** PRIMARY `signal_date` = ISO `YYYY-MM-DD` (the ONE
  sort/match/score key); SECONDARY `source_time` (the SOURCE's own HH:MM:SS) + `signal_time`
  (OUR fetch HH:MM:SS, stamped on every fetched row). Enforced by `date_utils` +
  `ingestion_gate.gate_date()`; an unparseable non-empty value → `format_review_queue`
  (human review), never guessed. Same-surge ledger floor `since=detection−30d`. Governs
  SORT/MATCH only — removes NO scoring input. Never reintroduce raw `[:10]` date slicing.
- **New sources (✅ LIVE):** reputable-direct RSS roster incl. **The New Yorker** (news+business);
  **Nasdaq Trade Halts** in the risk module (stage-2; `signal_date`=HaltDate, `source_time`=HaltTime).
- **M/D reweighting (⏳ IN DESIGN — NOT shipped; backtest-before-ship gates it):** reputable ≠
  automatic mainstream full weight — 1 reputable = ½ weight, FULL only on ≥2 DISTINCT reputable
  (distinct `source_name`; the "Belgium vs Iran" case). Research/early-signal outlets (War on
  Rocks, Rest of World, Global Issues, Pew, RAND, NBER) → Dark Matter via `blog_collectors`
  GHOST_FEEDS at **expert/niche tier** — the D-vs-M router is `platform_tier`, NOT `is_organic`;
  do NOT route them through `_RSS_FEEDS`/`_news_write` (which forces `mainstream` and suppresses
  the early signal).
- **For THIS skill:** Risk/Other tab — `risk_signals` now carry `signal_date` (primary) + `source_time` + `signal_time`; Nasdaq Trade Halts is a new stage-2 source (`source='nasdaq'`, `signal_type='trade_halt'`). Expect these columns + source when verifying a company's layers.
