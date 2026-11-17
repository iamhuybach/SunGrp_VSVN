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
| `evidence_status`, `*_evidence` | `USER_STATED` | Người dùng hoặc chủ nghiệp vụ đặt ra giá trị. `context_ref` ghi `USER_INPUT` khi giá trị nêu ngay trong tài liệu, hoặc ghi `q_id` của câu hỏi đã có `answer` và `answered_on`. Chỉ dùng cho yêu cầu và quyết định: câu yêu cầu, phạm vi, mức ưu tiên, rule mới, giá trị phi chức năng, tên `PROPOSED`, grain và khoá của bảng `PROPOSED`, nơi đặt rule mới. Không dùng cho sự kiện về đối tượng `EXISTING`: cột, grain, khoá, kiểu dữ liệu, độ duy nhất, tỉ lệ NULL, định dạng, giá trị enum, rule hoặc công thức đã có. Các sự kiện đó cần `CONTEXT_STATED` hoặc `TASK_EVIDENCE` (`docs/agent-system/WORKFLOW.md §5`, `AGENTS.md §6`) |
| `evidence_status`, `*_evidence` | `MISSING_EVIDENCE` | Chưa có nguồn hợp lệ, hoặc nguồn có ghi giá trị nhưng nói rõ là chưa xác nhận. Cần 1 dòng ở mục thiếu evidence của cùng file, có `blocks` chứa ID của dòng |
| `evidence_status`, `*_evidence` | `CONFLICT` | Hai nguồn trong repository nói khác nhau. Cần 1 dòng ở mục mâu thuẫn và 1 câu hỏi ở mục câu hỏi mở của cùng file |
| `evidence_status`, `*_evidence` | Nhiều giá trị | Được ghi nhiều giá trị trong `CONTEXT_STATED`, `TASK_EVIDENCE`, `USER_STATED`, cách nhau bằng dấu phẩy, khi giá trị dựa trên nhiều loại nguồn. `MISSING_EVIDENCE` và `CONFLICT` luôn đứng một mình |
| `name_status`, `trg_name_status` | `EXISTING` | Tên đã có trong repository. `context_ref` chỉ nơi nêu tên |
| `name_status`, `trg_name_status` | `PROPOSED` | Tên mới chưa có trong repository. Ghi nhãn `[PROPOSED]` ở `note` (`docs/context/02_NAMING_CONVENTION.md`, phần đầu file) |
| `layer` | `bronze`, `silver_l1`, `silver_l2`, `ref`, `gold`, `ctrl` | Tầng theo `docs/context/01_DATA_MODEL.md §2` |
| `resolution_type` | `REPO_READ` | Đọc thêm file trong repository |
| `resolution_type` | `PROBE` | Probe chỉ đọc trên Fabric DEV. Main viết probe, người dùng chạy (`AGENTS.md §6`). Ghi tiêu chí đạt và không đạt bằng lời, không viết code |
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
| `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_` cho partner (`slv_pn_<bảng Postgres>`). `slv_3p_` cho 3rd-party (`slv_3p_poi` và `slv_3p_poi_<khối>`). `slv_pm_` `[PROPOSED]` cho POI management | `AGENTS.md §7`, `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `ref` | `lh_vv_silver.dbo` | `ref_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `gold` | `lh_vv_gold.dbo` | `gld_`. Bảng phục vụ đặt tên `gld_srv_<chủ đề>_<grain>` | `AGENTS.md §7`, `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `ctrl` | `lh_vv_ctrl.dbo` | `ctrl_mng_`, `ctrl_cfg_`, `ctrl_log_`, `ctrl_cdc_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |

Bảng cũ không theo tiền tố trên, như `poi_master`, `destination_ward_mapping`, bảng `poi_*` cũ ở silver và `lh_vv_bronze.partner.*`, giữ nguyên tới cutover (`docs/context/01_DATA_MODEL.md §1`, `docs/context/02_NAMING_CONVENTION.md §1`). Yêu cầu có bảng đích là bảng cũ cần 1 câu hỏi cho người dùng.

### Định danh

