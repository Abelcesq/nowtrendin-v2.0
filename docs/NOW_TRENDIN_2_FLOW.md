# Now TrendIn 2.0 — Complete Screen Flow Document
## Phase 1: Auth, Onboarding, and Membership

---

## FLOW MAP OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         APP LAUNCH                                       │
│                              │                                           │
│           ┌──────────────────┴──────────────────┐                       │
│           │ Has valid token?                      │                       │
│          YES                                      NO                     │
│           │                                       │                       │
│           ▼                                       ▼                       │
│      DASHBOARD                              SPLASH SCREEN                │
│                                                   │                       │
│                                                   ▼                       │
│                                          ONBOARDING (3 slides)           │
│                                                   │                       │
│                                           ┌───────┴────────┐            │
│                                           ▼                ▼             │
│                                         LOGIN           SIGN UP           │
│                                           │                │              │
│                                     ┌────┴──────┐         │              │
│                                   EMAIL       GOOGLE       │              │
│                                     │           │          │              │
│                                     └─────┬─────┘          │              │
│                                           │                │              │
│                                    Existing    New User?   │              │
│                                    Member?──────────────── ┘              │
│                                       │           │                       │
│                                       │    MEMBERSHIP SELECTION           │
│                                       │           │                       │
│                                       │    ┌──────┴──────────┐           │
│                                       │  CONSUMER  BUSINESS  ENTERPRISE  │
│                                       │           │                       │
│                                       │       STRIPE PAYMENT              │
│                                       │           │                       │
│                                       └─────┬─────┘                       │
│                                             │                             │
│                                        DASHBOARD                          │
│                                             │                             │
│                          ┌──────────────────┼─────────────────────┐       │
│                     HOME        SEARCH       TRENDS     ALERTS   PROFILE  │
│                  (tier-aware) (tier-gated) (tier-gated)         (settings)│
└─────────────────────────────────────────────────────────────────────────┘
```

---

## SCREEN 01: SPLASH SCREEN
**File:** `app/(auth)/splash.tsx`
**Duration:** 2 seconds, then auto-advance

### Visual Layout
```
┌─────────────────────────────┐
│                             │
│                             │
│                             │
│         [FLAME LOGO]        │  ← Animated: scale from 0.8 to 1.0
│                             │     + opacity fade in
│       Now TrendIn           │  ← Fade in 0.3s delay
│                             │
│   ATTENTION INTELLIGENCE    │  ← Fade in 0.6s delay, textMuted color
│                             │
│                             │
│                             │
│        ●  ●  ●              │  ← Loading dots, pulsing
└─────────────────────────────┘
```

### Behaviour
- Check for valid auth token on mount
- If token valid → navigate to `(app)/index`
- If no token → navigate to `(auth)/onboarding`
- First install: always go to onboarding
- Return user (has seen onboarding): go to login directly

---

## SCREEN 02: ONBOARDING
**File:** `app/(auth)/onboarding.tsx`
**Slides:** 3 swipeable slides

### Slide 1 — The Problem
```
┌─────────────────────────────┐
│                     [Skip]  │
│                             │
│   [TrendingUp icon 64px]    │
│          (green)            │
│                             │
│   The world has data.       │  ← text-2xl font-bold text-white
│   It doesn't have           │
│   foresight.                │
│                             │
│   By the time Google Trends │  ← text-base text-textSecondary
│   fires, the opportunity    │
│   is already captured.      │
│                             │
│         ●  ○  ○             │  ← slide indicator
│                             │
│      [Continue →]           │  ← primary button
└─────────────────────────────┘
```

### Slide 2 — The Solution
```
┌─────────────────────────────┐
│                     [Skip]  │
│                             │
│   [Activity icon 64px]      │
│        (green)              │
│                             │
│   Introducing the           │  ← text-2xl font-bold
│   Gradient Score.           │     text-primary
│                             │
│   The only instrument that  │  ← text-base text-textSecondary
│   measures where human      │
│   attention is moving       │
│   before it arrives.        │
│                             │
│         ○  ●  ○             │
│                             │
│      [Continue →]           │
└─────────────────────────────┘
```

### Slide 3 — Choose Your Access
```
┌─────────────────────────────┐
│                             │
│   [Building2 icon 64px]     │
│         (gold)              │
│                             │
│   Built for every           │  ← text-2xl font-bold
│   decision-maker.           │
│                             │
│   Consumer · Business ·     │  ← text-base text-textSecondary
│   Enterprise                │
│                             │
│   Three tiers. One engine.  │
│   Your competitive edge.    │
│                             │
│         ○  ○  ●             │
│                             │
│      [Get Started →]        │  ← primary button → login
│      [Sign in]              │  ← ghost button → login
└─────────────────────────────┘
```

---

## SCREEN 03: LOGIN
**File:** `app/(auth)/login.tsx`

### Visual Layout
```
┌─────────────────────────────┐
│  [←]                        │
│                             │
│   [FLAME LOGO small]        │
│                             │
│   Welcome back              │  ← text-3xl font-bold text-white
│   Sign in to Now TrendIn    │  ← text-sm text-textMuted
│                             │
│  ┌───────────────────────┐  │
│  │ [Mail] Email           │  │  ← Input component
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │ [KeyRound] Password [👁]│  │  ← Password input with Eye toggle
│  └───────────────────────┘  │
│                             │
│              Forgot password?│  ← text-primary text-sm, right-aligned
│                             │
│  ┌───────────────────────┐  │
│  │       Sign In          │  │  ← primary button, full width
│  └───────────────────────┘  │
│                             │
│    ────── or ──────         │
│                             │
│  ┌───────────────────────┐  │
│  │ [G] Continue with      │  │  ← Google OAuth button
│  │     Google             │  │     bg-surface border-border
│  └───────────────────────┘  │
│                             │
│   Don't have an account?   │
│   [Sign up]                 │  ← text-primary
└─────────────────────────────┘
```

### Validation (Zod)
```ts
schema = z.object({
  email:    z.string().email('Enter a valid email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})
```

### Error States
- Invalid credentials → inline error below button: "Incorrect email or password"
- Network error → toast: "Connection error. Please try again."
- Loading → button shows spinner + "Signing in..."

---

## SCREEN 04: SIGN UP
**File:** `app/(auth)/signup.tsx`

### Visual Layout
```
┌─────────────────────────────┐
│  [←]                        │
│                             │
│   Create your account       │  ← text-3xl font-bold
│   Join the attention        │
│   intelligence platform.    │  ← text-sm text-textMuted
│                             │
│  ┌───────────────────────┐  │
│  │ [User] Full Name      │  │
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │ [Mail] Email          │  │
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │ [KeyRound] Password   │  │
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │ [KeyRound] Confirm pw │  │
│  └───────────────────────┘  │
│                             │
│  ☐ I agree to the          │  ← Checkbox (MANDATORY)
│    Terms & Conditions       │  ← link → (app)/profile/terms
│    and Privacy Policy       │
│                             │
│  ┌───────────────────────┐  │
│  │    Create Account     │  │  ← disabled until checkbox checked
│  └───────────────────────┘  │
│                             │
│    ────── or ──────         │
│                             │
│  ┌───────────────────────┐  │
│  │ [G] Sign up with       │  │
│  │     Google             │  │
│  └───────────────────────┘  │
│                             │
│   Already have an account?  │
│   [Sign in]                 │
└─────────────────────────────┘
```

### Validation
```ts
schema = z.object({
  name:            z.string().min(2, 'Name required'),
  email:           z.string().email(),
  password:        z.string().min(8, 'Min 8 characters')
                    .regex(/[A-Z]/, 'Must include uppercase')
                    .regex(/[0-9]/, 'Must include a number'),
  confirmPassword: z.string(),
  acceptedTerms:   z.literal(true, { errorMap: () =>
                     ({ message: 'You must accept the Terms & Conditions' })
                   }),
}).refine(d => d.password === d.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});
```

---

## SCREEN 05: FORGOT PASSWORD
**File:** `app/(auth)/forgot-password.tsx`

### Step 1 — Enter Email
```
┌─────────────────────────────┐
│  [←]                        │
│                             │
│   [Mail icon 48px]          │
│         (green)             │
│                             │
│   Forgot your password?     │  ← text-2xl font-bold
│   No problem. Enter your    │  ← text-sm text-textMuted
│   email and we'll send      │
│   you a reset link.         │
│                             │
│  ┌───────────────────────┐  │
│  │ [Mail] Email          │  │
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │    Send Reset Link    │  │  ← primary button
│  └───────────────────────┘  │
│                             │
│   Back to [Sign In]         │
└─────────────────────────────┘
```

### Step 2 — Confirmation (same screen, state change)
```
┌─────────────────────────────┐
│  [←]                        │
│                             │
│   [CheckCircle 48px]        │
│         (green)             │
│                             │
│   Email sent!               │  ← text-2xl font-bold text-primary
│                             │
│   We sent a reset link to   │  ← text-sm text-textMuted
│   your.email@example.com    │
│   Check your inbox.         │
│                             │
│  ┌───────────────────────┐  │
│  │   Open Email App      │  │  ← opens mail app via Linking
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │ Resend (in 00:45)     │  │  ← disabled countdown timer
│  └───────────────────────┘  │
└─────────────────────────────┘
```

---

## SCREEN 06: MEMBERSHIP SELECTION
**File:** `app/(auth)/membership.tsx`
**Trigger:** After signup (or from Profile → Upgrade)

### Visual Layout
```
┌─────────────────────────────┐
│                             │
│   Choose your plan          │  ← text-3xl font-bold
│   Start measuring attention │  ← text-sm text-textMuted
│   intelligence today.       │
│                             │
│  ┌─── CONSUMER ───────────┐ │
│  │ [Zap] $49/month        │ │  ← border-consumer (blue)
│  │                         │ │
│  │ ✓ Gradient Score history│ │  ← Check icon (green) + text-sm
│  │ ✓ 12h+ data access     │ │
│  │ ✓ Trend monitoring      │ │
│  │ ✓ Email alerts          │ │
│  │                         │ │
│  │ ✗ Live queries          │ │  ← X icon (muted) + text-textMuted
│  │ ✗ Real-time data        │ │
│  │                         │ │
│  │ [Start Consumer Plan]   │ │  ← variant="secondary" (blue border)
│  └─────────────────────────┘ │
│                             │
│  ┌─── BUSINESS ──── ✦ ───┐  │  ← "Most Popular" badge
│  │ [Briefcase] $499/month │  │     bg-primary text-black text-xs
│  │                         │  │     border-primary (green)
│  │ ✓ Everything in Consumer│  │
│  │ ✓ 1h+ data access       │  │
│  │ ✓ Signal search         │  │
│  │ ✓ Business analytics    │  │
│  │ ✓ Team sharing          │  │
│  │                         │  │
│  │ ✗ Live real-time queries│  │
│  │                         │  │
│  │ [Start Business Plan]   │  │  ← variant="primary"
│  └─────────────────────────┘  │
│                             │
│  ┌─── ENTERPRISE ──────────┐ │
│  │ [Building2] $25K/month  │ │  ← border-enterprise (gold)
│  │                         │ │
│  │ ✓ Everything + more     │ │
│  │ ✓ Real-time live data   │ │
│  │ ✓ Direct topic queries  │ │
│  │ ✓ Source weight control │ │
│  │ ✓ API access            │ │
│  │ ✓ 1,000 query tokens/mo │ │
│  │                         │ │
│  │ [Contact for Enterprise]│ │  ← opens email / Calendly
│  └─────────────────────────┘ │
│                             │
│   All plans include:        │  ← text-xs text-textMuted
│   • Push + email alerts     │
│   • Gradient Score access   │
│   • Cancel anytime          │
│                             │
│   [Continue with free trial]│  ← ghost button — 7-day trial Consumer
└─────────────────────────────┘
```

### After plan selection → Stripe Payment Sheet
```
// Uses @stripe/stripe-react-native initPaymentSheet
// On success → navigate to (app)/index with onboarding complete flag
// Show success animation before redirect
```

---

## SCREEN 07: DASHBOARD (HOME)
**File:** `app/(app)/index.tsx`
**Varies by tier**

### Consumer Dashboard
```
┌─────────────────────────────┐
│  Now TrendIn    [Bell] [👤] │  ← header
│  ATTENTION INTELLIGENCE     │  ← text-xs text-textMuted letterSpacing
│                             │
│  ┌─────────────────────────┐│
│  │ Good morning, Abel 👋   ││  ← personalized greeting
│  │                          ││
│  │  [Zap] CONSUMER PLAN    ││  ← tier badge
│  │  Data: 12h+ only        ││
│  └─────────────────────────┘│
│                             │
│  ── RECENT SIGNALS ─────── │
│  (Showing signals ≥12h old) │  ← text-xs text-textMuted
│                             │
│  ┌─────────────────────────┐│
│  │ agentic coding    87    ││  ← SignalCard component
│  │ BREAKOUT ↑              ││
│  │ 36m ago                 ││  ← "12h+" shown if exactly at threshold
│  └─────────────────────────┘│
│                             │
│  ┌─── 🔒 LIVE SIGNAL ─────┐│  ← TierGate: blurred card
│  │ [blurred content]       ││
│  │                         ││
│  │   Live data requires    ││
│  │   Business plan         ││
│  │   [Upgrade → $499/mo]   ││
│  └─────────────────────────┘│
│                             │
│  [View All History]         │  ← → history screen
└─────────────────────────────┘
```

### Enterprise Dashboard (full access)
```
┌─────────────────────────────┐
│  Now TrendIn    [Bell] [👤] │
│  ATTENTION INTELLIGENCE     │
│                             │
│  ┌─── LIVE GRADIENT ───────┐│
│  │ ●  LIVE                 ││  ← pulsing green dot
│  │                          ││
│  │   agentic coding        ││
│  │         100             ││  ← GradientScoreRing xl
│  │      BREAKOUT           ││
│  │                          ││
│  │  DET 100  CONF 100      ││
│  └─────────────────────────┘│
│                             │
│  ── TRENDING NOW ──────────│
│                             │
│  [SignalCard] [SignalCard]  │  ← horizontal scroll
│                             │
│  ── DIRECT QUERY ─────────│
│  ┌─────────────────────────┐│
│  │ [Search] Enter topic... ││  ← Enterprise only
│  │                   [→]   ││
│  └─────────────────────────┘│
│  Tokens remaining: 847/1000 │  ← text-xs
│                             │
└─────────────────────────────┘
```

---

## SCREEN 08: SIGNAL DETAIL
**File:** `app/(app)/trends/[id].tsx`

```
┌─────────────────────────────┐
│  [←] Signal Intel           │
│                             │
│  agentic coding             │  ← text-2xl font-bold
│  Multi-Platform · 2h ago   │  ← text-sm text-textMuted
│                             │
│  ┌─── DUAL SCORE ──────────┐│
│  │                          ││
│  │   DET        CONF       ││
│  │  [  97 ]    [  94 ]    ││  ← GradientScoreRing md
│  │  /100        /100       ││
│  │  VIRAL       VIRAL      ││
│  │                          ││
│  │ 3-point gap — Both agree││
│  └─────────────────────────┘│
│                             │
│  WHAT TO DO                 │
│  ┌─────────────────────────┐│
│  │ Act now.                ││  ← text-xl font-bold text-primary
│  │ This is a Tier 1 VIRAL  ││
│  │ topic. Expert community ││
│  │ only. Window is open.   ││
│  └─────────────────────────┘│
│                             │
│  WHY THIS MATTERS           │
│  text describing the signal │
│                             │
│  WHAT TO WATCH              │
│  text with next signals     │
│                             │
│  ── SCORE BREAKDOWN ───────│
│  Signal Quality        [▼] │  ← expandable groups
│  Signal Momentum       [▼] │
│  Signal Context        [▼] │
│                             │
│  [Set Alert for this topic] │  ← primary button
└─────────────────────────────┘
```

---

## SCREEN 09: HISTORY
**File:** `app/(app)/history.tsx`
**Restricted: Consumer sees ≥12h · Business sees ≥1h**

```
┌─────────────────────────────┐
│  History         [Filter]   │
│                             │
│  [Consumer badge: 12h+ data]│  ← shown for consumer + business
│                             │
│  ── TODAY ─────────────────│
│  [SignalCard] 14h ago      │  ← within access window
│  [SignalCard] 13h ago      │
│  [SignalCard] 12h ago      │
│                             │
│  ── YESTERDAY ─────────────│
│  [SignalCard] 36h ago      │
│                             │
│  ┌─── 🔒 LIVE DATA ────────┐│  ← items < freshness threshold
│  │ 2 newer signals hidden  ││
│  │ Upgrade to Business to  ││
│  │ access 1h+ data         ││
│  │ [Upgrade →]             ││
│  └─────────────────────────┘│
└─────────────────────────────┘
```

---

## SCREEN 10: ALERTS
**File:** `app/(app)/alerts.tsx`
**Available to all tiers**

```
┌─────────────────────────────┐
│  Alerts          [+ New]    │
│                             │
│  ── ACTIVE ALERTS ─────────│
│                             │
│  ┌─────────────────────────┐│
│  │ [Bell] agentic coding   ││
│  │ Alert when score ≥ 85   ││
│  │ Email + Push            ││
│  │                [●] ON   ││  ← toggle switch
│  └─────────────────────────┘│
│                             │
│  ┌─────────────────────────┐│
│  │ [Bell] mcp              ││
│  │ Alert when score ≥ 70   ││
│  │ Email only              ││
│  │                [○] OFF  ││
│  └─────────────────────────┘│
│                             │
│  ── CREATE NEW ALERT ──────│
│                             │
│  Topic                      │
│  ┌─────────────────────────┐│
│  │ [Search] Search topics  ││
│  └─────────────────────────┘│
│                             │
│  Alert when score reaches:  │
│  ──────●───── 75           │  ← slider
│                             │
│  Notify via:                │
│  [●] Push notification      │
│  [●] Email                  │
│                             │
│  [Create Alert]             │  ← primary button
└─────────────────────────────┘
```

---

## SCREEN 11: PROFILE
**File:** `app/(app)/profile/index.tsx`

```
┌─────────────────────────────┐
│  Profile                    │
│                             │
│  ┌─────────────────────────┐│
│  │  [Avatar]               ││
│  │  Abel Johnson           ││
│  │  abel@company.com       ││
│  │                          ││
│  │  [Building2] ENTERPRISE ││  ← tier badge with colour
│  │  Member since Jan 2026  ││
│  └─────────────────────────┘│
│                             │
│  ── ACCOUNT ────────────────│
│  [User]      Edit Profile [→]│
│  [Bell]      Notifications [→]│
│  [CreditCard] Billing      [→]│
│  [Shield]    Membership     [→]│
│                             │
│  ── ENTERPRISE ─────────────│  ← only for enterprise tier
│  [Activity]  Token Usage   [→]│
│  [SlidersHorizontal] Sources[→]│
│  [Code]      API Access    [→]│
│                             │
│  ── LEGAL ──────────────────│
│  [FileText]  Terms          [→]│
│  [Lock]      Privacy Policy [→]│
│                             │
│  ── SUPPORT ────────────────│
│  [HelpCircle] Help Center  [→]│
│  [Mail]      Contact Us    [→]│
│                             │
│  [LogOut]  Sign Out         │  ← text-error
└─────────────────────────────┘
```

---

## COMPONENT SPECIFICATIONS

### SignalCard
```
┌─────────────────────────────────────────────────┐
│  [Platform icons row]              [Tier badge] │
│                                                  │
│  agentic coding              DET    CONF        │
│  Multi-Platform         [87] [84]  [38]         │
│                         ring  blue  green        │
│  → Act now — viral                              │
│    signal. Window open.                          │
│                                                  │
│  14-point gap — Very early                       │
└─────────────────────────────────────────────────┘
```

### TierGate Component
```
┌─────────────────────────────────────────────────┐
│  ░░░░░░ [blurred/grayed content] ░░░░░░░░░░░░░  │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                                  │
│              [Lock icon 32px]                    │
│                                                  │
│         Business plan required                   │
│         to access this content                   │
│                                                  │
│         [Upgrade to Business]                    │
└─────────────────────────────────────────────────┘
```

### GradientScoreRing (sizes)
```
sm:  60x60  score font-size 16  — SignalCard list item
md:  90x90  score font-size 24  — SignalCard featured
lg: 120x120  score font-size 36  — Signal detail
xl: 160x160  score font-size 48  — Dashboard hero
```

---

## TESTING CHECKLIST PER PHASE

### Phase 1 Tests
```
□ Splash shows for 2s then navigates correctly
□ Onboarding slides swipe correctly, Skip works
□ Login form validates email format
□ Login form validates password length
□ Wrong credentials show error message
□ Google login opens OAuth flow
□ Sign up requires T&C checkbox
□ T&C checkbox blocks form submission when unchecked
□ Sign up navigates to Membership after success
□ All three tier cards show correct pricing
□ Enterprise shows "Contact us" not Stripe
□ Consumer + Business open Stripe payment sheet
□ After payment → Dashboard loads
□ Forgot password shows confirmation after submit
□ Back navigation works on all auth screens
```

### Phase 2 Tests
```
□ Consumer dashboard only shows ≥12h signals
□ Business dashboard only shows ≥1h signals
□ Enterprise dashboard shows all signals
□ TierGate locks content correctly
□ TierGate Upgrade button navigates to membership
□ History screen filters by tier data age
□ Alert creation saves to backend
□ Alert toggle works
```

### Phase 3 Tests
```
□ Gradient Score ring displays correctly at all sizes
□ Score colour matches tier (green=breakout, blue=strong, etc.)
□ Signal detail shows WHAT TO DO prominently first
□ Score breakdown expands correctly
□ Enterprise sees live scores, others see historical
```

---

*This document is the authoritative screen specification for Now TrendIn 2.0*
*All screens must match these layouts before moving to next phase*
