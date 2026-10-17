# Architect handoff: 20261016-setup-initial-ddl-and-patch-ddl

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261016-setup-initial-ddl-and-patch-ddl/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261016-setup-initial-ddl-and-patch-ddl | phase=triage

## STATE

id: 20261016-setup-initial-ddl-and-patch-ddl
title: Split one-shot initial DDL from the patch DDL notebook
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: idempotency, partial_failure, design_tradeoffs, runtime_proof_required
gates: evidence=not_required, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_SETUP_POI_ENTITY.ipynb
- docs/context/02_NAMING_CONVENTION.md
- docs/context/CTRL_TABLES_CONTEXT.md - AGENTS.md - notebooks/NB_SETUP_POI_AMENITY.ipynb - notebooks/NB_SLV_POI_ENTITY.ipynb - notebooks/NB_SLV_POI_AMENITY.ipynb

## VALIDATION

PASS

## RESUME

# Resume

Status: waiting_evidence
Done this session: Classified high/high (idempotency, partial_failure, design_tradeoffs, runtime_proof_required). Fast lane rejected. Architecture gate returned EVIDENCE_REQUIRED. Design is final except user decision U1. No implementation.
Next action: Record the user's U1 choice in decision.md (`Quyết định hiện hành`), transition to waiting_architecture, and run `python scripts/vv.py run-gate 20261016-setup-initial-ddl-and-patch-ddl`. Do not implement before round 2.
Read next: `.ai/tasks/20261016-setup-initial-ddl-and-patch-ddl/architecture.md` — `17. Required user decision (blocks E12–E14 only)` and Main brief `Decision`.
Waiting on: U1. Option A: treat existing `ctrl_mng_pipeline_config.nb_name` as the demonstration. Option B: user names table (architecture §5.1), nullable column, Spark type, and Vietnamese comment.

## REQUEST

# Request

## User outcome

VSVN is not in production. An operator can build an empty environment in one manual run from the DDL and configuration inserts already defined in the repository. After that, each new DDL or configuration-insert request patches only the new change on an environment that already has the tables. Agents follow that split on every later request.

## Scope

### In scope

- One manual first-run notebook that contains the full current DDL and configuration `INSERT` definitions from the repository, excluding `notebooks_lgc/`.
- `notebooks/NB_CREATE_DDL.ipynb` remains the patch notebook. New DDL or configuration `INSERT` requests are added there so they can run where the tables already exist.
- An agent-facing rule: a new DDL or configuration `INSERT` request must update both notebooks. The first-run notebook keeps the complete definition used to build an empty environment. `NB_CREATE_DDL` contains only the new change and must run against the existing environment.
- `docs/context/02_NAMING_CONVENTION.md`: one section that assigns those two roles. `AGENTS.md` currently says `NB_CREATE_DDL` creates the control tables; that sentence must stay consistent with the split.
- One new DDL change, for example an added column, present as a patch cell in `NB_CREATE_DDL` and as the full definition in the first-run notebook. User decision U1 selects the existing column `ctrl_mng_pipeline_config.nb_name`. Do not add a new column.
- `lh_vv_silver.dbo.slv_poi_amenity` and `lh_vv_silver.dbo.slv_poi_entity` are part of the first-run inventory. Sources: task `20261016-ref-amenities-poi-amenity` (`notebooks/NB_SETUP_POI_AMENITY.ipynb`) and task `20261016-ref-place-type-poi-entity` (`notebooks/NB_SLV_POI_ENTITY.ipynb`, cell `b1entitybuild`). `slv_poi_amenity` is already architecture §5.1 row 13. `slv_poi_entity` is not in that inventory and must be added from the repository definition. Do not invent columns.

### Out of scope

- `notebooks_lgc/`.
- Replacing `NB_CREATE_DDL` with a copy of the first-run notebook.
- Restoring `DROP` cells that have already been removed from `NB_CREATE_DDL`.
- `DROP` of tables that already hold data, in the first-run notebook.
- Configuration seeds taken from live Fabric tables (`INSERT … SELECT` against the running environment).
- Pipeline JSON, and any edit to extract or recompute notebooks. Their existing table definitions are sources for the first-run notebook. Control-table behavior stays limited to the DDL and configuration seeds already defined in the repository.

