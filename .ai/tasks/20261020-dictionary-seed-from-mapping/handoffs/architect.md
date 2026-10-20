# Architect handoff: 20261020-dictionary-seed-from-mapping

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261020-dictionary-seed-from-mapping --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261020-dictionary-seed-from-mapping/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261020-dictionary-seed-from-mapping | phase=triage

## STATE

id: 20261020-dictionary-seed-from-mapping
title: Dictionary seed from mapping
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change, idempotency, runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- docs/context/3p-google/mapping_place_type.md
- docs/context/3p-google/mapping_amenities.md
- notebooks/NB_SETUP_POI_ENTITY.ipynb
- notebooks/NB_SETUP_POI_AMENITY.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- tests/test_poi_entity_contract.py
- tests/test_poi_amenity_contract.py

## VALIDATION

PASS

## RESUME

# Resume

Status: user_decision
Done this session: Recorded D-02 Homestay Lodging, D-03 one non-Other group, D-04 lines 203 and 216, D-05 existing amenity token map. `run-author --kind model` wrote `model-design.md` (`claude-opus-5-5`, medium). Closed model questions except column name and type.
Next action: After Bách answers D-06, copy the names and types into `decision.md` D-06. Transition `user_decision` to `triage`, then `waiting_architecture`, then `python scripts/vv.py run-gate 20261020-dictionary-seed-from-mapping`. `model-design.md` already exists.
Read next: `.ai/tasks/20261020-dictionary-seed-from-mapping/decision.md` row D-06; `.ai/tasks/20261020-dictionary-seed-from-mapping/model-design.md` section `Conflicts and questions` items 2 and 3.
Waiting on: D-06 physical column names and types for `default_range(min)`, `avg_range(min)`, `candidate_best_time_code`, `canonical_candidate`.

## REQUEST

# Request

## User outcome

Update lại tài liệu mapping_place_type.md và mapping_amenities.md theo ref_dictionary_place_type (bổ sung cả phần category_group vào mục 1.8; không xóa mục 1.9. và 1.9._), ref_dictionary_amenities (không xóa mục 2.5).
Trong tài liệu mapping_place_type.md có map data của partner và 3rd, các case category_group của Partner cũng cần map tương ứng. Hiện tại đang không map. Sau khi update lại, update lại tài liệu mapping_place_type.md.
Cấu hình thêm các mục 1.9._ vào bảng ref_dictionary_place_type tôi mới bổ sung trong file mapping_place_type.md.
Cấu hình thêm các mục 2.5 vào bảng ref_dictionary_amenities tôi mới bổ sung trong file mapping_amenities.md.

## Scope

### In scope

- `docs/context/3p-google/mapping_place_type.md`: điền mục 1.8 từ `category_group` của từ điển; giữ mục 1.9, 1.9.1, 1.9.2, 1.9.3.
- `docs/context/3p-google/mapping_amenities.md`: giữ mục 2.5.
- `lh_vv_silver.dbo.ref_dictionary_place_type` và `lh_vv_silver.dbo.ref_dictionary_amenities`: cột mới trong DDL; giá trị mới ghi cứng trong `SEED_ROWS`.
- Notebook: `notebooks/NB_SETUP_POI_ENTITY.ipynb`, `notebooks/NB_SETUP_POI_AMENITY.ipynb`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, `notebooks/NB_CREATE_DDL.ipynb`.
- Test assertion của seed và cột từ điển: `tests/test_poi_entity_contract.py`, `tests/test_poi_amenity_contract.py`.
- Runbook xóa và init lại đúng hai bảng. User chạy Fabric DEV.

### Out of scope

- Suy `category_group` bằng hàm trong code.
- Tạo `place_type` mới cho cụm không nêu token.
- Biến công thức mục 1.9.3 thành dòng seed.
- Bịa tên flag cho `parkingOptions.*` và câu Derived amenities.
- Agent đánh `gates.runtime`.

## Acceptance criteria

