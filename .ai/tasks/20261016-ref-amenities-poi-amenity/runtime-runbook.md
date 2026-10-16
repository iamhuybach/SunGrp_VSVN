# Runtime runbook: 20261016-ref-amenities-poi-amenity

## Phạm vi và môi trường

Runbook này dành cho điểm dừng 6 trong `Main brief` của `architecture.md`. Người dùng chạy các bước trên Microsoft Fabric DEV trước khi merge.

- Môi trường: Microsoft Fabric DEV. Workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`.
- Lakehouse silver: `lh_vv_silver` (schema `lh_vv_silver.dbo`).
- Lakehouse control: `lh_vv_ctrl` (schema `lh_vv_ctrl.dbo`).
- Pipeline: `PL_VV_TRANS_SLV_TO_SLV_1H`. Pipeline này chưa schedule và được chạy tay. Repo chưa có JSON pipeline, nên runbook chạy trực tiếp các notebook.
- Notebook:
  - `NB_SETUP_POI_AMENITY` tạo `ref_dictionary_amenities` và `slv_poi_amenity`, seed từ điển theo kiểu insert-only, rồi ghi 3 cạnh.
  - `NB_SLV_POI_AMENITY` là node RECOMPUTE/MERGE cho `slv_poi_amenity`.
  - `NB_00_ORCHES_SLV_TO_GLD` là orchestrator. Nó chạy DAG của pipeline, giữ khoá luồng và tiến watermark cạnh.
- Bảng chịu tác động:
  - `lh_vv_silver.dbo.ref_dictionary_amenities` (mới)
  - `lh_vv_silver.dbo.slv_poi_amenity` (mới)
  - `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`: thêm 3 cạnh có `trg_tbl = slv_poi_amenity`
  - `lh_vv_ctrl.dbo.ctrl_mng_watermark`: dòng cạnh `wm_e__slv_poi_amenity__<src_tbl>` và dòng khoá `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`
  - `lh_vv_ctrl.dbo.ctrl_log_table_run`
- Dữ liệu: cờ tiện ích dạng boolean và nhãn tĩnh. Dữ liệu này không có thông tin cá nhân và không có secret. Mọi mẫu kết quả chỉ lấy tối đa 50 dòng và chủ yếu là số đếm tổng hợp.
- Mọi query trong runbook chỉ đọc. Ngoại lệ là các bước chạy notebook (bước 3, 5, các lần chạy lại idempotency) và các lệnh trong mục rollback, vốn chỉ chạy khi người dùng quyết định rollback.

## Điều kiện tiên quyết

1. Luồng `NB_SETUP_POI_ENTITY` đã chạy: `slv_poi_entity` phải có đúng 2 cạnh active trong `PL_VV_TRANS_SLV_TO_SLV_1H`, với `src_tbl` là `slv_3p_poi` và `ref_dictionary_place_type`. Bước 1 kiểm tra điều kiện này.
2. Các bảng `lh_vv_silver.dbo.slv_3p_poi_amenity` và `lh_vv_silver.dbo.slv_poi_entity` đã tồn tại và có dữ liệu. Nếu một input bắt buộc rỗng, node trả FAILED qua `required_inputs` và không soft-delete hàng loạt.
3. Pipeline `PL_VV_TRANS_SLV_TO_SLV_1H` đang nhàn rỗi: không có NB_00 hay node nào chạy tay. Kiểm tra khoá luồng bằng query sau, chỉ đọc:

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H';
```

Đạt khi không có dòng nào, hoặc khi `lock_exec_id` là NULL. Nếu `lock_exec_id` khác NULL, hãy chờ run đó kết thúc rồi mới tiếp tục.

