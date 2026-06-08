// THE AUTHORITY ON ACCESS CONTROL.
// Every tier check in the app must use this file. Never hardcode tier logic elsewhere.

export const TIERS = {
  consumer: {
    id: 'consumer' as const,
    name: 'Consumer',
    price: 49,
    colour: '#2D7EEF',
    dataFreshness: 24 * 60 * 60 * 1000, // 24h in ms — can only see data >= 24h old
    canSearch: false,
    canQueryNew: false,
    canAccessGradientScore: true,
    canSetAlerts: true,
    canEditSources: false,
    canDirectSearch: false,
    canAIGrade: true,
    apiTokens: 0,
    gradeTokens: 25,
    description: 'Trend history access (24h+).',
    features: [
      'Gradient Score history (24h+)',
      'Trend monitoring feed',
      'Email + push alerts',
      'All signal categories',
      'AI Grade — 25 credits/mo',
    ],
    restrictions: [
      'Cannot access signals less than 24 hours old',
      'Cannot query new trend topics',
    ],
  },
  business: {
    id: 'business' as const,
    name: 'Business',
    price: 499,
    colour: '#00C896',
    dataFreshness: 12 * 60 * 60 * 1000, // 12h in ms
    canSearch: true,
    canQueryNew: false,
    canAccessGradientScore: true,
    canSetAlerts: true,
    canEditSources: false,
    canDirectSearch: false,
    canAIGrade: true,
    apiTokens: 0,
    gradeTokens: 250,
    description: 'Twice-daily trend intelligence for teams (12h+).',
    features: [
      'Everything in Consumer',
      'Gradient Score history (12h+)',
      'Full signal search + filter',
      'Business analytics',
      'Team sharing',
      'AI Grade — 250 credits/mo',
    ],
    restrictions: [
      'Cannot access signals less than 12 hours old',
      'Cannot query new trend topics',
    ],
  },
  enterprise: {
    id: 'enterprise' as const,
    name: 'Enterprise',
    price: 250000,
    colour: '#D4A017',
    dataFreshness: 0, // live — data available as soon as it is obtained
    canSearch: true,
    canQueryNew: true,
    canAccessGradientScore: true,
    canSetAlerts: true,
    canEditSources: true,
    canDirectSearch: true,
    canAIGrade: true,
    apiTokens: 100000,
    gradeTokens: 1000,
    tokenCostPerSearch: 1,
    seats: 5,
    description: 'Live access the moment data is obtained + token-based queries.',
    features: [
      'Live Gradient Score (data the moment it is obtained)',
      'Unlimited reads of current trends',
      'Direct topic query — 1 token per search',
      '100,000 query tokens/month (included)',
      'AI Grade — 1,000 credits/mo',
      'Up to 5 users — shared token pool',
      'Edit data source weights',
      'Custom alert thresholds',
      'API access',
    ],
    restrictions: [
      'Each search query costs 1 token (100,000/month, shared across users)',
      'All search results proprietary to Now TrendIn',
    ],
  },
} as const;

export type TierID = keyof typeof TIERS;

export const TIER_ORDER: Record<TierID, number> = {
  consumer: 0,
  business: 1,
  enterprise: 2,
};

type BooleanFeature =
  | 'canSearch'
  | 'canQueryNew'
  | 'canAccessGradientScore'
  | 'canSetAlerts'
  | 'canEditSources'
  | 'canDirectSearch'
  | 'canAIGrade';

export function canAccess(tier: TierID, feature: BooleanFeature): boolean {
  return !!TIERS[tier]?.[feature];
}

// Returns true if data of the given age (ms) is accessible for this tier.
export function isDataAccessible(tier: TierID, dataAgeMs: number): boolean {
  return dataAgeMs >= TIERS[tier].dataFreshness;
}

export function getTierConfig(tier: TierID) {
  return TIERS[tier];
}
