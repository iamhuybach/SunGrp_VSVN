# Mẫu Business Requirements Document (BRD) — VSVN

> `template_id`: `VSVN-BRD-v1`. Mẫu này đi cùng `docs/templates/MAPPING_TEMPLATE.md` (`VSVN-MAPPING-v1`). Agent `requirements-analyst` (`.claude/agents/requirements-analyst.md`) đọc file đã điền theo đúng tên mục, tên cột và giá trị cho phép của mẫu này.
> Phần mô tả viết bằng tiếng Việt. Tên trường, tên bảng, tên cột, giá trị trạng thái và định danh giữ bằng tiếng Anh.
> Dòng và đoạn có nhãn `[EXAMPLE]` chỉ minh hoạ cách điền. Đó không phải dữ liệu production và không phải yêu cầu thật. Mọi giá trị trong phần `[EXAMPLE]` có nguồn ở `context_ref`, hoặc để trống và đặt `MISSING_EVIDENCE`.
> Không ghi dữ liệu cá nhân, secret, token hoặc trích xuất dữ liệu production vào file này.

## Cách điền

1. Sao chép mẫu thành `docs/requirements/<task_id>/BRD.md`. Mỗi task có đúng 1 file BRD và 1 file Mapping. Không lưu bản đã điền trong `.ai/tasks/`, vì task artifact ở đó phải viết bằng tiếng Anh (`AGENTS.md §1`).
2. Giữ nguyên mục "Quy ước dùng chung", tên mục, tên cột và thứ tự cột. Không xoá cột. Ô không dùng thì để trống.
3. Xoá mọi dòng và đoạn `[EXAMPLE]` trước khi đặt `doc_status` là `READY_FOR_ANALYSIS`. Agent bỏ qua phần `[EXAMPLE]` còn sót và báo lại.
4. Mỗi yêu cầu là 1 dòng ở mục 5. `statement` là yêu cầu của người dùng, viết sao cho kiểm chứng được. Sự kiện về hệ thống đã có được nêu trong yêu cầu cần `context_ref`.
5. Mỗi yêu cầu có bảng đích, grain và khoá ở mục 5, và có ít nhất 1 dòng nguồn ở mục 6. Cột nguồn chi tiết ghi ở Mapping mục 5.
6. Rule nghiệp vụ ghi ở mục 7. Rule repository đã nêu: đặt `CONTEXT_STATED` và ghi `context_ref`. Rule mới do người dùng đặt ra: ghi nguyên văn, đặt `USER_STATED` và ghi `context_ref` là `USER_INPUT`. Không tự đặt rule. Rule chỉ nằm ở tầng cho phép trong "Ràng buộc nền tảng".
7. Chỉ ghi một giá trị khi có nguồn hợp lệ theo `evidence_status` ở mục "Quy ước dùng chung". Ghi nguồn vào `context_ref`.
8. Khi chưa có nguồn: để trống ô, đặt `MISSING_EVIDENCE` và thêm 1 dòng ở mục 11 có `blocks` chứa ID của dòng đó. Nguồn có ghi giá trị nhưng nói rõ là chưa xác nhận: được ghi giá trị đó, đặt `MISSING_EVIDENCE` và nêu lý do ở `note`. Không đoán bảng, cột, kiểu dữ liệu, khoá, grain, giá trị enum, công thức hoặc rule.
9. Dòng ở mục 11 có `resolution_type` là `USER_ANSWER` hoặc `EXTERNAL` cần ít nhất 1 câu hỏi ở mục 13 có `blocks` chứa `gap_id` đó.
10. Hai nguồn trong repository nói khác nhau: không tự chọn. Đặt `CONFLICT`, thêm 1 dòng ở mục 12 và 1 câu hỏi ở mục 13 có `blocks` chứa `conflict_id` đó (`docs/context/00_README.md`, mục "Quy tắc khi làm việc với bộ này").
11. Tên mới chưa có trong repository: đặt `name_status` hoặc `trg_name_status` là `PROPOSED` và ghi nhãn `[PROPOSED]` ở `note`. Tên bảng mới phải đúng tiền tố của tầng ở mục "Quy ước dùng chung".
12. Khi có câu trả lời: ghi `answer` và `answered_on` ở mục 13, sửa ô liên quan theo luật của `evidence_status`, rồi tăng `version`.

## Quy ước dùng chung

> Mục này giống hệt nhau ở `docs/templates/MAPPING_TEMPLATE.md` và `docs/templates/BRD_TEMPLATE.md`. Không sửa mục này khi điền tài liệu.

### Giá trị cho phép

