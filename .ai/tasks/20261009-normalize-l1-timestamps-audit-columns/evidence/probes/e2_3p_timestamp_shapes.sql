-- Môi trường: Fabric DEV, lakehouse bronze, chỉ đọc.
-- Mục đích: phân loại hình dạng timestamp 3rd-party trên population hiện tại.
--   crawled_at, normalized_payload.created_at, poi_review[].time, ingested_date.
--   Một file mẫu không phải hợp đồng. Câu này chỉ đếm lớp hình dạng.
-- Thứ tự: chạy một mình. Không phụ thuộc E1.
-- Điều kiện: quyền đọc lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream.
-- Idempotent: không ghi. Cùng snapshot thì cùng kết quả.
-- Không trả số điện thoại, nội dung review, URL media, raw_payload, tên tác giả.
-- Lưu toàn bộ kết quả vào evidence/results/e2_3p_timestamp_shapes.txt.

WITH docs AS (
    SELECT
        crawled_at,
        ingested_date,
        get_json_object(normalized_payload, '$.created_at') AS payload_created_at,
        get_json_object(normalized_payload, '$.poi_review') AS review_json
    FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
),
review_times AS (
    SELECT review.time AS val
    FROM docs
    LATERAL VIEW explode(
        from_json(review_json, 'array<struct<time:string>>')
    ) r AS review
),
fields AS (
    SELECT 'crawled_at' AS field_name, crawled_at AS val FROM docs
    UNION ALL
    SELECT 'ingested_date', ingested_date FROM docs
    UNION ALL
    SELECT 'payload_created_at', payload_created_at FROM docs
    UNION ALL
    SELECT 'review_time', val FROM review_times
),
shaped AS (
    SELECT
        field_name,
        CASE
            WHEN val IS NULL OR trim(val) IN ('', 'null') THEN 'empty'
            WHEN val RLIKE '^-?[0-9]+$' THEN 'integer'
            WHEN val RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' THEN 'iso_date'
            WHEN val RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?Z$' THEN 'iso_utc_z'
            WHEN val RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?[+-][0-9]{2}:?[0-9]{2}$' THEN 'iso_offset'
            WHEN val RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}[T ]' THEN 'iso_other'
            ELSE 'other'
        END AS shape,
        CASE
            WHEN val RLIKE '^-?[0-9]+$' THEN length(regexp_replace(val, '^-', ''))
        END AS digit_len,
        CASE
            WHEN val RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}[T ]' THEN length(regexp_extract(val, '\\.([0-9]+)', 1))
        END AS frac_len,
        val
    FROM fields
)
SELECT
    field_name,
    shape,
    digit_len,
    frac_len,
    count(*) AS n,
    min(CASE WHEN shape = 'integer' THEN try_cast(val AS BIGINT) END) AS int_min,
    max(CASE WHEN shape = 'integer' THEN try_cast(val AS BIGINT) END) AS int_max,
    min(CASE WHEN shape LIKE 'iso%' AND length(val) <= 40 THEN val END) AS iso_min,
    max(CASE WHEN shape LIKE 'iso%' AND length(val) <= 40 THEN val END) AS iso_max
FROM shaped
GROUP BY field_name, shape, digit_len, frac_len
ORDER BY field_name, shape, digit_len, frac_len;
