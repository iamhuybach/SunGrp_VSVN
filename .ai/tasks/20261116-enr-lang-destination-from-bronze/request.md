# Request

## User outcome

Silver `slv_enr_poi_info_multi_lang` is loaded only from `event_type = LANG` and `slv_enr_poi_destination` only from `event_type = DESTINATION` of `bronze.brz_enrichment_result`, using the JSON paths below. `cost_vnd` becomes `cost` on the three named tables and on every API read of multi-lang `cost_vnd`. `street` is removed from `slv_enr_poi_destination`. `gld_srv_poi_info.street` and `full_address` follow the stated sources and three priority groups.

## Scope

### In scope

- One task for the whole scope. No separate task for Mapping, extract, gold, PostgreSQL, or the API.
- `docs/requirements/20261116-enr-lang-destination-from-bronze/MAPPING.md` and `BRD.md`.
- Extract of `slv_enr_poi_info_multi_lang` and `slv_enr_poi_destination` from `bronze.brz_enrichment_result`.
- Column rename `cost_vnd` to `cost` on `slv_enr_poi_info_multi_lang`, `gld_srv_poi_multi_lang`, and `apps.srv_poi_multi_lang`, and the API reads of that column.
- Drop `street` from `slv_enr_poi_destination`.
- `gld_srv_poi_info.street` and `full_address` rules below.
- Update `docs/context/mapping_gld_srv_poi_info.md` and `docs/context/mapping_gld_srv_poi_multi_lang.md` in this task before review.

### Out of scope

- Any other table or notebook that still has `cost_vnd` or `street` and is not named in the request. Record those as ledger gaps; do not change them here.
- New API columns. The repository has no Flyway.
- Inventing a `full_address` separator that is not already in a notebook.

## Acceptance criteria

- `MAPPING.md` and `BRD.md` follow the templates, `doc_status` reaches `READY_FOR_ANALYSIS`, and `requirements-analysis.md` is `COMPLETE`.
- Each silver table accepts only its `event_type` and the JSON paths below.
- In the sample, `cost`, `best_time`, and `time_to_spend` stay objects `{text, label}`. `experiences` and `destination` stay arrays. `destination_id` and `destination_name` keep element order.
- `cost_vnd` becomes `cost` on the three named tables and every API read of multi-lang `cost_vnd`. `street` is gone from `slv_enr_poi_destination`.
- `gld_srv_poi_info.street` and `full_address` match the stated source and three priority groups.
- Both mapping context files are updated in this task before review.
- `verify` is `PASS` before review. P0/P1 are closed or have a disposition before review is treated as done.

## Constraints

- Do not edit notebooks, DDL, or the API before `requirements-analysis.md` is `COMPLETE`, `model-design.md` exists, and architecture is `PASS`.
- Mapping and BRD: copy the templates, keep section and column names, delete every `[EXAMPLE]` row. User-stated rules and JSON paths are `USER_STATED` with `context_ref` `USER_INPUT`. Types, grain, and keys of tables already in the repository come from DDL or notebooks (`CONTEXT_STATED`). A value without a valid source is `MISSING_EVIDENCE` plus a question. Two disagreeing sources are `CONFLICT`. Do not invent a join separator for `full_address`.
- `brz_enrichment_result` is not in the repository. Columns and JSON paths the user gave are recorded from the sample. Table schema, MERGE key, watermark, and uniqueness are not in the repository: smallest probe, then stop at `waiting_evidence`.
- Save architecture `FILE` blocks with `python scripts/vv.py materialize <task-id> --write`.
- Record an architecture deviation in `decision.md` before further edits.
- Do not commit. Do not run Fabric DEV or `docker compose`.

## Verbatim request

Đã có nguồn cho slv_enr_poi_info_multi_lang và slv_enr_poi_destination.

Nguồn: bronze.brz_enrichment_result.
- event_type = LANG → dữ liệu cho slv_enr_poi_info_multi_lang
- event_type = DESTINATION → dữ liệu cho slv_enr_poi_destination

Đổi cột:
- slv_enr_poi_info_multi_lang.cost_vnd đổi thành cost
- gld_srv_poi_multi_lang.cost_vnd đổi thành cost
- apps.srv_poi_multi_lang.cost_vnd đổi thành cost
- API đọc cost thay cho cost_vnd
- slv_enr_poi_destination.street bỏ

