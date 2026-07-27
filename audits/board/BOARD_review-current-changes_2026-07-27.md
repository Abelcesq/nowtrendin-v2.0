# ADVISORY BOARD — REVIEW OF THE CURRENT CHANGES (post-remediation execution)
**Convened:** 2026-07-27 by the Chairman · **Five archetypes, independent, no cross-visibility**
**Scope:** commits `e9120b9`→`3ca1bda` + config v288 + the live prereg lock (engine v289).
The summary given to the Board was the object under audit; every archetype verified against
code and the live engine.

---

## 1. THE VERDICT (unanimous in structure)

**The chassis is good and the pack's claims survived contact** — the crypto gate, guard, and
C2b are live-verified; the firewall is clean (11 modules, 0 violations); the prereg was
committed 2026-07-27T04:16:42Z and locked 04:19:13Z (**committed-before-locked verified to
the minute**); person-data is clean end-to-end (names written in one place, SELECTed nowhere);
the contamination statement *"survives counsel"* (Outsider). The four accountability
corrections to the calibration were *"genuinely implemented"* (Economist).

**But the chain must NOT fire the last flag yet.** The never-reviewed `flow_enrollment.py`
repeats two defect classes this Board already named — and one defect would permanently
corrupt row 1 in a never-delete ledger.

> **Executioner:** *"Not ready to fire. F1 writes permanently defective treated rows into a
> never-delete ledger on day one; F2 leaves the cohort's defining threshold outside the lock
> it claims to live in. Both are hour-scale fixes. Parser flip and INSIDER_FLOW can proceed
> on their gates; FLOW_ENROLL waits — and nothing else needs to."*

## 2. BLOCKING — fix before `FLOW_ENROLL` (converged 4-5 of 5)

| # | Defect | Found by |
|---|---|---|
| **B1** | **Treated rows would enroll with NO sector and NO size band.** `run_cycle` reads `prof.get("match_facets")` — a key `_instrument_profile` never returns — so treated `sector` is always None and `size_decile` is hardcoded None, while controls carry both. The stratified analysis' strata would be missing on every treated row, permanently (never-delete). The self-test missed it because it builds the treated dict BY HAND instead of through `run_cycle`. | Executioner (F1), Challenger (F7), Guardian |
| **B2** | **The locked `enroll_threshold` is decorative.** `qualify_clusters` gates on env `FLOW_QUALIFY_MIN_BUYERS`; `run_cycle` never reads `pre["enroll_threshold"]`; `enroll()` never validates it; the `below_threshold` reject counter is initialized and incremented NOWHERE. Set the env to 2 and breadth-2 rows enroll under a registration that says 3, with a valid SHA and no cohort break. **The exact D2 class, one level up, in the module built after D2 was named.** | ALL FIVE |
| **B3** | **"10 trading days" locked; 10 CALENDAR days coded** (~7 trading days — a ~30% tighter window than registered). | Challenger (F2) |
| **B4** | **`ingest()` does not refuse when the salt is unset** — writes `actor_hash NULL`; mixed salt eras make `COUNT(DISTINCT COALESCE(actor_hash, role_raw))` overcount (one person = hash + role string = two "buyers"), and two real buyers + one fracture can fabricate the 3-buyer trigger itself. Salt is set today and the panel is empty — no damage yet — but the refusal must be code, like the parser-fix refusal beside it. Salt rotation = declared cohort break. | Challenger (F3), Guardian |
| **B5** | **Pre-arrival at enrollment uses env mult, not the prereg's** — `_instrument_profile` calls `already_arrived_before` with no `mult`. Coincidentally 3.0 today; D2 again. | Challenger (F8), Economist |
| **B6** | **Facet integrity:** screener "Volume" is TODAY'S volume, not ADV (a mid-spike treated name biases which controls pass the 0.2–5.0 band); `_adv_ok` returns True on missing data and then stamps `adv_matched: True` — *"the decorative-baseline pattern in miniature: the disclosure says matched, the code didn't match."* Tainted-set query lacks `<= asof` (lookahead in control selection on any backfill run) and one purchase taints where the registration excludes only *qualifying* clusters. | Executioner (F3), Challenger (F5/F6) |
| **B7** | **THE COSTLESS RE-LOCK** — one new registration before row 1 (zero-row superseded cohorts block nothing) folding in everything currently enforceable only by env/prose: the qualify window **in trading days**, the echo threshold (`FLOW_ECHO_SESSIONS` — a pre-registered FALSIFIER input currently outside the SHA), the persistence rule, the match-key spec (pretrend edges, ADV band, size bands), an **honest observable text** ("distinct open-market buyers, absolute breadth ≥3/10 trading days" — the locked "vs the name's own base rate" is not what the code computes; *"a registration whose prose flatters its code is a small lie in the one document whose entire value is that it cannot lie"*), and **min_episodes recomputed at the 90d null (25.2%), not the 60d null (19.6%)** — or 120 explicitly registered as a look point. | ALL FIVE, assembled |
| **B8** | **The stratified log-rank named PRIMARY in the lock exists NOWHERE in code.** The implemented gate (disjoint Greenwood bands) is the registered *secondary*. Commit the implementation, or at minimum the full spec (statistic, strata=match_group, censoring convention, two-sided α), before row 1 — *"writing the test statistic after the data accumulate is precisely the flexibility a prereg exists to foreclose."* | Economist |

