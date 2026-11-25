# Architect handoff: 20261125-legacy-init-destination-and-poi-name

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261125-legacy-init-destination-and-poi-name --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261125-legacy-init-destination-and-poi-name/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261125-legacy-init-destination-and-poi-name | phase=triage

## STATE

id: 20261125-legacy-init-destination-and-poi-name
title: Legacy init destination JSON string and per-lang poi_name
status/owner: waiting_architecture/architect
complexity/risk: medium/high
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: data_model_change, data_evidence_required, idempotency, stateful_logic, runtime_proof_required, cross_system
gates: evidence=pass, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb
- docs/context/mapping_gld_srv_poi_multi_lang.md
- sql/postgres/gld_srv_serve.pg.sql
- tests/test_srv_poi_serving_contract.py

## VALIDATION

PASS

## RESUME

# Resume

## Status

waiting_evidence. Gates unchanged: evidence=pending, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending.

## Done this session

First probe run: destination_id type string nullable; LEGACY_INIT 25921; load_origin null 19909. Shape query failed because schema_of_json accepts only a literal. Replaced that call with rlike shape counts. D-04 still open. No notebook or DDL edits.

## Next action

Interpret the new stdout only. keep_string -> handoffs/author-input.md, run-author --kind model, then run-gate. stop_user_decision -> user_decision with the shape counts. populated_shape_unobserved -> do not treat writer to_json as the stored shape.

## Read next

.ai/tasks/20261125-legacy-init-destination-and-poi-name/evidence/results/destination_id_non_legacy_shape.txt
.ai/tasks/20261125-legacy-init-destination-and-poi-name/decision.md — D-04

## Waiting on

User re-runs evidence/probes/destination_id_non_legacy_shape.py on Fabric DEV and pastes stdout to evidence/results/destination_id_non_legacy_shape.txt.

## REQUEST

# Request

## User outcome

A one-time legacy init writes `gld_srv_poi_info.destination_id` as one JSON array string of every old-gold destination id, and writes `gld_srv_poi_multi_lang.poi_name` from the matching language. Existing Dev `LEGACY_INIT` rows are repaired the same way. The scheduled pipeline is left unchanged. Prod init is correct on the first run, with no manual fix afterwards.

Reference task `20261119-legacy-gold-poi-init` (`ready_to_merge`) is context only. Do not change its gates or artifacts.

## Scope

### In scope

- `gld_srv_poi_info.destination_id` stays `STRING` when non-`LEGACY_INIT` rows already store a JSON array string. Do not switch the column to `ARRAY` while the current writer and DDL still use a string.
- `NB_SETUP_LEGACY_GOLD_POI`: stop using `get_json_object(destination_ids, '$[0]')`. Persist the whole old-gold id array as one JSON string of strings. A non-string element, or `destination_ids` that is not a JSON array, is not wrapped and the first element is not taken; stop at `user_decision` with the observed shape. If languages of the same old `poi_id` disagree on `destination_ids`, do not pick one; stop at `user_decision`.
- Update existing `LEGACY_INIT` rows. Do not modify rows the pipeline owns.
- Add nullable `STRING` `poi_name` on `gld_srv_poi_multi_lang`. Grain stays `(poi_id, lang)`. Init reads `poi_name` for that row's `lang` from the old-gold name source the notebook already uses. Do not copy the `vi` name onto every language.
- `NB_GLD_SRV_POI_MULTI_LANG` writes `poi_name = null` on both P1 and P2. It must not read a `poi_name` column that `slv_enr_poi_info_multi_lang` does not have. The main MERGE may overwrite an init `poi_name` with null when that row becomes a pipeline row. Record this consequence in `decision.md` before implementation.
- The init notebook takes the target workspace as a parameter. Do not hardcode `sgr_visitvn_dev`. Do not guess the Prod workspace name. The old-gold source keeps the workspace already in the notebook.
- A rerun does not duplicate rows and does not change `poi_id`.
- Update `docs/context/mapping_gld_srv_poi_multi_lang.md` in this task before review.
- Domain: DDL and registry, transform/gold library, init notebook. Touch PostgreSQL only when `tests/test_srv_poi_serving_contract.py` requires the gold column set to match `apps.srv_poi_multi_lang`. Do not add `poi_name` to API JSON unless an api-mapping file already requires it.
- D-06 of `20261119-legacy-gold-poi-init` still governs `poi_name` on `gld_srv_poi_info`. The new column is on `gld_srv_poi_multi_lang` and is per language.
- The sample `["d5a59a94-9237-57cc-87e4-a13866f49b01","511b3979-5a71-5360-acf3-9feaeeea740c"]` is a shape example only. Do not seed those two UUIDs.

