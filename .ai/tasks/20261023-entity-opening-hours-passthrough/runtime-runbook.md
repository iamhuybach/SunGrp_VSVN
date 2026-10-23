# Runtime runbook: 20261023-entity-opening-hours-passthrough

## Phạm vi và môi trường

- Môi trường: Fabric DEV. Workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`.
- Thay đổi được triển khai:
  - `NB_SLV_POI_ENTITY_NON_ENRICH` (cell `b1entitybuild`) tự tính `opening_hours_text`. Dòng google lấy `periods_json` của `slv_3p_poi_opening_hours`. Dòng partner lấy `$.policies.operating_hours` từ `amentities` của bản i18n `vi`. Nguồn khác để NULL. Node có thêm input `hours`.
  - `NB_ENR_POI_INFO` (cell `36415d3b`) chỉ truyền thẳng `e.opening_hours_text` và chặn khi gặp `opening_hours_text_mismatch`.
  - `NB_CREATE_DDL` có cell `ohpasspy`. Cell này `ALTER` để thêm cột `opening_hours_text STRING` (cho phép NULL) vào `lh_vv_silver.dbo.slv_poi_entity_non_enrich` nếu cột chưa có. Sau đó cell chạy một MERGE (một commit) trên `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` để:
    - thêm cạnh RECOMPUTE `slv_3p_poi_opening_hours -> slv_poi_entity_non_enrich`;
    - đặt cạnh `slv_3p_poi_opening_hours -> gld_enr_poi_info` về `is_active = 0`. Dòng này và watermark của nó được giữ lại.
- Pipeline bị ảnh hưởng: `PL_VV_TRANS_SLV_TO_ENR_15P`, orchestrator `NB_00_ORCHES_SLV_TO_ENR_15P`.
- Lakehouse mặc định của `NB_CREATE_DDL`: `lh_vv_bronze`. Không đổi lakehouse gắn sẵn của `NB_00_ORCHES_SLV_TO_ENR_15P`.
- Bảng liên quan:
  - `lh_vv_silver.dbo.slv_poi_entity_non_enrich`
  - `lh_vv_silver.dbo.slv_3p_poi_opening_hours`
  - `lh_vv_silver.dbo.slv_pn_business_service_i18ns`
  - `lh_vv_gold.enr.gld_enr_poi_info`
  - `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`
  - `lh_vv_ctrl.dbo.ctrl_mng_watermark`
  - `lh_vv_ctrl.dbo.ctrl_log_table_run`
- Rủi ro đã được chấp nhận (decision.md D-OH-07, 2026-10-23): `STATE-001`, `SQL-001`, `SQL-002`. Vòng review 3 không chạy. Điều kiện đi kèm là tắt trigger `PL_VV_TRANS_SLV_TO_ENR_15P` trước khi chạy `ohpasspy` và chỉ bật lại sau lần chạy orchestrator thứ hai.
- Những việc không làm trong runbook này:
  - Không chạy riêng `NB_SLV_POI_ENTITY_NON_ENRICH` hoặc `NB_ENR_POI_INFO`.
  - Không chạy lại các cell `enrddlpy`, `enrinfopy`, `mvpoipy` của `NB_CREATE_DDL`.
  - Không chạy `NB_SETUP_INITIAL_DDL` trên DEV. Notebook này chỉ dùng cho môi trường mới.
  - Không sửa tay `ctrl_mng_pipeline_config` hoặc `ctrl_mng_watermark` ngoài câu lệnh rollback ở mục cuối.
- Mọi truy vấn kiểm tra đều chỉ đọc. Mẫu kết quả tối đa 50 dòng và chỉ chứa `poi_id`, tên bảng, trạng thái, số đếm hoặc giá trị giờ mở cửa, không chứa dữ liệu cá nhân. Thời gian trong `ctrl_log_table_run` là UTC.

## Điều kiện tiên quyết

1. Code đã được merge vào `main` và đẩy lên remote mà workspace DEV đồng bộ. Commit: `<CẦN NGƯỜI DÙNG CUNG CẤP: hash commit đã merge>`. Khi runbook này được viết, các file `notebooks/NB_CREATE_DDL.ipynb`, `notebooks/NB_ENR_POI_INFO.ipynb`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb`, `docs/context/01_DATA_MODEL.md` và ba file test vẫn đang ở trạng thái sửa nhưng chưa commit.
2. Test local đều pass trên đúng commit đó:
   - `python -m pytest tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py tests/test_initial_ddl_contract.py -q`
   - `python -m pytest -q`
