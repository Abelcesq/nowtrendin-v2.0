// Google OAuth client IDs (not secret — safe to ship in the app bundle).
// Created in Google Cloud Console → APIs & Services → Credentials.
//
// In Expo Go and on web, Google sign-in uses the WEB client via Google's proxy.
// The iOS client kicks in for standalone iOS builds.
//
// ANDROID: not created yet. An Android OAuth client needs the app's package name
// + a SHA-1 fingerprint from the signing keystore, which only exists after the
// first native build. To add it later:
//   1. Run `eas credentials` (or `eas build -p android`) to get the SHA-1.
//   2. Create an "Android" OAuth client in Google Cloud with the package name + SHA-1.
//   3. Paste the ID below and set GOOGLE_ANDROID_CLIENT_ID on the backend.
export const GOOGLE_WEB_CLIENT_ID =
  '867868141220-veodvo5i3ntj8kvt4706mjc6ilknqhlc.apps.googleusercontent.com';

export const GOOGLE_IOS_CLIENT_ID =
  '867868141220-4kl9erq1jifnl8hj9bbk4avpgloffdrt.apps.googleusercontent.com';

export const GOOGLE_ANDROID_CLIENT_ID = ''; // TODO: add after first Android build
