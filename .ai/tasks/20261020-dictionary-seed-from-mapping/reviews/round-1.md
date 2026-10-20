## Review manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — confirmed.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`.
- Risk gate: completed.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | Location | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `.ai/tasks/20261020-dictionary-seed-from-mapping/runtime-runbook.md:28` | `CREATE TABLE IF NOT EXISTS` can reuse a stale backup whose row count matches current data, making rollback restore divergent dictionary state. | Before either `DROP`, prove backup/live schema and row equivalence in both directions with explicit-column `EXCEPT ALL`, or create uniquely named backups for the execution and verify them. |
| GATE-002 | P1 | `.ai/tasks/20261020-dictionary-seed-from-mapping/runtime-runbook.md:47` | The runbook resumes the hourly pipeline before the `p_apply=true` idempotency reruns, allowing a pipeline run to race or trip the active-run guard. | Move both idempotency reruns and assertions before R10, reconfirm pause/no active run immediately beforehand, and resume only after all checks pass. |

P2/P3: **1/0**.

Probe: No additional review probe is required; the separate Fabric DEV runtime gate remains pending after these P1 fixes.
