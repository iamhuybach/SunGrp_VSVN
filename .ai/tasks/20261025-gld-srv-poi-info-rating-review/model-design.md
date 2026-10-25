# Model design — 20261025-gld-srv-poi-info-rating-review

## Scope

- Base task: `20261025-gld-srv-poi-info-rating-review`. Source: `request.md` `## User outcome` and `## Acceptance criteria`, plus ledger rows D-01 to D-05 in `decision.md` `## Quyết định hiện hành`.
- The task has no `proposal.md`, so this design cannot cite `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. There is also no `problem-analysis.md` or `requirements-analysis.md`.
- What this design covers:
  - Three new nullable columns on `lh_vv_gold.dbo.gld_srv_poi_info`: `rating_overall`, `rating_count`, `review_count`.
  - Two new left-join sources, `lh_vv_silver.dbo.slv_3p_poi_rating` and `lh_vv_silver.dbo.slv_3p_poi_review`, joined on `poi_id`.
  - The matching new rows in mapping `docs/context/mapping_gld_srv_poi_info.md` §1.2.
- Ledger rows used: D-01 (rating grain), D-02 (`review_count`), D-03 (`INT` cast), D-04 (NULL for partner and for unmatched rows), D-05 (where columns are described).
- Out of scope, unchanged:
  - Mapping §1.1: the Google rule that keeps a `poi_id` only when it is in both enriched tables, and the partner-full rule.
  - `operating_hours` (§1.3, §1.5), `is_recommended`, and every current §1.2 column.
  - `docs/context/01_DATA_MODEL.md` (D-05).
  - The `ctrl_cfg_schema_registry` entries of the two silver tables. Both tables and their columns are already registered (`NB_CREATE_DDL` cell `e9c137c5-c9fc-4f8f-a925-bc511cfd71a7`, `NB_SETUP_INITIAL_DDL` cell `init_cfg_3p`), so no registry change is needed.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_info` (changed: three columns added) | gold serving | One row per `poi_id`; unchanged (request.md User outcome; mapping §1.1) | `NB_GLD_SRV_POI_INFO` (`SPEC.trg_tbl`, `pk=("poi_id",)`, `write_mode="MERGE"`) |
| `lh_vv_silver.dbo.slv_3p_poi_rating` (read only, new input) | silver L1 3rd-party, `load_mode` `DOC` | One row per `poi_id`. Declared key `poi_id` in the registry. Measured 1:1 on Fabric DEV 2026-10-26: 345 rows, 345 distinct `poi_id`, 0 null, 0 duplicate groups (D-01, `evidence/results/rating_grain.txt`) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` (01_DATA_MODEL §5.2) |
| `lh_vv_silver.dbo.slv_3p_poi_review` (read only, new input) | silver L1 3rd-party, `load_mode` `DOC_ARRAY` | One row per `review_id`; many rows per `poi_id` (registry `"key": "review_id"`; 01_DATA_MODEL §5.2) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |

## Keys

**`gld_srv_poi_info`**
- Primary key: `poi_id`, `STRING NOT NULL` (DDL in `NB_CREATE_DDL` cell `srvpoipy` `GOLD_COLS` and in `NB_SETUP_INITIAL_DDL` cell `init_tables`; `SPEC.pk`). MERGE key: `poi_id`. Both unchanged.
- Business key: `poi_id`. It comes from `slv_poi_entity_non_enrich.poi_id`, 1-1 (mapping §1.2).
- `poi_id` formulas (01_DATA_MODEL §5.2 and §8):
  - 3rd-party / Google: `uuid_format(md5(source_name ‖ source_id))`, rule `HASH_MD5_UUID`.
  - Partner: `md5(concat(id, 'partner'))` with dashes inserted as 8-4-4-4-12.
- Foreign keys: these are logical only; Delta enforces no FK.
  - Existing: `poi_id` → `slv_poi_entity_non_enrich.poi_id`.
  - New: `poi_id` → `slv_3p_poi_rating.poi_id` (left join, 0..1 per D-01).
  - New: `poi_id` → `slv_3p_poi_review.poi_id` (left join on a per-`poi_id` aggregate, 0..1 after grouping).

**`slv_3p_poi_rating`**
- Primary / business key: `poi_id` (registry `"key": "poi_id"`, column `POI_ID`, rule `HASH_MD5_UUID`).
- No UNIQUE constraint. Uniqueness is measured, not enforced (D-01; `decision.md` `## Giả định còn lại`).

**`slv_3p_poi_review`**
- Primary key: `review_id`, rule `HASH_SHA256` (registry; 01_DATA_MODEL §8).
- Join key to gold: `poi_id` (`POI_ID`, `HASH_MD5_UUID`). It is not unique in this table.

