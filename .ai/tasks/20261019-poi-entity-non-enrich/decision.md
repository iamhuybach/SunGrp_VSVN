# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Impact bronze → silver | Đã rà trước architecture. Chi tiết ở lịch sử 2026-10-19. Architecture phải xử lý đúng các reader, cạnh và seed đó. | Rà repo trong triage | 2026-10-19 |
| D2 | poi_id partner | md5(concat(id, 'partner')) rồi chèn gạch 8-4-4-4-12 | Người dùng, 2026-10-19 | 2026-10-19 |
| D3 | category_group dòng partner | Xử lý category_group của partner bằng cách lấy ref_dictionary_place_type place_type=primary_type, lấy được business_category. JOIN tiếp ref_dictionary_place_type qua ref_dictionary_place_type.business_category=business_category (lấy từ bước 1) và source_name = google để lấy được category_group. | Người dùng, 2026-10-19 | 2026-10-19 |
| D4 | Tên cột trạng thái trên entity | ghi vào operating_status, không thêm cột | Người dùng, 2026-10-19 | 2026-10-19 |
| D5 | Tên bảng i18n | Dùng lh_vv_silver.dbo.slv_pn_business_service_i18ns. Không tạo slv_pn_business_services_i18ns. | request.md mục 5; NB_CREATE_DDL target_table | 2026-10-19 |
| D6 | Cột bỏ trên entity | Chỉ bỏ subcategory_tags_json. Không bỏ thêm cột. | request.md mục 5 | 2026-10-19 |
| D7 | category_group dòng google | Lấy category_group của place_type mà entity đã resolve: primary_type, rồi phần tử types_json khớp đầu tiên. Không thêm rule khi một POI có nhiều type. | request.md mục 5 | 2026-10-19 |
| D8 | DROP bảng Fabric | Phase triage không xoá bảng Fabric. | request.md mục 5 | 2026-10-19 |
| A1 | Cột Delta L1 | Giữ cột vật lý trên Delta đang sống. Gỡ khỏi registry thì ghi mới ra NULL, giá trị cũ để nguyên. Không `DROP COLUMN`. | architecture.md §3 | 2026-10-19 |
| A2 | Dòng partner đã xoá | Loại `deleted = true` ở cả `slv_pn_business_services` và bảng i18n. | architecture.md §3 | 2026-10-19 |
| A3 | Địa chỉ partner | Copy nguyên `get_json_object`. Chuỗi rỗng giữ chuỗi rỗng. | architecture.md §3 | 2026-10-19 |
| A4 | primary_type partner | Đọc `slv_pn_business_services.amentities`, không đọc `amentities` của i18n. | architecture.md §3 | 2026-10-19 |
| A5 | primary_type không khớp partner | Không có dòng `source_name='partner'` thì `business_category` và `_vi` là NULL, đếm bằng warn. `primary_type` NULL vẫn fallback `business_sector`. | architecture.md §3 | 2026-10-19 |
| A6 | Khớp place_type | Partner: `place_type = trim(primary_type)` đúng chữ. Google: `lower(trim)`. | architecture.md §3 | 2026-10-19 |
| A7 | Backfill category_group | Chỉ dòng `category_group IS NULL`. Seed MERGE vẫn insert-only. | architecture.md §3 | 2026-10-19 |
| A8 | main_category | Duyệt JSON bằng Python thuần trong UDF Spark. | architecture.md §3 | 2026-10-19 |
| D9 | Hoà khi nhiều nhóm | Đồng ý. Other là phần còn lại. Nhiều nhóm, hoặc bước 1 ra nhiều business_category, thì QualityGateError. Bước 2 lấy distinct `category_group` của dòng google active cùng `business_category`, bỏ qua Other. 0 nhóm có tên ra Other. 1 nhóm ra nhóm đó. | Người dùng, 2026-10-19 | 2026-10-19 |
| A9 | Cutover cạnh | Một MERGE trong `NB_SETUP_POI_ENTITY` commit cả cạnh entity (UPSERT 5, RETIRE 2) và amenity (UPSERT 3, RETIRE 1). `NB_SETUP_POI_AMENITY` MERGE lại cạnh amenity sau khi đã có 5 cạnh entity. | GATE-001; lệch architecture.md §8.5 §9 | 2026-10-19 |
| A10 | Kiểm tra trước MERGE | Predicate trùng khoá, owner, cạnh thừa và cạnh mà MERGE không retire chạy dưới flow lock, trước MERGE. | GATE-002; lệch architecture.md §8.5 | 2026-10-19 |
| A11 | JSON không đệ quy | `first_child_value` duyệt bằng stack, đúng thứ tự tài liệu. Sâu hơn 64 mức, hoặc `RecursionError` khi `json.loads`, trả `JSON_INVALID`. | GATE-003; A8; lệch architecture.md §8.1 | 2026-10-19 |
| A12 | Khoá cạnh gồm schema | Nguồn MERGE, `ON` và predicate kiểm tra gồm `src_schema` và `trg_schema`. | GATE-004; lệch architecture.md §8.5 | 2026-10-19 |
| R1 | Không review round 3 | Chấp nhận rủi ro. STATE-001 và SQL-001 đã sửa và verify local. Không chạy review round 3 vì vượt cap. `specialist_review` và `risk_gate` giữ `fix_required` đến sau runtime, khi người dùng tự đánh dấu sẵn sàng merge. | Người dùng, 2026-10-19 | 2026-10-19 |
| V6 | Idempotency chạy tay | Chấp nhận exit `SUCCESS` và log `NEW_EDGE` khi chạy tay notebook node. Watermark cạnh chỉ tiến qua `NB_00`. Lần `p_force=true` MERGE ra version 2 vì nguồn Google sau DROP còn 41 dòng. | Người dùng, 2026-10-19 | 2026-10-19 |
| V7 | Amenity sau DROP L1 | Chấp nhận 43 dòng `slv_poi_amenity` bị xoá mềm. Exec `c611cee0-f4c8-4cb6-9e22-df69e48f8c15`, nguồn 54, insert 0, update 0, version 2. Nguyên nhân là 16 POI Google không còn trong tập entity đang sống. | Người dùng, 2026-10-19 | 2026-10-19 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- DEV không có dòng `amentities` nào chứa `main_category`. Rule "child-key main_category, parent không cố định, lấy giá trị đầu tiên" vẫn theo yêu cầu. Không hard-code path `facilities.classification`.
- Ánh xạ `category_group` người dùng viết chữ thường. Seed google trong repo cũng chữ thường. Seed partner là Hoa đầu từ (`Hotel`, `Resort`). Triage không đổi hoa thường.

