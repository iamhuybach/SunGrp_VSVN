## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`
- Risk gate: completed

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `SPARK-001` — P1 — `notebooks/NB_ENR_POI_INFO.ipynb:241`: Removing or soft-deleting a rating, price, hours, or review row does not emit its `poi_id`, leaving stale gold values. Fix by unioning reverse-diff removal keys into the changed POIs while retaining the full-spine fallback when no baseline exists.
- `STATE-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:2331`: An existing inactive desired edge is skipped by `WHERE NOT EXISTS`, so verification and every retry fail, potentially after the DEV reset leaves gold empty. Fix by failing before mutations or deterministically reactivating exactly the three task-owned desired edges while holding the flow lock.

## Lower-severity findings

P2: 0; P3: 0.
