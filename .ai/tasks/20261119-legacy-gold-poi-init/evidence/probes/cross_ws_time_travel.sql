-- P5. Mở notebook ở sgr_visitvn_dev. Chỉ đọc.
-- Câu 1 lấy version mới nhất. Câu 2 thay <version> bằng số đó.
-- Nếu câu 2 lỗi, dán nguyên lỗi và ghi CROSS_WS_TIME_TRAVEL_FAIL.
-- Dán vào evidence/results/cross_ws_time_travel.txt.
DESCRIBE HISTORY sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master LIMIT 1;

SELECT COUNT(*) AS n
FROM sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master VERSION AS OF <version>;
