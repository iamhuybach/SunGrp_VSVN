# Architect handoff: 20261016-ref-place-type-poi-entity

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261016-ref-place-type-poi-entity/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261016-ref-place-type-poi-entity | phase=triage

## STATE

id: 20261016-ref-place-type-poi-entity
title: Place-type dictionary and Google POI entity
status/owner: waiting_architecture/architect
complexity/risk: medium/medium
required: architecture_required=True, evidence_required=False, runtime_required=False
signals: design_tradeoffs, idempotency
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer
open findings: none
exceptions: none
scope.files:

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

Silver has a shared place-type dictionary `lh_vv_silver.dbo.ref_dictionary_place_type`, seeded from `docs/context/3p-google/mapping_place_type.md`, and a Google-only POI entity `lh_vv_silver.dbo.slv_poi_entity` that keeps every column of `lh_vv_silver.dbo.slv_3p_poi` and adds `business_sector`, `business_category`, and `business_category_vi` resolved from that dictionary.

The user wrote schema `slv.`. The silver schema in this repo is `lh_vv_silver.dbo`. Keep the table names.

## Scope

### In scope

- DDL for `lh_vv_silver.dbo.ref_dictionary_place_type` with columns: `source_name` string, `place_type` string, `business_sector` string, `business_category` string, `business_category_vi` string, `is_active` boolean, `updated_at` timestamp.
- One seed of that dictionary from `docs/context/3p-google/mapping_place_type.md`.
- DDL and build of `lh_vv_silver.dbo.slv_poi_entity` for Google only: all columns of `slv_3p_poi`, plus the three category columns resolved by the rules below.

### Out of scope

- Sectors other than the seven normalized values.
- Filling `business_category_vi` on the unmatched entity branch.
- Partner rows in `slv_poi_entity`.
- Commit, merge, or a Fabric DEV run during triage.

## Acceptance criteria

- Each Google place type has one row with `source_name = google`. No row has `place_type` equal to `Fallback`, `Không có`, or `Partner Portal bổ sung` (either casing of the Partner Portal label).
- `extended_stay_hotel` has a `google` row and no `partner` row.
- No two rows share `(source_name, place_type)`.
- `slv_poi_entity` includes every column of `slv_3p_poi`.
- When `primary_type` matches a `google` `place_type`, the three category columns come from that row and `types_json` does not change them.
- When `primary_type` does not match, the first matching element of `types_json`, in array order, supplies the three category columns and later elements are ignored.
- When neither matches, `business_sector = other` and `business_category = other`. `business_category_vi` stays unset on that branch.

## Constraints

- Dictionary seed:
  - `business_sector` comes from the section header, normalized only as: `1.1 Accomodation` → `accommodation`; `1.2 F&B` → `fnb`; `1.3 Spa & Wellness` → `spa_n_wellness`; `1.4 Shopping & Retail` → `shopping_n_retail`; `1.5 Attraction` → `attraction`; `1.6 Vehicle Rental` → `vehicle_rental`; `1.7 Public POI & Infrastructure` → `other`.
  - Partner Portal Enum emits `source_name = partner`. Google Place API – Place Type emits `source_name = google`. The two columns are separate rows that share that row's `business_category` and `business_category_vi`.
  - `place_type` is one cell value. A Google cell with comma-separated types becomes one row per type.
  - Do not emit a row for exactly these values: `Partner Portal bổ sung`, `Partner Portal Bổ sung`, `Fallback`, `Không có`. Dropping one of those values does not drop the other column on the same row. A Google type on a "Partner Portal bổ sung" row still emits a `google` row.
  - Hiển thị (VI) → `business_category_vi`. Hiển thị (EN) → `business_category`.
  - `is_active = true`. `updated_at` is the seed write time, one timestamp for the whole seed.
- Entity resolution uses only `source_name = google`. Match `slv_3p_poi.primary_type` first. On miss, scan `slv_3p_poi.types_json` in array order and stop at the first match.
- If `slv_3p_poi` lacked `primary_type` or `types_json`, stop and name the missing column. Both columns are present; see Evidence.
- Do not invent a Vietnamese label for the unmatched entity branch.

## Classification rationale

- Complexity: `medium`. Signals: `design_tradeoffs`, `idempotency`. The dictionary grain and the entity category resolution are specified, but `ref_dictionary_place_type` sits beside existing `ref_business_category`, and `slv_poi_entity` sits beside L2 `slv_poi` (N2), which already resolves sector and category. Seed uniqueness on `(source_name, place_type)` and first-match category resolution must stay deterministic on rerun.
- Risk: `medium`. New silver tables and a bounded mapping. No change to CDC, watermark, or lock behavior. Rollback is to stop reading the new tables.
- Architecture: required. New table grain and key, silver L2 mapping, and a placement trade-off against `ref_business_category` and `slv_poi`.
- Evidence: not required. `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` (note dated 14/10: 9 tables, 55 columns, 0 inactive) maps active `slv_3p_poi` columns `types_json` (`types`) and `primary_type` (`primaryType`). Neither uses `_off`. Registry business columns on that table: `poi_id`, `source_name`, `source_id`, `language_code`, `poi_name`, `poi_name_normalized`, `types_json`, `subcategory_tags_json`, `operating_status`, `primary_type`. `docs/context/01_DATA_MODEL.md` §5.2 also names L1 technical columns `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`, `created_at`, `updated_at`. Architecture must take the full physical column set of `slv_3p_poi` from that DDL contract.
- Runtime proof: not required for classification. Seed rows and match order are deterministic from the mapping file and the rules above. Local checks can prove them. A Fabric apply, if the design needs one, is a later runbook.
- Reviewer routing: `sql-data-reviewer` (DDL, types, grain, unique key, category lookup); `spark-runtime-reviewer` (silver notebook or `NB_LIB_*` transform that builds `slv_poi_entity`); `state-correctness-reviewer` (idempotent seed and deterministic entity rebuild). No pipeline reviewer: no pipeline change is in scope.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|

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
- decision.md | 721 bytes | placeholder
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 10472 bytes
- request.md | 5695 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1199 bytes

## NEXT

python scripts/vv.py run-gate 20261016-ref-place-type-poi-entity
