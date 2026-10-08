# NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV — Extract Debezium CDC partner → `slv_pn_*`

> Cập nhật: 08/10/2026. Bản code: `claude/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb` (project, 04/10). Luồng chi tiết: `claude/NB_EXTRACT_PARTNER_CDC_FLOW.md`, thiết kế: `claude/PARTNER_EXTRACT_REDESIGN.md`.
> Hàm dùng chung: `NB_LIB_EXTRACT_RAWDATA.md`.

## 1. Mô tả

Đọc event Debezium từ `lh_vv_bronze.dbo.partner_raw_data`, đưa mỗi bảng Postgres về 1 bảng `lh_vv_silver.dbo.slv_pn_<bảng>` (23 bảng): parse `before` / `after`, chuyển kiểu theo registry, giữ 1 bản mới nhất / khoá, xoá mềm theo `op = d`, xử lý cột TOAST. Không rule nghiệp vụ.

| | |
|---|---|
| Gọi bởi | `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` → ForEach nguồn → If_HasWork (pre-check Get Metadata) → Switch `item().src_tbl = partner_raw_data` |
| Đọc | `ctrl_mng_pipeline_config`, `ctrl_cfg_schema_registry`, `ctrl_mng_watermark`, `ctrl_cdc_state`; raw: file `add` của commit mới theo `_delta_log` (VERSION) hoặc `VERSION AS OF` toàn bộ (FULL) |
| Ghi | `slv_pn_*` (MERGE, xoá mềm), `ctrl_cdc_state`, `ctrl_cdc_reject`, `ctrl_log_run`, `ctrl_log_table_run`, `ctrl_mng_watermark` |
| Song song | Bảng cùng `priority` chạy cùng lúc (`max_parallel` luồng): wave 1 = 12 bảng nghiệp vụ / đơn hàng, wave 2 = 11 bảng `slv_pn_product*` |
| Chạy lại | An toàn: state theo entity bỏ event đã áp dụng; MERGE theo khoá; watermark chỉ tiến khi mọi bảng thành công, không lùi |
| Chạy chồng | Khoá nguyên tử trên dòng `wm_transform_partner_raw_data` → run thứ 2 `SKIPPED_CONCURRENT` |
| Đầu ra | Exit JSON (`build_summary`); FAILED / PARTIAL_FAILED / SKIPPED_CONCURRENT → raise (pipeline báo lỗi) |

## 2. Ý nghĩa

Thay notebook cũ `1. parsing_bronze_partner` + bảng `lh_vv_bronze.partner.*`:

| Cũ | Mới |
|---|---|
| `TABLE_CONFIGS` viết cứng trong notebook | `ctrl_cfg_schema_registry` (thêm cột = INSERT 1 dòng) |
| Lọc `EventProcessedUtcTime > watermark − overlap` → raw không có stats nên quét cả bảng, event commit trễ có thể bị bỏ sót | Đọc theo version Delta |
| TOAST xử lý bằng `COALESCE` → cột bị xoá trắng thật ở nguồn vẫn giữ giá trị cũ | Phân biệt giá trị thay thế với NULL thật (`_unavailable__`, `_has_value__`) |
| Không chống chạy chồng, không reject, không table log | Khoá, `ctrl_cdc_reject`, `ctrl_log_table_run`, state không lùi |
| Silver nằm ở bronze (`lh_vv_bronze.partner.*`) | `lh_vv_silver.dbo.slv_pn_*` |

## 3. Tham số

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `pl_name` | `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` | `@pipeline().Pipeline` |
| `run_id` | "" | `@pipeline().RunId`; trống = `exec_id` |
| `src_schema`, `src_tbl` | `lh_vv_bronze.dbo`, `partner_raw_data` | Bảng raw |
| `overlap_minutes` | 10 | Không còn dùng (giữ để pipeline cũ truyền không lỗi) |
| `allow_full_scan` | False | Đọc FULL khi không đọc theo version được |
| `max_parallel` | 4 | Bảng đồng thời / wave (rerun 04/10 dùng 12) |
| `max_retries` | 1 | Thử lại bảng khi lỗi tạm thời |
| `table_filter` | "" | `"slv_pn_products,slv_pn_orders"`; rỗng = tất cả |
| `full_reload` | False | Đọc toàn bộ raw, bỏ state (dùng kèm `table_filter`) |
| `dry_run` | False | Chỉ đọc, parse, đếm |
| `stop_on_failure` | False | Wave lỗi → dừng wave sau |
| `cast_null_policy` | FAIL | FAIL: bảng có giá trị thành NULL khi chuyển kiểu → FAILED trước MERGE; WARN: chỉ cảnh báo |
| `running_timeout_minutes` | 60 | > thời gian chạy dài nhất và > timeout activity (45 phút) |

