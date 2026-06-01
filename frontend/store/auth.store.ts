import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';
import type { TierID } from '../constants/tiers';

export interface User {
  id: string;
  name: string;
  email: string;
  tier: TierID | null;
  avatar?: string;
  tokensRemaining?: number;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  setUser: (user: User, token: string) => void;
  clearAuth: () => void;
  updateTier: (tier: TierID) => void;
  decrementTokens: (count?: number) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,

  setUser: (user, token) => {
    SecureStore.setItemAsync('access_token', token).catch(() => {});
    set({ user, accessToken: token, isAuthenticated: true });
  },

  clearAuth: () => {
    SecureStore.deleteItemAsync('access_token').catch(() => {});
    set({ user: null, accessToken: null, isAuthenticated: false });
  },

  updateTier: (tier) =>
    set((s) => ({ user: s.user ? { ...s.user, tier } : null })),

  decrementTokens: (count = 1) =>
    set((s) => ({
      user: s.user
        ? { ...s.user, tokensRemaining: Math.max(0, (s.user.tokensRemaining ?? 0) - count) }
        : null,
    })),
}));
