/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary:   '#00C896',
        primaryDk: '#009970',
        bg:        '#07080C',
        surface:   '#111827',
        elevated:  '#1A2332',
        border:    '#1E2D3D',
        textPrimary:   '#F0F2FF',
        textSecondary: '#94A3B8',
        textMuted:     '#475569',
        consumer:   '#2D7EEF',
        business:   '#00C896',
        enterprise: '#D4A017',
        success: '#00C896',
        warning: '#D4A017',
        error:   '#DC2626',
        info:    '#2D7EEF',
        breakout:   '#00C896',
        strong:     '#2D7EEF',
        emerging:   '#D4A017',
        watching:   '#E85A1E',
        monitoring: '#94A3B8',
      },
    },
  },
  plugins: [],
};
