# BOARD REVIEW — Aurora Rev 3: the Founder Hybrid (recommendations)
**Date:** 2026-07-17 · **Material:** branch `aurora-web-redesign` rev 3.1, staged on
nowtrendin-terminal · **Chairman ruling under review (SETTLED):** Aurora structure/
typography/chrome + the ORIGINAL vivid data palette (rev 2 was "too monotone").
Five of six memos verified the LIVE staging build (hash-matched; DOM-inspected).

## DECISION TABLE

| Item | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist |
|---|---|---|---|---|---|---|
| A — hybrid coherence | AWC | AWC | APPROVE | AWC | SHIP (after 3 fixes) | APPROVE |
| B — two-dialects policy | AWC | AWC | AWC | APPROVE | SHIP (docs) | AWC |
| C — merge readiness | REJECT as-is (flips on ~1-day fixes) | AWC | AWC | AWC (merge yes, demo after P0) | SHIP-LATER by hours | AWC |

**The board likes the hybrid.** Multiple memos: it reads as the institutional instrument
(AlphaSense/YCharts band); the founder's ruling RESTORED one-meaning-per-hue by
construction (orange emphasis ≠ red loss); green-Confidence passes the Economist's
valence test (confirmation aligns with green=good). "One brand, two dialects" is
Bloomberg-precedented and sellable once documented.

## FIXED DURING THE REVIEW (already on the branch, rev 3.1 staged)
- Ledger view had NO disclaimer (Economist; the founder's verbatim copy is mandatory on
  every panel — the one counsel reads first). Added top + bottom.
- Executioner's 3 ghosts: `.g-lev` back to #10B981, `.lg-stg.aligned` back to #7aa6f5,
  stale jewel comments reconciled to the hybrid.

## CONVERGENT CONDITIONS FOR THE CHAIRMAN

### 1. Contrast on the vivid data TEXT (Challenger, measured live) — NEEDS YOUR RULING
The original palette's bright hues, used AS TEXT on white, fail WCAG AA: Confidence
#00C896 text = 2.16:1 (the Det/Conf columns and the ledger's LED pill at 1.90:1 — the
moat's own scoreboard); three stage pills sit a hair under 4.5:1 (4.36–4.46). This is
TRUE OF PRODUCTION TODAY — it is the look you chose, not a regression. Options:
  (a) keep the exact production look (founder aesthetic; accept the AA misses),
  (b) "text-twins": keep the vivid hues for fills/rings/dots/charts, use slightly
      deeper twins ONLY where the color is text (the board's recommended pattern),
  (c) bump score columns to large-bold type (relaxes the threshold; green still shy).
### 2. Self-host Plus Jakarta Sans — 4 memos PRE-merge (bank proxies render system
   fonts in client demos; EU GDPR finding; Tauri pings Google) vs Executioner
   post-merge (fails open). ~1 hour. NEEDS YOUR RULING.
### 3. Documentation trio WITH the merge (Guardian/Expansionist/Economist/Executioner —
   effectively unanimous): rewrite CLAUDE.md §12 to SEMANTIC parity ("hue meanings are
   contractual cross-platform; hue values are per-surface — never restore jewel tones
   to web data colors, never copy vivid hexes into mobile"); fix mobileTheme.ts's
   "mirrored" header; re-point /frontend-consistency at semantic-not-hex parity (else
   the watchdog files your ruling as a bug every run). Plus ship WEB_DESIGN_SYSTEM.md
   (Expansionist outline in memo).
### 4. Outsider P0 polish (pre-DEMO, not necessarily pre-merge; mostly pre-existing):
   raw `Current_events` key visible in category cells · engine-room string leaking in
   the rail ("backfill(lifecycle-rule)… fallback 0.45") · dead "Generating a
   source-aware definition…" spinner when AI absent (§17 spirit: hide, don't show
   empty) · Ledger/Market explainer strips render as sentence fragments.
### 5. Post-merge queue: casing dictionary (Asi/Agi→ASI/AGI etc.) · warm-band chart
   separation (orange/amber/gold 1.18:1 in graphics) · token-file unification (the
   white-label engine) · off-white canvas A/B · dark mode roadmap · favorites hexes.

## MERGE SEQUENCE (Executioner, adopted)
Chairman rulings on 1+2 → land them → staging re-verify → founder walk → merge --no-ff
→ build main → record gh-pages SHA (rollback) → deploy gh-pages → sync Heroku mirror →
/terminal-deploy-parity → /frontend-consistency (AFTER its charter re-point).

## ARCHETYPE MEMOS (verbatim)

---

# BOARD MEMO — The Challenger — Aurora rev 3 HYBRID re-review
**Date:** 2026-07-16 · **Scope:** execution of the founder's settled hybrid ruling (not the choice)
**Evidence:** live staging bundle `index-Bvy1fa8w.css` / `index-DWXthJKM.js` (verified byte-identical to
`web-deploy-terminal/dist/assets/` — every hex below is read from the shipped CSS, every ratio computed
with the WCAG 2.x relative-luminance formula, not eyeballed).

---

## 0. What I verified (measured, not asserted)

| # | Element (size/weight) | FG on BG | Ratio | WCAG bar | Verdict |
|---|---|---|---|---|---|
| 1 | **Confidence score column** `.score-cell.conf` (14px/800) | #00C896 on #FFFFFF | **2.16** | 4.5 | **FAIL** |
| 2 | **Ledger LED verdict pill** `.verdict.LED` | #00C896 on #e0f5ec | **1.90** | 4.5 | **FAIL (worst on page)** |
| 3 | Detection score column `.score-cell.det` (14px/800) | #2D7EEF on #FFFFFF | **3.93** | 4.5 | **FAIL** |
| 4 | Calibration chip `.cal-chip` (9px/700) | #df7a36 on #fbecdc | **2.60** | 4.5 | **FAIL** |
| 5 | Alert-create primary CTA `.al-create` (14px/600), `.lg-btn.ok`, `.al-chip.on` | #FFF on #00C896 | **2.16** | 4.5 | **FAIL** |
| 6 | Fav save btn (10px/800), bell dot (9px), `.chip.early.active` (12px/700) | #FFF on #df7a36 | **3.01** | 4.5 | **FAIL** |
| 7 | Stage pill EMERGING (10px/800) | #8a6d0f on #fbf1d6 | **4.36** | 4.5 | **FAIL (hairline)** |
| 8 | Stage pill MONITORING | #6b7280 on #f1f4f7 | **4.38** | 4.5 | **FAIL (hairline)** |
| 9 | Stage pill WATCHING/MARGINAL | #c0431a on #fcebe0 | **4.46** | 4.5 | **FAIL (hairline)** |
| 10 | Stage pill BREAKOUT / STRONG | #007a5a·4.69 / #1b5fc4·5.30 | — | 4.5 | PASS |
| 11 | **Wordmark "TrendIn"** orange on topbar | #df7a36 on #0C1B3A | **5.65** | 4.5 | **PASS** |
| 12 | Nav active icon orange on #233B72 | — | **3.60** | 3.0 (icon) | PASS |
| 13 | Footer/asof LIVE green on ink | #00C896 on #0C1B3A | **7.87** | 4.5 | PASS |
| 14 | Cal-banner body text | #8a4a1c on #fbecdc | **5.89** | 4.5 | PASS |
| 15 | Gold chart hue (EMERGING dots) | #D4A017 on #FFF | **2.38** | 3.0 (graphic) | **FAIL** |
| 16 | Amber #E85A1E vs orange #df7a36 (hue separation) | — | **1.18** | — | indistinguishable |
| 17 | Muted `--text-3` | #9A9AA2 on #FFF | 2.79 | 4.5 | FAIL (Aurora-inherited, pre-existing) |

Note on the "14px bold is large text" dodge: WCAG large-text is ≥18.66px bold. The score columns are
14px. No exemption applies.

---

## A. HYBRID COHERENCE — **APPROVE-WITH-CONDITIONS**