| field | value | Ý nghĩa |
|---|---|---|
| `doc_status` | `DRAFT` | Đang soạn. Agent `requirements-analyst` không phân tích |
| `doc_status` | `READY_FOR_ANALYSIS` | Đã xoá dòng và đoạn `[EXAMPLE]`. Sẵn sàng cho agent `requirements-analyst` |
| `evidence_status`, `*_evidence` | `CONTEXT_STATED` | Một file trong repository nêu đúng giá trị: `AGENTS.md`, file trong `docs/context/`, notebook trong `notebooks/` hoặc pipeline trong `pipelines/`. `context_ref` ghi đường dẫn và mục, hoặc đường dẫn và tên cell, biến hay hàm trong notebook |
| `evidence_status`, `*_evidence` | `TASK_EVIDENCE` | Kết quả probe đã làm sạch ở `.ai/tasks/<task_id>/evidence/results/` nêu đúng giá trị. `context_ref` ghi đường dẫn file kết quả |
| `evidence_status`, `*_evidence` | `USER_STATED` | Người dùng hoặc chủ nghiệp vụ đặt ra giá trị. `context_ref` ghi `USER_INPUT` khi giá trị nêu ngay trong tài liệu, hoặc ghi `q_id` của câu hỏi đã có `answer` và `answered_on`. Chỉ dùng cho yêu cầu và quyết định: câu yêu cầu, phạm vi, mức ưu tiên, rule mới, giá trị phi chức năng, tên `PROPOSED`, grain và khoá của bảng `PROPOSED`, nơi đặt rule mới. Không dùng cho sự kiện về đối tượng `EXISTING`: cột, grain, khoá, kiểu dữ liệu, độ duy nhất, tỉ lệ NULL, định dạng, giá trị enum, rule hoặc công thức đã có. Các sự kiện đó cần `CONTEXT_STATED` hoặc `TASK_EVIDENCE` (`AGENTS.md §5`, `§8`) |
| `evidence_status`, `*_evidence` | `MISSING_EVIDENCE` | Chưa có nguồn hợp lệ, hoặc nguồn có ghi giá trị nhưng nói rõ là chưa xác nhận. Cần 1 dòng ở mục thiếu evidence của cùng file, có `blocks` chứa ID của dòng |
| `evidence_status`, `*_evidence` | `CONFLICT` | Hai nguồn trong repository nói khác nhau. Cần 1 dòng ở mục mâu thuẫn và 1 câu hỏi ở mục câu hỏi mở của cùng file |
| `evidence_status`, `*_evidence` | Nhiều giá trị | Được ghi nhiều giá trị trong `CONTEXT_STATED`, `TASK_EVIDENCE`, `USER_STATED`, cách nhau bằng dấu phẩy, khi giá trị dựa trên nhiều loại nguồn. `MISSING_EVIDENCE` và `CONFLICT` luôn đứng một mình |
| `name_status`, `trg_name_status` | `EXISTING` | Tên đã có trong repository. `context_ref` chỉ nơi nêu tên |
| `name_status`, `trg_name_status` | `PROPOSED` | Tên mới chưa có trong repository. Ghi nhãn `[PROPOSED]` ở `note` (`docs/context/02_NAMING_CONVENTION.md`, phần đầu file) |
| `layer` | `bronze`, `silver_l1`, `silver_l2`, `ref`, `gold`, `ctrl` | Tầng theo `docs/context/01_DATA_MODEL.md §2` |
| `resolution_type` | `REPO_READ` | Đọc thêm file trong repository |
| `resolution_type` | `PROBE` | Probe chỉ đọc trên Fabric DEV. Main viết probe, người dùng chạy (`AGENTS.md §8`). Ghi tiêu chí đạt và không đạt bằng lời, không viết code |
| `resolution_type` | `USER_ANSWER` | Người dùng hoặc chủ nghiệp vụ trả lời. Cần 1 câu hỏi có `blocks` chứa `gap_id` |
| `resolution_type` | `EXTERNAL` | Chờ team nguồn hoặc hệ thống bên ngoài. Cần 1 câu hỏi có `blocks` chứa `gap_id` |
| `priority` | `MUST`, `SHOULD`, `COULD` | Mức ưu tiên của yêu cầu ở BRD mục 5 |
| `scope` | `IN`, `OUT` | Trong hoặc ngoài phạm vi ở BRD mục 3 |
| `is_key` | `true`, `false` | Cột thuộc khoá của bảng đích ở Mapping mục 5 |
| `key_order` | Số nguyên từ 1 | Thứ tự trong khoá ghép của bảng silver L1 (`ctrl_cfg_schema_registry.key_order`, `docs/context/CTRL_TABLES_CONTEXT.md §5`). Để trống ở tầng khác và khi `is_key` là `false` |
| `field` | `pl_name`, `load_mode`, `orchestrator`, `nb_name`, `cadence` | Cột `field` ở Mapping mục 2 |
| `load_mode`, `convert_rule` | Giá trị ở `docs/context/02_NAMING_CONVENTION.md §6` | Mẫu không chép lại danh sách |
| `context_ref` | `<path> §<mục>`, `<path> <cell, biến hoặc hàm>`, `<file kết quả>`, `<q_id>`, `USER_INPUT` | Nguồn của giá trị. Nhiều nguồn cách nhau bằng dấu phẩy |

