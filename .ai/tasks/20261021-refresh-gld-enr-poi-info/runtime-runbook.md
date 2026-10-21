# Hướng dẫn kiểm chứng runtime — 20261021-refresh-gld-enr-poi-info

Trạng thái: `CHỜ CHẠY`

Runbook này chỉ dành cho Fabric DEV. Tài liệu không ghi nhận lần chạy Fabric nào đã diễn ra, và không đánh dấu gate. Mọi kết quả do người dùng chạy và dán vào `evidence/results/` (đường dẫn tương đối từ `.ai/tasks/20261021-refresh-gld-enr-poi-info/`).

## Phạm vi và môi trường

- Môi trường: chỉ dùng Fabric DEV. Workspace id là `<CẦN NGƯỜI DÙNG CUNG CẤP: workspace_id của DEV>`. Nếu workspace đang mở không phải DEV thì dừng ngay, không chạy bước nào.
- Mục tiêu: dựng lại `lh_vv_gold.enr.gld_enr_poi_info` theo hợp đồng mới gồm 40 cột, với nguồn `lh_vv_silver.dbo.slv_poi_entity_non_enrich`. Cách làm theo D-18: DROP bảng trên DEV rồi tạo lại đúng như lúc init.
- Thao tác phá huỷ chỉ có R-3 và R-4:
  - R-3: `DROP TABLE IF EXISTS lh_vv_gold.enr.gld_enr_poi_info`. R-3 chỉ đụng bảng này.
  - R-4: xoá 10 dòng `wm_e__gld_enr_poi_info__*` trong `lh_vv_ctrl.dbo.ctrl_mng_watermark`.
- Những thứ tuyệt đối không đụng:
  - bảng `lh_vv_gold.enr.gld_enr_poi_coordinate` và các dòng `wm_e__gld_enr_poi_coordinate__*`. Không DROP, không DELETE, không UPDATE;
  - dòng khoá `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`. Không bao giờ xoá dòng này;
  - cell `enrddlpy` của `NB_CREATE_DDL`. Không chạy lại cell này ở bất kỳ bước nào.
- Notebook và pipeline liên quan:
  - `NB_CREATE_DDL`: chỉ chạy cell `enrinfopy`;
  - `NB_SETUP_INITIAL_DDL`: chạy với cell tham số `init_param`, giá trị `p_apply = "false"` (chế độ chỉ đọc);
  - `NB_00_ORCHES_SLV_TO_ENR_15P`: chạy tay với tham số ở mục "Các bước thực hiện";
  - pipeline `PL_VV_TRANS_SLV_TO_ENR_15P`. Pipeline này có activity timeout `0.00:32:00`, `retry` 0, `concurrency` 1.
- Giới hạn dữ liệu: ưu tiên số tổng hợp. Mỗi mẫu tối đa 50 dòng. Không dán dữ liệu cá nhân (tên người, số điện thoại, email, nội dung review). Mã `poi_id` và tên cột thì được dán.

## Điều kiện tiên quyết

1. Review round 3 đã PASS (theo author input). Commit của task đã có trên nhánh dùng để sync. Commit hash: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit hash của task trên main>`.
2. Commit đó có đủ:
   - `notebooks/NB_ENR_POI_INFO.ipynb`;
   - `notebooks/NB_CREATE_DDL.ipynb`, có markdown `enrinfomd` và code `enrinfopy` là hai cell cuối;
   - `notebooks/NB_SETUP_INITIAL_DDL.ipynb`;
   - `docs/context/3p-google/mapping_gld_enr_poi_info.md`.
3. Kết quả test local đã được ghi lại. Runbook không khẳng định các test này đã pass:
   - `python -m pytest tests/test_enr_poi_contract.py tests/test_initial_ddl_contract.py -q`
   - `python -m pytest tests -q`
   - `python scripts/vv.py verify 20261021-refresh-gld-enr-poi-info`
4. Người chạy có quyền tạm dừng và bật lại schedule của `PL_VV_TRANS_SLV_TO_ENR_15P`. Tên schedule hoặc trigger: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên schedule/trigger của PL_VV_TRANS_SLV_TO_ENR_15P trên DEV>`.
5. Các bảng mà `enrinfopy` cần đã tồn tại. Kiểm tra chỉ đọc bằng PySpark và dán vào `evidence/results/r0-preconditions.txt`:

```python
for t in ["lh_vv_silver.dbo.slv_poi_entity_non_enrich", "lh_vv_silver.dbo.slv_poi_amenity",
          "lh_vv_silver.dbo.slv_pn_business_service_i18ns"]:
    print(t, spark.catalog.tableExists(t))
print("nb_name" in {f.name.lower() for f in spark.table("lh_vv_ctrl.dbo.ctrl_mng_pipeline_config").schema.fields})
```

   Kết quả cần là 4 dòng `True`. Nếu có dòng `False` thì dừng. Phải chạy `NB_SETUP_POI_ENTITY` / `NB_SETUP_POI_AMENITY` trước, và bước đó nằm ngoài runbook này.
6. Lưu ý về độ tươi dữ liệu: `PL_VV_TRANS_SLV_TO_SLV_1H` hiện đang chạy tay. Vì vậy các cột lấy từ entity chỉ mới bằng lần chạy 1H gần nhất.

## Baseline trước khi chạy

### B-1. Xác nhận DEV và tạm dừng trigger

1. Ghi lại tên workspace và workspace id đang mở, kèm xác nhận đây là DEV.
2. Tạm dừng schedule `<CẦN NGƯỜI DÙNG CUNG CẤP: tên schedule/trigger>` của `PL_VV_TRANS_SLV_TO_ENR_15P`.
3. Ghi thời điểm tạm dừng (UTC).
4. Dán vào `evidence/results/b1-dev-trigger-paused.txt`.

### B-2. Sync notebook từ git

Sync workspace DEV về commit `<CẦN NGƯỜI DÙNG CUNG CẤP: commit hash>`. Kiểm tra trong workspace:
- `NB_CREATE_DDL` có cell `enrinfopy`;
- cell `init_param` của `NB_SETUP_INITIAL_DDL` là `p_apply = "false"`.

Ghi kết quả vào `evidence/results/b2-sync.txt`.

### R-1. Pre-state (bắt buộc lưu trước R-3)

Đây là bản ghi duy nhất của bảng cũ sau khi DROP. Dán toàn bộ kết quả vào `evidence/results/r1-pre-state.txt`. Tất cả câu dưới đây chỉ đọc.

```sql
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_info LIMIT 1;
SELECT count(*), min(created_at), max(created_at) FROM lh_vv_gold.enr.gld_enr_poi_info;
DESCRIBE TABLE lh_vv_gold.enr.gld_enr_poi_info;
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_coordinate LIMIT 1;
SELECT watermark_id, last_src_version, last_src_table_id, status, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e%' AND trg_tbl IN ('gld_enr_poi_info', 'gld_enr_poi_coordinate')
ORDER BY watermark_id;
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P';
SELECT src_tbl, trg_tbl, is_active
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'
ORDER BY trg_tbl, src_tbl;
```

Lấy thứ tự cột và nullability (chỉ đọc):

```python
print([(f.name, f.dataType.simpleString(), f.nullable)
       for f in spark.table("lh_vv_gold.enr.gld_enr_poi_info").schema.fields])
```

So danh sách tên cột theo đúng thứ tự với hai danh sách dưới đây. Cả hai lấy từ `enrinfopy`.

- 23 tên cũ (`OLD_INFO_NAMES`): `poi_id`, `poi_name`, `types`, `subcategory_tags`, `business_sector`, `business_category`, `website_url`, `short_address`, `district`, `destination_name`, `destination_context`, `rating`, `userRatingCount`, `priceLevel`, `opening_hours_text`, `review_json`, `time_to_spend`, `best_time_type`, `best_time_from_month`, `best_time_to_month`, `cost`, `created_at`, `updated_at`.
- 40 cột mới (`INFO_COLS`): `poi_id` STRING NOT NULL, `source_name`, `source_id`, `language_code`, `poi_name`, `poi_name_normalized`, `types`, `operating_status`, `primary_type`, `website_url`, `house_number`, `street`, `ward`, `district`, `city`, `destination_name`, `full_address`, `lat` DOUBLE, `lng` DOUBLE, `business_sector`, `business_category`, `business_category_vi`, `category_group`, `range_low_min` INT, `range_high_min` INT, `avg_range_min` INT, `candidate_best_time_code`, `canonical_candidate`, `rating` DECIMAL(4,2), `user_rating_count` BIGINT, `price_level` INT, `opening_hours_text`, `review_json`, `time_to_spend`, `best_time`, `cost` BIGINT, `cost_vnd`, `service_flag`, `created_at` TIMESTAMP, `updated_at` TIMESTAMP. Những cột không ghi kiểu là STRING. Chỉ `poi_id` là NOT NULL.