**Concessions first (I attack what's broken, not what works).** The two combinations I was most
suspicious of are CLEAN: orange #df7a36 on midnight chrome measures **5.65:1** on the wordmark and
**3.60:1** on the active nav icon — both pass. Midnight chrome + vivid orange accent is contrast-sound.
The one-meaning-per-hue restore is real at the token level: red #DC2626 is down/error only, the garnet
collision is gone by construction. And the ELEVATED/WATCH maroon pills (5.77) and cal-banner (5.89) pass.

**Strongest attack — the flagship number is the least legible thing on the page.** Bright #00C896
Confidence as TEXT on white is **2.16:1** — less than half the floor — on exactly the elements a hedge-fund
buyer stares at: the Confidence score column (row after row of 14px numerals), the statcard "good" values,
the gauges, `al-fired`. Worse: the **LED verdict pill — the accuracy ledger's WIN marker, the moat's own
scoreboard — is 1.90:1**, green-on-green-tint, the single lowest ratio I measured. You are rendering the
company's proudest number in the site's most invisible ink, for an audience (traders on bright floors,
bankers on projectors, compliance reviewers running automated WCAG scans in vendor due-diligence) that
will notice. Same hue as a fat chart ring or a 22px hero number is fine (graphics/large); as 10–14px text
it is not. Detection blue at 3.93 fails the same test by a smaller margin.

**Second attack — the restore DID quietly undo part of the pill fix, exactly as I warned.** With the
rev-2 jewel override block removed, `.stage.*` resolves to the ORIGINAL tokens. Two of five survive
(BREAKOUT 4.69, STRONG 5.30) — but **EMERGING 4.36, MONITORING 4.38, and WATCHING/MARGINAL 4.46 all sit
just UNDER 4.5:1** at 10px/800. These are hairline misses, which is precisely why nobody caught them by
eye. The fix is three darkened text tokens, not a redesign — but "we restored the originals" silently
shipped three sub-threshold pills.

**Third attack — the warm band breaks one-meaning-per-hue where it matters: in the data.** The token
sheet is disciplined; the CHARTS are not. Three warm hues carry three different meanings within 1.2–2.4:1
of each other: orange #df7a36 (emphasis/gap/calibration), amber #E85A1E (WATCHING + MARGINAL chart dots),
gold #D4A017 (EMERGING chart dots, MODERATE/BUILDING tier, RESURGENT maturity). Orange-vs-amber mutual
contrast is **1.18:1** — on a scatter or sparkline they are the same color. Gold-on-white at 2.38 fails
even the 3:1 graphics floor, so EMERGING dots are both faint AND ambiguous. Meanwhile "N" has a
**fractured identity**: the pack says N = orange #df7a36; the shipped Methodology tag is brandOrange
#EE6A2A; the N-card is MAROON #b11226 (`.n-val`, borders, `.ntg-tag`); the N table cell I could find has
no color variant at all. Two oranges and a maroon all claim the proprietary metric. Pick ONE hue for N
and write it down. (Minor: `.tier.ACTIVE` renders pink #a8456a text on orange-soft while its chart hue is
amber #E85A1E — same tier, two hues.)

**Conditions (all are token edits, ~an afternoon):**
1. Introduce dark text twins: `--conf-text` ≈ #008A68→#007a5a-class (≥4.5 on white AND on #e0f5ec) for
   score cells / LED / statcards / al-fired; `--det-text` ≈ #1b5fc4 for `.score-cell.det`. Keep the
   bright #00C896/#2D7EEF for rings, fills, dots, chrome-on-ink (7.87 ✓) — vivid survives, text becomes legible.
2. Darken the three failing pill tokens a step (em-t, wa-t, mo-t) to clear 4.5.
3. `.cal-chip` text → the banner's #8a4a1c (proven 5.89); 9px warning text at 2.60 is a non-warning.
4. White-on-green CTAs and white-on-orange micro-controls: darken the fill (e.g. green CTA → #009970-class)
   or flip to ink-on-tint. A 2.16:1 primary button fails any enterprise accessibility review.
5. Chart discipline rule: #df7a36 is CHROME/EMPHASIS only, never a categorical series hue; gold/amber keep
   stage meanings and get a darker stroke or shape/label redundancy (gold dots currently fail 3:1).
6. Unify N's hue (one of #EE6A2A / #df7a36 / #b11226 — I don't care which; the founder does) everywhere.

**Mind-changer:** show me a WCAG audit convention under which 14px/800 numerals qualify as large text, or
bump the score columns to ≥19px bold — then #00C896-as-text passes at 3:1 and condition 1 shrinks to the
LED pill and small labels. Nothing else on this list has an escape hatch.

## B. CROSS-PLATFORM DIVERGENCE POLICY — **APPROVE-WITH-CONDITIONS**

**Verdict rationale:** "web = vivid instrument, mobile = jewel calm" is genuinely sellable to this
audience — Bloomberg's terminal and its mobile app share identity, not pixels; institutional buyers read
a denser, hotter desktop surface as SERIOUSNESS, not inconsistency. One brand, two dialects is defensible.

**Strongest attack:** undocumented divergence is a drift generator, and this project has the scar to prove
it — rev 2's garnet collision was exactly an unwritten recolor propagating unchecked. Today CLAUDE.md §12
still says the mobile color scheme is "mirrored for the web detail rails in mobileTheme.ts" — that sentence
is now FALSE on staging, which means the Frontend Consistency agent is enforcing a dead contract: it will
either false-alarm on every deliberate vivid/jewel difference or be loosened into enforcing nothing. A
policy that exists only in a board memo is not a policy.

**Conditions:** (1) rewrite §12 before merge: parity = SEMANTICS (same sections, data points, meaning
slots, one-meaning-per-hue within each platform); palette = two documented dialects keyed by the SAME
semantic token names (detection/confidence/emphasis/up/down/stage.*) in ONE checked-in mapping file
(mobileTheme.ts becomes the mobile column of that map, not "the mirror"). (2) Re-point
/frontend-consistency at token-slot parity, not hex parity. (3) The invariants that stay IDENTICAL across
dialects, in writing: red=down/error only, one hue per meaning per platform, §17 source-display rule.

**Mind-changer:** nothing changes my verdict to REJECT unless the founder wants per-page or per-feature
palette exceptions — two dialects is a brand; three is entropy. To reach clean APPROVE, just show me the
committed token map + updated §12.

## C. MERGE READINESS — **REJECT as-is** (fast path to approve: ~1 day)

**Strongest attack:** rev 3 ships the company's flagship metrics — Confidence and the accuracy-ledger LED
verdict — at 2.16:1 and 1.90:1, plus a 2.16:1 primary CTA and three sub-threshold stage pills, onto a
surface whose stated audience runs vendor accessibility scans as due-diligence. Merging that isn't shipping
the founder's vision; it's shipping the founder's vision with its headline numbers dimmed to near-invisible.
Every blocker is a CSS token edit; there is no schedule argument for merging before them.

**Pre-merge blockers:** A-conditions 1–4 (conf/det text twins, three pill tokens, cal-chip, CTA fills) +
B-condition 1 (§12 rewrite — merging code that falsifies the master doc violates the project's own
verify-before-ship rule). Then flip to APPROVE.

**Post-merge, prioritized:** (1) font self-hosting — Plus Jakarta via third-party CDN is a latency AND a
fingerprinting/procurement flag for institutional clients; (2) N-hue unification + chart warm-band
discipline (A-5/6); (3) muted `--text-3` #9A9AA2 (2.79) — Aurora-inherited, fix in the token map so both
dialects inherit; (4) dark mode — decide BEFORE more vivid-on-white tuning, because every text-twin token
chosen now needs a dark-canvas value; (5) casing dictionary; (6) off-white canvas experiment (re-measure
all ratios above against the new canvas — several hairline passes will flip); (7) favorites hexes
(`#a8456a`, `#b11226`-soft glows) folded into named tokens so the next recolor can't orphan them.

**Mind-changer:** a screenshot-level pass is NOT one — the failures are measured, not aesthetic. What
flips C to APPROVE is the six-token patch + §12 text, nothing more. I am deliberately NOT asking for dark
mode, self-hosted fonts, or the casing dictionary as blockers; the direction is ruled and the fast path is
real.

---
*The Challenger — I measured everything I attacked; ratios reproducible via WCAG relative luminance
against the shipped `index-Bvy1fa8w.css`.*

---

# BOARD MEMO — First-Principles Guardian
## Aurora rev 3 hybrid re-review ("one brand, two dialects") — 2026-07-16
### Ruling acknowledged as SETTLED. This memo assesses coherence, divergence policy, and merge readiness only.

---

## 0. The first principle at stake

**A product's identity lives in its semantics and structure, not in its saturation.**
What makes NowTrendIn *NowTrendIn* is: the Gradient Score's two-axis grammar (Detection =
earliness, Confidence = confirmation), the measurement-not-advice posture, the ledger as
the moat, Aurora's structural chrome (midnight frame, white canvas, Jakarta, pills, Title
Case). Saturation — jewel vs vivid — is *register*: the voice you use for the room you're
in. A trading floor and a phone in a pocket are different rooms. Two dialects of one
semantic contract is honest branding **if and only if the hue→meaning mapping is identical
on both platforms even when the rendered hex values differ.** I verified this is the case
(§2 below). So yes — the hybrid keeps the identity honest. What would make it dishonest is
the *documentation* still claiming literal parity, which it currently does. That is the
real risk, and it is fixable in two sentences (§3).