## 4. Hằng số Debezium

| Hằng số | Giá trị |
|---|---|
| `VALID_OPS` / `UPSERT_OPS` | `c r u d` / `c r u` (`r` = snapshot) |
| `TOAST_SENTINEL` | `__debezium_unavailable_value` — Debezium gửi cho cột TOAST không đổi |
| `IGNORE_REASONS` | `TOMBSTONE`, `OP_TRUNCATE`, `OP_MESSAGE`, `UNCONFIGURED`, `OUT_OF_SCOPE` (chỉ đếm, không phải lỗi) |
| `SOURCE_FIELDS` | `schema`, `table`, `db`, `ts_ms`, `lsn` |
| `ORDER_ASC` / `ORDER_DESC` | (`_cdc_ts_ms`, `_cdc_lsn`, `_raw_ingested_at`, `_is_delete`) — trùng thì event xoá mới hơn |
| `NB_NAME` | Tên notebook đang chạy (fallback tên cố định) |

## 5. Luồng

```
run_extract()
  build_context()                         tham số → RunContext (kiểm tra src, cast_null_policy)
  load_table_specs(ctx)                   allowed_modes = ("CDC",) → 23 TableSpec
  load_watermark(ctx)
  run_controlled(ctx, process_run)        [lib §14: khoá → run log → chốt version → body → watermark → log → nhả khoá]
    process_run:
      read_raw → classify_events → persist   (đọc 1 lần cho mọi bảng)
      profile_events                         1 job: đếm + watermark_to
      load_state(specs) → persist            (bỏ khi full_reload)
      run_waves → run_tables                 bảng 0 event → NO_DATA; còn lại theo wave
        process_table → process_with_retry → _run_table:
          ensure_target → build_table_events → persist → table_stats
          → cast null? (FAIL → CastNullError) → reject_rows (khoá NULL)
          → resolve_latest (gộp TOAST, 1 dòng / entity) → merge_into_target → state_rows
      decide_status
      commit: commit_state → commit_rejects → append ctrl_log_table_run
EXIT: in JSON; FAILED / PARTIAL_FAILED / SKIPPED_CONCURRENT → raise RuntimeError
```

## 6. Chi tiết hàm

### A. Đọc và phân loại raw

| Hàm | Mô tả |
|---|---|
| `objects_cond(objects)` | Điều kiện event thuộc tập (schema, bảng Debezium); schema None = mọi schema |
| `read_raw(ctx)` | `read_incremental(ctx, ["before", "after", "source", "op"], "_raw_ingested_at")` |
| `classify_events(raw, scope, configured)` | Parse `source` 1 lần; đổi tên cột payload sang `_before`, `_after`, `_source`, `_op`; gắn `_status` / `_reason` / `_reject_detail` theo luật dưới (luật đầu tiên khớp quyết định); event IGNORED bỏ payload cho cache nhẹ |
| `profile_events(classified)` | 1 job groupBy (status, reason, schema, object): `read / valid / ignored / rejected`, `ignored_detail`, `valid_by_src`, `watermark_to = max(_raw_ingested_at)` của mọi dòng đã đọc (kể cả IGNORED) |
| `reject_rows(df, ctx, reason, detail, trg_schema, trg_tbl)` | Chuẩn hoá theo schema `ctrl_cdc_reject`; `event_hash = sha256(source ‖ op ‖ before ‖ after)` (ngăn `\u0001`) → đọc lại không sinh dòng trùng |

Luật phân loại:

| # | Điều kiện | Trạng thái | Lý do |
|---|---|---|---|
| 1 | `op`, `before`, `after` đều NULL | IGNORED | `TOMBSTONE` |
| 2 | `op = t` / `op = m` | IGNORED | `OP_TRUNCATE` / `OP_MESSAGE` |
| 3 | `op` NULL hoặc ngoài `c r u d` | REJECTED | `INVALID_PAYLOAD` (op không hợp lệ) |
| 4 | Thiếu `source.table` | REJECTED | `INVALID_PAYLOAD` |
| 5 | Bảng không có trong registry | IGNORED | `UNCONFIGURED` |
| 6 | Bảng có trong registry nhưng ngoài phạm vi chạy (`table_filter`, bảng tắt) | IGNORED | `OUT_OF_SCOPE` |
| 7 | `c / r / u` mà `after` NULL / rỗng | REJECTED | `INVALID_PAYLOAD` (thiếu after / after rỗng) |
| 8 | `d` mà `before` NULL / rỗng | REJECTED | `INVALID_PAYLOAD` |
| 9 | Thiếu `source.ts_ms` | REJECTED | `MISSING_EVENT_ORDER` |
| 10 | Thiếu thời điểm ingest | REJECTED | `MISSING_RAW_CURSOR` |
| — | Còn lại | VALID | |

