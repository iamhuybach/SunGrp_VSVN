# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`

## Phạm vi và môi trường

Fabric DEV. Lakehouse `lh_vv_bronze`, `lh_vv_ctrl`, `lh_vv_silver`. Notebook `NB_CREATE_DDL` và `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` đã được đưa lên workspace từ bản repo sau Phần A.

Không chạy partner. Không thêm activity 3P vào `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`.

## Điều kiện tiên quyết

- `lock_exec_id` của `wm_transform_brz_3rd_crawler_poi_stream` là NULL. Không có lịch chạy 3P.
- Đã ghi snapshot ở mục dưới. `DROP` xóa dữ liệu enrich cũ. Muốn quay lại dữ liệu đó thì `RESTORE` từ snapshot trước khi `DROP`.

## Baseline trước khi chạy

Ghi lại, chỉ số đếm và version, không ghi payload:

- Version mới nhất của `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry`, `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`.
- Version và số dòng của 8 bảng còn giữ và 5 bảng sắp xóa, cộng `slv_3p_poi_policy`.
- Dòng watermark: `last_src_version`, `last_src_table_id`, `watermark_value`, `status`, `lock_exec_id`.
- Số dòng `ctrl_cdc_state` và `ctrl_cdc_reject` theo `trg_tbl` với `src_tbl = 'brz_3rd_crawler_poi_stream'`.

## Các bước thực hiện

Chạy trong notebook Spark. `%%sql` một câu một cell nếu Fabric không chạy nhiều câu trong một cell.

1. Không `ALTER` và không `DROP COLUMN`. Bảng Delta này không xóa được cột khi chưa bật column mapping, và không bật mapping. Muốn bỏ cột cũ thì `DROP TABLE` cả bảng, extract tạo lại từ registry.

Cell `DELETE` trong `NB_CREATE_DDL` chỉ xóa dòng ctrl của năm bảng đã bỏ. Cell đó không `DROP` bảng silver.

```sql
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_3p_poi_price;
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_3p_poi_raw_data;
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_3p_poi_content;
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_3p_poi_enrichment;
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_3p_poi_review_i18n;
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_3p_poi_amenity;
```

`slv_3p_poi_amenity` nằm trong danh sách vì bảng đã tạo lúc registry còn 38 cờ. Xóa bảng, seed registry xong rồi extract sẽ tạo lại với `poi_id`, `amenity_schema_json`, `ext_attributes_json`.

2. Chạy cell `DELETE` trong `NB_CREATE_DDL`. Xóa hẳn dòng của năm bảng, không soft delete:

```sql
DELETE FROM lh_vv_ctrl.dbo.ctrl_cfg_schema_registry
WHERE src_schema = 'lh_vv_bronze.dbo'
  AND src_tbl = 'brz_3rd_crawler_poi_stream'
  AND trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN (
      'slv_3p_poi_price', 'slv_3p_poi_raw_data', 'slv_3p_poi_content',
      'slv_3p_poi_enrichment', 'slv_3p_poi_review_i18n'
  );

DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00'
  AND src_schema = 'lh_vv_bronze.dbo'
  AND src_tbl = 'brz_3rd_crawler_poi_stream'
  AND trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN (
      'slv_3p_poi_price', 'slv_3p_poi_raw_data', 'slv_3p_poi_content',
      'slv_3p_poi_enrichment', 'slv_3p_poi_review_i18n'
  );
```

`slv_3p_poi_policy` không nằm trong hai câu này.

3. Chạy cell seed registry 3P (`seed_registry` + `show_registry`).

4. Dry-run `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`:

```text
dry_run = True
full_reload = True
allow_full_scan = True
max_parallel = 12
max_retries = 1
table_filter =
```

5. Chạy thật, cùng tham số, `dry_run = False`.

6. Chạy lại bước 5.

7. Chạy incremental, `full_reload = False`.

## Kiểm tra kết quả

- Pipeline config 3P: 9 dòng (8 `is_active = 1`, chỉ `slv_3p_poi_policy` là 0). Không còn năm bảng đã bỏ.
- Registry không còn dòng `trg_tbl` của năm bảng đó.
- Registry: 9 bảng, 93 cột, 15 cột tắt.
- Dry-run: không `ConfigError`, 8 bảng, `cast_null` rỗng, `watch` toàn 0, bảng DOC có khối thì `docs_by_table = 33`.
- `full_reload`: `SUCCESS`. Dòng watermark giống snapshot.
- Lần `full_reload` thứ hai: `inserted_rows = 0`.
- Incremental: `SUCCESS` hoặc `NO_DATA`. `last_src_version` không nhỏ hơn snapshot.
- Version Delta của `slv_3p_poi_policy` không đổi. Năm bảng đã `DROP` không còn.

## Chạy lại để kiểm tra idempotency

Bước 6 ở trên. Kết quả mong đợi: không thêm dòng, số dòng và cột nghiệp vụ giống lần `full_reload` đầu.

## Kiểm tra log và watermark

- `ctrl_log_run.run_mode = FULL_RELOAD` cho hai lần chạy thật đầu.
- `ctrl_log_table_run`: 8 dòng mỗi lần.
- `watch` khác 0 thì dừng, không bật lại bảng cũ. Mở task mới.

## Rollback và forward recovery

- Trước `DROP`: `RESTORE` bảng silver về version snapshot nếu cần giữ dữ liệu enrich.
- Sau `DROP`: dữ liệu năm bảng đó không còn. Seed lại registry bản cũ và `is_active = 1` không tạo lại dữ liệu đã xóa.
- `full_reload` không đẩy watermark. Không sửa watermark khi rollback.
- `CastNullError` trên `open_now`: ghi nhận, không đoán kiểu. Sửa registry hoặc chấp nhận `cast_null_policy = WARN` rồi chạy lại.
- Bảng `FAILED`: `full_reload = True` và `table_filter` đúng bảng lỗi.

## Kết quả người dùng ghi nhận

- Chưa chạy.
