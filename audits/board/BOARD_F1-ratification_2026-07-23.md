# BOARD RATIFICATION — F1 corrected: the "AI detection collapse" is CORRECT by design (2026-07-23)

**Why this record exists:** the 2026-07-23 health-check ranked F1 (`artificial_intelligence` serves
Detection 40 vs stored dual-pathway 79.1) as a CRITICAL live serve-integrity break, and all six
archetypes inherited that from the auditor's own hard-coded "pathway gate regressed" message. Root-
cause tracing OVERTURNED it. The founder ordered a ratification pass so every archetype holds the
corrected model and the Board never re-"fixes" this as a regression. **All six CONFIRMED. No dissent.**

## The corrected truth (supersedes F1 in BOARD_healthcheck_2026-07-23.md)
- The pathway gate did **not** regress — it preserved 79.1 correctly.
- `ai_topic_intelligence.py` **intentionally caps** the umbrella term `artificial_intelligence` at
  its **Tier-4 "MAINSTREAM — Already Arrived" ceiling (detection 40 / confidence 48).** By design.
- **Heisenberg duality (now in `docs/METHODOLOGY.md`, founder-ruled):** Detection ≈ momentum/
  earliness (Δp); Confidence ≈ position/confirmation (Δx); conjugate. A fully **position-localized**
  (already-arrived) term has ~zero earliness, so its **Detection correctly collapses regardless of
  raw mention MAGNITUDE.** High volume of a saturated term is confirmation, not earliness. The
  leading edge (real Δp) lives in the Tier-1 sub-topics. **A HIGH Detection on the umbrella would be
  the bug.** Stored 79.1 is a distinct observable (magnitude, kept for rankability) — never the
  served earliness headline.

## The TWO real bugs (fixed, `7f551af`; no score VALUE changed)
1. **Stage desync (user-facing):** served `signal_stage` came from the pre-taxonomy 79.1 (STRONG)
   beside Detection 40 → one response, two contradictory truths. Serve tail now recomputes
   `signal_stage` from FINAL served det/conf (AI → WATCHING), same invariant as the gap.
2. **Auditor misattribution:** B8 compared served-vs-STORED + hard-coded "pathway gate regressed."
   Now EXEMPTS taxonomy-capped topics + adds a STAGE↔DETECTION contradiction check (the class that
   WAS real). Transparency guard added (`serve_taxonomy_capped` count) so the exemption is VISIBLE.

## STANDING SCORING RULING (binds all future Board reviews + the scoring-assessor)
> **A low Detection on a fully-mainstream / "already-arrived" umbrella topic is CORRECT, not a
> collapse.** By the Heisenberg duality, position-localized ⇒ ~zero earliness. Stored dual-pathway
> MAGNITUDE ≠ served earliness DETECTION — they are conjugate observables. **NEVER "fix" a Tier-4
> taxonomy cap as a pathway-gate / serve regression.** Every derived label (stage, gap) MUST be
> recomputed from the FINAL served Detection/Confidence. Any proposal that raises a saturated
> umbrella term's Detection, or removes the taxonomy cap, contradicts this ruling and is blocked
> pending founder + backtest.

## Residual risks the Board surfaced (ratification is not rubber-stamping) — tracked follow-ups
- **R-A · Falsifiability (Challenger + Economist):** "40 is correct by design" is currently a closed
  loop. The held-out ledger enrollment (§14) EXCLUDES ESTABLISHED/MONITORING topics — exactly the
  mainstream-umbrella class — so the cap is **structurally unvalidatable** by the ledger. It is a
  defensible design PRIOR, not a measured value. ACTION: log the Tier-4 ceiling as an explicit
  assumption; stand up a proxy check (did AI's Tier-1 sub-topics actually LED while the umbrella did
  not? if the sub-topics ALSO collapsed, "already arrived" masks a real detection failure).
