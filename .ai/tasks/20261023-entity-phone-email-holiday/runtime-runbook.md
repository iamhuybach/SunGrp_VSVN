# Runtime runbook: 20261023-entity-phone-email-holiday

Trạng thái: `CHỜ CHẠY`

## Phạm vi và môi trường

- Môi trường: Fabric DEV. Workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`.
- Đây là runbook chung cho hai task, chạy một lần trên DEV:
  - `20261023-entity-opening-hours-passthrough`: cell `ohpasspy` chưa được áp trên DEV.
  - `20261023-entity-phone-email-holiday` (task này): cell `peholpy`.
- Theo D-OH-08, runtime của task giờ tạm dừng và chuyển sang runbook này. Không chạy `.ai/tasks/20261023-entity-opening-hours-passthrough/runtime-runbook.md`. Các bước giờ cần thiết đã được chép vào đây.
- Thay đổi được triển khai:
  - `NB_SLV_POI_ENTITY_NON_ENRICH` (cell `b1entitybuild`):
    - Tự tính `opening_hours_text` (D-OH-01..04). Node có thêm input `hours` = `slv_3p_poi_opening_hours`.
    - Thêm `DETAIL_COLS = ("phone", "email", "holiday_exceptions")` sau `HOURS_COLS` (D-PEH-01).
    - Google: `phone` lấy từ `slv_3p_poi_contact.phone`, `email` và `holiday_exceptions` là NULL (D-PEH-02).
    - Partner: `phone` và `email` lấy từ `slv_pn_business_services`. `holiday_exceptions` = `$.policies.holiday_exceptions` trong `amentities` của bản i18n `vi` (D-PEH-03).
    - Nguồn khác: ba cột là NULL, có block check `phone_email_holiday_other_source` (D-PEH-05).
  - `NB_ENR_POI_INFO` (cell `36415d3b`): truyền thẳng `e.opening_hours_text` và chặn khi gặp `opening_hours_text_mismatch`. Gold không thêm cột mới.
  - `NB_CREATE_DDL`:
    - Cell `ohpasspy`: `ALTER` thêm `opening_hours_text STRING` (cho phép NULL). Sau đó một MERGE trên `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` để thêm cạnh `slv_3p_poi_opening_hours -> slv_poi_entity_non_enrich` và đặt cạnh `slv_3p_poi_opening_hours -> gld_enr_poi_info` về `is_active = 0`. Cell này giữ khoá luồng.
    - Cell `peholpy`: đúng một `ALTER TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich ADD COLUMNS` với các cột còn thiếu trong `phone STRING, email STRING, holiday_exceptions STRING`. Không ghi ctrl, không giữ khoá, chạy lại thì không ghi gì.
  - `NB_SETUP_INITIAL_DDL`: spec entity có thêm ba tuple trước `row_hash`. Notebook này được deploy nhưng **không chạy trên DEV**.
- Thứ tự cột trên DEV sau khi patch: `… deleted_at, opening_hours_text, phone, email, holiday_exceptions`. Ba cột nằm sau `row_hash`. Đây là trạng thái đã được chấp nhận vì `schema_diff` và MERGE của lib so theo tên.
- Pipeline bị ảnh hưởng: `PL_VV_TRANS_SLV_TO_ENR_15P`, orchestrator `NB_00_ORCHES_SLV_TO_ENR_15P`.
- Lakehouse mặc định của `NB_CREATE_DDL`: `lh_vv_bronze`. Notebook này không có cell parameter. Không đổi lakehouse gắn sẵn của `NB_00_ORCHES_SLV_TO_ENR_15P`.
- Bảng liên quan:
  - `lh_vv_silver.dbo.slv_poi_entity_non_enrich`
  - `lh_vv_silver.dbo.slv_3p_poi_contact`
  - `lh_vv_silver.dbo.slv_3p_poi_opening_hours`
  - `lh_vv_silver.dbo.slv_pn_business_services`
  - `lh_vv_silver.dbo.slv_pn_business_service_i18ns`
  - `lh_vv_gold.enr.gld_enr_poi_info`
  - `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`
  - `lh_vv_ctrl.dbo.ctrl_mng_watermark`
  - `lh_vv_ctrl.dbo.ctrl_log_table_run`
- Rủi ro đã được chấp nhận (D-OH-07, 2026-10-23): `STATE-001`, `SQL-001`, `SQL-002`. Điều kiện đi kèm: tắt trigger `PL_VV_TRANS_SLV_TO_ENR_15P` trước `ohpasspy`. Chỉ bật lại sau lần chạy orchestrator thứ hai và lần chạy lại `ohpasspy`.
- Những việc không làm trong runbook này:
  - Không chạy riêng `NB_SLV_POI_ENTITY_NON_ENRICH` hoặc `NB_ENR_POI_INFO`.
  - Trong `NB_CREATE_DDL`, chỉ chạy `ohpasspy` và `peholpy`. Không chạy `enrddlpy`, `enrinfopy`, `mvpoipy` hay bất kỳ cell nào khác.
  - Không chạy `NB_SETUP_INITIAL_DDL` trên DEV.
  - Không sửa tay `ctrl_mng_pipeline_config` hoặc `ctrl_mng_watermark`. Không xoá khoá bằng tay.
  - Không `DROP` bảng hay cột.
- Mọi truy vấn kiểm tra đều chỉ đọc. Chỉ có các bước chạy cell và chạy orchestrator là ghi dữ liệu. Mẫu kết quả tối đa 50 dòng.
- Dữ liệu cá nhân: `phone` và `email` có thể là thông tin liên hệ cá nhân. Không chép giá trị `phone`/`email` vào kết quả. Mẫu chỉ được chứa `poi_id`, `source_name`, cờ NULL/không NULL, độ dài chuỗi, số đếm, trạng thái và giá trị giờ mở cửa.
- Thời gian trong `ctrl_log_table_run` là UTC.

## Điều kiện tiên quyết

1. Code của cả hai task đã được merge vào `main` và đẩy lên remote mà workspace DEV đồng bộ. Commit: `<CẦN NGƯỜI DÙNG CUNG CẤP: hash commit đã merge>`. Khi runbook này được viết, các file sau vẫn đang ở trạng thái sửa nhưng chưa commit:
   - `notebooks/NB_CREATE_DDL.ipynb`, `notebooks/NB_ENR_POI_INFO.ipynb`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb`
   - `docs/context/01_DATA_MODEL.md`
   - `tests/test_enr_poi_contract.py`, `tests/test_initial_ddl_contract.py`, `tests/test_poi_entity_contract.py`
2. Trên đúng commit đó, các lệnh local sau đều pass:
   - `python -m pytest tests/test_poi_entity_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py -q`
   - `python -m pytest -q`
   - `python scripts/vv.py verify 20261023-entity-phone-email-holiday`
