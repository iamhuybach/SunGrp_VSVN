# Model design: 20261116-srv-poi-info-is-active

## Scope

- Base task: `20261116-srv-poi-info-is-active` (`request.md`, `task-state.yaml` status `triage`, signal `data_model_change`).
- Proposal: this task has no `proposal.md`, `problem-analysis.md`, or `requirements-analysis.md`. Proposal sections `## Dòng thay đổi` and `## ctrl_cfg_schema_registry`: Not applicable.
- Rules implemented: `request.md` `## Scope` / `### In scope` and `## Constraints`, plus `decision.md` `## Quyết định hiện hành` rows D-1, D-2, D-3, D-4.
- Changes covered:
  - Gold: `lh_vv_gold.dbo.gld_srv_poi_info.is_active` (D-1).
  - PostgreSQL: `apps.srv_poi_info.is_active` (D-2), and `apps.*.ingestion_ts` on every `CREATE TABLE apps` in `sql/postgres/gld_srv_serve.pg.sql` (D-2).
  - The serving-contract exception (D-3).
  - Entity mapping for `SrvPoiInfo`, `SrvPoiMultiLang`, `SrvPoiAmenity`, `SrvPoiMediaGallery`, `SrvPoiReview` (D-4).
- Unchanged: grain, keys, and `poi_id` formulas (`request.md` Out of scope, Constraints). JSON API fields, `docs/context/api-mapping/`, and `docs/poi-serving-api/` also stay unchanged (D-4, `request.md` Out of scope).
- Out of this design: migration, ALTER execution, locks, ordering, and rollout. These belong to the Architect and `runtime-runbook.md`.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_info` | gold | one row per `poi_id` (`NB_GLD_SRV_POI_INFO` markdown cell `srvinfomd`; `docs/context/mapping_gld_srv_poi_info.md` §1.1) | `NB_GLD_SRV_POI_INFO` (`SPEC.trg_tbl = gld_srv_poi_info`, cell `srvinfobuild`) |
| `apps.srv_poi_info` | PostgreSQL serving | one row per `poi_id` (`PRIMARY KEY (poi_id)`) | None. No notebook writes PostgreSQL in the files read. Gold source: `NB_GLD_SRV_POI_INFO` |
| `apps.srv_poi_multi_lang` | PostgreSQL serving | one row per `(poi_id, lang)` | None. Gold source: `NB_GLD_SRV_POI_MULTI_LANG` |
| `apps.srv_poi_amenity` | PostgreSQL serving | one row per `(poi_id, business_sector, amenity_group, amenity_raw)` | None. Gold source: `NB_GLD_SRV_POI_AMENITY` |
| `apps.srv_poi_media_gallery` | PostgreSQL serving | one row per `(media_id, poi_id)` | None. Gold source: `NB_GLD_SRV_POI_MEDIA_GALLERY` |
| `apps.srv_poi_review` | PostgreSQL serving | one row per `review_id` | None. Gold source: `NB_GLD_SRV_POI_REVIEW` |

The grain of every table stays the same (`request.md` Constraints).

## Keys

| table | primary key | business key | foreign keys |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_info` | `poi_id` (`SPEC.pk = ("poi_id",)` in `srvinfobuild`; `poi_id STRING NOT NULL` in `NB_SETUP_INITIAL_DDL` `init_tables`) | `poi_id` | None declared |
| `apps.srv_poi_info` | `poi_id` | `poi_id` | None declared in `gld_srv_serve.pg.sql` |
| `apps.srv_poi_multi_lang` | `(poi_id, lang)` | same | None declared |
| `apps.srv_poi_amenity` | `(poi_id, business_sector, amenity_group, amenity_raw)` | same | None declared |
| `apps.srv_poi_media_gallery` | `(media_id, poi_id)` | same | None declared |
| `apps.srv_poi_review` | `review_id` | same | None declared |

