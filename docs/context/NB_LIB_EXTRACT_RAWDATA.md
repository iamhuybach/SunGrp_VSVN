# NB_LIB_EXTRACT_RAWDATA — Thư viện dùng chung cho extract raw → silver L1

> Cập nhật: 08/10/2026. Bản code: `claude/NB_LIB_EXTRACT_RAWDATA.ipynb` (project, 04/10). 14 mục, ~2.150 dòng.
> Liên quan: `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `CTRL_TABLES_CONTEXT.md`.

## 1. Mô tả

Notebook thư viện, được gọi bằng `%run NB_LIB_EXTRACT_RAWDATA` ở cell ngay sau cell tham số của mỗi notebook extract. Chứa toàn bộ phần **không phụ thuộc nguồn**: đọc raw theo version Delta, khoá chống chạy chồng, watermark, run log / table log, nạp + kiểm tra cấu hình từ ctrl, chuyển kiểu theo `convert_rule`, parse JSON, MERGE, state theo entity, reject, chạy song song theo wave và khung điều khiển 1 lần chạy (`run_controlled`).

Notebook extract chỉ còn viết phần riêng của nguồn: đọc + phân loại raw, xử lý 1 bảng, commit.

| | |
|---|---|
| Được gọi bởi | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` (và extract nguồn mới sau này) |
| Đọc / ghi khi `%run` | **Không**. Chỉ định nghĩa hằng số, class, hàm; không `spark.conf.set` |
| Default lakehouse | `lh_vv_bronze` (cùng notebook gọi); tên bảng luôn đầy đủ `lakehouse.schema.table` |
| Không dùng cho | Luồng tính lại silver → gold: lib riêng `NB_LIB_TRANSFORM_SLV_GLD` (khoá / watermark ở đây gắn với `RunContext` của 1 nguồn raw) |
| Deploy | Luôn deploy lib **trước** notebook gọi |

## 2. Ý nghĩa

| Vấn đề trước đây | Lib giải quyết bằng |
|---|---|
| Mỗi notebook tự viết lại khoá, log, watermark, retry → lệch hành vi giữa nguồn | 1 khung `run_controlled` dùng chung |
| `TABLE_CONFIGS` viết cứng trong notebook | `load_table_specs` đọc `ctrl_mng_pipeline_config` + `ctrl_cfg_schema_registry`, kiểm tra hết rồi mới chạy |
| Raw do Eventstream ghi không có stats → lọc theo thời gian quét cả bảng (231 s cho 1.588 dòng) và có thể bỏ sót event commit trễ | Đọc theo version: chỉ file `add` của các commit sau `last_src_version` (`delta_added_files`) |
| 2 run chạy chồng (lịch + chạy tay, retry activity) | Khoá nguyên tử trên dòng watermark (`acquire_lock`) |
| Chạy lại áp dụng lại event cũ / run chậm ghi đè run mới | State theo entity không lùi (`commit_state`), watermark không lùi (`finalize_watermark`) |
| Giá trị sai định dạng thành NULL âm thầm | Cờ `_cn__<cột>`, `cast_null_policy = FAIL` chặn trước MERGE |
| 2 nguồn ghi chung bảng ctrl → xung đột ghi | `with_retry` 6 lần + jitter; state / reject partition theo `src_tbl` + điều kiện partition trong MERGE |

## 3. Cấu trúc

| § | Nhóm | Nội dung chính |
|---|---|---|
| 1 | constants | Tên 7 bảng ctrl, cột kỹ thuật, mẫu tên, `LOAD_MODES`, tiền tố `json_path` |
| 2 | common_utils | `utc_now`, `to_bool`, `split_csv`, `short_error` |
| 3 | log_utils | `log` an toàn đa luồng |
| 4 | validation_utils | Kiểm tra / quote tên, chuẩn hoá kiểu |
| 5 | retry_utils | Nhận diện lỗi tạm thời, `with_retry` |
| 6 | convert_utils | Biểu thức chuyển kiểu theo `convert_rule`, khoá suy ra `HASH_*` |
| 7 | json_utils | Parse JSON 1 lần, phát hiện JSON hỏng |
| 8 | data_models | `ColumnSpec`, `TableSpec`, `RunContext`, `Profile`, `TableResult`, `RunOutcome`, lỗi |
| 9 | config_utils | Nạp + kiểm tra cấu hình |
| 10 | delta_utils | Version, đọc file theo `_delta_log`, tạo / bổ sung bảng đích, MERGE trả số dòng |
| 11 | run_control_utils | Watermark, chốt snapshot, chọn cách đọc, khoá, run log, table log, trạng thái |
| 12 | parallel_utils | `run_in_waves` |
| 13 | state_reject_utils | State theo entity, reject (chuyển từ partner 03/10) |
| 14 | table_flow_utils | `process_with_retry`, `run_tables`, `run_controlled` |

