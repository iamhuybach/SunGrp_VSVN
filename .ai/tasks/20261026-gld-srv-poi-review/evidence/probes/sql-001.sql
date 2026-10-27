-- Fabric DEV, SQL analytics endpoint, read-only. Resolves SQL-001.
-- Pass: 0 rows. Fail: any returned row.
-- Paste at most 50 rows into .ai/tasks/20261026-gld-srv-poi-review/evidence/results/sql-001.txt.
-- No personal data and no secrets.
SELECT 'rating_poi_id' AS check_name, CAST(poi_id AS STRING) AS key_value, COUNT(*) AS n
FROM lh_vv_silver.dbo.slv_3p_poi_rating
WHERE poi_id IS NOT NULL
GROUP BY poi_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 'review_id' AS check_name, CAST(ml.review_id AS STRING) AS key_value, COUNT(*) AS n
FROM lh_vv_silver.dbo.slv_enr_poi_review_multi_lang AS ml
INNER JOIN lh_vv_silver.dbo.slv_3p_poi_review AS rv
    ON ml.review_id = rv.review_id
GROUP BY ml.review_id
HAVING COUNT(*) > 1
