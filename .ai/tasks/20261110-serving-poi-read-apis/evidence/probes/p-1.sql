-- Environment: local compose PostgreSQL, database vv_data_serving, schema apps.
-- Prerequisite: representative gold rows already loaded. DEV or production only after an explicit approval for that run.
-- Decision: D-2. Pass: the result lists stored business_sector values after lower(trim), with counts.
-- Limit: aggregated counts only. No personal data, no secrets. At most 50 rows.
-- Save sanitized output to .ai/tasks/20261110-serving-poi-read-apis/evidence/results/p-1.txt.
-- If this returns zero rows, also paste: SELECT count(*) FROM apps.srv_poi_info;

SELECT lower(trim(business_sector)) AS s, count(*)
FROM apps.srv_poi_info
WHERE deleted_at IS NULL
GROUP BY 1
ORDER BY 2 DESC;
