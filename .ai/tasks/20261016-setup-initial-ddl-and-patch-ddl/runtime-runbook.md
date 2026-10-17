# Runtime runbook — 20261016-setup-initial-ddl-and-patch-ddl

Notebook: `notebooks/NB_SETUP_INITIAL_DDL.ipynb`. Nguồn: `architecture.md` (Main brief, §5.1, §5.2, §9, §10.2, §10.3, §12, §14, §15), cell `init_param` của notebook, `docs/context/CTRL_TABLES_CONTEXT.md` §1 và §4. Task này không có pipeline JSON.

## Phạm vi và môi trường

Runbook này dùng để thu bằng chứng runtime ở hai điểm dừng của architecture (Main brief, mục "Order and stop points" bước 4–5):

- R1–R5 (§14 bước 2) chạy trên một **môi trường trống do người dùng cung cấp**. Môi trường có 4 lakehouse `lh_vv_bronze`, `lh_vv_ctrl`, `lh_vv_silver`, `lh_vv_gold`, mỗi lakehouse có schema `dbo`, chưa có bảng nào và chưa có lịch chạy (schedule) nào.
  - Workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên / id workspace của môi trường trống>`
  - Capacity: `<CẦN NGƯỜI DÙNG CUNG CẤP: capacity id của môi trường trống>`
- R6 (§14 bước 3) chạy trên **DEV, chỉ chạy plan**: `p_apply = "false"`. **Không bao giờ apply trên DEV.**
  - Workspace DEV: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên / id workspace DEV>`

Tham số duy nhất là `p_apply`, nằm trong cell `init_param`, tag `parameters`. Giá trị mặc định trong file là:

```python
p_apply = "false"
```

Notebook chỉ ghi khi operator đặt `p_apply = "true"`. Với mọi giá trị khác `true`, notebook không ghi gì. Nó in 14 dòng hành động theo bảng, câu CREATE và `defined`/`to_insert` của từng seed, rồi thoát với `status = "PLAN"` (§10.3).

Notebook tạo 14 bảng, theo thứ tự tạo ở §5.1:

| # | Bảng |
|---|---|
| 1 | `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` |
| 2 | `lh_vv_ctrl.dbo.ctrl_mng_watermark` |
| 3 | `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` |
| 4 | `lh_vv_ctrl.dbo.ctrl_log_run` |
| 5 | `lh_vv_ctrl.dbo.ctrl_log_table_run` |
| 6 | `lh_vv_ctrl.dbo.ctrl_cdc_state` |
| 7 | `lh_vv_ctrl.dbo.ctrl_cdc_reject` |
| — | `CREATE SCHEMA IF NOT EXISTS lh_vv_gold.enr` |
| 8 | `lh_vv_gold.enr.gld_enr_poi_info` |
| 9 | `lh_vv_gold.enr.gld_enr_poi_coordinate` |
| 10 | `lh_vv_gold.enr.gld_enr_poi_review` |
| 11 | `lh_vv_silver.dbo.ref_dictionary_place_type` |
| 12 | `lh_vv_silver.dbo.ref_dictionary_amenities` |
| 13 | `lh_vv_silver.dbo.slv_poi_amenity` |
| 14 | `lh_vv_silver.dbo.slv_poi_entity` |

Notebook nạp 5 seed, theo thứ tự ghi ở §6 và §5.2:

| Seed | Bảng đích | Khoá logic | Số dòng định nghĩa |
|---|---|---|---|
| `pipeline_config` | #1 | (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`) | 50 |
| `watermark` | #2 | `watermark_id` | 2 |
| `registry` | #3 | (`src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`, `trg_column`) | flatten(partner) + 55. Không có số tuyệt đối trong file: lấy `defined` in ra ở R1 |
| `place_type` | #11 | (`source_name`, `place_type`) | `len(SEED_ROWS)`. Lấy `defined` in ra ở R1 |
| `amenities` | #12 | (`source_name`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`) | `len(SEED_ROWS)`. Lấy `defined` in ra ở R1 |