3. Người chạy có quyền tắt và bật trigger của `PL_VV_TRANS_SLV_TO_ENR_15P`. Cách tắt và tên item hoặc schedule: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên item / schedule trigger của PL_VV_TRANS_SLV_TO_ENR_15P trong DEV và cách tắt/bật>`.
   - Nếu không thể tắt trigger, ghi rõ điều đó: `<CẦN NGƯỜI DÙNG CUNG CẤP: xác nhận không thể tắt trigger>`. Khi đó, đồng bộ notebook, chạy `ohpasspy` và lần chạy orchestrator thứ nhất phải xong trong cùng một khoảng trống 15 phút giữa hai tick.
   - Lúc này rủi ro `STATE-001` không còn được giảm nhẹ. Nếu một tick rơi vào giữa chừng, tick đó sẽ fail an toàn (`ConfigError` hoặc `SKIPPED_CONCURRENT`, xem mục Rollback).
4. Cách đồng bộ notebook vào workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách sync (Fabric Git integration / deploy) cho workspace DEV>`.
5. `ctrl_mng_pipeline_config` đã có cột `nb_name`, tức `enrddlpy` đã chạy trước đây. Nếu chưa có cột này, `ohpasspy` sẽ dừng với thông báo `chưa có cột nb_name: chạy enrddlpy trước`. Khi đó dừng runbook và hỏi người dùng. Không tự chạy `enrddlpy`.

## Baseline trước khi chạy

Làm bước 1 (tắt trigger) ở mục `Các bước thực hiện` trước, rồi chạy các truy vấn dưới đây. Mọi truy vấn đều chỉ đọc. Ghi kết quả vào mục `Kết quả người dùng ghi nhận`.

B1. Ghi `V0`, version mới nhất của gold:

```sql
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_info LIMIT 1
```

Ghi `version` thành `V0` và `timestamp` thành `T_V0`.

B2. Ghi version hiện tại của bảng ctrl và bảng entity. `C0` dùng cho rollback và R6:

```sql
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 1
```

```sql
DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity_non_enrich LIMIT 1
```

Ghi `C0` và `E0`.

B3. Kiểm tra không còn run nào đang giữ khoá luồng:

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, error_message, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P'
```

Kỳ vọng: `lock_exec_id` là NULL. Nếu khoá đang có giá trị, chờ run đó kết thúc. Không xoá khoá bằng tay.

B4. Tick gần nhất của luồng:

```sql
SELECT exec_id, min(started_at) AS started_at, max(ended_at) AS ended_at, count(*) AS nodes
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'
GROUP BY exec_id
ORDER BY started_at DESC
LIMIT 5
```

Ghi `exec_id` mới nhất thành `EXEC_BASE`. Sau khi tắt trigger, không được có exec nào mới hơn `EXEC_BASE` cho tới bước 5.

B5. Các cạnh của entity và gold. Đây là điều kiện mà `ohpasspy` sẽ kiểm tra trước khi ghi:

```sql
SELECT trg_schema, trg_tbl, src_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND src_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_poi_entity_non_enrich', 'gld_enr_poi_info')
GROUP BY trg_schema, trg_tbl, src_tbl, is_active, priority, load_mode, nb_name
ORDER BY trg_tbl, src_tbl
```

Kỳ vọng:

- Entity (`trg_schema = lh_vv_silver.dbo`):
  - Có đúng 6 cạnh active, mỗi cạnh 1 dòng: `slv_3p_poi`, `slv_3p_poi_address`, `ref_dictionary_place_type`, `slv_pn_business_services`, `slv_pn_business_service_i18ns`, `slv_3p_poi_contact`.
  - Các cạnh này cùng `priority`, `load_mode = RECOMPUTE` và cùng `nb_name`.
  - Chưa có cạnh `slv_3p_poi_opening_hours`. Trường hợp duy nhất được chấp nhận ngoài ra là cạnh này đã tồn tại với đúng 1 dòng `is_active = 1`.
- Gold (`trg_schema = lh_vv_gold.enr`):
  - Cạnh `slv_3p_poi_opening_hours` có đúng 1 dòng. Trước patch, giá trị kỳ vọng là `is_active = 1`.
  - Các cạnh active còn lại đúng là: `slv_poi_entity_non_enrich`, `slv_poi_amenity`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_review`, `slv_pn_business_service_i18ns`, `slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination`, mỗi cạnh 1 dòng.
  - Lưu ý: danh sách này lấy từ `INFO_KEEP` của `ohpasspy`. Danh sách gold trong `docs/context/CTRL_TABLES_CONTEXT.md` §3 khác danh sách này (thiếu hai bảng `slv_enr_poi_*`). Cứ theo kết quả truy vấn. Nếu không khớp `INFO_KEEP`, cell sẽ dừng trước khi ghi.

