# Do we need OpenBB in Now TrendIn 2.0?

**Engineering assessment — 2026-07-28**
Reviewed: `notes on claude .doc`, `nowtrendin v 2 to do.docx`, `BOARD MEMBER claude project.docx`,
`Project container format.docx`, plus master `CLAUDE.md`, engine `CLAUDE.md`, `SESSION_LOG.md`,
`MARKET_SIGNAL_V2.md`, `SECURITY.md`, `ACCURACY_LOG.md`, and the OpenBB Open Data Platform release.

---

## CHAIRMAN'S RULING — 2026-07-28 (BINDING)

**The Chairman has decided that Now TrendIn will not use the OpenBB source code, or any version,
fork, derivative, or repackaging of it, for internal, external, or commercial purposes.**

This is a total exclusion. It covers the production engine, the local research machine, backtest
notebooks, the A5 null model, and any future evaluation. No OpenBB code is to be installed,
imported, linked, vendored, or referenced in any Now TrendIn repository or environment. The AGPLv3
question is therefore closed — not resolved in our favor, but rendered moot by declining the
dependency entirely.

This ruling supersedes the narrow "DO use it locally" recommendation in §7 below, which is retained
only as a record of what was considered and rejected.

**Standing rule for all agents and future sessions:** OpenBB is on the same footing as Reddit,
Guardian, CoinGecko and Messari in engine `CLAUDE.md` line 74 — excluded pending written Chairman
reversal. Any proposal to introduce it must go to the Chairman, not be decided at the working level.

---

**Analyst's verdict, as submitted (superseded in part by the ruling above):** DO NOT wire OpenBB
into the production application. DO install it locally as a research and validation tool.

---

## 1. What the four documents actually establish

Three of the four are the same document at different stages of editing. `nowtrendin v 2 to do.docx`,
`BOARD MEMBER claude project.docx`, and `Project container format.docx` all carry the identical
8-step project-container framework: get clear on the project, build a virtual board of directors,
turn the board into a skill, build a command center, move off the local drive, make the platform
AI-discoverable, create a "continuously improve" audit skill under a knowledge/skills/projects
structure, and top it with a project-manager `CLAUDE.md`. `Project container format.docx` applies
that framework to a **grip-sock business for active seniors**, not to Now TrendIn — it is filed in
the wrong folder for this question.

`notes on claude .doc` is the substantive one. It contains the complete `advisory-board` skill,
verbatim, with all six archetype prompts (Challenger, First-Principles Guardian, Expansionist,
Outsider VC/Banker, Executioner, Economist) and the non-negotiable mechanics: each archetype runs as
its own agent, no archetype sees another's output, same evidence pack for all, and the synthesis is
"a COLLATION, not a blend." The Chairman decides; the board never ships anything on its own word.

The engineering point that matters for the OpenBB question: **none of these four documents contain a
single data-agent specification.** They describe the governance layer — who reviews decisions and
under what values. They do not describe the collection layer. So the agent inventory below is drawn
from `CLAUDE.md` and `SESSION_LOG.md`, not from these four files.

---

## 2. What the app does, stated plainly

Now TrendIn measures **attention before price**. The product is the Gradient Score, a product of
seven components (G·I·M·D·C·P·N) rolled into two published readings:

```
Detection  = G·0.40 + D·0.25 + I·0.20 + M·0.10 + C·0.05    → earliness / momentum
Confidence = I·0.35 + M·0.30 + G·0.20 + C·0.10 + D·0.05    → position / conviction
```

Three coordinated layers sit on top: Attention (the Gradient), Risk/Other (per-company positioning),
and Trend Beneficiary (EARLY/MID/LATE/REALIZED). Three separate held-out accuracy ledgers grade the
system against reality: attention against Google Trends breakouts, equities against realized EOD
price direction, crypto against coin price direction.

The defensible asset is not the math. It is the **accuracy ledger** — 365 days of held-out,
never-deleted predictions graded against outcomes. `CLAUDE.md` calls it "the irreproducible moat,"
and that is correct: anyone can copy a formula, nobody can copy a year of timestamped calls.

This framing decides the OpenBB question by itself. A firm whose moat is *early attention on
non-financial surfaces* does not gain moat by adding a router to the same financial endpoints
everyone else already uses.

---

## 3. Current agent inventory

**Incomplete — flagged.** Master `CLAUDE.md` line 326 states: *"Full specs: `AGENT_CHARTER.md`
(Agents 1–16) + `DATA_BUILDING_BLOCKS.md`."* Neither file has been provided to me. What follows is
reconstructed from `CLAUDE.md` §13–14 and `SESSION_LOG.md`, and covers the agents by name and
function but not their full charters. Send those two files and I will complete this section.

### Tier 1 — Monitoring agents (`monitoring_agents.py` → `/monitor run_all`)

