# Problem analysis — 20261104-extract-cms-raw-data

## Phạm vi

- Task gốc: `20261104-extract-cms-raw-data` (`task-state.yaml` → `task.title`: "Extract cms_raw_data with existing load modes", `status: triage`, `classification.complexity: low`, `scope.systems`: `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_ctrl`).
- Câu hỏi phân tích: Nếu thêm extract bronze `lh_vv_bronze.dbo.cms_raw_data` → silver L1 và chỉ dùng một trong các `load_mode` đang có (`CDC`, `DOC`, `DOC_ARRAY`), không thêm giá trị mới vào `LOAD_MODES`, thì hiện trạng có những gì, còn thiếu gì, và những gì chưa biết.
- Ngoài phạm vi: đề xuất giải pháp, thiết kế bảng silver, `json_path`, khóa, rule chuyển kiểu.
- Ledger `Quyết định hiện hành` trong `decision.md` chưa có dòng nào. `## Quyết định của người dùng` ghi "Chưa có." Chưa có `requirements-analysis.md` trong thư mục task.

## Bài toán

Theo lời người dùng: "thêm extract bronze cms_raw_data. Tái sử dụng load_mode đang có của partner và 3rd-party. Không thêm giá trị mới vào LOAD_MODES."

Các đối tượng người dùng nêu: `lh_vv_bronze.dbo.cms_raw_data`; extract notebook và registry dùng mode cũ; bảng silver đích chưa có vì người dùng chưa nêu.

Người dùng cũng nêu các giới hạn sau:
- Chỉ có một dòng mẫu, và mẫu này chỉ cho khóa cùng kiểu JSON (`evidence/payload-shape.md`). Một dòng không phải hợp đồng schema.
- Yêu cầu chưa cho kiểu Delta thật của các cột bronze, và không được suy ra kiểu đó từ một dòng.
- `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` không được gắn `cms_raw_data` vào activity hiện có.
- Chưa có danh sách bảng silver, grain, khóa hay cột cần giữ.

## Hiện trạng

### Miền `load_mode` trong thư viện

- H1. `LOAD_MODES` = `CDC, DOC, DOC_ARRAY`. `SNAPSHOT_MODES` = `DOC, DOC_ARRAY` (`docs/context/NB_LIB_EXTRACT_RAWDATA.md`, `### §1 constants`).
- H2. Với bảng snapshot, `json_path` chỉ nhận các dạng sau: `a.b`, `$`, `_doc.<cột raw>`, `_root.a.b`, `_langs`, `_pos` (chỉ `DOC_ARRAY`), `_align.a` và `p1,p2,...` (chỉ `HASH_*`). Snapshot không để `json_path` NULL (`NB_LIB_EXTRACT_RAWDATA.md`, `### §1 constants`, đoạn "Bảng `json_path` của bảng snapshot").
- H3. Cột `load_mode` của `ctrl_mng_pipeline_config` nhận `CDC` cho partner (NULL = CDC) và `DOC` / `DOC_ARRAY` cho 3P. Notebook tự kiểm tra: partner chỉ nhận `CDC`, 3P chỉ nhận `DOC` và `DOC_ARRAY`. Lúc nạp, lib báo lỗi khi `load_mode` nằm ngoài miền hoặc không thuộc notebook (`docs/context/CTRL_TABLES_CONTEXT.md`, `## 3`, `### DDL` và `### Cột`).

### Mode `CDC` (partner)

- H4. Bảng raw partner có các cột `before`, `after`, `source` (JSON chuỗi), `op` và `EventProcessedUtcTime`. Mỗi event là một thay đổi của một dòng trong một bảng Postgres (`source.schema`, `source.table`) (`docs/context/01_DATA_MODEL.md`, `## 4. Bronze — bảng raw`, dòng `partner_raw_data`).
- H5. `read_raw` của partner đọc `before`, `after`, `source`, `op`. Luật phân loại như sau: `op`, `before`, `after` đều NULL thì `IGNORED` / `TOMBSTONE`. `op` NULL hoặc nằm ngoài `c r u d` thì `REJECTED` / `INVALID_PAYLOAD`. Thiếu `source.table` cũng `REJECTED` (`docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md`, `## 6`, `### A. Đọc và phân loại raw`).
- H6. Partner dùng các hằng số Debezium `VALID_OPS`, `TOAST_SENTINEL`, `SOURCE_FIELDS` (`schema`, `table`, `db`, `ts_ms`, `lsn`). Notebook partner gọi `load_table_specs` với `allowed_modes = ("CDC",)` (`NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md`, `## 4. Hằng số Debezium`, `## 5. Luồng`).
- H7. Notebook partner được gọi qua `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` → `ForEach_Source` → `If_HasWork` → activity `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK`. Notebook này đọc `partner_raw_data` và giữ khóa trên dòng `wm_transform_partner_raw_data` (`NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md`, `## 1. Mô tả`).

