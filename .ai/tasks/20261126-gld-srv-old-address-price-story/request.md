# Request

## User outcome

Add gold-only columns on `gld_srv_poi_info` (`old_address`, `price_level`, `price_min`, `price_max`) and `gld_srv_poi_multi_lang` (`story`, `local_tips`). Grain and MERGE keys stay as they are. PostgreSQL, Java entities, DTOs, and `docs/context/api-mapping/` do not gain these columns.

`old_address` follows `decision.md` row `D-OLD-ADDR`: keep `house_number`, `street`, and `full_address`; do not invent `old_house_number`, `old_street`, or `old_full_address`.

## Scope

### In scope

- `gld_srv_poi_info`: `old_address`, `price_level`, `price_min`, `price_max`.
- `gld_srv_poi_multi_lang`: `story`, `local_tips`.
- `NB_SETUP_INITIAL_DDL` `TABLE_SPECS`, one new patch cell at the end of `NB_CREATE_DDL`, `OUT_COLS` and build of `NB_GLD_SRV_POI_INFO` and `NB_GLD_SRV_POI_MULTI_LANG`.
- `slv_3p_poi_price` as an input of `NB_GLD_SRV_POI_INFO` and an edge in the `PL_VV_TRANS_SLV_TO_GLD_30M` seed.
- Mapping docs `docs/context/mapping_gld_srv_poi_info.md` and `docs/context/mapping_gld_srv_poi_multi_lang.md`.
- Contract tests, with the six columns as gold-only exceptions in `tests/test_srv_poi_serving_contract.py`.

### Out of scope

- `sql/postgres/gld_srv_serve.pg.sql`, Java entities, DTOs, `docs/context/api-mapping/`.
- `currency`. Extra `source_name` filter on price. Choosing one price row when several share `poi_id`.
- Fallback of `story` or `local_tips` to `slv_enr_poi_info_multi_lang`.
- Inventing `old_house_number`, `old_street`, or `old_full_address`. Using entity `full_address` as `old_address`.
- `notebooks_lgc/`, `docs/poi-serving-api/`, and `services/data-serving-service/` except the serving contract test.
- Fast lane. Commit. Fabric DEV execution by Main.

## Acceptance criteria

- Bốn cột info và hai cột multi_lang có trong `TABLE_SPECS` của `NB_SETUP_INITIAL_DDL`, một cell patch mới ở cuối `NB_CREATE_DDL`, `OUT_COLS` và build của `NB_GLD_SRV_POI_INFO` và `NB_GLD_SRV_POI_MULTI_LANG`.
- `slv_3p_poi_price` thành input của `NB_GLD_SRV_POI_INFO` và có cạnh trong seed `PL_VV_TRANS_SLV_TO_GLD_30M`. `story` và `local_tips` dùng cạnh i18n đang có.
- Kiểu lấy từ nguồn: `old_address`, `story`, `local_tips` là `STRING`; `price_level`, `price_min`, `price_max` giữ kiểu cột `slv_3p_poi_price`.
- PostgreSQL và API không có sáu cột này. `test_gold_and_pg_columns_and_types_match` vẫn khớp mọi cột gold khác; sáu cột này là ngoại lệ gold-only trong `tests/test_srv_poi_serving_contract.py`.
- `docs/context/mapping_gld_srv_poi_info.md` và `docs/context/mapping_gld_srv_poi_multi_lang.md` cập nhật trước review.
- Verify PASS trước review. P0/P1 được xử lý trong cap 2 vòng.

## Constraints

- Signal `data_model_change`. Main không viết `model-design.md`.
- Không bịa cột `old_house_number`, `old_street`, `old_full_address`. Không lấy `full_address` của entity làm `old_address`.
- Không đọc `notebooks_lgc/`, `docs/poi-serving-api/`, `services/data-serving-service/` ngoài test hợp đồng serving.
- Không commit. Không chạy Fabric DEV. Runtime để người dùng chạy theo `runtime-runbook.md`.
- Fast lane không áp dụng.
- Architecture bắt buộc vì thêm cột gold và thêm cạnh `slv_3p_poi_price`. Evidence không bắt buộc cho kiểu và grain đã có trong DDL và data model. Reviewer: `spark-runtime-reviewer` và `sql-data-reviewer`. `fabric-pipeline-reviewer` chỉ khi sửa `pipelines/*.json`.

