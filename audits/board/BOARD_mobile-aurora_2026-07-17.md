# BOARD REVIEW — Mobile Platform (Aurora) analysis + recommendations
**Date:** 2026-07-17 · **Convened by:** founder · **Material:** `frontend/` (~30 screens),
audience = CONSUMER $49 / BUSINESS $499 (retail — the most bias-prone population).
Six independent memos, identical evidence pack, source-verified (no cross-contamination).

## DECISION TABLE

| Item | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist |
|---|---|---|---|---|---|---|
| A — design/UX | AWC | APPROVE | AWC (store path) | APPROVE | AWC (ship 2 now) | AWC |
| B — display integrity | **REJECT** | AWC | APPROVE (en-first) | AWC | APPROVE | AWC |
| C — store readiness | **REJECT (fix B first)** | AWC | AWC | **REJECT (not yet)** | SHIP-LATER | AWC |

**Overall tone:** "Honest bones, mania dressing" (Economist). Aurora itself is strong
(gold hero 9.9:1; coherent identity); profile/accuracy.tsx was called "the most honest
retail ledger I've seen." The defects are copy/label/fallback-level — none touch the
engine — but four are FALSE DISPLAYS and one is billing-adjacent.

## P0 — FALSE DISPLAYS (the convergent core; every fix is small)
1. **`dataWindowLabel` falsehood (4 independent confirmations — billing-adjacent).**
   `lib/signals.ts:568` hand-codes Consumer "1h+ data" / Business "30m+ data"; the real
   contract gates are 24h/12h (a 24× understatement, rendered on dashboard + category
   screens). FIX: derive from `TIERS[tier].dataFreshness` (LockedSignalsBanner already
   does it correctly). "Which is true — the 24-hour delay we sell or the 1h+ label we
   display?" (Outsider, point-blank).
2. **`breakdownGroups()` fabrication (no-fabrication principle).** `lib/signals.ts:539`
   invents component values (Velocity=score+6, Novelty=100−score+20…) rendered as real
   on ANY row lacking engine `groups` — not just mocks. FIX: delete the arithmetic
   fallback; absent components render nothing (§17).
3. **Mock-fallback quarantine.** Sample mode fabricates freshness ("Updated 22m ago"),
   populates the hero, and detail screens ignore `isSample` entirely; no banner during
   load. FIX: sample rows carry no fabricated timestamps, detail inherits the sample
   banner, hero labeled ILLUSTRATIVE in sample mode.
4. **"Ranked by our Gradient Score" copy over the N-ranked default** (where N=100 walls
   dominate and true order is feedRank). FIX: copy tells the truth per view; mark
   saturated N as "100 · max".
5. **Monetization integrity (3 memos):** membership self-select GRANTS any tier —
   including a free $250k Enterprise — with no payment behind "cancel anytime · free
   trial · push+email alerts" claims; signup Terms checkbox never shows the §8 clause.
   FIX now: Enterprise → "Contact sales"; unbacked claims removed; §8 text in the flow.

## P1 — MEASUREMENT-NOT-ADVICE COPY (Guardian + Economist, retail lens)
"TODAY'S #1 PICK" → "SIGNAL" · "leads/led the market" → "leads Google Trends attention"
(the attention ledger is not price-validated) · engine `what_to_do` verbatim in the hero →
"Signal read" + imperative guard · headline counts only stage-true movers (not all 3,109
incl. MONITORING) · tier-conditional intro (no "right now" claims over 24h-old data) ·
"24–72h to alignment" unsupported forecast removed · upward-only alerts gain
"falls below" · surface "Our track record →" on the dashboard (make the ledger loud).

## P2 — AURORA HYGIENE + DISCLAIMERS
SignalAnalysisPanel is a pre-Aurora fossil (banned #00C896 icon, bordered card, sub-12px
text; renders on crypto/[coin] + ledger rows — pack's location was corrected by the
Executioner): exact ~30-min retrofit specced. Disclaimer gaps: dashboard (GradeTool AI
output), search, category/[stage], market-category/[key]; the Disclaimer component's own
text measures 2.79:1 — legibility fix. 12px muted text failures: inactive tabs 2.02:1,
sample banner 2.56:1. Casing-dictionary port from web specced into lib/signals.ts
(honest note: it does NOT fix "Mcgregor" — surname casing is engine-side if ever; CUT).

## P3 — STORE PATH (closer than assumed) + PERF
No dependency currently forces a custom dev client; bundle IDs/EAS project exist; the
enterprise preview gate is verified OFF for native. Real blockers are decisions, not
code: (a) monetization vs Apple 3.1.1/Play Billing — the Executioner recommends
WEB-SIGNUP + app-login (delete in-app Stripe entirely); (b) missing eas.json,
expo-dev-client/notifications deps, splash; `userInterfaceStyle:"dark"` wrong for light
Aurora; `supportsTablet` → false for v1. KILL the rival Capacitor track (Guideline 4.2
risk + breaks Google OAuth). Perf at 100×: FlashList virtualization, capped prefetch +
server-side filter, a single-topic endpoint (prerequisite for push), poll jitter.
Localization: freeze strings into one module; defer i18n (content is English anyway).

## DISAGREEMENTS
- Severity spread on B: Challenger REJECT vs others AWC/APPROVE — same facts, different
  weight on the falsehoods.
- Disclaimer coverage: Executioner "verified everywhere" vs Guardian's specific gap list
  (dashboard/search/category) — reconcile during the fix pass.
