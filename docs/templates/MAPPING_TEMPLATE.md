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
| `mapping_id` | `MAP-<task_id>` |
| `task_id` | `<task_id>` |
| `brd_id` | `BRD-<task_id>` |
| `version` | `<số nguyên từ 1>` |
| `doc_status` | `DRAFT` hoặc `READY_FOR_ANALYSIS` |
| `owner_role` | `<vai trò hoặc nhóm phụ trách; không ghi tên người, email, số điện thoại>` |
| `updated_on` | `<YYYY-MM-DD>` |

## 2. Luồng xử lý

> 1 dòng = 1 thuộc tính của luồng ghi các bảng đích ở `trg_ids` (mục 4). `field` chỉ nhận giá trị ở "Giá trị cho phép".
> `load_mode` theo `docs/context/02_NAMING_CONVENTION.md §6`. Tên notebook theo `§2`, tên pipeline theo `§3` của file đó.

| flow_id | trg_ids | field | value | name_status | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|
| `[EXAMPLE] FLOW-EX-01` | `TRG-EX-01` | `orchestrator` | `NB_00_ORCHES_SLV_TO_GLD` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §3`, `docs/context/02_NAMING_CONVENTION.md §2` | Chọn luồng bằng tham số `p_pl_name` |
| `[EXAMPLE] FLOW-EX-02` | `TRG-EX-01` | `load_mode` | `RECOMPUTE` | | `CONTEXT_STATED` | `docs/context/CTRL_TABLES_CONTEXT.md §2`, `§3` | Cạnh của luồng tính lại do `NB_00_ORCHES_SLV_TO_GLD` chạy. Cạnh gold chưa được seed (`docs/context/CTRL_TABLES_CONTEXT.md §10`, dòng 08/10) |
| `[EXAMPLE] FLOW-EX-03` | `TRG-EX-01` | `pl_name` | | | `MISSING_EVIDENCE` | `docs/context/02_NAMING_CONVENTION.md §3` | Context chỉ nêu hậu tố nhịp `_1H` là `[PROPOSED]`, chưa nêu tên pipeline. Xem `MGAP-EX-04` |
| `[EXAMPLE] FLOW-EX-04` | `TRG-EX-01` | `cadence` | Hằng giờ | | `CONTEXT_STATED` | `AGENTS.md §7` | Luồng silver → gold POI |
| `FLOW-001` | | | | | | | |

## 3. Bảng nguồn

> 1 dòng = 1 bảng nguồn. `layer` và `lakehouse_schema` theo bảng "Tiền tố bảng theo tầng".
> Grain trả lời câu "1 dòng của bảng ứng với cái gì". Khoá là các cột làm cho mỗi dòng là duy nhất.
> Bảng nguồn ở `bronze`: ghi grain theo `docs/context/01_DATA_MODEL.md §4`, để trống `key_columns` và `key_evidence`. Khoá của bảng đích silver L1 ghi ở mục 5 theo `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` (`docs/context/CTRL_TABLES_CONTEXT.md §5`).
> Bảng nguồn ở tầng khác: grain và khoá là bắt buộc. Chưa có nguồn thì để trống, đặt `MISSING_EVIDENCE` và thêm dòng ở mục 6.

| src_id | layer | lakehouse_schema | src_tbl | grain | grain_evidence | key_columns | key_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] SRC-EX-01` | `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_localization` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §2`, `§6` | Node N4. Notebook node chưa có trong repository |
| `[EXAMPLE] SRC-EX-02` | `bronze` | `lh_vv_bronze.dbo` | `brz_3rd_crawler_poi_stream` | 1 event = 1 tài liệu đầy đủ lúc crawl | `CONTEXT_STATED` | | | `EXISTING` | `docs/context/01_DATA_MODEL.md §4` | Bảng raw. `event_id` có giá trị trùng và không dùng làm khoá (`docs/context/99_PAIN_POINTS.md §2`, D12) |
| `SRC-001` | | | | | | | | | | |

## 4. Bảng đích

> 1 dòng = 1 bảng đích. Tầng và tiền tố theo bảng "Tiền tố bảng theo tầng". Bảng đích tuân theo "Ràng buộc nền tảng".
> Grain và khoá của bảng đích là bắt buộc. Thiếu một trong hai thì yêu cầu liên quan chưa được coi là đã map, và không được ghi tên notebook mới cho bảng đó.

| trg_id | layer | lakehouse_schema | trg_tbl | grain | grain_evidence | key_columns | key_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] TRG-EX-01` | `gold` | `lh_vv_gold.dbo` | `gld_srv_poi_multi_lang` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §7` | Chiếu 1–1 từ N4 |
| `[EXAMPLE] TRG-EX-02` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi` | 1 dòng / địa điểm (`poi_id`) | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | `load_mode` là `DOC`, `src_object` là `$` |
| `[EXAMPLE] TRG-EX-03` | `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_order_item_hotels` | 1 dòng / 1 dòng của bảng Postgres nguồn, bản mới nhất | `CONTEXT_STATED` | `order_id` | `MISSING_EVIDENCE` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.1`, `docs/context/CTRL_TABLES_CONTEXT.md §11` | Context ghi khoá `order_id` kèm "chưa xác nhận PK" (K1). Xem `MGAP-EX-02` |
| `TRG-001` | | | | | | | | | | |

## 5. Mapping cột

> 1 dòng = 1 cột đích. `req_ids` trỏ tới BRD mục 5. `rule_ids` trỏ tới BRD mục 7. `data_type` là kiểu Spark của cột đích (`docs/context/CTRL_TABLES_CONTEXT.md §5`, cột `data_type`).
> Ô bắt buộc ở mọi tầng: `req_ids`, `src_column_or_json_path`, `trg_id`, `trg_column`, `data_type`, `is_key`. `src_id` không bắt buộc.
> Ngoại lệ cột kỹ thuật lúc ghi: khi `trg_column` là `created_at` hoặc `updated_at` và giá trị được gán lúc ghi, `src_column_or_json_path` được để trống. `note` ghi điều này. `evidence_status` phải có `USER_STATED` và `context_ref` trỏ `USER_INPUT` hoặc câu hỏi đã trả lời. Ô trống đó không làm dòng thành thiếu nguồn. Kiểm tra nền tảng PC-09 vẫn áp dụng.
> Silver L1: bắt buộc thêm `src_object`, `convert_rule`, và `key_order` khi `is_key` là `true`. 1 dòng ứng với 1 dòng của `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` và theo luật cấu hình ở `docs/context/CTRL_TABLES_CONTEXT.md §5`. `rule_ids` để trống vì silver L1 không có rule nghiệp vụ.
> Silver L2: `src_object`, `convert_rule`, `key_order` để trống. Rule nghiệp vụ tạo ra giá trị của cột ghi ở `rule_ids`.
> Gold: `src_object`, `convert_rule`, `key_order`, `rule_ids` để trống, theo "Ràng buộc nền tảng".
> `evidence_status` của dòng: khi mọi ô bắt buộc đã có nguồn, ghi giá trị theo nguồn và ghi đủ nguồn ở `context_ref`. Còn ô bắt buộc chưa có nguồn: để trống ô đó, đặt `MISSING_EVIDENCE`, ghi tên ô ở `note` và thêm dòng ở mục 6.

| col_id | req_ids | src_id | src_object | src_column_or_json_path | trg_id | trg_column | data_type | convert_rule | is_key | key_order | rule_ids | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] COL-EX-01` | `BR-EX-01` | `SRC-EX-01` | | `poi_id` | `TRG-EX-01` | `poi_id` | | | `true` | | | `MISSING_EVIDENCE` | `docs/context/01_DATA_MODEL.md §6`, `§7` | `data_type` trống: context không nêu kiểu của cột. Xem `MGAP-EX-01` |
| `[EXAMPLE] COL-EX-02` | `BR-EX-01` | `SRC-EX-01` | | `lang` | `TRG-EX-01` | `lang` | | | `true` | | | `MISSING_EVIDENCE` | `docs/context/01_DATA_MODEL.md §6`, `§7` | `data_type` trống: context không nêu kiểu của cột. Xem `MGAP-EX-01` |
| `[EXAMPLE] COL-EX-03` | `BR-EX-01` | `SRC-EX-01` | | | `TRG-EX-01` | `poi_name` | | | `false` | | | `MISSING_EVIDENCE` | `docs/context/01_DATA_MODEL.md §6`, `§7` | `src_column_or_json_path` và `data_type` trống. Context liệt kê `poi_name` ở gold nhưng không liệt kê cột của `slv_poi_localization`. Xem `MGAP-EX-01`, `MGAP-EX-03` |
| `[EXAMPLE] COL-EX-04` | `BR-EX-02` | `SRC-EX-02` | `$` | `_doc.source_name,_doc.source_id` | `TRG-EX-02` | `poi_id` | `string` | `HASH_MD5_UUID` | `true` | `1` | | `CONTEXT_STATED` | `docs/context/CTRL_TABLES_CONTEXT.md §5`, `notebooks/NB_CREATE_DDL.ipynb` `POI_ID`, `TABLE_CONFIGS_3P`, `flatten_table_configs` | Notebook khai báo `POI_ID` với `path` `_doc.source_name,_doc.source_id`, `type` `string`, `rule` `HASH_MD5_UUID`, và `key` của `slv_3p_poi` là `poi_id`. `flatten_table_configs` đặt `key_order` theo vị trí trong `key`, bắt đầu từ 1 |
| `COL-001` | | | | | | | | | | | | | | |

