# Architect handoff: 20261112-poi-destination-name-api

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261112-poi-destination-name-api --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261112-poi-destination-name-api/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261112-poi-destination-name-api | phase=triage

## STATE

id: 20261112-poi-destination-name-api
title: POI destination_name and five read API fields
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change, cross_system, runtime_proof_required
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, api-contract-reviewer, jpa-performance-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_GLD_SRV_POI_INFO.ipynb
- notebooks/NB_GLD_SRV_POI_REVIEW.ipynb
- sql/postgres/gld_srv_serve.pg.sql
- docs/context/mapping_gld_srv_poi_info.md
- docs/context/mapping_gld_srv_poi_review.md
- docs/context/api-mapping/amenities.md
- docs/context/api-mapping/compact.md
- docs/context/api-mapping/practical_info.md
- docs/context/api-mapping/experiences.md
- docs/context/api-mapping/reviews.md
- services/data-serving-service/AGENTS.md
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiInfo.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiReview.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/util/StoredJsonParser.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiAmenityGroupResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/CompactPoiResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiPracticalInfoResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiExperiencesResponse.java
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/api/dto/PoiReviewItemResponse.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java
- services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/api/PoiControllerIntegrationTest.java
- tests/test_enr_poi_contract.py
- tests/test_gld_srv_poi_contract.py
- tests/test_srv_poi_serving_contract.py

## VALIDATION

PASS

## RESUME

# Resume

## Status

`user_decision`. Model design is `EVIDENCE_REQUIRED` for all three sources. No code edits. Gates: architecture pending, local_verification pending, specialist_review pending, runtime pending, evidence not_required.

## Done this session

Classified `20261112-poi-destination-name-api` (`data_model_change`, `cross_system`, `runtime_proof_required`; architecture and runtime required; Fabric evidence not required). Recorded Main `grok-4.7` medium. Author `claude-opus-5-5` medium wrote `model-design.md`.

## Next action

Do not implement. User names a live source column and type for each blocked item, or accepts stopping that item. Then a new chat re-runs `run-author --kind model` with that file in `handoffs/author-input.md`.

## Read next

- `.ai/tasks/20261112-poi-destination-name-api/model-design.md` — `## Conflicts and questions`
- `notebooks/NB_CREATE_DDL.ipynb` cell `cmscfgpy` — `slv_cms_destination.name` exists; no join to `destination_id` is declared

## Waiting on

User decision for conflicts 1–3. `slv_cms_destination.name` (`_str("name")`) is not a source until a declared key joins it to `slv_enr_poi_destination`.

## REQUEST

# Request

## User outcome

Five POI read APIs match the field changes below, and `destination_name` exists on the silver enrich destination table, gold POI info, and PostgreSQL `apps.srv_poi_info`, copied forward from a column that already exists in DDL or a notebook. One task covers the notebook, gold, PostgreSQL, and API. No notebook or pipeline rerun.

## Scope

### In scope

- Add `slv_enr_poi_destination.destination_name`. The value written into it must be a column that already exists in DDL or a notebook. Do not invent a source or a type.
- Add `gld_srv_poi_info.destination_name` from `slv_enr_poi_destination.destination_name`.
- Add `apps.srv_poi_info.destination_name` from `gld_srv_poi_info.destination_name`, including entity `SrvPoiInfo`.
- `GET /api/v1/pois/{poi_id}/amenities`: do not read and do not return `data[].items[].amenity_label_en` or `data[].items[].amenity_label_vi`. Keep `apps.srv_poi_amenity.amenity_en` and `amenity_vi`.
- `POST /api/v1/pois/compact`: add `data[].destinations` as `{"id": apps.srv_poi_info.destination_id, "name": apps.srv_poi_info.destination_name}`.
- `GET /api/v1/pois/{poi_id}/practical_info`: `data.destinations` is currently `{id}`. Add `name` from `apps.srv_poi_info.destination_name`. Remove `data.business_sector`. Keep `data.business_tags.business_sector`.
- `GET /api/v1/pois/{poi_id}/experiences`: add `data.items[].icon_key` from `keyword` of the selected `apps.srv_poi_multi_lang` row. The table has `experience` and no `keyword` column. Model design must show where `keyword` already lives. Do not add a `keyword` column.
- `GET /api/v1/pois/{poi_id}/reviews`: add `data[].source_name` from `apps.srv_poi_review.source_name`. That column is absent from `sql/postgres/gld_srv_serve.pg.sql`, and `services/data-serving-service/AGENTS.md` forbids it under D-10 of task `20261106-agent-system-unify-api`. This request adds the column only when model design finds `source_name` already on the silver path into `gld_srv_poi_review`. Then add `gld_srv_poi_review.source_name` and `apps.srv_poi_review.source_name`, and edit the forbid line in the service `AGENTS.md`.
- Mapping files in the same task: `docs/context/api-mapping/amenities.md`, `compact.md`, `practical_info.md`, `experiences.md`, `reviews.md`, `docs/context/mapping_gld_srv_poi_info.md`, and the review gold mapping if `source_name` is added.
- `scope.systems`: `poi-serving-api`. Domain: DDL/registry, lib transform/gold, serving API.