- The pack itself erred once (SignalAnalysisPanel's location) — corrected in-review.

## CUT LIST (Executioner)
Capacitor track · in-app Stripe before the payments decision · surname casing ·
Collapsible retrofit of the analysis panel · dark theme · web-density chasing.
CLAUDE.md §3/§11 doc-debt = ship-later but flagged: it still teaches agents the neon
palette — the exact leak vector the two-dialects ruling guards against.

## ARCHETYPE MEMOS (verbatim)

---

# BOARD MEMO — The Challenger — Mobile (Aurora) Review, 2026-07-17

Role: adversarial accuracy/readability skeptic. I read the source, not the pack's summary.
Every claim below cites file:line in `frontend/`. Contrast ratios computed (WCAG relative
luminance, exact).

---

## HEADLINE: two findings that are not style debates — they are false statements to paying users

### F1. The app tells the Consumer tier "1h+ data" while gating them to 24h+ (and Business "30m+" vs actual 12h)

`lib/signals.ts:568-573`:

```ts
export function dataWindowLabel(tier: TierID): string {
  if (tier === 'enterprise') return 'Live + full history';
  if (tier === 'business') return '30m+ data';
  return '1h+ data';
}
```

`constants/tiers.ts:10,38` — the actual enforcement (`isDataAccessible`):
Consumer `dataFreshness: 24h`, Business `12h`. CLAUDE.md §6 agrees with tiers.ts (≥24h / ≥12h).

This label RENDERS in three places: the Market Signals list subtitle
(`app/(app)/index.tsx:482`), the category page header (`app/(app)/category/[stage].tsx:48`),
and the market-category page (`app/(app)/market-category/[key].tsx:56`). A $49 subscriber is
told their data window is "1h+" when the gate actually withholds everything younger than 24
hours — a 24× misstatement of the product's central freshness promise, on the surface where
freshness IS the product ("before it arrives"). Business is a 24× misstatement too (30m vs
12h). Whichever number is the intended truth, one of `tiers.ts` and `dataWindowLabel` is
lying to users right now. This is not a design nit; it is a misrepresentation of a paid
tier's core entitlement, adjacent to refund/FTC territory.

### F2. The "Score breakdown" fabricates component values by arithmetic and presents them as measurements

`lib/signals.ts:540-560` — `breakdownGroups()` fallback when the engine sends no `groups`:

```ts
{ label: 'Velocity', value: clamp(s.score + 6) },
{ label: 'Acceleration', value: clamp(s.score - 8) },
{ label: 'Volume', value: clamp(s.detection - 3) },
{ label: 'Cross-platform', value: clamp(s.confidence + 5) },
{ label: 'Novelty', value: clamp(100 - s.score + 20) },
{ label: 'Saturation', value: clamp(s.score - 15) },
{ label: 'Source spread', value: clamp((s.detection + s.confidence) / 2 - 4) },
```

These are invented numbers — score±constants — rendered on the detail screen under
"Score breakdown · The components behind the score" (`app/(app)/signal/[id].tsx:96,249-259`)
with NO marker distinguishing them from real engine components. This is not confined to the
mock dataset: ANY live row that arrives without `groups` gets a fabricated component panel.
"Velocity 93" that is literally `score+6` violates the platform's first principle (no
fabricated data) and §17's spirit (never imply a component informed the read when it did
not). A hedge-fund counsel would call this manufactured evidence. Delete the fallback or
label it "illustrative — components unavailable"; better, render nothing (§17 already says
omit what doesn't contribute).

---

## (2) The mock-data fallback — can a $49 subscriber mistake sample for live? YES, four ways

Read `hooks/useSignals.ts` + `app/(app)/index.tsx` + `app/(app)/signal/[id].tsx`:

- **The banner is below the fold of the lie.** The sample hero card — gold 44px score,
  "TODAY'S #1 · NOWTRENDIN PICK" — renders at index.tsx:247-270. The banner ("Showing sample
  data — live engine unreachable", index.tsx:318-322) renders AFTER the hero, two chip rows,
  and the search box, as one 12px line in muted grey `#9A9AA2` on `#F4F5F8` — **2.56:1
  contrast** (AA floor is 4.5:1). The most prominent element on the screen is fake; the
  correction is the least prominent element on the screen.
- **During initial load there is no banner at all.** `isSample = !live && !q.isLoading`
  (useSignals.ts:43), and `signals` returns `MOCK_SIGNALS` whenever no page has landed
  (line 40). The hero, the "N Trends Are Heating Up!" headline, and the chip counts all sit
  OUTSIDE the `isLoading` ternary (index.tsx:205-307) — so on every cold start every user
  briefly sees a mock hero and mock counts with zero disclosure.
- **The detail screen has no sample state whatsoever.** `useSignal` returns `isSample`
  (useSignals.ts:55) but `signal/[id].tsx:69` destructures only `{ signal, isLoading }`. Tap
  a sample row → a full "SIGNAL INTEL" screen: rings, stage badge, N section, and the F2
  fabricated breakdown — presented identically to live data.
- **Fabricated freshness.** `lastUpdated` (index.tsx:74) reads mock `createdAt`, which is
  stamped relative to `now` at module load (signals.ts:415-429) — so an unreachable engine
  shows "UPDATED 22M AGO" for an Enterprise user. A freshness claim manufactured out of
  nothing, directly under the tier badge.
- Bonus incoherence: mock rows have no `nowTrending`, and the default view ranks by N — so
  sample mode's hero proudly displays **"0 N"** in gold.

Verdict on the banner question asked of me: **not remotely sufficient.** The honest designs
are (a) an empty state ("Engine unreachable — pull to retry") or (b) a persistent full-width
banner + watermark on every derived surface including detail. Ten realistic topic names with
plausible scores and a live-looking timestamp is a simulation of the product, and the current
disclosure is one low-contrast whisper on one of the three surfaces that render it.

## (1) N=100 saturation as the default hero/rank driver

Default view is `nowtrendin` (index.tsx:44), ranked and headlined by N. The codebase itself
testifies (signals.ts:189-192): "**N saturates at 100 for many topics, so ties dominate the
visible list**" — ordering within the wall of 100s comes from a hidden `feedRank`. So the
consumer's default screen is: gold hero "100 N", then rows "01 100 N, 02 100 N, 03 100 N…"
where the visible metric explains nothing about the visible order. Two honesty problems:
(a) a displayed rank driver that cannot reproduce the displayed rank is a fake explanation —
the real key is undisclosed; (b) N is self-referential ("how often OUR users query it",
signal/[id].tsx:151-155) — fine as a labeled lens, but as the DEFAULT consumer ranking it
leads with the platform's own popularity loop rather than the measured Gradient Score the
marketing line above it promises ("ranked by our Gradient Score", index.tsx:244-246 — which
is itself FALSE in the default view: it's ranked by N, not the Gradient Score). Fix: either
default to All Signals/Detection, or de-saturate N's display (show the tie-break metric as a
secondary number), and correct the intro copy per-view.

Also in this family: `gapInsight` (signals.ts:407-411) prints "Confirmation building —
**24–72h to alignment**" on every non-aligned card (TrendCard.tsx:113-115). Where does 24–72h
come from? No ledger citation, no per-topic basis — an invented precision window that reads
as a forecast. Measurement-not-advice says delete the number or back it with ledger data.

## (3) Contrast — computed worst ratios (AA normal-text floor 4.5:1)

| Element | Pair | Ratio |
|---|---|---|
| Inactive tab labels TRENDS/MARKET/CRYPTO/GRADE, 12px (index.tsx:236) | #B6B6BD / #FFF | **2.02** |
| Chip count badges, 12px (index.tsx:302) | #9A9AA2 / #F1F1F4 | **2.48** |
| Sample-data banner, 12px (index.tsx:320) | #9A9AA2 / #F4F5F8 | **2.56** |
| textMuted everywhere — "Updated", meta rows, **the legal Disclaimer itself** (Disclaimer.tsx:8) | #9A9AA2 / #FFF | **2.79** |
| Expand chevron (TrendCard.tsx:85) | #C7C7CE / #FFF | 1.68 (decorative, tolerable) |
| Hero gold 44px score | #E2C275 / #0C1B3A | 9.90 ✓ |
| Hero eyebrow pink 12px | #F0758A / #1B3066 | 4.58 (passes by 0.08 — fragile) |

The jewel palette and the gold-on-midnight hero are FINE — the failure is systemic use of
`textMuted #9A9AA2` at 12px for load-bearing text. Two of the worst offenders are exactly the
things that must be legible to function: the sample-data disclosure (2.56) and the
founder-mandated legal disclaimer (2.79). A disclaimer rendered below the accessibility floor
is a disclaimer a plaintiff's lawyer will argue was designed not to be read. Fix: darken
muted to ~#6E7280 for functional text, or bump these specific elements to textSecondary
(#3C4663 = 9.34 ✓). Also: app-store accessibility review risk.

## (4) SignalAnalysisPanel — the whole panel is a pre-Aurora fossil, not one hex

`components/trends/SignalAnalysisPanel.tsx`, used on signal/[id] AND risk/[key]:
- line 47: banned neon `#00C896` icon (the known one);
- line 45: `border border-border bg-surface` — a BORDERED card on a contract that says
  "no border outlines, ever" (§3), using the pre-Aurora `surface` token;
- lines 49, 63, 73, 79: `text-[11px]` and `text-[10px]` — below the contract's hard 12px
  type floor (§2), including the disclaimer at 10px;
- line 54: spinner `#9AA3B0` — the OLD palette's muted grey, not Aurora's;
- no `<Card>`, no `<Collapsible>`, no Rise motion — none of the §5 primitives;
- its disclaimer is server-optional and bottom-only (line 78), while the founder rule and
  the sibling screens (signal/[id].tsx:121-122, risk/[key].tsx:118,535) require the verbatim
  disclaimer top AND bottom.
So the "one banned hex" in the audit pack undercounts: this component violates §1, §2, §3,
§4 and §5 simultaneously. Rebuild it on the primitives; it's ~85 lines.

## (5) Title Case miscasing

`titleCaseTopic` (signals.ts:501-513) preserves interior caps but blindly capitalizes
lowercase engine strings: "mcgregor"→**Mcgregor**, "agi"→**Agi**, "openai"→**Openai**,
"iphone 17"→**Iphone 17** — at 28px on the hero and detail title. On a consumer product,
28px typos read as machine-generated sloppiness and directly undercut the "we measure
attention precisely" brand claim. The web already shipped an acronym/brand dictionary; mobile
rendering the SAME topics differently is also a frontend-consistency (§12) breach. Port the
dictionary into `titleCaseTopic` — one file, shared by all call sites.

Minor: `maturityColourHex` comment says "gold" for RESURGENT but returns rose #A8456A
(signals.ts:53) — dead comment, fix in passing.

---

## VERDICTS

**(A) Design/UX — APPROVE WITH CONDITIONS.**
Aurora is genuinely strong for this audience: the hero-first journey, progressive
disclosure, calm rows, and the 9.9:1 gold hero are excellent consumer design. Conditions:
(1) raise all functional 12px muted text to ≥4.5:1 (tabs, counts, banner, disclaimer);
(2) rebuild SignalAnalysisPanel on the Aurora primitives; (3) ship the title-case
dictionary. Strongest attack: the design system's own floor (12px, readable) is violated by
its own legal fine print at 2.79:1. Mind-changer: a device screenshot showing #9A9AA2 12px
is comfortably legible on target hardware would soften (not remove) the contrast condition —
WCAG would still fail.

**(B) Display integrity — REJECT (fix, then fast re-review).**
Strongest attack: the app currently makes four flatly false or unfalsifiable statements to
paying users — "1h+/30m+ data" vs the enforced 24h/12h gate (F1); arithmetic component
scores presented as measurements (F2); "ranked by our Gradient Score" over an N-ranked list;
and, when the engine is down, a live-looking hero + "Updated 22m ago" with a 2.56:1 whisper
of a banner and an undisclosed sample detail screen. Each alone is against the foundational
principles; together they are disqualifying for the accuracy-above-all brand. Mind-changer:
nothing changes my mind about F1/F2 — they are objectively false displays; showing me that
`groups` is always present in live payloads would downgrade F2 from "live fabrication" to
"sample-mode fabrication" (still a fix, lower severity). All five fixes are small
(one function, one fallback deletion, one banner redesign, one copy line, one destructure).

**(C) Store-readiness — REJECT for submission now.**
Not close yet, and not only because Stripe/push are deferred (phase 8). App review will
exercise the app against a flaky network — reviewers will meet the mock fallback; if they
recognize placeholder data presented as live financial-adjacent intelligence, that's a
4.2/2.3.1 rejection risk and, worse, a first-session trust kill for real users. Blockers in
order: B-fixes (F1 first — it is a billing-adjacent misstatement), mock-fallback quarantine,
disclaimer legibility, contrast pass, then payments/push off Expo Go. Mind-changer: none
until B clears; after B, a TestFlight/closed-track period with the fallback exercised would
earn conditional approval.

## PRIORITIZED FIXES (all small)
1. `dataWindowLabel` → derive from `TIERS[tier].dataFreshness` (single source of truth —
   the file header of tiers.ts already commands this). ~3 lines.
2. Delete/label the synthetic `breakdownGroups` fallback; render nothing per §17. ~15 lines.
3. Mock fallback: suppress hero/headline/counts in sample+loading states OR full-width
   persistent banner + sample marker on detail (wire `isSample` into signal/[id]). Kill the
   fabricated "Updated" label in sample mode.
4. Fix the intro copy per view ("ranked by N" when N-ranked); show tie-break metric among
   the 100s or default to Detection.
5. Disclaimer + sample banner + tabs + counts to ≥4.5:1.
6. Rebuild SignalAnalysisPanel (Aurora tokens, 12px floor, borderless, verbatim disclaimer
   top+bottom, not server-optional).
7. Title-case dictionary shared with web; remove "24–72h to alignment" or back it with
   ledger data.

— The Challenger

---

# BOARD MEMO — First-Principles Guardian
## Mobile (Aurora) audit vs the irreducible claim, 2026-07-17

**The claim being defended:** *we measure where attention is moving before it arrives, proven by a
held-out never-deleted ledger; measurement, NOT advice.* The mobile audience is the $49 Consumer —
the user MOST likely to read a measurement as a recommendation. Every finding below is judged
against that single principle.

All paths relative to `frontend/` (repo: `C:\Users\acinv\OneDrive\Desktop\CODING PROJECTS\NowTrendin v2.0\frontend`).

---

## 1. Prescriptive surfaces (measurement-into-advice)

### 1a. `whatToDo` / `actionFor` — the pass-through is the risk, not the fallback
- `lib/signals.ts:519-537` — the LOCAL fallback `ACTIONS` map is exemplary: every stage read is
  descriptive ("Breakout in progress.", "Attention falling."), and the code comment says so
  explicitly: *"Descriptive 'signal read' per stage — analysis only, no action guidance."*
- **But** `actionFor()` (line 532) prefers the ENGINE's `what_to_do_action` /
  `what_to_do_instruction` / `what_to_do_detail` (`lib/gradientApi.ts:88-94`) and renders it
  VERBATIM in the primary score card (`app/(app)/signal/[id].tsx:144`). The mobile client has no
  neutrality guarantee on that text; the field's very name ("what to do", "instruction") is
  prescriptive lineage. A Consumer reading an imperative sentence inside the hero score card will
  read it as instruction from the instrument.
- **Required:** (i) rename the concept on all surfaces to "Signal read" (server field can stay for
  compat); (ii) engine-side style contract: the text must describe the signal's state, never
  command the user; (iii) client-side belt-and-suspenders — if the served title is imperative
  ("Act now", "Watch closely", "Get in early"), fall back to the descriptive `ACTIONS[stage]`.

### 1b. "TODAY'S #1 · NOWTRENDIN PICK" — the single worst word in the app
- `app/(app)/index.tsx:254`. "PICK" is recommendation vocabulary (stock-pick, editor's pick). On a
  gold-lit hero card above a 44px score, a $49 retail user reads "our pick" = "what to buy/follow".
  This is the one place mobile crosses the line outright.
- **Required rewording:** "TODAY'S #1 SIGNAL" or "HIGHEST GRADIENT TODAY". Nothing else on the
  card needs to change — the measurement itself is the headline.

### 1c. "Heating Up!" / "Moving!" urgency headers
- `app/(app)/index.tsx:207,211,215` — "{n} Trends Are **Heating Up!**", "{n} Market Signals Are
  **Moving!**", "{n} Coins Are **Moving!**" in accent red #B11226.
- Two problems compound for the Consumer: (i) exclamation-point urgency is emotional framing, not
  measurement; (ii) for the Consumer tier every one of those rows is **≥24 hours old** by design —
  "are heating up (now)!" over day-old data is a present-tense claim the data does not support.
- **Required:** present-tense-neutral, no exclamation: "{n} Trends Rising" / "{n} Signals Above
  Baseline" / "{n} Coins Tracked" — or keep energy but anchor the tense to the tier's data window
  ("{n} trends rose in your data window"). The adjacent "Updated {lastUpdated}" line (line 224) is
  honest (it reads the newest ACCESSIBLE row) — good; keep it beside any headline.

### 1d. "Set an alert for this topic" (`signal/[id].tsx:307-316`)
- **Acceptable as-is.** An alert is a measurement-delivery mechanism ("tell me when the number
  changes"), not advice. It is followed immediately (line 318-320) by "Signal analysis only — not
  financial, investment, or legal advice. You decide any action." This is the correct pattern.

### 1e. Ledger overclaim copy (`app/(app)/profile/accuracy.tsx`)
- Line 137: "The auditable proof that the Gradient Score **leads the market**." The attention
  ledger validates lead vs **Google Trends attention**, not vs any market/price. "Market" here
  imports a financial meaning the data does not carry.
- Lines 309-310 (empty state): "the days you led the market — the proof asset for institutional
  clients" — internal marketing language leaked into consumer UI, same "market" overclaim.
- **Required:** "…detected a topic before it broke out on Google Trends — the auditable record
  that the Gradient Score leads public attention." Reserve "market" for the money/crypto ledgers,
  which really are price-validated.

### 1f. Clean surfaces (for the record)
- `SCORE_ROLES` who-text, maturity explains, entity-group copy, `DECAY`/`MONITORING` reads,
  market hero narrative fallback ("Unusual positioning vs its baseline") — all descriptive. The
  dashboard tagline "surfaced before it hits the mainstream" (index.tsx:245) is the product claim
  itself, backed by the ledger — permissible.

## 2. Disclaimer coverage (founder verbatim copy, top AND bottom of analysis panels)

Component: `components/ui/Disclaimer.tsx` — verbatim, founder-locked. Coverage found:

| Surface | Status |
|---|---|
| `signal/[id].tsx` | ✓ top (122) + bottom (322) — exemplary |
| `crypto/[coin].tsx` | ✓ top (82) + bottom (203) |
| `risk/[key].tsx` | ✓ top (119) + bottom (536) |
| `history.tsx`, `alerts.tsx`, `profile/methodology.tsx`, `profile/legal.tsx` | ✓ bottom |
| `profile/accuracy.tsx` | **bottom only (315) — missing the top instance** the founder rule requires |
| **`app/(app)/index.tsx` (dashboard)** | **✗ verbatim absent.** Only a paraphrase at 508-511 ("informational purposes only… All decisions are your own"). The dashboard is the highest-traffic analysis surface (hero score, ranked lists, market narratives) — and it hosts **GradeTool**, an AI-generated analysis with NO disclaimer anywhere near it (`components/trends/GradeTool.tsx`: zero matches). |
| `search.tsx` | ✗ none — renders scored trend + market results |
| `category/[stage].tsx`, `market-category/[key].tsx` | ✗ none — ranked score lists |
| `watchlists.tsx`, `favorites.tsx` | ✗ none (list-only; lower stakes but same scores) |
| `SignalAnalysisPanel.tsx` | conditional only — renders `a.disclaimer` IF the engine sends one (78-80); a payload without the field shows an AI-shaped analysis with no disclaimer. Should compose `<Disclaimer/>` unconditionally beneath. |

**Required:** verbatim `<Disclaimer/>` on the dashboard (replacing or supplementing the
paraphrase — a paraphrase of founder-locked legal copy is itself a drift risk), on search and both
category screens, top-of-panel instance on accuracy.tsx, and unconditional in SignalAnalysisPanel.
That closes every gap with one imported component — trivial diff, real legal surface.

## 3. Mobile ledger honesty (`profile/accuracy.tsx`) — the moat, correctly displayed

- **Blended AND tracked-race:** ✓ both metrics side-by-side (HIT RATE + TRACKED-RACE, lines
  208-209), mapped camelCase-first with snake_case fallbacks (`gradientApi.ts:598-600` — the
  2026-07-06 zeroing bug stays fixed).
- **Nothing hidden:** ✓ full breakdown line (led · same-day · near-miss · pre-broken · false
  positives, line 218-220) — false positives displayed to the paying user, which is exactly what
  a never-deleted ledger demands.
- **Pending in-flight:** ✓ "{n} pending detections still in flight — 365-day patience window"
  (224-228).
- **Pre-broken:** ✓ plain-English definition (229-233) states it STAYS counted in the honest rate;
  server-computed flag, one grace definition.
- **Referee honesty:** ✓ `refereeLine` renders "referee unchecked" for pre-metadata wins — never
  implies verification that didn't happen (83-88); LED referee tallies shown (221-223).
- **Gap:** the epoch/param stamp (`param_version`, e.g. `calib-params-v2-patience365`) is not
  parsed in `fetchAccuracy` and not displayed. A rate without its parameter epoch is a number that
  can silently change meaning across recalibrations. **Condition:** surface a one-line
  "methodology {param_version} · report {asOf}" caption under the metric tiles.
- Also fix the 1e copy overclaims above. Otherwise this screen is the most honest consumer-facing
  accuracy display I have reviewed on any platform of this product.

## 4. Tier data-aging honesty — one outright falsehood

- The gate itself is principled: `constants/tiers.ts:120-121` single-sources it;
  `filterFeed` ages on **first-seen** (`lib/signals.ts:440-446`) so a re-scored topic can't
  re-lock; dashboard/search/market-category all filter through `isDataAccessible`.
- `LockedSignalsBanner` (components/trends/LockedSignalsBanner.tsx) is honest by construction —
  it DERIVES the freshness label from `TIERS[next].dataFreshness` "so it never drifts from
  constants/tiers.ts", and tells the user "{n} newer signals hidden". Correct pattern.
- Per-row `ageLabel` + header "Updated {lastUpdated}" (from newest accessible row) — honest.
- **VIOLATION:** `dataWindowLabel` (`lib/signals.ts:568-572`) returns **"1h+ data"** for Consumer
  and **"30m+ data"** for Business — rendered on the dashboard Market Signals header
  (`index.tsx:482`). The real windows are **24h and 12h**. This tells a $49 user their data is
  ~24× fresher than it is — a factual freshness misstatement in the exact place the tier price is
  justified, and it contradicts the LockedSignalsBanner one scroll below. Stale label from an old
  freshness scheme; it hardcodes what the banner correctly derives.
- **Required (blocking):** derive `dataWindowLabel` from `TIERS[tier].dataFreshness` ("24h+ data" /
  "12h+ data" / "Live"), or delete it and reuse the banner's derivation. One function, five lines.

---

## VERDICTS (per the pack's A/B/C)

**(A) Design/UX for the consumer audience — APPROVE.**
Principle: *lead with the answer, hide depth, let the user decide.* The Aurora detail screen is a
model of progressive disclosure with the disclaimer sandwich done right; urgency language is a
copy problem (B), not a structural one.

**(B) Integrity / measurement-not-advice — APPROVE-WITH-CONDITIONS.**
Principle: *an instrument reports; the moment it recommends, the ledger stops being a defense and
becomes marketing.* Conditions, in order: (1) fix `dataWindowLabel` (the one factual falsehood);
(2) "PICK" → "SIGNAL"; (3) verbatim Disclaimer on dashboard/GradeTool/search/category +
accuracy top + unconditional in SignalAnalysisPanel; (4) neutralize "Heating Up!/Moving!" or
anchor them to the tier window; (5) "leads the market" → "leads Google Trends attention" in the
attention-ledger copy; (6) whatToDo rename + imperative guard.

**(C) Store-distribution readiness — APPROVE-WITH-CONDITIONS.**
Principle: *never ship a claim you cannot defend to a regulator reading over a consumer's
shoulder.* Items (1)-(3) of (B) are pre-store blockers — each is a small diff; none touches
scoring. The ledger screen (item 3 above) is store-ready today and is the strongest honest
differentiator the app has; add the param-epoch caption so the number it shows stays pinned to the
methodology that produced it.

— First-Principles Guardian

---

# BOARD MEMO — The Expansionist (Global Scale) — Mobile Platform Review
**Date:** 2026-07-17 · **Scope:** `frontend/` judged for store distribution, localization, 100× performance, one-codebase reach.
**Evidence:** app.json, package.json, capacitor.config.ts, constants/preview.ts, constants/google.ts, lib/useGoogleAuth.ts, lib/gradientApi.ts, hooks/useSignals.ts, app/(app)/index.tsx, app/(auth)/membership.tsx, app/(app)/profile/billing.tsx, lib/signals.ts, assets/.

---

## 1. STORE-DISTRIBUTION PATH — what actually blocks a submission today

**What is already in place (closer than the "phase 8 deferred" framing implies):**
- `app.json` has real bundle identity: `com.nowtrendin.app` (iOS + Android), scheme `nowtrendin`, an EAS `projectId` (`ef045a1d-…`), full Android adaptive-icon set, 384KB icon. The account plumbing for `eas build` exists.
- No forbidden-in-Expo-Go native modules in `package.json` — no `@stripe/stripe-react-native`, no `expo-notifications`, no `expo-dev-client`. Meaning: **nothing in the current dependency tree requires a custom dev client.** The app as it stands could be built with plain `eas build` today; the custom-dev-client need only materializes when Stripe/push are added (phase 8), exactly as CLAUDE.md says.
- **Enterprise preview gate is correctly OFF for native** (`constants/preview.ts`): `ENTERPRISE_ONLY` is true only when `EXPO_PUBLIC_ENTERPRISE_ONLY` is explicitly `'1'`/`'true'` at build time; a normal EAS build leaves it unset → gate false. Verified — no leak risk into store builds, and `membership.tsx` even closes the self-upgrade hole inside the preview build.

**Real blockers, in order of severity:**

1. **Monetization does not exist — and its design collides with Apple policy.** `membership.tsx` lets any fresh signup self-select ANY tier (`apply(tier)` → `updateTier` + `apiSetTier`) with **no payment step**; `billing.tsx` is an explicit shell ("Manage billing — coming soon"). You cannot ship a $49/$499 subscription product where the tier is free-selectable. Worse, the plan of record (Stripe via `@stripe/stripe-react-native`) sells a *digital service consumed in-app* — that is squarely App Store Guideline 3.1.1 territory: Apple will demand In-App Purchase (or the narrow US external-purchase-link entitlement) for the Consumer $49 tier. Business/Enterprise can plausibly be positioned as "sold outside the app to organizations" (the Netflix/Slack reader-app pattern), but Consumer at $49/mo in-app cannot dodge IAP. **This is a product/pricing decision, not an engineering task, and it gates the whole store path.** Nobody has made it yet.
2. **No `eas.json`** — zero build profiles (dev/preview/production, credentials, env). First concrete artifact needed.
3. **Google sign-in breaks on native Android**: `GOOGLE_ANDROID_CLIENT_ID = ''` (explicit TODO — needs the SHA-1 that only exists after the first EAS Android build). iOS client exists. Chicken-and-egg is documented in `constants/google.ts`; just needs the loop run.
4. **The Capacitor path is a liability, not an asset.** `capacitor.config.ts` + `@capacitor/*` deps wrap the Expo *web export* in an iOS WebView. Its own comments admit Google sign-in does not complete inside the WebView. A webview-wrapper of a subscription app is a classic Guideline 4.2 (minimum functionality) rejection, and it forks the native story into two builds of different quality. **Recommendation: delete the Capacitor path the day the first EAS build succeeds.** One store binary, built by EAS.
5. **Store-review hygiene gaps:** `userInterfaceStyle: "dark"` while the app is a light-white design (status-bar/trait mismatch on devices in dark mode); no splash-screen config in app.json (splash-icon.png exists but is unwired); no `ios.buildNumber`/`android.versionCode` strategy; no `ITSAppUsesNonExemptEncryption` flag; App Privacy labels/data-safety forms not yet drafted; Apple requires an in-app **account deletion** path for account-creating apps (5.1.1(v)) — I did not find one in the profile stack; `orientation: "default"` + `supportsTablet: true` exposes landscape/iPad surfaces the app has no layout for (see §4) — either build for them or declare portrait + `supportsTablet: false` for v1.
6. Push (`expo-notifications`) is honestly deferred and is NOT a submission blocker — alerts can ship pull-based v1.

**Verdict (A) STORE PATH: APPROVE-WITH-CONDITIONS.** The scaffolding (bundle IDs, EAS project, icons, gate-off-for-native) is genuinely ready; the blockers are (i) the unmade IAP-vs-Stripe monetization decision, (ii) eas.json + Android OAuth loop, (iii) killing Capacitor, (iv) a store-hygiene checklist pass. **Biggest opportunity:** the first EAS build is cheap and unlocks the entire consumer growth loop (store presence, then push, then paid conversion). **Biggest blocker:** monetization design vs Apple 3.1.1 — decide it BEFORE writing any Stripe code, or the code gets rejected.

---

## 2. LOCALIZATION DEBT — how big is the lift?

**Current state: 100% English-hardcoded, zero i18n machinery.**
- No i18n library in package.json (no i18next/lingui/expo-localization). Every one of ~30 screens carries literal JSX strings.
- **English morphology is baked into logic**, not just copy: `index.tsx:207` conjugates `{n === 1 ? 'Signal Is' : 'Signals Are'}` — subject-verb agreement in code; greeting logic ("Good morning/afternoon/evening") likewise.
- **The casing machinery is English-typographic.** `titleCaseTopic()` (lib/signals.ts:501) implements English Title Case with acronym preservation — a convention that simply doesn't exist in French/Spanish/German (where it's wrong to capitalize every word); the UPPERCASE eyebrow/label rule in DESIGN_SYSTEM.md degrades or breaks in scripts without case (CJK, Thai) and inflates width in German. The pending "Mcgregor" acronym-dictionary fix is itself an English-only patch.
- **Dates:** `accuracy.tsx:50` hardcodes `'en-US'`; other spots use bare `toLocaleDateString()` (device-locale — inconsistent with the hardcoded one). Numbers via `toLocaleString()` are the one locale-correct habit already in place.
- **RTL: nothing.** No `I18nManager`, no logical start/end styling; the layout is LTR-absolute (`flex-row`, left-aligned hierarchy, ChevronRight affordances).

**But the honest scale read is this: the CONTENT is English.** Topics, explainers, Signal Analysis narratives, categories — all engine-generated English from English-language sources (the trusted-direct RSS roster is Anglo/Euro). Localizing the chrome around English trend data buys little; true localization means localized *source rosters and topic extraction* — an engine project, not a frontend one.

**Lift estimate:** chrome i18n (string extraction across ~30 screens + plural rules + date/casing abstraction) ≈ 2–3 focused weeks; RTL ≈ another 1–2 (Aurora's borderless/soft design is actually RTL-friendly — few directional borders); content localization = an engine roadmap item measured in quarters.

**Verdict (B) LOCALIZATION: APPROVE deliberate English-first.** Do NOT pay the lift now — the $49/$499 attention-intelligence buyer is reachable in English worldwide, and the data is English anyway. Two cheap disciplines to stop the debt compounding: (1) route ALL new user-facing strings through one module (a `strings.ts` today, i18n-ready tomorrow), (2) fix the `'en-US'` inconsistency to one policy. Revisit when a non-English market shows revenue pull.

---

## 3. PERFORMANCE AT 100×

**What already scales well (credit where due):**
- Feed is paged 100-at-a-time against O(1) engine slices (`SCORES_PAGE_SIZE=100`), first page paints immediately (`useInfiniteQuery`), and the giant-payload crash was already learned and fixed.
- Ledger Money/Crypto modes are lazily fetched only when their chip is selected (`enabled:`-gated queries) — the default view costs nothing extra.
- The "4s crypto polling" is bounded: `refetchInterval` fires **only while `status==='warming'`** (engine cold boot), then stops; steady-state is a 5-min staleTime. Correct design.
- Payloads are small: assets total <700KB, one font family bundled via `@expo-google-fonts`, lucide icons tree-shaken, no remote images in the feed.

**What breaks at 100× (catalog 100× and/or users 100×):**

1. **Eager fetch-EVERYTHING loop.** `useSignals` auto-advances through *all* pages on mount (`useEffect` → `fetchNextPage` until done; `fetchScores()` hard-caps at 200 pages = 20k topics). Today (~1.9–3.1k topics) that is 20–31 sequential requests per app-open per user, with `staleTime: 60s` — a navigating user re-pulls the full superset every minute. At a 100× catalog this is 200 requests and ~10–50MB of JSON held in one client array; at 100× users it multiplies engine read load linearly. The prewarm superset cache absorbs it server-side today, but the *client contract* ("client owns the whole catalog") is the thing that doesn't scale. Fix: server-side filter/sort/search endpoints + fetch-on-demand pages; keep eager prefetch capped at ~3 pages.
2. **Non-virtualized lists.** The entire dashboard is ONE `ScrollView` (`index.tsx:175`) with a grow-only reveal window (`PAGE=6`, never trims). Only two `FlatList`s exist in the whole app (onboarding, country picker). A determined scroller mounts hundreds of TrendCards with no recycling — memory and frame-time grow monotonically. Fine at 6-row reveals over 1.6k rows; not at 100×. Fix: FlatList/FlashList for the three feed lanes (this also composes with the design rule "lists are windowed").
3. **Detail screens depend on full-feed residence.** `useSignal(id)` finds the topic inside the progressively-loaded feed — a deep link (or future push-notification tap) to a topic on page 40 waits for 40 sequential fetches. Needs a single-topic endpoint fetch path before push notifications ship (they will deep-link by design).
4. **Warming-poll herd.** Every client polls `/crypto` at a fixed 4s during an engine cold boot — at 100× users that is a synchronized herd against exactly the endpoint class that H12'd before. Add jitter + exponential backoff (4s → 8s → 16s, cap 60s).

**Verdict (C) PERFORMANCE: APPROVE-WITH-CONDITIONS.** Architecture is right for today's scale and the team demonstrably learns from perf incidents. Conditions before any growth push: virtualize the feed lanes, cap eager prefetch + add server-side filtering, single-topic fetch for deep links, jittered warming backoff. None is a rewrite; all four are days-not-weeks.

---

## 4. ONE CODEBASE: PHONE + TABLET + WEB-PREVIEW

**Holds up — with one asterisk and one dead branch.**
- The expo-router + react-native-web arrangement genuinely serves three surfaces from one tree: native phone (Expo Go today, EAS tomorrow), the enterprise web preview (`expo export --platform web` + build-time `ENTERPRISE_ONLY` gate, correctly inert in native builds), and the Heroku preview app. Web-parity work (feedRank, crypto, entity groups) lands once and ships everywhere. This is the right shape.
- **The dead branch is Capacitor** (§1) — a fourth surface wrapping the web export in a WebView, with broken Google auth. Cut it; it is the only place the "one codebase" story forks.
- **The asterisk is tablet: there is no tablet story.** `supportsTablet: true` + `orientation: "default"` are declared, but the codebase has zero responsive layout — no `useWindowDimensions` outside the country picker/onboarding, no breakpoints, no max-width containers (the only `maxWidth`s are 175px text clamps). On a 1024pt iPad the single phone column stretches edge-to-edge; App Review WILL screenshot it. Either (a) v1: declare portrait-phone honestly (`supportsTablet: false`) — zero work, no reach loss that matters for a phone-first consumer product — or (b) later: a cheap `maxWidth: ~640 + centered` content frame makes tablet acceptable in a day. Do not ship the accidental stretched layout.

**Verdict: APPROVE** the one-codebase strategy; condition = kill Capacitor and make the tablet declaration honest (option a now, option b post-launch).

---

## PRIORITIZED RECOMMENDATIONS

1. **Decide monetization vs Apple 3.1.1 NOW** (founder + counsel): Consumer $49 = Apple IAP (or US external-link entitlement); Business/Enterprise = provisioned-outside-the-app accounts. This decision shapes phase 8 before any Stripe code is written.
2. **Run the first EAS build loop this month** (create eas.json → `eas build -p android` → SHA-1 → Android OAuth client → internal-track/TestFlight). Cheap, unlocks everything, surfaces unknowns early.
3. **Delete the Capacitor path** once EAS builds work (one store binary).
4. **Store-hygiene checklist:** portrait + `supportsTablet:false` (v1), fix `userInterfaceStyle`, wire splash, version-code strategy, encryption flag, privacy labels, add an account-deletion flow (Apple 5.1.1(v)).
5. **Perf-at-scale quartet:** virtualize feed lanes (FlashList), cap eager prefetch + server-side filter/search, single-topic fetch endpoint for deep links (prerequisite for push), jittered warming backoff.
6. **Freeze localization debt cheaply:** one strings module for new copy; unify date-locale policy. Defer real i18n until a market pulls.
7. Close the payment-less tier selector before ANY store build reaches external testers (tie tier to backend entitlement, not client self-select).

— The Expansionist

---

# BOARD MEMO — The Outsider (VC / ex-hedge-fund banker)
## Mobile platform review (consumer $49 / business $499), 2026-07-17
Sources read: `frontend/app/(auth)/{onboarding,signup,login,membership}.tsx`,
`components/membership/MembershipPlans.tsx`, `constants/tiers.ts`, `app/(app)/index.tsx`,
`components/trends/LockedSignalsBanner.tsx`, `lib/signals.ts`, `app/(app)/profile/{membership,methodology}.tsx`,
`components/trends/DarkMatterPanel.tsx`, `hooks/useSignals.ts` (skim), evidence pack.

---

## 1. The $49 pitch — is the 24h delay honest and priced in?

**Mostly yes, and better than most subscription apps.** The tier card (`constants/tiers.ts` →
`MembershipPlans.tsx`) states the delay THREE ways: feature "Gradient Score history (24h+)",
description "Trend history access (24h+)", and an explicit restriction line with an X icon:
"Cannot access signals less than 24 hours old." A buyer who reads the card knows what they're buying.
The in-feed `LockedSignalsBanner` ("N newer signals hidden — Upgrade to Business") continuously
re-teaches the model. That is honest merchandising. I'd fund that posture.

**But three things undercut it:**

- **The onboarding oversells the tier the buyer lands on.** Slide 1: "By the time Google Trends
  fires, the opportunity is already captured." Slide 2: "measures where human attention is moving
  before it arrives." Then the $49 buyer receives *yesterday's* foresight. The delay is disclosed
  at the paywall, but the emotional close is "beat the crowd" and the product delivered is "watch
  the crowd from 24h behind." A sophisticated buyer will feel the bait within a week. One honest
  sentence on the Consumer card — "You see every signal the institutions saw, one day later — still
  ahead of the mainstream press cycle" — would convert the delay from a *restriction* into a
  *story*. Right now the delay is disclosed but never SOLD.
- **`dataWindowLabel()` contradicts the contract** (`lib/signals.ts:568-572`): it labels the
  Market feed "1h+ data" for Consumer and "30m+ data" for Business, while `tiers.ts` enforces
  24h/12h and the paywall says 24h/12h. Either the label overpromises freshness ~24× or the
  constants are stale — both are unacceptable on a paid data product. This is the single worst
  line in the mobile codebase from an investor-diligence standpoint. **Fix before anything else.**
- **Claims the product can't deliver yet:** "All plans include push + email alerts · Cancel
  anytime" (`MembershipPlans.tsx:104`) — push is deferred (Phase 8, no custom dev client), and
  there is no billing to cancel (Stripe deferred). "Email + push alerts" is also a Consumer tier
  feature bullet. Pre-revenue this is harmless; the day a card is charged it's an FTC-style claim.

**Would I subscribe at $49?** As a marketer/creator: plausibly yes — a ranked, cross-platform
attention feed with a track-record ledger is genuinely differentiated, and $49 is an impulse price
for a business expense. But only if week 2 doesn't feel stale (see §4).

## 2. Dashboard — value in 10 seconds?

**Yes. This is the strongest screen in the product.** Sequence: greeting → "1,899 Trends Are
Heating Up!" (32px) → the midnight-gradient #1 hero card with the topic name, a 44px gold score,
an action line, and a single red CTA. Tabs (Trends / Market / Crypto / Grade) are one thumb away.
The Aurora restraint (one gold number, borderless cards) makes the hero land. An 8-year-old test:
passes.

Nits that matter at this price point:
- **The hero metric label is "N"** with zero on-screen explanation. The methodology screen
  (buried at Profile → Methodology) explains N well — but the first number a new subscriber sees
  is a bare letter. One tappable "?" or a sublabel ("N · Now Trending index") is table stakes.
  Same for "MONEY MOVEMENT" on the Market hero.
- **"X Are Moving!" / "Heating Up!" is the feed COUNT, not a movement count.** On Crypto it says
  "12 Coins Are Moving!" when 12 is simply the tracked roster including Neutral-flow coins. On a
  measurement-not-advice product the headline is the one place mobile currently *editorializes*.
  Cheap fix: "Tracking 12 Coins" / "1,899 Trends on the Radar", keep the excitement word for the
  filtered movers.

## 3. The $49 → $499 → $250k ladder

- **$49 → $499: credible and well-built.** The upgrade motive (freshness) is felt inside the
  product every session via `LockedSignalsBanner` with a live locked-count and a priced CTA. The
  Business card is pre-selected + "Most Popular" on the plan screen. Classic good SaaS mechanics.
- **$499 → $250k: a category error on this surface.** A Business user's locked banner renders
  "Upgrade — $250,000/mo" as a self-serve tap, and Profile → Membership ("Change your plan
  anytime") offers a "Start Enterprise Plan" button that — because Stripe is deferred and
  `apiSetTier` just persists the tier — **actually grants Enterprise** (live data, 100k tokens,
  seat entitlements) to anyone who taps it, outside the `ENTERPRISE_ONLY` preview build. Nobody
  buys a $250k contract from a phone button; showing it makes the price look unserious, and the
  working self-upgrade is an access-control hole the moment real users exist. The Enterprise card
  on mobile should be "Contact sales" (deep-link to email/calendar), full stop.
- **No trial definition.** "Continue with free trial" silently sets Consumer with no length, no
  terms, no card. Fine for a preview; not shippable.
- Net: the ladder's first rung is real; the top rung on mobile is a prop that currently dispenses
  the product for free.

## 4. What makes me churn in week 2

1. **Alerts that never arrive.** Alerts are a headline feature on every tier card; push is
   deferred. A $49 subscriber who sets an alert and hears nothing cancels. Either ship push/email
   before charging, or strip the claim.
2. **Perceived staleness.** The header shows "Updated {age of newest accessible signal}" — for a
   Consumer that is structurally "1d ago", every day, forever. It reads as a dead app, not a tier
   window. Reframe: "Your data window: 24h+ · engine live" so staleness reads as tier, not neglect.
3. **Repetition + catch-all noise.** ~70% of the served working set is category "General"
   (engine-side, known). A consumer scrolling the same mega-topics with vague labels ("General")
   loses the "before it arrives" feeling fast. The category chips help; the feed's day-over-day
   delta ("new since yesterday") is the retention feature that doesn't exist yet.
4. **The sample-data fallback.** On engine failure the feed silently swaps to a mock dataset with
   a one-line grey banner ("Showing sample data — live engine unreachable"). For a paying user,
   fake trends styled identically to real ones is a trust grenade — one screenshot of a "sample"
   topic presented as a trend and the product's integrity story is gone. An outage should show an
   honest empty/retry state, not plausible fake signals.
5. **The 24h reality check** from §1 — if the delay was never *sold*, week 2 is when it's felt.

## 5. Jargon — explain vs assume

**Explained (well):** Detection vs Confidence, the gap, N, maturity — Profile → Methodology is
genuinely good plain-English writing. Dark Matter carries an honest in-context caveat where it
appears ("probabilistic, not deterministic… not a confirmed private signal" —
`DarkMatterPanel.tsx:88-91`). "Heisenberg" never reaches the user (internal field name only;
UI says "the gap"). That's the right call.

**Assumed (fix):** "N" on the hero (§2); "Money Movement" / "Market Confirmation"; "informed money
via crypto-exposure proxies" (Crypto tab intro — three abstractions in one clause); "Dark Matter"
as a bare label on list cards before any explainer; lane/tier chips like "Halted / micro-cap" for a
consumer. The pattern to copy is the DarkMatterPanel: one muted sentence at point of use, not a
buried methodology page. Also: the signup Terms checkbox links to `/membership` instead of any
terms text (`signup.tsx:110`), and Privacy Policy has no handler — the user consents to a §8
proprietary-rights clause they are never shown. Legal will not clear that for store submission.

## 6. Display integrity — one more material finding

`lib/signals.ts` `breakdownGroups()` (539-559): when live component groups are absent, the app
**fabricates** a nine-row breakdown by arithmetic on the headline score — "Velocity = score+6",
"Acceleration = score−8", "Novelty = 100−score+20", "Source spread = mean−4" — and renders it in
the same UI as real components. Comment says "fallback synthetic," but the user can't tell. This
is precisely what §17 forbids in spirit (implying inputs that didn't contribute) and what the
founder's enterprise standard ("every claim data-supported, defensible to hedge-fund counsel")
prohibits. A short-seller-minded diligence analyst finds this in an afternoon. Render "component
breakdown unavailable" instead. Same review for `actionFor()` fallback text (lower risk — it's
stage-derived, at least).

---

## VERDICTS

**(A) Design / UX — APPROVE.** Aurora on mobile is coherent, calm, and the dashboard hero is a
genuinely strong 10-second pitch; onboarding→paywall flow is clean. Conditions are polish, not
structure: explain "N"/"Money Movement" at point of use, fix the count-as-"Moving!" headline,
Enterprise→contact-sales.
*Point-blank question:* **"What does the $49 subscriber see on Day 8 that they didn't see on
Day 1?" If the answer is "the same list, a day later," design is done but retention isn't.**

**(B) Display integrity — APPROVE-WITH-CONDITIONS.** The tier-delay disclosure is honest and the
Dark Matter caveat is exemplary. Conditions (all must-fix): (1) `dataWindowLabel` "1h+/30m+" vs
the 24h/12h contract — one of them is lying; (2) synthetic `breakdownGroups` fabricating component
values from the headline score; (3) sample-data fallback rendering fake signals to paying users;
(4) "push + email alerts / cancel anytime / free trial" claims with no delivery mechanism behind
them; (5) signup consents to terms that are never displayed.
*Point-blank question:* **"Which is true — the 24-hour delay we sell, or the '1h+ data' label we
display? Pick one and delete the other today."**

**(C) Readiness for store distribution — REJECT (not yet).** Not because of quality — because the
commercial spine is missing: no Stripe means every price on the plan screen is decorative and the
$250k tier is a free button; no push means the advertised alert loop is dead; the terms flow won't
pass legal review. Priority order: (1) fix B-conditions 1–2 (hours of work, existential to the
integrity story); (2) Enterprise → contact-sales + remove self-serve tier grants; (3) wire the
terms/privacy screens into signup; (4) Stripe + push (the known Phase-8 gate) with a defined trial;
(5) staleness reframe + "new since yesterday" delta for retention; then ship.
*Point-blank question:* **"If 100 strangers install this tomorrow and 10 tap 'Start Enterprise
Plan', what happens?" Today the honest answer is: they all get a $250k product for free.**

— The Outsider

---

# BOARD MEMO — The Executioner — Mobile (Aurora) Executability Review
Date: 2026-07-17 · Repo: `frontend/` · Pack: board_pack_mobile.md

My lane: can this actually be shipped, in what order, with what verification, and what do we
refuse to spend time on. Every claim below was verified in source, not taken from the pack.

---

## 1. PACK CLAIM VERIFICATION

**Claim: exactly one #00C896 violation at `components/trends/SignalAnalysisPanel.tsx:47` — CONFIRMED.**
Full-tree grep of `frontend/` finds `#00C896` in exactly two places: the DESIGN_SYSTEM.md ban list
(line 32, correct) and `SignalAnalysisPanel.tsx:47` (`<Activity size={16} color="#00C896" />`).

**Pack ERROR (minor, changes nothing about the fix): the panel does NOT render on signal/[id] or
risk/[key].** Grep shows `SignalAnalysisPanel` is imported by exactly two screens:
- `app/(app)/crypto/[coin].tsx:125` (crypto detail)
- `app/(app)/profile/accuracy.tsx:274` (ledger row expand)
`signal/[id].tsx` uses `DualScoreAnalysis` (a different component); `risk/[key].tsx` has inline
analysis sections. So the neon-green leak is visible on the crypto detail and the Accuracy Ledger
row expansion — still user-facing, still a violation, same one-file fix.

**Claim: gold confined to the hero — CONFIRMED, with one footnote.** `C9A24B`/gold classes in
`app/` appear only in `app/(app)/index.tsx` at lines 260 and 411 — two hero eyebrow labels
(`{metricLabel}` and `MONEY MOVEMENT`), both on the Home screen. Line 411 is the Market/Money
hero tile, which is a hair beyond the literal "Home hero SCORE only" wording but is the same
hero-tile pattern on the same screen. I would not spend a minute on it; if the contract wording
matters, amend DESIGN_SYSTEM.md §1 to "Home hero tiles," not the code.

**Disclaimer coverage (integrity spot-check) — SOLID.** The founder-verbatim disclaimer lives in
`components/ui/Disclaimer.tsx` and is mounted top AND bottom on `signal/[id]` (122, 322),
`risk/[key]` (119, 536), `crypto/[coin]` (82, 203), plus `history`, `alerts`, `accuracy`,
`methodology`. The panel itself renders the engine-sent `a.disclaimer` and, §17-correctly,
renders NOTHING when the engine returns no sections (line 43).

---

## 2. THE EXACT FIX — SignalAnalysisPanel.tsx (whole file is pre-Aurora, not just line 47)

The pack undersells it: line 47 is the only BANNED hex, but the file is off-contract in five ways.
Fix all of them in one pass — it is one component, ~8 line edits, zero logic change:

| Line | Current | Aurora fix | Rule broken |
|---|---|---|---|
| 47 | `color="#00C896"` | `color="#16264A"` (ink — matches the adjacent `text-textPrimary` heading; sibling components pass icon hexes this way: Input.tsx `#3C4663`, ConvergenceBadge `#9A9AA2`) | §1 banned hex |
| 45 | `rounded-2xl border border-border bg-surface` | `rounded-3xl bg-card` (or wrap in `<Card>` from `components/ui/Card`) | §3 borderless cards |
| 54 | `ActivityIndicator color="#9AA3B0"` | `color="#9A9AA2"` (`#9AA3B0` is the PRE-Aurora textMuted — a second stealth legacy hex the banned-hex sweep didn't catch because it isn't on the ban list) | §1 approved palette only |
| 62 | `border border-border bg-bg` (fact chips) | `bg-cardAlt` borderless (`#EEF0F4` token exists for exactly this nested-chip case) | §3 |
| 18, 49, 55, 63, 73, 79 | `text-[12px]`, `text-[11px]`, `text-[10px]` | `text-xs` (12 is the hard floor; 10/11px are contract violations; `text-[12px]` works but should be the named class) | §2 type scale, min 12 |

Do NOT retrofit `<Collapsible>` here (§4 suggests it for analysis sections): on accuracy.tsx the
panel already mounts inside a row-expand (`open && <SignalAnalysisPanel .../>`), so adding a second
collapse layer is a UX regression. CUT that idea.

Verification for this fix: re-run the banned-hex grep (`#00C896|#2D7EEF|#E85A1E|#EE6A2A|#DC2626|#9AA3B0`
— ADD `#9AA3B0` and the rest of the pre-Aurora palette to the sweep), grep `border border-border`
and `text-\[(10|11)px\]` under `components/trends/`, then `npx expo export --platform web` + eyeball
the crypto detail on the preview. ~30 minutes end to end.

---

## 3. NATIVE-BUILD PATH OFF EXPO GO (phase 8) — what exists, what's missing, runnable checklist

**Exists in `app.json`:** iOS `bundleIdentifier: com.nowtrendin.app`; Android `package:
com.nowtrendin.app` + full adaptive-icon set; `scheme: nowtrendin` (deep links / OAuth redirect);
EAS `projectId: ef045a1d-05df-4ab5-b474-508c412ae420`; `owner: now-trendin`. That is a real,
non-trivial head start — the EAS project is already provisioned.

**Missing / wrong:**
- **No `eas.json`** — no build profiles at all.
- **No `expo-dev-client`, no `expo-notifications`, no `@stripe/stripe-react-native`** in
  package.json (consistent with "deferred", but they are the whole point of phase 8).
- **No `splash` config** — a store build will ship the bare default splash.
- `userInterfaceStyle: "dark"` while Aurora is a LIGHT app (bg #FFFFFF, dark-content status bar) —
  set to `"light"` before any native build or iOS will report dark scheme to the app.
- `adaptiveIcon.backgroundColor: "#E6F4FE"` — Expo scaffold blue, off-brand; cosmetic, fix in passing.
- **No push-token registration endpoint on the Django backend** (getExpoPushTokenAsync produces a
  token the server must store per-user; that backend work is unscoped anywhere).
- **A PARALLEL Capacitor path already sits in the repo**: `capacitor.config.ts` +
  `@capacitor/cli|core|ios ^8.4.0` in dependencies — wraps the web export in an iOS WebView, with a
  documented caveat that Google sign-in DOES NOT complete inside the WebView. Two half-native paths
  is how nothing ships.

**Runnable checklist (sequenced):**
1. **DECISION FIRST (founder, 30 min): kill the Capacitor track.** EAS dev-client is the
   CLAUDE.md-sanctioned path; Capacitor breaks Google OAuth and courts App Store 4.2
   (minimum-functionality/WebView) rejection. Remove `@capacitor/*` + `capacitor.config.ts`, or
   explicitly park them in a branch. Do not dual-track.
2. **DECISION SECOND (founder + counsel, before ANY Stripe code): the payments rail.** Apple
   guideline 3.1.1 and Google Play Billing both require platform billing (or the post-ruling US
   external-purchase-link flow) for digital subscriptions — a $49/mo digital-content sub bought
   in-app via raw Stripe is a rejection on iOS and a Play takedown risk. Options: StoreKit/Play
   Billing (RevenueCat), or web-signup + app-login (the Netflix/Spotify "reader" pattern — zero
   in-app payment code), or US external-link entitlement. The Executioner's pick: **web-signup +
   app-login for v1** — it deletes the entire Stripe-mobile work item from the critical path and
   ships weeks earlier. Stripe stays on the web surface where it already belongs.
3. `npx expo install expo-dev-client expo-notifications` (+ `@stripe/stripe-react-native` ONLY if
   step 2 chose in-app payments).
4. `app.json`: add `"expo-notifications"` to plugins (icon/color config), fix
   `userInterfaceStyle: "light"`, add `splash`, fix adaptiveIcon background.
5. Create `eas.json`: `development` (developmentClient: true, distribution: internal), `preview`
   (internal), `production` (autoIncrement). ~15 lines.
6. `eas build --profile development --platform android` FIRST (no Apple credential dance, fastest
   feedback), then iOS (`eas credentials` — Apple Developer account + push key needed; verify the
   $99 Apple Developer membership exists TODAY, it is the longest external lead time along with
   D-U-N-S/app-review, not code).
7. Wire push: `getExpoPushTokenAsync({ projectId })` on login → NEW Django endpoint to store
   tokens → engine/backend sends via Expo push API on alert triggers. (Backend endpoint is the
   hidden scope here — budget it.)
8. Re-verify Google OAuth in the dev client (`expo-auth-session` redirect via the `nowtrendin`
   scheme; native client IDs in Google console — Expo Go's proxy client id will NOT carry over).
9. `eas build --profile preview` → TestFlight / Play internal testing. Store listing assets,
   privacy labels, and the T&C clause (§8) come after a preview build installs clean.

---

## 4. CASING-DICTIONARY PORT (web → mobile)

**Verified:** `web-terminal/src/lib/mobileTheme.ts:108-122` has `TC_ACRONYMS` (ai/agi/llm/ipo/
nato/fifa/ufc/nba/nfl/nhl/mlb/gdp/etf/cpi/imf/ecb/un/eu/uk/nyc/uae/f1/ev + plurals) + `TC_SMALL`
(of/the/and/for/in/on/at/to/vs/de/a). Mobile `frontend/lib/signals.ts:501-513` has neither — it
only preserves interior-cap/all-caps words, so engine-lowercase "ai" renders "Ai" on mobile but
"AI" on web. Single definition site on mobile (grep confirms; `TopicTitle` routes through it), so
this is a one-file port.

**Spec — replace `titleCaseTopic` in `frontend/lib/signals.ts` with (keeps mobile's
whitespace-run preservation, adds the web dictionaries verbatim):**

```ts
// PARITY TWIN: keep dictionaries identical to web-terminal/src/lib/mobileTheme.ts
// (TC_ACRONYMS / TC_SMALL). Checked by /frontend-consistency.
const TC_ACRONYMS = new Set(['ai','agi','asi','llm','llms','ipo','ipos','nato','fifa','ufc',
  'nba','nfl','nhl','mlb','gdp','etf','etfs','cpi','imf','ecb','un','eu','uk','nyc','uae',
  'f1','ev','evs']);
const TC_SMALL = new Set(['of','the','and','for','in','on','at','to','vs','de','a']);
export function titleCaseTopic(s?: string): string {
  if (!s) return '';
  let wi = -1;
  return s
    .split(/(\s+)/)
    .map((w) => {
      if (!w.trim()) return w;          // keep whitespace runs
      wi++;
      const lw = w.toLowerCase();
      if (TC_ACRONYMS.has(lw)) return lw.toUpperCase();
      if (wi > 0 && TC_SMALL.has(lw)) return lw;
      if (w === w.toUpperCase() || /[A-Z]/.test(w.slice(1))) {
        return w.charAt(0).toUpperCase() + w.slice(1);
      }
      return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
    })
    .join('');
}
```

Cross-repo import is not worth the build-system entanglement (Metro vs Vite); duplicate with the
parity comment and add "TC dictionaries identical" to the /frontend-consistency checklist.

**Honesty note the pack glosses over:** the acronym dictionary does NOT fix "Mcgregor" — on BOTH
platforms `/[A-Z]/.test("mcgregor")` is false and it title-cases to "Mcgregor". Fixing McGregor
needs a Mc/Mac surname rule, which is an edge-case swamp (macron→"MacRon"? macbook→"MacBook" ok
but "machine"→"MacHine" catastrophic). CUT the surname rule from any near-term push; the
dictionary port is the whole shippable item. If Mc-names matter later, fix casing at the ENGINE
(display name canonicalization), not with client regex heroics ×2 platforms.

Verify: `node -e` spot-check of the function body against: "quantum llms"→"Quantum LLMs",
"ai"→"AI", "war of the worlds"→"War of the Worlds", "NASA"→"NASA", "iPhone"→"iPhone".

---

## 5. VERIFICATION STRATEGY (tsc crashes on this project — known, in memory)

What CANNOT be used: `tsc --noEmit` (crashes on this Expo setup — do not burn an hour rediscovering
this). No jest/test runner is configured; do not add one for this change set.

What CAN be verified, in order of cost:
1. **Pattern-parity greps** (seconds, run pre- and post-change): banned+legacy hex sweep
   (`#00C896|#2D7EEF|#E85A1E|#EE6A2A|#DC2626|#9AA3B0|#5B6472|#1A1A2E|#F4F5F7` over
   app/components/lib/constants), `border border-border` outside hairline-divider contexts,
   `text-\[(10|11)px\]`, gold outside `app/(app)/index.tsx`.
2. **`npx expo export --platform web`** — full Metro bundle; catches syntax/import/resolution
   errors (NOT type errors — never claim type-safety from it).
3. **Node spot-check** of pure functions (titleCaseTopic cases above).
4. **Deploy path: `/deploy-mobile-preview`** → nowtrendin-v2-preview Heroku (PIN gate 6969), then
   eyeball crypto/[coin] (panel card style + icon) and any list with "ai"/"fifa" topics for casing.
5. **Native motion/touch**: Expo Go on the founder's device — the only place 440ms Rise/Collapsible
   feel can actually be judged; batch this with other approval-gated founder time (per the
   approval-delay memory note).

---

## 6. WHAT I CUT from any near-term mobile push
1. **Capacitor track** — remove or park; two native paths = zero shipped native apps.
2. **In-app Stripe UI before the payments-rail decision** — likely 3.1.1 rejection; web-signup +
   app-login deletes the work item entirely.
3. **Mc/Mac surname casing** — edge-case swamp; dictionary port only. Engine-side fix if ever.
4. **`<Collapsible>` retrofit of SignalAnalysisPanel** — double-collapse UX regression on accuracy.
5. **Dark theme** — Aurora is light; just fix the `userInterfaceStyle` flag.
6. **Chasing web density on mobile** — §12 explicitly allows web MORE; mobile parity is semantic,
   not columnar.
7. **CLAUDE.md §3/§11 palette reconciliation** — real doc-debt (root CLAUDE.md still teaches agents
   the pre-Aurora neon palette, which is exactly how a #00C896 sneaks in), but it is a docs PR, not
   a mobile-push blocker. SHIP-LATER, soon, cheap.

---

## 7. VERDICTS + SEQUENCED WORKLIST

**(A) Design/UX — APPROVE-WITH-CONDITIONS.** The one banned hex is real but the file around it is
pre-Aurora in five ways; conditions = the §2 table fix + casing port. **SHIP.**

**(B) Integrity/honesty — APPROVE.** Founder-verbatim disclaimer verified top+bottom across all
detail/analysis screens; §17 null-render verified in the panel (line 43); measurement-not-advice
lines present on signal (319) and risk (532) details. No blocking work in my lane. (Deeper honesty
questions — N=100 display, mock banner semantics — are other seats' briefs.)

**(C) Store readiness — SHIP-LATER, with the scaffolding SHIPPED NOW.** Dev-client checklist
(§3 steps 1, 3–6) is ~1 day of code + external lead times (Apple account, credentials). Payments
rail is a DECISION, not code — make it before any Stripe line is written. Push needs an unscoped
Django endpoint — budget it explicitly.

**Sequenced worklist:**
| # | Item | Effort | Gate |
|---|---|---|---|
| 1 | SignalAnalysisPanel Aurora remap (§2 table, all 5 rows) | 30 min | greps + expo export + preview |
| 2 | titleCaseTopic dictionary port (§4 spec) | 30 min | node spot-check + preview |
| 3 | `/deploy-mobile-preview` + founder eyeball | 15 min + approval gap | live preview |
| 4 | Kill/park Capacitor; fix userInterfaceStyle + adaptiveIcon bg + splash in app.json | 1 h | expo export |
| 5 | Payments-rail decision (recommend web-signup + app-login) | founder session | — |
| 6 | eas.json + expo-dev-client + expo-notifications; Android dev build first | 0.5–1 day | dev build installs |
| 7 | Push-token Django endpoint + alert send path | 1–2 days (backend) | end-to-end test push |
| 8 | iOS credentials / TestFlight; Google OAuth native client ids | external lead time | preview build |
| 9 | CLAUDE.md §3/§11 Aurora reconciliation (docs) | 1 h | — |

Items 1–3 are this week's mobile push, full stop. 4–8 are phase 8 proper. Nothing else gets in.

— The Executioner

---

# BOARD MEMO — The Economist · Mobile (Aurora) Review · 2026-07-17

**To:** The Chairman (Founder)
**Re:** The mobile app as an instrument of investor psychology — does it measure attention, or manufacture it?
**Canon applied:** Kindleberger (manias), Taleb (silent evidence), Malkiel (null hypothesis / no edge in public data), Bernstein (risk is measurement), Belsky & Gilovich / Zweig (retail bias), Friedman & Schwartz (long series discipline), Adam Smith (prices as information).

**Premise.** The $49 subscriber is precisely the population Belsky/Gilovich and Zweig documented: loss-averse, anchor-prone, recency-driven, and most responsive to urgency cues at exactly the moments urgency is least warranted. An attention-measurement product sold to this population carries a special duty: it must not become a component of the mania it claims to measure. Kindleberger's structure — displacement → credit/attention expansion → euphoria → distress — is propagated by *amplifiers*. A push-distributed app that tells three thousand people "3,109 Trends Are Heating Up!" is, structurally, an amplifier candidate. The question for each finding below is which side of the measurement/amplification line the code sits on.

---

## Findings (from source, `frontend/`)

### 1. The hero + garnet headline — "Heating Up!" / "Moving!"
`app/(app)/index.tsx:205-217`: the greeting headline renders `{ranked.length} Trends Are <garnet>Heating Up!</garnet>` (and "Moving!" for Market/Crypto). Two problems, one venial, one structural:

- **The count is wrong as a claim.** `ranked` is *every accessible signal after filters* — including MARGINAL ("early, not yet confirmed") and MONITORING ("low-intensity background signal") rows. The sentence asserts that all of them are "heating up." That is not measurement framing; it is an aggregate excitement claim the underlying data explicitly does not support (the app's own STAGE_META calls the lower bands "Early / unconfirmed"). Kindleberger: euphoria spreads through exactly this kind of totalizing crowd-count — "everyone is in."
- **The exclamation mark is a trade signal to this audience.** Zweig's work on the anticipation circuitry is blunt: urgency cues fire *before* deliberation. Garnet + "!" + a gold 44px score + a red "VIEW TREND" pill (`index.tsx:254-266`) is a well-built desire funnel. On the institutional web terminal this would be tacky; on the retail surface it is a bias primer.

**Mitigation observed:** the hero's substance is honest — `actionLine(stage)` is descriptive ("Breakout in progress," "Marginal — early, not yet confirmed"), the codebase has deliberately stripped prescriptive "what to do" copy (`lib/signals.ts:148-155` comment: "no prescriptive guidance… the user decides"), and the disclaimer sits top and bottom of detail. The skeleton is measurement; the headline dressing is mania.

**Verdict: the headline is an amplifier, not a measurement.** Fixable with one line of copy.

### 2. N=100 walls — anchoring on a saturated scale
The DEFAULT dashboard view is "Now TrendIn," ranked by N (`index.tsx:44`), and the code itself concedes the problem: *"N saturates at 100 for many topics, so ties dominate the visible list"* (`lib/signals.ts:186-193`). The retail user therefore opens the app to a gold `100` on the hero and a column of 100s beneath it — with no visual admission that 100 is a *ceiling*, not a *measurement*. Belsky/Gilovich on anchoring: the first number seen becomes the reference for everything after; a wall of max-scale numbers teaches the user that "100 = normal excellent," destroying the scale's information content (Smith: a price that cannot vary carries no information). The detail screen is better — it explains N, keeps the headline scores demand-free, and shows the "+N what-if" separately with a demand-driven caveat flag (`signal/[id].tsx:151-172`, `lib/signals.ts:100-107` — genuinely good non-circularity discipline). But the list view presents saturation as distinction.

**Verdict: honest architecture, anchoring presentation.** Saturated values need a saturation mark.

### 3. Alerts — asymmetric attention training
`alerts.tsx` is better than I expected: alerts may target ONLY verified in-universe topics/market signals (free text rejected, line 25-27 + hard gate line 54), threshold framing is neutral ("when detection ≥ 75"), and the disclaimer is present. Two bias vectors remain:

- **Upward-only.** `SCORE_TYPES = detection|confidence|overall`, and the only semantics offered are "Alert when score **reaches**" (line 165). A user can be woken for rises, never for decay. This trains one-directional attention — Zweig's recency machine: each ping is another "things are going up" rep. There is no way to ask the instrument "tell me when attention *leaves*," which is half of what an attention gradient measures (and often the more valuable half — Kindleberger's distress phase begins in outflow).
- **The triggered line celebrates.** `🔔 Triggered 2h ago` renders in green (line 107-110). A trigger is an event, not a win; green codes it as a win.

**Verdict: structurally sound, behaviorally one-eyed.**

### 4. The 24h Consumer delay — the app's one factual falsehood
Here I must be severe, because everything else in this app's honesty case depends on it.

- The gate itself is clean: `constants/tiers.ts` — Consumer sees only data ≥24h old, enforced by `isDataAccessible` on first-seen age; membership copy states it plainly ("Cannot access signals less than 24 hours old"); `LockedSignalsBanner` derives its label from the actual constant so it cannot drift.
- **But `dataWindowLabel` (`lib/signals.ts:568-572`) hand-codes `'1h+ data'` for Consumer and `'30m+ data'` for Business** — displayed on the dashboard (`index.tsx:482`) and both category screens. The real windows are 24h and 12h. The label understates the Consumer delay by a factor of 24. Whatever its origin (stale copy from an earlier freshness scheme), as shipped it tells a $49 subscriber his feed is fresher than it is. Bernstein: risk began when we learned to measure honestly; a mislabeled vintage is a mismeasurement of the only thing the tier structure sells — time.
- **And the Trends intro oversells the delayed feed:** "What's gaining attention across every platform *right now*… *surfaced before it hits the mainstream*" (`index.tsx:244-246`) is shown to ALL tiers. For Enterprise it is the product thesis; for Consumer it is a claim of an edge the data-aging waterfall has deliberately removed. Malkiel's null: by the time information is a day old and mass-distributed, the residual edge for the marginal retail buyer approximates zero — and the business model *agrees* (that is exactly why Enterprise pays 5,000× more for liveness). The honest Consumer frame is the one the tier description already uses: *history and pattern literacy* ("Trend history access (24h+)") — a telescope pointed at yesterday, valuable as education and context, not as a trading edge. The app must not whisper "edge" on a surface whose price implies "history."
- Mitigating: "Updated 1d ago" renders truthfully from real timestamps; the upgrade banner states the trade honestly.

**Verdict: the gate is honest; two lines of copy are not.** This is the item I would hold a release for.

### 5. What the app teaches — calibrated skepticism or blind trust?
`profile/accuracy.tsx` is, for a retail product, remarkable — and I say this as the board member whose job is to disbelieve:

- Hit rate AND tracked-race rate side by side (10%-class blended vs races-actually-run) — publishing the *worse* number next to the better one is Taleb-grade discipline; most vendors publish only the numerator.
- False positives get their own filter chip and count; pre-broken (never-a-race) rows are explained in plain language and stay COUNTED in the honest rate; pending detections are disclosed ("365-day patience window"); LED wins carry an independent Wikipedia referee that honestly renders "referee unchecked" when unverified (`refereeLine`, line 84-88).
- Per-row entry analysis explains method and verdict without exposing formulas.

This is the silent evidence made audible. Three demerits: (a) it lives four taps deep in Profile while the "Heating Up!" headline lives on the front door — the skepticism curriculum is optional, the enthusiasm curriculum is mandatory. Friedman & Schwartz built credibility on the *long series shown whole*; the long series here is hidden behind the till. (b) "Best lead times" is a survivorship showcase with no adjacent "worst misses" (mitigated by the full filterable list above it, but the showcase is what a retail eye reads). (c) The empty-state copy — "the proof asset for institutional clients" — is marketing voice inside the measurement room.

**Verdict: the ledger is the most honest artifact in the product. Promote it.**

---

## (A) Design/UX for the retail audience — **APPROVE-WITH-CONDITIONS**
Framework: Zweig/Belsky-Gilovich (cue design for bias-prone users). The Aurora craft is excellent — calm palette, progressive disclosure, descriptive stage language, windowed lists, verified-entity alerts. Conditions: the garnet-exclamation headline and the always-on "right now / before the mainstream" intro are urgency primes inconsistent with the product's own measurement identity (Findings 1, 4b).

## (B) Integrity/honesty of what mobile displays — **APPROVE-WITH-CONDITIONS**
Framework: Bernstein (honest measurement) + Taleb (show the graveyard) + Malkiel (claim no edge you cannot demonstrate). The ledger, the N-separation, the demand-driven caveat, absent-data omission, and the verbatim disclaimer clear a high bar. Conditions (blocking): `dataWindowLabel` falsehood (24× understatement of the Consumer delay); saturated N=100 shown unmarked; "Heating Up!" count asserting what the stage data denies.

## (C) Store-distribution readiness — **APPROVE-WITH-CONDITIONS**
Framework: Kindleberger (an app-store product is a mass amplifier; review its mania surface before scale). Nothing here requires architecture; all conditions are copy/label-level and shippable in a day. Push notifications (Phase 8) will multiply whatever framing exists at launch — fix the framing BEFORE the amplifier arrives.

---

## PRESCRIPTIONS (priority order, canon-tied)

1. **P0 — Fix `dataWindowLabel` (lib/signals.ts:568) to derive from `TIERS[tier].dataFreshness`,** exactly as LockedSignalsBanner already does, so it reads "24h+ data" / "12h+ data" / "Live." Never hand-code a freshness claim twice. *(Bernstein: mismeasured vintage = mismeasured risk.)*
2. **P0 — Tier-conditional Trends intro** (index.tsx:244): delayed tiers get history framing — e.g. "What was gaining attention across every platform, served on your tier's 24-hour window — pattern history, not a live edge." Enterprise keeps "right now." *(Malkiel/Smith: public, delayed information is in the price; claim education, not edge.)*
3. **P1 — Replace the totalizing headline** with a stage-true count: "3,109 trends tracked · 41 in Breakout" — keep the garnet on the accurate subset if drama is wanted. Drop the exclamation mark on the retail surface. *(Kindleberger: don't be the crowd-count.)*
4. **P1 — Mark N saturation:** render `100` as `100 · max` (or a small "ceiling" tick on the hero and TrendCard metric) whenever N===100, and consider showing tie-count ("=1 of 37 at max"). *(Belsky/Gilovich: de-anchor the wall of 100s.)*
5. **P1 — Add "falls below" alerts** (direction toggle: reaches / drops-below) so the instrument teaches outflow as well as inflow; render the triggered line in neutral ink, not green. *(Zweig: symmetric attention is anti-recency training.)*
6. **P2 — Promote the ledger to the front door:** a small "Our track record →" line under the hero (showing tracked-race % and false-positive count, not just wins) linking to accuracy.tsx. Make skepticism one tap, not four. *(Taleb/Friedman-Schwartz: the long, whole series is the credibility asset — use it as marketing precisely because it is honest.)*
7. **P2 — Balance "Best lead times"** with the adjacent worst outcome (longest lag or most recent false positive), or retitle "Selected wins." Remove "proof asset for institutional clients" from user-facing empty-state copy. *(Taleb: silent evidence.)*
8. **P3 — Founder sign-off item:** the verbatim disclaimer's grammar ("and or site") slightly undermines the seriousness it exists to convey; recommend a counsel-reviewed re-draft under the founder's sign-off rule — verbatim discipline is right, the current text is not its best self.
9. **P3 — Keep and defend** the verified-entity alert gate, the N-free headline scores, the demand-driven caveat flag, and absent-data omission — these are the honest bones of the product; enforce them on every future mobile merge (frontend-consistency agent).

**Bottom line.** This is closer to an honest instrument than almost anything sold to retail at $49 — the ledger alone would embarrass most fintech marketing departments. But the front door currently speaks mania while the back room speaks measurement. Swap the volume levels: lead with the track record, whisper the heat. Three of the fixes are single lines; none touches the engine.

— *The Economist*

---

**Chairman — your decision per item (P0 false displays · P1 copy · P2 hygiene · P3 store path/payments model).**