---

## 1. Hybrid coherence — verified against the actual code

I read the restored `web-terminal/src/lib/mobileTheme.ts`. Findings:

**Confirmed restored, one-meaning-per-hue at the FAMILY level:**
- Blue #2D7EEF = Detection/earliness family (Detection score, STRONG stage, NEW maturity, ROUTINE tier, detection-feed). Coherent: "early/speed."
- Green #00C896 = confirmation/positive family (Confidence, BREAKOUT, EMERGING maturity, up-moves, AT_BASELINE, aligned gap band). Coherent as a family: "confirmed/healthy."
- Red family: **two reds with distinct jobs** — #CF2A1B = severity/intensity (VIRAL stage, ELEVATED market tier, SPIKE_VS_SELF, very-early gap band) vs #DC2626 = realized DOWN / error. These are different meanings deliberately carried on different hexes. Correct — but it only stays correct if documented; to a future session they look like an accidental near-duplicate to "consolidate."
- Orange family: **three oranges** — #DF7A36 = emphasis/N/instrument accent; #EE6A2A = brand "Now"; #E85A1E = WATCHING/MARGINAL/elevated-vs-baseline. Distinct jobs, close hues. Same documentation requirement.
- Gold #D4A017 = caution/emerging-value (EMERGING stage shown as INDICATING, MODERATE/BUILDING tier, RESURGENT, warning, Enterprise). The pack's worry (orange emphasis vs gold Enterprise) is a non-collision in practice: gold is always a *state* chip, orange is always an *attention* accent; they never compete for the same slot.
- The rev-2 garnet collision (orange emphasis ≈ red loss) is gone by construction — confirmed: emphasis is #DF7A36, loss is #DC2626, visually and semantically far apart.

**Contrast check (computed):** #DF7A36 on midnight #0C1B3A ≈ **5.7:1** — passes WCAG AA for normal text. Orange-on-chrome is safe as shipped.

**The one genuine residual watch-item:** Confidence and up-moves share the exact hex
#00C896. A Confidence ring beside a red down-move row can read as the instrument
contradicting itself ("green score, red outcome"). This is acceptable *family semantics*
(green = confirmation, whether of a score or a price direction) — but it is the seam a
hostile hedge-fund reviewer will poke. Mitigation is layout + labels, not palette surgery:
never render the Confidence hue and the outcome hue as adjacent unlabeled dots/chips in
the same visual block. Condition, not blocker.

**Verdict A — hybrid coherence: APPROVE-WITH-CONDITIONS.**
Principle at stake: *one meaning per hue is a contract about semantics, and a contract
that lives only in hex values will be broken by the next well-meaning refactor; it must
live in written words.* Conditions: (i) commit the hue-family map above into the design
docs; (ii) the Confidence/up-move adjacency rule; (iii) the two-reds/three-oranges roster
documented so nobody "deduplicates" them.

---

## 2. Cross-platform divergence — is "one brand, two dialects" defensible?

Yes, and it is the *stronger* position, provided the contract is stated correctly:

- **Parity of MEANING, structure, sections, and data points — divergence of RENDERING.**
  Both platforms say "blue means detected early, green means confirmed, red means down,
  gold means caution, grey means dormant, orange means look-here." Mobile says it in
  jewel tones; web says it in instrument tones. That is Bloomberg-vs-Bloomberg-app, not
  brand drift. Sellable to hedge funds (they *expect* a terminal to look like an
  instrument) and to mobile users (Aurora calm is the mobile promise).
- **What would NOT be defensible:** a hue meaning one thing on web and another on mobile
  (e.g., orange = emphasis on web but orange = warning on mobile). That line must be the
  documented invariant, and the Frontend Consistency agent must enforce *that* line —
  not literal hex equality.

**Three documentation defects that WILL cause a future session to "fix" the web back:**

1. **CLAUDE.md §12** still says: *"Mobile color scheme mirrored for the web detail rails
   in `web-terminal/src/lib/mobileTheme.ts`."* This is now false and is the single most
   dangerous sentence in the repo for this ruling — it is a standing instruction to undo
   the founder's decision. **Exact replacement sentence (proposed):**

   > "Color parity across platforms is SEMANTIC, not literal (founder ruling 2026-07-16,
   > settled): both surfaces share one hue-meaning contract — Detection=blue #2D7EEF,
   > Confidence=green #00C896, realized down/error=red #DC2626, severity=red #CF2A1B,
   > caution/emerging=gold #D4A017, emphasis/N=orange #DF7A36, dormant=grey — but render
   > it in two deliberate dialects: web/desktop = the vivid instrument palette (canonical
   > in `web-terminal/src/lib/mobileTheme.ts`, which is the WEB data-color authority, not
   > a mobile mirror), mobile = the Aurora jewel palette (canonical in
   > `frontend/DESIGN_SYSTEM.md`, where the vivid hexes are BANNED). Never restore the
   > web to jewel tones and never copy vivid hexes into mobile UI — the Frontend
   > Consistency agent enforces parity of sections, labels, data points, and hue MEANING
   > only, never hex equality."

2. **The file header of `mobileTheme.ts` itself** (lines 1–3) says "Mobile-app color
   scheme, mirrored for the web… so the two surfaces read identically." A future session
   reading the file will re-learn the dead rule from the code even after CLAUDE.md is
   fixed. Rewrite the header to declare it the web instrument palette bound to the shared
   hue-meaning contract; ideally rename the file (`signalPalette.ts`) — the *name*
   "mobileTheme" is itself an instruction to mirror. If renaming is churn, the header fix
   is the non-negotiable minimum.

3. **The Frontend Consistency agent charter** (`/frontend-consistency`) checks "the
   mobile color scheme" as a parity criterion. Unamended, the parity watchdog itself will
   file the founder's ruling as a bug every run — institutionalized regression pressure.
   Amend its charter to check hue-meaning parity + the two-dialect boundary (vivid hexes
   absent from mobile, jewel-only rule intact on mobile, `mobileTheme.ts` values intact
   on web).

**Verdict B — divergence policy: APPROVE-WITH-CONDITIONS.**
Principle at stake: *undocumented exceptions decay back to the rule; a settled ruling that
contradicts the written spec loses to the spec the moment the founder isn't in the room.*
Conditions: the §12 rewrite (verbatim above or founder-edited), the `mobileTheme.ts`
header/name fix, and the consistency-agent charter amendment — all BEFORE merge, because
they are the merge's immune system.

---

## 3. Rev-2 wins — preserved?

| Rev-2 win | Status in rev 3 | Evidence |
|---|---|---|
| One meaning per hue | **Preserved (family-level), garnet collision gone** | Code-verified §1; caveats: green double-duty (Confidence/up), two reds, three oranges — all coherent, all must be documented |
| Measurement-not-advice neutrality | **Preserved, one guardrail** | Red/green pair marks *realized* outcomes (ledger facts) and severity states, never a recommendation; bright-green Confidence must never be captioned or positioned to read as "go" — keep the Speed/Precision role copy exactly as is |
| Ledger + disclaimer prominence | **Preserved** | Flows byte-identical per the pack; disclaimer is founder-verbatim top AND bottom. Add one rule: the disclaimer renders in neutral ink ONLY, never in any palette color — on a vivid page, neutral text is what the eye treats as load-bearing, and coloring it would demote it to chrome |

---

## 4. Merge readiness + prioritized recommendations

**Verdict C — merge readiness: APPROVE-WITH-CONDITIONS.**
The build is coherent, contrast-safe, and the wins survived. What is NOT ready is the
paper: merging rev 3 while §12, the file header, and the parity agent still assert literal
mirroring ships a codebase at war with its own documentation.

**PRE-MERGE (blocking, all cheap):**
1. CLAUDE.md §12 replacement sentence (§2 above).
2. `mobileTheme.ts` header rewrite (+ rename to `signalPalette.ts` if churn is acceptable).
3. Frontend Consistency agent charter: hue-meaning parity, not hex parity; add the
   two-dialect boundary checks.
4. **Font self-hosting** — pre-merge, not cosmetic: hedge-fund/bank clients sit behind
   firewalls and proxy policies that routinely block Google Fonts; a blocked CDN font
   silently degrades the entire Aurora identity to a system fallback for exactly the
   audience the terminal exists for, and third-party font calls are a data-governance
   question those clients' counsel will ask. Self-host Jakarta (incl. the monospace
   numerals) in the bundle.