- Mục 1.8 có `category_group`. Mục 1.9, 1.9.1, 1.9.2, 1.9.3 và mục 2.5 còn nguyên.
- Mỗi dòng `SEED_ROWS` place type mang sẵn `category_group`. Hàm `category_group` và `with_category_group` không còn gán partner về `Other` bằng khớp token Google.
- Cột mới khai trong DDL của `NB_SETUP_POI_ENTITY` hoặc `NB_SETUP_POI_AMENITY`, và sửa cùng lúc `NB_SETUP_INITIAL_DDL` và `NB_CREATE_DDL`.
- Mục 1.9.1 và 1.9.2 ghi vào `SEED_ROWS` của dòng `place_type` đã có khi rule là exact type.
- Mục 2.5: mỗi `amenity_raw` liệt kê tường minh là một dòng `SEED_ROWS`. Đã có thì bổ sung đúng dòng đó. Chưa có thì `business_sector = other`, `amenity_group = other`, `amenity = amenity_raw`, `amenity_vi = amenity_raw`.
- Runbook: xóa, dựng lại, đếm dòng, quay lại. `p_apply` mặc định `false`. Bước apply tách riêng.

## Constraints

Cách làm đã chốt:

- Hai bảng `lh_vv_silver.dbo.ref_dictionary_place_type` và `lh_vv_silver.dbo.ref_dictionary_amenities` được phép xóa để init chạy lại. Runbook ghi bước xóa, dựng lại, đếm dòng và cách quay lại. User chạy Fabric DEV. Agent không đánh `gates.runtime`.
- Giá trị mới ghi cứng trong `SEED_ROWS` của `notebooks/NB_SETUP_POI_ENTITY.ipynb` và `notebooks/NB_SETUP_POI_AMENITY.ipynb`. Không suy `category_group` bằng hàm trong code. Hàm `category_group` và `with_category_group` hiện gán partner về `Other` vì khớp token Google. Bỏ cách gắn sau. Mỗi dòng `SEED_ROWS` mang sẵn `category_group`.
- Cột mới của bảng vẫn khai trong DDL của `NB_SETUP_POI_ENTITY` hoặc `NB_SETUP_POI_AMENITY`, và sửa cùng lúc `NB_SETUP_INITIAL_DDL` và `NB_CREATE_DDL`. Đó là khai báo cột, không phải logic gắn giá trị.

Quy tắc seed, không suy diễn:

- `category_group` của một place_type Google lấy theo mục 1.8 sau khi mục này được điền. place_type không nằm trong 1.8 thì `category_group = Other`.
- Dòng partner nhận `category_group` của Google Place Type cùng hàng trong `mapping_place_type.md`. Một Partner Portal Enum đứng ở nhiều hàng khác `category_group` thì ghi `USER_DECISION`, không chọn giúp.
- Mục 1.9.1 và 1.9.2 là cột và giá trị insert thêm vào `ref_dictionary_place_type`, ghi vào `SEED_ROWS` của dòng place_type đã có. Rule exact type gắn vào đúng place_type đó.
- Cụm "Có snorkel", "Có island" và các điều kiện không nêu token place_type: ghi `USER_DECISION`. Không tạo place_type mới.
- Mục 1.9.3 là công thức `deterministic_cost_vnd` từ `price_min` và `price_max`. Giữ trong tài liệu. Không biến công thức này thành dòng seed.
- Mục 2.5: mỗi amenity_raw liệt kê tường minh thành một dòng `SEED_ROWS`. Đã có thì bổ sung đúng dòng đó. Chưa có thì `business_sector = other`, `amenity_group = other`, `amenity = amenity_raw`, `amenity_vi = amenity_raw`.
- `parkingOptions.*` và câu "Derived amenities" không liệt kê token thì ghi `USER_DECISION`. Không bịa tên flag.
- Giữ nguyên mục 1.9, 1.9.1, 1.9.2, 1.9.3 và mục 2.5 trong hai file mapping.

## Classification rationale