Quyết định sau R-1:
- Tên cột trùng đúng 23 tên cũ: đi tiếp R-2, R-3, R-4.
- Đã trùng 40 cột mới: bỏ qua R-3 và R-4, đi thẳng tới bước S-1 (`enrinfopy`). Ghi rõ nhánh này vào `r1-pre-state.txt`.
- Trường hợp còn lại thì dừng và trả về Architect. Trường hợp còn lại bao gồm: bảng không tồn tại, hoặc tên cột không khớp danh sách nào. Không chạy R-3, R-4 hay `enrinfopy`.

### R-2. Kiểm tra khoá trống

```sql
SELECT lock_exec_id, lock_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P';
```

Điều kiện đạt (cần cả hai):
- `lock_exec_id` IS NULL, hoặc `lock_at` cũ hơn 35 phút (= `p_lock_timeout_min` "35");
- Fabric monitor không có run nào của `PL_VV_TRANS_SLV_TO_ENR_15P` hoặc `NB_00_ORCHES_SLV_TO_ENR_15P` đang chạy.

Nếu chưa đạt thì chờ rồi kiểm tra lại. Không xoá và không sửa dòng khoá. Dán kết quả và ảnh chụp trạng thái monitor (dạng chữ) vào `evidence/results/r2-lock-free.txt`.

## Các bước thực hiện

### R-3 và R-4. Reset bảng info trên DEV

Chỉ chạy khi có đủ ba điều kiện sau. Nếu R-1 đã là 40 cột mới thì bỏ qua cả R-3 và R-4.
- R-1 đã được lưu và cho đúng 23 tên cũ;
- R-2 đạt;
- trigger đang tạm dừng.

```sql
-- R-3 (D-18): chỉ bảng info. Không đụng gld_enr_poi_coordinate.
DROP TABLE IF EXISTS lh_vv_gold.enr.gld_enr_poi_info;
-- R-4: xoá cạnh của đúng trg_tbl này (CTRL_TABLES_CONTEXT §4). Không xoá wm_flow__, không xoá cạnh coordinate.
DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN (
    'wm_e__gld_enr_poi_info__slv_3p_poi', 'wm_e__gld_enr_poi_info__slv_3p_poi_address',
    'wm_e__gld_enr_poi_info__slv_3p_poi_contact', 'wm_e__gld_enr_poi_info__slv_3p_poi_rating',
    'wm_e__gld_enr_poi_info__slv_3p_poi_price', 'wm_e__gld_enr_poi_info__slv_3p_poi_opening_hours',
    'wm_e__gld_enr_poi_info__slv_3p_poi_review', 'wm_e__gld_enr_poi_info__slv_poi_entity_non_enrich',
    'wm_e__gld_enr_poi_info__slv_poi_amenity', 'wm_e__gld_enr_poi_info__slv_pn_business_service_i18ns');
```

Chạy R-3 trước, R-4 sau. Cả hai đều chạy lại được. Ghi số dòng DELETE trả về vào `evidence/results/r3-r4-reset.txt`. Sau đó làm ngay P-1 (mục "Kiểm tra kết quả").

### S-1. Chạy cell `enrinfopy` của `NB_CREATE_DDL`

- Chỉ chạy cell `enrinfopy`. Không chạy `enrddlpy` và không chạy cả notebook.
- Kết quả mong đợi khi đi nhánh reset là 2 dòng in:
  - `lh_vv_gold.enr.gld_enr_poi_info: đã tạo theo định nghĩa NB_SETUP_INITIAL_DDL`
  - `lh_vv_gold.enr.gld_enr_poi_info: hợp đồng mới; cạnh active [...]; coordinate không còn cạnh active`
