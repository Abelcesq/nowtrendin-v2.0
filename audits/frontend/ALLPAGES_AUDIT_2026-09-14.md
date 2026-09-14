# ALL-PAGES FRONTEND AUDIT — 2026-09-14 (post-divergence-merge, Chairman-ordered)

Tree audited: `main` at `baff749` (read-only; nothing edited or committed).
Scope: every web-terminal view + shared components, mobile (Expo) screens + trend components,
desktop (Tauri wrapper — confirmed `tauri-desktop/src-tauri/tauri.conf.json` `frontendDist:
"../../web-terminal/dist"`, i.e. the identical web build; nothing separate to audit).

Rules applied: item 1 (crypto-scoped money-vocabulary retirement, Chairman order 2026-09-14 /
`aae54f8`), item 2 (divergence forbidden-words), §17 (source display / no NaN), §16a+C1 (honest
absence), K17 (sign-aware gap display), founder-verbatim disclaimer, §12 semantic hue parity.
Equity Market Signal legitimately keeps "Money Movement" — equity-scoped uses are NOT flagged.

---

## 0. HEADLINE COUNTS

| Class | Count |
|---|---|
| **DEFECT** | **22** (10 web · 12 mobile) |
| **NIT** | 9 |
| **OK-BY-DESIGN** (suspicious but correct, explained) | 8 |
| Checks that PASSED clean | forbidden-words in divergence copy · NaN in live render paths · §17 gating on all detail views · divergence merge touched 0 `frontend/` files · disclaimer byte-identity (1 variant excepted) |

**Two audit-premise corrections (read first):**

1. **The mobile app HAS crypto screens.** `frontend/app/(app)/crypto/[coin].tsx`,
   `frontend/components/trends/CryptoCard.tsx`, and a `mode === 'crypto'` section of the mobile
   dashboard (`frontend/app/(app)/index.tsx:348-392`) exist on main (added in `148487d`,
   2026-08-18). The task premise "mobile has NO crypto screen — documented N/A" (from the
   CLAUDE.md 2026-06-26 note) is **stale**. Consequence: the crypto money-movement retirement
   was applied to the WEB view only; the mobile crypto surface still renders the retired
   presentation end to end (findings D-M1…D-M4).
2. **K17 web enumeration: the board said "up to 3 more web files"; there are 4** beyond the
   known Crypto.tsx instance (MarketSignal, Grade, Dashboard, Screener — §5 below).

---

## 1. CRYPTO-SCOPED "MONEY MOVEMENT" LEFTOVERS (visible strings only; comments ignored)

### Web

**D-W1 · DEFECT — `web-terminal/src/views/Dashboard.tsx:41`**
`'top-crypto': { title: 'Top crypto · money movement', … }` — the default crypto dashboard
tile's visible title. Crypto-scoped retired vocabulary.
Fix: `'Top crypto · positioning'`.

**D-W2 · DEFECT — `web-terminal/src/views/Ledger.tsx:147`**
Crypto ledger chip tooltip: `"Crypto Money Gradient — validated against realized COIN price
direction (FMP crypto + AV)"`. Fix: "Crypto positioning signal — validated against realized
COIN price direction".

**D-W3 · DEFECT — `web-terminal/src/views/Ledger.tsx:159, 187, 249–250`**
Crypto-mode sub-header "Crypto money-movement detections validated against realized …",
banner "whether our crypto money-movement read matched the coin", empty-state "No resolved
crypto money-movement detections yet … Populates once the Crypto Money Gradient is live."
All render only when `mode === 'crypto'` → crypto-scoped. Fix: branch the string on `crypto`
to positioning vocabulary ("crypto positioning reads/detections"); the equity (`money`) branch
keeps its wording.

**D-W4 · DEFECT — `web-terminal/src/views/Ledger.tsx:258`**
Shared price-ledger table header `<th className="r">Money @ call</th>` renders in crypto mode
too. Fix: `{crypto ? 'Positioning @ call' : 'Money @ call'}`.

### Mobile

**D-M1 · DEFECT — `frontend/app/(app)/index.tsx:352`**
Crypto section intro: `"The Crypto Money Gradient — Money Movement (informed money via
crypto-exposure proxies) vs Market Confirmation (the coin's own price)…"` — the exact
presentation the Chairman retired, verbatim, as the mobile crypto page's header line.
Fix: mirror the web's retired copy ("Crypto signal — Positioning … vs Market Confirmation").