### Out of scope

- Gates, decisions, and code changes owned by `20261119-legacy-gold-poi-init`.
- Splitting this work into a new-column task, a Dev-repair task, and a Prod-prep task.
- Fast lane.
- Running Fabric notebooks or `docker compose` from the agent session.
- Reading `notebooks_lgc/` unless the init notebook and the prior `decision.md` do not show where `destination_ids` or per-lang `poi_name` come from.

## Acceptance criteria

- DDL keeps `gld_srv_poi_info.destination_id` as `STRING` when non-`LEGACY_INIT` rows contain a JSON array string, and the live writer plus DDL do not already use an array type.
- Init no longer takes only `$[0]`. The full old-gold id array is stored as one JSON string of strings. Invalid element types or a non-array `destination_ids` stop at `user_decision` with that shape. Conflicting `destination_ids` across languages of one old `poi_id` stop at `user_decision`.
- `gld_srv_poi_multi_lang.poi_name` is nullable `STRING`. Grain remains `(poi_id, lang)`. Init fills the name of that language only.
- `NB_GLD_SRV_POI_MULTI_LANG` sets `poi_name` null on P1 and P2 without reading a missing source column. Pipeline ownership may replace the init name with null. That consequence is in `decision.md` before the edit.
- Target workspace is a parameter. Old-gold workspace stays as already written. Rerun does not insert a second row and does not change `poi_id`.

## Constraints

- One task, one chat, the full `docs/agent-system/WORKFLOW.md` §6 path. Stop only for a Fabric DEV probe, `user_decision`, a CLI or model fallback, a round cap, or `waiting_runtime`.
- `data_model_change` applies because `poi_name` is a new column. Required reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, and `state-correctness-reviewer` (init MERGE and the main MERGE both write `poi_name`).
- If the stored shape of non-`LEGACY_INIT` `destination_id` is not in the repo, write the smallest probe, move to `waiting_evidence`, and stop. The probe counts shapes only, returns no bulk UUIDs, and stays within 50 rows.
- After evidence is sufficient: `handoffs/author-input.md`, `run-author --kind model`, then `run-gate`. Main does not write `model-design.md` or `architecture.md`.
- Implement only the architecture edit list. Record any deviation in `decision.md` before further edits. Save `FILE` blocks with `python scripts/vv.py materialize <task-id> --write`.
- `verify` must pass before `reviewing` and `run-gate`. Fix P0/P1 in this chat inside the round cap.
- Dev repair and Prod init are user-run: `run-author --kind runbook`, then stop at `waiting_runtime`. The runbook takes the target workspace, orders the repair of existing `LEGACY_INIT` rows, and states how to check that `destination_id` is a JSON array string and `poi_name` matches the language. Do not run the notebook on Fabric in this chat.
- On every stop, overwrite `resume.md` (at most 40 lines) and close with `python scripts/vv.py closeout <task-id>`. Do not commit.
- `tests/test_srv_poi_serving_contract.py` `test_gold_and_pg_columns_and_types_match` compares `NB_SETUP_INITIAL_DDL` `TABLE_SPECS` for `gld_srv_poi_*` with `sql/postgres/gld_srv_serve.pg.sql` and, when the service tree is present, with JPA entities. A `TABLE_SPECS` column add fails that test until PostgreSQL matches. API JSON stays unchanged unless an api-mapping file already names `poi_name`.

## Classification rationale

