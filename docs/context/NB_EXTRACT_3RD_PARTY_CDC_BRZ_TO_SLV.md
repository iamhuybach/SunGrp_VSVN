# NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV — Extract tài liệu crawl 3rd-party → `slv_3p_poi_*`

> Cập nhật: 08/10/2026. Bản code: `claude/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` (project, 04/10). Thiết kế + kết quả đối chiếu payload: `claude/POI_3P_EXTRACT_REDESIGN.md` §5.
> Hàm dùng chung: `NB_LIB_EXTRACT_RAWDATA.md`. Tên có "CDC" để cùng mẫu với partner, thực chất nguồn là **snapshot** (mỗi event = 1 tài liệu đầy đủ).

## 1. Mô tả

Đọc tài liệu crawl (Google Places + enrichment) từ `lh_vv_bronze.dbo.poi_raw_event`, tách mỗi tài liệu ra 14 bảng `lh_vv_silver.dbo.slv_3p_poi_*` (13 active) theo cấu hình: 1 dòng / tài liệu, / khối, / phần tử mảng, / object bản địa hoá, / phần tử mảng trong object bản địa hoá. Chuẩn kiểu, sinh khoá. **Chỉ extract**: không rule nghiệp vụ, không canonical, không gate.

| | |
|---|---|
| Gọi bởi | Không có trong `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`. Chạy tay hoặc pipeline khác. Chuỗi `NB_00_POI_PIPELINE_ORCHESTRATOR` cũ vẫn chạy song song tới cutover |
| Đọc | `ctrl_mng_pipeline_config` (`load_mode`, `align_path`, `dedup_order`), `ctrl_cfg_schema_registry`, `ctrl_mng_watermark`, `ctrl_cdc_state`; raw theo version / FULL |
| Ghi | `slv_3p_poi_*` (MERGE, **không xoá**), `ctrl_cdc_state`, `ctrl_cdc_reject`, `ctrl_log_run`, `ctrl_log_table_run`, `ctrl_mng_watermark` |
| Song song | 13 bảng active cùng priority 1 → 1 wave, `max_parallel` luồng |
| Chạy lại | State (`poi_id`) bỏ tài liệu đã áp dụng; MERGE chỉ ghi đè khi (`_crawled_at`, `_event_id`) mới ≥ đang lưu; watermark chỉ tiến khi mọi bảng thành công |
| Chạy chồng | Khoá trên dòng `wm_transform_poi_raw_event`. Song song với partner: MERGE state / reject chỉ đọc partition `src_tbl` của mình |

## 2. Ý nghĩa

Thay phần extract của chuỗi cũ NB_00 → NB_30 (3P):

| Cũ | Mới |
|---|---|
| Watermark `MAX(crawled_at)` không overlap → tài liệu commit trễ bị bỏ sót vĩnh viễn | Đọc theo version Delta |
| Cell 0 NB_00 `DELETE` dòng `brz_watermark` rồi tạo lại mốc 18/09 → nguy cơ đọc lại từ 18/09 mỗi run | Watermark ctrl, chỉ tiến, có khoá |
| Tài liệu thiếu 1 trong vi / en / ko bị loại cả tài liệu, chỉ `print` | Nhận mọi ngôn ngữ trong `langs`; thiếu → đếm ở exit JSON, quyết định ở silver L2 |
| Khoá có lang → address, contact… ghi 3 lần | Khoá theo `poi_id`; chỉ bảng theo ngôn ngữ có `lang` trong khoá |
| Tên 4 phần `sgr_visitvn_stg.*` viết cứng | Tên đọc từ ctrl |
| Silver phụ thuộc gold (`poi_master.is_enrichable`, `destination_ward_mapping`) | Extract không đọc gold |
| Thiếu khối: lúc ghi NULL đè, lúc giữ cũ | Thống nhất: khối vắng → bảng không nhận tài liệu đó, giữ dữ liệu cũ |
| Không reject / table log / chống chạy chồng | Như partner |

