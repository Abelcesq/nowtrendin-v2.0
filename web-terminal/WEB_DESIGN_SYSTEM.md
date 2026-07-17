# NowTrendIn Web Terminal — Design System (CONTRACT)

**This file is the single source of truth for the web terminal's look & feel** (desktop
inherits it via the Tauri wrapper). It is the WEB dialect of the "one brand, two
dialects" contract ruled by the founder 2026-07-16/17 after board review
(`audits/board/BOARD_aurora-hybrid-rev3_2026-07-17.md`). The mobile dialect is
`frontend/DESIGN_SYSTEM.md` (Aurora). Any code added or merged into `web-terminal/`
MUST follow this file.

## 1. The Dialect Rule (cross-platform contract)

**Parity with mobile is SEMANTIC, not literal.** Hue MEANINGS are contractual on every
surface; hue VALUES are per-surface:

| Meaning (contractual everywhere) | Web value (this surface) | Mobile value (Aurora) |
|---|---|---|
| Detection / earliness | `#2D7EEF` (+ text twin `#1b5fc4`) | sapphire `#2A5B9E` |
| Confidence / confirmation | `#00C896` (+ text twin `#007a5a`) | emerald `#2E7D5B` |
| Emphasis / N / interactive focus | orange `#df7a36` (+ text twin `#b35a18`) | garnet `#B11226` |
| Loss / error / down / alarm — **red means NOTHING else** | `#DC2626` | `#B11226` (error token) |
| Up / positive outcome | `#00C896` | `#2E7D5B` |
| Neutral / muted | `#9A9AA2` scale | `#9A9AA2` scale |

- NEVER restore jewel tones to web DATA colors ("fixing" the founder's ruling).
- NEVER copy the vivid web hexes into mobile UI (banned there by Aurora).
- The Frontend Consistency agent checks hue MEANING + section/data parity — never
  hex equality across platforms.

## 2. One meaning per hue (within this surface)

A hue family carries ONE meaning per view. Red is reserved: loss, error, down,
FALSE_POSITIVE, alarm — never emphasis, never a positive delta. Orange is emphasis/N —
never an error state. Green is confidence/up (valence-aligned by ruling). Where a
signed number renders, its color encodes DIRECTION only.

## 3. Surface-vs-text rule (WCAG)

Vivid hues are used where color is a SURFACE: rings, fills, dots, bars, chart strokes,
tinted pill backgrounds. Wherever the hue is TEXT (score columns, stat numbers, pill
labels), use the dark text twins: `--det-text:#1b5fc4`, `--conf-text:#007a5a`,
`--early-text:#b35a18`, stage pill text tokens (`--bk-t #007a5a`, `--st-t #1b5fc4`,
`--em-t #7d630d`, `--wa-t #b23e18`, `--mo-t #5f6774`). Contrast floors: 4.5:1 normal
text, 3:1 large text (≥19px bold) and graphics.

## 4. Typography

One family: **Plus Jakarta Sans**, weights 400/500/600/700/800, **SELF-HOSTED via
`@fontsource/plus-jakarta-sans`** (board condition — never a third-party font CDN:
bank proxies block them and the EU flags them). Base 13px (institutional density —
deliberately below mobile's 12px-floor-at-16px-body scale). **Numeric data columns
stay on the true monospace stack (`--mono`) with `tabular-nums`** — digit alignment
outranks font purity in a terminal. Topic/market names render Title Case via
`titleCaseTopic()` (shared acronym dictionary: AI/AGI/ASI/LLM/IPO/NATO/FIFA…);
category keys render via `catLabel()` (never raw `current_events`). Eyebrows/labels
UPPERCASE with letter-spacing; big numbers carry negative tracking; negative tracking
never on tabular numerals.

## 5. Chrome vs content

- **Chrome** (topbar, sidebar, footer): Aurora midnight (`--ink` scale `#0C1B3A`/
  `#1B3066`) — the instrument's dark housing. Kept deliberately (institutional
  identity; mobile has no chrome). Accents on dark grounds must clear contrast on
  midnight (wordmark orange passes; test anything new).
- **Content**: white canvas (`--canvas #FFFFFF`), soft borderless cards
  (`--surface #F4F5F8`, radius 16px, no outlines), hairline row dividers `#ECECEC`.
- Wordmark: "Now" white/ink + "TrendIn" orange `var(--early)`. Logo flame stays the
  brand flame — never retinted.

## 6. Components

- Buttons/chips are pills (radius 999): primary = ink `#16264A` + white text;
  inactive chip = `#F1F1F4` + `#3C4663`; active chip = colored fill + white text.
  CTA fills carrying white text use text-twin-depth fills (≥4.5:1).
- Stage/verdict pills: tinted background + dark token text (§3).
- Search fields: the orange identity (tint fill + orange border) — the founder's
  signature accent; focus ring orange.
- Empty/absent data: HIDE the block (§17 of CLAUDE.md) — never a dead spinner,
  never "not available" filler, never NaN. Internal engine strings (backfill/
  fallback/lifecycle-rule jargon) never render to users.
- The founder's verbatim disclaimer renders top AND bottom of every analysis panel —
  including the Accuracy Ledger — in neutral ink, never palette-colored.

## 7. Measurement, not advice (visual discipline)

No motion on up-moves; symmetric visual salience for up and down; zeros and headline
rates in neutral ink; tier labels descriptive, never prescriptive; the login page
stays dry (ILLUSTRATIVE markers on demo data).

## 8. Roadmap (ruled, not yet built)

Dark content mode (a third rendering of the SAME semantic contract — name any new
tokens theme-neutrally); off-white canvas A/B; token-file unification (styles.css
`:root` + mobileTheme.ts into one generated registry — the white-label engine);
casing-dictionary parity on mobile.

*Created 2026-07-17 (branch aurora-web-redesign) from the founder's rev-3 hybrid
ruling + six-memo board review. Change this file only with founder sign-off.*