## Verbatim request

Update bảng gld_srv_poi_info:
- Thêm field old_address: transform như full address nhưng lấy các field có tiền tố old_
- Thêm price_level, price_min, price_max lấy từ slv_3p_poi_price (price_level, price_min, price_max)

Update bảng gld_srv_poi_multi_lang:
- Thêm field story (hiện tại chỉ có của partner): slv_pn_business_service_i18ns.story
- Thêm field local_tips (hiện tại chỉ có của partner): slv_pn_business_service_i18ns.local_tips

2 bảng này không cần sink xuống db serving và api không sử dụng.

Diễn giải đã chốt:
- Grain giữ nguyên: gld_srv_poi_info một dòng poi_id; gld_srv_poi_multi_lang một dòng (poi_id, lang). MERGE giữ khóa hiện tại.
- old_address, price_level, price_min, price_max, story, local_tips chỉ ở gold. Không thêm vào sql/postgres/gld_srv_serve.pg.sql, entity Java, DTO, hay docs/context/api-mapping/.
- price_level, price_min, price_max lấy đúng ba cột slv_3p_poi_price. Không thêm currency. Không có dòng giá thì null. Không lọc thêm source_name. Nhiều dòng cùng poi_id thì dừng, không chọn dòng.
- story và local_tips chỉ từ slv_pn_business_service_i18ns, cùng cách nối partner đang dùng cho bio và usps: poi_id = uuid_md5(business_service_id, 'partner') và lang = locale. P1 partner lấy hai cột đó, không fallback sang slv_enr_poi_info_multi_lang. P1 không phải partner thì null. P2 lấy thẳng từ i18n, không fallback.
- full_address hiện tại, docs/context/mapping_gld_srv_poi_info.md §1.6: có dòng destination thì coalesce ba nhóm, nối bằng ", ". Nhóm 1: house_number + street + formatted_address. Nhóm 2: house_number + street + ward_with_type + city_with_type. Nhóm 3: slv_enr_poi_destination.full_address. Field null, hoặc house_number hay street chỉ còn khoảng trắng sau trim, thì bỏ cả nhóm. Không có dòng destination thì full_address của slv_poi_entity_non_enrich.
- Cột old_* đã có trên slv_enr_poi_destination: old_ward, old_ward_with_type, old_district, old_district_with_type, old_city, old_city_with_type, old_formatted_address. Không có old_house_number, old_street, old_full_address. Entity không có cột old_* cho địa chỉ.

## Classification rationale

- Complexity: medium. Column add plus one new gold input, grain unchanged. More than a two-file fast-lane edit. Fast lane does not apply.
- Risk: medium. Bounded gold behavior change. MERGE keys stay. Rollback is a column drop and notebook revert. Local contract tests prove the column contract; Fabric apply is a separate runtime step.
- Architecture: required. New gold columns and a new `slv_3p_poi_price` → `gld_srv_poi_info` edge. Signal `data_model_change`, so `model-design.md` is required before the Architect.
- Evidence: not required. Types and grain for the named source columns are already in `NB_SETUP_INITIAL_DDL` `TABLE_SPECS` and the data-model docs named in the prompt. `old_address` is a formula choice, not a missing runtime fact.
- Runtime proof: required after implementation. Notebook DDL and recompute must run on Fabric DEV by the user, from `runtime-runbook.md`.
- Reviewer routing: `spark-runtime-reviewer`, `sql-data-reviewer`. `fabric-pipeline-reviewer` only if `pipelines/*.json` changes. The gold edge seed lives in `NB_CREATE_DDL`, so the pipeline reviewer is not required at triage.
