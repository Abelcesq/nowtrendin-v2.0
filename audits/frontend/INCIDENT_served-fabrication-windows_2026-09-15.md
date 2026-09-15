# INCIDENT NOTE — served-fabrication exposure windows (display layer, all classes)

**2026-09-15 · Board item D9 (Challenger R4 exposure accounting, `BOARD_24h-review_2026-09-15.md`).**
Addendum 11 recorded D9 as *"SKIPPED by ruling"*; the founder **reversed that on 2026-09-15 and
ordered it implemented** — this note is that order executed. Provenance rule (§10a): every
intro/fix commit below was traced with `git log -S` on the full (deepened) history, not asserted
from memory. Dates are commit dates (UTC).

**What this incident is:** for the windows below, the web terminal and/or the mobile app rendered
**fabricated display states** — absent data wearing a measured badge (tier fallbacks, a measured-
looking `0`, sign-blind gap prose) — and one **diverged founder disclaimer**. All classes are
DISPLAY-layer: no engine-stored score, serve payload, or ledger row was altered at any point.
What users *saw* was wrong; what was *stored* was not. Detected by the Chairman-ordered all-pages
audit (`ALLPAGES_AUDIT_2026-09-14.md`) and the D11 fabricated-default lint
(`test_display_defaults.py`, 3 further catches on its first run).

---

## Exposure table (intro commit → fix commit → live date, per class)

| # | Class | Surface | Intro (served from) | Fixed in code | Live to users | Window |
|---|---|---|---|---|---|---|
| A1 | Tier fallback `\|\| 'DORMANT'` — absent market tier rendered as DORMANT | Mobile market detail | `0989136` 2026-06-10 | `33ba1db` 2026-09-14 (+ lint catch `30f25f9`) | **⚠ NOT YET — awaits Expo publish** | **2026-06-10 → OPEN** |
| A2 | Tier fallback `?? 'ROUTINE'` — absent crypto tier rendered as ROUTINE | Mobile crypto | `8373ecd` 2026-07-14 | `33ba1db` / `30f25f9` | **⚠ NOT YET — awaits Expo publish** | **2026-07-14 → OPEN** |
| A3 | Tier fallback `\|\| 'ROUTINE'` | Web MarketSignal | `3abe524` 2026-06-15 | `30f25f9` 2026-09-15 | gh-pages `0f8b8f5` 2026-09-15 06:01 UTC | ~92 days, CLOSED |
| A4 | Stage fallback `\|\| 'BACKGROUND'` | Mobile `gradientApi` (feeds multiple screens) | `5e8c388` 2026-06-04 | `30f25f9` | **⚠ NOT YET — awaits Expo publish** | **2026-06-04 → OPEN** |
| B | Dashboard crypto tile: money-absent coins rendered as a **measured 0** and ranked | Web Dashboard | `c7854cc` 2026-06-26 | `60242ee` 2026-09-14 | gh-pages `97533e7` 2026-09-14 22:19 UTC | ~80 days, CLOSED |
| C | K17 sign-blind gap class: negative gaps wearing early-stage prose ("Very early" on lagging topics) | Web (Crypto/MarketSignal/Grade/Dashboard/Screener) + mobile (root: unsigned `gradientApi` gap) | web `965805c`/`0e03688` 2026-06-16; mobile root predates, same lib lineage (`5e8c388` era) | web `60242ee`; mobile `33ba1db` | web live `97533e7` 2026-09-14; **mobile awaits Expo publish** | web ~90 days CLOSED; **mobile OPEN** |
| D | History AI-disclaimer DIVERGED from the founder-verbatim text (sign-off-required, adopted 2026-07-07): dropped "including any and all figures … may be an approximation" | Web History | short variant introduced `29d84a4` 2026-06-18; **became a divergence 2026-07-07** when the verbatim standard landed and this line was not updated | `60242ee` 2026-09-14 (restored byte-identical) | gh-pages `97533e7` 2026-09-14 | 2026-07-07 → 2026-09-14, CLOSED |

**The open half of this incident is the founder's Expo publish.** Production mobile serves
classes A1, A2, A4 and mobile-C **today**; every fix is merged and waiting. The publish is the
closing event — when it runs, append the date here and mark the mobile rows CLOSED.

## External-artifact sweep (Challenger's third ask)

- **In-repo:** no screenshots/captures exist in the repository outside app icon/splash assets
  (swept `*.png/*.jpg/*.jpeg`, 2026-09-15). No buyer-diligence document quotes a per-coin tier
  or the Dashboard crypto-tile zero captured inside the windows (the packs quote ledger/accuracy
  figures, a separate lineage).
- **Outside the repo (founder-only, owed):** any demo screenshots, decks, or screen recordings
  taken between 2026-06-04 and the fix dates may show fabricated tiers/zeros — sweep before any
  external use; annotate rather than delete (they are evidence of the window).

## Standing linkage

- The fabricated-default class now has a permanent enforcer: `test_display_defaults.py`
  (D11 CI lint — `?? '<LITERAL>'` / `\|\| '<LITERAL>'` on display-state fields fails the build).
- Class D's rule stands: the founder disclaimer is verbatim, sign-off required to edit
  (SESSION_LOG 2026-07-07); byte-identity is the test.
- This note is the dated record ruling D9 asked for; recurrence of any class here should cite
  this file and add a row (recurrence-ledger discipline, round-4 B5).
