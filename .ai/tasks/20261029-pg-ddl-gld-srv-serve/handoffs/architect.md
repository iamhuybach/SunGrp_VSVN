# Architect handoff: 20261029-pg-ddl-gld-srv-serve

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261029-pg-ddl-gld-srv-serve --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261029-pg-ddl-gld-srv-serve/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261029-pg-ddl-gld-srv-serve | phase=triage

## STATE

id: 20261029-pg-ddl-gld-srv-serve
title: PostgreSQL DDL for five gold serving tables
status/owner: waiting_architecture/architect
complexity/risk: medium/low
required: architecture_required=True, evidence_required=False, runtime_required=False
signals: cross_system, data_model_change
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer
open findings: none
exceptions: none
scope.files:
- sql/postgres/gld_srv_serve.sql

## VALIDATION

PASS

## RESUME

# Resume

## Status

`user_decision`. Architecture is `pending` and has not been run. `model-design.md` is required before `run-gate` because signal `data_model_change` is set. Local verification and specialist review are `pending`.

## Done this session

Recorded user decisions: schema `apps`; PostgreSQL tables `srv_poi_info`, `srv_poi_multi_lang`, `srv_poi_amenity`, `srv_poi_media_gallery`, `srv_poi_review` (drop the `gld_` prefix); `apps.srv_poi_review` omits gold column `lang`. Primary key stays `review_id`. Attached `data_model_change`. Did not call `run-author` or `run-gate`.

## Next action

Wait for the PostgreSQL type of Fabric `BIGINT` (`gld_srv_poi_review.rating_count`). Then record it in `decision.md` D-BIGINT and D-TYPE, transition `user_decision` → `triage` → `waiting_architecture`, run `python scripts/vv.py run-author 20261029-pg-ddl-gld-srv-serve --kind model`, then `python scripts/vv.py run-gate 20261029-pg-ddl-gld-srv-serve`. On architecture `PASS`, write `sql/postgres/gld_srv_serve.sql`. Do not probe Fabric. Do not change `NodeSpec.pk`.

## Read next

- `.ai/tasks/20261029-pg-ddl-gld-srv-serve/decision.md` — `Quyết định hiện hành` D-SCHEMA, D-NAME, D-LANG, D-BIGINT
- `.ai/tasks/20261029-pg-ddl-gld-srv-serve/request.md` — `Classification rationale`
- `docs/agent-system/WORKFLOW.md` — `5. Classification` (`data_model_change`)

## Waiting on

The PostgreSQL type for `gld_srv_poi_review.rating_count` (`BIGINT`). The approved map has no `BIGINT` row, so the type is `MISSING`.

## REQUEST

# Request

## User outcome

PostgreSQL that serves the API has five gold serving tables, with the same columns and the same keys as current Fabric gold.

Verbatim request:

Tạo DDL cho 5 bảng Gold ở db PostgreSQL phục vụ serve API. Key sẽ tương ứng với grain của các bảng.

Lý do nghiệp vụ: PostgreSQL phục vụ API cần năm bảng gold serving, cùng cột và cùng khóa với gold Fabric hiện tại.

Năm bảng, schema Fabric `lh_vv_gold.dbo`:

- `gld_srv_poi_info`
- `gld_srv_poi_multi_lang`
- `gld_srv_poi_amenity`
- `gld_srv_poi_media_gallery`
- `gld_srv_poi_review`

Không gồm `gld_enr_poi_info` và `gld_enr_poi_review`.

## Scope

### In scope

- One file `sql/postgres/gld_srv_serve.sql` with five `CREATE TABLE` statements.
- Primary key column order from each table notebook's `NodeSpec.pk`.
- Columns and Fabric types from current gold DDL (`NB_SETUP_INITIAL_DDL` cell `init_tables`, confirmed by the latest `NB_CREATE_DDL` cell for that table).
- Type mapping recorded at the top of the SQL file and in `decision.md`.

### Out of scope

- `gld_enr_poi_info` and `gld_enr_poi_review`.
- Extra columns, indexes, views, or an API.
- A sync notebook or sync job.
- Edits to Fabric notebooks, pipelines, or lakehouse DDL.
- `notebooks_lgc/` and `srv_*` tags in `docs/diagram/VSVN_DATA_MODEL.drawio`.

## Acceptance criteria

