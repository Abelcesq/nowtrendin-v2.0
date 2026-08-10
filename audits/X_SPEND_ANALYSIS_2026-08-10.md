# X (Twitter) API — value analysis + spend-reduction plan (2026-08-10)

Sources: the founder's Developer Console (cycle Jul 21–Aug 21: **$250.42 spent, 83.5%
of the $300 cycle cap, 12 days remaining; $147.77 prepaid balance; auto-recharge ON
$200-at-$10**; 30-day usage **35.98k requests / $350.53** — dominant lines per the
founder's Gemini read: **Trends ~985+/day**, Counts ~200–400/day), X's published
pay-per-use rates (~$0.010/request for Trends/Users/Counts, ~$0.005/post-read;
corroborated by the console's own average $350.53/35,980 ≈ $0.0097/req), live
`/x/budget` (3,480 posts MTD of the 4,800 cap), and a full code audit of the ONLY
X-calling module (`x_signal_module.py`).

## 1. Does X data actually make a difference to trends/scoring? (honest assessment)

**Footprint:** X touches at most ~2 deep-pulled topics/day (X_DAILY_PULL_CAP=2,
1 pull/scan × 2 scans/day) plus cached detail-page pulls — ~29 pulls MTD ≈ 60/mo,
against ~4,000 scored topics. Coverage of the scored universe: **well under 1%**.
**Contribution path:** deep pulls feed the D-leg (author gradient / dark matter) and
medium components for those few topics; the 12h volume scan only selects which
topics get pulls (it writes no score input itself).
**Ledger evidence:** no per-source LED attribution exists yet, but the 2026-07-07
feature-mining found D≈0 at first sighting for LED winners — the Dark-Matter class
(X included) has been LATE-confirmation, not the early edge. There is currently
**no evidence X drives detections the ledger rewards** — and no clean evidence it
doesn't. VERDICT: unproven contributor at low coverage. RECOMMENDED TEST (held-out,
cheap): tag ledger enrollments with "X-touched at/before detection" and compare
outcomes — the X-attribution audit. Until it shows lift, X spend is a discovery
option, not a proven input — size it accordingly.

## 2. Where the money actually goes (the corrected picture)

| Line | Volume | Est. cost | Whose it is |
|---|---|---|---|
| **Trends requests ~985/day** | ~29.5k/mo | **~$295/mo** | **NOT this engine.** `x_signal_module.py` is the only X caller in the codebase and contains ZERO trends-endpoint calls. This traffic comes from ANOTHER consumer of the same "joinmynet" app — same failure class as the June dual-process overrun. Candidates: the JoinMyNet product itself, a leftover schedule, or any AI tool/agent configured with the app's keys (note: X's MCP server exposes trends/news tools and bills the connected app). |
| Counts/recent ~200–400/day | 6–12k/mo | ~$30–60/mo charged (24h-dedup helps: our query strings carry no timestamps, so the two daily scans dedupe per topic) | Ours (the 12h scan's volume poll — assumed FREE under the old plan; now capped + metered) |
| Post reads (deep pulls) | ~3.5–4.8k posts/mo | ~$18–24/mo at $0.005/read | Ours (budget-capped at 4,800 posts) |

**NowTrendIn's true X cost ≈ $50–85/mo, falling to ≈ $30–50/mo after tonight's cap.
The other ~$295/mo is external to this engine.** The old $0.0413/post estimate was a
blended artifact of dividing total console spend by our posts — it silently charged
the external Trends traffic to our pulls.

## 3. On the founder's "2 pulls/day (12:01 AM / 6:01 PM)" intent

Verified in code: deep pulls ARE capped at 2/day (X_DAILY_PULL_CAP=2, 1 per scan);
scans run 2×/day at 00:00 and 12:00 UTC (X_SCAN_HOURS="0,12"). So the PULL intent is
enforced; the clock times differ from the founder's recollection (00:00/12:00 UTC ≈
8 PM / 8 AM ET). If 12:01 AM + 6:01 PM (ET) is the desired schedule, it is one env
change: `X_SCAN_HOURS` set to the matching UTC hours — say the word.

## 4. STEP-BY-STEP spend reduction

**Engine side — SHIPPED tonight (commit batch 2):**
1. ✅ Counts universe hard-capped: `X_SCAN_MAX_CANDIDATES=40` (was up to the full
   scan universe) → ≤80 counts-req/day, ~40 charged after dedup ≈ **~$12/mo**.
2. ✅ Every counts request now METERED (`x_request_usage`, surfaced in `/x/budget`
   and the Cost Sentinel) — the unmetered class can never be silent again.
3. ✅ Sentinel recalibrated: projection clamped to what the (verified-enforcing)
   4,800-post cap permits; new honest alarm = the mid-month COVERAGE GAP; warns
   until `X_COST_PER_REQUEST_USD` is calibrated.

**Founder console actions (in order, ~10 minutes):**
4. **Developer Portal → Usage:** open the per-endpoint breakdown and identify the
   Trends caller (~985/day). Check: any Grok Build / Cursor / xurl-MCP config using
   the joinmynet keys; any other product/schedule on this app. Kill or migrate it.
5. **Create a dedicated X app for NowTrendIn** (5 min) and move `X_BEARER_TOKEN` to
   it — from then on, the console's spend for that app IS NowTrendIn's spend,
   attributable and auditable (the vendor-diligence answer too).
6. **Billing → Manage Spend Cap:** lower the Billing Cycle Cap from $300 to ~$100
   for the NowTrendIn app (our true need is ≤$85 with headroom) — the hard stop on
   X's side.
7. **Auto Recharge:** reduce from $200 to $100 per top-up (keep ON so the cap, not
   an empty balance, is the limiter).
8. **Set the env rates once verified** on the engine:
   `heroku config:set X_COST_PER_REQUEST_USD=0.010 X_COST_PER_POST_USD=0.005 COST_X_API_USD=100 -a nowtrendin-v2-engine`
   (rates per X's published pay-per-use pricing; verify on the console pricing page
   when setting — the sentinel refuses to meter dollars until set).
9. **Optional deeper cuts (your call):** scans 2/day → 1/day (`X_SCAN_HOURS="0"`,
   halves counts + pull cadence); or suspend X entirely pending the attribution
   audit (§1) — at <1% topic coverage and no proven ledger lift, that is a
   defensible measurement-first position.

## 5. Expected outcome
After steps 4–7: NowTrendIn's X line ≈ **$30–50/mo, fully metered and attributable**
(vs the $200 configured line and the $350 blended console reality) — a ~$250–300/mo
account-level reduction once the external Trends consumer is stopped or separated.