## 3. Khác partner

| | Partner (CDC) | 3rd-party (snapshot) |
|---|---|---|
| 1 event | 1 thay đổi dòng của 1 bảng Postgres | 1 tài liệu đầy đủ của 1 địa điểm lúc crawl |
| Bảng nhận event | Đúng 1 (`source.table`) | Mọi bảng có khối tương ứng trong tài liệu |
| Thứ tự | (`ts_ms`, `lsn`, ingest) | `crawled_at`; trùng thì `event_id` |
| State | Theo khoá bảng | Theo `poi_id` cho mọi bảng (`state_key = "doc"`); `"row"` = theo khoá bảng |
| Khối / trường vắng | TOAST | Khối vắng → không nhận, giữ cũ |
| Xoá | `op = d` → `deleted` | Không có; bảng con chỉ upsert, `_last_seen_at` cho biết lần cuối thấy |
| Khoá | Có sẵn trong payload | Suy ra: `poi_id` (md5), `review_id` (sha256), `media_dedup_key` (sha256 pipe) |

## 4. Tham số

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `pl_name`, `run_id`, `src_schema`, `src_tbl` | FL_00, "", `lh_vv_bronze.dbo`, `poi_raw_event` | |
| `allow_full_scan`, `max_retries`, `table_filter`, `full_reload`, `dry_run`, `stop_on_failure`, `cast_null_policy`, `running_timeout_minutes` | như partner | `dry_run` không raise `CastNullError` (để xem đủ mọi bảng) |
| `max_parallel` | 8 | Nên ≥ 13 (= số bảng active) để không có lượt 2 (rerun dùng 12 → `review_i18n` chạy lượt 2) |
| `sources` | `google` | `source_name` được xử lý (CSV, không phân biệt hoa thường); ngoài danh sách → IGNORED `OUT_OF_SCOPE`; rỗng = mọi nguồn |
| `langs` | `vi,en,ko` | Ngôn ngữ nhận cho bảng LANG / LANG_ARRAY; ngôn ngữ khác: đếm, bỏ qua |
| `lang_object_path` | `extra_info.enrichment` | Object bản địa hoá chính; ngôn ngữ ở trường `lang_field` |
| `lang_field` | `lang` | |
| `lang_map_path` | `extra_info.enrichmentSiblings` | Map ngôn ngữ → object bản địa hoá |
| `doc_key_column` | `poi_id` | Cột định danh tài liệu, phải có trong registry của **mọi** bảng |
| `state_key` | `doc` | `doc`: `entity_key` = `poi_id` (mọi bảng; tài liệu cũ đến trễ bị bỏ qua ở mọi bảng). `row`: khoá bảng (bảng con nhận phần tử chỉ có ở tài liệu cũ đến trễ; state ~3 lần nhiều dòng hơn). Đổi không cần reset state |

## 5. Hằng số nguồn

| Hằng số | Giá trị |
|---|---|
| `RAW_PAYLOAD` | `normalized_payload` |
| `RAW_EVENT_ID` | `event_id` |
| `RAW_DOC_ID` | (`source_name`, `source_id`) — bắt buộc; cột đầu lọc theo `sources` |
| `RAW_LANG` | `language_code` (gộp vào `_langs`) |
| `IGNORE_REASONS` | `OUT_OF_SCOPE` |
| `ENTRY_TYPE` | `array<struct<lang, obj>>` |
| `ARRAY_MODES` / `LANG_MODES` | `DOC_ARRAY, LANG_ARRAY` / `LANG, LANG_ARRAY` |

Cột thứ tự = `watermark_column` của dòng watermark (`crawled_at`), không viết cứng. Cột raw khác khai báo trong registry dạng `_doc.<cột>`.

## 6. Luồng