3. Người chạy có quyền tắt và bật trigger của `PL_VV_TRANS_SLV_TO_ENR_15P`. Tên item / schedule và cách tắt/bật: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên item / schedule trigger của PL_VV_TRANS_SLV_TO_ENR_15P trong DEV và cách tắt/bật>`.
   - Nếu không thể tắt trigger, ghi rõ: `<CẦN NGƯỜI DÙNG CUNG CẤP: xác nhận không thể tắt trigger>`. Khi đó các bước 3–7 của mục `Các bước thực hiện` (deploy, `ohpasspy`, `peholpy`, orchestrator lần 1) phải xong trong cùng một khoảng trống 15 phút giữa hai tick.
   - Lúc này `STATE-001` không còn được giảm nhẹ. Tick rơi vào giữa chừng sẽ fail an toàn (`ConfigError` hoặc `SKIPPED_CONCURRENT`, xem mục Rollback).
4. Cách đồng bộ notebook vào workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách sync (Fabric Git integration / deploy) cho workspace DEV>`.
5. `ctrl_mng_pipeline_config` đã có cột `nb_name` (tức `enrddlpy` đã chạy trước đây). Nếu chưa có, `ohpasspy` dừng với `chưa có cột nb_name: chạy enrddlpy trước`. Khi đó dừng runbook và hỏi người dùng. Không tự chạy `enrddlpy`.
6. Bảng `lh_vv_silver.dbo.slv_poi_entity_non_enrich` đã tồn tại. Nếu chưa có, `peholpy` dừng với `chưa có, chạy NB_SETUP_INITIAL_DDL`. Khi đó dừng và hỏi người dùng. Không chạy setup trên DEV.

## Baseline trước khi chạy

Làm bước 1 (tắt trigger) của mục `Các bước thực hiện` trước, rồi chạy các truy vấn dưới đây. Tất cả đều chỉ đọc. Ghi kết quả vào mục `Kết quả người dùng ghi nhận`.

B1. Version mới nhất và schema của gold:

```sql
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_info LIMIT 1
```

Ghi `version` thành `V0` và `timestamp` thành `T_V0`.

```sql
DESCRIBE TABLE lh_vv_gold.enr.gld_enr_poi_info
```

Ghi toàn bộ danh sách `col_name`, `data_type` (theo thứ tự) thành `GOLD_SCHEMA_0`.

B2. Version hiện tại của bảng ctrl và bảng entity:

```sql
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 1
```

```sql
DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity_non_enrich LIMIT 1
```

Ghi `C0` và `E0`.

B3. Dòng khoá luồng:

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, substr(error_message, 1, 300) AS error_message, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P'
```

Kỳ vọng: `lock_exec_id` là NULL. Nếu khoá đang có giá trị, chờ run đó kết thúc. Không xoá khoá bằng tay. Ghi dòng này thành `LOCK_0`.

B4. Tick gần nhất của luồng:

```sql
SELECT exec_id, min(started_at) AS started_at, max(ended_at) AS ended_at, count(*) AS nodes
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'
GROUP BY exec_id
ORDER BY started_at DESC
LIMIT 5
```

Ghi `exec_id` mới nhất thành `EXEC_BASE`. Sau khi tắt trigger, không được có exec nào mới hơn `EXEC_BASE` cho tới bước 7.

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
  - Chưa có cạnh `slv_3p_poi_opening_hours`. Ngoại lệ duy nhất được chấp nhận: cạnh này đã tồn tại với đúng 1 dòng `is_active = 1`.
- Gold (`trg_schema = lh_vv_gold.enr`):
  - Cạnh `slv_3p_poi_opening_hours` có đúng 1 dòng. Trước patch, kỳ vọng `is_active = 1`.
  - Các cạnh active còn lại đúng là `slv_poi_entity_non_enrich`, `slv_poi_amenity`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_review`, `slv_pn_business_service_i18ns`, `slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination`, mỗi cạnh 1 dòng.
  - Danh sách này lấy từ `INFO_KEEP` của `ohpasspy`. Danh sách gold trong `docs/context/CTRL_TABLES_CONTEXT.md` §3 thiếu hai bảng `slv_enr_poi_*`. Cứ theo kết quả truy vấn. Nếu không khớp `INFO_KEEP`, cell sẽ dừng trước khi ghi.

Nếu có điểm nào lệch, dừng và báo người dùng.

B6. Schema các bảng silver:

```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich
```

```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_3p_poi_opening_hours
```

```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_3p_poi_contact
```

```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_pn_business_services
```

Kỳ vọng:

- Entity: chưa có `opening_hours_text`, hoặc đã có với kiểu `string` cho phép NULL. Chưa có `phone`, `email`, `holiday_exceptions`. Nếu đã có cột nào trong ba cột này, ghi lại vị trí và kiểu. `peholpy` chỉ chấp nhận khi các cột đó là phần đầu của `phone, email, holiday_exceptions`, đúng thứ tự, kiểu string cho phép NULL. Ghi danh sách cột thành `ENTITY_SCHEMA_0`.
- `slv_3p_poi_opening_hours.periods_json` có kiểu `string`.
- `slv_3p_poi_contact.phone`, `slv_pn_business_services.phone`, `slv_pn_business_services.email` có kiểu `string` (D-PEH-06). Nếu thiếu, entity sẽ dừng bằng `ConfigError`.

B7. Số dòng entity theo `source_name`:

```sql
SELECT source_name, count(*) AS n, count_if(deleted_at IS NULL) AS n_live
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich
GROUP BY source_name
ORDER BY source_name
LIMIT 50
```

Ghi thành `COUNTS_0`.

B8. Các watermark liên quan:

```sql
SELECT watermark_id, src_tbl, trg_tbl, status, last_src_version, last_src_table_id, last_success_at,
       last_run_id, substr(error_message, 1, 300) AS error_message, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE trg_tbl IN ('slv_poi_entity_non_enrich', 'gld_enr_poi_info') AND watermark_id LIKE 'wm_e%'
ORDER BY trg_tbl, src_tbl
LIMIT 50
```

Kỳ vọng:

- Chưa có `wm_e__slv_poi_entity_non_enrich__slv_3p_poi_opening_hours`. Nếu dòng này đã có, nó phải có `src_schema = lh_vv_silver.dbo`, `src_tbl = slv_3p_poi_opening_hours`, `trg_schema = lh_vv_silver.dbo`, `trg_tbl = slv_poi_entity_non_enrich`.
- Ghi toàn bộ dòng `wm_e__gld_enr_poi_info__slv_3p_poi_opening_hours` thành `WM_GOLD_HOURS_0`. Dòng này phải giữ nguyên trong suốt quá trình chạy.

B9. Số đếm tham chiếu của gold tại `V0`, chỉ để ghi nhận:

```sql
SELECT count(*) AS rows_v0, count(DISTINCT poi_id) AS poi_v0, count(opening_hours_text) AS with_hours_v0
FROM lh_vv_gold.enr.gld_enr_poi_info VERSION AS OF <V0>
```

## Các bước thực hiện

1. **Tắt trigger (D-OH-07).**
   - Tắt trigger của `PL_VV_TRANS_SLV_TO_ENR_15P` theo `<CẦN NGƯỜI DÙNG CUNG CẤP: tên item / schedule trigger và cách tắt>`. Ghi thời điểm thành `T_PAUSE`.
   - Trên Fabric Monitor, xác nhận không có run nào của pipeline này đang chạy. Chạy B3: `lock_exec_id` phải là NULL.
   - Nếu không tắt được trigger, ghi điều đó vào kết quả và làm theo điều kiện tiên quyết 3.
2. **Baseline.** Chạy B1–B9. Ghi `V0`, `T_V0`, `GOLD_SCHEMA_0`, `C0`, `E0`, `LOCK_0`, `EXEC_BASE`, `ENTITY_SCHEMA_0`, `COUNTS_0`, `WM_GOLD_HOURS_0`.
3. **Deploy cùng lúc bốn notebook.**
   - Đồng bộ workspace DEV về commit `<CẦN NGƯỜI DÙNG CUNG CẤP: hash commit>` theo `<CẦN NGƯỜI DÙNG CUNG CẤP: cách sync>`. Bốn notebook phải lên cùng một lần: `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_ENR_POI_INFO`, `NB_CREATE_DDL`, `NB_SETUP_INITIAL_DDL`.
   - Mở và đọc trong workspace, không chạy, để xác nhận đã có bản 23/10:
     - `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild` có `HOURS_COLS = ("opening_hours_text",)`, `DETAIL_COLS = ("phone", "email", "holiday_exceptions")`, `+ HOURS_COLS + DETAIL_COLS`, input `"hours": "slv_3p_poi_opening_hours"` và block check `phone_email_holiday_other_source`.
     - `NB_ENR_POI_INFO` cell `36415d3b` có dòng `[SỬA 23/10]` và không còn `_partner_hours`.
     - Bốn cell cuối của `NB_CREATE_DDL` là `ohpassmd`, `ohpasspy`, `peholmd`, `peholpy`.
     - `NB_SETUP_INITIAL_DDL` đã được sync. **Không chạy.**
   - Từ lúc này đến khi bước 4 xong, mọi tick chạy vào đều fail với `ConfigError` trước khi ghi. Vì vậy trigger phải đang tắt.
4. **Chạy `ohpasspy`.**
   - Chạy lại B3. Chỉ tiếp tục khi `lock_exec_id` là NULL.
   - Mở `NB_CREATE_DDL` với lakehouse mặc định `lh_vv_bronze`. Chỉ chạy cell `ohpasspy`. Cell này không có parameter. Không chạy `enrddlpy`, `enrinfopy`, `mvpoipy` hay cell nào khác.
   - Cell thành công khi in ra đúng một dòng:

     ```
     lh_vv_silver.dbo.slv_poi_entity_non_enrich.opening_hours_text string NULL; cạnh slv_poi_entity_non_enrich ['ref_dictionary_place_type', 'slv_3p_poi', 'slv_3p_poi_address', 'slv_3p_poi_contact', 'slv_3p_poi_opening_hours', 'slv_pn_business_service_i18ns', 'slv_pn_business_services']; cạnh gld_enr_poi_info ['slv_3p_poi_price', 'slv_3p_poi_rating', 'slv_3p_poi_review', 'slv_enr_poi_destination', 'slv_enr_poi_info_multi_lang', 'slv_pn_business_service_i18ns', 'slv_poi_amenity', 'slv_poi_entity_non_enrich']
     ```

   - Chép nguyên văn dòng in vào mục kết quả. Chạy `DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity_non_enrich LIMIT 1` và ghi version thành `E_OH`.
   - Xử lý khi cell báo lỗi:
     - `Luồng PL_VV_TRANS_SLV_TO_ENR_15P đang giữ khoá (...)`: có run khác đang chạy. Chờ run đó xong rồi chạy lại cell. Không xoá khoá.
     - `Dừng trước khi ghi: ...`: cell chưa ghi gì vào entity hoặc ctrl (chỉ dòng khoá `wm_flow__` được ghi `FAILED`). Dừng, chép lỗi và báo người dùng.
     - `... chưa có cột nb_name: chạy enrddlpy trước`: dừng và hỏi người dùng (điều kiện tiên quyết 5).
     - `Luồng ... mất khoá trước khi ghi` hoặc `Sau khi ghi: ...`: dừng và làm theo mục `Rollback và forward recovery`.
5. **Chạy `peholpy`.**
   - Chạy lại B3. Chỉ chạy khi `lock_exec_id` là NULL, tức `ohpasspy` đã nhả khoá.
   - Trong `NB_CREATE_DDL` (lakehouse mặc định `lh_vv_bronze`), chỉ chạy cell `peholpy`. Cell này không có parameter.
   - Cell thành công khi in ra đúng một dòng. Dòng này chứa `['phone', 'email', 'holiday_exceptions'] string NULL sau opening_hours_text`. Ở lần chạy đầu, kỳ vọng nguyên văn:

     ```
     lh_vv_silver.dbo.slv_poi_entity_non_enrich: ['phone', 'email', 'holiday_exceptions'] string NULL sau opening_hours_text; vừa thêm ['phone', 'email', 'holiday_exceptions']
     ```

   - Nếu `vừa thêm` không đủ ba cột, nghĩa là một phần đã có từ trước (B6). Ghi lại như một sai lệch, rồi tiếp tục nếu dòng in vẫn có phần `string NULL sau opening_hours_text`.
   - Chép nguyên văn dòng in. Chạy `DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity_non_enrich LIMIT 1` và ghi version thành `E_PEH`. Kỳ vọng `E_PEH` lớn hơn `E_OH` đúng 1, với `operation` là `ADD COLUMNS`.
   - Xử lý khi cell báo lỗi:
     - `Dừng trước khi ghi: ... chưa có opening_hours_text: chạy ohpasspy trước`: bước 4 chưa xong. Quay lại bước 4.
     - `Dừng trước khi ghi: ...` (các lý do khác: sai kiểu, sai vị trí, cột đã có không phải phần đầu): chưa ghi gì. Dừng, chép lỗi và báo người dùng.
     - `Sau khi ghi: ...`: `ALTER` đã commit nhưng kết quả sai. Dừng, chạy `DESCRIBE TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich`, chép kết quả và báo người dùng. Không `DROP`. Chỉ forward fix.
