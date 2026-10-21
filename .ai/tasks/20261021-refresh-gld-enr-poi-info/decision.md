# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Nguồn info | Schema gold là lh_vv_gold.enr. Nguồn info là lh_vv_silver.dbo.slv_poi_entity_non_enrich. Bỏ slv_pn_poi khỏi nguồn của ba bảng này. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-02 | Coordinate | gld_enr_poi_coordinate: bỏ khỏi xử lý. Tắt cạnh ctrl tới bảng này. Notebook NB_ENR_POI_COORDINATE không còn được pipeline gọi. Không DROP bảng vì request không cho phép xóa bảng. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-03 | Review | gld_enr_poi_review: giữ nguyên logic NB_ENR_POI_REVIEW và hợp đồng cột. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-04 | Cột entity | Cột op không đưa sang gold: row_hash, created_at, updated_at, deleted_at. Cột nghiệp vụ của entity, gồm website_url và các cột estimate, vẫn lấy. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-05 | Cột bỏ | Bỏ khỏi gld_enr_poi_info: subcategory_tags, short_address, best_time_from_month, best_time_to_month, best_time_type. canonical_candidate chỉ đi vào best_time theo mục 1.2 của mapping_gld_enr_poi_info.md. Không tạo lại cột best_time_type. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-06 | Địa danh | district lấy ward, destination_name lấy city của entity. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-07 | Cột google | Năm cột rating, user_rating_count, price_level, opening_hours_text, review_json chỉ áp rule google hiện có khi source_name = google. Đổi tên userRatingCount thành user_rating_count và priceLevel thành price_level. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-08 | Cost đủ giá | cost chỉ tính khi có đủ price_min và price_max: ROUND((price_min + price_max) / 2). Không gọi LLM. cost_method và cost_confidence không phải cột gold: trong mapping gld_enr_poi_info và xử lý cũ đều không có. | mapping_place_type.md mục 1.9.3; user 2026-10-21 | 2026-10-21 |
| D-09 | JSON hiển thị | time_to_spend, best_time, cost_vnd làm theo mục 1.1, 1.2, 1.3 và mục 2 của mapping_gld_enr_poi_info.md. cost null thì JSON null, không phải object có value null. | request.md Cách hiểu đã chốt | 2026-10-21 |
| D-10 | Thiếu giá | Thiếu price_min hoặc price_max thì cost null và cost_vnd là JSON null. | user 2026-10-21 | 2026-10-21 |
| D-11 | Làm tròn 1.3 | Làm tròn về phần nghìn. Ví dụ 545899 làm tròn thành 546000; 5455 làm tròn thành 5000. | user 2026-10-21 | 2026-10-21 |
| D-12 | service_flag | Join amenity và join price không được nhân dòng gold. Cột gold service_flag là một mảng JSON; value trong JSON không bị trùng. Sort chữ tăng dần, bỏ null, POI không có value thì []. | user 2026-10-21 phương án B | 2026-10-21 |
| D-13 | types | Giữ tên types, giá trị lấy từ types_json. Không tạo thêm cột types_json. | user 2026-10-21 phương án B | 2026-10-21 |
| D-14 | destination_context | Bỏ cột destination_context. | user 2026-10-21 phương án A | 2026-10-21 |
| D-15 | cost_vnd chữ | cost_vnd là object JSON, key theo mục 2. Value dạng Từ 546,000đ khi số đã làm tròn là 546000. | user 2026-10-21; mapping_gld_enr_poi_info.md mục 1 | 2026-10-21 |
| D-16 | time_to_spend chữ | null hoặc ≤ 0: Không cố định, xét trước các nhánh khác. accommodation và giá trị > 0: ceil(avg_range_min / 1440) rồi {n} ngày. tour_n_activities và > 420: Cả ngày. < 60: {n} phút. Đúng 60: 1 tiếng. > 60: {h} tiếng khi dư 0 phút, còn lại {h} tiếng {m} phút. Sector ngoài mục 2 dùng nhãn other. Không thêm cột time_to_spend_minutes. | user 2026-10-21 phương án A | 2026-10-21 |
| D-17 | Giờ và cột không google | source_name khác google: rating, user_rating_count, price_level, review_json là null. opening_hours_text của partner lấy từ slv_pn_business_service_i18ns.amentities. Join bằng hash business_service_id + 'partner' như poi_id partner của slv_poi_entity_non_enrich: uuid_md5(business_service_id, 'partner') = entity.poi_id. Chỉ locale = vi. Lấy key operating_hours trong policies; không có thì null. Nguồn khác google và partner thì opening_hours_text null. | user 2026-10-21 | 2026-10-21 |
| D-18 | DROP info trên DEV | Đây là môi trường dev và đang phát triển. Xóa bảng gld_enr_poi_info và chạy lại như lần init đầu tiên. Không DROP gld_enr_poi_coordinate. Không dùng CREATE OR REPLACE. | user 2026-10-21 | 2026-10-21 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- `tests/test_poi_entity_contract.py` `test_create_ddl_patch`: assertion hai cell cuối đổi từ `entwebmd`/`entwebpy` sang `enrinfomd`/`enrinfopy`. Cell website vẫn liền nhau và đứng trước patch info. File này không có trong Edit list; suite đầy đủ fail nếu không sửa. Đã thêm vào `scope.files`.
- SPARK-001: Code A chỉ reverse-diff amenity. Review round 1 yêu cầu cùng cách cho rating, price, hours, review. `_role_keys` dùng chung năm vai trò. Entity vẫn chỉ `ctx.changed` vì APPEND không phát dòng đã rời spine.
- STATE-001: Code B để verify sau UPDATE phát hiện cạnh `EDGES_ON` đang tắt. Cell nay kiểm tra trước INSERT/UPDATE và raise. Không thêm `SET is_active = 1`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-001 | P1 | fixed | `_role_keys` lấy poi_id biến mất khỏi snapshot live của rating, price, hours, review và amenity. Không baseline thì trả cả spine. `ctx.changed` vẫn là `current.subtract(old)`. | |
| STATE-001 | P1 | fixed | `enrinfopy` đọc cạnh `EDGES_ON` trước INSERT/UPDATE. Dòng đã có mà không đúng một dòng `is_active = 1` thì raise và không ghi cạnh. Cell không tự bật cạnh (I7). | |
| SQL-001 | P1 | rejected-false-positive | Probe DEV `evidence/results/sql-001-sql-002.txt` (2026-10-21): câu SQL-001 trả 0 dòng. Không có `poi_id` null hoặc trùng trên `slv_poi_entity_non_enrich`. Node vẫn chặn bằng `pk_duplicate` nếu sau này có trùng. | |
| SQL-002 | P1 | rejected-false-positive | Cùng file kết quả: câu SQL-002 trả 0 dòng. Không có `business_service_id` null hoặc nhiều hơn một dòng `locale = vi` chưa deleted. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- D-17 và D-18 đã chốt 2026-10-21. Join i18n bằng hash `business_service_id` + `partner`, chỉ `locale = vi`. DEV: xóa `gld_enr_poi_info` rồi tạo lại như init.
- 2026-10-21: user duyệt thêm một vòng review. `review_plan.extra_round_approved_on = 2026-10-21`.
- 2026-10-21: user xác nhận runtime DEV đạt và task done. `gates.runtime` chuyển `pass`. Status chuyển `ready_to_merge`.