- **`poi_id` formula source.** `gld_srv_poi_info.poi_id` is a 1-1 copy of `slv_poi_entity_non_enrich.poi_id` (`mapping_gld_srv_poi_info.md` §1.2 row `poi_id`; §1.1 "Grain một dòng `poi_id`. MERGE theo `poi_id`"). This task does not change the upstream formula. `poi_id` never includes language (`services/data-serving-service/AGENTS.md` `## Contract`).
- **PostgreSQL keys.** They follow `services/data-serving-service/AGENTS.md` `## Contract` (Keys) and the `PRIMARY KEY` clauses in `sql/postgres/gld_srv_serve.pg.sql`.
- **Entity keys.** Composite keys use `@IdClass`, and `test_entities_match_gold_columns_types_and_keys` checks this.
- **New columns and keys.** No key, unique constraint, or index is added. Neither `is_active` nor `ingestion_ts` joins any key.

## Columns

Only the affected columns are listed.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_info` | `is_active` | `BOOLEAN` | yes | No source column. `NB_GLD_SRV_POI_INFO` writes literal `true` on every output row | D-1. Placed immediately after `is_bookable` in `init_tables` spec, the current `NB_CREATE_DDL` contract, and `OUT_COLS` of `srvinfobuild`. Not read from silver. Not derived from or tied to `deleted_at`. Mapping §1.2 gains one row with no source field, type `boolean`, transform `true`, target `is_active` (`request.md` In scope) |
| `apps.srv_poi_info` | `is_active` | `boolean` | yes | copy of `gld_srv_poi_info.is_active` | D-2. Placed immediately after `is_bookable`. Type follows the file's `BOOLEAN -> boolean` mapping. D-3: must match the gold column in name and type |
| `apps.srv_poi_info` | `ingestion_ts` | `timestamp without time zone` | yes | none: PostgreSQL only | D-2. Placed immediately after `deleted_at`. Not in silver or gold. No writer job. D-3 exception |
| `apps.srv_poi_multi_lang` | `ingestion_ts` | `timestamp without time zone` | yes | none: PostgreSQL only | D-2, D-3 (same as above) |
| `apps.srv_poi_amenity` | `ingestion_ts` | `timestamp without time zone` | yes | none: PostgreSQL only | D-2, D-3 (same as above) |
| `apps.srv_poi_media_gallery` | `ingestion_ts` | `timestamp without time zone` | yes | none: PostgreSQL only | D-2, D-3 (same as above). The existing `is_active boolean` stays unchanged (D-2) |
| `apps.srv_poi_review` | `ingestion_ts` | `timestamp without time zone` | yes | none: PostgreSQL only | D-2, D-3 (same as above) |
| entity `SrvPoiInfo` | `is_active` | `Boolean` | yes | maps `apps.srv_poi_info.is_active` | D-4. Java type follows `GOLD_TO_JAVA["BOOLEAN"] = "Boolean"` in `tests/test_srv_poi_serving_contract.py`. Placed after `is_bookable` (`isBookable`). Not in any DTO or JSON response |
| entities `SrvPoiInfo`, `SrvPoiMultiLang`, `SrvPoiAmenity`, `SrvPoiMediaGallery`, `SrvPoiReview` | `ingestion_ts` | `LocalDateTime` | yes | maps `apps.<table>.ingestion_ts` | D-4. Java type follows the mapping for `timestamp without time zone` already used by `deleted_at` (`LocalDateTime deletedAt`; `GOLD_TO_JAVA["TIMESTAMP"]`). Placed after `deletedAt`. Not in any DTO or JSON response |

- **Fresh-install DDL.** `CREATE TABLE` in `gld_srv_serve.pg.sql` must list every new column (`request.md` Constraints). The header ALTER note only records columns the user already added. The agent runs no ALTER (D-2).
- **Scope of `ingestion_ts`.** It is a PostgreSQL-only column. It has no `json_path`, no source, and no writer job, and nothing in the repository assigns it (D-2).

## Lineage

**`lh_vv_gold.dbo.gld_srv_poi_info`**
- Bronze: none.
- Silver: unchanged from `SPEC.inputs`: `slv_poi_entity_non_enrich`, `slv_enr_poi_destination`, `slv_enr_poi_info_multi_lang`, `slv_3p_poi_rating`, `slv_3p_poi_review`, and `slv_poi_media_info`.
- Gold: none. Gold does not read gold.
- `is_active` reads no input. It is a literal `true` (D-1).

**`apps.srv_poi_info`**
- Bronze and silver: none.
- Gold: `lh_vv_gold.dbo.gld_srv_poi_info`. The `sql/postgres/gld_srv_serve.pg.sql` header names `lh_vv_gold.dbo.gld_srv_poi_*` as the column source.
- `is_active` copies `gld_srv_poi_info.is_active` (D-2).
- `ingestion_ts` has no bronze, silver, or gold lineage. It exists only in PostgreSQL (D-2).

**`apps.srv_poi_multi_lang`, `apps.srv_poi_amenity`, `apps.srv_poi_media_gallery`, `apps.srv_poi_review`**
- Existing columns keep their gold lineage from the matching `gld_srv_poi_*` table, unchanged.
- `ingestion_ts` has no bronze, silver, or gold lineage. It exists only in PostgreSQL, and no writer job exists (D-2).

**Entities**
- Each entity reads only its `apps` table. The JSON API and `docs/context/api-mapping/` gain no lineage (D-4).

## Conflicts and questions

1. **Resolved by D-3: serving-contract exception.**
   - Current state: `test_gold_and_pg_columns_and_types_match` asserts that the gold and PostgreSQL column sets are equal. `test_entities_match_gold_columns_types_and_keys` asserts that the entity and gold column sets are equal. `ingestion_ts` breaks both.
   - Rule: `tests/test_srv_poi_serving_contract.py` may allow `ingestion_ts` on every `apps` table even though gold has no such column. D-4 requires the entities to map it, so the exception applies to both tests in that file.
   - No other gap is allowed. `apps.srv_poi_info.is_active` must match `gld_srv_poi_info.is_active`: `BOOLEAN` → `boolean` → `Boolean`.
   - This is a resolved rule, not an open question.
2. **Resolved by D-1: `is_active` and `deleted_at`.** `is_active` is `true` on every written row and does not depend on `deleted_at`. Soft-deleted rows can therefore carry `is_active = true`. This is intended.
3. **Open: `services/data-serving-service/AGENTS.md` `## Contract` wording.**
   - The section says columns and types come from gold, and that entities and DTOs expose only columns that exist there. `ingestion_ts` contradicts that wording.
   - `request.md` does not list `AGENTS.md` in scope.
   - Question: should the Contract text record the D-3 exception, or should only `model-design.md` and `decision.md` record it, as D-3 states?
