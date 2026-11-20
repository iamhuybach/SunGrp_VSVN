-- P1. Chỉ đọc, từng câu. Workspace cũ sgr_visitvn_prd_batch.
-- Mục đích: kiểu cột đã cặp, và số giá trị không cast được sang kiểu gold mới.
-- Không in giá trị gốc. Thiếu bảng thì ghi MISSING_TABLE.
-- Dán vào evidence/results/legacy_gold_types.txt.
DESCRIBE TABLE sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master;

-- Số dòng poi_master mà try_cast thất bại. 0 là cast không mất dòng.
SELECT COUNT(*) AS rows_n,
       SUM(CASE WHEN subcategory_tags IS NOT NULL AND TRY_CAST(subcategory_tags AS STRING) IS NULL THEN 1 ELSE 0 END) AS subcategory_tags_fail,
       SUM(CASE WHEN rating_overall IS NOT NULL AND TRY_CAST(rating_overall AS DECIMAL(4,2)) IS NULL THEN 1 ELSE 0 END) AS rating_overall_fail,
       SUM(CASE WHEN rating_count IS NOT NULL AND TRY_CAST(rating_count AS INT) IS NULL THEN 1 ELSE 0 END) AS rating_count_fail,
       SUM(CASE WHEN is_verified IS NOT NULL AND TRY_CAST(is_verified AS BOOLEAN) IS NULL THEN 1 ELSE 0 END) AS is_verified_fail,
       SUM(CASE WHEN is_bookable IS NOT NULL AND TRY_CAST(is_bookable AS BOOLEAN) IS NULL THEN 1 ELSE 0 END) AS is_bookable_fail,
       SUM(CASE WHEN is_active IS NOT NULL AND TRY_CAST(is_active AS BOOLEAN) IS NULL THEN 1 ELSE 0 END) AS is_active_fail
FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master;

DESCRIBE TABLE sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_enrichment_display;