## 4. Luồng điều khiển 1 lần chạy (`run_controlled`)

```
notebook: build_context() → load_table_specs() → (3P: check_config) → load_watermark()
run_controlled(ctx, body):
  [dry_run bỏ qua khoá + ghi ctrl]
  1 acquire_lock: UPDATE dòng watermark SET lock_exec_id, lock_at [, status RUNNING, last_run_id]
                  WHERE lock trống hoặc quá running_timeout_minutes → đọc lại xác nhận
                  không được → ghi run log SKIPPED_CONCURRENT, trả JSON (notebook raise)
  2 write_run_log(RUNNING)
  3 pin_snapshot: chốt version + table id + DESCRIBE DETAIL của raw
  4 body(out)  ← phần riêng notebook: read_incremental → phân loại → profile → load_state → run_tables → decide_status → commit
  5 finally: finalize_watermark (tách try) → write_run_log (cuối) → release_lock → unpersist cache
  6 build_summary (+ out.extra) → notebook in JSON, raise nếu FAILED / PARTIAL_FAILED / SKIPPED_CONCURRENT
```

Bất kỳ lỗi nào trong `body` → run `FAILED`, watermark giữ nguyên, vẫn đóng run log và nhả khoá.

## 5. Chi tiết hàm

### §1 constants

| Tên | Giá trị / ý nghĩa |
|---|---|
| `CTRL_SCHEMA`, `T_PIPELINE_CONFIG`, `T_WATERMARK`, `T_REGISTRY`, `T_LOG_RUN`, `T_LOG_TABLE_RUN`, `T_CDC_STATE`, `T_CDC_REJECT` | `lh_vv_bronze.ctrl` + tên đầy đủ 7 bảng |
| `TECH_COLUMNS` | Cột kỹ thuật bảng CDC: `deleted` BOOLEAN, `_ingested_at` TIMESTAMP, `_source_db` STRING |
| `SNAPSHOT_TECH_COLUMNS` | Bảng snapshot: `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`, `_ingested_at` |
| `IDENT_RE` | `[A-Za-z][A-Za-z0-9_]*` — không cho bắt đầu bằng `_` (dành cho cột nội bộ) |
| `JSON_PATH_RE` | `a`, `a.b.c` |
| `MIN_TS` | 1900-01-01, thay NULL khi so thứ tự |
| `LOAD_MODES` / `SNAPSHOT_MODES` | `CDC, DOC, DOC_ARRAY, LANG, LANG_ARRAY` / 4 mode sau |
| `PATH_SCOPES` | Tiền tố `json_path` đặc biệt: `_doc`, `_root`, `_align`, `_lang`, `_pos`, `_langs` |

Bảng `json_path` của bảng snapshot: `a.b` (trường trong phần tử / khối) · `$` (cả phần tử dạng JSON) · `_doc.<cột raw>` · `_root.a.b` (từ gốc payload) · `_langs` (mảng ngôn ngữ của tài liệu) · `_lang` (LANG*) · `_pos` (*_ARRAY, từ 0) · `_align.a` (phần tử cùng vị trí trong `align_path`, chỉ khi 2 mảng cùng số phần tử) · `p1,p2,...` (chỉ với `HASH_*`).

### §2 common_utils

| Hàm | Input → Output | Ghi chú |
|---|---|---|
| `utc_now()` | → `datetime` UTC không tzinfo | Ghi cột TIMESTAMP |
| `to_bool(value)` | bool / str / int / None → bool | `"1"`, `"true"`, `"yes"`, `"y"` = True |
| `split_csv(value)` | `" a, b ,,"` → `["a", "b"]` | Tham số danh sách |
| `short_error(e, limit=4000)` | exception → `"<Tên>: <nội dung>"` | Cột `error_message` |