- Nếu cell báo "đang giữ khoá": chờ rồi chạy lại cell. Khoá hết hạn sau 35 phút.
- Nếu cell báo "còn hợp đồng cũ": R-3 chưa chạy, hoặc `enrddlpy` đã bị chạy lại. Làm lại R-1..R-4 rồi chạy lại cell.
- Nếu cell báo "không khớp hợp đồng mới": dừng và trả về Architect.

Dán output vào `evidence/results/s1-enrinfopy.txt`.

### S-2. Chạy `NB_SETUP_INITIAL_DDL` ở chế độ chỉ đọc

- Tham số cell `init_param`: `p_apply = "false"`. Không đổi thành `"true"`.
- Kết quả cần: phần plan không báo lệch schema nào cho `gld_enr_poi_info`.
- Dán phần output liên quan `gld_enr_poi_info` và `PL_VV_TRANS_SLV_TO_ENR_15P` vào `evidence/results/s2-init-plan.txt`. Lệch của bảng khác chỉ ghi nhận, không sửa trong runbook này.

### S-3. `NB_00_ORCHES_SLV_TO_ENR_15P` ở chế độ PLAN

Chạy tay notebook với các tham số sau. Chúng lấy từ cell tham số `5de61e9d` và pipeline JSON. Chỉ `p_mode` khác mặc định.

| Tham số | Giá trị |
|---|---|
| `p_pl_name` | `"PL_VV_TRANS_SLV_TO_ENR_15P"` |
| `p_run_id` | `""` |
| `p_mode` | `"PLAN"` |
| `p_max_parallel` | `"2"` |
| `p_node_timeout_min` | `"15"` |
| `p_dag_timeout_min` | `"25"` |
| `p_lock_timeout_min` | `"35"` |
| `p_force_nodes` | `""` |
| `p_history_limit` | `"1000"` |
| `p_non_data_ops` | `""` |

Dán `RUN_SUMMARY` vào `evidence/results/s3-plan.txt` rồi kiểm tra theo P-5.

### S-4. `NB_00_ORCHES_SLV_TO_ENR_15P` ở chế độ RUN (lần 1)

- Dùng đúng bảng tham số của S-3, chỉ đổi `p_mode = "RUN"`.
- Ghi thời điểm bắt đầu, thời điểm kết thúc và thời lượng.
- Nếu node info hết thời gian (vượt `p_node_timeout_min` "15"): chạy lại tay với `p_node_timeout_min = "<CẦN NGƯỜI DÙNG CUNG CẤP: giá trị lớn hơn 15, không quá 25>"` và giữ nguyên các tham số khác. Ghi lại giá trị đã dùng.

Dán `RUN_SUMMARY` vào `evidence/results/s4-run1.txt`. Sau đó làm P-4, P-6, P-7.

### S-5. RUN lần 2 và bật lại trigger

1. Làm mục "Chạy lại để kiểm tra idempotency" (P-8).
2. Chỉ sau khi RUN lần 2 xong mới bật lại schedule `<CẦN NGƯỜI DÙNG CUNG CẤP: tên schedule/trigger>`.
3. Ghi thời điểm bật lại vào `evidence/results/s5-trigger-resumed.txt`.

## Kiểm tra kết quả

Tất cả câu dưới đây chỉ đọc. Mỗi mẫu tối đa 50 dòng.

### P-0

`evidence/results/r1-pre-state.txt` đã có đủ các phần của R-1 trước khi chạy R-3.

### P-1. Sau R-3 và R-4

Dán vào `evidence/results/p1-after-reset.txt`.

```python
print(spark.catalog.tableExists("lh_vv_gold.enr.gld_enr_poi_info"))  # cần False
```

```sql
SELECT count(*) FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e__gld_enr_poi_info__%';  -- cần 0
SELECT watermark_id, last_src_version, last_src_table_id, status, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e%' AND trg_tbl = 'gld_enr_poi_coordinate' ORDER BY watermark_id;  -- bằng R-1
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P';  -- bằng R-1
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_coordinate LIMIT 1;  -- version bằng R-1
```