## Lịch sử quyết định

### 2026-10-21 — Rà impact trước architecture

Nguồn và hợp đồng hiện tại:

- `NB_ENR_POI_INFO` cell `build`: spine `slv_3p_poi`, left join `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, review top 20. Không đọc `slv_pn_poi`. `time_to_spend` đang là `Không cố định`. `best_time_type`, `best_time_from_month`, `best_time_to_month`, `cost` đang null. Tên cột còn `userRatingCount`, `priceLevel`.
- `NB_ENR_POI_COORDINATE` đọc `slv_3p_poi`, `slv_3p_poi_address`, `slv_pn_poi`. `NB_ENR_POI_REVIEW` đọc `slv_3p_poi_review`, pk `review_id`. Review giữ nguyên. Coordinate không sửa logic.
- Hợp đồng cột info, coordinate, review nằm ở `NB_SETUP_INITIAL_DDL` cell `init_tables` và `NB_CREATE_DDL` cell `enrddlpy`. `tests/test_enr_poi_contract.py` khóa `INFO_COLS` và 13 cạnh. `tests/test_initial_ddl_contract.py` khóa ba fq gold enr.

Cạnh `PL_VV_TRANS_SLV_TO_ENR_15P` trong `NB_SETUP_INITIAL_DDL` cell `init_seed_ctrl`, `is_active = 1`:

- Info: `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_review`.
- Coordinate: `slv_3p_poi`, `slv_3p_poi_address`, `slv_pn_poi`. `nb_name = NB_ENR_POI_COORDINATE`, priority 2.
- Review: `slv_3p_poi_review`.

`CTRL_TABLES_CONTEXT.md` không liệt kê các cạnh enr này. Cột `is_active`: 0 tắt cạnh. Seed initial chỉ `MERGE` khi chưa có dòng. Cell `enrddlpy` không sửa. Tắt cạnh coordinate và thay cạnh info: sửa danh sách seed tại chỗ, thêm một cell patch `NB_CREATE_DDL` cập nhật dòng đã có. Không DROP bảng. JSON `pipelines/PL_VV_TRANS_SLV_TO_ENR_15P` gọi `NB_00_ORCHES_SLV_TO_ENR_15P` qua `nb_orches_id`, không gọi thẳng `NB_ENR_POI_COORDINATE`.

Cột nghiệp vụ `slv_poi_entity_non_enrich` trong `TABLE_SPECS`: `poi_id`, `source_name`, `source_id`, `language_code`, `poi_name`, `poi_name_normalized`, `types_json`, `operating_status`, `primary_type`, `website_url`, `house_number`, `street`, `ward`, `city`, `full_address`, `lat`, `lng`, `business_sector`, `business_category`, `business_category_vi`, `category_group`, `range_low_min`, `range_high_min`, `avg_range_min`, `candidate_best_time_code`, `canonical_candidate`. Bốn cột op không sang gold. `created_at` và `updated_at` của chính bảng gold vẫn do lib gán, không copy từ entity.

`slv_poi_amenity` grain (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`), có `service_flags`. `slv_3p_poi_price` trong data model là DOC, khóa `poi_id`, cột `price_min`, `price_max`. Join price không được nhân dòng; chưa thấy grain amenity một dòng mỗi `poi_id`.

