# NowTrendIn DB — Data Dictionary (auto-generated, read-only)

_32 tables. Format buckets shown for date-ish TEXT columns._


## accuracy_ledger  (13 rows, 11 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| topic_key | text | YES |  |
| topic_display | text | YES |  |
| detection_date | text | YES | iso_date:13 |
| detection_score | real | YES |  |
| breakout_date | text | YES | human:13 |
| breakout_multiple | real | YES |  |
| lead_time_days | integer | YES |  |
| verdict | text | YES |  |
| validated_at | text | YES | iso_dt:13 |
| provider | text | YES |  |

## ai_costs  (690 rows, 7 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| kind | text | YES |  |
| topic | text | YES |  |
| perplexity_cost | real | YES |  |
| anthropic_cost | real | YES |  |
| total_cost | real | YES |  |
| created_at | text | YES | iso_dt:690 |

## ai_grade_costs  (18 rows, 6 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| topic | text | YES |  |
| perplexity_cost | real | YES |  |
| anthropic_cost | real | YES |  |
| total_cost | real | YES |  |
| created_at | text | YES | iso_dt:18 |

## anomaly_log  (511356 rows, 10 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| flagged_at | text | NO | iso_dt:511356 |
| topic_key | text | NO |  |
| topic_display | text | NO |  |
| overall_score | real | YES |  |
| detection_score | real | YES |  |
| confidence_score | real | YES |  |
| anomaly_reason | text | YES |  |
| was_confirmed | integer | YES |  |
| confirmed_at | text | YES |  |

## api_usage  (250 rows, 4 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| source | text | NO |  |
| day | text | NO |  |
| calls | integer | YES |  |
| last_call_at | text | YES | iso_dt:250 |

## author_history  (28853 rows, 5 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| author | text | NO |  |
| platform | text | NO |  |
| community | text | NO |  |
| first_seen_at | text | YES | iso_dt:28853 |
| post_count | integer | YES |  |

## blog_collection_log  (3053 rows, 7 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| collected_at | text | YES | iso_dt:3053 |
| platform | text | NO |  |
| source_name | text | YES |  |
| signals_collected | integer | YES |  |
| topics_extracted | integer | YES |  |
| error_message | text | YES |  |

## calibration_epochs  (1 rows, 10 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| run_at | text | NO | iso_dt:1 |
| methodology_version | text | YES |  |
| param_version | text | YES |  |
| gate_status | text | YES |  |
| gate_n | integer | YES |  |
| gate_median_lead | real | YES |  |
| led_rate | real | YES |  |
| fp_rate | real | YES |  |
| payload | text | YES |  |

## collector_health  (21 rows, 7 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| collector | text | NO |  |
| last_success_at | text | YES | iso_dt:21 |
| last_run_at | text | YES | iso_dt:21 |
| last_signal_count | integer | YES |  |
| consecutive_failures | integer | YES |  |
| total_runs | integer | YES |  |
| total_signals | integer | YES |  |

## market_signal_history  (57930 rows, 5 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| item_key | text | YES |  |
| component | text | YES |  |
| value | real | YES |  |
| cycle_at | text | YES | iso_date:180, iso_dt:57750  ⚠MIXED |

## pending_detections  (1045 rows, 8 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| topic_key | text | YES |  |
| topic_display | text | YES |  |
| detection_date | text | YES | iso_date:1045 |
| detection_score | real | YES |  |
| timeout_date | text | YES | iso_dt:1045 |
| last_checked | text | YES | iso_dt:1045 |
| status | text | YES |  |

## pg_stat_statements_info  (1 rows, 2 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| dealloc | bigint | YES |  |
| stats_reset | timestamp with time zone | YES |  |

## positioning_history  (30780 rows, 5 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| item_key | text | YES |  |
| stage | integer | YES |  |
| signal_count | integer | YES |  |
| cycle_at | text | YES | iso_dt:30780 |

## pull_history  (190580 rows, 11 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| snapshot_date | text | NO | iso_date:190580 |
| feed | text | NO |  |
| topic_key | text | NO |  |
| topic_display | text | YES |  |
| detection_score | real | YES |  |
| confidence_score | real | YES |  |
| overall_score | real | YES |  |
| signal_stage | text | YES |  |
| total_signals | integer | YES |  |
| scored_at | text | YES | iso_dt:190580 |
| archived_at | text | YES | iso_dt:190580 |

