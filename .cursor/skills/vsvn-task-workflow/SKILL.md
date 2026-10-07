---
name: vsvn-task-workflow
description: Start, resume, route, validate, or complete a VSVN engineering task using task-state.yaml and the evidence, architecture, review, verification, and runtime gates. Use for implementation work or when asked what gate comes next. Do not use for a read-only repository question that is unrelated to a task.
---

# VSVN task workflow

1. Read `AGENTS.md` and `.ai/tasks/<task-id>/task-state.yaml`.
2. For a new task, run `python scripts/vv.py new <slug>` and fill `request.md` plus the classification.
3. Route in this order: evidence -> architecture -> implementation -> verification -> targeted review -> risk gate -> runtime.
4. Use `python scripts/vv.py transition` for status changes and `validate` after editing state.
5. At `waiting_architecture` or `reviewing`, run `python scripts/vv.py run-gate <task-id>` so the designated Claude or Codex CLI completes the gate non-interactively. Use `prompt` only for diagnosis or a user-approved manual fallback.
6. Stop at user-owned Fabric execution, risk acceptance, and merge steps.

Keep `task-state.yaml` factual. Do not mark a gate passed based on intent, a generated prompt, or an unexecuted runbook.
