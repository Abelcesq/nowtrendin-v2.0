---
name: feedback-integrity-standard
description: "HARD RULE for NowTrendIn — protect Gradient Score integrity: reject circular metrics, reputable licensed sources only, measurement-not-advice, and NEVER publish performance/accuracy claims we can't support with real denominator-backed data. Apply to every addition + every public-facing claim."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 68bada2a-c5b3-4db5-a55b-bc9a4f6844d3
---

**HARD RULE (founder-level, applies to EVERY addition to NowTrendIn — no exceptions):**

Before adding any feature, metric, or data source, it MUST pass the integrity standard. If it fails, push back and propose a clean alternative rather than building it — even if the user asked for it directly. The founder explicitly wants this perspective enforced as a hard rule and thanked me for pushing back on a circular metric.

**Why:** NowTrendIn sells to hedge funds, banks, businesses, and consumers. The entire product value is *trustworthy, accurate measurement* — the Gradient Score is the objective instrument. One contaminated metric or one unlicensed/disreputable source destroys client trust and the company's viability. Integrity is the moat, not a nice-to-have.

**The four guardrails to check on every addition:**

1. **Gradient Score objectivity** — nothing may flow *upstream* into the Gradient Score that would contaminate it. Derived/internal signals (e.g. the N demand metric) that already feed it are the ceiling; do not add more. New validation layers must sit *downstream* (read-only), never feed back. [[feedback-no-circular-metrics]]

2. **No circular metrics** — a metric must not validate against something it is itself an input to. Example caught live: "does N agree with the Gradient Score" is circular because N is *inside* the score. Validation must use INDEPENDENT factors. State the independence explicitly in code + UI copy.

3. **Reputable, licensed sources only** — every data source must be (a) commercially licensed for our use, and (b) from a reputable/authoritative publisher. Banned until written commercial approval: Reddit, Guardian, CoinGecko, Messari. See SECURITY.md allowlist. NEVER add a source without confirming commercial terms. When in doubt, leave it OFF and flag it.

4. **Measurement, not advice** — outputs describe exposure / positioning / cycle position, never "buy"/"sell"/"will grow". Every financial output carries the not-investment-advice disclaimer. (Why "Risk" was renamed "Positioning"/"Market".)

5. **Never assert what we can't support (public claims)** — confirmed by the founder 2026-06-15: do not publish any performance/accuracy/scale number we cannot defend with a real, denominator-backed source. No hardcoded marketing stats. If the live data isn't there yet, remove the claim or show the honest value with its denominator; never inflate. Same for "Live" labels on static/mock data — label illustrative content "Illustrative", wire to live later. Example caught live: the terminal login proof strip ("73% accuracy · 11d lead · 2,840 topics") was hardcoded while the ledger was 0%/5-sample/850-pending → removed it (would have undermined integrity with hedge-fund clients). [[feedback-verify-before-ship]]

**How to apply:** When asked to add anything, silently run it against these four. If it passes, build it and note which guardrail it respected. If it fails, say so plainly, explain the integrity risk, and propose the clean version. Do not quietly comply with something that erodes integrity. Surfacing the risk IS the job.

Related: [[feedback-no-circular-metrics]], [[project-nowtrendin-2]]. Source policy lives in NowTrendin/SECURITY.md.