| ID | Dạng | Ghi ở |
|---|---|---|
| `task_id` | Tên thư mục `.ai/tasks/<task_id>/`, dạng `YYYYMMDD-slug` (`docs/agent-system/WORKFLOW.md §4`) | Mục 1 của cả hai file |
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
- Rule nghiệp vụ dùng chung chỉ nằm ở silver L2 (`slv_poi_*`) hoặc bảng `ref_*`. 1 dòng của bảng `ref_*` là 1 rule (`docs/context/01_DATA_MODEL.md §2`, `AGENTS.md §7`).
- Gold phơi dữ liệu và xử lý nghiệp vụ riêng của bảng gold đó: join theo khoá, gom, tính `row_hash`, lọc theo cờ silver, và biến đổi chỉ dùng cho bảng đó. Gold không đọc gold khác (`docs/context/01_DATA_MODEL.md §2`).
- Tiền tố bảng khớp tầng theo bảng "Tiền tố bảng theo tầng".
- `poi_id` không bao giờ chứa ngôn ngữ. Không dùng `poi_uid` (`AGENTS.md §7`).
- Tên cột nghiệp vụ không trùng cột kỹ thuật của tầng (`docs/context/02_NAMING_CONVENTION.md §5.2`).
- Tên notebook theo `docs/context/02_NAMING_CONVENTION.md §2`. Tên pipeline theo `docs/context/02_NAMING_CONVENTION.md §3`.
## 1. Thông tin tài liệu

| field | value |
|---|---|
| `template_id` | `VSVN-BRD-v1` |
| `brd_id` | `BRD-20261116-enr-lang-destination-from-bronze` |
| `task_id` | `20261116-enr-lang-destination-from-bronze` |
| `mapping_id` | `MAP-20261116-enr-lang-destination-from-bronze` |
| `version` | `5` |
| `doc_status` | `READY_FOR_ANALYSIS` |
| `owner_role` | `data-platform` |
| `updated_on` | `2026-11-16` |

## 2. Bối cảnh và mục tiêu

Serving cần bản đa ngôn ngữ và địa chỉ chuẩn từ sự kiện enrich trên bronze. `event_type = LANG` đổ vào `slv_enr_poi_info_multi_lang`. `event_type = DESTINATION` đổ vào `slv_enr_poi_destination`. Cột `cost_vnd` của multi_lang đổi thành `cost` trên silver, gold, PostgreSQL và API. `gld_srv_poi_info` lấy `street` từ entity và ghép `full_address` theo ba mức ưu tiên.

## 3. Phạm vi

| scope_id | scope | description | evidence_status | context_ref |
|---|---|---|---|---|
| `SCOPE-001` | `IN` | Extract `slv_enr_poi_info_multi_lang` từ `event_type = LANG` của `brz_enrichment_result` | `USER_STATED` | `USER_INPUT` |
| `SCOPE-002` | `IN` | Extract `slv_enr_poi_destination` từ `event_type = DESTINATION`, bỏ `street` | `USER_STATED` | `USER_INPUT` |
| `SCOPE-003` | `IN` | Đổi `cost_vnd` thành `cost` trên `slv_enr_poi_info_multi_lang`, `gld_srv_poi_multi_lang`, `apps.srv_poi_multi_lang` và mọi chỗ API đọc `cost_vnd` của multi_lang | `USER_STATED` | `USER_INPUT` |
| `SCOPE-004` | `IN` | `gld_srv_poi_info.street` lấy từ `slv_poi_entity_non_enrich.street`. `full_address` ghép theo ba mức ưu tiên | `USER_STATED` | `USER_INPUT` |
| `SCOPE-005` | `IN` | Cập nhật `docs/context/mapping_gld_srv_poi_info.md` và `docs/context/mapping_gld_srv_poi_multi_lang.md` trong cùng task trước review | `USER_STATED` | `USER_INPUT` |
| `SCOPE-006` | `OUT` | Bảng hoặc notebook khác còn `cost_vnd` hoặc `street` mà yêu cầu không nêu, gồm `gld_enr_poi_info`, `slv_poi_entity_non_enrich.street`, và `(ood).general-information.md` | `USER_STATED` | `USER_INPUT` |
| `SCOPE-007` | `IN` | `docs/context/api-mapping/practical_info.md`: `data.cost` đọc `cost` thay cho `cost_vnd` | `USER_STATED` | `USER_INPUT` |

