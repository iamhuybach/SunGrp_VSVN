# Architect handoff: 20261109-srv-poi-amenity-en

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261109-srv-poi-amenity-en --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261109-srv-poi-amenity-en/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261109-srv-poi-amenity-en | phase=triage

## STATE

id: 20261109-srv-poi-amenity-en
title: Amenity snake_case code and amenity_en through silver, gold, PostgreSQL, and the amenities API
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change, cross_system, cross_state_impact, runtime_proof_required
gates: evidence=not_required, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: spark-runtime-reviewer, sql-data-reviewer, api-contract-reviewer, jpa-performance-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_SETUP_POI_AMENITY.ipynb
- notebooks/NB_SLV_POI_AMENITY.ipynb
- notebooks/NB_GLD_SRV_POI_AMENITY.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- sql/postgres/gld_srv_serve.pg.sql
- docs/context/mapping_gld_srv_poi_amenity.md
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/PoiController.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiAmenityGroupResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiAmenity.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/PoiAmenityId.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/repository/SrvPoiAmenityRepository.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java
- tests/test_poi_amenity_contract.py
- tests/test_srv_poi_serving_contract.py
- tests/test_poi_media_amenity_contract.py
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java
- docs/context/01_DATA_MODEL.md

## VALIDATION

PASS

## RESUME

# Resume

## Status

user_decision. Task `20261109-srv-poi-amenity-en`. Model design exists. Architecture round 1 is `EVIDENCE_REQUIRED`. No implementation.

## Done this session

Closed D-01 (JSON sample) and D-02 (path stays `GET /api/v1/pois/{poi_id}/amenities`). Ran `run-author --kind model` and `run-gate`. Architect blocked on U-1, U-2, and U-3. No Fabric probe. Added M-1 files to `scope.files`. Main did not pick an option.

## Next action

After the user answers U-1, U-2, and U-3, copy the answers into `decision.md`. Transition `user_decision` to `triage`, update `handoffs/author-input.md`, run `python scripts/vv.py run-author 20261109-srv-poi-amenity-en --kind model`, transition `triage` to `waiting_architecture`, then `python scripts/vv.py run-gate 20261109-srv-poi-amenity-en`. Architecture round cap is 2.

## Read next

- `.ai/tasks/20261109-srv-poi-amenity-en/architecture.md` — `Verdict and blocking items`
- `.ai/tasks/20261109-srv-poi-amenity-en/decision.md` — `Quyết định hiện hành`
- `.ai/tasks/20261109-srv-poi-amenity-en/model-design.md` — `Conflicts and questions`

## Waiting on

U-1 snake_case rule (A, B, or C). U-2 JSON `service_flags` source (`amenity_vi` or column `service_flags`). U-3 whether the runbook DROPs `ref_dictionary_amenities` and reruns `NB_SETUP_POI_AMENITY` with `p_apply=true`.

## REQUEST

# Request

## User outcome

Keep the current amenity string as `amenity_en`, store the snake_case of that string in `amenity`, and carry both columns from the silver dictionary through gold into `apps.srv_poi_amenity`.

`GET /api/v1/pois/{poi_id}/amenities` stays (D-02). Remove the `lang` query. The response tree is the D-01 sample in `decision.md`: `data[].amenity_group` plus `data[].items[]` with `amenity_code`, `amenity_label_en`, `amenity_label_vi`, and `service_flags`.

## Scope

### In scope

One task for the silver dictionary, `slv_poi_amenity`, gold, PostgreSQL DDL, and the serving API.

- `lh_vv_silver.dbo.ref_dictionary_amenities`: add `amenity_en`. Its value is the current `amenity` string. Change `amenity` to the snake_case of that current string.
- `slv_poi_amenity` stays in this task because `gld_srv_poi_amenity` is a 1-1 copy of it.
- `lh_vv_gold.dbo.gld_srv_poi_amenity`: add `amenity_en` from `ref_dictionary_amenities.amenity_en`. Take `amenity` from `ref_dictionary_amenities.amenity`. The gold table is dropped and initialized again because the dictionary changed. The agent does not DROP on Fabric.
- `apps.srv_poi_amenity`: drop the table and create it again with `amenity_en`. The user runs the Copy Job. The agent does not run the Copy Job and does not DROP on PostgreSQL.
- API path stays `GET /api/v1/pois/{poi_id}/amenities` (D-02). Remove the `lang` parameter. The response tree is the D-01 sample.
- Earlier response lines, kept as the column sources for the D-01 field names:

