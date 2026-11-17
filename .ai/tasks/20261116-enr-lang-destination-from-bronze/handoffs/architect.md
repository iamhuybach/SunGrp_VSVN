# Architect handoff: 20261116-enr-lang-destination-from-bronze

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261116-enr-lang-destination-from-bronze --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261116-enr-lang-destination-from-bronze/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261116-enr-lang-destination-from-bronze | phase=triage

## STATE

id: 20261116-enr-lang-destination-from-bronze
title: Extract enrichment LANG and DESTINATION from bronze
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: stateful_logic, event_ordering, idempotency, cross_system, runtime_proof_required, data_evidence_required, data_model_change
gates: evidence=pass, architecture=evidence_required, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: state-correctness-reviewer, spark-runtime-reviewer, sql-data-reviewer, api-contract-reviewer, jpa-performance-reviewer
open findings: none
exceptions: none
scope.files:

## VALIDATION

PASS

## RESUME

# Resume

## Status

user_decision. architecture=evidence_required, round 1 of 2. evidence=pass. U-4 is recorded. Do not implement. Do not spend architecture round 2 until the Copy Job column mapping is known.

## Done this session

Whitespace-only `house_number` or `street` skips the whole `full_address` group. Recorded in D-5 and `mapping_gld_srv_poi_info.md` §1.6. The three-group formula still applies only when a destination row exists.

## Next action

User says whether the Fabric Copy Job maps columns by current gold names or by a fixed list that still contains `cost_vnd`, and whether the job can be paused. Then Main runs architecture round 2.

## Read next

- `decision.md` D-5 and D-11
- `architecture.md` §17.4

## Waiting on

Copy Job column mapping and whether it can be paused.

## REQUEST

# Request

## User outcome

Silver `slv_enr_poi_info_multi_lang` is loaded only from `event_type = LANG` and `slv_enr_poi_destination` only from `event_type = DESTINATION` of `bronze.brz_enrichment_result`, using the JSON paths below. `cost_vnd` becomes `cost` on the three named tables and on every API read of multi-lang `cost_vnd`. `street` is removed from `slv_enr_poi_destination`. `gld_srv_poi_info.street` and `full_address` follow the stated sources and three priority groups.

## Scope

### In scope

- One task for the whole scope. No separate task for Mapping, extract, gold, PostgreSQL, or the API.
- `docs/requirements/20261116-enr-lang-destination-from-bronze/MAPPING.md` and `BRD.md`.
- Extract of `slv_enr_poi_info_multi_lang` and `slv_enr_poi_destination` from `bronze.brz_enrichment_result`.
- Column rename `cost_vnd` to `cost` on `slv_enr_poi_info_multi_lang`, `gld_srv_poi_multi_lang`, and `apps.srv_poi_multi_lang`, and the API reads of that column.
- Drop `street` from `slv_enr_poi_destination`.
- `gld_srv_poi_info.street` and `full_address` rules below.
- Update `docs/context/mapping_gld_srv_poi_info.md` and `docs/context/mapping_gld_srv_poi_multi_lang.md` in this task before review.

### Out of scope

- Any other table or notebook that still has `cost_vnd` or `street` and is not named in the request. Record those as ledger gaps; do not change them here.
- New API columns. The repository has no Flyway.
- Inventing a `full_address` separator that is not already in a notebook.

## Acceptance criteria

- `MAPPING.md` and `BRD.md` follow the templates, `doc_status` reaches `READY_FOR_ANALYSIS`, and `requirements-analysis.md` is `COMPLETE`.
- Each silver table accepts only its `event_type` and the JSON paths below.
- In the sample, `cost`, `best_time`, and `time_to_spend` stay objects `{text, label}`. `experiences` and `destination` stay arrays. `destination_id` and `destination_name` keep element order.
- `cost_vnd` becomes `cost` on the three named tables and every API read of multi-lang `cost_vnd`. `street` is gone from `slv_enr_poi_destination`.
- `gld_srv_poi_info.street` and `full_address` match the stated source and three priority groups.
- Both mapping context files are updated in this task before review.
- `verify` is `PASS` before review. P0/P1 are closed or have a disposition before review is treated as done.

