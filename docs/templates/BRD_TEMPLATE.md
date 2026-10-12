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
| `brd_id` | `BRD-<task_id>` |
| `task_id` | `<task_id>` |
| `mapping_id` | `MAP-<task_id>` |
| `version` | `<số nguyên từ 1>` |
| `doc_status` | `DRAFT` hoặc `READY_FOR_ANALYSIS` |
| `owner_role` | `<vai trò hoặc nhóm phụ trách; không ghi tên người, email, số điện thoại>` |
| `updated_on` | `<YYYY-MM-DD>` |

## 2. Bối cảnh và mục tiêu

> Viết ngắn: vấn đề nghiệp vụ, ai cần dữ liệu, dùng dữ liệu để làm gì. Không mô tả thiết kế kỹ thuật.

`[EXAMPLE]` Backend PostgreSQL nhận dữ liệu POI từ gold qua đồng bộ theo `updated_at` (`docs/context/01_DATA_MODEL.md §1`, `§3`). Phần minh hoạ của mẫu này dùng một yêu cầu giả định: cần tên POI theo từng ngôn ngữ vi, en, ko trên `gld_srv_poi_multi_lang` (`docs/context/01_DATA_MODEL.md §7`).

`<Mô tả bối cảnh và mục tiêu>`

## 3. Phạm vi

> `scope` là quyết định của người dùng. `evidence_status` và `context_ref` chỉ nguồn của bảng, luồng hoặc ràng buộc có thật được nêu trong `description`.

| scope_id | scope | description | evidence_status | context_ref |
|---|---|---|---|---|
| `[EXAMPLE] SCOPE-EX-01` | `IN` | Tên POI theo ngôn ngữ trên `gld_srv_poi_multi_lang` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §7` |
| `[EXAMPLE] SCOPE-EX-02` | `OUT` | Bảng `poi_*` cũ và chuỗi NB_00 cũ. Hai phần này giữ nguyên và chạy song song tới cutover | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §1`, `§9` |
| `SCOPE-001` | | | | |

## 4. Bên sử dụng dữ liệu

| consumer_id | consumer | reads_from | sync_rule | evidence_status | context_ref |
|---|---|---|---|---|---|
| `[EXAMPLE] CSM-EX-01` | PostgreSQL backend | `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | Đồng bộ theo `updated_at`. `updated_at` chỉ đổi khi `row_hash` đổi | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §1`, `§3`, `§7`, `§10` |
| `CSM-001` | | | | | |

## 5. Yêu cầu nghiệp vụ

> 1 dòng = 1 yêu cầu kiểm chứng được. `trg_tbl`, `grain` và `key_columns` khớp Mapping mục 4 theo "Liên kết giữa hai file".
> `rule_ids` trỏ tới mục 7. `id_rule_ids` trỏ tới mục 8. `consumer_id` để trống khi yêu cầu không có bên sử dụng trực tiếp.
> Chưa biết grain hoặc khoá thì để trống, đặt `MISSING_EVIDENCE` và thêm dòng ở mục 11.

| req_id | priority | statement | consumer_id | trg_tbl | trg_name_status | grain | grain_evidence | key_columns | key_evidence | rule_ids | id_rule_ids | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] BR-EX-01` | `MUST` | `gld_srv_poi_multi_lang` chỉ giữ POI có đủ vi, en, ko, 1 dòng / (`poi_id`, `lang`), có cột `poi_name` | `CSM-EX-01` | `gld_srv_poi_multi_lang` | `EXISTING` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | `RULE-EX-01`, `RULE-EX-02` | | `docs/context/01_DATA_MODEL.md §7` | |
| `[EXAMPLE] BR-EX-02` | `MUST` | `poi_id` của địa điểm 3rd-party tính theo công thức ở `ID-EX-01` từ `source_name` và `source_id`, và không chứa ngôn ngữ | | `slv_3p_poi` | `EXISTING` | 1 dòng / địa điểm (`poi_id`) | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | | `ID-EX-01` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §5.2`, `§8`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | |
| `[EXAMPLE] BR-EX-03` | `SHOULD` | Yêu cầu giả định để minh hoạ thiếu nguồn: có `short_description` theo ngôn ngữ cho POI partner trên `gld_srv_poi_multi_lang` | `CSM-EX-01` | `gld_srv_poi_multi_lang` | `EXISTING` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | | | `docs/context/01_DATA_MODEL.md §7` | Nguồn chưa có. Xem `DS-EX-03`, `BGAP-EX-02` |
| `BR-001` | | | | | | | | | | | | | |

