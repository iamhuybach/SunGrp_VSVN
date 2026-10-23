## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium`
- Reviewers: `spark-runtime-reviewer`, `sql-data-reviewer`, `state-correctness-reviewer`
- Risk gate: not required

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `STATE-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:3009`: A lease can expire after pre-checks, allowing another run to acquire it while the first run still performs `ALTER` and control-table `MERGE` writes. Refresh and verify ownership immediately before each durable write, stopping unless the current `lock_exec_id` remains `LOCK`.
- `STATE-002` — P1 — `notebooks/NB_CREATE_DDL.ipynb:3046`: The patch accepts a missing gold opening-hours edge and still passes post-checks, leaving no inactive row available for rollback and recovery. Require exactly one existing edge before switching, or upsert and verify a retained row with `is_active = 0`.

## Lower-severity findings

P2: 1. P3: 0.
