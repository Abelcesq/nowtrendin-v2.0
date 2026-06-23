"""
scoring_weights.py — single authoritative source of the six-component
Gradient Score weight vectors (G·I·M·D·C·P, N excluded by design).

RULES:
- Import ONLY from here.  Never copy-paste weights into another module.
- If you change a value, it takes effect everywhere simultaneously.
- Adding or removing a component requires a backtest before shipping.

COMPONENT KEY:
  G  gradient_strength        (niche concentration, fires first)
  I  inertia_score            (sustained multi-window acceleration)
  M  platform_diversity       (breadth across sources)
  D  dark_matter_score        (first-timer / engagement anomaly)
  C  confidence_decay         (freshness + directional momentum)
  P  persistence_score        (historical longevity across cycles)
  N  nowtrendin_score         (internal demand — EXCLUDED from composite,
                               stored separately, never in these weights)

All three vectors sum to 1.0 (renormalized after N removal at v2.1).
Scores computed via: 0-100 = min(100, sum(component * weight for ...))
"""

# ── Balanced read — equal emphasis on early AND confirmed signals ─────────────
WEIGHTS_OVERALL = {
    "G": 0.244,   # Gradient — niche concentration
    "I": 0.222,   # Inertia — sustained acceleration
    "M": 0.167,   # Platform diversity
    "D": 0.133,   # Dark matter
    "C": 0.078,   # Confidence decay
    "P": 0.156,   # Persistence — historical longevity
}
# sum = 1.000

# ── Detection — earliness (G+D weighted highest) ─────────────────────────────
WEIGHTS_DETECTION = {
    "G": 0.375,   # Gradient fires first on niche concentration
    "D": 0.216,   # Dark matter: hidden private signal
    "I": 0.182,   # Inertia
    "M": 0.102,   # Platform spread
    "C": 0.057,   # Decay
    "P": 0.068,   # Persistence: minimal — want to catch early
}
# sum = 1.000

# ── Confidence — precision (I+P weighted highest) ────────────────────────────
WEIGHTS_CONFIDENCE = {
    "I": 0.278,   # Inertia — multi-window acceleration confirms
    "P": 0.267,   # Persistence — historical consistency
    "M": 0.222,   # Platform spread
    "G": 0.122,   # Gradient
    "C": 0.067,   # Decay
    "D": 0.044,   # Dark matter: lowest weight for precision
}
# sum = 1.000

# Ordered component list (canonical iteration order)
COMPONENTS = ["G", "I", "M", "D", "C", "P"]