## 6. Nguồn dữ liệu

> 1 dòng = 1 bảng nguồn cho các yêu cầu ở `req_ids`. Mỗi yêu cầu ở mục 5 có ít nhất 1 dòng. `src_tbl` khớp Mapping mục 3 theo "Liên kết giữa hai file".
> `src_columns` chỉ ghi cột đã có nguồn. Cột chi tiết và mục thiếu evidence của cột ghi ở Mapping mục 5 và mục 6.
> Chưa biết bảng nguồn thì để trống, đặt `MISSING_EVIDENCE` và thêm dòng ở mục 11.

| ds_id | req_ids | layer | lakehouse_schema | src_tbl | src_columns | name_status | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] DS-EX-01` | `BR-EX-01` | `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_localization` | `poi_id`, `lang` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §6`, `§7` | Cột tên POI của N4 xem Mapping `COL-EX-03`, `MGAP-EX-03` |
| `[EXAMPLE] DS-EX-02` | `BR-EX-02` | `bronze` | `lh_vv_bronze.dbo` | `brz_3rd_crawler_poi_stream` | `source_name`, `source_id` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §4`, `docs/context/CTRL_TABLES_CONTEXT.md §5` | |
| `[EXAMPLE] DS-EX-03` | `BR-EX-03` | | | | | | `MISSING_EVIDENCE` | | Context nêu mô tả 3P là NULL ở N4 nhưng không nêu nguồn mô tả của POI partner (`docs/context/01_DATA_MODEL.md §6`). Xem `BGAP-EX-02` |
| `DS-001` | | | | | | | | | |

## 7. Rule nghiệp vụ

> Rule là quyết định nghiệp vụ: phân loại, chọn nguồn, fallback, lọc. `evidence_status` là nguồn của `statement`.
> `layer` chỉ nhận `silver_l2` hoặc `ref`. `rule_home` ghi bảng chứa rule hoặc node áp rule. Chưa biết thì để trống, đặt `MISSING_EVIDENCE` ở `rule_home_evidence` và thêm dòng ở mục 11.
> Ngoại lệ không có bảng rule riêng: khi người dùng chốt rule không nằm ở bảng riêng, `rule_home` ghi đúng `TEMPLATE_EXCEPTION_NO_RULE_TABLE`. `rule_home_evidence` là `USER_STATED` và `context_ref` trỏ `USER_INPUT` hoặc câu hỏi đã trả lời. Giá trị đó là `rule_home` đã biết cho mục phủ sóng. Kiểm tra nền tảng PC-03 vẫn báo vi phạm vì giá trị không bắt đầu bằng `slv_poi_` hoặc `ref_`.

| rule_id | statement | evidence_status | layer | rule_home | rule_home_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] RULE-EX-01` | POI chỉ lên gold khi có đủ vi, en, ko | `CONTEXT_STATED` | `silver_l2` | | `MISSING_EVIDENCE` | | `docs/context/01_DATA_MODEL.md §2`, `§6.1`, `§7` | Context nêu gold lọc theo cờ silver `has_required_langs` ở cả 3 bảng gold (`§7`), cờ đủ ngôn ngữ là quyết định của silver L2 (`§2`), và danh sách ngôn ngữ bắt buộc ở `ref_lang_policy.is_required` (`§6.1`). Context không nêu bảng chứa cờ. Xem `BGAP-EX-01` |
| `[EXAMPLE] RULE-EX-02` | Thiếu tên en thì dùng tên vi bỏ dấu. Thiếu tên ko thì chép tên vi | `CONTEXT_STATED` | `ref` | `ref_lang_policy` (`fallback_lang`, `fallback_method`) | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §6`, `§6.1` | Fallback tên áp ở silver L2 và không copy mô tả (`docs/context/01_DATA_MODEL.md §6`, N4) |
| `RULE-001` | | | | | | | | |

## 8. Định danh

> `poi_id` không bao giờ chứa ngôn ngữ. Không dùng `poi_uid` (`AGENTS.md §9`). Định danh mới cần công thức và nguồn. Chưa có thì để trống, đặt `MISSING_EVIDENCE` và thêm dòng ở mục 11.

| id_rule_id | identifier | formula | applies_to | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|
| `[EXAMPLE] ID-EX-01` | `poi_id` (3rd-party) | `uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`) | `slv_3p_poi` và các bảng `slv_3p_poi_*` | `CONTEXT_STATED` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §8`, `docs/context/CTRL_TABLES_CONTEXT.md §5` | |
| `[EXAMPLE] ID-EX-02` | `poi_id` (partner) | `uuid_format(md5('partner_portal' \|\| business_service_id))` | Chưa có. Notebook hiện tại chưa áp dụng | `CONTEXT_STATED` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §8` | Yêu cầu dùng định danh này cần 1 câu hỏi ở mục 13 |
| `ID-001` | | | | | | |

## 9. Yêu cầu phi chức năng

| nfr_id | item | value | evidence_status | context_ref | note |
|---|---|---|---|---|---|
| `[EXAMPLE] NFR-EX-01` | SLA từ nguồn tới serving | 30–60 phút | `CONTEXT_STATED` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §1` | |
| `[EXAMPLE] NFR-EX-02` | Nhịp silver → gold POI | Hằng giờ | `CONTEXT_STATED` | `AGENTS.md §9` | |
| `NFR-001` | | | | | |

