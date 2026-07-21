# S1 — Congress-Net Degeneracy Test (ledger-independent) — 2026-07-20

**Board-ordered decision test** (`BOARD_T1-principle-rulings_2026-07-20.md` — Economist's synthesis,
5/6 concurring). The S1 "insider-parity" principle reopens ONLY if congress net is degenerate the
way insider net was ruled degenerate on 2026-06-26 ("raw insider NET is degenerate — insiders
structurally sell; the signal is BUYING"). That is a **distributional** claim, provable from the
distribution of congress `net(buys−sells)` across the served universe — **with no ledger and no n**,
so it carries zero circularity and zero tuning-to-outcomes (the 0-for-5 outflow record is discarded
as evidence entirely, per the unanimous red line). Read-only; source: live `/risk/scores?limit=300`
(2026-07-20). This file is the only artifact.

## Method
For every served instrument carrying a congress block, take `net = buys − sells` (the exact quantity
`positioning_intel.py` L118 keys the flow claim on: `inflow if net>1 else outflow if net<-1 else
neutral`). Compare the distribution to the insider precedent (a ~15/15 all-sell basket → degenerate).

## Result — congress net DISCRIMINATES; it is NOT degenerate

Instruments with congress data: 300; **14 are non-zero** (286 net==0 → correctly emit neutral).
Among the 14 names congress actually trades:

| | count | detail |
|---|---|---|
| net-BUY (net>0) | **7** | incl. clean buys 3/0, 3/0, 5/0, 1/0, 1/0 and mixed 2/1, 5/4 |
| net-SELL (net<0) | **7** | the 4 outflow-emitters are two-sided: 6b/14s, 4b/10s, 7b/11s, 1b/3s |
| directional (\|net\|>1) | 3 inflow / 4 outflow | roughly balanced |
| net stats | mean **−0.03**, median **0.0**, range −8…+5 | ~symmetric |

**The insider precedent was ~15/15 = 100% sell (BUYING the rare exception, gated ≥$250K).** Congress
net is **7-buy / 7-sell, mean ≈ 0** — categorically different. When congress net<−1 fires "outflow,"
that is a *relative* signal (this name net-sold more than others), not a structural artifact; and the
feed surfaces clean net-BUYERS (3/0, 5/0) that emit real "inflow." **Congress buying is common, not
rare** — so the premise that "routine congress selling ≈ noise" (the insider degeneracy) does NOT
hold for congress.

## Verdict — REJECT S1 parity (board branch S1-4)

The insider-parity **principle does NOT transfer**: congress net is not degenerate-by-construction,
so the accumulation-only asymmetry that was correct for insiders is NOT justified for the congress
base flow. **Keep `positioning_intel.py` L118 unchanged.**

**This does NOT clear the outflow lane** — it closes the *principle-reopen* path only. The outflow
0-for-5 / 0-for-3-episodes remains an open question to be settled by **DATA at the pre-registered
n≥15 resolved episodes (or 0-for-10)**, never by the parity shortcut and never by the
regime-confounded small-n rate. The S1 reactivation trigger therefore drops its PRINCIPLE arm and
keeps only its n arm.

## Caveats / spin-off (not acted on)
- Point-in-time snapshot; re-run over a rolling window as n grows (the balance could shift).
- Narrower, DIFFERENT critique observed but out of S1's scope: the 4 outflow mega-caps are two-sided
  (e.g. 6 buys / 14 sells) yet fire "outflow" at saturated intensity 1.0 — a *conviction/intensity*
  calibration question (the gate measures breadth of trading, not directional conviction), not a
  degeneracy question. If pursued, that is a new item with its own investigation + backtest — it is
  NOT S1 and NOT shipped here.
