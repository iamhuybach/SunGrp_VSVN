# Request

## User outcome

`lh_vv_gold.dbo.gld_srv_poi_review` exists and is loaded with one row per `review_id` for reviews that already have an enrich row. `slv_enr_poi_review_multi_lang` has nullable `lang` and `title` columns. A review absent from `slv_3p_poi_review` does not appear in gold.

## Scope

### In scope

- New notebook `NB_GLD_SRV_POI_REVIEW`, one notebook for one target table. No new orchestration tier.
- Processing from mapping §1: `slv_enr_poi_review_multi_lang` INNER JOIN `slv_3p_poi_review` on `review_id`, LEFT JOIN `slv_3p_poi_rating` on `poi_id`.
- Columns and transforms only from mapping §2. `created_at` and `updated_at` are system timestamps.
- Target lakehouse.schema is `lh_vv_gold.dbo`. Do not place this table in schema `enr`. Do not change `NB_ENR_POI_REVIEW` logic.
- Add `lang` and `title` to `slv_enr_poi_review_multi_lang`, STRING, nullable. The mapping does not name a source for those two columns. Do not write a notebook that loads them.
- DDL in both `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL`. Setup edits the current definition in place. Create adds only a markdown cell `[THÊM dd/mm] 20261026-gld-srv-poi-review` and one self-contained patch cell at the end. Add columns with nullable `ALTER`. No `DROP TABLE`.
- Pipeline and `load_mode` use the values seeded for `gld_srv_poi_info`: `PL_VV_TRANS_SLV_TO_GLD_30M` and `RECOMPUTE`. Do not attach this table to `PL_VV_TRANS_SLV_TO_ENR_15M`.
- Grain is one row per `review_id`. If `slv_3p_poi_rating` has more than one row for one `poi_id`, stop. Do not pick a row.

### Out of scope

- Changes to `NB_ENR_POI_REVIEW` logic.
- A loader for `slv_enr_poi_review_multi_lang.lang` and `.title`.
- Schema `lh_vv_gold.enr` for `gld_srv_poi_review`.
- Pipeline `PL_VV_TRANS_SLV_TO_ENR_15M`.
- `notebooks_lgc/`, `docs/context/3p-google/*.txt`, pipeline manifests, and other tasks' artifacts.

## Acceptance criteria

- `NB_GLD_SRV_POI_REVIEW` is the only new business notebook, and it writes only `lh_vv_gold.dbo.gld_srv_poi_review`.
- Both DDL notebooks define the new gold table and the two new silver columns. Create's patch is idempotent and does not drop a table.
- Seeded pipeline is `PL_VV_TRANS_SLV_TO_GLD_30M` and `load_mode` is `RECOMPUTE`, matching `gld_srv_poi_info`.
- Gold grain is one row per `review_id`. A duplicate `slv_3p_poi_rating.poi_id` fails the run instead of choosing a row.
- Gold keeps only reviews present in both `slv_enr_poi_review_multi_lang` and `slv_3p_poi_review`. Rating is attached by `poi_id` when present.

## Constraints

- Mapping: `docs/context/mapping_gld_srv_poi_review.md`.
- Registry in `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_cfg_3p`: `slv_3p_poi_review` key `review_id`, columns `review_id` string, `poi_id`, `author_name` string, `rating` decimal(4,2), `time` string. `slv_3p_poi_rating` key `poi_id`, columns `poi_id`, `rating_overall` decimal(4,2), `rating_count` bigint.
- D-01: gold `rating_count` is Spark Long (`bigint`), the registry type of `slv_3p_poi_rating.rating_count`. Do not cast it to integer. Mapping §2's `integer` is not the column type.
- D-02: gold `rating` is `DECIMAL(4,2)`, the registry type of `slv_3p_poi_review.rating`. Transform 1-1. Do not cast it to string. Mapping §2's `string` is not the column type.
- `lang` and `title` have no fill source in the mapping.
- Business reason: gold serving keeps a review only when an enrich row exists, and attaches the POI rating. A review missing from `slv_3p_poi_review` does not reach gold.
- Domain: lib transform/gold and DDL/registry.

## Classification rationale

- Complexity: medium. New gold grain plus columns on an existing silver table. This is a behavior change across more than two files, so it is not the fast lane.
- Risk: medium. Bounded new serving table and nullable columns. No `DROP`. `NB_ENR_POI_REVIEW` logic stays as it is.
- Architecture: required. The new table has grain and key `review_id`, and `slv_enr_poi_review_multi_lang` gains columns.
- Evidence: not required for triage. Registry types and keys are in the repo. Duplicate `poi_id` handling is specified as fail, not as a distribution lookup. The open item is the `rating_count` type choice.
- Runtime proof: required after review, because the new notebook and DDL must run in Fabric DEV.
- Reviewer routing: `sql-data-reviewer` for the joins, grain, DDL, and types; `spark-runtime-reviewer` for the notebook contract and Delta write. No pipeline JSON change, so no `fabric-pipeline-reviewer`. Risk is medium, so no risk gate.