- `sql/postgres/gld_srv_serve.sql` contains five `CREATE TABLE` statements.
- `PRIMARY KEY` column order matches `NodeSpec.pk` for that table's notebook.
- Columns and types come from current gold DDL. No added column, index, view, or API. No sync notebook.
- `NOT NULL` only where gold DDL writes `NOT NULL`, plus columns that belong to the primary key.
- Type mapping, written at the top of the file and in `decision.md`: `STRING` → `text`, `BOOLEAN` → `boolean`, `INT` → `integer`, `DOUBLE` → `double precision`, `DECIMAL(p,s)` → `numeric(p,s)`, `TIMESTAMP` → `timestamp without time zone`. Any other Fabric type is `MISSING`. Do not invent `varchar(n)` or `timestamptz`.
- If the repository has no PostgreSQL schema name, stop at `user_decision` and ask one question: the schema name. Do not use `public` and do not use a `srv_*` name from the old diagram.
- Do not edit Fabric notebooks, pipelines, or lakehouse DDL.

## Constraints

- `NodeSpec.pk` is the grain. Do not call `run-author --kind model` to change keys.
- Attach `data_model_change` only when a PostgreSQL column or key differs from gold. A full-column copy does not attach it.
- Run architecture when §Classification requires it because this is PostgreSQL DDL. Do not expand scope to a sync job.
- Do not read `notebooks_lgc/` and do not read `srv_*` tags in `docs/diagram/VSVN_DATA_MODEL.drawio`.
- No Fabric DEV probe for this DDL.

## Classification rationale

- Complexity: `medium`. Signal `cross_system`: the SQL file is a PostgreSQL serving contract taken from Fabric gold grain and columns. Signal `data_model_change`: the user removed column `lang` from the PostgreSQL review table (`decision.md` D-LANG). Keys stay `NodeSpec.pk`. The unmapped `BIGINT` still blocks writing.
- Risk: `low`. The change is one new SQL file. Fabric notebooks, pipelines, and lakehouse DDL stay unchanged. Once the schema name and the `BIGINT` mapping are known, local verification can check the file. No deployed behavior changes in this task.
- Architecture: required. `docs/agent-system/WORKFLOW.md` §Classification: logic moving between bronze, silver, gold, orchestration, or PostgreSQL sync. This task adds the PostgreSQL DDL for the five gold serving tables. The sync job stays out of scope. The gate is not run in this session: the schema name and the `BIGINT` mapping are missing, so the task stops at `user_decision` before architecture.
- Evidence: not required. Keys and column types are in the repository notebooks named by the request. No Fabric probe.
- Runtime proof: not required. The deliverable is a SQL file. Runtime gate stays `not_required` and is not marked pass.
- Reviewer routing: `sql-data-reviewer`. `docs/agent-system/WORKFLOW.md` §Review routing: that reviewer owns PostgreSQL SQL. No Spark notebook, pipeline JSON, CDC, or MERGE is in scope, so `spark-runtime-reviewer`, `fabric-pipeline-reviewer`, and `state-correctness-reviewer` are not routed. Risk is `low`, so `risk-gate` is not required.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-TYPE | Ánh xạ kiểu | STRING → text, BOOLEAN → boolean, INT → integer, DOUBLE → double precision, DECIMAL(p,s) → numeric(p,s), TIMESTAMP → timestamp without time zone. BIGINT sẽ là INT8. Kiểu khác: MISSING, không bịa varchar(n) hay timestamptz. | request.md Acceptance criteria; User 2026-10-29 | 2026-10-29 |
| D-SCHEMA | Tên schema PostgreSQL | Tên schema: apps. | User 2026-10-29 | 2026-10-29 |
| D-NAME | Tên bảng PostgreSQL | Tên bảng tiền tố bỏ gld_; Bắt đầu bằng srv_. `apps.srv_poi_info`, `apps.srv_poi_multi_lang`, `apps.srv_poi_amenity`, `apps.srv_poi_media_gallery`, `apps.srv_poi_review`. | User 2026-10-29 | 2026-10-29 |
| D-LANG | Cột lang của review | review_id bỏ field lang. Bảng PostgreSQL `apps.srv_poi_review` (pk `review_id`) không có cột `lang`. Gold `gld_srv_poi_review.lang` giữ nguyên. | User 2026-10-29 | 2026-10-29 |
| D-BIGINT | Kiểu BIGINT | BIGINT sẽ là INT8. Cột `gld_srv_poi_review.rating_count` trên PostgreSQL là `int8`. | User 2026-10-29 | 2026-10-29 |
| D-MODEL | data_model_change | Gắn data_model_change vì cột PostgreSQL khác gold: `apps.srv_poi_review` không có `lang`. Khóa không đổi, vẫn `NodeSpec.pk` (`review_id`). `model-design.md` viết bằng `run-author --kind model` trước architecture. Author không đổi khóa. | request.md Constraints; WORKFLOW.md §Classification | 2026-10-29 |

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
- decision.md | 12501 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 2027 bytes
- model-design.md | 19593 bytes
- request.md | 4438 bytes
- resume.md | 1556 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 1262 bytes

## NEXT

python scripts/vv.py run-gate 20261029-pg-ddl-gld-srv-serve
