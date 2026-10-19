# Architect handoff: 20261019-amenity-raw-key-only

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261019-amenity-raw-key-only --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261019-amenity-raw-key-only/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261019-amenity-raw-key-only | phase=triage

## STATE

id: 20261019-amenity-raw-key-only
title: Amenity raw values become keys
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: stateful_logic, idempotency, transaction_boundaries, cross_state_impact, design_tradeoffs, runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SLV_POI_AMENITY.ipynb
- notebooks/NB_SETUP_POI_AMENITY.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- tests/test_poi_amenity_contract.py
- tests/test_initial_ddl_contract.py
- docs/context/3p-google/mapping_amenities.md
- docs/context/01_DATA_MODEL.md

## VALIDATION

PASS

## RESUME

# Resume

Status: waiting_architecture

Done this session: Task `20261019-amenity-raw-key-only` created. Request, ledger D1-D5, and seed census recorded. Classification: complexity high, risk high, architecture required, evidence not required, runtime required. No DEV probe. `run-gate` started Claude Architect and failed before writing architecture.

Next action: Rerun `python scripts/vv.py run-gate 20261019-amenity-raw-key-only` after the working tree stops changing. The immutability check failed because these files changed during the run and are not this task: `.ai/prompts/architect.md`, `.ai/prompts/author-proposal.md`, `.ai/prompts/author-runbook.md`, `.ai/tasks/_template/task-state.yaml`, `scripts/agent_runner.py`, `scripts/vv.py`, plus the pre-existing delete `docs/context/3p-google/Mapping_POI_Service_Data.md` and task `20261019-agent-system-claude-opus-design`. Do not revert them here. `rounds.architecture` is still 0. `architecture.md` is still the placeholder.

Read next: `.ai/tasks/20261019-amenity-raw-key-only/request.md` §Repository impact; `decision.md` `Quyết định hiện hành`.

Waiting on: a quiet working tree, then the architecture gate.

## REQUEST

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


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Phân loại | Đổi giá trị khóa, số dòng seed và cách MERGE: architecture bắt buộc, risk high, không fast lane. Review gồm sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer và risk-gate. | request.md §Classification rationale | 2026-10-19 |
| D2 | Evidence | Không probe DEV. Mọi dạng amenity_raw hiện có nằm trong SEED_ROWS của repository. | request.md §Repository impact | 2026-10-19 |
| D3 | Runtime | Step chạy lại full hai bảng là runtime-runbook sau review PASS. User chạy trên Fabric DEV. Agent không đánh gates.runtime. | request.md §User outcome | 2026-10-19 |
| D4 | Khóa và seed | Khóa từ điển vẫn là (source_name, business_sector, amenity_group, amenity_raw, amenity). Khóa slv_poi_amenity vẫn gồm amenity_raw. Seed hiện insert-only. | request.md §Acceptance criteria | 2026-10-19 |
| D5 | Cạnh ctrl | Cạnh ctrl_mng_pipeline_config của slv_poi_amenity không được nhân đôi. | request.md §Acceptance criteria | 2026-10-19 |

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
- decision.md | 2158 bytes
- evidence/plan.md | 1227 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 18102 bytes
- request.md | 7949 bytes
- resume.md | 1191 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1567 bytes

## NEXT

python scripts/vv.py run-gate 20261019-amenity-raw-key-only

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_POI_AMENITY.ipynb (43993 bytes)

[0] markdown id=c1setupmd json=47-56 lines=3 | NB_SETUP_POI_AMENITY | defs: none
[1] code id=c1setupparam json=57-66 lines=1 | p_apply = "false" | defs: none
[2] code id=c1setuprun json=67-76 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=c1setupseed json=77-447 lines=362 | SEED_SECTORS = ("accommodation", "f_n_b", "attraction", "shopping_n_retail") | defs: validate_seed
[4] code id=c1setupplan json=448-501 lines=45 | import json | defs: none
[5] code id=c1setupddl json=502-566 lines=56 | spark.sql(""" | defs: none
[6] code id=c1setupmerge json=567-642 lines=67 | def _seed_merge(): | defs: _seed_merge
[7] code id=c1setupedges json=643-828 lines=177 | import uuid | defs: setup_edge_issues, _write_edges
[8] code id=c1setupexit json=829-848 lines=11 | import json | defs: none

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (171108 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-426 lines=325 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=427-441 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=442-639 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=640-654 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=655-735 lines=67 | _FL00, _ENR, _SLV1H = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV | defs: none
[8] code id=init_seed_place_type json=736-1182 lines=433 | import re | defs: category_group, with_category_group, validate_seed
[9] code id=init_seed_amenity json=1183-1197 lines=364 | SEED_SECTORS = ("accommodation", "f_n_b", "attraction", "shopping_n_retail") | defs: validate_seed
[10] code id=init_plan json=1198-1355 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=1356-1370 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=1371-1561 lines=177 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=1562-1576 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=1577-1591 lines=7 | summary = { | defs: none

### docs/context/3p-google/mapping_amenities.md (26371 bytes)

#### **2.1 accomodation** | L1-L41
#### **2.2 f_n_b** | L42-L86
#### **2.3 attraction** | L87-L122
#### **2.4 shopping_n_retail** | L123-L140

### docs/context/01_DATA_MODEL.md (31999 bytes)

# 01 — Data Model mới của Visit Vietnam (POI) trên Microsoft Fabric | L1-L399
## 1. Bối cảnh nền tảng | L7-L18
## 2. Nguyên tắc phân tầng (đã chốt) | L19-L35
## 3. Sơ đồ tổng | L36-L75
## 4. Bronze — bảng raw | L76-L253
### Cấu trúc `normalized_payload` | L86-L253
## 5. Silver L1 — extract (đúng cấu trúc nguồn) | L254-L317
### 5.1 Partner `slv_pn_*` (23 bảng, `load_mode = CDC`) | L256-L287
### 5.2 3rd-party `slv_3p_poi_*` (10 bảng trong registry, 9 active, snapshot) | L288-L317
## 6. Silver L2 — tích hợp POI (7 node) | L318-L347
### 6.1 Bảng ref (rule dạng dữ liệu) | L334-L347
## 7. Gold — 3 bảng phục vụ (`lh_vv_gold.dbo`) | L348-L357
## 8. Định danh | L358-L370
## 9. Model cũ (vẫn chạy song song) và lý do đổi | L371-L380
## 10. Ý nghĩa của model mới | L381-L390
## 11. Hướng sắp tới (chưa làm) | L391-L399