- **R-B · Auditor blind spot (Engineer + Outsider):** the exemption keys on taxonomy MEMBERSHIP, not
  on WHY the value diverges. PARTIAL MITIGATION SHIPPED: capped topics are now recorded visibly
  (`serve_taxonomy_capped`), not silently dropped, and the stage-desync check still runs for them.
  OPEN: add a magnitude-crater alarm (a capped topic whose STORED magnitude falls below the ceiling
  is decaying, not "arrived").
- **R-C · Static-taxonomy coverage (Data-Collection):** the taxonomy is HAND-MAINTAINED. The next
  umbrella term to go mainstream ("agentic AI", "vibe coding") escapes the cap until a human adds it
  → over-scores as false earliness, silently. ACTION: a saturation-detector that FLAGS taxonomy
  candidates from live distribution (mainstream_ratio + breadth), never auto-adds (flag-not-force).
- **R-D · Presentation/trust (Fiduciary + Outsider):** the model is right but "AI scored 40" reads
  as broken. The DETAIL view must carry the reason AT the number: "MAINSTREAM — already arrived;
  earliness low by design — Detection measures movement, not size," with the leading-edge sub-topic
  surfaced inline. Without on-screen disclosure the correct number is a churn/misrepresentation risk.

## Ratification roll-up
Challenger ✅ · Engineer ✅ (owned the incomplete trace) · Economist ✅ · Fiduciary ✅ ·
Data-Collection ✅ · Outsider ✅. Six of six confirm; the four residual risks above are logged as
tracked follow-ups, not blockers.

---

## PROCESS GOTCHA — VERIFY-BEFORE-FIX (founder-ordered 2026-07-23; binds Claude across ALL models + sessions)

**The failure this session, stated plainly:** a fix was IMPLEMENTED AND DEPLOYED before the issue
was independently traced to its actual root cause. The `pipeline_integrity` alert *hard-coded* the
words "the pathway gate in apply_calibration regressed"; the Board (all six archetypes) inherited
that hypothesis; the Engineer "traced" it but stopped at the gate; and the first fix shipped —
which was **wrong-direction and made it worse** (it desynced the stage label). The real cause was a
downstream taxonomy cap that nobody had read yet. An authoritative-sounding hypothesis became a
"fact" through repetition, not verification.

**THE RULE (mandatory, every model, every session):**
> Before implementing ANY fix or solution — especially anything score-affecting, or a diagnosis
> handed to you by a monitoring alert, an agent, the Board, or an outside AI analysis — INDEPENDENTLY
> verify, check, and CONFIRM the actual root cause in the code/data FIRST. Trace to the real
> mechanism (the actual line/module that produces the behavior), reproduce it, and confirm your
> hypothesis is the cause — THEN fix. A hypothesis, an alert message, or another AI's analysis is a
> STARTING POINT, never a verified diagnosis. If you cannot point to the exact code/data that
> produces the symptom, you have not diagnosed it — do not deploy.

**Operational checklist the AI must satisfy before shipping a fix:**
1. Read the actual code path end-to-end (every layer that touches the value), not just the first
   plausible site. The bug is often DOWNSTREAM of the first suspect.
2. Reproduce the symptom from real data and state the exact mechanism in one sentence naming the
   file + line.
3. Independently sanity-check the "expected correct" value against the product's own design docs
   (e.g. METHODOLOGY.md / the taxonomy) — the anomaly may be intended behavior.
4. For score-affecting changes: unit/behavioral test the fix locally, confirm no NEW inconsistency
   (this session's fix introduced a stage/detection desync), THEN deploy + verify live + regen
   serve_payload.
5. Treat Board hypotheses and external analyses as leads to VERIFY, not conclusions to implement.
   The Board's job is to widen the search; the AI's job is to prove the mechanism before acting.

This is now also recorded as a standing hard rule in CLAUDE.md, the `nowtrendin2.0` session-startup
skill, and the `feedback-verify-root-cause-before-fix` memory, so it loads for every future session
and model.