**POST-MERGE (ordered):**
5. Casing dictionary for `titleCaseTopic` (small-words list: of/the/de/vs; proper-noun
   overrides) — current heuristic is good, edge cases are display-only polish.
6. Confidence/up-move adjacency rule applied as a layout audit pass (§1 watch-item).
7. Dark mode — do it as a third *rendering* of the SAME hue-meaning contract, which the
   new §12 language already accommodates; never as a new palette with new meanings.
8. Off-white canvas — pure founder taste; test against the WCAG thead shade before adopting.
9. Favorites hexes — minor; slot them into an existing family (orange=emphasis or gold),
   do not mint a new hue meaning for a convenience feature.

---

## 5. Summary of verdicts

| Question | Verdict | Principle |
|---|---|---|
| A — Hybrid coherence | **APPROVE-WITH-CONDITIONS** | Identity lives in semantics + structure; saturation is register. The contract must live in words, not hexes. |
| B — Divergence policy | **APPROVE-WITH-CONDITIONS** | Undocumented exceptions decay back to the rule — fix §12, the file header, and the parity agent's charter or the system will "correct" the founder. |
| C — Merge readiness | **APPROVE-WITH-CONDITIONS** | Never merge code at war with its own documentation; the three doc fixes + self-hosted fonts are the merge's immune system. |

— First-Principles Guardian

---

# BOARD MEMO — The Expansionist
## Aurora rev 3 HYBRID · Global Enterprise Sale Lens · 2026-07-16

**Standing acknowledged:** the founder's hybrid ruling is settled. This memo does not
re-litigate the direction; it assesses whether "one brand, two dialects" survives global
enterprise diligence, how to codify it, and re-ranks my prior merge conditions against the
staging build as it actually exists today (I re-verified the code, not the pack's claims).

---

## 1. "One brand, two dialects" — is it a sellable diligence story?

**Yes — and it is a BETTER story than rev 2's uniformity, on one condition: it must be
written down.** The distinction that matters in an enterprise procurement room is not
"identical pixels everywhere"; it is "governed divergence vs. accidental divergence."

- **The precedent is the strongest in the industry.** Bloomberg Terminal is a vivid,
  dense, dark instrument; Bloomberg's mobile and B-Unity surfaces are calm, restrained,
  jewel-toned. FactSet and LSEG Workspace do the same. Nobody in a fund's ops review has
  ever marked a vendor down because the desk tool is louder than the phone app — they mark
  vendors down when the two surfaces *contradict* each other (same datum, different color
  meaning) or when the vendor cannot explain why they differ.
- **The sentence a salesperson can say:** "One brand, two dialects — the web terminal is
  the *instrument* (vivid, dense, built for an analyst's two-monitor day); mobile is the
  *jewel* (calm, glanceable, built for the partner's pocket). Same structure, same
  typography, same chrome, same data — different volume." That is demo collateral, not
  spin.
- **What makes it defensible rather than post-hoc:** the hybrid keeps the STRUCTURAL
  identity shared (Plus Jakarta Sans 400–800, midnight #0C1B3A/#1B3066 chrome, white
  canvas, Aurora ink, pill chips, borderless cards) and diverges ONLY on the data-semantic
  layer. That is exactly the right cut line. Diligence reads: shared skeleton = one
  platform; divergent data palette = platform-appropriate expression. The inverse split
  (shared colors, divergent structure) would read as chaos.
- **The one thing that would kill the story:** if the divergence lives in tribal memory
  and a CLAUDE.md paragraph instead of a contract document. Today CLAUDE.md §12 says the
  web detail rails MIRROR the mobile color scheme via `mobileTheme.ts` — that language is
  now factually wrong in spirit (mobile Aurora BANS the vivid colors the web just
  restored). An acquirer's technical diligence WILL read the two design docs against the
  code; a contradiction between the master instructions and the shipped surfaces is a
  finding. Fix the paperwork with the merge.

**Verdict on the story: sellable, provided it is codified as a contract (below) and §12
is rewritten from "parity of colors" to "parity of DATA + STRUCTURE; dialect on
expression."**

## 2. Codification — WEB_DESIGN_SYSTEM.md (contract mirroring frontend/DESIGN_SYSTEM.md)

Create `web-terminal/WEB_DESIGN_SYSTEM.md` with the same authority language the mobile
Aurora contract carries ("this file wins over taste"). Proposed outline:

1. **IDENTITY & SCOPE** — "The web terminal is the vivid INSTRUMENT dialect of the
   NowTrendIn brand. Mobile (frontend/DESIGN_SYSTEM.md, Aurora) is the calm JEWEL
   dialect. Both are dialects of ONE language; this section names what is SHARED and
   IMMUTABLE across both: Plus Jakarta Sans (400–800, self-hosted), midnight chrome
   #0C1B3A/#1B3066, white canvas, Aurora ink (#16264A/#3C4663/#9A9AA2), pill chips,
   borderless soft cards, Title Case topics, hairline dividers, WCAG thead shade."
2. **THE DIALECT RULE (the sellable clause)** — divergence is PERMITTED only on the
   data-semantic color layer and density; divergence is FORBIDDEN on structure,
   typography, chrome, spacing grammar, and — hard rule — on *meaning*: a hue may carry a
   different intensity per platform but NEVER a different semantics (green = confirmation
   /up on both; red = down/error on both; orange = emphasis on web, absent on mobile —
   absent is allowed, contradictory is not).
3. **ONE MEANING PER HUE — the semantic color registry** — the single normative table:
   #df7a36 orange = emphasis/N/brand only; #2D7EEF = Detection; #00C896 = Confidence +
   up-moves; #DC2626 = down/error ONLY; #D4A017 gold = Enterprise tier + EMERGING/
   MODERATE stages; #E85A1E amber = WATCHING/MARGINAL; greys = monitoring/muted. Every
   NEW color must be added here before use, with its one meaning. (This is the section a
   diligence team photographs.)
4. **TOKEN AUTHORITY** — all colors live in `:root` CSS variables + `mobileTheme.ts`
   (interim), migrating to ONE generated token file (JSON → CSS vars + TS export). Raw
   hex literals outside the token layer are a lint failure. White-label variables named
   here.
5. **TYPOGRAPHY & NUMERALS** — Jakarta stack; the `--mono`/tabular-numeral rule for every
   data column (score cells, ledgers, screeners must verify tabular alignment); size/
   weight scale; Title Case dictionary reference.
6. **COMPONENTS** — pills, cards, chips, tables, detail rails, stage/tier/maturity/
   verdict palettes (the restored mobileTheme tables reproduced as normative).
7. **ACCESSIBILITY & CONTRAST FLOORS** — WCAG AA on canvas AND on midnight chrome
   (#df7a36-on-#0C1B3A passes for large/bold text only — write the floor: orange on
   chrome at ≥600 weight or ≥14px, never body-size regular).
8. **§17 SOURCE-DISPLAY + DISCLAIMER hooks** — restate the contributing-sources-only rule
   and the founder's verbatim disclaimer placement as design-contract items.
9. **PARITY & ENFORCEMENT** — what the Frontend Consistency agent checks (data + labels +
   structure parity; NOT color parity), and the amendment process (founder sign-off).
10. **DARK MODE (RESERVED)** — placeholder section declaring dark mode a planned second
    theme of the SAME token registry, so tokens are named theme-neutrally now
    (`--canvas`, not `--white`).

Simultaneously amend CLAUDE.md §12: replace "Mobile color scheme mirrored for the web
detail rails" with "Web + mobile share DATA/STRUCTURE parity; color expression follows
each platform's design contract (frontend/DESIGN_SYSTEM.md = jewel; web-terminal/
WEB_DESIGN_SYSTEM.md = instrument); semantics per the shared hue registry."

## 3. Re-ranking my prior conditions (verified against staging code today)

**#1 — Font self-hosting: STILL MY PRE-MERGE BLOCKER, unchanged and now verified
outstanding.** `web-terminal/index.html` lines 9–12 still preconnect to
`fonts.googleapis.com`/`fonts.gstatic.com` and load Jakarta from the CDN at runtime. All
three failure modes from my last memo stand: (a) blocked-CDN client networks render the
demo in Segoe UI *in the exact rooms we sell in*; (b) EU GDPR exposure (German case law
on remote Google Fonts) — a named line-item on Zurich/Frankfurt security questionnaires;
(c) the Tauri desktop flagship phones Google on every launch and falls back offline. The
hybrid made this MORE important, not less: the whole ruling is about a precise visual
identity, and this is the one dependency that silently swaps that identity for a system
font inside a client's building. One hour (`@fontsource/plus-jakarta-sans` or vendored
woff2), three diligence findings closed. **Rank: unchanged, #1, pre-merge.**

**#2 — Token-file unification for white-labeling: RISES in priority (was fast-follow;
now the load-bearing proof of the dialect story).** "One brand, two dialects" is a claim;
a single token registry generating both `styles.css` vars and `mobileTheme.ts` is the
*evidence*. Current state: orange is properly tokenized (`--early:#df7a36`), but I count
~68 raw hex literals in styles.css, ~29 in TSX components, and `mobileTheme.ts` remains a
second hand-maintained source of truth. Every stray hex is (a) a white-label leak and
(b) a place where the two dialects can silently contradict the hue registry. Upgrade
this from "fast follow" to **first post-merge sprint, with the lint rule landing in the
same PR as WEB_DESIGN_SYSTEM.md** — the contract without the enforcement is a brochure.
White-label remains the biggest revenue-side opportunity in the whole design program:
sovereign funds and prime-broker resellers pay for "your chrome, our instrument," and
this token layer is 80% of that SKU.

