# Request

## User outcome

A solution proposal for extracting `lh_vv_bronze.dbo.cms_raw_data` by reusing an existing load mode. This phase does not change runtime behavior.

## Scope

### In scope

- Problem analysis and a solution proposal for a new per-source extract notebook and registry rows that use only the current load modes.
- A key tree of the one sample row, with no values and no URLs.

### Out of scope

- Adding a value to `LOAD_MODES`.
- Changing the mode signature in `NB_LIB_EXTRACT_RAWDATA` when `DOC` or `DOC_ARRAY` is enough.
- Attaching `cms_raw_data` to the `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` activity that runs `partner_raw_data`.
- Interpreting the parenthetical names in D-05, or inventing grain, kept columns, or a `json_path`.
- A `json_path` for a key that was not seen.
- A POI table designed from `pois[]`, whose sample element is empty.
- Architecture and specialist review for this proposal-only phase.

## Acceptance criteria

- `problem-analysis.md` and `proposal.md` exist and were written by `run-author`.
- The proposal chooses only among `CDC`, `DOC`, and `DOC_ARRAY`.
- The proposal lists which payload blocks are `DOC` and which are `DOC_ARRAY`, then stops for the user to lock target tables.
- `evidence/payload-shape.md` records the sample key tree. Unseen columns and keys are `MISSING_EVIDENCE`.

## Constraints

- `LOAD_MODES` is only `CDC`, `DOC`, `DOC_ARRAY`. The proposal must choose one of these three. Do not add a new value.
- The sample row has no `before`, `after`, `op`, `source.schema`, or `source.table`. Do not assign `CDC` until a real Debezium event exists.
- The envelope is close to `brz_3rd_crawler_poi_stream` but has no `source_id`, `normalized_payload`, or `language_code`, and it adds a `type` column. Do not treat `type` as `language_code` or as an entity type from one value.
- `NB_EXTRACT_<SOURCE>_CDC_BRZ_TO_SLV` is the per-source notebook name, not a new load mode.
- `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` runs only `partner_raw_data`. Do not attach `cms_raw_data` to that activity.
- On 2026-11-05 the user said invalid records are written to `ctrl_cdc_reject` the same way as the partner flow. `notebooks_lgc/cms_transform/nb_cms_transformation.ipynb` is a business reference from the old model, not the code or table-structure standard. Extract targets are `slv_cms_blog`, `slv_cms_destination`, `slv_cms_news`, and `slv_cms_promotion_article`. The MERGE key of each table is `document_id` together with `locale`. Gold is out of scope.
- One row is not a schema contract. Do not write URLs, signatures, proper names, or description text into an artifact.

## Classification rationale

- Complexity: `low`. No runtime behavior has changed. The accepted names and key are recorded; model design waits on the remaining choices.
- Risk: `low`. No runtime behavior changes.
- Architecture: required before implementation, because the task now names four target tables and key `id`. Gate stays `pending`. Do not call the Architect until `model-design.md` exists and the open choices are closed.
- Evidence: required. One row does not establish the payload shape of the four `source_name` values. Probe `evidence/probes/cms-source-sample.sql` is read-only and has not been run.
- Runtime proof: not required. Nothing is deployed or executed.
- Reviewer routing: none until implementation. This phase still does not change behavior.
