# Architect handoff: 20261119-gsm-as-google-extract

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261119-gsm-as-google-extract --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261119-gsm-as-google-extract/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261119-gsm-as-google-extract | phase=triage

## STATE

id: 20261119-gsm-as-google-extract
title: Extract sgm through the current Google 3P path
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: stateful_logic, event_ordering, idempotency, design_tradeoffs, cross_state_impact, runtime_proof_required, data_evidence_required, data_model_change
gates: evidence=pass, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: state-correctness-reviewer, spark-runtime-reviewer, sql-data-reviewer, fabric-pipeline-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb
- notebooks/NB_CREATE_DDL.ipynb
- pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json
- notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb
- notebooks/NB_SLV_POI_AMENITY.ipynb
- notebooks/NB_SLV_POI_MEDIA_INFO.ipynb
- notebooks/NB_ENR_POI_INFO.ipynb
- notebooks/NB_GLD_SRV_POI_INFO.ipynb
- docs/context/mapping_gld_srv_poi_amenity.md
- docs/context/mapping_gld_srv_poi_info.md
- docs/context/mapping_gld_srv_poi_multi_lang.md
- docs/context/mapping_poi_media_info.md
- docs/context/mapping_gld_srv_poi_review.md

## VALIDATION

PASS

## RESUME

# Resume 20261119-gsm-as-google-extract

Status: user_decision. Owner: user. Gates: evidence=pass, architecture=evidence_required.

Done this session:
- Saved evidence/results/p2_sgm_overlap_detail.txt.
- NAME is exactly google and sgm. overlap_exact=overlap_trimmed=402. silver_hit=402.
- All 402 overlaps are sgm_newer. sgm_only=2228. match_exact=93 of 2041 reviews. photo match_name=0, scraper_named=2814.
- No notebook edit.

Next action: record D-4 and D-5, then run-author --kind model and run-gate.
- D-4 A: keep bronze sgm in review_id and media_dedup_key. Leftover rows after a later google takeover are accepted.
- D-4 B: hash those two keys with google for sgm events. 93 exact reviews would converge. Photos with scraper names would not.
- D-5 accept: an older or equal google event stays stale and the stored sgm row remains until a newer google crawl.
- D-5 override: an older google event still overwrites the sgm row.

Read next: architecture.md ## Decision D-4 options; ## Ordering D-5; evidence/results/p2_sgm_overlap_detail.txt.

Waiting on: user choice of D-4 A or B, and D-5 accept or override.

## REQUEST

# Request

## User outcome

Bronze rows with `source_name = 'sgm'` on `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` enter the existing Google third-party extract. `slv_3p_poi.source_name` stays `sgm` or `google` as stored on bronze. Every consumer after `slv_3p_poi` treats a `sgm` row as effective `source_name` `google`, with `poi_id = HASH_MD5_UUID('google', source_id)`. Existing `google` rows keep their `source_name` and `poi_id`.

## Scope

### In scope

- `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` and the existing Google registry and pipeline parameter that selects `sources`. No new extract notebook and no new pipeline.
- Active `DOC` / `DOC_ARRAY` tables `slv_3p_poi_*` only. Do not reactivate a disabled table.
- Consumers after `slv_3p_poi` that filter or write `source_name = 'google'`, including the place-type and amenity dictionaries. No new `source_name = 'sgm'` dictionary rows.
- Mapping docs whose table behavior changes, before review.

### Out of scope

- A separate gold or serving task.
- Java serving API changes unless the gold column set or key changes. A different `source_name` value on gold is not an API change.
- New `json_path` entries for keys that are not already in the Google registry contract.
- `NB_LIB_*` changes unless the extract notebook cannot express the identity rule.

## Acceptance criteria

- `source_name = 'sgm'` is not classified `IGNORED` / `OUT_OF_SCOPE`. The current `sources` default and the pipeline parameter are `google` only.
- Same active `DOC` / `DOC_ARRAY` contract and the same active `slv_3p_poi_*` tables.
- `slv_3p_poi.source_name = 'sgm'` when bronze `source_name` is `sgm`.
- Tables and logic after `slv_3p_poi` see that row as effective `source_name` `google`, including dictionaries that filter `source_name = 'google'`.
- MERGE, watermark, reject, and `crawled_at` ordering keep current semantics. A rerun does not insert a second row.
- A registry key that is JSON null on the supplied `sgm` document is not treated as a missing field. A key that is not in the registry contract does not receive a `json_path`.
- The serving API changes only when the gold column set or key changes.

## Constraints