**#3 — Dark mode: DROPS to roadmap (post-merge, pre-first-enterprise-POC).** The hybrid
weakens the urgency two ways: the midnight chrome already gives the terminal an
institutional dark frame, and the vivid data palette was tuned on a white canvas —
rushing a dark theme would force re-tuning every restored hex and re-fighting settled
collisions. But do not delete it from the plan: trading desks EXPECT a dark terminal
theme (Bloomberg is the reference retina), and the first serious hedge-fund POC will ask.
The cheap move now is naming discipline only — theme-neutral token names + the reserved
§10 in the contract — so dark mode later is a second value-set, not a rewrite.
**Rank: #3, explicitly deferred, tokens named for it now.**

## 4. Hybrid-specific coherence notes (Question A substance)

- **The warm-hue cluster is the one NEW risk the combination creates.** Orange #df7a36
  (emphasis), amber #E85A1E (WATCHING/MARGINAL), gold #D4A017 (Enterprise tier +
  EMERGING/MODERATE) are three adjacent warm hues now on one screen. Each has one
  meaning — the discipline holds ON PAPER — but at 13px pill size, gold vs orange is a
  squint. Mitigation is cheap and non-color: stage/tier pills always carry their LABEL
  (never color-only encoding), and the hue registry (contract §3) pins the three meanings.
  No re-coloring needed; write the "never color-only" rule.
- **Orange on midnight chrome:** #df7a36 on #0C1B3A is roughly 5:1 — passes AA for
  large/bold text, fails for small body text. The nav-accent/wordmark uses are fine;
  codify the weight/size floor (contract §7) so no future body-size orange-on-chrome
  slips in.
- **Green double-duty is the palette's one genuine ambiguity** (#00C896 = Confidence
  metric AND up-moves). It is inherited from the original palette, both meanings are
  positive-valence, and mobile shares it — acceptable, but register it explicitly in the
  hue table as a KNOWN dual with a rationale, so diligence finds a decision, not an
  oversight.
- Otherwise the hybrid is coherent by construction: vivid semantics ride on Aurora
  structure, and the rev-2 garnet collision is gone because the original palette never
  had it.

## 5. Verdicts

| Question | Verdict | Biggest opportunity | Biggest blocker |
|---|---|---|---|
| **A — Hybrid coherence** | **APPROVE** | The instrument identity is now demo-differentiated from every calm SaaS dashboard a fund has seen this quarter — vivid-on-Aurora photographs well on a trading floor. | The warm-hue cluster (orange/amber/gold) at pill size — solved by the never-color-only rule + hue registry, not by re-coloring. |
| **B — Cross-platform divergence policy** | **APPROVE-WITH-CONDITIONS** | "One brand, two dialects" with Bloomberg-grade precedent becomes a *diligence asset* — governed divergence reads as design governance, i.e., acquisition-grade maturity. | Condition: it must be CODIFIED — ship WEB_DESIGN_SYSTEM.md (outline above) + rewrite CLAUDE.md §12 parity language with the merge; an undocumented divergence contradicting the master doc is a diligence finding. |
| **C — Merge readiness** | **APPROVE-WITH-CONDITIONS** | Merging unblocks the white-label token program (the design program's only direct revenue line). | Condition (unchanged, re-verified in code today): **self-host Plus Jakarta Sans before merge** — index.html still loads Google Fonts at runtime; blocked-CDN demo failure + GDPR line-item + Tauri offline fallback. ~1 hour. Token unification + lint = first post-merge sprint; dark mode = roadmap with theme-neutral token names now. |

**One-line summary:** the hybrid is the most sellable web identity this product has had —
approve it, but make the dialect a signed contract (WEB_DESIGN_SYSTEM.md + §12 rewrite),
and do not let it onto main while the flagship enterprise surface still fetches its
typeface from Google.

— The Expansionist

---

# BOARD MEMO — The Outsider (VC / ex-hedge-fund banker)
## Aurora rev 3 HYBRID re-review — 2026-07-16
### Evidence: live staging walk (Dashboard, Trends grid, FIFA World Cup detail rail, Accuracy Ledger, Market Signal) + DOM/computed-style inspection at https://nowtrendin-terminal-1183c0ac00c4.herokuapp.com

The direction is ruled and I am not re-litigating it. For the record: the hybrid is what I
asked for last round, and on the screen it lands. This memo is the buyer's-chair pass —
does it read as a $250k instrument, and what still smells like retrofit.

---

## 1. THE BUYER'S FIRST 10 SECONDS

Midnight chrome (#0C1B3A topbar confirmed via computed style), white canvas, Jakarta,
orange search pill, orange N column, blue Detection / green Confidence, bright stage
pills, red confined to down-moves and high-risk numerics. That combination sits squarely
in the AlphaSense / YCharts / Koyfin visual band — credible institutional territory. The
monospace numeral stack on data columns (`ui-monospace / SF Mono / JetBrains Mono`,
verified in computed styles) is exactly the right instinct; columns align and read like a
terminal, not a dashboard toy. Density on the Trends grid and Market Signal table is
right for a trader audience.

Verdict on the core question: **yes, the hybrid reads as the instrument.** The vivid
data palette on Aurora structure is coherent, not clownish. What remains between this and
"designed, not retrofitted" is almost entirely copy/data hygiene, not color.

## 2. COLLISION AUDIT (the specific questions asked)

- **Orange emphasis vs gold Enterprise/warning** — NOT a live collision. I scanned the
  rendered DOM: zero elements paint #D4A017 gold on the dashboard; the ENTERPRISE chip is
  a muted green-tinted pill (rgba(46,125,91,…)), well clear of #df7a36. The amber
  "INDICATING" / "gap 0" pills are the nearest neighbors to orange and they read as a
  distinct family. Pass.
- **#df7a36 on midnight chrome** — the topbar search placeholder computes to
  rgb(176,122,79) on #0C1B3A: roughly 4.4–4.6:1. Acceptable for placeholder text,
  borderline for anything smaller/lighter. Rule to write down: on midnight chrome, orange
  may tint CONTAINERS and placeholders, but running text on chrome stays in the light
  ink ramp. Currently honored; codify it so a future PR doesn't break it.
- **Bright green Confidence vs green up-moves** — this is the one REAL residual
  polysemy, and it is wider than the pack states: on one screen green is simultaneously
  Confidence (ring/column), up-move, BREAKOUT stage pill, INFLOW chip, LED verdict, and
  the color of the 9.2% honest hit-rate figure. Defensible as a "green = positive
  family" convention (AlphaSense does the same), but it must be DOCUMENTED as a family
  with one hard rule inside it: **red/green encode OUTCOME DIRECTION only in cells that
  are outcomes; metric-identity green (Confidence) never appears in a directional
  column.** Today that holds. Keep it held.
- **New collision found, minor:** Citigroup "% vs baseline" renders **0% in red**. Zero
  is neutral; paint it ink-grey. Red must mean loss, never "not positive." Same logic:
  the 9.2% honest hit rate in GREEN is color editorializing a number a skeptical PM will
  attack — set headline stats in neutral ink and let the number defend itself.

## 3. RETROFIT TELLS (what still screams retrofit, in demo-kill order)

1. **Fonts are rented, not owned.** The live page loads Plus Jakarta Sans from
   fonts.googleapis.com/fonts.gstatic.com (confirmed in the document `<link>` tags; zero
   bundled @font-face rules). Behind a bank VPN, VDI, or an ad-blocking proxy — i.e., the
   exact machines this demos on — the instrument falls back to Segoe UI and the whole
   Aurora identity evaporates. Also a data-residency/telemetry question compliance will
   ask. Self-host woff2 in the bundle. This is my #1.
2. **A dead robot on the flagship detail rail.** The AI Context box shows "Generating a
   source-aware definition…" indefinitely (Anthropic credits exhausted — known ops
   state). An IC watching a spinner that never resolves concludes the product is broken.
   Apply the §17 spirit to the AI lane: when the stage is down and no cached explainer
   exists, render NOTHING, not a promise.
3. **Internal diagnostics leaking to the buyer.** The FIFA World Cup rail leads with
   "backfill(lifecycle-rule): 537 cycles / 29 days — calibration-neutral (matches
   fallback 0.45)." That is engine-room language — it half-exposes internal calibration
   mechanics the enterprise-analysis standard says stay confidential, and it reads like a
   debug string shipped to prod. Replace with the plain-English maturity sentence only.