4. Code của nhánh hiện tại (`NB_SETUP_POI_AMENITY`, `NB_SLV_POI_AMENITY`) đã được đưa lên workspace DEV. Cách đồng bộ: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách đồng bộ notebook từ nhánh lên workspace DEV>`.

## Baseline trước khi chạy

Chạy các query sau trước bước 1 và ghi kết quả vào mục `Kết quả người dùng ghi nhận`.

B1. Bảng mới đã tồn tại chưa. Trên DEV, nếu đây là lần chạy đầu thì hai bảng chưa có.

```sql
SHOW TABLES IN lh_vv_silver.dbo LIKE 'ref_dictionary_amenities|slv_poi_amenity';
```

B2. Các cạnh hiện có của `slv_poi_amenity` và `slv_poi_entity`:

```sql
SELECT pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H'
  AND trg_tbl IN ('slv_poi_entity', 'slv_poi_amenity')
ORDER BY trg_tbl, src_tbl
LIMIT 50;
```

B3. Version hiện tại của các input (ghi lại `version` mới nhất):

```sql
DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity LIMIT 5;
```

```sql
DESCRIBE HISTORY lh_vv_silver.dbo.slv_3p_poi_amenity LIMIT 5;
```

B4. Quy mô input, chỉ số đếm:

```sql
SELECT business_sector, count(*) AS n
FROM lh_vv_silver.dbo.slv_poi_entity
GROUP BY business_sector
ORDER BY business_sector
LIMIT 50;
```

```sql
SELECT count(*) AS src_rows,
       count(DISTINCT poi_id) AS pois,
       sum(CASE WHEN source_flags_json IS NULL THEN 1 ELSE 0 END) AS null_json
FROM lh_vv_silver.dbo.slv_3p_poi_amenity;
```

B5. Watermark cạnh của `slv_poi_amenity`. Lần đầu chạy thì không có dòng nào.

```sql
SELECT watermark_id, src_tbl, trg_tbl, status, last_src_version, last_src_table_id,
       watermark_value, last_success_at, last_run_id, error_message, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e__slv_poi_amenity__%'
ORDER BY watermark_id
LIMIT 50;
```

B6. Log đã có của `slv_poi_amenity`. Lần đầu chạy thì không có dòng nào.

```sql
SELECT exec_id, run_id, pl_name, trg_tbl, status, started_at
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl = 'slv_poi_amenity'
ORDER BY started_at DESC
LIMIT 50;
```

## Các bước thực hiện

### Bước 1: Kiểm tra cạnh `slv_poi_entity` (chỉ đọc)

Query này lấy từ cell `c1setupplan` của `NB_SETUP_POI_AMENITY`:

```sql
SELECT count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H'
  AND trg_tbl = 'slv_poi_entity'
  AND is_active = 1;
```

- Đạt khi `n = 2`.
- Nếu `n` khác 2 thì DỪNG. Không chạy setup với `p_apply = "true"`. Khi đó `_write_edges` sẽ báo `ConfigError("slv_poi_amenity: chưa có cạnh slv_poi_entity, chạy NB_SETUP_POI_ENTITY trước")`. Cần xử lý luồng `NB_SETUP_POI_ENTITY` trước.

### Bước 2: Chạy `NB_SETUP_POI_AMENITY` ở chế độ plan

- Tham số (cell `c1setupparam`): `p_apply = "false"`. Đây là giá trị mặc định.
- Exit JSON kỳ vọng:
  - `status = "PLAN"`
  - `google = 78`
  - `partner = 74`
  - `entity_edges_ok = 2`
  - `matchable_hint = null`
  - `planned_edges = ["slv_3p_poi_amenity", "slv_poi_entity", "ref_dictionary_amenities"]`
- `missing_keys` bằng 0 nếu `ref_dictionary_amenities` chưa tồn tại. Nếu bảng đã tồn tại, giá trị này là số khoá seed còn thiếu theo khoá 5 cột.
- Notebook không ghi bảng và không ghi cạnh: nó gọi `notebookutils.notebook.exit` trước cell DDL. Để xác nhận, chạy lại B1 và B2. Kết quả phải không đổi so với baseline.
- Nếu `google` khác 78, `partner` khác 74, hoặc `entity_edges_ok` khác 2 thì DỪNG.

### Bước 3: Chạy `NB_SETUP_POI_AMENITY` ở chế độ apply

- Tham số: `p_apply = "true"`. Đây là tham số duy nhất thay đổi.
- Thứ tự trong notebook:
  1. Validate seed.
  2. Plan.
  3. `CREATE TABLE IF NOT EXISTS` hai bảng và assert schema.
  4. Seed MERGE theo kiểu insert-only.
  5. Kiểm tra trùng, thiếu và drift.
  6. Ghi 3 cạnh.
- Exit JSON kỳ vọng: `status = "SUCCESS"`.
  - `inserted`: số khoá seed chưa có trước MERGE. Nếu từ điển vừa được tạo rỗng thì giá trị là 152 (78 + 74).
  - `drift = 0`.
  - `edges_inserted`: số cạnh chưa có trước MERGE. Nếu B2 chưa có cạnh `slv_poi_amenity` thì giá trị là 3.
- Kiểm tra sau bước 3, chỉ đọc:

```sql
SELECT source_name, business_sector, count(*) AS n, sum(CASE WHEN is_active THEN 1 ELSE 0 END) AS active
FROM lh_vv_silver.dbo.ref_dictionary_amenities
GROUP BY source_name, business_sector
ORDER BY source_name, business_sector
LIMIT 50;
```

```sql
SELECT pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H'
  AND trg_tbl = 'slv_poi_amenity'
