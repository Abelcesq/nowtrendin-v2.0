# C7 — CRYPTO COPY DISCIPLINE SWEEP (Graham: measurement, never advice)
**Date:** 2026-08-05 PT · **Chairman-ordered** · Criteria: every crypto user-facing string
states what is MEASURED and its disclosed error (smear/latency/coverage); zero imperative
verbs; zero forward-looking valuation language; "margin of safety" itself never in user
copy; the founder's verbatim disclaimer untouched.

## Strings audited (engine payload + web terminal)

| Location | String (abridged) | Verdict |
|---|---|---|
| crypto_money_gradient.py `_DISCLAIMER` | "tracks significant money movement relative to this coin's own baseline… not intended to be financial, legal or investment advice" | PASS |
| crypto_money_gradient.py interpretation footer | "recorded in the crypto accuracy ledger over time — this is a measurement, not a recommendation" | PASS |
| crypto payload `note` (signal_for) | "A FACT of where money is moving — not advice, not a prediction" | PASS |
| Crypto.tsx main-sub (both branches) | "Measurement, not advice"; absent-state text names the source limit explicitly | PASS |
| Crypto.tsx calibrating banner | "tiers settle as each coin's baseline accumulates… Measurement only — not advice" | PASS |
| Crypto.tsx direction-filter tooltip | "Inflow = informed buying · Outflow = selling · Neutral = no clear net direction" | PASS-WITH-NOTE — describes the measured direction, not an instruction; wording stays descriptive ("informed buying" = the observed Form-4/creation side). Watch that future edits never invert it into "buy". |
| Crypto.tsx rail AI-context disclaimer | founder verbatim disclaimer | PASS (locked — sign-off to edit) |
| Crypto.tsx "What the Crypto signal measures" | explains D/M + ledger records after the fact | PASS |
| NEW: supply section (this change) | "Reference facts, not a valuation or advice" + lost-coins caveat + "no max supply" honest state | PASS (written to the standard) |
| crypto_accuracy_ledger report `note` | "MEASUREMENT of the Crypto Money Gradient's own accuracy… NOT a forecast, NOT advice, NOT a buy/sell signal" | PASS |
| crypto_accuracy_ledger F8 `meaning` | "what a COIN-FLIP detection would score by luck alone" | PASS |

## Findings
- **Zero violations.** No imperative verbs, no price targets, no forward-looking valuation
  language, no "margin of safety" in user copy anywhere on the crypto surface.
- One WATCH item (the direction tooltip) recorded above.
- **Recurrence (the Outsider's "process, not memory"):** this sweep's criteria run as a
  standing checklist line in the weekly /improve-system attorney lens (added this session,
  alongside the C3 supply-stamp review). A new crypto-facing string is in scope the week it
  ships.
