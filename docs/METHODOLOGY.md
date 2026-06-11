# Gradient Score — Methodology (Single Source of Truth)

> **Governance rule:** this file is the authoritative record of *which components
> each scorer uses and how they relate*. If the engine code and this file ever
> disagree, that is a bug to fix — not a lag to tolerate. The product's value
> proposition is auditable rigor, so the audit trail must match the machine.
>
> **Trade secret:** exact component **weights, thresholds, and calibration
> constants live in code only** (server-side, env-overridable). They are never
> published here, in the UI, or in any API response. This doc describes the
> *structure* and *relative emphasis*, not the numbers.

_Last updated: 2026-06-11._

---

## The two public scores (the "Duality")

Both are produced from the same components, with different emphasis:

- **Detection** — *earliness*. Weighted toward the components that fire first
  (Gradient Strength, Dark Matter). Optimized for speed; accepts more false
  alarms. Audience: creators, marketers, trend-forward brands.
- **Confidence** — *precision*. Weighted toward components that require sustained,
  repeated evidence (Inertia, Persistence, Platform Diversity). Audience:
  institutional analysts, investors, strategic planners.
- **Overall** — a balanced blend, used for stage classification on the engine side.

The **gap** (Detection − Confidence) is the earliness signal: a large gap = detected
early, not yet broadly confirmed; it closes as Persistence rises.

> **Displayed stage band** (BREAKOUT/STRONG/EMERGING/WATCHING/MONITORING) is derived
> from **Detection** in the app (`stageFromScore` in `frontend/lib/signals.ts`), the
> same basis the category tiles use, so a topic's badge can't contradict the category
> it appears in. The engine also stores an `overall`-based `signal_stage`, surfaced as
> `engineStage` for reference.

---

## Components

| Code | Name | What it measures | Live engine fn |
|------|------|------------------|----------------|
| **G** | Gradient Strength (a.k.a. Niche Concentration) | Ratio of niche/expert signal density to mainstream. High = experts talking, public hasn't caught on (runway ahead). | `compute_gradient_strength` |
| **I** | Inertia / Momentum | Acceleration across consecutive scoring cycles (rising vs flat vs declining). For established topics (≥2 cycles) supplied continuously by `momentum_engine`. | `compute_inertia` / `momentum_engine.compute_inertia` |
| **M** | Platform Diversity | How many distinct platforms carry the signal + tier spread (niche↔mainstream) + diffusion pattern. | `compute_platform_diversity` |
| **D** | Dark Matter | Inferred hidden/private activity: first-timer surge + engagement asymmetry, scaled by an organic-authenticity gate. Concave first-timer curve (`100·ratio^0.7`) keeps resolution to a true 100% flood. | `compute_dark_matter` |
| **C** | Confidence Decay | Freshness of the signal + short-term directional trajectory. | `compute_confidence_decay` |
| **P** | **Persistence** | **Has the topic STAYED elevated across multiple scoring cycles, or is it a one-day spike?** A brand-new topic scores P=0 (no history, no penalty); a topic above EMERGING for ~7+ consecutive cycles (~3 days of hourly scoring) approaches P=100. Detection barely uses P (speed matters, not history); **Confidence weights P heavily** — it is one of the strongest precision drivers, and the gap closes as P rises. | `compute_persistence` / `momentum_engine.compute_persistence` |
| **N** | Now Trending (internal demand) | How often Now TrendIn users query a topic (volume + recency spike). **NOT a component of the public Gradient Score** — see below. | `compute_nowtrendin_score` |

---

## Where N lives (and where it does not)

- **Trend Gradient Score (the product sold to institutions): N is EXCLUDED.**
  The live trend scorer (`gravitational_anomaly_detector.py`, the path that writes
  `velocity_scores` → `/scores`) composes Detection/Confidence/Overall from the
  **six external components G/I/M/D/C/P only**, renormalized to sum to 1.0. This is
  deliberate: blending our own users' demand would create a reflexive feedback loop
  (users search → score rises → they search more) and compromise the external-world
  objectivity institutions pay for.
- **"Now Trending Gradient Score" (separate what-if):** on the trend signal page only,
  we additionally show what the score *would* be if N were folded in as an extra
  factor — `score_with_n = score·(1−w_eff) + N·w_eff`. It is clearly labeled
  *separate / demand-inclusive* and **never sold as the Gradient Score**. To prevent
  the thin-data trap (a fixed % of a near-zero external base being dominated by N),
  `w_eff` is **scaled down by external-evidence sufficiency**, so a topic with little
  external footprint cannot be lifted by internal demand alone; a transparency flag
  (`demand_driven`) surfaces a "limited external confirmation" note when it fires.
- **Grade tool (`ai_grade.py`): N is INCLUDED, intentionally.** The Grade tool is an
  explicitly user-requested, demand-aware estimate for topics that lack rich external
  data — internal demand is one of the few real signals in that regime. It is a
  **different metric from the trend Gradient Score** and is labeled as such. ⚠️ Two
  open items: (1) verify against real query data whether graded topics actually have
  *low* N (likely the opposite — they're the topics users ask about most); (2) the
  Grade tool should carry the same thin-data N down-weighting + transparency flag as
  the trend what-if, or it can grade a no-footprint topic high on demand alone.

---

## Known scorer divergences to keep in view

There are **three scorer modules** in the engine repo — only one is canonical:

| Module | Components | Status |
|--------|-----------|--------|
| `gravitational_anomaly_detector.py` | G/I/M/D/C/P (N excluded) | **CANONICAL — live serve path** (writes `velocity_scores`). |
| `ai_grade.py` | G/I/M/D/C/P + **N** | Grade tool only (demand-aware estimate). |
| `gradient_engine_backend.py` | G/I/M/D/C (no P, no N) | **Legacy** 5-component scorer. Not on the serve path — do not cite as authoritative (it has misled two separate reviewers). Candidate for removal/quarantine. |

---

## Open calibration / integrity items

1. **Detection saturation** — `compute_platform_diversity` previously pinned every
   4+-platform topic at a flat **M=90** (no top-end resolution), a primary cause of
   Detection freezing. Fixed 2026-06-11 with a continuous curve (anchor-preserved at
   4→90, climbing toward 100), env-revertible via `PLATFORM_DIVERSITY_CONTINUOUS`.
   **Validate with the accuracy sweep before relying on it.** Secondary: the M
   tier/pattern bonuses still saturate to 100 quickly; the discrete fallback `I`
   (`max_consecutive·25`) only affects <2-cycle topics (established topics use the
   continuous `momentum_engine` I).
2. **Narrative conditioning** — _addressed 2026-06-11._ The contradictory "accelerating"
   language and implausible stats ("55K stars / 73K new this week", "10% of commits")
   came from the AI explainer (`ai_grade.explain_topic`, Perplexity free-text), not the
   template generators or the live momentum read (which is well-conditioned). Fixed at
   the source: `_EXPLAINER_PROMPT` now forbids fabricated/unverifiable specific metrics
   and forbids asserting momentum DIRECTION (the engine reports velocity separately);
   `_RESEARCH_PROMPT` got the no-fabricated-stats rule; the UI disclaimer was strengthened
   ("figures are approximate; the measured score and velocity are the engine's").
   **Action required:** the guardrails apply only to NEWLY generated explainers —
   purge the cache to regenerate existing ones: `DELETE FROM topic_explainers;` on the
   engine DB (the per-cycle `_backfill_explainers` then regenerates them, paced).