- Complexity: high. Đổi cột từ điển và seed trên nhiều notebook DDL, có rebuild xóa-rồi-init.
- Risk: high. Seed là nguồn từ điển dùng chung; init lại hai bảng silver là thay trạng thái bền, rollback chỉ có trong runbook.
- Architecture: required. Đổi cột và grain giá trị seed; `data_model_change` đòi `model-design.md` trước Architect.
- Evidence: not required at triage. Lệch seed và mapping đọc được trong repository. Probe chỉ khi cổng architecture đòi.
- Runtime proof: required. User xóa và init lại hai bảng trên Fabric DEV. Agent không đánh `gates.runtime`.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, rồi `risk-gate`. Không fast lane.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Lệch seed và mapping | D-02 đến D-05 đã chốt. Mục 1.8 vẫn chỉ có heading cho đến khi implement điền từ `CATEGORY_GROUPS`. 21 token mục 1.7 và hai enum `Car with Driver`, `Campervan Rental` không có Google type: không thêm, vì không nằm trong quy tắc seed đã chốt. Seed giữ nhãn mục 1.5 cho `national_park`, `hiking_area`, `church`, `hindu_temple`, `mosque`, `synagogue`. | request.md Constraints; mapping_place_type.md 1.1–1.7 | 2026-10-20 |
| D-02 | Homestay | Homestay nhận Lodging. | User 2026-10-20 | 2026-10-20 |
| D-03 | Partner cùng hàng | một nhóm khác Other: nếu hàng chỉ có một nhóm khác Other, partner nhận nhóm đó. Token không có trong 1.8 vẫn là Other. Mục 1.8 điền đúng token `CATEGORY_GROUPS` hiện có. | User 2026-10-20; NB_SETUP_POI_ENTITY `CATEGORY_GROUPS` | 2026-10-20 |
| D-04 | Place type chưa có | D-04 thay câu Constraints "không tạo place_type mới" cho các token trong mục 1.9.1 và 1.9.2. Đã có trong `place_type` thì thêm vào dòng đó. Chưa có thì thêm dòng `google`, `business_sector`/`business_category`/`business_category_vi` = `other`, `category_group` = `Other`. Khớp đúng chuỗi; khoảng trắng Latin đổi `_` một lần (`water park` → `water_park` đã có; `night market` → thêm `night_market`). Không gắn nhầm `temple`, `boat`, `hiking`, `wellness`, `shopping`, `mall` sang place_type dài hơn. `suối` và `thác` giữ đúng chữ. `OUTDOOR_TYPES` không có danh sách; không gán `dry_season`. Mọi dòng nhận `default_range`/`avg_range` theo `category_group` ở bảng L193–L201. Bảng đặc biệt L205–L210 ghi đè đúng `place_type` đó. Nhiều rule 1.9.2: priority số nhỏ hơn thắng. Không match thì `candidate_best_time_code` = `all`. `is_active` của dòng mới là `true`, giống `VALUES` hiện tại của MERGE. Mục 1.9.3 không thành dòng seed. Tên cột vật lý và kiểu dữ liệu: D-06. | mapping_place_type.md L193–L231; User 2026-10-20 | 2026-10-20 |
| D-05 | Amenity 2.5 | Liệt kê token. Hãy kiểm tra hiện có và map data tương ứng. Đã có đúng `amenity_raw` thì giữ dòng, không thêm cột alias: `delivery`, `dineIn`, `outdoorSeating`, `liveMusic`, `servesCocktails`, `goodForChildren`, `restroom`, `goodForGroups`, `goodForWatchingSports`, `paymentOptions.acceptsCreditCards`, `accessibilityOptions.wheelchairAccessibleParking`, và ba tên rút gọn trỏ tới `accessibilityOptions.wheelchairAccessibleEntrance`, `accessibilityOptions.wheelchairAccessibleRestroom`, `accessibilityOptions.wheelchairAccessibleSeating`. `parkingOptions.*` chỉ 8 token đã có ở mục 2.1–2.4. Derived amenities chỉ dòng seed đã có (`swimming_pool`, json_type gym/spa/bar/restaurant, `hot_spring`, `sauna`, `garden`, `botanical_garden`, `electric_vehicle_charging_station`). Coworking không có field: không thêm. 17 flag chưa có thì thêm dòng `google` / `other` / `other` / `amenity_raw` / `amenity_raw`: `takeout`, `curbsidePickup`, `reservable`, `servesBreakfast`, `servesLunch`, `servesDinner`, `servesBeer`, `servesWine`, `servesBrunch`, `servesVegetarianFood`, `menuForChildren`, `servesDessert`, `servesCoffee`, `allowsDogs`, `pureServiceAreaBusiness`, `acceptsDebitCards`, `acceptsNfc`. `is_active` = `true` như MERGE hiện tại. | User 2026-10-20; mapping_amenities.md 2.1–2.5 | 2026-10-20 |
| D-06 | Tên cột và kiểu | two_ints: `range_low_min` INT, `range_high_min` INT, `avg_range_min` INT, hai cột best time STRING. Hai cột best time là `candidate_best_time_code` STRING và `canonical_candidate` STRING. Chuỗi `1,200–1,200` hoặc `60–90` tách tại dấu gạch: số trước là `range_low_min`, số sau là `range_high_min`, bỏ dấu phẩy. `avg_range_min` bỏ dấu phẩy. | User 2026-10-20 | 2026-10-20 |

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
- decision.md | 5772 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 24627 bytes | large: use toc/show
- handoffs/author-input.md | 950 bytes
- model-design.md | 11669 bytes
- request.md | 5953 bytes
- resume.md | 914 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1634 bytes

