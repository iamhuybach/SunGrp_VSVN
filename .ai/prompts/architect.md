# Architect handoff: {{TASK_ID}}

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

Read:

- `.ai/tasks/{{TASK_ID}}/task-state.yaml`
- `.ai/tasks/{{TASK_ID}}/request.md`
- `.ai/tasks/{{TASK_ID}}/decision.md`
- `.ai/tasks/{{TASK_ID}}/evidence/`
- Relevant source and context files

Write only `.ai/tasks/{{TASK_ID}}/architecture.md`.

The document must state one result: `PASS` or `EVIDENCE_REQUIRED`. Define scope, non-goals, invariants, state ownership, grain and keys, ordering, transaction/commit boundaries, idempotency, concurrency, retry/recovery, partial-failure behavior, observability, security, rollout, rollback/forward recovery, implementation plan, and verification strategy. Compare material design alternatives and explain the selected trade-off.

If evidence is missing, list exact probes and the decisions blocked by each probe. Do not implement code, update task state, or fill gaps with assumptions.
