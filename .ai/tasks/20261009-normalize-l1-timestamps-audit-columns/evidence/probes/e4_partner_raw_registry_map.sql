-- Môi trường: Fabric DEV, lakehouse bronze + ctrl, chỉ đọc.
-- Mục đích: 3 payload đầy nhất của mỗi bảng trong partner_raw_data,
--   đối chiếu khóa JSON với ctrl_cfg_schema_registry.
--   section = column: mỗi cột registry có mặt trên sample hay không, và dạng giá trị.
--   section = extra_key: khóa có trong payload nhưng không có json_path trong registry.
-- Thứ tự: chạy một mình. Quét toàn bộ partner_raw_data vì raw không có stats.
-- Idempotent: không ghi.
-- Không trả after/before, tên, điện thoại, email, địa chỉ. Chuỗi lạ chỉ ghi độ dài.
-- Lưu kết quả vào evidence/results/e4_partner_raw_registry_map.txt.

WITH registry AS (
    SELECT
        src_object,
        trg_tbl,
        trg_column,
        json_path,
        data_type,
        convert_rule,
        CAST(is_active AS STRING) AS is_active
    FROM lh_vv_ctrl.dbo.ctrl_cfg_schema_registry
    WHERE src_schema = 'lh_vv_bronze.dbo'
      AND src_tbl = 'partner_raw_data'
      AND src_object_schema = 'public'
),
events AS (
    SELECT
        get_json_object(source, '$.table') AS src_table,
        op,
        CASE
            WHEN op IN ('c', 'r', 'u')
             AND after IS NOT NULL
             AND length(trim(after)) > 2
            THEN after
            WHEN before IS NOT NULL
             AND length(trim(before)) > 2
            THEN before
        END AS payload
    FROM lh_vv_bronze.dbo.partner_raw_data
    WHERE op IN ('c', 'r', 'u', 'd')
),
ranked AS (
    SELECT
        src_table,
        op,
        payload,
        row_number() OVER (
            PARTITION BY src_table
            ORDER BY length(payload) DESC, crc32(payload)
        ) AS sample_n
    FROM events
    WHERE src_table IS NOT NULL
      AND payload IS NOT NULL
      AND left(trim(payload), 1) = '{'
),
picked AS (
    SELECT
        src_table,
        sample_n,
        op,
        length(payload) AS payload_chars,
        from_json(payload, 'map<string,string>') AS m
    FROM ranked
    WHERE sample_n <= 3
),
column_map AS (
    SELECT
        r.src_object,
        r.trg_tbl,
        p.sample_n,
        p.op,
        p.payload_chars,
        r.trg_column,
        r.json_path,
        r.data_type,
        r.convert_rule,
        r.is_active,
        CASE
            WHEN p.src_table IS NULL THEN 'no_sample'
            WHEN p.m IS NULL THEN 'invalid_json'
        END AS parse_state,
        element_at(p.m, r.json_path) AS raw_value
    FROM registry r
    LEFT JOIN picked p
        ON p.src_table = r.src_object
),
samples AS (
    SELECT
        'column' AS section,
        src_object,
        trg_tbl,
        sample_n,
        op,
        payload_chars,
        trg_column,
        json_path,
        data_type,
        convert_rule,
        is_active,
        CASE
            WHEN parse_state IS NOT NULL THEN parse_state
            WHEN raw_value IS NULL THEN 'absent'
            WHEN raw_value = '__debezium_unavailable_value' THEN 'toast'
            WHEN raw_value = '' THEN 'empty'
            WHEN raw_value RLIKE '^-?[0-9]+$'
                THEN concat('integer:', length(regexp_replace(raw_value, '^-', '')))
            WHEN raw_value RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}([T ].*)?$' THEN 'iso'
            WHEN lower(raw_value) IN ('true', 'false') THEN lower(raw_value)
            WHEN raw_value LIKE '{%' THEN 'object'
            WHEN raw_value LIKE '[%' THEN 'array'
            ELSE concat('string_len:', length(raw_value))
        END AS shape
    FROM column_map
),
extra AS (
    SELECT
        'extra_key' AS section,
        p.src_table AS src_object,
        CAST(NULL AS STRING) AS trg_tbl,
        p.sample_n,
        p.op,
        p.payload_chars,
        CAST(NULL AS STRING) AS trg_column,
        p.k AS json_path,
        CAST(NULL AS STRING) AS data_type,
        CAST(NULL AS STRING) AS convert_rule,
        CAST(NULL AS STRING) AS is_active,
        'not_in_registry' AS shape
    FROM (
        SELECT src_table, sample_n, op, payload_chars, k
        FROM picked
        LATERAL VIEW explode(map_keys(m)) keys AS k
        WHERE m IS NOT NULL
    ) p
    LEFT JOIN registry r
        ON r.src_object = p.src_table
       AND r.json_path = p.k
    WHERE r.json_path IS NULL
)
SELECT *
FROM samples
UNION ALL
SELECT *
FROM extra
ORDER BY section, src_object, sample_n, json_path;
