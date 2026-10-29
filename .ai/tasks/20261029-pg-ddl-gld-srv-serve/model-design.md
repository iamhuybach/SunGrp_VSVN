# Model design: 20261029-pg-ddl-gld-srv-serve

## Scope

Base task: `20261029-pg-ddl-gld-srv-serve`. The deliverable is the PostgreSQL serving DDL file `sql/postgres/gld_srv_serve.sql` (see `request.md` In scope and `task-state.yaml` `scope.files`). This design covers only the five new PostgreSQL tables in schema `apps`. Fabric gold tables, keys, columns, notebooks, pipelines, and lakehouse DDL do not change.

`proposal.md` does not exist in this task, so it has no `## Dòng thay đổi` or `## ctrl_cfg_schema_registry` section to cite. `problem-analysis.md` and `requirements-analysis.md` do not exist either. This design implements these accepted ledger rows in `decision.md` `## Quyết định hiện hành`:

- D-TYPE: Fabric to PostgreSQL type mapping.
- D-SCHEMA: schema `apps`.
- D-NAME: table names drop the `gld_` prefix and start with `srv_`.
- D-LANG: `apps.srv_poi_review` has no `lang` column. Gold `gld_srv_poi_review.lang` stays as it is.
- D-BIGINT: `BIGINT` maps to `int8`.
- D-MODEL: `data_model_change` is set because of D-LANG. Keys stay `NodeSpec.pk`.

The column inventory comes from `decision.md` `## Bảng kiểm`. I checked it against the five `lh_vv_gold.dbo.gld_srv_poi_*` specs in `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables` (file lines 362–481) and found no differences.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `apps.srv_poi_info` | PostgreSQL serving copy of gold `lh_vv_gold.dbo.gld_srv_poi_info` | One row per `poi_id` | No PostgreSQL node. Source gold node: `notebooks/NB_GLD_SRV_POI_INFO.ipynb` (cell 4 `NodeSpec` `pk=("poi_id",)`) |
| `apps.srv_poi_multi_lang` | PostgreSQL serving copy of gold `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | One row per (`poi_id`, `lang`) | No PostgreSQL node. Source gold node: `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb` (cell 3 `NodeSpec` `pk=("poi_id", "lang")`) |
| `apps.srv_poi_amenity` | PostgreSQL serving copy of gold `lh_vv_gold.dbo.gld_srv_poi_amenity` | One row per (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) | No PostgreSQL node. Source gold node: `notebooks/NB_GLD_SRV_POI_AMENITY.ipynb` (cell 3 `NodeSpec` `pk=("poi_id", "business_sector", "amenity_group", "amenity_raw")`) |
| `apps.srv_poi_media_gallery` | PostgreSQL serving copy of gold `lh_vv_gold.dbo.gld_srv_poi_media_gallery` | One row per `media_id` | No PostgreSQL node. Source gold node: `notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb` (cell 3 `NodeSpec` `pk=("media_id",)`) |
| `apps.srv_poi_review` | PostgreSQL serving copy of gold `lh_vv_gold.dbo.gld_srv_poi_review`, without `lang` (D-LANG) | One row per `review_id` | No PostgreSQL node. Source gold node: `notebooks/NB_GLD_SRV_POI_REVIEW.ipynb` (cell 3 `NodeSpec` `pk=("review_id",)`) |

There is no sync job or node notebook for the PostgreSQL tables (`request.md` Out of scope).

## Keys

| table | primary key (order = `NodeSpec.pk`) | business key | foreign keys |
|---|---|---|---|
| `apps.srv_poi_info` | (`poi_id`) | `poi_id` | None declared. |
| `apps.srv_poi_multi_lang` | (`poi_id`, `lang`) | (`poi_id`, `lang`) | None declared. `poi_id` refers logically to `apps.srv_poi_info.poi_id`. |
| `apps.srv_poi_amenity` | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) | same as primary key | None declared. `poi_id` refers logically to `apps.srv_poi_info.poi_id`. |
| `apps.srv_poi_media_gallery` | (`media_id`) | `media_id` | None declared. `poi_id` (nullable) refers logically to `apps.srv_poi_info.poi_id`. |
| `apps.srv_poi_review` | (`review_id`) | `review_id` | None declared. `poi_id` (nullable) refers logically to `apps.srv_poi_info.poi_id`. |

Every primary-key column is `STRING NOT NULL` in gold DDL, so it is `text NOT NULL` in PostgreSQL (`decision.md` `## Bảng kiểm`, closing note). The gold DDL has no foreign-key constraints, and `request.md` forbids extra objects, so this design declares none. The relationships listed above are logical only.