### Mode `DOC` / `DOC_ARRAY` (3rd-party)

- H8. Bảng raw 3P có các cột `event_id`, `source_name`, `source_id`, `crawled_at`, `ingested_date`, `normalized_payload`, `raw_payload`, `language_code`, tất cả là STRING. Mỗi event là một tài liệu đầy đủ (snapshot), không có tín hiệu xóa và không có TOAST (`01_DATA_MODEL.md`, `## 4`, dòng `brz_3rd_crawler_poi_stream`).
- H9. Hằng số nguồn 3P:
  - `RAW_PAYLOAD` = `normalized_payload`
  - `RAW_EVENT_ID` = `event_id`
  - `RAW_DOC_ID` = (`source_name`, `source_id`), bắt buộc
  - `RAW_LANG` = `language_code`
  - `ARRAY_MODES` = `DOC_ARRAY`
  
  Cột thứ tự lấy từ `watermark_column` của dòng watermark (`crawled_at`), không viết cứng (`docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `## 5. Hằng số nguồn`).
- H10. Luật phân loại tài liệu 3P: `source_name` / `source_id` NULL hoặc rỗng thì `REJECTED` / `MISSING_ENTITY_KEY`. Payload không phải JSON object thì `INVALID_PAYLOAD`. `crawled_at` NULL thì `MISSING_EVENT_ORDER` (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `## 7`, `### A`, bảng luật phân loại).
- H11. `expand_rows` tách dòng theo `load_mode`:
  - `DOC` với `$` cho một dòng / tài liệu.
  - `DOC` với khối khác cho một dòng khi khối khác NULL.
  - `DOC_ARRAY` dùng `posexplode`.
  - Mode khác thì `ConfigError`.
  
  `presence`: `DOC_ARRAY` chỉ có khi mảng ≥ 1 phần tử (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `## 7`, `### A` dòng `presence` và `### B` dòng `expand_rows`).
- H12. 3P khác partner ở các điểm sau: thứ tự theo `crawled_at` rồi `event_id`; state theo `poi_id` (`state_key = "doc"`); khối vắng thì giữ dữ liệu cũ; không xóa; khóa được suy ra bằng hash (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `## 3. Khác partner`). Tham số `doc_key_column` (mặc định `poi_id`) phải có trong registry của mọi bảng (`## 4. Tham số`).
- H13. Bảng đích 3P đang dùng `DOC` cho `$` và các khối object, và dùng `DOC_ARRAY` cho các khối mảng (`poi_review`, `poi_media`) (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `## 8. Bảng đích`).

### Cấu hình ctrl

- H14. `ctrl_mng_pipeline_config` hiện có dòng `pl_name = PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` cho hai nguồn. Nguồn `partner_raw_data` có 23 bảng `CDC`. Nguồn `brz_3rd_crawler_poi_stream` có 9 bảng `DOC` / `DOC_ARRAY`. Không có dòng nào cho `cms_raw_data` (`CTRL_TABLES_CONTEXT.md`, `## 3`, `### Dữ liệu hiện có`).
- H15. Các luật của `ctrl_cfg_schema_registry`:
  - Mỗi bảng đích ứng với đúng một (`src_object_schema`, `src_object`).
  - Mỗi bảng có ≥ 1 cột khóa.
  - Với snapshot: `src_object` là khối trong payload (`$` = gốc). `src_object_schema` NULL. `json_path` không NULL. `$` không dùng với `*_ARRAY`.
  
  Registry hiện có partner và 3P, không có `cms_raw_data` (`CTRL_TABLES_CONTEXT.md`, `## 5`, `### DDL`, `### Luật cấu hình`, `### Dữ liệu hiện có`).

### Quy ước đặt tên

- H16. Tên raw ở bronze theo nguồn, và hiện chỉ có hai tên. Quy ước ghi rõ: "Không suy ra thêm quy tắc đặt tên raw". Tiền tố silver L1 đã định nghĩa chỉ có `slv_pn_`, `slv_3p_poi_` và `slv_pm_` `[PROPOSED]` (`docs/context/02_NAMING_CONVENTION.md`, `## 1`).
- H17. Notebook extract đặt tên theo mẫu `NB_EXTRACT_<NGUỒN>_CDC_BRZ_TO_SLV`, một notebook / nguồn. Danh sách notebook cũ có `2.2 nb_cms_transform` (`02_NAMING_CONVENTION.md`, `## 2. Notebook`).

### Dòng mẫu `cms_raw_data`

- H18. Dòng mẫu của `cms_raw_data` có các cột `event_id`, `source_name`, `type`, `crawled_at`, `ingested_date`, `raw_payload`. Kiểu Delta của cả sáu cột là `MISSING_EVIDENCE` (`.ai/tasks/20261104-extract-cms-raw-data/evidence/payload-shape.md`, `## Bronze columns on the sample row`).
- H19. Dòng mẫu không có `before`, `after`, `op`, `source.schema`, `source.table`, `source_id`, `normalized_payload`, `language_code` (`payload-shape.md`, `## Not on the sample row`).
- H20. `raw_payload` sau khi parse (`payload-shape.md`, `## raw_payload after parse`):
  - Gốc là object.
  - Cấp gốc có các trường vô hướng `id`, `documentId`, `createdAt`, `updatedAt`, `publishedAt`, `locale`, `name`, `description`, `slug`.
  - Có các mảng object `cover_gallery`, `SEO`, `FAQ`, `experiences`, `highlight`.
  - Có mảng `pois`, kiểu phần tử là `MISSING_EVIDENCE`.
  - Các khóa con trong `cover_gallery[].formats.{large,small,medium,thumbnail}` đều là `MISSING_EVIDENCE`.
  - Cấp gốc không có khối object nào ngoài các mảng.
- H21. `type` ở đây chỉ là tên cột bronze. Một giá trị chưa đủ để coi nó là `language_code` hay entity type (`payload-shape.md`, `## Bronze columns on the sample row`, đoạn ghi chú).

## Khoảng trống hoặc nguyên nhân

- K1. Chưa thể chọn `CDC` cho `cms_raw_data`. Dòng mẫu không có `before`, `after`, `op`, `source` (H19), trong khi partner đọc đúng các cột đó và dựa vào `op` cùng `source.table` (H4, H5, H6). Nếu đọc bằng luật partner, dòng như mẫu sẽ rơi vào luật 1 (`TOMBSTONE`).
- K2. Hình dạng dòng mẫu giống loại "một event = một tài liệu" của snapshot (H8, H18), là loại mà `DOC` / `DOC_ARRAY` phục vụ (H1, H11, H13). Có ba điểm chưa khớp:
  - Hằng số nguồn 3P cần `normalized_payload`, `source_id`, `language_code` (H9). Cả ba không có trên dòng mẫu (H19).
  - Nếu dùng nguyên luật 3P, thiếu `source_id` sẽ dẫn tới `REJECTED` / `MISSING_ENTITY_KEY` (H10).
  - Hằng số nguồn nằm trong notebook 3P (H9), còn tên notebook là một notebook / nguồn (H17). Vì vậy notebook 3P hiện tại không đọc được `cms_raw_data` khi giữ nguyên hằng số.
- K3. Định danh tài liệu và khóa còn trống. 3P bắt buộc `doc_key_column` ở mọi bảng và lấy `poi_id` từ `source_name`, `source_id` (H12). Với `cms_raw_data`, người dùng chưa nêu cột hay khóa định danh nào (H18, H20, `## Bài toán`). Registry lại đòi ≥ 1 cột khóa cho mỗi bảng (H15).
- K4. Bảng đích còn trống. Registry và pipeline config chưa có dòng nào cho `cms_raw_data` (H14, H15). Tiền tố silver L1 cũng chưa có cho nguồn CMS (H16).
- K5. Kiểu Delta còn trống. Kiểu của `crawled_at`, `ingested_date` và các cột khác là `MISSING_EVIDENCE` (H18). 3P lấy cột thứ tự từ `watermark_column` (`crawled_at`) (H9), nhưng tài liệu chỉ ghi kiểu STRING cho bảng 3P (H8), không ghi cho `cms_raw_data`.
- K6. Ngữ nghĩa cột chưa rõ:
  - `type` chưa có nghĩa đã xác nhận (H21).
  - `locale` trong payload (H20) chưa được xác nhận có tương đương `RAW_LANG` / `_langs` hay không (H2, H9).
- K7. Một số phần của payload chưa có bằng chứng. `pois[]` không có phần tử, nên `presence` của `DOC_ARRAY` sẽ không sinh dòng nào (H11). Khóa con của `formats.*` cũng chưa thấy (H20). Không có bằng chứng để đặt `json_path` cho các phần này (H2).
- K8. Cách điều phối chưa rõ:
  - Người dùng cấm gắn `cms_raw_data` vào activity của `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` (`## Bài toán`).
  - Tài liệu đã đọc chỉ cho thấy activity partner (H7). Trong khi đó, dòng config 3P vẫn mang `pl_name` đó (H14).
  - Các mục đã đọc không cho biết notebook 3P được gọi thế nào, và notebook mới sẽ chạy theo pipeline hay lịch nào.
- K9. Quan hệ giữa notebook cũ `2.2 nb_cms_transform` (H17) và `cms_raw_data` không có trong các mục đã đọc.

## Đối tượng bị ảnh hưởng

- Bảng raw: `lh_vv_bronze.dbo.cms_raw_data`, chỉ đọc.
- Notebook:
  - Một notebook extract mới theo mẫu `NB_EXTRACT_<NGUỒN>_CDC_BRZ_TO_SLV` (H17). Tên `<NGUỒN>` chưa chốt.
  - `NB_LIB_EXTRACT_RAWDATA`, được dùng qua `%run`. Không sửa chữ ký mode nếu `DOC` / `DOC_ARRAY` đủ dùng.
  - `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` và `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, là các bản tham chiếu hành vi mode.
  - `2.2 nb_cms_transform`, chưa rõ mức ảnh hưởng (K9).
- Cấu hình ctrl:
  - `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`, sẽ có dòng mới cho `src_tbl = cms_raw_data` (H3, H14).
  - `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry`, sẽ có dòng mới cho `src_tbl = cms_raw_data` (H15).
  - Dòng watermark mà 3P dùng để lấy `watermark_column` (H9).
- Bảng ctrl mà extract ghi khi chạy: `ctrl_cdc_state`, `ctrl_cdc_reject`, `ctrl_log_run`, `ctrl_log_table_run`, `ctrl_mng_watermark` (`NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md`, `## 1. Mô tả`, dòng "Ghi"; `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `## 7`, `### C`).
- Seed / DDL: một cell mới ở cuối `NB_CREATE_DDL` cho môi trường đã có bảng, và `NB_SETUP_INITIAL_DDL` cho môi trường trống (`02_NAMING_CONVENTION.md`, `## 2. Notebook`).
- Pipeline: `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, chỉ ở mức ràng buộc "không gắn vào activity hiện có". Pipeline sẽ chạy notebook mới chưa xác định.
- Bảng silver đích: chưa có (K4).
- Consumer hạ nguồn: các mục đã đọc không cho thấy consumer nào của dữ liệu CMS ở silver L2 / gold.

## Câu hỏi

1. Bảng silver đích của `cms_raw_data` gồm những bảng nào, và dùng tiền tố nguồn nào? Hiện chỉ có `slv_pn_`, `slv_3p_poi_`, `slv_pm_` `[PROPOSED]`.
2. Mỗi bảng đích có grain gì, cột khóa nào, và giữ những cột nào?
3. Cột hoặc trường nào định danh một tài liệu CMS? Câu hỏi này tương đương `RAW_DOC_ID` và `doc_key_column` của 3P. Dòng mẫu không có `source_id`.
4. Kiểu Delta thật của `event_id`, `source_name`, `type`, `crawled_at`, `ingested_date`, `raw_payload` trong `lh_vv_bronze.dbo.cms_raw_data` là gì?
5. Mỗi event của `cms_raw_data` có phải luôn là một tài liệu đầy đủ (snapshot) không? Nguồn có tín hiệu xóa hay event Debezium (`before`, `after`, `op`, `source`) nào không?
6. Payload cần đọc có phải là `raw_payload` không? Bảng có cột payload nào khác không?
7. Cột `type` có nghĩa gì, có những giá trị nào, và có dùng để lọc hay phân bảng không?
8. `source_name` có những giá trị nào? Có cần một tham số lọc nguồn tương tự `sources` của 3P không?
9. `locale` trong payload có phải ngôn ngữ của tài liệu không? Nó có cần đối ứng với `RAW_LANG` / `_langs` không?
10. Cột thứ tự event là gì (ví dụ `crawled_at` làm `watermark_column`), và khi trùng thì xếp theo cột nào?
11. Notebook extract mới tên gì (`<NGUỒN>`)? Pipeline, activity hoặc lịch nào sẽ chạy nó, khi không được gắn vào activity của `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`? Notebook 3P hiện được gọi thế nào?
12. Dòng watermark và khóa chống chạy chồng dành cho `cms_raw_data` có id và `watermark_column` gì?
13. Phần tử của `pois[]` có hình dạng gì? Khi nào có mẫu có phần tử?
14. Khóa con của `cover_gallery[].formats.{large,small,medium,thumbnail}` có những gì, và có cần giữ không?
15. Notebook cũ `2.2 nb_cms_transform` có đọc `cms_raw_data` không? Nó có liên quan tới cutover của extract mới không?
16. `cms_raw_data` có được ghi append-only bởi Eventstream giống hai bảng raw hiện có không? Bảng có cho phép đọc theo version Delta không?
