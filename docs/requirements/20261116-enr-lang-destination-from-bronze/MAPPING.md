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
| `mapping_id` | `MAP-20261116-enr-lang-destination-from-bronze` |
| `task_id` | `20261116-enr-lang-destination-from-bronze` |
| `brd_id` | `BRD-20261116-enr-lang-destination-from-bronze` |
| `version` | `6` |
| `doc_status` | `READY_FOR_ANALYSIS` |
| `owner_role` | `data-platform` |
| `updated_on` | `2026-11-16` |

## 2. Luồng xử lý

| flow_id | trg_ids | field | value | name_status | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|
| `FLOW-001` | `TRG-003` | `orchestrator` | `NB_00_ORCHES_SLV_TO_GLD` | `EXISTING` | `CONTEXT_STATED` | `docs/context/mapping_gld_srv_poi_multi_lang.md §1.1`, `docs/context/02_NAMING_CONVENTION.md §2` | |
| `FLOW-002` | `TRG-003` | `load_mode` | `RECOMPUTE` | | `CONTEXT_STATED` | `docs/context/mapping_gld_srv_poi_multi_lang.md §1.1`, `docs/context/02_NAMING_CONVENTION.md §6` | |
| `FLOW-003` | `TRG-003` | `pl_name` | `PL_VV_TRANS_SLV_TO_GLD_30M` | `EXISTING` | `CONTEXT_STATED` | `docs/context/mapping_gld_srv_poi_multi_lang.md §1.1`, `docs/context/02_NAMING_CONVENTION.md §3` | |
| `FLOW-004` | `TRG-003` | `cadence` | 30 phút | | `CONTEXT_STATED` | `docs/context/02_NAMING_CONVENTION.md §3`, `AGENTS.md §7` | Hậu tố `_30M` |
| `FLOW-005` | `TRG-003` | `nb_name` | `NB_GLD_SRV_POI_MULTI_LANG` | `EXISTING` | `CONTEXT_STATED` | `docs/context/mapping_gld_srv_poi_multi_lang.md §1.1`, `docs/context/02_NAMING_CONVENTION.md §2` | |
| `FLOW-006` | `TRG-004` | `orchestrator` | `NB_00_ORCHES_SLV_TO_GLD` | `EXISTING` | `CONTEXT_STATED` | `docs/context/mapping_gld_srv_poi_info.md §1.1`, `docs/context/02_NAMING_CONVENTION.md §2` | |
| `FLOW-007` | `TRG-004` | `load_mode` | `RECOMPUTE` | | `CONTEXT_STATED` | `docs/context/mapping_gld_srv_poi_info.md §1.1`, `docs/context/02_NAMING_CONVENTION.md §6` | |
| `FLOW-008` | `TRG-004` | `pl_name` | `PL_VV_TRANS_SLV_TO_GLD_30M` | `EXISTING` | `CONTEXT_STATED` | `docs/context/mapping_gld_srv_poi_info.md §1.1`, `docs/context/02_NAMING_CONVENTION.md §3` | |
| `FLOW-009` | `TRG-004` | `cadence` | 30 phút | | `CONTEXT_STATED` | `docs/context/02_NAMING_CONVENTION.md §3`, `AGENTS.md §7` | |
| `FLOW-010` | `TRG-004` | `nb_name` | `NB_GLD_SRV_POI_INFO` | `EXISTING` | `CONTEXT_STATED` | `docs/context/mapping_gld_srv_poi_info.md §1.1`, `docs/context/02_NAMING_CONVENTION.md §2` | |
| `FLOW-011` | `TRG-001`, `TRG-002` | `load_mode` | `DOC` | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `docs/context/02_NAMING_CONVENTION.md §6`, `docs/context/mapping_gld_srv_poi_multi_lang.md §2` | Watermark `EventProcessedUtcTime`. Mỗi bảng chỉ nhận đúng `event_type` của nó |
| `FLOW-012` | `TRG-001`, `TRG-002` | `nb_name` | `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` | `PROPOSED` | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `docs/context/02_NAMING_CONVENTION.md §2` | `[PROPOSED]` Một notebook extract cho nguồn enrichment. Hậu tố `_CDC_` theo mẫu tên, `load_mode` vẫn là `DOC` |

