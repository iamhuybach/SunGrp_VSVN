# Mẫu Mapping nguồn → đích (VSVN)

> `template_id`: `VSVN-MAPPING-v1`. Mẫu này đi cùng `docs/templates/BRD_TEMPLATE.md` (`VSVN-BRD-v1`). Agent `requirements-analyst` (`.claude/agents/requirements-analyst.md`) đọc file đã điền theo đúng tên mục, tên cột và giá trị cho phép của mẫu này.
> Phần mô tả viết bằng tiếng Việt. Tên trường, tên bảng, tên cột, giá trị trạng thái và định danh giữ bằng tiếng Anh.
> Dòng có nhãn `[EXAMPLE]` chỉ minh hoạ cách điền. Đó không phải dữ liệu production và không phải yêu cầu thật. Mọi giá trị trong dòng `[EXAMPLE]` có nguồn ở `context_ref`, hoặc để trống và đặt `MISSING_EVIDENCE`.
> Không ghi dữ liệu cá nhân, secret, token hoặc trích xuất dữ liệu production vào file này.

## Cách điền

1. Sao chép mẫu thành `docs/requirements/<task_id>/MAPPING.md`. Mỗi task có đúng 1 file Mapping và 1 file Business Requirements Document (BRD). Không lưu bản đã điền trong `.ai/tasks/`, vì task artifact ở đó phải viết bằng tiếng Anh (`AGENTS.md §1`).
2. Giữ nguyên mục "Quy ước dùng chung", tên mục, tên cột và thứ tự cột. Không xoá cột. Ô không dùng thì để trống.
3. Xoá mọi dòng `[EXAMPLE]` trước khi đặt `doc_status` là `READY_FOR_ANALYSIS`. Agent bỏ qua dòng `[EXAMPLE]` còn sót và báo lại.
4. Chỉ ghi một giá trị khi có nguồn hợp lệ theo `evidence_status` ở mục "Quy ước dùng chung". Ghi nguồn vào `context_ref`.
5. Khi chưa có nguồn: để trống ô, đặt `MISSING_EVIDENCE` và thêm 1 dòng ở mục 6 có `blocks` chứa ID của dòng đó. Nguồn có ghi giá trị nhưng nói rõ là chưa xác nhận: được ghi giá trị đó, đặt `MISSING_EVIDENCE` và nêu lý do ở `note`. Không đoán tên bảng, tên cột, kiểu dữ liệu, khoá, grain, giá trị enum, công thức hoặc rule.
6. Dòng ở mục 6 có `resolution_type` là `USER_ANSWER` hoặc `EXTERNAL` cần ít nhất 1 câu hỏi ở mục 8 có `blocks` chứa `gap_id` đó.
7. Hai nguồn trong repository nói khác nhau: không tự chọn. Đặt `CONFLICT`, thêm 1 dòng ở mục 7 và 1 câu hỏi ở mục 8 có `blocks` chứa `conflict_id` đó (`docs/context/00_README.md`, mục "Quy tắc khi làm việc với bộ này").
8. Tên mới chưa có trong repository: đặt `name_status` là `PROPOSED` và ghi nhãn `[PROPOSED]` ở `note`. Tên bảng mới phải đúng tiền tố của tầng ở mục "Quy ước dùng chung".
9. Không ghi tên notebook mới ở mục 2 khi `grain_evidence` hoặc `key_evidence` của bảng đích liên quan ở mục 4 là `MISSING_EVIDENCE` hoặc `CONFLICT`.
10. Khi có câu trả lời: ghi `answer` và `answered_on` ở mục 8, sửa ô liên quan theo luật của `evidence_status`, rồi tăng `version`.

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
| `template_id` | `VSVN-MAPPING-v1` |
| `mapping_id` | `MAP-20261012-map-gld-enr-poi-tables` |
| `task_id` | `20261012-map-gld-enr-poi-tables` |
| `brd_id` | `BRD-20261012-map-gld-enr-poi-tables` |
| `version` | `18` |
| `doc_status` | `READY_FOR_ANALYSIS` |
| `owner_role` | `data-platform` |
| `updated_on` | `2026-10-12` |

## 2. Luồng xử lý

> Nguồn hiện tại chỉ có tiếng Việt. Luồng này chuẩn bị dữ liệu để enrichment service tạo thêm ngôn ngữ. Dữ liệu service trả về là task khác (`MQ-002`).

