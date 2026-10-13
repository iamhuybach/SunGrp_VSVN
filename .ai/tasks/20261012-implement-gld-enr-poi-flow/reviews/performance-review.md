Model: gpt-5.6-sol
Effort: medium

## spark-runtime-reviewer

### 1. Correct processing

#### SPARK-001 — P1

- **File / cell or function:** `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`, `NodeContext.changed()`; consumers in `notebooks/NB_ENR_POI_INFO.ipynb` and `notebooks/NB_ENR_POI_COORDINATE.ipynb`; edge advancement in `advance_edges()`.
- **Extra work or wrong step:** `changed()` only computes `current.subtract(old)`. Rows present in the baseline but absent from the current satellite version are therefore invisible. A node can append zero rows, report `SUCCESS`, and advance its edges past the deletion-like change.
- **Correctness impact:** Info or coordinate may omit the required rebuilt current-state row permanently until a force run or another change touches the same key. This can produce the wrong append set.
- **Change direction:** Detect differences in both directions—`current EXCEPT old` plus `old EXCEPT current`—inside the existing time-travel error boundary, derive distinct dirty keys, and rebuild from the current snapshot. If deletion of a base row cannot be represented under the retained append-only schema, fail the node and do not advance the affected edge until an explicit policy exists. Add regression coverage for an old-only satellite row.

### 2. Speed

No P0/P1 speed finding was established. The observed DEV timings—169 seconds for the first run, 39 seconds for `NO_DATA`, and 84–102 seconds for force runs—do not by themselves establish a serious F16 performance risk.

The reviewer counted three P2 observations and no P3 observations. Its reviewer contract permitted detailed write-up of P0/P1 findings only, so those lower-severity observations are not promoted into unsupported proposals here.

## sql-data-reviewer

### 1. Correct processing

#### SQL-001 — P1

- **File / cell or function:** `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`, `iso_utc_ts`; consumed by the review-row construction in `notebooks/NB_ENR_POI_REVIEW.ipynb`.
- **Extra work or wrong step:** The expression casts an offset-bearing ISO value to `TIMESTAMP` and then calls `to_utc_timestamp(..., current_timezone())`. Correctness therefore depends on the Spark session timezone being UTC, but the supplied runtime evidence does not record that condition.
- **Correctness impact:** In a non-UTC session, an already offset-aware timestamp can be shifted again. The resulting incorrect `review_date` or `review_updated_at` would be retained in the append-only target.
- **Change direction:** Add a fail-fast UTC-session assertion before review rows are built, or replace the parser with an implementation whose result does not depend on `current_timezone()`. The smallest evidence check is `SELECT current_timezone() AS session_timezone`; only `UTC` or `Etc/UTC` satisfies the current design assumption. No pipeline trigger is requested.

### 2. Speed

No P0/P1 speed finding was established. Existing runtimes and the absence of additional volume evidence do not justify classifying any SQL action, scan, or shuffle as a serious F16 performance risk.

The reviewer counted five P2 observations and no P3 observations. Its reviewer contract permitted detailed write-up of P0/P1 findings only, so those lower-severity observations are not promoted into unsupported proposals here.

## Consolidated proposal list

### 1. Correct processing

1. **P1 — Make dirty-key detection deletion-aware.** In `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`, change `NodeContext.changed()` from a one-way subtraction to a materialized bidirectional difference. Continue rebuilding `NB_ENR_POI_INFO.ipynb` and `NB_ENR_POI_COORDINATE.ipynb` from the current snapshot, and prevent `advance_edges()` from committing an unrepresentable deletion.
2. **P1 — Remove the unverified timezone dependency.** In `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`, change `iso_utc_ts`, or add a fail-fast assertion before the review-row construction in `notebooks/NB_ENR_POI_REVIEW.ipynb`, so offset-aware review timestamps cannot be double-shifted. Runtime evidence of the session timezone is still required if the existing implementation is retained.

Both directions retain the recorded append-only design and the existing grains and keys: `(poi_id, updated_at)` and `(review_id, updated_at)`.

### 2. Speed

No P0/P1 speed change is justified by the supplied evidence. The measured runs fit within the 15-minute cadence, but they are too small and too limited to support claims about broader F16 scaling. Avoid speculative cache, repartition, or shuffle changes until action-level timing or execution-plan evidence identifies a concrete slow step.