### B. Xử lý 1 bảng

| Hàm | Mô tả |
|---|---|
| `build_table_events(spec, valid_df, state_df)` | Lọc event của bảng → payload = `before` nếu `op = d`, không thì `after` → parse cột cấp 1 bằng `parse_json_strings` (đường dẫn lồng nhau dùng `get_json_object`) → `_raw__<cột>` → chuyển kiểu (`convert_sql`); cột TOAST: sentinel → NULL. Cờ: `_parse_failed`, `_cn__<cột>` (có ở raw, thành NULL), `_unavailable__<cột TOAST>` (luôn true/false), `_key_null` (khoá NULL / rỗng / JSON hỏng), `_entity_key` (khoá đơn: chuỗi; khoá ghép: nối `\|` theo `key_order`), `_is_stale` (thứ tự event ≤ state), `_applicable`. Payload gốc chỉ giữ cho dòng reject |
| `table_stats(spec, events)` | 1 job: `input_rows`, `rejected_rows`, `stale_rows`, `applicable_rows`, `upsert_event_rows`, `delete_event_rows`, `entity_rows`, `_cn__*` |
| `resolve_latest(spec, events)` | Cột TOAST: giá trị của event gần nhất **có cung cấp** giá trị (không sentinel, không event xoá) — bọc `struct` để `last(ignorenulls)` không bỏ NULL thật; `_has_value__<cột>` = false khi cả batch chỉ có sentinel. Event xoá bị loại khỏi bước điền vì `before` (REPLICA IDENTITY DEFAULT) có thể chỉ có khoá. Rồi giữ 1 dòng mới nhất / entity (`ORDER_DESC`) |
| `build_merge_sql(spec, target, view)` | Khớp + `_cdc_op = d` → `deleted = true`; khớp → cập nhật mọi cột không khoá (TOAST: `CASE WHEN s._has_value__c THEN s.c ELSE t.c END`), `deleted = false`, `_ingested_at = now`, `_source_db`; không khớp và không xoá → INSERT; không khớp + xoá → bỏ qua |
| `merge_into_target(spec, latest, ctx)` | `run_merge` với view `_v_<exec_id[:8]>_<trg_tbl>` |
| `_run_table(res, valid_df, state_df, ctx)` | Các bước của 1 bảng; cast null + FAIL → `CastNullError` **trước MERGE** (không ghi đích, không ghi state); `dry_run` dừng trước MERGE |
| `process_table(spec, valid_df, state_df, ctx, wave)` | `process_with_retry` (lib) |

### C. Chạy theo wave và commit

| Hàm | Mô tả |
|---|---|
| `run_waves(specs, profile, valid_df, state_df, ctx, results)` | `run_tables(specs, profile.events_for, …)` |
| `target_of(specs, field)` | Tra `trg_schema` / `trg_tbl` theo bảng nguồn của event → reject phân loại vẫn biết bảng đích |
| `commit_rejects(classified, profile, results, ctx)` | Reject theo bảng của bảng SUCCESS + reject phân loại → `merge_rejects(..., ctx.src_tbl)` |
| `commit(classified, profile, results, ctx)` | Thứ tự: `commit_state` → `commit_rejects` → append `ctrl_log_table_run`. Chết giữa chừng: lần sau đọc lại, state lọc event đã áp dụng |

### Main

| Hàm | Mô tả |
|---|---|
| `build_context()` | Tham số → `RunContext`; `run_mode` = DRY_RUN > FULL_RELOAD > INCREMENTAL; `run_params` JSON |
| `process_run(ctx, specs, configured, out)` | Phần riêng của partner bên trong `run_controlled` |
| `run_extract()` | `build_context` → `load_table_specs` → `load_watermark` → `run_controlled` |

## 7. Bảng đích và quy tắc TOAST

- 23 bảng, khoá và số cột: `CTRL_TABLES_CONTEXT.md` §5. Cột kỹ thuật: `deleted`, `_ingested_at`, `_source_db`.
- 61 cột `is_toast` (giá trị lớn: JSON, text dài). Entity mới mà event đầu chỉ có sentinel → cột đó NULL (Debezium không gửi giá trị, cần snapshot lại).
- `DECIMAL_BASE64`: `orders.total_payment`, `order_refs.total_payment`, `order_refs.sub_total`. `EPOCH_S_TS`: `business_services.last_verify_at`. Cột ngày `order_item_*` là timestamptz ISO (`NONE`); lấy ngày giờ VN bằng `from_utc_timestamp(..., 'Asia/Ho_Chi_Minh')`.