| flow_id | trg_ids | field | value | name_status | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|
| `FLOW-001` | `TRG-001`, `TRG-002`, `TRG-003` | `pl_name` | `PL_VV_TRANS_SLV_TO_ENR_15P` | `PROPOSED` | `USER_STATED` | `MQ-028` | `[PROPOSED]` Quy ước pipeline là `PL_VV_TRANSFORM_...` và hậu tố nhịp `_15M`. Giữ đúng tên người dùng nêu |
| `FLOW-002` | `TRG-001`, `TRG-002`, `TRG-003` | `load_mode` | `APPEND` | | `USER_STATED` | `MQ-027`, `MQ-047`, `MQ-058` | Mọi thay đổi đều là POI có update. Append khi POI tạo mới và khi POI có update. Partner và 3rd-party append thành các dòng riêng, không join. Không merge theo khoá. Không có soft delete. `src_id` trên dòng mapping không bắt buộc. `docs/context/02_NAMING_CONVENTION.md §6` không có giá trị `APPEND`. Người dùng giữ tên này |
| `FLOW-003` | `TRG-001`, `TRG-002`, `TRG-003` | `orchestrator` | `NB_00_ORCHES_SLV_TO_ENR_15P` | `PROPOSED` | `USER_STATED` | `MQ-044` | `[PROPOSED]` Clone từ `NB_00_ORCHES_SLV_TO_GLD`. Đây là orchestrator của luồng enrich |
| `FLOW-004` | `TRG-001` | `nb_name` | `NB_ENR_POI_INFO` | `PROPOSED` | `USER_STATED` | `MQ-028` | `[PROPOSED]` |
| `FLOW-005` | `TRG-002` | `nb_name` | `NB_ENR_POI_COORDINATE` | `PROPOSED` | `USER_STATED` | `MQ-028` | `[PROPOSED]` |
| `FLOW-006` | `TRG-003` | `nb_name` | `NB_ENR_POI_REVIEW` | `PROPOSED` | `USER_STATED` | `MQ-028` | `[PROPOSED]` |
| `FLOW-007` | `TRG-001`, `TRG-002`, `TRG-003` | `cadence` | Mỗi 15 phút một lần | | `USER_STATED` | `MQ-002` | |

## 3. Bảng nguồn

| src_id | layer | lakehouse_schema | src_tbl | grain | grain_evidence | key_columns | key_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `SRC-001` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_review` | 1 dòng / `review_id` | `CONTEXT_STATED` | `review_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | `gld_enr_poi_review.review_id` copy cột `review_id` này. Không hash lại |
| `SRC-002` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Có `poi_name`, `types_json` |
| `SRC-003` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_address` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Có `short_address`, `ward`, `district`, `city`, `state_province`, `lat`, `lng` |
| `SRC-004` | `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_business_services` | 1 dòng / `id` | `CONTEXT_STATED` | `id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.1`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS` | Có `name`, `bio`, `address` |
| `SRC-005` | `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_business_service_i18ns` | 1 dòng / (`business_service_id`, `locale`) | `CONTEXT_STATED` | `business_service_id`, `locale` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.1`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS` | Có `name`, `bio`. Nghiệp vụ chỉ lấy locale tiếng Việt |
| `SRC-013` | `silver_l2` | `lh_vv_silver.dbo` | `slv_pn_poi` | 1 dòng / `poi_id` | `USER_STATED` | `poi_id` | `USER_STATED` | `PROPOSED` | `MQ-063` | `[PROPOSED]` Tính `poi_id` partner trước gold. Cột: `poi_id`, `business_service_id`, `name`, `short_address`, `ward`, `district`, `province_name`. Người dùng chốt tên `slv_pn_poi` |
| `SRC-009` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_contact` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Có `website_url` |
| `SRC-010` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_rating` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Có `rating_overall`, `rating_count`. Không có cột `rating` |
| `SRC-011` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_price` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Có `price_level` kiểu `int` |
| `SRC-012` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi_opening_hours` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Có `periods_json` |

## 4. Bảng đích

| trg_id | layer | lakehouse_schema | trg_tbl | grain | grain_evidence | key_columns | key_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `TRG-001` | `gold` | `lh_vv_gold.enr` | `gld_enr_poi_info` | 1 dòng lịch sử append / (`poi_id`, `updated_at`) | `USER_STATED` | `poi_id`, `updated_at` | `USER_STATED` | `PROPOSED` | `MQ-039` | `[PROPOSED]` Append để lưu lịch sử. Nhiều dòng cùng `poi_id` khi `updated_at` khác nhau |
| `TRG-002` | `gold` | `lh_vv_gold.enr` | `gld_enr_poi_coordinate` | 1 dòng lịch sử append / (`poi_id`, `updated_at`) | `USER_STATED` | `poi_id`, `updated_at` | `USER_STATED` | `PROPOSED` | `MQ-039` | `[PROPOSED]` Cùng grain với `TRG-001` |
| `TRG-003` | `gold` | `lh_vv_gold.enr` | `gld_enr_poi_review` | 1 dòng lịch sử append / (`review_id`, `updated_at`) | `USER_STATED` | `review_id`, `updated_at` | `USER_STATED` | `PROPOSED` | `MQ-039` | `[PROPOSED]` Append để lưu lịch sử. Nhiều dòng cùng `review_id` khi `updated_at` khác nhau. Không có nguồn partner |

## 5. Mapping cột

> Một POI thuộc một nguồn. Dòng 3rd-party và dòng partner dùng công thức của nguồn đó, không gộp thành một biểu thức.