6. **Kiểm tra schema trước khi chạy luồng.**

   ```sql
   DESCRIBE TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich
   ```

   Kỳ vọng: `opening_hours_text`, `phone`, `email`, `holiday_exceptions` đều có kiểu `string`, cho phép NULL, theo đúng thứ tự đó, nằm sau `deleted_at`.
7. **Chạy orchestrator lần 1.**
   - Ghi thời điểm bắt đầu (UTC) thành `T_RUN1`.
   - Chạy notebook `NB_00_ORCHES_SLV_TO_ENR_15P`. Cell parameter `5de61e9d` giữ đúng các giá trị:

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

8. **Kiểm tra R1–R8** theo mục `Kiểm tra kết quả`. Đây là điểm dừng lấy bằng chứng. Nếu có probe fail, không chạy tiếp mà chuyển sang mục Rollback.
9. **Kiểm tra idempotency.** Làm theo mục `Chạy lại để kiểm tra idempotency` (R9 và R10).
10. **Bật lại trigger (D-OH-07).** Chỉ bật sau khi bước 9 xong.
    - Bật trigger theo `<CẦN NGƯỜI DÙNG CUNG CẤP: cách bật trigger>`. Ghi thời điểm thành `T_RESUME`.
    - Theo dõi R11 ở các tick sau.

## Kiểm tra kết quả

Chạy các probe sau ngay khi bước 7 xong. Tất cả đều chỉ đọc.

**R1. Schema entity, cạnh ctrl và schema gold (Verification 1, 6).**

```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich
```

Kỳ vọng: `phone`, `email`, `holiday_exceptions` có kiểu `string`, cho phép NULL. Vị trí `opening_hours_text < phone < email < holiday_exceptions` tăng dần.

```sql
SELECT id, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND src_schema = 'lh_vv_silver.dbo'
  AND src_tbl = 'slv_3p_poi_opening_hours'
ORDER BY trg_tbl
```

Kỳ vọng: đúng 2 dòng.

- `slv_poi_entity_non_enrich`: `is_active = 1`, `load_mode = RECOMPUTE`, `priority` và `nb_name` giống các cạnh entity khác ở B5.
- `gld_enr_poi_info`: `is_active = 0`.

```sql
DESCRIBE TABLE lh_vv_gold.enr.gld_enr_poi_info
```

Kỳ vọng: giống hệt `GOLD_SCHEMA_0`. Gold không có `phone`, `email`, `holiday_exceptions` mới.

**R2. Log của exec 1 (Verification 6).**

```sql
SELECT trg_tbl, status, priority, entity_rows, inserted_rows, updated_rows, deactivated_rows, trg_version,
       get_json_object(qg_json, '$.inbox') AS inbox,
       get_json_object(qg_json, '$.blocks') AS blocks,
       get_json_object(qg_json, '$.warns') AS warns,
       get_json_object(qg_json, '$.metrics.opening_hours_text_mismatch') AS oh_mismatch,
       get_json_object(qg_json, '$.metrics.google_with_hours') AS google_with_hours,
       get_json_object(qg_json, '$.metrics.partner_with_hours') AS partner_with_hours,
       get_json_object(qg_json, '$.metrics.google_with_phone') AS google_with_phone,
       get_json_object(qg_json, '$.metrics.partner_with_phone') AS partner_with_phone,
       get_json_object(qg_json, '$.metrics.partner_with_email') AS partner_with_email,
       get_json_object(qg_json, '$.metrics.partner_with_holiday') AS partner_with_holiday,
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
  - `blocks` có `opening_hours_other_source = 0` và `phone_email_holiday_other_source = 0`.
  - `warns` có `partner_opening_hours_null`. Giá trị chỉ để ghi nhận.
  - `google_with_hours`, `partner_with_hours`, `google_with_phone`, `partner_with_phone`, `partner_with_email`, `partner_with_holiday` đều có giá trị. Đây là số đếm, ghi nhận.
  - Ghi `trg_version` thành `E1`, cùng `updated_rows` và `inserted_rows`.
- `slv_poi_amenity`: `SUCCESS` hoặc `NO_DATA`.
- `gld_enr_poi_info`:
  - `status = SUCCESS` và `oh_mismatch = 0`.
  - `inbox` không còn `slv_3p_poi_opening_hours`.
  - `inserted_rows` là lượng append một lần cho các key có `opening_hours_text` khác NULL. Chỉ ghi nhận.
- Các node khác: ghi nhận trạng thái. Chúng không thuộc tiêu chí nghiệm thu.
- Nếu `get_json_object` trả NULL vì cấu trúc `qg_json` khác, đọc `substr(qg_json, 1, 4000)` của đúng dòng đó.

**R3. Version input mà entity đã đọc trong exec 1.**

```sql
SELECT trg_version,
       get_json_object(src_versions_json, '$.slv_3p_poi_opening_hours.v') AS v_hours,
       get_json_object(src_versions_json, '$.slv_pn_business_service_i18ns.v') AS v_i18n,
       get_json_object(src_versions_json, '$.slv_pn_business_services.v') AS v_svc,
       get_json_object(src_versions_json, '$.slv_3p_poi_contact.v') AS v_contact,
       substr(src_versions_json, 1, 4000) AS src_versions_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id = '<EXEC_1>' AND trg_tbl = 'slv_poi_entity_non_enrich'
```

Ghi `E1`, `v_hours`, `v_i18n`, `v_svc`, `v_contact`. Nếu cột `v_*` là NULL vì khoá trong JSON có dạng khác, đọc thẳng `v` của đúng bảng trong `src_versions_json`.

**R4. Grain và số dòng (Verification 2).**

```sql
SELECT source_name, count(*) AS n, count_if(deleted_at IS NULL) AS n_live
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <E1>
GROUP BY source_name
ORDER BY source_name
LIMIT 50
```

Kỳ vọng: bằng `COUNTS_0`, chỉ lệch theo drift nguồn bình thường. Ghi lệch từng nguồn.

```sql
SELECT count(*) AS n, count(DISTINCT poi_id) AS n_poi
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <E1>
```

Kỳ vọng: `n = n_poi`.

**R5. Google (Verification 3).** Kỳ vọng cả hai số là `0`:

```sql
SELECT count_if(e.email IS NOT NULL OR e.holiday_exceptions IS NOT NULL) AS google_email_holiday_not_null,
       count_if(NOT (e.phone <=> c.phone)) AS google_phone_mismatch
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <E1> e
LEFT JOIN (SELECT poi_id, phone FROM lh_vv_silver.dbo.slv_3p_poi_contact VERSION AS OF <v_contact>
           WHERE poi_id IS NOT NULL) c ON c.poi_id = e.poi_id