ORDER BY src_tbl
LIMIT 50;
```

- Kỳ vọng:
  - Tổng `source_name = google` là 78 và tổng `partner` là 74. Tất cả dòng đều active.
  - Có đúng 3 cạnh: `slv_3p_poi_amenity`, `slv_poi_entity`, `ref_dictionary_amenities`. Cả 3 có `src_schema` và `trg_schema` là `lh_vv_silver.dbo`, `is_active = 1`, `priority = 1`, `load_mode = RECOMPUTE`, `align_path` NULL và `dedup_order` NULL.

- Ghi lại version của `slv_poi_amenity` ngay sau bước 3. Version này là mốc `<v>` cho `RESTORE TABLE` trong mục rollback.

```sql
DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_amenity LIMIT 5;
```

### Bước 4: Chạy `NB_SLV_POI_AMENITY` ở chế độ DRY_RUN

- Tham số (cell `d1amenparam`). Chỉ đổi `p_mode`, mọi tham số khác giữ mặc định:
  - `p_exec_id = ""`
  - `p_run_id = ""`
  - `p_pl_name = ""`
  - `p_trg_fq = ""`
  - `p_pinned_json = ""`
  - `p_mode = "DRY_RUN"`
  - `p_force = "false"`
  - `p_history_limit = "1000"`
- Theo `NODE_MODES` trong `NB_LIB_TRANSFORM_SLV_GLD`, ở chế độ DRY_RUN node vẫn tính kết quả, chạy quality gate và đếm diff, nhưng không tạo và không ghi bảng đích.
- Kỳ vọng:
  - Exit không phải FAILED.
  - Không có `QualityGateError`. Hai lỗi còn lại là điều kiện google trùng khoá, và không có điều kiện google nào khớp được. DataFrame rỗng khi không có amenity khớp là trạng thái hợp lệ (SPARK-001).
  - Ghi lại exit JSON, gồm số diff và các metrics nếu có: `src_rows`, `pois_joined`, `pois_without_entity`, `unparsed_json`, `dict_google_active`, `conditions_matchable`, `conditions_skipped`, `rows`.
- Kiểm tra không ghi đích: chạy lại `DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_amenity LIMIT 5;`. Version mới nhất phải trùng với version đã ghi ở cuối bước 3.

### Bước 5: Chạy `NB_00_ORCHES_SLV_TO_GLD`

- Tham số: chỉ ghi đè `p_pl_name`, các tham số khác giữ mặc định của cell 1.
  - `p_pl_name = "PL_VV_TRANS_SLV_TO_SLV_1H"`
  - `p_run_id = ""`
  - `p_mode = "RUN"`
  - `p_max_parallel = "3"`
  - `p_node_timeout_min = "20"`
  - `p_dag_timeout_min = "45"`
  - `p_lock_timeout_min = "90"`
  - `p_force_nodes = ""`
  - `p_history_limit = "1000"`
  - `p_non_data_ops = ""`
- Hành vi kỳ vọng:
  - `build_dag` xếp `slv_poi_entity` chạy trước `slv_poi_amenity`, vì `slv_poi_entity` là `src_tbl` của một cạnh trong cùng pipeline.
  - Nếu `slv_poi_entity` lỗi hoặc bị bỏ qua, `slv_poi_amenity` sẽ là `SKIPPED`.
  - `slv_poi_amenity` kết thúc ở `SUCCESS`.
  - Node thực hiện một MERGE commit vào `slv_poi_amenity`, rồi append một dòng vào `ctrl_log_table_run`.
  - NB_00 chỉ tiến watermark cạnh sau khi node SUCCESS.
- Ghi lại `exec_id` và `run_id` của lần chạy (lấy từ output NB_00 hoặc từ `ctrl_log_table_run` ở mục `Kiểm tra log và watermark`).

### Bước 6: Chạy 4 runtime check

Xem mục `Kiểm tra kết quả`. Cả bốn check phải trả về 0.

## Kiểm tra kết quả

Mọi query trong mục này chỉ đọc. Mỗi check phải trả về `0`.

Check 1: không có khoá live bị trùng.

```sql
SELECT count(*) AS n
FROM (
    SELECT poi_id, business_sector, amenity_group, amenity_raw
    FROM lh_vv_silver.dbo.slv_poi_amenity
    WHERE deleted_at IS NULL
    GROUP BY 1, 2, 3, 4
    HAVING count(*) > 1
);
```

Check 2: không thiếu dòng dương (`accommodation` với `parkingOptions.freeStreetParking = true`).

```sql
SELECT count(*) AS n
FROM lh_vv_silver.dbo.slv_3p_poi_amenity a
JOIN lh_vv_silver.dbo.slv_poi_entity e USING (poi_id)
LEFT ANTI JOIN (
    SELECT poi_id
    FROM lh_vv_silver.dbo.slv_poi_amenity
    WHERE deleted_at IS NULL
      AND amenity_raw = 'parkingOptions.freeStreetParking = true'
) s USING (poi_id)
WHERE e.business_sector = 'accommodation'
  AND get_json_object(a.source_flags_json, '$.parkingOptions.freeStreetParking') = 'true';
