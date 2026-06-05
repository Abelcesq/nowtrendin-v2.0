# CLAUDE.md — Now TrendIn 2.0
## Master Instructions for Claude Code

> This file is the single source of truth for all development decisions.
> Claude Code MUST read this file before making any code change.
> Do NOT deviate from these specifications without explicit user confirmation.

---

## 1. PROJECT IDENTITY

**App:** Now TrendIn 2.0
**Purpose:** Attention Intelligence Platform — provides the Gradient Score,
             a proprietary algorithm that measures where human attention
             is moving before it arrives.
**Tagline:** "The first instrument that measures where human attention is moving before it arrives."
**Platform:** React Native (Expo) — iOS + Android
**Backend:** Django REST API on Heroku with Postgres
**Repo:** github.com/Abelcesq/nowtrendin-v2.0

---

## 2. TECH STACK — NEVER CHANGE THESE

```
Mobile:      React Native 0.81 + Expo SDK 54   (React 19)
Routing:     expo-router (file-based, NOT React Navigation)
Styling:     NativeWind v4 (Tailwind CSS for React Native)
Icons:       lucide-react-native EXCLUSIVELY — no other icon library
State:       Zustand (global) + React Query (server state)
Auth:        Django JWT + Google OAuth via expo-auth-session
Payments:    Stripe via @stripe/stripe-react-native
Forms:       react-hook-form + zod validation
HTTP:        axios/fetch with interceptors (in lib/api.ts)
Storage:     expo-secure-store (tokens) + AsyncStorage (preferences)
Push alerts: expo-notifications
```

> **Phase 1 deviations (Expo Go compatibility):**
> - `@stripe/stripe-react-native` and `expo-notifications` push are NOT installed yet —
>   they require a custom dev client and break Expo Go. They are added in a later phase.
> - Phase 1 uses a **mock auth** flow (no real Django endpoints yet) so the full
>   navigation can be tested on a device immediately. Real JWT auth replaces the mock
>   in a follow-up step without changing screen code.

**FORBIDDEN:** Do not use:
- react-navigation (use expo-router only)
- Any icon library other than lucide-react-native
- Styled-components, emotion, or StyleSheet (use NativeWind/Tailwind only)
- Any UI component library (build from scratch with NativeWind)
- React Native Paper, NativeBase, RN Elements, etc.

---

## 3. DESIGN SYSTEM — EXACT VALUES ONLY

### 3.1 Color Tokens (tailwind.config.js)

```js
colors: {
  primary:   '#00C896',   // Now TrendIn green — buttons, accents, active states
  primaryDk: '#009970',
  brandOrange: '#EE6A2A',  // Wordmark "Now"
  brandMaroon: '#B5341B',  // Wordmark "TrendIn" (maroon-orange, matches logo N)
  bg:        '#F4F5F7',   // Page background (light grey — matches v1.0)
  surface:   '#FFFFFF',   // Cards, panels
  elevated:  '#FFFFFF',   // Modals, drawers
  border:    '#E4E7EC',
  textPrimary:   '#1A1A2E',
  textSecondary: '#5B6472',
  textMuted:     '#9AA3B0',
  consumer:    '#2D7EEF',   // Blue
  business:    '#00C896',   // Green
  enterprise:  '#D4A017',   // Gold
  success:  '#00C896',
  warning:  '#D4A017',
  error:    '#DC2626',
  info:     '#2D7EEF',
  breakout:    '#00C896',
  strong:      '#2D7EEF',
  emerging:    '#D4A017',
  watching:    '#E85A1E',
  monitoring:  '#94A3B8',
}
```

### 3.2 Typography
```
text-xs 10 · text-sm 12 · text-base 14 · text-lg 16 · text-xl 18
text-2xl 22 · text-3xl 28 · text-4xl 36 · text-5xl 48
font-normal 400 · medium 500 · semibold 600 · bold 700 · black 900
```

### 3.3 Spacing — Tailwind only (p-2..p-6, gap-2..gap-4, screen = px-5)
### 3.4 Radius — rounded-lg 8 · rounded-xl 12 · rounded-2xl 16 · rounded-full

---

## 4. ICON SYSTEM — LUCIDE ONLY

```tsx
import { TrendingUp, Lock, Bell } from 'lucide-react-native';
<TrendingUp size={20} color="#00C896" />
```
Sizes: 14 tiny · 16 small · 20 standard · 24 header · 28 large · 32 hero · 48 empty-state

