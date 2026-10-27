## Model and reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium`.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`.
- Risk gate: not required, not run.

## Gate verdict

`EVIDENCE_REQUIRED`

## P0/P1 findings

- `SQL-001` — **P1** — `notebooks/NB_GLD_SRV_POI_REVIEW.ipynb:99`: Duplicate rating rows or a multiplicative `multi_lang × review` join can violate the required one-row-per-`review_id` MERGE source and stop the run before writing. Fix: prove both source assumptions in Fabric DEV; if duplicates exist, remediate the source or obtain an explicit grain decision without selecting an arbitrary row.

## P2/P3

P2: 1; P3: 0.

## Required probe

Run the SQL reviewer’s combined duplicate probe for non-null `slv_3p_poi_rating.poi_id` and post-join `review_id`; pass criterion: **0 rows**.