- Complexity: `medium`. New column, two MERGE writers on `poi_name`, and a destination encoding change. Not a fast lane (behavior change and more than two files).
- Risk: `high`. Idempotent rerun, two writers on one column, and the Dev repair / Prod init can be proved only at runtime.
- Architecture: required. New column ownership and the commit that may null an init `poi_name` need an Architect edit list. `data_model_change` requires `model-design.md` before that gate.
- Evidence: required. Repo code shows `slv_enr_poi_destination.destination_id` as `to_json` of the `id` array and `NB_GLD_SRV_POI_INFO` copies it 1-1 into a `STRING` column. No stored sample of non-`LEGACY_INIT` `gld_srv_poi_info.destination_id` values is in the repo. DDL type stays open until the probe counts those shapes.
- Runtime proof: required. The user runs the Dev `LEGACY_INIT` repair and the Prod init from the runbook.
- Reviewer routing: `sql-data-reviewer` (DDL and both MERGEs), `spark-runtime-reviewer` (Fabric notebooks), `state-correctness-reviewer` (init MERGE and main MERGE both write `poi_name`). Risk `high` also requires the risk gate after specialist review.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | `poi_name` theo lang trên `gld_srv_poi_multi_lang` | Cột mới `poi_name` là STRING, nullable. Grain vẫn `(poi_id, lang)`. Init lấy `poi_name` của đúng lang từ nguồn gold cũ mà notebook đang dùng cho tên. Không lấy tên lang `vi` cho mọi dòng. D-06 của `20261119-legacy-gold-poi-init` vẫn áp cho `poi_name` trên `gld_srv_poi_info`. | request.md Acceptance criteria | 2026-11-25 |
| D-02 | Luồng chính ghi đè `poi_name` init bằng null | `NB_GLD_SRV_POI_MULTI_LANG` ghi `poi_name = null` trên cả P1 và P2. Không đọc một cột chưa có của `slv_enr_poi_info_multi_lang`. MERGE của luồng chính được phép ghi đè `poi_name` init bằng null khi dòng đó thành dòng pipeline. Init không sửa dòng pipeline đang sở hữu. | request.md Acceptance criteria | 2026-11-25 |
| D-03 | Workspace đích của notebook init | Notebook init nhận workspace đích bằng tham số. Không gắn cứng `sgr_visitvn_dev`. Không đoán tên workspace Prod. Nguồn gold cũ giữ workspace đang có trong notebook. | request.md Acceptance criteria | 2026-11-25 |
| D-04 | Giữ `destination_id` là STRING | Giữ `gld_srv_poi_info.destination_id` là STRING. Không đổi sang ARRAY. Probe Fabric DEV: cột `string` nullable; dòng `load_origin` null có 19797 `json_array_string`, 2 `json_array_empty`, 110 null, `bad=0`, verdict `keep_string`. | evidence/results/destination_id_non_legacy_shape.txt | 2026-11-25 |

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
- decision.md | 2859 bytes
- evidence/plan.md | 2015 bytes
- evidence/probes/destination_id_non_legacy_shape.py | 3734 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/destination_id_non_legacy_shape.txt | 273 bytes
- handoffs/architect.md | 28911 bytes | large: use toc/show
- handoffs/author-input.md | 3683 bytes
- model-design.md | 12508 bytes
- request.md | 7380 bytes
- resume.md | 1119 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1720 bytes

## NEXT

python scripts/vv.py run-gate 20261125-legacy-init-destination-and-poi-name

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb (49201 bytes)

[0] markdown id=lgpmd json=3-14 lines=5 | NB_SETUP_LEGACY_GOLD_POI | defs: none
[1] code id=lgpparams json=15-30 lines=2 | p_mode = "PLAN" | defs: none
[2] code id=lgplib json=31-45 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=lgpconst json=46-68 lines=9 | OLD = "sgr_visitvn_prd_batch.lh_vv_gold.dbo" | defs: none
[4] code id=lgphours json=69-181 lines=99 | import json | defs: _int, _open, _closed, _all_day, _dump, google_hours, partner_hours, operating_hours
[5] code id=lgppure json=182-300 lines=105 | ORIGIN = "LEGACY_INIT" | defs: legacy_source_name, new_poi_id, insert_only_sql, single_payload, legacy_upsert_sql, legacy_hours, amenity_enum_values, add, walk
[6] code id=lgpmain json=301-824 lines=510 | import inspect | defs: _workspace_name, _history_version, old, present_counts, to_target, _metrics, _commit_lookup, write_insert_only, _j

### notebooks/NB_CREATE_DDL.ipynb (412768 bytes)