4. **Raw key leakage.** Category column prints `Current_events` (underscore) while the
   filter chip above it says "Current Events." One `formatCategory()` fixes it; its
   absence says "we bound the API field straight to the cell."
5. **Explainer-strip typography is broken.** The peach explainer bands on Accuracy
   Ledger and Market Signal render as jumbled fragments ("Pre- = the Google … 7 days —
   the topic entered…", a sentence beginning with a period on Market Signal). Inline
   emphasized tokens are shattering the sentence flow. On the LEDGER page — the moat, the
   page I'd linger on in a demo — the explanation of the methodology is unreadable.
6. **Naive Title Case.** "Asi"/"Agi" (should be ASI/AGI), "Multi Lingual," "Strait Of
   Hormuz," "FiEE, Inc Common Stock," plus the lowercase "space ipo" dashboard tile
   title against Title Case everywhere else. The casing dictionary on the punch-list is
   real; acronyms + minor-words ("of") + a per-topic override map.
7. **Cryptic tile glyphs.** LED REFEREE CHECK reads "0√ · 6- · 2." — symbol soup. Label
   the counts (Corroborated / Not corroborated / Unchecked).
8. **Demo-path data, not design:** the first screen's top trends include "Shutting" and
   the ledger's top row is "Multi Lingual." No palette survives a top-of-book fragment.
   Curate the demo account's default sort or lean on the fragment gate before any IC
   walk-through.

## 4. VERDICTS

### (A) Hybrid coherence — **APPROVE-WITH-CONDITIONS**
Plain English: the vivid-data-on-Aurora combination works and looks like money; the
one-meaning-per-hue discipline is restored in substance. Conditions: document the green
"positive family" with the outcome-column rule (§2), neutral-ink zeros and headline
stats, and codify the orange-on-chrome rule.
**Point-blank question:** *If green means Confidence AND up AND breakout AND inflow, can
a PM tell me what a green number means in a column he's never seen — without reading the
header?* (Today: yes, because outcomes and identities never share a column. Write that
rule down before it becomes false.)

### (B) Cross-platform divergence — **APPROVE**
Plain English: "one brand, two dialects" is not just sellable, it's the industry norm —
Bloomberg Terminal and Bloomberg's mobile app share semantics, not saturation. Web =
vivid dense instrument for the desk; mobile = jewel-calm Aurora for the pocket. The rule
to write into CLAUDE.md §12: **"Shared semantics, divergent gamut."** Hue MEANINGS
(Detection, Confidence, up/down, stage ladder, verdicts) are contractual across all three
platforms and stay parity-enforced by /frontend-consistency; hue VALUES are per-surface
dialect, with mobileTheme.ts as the web/desktop data palette of record and Aurora
(frontend/DESIGN_SYSTEM.md) as mobile chrome of record. Red = loss/error on every
surface, no exceptions.
**Point-blank question:** *When an Enterprise user walks from the terminal to the phone
mid-trade, does anything change MEANING — or only intensity?* If the answer is ever
"meaning," the divergence policy is broken.

### (C) Merge readiness — **APPROVE-WITH-CONDITIONS**
Plain English: merge rev 3 — the palette and structure are done and staging is stable;
holding the branch open invites drift. But the merge is not the demo. Conditions split:
**Pre-merge / immediate (P0, blocks any IC demo):**
1. Self-host Plus Jakarta Sans (woff2 in bundle, kill the Google Fonts links).
2. Hide the dead "Generating a source-aware definition…" state when the AI lane is down.
3. Scrub internal diagnostics ("backfill(lifecycle-rule)… fallback 0.45") from rails.
4. `Current_events` → "Current Events" (one formatter, all category cells).
5. Fix the explainer-strip sentence flow on Ledger + Market Signal.
**P1 (this sprint):** casing dictionary + tile-title casing; neutral-ink zeros and
headline stats; label the referee-tile counts; write the §12 "shared semantics, divergent
gamut" language.
**P2 (post-merge, deliberate):** off-white canvas A/B (#FAFBFC-class, glare over 8-hour
sessions); dark mode as a fast-follow (traders live at night — this is the most-requested
terminal feature in the category); favorites hexes.
**Point-blank question:** *Would you run the IC demo on hotel Wi-Fi with
fonts.googleapis.com blocked?* If not, the $250k instrument's typeface is currently
rented from a CDN, and that's a ten-minute fix.

## 5. BOTTOM LINE FROM THE BUYER'S CHAIR

The hybrid clears the bar I set: it reads as an instrument, not a website. Nothing left
on the punch-list is a design decision — it is all finishing. The tells that remain
(rented fonts, a dead spinner, debug strings, underscore keys, broken explainer copy)
are exactly the class of thing a hedge-fund diligence analyst screenshots and puts in
the "is this real?" column. Clear the five P0 items and I would put this in front of an
investment committee without apology.

— The Outsider

---

# THE EXECUTIONER — Board Memo: Aurora Rev 3 (Founder Hybrid)
**Date:** 2026-07-16 · **Scope:** merge-diff coherence verify + merge sequence + cut list
**Staging verified live:** https://nowtrendin-terminal-1183c0ac00c4.herokuapp.com

The direction is ruled. I verified the artifact, not the taste. Rev 3 is one pre-merge
line away from clean.

---

## 1. VERIFICATION RESULTS (fetched from staging, diffed against main)

### 1.3 Bundle serves the rev-3 hash — CONFIRMED
- Staging `index.html` references `assets/index-Bvy1fa8w.css` + `assets/index-DWXthJKM.js`
  — exactly the assets introduced by rev-3 commit `2795a92` ("staging: Aurora rev 3") in
  `web-deploy-terminal`.
- Byte-level proof: md5 of the CSS served by Heroku = md5 of the committed
  `dist/assets/index-Bvy1fa8w.css` = `838f3b1d8505e5961a380fdb4c3da5be`. No stale dyno,
  no CDN ghost. Source branch `aurora-web-redesign` HEAD `85f2e92` matches.

### 1.2 Override block — VALID, no dead rules
Tail-of-bundle override block contains only: `.topic-name` (6 refs in served JS),
`.score-cell` (11 refs), `.main-title,h2,h3` (22 refs), `input,select,textarea`
(element selectors), `::selection`/`::-moz-selection` (orange `#df7a3633` tint —
on-brand emphasis). Every class is live in the bundle. Nothing to cut here.

### 1.1 Jewel-palette ghost hunt — ONE real ghost, one borderline, one stale comment
Full sweep of every `#2A5B9E` / `#2E7D5B` occurrence in the served CSS:

| Occurrence | Where | Verdict |
|---|---|---|
| `.avatar` gradient `#2A5B9E→#2E7D5B` | topbar avatar (chrome) | DELIBERATE — allowed |
| `.plan` badge (jewel-green tint + `#CFE4DA`) | topbar plan pill (chrome) | DELIBERATE — allowed |
| `--ink-*` midnight vars | chrome scaffolding | DELIBERATE — the ruling keeps them |
| **`.g-lev{color:#2E7D5B}`** | **Grade page, "Leverage Health X/100" — LIVE DATA PATH** (`Grade.tsx:103`) | **GHOST. Main is `#10B981`. Grade.tsx was restored but the stylesheet kept the jewel recolor. FIX PRE-MERGE (1 line, styles.css:338).** |
| `.lg-stg.aligned{background:#2a5b9e24;color:#8FA0C6}` | Login page illustrative demo pill (`Login.tsx:182`, hardcoded SAMPLE, sits on midnight `--ink` bg) | BORDERLINE. Readable (ink-text-2 on ink bg) and not live data — but main's vivid `rgba(47,111,237,.14)/#7aa6f5` should be restored so the stage-pill family reads identically on login and in-app. FIX PRE-MERGE (1 line, styles.css:443). |
| Stale CSS comment "Detection #2A5B9E · Confidence #2E7D5B" | styles.css comment | Actual vars are correctly `--det:#2D7EEF`, `--conf:#00C896`. Fix the comment so the next engineer doesn't "restore" the wrong palette. |

Data color path is otherwise CLEAN: `--det:#2D7EEF` / `--conf:#00C896` /
`--early:#df7a36` / `--up:#00C896` / `--down:#DC2626`; bright stage-pill tint pairs
(`--bk/--st/--em/...`) all original-vivid. One meaning per hue holds: red `#DC2626` is
down/error only; orange is emphasis; emerging amber text is `#8a6d0f`, not orange.
`#df7a36` on `#0C1B3A` chrome ≈ 5.6:1 — passes AA.

### Restore integrity — CONFIRMED
`Grade.tsx`, `MarketSignal.tsx`, `Methodology.tsx`, `Login.tsx`, `SignalAnalysis.tsx`,
`App.tsx`, `Shell.tsx`: **0 diff lines vs main.** `mobileTheme.ts`: byte-identical color
values vs main + one ADDITIVE helper (`titleCaseTopic`, display-only) — the "restored"
claim is honest. Total merge surface: 9 files (index.html font link, mobileTheme
additive, styles.css retheme, titleCase applied in Alerts/Dashboard/History/Ledger/
Screener/Watchlists). The diff shape is coherent and small. This is mergeable.

---

## 2. VERDICTS

**(A) Hybrid coherence — SHIP (APPROVE-WITH-CONDITIONS).**
Steps, all pre-merge, ~10 minutes:
1. `styles.css:338` `.g-lev` `#2E7D5B` → `#10B981` (main's value).
2. `styles.css:443` `.lg-stg.aligned` → `background:rgba(47,111,237,.14); color:#7aa6f5`.
3. Fix the stale det/conf jewel comment in styles.css.
4. Rebuild, redeploy staging, re-run the hex sweep (expect `#2E7D5B`/`#2A5B9E` only in
   `.avatar`/`.plan`/`--ink` radial washes).
No new collisions found: orange emphasis vs Enterprise gold `#D4A017` — gold is absent
from the CSS (tier colors live in restored mobileTheme, original values); green
Confidence vs green up-moves share `#00C896` deliberately, as production always has —
pre-existing, not introduced by the hybrid; not a blocker.

**(B) Cross-platform divergence policy — SHIP.**
"One brand, two dialects" is sellable to this audience: web = vivid instrument (trading-
terminal grammar hedge funds expect), mobile = Aurora jewel calm. It is defensible ONLY
if written down. Steps:
1. Update CLAUDE.md §12: parity = same sections, data points, and SEMANTIC color mapping
   (mobileTheme.ts is the shared semantic map for detail rails — now again identical to
   main); hex-level identity is NOT required on chrome/structure. Web data palette =
   vivid originals; mobile UI palette = frontend/DESIGN_SYSTEM.md Aurora (which BANS the
   vivid hexes in mobile chrome).
2. Point the Frontend Consistency agent at semantic parity (labels/sections/mapping),
   not hex equality, for the diverged tokens — otherwise it will false-alarm every run.
3. One sentence in Methodology/docs is enough externally; no user-facing change needed.

**(C) Merge readiness — SHIP-LATER (hours, not days): ready AFTER A's fixes + founder walk.**
Do not merge the current `85f2e92` as-is; merge the fixed build.

---

## 3. MERGE SEQUENCE — REV 3 (re-issued)

0. Pre-merge fixes (A.1–A.3) on `aurora-web-redesign`; build; deploy staging; hex sweep.
1. **Founder walk** of fixed staging vs production, side by side. Chairman says GO.
2. **Merge:** `git checkout main && git merge --no-ff aurora-web-redesign`
   (commit msg: "Aurora rev 3 hybrid: Aurora structure + original vivid data palette").
   `--no-ff` so the whole redesign reverts with one `git revert -m 1`.
3. **Build + record rollback:** `npm run build` in `web-terminal/`; record the current
   `gh-pages` HEAD SHA and current Heroku release (`heroku releases -a nowtrendin-terminal`)
   in the commit/session log as ROLLBACK POINTS.
4. **Deploy gh-pages** (the CANONICAL production — GitHub Pages, worktree steps per
   deploy memory; the Heroku app is the mirror). Verify the live site serves the new
   bundle hash.
5. **Mirror sync:** push the same dist to `web-deploy-terminal` → `heroku/main`
   (nowtrendin-terminal), same-hash check.
6. **Parity check:** run `/terminal-deploy-parity` (Pages vs gh-pages branch vs Heroku
   mirror by bundle hash) + `/frontend-consistency` (semantic parity per B).
7. **Rollback plan (pre-agreed):** gh-pages → force-push recorded SHA; Heroku →
   `heroku releases:rollback vN`; main → `git revert -m 1 <merge>`. Rollback is one
   command per surface; no data migration involved — visual-only change.

---

## 4. FINAL CUT LIST

| Item | Ruling | Why |
|---|---|---|
| `.g-lev` jewel green in data path | **CUT NOW** (pre-merge fix) | last data-path ghost |
| `.lg-stg.aligned` jewel pill | **CUT NOW** (pre-merge fix) | pill-family consistency |
| Stale jewel comment in styles.css | **CUT NOW** | prevents future mis-restore |
| Dark mode | **CUT** | founder ruled light; second theme doubles the QA surface for zero ruled demand |
| Off-white canvas | **CUT** | founder walked it and chose white; re-litigating a settled aesthetic is waste |
| Jewel palette anywhere in data colors | **CUT** (enforced by the hex sweep in step 0) | the ruling |
| Font self-hosting (Plus Jakarta Sans is a Google Fonts runtime dependency) | **SHIP-LATER** — first post-merge task | availability + privacy for a hedge-fund audience; ~30 min: woff2 into dist, swap the `<link>` |
| Casing dictionary (acronyms: "Ai" → "AI", tickers, "iPhone") | **SHIP-LATER** | `titleCaseTopic` heuristic already preserves interior caps; add a small exceptions map when a real miscasing is reported |
| Favorites hexes (star/favorite accents aligned to orange emphasis) | **SHIP-LATER** | cosmetic, non-blocking, batch with the casing pass |

**Bottom line:** the artifact matches the ruling to within three one-line stylesheet
edits. Make them, walk it, merge it, and stop redesigning the terminal.

— The Executioner

---

# BOARD MEMO — The Economist · Aurora rev 3 (founder hybrid) re-review
**Date:** 2026-07-16 · **Ruling status:** hybrid direction is SETTLED; recommendations only.
**Evidence:** board_pack_hybrid.md; code-verified against `web-terminal/src/lib/mobileTheme.ts`,
`components/Disclaimer.tsx`, `views/{Ledger,Login,Grade,Screener,MarketSignal,History,Crypto}.tsx`, `styles.css`.

---

## 0. Where I stand on my own prior P1 — honestly reassessed

My prior P1 said: *meaning-colors and outcome-colors never share a hue family on one view.*
The hybrid restores green #00C896 as BOTH Confidence (a component meaning) and up-moves (an
outcome), blue #2D7EEF as Detection. Was P1 right as written? **No — it was overbroad, and I
amend it.**

The economic argument (Kindleberger: *conventions are capital*): green=good/up is the single
deepest sunk convention on any trading desk. Fighting it costs cognition every session and
buys nothing. The correct test is not "no shared hue" but a **valence-contradiction test**:

> A meaning-color and an outcome-color may share a hue **only if their valences can never
> contradict on the same row.**

Green passes this test cleanly: Confidence = confirmation = "the read is validated" — the
same valence as "up/good." A Confidence-green cell beside a green up-move never tells the
user two opposite things in one hue. The palette that FAILED the test was rev 2's garnet —
a loss-red-adjacent hue carrying *emphasis*, i.e., a positive-attention meaning wearing the
market's universal loss color. That contradiction is gone by construction in rev 3.

So: **the inherited green collision does NOT merit conditioning the merge.** It downgrades
from a blocker to a documented residual, with one real (but copy-side, not palette-side)
exposure:

- **Residual:** Confidence-green beside a red down-move on the same row could tempt a user
  to read Confidence as a buy signal that "failed." That is a *communication/liability*
  surface, not a legibility one — and the platform's own copy already carries the mitigation
  (`SCORE_ROLES`: Confidence = "Precision," never "bullish"; measurement-not-advice
  everywhere). Keep it that way; do not let any future copy pair Confidence-green with
  directional language.
- **Watch-item, red family:** the gap band "Very early — detected, not confirmed" renders
  in red #CF2A1B. Red elsewhere = down/error/VIRAL/ELEVATED. "Very early" is the product's
  prize, wearing the caution color. This is *defensible* (unconfirmed = risk-caution valence
  — genuinely anti-euphoric) and I would not change it; I record it so nobody later
  "fixes" it into a celebratory hue.

---

## A. HYBRID COHERENCE — verdict: **APPROVE**

**Framework:** valence-contradiction test (above) + redundant-encoding check (hue must
never be the *sole* carrier of a meaning) + warm-family congestion audit.

1. **Green (Confidence / up / BREAKOUT / EMERGING-maturity / AT_BASELINE / aligned-gap).**
   Many-to-one, but every use is confirmatory-valence and every chip carries a text label;
   outcome green additionally carries sign and monospace-delta position. Bloomberg reuses
   green across dozens of meanings; desks parse by position+label, hue is an accelerant.
   Passes. Mechanical rule to document: *no two same-hue chips of different dimensions
   (stage vs maturity vs tier) adjacent without their text labels.* Currently satisfied.

2. **Blue (Detection / STRONG / NEW / ROUTINE-tier).** Same structure, same pass, same rule.

3. **The warm family is the real congestion point — five hues:** emphasis #df7a36, brand
   "Now" #EE6A2A, amber #E85A1E (WATCHING/ACTIVE), gold #D4A017 (EMERGING-stage/MODERATE/
   warning), maroon #B5341B. The NEW entrant is emphasis-orange. #df7a36 vs #E85A1E vs
   #EE6A2A are near-neighbors. This does not fail the valence test (none is a loss color),
   but it fails *quietly* if emphasis-orange ever appears as a status pill — an emphasized
   N value beside a WATCHING pill would read as one "warning family."
   **Prescription (condition under C):** write the emphasis rule down as a disclosed
   MECHANICAL rule: *orange #df7a36 marks the proprietary-N dimension and interactive foci
   (N column, N-card, search chrome, nav accent, wordmark, gap-emphasis at its disclosed
   threshold). It never encodes magnitude, direction, urgency, or status; it never appears
   as a pill.* Put this in `styles.css` (the `--early` token comment) and CLAUDE.md §12.
   This is exactly my prior "emphasis as disclosed mechanical rule" prescription — the
   hybrid satisfies it in behavior (column-wide, not editorial cherry-picking); it must now
   satisfy it in documentation.

