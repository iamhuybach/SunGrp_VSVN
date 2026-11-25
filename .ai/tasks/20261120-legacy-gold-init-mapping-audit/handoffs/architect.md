# Architect handoff: 20261120-legacy-gold-init-mapping-audit

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261120-legacy-gold-init-mapping-audit --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261120-legacy-gold-init-mapping-audit/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261120-legacy-gold-init-mapping-audit | phase=triage

## STATE

id: 20261120-legacy-gold-init-mapping-audit
title: Audit legacy gold init column mapping
status/owner: waiting_architecture/architect
complexity/risk: medium/high
required: architecture_required=True, evidence_required=True, runtime_required=True
signals: design_tradeoffs, data_evidence_required, idempotency, runtime_proof_required
gates: evidence=evidence_required, architecture=pending, local_verification=pass, specialist_review=evidence_required, risk_gate=evidence_required, runtime=pending
rounds: verification=0, review=3, architecture=1, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer
open findings: none
exceptions: none
scope.files:
- notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb
- tests/test_legacy_gold_poi_init_contract.py

## VALIDATION

PASS

## RESUME

# Resume

## Status
user_decision. PLAN is valid. RUN has not started. GOOGLE_BAD_TIME is explained.

## Done this session
- Saved `evidence/results/google-bad-time-cause.txt`.
- All 6450 classified Google rows are `close_null` with `is_24_7 = true`. No fractional hours and no null open time. PLAN still has 6430 `GOOGLE_BAD_TIME` inside the info candidate set.

## Next action
Wait for the user to keep D-05, leaving those rows null, or to name a new rule for `is_24_7 = true` with null close. Do not change `google_hours` before that choice.

## Read next
- `evidence/results/google-bad-time-cause.txt`
- `decision.md`, D-05
- `docs/context/mapping_gld_srv_poi_info.md`, Case 2

## Waiting on
User confirmation to RUN under D-05, or a named rule for the 24-hour rows.

## REQUEST

# Request

## User outcome

The one-time legacy gold init written by `NB_SETUP_LEGACY_GOLD_POI` matches the current gold model and the old-flow notebooks on every column it writes into `gld_srv_*`. `operating_hours` and `holiday_exceptions` are not left null by an unproven expression. Where the old JSON shape is not the input the current rule expects, the task stops and asks for the transform rule.

## Scope

### In scope

- Column-by-column comparison of what `NB_SETUP_LEGACY_GOLD_POI` writes into `gld_srv_*` against the old-flow notebooks and the current model notebooks.
- Fix only columns that mismatch, or that are null because the init transform is wrong.
- `operating_hours` and `holiday_exceptions`, including the two init paths `get_json_object(poi_content_json, $.hours_weekday_text)` and `get_json_object(poi_opening_hours_json, $.holiday_exceptions)`.
- Current-model rules from `docs/context/mapping_gld_srv_poi_info.md` (Google and partner `operating_hours`, and `holiday_exceptions`) and from `NB_SLV_POI_ENTITY_NON_ENRICH` and `NB_GLD_SRV_POI_INFO`.
- Old-flow shape from `notebooks_lgc/3rd_data_ingested_orches/` and `notebooks_lgc/pl_transform_partner_userprofile_cms/`.
- A Fabric DEV probe only when a rule exists and still depends on the DEV JSON shape: null rate and the key tree of the related old field, at most 50 rows, no names or content.
- `model-design.md` through `run-author --kind model` only when a confirmed rule changes a column's meaning, type, or key.
- Architecture and review for this task only.
- A runtime runbook, through `run-author --kind runbook`, when the init notebook must be run again on Fabric.

### Out of scope

- Task `20261119-legacy-gold-poi-init`: no edits, no reopened gates, no reimplementation of D-01 through D-09.
- The "do not load" list in that task's `model-design.md`. Current init notebook and current mapping are the baseline. D-07 requires loading a field that has a source.
- `poi_id`, `load_origin`, map-table grain, pipeline schedule, and the init table list, unless the comparison shows a defect in one of them.
- A new JSON parser when the old gold JSON shape is not the input of the current-model rule.
- Guessed `json_path` values. A key absent from the old notebook and from a probe is `MISSING_EVIDENCE`.
- Serving API, `services/data-serving-service`.
- DDL, unless a confirmed rule requires a column change.
- Fabric DEV execution of the init notebook in this chat.

## Acceptance criteria

