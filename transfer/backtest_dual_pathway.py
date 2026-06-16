"""
Backtest for the dual-pathway recalibration (Phase C) + baseline-relative
mainstreaming (fame vs. diffusion).

Validates the REQUIRED behaviours before shipping:
  1. Early-tech (expert-origin) detection ~= unchanged (the MOAT preserved)
  2. FIFA cold-start surfaces via ABSOLUTE magnitude (day-one spike)
  3. FIFA spike (established baseline ~0 off-season) reads mainstream/high
  4. SpaceX at BASELINE FAME is NOT dragged into mainstream suppression
     (w ~ 0) -> scores on its real signal, not its fame
  5. SpaceX with a real EARLY EXPERT signal scores HIGH despite its fame
  6. Broad-but-persistent fragment (breadth at baseline) stays LOW
  7. Single source + mainstream noise stay LOW
"""

import math
from dual_pathway import blend

LOG = lambda v: math.log1p(v)   # engagement_raw is log1p(views/traffic)


def sig(tier, eng, platform, source, n=1):
    return [{"platform_tier": tier, "engagement_raw": eng,
             "platform": platform, "source_name": source} for _ in range(n)]


# (name, expert_det, expert_overall, components, signals,
#  breadth_baseline, magnitude_baseline, baseline_cycles)
CASES = [
    # Expert-origin tech, concentrated on dev platforms — moat, unchanged.
    ("early_tech_expert", 78, 70, {"M": 80, "I": 70, "P": 60},
     sig("expert", LOG(120), "github", "trending", 14)
     + sig("expert", LOG(90), "hackernews", "front_page", 6),
     0, 0, 10),

    # FIFA cold-start (no baseline yet) — must surface via absolute magnitude.
    ("fifa_coldstart", 25, 25, {"M": 100, "I": 10, "P": 100},
     sig("mainstream", LOG(777000), "wikipedia_hot", "top", 1)
     + sig("mainstream", LOG(40000), "google_trends_hot", "daily_US", 1),
     None, None, 0),

    # FIFA established: off-season baseline ~0, now spiking -> mainstream/high.
    ("fifa_spike", 25, 25, {"M": 100, "I": 10, "P": 100},
     sig("mainstream", LOG(777000), "wikipedia_hot", "top", 1)
     + sig("mainstream", LOG(40000), "google_trends_hot", "daily_US", 1)
     + sig("mainstream", LOG(20000), "gdelt", "news", 1),
     0, 2, 10),

    # SpaceX at BASELINE FAME: always ~3 mainstream platforms + magnitude ~39.
    # Current footprint == baseline -> deviation ~0 -> w~0 -> NOT dragged into
    # the mainstream-suppressed blend. Scores on its (modest) real signal.
    ("spacex_fame", 24, 24, {"M": 100, "I": 10, "P": 100},
     sig("mainstream", LOG(24348), "wikipedia_hot", "top", 1)
     + sig("mainstream", LOG(9000), "gdelt", "news", 1)
     + sig("mainstream", LOG(7000), "bluesky", "whats-hot", 1),
     3, 39, 10),

    # SpaceX with a genuine EARLY EXPERT signal (r/SpaceX-style + NASASpaceflight),
    # at baseline fame breadth. Expert gradient is high -> w~0 keeps it on the
    # expert pathway -> scores HIGH (fame does not suppress the early signal).
    ("spacex_early_signal", 74, 68, {"M": 60, "I": 72, "P": 55},
     sig("expert", LOG(300), "reddit", "r/SpaceX", 8)
     + sig("expert", LOG(220), "forum", "nasaspaceflight", 5)
     + sig("mainstream", LOG(24000), "wikipedia_hot", "top", 1),
     3, 39, 10),

    # Persistently broad fragment — breadth at its own baseline (always chatty),
    # tiny magnitude. Deviation ~0 -> expert pathway -> low expert det -> low.
    ("fragment_persistent", 15, 20, {"M": 95, "I": 66, "P": 55},
     sig("mainstream", LOG(900), "newsapi_org", "reuters", 6)
     + sig("mainstream", LOG(700), "newsapi_ai", "ap", 5)
     + sig("mainstream", LOG(500), "bluesky", "whats-hot", 6),
     3, 9, 10),

    ("single_source_niche", 22, 22, {"M": 30, "I": 20, "P": 20},
     sig("mainstream", LOG(1500), "newsapi_org", "reuters", 1),
     1, 8, 10),

    ("mainstream_noise", 20, 20, {"M": 40, "I": 8, "P": 10},
     sig("mainstream", LOG(800), "gdelt", "news", 2),
     1, 7, 10),

    # Tier migration — a topic that lived in EXPERT communities and is NOW
    # crossing into mainstream ones (the textbook niche->mainstream transition).
    # Expert presence + mainstream breadth expanding above baseline -> migration
    # amplifies the mainstreaming weight.
    ("tech_crossing", 60, 55, {"M": 70, "I": 65, "P": 50},
     sig("expert", LOG(400), "github", "trending", 6)
     + sig("expert", LOG(300), "reddit", "r/MachineLearning", 4)
     + sig("mainstream", LOG(9000), "gdelt", "news", 2)
     + sig("mainstream", LOG(8000), "youtube", "trending", 1)
     + sig("mainstream", LOG(7000), "wikipedia_hot", "top", 1),
     1, 8, 10),

    # ── News-outlet corroboration (the founder's model) ──────────────────────
    # BREAKING story, cold-start: carried across 6 DISTINCT reputable outlets but
    # NO search/view traffic yet (news engagement is below the magnitude floor ->
    # magnitude ~0). BEFORE this fix it was invisible (calibrating dropped breadth
    # -> w=0 -> scored as expert/dark-matter). It must now read mainstream-
    # CONFIRMED and surface on the mainstream pathway. "Multiple outlets = mainstream."
    ("news_breaking_coldstart", 18, 18, {"M": 55, "I": 25, "P": 15},
     sig("mainstream", LOG(120), "newsapi_org", "reuters", 1)
     + sig("mainstream", LOG(120), "newsapi_org", "bbc", 1)
     + sig("mainstream", LOG(120), "newsapi_ai", "ap", 1)
     + sig("mainstream", LOG(120), "newsapi_ai", "bloomberg", 1)
     + sig("mainstream", LOG(120), "newsdata_io", "the guardian", 1)
     + sig("mainstream", LOG(120), "gdelt", "nytimes", 1),
     None, None, 0),

    # ONE outlet, cold-start: a single source can still be niche/early. Must NOT
    # be mainstream-confirmed and must stay on the expert pathway (w~0).
    ("news_single_outlet", 20, 20, {"M": 20, "I": 15, "P": 10},
     sig("mainstream", LOG(120), "newsapi_org", "reuters", 1),
     None, None, 0),

    # ESTABLISHED multi-outlet topic AT its own baseline (always covered by ~5
    # outlets, not expanding). It IS mainstream-confirmed ("has arrived") but is
    # NOT newly mainstreaming -> w~0, so the Gradient Score does not flag movement.
    # This is the fame-vs-diffusion distinction applied to news.
    ("news_confirmed_baseline", 22, 22, {"M": 50, "I": 8, "P": 60},
     sig("mainstream", LOG(120), "newsapi_org", "reuters", 1)
     + sig("mainstream", LOG(120), "newsapi_org", "bbc", 1)
     + sig("mainstream", LOG(120), "newsapi_ai", "ap", 1)
     + sig("mainstream", LOG(120), "newsdata_io", "cnn", 1)
     + sig("mainstream", LOG(120), "gdelt", "the washington post", 1),
     5, 0, 10),
]

