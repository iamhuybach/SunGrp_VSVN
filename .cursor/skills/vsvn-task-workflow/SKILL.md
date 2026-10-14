---
name: vsvn-task-workflow
description: Start, resume, route, validate, or close a VSVN engineering task through task-state.yaml and its evidence, architecture, review, verification, and runtime gates. Use for task work, when asked which gate comes next, or when the operator asks how to run an existing task's probes or runtime runbook. Do not use for a read-only repository question that is unrelated to a task.
---

# VSVN task workflow

## Phases

One chat per phase. Every phase starts with `python scripts/vv.py context <task-id>` (a new task runs `python scripts/vv.py new <slug>` first).

| Status | Phase | Read after the context pack | Ends with |
|---|---|---|---|
| `triage` | triage | `docs/agent-system/WORKFLOW.md` §Classification and §Review routing; context-map sections the prompt names | probes, `run-gate` architecture, or a fast-lane edit |
| `waiting_evidence` | evidence | probe headers and new results | ledger interpretation; `run-gate` or another probe |
| `implementing`, `verifying` | implement | Main brief; edit-list anchors through `vv.py show` | verify PASS; `run-gate` review |
| `implementing` after FIX_REQUIRED | remediate | P0/P1 rows; cited `file:line` | verify PASS; next review round |
| `waiting_runtime` | runtime | runbook sections | closeout |
| `user_decision` | closeout | ledger; open findings | closeout |

## Steps

1. Use `python scripts/vv.py transition` for status changes and `validate` after editing state.
2. At `waiting_architecture` or `reviewing`, run `python scripts/vv.py run-gate <task-id>`. Use `prompt` only for diagnosis or a user-approved manual fallback. Never use Cursor subagents for review. Never stage files as a handoff.
3. Save `FILE:` or `SKILL_FILE:` blocks with `python scripts/vv.py materialize <task-id>` (dry run), then `--write`.
4. Keep `task-state.yaml` factual. Do not mark a gate passed based on intent, a generated prompt, or an unexecuted runbook. Record role or model exceptions only in `exceptions`, with the user's approval date, and mirror them in `decision.md`.
5. In `decision.md`, edit the `Quyết định hiện hành` row in place, copying the decision text verbatim from its source section. Append details under `Lịch sử quyết định`.
6. Before stopping, overwrite `resume.md` (≤ 40 lines, English): `Status`, `Done this session`, `Next action`, `Read next` (path + anchor), `Waiting on`.

## Runtime runbook

When runtime proof is required, `runtime-runbook.md` is Vietnamese and has these sections: `Phạm vi và môi trường`, `Điều kiện tiên quyết`, `Baseline trước khi chạy`, `Các bước thực hiện`, `Kiểm tra kết quả`, `Chạy lại để kiểm tra idempotency`, `Kiểm tra log và watermark`, `Rollback và forward recovery`, `Kết quả người dùng ghi nhận`. Take parameter values from the notebook parameter cell or the pipeline JSON. If a value is unknown, ask for it; do not guess.

## Build the closeout

Run `python scripts/vv.py closeout <task-id>`, then edit only the summary lines. The four sections, in Vietnamese, in this order, with these exact headings:

1. `Đã làm`: what changed, the current `status` and gates in one line, and the files the operator must open, as paths.
2. `Bạn cần chạy`: one block per operator-run step:
   - Environment and the exact item to run.
   - Parameters with exact values.
   - Numbered steps in run order.
   - Expected result as a pass/fail criterion.
   - Where to paste sanitized output: an exact path under `evidence/results/`, or the runbook's `Kết quả người dùng ghi nhận`. Restate the limits: at most 50 rows, no personal data, no secrets.
   - When the runbook has them: the rerun/idempotency check, the control-log and watermark check, rollback, and forward recovery.

   Write `Không có.` when there is nothing to run.
3. `Agent đang chờ`: one request per line, typed `probe`, `decision`, `accept-risk`, `runtime-result`, or `commit`. A decision lists the options and what Main does for each. A commit request lists the changed files. Write `Không có.` when nothing is pending.
4. `Kết thúc`: when sections 2 and 3 are `Không có.`, or the only open item is `commit`, write `Lượt này đã xong trong repository.` Otherwise name the next `status` and the reply that lets Main resume.

Rules:

- At `waiting_evidence` or `waiting_runtime`, a file path is not an instruction. Write the ordered steps and the paste-back data inline.
- Probe files and `runtime-runbook.md` are the full source; the answer is the condensed list. If they disagree, fix the file first.
- Map the runbook sections in the order above. Skip an empty section; do not fill it in from memory.
- At `user_decision`, write each pending choice as one `decision` or `accept-risk` request with its options.
- Uncommitted changes add one `commit` request. Main never commits.
- Never claim that a Fabric DEV step ran.
