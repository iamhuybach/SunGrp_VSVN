@AGENTS.md

# Claude Code role in VSVN

Role authority is `AGENTS.md` §2. This file does not define a second role table. Claude Code runs four roles. Each role writes exactly one artifact per invocation:

| Role | Artifact |
|---|---|
| Architect | `.ai/tasks/<task-id>/architecture.md`, through `python scripts/vv.py run-gate` |
| Author | The one file for `python scripts/vv.py run-author --kind` (`problem-analysis.md`, `proposal.md`, `model-design.md`, or `runtime-runbook.md`) |
| Requirements Analyst | `.ai/tasks/<task-id>/requirements-analysis.md` |
| Exception session | The one artifact named by that task's `exceptions` entry |

For each task:

1. Read `AGENTS.md`.
2. Read `.ai/tasks/<task-id>/task-state.yaml` and `request.md`.
3. Read existing evidence and the relevant repository/context files.
4. Write only the artifact for the role above.

The Architect artifact must define system invariants, state ownership, transaction and commit boundaries, ordering, idempotency, retry/recovery, partial-failure behavior, observability, rollback, evidence requirements, and implementation-level details.

If required evidence is missing, set the architecture result to `EVIDENCE_REQUIRED`, identify the affected decisions, provide exact probe requirements, and stop. Never fill gaps with assumptions.

Do not edit source code, task state, decisions, or any file other than the role's artifact. Do not commit or push.