Extract hai bảng silver theo mapping. Cập nhật mapping và transform gld_srv_poi_info.

slv_enr_poi_info_multi_lang:
- poi_id ← bronze.brz_enrichment_result.poi_id
- source_name ← bronze.brz_enrichment_result.source
- lang ← bronze.brz_enrichment_result.lang
- cost ← bronze.brz_enrichment_result.data.display.cost
- best_time ← bronze.brz_enrichment_result.data.display.best_time
- time_to_spend ← bronze.brz_enrichment_result.data.display.time_to_spend
- description ← bronze.brz_enrichment_result.data.description
- experiences ← bronze.brz_enrichment_result.data.experiences
- translated_at ← bronze.brz_enrichment_result.data.translated_at

slv_enr_poi_destination:
- poi_id ← bronze.brz_enrichment_result.poi_id
- source_name ← bronze.brz_enrichment_result.source
- ward ← data.address.new.ward.name
- ward_with_type ← data.address.new.ward.name_with_type
- district ← data.address.new.district.name
- district_with_type ← data.address.new.district.name_with_type
- city ← data.address.new.province.name
- city_with_type ← data.address.new.province.name_with_type
- formatted_address ← data.address.new.formatted_address
- old_ward ← data.address.old.ward.name
- old_ward_with_type ← data.address.old.ward.name_with_type
- old_district ← data.address.old.district.name
- old_district_with_type ← data.address.old.district.name_with_type
- old_city ← data.address.old.province.name
- old_city_with_type ← data.address.old.province.name_with_type
- old_formatted_address ← data.address.old.formatted_address
- lat ← data.lat
- lng ← data.lng
- full_address ← data.request.address
- destination ← data.destinations
- destination_id ← mảng data.destinations.id
- destination_name ← mảng data.destinations.name (cùng thứ tự với destination_id)
- country_code = null
- postal_code = null

gld_srv_poi_info:
- street ← slv_poi_entity_non_enrich.street
- full_address, ghép theo ưu tiên; một field trong nhóm null thì chuyển nhóm sau:
  Ưu tiên 1: slv_poi_entity_non_enrich.house_number + slv_poi_entity_non_enrich.street + slv_enr_poi_destination.formatted_address
  Ưu tiên 2: slv_poi_entity_non_enrich.house_number + slv_poi_entity_non_enrich.street + slv_enr_poi_destination.ward_with_type + slv_enr_poi_destination.city_with_type
  Ưu tiên 3: slv_enr_poi_destination.full_address

Sample (4 rows, `data` is a JSON string) is stored verbatim at `evidence/samples/brz_enrichment_result_lang_destination.tsv`. The JSON key tree without values is `evidence/payload-shape.md`. Do not copy sample rows into `MAPPING.md`.

## Classification rationale

- Complexity: high. The change renames and drops columns, adds an extract from a new bronze event source, and changes gold address composition across silver, gold, PostgreSQL, and the serving API.
- Risk: high. Cross-system column rename plus a new stateful extract (MERGE and watermark) can diverge silver, gold, and PostgreSQL if the bronze key or watermark is wrong.
- Architecture: required. Column and key changes, and logic moves from bronze to silver, gold, and PostgreSQL. `data_model_change` requires `model-design.md` before the Architect.
- Evidence: required. Repository search found no `brz_enrichment_result`. User-stated columns and JSON paths are recorded from the sample. Table schema, MERGE key, watermark, and uniqueness are not in the repository.
- Runtime proof: required. A correct extract from the live bronze table cannot be proven by repository inspection. API rename still needs the local verification lane; Fabric DEV proof stays a later runbook, not this phase.
- Reviewer routing: `state-correctness-reviewer` (watermark, MERGE idempotency, event order), `spark-runtime-reviewer` (notebooks), `sql-data-reviewer` (Delta DDL and MERGE), `api-contract-reviewer` (DTO and `sql/postgres/gld_srv_serve.pg.sql`), `jpa-performance-reviewer` (entity field rename). `risk-gate` because risk is high. Pipeline JSON is not in the stated scope, so `fabric-pipeline-reviewer` is not routed yet. No security-surface files are in scope, so `app-security-reviewer` is not routed.
