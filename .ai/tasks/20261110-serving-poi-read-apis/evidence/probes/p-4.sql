-- Environment: local compose PostgreSQL, database vv_data_serving, schema apps.
-- Prerequisite: representative gold rows already loaded. DEV or production only after an explicit approval for that run.
-- Decision: practical_info parsers (architecture P-4). Pass: shows whether each text is valid jsonb and a short sample.
-- holiday_exceptions has no lang column; the other three queries keep lang.
-- Limit: 30 rows and 300 characters per query. Redact any email or phone. No secrets.
-- Save sanitized output to .ai/tasks/20261110-serving-poi-read-apis/evidence/results/p-4.txt.

SELECT pg_input_is_valid(holiday_exceptions, 'jsonb') AS j, left(holiday_exceptions, 300) AS sample
FROM apps.srv_poi_info
WHERE holiday_exceptions IS NOT NULL
ORDER BY random()
LIMIT 30;

SELECT lang, pg_input_is_valid(time_to_spend, 'jsonb') AS j, left(time_to_spend, 300) AS sample
FROM apps.srv_poi_multi_lang
WHERE time_to_spend IS NOT NULL
ORDER BY random()
LIMIT 30;

SELECT lang, pg_input_is_valid(best_time, 'jsonb') AS j, left(best_time, 300) AS sample
FROM apps.srv_poi_multi_lang
WHERE best_time IS NOT NULL
ORDER BY random()
LIMIT 30;

SELECT lang, pg_input_is_valid(cost_vnd, 'jsonb') AS j, left(cost_vnd, 300) AS sample
FROM apps.srv_poi_multi_lang
WHERE cost_vnd IS NOT NULL
ORDER BY random()
LIMIT 30;
