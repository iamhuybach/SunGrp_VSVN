# VSVN Agent Constitution

This file is the shared source of truth for Cursor, Claude Code, Codex, and human operators.
Keep it concise. Put detailed, tool-specific procedures in rules, skills, or specialist-agent files.

## 1. Language policy

English is mandatory for:

- Agent definitions, rules, skills, prompts, configuration, and setup documentation.
- Machine-readable files, keys, enum values, status values, finding IDs, logs, and error codes.
- Task artifacts, except for `decision.md` and `runtime-runbook.md`.
- Code identifiers, table names, column names, and database metadata descriptions.

Vietnamese is mandatory for:

- `decision.md` and `runtime-runbook.md` prose.
- Explanatory comments in source code, notebooks, and SQL scripts.
- Conversation with the user.

Commands, identifiers, paths, status tokens, and finding IDs remain in English even inside Vietnamese files.

## 2. Roles and authority

| Role | Runtime | Authority |
|---|---|---|
| Main | Cursor, Grok 4.7 High | Sole source-code writer. Owns task state, implementation, remediation, decisions, and runtime runbooks. |
| Architect | Claude Code, Claude Opus 5.5 High | Reads the repository and writes only the current task's `architecture.md`. Never implements. |
| Review Coordinator | Codex, GPT-5.6 Sol High | Runs independent read-only specialist reviews and produces the consolidated review result. Never fixes code. |
| Specialist Reviewers | Codex custom agents, GPT-5.6 Sol High | Read-only review of state correctness, Spark runtime, SQL/data, or Fabric pipelines. |
| Local Verifier | `python scripts/vv.py verify` | Deterministic validation; no LLM judgment. |
| External Gate Runner | `python scripts/vv.py run-gate` | Calls the configured Claude or Codex CLI non-interactively, validates structured output and repository immutability, persists the owned artifact, and updates state on behalf of Main. |
| User | Fabric DEV and Git | Runs probes and runtime runbooks, accepts risk, and commits/merges. |

The role model is **single code writer plus explicit artifact ownership**, not a universal single writer.

- Main is the only role allowed to edit source code, notebooks, pipelines, schemas, or deployment configuration.
- Architect may edit only `.ai/tasks/<task-id>/architecture.md`. In automated mode it returns structured document content and the deterministic runner persists that exact content.
- Codex specialist reviewers are read-only. The consolidated result is captured under the current task's `reviews/` directory by the review runner or Main.
- Only Main updates `task-state.yaml`.
- There is no `writer: claude` mode.

## 3. Model policy

- Main: Grok 4.7 with `high` reasoning in Cursor. The active model must be confirmed in the model picker and recorded in `task-state.yaml`.
- Architect: Claude Opus 5.5 with `high` effort. Record the actual model in `task-state.yaml`.
- Review Coordinator and all specialist reviewers: `gpt-5.6-sol` with `high` reasoning through Codex authenticated with ChatGPT. Record the actual model in `task-state.yaml`.
- Do not silently substitute models. If a configured model is unavailable or a client falls back, stop the affected gate and report it to the user.
- Change model versions only after running the repository's agent evaluation suite or recording a user-approved exception.

## 4. Canonical task state

Every task lives at `.ai/tasks/<YYYYMMDD-slug>/` and has one machine-readable source of truth: `task-state.yaml`.

Allowed task statuses:

```text
triage
waiting_evidence
waiting_architecture
implementing
verifying
reviewing
waiting_runtime
user_decision
ready_to_merge
blocked
```

Allowed gate results:

```text
pending
pass
fix_required
evidence_required
user_decision
not_required
```

`PASS` is never valid while required evidence is missing or a P0/P1 finding remains unresolved.

## 5. Classification

Classify complexity, risk, architecture needs, and evidence needs separately. Do not use one `risky` boolean as a substitute for all four.

### Complexity signals

Use the following exact values in `task-state.yaml`:

```text
stateful_logic
concurrency
retry_recovery
partial_failure
transaction_boundaries
event_ordering
idempotency
distributed_behavior
cross_system
design_tradeoffs
cross_state_impact
runtime_proof_required
data_evidence_required
low_probability_high_impact
deep_reasoning_required
```

### Architecture is required when any of these apply

- A table grain, key, state owner, transaction boundary, or commit order changes.
- Logic moves between bronze, silver, gold, orchestration, or PostgreSQL sync.
- CDC, watermark, locking, retry/recovery, or partial-failure behavior changes.
- Pipeline or notebook orchestration structure changes.
- Multiple viable implementations have material trade-offs.
- The change spans at least three services or eight source files.

### Evidence is required when any of these apply

- Correctness depends on data distribution, uniqueness, null rates, formats, enums, or actual schemas not already captured in task evidence.
- Correctness cannot be established by repository inspection and deterministic local checks.
- A runtime failure indicates a possible data or environment cause.

### Risk levels

- `low`: no behavior change or a narrow, locally provable change.
- `medium`: bounded behavior change with straightforward rollback and local proof.
- `high`: stateful logic, concurrency, retry/recovery, event ordering, idempotency, cross-system effects, or runtime-only proof.
- `critical`: a credible path to data loss, irreversible corruption, broad production outage, or unsafe recovery.

Fast lane is derived, not manually asserted: `complexity=low`, `risk_level=low`, no behavior change, and at most two changed files.

## 6. Workflow

```text
TRIAGE
  -> EVIDENCE, when required
  -> ARCHITECTURE, when required
  -> IMPLEMENT
  -> LOCAL VERIFY
  -> TARGETED REVIEW
  -> CROSS-SYSTEM GATE, when risk is high or critical
  -> RUNTIME RUNBOOK, when runtime proof is required
  -> READY TO MERGE
```

Rules:

1. Main creates the task and classifies it before implementation.
2. Evidence precedes architecture when architecture depends on runtime data.
3. Architect defines invariants, state ownership, failure behavior, transaction boundaries, recovery, and the implementation-level design. Main invokes `python scripts/vv.py run-gate <task-id>` at `waiting_architecture`; the runner must stop on CLI, model, structured-output, or repository-immutability failure.
4. Main implements the approved architecture. Any deviation is recorded in `decision.md` before code changes continue.
5. Local verification must pass before LLM review.
6. At `reviewing`, Main invokes `python scripts/vv.py run-gate <task-id>`. Review Coordinator invokes only relevant specialist reviewers. First-round specialists work independently and do not read each other's findings. The runner rejects an incomplete reviewer manifest or an omitted required risk gate.
7. Round 2 checks unresolved P0/P1 findings and regressions caused by fixes.
8. A maximum of two verification/remediation rounds and two review rounds is allowed. Exceeding a cap routes to `user_decision`.
9. Runtime failures are classified as `code`, `data`, `architecture`, or `unclear`; route respectively to implementation, evidence, architecture, or user decision.
10. Only the user may accept risk and mark a task ready for merge after required runtime verification.

## 7. Review routing

- `state-correctness-reviewer`: owns state-transition correctness across CDC, MERGE commit order, watermark, locks, retry/recovery, event ordering, partial failure, idempotency, and cross-system state. It reviews crash timelines and durable-state invariants, not SQL statement construction.
- `spark-runtime-reviewer`: PySpark, Fabric notebook contracts, concurrency, Delta writes, logging, and F16 performance.
- `sql-data-reviewer`: owns statement-level correctness for Spark SQL, Delta DDL, SQL/Delta MERGE match keys and clauses, MERGE-source uniqueness, deterministic rerun behavior, joins, windows, types, grain, and PostgreSQL SQL. Route it whenever a SQL/Delta MERGE implementation is in scope, including retry scenarios reviewed for state correctness.
- `fabric-pipeline-reviewer`: pipeline expressions, parameters, pre-check, Switch, dependencies, ForEach concurrency, timeout/retry, failure propagation, and notebook exit contracts.
- `risk-gate`: cross-system invariants and unresolved high-impact risks after specialist review.

Severity is impact-based:

- P0: data loss/corruption, irreversible state divergence, or non-idempotent behavior with material impact.
- P1: runtime failure, broken recovery/locking/watermark behavior, serious performance risk, or architecture-rule violation.
- P2: maintainability, testability, observability, or convention issue.
- P3: minor clarity or consistency issue.

Finding dispositions in `decision.md` are: `fixed`, `accepted-risk`, `rejected-false-positive`, or `backlog`.

## 8. Data and runtime evidence

- Never infer unknown runtime data characteristics.
- Main writes probes under `.ai/tasks/<task-id>/evidence/probes/` and the user runs them in Fabric DEV.
- Results go under `evidence/results/` and must not include personal data. Limit samples to 50 rows.
- Reviewers may return `EVIDENCE_REQUIRED` with an exact probe instead of guessing.
- Runtime evidence is required for changes whose correctness cannot be proven locally.

## 9. VSVN platform invariants

- Microsoft Fabric F16 per environment; capacity is shared with Eventstream, Copy Job, and the SQL analytics endpoint.
- Bronze, silver, and gold are separate Lakehouses in the same workspace: `lh_vv_bronze`, `lh_vv_silver`, and `lh_vv_gold`.
- Ingestion: Event Hub -> Eventstream -> bronze. Transformation: Spark SQL/PySpark notebooks. Orchestration: Fabric Data Pipeline.
- Batch cadence is 10-15 minutes; source-to-serving SLA is 30-60 minutes; silver-to-gold POI runs hourly.
- Gold is expose/sync only. Cleansing, normalization, enrichment, canonical entities, reusable business rules, and intermediate tables belong in silver.
- Silver prefixes: `slv_pn_` for partner and `slv_3p_` for third party. Gold prefix: `gld_`.
- The POI identifier is `poi_id`. It never includes language. Do not use `poi_uid`.
- Third-party `poi_id = uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`).
- Partner `poi_id = uuid_format(md5('partner_portal' || business_service_id))`. The formula is retained for a future notebook. No current notebook applies it.
- Notebook roles follow `docs/context/02_NAMING_CONVENTION.md`. `NB_LIB_*` is a `%run` library. `NB_EXTRACT_*_CDC_BRZ_TO_SLV` is one extract notebook per raw source. `NB_00_ORCHES_*` is the shared orchestrator, selected by `p_pl_name`. `NB_<UPPER(trg_tbl)>` is one node notebook per target table. `NB_SETUP_*` is a manual one-shot setup notebook. `NB_CREATE_DDL` creates the control tables. No deeper orchestration tier.
- `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` has no Switch. Its notebook activity is `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` with `partner_raw_data` fixed. `run_id` may be empty so the notebook uses `exec_id` and the other activity parameters. Other sources are handled by a script outside this pipeline.
- Pipeline pre-check reads `ctrl_mng_pipeline_config` and `ctrl_mng_watermark`, then inspects `_delta_log` through `Files/_delta_src/<table>`. No new data means no Spark startup.
- Control-table semantics belong in `docs/context/CTRL_TABLES_CONTEXT.md`. If that file is missing or incomplete, changes to `ctrl_*` require evidence and user action.

## 10. Commands

Run from repository root:

```text
python scripts/vv.py new <slug>
python scripts/vv.py validate <task-id>
python scripts/vv.py transition <task-id> <status>
python scripts/vv.py prompt <task-id> architect
python scripts/vv.py prompt <task-id> review --round N
python scripts/vv.py external-doctor
python scripts/vv.py external-smoke
python scripts/vv.py run-gate <task-id> [--round N]
python scripts/vv.py verify <task-id>
python scripts/vv.py doctor
```

## 11. Prohibited actions

- Agents do not commit, push, merge, or rewrite Git history.
- Do not delete or rename Fabric tables without rollback and forward-recovery steps in `runtime-runbook.md`.
- Do not place secrets, tokens, personal data, or production extracts in task artifacts.
- Do not bypass required evidence, architecture, review, or runtime gates.
- Do not modify agent-system configuration unless the user explicitly requests an agent-system change.