[0] markdown id=b0b1203a-7c40-48bf-bfc9-7b29d7064bdc json=3-25 lines=6 | NB_CREATE_DDL — 7 bảng control `lh_vv_ctrl.dbo` | defs: none
[1] markdown id=b7e4c1a0-6f28-4d3e-9a15-2c8d0e4f6a91 json=26-36 lines=4 | Ghi chú migration 08/10 | defs: none
[2] markdown id=d20a367e-98da-4b91-9237-dd2b2cebfeae json=37-54 lines=1 | Tạo bảng ctrl_mng_pipeline_config | defs: none
[3] code id=80154b61-ea1a-415b-834c-3c07d689d036 json=55-177 lines=108 | %%sql | defs: none
[4] markdown id=<none> json=178-188 lines=5 | Reset silver (DROP/DELETE) không nằm trong luồng tạo bảng. | defs: none
[5] code id=502cd242 json=189-242 lines=40 | %%sql | defs: none
[6] markdown id=a0c11600-5f15-4ec4-ab3b-cd590b5ce6a8 json=243-260 lines=1 | Tạo bảng ctrl_mng_watermark | defs: none
[7] markdown id=e80b9799-8de0-4319-8c62-be8096d373c8 json=261-288 lines=11 | **[SỬA 03/10] Bỏ cell MERGE watermark từ `lh_vv_bronze.partner.brz_watermark`**  | defs: none
[8] code id=3ea73e14-6a1f-42a5-b960-34123b0a3fc4 json=289-304 lines=51 | %%sql | defs: none
[9] markdown id=ed3d2dc0-d9f4-4cd7-b5aa-5e65afb7aca0 json=305-322 lines=1 | Tạo bảng ctrl_cfg_schema_registry | defs: none
[10] code id=d06c9671-6b88-4afa-97a8-d028f6b9e936 json=323-366 lines=30 | CONFIG_TABLE = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry" | defs: none
[11] code id=28e2be98-7f9a-41d5-b7f8-b4d4a5baf5ff json=367-915 lines=535 | TABLE_CONFIGS = [ | defs: none
[12] code id=0f228dc1-7bc8-4ed2-a10f-e6125a806e83 json=916-1116 lines=186 | from pyspark.sql.types import ( | defs: resolve_type, flatten_table_configs, validate_rows, seed_registry, show_registry
[13] markdown id=7517dd85-f292-4361-9d9d-6bad3f2e4f34 json=1117-1137 lines=4 | **[THÊM 03/10 - 3P] Seed registry nguồn 3rd-party `brz_3rd_crawler_poi_stream`** | defs: none
[14] code id=e9c137c5-c9fc-4f8f-a925-bc511cfd71a7 json=1138-1335 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[15] code id=0271d481-4188-43ab-8cb4-03acd3452550 json=1336-1355 lines=5 | seed_registry(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream" | defs: none
[16] markdown id=5c2996a4-3ddc-4924-8645-c0cc545cdd63 json=1356-1373 lines=1 | Tạo các bảng log & debug | defs: none
[17] code id=7dad05d9-20f0-4ab4-af1e-dec1dfe5d8cb json=1374-1515 lines=127 | %%sql | defs: none
[18] code id=ea524452-c135-4ef4-b4a8-3a076fa67ee7 json=1516-1551 lines=22 | GOLD_LOG_COLUMNS = ( | defs: none
[19] markdown id=de14c4c2-7925-4582-b080-8b0a660fb99c json=1552-1569 lines=1 | Kiểm tra cấu hình | defs: none
[20] code id=6e95fc60-2ef9-47af-a250-95844179c188 json=1570-1655 lines=71 | %%sql | defs: none
[21] code id=5784a286-d45c-4be8-8223-5a43800b6e2b json=1656-1690 lines=17 | %%sql | defs: none
[22] markdown id=enrddlmd json=1691-1700 lines=3 | [THÊM 13/10] Gold enr và cạnh PL_VV_TRANS_SLV_TO_ENR_15P | defs: none
[23] code id=enrddlpy json=1701-1844 lines=130 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _ddl, _expected_type
[24] markdown id=nonenrmd json=1845-1857 lines=1 | [THÊM 19/10] 20261019-poi-entity-non-enrich | defs: none
[25] code id=nonenrpy json=1858-1935 lines=64 | import re | defs: category_group, with_category_group
[26] markdown id=dictseedmd json=1936-1943 lines=1 | [THÊM 20/10] 20261020-dictionary-seed-from-mapping | defs: none
[27] code id=dictseedpy json=1944-1994 lines=37 | AM_FQ = "lh_vv_silver.dbo.ref_dictionary_amenities" | defs: none
[28] markdown id=entwebmd json=1995-2002 lines=1 | [THÊM 20/10] 20261020-entity-drop-op-cols-add-website | defs: none
[29] code id=entwebpy json=2003-2118 lines=102 | CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: lock_is_free
[30] markdown id=amenpnmd json=2119-2132 lines=7 | [THÊM 18/11] 20261118-amenity-poi-id-align | defs: none
[31] code id=amenpnpy json=2133-2281 lines=140 | import uuid | defs: _refresh_lock, _edges
[32] markdown id=enrinfomd json=2282-2289 lines=1 | [THÊM 21/10] 20261021-refresh-gld-enr-poi-info | defs: none
[33] code id=enrinfopy json=2290-2516 lines=213 | import uuid | defs: _schema, _create
[34] markdown id=mvpoimd json=2517-2524 lines=1 | [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup | defs: none
[35] code id=mvpoipy json=2525-2758 lines=220 | import uuid | defs: _names, _n, _node_edges, _info_edges
[36] markdown id=enrflagmd json=2759-2766 lines=1 | [THÊM 22/10] 20261022-enr-landing-and-gld-flags | defs: none
[37] code id=enrflagpy json=2767-3033 lines=253 | import uuid | defs: _want, _schema, _create_sql, _missing_flags, _add_flags, _edge_rows
[38] markdown id=ohpassmd json=3034-3041 lines=1 | [THÊM 23/10] 20261023-entity-opening-hours-passthrough | defs: none
[39] code id=ohpasspy json=3042-3245 lines=190 | import uuid | defs: _rows, _active, _refresh_lock, _column
[40] markdown id=peholmd json=3246-3253 lines=1 | [THÊM 23/10] 20261023-entity-phone-email-holiday | defs: none
[41] code id=peholpy json=3254-3317 lines=50 | ENTITY_FQ = "lh_vv_silver.dbo.slv_poi_entity_non_enrich" | defs: _fields, _issues
[42] markdown id=srvpoimd json=3318-3329 lines=5 | [THÊM 24/10] 20261024-gld-srv-poi-from-mapping | defs: none
[43] code id=srvpoipy json=3330-3548 lines=205 | import uuid | defs: _want, _schema, _create_sql, _edge_rows, _refresh_lock
[44] markdown id=srvratemd json=3549-3560 lines=5 | [THÊM 26/10] 20261025-gld-srv-poi-info-rating-review | defs: none
[45] code id=srvratepy json=3561-3741 lines=167 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[46] markdown id=mediaddlmd json=3742-3751 lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[47] code id=mediaddlpy json=3752-3951 lines=186 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[48] markdown id=amenddlmd json=3952-3963 lines=5 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[49] code id=amenddlpy json=3964-4155 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[50] markdown id=plcadmd json=4156-4166 lines=4 | [THÊM 26/10] 20261026-pl-name-cadence-suffix | defs: none
[51] code id=plcadpy json=4167-4420 lines=240 | import uuid | defs: _n, _lock_rows, _refresh_lock, _issues
[52] markdown id=mlexpmd json=4421-4429 lines=2 | [THÊM 26/10] 20261026-add-poi-multi-lang-experience | defs: none
[53] code id=mlexppy json=4430-4581 lines=138 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[54] markdown id=srvrevmd json=4582-4591 lines=3 | [THÊM 27/10] 20261026-gld-srv-poi-review | defs: none
[55] code id=srvrevpy json=4592-4800 lines=195 | import uuid | defs: _want, _schema, _edge_rows, _create_sql, _refresh_lock
[56] markdown id=rvi18nenrmd json=4801-4810 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (1/2) | defs: none
[57] code id=rvi18nenrpy json=4811-4973 lines=149 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[58] markdown id=rvi18ngldmd json=4974-4983 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (2/2) | defs: none
[59] code id=rvi18ngldpy json=4984-5136 lines=139 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[60] markdown id=mlsrcmd json=5137-5146 lines=3 | [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr | defs: none
[61] code id=mlsrcpy json=5147-5265 lines=105 | import uuid | defs: _want, _schema, _refresh_lock
[62] markdown id=cmscfgmd json=5266-5275 lines=3 | [THÊM 08/11] 20261104-extract-cms-raw-data | defs: none
[63] code id=cmscfgpy json=5276-5385 lines=96 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _cms_ts, _cms
[64] markdown id=srvcovermd json=5386-5396 lines=4 | [THÊM 08/11] 20261108-gld-srv-poi-info-cover | defs: none
[65] code id=srvcoverpy json=5397-5588 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[66] markdown id=poidestmd json=5589-5599 lines=4 | [THÊM 12/11] 20261112-poi-destination-name-api | defs: none
[67] code id=poidestpy json=5600-5765 lines=152 | import uuid | defs: _want, _schema, _accepted, _anchor, _refresh_lock
[68] markdown id=enrmergemd json=5766-5773 lines=1 | [THÊM 12/11] 20261112-enr-poi-append-to-merge | defs: none
[69] code id=enrmergepy json=5774-5950 lines=163 | import uuid | defs: _release_lock, _refresh_lock, _types, _modes, _run
[70] markdown id=srvactivemd json=5951-5961 lines=4 | [THÊM 16/11] 20261116-srv-poi-info-is-active | defs: none
[71] code id=srvactivepy json=5962-6089 lines=114 | import uuid | defs: _want, _schema, _refresh_lock
[72] markdown id=enrbrzcfgmd json=6090-6101 lines=5 | B3 — cell `enrbrzcfgpy` | defs: none
[73] code id=enrbrzcfgpy json=6102-6116 lines=96 | def _enr(path, typ="string", rule=None): | defs: _enr
[74] markdown id=enrbrzmd json=6117-6128 lines=5 | B2 — cell `enrbrzpy` | defs: none
[75] code id=enrbrzpy json=6129-6143 lines=269 | def plan_rewrite(current, target, renames, drops): | defs: plan_rewrite, should_auto_restore, _touch_locks, _head, _fence, _confirm_skip, rewrite_table, _norm, _take
[76] markdown id=enrgldmd json=6144-6155 lines=5 | B5 — cell `enrgldpy` | defs: none
[77] code id=enrgldpy json=6156-6170 lines=257 | def plan_rewrite(current, target, renames, drops): | defs: plan_rewrite, should_auto_restore, _touch_locks, _head, _fence, _confirm_skip, rewrite_table, _norm
[78] markdown id=legacyidmd json=6171-6185 lines=3 | [THÊM 19/11] 20261119-legacy-gold-poi-init | defs: none
[79] code id=legacyidpy json=6186-6319 lines=120 | import uuid | defs: _want, _schema, _exists, _refresh_lock

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (224000 bytes)

[0] markdown id=init_md json=3-10 lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=11-28 lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=29-43 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=44-58 lines=534 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=59-73 lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=74-271 lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_cfg_cms json=272-329 lines=44 | def _cms_ts(path): | defs: _cms_ts, _cms
[7] code id=init_cfg_enr json=330-344 lines=45 | def _enr(path, typ="string", rule=None): | defs: _enr
[8] code id=init_registry_pure json=345-359 lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[9] code id=init_seed_ctrl json=360-482 lines=109 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[10] code id=init_seed_place_type json=483-951 lines=455 | import re | defs: validate_seed
[11] code id=init_seed_amenity json=952-1256 lines=291 | import re | defs: amenity_keys, amenity_code, amenity_seed_rows, validate_seed
[12] code id=init_plan json=1257-1271 lines=148 | import json | defs: _missing, _dup_keys, _target_dup_keys
[13] code id=init_ddl json=1272-1286 lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[14] code id=init_seed_write json=1287-1480 lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[15] code id=init_verify json=1481-1495 lines=30 | verify_errors = [] | defs: none
[16] code id=init_exit json=1496-1510 lines=7 | summary = { | defs: none