| # | Agent | What it watches |
|---|---|---|
| 1 | Source Watchdog | Per-source liveness and signal volume |
| 2 | Scorer Watchdog | Scoring runs completing, scores in range |
| 3 | Pipeline Integrity | Collect → score → serve chain intact |
| 4 | Topic Quality Auditor | Topic hygiene, junk/duplicate suppression |
| 5 | Catch-All Auditor (daily EOD) | Corroboration floor `CATCHALL_MIN_SOURCES` = 2 |
| 6 | Cost Sentinel | Spend against the $700/mo cap (live: $542) |
| 7 | Data Subscriptions | Paid-key validity and entitlement |
| 8 | Calibration Auditor | Score distribution drift vs `calib-params-v2-patience365` |
| 9 | Canonical Date Auditor (B3a) | `/monitor/datecanon` — date-format quarantine |

Plus `flow_integrity`, which reports `not_started` rather than `ok` on an empty room — the correct
design, and the one that would have surfaced the Finviz failure faster.

### Tier 2 — Operational agents

**Prewarm Agent** — read-only, API-process `/prewarm`, pull-synchronized, fires
`PREWARM_AFTER_PULL_S` = 60s after every data pull.
**Frontend Consistency Agent** — `/frontend-consistency`, UI/score agreement.

### Tier 3 — Governance archetypes (from `notes on claude .doc`)

Challenger, First-Principles Guardian, Expansionist, Outsider VC/Banker, Executioner, Economist.
These review proposals. They consume no market data feeds.

### The ground rules every agent inherits

Accuracy above all — a number we can't defend is worse than no number. Reproducibility. No
fabricated data. **No circular metrics: N never feeds or validates the Gradient Score.** No score
inflation. Reputable/licensed sources only. Measurement, not advice. Flag-never-force. The accuracy
ledger is held out and never deleted.

That last cluster is the real filter on any new data dependency, and OpenBB has to pass it.

---

## 4. Data already obtained independently, without OpenBB

**Attention side — the Dark Matter thesis.** GitHub, Hacker News (Algolia), DEV.to and technical
blogs, X (movers only, budget-capped), NewsAPI.org, NewsAPI.ai, NewsData.io, YouTube, GDELT, Google
Trends via Apify, five retail creator channels, twenty-two broadcast outlets.

**Money side.** SEC EDGAR, Finnhub, FRED, FINRA short interest, OFR STFM, WhaleWisdom 13F, Alpha
Vantage (production + research keys), **Finviz Elite** ($30/mo — primary insider and equity market
data), **Databento** (metered — price truth and microstructure), **FMP** ($20 Starter),
**QuiverQuant** ($30 — congressional trades), Yahoo Finance via RapidAPI, Nasdaq trade-halt RSS.

**Enrichment.** Perplexity and Anthropic for AI Grade.

Total: **$542/mo against a $700 cap.** Reddit, Guardian, CoinGecko and Messari are banned pending
written commercial approval (engine `CLAUDE.md` line 74) — the Guardian conflict flagged as A1 in
the prior audit is still open and is a licensing question, not a documentation question.

---

## 5. What OpenBB is, precisely

OpenBB is a **schema router**, not a data source. It normalizes responses from providers you already
pay for into a common Python/REST interface. Its own positioning is "connect once, consume
everywhere." The Open Data Platform release ships the Python SDK, a desktop app, a local REST
server, an Excel add-in, MCP servers, and Jupyter integration.

Its provider roster: FMP, Polygon, SEC EDGAR, Yahoo Finance, FRED, Databento, IMF, BLS, Congress,
FOMC.

Overlay that on §4. **You already hold direct keys for FMP, SEC EDGAR, Yahoo Finance, FRED, and
Databento.** Polygon, IMF, BLS, FOMC and Congress data are either redundant with Alpha Vantage /
QuiverQuant or freely available direct. OpenBB brings **zero new data** to this stack. It brings a
different way to call data you already have.

And it brings none of what actually differentiates you: no GitHub, no Hacker News, no DEV.to, no
Apify Google Trends, no broadcast set, no YouTube creator tier, no Finviz Elite insider, no
WhaleWisdom 13F, no OFR STFM, no FINRA short interest.

---

## 6. Why DO NOT — four grounds

**Ground 1: near-total provider overlap, zero marginal signal.** Every OpenBB provider that matters
to you is already wired direct. A router that sits between you and a key you already own adds
latency, a failure mode, and a version-compatibility surface, in exchange for tidier function
signatures.

**Ground 2: it supplies none of the moat.** The Gradient's G component — the 0.40-weighted term in
Detection — is fed by developer and community surfaces OpenBB does not touch. Adding OpenBB to a
system whose edge is non-financial attention is optimizing the part that isn't the product.

**Ground 3: AGPLv3 against paid tiers is a live legal exposure.** OpenBB's own statement: *"Anyone
who modifies the OpenBB Platform code and distributes it in applications or hosts it for SaaS needs
a commercial license unless they provide the source code."* Now TrendIn is a hosted service with
$49 / $499 / $250,000 tiers. Embedding AGPL-licensed code in the served Heroku engine puts you in
exactly the fact pattern that sentence describes. I am not giving you a legal conclusion on where
the linking boundary falls — that is counsel's call, and it turns on facts about your build you know
better than I do. I am telling you the exposure is real enough that it should not be resolved by a
`pip install`. This also runs straight into `SECURITY.md` §3, which gates any new party's access to
Now TrendIn data behind three-factor human approval.

