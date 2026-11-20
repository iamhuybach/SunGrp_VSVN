# Architect handoff: 20261119-legacy-gold-poi-init

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261119-legacy-gold-poi-init --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261119-legacy-gold-poi-init/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261119-legacy-gold-poi-init | phase=triage

## STATE

id: 20261119-legacy-gold-poi-init
title: One-time legacy gold POI init and poi_id map
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: data_model_change, idempotency, cross_state_impact, design_tradeoffs, data_evidence_required, runtime_proof_required, low_probability_high_impact
gates: evidence=evidence_required, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_CREATE_DDL.ipynb
- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb
- notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb

## VALIDATION

PASS

## RESUME

# Resume

## Status

waiting_evidence. Task `20261119-legacy-gold-poi-init`. D-06 takes `poi_name` and `district` from `lang = vi`. Architecture round 2 is unused.

## Done this session

Recorded D-06. P1, P4, P5, and P7 are saved. P2 still has no counts. The probe no longer calls `uuid_format`.

## Next action

Re-run `evidence/probes/legacy_key_overlap.sql`. Paste the two count tables into `evidence/results/legacy_key_overlap.txt`. Then the Architect can run round 2.

## Read next

`decision.md` row D-06. Probe `evidence/probes/legacy_key_overlap.sql`.

## Waiting on

P2 overlap counts.

## REQUEST

# Request

## User outcome

Một bảng map ở `lh_vv_gold`, tiền tố `gld_`, grain một dòng cho mỗi `poi_id` của gold model cũ. `poi_id` model mới trên bảng đó được tính lại theo rule model mới từ `source_id` / id nguồn mà notebook luồng cũ đang dùng. Không inner-join với dòng gold mới. Gold cũ có `poi_id` mà gold mới chưa có dòng vẫn phải ra `poi_id` model mới.

Một lần init toàn bộ dữ liệu gold model cũ sang gold model mới. `poi_id` google và partner trên dữ liệu init được tính lại, không chứa lang, không dùng `poi_uid`. Chạy init lần hai không nhân đôi dòng và không đổi `poi_id` google hoặc partner mà pipeline mới đã tính đúng.

## Scope

### In scope

- Bảng map gold, khóa là `poi_id` model cũ.
- Init một lần từ các bảng gold mà `notebooks_lgc/3rd_data_ingested_orches/` và `notebooks_lgc/pl_transform_partner_userprofile_cms/` ghi, sang các bảng gold model mới đã có.
- DDL/registry, lib transform/gold, và một notebook init nếu kiến trúc buộc.
- Ngoại lệ có thời hạn: chỉ notebook init được đọc gold cũ để ghi gold mới. Không phải đường đọc của pipeline định kỳ.

### Out of scope

- Sửa pipeline định kỳ hoặc gắn lịch 15 phút.
- Chạy init trên Fabric trong chat này.
- Serving API khi tập cột và khóa gold không đổi.
- Tạo bảng nghiệp vụ mới để chứa phần dữ liệu POI cũ không có bảng gold mới.
- Đoán lại công thức `poi_id` cũ. `ref_poi_legacy_id` chỉ là bằng chứng thu hoạch, không thay bảng map.

## Acceptance criteria

- Grain map: một dòng mỗi `poi_id` model cũ. Khóa không phải `poi_id` mới.
- Cùng `source_id` google, các `poi_id` cũ khác lang cho một `poi_id` mới: `uuid_format(md5(concat('google', source_id)))` (`HASH_MD5_UUID`).
- Cùng id partner, các `poi_id` cũ khác lang cho một `poi_id` mới: `uuid_format(md5(concat(id, 'partner')))` (`uuid_md5(id, lit('partner'))`). `id` là id nghiệp vụ notebook cũ dùng, đối chiếu `slv_pn_business_services.id`. Không hash cụm `partner_portal`.
- Thiếu `source_id` hoặc id nguồn thì không suy ra `poi_id`. Ghi `MISSING_EVIDENCE`.
- `ingestion_source` model cũ là `source_name` model mới. `partner_portal` thành `partner`. Giá trị khác `google` và `partner_portal` không tự đặt `source_name`.
- Field JSON, array và kiểu gộp của bảng cũ ra đúng kiểu field của bảng mới.
- Cột không có cặp trong notebook cũ hoặc DDL model mới thì không điền.
- Init một lần. Lần hai không nhân đôi dòng và không đổi `poi_id` google/partner mà pipeline mới đã tính đúng.
- Architect ghi rollback, thứ tự ghi, và cách init không ghi đè dòng pipeline mới đang sở hữu hoặc không bị pipeline đó ghi đè ngay sau init. Không tách được hai writer thì dừng `user_decision` trước khi sửa code.

## Constraints