```
run_extract()
  build_context()           kiểm tra tham số riêng (đường dẫn lang, doc_key_column, state_key)
  load_table_specs(ctx, SNAPSHOT_MODES) → 14 cấu hình, 13 active
  check_config(ctx, specs)  mọi bảng có doc_key_column; mọi cột raw cần đọc có trong bảng raw
  load_watermark(ctx)
  run_controlled(ctx, process_run)
    process_run:
      uses_langs → classify_docs(read_raw(doc_columns), top_fields) → persist
      profile_docs → (Profile, số tài liệu có khối / bảng, độ phủ ngôn ngữ, khối sai dạng)  → out.extra
      load_state → persist
      run_tables(specs, docs_by_table, process_table)   bảng 0 tài liệu có khối → NO_DATA
        _run_table: ensure_target → build_table_rows (expand_rows → part_value → convert / derived → key → stale)
                    → table_stats → cast null? → element_reject_rows → resolve_latest → merge_into_target
                    → state_rows(doc_state_latest)
      decide_status → commit: commit_state → merge_rejects (tài liệu lỗi + phần tử lỗi) → table log
```

## 7. Chi tiết hàm

### A. Đọc, phân loại, dựng tài liệu

| Hàm | Mô tả |
|---|---|
| `path_value(parsed, path)` | `a.b.c`: trường đầu từ struct đã parse, phần sau bằng `get_json_object` |
| `block_col(field)` / `doc_value(path)` | Sau phân loại, mỗi trường cấp 1 của payload là 1 cột `_b__<trường>` → mỗi bảng chỉ đọc khối mình cần, không giải mã cả payload; `doc_value` lấy đường dẫn tính từ gốc |
| `spec_paths(spec)` | Mọi đường dẫn của các cột (cột suy ra tách nhiều phần) |
| `is_scoped(path)` | `$` hoặc có tiền tố đặc biệt |
| `top_fields(specs, need_langs)` | Trường cấp 1 cần parse (1 lần cho mọi bảng): khối nguồn, `_root.*`, `align_path`, trường bảng DOC `$`, 2 đường dẫn bản địa hoá |
| `doc_columns(specs)` | Cột raw cần đọc: 5 cột cố định + mọi `_doc.<cột>` |
| `uses_langs(specs)` | Có bảng LANG* hoặc cột `_langs` |
| `read_raw(ctx, doc_cols)` | `read_incremental(ctx, doc_cols, "_crawled_at")` |
| `lang_entries()` | `[(lang, obj)]` từ object chính (đứng trước) + map siblings; `lang` = `lower(trim)`; bỏ lang rỗng / obj NULL; object chính thiếu `lang` bị bỏ (không đoán) |
| `classify_docs(raw, fields, need_langs)` | Parse payload 1 lần; luật phân loại dưới; dựng cột event theo hợp đồng lib §13 (`_cdc_ts_ms = unix_millis(crawled_at)`, `_cdc_lsn` NULL, `_raw_ingested_at = crawled_at`, `_is_delete = 0`, `_op` NULL); tách `_p` thành `_b__*` (chỉ VALID); ngôn ngữ: `_langs_arr` / `_langs` (mọi ngôn ngữ có trong tài liệu + `language_code`), `_lang_entries` (bỏ trùng lang — object chính thắng — rồi lọc theo `langs`), `_primary_no_lang`; payload gốc chỉ giữ cho REJECTED |
| `presence(spec)` | Tài liệu có khối của bảng: DOC `$` luôn có; DOC: khối khác NULL; DOC_ARRAY: mảng ≥ 1 phần tử; LANG*: ≥ 1 object bản địa hoá |
| `bad_shape(spec)` | Khối DOC_ARRAY có giá trị nhưng không phải mảng JSON → đếm, WARN (không reject vì tài liệu đúng với bảng khác) |
| `profile_docs(classified, specs, need_langs)` | Profile (`ignored_detail` theo `source_name`, `watermark_to = max(crawled_at)`); `{trg_tbl: số tài liệu có khối}`; `langs` = {`missing`: {lang: số tài liệu thiếu}, `not_allowed`: {lang ngoài `langs`: n}, `primary_without_lang`}; `bad_shape` |
| `reject_frame(...)` | Dòng `ctrl_cdc_reject` của 3P: `src_db = source_name`, `cdc_op` NULL, `before_payload` NULL, `after_payload` = payload / phần tử lỗi, `source_payload` = JSON định danh |
| `doc_source_payload(extra)` | JSON `{event_id, source_name, source_id, language_code, crawled_at [, lang, pos]}` |
| `doc_reject_rows(df, ctx)` | Tài liệu lỗi; `event_hash = sha256(event_id, source_name, source_id, crawled_at, payload)`; `entity_key = source_name\|source_id` |

