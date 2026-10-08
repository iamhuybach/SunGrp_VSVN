# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`.

Chỉ chạy trên Fabric DEV, workspace `68c81db2-fa14-4fee-91f3-a9f31b1ca2c8`. Không chạy PROD. Không copy dữ liệu từ `lh_vv_bronze.ctrl`. Không DROP bảng control cũ hay raw cũ từ notebook.

## Phạm vi và môi trường

- Lakehouse mới: `lh_vv_ctrl`, schema `dbo`, bảy bảng `ctrl_mng_pipeline_config`, `ctrl_mng_watermark`, `ctrl_cfg_schema_registry`, `ctrl_log_run`, `ctrl_log_table_run`, `ctrl_cdc_state`, `ctrl_cdc_reject`.
- Raw 3P: `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`. Partner giữ `partner_raw_data`.
- Notebook: `NB_CREATE_DDL`, `NB_LIB_EXTRACT_RAWDATA`, `NB_LIB_TRANSFORM_SLV_GLD`, `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, `NB_00_ORCHES_SLV_TO_GLD`.
- Pipeline: `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`.
- Quyền workspace của `lh_vv_ctrl` phải bằng `lh_vv_bronze`, vì `ctrl_cdc_reject.after_payload` có thể chứa dữ liệu cá nhân.

## Điều kiện tiên quyết

Dừng trước bước 0 nếu thiếu một điều kiện.

- P1: `lh_vv_ctrl` đã có trong workspace, bật schema. Từ session default lakehouse `lh_vv_bronze`, `SHOW TABLES IN lh_vv_ctrl.dbo` chạy được.
- P2: shortcut `lh_vv_bronze` `Files/_delta_src/brz_3rd_crawler_poi_stream` trỏ tới `Tables/dbo/brz_3rd_crawler_poi_stream`. Thư mục `_delta_log` có file `*.json`. Không xoá file trong shortcut.
- P3: người dùng yêu cầu gỡ lock và cấu hình gold hiện tại. Seed mới không có cạnh `RECOMPUTE`. `NB_00` ném `ConfigError` trước khi tạo `wm_flow__<pl>` và trước khi ghi log. Không có node nào chạy và không có bảng gold nào bị ghi. Chạy SQL ở mục Gold trước khi bật notebook này.

## Baseline trước khi chạy

Chỉ đọc. Ghi số liệu vào bảng kết quả. Không dán payload. Mẫu nếu cần thì tối đa 50 dòng và không lấy cột payload.

### Ghi chú migration — đọc control cũ

- B1: từ `lh_vv_bronze.ctrl.ctrl_mng_watermark` ghi `watermark_id`, `status`, `last_src_version`, `lock_exec_id` của các dòng nguồn. Đếm `ctrl_log_run` có `status = 'RUNNING'`. Kỳ vọng 0. Không `INSERT`, `MERGE`, `UPDATE`, `DELETE` trên `lh_vv_bronze.ctrl`.

```sql
SELECT watermark_id, status, last_src_version, lock_exec_id
FROM lh_vv_bronze.ctrl.ctrl_mng_watermark;