Nếu có bất kỳ điểm nào lệch, dừng và báo người dùng.

B6. Schema của hai bảng silver:

```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_3p_poi_opening_hours
```

```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich
```

Kỳ vọng: `periods_json` có kiểu `string`. Entity hoặc chưa có `opening_hours_text`, hoặc đã có với kiểu `string` (cho phép NULL).

B7. Các watermark liên quan:

```sql
SELECT watermark_id, src_tbl, trg_tbl, status, last_src_version, last_src_table_id, last_success_at,
       last_run_id, error_message, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE trg_tbl IN ('slv_poi_entity_non_enrich', 'gld_enr_poi_info') AND watermark_id LIKE 'wm_e%'
ORDER BY trg_tbl, src_tbl
LIMIT 50
```

Kỳ vọng:

- Chưa có `wm_e__slv_poi_entity_non_enrich__slv_3p_poi_opening_hours`. Nếu dòng này đã có, nó phải có `src_schema = lh_vv_silver.dbo`, `src_tbl = slv_3p_poi_opening_hours`, `trg_schema = lh_vv_silver.dbo`, `trg_tbl = slv_poi_entity_non_enrich`.
- Ghi lại toàn bộ dòng `wm_e__gld_enr_poi_info__slv_3p_poi_opening_hours` thành `WM_GOLD_HOURS_0`. Dòng này phải giữ nguyên trong suốt quá trình chạy.

B8. Số đếm tham chiếu của gold tại `V0`. Kết quả chỉ để ghi nhận:

```sql
SELECT count(*) AS rows_v0, count(DISTINCT poi_id) AS poi_v0, count(opening_hours_text) AS with_hours_v0
FROM lh_vv_gold.enr.gld_enr_poi_info VERSION AS OF <V0>
```

## Các bước thực hiện

1. **Tắt trigger.**
   - Tắt trigger của `PL_VV_TRANS_SLV_TO_ENR_15P` theo `<CẦN NGƯỜI DÙNG CUNG CẤP: tên item / schedule trigger và cách tắt>`. Ghi thời điểm tắt thành `T_PAUSE`.
   - Trên Fabric Monitor, xác nhận không có run nào của pipeline này đang chạy. Chạy lại B3: `lock_exec_id` phải là NULL.
   - Nếu không tắt được trigger, ghi điều đó vào kết quả. Khi đó các bước 3, 4 và 5 phải xong trong một khoảng trống 15 phút, tính từ khi tick gần nhất ở B4 kết thúc.
2. **Baseline.** Chạy B1–B8 và ghi `V0`, `C0`, `E0`, `EXEC_BASE`, `WM_GOLD_HOURS_0`.
3. **Đồng bộ notebook.**
   - Đồng bộ workspace DEV về commit `<CẦN NGƯỜI DÙNG CUNG CẤP: hash commit>` theo `<CẦN NGƯỜI DÙNG CUNG CẤP: cách sync>`.
   - Mở và đọc trong workspace (không chạy) để xác nhận đã có bản 23/10:
     - Cell `b1entitybuild` của `NB_SLV_POI_ENTITY_NON_ENRICH` có `HOURS_COLS = ("opening_hours_text",)` và input `"hours": "slv_3p_poi_opening_hours"`.
     - Cell `36415d3b` của `NB_ENR_POI_INFO` có dòng `[SỬA 23/10]` và không còn `_partner_hours`.
     - Hai cell cuối của `NB_CREATE_DDL` là `ohpassmd` và `ohpasspy`.
   - Từ lúc này đến khi bước 4 xong, mọi tick chạy vào đều fail với `ConfigError` trước khi ghi. Vì vậy trigger phải đang tắt.
