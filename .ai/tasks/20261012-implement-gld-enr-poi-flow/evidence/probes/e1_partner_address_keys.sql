-- Môi trường: Fabric DEV, lakehouse lh_vv_silver, chỉ đọc.
-- Mục đích: liệt kê khoá cấp 1 của slv_pn_business_services.address và số dòng không rỗng.
--   Quyết định cần chốt: khoá nào điền slv_pn_poi.ward, district, province_name.
--   short_address đã chốt là address.full_address. Probe chỉ đếm khoá đó.
-- Thứ tự: chạy một mình. Không phụ thuộc probe khác.
-- Điều kiện: quyền đọc lh_vv_silver.dbo.slv_pn_business_services.
-- Idempotent: không ghi. Cùng snapshot thì cùng kết quả.
-- Không trả địa chỉ, tên, số điện thoại. Chỉ tên khoá và số đếm.
-- Lưu toàn bộ kết quả vào evidence/results/e1_partner_address_keys.txt.
-- Giới hạn: không quá 50 dòng khoá. Dòng summary luôn có, kể cả khi không có khoá.

WITH src AS (
    SELECT address
    FROM lh_vv_silver.dbo.slv_pn_business_services
    WHERE COALESCE(deleted, false) = false
),
parsed AS (
    SELECT from_json(address, 'map<string,string>') AS addr_map
    FROM src
),
flat AS (
    SELECT address_key, address_value
    FROM parsed
    LATERAL VIEW explode(addr_map) e AS address_key, address_value
    WHERE addr_map IS NOT NULL
),
totals AS (
    SELECT
        (SELECT COUNT(*) FROM src) AS active_row_count,
        (SELECT COUNT(*) FROM parsed WHERE addr_map IS NOT NULL) AS json_object_count
),
key_counts AS (
    SELECT address_key, COUNT(*) AS non_empty_count
    FROM flat
    WHERE address_value IS NOT NULL
      AND TRIM(address_value) <> ''
    GROUP BY address_key
),
combined AS (
    SELECT
        'summary' AS row_kind,
        active_row_count,
        json_object_count,
        CAST(NULL AS STRING) AS address_key,
        CAST(NULL AS BIGINT) AS non_empty_count,
        0 AS sort_group,
        CAST(NULL AS BIGINT) AS sort_count
    FROM totals
    UNION ALL
    SELECT
        'key' AS row_kind,
        t.active_row_count,
        t.json_object_count,
        k.address_key,
        k.non_empty_count,
        1 AS sort_group,
        k.non_empty_count AS sort_count
    FROM key_counts k
    CROSS JOIN totals t
)
SELECT
    row_kind,
    active_row_count,
    json_object_count,
    address_key,
    non_empty_count
FROM combined
ORDER BY sort_group, sort_count DESC, address_key
LIMIT 50;
