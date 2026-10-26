# VSVN Agent Constitution

Shared source of truth for Cursor, Claude Code, Codex, and human operators. Keep this file under 8 KB. Procedures live in `docs/agent-system/WORKFLOW.md` (statuses, classification, workflow, review routing, commands), rules, skills, and agent files. Read them only when the current step needs them.

## 1. Language policy

- English: agent definitions, rules, skills, prompts, configuration, and setup documentation; machine-readable files, keys, enums, statuses, finding IDs, logs, and error codes; task artifacts except the Vietnamese ones below; code identifiers and database metadata.
- Vietnamese: prose in `decision.md`, `runtime-runbook.md`, `problem-analysis.md`, and `proposal.md`; explanatory comments in source, notebooks, and SQL; conversation with the user.
- Commands, identifiers, paths, status tokens, and finding IDs stay in English inside Vietnamese files.

## 2. Roles and authority

| Role | Runtime | Authority |
|---|---|---|
| Main | Cursor, Grok 4.7 Medium | Sole source-code writer. Owns task state, implementation, remediation, decisions, `resume.md`, and runtime runbooks. |
| Architect | Claude Code, Claude Opus 5.5 High | Writes only the current task's `architecture.md`, including the `Main brief`, through the runner. Reads `model-design.md`; never writes model design. Never implements. |
| Author | Claude Code, Claude Opus 5.5 (effort in §3) | Through `vv.py run-author --kind` only, on Main's request: writes `problem-analysis.md`, `proposal.md`, `model-design.md`, or `runtime-runbook.md`. Never implements. |
| Requirements Analyst | Claude Code, Claude Opus 5.5 Medium | Business analysis on the user's request: writes only the task's `requirements-analysis.md`. Never writes `architecture.md` or replaces the Architect. |
| Review Coordinator and specialists | Codex, GPT-5.6 Sol Medium | Read-only review; the consolidated result goes under `reviews/`. Never fixes code. |
| Local Verifier | `python scripts/vv.py verify` | Deterministic validation. |
| External Gate Runner | `python scripts/vv.py run-gate` / `run-author` | Calls the configured CLI non-interactively, validates structured output and repository immutability, persists the owned artifact, and updates state on behalf of Main. |
| User | Fabric DEV and Git | Runs probes and runbooks, accepts risk, commits and merges. |

- Single code writer plus explicit artifact ownership. Only Main edits source, notebooks, pipelines, schemas, deployment configuration, and `task-state.yaml`.
- There is no `writer: claude` mode. A per-task role or model exception exists only as a user-approved `exceptions` entry in `task-state.yaml`, mirrored in `decision.md`.

## 3. Model policy

- Main: Grok 4.7, `medium` (user approved 2026-10-09). Architect: Claude Opus 5.5, `high`. Review: `gpt-5.6-sol`, `medium` (user approved 2026-10-08). Author: Claude Opus 5.5, `high` for `--kind proposal` (`models.author_proposal`), `medium` for `--kind analysis`, `model`, and `runbook` (`models.author`). Requirements Analyst: Claude Opus 5.5, `medium`.
- Lanes (user approved 2026-10-20): business analysis is the Requirements Analyst, problem analysis is `--kind analysis`, solution proposal is `--kind proposal`, model design is `--kind model`, and architecture is the Architect. Main does not author them.
- Record actual models in `task-state.yaml`. Do not silently substitute. On fallback or unavailability, stop the gate and report it.
- Change models only after the agent evaluation suite or a recorded user-approved exception.

## 4. Context discipline

1. Start every task step with `python scripts/vv.py context <task-id>`.
2. Read files over 20 KB by section or cell (`vv.py toc`, `vv.py show`). Read a file whole only when it is small or the step edits most of it.
3. Do not read `notebooks_lgc/`, `docs/context/3p-google/*.txt`, `.ai/tasks/*/evidence/context/`, `pipelines/*/manifest.json`, or other tasks' artifacts unless the request names them.
4. Reference context by path and section. Never copy context files into a task.
5. One chat per phase. End each phase by overwriting `resume.md`.

## 5. Gates and severity

