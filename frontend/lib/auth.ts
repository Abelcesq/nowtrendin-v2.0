// Real auth — talks to the Django JWT backend (lib/api.ts).
import * as SecureStore from 'expo-secure-store';
import { api } from './api';
import type { User } from '../store/auth.store';
import type { TierID } from '../constants/tiers';

interface AuthResult {
  user: User;
  token: string;
}

function normalizeUser(u: any): User {
  return {
    id: String(u.id),
    name: u.name,
    email: u.email,
    tier: (u.tier ?? null) as TierID | null,
    tokensRemaining: u.tokensRemaining ?? 0,
    phone: u.phone ?? null,
    phoneVerified: !!u.phoneVerified,
  };
}

async function persistRefresh(refresh?: string) {
  if (refresh) {
    await SecureStore.setItemAsync('refresh_token', refresh).catch(() => {});
  }
}

export async function login(email: string, password: string): Promise<AuthResult> {
  const data = await api.post('/api/auth/login/', { email, password });
  await persistRefresh(data.refresh);
  return { user: normalizeUser(data.user), token: data.access };
}

export async function signup(name: string, email: string, password: string): Promise<AuthResult> {
  const data = await api.post('/api/auth/signup/', { name, email, password });
  await persistRefresh(data.refresh);
  return { user: normalizeUser(data.user), token: data.access };
}

// Hydrate the current user from a stored token (used on app launch).
export async function fetchMe(): Promise<User | null> {
  try {
    const data = await api.get('/api/auth/me/');
    return normalizeUser(data.user);
  } catch {
    return null;
  }
}

// Persist the chosen membership tier server-side; returns the updated user.
export async function setTier(tier: TierID): Promise<User | null> {
  try {
    const data = await api.patch('/api/auth/me/', { tier });
    return normalizeUser(data.user);
  } catch {
    return null;
  }
}

// Update name / email / phone. Returns the updated user; throws { data } on validation error.
export async function updateProfile(fields: {
  name?: string;
  email?: string;
  phone?: string | null;
}): Promise<User> {
  const data = await api.patch('/api/auth/me/', fields);
  return normalizeUser(data.user);
}

// Change password. Throws { data: { detail } } on error (e.g. wrong current password).
export async function changePassword(currentPassword: string, newPassword: string) {
  return api.post('/api/auth/change-password/', {
    current_password: currentPassword,
    new_password: newPassword,
  });
}

// Send an SMS verification code (saves the phone too). Throws { data:{detail} } / 503 if SMS unconfigured.
export async function sendPhoneCode(phone?: string) {
  return api.post('/api/auth/phone/send-code/', phone ? { phone } : {});
}

// Verify the SMS code; returns the updated (phone-verified) user.
export async function verifyPhoneCode(code: string): Promise<User> {
  const data = await api.post('/api/auth/phone/verify/', { code });
  return normalizeUser(data.user);
}

// Update notification preferences (email/push). Returns the updated user.
export async function updateNotifyPrefs(prefs: { notifyEmail?: boolean; notifyPush?: boolean }): Promise<User> {
  const data = await api.patch('/api/auth/me/', prefs);
  return normalizeUser(data.user);
}

export async function logout() {
  await SecureStore.deleteItemAsync('access_token').catch(() => {});
  await SecureStore.deleteItemAsync('refresh_token').catch(() => {});
}

export function tierDefaults(tier: TierID): Partial<User> {
  return tier === 'enterprise' ? { tokensRemaining: 1000 } : { tokensRemaining: 0 };
}