## Columns

Physical position in both DDL definitions: after `holiday_exceptions`, before `row_hash`, `created_at`, `updated_at`, `deleted_at`. The same order applies to `OUT_COLS` after `holiday_exceptions`.

All three columns are nullable, because columns added to an existing table must allow NULL (02_NAMING_CONVENTION §2.1 rule 5).

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `gld_srv_poi_info` | `rating_overall` | `DECIMAL(4,2)` | yes | `slv_3p_poi_rating.rating_overall` (registered and measured `decimal(4,2)`; D-01) | Transform 1-1, no cast (request.md User outcome; Acceptance criteria). Left join on `poi_id`. Filled only for rows whose `lower(trim(source_name))` is `google` and that match in rating. Partner rows and unmatched rows are NULL and keep their `poi_id` (D-04). No rule picks one rating row among several (D-01; request.md Out of scope). |
| `gld_srv_poi_info` | `rating_count` | `INT` | yes | `slv_3p_poi_rating.rating_count` (registered and measured `bigint`; D-01) | Transform 1-1 with a cast from `bigint` to `INT` (request.md User outcome: "integer"; D-03). A value outside `INT` range fails the node. Such a value is never stored as NULL, and the column is never widened to `BIGINT` (D-03). Same join, partner and unmatched rules as `rating_overall` (D-04). |
| `gld_srv_poi_info` | `review_count` | `INT` | yes | `slv_3p_poi_review`, rows grouped by `poi_id` | `COUNT(*)` grouped by `poi_id`, then cast to `INT`. Not `COUNT(DISTINCT review_id)`. A row with NULL `review_id` still counts (D-02). The aggregate is left-joined on `poi_id`. A `poi_id` with no review row is NULL, never coalesced to 0 (request.md User outcome; D-02). Partner rows are NULL (D-04). Overflow past `INT` fails the node (D-03). |

New mapping §1.2 rows (D-05; mapping §1.2 is the description source):

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| `slv_3p_poi_rating.rating_overall` | `decimal(4,2)` | transform 1-1 | `rating_overall` |
| `slv_3p_poi_rating.rating_count` | `integer` | transform 1-1 | `rating_count` |
| `slv_3p_poi_review` | `integer` | count review theo `poi_id` | `review_count` |

The wording comes from request.md User outcome. The same three columns must also appear in `OUT_COLS`, in both DDL definitions, and in `tests/test_gld_srv_poi_contract.py` (Acceptance criteria; D-05).

## Lineage

**`gld_srv_poi_info`**
- Bronze: none is read directly. Both new silver inputs are extracted from `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` by `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`. The `pipeline_config` seed rows for those two silver targets are in `NB_SETUP_INITIAL_DDL`.
- Silver, existing inputs (unchanged):
  - `lh_vv_silver.dbo.slv_poi_entity_non_enrich` (`entity`)
  - `lh_vv_silver.dbo.slv_enr_poi_destination` (`destination`)
  - `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` (`multi_lang`)
- Silver, new inputs:
  - `lh_vv_silver.dbo.slv_3p_poi_rating`, read columns `poi_id`, `rating_overall`, `rating_count`.
  - `lh_vv_silver.dbo.slv_3p_poi_review`, read columns `poi_id` plus a row count.
- Gold: none. Gold reads silver only.

**`slv_3p_poi_rating`, `slv_3p_poi_review`**
- Bronze: `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`, payload blocks `poi_rating` and `poi_review` (01_DATA_MODEL §5.2).
- Silver and gold reads: none. This task does not change these tables.

## Conflicts and questions

1. **Source label is wider than the target type.** The request labels the source of `rating_count` as `integer`, but the source is registered and measured as `bigint`. The request's `integer` is read as the target type. D-03 settles this: cast 1-1 to `INT`, fail the node on overflow, never widen. This item is recorded for traceability only; it is not open.
2. **Sources other than `google` and `partner` are not covered.** The request only gives the rule for `google` (join) and `partner` (NULL). Rows with any other `source_name` already fail the node through `operating_hours` (`SOURCE_NOT_GOOGLE_PARTNER` in `srvinfohours`), so the three columns are never written for them today. If that check is ever relaxed, the rule for these rows has to be decided. This design does not invent one.
3. **Architecture items, not model questions:**
   - edge sequence numbers and `ctrl_mng_pipeline_config` rows for the two new inputs
   - `SPEC.inputs` aliases and whether the new inputs are required
   - the run-time stop check when `slv_3p_poi_rating` stops being one row per `poi_id`
   - in-place DDL placement and the `NB_CREATE_DDL` patch cell
   - the `row_hash` change on existing rows once the business-column set grows

   They are left to `architecture.md`.
