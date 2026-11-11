-- Environment: local compose PostgreSQL, database vv_data_serving, schema apps.
-- Prerequisite: representative gold rows already loaded. DEV or production only after an explicit approval for that run.
-- Decision: experiences JSON parser (architecture P-3, §6.5). Pass: shows whether experience is valid jsonb and a short sample.
-- Limit: 30 rows, 300 characters. Redact any email or phone before pasting. No secrets.
-- Save sanitized output to .ai/tasks/20261110-serving-poi-read-apis/evidence/results/p-3.txt.

SELECT lang, pg_input_is_valid(experience, 'jsonb') AS j, left(experience, 300) AS sample
FROM apps.srv_poi_multi_lang
WHERE experience IS NOT NULL
ORDER BY random()
LIMIT 30;
