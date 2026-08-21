# EVIDENCE PACK — round 4. The production verification, and the pattern found inside the register.
### Prepared 2026-08-20 (late) for the nine-seat board. Commit under review: `57e2ae7`.
### Prior rounds: `BOARD_updates-assessment_2026-08-20B.md`, `CLAIMS_EVIDENCE_PACK_2026-08-20C.md`.

---

## 1. WHAT THE LAST BOARD LEFT OPEN

Round 3 reviewed Layers 1–3 (test runner + gate, claim register, three lints) and the
closing of three OPEN claims. The Executioner's verdict on one row was
**`C-DMEASURED-SERVED` — UNVERIFIED (source-only)**, with the instruction: *"Deploying is
necessary and not sufficient; POST the `_precompute_serve_payloads` rebuild and confirm."*
Three seats independently said the claim should read OPEN until seen in production.

This pack reports what happened when that was done.

## 2. THE VERIFICATION (what is now true)

Engine **v370**, after `POST /precompute?top_n=800`. Probe row chosen by querying
`SELECT topic_key FROM velocity_scores WHERE d_measured = 0` — i.e. selected by the
condition under test, not chosen for how it would read. It is a Cyrillic sports topic,
`хапоэль_беэршева_сабах`:

```
d_measured        : False
first_timer_ratio : None
plain_english     : UNMEASURED — no author-bearing or engagement-bearing signals for this
                    topic, so no dark-matter reading exists. This is absence of
                    measurement, not evidence of public origin.
unmeasured_note   : UNMEASURED — this topic carried no author-bearing and no
                    engagement-bearing signals...
```

A control row (`nasa`) returns `d_measured: True`, `first_timer_ratio: 0.0` — a genuine
measured zero, distinguishable from the unmeasured case. §16a stage 2 and §17 hold on the
wire, not only in source.

## 3. THE FINDING (what the route there exposed)

**Deploying was not sufficient, and the gap was not benign.** For several hours after the
fix shipped, production served a stored `serve_payload` written BETWEEN the commit that
added `d_measured`/`unmeasured_note` and the commit that added the `plain_english` guard.
The live object therefore contained, simultaneously:

- `d_measured: false` + an `unmeasured_note` saying D could not be read, and
- `plain_english: "No dark matter signatures. Signal appears to originate publicly."`

An outside reader does not perceive a stale cache there. They perceive a system asserting
a measured conclusion and its own inability to measure, in one response.

**The diagnostic:** both fields are in the SAME dict literal. Code cannot be half-applied
within one object; a stored blob can. That is what identified INV-1 rather than a code
defect. (INV-1: rows older than `SERVE_LIVECAL_MAX_AGE_H` = 48h serve stored values
verbatim — CLAUDE.md §13 footer / GOTCHA G1.)

**Why this is a register-level finding, not a bug report.** `C-DMEASURED-SERVED` claimed
users SEE the UNMEASURED state. Its enforcer is **L3, a source lint**. Both were GREEN for
the entire window in which production served the contradiction. A claim about PRODUCTION
STATE enforced by a check on SOURCE TEXT is the Guardian's pattern — a claim written in
one register, enforced in a weaker one — occurring INSIDE the register built to end it.

Round 3 asked: *"is the claim register itself a claim written in a register stronger than
its enforcement?"* On this row, the answer is yes, and it was found by experiment rather
than by review.

## 4. WHAT WAS BUILT IN RESPONSE (`57e2ae7`)

**(a) SERVE-PAYLOAD GATE** — `.githooks/commit-msg`. Triggers off git's own hunk-header
function context (`get_topic_detail` / `_serve_payload` / `_precompute_serve_payloads`);
refuses the commit unless it asserts `[payload-rebuilt]`. A hook cannot verify production,
so it enforces the only thing available to it: that the author knows the rebuild is a
separate act from the deploy.

PROVEN on a real staged hunk: refuses without the marker, allows with it, silent on
unrelated changes. A first draft referenced `$MSG` (unset; the file uses `$msg`) — under
`set -u` that gate would have ABORTED rather than gated. It was caught by testing the
gate, which is now the second time in one day that testing a new gate is the only reason
it is known to work (the first was the `exit 0` gate-chain defect).

**(b) `C-DMEASURED-SERVED` NARROWED** to what L3 actually proves — source wiring — with an
explicit scope line stating the enforcer "cannot and does not attest to what production is
serving." The production check is recorded as a **DATED OBSERVATION, not a standing
guarantee** (v370, 2026-08-20, named row, named values).

**(c) NEW CLAIM `C-PAYLOAD-REBUILD`** carries the production half, enforced by the new
hookgate.

**State:** 15 of 15 asserted claims enforced. Suite: 10 files, 10 passed, 0 failed, ~5s.

## 5. WHAT REMAINS OPEN (not claimed done)

- **AB-ATTRIBUTION — HARD DEADLINE 2026-08-27.** Paired A/B recompute; after that date
  retention deletes the inputs and today's overlapping changes become permanently
  unattributable. Tracked in `audits/DEFERRED_ITEMS.md`.
- Round-3 register findings NOT yet fixed: the register's **degenerate case (0-of-0
  passes)**; the `sealed` enforcer **never recomputes the hash** it cites; **L3 is
  substring-only**; **no CI** — every gate is laptop-local via `core.hooksPath`, so none
  of it binds a second machine or a cloud agent.
- GDELT second referee arm + wiki-v3; candidate feeds sealed but NOT WIRED (gates 1–3 +
  acceptance harness per feed; ERRATUM 01 binds Marca/Kicker behind ES/DE fixtures);
  rights rows + jurisdiction annex for the seven foreign feeds; `UNSCORABLE` and
  per-domain cells absent from `report()`; `implied_prob` has no writer; tail accounting
  without a disposition; forecast B5 unresolvable as sealed.
- The convergent round-3 ask, still only partly met: **every enforcer should be shown to
  FAIL on a fixture violating its claim** (the `test_feed_tripwire` t6 pattern), applied
  to all 15 claims. The new gate meets it; most inherited rows do not.

## 6. THE QUESTIONS FOR THE BOARD

1. Does §4 actually close the gap in §3, or does it move the same pattern one level
   further out — a production claim now enforced by a hook that still cannot see
   production, on a laptop, with no CI?
2. Is "dated observation, not standing guarantee" an honest instrument or a way to keep a
   green board while the underlying state is unverified between observations?
3. The contradiction in §3 was SERVED to whoever called that endpoint during the window.
   What is the correct disposition of that — nothing, a note, or something else?
4. What is the pattern's NEXT costume?
