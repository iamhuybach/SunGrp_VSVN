-- Probe: key-uniqueness
-- Environment: Fabric DEV. Spark SQL on lakehouse lh_vv_gold. Do not run a pipeline or business notebook.
-- Decision: existing MERGE on poi_id / review_id is valid only if each current target key is unique and not null.
-- Pass: each result row has null_key_count = 0 and row_count = distinct_key_count.
-- Fail: null_key_count > 0, or row_count <> distinct_key_count. A missing table fails; paste the error text.
-- Steps: open one notebook on lh_vv_gold, run only this SELECT, paste the two aggregate rows.
-- Output: .ai/tasks/20261112-enr-poi-append-to-merge/evidence/results/key-uniqueness.txt
-- Limits: two aggregate rows, no personal data, no secrets, no sample of review text or names.

SELECT 'gld_enr_poi_info' AS table_name,
       'poi_id' AS key_column,
       COUNT(*) AS row_count,
       SUM(CASE WHEN poi_id IS NULL THEN 1 ELSE 0 END) AS null_key_count,
       COUNT(DISTINCT poi_id) AS distinct_key_count
FROM lh_vv_gold.enr.gld_enr_poi_info

UNION ALL

SELECT 'gld_enr_poi_review' AS table_name,
       'review_id' AS key_column,
       COUNT(*) AS row_count,
       SUM(CASE WHEN review_id IS NULL THEN 1 ELSE 0 END) AS null_key_count,
       COUNT(DISTINCT review_id) AS distinct_key_count
FROM lh_vv_gold.enr.gld_enr_poi_review
;