### Tiền tố bảng theo tầng

| layer | lakehouse_schema | Tiền tố bảng | context_ref |
|---|---|---|---|
| `bronze` | `lh_vv_bronze.dbo` | Không có tiền tố chung. Hai bảng raw đang dùng là `partner_raw_data` và `brz_3rd_crawler_poi_stream`. Không suy ra quy tắc đặt tên raw | `docs/context/02_NAMING_CONVENTION.md §1` |
| `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_` cho partner (`slv_pn_<bảng Postgres>`). `slv_3p_` cho 3rd-party (`slv_3p_poi` và `slv_3p_poi_<khối>`). `slv_pm_` `[PROPOSED]` cho POI management | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `ref` | `lh_vv_silver.dbo` | `ref_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `gold` | `lh_vv_gold.dbo` | `gld_`. Bảng phục vụ đặt tên `gld_srv_<chủ đề>_<grain>` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `ctrl` | `lh_vv_ctrl.dbo` | `ctrl_mng_`, `ctrl_cfg_`, `ctrl_log_`, `ctrl_cdc_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |

Bảng cũ không theo tiền tố trên, như `poi_master`, `destination_ward_mapping`, bảng `poi_*` cũ ở silver và `lh_vv_bronze.partner.*`, giữ nguyên tới cutover (`docs/context/01_DATA_MODEL.md §1`, `docs/context/02_NAMING_CONVENTION.md §1`). Yêu cầu có bảng đích là bảng cũ cần 1 câu hỏi cho người dùng.

### Định danh

| ID | Dạng | Ghi ở |
|---|---|---|
| `task_id` | Tên thư mục `.ai/tasks/<task_id>/`, dạng `YYYYMMDD-slug` (`AGENTS.md §4`) | Mục 1 của cả hai file |
| `mapping_id` | `MAP-<task_id>` | Mục 1 của cả hai file |
| `brd_id` | `BRD-<task_id>` | Mục 1 của cả hai file |
| `version` | Số nguyên từ 1, tăng 1 mỗi lần sửa file | Mục 1 của từng file |
| `updated_on` | `YYYY-MM-DD` | Mục 1 của từng file |

| Tiền tố dòng | File | Mục |
|---|---|---|
| `FLOW-` | Mapping | 2. Luồng xử lý |
| `SRC-` | Mapping | 3. Bảng nguồn |
| `TRG-` | Mapping | 4. Bảng đích |
| `COL-` | Mapping | 5. Mapping cột |
| `MGAP-` | Mapping | 6. Mục thiếu evidence |
| `MCONF-` | Mapping | 7. Mâu thuẫn trong repository |
| `MQ-` | Mapping | 8. Câu hỏi mở |
| `SCOPE-` | BRD | 3. Phạm vi |
| `CSM-` | BRD | 4. Bên sử dụng dữ liệu |
| `BR-` | BRD | 5. Yêu cầu nghiệp vụ |
| `DS-` | BRD | 6. Nguồn dữ liệu |
| `RULE-` | BRD | 7. Rule nghiệp vụ |
| `ID-` | BRD | 8. Định danh |
| `NFR-` | BRD | 9. Yêu cầu phi chức năng |
| `AC-` | BRD | 10. Tiêu chí nghiệm thu |
| `BGAP-` | BRD | 11. Mục thiếu evidence |
| `BCONF-` | BRD | 12. Mâu thuẫn trong repository |
| `BQ-` | BRD | 13. Câu hỏi mở |

- Dòng thật: tiền tố cộng 3 chữ số, bắt đầu từ `001`, không trùng trong file.
- Dòng minh hoạ: tiền tố cộng `EX-` và 2 chữ số. Ô đầu của dòng bắt đầu bằng `[EXAMPLE]`.
- Cột trỏ sang dòng khác (`trg_ids`, `src_id`, `trg_id`, `req_ids`, `rule_ids`, `id_rule_ids`, `consumer_id`, `blocks`) chỉ ghi ID của dòng có thật ở một trong hai file. Nhiều ID cách nhau bằng dấu phẩy.

### Liên kết giữa hai file

- Mapping mục 5: `req_ids` trỏ tới BRD mục 5, `rule_ids` trỏ tới BRD mục 7.
- BRD mục 5: `trg_tbl`, `grain` và `key_columns` khớp dòng có cùng `trg_tbl` ở Mapping mục 4.
- BRD mục 6: tập `src_tbl` của một yêu cầu khớp tập `src_tbl` ở Mapping mục 3 của các dòng Mapping mục 5 có `req_ids` chứa yêu cầu đó.
- Hai file lệch nhau thì sửa cho khớp trước khi đặt `READY_FOR_ANALYSIS`. Agent `requirements-analyst` báo mọi chỗ lệch là `CONFLICT`.

### Ràng buộc nền tảng