### §3 log_utils

| Hàm | Mô tả |
|---|---|
| `log(msg, level="INFO", wave=None, table=None)` | In `[HH:MM:SS][LEVEL][w<wave>][<bảng>] msg`; khoá `_LOG_LOCK` để luồng song song không in chồng |

### §4 validation_utils

| Hàm | Mô tả |
|---|---|
| `is_identifier(name)` | Tên 1 phần hợp lệ theo `IDENT_RE` |
| `is_fq_name(name)` | Mọi phần của `a.b.c` hợp lệ |
| `quote_name(fq)` | `` `a`.`b`.`c` `` để ghép SQL (chỉ dùng sau khi kiểm tra) |
| `canonical_type(data_type)` | Chặn ký tự lạ bằng regex, nhờ Spark `CAST(NULL AS <kiểu>)` xác nhận, trả `simpleString` (`"decimal(19, 4)"` → `"decimal(19,4)"`); sai → `ValueError`; cache `_TYPE_CACHE` |

### §5 retry_utils

| Tên | Mô tả |
|---|---|
| `TRANSIENT_MARKERS` | `Concurrent*Exception`, `MetadataChangedException`, `ProtocolChangedException`, `TooManyRequestsForCapacity`, `Connection reset` |
| `is_transient(e)` | So tên lớp + nội dung lỗi (kể cả lỗi Java qua Py4J) |
| `with_retry(fn, label, attempts=6, base_s=2.0)` | Lỗi tạm thời → chờ `2 × 2^(i-1) + rand(0..1)` giây (2, 4, 8, 16, 32 s, tổng ~62 s) rồi chạy lại; lỗi khác / hết lượt → raise lỗi gốc. 03/10: 4 → 6 lần + jitter vì 2 nguồn ghi chung bảng ctrl |

### §6 convert_utils

| Tên | Mô tả |
|---|---|
| `CAST_FN` | `CAST` khi ANSI tắt (Runtime 1.3), `TRY_CAST` khi ANSI bật (Runtime 2.0) |
| `CONVERT_RULES` | `NONE` = cast; `EPOCH_S_TS` / `EPOCH_MS_TS` / `EPOCH_US_TS` = `timestamp_seconds/millis/micros`; `DATE_DAYS` = `date_add('1970-01-01', n)`; `LOWER_TRIM` = `lower(trim())`; `DECIMAL_BASE64` dựng riêng |
| `DERIVED_RULES` | `HASH_MD5_UUID`, `HASH_SHA256`, `HASH_SHA256_PIPE` |
| `decimal_base64_sql(col, data_type)` | Giải mã decimal Debezium (`decimal.handling.mode = precise`): base64 của số nguyên big-endian bù 2 chưa chia scale → `decimal(p,s)`. Chỉ hàm Spark (không UDF), tới 15 byte; tách 7 byte cuối vì `conv()` chỉ đúng 64 bit. Vd `'CMHohyA='` → 3761298.0000 |
| `convert_sql(raw_col, data_type, rule)` | Biểu thức SQL chuyển 1 cột chuỗi `_raw__<cột>` sang kiểu đích |
| `derived_sql(raw_cols, rule)` | Khoá suy ra từ nhiều phần; **1 phần NULL / rỗng → NULL** (thiếu khoá → reject, không sinh khoá sai). `HASH_MD5_UUID` = md5(concat) dạng 8-4-4-4-12 (= `poi_group_id` cũ); `HASH_SHA256` = sha2(concat) (= `source_review_id` cũ); `HASH_SHA256_PIPE` = sha2(concat_ws('\|', trim)) (= media cũ) |

### §7 json_utils

| Tên | Mô tả |
|---|---|
| `JSON_OPTIONS` | `allowUnquotedControlChars`, `allowSingleQuotes` (giống `get_json_object` cũ) |
| `CORRUPT_COL` | `__corrupt` |
| `parse_json_strings(json_col, paths)` | `from_json` 1 lần, mọi trường cấp 1 dạng chuỗi (object con giữ JSON) + `__corrupt`. Thay `get_json_object` từng cột (đọc lại cả chuỗi mỗi cột) |
| `is_json_corrupt(parsed, json_col=None)` | Cờ JSON hỏng; truyền `json_col` để bắt cả chuỗi rỗng / khoảng trắng (from_json trả NULL không ghi `__corrupt`) |

