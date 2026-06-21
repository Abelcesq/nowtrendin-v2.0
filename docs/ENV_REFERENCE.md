# ENV_REFERENCE.md — NowTrendIn 2.0 Environment Variables

All required environment variable **names** for `nowtrendin-v2-engine` and
`nowtrendin-backend`. **Never commit actual values to this file or any tracked
file.** Values live only in Heroku Config Vars and in the local `.env` files
(which are gitignored).

Status legend:
- **SET** — confirmed set on Heroku as of 2026-06-20
- **MISSING** — referenced in code but not set on Heroku (causes silent data gap or error)
- **OPTIONAL** — referenced in code but has a safe default; set for production tuning
- **DEFERRED** — not needed until Stripe/push-notification work resumes

---

## Engine — `nowtrendin-v2-engine`

### Infrastructure
| Variable | Status | Description |
|---|---|---|
| `DATABASE_URL` | SET | Postgres connection string (Heroku Postgres add-on) |
| `PORT` | SET (auto) | HTTP port — set by Heroku automatically |
| `INTERNAL_API_KEY` | SET | Founder-only endpoint gating key |
| `ADMIN_API_KEY` | MISSING | Admin API gating key — endpoints may be ungated without this |

### AI / Grading
| Variable | Status | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | SET | Claude API key for AI grading (`/grade`) |
| `PERPLEXITY_API_KEY` | SET | Perplexity API key for AI grading research step |
| `FIRECRAWL_API_KEY` | SET ✅ | Firecrawl web search — Stage 0 pre-research in grade pipeline. Anchors Perplexity to real URLs. Set 2026-06-21 v74. |
| `AI_GRADE_CLAUDE_MODEL` | SET | Claude model for grading — must be `claude-sonnet-4-6` |
| `AI_GRADE_PPLX_MODEL` | OPTIONAL | Perplexity model for grading — defaults to `sonar` |
| `AI_MONTHLY_BUDGET_USD` | OPTIONAL | Monthly AI spend cap (default: no cap) |

### Social / Creator signals
| Variable | Status | Description |
|---|---|---|
| `X_BEARER_TOKEN` | SET | X (Twitter) API v2 bearer token — drives the demand scan |
| `YOUTUBE_API_KEY` | SET | YouTube Data API v3 — creator + broadcast channels |
| `REDDIT_CLIENT_ID` | **MISSING** | Reddit API OAuth client ID — Reddit signal not collected |
| `REDDIT_CLIENT_SECRET` | **MISSING** | Reddit API OAuth secret — Reddit signal not collected |
| `REDDIT_USER_AGENT` | **MISSING** | Reddit API user-agent string (e.g. `nowtrendin/1.0`) |
| `APIFY_TOKEN` | SET | Apify platform API token |
| `APIFY_REALTIME_ACTOR` | OPTIONAL | Override for realtime actor ID. Default `oOHXMAv8kImUCpHff` (`easyapi/google-realtime-trends-data-scraper`) is hardcoded in `gravitational_anomaly_detector.py:1811` — engine calls it successfully without this var. ~$0.57/run, every 6h. |
| `APIFY_TRENDS_ACTOR` | OPTIONAL | Override for trends validation actor ID. Default `apify~google-trends-scraper` is hardcoded in `google_trends_validation.py:161` — works without this var. |
| `MASTODON_INSTANCE` | **MISSING** | Mastodon instance URL (e.g. `mastodon.social`) — collector silently skips |

### News / Media signals
| Variable | Status | Description |
|---|---|---|
| `NEWSAPI_ORG_KEY` | SET | NewsAPI.org key — news headlines |
| `NEWSAPI_AI_KEY` | SET | NewsAPI.ai key — AI-indexed news |
| `NEWSDATA_IO_KEY` | SET | NewsData.io key — global news |
| `CURRENTS_API_KEY` | SET | Currents API key — news feeds |
| `CURRENTS_DAILY_CAP` | SET | Currents daily call cap (default: 900) |
| `GUARDIAN_API_KEY` | **MISSING** | The Guardian Open Platform key — mainstream media Stage 4 signal. **Without this, GDELT fallback is used; GDELT is rate-limited on Heroku IPs → mainstream media signal may be absent.** Register free at open-platform.theguardian.com/access (5,000 calls/day) |
| `DEVTO_API_KEY` | SET ✅ | Dev.to (Forem API v1) — developer blog Dark Matter signal. Set 2026-06-21 v71. |
| `HASHNODE_TOKEN` | SET | Hashnode API token — developer blog signal |
| `GITHUB_TOKEN` | SET | GitHub API token — trending repos signal |
| `BLOGGER_API_KEY` | SET | Google Blogger API key |

### Market / Financial signals
| Variable | Status | Description |
|---|---|---|
| `ALPHAVANTAGE_API_KEY` | SET | Alpha Vantage — news sentiment (article count + tone) |
| `FINNHUB_API_KEY` | SET | Finnhub — sustainability sub-scores (free tier: limited backfill) |
| `FMP_API_KEY` | SET ✅ | Financial Modeling Prep — income statement + profile → fundamental_confirmation component. Set 2026-06-21 v72. |
| `FINRA_API_KEY` | SET | FINRA short interest API key |
| `WHALEWISDOM_SHARED_KEY` | SET | WhaleWisdom 13F shared key |
| `WHALEWISDOM_SECRET_KEY` | SET | WhaleWisdom 13F secret key |
| `RAPIDAPI_YF_KEY` | SET | RapidAPI key for Yahoo Finance news |
| `FRED_API_KEY` | SET | FRED (Federal Reserve) economic data key |