### P-2. Sau `enrinfopy`

Dán vào `evidence/results/p2-after-enrinfopy.txt`.

- Output của S-1 có "đã tạo". Nếu đã bỏ qua R-3/R-4 thì chỉ có dòng "hợp đồng mới".
- Schema bằng `INFO_COLS`: chạy lại đoạn PySpark ở R-1. Kết quả cần đúng 40 cột, đúng thứ tự và kiểu đã liệt kê, và chỉ `poi_id` có `nullable = False`.
- Chạy `DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_info;`. Kết quả cần đúng 1 commit `CREATE TABLE`.
- Kiểm tra cạnh theo I6:

```sql
SELECT src_tbl, trg_tbl, is_active, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND trg_tbl IN ('gld_enr_poi_info', 'gld_enr_poi_coordinate')
GROUP BY src_tbl, trg_tbl, is_active
ORDER BY trg_tbl, is_active DESC, src_tbl;
```

Kết quả cần:
- `gld_enr_poi_info` có `is_active = 1`, mỗi nguồn `n = 1`, đúng 7 nguồn: `slv_poi_entity_non_enrich`, `slv_poi_amenity`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_review`, `slv_pn_business_service_i18ns`;
- `gld_enr_poi_info` có `is_active = 0` cho `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`;
- `gld_enr_poi_coordinate` còn đúng 3 dòng (`slv_3p_poi`, `slv_3p_poi_address`, `slv_pn_poi`), tất cả `is_active = 0`.

Phép kiểm tra chạy lại `enrinfopy` nằm ở mục "Chạy lại để kiểm tra idempotency".

### P-3

Output S-2 không báo lệch schema nào cho `gld_enr_poi_info`.

### P-4. Giờ mở cửa partner

Dán vào `evidence/results/p4-partner-hours.txt`.

```sql
SELECT count(*) FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns
WHERE locale = 'vi' AND NOT coalesce(deleted, false)
  AND get_json_object(amentities, '$.policies.operating_hours') IS NOT NULL;
