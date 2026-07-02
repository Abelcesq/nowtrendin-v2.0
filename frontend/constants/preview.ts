// Preview / testing-build gate.
//
// When EXPO_PUBLIC_ENTERPRISE_ONLY is truthy (set at BUILD time — Expo inlines
// EXPO_PUBLIC_* into the bundle), only accounts whose tier === 'enterprise' may
// enter the app. This is the lock for the live WEB mobile preview that current
// Enterprise accounts use for testing against the production database.
//
// The normal iOS/Android build leaves this env var UNSET, so the flag is false
// and there is no gate — mobile behavior is completely unchanged.
export const ENTERPRISE_ONLY =
  process.env.EXPO_PUBLIC_ENTERPRISE_ONLY === '1' ||
  process.env.EXPO_PUBLIC_ENTERPRISE_ONLY === 'true';
