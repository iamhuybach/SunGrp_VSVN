# Model design input

`proposal.md`, `problem-analysis.md`, and `requirements-analysis.md` do not exist. Do not invent them.

## Decision to model

D-COL-1, 2026-11-12: the user accepted two technical columns. Add only `row_hash` STRING and `deleted_at` TIMESTAMP to `lh_vv_gold.enr.gld_enr_poi_info` and `lh_vv_gold.enr.gld_enr_poi_review`. They are the existing `TECH_COLUMNS` of `sql_merge_target` in `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` (`row_hash` string, then existing `created_at` and `updated_at`, then `deleted_at` timestamp). Business columns, grain, and keys stay as documented.

## Read

- `.ai/tasks/20261112-enr-poi-append-to-merge/decision.md`, section `Quyết định hiện hành`, rows D-MERGE-1, D-RISK-1, and D-COL-1.
- `docs/context/gld_enr_poi_info_review.md`, both grain tables.
- `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`: `TECH_COLUMNS` and `def:sql_merge_target`.
- `architecture.md` section `0. Blocking gap` and section `5. Alternatives` row A1 only. Do not copy the rest of the architecture.

## Required content

- Grain stays one row per `poi_id` and one row per `review_id`.
- Keys stay `poi_id` and `review_id`. Do not change the `poi_id` formulas in `AGENTS.md`.
- `deleted_at` NULL means the key is still in the source. A non-null `deleted_at` means the key left the source and the row is kept.
- `row_hash` is the library hash of the business columns. Do not invent a hash formula.
- D-RISK-1 deletes and re-inits review data later in Fabric. Info rows are not deleted. Review edges stay `is_active = 0`.
- If `docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio` is not among the files above, ask whether it shows these columns. Do not open `notebooks_lgc/` or `services/`.

## Out of scope

No new MERGE. No business-column change. No `gld_enr_poi_coordinate`. No API.
