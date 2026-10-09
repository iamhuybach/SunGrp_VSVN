-- Probe E1: hình dạng population của normalized_payload 3P
-- Môi trường: Fabric DEV, lakehouse lh_vv_bronze, chỉ đọc.
-- Mục đích: chốt các số liệu còn thiếu trước kiến trúc L1.
--   enrichment / enrichmentSiblings / enrichmentFailedLangs có còn không
--   extra_info có rỗng không
--   poi_content, poi_price, policies, raw_data có giá trị không
--   cờ phẳng poi_amenity có còn không
--   khóa review và media có thiếu hoặc trùng trong cùng event không
-- Thứ tự: chạy một mình. Không phụ thuộc probe khác.
-- Idempotent: không ghi. Chạy lại cho cùng một snapshot thì cùng kết quả.
-- Không SELECT normalized_payload, raw_payload, số điện thoại, review, tên tác giả, URL.
-- Lưu đúng một dòng tổng vào evidence/results/e1_3p_payload_shape.txt.

WITH base AS (
    SELECT
        source_name,
        source_id,
        event_id,
        normalized_payload AS p
    FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
),
shaped AS (
    SELECT
        source_name,
        source_id,
        event_id,
        p,
        get_json_object(p, '$.extra_info') AS extra_info,
        get_json_object(p, '$.poi_amenity') AS poi_amenity,
        get_json_object(p, '$.poi_content') AS poi_content,
        get_json_object(p, '$.poi_price') AS poi_price,
        get_json_object(p, '$.policies') AS policies,
        get_json_object(p, '$.raw_data') AS raw_data,
        get_json_object(p, '$.poi_review') AS poi_review,
        get_json_object(p, '$.poi_media') AS poi_media
    FROM base
),
review_elems AS (
    SELECT
        source_name,
        source_id,
        event_id,
        review.author_name AS author_name,
        review.`time` AS review_time
    FROM shaped
    LATERAL VIEW posexplode(
        from_json(poi_review, 'ARRAY<STRUCT<author_name:STRING,time:STRING>>')
    ) rv AS pos, review
    WHERE poi_review IS NOT NULL AND LEFT(TRIM(poi_review), 1) = '['
),
review_dups AS (
    SELECT source_name, source_id, event_id, author_name, review_time
    FROM review_elems
    WHERE author_name IS NOT NULL AND TRIM(author_name) <> ''
      AND review_time IS NOT NULL AND TRIM(review_time) <> ''
    GROUP BY source_name, source_id, event_id, author_name, review_time
    HAVING COUNT(*) > 1
),
media_elems AS (
    SELECT
        source_name,
        source_id,
        event_id,
        media.photo_api_uri AS photo_api_uri
    FROM shaped
    LATERAL VIEW posexplode(
        from_json(poi_media, 'ARRAY<STRUCT<photo_api_uri:STRING>>')
    ) md AS pos, media
    WHERE poi_media IS NOT NULL AND LEFT(TRIM(poi_media), 1) = '['
),
media_dups AS (
    SELECT source_name, source_id, event_id, photo_api_uri
    FROM media_elems
    WHERE photo_api_uri IS NOT NULL AND TRIM(photo_api_uri) <> ''
    GROUP BY source_name, source_id, event_id, photo_api_uri
    HAVING COUNT(*) > 1
)
SELECT
    COUNT(*) AS docs,
    SUM(CASE WHEN p IS NULL OR TRIM(p) = '' THEN 1 ELSE 0 END) AS payload_blank,
    SUM(CASE WHEN p IS NOT NULL AND TRIM(p) <> '' AND LEFT(TRIM(p), 1) <> '{' THEN 1 ELSE 0 END) AS payload_not_object,
    SUM(CASE WHEN extra_info IS NULL THEN 1 ELSE 0 END) AS extra_info_sql_null,
    SUM(CASE WHEN regexp_replace(extra_info, '\\s', '') = '{}' THEN 1 ELSE 0 END) AS extra_info_empty_object,
    SUM(CASE WHEN extra_info IS NOT NULL AND regexp_replace(extra_info, '\\s', '') <> '{}' THEN 1 ELSE 0 END) AS extra_info_nonempty,
    SUM(CASE WHEN extra_info RLIKE '"enrichment"\\s*:' THEN 1 ELSE 0 END) AS has_enrichment,
    SUM(CASE WHEN extra_info RLIKE '"enrichmentSiblings"\\s*:' THEN 1 ELSE 0 END) AS has_enrichment_siblings,
    SUM(CASE WHEN extra_info RLIKE '"enrichmentFailedLangs"\\s*:' THEN 1 ELSE 0 END) AS has_enrichment_failed_langs,
    SUM(CASE WHEN poi_content IS NOT NULL THEN 1 ELSE 0 END) AS poi_content_nonnull,
    SUM(CASE WHEN LEFT(TRIM(poi_content), 1) = '[' THEN 1 ELSE 0 END) AS poi_content_array,
    SUM(CASE WHEN LEFT(TRIM(poi_content), 1) = '{' THEN 1 ELSE 0 END) AS poi_content_object,
    SUM(CASE WHEN poi_price IS NOT NULL THEN 1 ELSE 0 END) AS poi_price_nonnull,
    SUM(CASE WHEN LEFT(TRIM(poi_price), 1) = '{' THEN 1 ELSE 0 END) AS poi_price_object,
    SUM(CASE WHEN policies IS NOT NULL THEN 1 ELSE 0 END) AS policies_nonnull,
    SUM(CASE WHEN raw_data IS NOT NULL THEN 1 ELSE 0 END) AS raw_data_nonnull,
    SUM(CASE WHEN poi_review IS NOT NULL THEN 1 ELSE 0 END) AS poi_review_nonnull,
    SUM(CASE WHEN LEFT(TRIM(poi_review), 1) = '[' THEN 1 ELSE 0 END) AS poi_review_array,
    SUM(CASE WHEN poi_media IS NOT NULL THEN 1 ELSE 0 END) AS poi_media_nonnull,
    SUM(CASE WHEN LEFT(TRIM(poi_media), 1) = '[' THEN 1 ELSE 0 END) AS poi_media_array,
    SUM(CASE
        WHEN poi_amenity RLIKE '"accessible_seating"|"is_wheelchair_accessible"|"has_parking"|"parking_is_free"|"has_outdoor_seating"|"has_wifi"|"has_ac"|"has_garden"|"has_ev_charging"|"payment_cash"|"payment_card"|"payment_debit_card"|"fnb_dine_in"|"fnb_takeaway"|"fnb_delivery"|"fnb_curbside_pickup"|"fnb_reservable"|"fnb_restroom"|"fnb_breakfast_available"|"fnb_serves_brunch"|"fnb_serves_lunch"|"fnb_serves_dinner"|"fnb_serves_dessert"|"fnb_serves_coffee"|"fnb_serves_alcohol"|"fnb_serves_vegetarian_food"|"fnb_good_for_groups"|"fnb_good_for_families"|"fnb_good_for_couples"|"hotel_has_breakfast"|"hotel_breakfast_included"|"hotel_free_cancellation"|"hotel_pets_allowed"|"hotel_has_pool"|"hotel_has_spa"|"hotel_has_gym"|"hotel_has_bar"|"hotel_has_restaurant"'
        THEN 1 ELSE 0
    END) AS amenity_flat_flag_docs,
    COALESCE((SELECT COUNT(*) FROM review_elems), 0) AS review_elements,
    COALESCE((SELECT SUM(CASE WHEN author_name IS NULL OR TRIM(author_name) = '' OR review_time IS NULL OR TRIM(review_time) = '' THEN 1 ELSE 0 END) FROM review_elems), 0) AS review_missing_author_or_time,
    COALESCE((SELECT COUNT(*) FROM review_dups), 0) AS review_dup_groups,
    COALESCE((SELECT COUNT(*) FROM media_elems), 0) AS media_elements,
    COALESCE((SELECT SUM(CASE WHEN photo_api_uri IS NULL OR TRIM(photo_api_uri) = '' THEN 1 ELSE 0 END) FROM media_elems), 0) AS media_missing_photo_api_uri,
    COALESCE((SELECT COUNT(*) FROM media_dups), 0) AS media_dup_groups
FROM shaped;