## 4. Bên sử dụng dữ liệu

| consumer_id | consumer | reads_from | sync_rule | evidence_status | context_ref |
|---|---|---|---|---|---|
| `CSM-001` | API serving POI | `apps.srv_poi_multi_lang` | API đọc cột `cost` thay cho `cost_vnd`. Repo không có Flyway. Đồng bộ gold sang PostgreSQL theo hợp đồng bảng `gld_srv_poi_*` | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `AGENTS.md §7`, `sql/postgres/gld_srv_serve.pg.sql` |

## 5. Yêu cầu nghiệp vụ

| req_id | priority | statement | consumer_id | trg_tbl | trg_name_status | grain | grain_evidence | key_columns | key_evidence | rule_ids | id_rule_ids | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `BR-001` | `MUST` | `slv_enr_poi_info_multi_lang` chỉ nhận `event_type = LANG`. Cột theo path đã chốt. `cost`, `best_time`, `time_to_spend` giữ object `{text, label}` dạng chuỗi JSON. Mảng `data.experiences` ghi vào cột `experience` | | `slv_enr_poi_info_multi_lang` | `EXISTING` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | | | `USER_INPUT`, `docs/context/mapping_gld_srv_poi_multi_lang.md §2` | |
| `BR-002` | `MUST` | `slv_enr_poi_destination` chỉ nhận `event_type = DESTINATION`. `destination` là chuỗi JSON của cả mảng. `destination_id` và `destination_name` cùng thứ tự phần tử. `country_code` và `postal_code` null. Bỏ `street` | | `slv_enr_poi_destination` | `EXISTING` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | | | `USER_INPUT`, `docs/context/mapping_gld_srv_poi_info.md §1.6` | |
| `BR-003` | `MUST` | `gld_srv_poi_multi_lang.cost_vnd` đổi thành `cost`. P1 copy từ silver, P2 null. `apps.srv_poi_multi_lang.cost_vnd` đổi thành `cost` và giữ PostgreSQL `text`. API và `practical_info.md` đọc `cost` | `CSM-001` | `gld_srv_poi_multi_lang` | `EXISTING` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | | | `USER_INPUT`, `docs/context/mapping_gld_srv_poi_multi_lang.md §1.1`, `§2` | Không có dòng Mapping cho bảng PostgreSQL |
| `BR-004` | `MUST` | `slv_enr_poi_info_multi_lang.cost_vnd` đổi thành `cost` | | `slv_enr_poi_info_multi_lang` | `EXISTING` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | | | `USER_INPUT`, `docs/context/mapping_gld_srv_poi_multi_lang.md §2` | Cột map ở `COL-004` |
| `BR-005` | `MUST` | `gld_srv_poi_info.street` lấy từ `slv_poi_entity_non_enrich.street` | | `gld_srv_poi_info` | `EXISTING` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | | | `USER_INPUT`, `docs/context/mapping_gld_srv_poi_info.md §1.1` | |
| `BR-006` | `MUST` | `gld_srv_poi_info.full_address` ghép bằng `, `. Một field null, hoặc `house_number` hay `street` chỉ còn khoảng trắng sau trim, thì bỏ cả nhóm. Ba nhóm chỉ khi có dòng destination; không có thì giữ `full_address` của entity. Nhóm 1: `house_number` + `street` + `formatted_address`. Nhóm 2: `house_number` + `street` + `ward_with_type` + `city_with_type`. Nhóm 3: `slv_enr_poi_destination.full_address` | | `gld_srv_poi_info` | `EXISTING` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | | | `USER_INPUT`, `docs/context/mapping_gld_srv_poi_info.md §1.1`, `§1.6` | |

## 6. Nguồn dữ liệu