## Sai lệch so với kiến trúc

- A9: một commit Delta trong `NB_SETUP_POI_ENTITY` ghi cả hai bộ cạnh. §8.5 và §9 tách hai MERGE và coi khoảng giữa là an toàn vì mỗi notebook giữ khoá lúc ghi. Nhả khoá giữa hai notebook vẫn để `NB_00` thấy hai thế hệ cạnh.
- A10: không còn `raise` sau khi MERGE đã commit. §8.5 kiểm tra `ok` / `extra` / `stale` sau MERGE.
- A11: thay hàm đệ quy §8.1 bằng stack. A8 giữ nguyên, vẫn là Python thuần trong UDF. Quá độ sâu không làm hỏng executor.
- A12: `ON` §8.5 chỉ có `pl_name`, `src_tbl`, `trg_tbl`. Cạnh cùng tên ở schema khác không bị rewrite hoặc retire.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | A9. Một MERGE commit cạnh entity và amenity. | |
| GATE-002 | P1 | fixed | A10. Kiểm tra dưới flow lock, trước MERGE. | |
| GATE-003 | P1 | fixed | A11. Duyệt lặp, sâu tối đa 64, lỗi parse thành `JSON_INVALID`. | |
| GATE-004 | P1 | fixed | A12. Khoá MERGE và predicate gồm `src_schema`, `trg_schema`. | |
| STATE-001 | P1 | fixed | `setup_edge_issues` cho đúng bộ RETIRE (`slv_poi_entity` → `slv_poi_amenity`, flow SLV_1H, schema silver) đi vào MERGE. Owner khác hoặc nguồn lạ vẫn chặn. | |
| SQL-001 | P1 | fixed | Stale và extra chỉ đếm dòng có cả `src_schema` và `trg_schema` là `lh_vv_silver.dbo`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-19: D2 là `md5(concat(id, 'partner')) rồi chèn gạch 8-4-4-4-12`.
- 2026-10-19: D4 là `ghi vào operating_status, không thêm cột`.
- 2026-10-19: D3 chốt hai bước lookup ref_dictionary_place_type. Bước 1 không ghi source_name.
- D5, D6, D7, D8 lấy nguyên văn từ yêu cầu.
- 2026-10-19: D9 nguyên văn: `Đồng ý. Other là phần còn lại. Nhiều nhóm, hoặc bước 1 ra nhiều business_category, thì QualityGateError`. Other không tính là một nhóm khi đếm.
- 2026-10-19: R1 nguyên văn: `Chấp nhận rủi ro.` Không review round 3.

