# Architect handoff: 20261118-amenity-poi-id-align

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261118-amenity-poi-id-align --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261118-amenity-poi-id-align/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261118-amenity-poi-id-align | phase=triage

## STATE

id: 20261118-amenity-poi-id-align
title: Align amenity poi_id with gld_srv_poi_info
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=True, runtime_required=False
signals: data_evidence_required, cross_state_impact, data_model_change
gates: evidence=pass, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SLV_POI_AMENITY.ipynb
- notebooks/NB_GLD_SRV_POI_AMENITY.ipynb
- notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb
- notebooks/NB_GLD_SRV_POI_INFO.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- docs/context/mapping_gld_srv_poi_amenity.md
- tests/test_poi_amenity_contract.py

## VALIDATION

PASS

## RESUME

# Resume

Status: user_decision

Done this session: Recorded D-11. Partner amenities read `locale = 'vi'` `amentities.facilities.specialty_tags`, fall back to `slv_pn_business_services` when that value is null, left join partner `ref_dictionary_amenities.amenity_raw`, and still write labels that do not match. Reran `run-author --kind model`. Merged `model-design.new.md` into `model-design.md`. Did not run architecture: Conflicts 3, 4, and 5 are still open. No notebook edit.

Next action: Wait for `business_sector`, `amenity_group`, and the multi-match rule. Then run architecture before code. Do not invent those values.

Read next: `model-design.md` section `Conflicts and questions` items 3, 4, and 5; `decision.md` section `D-11`

Waiting on: user answers for sector source, amenity_group value, and duplicate dictionary matches

## REQUEST

# Request

## User outcome

`slv_poi_amenity` and `gld_srv_poi_amenity` rows for one POI carry the same `poi_id` that `gld_srv_poi_info` stores for that POI.

## Scope

### In scope

- Compare the `poi_id` space of `NB_SLV_POI_AMENITY`, `NB_SLV_POI_ENTITY_NON_ENRICH`, and `NB_GLD_SRV_POI_INFO`.
- Record one cause in `decision.md` before any code change.
- If the repository does not show the cause, the smallest Fabric DEV probe: how many amenity `poi_id` values are on `gld_srv_poi_info`, and how many are not.
- After a single chosen fix: align code, `docs/context/mapping_gld_srv_poi_amenity.md`, and `tests/test_poi_amenity_contract.py`; verify; review with `sql-data-reviewer` and `spark-runtime-reviewer` (add `state-correctness-reviewer` only if the MERGE key or write order changes); write `runtime-runbook.md` and stop before the Fabric DEV rerun.

### Out of scope

- Changing the grain of `slv_poi_amenity` or `gld_srv_poi_amenity`.
- Changing the amenities JSON API.
- A third `poi_id` formula beyond `uuid_md5(id, 'partner')` and `HASH_MD5_UUID(source_name, source_id)`.
- `notebooks_lgc/`.
- Task `20261116-srv-poi-info-is-active`.
- Running a Fabric notebook, copying credentials or hosts, or inferring row counts.
- Commit, push, or merge.

## Acceptance criteria

- `decision.md` states one cause, with file and cell.
- Code, `docs/context/mapping_gld_srv_poi_amenity.md`, and `tests/test_poi_amenity_contract.py` match the chosen fix.
- `python scripts/vv.py verify` passes. No Fabric notebook run belongs to this task.
- Reviewers: `sql-data-reviewer` and `spark-runtime-reviewer`. Add `state-correctness-reviewer` if the MERGE key or write order changes.

## Constraints

- One task. Do not stop after triage when the repository already shows the cause.
- Two different fixes: record both and do not choose.
- `data_model_change` and `run-author --kind model` only if the `poi_id` formula changes.
- Main model must be Grok 4.7 Medium unless an approved `exceptions` entry says otherwise.
- Samples at most 50 rows and no personal data.

## Classification rationale

- Complexity: medium. The id contract crosses `slv_poi_amenity`, `gld_srv_poi_amenity`, and `gld_srv_poi_info`. Two later repairs are possible, so this is not a fast lane.
- Risk: medium. A later repair changes which amenity rows stay live. Rollback is a RECOMPUTE rerun. No data-loss path is chosen in this phase.
- Architecture: required after evidence, because more than one repair has a material trade-off. Not run in this phase.
- Evidence: required. The repository shows the id spaces and does not show a formula mismatch or which population gap is present.
- Runtime proof: not required yet. A runbook is written only after a code change, and the Fabric DEV step stays with the user.
- Reviewer routing: `sql-data-reviewer` and `spark-runtime-reviewer` for the amenity build. `state-correctness-reviewer` stays off until a MERGE key or write order changes.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Không gian `poi_id` amenity và `gld_srv_poi_info` | `business_sector` lấy từ `slv_pn_business_services`, join `slv_pn_business_service_i18ns` qua `business_service_id = id` và `locale = 'vi'`. Khớp từ điển thì `amenity_group` lấy từ dòng từ điển; không khớp thì `specialty_tags`. Một nhãn khớp nhiều dòng từ điển partner thì dừng notebook, không ghi. | Lịch sử quyết định, D-12 | 2026-11-18 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 24811 bytes

