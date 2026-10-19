# Request

## User outcome

Yêu cầu nghiệp vụ (nguyên văn):

Với NB_SLV_POI_AMENITY và ref_dictionary_amenities, cột amenity_raw hiện có dạng key = true hoặc types[] = .... Định dạng mới của cột này chỉ còn key.
- Bỏ hậu tố " = true". Ví dụ outdoorSeating = true thành outdoorSeating. Path có dấu chấm giữ nguyên phần trước " = true", ví dụ parkingOptions.freeElectricVehicleParking = true thành parkingOptions.freeElectricVehicleParking.
- Dạng types[] = ... tách thành nhiều dòng, mỗi dòng một key. Ví dụ types[] = hot_spring, sauna thành hai dòng amenity_raw hot_spring và sauna. Các cột còn lại của dòng seed giữ nguyên.
- amenity_raw không thuộc hai dạng trên giữ nguyên từng ký tự. Không viết lại các câu types[] có ....
- Rule khớp trong NB_SLV_POI_AMENITY đọc amenity_raw mới: key cờ khớp source_flags_json bằng true; mỗi key tách từ types[] khớp đúng một phần tử type. Dòng amenity_raw giữ nguyên thì giữ hành vi khớp hiện tại.
- Cho chi tiết các step chạy lại full hai bảng lh_vv_silver.dbo.ref_dictionary_amenities và lh_vv_silver.dbo.slv_poi_amenity như init lần đầu. Step này là runtime-runbook sau review PASS. User chạy trên Fabric DEV. Agent không đánh gates.runtime.

Observable outcome: `ref_dictionary_amenities.amenity_raw` and the `NB_SLV_POI_AMENITY` matcher use the new key-only values; a full rebuild of both silver tables is specified for the user to run after review PASS.

## Scope

### In scope

- `notebooks/NB_SLV_POI_AMENITY.ipynb` matcher and quality gate.
- Amenity seed shared by `notebooks/NB_SETUP_POI_AMENITY.ipynb` and `notebooks/NB_SETUP_INITIAL_DDL.ipynb` (`BEGIN_AMENITY_SEED` / `END_AMENITY_SEED`).
- `tests/test_poi_amenity_contract.py` and `tests/test_initial_ddl_contract.py`.
- `docs/context/3p-google/mapping_amenities.md` where the seed contract is parsed from it.
- `docs/context/01_DATA_MODEL.md` seed-count sentence for `ref_dictionary_amenities`.
- Runtime runbook, after review PASS, to rebuild `lh_vv_silver.dbo.ref_dictionary_amenities` and `lh_vv_silver.dbo.slv_poi_amenity` on Fabric DEV.

### Out of scope

- Source edits in the triage chat.
- Marking `gates.runtime` from an agent result.
- Dropping either table before the runbook has a rollback step.
- A new entity input name. The amenity node entity input stays `slv_poi_entity_non_enrich`.

## Acceptance criteria

- Seed, parser, and the test contract use the new `amenity_raw`. Dictionary key stays `(source_name, business_sector, amenity_group, amenity_raw, amenity)`. `slv_poi_amenity` key still includes `amenity_raw`.
- One `types[] = a, b` cell is no longer one row. Two equal keys in the same `(source_name, business_sector, amenity_group)` fail the quality gate.
- The current seed is insert-only. `amenity_raw` is part of the key, so rerunning the seed notebook does not delete old keys. The runbook rebuilds both tables to the new seed, with a stop point, before and after row counts, and a way back. No `DROP TABLE` before that rollback step exists in the runbook.
- The `ctrl_mng_pipeline_config` edges of `slv_poi_amenity` are not duplicated.

## Constraints

- Không có.
- Real schema is `lh_vv_silver.dbo`.

## Repository impact

Counted from `SEED_ROWS` in `notebooks/NB_SETUP_POI_AMENITY.ipynb` (`BEGIN_AMENITY_SEED`). No Fabric probe. Current seed is 152 rows: 74 `partner`, 78 `google` (`tests/test_poi_amenity_contract.py` `test_seed_counts`; `docs/context/01_DATA_MODEL.md` §6.1).

Form rules applied only as a census, not as a source edit:

- Flag form `^[A-Za-z][A-Za-z0-9]*(?:\.[A-Za-z][A-Za-z0-9]*)? = true$`: 27 google rows. This set equals `MATCHABLE` in the contract test. Strip the suffix ` = true`.
- `^types\[\] = (.+)$`: 8 google rows, split on comma into 14 keys. Net +6 rows. Resulting seed size 158 if no row is dropped. The eight cells become: `swimming_pool`; `hot_spring` + `sauna`; `garden` + `botanical_garden`; `meeting_rooms`; `food_stand` + `street_food_gathering`; `seafood_restaurant` + `oyster_bar_restaurant`; `steakhouse`; `bakery` + `pastry_shop` + `cake_shop`. Other columns of each seed row stay on every split row.
- Everything else stays character-for-character: 117 rows. That includes partner text, bare tokens such as `dim_sum_restaurant`, comma lists that are not `types[] = ...` (`yakiniku_restaurant, yakitori_restaurant`, `cat_cafe, dog_cafe`, `parkingOptions.freeParkingLot, parkingOptions.paidParkingLot = true`), `serves_meals = true`, `outdoorSeating = true = true`, and narrative `types[]` sentences (`types[] có ...`, `types[] thuộc ...`). No seed value contains `false`.

After that census, one duplicate key remains inside `(source_name, business_sector, amenity_group)`:

- `('google', 'attraction', 'facilities_and_services', 'goodForChildren')` twice, amenities `Good for Children` and `Family Friendly`. Both raw values are already the bare token `goodForChildren`. The 5-column dictionary key stays unique. The current `validate_seed` checks that 5-column key only.

Current matcher (`NB_SLV_POI_AMENITY` `resolve_condition`): full match of `head[.leaf] = true|false` against `FLAG_KEYS` / `OBJECT_KEYS`. `types[] = ...`, bare keys, `serves_meals = true`, and `outdoorSeating = true = true` return None and are skipped. The build joins exploded `source_flags_json` path and value. `source_flags_json` members in the 3P registry are boolean `flags` plus object keys `parkingOptions`, `paymentOptions`, `accessibilityOptions`, `evChargeOptions`, `fuelOptions`. `types` is `slv_3p_poi.types_json` (`array` via `_str("types")` in `NB_SETUP_INITIAL_DDL` / `NB_CREATE_DDL`), not a member of `source_flags_json`.

Seed MERGE is `WHEN NOT MATCHED THEN INSERT` only (`test_setup_contract`). Old `amenity_raw` values stay after a rerun. `docs/context/02_NAMING_CONVENTION.md` §2.1: the amenity seed block stays identical between `NB_SETUP_POI_AMENITY` and `NB_SETUP_INITIAL_DDL`; `tests/test_initial_ddl_contract.py` asserts that marker. No `DROP` of a populated table in either DDL notebook.

`docs/context/CTRL_TABLES_CONTEXT.md` §3, `PL_VV_TRANS_SLV_TO_SLV_1H`, `slv_poi_amenity`: three active edges from `slv_3p_poi_amenity`, `slv_poi_entity_non_enrich`, and `ref_dictionary_amenities`. Prerequisite is five active edges into `slv_poi_entity_non_enrich`. Edge seed is in `NB_SETUP_POI_AMENITY`. A rebuild of the two data tables must not insert a second copy of those edges.

`docs/context/01_DATA_MODEL.md` §6 N7: grain `(poi_id, business_sector, amenity_group, amenity_raw)`; inputs `slv_3p_poi_amenity`, `slv_poi_entity_non_enrich`, `ref_dictionary_amenities`; full recompute then MERGE on `row_hash`, soft-delete when a row disappears.

## Classification rationale

- Complexity: high. Signals: `stateful_logic`, `idempotency`, `transaction_boundaries`, `cross_state_impact`, `design_tradeoffs`, `runtime_proof_required`.
- Risk: high. Key values, seed cardinality, and MERGE behavior change. User: "Đổi giá trị khóa, số dòng seed và cách MERGE: architecture bắt buộc, risk high, không fast lane."
- Architecture: required. Grain values and commit/MERGE behavior change (`WORKFLOW.md` §5).
- Evidence: not required. Every current `amenity_raw` form is in the repository seed. `source_flags_json` and `types_json` placement is in the DDL registry. A DEV group-by would only restate that insert-only table, which the request already treats as stale until the runbook rebuilds it.
- Runtime proof: required as a runbook after review PASS. The user runs it on Fabric DEV. The agent does not set `gates.runtime`.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, and `risk-gate` (`WORKFLOW.md` §7). `risk-gate` follows `risk_level=high`.
