## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`
- Risk gate: completed

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `GATE-004` — P1 — `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb:959`: `assert_rule_sql()` constructs `proj_cn` but never evaluates it in the executed query, allowing malformed-array and projected-field cast regressions in `ARRAY_PROJECT` to pass the pre-read self-check. Add executed fixtures using `proj_cn` for malformed-array and invalid-field-cast inputs, each expecting the error condition to be `true`.

## P2/P3

Count: 0
