## Review manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- `spark-runtime-reviewer`: `FIX_REQUIRED`
- `sql-data-reviewer`: `PASS`
- Risk gate: not required

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `SPARK-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:6967`: A failed MERGE leaves session-scoped Delta commit metadata active, so a later commit may be falsely tagged and corrupt recovery/audit attribution. Wrap the MERGE in `try/finally` and always unset `spark.databricks.delta.commitInfo.userMetadata` while preserving the original exception.
- `SPARK-002` — P1 — `notebooks/NB_CREATE_DDL.ipynb:6894`: Driver loss or hard cancellation can retain the extraction watermark lock for the hard-coded 780 minutes, exceeding the 30–60 minute SLA. Use the canonical bounded extraction-lock timeout and add a DEV cancellation/reacquisition check to the runtime runbook.

P2: 4. P3: 0.
