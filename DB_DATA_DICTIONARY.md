# NowTrendIn DB — Data Dictionary

_Regenerated **2026-06-24** from the LIVE Postgres schema (`GET /schema`) + the Canonical Date Auditor (`GET /monitor/datecanon`). This is the source of truth — earlier versions were pre-migration (showed dropped columns like `market_signal_history.cycle_at` and mixed date formats the live schema no longer has). To refresh: re-fetch both endpoints and re-run `_audit_work/gen_dict.py`._

**32 app tables** (Postgres `pg_stat_statements*` extension tables excluded). Row counts are planner estimates (`reltuples`; `-1`/`?` = not yet analyzed). Engine: `nowtrendin-v2-engine`.

> **Canonical date model (§14):** every date-semantic value normalizes to a PRIMARY `signal_date` = ISO `YYYY-MM-DD`; secondary `source_time` (source's own HH:MM:SS) + `signal_time` (our fetch). Enforced by `ingestion_gate.gate_date()`. Live: **0 non-canonical across all declared date columns**.
> **Retention:** `velocity_scores` rows kept **365 days** (canonical, 2026-06-24); never deleted within the window.

---

## `accuracy_ledger`  (5 rows · 11 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `topic_key` | text |  |  |
| `topic_display` | text |  |  |
| `detection_date` | text |  | **canonical `signal_date` (ISO YYYY-MM-DD)** · datecanon: 0/36 non-canonical |
| `detection_score` | real |  |  |
| `breakout_date` | text |  | **canonical `signal_date` (ISO YYYY-MM-DD)** · datecanon: 0/36 non-canonical |
| `breakout_multiple` | real |  |  |
| `lead_time_days` | integer |  |  |
| `verdict` | text |  |  |
| `validated_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `provider` | text |  |  |

## `ai_costs`  (2,501 rows · 7 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `kind` | text |  |  |
| `topic` | text |  |  |
| `perplexity_cost` | real |  |  |
| `anthropic_cost` | real |  |  |
| `total_cost` | real |  |  |
| `created_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |

## `ai_grade_costs`  (15 rows · 6 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `topic` | text |  |  |
| `perplexity_cost` | real |  |  |
| `anthropic_cost` | real |  |  |
| `total_cost` | real |  |  |
| `created_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |

## `anomaly_log`  (530,230 rows · 10 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `flagged_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `topic_key` | text | NOT NULL |  |
| `topic_display` | text | NOT NULL |  |
| `overall_score` | real |  |  |
| `detection_score` | real |  |  |
| `confidence_score` | real |  |  |
| `anomaly_reason` | text |  |  |
| `was_confirmed` | integer |  |  |
| `confirmed_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |

## `api_usage`  (289 rows · 4 cols)

| column | type | null | notes |
|---|---|---|---|
| `source` | text | NOT NULL |  |
| `day` | text | NOT NULL |  |
| `calls` | integer |  |  |
| `last_call_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |

## `author_history`  (32,084 rows · 5 cols)

| column | type | null | notes |
|---|---|---|---|
| `author` | text | NOT NULL |  |
| `platform` | text | NOT NULL |  |
| `community` | text | NOT NULL |  |
| `first_seen_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `post_count` | integer |  |  |

## `blog_collection_log`  (3,370 rows · 7 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `collected_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `platform` | text | NOT NULL |  |
| `source_name` | text |  |  |
| `signals_collected` | integer |  |  |
| `topics_extracted` | integer |  |  |
| `error_message` | text |  |  |

## `calibration_epochs`  (? rows · 10 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `run_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `methodology_version` | text |  |  |
| `param_version` | text |  |  |
| `gate_status` | text |  |  |
| `gate_n` | integer |  |  |
| `gate_median_lead` | real |  |  |
| `led_rate` | real |  |  |
| `fp_rate` | real |  |  |
| `payload` | text |  |  |

## `catchall_floor_log`  (? rows · 7 cols)

| column | type | null | notes |
|---|---|---|---|
| `logged_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `total_scored` | integer |  |  |
| `catchall_count` | integer |  |  |
| `catchall_pct` | real |  |  |
| `single_source_leak` | integer |  |  |
| `misclassified_tracked` | integer |  |  |
| `min_sources` | integer |  |  |

## `collector_health`  (21 rows · 7 cols)

| column | type | null | notes |
|---|---|---|---|
| `collector` | text | NOT NULL |  |
| `last_success_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `last_run_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `last_signal_count` | integer |  |  |
| `consecutive_failures` | integer |  |  |
| `total_runs` | integer |  |  |
| `total_signals` | integer |  |  |

## `market_signal_history`  (87,771 rows · 6 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `item_key` | text |  |  |
| `component` | text |  |  |
| `value` | real |  |  |
| `signal_date` | text |  | **canonical `signal_date` (ISO YYYY-MM-DD)** · datecanon: 0/91166 non-canonical |
| `signal_time` | text |  | 24h-UTC time `HH:MM:SS` (§14 secondary) |

## `pending_detections`  (1,096 rows · 8 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `topic_key` | text |  |  |
| `topic_display` | text |  |  |
| `detection_date` | text |  | **canonical `signal_date` (ISO YYYY-MM-DD)** · datecanon: 0/1117 non-canonical |
| `detection_score` | real |  |  |
| `timeout_date` | text |  | canonical date (ISO YYYY-MM-DD) via `gate_date()` |
| `last_checked` | text |  |  |
| `status` | text |  |  |

## `positioning_history`  (37,588 rows · 5 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `item_key` | text |  |  |
| `stage` | integer |  |  |
| `signal_count` | integer |  |  |
| `cycle_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |

## `pull_history`  (252,217 rows · 11 cols)

| column | type | null | notes |
|---|---|---|---|
| `snapshot_date` | text | NOT NULL | **canonical `signal_date` (ISO YYYY-MM-DD)** · datecanon: 0/252217 non-canonical |
| `feed` | text | NOT NULL |  |
| `topic_key` | text | NOT NULL |  |
| `topic_display` | text |  |  |
| `detection_score` | real |  |  |
| `confidence_score` | real |  |  |
| `overall_score` | real |  |  |
| `signal_stage` | text |  |  |
| `total_signals` | integer |  |  |
| `scored_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `archived_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |

## `raw_signals`  (62,312 rows · 15 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `collected_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `platform` | text | NOT NULL |  |
| `platform_tier` | text | NOT NULL |  |
| `source_name` | text |  |  |
| `title` | text |  |  |
| `url` | text |  |  |
| `author` | text |  |  |
| `upvotes` | integer |  |  |
| `comments` | integer |  |  |
| `engagement_raw` | real |  |  |
| `sentiment` | real |  |  |
| `is_first_timer` | integer |  |  |
| `is_organic` | integer |  |  |
| `raw_text` | text |  |  |

## `research_history_cache`  (1 rows · 5 cols)

| column | type | null | notes |
|---|---|---|---|
| `topic_key` | text | NOT NULL |  |
| `researched_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `expires_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `result_json` | text | NOT NULL |  |
| `sources_found` | integer |  |  |

## `risk_scores`  (18,946 rows · 20 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `risk_topic` | text |  |  |
| `risk_display` | text |  |  |
| `detection_score` | real |  |  |
| `confidence_score` | real |  |  |
| `risk_stage` | text |  |  |
| `risk_action` | text |  |  |
| `interpretation` | text |  |  |
| `components` | text |  |  |
| `diffusion` | text |  |  |
| `total_signals` | integer |  |  |
| `scored_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `source_provenance` | text |  |  |
| `maturity` | text |  |  |
| `maturity_note` | text |  |  |
| `baseline_signals` | real |  |  |
| `baseline_cycles` | integer |  |  |
| `abnormality` | real |  |  |
| `baseline_status` | text |  |  |
| `positioning_json` | text |  |  |

## `risk_signals`  (2,284 rows · 11 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `risk_topic` | text |  |  |
| `risk_display` | text |  |  |
| `signal_type` | text |  |  |
| `source` | text |  |  |
| `diffusion_stage` | integer |  |  |
| `raw_signal` | text |  |  |
| `signal_date` | text |  | **canonical `signal_date` (ISO YYYY-MM-DD)** · datecanon: 0/2368 non-canonical |
| `collected_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `signal_time` | text |  | 24h-UTC time `HH:MM:SS` (§14 secondary) |
| `source_time` | text |  | 24h-UTC time `HH:MM:SS` (§14 secondary) |

## `score_archive`  (1,050 rows · 9 cols)

| column | type | null | notes |
|---|---|---|---|
| `snapshot_date` | text | NOT NULL | **canonical `signal_date` (ISO YYYY-MM-DD)** · datecanon: 0/1050 non-canonical |
| `topic_key` | text | NOT NULL |  |
| `topic_display` | text |  |  |
| `detection_score` | real |  |  |
| `confidence_score` | real |  |  |
| `overall_score` | real |  |  |
| `signal_stage` | text |  |  |
| `scored_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `total_mentions` | integer |  |  |

## `themes_blocklist`  (? rows · 3 cols)

| column | type | null | notes |
|---|---|---|---|
| `theme_key` | text | NOT NULL |  |
| `reason` | text |  |  |
| `blocked_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |

## `themes_extension`  (? rows · 10 cols)

| column | type | null | notes |
|---|---|---|---|
| `theme_key` | text | NOT NULL |  |
| `label` | text | NOT NULL |  |
| `keywords` | text | NOT NULL |  |
| `sectors` | text | NOT NULL |  |
| `detection_score` | real |  |  |
| `source_signals` | integer |  |  |
| `stage` | text |  |  |
| `promoted_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `last_seen_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `confirmed_by_human` | integer |  |  |

## `topic_baselines`  (? rows · 7 cols)

| column | type | null | notes |
|---|---|---|---|
| `topic_key` | text | NOT NULL |  |
| `snapshot_date` | text | NOT NULL | **canonical `signal_date` (ISO YYYY-MM-DD)** · datecanon: 0/0 non-canonical |
| `avg_gradient` | real |  |  |
| `avg_overall` | real |  |  |
| `avg_detection` | real |  |  |
| `avg_confidence` | real |  |  |
| `signal_count` | integer |  |  |

## `topic_lifecycle`  (39,349 rows · 16 cols)

| column | type | null | notes |
|---|---|---|---|
| `topic_key` | text | NOT NULL |  |
| `first_detected_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `last_scored_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `total_scoring_cycles` | integer |  |  |
| `cycles_above_emerging` | integer |  |  |
| `cycles_above_strong` | integer |  |  |
| `cycles_above_breakout` | integer |  |  |
| `peak_overall_score` | real |  |  |
| `peak_detection_score` | real |  |  |
| `peak_confidence_score` | real |  |  |
| `current_streak_cycles` | integer |  |  |
| `longest_streak_cycles` | integer |  |  |
| `persistence_rate` | real |  |  |
| `trend_age_hours` | real |  |  |
| `confirmed_trend` | integer |  |  |
| `updated_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |

## `topic_maturity`  (48 rows · 18 cols)

| column | type | null | notes |
|---|---|---|---|
| `topic_key` | text | NOT NULL |  |
| `topic_display` | text |  |  |
| `first_detected_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `last_scored_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `times_scored` | integer |  |  |
| `days_in_system` | integer |  |  |
| `maturity_class` | text |  |  |
| `maturity_reason` | text |  |  |
| `baseline_gradient` | real |  |  |
| `baseline_overall` | real |  |  |
| `baseline_detection` | real |  |  |
| `baseline_confidence` | real |  |  |
| `gradient_velocity` | real |  |  |
| `score_velocity` | real |  |  |
| `velocity_trend` | text |  |  |
| `calibration_multiplier` | real |  |  |
| `anomaly_gate_passed` | integer |  |  |
| `updated_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |

## `topic_queries`  (178,505 rows · 4 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | integer | NOT NULL |  |
| `queried_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `topic_key` | text | NOT NULL |  |
| `endpoint` | text | NOT NULL |  |

## `topic_registry`  (39,349 rows · 13 cols)

| column | type | null | notes |
|---|---|---|---|
| `topic_key` | text | NOT NULL |  |
| `topic_display` | text | NOT NULL |  |
| `first_seen_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `first_seen_platform` | text |  |  |
| `last_seen_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `total_mentions` | integer |  |  |
| `niche_mentions` | integer |  |  |
| `mainstream_mentions` | integer |  |  |
| `platforms_seen` | text |  |  |
| `current_stage` | text |  |  |
| `is_anomaly` | integer |  |  |
| `created_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `updated_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |

## `topic_score_history`  (? rows · 12 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `topic_key` | text | NOT NULL |  |
| `scored_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `overall_score` | real |  |  |
| `detection_score` | real |  |  |
| `confidence_score` | real |  |  |
| `gradient_raw` | real |  |  |
| `gradient_cal` | real |  |  |
| `inertia_score` | real |  |  |
| `platform_count` | integer |  |  |
| `total_mentions` | integer |  |  |
| `maturity_at_time` | text |  |  |

## `topic_signals`  (425,284 rows · 13 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `extracted_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `topic` | text | NOT NULL |  |
| `topic_key` | text | NOT NULL |  |
| `signal_id` | text |  |  |
| `platform` | text | NOT NULL |  |
| `platform_tier` | text | NOT NULL |  |
| `source_name` | text |  |  |
| `upvotes` | integer |  |  |
| `comments` | integer |  |  |
| `engagement_raw` | real |  |  |
| `is_first_timer` | integer |  |  |
| `is_organic` | integer |  |  |

## `velocity_scores`  (1,237,546 rows · 37 cols)

| column | type | null | notes |
|---|---|---|---|
| `id` | text | NOT NULL |  |
| `scored_at` | text | NOT NULL | ISO datetime (operational instant via `to_iso_dt`) |
| `topic_key` | text | NOT NULL |  |
| `topic_display` | text | NOT NULL |  |
| `gradient_strength` | real |  |  |
| `inertia_score` | real |  |  |
| `platform_diversity` | real |  |  |
| `dark_matter_score` | real |  |  |
| `confidence_decay` | real |  |  |
| `persistence_score` | real |  |  |
| `nowtrendin_score` | real |  |  |
| `overall_score` | real |  |  |
| `detection_score` | real |  |  |
| `confidence_score` | real |  |  |
| `heisenberg_gap` | real |  |  |
| `total_mentions` | integer |  |  |
| `niche_mentions` | integer |  |  |
| `mainstream_mentions` | integer |  |  |
| `platforms_active` | text |  |  |
| `first_timer_ratio` | real |  |  |
| `engagement_asymmetry` | integer |  |  |
| `gradient_ratio` | real |  |  |
| `signal_stage` | text |  |  |
| `is_gravitational_anomaly` | integer |  |  |
| `anomaly_reason` | text |  |  |
| `why_this_matters` | text |  |  |
| `what_to_watch` | text |  |  |
| `created_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |
| `serve_payload` | text |  |  |
| `attention_magnitude` | real |  |  |
| `n_mainstream_platforms` | integer |  |  |
| `detection_pathway` | text |  |  |
| `mainstream_ratio` | real |  |  |
| `mainstream_breadth` | real |  |  |
| `news_outlets` | integer |  |  |
| `mainstream_confirmed` | integer |  |  |
| `tier_migration` | integer |  |  |

## `worker_heartbeat`  (2 rows · 2 cols)

| column | type | null | notes |
|---|---|---|---|
| `role` | text | NOT NULL |  |
| `beat_at` | text |  | ISO datetime (operational instant via `to_iso_dt`) |

## `x_post_usage`  (1 rows · 2 cols)

| column | type | null | notes |
|---|---|---|---|
| `month` | text | NOT NULL |  |
| `posts` | integer |  |  |

## `x_pull_usage`  (1 rows · 2 cols)

| column | type | null | notes |
|---|---|---|---|
| `day` | text | NOT NULL |  |
| `pulls` | integer |  |  |

---

## Canonical date columns (datecanon-verified)

| column | rows | non-canonical |
|---|---|---|
| `accuracy_ledger.breakout_date` | 36 | 0 |
| `accuracy_ledger.detection_date` | 36 | 0 |
| `market_signal_history.signal_date` | 91166 | 0 |
| `pending_detections.detection_date` | 1117 | 0 |
| `pull_history.snapshot_date` | 252217 | 0 |
| `risk_signals.signal_date` | 2368 | 0 |
| `score_archive.snapshot_date` | 1050 | 0 |
| `topic_baselines.snapshot_date` | 0 | 0 |