SELECT COUNT(*) AS running_rows
FROM lh_vv_bronze.ctrl.ctrl_log_run
WHERE status = 'RUNNING';
```

- B2: `DESCRIBE HISTORY <bảng> LIMIT 1` cho 23 bảng `slv_pn_*` và 14 bảng `slv_3p_poi_*`. Ghi version. Đây là mốc `RESTORE` nếu người dùng quyết định gỡ dữ liệu raw mới khỏi silver 3P.
- B3: version hiện tại và `COUNT(*)` của `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`.

## Các bước thực hiện

| Bước | Việc | Mốc commit |
|---|---|---|
| 0 | Pause lịch `FL_00`. Dừng trigger tay. Đợi không còn run `FL_00`, extract, hay `NB_00` (monitor pipeline + B1) | C0 đã dừng |
| 1 | Import `NB_CREATE_DDL` bản mới. Chạy từ trên xuống. Đối chiếu R-D1 | C1 control mới đã seed |
| 2 | R-D3, chỉ đọc, so config và registry mới với bản lưu. Lệch 0 hoặc dừng chờ người dùng | — |
| 3 | Deploy `NB_LIB_EXTRACT_RAWDATA` và `NB_LIB_TRANSFORM_SLV_GLD` | C2 điểm chuyển |
| 4 | Deploy hai notebook extract và `NB_00` trong cùng cửa sổ | — |
| 5 | Partner: `dry_run = True, allow_full_scan = True`, rồi chạy thật `allow_full_scan = True, max_retries = 1, max_parallel = 12`. Đối chiếu R-E1 | C3 |
| 6 | 3P: `dry_run = True, allow_full_scan = True, max_parallel = 12`. Xem `cast_null`, `bad_shape`, `langs`, `ignored_detail`. Rồi chạy thật `allow_full_scan = True, max_parallel = 12, max_retries = 1`. Đối chiếu R-E2 | C4 silver 3P phản ánh raw mới |
| 7 | Chạy lại cả hai với `allow_full_scan = False`. Đối chiếu R-E3 | — |
| 8 | Tạo connection Fabric tới SQL analytics endpoint của `lh_vv_ctrl`. Deploy `FL_00` với `conn_lh_vv_ctrl_by_sqlep`, `lh_vv_ctrl`, và `lh_vv_bronze`. Đối chiếu R-FL1 đến R-FL3. Trigger tay một lần. Đối chiếu R-FL4 | C5 |
| 9 | Bật lại lịch `FL_00` | C6 |

Giữ `FL_00` pause đến khi bước 5 và bước 6 đều thành công. Pipeline truyền `allow_full_scan = false`. Watermark còn NULL thì lần đó ném `VersionGapError`.

`src_tbl` của notebook 3P là `brz_3rd_crawler_poi_stream`. Dòng log đầu của mỗi lần extract và của `NB_00` phải in `ctrl=lh_vv_ctrl.dbo` (R-D2).

## Kiểm tra kết quả

- R-D1: bảy bảng có trong `lh_vv_ctrl.dbo`. `DESCRIBE DETAIL` của `ctrl_cdc_state` và `ctrl_cdc_reject` có `partitionColumns = [src_tbl]`. `pipeline_config` 37 dòng (partner 23, 3P 14, `slv_3p_poi_policy` có `is_active = 0`). `watermark` 2 dòng, cả hai `INITIALIZED`, `last_src_version` NULL. Registry partner 301 cột, 3P 182 cột. Kiểm tra D1 trong notebook: 0 dòng trùng. D5: đúng 1 dòng nguồn cho mỗi nguồn active.
- R-D2: dòng log đầu của mỗi lần extract và của `NB_00` in `ctrl=lh_vv_ctrl.dbo`.
- R-D3: so `pipeline_config` và `ctrl_cfg_schema_registry` mới với bản lưu tại control cũ, map tên raw 3P cũ sang `brz_3rd_crawler_poi_stream`. Kỳ vọng lệch 0. Có lệch, kể cả sửa tay `is_active` trên bản lưu, thì dừng rollout và chờ quyết định.

### Ghi chú migration — đối chiếu control cũ cho R-D3

Chỉ `SELECT`. Không ghi vào `lh_vv_bronze.ctrl`.

- R-E1 partner: `ctrl_log_run` status `SUCCESS`, `read_mode = FULL`, khoá atomic và không có WARN về cột khoá. Watermark `status = SUCCESS`, `last_src_version = src_version_to`, `last_src_table_id` có giá trị, lock NULL. `ctrl_cdc_state` chỉ có partition `partner_raw_data`. Cặp `(trg_tbl, entity_key)` trùng = 0.
- R-E2 3P: `SUCCESS`. `read_rows` bằng số dòng `brz_3rd_crawler_poi_stream VERSION AS OF src_version_to`. `valid_rows + ignored_rows + rejected_rows = read_rows`. Watermark `wm_transform_brz_3rd_crawler_poi_stream` đã tiến. `ctrl_cdc_state` và `ctrl_cdc_reject` chỉ có partition `brz_3rd_crawler_poi_stream`. Trùng = 0. Với mỗi `slv_3p_poi_*`, `MAX(_crawled_at)` không nhỏ hơn giá trị thời điểm B2, và join `VERSION AS OF <B2>` đếm 0 dòng có `_crawled_at` thấp hơn cùng khoá.
- R-E3: cả hai lần chạy lại kết thúc `NO_DATA` với `read_mode = VERSION`, hoặc chỉ xử lý commit sau `src_version_to`. `last_src_version` không nhỏ hơn trước. Không có commit mới thì số dòng state không đổi.
- R-FL1: trên SQL endpoint của `lh_vv_ctrl`, câu dưới trả đúng 1 dòng, `src_tbl = partner_raw_data`.

```sql
SELECT DISTINCT src_schema, src_tbl
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00'
  AND is_active = 1
  AND src_tbl = 'partner_raw_data';