- Chỉ Eventstream ghi bronze, bằng append. Bronze không sửa, không xoá (`docs/context/01_DATA_MODEL.md §1`, `§2`). Yêu cầu không có bảng đích ở bronze.
- Silver L1 chỉ đưa payload về đúng cấu trúc nguồn và chuyển kiểu theo cấu hình. Silver L1 không có rule nghiệp vụ (`docs/context/01_DATA_MODEL.md §2`).
- Rule nghiệp vụ dùng chung chỉ nằm ở silver L2 (`slv_poi_*`) hoặc bảng `ref_*`. 1 dòng của bảng `ref_*` là 1 rule (`docs/context/01_DATA_MODEL.md §2`, `AGENTS.md §9`).
- Gold phơi dữ liệu và xử lý nghiệp vụ riêng của bảng gold đó: join theo khoá, gom, tính `row_hash`, lọc theo cờ silver, và biến đổi chỉ dùng cho bảng đó. Gold không đọc gold khác (`docs/context/01_DATA_MODEL.md §2`).
- Tiền tố bảng khớp tầng theo bảng "Tiền tố bảng theo tầng".
- `poi_id` không bao giờ chứa ngôn ngữ. Không dùng `poi_uid` (`AGENTS.md §9`).
- Tên cột nghiệp vụ không trùng cột kỹ thuật của tầng (`docs/context/02_NAMING_CONVENTION.md §5.2`).
- Tên notebook theo `docs/context/02_NAMING_CONVENTION.md §2`. Tên pipeline theo `docs/context/02_NAMING_CONVENTION.md §3`.

## 1. Thông tin tài liệu

| field | value |
|---|---|
| `template_id` | `VSVN-BRD-v1` |
| `brd_id` | `BRD-20261012-map-gld-enr-poi-tables` |
| `task_id` | `20261012-map-gld-enr-poi-tables` |
| `mapping_id` | `MAP-20261012-map-gld-enr-poi-tables` |
| `version` | `16` |
| `doc_status` | `READY_FOR_ANALYSIS` |
| `owner_role` | `data-platform` |
| `updated_on` | `2026-10-12` |

## 2. Bối cảnh và mục tiêu

Enrichment service cần ba bảng Delta để đọc dữ liệu POI trước khi chuẩn hóa. Nguồn hiện tại chỉ có tiếng Việt. Luồng này gom dữ liệu tiếng Việt để service tạo thêm ngôn ngữ. Dữ liệu service trả về sau khi enrich là một task khác (`BQ-001`).

Ba bảng giữ schema `lh_vv_gold.enr` và tiền tố `gld_enr_` (`BQ-007`). `poi_id` không chứa ngôn ngữ. Khi một bảng dùng cả hai nguồn, các dòng được append, không join (`BQ-026`). Model cũ chỉ cung cấp nghiệp vụ của `time_to_spend`, `best_time_type`, `best_time_from_month` và `best_time_to_month` (`BQ-028`). `destination_context` dùng cột địa chỉ của model mới.

## 3. Phạm vi

| scope_id | scope | description | evidence_status | context_ref |
|---|---|---|---|---|
| `SCOPE-001` | `IN` | Hợp đồng cột của `gld_enr_poi_info`, `gld_enr_poi_coordinate` và `gld_enr_poi_review` | `USER_STATED` | `USER_INPUT`, `BQ-007` |
| `SCOPE-002` | `IN` | Nguồn tiếng Việt từ partner và 3rd-party, theo công thức đã chốt ở phiên bản 2 | `USER_STATED` | `MQ-006` |
| `SCOPE-003` | `OUT` | Notebook, DDL, pipeline và schema | `USER_STATED` | `USER_INPUT` |
| `SCOPE-004` | `OUT` | Đổi tên ba bảng sang `gld_srv_<chủ đề>_<grain>` | `USER_STATED` | `BQ-007` |
| `SCOPE-005` | `OUT` | Cột `title`, `positive`, `negative`, `response_text` trên `gld_enr_poi_review`, và cột `description` trên `gld_enr_poi_info` | `USER_STATED` | `MQ-003`, `USER_INPUT` |
| `SCOPE-006` | `OUT` | Dữ liệu enrichment service trả về sau khi xử lý xong | `USER_STATED` | `BQ-001` |
| `SCOPE-007` | `OUT` | Suy diễn từ model cũ: bảng `poi_enrichment`, bảng `poi_address_enrichment_staging`, key JSON địa chỉ partner, `vietmap_ward`, `vietmap_province`, và `costVnd` | `USER_STATED` | `BQ-028` |

## 4. Bên sử dụng dữ liệu

| consumer_id | consumer | reads_from | sync_rule | evidence_status | context_ref |
|---|---|---|---|---|---|
| `CSM-001` | Enrichment service, service chuẩn hóa dữ liệu | `lh_vv_gold.enr.gld_enr_poi_info`, `lh_vv_gold.enr.gld_enr_poi_coordinate`, `lh_vv_gold.enr.gld_enr_poi_review` | Ba bảng gold phục vụ enrichment service đọc. Dữ liệu trả về sau enrich thuộc task khác | `USER_STATED` | `BQ-001` |

