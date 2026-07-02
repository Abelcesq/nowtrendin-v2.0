import type { CapacitorConfig } from '@capacitor/cli';

// Capacitor wraps the Expo *web* export (frontend/dist) in a native iOS WebView.
// Rebuild flow after any code change:
//   npx expo export --platform web && npx cap sync ios
//
// NOTE / known caveat: Google sign-in (expo-auth-session) relies on a browser
// redirect flow that does not complete inside a Capacitor WebView. Email +
// password login works normally. To enable Google later, swap in the
// @capacitor/browser or a native Google-sign-in plugin.
const config: CapacitorConfig = {
  appId: 'com.nowtrendin.app',
  appName: 'Now TrendIn',
  webDir: 'dist',
  // Match the app's light background so there's no white/black flash on launch.
  backgroundColor: '#F4F5F7',
  ios: {
    backgroundColor: '#F4F5F7',
    // Keep WebView content under the status bar / notch laid out sensibly.
    contentInset: 'always',
  },
};

export default config;
