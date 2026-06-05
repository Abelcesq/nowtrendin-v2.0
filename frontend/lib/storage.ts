import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

// Cross-platform key/value storage with the same async API as expo-secure-store.
// Native (iOS/Android): backed by the secure keychain/keystore.
// Web (browser): expo-secure-store is unavailable, so fall back to localStorage.
// This lets the SAME auth/token code run on iOS, Android, and the web platform.

const isWeb = Platform.OS === 'web';

function webGet(key: string): string | null {
  try {
    return typeof window !== 'undefined' ? window.localStorage.getItem(key) : null;
  } catch {
    return null;
  }
}

export async function getItem(key: string): Promise<string | null> {
  if (isWeb) return webGet(key);
  try {
    return await SecureStore.getItemAsync(key);
  } catch {
    return null;
  }
}

export async function setItem(key: string, value: string): Promise<void> {
  if (isWeb) {
    try {
      window.localStorage.setItem(key, value);
    } catch {
      /* quota / private mode — non-fatal */
    }
    return;
  }
  try {
    await SecureStore.setItemAsync(key, value);
  } catch {
    /* non-fatal */
  }
}

export async function deleteItem(key: string): Promise<void> {
  if (isWeb) {
    try {
      window.localStorage.removeItem(key);
    } catch {
      /* non-fatal */
    }
    return;
  }
  try {
    await SecureStore.deleteItemAsync(key);
  } catch {
    /* non-fatal */
  }
}

// Drop-in aliases matching the SecureStore method names, so call sites can
// switch with a one-line import change.
export const getItemAsync = getItem;
export const setItemAsync = setItem;
export const deleteItemAsync = deleteItem;