| col_id | req_ids | src_id | src_object | src_column_or_json_path | trg_id | trg_column | data_type | convert_rule | is_key | key_order | rule_ids | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `COL-001` | `BR-001` | `SRC-002`, `SRC-013` | | `poi_id`; `poi_id` | `TRG-001` | `poi_id` | `string` | | `true` | | | `CONTEXT_STATED, USER_STATED` | `MQ-006`, `MQ-039`, `MQ-063`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: copy `slv_3p_poi.poi_id`. Partner: copy `slv_pn_poi.poi_id`. Không hash trên gold. `NOT NULL`. Khoá ghép với `updated_at` |
| `COL-003` | `BR-001` | `SRC-002` | | `business_sector` | `TRG-001` | `time_to_spend` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-048`, `MQ-061`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | `business_sector` có trong model mới. Chuỗi hiển thị là nghiệp vụ model cũ của riêng cột này: NULL hoặc <= 0 thì `Không cố định`; `accommodation` thì số ngày làm tròn lên; `tour_n_activities` và >= 420 phút thì `Cả ngày`; dưới 60 phút thì số phút; còn lại thì số tiếng và phút dư. Giá trị là `to_json(map(duration_label, duration_text))`. `duration_label` theo `RULE-003`. Model mới đã gỡ `slv_3p_poi_enrichment`. Không có bảng `poi_enrichment` |
| `COL-004` | `BR-001` | | | | `TRG-001` | `best_time_type` | `string` | | `false` | | | `USER_STATED` | `MQ-009`, `MQ-061` | Nghiệp vụ model cũ của riêng cột này: lấy type của best time. Model mới đã gỡ `slv_3p_poi_enrichment`. Không có bảng nguồn hiện tại |
| `COL-005` | `BR-001` | | | | `TRG-001` | `best_time_from_month` | `int` | | `false` | | | `USER_STATED` | `MQ-010`, `MQ-061` | Nghiệp vụ model cũ của riêng cột này: giữ số tháng bắt đầu, kiểu `int`. Model mới không có bảng nguồn |
| `COL-006` | `BR-001` | | | | `TRG-001` | `best_time_to_month` | `int` | | `false` | | | `USER_STATED` | `MQ-010`, `MQ-061` | Nghiệp vụ model cũ của riêng cột này: giữ số tháng kết thúc, kiểu `int`. Model mới không có bảng nguồn |
| `COL-007` | `BR-001` | | | | `TRG-001` | `cost` | `bigint` | | `false` | | | `USER_STATED` | `MQ-061` | Không lấy `costVnd` từ model cũ. Model mới không có cột đó. Cột `cost` giữ theo yêu cầu. Chưa gắn nguồn model mới |
| `COL-008` | `BR-001` | `SRC-002` | | `types_json` | `TRG-001` | `subcategory_tags` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-049`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: copy `types_json`, cùng nguồn với cột `types`. Không dùng `subcategory_tags_json`. Partner: NULL |
| `COL-009` | `BR-001` | | | | `TRG-001` | `created_at` | `timestamp` | | `false` | | | `USER_STATED` | `MQ-052`, `MQ-058` | Cột kỹ thuật lúc ghi. `src_id` không bắt buộc. Gán mỗi lần ghi |
| `COL-010` | `BR-001` | | | | `TRG-001` | `updated_at` | `timestamp` | | `true` | | | `USER_STATED` | `MQ-039`, `MQ-052`, `MQ-058` | Cột kỹ thuật lúc ghi. `src_id` không bắt buộc. Thuộc khoá grain lịch sử |
| `COL-011` | `BR-002` | `SRC-002`, `SRC-013` | | `poi_id`; `poi_id` | `TRG-002` | `poi_id` | `string` | | `true` | | | `CONTEXT_STATED, USER_STATED` | `MQ-006`, `MQ-039`, `MQ-063`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Cùng `COL-001`. 3rd-party copy `slv_3p_poi.poi_id`. Partner copy `slv_pn_poi.poi_id`. Không hash trên gold |
| `COL-012` | `BR-002` | `SRC-002`, `SRC-013` | | `poi_name`; `name` | `TRG-002` | `name` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-014`, `MQ-063`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: `slv_3p_poi.poi_name`. Partner: copy `slv_pn_poi.name` |
| `COL-013` | `BR-002` | `SRC-003`, `SRC-013` | | `short_address`; `short_address` | `TRG-002` | `short_address` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-063`, `docs/context/01_DATA_MODEL.md §4`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: `slv_3p_poi_address.short_address`. Partner: copy `slv_pn_poi.short_address` |
| `COL-014` | `BR-002` | `SRC-003`, `SRC-013` | | `ward`; `ward` | `TRG-002` | `ward` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-063`, `docs/context/01_DATA_MODEL.md §4`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: `slv_3p_poi_address.ward`. Partner: copy `slv_pn_poi.ward` |
| `COL-015` | `BR-002` | `SRC-003`, `SRC-013` | | `district`; `district` | `TRG-002` | `district` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-063`, `docs/context/01_DATA_MODEL.md §4`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: `slv_3p_poi_address.district`. Partner: copy `slv_pn_poi.district` |
| `COL-016` | `BR-002` | `SRC-003`, `SRC-013` | | `city`; `province_name` | `TRG-002` | `province_name` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-063`, `docs/context/01_DATA_MODEL.md §4`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: `slv_3p_poi_address.city`. Partner: copy `slv_pn_poi.province_name` |
| `COL-017` | `BR-002` | `SRC-003` | | `city` | `TRG-002` | `destination_name` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-050`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | [SỬA 19/10] Chỉ `city`. Không còn JSON array. Partner: NULL |
| `COL-018` | `BR-002` | `SRC-003` | | `lat` | `TRG-002` | `lat` | `double` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-019`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: `lat`. Partner: NULL |
| `COL-019` | `BR-002` | `SRC-003` | | `lng` | `TRG-002` | `lng` | `double` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-019`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: `lng`. Partner: NULL |
| `COL-020` | `BR-002` | | | | `TRG-002` | `created_at` | `timestamp` | | `false` | | | `USER_STATED` | `MQ-052`, `MQ-058` | Cột kỹ thuật lúc ghi. `src_id` không bắt buộc |
| `COL-021` | `BR-002` | | | | `TRG-002` | `updated_at` | `timestamp` | | `true` | | | `USER_STATED` | `MQ-039`, `MQ-052`, `MQ-058` | Cột kỹ thuật lúc ghi. `src_id` không bắt buộc. Thuộc khoá grain lịch sử |
| `COL-022` | `BR-003` | `SRC-001` | | `review_id` | `TRG-003` | `review_id` | `string` | | `true` | | | `CONTEXT_STATED, USER_STATED` | `MQ-062`, `MQ-039`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Copy `slv_3p_poi_review.review_id`. Không hash. `NOT NULL`. Khoá ghép với `updated_at`. Chỉ 3rd-party |
| `COL-023` | `BR-003` | `SRC-001` | | `poi_id` | `TRG-003` | `poi_id` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-045`, `MQ-062`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Copy `slv_3p_poi_review.poi_id`. Không hash lại. Không có nguồn partner |
| `COL-025` | `BR-003` | `SRC-001` | | `rating` | `TRG-003` | `rating` | `decimal(3,1)` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-051`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Thang 5 sao. Kiểu đích `decimal(3,1)`. Nguồn registry là `decimal(4,2)` |
| `COL-027` | `BR-003` | `SRC-001` | | `text` | `TRG-003` | `review_text` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-057`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Tên đích `review_text`. Giá trị lấy `slv_3p_poi_review.text` |
| `COL-031` | `BR-003` | `SRC-001` | | `time` | `TRG-003` | `review_date` | `timestamp` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-023`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Giữ `timestamp`. Cast `time` sang `timestamp`, cùng trường với `review_updated_at`. Không dùng cast `date` của NB_20 |
| `COL-032` | `BR-003` | `SRC-001` | | `time` | `TRG-003` | `review_updated_at` | `timestamp` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-004`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Nguồn là `slv_3p_poi_review.time`. Cùng trường được registry cast `ISO_UTC_TS` thành `published_at`. Không còn dùng tên `updatedAt` |
| `COL-033` | `BR-003` | | | | `TRG-003` | `created_at` | `timestamp` | | `false` | | | `USER_STATED` | `MQ-052`, `MQ-058` | Cột kỹ thuật lúc ghi. `src_id` không bắt buộc |
| `COL-034` | `BR-003` | | | | `TRG-003` | `updated_at` | `timestamp` | | `true` | | | `USER_STATED` | `MQ-039`, `MQ-052`, `MQ-058` | Cột kỹ thuật lúc ghi. `src_id` không bắt buộc. Thuộc khoá grain lịch sử |
| `COL-035` | `BR-001` | `SRC-002` | | `poi_name` | `TRG-001` | `poi_name` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-033`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: `slv_3p_poi.poi_name`. Partner: NULL |
| `COL-036` | `BR-001` | `SRC-002` | | `types_json` | `TRG-001` | `types` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-033`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: copy `types_json`. Partner: NULL. Khác cột `subcategory_tags` |
| `COL-037` | `BR-001` | `SRC-002` | | `business_sector` | `TRG-001` | `business_sector` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-033`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: copy. Partner: NULL |
| `COL-038` | `BR-001` | `SRC-002` | | `business_category` | `TRG-001` | `business_category` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-033`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: copy. Partner: NULL |
| `COL-039` | `BR-001` | `SRC-009` | | `website_url` | `TRG-001` | `website_url` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-033`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: copy. Partner: NULL |
| `COL-040` | `BR-001` | `SRC-003` | | `address_viet_map` | `TRG-001` | `short_address` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-033`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: `address_viet_map`. Partner: NULL. Khác `short_address` của bảng coordinate |
| `COL-041` | `BR-001` | `SRC-003` | | `district` | `TRG-001` | `district` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-033`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | 3rd-party: copy `district`. Partner: NULL |
| `COL-042` | `BR-001` | `SRC-003` | | `city` | `TRG-001` | `destination_name` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-050`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | [SỬA 19/10] Chỉ `city`. Không còn JSON array. Partner: NULL |
| `COL-043` | `BR-001` | `SRC-003` | | `short_address`, `district`, `city` | `TRG-001` | `destination_context` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-036`, `MQ-061`, `docs/context/01_DATA_MODEL.md §4`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Câu người dùng chốt, nguồn là cột model mới `short_address`, `district`, `city` và `destination_name` của `COL-042`. Không lấy từ model cũ. Partner: NULL |
| `COL-044` | `BR-001` | `SRC-010` | | `rating_overall` | `TRG-001` | `rating` | `decimal(4,2)` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-035`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Tên đích giữ `rating`. Nguồn là `rating_overall`. Partner: NULL |
| `COL-045` | `BR-001` | `SRC-010` | | `rating_count` | `TRG-001` | `userRatingCount` | `bigint` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-033`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | `[PROPOSED]` Tên đích giữ camelCase. Partner: NULL |
| `COL-046` | `BR-001` | `SRC-011` | | `price_level` | `TRG-001` | `priceLevel` | `int` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-033`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | `[PROPOSED]` Tên đích giữ camelCase. Partner: NULL |
| `COL-047` | `BR-001` | `SRC-012` | | `periods_json` | `TRG-001` | `opening_hours_text` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-037`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | Copy 1:1. Partner: NULL |
| `COL-048` | `BR-001` | `SRC-001` | | `review_id`, `text`, `time`, `published_at` | `TRG-001` | `review_json` | `string` | | `false` | | | `CONTEXT_STATED, USER_STATED` | `MQ-053`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | JSON array, sắp `time` giảm, tối đa 20 review. `review_text` cắt 350 ký tự. Mỗi phần tử có `review_id`, `review_text`, `time`, `published_at`. Không chép nội dung mẫu. Partner: NULL. Rule `RULE-006` |