SELECT count(opening_hours_text) FROM lh_vv_gold.enr.gld_enr_poi_info WHERE source_name = 'partner';
```

Hai số phải bằng nhau. Chênh lệch chỉ được phép do các POI partner không có trong spine entity còn sống. Nếu chênh, ghi số chênh lệch, và nếu warn `partner_opening_hours_null` cao thì báo lại người dùng.

### P-5. PLAN

`RUN_SUMMARY` của S-3 có các node `slv_pn_poi`, `gld_enr_poi_review`, `gld_enr_poi_info`, và không có `gld_enr_poi_coordinate`.

### P-6. RUN lần 1

Dán vào `evidence/results/p6-run1-checks.txt`.

- `RUN_SUMMARY`: info và review đều `SUCCESS`, không có node coordinate.
- Lấy `exec_id` của RUN:

```sql
SELECT exec_id, run_mode, status, tbl_total_count, tbl_success_count, tbl_failed_count, started_at, ended_at, duration_ms
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'
ORDER BY started_at DESC LIMIT 5;
```

- Log node info, với `<exec_id>` lấy từ câu trên:

```sql
SELECT trg_tbl, status, entity_rows, trg_version, src_versions_json, qg_json, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND exec_id = '<exec_id>'
ORDER BY trg_tbl;
```

  Trong `qg_json` của `gld_enr_poi_info` cần có:
  - basis `FULL` cho cả 7 role: entity, amenity, rating, price, hours, review, i18n;
  - mọi block check bằng 0: `json_text_null`, `cost_vnd_mismatch`, `google_cols_not_google`, `opening_hours_other_source`;
  - các warn `cost_null`, `time_to_spend_unfixed`, `partner_opening_hours_null`, `review_poi_not_in_entity` được ghi lại nguyên giá trị.
- Số dòng đã ghi bằng số entity còn sống tại version đã ghim. Lấy `<v>` là `v` của `slv_poi_entity_non_enrich` trong `src_versions_json`:

```sql
SELECT count(*) FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <v> WHERE deleted_at IS NULL;
SELECT count(*) FROM lh_vv_gold.enr.gld_enr_poi_info;
SELECT poi_id FROM lh_vv_gold.enr.gld_enr_poi_info GROUP BY poi_id HAVING count(*) > 1 LIMIT 50;  -- cần 0 dòng
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_coordinate LIMIT 1;  -- version bằng R-1 (I10)
SELECT watermark_id, last_src_version, status FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e__gld_enr_poi_info__%' ORDER BY watermark_id;  -- cần đúng 7 dòng, 1 dòng / nguồn active
```

### P-7. Kiểm tra hình dạng dữ liệu

Dán vào `evidence/results/p7-shape.txt`.

```sql
SELECT business_sector, avg_range_min, time_to_spend, count(*) AS n
FROM lh_vv_gold.enr.gld_enr_poi_info GROUP BY 1, 2, 3 ORDER BY 4 DESC LIMIT 50;  -- đối chiếu D-16 (decision.md)
SELECT canonical_candidate, best_time, count(*) AS n
FROM lh_vv_gold.enr.gld_enr_poi_info GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 50;  -- Month a–b / Month a-b -> Tháng a - Tháng b
SELECT cost, cost_vnd FROM lh_vv_gold.enr.gld_enr_poi_info WHERE cost IS NOT NULL LIMIT 20;  -- {label3:"Từ n,nnnđ"}, làm tròn half-up tới nghìn (D-15)
SELECT count(*) FROM lh_vv_gold.enr.gld_enr_poi_info WHERE (cost IS NULL) <> (cost_vnd = 'null');  -- cần 0 (I5)
SELECT count(*) FROM lh_vv_gold.enr.gld_enr_poi_info WHERE cost_vnd IS NULL;  -- theo I5 cần 0
SELECT service_flag, count(*) AS n FROM lh_vv_gold.enr.gld_enr_poi_info GROUP BY 1 ORDER BY 2 DESC LIMIT 20;
SELECT source_name, count(*) AS n, count(opening_hours_text), count(rating), count(review_json), count(price_level)
FROM lh_vv_gold.enr.gld_enr_poi_info GROUP BY 1;  -- I4
```

Theo I4:
- Với nguồn khác `google`, `rating`, `review_json`, `price_level` (và `user_rating_count`) phải đếm được 0.
- `opening_hours_text` chỉ có ở `google` và `partner`.

## Chạy lại để kiểm tra idempotency

### I-1. Chạy lại `enrinfopy` (một phần của P-2)

1. Trước khi chạy lại, ghi version mới nhất:

```sql
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_info LIMIT 1;
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 1;
```

2. Chạy lại riêng cell `enrinfopy`. Output cần chỉ có dòng "hợp đồng mới; cạnh active [...]; coordinate không còn cạnh active", không có "đã tạo".
3. Chạy lại hai câu `DESCRIBE HISTORY`. Version của cả hai bảng phải không đổi.
   - Nếu `ctrl_mng_pipeline_config` có commit mới với 0 dòng thay đổi, ghi nguyên `operationMetrics` và báo Architect. Không tự kết luận PASS.
   - Dòng `wm_flow__` sẽ thay đổi vì cell nhận và nhả khoá. Đó là hành vi đúng.

Dán vào `evidence/results/i1-enrinfopy-rerun.txt`.

### P-8. NB_00 RUN lần 2

Chỉ chạy sau khi P-6 và P-7 đã xong. Giữa RUN 1 và RUN 2 không được có commit mới ở các nguồn.

1. Ghi version nguồn và version đích trước RUN 2 (chỉ đọc):

```python
for t in ["lh_vv_silver.dbo.slv_poi_entity_non_enrich", "lh_vv_silver.dbo.slv_poi_amenity",
          "lh_vv_silver.dbo.slv_3p_poi_rating", "lh_vv_silver.dbo.slv_3p_poi_price",
          "lh_vv_silver.dbo.slv_3p_poi_opening_hours", "lh_vv_silver.dbo.slv_3p_poi_review",
          "lh_vv_silver.dbo.slv_pn_business_service_i18ns", "lh_vv_gold.enr.gld_enr_poi_info"]:
    print(t, spark.sql(f"DESCRIBE HISTORY {t} LIMIT 1").select("version").first()[0])
