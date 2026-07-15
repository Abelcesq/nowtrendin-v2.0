# FAMILY-COLLAPSED LEDGER SENSITIVITY LINE — 2026-07-15

**Read-only, report-time only. No stored ledger rows changed; the raw per-key ledger
remains the canonical record.** Closes the "your wins are correlated" attack (Board
2026-07-15 pre-build item, Challenger + Outsider): if fragment keys of one real-world
entity each earn a ledger verdict, per-key counting could overstate independent wins.

- Confirmed families: **46** (51 aliases) — the founder-ruled 2026-07-15 set.
- Resolved ledger rows: **84** (engine-reported: total 84, blended 9.5%, tracked-race 25.0% on 32).
- Resolved rows belonging to ANY confirmed family: **3** (['andy_burnham', 'haaland', 'world_cup']).
- Families with MORE THAN ONE resolved member (the correlated-win case): **0**.

| metric | RAW per-key | FAMILY-COLLAPSED |
|---|---|---|
| resolved units | 84 | 84 |
| LED | 8 | 8 |
| SAME_DAY | 6 | 6 |
| LAGGED | 70 | 70 |
| · pre-broken | 52 | 52 |
| · near-miss | 18 | 18 |
| blended hit rate % | 9.5 | 9.5 |
| tracked-race hit rate % | 25.0 | 25.0 |
| race sample | 32 | 32 |

**Finding: the correlated-win effect is currently ZERO** — no confirmed family has
more than one resolved ledger row, so the collapsed rates equal the raw rates.
The sensitivity line should be re-run as families accumulate resolved members
(the pending pool + future enrollments can change this).

*Method: family verdict = best member verdict (LED > SAME_DAY > LAGGED > FP); a collapsed*
*LAGGED family is pre-broken only if every lagged member was. param calib-params-v3|patience365|lead365|match30|preb7|estmin14.*