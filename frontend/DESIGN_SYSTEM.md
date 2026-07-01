# Now TrendIn — "Aurora" Design System (CONTRACT)

**This file is the single source of truth for the app's look & feel. Any code added or
merged into this repo — new cards, analysis sections, screens, anything — MUST follow it,
automatically, with no exceptions. If you are an AI agent or developer integrating new code,
apply these rules as part of the merge. The UI/UX must stay intact.**

The design is **Apple interaction + Disney aesthetic**: minimalist, calm, white space,
progressive disclosure, subtle touch motion. Inspiration is midnight-blue "magic" with red
accents — NOT the old "AI-generated" look (bordered white boxes, neon green/orange).

---

## 1. Color — APPROVED PALETTE ONLY

Use **semantic Tailwind tokens** (`tailwind.config.js`), never raw hex, never a color outside
this list. The tokens already hold the approved values, so token-based code is correct
automatically.

| Purpose | Token / hex |
|---|---|
| Brand / primary action / ink | `primary` `#1B3066`, `ink`/`textPrimary` `#16264A`, `primaryDk` `#0C1B3A` |
| Accent (sparing emphasis, CTAs) | `accent`/`error` `#B11226`, soft `accentSoft` `#F0758A` |
| Gold | `gold` `#C9A24B` — **RESERVED for the Home hero score ONLY.** Do NOT use gold anywhere else in functional UI. |
| Canvas / surfaces | page `bg` `#FFFFFF`; **cards** `card` `#F4F5F8` (borderless light fill) |
| Text | `textSecondary` `#3C4663`, `textMuted` `#9A9AA2` |
| Hairlines / tracks | `border` `#ECECEC`, `#EDEDED` |
| Jewel stage colors | Breakout `breakout` `#2E7D5B` (emerald) · Strong `strong` `#2A5B9E` (sapphire) · Indicating/Emerging `emerging` `#6B4FA0` (amethyst) · Watching/Marginal `watching` `#A8456A` (rose) · Monitoring `monitoring` `#8A8F9C` (slate) |
| Tier identity | Consumer `#2A5B9E` · Business `#2E7D5B` · Enterprise `#C9A24B` (crown) |
| Logo / wordmark (DO NOT CHANGE) | flame PNG + `brandMaroon` `#6E1A17` / `brandOrange` `#E8551C` |

**Banned in any new UI:** neon green `#00C896`, bright blue `#2D7EEF`, orange `#E85A1E`/`#EE6A2A`,
generic error red `#DC2626`, the rainbow content-category colors, and gold outside the hero score.
If merged code introduces any of these, remap to the nearest token above.

## 2. Typography

- One family: **Plus Jakarta Sans** — loaded globally in `app/_layout.tsx` and applied to every
  `Text`/`TextInput` via `defaultProps`. New text inherits it automatically; do not set another font.
- **Titles / headlines / trend & topic names → Title Case.** Wrap any engine-supplied name in
  `titleCaseTopic()` (from `lib/signals`) or render it with `<TopicTitle topic={...}/>`. Never show
  a raw lowercase name ("correction", "quantum LLMs").
- **Eyebrows / nav / filters / CTAs / small labels → UPPERCASE** with letter-spacing.
- Numbers shown to users → `Number(n).toLocaleString()` (e.g. `2,417`, not `2417`).
- **Type scale — STANDARDIZED. Use ONLY these sizes** (px). Minimum 12 (mobile readability).
  The Tailwind named classes already map to it (`text-xs`=12 … `text-5xl`=44), so prefer those;
  if you must use an explicit size, snap to the nearest step. Never introduce a new size.

  | Size | Use | Tailwind |
  |---|---|---|
  | **12** | caption / label / eyebrow / meta / fine print (the floor) | `text-xs` |
  | **14** | small / secondary text | `text-sm` |
  | **16** | body (default reading) | `text-base` |
  | **18** | row title / subheading | `text-lg` |
  | **22** | card title | `text-xl` / `text-2xl` |
  | **28** | screen / detail title | `text-3xl` |
  | **32** | hero headline | `text-4xl` |
  | **44** | hero score (the one special display number) | `text-5xl` |

## 3. Cards & containers — BORDERLESS

- **No border outlines, ever.** Cards/boxes are a borderless soft light fill: use `<Card>`
  (`components/ui/Card`) or `className="bg-card rounded-3xl"`. Never `border`, never a white box
  with a `#ECECEC` outline. Hairline **list dividers** (`borderBottom`) are fine.

## 4. Motion (touch-only — never a `:hover` state)

- Screen entrance / transition: every `<Screen>` slides+fades in (`Rise axis="x"`). Build screens
  with `<Screen>` to inherit it.
- Expand / reveal: use `<Collapsible>` (`components/ui/Collapsible`) for analysis sections — it
  carries the soft, relaxed (non-bouncy) 440ms ease + content fade. Don't hand-roll expand motion.
- Keep motion subtle and purposeful.

## 5. Reusable primitives — COMPOSE NEW UI FROM THESE

`components/ui`: `Screen` (frame + transition), `Card` (borderless card), `Collapsible` (analysis
section + motion), `TopicTitle` (auto Title-Case name), `Rise` (entrance motion), `Button`,
`GradientScoreRing`. Trend/market rows: `components/trends/TrendCard`, `RiskCard` (calm
tap-to-expand rows). The bottom tab bar is a custom component in `app/(app)/_layout.tsx`
(`NowTabBar`) — keep it; do not revert to the default navigator bar (its labels clip).

## 6. Journey / UX principles ("Don't Make Me Think")

- Lead with the answer (#1 hero), then a ranked list; show the essentials, hide depth behind
  `Collapsible`. Lists are windowed/paginated (reveal in batches on scroll) — never render a huge
  list at once. Primary actions (e.g. Pull Trends) stay **persistently visible**, not buried.
- An 8-year-old with no context should be able to navigate it.

---

### Rule for merges
When new backend-driven UI arrives (new cards, analysis sections, fields): render it with the
primitives in §5, the tokens in §1, the type rules in §2, borderless per §3, motion per §4. Do
**not** introduce new colors, borders, fonts, or hover states. Treat this as a hard requirement so
the design stays intact automatically.
