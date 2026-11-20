-- Môi trường: cùng tenant. Chỉ đọc, chạy từng câu. Chạy lại không ghi gì.
-- Model cũ: workspace sgr_visitvn_prd_batch, lakehouse lh_vv_gold, schema dbo.
-- Model mới: workspace sgr_visitvn_dev, lakehouse lh_vv_gold và lh_vv_silver, schema dbo.
-- Mở notebook ở một trong hai workspace. Không dùng tên tắt lh_vv_gold.
-- Thiếu bảng thì ghi MISSING_TABLE cho câu đó và chạy câu sau.
-- Aggregate, mẫu khóa tối đa 50 dòng. Không tên, địa chỉ, điện thoại, email, review.
-- Dán kết quả vào evidence/results/legacy_gold_poi_profile.txt.
-- Q1. poi_master model cũ: ingestion_source, lang, source_id trống.
SELECT ingestion_source,
       COUNT(*) AS rows_n,
       COUNT(DISTINCT poi_id) AS poi_ids,
       COUNT(DISTINCT source_id) AS source_ids,
       COUNT(DISTINCT lang) AS langs,
       SUM(CASE WHEN source_id IS NULL OR TRIM(source_id) = '' THEN 1 ELSE 0 END) AS blank_source_id
FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master
GROUP BY ingestion_source
ORDER BY rows_n DESC;

-- Q2. Số poi_id cũ trên một source_id, model cũ.
SELECT ingestion_source, lang_n, COUNT(*) AS source_ids
FROM (
  SELECT ingestion_source, source_id, COUNT(DISTINCT lang) AS lang_n
  FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master
  WHERE source_id IS NOT NULL AND TRIM(source_id) <> ''
  GROUP BY ingestion_source, source_id
)
GROUP BY ingestion_source, lang_n
ORDER BY ingestion_source, lang_n;

-- Q3. source_id partner_portal của gold cũ đối chiếu id silver model mới.
SELECT SUM(CASE WHEN s.id IS NULL THEN 1 ELSE 0 END) AS missing_in_silver,
       SUM(CASE WHEN s.id IS NOT NULL THEN 1 ELSE 0 END) AS matched,
       COUNT(*) AS gold_ids
FROM (
  SELECT DISTINCT source_id
  FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master
  WHERE ingestion_source = 'partner_portal'
    AND source_id IS NOT NULL AND TRIM(source_id) <> ''
) g
LEFT JOIN sgr_visitvn_dev.lh_vv_silver.dbo.slv_pn_business_services s
  ON s.id = g.source_id;

-- Q4. Mẫu khóa google và partner_portal. Tối đa 50 dòng.
SELECT ingestion_source, source_id,
       concat_ws(',', sort_array(collect_set(lang))) AS langs,
       COUNT(DISTINCT poi_id) AS poi_ids
FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master
WHERE ingestion_source IN ('google', 'partner_portal')
  AND source_id IS NOT NULL AND TRIM(source_id) <> ''
GROUP BY ingestion_source, source_id
LIMIT 50;

-- Q5. Đếm dòng gold cũ. Câu nào lỗi vì thiếu bảng thì ghi MISSING_TABLE, chạy tiếp.
SELECT 'poi_detail' AS table_name, COUNT(*) AS n
FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_detail
UNION ALL
SELECT 'poi_review', COUNT(*) FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_review
UNION ALL
SELECT 'poi_rating', COUNT(*) FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_rating
UNION ALL
SELECT 'poi_enrichment_display', COUNT(*) FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_enrichment_display
UNION ALL
SELECT 'ai_poi', COUNT(*) FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_poi
UNION ALL
SELECT 'ai_poi_rating', COUNT(*) FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_poi_rating
UNION ALL
SELECT 'ai_poi_review', COUNT(*) FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_poi_review
UNION ALL
SELECT 'ai_enriched_poi', COUNT(*) FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_enriched_poi
UNION ALL
SELECT 'poi_address_enrichment_staging', COUNT(*)
FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_address_enrichment_staging;

-- Q6. Đếm dòng gold mới đang có, workspace sgr_visitvn_dev.
SELECT 'gld_srv_poi_info' AS table_name, COUNT(*) AS n
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info
UNION ALL
SELECT 'gld_srv_poi_multi_lang', COUNT(*) FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang
UNION ALL
SELECT 'gld_srv_poi_review', COUNT(*) FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_review;
