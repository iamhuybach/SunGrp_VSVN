# Round 1

Model: `gpt-5.6-sol` medium, Cursor subagents, read-only. No `run-gate`.

Reviewers, independent: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`. Then `risk-gate`.

L2 was out of scope. The user deferred `NB_SLV_POI` and `NB_SLV_POI_LOCALIZATION`.

## Verdict

`FIX_REQUIRED`

Pipeline review: `PASS`. Risk-gate kept one P1.

## P0/P1

| ID | Severity | Location | Failure | Fix |
|---|---|---|---|---|
| RISK-001 | P1 | `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` `event_order` | 3P state order is `(crawled_at, lsn, ingested_at, is_delete)`. `event_id` is not in it. A later event with the same `crawled_at` and a greater `event_id` is marked stale, skipped, and the watermark can move past it. Target MERGE still uses `event_id` as the tie-break. | Align 3P state comparison with `(crawled_at, event_id)`. The function is shared with partner. |

## Not blocking

| ID | Disposition |
|---|---|
| SQL-001 | Not blocking. All 13 price objects in the 53-row bronze file were JSON integers, and the price `full_reload` reported `cast_null = 0`. |
| SPARK-001 | Not blocking. `poi_price` is an active table again. `WATCH_BLOCKS` is only for inactive blocks. |
| SPARK-002, STATE-002 | Not blocking for this rollout. The reset full scans already ran. Notebook markdown "Lần đầu" is still stale. |

P2/P3 from risk-gate: 1/0.