WHERE e.deleted_at IS NULL AND lower(trim(e.source_name)) = 'google'
```

Nếu khác 0, lấy mẫu (không chép giá trị phone/email):

```sql
SELECT e.poi_id, e.source_name,
       e.phone IS NULL AS e_phone_null, c.phone IS NULL AS src_phone_null,
       e.email IS NULL AS e_email_null, e.holiday_exceptions IS NULL AS e_holiday_null
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <E1> e
LEFT JOIN (SELECT poi_id, phone FROM lh_vv_silver.dbo.slv_3p_poi_contact VERSION AS OF <v_contact>
           WHERE poi_id IS NOT NULL) c ON c.poi_id = e.poi_id
WHERE e.deleted_at IS NULL AND lower(trim(e.source_name)) = 'google'
  AND (NOT (e.phone <=> c.phone) OR e.email IS NOT NULL OR e.holiday_exceptions IS NOT NULL)
LIMIT 50
```

**R6. Partner và hồi quy giờ (Verification 4).** Kỳ vọng cả bốn số là `0`:

```sql
WITH s AS (SELECT id, phone, email
           FROM lh_vv_silver.dbo.slv_pn_business_services VERSION AS OF <v_svc>
           WHERE NOT coalesce(deleted, false)),
     i AS (SELECT business_service_id,
                  get_json_object(amentities, '$.policies.operating_hours') AS hours,
                  get_json_object(amentities, '$.policies.holiday_exceptions') AS holiday
           FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns VERSION AS OF <v_i18n>
           WHERE locale = 'vi' AND NOT coalesce(deleted, false))
SELECT count_if(NOT (e.phone <=> s.phone)) AS partner_phone_mismatch,
       count_if(NOT (e.email <=> s.email)) AS partner_email_mismatch,
       count_if(NOT (e.holiday_exceptions <=> i.holiday)) AS partner_holiday_mismatch,
       count_if(NOT (e.opening_hours_text <=> i.hours)) AS partner_hours_mismatch
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <E1> e
LEFT JOIN s ON s.id = e.source_id
LEFT JOIN i ON i.business_service_id = e.source_id
WHERE e.deleted_at IS NULL AND lower(trim(e.source_name)) = 'partner'
```

Hồi quy giờ cho dòng google. Kỳ vọng `0`:

```sql
SELECT count(*)
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <E1> e
LEFT JOIN lh_vv_silver.dbo.slv_3p_poi_opening_hours VERSION AS OF <v_hours> oh ON oh.poi_id = e.poi_id
WHERE e.deleted_at IS NULL AND lower(trim(e.source_name)) = 'google'
  AND NOT (e.opening_hours_text <=> oh.periods_json)
```

Nếu số nào khác 0, lấy tối đa 50 dòng với các cột sau rồi dừng: `e.poi_id`, `e.source_name`, các cờ `IS NULL` của `phone`/`email` hai bên, `length(e.holiday_exceptions)`, `length(i.holiday)`, `e.opening_hours_text` và giá trị giờ nguồn tương ứng (`LIMIT 50`). Không chép giá trị phone/email.

**R7. Nguồn khác (Verification 5).** Kỳ vọng cả hai số là `0`, khớp block `phone_email_holiday_other_source` và `opening_hours_other_source`:

```sql
SELECT count_if(coalesce(phone, email, holiday_exceptions) IS NOT NULL) AS other_detail_not_null,
       count_if(opening_hours_text IS NOT NULL) AS other_hours_not_null
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich VERSION AS OF <E1>
WHERE deleted_at IS NULL
  AND coalesce(lower(trim(source_name)), '') NOT IN ('google', 'partner')
```

**R8. Gold không đổi giá trị giờ.**

Gold bằng silver. Kỳ vọng `0`:

```sql
WITH g AS (SELECT poi_id, opening_hours_text,
                  row_number() OVER (PARTITION BY poi_id ORDER BY updated_at DESC, created_at DESC) AS rn
           FROM lh_vv_gold.enr.gld_enr_poi_info)
SELECT count(*) FROM g JOIN lh_vv_silver.dbo.slv_poi_entity_non_enrich e
  ON e.poi_id = g.poi_id AND e.deleted_at IS NULL
WHERE g.rn = 1 AND NOT (g.opening_hours_text <=> e.opening_hours_text)
```

Giá trị gold giữ nguyên so với `V0`. Kỳ vọng `0`:

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

Nếu khác 0, lấy mẫu bằng cách đổi `SELECT count(*)` thành `SELECT o.poi_id, o.opening_hours_text AS v0_value, n.opening_hours_text AS new_value` (hoặc `g.poi_id, e.source_name, g.opening_hours_text, e.opening_hours_text` cho truy vấn đầu), rồi thêm `LIMIT 50`.

## Chạy lại để kiểm tra idempotency

Trigger vẫn đang tắt trong toàn bộ mục này.

**R9. Chạy lại `peholpy` (Verification 7).**

1. Ghi version mới nhất của entity thành `E_PRE`:

   ```sql
   DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity_non_enrich LIMIT 1
   ```

2. Chạy lại B3. Chỉ tiếp tục khi `lock_exec_id` là NULL.
3. Trong `NB_CREATE_DDL` (lakehouse mặc định `lh_vv_bronze`), chỉ chạy lại cell `peholpy`. Kỳ vọng in ra nguyên văn:

   ```
   lh_vv_silver.dbo.slv_poi_entity_non_enrich: ['phone', 'email', 'holiday_exceptions'] string NULL sau opening_hours_text; vừa thêm []
   ```

4. Chạy lại truy vấn ở 1. Kỳ vọng: version mới nhất vẫn là `E_PRE`, tức không có Delta version mới.

**R10. Orchestrator lần 2 và chạy lại `ohpasspy`.**

1. Ghi version hiện tại của bảng ctrl thành `C1`:

   ```sql
   DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 1
   ```

2. Ghi thời điểm thành `T_RUN2`. Chạy `NB_00_ORCHES_SLV_TO_ENR_15P` lần 2 với đúng các giá trị cell `5de61e9d` của bước 7: `p_pl_name = "PL_VV_TRANS_SLV_TO_ENR_15P"`, `p_run_id = ""`, `p_mode = "RUN"`, `p_max_parallel = "2"`, `p_node_timeout_min = "15"`, `p_dag_timeout_min = "25"`, `p_lock_timeout_min = "35"`, `p_force_nodes = ""`, `p_history_limit = "1000"`, `p_non_data_ops = ""`. Tìm `EXEC_2` bằng truy vấn của bước 7, thay `<T_RUN1>` bằng `<T_RUN2>`.
3. Đọc log của exec 2 bằng truy vấn R2 với `exec_id = '<EXEC_2>'`.
   - Kỳ vọng: `slv_poi_entity_non_enrich` có `NO_DATA` và `gld_enr_poi_info` có `NO_DATA`.
   - Nếu entity hoặc gold không ra `NO_DATA`, so `src_versions_json` của exec 2 với exec 1:
     - Có input đổi version (FL_00 có thể ghi bất kỳ lúc nào): R10 chưa kết luận được. Ghi lại, giữ trigger tắt và hỏi người dùng có chạy thêm một lần không.
     - Không input nào đổi version: R10 fail. Dừng.
4. Ghi version mới nhất của entity thành `E2` (`DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity_non_enrich LIMIT 1`).
5. Chạy lại B3, rồi chạy lại riêng cell `ohpasspy` của `NB_CREATE_DDL` (lakehouse mặc định `lh_vv_bronze`).
   - Kỳ vọng: in ra đúng dòng như bước 4 của `Các bước thực hiện`.
   - Cell không `ALTER` vì cột đã có. MERGE không khớp dòng nào để insert hoặc update.
6. Kiểm tra history của bảng ctrl:

   ```sql
   DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 3
   ```

   - Kỳ vọng: version mới nhất vẫn là `C1`.
   - Nếu có version mới, ghi `operation` và `operationMetrics` (`numTargetRowsInserted`, `numTargetRowsUpdated`) vào kết quả như một sai lệch, rồi báo người dùng. Không sửa gì.
7. Kiểm tra history của bảng entity:

   ```sql
   DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity_non_enrich LIMIT 3
   ```

   Kỳ vọng: version mới nhất vẫn là `E2`. Không có commit `ADD COLUMNS` mới.

`ohpasspy` luôn cập nhật dòng khoá `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` trong `ctrl_mng_watermark` (nhận khoá, gia hạn, nhả khoá). Đây là hành vi đúng và không tính là thay đổi trong R10. `peholpy` không đọc hay ghi bảng ctrl nào.

Sau khi R9 và R10 đạt, quay lại bước 10 của `Các bước thực hiện` để bật trigger.

## Kiểm tra log và watermark

Chạy truy vấn sau tại bốn thời điểm: sau `peholpy` lần 1, sau exec 1, sau exec 2 và sau lần chạy lại `ohpasspy`.

```sql
SELECT watermark_id, src_tbl, trg_tbl, status, last_src_version, last_src_table_id, last_success_at,
       last_run_id, substr(error_message, 1, 300) AS error_message, lock_exec_id, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE (trg_tbl IN ('slv_poi_entity_non_enrich', 'gld_enr_poi_info') AND watermark_id LIKE 'wm_e%')
   OR watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P'