4. **#df7a36 on midnight chrome (#0C1B3A/#1B3066):** likely ~5:1 — fine for the wordmark,
   nav accent, and large glyphs; marginal for small text. **Run a WCAG pass on every small
   orange-on-midnight string; where it fails, lift to the soft variant or enlarge.** Do not
   assert compliance without the measurement.

5. **Anti-euphoria (Kindleberger/Taleb — interfaces that celebrate up-moves manufacture
   mania):** the vivid palette raises the temptation. Checks against rev 3: up/down pair
   #00C896/#DC2626 is symmetric in saturation (good — keep salience symmetric); VIRAL is
   red, not gold-confetti (good); no evidence of up-tick animation (keep it that way —
   **no flashes, pulses, or motion on favorable moves, ever**). The vividness is
   instrument-vivid, not casino-vivid, as long as motion stays out.

## B. CROSS-PLATFORM DIVERGENCE — verdict: **APPROVE-WITH-CONDITIONS**

**Framework:** product-line segmentation (one brand, two dialects). Different audiences
buy different affects: institutions read *density + vivid encodings* as information
(Bloomberg Terminal vs Bloomberg mobile is the exact precedent); consumers read *calm* as
trust. Divergence on data colors is not brand drift — it is correct price-of-attention
segmentation — **provided the invariants are written down and enforced.**

