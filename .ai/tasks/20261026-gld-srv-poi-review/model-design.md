# Model design: 20261026-gld-srv-poi-review

## Scope

- Base task: `20261026-gld-srv-poi-review`. Per `task-state.yaml`: status `triage`, `architecture_required: true`, signal `data_model_change`, architecture round 1.
- This is a model rerun. It replaces the prior `model-design.md`. It closes prior Conflicts 1 and 2 and the `architecture.md` `## Blocking gaps` G1 column gap. The rest of the prior design is kept unless a named file contradicts it.
- There are no `proposal.md`, `problem-analysis.md`, or `requirements-analysis.md` files in the task folder. This design implements:
  - `request.md` `## Constraints`.
  - Mapping `docs/context/mapping_gld_srv_poi_review.md` §1 (Xử lý) and §2 (Field Mapping).
  - `decision.md` `Quyết định hiện hành` ledger rows:
    - D-01: `rating_count` is Long ("Kiểu Long như source hiện tại").
    - D-02: `rating` is decimal(4,2) ("Kết quả là decimal(4,2)").
  - `architecture.md` `## Blocking gaps` G1 (technical columns for RECOMPUTE MERGE) and `### Gold contract` (column list and order).
- The handoff asks for citations of `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry`. That file does not exist. For the change flow, this design cites mapping §1 and `architecture.md` `## Scope`. For registry facts, it cites the `request.md` `## Constraints` registry bullet (cell `init_cfg_3p` in `notebooks/NB_SETUP_INITIAL_DDL.ipynb`).
- Out of model scope (`architecture.md` `## Non-goals`):
  - `NB_ENR_POI_REVIEW`.
  - A loader for `lang` / `title`.
  - Schema `lh_vv_gold.enr`.
  - `PL_VV_TRANS_SLV_TO_ENR_15M` edges.
  - A mapping-doc edit.
- Load mode `RECOMPUTE` and pipeline `PL_VV_TRANS_SLV_TO_GLD_30M` are runtime facts. They are not columns. They matter here only because RECOMPUTE implies the lib MERGE technical columns (G1).

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_review` (new) | gold serving (`gld_srv_<chủ đề>_<grain>`, naming §1) | one row per `review_id` | `NB_GLD_SRV_POI_REVIEW` (new, `NB_<UPPER(trg_tbl)>`, naming §2) |
| `lh_vv_silver.dbo.slv_enr_poi_review_multi_lang` (existing, +2 columns) | silver | Unchanged by this task. Key column `review_id STRING NOT NULL` (prior design, `TABLE_SPECS`). Uniqueness on `review_id` is not stated (Conflicts 4). | None. No loader (`architecture.md` `## Non-goals`). |

Read-only sources, not changed by this task (`request.md` `## Constraints`):
- `lh_vv_silver.dbo.slv_3p_poi_review`, registry key `review_id`.
- `lh_vv_silver.dbo.slv_3p_poi_rating`, registry key `poi_id`.

## Keys

`lh_vv_gold.dbo.gld_srv_poi_review`
- Primary / grain key: `review_id`, so `NodeSpec.pk = ("review_id",)` (`architecture.md` `## Grain and keys`).
- Business key: `review_id`, copied 1-1 from `slv_enr_poi_review_multi_lang.review_id` (mapping §2). No new derivation.
- `poi_id`: copied 1-1 from `slv_enr_poi_review_multi_lang.poi_id` (mapping §2). It is not derived here, so the AGENTS.md §7 `poi_id` formula is not applied. Upstream, both `slv_3p` tables take `poi_id` from the registry `POI_ID` definition (cell `init_cfg_3p`, per the prior design). That is context only.
- Logical foreign keys (join keys, mapping §1):
  - `review_id` → `slv_3p_poi_review.review_id`, INNER JOIN.
  - enrich `poi_id` → `slv_3p_poi_rating.poi_id`, LEFT JOIN.
- Physical constraints: none. No FK constraint is declared.
- The model does not pick a survivor row. A duplicate `review_id` in the output, or a duplicate `slv_3p_poi_rating.poi_id`, stops the run. That stop is runtime behaviour owned by `architecture.md`, not by this design.

`lh_vv_silver.dbo.slv_enr_poi_review_multi_lang`
- Keys are unchanged. `review_id STRING NOT NULL`, `poi_id STRING` nullable.
- `lang` and `title` are not key columns.

## Columns

