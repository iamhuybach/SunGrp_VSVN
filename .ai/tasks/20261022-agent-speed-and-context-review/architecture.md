# Architecture

RESULT: PASS

## Main brief

### Decision

The locked design is `.ai/tasks/20261022-agent-speed-and-context-review/reviews/agent-speed-review.md`, section `## 8. Mục sửa`, rows 1–15. Each row names one change sentence and one check. Item 9 is closed: do not change the round-2 manifest, `scripts/agent_runner.py`, `.ai/prompts/review.md`, `WORKFLOW.md` §6, `_architect_appendix`, the `fabric-pipeline-reviewer` rule, or `AGENT_PROMPT_SAMPLES.md` A18. Keep `PL_VV_TRANS_SLV_TO_ENR_15P` and apply row 4 as written. EXC-02 applies only to this task.

### Invariants Main must preserve

Do not change model id or effort in `.claude/settings.json` or `.codex/config.toml`. Do not call `run-author` or `run-gate`. Do not edit notebooks, pipeline JSON, or tests except the `elapsed_seconds` test for row 15. Do not edit `scripts/agent_runner.py`.

### Edit list

The edit list is the table in `reviews/agent-speed-review.md` section 8, rows 1–15. Apply each change sentence. The done-when column is that table's `Cách kiểm tra` column.

### Order and stop points

Record the lock in `decision.md` before editing. Then transition to `implementing`. After the fifteen edits, run the table checks and `python scripts/vv.py validate 20261022-agent-speed-and-context-review`. Stop for the Opus 5.5 high diff review. Do not call `run-gate`.

### Tests and verification

Row 15 adds `elapsed_seconds` to the `reviews/round-N.json` snapshot test in `tests/test_vv.py`. `python scripts/vv.py verify 20261022-agent-speed-and-context-review` must pass. The other rows use the grep and `vv.py show` checks in the table.

### Read only if needed

`reviews/agent-speed-review.md` → `## 8. Mục sửa` and `## 9. Câu hỏi cần chốt`.