print(f"{'case':<22}{'pathway':<11}{'mode':<18}{'w':>6}{'mag':>7}{'OLD':>6}{'NEW':>7}")
print("-" * 76)
res = {}
for name, ed, eo, comp, signals, bb, mb, bc in CASES:
    r = blend(ed, eo, comp, signals,
              breadth_baseline=bb, magnitude_baseline=mb, baseline_cycles=bc)
    res[name] = r
    print(f"{name:<22}{r['pathway']:<11}{r['breadth_mode']:<18}"
          f"{r['mainstream_ratio']:>6.2f}{r['magnitude']:>7.1f}{ed:>6}{r['detection']:>7}")

print("\n-- Assertions --")
checks = [
    ("Moat: early_tech unchanged (|delta|<=3)", abs(res["early_tech_expert"]["detection"] - 78) <= 3),
    ("FIFA cold-start surfaces via magnitude (>60)", res["fifa_coldstart"]["detection"] > 60),
    ("FIFA spike reads mainstream + high (>60)",
        res["fifa_spike"]["pathway"] == "mainstream" and res["fifa_spike"]["detection"] > 60),
    ("SpaceX fame NOT dragged by fame (w<0.2)", res["spacex_fame"]["mainstream_ratio"] < 0.2),
    ("SpaceX early expert signal scores high (>60)", res["spacex_early_signal"]["detection"] > 60),
    ("Persistent fragment stays low (<35)", res["fragment_persistent"]["detection"] < 35),
    ("Single source low (<35)", res["single_source_niche"]["detection"] < 35),
    ("Mainstream noise low (<35)", res["mainstream_noise"]["detection"] < 35),
    ("Tier migration detected (expert->mainstream crossing)",
        res["tech_crossing"]["tier_migration"] and res["tech_crossing"]["pathway"] in ("mainstream", "blended")),
    # ── News-outlet corroboration ──
    ("News breaking (6 outlets, no views) surfaces mainstream (det>30)",
        res["news_breaking_coldstart"]["detection"] > 30
        and res["news_breaking_coldstart"]["pathway"] in ("mainstream", "blended")),
    ("News breaking is mainstream-CONFIRMED (multiple outlets)",
        res["news_breaking_coldstart"]["mainstream_confirmed"] is True),
    ("Single outlet NOT confirmed mainstream, stays expert (w<0.2)",
        res["news_single_outlet"]["mainstream_confirmed"] is False
        and res["news_single_outlet"]["mainstream_ratio"] < 0.2),
    ("Established multi-outlet at baseline: CONFIRMED but NOT moving (w<0.2)",
        res["news_confirmed_baseline"]["mainstream_confirmed"] is True
        and res["news_confirmed_baseline"]["mainstream_ratio"] < 0.2),
]
ok = True
for label, passed in checks:
    print(f"  [{'PASS' if passed else 'FAIL'}] {label}")
    ok = ok and passed
print("\nRESULT:", "ALL PASS [OK]" if ok else "FAILURES [X]")
