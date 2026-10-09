# CTRL_TABLES_CONTEXT — 7 bảng control `lh_vv_ctrl.dbo`

> Nguồn sự thật cho bảng ctrl của Visit Vietnam. Cập nhật: **08/10/2026** (thay bản 04/10 trong project: 5 cột log mới, dòng cạnh / dòng khoá của luồng tính lại).
> DDL + seed 2 nguồn extract: `notebooks/NB_CREATE_DDL.ipynb`.
> **Dữ liệu ở mục "Dữ liệu hiện có" là theo log / kết quả đã gửi về tới 05/10**, không phải đọc trực tiếp hôm nay. Lấy số mới nhất: chạy `CHECK_CTRL_SNAPSHOT.py` (chỉ đọc, kèm bộ này) và gửi lại output.

## 1. Tổng quan

| # | Bảng | Nhóm | Grain / khoá logic | Ghi bởi | Đọc bởi |
|---|---|---|---|---|---|
| 1 | `ctrl_mng_pipeline_config` | Cấu hình | 1 dòng / (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`) | Tay / `NB_CREATE_DDL` | Pre-check FL_00, 2 notebook extract, NB_00 |
| 2 | `ctrl_mng_watermark` | Trạng thái | 1 dòng / `watermark_id` | Notebook extract, NB_00 (cạnh + khoá), node chạy tay (chỉ khoá) | Pre-check FL_00, extract, NB_00, node |
| 3 | `ctrl_cfg_schema_registry` | Cấu hình | 1 dòng / (`src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`, `trg_column`) | Tay (cell seed trong `NB_CREATE_DDL`) | 2 notebook extract |
| 4 | `ctrl_log_run` | Log | 1 dòng / `exec_id` | Extract (MERGE theo `exec_id`), NB_00 (append + UPDATE) | Vận hành, extract (run RUNNING quá hạn), NB_00 (ghim theo batch extract, lát cắt luồng khác) |
| 5 | `ctrl_log_table_run` | Log | 1 dòng / (`exec_id`, `trg_schema`, `trg_tbl`, `attempt_no`) | Extract (append cuối run), node (append mỗi lần chạy) | Vận hành, NB_00 (kết quả node) |
| 6 | `ctrl_cdc_state` | Trạng thái extract | 1 dòng / (`trg_schema`, `trg_tbl`, `entity_key`) | Extract (MERGE, không lùi) | Extract (lọc event đã áp dụng) |
| 7 | `ctrl_cdc_reject` | Lỗi extract | 1 dòng / `event_hash` | Extract (MERGE) | Vận hành |

Quy ước chung:
- Vị trí `lh_vv_ctrl.dbo`. Code và SQL luôn viết đầy đủ `lh_vv_ctrl.dbo.<bảng>`. Không dùng dạng ngắn `ctrl.<bảng>`. Default lakehouse của notebook vẫn có thể là `lh_vv_bronze`.
- Delta **không có PK / UNIQUE**: khoá logic ghi ở tài liệu này; ghi bằng MERGE theo khoá hoặc `WHERE NOT EXISTS` trước INSERT.
- Mọi `*_at` là UTC. `exec_id` = uuid mỗi lần notebook chạy; `run_id` = `@pipeline().RunId` (chạy tay = `exec_id`).
- 7 bảng **chưa** bật `optimizeWrite` / `autoCompact`, chưa có lịch OPTIMIZE / VACUUM (xem `99_PAIN_POINTS.md` M6).

## 2. Quan hệ

```
                                  ┌── load_mode CDC / DOC / DOC_ARRAY / LANG / LANG_ARRAY ─► EXTRACT (1 notebook / nguồn raw)
ctrl_mng_pipeline_config ─────────┤        (src = bảng raw, trg = bảng silver L1)
  pl_name, src_*, trg_*           │        ├─ (src_schema, src_tbl) ──► ctrl_mng_watermark  wm_transform_<src_tbl>   (1 dòng / nguồn)
                                  │        └─ (src_*, trg_*) ─────────► ctrl_cfg_schema_registry                  (1 dòng / cột đích)
                                  │
                                  └── load_mode RECOMPUTE ──► LUỒNG TÍNH LẠI (NB_00_ORCHES_SLV_TO_GLD, p_pl_name)
                                           1 dòng = 1 cạnh (src = bảng đầu vào, trg = node)
                                           ├─ (src_tbl, trg_tbl) ──► ctrl_mng_watermark  wm_e__<trg_tbl>__<src_tbl>  (hộp thư cạnh)
                                           └─ pl_name ────────────► ctrl_mng_watermark  wm_flow__<pl_name>         (khoá cả luồng)

Mỗi lần chạy (exec_id):
  ctrl_log_run (1 dòng) ──exec_id──► ctrl_log_table_run (extract: 1 dòng / bảng đích ; luồng tính lại: 1 dòng / node)
  Extract còn ghi: ctrl_cdc_state (1 dòng / entity / bảng đích), ctrl_cdc_reject (1 dòng / event lỗi)
```

Pre-check FL_00 (Get Metadata, không Spark) chỉ đọc 8 cột cũ của `pipeline_config` và `last_src_version`, `last_success_at`, `watermark_value` của dòng nguồn — thêm cột / thêm dòng `RECOMPUTE` không ảnh hưởng (lọc theo `pl_name` và `src_tbl = 'partner_raw_data'`).

JSON trong repo (`pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/`): bản export Fabric 09/10. `Get_Config_4Run` dùng connection `conn_lh_vv_bronze_by_sqlep`, `database = lh_vv_ctrl`, query `dbo.ctrl_mng_pipeline_config` với `is_active = 1` và `src_tbl = 'partner_raw_data'`. `Lookup_WM` đọc `lh_vv_ctrl` schema `dbo` bảng `ctrl_mng_watermark`. `manifest.json` khai báo cùng ba linked service: connection đó, `lh_vv_ctrl`, `lh_vv_bronze`. ForEach tuần tự. Dòng 3P vẫn nằm trong bảng config cho notebook chạy tay và không vào ForEach. Nhánh có việc gọi activity `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK`, tham số gắn cứng `src_tbl = partner_raw_data`. Không có Switch.

---

## 3. `ctrl_mng_pipeline_config`

**Mục đích:** danh sách việc của mỗi pipeline. Với extract: bảng đích + nguồn raw + wave + cách tách dòng. Với luồng tính lại: **cạnh** của DAG.
**Ý nghĩa:** thêm / tắt bảng, đổi thứ tự, thêm luồng mới bằng dữ liệu, không sửa code. Notebook không lưu GUID (khác giữa dev / stg / prod).

### DDL

```sql
CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.ctrl_mng_pipeline_config (
    id          BIGINT,
    pl_name     STRING,
    src_schema  STRING,
    src_tbl     STRING,
    trg_schema  STRING,
    trg_tbl     STRING,
    is_active   INT,
    priority    INT,
    load_mode   STRING  COMMENT 'CDC (Debezium, partner) | DOC | DOC_ARRAY | LANG | LANG_ARRAY (snapshot, 3rd-party). NULL = CDC',
    align_path  STRING  COMMENT 'DOC_ARRAY / LANG_ARRAY: mảng tính từ gốc payload ghép theo vị trí, đọc bằng json_path _align.<trường>',
    dedup_order STRING  COMMENT 'Snapshot: chọn 1 dòng khi 1 tài liệu có nhiều dòng cùng khoá, vd is_original DESC, created_at DESC'
) USING DELTA;
-- Tuỳ chọn (chưa tạo): nb_name STRING — notebook của node khi khác NB_<UPPER(trg_tbl)>; lib gold tự nhận nếu có cột
```

### Cột

| Cột | Kiểu | Extract | Luồng tính lại (`RECOMPUTE`) |
|---|---|---|---|
| `id` | BIGINT | `MAX(id) + seq` lúc seed, chỉ là số thứ tự | Như extract |
| `pl_name` | STRING | `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` | Tên pipeline của luồng tính lại; hậu tố nhịp bắt buộc |
| `src_schema`, `src_tbl` | STRING | Bảng raw (`lh_vv_bronze.dbo`, `partner_raw_data` / `brz_3rd_crawler_poi_stream`) | Bảng đầu vào của node (silver L1, ref, node khác, bảng gold cũ) |
| `trg_schema`, `trg_tbl` | STRING | Bảng silver L1 | Node (silver L2 / gold) |
| `is_active` | INT | 1 bật / 0 tắt **cả bảng** | 1 bật / 0 tắt cạnh |
| `priority` | INT | Wave: cùng priority chạy song song (`max_parallel`) | = tầng của node trong DAG (chỉ để đọc; NB_00 tự tính thứ tự từ cạnh) |
| `load_mode` | STRING | `CDC` (partner; NULL = CDC) · `DOC` · `DOC_ARRAY` · `LANG` · `LANG_ARRAY` (3P). Notebook kiểm tra: partner chỉ nhận `CDC`, 3P chỉ nhận 4 mode snapshot | `RECOMPUTE` |
| `align_path` | STRING | `*_ARRAY`: mảng ghép theo vị trí (đọc bằng `json_path` `_align.<trường>`) | NULL |
| `dedup_order` | STRING | Snapshot: `"<cột> [ASC\|DESC], ..."` chọn 1 dòng khi 1 tài liệu có nhiều dòng cùng khoá (NULL xếp cuối, rồi `_pos`) | NULL |

Kiểm tra khi nạp (lib): trùng bảng đích, `table_filter` có tên lạ, `load_mode` ngoài miền / không thuộc notebook, `align_path` / `dedup_order` sai chỗ. Luồng tính lại (`build_dag`): 1 node chỉ thuộc 1 pl active, không chu trình, node không tự đọc chính nó, luồng nhanh không đọc node của luồng chậm (theo hậu tố), mọi cạnh của 1 node cùng notebook, id watermark không trùng.

### Dữ liệu hiện có

**`PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` — nguồn `partner_raw_data`** (id 1–23, `load_mode = CDC`, `trg_schema = lh_vv_silver.dbo`, `is_active = 1`):

| priority | trg_tbl |
|---|---|
| 1 (12 bảng) | `slv_pn_partners`, `slv_pn_business_services`, `slv_pn_business_locations`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`, `slv_pn_business_service_i18ns`, `slv_pn_business_service_poi_link`, `slv_pn_orders`, `slv_pn_order_refs`, `slv_pn_order_item_tickets`, `slv_pn_order_item_hotels`, `slv_pn_order_item_flights` |
| 2 (11 bảng) | `slv_pn_products`, `slv_pn_product_translations`, `slv_pn_product_attributes`, `slv_pn_product_attribute_translations`, `slv_pn_product_attribute_values`, `slv_pn_product_attribute_value_translations`, `slv_pn_product_variants`, `slv_pn_product_variant_translations`, `slv_pn_product_business_service_relation`, `slv_pn_product_posts`, `slv_pn_product_post_translations` |

Công thức: `CASE WHEN trg_tbl LIKE 'slv_pn_product%' THEN 2 ELSE 1 END` (chốt 02/10). Các bảng không phụ thuộc nhau (L2 trong review: có thể gộp 1 priority).

**`PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` — nguồn `brz_3rd_crawler_poi_stream`** (id 24–37, priority 1, 1 wave):

| trg_tbl | load_mode | align_path | dedup_order | is_active |
|---|---|---|---|---|
| `slv_3p_poi` | DOC | | | 1 |
| `slv_3p_poi_address`, `_contact`, `_price`, `_opening_hours`, `_rating`, `_amenity`, `_raw_data` | DOC | | | 1 |
| `slv_3p_poi_policy` | DOC | | | **0** (khối `policies` luôn null, D1 04/10) |
| `slv_3p_poi_content` | DOC_ARRAY | | (NULL từ 04/10) | 1 |
| `slv_3p_poi_review` | DOC_ARRAY | | | 1 |
| `slv_3p_poi_media` | DOC_ARRAY | | `display_order ASC, media_id ASC` | 1 |
| `slv_3p_poi_enrichment` | LANG | | | 1 |
| `slv_3p_poi_review_i18n` | LANG_ARRAY | `poi_review` | | 1 |

### Thao tác thường gặp

```sql
-- Tắt 1 bảng extract (vd bảng policy) / bật lại (sau đó full_reload bảng đó)
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0
WHERE pl_name = 'PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00' AND src_tbl = 'brz_3rd_crawler_poi_stream' AND trg_tbl = 'slv_3p_poi_policy';
```

---

## 4. `ctrl_mng_watermark`

**Mục đích:** 3 loại dòng dùng chung 1 bảng (không thêm cột):

| Loại | `watermark_id` | Ai ghi | Vai trò |
|---|---|---|---|
| Nguồn raw (extract) | `wm_transform_<src_tbl>` | Notebook extract | Con trỏ đọc raw (`last_src_version`) + khoá chống chạy chồng của nguồn |
| Cạnh (luồng tính lại) | `wm_e__<trg_tbl>__<src_tbl>` | NB_00 (chỉ NB_00) | "Hộp thư": version đầu vào đã đọc ở lần node thành công gần nhất |
| Khoá luồng | `wm_flow__<pl_name>` | NB_00, node chạy tay | Khoá cả luồng + hạn khoá |

### DDL

```sql
CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.ctrl_mng_watermark (
    watermark_id        STRING,
    src_schema          STRING,
    src_tbl             STRING,
    trg_schema          STRING,
    trg_tbl             STRING,
    watermark_column    STRING,
    watermark_value     TIMESTAMP,
    last_success_at     TIMESTAMP,
    status              STRING,
    flow_name           STRING,
    watermark_sequence  BIGINT,
    last_run_id         STRING,
    last_src_version    BIGINT,
    last_src_table_id   STRING,     -- [SỬA 03/10] Delta table id của raw lúc ghi last_src_version (phát hiện raw bị tạo lại)
    error_message       STRING,
    lock_exec_id        STRING,
    lock_at             TIMESTAMP,
    updated_at          TIMESTAMP
) USING DELTA;
```

### Cột theo loại dòng

| Cột | Dòng nguồn (extract) | Dòng cạnh | Dòng khoá luồng |
|---|---|---|---|
| `watermark_id` | `wm_transform_partner_raw_data` | `wm_e__<trg_tbl>__<src_tbl>` | `wm_flow__<pl_name>` |
| `src_schema`, `src_tbl` | Bảng raw | Bảng đầu vào | `src_tbl` = `pl_name` |
| `trg_schema`, `trg_tbl` | NULL (dòng cấp nguồn; notebook cần **đúng 1** dòng `trg_tbl IS NULL`) | Node | NULL |
| `watermark_column` | `EventProcessedUtcTime` / `crawled_at` | `commit_ts` | NULL. Notebook không ghi `LOCK_EXPIRES_AT` |
| `watermark_value` | Max thời điểm ingest đã đọc — **chỉ để theo dõi** (không lọc theo cột này) | Thời điểm commit của version đã đọc | NULL. Không dùng làm hạn khoá |
| `last_success_at` | Lần chạy thành công gần nhất (pre-check: Start time = giá trị − 1 ngày) | Lần tiến cạnh gần nhất | — |
| `status` | `INITIALIZED` / `RUNNING` / `SUCCESS` / `FAILED` | `INITIALIZED` / `SUCCESS` / `FAILED` / `SKIPPED` / `NOT_RUN` | `RUNNING` khi nhận khoá; nhả khoá → trạng thái run (`SUCCESS`, `NO_DATA`, `PARTIAL_FAILED`, `FAILED`) |
| `flow_name` | Notebook extract | Notebook node | `NB_00_ORCHES_SLV_TO_GLD` |
| `watermark_sequence` | -1 (không dùng) | NULL | — |
| `last_run_id` | `run_id` gần nhất | `run_id` gần nhất | `run_id` gần nhất |
| `last_src_version` | **Con trỏ đọc chính**: version raw đã xử lý. NULL → pre-check luôn cho chạy, notebook phải `allow_full_scan = True` | Version đầu vào node đã đọc. Cùng table id thì chỉ ghi khi version mới ≥ version đang lưu; table id khác thì ghi version mới (bảng tạo lại) | — |
| `last_src_table_id` | Delta table id raw lúc ghi version; khác hiện tại = raw bị tạo lại | Table id đầu vào lúc đọc (`TABLE_RECREATED`) | — |
| `error_message` | Lỗi gần nhất | Lỗi node gần nhất | — |
| `lock_exec_id`, `lock_at` | Khoá chạy của nguồn; quá `running_timeout_minutes` (780, 13 giờ) → run sau lấy lại | NULL | Khoá luồng. Quá hạn khi `lock_at` NULL hoặc `lock_at` < now − timeout của **run đang xét** (NB_00: `p_lock_timeout_min`; node chạy tay: 90 phút) |
| `updated_at` | Lần sửa dòng gần nhất (kể cả RUNNING / lỗi) | Như bên | Như bên |

Luật ghi:
- **Extract**: SUCCESS / NO_DATA → tiến `last_src_version`, `last_success_at`, `watermark_value = max(cũ, mới)` cùng lúc, chỉ khi còn giữ khoá và **không lùi** (ghi khi NULL / ≤ version chốt / raw bị tạo lại). Lỗi → giữ nguyên, chỉ ghi `FAILED` + lỗi.
- **Cạnh**: NB_00 ghi bằng 1 MERGE sau runMultiple (`sql_merge_edge_wm`). Node SUCCESS / NO_DATA và có version trong `src_versions_json` → ghi version, table id, commit ts khi version mới ≥ version đang lưu hoặc table id khác. Node lỗi → chỉ ghi trạng thái và lỗi. MERGE không có `EXISTS` dòng khoá. Cạnh chưa có dòng → INSERT.
- **Khoá luồng**: nhận = `UPDATE` `lock_exec_id`, `lock_at = current_timestamp()`, `status = RUNNING` khi khoá trống hoặc `_lock_expired_sql(timeout_min)`, rồi đọc lại. `timeout_min` là của run đang nhận khoá. Nhả trong `finally` chỉ khi `lock_exec_id` còn là mình. Run mất khoá vẫn có thể ghi MERGE đích và tiến cạnh.

### Ghi chú migration — số đo watermark trước 08/10 tại `lh_vv_bronze.ctrl` (dòng 3P cũ `wm_transform_poi_raw_event`)

| watermark_id | Trạng thái biết được | Nguồn thông tin |
|---|---|---|
| `wm_transform_partner_raw_data` | Tạo lại 03/10 (INITIALIZED) → rerun FULL 04/10 (exec `de379b89`, 313 s, 1,52 triệu event). `last_src_version`, `watermark_value` sau rerun **chưa có số** — raw partner dừng nhận từ 17/09 nên `watermark_value` dự kiến ≈ 17/09 `[chưa xác nhận]` | Log rerun 04/10 |
| `wm_transform_poi_raw_event` | Tạo lại → rerun 04/10 (exec `88ea49e7`, 213 s, 21.168 tài liệu). Lần FULL trước đó (exec `43cae547`) ghi version 1043, `watermark_value` 2026-09-16 11:01:11 — raw 3P không nhận dữ liệu từ 16/09 nên giá trị sau rerun dự kiến như vậy `[chưa xác nhận]` | `POI_3P_EXTRACT_REDESIGN.md` §5.8 |

Tổng biết được trong repo: **2 dòng** nguồn extract.

### Thao tác thường gặp

```sql
-- Nhả khoá extract treo (run bị kill, chưa hết hạn) — chỉ khi chắc chắn không còn run nào chạy
UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark SET lock_exec_id = NULL, lock_at = NULL
WHERE watermark_id = 'wm_transform_partner_raw_data' AND lock_exec_id = '<exec_id trong lỗi SKIPPED_CONCURRENT>';

-- Đọc lại N commit raw gần nhất (extract)
UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark SET last_src_version = last_src_version - <N>
WHERE watermark_id = 'wm_transform_brz_3rd_crawler_poi_stream';

-- Reset nguồn để nạp lại từ đầu → lần chạy sau phải allow_full_scan = True
UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark
SET watermark_value = NULL, last_success_at = NULL, last_src_version = NULL, last_src_table_id = NULL,
    lock_exec_id = NULL, lock_at = NULL, status = 'INITIALIZED'
WHERE watermark_id = '<wm_transform_...>';

-- Ép 1 node tính lại: KHÔNG sửa dòng cạnh, dùng tham số NB_00 p_force_nodes = '<trg_tbl>'
```

---

## 5. `ctrl_cfg_schema_registry`

**Mục đích:** mapping từng cột JSON (Debezium `before` / `after`; payload tài liệu 3P) → cột bảng silver L1. Thay `TABLE_CONFIGS` viết cứng trong notebook cũ.
**Ý nghĩa:** thêm cột = INSERT 1 dòng (notebook tự `ALTER TABLE ADD COLUMNS`); đổi kiểu / rule = UPDATE rồi chạy lại.

### DDL

```sql
CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.ctrl_cfg_schema_registry (
    src_schema          STRING    COMMENT 'Schema bảng raw, vd lh_vv_bronze.dbo',
    src_tbl             STRING    COMMENT 'Bảng raw, vd partner_raw_data (khớp ctrl_mng_pipeline_config.src_tbl)',
    src_object_schema   STRING    COMMENT 'CDC: schema trong Debezium source.schema, vd public. Snapshot (3rd-party): NULL',
    src_object          STRING    COMMENT 'CDC: bảng trong Debezium source.table, vd products. Snapshot: khối trong payload, vd poi_address ($ = gốc payload)',
    trg_schema          STRING    COMMENT 'Schema bảng đích, vd lh_vv_silver.dbo',
    trg_tbl             STRING    COMMENT 'Bảng đích, khớp ctrl_mng_pipeline_config.trg_tbl',
    trg_column          STRING    COMMENT 'Tên cột trong bảng đích',
    json_path           STRING    COMMENT 'CDC: đường dẫn trong JSON before/after. Snapshot: đường dẫn trong phần tử/khối, hoặc $ / _doc.cột / _root.a / _align.a / _lang / _pos / _langs. Nhiều phần p1,p2 chỉ với HASH_*',
    data_type           STRING    COMMENT 'Kiểu Spark của cột đích: string, bigint, int, smallint, boolean, timestamp, decimal(19,4)...',
    convert_rule        STRING    COMMENT 'Cách chuyển giá trị gốc: NONE | EPOCH_S_TS | EPOCH_MS_TS | EPOCH_US_TS | DATE_DAYS | DECIMAL_BASE64 | LOWER_TRIM. Khoá suy ra (snapshot): HASH_MD5_UUID | HASH_SHA256 | HASH_SHA256_PIPE',
    is_key              BOOLEAN   COMMENT 'Cột thuộc khoá MERGE',
    key_order           INT       COMMENT 'Thứ tự trong khoá ghép (1, 2...), NULL nếu không phải khoá',
    is_toast            BOOLEAN   COMMENT 'Cột có thể nhận giá trị TOAST thay thế của Debezium (chỉ CDC, snapshot luôn false)',
    column_order        INT       COMMENT 'Thứ tự cột trong bảng đích (1, 2...)',
    is_active           BOOLEAN   COMMENT 'Bật/tắt cột; bật/tắt cả bảng dùng ctrl_mng_pipeline_config.is_active',
    description         STRING    COMMENT 'Ghi chú'
) USING DELTA
COMMENT 'Mapping cột JSON sang bảng đích (CDC partner, snapshot 3rd-party) - 1 dòng / cột';
```

### Luật cấu hình (lib kiểm tra, sai → `ConfigError` trước khi ghi)

| Luật | Áp dụng |
|---|---|
| 1 bảng đích = đúng 1 (`src_object_schema`, `src_object`) | Mọi bảng |
| Có ≥ 1 cột khoá, `key_order` không NULL / trùng; `column_order` không NULL / trùng; tên cột không trùng nhau, không trùng cột kỹ thuật | Mọi bảng |
| `data_type` được Spark xác nhận (`CAST(NULL AS <kiểu>)`); `DECIMAL_BASE64` chỉ cho `decimal(p,s)`; `LOWER_TRIM` / `HASH_*` chỉ cho `string` | Mọi bảng |
| `HASH_*` cấm ở CDC; `json_path` dạng `a.b` | CDC |
| `json_path` theo bảng tiền tố (`_lang` chỉ LANG*, `_pos` chỉ *_ARRAY, `_align.*` cần `align_path`, nhiều phần chỉ với `HASH_*`); `is_toast` = false; `src_object` `$` không dùng với *_ARRAY | Snapshot |
| Cột inactive bị bỏ qua (bảng đích không có cột đó) | Mọi bảng |

### Dữ liệu hiện có (seed `NB_CREATE_DDL`, cấu hình chốt 04/10 chiều)

**Partner** (`src_tbl = partner_raw_data`, `src_object_schema = public`): 23 bảng, **301 cột**, 61 cột `is_toast`. Rule đặc biệt: `slv_pn_business_services.last_verify_at` = `EPOCH_S_TS`; `slv_pn_orders.total_payment`, `slv_pn_order_refs.total_payment`, `slv_pn_order_refs.sub_total` = `DECIMAL_BASE64` (`decimal(19,4)`); còn lại `NONE`.

| Bảng | Khoá | Số cột | TOAST |
|---|---|---|---|
| `slv_pn_products` | id | 10 | 3 |
| `slv_pn_product_translations` | id | 7 | 1 |
| `slv_pn_product_attributes` | id | 8 | 1 |
| `slv_pn_product_attribute_translations` | id | 6 | 0 |
| `slv_pn_product_attribute_values` | id | 7 | 1 |
| `slv_pn_product_attribute_value_translations` | id | 4 | 0 |
| `slv_pn_product_variants` | id | 9 | 2 |
| `slv_pn_product_variant_translations` | id | 6 | 0 |
| `slv_pn_product_business_service_relation` | id | 5 | 0 |
| `slv_pn_product_posts` | id | 19 | 6 |
| `slv_pn_product_post_translations` | id | 15 | 5 |
| `slv_pn_partners` | id | 30 | 6 |
| `slv_pn_business_services` | id | 28 | 10 |
| `slv_pn_business_locations` | id | 12 | 3 |
| `slv_pn_hotel_room_types` | id | 25 | 4 |
| `slv_pn_hotel_rate_plans` | id | 19 | 3 |
| `slv_pn_business_service_i18ns` | business_service_id, locale (khoá ghép duy nhất) | 12 | 8 |
| `slv_pn_business_service_poi_link` | id | 6 | 0 |
| `slv_pn_orders` | id | 13 | 2 |
| `slv_pn_order_refs` | id | 11 | 2 |
| `slv_pn_order_item_tickets` | order_ref_id (1 đơn nhiều vé) | 15 | 1 |
| `slv_pn_order_item_hotels` | order_id **[chưa xác nhận K1]** | 12 | 1 |
| `slv_pn_order_item_flights` | order_id **[chưa xác nhận K1]** | 22 | 2 |

**3rd-party** (`src_tbl = brz_3rd_crawler_poi_stream`, `src_object_schema` NULL): [SỬA 10/10] 10 bảng, **98 cột (83 bật, 15 tắt)**. Chỉ `DOC` / `DOC_ARRAY`. Mọi bảng có `poi_id` (`HASH_MD5_UUID` của `_doc.source_name,_doc.source_id`) — bắt buộc vì là `entity_key` của state.

| Bảng | src_object | Khoá | Cột (bật) | Rule khoá / đặc biệt |
|---|---|---|---|---|
| `slv_3p_poi` | `$` | poi_id | 21 (15) | `HASH_MD5_UUID`, `LOWER_TRIM` (`language_code`) |
| `slv_3p_poi_address` | `poi_address` | poi_id | 21 (20) | |
| `slv_3p_poi_contact` | `poi_contact` | poi_id | 8 (5) | |
| `slv_3p_poi_price` | `poi_price` | poi_id | 5 (5) | `price_level` int, `price_min`/`price_max` decimal(18,2) |
| `slv_3p_poi_opening_hours` | `poi_opening_hours` | poi_id | 7 (7) | Thêm `open_now` |
| `slv_3p_poi_policy` | `policies` | poi_id | 2 (2) | Bảng tắt |
| `slv_3p_poi_rating` | `poi_rating` | poi_id | 5 (3) | |
| `slv_3p_poi_amenity` | `poi_amenity` | poi_id | 3 (3) | Chỉ JSON `amenity_schema_json`, `ext_attributes_json` |
| `slv_3p_poi_review` | `poi_review` | review_id | 8 (8) | `HASH_SHA256` |
| `slv_3p_poi_media` | `poi_media` | media_dedup_key | 18 (15) | `HASH_SHA256_PIPE` |

Seed lại: cell seed trong `NB_CREATE_DDL` hoặc `claude/seed_ctrl_cfg_schema_registry.py` — flatten → validate → so dòng đang có (dừng nếu mất cột trừ khi `ALLOW_REMOVE = True`) → giữ `is_active` / `description` sửa tay → ghi `overwrite` + `replaceWhere` theo (`src_schema`, `src_tbl`).

---

## 6. `ctrl_log_run` — 1 dòng / lần chạy notebook (khoá `exec_id`)

**Mục đích:** lịch sử chạy, nguồn dữ liệu cho chống chạy chồng (run `RUNNING` quá hạn → `ABANDONED`), ghim theo batch extract và lát cắt nhất quán của luồng tính lại.

### DDL

```sql
CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.ctrl_log_run (
    exec_id             STRING    COMMENT 'ID mỗi lần notebook chạy (uuid) - khoá',
    run_id              STRING    COMMENT 'RunId của pipeline (chạy tay: = exec_id)',
    pl_name             STRING    COMMENT 'Pipeline, khớp ctrl_mng_pipeline_config.pl_name',
    nb_name             STRING    COMMENT 'Notebook thực thi',
    src_schema          STRING    COMMENT 'Schema bảng nguồn raw, vd lh_vv_bronze.dbo',
    src_tbl             STRING    COMMENT 'Bảng nguồn raw, vd partner_raw_data',
    watermark_id        STRING    COMMENT 'Khớp ctrl_mng_watermark.watermark_id',
    run_mode            STRING    COMMENT 'INCREMENTAL | FULL_RELOAD | DRY_RUN',
    table_filter        STRING    COMMENT 'Danh sách trg_tbl khi chạy lại một phần, NULL = tất cả',
    src_version_from    BIGINT    COMMENT 'last_src_version trước khi chạy',
    src_version_to      BIGINT    COMMENT 'Delta version snapshot đã đọc',
    watermark_from      TIMESTAMP COMMENT 'watermark_value trước khi chạy',
    watermark_to        TIMESTAMP COMMENT 'Max watermark_column của phần đã đọc (partner: EventProcessedUtcTime, 3rd-party: crawled_at)',
    overlap_minutes     INT       COMMENT 'Số phút đọc lùi so với watermark_from',
    read_rows           BIGINT    COMMENT 'Số event đọc được',
    valid_rows          BIGINT    COMMENT 'Số event hợp lệ đưa vào xử lý',
    ignored_rows        BIGINT    COMMENT 'Số event bỏ qua (bảng chưa cấu hình, tombstone, truncate...)',
    rejected_rows       BIGINT    COMMENT 'Số event lỗi ghi vào ctrl_cdc_reject',
    ignored_detail      STRING    COMMENT 'JSON số event bỏ qua theo src_object/lý do',
    tbl_total_count     INT       COMMENT 'Số bảng đích trong phạm vi chạy',
    tbl_success_count   INT       COMMENT 'Số bảng SUCCESS',
    tbl_failed_count    INT       COMMENT 'Số bảng FAILED',
    tbl_no_data_count   INT       COMMENT 'Số bảng không có event',
    status              STRING    COMMENT 'RUNNING | SUCCESS | PARTIAL_FAILED | FAILED | NO_DATA | SKIPPED_CONCURRENT | ABANDONED',
    started_at          TIMESTAMP COMMENT 'Bắt đầu (UTC)',
    ended_at            TIMESTAMP COMMENT 'Kết thúc (UTC)',
    duration_ms         BIGINT    COMMENT 'Thời gian chạy (ms)',
    run_params          STRING    COMMENT 'JSON tham số notebook',
    error_message       STRING    COMMENT 'Lỗi tổng (tóm tắt)',
    read_mode           STRING    COMMENT 'Cách đọc raw: VERSION | FULL',
    read_note           STRING    COMMENT 'Chi tiết cách đọc: khoảng version, số file, lý do đọc FULL',
    -- [THÊM 05/10 GOLD] NB_00_ORCHES_SLV_TO_GLD (luồng tính lại silver -> gold); extract để NULL
    output_versions_json STRING    COMMENT 'NB_00: version các bảng pl sở hữu khi run SUCCESS / NO_DATA (lát cắt cho luồng khác)'
) USING DELTA
COMMENT 'Log mỗi lần chạy notebook extract CDC';
```

### Cột khác nghĩa giữa extract và NB_00

| Cột | Extract | NB_00 (luồng tính lại) |
|---|---|---|
| `src_schema`, `src_tbl` | Bảng raw | NULL |
| `watermark_id` | `wm_transform_<src_tbl>` | `wm_flow__<pl>` |
| `run_mode` | `INCREMENTAL` / `FULL_RELOAD` / `DRY_RUN` | `RUN` / `DRY_RUN` (`PLAN` không ghi) |
| `table_filter` | Danh sách `trg_tbl` | `p_force_nodes` |
| `src_version_from/to`, `watermark_from/to`, `read_rows`…`ignored_detail` | Có | NULL |
| `overlap_minutes` | Không còn dùng (giữ cho tương thích) | NULL |
| `tbl_*_count` | Số bảng | Số node ứng viên (failed gồm `FAILED` / `SKIPPED` / `NOT_RUN`) |
| `read_mode` / `read_note` | `VERSION` / `FULL`; khoảng version, số file, MB, lý do FULL | `VERSION_INBOX`; JSON tóm tắt kế hoạch (cạnh bẩn, node ứng viên, ghim) ≤ 8000 ký tự |
| `output_versions_json` | NULL | Version các node của pl khi run SUCCESS / NO_DATA (RUN) |
| Cách ghi | MERGE theo `exec_id` (mở RUNNING, đóng cuối run) | Append dòng RUNNING, UPDATE khi đóng; không nhận được khoá → append 1 dòng `SKIPPED_CONCURRENT` |

### Ghi chú migration — log đã thấy trước 08/10 tại vị trí control cũ

| exec_id | Notebook | Kết quả |
|---|---|---|
| `de379b89…` | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` (rerun FULL 04/10) | 313 s; 1,52 triệu event; điều khiển + commit 132 s (42%) |
| `88ea49e7…` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` (rerun FULL 04/10) | 213 s; 21.168 tài liệu, 19.046 địa điểm; điều khiển + commit 118 s (55%) |

Log trước 04/10 16:09 có thể đã mất khi tạo lại 7 bảng ctrl (`RERUN_ALL_0410.sql`, sao lưu log là tuỳ chọn).

---

## 7. `ctrl_log_table_run` — 1 dòng / bảng đích (hoặc node) / lần chạy

### DDL

```sql
CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.ctrl_log_table_run (
    exec_id             STRING    COMMENT 'Khớp ctrl_log_run.exec_id',
    run_id              STRING    COMMENT 'RunId của pipeline',
    pl_name             STRING    COMMENT 'Pipeline',
    src_schema          STRING    COMMENT 'Schema bảng nguồn raw',
    src_tbl             STRING    COMMENT 'Bảng nguồn raw',
    src_object          STRING    COMMENT 'Bảng trong Debezium source.table',
    trg_schema          STRING    COMMENT 'Schema bảng đích, vd lh_vv_silver.dbo',
    trg_tbl             STRING    COMMENT 'Bảng đích, vd slv_products',
    priority            INT       COMMENT 'Wave chạy (ctrl_mng_pipeline_config.priority)',
    attempt_no          INT       COMMENT 'Lần thử (1 = lần đầu, >1 = retry)',
    input_rows          BIGINT    COMMENT 'Số event của bảng trong phần đã đọc (3rd-party: số dòng sau khi tách khối/mảng)',
    stale_rows          BIGINT    COMMENT 'Số event cũ hơn state, bị bỏ qua',
    applicable_rows     BIGINT    COMMENT 'Số event mới hơn state, được áp dụng',
    entity_rows         BIGINT    COMMENT 'Số entity (khoá) đưa vào MERGE (3rd-party: số khoá bảng)',
    upsert_event_rows   BIGINT    COMMENT 'Số event c/r/u được áp dụng',
    delete_event_rows   BIGINT    COMMENT 'Số event d được áp dụng',
    inserted_rows       BIGINT    COMMENT 'MERGE: số dòng insert',
    updated_rows        BIGINT    COMMENT 'MERGE: số dòng update (gồm xoá mềm)',
    cast_null_rows      BIGINT    COMMENT 'Số giá trị có ở raw nhưng thành NULL sau chuyển kiểu',
    rejected_rows       BIGINT    COMMENT 'Số event của bảng bị reject',
    status              STRING    COMMENT 'SUCCESS | FAILED | NO_DATA | SKIPPED',
    started_at          TIMESTAMP COMMENT 'Bắt đầu (UTC)',
    ended_at            TIMESTAMP COMMENT 'Kết thúc (UTC)',
    duration_ms         BIGINT    COMMENT 'Thời gian xử lý bảng (ms)',
    error_message       STRING    COMMENT 'Lỗi của bảng (tóm tắt)',
    -- [THÊM 05/10 GOLD] node của luồng tính lại (NB_LIB_TRANSFORM_SLV_GLD); extract để NULL
    src_versions_json   STRING    COMMENT 'Node: JSON {bảng đầu vào: {v, tid, ts, dirty}} đã đọc',
    trg_version         BIGINT    COMMENT 'Node: version bảng đích sau MERGE',
    deactivated_rows    BIGINT    COMMENT 'Node: số dòng xoá mềm',
    qg_json             STRING    COMMENT 'Node: kết quả exit QG, hộp thư, cảnh báo'
) USING DELTA
COMMENT 'Log từng bảng đích trong mỗi lần chạy extract CDC';
```

| Cột | Extract | Node luồng tính lại |
|---|---|---|
| `priority` | Wave | Tầng DAG |
| `attempt_no` | 1 + số lần retry lỗi tạm thời | Luôn 1 (runMultiple retry 0) |
| `input_rows`…`delete_event_rows`, `cast_null_rows` | Có | NULL (trừ `entity_rows` = số dòng build) |
| `inserted_rows`, `updated_rows` | Từ kết quả MERGE | Từ đếm diff trước MERGE |
| `deactivated_rows` | NULL | Số dòng xoá mềm |
| `error_message` | Lỗi; bảng thành công có NULL do chuyển kiểu → `{"cast_null": {cột: n}}` | Lỗi / lý do `SKIPPED` |
| `src_versions_json` | NULL | `{"<bảng đầu vào>": {"v": version đã đọc, "tid": table id, "ts": commit ts (khi đọc bản mới nhất), "dirty": lý do | null}}` |
| `qg_json` | NULL | `{"mode", "force", "inbox": {bảng: lý do cạnh}, "rows", "blocks", "warns", "metrics"}` (≤ 16000 ký tự) |
| Ghi | Luồng chính append 1 lần cuối run | Mỗi node append 1 dòng (cả FAILED / SKIPPED / NO_DATA); append mù không xung đột |

Gold run 1 (exec `c8d4218f`, theo DAG): `slv_poi_source_map` 19.070 · `slv_poi` 19.070 · `slv_poi_address` 19.070 · `slv_poi_localization` 57.200 · `slv_poi_destination` 22.298 · `gld_srv_poi_multi_lang` 57.198 · `gld_srv_poi_destination_membership` 22.293 · `gld_srv_poi_registry` 19.066 (số dòng build).

---

## 8. `ctrl_cdc_state` — 1 dòng / entity / bảng đích (chỉ extract)

**Mục đích:** nhớ event mới nhất đã áp dụng cho từng entity → chạy lại / đọc FULL không áp dụng lại event cũ. **Là trạng thái, không xoá.**

### DDL

```sql
CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.ctrl_cdc_state (
    trg_schema          STRING    COMMENT 'Schema bảng đích (khoá)',
    trg_tbl             STRING    COMMENT 'Bảng đích (khoá)',
    entity_key          STRING    COMMENT 'Giá trị khoá; khoá ghép nối bằng | (khoá). 3rd-party: poi_id cho mọi bảng',
    src_schema          STRING    COMMENT 'Schema bảng nguồn raw',
    src_tbl             STRING    COMMENT 'Bảng nguồn raw',
    src_object          STRING    COMMENT 'Bảng trong Debezium source.table',
    cdc_op              STRING    COMMENT 'Op của event mới nhất: c | r | u | d',
    cdc_ts_ms           BIGINT    COMMENT 'source.ts_ms của event mới nhất (3rd-party: crawled_at tính ms)',
    cdc_lsn             BIGINT    COMMENT 'source.lsn của event mới nhất',
    raw_ingested_at     TIMESTAMP COMMENT 'EventProcessedUtcTime của event mới nhất (3rd-party: crawled_at)',
    is_deleted          BOOLEAN   COMMENT 'Entity đang ở trạng thái xoá mềm',
    src_version         BIGINT    COMMENT 'Delta version raw của lần áp dụng',
    last_run_id         STRING    COMMENT 'run_id lần cập nhật gần nhất',
    updated_at          TIMESTAMP COMMENT 'Thời điểm cập nhật state (UTC)'
) USING DELTA
PARTITIONED BY (src_tbl) -- FL_00 ForEach chạy tuần tự. Partition theo src_tbl để MERGE của partner và 3P (chạy tay hoặc pipeline khác) chỉ đọc partition của nguồn mình
COMMENT 'State CDC theo entity - đảm bảo chạy lại không áp dụng event cũ';
```

| | Partner (CDC) | 3rd-party (snapshot) |
|---|---|---|
| `entity_key` | Khoá bảng đích (khoá ghép nối `\|` theo `key_order`) | `poi_id` cho mọi bảng (tham số `state_key = "doc"`); `"row"` → khoá bảng |
| Thứ tự event | (`cdc_ts_ms`, `cdc_lsn`, `raw_ingested_at`, `is_deleted`) — trùng thì xoá thắng | `cdc_ts_ms` = crawled_at (ms), `cdc_lsn` NULL, `raw_ingested_at` = crawled_at |
| `cdc_op` / `is_deleted` | c / r / u / d / theo `op = d` | NULL / false |
| Ghi | 1 MERGE / run cho các bảng SUCCESS; dòng khớp chỉ cập nhật khi thứ tự mới ≥ đang lưu (**không lùi**); thêm điều kiện `t.src_tbl = <nguồn>` | Như bên |

**Ghi chú migration — số đo state trước 08/10 tại vị trí control cũ:** 3P ~188k dòng (13 bảng × POI có khối, đo 04/10). Partner: chưa có số → snapshot.

Kiểm tra: `SELECT trg_tbl, entity_key, COUNT(*) FROM lh_vv_ctrl.dbo.ctrl_cdc_state GROUP BY 1, 2 HAVING COUNT(*) > 1` — kỳ vọng 0 dòng.

---

## 9. `ctrl_cdc_reject` — 1 dòng / event (hoặc phần tử) lỗi (chỉ extract)

### DDL

```sql
CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.ctrl_cdc_reject (
    event_hash          STRING    COMMENT 'sha2(source||op||before||after) - khoá MERGE',
    pl_name             STRING    COMMENT 'Pipeline',
    src_schema          STRING    COMMENT 'Schema bảng nguồn raw',
    src_tbl             STRING    COMMENT 'Bảng nguồn raw',
    src_object          STRING    COMMENT 'Bảng trong Debezium source.table',
    src_db              STRING    COMMENT 'Database trong Debezium source.db (3rd-party: source_name)',
    trg_schema          STRING    COMMENT 'Schema bảng đích (nếu xác định được)',
    trg_tbl             STRING    COMMENT 'Bảng đích (nếu xác định được)',
    cdc_op              STRING    COMMENT 'Op của event',
    entity_key          STRING    COMMENT 'Khoá entity (có thể NULL nếu lỗi thiếu khoá)',
    cdc_ts_ms           BIGINT    COMMENT 'source.ts_ms',
    cdc_lsn             BIGINT    COMMENT 'source.lsn',
    raw_ingested_at     TIMESTAMP COMMENT 'EventProcessedUtcTime',
    reject_reason       STRING    COMMENT 'MISSING_ENTITY_KEY | MISSING_EVENT_ORDER | MISSING_RAW_CURSOR | INVALID_PAYLOAD',
    reject_detail       STRING    COMMENT 'Mô tả chi tiết',
    before_payload      STRING    COMMENT 'Giá trị before gốc',
    after_payload       STRING    COMMENT 'Giá trị after gốc (3rd-party: normalized_payload, hoặc phần tử lỗi của 1 bảng)',
    source_payload      STRING    COMMENT 'Giá trị source gốc (3rd-party: JSON event_id, source_name, source_id, language_code, crawled_at)',
    first_run_id        STRING    COMMENT 'run_id lần đầu phát hiện',
    last_run_id         STRING    COMMENT 'run_id lần gần nhất phát hiện',
    reject_count        INT       COMMENT 'Số lần bị đọc lại và reject',
    first_rejected_at   TIMESTAMP COMMENT 'Lần đầu reject (UTC)',
    last_rejected_at    TIMESTAMP COMMENT 'Lần gần nhất reject (UTC)',
    is_resolved         BOOLEAN   COMMENT 'Đã xử lý xong (đánh dấu tay hoặc khi nạp lại)',
    resolved_at         TIMESTAMP COMMENT 'Thời điểm đánh dấu đã xử lý'
) USING DELTA
PARTITIONED BY (src_tbl) -- FL_00 ForEach chạy tuần tự. Partition theo src_tbl để MERGE của partner và 3P (chạy tay hoặc pipeline khác) chỉ đọc partition của nguồn mình
COMMENT 'Event CDC lỗi, không áp dụng được vào bảng đích';
```

| | Partner | 3rd-party |
|---|---|---|
| `event_hash` | sha256(source ‖ op ‖ before ‖ after) | Tài liệu lỗi: sha256(event_id, source_name, source_id, crawled_at, payload). Phần tử lỗi: sha256(bảng, định danh, lang, phần tử, phần tử align) → crawl lại không sinh dòng trùng |
| Lỗi phân loại | `INVALID_PAYLOAD` (op lạ, thiếu `source.table`, `after` / `before` thiếu hoặc rỗng), `MISSING_EVENT_ORDER` (thiếu `ts_ms`), `MISSING_RAW_CURSOR` (thiếu thời điểm ingest) | `MISSING_ENTITY_KEY` (thiếu `source_name` / `source_id`), `INVALID_PAYLOAD` (payload rỗng / không phải JSON object), `MISSING_EVENT_ORDER` (thiếu `crawled_at`) |
| Lỗi theo bảng | `MISSING_ENTITY_KEY` (khoá NULL / rỗng / không chuyển được kiểu), `INVALID_PAYLOAD` (JSON hỏng) | Phần tử thiếu khoá (review thiếu author / time, media thiếu `photo_api_uri`, bản dịch lệch số phần tử) / không phải JSON object |
| Đọc lại cùng event | `reject_count + 1`, cập nhật `last_*`, lý do | Như bên |

Event **bỏ qua** (tombstone, truncate, message, bảng chưa cấu hình, ngoài phạm vi / ngoài tham số `sources`) không ghi ở đây, chỉ đếm ở `ctrl_log_run.ignored_rows` / `ignored_detail`.

**Ghi chú migration — số đo reject trước 08/10 tại vị trí control cũ:** partner ~199k dòng, gần như toàn bộ `INVALID_PAYLOAD` "after rỗng" của 10 bảng `slv_pn_product*` + 10 event `order_item_*` (upstream gửi `after = ''`, xem `99_PAIN_POINTS.md`). 3P: chưa có số → snapshot.

```sql
SELECT src_tbl, trg_tbl, reject_reason, reject_detail, COUNT(*) AS so_dong, SUM(reject_count) AS so_lan
FROM lh_vv_ctrl.dbo.ctrl_cdc_reject WHERE NOT is_resolved GROUP BY 1, 2, 3, 4 ORDER BY so_dong DESC;
```

---

## 10. Lịch sử thay đổi (tóm tắt)

| Ngày | Thay đổi |
|---|---|
| 01/10 | Registry v2 (`src_*` / `trg_*`, `convert_rule`, bỏ `table_is_active`, order từ 1); `exec_id` cho 2 bảng log; `updated_at` cho watermark. Bản thiết kế có Switch theo nguồn; JSON FL_00 trong repo không có Switch |
| 02/10 | Đọc raw theo version (`_delta_log`) thay lọc `EventProcessedUtcTime`; thêm `read_mode`, `read_note`; reject "after rỗng" ở bước phân loại |
| 03/10 | Tiền tố silver theo nguồn (`slv_pn_*`, `slv_3p_poi_*`); tạo lại 7 bảng ctrl; `last_src_table_id`, `lock_exec_id`, `lock_at` vào DDL; sửa INSERT watermark 16 cột / 17 giá trị; sửa công thức priority; khoá nguyên tử; state không lùi; `cast_null_policy` |
| 04/10 | `pipeline_config` + `load_mode`, `align_path`, `dedup_order`; 14 bảng 3P; `ctrl_cdc_state` / `ctrl_cdc_reject` `PARTITIONED BY (src_tbl)`; registry 3P 182 cột (36 tắt), `policy` tắt, content khoá + `content_type`; tạo lại toàn bộ ctrl + silver 2 luồng (`RERUN_ALL_0410.sql`) |
| 05/10 | `ctrl_log_run.output_versions_json`; `ctrl_log_table_run` + `src_versions_json`, `trg_version`, `deactivated_rows`, `qg_json`. Notebook trong repo chưa ghi `LOCK_EXPIRES_AT` và chưa cho lùi dấu đã đọc khi cùng table id |
| 08/10 | Chuyển 7 bảng sang `lh_vv_ctrl.dbo`, seed mới từ repo (không copy vị trí cũ), đổi danh tính nguồn 3P sang `brz_3rd_crawler_poi_stream` / `wm_transform_brz_3rd_crawler_poi_stream`, bỏ cell DROP trong `NB_CREATE_DDL`, không seed cạnh gold |

## 11. Việc còn lại liên quan ctrl

| # | Việc |
|---|---|
| 1 | Chạy `CHECK_CTRL_SNAPSHOT.py` → cập nhật số liệu thật vào mục "Dữ liệu hiện có" |
| 2 | Bảo trì: bật `optimizeWrite` / `autoCompact` cho 7 bảng ctrl + lịch OPTIMIZE / VACUUM hằng tuần (≥ 7 ngày, không chồng FL_00) |
| 3 | Hạn giữ `ctrl_cdc_reject` (partner tăng mỗi run khi nguồn chưa sửa `after` rỗng) |
| 4 | Chốt khoá `slv_pn_order_item_hotels` / `_flights` (K1) + replica identity (H2) với team nguồn |
| 5 | DROP `ctrl_cfg_schema_registry_bak_20261001` khi extract mới chạy ổn |
| 6 | `claude/seed_ctrl_poi_3rd_party.sql`, `APPLY_3P_CONFIG_0410.sql`, `RESULT_RERUN_0410.py`, `DOC_MAP_0410.diff`, `NB_EXTRACT_PARTNER_CDC.ipynb` đã cũ — không dùng |
