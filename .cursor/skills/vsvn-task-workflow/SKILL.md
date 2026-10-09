---
name: vsvn-task-workflow
description: Start, resume, route, validate, or complete a VSVN engineering task using task-state.yaml and the evidence, architecture, review, verification, and runtime gates. Use for implementation work, when asked what gate comes next, or when the operator asks how to run an existing task's probes or runtime runbook. Do not use for a read-only repository question that is unrelated to a task.
---

# VSVN task workflow

1. Read `AGENTS.md` and `.ai/tasks/<task-id>/task-state.yaml`.
2. For a new task, run `python scripts/vv.py new <slug>` and fill `request.md` plus the classification.
3. Route in this order: evidence -> architecture -> implementation -> verification -> targeted review -> risk gate -> runtime.
4. Use `python scripts/vv.py transition` for status changes and `validate` after editing state.
5. At `waiting_architecture` or `reviewing`, run `python scripts/vv.py run-gate <task-id>` so the designated Claude or Codex CLI completes the gate non-interactively. Use `prompt` only for diagnosis or a user-approved manual fallback.
6. Stop at user-owned Fabric execution, risk acceptance, and merge steps.
7. End the turn with the `Turn closeout` sections from `.cursor/rules/00-main-orchestrator.mdc`.

Keep `task-state.yaml` factual. Do not mark a gate passed based on intent, a generated prompt, or an unexecuted runbook.

## Build the closeout

Use the same steps when the operator asks how to run an existing `task-id`.

1. Read `task-state.yaml` for `status`, gates, and `open_findings`. Read the open items in `decision.md`.
2. At `waiting_evidence`, read each probe under `evidence/probes/`, excluding `README.md`, that has no result under `evidence/results/`. Treat `.sql` and `.py` variants with the same stem as one probe and say which one to run. Each probe becomes one `Bạn cần chạy` block: where it runs, how to run it, parameters, the pass/fail criterion, and the result path.
3. At `waiting_runtime`, read `runtime-runbook.md`. Map its sections to the block:

   | `runtime-runbook.md` section | Closeout content |
   |---|---|
   | `Phạm vi và môi trường`, `Điều kiện tiên quyết` | Environment, item to run, prerequisites |
   | `Baseline trước khi chạy` | Step 1: capture the baseline |
   | `Các bước thực hiện` | Numbered run steps with parameters |
   | `Kiểm tra kết quả` | Expected correct result |
   | `Chạy lại để kiểm tra idempotency` | Rerun step and the expected unchanged counts |
   | `Kiểm tra log và watermark` | Control-log and watermark queries and the expected values |
   | `Rollback và forward recovery` | What to do when a check fails |
   | `Kết quả người dùng ghi nhận` | Where to paste the sanitized output |

   Skip an empty section. Do not fill it in from memory. If a step needs a value the runbook lacks, update the runbook or ask for the value in `Agent đang chờ`.
4. At `user_decision`, write every pending choice as one `decision` or `accept-risk` request with its options.
5. Uncommitted changes add one `commit` request that lists the changed files. Main never commits.
6. If nothing is pending, or only `commit` is pending, write `Lượt này đã xong trong repository.`