### §8 data_models

| Class | Trường / thuộc tính chính |
|---|---|
| `ConfigError` | Cấu hình / tham số sai: dừng trước khi ghi gì |
| `CastNullError` | Có giá trị thành NULL khi chuyển kiểu và `cast_null_policy = FAIL`: bảng FAILED trước MERGE, không retry |
| `CAST_NULL_POLICIES` | `FAIL`, `WARN` |
| `ColumnSpec` (frozen) | `name`, `json_path`, `data_type`, `convert_rule`, `is_key`, `key_order`, `is_toast`, `column_order`; `raw_col` = `_raw__<name>`; `is_derived`; `paths` (tách `,`); `part_cols`; `can_cast_null` (false với string + `NONE` / `LOWER_TRIM` và cột suy ra) |
| `TableSpec` (frozen) | `trg_schema`, `trg_tbl`, `src_object_schema`, `src_object`, `priority`, `columns`, `load_mode` = CDC, `align_path`, `dedup_order` (tuple (cột, desc)); `fq_name`, `is_snapshot`, `tech_columns`, `key_cols` (theo `key_order`), `toast_cols` (không gồm khoá), `src_ref`, `matches(schema, obj)` |
| `RunContext` | `exec_id`, `run_id`, `pl_name`, `nb_name`, `src_schema`, `src_tbl`, `run_mode`, `table_filter`, `overlap_minutes` (không dùng), `max_parallel`, `max_retries`, `full_reload`, `dry_run`, `stop_on_failure`, `running_timeout_minutes`, `run_params`, `started_at` + điền dần: `watermark_id/column/from`, `src_version_from/to`, `src_table_id_from`, `src_table_id`, `src_detail`, `allow_full_scan`, `read_mode`, `read_note`, `cast_null_policy`, `lock_mode` (`WATERMARK` / `RUN_LOG`); `raw_fq`; `updates_watermark` = không `dry_run`, không `full_reload`, không `table_filter` |
| `Profile` | `read_rows`, `valid_rows`, `ignored_rows`, `rejected_rows`, `ignored_detail` {lý do: {đối tượng: n}}, `valid_by_src`, `watermark_to`; `events_for(spec)` |
| `TableResult` | `spec`, `wave`, `status` (PENDING → SUCCESS / FAILED / NO_DATA / SKIPPED), `attempt_no`, các `*_rows` khớp `ctrl_log_table_run`, `cast_null_detail`, `started_at`, `ended_at`, `error_message`, `state_df`, `reject_df` (chờ commit), `cached`; `duration_ms`, `release()` |
| `RunOutcome` | `status` (mặc định FAILED), `error`, `profile`, `results`, `cached`, `extra` (thêm vào exit JSON) |

### §9 config_utils

| Hàm | Mô tả |
|---|---|
| `table_has(table, *cols)` | Bảng đã có các cột thêm sau chưa |
| `snapshot_path_error(path, mode, src_object, align_path)` | Lý do 1 phần `json_path` snapshot không hợp lệ, hoặc None |
| `parse_dedup_order(text)` | `"is_original DESC, created_at"` → `(("is_original", True), ("created_at", False))`; sai cú pháp → `ValueError` |
| `build_table_specs(pc_rows, reg_rows, table_filter, allowed_modes)` | **Hàm thuần** (test được không cần bảng): ghép config + registry → `(specs sắp theo (priority, trg_tbl), configured = mọi (schema, object) có trong registry)`. Gom **mọi** lỗi rồi raise 1 `ConfigError` (danh sách luật: `CTRL_TABLES_CONTEXT.md` §5) |
| `PC_OPTIONAL_COLUMNS` | `load_mode`, `align_path`, `dedup_order` (bảng chưa có cột → NULL = CDC) |
| `load_table_specs(ctx, allowed_modes=("CDC",))` | Đọc config (`pl_name`, nguồn, `is_active = 1`) + registry (nguồn, kể cả cột inactive) bằng tham số SQL, gọi `build_table_specs`. Partner gọi mặc định; 3P truyền `SNAPSHOT_MODES` |

