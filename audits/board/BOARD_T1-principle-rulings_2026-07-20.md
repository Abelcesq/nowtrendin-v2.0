# BOARD REVIEW — T1 / Principle rulings for D8 and S1 (2026-07-20)

**Convened:** founder question — "what are the options under a T1/principle ruling for D8 and S1,
and how should we proceed?" Six independent archetype memos (Challenger, Economist, Expansionist,
Outsider, Fiduciary, Engineer), identical evidence pack (the reopened D8 backtest + the E2 outflow
investigation + live P1 regime-adjusted ledger + the positioning_intel L118/L160 mechanism trace).
Advisory only — the Chairman rules. No code shipped from this review.

---

## 1. Vote table

| Reviewer | D8 | S1 |
|---|---|---|
| Challenger | **D8-1 HOLD** | S1-2 (reopen backtest) |
| Economist | D8-2 FULL T1 | **S1-2 scoped to a DISTRIBUTIONAL degeneracy test** |
| Expansionist | D8-2 FULL T1 | **S1-3 ship as integrity fix** (discard 0-for-5) |
| Outsider | D8-2 FULL T1 | S1-2 (reopen backtest) |
| Fiduciary | D8-2 FULL T1 | S1-2 (reopen backtest) |
| Engineer | D8-3 equity-only T1 | S1-2 (reopen backtest) |

**D8:** FULL T1 (D8-2) 4 · equity-only (D8-3) 1 · HOLD (D8-1) 1 → **majority: ship D8 as T1,
flag-gated, presentation-truth; crypto relabel mandatory.**
**S1:** reopen/test-before-ship 5 · ship-now 1 → **near-consensus: rule the principle, then a
LEDGER-INDEPENDENT test decides the ship; the 0-for-5 is never the justification.**

---

## 2. D8 — the board's recommendation: **ship T1, flag-gated, as presentation-truth (D8-2)**

Five of six agree the served `mm==30.0` pin under a display that reads "absent/baseline forming" is
an integrity defect worth closing — a "fabricated read wearing an honesty sticker" (Fiduciary), the
§16a "30 ✓" defect, and the exact display-vs-number contradiction a skeptical customer reads as
bluffing (Outsider). The reopened backtest makes it SAFE: Δ(enrollments)=Δ(verdicts)=0 by mechanism,
disjoint cohorts — **zero accuracy cost, zero circularity.** So caution-budget is spent freely on
honesty (Fiduciary/Economist).

**Two live sub-decisions the Chairman must settle:**
- **Scope — full vs equity-first.** Fiduciary + Outsider: ship equity AND crypto together, or the
  mixed message (honest equity, fabricated crypto ring) is WORSE. Engineer: equity-FIRST (D8-3) to
  watch the 95 ROUTINE→DORMANT flips + tier hysteresis on one surface before touching crypto, and
  because crypto is blocked on a product rename anyway. Both are defensible; the split is transient
  parity-drift the frontend-consistency agent would flag.
- **Crypto label — non-negotiable if crypto ships:** all 12 coins go M-only (D-ring annihilated) →
  **must be relabeled "Market-Confirmation-only," never headlined "Money Gradient" with zero money
  data** (unanimous among the ship votes). This is a product-naming decision, founder's call.

**The dissent (Challenger, D8-1 HOLD) — recorded, not overruled lightly:** the T2 tripwire has NOT
tripped (covered-lane unmeasured_fraction 0.524 ≥ 0.5), so exclusion still binds on ABSENCE by our
own pre-registered rule; D7 already discloses the absence on-screen; D8 is score-surface churn (174
rows, regen, hysteresis, a crypto rename) bought for zero accuracy and one cosmetic gap. The
majority answer: D8 is honesty, not accuracy — and honesty doesn't wait for a coverage tripwire that
governs the ACCURACY reactivation (T2), not the presentation one (T1). T1 is the founder's truth-
ruling, available now.

## 3. S1 — the board's recommendation: **rule the principle, then a ledger-INDEPENDENT distributional test decides the ship (synthesis of S1-2 + Economist)**

