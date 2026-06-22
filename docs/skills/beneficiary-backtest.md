---
name: beneficiary-backtest
description: Validate NowTrendIn's Trend Beneficiary (SanDisk-pattern) engine against known historical beneficiaries — runs it against a basket of tickers (early Nvidia, early Tesla, Vistra/CEG, SanDisk-2025) and checks whether the engine would have flagged them EARLY in the cycle, not in hindsight after the move already happened. This is the ONLY honest validation of the weights. Use when the user says "backtest beneficiary", "validate the SanDisk metric", "test the beneficiary engine", "would we have caught Nvidia early", or asks if the financial gradient weights are correct.
---

# /beneficiary-backtest — Honest validation of the Trend Beneficiary engine

You run the Trend Beneficiary engine against a basket of KNOWN past winners and verify it would have flagged them EARLY (not LATE in hindsight). Without this, the weights (0.30 theme / 0.30 cycle / 0.20 structural / 0.20 attention) are unvalidated guesses.

**Engine URL**: `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com`

## Concept

A backward-looking model would score TODAY's SanDisk as a max buy — it has every lagging signal maxed (+4000% return, re-rated valuation, saturated narrative). A correctly designed early-detection engine should:

- Score TODAY's SanDisk: high exposure + **REALIZED** cycle stage → "move already done"
- Score 2025-early SanDisk: high exposure + **EARLY** cycle stage → "the find"

Same logic must apply to other known winners. If the engine flags them all as EARLY today, it's overfit. If it flags all as REALIZED today, that's actually correct (because they ARE late now) — but we need to confirm it WOULD have flagged them EARLY at the right historical moment.

## Default test basket (ask the user if they want to modify)

| Theme | Ticker | Why it's in the basket |
|---|---|---|
| ai_infrastructure | NVDA | The classic — was EARLY in 2022, REALIZED by mid-2024 |
| ai_infrastructure | SMCI | Server beneficiary; was EARLY in 2023, REALIZED + correction by 2024 |
| ai_infrastructure | VST | Vistra — AI power demand; was EARLY mid-2024 |
| ai_infrastructure | CEG | Constellation Energy — nuclear/AI; EARLY mid-2024 |
| ai_infrastructure | SNDK | SanDisk — the canonical case, EARLY Feb 2025 |
| energy_transition | TSLA | Was EARLY 2019-2020, REALIZED 2021 |
| energy_transition | ALB | Albemarle — lithium beneficiary; EARLY 2020-2021 |

## Steps

1. **Hit the backtest endpoint per theme**:
   ```bash
   curl -s --max-time 60 "https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/beneficiary/backtest/ai_infrastructure?tickers=NVDA,SMCI,VST,CEG,SNDK&lookback_days=365"
   curl -s --max-time 60 "https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com/beneficiary/backtest/energy_transition?tickers=TSLA,ALB&lookback_days=365"
   ```

2. **For each ticker, report**:
   - Live exposure score (0-100)
   - Live cycle stage (EARLY / MID / LATE / REALIZED / UNKNOWN)
   - When attention first hit BREAKOUT/STRONG for the theme (`would_have_flagged_early_at`)
   - Live theme attention score
   - Verdict: does this make sense given what you know about the company's actual trajectory?

3. **Per-ticker verdict format**:
   - **PASS**: high exposure AND cycle stage matches reality (e.g. NVDA showing REALIZED today, with attention having flagged BREAKOUT a year+ ago)
   - **FAIL — overfit**: shows EARLY today when the move has clearly already happened
   - **FAIL — under-detected**: shows low exposure for a company clearly in the theme
   - **INCONCLUSIVE**: insufficient attention history (e.g. theme too new in our data)

4. **Aggregate verdict** at the end:
   - If ≥5/7 PASS → weights are reasonable, ship as-is
   - If 3-4/7 PASS → weights need calibration; identify which sub-score is off
   - If <3/7 PASS → engine needs redesign before marketing the beneficiary feature

5. **Three honest caveats** to surface in the report:
   - This is a LIGHT backtest — Finnhub data is live, not historical, so company financials reflect TODAY not the historical moment. A full backtest requires period-matched financial snapshots (Finnhub `/stock/financials-reported` across quarters).
   - Cycle stage depends on Finnhub `52WeekPriceReturnDaily` + valuation, which IS historical. So the cycle-stage signal IS being validated, even with live financials.
   - The `theme_attention` input IS historical — `pull_history` persists 12 months of Gradient Scores. So the attention-rise timing IS being validated.

6. **Persist results** to `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\BACKTEST_LOG.md` (create if missing) with the date + verdict counts. Builds a longitudinal calibration record.

## Output discipline

NEVER claim the engine has been "validated" if PASS rate < 80% across multiple themes. The honest answer is "calibration in progress" with the specific weight that's off. Investor-grade truth, not marketing.
