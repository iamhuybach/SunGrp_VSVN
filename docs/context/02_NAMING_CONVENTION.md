# 02 — Quy ước đặt tên và convention theo Data Model mới

> Cập nhật: 08/10/2026. Áp dụng cho mọi bảng, notebook, pipeline, cột, dòng ctrl và code mới.
> Tên mới chưa có trong hệ thống: gắn nhãn `[PROPOSED]` cho tới khi được chốt.
> Kèm: `01_DATA_MODEL.md` (model), `CTRL_TABLES_CONTEXT.md` (bảng ctrl).

## 1. Lakehouse, schema, tiền tố bảng

| Vị trí | Tiền tố | Ý nghĩa | Ví dụ |
|---|---|---|---|
| `lh_vv_bronze.dbo` | (tên nguồn) + `_raw_data` / `_raw_event` | Raw do Eventstream append, không sửa | `partner_raw_data`, `poi_raw_event` |
| `lh_vv_bronze.ctrl` | `ctrl_mng_` | Cấu hình + trạng thái điều khiển pipeline | `ctrl_mng_pipeline_config`, `ctrl_mng_watermark` |
| | `ctrl_cfg_` | Cấu hình chi tiết (mapping cột) | `ctrl_cfg_schema_registry` |
| | `ctrl_log_` | Log chạy | `ctrl_log_run`, `ctrl_log_table_run` |
| | `ctrl_cdc_` | State / reject của extract | `ctrl_cdc_state`, `ctrl_cdc_reject` |
| `lh_vv_silver.dbo` | `slv_pn_<bảng Postgres>` | Silver L1 extract nguồn partner (CDC) — tên giữ đúng tên bảng nguồn | `slv_pn_business_services` |
| | `slv_3p_poi_<khối>` | Silver L1 extract nguồn 3rd-party (snapshot) — tên theo khối payload | `slv_3p_poi_address` |
| | `slv_pm_<bảng>` `[PROPOSED]` | Silver L1 extract POI management (quyết định canonical, CDC) | — |
| | `slv_poi_<chủ đề>` | Silver L2 tích hợp (node của luồng tính lại) | `slv_poi_localization` |
| | `ref_<chủ đề>` | Bảng tham chiếu = rule dạng dữ liệu, sửa tay | `ref_lang_policy` |
| `lh_vv_gold.dbo` | `gld_srv_<chủ đề>_<grain>` | Gold phục vụ (serving) | `gld_srv_poi_multi_lang` |
| | (không tiền tố) | Bảng cũ — **giữ nguyên, không đổi tên** | `poi_master`, `destination_ward_mapping` |

Quy tắc:
- Tiền tố theo **nguồn** ở L1 (`pn`, `3p`, `pm`), theo **chủ đề** ở L2 / gold.
- Tên bảng `snake_case`, chữ thường, chỉ `[a-z0-9_]`, bắt đầu bằng chữ (kiểm tra bằng `IDENT_RE = [A-Za-z][A-Za-z0-9_]*`). Không bắt đầu bằng `_` (dành cho cột nội bộ).
- Không tạo schema mới khi tiền tố đã đủ phân biệt (OD-G11). Bảng luôn viết đầy đủ `lakehouse.schema.table` trong code (notebook default lakehouse = `lh_vv_bronze`).
- Bảng `poi_*` cũ ở silver (chuỗi NB_00 cũ) và `lh_vv_bronze.partner.*` giữ nguyên tới cutover.

## 2. Notebook