## 5. Yêu cầu nghiệp vụ

| req_id | priority | statement | consumer_id | trg_tbl | trg_name_status | grain | grain_evidence | key_columns | key_evidence | rule_ids | id_rule_ids | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `BR-001` | `MUST` | `gld_enr_poi_info` ghi bằng `APPEND`. 1 dòng lịch sử là (`poi_id`, `updated_at`). Append khi POI tạo mới hoặc có update. Không có soft delete. Không có `description`. Cột mới của POI partner là NULL. Partner `poi_id` copy từ `slv_pn_poi`. Model cũ chỉ cho nghiệp vụ `time_to_spend` và ba cột `best_time_*` | `CSM-001` | `gld_enr_poi_info` | `PROPOSED` | 1 dòng lịch sử append / (`poi_id`, `updated_at`) | `USER_STATED` | `poi_id`, `updated_at` | `USER_STATED` | `RULE-003`, `RULE-004`, `RULE-006` | `ID-003`, `ID-004` | `MQ-039`, `MQ-040`, `MQ-063` | `[PROPOSED]` |
| `BR-002` | `MUST` | `gld_enr_poi_coordinate` ghi bằng `APPEND`. 1 dòng lịch sử là (`poi_id`, `updated_at`). `destination_name` là chuỗi `coalesce(city, state_province)` từ `slv_3p_poi_address`, partner là NULL. Không có soft delete. Partner `poi_id`, `name`, `short_address`, `ward`, `district`, `province_name` copy từ `slv_pn_poi` | `CSM-001` | `gld_enr_poi_coordinate` | `PROPOSED` | 1 dòng lịch sử append / (`poi_id`, `updated_at`) | `USER_STATED` | `poi_id`, `updated_at` | `USER_STATED` | `RULE-005` | `ID-003`, `ID-004` | `MQ-039`, `MQ-050`, `MQ-063` | `[PROPOSED]` |
| `BR-003` | `MUST` | `gld_enr_poi_review` ghi bằng `APPEND`. 1 dòng lịch sử là (`review_id`, `updated_at`). Chỉ nguồn 3rd-party, không có partner. Không có `source_review_id`. `review_id` copy `slv_3p_poi_review.review_id`, không hash. `review_text` lấy `text`. `review_date` và `review_updated_at` cast `time` sang `timestamp` | `CSM-001` | `gld_enr_poi_review` | `PROPOSED` | 1 dòng lịch sử append / (`review_id`, `updated_at`) | `USER_STATED` | `review_id`, `updated_at` | `USER_STATED` | | `ID-003` | `MQ-039`, `MQ-045`, `MQ-062` | `[PROPOSED]` |

## 6. Nguồn dữ liệu