```

- R-FL2: output `Lookup_WM` có dòng watermark partner và `last_src_version` khác NULL sau lần FULL. Dòng watermark 3P có thể nằm trong lookup, nhưng ForEach không duyệt nó.
- R-FL3: `GM_DeltaLog` thành công cho `partner_raw_data`. Metadata vẫn đọc `Files/_delta_src/partner_raw_data` trên `lh_vv_bronze`. Shortcut 3P được kiểm tra ở P2, không phải bằng vòng ForEach của `FL_00`.
- R-FL4: lần trigger tay thành công với một vòng. `v_msg` / `v_msg_skip` hiện đúng `last_src_version` của partner. Không có commit partner mới thì vòng đó đi nhánh SKIP và không bật Spark. Commit mới của raw 3P không tạo vòng ForEach và không gọi notebook partner. `ctrl_log_run` chỉ có dòng mới nếu nhánh partner đã chạy notebook. Số dòng control cũ bằng B1.

Activity notebook của `FL_00` vẫn là `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`. Không thêm Switch.

## Chạy lại để kiểm tra idempotency

Bước 7 là lần chạy lại extract. Thêm một lần chạy lại cell seed của `NB_CREATE_DDL` sau R-D1:

- config không tăng dòng (`WHERE NOT EXISTS`);
- watermark vẫn 2 dòng và không bị kéo `last_src_version` về NULL sau khi bước 5 hoặc 6 đã tiến;
- `seed_registry` dùng `replaceWhere` theo từng nguồn, registry 3P vẫn 182 cột.

## Kiểm tra log và watermark

```sql
SELECT watermark_id, status, last_src_version, last_src_table_id, lock_exec_id
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark;

