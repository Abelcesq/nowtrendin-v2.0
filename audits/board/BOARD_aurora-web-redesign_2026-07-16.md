# BOARD REVIEW — Aurora Web-Terminal Redesign (design input + analysis)
**Date:** 2026-07-16 · **Convened by:** founder (Chairman) · **Material:** branch
`aurora-web-redesign`, staged at nowtrendin-terminal (gh-pages prod untouched).
**Founder lens:** end users are hedge funds, bankers, traders — the institutional
experience may legitimately differ from the consumer/mobile experience.

Six independent archetype memos, identical evidence pack, no cross-contamination.
Three memos verified the LIVE staging build independently (Guardian, Outsider,
Executioner — the Executioner hash-matched staging against a local build).

## DECISION TABLE

| Item | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist |
|---|---|---|---|---|---|---|
| A — Aurora-on-web direction | AWC | APPROVE | APPROVE | AWC | SHIP | APPROVE |
| B — token mapping | **REJECT as shipped** | AWC | AWC | AWC | SHIP after 2 fixes | AWC |
| C — merge readiness | **REJECT (merge date)** | AWC | AWC (self-host font) | AWC | SHIP-LATER (founder walk) | AWC |

**Unanimous on direction:** one design language across surfaces strengthens the
institutional read; the five deliberate divergences (dark chrome, 13px density, no gold
hero, hover kept, flows unchanged) were called the RIGHT divergences by every memo.

## THE CONVERGENT FINDING (all six, three verified live): GARNET DOUBLE-BOOKED
The first-pass transform mapped BOTH the old orange emphasis AND the old error/down red
onto garnet #B11226 (`--early` and `--down` literally identical; ~17 semantics on one
hue, five opposite-valence). On a trading desk red is a reserved word (loss/halt);
positive deltas rendered red on the login page. Verdict across memos: fix before merge.

## CONVERGENT CONDITIONS (and their status — rev 2 applied same-day)
1. One meaning per hue: red = loss/error/alarm ONLY; emphasis -> midnight #1B3066;
   wordmark -> brand orange #E8551C; dark-chrome accents -> accentSoft #F0758A. ✅ FIXED (rev 2)
