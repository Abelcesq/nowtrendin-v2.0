---
name: market-coverage
description: NowTrendIn Market Universe Coverage monitor — catches the "SpaceX problem" where a real publicly-traded company is trending in attention but missing from the curated Market Signal universe (e.g. a fresh IPO). Scans trending business/tech topics, resolves untracked ones to a real ticker, and flags coverage gaps to add to WATCHLIST_TICKERS. Use when the user says "why isn't <company> on Market Signal", "is the market universe current", "check market coverage", "did we miss an IPO", or after a notable IPO.
---

# /market-coverage — keep the Market Signal universe current (the "SpaceX problem")

Market Signal only scores companies in a **curated universe** (`WATCHLIST_TICKERS` +
the SEC watchlist) because it needs a real ticker (FINRA short interest, 13F, price,
fundamentals). When a new company IPOs or starts trending, the static list goes stale
and the company is silently absent — exactly what happened with **SpaceX (NASDAQ:SPCX,
IPO 2026-06-12)**. This agent catches that automatically.

**Engine (v2):** `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com` (public).

## Steps
1. Run the agent (standalone — NOT in `/monitor`, because it makes Finnhub lookups):
   ```bash
   curl -s --max-time 60 https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/monitor/market-coverage
   ```
2. **Report** from `summary`:
   - `tracked_universe` (size of `WATCHLIST_TICKERS`) · `company_candidates_checked` ·
     `coverage_gaps`.
   - `gaps[]` — each `{topic, ticker, resolved_as, mentions}`: a company trending now,
     publicly traded, but NOT tracked.
3. **Act on each gap (with confirmation — never blind-add):**
   - Confirm the ticker is correct and the company is genuinely public (Finnhub already
     filtered to Common Stock; spot-check if the name is ambiguous).
   - Add `"<Display>": "<TICKER>"` to `financial_risk_gradient.WATCHLIST_TICKERS`, and a
     sector to `_TICKER_SECTOR` (pick from banks/technology/autos/energy/defense/general).
   - Deploy the engine, then run a risk collection + score so it populates:
     ```python
     import financial_risk_gradient as risk
     risk.run_risk_collection(risk.DB_PATH); risk.score_all_risks(risk.DB_PATH)
     ```
   - A just-IPO'd name will read **calibrating / ROUTINE** until 13F + short-interest
     history accrues — that's correct, not a bug.

## Integrity (hard rules)
- **Flag, don't force.** Add only companies that resolve to a REAL public ticker and are
  genuinely trending — surfaced from data, never injected. Private companies (Anthropic,
  OpenAI, Stripe…) correctly don't resolve to a Common Stock and must NOT be added with
  fabricated market data.
- Never assert financial figures we can't support; a thin just-IPO'd read stays "calibrating".

Part of the monitoring fleet (see `/data-watchdog`, `/frontend-consistency`,
DATA_BUILDING_BLOCKS.md block B1).

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
- **For THIS skill:** Market coverage — the risk roster gained Nasdaq Trade Halts (stage-2 microstructure); coverage audits should account for it.