- An evidence table lists every column `NB_SETUP_LEGACY_GOLD_POI` writes into `gld_srv_*`. Each row states the init expression, the source in the old-flow notebook, and the rule running in the current model. Matching columns are marked match. Mismatched columns are marked mismatch.
- `operating_hours` and `holiday_exceptions` are not assigned by an unproven path. The two current init paths are in the comparison table.
- The current-model rule is taken from `docs/context/mapping_gld_srv_poi_info.md` and from `NB_SLV_POI_ENTITY_NON_ENRICH` plus `NB_GLD_SRV_POI_INFO`. Gold `operating_hours` is not a raw copy of `opening_hours_text`. Google stops when the hours JSON is not the shape recorded in the mapping. Partner reads the object `$.policies.operating_hours`. Partner `holiday_exceptions` is a JSON string and is not parsed. Google has no entity `holiday_exceptions`, so the task does not invent a value.
- When the old gold JSON shape is not the current rule's input, no new parser is written. Status becomes `user_decision`, naming the field and the JSON keys actually seen, and asking for the transform rule.
- Only mismatched columns, or columns null because of a wrong transform, are changed.
- Rerunning init does not duplicate rows and does not update rows the new pipeline owns.

## Constraints

- One task, one chat, full `docs/agent-system/WORKFLOW.md` §6. No fast lane. No split between an audit task and a fix task.
- Stop only for a Fabric DEV probe, `user_decision`, a CLI or model fallback, a round cap, or `waiting_runtime`.
- Comparison is done before DEV evidence and before code changes. The comparison table is task evidence. A column with no transform rule is a question, then `user_decision`. Do not call the Architect to invent a rule.
- Domain: transform/gold library and the init notebook. DDL only when a confirmed rule requires a column change.
- Reference task `20261119-legacy-gold-poi-init` is `ready_to_merge` (architecture round 2, review round 3, `extra_round_approved_on` 2026-11-19). All edits live in this task.
- Do not infer a `json_path`. Do not read that task's `reviews/` or `docs/context/3p-google/*.txt`.
- The user runs Fabric DEV. This chat does not run the init notebook on DEV.
- No commit unless the user's current turn asks for one.

## Classification rationale

- Complexity: medium. The change is bounded to init column expressions, but the hours fields are not a single `get_json_object` and a wrong assignment leaves historical gold unusable.
- Risk: medium. Rollback is a rerun of the same init notebook under the existing row-ownership guard. Risk becomes high only if the comparison shows a MERGE, `load_origin`, or write-order defect.
- Architecture: required. The task has its own architecture and review. A missing transform rule stops at `user_decision` and is not sent to the Architect.
- Evidence: required. The all-null hours symptom is not a cause. If a rule exists and still depends on the DEV JSON shape, the smallest probe is the null rate and the key tree.
- Runtime proof: required when init SQL changes, because the historical load must be rerun without duplicating rows or touching pipeline-owned rows. The runbook states the rerun and how to see that the two hours columns are no longer null for a transform reason.
- Reviewer routing: `sql-data-reviewer` and `spark-runtime-reviewer`. Add `state-correctness-reviewer` only if the fix changes MERGE, `load_origin`, or write order. Signals expected on this path: `design_tradeoffs`, `data_evidence_required`, `runtime_proof_required`, and `data_model_change` only if a confirmed rule changes a column type or meaning.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | `operating_hours` partner | Lấy `poi_opening_hours_json.periods_json` và chạy `google_hours` của `NB_GLD_SRV_POI_INFO` (mapping §1.3). `periods_json` null hoặc `[]` thì `operating_hours` null. Object `policies.operating_hours` không còn trong gold cũ nên không chạy mapping §1.5 và không dựng lại object đó. Khoảng giờ thứ hai mỗi ngày đã mất lúc ghi gold cũ thì không phục hồi. | Người dùng, 2026-11-24. Probe `hours-shape.txt`: 63 dòng partner có khóa `close_hour`, `close_minute`, `day_of_week`, `open_hour`, `open_minute`; 93 dòng là mảng rỗng | 2026-11-24 |
| D-02 | `operating_hours` Google | Lấy `poi_opening_hours_json.periods_json` và chạy cùng `google_hours`. `$.periods` null trên toàn bộ 45521 dòng Google. 36521 dòng có khóa phần tử `close_day`, `close_hour`, `close_minute`, `day_of_week`, `open_hour`, `open_minute`. `close_day` không đọc. `periods_json` null hoặc `[]` thì `operating_hours` null. | Probe `evidence/results/hours-shape.txt`, 2026-11-24 | 2026-11-24 |
| D-03 | `holiday_exceptions` | Google ghi null. Partner copy nguyên chuỗi `poi_opening_hours_json.holiday_exceptions_json`, không parse. Thiếu khóa trong notebook cũ đã thành `[]` thì giữ chuỗi `[]`. Không đọc `$.policies.holiday_exceptions` vì khóa đó không còn trong gold cũ. | Người dùng, 2026-11-24. Entity Google là `lit(None)`. Partner entity giữ chuỗi JSON | 2026-11-24 |
| D-04 | Ba cột lệch đã có rule | `rating_count`: chỉ Google, từ `poi_rating.total_reviews`, null khi nguồn null, không coalesce 0. `review_count`: chỉ Google, `COUNT(*)` dòng `poi_review`, không có dòng thì null. `is_recommended`: true khi `source_name` là partner, còn lại false. | Mapping `gld_srv_poi_info` và `NB_GLD_SRV_POI_INFO` | 2026-11-24 |
| D-05 | Dòng giờ không đúng shape | Dòng `google_hours` trả mã lỗi thì `operating_hours` null, trừ dòng `is_24_7` true thì theo D-07. Init vẫn ghi các dòng khác. Summary đếm từng mã lỗi. Cả lần init không dừng vì một dòng. | Người dùng, 2026-11-24, sửa 2026-11-25 theo D-07 | 2026-11-25 |
| D-07 | `is_24_7` true | Mọi dòng có `poi_opening_hours_json.$.is_24_7` sau `lower(trim)` bằng `true` thì `operating_hours` là output case 2 của mapping: bảy ngày 1–7, `is_open_all_day` true, `is_closed` false, không có `open_time`, `close_time`, `value`. Không đọc `periods_json` ở những dòng này. Áp cho google và partner. | Người dùng, 2026-11-25. Model mới không có nhánh `is_24_7`. Case 2 là dạng mở cả ngày duy nhất của `google_hours` | 2026-11-25 |
| D-06 | `vi_key` khi trùng `poi_id` mới | Chọn dòng vào sau: `poi_master.created_at` lớn nhất trong các dòng `lang = vi` cùng `poi_id` mới. `created_at` null xếp sau dòng có giờ. Cùng `created_at` thì lấy `legacy_poi_id` lớn hơn theo thứ tự chữ. Áp cho mọi nhóm trùng, không dừng notebook. | Người dùng, 2026-11-25: SQL-001 chọn dòng vào sau. Cột `created_at` có trong `NB_40_GOLD_POI_SERVING` trên `poi_master` | 2026-11-25 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-002 | P1 | rejected-false-positive | `total_reviews` đã là `bigint`. `rating_not_exact_bigint_n` = 0 trên probe `review-round1-guards.txt`. Cast sang `bigint` không cắt giá trị. | |
| SQL-001 | P1 | fixed | D-06 đã chạy. Probe `vi-key-rank1-source.txt`: `rank1_source_conflict_n` = 0. Hạng 1 không có hai `source_name`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: PASS
size: 30092 bytes

