/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        // === Aurora design system ===
        // Midnight blue is the dominant brand/action color (was neon green).
        primary:   '#1B3066',
        primaryDk: '#0C1B3A',
        // Accent system: garnet red for sparing emphasis, midnight ink, single gold.
        accent:    '#B11226',
        accentDk:  '#7A0D1A',
        accentSoft:'#F0758A',
        ink:       '#16264A',
        midnight:  '#1B3066',
        indigo:    '#1A1442',
        gold:      '#C9A24B',
        goldLite:  '#E2C275',
        // Brand wordmark (matches logo PNG): "Now" maroon, "TrendIn" orange-red — UNTOUCHED
        brandMaroon: '#6E1A17',
        brandOrange: '#E8551C',
        // Flame gradient stops — UNTOUCHED
        flameGold: '#F7A41C',
        flameOrange: '#F26522',
        flameRed: '#CF2A1B',
        flameDeep: '#6E1410',
        // Canvas / surfaces — approved white system, midnight ink text
        bg:        '#FFFFFF',
        surface:   '#FFFFFF',
        elevated:  '#FFFFFF',
        // Borderless card fill — soft light gray, no outline (Apple grouped style)
        card:      '#F4F5F8',
        cardAlt:   '#EEF0F4',
        border:    '#ECECEC',
        textPrimary:   '#16264A',
        textSecondary: '#3C4663',
        textMuted:     '#9A9AA2',
        // Tier identity (gold = Enterprise, the premium tier)
        consumer:   '#2A5B9E',
        business:   '#2E7D5B',
        enterprise: '#C9A24B',
        success: '#2E7D5B',
        warning: '#C9A24B',
        error:   '#B11226',
        info:    '#2A5B9E',
        // Stage coding — jewel tones (approved)
        breakout:   '#2E7D5B',
        strong:     '#2A5B9E',
        emerging:   '#6B4FA0',
        watching:   '#A8456A',
        monitoring: '#8A8F9C',
      },
    },
  },
  plugins: [],
};
