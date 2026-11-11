-- Environment: local compose PostgreSQL, database vv_data_serving, schema apps.
-- Prerequisite: representative gold rows already loaded. DEV or production only after an explicit approval for that run.
-- Decision: D-2. Pass: counts of source_name by is_recommended, plus how many rows have rating_overall.
-- Limit: aggregated counts only. No personal data, no secrets. At most 50 rows.
-- Save sanitized output to .ai/tasks/20261110-serving-poi-read-apis/evidence/results/p-2.txt.
-- If this returns zero rows, also paste: SELECT count(*) FROM apps.srv_poi_info;

SELECT lower(trim(source_name)) AS src, is_recommended, count(*) AS n, count(rating_overall) AS n_rating
FROM apps.srv_poi_info
WHERE deleted_at IS NULL
GROUP BY 1, 2;