## FILES

- architecture.md | 30092 bytes | large: use toc/show
- decision.md | 8472 bytes
- evidence/column-mapping.md | 12112 bytes
- evidence/plan.md | 1717 bytes
- evidence/probes/google_bad_time_cause.py | 3000 bytes
- evidence/probes/hours_shape.py | 5450 bytes
- evidence/probes/README.md | 175 bytes | placeholder
- evidence/probes/review_round1_guards.py | 1453 bytes
- evidence/probes/vi_key_rank1_source.py | 1483 bytes
- evidence/results/google-bad-time-cause.txt | 89 bytes
- evidence/results/hours-shape.txt | 4474 bytes
- evidence/results/plan-summary.json | 1460 bytes
- evidence/results/review-round1-guards.txt | 90 bytes
- evidence/results/vi-key-detail-hash.txt | 313 bytes
- evidence/results/vi-key-rank1-source.txt | 31 bytes
- handoffs/architect.md | 16205 bytes
- handoffs/author-input.md | 1984 bytes
- handoffs/review-round-1.md | 1605 bytes
- handoffs/review-round-2.md | 3070 bytes
- handoffs/review-round-3.md | 2788 bytes
- request.md | 6183 bytes
- resume.md | 790 bytes
- reviews/README.md | 157 bytes | placeholder
- reviews/round-1.json | 486 bytes
- reviews/round-1.md | 936 bytes
- reviews/round-2.json | 423 bytes
- reviews/round-2.md | 1049 bytes
- reviews/round-3.json | 357 bytes
- reviews/round-3.md | 702 bytes
- runtime-runbook.md | 18866 bytes
- task-state.yaml | 1502 bytes
- verification/verify.log | 1922 bytes

## NEXT

python scripts/vv.py run-gate 20261120-legacy-gold-init-mapping-audit

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb (48592 bytes)

[0] markdown id=lgpmd json=3-14 lines=5 | NB_SETUP_LEGACY_GOLD_POI | defs: none
[1] code id=lgpparams json=15-30 lines=2 | p_mode = "PLAN" | defs: none
[2] code id=lgplib json=31-45 lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=lgpconst json=46-68 lines=9 | OLD = "sgr_visitvn_prd_batch.lh_vv_gold.dbo" | defs: none
[4] code id=lgphours json=69-181 lines=99 | import json | defs: _int, _open, _closed, _all_day, _dump, google_hours, partner_hours, operating_hours
[5] code id=lgppure json=182-297 lines=102 | ORIGIN = "LEGACY_INIT" | defs: legacy_source_name, new_poi_id, insert_only_sql, single_payload, legacy_upsert_sql, legacy_hours, amenity_enum_values, add, walk
[6] code id=lgpmain json=298-816 lines=505 | import inspect | defs: _workspace_name, _history_version, old, present_counts, to_target, _metrics, _commit_lookup, write_insert_only, _j