4. **Open: which `NB_CREATE_DDL` cell carries the contract.**
   - `srvpoipy`, `srvratepy`, and `srvcoverpy` hold earlier frozen versions of the `gld_srv_poi_info` contract. Their markdown says not to rerun them after later cells.
   - `poidestpy` holds the current 35-column contract.
   - `request.md` asks for "the matching `NB_CREATE_DDL` contract" without naming a cell.
   - Question: should `is_active` go into `poidestpy` or into a new cell? The Architect decides; this design only fixes the column, type, nullability, and position.
5. **Open: `row_hash` coverage.**
   - `OUT_COLS` excludes `row_hash`, `created_at`, `updated_at`, and `deleted_at`, so the run library computes them. The files read do not show which columns feed `row_hash`.
   - Question: does adding `is_active` to `OUT_COLS` change `row_hash` for every existing row on the first run? If so, should that be expected?
6. **Open: Java type for `ingestion_ts`.**
   - This design uses `LocalDateTime`, by analogy with the existing `deleted_at` mapping (`timestamp without time zone`). No gold type exists to drive `GOLD_TO_JAVA`.
   - Question: confirm `LocalDateTime`, or name a different type.
7. **Open: PostgreSQL load path.**
   - The files read do not show how `apps.*` rows are loaded from gold. `request.md` mentions a Copy Job only as out of scope to run.
   - This design states only that `apps.srv_poi_info.is_active` copies the gold column (D-2). Mapping the new column in the load path, if it needs explicit mapping, is outside these files.
   - Question: does the load path need a change to carry `is_active`?
