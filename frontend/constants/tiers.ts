// THE AUTHORITY ON ACCESS CONTROL.
// Every tier check in the app must use this file. Never hardcode tier logic elsewhere.

export const TIERS = {
  consumer: {
    id: 'consumer' as const,
    name: 'Consumer',
    price: 49,
    colour: '#2D7EEF',
    dataFreshness: 12 * 60 * 60 * 1000, // 12h in ms — can only see data >= 12h old
    canSearch: false,
    canQueryNew: false,
    canAccessGradientScore: true,
    canSetAlerts: true,
    canEditSources: false,
    canDirectSearch: false,
    apiTokens: 0,
    description: 'Trend history access (12h+).',
    features: [
      'Gradient Score history (12h+)',
      'Trend monitoring feed',
      'Email + push alerts',
      'All signal categories',
    ],
    restrictions: [
      'Cannot access signals less than 12 hours old',
      'Cannot query new trend topics',
    ],
  },
  business: {
    id: 'business' as const,
    name: 'Business',
    price: 499,
    colour: '#00C896',
    dataFreshness: 1 * 60 * 60 * 1000, // 1h in ms
    canSearch: true,
    canQueryNew: false,
    canAccessGradientScore: true,
    canSetAlerts: true,
    canEditSources: false,
    canDirectSearch: false,
    apiTokens: 0,
    description: 'Near-real-time trend intelligence for teams.',
    features: [
      'Everything in Consumer',
      'Gradient Score history (1h+)',
      'Full signal search + filter',
      'Business analytics',
      'Team sharing',
    ],
    restrictions: [
      'Cannot access signals less than 1 hour old',
      'Cannot query new trend topics',
    ],
  },
  enterprise: {
    id: 'enterprise' as const,
    name: 'Enterprise',
    price: 25000,
    colour: '#D4A017',
    dataFreshness: 0, // real-time
    canSearch: true,
    canQueryNew: true,
    canAccessGradientScore: true,
    canSetAlerts: true,
    canEditSources: true,
    canDirectSearch: true,
    apiTokens: 1000,
    description: 'Full real-time access + live queries.',
    features: [
      'Real-time Gradient Score (live)',
      'Direct topic query (tokenised)',
      'Edit data source weights',
      'Custom alert thresholds',
      'API access',
      '1,000 query tokens/month',
    ],
    restrictions: [
      'Token-based queries (1,000/month)',
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
  | 'canDirectSearch';

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