```

2. Chạy NB_00 với đúng tham số của S-4 (`p_mode = "RUN"`, `p_node_timeout_min` như ở RUN 1).
3. Chạy lại đoạn trên.

Kết quả cần:
- version các nguồn trước và sau bằng nhau. Nếu khác, RUN 2 không chứng minh được gì và phải chạy lại P-8;
- version `gld_enr_poi_info` không đổi;
- `count(*)` bằng kết quả ở P-6;
- node info hoặc không nằm trong số node chạy, hoặc có `entity_rows` 0 và log lib "APPEND 0 dòng -> không ghi".

Dán vào `evidence/results/p8-run2.txt`. Sau đó làm S-5 (bật lại trigger).

## Kiểm tra log và watermark

Dán vào `evidence/results/l1-logs-watermark.txt`.

```sql
SELECT exec_id, run_mode, status, table_filter, tbl_total_count, tbl_success_count, tbl_failed_count, duration_ms, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'
ORDER BY started_at DESC LIMIT 5;
SELECT exec_id, trg_tbl, status, entity_rows, trg_version, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'
ORDER BY started_at DESC LIMIT 20;
SELECT watermark_id, trg_tbl, last_src_version, last_src_table_id, status, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e__gld_enr_poi_%' ORDER BY watermark_id;
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P';
```

Kết quả cần:
- RUN 1 và RUN 2 đều có `run_mode = RUN`. PLAN không ghi dòng log.
- Không có node `FAILED`.
- Có đúng 7 dòng `wm_e__gld_enr_poi_info__*`, mỗi dòng có `last_src_version` khác NULL. `last_src_table_id` của info edge là id hiện tại của nguồn.
- Các dòng `wm_e__gld_enr_poi_coordinate__*` giữ nguyên như R-1 (I10).
- Sau RUN 2, dòng `wm_flow__` có `lock_exec_id` NULL, và `status` là trạng thái của run cuối (`SUCCESS` hoặc `NO_DATA`).

## Rollback và forward recovery

Ưu tiên forward recovery, vì silver vẫn còn nguyên nên lúc nào cũng tạo lại được bản refresh.

| Trạng thái | Cách xử lý |
|---|---|
| Đã sync, chưa R-3: `enrinfopy` báo "hợp đồng cũ" | Làm R-1..R-4 rồi chạy `enrinfopy` |
| Đã R-3, chưa R-4 | Chạy R-4 (chạy lại được) |
| Đã R-3, chưa chạy `enrinfopy`: node info báo `ConfigError` "chưa có bảng đích" | Chạy `enrinfopy` |
| Lỡ chạy lại `enrddlpy` sau R-3 | Làm lại R-1..R-4 rồi chạy `enrinfopy` |
| Bảng đã tạo nhưng bước cạnh lỗi: node info báo `ConfigError` lệch inputs | Chạy lại `enrinfopy` |
| Bảng đã tạo nhưng RUN 1 chưa thành công (bảng rỗng với consumer) | Chạy NB_00 RUN ngay. Giữ trigger tạm dừng tới hết RUN 2 |
| Node info FAILED (QG block, timeout) | Không có gì được ghi và cạnh không tiến. Sửa nguyên nhân rồi chạy lại NB_00. Nếu cần phát lại toàn bộ: `p_force_nodes = "gld_enr_poi_info"`, các tham số khác như S-4 |
| `pk_duplicate` | Sửa ở upstream. Không tự chọn dòng |
| Bảng không mang hợp đồng mới cũng không mang hợp đồng cũ | Dừng, trả về Architect |

Rollback dữ liệu không thực hiện được sau R-3. DROP xoá cả bảng lẫn Delta history, và D-18 chấp nhận điều này trên DEV. R-1 giữ lại số dòng và khoảng ngày của bảng cũ.

Rollback hợp đồng (chỉ DEV, trigger tạm dừng, cần người dùng quyết định trước khi làm):
1. Revert commit của task rồi sync.
2. Làm lại R-2, R-3, R-4.
3. Chạy `enrddlpy` để tạo lại hợp đồng cũ. Đây là trường hợp duy nhất được chạy `enrddlpy`.
4. Bật lại 3 cạnh info cũ:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 1
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND src_schema = 'lh_vv_silver.dbo' AND trg_schema = 'lh_vv_gold.enr'
  AND trg_tbl = 'gld_enr_poi_info' AND src_tbl IN ('slv_3p_poi', 'slv_3p_poi_address', 'slv_3p_poi_contact');
```

   Chỉ khi người dùng muốn lấy lại coordinate (`<CẦN NGƯỜI DÙNG CUNG CẤP: có bật lại coordinate không>`), chạy thêm:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 1
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND src_schema = 'lh_vv_silver.dbo' AND trg_schema = 'lh_vv_gold.enr'
  AND trg_tbl = 'gld_enr_poi_coordinate' AND src_tbl IN ('slv_3p_poi', 'slv_3p_poi_address', 'slv_pn_poi');
