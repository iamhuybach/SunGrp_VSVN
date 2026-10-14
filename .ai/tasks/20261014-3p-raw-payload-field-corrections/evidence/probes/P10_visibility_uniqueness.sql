-- P10: ordering-tie and review-key uniqueness. Fabric DEV, read-only.
-- Save the single output row to evidence/results/P10_visibility_uniqueness.md.
-- Pass only when both counts are 0.
WITH ambiguous AS (
  SELECT source_name, source_id, CAST(crawled_at AS TIMESTAMP) AS crawled_ts, event_id
  FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
  WHERE lower(trim(source_name)) = 'google'
  GROUP BY source_name, source_id, CAST(crawled_at AS TIMESTAMP), event_id
  HAVING count(DISTINCT concat(
           CASE WHEN normalized_payload IS NULL THEN 'N:' ELSE 'V:' END,
           coalesce(sha2(normalized_payload, 256), '')
         )) > 1
),
duplicate_review AS (
  SELECT review_id
  FROM lh_vv_silver.dbo.slv_3p_poi_review
  WHERE review_id IS NOT NULL
  GROUP BY review_id
  HAVING count(*) > 1
)
SELECT
  (SELECT count(*) FROM ambiguous) AS ambiguous_order_groups,
  (SELECT count(*) FROM duplicate_review) AS duplicate_target_review_id_groups;