The sellable formulation: **"One measurement, one meaning, two dialects."** Shared across
surfaces (the brand): the numbers themselves, section structure, labels, semantic mappings
(what Detection/Confidence/stages MEAN), typography family, midnight chrome, Title Case,
the verbatim disclaimer, flows byte-identical. Per-surface (the dialect): the data-color
rendering — web = vivid instrument, mobile = Aurora jewel calm.

**Conditions:**
1. **Rewrite CLAUDE.md §12.** Its current language ("Mobile color scheme mirrored for the
   web detail rails in mobileTheme.ts") is now false in direction: mobile Aurora BANS these
   hexes while web restores them, so `mobileTheme.ts` has become the *web data-palette
   authority*, not a mobile mirror. §12 must state the two-dialect rule explicitly and name
   the invariants list above. Also fix the stale header comment in `mobileTheme.ts` itself
   ("mirrored... so the two surfaces read identically" — no longer the contract).
2. **Repoint the Frontend Consistency agent in the same merge.** Parity = same sections,
   data points, labels, and *semantic* color mappings — NOT hex equality on data colors.
   If the agent isn't updated with the skin, it will file false parity alarms forever, and
   real regressions will drown in them (alarm-fatigue is how integrity rules die).

## C. MERGE READINESS — verdict: **APPROVE-WITH-CONDITIONS**

**Framework:** Bernstein's reversibility split — condition the merge only on items that are
(a) integrity/liability-bearing or (b) contracts other systems depend on; defer everything
reversible.

**Code-verified state:** `Disclaimer.tsx` is single-sourced, founder-verbatim (2026-07-07
copy intact), rendered top AND bottom on Screener, MarketSignal, Grade, History, Crypto.
**GAP FOUND: `views/Ledger.tsx` renders NO disclaimer** — zero matches. The Accuracy Ledger
is the single panel a hedge-fund counsel reads first, and the founder rule says all panels,
top and bottom. This is the one true blocker.

**Pre-merge conditions (ordered):**
1. **Ledger disclaimer** — mount `<Disclaimer/>` top + bottom of the Ledger view; while
   there, confirm the ledger UI still publishes blended AND tracked-race rates side by side
   (never the flattering one alone).
2. **§12 rewrite + Frontend Consistency repoint** (B-1, B-2) — same commit as the skin.
3. **Emphasis-orange mechanical rule documented** (A-3) + **WCAG pass on orange-on-midnight
   small text** (A-4).
4. **Font self-hosting** — if Plus Jakarta Sans loads from Google Fonts, self-host before
   merge: third-party font calls are an external dependency, a latency tail, and a request
   log institutional compliance departments notice. Cheap now, awkward after a client asks.

**Post-merge (reversible — do not hold the merge):**
5. Casing dictionary — `titleCaseTopic` is naive: lowercase acronyms ("ai" → "Ai") and
   particles ("Of/The/And" capitalized). Cosmetic; ship a small-words + acronym dictionary.
6. Off-white canvas — A/B against pure white; reversible experiment.
7. Dark mode — real institutional demand (traders live in dark rooms), but it is a second
   full palette-collision audit, not a toggle; scope it properly, demand-driven.
8. Favorites hexes — minor; fold into the emphasis/warm-family documentation when touched.

**Login stays dry — verified:** `Login.tsx` carries only the flame mark and the signature
connector (#df7a36); the disclaimer link is present; no performance claims, no euphoria.
Hold that line: the login page never carries a hit-rate, a testimonial, or an up-arrow.

**Anti-euphoria standing rules (restated for the vivid skin):** no motion on favorable
moves; up/down salience symmetric; catch-all % never externalized as accuracy; blended and
tracked-race always co-published; disclaimer adjacent to every accuracy figure.

---

## PRESCRIPTIONS (condensed)
1. **[BLOCKER]** Ledger view: verbatim `<Disclaimer/>` top + bottom; blended + tracked-race co-displayed.
2. **[BLOCKER]** CLAUDE.md §12 → "one measurement, two dialects" contract; fix `mobileTheme.ts` header; repoint Frontend Consistency agent to semantic (not hex) parity on data colors — same merge.
3. **[BLOCKER]** Emphasis-orange = disclosed mechanical rule (N-dimension + interactive foci only; never a pill, never magnitude/direction) in styles.css + §12; WCAG-check small #df7a36 text on midnight.
4. **[PRE-MERGE]** Self-host Plus Jakarta Sans.
5. **[POST]** titleCase dictionary; off-white A/B; scoped dark-mode audit; favorites hexes.
6. **[STANDING]** No up-move animation; symmetric up/down salience; login stays dry; Confidence copy stays "precision," never directional.
7. **[AMENDED P1]** Replace my old rule with the valence-contradiction test: shared hue between meaning and outcome is permitted only where valences can never contradict on one row. Green passes; any red-family reuse for a positive meaning fails.

**Verdicts: A = APPROVE · B = APPROVE-WITH-CONDITIONS · C = APPROVE-WITH-CONDITIONS.**

— The Economist

---

**Chairman — rulings requested: (1) vivid text vs text-twins vs as-is · (2) font self-hosting pre/post merge · then the merge gate (your staging walk).**