## 3. BLOCKING — before `INSIDER_FLOW` (not before the flip)

- **B9 — The minimal liveness tripwire (Outsider):** the flip makes Finviz load-bearing again;
  *"reviving a source that died silently for 30 days with no alarm on the identical failure
  mode is not a risk I'd sign."* ~20 lines: distinct-ticker count from the market-wide feed
  below floor → RED. Full contract still post-thaw; the tripwire is not optional.
- **B10 — Hourly ingest tick** (ingest only; `run_cycle` stays 6h). The ~200-row cap vs the
  4–10pm ET burst: 4×200/day cannot cover heavy days, and heavy days are cluster days. The
  watermark then verifies within 48h instead of discovering.
- **B11 — `CRYPTO_LEDGER_CLEAN_COHORT_START` set to the ACTUAL flip date in the same
  `config:set` as the flip** (the 07-27 default is already stale; report-time computation
  makes late setting retroactively correct, but no read in between should be wrong).

## 4. SHOULD-FIX (same commits, not gating)

- Crypto `by_flow.inflow.confirm_rate_pct: 100.0` served live on n=1 (the dead-parser-era
  row) while the headline is withheld — *"that 100% will end up in a screenshot"*; withhold
  sub-rates and `median_lead_days` under the same floor. **And n=20 in code vs the n=30 the
  Outsider demanded — nobody argued it down; it silently shipped at 20.** Chairman to pick.
- Pretrend-None short-circuit in `build_controls` (today: up to 24 fetches ×10s sleeps for a
  predetermined refusal). Ops tuning before the flags: `FLOW_SWEEP_PAUSE_S=5`,
  `ENROLL_PER_CYCLE_MAX=3` (worst-case flow block 35–40 min → 13–15 min; the 6h cycle
  currently has ~20 min headroom against the 420-min risk-stale window).
- Ingest/sweep failure monitor within 48h of `INSIDER_FLOW` (nobody is paged today).
- Determinism disclosure: control selection is reproducible **given the screener snapshot**,
  which is live; persist the snapshot per cycle or say so.
- `CRYPTO_COVERAGE_GATE=0` post-flip = the silent-revival lever; Chairman-sign-off-only.

## 5. WHAT WAS VERIFIED GOOD (for the record)

- **Crypto, walked forward through the flip (Guardian):** BTC/ETH go numeric only when ≥2 of
  their OWN proxies vote; the ten COIN-only coins are structurally absent forever; no path to
  a single-proxy directional read through serve OR enrollment.
- **The calibration (Economist):** cluster bootstrap done right; hazard formula correct;
  pre-arrival conditioning now SYMMETRIC between null and ledger; the universe's filing-heavy
  tilt is the right reference for the enrolling population, with one pre-publication
  robustness re-run prescribed (screener-random universe). Disclosure owed: the 2.5×/3.0×
  CIs overlap — 3.0× is a pre-fixed convention, not measured superiority.
- **The prereg as a data-room artifact (Outsider):** *"Yes — this is the artifact I said no
  seed company shows you."* The LP story: *"not circling — a fundable PROCESS story... but it
  is all infrastructure and no evidence, and infrastructure doesn't compound."* The one
  artifact that changes the answer in 30 days: a live `/flow/accuracy` with ~60–90 era-clean
  treated enrollments at 1:3 parity under the re-locked prereg.

## 6. ORDER OF EXECUTION (consensus)

1. Fix B1–B6 + should-fixes in one commit; self-tests must route the treated dict THROUGH
   `run_cycle` (the gap that hid B1).
2. **One costless re-lock (B7)** with every material term inside the SHA + the log-rank spec
   (B8) committed first.
3. B9 tripwire ships.
4. Flip fires on the monitor's gate (all |z|<1.5), WITH B11's cohort stamp, with capture.
5. `INSIDER_FLOW=1` + hourly ingest (B10) after ≥2 clean cycles; watch the watermark 48h.
6. `FLOW_ENROLL=1`. Success unchanged: `pending_treated ≥ 1, pending_control ≥ 3`, treated
   rows carrying sector + size.

---
*Five memos, faithful collation; the full texts remain in the session record. Nothing here
reopens the freeze — every blocking item is inside the enrollment chain the freeze exists
to serve.*