```

5. Tắt 3 cạnh mới:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND src_schema = 'lh_vv_silver.dbo' AND trg_schema = 'lh_vv_gold.enr'
  AND trg_tbl = 'gld_enr_poi_info' AND src_tbl IN ('slv_poi_entity_non_enrich', 'slv_poi_amenity', 'slv_pn_business_service_i18ns');
```

6. Chạy NB_00 với tham số như S-4. Logic cũ sẽ phát lại mọi POI (FULL) từ silver hiện tại.
7. Bật lại trigger.

Về git: chỉ cần revert commit của task. `NB_SETUP_INITIAL_DDL` chỉ ảnh hưởng môi trường trống.

Môi trường khác DEV: không áp dụng R-3 nếu chưa có quyết định mới của người dùng. Ở đó `enrinfopy` sẽ từ chối hợp đồng cũ.

## Kết quả người dùng ghi nhận

Người dùng điền cột "Kết quả" bằng `PASS`, `FAIL` hoặc `BỎ QUA (lý do)`, và dán chứng cứ vào đúng file. Trạng thái đầu tài liệu chỉ đổi sau khi người dùng điền xong.

| Mục | Chứng cứ | Kết quả | Ghi chú |
|---|---|---|---|
| R-0 điều kiện tiên quyết | `evidence/results/r0-preconditions.txt` | | |
| B-1 DEV, tạm dừng trigger | `evidence/results/b1-dev-trigger-paused.txt` | | thời điểm UTC: |
| B-2 sync notebook | `evidence/results/b2-sync.txt` | | commit: |
| R-1 / P-0 pre-state (nhánh: 23 cũ / 40 mới) | `evidence/results/r1-pre-state.txt` | | số dòng cũ, min/max `created_at`: |
| R-2 khoá trống | `evidence/results/r2-lock-free.txt` | | |
| R-3, R-4 reset | `evidence/results/r3-r4-reset.txt` | | số dòng DELETE: |
| P-1 sau reset | `evidence/results/p1-after-reset.txt` | | |
| S-1 / P-2 `enrinfopy` | `evidence/results/s1-enrinfopy.txt`, `evidence/results/p2-after-enrinfopy.txt` | | |
| I-1 chạy lại `enrinfopy` | `evidence/results/i1-enrinfopy-rerun.txt` | | |
| S-2 / P-3 init `p_apply = "false"` | `evidence/results/s2-init-plan.txt` | | |
| S-3 / P-5 PLAN | `evidence/results/s3-plan.txt` | | |
| S-4 / P-6 RUN 1 | `evidence/results/s4-run1.txt`, `evidence/results/p6-run1-checks.txt` | | thời lượng; `p_node_timeout_min` đã dùng: |
| P-4 giờ mở cửa partner | `evidence/results/p4-partner-hours.txt` | | hai số đếm: |
| P-7 hình dạng dữ liệu | `evidence/results/p7-shape.txt` | | |
| P-8 RUN 2 | `evidence/results/p8-run2.txt` | | |
| Log và watermark | `evidence/results/l1-logs-watermark.txt` | | |
| S-5 bật lại trigger | `evidence/results/s5-trigger-resumed.txt` | | thời điểm UTC: |

Người chạy: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên người chạy>`. Ngày chạy: `<CẦN NGƯỜI DÙNG CUNG CẤP: ngày chạy>`.