Mapping: Trends→TrendingUp, History→Clock, Search→Search, Profile→User,
Alert→Bell, Lock→Lock, Consumer→Zap, Business→Briefcase, Enterprise→Building2,
Gradient Score→Activity, Breakout→Flame, Home→Home, Back→ChevronLeft, Close→X,
Check→Check/CheckCircle, Email→Mail, Password→KeyRound, Eye/EyeOff, Logout→LogOut.

---

## 5. FOLDER STRUCTURE — STRICT

```
app/
├── _layout.tsx               # Root — imports global.css, gesture handler, providers
├── index.tsx                 # Redirect → (auth)/splash or (app)
├── (auth)/
│   ├── _layout.tsx
│   ├── splash.tsx
│   ├── onboarding.tsx
│   ├── login.tsx
│   ├── signup.tsx
│   ├── forgot-password.tsx
│   └── membership.tsx
└── (app)/
    ├── _layout.tsx           # Tab bar (tier-aware)
    ├── index.tsx             # Dashboard
    ├── history.tsx
    ├── search.tsx
    ├── alerts.tsx
    └── profile/index.tsx
lib/        api.ts · auth.ts (mock for now)
store/      auth.store.ts
components/  ui/{Screen,Button,Input}.tsx · trends/TierGate.tsx
constants/  tiers.ts          # ← THE authority on access control
```

---

## 6. MEMBERSHIP TIERS — access rules live ONLY in constants/tiers.ts

| Tier | Price/mo | Data freshness | Search | New query | Sources | Tokens |
|------|----------|----------------|--------|-----------|---------|--------|
| Consumer   | $49      | ≥ 24h  | ✗ | ✗ | ✗ | 0 |
| Business   | $499     | ≥ 12h  | ✓ | ✗ | ✗ | 0 |
| Enterprise | $250,000 | live   | ✓ | ✓ (1 token/search) | ✓ | 10000 (5 users, shared) |

Use `canAccess(tier, feature)` and `isDataAccessible(tier, dataAgeMs)` everywhere.
Never hardcode a tier check anywhere else.

**Data-aging waterfall:** a new score is Enterprise-only at first (live, the moment
it is obtained) → at 12 h it becomes visible to Business → at 24 h to Consumer →
(future) at 1 day+ to partners. X data is pulled twice daily (1am & 1pm Pacific)
to feed the 12 h Business window. Consumer/Business cannot run queries; Enterprise
can run direct queries at 1 token per search.
Enforced purely by `dataFreshness` + `isDataAccessible(tier, age)` on the score's age.
**Retention:** engine persists all scores in Postgres (≥30-day history); monthly
research snapshots for a year are a planned backend job.

---

## 7. MANDATORY PATTERNS
- Every screen wrapped in `<Screen>` (components/ui/Screen.tsx)
- Every button is `<Button variant size>` — never raw styled TouchableOpacity
- Every restricted region wrapped in `<TierGate>`
- The Gradient Score hero is `<GradientScoreRing>` (Phase 3)

---

## 8. TERMS & CONDITIONS — MANDATORY CLAUSE
All users must accept at signup (checkbox blocks submit):
"All Gradient Score results, trend analyses, signal data, and any information
generated by or accessed through the Now TrendIn platform are proprietary to
Now TrendIn LLC. Users have no ownership rights to any data, scores, analyses,
or results obtained through the platform."

---

## 9. PHASES — DO NOT SKIP
1. **Auth + onboarding + membership shell** (mock auth) ← CURRENT
2. Dashboard + tier-restricted nav (TierGate + age filtering)
3. Gradient Score display (rings, signal cards, breakdown)
4. Search + alerts + push
5. Enterprise direct-query + token deduction + source editor

---

## 10. MEMORY CHECKPOINTS — verify before each change
1. lucide-react-native for ALL icons?
2. NativeWind/Tailwind for ALL styling?
3. expo-router for ALL navigation?
4. Tier logic in constants/tiers.ts only?
5. Restricted features use TierGate?
If any answer is NO — stop and fix.

---

## 11. THEME — light (matches v1.0). bg #F4F5F7, surface #FFFFFF (white cards w/ soft shadow),
dark text #1A1A2E. Green #00C896 = accents/active states. Wordmark: "Now" brandOrange + "TrendIn"
brandMaroon. Flame logo preserved from v1.0 — rendered via components/ui/Logo.tsx (SVG stand-in;
swap for the original logo.png in assets/ when available). StatusBar = dark-content.

*Last updated: Now TrendIn 2.0 — Phase 1 (SDK 54, mock auth)*