### §10 delta_utils

| Hàm | Mô tả |
|---|---|
| `current_version(table)` | Version mới nhất (`history(1)`) |
| `table_detail(table)` | `DESCRIBE DETAIL` → dict (`location`, `id`, `partitionColumns`, `minReaderVersion`…) |
| `delta_added_files(detail, v_from, v_to)` | Đọc thẳng `_delta_log/<20 chữ số>.json` các commit `(v_from, v_to]`, lấy `add` có `dataChange = true` (bỏ OPTIMIZE / auto compaction). Gặp trường hợp đọc file trực tiếp không còn đúng → `DeltaReadUnsupported`: thiếu file log, `remove dataChange = true` (DELETE / UPDATE / MERGE / RESTORE), deletion vector, reader version > 1, column mapping, partition |
| `read_delta_files(table, location, paths)` | Đọc parquet trực tiếp theo schema hiện tại của bảng (path URL-decode); file đã VACUUM → `DeltaReadUnsupported` |
| `DeltaReadUnsupported` | Không đọc theo version được |
| `VersionGapError` | Không xác định đủ commit cần đọc → dừng run, không tiến watermark; xử lý: chạy 1 lần `allow_full_scan = True` |
| `target_ddl(spec, tech_columns=None)` | `CREATE TABLE IF NOT EXISTS` cột theo `column_order` + cột kỹ thuật theo `spec.tech_columns`, `optimizeWrite` + `autoCompact`, không `CLUSTER BY` |
| `ensure_target(spec, dry_run, tech_columns=None)` | Chưa có bảng → tạo; cấu hình có cột mới → `ALTER TABLE ADD COLUMNS`; lệch kiểu → `ConfigError`; `dry_run` chỉ kiểm tra. Trả mô tả thay đổi |
| `run_merge(source, target_fq, build_sql, view_name)` | MERGE qua temp view tên riêng; số dòng lấy từ kết quả MERGE, thiếu thì đọc commit `MERGE` trong `history(10)` (không dùng `history(1)` vì auto compaction có thể commit ngay sau). Yêu cầu 1 luồng ghi / bảng |
| `append_rows(table, rows)` | Append list[dict] theo đúng schema bảng (khoá thiếu → NULL), có retry. Nhờ đó cột ctrl thêm sau (vd cột gold) không làm hỏng extract |

### §11 run_control_utils