`poi_id` formula source: `AGENTS.md` §7.

- Third party: `poi_id = uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`).
- Partner: `poi_id = uuid_format(md5(concat(id, 'partner')))`, 8-4-4-4-12.
- `poi_id` never includes language.

PostgreSQL does not compute `poi_id`. It copies the value from gold unchanged.

`review_id`, `media_id`, and the amenity key parts are copied from gold unchanged. The files I was allowed to read do not show their formulas (see Conflicts and questions item 3).

## Columns

Every column is new because the five tables are new. `G` stands for `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables`, followed by the file line of the gold column spec. Type rules cite D-TYPE unless another row is named. Nullability follows `request.md` Acceptance criteria: `NOT NULL` only where gold DDL says `NOT NULL`, plus primary-key columns.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `apps.srv_poi_info` | `poi_id` | `text` | NOT NULL | `gld_srv_poi_info.poi_id` (G L379, `STRING NOT NULL`) | PK 1 (`NodeSpec.pk`); D-TYPE; D-MODEL keys unchanged |
| `apps.srv_poi_info` | `poi_name` | `text` | yes | `gld_srv_poi_info.poi_name` (G L380, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `source_name` | `text` | yes | `gld_srv_poi_info.source_name` (G L381, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `business_sector` | `text` | yes | `gld_srv_poi_info.business_sector` (G L382, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `business_category` | `text` | yes | `gld_srv_poi_info.business_category` (G L383, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `subcategory_tags` | `text` | yes | `gld_srv_poi_info.subcategory_tags` (G L384, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `destination_id` | `text` | yes | `gld_srv_poi_info.destination_id` (G L385, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `full_address` | `text` | yes | `gld_srv_poi_info.full_address` (G L386, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `street` | `text` | yes | `gld_srv_poi_info.street` (G L387, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `ward` | `text` | yes | `gld_srv_poi_info.ward` (G L388, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `district` | `text` | yes | `gld_srv_poi_info.district` (G L389, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `city` | `text` | yes | `gld_srv_poi_info.city` (G L390, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `country_code` | `text` | yes | `gld_srv_poi_info.country_code` (G L391, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `postal_code` | `text` | yes | `gld_srv_poi_info.postal_code` (G L392, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `lat` | `double precision` | yes | `gld_srv_poi_info.lat` (G L393, `DOUBLE`) | D-TYPE |
| `apps.srv_poi_info` | `lng` | `double precision` | yes | `gld_srv_poi_info.lng` (G L394, `DOUBLE`) | D-TYPE |
| `apps.srv_poi_info` | `phone` | `text` | yes | `gld_srv_poi_info.phone` (G L395, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `email` | `text` | yes | `gld_srv_poi_info.email` (G L396, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `website_url` | `text` | yes | `gld_srv_poi_info.website_url` (G L397, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `operating_status` | `text` | yes | `gld_srv_poi_info.operating_status` (G L398, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `is_verified` | `boolean` | yes | `gld_srv_poi_info.is_verified` (G L399, `BOOLEAN`) | D-TYPE |
| `apps.srv_poi_info` | `is_recommended` | `boolean` | yes | `gld_srv_poi_info.is_recommended` (G L400, `BOOLEAN`) | D-TYPE |
| `apps.srv_poi_info` | `is_bookable` | `boolean` | yes | `gld_srv_poi_info.is_bookable` (G L401, `BOOLEAN`) | D-TYPE |
| `apps.srv_poi_info` | `operating_hours` | `text` | yes | `gld_srv_poi_info.operating_hours` (G L402, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `holiday_exceptions` | `text` | yes | `gld_srv_poi_info.holiday_exceptions` (G L403, `STRING`) | D-TYPE |
| `apps.srv_poi_info` | `rating_overall` | `numeric(4,2)` | yes | `gld_srv_poi_info.rating_overall` (G L404, `DECIMAL(4,2)`) | D-TYPE |
| `apps.srv_poi_info` | `rating_count` | `integer` | yes | `gld_srv_poi_info.rating_count` (G L405, `INT`) | D-TYPE |
| `apps.srv_poi_info` | `review_count` | `integer` | yes | `gld_srv_poi_info.review_count` (G L406, `INT`) | D-TYPE |
| `apps.srv_poi_info` | `row_hash` | `text` | yes | `gld_srv_poi_info.row_hash` (G L407, `STRING`) | D-TYPE; kept per `## Bảng kiểm` note |
| `apps.srv_poi_info` | `created_at` | `timestamp without time zone` | yes | `gld_srv_poi_info.created_at` (G L408, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_info` | `updated_at` | `timestamp without time zone` | yes | `gld_srv_poi_info.updated_at` (G L409, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_info` | `deleted_at` | `timestamp without time zone` | yes | `gld_srv_poi_info.deleted_at` (G L410, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_multi_lang` | `poi_id` | `text` | NOT NULL | `gld_srv_poi_multi_lang.poi_id` (G L364, `STRING NOT NULL`) | PK 1 (`NodeSpec.pk`); D-TYPE |
| `apps.srv_poi_multi_lang` | `lang` | `text` | NOT NULL | `gld_srv_poi_multi_lang.lang` (G L365, `STRING NOT NULL`) | PK 2 (`NodeSpec.pk`); D-TYPE. D-LANG applies only to review. |
| `apps.srv_poi_multi_lang` | `source_name` | `text` | yes | `gld_srv_poi_multi_lang.source_name` (G L366, `STRING`) | D-TYPE |
| `apps.srv_poi_multi_lang` | `time_to_spend` | `text` | yes | `gld_srv_poi_multi_lang.time_to_spend` (G L367, `STRING`) | D-TYPE |
| `apps.srv_poi_multi_lang` | `best_time` | `text` | yes | `gld_srv_poi_multi_lang.best_time` (G L368, `STRING`) | D-TYPE |
| `apps.srv_poi_multi_lang` | `cost_vnd` | `text` | yes | `gld_srv_poi_multi_lang.cost_vnd` (G L369, `STRING`) | D-TYPE |
| `apps.srv_poi_multi_lang` | `description` | `text` | yes | `gld_srv_poi_multi_lang.description` (G L370, `STRING`) | D-TYPE |
| `apps.srv_poi_multi_lang` | `experience` | `text` | yes | `gld_srv_poi_multi_lang.experience` (G L371, `STRING`) | D-TYPE |
| `apps.srv_poi_multi_lang` | `row_hash` | `text` | yes | `gld_srv_poi_multi_lang.row_hash` (G L372, `STRING`) | D-TYPE |
| `apps.srv_poi_multi_lang` | `created_at` | `timestamp without time zone` | yes | `gld_srv_poi_multi_lang.created_at` (G L373, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_multi_lang` | `updated_at` | `timestamp without time zone` | yes | `gld_srv_poi_multi_lang.updated_at` (G L374, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_multi_lang` | `deleted_at` | `timestamp without time zone` | yes | `gld_srv_poi_multi_lang.deleted_at` (G L375, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_amenity` | `poi_id` | `text` | NOT NULL | `gld_srv_poi_amenity.poi_id` (G L453, `STRING NOT NULL`) | PK 1 (`NodeSpec.pk`); D-TYPE |
| `apps.srv_poi_amenity` | `business_sector` | `text` | NOT NULL | `gld_srv_poi_amenity.business_sector` (G L454, `STRING NOT NULL`) | PK 2 (`NodeSpec.pk`); D-TYPE |
| `apps.srv_poi_amenity` | `amenity_group` | `text` | NOT NULL | `gld_srv_poi_amenity.amenity_group` (G L455, `STRING NOT NULL`) | PK 3 (`NodeSpec.pk`); D-TYPE |
| `apps.srv_poi_amenity` | `amenity_raw` | `text` | NOT NULL | `gld_srv_poi_amenity.amenity_raw` (G L456, `STRING NOT NULL`) | PK 4 (`NodeSpec.pk`); D-TYPE |
| `apps.srv_poi_amenity` | `amenity` | `text` | yes | `gld_srv_poi_amenity.amenity` (G L457, `STRING`) | D-TYPE |
| `apps.srv_poi_amenity` | `amenity_vi` | `text` | yes | `gld_srv_poi_amenity.amenity_vi` (G L458, `STRING`) | D-TYPE |
| `apps.srv_poi_amenity` | `service_flags` | `text` | yes | `gld_srv_poi_amenity.service_flags` (G L459, `STRING`) | D-TYPE |
| `apps.srv_poi_amenity` | `row_hash` | `text` | yes | `gld_srv_poi_amenity.row_hash` (G L460, `STRING`) | D-TYPE |
| `apps.srv_poi_amenity` | `created_at` | `timestamp without time zone` | yes | `gld_srv_poi_amenity.created_at` (G L461, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_amenity` | `updated_at` | `timestamp without time zone` | yes | `gld_srv_poi_amenity.updated_at` (G L462, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_amenity` | `deleted_at` | `timestamp without time zone` | yes | `gld_srv_poi_amenity.deleted_at` (G L463, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `media_id` | `text` | NOT NULL | `gld_srv_poi_media_gallery.media_id` (G L434, `STRING NOT NULL`) | PK 1 (`NodeSpec.pk`); D-TYPE |
| `apps.srv_poi_media_gallery` | `poi_id` | `text` | yes | `gld_srv_poi_media_gallery.poi_id` (G L435, `STRING`) | D-TYPE; not a key, so it stays nullable as in gold |
| `apps.srv_poi_media_gallery` | `source_name` | `text` | yes | `gld_srv_poi_media_gallery.source_name` (G L436, `STRING`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `photo_api_uri` | `text` | yes | `gld_srv_poi_media_gallery.photo_api_uri` (G L437, `STRING`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `display_order` | `integer` | yes | `gld_srv_poi_media_gallery.display_order` (G L438, `INT`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `width_px` | `integer` | yes | `gld_srv_poi_media_gallery.width_px` (G L439, `INT`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `height_px` | `integer` | yes | `gld_srv_poi_media_gallery.height_px` (G L440, `INT`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `photographer` | `text` | yes | `gld_srv_poi_media_gallery.photographer` (G L441, `STRING`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `blob_url` | `text` | yes | `gld_srv_poi_media_gallery.blob_url` (G L442, `STRING`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `thumbnail_url` | `text` | yes | `gld_srv_poi_media_gallery.thumbnail_url` (G L443, `STRING`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `is_cover` | `boolean` | yes | `gld_srv_poi_media_gallery.is_cover` (G L444, `BOOLEAN`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `is_active` | `boolean` | yes | `gld_srv_poi_media_gallery.is_active` (G L445, `BOOLEAN`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `row_hash` | `text` | yes | `gld_srv_poi_media_gallery.row_hash` (G L446, `STRING`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `created_at` | `timestamp without time zone` | yes | `gld_srv_poi_media_gallery.created_at` (G L447, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `updated_at` | `timestamp without time zone` | yes | `gld_srv_poi_media_gallery.updated_at` (G L448, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_media_gallery` | `deleted_at` | `timestamp without time zone` | yes | `gld_srv_poi_media_gallery.deleted_at` (G L449, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_review` | `review_id` | `text` | NOT NULL | `gld_srv_poi_review.review_id` (G L467, `STRING NOT NULL`) | PK 1 (`NodeSpec.pk`); D-TYPE; D-MODEL keys unchanged |
| `apps.srv_poi_review` | `poi_id` | `text` | yes | `gld_srv_poi_review.poi_id` (G L468, `STRING`) | D-TYPE; not a key, so it stays nullable as in gold |
| `apps.srv_poi_review` | `lang` | not created | — | `gld_srv_poi_review.lang` (G L469, `STRING`) | D-LANG: column omitted in PostgreSQL; gold column unchanged |
| `apps.srv_poi_review` | `rating_overall` | `numeric(4,2)` | yes | `gld_srv_poi_review.rating_overall` (G L470, `DECIMAL(4,2)`) | D-TYPE |
| `apps.srv_poi_review` | `rating_count` | `int8` | yes | `gld_srv_poi_review.rating_count` (G L471, `BIGINT`) | D-BIGINT; D-TYPE |
| `apps.srv_poi_review` | `title` | `text` | yes | `gld_srv_poi_review.title` (G L472, `STRING`) | D-TYPE |
| `apps.srv_poi_review` | `review_text` | `text` | yes | `gld_srv_poi_review.review_text` (G L473, `STRING`) | D-TYPE |
| `apps.srv_poi_review` | `rating` | `numeric(4,2)` | yes | `gld_srv_poi_review.rating` (G L474, `DECIMAL(4,2)`) | D-TYPE |
| `apps.srv_poi_review` | `review_date` | `text` | yes | `gld_srv_poi_review.review_date` (G L475, `STRING`) | D-TYPE; kept as `text` because gold is `STRING` |
| `apps.srv_poi_review` | `author_name` | `text` | yes | `gld_srv_poi_review.author_name` (G L476, `STRING`) | D-TYPE |
| `apps.srv_poi_review` | `row_hash` | `text` | yes | `gld_srv_poi_review.row_hash` (G L477, `STRING`) | D-TYPE |
| `apps.srv_poi_review` | `created_at` | `timestamp without time zone` | yes | `gld_srv_poi_review.created_at` (G L478, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_review` | `updated_at` | `timestamp without time zone` | yes | `gld_srv_poi_review.updated_at` (G L479, `TIMESTAMP`) | D-TYPE |
| `apps.srv_poi_review` | `deleted_at` | `timestamp without time zone` | yes | `gld_srv_poi_review.deleted_at` (G L480, `TIMESTAMP`) | D-TYPE |

Column order in each `CREATE TABLE` follows the gold DDL order, with `lang` removed from review.

None of the five gold specs uses a Fabric type outside D-TYPE, so no column is `MISSING`.

## Lineage

| table | bronze reads | silver reads | gold reads |
|---|---|---|---|
| `apps.srv_poi_info` | None | None | Content comes from `lh_vv_gold.dbo.gld_srv_poi_info` |
| `apps.srv_poi_multi_lang` | None | None | Content comes from `lh_vv_gold.dbo.gld_srv_poi_multi_lang` |
| `apps.srv_poi_amenity` | None | None | Content comes from `lh_vv_gold.dbo.gld_srv_poi_amenity` |
| `apps.srv_poi_media_gallery` | None | None | Content comes from `lh_vv_gold.dbo.gld_srv_poi_media_gallery` |
| `apps.srv_poi_review` | None | None | Content comes from `lh_vv_gold.dbo.gld_srv_poi_review`, minus `lang` |

The PostgreSQL tables live outside the Fabric medallion. They are one-to-one serving copies of gold tables, and no gold node reads them. This task does not change the upstream lineage of the gold nodes. The rule that gold never reads gold still holds: no Fabric gold table gains a gold input. This task does not define any process that loads PostgreSQL from gold. The sync job is out of scope (`request.md` Out of scope).

## Conflicts and questions

1. `proposal.md` is missing, so this design cannot cite `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. Following the author constraints, ledger rows D-TYPE, D-SCHEMA, D-NAME, D-LANG, D-BIGINT, and D-MODEL stand in for the proposal. No `ctrl_cfg_schema_registry` change is designed.
2. Two parts of `request.md` are overridden by the ledger:
   - User outcome and Acceptance criteria say "same columns" as gold. D-LANG overrides this for `apps.srv_poi_review`, which has no `lang`.
   - The Acceptance criteria type mapping has no `BIGINT`. D-TYPE and D-BIGINT add `BIGINT` → `int8`.
   - The file name `sql/postgres/gld_srv_serve.sql` keeps the `gld_` prefix. D-NAME covers table names only, so the file name is kept as `request.md` and `task-state.yaml` state it.
3. The files I was allowed to read do not show formulas for `review_id`, `media_id`, or the amenity key parts. PostgreSQL copies these values from gold and does not derive them, so no formula is designed.
   - The user comment "review_id bỏ field lang" was recorded in D-LANG as dropping the `lang` column, with the key unchanged. This design follows the ledger.
   - Because gold `NodeSpec.pk` is (`review_id`) alone, dropping `lang` does not change the grain.
   - Question: does "review_id bỏ field lang" also mean a change to how gold `review_id` is built? The ledger says no, and this design assumes no.
4. The `poi_id` relationships from the other four tables to `apps.srv_poi_info` are logical only. No foreign-key constraint is designed, because gold DDL declares none and `request.md` forbids extra objects. `poi_id` stays nullable in media and review, matching gold.
5. The line references in `decision.md` `## Bảng kiểm` (for example "init_tables L327") use a different numbering from the raw `.ipynb` file lines cited above (for example L379). Column names, order, and types match, so this is not a content conflict.