- `sgm` and `google` are the same business source. Keep one notebook, one registry, and one pipeline.
- Identity is fixed: `slv_3p_poi` stores the bronze `source_name`. Downstream of `slv_3p_poi`, a `sgm` row uses effective `source_name` `google` and the same `poi_id` as `google` for the same `source_id`: `HASH_MD5_UUID('google', source_id)`. Do not create a second `poi_id` from `'sgm'`.
- If that identity hits grain, a MERGE key, or a duplicate count, stop at `user_decision` and name the exact collision before any code change.
- Do not assume `normalized_payload.id` is bronze `source_id`. The extract contract is the bronze columns `source_name` and `source_id` (`RAW_DOC_ID`).
- The supplied document is one shape sample, not a distribution. Record keys and JSON types only.
- No fast lane.

## Classification rationale

- Complexity: high. Signals: `stateful_logic`, `idempotency`, `event_ordering`, `data_evidence_required`, `data_model_change`, `cross_state_impact`, `design_tradeoffs`, `runtime_proof_required`. The `poi_id` hash input for `sgm` changes, and watermark, state, and MERGE stay in the same notebook.
- Risk: high. A shared `poi_id` can update an existing `google` row, including `source_name`, when the same `source_id` exists on both bronze values.
- Architecture: required. The key input changes, and the effective `source_name` is applied after `slv_3p_poi` across entity, dictionary, enrich, and gold filters. The repository pipeline activity passes `sources` = `google`, so the existing pipeline JSON must change with the notebook default.
- Evidence: required. Overlap of `source_id` between `sgm` and `google`, equality of `normalized_payload.id` and bronze `source_id`, and absent versus JSON-null registry keys are not in the repository. One sample does not answer them.
- Runtime proof: required. MERGE, watermark, and rerun behavior of this extract are proven on Fabric DEV, not by the local verifier alone.
- Reviewer routing: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`, `fabric-pipeline-reviewer`. Risk gate after specialist review because risk is high. No API reviewers unless the gold column set or key changes.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Danh tính sgm | `slv_3p_poi` lưu `source_name` bronze (`sgm` hoặc `google`). Phía sau `slv_3p_poi`, dòng `sgm` dùng `source_name` hiệu lực `google` và `poi_id = HASH_MD5_UUID('google', source_id)`. Không tạo `poi_id` thứ hai từ `sgm`. | request.md Constraints | 2026-11-19 |
| D-2 | Chỗ đụng khóa MERGE | Probe `p1_sgm_source_id`: `bronze_sgm=2630`, `overlap_source_id=402`, `id_eq_source_id=2630`. 402 `source_id` có cả `sgm` và `google`. D-1 đặt `poi_id = HASH_MD5_UUID('google', source_id)`, trùng khóa MERGE `poi_id`. Cách xử lý 402 khóa là D-3. Công thức `review_id` và `media_dedup_key` của event `sgm` là D-4. | evidence/results/p1_sgm_source_id.txt | 2026-11-19 |
| D-3 | Ưu tiên google | Ưu tiên `source_name` là `google`. Event `sgm` mới hơn dòng đã có `source_name=google` thì không MERGE. Event `google` mới hơn dòng `sgm` thì ghi `google` và `source_name=google`. Dòng chỉ có `sgm` vẫn lưu `source_name=sgm`, `poi_id=HASH_MD5_UUID('google', source_id)`. | Quyết định của người dùng | 2026-11-19 |
| D-4 | Hash review và ảnh | Phương án B. Event `sgm`: `review_id` và `media_dedup_key` hash `source_name` hiệu lực `google`, không hash bronze `sgm`. `poi_id` vẫn theo D-1. Dòng `google` không đổi công thức khóa. Ảnh tên `scraper-` không trùng tên `google` vẫn là dòng riêng. | Quyết định của người dùng | 2026-11-19 |
| D-5 | Google cũ hơn vẫn ghi đè | Override đề xuất giữ thứ tự `crawled_at` trong `architecture.md` mục Ordering. Event `google` có `crawled_at` cũ hơn dòng `sgm` đã lưu vẫn MERGE, `source_name=google`. | Quyết định của người dùng | 2026-11-19 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 34367 bytes

## FILES

- architecture.md | 34367 bytes | large: use toc/show
- decision.md | 4936 bytes
- evidence/payload-shape.md | 6184 bytes
- evidence/plan.md | 3430 bytes
- evidence/probes/__pycache__/p2_sgm_overlap_detail.cpython-314.pyc | 10519 bytes
- evidence/probes/p1_sgm_source_id.py | 4734 bytes
- evidence/probes/p2_sgm_overlap_detail.py | 5890 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/p1_gsm_source_id.txt | 245 bytes
- evidence/results/p1_sgm_source_id.txt | 2399 bytes
- evidence/results/p2_sgm_overlap_detail.txt | 297 bytes
- handoffs/architect.md | 27449 bytes | large: use toc/show
- handoffs/author-input.md | 1633 bytes
- model-design.md | 9952 bytes
- model-design.pre-d4.md | 14954 bytes
- model-design.void-gsm.md | 14371 bytes
- request.md | 4407 bytes
- resume.md | 1135 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 2163 bytes

## NEXT

python scripts/vv.py run-gate 20261119-gsm-as-google-extract

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb (74532 bytes)

[0] markdown id=e2a3d4ba json=unknown lines=31 | NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV | defs: none
[1] code id=e3eb64e4 json=unknown lines=19 | pl_name                 = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"   # @pipeline | defs: none
[2] code id=9a6e8ee5 json=unknown lines=1 | %run NB_LIB_EXTRACT_RAWDATA | defs: none
[3] markdown id=26225682 json=unknown lines=13 | Hằng số nguồn `brz_3rd_crawler_poi_stream` | defs: none
[4] code id=1ccbf8fd json=unknown lines=20 | import uuid | defs: none
[5] markdown id=266a7442 json=unknown lines=24 | A. Đọc raw, phân loại và dựng tài liệu | defs: none
[6] code id=803f3d1d json=unknown lines=242 | def path_value(parsed: Column, path: str) -> Column: | defs: path_value, block_col, doc_value, spec_paths, is_scoped, top_fields, doc_columns, read_raw, classify_docs, blank, presence, bad_shape, profile_docs, reject_frame, doc_source_payload, doc_reject_rows
[7] markdown id=0e22c079 json=unknown lines=25 | B. Xử lý 1 bảng: tách dòng → chuyển kiểu, khoá → lọc theo state → bản mới nhất → | defs: none
[8] code id=65ab1f40 json=unknown lines=303 | def expand_rows(spec: TableSpec, docs: DataFrame) -> DataFrame: | defs: expand_rows, part_value, build_table_rows, typed, table_stats, as_int, resolve_latest, build_merge_sql, merge_into_target, doc_state_latest, element_reject_rows, _run_table, process_table
[9] markdown id=75a0b860 json=unknown lines=5 | C. Commit | defs: none
[10] code id=029cb77f json=unknown lines=12 | def commit(classified: DataFrame, profile: Profile, results: list, ctx: RunConte | defs: commit
[11] markdown id=0ddb2d5b json=unknown lines=5 | Main | defs: none
[12] code id=84cc99f5 json=unknown lines=112 | def build_context() -> RunContext: | defs: build_context, check_config, process_run, run_extract
[13] code id=f33f88d2 json=unknown lines=8 | _summary_json = json.dumps(RUN_SUMMARY, ensure_ascii=False, default=str) | defs: none
[14] markdown id=ed47805a json=unknown lines=55 | Vận hành | defs: none

### notebooks/NB_CREATE_DDL.ipynb (405318 bytes)

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

### notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb (28277 bytes)

[0] markdown id=b1entitymd json=unknown lines=6 | NB_SLV_POI_ENTITY_NON_ENRICH | defs: none
[1] code id=b1entityparam json=unknown lines=8 | p_exec_id = "" | defs: none
[2] code id=b1entityrun json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=b1entityjson json=unknown lines=83 | import json | defs: _first_text, first_child_value, top_level_text
[4] code id=b1entitybuild json=unknown lines=224 | GOOGLE = "google" | defs: _live, _google, pick, _partner, build
[5] code id=b1entityres json=unknown lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=b1entityexit json=unknown lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_SLV_POI_AMENITY.ipynb (28533 bytes)

[0] markdown id=d1amenmd json=47-57 lines=4 | NB_SLV_POI_AMENITY | defs: none
[1] code id=d1amenparam json=58-82 lines=8 | p_exec_id = "" | defs: none
[2] code id=d1amenrun json=83-92 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=d1amenmatch json=93-241 lines=140 | import re | defs: resolve_condition, is_legacy_form, match_conditions, legacy_blocks_write, match_coverage, partner_multi_match
[4] code id=d1amenbuild json=242-395 lines=145 | GOOGLE = "google" | defs: _live, _partner_rows, build
[5] code id=d1amenres json=396-405 lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=d1amenexit json=406-415 lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none

### notebooks/NB_GLD_SRV_POI_INFO.ipynb (25102 bytes)

[0] markdown id=srvinfomd json=unknown lines=11 | NB_GLD_SRV_POI_INFO | defs: none
[1] code id=srvinfoparam json=unknown lines=8 | p_exec_id = "" | defs: none
[2] code id=srvinforun json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=srvinfohours json=unknown lines=99 | import json | defs: _int, _open, _closed, _all_day, _dump, google_hours, partner_hours, operating_hours
[4] code id=srvinfobuild json=unknown lines=182 | ENT_COLS = ("poi_id", "poi_name", "source_name", "business_sector", "business_ca | defs: _require, _destination, _rating, _reviews, _cover, build, _text_or_null
[5] code id=srvinfores json=unknown lines=1 | RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_n | defs: none
[6] code id=srvinfoexit json=unknown lines=1 | notebookutils.notebook.exit(finish_node(RES)) | defs: none