## Constraints

- Do not edit notebooks, DDL, or the API before `requirements-analysis.md` is `COMPLETE`, `model-design.md` exists, and architecture is `PASS`.
- Mapping and BRD: copy the templates, keep section and column names, delete every `[EXAMPLE]` row. User-stated rules and JSON paths are `USER_STATED` with `context_ref` `USER_INPUT`. Types, grain, and keys of tables already in the repository come from DDL or notebooks (`CONTEXT_STATED`). A value without a valid source is `MISSING_EVIDENCE` plus a question. Two disagreeing sources are `CONFLICT`. Do not invent a join separator for `full_address`.
- `brz_enrichment_result` is not in the repository. Columns and JSON paths the user gave are recorded from the sample. Table schema, MERGE key, watermark, and uniqueness are not in the repository: smallest probe, then stop at `waiting_evidence`.
- Save architecture `FILE` blocks with `python scripts/vv.py materialize <task-id> --write`.
- Record an architecture deviation in `decision.md` before further edits.
- Do not commit. Do not run Fabric DEV or `docker compose`.

## Verbatim request

Đã có nguồn cho slv_enr_poi_info_multi_lang và slv_enr_poi_destination.

Nguồn: bronze.brz_enrichment_result.
- event_type = LANG → dữ liệu cho slv_enr_poi_info_multi_lang
- event_type = DESTINATION → dữ liệu cho slv_enr_poi_destination

Đổi cột:
- slv_enr_poi_info_multi_lang.cost_vnd đổi thành cost
- gld_srv_poi_multi_lang.cost_vnd đổi thành cost
- apps.srv_poi_multi_lang.cost_vnd đổi thành cost
- API đọc cost thay cho cost_vnd
- slv_enr_poi_destination.street bỏ

Extract hai bảng silver theo mapping. Cập nhật mapping và transform gld_srv_poi_info.

slv_enr_poi_info_multi_lang:
- poi_id ← bronze.brz_enrichment_result.poi_id
- source_name ← bronze.brz_enrichment_result.source
- lang ← bronze.brz_enrichment_result.lang
- cost ← bronze.brz_enrichment_result.data.display.cost
- best_time ← bronze.brz_enrichment_result.data.display.best_time
- time_to_spend ← bronze.brz_enrichment_result.data.display.time_to_spend
- description ← bronze.brz_enrichment_result.data.description
- experiences ← bronze.brz_enrichment_result.data.experiences
- translated_at ← bronze.brz_enrichment_result.data.translated_at

slv_enr_poi_destination:
- poi_id ← bronze.brz_enrichment_result.poi_id
- source_name ← bronze.brz_enrichment_result.source
- ward ← data.address.new.ward.name
- ward_with_type ← data.address.new.ward.name_with_type
- district ← data.address.new.district.name
- district_with_type ← data.address.new.district.name_with_type
- city ← data.address.new.province.name
- city_with_type ← data.address.new.province.name_with_type
- formatted_address ← data.address.new.formatted_address
- old_ward ← data.address.old.ward.name
- old_ward_with_type ← data.address.old.ward.name_with_type
- old_district ← data.address.old.district.name
- old_district_with_type ← data.address.old.district.name_with_type
- old_city ← data.address.old.province.name
- old_city_with_type ← data.address.old.province.name_with_type
- old_formatted_address ← data.address.old.formatted_address
- lat ← data.lat
- lng ← data.lng
- full_address ← data.request.address
- destination ← data.destinations
- destination_id ← mảng data.destinations.id
- destination_name ← mảng data.destinations.name (cùng thứ tự với destination_id)
- country_code = null
- postal_code = null

