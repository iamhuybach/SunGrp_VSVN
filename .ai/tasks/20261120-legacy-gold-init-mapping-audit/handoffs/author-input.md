# Author input — update the runtime runbook for D-07

Rewrite `runtime-runbook.md` in Vietnamese for task `20261120-legacy-gold-init-mapping-audit`. Keep the required runbook sections.

Notebook `NB_SETUP_LEGACY_GOLD_POI`, workspace `sgr_visitvn_dev`, lakehouse `lh_vv_gold`. Parameters: `p_mode` is `PLAN` or `RUN`. `p_pin_json` for this rerun is exactly:

{"poi_master": 8065, "poi_enrichment_display": 6489, "poi_detail": 6912, "poi_review": 69, "poi_rating": 63}

D-07: when `$.is_24_7` lower-trim equals `true`, `operating_hours` is the mapping case-2 JSON (seven days, `is_open_all_day` true, no open or close time). The summary code is `IS_24_7`. Other bad periods stay `GOOGLE_BAD_TIME` and null.

PLAN passes only if `map.drift_n` is 0, `detail_conflict_n` is 0, `rating_cast_fail_n` is 0, `candidates` is 45476, the `hours_reason` counts sum to `candidates`, `GOOGLE_BAD_TIME` is absent or 0, `IS_24_7` is at least 6430, `OK` is at most 29988, `NO_PERIODS` is at most 9058, and `NO_DETAIL` is absent or 0. Report `29988 - OK`, `9058 - NO_PERIODS`, and `hours_24_7_partner_n`. Those three do not block.

RUN passes when the info commit is `COMMITTED`, there is no duplicate `poi_id`, both `load_origin IS NULL` EXCEPT ALL directions return 0 rows, Google legacy null hours are below 25917 and at most `NO_PERIODS + NO_DETAIL + GOOGLE_*`, Google all-day rows are above 0 and all-day rows with a bad shape are 0, Google `holiday_exceptions` is NULL, partner rating and review counts are NULL, and `is_recommended` is true exactly for partner.

The user runs Fabric. Do not invent pins. Counts and codes only, at most 50 rows, no names and no hour text. Paste into `Kết quả người dùng ghi nhận`.