```text
- data[].amenity_group[].amenity_code lấy từ apps.srv_poi_amenity.amenity
- data[].item[].amenity_code[].amenity_label_en lấy từ apps.srv_poi_amenity.amenity_en
- data[].item[].amenity_code[].amenity_label_vi lấy từ apps.srv_poi_amenity.amenity_vi
- data[].item[].service_flags lấy từ apps.srv_poi_amenity.amenity_vi
- Bỏ data[].amenity_vi và data[].items[]
- Bỏ data[].amenity_vi và data[].items[].amenity_label
```

- Update `docs/context/mapping_gld_srv_poi_amenity.md` in this task before review.
- The later runbook records DROP gold, re-init, DROP `apps.srv_poi_amenity`, and the Copy Job for the user to run.

### Out of scope

- A separate task for silver, gold, PostgreSQL, or the API.
- Agent execution of Fabric, DROP, Copy Job, or docker compose.
- Reading `docs/poi-serving-api/`.
- Fast lane.
- Extra snake_case rules for diacritics, spaces, or Vietnamese when the code and seed do not already have them.

## Acceptance criteria

- `amenity_en` keeps the current `amenity` string. The new `amenity` follows U-1: option B (option A plus camelCase split, `servesWine` → `serves_wine`) and letters like `é` in `Café` become `e`.
- `gld_srv_poi_amenity.amenity_en` and `amenity` come from those two ref columns. Do not change grain or keys on your own.
- `sql/postgres/gld_srv_serve.pg.sql`, the JPA entity, and the gold DDL match, including `amenity_en`.
- The API path stays `GET /api/v1/pois/{poi_id}/amenities`. There is no `lang` query. The JSON matches the D-01 sample. Contract tests stay green.
- Same task. Do not split silver, gold, PostgreSQL, or the API.
- `mapping_gld_srv_poi_amenity.md` is updated in this task before review.

## Constraints

- Signal `data_model_change`. The current ref key includes `amenity`, so changing `amenity` values changes the key.
- Do not read `docs/poi-serving-api/`.
- Do not run Fabric, DROP, Copy Job, or docker compose.
- D-01 and D-02 are closed in `decision.md`. The path is unchanged. `lang` is still removed.

## Classification rationale

- Complexity: high. The dictionary column and key value change crosses silver, gold, PostgreSQL, and the API, in more than eight files, and changes API behavior. Fast lane does not apply.
- Risk: high. A new `amenity` value is a key change on a table gold copies 1-1, then PostgreSQL and the API. Fabric DROP, re-init, and the Copy Job are runtime-only proof.
- Architecture: required. The ref key includes `amenity`. The change also spans silver, gold, PostgreSQL, and the serving API.
- Evidence: not required. Current amenity strings and any snake_case rule come from repository code and seed. No Fabric probe.
- Runtime proof: required. The runbook, written after implementation, tells the user to DROP gold, initialize again, DROP `apps.srv_poi_amenity`, and run the Copy Job.
- Reviewer routing: `spark-runtime-reviewer` for the notebook DDL and builds; `sql-data-reviewer` for Delta DDL, grain, keys, and PostgreSQL SQL; `api-contract-reviewer` for the path, DTO JSON names, removal of `lang`, and the gold contract tests; `jpa-performance-reviewer` for the amenity entity and service. `risk_gate` follows risk high. No pipeline JSON, so no `fabric-pipeline-reviewer`. No security-surface files, so no `app-security-reviewer`. No CDC, watermark, lock, or retry change is in the request, so no `state-correctness-reviewer`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Cây JSON amenities | Chốt theo sample ở mục Quyết định của người dùng. `data[]` có `amenity_group` (string) và `items[]`. Mỗi item có `amenity_code`, `amenity_label_en`, `amenity_label_vi`, `service_flags`. | User 2026-11-09 | 2026-11-09 |
| D-02 | Path amenities | Chốt. Nguyên văn: Vẫn giữ /api/v1/pois/{poi_id}/amenities, không sửa. | User 2026-11-09 | 2026-11-09 |
| U-1 | Quy tắc snake_case của amenity | Chốt. Nguyên văn: chọn B: như A và tách camelCase (servesWine → serves_wine) và những kí tự như é trong Café chuyển thành e. | User 2026-11-09 | 2026-11-09 |
| U-2 | Nguồn JSON service_flags | Chốt. Nguyên văn: Lấy srv_poi_amenity.service_flags. | User 2026-11-09 | 2026-11-09 |
| U-3 | DROP ref_dictionary_amenities | Chốt. Nguyên văn: runbook có bước người dùng DROP ref_dictionary_amenities và chạy NB_SETUP_POI_AMENITY p_apply=true. | User 2026-11-09 | 2026-11-09 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 42102 bytes

