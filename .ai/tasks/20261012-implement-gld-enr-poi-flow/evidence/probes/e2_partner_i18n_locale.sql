-- Môi trường: Fabric DEV, lakehouse lh_vv_silver, chỉ đọc.
-- Mục đích: liệt kê giá trị locale của slv_pn_business_service_i18ns và số dòng.
--   Quyết định cần chốt: mã locale tiếng Việt dùng cho slv_pn_poi.name.
-- Thứ tự: chạy một mình. Không phụ thuộc probe khác.
-- Điều kiện: quyền đọc lh_vv_silver.dbo.slv_pn_business_service_i18ns.
-- Idempotent: không ghi. Cùng snapshot thì cùng kết quả.
-- Không trả name, bio, hay business_service_id.
-- Lưu toàn bộ kết quả vào evidence/results/e2_partner_i18n_locale.txt.
-- Giới hạn: không quá 50 giá trị locale.

SELECT
    locale,
    COUNT(*) AS row_count
FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns
WHERE COALESCE(deleted, false) = false
GROUP BY locale
ORDER BY row_count DESC, locale
LIMIT 50;
