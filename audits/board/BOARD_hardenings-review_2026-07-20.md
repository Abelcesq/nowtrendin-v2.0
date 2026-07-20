# BOARD REVIEW — E3/E4/E5 scoring hardenings + the S1 hold (2026-07-20)

**Convened on the founder's order** ("have the board review these updates and provide its
analysis and recommendations"). Material: the shipped-and-verified changeset (deployed engine
`e44a6a4`, git `da37d49..19d4620`) — measurement-integrity hardenings + the deliberate hold on
the S1 outflow score change. Six independent archetypes; five pulled the live endpoints and
reproduced every figure; the Expansionist relied on the pack's live readings (its host DNS
didn't resolve). **Nothing reviewed touches a served Gradient or Market score.** Chairman rules
per item.

## HEADLINE: SHIP STANDS — nothing reverted; six convergent OPERATIONAL fixes + one new measurement item

Unanimous: the changeset is sound, correctly scoped, and lands the reviewers' own D8
prescriptions; **the S1 hold is the correct, principled call (6/6 APPROVE the hold)**. But the
board caught that the changeset "made the *denominators* honest (episodes, gate-rejects, census)
while leaving three *numerators/thresholds* that quietly favor the good news" (Challenger) — and
those need closing. All follow-ups are OPERATIONAL or documentation; none is a revert; none
touches a served score.

## PER-ITEM VERDICTS (6 memos)

| Item | Verdict (consensus) | Required follow-up |
|---|---|---|
| E4.1 witness NULL fix | **SHIP 6/6** | Replace the `if None: = None` tautology (a comment, not a mechanism) with a regression test asserting NULL is stored (Challenger); confirm no pre-fix row already stored intensity×100 (Outsider) |
| E4.2 episode-collapse | **SHIP 6/6** | The "CONFIRMED if ANY row confirmed" rule is a MAX operator that inflates the winning lane (inflow 6/7 rows → 3/3 episodes buries the documented miss). Also serve a strict/majority/most-recent rate; never headline the optimistic one. Expansionist: this sits on a stat the Chairman ruled IS a legitimate accuracy KPI → **RULED** |
| E4.3 gate-reject counter | **SHIP but FIX** | Module-level, since-process-boot, on a daily-recycled multi-dyno fleet → structurally ~always 0 (live: 0/0 despite ~188 flow-neutral instruments). Persist to a durable fleet-global counter (or relabel "this_process"); **until fixed, a 0 means "unknown," not "none" — do not cite it in board readings** |
| E4.4 degenerate-census | **SHIP but FIX (×2)** | (a) Cold `crypto_full` cache returns `coins:0` = false "converted/healthy" on a reactivation trigger → return `available:false`/unknown, never 0 (all 6). (b) The T2 tripwire is **saturated/un-fireable**: "has ≥1 unmeasured" = 299/300 and stays 100% forever by E5's own permanent-frontier logic, so `deg > half` can never fire → re-spec as a **fraction that can trend AND segmented per-cohort** (asset class / coverage source), else T2 is dead furniture (Challenger + Expansionist) |
| E3 DEFERRED_ITEMS.md | **SHIP but FIX (×2)** | (a) S1's "0-for-10" trigger unit is unspecified — rows vs episodes run at ~3× different speeds; since episodes are now canonical, state **episodes** (Challenger/Expansionist/Executioner). (b) No scheduled OWNER — wire the census-T2 read + the /market/accuracy episode counts into a weekly cadence (improve-system or scoring-assessor) so the shelf is walked by rule, not memory |
| E5 §16a cold-start posture | **SHIP 6/6** | Give §16a an ENFORCEMENT gate like §16's `[source-onboarded]` commit hook (a `[cold-start-stated]` assertion on universe-expansion commits) — "MUST state" without a hook is aspirational at >1 engineer (Expansionist) |
| **S1 HOLD** | **APPROVE THE HOLD 6/6 (RULED)** | Do not reopen now. See the symmetry ruling + the principle-vs-n question below |

## THE SYMMETRY RULING (adopt into the record — Challenger, Economist, Expansionist, Outsider)

The pack's regime argument was applied asymmetrically and the board corrects it: if outflow's
0-for-5 is "fully consistent with market regime alone" (these names rallied +8–19% in-window;
P(0-for-5 | regime) = 0.35), then **inflow's 6/7 rows / 3-of-3 episodes is EQUALLY regime-
flattered** — "the same coin landing heads because the market went up" (Challenger). **Neither
lane is validated at this n.** The single accuracy error a skeptic would seize on is anyone
citing "inflow 85.7%" as evidence the Money Gradient works. The board's narrative must drop any
implication that inflow is a win.

