# Request

## User outcome

Silver L1 drops two duplicate columns, `ref_dictionary_place_type` gains `category_group`, and the Google POI entity node is renamed to `slv_poi_entity_non_enrich` with address columns and a partner append. Live Fabric tables are not dropped in triage.

## Verbatim requirement

Vì thay đổi đi từ bronze sang silver, hãy kiểm tra impact và impact ra sao. Ghi impact vào ledger trước khi chuyển architecture.

1. slv_3p_poi bỏ cột subcategory_tags_json (trùng types_json).
2. slv_3p_poi_address bỏ cột state_province (trùng city).
3. slv_poi_entity cũng bỏ subcategory_tags_json.
4. Thêm category_group vào lh_vv_silver.dbo.ref_dictionary_place_type, map theo type trong types_json. Type không có trong bảng thì category_group = Other.
category_group; types
Lodging; lodging, hotel, resort_hotel, motel, guest_house, hostel, bed_and_breakfast, resort
Main Meals; restaurant, food, meal_takeaway, seafood_restaurant, bistro
Light Snacks / Cafe; cafe, bakery, coffee_shop, tea_house
Heavy Entertainment; amusement_park, theme_park, water_park, zoo, aquarium, national_park, hiking_area
Light Sightseeing / Culture & Nature; tourist_attraction, museum, place_of_worship, beach, park, historical_landmark, pagoda, church
Shopping & Nightlife; shopping_mall, market, night_market, bar, night_club, souvenir_store
Other; phần còn lại
5. Sửa slv_poi_entity:
   - Đổi tên bảng thành slv_poi_entity_non_enrich. Đổi tên notebook theo NB_<UPPER(trg_tbl)>. Cập nhật cạnh ctrl và mọi chỗ đọc bảng. Không xoá bảng Fabric trong phase triage.
   - Dòng "+ bỏ" trong yêu cầu gốc bị cụt. Chỉ bỏ subcategory_tags_json. Không bỏ thêm cột.
   - Thêm category_group. Dòng google lấy category_group của place_type mà entity đã resolve (primary_type, rồi phần tử types_json khớp đầu tiên). Không thêm rule chọn group khi một POI có nhiều type.
   - slv_3p_poi LEFT JOIN slv_3p_poi_address qua poi_id, lấy house_number, street, ward, city, full_address, lat, lng.
   - APPEND nguồn partner:
     - poi_id: hash(slv_pn_business_services.id + "partner"), cùng kiểu hash 3rd party uuid_format(md5(...)).
     - source_name: partner
     - source_id: slv_pn_business_services.id
     - language_code: vi
     - poi_name: slv_pn_business_services.name
     - poi_name_normalized: lower(name)
     - types_json: null
     - operation_status: slv_pn_business_services.operation_status
     - Từ JSON address: house_number = address_line1, street = street, ward = ward, city = city, full_address = full_address. Khoá sample: full_address, address_line1, address_line2, street, ward, district, city, state, zip, country.
     - lat, lng: null
     - INNER JOIN bản i18n ON id = business_service_id, chỉ locale = vi. Người dùng ghi slv_pn_business_services_i18ns; repo/CTRL đang là slv_pn_business_service_i18ns. Dùng tên có trong registry. Không tạo bảng mới.
     - primary_type: child-key main_category trong amenities; parent-key không cố định; nhiều giá trị thì lấy giá trị đầu tiên; không có key thì null. Sample 1 không có main_category. Sample 2 có facilities.classification.main_category.
     - business_sector: slv_pn_business_services.business_sector
     - business_category và business_category_vi: từ ref_dictionary_place_type với source_name = partner và place_type = primary_type. primary_type null thì cả hai bằng business_sector.

## Scope

### In scope

- Registry and DDL for dropping `subcategory_tags_json` and `state_province` from the silver L1 definitions, and every current reader of those columns.
- `category_group` on `lh_vv_silver.dbo.ref_dictionary_place_type` and on the renamed entity.
- Rename `slv_poi_entity` to `slv_poi_entity_non_enrich`, notebook `NB_<UPPER(trg_tbl)>`, control edges, and readers.
- Google address join and partner append, after the open decisions and the JSON-shape probe.

### Out of scope

- Dropping the live Fabric table in triage.
- Choosing the MD5 byte order or assigning partner `category_group`.
- Creating `slv_pn_business_services_i18ns`.
- Dropping any entity column other than `subcategory_tags_json`.

## Acceptance criteria

- Impact is recorded in `decision.md` before architecture.
- A minimal read-only DEV probe exists for the partner JSON shape.
- Open user decisions stay `USER_DECISION` until the user answers.
- Architecture runs only after the probe result and those answers exist.

## Constraints

- Schema names are `lh_vv_silver.dbo` unless a control table is explicitly `lh_vv_ctrl.dbo`.
- i18n table name is the registry name `slv_pn_business_service_i18ns`.
- Partner `primary_type` reads child key `main_category`; the parent key is not fixed.
- Google `category_group` uses the place type the entity already resolves. No extra multi-type rule.
- This phase does not edit source notebooks, pipelines, or docs outside the task folder.

## Classification rationale

- Complexity: high. Signals: `cross_system`, `stateful_logic`, `idempotency`, `cross_state_impact`, `design_tradeoffs`, `data_evidence_required`, `runtime_proof_required`. Grain and table name change, MERGE inputs change, and control edges change.
- Risk: high. Rename plus column removal on live Delta and control-edge identity is cross-system. Not a fast lane.
- Architecture: required. Table grain, commit target, and bronze-to-silver column removal.
- Evidence: required. Partner `address` and `amentities` are strings in the registry. The JSON shape is not in the repo. Sample keys are not a DEV census.
- Runtime proof: required. Live table rename, column removal, and control-edge update cannot be proved by local tests alone.
- Reviewer routing: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`, then `risk-gate`. No pipeline JSON exists for `PL_VV_TRANS_SLV_TO_SLV_1H`, so `fabric-pipeline-reviewer` is not routed.