## raw_signals  (64816 rows, 15 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| collected_at | text | NO | iso_dt:64816 |
| platform | text | NO |  |
| platform_tier | text | NO |  |
| source_name | text | YES |  |
| title | text | YES |  |
| url | text | YES |  |
| author | text | YES |  |
| upvotes | integer | YES |  |
| comments | integer | YES |  |
| engagement_raw | real | YES |  |
| sentiment | real | YES |  |
| is_first_timer | integer | YES |  |
| is_organic | integer | YES |  |
| raw_text | text | YES |  |

## research_history_cache  (16 rows, 5 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| topic_key | text | NO |  |
| researched_at | text | NO | iso_dt:16 |
| expires_at | text | NO | iso_dt:16 |
| result_json | text | NO |  |
| sources_found | integer | YES |  |

## risk_scores  (14716 rows, 20 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| risk_topic | text | YES |  |
| risk_display | text | YES |  |
| detection_score | real | YES |  |
| confidence_score | real | YES |  |
| risk_stage | text | YES |  |
| risk_action | text | YES |  |
| interpretation | text | YES |  |
| components | text | YES |  |
| diffusion | text | YES |  |
| total_signals | integer | YES |  |
| scored_at | text | YES | iso_dt:14716 |
| source_provenance | text | YES |  |
| maturity | text | YES |  |
| maturity_note | text | YES |  |
| baseline_signals | real | YES |  |
| baseline_cycles | integer | YES |  |
| abnormality | real | YES |  |
| baseline_status | text | YES |  |
| positioning_json | text | YES |  |

## risk_signals  (1947 rows, 9 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| risk_topic | text | YES |  |
| risk_display | text | YES |  |
| signal_type | text | YES |  |
| source | text | YES |  |
| diffusion_stage | integer | YES |  |
| raw_signal | text | YES |  |
| signal_date | text | YES | iso_date:1829, iso_dt:52, compactZ:66  ⚠MIXED |
| collected_at | text | YES | iso_dt:1947 |

## score_archive  (1050 rows, 9 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| snapshot_date | text | NO | iso_date:1050 |
| topic_key | text | NO |  |
| topic_display | text | YES |  |
| detection_score | real | YES |  |
| confidence_score | real | YES |  |
| overall_score | real | YES |  |
| signal_stage | text | YES |  |
| scored_at | text | YES | iso_dt:1050 |
| total_mentions | integer | YES |  |

## themes_blocklist  (0 rows, 3 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| theme_key | text | NO |  |
| reason | text | YES |  |
| blocked_at | text | NO |  |

## themes_extension  (0 rows, 10 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| theme_key | text | NO |  |
| label | text | NO |  |
| keywords | text | NO |  |
| sectors | text | NO |  |
| detection_score | real | YES |  |
| source_signals | integer | YES |  |
| stage | text | YES |  |
| promoted_at | text | NO |  |
| last_seen_at | text | YES |  |
| confirmed_by_human | integer | YES |  |

## topic_baselines  (0 rows, 7 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| topic_key | text | NO |  |
| snapshot_date | text | NO |  |
| avg_gradient | real | YES |  |
| avg_overall | real | YES |  |
| avg_detection | real | YES |  |
| avg_confidence | real | YES |  |
| signal_count | integer | YES |  |

## topic_lifecycle  (32137 rows, 16 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| topic_key | text | NO |  |
| first_detected_at | text | NO | iso_dt:32137 |
| last_scored_at | text | YES | iso_dt:32137 |
| total_scoring_cycles | integer | YES |  |
| cycles_above_emerging | integer | YES |  |
| cycles_above_strong | integer | YES |  |
| cycles_above_breakout | integer | YES |  |
| peak_overall_score | real | YES |  |
| peak_detection_score | real | YES |  |
| peak_confidence_score | real | YES |  |
| current_streak_cycles | integer | YES |  |
| longest_streak_cycles | integer | YES |  |
| persistence_rate | real | YES |  |
| trend_age_hours | real | YES |  |
| confirmed_trend | integer | YES |  |
| updated_at | text | YES | iso_dt:32137 |

