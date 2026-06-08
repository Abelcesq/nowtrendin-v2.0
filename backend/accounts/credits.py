"""Monthly membership credit allowances + reset logic (shared by the
management command and the internal reset endpoint)."""
from .models import Profile

# Monthly allowances per tier.
TIER_QUERY_TOKENS = {'consumer': 0, 'business': 0, 'enterprise': 100000}
TIER_GRADE_TOKENS = {'consumer': 25, 'business': 250, 'enterprise': 1000}


def reset_all_credits() -> dict:
    """Restore every profile's monthly allowances to its tier's full amount.
    Used for the monthly reset AND as a one-time backfill. Profiles with no
    tier are left at 0. Returns a per-tier count."""
    counts = {'consumer': 0, 'business': 0, 'enterprise': 0, 'no_tier': 0}
    for p in Profile.objects.all():
        tier = p.tier
        if not tier:
            counts['no_tier'] += 1
            continue
        p.tokens_remaining = TIER_QUERY_TOKENS.get(tier, 0)
        p.grade_tokens = TIER_GRADE_TOKENS.get(tier, 0)
        p.save(update_fields=['tokens_remaining', 'grade_tokens'])
        counts[tier] = counts.get(tier, 0) + 1
    return counts