- Người dùng đã chốt bảng map nằm ở gold và init một lần từ gold cũ sang gold mới.
- Danh sách bảng ở mục 2.1 không đủ. Kiểm kê mọi bảng gold hai thư mục notebook ghi.
- Bảng watermark và bảng kỹ thuật không phải dữ liệu POI: liệt kê, không copy.
- Bảng POI cũ không có bảng gold mới tương ứng: liệt kê và dừng `user_decision`. Không tạo bảng nghiệp vụ mới.
- `ref_source` trong tài liệu còn `partner_portal`. Trên dữ liệu init, `source_name` ghi `partner`.
- Không đọc `docs/context/3p-google/*.txt`, manifest pipeline, hay artifact task khác.
- Model cũ nằm ở workspace `sgr_visitvn_prd_batch`. Model mới nằm ở workspace `sgr_visitvn_dev`. Cùng tenant, cả hai có quyền đọc và viết. Script kiểm tra và init dùng tên đủ `workspace.lakehouse.schema.table`. Không dùng tên tắt lakehouse.
- Không fast lane. Không commit trong lượt này.

## Classification rationale

- Complexity: high. Đổi grain và khóa, gộp nhiều `poi_id` cũ vào một `poi_id` mới, init có thứ tự ghi và rollback.
- Risk: high. Ghi gold một lần, idempotency, và khả năng đụng writer của pipeline mới. Sau review bắt buộc risk-gate.
- Architecture: required. Đổi grain/khóa, ngoại lệ gold đọc gold, nhiều cách tách writer.
- Evidence: required. Số lang trên một thực thể, giá trị `ingestion_source`, chỗ `source_id` có dữ liệu, và gold cũ còn dòng hay không không chứng minh được từ repo.
- Runtime proof: required. Init không chạy trên Fabric trong chat này. Khi cần chạy, runbook rồi `waiting_runtime`.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`. `fabric-pipeline-reviewer` chỉ khi sửa pipeline JSON. Risk high nên có `risk-gate` sau specialist review.
- Signals: `data_model_change`, `idempotency`, `cross_state_impact`, `design_tradeoffs`, `data_evidence_required`, `runtime_proof_required`, `low_probability_high_impact`.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Chỗ đặt bảng map và init một lần | Bảng map ở `lh_vv_gold`, tiền tố `gld_`, một dòng mỗi `poi_id` cũ. Init một lần từ gold cũ sang gold mới. Chỉ notebook init được đọc gold khác. Pipeline định kỳ không đọc đường này. | request.md User outcome | 2026-11-19 |
| D-02 | Bảng POI cũ không có gold mới | Chỉ điền cột đã có cặp với bảng `gld_srv_*` hiện có. Cột không có cặp không điền. Không tạo bảng nghiệp vụ mới. Áp cho `ai_poi`, `ai_poi_rating`, `ai_poi_review`, `ai_enriched_poi`, `poi_enrichment_display`, `poi_address_enrichment_staging`, `poi_rating`. | Người dùng, 2026-11-19 | 2026-11-19 |
| D-03 | Hai workspace | Model cũ đọc và ghi ở workspace `sgr_visitvn_prd_batch`. Model mới đọc và ghi ở workspace `sgr_visitvn_dev`. Cùng tenant, cả hai đều có quyền đọc và viết. Mọi script kiểm tra dùng tên đủ `workspace.lakehouse.schema.table`. Lakehouse vẫn là `lh_vv_gold` và `lh_vv_silver`, schema `dbo`. | Người dùng, 2026-11-19 | 2026-11-19 |
| D-04 | Hai writer trên `gld_srv_*` | Phương án B. Thêm cột kỹ thuật `load_origin` STRING trên `gld_srv_poi_info`, `gld_srv_poi_multi_lang`, `gld_srv_poi_review`. Init ghi `LEGACY_INIT`. Lib chỉ xóa mềm dòng `load_origin` NULL. Lần MATCHED đầu của pipeline đặt `load_origin` về NULL. Dòng pipeline không sinh ra thì giữ đến khi pipeline sinh đúng khóa. Không có đợt xóa riêng. | Người dùng, 2026-11-19 | 2026-11-19 |
| D-05 | Tên map và notebook init | Bảng map `lh_vv_gold.dbo.gld_poi_legacy_id_map`. Notebook một lần `NB_SETUP_LEGACY_GOLD_POI`. Không gắn pipeline 15 phút. | model-design.md sau D-04 | 2026-11-19 |
| D-06 | `poi_name` và `district` nhiều lang | Lấy hai cột từ dòng `poi_master` có `lang = vi` của cùng `source_id`. Không chọn lang khác. Không có dòng `vi` thì hai cột NULL, vẫn ghi dòng info khi các cột đã cặp còn lại không khác nhau giữa các lang. | Người dùng, 2026-11-19 | 2026-11-19 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 27819 bytes

## FILES

- architecture.md | 27819 bytes | large: use toc/show
- decision.md | 5066 bytes
- evidence/plan.md | 5904 bytes
- evidence/probes/cross_ws_time_travel.sql | 441 bytes
- evidence/probes/gld_srv_owner_pl.sql | 752 bytes
- evidence/probes/legacy_gold_poi_profile.sql | 3858 bytes
- evidence/probes/legacy_gold_types.sql | 1407 bytes
- evidence/probes/legacy_key_overlap.sql | 2296 bytes
- evidence/probes/legacy_lang_payload_diff.sql | 3499 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/cross_ws_time_travel.txt | 184 bytes
- evidence/results/gld_srv_owner_pl.txt | 704 bytes
- evidence/results/legacy_gold_poi_profile.txt | 1196 bytes
- evidence/results/legacy_gold_types.txt | 787 bytes
- evidence/results/legacy_key_overlap.txt | 383 bytes
- evidence/results/legacy_lang_payload_diff.txt | 425 bytes
- handoffs/architect.md | 22864 bytes | large: use toc/show
- handoffs/author-input.md | 1742 bytes
- model-design.md | 17435 bytes
- request.md | 5242 bytes
- resume.md | 617 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1563 bytes

## NEXT

python scripts/vv.py run-gate 20261119-legacy-gold-poi-init

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

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

### notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb (126141 bytes)

[0] markdown id=026c3072 json=3-56 lines=47 | NB_LIB_TRANSFORM_SLV_GLD — Thư viện dùng chung cho luồng silver → silver L2 → go | defs: none
[1] code id=9ff87eee json=57-142 lines=72 | import json | defs: none
[2] markdown id=bf3d6ad5 json=143-150 lines=1 | 2. common — thời gian, tham số, log, retry, tên bảng, append | defs: none
[3] code id=649c6944 json=151-302 lines=138 | _LOG_LOCK = threading.Lock() | defs: ConfigError, QualityGateError, utc_now, to_bool, split_csv, short_error, log, is_transient, with_retry, is_identifier, is_fq_name, quote_name, table_exists, table_columns, append_rows, json_dumps, current_notebook_name, cadence_minutes, edge_wm_id, flow_lock_id, require_ctrl_columns
[4] markdown id=10ad924b json=303-318 lines=9 | 3. delta — trạng thái bảng, history, commit đổi dữ liệu, đọc theo version | defs: none
[5] code id=5217686f json=319-423 lines=91 | def table_state(fq: str) -> Optional[dict]: | defs: table_state, table_history, is_data_change, HistoryCache, __init__, changes, read_at, read_current
[6] markdown id=4accd2b3 json=424-437 lines=7 | 4. config / DAG | defs: none
[7] code id=b3673b19 json=438-630 lines=179 | @dataclass(frozen=True) | defs: Edge, src_fq, trg_fq, wm_id, Dag, descendants, node_by_name, load_config_rows, node_owner, build_dag
[8] markdown id=176b794b json=631-647 lines=10 | 5. ctrl — hộp thư cạnh, khoá luồng, run log, table log | defs: none
[9] code id=5cd650fc json=648-931 lines=270 | WM_EDGE_SCHEMA = T.StructType([ | defs: load_edge_wm, edge_status, sql_merge_edge_wm, merge_edge_wm, sql_ensure_lock_row, ensure_lock_row, _lock_expired_sql, read_flow_lock, _update_lock_row, acquire_flow_lock, release_flow_lock, refresh_flow_lock, close_stale_runs, write_run_log, update_run_log, write_node_log, node_logs, last_output_versions
[10] markdown id=191e1851 json=932-960 lines=22 | 6. node — `NodeSpec`, `NodeContext`, QG, MERGE row_hash, `run_node` | defs: none
[11] code id=926a3f9c json=961-1665 lines=691 | @dataclass | defs: NodeSpec, NodeContext, __init__, input, is_empty, current_target, warn, _input_at, changed, _hash_expr, add_row_hash, quality_gate, diff_counts, target_ddl, ensure_target, sql_merge_target, merge_target, _resolve_node, choose_append_baseline, append_history_stops, parse_append_marker, _version_unavailable, _align_snapshot, find_append_marker, check_append_schema, _reject_append_build, append_target, _once, execute_append, run_node, finish_node
[12] markdown id=3650f3b1 json=1666-1685 lines=13 | 7. orchestrator — `plan_run`, DAG runMultiple, gom kết quả, tiến cạnh, `orchestr | defs: none
[13] code id=294534d1 json=1686-1969 lines=270 | @dataclass | defs: Plan, plan_run, plan_summary, print_plan, build_run_multiple_dag, collect_outcomes, advance_edges, _validate_orch_params, orchestrate
[14] markdown id=46eb3baf json=1970-1989 lines=13 | 8. build helpers — chuẩn hoá chữ, bỏ dấu, slug, uuid md5, epoch, JSON | defs: none
[15] code id=4938ec32 json=1990-2099 lines=96 | TOAST_SENTINEL = "__debezium_unavailable_value" | defs: _build_unaccent_map, clean_str, norm_text, norm_admin, unaccent, slugify, uuid_md5, epoch_to_ts, json_scalar, json_array_at, json_sorted_array, iso_utc_ts
