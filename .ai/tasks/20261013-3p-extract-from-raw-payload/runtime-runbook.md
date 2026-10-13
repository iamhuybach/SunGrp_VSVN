# Hướng dẫn kiểm chứng runtime

Trạng thái: `ĐÃ CHẠY DEV`.

## Phạm vi và môi trường

Fabric DEV. Lakehouse `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_ctrl`. Chạy `NB_LIB_EXTRACT_RAWDATA`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, và cell cấu hình 3P trong `NB_CREATE_DDL`. Không deploy notebook gold. `PL_VV_TRANS_SLV_TO_ENR_15P` giữ tắt.

Khóa tay: `cutover-20261014`.

## Điều kiện tiên quyết

Code mới đã có trên workspace DEV. Schedule `PL_VV_TRANS_SLV_TO_ENR_15P` đang tắt và không có instance đang chạy. `lock_exec_id` của `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` và `wm_transform_brz_3rd_crawler_poi_stream` đều NULL.

## Baseline trước khi chạy

Chỉ `SELECT`. Ghi số dòng vào mục kết quả.

```sql
SELECT 'slv_3p_poi' AS tbl, count(*) AS n FROM lh_vv_silver.dbo.slv_3p_poi
UNION ALL SELECT 'slv_3p_poi_address', count(*) FROM lh_vv_silver.dbo.slv_3p_poi_address
UNION ALL SELECT 'slv_3p_poi_contact', count(*) FROM lh_vv_silver.dbo.slv_3p_poi_contact
UNION ALL SELECT 'slv_3p_poi_price', count(*) FROM lh_vv_silver.dbo.slv_3p_poi_price
UNION ALL SELECT 'slv_3p_poi_opening_hours', count(*) FROM lh_vv_silver.dbo.slv_3p_poi_opening_hours
UNION ALL SELECT 'slv_3p_poi_rating', count(*) FROM lh_vv_silver.dbo.slv_3p_poi_rating
UNION ALL SELECT 'slv_3p_poi_amenity', count(*) FROM lh_vv_silver.dbo.slv_3p_poi_amenity
UNION ALL SELECT 'slv_3p_poi_review', count(*) FROM lh_vv_silver.dbo.slv_3p_poi_review
UNION ALL SELECT 'slv_3p_poi_media', count(*) FROM lh_vv_silver.dbo.slv_3p_poi_media;

SELECT watermark_id, status, last_src_version, lock_exec_id
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN (
  'wm_transform_brz_3rd_crawler_poi_stream',
  'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P'
);

SELECT count(*) AS state_rows FROM lh_vv_ctrl.dbo.ctrl_cdc_state
WHERE src_tbl = 'brz_3rd_crawler_poi_stream';
SELECT count(*) AS reject_rows FROM lh_vv_ctrl.dbo.ctrl_cdc_reject
WHERE src_tbl = 'brz_3rd_crawler_poi_stream';
```

## Các bước thực hiện

1. Giữ khóa, chỉ khi `lock_exec_id` đang NULL:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark
SET lock_exec_id = 'cutover-20261014', lock_at = current_timestamp()
WHERE watermark_id = 'wm_transform_brz_3rd_crawler_poi_stream'
  AND lock_exec_id IS NULL;