## 3. Bảng nguồn

| src_id | layer | lakehouse_schema | src_tbl | grain | grain_evidence | key_columns | key_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `SRC-001` | `bronze` | `lh_vv_bronze.dbo` | `brz_enrichment_result` | 1 dòng / `event_id` trong snapshot DEV 473 dòng | `TASK_EVIDENCE` | | | `PROPOSED` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | `[PROPOSED]` Tên không có trong repository. Probe: `TABLE_STATUS=PRESENT`, `event_id` distinct 473, surplus 0. `key_columns` để trống vì nguồn bronze |
| `SRC-002` | `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_entity_non_enrich` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` `pk` | `pk=("poi_id",)` |
| `SRC-003` | `silver_l1` | `lh_vv_silver.dbo` | `slv_enr_poi_info_multi_lang` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | `EXISTING` | `docs/context/mapping_gld_srv_poi_multi_lang.md §2` | Cùng khoá thì giữ `version` lớn hơn; bằng `version` thì giữ `EventProcessedUtcTime` lớn hơn. Tiền tố `slv_enr_` được giữ |
| `SRC-004` | `silver_l1` | `lh_vv_silver.dbo` | `slv_enr_poi_destination` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/mapping_gld_srv_poi_info.md §1.6` | Cùng luật `version` như `SRC-003`. Tiền tố `slv_enr_` được giữ |

## 4. Bảng đích

| trg_id | layer | lakehouse_schema | trg_tbl | grain | grain_evidence | key_columns | key_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `TRG-001` | `silver_l1` | `lh_vv_silver.dbo` | `slv_enr_poi_info_multi_lang` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | `EXISTING` | `docs/context/mapping_gld_srv_poi_multi_lang.md §2` | Giữ tên bảng. Tiền tố `slv_enr_` không có trong bảng tiền tố |
| `TRG-002` | `silver_l1` | `lh_vv_silver.dbo` | `slv_enr_poi_destination` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/mapping_gld_srv_poi_info.md §1.6` | Giữ tên bảng. Bỏ cột `street` |
| `TRG-003` | `gold` | `lh_vv_gold.dbo` | `gld_srv_poi_multi_lang` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | `EXISTING` | `docs/context/mapping_gld_srv_poi_multi_lang.md §1.1` | MERGE theo (`poi_id`, `lang`) |
| `TRG-004` | `gold` | `lh_vv_gold.dbo` | `gld_srv_poi_info` | 1 dòng / `poi_id` | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/mapping_gld_srv_poi_info.md §1.1` | MERGE theo `poi_id` |

## 5. Mapping cột