## NEXT

python scripts/vv.py run-gate 20261020-dictionary-seed-from-mapping

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### docs/context/3p-google/mapping_place_type.md (54616 bytes)

# **1.1 Accommodation** | L1-L23
# **1.2 F&B** | L24-L55
# **1.3 Spa & Wellness** | L56-L77
# **1.4 Shopping & Retail** | L78-L103
# **1.5 Attraction** | L104-L142
# **1.6 Vehicle Rental** | L143-L154
# **1.7. Public POI & Infrastructure (Không thuộc quản lý của Partner)** | L155-L183
# **1.8. Category Group** | L184-L185
# **1.9. Category Group Estimation** | L186-L270
## 1.9.1 Để tính candidate_time_to_spend_minutes | L189-L211
## 1.9.2 Để tính candidate_best_time_code và candidate_best_time | L212-L243
## 1.9.3 deterministic_cost_vnd | L244-L270

### docs/context/3p-google/mapping_amenities.md (27875 bytes)

#### **2.1 accomodation** | L1-L41
#### **2.2 f_n_b** | L42-L86
#### **2.3 attraction** | L87-L122
#### **2.4 shopping_n_retail** | L123-L141
#### **2.5 Tạo danh sách TRUE Amenity** | L142-L155

### notebooks/NB_SETUP_POI_ENTITY.ipynb (60157 bytes)