```

Đọc lại dòng. `lock_exec_id` phải là `cutover-20261014`. Xong các bước ghi trong hạn 780 phút.

2. Trong `NB_CREATE_DDL`, chạy đúng bốn cell sau. Không chạy cell kết thúc bằng `seed_registry(TABLE_CONFIGS, SRC_SCHEMA, SRC_TBL)`. Cell đó ghi đè registry partner.

   - Cell code tiêu đề gần `Tạo bảng ctrl_cfg_schema_registry`. Nó `CREATE TABLE IF NOT EXISTS` bảng registry. Bảng đã có thì không đổi.
   - Cell code bắt đầu bằng comment `TABLE_CONFIGS_3P`. Nó chỉ tạo biến Python, chưa ghi bảng.
   - Cell code gọi `seed_registry(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream")` rồi `show_registry`. Hàm này tự `ALTER` thêm `convert_arg` nếu cột chưa có, rồi thay đúng các dòng của `brz_3rd_crawler_poi_stream`. Kỳ vọng trên `show_registry`: 9 bảng, tổng 52 cột, không có cột `is_active = false`, 10 cột có `convert_arg`. Comment trong cell vẫn ghi 10 bảng và 98 cột. Số đúng là output của `show_registry`.
   - Cell `%%sql` có `DELETE` và danh sách gồm `slv_3p_poi_policy`. Nó xóa dòng policy và các bảng 3P đã bỏ khỏi pipeline config và registry.
   - Phần `UPDATE dedup_order = 'display_order ASC'` nằm ở cuối cell `%%sql` tiêu đề `Tạo bảng ctrl_mng_pipeline_config`. Chạy cả cell đó được: `CREATE` và `INSERT` đều có `IF NOT EXISTS` hoặc `WHERE NOT EXISTS`. Câu cuối sửa dòng media đã có từ trước.

3. Chạy `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` với `dry_run = True`, `src_tbl = partner_raw_data`, tham số khác giữ mặc định. Đạt khi không có `ConfigError`.

4. Chạy `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` khi bảng cũ vẫn còn:

- `dry_run = True`
- `full_reload = True`
- `allow_full_scan = True`
- `max_parallel = 12`
- `max_retries = 1`
- `cast_null_policy = FAIL`
- `sources = google`
- `src_schema = lh_vv_bronze.dbo`
- `src_tbl = brz_3rd_crawler_poi_stream`
- `pl_name = PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`
- `table_filter` trống
- `run_id` trống

Đạt khi self-check pass, `cast_null` rỗng, `mapped_heads_missing` rỗng, mỗi bảng `DOC` có `docs_by_table = 53`, `bad_shape` rỗng, rejected = 0. Fail thì làm R1, chưa `DROP`.

5. Sao lưu:

```sql
CREATE TABLE lh_vv_silver.dbo.bak_20261014_slv_3p_poi AS SELECT * FROM lh_vv_silver.dbo.slv_3p_poi;
CREATE TABLE lh_vv_silver.dbo.bak_20261014_slv_3p_poi_address AS SELECT * FROM lh_vv_silver.dbo.slv_3p_poi_address;
CREATE TABLE lh_vv_silver.dbo.bak_20261014_slv_3p_poi_contact AS SELECT * FROM lh_vv_silver.dbo.slv_3p_poi_contact;
CREATE TABLE lh_vv_silver.dbo.bak_20261014_slv_3p_poi_price AS SELECT * FROM lh_vv_silver.dbo.slv_3p_poi_price;
CREATE TABLE lh_vv_silver.dbo.bak_20261014_slv_3p_poi_opening_hours AS SELECT * FROM lh_vv_silver.dbo.slv_3p_poi_opening_hours;
CREATE TABLE lh_vv_silver.dbo.bak_20261014_slv_3p_poi_rating AS SELECT * FROM lh_vv_silver.dbo.slv_3p_poi_rating;
CREATE TABLE lh_vv_silver.dbo.bak_20261014_slv_3p_poi_amenity AS SELECT * FROM lh_vv_silver.dbo.slv_3p_poi_amenity;
CREATE TABLE lh_vv_silver.dbo.bak_20261014_slv_3p_poi_review AS SELECT * FROM lh_vv_silver.dbo.slv_3p_poi_review;
CREATE TABLE lh_vv_silver.dbo.bak_20261014_slv_3p_poi_media AS SELECT * FROM lh_vv_silver.dbo.slv_3p_poi_media;
```

Ghi `count(*)` từng bảng `bak_*`.

6. Cổng đủ POI. Kết quả phải là 0.

```sql
WITH b AS (
  SELECT DISTINCT regexp_replace(md5(concat(source_name, source_id)),
         '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5') AS poi_id
  FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
  WHERE lower(trim(source_name)) = 'google'
    AND raw_payload IS NOT NULL AND trim(raw_payload) <> ''
)
SELECT count(*) AS missing_in_bronze
FROM lh_vv_silver.dbo.slv_3p_poi s
LEFT ANTI JOIN b ON s.poi_id = b.poi_id;
```

7. `DROP` từng bảng:

```sql
DROP TABLE lh_vv_silver.dbo.slv_3p_poi;
DROP TABLE lh_vv_silver.dbo.slv_3p_poi_address;
DROP TABLE lh_vv_silver.dbo.slv_3p_poi_contact;
DROP TABLE lh_vv_silver.dbo.slv_3p_poi_price;
DROP TABLE lh_vv_silver.dbo.slv_3p_poi_opening_hours;
DROP TABLE lh_vv_silver.dbo.slv_3p_poi_rating;
DROP TABLE lh_vv_silver.dbo.slv_3p_poi_amenity;
DROP TABLE lh_vv_silver.dbo.slv_3p_poi_review;
DROP TABLE lh_vv_silver.dbo.slv_3p_poi_media;
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_3p_poi_policy;
```

8. Nhả khóa rồi chạy init:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark
SET lock_exec_id = NULL, lock_at = NULL
WHERE watermark_id = 'wm_transform_brz_3rd_crawler_poi_stream'
  AND lock_exec_id = 'cutover-20261014';
```

Chạy `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` ba lần. Giữ `sources = google`, `src_schema = lh_vv_bronze.dbo`, `src_tbl = brz_3rd_crawler_poi_stream`, `pl_name = PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, `max_parallel = 12`, `max_retries = 1`, `cast_null_policy = FAIL`, `allow_full_scan = True`, `table_filter` trống, `run_id` trống, `dry_run = False`.

- Lần 1: `full_reload = True`.
- Lần 2: `full_reload = True`.
- Lần 3: `full_reload = False`.

## Kiểm tra kết quả

Chín bảng `SUCCESS`. Lần full thứ hai có `inserted_rows = 0`. Lần incremental là `SUCCESS` hoặc `NO_DATA`. `last_src_version` không nhỏ hơn baseline. Mỗi bảng `DOC` có 17 dòng, không trùng `poi_id`. `review_id` và `media_dedup_key` không trùng. Khóa review và media trong `bak_*` đều còn ở bảng mới. Các cột đã chứng minh khớp `<=>` với `bak_*`. Chỉ báo số dòng `city` và `ward` khác nhau. `PL_VV_TRANS_SLV_TO_ENR_15P` vẫn tắt.

## Chạy lại để kiểm tra idempotency

Lần full thứ hai ở bước 8. `inserted_rows = 0`. Số dòng chín bảng không đổi so với lần full thứ nhất.

## Kiểm tra log và watermark

```sql
SELECT status, run_mode, read_rows, valid_rows, rejected_rows, tbl_success_count, tbl_failed_count
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE nb_name LIKE '%3RD_PARTY%'
ORDER BY started_at DESC
LIMIT 5;

SELECT watermark_id, status, last_src_version, lock_exec_id
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_transform_brz_3rd_crawler_poi_stream';
```

Sau bước 8, `lock_exec_id` là NULL.

## Rollback và forward recovery

R1, chưa `DROP`: seed lại registry 3P bản cũ, đưa `dedup_order` media về `display_order ASC, media_id ASC`, deploy notebook extract cũ, nhả khóa, bật lại schedule 15P.

R2, đã `DROP`: giữ 15P tắt, giữ khóa nguồn, làm R1 cho code và config, `DROP` bảng hình mới, nhả khóa, chạy notebook cũ với `full_reload = True` và `allow_full_scan = True`, đối chiếu số dòng với `bak_*`, rồi mới bật 15P.

Không sửa watermark bằng tay. Không rollback gold. Chỉ `DROP` bảng `bak_*` sau khi bạn chấp nhận kết quả.

## Kết quả người dùng ghi nhận

Ngày 2026-10-14, Fabric DEV.

Baseline: `slv_3p_poi` 17, address 17, contact 17, price 11, opening_hours 13, rating 17, amenity 17, review 85, media 265. Watermark `wm_transform_brz_3rd_crawler_poi_stream` SUCCESS, `last_src_version` 13, khóa trống. State 143 dòng. Reject 0.

Seed 3P: 9 bảng, mọi bảng 0 cột tắt. Tổng cột 10+12+2+3+6+4+5+3+7 = 52. Mười rule có đối số: 7 `ARRAY_PICK`, `JSON_PICK`, `ARRAY_PROJECT`, `ENUM_MAP`.

Dry run `exec_id` `6a2d2d6c-192c-4994-acad-f980a6a98a51`: self-check pass, `NO_DATA`, đọc version 13 không có commit mới. Không đọc 53 tài liệu vì `full_reload` không bật.

Full reload `exec_id` `3b3804b5-e61a-4b75-aec8-d1cdc7885453`: `SUCCESS`, đọc 53, hợp lệ 53, rejected 0, cast_null 0, 9 bảng ok. Insert: poi, address, contact, price, opening_hours, rating, amenity mỗi bảng 17. Review input 265, insert 85. Media input 530, insert 530.

Người dùng xác nhận lần full thứ hai và lần incremental đều success. Lần incremental không có update mới.

`mapped_heads_missing` báo `authorAttribution`, `heightPx`, `name`, `publishTime`, `text`, `widthPx`. Đó là khóa nằm trong `reviews` và `photos`, không phải khóa cấp 1. Watch đã đếm nhầm. Dữ liệu review và media vẫn ghi được. Code watch đã sửa sau lần chạy này. Không cần `DROP` lại.

Đối chiếu `slv_3p_poi_address` với `bak_20261014_slv_3p_poi_address`: `city_differ = 1`, `ward_differ = 3`. Đây là số báo cáo đã được chấp nhận từ trước. Không chặn cutover.
