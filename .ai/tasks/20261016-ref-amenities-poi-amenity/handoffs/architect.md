# Architect handoff: 20261016-ref-amenities-poi-amenity

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261016-ref-amenities-poi-amenity/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261016-ref-amenities-poi-amenity | phase=triage

## STATE

id: 20261016-ref-amenities-poi-amenity
title: Dictionary amenities and slv_poi_amenity
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=False
signals: design_tradeoffs, idempotency, transaction_boundaries
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_CREATE_DDL.ipynb

## VALIDATION

PASS

## RESUME

# Resume

- Status: user_decision
- Done this session: Explained that putting `amenity_raw` in the key leaves `amenity` and `amenity_vi` as the values. `amenity_raw` is the condition string. Matching rows only. No boolean column. Q3 is still open.
- Next action: Wait for Q3 in `decision.md` (`Quyết định của người dùng`). After A, B, or C, transition to `waiting_architecture` and run `python scripts/vv.py run-gate 20261016-ref-amenities-poi-amenity`.
- Read next: `.ai/tasks/20261016-ref-amenities-poi-amenity/decision.md` section `Quyết định của người dùng`
- Waiting on: user decision Q3

## REQUEST

# Request

## User outcome

`lh_vv_silver.dbo.ref_dictionary_amenities` exists and is seeded from `docs/context/3p-google/mapping_amenities.md`. `lh_vv_silver.dbo.slv_poi_amenity` is a key-value table of the amenities that match `slv_3p_poi_amenity.source_flags_json`. The operator wrote the schema as `slv.`; the silver schema in this repo is `lh_vv_silver.dbo`.

## Scope

### In scope

- DDL for `lh_vv_silver.dbo.ref_dictionary_amenities` with exactly these columns: `source_name` string, `business_sector` string, `amenity_group` string, `amenity_raw` string, `amenity` string, `amenity_vi` string, `is_active` boolean, `updated_at` timestamp. No `business_category` column.
- Seed that dictionary from `docs/context/3p-google/mapping_amenities.md`.
- DDL for `lh_vv_silver.dbo.slv_poi_amenity`. Key is (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). Values are `amenity` and `amenity_vi`. No boolean column and no `business_category` column. Q3 in `decision.md`.
- Rows in `slv_poi_amenity` come from `slv_3p_poi_amenity.source_flags_json`, matched to dictionary rows with `source_name = google`.
- Read `business_sector` from `lh_vv_silver.dbo.slv_poi_entity` by joining on `poi_id`. The dictionary match also requires `business_sector`. This task does not create or change `slv_poi_entity`.

### Out of scope

- Adding `business_category` to either table.
- Renaming `f_n_b`. Q2 corrected only `accomodation` to `accommodation`.
- Creating or changing `lh_vv_silver.dbo.slv_poi_entity`. Another flow owns that table.
- Putting `amenity` into the `slv_poi_amenity` key. Q3 adds only `amenity_raw`.
- Inferring `source_flags_json` from `amenity_schema_json` or `ext_attributes_json`.
- Storing the operator's sample JSON in the repo.
- A commit from Main.

## Acceptance criteria

- `parkingOptions.freeStreetParking = true` is one `source_name = google` dictionary row. `Không có field riêng` produces no dictionary row.
- A `source_flags_json` value with `freeStreetParking: true` produces the matching `slv_poi_amenity` row. `freeParkingLot: false` does not produce the row for a `= true` condition.
- `evChargeOptions: null` produces no row.
- Neither table has a `business_category` column.
- An unmatched flag is skipped. No `other` row is created.

## Constraints

- Seed `business_sector` as `accommodation` for header `accomodation` (Q2). Keep `f_n_b`, `attraction`, and `shopping_n_retail` as written in the headers.
- `slv_poi_amenity.business_sector` comes from `lh_vv_silver.dbo.slv_poi_entity` joined on `poi_id` (Q1). The dictionary join includes `business_sector`.
- A bold table label (`general_amenities`, `accessibility`, `specialty_tags`, `space_and_services`, `facilities_and_services`) is the `amenity_group` for following rows until the next bold label. In section 2.3 the label `facilities_and_services` is repeated and stays one group.
- Partner Portal Enum emits `source_name = partner` and `amenity_raw` = that enum. The real Google column header is `Google Place API Field / Value`, not Place Type. That column emits `source_name = google` and `amenity_raw` = the Google expression.
- Do not emit a row for the values `Bổ sung sau`, `Fallback`, `Không có field`, `Không có field riêng`, or an empty Google cell. Drop only that value. Keep the other value on the same row.
- A Google cell with several conditions joined by `hoặc` becomes several `google` rows with the same `amenity` and `amenity_vi`.
- Hiển thị (VI) maps to `amenity_vi`. Hiển thị (EN) maps to `amenity`.
- `is_active = true`. `updated_at` is the seed write time.
- `amenity_raw` is a condition. It matches when the JSON has that path and the right-hand value. `true` does not match `false` or null. A null object such as `evChargeOptions` produces no row.
- `slv_poi_amenity` key is (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). `amenity_raw` is the condition string. `amenity` and `amenity_vi` are the values. Q3.
- Three sample JSON documents were used only to check paths. They are not copied into the repo.
- Domain: DDL/registry and silver transform. Do not commit.

## Classification rationale

- Complexity: medium. Signals: `design_tradeoffs`, `idempotency`, `transaction_boundaries`. The silver key includes `amenity_raw`, and the silver write has to be rerunnable.
- Risk: medium. New silver tables with a bounded rollback. Q3 puts `amenity_raw` in the key.
- Architecture: required. New table grain and a silver transform that matches JSON conditions to dictionary rows.
- Evidence: not required. `notebooks/NB_CREATE_DDL.ipynb` defines `slv_3p_poi_amenity` columns `poi_id` and `source_flags_json`. The collision count comes from the mapping file plus the match rule, not from an unknown runtime distribution.
- Runtime proof: not required at triage. Architecture has not been written.
- Reviewer routing: `sql-data-reviewer` for DDL, grain, and row uniqueness; `spark-runtime-reviewer` for the Fabric notebook that reads JSON and writes the silver table. No pipeline reviewer. Risk is not high, so no risk gate.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| Q1 | Nguồn business_sector | join thêm slv.slv_poi_entity (bảng này đang xử lý ở một luồng khác) qua poi_id để lấy business_sector. Thêm điệu kiện business_sector để join. | Quyết định của người dùng | 2026-10-16 |
| Q2 | Chính tả accommodation | Sửa chính tả accommodation | Quyết định của người dùng | 2026-10-16 |
| Q3 | Khóa slv_poi_amenity | ok chốt phương án đưa amenity_raw vào khóa. Vẫn giữ việc join thêm slv.slv_poi_entity (bảng này đang xử lý ở một luồng khác) qua poi_id để lấy business_sector. Thêm điệu kiện business_sector để join. | Quyết định của người dùng | 2026-10-16 |

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
- decision.md | 4778 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- request.md | 5136 bytes
- resume.md | 622 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1243 bytes

## NEXT

python scripts/vv.py run-gate 20261016-ref-amenities-poi-amenity

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