Luật phân loại tài liệu (luật đầu tiên khớp quyết định):

| # | Điều kiện | Trạng thái | Lý do |
|---|---|---|---|
| 1 | `source_name` / `source_id` NULL hoặc rỗng | REJECTED | `MISSING_ENTITY_KEY` |
| 2 | `source_name` ngoài `sources` | IGNORED | `OUT_OF_SCOPE` |
| 3 | Payload NULL / rỗng / không phải JSON object | REJECTED | `INVALID_PAYLOAD` |
| 4 | `crawled_at` NULL | REJECTED | `MISSING_EVENT_ORDER` |

### B. Xử lý 1 bảng

| Hàm | Mô tả |
|---|---|
| `expand_rows(spec, docs)` | Tách dòng theo `load_mode`: DOC `$` → 1 dòng / tài liệu (`_elem` NULL); DOC → khối khác NULL; DOC_ARRAY → `posexplode` (`_pos`, `_elem`); LANG → 1 dòng / object bản địa hoá (`_lang`, `_elem` = object hoặc đường dẫn trong object); LANG_ARRAY → `posexplode` mảng trong object. `align_path`: parse 1 lần / tài liệu trước khi nổ, `_align` chỉ có khi 2 mảng cùng số phần tử |
| `part_value(path)` | Chuỗi gốc của 1 đường dẫn theo tiền tố (`$`, `_lang`, `_pos`, `_langs`, `_doc.`, `_root.`, `_align.`, còn lại = trường của phần tử từ struct `_e`) |
| `build_table_rows(spec, docs, state_df)` | `_e` = struct trường phần tử (DOC `$`: từ `_b__*`; khác: `parse_json_strings(_elem)`; `_parse_failed` khi bảng cần trường mà phần tử không phải object) → `_raw__*` → chuyển kiểu (`convert_sql` / `derived_sql`) → `_cn__*` → `_key_null` (khoá bảng hoặc `doc_key_column` thiếu) → `_entity_key` (theo `state_key`), `_row_key` → `_is_stale`, `_applicable`. `_elem` / `_align` chỉ giữ cho dòng reject |
| `table_stats(spec, rows)` | `input_rows` = số dòng sau khi tách; `entity_rows` = số khoá bảng; `upsert_event_rows = applicable_rows`; `delete_event_rows = 0` |
| `resolve_latest(spec, rows)` | 1 dòng / khoá bảng: tài liệu mới nhất (`crawled_at`, `event_id`) → `dedup_order` (NULL cuối) → `_pos`; `_first_seen_at` / `_last_seen_at` = min / max `crawled_at` của khoá trong lần chạy |
| `build_merge_sql(spec, target, view)` | Khớp **và** (`s._crawled_at > t._crawled_at` hoặc bằng và `s._event_id ≥ t._event_id`) → UPDATE cột + `_crawled_at`, `_event_id`, `_first_seen_at = least`, `_last_seen_at = greatest`, `_ingested_at`; không khớp → INSERT. Không có nhánh xoá. Điều kiện thứ tự chặn ghi lùi ở mức dòng |
| `merge_into_target(spec, latest, ctx)` | `run_merge` |
| `doc_state_latest(rows)` | 1 dòng / `_entity_key` (tài liệu mới nhất) cho `state_rows` |
| `element_reject_rows(spec, rows, ctx)` | Phần tử thiếu khoá / không phải object → reject; `event_hash = sha256(bảng, source_name, source_id, lang, phần tử, phần tử align)` → crawl lại cùng phần tử lỗi chỉ tăng `reject_count`; ghi chú "align_path khác số phần tử?" khi có align |
| `_run_table(res, docs, state_df, ctx)` / `process_table(...)` | Như partner; `dry_run` chỉ cảnh báo cast null |