## THE STANDOUT NEW PRESCRIPTION — regime-adjust the ledger (Economist P1, highest value)

The symmetry problem has a real fix: resolve market-ledger verdicts against a **concurrent
benchmark** (did the instrument beat SPY over the window?), reported alongside the absolute ±5%
verdict, using the FMP/Databento price feed already wired. This de-confounds BOTH lanes at once
and is the honest denominator for the S1 trigger — it is what makes the whole ledger (inflow
included) diligence-defensible rather than regime-flattered. Held-out, measurement-only, no
served score touched. OPERATIONAL.

## THE S1 PRINCIPLE-VS-n QUESTION (Expansionist + Outsider — for the Chairman)

The S1 mechanism (routine net-sell = noise, net-buy = signal) is ALREADY ruled true for
insiders on 2026-06-26 **on principle** (net is degenerate/sell-dominated), with no ledger n
required. S1 is the identical principle applied to congress flow, yet its reopen is gated on a
ledger losing-streak count. The Outsider's point-blank: "is there a world where you look at 15
episodes and decide routine congress selling IS signal?" The Expansionist's resolution: reframe
the S1 reopen trigger to **principle-OR-n** — reopen for a held-out, regime-adjusted,
precision-AND-recall backtest when EITHER n≥15 episodes accrue OR the founder rules
insider-parity governs the principle. **Note: even the principle-reopen still requires the
held-out regime-adjusted backtest before ship — no memo says ship now.** The "don't build now"
verdict is unchanged; only the reopening logic is at issue.

## EXTERNAL-SURFACE DISCIPLINE (Outsider — standing)

The honest surfaces now carry small-n numbers (outflow 0/3, blended 3/6) and the 299/300 census
— all correctly flagged/firewalled in the payload. But **no external surface (pitch, client
demo, terminal marketing) may ever quote the market-ledger confirm rate at this n or the census
%** — the flags protect the payload, not a slide.

## LOAD-BEARING INVARIANT (6/6 — keep inviolate)

The single most durable line in the changeset, in DEFERRED_ITEMS.md: **ledger enrollment must
NEVER read money_movement or tier.** It is the anti-circularity keystone — what keeps the score
and its own validator independent; T3 correctly makes any proposal to couple them void the Δ=0
shield and force a re-backtest first.

## DECISION TABLE FOR THE CHAIRMAN (all OPERATIONAL/documentation — none touches a served score)

| # | Fix | Class | Board standing |
|---|---|---|---|
| H1 | Census cold-cache (crypto + equity) → `available:false`/unknown, never 0 | OPERATIONAL | 6/6 — highest consensus |
| H2 | Census T2 tripwire: fraction-based AND per-cohort segmented (else un-fireable) | OPERATIONAL / RULED | Challenger + Expansionist |
| H3 | Episode-collapse: also serve strict/majority rate; never headline the optimistic ANY-rule | RULED (accuracy-KPI measurement rule) | 6/6 |
| H4 | Gate-reject counter: persist durable/fleet-global (or relabel this_process); treat 0 as unknown meanwhile | OPERATIONAL | 6/6 |
| H5 | E3: state S1 trigger unit = **episodes**; note T2 granularity fix | documentation | Challenger/Expansionist/Executioner |
| H6 | Wire census-T2 + episode-count triggers into a weekly scheduled reader (improve-system/scoring-assessor) | OPERATIONAL | Guardian/Expansionist/Outsider/Executioner |
| H7 | E4.1: add regression test asserting NULL; then delete the tautology | OPERATIONAL | Challenger |
| H8 | §16a enforcement gate (`[cold-start-stated]` commit hook, like §16) | OPERATIONAL | Expansionist |
| P1 | **Regime-adjust the market ledger** (benchmark/beta vs SPY alongside absolute ±5%) | OPERATIONAL (measurement) | Economist — highest-value new item |
| R1 | Adopt the symmetry ruling: neither lane validated at this n; drop "inflow is a win" narrative; keep small-n rates + census off every external surface | RULED / documentation | 4/6 explicit, 0 oppose |
| R2 | S1 reopen trigger → **principle-OR-n** (still held-out regime-adjusted backtest before ship) | RULED (trigger reframe) | Expansionist + Outsider raise; Chairman's call |

**Chairman — your decision per item.** Nothing here reverts; nothing ships to a served score.
