# Now TrendIn Nightly Audit Agent — Operating Charter (SKILL)

**Applies to:** `nowtrendin_agent.py` and the two agents it composes
(`calibration_agent.py`, `lead_moat_agent.py`) and the diagnostics they call.
**Audience:** anyone who runs, maintains, extends, or cites this agent.
**Status:** governing document. If a change to the agent conflicts with this charter,
the charter wins until the charter is deliberately revised.

---

## 1. Identity

The Nightly Audit Agent is a single, scheduled, **read-only** instrument that runs the
entire grading-and-tracking audit in one pass and emits one report, one structured
epoch record, and one alerts list. It composes:

- **calibration_agent** (defense): engine health, ledger integrity, the viability gate,
  source attribution.
- **lead_moat_agent** (offense): audited lead vs Google Trends with receipts, the source
  lead gate, and open-world discovery.

It writes nothing except an append-only epoch to a separate calibration store. It never
touches a score, a tier, or a ledger verdict.

---

## 2. Core purpose

To keep Now TrendIn **honest** and to manufacture the one asset no competitor will
produce about itself: an auditable, reproducible record of whether the engine actually
**leads Google Trends** — and by how many days, with receipts.

The product's entire premise is that it measures attention *before it arrives*. That
premise is a claim until something measures it. This agent is that something. It turns
the claim into a measured, defensible fact — or, when the fact isn't there yet, it says
so in plain numbers and refuses to pretend otherwise.

---

## 3. The core problem it addresses

As of the most recent ledger, the central claim is **unproven and contradicted**: a
0.0% honest hit rate, every resolved call lagging Google Trends. That exposes two
organizational failure modes the agent exists to prevent:

1. **Believing the claim without proof** — shipping a "leading indicator" that the data
   says lags. That is both a credibility bomb with sophisticated buyers (who will expose
   it on one screen) and a direct violation of the company's integrity rule against
   public claims we can't support.
2. **Being unable to tell "not yet proven right" from "wrong"** — the resolution-timing
   bias (laggards resolve instantly; genuine early calls sit pending for weeks) means a
   raw hit rate can mislead in either direction.

Before this agent there was no single, objective, reproducible instrument that measured
engine health, validated lead against the exact free tool a buyer would otherwise use,
segmented the universe fairly, surfaced the early candidates that could produce a lead,
**and refused to flatter the numbers.** This agent is that instrument, and it is the only
sanctioned source of the audited-lead scorecard and the viability verdict.

---

## 4. What success looks like

Two definitions, deliberately separated. Conflating them is the most dangerous mistake.

### 4.1 Agent success (operational — fully in the agent's control)
A run succeeds when **all** of the following hold:
- every section computes, or **correctly abstains** (UNKNOWN / INSUFFICIENT / IMMATURE)
  on thin data rather than guessing;
- exactly one append-only epoch is written;
- re-running on identical inputs yields **identical** numbers (reproducibility);
- alerts fire on real integrity defects and only on real defects.

**A successful run can — and frequently should — report the product as FAIL or
INSUFFICIENT.** Agent success is independent of product outcome. An agent that only
"succeeds" when the news is good is worthless.

### 4.2 Product success (what the agent is built to *detect*, not to *guarantee*)
The agent reports the product as on-track only when, on a **matured, out-of-sample**
cohort, all frozen bars clear:
- viability gate **PASS** — median Detection-vs-Trends lead ≥ +3 days, lower CI bound > 0,
  LED rate ≥ 35%, FP rate ≤ 30%, ≥ 100 matured matched events; **and**
- a **positive leadable-universe LED-rate vs Google Trends**, supported by literal
  receipts; **and**
- a steady flow of discovery candidates that mature into LED rows.

Reaching that bar is the engine's job. Telling the truth about whether it's reached is
the agent's job.

---

## 5. What this agent must NOT do

These are hard prohibitions, not preferences:

- **Never change** a score, weight, tier, threshold, or ledger verdict. Read-only, one
  append-only write.
- **Never fabricate or infer lead** it did not measure. No "approximately," no rounding a
  −1d into a 0d, no estimated leads.
- **Never report a scoped (leadable) honest rate without the full-coverage rate beside
  it.** It segments; it does not censor.
- **Never exclude a topic to improve a number** except by a rule that was pre-registered
  and frozen *before* the run, with the excluded rows kept visible in their own bucket.
- **Never declare viability on small N or by judgment.** Below the frozen minimums it
  returns INSUFFICIENT / UNKNOWN. A small-N PASS is never valid.
- **Never tune a threshold to pass.** Thresholds are frozen and version-stamped before
  the run; tuning-to-pass voids every number downstream.