## topic_maturity  (48 rows, 18 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| topic_key | text | NO |  |
| topic_display | text | YES |  |
| first_detected_at | text | YES | iso_dt:48 |
| last_scored_at | text | YES | iso_dt:48 |
| times_scored | integer | YES |  |
| days_in_system | integer | YES |  |
| maturity_class | text | YES |  |
| maturity_reason | text | YES |  |
| baseline_gradient | real | YES |  |
| baseline_overall | real | YES |  |
| baseline_detection | real | YES |  |
| baseline_confidence | real | YES |  |
| gradient_velocity | real | YES |  |
| score_velocity | real | YES |  |
| velocity_trend | text | YES |  |
| calibration_multiplier | real | YES |  |
| anomaly_gate_passed | integer | YES |  |
| updated_at | text | YES | iso_dt:48 |

## topic_queries  (139508 rows, 4 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | integer | NO |  |
| queried_at | text | NO | iso_dt:139508 |
| topic_key | text | NO |  |
| endpoint | text | NO |  |

## topic_registry  (32137 rows, 13 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| topic_key | text | NO |  |
| topic_display | text | NO |  |
| first_seen_at | text | YES | iso_dt:32137 |
| first_seen_platform | text | YES |  |
| last_seen_at | text | YES | iso_dt:32137 |
| total_mentions | integer | YES |  |
| niche_mentions | integer | YES |  |
| mainstream_mentions | integer | YES |  |
| platforms_seen | text | YES |  |
| current_stage | text | YES |  |
| is_anomaly | integer | YES |  |
| created_at | text | YES | iso_dt:32137 |
| updated_at | text | YES | iso_dt:32137 |

## topic_score_history  (0 rows, 12 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| topic_key | text | NO |  |
| scored_at | text | NO |  |
| overall_score | real | YES |  |
| detection_score | real | YES |  |
| confidence_score | real | YES |  |
| gradient_raw | real | YES |  |
| gradient_cal | real | YES |  |
| inertia_score | real | YES |  |
| platform_count | integer | YES |  |
| total_mentions | integer | YES |  |
| maturity_at_time | text | YES |  |

## topic_signals  (489719 rows, 13 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| extracted_at | text | NO | iso_dt:489719 |
| topic | text | NO |  |
| topic_key | text | NO |  |
| signal_id | text | YES |  |
| platform | text | NO |  |
| platform_tier | text | NO |  |
| source_name | text | YES |  |
| upvotes | integer | YES |  |
| comments | integer | YES |  |
| engagement_raw | real | YES |  |
| is_first_timer | integer | YES |  |
| is_organic | integer | YES |  |

## velocity_scores  (936614 rows, 37 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| id | text | NO |  |
| scored_at | text | NO | iso_dt:936614 |
| topic_key | text | NO |  |
| topic_display | text | NO |  |
| gradient_strength | real | YES |  |
| inertia_score | real | YES |  |
| platform_diversity | real | YES |  |
| dark_matter_score | real | YES |  |
| confidence_decay | real | YES |  |
| persistence_score | real | YES |  |
| nowtrendin_score | real | YES |  |
| overall_score | real | YES |  |
| detection_score | real | YES |  |
| confidence_score | real | YES |  |
| heisenberg_gap | real | YES |  |
| total_mentions | integer | YES |  |
| niche_mentions | integer | YES |  |
| mainstream_mentions | integer | YES |  |
| platforms_active | text | YES |  |
| first_timer_ratio | real | YES |  |
| engagement_asymmetry | integer | YES |  |
| gradient_ratio | real | YES |  |
| signal_stage | text | YES |  |
| is_gravitational_anomaly | integer | YES |  |
| anomaly_reason | text | YES |  |
| why_this_matters | text | YES |  |
| what_to_watch | text | YES |  |
| created_at | text | YES | iso_dt:936614 |
| serve_payload | text | YES |  |
| attention_magnitude | real | YES |  |
| n_mainstream_platforms | integer | YES |  |
| detection_pathway | text | YES |  |
| mainstream_ratio | real | YES |  |
| mainstream_breadth | real | YES |  |
| news_outlets | integer | YES |  |
| mainstream_confirmed | integer | YES |  |
| tier_migration | integer | YES |  |

## worker_heartbeat  (2 rows, 2 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| role | text | NO |  |
| beat_at | text | YES | iso_dt:2 |

## x_post_usage  (1 rows, 2 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| month | text | NO |  |
| posts | integer | YES |  |

## x_pull_usage  (5 rows, 2 cols)

| column | type | null | format (if date/text) |
|---|---|---|---|
| day | text | NO |  |
| pulls | integer | YES |  |