### Out of scope

- A new table. Splitting the notebook work from the API work.
- Rerunning a notebook, pipeline, Copy Job, or Fabric probe. There is no data reload.
- `docs/poi-serving-api/`. Continuing task `20261110-serving-poi-read-apis`.
- Credentials or hosts in the repository. The API reads gold only through PostgreSQL `apps.srv_poi_*`.

## Acceptance criteria

- The three `destination_name` columns are in silver DDL, gold DDL, `sql/postgres/gld_srv_serve.pg.sql`, and entity `SrvPoiInfo`. The gold transform reads the silver column.
- The five API JSON contracts match the scope. The mapping files above change in this task.
- `tests/test_enr_poi_contract.py`, `tests/test_gld_srv_poi_contract.py`, `tests/test_srv_poi_serving_contract.py`, and the Java tests of the changed endpoints pass.
- `gates.local_verification` is `pass` only when `python scripts/vv.py verify` runs with Docker.
- `runtime-runbook.md` is written for the `services/data-serving-service` docker compose runtime, and the task stops before the compose step so the user can run it.

## Constraints

- Decisions D-1, D-2, D-3, and D-4 in `decision.md` (2026-11-12) supersede the earlier stop rules for a missing source.
- D-1: `slv_enr_poi_destination.destination_name` is DDL only. No notebook loads it. Type is nullable `STRING`, the same as the other text columns on that table. Gold and `apps.srv_poi_info` still copy the column. Values stay null until a later load exists.
- D-2: `icon_key` reads `keyword` inside the selected row's `experience` JSON. A missing `keyword` yields null. Do not add a `keyword` column.
- D-3: the gold review transform sets `source_name` to the literal `google`, because the source tables belong to the Google flow. Add the column on `gld_srv_poi_review` and `apps.srv_poi_review`, and edit the D-10 forbid line in the service `AGENTS.md`.
- D-4: the amenity label removal and the `practical_info` `data.business_sector` removal are in this task.
- No commit unless the user asks in the current turn.

## Classification rationale

- Complexity: `medium`. Signals `data_model_change`, `cross_system`, `runtime_proof_required`. New columns cross silver, gold, PostgreSQL, and the serving API, and five response contracts change.
- Risk: `medium`. Bounded column passthrough and response-field changes. Rollback is the reverse DDL and code change. No watermark, lock, or CDC change.
- Architecture: required. The change spans DDL, a gold notebook, PostgreSQL, entities, and API DTO files, more than eight source files, and the column moves silver to gold to PostgreSQL.
- Evidence: not required as a Fabric probe. The user forbade notebook, pipeline, Copy Job, and Fabric probes. Source columns must already be in the repository. A missing source stops at model design.
- Runtime proof: required. Local docker compose of `services/data-serving-service` only, user-run, after the runbook. `gates.local_verification` still requires `vv.py verify` with Docker.
- Reviewer routing: `sql-data-reviewer` (Delta DDL and gold column copy), `spark-runtime-reviewer` (gold notebook), `api-contract-reviewer` (`api/` or `dto/` and `gld_srv_serve.pg.sql`), `jpa-performance-reviewer` (entity, and repository or query if the diff touches them). Risk is not `high` or `critical`, so no risk gate.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | destination_name chỉ DDL | slv_enr_poi_destination.destination_name hiện tại chỉ tạo DDL, chưa có nguồn đổ vào. | User, 2026-11-12 | 2026-11-12 |
| D-2 | keyword trong experience | Tôi confirm có keyword trong apps.srv_poi_multi_lang.experience. Nếu không có thì để null cho key keyword. | User, 2026-11-12 | 2026-11-12 |
| D-3 | review source_name | Lấy source_name trong gld_srv_poi_review fix cứng trong transform là 'google' vì lấy từ bảng thuộc luồng google. | User, 2026-11-12 | 2026-11-12 |
| D-4 | phần bỏ field | Các phần bỏ code thực hiện ngay trong task này. | User, 2026-11-12 | 2026-11-12 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: missing
size: 483 bytes