### C. Commit + Main

| Hàm | Mô tả |
|---|---|
| `commit(classified, profile, results, ctx)` | `commit_state(results, src_tbl)` → `merge_rejects([phần tử lỗi bảng SUCCESS, tài liệu lỗi], src_tbl)` → append table log |
| `build_context()` | Kiểm tra `cast_null_policy`, `lang_object_path`, `lang_map_path` (dạng `a.b`), `lang_field`, `doc_key_column` (identifier), `state_key` ∈ {doc, row}; gom lỗi → `ConfigError` |
| `check_config(ctx, specs)` | Trước khi nhận khoá: mọi bảng có `doc_key_column`; cột raw cần đọc có trong bảng raw |
| `process_run(ctx, specs, out)` | Phần riêng bên trong `run_controlled`; ghi `out.extra`: `langs`, `docs_by_table`, `bad_shape` |
| `run_extract()` | Luồng chính |

## 8. Bảng đích

| Bảng | load_mode | src_object | Khoá | Bảng cũ tương ứng |
|---|---|---|---|---|
| `slv_3p_poi` | DOC | `$` | poi_id | `poi_source_map` / `poi_entity` (danh tính nguồn) |
| `slv_3p_poi_address` | DOC | `poi_address` | poi_id | `poi_address` |
| `slv_3p_poi_contact` | DOC | `poi_contact` | poi_id | `poi_contact` |
| `slv_3p_poi_price` | DOC | `poi_price` | poi_id | `poi_price` |
| `slv_3p_poi_opening_hours` | DOC | `poi_opening_hours` | poi_id | `poi_opening_hours` |
| `slv_3p_poi_policy` | DOC | `policies` | poi_id | `poi_policy` — **tắt** (khối luôn null) |
| `slv_3p_poi_rating` | DOC | `poi_rating` | poi_id | `poi_rating` |
| `slv_3p_poi_amenity` | DOC | `poi_amenity` | poi_id | `poi_amenity_source` |
| `slv_3p_poi_raw_data` | DOC | `raw_data` | poi_id | (mới) |
| `slv_3p_poi_content` | DOC_ARRAY | `poi_content` | poi_id, locale, content_type | `poi_content` |
| `slv_3p_poi_review` | DOC_ARRAY | `poi_review` | review_id | `poi_review` (bản gốc) |
| `slv_3p_poi_media` | DOC_ARRAY | `poi_media` | media_dedup_key | `poi_media` |
| `slv_3p_poi_enrichment` | LANG | `$` | poi_id, lang | `poi_enrichment` |
| `slv_3p_poi_review_i18n` | LANG_ARRAY | `reviews` (align `poi_review`) | review_id, lang | `poi_review` (bản dịch) |

Cột JSON giữ nguyên khối (transform sau): `raw_data_json`, `amenity_schema_json`, `ext_attributes_json` (62 khoá phẳng, có `primaryType`, `open_now`), `facilities_json`, `secondary_hours_json`. Mảng 1 tầng để cột JSON: `periods_json`, `experiences_json`, `types_json`, `subcategory_tags_json`, `weekday_text_json`, `enrichment_failed_langs_json`, `available_langs_json`. Cần tách sau: chỉ thêm cấu hình `DOC_ARRAY` / `LANG_ARRAY`, không sửa code.

