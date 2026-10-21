# Request

## User outcome

One Vietnamese reference note that shows what `gld_enr_poi_info` and `gld_enr_poi_review` contain, using the columns the current notebooks and DDL actually write.

## Scope

### In scope

- Add `docs/context/gld_enr_poi_info_review.md`.
- Describe both gold tables: schema `lh_vv_gold.enr`, grain, notebook, and sources the notebook reads now.
- List each column with its DDL type and one short meaning, taken from `NB_ENR_POI_INFO`, `NB_ENR_POI_REVIEW`, and `NB_SETUP_INITIAL_DDL`.

### Out of scope

- `gld_enr_poi_coordinate`.
- Notebooks, DDL, pipelines, and mapping files.
- Changing table grain, keys, or runtime behavior.

## Acceptance criteria

- One file. Vietnamese prose. Column names, types, and table names stay in English.
- Each gold table has a markdown table for table facts: schema `lh_vv_gold.enr`, grain, notebook, sources in use.
- Each gold table has a markdown table for columns: name, type, one short meaning.
- The column list matches current code. Do not copy an older document when the code differs. Do not invent columns.
- The `gld_enr_poi_info` column table has an `enrich_type` documentation column. Values come only from the user's three lists. A column in more than one list shows every matching type. A column in none is blank. This is not a Delta column.

## Constraints

- Read the output-column cells of the two enrich notebooks, the `gld_enr_poi_info` and `gld_enr_poi_review` blocks in `NB_SETUP_INITIAL_DDL`, and only the matching lines in `docs/context/01_DATA_MODEL.md`.
- `01_DATA_MODEL.md` has no lines for these two tables.

## Classification rationale

- Complexity: `low`. No classification signals. The task adds one description file and does not change a table, column, grain, or key.
- Risk: `low`. No behavior change.
- Architecture: not required. No grain, key, commit, CDC, watermark, or orchestration change.
- Evidence: not required. Column names and types are in the repository notebooks.
- Runtime proof: not required. No Fabric run.
- Reviewer routing: none. No SQL/Delta MERGE, notebook logic, pipeline, or durable-state change, so `specialist_review` and `risk_gate` stay `not_required`.
- Fast lane: `complexity=low`, `risk_level=low`, no behavior change, one changed file. `WORKFLOW.md` allows at most two.
