# Architect handoff: 20261022-enr-landing-and-gld-flags

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261022-enr-landing-and-gld-flags --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261022-enr-landing-and-gld-flags/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261022-enr-landing-and-gld-flags | phase=triage

## STATE

id: 20261022-enr-landing-and-gld-flags
title: Silver enrich landing tables and gold enrich flags
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: data_model_change, cross_state_impact, idempotency, runtime_proof_required, design_tradeoffs
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_ENR_POI_INFO.ipynb
- notebooks/NB_ENR_POI_REVIEW.ipynb
- tests/test_initial_ddl_contract.py
- tests/test_enr_poi_contract.py

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

Returned enrich data lands in three silver tables. Gold marks a POI or review that already has a multi-language or destination enrich row, so downstream does not wait for enrich content on gold.

## Scope

### In scope

- DDL only for three landing tables in `lh_vv_silver.dbo`: `slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination`, `slv_enr_poi_review_multi_lang`. No notebook loads those tables.
- `lh_vv_gold.enr.gld_enr_poi_info`: remove `district` and `destination_name` from the contract and from the node processing. Keep `street`, `ward`, `city`, `full_address`. Add existence flags `is_enriched_multi_lang` and `is_enriched_destination`.
- `lh_vv_gold.enr.gld_enr_poi_review`: add existence flag `is_enriched_multi_lang`. Keep the other columns and logic.
- Both `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL` in this task. Update `tests/test_initial_ddl_contract.py` when the DDL source changes. Update the INFO and REVIEW lists in `tests/test_enr_poi_contract.py` so they match the node notebooks. Leave the COORD list unchanged.

### Out of scope

- A load notebook for the three landing tables.
- Copying enrich text or address content onto gold.
- A new schema, a new orchestration tier, or a new `UNIQUE` key.
- `gld_enr_poi_coordinate` columns, including its own `district` and `destination_name`.
- Task `20261021-refresh-gld-enr-poi-info`, `notebooks_lgc/`, `docs/context/3p-google/*.txt`, pipeline manifests, and other task artifacts.
- `docs/context/gld_enr_poi_info_review.md` unless the user later asks to update that catalog. It documents the two dropped columns. No other runtime reader of `gld_enr_poi_info.district` or `gld_enr_poi_info.destination_name` was found in notebooks, tests, SQL, or JSON.

## Acceptance criteria

- Landing columns and nullability match the locked list. The review landing table has `description` corrected from the typed `descrption`, and it has no `lang` column. `created_at` and `updated_at` are nullable `TIMESTAMP`, the same type as `gld_enr_poi_info`. No `UNIQUE` and no composite key beyond the stated `NOT NULL`.
- `is_enriched_multi_lang` on info is true when `poi_id` has at least one row in `slv_enr_poi_info_multi_lang`, otherwise false. `is_enriched_destination` is true when `poi_id` has at least one row in `slv_enr_poi_destination`, otherwise false.
- `is_enriched_multi_lang` on review is true when `review_id` has at least one row in `slv_enr_poi_review_multi_lang`, otherwise false.
- An unmatched `poi_id` or `review_id` is false. Flags do not depend on landing grain.
- Setup edits the empty-environment definition in place. Create appends one markdown `[THÊM dd/mm] <task-id>` and one self-contained patch cell at the end. Old Create cells stay unchanged. No `DROP` of a table that has data. Columns added to an existing gold table are nullable on `ALTER`. The notebook writes true or false when it runs.
- The patch cell and the runbook state how to remove `district` and `destination_name` on an environment that already has the table. No silent `DROP COLUMN`.
- The info column contract is the current `INFO_COLS` patch cell in `NB_CREATE_DDL` (cell `enrinfopy`), which still contains `district` and `destination_name`. Cell `enrddlpy` is the old info contract. `REVIEW_COLS` still lives only in cell `enrddlpy` because no later patch replaces it.
- Gold node notebooks read the landing tables when computing flags. A ctrl or orchestrator edge is added only when architecture requires it so flags refresh after a new landing row. No new orchestration tier.
- Another consumer of `gld_enr_poi_info.district` or `.destination_name`: list the file and stop at `user_decision`. Do not edit it in this task.

## Constraints

- Domain: lib transform/gold and DDL/registry. One task, one chat, through model, architecture, implement, review, and runtime.
- Prefix `slv_enr_` is not in naming §1. The user locked the table names. Use `lh_vv_silver.dbo.slv_enr_*`.
- Landing grain and unique key are not locked. Do not choose a key. If `UNIQUE` is required for `MERGE` or to prevent duplicates and the repo does not answer it, stop at `user_decision` with each option.
- Gold column contract comes from the current Create patch, not from cell `enrddlpy` info columns.
- Missing evidence at any gate: smallest probe, then `waiting_evidence`. Do not invent data characteristics.

## Classification rationale