| ds_id | req_ids | layer | lakehouse_schema | src_tbl | src_columns | name_status | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|
| `DS-001` | `BR-001`, `BR-003`, `BR-004` | `bronze` | `lh_vv_bronze.dbo` | `brz_enrichment_result` | `poi_id`, `source`, `lang`, `data` | `PROPOSED` | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | `[PROPOSED]` Schema probe: các cột này có thật |
| `DS-002` | `BR-002` | `bronze` | `lh_vv_bronze.dbo` | `brz_enrichment_result` | `poi_id`, `source`, `data` | `PROPOSED` | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | `[PROPOSED]` |
| `DS-003` | `BR-003` | `silver_l1` | `lh_vv_silver.dbo` | `slv_enr_poi_info_multi_lang` | `cost` | `EXISTING` | `USER_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | Cột hiện tại tên `cost_vnd` |
| `DS-004` | `BR-005`, `BR-006` | `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_entity_non_enrich` | `street`, `house_number` | `EXISTING` | `CONTEXT_STATED`, `USER_STATED` | `USER_INPUT`, `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` `ADDRESS_COLS`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | `house_number` và `street` là STRING trong `TABLE_SPECS` |
| `DS-005` | `BR-006` | `silver_l1` | `lh_vv_silver.dbo` | `slv_enr_poi_destination` | `formatted_address`, `ward_with_type`, `city_with_type`, `full_address` | `EXISTING` | `CONTEXT_STATED`, `USER_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | `full_address` có trong `TABLE_SPECS`. Ba cột kia là cột mới STRING |

## 7. Rule nghiệp vụ

| rule_id | statement | evidence_status | layer | rule_home | rule_home_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|

## 8. Định danh

| id_rule_id | identifier | formula | applies_to | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|

## 9. Yêu cầu phi chức năng

| nfr_id | item | value | evidence_status | context_ref | note |
|---|---|---|---|---|---|

## 10. Tiêu chí nghiệm thu

| ac_id | req_ids | criterion | how_to_check | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|
| `AC-001` | `BR-001` | Silver multi_lang chỉ có dòng LANG. `cost`, `best_time`, `time_to_spend` là object khóa `text` và `label`. `experience` là mảng từ `data.experiences` | Đối chiếu `probe_json_shape.txt` và `probe_json_shape_rest.txt` | `TASK_EVIDENCE` | `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape.txt`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape_rest.txt` | 360/360 object và mảng |
| `AC-002` | `BR-002` | Silver destination chỉ có dòng DESTINATION, không còn `street`. `destination` là chuỗi JSON mảng. `destination_id` và `destination_name` cùng thứ tự, kể cả 1 phần tử null | Đối chiếu `probe_json_shape_rest.txt` | `TASK_EVIDENCE` | `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape_rest.txt` | 113 mảng, 271 phần tử, 1 id và 1 name null |
| `AC-003` | `BR-003`, `BR-004` | `cost_vnd` thành `cost` trên silver, gold, `apps.srv_poi_multi_lang` (giữ `text`), API, và `practical_info.md` | Rà DDL, entity, DTO, service, test, và file mapping API | `USER_STATED` | `USER_INPUT` | |
| `AC-004` | `BR-005`, `BR-006` | `gld_srv_poi_info.street` từ entity. `full_address` đúng ba mức ưu tiên và dấu `, ` | Đối chiếu notebook gold | `USER_STATED` | `USER_INPUT` | |
| `AC-005` | `BR-003`, `BR-005`, `BR-006` | Hai file mapping context được cập nhật trong cùng task trước review | Đọc hai file `docs/context/mapping_gld_srv_poi_*.md` | `USER_STATED` | `USER_INPUT` | |

## 11. Mục thiếu evidence

| gap_id | blocks | missing_fact | why_repo_cannot_answer | resolution_type | pass_fail_criterion | note |
|---|---|---|---|---|---|---|

## 12. Mâu thuẫn trong repository

| conflict_id | blocks | item | source_a | source_b | note |
|---|---|---|---|---|---|

## 13. Câu hỏi mở

| q_id | blocks | question | resolution_type | answer | answered_on |
|---|---|---|---|---|---|