| Hàm | Mô tả |
|---|---|
| `load_watermark(ctx)` | Đọc **đúng 1** dòng cấp nguồn (`trg_tbl IS NULL`) → `watermark_id`, `watermark_column`, `watermark_from`, `src_version_from`, `src_table_id_from`; không đúng 1 dòng → `ConfigError` |
| `pin_snapshot(ctx)` | Chốt `src_version_to`, `src_table_id`, `src_detail`: dữ liệu ghi vào raw trong lúc chạy không lẫn vào lần này |
| `version_gap_reason(ctx)` | `last_src_version` NULL / table id đổi / version lùi → lý do; None = đọc VERSION được |
| `_gap(ctx, reason)` | `allow_full_scan` → `("FULL", lý do)`; không → `VersionGapError` |
| `choose_read_mode(ctx)` | `full_reload` → FULL; có khoảng trống → `_gap`; còn lại VERSION. **Không có kiểu lọc theo thời gian** |
| `read_incremental(ctx, columns, wm_alias)` | VERSION: `delta_added_files` → `read_delta_files` (không có commit mới → DataFrame rỗng); `DeltaReadUnsupported` → `_gap`. FULL: `VERSION AS OF v_to`. Trả `columns` + cột watermark ép TIMESTAMP; ghi `ctx.read_mode`, `ctx.read_note` (`"v18501..v18543: 43 commit, 41 file, 6.2 MB"`) |
| `LOCK_COLUMNS`, `watermark_has(*cols)` | Bảng watermark có cột khoá / `last_src_table_id` chưa |
| `_abandon_stale_runs(ctx)` | Run log `RUNNING` khác của nguồn quá `running_timeout_minutes` → `ABANDONED`; trả run còn trong hạn |
| `claim_run(ctx)` | Dự phòng khi chưa có cột khoá (không nguyên tử) |
| `update_watermark(ctx, values, condition)` | UPDATE dòng watermark + `updated_at`, có retry (điều kiện xét lại trên snapshot mới nên an toàn) |
| `_lock_expired_sql(ctx)`, `read_lock(ctx)` | Khoá quá hạn = `lock_at < current_timestamp() - running_timeout_minutes` (NULL = quá hạn) |
| `acquire_lock(ctx, extra)` | Đọc khoá → còn hạn: từ chối; trống / quá hạn: `UPDATE … WHERE lock trống hoặc quá hạn` → đọc lại, `lock_exec_id = exec_id` mới là thắng (Delta optimistic concurrency: 2 run cùng UPDATE thì 1 run xung đột, thử lại thấy đã có chủ). Lấy lại khoá quá hạn → WARN + đánh `ABANDONED` run cũ. Trả `(ok, ai đang giữ)` |
| `release_lock(ctx)` | Nhả khi còn là chủ (`WHERE lock_exec_id = exec_id`) |
| `finalize_watermark(ctx, status, watermark_to, error)` | Chỉ khi `updates_watermark`. SUCCESS / NO_DATA: `status SUCCESS`, `last_success_at`, `last_src_version = v_to`, `last_src_table_id`, `watermark_value = max(cũ, mới)`, `flow_name` — điều kiện **còn giữ khoá** và **không lùi** (`last_src_version` NULL / ≤ v_to / table id đổi). Lỗi: chỉ `FAILED` + lỗi. Đọc lại; không ghi được → trả cảnh báo (ghi vào `error_message`) |
| `run_log_row(ctx, status, profile, results, error, ended_at)` | Dựng đủ cột `ctrl_log_run`; `rejected_rows` = lỗi phân loại + lỗi theo bảng của bảng SUCCESS; `tbl_failed_count` gồm SKIPPED |
| `write_run_log(row)` | MERGE theo `exec_id` (mở RUNNING, đóng cùng dòng) |
| `table_log_row(res, ctx)` | Dòng `ctrl_log_table_run`; bảng SUCCESS có cast null → `error_message = {"cast_null": {...}}` |
| `decide_status(results)` | Có FAILED / SKIPPED: tất cả bảng xử lý đều lỗi → FAILED, không → PARTIAL_FAILED; không lỗi: có bảng xử lý → SUCCESS, không → NO_DATA |
| `build_summary(...)` | JSON exit: status, exec_id, version, read_mode, watermark, tables {total, ok, failed, skipped, no_data}, rows {read, valid, ignored, rejected, inserted, updated, cast_null}, duration_s, error |

### §12 parallel_utils

| Hàm | Mô tả |
|---|---|
| `run_in_waves(items_by_priority, worker, max_parallel, results, is_failed, on_skip, stop_on_failure, label)` | Priority nhỏ trước; trong 1 wave `ThreadPoolExecutor(min(max_parallel, số việc))`; `inheritable_thread_target` để Cancel cell dừng cả luồng con; `stop_on_failure` → wave sau `on_skip`. Dùng thread (không phải notebook riêng) để các bảng dùng chung DataFrame đã cache trong 1 Spark session; mỗi luồng chỉ ghi bảng của nó, bảng ctrl do luồng chính ghi |

### §13 state_reject_utils

Hợp đồng cột event notebook phải dựng: `_cdc_ts_ms` BIGINT, `_cdc_lsn` BIGINT, `_raw_ingested_at` TIMESTAMP, `_is_delete` INT, `_op` STRING (NULL được), `_entity_key` STRING.

| Tên | Mô tả |
|---|---|
| `STATE_COLUMNS` | Thứ tự cột MERGE `ctrl_cdc_state` |
| `event_order()` | `struct(ts, lsn, ing, del)` với NULL → -1 / `MIN_TS`; trùng thứ tự thì xoá mới hơn |
| `load_state(specs)` | State các bảng trong phạm vi (lazy, notebook persist) → `_st_key`, `_st_order` |
| `state_rows(spec, latest, ctx)` | Dòng state mới; `is_deleted = coalesce(_op = 'd', false)` |
| `state_order_sql(alias)`, `STATE_NOT_OLDER` | Điều kiện MERGE: event mới ≥ đang lưu (bằng vẫn ghi để cập nhật `last_run_id`) |
| `src_partition_cond(src_tbl)` | `" AND t.src_tbl = '<nguồn>'"`: MERGE chỉ đọc partition của nguồn → 2 nguồn song song không xung đột |
| `commit_state(results, src_tbl)` | 1 MERGE cho mọi bảng SUCCESS; bảng lỗi không ghi state → lần sau xử lý lại |
| `merge_rejects(parts, note, src_tbl)` | Union, bỏ trùng `event_hash`, MERGE: đã có → `reject_count + 1`, cập nhật `last_*`, lý do; chưa có → insert |

