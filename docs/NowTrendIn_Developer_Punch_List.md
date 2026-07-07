# NowTrendIn — Developer Punch List (one page)

**How to read this:** do the steps in order — you can't fix or test scores that are computed on bad inputs.
**⚡ = ship now** (mechanical, safe, no backtest).  **🔒 = backtest-before-ship** (changes scores → validate against the Wikipedia/GDELT referee, never auto-apply).  **➕ = new capability to build.**

---

### STEP 0 — Make the inputs trustworthy (the foundation)
- ⚡ **Grade tool: drop N, use the engine's renormalized 6-component weights.** Fixes both the N-into-gradient integrity leak *and* the Grade-vs-engine scale mismatch. *Highest-value single fix.* `transfer/ai_grade.py`
- ⚡ Clamp every AI-returned number to its allowed range; reject partial AI JSON instead of defaulting the missing pieces to 0; check AI category labels are valid before they enter a score.
- ⚡ Fix the `engagement_asymmetry` key mismatch (producer writes one name, scorer reads another → silently reads 0). `signal_calibration_integration.py`
- ⚡ Add the 3 missing N-detail columns, or stop displaying the stale N breakdown.
- ⚡ Make the silent calibration error-swallow **log** the failure instead of hiding it (`except: pass` → log).
- 🔒 Build the **SCORING_CONTRACT** (one written format spec per input) + a write-time check that **quarantines** bad data instead of zeroing it; replace the "missing-becomes-0" reads so *absent ≠ real zero*.
- 🔒 Collapse the **three disagreeing weight recipes** into one shared definition imported everywhere.
- 🔒 Fix the market **Positioning Concentration** flat-default (distinguish absent vs 0), and the watchlist exact-name match that silently drops company financials on a name drift.
- 🔒 Split the overloaded `risk_stage` column into one vocabulary.
- ➕ Ship the read-only **Scoring Contract Auditor** into the nightly run, beside the date auditor — it catches future input bugs automatically, no matter which code wrote them.

### STEP 1 — Fix the scoring errors (after Step 0)
- ⚡ **`heisenberg_gap` bug:** the stored gap must equal Detection − Confidence (the mcp family is off by ~24 points — flat arithmetic bug, easiest credibility win).
- ⚡ **Alias-merge** so duplicate spellings score as one topic (`hormuz` / `strait of hormuz`; `mcp` / `model-context-protocol`).
- ⚡ **Market tier:** reconcile the 3 disagreeing tier fields to one surfaced value; require a minimum signal count before ranking "movers"; fix the garbled-text (UTF-8) payload; remove the identical hardcoded interpretation string.
- 🔒 Extend the **anti-collapse protection across the full mainstream band** so china / apple / openai stop reading as "emerging."
- 🔒 Add a **breaking-news / same-surge override** so a confirmed wall-to-wall event (the Greenspan case) isn't read as a speculative early lead.
- 🔒 **Down-weight or replace Persistence** — it feeds on the engine's own past scores (the one real circularity to watch).

### STEP 2 — Wire the independent referee
- ➕ Stand up **Wikipedia Pageviews + GDELT** in a held-out table the score can **never** read. This is the outside truth that tells you whether Steps 0–1 actually worked. **No public accuracy claim before this exists.**

### STEP 3 — Test prediction (the alpha question)
- ➕ Only after 0–2: validate against **market price** (not Google Trends), on a **pre-registered, frozen bar** (e.g. median lead ≥ +3 trading days, ≥100 matured events, out-of-sample). This gate decides whether the alpha engine is real. **Until it passes, no "before it arrives" performance claim to investors.**

---

**Integrity gate (applies throughout):** ⚡ items are mechanical — ship now. 🔒 items change *which data enters a score*, so they move scores and must pass backtest-before-ship against the referee — never auto-applied. The Grade-weight fix is ⚡ but spot-check it, since it correctly changes graded values.