## 6. Mục thiếu evidence

> 1 dòng = 1 sự kiện còn thiếu trong file này. `blocks` ghi ID bị chặn. `PROBE` ghi tiêu chí đạt và không đạt bằng lời, không viết code probe.

| gap_id | blocks | missing_fact | why_repo_cannot_answer | resolution_type | pass_fail_criterion | note |
|---|---|---|---|---|---|---|
| `[EXAMPLE] MGAP-EX-01` | `COL-EX-01`, `COL-EX-02`, `COL-EX-03` | Kiểu dữ liệu của `poi_id`, `lang`, `poi_name` ở `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | Context nêu grain, khoá và tên cột của bảng nhưng không nêu kiểu dữ liệu (`docs/context/01_DATA_MODEL.md §7`) | `PROBE` | Đạt: schema thật của bảng trên Fabric DEV có đủ 3 cột và cho biết kiểu của từng cột. Không đạt: thiếu bảng hoặc thiếu cột | |
| `[EXAMPLE] MGAP-EX-02` | `TRG-EX-03` | Khoá chính của `slv_pn_order_item_hotels` | Context ghi khoá `order_id` kèm "chưa xác nhận PK" (K1). Việc chốt khoá còn chờ team nguồn (`docs/context/CTRL_TABLES_CONTEXT.md §11`) | `EXTERNAL` | Đạt: xác nhận của team nguồn được ghi vào một file trong repository, rồi `key_evidence` đổi sang `CONTEXT_STATED`. Không đạt: chưa có xác nhận | |
| `[EXAMPLE] MGAP-EX-03` | `COL-EX-03` | Cột của `slv_poi_localization` chứa tên POI | Context không liệt kê cột của N4. Notebook node N4 chưa có trong repository (`docs/context/01_DATA_MODEL.md §6`) | `PROBE` | Đạt: schema thật của `lh_vv_silver.dbo.slv_poi_localization` có đúng 1 cột tên POI. Không đạt: không có cột nào, hoặc có hơn 1 cột ứng viên | |
| `[EXAMPLE] MGAP-EX-04` | `FLOW-EX-03` | Tên pipeline của luồng tính lại hằng giờ ghi `gld_srv_poi_multi_lang` | Context chỉ nêu hậu tố nhịp `_1H` là `[PROPOSED]` (`docs/context/02_NAMING_CONVENTION.md §3`) | `USER_ANSWER` | Đạt: tên pipeline đã có được ghi trong một file của repository, hoặc người dùng chốt tên mới `[PROPOSED]` có hậu tố nhịp khớp `CADENCE_RE` (`docs/context/02_NAMING_CONVENTION.md §3`). Không đạt: chưa có tên | |
| `MGAP-001` | | | | | | |

## 7. Mâu thuẫn trong repository

> Ghi cả hai nguồn và nội dung từng nguồn. Không tự chọn bên nào. Mỗi dòng cần 1 câu hỏi ở mục 8.

| conflict_id | blocks | item | source_a | source_b | note |
|---|---|---|---|---|---|
| `[EXAMPLE] MCONF-EX-01` | | Tên activity notebook trong `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` | `AGENTS.md §7`: `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` | `docs/context/CTRL_TABLES_CONTEXT.md §2`: `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` | Không tự chọn. Xem `MQ-EX-03` |
| `MCONF-001` | | | | | |

## 8. Câu hỏi mở

> 1 dòng = 1 câu hỏi cho người dùng, chủ nghiệp vụ hoặc team nguồn. `blocks` chứa `gap_id` hoặc `conflict_id` liên quan. Khi có câu trả lời, ghi `answer`, `answered_on` và làm theo bước 10 của "Cách điền".

| q_id | blocks | question | resolution_type | answer | answered_on |
|---|---|---|---|---|---|
| `[EXAMPLE] MQ-EX-01` | `MGAP-EX-02` | Team nguồn đã xác nhận khoá chính của bảng Postgres nguồn của `slv_pn_order_item_hotels` chưa? | `EXTERNAL` | | |
| `[EXAMPLE] MQ-EX-02` | `MGAP-EX-04` | Luồng tính lại hằng giờ ghi `gld_srv_poi_multi_lang` đã có pipeline chưa, và `pl_name` là gì? | `USER_ANSWER` | | |
| `[EXAMPLE] MQ-EX-03` | `MCONF-EX-01` | Tên activity nào khớp JSON trong `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/`, và tài liệu nào cần sửa? | `USER_ANSWER` | | |
| `MQ-001` | | | | | |
