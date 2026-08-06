# ADVISORY BOARD — INCORPORATING THE BOOK CANON (market cap · crypto · investing)
**Convened:** 2026-08-05 PT at the Chairman's order · **Six archetypes, fully independent**
**Evidence pack:** `EVIDENCE_PACK_bookprinciples_2026-08-05.md` · Canon: Burniske & Tatar
*Cryptoassets*, Lewis *The Basics of Bitcoins and Blockchains*, Graham *The Intelligent
Investor*, + the founder's market-cap brief. Every archetype independently verified the A1
implementation (commit `75e0726`, dark) against the actual code before writing.

**Items:** A1 (the first incorporation — AUM-relative fund weights, venue classes, 4h strike
capture, latency stamps, continuous reconciliation) · C1 size bands · C2 circulating-vs-FDV ·
C3 supply-schedule stamps · C4 attention-beside-flow · C5 NVT · C6 realized cap · C7 Graham
copy sweep · C8 divergence detector.

---

## VERDICT TABLE

| Item | Challenger | Guardian | Expansionist | Outsider | Executioner | Economist |
|---|---|---|---|---|---|---|
| A1 (dark commit) | AWC | AWC | AWC | AWC | SHIP dark / flip NOT shippable | AWC |
| C1 size bands | AWC | AWC | APPROVE | APPROVE | SHIP (3rd) | APPROVE |
| C2 circ-vs-FDV | AWC | APPROVE | APPROVE | APPROVE | SHIP (2nd) | APPROVE |
| C3 supply stamps | AWC | AWC | AWC | AWC | SHIP-LATER | AWC |
| C4 attention∥flow | AWC | AWC | APPROVE | AWC (**rename**) | SHIP-LATER (post-flip) | AWC |
| C5 NVT | shelf | shelf | shelf | REJECT-build/APPROVE-shelf | CUT→shelf | REJECT→shelf |
| C6 realized cap | shelf | shelf | shelf | REJECT-build/APPROVE-shelf | CUT→shelf | REJECT→shelf |
| C7 copy sweep | APPROVE | APPROVE | APPROVE | APPROVE | SHIP (1st) | APPROVE |
| C8 divergence | AWC | AWC | AWC | AWC | SHIP-LATER (>C4) | AWC |

AWC = approve-with-conditions. **Unanimous:** C7 approve (ship first); C5/C6 shelved with
written triggers (the *refusal to fake them* praised by four seats); C8 approved in principle,
gated behind design + pre-registered thresholds + backtest + post-flip flow data.

---

## A1 — THE LOAD-BEARING FINDINGS (all verified in code by the finders)

**F1 — Class-budget invariant: spec ≠ code (found INDEPENDENTLY by 4 seats: Challenger,
Guardian, Executioner, Economist).** The amendment promises the fund class "keeps the coin's
CONFIGURED weight budget… adding funds never grows the class's share." As coded,
`class_budget = Σ weights of funds that VOTED today` (`crypto_signals.py:351`): adding a
configured fund grows the class's voice vs insider-equity (BTC 2.5→4.2 already, D-share
~74%→~82% per the Challenger's recomputation), and a stale fund shrinks it — availability,
not information, moves the mix. Fix before flip: pin a per-coin class budget (or amend the
spec sentence); Executioner adds a startup assertion / cold-start-gate lint for roster changes.

**F2 — Pre-strike duplicate row fabricates "measured quiet" (Challenger — NEW, material).**
`snapshot()` inserts today's daily row at first sight after UTC midnight carrying yesterday's
strike values; `latest_delta` then compares today's stale copy vs yesterday → delta 0.0 →
vote 0.0 "measured quiet IN the denominator" for the ~13–21h before the day's strike lands —
and all weekend (no strikes) while crypto itself trades. The genuine flow point is shadowed
for most of each day. Fix: `latest_delta` must not treat a value-identical pre-strike copy as
a new observation day (or gate the vote on strike-confirmed, which `intraday_report` already
detects); weekends should read "no read (fund market closed)", never zero-in-denominator.

**F3 — The flip is a definitional break the baseline store can't absorb (Challenger — NEW).**
At flip, `proxy_positioning` and `venue_diffusion` change their data-generating process;
months of near-zero crypto baselines + the 0.05 stdev floor → z≥3 → day-one "Money Movement"
~0.96 as a break statistic, not a measurement (the SpaceX artifact class the S5 epoch was
built for). But `MARKET_SERIES_EPOCH` is GLOBAL — bumping it for crypto resets every equity
baseline as collateral. Required before flip: a crypto-scoped epoch or explicit crypto
baseline retirement / forced-CALIBRATING at flip. (Neither A1 nor the spec addressed this.)

**F4 — Monday attenuation (Challenger).** Gap normalization divides weekend-spanning deltas
by CALENDAR days: Monday's one-trading-day flow reads at ⅓ strength vs identical Tuesday
flow — a systematic weekday bias in a signed vote. Normalize by trading days in the gap.

**F5 — Tests not committed (Challenger + Executioner, independently).** The "6/6 synthetic
checks + dominance proof" ran once in-session; nothing in the repo re-runs them. Commit the
harness (dominance sign-flip case included) so the flip can be re-verified in minutes by anyone.

**F6 — Sibling fund-count fields survive (Challenger).** A1.3 fixed diffusion + intensity
coverage, but `proxy_coverage` ("strong if total≥4 and covered≥2") and `covered` — which the
coverage gate and `record_from_serve` consult — still count instruments. Apply the venue-class
principle or document why not.

**F7 — Reconciliation floor not pinned (Challenger; Bernstein-rule hole).** The ±25%/±$20M
band is pre-declared but the per-fund MATERIALITY floor that selects which days get
direction-tested is not a number yet — a post-hoc floor choice could select the comparison
set. Pin it numerically before the first comparison runs.