## 8. Số liệu đo (rerun FULL 04/10, exec `de379b89`)

| Giai đoạn | Thời gian |
|---|---|
| Nạp cấu hình + watermark | 33 s |
| Nhận khoá | 23 s |
| Mở run log + chốt version | 27 s |
| Đọc + phân loại 1,52 triệu event (FULL, CPU 16/16 core) | 110 s |
| Wave bảng (12 luồng, CPU bão hoà; 40–57 s / bảng kể cả bảng 1 dòng) | 69 s |
| Commit state / reject / table log | 31 s |
| Watermark + run log + nhả khoá | 18 s |
| **Tổng** / phần điều khiển + commit | **313 s** / 132 s (42%) |

## 9. Vận hành

| Việc | Cách |
|---|---|
| Pipeline | Notebook activity nhánh `partner_raw_data`: `pl_name = @pipeline().Pipeline`, `run_id = @pipeline().RunId`; timeout 45 phút (< 60), retry 0, Concurrency pipeline = 1 |
| Chạy thử | `dry_run = True` |
| Nạp lại vài bảng | `table_filter = "..."`, `full_reload = True` (watermark không đổi; tạm dừng lịch khi chạy lâu) |
| Chạy lại sau lỗi | Chạy bình thường |
| `CastNullError` | Sửa `data_type` / `convert_rule` trong registry rồi chạy lại; hoặc chấp nhận NULL: 1 lần `cast_null_policy = "WARN"` |
| `SKIPPED_CONCURRENT` mà không có run nào chạy | Chờ quá 60 phút, hoặc nhả tay (SQL ở `CTRL_TABLES_CONTEXT.md` §4) |
| Lần đầu / sau reset / `VersionGapError` | 1 lần `allow_full_scan = True`; sau đó `False` |
| Raw | Không VACUUM raw < 7 ngày; không giảm `delta.logRetentionDuration` dưới thời gian pipeline có thể dừng |

```sql
SELECT status, run_mode, read_mode, read_rows, valid_rows, ignored_rows, rejected_rows, tbl_success_count, tbl_failed_count,
       watermark_from, watermark_to, duration_ms, error_message
FROM lh_vv_bronze.ctrl.ctrl_log_run WHERE src_tbl = 'partner_raw_data' ORDER BY started_at DESC LIMIT 10;
```

## 10. Vấn đề đã biết

| # | Nội dung | Trạng thái |
|---|---|---|
| Dữ liệu | Upstream gửi `after = ''` cho 100% event 10 bảng `product*` (199.408 event) + 10 event `order_item_*` → reject `INVALID_PAYLOAD` | Chờ team nguồn sửa Debezium / Eventstream, rồi snapshot lại |
| Dữ liệu | Update storm: >99,9% raw là update lặp y hệt (`hotel_room_types` 341.204 event / 203 dòng, `hotel_rate_plans` 274.630 / 162, `orders` 26.253 / 28) | Đề xuất phía Postgres `suppress_redundant_updates_trigger()` |
| Dữ liệu | Raw partner không nhận dữ liệu từ 17/09 | Kiểm tra Eventstream |
| K1 | Khoá `order_item_hotels` / `_flights` = `order_id` chưa xác nhận | Chờ team nguồn |
| H2 | Event xoá lấy khoá từ `before`; REPLICA IDENTITY DEFAULT chỉ gửi PK → bảng có khoá silver khác PK bị reject `MISSING_ENTITY_KEY` khi xoá | Đã nắm, chờ PK + replica identity 23 bảng |
| M5 | Nhánh cập nhật MERGE vô điều kiện + `_ingested_at = now` → update storm ghi lại silver liên tục | Thêm `WHEN MATCHED AND NOT (t.c <=> s.c AND …)` sau khi xác nhận |
| L4 | Khoá ghép nối `\|`: giá trị chứa `\|` có thể trùng `_entity_key` | Window theo cột khoá thật (như 3P) |
| C1 | Mất khoá giữa chừng vẫn SUCCESS; MERGE đích không chặn ghi lùi | Low nhờ Concurrency = 1 + timeout activity < 60 |
| L2 | Wave 2 chỉ chạy khi wave 1 xong; bảng không phụ thuộc nhau | Có thể gộp 1 priority |