4. **Chạy `ohpasspy`.**
   - Mở `NB_CREATE_DDL` với lakehouse mặc định `lh_vv_bronze`. Chỉ chạy cell `ohpasspy`. Không chạy cell nào khác, đặc biệt không chạy `enrddlpy`, `enrinfopy`, `mvpoipy`. Cell này không có parameter.
   - Cell thành công khi in ra đúng một dòng như sau:

     ```
     lh_vv_silver.dbo.slv_poi_entity_non_enrich.opening_hours_text string NULL; cạnh slv_poi_entity_non_enrich ['ref_dictionary_place_type', 'slv_3p_poi', 'slv_3p_poi_address', 'slv_3p_poi_contact', 'slv_3p_poi_opening_hours', 'slv_pn_business_service_i18ns', 'slv_pn_business_services']; cạnh gld_enr_poi_info ['slv_3p_poi_price', 'slv_3p_poi_rating', 'slv_3p_poi_review', 'slv_enr_poi_destination', 'slv_enr_poi_info_multi_lang', 'slv_pn_business_service_i18ns', 'slv_poi_amenity', 'slv_poi_entity_non_enrich']
     ```

   - Chép nguyên văn dòng in ra vào mục kết quả.
   - Xử lý khi cell báo lỗi:
     - `Luồng PL_VV_TRANS_SLV_TO_ENR_15P đang giữ khoá (...)`: có run khác đang chạy. Chờ run đó xong rồi chạy lại cell. Không xoá khoá.
     - `Dừng trước khi ghi: ...`: cell chưa ghi gì vào entity hoặc ctrl (chỉ dòng khoá `wm_flow__` được ghi `FAILED`). Dừng, chép lỗi và báo người dùng.
     - `Luồng ... mất khoá trước khi ghi` hoặc `Sau khi ghi: ...`: dừng và làm theo mục `Rollback và forward recovery`.
5. **Chạy orchestrator lần 1.**
   - Ghi thời điểm bắt đầu (UTC) thành `T_RUN1`.
   - Chạy notebook `NB_00_ORCHES_SLV_TO_ENR_15P`, cell 1 giữ đúng các giá trị sau:

     ```
     p_pl_name = "PL_VV_TRANS_SLV_TO_ENR_15P"
     p_run_id = ""
     p_mode = "RUN"
     p_max_parallel = "2"
     p_node_timeout_min = "15"
     p_dag_timeout_min = "25"
     p_lock_timeout_min = "35"
     p_force_nodes = ""
     p_history_limit = "1000"
     p_non_data_ops = ""
     ```

   - Chờ notebook kết thúc. Tìm `EXEC_1` bằng truy vấn sau. Kỳ vọng có đúng 1 exec vì trigger đang tắt:

     ```sql
     SELECT exec_id, run_id, min(started_at) AS started_at, max(ended_at) AS ended_at, count(*) AS nodes
     FROM lh_vv_ctrl.dbo.ctrl_log_table_run
     WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND started_at >= TIMESTAMP '<T_RUN1>'
     GROUP BY exec_id, run_id
     ORDER BY started_at DESC
     LIMIT 5
     ```

6. **Kiểm tra R1–R5** theo mục `Kiểm tra kết quả`. Đây là điểm dừng lấy bằng chứng. Nếu có probe fail, không chạy tiếp mà chuyển sang mục Rollback.
7. **Chạy orchestrator lần 2 và chạy lại `ohpasspy`.** Làm theo mục `Chạy lại để kiểm tra idempotency` (R6).
8. **Bật lại trigger.**
   - Bật trigger theo `<CẦN NGƯỜI DÙNG CUNG CẤP: cách bật trigger>`. Ghi thời điểm thành `T_RESUME`.
   - Theo dõi R7 ở các tick sau.

## Kiểm tra kết quả

Chạy các probe sau ngay khi bước 5 xong. Tất cả đều chỉ đọc.

**R1. Cột và cạnh.**

```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich
```

Kỳ vọng: có `opening_hours_text` với kiểu `string`, cho phép NULL. Cột này nằm cuối bảng nếu được `ALTER` thêm vào.

```sql
SELECT id, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND src_schema = 'lh_vv_silver.dbo'
  AND src_tbl = 'slv_3p_poi_opening_hours'
ORDER BY trg_tbl
```

Kỳ vọng: có đúng 2 dòng.

- `slv_poi_entity_non_enrich`: `is_active = 1`, `load_mode = RECOMPUTE`, `priority` và `nb_name` giống các cạnh entity khác ở B5.
- `gld_enr_poi_info`: `is_active = 0`.

**R2. Log của exec 1.**

```sql
SELECT trg_tbl, status, priority, entity_rows, inserted_rows, updated_rows, deactivated_rows, trg_version,
       get_json_object(qg_json, '$.inbox') AS inbox,
       get_json_object(qg_json, '$.blocks') AS blocks,
       get_json_object(qg_json, '$.warns') AS warns,
       get_json_object(qg_json, '$.metrics.opening_hours_text_mismatch') AS oh_mismatch,
       get_json_object(qg_json, '$.metrics.google_with_hours') AS google_with_hours,
       get_json_object(qg_json, '$.metrics.partner_with_hours') AS partner_with_hours,
       substr(error_message, 1, 500) AS error_message
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id = '<EXEC_1>'
ORDER BY priority, trg_tbl
LIMIT 50
```

Kỳ vọng:

- `slv_poi_entity_non_enrich`:
  - `status = SUCCESS`.
  - Trong `inbox`, `slv_3p_poi_opening_hours` có lý do `NEW_EDGE`.
  - `blocks` có `opening_hours_other_source = 0`. `warns` có `partner_opening_hours_null` (giá trị chỉ để ghi nhận).
  - `google_with_hours` và `partner_with_hours` có giá trị.
  - MERGE cập nhật toàn bộ dòng vì `row_hash` mới. Ghi `trg_version` thành `E1`.
- `slv_poi_amenity`: `SUCCESS` hoặc `NO_DATA`.
- `gld_enr_poi_info`:
  - `status = SUCCESS` và `oh_mismatch = 0`.
  - `inbox` không còn `slv_3p_poi_opening_hours`.
  - `inserted_rows` là lượng append một lần cho các key có `opening_hours_text` khác NULL. Chỉ ghi nhận số này.
- Các node khác của pipeline: ghi nhận trạng thái. Chúng không thuộc tiêu chí nghiệm thu.
- Nếu `get_json_object` trả NULL vì cấu trúc `qg_json` khác, đọc `substr(qg_json, 1, 4000)` của đúng dòng đó.

**R3. Gold bằng silver (I1).** Kỳ vọng `0`:

```sql
WITH g AS (SELECT poi_id, opening_hours_text,
                  row_number() OVER (PARTITION BY poi_id ORDER BY updated_at DESC, created_at DESC) AS rn
           FROM lh_vv_gold.enr.gld_enr_poi_info)
SELECT count(*) FROM g JOIN lh_vv_silver.dbo.slv_poi_entity_non_enrich e
  ON e.poi_id = g.poi_id AND e.deleted_at IS NULL
WHERE g.rn = 1 AND NOT (g.opening_hours_text <=> e.opening_hours_text)
```

Nếu kết quả khác 0, lấy mẫu (tối đa 50 dòng):

```sql
WITH g AS (SELECT poi_id, opening_hours_text,
                  row_number() OVER (PARTITION BY poi_id ORDER BY updated_at DESC, created_at DESC) AS rn
           FROM lh_vv_gold.enr.gld_enr_poi_info)
SELECT g.poi_id, e.source_name, g.opening_hours_text AS gold_value, e.opening_hours_text AS silver_value
FROM g JOIN lh_vv_silver.dbo.slv_poi_entity_non_enrich e
  ON e.poi_id = g.poi_id AND e.deleted_at IS NULL
WHERE g.rn = 1 AND NOT (g.opening_hours_text <=> e.opening_hours_text)
LIMIT 50
```

**R4. Giá trị gold giữ nguyên so với `V0`.** Kỳ vọng `0`:

```sql
WITH o AS (SELECT poi_id, opening_hours_text,
                  row_number() OVER (PARTITION BY poi_id ORDER BY updated_at DESC, created_at DESC) AS rn
           FROM lh_vv_gold.enr.gld_enr_poi_info VERSION AS OF <V0>),
     n AS (SELECT poi_id, opening_hours_text,
                  row_number() OVER (PARTITION BY poi_id ORDER BY updated_at DESC, created_at DESC) AS rn
           FROM lh_vv_gold.enr.gld_enr_poi_info)
SELECT count(*) FROM o JOIN n ON o.poi_id = n.poi_id
WHERE o.rn = 1 AND n.rn = 1 AND NOT (o.opening_hours_text <=> n.opening_hours_text)
```

Nếu kết quả khác 0, lấy mẫu bằng cách đổi `SELECT count(*)` thành `SELECT o.poi_id, o.opening_hours_text AS v0_value, n.opening_hours_text AS new_value` và thêm `LIMIT 50`.

**R5. Công thức tương đương (I2).**

Bước 1: lấy version các input mà entity đã đọc trong exec 1.

```sql
SELECT trg_version,
       get_json_object(src_versions_json, '$.slv_3p_poi_opening_hours.v') AS v_hours,
       get_json_object(src_versions_json, '$.slv_pn_business_service_i18ns.v') AS v_i18n,
       substr(src_versions_json, 1, 4000) AS src_versions_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id = '<EXEC_1>' AND trg_tbl = 'slv_poi_entity_non_enrich'
```

Ghi `v_hours`, `v_i18n` và `E1` (`trg_version`). Nếu hai cột `v_*` là NULL vì khoá trong JSON có dạng khác, đọc thẳng `v` của đúng bảng trong `src_versions_json`.

Bước 2: so sánh dòng google. Kỳ vọng `0`:

```sql
SELECT count(*)
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <E1> e
LEFT JOIN lh_vv_silver.dbo.slv_3p_poi_opening_hours VERSION AS OF <v_hours> oh ON oh.poi_id = e.poi_id
WHERE e.deleted_at IS NULL AND lower(trim(e.source_name)) = 'google'
  AND NOT (e.opening_hours_text <=> oh.periods_json)
```

Bước 3: so sánh dòng partner. Kỳ vọng `0`:

```sql
WITH i AS (SELECT business_service_id,
                  get_json_object(amentities, '$.policies.operating_hours') AS hours
           FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns VERSION AS OF <v_i18n>
           WHERE locale = 'vi' AND NOT coalesce(deleted, false))
SELECT count(*)
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <E1> e
LEFT JOIN i ON i.business_service_id = e.source_id
WHERE e.deleted_at IS NULL AND lower(trim(e.source_name)) = 'partner'
  AND NOT (e.opening_hours_text <=> i.hours)
```

Bước 4: dòng thuộc nguồn khác. Kỳ vọng `0`, khớp block `opening_hours_other_source`:

```sql
SELECT count(*)
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <E1>
WHERE deleted_at IS NULL
  AND coalesce(lower(trim(source_name)), '') NOT IN ('google', 'partner')
  AND opening_hours_text IS NOT NULL
```

Nếu bất kỳ count nào khác 0, lấy tối đa 50 dòng gồm `e.poi_id`, `e.source_name`, `e.opening_hours_text` và giá trị nguồn tương ứng (`LIMIT 50`), rồi dừng.

## Chạy lại để kiểm tra idempotency

Trigger vẫn đang tắt trong toàn bộ mục này.

1. Chạy lại B2 cho bảng ctrl và ghi version thành `C1`:

   ```sql
   DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 1
   ```

2. Ghi thời điểm thành `T_RUN2`. Chạy `NB_00_ORCHES_SLV_TO_ENR_15P` lần 2 với đúng các giá trị cell 1 của bước 5 (`p_pl_name = "PL_VV_TRANS_SLV_TO_ENR_15P"`, `p_run_id = ""`, `p_mode = "RUN"`, `p_max_parallel = "2"`, `p_node_timeout_min = "15"`, `p_dag_timeout_min = "25"`, `p_lock_timeout_min = "35"`, `p_force_nodes = ""`, `p_history_limit = "1000"`, `p_non_data_ops = ""`). Tìm `EXEC_2` bằng truy vấn của bước 5, thay `<T_RUN1>` bằng `<T_RUN2>`.
3. Đọc log của exec 2. Dùng truy vấn R2 với `exec_id = '<EXEC_2>'`.
   - Kỳ vọng: `slv_poi_entity_non_enrich` có `NO_DATA` và `gld_enr_poi_info` có `NO_DATA`.
   - Nếu entity hoặc gold không ra `NO_DATA`, so `src_versions_json` của exec 2 với exec 1:
     - Có input đổi version (FL_00 có thể ghi bất kỳ lúc nào): R6 chưa kết luận được. Ghi lại, giữ trigger tắt và hỏi người dùng có chạy thêm một lần nữa không.
     - Không input nào đổi version: R6 fail. Dừng.
4. Chạy lại riêng cell `ohpasspy` của `NB_CREATE_DDL` (lakehouse mặc định `lh_vv_bronze`).
   - Kỳ vọng: in ra đúng dòng như bước 4.
   - Cell không `ALTER` vì cột đã có. MERGE không khớp dòng nào để insert hoặc update.
5. Kiểm tra history của bảng ctrl:

   ```sql
   DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 3
   ```

   - Kỳ vọng (R6): version mới nhất vẫn là `C1`.
   - Nếu có version mới, ghi `operation` và `operationMetrics` (`numTargetRowsInserted`, `numTargetRowsUpdated`) vào kết quả như một sai lệch so với R6, rồi báo người dùng. Không sửa gì.
6. Kiểm tra history của bảng entity:

   ```sql
   DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity_non_enrich LIMIT 3
   ```

   Kỳ vọng: không có commit `ADD COLUMNS` mới sau lần chạy `ohpasspy` thứ hai.

`ohpasspy` luôn cập nhật dòng khoá `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` trong `ctrl_mng_watermark` (nhận khoá, gia hạn, nhả khoá). Đây là hành vi đúng và không tính là thay đổi trong R6.

## Kiểm tra log và watermark

Chạy truy vấn sau sau exec 1, sau exec 2 và sau lần chạy lại `ohpasspy`:

```sql
SELECT watermark_id, src_tbl, trg_tbl, status, last_src_version, last_src_table_id, last_success_at,
       last_run_id, substr(error_message, 1, 300) AS error_message, lock_exec_id, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE (trg_tbl IN ('slv_poi_entity_non_enrich', 'gld_enr_poi_info') AND watermark_id LIKE 'wm_e%')
   OR watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P'
ORDER BY trg_tbl, src_tbl
LIMIT 50
```

Kỳ vọng sau exec 1:

- `wm_e__slv_poi_entity_non_enrich__slv_3p_poi_opening_hours`: dòng mới do lib chèn ở lần SUCCESS đầu tiên. `last_src_version` bằng `v_hours` của R5.
- `wm_e__gld_enr_poi_info__slv_3p_poi_opening_hours`: giống hệt `WM_GOLD_HOURS_0`. Dòng này bị đóng băng và không bị xoá.
- `wm_e__gld_enr_poi_info__slv_poi_entity_non_enrich`: `last_src_version` bằng `E1`.
- `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`: `lock_exec_id` và `lock_at` là NULL. `status` là trạng thái của run.

Kỳ vọng sau exec 2:

- Các dòng `wm_e__` của entity và gold có `last_src_version` không lùi.
- `wm_e__gld_enr_poi_info__slv_3p_poi_opening_hours` vẫn giống `WM_GOLD_HOURS_0`.

Kỳ vọng sau khi chạy lại `ohpasspy`:

- `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` có `status = SUCCESS`, `error_message` rỗng và `lock_exec_id` là NULL.
- Nếu cell lỗi, `status = FAILED` và `error_message` chứa lỗi, tối đa 500 ký tự.

Log node: không được có exec nào ngoài `EXEC_1` và `EXEC_2` trong khoảng từ `T_PAUSE` đến `T_RESUME`.

```sql
SELECT exec_id, min(started_at) AS started_at, collect_set(status) AS statuses
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND started_at >= TIMESTAMP '<T_PAUSE>'
GROUP BY exec_id
ORDER BY started_at
LIMIT 50
```

**R7. Lan truyền (sau `T_RESUME`, quan sát qua các tick sau).** Khi FL_00 ghi version mới vào `slv_3p_poi_opening_hours`, exec tiếp theo phải có:

- Entity có `inbox.slv_3p_poi_opening_hours` là `DATA_CHANGED`.
- Gold chạy sau entity trong cùng exec.

Truy vấn kiểm tra:

```sql
SELECT exec_id, trg_tbl, status, started_at, ended_at,
       get_json_object(qg_json, '$.inbox.slv_3p_poi_opening_hours') AS hours_inbox,
       get_json_object(qg_json, '$.metrics.opening_hours_text_mismatch') AS oh_mismatch
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND started_at >= TIMESTAMP '<T_RESUME>'
  AND trg_tbl IN ('slv_poi_entity_non_enrich', 'gld_enr_poi_info')
ORDER BY started_at DESC
LIMIT 50
```

## Rollback và forward recovery

Ưu tiên forward recovery. Không tự sửa tay ctrl ngoài câu lệnh rollback dưới đây.

Xử lý theo điểm lỗi:

| Điểm lỗi | Trạng thái | Xử lý |
|---|---|---|
| Đã sync notebook nhưng chưa chạy `ohpasspy` | Spec entity có `hours` nhưng chưa có cạnh. Gold còn cạnh giờ active nhưng không còn role. Cả hai node fail `ConfigError` trước khi ghi | Chạy `ohpasspy` (bước 4) |
| `ohpasspy` đã chạy nhưng notebook chưa sync | Trạng thái ngược lại, kết quả giống dòng trên | Sync notebook (bước 3) |
| `ALTER` xong nhưng MERGE lỗi | Cột đã có, cạnh chưa đổi. Code cũ vẫn chạy như trước, code mới fail như dòng 1 | Sửa nguyên nhân trong thông báo lỗi rồi chạy lại `ohpasspy`. Cell idempotent |
| `ohpasspy` báo `Dừng trước khi ghi` | Chưa ghi gì | Báo người dùng. Không sửa ctrl bằng tay |
| `ohpasspy` báo `mất khoá trước khi ghi` | Một run khác đã chiếm lease (rủi ro `STATE-001` đã được chấp nhận) | Dừng. Kiểm tra lại trigger, chạy R1 và B7 rồi báo người dùng. Nếu R1 cho thấy chưa đổi hoặc chỉ mới `ALTER`, chạy lại cell khi chắc chắn không còn run nào |
| Entity SUCCESS nhưng gold bị chặn `opening_hours_text_mismatch` | Entity đã có giá trị mới, gold chưa append. Cạnh entity của gold không tiến | Điều tra bằng mẫu R3. Lần chạy sau sẽ thử lại đúng các key đó |
| Entity fail vì dữ liệu, ví dụ trùng `poi_id` trong `slv_3p_poi_opening_hours` (QG khoá) | Entity không ghi. Amenity và gold có trạng thái `SKIPPED`. Gold giữ trạng thái nhất quán gần nhất | Sửa dữ liệu ở nguồn (FL_00), rồi để tick sau hoặc orchestrator chạy lại |

