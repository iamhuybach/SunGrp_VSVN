## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `spark-runtime-reviewer`, `sql-data-reviewer`, `state-correctness-reviewer`
- Risk gate: not required
- Carry-over: `STATE-002` fixed; `STATE-001` unresolved

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `STATE-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:3070`: A refreshed lease can still expire during a long `ALTER` or `MERGE`, allowing another run to acquire the lock before the first run commits. Fix: use non-stealable ownership with explicit stale-lock recovery or require exclusive paused execution for the entire patch cell.
- `SQL-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:3057`: A sole gold-hours edge with `is_active = NULL` passes the pre-check, after which the DDL commits but the MERGE skips the row and fails post-validation. Fix: before any write, require exactly one edge whose `is_active` is `0` or `1`.
- `SQL-002` — P1 — `notebooks/NB_CREATE_DDL.ipynb:3072`: An apostrophe in the selected `nb_name` produces invalid interpolated MERGE SQL after the DDL has committed. Fix: escape SQL literals or construct the MERGE source without string interpolation.

## Lower-severity findings

P2: 0; P3: 0.

Probe: group the exact gold-hours edge by `is_active` and check the selected entity template for `instr(nb_name, chr(39)) > 0`; pass only with one edge row flagged `0` or `1` and zero quoted `nb_name` values.