Mọi query trong runbook đều chỉ đọc, trừ bước chạy notebook (R2, R3) và các lệnh trong mục Rollback. Các bảng ở đây chỉ chứa cấu hình và từ điển, không có dữ liệu cá nhân. Mẫu kết quả vẫn giới hạn tối đa 50 dòng.

## Điều kiện tiên quyết

1. Code đã qua kiểm tra local (Main brief, mục "Tests and verification"):
   - `python -m pytest tests/test_initial_ddl_contract.py -q` pass.
   - `python -m pytest tests -q` pass.
   - `git diff --exit-code notebooks/NB_CREATE_DDL.ipynb` sạch.
   - `python scripts/vv.py verify 20261016-setup-initial-ddl-and-patch-ddl` pass.
2. `notebooks/NB_SETUP_INITIAL_DDL.ipynb` và `NB_LIB_TRANSFORM_SLV_GLD` (notebook này gọi `%run NB_LIB_TRANSFORM_SLV_GLD` ở cell `init_run`) đã được đưa lên workspace đích. Commit / phiên bản được deploy: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit hash đã deploy>`.
3. Môi trường trống (R1–R5) có 4 lakehouse `lh_vv_bronze`, `lh_vv_ctrl`, `lh_vv_silver`, `lh_vv_gold`, mỗi lakehouse có schema `dbo`, chưa có bảng và chưa có schedule.
4. Trong suốt thời gian apply, không có pipeline, notebook extract, NB_00 hay node nào đang chạy (§9). Notebook không tự phát hiện được điều này, nên operator phải tự xác nhận.
5. Default lakehouse đính kèm notebook: `<CẦN NGƯỜI DÙNG CUNG CẤP: default lakehouse gắn cho NB_SETUP_INITIAL_DDL trên môi trường trống và trên DEV>`. Mọi tên bảng trong notebook đều viết đầy đủ ba phần.
6. Với R6: người chạy có quyền đọc DEV và cam kết giữ `p_apply = "false"`.

## Baseline trước khi chạy

Chạy các lệnh sau trong một notebook Spark SQL hoặc SQL cell riêng, chỉ đọc, trên **môi trường trống**:

```sql
SHOW TABLES IN lh_vv_bronze.dbo;
SHOW TABLES IN lh_vv_ctrl.dbo;
SHOW TABLES IN lh_vv_silver.dbo;
SHOW TABLES IN lh_vv_gold.dbo;
SHOW SCHEMAS IN lh_vv_gold;
```

Kỳ vọng: bốn lệnh `SHOW TABLES` trả 0 dòng, và `SHOW SCHEMAS IN lh_vv_gold` chưa có `enr`. Nếu có bảng nào: DỪNG, vì môi trường không còn trống. Ghi nhận lại và hỏi người dùng.

Kiểm tra schedule: trong Fabric UI, xác nhận workspace không có pipeline / notebook nào được đặt lịch. Ghi kết quả vào mục cuối.

Baseline trên **DEV** (trước R6, chỉ đọc). Bước này cần để có version Delta phục vụ rollback nếu có ai lỡ apply:

```sql
SHOW TABLES IN lh_vv_ctrl.dbo;
SHOW TABLES IN lh_vv_silver.dbo;
SHOW TABLES IN lh_vv_gold.enr;

DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 5;
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_watermark LIMIT 5;
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_cfg_schema_registry LIMIT 5;
DESCRIBE HISTORY lh_vv_silver.dbo.ref_dictionary_place_type LIMIT 5;
DESCRIBE HISTORY lh_vv_silver.dbo.ref_dictionary_amenities LIMIT 5;
```

Ghi lại `version` mới nhất của từng bảng. Bảng nào chưa có thì ghi "không có".

## Các bước thực hiện

Cách đặt tham số: mở notebook trong Fabric, sửa giá trị trong cell `init_param`, hoặc override tham số `p_apply` khi chạy. Sau mỗi lần chạy, ghi lại toàn bộ output gồm các dòng in theo bảng, các dòng `seed=… defined=… to_insert=…` và JSON exit.

**R1 — plan trên môi trường trống**
- Tham số: `p_apply = "false"`
- Kỳ vọng:
  - JSON exit `{"status": "PLAN", "p_apply": false, ...}`.
  - 14 dòng bảng đều là `CREATE`, mỗi dòng kèm câu CREATE.
  - Với mọi seed, `to_insert = defined`. `pipeline_config defined=50`, `watermark defined=2`.
- Sau khi chạy, lặp lại 4 lệnh `SHOW TABLES` ở mục Baseline: vẫn 0 bảng, tức là không có gì được tạo.
- Ghi lại `defined` của `registry`, `place_type`, `amenities`. Các con số này là kỳ vọng cho R2 và R4.

**R2 — apply lần đầu trên môi trường trống**
- Tham số: `p_apply = "true"`
- Kỳ vọng:
  - JSON exit `{"status":"SUCCESS","tables":[…14],"seeds":{name:{"defined","inserted","drift"}}}`.
  - Đủ 14 bảng.
  - Với mọi seed, `inserted = defined` và `drift = 0`.
- Ngay sau R2, chạy SQL R4 (mục Kiểm tra kết quả) và ghi lại `n`, `k`.

**R3 — apply lần hai trên môi trường trống**
- Tham số: `p_apply = "true"`
- Kỳ vọng: SUCCESS. Với mọi seed, `inserted = 0` và `drift = 0`.

**R4 — kiểm tra đếm sau R2 và sau R3**
- Chạy SQL ở mục Kiểm tra kết quả: một lần sau R2 và một lần sau R3.
- Kỳ vọng: ở mỗi dòng `n = k`, và `n` của R3 bằng `n` của R2.

**R5 — plan lại trên môi trường trống**
- Tham số: `p_apply = "false"`
- Kỳ vọng: PLAN, 14 × `EXISTS_OK`, và `to_insert = 0` cho mọi seed.

**R6 — DEV, chỉ plan**
- Tham số: `p_apply = "false"`. **Không đổi sang `"true"`.**
- Ghi lại toàn bộ 14 dòng theo bảng. Kỳ vọng:
  - `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config EXISTS_OK`. Điều này chứng minh môi trường đã vá bằng ALTER `enrddlpy` khớp với định nghĩa đầy đủ.
  - `lh_vv_silver.dbo.slv_poi_entity EXISTS_OK` nếu node đã chạy trên DEV. Nếu bảng chưa có trên DEV, ghi "không chứng minh được trên DEV". Khi đó R2 cùng test `test_poi_entity_columns_derived` là bằng chứng.
- Nếu DEV có khác biệt schema ở bảng khác, plan sẽ in rồi raise `ConfigError` mà không ghi gì. Ghi các khác biệt thành finding và **không apply**. Lỗi `thiếu <col>` nghĩa là DEV còn thiếu patch `NB_CREATE_DDL` (§9). Ghi lại thành finding, không xử lý trong runbook này.

## Kiểm tra kết quả

SQL đếm của §14, chỉ đọc. Chạy sau R2 và sau R3:

```sql
SELECT 'pipeline_config' AS t, COUNT(*) AS n, COUNT(DISTINCT pl_name, src_schema, src_tbl, trg_schema, trg_tbl) AS k FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
UNION ALL SELECT 'watermark', COUNT(*), COUNT(DISTINCT watermark_id) FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
UNION ALL SELECT 'registry', COUNT(*), COUNT(DISTINCT src_schema, src_tbl, trg_schema, trg_tbl, trg_column) FROM lh_vv_ctrl.dbo.ctrl_cfg_schema_registry
UNION ALL SELECT 'place_type', COUNT(*), COUNT(DISTINCT source_name, place_type) FROM lh_vv_silver.dbo.ref_dictionary_place_type
UNION ALL SELECT 'amenities', COUNT(*), COUNT(DISTINCT source_name, business_sector, amenity_group, amenity_raw, amenity) FROM lh_vv_silver.dbo.ref_dictionary_amenities;
```

Kỳ vọng:
- `pipeline_config`: n = k = 50.
- `watermark`: n = k = 2.
- `registry`, `place_type`, `amenities`: n = k = `defined` đã ghi ở R1.

Kiểm tra đủ 14 bảng sau R2:

```sql
SHOW TABLES IN lh_vv_ctrl.dbo;     -- 7 bảng #1–#7
SHOW TABLES IN lh_vv_gold.enr;     -- 3 bảng #8–#10
SHOW TABLES IN lh_vv_silver.dbo;   -- 4 bảng #11–#14
```

Kiểm tra id của pipeline_config. Trên môi trường sạch, id phải chạy từ 1 đến 50 (§8):

```sql
SELECT MIN(id) AS min_id, MAX(id) AS max_id, COUNT(DISTINCT id) AS n_id
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config;
```

Kỳ vọng: `min_id = 1`, `max_id = 50`, `n_id = 50`.

Mẫu cấu hình để đối chiếu (tối đa 50 dòng, không có dữ liệu cá nhân):

```sql
SELECT id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, dedup_order, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
ORDER BY id
LIMIT 50;
```

Bảng `slv_poi_entity` phải rỗng và có 21 cột, tất cả nullable (§10.1a):

```sql
SELECT COUNT(*) AS n FROM lh_vv_silver.dbo.slv_poi_entity;
DESCRIBE TABLE lh_vv_silver.dbo.slv_poi_entity;
```

## Chạy lại để kiểm tra idempotency

R3 và R5 chính là bước kiểm tra idempotency:
- R3 (`p_apply = "true"` lần hai): mọi seed có `inserted = 0` và `drift = 0`, và SQL R4 cho `n` không đổi so với R2.
- R5 (`p_apply = "false"`): 14 × `EXISTS_OK`, `to_insert = 0`.

Đối chiếu thêm qua lịch sử Delta, chỉ đọc. Commit MERGE của R3 phải có `numTargetRowsInserted = 0` (§12):

```sql
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 5;
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_watermark LIMIT 5;
DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_cfg_schema_registry LIMIT 5;
DESCRIBE HISTORY lh_vv_silver.dbo.ref_dictionary_place_type LIMIT 5;
DESCRIBE HISTORY lh_vv_silver.dbo.ref_dictionary_amenities LIMIT 5;
```

Với mỗi bảng, ghi lại `version`, `operation` và `operationMetrics.numTargetRowsInserted` của MERGE ở R2 (bằng `defined`) và ở R3 (bằng 0).

## Kiểm tra log và watermark

**Log:** notebook này **không ghi dòng `ctrl_log_run`** (§12), giống các notebook `NB_SETUP_*` hiện có. Bằng chứng nằm ở output và JSON exit của notebook. Trên môi trường trống, kiểm tra rằng bảng log vẫn rỗng sau R2 và R3:

```sql
SELECT COUNT(*) AS n FROM lh_vv_ctrl.dbo.ctrl_log_run;
SELECT COUNT(*) AS n FROM lh_vv_ctrl.dbo.ctrl_log_table_run;
```

Kỳ vọng: cả hai bằng `0`.

**Watermark:** chỉ kiểm tra 2 dòng nguồn trong `WATERMARK_ROWS` (§10.2), không kiểm tra watermark cạnh (`wm_e__…`) hay khoá luồng (`wm_flow__…`):

```sql
SELECT watermark_id, src_schema, src_tbl, trg_schema, trg_tbl, watermark_column, watermark_value,
       last_success_at, status, flow_name, watermark_sequence, last_run_id, last_src_version,
       last_src_table_id, error_message, lock_exec_id, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN ('wm_transform_partner_raw_data', 'wm_transform_brz_3rd_crawler_poi_stream')