### §14 table_flow_utils

| Hàm | Mô tả |
|---|---|
| `process_with_retry(spec, wave, ctx, body)` | Chạy `body(res)` cho 1 bảng; lỗi tạm thời → thử lại (`max_retries`, chờ 5 × lần); lỗi khác → FAILED. **Không bao giờ raise**; lỗi thì giải phóng cache, bỏ state / reject chờ commit; `setJobDescription` để dễ đọc Spark UI |
| `run_tables(specs, events_for, worker, ctx, results)` | Bảng 0 event → NO_DATA (không tốn job); còn lại `run_in_waves`; `stop_on_failure` → SKIPPED |
| `run_controlled(ctx, body)` | Xem mục 4 |

## 6. Tham số dùng chung (notebook truyền vào `RunContext`)

| Tham số | Partner | 3P | Ý nghĩa |
|---|---|---|---|
| `allow_full_scan` | False | False | Cho phép đọc FULL khi có khoảng trống version (lần đầu, sau reset, thiếu log, raw tạo lại) |
| `max_parallel` | 4 (rerun dùng 12) | 8 (rerun dùng 12) | Bảng chạy đồng thời trong 1 wave |
| `max_retries` | 1 | 1 | Thử lại 1 bảng khi lỗi tạm thời |
| `table_filter` | "" | "" | Chỉ chạy các `trg_tbl` này (watermark không đổi) |
| `full_reload` | False | False | Đọc toàn bộ raw, bỏ state (watermark không đổi) |
| `dry_run` | False | False | Chỉ đọc, parse, đếm |
| `stop_on_failure` | False | False | Wave lỗi thì dừng wave sau |
| `cast_null_policy` | FAIL | FAIL | FAIL / WARN |
| `running_timeout_minutes` | 60 | 60 | Khoá nguồn quá hạn theo số phút này. Activity FL_00 trong repo đặt timeout 12 giờ, lớn hơn 60 |

## 7. Vấn đề đã biết / việc còn mở

| # | Mức | Nội dung |
|---|---|---|
| C2 | Medium | `max_retries < 0` → vòng thử rỗng, bảng PENDING bị tính là thành công → watermark tiến qua dữ liệu chưa xử lý. Bản vá 1 chỗ trong `run_controlled` (REVIEW_EXTRACT_PROD_0410 §8.1) **chưa có trong bản lib của project** |
| C1 | Low | Mất khoá giữa chừng → `finalize_watermark` chỉ cảnh báo, run vẫn SUCCESS; partner MERGE đích không có điều kiện thứ tự. Đã hạ Low nhờ pipeline Concurrency = 1 + timeout activity < `running_timeout_minutes` |
| M2 | Medium | Phần điều khiển mỗi run: 7–8 commit ctrl + ~9 query + ~8 lần tra catalog (`watermark_has` 3 lần, `table_has` 3 lần, đọc khoá 2 lần, UPDATE watermark + nhả khoá riêng) |
| M3 | Medium | `load_state` lọc `concat_ws(trg_schema, trg_tbl) IN (...)` → không cắt partition `src_tbl`, đọc state của cả 2 nguồn |
| M4 | Medium | `merge_rejects` MERGE theo `event_hash` (băm) → quét cả partition reject mỗi lần có reject |
| L1 | Low | `run_merge` đọc `current_version` trước mỗi MERGE chỉ cho nhánh dự phòng |
| — | Low | 3P FULL: raw đọc thành ~1 partition → parse 1 task; cân nhắc `repartition` sau khi đọc FULL |

Chi tiết + số liệu: `99_PAIN_POINTS.md`, `claude/REVIEW_EXTRACT_PROD_0410.md`.