## FILES

- architecture.md | 24811 bytes | large: use toc/show
- decision.md | 13803 bytes
- evidence/plan.md | 2991 bytes
- evidence/probes/amenity-poi-id-overlap.sql | 2202 bytes
- evidence/probes/amenity-poi-id-side.sql | 2037 bytes
- evidence/probes/partner-amenity-label-column.sql | 3814 bytes
- evidence/probes/partner-amenity-label-match.sql | 7084 bytes
- evidence/probes/partner-amentities-shape.sql | 3729 bytes
- evidence/probes/partner-dict-keys.sql | 1585 bytes
- evidence/probes/partner-entity-coverage.sql | 1459 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/amenity-poi-id-overlap.txt | 3188 bytes
- evidence/results/amenity-poi-id-side.txt | 392 bytes
- evidence/results/partner-amenity-label-column.txt | 1738 bytes
- evidence/results/partner-amenity-label-match-run1-error.txt | 129 bytes
- evidence/results/partner-amenity-label-match.txt | 3054 bytes
- evidence/results/partner-amentities-shape-run1-error.txt | 284 bytes
- evidence/results/partner-amentities-shape-run2-error.txt | 206 bytes
- evidence/results/partner-amentities-shape.txt | 1965 bytes
- evidence/results/partner-dict-keys-run1-error.txt | 258 bytes
- evidence/results/partner-dict-keys.txt | 386 bytes
- evidence/results/partner-entity-coverage.txt | 370 bytes
- handoffs/architect.md | 22221 bytes | large: use toc/show
- handoffs/author-input.md | 1759 bytes
- model-design.md | 12691 bytes
- model-design.new.md | 12691 bytes
- request.md | 3001 bytes
- resume.md | 838 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1621 bytes

## NEXT

python scripts/vv.py run-gate 20261118-amenity-poi-id-align

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SLV_POI_AMENITY.ipynb (21682 bytes)

[0] markdown id=d1amenmd json=47-56 lines=3 | NB_SLV_POI_AMENITY | defs: none
[1] code id=d1amenparam json=57-81 lines=8 | p_exec_id = "" | defs: none
[2] code id=d1amenrun json=82-91 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=d1amenmatch json=92-226 lines=126 | import re | defs: resolve_condition, is_legacy_form, match_conditions, legacy_blocks_write, match_coverage
[4] code id=d1amenbuild json=227-312 lines=77 | GOOGLE = "google" | defs: build
[5] code id=d1amenres json=313-322 lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=d1amenexit json=323-332 lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb (28277 bytes)

[0] markdown id=b1entitymd json=unknown lines=6 | NB_SLV_POI_ENTITY_NON_ENRICH | defs: none
[1] code id=b1entityparam json=unknown lines=8 | p_exec_id = "" | defs: none
[2] code id=b1entityrun json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=b1entityjson json=unknown lines=83 | import json | defs: _first_text, first_child_value, top_level_text
[4] code id=b1entitybuild json=unknown lines=224 | GOOGLE = "google" | defs: _live, _google, pick, _partner, build
[5] code id=b1entityres json=unknown lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=b1entityexit json=unknown lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_GLD_SRV_POI_INFO.ipynb (25102 bytes)