ORDER BY watermark_id;
```

Kỳ vọng sau R2, giữ nguyên sau R3:

| watermark_id | src_schema | src_tbl | watermark_column | status | flow_name | watermark_sequence |
|---|---|---|---|---|---|---|
| `wm_transform_brz_3rd_crawler_poi_stream` | `lh_vv_bronze.dbo` | `brz_3rd_crawler_poi_stream` | `crawled_at` | `INITIALIZED` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` | -1 |
| `wm_transform_partner_raw_data` | `lh_vv_bronze.dbo` | `partner_raw_data` | `EventProcessedUtcTime` | `INITIALIZED` | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` | -1 |

Các cột còn lại là NULL: `trg_schema`, `trg_tbl`, `watermark_value`, `last_success_at`, `last_run_id`, `last_src_version`, `last_src_table_id`, `error_message`, `lock_exec_id`, `lock_at`. `updated_at` có giá trị là thời điểm R2. Vì MERGE không có `WHEN MATCHED`, `updated_at` **không đổi** sau R3.

Mỗi dòng phải có `trg_tbl IS NULL`, vì notebook extract cần đúng 1 dòng cấp nguồn (CTRL_TABLES_CONTEXT §4). Kiểm tra thêm rằng bảng chỉ có đúng 2 dòng này:

```sql
SELECT COUNT(*) AS n FROM lh_vv_ctrl.dbo.ctrl_mng_watermark;   -- kỳ vọng 2
```

## Rollback và forward recovery

Phần này theo §15. Các lệnh ghi ở đây **chỉ chạy khi cần rollback** và sau khi người dùng xác nhận. **Không chạy trên DEV**, trừ trường hợp "apply nhầm trên môi trường có dữ liệu" bên dưới.

1. **Code:** revert commit. Mọi thay đổi đều là thêm mới, và `NB_CREATE_DDL` không bị sửa.

2. **Môi trường trống, apply lỗi giữa chừng:** forward recovery là chạy lại `p_apply = "true"`.
   - Nếu lỗi sau k lệnh CREATE, lần chạy lại tạo nốt các bảng còn thiếu.
   - Nếu lỗi giữa các seed, lần chạy lại chỉ thêm khoá còn thiếu (§9).
   - `ConfigError` (validation, schema diff, khoá trùng) xảy ra trước mọi lệnh ghi. Sửa nguyên nhân rồi chạy lại.

3. **Môi trường trống, cần gỡ toàn bộ:** các bảng không chứa dữ liệu nghiệp vụ, nên operator có thể xoá chúng bằng tay.
   - Trước khi xoá: chạy lại 4 lệnh `SHOW TABLES` và SQL R4 để xác nhận đây đúng là môi trường thử, rồi ghi kết quả.
   - Sau đó chạy:

   ```sql
   -- CHỈ trên môi trường trống: <CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace môi trường trống>
   DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_poi_entity;
   DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_poi_amenity;
   DROP TABLE IF EXISTS lh_vv_silver.dbo.ref_dictionary_amenities;
   DROP TABLE IF EXISTS lh_vv_silver.dbo.ref_dictionary_place_type;
   DROP TABLE IF EXISTS lh_vv_gold.enr.gld_enr_poi_review;
   DROP TABLE IF EXISTS lh_vv_gold.enr.gld_enr_poi_coordinate;
   DROP TABLE IF EXISTS lh_vv_gold.enr.gld_enr_poi_info;
   DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_cdc_reject;
   DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_cdc_state;
   DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_log_table_run;
   DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_log_run;
   DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_cfg_schema_registry;
   DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_mng_watermark;
   DROP TABLE IF EXISTS lh_vv_ctrl.dbo.ctrl_mng_pipeline_config;
   ```

   Schema `lh_vv_gold.enr` là do notebook tạo. Có xoá schema này không: `<CẦN NGƯỜI DÙNG CUNG CẤP: có xoá schema lh_vv_gold.enr trên môi trường trống hay không>`.

4. **Lỡ apply trên môi trường có dữ liệu (ví dụ DEV):** notebook chỉ thêm bảng còn thiếu (rỗng) và dòng còn thiếu, không sửa hay xoá dòng có sẵn. Cách gỡ:
   - Với mỗi bảng seed có commit MERGE ngoài ý muốn, lấy version **trước MERGE** từ `DESCRIBE HISTORY`. Nên dùng version đã ghi ở mục Baseline của DEV.
   - Sau đó chạy:

   ```sql
   RESTORE TABLE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config TO VERSION AS OF <version trước MERGE>;
   RESTORE TABLE lh_vv_ctrl.dbo.ctrl_mng_watermark TO VERSION AS OF <version trước MERGE>;
   RESTORE TABLE lh_vv_ctrl.dbo.ctrl_cfg_schema_registry TO VERSION AS OF <version trước MERGE>;
   RESTORE TABLE lh_vv_silver.dbo.ref_dictionary_place_type TO VERSION AS OF <version trước MERGE>;
   RESTORE TABLE lh_vv_silver.dbo.ref_dictionary_amenities TO VERSION AS OF <version trước MERGE>;
   ```

   Chỉ RESTORE bảng nào thực sự có commit MERGE từ lần apply nhầm. Bảng do lần apply nhầm tạo mới (rỗng) thì xử lý theo quyết định của người dùng: `<CẦN NGƯỜI DÙNG CUNG CẤP: xử lý bảng rỗng được tạo nhầm trên môi trường có dữ liệu>`.

5. **Spec `slv_poi_entity` sai, phát hiện sau R2 trên môi trường trống:** bảng rỗng, nên operator chạy `DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_poi_entity;`, sửa spec, rồi chạy lại. Ở môi trường mà node đã ghi dữ liệu thì **không DROP**: sửa tiến bằng một patch trong `NB_CREATE_DDL`.

6. **Rủi ro còn lại (§9):** một CREATE bị huỷ giữa chừng có thể để lại entry catalog không có Delta log, khiến `spark.table` lỗi. Khôi phục thủ công: `<CẦN NGƯỜI DÙNG CUNG CẤP: quy trình gỡ entry catalog hỏng trên Fabric>`. Notebook không bao giờ tự xoá.

## Kết quả người dùng ghi nhận

Dán kết quả đã làm sạch: tối đa 50 dòng, không có dữ liệu cá nhân, không có secret. File bằng chứng lưu ở `evidence/results/`.

**Môi trường**
- Workspace môi trường trống: không có. Người dùng xác nhận không chạy được `p_apply = true` vì chưa có prod.
- Workspace DEV: namespace `sgr_visitvn_dev`.
- Commit đã deploy: chưa ghi.
- Thời điểm chạy: 2026-10-17. History Delta mới nhất là 2026-10-16.

**Baseline**
- `SHOW TABLES` không phải môi trường trống. DEV đã có bảng model cũ và 14 bảng model mới. Người dùng: chỉ xét bảng model mới.
- Schedule: chưa ghi.
- Version mới nhất: `ctrl_mng_pipeline_config` 10, `ctrl_mng_watermark` 78, `ctrl_cfg_schema_registry` 15, `ref_dictionary_place_type` 1, `ref_dictionary_amenities` 1. Chi tiết ở `evidence/results/dev-plan-20261017.md`.

**R1–R5**
- Không chạy. Không có môi trường trống.

**R6** (DEV, `p_apply = "false"`)
- 14 bảng model mới: `EXISTS_OK`. Exit `PLAN`, `p_apply` false. Không `ConfigError`.
- `ctrl_mng_pipeline_config`: `EXISTS_OK`, CREATE in ra có `nb_name`.
- `slv_poi_entity`: `EXISTS_OK`, 21 cột khớp spec.
- `slv_poi_amenity`: `EXISTS_OK`.
- Seed `defined`/`to_insert`: pipeline_config 50/0, watermark 2/0, registry 356/0, place_type 356/0, amenities 152/0.
- Không apply trên DEV: có.