gld_srv_poi_info:
- street ← slv_poi_entity_non_enrich.street
- full_address, ghép theo ưu tiên; một field trong nhóm null thì chuyển nhóm sau:
  Ưu tiên 1: slv_poi_entity_non_enrich.house_number + slv_poi_entity_non_enrich.street + slv_enr_poi_destination.formatted_address
  Ưu tiên 2: slv_poi_entity_non_enrich.house_number + slv_poi_entity_non_enrich.street + slv_enr_poi_destination.ward_with_type + slv_enr_poi_destination.city_with_type
  Ưu tiên 3: slv_enr_poi_destination.full_address

Sample (4 rows, `data` is a JSON string) is stored verbatim at `evidence/samples/brz_enrichment_result_lang_destination.tsv`. The JSON key tree without values is `evidence/payload-shape.md`. Do not copy sample rows into `MAPPING.md`.

## Classification rationale

- Complexity: high. The change renames and drops columns, adds an extract from a new bronze event source, and changes gold address composition across silver, gold, PostgreSQL, and the serving API.
- Risk: high. Cross-system column rename plus a new stateful extract (MERGE and watermark) can diverge silver, gold, and PostgreSQL if the bronze key or watermark is wrong.
- Architecture: required. Column and key changes, and logic moves from bronze to silver, gold, and PostgreSQL. `data_model_change` requires `model-design.md` before the Architect.
- Evidence: required. Repository search found no `brz_enrichment_result`. User-stated columns and JSON paths are recorded from the sample. Table schema, MERGE key, watermark, and uniqueness are not in the repository.
- Runtime proof: required. A correct extract from the live bronze table cannot be proven by repository inspection. API rename still needs the local verification lane; Fabric DEV proof stays a later runbook, not this phase.
- Reviewer routing: `state-correctness-reviewer` (watermark, MERGE idempotency, event order), `spark-runtime-reviewer` (notebooks), `sql-data-reviewer` (Delta DDL and MERGE), `api-contract-reviewer` (DTO and `sql/postgres/gld_srv_serve.pg.sql`), `jpa-performance-reviewer` (entity field rename). `risk-gate` because risk is high. Pipeline JSON is not in the stated scope, so `fabric-pipeline-reviewer` is not routed yet. No security-surface files are in scope, so `app-security-reviewer` is not routed.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Evidence bronze | `experiences` là mảng 360/360, khóa phần tử `description,keyword,title`. `destinations` là mảng 113/113. 271 phần tử, 1 phần tử `id` và `name` null, 1 mảng không có khóa ở phần tử đầu. `translated_at` parse_null=0 trên 360 dòng. | evidence/results/probe_json_shape_rest.txt | 2026-11-16 |
| D-2 | Ngoài phạm vi sửa | Không sửa `gld_enr_poi_info`, cell lịch sử `NB_CREATE_DDL`, `slv_poi_entity_non_enrich.street`, và `(ood).general-information.md`. | request.md ## Constraints | 2026-11-16 |
| D-3 | Khoá silver | `slv_enr_poi_info_multi_lang`: một dòng cho `(poi_id, lang)`, MERGE đúng cặp đó. `slv_enr_poi_destination`: một dòng cho `poi_id`. `version` không nằm trong khoá. Cùng khoá thì giữ `version` lớn hơn; bằng `version` thì giữ `EventProcessedUtcTime` lớn hơn. | docs/context/mapping_gld_srv_poi_multi_lang.md §2; docs/context/mapping_gld_srv_poi_info.md §1.6 | 2026-11-16 |
| D-4 | Extract | `load_mode = DOC`. `src_object = $`. Cột gốc: `_doc.poi_id`, `_doc.source`, `_doc.lang`. Cột trong `data`: path JSON đã nêu. `convert_rule = NONE` cho STRING và `lat`/`lng`. `translated_at` là TIMESTAMP, `ISO_UTC_TS`, `parse_null = 0`. `country_code` và `postal_code` ghi NULL. Watermark `EventProcessedUtcTime`. | evidence/results/probe_json_shape_rest.txt | 2026-11-16 |
| D-5 | full_address | Nối bằng `, ` (phẩy và một dấu cách). Một field null, hoặc `house_number` hay `street` chỉ còn khoảng trắng sau trim, thì bỏ cả nhóm. Ba nhóm chỉ khi có dòng destination; không có thì giữ `full_address` của entity. | docs/context/mapping_gld_srv_poi_info.md §1.6; người dùng U-2 và U-4, 2026-11-17 | 2026-11-17 |
| D-6 | Cột và tên bảng | Cột chữ mới là STRING. `destination` là chuỗi JSON của cả mảng. `data.experiences` ghi vào `experience` STRING. Giữ tên hai bảng `slv_enr_*`. Bỏ Mapping `TRG-005`. `apps.srv_poi_multi_lang.cost_vnd` thành `cost`, giữ `text`. `practical_info.md` nằm trong phạm vi. | docs/context/mapping_gld_srv_poi_multi_lang.md §2 | 2026-11-16 |
| D-7 | PC-01 nguồn slv_enr_ | Người dùng chấp nhận lệch PC-01 trên `SRC-003` và `SRC-004`. Giữ nguyên tên `slv_enr_poi_info_multi_lang` và `slv_enr_poi_destination`. | Người dùng, 2026-11-16; MAPPING.md `MQ-001` | 2026-11-16 |
| D-8 | Quyết định Architect | A-1 đến A-10 trong `architecture.md` §19 được ghi nhận. Vòng architecture 1 là `EVIDENCE_REQUIRED`. Chưa implement. | architecture.md §19 | 2026-11-17 |
| D-9 | U-1 U-2 U-3 | U-1: sửa parser để `{text, label}` thành `{label, value=text}`. U-2: ba nhóm `full_address` chỉ khi có dòng destination; không có thì giữ `full_address` của entity. U-3: `destination_id` và `destination_name` là chuỗi JSON mảng, kể cả null. | Người dùng, 2026-11-17 | 2026-11-17 |
| D-10 | Probe P-1 P-3 P-4 | `slv_enr_poi_info_multi_lang` có 3 dòng, không tạo lại bảng. `slv_enr_poi_destination` có 0 dòng. Gold multi_lang 859 dòng sống, 0 dòng `deleted_at`, reader 1, writer 2. Mọi `poi_id` bronze khớp entity. Destination JSON không có chuỗi rỗng. Partner entity có 39 `house_number` rỗng và 39 `street` rỗng. | evidence/results/probe_arch_gaps.txt | 2026-11-17 |
| D-11 | Copy Job | Gold sang `apps.srv_poi_*` bằng Fabric Copy Job. Job map cột theo tên hiện có trên gold, không theo danh sách cố định `cost_vnd`. Người dùng không nói job có tạm dừng được hay không. | Người dùng, 2026-11-17 | 2026-11-17 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: EVIDENCE_REQUIRED
size: 44470 bytes

## FILES

- architecture.md | 44470 bytes | large: use toc/show
- decision.md | 6490 bytes
- evidence/payload-shape.md | 1799 bytes
- evidence/plan.md | 2405 bytes
- evidence/probes/probe_arch_gaps.py | 3605 bytes
- evidence/probes/probe_brz_enrichment_result.py | 5991 bytes
- evidence/probes/probe_json_shape.py | 2343 bytes
- evidence/probes/probe_json_shape_rest.py | 3291 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/results/probe_arch_gaps.txt | 659 bytes
- evidence/results/probe_brz_enrichment_result.txt | 2584 bytes
- evidence/results/probe_json_shape.txt | 434 bytes
- evidence/results/probe_json_shape_rest.txt | 443 bytes
- evidence/samples/brz_enrichment_result_lang_destination.tsv | 5796 bytes
- handoffs/architect.md | 17786 bytes
- handoffs/author-input.md | 2973 bytes
- model-design.md | 18547 bytes
- request.md | 8238 bytes
- requirements-analysis.md | 11938 bytes
- resume.md | 821 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1532 bytes

## NEXT

python scripts/vv.py run-gate 20261116-enr-lang-destination-from-bronze
