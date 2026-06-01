// MOCK AUTH — Phase 1 only.
// Lets the full navigation flow be tested on-device without real Django endpoints.
// Replace these three functions with real calls to lib/api.ts in a later phase;
// screen code does not need to change.
import type { User } from '../store/auth.store';
import type { TierID } from '../constants/tiers';

const FAKE_TOKEN = 'mock.dev.token';

function wait(ms = 600) {
  return new Promise((r) => setTimeout(r, ms));
}

// Existing user signs in → returns a user that already has a tier → goes to dashboard.
export async function mockLogin(email: string, _password: string): Promise<{ user: User; token: string }> {
  await wait();
  return {
    token: FAKE_TOKEN,
    user: {
      id: 'u_mock_1',
      name: email.split('@')[0] || 'Member',
      email,
      tier: 'consumer', // returning member — change to test other tiers
      tokensRemaining: 0,
    },
  };
}

// New user signs up → returns a user with NO tier → routes to membership selection.
export async function mockSignup(name: string, email: string, _password: string): Promise<{ user: User; token: string }> {
  await wait();
  return {
    token: FAKE_TOKEN,
    user: {
      id: 'u_mock_new',
      name,
      email,
      tier: null,
    },
  };
}

export function tierDefaults(tier: TierID): Partial<User> {
  return tier === 'enterprise' ? { tokensRemaining: 1000 } : { tokensRemaining: 0 };
}