| ds_id | req_ids | layer | lakehouse_schema | src_tbl | src_columns | name_status | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|
| `DS-001` | `BR-001`, `BR-002` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi` | `poi_id`, `poi_name`, `types_json`, `business_sector`, `business_category`, `source_name`, `source_id` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Gold copy `poi_id` 3rd-party từ đây. Bảng review không đọc bảng này |
| `DS-002` | | `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_business_services` | `id`, `name`, `address` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §5.1`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS` | Đầu vào của `slv_pn_poi`. `id` là `business_service_id`. Gold không đọc bảng này |
| `DS-003` | | `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_business_service_i18ns` | `name`, `locale` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §5.1`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS` | Đầu vào `name` của `slv_pn_poi`. Gold không đọc bảng này |
| `DS-013` | `BR-001`, `BR-002` | `silver_l2` | `lh_vv_silver.dbo` | `slv_pn_poi` | `poi_id`, `business_service_id`, `name`, `short_address`, `ward`, `district`, `province_name` | `PROPOSED` | `USER_STATED` | `MQ-063` | `[PROPOSED]` 1 dòng / `poi_id`. Gold info copy `poi_id`. Gold coordinate copy `poi_id`, `name`, `short_address`, `ward`, `district`, `province_name` |
| `DS-005` | `BR-001`, `BR-002` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_address` | `short_address`, `address_viet_map`, `ward`, `district`, `city`, `state_province`, `lat`, `lng` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §4`, `§5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | `destination_name` là `coalesce(city, state_province)`. `destination_context` dùng `short_address`, `district`, `city` |
| `DS-007` | `BR-001`, `BR-003` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_review` | `review_id`, `poi_id`, `text`, `time`, `published_at`, `rating` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | `review_id` của bảng review copy cột này, không hash. `review_json` sắp `time` giảm, tối đa 20, `review_text` cắt 350 ký tự |
| `DS-009` | `BR-001` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_contact` | `website_url` | `EXISTING` | `CONTEXT_STATED` | `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | |
| `DS-010` | `BR-001` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_rating` | `rating_overall`, `rating_count` | `EXISTING` | `CONTEXT_STATED` | `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Cột đích `rating` lấy `rating_overall`. `userRatingCount` lấy `rating_count` |
| `DS-011` | `BR-001` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_price` | `price_level` | `EXISTING` | `CONTEXT_STATED` | `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | |
| `DS-012` | `BR-001` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_opening_hours` | `periods_json` | `EXISTING` | `CONTEXT_STATED` | `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Copy 1:1 sang `opening_hours_text` |

## 7. Rule nghiệp vụ

| rule_id | statement | evidence_status | layer | rule_home | rule_home_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|
| `RULE-001` | Rule nghiệp vụ của POI nằm ở silver L2 hoặc `ref_*`. Gold chỉ đồng bộ và phơi dữ liệu | `CONTEXT_STATED` | `silver_l2` | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` | `USER_STATED` | | `docs/context/01_DATA_MODEL.md §2`, `MQ-054` | Người dùng chốt không có bảng rule riêng. Ba bảng đích không đọc `ref_*` |
| `RULE-003` | `duration_label` theo `slv_3p_poi.business_sector`: accommodation Thời gian lưu trú lý tưởng; f_n_b Thời gian dùng bữa; attraction Thời gian tham quan; tour_n_activities Thời lượng hoạt động; shopping_n_retail Thời gian mua sắm; transport_route_base Thời gian đưa đón; transport_on_demand Thời gian thuê phổ biến; vehicle_rental Thời gian thuê phổ biến; spa_n_wellness Thời lượng liệu trình; event Thời lượng chương trình; else Thời lượng trải nghiệm. `best_time_label`: accommodation Mùa lưu trú đẹp nhất; f_n_b Thời điểm nên ghé; attraction Mùa đẹp nhất; tour_n_activities Thời điểm phù hợp; shopping_n_retail Thời điểm nên ghé; transport_route_base Thời điểm phù hợp; transport_on_demand Thời điểm nên thuê; vehicle_rental Thời điểm nên thuê; spa_n_wellness Thời điểm phù hợp; event Thời điểm nên xem; else Thời điểm phù hợp. `cost_label`: accommodation Giá phòng tham khảo; f_n_b Mức giá tham khảo; attraction Chi phí tham quan; tour_n_activities Chi phí tham khảo; shopping_n_retail Chi tiêu tham khảo; transport_route_base Chi phí đưa đón; transport_on_demand Giá thuê tham khảo; vehicle_rental Giá thuê tham khảo; spa_n_wellness Giá dịch vụ tham khảo; event Giá vé tham khảo; else Chi phí tham khảo | `USER_STATED` | `silver_l2` | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` | `USER_STATED` | | `MQ-041`, `MQ-054` | Không có bảng rule riêng |
| `RULE-006` | `review_json` là JSON array, sắp `time` giảm, tối đa 20 phần tử. `review_text` cắt 350 ký tự. Mỗi phần tử có `review_id`, `review_text`, `time`, `published_at`. Không có Title, Positive, Negative | `USER_STATED` | `silver_l2` | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` | `USER_STATED` | | `MQ-053`, `MQ-054` | Không có bảng rule riêng. POI partner thì NULL |
| `RULE-004` | `subcategory_tags` của 3rd-party lấy `types_json`. Partner là NULL | `USER_STATED` | `silver_l2` | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` | `USER_STATED` | | `MQ-012`, `MQ-054`, `BQ-016` | Không có bảng rule riêng |
| `RULE-005` | `lat` và `lng` của partner là NULL. 3rd-party lấy `lat` và `lng` | `USER_STATED` | `silver_l2` | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` | `USER_STATED` | | `MQ-019`, `MQ-054`, `BQ-016` | Không có bảng rule riêng |

## 8. Định danh

| id_rule_id | identifier | formula | applies_to | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|
| `ID-003` | `poi_id` (3rd-party) | `uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`) | Dòng 3rd-party của `gld_enr_poi_info`, `gld_enr_poi_coordinate`, và `slv_3p_poi_*` | `CONTEXT_STATED, USER_STATED` | `MQ-006`, `MQ-062`, `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §8` | Không có ngôn ngữ. Bảng review copy `slv_3p_poi_review.poi_id`, không hash lại |
| `ID-004` | `poi_id` (partner) | `uuid_format(md5('partner_portal' ‖ business_service_id))` | `slv_pn_poi` | `CONTEXT_STATED, USER_STATED` | `MQ-006`, `MQ-063`, `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §8` | Không có ngôn ngữ. Tính ở silver. Gold info và coordinate chỉ copy `poi_id`. Bảng review không có partner |

## 9. Yêu cầu phi chức năng