Mục 1.1 và 1.2 của `mapping_gld_enr_poi_info.md` có formatter. Mục 1.3 chỉ có tiêu đề. Mục 1.9.3 có công thức khi đủ hai giá và một nhánh LLM; D-08 cấm LLM. Bảng mục 1 của mapping vẫn có dòng `best_time_type`; D-05 không tạo lại cột đó.

Signal `data_model_change`: sau khi D-10, D-11, D-12 chốt, viết `model-design.md` bằng `run-author --kind model` rồi mới `waiting_architecture`. Không probe ở triage.

### 2026-10-21 — Chốt D-08, D-10, D-11, D-12

`cost_method` và `cost_confidence` là hai nhãn đi kèm `deterministic_cost_vnd` trong `mapping_place_type.md` mục 1.9.3 (`observed_average`, `high`, hoặc nhánh LLM). `mapping_gld_enr_poi_info.md` không có hai tên này. `NB_ENR_POI_INFO` không select hai cột này. Không thêm hai cột đó lên gold. Cột `cost` khi đủ hai giá vẫn là `ROUND((price_min + price_max) / 2)`.

D-10: thiếu `price_min` hoặc `price_max` thì `cost` null và `cost_vnd` là JSON null.

D-11 áp cho số đưa vào `cost_vnd`, sau khi đã có `cost` theo D-08. Công thức khớp hai ví dụ, số VND dương: `1000 * round_half_up(cost / 1000)`. `545899 / 1000 = 545.899` thành `546000`. `5455 / 1000 = 5.455` thành `5000`. Phần thập phân từ 0.5 làm tròn lên.

