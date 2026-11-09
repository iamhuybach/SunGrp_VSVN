# Architect handoff: 20261108-gld-srv-poi-info-cover

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261108-gld-srv-poi-info-cover --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261108-gld-srv-poi-info-cover/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261108-gld-srv-poi-info-cover | phase=triage

## STATE

id: 20261108-gld-srv-poi-info-cover
title: Add cover_id and cover_blob_url to gld_srv_poi_info
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=False
signals: data_model_change, cross_system
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: spark-runtime-reviewer, sql-data-reviewer, api-contract-reviewer, jpa-performance-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_GLD_SRV_POI_INFO.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- sql/postgres/gld_srv_serve.pg.sql
- services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiInfo.java
- docs/context/mapping_gld_srv_poi_info.md
- tests/test_srv_poi_serving_contract.py

## VALIDATION

PASS

## RESUME

# Resume

Status: waiting_architecture. Owner architect. Gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=not_required. Model design is missing. Architect has not run.

Done this session: Created task 20261108-gld-srv-poi-info-cover. Classified medium/medium, signals data_model_change and cross_system, architecture required, evidence and runtime not required. Reviewers: spark-runtime, sql-data, api-contract, jpa-performance. Wrote request.md, decision.md D-01, handoffs/author-input.md. Recorded Main as grok-4.7 medium. Transitioned triage to waiting_architecture. run-author --kind model started on claude-opus-5-5 medium and failed after 124s: repository immutability check. model-design.md was not written. No notebook, DDL, SQL, or entity edit in this phase. cover_id is not in NB_CREATE_DDL.ipynb.

Next action: On the user's reply to retry, run `python scripts/vv.py run-author 20261108-gld-srv-poi-info-cover --kind model`, then `python scripts/vv.py run-gate 20261108-gld-srv-poi-info-cover`. Do not implement before architecture PASS.

Read next: `.ai/tasks/20261108-gld-srv-poi-info-cover/request.md` and `decision.md` ledger D-01. Author input: `handoffs/author-input.md`.

Waiting on: User decision to retry the model author. The working tree already had unrelated CMS edits (NB_CREATE_DDL cell cmscfgpy, contract tests, CTRL_TABLES_CONTEXT.md, task 20261104-extract-cms-raw-data). Those files were not reverted. The author check prints full git status, not a proven Claude diff.

## REQUEST

# Request

## User outcome

`lh_vv_gold.dbo.gld_srv_poi_info` carries the POI cover on the info row: `cover_id` from `slv_poi_media_info.media_id` and `cover_blob_url` from `slv_poi_media_info.blob_url`. `apps.srv_poi_info` has the same two columns. A POI with no cover stays one `gld_srv_poi_info` row and both columns are null.

## Scope

### In scope

