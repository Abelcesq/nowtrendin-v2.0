/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary:   '#00C896',
        primaryDk: '#009970',
        // Brand wordmark (maroon-orange flame palette)
        brandOrange: '#EE6A2A',
        brandMaroon: '#B5341B',
        // Light theme (matches v1.0)
        bg:        '#F4F5F7',
        surface:   '#FFFFFF',
        elevated:  '#FFFFFF',
        border:    '#E4E7EC',
        textPrimary:   '#1A1A2E',
        textSecondary: '#5B6472',
        textMuted:     '#9AA3B0',
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