| col_id | req_ids | src_id | src_object | src_column_or_json_path | trg_id | trg_column | data_type | convert_rule | is_key | key_order | rule_ids | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `COL-001` | `BR-001` | `SRC-001` | `$` | `_doc.poi_id` | `TRG-001` | `poi_id` | `string` | `NONE` | `true` | `1` | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `docs/context/mapping_gld_srv_poi_multi_lang.md §2` | Chỉ `event_type = LANG`. Khoá 1 |
| `COL-002` | `BR-001` | `SRC-001` | `$` | `_doc.source` | `TRG-001` | `source_name` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | Cột bronze `source` |
| `COL-003` | `BR-001` | `SRC-001` | `$` | `_doc.lang` | `TRG-001` | `lang` | `string` | `NONE` | `true` | `2` | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `docs/context/mapping_gld_srv_poi_multi_lang.md §2` | Khoá 2 |
| `COL-004` | `BR-001`, `BR-003`, `BR-004` | `SRC-001` | `$` | `data.display.cost` | `TRG-001` | `cost` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape.txt` | Đổi tên từ `cost_vnd`. 360/360 khóa `label,text`. Giữ chuỗi JSON object |
| `COL-005` | `BR-001` | `SRC-001` | `$` | `data.display.best_time` | `TRG-001` | `best_time` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape.txt` | 360/360 khóa `label,text`. Giữ chuỗi JSON object |
| `COL-006` | `BR-001` | `SRC-001` | `$` | `data.display.time_to_spend` | `TRG-001` | `time_to_spend` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape.txt` | 360/360 khóa `label,text`. Giữ chuỗi JSON object |
| `COL-007` | `BR-001` | `SRC-001` | `$` | `data.description` | `TRG-001` | `description` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` |  |
| `COL-008` | `BR-001` | `SRC-001` | `$` | `data.experiences` | `TRG-001` | `experience` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `docs/context/mapping_gld_srv_poi_multi_lang.md §2`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape_rest.txt` | Mảng 360/360. Phần tử đầu có khóa `description,keyword,title`. Ghi vào cột `experience` |
| `COL-009` | `BR-001` | `SRC-001` | `$` | `data.translated_at` | `TRG-001` | `translated_at` | `timestamp` | `ISO_UTC_TS` | `false` |  | | `USER_STATED`, `CONTEXT_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `docs/context/02_NAMING_CONVENTION.md §5.1`, `§6`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape_rest.txt` | 360/360 `parse_null=0` |
| `COL-010` | `BR-002` | `SRC-001` | `$` | `_doc.poi_id` | `TRG-002` | `poi_id` | `string` | `NONE` | `true` | `1` | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `docs/context/mapping_gld_srv_poi_info.md §1.6` | Chỉ `event_type = DESTINATION`. Khoá 1 |
| `COL-011` | `BR-002` | `SRC-001` | `$` | `_doc.source` | `TRG-002` | `source_name` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING |
| `COL-012` | `BR-002` | `SRC-001` | `$` | `data.address.new.ward.name` | `TRG-002` | `ward` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | DDL STRING. Nonempty 93/113 |
| `COL-013` | `BR-002` | `SRC-001` | `$` | `data.address.new.ward.name_with_type` | `TRG-002` | `ward_with_type` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING. Nonempty 93/113 |
| `COL-014` | `BR-002` | `SRC-001` | `$` | `data.address.new.district.name` | `TRG-002` | `district` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | DDL STRING. Nonempty 0/113 |
| `COL-015` | `BR-002` | `SRC-001` | `$` | `data.address.new.district.name_with_type` | `TRG-002` | `district_with_type` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING. Nonempty 0/113 |
| `COL-016` | `BR-002` | `SRC-001` | `$` | `data.address.new.province.name` | `TRG-002` | `city` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | DDL STRING. Nonempty 112/113 |
| `COL-017` | `BR-002` | `SRC-001` | `$` | `data.address.new.province.name_with_type` | `TRG-002` | `city_with_type` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING |
| `COL-018` | `BR-002` | `SRC-001` | `$` | `data.address.new.formatted_address` | `TRG-002` | `formatted_address` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING. Nonempty 112/113 |
| `COL-019` | `BR-002` | `SRC-001` | `$` | `data.address.old.ward.name` | `TRG-002` | `old_ward` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING. Nonempty 111/113 |
| `COL-020` | `BR-002` | `SRC-001` | `$` | `data.address.old.ward.name_with_type` | `TRG-002` | `old_ward_with_type` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING |
| `COL-021` | `BR-002` | `SRC-001` | `$` | `data.address.old.district.name` | `TRG-002` | `old_district` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING. Nonempty 111/113 |
| `COL-022` | `BR-002` | `SRC-001` | `$` | `data.address.old.district.name_with_type` | `TRG-002` | `old_district_with_type` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING |
| `COL-023` | `BR-002` | `SRC-001` | `$` | `data.address.old.province.name` | `TRG-002` | `old_city` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING. Nonempty 112/113 |
| `COL-024` | `BR-002` | `SRC-001` | `$` | `data.address.old.province.name_with_type` | `TRG-002` | `old_city_with_type` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING |
| `COL-025` | `BR-002` | `SRC-001` | `$` | `data.address.old.formatted_address` | `TRG-002` | `old_formatted_address` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt` | Cột mới STRING. Nonempty 112/113 |
| `COL-026` | `BR-002` | `SRC-001` | `$` | `data.lat` | `TRG-002` | `lat` | `double` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | DDL DOUBLE. Nonempty 112/113 |
| `COL-027` | `BR-002` | `SRC-001` | `$` | `data.lng` | `TRG-002` | `lng` | `double` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | DDL DOUBLE |
| `COL-028` | `BR-002` | `SRC-001` | `$` | `data.request.address` | `TRG-002` | `full_address` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | full_address silver, không phải công thức gold. Nonempty 113/113 |
| `COL-029` | `BR-002` | `SRC-001` | `$` | `data.destinations` | `TRG-002` | `destination` | `string` | `NONE` | `false` |  | | `USER_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape_rest.txt` | Chuỗi JSON của cả mảng. 113/113 là mảng. 112 mảng có phần tử đầu đủ khóa `id,kind,level,name,slug,status,strapi_document_id`. 1 mảng không có khóa ở phần tử đầu |
| `COL-030` | `BR-002` | `SRC-001` | `$` | `data.destinations.id` | `TRG-002` | `destination_id` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape_rest.txt` | DDL STRING. 271 phần tử, 1 phần tử id null. Giữ đúng thứ tự, kể cả null |
| `COL-031` | `BR-002` | `SRC-001` | `$` | `data.destinations.name` | `TRG-002` | `destination_name` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED`, `TASK_EVIDENCE` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `.ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape_rest.txt` | DDL STRING. Cùng thứ tự `destination_id`. 271 phần tử, 1 name null |
| `COL-032` | `BR-002` |  | `$` | `null` | `TRG-002` | `country_code` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | Ghi NULL. Không lấy từ JSON |
| `COL-033` | `BR-002` |  | `$` | `null` | `TRG-002` | `postal_code` | `string` | `NONE` | `false` |  | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` | Ghi NULL. Không lấy từ JSON |
| `COL-034` | `BR-003` | `SRC-003` | | `cost` | `TRG-003` | `cost` | `string` | | `false` | | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `docs/context/mapping_gld_srv_poi_multi_lang.md §1.2`, `docs/context/mapping_gld_srv_poi_multi_lang.md §2` | Đổi tên từ `cost_vnd` STRING. P1 copy 1-1, P2 null |
| `COL-035` | `BR-005` | `SRC-002` | | `street` | `TRG-004` | `street` | `string` | | `false` | | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `docs/context/mapping_gld_srv_poi_info.md §1.2`, `docs/context/mapping_gld_srv_poi_info.md §1.6` | Nguồn `slv_poi_entity_non_enrich.street` |
| `COL-036` | `BR-006` | `SRC-002`, `SRC-004` | | nhóm 1 `house_number` + `street` + `formatted_address`; nhóm 2 `house_number` + `street` + `ward_with_type` + `city_with_type`; nhóm 3 `slv_enr_poi_destination.full_address` | `TRG-004` | `full_address` | `string` | | `false` | | | `USER_STATED`, `CONTEXT_STATED` | `USER_INPUT`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS`, `docs/context/mapping_gld_srv_poi_info.md §1.6` | Dấu `, `. Null hoặc `house_number`/`street` chỉ còn khoảng trắng thì bỏ cả nhóm. Chỉ khi có dòng destination |

## 6. Mục thiếu evidence

| gap_id | blocks | missing_fact | why_repo_cannot_answer | resolution_type | pass_fail_criterion | note |
|---|---|---|---|---|---|---|

## 7. Mâu thuẫn trong repository

| conflict_id | blocks | item | source_a | source_b | note |
|---|---|---|---|---|---|

## 8. Câu hỏi mở

| q_id | blocks | question | resolution_type | answer | answered_on |
|---|---|---|---|---|---|
| `MQ-001` | `TRG-001`, `TRG-002` | Giữ tên `slv_enr_poi_info_multi_lang` và `slv_enr_poi_destination` dù tiền tố `slv_enr_` không nằm trong bảng tiền tố silver L1, và chấp nhận lệch PC-01 trên `SRC-003`, `SRC-004`? | `USER_ANSWER` | Giữ hai tên bảng đã có. Chấp nhận tiền tố `slv_enr_` lệch PC-01. | 2026-11-16 |
