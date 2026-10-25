# Evidence plan

## Decision to resolve

Why `is_empty("multi_lang")` was true for `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` at Delta version 2 during exec `8f8da0f2-175e-4e9d-bd0e-6bb3756f5a06`.

`is_empty` is `input(role).limit(1).count() == 0`. `input` defaults to `live_only=True` and keeps only `deleted_at IS NULL` when both `row_hash` and `deleted_at` exist. `build` reads the same role with `live_only=False`, but that call is after the quality gate and did not run.

## Existing evidence

- Repository code and naming doc cited in `decision.md` D1.
- `evidence/results/multi_lang_row_count.txt`: version 2 is current, `row_count=0`, `row_hash` and `deleted_at` are absent. Interpreted as data in D2.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `multi_lang_row_count.py` | Fabric DEV, Spark that can read `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` | Current columns and row counts, plus the same aggregates at Delta version 2 | Interpret only version 2. `row_count=0`: data, the gate matched an empty snapshot. `row_count>0` and both `row_hash` and `deleted_at` exist and `deleted_at_is_null=0`: code, the live filter hid rows that `build` would read. `row_count>0` and the live filter would still see a row (`deleted_at` absent, or `row_hash` absent, or `deleted_at_is_null>0`): code, `is_empty` should not have fired at that snapshot. Version 2 `UNAVAILABLE`: do not classify from current counts. | `evidence/results/multi_lang_row_count.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
- This probe prints aggregates and column names only.
