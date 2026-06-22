---
name: feedback-no-circular-metrics
description: NowTrendIn — never let a validation metric depend on something it is itself an input to. Validate with independent factors only.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 68bada2a-c5b3-4db5-a55b-bc9a4f6844d3
---

When building any validation / confirmation / cross-check metric for NowTrendIn, it must validate against **independent** inputs — never against something the metric itself feeds.

**The live example that established this:** The N component (`nowtrendin_score`, internal query demand) already feeds the Gradient Score (12% of Detection, 10% of Confidence). So a "does Now TrendIn demand confirm the Gradient Score" check would be partly circular — N is *inside* the score. The fix that shipped: the Signal Convergence validator (`now_trending_direction.py`) validates the score's direction against raw volume + niche concentration (both N-independent), and the UI copy states it's "independent of N demand."

**How to apply:**
- Before building a validator, list its inputs and the thing it validates. If they overlap, it's circular — redesign with independent factors.
- Make the independence explicit in code comments AND user-facing copy (clients are sophisticated; they will notice circularity and it destroys trust).
- Downstream read-only validation (consume the score, never feed it) is the safe pattern.

Part of the broader [[feedback-integrity-standard]].
