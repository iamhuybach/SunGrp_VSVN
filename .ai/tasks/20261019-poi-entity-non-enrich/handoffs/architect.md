# Architect handoff: 20261019-poi-entity-non-enrich

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261019-poi-entity-non-enrich/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

The first non-blank line is `RESULT: PASS` or `RESULT: EVIDENCE_REQUIRED`. Cover: scope, non-goals, invariants, state ownership, grain and keys, ordering, transaction and commit boundaries, idempotency, concurrency, retry and recovery, partial failure, observability, security, rollout, rollback and forward recovery, implementation plan, and verification. Compare material alternatives and explain the selected trade-off. Write a section that does not apply as one line: `Not applicable: <reason>`.

Size: for `low` or `medium` risk, keep the document under 25 KB, excluding `FILE:` blocks. For `high` or `critical` risk, use the space the failure analysis needs, without repeating the request or the evidence.

Files that Main must save verbatim go in blocks: a line `FILE: <repo-relative path>`, the exact content, then a line `END_FILE`. Every path must be in `scope.files`.

## Main brief contract

Return a separate Main brief, at most 14,000 characters, in English. It is the only part Main reads by default. Use `###` headings only, in this order:

1. `Decision`: at most 5 lines.
2. `Invariants Main must preserve`: at most 10 testable bullets.
3. `Edit list`: table `# | file | anchor (cell id, function, or heading) | change | done-when`, one row per anchor.
4. `Order and stop points`: numbered; mark each stop for evidence or a user decision.
5. `Tests and verification`: exact test names and commands.
6. `Read only if needed`: full-document headings mapped to the edit rows they justify.

Do not restate the request or the evidence in the brief. Code longer than 15 lines goes in the full document under a heading the edit list references.

If evidence is missing, list exact probes and the decisions each one blocks. Do not implement code, update task state, or fill gaps with assumptions.

## Generated context pack

`vv.py` generated this block. Do not re-read the task state, request, decision ledger, or task file list it covers.

# Context 20261019-poi-entity-non-enrich | phase=triage

## STATE

id: 20261019-poi-entity-non-enrich
title: Rename POI entity and drop duplicate silver columns
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: cross_system, stateful_logic, idempotency, cross_state_impact, design_tradeoffs, data_evidence_required, runtime_proof_required
gates: evidence=pass, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: state-correctness-reviewer, spark-runtime-reviewer, sql-data-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_SLV_POI_ENTITY.ipynb
- notebooks/NB_SETUP_POI_ENTITY.ipynb
- notebooks/NB_SLV_POI_AMENITY.ipynb
- notebooks/NB_SETUP_POI_AMENITY.ipynb
- notebooks/NB_ENR_POI_INFO.ipynb
- notebooks/NB_ENR_POI_COORDINATE.ipynb
- docs/context/01_DATA_MODEL.md
- docs/context/02_NAMING_CONVENTION.md
- docs/context/CTRL_TABLES_CONTEXT.md
- docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md
- docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md
- docs/requirements/20261012-map-gld-enr-poi-tables/BRD.md
- tests/test_poi_entity_contract.py
- tests/test_poi_amenity_contract.py
- tests/test_initial_ddl_contract.py

## VALIDATION

PASS

## RESUME

# Resume 20261019-poi-entity-non-enrich

Status: user_decision
Done this session: Traced ai_poi type fields through notebooks 1, 2.1, and 2.3. Notebook 2.1 writes business_category from a sector path in amentities, poi_types from partners.type, and subcategory_tags as None. No primary_type column. D3 still open. No source edits.
Next action: New chat. Record the D3 answer verbatim in decision.md. Then transition user_decision to triage, triage to waiting_architecture, and run python scripts/vv.py run-gate 20261019-poi-entity-non-enrich. Stop after the gate. Do not implement.
Read next: decision.md lịch sử 2026-10-19 lần ngược ai_poi; notebooks_lgc/pl_transform_partner_userprofile_cms/2.1. transform_partner_to_gold_poi_master.ipynb build_row_base and ai_poi row
Waiting on: D3 category_group for partner rows