Rollback chỉ làm khi người dùng quyết định:

1. Tắt trigger `PL_VV_TRANS_SLV_TO_ENR_15P` theo `<CẦN NGƯỜI DÙNG CUNG CẤP: cách tắt trigger>`. Xác nhận không có run nào đang chạy (B3).
2. Revert commit code `<CẦN NGƯỜI DÙNG CUNG CẤP: hash commit cần revert>` và sync workspace DEV.
3. Trong khi trigger vẫn tắt, chạy câu lệnh dưới đây. Đây là một câu lệnh, tức một commit:

```sql
MERGE INTO lh_vv_ctrl.dbo.ctrl_mng_pipeline_config AS t
USING (SELECT 'lh_vv_silver.dbo' AS trg_schema, 'slv_poi_entity_non_enrich' AS trg_tbl, 0 AS flag
       UNION ALL SELECT 'lh_vv_gold.enr', 'gld_enr_poi_info', 1) AS s
ON t.pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND t.src_schema = 'lh_vv_silver.dbo'
   AND t.src_tbl = 'slv_3p_poi_opening_hours' AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl
WHEN MATCHED THEN UPDATE SET t.is_active = s.flag
```

4. Kiểm tra bằng truy vấn cạnh của R1. Kỳ vọng: cạnh entity `is_active = 0` và cạnh gold `is_active = 1`.
5. Chạy orchestrator với đúng tham số của bước 5 rồi bật lại trigger.

Sau rollback:

- Cạnh giờ của gold được bật lại với watermark cũ. Trạng thái của cạnh này sẽ là `DATA_CHANGED` hoặc `HISTORY_GAP`. `_role_keys` lấy dư key nên kết quả vẫn đúng.
- Cột `opening_hours_text` của entity được giữ lại (cho phép NULL). Code cũ không đọc cột này nên không cần sửa dữ liệu. Probe R4 trên `V0` chứng minh giá trị gold không đổi.
- Không xoá dòng ctrl hay watermark nào, kể cả `wm_e__slv_poi_entity_non_enrich__slv_3p_poi_opening_hours` (nó vô hại khi cạnh đã tắt) và `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`.
- Không dùng `DROP`, `RESTORE` hay `DELETE`.

## Kết quả người dùng ghi nhận

| Mục | Giá trị / kết quả |
|---|---|
| Workspace DEV | |
| Commit đã sync | |
| Trigger đã tắt? (có / không thể) và `T_PAUSE` | |
| `EXEC_BASE` (B4) | |
| `V0`, `T_V0` (B1) | |
| `C0` ctrl, `E0` entity (B2) | |
| B5 cạnh entity / gold khớp kỳ vọng? | |
| B6 `periods_json` kiểu / cột entity trước patch | |
| `WM_GOLD_HOURS_0` (B7) | |
| B8 `rows_v0`, `poi_v0`, `with_hours_v0` | |
| Dòng in của `ohpasspy` lần 1 (nguyên văn) | |
| `T_RUN1`, `EXEC_1` | |
| R1 cột + 2 cạnh | |
| R2 trạng thái entity / amenity / gold; `NEW_EDGE`; `opening_hours_other_source`; `partner_opening_hours_null`; `google_with_hours`; `partner_with_hours`; `oh_mismatch`; gold `inserted_rows` | |
| `E1`, `v_hours`, `v_i18n` | |
| R3 (kỳ vọng 0) | |
| R4 (kỳ vọng 0) | |
| R5 google / partner / nguồn khác (kỳ vọng 0 / 0 / 0) | |
| `C1`, `T_RUN2`, `EXEC_2` | |
| R6 entity / gold (kỳ vọng `NO_DATA` / `NO_DATA`) | |
| Dòng in của `ohpasspy` lần 2; ctrl history vẫn là `C1`? | |
| Watermark sau exec 1 / exec 2 / sau `ohpasspy` lần 2 | |
| Exec trong khoảng `T_PAUSE`–`T_RESUME` (chỉ `EXEC_1`, `EXEC_2`?) | |
| `T_RESUME` | |
| R7 (exec, `hours_inbox`, thứ tự entity → gold) | |
| Sai lệch / lỗi / quyết định rollback | |
| Người chạy, ngày | |
