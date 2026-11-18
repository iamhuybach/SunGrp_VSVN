# Architect handoff: 20261117-pipeline-precheck-flows

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261117-pipeline-precheck-flows --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261117-pipeline-precheck-flows/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

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

# Context 20261117-pipeline-precheck-flows | phase=triage

## STATE

id: 20261117-pipeline-precheck-flows
title: Pipeline pre-check so extract and transform skip when there is no data
status/owner: waiting_architecture/architect
complexity/risk: high/high
required: architecture_required=True, evidence_required=False, runtime_required=True
signals: design_tradeoffs, concurrency, retry_recovery, partial_failure, cross_system, stateful_logic, runtime_proof_required
gates: evidence=not_required, architecture=pass, local_verification=pending, specialist_review=pending, risk_gate=pending, runtime=pending
rounds: verification=0, review=0, architecture=1, runtime_failure=0
reviewers: fabric-pipeline-reviewer, sql-data-reviewer
open findings: none
exceptions: EX-ARCH architect claude-fable-5-2 medium 2026-11-17, EX-AUTHOR author claude-fable-5-2 medium 2026-11-17, EX-PROPOSAL author_proposal claude-fable-5-2 medium 2026-11-17
scope.files:
- pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json
- pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json
- pipelines/PL_VV_TRANS_SLV_TO_GLD_30M/PL_VV_TRANS_SLV_TO_GLD_30M.json

## VALIDATION

PASS

## REQUEST

# Request

## User outcome

Extract and transform pipelines skip a notebook when that source has no new data, without starting Spark. Partner, 3rd-party, and the silver-to-enrichment and silver-to-gold flows follow one recorded layout. A source that has no extract notebook has no pipeline activity.

## Scope

### In scope

- Pre-check for bronze sources `partner_raw_data`, `brz_3rd_crawler_poi_stream`, `cms_raw_data`, and `brz_enrichment_result` on `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` config, using `ctrl_mng_pipeline_config`, `ctrl_mng_watermark`, and `_delta_log`. `NO_DATA` must not start Spark.
- The same no-data skip for extract notebooks that exist and for the transform flows `PL_VV_TRANS_SLV_TO_ENR_15M` (JSON exists) and `PL_VV_TRANS_SLV_TO_GLD_30M` (JSON does not exist).
- One layout choice, recorded in `decision.md` before any pipeline JSON edit: one combined pipeline, separate pipelines, or another layout. The criteria are shared F16 capacity must not be exhausted, and a no-data run must not start Spark or incur Spark cost. Do not leave two options open.
- `ctrl` seed rows must use the same `pl_name` as the chosen pipeline. `pl_name` equals the pipeline name. One active node belongs to one `pl_name`.
- Partner pipeline JSON may change. It is not in production. Keep the `NO_DATA` contract, timeout, retry, notebook parameters, sequential ForEach, `If_HasWork`, and the rule that a failed child is not a success. Do not add a Switch.
- A Fabric runtime runbook for a later DEV run, covering a no-data case and a has-data case. Stop before any Fabric DEV step.

### Out of scope

- Creating a notebook. Do not invent a notebook name, a notebook GUID, a host, or a credential. Do not store a notebook GUID in `ctrl`.
- Running a pipeline on Fabric, `docker compose`, or a local capacity.
- `notebooks_lgc/` and task `20261112-enr-poi-append-to-merge`.
- Changing a table column, grain, or key. Do not infer source row counts.
- A commit, push, or merge.

## Repository facts the layout must use

