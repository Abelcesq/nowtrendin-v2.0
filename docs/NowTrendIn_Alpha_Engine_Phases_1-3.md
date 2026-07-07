# NowTrendIn — Alpha-Engine Punch List, Phases 1–3 (one page)

This is the path that **tests whether the "alpha engine" is real** — built so that if it isn't, you've still built a real product. Each phase has an objective pass bar. You don't move to the next until the current one is met. **No performance claim to any investor until Phase 3 returns PASS.**

---

### PHASE 1 — Make the present-tense score correct  (~months 0–2)
**Goal:** the engine reads *today's* attention accurately, before you test whether it predicts tomorrow's.
**Do:** execute Steps 0–1 of the *Developer Punch List* — fix the input contract, close the Grade-tool integrity leak, fix the scoring errors.
**Done when (objective):**
- a known-mainstream topic reliably reads **high on both** detection and confidence;
- no topic is scored twice under different spellings;
- the stored gap equals detection − confidence on every row;
- market tiers carry information (not 87 of 88 "routine");
- the Scoring Contract Auditor runs clean nightly.
**Gate:** ⚡ mechanical fixes ship now; 🔒 score-moving fixes pass backtest-before-ship against the referee.

### PHASE 2 — Stand up the independent referee  (~months 1–3, in parallel)
**Goal:** an outside source of truth that shares no inputs with your score, so every later claim is falsifiable.
**Do:** wire **Wikipedia Pageviews + GDELT** into a held-out table the score can **never** read; resolve each topic to a canonical Wikipedia article (quarantine what you can't resolve — never guess).
**Done when (objective):** the no-gap test runs automatically against the referee and reports a **false-early rate** (you called something "emerging" that the referee says already arrived) — the Greenspan / country-collapse failures become a *number*, not a hunch.
**Gate:** the referee is read-only to the score, forever; never folded into a weight. No public accuracy claim before it exists.

### PHASE 3 — Prove a predictive lead against PRICE  (~months 2–8) — the decisive gate
**Goal:** show your signal leads a **market price move**, not a search trend. Leading search earns nothing; leading price is alpha.
**Do:**
1. Pick tradable instruments and define the event you're predicting (a price/volatility move of size **M** within window **W**).
2. **Pre-register the pass bar before looking, and freeze it:** median lead ≥ **+3 trading days**, hit rate ≥ *[set with your team]*, false-positive ≤ *[set]*, **≥100 matured events**, tested **out-of-sample** (calibrate on an early window, validate on a later one — no peeking).
3. Run prospectively with timestamped detections; let events mature; measure on the frozen bar.
**Done when (objective):** the frozen bar is met out-of-sample on ≥100 matured events → **PASS**.
**Decision rule:**
- **PASS** → the alpha premise is real; proceed to tradability + exclusivity (later phases).
- **FAIL in every scope** → it's a measurement / screening tool, not a predictor; reposition honestly and harvest that business.
- **INSUFFICIENT (<100 matured)** → keep running; claim nothing yet.
**Gate (integrity + legal):** no "before it arrives" or performance claim to any investor until this returns PASS, documented and reproducible. Pitching unproven predictive performance to investment firms is the legal/ethical line — do not cross it.

---

**Honest framing (held to your standard):** Phase 1 is achievable, Phase 2 is straightforward, **Phase 3 is genuinely uncertain — and the current evidence (0.0% ledger, mid-mainstream collapse) leans against it.** That's exactly why it's a *gate*, not an assumption — and why the plan is built so a Phase-3 FAIL still leaves you a real, sellable measurement product instead of a dead end.