D-12: một dòng gold mỗi `poi_id`. Cột `service_flag` là mảng JSON các value lấy từ `slv_poi_amenity.service_flags`, bỏ value trùng. Seed amenity: mỗi dòng một chuỗi hoặc null, tập `Food/service`, `Suitability`, `Payment`, `Parking`, `Accessibility`, `Derived amenities`.

`run-author --kind model` đã ghi `model-design.md` (claude-opus-5-5, effort medium). Conflicts 1, 5, 10, 11 không mở quyết định mới: gold lấy `poi_id` sẵn có trên entity; D-04 và D-06 giữ cả `ward`/`district` và `city`/`destination_name`; đổi cột vật lý để Architect xử lý; D-05 không tạo `best_time_type`.

### 2026-10-21 — Chốt D-12 đến D-17

D-13: cột gold `types`, giá trị `entity.types_json`. D-14: bỏ `destination_context`. D-15: `{"<nhãn mục 2>":"Từ 546,000đ"}` với dấu phẩy ngăn nghìn. D-16 ghi nguyên các câu chữ của phương án A. D-12 phương án B: sort chữ tăng dần, bỏ null, không có value thì `[]`.

`slv_pn_business_service_i18ns` không có cột `poi_id`. Registry `TABLE_CONFIGS`: khóa (`business_service_id`, `locale`), cột `amentities` đúng chính tả nguồn. `NB_SLV_POI_ENTITY_NON_ENRICH` đặt `source_id = id` và `poi_id = uuid_md5(id, 'partner')`, `language_code = vi`. Join D-17 ban đầu ghi `source_id = business_service_id`. Câu này bị thay bởi mục «D-17 join hash và D-18 DROP».

`canonical_candidate` vẫn là cột gold theo D-04. D-05 chỉ cấm tạo `best_time_type`. `best_time` vẫn lấy từ cột này. Sector null hoặc ngoài mục 2 dùng dòng `other` cho cả ba nhãn. `canonical_candidate` không đúng dạng `Month {from}-{to}` với hai tháng 1–12 thì `best_time` là `Quanh năm`. `cost_vnd`, `best_time`, `time_to_spend`, `service_flag` là STRING. `cost` null thì chuỗi JSON `null`, không phải SQL NULL. Spine entity và amenity chỉ lấy dòng `deleted_at` null.

### 2026-10-21 — Architecture PASS, dừng tại D-18

`run-gate` architecture vòng 1 PASS với `CREATE OR REPLACE`. User từ chối phương án đó.

### 2026-10-21 — D-17 join hash và D-18 DROP

Join partner: `uuid_md5(slv_pn_business_service_i18ns.business_service_id, 'partner') = slv_poi_entity_non_enrich.poi_id`, cùng hàm với `_partner` trong `NB_SLV_POI_ENTITY_NON_ENRICH`. Chỉ dòng `locale = vi`. `operating_hours` vẫn là `$.policies.operating_hours`.

D-18: môi trường dev đang phát triển. Xóa `lh_vv_gold.enr.gld_enr_poi_info` rồi tạo lại theo định nghĩa init. Không xóa `gld_enr_poi_coordinate`. Vòng architecture 1 không còn hiệu lực cho bước migration. Seed `Month 11–4` vẫn cần nhận en dash khi parse `best_time`.

### 2026-10-21 — Probe SQL-001 và SQL-002

User chạy probe trên Fabric DEV. Cả hai câu trả 0 dòng. Kết quả: `evidence/results/sql-001-sql-002.txt`. SQL-001 và SQL-002 là `rejected-false-positive`. `rounds.review` đang ở cap 2, nên vòng review xác nhận disposition cần user duyệt thêm một vòng.

### 2026-10-21 — User chấp nhận runtime

User xác nhận các kiểm tra DEV còn lại đúng kỳ vọng: hai `count(*)` đều 65, trùng `poi_id` là 0 dòng, đúng 7 watermark info, history coordinate đứng trước `2026-10-21T03:58:42Z`. Cùng P-4, P-6, P-7 và RUN 2 `NO_DATA`, user xác nhận task done. `gates.runtime` = `pass`.