`gld_srv_poi_review` columns are listed in contract order (`architecture.md` `### Gold contract`, author input column contract).

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_enr_poi_review_multi_lang` | `lang` | STRING | yes | unknown: the mapping names no fill source | New column after `poi_id`. Mapping §1 "Thêm cột `lang`, `title`". `request.md` `## Constraints`: no fill source. No loader. |
| `slv_enr_poi_review_multi_lang` | `title` | STRING | yes | unknown: the mapping names no fill source | New column after `lang`. Mapping §1 "Thêm cột `lang`, `title`". `request.md` `## Constraints`: no fill source. No loader. Silver order: `review_id, poi_id, lang, title, review_text, created_at, updated_at` (`architecture.md` `## Invariants` 6). |
| `gld_srv_poi_review` | `review_id` | STRING | no | `slv_enr_poi_review_multi_lang.review_id` | Transform 1-1, mapping §2 row `review_id`. NOT NULL as accepted in `architecture.md` `### Non-blocking items` (Model Q5). |
| `gld_srv_poi_review` | `poi_id` | STRING | yes | `slv_enr_poi_review_multi_lang.poi_id` | Transform 1-1, mapping §2 row `poi_id`. |
| `gld_srv_poi_review` | `lang` | STRING | yes | `slv_enr_poi_review_multi_lang.lang` | Transform 1-1, mapping §2 row `lang`. Null until an upstream writer exists (Conflicts 3). |
| `gld_srv_poi_review` | `rating_overall` | DECIMAL(4,2) | yes (LEFT JOIN) | `slv_3p_poi_rating.rating_overall` | Transform 1-1, mapping §2 row `rating_overall`. Registry type `decimal(4,2)` (`request.md` `## Constraints`). |
| `gld_srv_poi_review` | `rating_count` | BIGINT (Spark Long) | yes (LEFT JOIN) | `slv_3p_poi_rating.rating_count` | Transform 1-1, no cast to integer. D-01. Registry type `bigint`. The mapping §2 `integer` is not the column type (`request.md` `## Constraints`). |
| `gld_srv_poi_review` | `title` | STRING | yes | `slv_enr_poi_review_multi_lang.title` | Transform 1-1, mapping §2 row `title`. Null until an upstream writer exists (Conflicts 3). |
| `gld_srv_poi_review` | `review_text` | STRING | yes | `slv_enr_poi_review_multi_lang.review_text` | Transform 1-1, mapping §2 row `review_text`. |
| `gld_srv_poi_review` | `rating` | DECIMAL(4,2) | yes | `slv_3p_poi_review.rating` | Transform 1-1, no cast to string. D-02. Registry type `decimal(4,2)`. The mapping §2 `string` is not the column type (`request.md` `## Constraints`). |
| `gld_srv_poi_review` | `review_date` | STRING | yes | `slv_3p_poi_review.time` | Transform 1-1 with rename `time` → `review_date`, mapping §2 row `review_date`. |
| `gld_srv_poi_review` | `author_name` | STRING | yes | `slv_3p_poi_review.author_name` | Transform 1-1, mapping §2 row `author_name`. |
| `gld_srv_poi_review` | `row_hash` | STRING | yes | lib technical column | Lib `TECH_COLUMNS` for RECOMPUTE MERGE. `architecture.md` G1. Not a mapping §2 business column. |
| `gld_srv_poi_review` | `created_at` | TIMESTAMP | yes | system | "field hệ thống", mapping §2 row `created_at`. Nullable as accepted in `architecture.md` Model Q5. |
| `gld_srv_poi_review` | `updated_at` | TIMESTAMP | yes | system | "field hệ thống", mapping §2 row `updated_at`. Nullable as accepted in `architecture.md` Model Q5. |
| `gld_srv_poi_review` | `deleted_at` | TIMESTAMP | yes | lib technical column | Lib `TECH_COLUMNS` for RECOMPUTE MERGE (soft delete). `architecture.md` G1. Not a mapping §2 business column. |

The gold table has no other columns. The technical columns follow lib order after `author_name`: `row_hash, created_at, updated_at, deleted_at` (`architecture.md` G1 and `### Gold contract`).

## Lineage

`lh_vv_gold.dbo.gld_srv_poi_review`
- Bronze: no direct read. Upstream, `slv_3p_poi_review` and `slv_3p_poi_rating` are loaded from `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` through the registry (prior design, cell `init_cfg_3p`).
- Silver reads (mapping §1):
  - `lh_vv_silver.dbo.slv_enr_poi_review_multi_lang`: the driving table. Reads `review_id, poi_id, lang, title, review_text`.
  - INNER JOIN `lh_vv_silver.dbo.slv_3p_poi_review` on `review_id`. Reads `rating, time, author_name`.
  - LEFT JOIN `lh_vv_silver.dbo.slv_3p_poi_rating` on the enrich `poi_id`. Reads `rating_overall, rating_count`.
- Gold reads: none. Gold does not read gold (AGENTS.md §7).
- Technical columns (`row_hash`, `created_at`, `updated_at`, `deleted_at`) are produced by the lib MERGE. They are not read from any source.
- Retention result: a review reaches gold only when its `review_id` exists in both `slv_enr_poi_review_multi_lang` and `slv_3p_poi_review`. Rating columns are null when no `slv_3p_poi_rating` row matches (`request.md` `## Constraints` business reason).

`lh_vv_silver.dbo.slv_enr_poi_review_multi_lang`
- No bronze, silver, or gold reads are designed for the new columns `lang` and `title`, because the source is unknown and there is no loader. Reads for the existing columns are unchanged and not covered here.

## Conflicts and questions

1. Missing `proposal.md`. The handoff asks for citations of `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry`. The file does not exist, so this design cites mapping §1, `request.md` `## Constraints`, and `architecture.md` instead. If a proposal is written later, check it against this design.
2. Mapping §2 types still differ from the column types. Mapping §2 still says `integer` for `rating_count` and `string` for `rating`. D-01 and D-02 are the record, and `architecture.md` `## Non-goals` excludes a mapping-doc edit. No action in this design. This item is recorded only so a reader of the mapping is not misled.
3. Unknown source for `slv_enr_poi_review_multi_lang.lang` and `.title`. The mapping names no fill source, and there is no loader. Both columns stay null in gold until an upstream writer exists. Open: which notebook and source will fill them, and in which task?
4. Uniqueness of `slv_enr_poi_review_multi_lang` on `review_id`. Gold grain requires at most one enrich row per `review_id`. The table name contains `multi_lang`, and `architecture.md` Model Q6 notes that the table may hold duplicates. This design picks no survivor row. A duplicate stops the run through lib QG `pk_duplicate` (`architecture.md`). Open: can one review have several language rows? If so, the requested grain conflicts with the source. Probe P1 answers this for DEV.
5. `poi_id` used for the rating join. Mapping §1 and §2 use the enrich `poi_id`. `slv_3p_poi_review` also has `poi_id`. This design uses the enrich `poi_id`, as the mapping states. `architecture.md` Model Q7 keeps it and adds a mismatch warn metric. Open: confirm that the review-table `poi_id` is not meant to be used.