**Ground 4: you cannot afford another silent dependency.** `MARKET_SIGNAL_V2.md` records the Finviz
insider parser dead for up to a month — 2026-06-25 to 2026-07-25 — with onset **unknowable because
no raw snapshots were retained**. That window swallowed the entire life of the equity money ledger:
the 12 resolved rows, the 50% blended rate, the 6/6 inflow lane, the 0/5 outflow lane. Every
published money number sits inside it. The engineering lesson is that an abstraction layer between
you and a provider is exactly where a silent failure hides. Putting a general-purpose router in
front of ten collectors, one month after a parser failure cost you a ledger, is the wrong direction.

The system already has nine watchdogs precisely because it has learned this. Adding a dependency
those nine agents were not written to monitor means writing a tenth.

---

## 7. Where OpenBB IS worth using — ~~narrow, internal, off the served path~~ REJECTED BY RULING

> **This section is superseded.** The Chairman's ruling of 2026-07-28 excludes OpenBB from internal
> use as well as external and commercial use. The two applications below were considered and are
> **not** to be implemented with OpenBB. The underlying needs remain valid and must be met another
> way — see §8 and the replacement note at the end of this section.

Install it on the local research machine, never on Heroku. Two concrete uses:

**A5 null model.** The prior audit's open item A5: the 365-day lead window means any topic that
eventually trends within a year scores as a hit, and the published rate has no baseline to beat. You
need the same 365-day rule applied to a matched set of topics that were *not* detected. OpenBB's
normalized FRED/BLS/IMF macro pulls are a fast way to assemble that control universe **offline**.
Nothing is served, nothing is conveyed, the AGPL network question never arises.

**Backtest scaffolding.** Ad-hoc historical pulls for research notebooks, where uniform schema
genuinely saves time and where a broken call fails in front of a human instead of silently in a
worker dyno.

Rule to hold: **OpenBB may inform research. It may never feed a score.** That is the same
classification your team already gave Databento — "referee, never feeds a score → no backtest gate."
It is the right precedent and it applies cleanly here.

**Replacement path under the ruling.** Both needs are met without OpenBB. The A5 null-model control
universe can be assembled from the FRED, BLS and IMF public endpoints called directly — these are US
government and multilateral data sources, freely redistributable, and the project already holds a
working FRED integration. Backtest scaffolding is served by the existing direct keys (Databento,
FMP, Alpha Vantage, SEC EDGAR) plus the project's own `hist_store.py` bitemporal reader, which gives
stronger point-in-time guarantees than a schema router does. Nothing in §7 required OpenBB
specifically; it was a convenience, and the convenience is declined.

---

## 8. What to do instead of OpenBB

If the underlying want is "our data plumbing is fragile," the fix is internal, not external:

1. **Bitemporal store for market inputs.** `hist_store.py` from the N Market Score prototype —
   `event_date` + `knowable_at`, reads only through `as_of(t)`, mutation blocked by DB triggers —
   makes "onset unknowable" structurally impossible. Had it been in place, the Finviz onset date
   would have been a query, not a guess.
2. **OpenFIGI validation gate.** Free, MIT-licensed, no commercial restriction. A ticker-validation
   tripwire would have caught the `LEVI` → `LLEVI` parser failure on its first cycle. Referee only.
3. **A tenth monitoring agent: Parser Integrity.** `flow_integrity`'s `not_started`-over-`ok`
   discipline, applied per-parser rather than per-flow.

Those three cost nothing in licensing, add nothing to the served path, and fix the actual failure
mode that has already cost you a month of data.

---

## Bottom line

OpenBB is a good piece of engineering solving a problem you do not have. You are not short of
financial endpoints — you hold direct keys to nearly everything it routes. You are short of
**verified integrity on the collectors you already run**. Buy that, not a router.

**DECIDED — Chairman's ruling, 2026-07-28:** Now TrendIn will **not** use the OpenBB source code, or
any version, fork, or derivative of it, for internal, external, or commercial purposes. The
exclusion is total and covers the production engine, local research, and backtesting alike. The A5
null model and backtest scaffolding will be built on direct FRED/BLS/IMF calls and the existing
`hist_store.py` bitemporal reader instead.

---

### Open gap in this analysis

`AGENT_CHARTER.md` (Agents 1–16) and `DATA_BUILDING_BLOCKS.md` were not provided. §3 above names the
agents and their functions from `CLAUDE.md` and `SESSION_LOG.md`, but I have not read their full
charters and cannot claim the inventory is complete. Send those two files and I will finish it. The
OpenBB verdict does not depend on them — it rests on provider overlap, licensing, and the served
path — but the agent section does.