- Statuses, gate results, transitions, and round caps are defined in `docs/agent-system/WORKFLOW.md` and enforced by `vv.py`.
- `PASS` is never valid while required evidence is missing or a P0/P1 finding is unresolved.
- P0: data loss or corruption, irreversible state divergence, or non-idempotent behavior with material impact. P1: runtime failure, broken recovery, locking, or watermark behavior, serious performance risk, or an architecture-rule violation. P2: maintainability, testability, observability, or convention. P3: minor clarity.
- Finding dispositions in `decision.md`: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## 6. Data and runtime evidence

- Never infer unknown runtime data characteristics.
- Main writes probes under `.ai/tasks/<task-id>/evidence/probes/`, and the user runs them in Fabric DEV.
- Results go under `evidence/results/` without personal data. Samples are limited to 50 rows.
- Reviewers may return `EVIDENCE_REQUIRED` with an exact probe instead of guessing.

## 7. VSVN platform invariants

- Microsoft Fabric F16 per environment; capacity is shared with Eventstream, Copy Job, and the SQL analytics endpoint.
- Bronze, silver, and gold are separate Lakehouses in the same workspace: `lh_vv_bronze`, `lh_vv_silver`, and `lh_vv_gold`.
- Ingestion: Event Hub -> Eventstream -> bronze. Transformation: Spark SQL/PySpark notebooks. Orchestration: Fabric Data Pipeline.
- Batch cadence is 10-15 minutes; source-to-serving SLA is 30-60 minutes; `PL_VV_TRANS_SLV_TO_ENR_15M` runs every 15 minutes.
- Gold exposes data and may apply business logic that belongs only to that gold table. Shared business decisions, canonical entities, reusable rules, and intermediate tables belong in silver. Gold does not read other gold.
- Silver prefixes: `slv_pn_` for partner and `slv_3p_` for third party. Gold prefix: `gld_`.
- The POI identifier is `poi_id`. It never includes language. Do not use `poi_uid`.
- Third-party `poi_id = uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`).
- Partner `poi_id = uuid_format(md5(concat(id, 'partner')))` 8-4-4-4-12. `slv_pn_business_services.id` or `slv_pn_business_service_i18ns.business_service_id`. uuid_md5(id, lit('partner')): NB_SLV_POI_ENTITY_NON_ENRICH, NB_ENR_POI_INFO, NB_GLD_SRV_POI_MULTI_LANG.
- Notebook roles follow `docs/context/02_NAMING_CONVENTION.md`. `NB_LIB_*` is a `%run` library. `NB_EXTRACT_*_CDC_BRZ_TO_SLV` is one extract notebook per raw source. `NB_00_ORCHES_*` is the shared orchestrator, selected by `p_pl_name`, with two copies in the repo: `NB_00_ORCHES_SLV_TO_ENR_15P` and `NB_00_ORCHES_SLV_TO_GLD`. `NB_<UPPER(trg_tbl)>` is one node notebook per target table. `NB_SETUP_*` is a manual one-shot setup notebook. `NB_SETUP_INITIAL_DDL` builds an empty environment and `NB_CREATE_DDL` patches an existing one; every DDL or configuration-insert change updates both (§2.1). No deeper orchestration tier.
- `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` has no Switch. Its notebook activity is `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` with `partner_raw_data` fixed. `run_id` may be empty so the notebook uses `exec_id` and the other activity parameters. Other sources are handled by a script outside this pipeline.
- Pipeline pre-check reads `ctrl_mng_pipeline_config` and `ctrl_mng_watermark`, then inspects `_delta_log` through `Files/_delta_src/<table>`. No new data means no Spark startup.
- Control-table semantics belong in `docs/context/CTRL_TABLES_CONTEXT.md`. If that file is missing or incomplete, changes to `ctrl_*` require evidence and user action.

## 8. Prohibited actions

- Agents do not commit, push, merge, or rewrite Git history.
- Do not delete or rename Fabric tables without rollback and forward-recovery steps in `runtime-runbook.md`.
- Do not place secrets, tokens, personal data, or production extracts in task artifacts.
- Do not bypass required evidence, architecture, review, or runtime gates.
- Do not modify agent-system configuration unless the user explicitly requests an agent-system change.