| nfr_id | item | value | evidence_status | context_ref | note |
|---|---|---|---|---|---|
| `NFR-001` | Nhịp ghi ba bảng `gld_enr_*` | Mỗi 15 phút một lần | `USER_STATED` | `MQ-028`, `MQ-040`, `MQ-044` | Pipeline `PL_VV_TRANS_SLV_TO_ENR_15P`. Orchestrator `NB_00_ORCHES_SLV_TO_ENR_15P`, clone từ `NB_00_ORCHES_SLV_TO_GLD`. Notebook node: `NB_ENR_POI_INFO`, `NB_ENR_POI_COORDINATE`, `NB_ENR_POI_REVIEW`. `load_mode` là `APPEND` |

## 10. Tiêu chí nghiệm thu

| ac_id | req_ids | criterion | how_to_check | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|
| `AC-001` | `BR-001`, `BR-002`, `BR-003` | Mapping có các cột info từ `COL-001`, `COL-003` đến `COL-010`, `COL-035` đến `COL-048`, 11 cột coordinate và 8 cột review. Không còn `description` trên info và không còn `source_review_id` trên review | Đếm dòng mục 5 và đối chiếu `BR-001` | `USER_STATED` | `MQ-062` | |
| `AC-002` | `BR-003` | `review_id` copy `slv_3p_poi_review.review_id`. Không có `source_review_id` | Đọc Mapping `COL-022` và câu trả lời `MQ-062` | `USER_STATED` | `MQ-062` | |
| `AC-003` | `BR-001`, `BR-002` | `poi_id` 3rd-party và partner không chứa ngôn ngữ, theo `ID-003` và `ID-004` | Đọc Mapping `COL-001` | `USER_STATED` | `MQ-006` | |
| `AC-004` | `BR-003` | `rating` là số trên thang 5 sao, kiểu `decimal(3,1)` | Đọc Mapping `COL-025` và câu trả lời `MQ-051` | `USER_STATED` | `MQ-051` | |

## 11. Mục thiếu evidence

| gap_id | blocks | missing_fact | why_repo_cannot_answer | resolution_type | pass_fail_criterion | note |
|---|---|---|---|---|---|---|

Không còn mục thiếu evidence mở. `BGAP-005` đến `BGAP-008` đã được trả lời ở mục 13.

## 12. Mâu thuẫn trong repository

| conflict_id | blocks | item | source_a | source_b | note |
|---|---|---|---|---|---|

Không còn mâu thuẫn mở. `BCONF-007` chốt fallback `state_province`. `BCONF-008` chốt tên đích `rating` lấy từ `rating_overall`.

## 13. Câu hỏi mở