- `notebooks/NB_GLD_SRV_POI_INFO.ipynb` cell `srvinfobuild`: LEFT JOIN the `slv_poi_media_info` row whose `is_cover` is the cover `gld_srv_poi_media_gallery` already uses. Gallery is a 1-1 projection of `slv_poi_media_info`; `is_cover` is computed on silver by `with_cover` and is not recomputed in the gallery.
- Gold DDL for `gld_srv_poi_info` in `notebooks/NB_CREATE_DDL.ipynb` and `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, including a new ctrl edge to `slv_poi_media_info` when the model or architecture adds that read. Column types come from existing `media_id` and `blob_url`.
- `sql/postgres/gld_srv_serve.pg.sql` `CREATE TABLE apps.srv_poi_info`, types mapped by the header of that file.
- JPA entity `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiInfo.java`.
- `docs/context/mapping_gld_srv_poi_info.md`, updated in this task before review.
- `tests/test_srv_poi_serving_contract.py` must still pass (gold DDL + NodeSpec `pk` = PostgreSQL DDL = JPA entity).

### Out of scope

- A second cover rule, any change to `is_cover` or to `with_cover`, and any change to gallery grain or logic.
- Changing `gld_srv_poi_info` grain: one row per `poi_id`. NodeSpec `pk` stays `("poi_id",)`.
- A new endpoint, DTO, or API field.
- `docs/poi-serving-api/`.
- `pipelines/PL_VV_TRANS_SLV_TO_GLD_30M/PL_VV_TRANS_SLV_TO_GLD_30M.json`, unless the model or architecture shows the new `slv_poi_media_info` edge is declared in that JSON rather than in the ctrl seed inside the DDL notebooks.

## Acceptance criteria

- `gld_srv_poi_info` has `cover_id` and `cover_blob_url`, and each `poi_id` is still one row.
- The two values equal `media_id` and `blob_url` of the `slv_poi_media_info` row with the `is_cover` value that marks the cover for that `poi_id`. Both columns are null when that row does not exist.
- `apps.srv_poi_info` has the same two columns. The contract gold DDL + NodeSpec `pk` = PostgreSQL DDL = JPA entity still holds (`tests/test_srv_poi_serving_contract.py`). No new endpoint.
- `docs/context/mapping_gld_srv_poi_info.md` is updated in this task before review.

## Constraints

- One task for gold, PostgreSQL, the JPA entity, and the ctrl edge. Do not split them.
- Signal `data_model_change`. Do not invent column types or a cover predicate the named files do not show.
- This phase writes the request, classification, and model design, then runs the Architect. It does not edit notebooks, DDL, SQL, or the entity.

## Classification rationale

- Complexity: `medium`. Two new nullable columns and one new silver read. Fast lane does not apply: the column values change, and the edit spans the gold notebook, both DDL notebooks, PostgreSQL DDL, the JPA entity, and the mapping doc.
- Risk: `medium`. Bounded LEFT JOIN onto an existing one-row-per-`poi_id` MERGE. Rollback is reverting those columns. Local proof is `tests/test_srv_poi_serving_contract.py`. Not `high`: no watermark, lock, retry, or commit-order change, and the cross-system column contract is locally testable, so `risk-gate` is not required.
- Architecture: required. Not fast lane. The info node gains a read of `slv_poi_media_info` (ctrl edge, same shape as cell `srvratepy`) and the new columns must match across gold DDL, PostgreSQL, and the JPA entity. `data_model_change` requires `model-design.md` before `run-gate`.
- Evidence: not required. `with_cover` assigns one cover per `poi_id`, `unique_checks` names `one_cover_per_poi`, and `docs/context/mapping_poi_media_info.md` states that rule. `media_id` is `STRING NOT NULL` and `blob_url` is `STRING` on `MEDIA_COLS` in cell `mediaddlpy`. The Architect may still return `EVIDENCE_REQUIRED`.
- Runtime proof: not required for this classification. No new endpoint. Fabric apply and any `docker compose` step stay with the user and are not claimed here.
- Reviewer routing: `spark-runtime-reviewer` (notebook), `sql-data-reviewer` (join, grain, Delta DDL, PostgreSQL DDL), `api-contract-reviewer` (entity and `gld_srv_serve.pg.sql`), `jpa-performance-reviewer` (entity). No `fabric-pipeline-reviewer` while the pipeline JSON stays out of scope. No `app-security-reviewer` (diff does not touch `common/web/`, `config/`, `application*.yml`, `pom.xml`, or Docker files). No `state-correctness-reviewer` (no CDC, watermark, lock, or retry change).


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Ảnh cover trên dòng POI info | Thêm `cover_id` và `cover_blob_url` vào `lh_vv_gold.dbo.gld_srv_poi_info` và `apps.srv_poi_info` trong cùng một task. `cover_id` lấy từ `slv_poi_media_info.media_id`. `cover_blob_url` lấy từ `slv_poi_media_info.blob_url`. LEFT JOIN `slv_poi_media_info`. POI không có cover vẫn giữ một dòng `gld_srv_poi_info`; hai cột mới để null. Chọn đúng dòng cover mà `gld_srv_poi_media_gallery` đang dùng qua `is_cover`. Gallery là bản 1-1 của `slv_poi_media_info`; `is_cover` đã tính trên silver (`with_cover`), không tính lại trong gallery. Dùng dòng `is_cover` đó. Không viết rule cover thứ hai, không đổi rule `is_cover`, không đổi grain một dòng `poi_id`. | request.md ## User outcome | 2026-11-08 |

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
- decision.md | 1780 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 2855 bytes
- model-design.md | 9155 bytes
- request.md | 4726 bytes
- resume.md | 1598 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1714 bytes

## NEXT

python scripts/vv.py run-gate 20261108-gld-srv-poi-info-cover

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_CREATE_DDL.ipynb (320983 bytes)

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

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (222518 bytes)

[0] markdown id=init_md json=3-10 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=11-28 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=29-43 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=44-557 lines=499 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=558-572 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=573-770 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_cfg_cms json=771-828 lines=44 | def _cms_ts(path): | defs: _cms_ts, _cms
[7] code id=init_registry_pure json=829-843 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[8] code id=init_seed_ctrl json=844-957 lines=100 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[9] code id=init_seed_place_type json=958-1426 lines=455 | import re | defs: validate_seed
[10] code id=init_seed_amenity json=1427-1702 lines=262 | import re | defs: amenity_keys, validate_seed
[11] code id=init_plan json=1703-1862 lines=146 | import json | defs: _missing, _dup_keys, _target_dup_keys
[12] code id=init_ddl json=1863-1877 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[13] code id=init_seed_write json=1878-2071 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[14] code id=init_verify json=2072-2086 lines=30 | verify_errors = [] | defs: none
[15] code id=init_exit json=2087-2101 lines=7 | summary = { | defs: none