Prompt:
Task 20261019-poi-entity-non-enrich
Phase: architecture
D3 category_group dòng partner: <một trong các phương án ở closeout>
Ghi D3 vào ledger. transition user_decision -> triage -> waiting_architecture. python scripts/vv.py run-gate 20261019-poi-entity-non-enrich. Dừng sau gate. Không sửa source.

## REQUEST

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


## DECISIONS

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

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: missing
size: 483 bytes

## FILES

- architecture.md | 483 bytes | placeholder
- decision.md | 11303 bytes
- evidence/plan.md | 1900 bytes
- evidence/probes/partner-json-shape.py | 6001 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/partner-json-shape.txt | 1055 bytes
- request.md | 6073 bytes
- resume.md | 1163 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 2071 bytes

## NEXT

python scripts/vv.py run-gate 20261019-poi-entity-non-enrich

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_CREATE_DDL.ipynb (142872 bytes)

[0] markdown id=b0b1203a-7c40-48bf-bfc9-7b29d7064bdc json=unknown lines=6 | NB_CREATE_DDL — 7 bảng control `lh_vv_ctrl.dbo` | defs: none
[1] markdown id=b7e4c1a0-6f28-4d3e-9a15-2c8d0e4f6a91 json=unknown lines=4 | Ghi chú migration 08/10 | defs: none
[2] markdown id=d20a367e-98da-4b91-9237-dd2b2cebfeae json=unknown lines=1 | Tạo bảng ctrl_mng_pipeline_config | defs: none
[3] code id=80154b61-ea1a-415b-834c-3c07d689d036 json=unknown lines=108 | %%sql | defs: none
[4] markdown id=<none> json=unknown lines=5 | Reset silver (DROP/DELETE) không nằm trong luồng tạo bảng. | defs: none
[5] code id=502cd242 json=unknown lines=40 | %%sql | defs: none
[6] markdown id=a0c11600-5f15-4ec4-ab3b-cd590b5ce6a8 json=unknown lines=1 | Tạo bảng ctrl_mng_watermark | defs: none
[7] markdown id=e80b9799-8de0-4319-8c62-be8096d373c8 json=unknown lines=11 | **[SỬA 03/10] Bỏ cell MERGE watermark từ `lh_vv_bronze.partner.brz_watermark`**  | defs: none
[8] code id=3ea73e14-6a1f-42a5-b960-34123b0a3fc4 json=unknown lines=43 | %%sql | defs: none
[9] markdown id=ed3d2dc0-d9f4-4cd7-b5aa-5e65afb7aca0 json=unknown lines=1 | Tạo bảng ctrl_cfg_schema_registry | defs: none
[10] code id=d06c9671-6b88-4afa-97a8-d028f6b9e936 json=unknown lines=30 | CONFIG_TABLE = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry" | defs: none
[11] code id=28e2be98-7f9a-41d5-b7f8-b4d4a5baf5ff json=unknown lines=535 | TABLE_CONFIGS = [ | defs: none
[12] code id=0f228dc1-7bc8-4ed2-a10f-e6125a806e83 json=unknown lines=186 | from pyspark.sql.types import ( | defs: resolve_type, flatten_table_configs, validate_rows, seed_registry, show_registry
[13] markdown id=7517dd85-f292-4361-9d9d-6bad3f2e4f34 json=unknown lines=4 | **[THÊM 03/10 - 3P] Seed registry nguồn 3rd-party `brz_3rd_crawler_poi_stream`** | defs: none
[14] code id=e9c137c5-c9fc-4f8f-a925-bc511cfd71a7 json=unknown lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[15] code id=0271d481-4188-43ab-8cb4-03acd3452550 json=unknown lines=5 | seed_registry(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream" | defs: none
[16] markdown id=5c2996a4-3ddc-4924-8645-c0cc545cdd63 json=unknown lines=1 | Tạo các bảng log & debug | defs: none
[17] code id=7dad05d9-20f0-4ab4-af1e-dec1dfe5d8cb json=unknown lines=127 | %%sql | defs: none
[18] code id=ea524452-c135-4ef4-b4a8-3a076fa67ee7 json=unknown lines=22 | GOLD_LOG_COLUMNS = ( | defs: none
[19] markdown id=de14c4c2-7925-4582-b080-8b0a660fb99c json=unknown lines=1 | Kiểm tra cấu hình | defs: none
[20] code id=6e95fc60-2ef9-47af-a250-95844179c188 json=unknown lines=71 | %%sql | defs: none
[21] code id=5784a286-d45c-4be8-8223-5a43800b6e2b json=unknown lines=17 | %%sql | defs: none
[22] markdown id=enrddlmd json=unknown lines=3 | [THÊM 13/10] Gold enr và cạnh PL_VV_TRANS_SLV_TO_ENR_15P | defs: none
[23] code id=enrddlpy json=unknown lines=130 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _ddl, _expected_type

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (156901 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-102 lines=317 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=103-117 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=118-132 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=133-147 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=148-162 lines=64 | _FL00, _ENR, _SLV1H = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV | defs: none
[8] code id=init_seed_place_type json=163-177 lines=400 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=178-192 lines=364 | SEED_SECTORS = ("accommodation", "f_n_b", "attraction", "shopping_n_retail") | defs: validate_seed
[10] code id=init_plan json=193-207 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=208-222 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=223-237 lines=177 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=238-252 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=253-267 lines=7 | summary = { | defs: none

### notebooks/NB_SETUP_POI_ENTITY.ipynb (51687 bytes)

[0] markdown id=a1setupmd json=47-56 lines=3 | NB_SETUP_POI_ENTITY | defs: none
[1] code id=a1setupparam json=57-74 lines=1 | p_apply = "false" | defs: none
[2] code id=a1setuprun json=75-89 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=a1setupseed json=90-501 lines=398 | import re | defs: validate_seed
[4] code id=a1setupplan json=502-548 lines=33 | import json | defs: none
[5] code id=a1setupddl json=549-587 lines=25 | spark.sql(""" | defs: none
[6] code id=a1setupmerge json=588-655 lines=54 | def _seed_merge(): | defs: _seed_merge
[7] code id=a1setupedges json=656-775 lines=106 | def _write_edges(): | defs: _write_edges
[8] code id=a1setupexit json=776-799 lines=10 | import json | defs: none

### notebooks/NB_SETUP_POI_AMENITY.ipynb (40277 bytes)

[0] markdown id=c1setupmd json=47-56 lines=3 | NB_SETUP_POI_AMENITY | defs: none
[1] code id=c1setupparam json=57-66 lines=1 | p_apply = "false" | defs: none
[2] code id=c1setuprun json=67-76 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=c1setupseed json=77-447 lines=362 | SEED_SECTORS = ("accommodation", "f_n_b", "attraction", "shopping_n_retail") | defs: validate_seed
[4] code id=c1setupplan json=448-501 lines=45 | import json | defs: none
[5] code id=c1setupddl json=502-566 lines=56 | spark.sql(""" | defs: none
[6] code id=c1setupmerge json=567-642 lines=67 | def _seed_merge(): | defs: _seed_merge
[7] code id=c1setupedges json=643-766 lines=115 | def _write_edges(): | defs: _write_edges
[8] code id=c1setupexit json=767-785 lines=10 | import json | defs: none

### docs/context/01_DATA_MODEL.md (31193 bytes)

# 01 — Data Model mới của Visit Vietnam (POI) trên Microsoft Fabric | L1-L395
## 1. Bối cảnh nền tảng | L7-L18
## 2. Nguyên tắc phân tầng (đã chốt) | L19-L35
## 3. Sơ đồ tổng | L36-L75
## 4. Bronze — bảng raw | L76-L253
### Cấu trúc `normalized_payload` | L86-L253
## 5. Silver L1 — extract (đúng cấu trúc nguồn) | L254-L313
### 5.1 Partner `slv_pn_*` (23 bảng, `load_mode = CDC`) | L256-L287
### 5.2 3rd-party `slv_3p_poi_*` (10 bảng trong registry, 9 active, snapshot) | L288-L313
## 6. Silver L2 — tích hợp POI (7 node) | L314-L343
### 6.1 Bảng ref (rule dạng dữ liệu) | L330-L343
## 7. Gold — 3 bảng phục vụ (`lh_vv_gold.dbo`) | L344-L353
## 8. Định danh | L354-L366
## 9. Model cũ (vẫn chạy song song) và lý do đổi | L367-L376
## 10. Ý nghĩa của model mới | L377-L386
## 11. Hướng sắp tới (chưa làm) | L387-L395

### docs/context/CTRL_TABLES_CONTEXT.md (45327 bytes)

# CTRL_TABLES_CONTEXT — 7 bảng control `lh_vv_ctrl.dbo` | L1-L564
## 1. Tổng quan | L7-L24
## 2. Quan hệ | L25-L48
## 3. `ctrl_mng_pipeline_config` | L49-L140
### DDL | L54-L73
### Cột | L74-L89
### Dữ liệu hiện có | L90-L130
### Thao tác thường gặp | L131-L140
## 4. `ctrl_mng_watermark` | L141-L231
### DDL | L151-L175
### Cột theo loại dòng | L176-L200
### Ghi chú migration — số đo watermark trước 08/10 tại `lh_vv_bronze.ctrl` (dòng 3P cũ `wm_transform_poi_raw_event`) | L201-L209
### Thao tác thường gặp | L210-L231
## 5. `ctrl_cfg_schema_registry` | L232-L321
### DDL | L237-L261
### Luật cấu hình (lib kiểm tra, sai → `ConfigError` trước khi ghi) | L262-L272
### Dữ liệu hiện có (seed `NB_CREATE_DDL`, cấu hình chốt 04/10 chiều) | L273-L321
## 6. `ctrl_log_run` — 1 dòng / lần chạy notebook (khoá `exec_id`) | L322-L392
### DDL | L326-L366
### Cột khác nghĩa giữa extract và NB_00 | L367-L381
### Ghi chú migration — log đã thấy trước 08/10 tại vị trí control cũ | L382-L392
## 7. `ctrl_log_table_run` — 1 dòng / bảng đích (hoặc node) / lần chạy | L393-L448
### DDL | L395-L448
## 8. `ctrl_cdc_state` — 1 dòng / entity / bảng đích (chỉ extract) | L449-L488
### DDL | L453-L488
## 9. `ctrl_cdc_reject` — 1 dòng / event (hoặc phần tử) lỗi (chỉ extract) | L489-L542
### DDL | L491-L542
## 10. Lịch sử thay đổi (tóm tắt) | L543-L554
## 11. Việc còn lại liên quan ctrl | L555-L564

### docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md (45965 bytes)

# Mẫu Mapping nguồn → đích (VSVN) | L1-L297
## Cách điền | L8-L20
## Quy ước dùng chung | L21-L117
### Giá trị cho phép | L25-L51
### Tiền tố bảng theo tầng | L52-L64
### Định danh | L65-L99
### Liên kết giữa hai file | L100-L106
### Ràng buộc nền tảng | L107-L117
## 1. Thông tin tài liệu | L118-L130
## 2. Luồng xử lý | L131-L144
## 3. Bảng nguồn | L145-L159
## 4. Bảng đích | L160-L167
## 5. Mapping cột | L168-L218
## 6. Mục thiếu evidence | L219-L225
## 7. Mâu thuẫn trong repository | L226-L232
## 8. Câu hỏi mở | L233-L297

### docs/requirements/20261012-map-gld-enr-poi-tables/BRD.md (33193 bytes)

# Mẫu Business Requirements Document (BRD) — VSVN | L1-L256
## Cách điền | L8-L22
## Quy ước dùng chung | L23-L119
### Giá trị cho phép | L27-L53
### Tiền tố bảng theo tầng | L54-L66
### Định danh | L67-L101
### Liên kết giữa hai file | L102-L108
### Ràng buộc nền tảng | L109-L119
## 1. Thông tin tài liệu | L120-L132
## 2. Bối cảnh và mục tiêu | L133-L138
## 3. Phạm vi | L139-L150
## 4. Bên sử dụng dữ liệu | L151-L156
## 5. Yêu cầu nghiệp vụ | L157-L164
## 6. Nguồn dữ liệu | L165-L179
## 7. Rule nghiệp vụ | L180-L189
## 8. Định danh | L190-L196
## 9. Yêu cầu phi chức năng | L197-L202
## 10. Tiêu chí nghiệm thu | L203-L211
## 11. Mục thiếu evidence | L212-L218
## 12. Mâu thuẫn trong repository | L219-L225
## 13. Câu hỏi mở | L226-L256