`COL-002` đã bỏ: `description` không còn trên `gld_enr_poi_info`. `COL-024` đã bỏ: `source_review_id` không còn trên `gld_enr_poi_review`. `COL-026`, `COL-028`, `COL-029`, `COL-030` đã bỏ: `title`, `positive`, `negative`, `response_text` không còn trên `gld_enr_poi_review`.

## 6. Mục thiếu evidence

| gap_id | blocks | missing_fact | why_repo_cannot_answer | resolution_type | pass_fail_criterion | note |
|---|---|---|---|---|---|---|

Không còn mục thiếu evidence mở. `MGAP-008` đến `MGAP-011` đã được trả lời ở mục 8.

## 7. Mâu thuẫn trong repository

| conflict_id | blocks | item | source_a | source_b | note |
|---|---|---|---|---|---|

Không còn mâu thuẫn mở. `MCONF-022` chốt tên đích `rating` lấy từ `rating_overall`. `MCONF-023` chốt fallback `state_province`.

## 8. Câu hỏi mở

| q_id | blocks | question | resolution_type | answer | answered_on |
|---|---|---|---|---|---|
| `MQ-001` | `TRG-001`, `TRG-002`, `TRG-003` | Grain và khoá của ba bảng là gì? | `USER_ANSWER` | `gld_enr_poi_info`: `poi_id`. `gld_enr_poi_coordinate`: `poi_id`. `gld_enr_poi_review`: `review_id`. | `2026-10-12` |
| `MQ-002` | `FLOW-002`, `FLOW-003`, `FLOW-005` | Luồng ghi ba bảng dùng orchestrator, nhịp và `load_mode` nào? | `USER_ANSWER` | Orchestrator `NB_00_ORCHES_SLV_TO_GLD`. Nhịp 15 phút một lần. `load_mode` là `Append`. | `2026-10-12` |
| `MQ-003` | `BR-003` | `title`, `positive`, `negative` và `response_text` lấy từ đâu? | `USER_ANSWER` | Bỏ, không xử lý. | `2026-10-12` |
| `MQ-004` | `COL-032` | `updatedAt` của review nằm ở đâu? | `USER_ANSWER` | Nguồn là `slv_3p_poi_review.time`. | `2026-10-12` |
| `MQ-005` | `COL-025` | Đơn vị của `rating` là gì? | `USER_ANSWER` | Thang 5 sao. | `2026-10-12` |
| `MQ-006` | `COL-001`, `COL-011`, `COL-023` | `poi_id` dùng công thức nào? | `USER_ANSWER` | Nguồn chỉ có tiếng Việt. 3rd-party và partner đều không đưa ngôn ngữ vào `poi_id`, theo model mới. | `2026-10-12` |
| `MQ-007` | | `description` lấy từ đâu? | `USER_ANSWER` | Bio của partner. 3rd-party là NULL. Cột `description` sau đó đã bỏ khỏi `gld_enr_poi_info`. | `2026-10-12` |
| `MQ-008` | `COL-003` | `time_to_spend` là số phút hay chuỗi hiển thị? | `USER_ANSWER` | Chuỗi hiển thị tiếng Việt. | `2026-10-12` |
| `MQ-009` | `COL-004` | `best_time_type` lấy từ đâu? | `USER_ANSWER` | `$.bestTime.type`. | `2026-10-12` |
| `MQ-010` | `COL-005`, `COL-006` | Tháng giữ số hay chuỗi? | `USER_ANSWER` | Giữ số. | `2026-10-12` |
| `MQ-011` | `COL-007` | `cost` là giá gốc hay chuỗi hiển thị? | `USER_ANSWER` | `costVnd`, giá gốc, vì chỉ còn tiếng Việt. | `2026-10-12` |
| `MQ-012` | `COL-008` | `subcategory_tags` lấy từ đâu? | `USER_ANSWER` | 3rd-party từ `types_json`. Partner là NULL. | `2026-10-12` |
| `MQ-013` | `COL-009` | `created_at` và `updated_at` đổi mỗi lần ghi, hay `updated_at` chỉ đổi khi `row_hash` đổi? | `USER_ANSWER` | Có hai câu trong cùng lượt: `updated_at` chỉ đổi khi `row_hash` đổi; và `created_at` cùng `updated_at` đổi mỗi lần ghi. Câu được chọn ở `MQ-030` là đổi mỗi lần ghi. | `2026-10-12` |
| `MQ-030` | `COL-009`, `COL-010`, `COL-020`, `COL-021`, `COL-033`, `COL-034` | Trong hai câu vừa nêu, câu nào là rule của ba bảng mới? | `USER_ANSWER` | Đổi mỗi lần ghi. | `2026-10-12` |
| `MQ-014` | `COL-012` | `name` lấy từ ngôn ngữ nào? | `USER_ANSWER` | `poi_name` của tiếng Việt, ngôn ngữ gốc duy nhất của nguồn. | `2026-10-12` |
| `MQ-015` | `COL-013` | `short_address` của partner lấy `full_address` hay `street`? | `USER_ANSWER` | Cả partner và 3rd-party đều cung cấp cột. 3rd-party dùng `short_address`. Partner chốt `address.full_address` ở `MQ-025`. | `2026-10-12` |
| `MQ-016` | `COL-014`, `COL-015` | `ward` và `district` lấy từ nguồn nào? | `USER_ANSWER` | Cả partner và 3rd-party. | `2026-10-12` |
| `MQ-017` | `COL-016` | `province_name` của 3rd-party lấy `city` hay `state_province`? | `USER_ANSWER` | Cả partner và 3rd-party đều cung cấp cột. 3rd-party chốt `city` ở `MQ-026`. | `2026-10-12` |
| `MQ-018` | `COL-017` | `destination_name` là một tên hay JSON array? | `USER_ANSWER` | JSON array. | `2026-10-12` |
| `MQ-019` | `COL-018`, `COL-019` | `lat` và `lng` lấy từ đâu? | `USER_ANSWER` | 3rd-party lấy `lat` và `lng`. Partner là NULL. | `2026-10-12` |
| `MQ-020` | `COL-022` | `review_id` dùng công thức nào? | `USER_ANSWER` | Câu này bị thay bởi `MQ-062`: copy `slv_3p_poi_review.review_id`, không hash. | `2026-10-12` |
| `MQ-021` | `TRG-003` | `source_review_id` là gì? | `USER_ANSWER` | Câu này bị thay bởi `MQ-062`: bỏ `source_review_id`. | `2026-10-12` |
| `MQ-023` | `COL-031` | `review_date` cast `time` sang `timestamp` hay sang `date`? | `USER_ANSWER` | Giữ `timestamp`. | `2026-10-12` |
| `MQ-024` | `TRG-001`, `TRG-002`, `TRG-003` | Giữ schema `enr` và tiền tố `gld_enr_` hay đổi về `gld_srv_`? | `USER_ANSWER` | Giữ `lh_vv_gold.enr` và `gld_enr_`. | `2026-10-12` |
| `MQ-025` | `COL-013` | Partner ghi `short_address` từ `address.full_address` hay từ `address.street`? | `USER_ANSWER` | `address.full_address`. | `2026-10-12` |
| `MQ-026` | `COL-016` | 3rd-party ghi `province_name` từ `city` hay từ `state_province`? | `USER_ANSWER` | `city`. | `2026-10-12` |
| `MQ-027` | `FLOW-002` | `Append` có được giữ làm `load_mode`, hay phải đổi thành một giá trị ở `docs/context/02_NAMING_CONVENTION.md §6`? | `USER_ANSWER` | Giữ tên `APPEND`. Có dữ liệu mới thì append, không merge kể cả khi key đã tồn tại. | `2026-10-12` |
| `MQ-028` | `FLOW-001`, `FLOW-003`, `FLOW-004`, `FLOW-005`, `FLOW-006` | `pl_name` và `nb_name` của luồng này là gì? | `USER_ANSWER` | `pl_name` là `PL_VV_TRANS_SLV_TO_ENR_15P`. `nb_name` là `NB_ENR_POI_INFO` `NB_ENR_POI_COORDINATE` `NB_ENR_POI_REVIEW`. | `2026-10-12` |
| `MQ-029` | `COL-017` | Grain và khoá của `destination_ward_mapping` là gì? | `USER_ANSWER` | Ba bảng đích không dùng `destination_ward_mapping`. | `2026-10-12` |
| `MQ-031` | `TRG-001`, `TRG-002`, `TRG-003` | `APPEND` không merge khi key đã có. Bảng vẫn là 1 dòng / key, hay được nhiều dòng cùng `poi_id` hoặc `review_id`? | `USER_ANSWER` | Được nhiều dòng cùng `poi_id` hoặc `review_id`. | `2026-10-12` |
| `MQ-032` | `COL-017`, `COL-042` | `destination_name` lấy từ cột nguồn nào? | `USER_ANSWER` | `city`, fallback `province_name`. Dạng giá trị được chốt sau ở `MQ-043` là JSON array chuỗi. | `2026-10-12` |
| `MQ-033` | `COL-035`, `COL-036`, `COL-037`, `COL-038`, `COL-039`, `COL-040`, `COL-041`, `COL-042`, `COL-043`, `COL-044`, `COL-045`, `COL-046`, `COL-047`, `COL-048` | Các cột mới trên `gld_enr_poi_info` với dòng partner lấy từ đâu, hay để NULL? | `USER_ANSWER` | Không lấy partner. POI partner thì NULL. | `2026-10-12` |
| `MQ-034` | `COL-017`, `COL-042` | Fallback `province_name` không có trên `slv_3p_poi_address`. Dùng `state_province`, hay giữ một cột tên `province_name`? | `USER_ANSWER` | Dùng `slv_3p_poi_address.state_province`. [SỬA 19/10] `destination_name` chỉ còn `city`. | `2026-10-12` |
| `MQ-035` | `COL-044` | `rating` của bảng info lấy `rating_overall`, hay một cột khác tên `rating`? | `USER_ANSWER` | Tên đích giữ `rating`. Nguồn là `slv_3p_poi_rating.rating_overall`. | `2026-10-12` |
| `MQ-036` | `COL-043` | `{address}` và `{province}` trong `destination_context` lấy cột nào? | `USER_ANSWER` | `This POI is located at {slv_3p_poi_address.short_address}, {slv_3p_poi_address.district}, {slv_3p_poi_address.city}, Vietnam (destination area: {destination_name}).` | `2026-10-12` |
| `MQ-037` | `COL-047` | `periods_json` được đổi thành `opening_hours_text` bằng phép nào? | `USER_ANSWER` | Copy 1:1. | `2026-10-12` |
| `MQ-038` | `COL-048` | `Title`, `Positive`, `Negative` lấy từ cột nào, và sắp review theo `time` hay `published_at`? | `USER_ANSWER` | Không cần Title, Positive, Negative. Dạng sau được chốt ở `MQ-042` là JSON array sắp theo `time`. | `2026-10-12` |
| `MQ-039` | `TRG-001`, `TRG-002`, `TRG-003` | Một dòng lịch sử append được xác định bởi cột nào? | `USER_ANSWER` | Info và coordinate: `poi_id` với `updated_at`. Review: `review_id` với `updated_at`. | `2026-10-12` |
| `MQ-040` | `FLOW-002` | Append khi nào? | `USER_ANSWER` | Append cả POI tạo mới và POI có update. | `2026-10-12` |
| `MQ-041` | `COL-003` | `duration_label` lấy từ đâu? | `USER_ANSWER` | `slv_3p_poi.business_sector`. Nhãn tiếng Việt theo từng giá trị sector, ghi ở `RULE-003`. | `2026-10-12` |
| `MQ-042` | `COL-048` | `review_json` sắp và định dạng thế nào? | `USER_ANSWER` | Sắp theo `slv_3p_poi_review.time`. Giá trị là JSON array. Mỗi phần tử có `review_id`, `review_text`, `time`, `published_at`. Không chép nội dung mẫu. | `2026-10-12` |
| `MQ-043` | `COL-017`, `COL-042` | `destination_name` có dạng gì? | `USER_ANSWER` | JSON array các chuỗi. Không chép nội dung mẫu. | `2026-10-12` |
| `MQ-044` | `FLOW-003` | Orchestrator của luồng enrich là notebook nào? | `USER_ANSWER` | `NB_00_ORCHES_SLV_TO_ENR_15P`, clone từ `NB_00_ORCHES_SLV_TO_GLD`. | `2026-10-12` |
| `MQ-045` | `COL-023`, `TRG-003` | Bảng review có nguồn partner không? | `USER_ANSWER` | Không. | `2026-10-12` |
| `MQ-046` | `FLOW-002` | Có lọc soft delete không? | `USER_ANSWER` | Chưa có nghiệp vụ soft delete. Xử lý không có delete. | `2026-10-12` |
| `MQ-047` | `FLOW-002` | Thay đổi nào được tính là POI có update? | `USER_ANSWER` | Mọi thay đổi đều tính là POI có update. | `2026-10-12` |
| `MQ-048` | `COL-003` | Logic transform lấy từ đâu, và `best_time_label` với `cost_label` nằm ở cột nào? | `USER_ANSWER` | Logic transform lấy như notebook legacy trong `notebooks_lgc/3rd_data_ingested_orches`. `best_time_label` và `cost_label` không có cột đích riêng. | `2026-10-12` |
| `MQ-049` | `COL-008` | `subcategory_tags` copy `types_json` hay `subcategory_tags_json`? | `USER_ANSWER` | Copy `types_json`. | `2026-10-12` |
| `MQ-050` | `COL-017`, `COL-042` | `destination_name` là JSON array hay chuỗi `coalesce`? | `USER_ANSWER` | Chuỗi `coalesce(city, state_province)`. Không để JSON array. | `2026-10-12` |
| `MQ-051` | `COL-025` | Kiểu `rating` của bảng review là gì? | `USER_ANSWER` | `decimal(3,1)`. | `2026-10-12` |
| `MQ-052` | `COL-009`, `COL-010`, `COL-020`, `COL-021`, `COL-033`, `COL-034` | `created_at` và `updated_at` ghi thế nào khi mẫu bắt buộc có nguồn? | `USER_ANSWER` | Chấp nhận là cột kỹ thuật lúc ghi. | `2026-10-12` |
| `MQ-053` | `COL-048` | `review_json` sắp chiều nào, giới hạn bao nhiêu, và `review_text` có cắt không? | `USER_ANSWER` | Sắp `time` giảm. Tối đa 20 review. `review_text` cắt 350 ký tự. | `2026-10-12` |
| `MQ-054` | `RULE-001`, `RULE-003`, `RULE-004`, `RULE-005`, `RULE-006` | Rule nằm ở bảng `slv_poi_*` hoặc `ref_*` nào? | `USER_ANSWER` | Không có bảng rule riêng. | `2026-10-12` |
| `MQ-056` | `SRC-005`, `COL-022` | Có probe schema và dữ liệu của model cũ không? | `USER_ANSWER` | Không. Model cũ chỉ cung cấp nghiệp vụ bốn trường ở `MQ-059`. | `2026-10-12` |
| `MQ-057` | `COL-027` | Cột chữ review trên `gld_enr_poi_review` tên gì và lấy từ đâu? | `USER_ANSWER` | Giữ tên `review_text`. Lấy từ `slv_3p_poi_review.text`. | `2026-10-12` |
| `MQ-058` | `FLOW-002`, `COL-001`, `COL-009`, `COL-010`, `COL-011`, `COL-012`, `COL-013`, `COL-014`, `COL-015`, `COL-016`, `COL-020`, `COL-021`, `COL-033`, `COL-034` | Khi một bảng đích dùng cả partner và 3rd-party thì hai nguồn join hay append, và `src_id` có bắt buộc không? | `USER_ANSWER` | Append, không join. `source_id` luôn có trên dòng của từng nguồn. Bỏ luật bắt buộc phải có `src_id`. Câu ngoại lệ mẫu về `src_id` bỏ vì ngoài phạm vi. | `2026-10-12` |
| `MQ-059` | `COL-003`, `COL-004`, `COL-005`, `COL-006` | Model cũ được dùng cho trường nào? | `USER_ANSWER` | Chỉ nghiệp vụ của `time_to_spend`, `best_time_type`, `best_time_from_month`, `best_time_to_month`. Không dùng cho `cost`, địa chỉ partner, hay một bảng staging. | `2026-10-12` |
| `MQ-060` | `COL-014`, `COL-016` | Ba bảng `gld_enr_*` có đọc `poi_address_enrichment_staging` không? | `USER_ANSWER` | Không. Bảng đó không thuộc model mới của task này. Nó bị suy ra từ notebook cũ. | `2026-10-12` |
| `MQ-061` | `COL-003`, `COL-004`, `COL-005`, `COL-006`, `COL-007`, `COL-012`, `COL-013`, `COL-014`, `COL-015`, `COL-016`, `COL-043` | Context model cũ còn được đưa vào thiết kế những chỗ nào? | `USER_ANSWER` | Chỉ bốn trường info ở `MQ-059`. `destination_context` dùng cột địa chỉ của model mới. | `2026-10-12` |
| `MQ-062` | `COL-022`, `TRG-003` | `review_id` của `gld_enr_poi_review` lấy từ đâu, và `source_review_id` còn không? | `USER_ANSWER` | Bảng review chỉ có 3rd-party, không có partner. Bỏ `source_review_id`. `review_id` copy `slv_3p_poi_review.review_id`, không hash. | `2026-10-12` |
| `MQ-063` | `SRC-013`, `COL-001`, `COL-011`, `COL-012`, `COL-013`, `COL-014`, `COL-015`, `COL-016` | `poi_id` partner tính ở đâu? | `USER_ANSWER` | Tính ở silver, bảng `slv_pn_poi`. Gold info và coordinate chỉ copy. | `2026-10-12` |