## 9. Số liệu đo

| Lần | Kết quả |
|---|---|
| FULL đầu 04/10 (exec `43cae547`) | 21.168 event, tất cả VALID, 19.046 địa điểm; 13 bảng SUCCESS, `policy` NO_DATA; `cast_null` = 0; 224 s; version 1043, watermark 2026-09-16 11:01:11 |
| Số dòng sau tách (PREVIEW 04/10) | poi 21.168 · price 9.726 · opening_hours 17.829 · raw_data 8.199 · content 1.179 · review 102.401 · media 102.643 · enrichment 38.195 · review_i18n 181.687 |
| Rerun FULL 04/10 (exec `88ea49e7`) | 213 s: cấu hình 44 s, khoá 26 s (1 lần retry xung đột ghi watermark với partner), mở log + chốt 13 s, đọc + phân loại 29 s (raw ~1 partition → 1 task), wave 64 s, commit 18 s, watermark + log + nhả khoá 17 s. Điều khiển + commit 118 s (55%) |
| Đối chiếu | Q11: bản dịch review khớp thứ tự 100% (52.690 cặp). Q13: 0 địa điểm có > 1 `language_code`. 125 `event_id` trùng (cùng payload) — raw ghi lặp, vô hại. V7: 8.317 dòng raw không có enrichment; lỗi dịch en 616, ko 373 |

## 10. Vận hành

| Việc | Cách |
|---|---|
| Pipeline | Chưa có activity trong FL_00. JSON hiện tại chỉ gọi notebook partner |
| Lần đầu | `dry_run = True, allow_full_scan = True` (xem `cast_null`, `langs`) → `allow_full_scan = True` → bật lịch, sau đó `False` |
| Thêm cột | INSERT 1 dòng registry; dữ liệu cũ: `full_reload` bảng đó |
| Thêm ngôn ngữ | Tham số `langs`; tài liệu cũ: `full_reload` bảng LANG* |
| Thêm nguồn crawl | Tham số `sources`; kiểm tra payload cùng cấu trúc; tài liệu cũ đã IGNORED → 1 lần `full_reload = True` |
| Exit có `bad_shape` / `langs.primary_without_lang` | Payload khác cấu trúc cấu hình: xem mẫu raw, sửa cấu hình hoặc báo collector |
| `CastNullError`, `VersionGapError`, `SKIPPED_CONCURRENT` | Như partner |

```sql
SELECT trg_tbl, reject_reason, reject_detail, COUNT(*) AS so_dong, SUM(reject_count) AS so_lan
FROM lh_vv_bronze.ctrl.ctrl_cdc_reject WHERE src_tbl = 'poi_raw_event' AND NOT is_resolved
GROUP BY 1, 2, 3 ORDER BY so_dong DESC;
```

## 11. Vấn đề đã biết

| # | Nội dung |
|---|---|
| Dữ liệu | Raw 3P không nhận dữ liệu từ 16/09 (collector / Eventstream) |
| Dữ liệu | `business_sector` vừa `accommodation` vừa `accomodation` (250); category lộn xộn (`Café` / `Cafe`) — chuẩn hoá ở silver L2 qua `ref_business_category` |
| Dữ liệu | 21 object enrichment có `poiId` là UUID khác nhau theo ngôn ngữ; `enrichmentId` đổi mỗi event → không dùng làm khoá |
| M7 | Khối LANG_ARRAY (`review_i18n`) sai dạng mất dòng không báo (`bad_shape` chỉ đếm DOC_ARRAY) |
| Hiệu năng | FULL: raw đọc thành ~1 partition → parse 1 task (cân nhắc `repartition`); `max_parallel` < 13 → lượt 2 |
| Thiết kế | Bảng con chỉ upsert: phần tử không còn trong tài liệu mới vẫn giữ (dùng `_last_seen_at` để lọc ở L2 nếu cần) |