The whole board accepts the *principle*: L118's `net<-1 → outflow` is the same degenerate-NET class
ruled noise for insiders on 2026-06-26, and in production (AV blend off) L118 IS the entire flow
signal. Where they split is whether the principle TRANSFERS to congress automatically (Expansionist:
yes, ship it) or must be DEMONSTRATED for congress (everyone else: prove it first).

**The Economist breaks the tie with the decisive move, and it resolves the integrity-vs-Goodhart
tension cleanly:** the claim "congress net is degenerate" is a **distributional** claim, provable
from the distribution of congress net across the whole universe — **with no ledger and no n.** So:

- **Run a held-out DEGENERACY test on congress net** (does `net(buys−sells)` discriminate across
  tickers, or is it structurally sell-dominated / near-constant "outflow" like insider net was
  15/15?). Ledger-independent → **no circularity, no tuning-to-outcomes, no Goodhart.**
  - **If degenerate** → parity is EARNED; ship the accumulation-only asymmetry on L118 as an
    **integrity fix** (the Expansionist outcome, now justified by evidence independent of the losing
    lane). It would ship identically if the lane were 5-for-5.
  - **If it discriminates** → parity does NOT transfer (congress ≠ insider — blind trusts, ethics
    rules, discretionary trading are real counter-mechanisms); **reject S1 (S1-4)**, keep L118, wait
    for n.
- **The regime-confounded 0-for-5 / 18.8% base rate is discarded as evidence entirely** (unanimous).
  P(0-for-5 | regime)=0.35 — it justifies nothing.
- **Even the "ship" branch is score-affecting** (it changes a served DIRECTIONAL claim on named
  securities — the Fiduciary's live exposure: calling AAPL/GOOGL/NVDA high-conviction "outflow" off
  congress net −8/−5/−5 while all three rose is a claim we could not defend to counsel). So the ship
  branch still requires founder sign-off + serve_payload regen + flag-gating; it stays reversible for
  the eventual n≥15 confirm.

**Why not S1-3 straight-ship (Expansionist alone):** the insider fix shipped bare because it was
uncontested and AV-gated OFF; L118 moves production mm TODAY, and the change is entangled with a live
losing lane — so parity of *principle* does not buy parity of *process* (Outsider/Engineer). The
degeneracy test is the cheap, clean thing that earns the ship without the entanglement.
**Why not pure S1-1 HOLD:** the directional display claim is a standing defensibility exposure
(Fiduciary) — waiting for n≥15 while emitting an unsupported sell-side claim on named megacaps is the
one thing worse than acting; the degeneracy test resolves it in days, not months.

---

## 4. Unanimous red lines (bind any option)
- The 0-for-5 / 18.8% regime-confounded rate is **NEVER** a ship justification.
- Never throttle the outflow lane to flatter a rate; keep enrolling it unchanged.
- Ledger enrollment never reads mm/tier; S1 never tuned against the ledger it is measured by.
- No crypto "Money Gradient" over a null / M-only D-ring — relabel or don't ship crypto.
- No small-n ledger rate or census % published externally as an accuracy KPI.
- Every score-affecting ship: flag-gated (default off) + founder sign-off + serve_payload regen.

## 5. Recommended sequencing (near-consensus)
1. **D8 first** — pure presentation-truth, zero ledger risk; it proves the flag / tier-hysteresis /
   serve_payload-regen machinery on a safe cohort. Chairman settles scope (full vs equity-first) +
   crypto label at ruling time.
2. **S1 in parallel as ANALYSIS ONLY** — rule the principle, run the ledger-independent congress-net
   degeneracy test; the test result (degenerate → ship integrity fix / discriminates → reject)
   returns to the founder before any L118 code change. No S1 deploy from this review.

---

## 6. Chairman decision block (to be filled)
- **D8:** ☐ D8-1 HOLD ☐ D8-2 FULL T1 ☐ D8-3 equity-first · crypto label: ☐ relabel & ship ☐ defer crypto
- **S1:** ☐ S1-1 HOLD ☐ rule principle + run degeneracy test ☐ S1-4 reject parity
- Ruling logged in SESSION_LOG on decision.