**D-M2 · DEFECT — `frontend/app/(app)/crypto/[coin].tsx:96, 97, 169, 202–207`**
Detail screen: gauge label `MONEY MOVEMENT` (:96), captions `'no proxy money data'` /
`'informed money · D'` (:97), factor legend `"● money movement · ● market confirmation"`
(:169), and the closing explainer `"…whether money is moving into or out of a coin. Money
Movement "D" = informed / early money…"` (:202-207). The web equivalents were all reworded
in `aae54f8`; the mobile screen — which its own header comment declares "WEB PARITY" — was not.
Fix: adopt the web's `MM_LABEL = 'Positioning'` strings 1:1 (labels, captions, legend,
explainer).

**D-M3 · DEFECT — `frontend/components/trends/CryptoCard.tsx:63`**
Collapsed crypto row's score label is the visible abbreviation `MM` (Money Movement).
Fix: `POS` / `POSITIONING` (and keep the equity `RiskCard`'s `MM` — equity keeps the name).

**D-M4 · DEFECT — `frontend/app/(app)/profile/accuracy.tsx:144`**
Crypto ledger mode banner: `"crypto money-movement reads validated against realized coin
price direction"`. Fix: "crypto positioning reads validated against…".

### OK-BY-DESIGN (money vocabulary that stays)
- `MarketSignal.tsx` (`MM_LABEL='Money Movement'` :104 and all uses), `Grade.tsx:96/100/109`,
  `Dashboard.tsx:261` (`MKT_RANK` "Money Movement"), `Methodology.tsx:183-195` (Money Gradient
  section), `Ledger.tsx` **equity** branch, mobile `risk/[key].tsx:138/206-207`,
  `RiskCard.tsx` `MM`, `index.tsx:418` market hero — all EQUITY Market Signal scope; the Money
  Gradient v2 legitimately keeps its name.
- `Crypto.tsx:7/24/142/326-327/401` — code comments only, explicitly out of scope.

---

## 2. FORBIDDEN WORDS IN THE DIVERGENCE RENDERINGS — **PASS**

Programmatic check of every client-facing divergence string in `web-terminal/src/views/Crypto.tsx`
(`PVP_LABEL`, `PVP_HEADER_TIP` :64, `PVP_ABSENT_TIP` :68, `PvpCell` :89-103, the
"Positioning vs Price Register" panel :228-238, and "About Positioning vs Price" :245-267)
against the banned list (`money movement, inflow, distress, warning, risk, fragile, unwind,
overheated, crash, bubble`): **zero hits**. "Leverage/leveraged" appears and is not on the list.
The crypto flow chips' `inflow/outflow` (`Crypto.tsx:113-114`, direction filter :291-296) belong
to the separate live proxy-flow signal — allowed by the stated rule. The divergence block is the
only web surface rendering the sealed signal; mobile renders no divergence UI at all (see §7).

---

## 3. NaN RISKS + §17 SOURCE-DISPLAY

**No live NaN path found.** Specifically verified:
- Both platforms' "Score Components" NaN panels remain removed with tombstone comments
  (`MarketSignal.tsx:532-534`, mobile `risk/[key].tsx:546-551`); Market Factors reads `.score`
  with `n/a`/`—` (`MarketSignal.tsx:355-366`, `Crypto.tsx:193-201`, mobile `risk/[key].tsx:219-231`,
  mobile `crypto/[coin].tsx:148-164`). No `Number()` on an object anywhere
  (all `Number()` call sites in both trees inspected).
- Guarded date math (`isNaN` checks: `Screener.tsx:44`, `Grade.tsx:18`, `Ledger.tsx:42`,
  `MarketSignal.tsx:44`, `ScoreChart.tsx:23/30`).
- `frontend/app/(app)/risk/[key].tsx:92` `Math.abs(mg.gap)` cannot NaN — `gradientApi.ts:502`
  maps `gap: Number(r.market_gradient.gap ?? 0)`.

**§17 gating verified present** (coverage sections render only with real content; no
"0 articles"/"not in recent uploads" rows): web `MarketSignal.tsx:424-452` (hasNews /
coveredCreators / hasBroadcast), mobile `risk/[key].tsx:331-336`, web `Screener.tsx:447`
(Dark Matter section gated `dm > 0`), `Crypto.tsx:168/211` (supply & price blocks),
`SignalAnalysis.tsx:31-38` (empty → renders nothing), web `MarketSignal.tsx:311-318`
(honest AI-context absence with reason). **PASS.**

**N-W1 · NIT — `web-terminal/src/views/Screener.tsx:91-106`** — `scoreFor` =
`Math.round(Number(c?.score ?? 0))`: an absent component renders `0` in the Score Breakdown
(incl. `D_dark_matter`). Mirrors the known open engine defect (round-4 (2)(a): D serves a
fabricated 0), so the client currently cannot distinguish; when the engine ships the D fix,
this `?? 0` will keep manufacturing floors. Fix alongside the engine change: render `—` for
`score == null`.

---

## 4. HONEST-ABSENCE REGRESSIONS (§16a/C1)

**D-W5 · DEFECT — `web-terminal/src/views/Dashboard.tsx:107 + 142-144`**
`C = coins.map(c => ({ …, mm: r0(c.money_movement) }))` then the `top-crypto` tile ranks by and
prints `mm`. `r0(v) = Math.round(Number(v || 0))` → every `money_data_absent` coin (per D8,
currently ALL of them) renders **0 as a measured value** and is ranked on it — a numeric floor
wearing a measured badge, on the dashboard, for the exact signal whose rail carefully renders
"NOT MEASURED". Fix: absent → `'n/a'` text (not 0), rank by `market_confirmation`, or retitle
the tile to a confirmation read.

**D-M5 · DEFECT — `frontend/components/trends/DarkMatterPanel.tsx:66`**
Section heading `Under-the-Radar Signals · {dm ?? 0}/100` — when `darkMatter` is null but
`firstTimerRatio`/`engagementAsymmetry` exist (so the early-return at :47 doesn't fire), the
heading prints **0/100**: the precise "floor value wearing a measured badge" the 2026-08-20
board fixed one line lower. Fix: `dm != null ? \`· ${dm}/100\` : ''`.

**D-M6 · DEFECT — `frontend/components/trends/DarkMatterPanel.tsx:56-58, 78`**
`dUnmeasured = dMeasured === false || (dMeasured === undefined && firstTimerRatio == null)` —
the NULL/unknown stratum **with** a (stale) ratio present falls to the numeric branch and
renders `${ftrPct}%` as a measured reading. The web fixed exactly this with 4c TRI-STATE
(`Screener.tsx:228-237`: NULL → "UNKNOWN — readability not recorded", never a number). Per
round-4 finding (2)(b), >90% of topics sit in the NULL stratum. Fix: port the web tri-state —
ratio renders only when `dMeasured === true`; `undefined` → UNKNOWN wording, `false` → UNMEASURED.
(Sibling: `WhyScoresDiverge.tsx:26-33` at least suppresses the number for the NULL stratum, but
pools NULL into the "Unmeasured — D could not be read" wording; web distinguishes UNKNOWN. NIT
N-M1.)

**D-M7 · DEFECT — mobile has NO ABSENT-tier treatment (C1/K1 parity)**
- `frontend/lib/marketCategories.ts:146-149` — `MARKET_TIER_COLOR` has no `ABSENT` key;
- `frontend/lib/gradientApi.ts:978` — `tier: c.tier ?? 'ROUTINE'` **fabricates a measured tier**
  for a missing one (and :501 `tier || 'DORMANT'` on the market side);
- `frontend/app/(app)/crypto/[coin].tsx:53/73` and `CryptoCard.tsx:30/56` render `c.tier`
  as plain colored text with a `#9A9AA2` fallback — an engine-served `ABSENT` (declared in the
  type at `gradientApi.ts:949`) would render as a filled/plain tier in DORMANT's measured grey —
  the exact K1 defect the web fixed with `AbsentTierChip` (`Crypto.tsx:46-54`, hollow, dashed,
  distinct `#6E7A8A`). `absence_class` is not consumed anywhere on mobile.
Fix: map `ABSENT` to a hollow "NOT MEASURED" chip (Aurora form), never default a missing tier
to ROUTINE/DORMANT, and carry `absence_class` through `fetchCrypto`.

**D-W6 · DEFECT (low) — `web-terminal/src/views/MarketSignal.tsx:440`**
Creator-coverage heading `style={{ color: MC.red }}` — red for a coverage source's name.
The web's own hue contract (`mobileTheme.ts:4`, §12) is **red = loss/error ONLY**; a creator
covering a stock is neither. (Mobile uses `#B11226` here — legal there, it is Aurora's ACCENT.)
Fix: `MC.textSec` or the amber emphasis used elsewhere on the rail.

**N-W2 · NIT — `web-terminal/src/views/MarketSignal.tsx:249`** — absent money read renders
`ring(0,'var(--line)')` + "n/a": honest value, but a solid zero-arc track rather than the C1
dashed `absentSlot()` the crypto rail uses (`Crypto.tsx:26-32`). Inconsistent absence rendering
on the same platform; adopt the dashed empty slot.

**N-M2 · NIT — `frontend/app/(app)/risk/[key].tsx:161`** — no-gradient fallback ring
`score={risk.positioningScore ?? 0}` with caption `/100` — a missing positioning score draws a
measured-looking 0 ring. Render an empty state instead.

**OK-BY-DESIGN (red family):**
- Outflow chips red on both platforms (`Crypto.tsx:114` MC.red; mobile `#B11226`) — net informed
  selling is the down/loss direction family, consistent with `pct down` rows; cross-platform
  consistent. Noted, not flagged.
- `ELEVATED` tier / `VIRAL` stage / `SPIKE_VS_SELF` baseline / gap-band-3 in the red family on
  both surfaces (`mobileTheme.ts:31/53/67/100`, mobile `signals.ts:405`, `risk/[key].tsx:38`) —
  a long-standing cross-platform "intensity" convention that predates the one-meaning-per-hue
  wording and is hue-MEANING-consistent across surfaces. Flagging it would require a board-level
  palette decision, not a parity fix; recorded here as standing tension with §12, not a defect
  introduced by any recent change.
- `Ledger.tsx:275` `NOT_CONFIRMED` verdict in red — a miss IS the loss meaning. Correct.
  (Hex is `#DC2626`, not `MC.red` — cosmetic inconsistency only; web has no #DC2626 ban.)

---

## 5. K17 CLASS — `Math.abs()` WHERE THE SIGN DIES IN DISPLAY (complete enumeration)

Every `Math.abs` call site in both trees was read in context. Sign-losing DISPLAY instances:

### Web — the known instance + **4** more files (board estimated "up to 3")

| # | file:line | What renders | Why defective |
|---|---|---|---|
| K17-W1 (known) | `web-terminal/src/views/Crypto.tsx:160` | `` `· ${Math.abs(c.gap)}-pt gap` `` in the rail's gap headline | A −18 (price leading positioning) prints identically to +18; only `gap_state` hints direction, and it can be absent. The Lead column (:406) prints signed — same page, two answers. |
| K17-W2 | `web-terminal/src/views/MarketSignal.tsx:339` | `` (mg.gap_state \|\| `${Math.abs(row.gap)}-pt gap`) + ` · ${Math.abs(row.gap)}-pt gap` `` | Sign lost twice — **and a duplicate-print bug**: with `gap_state` falsy and not calibrating it renders "12-pt gap · 12-pt gap". Fix: signed value once, `gap_state` as the label. |
| K17-W3 | `web-terminal/src/views/Grade.tsx:40 → 132` | `gap = Math.abs(Math.round(heisenberg_gap ?? det−conf))` → `"{gap}-point gap — {band.label}"` | A lagging topic (conf ≫ det) is banded and captioned as if EARLY ("Very early — detected, not confirmed") — the abs value indexes direction-asserting band labels. Same bug in the mobile twin (K17-M5). |
| K17-W4 | `web-terminal/src/views/Dashboard.tsx:132` | `pill('gap ' + Math.abs(x.det − x.conf))` on the min-gap tile | Unsigned "gap 12" — det-lead vs conf-lead indistinguishable. Print signed like every table row does. |
| K17-W5 | `web-terminal/src/views/Screener.tsx:149-155` (`deriveDivergence`) | `g = Math.abs(gap)`; summary at g≥18: "early-edge components run **well ahead of** cross-platform confirmation" | For a NEGATIVE gap the prose asserts the wrong direction. (`gapInterp` :78-84 handles `d < 0` first — this function doesn't.) Add a negative-gap branch like the "Signal Read" section (:546-552) has. |

**Web OK-BY-DESIGN abs uses:** `Screener.tsx:79` (negative handled first → LAGGING),
`Screener.tsx:51/797`, `MarketSignal.tsx:51/747`, `Watchlists.tsx:18/205`, `Login.tsx:10/177`
(booleans/row classes; the printed gap value is signed in each), `Dashboard.tsx:115/131`
(sort keys only), `mobileTheme.ts:71` (band index; callers print signed — except Grade, flagged),
`ScoreChart.tsx:72` (hover hit-test distance).

### Mobile

| # | file:line | Detail |
|---|---|---|
| K17-M1 | `frontend/lib/gradientApi.ts:89` | `gap: Math.abs(det − conf)` — the **data layer** discards the sign for every trend Signal; nothing downstream can recover it. |
| K17-M2 | `frontend/lib/signals.ts:537` | `scoreGap = s.gap ?? Math.abs(det − conf)` — abs fallback; and `gapBandIndex` callers (`signal/[id].tsx:95-149`) treat any negative as "aligned". |
| K17-M3 | `frontend/app/(app)/risk/[key].tsx:92 → 150-151` | `Math.round(Math.abs(mg.gap))` → `"· {gap}-pt gap"` — mobile twin of K17-W1/W2. |
| K17-M4 | `frontend/app/(app)/crypto/[coin].tsx:56 → 112` | `gapAbs = Math.abs(round(c.lead*10)/10)` → `"· {gapAbs}-pt gap"` — while `CryptoCard.tsx:80` prints the same `lead` SIGNED (`+`/−). Same value, sign kept in the list, dropped in the detail. |
| K17-M5 | `frontend/components/trends/GradeTool.tsx:216` | Same as K17-W3 (abs-indexed direction-asserting band label). |

**Mobile OK-BY-DESIGN:** `profile/watchlists.tsx:245` (abs only for the color threshold; the
printed gap is signed), `TrajectoryCard.tsx:52` (hit-test).

Recommended single fix pattern (the one `Crypto.tsx:70` already codifies for PvP): print via a
`signed()` helper; use `Math.abs` only for banding/thresholds; never let an abs value select a
direction-asserting sentence.

---

## 6. DISCLAIMER DRIFT

Canonical (founder-approved 2026-07-07, verbatim):
`*All information contained herein may not be accurate including any and all figures indicated
in this section and or site and may be an approximation and should not be construed as
financial, investment, or legal advice.`

| Copy | Verdict |
|---|---|
| `web-terminal/src/components/Disclaimer.tsx:5` (`LEGAL_DISCLAIMER`) | canonical — byte-identical ✓ |
| `frontend/components/ui/Disclaimer.tsx:9-12` | byte-identical after JSX whitespace collapse (verified programmatically) ✓ |
| Inline "AI-generated overview" variants — `Crypto.tsx:162`, `Screener.tsx:330`, `MarketSignal.tsx:320/341`, mobile `crypto/[coin].tsx:122-126`, `TopicResearch.tsx:48` | carry the FULL founder sentence verbatim (± the leading `*`; TopicResearch keeps it) ✓ |
| `web-terminal/src/components/Shell.tsx:236` (footer) | full sentence, **leading `*` dropped** — **NIT N-W3** (cosmetic; restore the `*` or import `LEGAL_DISCLAIMER`). |
| **`web-terminal/src/views/History.tsx:159`** | **D-W7 · DEFECT (drift)** — truncated edit: `"…may not be accurate and should not be construed…"` — drops *"including any and all figures indicated in this section and or site and may be an approximation"*. The founder text is sign-off-to-edit; this is the only drifted copy in either tree. Fix: import `LEGAL_DISCLAIMER` (the canonical `<Disclaimer/>` at :152 already covers the section; this ad-hoc line should either be the verbatim string or a clearly distinct AI-note that doesn't half-quote it). |
| "Be advised that this summary may be inaccurate…" (`Crypto.tsx:284`, `MarketSignal.tsx:344`, mobile `crypto/[coin].tsx:206-207`) | a different, deliberate sentence, identical across platforms — not the founder disclaimer ✓ |

---

## 7. MOBILE-SPECIFIC CHECKS

- **Crypto screens exist** (premise correction #1 above): entry via the dashboard `crypto` mode
  (`index.tsx:348-392` → `CryptoCard` → `/crypto/[coin]`). All the retired-vocabulary findings
  D-M1…D-M4 live there. Mobile renders NO divergence UI (no PvP column/panel/explainers) — that
  is acceptable ("web may add more") but note the mobile crypto detail still points users at
  "the crypto accuracy ledger" (`crypto/[coin].tsx:205-206`) where the web crypto rail's panel
  was replaced by the Positioning-vs-Price Register — content-parity drift to resolve with D-M2.
- **Divergence merge isolation — VERIFIED:** `git diff --name-only 70119d4^1 70119d4 -- frontend/`
  → **0 files**. The merge touched `web-terminal/src/views/Crypto.tsx`, `web-terminal/src/lib/api.ts`,
  engine/tooling only. ✓ (The wording retirement itself was the follow-up commit `aae54f8`,
  also web-only — which is exactly why the mobile crypto surface was left behind.)
- Mobile market/risk screens: defect classes covered in §§3-5 (D-M7, K17-M3, N-M2); §17 gating
  present (`risk/[key].tsx:331-336`); no NaN path found.

---

## 8. CROSS-PLATFORM PARITY — web MarketSignal rail vs mobile `risk/[key].tsx`

Sections present and matching on BOTH (data points aligned): disclaimer top+bottom · dual
rings with v2 labels · absent-money "n/a" + "Market-Confirmation only" notice · macro-theme /
insufficient-data notices · gap-state band + interpretation · AI Context · Market Factors
(feeds-colored, `n/a`, composite_note) · tier legend · Financial Sustainability (raw +
sector-adjusted) · Retail/Media Coverage (§17-gated) · Leverage & Funding (FINRA/OFR/13F) ·
Market Tenure · Vs-Own-Baseline · Diffusion Pipeline · Sources · positioning-not-advice footer.
Hue MEANINGS consistent (detection blue-family `#2D7EEF`/`#2A5B9E`, confidence green
`#00C896`/`#2E7D5B`, both-purple, red family in the same roles). Hex differences are
per-surface by design — none flagged.

**Parity breaks (mobile side):**

**D-M8 · DEFECT — mobile tier legend still says BUILDING.**
`frontend/app/(app)/risk/[key].tsx:44` — `{ key: 'BUILDING', range: '40–59', desc: 'Building,
not yet elevated' }` vs web/engine `MODERATE 40–59` (`mobileTheme.ts:85`; the BUILDING→MODERATE
rename shipped "engine + web + mobile" per CLAUDE.md §15, 2026-06-26 — the mobile legend was
missed; `marketCategories.ts:37` even filter-matches both). An engine-served MODERATE tier chip
sits above a legend that has no MODERATE row. Fix: rename the legend row (color map already has
both keys).

**D-M9 · DEFECT — mobile market & trend details have NO Signal Analysis section.**
Web renders `SignalAnalysisPanel` on all three rails (`MarketSignal.tsx:349`, `Screener.tsx:366`,
`Crypto.tsx:187`). On mobile it exists as a component and is used ONLY by `crypto/[coin].tsx:132`
and `profile/accuracy.tsx:304`; `git log -S SignalAnalysisPanel` shows it was **never** wired
into `signal/[id].tsx` or `risk/[key].tsx` — despite CLAUDE.md (2026-06-26) recording it "LIVE
on … mobile (trend signal/[id] + market risk/[key])". Both a section-parity break and a stale
doc claim. Fix: add the panel to both screens (the component is mobile-ready), or correct the
record.

**D-M10 · DEFECT — mobile market detail lacks the N / Platform Indicator card.**
Web market rail: `MarketSignal.tsx:258-289` (N card + N-inclusive what-if + convergence).
Mobile `risk/[key].tsx` has no N section at all. Same-sections rule (§12: web may add *denser
filters/extra columns*, but N is a headline data point of the market detail on web, and mobile's
trend detail does surface N in its breakdown). Fix: port the N card (or record a ruling that N
is web-only on market detail).

**N-M3 · NIT** — mobile `risk/[key].tsx:166-170` explainer footer still describes the v1
Detection/Confidence framing for ALL rows; the web footer branches to the v2 Money-Movement
explanation when `row.v2` (`MarketSignal.tsx:343-345`). Mobile shows v2 labels above and v1
prose below.
**N-M4 · NIT** — web appends the AI-generated-overview disclaimer under `interpretation`
(`MarketSignal.tsx:341`); mobile `risk/[key].tsx:153-155` renders interpretation without it
(the screen carries the founder disclaimer top+bottom, so legal coverage is intact — parity
polish only).

---

## 9. COVERAGE TABLE (what was actually read — absence of findings is meaningful only here)

| Surface | File | Depth |
|---|---|---|
| Web Dashboard | `web-terminal/src/views/Dashboard.tsx` | full read |
| Web Trends (screener + rail) | `web-terminal/src/views/Screener.tsx` | full read of rail/derivations/rows (lines 1–560, 735–830); remainder grep-scanned |
| Web Market Signal + rail | `web-terminal/src/views/MarketSignal.tsx` | full read (1–560, 600–771) |
| Web Crypto + rail | `web-terminal/src/views/Crypto.tsx` | full read |
| Web Grade | `web-terminal/src/views/Grade.tsx` | full read |
| Web History | `web-terminal/src/views/History.tsx` | full read |
| Web Watchlists | `web-terminal/src/views/Watchlists.tsx` | head + rows read; rest grep-scanned |
| Web Alerts | `web-terminal/src/views/Alerts.tsx` | head read + defect-class grep (clean) |
| Web Accuracy Ledger | `web-terminal/src/views/Ledger.tsx` | full read (30–361) |
| Web Methodology | `web-terminal/src/views/Methodology.tsx` | targeted read (§Money Gradient, ledger prose) + grep |
| Web Account / Login / Shell | `Account.tsx`, `Login.tsx`, `Shell.tsx` | defect-class grep + targeted reads (footer, demo rows) |
| Web components | `Disclaimer.tsx`, `SignalAnalysis.tsx`, `ScoreChart.tsx` (hit-test/labels), `lib/mobileTheme.ts`, `lib/api.ts` (crypto/divergence types) | full read (ScoreChart: abs/NaN sites) |
| Desktop | `tauri-desktop/src-tauri/tauri.conf.json` | confirmed pure wrapper of `web-terminal/dist` — inherits every web finding, nothing separate |
| Mobile dashboard (trends/market/crypto/grade modes) | `frontend/app/(app)/index.tsx` | targeted read (85–130, 340–430) + grep |
| Mobile trend detail | `frontend/app/(app)/signal/[id].tsx` | imports + gap/render sites read; grep |
| Mobile market detail | `frontend/app/(app)/risk/[key].tsx` | full read |
| Mobile crypto detail | `frontend/app/(app)/crypto/[coin].tsx` | full read |
| Mobile crypto row | `frontend/components/trends/CryptoCard.tsx` | full read |
| Mobile market row | `frontend/components/trends/RiskCard.tsx` | full read (38–100) |
| Mobile DarkMatterPanel / WhyScoresDiverge | both files | full read |
| Mobile GradeTool | `frontend/components/trends/GradeTool.tsx` | ProposedCard read (210–235) + grep |
| Mobile Accuracy Ledger | `frontend/app/(app)/profile/accuracy.tsx` | targeted read (10–30, 100–180, 300–310) + grep |
| Mobile libs | `lib/gradientApi.ts` (signal/market/crypto mappers), `lib/signals.ts` (scoreGap/GAP_BANDS), `lib/marketCategories.ts` | targeted reads of every mapping/abs site |
| Mobile ui Disclaimer / TopicResearch | both | disclaimer strings read + byte-compared |
| Mobile remaining screens (search, history, alerts, watchlists, favorites, market-category/[key], category/[stage], profile/*) | | **grep-scan only** (money-vocab, Math.abs, Number(), NaN, disclaimer variants — all clean); not line-read |

---

## 10. TOP FIXES IN PRIORITY ORDER

1. **D-M1…D-M4** — apply the Chairman's crypto vocabulary retirement to the mobile crypto
   surface (dashboard intro, detail labels/legend/explainer, `MM` chip, accuracy banner);
   it is one commit mirroring `aae54f8`'s strings.
2. **D-W5** — stop the dashboard crypto tile printing/ranking absent money reads as 0.
3. **D-M6 + D-M5** — port 4c tri-state into `DarkMatterPanel` and kill the `dm ?? 0` heading
   (>90% of rows are the NULL stratum; mobile is currently asserting numbers web refuses to).
4. **K17 sweep** — 5 web + 5 mobile sites (§5), one `signed()` helper + a negative-gap prose
   branch; includes the MarketSignal double-print.
5. **D-W1…D-W4** — web Dashboard tile title + the three crypto-mode Ledger strings + the
   shared "Money @ call" header.
6. **D-M7 / D-M8 / D-M9 / D-M10** — mobile ABSENT-tier treatment, BUILDING→MODERATE legend,
   Signal Analysis + N-card parity (or a recorded ruling).
7. **D-W7** — restore the verbatim founder disclaimer in `History.tsx:159`.

*Audit performed read-only per instructions; no source files modified, nothing committed.*