SELECT src_tbl, status, read_mode, COUNT(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_log_run
GROUP BY src_tbl, status, read_mode;

SELECT src_tbl, COUNT(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_cdc_state
GROUP BY src_tbl;
```

`lock_exec_id` NULL khi không còn notebook đang chạy. `last_src_version` không được nhỏ hơn giá trị đã ghi ở lần thành công trước.

## Rollback và forward recovery

### Rollback

Trước khi deploy bản cũ, lập lại hàng rào dừng của bước 0 trên cả hai mặt phẳng:

1. Pause `FL_00`. Dừng trigger tay, runner 3P bên ngoài, extract tay, và `NB_00`.
2. Xác nhận không còn run active trên monitor.
3. `RUNNING` trên `lh_vv_ctrl.dbo.ctrl_log_run` và trên `lh_vv_bronze.ctrl.ctrl_log_run` đều bằng 0.
4. `lock_exec_id` trên watermark của cả hai mặt phẳng đều NULL, hoặc chủ khoá đã chết. Chỉ nhả khoá cũ bằng compare-and-set đúng `lock_exec_id` của chủ đã chết. Không `UPDATE` khoá còn sống.
5. Deploy lại notebook và pipeline từ commit `eedb718` hoặc merge base. Gắn lại `conn_lh_vv_bronze_by_sqlep`.
6. Xác nhận mọi reader và writer đang chạy trỏ về control cũ, rồi mới bật lịch.

- Trước C3, chưa có extract nào ghi trên control mới: sau hàng rào trên, không có tác động dữ liệu. Bảng `lh_vv_ctrl` có thể để nguyên hoặc DROP tay. Không có gì đọc chúng sau khi rollback.
- Sau C3 hoặc C4: deploy lại cùng cách đó. Watermark partner cũ tiếp tục từ `last_src_version` trước cutover. Đọc lại sự kiện đã áp ở control mới cho cùng kết quả latest-theo-entity. Đường 3P cũ đọc `poi_raw_event` đang dừng. Dòng silver 3P đã ghi từ raw mới không bị bản cũ kéo lùi. `ctrl_cdc_state` cũ không đổi. Silver 3P giữ các document đã áp từ `brz_3rd_crawler_poi_stream`.
- Gỡ dữ liệu raw mới khỏi silver 3P chỉ bằng `RESTORE TABLE ... TO VERSION AS OF <B2>` trên 14 bảng `slv_3p_poi_*`. Thao tác này phá các ghi sau mốc B2. Chỉ người dùng quyết định. Không tự chạy. Sau đó phải tính lại gold.
- Rollback không sửa `lh_vv_bronze.ctrl`. Ngoại lệ duy nhất là mục Gold bên dưới, do người dùng yêu cầu ngày 2026-10-08.

### Gold

Người dùng yêu cầu bỏ lock và cấu hình gold đang có. Không xoá watermark extract `wm_transform_%`. Không xoá năm cột gold-log. Chạy khi không còn `NB_00` active. Câu trên `lh_vv_bronze.ctrl` là ghi chú migration, chỉ gồm đúng các `DELETE` này.

```sql
DELETE FROM lh_vv_bronze.ctrl.ctrl_mng_pipeline_config
WHERE upper(trim(load_mode)) = 'RECOMPUTE';

DELETE FROM lh_vv_bronze.ctrl.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_flow__%'
   OR watermark_id LIKE 'wm_e__%';

DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE upper(trim(load_mode)) = 'RECOMPUTE';

DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_flow__%'
   OR watermark_id LIKE 'wm_e__%';
```

Sau đó `NB_00` thiếu cạnh thì `ConfigError` và không tạo khoá, không ghi log. Task sau muốn chạy gold thì seed lại cạnh `RECOMPUTE` từ literal trong repo.

### Forward recovery

- Sai dòng seed, trước bước 5: được DROP tay bảy bảng `lh_vv_ctrl.dbo` bằng SQL trong runbook này, không thêm cell DROP vào notebook, rồi chạy lại `NB_CREATE_DDL`.

```sql
DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_cdc_reject;
DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_cdc_state;
DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_log_table_run;
DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_log_run;
DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_cfg_schema_registry;
DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_mng_watermark;
DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_mng_pipeline_config;
```

- Sai dòng seed, sau bước 5: không DROP. `UPDATE` hoặc `DELETE` đúng khoá logic trên `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` hoặc `ctrl_mng_watermark`. Registry thì sửa `TABLE_CONFIGS*` rồi chạy lại `seed_registry` (`replaceWhere` theo nguồn).
- Extract lỗi: watermark còn NULL thì mọi lần chạy lại phải `allow_full_scan = True`. `VersionGapError` không ghi silver và không đổi watermark. `CastNullError`, `bad_shape`, hoặc `source_name` lạ thì xem bằng `dry_run = True`, sửa registry hoặc tham số, rồi chạy lại với `allow_full_scan = True`.
- Partner FULL xong mà 3P FULL lỗi: giữ `FL_00` pause, sửa rồi chạy lại 3P với `allow_full_scan = True`.
- `FL_00` chỉ có vòng `partner_raw_data`. Lỗi pre-check hoặc vòng partner thì sửa binding `lh_vv_ctrl` hoặc shortcut `Files/_delta_src/partner_raw_data`, rồi trigger lại. Shortcut 3P thuộc notebook 3P chạy tay, không thuộc `FL_00`.

## Kết quả người dùng ghi nhận

| Mốc | Kết quả | exec_id | Ghi chú |
|---|---|---|---|
| P1–P3 | | | |
| B1–B3 | | | |
| R-D1 | | | |
| R-D2 | | | |
| R-D3 | | | |
| R-E1 | | | |
| R-E2 | | | |
| R-E3 | | | |
| R-FL1–R-FL4 | | | |