```

Check 3: không có dương tính giả. Check này đếm các dòng live có `parkingOptions.freeParkingLot = true` mà nguồn tương ứng không có cờ đó, hoặc cờ đó là NULL.

```sql
SELECT count(*) AS n
FROM lh_vv_silver.dbo.slv_poi_amenity s
JOIN lh_vv_silver.dbo.slv_3p_poi_amenity a
  ON a.poi_id = s.poi_id
WHERE s.deleted_at IS NULL
  AND s.amenity_raw = 'parkingOptions.freeParkingLot = true'
  AND (get_json_object(a.source_flags_json, '$.parkingOptions.freeParkingLot') IS NULL
       OR get_json_object(a.source_flags_json, '$.parkingOptions.freeParkingLot') <> 'true');
```

Check 4: không có dòng live nào có `amenity_raw` bắt đầu bằng `evChargeOptions.`.

```sql
SELECT count(*) AS n
FROM lh_vv_silver.dbo.slv_poi_amenity
WHERE deleted_at IS NULL
  AND amenity_raw LIKE 'evChargeOptions.%';
```

Mẫu tổng hợp để ghi nhận. Query này chỉ đọc, chỉ lấy số đếm và không lấy `poi_id`:

```sql
SELECT business_sector, amenity_group, amenity_raw,
       sum(CASE WHEN deleted_at IS NULL THEN 1 ELSE 0 END) AS live_rows,
       sum(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END) AS deleted_rows