- Complexity: medium. New silver tables, dropped gold columns, and derived flags. Signals: `data_model_change`, `cross_state_impact`, `idempotency`, `runtime_proof_required`, `design_tradeoffs`.
- Risk: medium. Bounded column and flag change. Rollback is the runbook. Not high: no new concurrency, watermark owner, or cross-system write.
- Architecture: required. Gold gains a read of new silver tables, column removal is a state change, and a ctrl edge is a real trade-off architecture must accept or reject.
- Evidence: not required to start. The column contract is in the notebooks. Flags are key existence, not a distribution. Uniqueness of landing rows is a user decision if a later gate needs a key, not a Fabric probe.
- Runtime proof: required. Existing gold tables need an explicit patch and column-removal steps. The node must write true or false on a real run.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`. No `fabric-pipeline-reviewer` unless architecture changes pipeline JSON. No risk gate at medium risk.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Tiền tố landing | Prefix `slv_enr_` chưa có trong §1 naming. Người dùng đã chốt tên bảng. Dùng `lh_vv_silver.dbo.slv_enr_*`. Không tạo schema mới. | request.md Constraints | 2026-10-22 |
| D-02 | Cột landing | Người yêu cầu gõ nhầm `descrption`; tên cột là `description`. Không thêm cột `lang` vào bảng review. `created_at` và `updated_at` cùng kiểu `TIMESTAMP` với `gld_enr_poi_info`, nullable vì không được khai `NOT NULL`. Không thêm `UNIQUE` hay khoá tổ hợp ngoài `NOT NULL` đã nêu. | request.md Acceptance criteria | 2026-10-22 |
| D-03 | Grain landing | Grain và khoá duy nhất của 3 bảng landing chưa được chốt. Cờ không phụ thuộc grain. Không tự chọn khoá. | request.md Constraints | 2026-10-22 |
| D-04 | Cờ gold | Cờ chỉ kiểm tra tồn tại khoá. Không chép nội dung enrich sang gold. `poi_id` hoặc `review_id` không khớp thì false. | request.md Acceptance criteria | 2026-10-22 |
| D-05 | Cột info bỏ | Bỏ `district` và `destination_name` khỏi hợp đồng và khỏi câu xử lý của `gld_enr_poi_info`. Giữ `street`, `ward`, `city`, `full_address`. | request.md Scope | 2026-10-22 |
| D-06 | Hợp đồng cột | Hợp đồng cột `gld_enr_poi_info` lấy từ cell patch hiện hành `enrinfopy` của `NB_CREATE_DDL` (`INFO_COLS` đang có `district`, `destination_name`). Không dùng `INFO_COLS` của cell `enrddlpy`. `REVIEW_COLS` chỉ còn ở cell `enrddlpy` vì chưa có patch sau thay nó. | request.md Acceptance criteria | 2026-10-22 |
| D-07 | NULL khi ALTER | Cột thêm vào bảng gold đã tồn tại phải nullable ở `ALTER`. Notebook ghi true hoặc false khi chạy. | request.md Acceptance criteria | 2026-10-22 |
| D-08 | Không nạp landing | Task này không viết notebook nạp dữ liệu vào 3 bảng landing. | request.md Scope | 2026-10-22 |

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
- decision.md | 3722 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 3720 bytes
- model-design.md | 14498 bytes
- request.md | 5530 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1624 bytes

## NEXT

python scripts/vv.py run-gate 20261022-enr-landing-and-gld-flags

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (206333 bytes)

[0] markdown id=init_md json=47-54 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=55-72 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=73-87 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=88-438 lines=337 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=439-453 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=454-651 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=652-666 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=667-744 lines=64 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=745-1213 lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=1214-1489 lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=1490-1647 lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=1648-1662 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=1663-1856 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=1857-1871 lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=1872-1886 lines=7 | summary = { | defs: none

### notebooks/NB_CREATE_DDL.ipynb (172473 bytes)

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
[26] markdown id=dictseedmd json=1978-1985 lines=1 | [THÊM 20/10] 20261020-dictionary-seed-from-mapping | defs: none
[27] code id=dictseedpy json=1986-2036 lines=37 | AM_FQ = "lh_vv_silver.dbo.ref_dictionary_amenities" | defs: none
[28] markdown id=entwebmd json=2037-2044 lines=1 | [THÊM 20/10] 20261020-entity-drop-op-cols-add-website | defs: none
[29] code id=entwebpy json=2045-2160 lines=102 | CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: lock_is_free
[30] markdown id=enrinfomd json=2161-2168 lines=1 | [THÊM 21/10] 20261021-refresh-gld-enr-poi-info | defs: none
[31] code id=enrinfopy json=2169-2395 lines=213 | import uuid | defs: _schema, _create
[32] markdown id=mvpoimd json=2396-2403 lines=1 | [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup | defs: none
[33] code id=mvpoipy json=2404-2637 lines=220 | import uuid | defs: _names, _n, _node_edges, _info_edges
