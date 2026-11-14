# Evidence plan

## Decision to resolve

Can the existing gold MERGE (`sql_merge_target` on the grain key) be applied to the current Fabric DEV rows of `lh_vv_gold.enr.gld_enr_poi_info` and `lh_vv_gold.enr.gld_enr_poi_review`?

The repository records the intended grain and states that Delta has no primary key. It does not record whether those tables currently contain duplicate or null grain keys. APPEND writes can leave both.

## Existing evidence

- `docs/context/gld_enr_poi_info_review.md`: one row per `poi_id`; one row per `review_id`. This is the intended grain, not a measured count.
- `docs/context/CTRL_TABLES_CONTEXT.md`: Delta has no PK or UNIQUE. `PL_VV_TRANS_SLV_TO_ENR_15M` gold targets are `APPEND`.
- `NB_LIB_TRANSFORM_SLV_GLD`: one target MERGE, `sql_merge_target`, matched on `NodeSpec.pk`. The pass criterion for applying it is uniqueness of the current target key. This file does not record the Fabric error text for a non-unique target.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `evidence/probes/key-uniqueness.sql` | Fabric DEV, Spark SQL on `lh_vv_gold` | Are `poi_id` and `review_id` unique and non-null in the current target tables? | Pass when each result row has `null_key_count = 0` and `row_count = distinct_key_count`. Fail when either differs, or when the statement errors because a table is missing. | `evidence/results/key-uniqueness.txt` |
| `evidence/probes/source-uniqueness.sql` | Fabric DEV, Spark SQL on `lh_vv_silver` | Are the MERGE sources unique on `poi_id` (entity, rating, price) and `review_id` (review)? | Pass when each of the four rows has `null_key_count = 0` and `row_count = distinct_key_count`. | `evidence/results/source-uniqueness.txt` |
| Info `DRY_RUN` | Fabric DEV, schedule `PL_VV_TRANS_SLV_TO_ENR_15M` paused | Does one full info snapshot stay inside the 15-minute cadence on shared F16? | Pass when duration is under 15 minutes and the run has no OOM, throttling, or prolonged spill. Record duration, rows, bytes, shuffle, spill, peak memory, and capacity utilization. | `evidence/results/info-dry-run.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
- This probe returns two aggregate rows. Do not select review text, names, or addresses.

## Observed result — 2026-11-12

Fabric DEV aggregate paste, saved as `evidence/results/key-uniqueness.txt`. No sample rows.

| table_name | key_column | row_count | null_key_count | distinct_key_count | criterion |
|---|---|---:|---:|---:|---|
| `gld_enr_poi_info` | `poi_id` | 20829 | 0 | 20829 | pass |
| `gld_enr_poi_review` | `review_id` | 110342 | 0 | 109682 | fail |

`gld_enr_poi_info`: `null_key_count = 0` and `row_count = distinct_key_count`. The current info rows are unique on `poi_id`.

`gld_enr_poi_review`: `null_key_count = 0`. `row_count` is 660 greater than `distinct_key_count` (110342 − 109682). The current review rows are not unique on `review_id`. The probe does not say how many keys repeat, or whether repeated rows have the same payload.

The existing MERGE cannot be applied to the current review table under the pass criterion. No cleanup is designed here. Scope of the task is a user decision.

## Observed result — 2026-11-14

`evidence/results/source-uniqueness.txt`. Four aggregate rows. No sample rows.

| table_name | key_column | row_count | null_key_count | distinct_key_count | criterion |
|---|---|---:|---:|---:|---|
| `slv_poi_entity_non_enrich` | `poi_id` | 20829 | 0 | 20829 | pass |
| `slv_3p_poi_rating` | `poi_id` | 20808 | 0 | 20808 | pass |
| `slv_3p_poi_price` | `poi_id` | 20808 | 0 | 20808 | pass |
| `slv_3p_poi_review` | `review_id` | 109682 | 0 | 109682 | pass |

SQL-001 and SQL-002 pass on current DEV rows. Each source key is non-null and unique. No dedupe was added.

`evidence/results/enrmergepy.txt`: the cell printed `row_hash string`, `deleted_at timestamp`, and `load_mode RECOMPUTE` for 11 rows (info active 8, info inactive 1, review inactive 2).

`evidence/results/info-dry-run.txt`: the first `DRY_RUN` hit `ConfigError` while live `load_mode` was still `APPEND`. After `enrmergepy`, the same notebook with `p_mode = DRY_RUN` and `p_force = true` ended `SUCCESS` in 53s. Diff was insert 0, update 20829, soft delete 0, source 20829. The log has QG warnings and no OOM, throttling, or spill line. Bytes, shuffle, spill, peak memory, and capacity utilization were not in the notebook log. `DRY_RUN` does not commit, so this is not the second-RUN 0/0/0 proof. Review round 2 reopened SPARK-002: the 53s log does not confirm shuffle, spill, peak memory, or shared F16 headroom.

## Still required — SPARK-002

The Jobs page for jobs 259–278 is saved as `evidence/results/spark-ui-jobs.png` and transcribed in `evidence/results/info-dry-run-metrics.txt`. All visible jobs succeeded. The largest data read on that page is 34.18 MB. The page has no shuffle, spill, peak memory, or capacity columns.

`evidence/results/spark-resources.png`: 20 of 20 jobs succeeded. At 10:11:48.886 AM the tooltip reads Running 0, Allocated 8, Max instance 72. The chart is cores for the notebook pool, not F16 capacity CU, and it has no memory, shuffle, or spill.

Job 270, saved as `evidence/results/spark-job-270.png`: SUCCEEDED, submitted 2026/11/14 03:12:41, duration 0.2 s, one stage, tasks 2/2. The stage shuffles 2.1 MiB read and 2.1 MiB write after a parquet scan of `slv_poi_entity_non_enrich`. That table has no spill column.

On 2026-11-14 the user accepted the missing spill numbers and Fabric Capacity Metrics (D-SPARK-2) and asked to continue with `p_mode = RUN`. Those two figures stay unmeasured. They are not recorded as zero.