FROM lh_vv_silver.dbo.slv_poi_amenity
GROUP BY business_sector, amenity_group, amenity_raw
ORDER BY business_sector, amenity_group, amenity_raw
LIMIT 50;
```

Nếu một check khác 0, hãy ghi lại giá trị và chuyển sang mục `Rollback và forward recovery`. Không merge khi còn check khác 0.

## Chạy lại để kiểm tra idempotency

I1. Chạy lại `NB_SETUP_POI_AMENITY` với `p_apply = "true"`.

- Exit JSON kỳ vọng: `status = "SUCCESS"`, `inserted = 0`, `drift = 0`, `edges_inserted = 0`.
- Lý do: anti-join trên khoá 5 cột không còn dòng nào, nên seed MERGE không chèn thêm. Cạnh được MERGE theo (`pl_name`, `src_tbl`, `trg_tbl`) nên không bị nhân đôi.
- Kiểm tra từ điển không bị nhân đôi và `updated_at` không đổi. Query sau phải trả 0 dòng:

```sql
SELECT source_name, business_sector, amenity_group, amenity_raw, amenity, count(*) AS n
FROM lh_vv_silver.dbo.ref_dictionary_amenities
GROUP BY source_name, business_sector, amenity_group, amenity_raw, amenity
HAVING count(*) > 1
LIMIT 50;
```

```sql
SELECT count(*) AS n, min(updated_at) AS min_updated_at, max(updated_at) AS max_updated_at
FROM lh_vv_silver.dbo.ref_dictionary_amenities;
```

Kỳ vọng: `n = 152`, và `min_updated_at`/`max_updated_at` giữ nguyên như sau bước 3.

- Chạy lại query cạnh ở bước 3. Kết quả vẫn phải là đúng 3 cạnh.

I2. Chạy lại `NB_00_ORCHES_SLV_TO_GLD` với đúng bộ tham số của bước 5:

- `p_pl_name = "PL_VV_TRANS_SLV_TO_SLV_1H"`
- `p_run_id = ""`
- `p_mode = "RUN"`
- `p_max_parallel = "3"`
- `p_node_timeout_min = "20"`
- `p_dag_timeout_min = "45"`
- `p_lock_timeout_min = "90"`
- `p_force_nodes = ""`
- `p_history_limit = "1000"`
- `p_non_data_ops = ""`

Kỳ vọng:

- Node diff bằng 0: dòng log mới của `slv_poi_amenity` có `inserted_rows = 0`, `updated_rows = 0` và `deactivated_rows = 0`.
- Lý do: node tính lại toàn bộ từ input đã pin, và MERGE theo `row_hash` cho diff bằng 0 khi input không đổi.
- Nếu NB_00 không đưa node vào kế hoạch vì input không đổi, nên không có dòng log mới, hãy ghi nhận đúng như vậy vào mục kết quả. Runbook này không đổi `p_force_nodes`.

Chạy lại 4 check ở mục `Kiểm tra kết quả`. Cả bốn vẫn phải bằng 0.

## Kiểm tra log và watermark

L1. Log node của `slv_poi_amenity` trong `lh_vv_ctrl.dbo.ctrl_log_table_run`:

```sql
SELECT exec_id, run_id, pl_name, trg_schema, trg_tbl, priority, status,
       entity_rows, inserted_rows, updated_rows, deactivated_rows, trg_version,
       src_versions_json, qg_json, error_message, started_at, ended_at, duration_ms
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl = 'slv_poi_amenity'
ORDER BY started_at DESC
LIMIT 50;
```

Kỳ vọng:

- Lần chạy ở bước 5 có `status = SUCCESS` và `pl_name = PL_VV_TRANS_SLV_TO_SLV_1H`.
- `entity_rows` là số dòng build.
- `qg_json.metrics` có đủ các khoá `src_rows`, `pois_joined`, `pois_without_entity`, `unparsed_json`, `dict_google_active`, `conditions_matchable`, `conditions_skipped`, `rows`.
- `src_versions_json` có đủ 3 input: `slv_3p_poi_amenity`, `slv_poi_entity`, `ref_dictionary_amenities`.
- Lần chạy lại ở I2 có diff bằng 0, như mô tả trong mục idempotency.

L2. Watermark cạnh. Chỉ NB_00 ghi các dòng này, và chỉ tiến watermark khi node SUCCESS hoặc NO_DATA.

```sql
SELECT watermark_id, src_tbl, trg_tbl, watermark_column, status, last_src_version, last_src_table_id,
       watermark_value, last_success_at, last_run_id, error_message, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN (
    'wm_e__slv_poi_amenity__slv_3p_poi_amenity',
    'wm_e__slv_poi_amenity__slv_poi_entity',
    'wm_e__slv_poi_amenity__ref_dictionary_amenities'
)
ORDER BY watermark_id
LIMIT 50;
```

Kỳ vọng sau bước 5:

- Có 3 dòng, mỗi dòng `status = SUCCESS` và `watermark_column = commit_ts`.
- `last_src_version` của mỗi dòng bằng `v` của input đó trong `src_versions_json` của dòng log SUCCESS.
- `last_run_id` khớp với run ở bước 5.
- Bước 4 (DRY_RUN) không tạo và không tiến các dòng này.
- Nếu node FAILED, watermark không tiến. Khi đó chỉ trạng thái và `error_message` thay đổi.

L3. Khoá luồng đã được nhả sau khi chạy:

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H';
```