[0] markdown id=a1setupmd json=47-58 lines=5 | NB_SETUP_POI_ENTITY | defs: none
[1] code id=a1setupparam json=59-76 lines=1 | p_apply = "false" | defs: none
[2] code id=a1setuprun json=77-91 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=a1setupseed json=92-535 lines=430 | import re | defs: category_group, with_category_group, validate_seed
[4] code id=a1setupplan json=536-589 lines=40 | import json | defs: none
[5] code id=a1setupddl json=590-630 lines=27 | spark.sql(""" | defs: none
[6] code id=a1setupmerge json=631-699 lines=55 | def _seed_merge(): | defs: _seed_merge
[7] code id=a1setupedges json=700-900 lines=187 | import uuid | defs: setup_edge_issues, _write_edges
[8] code id=a1setupexit json=901-925 lines=11 | import json | defs: none

### notebooks/NB_SETUP_POI_AMENITY.ipynb (52756 bytes)

[0] markdown id=c1setupmd json=47-56 lines=3 | NB_SETUP_POI_AMENITY | defs: none
[1] code id=c1setupparam json=57-66 lines=1 | p_apply = "false" | defs: none
[2] code id=c1setuprun json=67-76 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=c1setupseed json=77-321 lines=236 | import re | defs: amenity_keys, validate_seed
[4] code id=c1setupplan json=322-388 lines=58 | import json | defs: none
[5] code id=c1setupddl json=389-453 lines=56 | spark.sql(""" | defs: none
[6] code id=c1setupmerge json=454-530 lines=68 | def _seed_merge(): | defs: _seed_merge
[7] code id=c1setupedges json=531-716 lines=177 | import uuid | defs: setup_edge_issues, _write_edges
[8] code id=c1setupexit json=717-737 lines=12 | import json | defs: none

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (182459 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-426 lines=325 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=427-441 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=442-639 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=640-654 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=655-735 lines=67 | _FL00, _ENR, _SLV1H = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV | defs: none
[8] code id=init_seed_place_type json=736-1182 lines=433 | import re | defs: category_group, with_category_group, validate_seed
[9] code id=init_seed_amenity json=1183-1434 lines=238 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=1435-1592 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=1593-1607 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=1608-1798 lines=177 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=1799-1813 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=1814-1828 lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (135310 bytes)

[0] markdown id=b0b1203a-7c40-48bf-bfc9-7b29d7064bdc json=3-25 lines=6 | NB_CREATE_DDL — 7 bảng control `lh_vv_ctrl.dbo` | defs: none
[1] markdown id=b7e4c1a0-6f28-4d3e-9a15-2c8d0e4f6a91 json=26-36 lines=4 | Ghi chú migration 08/10 | defs: none
[2] markdown id=d20a367e-98da-4b91-9237-dd2b2cebfeae json=37-54 lines=1 | Tạo bảng ctrl_mng_pipeline_config | defs: none
[3] code id=80154b61-ea1a-415b-834c-3c07d689d036 json=55-177 lines=108 | %%sql | defs: none
[4] markdown id=<none> json=178-188 lines=5 | Reset silver (DROP/DELETE) không nằm trong luồng tạo bảng. | defs: none
[5] code id=502cd242 json=189-242 lines=40 | %%sql | defs: none
[6] markdown id=a0c11600-5f15-4ec4-ab3b-cd590b5ce6a8 json=243-260 lines=1 | Tạo bảng ctrl_mng_watermark | defs: none
[7] markdown id=e80b9799-8de0-4319-8c62-be8096d373c8 json=261-288 lines=11 | **[SỬA 03/10] Bỏ cell MERGE watermark từ `lh_vv_bronze.partner.brz_watermark`**  | defs: none
[8] code id=3ea73e14-6a1f-42a5-b960-34123b0a3fc4 json=289-346 lines=43 | %%sql | defs: none
[9] markdown id=ed3d2dc0-d9f4-4cd7-b5aa-5e65afb7aca0 json=347-364 lines=1 | Tạo bảng ctrl_cfg_schema_registry | defs: none
[10] code id=d06c9671-6b88-4afa-97a8-d028f6b9e936 json=365-408 lines=30 | CONFIG_TABLE = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry" | defs: none
[11] code id=28e2be98-7f9a-41d5-b7f8-b4d4a5baf5ff json=409-957 lines=535 | TABLE_CONFIGS = [ | defs: none
[12] code id=0f228dc1-7bc8-4ed2-a10f-e6125a806e83 json=958-1158 lines=186 | from pyspark.sql.types import ( | defs: resolve_type, flatten_table_configs, validate_rows, seed_registry, show_registry
[13] markdown id=7517dd85-f292-4361-9d9d-6bad3f2e4f34 json=1159-1179 lines=4 | **[THÊM 03/10 - 3P] Seed registry nguồn 3rd-party `brz_3rd_crawler_poi_stream`** | defs: none
[14] code id=e9c137c5-c9fc-4f8f-a925-bc511cfd71a7 json=1180-1377 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[15] code id=0271d481-4188-43ab-8cb4-03acd3452550 json=1378-1397 lines=5 | seed_registry(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream" | defs: none
[16] markdown id=5c2996a4-3ddc-4924-8645-c0cc545cdd63 json=1398-1415 lines=1 | Tạo các bảng log & debug | defs: none
[17] code id=7dad05d9-20f0-4ab4-af1e-dec1dfe5d8cb json=1416-1557 lines=127 | %%sql | defs: none
[18] code id=ea524452-c135-4ef4-b4a8-3a076fa67ee7 json=1558-1593 lines=22 | GOLD_LOG_COLUMNS = ( | defs: none
[19] markdown id=de14c4c2-7925-4582-b080-8b0a660fb99c json=1594-1611 lines=1 | Kiểm tra cấu hình | defs: none
[20] code id=6e95fc60-2ef9-47af-a250-95844179c188 json=1612-1697 lines=71 | %%sql | defs: none
[21] code id=5784a286-d45c-4be8-8223-5a43800b6e2b json=1698-1732 lines=17 | %%sql | defs: none
[22] markdown id=enrddlmd json=1733-1742 lines=3 | [THÊM 13/10] Gold enr và cạnh PL_VV_TRANS_SLV_TO_ENR_15P | defs: none
[23] code id=enrddlpy json=1743-1886 lines=130 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _ddl, _expected_type
[24] markdown id=nonenrmd json=1887-1899 lines=1 | [THÊM 19/10] 20261019-poi-entity-non-enrich | defs: none
[25] code id=nonenrpy json=1900-1977 lines=64 | import re | defs: category_group, with_category_group
