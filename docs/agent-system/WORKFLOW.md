# VSVN Agent Workflow

Detailed procedures referenced by `AGENTS.md`. Read only the sections required by the current phase.

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
python scripts/vv.py toc <path>
python scripts/vv.py show <path> <anchor> [--max-lines N]
python scripts/vv.py context <task-id> [--phase P] [--max-lines N]
python scripts/vv.py materialize <task-id> [--source F] [--write]
python scripts/vv.py closeout <task-id>
python scripts/vv.py verify <task-id> --full
python scripts/vv.py run-author <task-id> --kind proposal|runbook
```

## Phases and context budgets

| Phase | Default read set | Budget (≈ tokens) |
|---|---|---:|
| any | Rule, `AGENTS.md` core, skill descriptions | ≤ 3.5k |
| triage | Request text, `WORKFLOW.md` §Classification and §Review routing, named context sections | ≤ 15k |
| evidence | Context pack, probe headers, results | ≤ 15k |
| implement | Context pack (≤ 400 lines), Main brief, edit-list cells/sections | ≤ 35k |
| remediate | Context pack (P0/P1 rows), cited `file:line` ranges | ≤ 20k |
| runtime / close | Context pack, closeout skeleton | ≤ 10k |

## Task artifacts

| Artifact | Owner | Language | Contract |
|---|---|---|---|
| `resume.md` (new, task root) | Main | English | Overwritten at every stop. At most 40 lines. Sections: `Status`, `Done this session`, `Next action`, `Read next` (path + anchor), `Waiting on`. |
| `architecture.md` → `## Main brief` (new section) | Architect, through the runner | English | At most 14,000 characters, directly after the `RESULT:` line. Uses only `###` sub-headings. Contents: Decision; Invariants Main must preserve; Edit list (`# \| file \| anchor \| change \| done-when`); Order and stop points; Tests and verification; Read only if needed (full-document headings → edit rows). |
| `decision.md` → `## Quyết định hiện hành` (new ledger) | Main | Vietnamese | Directly after `# Quyết định`. Table `ID \| Chủ đề \| Quyết định hiện hành \| Nguồn (mục) \| Ngày`. A superseded row is edited in place; details are appended under `## Lịch sử quyết định`. |
| `task-state.yaml` → `exceptions` (new, optional) | Main | English | Typed list (SOL-09). Replaces free-form `model_policy_exception` blocks for new tasks. |
| `reviews/round-N.json` | Review runner | Machine-readable | Written by `run-gate` after each review round: verdict, findings, and SHA-256 of the scoped non-task files reviewed. Round 2 uses it to embed the round-1 P0/P1 carry-over and the files changed since round 1. Never edited by hand. |
| `proposal.md` | Author lane, through the runner | Vietnamese | Proposal for the user. `decision.md` ledger rows point to it. |
| `handoffs/author-input.md` | Main | English, user comments verbatim | At most 60 lines: user comments verbatim, files and anchors the author may read, constraints. |