Kỳ vọng: `lock_exec_id` là NULL, và `status` là trạng thái kết thúc của run, ví dụ `SUCCESS`.

## Rollback và forward recovery

Các lệnh trong mục này có ghi dữ liệu. Chỉ chạy sau khi người dùng quyết định rollback. Runbook này không dùng `DROP TABLE`.

R1. Tắt node. Các cạnh của `slv_poi_entity` không bị ảnh hưởng.

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
SET is_active = 0
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H'
  AND trg_tbl = 'slv_poi_amenity';
```

Kiểm tra lại bằng query cạnh ở bước 3. Cả 3 dòng phải có `is_active = 0`.

R2. Khôi phục output sai về version đã ghi sau bước 3, hoặc về một version tốt đã ghi trước đó:

```sql
RESTORE TABLE lh_vv_silver.dbo.slv_poi_amenity TO VERSION AS OF <CẦN NGƯỜI DÙNG CUNG CẤP: version tốt lấy từ DESCRIBE HISTORY đã ghi ở bước 3 hoặc trước đó>;
```

Thay vì restore, có thể sửa từ điển rồi chạy lại. Vì node tính lại toàn bộ nên kết quả sẽ hội tụ.

R3. Tắt một dòng từ điển sai. Lần chạy kế tiếp sẽ soft-delete các khoá bị ảnh hưởng.

```sql
UPDATE lh_vv_silver.dbo.ref_dictionary_amenities
SET is_active = false
WHERE source_name = '<CẦN NGƯỜI DÙNG CUNG CẤP: source_name>'
  AND business_sector = '<CẦN NGƯỜI DÙNG CUNG CẤP: business_sector>'
  AND amenity_group = '<CẦN NGƯỜI DÙNG CUNG CẤP: amenity_group>'
  AND amenity_raw = '<CẦN NGƯỜI DÙNG CUNG CẤP: amenity_raw>'
  AND amenity = '<CẦN NGƯỜI DÙNG CUNG CẤP: amenity>';