| Mẫu | Vai trò | Ví dụ |
|---|---|---|
| `NB_LIB_<VIỆC>` | Thư viện `%run`: chỉ hằng số / class / hàm, không đọc ghi khi được `%run` | `NB_LIB_EXTRACT_RAWDATA`, `NB_LIB_TRANSFORM_SLV_GLD` |
| `NB_EXTRACT_<NGUỒN>_CDC_BRZ_TO_SLV` | Extract 1 nguồn raw → silver L1 (**1 notebook / nguồn**) | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, `NB_EXTRACT_POIMGMT_CDC_BRZ_TO_SLV` `[PROPOSED]` |
| `NB_00_ORCHES_<TỪ>_TO_<ĐẾN>` | Điều phối dùng chung, chọn luồng bằng tham số `p_pl_name` | `NB_00_ORCHES_SLV_TO_GLD` |
| `NB_<UPPER(trg_tbl)>` | Notebook node: 1 notebook = 1 bảng đích. Tên suy ra từ `trg_tbl` (hoặc cột tuỳ chọn `nb_name` ở `pipeline_config`) | `NB_SLV_POI_SOURCE_MAP`, `NB_GLD_SRV_POI_REGISTRY` |
| `NB_SETUP_<LUỒNG>` | Chạy tay 1 lần: thêm cột ctrl, tạo + seed ref, cạnh, watermark. Mặc định chỉ in (`p_apply = false`) | `NB_SETUP_GOLD_POI_1H` |
| `NB_CREATE_DDL` | DDL + seed 7 bảng ctrl + `TABLE_CONFIGS` / `TABLE_CONFIGS_3P` | — |
| `CHECK_<CHỦ ĐỀ>_<DDMM>.py` | Script **chỉ đọc**, dán vào 1 cell, gửi lại output | `CHECK_PIN_EXTRACT_0510.py` |
| `DIAG_<CHỦ ĐỀ>_<DDMM>.py` | Chẩn đoán chỉ đọc (truy nguyên nhân) | `DIAG_GOLD_GAPS_0510.py` |
| `VERIFY_<CHỦ ĐỀ>_<DDMM>.py` / `PREVIEW_…` | Đối chiếu cấu hình ↔ payload thật, chỉ đọc | `VERIFY_3P_CONFIG_0410.py` |
| `APPLY_…_<DDMM>.sql`, `RERUN_…_<DDMM>.sql` | Script có ghi — chạy có chủ đích, theo runbook | `RERUN_ALL_0410.sql` |
| `<CHỦ ĐỀ>_REDESIGN.md`, `<…>_DESIGN.md`, `REVIEW_…_<DDMM>.md`, `PATCH_…_<DDMM>.md` | Tài liệu thiết kế / review / bản vá | `GOLD_POI_FLOW_DESIGN.md` |

Notebook cũ (không đổi tên): `NB_00_POI_PIPELINE_ORCHESTRATOR`, `NB_10…NB_60` (3P cũ), `1. parsing_bronze_partner`, `2.1 transform_partner_to_gold_poi_master`, `2.2 nb_cms_transform`, `3.1 …`, `4. …`, `5. nb_prepare_product_for_ingestion`, `6. …`.

## 3. Pipeline

| Mẫu | Ví dụ | Ghi chú |
|---|---|---|
| `PL_VV_TRANSFORM_<TỪ>_TO_<ĐẾN>_<HẬU TỐ>` | `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` | Pipeline extract (hậu tố `FL_00` = luồng chính) |
| Hậu tố nhịp `_<n>M` / `_<n>H` / `_<n>D` | `PL_VV_TRANSFORM_SLV_TO_GLD_1H`, `…_15M` `[PROPOSED]`, `…_1D` `[PROPOSED]` | **Bắt buộc với luồng tính lại**: lib đọc nhịp từ hậu tố (`CADENCE_RE = _(\d+)([MHD])$`) để chặn luồng nhanh đọc node của luồng chậm |

`pl_name` trong ctrl = đúng tên pipeline (`@pipeline().Pipeline`). 1 node chỉ thuộc 1 `pl_name` đang active.

## 4. Định danh dòng ctrl

| Đối tượng | Mẫu `watermark_id` | Ví dụ |
|---|---|---|
| Nguồn raw của extract | `wm_transform_<src_tbl>` | `wm_transform_partner_raw_data` |
| Cạnh của luồng tính lại (hộp thư) | `wm_e__<trg_tbl>__<src_tbl>` | `wm_e__slv_poi__slv_3p_poi` |
| Khoá cả luồng tính lại | `wm_flow__<pl_name>` | `wm_flow__PL_VV_TRANSFORM_SLV_TO_GLD_1H` |

| Id chạy | Ý nghĩa |
|---|---|
| `exec_id` | uuid sinh mỗi lần **notebook** chạy — khoá của `ctrl_log_run`; NB_00 truyền cho mọi node của lần chạy |
| `run_id` | `@pipeline().RunId`; chạy tay = `exec_id`. Không duy nhất theo notebook |
| `lock_exec_id` | `exec_id` của run đang giữ khoá |

