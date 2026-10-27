# Architect handoff: 20261026-gld-srv-poi-review

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261026-gld-srv-poi-review --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261026-gld-srv-poi-review/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261026-gld-srv-poi-review | phase=triage

## STATE

id: 20261026-gld-srv-poi-review
title: Create gld_srv_poi_review and add lang, title on slv_enr_poi_review_multi_lang
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_GLD_SRV_POI_REVIEW.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- tests/test_initial_ddl_contract.py

## VALIDATION

PASS

## RESUME

# Resume

## Status
user_decision. Architecture round 1 verdict EVIDENCE_REQUIRED. Gates: evidence=evidence_required, architecture=evidence_required.

## Done this session
Reran run-author --kind model. model-design.md written (claude-opus-5-5, medium). Transitioned to waiting_architecture and ran run-gate. Architect returned EVIDENCE_REQUIRED. G2 (gold rating type) is the user stop. G1 (add row_hash and deleted_at) waits for the model rerun after D-02. P1–P3 do not block the design; no probe was written.

## Next action
Record the user's G2 choice as D-02 in decision.md. Rewrite handoffs/author-input.md so the model lists row_hash STRING and deleted_at TIMESTAMP, and the chosen rating type. Run python scripts/vv.py run-author 20261026-gld-srv-poi-review --kind model, then transition to waiting_architecture and run-gate again.

## Read next
.ai/tasks/20261026-gld-srv-poi-review/architecture.md — ## Blocking gaps
.ai/tasks/20261026-gld-srv-poi-review/model-design.md — ## Conflicts and questions
.ai/tasks/20261026-gld-srv-poi-review/decision.md — Quyết định hiện hành

## Waiting on
User choice for gld_srv_poi_review.rating: string (cast decimal(4,2) to string, value like "4.50") or decimal (DECIMAL(4,2), no cast).

## REQUEST

# Request

## User outcome

`lh_vv_gold.dbo.gld_srv_poi_review` exists and is loaded with one row per `review_id` for reviews that already have an enrich row. `slv_enr_poi_review_multi_lang` has nullable `lang` and `title` columns. A review absent from `slv_3p_poi_review` does not appear in gold.

## Scope

### In scope

- New notebook `NB_GLD_SRV_POI_REVIEW`, one notebook for one target table. No new orchestration tier.
- Processing from mapping §1: `slv_enr_poi_review_multi_lang` INNER JOIN `slv_3p_poi_review` on `review_id`, LEFT JOIN `slv_3p_poi_rating` on `poi_id`.
- Columns and transforms only from mapping §2. `created_at` and `updated_at` are system timestamps.
- Target lakehouse.schema is `lh_vv_gold.dbo`. Do not place this table in schema `enr`. Do not change `NB_ENR_POI_REVIEW` logic.
- Add `lang` and `title` to `slv_enr_poi_review_multi_lang`, STRING, nullable. The mapping does not name a source for those two columns. Do not write a notebook that loads them.
- DDL in both `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL`. Setup edits the current definition in place. Create adds only a markdown cell `[THÊM dd/mm] 20261026-gld-srv-poi-review` and one self-contained patch cell at the end. Add columns with nullable `ALTER`. No `DROP TABLE`.
- Pipeline and `load_mode` use the values seeded for `gld_srv_poi_info`: `PL_VV_TRANS_SLV_TO_GLD_30M` and `RECOMPUTE`. Do not attach this table to `PL_VV_TRANS_SLV_TO_ENR_15M`.
- Grain is one row per `review_id`. If `slv_3p_poi_rating` has more than one row for one `poi_id`, stop. Do not pick a row.

### Out of scope

- Changes to `NB_ENR_POI_REVIEW` logic.
- A loader for `slv_enr_poi_review_multi_lang.lang` and `.title`.
- Schema `lh_vv_gold.enr` for `gld_srv_poi_review`.
- Pipeline `PL_VV_TRANS_SLV_TO_ENR_15M`.
- `notebooks_lgc/`, `docs/context/3p-google/*.txt`, pipeline manifests, and other tasks' artifacts.

## Acceptance criteria

- `NB_GLD_SRV_POI_REVIEW` is the only new business notebook, and it writes only `lh_vv_gold.dbo.gld_srv_poi_review`.
- Both DDL notebooks define the new gold table and the two new silver columns. Create's patch is idempotent and does not drop a table.
- Seeded pipeline is `PL_VV_TRANS_SLV_TO_GLD_30M` and `load_mode` is `RECOMPUTE`, matching `gld_srv_poi_info`.
- Gold grain is one row per `review_id`. A duplicate `slv_3p_poi_rating.poi_id` fails the run instead of choosing a row.
- Gold keeps only reviews present in both `slv_enr_poi_review_multi_lang` and `slv_3p_poi_review`. Rating is attached by `poi_id` when present.

## Constraints

- Mapping: `docs/context/mapping_gld_srv_poi_review.md`.
- Registry in `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_cfg_3p`: `slv_3p_poi_review` key `review_id`, columns `review_id` string, `poi_id`, `author_name` string, `rating` decimal(4,2), `time` string. `slv_3p_poi_rating` key `poi_id`, columns `poi_id`, `rating_overall` decimal(4,2), `rating_count` bigint.
- D-01: gold `rating_count` is Spark Long (`bigint`), the registry type of `slv_3p_poi_rating.rating_count`. Do not cast it to integer. Mapping §2's `integer` is not the column type.
- D-02: gold `rating` is `DECIMAL(4,2)`, the registry type of `slv_3p_poi_review.rating`. Transform 1-1. Do not cast it to string. Mapping §2's `string` is not the column type.
- `lang` and `title` have no fill source in the mapping.
- Business reason: gold serving keeps a review only when an enrich row exists, and attaches the POI rating. A review missing from `slv_3p_poi_review` does not reach gold.
- Domain: lib transform/gold and DDL/registry.

