# Architect handoff: 20261013-3p-extract-from-raw-payload

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

Read:

- `.ai/tasks/20261013-3p-extract-from-raw-payload/task-state.yaml`
- `.ai/tasks/20261013-3p-extract-from-raw-payload/request.md`
- `.ai/tasks/20261013-3p-extract-from-raw-payload/decision.md`
- `.ai/tasks/20261013-3p-extract-from-raw-payload/evidence/`
- Relevant source and context files

Produce only `.ai/tasks/20261013-3p-extract-from-raw-payload/architecture.md`. In an interactive handoff, write that file directly. When an automated execution contract requests structured output, do not edit the repository; return the complete document through that contract so the deterministic runner can persist it.

The first non-blank line must be `RESULT: PASS` or `RESULT: EVIDENCE_REQUIRED`. Define scope, non-goals, invariants, state ownership, grain and keys, ordering, transaction/commit boundaries, idempotency, concurrency, retry/recovery, partial-failure behavior, observability, security, rollout, rollback/forward recovery, implementation plan, and verification strategy. Compare material design alternatives and explain the selected trade-off.

If evidence is missing, list exact probes and the decisions blocked by each probe. Do not implement code, update task state, or fill gaps with assumptions.