**F8 — Ledger null precondition (Challenger, cross-cutting).** An 8%-threshold first-crossing
over 45 days on assets with 2–4% daily vol and positive drift has a high UNCONDITIONAL hit
probability favoring "inflow." Serve the per-coin unconditional first-crossing base rate
beside the confirm rate as a publication precondition — adopt now, while n=0.

**Also (Outsider):** disclose the IBIT concentration fact ("top fund = X% of class weight") —
correct weighting, but say it before a diligence team finds it. **(Guardian):** NAV-repeat
edge (shares move, NAV repeats to 1e-9 → stale share count) is a known artifact class for the
harness; `/diag` shows configured weight while the fold uses AUM share — §17 if ever user-facing.
**(Expansionist):** carry venue/currency fields on roster entries NOW (all "US"/"USD") and
build the harness adapter-per-issuer — cheap now, a rebuild later; per-venue strike calendars
+ FX-normalized floors the day a non-US ETP lands.

---

## THE C-ITEMS — CONDITIONS THAT MATTER

- **C2 (top display pick — 4 of 6 rank it #1–2):** §16-verify the FMP fields themselves
  (circulating + max supply, live sample); **uncapped coins render "no max supply
  (policy-changeable)" — never a fabricated FDV** (ETH has no cap; the NaN-class defect);
  one-line lost-coins caveat from the canon itself.
- **C1:** pre-declare crypto-native band edges in a spec file (the $10B/$2B equity edges make
  every top-12 coin "large" — no discriminating power); verify FMP circulating supply against
  a second reference (~5%) for a week; as-of date on the display; bands describe
  volatility/liquidity character, never quality.
- **C3:** the Challenger's decisive point — **Lewis's ETH mechanics are a decade stale**
  (post-merge PoS + EIP-1559 burn), so stamps must come from CURRENT authoritative docs, not
  the book; `as_of` + source citation per stamp; an owner + review trigger (protocol upgrade →
  re-verify); extend the cold-start commit gate: adding a coin requires stating its schedule.
- **C4 (3 seats converge on the rename):** the display is the product's best idea, but
  Burniske's "utility vs speculative value" is a valuation theory we do not compute — label
  the axes "attention heat" / "measured fund flow," cite the canon in methodology notes only;
  topic→coin mapping rule written down; §17 omission when either axis is unmeasured.
- **C7:** produce an ARTIFACT (file/line list of every crypto copy string checked,
  before/after); founder's verbatim disclaimer untouchable; run as a standing checklist line
  (improve-system attorney lens), not a one-time pass; "margin of safety" itself never in
  user copy.
- **C8:** hard-gate divergence display on flow being MEASURABLE (reuse `absence_class`) — on
  the 8 structurally-blind coins the mania signature fires as instrument blindness, exactly
  where it knows least; pre-register thresholds before first render; never "mania"/"bubble"
  in user copy — "attention-flow divergence"; own ledger before anything touches a score;
  build on ≥30 days of live flow, never the 4-day bridge history.
- **C5/C6 shelf triggers (Guardian + Challenger):** the trigger is necessary-but-not-
  sufficient — it must also demand denominator validation (exchange volume ≠ on-chain volume;
  L2s drain the L1 denominator) and full-coverage data for realized cap (no sampled
  approximation). Write the NO-PROXY prohibition into the shelf entry.

## DISAGREEMENTS

1. **C1/C2 readiness:** Expansionist/Outsider/Economist/Executioner = ship now (with n/a
   handling); Challenger demands a §16 field-verification week + crypto-native band edges
   first. (Narrow: both agree on the conditions, differ on whether they gate the deploy.)
2. **C4 vs C8 order:** Guardian & Challenger rank C4 as C8's precursor (ship display first);
   Executioner & Economist rank C8 above C4 in value but AFTER it in sequence (post-flip);
   Outsider ranks C8 4th, C4 5th (rename first). All agree: neither before the flip.
3. **Ranking #1 overall:** C7 first (Challenger, Executioner, Economist-2nd) vs C2 first
   (Expansionist, Outsider) vs C8-in-importance (Guardian, Economist). No seat ranked C3
   above the middle; every seat shelved C5/C6.

## CONSENSUS WORTH RECORDING

- A1's dark commit is sound and **survived six independent cold code reads** ("in fifteen
  years of diligence I have rarely seen a deck's engineering claims survive a direct code
  read this cleanly" — Outsider). The flip is blocked by: F1 (budget), F2 (pre-strike
  quiet), F3 (epoch), F5 (committed tests), the A1.5 harness, F7 (pinned floor). F4/F6/F8
  ride along as cheap same-change fixes.
- The canon was used to NAME disciplines the platform already had, not to import machinery —
  and the two places books could corrupt rather than confirm (C4's vocabulary; C5/C6's proxy
  temptation) are now fenced (Guardian's framing, echoed by 3 seats).
- The C1+C2(+C4 renamed) trio is "the fastest legibility-per-dollar this board has been
  offered this quarter" (Expansionist), pending the Challenger's field checks.

---

**Chairman — your decision per item:** A1 pre-flip fix list (F1–F8: which are mandatory vs
noted) · C1 (ship now vs after the field-verification week; band edges) · C2 (ship now with
n/a handling) · C3 (ship with owner+cadence, or hold) · C4 (rename + ship post-flip) · C5/C6
(shelf entries with no-proxy prohibitions) · C7 (ship first, artifact required) · C8 (design
with coverage gate + pre-registered thresholds, post-flip) · the Expansionist's
venue/currency schema ask · the Challenger's ledger-null publication precondition (F8).