## Lịch sử quyết định

- 2026-10-19 — D1 impact. Schema vật lý là `lh_vv_silver.dbo` trừ control ở `lh_vv_ctrl.dbo`.

Bảng và cột:

- `slv_3p_poi`: registry `TABLE_CONFIGS_3P` map cả `types_json` và `subcategory_tags_json` từ `types` (`NB_CREATE_DDL` cell 14, cùng khối trong `NB_SETUP_INITIAL_DDL`). Bỏ cột là sửa registry ở cả hai notebook. `ensure_target` chỉ ADD cột mới; cột build không trả về bị WARN, không DROP. Cột Delta đã có không tự mất khi tắt registry.
- `slv_3p_poi_address`: `city` và `state_province` cùng `ARRAY_PICK` `administrative_area_level_1` / `longText`. Reader đang chạy: `NB_ENR_POI_INFO` cell 3 `coalesce(a.city, a.state_province)`; `NB_ENR_POI_COORDINATE` cell 3 cùng coalesce cho `destination_name`. `province_name` của coordinate lấy `a.city`. Docs đọc cột này: `docs/context/01_DATA_MODEL.md` mục bronze `poi_address.state_province`; `docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md` và `BRD.md`.
- `slv_poi_entity` `TABLE_SPECS`: `poi_id`, `source_name`, `source_id`, `language_code`, `poi_name`, `poi_name_normalized`, `types_json`, `subcategory_tags_json`, `operating_status`, `primary_type`, `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`, `business_sector`, `business_category`, `business_category_vi`, `row_hash`, `created_at`, `updated_at`, `deleted_at`. Build `b1entitybuild` giữ mọi cột `slv_3p_poi` trừ tên kỹ thuật, rồi thêm 3 cột category. Không có cột địa chỉ hôm nay.
- Cột thêm theo yêu cầu, chưa có trong spec: `category_group`, `house_number`, `street`, `ward`, `city`, `full_address`, `lat`, `lng`. Registry 3P: các cột chữ là string; `lat` và `lng` là double.
- `ref_dictionary_place_type` spec: `source_name`, `place_type`, `business_sector`, `business_category`, `business_category_vi`, `is_active`, `updated_at`. Khoá (`source_name`, `place_type`). Seed 5 trường, insert-only. Thêm `category_group` không backfill dòng Fabric sẵn có nếu chỉ INSERT khi chưa có. `NB_CREATE_DDL` cần patch ADD COLUMN và UPDATE; `NB_SETUP_INITIAL_DDL` sửa CREATE và seed tại chỗ.

Notebook và test:

- Node: `notebooks/NB_SLV_POI_ENTITY.ipynb`, `trg_tbl="slv_poi_entity"`. Tên mới theo `NB_<UPPER(trg_tbl)>` là `NB_SLV_POI_ENTITY_NON_ENRICH`. `nb_name` NULL nên lib suy tên từ `trg_tbl`.
- Setup node: `notebooks/NB_SETUP_POI_ENTITY.ipynb` (DDL ref, seed, cạnh). Mẫu `NB_SETUP_*`, không phải `NB_<UPPER(trg_tbl)>`.
- Reader: `notebooks/NB_SLV_POI_AMENITY.ipynb` input `entity` = `slv_poi_entity`, lấy `business_sector`. `notebooks/NB_SETUP_POI_AMENITY.ipynb` đòi 2 cạnh active `trg_tbl = slv_poi_entity` rồi ghi cạnh nguồn `slv_poi_entity` vào `slv_poi_amenity`.
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb`: `TABLE_SPECS` entity, seed pipeline, seed place type.
- Test: `tests/test_poi_entity_contract.py`, `tests/test_poi_amenity_contract.py`, `tests/test_initial_ddl_contract.py`.
- Docs: `docs/context/01_DATA_MODEL.md` §5.2 và §6 N6/N7; `docs/context/CTRL_TABLES_CONTEXT.md` §3 `PL_VV_TRANS_SLV_TO_SLV_1H`; `docs/context/02_NAMING_CONVENTION.md` §2.1 điều 7; `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` mục cột JSON.

Cạnh control `PL_VV_TRANS_SLV_TO_SLV_1H`, `load_mode = RECOMPUTE`, schema `lh_vv_silver.dbo`:

- Vào `slv_poi_entity`: `slv_3p_poi`, `ref_dictionary_place_type`.
- Vào `slv_poi_amenity`: `slv_3p_poi_amenity`, `slv_poi_entity`, `ref_dictionary_amenities`.
- Watermark lib: `wm_e__<trg_tbl>__<src_tbl>`. Đổi tên bảng đổi id watermark. Seed initial chỉ INSERT khi chưa khớp; dòng Fabric đang trỏ `slv_poi_entity` không tự đổi tên.
- Yêu cầu thêm đầu vào: `slv_3p_poi_address`, `slv_pn_business_services`, `slv_pn_business_service_i18ns`.
- Chưa có JSON pipeline cho luồng này trong repo.

Partner, lấy từ registry, không suy JSON:

- Bảng `slv_pn_business_services`. Cột `address` string, toast. Cột amenities trong registry viết `amentities` string, toast. `id`, `name`, `business_sector`, `operation_status` là cột thường.
- i18n đúng tên `slv_pn_business_service_i18ns`, khoá (`business_service_id`, `locale`).
- `poi_id` 3rd party trong lib là `regexp_replace(md5(concat(...)), hex 8-4-4-4-12)`. §8 data model còn công thức partner `uuid_format(md5('partner_portal' || business_service_id))`, notebook hiện không gọi. D2 để người dùng chốt layout.

- 2026-10-19 — D2 chốt. Nguyên văn: `md5(concat(id, 'partner')) rồi chèn gạch 8-4-4-4-12`. Cùng kiểu `HASH_MD5_UUID`: hex md5, không đảo byte. Không dùng công thức §8 `partner_portal`.
- 2026-10-19 — D4 chốt. Nguyên văn: `ghi vào operating_status, không thêm cột`. Giá trị partner `operation_status` ghi vào cột hiện có `operating_status`.
- 2026-10-19 — Probe `partner-json-shape` trên Fabric DEV, 30 dòng `slv_pn_business_services`, `deleted = false` cả 30. `address` là object ở cả 30 dòng. `full_address` nonempty 30. `address_line1`, `street`, `ward`, `city` nonempty 23 và empty string 7. `address_line2`, `district`, `state`, `zip` empty string 30. `country` nonempty 12, empty 18. Không có khoá top-level ngoài danh sách sample. Cột amenity là `amentities`. 28 dòng JSON `null`, 1 dòng null, 1 dòng object và object đó không có `main_category`. Không có path `main_category`. i18n: `vi` 121 dòng / 121 id, `multi_vi_ids = 0`. 24/30 service có bản `vi`. Locale: `ko` 123, `vi` 121, `en` 118.
- 2026-10-19 — Lần ngược `ai_poi` trong `1. parsing_bronze_partner.ipynb`, `2.1. transform_partner_to_gold_poi_master.ipynb`, `2.3. nb_transform_bronze_userprofile.ipynb`. Notebook 1 chỉ ghi `lh_vv_bronze.partner.business_services.amentities` dạng string. Notebook 2.3 không đụng `ai_poi`. Notebook 2.1 MERGE `lh_vv_gold.dbo.ai_poi`: không có cột `primary_type`. `business_category` lấy phần tử đầu nếu là list, không thì scalar, từ `deep_get(amentities, *category_path)` theo `business_sector`. `poi_types` = `lh_vv_bronze.partner.partners.type`. `subcategory_tags` gán `None`. `amentities` ưu tiên bản i18n cùng locale, không chỉ `vi`. Dataframe là `poi_df = SELECT * FROM ai_poi` (cell 3), lakehouse notebook ghi `ll_vv_gold` (cell 7). Cell 15, nhánh `partner_portal`, gọi `normalize_poi_dataframe` trên chính dataframe đó, không join bảng khác trước khi tính nhóm. `primary_type` không đọc cột cùng tên: gán từ `ai_poi.business_category`, null thì chuỗi `unknown`, rồi `strip`. Phần tử `types` là `as_list(ai_poi.poi_types)` nối sau bởi `as_list(ai_poi.subcategory_tags)`. `as_list` nhận list, JSON array, hoặc chuỗi cách dấu phẩy. `infer_group` bỏ thứ tự vì đưa vào set.
- 2026-10-19 — D3 chốt. Nguyên văn: xử lý category_group của partner bằng cách lấy ref_dictionary_place_type place_type=primary_type, lấy được business_category. JOIN tiếp ref_dictionary_place_type qua ref_dictionary_place_type.business_category=business_category (lấy từ bước 1) và source_name = google để lấy được category_group. Bước 1 không nêu source_name. Không tự thêm. Không chọn thứ khi nhiều dòng google cùng business_category.
- 2026-10-19 — D3 trước khi chốt. Review `notebooks_lgc/pl_transform_partner_userprofile_cms/4. nb_data_enrichment_partner.ipynb` cell 9. `CATEGORY_GROUPS` trùng bảng trong yêu cầu, không có nhóm `Other` trong dict. `infer_group` lấy `candidates = {primary_type, *types}`, duyệt dict theo thứ tự khai báo, nhóm đầu tiên có giao với candidates thì thắng, không thì `Other`. Không ưu tiên `primary_type`. So khớp phân biệt hoa thường. Input lúc gọi: `primary_type = business_category` (rỗng thì `unknown`, có strip), `types = poi_types + subcategory_tags`. Cell 10 chỉ lọc dòng partner, không đổi `category_group`. Rule này khác D7 của dòng google. DEV hiện không có `main_category`, nên `primary_type` partner theo yêu cầu mới đang null trên cả 30 dòng.
- 2026-10-19 — D5 đến D8 ghi theo yêu cầu, không thêm lựa chọn.
- 2026-10-19 — D9 chốt. Nguyên văn: `Đồng ý. Other là phần còn lại. Nhiều nhóm, hoặc bước 1 ra nhiều business_category, thì QualityGateError`. A1–A8 ghi từ architecture.md §3 trước khi sửa code. `ensure_lock_row` chỉ INSERT dòng `wm_flow__` khi chưa có, không ghi đè field của NB_00, nên setup gọi hàm đó.
- 2026-10-19 — `tests/test_3p_l1_contract.py` cũng khoá 55 cột registry. Sửa thành 53, `slv_3p_poi` 9 cột, `slv_3p_poi_address` 11 cột. Edit list không nêu file này; suite local không xanh nếu để nguyên.
- 2026-10-19 — Comment cũ trong `TABLE_CONFIGS_3P` vẫn liệt kê `subcategory_tags_json` như cột JSON đang dùng. Cell seed 3P vẫn ghi `55 cột`. Đã sửa cả hai cho khớp registry 53 cột. Khoá cột trong dict đã bị gỡ từ trước.
- 2026-10-19 — Fabric DEV, người dùng chạy. Registry 9 bảng, 53 cột, 0 cột tắt (`slv_3p_poi` 9, `slv_3p_poi_address` 11). `category_group` khớp seed: google 297, partner 59 toàn `Other`, không thấy nhóm NULL. `NB_SETUP_POI_ENTITY` `p_apply=true`: inserted=0, drift=0, edges_inserted=5, edges_retired=2. `NB_SETUP_POI_AMENITY` `p_apply=true`: inserted=0, drift=6, edges_inserted=1, edges_retired=1. drift amenity là `amenity_vi` hoặc `is_active` lệch seed; MERGE insert-only không ghi đè. Cạnh đã chuyển. Chi tiết ở `evidence/results/setup-dev.txt`. Chưa chạy node entity.
- 2026-10-19 — A9 đến A12, trước khi sửa GATE-001..004. Seq amenity trong MERGE chung là 6, 7, 8 để không trùng id với seq entity 1..5 trong cùng một câu INSERT. `NB_SETUP_POI_AMENITY` giữ seq 1, 2, 3 cho đường sửa lại.
- 2026-10-19 — Review round 2 `FIX_REQUIRED`. GATE-003 đóng. STATE-001: predicate `extra` chặn cạnh legacy `slv_poi_entity → slv_poi_amenity` trước khi MERGE retire. SQL-001: stale đếm cả schema khác `lh_vv_silver.dbo` nên chặn setup. `rounds.review=2`, `rounds.verification=2`. Lượt review kế tiếp vượt cap.
- 2026-10-19 — STATE-001 và SQL-001 sửa trong cùng lượt, không chạy `run-gate` vì round 3 vượt cap. Hàm `setup_edge_issues` dùng chung hai notebook. Fixture: cạnh RETIRE đúng bộ không chặn; owner khác thì chặn; schema khác thì bỏ qua.
- 2026-10-19 — R1. Người dùng chấp nhận rủi ro không có review round 3. Bước còn lại là runtime DEV theo `runtime-runbook.md`. Không đánh `gates.runtime`.
- 2026-10-19 — Runtime DEV, người dùng chạy. Entity RUN đầu: SUCCESS, insert 81, version 1, bảng mới. Chạy lại: SUCCESS, diff 0, không commit, version vẫn 1, không phải NO_DATA. Extract FULL_RELOAD rồi INCREMENTAL đều SUCCESS; lần sau apply 0. Chi tiết `evidence/results/runtime-dev.txt`. Cột vật lý `subcategory_tags_json` và `state_province` còn trên Delta là A1, không phải bước DROP bị quên. ENR 15P để task khác. Đổi `amenity_raw` thành chỉ còn key, và tách `types[]`, đổi grain và khóa `slv_poi_amenity`; không sửa trong task này.
- 2026-10-19 — Người dùng đã DROP bảng L1 trên DEV để bỏ cột vật lý `state_province` và `subcategory_tags_json`. A1 trên repo vẫn giữ: không DROP ở prod cho đến khi có quyết định mới. Script kiểm tra đọc schema trước, không giả định hai cột còn tồn tại.
- 2026-10-19 — Check DEV sau DROP: registry 53, cạnh 5 và 3, partner 24 đúng nhóm Other, hai cột vật lý đã mất, khoá luồng trống, không có watermark cạnh. Amenity workspace còn spec `slv_poi_entity` nên dừng trước khi build. Entity `p_force=true`, exec `b94fc4c7-dbda-4b3d-86ab-28deb72dfa9d`, nguồn 65, update 1, xoá mềm 16, version 2. Chi tiết `evidence/results/runtime-dev.txt`.
- 2026-10-19 — Amenity chạy lại, exec `c611cee0-f4c8-4cb6-9e22-df69e48f8c15`, SUCCESS, nguồn 54, insert 0, update 0, xoá mềm 43, version 2. `slv_poi_entity` history dừng ở version 1 ngày 2026-10-16. V9 vẫn để task khác. Chưa đánh `gates.runtime`.
- 2026-10-19 — V6. Người dùng chấp nhận exit `SUCCESS` cùng `NEW_EDGE` của lần chạy tay, và MERGE version 2 của lần `p_force=true`. Chưa chấp nhận số dòng amenity đổi sau DROP. `gates.runtime` vẫn `pending`.
- 2026-10-19 — V7. Người dùng chấp nhận 43 dòng amenity xoá mềm, exec `c611cee0-f4c8-4cb6-9e22-df69e48f8c15`, version 2. `gates.runtime` chuyển `pass`. `specialist_review` và `risk_gate` giữ `fix_required` theo R1.