## 10. Tiêu chí nghiệm thu

> Mỗi tiêu chí kiểm tra được bằng repository hoặc bằng probe chỉ đọc. Main viết probe, người dùng chạy trên Fabric DEV (`AGENTS.md §8`).
> `evidence_status` và `context_ref` chỉ nguồn của bảng, khoá, grain hoặc rule mà tiêu chí dựa vào.

| ac_id | req_ids | criterion | how_to_check | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|
| `[EXAMPLE] AC-EX-01` | `BR-EX-01` | Không có 2 dòng cùng (`poi_id`, `lang`) trong `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | Probe chỉ đọc đếm số nhóm trùng (`poi_id`, `lang`). Đạt: 0 nhóm | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §7`, `AGENTS.md §8` | Grain và khoá lấy từ `docs/context/01_DATA_MODEL.md §7` |
| `AC-001` | | | | | | |

## 11. Mục thiếu evidence

> 1 dòng = 1 sự kiện còn thiếu trong file này. `blocks` ghi ID bị chặn. `PROBE` ghi tiêu chí đạt và không đạt bằng lời, không viết code probe.

| gap_id | blocks | missing_fact | why_repo_cannot_answer | resolution_type | pass_fail_criterion | note |
|---|---|---|---|---|---|---|
| `[EXAMPLE] BGAP-EX-01` | `RULE-EX-01` | Bảng silver L2 chứa cờ `has_required_langs` | Context nêu tên cờ nhưng không nêu bảng chứa cờ (`docs/context/01_DATA_MODEL.md §7`, `docs/context/02_NAMING_CONVENTION.md §5.1`) | `PROBE` | Đạt: đúng 1 bảng `lh_vv_silver.dbo.slv_poi_*` có cột `has_required_langs`. Không đạt: không có bảng nào, hoặc có hơn 1 bảng | |
| `[EXAMPLE] BGAP-EX-02` | `DS-EX-03`, `BR-EX-03` | Bảng và cột nguồn của mô tả theo ngôn ngữ cho POI partner | Context nêu mô tả 3P là NULL ở N4 và liệt kê đầu vào của N4, nhưng không nêu nguồn mô tả của partner (`docs/context/01_DATA_MODEL.md §6`) | `USER_ANSWER` | Đạt: người dùng chọn bảng nguồn, rồi bảng và cột đó có `CONTEXT_STATED` hoặc `TASK_EVIDENCE`. Không đạt: chưa chọn được nguồn | |
| `BGAP-001` | | | | | | |

## 12. Mâu thuẫn trong repository

> Ghi cả hai nguồn và nội dung từng nguồn. Không tự chọn bên nào. Mỗi dòng cần 1 câu hỏi ở mục 13.

| conflict_id | blocks | item | source_a | source_b | note |
|---|---|---|---|---|---|
| `BCONF-001` | | | | | |

## 13. Câu hỏi mở

> 1 dòng = 1 câu hỏi cho người dùng, chủ nghiệp vụ hoặc team nguồn. `blocks` chứa `gap_id` hoặc `conflict_id` liên quan. Khi có câu trả lời, ghi `answer`, `answered_on` và làm theo bước 12 của "Cách điền".

| q_id | blocks | question | resolution_type | answer | answered_on |
|---|---|---|---|---|---|
| `[EXAMPLE] BQ-EX-01` | `BGAP-EX-02` | Mô tả theo ngôn ngữ của POI partner phải lấy từ nguồn partner nào? | `USER_ANSWER` | | |
| `BQ-001` | | | | | |