## API

service: services/data-serving-service (rules: services/data-serving-service/AGENTS.md)
test: cd services/data-serving-service && mvnw.cmd -q -B test  (JDK 26, Docker)
jdk: 26 | docker: up
runtime: user-run docker compose per runtime-runbook.md (D-12)

## FILES

- architecture.md | 42102 bytes | large: use toc/show
- decision.md | 4482 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 25068 bytes | large: use toc/show
- handoffs/author-input.md | 2708 bytes
- model-design.md | 12219 bytes
- request.md | 4950 bytes
- resume.md | 1368 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 2819 bytes

## NEXT

python scripts/vv.py run-gate 20261109-srv-poi-amenity-en

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (222858 bytes)

[0] markdown id=init_md json=3-10 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=11-28 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=29-43 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=44-559 lines=501 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=560-574 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=575-772 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_cfg_cms json=773-830 lines=44 | def _cms_ts(path): | defs: _cms_ts, _cms
[7] code id=init_registry_pure json=831-845 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[8] code id=init_seed_ctrl json=846-961 lines=102 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[9] code id=init_seed_place_type json=962-1430 lines=455 | import re | defs: validate_seed
[10] code id=init_seed_amenity json=1431-1706 lines=262 | import re | defs: amenity_keys, validate_seed
[11] code id=init_plan json=1707-1866 lines=146 | import json | defs: _missing, _dup_keys, _target_dup_keys
[12] code id=init_ddl json=1867-1881 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[13] code id=init_seed_write json=1882-2075 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[14] code id=init_verify json=2076-2090 lines=30 | verify_errors = [] | defs: none
[15] code id=init_exit json=2091-2105 lines=7 | summary = { | defs: none

### notebooks/NB_SETUP_POI_AMENITY.ipynb (57271 bytes)

[0] markdown id=c1setupmd json=47-56 lines=3 | NB_SETUP_POI_AMENITY | defs: none
[1] code id=c1setupparam json=57-66 lines=1 | p_apply = "false" | defs: none
[2] code id=c1setuprun json=67-76 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=c1setupseed json=77-345 lines=260 | import re | defs: amenity_keys, validate_seed
[4] code id=c1setupplan json=346-412 lines=58 | import json | defs: none
[5] code id=c1setupddl json=413-481 lines=60 | spark.sql(""" | defs: none
[6] code id=c1setupmerge json=482-558 lines=68 | def _seed_merge(): | defs: _seed_merge
[7] code id=c1setupedges json=559-744 lines=177 | import uuid | defs: setup_edge_issues, _write_edges
[8] code id=c1setupexit json=745-765 lines=12 | import json | defs: none

### notebooks/NB_SLV_POI_AMENITY.ipynb (21131 bytes)

[0] markdown id=d1amenmd json=47-56 lines=3 | NB_SLV_POI_AMENITY | defs: none
[1] code id=d1amenparam json=57-81 lines=8 | p_exec_id = "" | defs: none
[2] code id=d1amenrun json=82-91 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=d1amenmatch json=92-226 lines=126 | import re | defs: resolve_condition, is_legacy_form, match_conditions, legacy_blocks_write, match_coverage
[4] code id=d1amenbuild json=227-307 lines=72 | GOOGLE = "google" | defs: build
[5] code id=d1amenres json=308-317 lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=d1amenexit json=318-327 lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_CREATE_DDL.ipynb (333293 bytes)

[0] markdown id=b0b1203a-7c40-48bf-bfc9-7b29d7064bdc json=3-25 lines=6 | NB_CREATE_DDL — 7 bảng control `lh_vv_ctrl.dbo` | defs: none
[1] markdown id=b7e4c1a0-6f28-4d3e-9a15-2c8d0e4f6a91 json=26-36 lines=4 | Ghi chú migration 08/10 | defs: none
[2] markdown id=d20a367e-98da-4b91-9237-dd2b2cebfeae json=37-54 lines=1 | Tạo bảng ctrl_mng_pipeline_config | defs: none
[3] code id=80154b61-ea1a-415b-834c-3c07d689d036 json=55-177 lines=108 | %%sql | defs: none
[4] markdown id=<none> json=178-188 lines=5 | Reset silver (DROP/DELETE) không nằm trong luồng tạo bảng. | defs: none
[5] code id=502cd242 json=189-242 lines=40 | %%sql | defs: none
[6] markdown id=a0c11600-5f15-4ec4-ab3b-cd590b5ce6a8 json=243-260 lines=1 | Tạo bảng ctrl_mng_watermark | defs: none
[7] markdown id=e80b9799-8de0-4319-8c62-be8096d373c8 json=261-288 lines=11 | **[SỬA 03/10] Bỏ cell MERGE watermark từ `lh_vv_bronze.partner.brz_watermark`**  | defs: none
[8] code id=3ea73e14-6a1f-42a5-b960-34123b0a3fc4 json=289-350 lines=47 | %%sql | defs: none
[9] markdown id=ed3d2dc0-d9f4-4cd7-b5aa-5e65afb7aca0 json=351-368 lines=1 | Tạo bảng ctrl_cfg_schema_registry | defs: none
[10] code id=d06c9671-6b88-4afa-97a8-d028f6b9e936 json=369-412 lines=30 | CONFIG_TABLE = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry" | defs: none
[11] code id=28e2be98-7f9a-41d5-b7f8-b4d4a5baf5ff json=413-961 lines=535 | TABLE_CONFIGS = [ | defs: none
[12] code id=0f228dc1-7bc8-4ed2-a10f-e6125a806e83 json=962-1162 lines=186 | from pyspark.sql.types import ( | defs: resolve_type, flatten_table_configs, validate_rows, seed_registry, show_registry
[13] markdown id=7517dd85-f292-4361-9d9d-6bad3f2e4f34 json=1163-1183 lines=4 | **[THÊM 03/10 - 3P] Seed registry nguồn 3rd-party `brz_3rd_crawler_poi_stream`** | defs: none
[14] code id=e9c137c5-c9fc-4f8f-a925-bc511cfd71a7 json=1184-1381 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[15] code id=0271d481-4188-43ab-8cb4-03acd3452550 json=1382-1401 lines=5 | seed_registry(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream" | defs: none
[16] markdown id=5c2996a4-3ddc-4924-8645-c0cc545cdd63 json=1402-1419 lines=1 | Tạo các bảng log & debug | defs: none
[17] code id=7dad05d9-20f0-4ab4-af1e-dec1dfe5d8cb json=1420-1561 lines=127 | %%sql | defs: none
[18] code id=ea524452-c135-4ef4-b4a8-3a076fa67ee7 json=1562-1597 lines=22 | GOLD_LOG_COLUMNS = ( | defs: none
[19] markdown id=de14c4c2-7925-4582-b080-8b0a660fb99c json=1598-1615 lines=1 | Kiểm tra cấu hình | defs: none
[20] code id=6e95fc60-2ef9-47af-a250-95844179c188 json=1616-1701 lines=71 | %%sql | defs: none
[21] code id=5784a286-d45c-4be8-8223-5a43800b6e2b json=1702-1736 lines=17 | %%sql | defs: none
[22] markdown id=enrddlmd json=1737-1746 lines=3 | [THÊM 13/10] Gold enr và cạnh PL_VV_TRANS_SLV_TO_ENR_15P | defs: none
[23] code id=enrddlpy json=1747-1890 lines=130 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _ddl, _expected_type
[24] markdown id=nonenrmd json=1891-1903 lines=1 | [THÊM 19/10] 20261019-poi-entity-non-enrich | defs: none
[25] code id=nonenrpy json=1904-1981 lines=64 | import re | defs: category_group, with_category_group
[26] markdown id=dictseedmd json=1982-1989 lines=1 | [THÊM 20/10] 20261020-dictionary-seed-from-mapping | defs: none
[27] code id=dictseedpy json=1990-2040 lines=37 | AM_FQ = "lh_vv_silver.dbo.ref_dictionary_amenities" | defs: none
[28] markdown id=entwebmd json=2041-2048 lines=1 | [THÊM 20/10] 20261020-entity-drop-op-cols-add-website | defs: none
[29] code id=entwebpy json=2049-2164 lines=102 | CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: lock_is_free
[30] markdown id=enrinfomd json=2165-2172 lines=1 | [THÊM 21/10] 20261021-refresh-gld-enr-poi-info | defs: none
[31] code id=enrinfopy json=2173-2399 lines=213 | import uuid | defs: _schema, _create
[32] markdown id=mvpoimd json=2400-2407 lines=1 | [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup | defs: none
[33] code id=mvpoipy json=2408-2641 lines=220 | import uuid | defs: _names, _n, _node_edges, _info_edges
[34] markdown id=enrflagmd json=2642-2649 lines=1 | [THÊM 22/10] 20261022-enr-landing-and-gld-flags | defs: none
[35] code id=enrflagpy json=2650-2916 lines=253 | import uuid | defs: _want, _schema, _create_sql, _missing_flags, _add_flags, _edge_rows
[36] markdown id=ohpassmd json=2917-2924 lines=1 | [THÊM 23/10] 20261023-entity-opening-hours-passthrough | defs: none
[37] code id=ohpasspy json=2925-3128 lines=190 | import uuid | defs: _rows, _active, _refresh_lock, _column
[38] markdown id=peholmd json=3129-3136 lines=1 | [THÊM 23/10] 20261023-entity-phone-email-holiday | defs: none
[39] code id=peholpy json=3137-3200 lines=50 | ENTITY_FQ = "lh_vv_silver.dbo.slv_poi_entity_non_enrich" | defs: _fields, _issues
[40] markdown id=srvpoimd json=3201-3212 lines=5 | [THÊM 24/10] 20261024-gld-srv-poi-from-mapping | defs: none
[41] code id=srvpoipy json=3213-3431 lines=205 | import uuid | defs: _want, _schema, _create_sql, _edge_rows, _refresh_lock
[42] markdown id=srvratemd json=3432-3443 lines=5 | [THÊM 26/10] 20261025-gld-srv-poi-info-rating-review | defs: none
[43] code id=srvratepy json=3444-3624 lines=167 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[44] markdown id=mediaddlmd json=3625-3634 lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[45] code id=mediaddlpy json=3635-3834 lines=186 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[46] markdown id=amenddlmd json=3835-3844 lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[47] code id=amenddlpy json=3845-4035 lines=177 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[48] markdown id=plcadmd json=4036-4046 lines=4 | [THÊM 26/10] 20261026-pl-name-cadence-suffix | defs: none
[49] code id=plcadpy json=4047-4300 lines=240 | import uuid | defs: _n, _lock_rows, _refresh_lock, _issues
[50] markdown id=mlexpmd json=4301-4309 lines=2 | [THÊM 26/10] 20261026-add-poi-multi-lang-experience | defs: none
[51] code id=mlexppy json=4310-4461 lines=138 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[52] markdown id=srvrevmd json=4462-4471 lines=3 | [THÊM 27/10] 20261026-gld-srv-poi-review | defs: none
[53] code id=srvrevpy json=4472-4680 lines=195 | import uuid | defs: _want, _schema, _edge_rows, _create_sql, _refresh_lock
[54] markdown id=rvi18nenrmd json=4681-4690 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (1/2) | defs: none
[55] code id=rvi18nenrpy json=4691-4853 lines=149 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[56] markdown id=rvi18ngldmd json=4854-4863 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (2/2) | defs: none
[57] code id=rvi18ngldpy json=4864-5016 lines=139 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[58] markdown id=mlsrcmd json=5017-5026 lines=3 | [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr | defs: none
[59] code id=mlsrcpy json=5027-5145 lines=105 | import uuid | defs: _want, _schema, _refresh_lock
[60] markdown id=cmscfgmd json=5146-5155 lines=3 | [THÊM 08/11] 20261104-extract-cms-raw-data | defs: none
[61] code id=cmscfgpy json=5156-5265 lines=96 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _cms_ts, _cms
[62] markdown id=srvcovermd json=5266-5276 lines=4 | [THÊM 08/11] 20261108-gld-srv-poi-info-cover | defs: none
[63] code id=srvcoverpy json=5277-5468 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock

### docs/context/01_DATA_MODEL.md (36598 bytes)

# 01 — Data Model mới của Visit Vietnam (POI) trên Microsoft Fabric | L1-L406
## 1. Bối cảnh nền tảng | L7-L18
## 2. Nguyên tắc phân tầng (đã chốt) | L19-L35
## 3. Sơ đồ tổng | L36-L75
## 4. Bronze — bảng raw | L76-L253
### Cấu trúc `normalized_payload` | L86-L253
## 5. Silver L1 — extract (đúng cấu trúc nguồn) | L254-L318
### 5.1 Partner `slv_pn_*` (23 bảng, `load_mode = CDC`) | L256-L289
### 5.2 3rd-party `slv_3p_poi_*` (9 bảng trong registry, 9 active, snapshot) | L290-L318
## 6. Silver L2 — tích hợp POI (7 node) | L319-L348
### 6.1 Bảng ref (rule dạng dữ liệu) | L335-L348
## 7. Gold hiện hành (`lh_vv_gold.enr`) | L349-L361
## 8. Định danh | L362-L374
## 9. Model cũ (vẫn chạy song song) và lý do đổi | L375-L384
## 10. Ý nghĩa của model mới | L385-L394
## 11. Hướng sắp tới (chưa làm) | L395-L406