## Acceptance criteria

- The first-run notebook has `p_apply` defaulting to `false` and prints the DDL list and the configuration `INSERT` row counts before it writes.
- `p_apply = true` on an empty environment creates the full table set and seeds. Running it again does not duplicate configuration rows.
- `NB_CREATE_DDL` is not replaced by a copy of the first-run notebook. `DROP` cells already removed from `NB_CREATE_DDL` are not put back.
- `docs/context/02_NAMING_CONVENTION.md` has a section that assigns the two notebook roles.
- A new DDL change, for example an added column, appears as a patch cell in `NB_CREATE_DDL` and as the full definition in the first-run notebook. U1 is satisfied by the existing `ctrl_mng_pipeline_config.nb_name` pair, with no new column.
- The first-run notebook creates `lh_vv_silver.dbo.slv_poi_amenity` and `lh_vv_silver.dbo.slv_poi_entity` from the definitions already in the two 2026-10-16 tasks named above.

## Constraints

- Seeds come from definitions already in the repository, not from `INSERT … SELECT` against Fabric.
- Do not invent a business column, key, or seed row that the repository does not already define. If the required example change has no already-specified column, the architecture must stop for a user decision instead of choosing one.
- The first-run notebook must not `DROP` tables that already contain data.
- `p_apply` behavior should follow the existing manual-setup pattern in `notebooks/NB_SETUP_POI_ENTITY.ipynb` (default `false`: print the plan, then exit without writing).
- Name the first-run notebook with the existing `NB_SETUP_*` role. Do not rename `NB_CREATE_DDL`.

## Classification rationale

- Complexity: `high`. Signals: `idempotency`, `partial_failure`, `design_tradeoffs`, `runtime_proof_required`. A rerun must not duplicate configuration rows; a multi-statement apply can stop midway; the full definition and the patch notebook are two viable shapes with different failure behavior; empty-environment proof cannot be done from the repository alone.
- Risk: `high`. Idempotent writes of control configuration, and proof that exists only at runtime, match the high-risk criteria. The no-`DROP` constraint keeps this below `critical`.
- Architecture: required. Material trade-offs remain: which statements belong in the full inventory, how a rerun stays idempotent after a partial apply, where the agent rule is stored without breaking the `AGENTS.md` size limit, and which already-defined column (if any) demonstrates the dual update. This is not a fast lane: more than two files change, and the notebook writes tables and seeds.
- Evidence: not required. Current DDL and seeds are in the repository. Live Fabric contents must not be used as the seed source.
- Runtime proof: required. Acceptance includes `p_apply = true` on an empty environment and a rerun that does not duplicate configuration rows.
- Reviewer routing: `sql-data-reviewer` (DDL, seed statements, deterministic rerun), `spark-runtime-reviewer` (Fabric notebook contract, `p_apply`, apply and exit), `state-correctness-reviewer` (durable control-row idempotency and partial apply). No pipeline reviewer. Risk gate runs because risk is `high`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| U1 | Cột minh họa phải sửa cả hai notebook | A. Dùng `ctrl_mng_pipeline_config.nb_name` đã có trong repo. Không thêm cột mới. | architecture.md §17 | 2026-10-16 |
| U2 | Hai bảng silver trong notebook lần đầu | Thêm `slv_poi_amenity` và `slv_poi_entity` từ hai task `20261016-ref-amenities-poi-amenity` và `20261016-ref-place-type-poi-entity`. | User, 2026-10-16 | 2026-10-16 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 45377 bytes

## FILES

- architecture.md | 45377 bytes | large: use toc/show
- decision.md | 1851 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 15510 bytes
- request.md | 5799 bytes
- resume.md | 887 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1603 bytes

## NEXT

python scripts/vv.py run-gate 20261016-setup-initial-ddl-and-patch-ddl

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