- Template: `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json`. `Get_Config_4Run` filters `is_active = 1` and `src_tbl = 'partner_raw_data'`. ForEach is sequential. `If_HasWork` calls activity `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` with `src_tbl` fixed to `partner_raw_data`. There is no Switch. `NO_DATA` is the false branch (`Set_Msg_Skip` only).
- The same `pl_name` also has config rows for `brz_3rd_crawler_poi_stream`, `cms_raw_data` (four targets), and `brz_enrichment_result` (two targets). Those sources are not in the ForEach. `docs/context/CTRL_TABLES_CONTEXT.md` records `nb_name` NULL for the CMS and enrichment rows. Partner extract rows also leave `nb_name` NULL; the pipeline activity names that notebook. NULL `nb_name` on an extract row is not proof that the notebook file is missing, and it is not a value to invent.
- Extract notebook files under `notebooks/`: `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`, `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb`, `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb`.
- Transform notebook files: `NB_00_ORCHES_SLV_TO_ENR.ipynb` for `PL_VV_TRANS_SLV_TO_ENR_15M`, and `NB_00_ORCHES_SLV_TO_GLD.ipynb` for `PL_VV_TRANS_SLV_TO_GLD_30M`. Enrichment JSON calls `NB_00_ORCHES_SLV_TO_ENR_15P` after a binding check. It always starts the notebook when the binding is present. Gold has no pipeline JSON.
- The only notebook id embedded in pipeline JSON today is the partner activity in the FL_00 export. Do not copy that id onto another activity. A new notebook activity whose Fabric id is not already in the repo uses a parameter binding that fails closed when the id is empty or a placeholder. Do not invent the id.
- Activity names are globally unique. `dependsOn` points only at an activity in the same list. Every notebook activity has an explicit timeout, retry, and parameter map. `run_id` may be an empty string. `pl_name` is the pipeline name stored in `ctrl`.
- Rule `.cursor/rules/20-data-pipeline.mdc` says other sources stay outside FL_00 and FL_00 must not gain a Switch. The user allows the partner template to change because it is not in production. The chosen layout still keeps the `NO_DATA` contract and no Switch.

## Acceptance criteria

- Pipeline JSON and the `ctrl` seed match the single layout recorded in `decision.md`. A source with no notebook has no activity. Architecture names that gap when it applies.
- Each notebook activity has a timeout, a retry, and a parameter map. Activity names do not collide. `dependsOn` points only at an activity in the same scope. A failed child is not reported as success. `NO_DATA` does not start Spark.
- `python scripts/vv.py verify <task-id>` passes before review.
- Reviewers: `fabric-pipeline-reviewer` and `risk-gate`. Add `sql-data-reviewer` because the diff includes pre-check SQL. Add `spark-runtime-reviewer` only if the diff edits a notebook.

## Constraints

- Do not copy credentials, hosts, or notebook GUIDs into `ctrl`.
- Do not infer source row counts.
- Do not run the pipeline on Fabric in this task.
- Main model for this task is Grok 4.7 medium. Architect, author, and author_proposal lanes use the user-approved exception `claude-fable-5-2` at effort medium (2026-11-17). Review stays `gpt-5.6-sol` medium. If the CLI rejects `claude-fable-5-2`, stop. Do not fall back to Opus.

## Classification rationale

- Complexity: high. The change spans extract and two transform cadences, and the layout has material alternatives.
- Risk: high. A wrong skip stalls freshness; overlapping notebook runs can exhaust shared F16 capacity; retry and child-failure behavior must stay fail-closed. Not critical: the change does not itself rewrite table grain or keys.
- Architecture: required. Pipeline orchestration changes, and more than one layout meets the capacity and no-Spark criteria (`design_tradeoffs`).
- Evidence: not required. The pre-check contract and config rows are already in the repo. Correctness of the JSON and seed does not depend on source row counts.
- Runtime proof: required for the later Fabric DEV check that `NO_DATA` does not start Spark and that a has-data run calls the notebook. This task writes the runbook and stops before that step.
- Reviewer routing: `fabric-pipeline-reviewer` for expressions, pre-check, ForEach, timeout, retry, and failure propagation; `sql-data-reviewer` for the pre-check SQL text; `risk-gate` because risk is high. `spark-runtime-reviewer` only if a notebook file changes.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Model lane | Main giữ Grok 4.7 medium (`models.main.actual=grok-4.7`). Ba lane Claude Opus 5.5 của task này chạy Claude Code Fable 5.2, effort medium: EX-ARCH role architect, EX-AUTHOR role author, EX-PROPOSAL role author_proposal. kind `model_override`, runtime `claude-code-extension`, approved_by user, approved_on 2026-11-17. Review giữ gpt-5.6-sol medium. CLI không nhận `claude-fable-5-2` thì dừng, không đổi về Opus. | Người dùng, 2026-11-17 | 2026-11-17 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: PASS
size: 57287 bytes

## FILES

- architecture.md | 57287 bytes | large: use toc/show
- decision.md | 1577 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/architect.md | 13188 bytes
- request.md | 6606 bytes
- resume.md | 90 bytes | placeholder
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 2481 bytes

## NEXT

python scripts/vv.py run-gate 20261117-pipeline-precheck-flows
