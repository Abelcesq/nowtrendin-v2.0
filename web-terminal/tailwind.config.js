/** @type {import('tailwindcss').Config} */
// Phase 1 (Foundations) of the 3-platform UI consistency migration (Charter §0.6).
// Tokens ported verbatim from the mobile app (frontend/tailwind.config.js) — the
// design model — plus the detection/confidence pair from mobileTheme.ts. preflight is
// OFF so the existing hand-written styles.css is left completely intact; Tailwind
// utilities are additive only. Subsequent phases migrate icons → lucide-react, then
// colors, then the dashboard, onto these shared tokens.
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  corePlugins: { preflight: false },
  theme: {
    extend: {
      colors: {
        primary: '#00C896',
        primaryDk: '#009970',
        brandMaroon: '#6E1A17',
        brandOrange: '#E8551C',
        flameGold: '#F7A41C',
        flameOrange: '#F26522',
        flameRed: '#CF2A1B',
        flameDeep: '#6E1410',
        bg: '#F4F5F7',
        surface: '#FFFFFF',
        elevated: '#FFFFFF',
        border: '#E4E7EC',
        textPrimary: '#1A1A2E',
        textSecondary: '#5B6472',
        textMuted: '#9AA3B0',
        consumer: '#2D7EEF',
        business: '#00C896',
        enterprise: '#D4A017',
        success: '#00C896',
        warning: '#D4A017',
        error: '#DC2626',
        info: '#2D7EEF',
        breakout: '#00C896',
        strong: '#2D7EEF',
        emerging: '#D4A017',
        watching: '#E85A1E',
        monitoring: '#94A3B8',
        // Detection/Confidence pair — single source of truth (mobileTheme.ts)
        detection: '#2D7EEF',
        confidence: '#00C896',
      },
    },
  },
  plugins: [],
};