```

Lưu ý: lần chạy setup sau đó sẽ báo `drift` lớn hơn 0 cho khoá này, vì `drift` đếm các khoá seed có `is_active` khác true.

Forward recovery:

1. Chạy lại `NB_SETUP_POI_AMENITY` với `p_apply = "true"`. MERGE cạnh sẽ đưa 3 cạnh về `is_active = 1`, `priority = 1`, `RECOMPUTE`. Đây cũng là cách bật lại node sau R1.
2. Chạy lại `NB_00_ORCHES_SLV_TO_GLD` với đúng tham số của bước 5.
3. Chạy lại 4 check ở mục `Kiểm tra kết quả`.

Xử lý lỗi giữa chừng (theo mục `Partial failure` của architecture):

| Điểm lỗi | Trạng thái | Hành động |
|---|---|---|
| Sau DDL, trước seed | Bảng rỗng, chưa có cạnh | Chạy lại setup với `p_apply = "true"` |
| Sau seed, trước cạnh | Từ điển đã seed, node chưa được nối vào pipeline | Chạy lại setup với `p_apply = "true"` |
| Thiếu cạnh entity | `ConfigError`, không ghi cạnh nào | Chạy `NB_SETUP_POI_ENTITY`, rồi chạy lại setup |
| Node QG lỗi (điều kiện trùng khoá, hoặc không có điều kiện google khớp được) | Bảng đích không bị chạm tới | Sửa từ điển (`is_active`) hoặc kiểm tra dạng `source_flags_json`, rồi chạy lại |
| Không có amenity khớp | DataFrame rỗng đi vào MERGE. RECOMPUTE soft-delete amenity cũ. Metric `rows = 0` | Đây là trạng thái hợp lệ (SPARK-001). Không coi là lỗi |
| Input rỗng | `required_inputs` trả FAILED, không soft-delete hàng loạt | Sửa ở upstream |
| Node FAILED | Watermark không tiến | Chạy lại NB_00. Lần sau sẽ tính lại |
| Crash sau MERGE, trước khi ghi log | Đích đã ghi, log thiếu | Chạy lại NB_00. Diff lần sau bằng 0 |

## Kết quả người dùng ghi nhận

Fabric DEV, 2026-10-16. Không có `poi_id`. Tối đa 50 dòng.

1. Cạnh `slv_poi_entity` active: `n = 2`. Đạt.
2. Setup `p_apply = "false"`: `google = 78`, `partner = 74`, `missing_keys = 0`, `entity_edges_ok = 2`, `status = PLAN`. Đạt.
3. Setup `p_apply = "true"`: `inserted = 152`, `drift = 0`, `edges_inserted = 3`, `status = SUCCESS`. Đạt.
4. Node `p_mode = DRY_RUN`, exec `db75a01d-daef-47f0-8999-9bc43d062f3f`, log ghi `chạy tay`. Diff insert 97, update 0, xoá mềm 0. Exit `SUCCESS`, `trg_version = null`. Đạt: không ghi đích.
5. Node `p_mode = RUN`, exec `e292bb66-949b-44cc-a2b6-68d337c6a000`, log ghi `chạy tay`. Diff insert 97. Exit `SUCCESS`, `trg_version = 1`. Đây là chạy node tay, không phải `NB_00_ORCHES_SLV_TO_GLD` gọi node (`p_exec_id` rỗng).
6. Check 1–4 đều `n = 0`. Đạt. Mẫu live cộng lại 97 dòng, khớp `rows = 97`. Sector trong mẫu: `accommodation`, `attraction`, `f_n_b`.
7. Setup chạy lại: `inserted = 0`, `drift = 0`, `edges_inserted = 0`. Đạt. Lần RUN sau, exec `4b83a2ad-e861-42d3-880c-8110501172c7`, vẫn `chạy tay`: diff 0, bỏ qua MERGE, `trg_version = 1`. Đạt phần idempotency của dữ liệu.
8. `ctrl_log_table_run`: ba dòng SUCCESS. Metrics chung: `conditions_matchable = 27`, `conditions_skipped = 51`, `dict_google_active = 78`, `pois_joined = 57`, `pois_without_entity = 0`, `unparsed_json = 0`, `rows = 97`. Lần chạy lại: `inserted_rows = 0`, `updated_rows = 0`, `deactivated_rows = 0`. Khoá `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`: `status = SUCCESS`, `lock_exec_id` null, `last_run_id = 4b83a2ad-e861-42d3-880c-8110501172c7`.
9. Watermark cạnh `wm_e__slv_poi_amenity__*`: người dùng xác nhận đã pass sau khi chạy `NB_00`.

Kết luận Main: bốn check, idempotency dữ liệu, và watermark cạnh đều đạt. `gates.runtime = pass`.