ORDER BY trg_tbl, src_tbl
LIMIT 50
```

Kỳ vọng sau `peholpy` lần 1: mọi dòng giống hệt lần đọc ngay sau `ohpasspy`. `peholpy` không ghi watermark hay khoá.

Kỳ vọng sau exec 1:

- `wm_e__slv_poi_entity_non_enrich__slv_3p_poi_opening_hours`: dòng mới do lib chèn ở lần SUCCESS đầu tiên. `last_src_version` bằng `v_hours` của R3.
- `wm_e__slv_poi_entity_non_enrich__slv_3p_poi_contact`, `__slv_pn_business_services`, `__slv_pn_business_service_i18ns`: `last_src_version` không lùi so với B8 và bằng `v_contact`, `v_svc`, `v_i18n` của R3.
- `wm_e__gld_enr_poi_info__slv_3p_poi_opening_hours`: giống hệt `WM_GOLD_HOURS_0`. Dòng này bị đóng băng và không bị xoá.
- `wm_e__gld_enr_poi_info__slv_poi_entity_non_enrich`: `last_src_version` bằng `E1`.
- `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`: `lock_exec_id` và `lock_at` là NULL. `status` là trạng thái của run.

Kỳ vọng sau exec 2:

- Các dòng `wm_e__` của entity và gold có `last_src_version` không lùi.
- `wm_e__gld_enr_poi_info__slv_3p_poi_opening_hours` vẫn giống `WM_GOLD_HOURS_0`.

Kỳ vọng sau khi chạy lại `ohpasspy`:

- `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` có `status = SUCCESS`, `error_message` rỗng và `lock_exec_id` là NULL.
- Nếu cell lỗi, `status = FAILED` và `error_message` chứa lỗi (tối đa 500 ký tự).

Log node: trong khoảng `T_PAUSE` đến `T_RESUME`, chỉ được có `EXEC_1` và `EXEC_2`.

```sql
SELECT exec_id, min(started_at) AS started_at, collect_set(status) AS statuses
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND started_at >= TIMESTAMP '<T_PAUSE>'
GROUP BY exec_id
ORDER BY started_at
LIMIT 50
```

**R11. Lan truyền (sau `T_RESUME`, quan sát qua các tick sau).**

- Khi FL_00 ghi version mới vào `slv_3p_poi_opening_hours`, exec tiếp theo phải có entity với `inbox.slv_3p_poi_opening_hours = DATA_CHANGED`, và gold chạy sau entity trong cùng exec.
- Block `phone_email_holiday_other_source` tiếp tục bằng 0.

```sql
SELECT exec_id, trg_tbl, status, started_at, ended_at,
       get_json_object(qg_json, '$.inbox.slv_3p_poi_opening_hours') AS hours_inbox,
       get_json_object(qg_json, '$.metrics.opening_hours_text_mismatch') AS oh_mismatch,
       get_json_object(qg_json, '$.blocks') AS blocks
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND started_at >= TIMESTAMP '<T_RESUME>'
  AND trg_tbl IN ('slv_poi_entity_non_enrich', 'gld_enr_poi_info')