## API

service: services/data-serving-service (rules: services/data-serving-service/AGENTS.md)
test: cd services/data-serving-service && mvnw.cmd -q -B test  (JDK 26, Docker)
jdk: 26 | docker: down
runtime: user-run docker compose per runtime-runbook.md (D-12)

## FILES

- architecture.md | 483 bytes | placeholder
- decision.md | 2524 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 26142 bytes | large: use toc/show
- handoffs/author-input.md | 1892 bytes
- model-design.md | 7563 bytes
- request.md | 5816 bytes
- resume.md | 1186 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 3236 bytes

## NEXT

python scripts/vv.py run-gate 20261112-poi-destination-name-api

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_CREATE_DDL.ipynb (333433 bytes)

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
[46] markdown id=amenddlmd json=3835-3846 lines=5 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[47] code id=amenddlpy json=3847-4038 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[48] markdown id=plcadmd json=4039-4049 lines=4 | [THÊM 26/10] 20261026-pl-name-cadence-suffix | defs: none
[49] code id=plcadpy json=4050-4303 lines=240 | import uuid | defs: _n, _lock_rows, _refresh_lock, _issues
[50] markdown id=mlexpmd json=4304-4312 lines=2 | [THÊM 26/10] 20261026-add-poi-multi-lang-experience | defs: none
[51] code id=mlexppy json=4313-4464 lines=138 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[52] markdown id=srvrevmd json=4465-4474 lines=3 | [THÊM 27/10] 20261026-gld-srv-poi-review | defs: none
[53] code id=srvrevpy json=4475-4683 lines=195 | import uuid | defs: _want, _schema, _edge_rows, _create_sql, _refresh_lock
[54] markdown id=rvi18nenrmd json=4684-4693 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (1/2) | defs: none
[55] code id=rvi18nenrpy json=4694-4856 lines=149 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[56] markdown id=rvi18ngldmd json=4857-4866 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (2/2) | defs: none
[57] code id=rvi18ngldpy json=4867-5019 lines=139 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[58] markdown id=mlsrcmd json=5020-5029 lines=3 | [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr | defs: none
[59] code id=mlsrcpy json=5030-5148 lines=105 | import uuid | defs: _want, _schema, _refresh_lock
[60] markdown id=cmscfgmd json=5149-5158 lines=3 | [THÊM 08/11] 20261104-extract-cms-raw-data | defs: none
[61] code id=cmscfgpy json=5159-5268 lines=96 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _cms_ts, _cms
[62] markdown id=srvcovermd json=5269-5279 lines=4 | [THÊM 08/11] 20261108-gld-srv-poi-info-cover | defs: none
[63] code id=srvcoverpy json=5280-5471 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (224721 bytes)

[0] markdown id=init_md json=3-10 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=11-28 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=29-43 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=44-561 lines=504 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=562-576 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=577-774 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_cfg_cms json=775-832 lines=44 | def _cms_ts(path): | defs: _cms_ts, _cms
[7] code id=init_registry_pure json=833-847 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[8] code id=init_seed_ctrl json=848-963 lines=102 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[9] code id=init_seed_place_type json=964-1432 lines=455 | import re | defs: validate_seed
[10] code id=init_seed_amenity json=1433-1737 lines=291 | import re | defs: amenity_keys, amenity_code, amenity_seed_rows, validate_seed
[11] code id=init_plan json=1738-1897 lines=146 | import json | defs: _missing, _dup_keys, _target_dup_keys
[12] code id=init_ddl json=1898-1912 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[13] code id=init_seed_write json=1913-2106 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[14] code id=init_verify json=2107-2121 lines=30 | verify_errors = [] | defs: none
[15] code id=init_exit json=2122-2136 lines=7 | summary = { | defs: none

### notebooks/NB_GLD_SRV_POI_INFO.ipynb (21290 bytes)

[0] markdown id=srvinfomd json=unknown lines=7 | NB_GLD_SRV_POI_INFO | defs: none
[1] code id=srvinfoparam json=unknown lines=8 | p_exec_id = "" | defs: none
[2] code id=srvinforun json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=srvinfohours json=unknown lines=99 | import json | defs: _int, _open, _closed, _all_day, _dump, google_hours, partner_hours, operating_hours
[4] code id=srvinfobuild json=unknown lines=148 | ENT_COLS = ("poi_id", "poi_name", "source_name", "business_sector", "business_ca | defs: _require, _destination, _rating, _reviews, _cover, build
[5] code id=srvinfores json=unknown lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=srvinfoexit json=unknown lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none