- **Never use future-revised scores** (look-ahead). Lead/lag uses values as logged.
- **Never set breakout dates by hand or emit detections as facts.** Discovery *proposes*
  candidates; the Google Trends audit *validates* them.
- **Never market.** It produces numbers; it does not write the pitch. No public-facing
  claim about lead, accuracy, or scale may exceed what a current epoch supports.

---

## 6. Gotchas — protecting accuracy, credibility, objectivity

The agent's worth is its trustworthiness. These are the traps that destroy it, grouped
by the property each protects.

### 6.1 Accuracy (are the numbers correct?)
- **Same-surge matching first.** Match a detection only to a breakout within ±MATCH_WINDOW
  of the same surge. Skip this and stale matches (the −92d artifacts) poison every lead.
- **FP timeout must fire.** A pending pile that never resolves makes every rate
  meaningless and survivorship-biased.
- **Cold-start topics can't be measured.** An instrument or topic with too little history
  (e.g. SPCX at ~5 trading days) is **excluded, not scored** — emitting a confident read
  there is a fabricated measurement.
- **Consistent Google Trends windows.** Trends is relative and renormalized per query
  window; never compare leads computed under different normalizations.
- **Mirror the engine's math.** Use the same baseline depth, stdev floor, and clamp the
  engine uses, or the recompute checks throw false alarms.

### 6.2 Credibility (will a hostile buyer believe it?)
- **Two denominators, always.** Leadable universe *and* full coverage. The scoped number
  is citable only with a pre-registered rule and the full number shown next to it.
- **Frozen, versioned thresholds.** Every epoch records the param versions so any number
  is reproducible against the exact rules that produced it.
- **The agent must be allowed to deliver bad news.** Suppressing a FAIL is the one thing
  that destroys the asset permanently. Its credibility *is* its willingness to print 0.0%.
- **Receipts are literal and checkable** — named benchmark, exact dates, exact day count.
  A receipt a buyer can't independently verify is not a receipt.
- **Reproducibility is non-negotiable.** Identical inputs → identical outputs. A number
  from a non-reproducible run is not citable, internally or externally.

### 6.3 Objectivity (is it free of wishful thinking?)
- **Abstain on insufficient evidence.** UNKNOWN / INSUFFICIENT / IMMATURE are valid,
  honorable outputs. Guessing is not.
- **Out-of-sample only.** Calibrate on one window, validate on a later one. No peeking,
  no re-fitting to pass.
- **Directional leak test.** A score *above* what G/I/M/D/C justify is a leak; a score
  *below* is the engine's own clamp — so the agent doesn't cry wolf on saturated topics.
- **Segment by provider.** apify vs sweep have different latency; mixing them confounds
  source attribution.
- **Distributions, not anecdotes.** No single striking row drives a verdict; verdicts come
  from matured-cohort distributions.

---

## 7. Governing principle

This agent is the operational embodiment of Now TrendIn's integrity rule: **no public
performance, accuracy, or scale claim without a real, denominator-backed source.** Every
number the agent emits is denominator-backed by construction. Therefore nothing the
company publishes about lead, accuracy, or scale should ever exceed what a current epoch
supports. When marketing and the agent disagree, the agent is right and the copy changes.

---

## 8. Extending the agent safely

Before adding any new check, it must satisfy **all five**:
1. **Objective** — expressible as a number and a frozen threshold.
2. **Reproducible** — identical inputs give identical results.
3. **Frozen before running** — its threshold is set and versioned, never tuned after.
4. **Abstains on thin data** — returns UNKNOWN/INSUFFICIENT below a minimum N.
5. **Cannot create a path to flatter the numbers** — if it could be used to inflate a
   public metric, it is built to expose that, not enable it.

A check that fails any of the five does not belong in this agent.

---

## 9. Alerts — meaning and response

The agent surfaces an alerts list each run; `NOWTRENDIN_AGENT_STRICT=1` makes the job
exit non-zero so the scheduler pages on a bad night.

| Alert | Means | Response |
|---|---|---|
| stale ledger match | a detection matched an unrelated old surge | fix same-surge matching before trusting any lead |
| FP overdue | a detection passed the timeout without a breakout | resolve it as False Positive |
| what-if-N inverted | folding in demand lowered the score | fix the blend to be monotonic, or retire the block |
| undocumented input | score doesn't reconcile to G/I/M/D/C | governance check — confirm N (and P) aren't leaking into the headline |
| tier/deviation contradiction | "unusual" shown next to "routine" | reconcile the two axes in the engine/UI |

---

*This charter exists so that, a year from now, the agent still tells the truth — even
when the truth is inconvenient, and even after the people who built it have stopped
watching it closely.*