2. Contrast: thead + stage-pill text to >=4.5:1 shades (the old dark-shade discipline). ✅ FIXED
3. Search fields must not read as an error state at rest. ✅ FIXED (neutral + midnight focus)
4. True-monospace numerals (Jakarta-first --mono risked column alignment). ✅ FIXED
5. Stray #2f6fed avatar hex (the "zero banned hexes" claim was false). ✅ FIXED
6. Override-block phantom classes (.hv-item/.wl-card/.g-box didn't exist). ✅ FIXED (real classes)
7. titleCase coverage (3 of ~8 views -> same topic, two labels). ✅ EXTENDED (Alerts/
   Watchlists/Dashboard added). ⚠ residual: naive casing ("Mcgregor") — mobile ships the
   same behavior (parity); a casing dictionary is a shared future fix, founder's call.
8. Self-host Plus Jakarta Sans (bank proxies/GDPR/Tauri phoning Google). ⚠ OPEN —
   DISAGREEMENT: Expansionist wants it BEFORE merge; Executioner cut it from merge scope
   (font fails open via display=swap + fallbacks). Founder decides.
9. FOUNDER WALK of the 13 authenticated views on staging with live data — the risk agents
   cannot retire. ⚠ OPEN (the gate). Checklist: numbers align in columns · no ghost old-
   palette panel · pill text readable · hover states sane · casing acceptable · nothing
   reads alarmist where data is positive.

## OTHER DISAGREEMENTS / NON-BLOCKING NOTES
- Off-white canvas vs pure #FFF (Outsider: glare on long desk sessions) — not applied,
  founder taste call.
- Dark mode: multiple memos call it the obvious v2 (the token refactor made it cheap).
- Gold-as-text in Grade view contrast (2.4:1) — bounded follow-up.
- Favorites persist old hex colors server-side (cosmetic follow-up).
- Economist prescriptions: emphasis must stay a disclosed mechanical rule; ledger +
  verbatim disclaimer keep full prominence in the new skin; login stays dry.
- Post-merge: /terminal-deploy-parity + /frontend-consistency; reconcile CLAUDE.md §3/§11.

## MERGE SEQUENCE (Executioner, adopted)
Founder walk on staging -> merge --no-ff to main -> build -> note current gh-pages SHA
(rollback pointer) -> deploy gh-pages -> sync Heroku mirror -> parity one-hash check ->
smoke (CDN index can lag ~10 min; don't panic-rollback) -> /frontend-consistency.
Rollback = repush prior gh-pages SHA (~2 min); zero engine/schema coupling.

## ARCHETYPE MEMOS (verbatim)

---

# BOARD MEMO — The Challenger
## Aurora web-terminal redesign (branch `aurora-web-redesign`) — design review for the institutional audience
**Date:** 2026-07-16 · **Reviewer:** The Challenger · **Evidence:** board pack; full read of `web-terminal/src/styles.css` (incl. the Aurora override block, lines 658–692), `web-terminal/src/lib/mobileTheme.ts`, diff `main..aurora-web-redesign` (index.html, App.tsx, Shell.tsx, Login.tsx); grep of `titleCaseTopic` call sites and directional-glyph usage; `main`'s prior token block for regression comparison. WCAG ratios below are computed from the actual hexes.

My brief: attack the redesign — where can it MISLEAD or degrade an institutional user's read of the data? Findings ordered by severity.

---

## ATTACK 1 — Garnet #B11226 is doing seventeen jobs, five of them with opposite valence (DISQUALIFYING as shipped)

This is not a subjective "collision risk" — it is literal at the token level:

```css
--early:#B11226;  --down:#B11226;      /* NEW: identical */
```

The **prior** design kept these apart: `--early:#df7a36` (orange emphasis) vs `--down:#DC2626` (red loss). The Aurora mapping **merged emphasis and loss into one hex.** For hedge funds and traders, red is the single most overloaded convention in the industry: red = loss, unambiguously, pre-attentively, before any label is read.

Inventory of what #B11226 now means in this one terminal (all from the shipped CSS/TS):

| Semantic | Where | Valence |
|---|---|---|
| Negative price/velocity move | `.pct.down`, `.vel.down`, `▼ outflow` (`MC.red`, MarketSignal/Grade/Ledger) | BAD |
| FALSE_POSITIVE ledger verdict | `.verdict.FALSE_POSITIVE` | BAD (our own miss) |
| Error text | `.g-err`, `.al-err`, `.lg-err`, `.lg-field.err` (via `--down`) | BAD |
| Delete/remove affordances | `.fav-del`, `.rm:hover`, `.dash-del`, `.wl-del:hover` | DESTRUCTIVE |
| "Early" emphasis — the value prop | `--early`: `.gapnum.wide`, `.statcard .sv.early`, gap band 36–60 "very early" | GOOD (the edge) |
| The proprietary N score | `.n-val`, `.n-card` frame, `MC.orange` | GOOD (flagship) |
| VIRAL stage | `STAGE_COLOR.VIRAL` | GOOD/strong signal |
| ELEVATED / WATCH / UNUSUAL market tier | `.tier.ELEVATED`, `MARKET_TIER_COLOR.ELEVATED` | ALERT |
| SPIKE_VS_SELF baseline | `BASELINE_META` | ALERT |
| Brand wordmark "TrendIn" accent, nav-active icon, sort indicator, search accent, bell dot, save buttons, calibration banner | chrome-wide | NEUTRAL/BRAND |

Concrete misread scenario, one screen: a Market Signal row shows tier **ELEVATED** (garnet pill), the % change column shows **−3.2% in garnet**, the sorted column header carries a **garnet sort caret**, the right rail shows **N = 87 in garnet**, and a gap number of 42 is garnet meaning **"very early — detected, not confirmed."** Four of those five are supposed to mean *materially different things* — loss, alert, brand emphasis, opportunity. A trader scanning color cannot separate "we detected this early" (buy-side edge) from "this is falling / this was a false positive / this is an error." The system's OWN accuracy failures (`FALSE_POSITIVE`) render in the same hue as its flagship N score. That is a self-inflicted credibility wound in front of exactly the audience that reads color fastest.

**Mitigations that genuinely exist** (fairness): directional glyphs accompany most up/down colors (`TrendingUp/TrendingDown` icons, `▲/▼` prefixes), so direction is not encoded by color alone. And garnet on white passes contrast at 7.1:1. Neither fixes valence contamination: glyphs disambiguate *direction*, not *emphasis-vs-loss*.

**The emerald collision (`--up` = `--conf` = #2E7D5B) is inherited, not new** — the old design already had `--up` = `--conf` = #00C896. I flag it (a Confidence gauge reading 28 still renders in "up-green"), but it is not a regression of this branch and I do not hold the merge to it.

**Required fix:** split the tokens. `--down` must be a hue that is NOT the brand accent (or the reverse: move brand emphasis off garnet). Minimum acceptable: distinct hexes for {loss/error}, {alert tier}, {brand/N/early emphasis}, with the loss hue never appearing in chrome. "Garnet is the Aurora accent" is a mobile constraint; mobile has no P&L columns. The founder's own lens — institutional may legitimately differ — cuts exactly here.

---

## ATTACK 2 — Contrast regressions, with numbers (WCAG AA = 4.5:1 normal text; these are 8.5–13px)

Computed from the shipped hexes:

| Element | Colors | Ratio | Verdict |
|---|---|---|---|
| Muted text `--text-3:#9A9AA2` on white | 9A9AA2 / FFFFFF | **2.8:1** | FAIL — and it is now the TABLE HEADER color (`thead th{color:#9A9AA2}` in the override) at 10px uppercase. Column identification in a dense screener at 2.8:1. Old `--text-3` was #8a97a7 (~3.2:1, also weak, but headers were not remapped to it). |
| Wordmark "TrendIn" garnet on ink topbar | B11226 / 0C1B3A | **2.4:1** | FAIL — was orange-on-ink at ~5.8:1. The brand got dimmer on the surface it lives on 100% of the session. |
| Active nav icon garnet on `--ink-3` | B11226 / 233B72 | **1.5:1** | Effectively invisible. `.nav-item.active .ni{color:var(--early)}`. |
| Gold #C9A24B text (MODERATE/BUILDING tier, RESURGENT maturity, gap band 16–35) on white/tint | C9A24B / ~white | **2.4:1** | FAIL. |
| Slate MONITORING/DECAY pill text on its 1A tint | 8A8F9C / ~white | **2.9:1** | FAIL. |
| Emerald BREAKOUT pill text on its 1A tint | 2E7D5B / ~white | **4.4:1** | Borderline fail at 10px bold (not "large text"). |
| Sapphire STRONG pill | 2A5B9E | 6.0:1 | Pass. |
| Rose WATCHING pill | A8456A | 5.0:1 | Pass (barely). |
| Search placeholder #A7808C on pink #F7E4E7 | | **2.8:1** | Weak. |
| Login hero `em` garnet on ink (PUBLIC page) | B11226 / 0C1B3A | **2.4:1** | The headline emphasis on the marketing surface fails. |

The old stylesheet carried an explicit discipline, in its own comment: *"Stage-pill text is a readable dark shade of each mobile hue"* — e.g. EMERGING text was #8a6d0f (darkened gold), not raw gold. The Aurora override **dropped that discipline**: pill text is now the raw jewel hue on its own `{color}1A` tint. Two of five stage pills fail, one is borderline. Restoring darkened text shades per pill (keeping the jewel tint backgrounds) fixes this without touching the Aurora look.

---

## ATTACK 3 — The permanently-red search field reads as an error state, and dilutes real alarms

`.search input`, `.chip-search`, `.hv-search`: pink `--early-soft` fill + garnet border + a 30%-alpha garnet focus ring — **at rest, always**. In every institutional convention (and this terminal's own `.lg-field.err` / `.lg-err`, which use near-identical red-tinted treatments), a red-bordered pink input means *validation failure*. The calibration WARNING banner (`.cal-banner`) uses the same pink/garnet family. So the resting search box, a genuine data-integrity warning, and a form error are one visual class. First-session enterprise users will read the terminal as "something is wrong"; long-term users will learn to ignore the pink family — which is exactly the alarm you cannot afford to have ignored on a data-integrity product. Neutral or ink-accented search restores the hierarchy.

---

## ATTACK 4 — The borderless-card sweep is partially applied, provably unverified, and erases pane boundaries

The override removes borders from a class list that includes **three selectors that do not exist in the codebase**: `.hv-item` (real class: `.hv-row`), `.wl-card` (no such class), `.g-box` (real: `.g-grade-box`/`.g-card`/`.g-row`). Meanwhile the real History rows, Grade cards, gauges, div-cells, tier-cells, and coverage cards **keep** their 1px borders. Result: a mixed language — half the terminal borderless Aurora, half old bordered — and direct evidence the sweep was greps-and-hope, not per-view visual verification. "Zero banned hexes, tokens verified live" verifies the *palette*, not the *design*.

Worse, `.rail-card` has **no background fill of its own** (it sat on `--surface` and was defined by its border alone). With `border-color:transparent`, the right-rail cards (Accuracy snapshot, movers) dissolve into an undifferentiated grey column — real information-boundary loss on the densest pane. Also: `.rail,.sect{border-color:#F1F1F4}` makes the rail/table pane divider near-invisible, and table-row hover `#fafbfc` against the new `--surface:#F4F5F8` grid background is a barely-perceptible *lightening*. Under a Bloomberg-style workflow — eyes jumping between panes hundreds of times an hour — pane edges and row feedback are load-bearing, not decoration. Soft-fill cards need actual fills; hover needs a visible delta.

---

## ATTACK 5 — `titleCaseTopic` fabricates wrong proper-noun casing and is inconsistently applied

Engine topic keys are lowercase. The transform (`/[A-Z]/.test(w) ? w : capitalize`) therefore produces, for real topic shapes: **"mcgregor" → "Mcgregor"**, **"iphone 17" → "Iphone 17"**, **"openai" → "Openai"**, **"ai bubble" → "Ai Bubble"**, **"s&p 500" → "S&p 500"**, "bank of america" → "Bank Of America". An *attention-intelligence* platform showing hedge funds "Ai" and "Iphone" is a small, visible, repeated accuracy violation — and this house's first principle is accuracy above all. The interior-capitals guard only protects words that *already* carry capitals, which engine keys never do.

Second, it is applied in exactly three views (Screener, History, Ledger) and **not** in Dashboard tiles, MarketSignal, Grade results, Watchlists, Alerts, or search suggestions. The same topic renders as "Ai Bubble" in the trends table and "ai bubble" in the dashboard tile or alert card — two labels for one entity, sometimes simultaneously on screen (table + rail). Third, exports/API/alert echoes carry raw keys; case-sensitive institutional tooling (joins, dedup scripts) now sees screen labels that don't string-match the data. Either ship a curated casing dictionary (McGregor, iPhone, AI, S&P) or drop the transform on web and show keys verbatim — verbatim is the more institutional choice anyway.

---

## ATTACK 6 — Plus Jakarta Sans was put FIRST in the `--mono` stack; numeric column alignment is now unverified

```css
--mono:"Plus Jakarta Sans",ui-monospace,"SF Mono",...
```

Since Jakarta always loads (index.html Google Fonts link), the monospace fallbacks are dead — every `var(--mono)` consumer now renders a **proportional** face. `font-variant-numeric:tabular-nums` is declared on only TWO selectors (`.num`, `.score-cell`). Everything else that used to get digit alignment *from the font itself* — `.pct` (% change columns), `.gapnum`, `.hist-row`, `.asof b`, badges, counts, `.lg-gn` — now depends on nothing. If Plus Jakarta Sans lacks the `tnum` feature (unverified in the evidence pack), even the two declared cases silently no-op. Misaligned figures in scan columns are the classic "1.11 read as 11.1" error class; on a terminal this is a data-read hazard, not a typographic nicety. Also note: the Google Fonts CDN adds a third-party runtime dependency (FOUT on cold desk loads; CSP-locked and GDPR-sensitive enterprise environments block `fonts.gstatic.com`). Self-host the woff2 and prove tabular figures with a rendered column screenshot, or blanket-apply `tabular-nums`/keep a true mono for numerics.

Minor, same family: white `#FFFFFF` canvas vs the old `#f4f6f8` slightly raises full-screen luminance for 8-hour sessions, and the card model inverted (white-cards-on-grey → grey-cards-on-white). Not disqualifying; worth a founder eyeball at desk brightness.

---

## What is RIGHT (so the verdict is fair)

The five institutional divergences are correct calls, and I want them on the record as such: dark chrome retained (instrument identity), 13px density retained, no gold hero, hover states retained, flows byte-identical. The jewel palette is more credible for this audience than the neon #00C896/#2D7EEF it replaces. The direction is sound; the execution of the meaning-token layer is not.

---

## VERDICTS

**A — Aurora-on-web direction: APPROVE-WITH-CONDITIONS.**
The dark-chrome/density/no-hero divergences show real judgment; jewel tones read more institutional than the neons. Condition: the direction is only safe if the meaning layer is separated from the brand layer (Attack 1). *Strongest attack:* Aurora was designed for a consumer surface with no P&L semantics; porting its accent into a terminal where red carries centuries of financial meaning imports a consumer assumption into an institutional instrument. *Would change my mind:* a trader-task test (n≥3 finance-literate users) reading a Market Signal screen cold, with zero emphasis-vs-loss confusions.

**B — Token mapping: REJECT as shipped.**
`--early` ≡ `--down` ≡ brand ≡ N ≡ FALSE_POSITIVE (#B11226) is disqualifying for this audience; muted text/table headers at 2.8:1, nav-active icon at 1.5:1, and two failing stage pills are objective regressions from the prior "readable dark shade" discipline. *Strongest attack:* the platform's own misses (FALSE_POSITIVE) are painted in its flagship color — an adversarial due-diligence reviewer would screenshot that. *Would change my mind:* a revised token sheet with distinct {loss/error}, {alert}, {brand/emphasis} hues plus a computed contrast table showing every text-bearing token ≥4.5:1 at its used size.

**C — Merge readiness: REJECT.**
Dead selectors (`.hv-item`, `.wl-card`, `.g-box`) prove the retheme was not visually verified per view; rail cards lost their boundaries entirely; `titleCaseTopic` ships wrong proper-noun casing inconsistently across views; numeric alignment is unproven after the mono-stack change; Google Fonts is an unvetted third-party runtime dependency for enterprise clients. None of these is large; together they say "not yet." *Would change my mind:* fixed selectors + per-view screenshots (esp. detail rail and Ledger), tnum proof or self-hosted font with blanket tabular numerals, Title Case dictionary-or-removal, and the Attack-1/2 token fixes. That is roughly a one-day punch list — this is a REJECT of the merge date, not of the work.

*Flag-never-force: everything above is input; the founder decides. But if garnet stays double-booked as both the brand and the loss color, I ask that the decision be recorded as made over this memo's objection.*

— The Challenger

---

# BOARD MEMO — First-Principles Guardian
## Aurora Web-Terminal Redesign · Design Review · 2026-07-16

**Reviewed:** evidence pack (`board_pack_aurora.md`), token mapping table, diff summary,
and the LIVE staging login page (screenshot taken directly from
https://nowtrendin-terminal-1183c0ac00c4.herokuapp.com).

---

## 0. The first principle at stake

Strip the question to its irreducible form. This product's entire claim to existence is:
**it measures attention before it arrives, and a held-out ledger proves it.** For a hedge
fund, a banker, a trader, credibility does not come from styling — it comes from
**semantic reliability**: every encoding on the screen means exactly one thing, means it
every time, and means the same thing on every surface. An instrument is trusted when its
needle never lies, including its *visual* needle.

From that principle, two derived rules govern this review:

1. **Identity may unify; semantics must never collide.** One design language across
   mobile and web strengthens the "one instrument" read — *provided* the unified tokens
   don't overload a semantic channel that finance users have culturally hardwired.
2. **Diverge on ergonomics, converge on identity, and NEVER diverge on data semantics.**
   The same score must look like the same score on every platform (this is already the
   codebase's own doctrine — `mobileTheme.ts`, the Frontend Consistency agent, §12/§17).

---

## 1. Question A — Direction: does unified Aurora strengthen or dilute?

**STRENGTHENS — the founder's instinct is right, for a first-principles reason, not a
taste reason.** Institutions do diligence across surfaces. When the mobile app, the web
terminal, and the desktop app speak one visual language, the product reads as **one
instrument with multiple faces**; when they diverge arbitrarily, it reads as a startup
that hasn't decided what it is — and *that* is what dilutes institutional credibility,
not "consumer-derived styling" per se. Bloomberg's credibility does not come from being
ugly; it comes from being *consistent and dense*. Jakarta Sans at 13px with tabular
numerals and dark chrome does not read consumer; it reads like a modern institutional
product (cf. current-generation fintech terminals). Typeface choice is not where the
institutional read lives — density, latency, and semantic reliability are.

The worry that consumer styling dilutes the instrument would be valid if the redesign had
imported mobile's *ergonomics* (hero cards, gold showcase moments, touch-sized targets,
12px floor, chrome removal). It did not — see below.

**Verdict A: APPROVE.**
**Principle:** one instrument, one language — identity unification is a credibility
asset as long as divergence is reserved for ergonomics and semantics stay collision-free.

## 2. The five divergences — are they the RIGHT five?

Yes — and the reason they're right is that all five sit on the **ergonomics/context
axis**, none on the identity axis and none on the data-semantics axis:

| Divergence | Axis | First-principles read |
|---|---|---|
| 1. Dark chrome kept | Ergonomics/identity of *place* | Correct. Mobile has no chrome to copy — this isn't even a divergence, it's an undefined mapping filled in sensibly. Midnight remap keeps it in-family. A terminal frame signals "instrument," and traders' peripheral vision expects dark chrome. |
| 2. 13px density kept | Ergonomics | Correct and essential. Density IS the institutional read. Had this been loosened to mobile card spacing, I would have rejected A outright. |
| 3. No gold hero | Semantics + restraint | Correct. Gold on mobile is a *showcase* moment; a terminal has no showcase, it has work. Importing a hero would have been the actual "consumer dilution." Gold confined to tier/warning identity is the disciplined call. |
| 4. Hover kept | Ergonomics (input modality) | Trivially correct — pointer vs touch is a physical fact, not a design opinion. |
| 5. Flows unchanged | Trust preservation | The most important one. Enterprise users have muscle memory; a retheme that silently moved cheese would burn trust far faster than any color could build it. Also makes the change AUDITABLE: the diff is 14 files, dominated by styles.css + mobileTheme.ts — reviewable as "tokens only," exactly as claimed. |

No sixth divergence is missing that I can identify, and none of the five is gratuitous.
The founder's lens ("institutional experience may legitimately differ") was applied at
exactly the right altitude.

## 3. Question B — Token mapping: the hidden drift IS there, and it's garnet

I examined the live login page. Three observations from the screenshot:

1. The hero tagline renders "**before it arrives.**" in garnet — as a brand moment on a
   marketing surface, acceptable.
2. The illustrative signal panel renders **EARLY SIGNAL pills in garnet** and the gap
   deltas **+38 / +31 / +22 in red**, while ALIGNED renders neutral slate.
3. The panel is honestly labeled ILLUSTRATIVE and footed "Measurement, not investment
   advice" — good integrity hygiene, noted and commended.

Item 2 is the drift. Per the mapping table, garnet #B11226 now carries **both** the
accent channel ("early"/N/emphasis — the product's *proudest, most positive* signal) and
the generic-red channel (#DC2626 → garnet — error/warning). One hue, two opposite
meanings. For a general consumer this is a mood; for this audience it is a **semantic
error**:

- In finance, red numerals mean one thing, universally and pre-cognitively: **loss /
  danger / halt**. A trader glancing at "+38 in red" experiences a contradiction between
  the sign and the color before conscious reading begins.
- The terminal displays actual market data (Market Signal, Screener, Ledger, crypto)
  where red will *also* legitimately encode negative price direction and genuine
  warnings/errors. Garnet-as-emphasis sitting next to garnet-as-loss next to
  garnet-as-error makes the instrument feel **alarmist** in aggregate and — worse —
  degrades the salience of TRUE warnings. An alarm channel shared with an emphasis
  channel is an alarm channel that cries wolf.
- This is an **integrity issue**, not a taste issue, by the project's own standard
  ([[feedback-integrity-standard]] — the display must not misrepresent the measurement):
  if emphasis reads as warning, the screen asserts a threat the data does not contain.
  §17's spirit ("only reference what contributes") extends naturally to color: only
  signal what the data signals.

**Required fix (condition, not suggestion): split the garnet channel.**
- **Garnet keeps exactly ONE meaning.** My recommendation: garnet = *early/emphasis/N*
  (it is distinctive, in-family with the wordmark maroon #B5341B, and "early" is the
  brand). Then error/warning must move OFF garnet — gold #C9A24B is already mapped to
  warning identity; give hard errors either a clearly distinct red (the old #DC2626 is
  fine — it never had to be "banned" in a semantic slot) or garnet-with-iconography that
  emphasis never uses. The alternative split (garnet = error only, emphasis = ink/flame
  #E8551C) is also acceptable — what is NOT acceptable is one hue in both slots.
- **Numeric-delta rule (hard):** in any data context, a signed numeric delta may be red
  only when the underlying quantity is adverse. Positive lead-time gaps (+38) must not
  render red — use garnet on the pill *label* if "early" keeps garnet, but the numeral
  itself should be ink or the emphasis color, never ambiguous-red next to market data.
- **Audit the three money surfaces** (MarketSignal.tsx, Screener.tsx, Ledger.tsx — all in
  the diff) for garnet adjacency to genuine price-direction reds before merge.

Secondary mapping notes (non-blocking):
- **Sapphire #2A5B9E / emerald #2E7D5B** for Detection/Confidence: correct direction.
  Desaturating the neon green was the single best institutional call in the mapping —
  #00C896 read consumer; jewel tones read instrument. Verify sapphire stays legible
  against the midnight chrome where they meet (both are blue-family).
- **White canvas vs old grey:** for long desk sessions the old #f4f6f8 grey was slightly
  kinder; white raises luminance fatigue marginally. The soft-fill #F4F5F8 cards recover
  most of it. Not a blocker — but the durable answer for trading desks is a **dark mode**
  of the terminal content area, which the Aurora midnight palette now makes natural.
  Log it as the obvious v2; do not scope-creep it into this merge.
- **Jakarta vs a grotesk:** non-issue. At 13px/400–600 with tabular numerals it reads
  crisp and modern-institutional. One check: **negative tracking must never apply to
  tabular numerals or table cells** — tracking belongs to titles/big numbers only, or
  column alignment and scan-speed suffer. Verify in Screener/History tables.
- **Pills vs rectangles:** cosmetic; ink-filled primary buttons read fine. No objection.
- **Logo flame #E8551C per Aurora contract:** correct — brand identity is exactly where
  cross-platform byte-consistency should be absolute.

**Verdict B: APPROVE-WITH-CONDITIONS.**
**Principle:** every visual channel encodes one meaning — in a financial instrument, red
is a reserved word, and emphasis must never be spelled with it.

## 4. Question C — Merge readiness

Technical readiness is genuinely strong and I note the discipline: tsc clean, build
clean, zero banned hexes, tokens verified in the built preview, staging serving the exact
bundle, production untouched, flows byte-identical by constraint, and the diff shape
(styles + token file dominant, view files touched lightly) is consistent with the
"visual tokens only" claim. This is how a retheme should be shipped.

But B's condition is load-bearing, so C inherits it:

1. **[BLOCKING]** Split the garnet channel (one meaning per hue; error/warning off the
   emphasis color) and apply the numeric-delta rule. Re-verify the three money views.
2. **[BLOCKING]** Founder eyeballs Market Signal + Ledger + Screener on staging with
   LIVE data — the login page is illustrative; the collision risk lives where real
   red-means-loss data coexists with garnet emphasis. (The pack shows only the login
   page was publicly verifiable; the board should not certify data views it hasn't seen
   under real data — and neither should the founder merge them unseen.)
3. **[NON-BLOCKING]** Confirm tracking excluded from tabular numerals; confirm
   sapphire-on-midnight contrast at chrome boundaries; run /frontend-consistency after
   merge so the parity agent blesses the new tokens as the canonical palette (update
   `mobileTheme.ts` consumers on mobile if any web-side semantic hue changes as a result
   of condition 1 — semantic parity must survive the fix).
4. **[NON-BLOCKING]** Reconcile CLAUDE.md §3/§11 (which still specify the pre-Aurora
   palette) after merge — the pack's change makes the doc drift wider; stale design
   authority is its own integrity hazard.

**Verdict C: APPROVE-WITH-CONDITIONS** (merge after conditions 1–2; 3–4 within the week).
**Principle:** verify-before-ship applies to semantics, not just syntax — a clean build
proves the tokens compiled, not that they tell the truth.

## 5. Summary table

| Question | Verdict | Principle |
|---|---|---|
| A — Aurora-on-web direction | **APPROVE** | One instrument, one language; diverge on ergonomics, converge on identity, never on data semantics. Founder's instinct right; all five divergences on the correct axis. |
| B — Token mapping | **APPROVE-WITH-CONDITIONS** | One meaning per hue. Garnet currently serves both emphasis and error — in a finance terminal that makes emphasis read as alarm and dulls true warnings. Integrity issue, not taste. Split the channel; positive deltas never red. |
| C — Merge readiness | **APPROVE-WITH-CONDITIONS** | Technically exemplary; blocked only on the garnet split + founder review of the live-data money views. Then reconcile §3/§11 docs and re-run frontend-consistency. |

— First-Principles Guardian

---

# BOARD MEMO — The Expansionist
## Aurora Web Redesign · Global Enterprise Sale Lens · 2026-07-16

**Mandate applied:** does this design ship to institutional clients on every continent — London, Singapore, Zurich, New York, the Gulf — and does it survive enterprise diligence, locked-down client networks, and eventual white-labeling?

---

## 1. One design language across mobile/web/desktop — is it MORE sellable?

**Yes, decisively.** In enterprise diligence, visual coherence is read as *organizational* coherence. When a hedge fund's ops team sees the mobile app in the partner's hand, the terminal on the analyst's desk, and the Tauri desktop build all speaking one token system, the inference they draw is "this vendor has design governance and a real platform, not three contractors' outputs." Fragmented UI is a classic small-vendor tell; unified UI is a classic acquisition-grade tell.

The **deliberate divergences are the strongest part of the pack**, not a weakness. Keeping the dark chrome, 13px density, tabular numerals, and hover states on the terminal while mobile stays card-based shows the team understands *platform-appropriate expression of one identity* — exactly what Bloomberg (Terminal vs. mobile) and FactSet do. In a demo, "same language, institutional dialect" is a sentence a salesperson can actually say. Document these five divergences as a one-page "Aurora Institutional Dialect" note; it becomes demo collateral.

**A demo-flow point:** global sales means the SAME staging build gets shown in every timezone. Flows-unchanged is the right constraint — sales engineers don't have to relearn the demo script, and existing client screenshots/decks stay approximately valid. That is real go-to-market velocity preserved.

## 2. Plus Jakarta Sans + jewel palette — institutional or consumer fintech?

**Jewel palette: institutional. It clears the bar in all three cities.** Sapphire #2A5B9E / emerald #2E7D5B / garnet #B11226 are private-bank colors — this is the palette of Swiss annual reports and City of London asset managers, not of a neobank. Critically, the neon green #00C896 and orange accents being BANNED removes the single biggest "consumer crypto app" tell the old build had. Garnet-as-accent is fine for finance *because it is reserved for emphasis, not for negative P&L*: the one condition is a written rule that **garnet never doubles as "loss/down/red"** anywhere numbers move — a European trader reads deep red on a number as negative before reading it as brand. Keep semantic down-moves on a distinct token forever.

**Jakarta: acceptable, slightly soft, not a blocker.** A geometric-humanist face reads modern-institutional (think Revolut Business rather than UBS). A grotesk (Inter, Söhne-alikes) would read colder/more Bloomberg. But at 13px with tight tracking and dark chrome, Jakarta at weights 400–800 does NOT read consumer — the chrome and density carry the institutional read; the face is a flavoring. Where I *would* push: **stop putting Jakarta first in the `--mono` stack** (styles.css:23). Every score cell, gauge, and ledger number is styled `--mono` + `tabular-nums`, but Jakarta is loaded first, so the "mono" slot is Jakarta in practice. Verify Jakarta's tabular-figure support actually aligns your score columns; if it doesn't, misaligned numerals in a screener table is the ONE typography detail a trader will notice in the first 30 seconds of a demo. A true tabular/mono face for numerals (with Jakarta for everything else) is the more institutional pattern anyway.

## 3. Google Fonts CDN — this IS a problem, and it's my merge condition.

`index.html` loads Jakarta from `fonts.googleapis.com`/`fonts.gstatic.com` at runtime. Three independent enterprise failures:

1. **Blocked client networks.** Banks and funds routinely block third-party CDNs at the proxy. Fallback behavior is graceful but *brand-destroying in the exact rooms we sell in*: `--sans` falls to Segoe UI/system, and `--mono` falls to SF Mono/JetBrains — so on a locked-down desk the terminal silently renders in a DIFFERENT typeface than the one in the sales deck, and numerals change width. The client-side demo (their machine, their network) is precisely where this fires.
2. **EU privacy exposure.** Loading Google Fonts remotely transmits visitor IPs to Google; a German court has already held this a GDPR violation for EU sites. Zurich/London/Frankfurt security questionnaires ask about third-party subresources by name. "Zero third-party runtime calls" is a diligence checkbox we can have for one hour of work.
3. **Tauri desktop.** The desktop app wraps this same build — a native-feeling institutional app that phones Google for its typeface on every launch, and renders in fallback when offline or behind a proxy. Unacceptable for the flagship enterprise surface.

**Fix (cheap, before merge): self-host the five weights** (`@fontsource/plus-jakarta-sans` or vendored woff2 + `@font-face`), drop the two preconnects and the stylesheet link. Same visual result, zero external dependency, one diligence answer upgraded from "mitigated" to "not applicable" on all continents at once.

## 4. Does the token approach scale to desktop + white-labeling?

**Desktop: yes by construction** — Tauri wraps the identical bundle, so token parity is automatic (modulo the font fix above).

**White-labeling: 80% of the way there, and this is the biggest scale opportunity in the whole change-set.** The CSS-variable layer (`--sans/--mono/--det/--early/--ink/--canvas/...`) plus `mobileTheme.ts` is, functionally, the beginning of a theme kit. Sovereign funds, prime brokers, and data-desk resellers pay real money to put their own chrome on an instrument like this. Two gaps before that's true:
- **Stray literal hexes** outside the variable layer (e.g. styles.css:52 `#A7808C`/`#E7C9CF`, and similar) — every raw hex is a white-label leak. Sweep them into tokens.
- **Split-brain theming**: `styles.css` variables and `mobileTheme.ts` constants are two sources of truth. Generate both from ONE token file (JSON → CSS vars + TS export) and "client-branded terminal in a config file" becomes a sellable SKU, not a services project.

Neither gap blocks THIS merge; both should be a fast follow because they convert a retheme into a product capability.

## 5. Verdicts

| Question | Verdict | Reason |
|---|---|---|
| **A — Aurora-on-web direction** | **APPROVE** | One language, platform-appropriate dialects = enterprise-diligence asset; strongest global-sale story the UI has had. |
| **B — Token mapping** | **APPROVE-WITH-CONDITIONS** | Jewel palette clears London/Singapore/Zurich. Conditions: (1) garnet never means "down/loss" on numbers — write the rule; (2) fix `--mono` — verify tabular alignment or put a true tabular face first for numerals. |
| **C — Merge readiness** | **APPROVE-WITH-CONDITIONS** | **Condition: self-host Plus Jakarta Sans before merge** (blocked-CDN fallback breaks brand on client networks; GDPR exposure in EU; Tauri phones Google). ~1 hour of work, closes three diligence findings. |

**Single biggest scale opportunity:** the token layer is an accidental white-label engine — unify styles.css + mobileTheme.ts into one generated token file, purge stray hexes, self-host fonts, and NowTrendIn can ship client-branded terminals from a config file. That turns a design refresh into a revenue line.

**Single biggest blocker:** the Google Fonts runtime dependency — the only element of this redesign that can visibly FAIL inside a client's building during the sale.

— The Expansionist

---

# BOARD MEMO — The Outsider (VC / ex-hedge-fund banker)
## Aurora web-terminal redesign — design-direction review
**Date:** 2026-07-16 · **Reviewed:** evidence pack + live staging login page (https://nowtrendin-terminal-1183c0ac00c4.herokuapp.com/) · **Basis:** first look; I have not seen prior board material on this branch.

---

## 0. The buyer's chair, stated plainly

Nobody pays $250k/yr for a palette. They pay for the accuracy ledger, the lead time, and whether the instrument feels *trustworthy* under a compliance officer's stare. Design cannot win that sale; it can only lose it. So my test for every token below is a single question: **does anything here make a PM, a trader, or the fund's counsel trust the numbers less?** Measured that way, this redesign is mostly clean — with one genuine semantic hazard.

First impression of the staging login: it reads better than I expected. The split layout (white form / midnight hero with an illustrative signal card and honest "ILLUSTRATIVE" and "Measurement, not investment advice" labels) is closer to AlphaSense than to a consumer app. This is not Robinhood cosplay. Good.

---

## 1. White canvas vs dark terminal — liability or differentiator?

The reflexive answer — "trading software is dark, therefore dark" — is wrong for this product, and the founder's instinct to differentiate the institutional surface is right, but the *reason* matters:

- **Dark is the convention for execution and monitoring surfaces** — blotters, order books, market-data walls that are stared at 8+ hours (Bloomberg, most OMS/EMS). Dark chrome there is about glare across six monitors in a dim trading floor.
- **Light is the convention for research/analytics surfaces** — AlphaSense, YCharts, FactSet workstation views, Capital IQ, Morningstar Direct all default light. Buyers *read* on these; they don't stare at ticking prices.

NowTrendIn is an **analytics/signal instrument, not an execution blotter**. A light canvas is defensible and even a mild differentiator — it says "research terminal," not "Bloomberg costume." Keeping the **dark midnight chrome** (topbar/sidebar/footer) was the single smartest divergence in the mapping: the frame reads instrument, the content reads research. That hybrid is exactly how AlphaSense and Koyfin-light present.

Two caveats:

1. **The redesign went the wrong direction on glare.** Old: grey canvas #f4f6f8 with white cards. New: *pure white* canvas with grey cards. Net luminance is similar but a full-#FFFFFF field is the harshest possible choice for long sessions — the one thing desk users will actually feel by hour six. An off-white canvas (#FAFAFB–#F7F8FA family) buys back most of the comfort at zero design cost.
2. **At this price point, a dark mode will be asked for in the first three enterprise QBRs.** Not a merge blocker — but it should exist on the roadmap as a first-class theme, not a maybe. If the token work was done properly (and the diff suggests it was — one `mobileTheme.ts` mapping file), a dark theme is now cheap. That's an argument *for* this refactor, and I'd say so to buyers.

**Verdict on this axis: differentiator, not liability — provided the canvas softens off pure white and dark mode is a committed roadmap item.**

---

## 2. Garnet as the emphasis color — the one real problem

Red in a finance product is not a brand decision; it is a **reserved word**. Every buyer in your stated audience has decades of pre-attentive conditioning: red = loss, down, sell, alert, halt. You do not get to reassign it by fiat, and this mapping tries to make garnet #B11226 do **three jobs at once**:

1. Brand emphasis ("early", N, the headline accent) — per the mapping table;
2. **Error/negative** — generic red #DC2626 was remapped *to the same garnet*;
3. Adjacent to **directional market data** — this terminal shows Market Signal and crypto ledgers validated by *realized price direction*. Red WILL sit near up/down numbers.

I saw the collision live on your own login page: **"+38 EARLY SIGNAL" rendered in red.** A positive delta, your product's proudest moment — the early catch — painted in the color every trader reads as *down*. On a marketing hero it's survivable dissonance. Inside the Market Signal view, a garnet "early/emphasis" chip next to a stock that's actually up (or an error state that's actually benign) is a genuine misread — the kind a head trader mentions in the renewal call.

This is fixable without abandoning garnet, because deep garnet is a legitimately elegant, old-money color (think Bordeaux annual-report, not sell-ticket). The fix is **semantic separation, not a new palette**:

- **Split the token.** Garnet #B11226 = brand emphasis ONLY (headlines, "early" identity, the wordmark's TrendIn). Errors/negative/loss get their own hue — either restore #DC2626 for error states or, better, shift errors to a visibly distinct signal red and keep them rare.
- **Rule: garnet never touches a number that has a sign.** Deltas, price moves, ledger direction — those use the conventional up/down encoding (your emerald already covers up). A signed quantity in garnet is banned.
- The "EARLY SIGNAL" pill specifically should not be red-filled next to "+38". Ink #16264A or gold-tier treatment would carry the same emphasis without the directional lie.

Do this and garnet becomes a strength — it's distinctive, it's not another blue-terminal, and it survives the counsel test.

---

## 3. Pill buttons in institutional software

Lower stakes than the founder fears. Filter *chips* as pills are now standard in institutional research tools (AlphaSense's entire filter rail is pills). The staging login's primary CTA — full-pill, ink #16264A fill, white text — is restrained; it reads fintech-professional, not toy. Two notes:

- Keep primary CTAs' radius on the conservative side inside *data* views; full pills are fine for filters/chips, slightly consumer for destructive or transactional actions.
- The active-state convention (colored fill + white text) is clear and scannable — keep it.

Not a condition. A taste note.

## 4. Typography — Jakarta vs a grotesk

Plus Jakarta Sans is geometric and slightly friendly — a neobank face, not a Söhne/Inter grotesk. On its own I'd have picked a grotesk for this audience. But the density decisions rescue it: 13px base kept, tabular numerals kept, data tables unchanged. Those three carry the "instrument" read far more than the letterforms do. One technical condition: **no negative tracking on numerals.** Tight tracking on big numbers hurts digit disambiguation (6/8, 3/9) — keep display-tracking for words, normal tracking for figures.

## 5. What I'd also note as an investor (not a designer)

- **Process discipline is the real asset here.** Visual-tokens-only, flows byte-identical, staging-first, production untouched, banned-hex verification, one theme file. That is how a company that sells *measurement integrity* should ship a retheme. It's worth more in diligence than the palette itself.
- **Reversibility:** a 14-file, ~180-line token change with prod untouched is a one-deploy rollback. Merge risk is low; the risk is entirely semantic (garnet), not mechanical.
- The login page's honesty markers ("ILLUSTRATIVE", "Measurement, not investment advice", proprietary-data clause) are exactly what an institutional buyer's counsel wants to see on first contact. Whoever insisted on those — keep insisting.

---

## VERDICTS

**A. Overall Aurora-on-web direction — APPROVE-WITH-CONDITIONS.**
Light analytics canvas + dark instrument chrome is the right hybrid for a research terminal aimed at funds; unifying on one token system is strategically sound. Conditions: soften pure-white canvas toward off-white; commit dark mode to the roadmap as a named deliverable (the token refactor just made it cheap).
**Point-blank question to the founder:** *"When a Bloomberg-native PM runs this next to a dark six-screen wall for a ten-hour session — what do you tell him when he asks for dark mode, and what's the date on it?"*

**B. Token mapping — APPROVE-WITH-CONDITIONS.**
The mapping is disciplined except for one flaw: garnet #B11226 is simultaneously brand emphasis AND the error/negative color, in a product that displays realized price direction. Conditions (pre-merge): split the error token from the brand token; ban garnet on any signed number; recolor the red "EARLY SIGNAL"-next-to-positive-delta pattern; no negative tracking on numerals.
**Point-blank question:** *"In your terminal today, garnet means 'early', 'error', and sits next to 'price down'. A trader gets 200ms to parse it. Which one does it mean?"*

**C. Merge readiness — APPROVE-WITH-CONDITIONS.**
Mechanically ready (flows unchanged, staging verified, prod untouched, trivially reversible). Hold the merge only for the garnet/error token split — it's a small change and this is the cheapest moment it will ever be to make it. Everything else can follow post-merge.
**Point-blank question:** *"What's your rollback trigger — name the client reaction that reverts this, and confirm it's one deploy."*

---

*The Outsider — first look, no prior context. I evaluate what a buyer sees, not what the codebase intends.*

---

# BOARD MEMO — The Executioner
## Aurora web redesign (`aurora-web-redesign`, fa16b38) — executability + merge sequencing
Date: 2026-07-16 · Reviewer role: execution, sequencing, rollback, cut list

---

## 1. WHAT I INDEPENDENTLY VERIFIED (not taken from the pack)

| Claim | My check | Result |
|---|---|---|
| tsc clean | `npx tsc --noEmit` on the branch | **PASS** (exit 0) |
| build clean | `npx vite build` | **PASS** — `index-BMcoqFBf.js` / `index-Cj8a2Z9l.css` |
| staging = branch head | curl'd staging, compared asset hashes to my local build | **PASS — byte-identical hashes.** Staging serves exactly this commit's bundle. |
| zero banned hexes | independent grep sweep for the full old palette | **ONE MISS**: `#2f6fed` (old spark blue) survives at `web-terminal/src/styles.css:60` in the `.avatar` gradient — now paired with new emerald `#2E7D5B`. Half-migrated. |
| flows unchanged / tokens only | line-by-line diff of all 14 files | **True with ONE exception**: `titleCaseTopic()` is a new *runtime string transform* applied to topic names in History/MarketSignal/detail rails. Declared in the pack ("Title Case topic names") but it is code, not a token. Implementation: words containing any uppercase are left alone, otherwise first letter capitalized — so a lowercase-stored brand like `iphone` renders "Iphone". Cosmetic, but the founder should eyeball topic names. |
| mobile parity contract | grepped `frontend/DESIGN_SYSTEM.md` for every new hex | **PASS** — all 13 Aurora hexes (2A5B9E, 2E7D5B, B11226, 6B4FA0, C9A24B, A8456A, 8A8F9C, 1B3066, 0C1B3A, E8551C…) exist in the mobile Aurora contract. `mobileTheme.ts` still mirrors mobile exactly. §12 parity holds. |
| Google Fonts fail mode | read `index.html` + `tauri.conf.json` | **Fails OPEN.** `display=swap` + full system fallback stacks in both `--sans` and `--mono`; Tauri `csp: null` (no block). If fonts.googleapis.com is unreachable (offline desktop, egress-filtered hedge-fund network), the app renders in system fonts and everything works. Cosmetic degradation only. |
| regex-sweep collateral | grep of non-color lines in the full diff | **CLEAN.** Only color literals, font stacks, the font `<link>`, and `titleCaseTopic`. No logic, no filters, no handlers touched. The diff is small enough (178+/121−) that this was a targeted edit, not a blind regex sweep. |

## 2. WHAT NOBODY HAS VERIFIED (the real merge gate)

**R1 — `--mono` is no longer monospace (HIGHEST RISK, unverified).**
The branch put `"Plus Jakarta Sans"` FIRST in `--mono`. ~30 CSS classes use
`var(--mono)` for numbers (`.pct`, `.gapnum`, `.dash-row .v`, `.al-thr`, `.hist-row`,
gauge values, stat cards, footer). Only TWO (`.num`, `.score-cell`) also set
`font-variant-numeric: tabular-nums`. Every other numeric column previously got fixed-width
digits from the monospace font itself; now alignment depends entirely on whether Plus
Jakarta Sans ships tabular/uniform-width digits — **which no one has checked**. If not,
% columns shimmer on refresh and right-aligned number stacks ragged — precisely the thing
a trader notices. The pack's "kept tabular numerals" claim is currently an assumption.
- **Check:** founder stares at Market Signal % column + History rows on staging; do digits align?
- **One-line fix if not:** restore `--mono` to a true monospace stack (or add
  `font-variant-numeric:tabular-nums` to the shared numeric classes) — Jakarta stays for prose.

**R2 — 13 authenticated views walked by nobody.** Staging login is public; the app inside
is Enterprise-only. No agent has seen the authenticated surface. Founder is the only
qualified reviewer. Per-view checklist below contains this.

**R3 — persisted favorites resurrect banned hexes.** Favorite colors are stored
server-side as raw strings (`PUT /api/dashboard/`, `web-terminal/src/lib/auth.ts:166`).
Existing users' saved favorites still carry `#8B5CF6` etc. and will render post-merge.
Cosmetic; fix is a load-time old→new hex remap. NOT a merge blocker — follow-up.

**R4 — stray `#2f6fed`** (styles.css:60). Two-minute pre-merge fix → `#2A5B9E`.

## 3. FOUNDER PER-VIEW CHECKLIST (staging, before merge)

Views: Login · Dashboard · Trends/All Signals · Signal detail rail · Market Signal ·
Market detail rail · Crypto · Grade · History · Ledger · Screener · Watchlists ·
Methodology — plus the Shell chrome (topbar / sidebar / footer / search).

Per view, 5 checks (~90 seconds each):
1. **Numbers align** — any column of %s/scores: digits vertically aligned, no ragged right edge (R1).
2. **No ghost palette** — no neon green / old blue / orange anywhere (esp. avatar, saved favorites).
3. **Pill/chip contrast on white** — jewel-tint `1A` pills still legible at 13px.
4. **Hover states** — table rows, chips, buttons still respond.
5. **Topic-name casing** — no mangled brands ("Iphone", "Mcdonald's") from `titleCaseTopic`.

## 4. PRECISE MERGE-AND-VERIFY SEQUENCE

**Pre-merge (on the branch, then redeploy staging):**
1. Fix `styles.css:60` avatar `#2f6fed` → `#2A5B9E`.
2. Resolve R1: verify digit alignment on staging OR apply the one-line `--mono` fix. Rebuild, redeploy staging, confirm new hash serves.
3. Founder walks the checklist (§3) on staging. Any FAIL → fix on branch, redeploy, re-walk only the failed view.

**Merge + deploy:**
4. `git merge --no-ff aurora-web-redesign` into `main`; run `tsc --noEmit` + `vite build` on main; record the dist hashes.
5. **Note the current gh-pages HEAD SHA first** (this is the rollback pointer). Then deploy via the gh-pages worktree flow (production is GitHub Pages — NOT the Heroku mirror; deploying only Heroku makes the change invisible, per deploy topology).
6. Update the Heroku mirror (nowtrendin-terminal) to the same build so staging/mirror converge.
7. Run `/terminal-deploy-parity` — GitHub Pages live vs gh-pages branch vs Heroku mirror must show ONE bundle hash.
8. Post-deploy smoke: hard-refresh production (GitHub Pages CDN can serve stale index.html ~10 min — wait it out, don't panic-rollback on a stale cache), login, open one trend detail + one market detail, confirm fonts + numbers.
9. Run `/frontend-consistency` (§12/§17 parity agent).
10. Desktop: rebuild Tauri whenever convenient — it inherits the web build; **not a merge blocker**. Verify once that offline = clean system-font fallback.

**Rollback path (cheap — this is why the change is safe to ship):**
- Production = static bundle on gh-pages. Rollback = push the previous gh-pages commit (the SHA noted in step 5) / `git revert` the deploy commit → production restored in ~2 minutes + CDN TTL.
- No engine, API, schema, or localStorage coupling; flows unchanged means nothing to migrate back. Heroku mirror: `heroku rollback`.
- Keep the pre-merge gh-pages SHA in the merge commit message so rollback needs zero archaeology.

## 5. CUT LIST

- **CUT feature-flagging the theme.** It's a CSS token swap with a 2-minute static rollback; flag infrastructure is pure overhead. gh-pages revert IS the flag.
- **CUT self-hosting the font pre-merge.** Fails open (verified). Self-host woff2 later only if an institutional client's egress filter actually bites.
- **CUT the favorites hex migration from merge scope** (R3) — cosmetic follow-up ticket.
- **CUT waiting on the desktop rebuild** — inherits the web build on its own schedule.
- **CUT any further automated review rounds.** The remaining risk is visual-on-authenticated-screens; only the founder's eyes retire it. More agent passes are theater.

## 6. VERDICTS

| Item | Verdict | Ship steps |
|---|---|---|
| **A. Direction** (Aurora-on-terminal) | **SHIP** | Executable, cheap, fully reversible; the institutional divergences (dark chrome, 13px density, hover kept, no gold hero) are the right calls and cost nothing to keep. Design merit is other members' lane; execution risk is near-zero. |
| **B. Token mapping** | **SHIP** — after 2 mechanical fixes | (1) styles.css:60 stray `#2f6fed`; (2) settle `--mono`/tabular-digit alignment (verify or one-line fix). Mapping is otherwise verified consistent with the mobile Aurora contract, hex-for-hex. |
| **C. Merge readiness** | **SHIP-LATER** (days, not weeks) | Not mergeable TODAY: the founder walk hasn't happened and R1 is unverified. Gate = §3 checklist complete + the two fixes on staging. Then execute §4 steps 4–9. Nothing else stands between this branch and production. |

*Everything in this memo I verified against the working tree, the branch diff, a local build, and the live staging bundle — not the pack's own claims.*

---

# BOARD MEMO — The Economist
## Aurora Web Redesign: Behavioral-Economics & Market-Psychology Review
**Date:** 2026-07-16 · **Reviewer:** The Economist (advisory board) · **Subject:** branch `aurora-web-redesign`, staging build
**Canon applied:** Zweig / Belsky & Gilovich (investor psychology), Kindleberger (manias & euphoria transfer), Adam Smith (prices as information), Taleb (signal vs. noise), Malkiel & Bernstein (discipline), Reinhart & Rogoff ("this time is different" pattern-recognition)

---

## 0. Framing

A financial interface is not decoration; it is part of the price system. Smith's insight — prices carry information and coordinate behavior — applies directly: on this terminal, the Gradient Score IS the price of attention. Every color, weight, and animation applied to that number is a tax or subsidy on how the user perceives it. The behavioral question is therefore not "is Aurora beautiful?" but "does Aurora distort the price?"

The audience matters. Hedge-fund and trading-desk users are, per Zweig, *not* immune to color priming — they are arguably MORE exposed, because they make many small decisions per session under time pressure, which is exactly the regime where System-1 cues (color, size, motion) dominate System-2 reading. Institutional users forgive a plain interface; they do not forgive a manipulative one — and their counsel notices.

---

## 1. Zweig / Belsky-Gilovich — Color psychology: garnet, and the emerald collision

### 1a. Garnet (#B11226) as the accent for "early" / N / emphasis

Garnet is a red. The behavioral literature Zweig popularized is unambiguous about red in financial contexts: red primes loss-aversion, urgency, and avoidance; it measurably shortens deliberation and increases risk-averse or panicked responses (the "red numbers make investors sell" effect). Belsky-Gilovich would add anchoring: the FIRST color-coded read of a number frames every subsequent interpretation.

The design uses garnet for **emphasis and earliness** — i.e., for the product's most positive, most differentiated finding ("we saw this before the market"). That is a semantic inversion of forty years of financial-UI convention, where red = down / loss / halt. Two failure modes follow:

1. **False-alarm priming.** A desk user scanning quickly reads a garnet-highlighted topic as *deteriorating* or *risk-flagged*, not as *early*. The product's best signal arrives pre-wrapped in the psychology of a warning. That is a herding trigger in the wrong direction: it nudges users to treat early detections as threats to react to, not measurements to consider — exactly the urgency-mediated behavior the "measurement, not advice" doctrine forbids the platform from inducing.
2. **Dilution of true warnings.** If garnet also serves genuine negative semantics anywhere (it replaced generic red #DC2626 per the token table), then the same hue means both "our proudest early call" and "error/danger." Crying wolf in a single channel. Taleb: when one channel carries both signal and alarm, the user rationally discounts both.

**However** — and this is the saving nuance — garnet #B11226 is a *dark, desaturated, jewel* red, not alert-red. At small accent sizes (an N chip, an "early" tag) it reads closer to a Bloomberg-terminal burgundy than to a stop sign. The bias risk is real but scale-dependent: acceptable for thin accents, unacceptable if garnet is ever used for large numbers, backgrounds, directional deltas, or anything a user could mistake for a P&L read.

### 1b. The emerald collision

Emerald #2E7D5B is assigned to **Confidence** (a component of the measurement). Emerald is also, universally on trading desks, the color of **up / gain**. If the terminal ever shows price or score *direction* (the market/crypto rails show realized price direction; the ledger shows wins/losses), the user's learned mapping "green = it went up" will contaminate "green = we are confident." A high-Confidence topic reads as a *rising* topic; a topic whose Confidence chip sits next to a falling price reads as dissonant. This is precisely the Belsky-Gilovich "mental accounting by color" trap: two different accounts (confidence in measurement vs. direction of outcome) forced into one color ledger.

Verdict on 1: the palette is defensible ONLY under strict channel separation — see Prescriptions P1–P3.

---

## 2. Kindleberger — Euphoria transfer from form to content

Kindleberger's anatomy of manias begins with displacement and is amplified by *credibility props*: the beautiful prospectus, the marble bank lobby, the confident chart. Form lends unearned credence to content. A markedly more beautiful terminal WILL raise perceived signal quality without one basis point of accuracy improvement — this is not hypothetical; it is the entire history of financial marketing.

Three observations temper the concern here:

1. **The direction of the aesthetic matters.** Aurora-on-web went *toward* restraint: white canvas, hairlines, desaturated jewel tones, dark instrument chrome, tabular numerals, 13px density retained. This is the aesthetic of an instrument, not a pitch deck. Kindleberger's props are gold-leafed and euphoric; this mapping deliberately confined gold to tier/warning identity and added **no hero card** on the web. That is the correct institutional instinct: density and neutrality signal "measure," ornament signals "believe."
2. **The counterweight exists in-product.** The accuracy ledger — with its honest blended-10% / tracked-race-26.9% split, pre-broken chips, and the founder's verbatim disclaimer top AND bottom — is a structural anti-euphoria device. A beautiful interface that *prominently displays its own miss rate* is the opposite of a mania prop. Condition: the redesign must not visually demote the ledger or the disclaimer (they must not become elegant grey whispers while scores become jewel-toned declarations).
3. **The residual risk is the login/lobby.** The public-facing surface (login page, marketing edges) is where euphoria transfer is cheapest and most tempting. Keep it as dry as the terminal inside.

Reinhart-Rogoff footnote: the greatest interface danger is any visual grammar implying "this instrument is different — it doesn't miss." The pre-broken / near-miss chips shipped on 07-07 are the right vaccination. Keep them visible in Aurora.

---

## 3. Smith — Are the prices presented neutrally or theatrically?

The test: does the SAME number render with the same visual weight regardless of whether it flatters the platform? Neutral presentation requirements, checked against the mapping:

- **Uniform rendering of scores.** Detection sapphire, Confidence emerald, stage from `stageOf` — the mapping is *categorical* (which metric) not *evaluative* (good/bad score). Good. A score of 35 and a score of 95 should differ only in the number and the stage pill derived from the disclosed stage function — never in saturation, glow, size, or motion. From the token table, nothing suggests score-magnitude-driven theatrics were added. PASS, conditionally.
- **Stage pills as {color}1A tints** — 10%-alpha tints are the typographically quiet way to encode category; this is the neutral choice. PASS.
- **The dark chrome** — midnight topbar/sidebar is identity, not information; it frames rather than colors the prices. Kindleberger-safe, Smith-neutral. PASS, and the institutional-divergence call (keep the chrome; mobile has none) is right: traders read dark chrome as *instrument housing*.
- **One reservation:** "garnet as emphasis" is by definition theatrical — emphasis is an editorial act on a price. Every use of the emphasis accent should be traceable to a *disclosed, mechanical rule* (e.g., "garnet tags N when N ≥ threshold X, always"), never to discretionary highlighting of flattering rows. If the rule is mechanical and documented in Methodology, emphasis is metadata; if it is discretionary, it is a thumb on the scale.

---

## 4. The discipline question — "measurement, not advice," visually

Malkiel/Bernstein discipline is about removing the interface's ability to whisper "do something." Checks:

- **No prescriptive color-coding of action** — the mapping contains no buy/sell/act semantics; stage labels (Breakout/Strong/Emerging/Watching/Monitoring) are descriptive of the *measurement's* state. PASS — but note stage names like "Breakout" already sit at the edge of prescription; the jewel-tint restraint helps keep them descriptive. Do not let any future token give "Breakout" a hotter treatment than its siblings beyond the existing tint scheme.
- **Tier labels neutral** — gold confined to tier/warning identity, consumer/business/enterprise unrevised. PASS.
- **The disclaimer** — founder-approved verbatim text must survive restyling at full legibility (not muted below body contrast). CONDITION.
- **Red/green directional truth** — where realized price direction IS shown (market/crypto ledgers), up/down colors must be visually distinguishable from Confidence-emerald and garnet-accent, or direction and judgment blur. CONDITION (same as P1).

---

## 5. Verdicts

**(A) Direction — Aurora-on-web for the institutional audience: APPROVE.**
Framework: Kindleberger + Smith. The mapping moves toward instrument-grade restraint (white canvas, density kept, hairlines, no hero, dark chrome as housing). Form does not overwhelm content; the aesthetic direction *reduces* euphoria-transfer risk relative to a flashier alternative, and the deliberate divergences from mobile (chrome, density, hover, no gold hero) are exactly the institutional adaptations the founder's lens asked for. White canvas vs. old grey: behaviorally neutral for judgment; for 8-hour desk sessions it is a mild ergonomic (glare) question, not a psychology question — offer a dim/desk mode eventually, not a blocker.

**(B) Token mapping: APPROVE-WITH-CONDITIONS.**
Framework: Zweig/Belsky-Gilovich channel separation. Two collisions must be governed before this palette hardens into habit: (i) garnet = both emphasis/early AND the error/danger red family — red-as-praise inverts desk convention and primes alarm on the product's best output; (ii) emerald = Confidence while emerald-family green will inevitably also mean "up" wherever direction appears. Conditions are P1–P4 below — all are usage *rules*, not re-pigmentation; the hexes themselves can stand.

**(C) Merge readiness: APPROVE-WITH-CONDITIONS.**
Framework: discipline + verification. tsc/build clean, zero banned hexes, staging serving the bundle, flows byte-identical — mechanically ready. Gate the merge on: P1 (directional-color separation audit on the market/crypto/ledger rails), P2 (garnet scale rule), P5 (disclaimer + ledger prominence unchanged), each a visual spot-check, not a rebuild. Nothing here requires REJECT; nothing here should be deferred past merge either, because color-meaning habits form in the first weeks of use and are expensive to reverse (anchoring works on palettes too).

---

## PRESCRIPTIONS

**P1 — Separate the directional channel (Zweig).** Reserve a distinct up/down pair for realized price direction (e.g., a brighter market-green and a brighter alert-red, or ▲/▼ glyphs + sign as the primary carrier with color secondary). Neither Confidence-emerald #2E7D5B nor garnet #B11226 may ever encode direction. One-line rule for `mobileTheme.ts`: *meaning-colors (metric identity) and outcome-colors (direction) never share a hue family on the same view.*

**P2 — Garnet scale rule (loss-aversion containment).** Garnet is permitted only at accent scale: chips, tags, thin underlines, the N monogram. Never as a panel background, a large numeral, a delta, or a row highlight. Codify in the token file as a comment; enforce via frontend-consistency agent.

**P3 — Mechanical emphasis (Smith).** Every garnet "emphasis" application must map to a disclosed rule (threshold or state), documented in Methodology. No discretionary highlighting of favorable rows — emphasis is metadata about the measurement, not editorial about the result.

**P4 — Redundant encoding (Belsky-Gilovich accessibility + de-priming).** Wherever color carries meaning (stage pills, verdict chips, direction), pair it with a text/glyph carrier so the meaning survives color-blindness AND so color is demoted from sole carrier to reinforcement — this alone halves the priming budget of the palette.

**P5 — Anti-euphoria anchors (Kindleberger).** The accuracy ledger entry point, the miss/pre-broken chips, and the verbatim disclaimer keep their current prominence and contrast in Aurora — audit the staging build specifically for any restyling that visually subordinates them. A terminal this handsome must wear its miss rate on its sleeve.

**P6 — Login lobby stays dry.** No euphoric flourish on the public surface; the marble-lobby effect is strongest where the least information lives.

**P7 (non-blocking) — Desk-session dim mode.** White canvas is fine for judgment; for trader ergonomics across long sessions, schedule a dimmed canvas variant. Ergonomics, not psychology; post-merge backlog.

— The Economist

---

**Chairman — your decision: merge / adjust / reject, plus the open items (font self-hosting · casing dictionary · off-white canvas · dark-mode roadmap).**
