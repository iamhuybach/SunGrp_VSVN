-- Môi trường: Fabric DEV, lakehouse bronze, chỉ đọc.
-- Mục đích: phân loại hình dạng từng cột timestamp ứng viên của partner.
--   Quyết định cần chốt: EPOCH_S_TS, EPOCH_MS_TS, EPOCH_US_TS, DATE_DAYS, ISO datetime, ISO date, hoặc không phải timestamp.
--   Không gán đơn vị từ tên cột. last_verify_at là mốc đối chứng: seed đang là EPOCH_S_TS.
-- Thứ tự: chạy một mình. Không phụ thuộc probe khác.
-- Điều kiện: quyền đọc lh_vv_bronze.dbo.partner_raw_data.
--   Bảng raw không có stats. Câu này quét toàn bộ snapshot hiện tại. Chạy khi capacity F16 đang rảnh.
-- Idempotent: không ghi. Cùng snapshot thì cùng kết quả.
-- Không trả payload, số điện thoại, text, URL. Giá trị 'other' chỉ đếm, không in mẫu.
-- Lưu toàn bộ kết quả vào evidence/results/e1_partner_timestamp_shapes.txt.

WITH events AS (
    SELECT
        get_json_object(source, '$.table') AS src_table,
        CASE WHEN op = 'd' THEN before ELSE after END AS payload
    FROM lh_vv_bronze.dbo.partner_raw_data
    WHERE op IN ('c', 'r', 'u', 'd')
),
flat AS (
    SELECT src_table, column_name, val
    FROM events
    LATERAL VIEW stack(
        14,
        'created_at', get_json_object(payload, '$.created_at'),
        'updated_at', get_json_object(payload, '$.updated_at'),
        'deleted_at', get_json_object(payload, '$.deleted_at'),
        'last_updated_at', get_json_object(payload, '$.last_updated_at'),
        'last_in_activated_at', get_json_object(payload, '$.last_in_activated_at'),
        'last_verify_at', get_json_object(payload, '$.last_verify_at'),
        'valid_from', get_json_object(payload, '$.valid_from'),
        'valid_to', get_json_object(payload, '$.valid_to'),
        'expire_at', get_json_object(payload, '$.expire_at'),
        'usage_date', get_json_object(payload, '$.usage_date'),
        'check_in_date', get_json_object(payload, '$.check_in_date'),
        'checkout_date', get_json_object(payload, '$.checkout_date'),
        'departure_time', get_json_object(payload, '$.departure_time'),
        'arrival_time', get_json_object(payload, '$.arrival_time')
    ) s AS column_name, val
),
candidates AS (
    SELECT * FROM VALUES
        ('products', 'created_at'),
        ('products', 'updated_at'),
        ('products', 'deleted_at'),
        ('product_translations', 'created_at'),
        ('product_translations', 'updated_at'),
        ('product_attributes', 'created_at'),
        ('product_attributes', 'updated_at'),
        ('product_attribute_translations', 'created_at'),
        ('product_attribute_translations', 'updated_at'),
        ('product_attribute_values', 'created_at'),
        ('product_attribute_values', 'updated_at'),
        ('product_variants', 'created_at'),
        ('product_variants', 'updated_at'),
        ('product_variants', 'deleted_at'),
        ('product_variant_translations', 'created_at'),
        ('product_variant_translations', 'updated_at'),
        ('product_business_service_relation', 'created_at'),
        ('product_business_service_relation', 'updated_at'),
        ('product_posts', 'created_at'),
        ('product_posts', 'updated_at'),
        ('product_posts', 'deleted_at'),
        ('product_post_translations', 'created_at'),
        ('product_post_translations', 'updated_at'),
        ('partners', 'created_at'),
        ('partners', 'last_updated_at'),
        ('business_services', 'created_at'),
        ('business_services', 'last_updated_at'),
        ('business_services', 'last_in_activated_at'),
        ('business_services', 'last_verify_at'),
        ('business_locations', 'created_at'),
        ('business_locations', 'last_updated_at'),
        ('hotel_room_types', 'created_at'),
        ('hotel_room_types', 'updated_at'),
        ('hotel_room_types', 'deleted_at'),
        ('hotel_rate_plans', 'valid_from'),
        ('hotel_rate_plans', 'valid_to'),
        ('hotel_rate_plans', 'created_at'),
        ('hotel_rate_plans', 'updated_at'),
        ('hotel_rate_plans', 'deleted_at'),
        ('business_service_i18ns', 'created_at'),
        ('business_service_i18ns', 'updated_at'),
        ('business_service_poi_link', 'created_at'),
        ('business_service_poi_link', 'updated_at'),
        ('orders', 'expire_at'),
        ('orders', 'created_at'),
        ('orders', 'updated_at'),
        ('order_refs', 'created_at'),
        ('order_refs', 'updated_at'),
        ('order_item_tickets', 'usage_date'),
        ('order_item_tickets', 'valid_from'),
        ('order_item_tickets', 'valid_to'),
        ('order_item_tickets', 'created_at'),
        ('order_item_tickets', 'updated_at'),
        ('order_item_hotels', 'check_in_date'),
        ('order_item_hotels', 'checkout_date'),
        ('order_item_hotels', 'created_at'),
        ('order_item_hotels', 'updated_at'),
        ('order_item_flights', 'departure_time'),
        ('order_item_flights', 'arrival_time'),
        ('order_item_flights', 'created_at'),
        ('order_item_flights', 'updated_at')
    AS t(src_table, column_name)
),
shaped AS (
    SELECT
        f.src_table,
        f.column_name,
        CASE
            WHEN f.val IS NULL OR trim(f.val) IN ('', 'null') THEN 'empty'
            WHEN f.val RLIKE '^-?[0-9]+$' THEN 'integer'
            WHEN f.val RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' THEN 'iso_date'
            WHEN f.val RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?Z$' THEN 'iso_utc_z'
            WHEN f.val RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?[+-][0-9]{2}:?[0-9]{2}$' THEN 'iso_offset'
            WHEN f.val RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}[T ]' THEN 'iso_other'
            ELSE 'other'
        END AS shape,
        CASE
            WHEN f.val RLIKE '^-?[0-9]+$' THEN length(regexp_replace(f.val, '^-', ''))
        END AS digit_len,
        CASE
            WHEN f.val RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}[T ]' THEN length(regexp_extract(f.val, '\\.([0-9]+)', 1))
        END AS frac_len,
        f.val
    FROM flat f
    INNER JOIN candidates c
        ON f.src_table = c.src_table
       AND f.column_name = c.column_name
)
SELECT
    src_table,
    column_name,
    shape,
    digit_len,
    frac_len,
    count(*) AS n,
    min(CASE WHEN shape = 'integer' THEN try_cast(val AS BIGINT) END) AS int_min,
    max(CASE WHEN shape = 'integer' THEN try_cast(val AS BIGINT) END) AS int_max,
    min(CASE WHEN shape LIKE 'iso%' AND length(val) <= 40 THEN val END) AS iso_min,
    max(CASE WHEN shape LIKE 'iso%' AND length(val) <= 40 THEN val END) AS iso_max
FROM shaped
GROUP BY src_table, column_name, shape, digit_len, frac_len
ORDER BY src_table, column_name, shape, digit_len, frac_len;
