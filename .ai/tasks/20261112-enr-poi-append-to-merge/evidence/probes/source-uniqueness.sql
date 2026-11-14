-- Môi trường: Fabric DEV, Spark SQL. Notebook gắn được lh_vv_silver. Không chạy pipeline hay notebook nghiệp vụ.
-- Mục đích: SQL-001 và SQL-002. Nguồn MERGE của info và review phải duy nhất trên khoá grain.
-- Thứ tự: chạy một SELECT này. Không ghi bảng.
-- Điều kiện: bốn bảng silver dưới đây đã có.
-- Chạy lại: chỉ đọc, kết quả phụ thuộc dữ liệu hiện tại, không đổi dữ liệu.
-- Đạt: mỗi dòng có null_key_count = 0 và row_count = distinct_key_count.
-- Không đạt: null_key_count > 0, hoặc row_count khác distinct_key_count, hoặc bảng thiếu.
-- Kết quả: .ai/tasks/20261112-enr-poi-append-to-merge/evidence/results/source-uniqueness.txt
-- Giới hạn: bốn dòng tổng hợp. Không lấy nội dung review, tên, hay địa chỉ.

SELECT 'slv_poi_entity_non_enrich' AS table_name,
       'poi_id' AS key_column,
       COUNT(*) AS row_count,
       SUM(CASE WHEN poi_id IS NULL THEN 1 ELSE 0 END) AS null_key_count,
       COUNT(DISTINCT poi_id) AS distinct_key_count
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich

UNION ALL

SELECT 'slv_3p_poi_rating' AS table_name,
       'poi_id' AS key_column,
       COUNT(*) AS row_count,
       SUM(CASE WHEN poi_id IS NULL THEN 1 ELSE 0 END) AS null_key_count,
       COUNT(DISTINCT poi_id) AS distinct_key_count
FROM lh_vv_silver.dbo.slv_3p_poi_rating

UNION ALL

SELECT 'slv_3p_poi_price' AS table_name,
       'poi_id' AS key_column,
       COUNT(*) AS row_count,
       SUM(CASE WHEN poi_id IS NULL THEN 1 ELSE 0 END) AS null_key_count,
       COUNT(DISTINCT poi_id) AS distinct_key_count
FROM lh_vv_silver.dbo.slv_3p_poi_price

UNION ALL

SELECT 'slv_3p_poi_review' AS table_name,
       'review_id' AS key_column,
       COUNT(*) AS row_count,
       SUM(CASE WHEN review_id IS NULL THEN 1 ELSE 0 END) AS null_key_count,
       COUNT(DISTINCT review_id) AS distinct_key_count
FROM lh_vv_silver.dbo.slv_3p_poi_review
;
