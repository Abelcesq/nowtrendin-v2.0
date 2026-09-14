"""Deferred-items registry — the engine-readable mirror of audits/DEFERRED_ITEMS.md.

C5 (Chairman-ruled 2026-09-14, BOARD_crypto-money_2026-09-14.md): /monitor/deferred-triggers'
docstring claimed it evaluated "every reactivation trigger in audits/DEFERRED_ITEMS.md" while
hard-coding two triggers and never opening the file — and the file is not even in the Heroku
slug (only transfer/ deploys). This registry closes that gap: every `## ` heading in the
shelf document has exactly one entry here, and `transfer/test_deferred_registry.py` FAILS THE
BUILD when the two drift (the same doc↔code bridge as `[cold-start-stated]`). Entries with a
`review_date` are evaluated by the endpoint: past-due → FIRE (reopen for the founder, never an
auto-action). Undated entries are condition-triggered — their conditions stay hand-evaluated
where cheap (D8_T2, S1) or human-walked; registering them here is what makes an unregistered
shelf impossible, which was the defect (three crypto sources + one orphaned date, all unowned).
Nothing may be shelved that is not registered; nothing registered may lack a date or a trigger.
"""

DEFERRED_ITEMS = [
    {"heading": "D8 — score-side exclusion of degenerate positioning components (T1 SHIPPED; fuller exclusion DEFERRED)", "review_date": None},
    {"heading": "S1 — asymmetric outflow gate (PRINCIPLE ARM CLOSED 2026-07-20; n-arm remains)", "review_date": None},
    {"heading": "R1 — SYMMETRY RULING (Chairman-adopted 2026-07-20; standing, not deferred)", "review_date": None},
    {"heading": "Standing reporting/monitoring hardenings SHIPPED — recorded here for the trail", "review_date": None},
    {"heading": "SCHEDULED READER (H6 — so triggers fire by rule, not memory)", "review_date": None},
    {"heading": "S8 — DISPOSITION (Chairman-ruled 2026-08-05 PT; resolves the Executioner-vs-Outsider board split)", "review_date": None},
    {"heading": "C5/C6 — NVT metric + realized-cap corrective (Chairman-ruled shelf, 2026-08-05 PT)", "review_date": None},
    {"heading": "C8 — attention-flow divergence detector (Chairman-approved; gated build)", "review_date": None},
    {"heading": "IDX-RC4 — index self-influence monitor (PUBLICATION GATE; register r1 obligation)", "review_date": None},
    {"heading": "IDX-RC3 — index capacity/AUM-share cap parameter (PRE-LICENSE GATE; register r1 obligation)", "review_date": None},
    {"heading": "FCAST-RESOLUTION — forecast_resolution PIT path (FIRST-RESOLUTION GATE)", "review_date": None},
    {"heading": "PIT-STORAGE — capacity plan for the never-pruned archive", "review_date": None},
    {"heading": "ACC-Q — quarterly benchmark scoring (DATED; Chairman ruling 2026-08-18)", "review_date": "2026-11-30"},
    {"heading": "ACC-LC — recurring lifecycle case study (Chairman ruling 2026-08-18: \"learn from past events\")", "review_date": None},
    {"heading": "A3-CEILING / A3-ECHO / A3-TRIPWIRE — completion items for the \"never measured as nothing\" invariant (Chairman-adopted 2026-08-19, CLAUDE.md §15a)", "review_date": None},
    {"heading": "A4-SEQ — the GHOST_FEEDS remedy sequence (Chairman-RULED 2026-08-19; execute in this order)", "review_date": None},
    {"heading": "D-REMINE — LED feature-mining re-run on the repaired instrument (DATED; board 2026-08-20)", "review_date": "2026-09-30"},
    {"heading": "D-RIGHTS — per-source rights file for the D roster (board 2026-08-20, Buyer gate 3)", "review_date": None},
    {"heading": "AB-ATTRIBUTION — the paired A/B recompute (HARD DEADLINE 2026-08-27; set by data expiry)", "review_date": "2026-08-27"},
    {"heading": "D-FLOOR-3C — score-side honest absence for unmeasured D (ruling 3c, board round 4; GATED)", "review_date": None},
    {"heading": "PII-AUTHOR-HISTORY — author-handle behavioural aggregate: retention, erasure, lawful basis", "review_date": None},
    {"heading": "CRYPTO-COINAPI — perp funding/OI collector: review gate (DATED; Chairman-ruled register, 2026-09-14)", "review_date": "2026-11-10"},
    {"heading": "CRYPTO-COINMETRICS — on-chain activity collector (trigger-based; registered 2026-09-14)", "review_date": None},
    {"heading": "CRYPTO-COINBASE-PREMIUM — retail-premium collector (SHELVED 2026-08-18; registered 2026-09-14)", "review_date": None},
    {"heading": "ETF-ISSUER-REEVAL — issuer-page adapter re-evaluation (DATED — OVERDUE; registered 2026-09-14)", "review_date": "2026-09-05"},
]