ORDER BY started_at DESC
LIMIT 50
```

## Rollback và forward recovery

Ưu tiên forward recovery: sửa notebook rồi để lần chạy 15P sau tính lại. Entity là full recompute rồi MERGE, nên một lần chạy đúng sẽ sửa mọi giá trị. Không `DROP` bảng hay cột. Không sửa tay ctrl.

Xử lý theo điểm lỗi:

| Điểm lỗi | Trạng thái | Xử lý |
|---|---|---|
| Đã deploy nhưng chưa chạy `ohpasspy` | Spec entity có `hours` nhưng chưa có cạnh. Gold còn cạnh giờ active nhưng không còn role. Cả hai node fail `ConfigError` trước khi ghi | Chạy `ohpasspy` (bước 4) |
| `ohpasspy` đã chạy nhưng notebook chưa deploy | Ngược lại với dòng trên, kết quả giống nhau | Deploy notebook (bước 3) |
| `ohpasspy`: `ALTER` xong nhưng MERGE lỗi | Cột đã có, cạnh chưa đổi | Sửa nguyên nhân trong thông báo lỗi, rồi chạy lại `ohpasspy`. Cell idempotent |
| `ohpasspy` báo `Dừng trước khi ghi` | Chưa ghi gì | Báo người dùng. Không sửa ctrl bằng tay |
| `ohpasspy` báo `mất khoá trước khi ghi` | Một run khác đã chiếm lease (`STATE-001` đã được chấp nhận) | Dừng. Kiểm tra lại trigger, chạy R1 và B8, rồi báo người dùng. Nếu R1 cho thấy chưa đổi gì hoặc chỉ mới `ALTER`, chạy lại cell khi chắc chắn không còn run nào |
| `ohpasspy` xong nhưng `peholpy` chưa chạy hoặc báo `Dừng trước khi ghi` | Entity có `opening_hours_text` nhưng chưa có ba cột. Đây là trạng thái hợp lệ. Nếu notebook mới chạy, `ensure_target` của lib tự thêm ba cột theo thứ tự build | Sửa điều kiện được báo rồi chạy lại `peholpy`. Nếu cột đã được `ensure_target` thêm đúng, `peholpy` in `vừa thêm []` |
| `peholpy` báo `Sau khi ghi` | `ALTER` đã commit nhưng sai kiểu hoặc sai vị trí | Dừng. Chép `DESCRIBE TABLE` rồi báo người dùng. Không `DROP`. Chỉ forward fix |
| `ALTER` của `peholpy` xung đột với MERGE của node | Delta làm fail một bên. Không có schema dở dang | Chạy lại bên bị fail: `peholpy` do người chạy, node bằng orchestrator |
| Entity fail `ConfigError` thiếu `phone`/`email` | Entity không ghi | Kiểm tra B6. Báo người dùng (D-PEH-06) |
| Entity SUCCESS nhưng gold bị chặn `opening_hours_text_mismatch` | Entity đã có giá trị mới, gold chưa append. Cạnh entity của gold không tiến | Điều tra bằng mẫu R8. Lần chạy sau sẽ thử lại đúng các key đó |
| Entity fail vì dữ liệu (ví dụ QG trùng `poi_id` của contact) | Entity không ghi. Amenity và gold có trạng thái `SKIPPED`. Gold giữ trạng thái nhất quán gần nhất | Sửa dữ liệu ở nguồn (FL_00), rồi để orchestrator hoặc tick sau chạy lại |
| R5, R6 hoặc R7 khác 0 | Giá trị entity sai | Dừng, giữ trigger tắt và báo người dùng. Forward fix notebook rồi chạy lại orchestrator |

**Rollback code của task này (chỉ khi người dùng quyết định).**

1. Tắt trigger theo `<CẦN NGƯỜI DÙNG CUNG CẤP: cách tắt trigger>`. Xác nhận không có run nào đang chạy (B3).
2. Redeploy bản notebook chỉ có phần giờ (cây làm việc của task giờ, chưa có `DETAIL_COLS` và `peholpy`): `<CẦN NGƯỜI DÙNG CUNG CẤP: commit / bản notebook hours-only để redeploy>` theo `<CẦN NGƯỜI DÙNG CUNG CẤP: cách sync>`.
3. Chạy orchestrator với đúng tham số của bước 7, rồi bật lại trigger.
4. Sau rollback:
   - `ensure_target` ghi WARN về cột thừa. MERGE ngừng ghi ba cột: dòng đã khớp giữ giá trị cũ, dòng mới có NULL. Không consumer nào đọc ba cột này, nên trạng thái này vô hại.
   - Ba cột được giữ lại trong schema. `DROP COLUMN` cần column mapping và nằm ngoài phạm vi.

**Các thao tác ghi dữ liệu, chỉ làm khi người dùng quyết định rõ:**

- Làm sạch ba cột (một commit). Chỉ chạy khi trigger đang tắt và đã có quyết định của người dùng:

  ```sql
  UPDATE lh_vv_silver.dbo.slv_poi_entity_non_enrich
  SET phone = NULL, email = NULL, holiday_exceptions = NULL
  ```

- `RESTORE` entity về một version đã ghi chỉ làm được khi không có lần chạy nào sau đó cần giữ. Cần quyết định của người dùng và không phải lựa chọn mặc định:
  - `E0`: trước cả `ohpasspy`. Schema cũng quay về trạng thái trước `opening_hours_text`, nên chỉ nhất quán khi phần giờ cũng được rollback (xem dưới).
  - `E_OH` hoặc `E_PEH`: chỉ quay schema/dữ liệu về sau từng patch.
  - Câu lệnh mẫu: `RESTORE TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich TO VERSION AS OF <version người dùng chọn>`.

**Rollback cả phần giờ (`ohpasspy`), chỉ khi người dùng quyết định.**

1. Tắt trigger và xác nhận khoá trống (B3).
2. Revert commit code `<CẦN NGƯỜI DÙNG CUNG CẤP: hash commit cần revert>` và sync workspace DEV.
3. Trong khi trigger vẫn tắt, chạy câu lệnh dưới đây (một câu, một commit):

   ```sql
   MERGE INTO lh_vv_ctrl.dbo.ctrl_mng_pipeline_config AS t
   USING (SELECT 'lh_vv_silver.dbo' AS trg_schema, 'slv_poi_entity_non_enrich' AS trg_tbl, 0 AS flag
          UNION ALL SELECT 'lh_vv_gold.enr', 'gld_enr_poi_info', 1) AS s
   ON t.pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND t.src_schema = 'lh_vv_silver.dbo'
      AND t.src_tbl = 'slv_3p_poi_opening_hours' AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl
   WHEN MATCHED THEN UPDATE SET t.is_active = s.flag
   ```

4. Kiểm tra bằng truy vấn cạnh của R1. Kỳ vọng: cạnh entity `is_active = 0`, cạnh gold `is_active = 1`.
5. Chạy orchestrator với đúng tham số của bước 7, rồi bật lại trigger.
6. Sau rollback:
   - Cạnh giờ của gold được bật lại với watermark cũ, nên sẽ có `DATA_CHANGED` hoặc `HISTORY_GAP`. `_role_keys` lấy dư key nên kết quả vẫn đúng.
   - Các cột `opening_hours_text`, `phone`, `email`, `holiday_exceptions` được giữ lại (cho phép NULL). Code cũ không đọc chúng.
   - Không xoá dòng ctrl hay watermark nào, kể cả `wm_e__slv_poi_entity_non_enrich__slv_3p_poi_opening_hours` và `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`.
   - Không dùng `DROP` hay `DELETE`.

## Kết quả người dùng ghi nhận

Không chép giá trị `phone`/`email` vào bảng này.

| Mục | Giá trị / kết quả |
|---|---|
| Workspace DEV | |
| Commit đã sync | |
| Trigger đã tắt? (có / không thể), `T_PAUSE` | |
| `EXEC_BASE` (B4), `LOCK_0` (B3) | `EXEC_BASE` = `8af0f170-dd54-4dba-8968-3bffdf3339c0`, 2026-10-22T07:58:25Z–07:58:45Z, 1 node. `LOCK_0`: `SUCCESS`, `lock_exec_id` NULL, `last_run_id` = `8af0f170-dd54-4dba-8968-3bffdf3339c0`, `updated_at` 2026-10-22T07:58:50Z. |
| `V0`, `T_V0`, `GOLD_SCHEMA_0` (B1) | `V0` = 7, `T_V0` = 2026-10-22T07:36:56Z, WRITE Append 65 dòng, exec `ee89eb57-fc56-48ec-b860-eced85c44ea8`. Schema gold có `opening_hours_text` string; không có `phone`, `email`, `holiday_exceptions`. |
| `C0` ctrl, `E0` entity (B2) | `C0` = 19, 2026-10-22T06:31:49Z. `E0` = 1, MERGE 2026-10-20T10:14:46Z, 65 dòng insert. |
| B5: cạnh entity / gold khớp kỳ vọng? | Khớp. Entity: đúng 6 cạnh active, `RECOMPUTE`, `nb_name` NULL, chưa có `slv_3p_poi_opening_hours`. Gold: cạnh giờ `is_active` = 1; đủ 9 cạnh `INFO_KEEP`, mỗi cạnh 1 dòng. |
| B6: `ENTITY_SCHEMA_0`; kiểu `periods_json`, `contact.phone`, `svc.phone`, `svc.email` | Entity chưa có `opening_hours_text`, `phone`, `email`, `holiday_exceptions`. `periods_json`, `contact.phone`, `svc.phone`, `svc.email` đều `string`. |
| `COUNTS_0` (B7) | google 41 / 41 live. partner 24 / 24 live. |
| `WM_GOLD_HOURS_0` (B8) | `wm_e__gld_enr_poi_info__slv_3p_poi_opening_hours`: SUCCESS, `last_src_version` 4, `last_run_id` `5edc3634-ad7a-4545-8465-d0c7830dc543`, `last_success_at` 2026-10-22T03:19:13Z. Chưa có watermark giờ của entity. |
| B9: `rows_v0`, `poi_v0`, `with_hours_v0` | Chưa có. |
| Đã xác nhận bốn notebook bản 23/10 (bước 3) | Workspace có `DETAIL_COLS = ("phone", "email", "holiday_exceptions")` trong `b1entitybuild`. |
| Dòng in `ohpasspy` lần 1 (nguyên văn), `E_OH` | Khớp nguyên văn dòng kỳ vọng trong bước 4. `E_OH` = 2, `ADD COLUMNS` `opening_hours_text`, 2026-10-23T09:59:45Z. |
| Dòng in `peholpy` lần 1 (nguyên văn), `E_PEH` | `lh_vv_silver.dbo.slv_poi_entity_non_enrich: ['phone', 'email', 'holiday_exceptions'] string NULL sau opening_hours_text; vừa thêm ['phone', 'email', 'holiday_exceptions']`. `E_PEH` = 3, `ADD COLUMNS` ba cột, 2026-10-23T10:00:30Z. |
| Schema entity sau patch (bước 6) | Sau `deleted_at`: `opening_hours_text`, `phone`, `email`, `holiday_exceptions`, đều `string`. |
| `T_RUN1`, `EXEC_1` | `EXEC_1` = `525a64db-8c5a-46ab-acf2-2a68330bf384`, 2026-10-23T10:38:51Z–10:44:29Z. Pipeline `SUCCESS`, 4 node, 20 cạnh. |
| R1: schema entity, 2 cạnh giờ, gold schema = `GOLD_SCHEMA_0`? | Đạt. Entity: thứ tự bốn cột string tăng dần. Cạnh giờ: id 83 entity `is_active` 1 `RECOMPUTE` `nb_name` NULL; id 54 gold `is_active` 0. Gold schema giống B1. |
| R2: trạng thái entity / amenity / gold; `NEW_EDGE`; `opening_hours_other_source`; `phone_email_holiday_other_source`; `partner_opening_hours_null`; các metric `*_with_*`; `oh_mismatch`; gold `inserted_rows` | Đạt phần entity. Entity `SUCCESS`, 65 dòng, `updated` 64, version 4. Inbox giờ `NEW_EDGE`. Block `opening_hours_other_source` = 0, `phone_email_holiday_other_source` = 0. Warn `partner_opening_hours_null` = 13. Metric: hours 40/11, phone 38/24, email 24, holiday 11. Amenity `SUCCESS` version 1. Gold `SUCCESS`, `inserted` 64, version 8. Inbox gold không có `slv_3p_poi_opening_hours`. `oh_mismatch` không có trong `qg_json`. |
| R3: `E1`, `v_hours`, `v_i18n`, `v_svc`, `v_contact` | `E1` = 4. Khoá JSON là tên đủ. `v_hours` = 4, `v_i18n` = 6, `v_svc` = 6, `v_contact` = 5. Giờ dirty `NEW_EDGE`. |
| R4: số dòng theo nguồn so với `COUNTS_0`; `n = n_poi`? | Đạt. google 41/41, partner 24/24. `n` = 65, `n_poi` = 65. |
| R5 google: email/holiday khác NULL, phone mismatch (kỳ vọng 0 / 0) | 0 / 0. |
| R6 partner: phone / email / holiday / hours mismatch; google hours mismatch (kỳ vọng 0 / 0 / 0 / 0 / 0) | 0 / 0 / 0 / 0 / 0. |
| R7 nguồn khác: detail / hours (kỳ vọng 0 / 0) | 0 / 0. |
| R8: gold = silver; gold so với `V0` (kỳ vọng 0 / 0) | 0 / 0. |
| R9: `E_PRE`; dòng in `peholpy` lần 2 (`vừa thêm []`); entity history vẫn là `E_PRE`? | Đạt. `E_PRE` = 4. Dòng in `vừa thêm []`. History mới nhất vẫn version 4, `MERGE` 2026-10-23T10:42:17Z. Copy 1, update 64, source 65. Không có version 5. |
| R10: `C1`, `T_RUN2`, `EXEC_2`; entity / gold (kỳ vọng `NO_DATA` / `NO_DATA`); `E2` | |
| R10: dòng in `ohpasspy` lần 2; ctrl history vẫn là `C1`? entity vẫn là `E2`? | |
| Watermark sau `peholpy` / exec 1 / exec 2 / `ohpasspy` lần 2 | |
| Exec trong khoảng `T_PAUSE`–`T_RESUME` (chỉ `EXEC_1`, `EXEC_2`?) | |
| `T_RESUME` | |
| R11 (exec, `hours_inbox`, thứ tự entity → gold, blocks) | |
| Sai lệch / lỗi / quyết định rollback | D-PEH-13: R9 đạt. R10 chưa chạy; thuộc task giờ. Không rollback. |
| Người chạy, ngày | Bách, 2026-10-23 |