[0] markdown id=srvinfomd json=unknown lines=11 | NB_GLD_SRV_POI_INFO | defs: none
[1] code id=srvinfoparam json=unknown lines=8 | p_exec_id = "" | defs: none
[2] code id=srvinforun json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=srvinfohours json=unknown lines=99 | import json | defs: _int, _open, _closed, _all_day, _dump, google_hours, partner_hours, operating_hours
[4] code id=srvinfobuild json=unknown lines=182 | ENT_COLS = ("poi_id", "poi_name", "source_name", "business_sector", "business_ca | defs: _require, _destination, _rating, _reviews, _cover, build, _text_or_null
[5] code id=srvinfores json=unknown lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=srvinfoexit json=unknown lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_CREATE_DDL.ipynb (396228 bytes)

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
[30] markdown id=enrinfomd json=2119-2126 lines=1 | [THÊM 21/10] 20261021-refresh-gld-enr-poi-info | defs: none
[31] code id=enrinfopy json=2127-2353 lines=213 | import uuid | defs: _schema, _create
[32] markdown id=mvpoimd json=2354-2361 lines=1 | [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup | defs: none
[33] code id=mvpoipy json=2362-2595 lines=220 | import uuid | defs: _names, _n, _node_edges, _info_edges
[34] markdown id=enrflagmd json=2596-2603 lines=1 | [THÊM 22/10] 20261022-enr-landing-and-gld-flags | defs: none
[35] code id=enrflagpy json=2604-2870 lines=253 | import uuid | defs: _want, _schema, _create_sql, _missing_flags, _add_flags, _edge_rows
[36] markdown id=ohpassmd json=2871-2878 lines=1 | [THÊM 23/10] 20261023-entity-opening-hours-passthrough | defs: none
[37] code id=ohpasspy json=2879-3082 lines=190 | import uuid | defs: _rows, _active, _refresh_lock, _column
[38] markdown id=peholmd json=3083-3090 lines=1 | [THÊM 23/10] 20261023-entity-phone-email-holiday | defs: none
[39] code id=peholpy json=3091-3154 lines=50 | ENTITY_FQ = "lh_vv_silver.dbo.slv_poi_entity_non_enrich" | defs: _fields, _issues
[40] markdown id=srvpoimd json=3155-3166 lines=5 | [THÊM 24/10] 20261024-gld-srv-poi-from-mapping | defs: none
[41] code id=srvpoipy json=3167-3385 lines=205 | import uuid | defs: _want, _schema, _create_sql, _edge_rows, _refresh_lock
[42] markdown id=srvratemd json=3386-3397 lines=5 | [THÊM 26/10] 20261025-gld-srv-poi-info-rating-review | defs: none
[43] code id=srvratepy json=3398-3578 lines=167 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[44] markdown id=mediaddlmd json=3579-3588 lines=3 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[45] code id=mediaddlpy json=3589-3788 lines=186 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[46] markdown id=amenddlmd json=3789-3800 lines=5 | [THÊM 26/10] 20261025-poi-media-and-srv-amenity | defs: none
[47] code id=amenddlpy json=3801-3992 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock, _create_sql
[48] markdown id=plcadmd json=3993-4003 lines=4 | [THÊM 26/10] 20261026-pl-name-cadence-suffix | defs: none
[49] code id=plcadpy json=4004-4257 lines=240 | import uuid | defs: _n, _lock_rows, _refresh_lock, _issues
[50] markdown id=mlexpmd json=4258-4266 lines=2 | [THÊM 26/10] 20261026-add-poi-multi-lang-experience | defs: none
[51] code id=mlexppy json=4267-4418 lines=138 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[52] markdown id=srvrevmd json=4419-4428 lines=3 | [THÊM 27/10] 20261026-gld-srv-poi-review | defs: none
[53] code id=srvrevpy json=4429-4637 lines=195 | import uuid | defs: _want, _schema, _edge_rows, _create_sql, _refresh_lock
[54] markdown id=rvi18nenrmd json=4638-4647 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (1/2) | defs: none
[55] code id=rvi18nenrpy json=4648-4810 lines=149 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[56] markdown id=rvi18ngldmd json=4811-4820 lines=3 | [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (2/2) | defs: none
[57] code id=rvi18ngldpy json=4821-4973 lines=139 | import uuid | defs: _want, _schema, _edges, _refresh_lock
[58] markdown id=mlsrcmd json=4974-4983 lines=3 | [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr | defs: none
[59] code id=mlsrcpy json=4984-5102 lines=105 | import uuid | defs: _want, _schema, _refresh_lock
[60] markdown id=cmscfgmd json=5103-5112 lines=3 | [THÊM 08/11] 20261104-extract-cms-raw-data | defs: none
[61] code id=cmscfgpy json=5113-5222 lines=96 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _cms_ts, _cms
[62] markdown id=srvcovermd json=5223-5233 lines=4 | [THÊM 08/11] 20261108-gld-srv-poi-info-cover | defs: none
[63] code id=srvcoverpy json=5234-5425 lines=178 | import uuid | defs: _want, _schema, _edge_rows, _refresh_lock
[64] markdown id=poidestmd json=5426-5436 lines=4 | [THÊM 12/11] 20261112-poi-destination-name-api | defs: none
[65] code id=poidestpy json=5437-5602 lines=152 | import uuid | defs: _want, _schema, _accepted, _anchor, _refresh_lock
[66] markdown id=enrmergemd json=5603-5610 lines=1 | [THÊM 12/11] 20261112-enr-poi-append-to-merge | defs: none
[67] code id=enrmergepy json=5611-5787 lines=163 | import uuid | defs: _release_lock, _refresh_lock, _types, _modes, _run
[68] markdown id=srvactivemd json=5788-5798 lines=4 | [THÊM 16/11] 20261116-srv-poi-info-is-active | defs: none
[69] code id=srvactivepy json=5799-5926 lines=114 | import uuid | defs: _want, _schema, _refresh_lock
[70] markdown id=enrbrzcfgmd json=5927-5938 lines=5 | B3 — cell `enrbrzcfgpy` | defs: none
[71] code id=enrbrzcfgpy json=5939-5953 lines=96 | def _enr(path, typ="string", rule=None): | defs: _enr
[72] markdown id=enrbrzmd json=5954-5965 lines=5 | B2 — cell `enrbrzpy` | defs: none
[73] code id=enrbrzpy json=5966-5980 lines=269 | def plan_rewrite(current, target, renames, drops): | defs: plan_rewrite, should_auto_restore, _touch_locks, _head, _fence, _confirm_skip, rewrite_table, _norm, _take
[74] markdown id=enrgldmd json=5981-5992 lines=5 | B5 — cell `enrgldpy` | defs: none
[75] code id=enrgldpy json=5993-6007 lines=257 | def plan_rewrite(current, target, renames, drops): | defs: plan_rewrite, should_auto_restore, _touch_locks, _head, _fence, _confirm_skip, rewrite_table, _norm
