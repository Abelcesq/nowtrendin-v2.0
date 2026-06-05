# Milestone 1 — 48-Hour Continuous Run

**Goal:** let the full source set collect + score continuously for 48 hours so the
engine accumulates inertia/persistence/baseline history on *complete* data, and
the Accuracy Ledger starts compounding on a full-spectrum signal.

**Started:** 2026-06-05 (worker dyno running `--mode=worker`, collect+score every 30 min)

---

## What's running
- **Engine worker dyno** (`nowtrendin`): collect+score every 30 min · velocity recompute 06:00 UTC · X velocity scan 1am/1pm PT · retention monthly.
- **Engine web dyno**: serves the app/API only (no background work).
- **Django backend**: web only; alerts webhook-triggered from the worker.

## Active sources (free-tier, defensible terms)
| Mode | Sources |
|---|---|
| Attention | GitHub, Hacker News, Reddit, YouTube, blogs (dev.to/Hashnode/etc.), X (dual-role), on-demand Guardian/GDELT (mainstream news) |
| Risk | SEC EDGAR (Form 4/8-K), **Finnhub** (insider Stage 1 + news Stage 4), FRED (macro), YouTube (retail), GDELT-risk |
| AI Grade | Perplexity (research) + Claude (synthesis) |

## Keys configured
FRED ✓ · YouTube ✓ · X Bearer ✓ · Finnhub ✓ · Apify ✓ (billing-capped until reset) ·
Anthropic ✓ · Perplexity ✓ · Guardian ✗ (pending commercial terms)

---

## ⚠️ Rule during the run
**Do not redeploy the engine.** Each deploy restarts the worker and resets its
30-min cycle timer. Leave it alone for 48 h so cycles run uninterrupted.

## Known gaps during this run
- **Accuracy Ledger** needs Apify (Google Trends) which is **billing-capped** —
  it will start populating once Apify resets (~Mon 06/08). Until then the ledger
  stays empty; everything else accumulates normally.
- **Finnhub spike**: watchlist names read `SPIKE_VS_SELF` immediately after
  Finnhub was added; the recent-12-cycle baseline re-centres them to
  `AT_BASELINE` within ~6 hours of uninterrupted cycles.

---

## Checkpoints
**At ~6 h:** risk watchlist `baseline_status` should move from SPIKE_VS_SELF →
AT_BASELINE (Finnhub now in baseline).

**At 24 h:** 
- `GET /scores` — attention topics should have `total_scoring_cycles` ~48 and
  inertia/persistence components activating (no more "first collection").
- `GET /risk/scores` — watchlist detection differentiated (not pegged), baselines settled.

**At 48 h:**
- Confirm continuous cycles in worker logs (no gaps).
- If Apify reset: `GET /accuracy/ledger` should show first validated lead-times.
- Review score stability + any collector errors in logs.

## Quick health commands
```
heroku ps -a nowtrendin                         # both dynos up
heroku logs -n 100 -a nowtrendin --dyno worker  # cycle activity
curl .../scores?sort_by=detection&limit=20      # attention feed
curl .../risk/scores                            # risk feed
curl .../accuracy/ledger                        # lead-time ledger (after Apify reset)
curl .../grade/costs                             # AI cost tally
```
