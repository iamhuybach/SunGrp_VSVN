# Evidence plan

## Decision to resolve

Does `lh_vv_silver.dbo.slv_3p_poi_rating` currently contain at most one row for each non-null `poi_id`, with no null `poi_id`?

Pass: continue to `model-design`, then architecture. The gold left join may treat rating as one row per `poi_id`.

Fail: stop. Do not pick a rating row. The next step is a user decision on duplicate or null `poi_id` rows.

## Existing evidence

- `docs/context/01_DATA_MODEL.md` §5.2: `slv_3p_poi_rating` is `DOC`, source object `poi_rating`, key `poi_id`. `slv_3p_poi_review` is `DOC_ARRAY`, key `review_id`.
- `notebooks/NB_CREATE_DDL.ipynb` and `notebooks/NB_SETUP_INITIAL_DDL.ipynb` registry: key `poi_id`; `rating_overall` `decimal(4,2)` from `rating`; `rating_count` `bigint` from `userRatingCount`.
- No UNIQUE constraint and no measured row count are in the repository. The declared MERGE key does not prove the current Delta table.

The silver `rating_count` type is `bigint`. The requested gold type is integer. That cast belongs to model design after this grain probe. It is not a second probe.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `evidence/probes/rating_grain.py` | Fabric DEV, `lh_vv_silver` | How many rows, distinct `poi_id`, null `poi_id`, and duplicate `poi_id` groups are in `slv_3p_poi_rating`? | Pass when `null_poi_id_rows = 0` and `duplicate_poi_id_groups = 0`. Fail otherwise. An empty table passes this predicate and must still report `row_count = 0`. | `evidence/results/rating_grain.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