## Classification rationale

- Complexity: medium. New gold grain plus columns on an existing silver table. This is a behavior change across more than two files, so it is not the fast lane.
- Risk: medium. Bounded new serving table and nullable columns. No `DROP`. `NB_ENR_POI_REVIEW` logic stays as it is.
- Architecture: required. The new table has grain and key `review_id`, and `slv_enr_poi_review_multi_lang` gains columns.
- Evidence: not required for triage. Registry types and keys are in the repo. Duplicate `poi_id` handling is specified as fail, not as a distribution lookup. The open item is the `rating_count` type choice.
- Runtime proof: required after review, because the new notebook and DDL must run in Fabric DEV.
- Reviewer routing: `sql-data-reviewer` for the joins, grain, DDL, and types; `spark-runtime-reviewer` for the notebook contract and Delta write. No pipeline JSON change, so no `fabric-pipeline-reviewer`. Risk is medium, so no risk gate.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | rating_count | Kiểu Long như source hiện tại | user 2026-10-26 | 2026-10-26 |
| D-02 | rating | Kết quả là decimal(4,2) | user 2026-10-27 | 2026-10-27 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 27916 bytes

## FILES

- architecture.md | 27916 bytes | large: use toc/show
- decision.md | 1730 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 19808 bytes
- handoffs/author-input.md | 1748 bytes
- model-design.md | 10613 bytes
- request.md | 4586 bytes
- resume.md | 1266 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1495 bytes

## NEXT

python scripts/vv.py run-gate 20261026-gld-srv-poi-review

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (224824 bytes)

[0] markdown id=init_md json=unknown lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=unknown lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=unknown lines=482 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=unknown lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=unknown lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=unknown lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=unknown lines=86 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=unknown lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=unknown lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=unknown lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=unknown lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=unknown lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=unknown lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=unknown lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (270159 bytes)

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
[24] markdown id=nonenrmd json=unknown lines=1 | [THÊM 19/10] 20261019-poi-entity-non-enrich | defs: none
[25] code id=nonenrpy json=unknown lines=64 | import re | defs: category_group, with_category_group
[26] markdown id=dictseedmd json=unknown lines=1 | [THÊM 20/10] 20261020-dictionary-seed-from-mapping | defs: none
[27] code id=dictseedpy json=unknown lines=37 | AM_FQ = "lh_vv_silver.dbo.ref_dictionary_amenities" | defs: none
[28] markdown id=entwebmd json=unknown lines=1 | [THÊM 20/10] 20261020-entity-drop-op-cols-add-website | defs: none
[29] code id=entwebpy json=unknown lines=102 | CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: lock_is_free
[30] markdown id=enrinfomd json=unknown lines=1 | [THÊM 21/10] 20261021-refresh-gld-enr-poi-info | defs: none
[31] code id=enrinfopy json=unknown lines=213 | import uuid | defs: _schema, _create
[32] markdown id=mvpoimd json=unknown lines=1 | [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup | defs: none
[33] code id=mvpoipy json=unknown lines=220 | import uuid | defs: _names, _n, _node_edges, _info_edges
[34] markdown id=enrflagmd json=unknown lines=1 | [THÊM 22/10] 20261022-enr-landing-and-gld-flags | defs: none
[35] code id=enrflagpy json=unknown lines=253 | import uuid | defs: _want, _schema, _create_sql, _missing_flags, _add_flags, _edge_rows
[36] markdown id=ohpassmd json=unknown lines=1 | [THÊM 23/10] 20261023-entity-opening-hours-passthrough | defs: none
[37] code id=ohpasspy json=unknown lines=190 | import uuid | defs: _rows, _active, _refresh_lock, _column
[38] markdown id=peholmd json=unknown lines=1 | [THÊM 23/10] 20261023-entity-phone-email-holiday | defs: none
[39] code id=peholpy json=unknown lines=50 | ENTITY_FQ = "lh_vv_silver.dbo.slv_poi_entity_non_enrich" | defs: _fields, _issues
[40] markdown id=srvpoimd json=unknown lines=5 | [THÊM 24/10] 20261024-gld-srv-poi-from-mapping | defs: none
[41] code id=srvpoipy json=unknown lines=205 | import uuid | defs: _want, _schema, _create_sql, _edge_rows, _refresh_lock
[42] markdown id=srvratemd json=unknown lines=5 | [THÊM 26/10] 20261025-gld-srv-poi-info-rating-review | defs: none
[43] code id=srvratepy json=unknown lines=167 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[44] markdown id=mediaddlmd json=unknown lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[45] code id=mediaddlpy json=unknown lines=186 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[46] markdown id=amenddlmd json=unknown lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[47] code id=amenddlpy json=unknown lines=177 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[48] markdown id=plcadmd json=unknown lines=4 | [THÊM 26/10] 20261026-pl-name-cadence-suffix | defs: none
[49] code id=plcadpy json=unknown lines=240 | import uuid | defs: _n, _lock_rows, _refresh_lock, _issues
[50] markdown id=mlexpmd json=unknown lines=2 | [THÊM 26/10] 20261026-add-poi-multi-lang-experience | defs: none
[51] code id=mlexppy json=unknown lines=138 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
