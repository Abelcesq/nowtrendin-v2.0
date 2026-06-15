"""
================================================================
NOW TRENDIN — COMMUNITY-LEVEL TIERS  (calibration refinement 1)
================================================================

THE PRINCIPLE:
  Dark matter vs. mainstream is a property of the COMMUNITY, not the
  platform. The same entity is EXPERT on a specialist community and
  MAINSTREAM on a general one:

    SpaceX on r/SpaceX / NASASpaceflight forum  -> expert (early signal)
    SpaceX on r/all / general news              -> mainstream (arrived)

  Tagging tiers per-platform (what the engine did) misreads a famous
  entity's specialist chatter as mainstream and buries the early signal.
  This module assigns the tier from (platform, community) so the gradient
  and the niche->mainstream tier-migration signal are measured correctly.

DEFAULT: mainstream. A community only earns "expert"/"niche" by being a
genuine specialist venue — general-audience venues (a city's news, r/all,
a trending feed, Wikipedia, broadcast TV) are mainstream by definition.
================================================================
"""

import re

# Platforms that ARE specialist venues end-to-end (the platform == the
# expert community): developer / research surfaces.
_EXPERT_PLATFORMS = {"github", "hackernews"}

# General-audience platforms — always mainstream regardless of community
# (these surface what the broad public is already looking at).
_MAINSTREAM_PLATFORMS = {
    "wikipedia_hot", "google_trends_hot", "google_trends", "youtube",
    "gdelt", "broadcast", "creator", "newsapi_org", "newsapi_ai",
    "newsdata_io", "guardian", "reddit_all", "reddit_popular",
}

# Specialist communities (subreddits / forums / lemmy comms / discourse
# instances) — expert tier. Matched case-insensitively, with/without r/ or c/.
_EXPERT_COMMUNITIES = {
    # AI / ML / data
    "machinelearning", "localllama", "learnmachinelearning", "deeplearning",
    "artificial", "singularity", "datascience", "statistics", "mlops",
    "huggingface", "pytorch", "fastai", "tensorflow",
    # software / infra
    "programming", "rust", "golang", "python", "cpp", "kubernetes",
    "devops", "selfhosted", "homelab", "netsec", "reverseengineering",
    "experienceddevs", "compsci", "hardware",
    # science / engineering / space
    "spacex", "nasaspaceflight", "space", "rocketry", "engineering",
    "physics", "askscience", "chemistry", "biology", "energy",
    "nuclearpower", "askengineers", "materials",
    # finance / specialist markets
    "algotrading", "quant", "options", "securityanalysis",
    # discourse instances (host-style)
    "discuss.huggingface.co", "discuss.pytorch.org", "forums.fast.ai",
    "discuss.python.org",
}

# General communities that explicitly mean "broad public" even on an
# otherwise community-structured platform.
_MAINSTREAM_COMMUNITIES = {
    "all", "popular", "news", "worldnews", "whats-hot", "trending",
    "trending-tags", "trending-links", "top", "frontpage", "lemmy.world",
}

# Keyword hints in a community name that imply a specialist venue.
_EXPERT_HINT = re.compile(
    r"(machine|learning|\bml\b|\bai\b|llm|data|dev|program|engineer|science|"
    r"physics|space|rocket|quant|crypto|security|infosec|research|academ)",
    re.IGNORECASE)


def _norm(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"^(r/|c/|/r/|/c/|@)", "", s)        # strip subreddit/lemmy prefixes
    s = s.split("@")[0]                              # lemmy comm@instance -> comm
    return s.strip()


def community_tier(platform: str, community: str = "") -> str:
    """
    Classify a (platform, community) into 'expert' | 'mainstream'.

    (We collapse the old 'niche' into 'expert' here — both mean
    pre-mainstream specialist — so the gradient's niche/expert grouping is
    unchanged while the assignment becomes community-aware.)
    """
    p = (platform or "").strip().lower()
    if p in _EXPERT_PLATFORMS:
        return "expert"
    if p in _MAINSTREAM_PLATFORMS:
        return "mainstream"

    c = _norm(community)
    if not c:
        return "mainstream"
    if c in _MAINSTREAM_COMMUNITIES:
        return "mainstream"
    if c in _EXPERT_COMMUNITIES:
        return "expert"
    # Heuristic: a specialist-sounding community name is expert; otherwise the
    # broad public default.
    if _EXPERT_HINT.search(c):
        return "expert"
    return "mainstream"


if __name__ == "__main__":
    tests = [
        ("reddit", "r/SpaceX"), ("reddit", "r/all"), ("reddit", "news"),
        ("lemmy", "machinelearning@lemmy.ml"), ("lemmy", "world"),
        ("github", ""), ("hackernews", "front_page"),
        ("wikipedia_hot", "top"), ("bluesky", "whats-hot"),
        ("forum", "nasaspaceflight"), ("discourse", "discuss.pytorch.org"),
        ("lemmy", "technology"), ("newsapi_org", "reuters"),
    ]
    for plat, comm in tests:
        print(f"  {plat:<16} {comm:<28} -> {community_tier(plat, comm)}")