`ctrl_mng_pipeline_config.id` = `MAX(id) + seq` khi seed (không phải khoá nghiệp vụ). Khoá logic: (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`).

## 5. Tên cột

### 5.1 Hậu tố / tiền tố có nghĩa cố định

| Mẫu | Nghĩa | Ví dụ |
|---|---|---|
| `*_at` | Thời điểm, **UTC**, kiểu `TIMESTAMP` (Python ghi `utc_now()` = UTC bỏ tzinfo) | `started_at`, `last_success_at` |
| `*_rows` | Số dòng / event | `input_rows`, `deactivated_rows` |
| `*_count` | Số đối tượng (bảng, lần) | `tbl_success_count`, `reject_count` |
| `is_*` / `has_*` | Cờ boolean | `is_active`, `has_required_langs` |
| `*_order` | Thứ tự đếm **từ 1** | `column_order`, `key_order` |
| `*_json` | Chuỗi JSON (mảng đã `array_sort` + bỏ trùng nếu đưa vào hash) | `src_versions_json`, `available_langs` (JSON) |
| `*_id` | Định danh | `poi_id`, `destination_id` |
| `*_norm` | Giá trị đã chuẩn hoá để so khớp (lower, bỏ tiền tố hành chính) | `ward_norm`, `province_norm` |
| `*_source` | Giá trị lấy từ đâu (enum, xem §6) | `name_source`, `address_source` |
| `src_*` / `trg_*` | Nguồn / đích (ctrl) | `src_tbl`, `trg_schema` |
| `last_*` | Giá trị của lần gần nhất (ctrl) | `last_src_version`, `last_run_id` |

### 5.2 Cột kỹ thuật theo tầng

| Tầng | Cột | Ý nghĩa |
|---|---|---|
| Silver L1 partner (CDC) | `deleted` BOOLEAN, `_ingested_at` TIMESTAMP, `_source_db` STRING | Xoá mềm theo `op = d`; lần MERGE gần nhất; `source.db` |
| Silver L1 3rd-party (snapshot) | `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`, `_ingested_at` | Tài liệu đang áp dụng; lần đầu / cuối thấy khoá; lần MERGE gần nhất. Không có xoá |
| Silver L2 + gold (luồng tính lại) | `row_hash` STRING, `created_at`, `updated_at`, `deleted_at` TIMESTAMP | `row_hash = sha2(to_json(struct(cột nghiệp vụ)), 256)`; `updated_at` chỉ đổi khi hash đổi; `deleted_at` khác NULL = xoá mềm (gold kèm `is_active = false`) |

Không đặt tên cột nghiệp vụ trùng cột kỹ thuật (lib chặn bằng `ConfigError`).

### 5.3 Cột nội bộ trong notebook (không ghi ra bảng)

Bắt đầu bằng `_` để không trùng cột nghiệp vụ.

| Mẫu | Ở đâu | Nghĩa |
|---|---|---|
| `_raw__<cột>` / `_raw__<cột>__<i>` | Extract | Chuỗi gốc lấy từ JSON trước khi chuyển kiểu / phần thứ i của khoá suy ra |
| `_b__<trường>` | Extract 3P | Trường cấp 1 của payload sau khi parse 1 lần |
| `_doc__<cột>` | Extract 3P | Cột của bảng raw (`_doc.<cột>` trong registry) |
| `_cn__<cột>` | Extract | Cờ: có giá trị ở raw nhưng thành NULL khi chuyển kiểu |
| `_unavailable__<cột>` | Extract partner | Cờ: raw là giá trị TOAST thay thế `__debezium_unavailable_value` |
| `_has_value__<cột>` | Extract partner | Cờ: batch có ít nhất 1 giá trị thật (kể cả NULL thật) cho cột TOAST |
| `_known__<cột>` | Extract partner | Struct giá trị TOAST gần nhất đã biết (bước điền) |
| `_cdc_ts_ms`, `_cdc_lsn`, `_raw_ingested_at`, `_is_delete`, `_op`, `_entity_key` | Extract (hợp đồng lib §13) | Thứ tự event và khoá state |
| `_st_key`, `_st_order` | Extract | State đã lưu |
| `_status`, `_reason`, `_reject_detail` | Extract | Phân loại VALID / IGNORED / REJECTED |
| `_parse_failed`, `_key_null`, `_is_stale`, `_applicable` | Extract | Cờ xử lý từng dòng |
| `_elem`, `_pos`, `_lang`, `_align`, `_langs` | Extract 3P | Phần tử / vị trí / ngôn ngữ / phần tử ghép theo vị trí / danh sách ngôn ngữ |
| `_v_<id>_<bảng>`, `_v_wm_<tag>`, `_v_setup_<nhãn>` | Mọi nơi | Tên temp view MERGE, duy nhất theo exec / bảng |

## 6. Giá trị enum

| Trường | Giá trị |
|---|---|
| `ctrl_mng_pipeline_config.load_mode` | `CDC` (NULL = CDC) · `DOC` · `DOC_ARRAY` · `LANG` · `LANG_ARRAY` · `RECOMPUTE` (cạnh luồng tính lại) |
| `ctrl_cfg_schema_registry.convert_rule` | `NONE` · `EPOCH_S_TS` · `EPOCH_MS_TS` · `EPOCH_US_TS` · `DATE_DAYS` · `DECIMAL_BASE64` · `LOWER_TRIM` · khoá suy ra: `HASH_MD5_UUID` · `HASH_SHA256` · `HASH_SHA256_PIPE` |
| `json_path` snapshot | `a.b` · `$` · `_doc.<cột>` · `_root.a.b` · `_langs` · `_lang` · `_pos` · `_align.a` · `p1,p2,...` (chỉ `HASH_*`) |
| `ctrl_log_run.status` | `RUNNING` · `SUCCESS` · `PARTIAL_FAILED` · `FAILED` · `NO_DATA` · `SKIPPED_CONCURRENT` · `ABANDONED` |
| `ctrl_log_run.run_mode` | Extract: `INCREMENTAL` · `FULL_RELOAD` · `DRY_RUN`. NB_00: `RUN` · `DRY_RUN` (`PLAN` không ghi log) |
| `ctrl_log_run.read_mode` | Extract: `VERSION` · `FULL`. NB_00: `VERSION_INBOX` |
| `ctrl_log_table_run.status` | `SUCCESS` · `FAILED` · `NO_DATA` · `SKIPPED` (NB_00 tự suy `NOT_RUN` khi node không có dòng log) |
| `ctrl_mng_watermark.status` | Nguồn: `INITIALIZED` · `RUNNING` · `SUCCESS` · `FAILED`. Cạnh: `INITIALIZED` · `SUCCESS` · `FAILED` · `SKIPPED` · `NOT_RUN`. Dòng khoá: trạng thái run cuối |
| `ctrl_mng_watermark.watermark_column` | Nguồn: tên cột thời gian raw (`EventProcessedUtcTime`, `crawled_at`). Cạnh: `commit_ts`. Dòng khoá: `LOCK_EXPIRES_AT` |
| `ctrl_cdc_reject.reject_reason` | `MISSING_ENTITY_KEY` · `MISSING_EVENT_ORDER` · `MISSING_RAW_CURSOR` · `INVALID_PAYLOAD` |
| Lý do bỏ qua (`ignored_detail`) | Partner: `TOMBSTONE` · `OP_TRUNCATE` · `OP_MESSAGE` · `UNCONFIGURED` · `OUT_OF_SCOPE`. 3P: `OUT_OF_SCOPE` |
| Lý do cạnh (`edge_status`) | Bẩn: `MISSING_TABLE` · `NEW_EDGE` · `TABLE_RECREATED` · `VERSION_BACKWARD` · `HISTORY_GAP` · `DATA_CHANGED` · `PARENT_NOT_BUILT`. Sạch: `UNCHANGED` · `MAINTENANCE_ONLY` |
| `cast_null_policy` | `FAIL` · `WARN` |
| `slv_poi_source_map.match_rule` | `SELF` (hiện tại) · `PARTNER_LINK` · `POI_MGMT` · `MANUAL` `[PROPOSED]` |
| `slv_poi.category_rule` | `EXACT` · `SECTOR` · `SOURCE_DEFAULT` · `PASS_THROUGH` |
| `slv_poi.lifecycle_state` | `ACTIVE` · `MERGED` |
| `slv_poi_address.address_source` / `coord_source` | `3P` · `PARTNER_VIETMAP` · `PARTNER_JSON` · `NONE` / `GOOGLE_ENRICH` |
| `name_source` / `description_source` | `SOURCE` · `ENRICHMENT` · `I18N` · `CONTENT` · `FALLBACK_UNACCENT` · `FALLBACK_COPY` |
| `ref_lang_policy.fallback_method` | `UNACCENT` · `COPY` |
| `slv_poi_destination.match_rule` / `relation_type` | `WARD_PROVINCE` · giá trị `match_rule` của ref (vd `ADDR_TOKEN`) / `DIRECT` · `ANCESTOR` |

## 7. Tham số notebook

| Loại | Quy ước | Ví dụ |
|---|---|---|
| Extract | Tên thường, không tiền tố | `allow_full_scan`, `max_parallel`, `table_filter`, `running_timeout_minutes` |
| Luồng tính lại (NB_00, node, setup) | Tiền tố `p_`, **giá trị chuỗi** (pipeline truyền chuỗi), lib tự ép kiểu + kiểm tra miền | `p_pl_name`, `p_mode`, `p_force_nodes` |
| Bool | `"true"` / `"1"` / `"yes"` / `"y"` = True (`to_bool`) | |
| Danh sách | CSV, bỏ khoảng trắng, bỏ phần tử rỗng (`split_csv`) | `"slv_poi,slv_poi_address"` |
| Bắt buộc từ pipeline | `pl_name` / `p_pl_name` = `@pipeline().Pipeline` (hoặc tên luồng), `run_id` / `p_run_id` = `@pipeline().RunId` | |

## 8. Convention code

| Hạng mục | Quy ước |
|---|---|
| Ngôn ngữ | Comment, docstring, log, tài liệu bằng tiếng Việt chuẩn, từ ngữ đơn giản |
| Docstring | Mỗi hàm: mục đích 1 dòng → `Input :` → `Output:` → `Ví dụ :` (giá trị cụ thể) |
| Đánh dấu thay đổi | `[SỬA dd/mm]`, `[THÊM dd/mm]`, kèm phạm vi khi cần: `[SỬA 03/10 - 3P]`, `[03/10 → LIB]`, `[05/10 review #2]`, `[H1 04/10]`, `[SỬA C2 04/10]`. Ghi **vì sao**, không chỉ ghi đã làm gì |
| Nhãn tài liệu | `[PROPOSED]` tên mới chưa chốt · `[VERIFY]` cần kiểm tra trên Fabric · `[ASSUMED]` giả định chưa xác nhận · `[NEEDS-SCHEMA]` cần schema nguồn · `OD-xx` quyết định mở · `ADR-xx` quyết định kiến trúc |
| Không viết cứng | Tên bảng / cột / lang / rule / notebook đọc từ ctrl, ref, tham số. Tên 4 phần kiểu `sgr_visitvn_stg.*` cấm (không đổi theo môi trường được) |
| An toàn SQL | Tên ghép vào SQL phải qua `is_identifier` / `is_fq_name` rồi `quote_name`; giá trị truyền bằng tham số `spark.sql(..., args={...})` |
| Lib | Chỉ định nghĩa; không đọc / ghi khi `%run`; không `spark.conf.set`; không phụ thuộc nguồn cụ thể. Deploy lib **trước** notebook gọi |
| Lỗi | Cấu hình sai → `ConfigError` gom đủ lỗi, raise **trước** khi ghi. Lỗi tạm thời (xung đột Delta, HTTP 430, mất kết nối) → `with_retry` (6 lần, 2s→32s + jitter) |
| Ghi bảng ctrl | Chỉ luồng chính ghi (luồng con / node chỉ append log của mình); MERGE theo khoá logic hoặc `NOT EXISTS` trước INSERT (Delta không có PK) |
| Thời gian | Ghi UTC; hiển thị giờ VN bằng `from_utc_timestamp(..., 'Asia/Ho_Chi_Minh')` |
| Bảng mới | `optimizeWrite` + `autoCompact` bật; không `CLUSTER BY` trên Runtime 1.3 |
| Script kiểm tra | Chỉ đọc, dán cả file vào 1 cell, in đủ để gửi lại; ghi rõ kết quả kỳ vọng |
| Kiểm chứng | Code mới chưa được tin cho tới khi chạy kiểm chứng (test local hoặc chạy dev); không suy đoán dữ liệu — hỏi hoặc viết script chỉ đọc |