| q_id | blocks | question | resolution_type | answer | answered_on |
|---|---|---|---|---|---|
| `BQ-001` | `CSM-001`, `SCOPE-006` | Enrichment service dùng ba bảng thế nào? | `USER_ANSWER` | Luồng này chuẩn hóa dữ liệu ra 3 bảng gold để enrichment service đọc. Dữ liệu service trả về là task khác. | `2026-10-12` |
| `BQ-002` | `BR-001`, `BR-002`, `BR-003` | Grain và khoá của từng bảng là gì? | `USER_ANSWER` | Info và coordinate: `poi_id`. Review: `review_id`. | `2026-10-12` |
| `BQ-005` | `NFR-001` | Nhịp của ba bảng là gì? | `USER_ANSWER` | 15 phút một lần, orchestrator `NB_00_ORCHES_SLV_TO_GLD`. | `2026-10-12` |
| `BQ-007` | `SCOPE-001`, `SCOPE-004` | Giữ `lh_vv_gold.enr` và `gld_enr_` hay đổi tên? | `USER_ANSWER` | Giữ `lh_vv_gold.enr` và `gld_enr_`. | `2026-10-12` |
| `BQ-008` | `ID-003`, `ID-004` | `poi_id` dùng công thức nào? | `USER_ANSWER` | 3rd-party không ngôn ngữ và partner không ngôn ngữ, theo model mới. Nguồn chỉ có tiếng Việt. | `2026-10-12` |
| `BQ-009` | `BR-003` | `review_id` dùng công thức nào? | `USER_ANSWER` | Câu này bị thay bởi `BQ-029`: copy `slv_3p_poi_review.review_id`, không hash. | `2026-10-12` |
| `BQ-010` | `BR-003` | `source_review_id` là gì? | `USER_ANSWER` | Câu này bị thay bởi `BQ-029`: bỏ cột `source_review_id`. | `2026-10-12` |
| `BQ-011` | `COL-009` | `created_at` và `updated_at` theo câu nào trong hai câu đã ghi? | `USER_ANSWER` | Đổi mỗi lần ghi. | `2026-10-12` |
| `BQ-012` | `COL-013` | Partner lấy `short_address` từ `full_address` hay `street`? | `USER_ANSWER` | `address.full_address`. | `2026-10-12` |
| `BQ-013` | `COL-016` | 3rd-party lấy `province_name` từ `city` hay `state_province`? | `USER_ANSWER` | `city`. | `2026-10-12` |
| `BQ-014` | `COL-031` | `review_date` là `timestamp` hay `date`? | `USER_ANSWER` | Giữ `timestamp`. | `2026-10-12` |
| `BQ-015` | `FLOW-002` | `Append` có được giữ, hay đổi thành giá trị `load_mode` trong quy ước? | `USER_ANSWER` | Giữ tên `APPEND`. Có dữ liệu mới thì append, không merge kể cả khi key đã tồn tại. | `2026-10-12` |
| `BQ-016` | `RULE-001` | Rule đã chốt nằm ở bảng silver L2 hoặc `ref_*` nào? | `USER_ANSWER` | Ba bảng đích không dùng bảng `ref`. | `2026-10-12` |
| `BQ-017` | `COL-017` | Grain và khoá của `destination_ward_mapping` là gì? | `USER_ANSWER` | Ba bảng đích không dùng `destination_ward_mapping`. | `2026-10-12` |
| `BQ-018` | `BR-001`, `BR-002`, `BR-003` | `APPEND` không merge khi key đã có. Bảng vẫn là 1 dòng / key, hay được nhiều dòng cùng key? | `USER_ANSWER` | Được nhiều dòng cùng `poi_id` hoặc `review_id`. | `2026-10-12` |
| `BQ-019` | `COL-017`, `COL-042` | `destination_name` lấy từ cột nguồn nào, hay bỏ cột này? | `USER_ANSWER` | `city`, fallback `province_name`. | `2026-10-12` |
| `BQ-020` | `COL-017`, `COL-042` | Fallback dùng `state_province` hay một cột tên `province_name`? | `USER_ANSWER` | Dùng `slv_3p_poi_address.state_province`. | `2026-10-12` |
| `BQ-021` | `COL-044` | `rating` của bảng info lấy `rating_overall` hay cột `rating`? | `USER_ANSWER` | Tên đích giữ `rating`. Nguồn là `slv_3p_poi_rating.rating_overall`. | `2026-10-12` |
| `BQ-022` | `COL-043`, `COL-047`, `COL-048` | `{address}`, `{province}`, text giờ mở cửa, `Title`, `Positive`, `Negative` và cột sắp review lấy từ đâu? | `USER_ANSWER` | `destination_context` dùng `short_address`, `district`, `city` và `destination_name`. `opening_hours_text` copy 1:1 từ `periods_json`. Dòng review không cần Title, Positive, Negative. | `2026-10-12` |
| `BQ-023` | `COL-035` | Các cột mới của `gld_enr_poi_info` với dòng partner là NULL hay có nguồn riêng? | `USER_ANSWER` | Không lấy partner. POI partner thì NULL. | `2026-10-12` |
| `BQ-024` | `DS-003`, `DS-007` | Có probe schema và dữ liệu của model cũ không? | `USER_ANSWER` | Không. Model cũ chỉ cung cấp nghiệp vụ bốn trường ở `BQ-028`. | `2026-10-12` |
| `BQ-025` | `BR-003`, `COL-027` | Cột chữ review trên `gld_enr_poi_review` tên gì và lấy từ đâu? | `USER_ANSWER` | Giữ tên `review_text`. Lấy từ `slv_3p_poi_review.text`. | `2026-10-12` |
| `BQ-026` | `BR-001`, `BR-002`, `BR-003` | Khi một bảng đích dùng cả partner và 3rd-party thì hai nguồn join hay append? | `USER_ANSWER` | Append, không join. `source_id` luôn có trên dòng của từng nguồn. Bỏ luật bắt buộc phải có `src_id`. | `2026-10-12` |
| `BQ-027` | `BR-002`, `COL-014`, `COL-016` | Ba bảng `gld_enr_*` có đọc `poi_address_enrichment_staging` không? | `USER_ANSWER` | Không. Bảng đó không thuộc model mới của task này. Nó bị suy ra từ notebook cũ. | `2026-10-12` |
| `BQ-028` | `SCOPE-007`, `BR-001`, `BR-002`, `COL-003`, `COL-004`, `COL-005`, `COL-006`, `COL-007`, `COL-043` | Model cũ còn được dùng cho trường nào? | `USER_ANSWER` | Chỉ nghiệp vụ của `time_to_spend`, `best_time_type`, `best_time_from_month`, `best_time_to_month`. `destination_context` dùng cột địa chỉ của model mới. | `2026-10-12` |
| `BQ-029` | `BR-003`, `COL-022` | `gld_enr_poi_review` lấy `review_id` từ đâu, và còn `source_review_id` không? | `USER_ANSWER` | Chỉ 3rd-party, không có partner. Bỏ `source_review_id`. `review_id` copy `slv_3p_poi_review.review_id`, không hash. | `2026-10-12` |
| `BQ-030` | `DS-013`, `ID-004`, `COL-001`, `COL-011` | `poi_id` partner tính ở đâu, bảng silver tên gì? | `USER_ANSWER` | Tính ở silver. Bảng tên `slv_pn_poi`. Gold info và coordinate chỉ copy. | `2026-10-12` |