### Search / Discovery
| Variable | Status | Description |
|---|---|---|
| `SERPAPI_KEY` | **MISSING** | SerpAPI key — used when `TRENDS_PROVIDER=serpapi`; also powers Google Trends fallback |
| `GOOGLE_TRENDS_API_KEY` | **MISSING** | Google Trends API key — only needed if `TRENDS_PROVIDER=google_trends` (not serpapi) |
| `GOOGLE_TRENDS_ENABLED` | OPTIONAL | Enable/disable Google Trends collection (default: true if key set) |

### Snowflake (future / enterprise data warehouse)
| Variable | Status | Description |
|---|---|---|
| `SNOWFLAKE_ACCOUNT` | MISSING | Snowflake account identifier — not yet in production use |
| `SNOWFLAKE_USER` | MISSING | Snowflake username |
| `SNOWFLAKE_PASSWORD` | MISSING | Snowflake password |
| `SNOWFLAKE_WAREHOUSE` | MISSING | Snowflake warehouse name |

### Pipeline tuning (have safe defaults — set only to override)
| Variable | Default | Description |
|---|---|---|
| `COLLECT_INTERVAL_MIN` | 360 | How often the collection cycle runs (minutes) |
| `SCORE_INTERVAL_MIN` | — | Scoring cycle interval |
| `SCORE_STALE_MIN` | — | Age at which a score is considered stale |
| `VELOCITY_RETENTION_DAYS` | 90 | How long velocity_scores rows are kept (**hard rule — do not change without explicit confirmation**) |
| `CATCHALL_MIN_SOURCES` | 2 | Min distinct sources for news/general topics to score |
| `X_MONTHLY_POST_BUDGET` | 12000 | Monthly X API post budget cap |
| `MAINSTREAM_NEWS_LIMIT` | — | Max mainstream news items per cycle |
| `DUAL_PATHWAY` | true | Enable dual-pathway calibration (fame vs diffusion) |

---

## Backend — `nowtrendin-backend`

### Infrastructure
| Variable | Status | Description |
|---|---|---|
| `SECRET_KEY` | SET ✅ | Django secret key — set 2026-06-20, Heroku release v39. |
| `DATABASE_URL` | SET | Postgres connection string (Heroku Postgres add-on) |
| `DEBUG` | SET | Django debug mode — must be `False` in production |
| `PORT` | SET (auto) | HTTP port — set by Heroku automatically |
| `WEB_CONCURRENCY` | OPTIONAL | Gunicorn worker count |
| `GRADIENT_API` | SET | v2 engine URL — must be `https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com` |
| `INTERNAL_API_KEY` | SET | Internal API gating key (must match engine's value) |

### Google OAuth
| Variable | Status | Description |
|---|---|---|
| `GOOGLE_IOS_CLIENT_ID` | SET | Google OAuth iOS client ID |
| `GOOGLE_WEB_CLIENT_ID` | SET | Google OAuth web client ID |
| `GOOGLE_ANDROID_CLIENT_ID` | **MISSING** | Google OAuth Android client ID — Android Google sign-in may fail |

### Email
| Variable | Status | Description |
|---|---|---|
| `EMAIL_HOST` | SET | SMTP host (smtp.gmail.com) |
| `EMAIL_HOST_USER` | SET | SMTP username / from address |
| `EMAIL_HOST_PASSWORD` | SET | SMTP app password |
| `EMAIL_PORT` | SET | SMTP port (587) |
| `EMAIL_USE_TLS` | SET | TLS enabled (True) |
| `DEFAULT_FROM_EMAIL` | MISSING | Default sender address — Django uses EMAIL_HOST_USER if not set |

### Push notifications (deferred)
| Variable | Status | Description |
|---|---|---|
| `TWILIO_ACCOUNT_SID` | DEFERRED | Twilio account SID — required when SMS/push alerts ship |
| `TWILIO_AUTH_TOKEN` | DEFERRED | Twilio auth token |
| `TWILIO_FROM_NUMBER` | DEFERRED | Twilio sender number |

---

## Action items (by priority)

**Resolved ✅**
- `SECRET_KEY` (backend) — Set 2026-06-20, Heroku v39.
- `AI_GRADE_CLAUDE_MODEL` — Updated 2026-06-20 to `claude-sonnet-4-6`.
- Apify actors — Running with hardcoded defaults (125 results, $0.574/run confirmed 2026-06-20).

**On hold (user deferred)**
- `GUARDIAN_API_KEY` — Register free at open-platform.theguardian.com/access when ready, then `heroku config:set GUARDIAN_API_KEY=<key> -a nowtrendin-v2-engine`. Restores Stage 4 mainstream media signal.
- `REDDIT_CLIENT_ID/SECRET/USER_AGENT` — Register at reddit.com/prefs/apps when ready.

**Deferred until app store publish (Google Play / App Store)**
- `GOOGLE_ANDROID_CLIENT_ID` — Not needed until Google Play submission. Retrieve from Google Cloud Console → OAuth credentials at that time.
- Stripe (`@stripe/stripe-react-native`) + push notifications (`expo-notifications`) — Require custom dev client off Expo Go. Do not touch until store submission.

**Still open (low priority)**
- _(none — all gaps resolved or deferred)_

---

_Last updated: 2026-06-21_
_See `transfer/.env.example` and `backend/.env.example` for local dev setup._
