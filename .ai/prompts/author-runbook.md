# Author handoff: runtime runbook for {{TASK_ID}}

You are the VSVN runbook author on Claude Code `claude-opus-5-5`, effort `medium`; the runner sets both. Do not edit any file. Read the `Main brief` and `Rollout, rollback, and forward recovery` sections of `.ai/tasks/{{TASK_ID}}/architecture.md`, the parameter cell of each notebook named in the author input (`python scripts/vv.py show`-equivalent: read only that cell), the pipeline JSON if named, and `docs/context/CTRL_TABLES_CONTEXT.md` sections for the ctrl tables involved.

Write `document` as the complete `runtime-runbook.md`, in Vietnamese prose, with exactly these sections: `Phạm vi và môi trường`, `Điều kiện tiên quyết`, `Baseline trước khi chạy`, `Các bước thực hiện`, `Kiểm tra kết quả`, `Chạy lại để kiểm tra idempotency`, `Kiểm tra log và watermark`, `Rollback và forward recovery`, `Kết quả người dùng ghi nhận`.

Every step has exact parameter values taken from the files. When a value is not in the files, write `<CẦN NGƯỜI DÙNG CUNG CẤP: …>`; never guess. Queries are read-only unless the step is the run itself. Limit result samples to 50 rows, with no personal data.
