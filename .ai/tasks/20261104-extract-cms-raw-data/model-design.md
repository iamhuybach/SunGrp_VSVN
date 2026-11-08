# Model design — 20261104-extract-cms-raw-data

## Scope

- Base task: `20261104-extract-cms-raw-data` (`task-state.yaml`: signal `data_model_change`, systems `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_ctrl`; `scope.files` lists `notebooks/NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb`, the two DDL notebooks, and the CMS context doc).
- Proposal sections implemented: `proposal.md` `## Giải pháp đề xuất`, option C, and the `$` → `DOC` row of the block table (`proposal.md:41`). For the object list, see `proposal.md` `## Dòng thay đổi` (rows for the new extract notebook, `ctrl_mng_pipeline_config`, and `ctrl_cfg_schema_registry`). `proposal.md` `## ctrl_cfg_schema_registry` ("Không áp dụng" until Q1–3 are answered) is superseded: D-05 answers Q1–3, and D-15 U4 accepts the earlier model Conflict 15. The `DOC_ARRAY` rows at `proposal.md:42-46` are replaced by JSON-text columns (column bundle, D-15 U4).
- Ledger rows implemented: D-01 (`DOC` only), D-02 (`SNAPSHOT_MODES`), D-03 (no partner activity), D-04 (no `pois[]` table, no `formats.*` path), D-05 (four tables, `source_name` mapping, `raw_payload`, MERGE key `document_id` + `locale` on all four tables, destination included), D-06 (bronze columns are `string`), D-10 (rejects go to `ctrl_cdc_reject`, no gold), D-12 (formats), D-13 (closed key sets), D-14 (event order facts), D-15 (U1 open/invalid payloads go to `ctrl_cdc_reject`; U2 notebook `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV`, `pl_name = PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, partner activity not attached; U3 signed URLs accepted; U4 column bundle accepted, null `locale` loaded, not rejected and not defaulted), and D-17 (U5: the recommended answers in `architecture.md` `## Required probes and decisions`).
- This revision applies D-17 / U5 only: `first_publish_date` moves from `DATE_DAYS` to `NONE` (B1), Conflicts 3, 4, and 5 are answered (B2), and a blank `locale` stays `''`. Grain, keys, `src_object = $`, `DOC`, and `cms_updated_at` on all four tables are unchanged (`architecture.md` `### PASS criteria for the next round`, item 3).
- Code facts cited, not asked again: `parse_json_strings` keeps nested objects and arrays as JSON text (`architecture.md` `## Verdict and blocking gaps`). In `CONVERT_RULES`, `NONE` is a plain cast and `DATE_DAYS` turns an integer day count into a `date` (`NB_LIB_EXTRACT_RAWDATA.md` `CONVERT_RULES` row; `architecture.md` `## Verdict and blocking gaps`). No CMS column uses `DATE_DAYS`.
- Out of scope (Architect): invariants, state ownership, commit boundaries, ordering, locking, watermark, idempotency, retry, recovery, rollout, and source routing.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_bronze.dbo.cms_raw_data` | bronze (read only) | One row per ingested event (`event_id`). Unchanged. | Not applicable (Eventstream landing) |
| `lh_vv_silver.dbo.slv_cms_blog` | silver L1 | One row per (`document_id`, `locale`) from events with `source_name = strapi_blog`. `src_object = $`, `load_mode = DOC`. | `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV` (D-15 U2) |
| `lh_vv_silver.dbo.slv_cms_destination` | silver L1 | One row per (`document_id`, `locale`) from `source_name = strapi_destination`. `$`, `DOC`. | same notebook |
| `lh_vv_silver.dbo.slv_cms_news` | silver L1 | One row per (`document_id`, `locale`) from `source_name = strapi_news`. `$`, `DOC`. | same notebook |
| `lh_vv_silver.dbo.slv_cms_promotion_article` | silver L1 | One row per (`document_id`, `locale`) from `source_name = strapi_ph_promotion_article`. `$`, `DOC`. | same notebook |
| `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` | ctrl | One row per target column. New rows only for `src_tbl = cms_raw_data`. | Seed in `NB_SETUP_INITIAL_DDL` + `NB_CREATE_DDL` (`proposal.md` `## Dòng thay đổi`) |
| `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` | ctrl | One row per target table. Four new rows. | Same seed notebooks |
| `lh_vv_ctrl.dbo.ctrl_cdc_reject` | ctrl | Existing grain, unchanged. Receives open and invalid CMS payloads (D-10, D-15 U1). | Written by `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV` |

No fifth silver table, no `DOC_ARRAY` table, no `pois[]` table (D-04), and no gold (D-10). Array and object blocks are JSON-text columns on the four tables (D-15 U4).

## Keys

| table | primary / MERGE key | business key | foreign keys |
|---|---|---|---|
| `slv_cms_blog` | `document_id` (`key_order` 1), `locale` (`key_order` 2) (D-05) | same as primary | None. Raw `destination` is not modelled (D-17, Conflict 3). `pois_json` is JSON text, not a key. |
| `slv_cms_destination` | `document_id` (1), `locale` (2) (D-05, destination included) | same | None. `pois[]` element type stays `MISSING_EVIDENCE` (D-04). |
| `slv_cms_news` | `document_id` (1), `locale` (2) (D-05) | same | None |
| `slv_cms_promotion_article` | `document_id` (1), `locale` (2) (D-05) | same | None. `pois_json` is JSON text, not a key. |
| `cms_raw_data` | `event_id` (bronze ingest id, unchanged) | — | — |

- `id` is not a key. It is a plain `bigint` column (column bundle).
- `poi_id`: not applicable. The formulas in `AGENTS.md` §7 (third party `uuid_format(md5(concat(source_name, source_id)))` / `HASH_MD5_UUID`; partner `uuid_format(md5(concat(id, 'partner')))`) need a `source_id` or a partner `id`. The CMS key sets in `cms-closed-key-census.md` `## Parsed key sets` have neither. No CMS table carries or derives `poi_id`. Document identity and state granularity for the lib are Architect decisions (`architecture.md` A4), not modelled here.
- `locale` in the key: a null `locale` is loaded as its own key value and a blank `locale` stays `''` as a separate key value (D-15 U4, D-17). How the key is matched is `architecture.md` A6, not modelled here.

## Columns

Every business column below is one `ctrl_cfg_schema_registry` row with `src_schema = lh_vv_bronze.dbo`, `src_tbl = cms_raw_data`, `src_object_schema = NULL`, `src_object = $`, `trg_schema = lh_vv_silver.dbo`, `is_toast = false`, `is_active = true` (same registry rules as the previous revision). Every `json_path` is a top-level key listed for that source in `cms-closed-key-census.md` `## Parsed key sets`. `convert_rule` is NULL unless stated. No CMS registry row uses `DATE_DAYS` (D-17). JSON-text columns rely on `parse_json_strings` (`architecture.md` `## Verdict and blocking gaps`). Their `data_type` is `string`, and a JSON null in the payload gives a NULL column. Signed URLs inside JSON text are accepted (D-15 U3). The `*_json` column names are accepted (D-17, Conflict 4).

### Columns shared by all four tables

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| all four | `document_id` | `string` | no (key) | `json_path = documentId` | `is_key`, `key_order` 1 (D-05). Key present in all four key sets (D-13). |
| all four | `locale` | `string` | yes | `json_path = locale` | `is_key`, `key_order` 2 (D-05). Plain payload field, not `_langs` / `RAW_LANG`, never filled from bronze `type` (`proposal.md` `## Ràng buộc cho Architect` item 5). No convert rule (D-17, Conflict 5); closed values are lowercase `vi`, `en`, `ko` plus 9 blank blog rows (D-12). A blank value stays `''` (D-17). A null value is loaded, not rejected, and not defaulted (D-15 U4; `architecture.md` A6). |
| all four | `id` | `bigint` | yes | `json_path = id` | Column bundle (D-15 U4). Spark TYPE `long` on the first blog object (`cms-closed-key-census.md`). Not a key. |
| all four | `slug` | `string` | yes | `json_path = slug` | Kept, same name on all four tables (column bundle). |
| all four | `cms_created_at` | `timestamp` | yes | `json_path = createdAt` | `convert_rule = ISO_UTC_TS` (column bundle; ISO-with-Z on closed rows, D-12). |
| all four | `cms_updated_at` | `timestamp` | yes | `json_path = updatedAt` | `ISO_UTC_TS` (D-12). Active registry column on all four tables; used by the Architect's ordering (`architecture.md` A5), not designed here. |
| all four | `cms_published_at` | `timestamp` | yes | `json_path = publishedAt` | `ISO_UTC_TS` (D-12). |
| all four | `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`, `created_at`, `updated_at` | per lib (`_crawled_at`, `_first_seen_at`, `_last_seen_at`, `created_at`, `updated_at` TIMESTAMP; `_event_id` STRING) | lib-managed | `SNAPSHOT_TECH_COLUMNS` | `NB_LIB_EXTRACT_RAWDATA.md` `### §1 constants`. Not registry rows. Bronze `crawled_at` matches ISO-with-Z on every row, `try_cast` null count 0 (D-12). |

### `slv_cms_blog`

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_cms_blog` | `title` | `string` | yes | `json_path = title` | Blog key set (D-13). |
| `slv_cms_blog` | `sapo` | `string` | yes | `json_path = sapo` | Blog key set (D-13). |
| `slv_cms_blog` | `first_publish_date` | `date` | yes | `json_path = first_publish_date` | `convert_rule = NONE` (plain cast, `NB_LIB_EXTRACT_RAWDATA.md` `CONVERT_RULES`) (D-17, `architecture.md` B1). `yyyy-MM-dd` on 79756 closed rows (D-12). Non-matching closed rows are the rollout gate `architecture.md` A7, not a model question. |
| `slv_cms_blog` | `block_content_json` | `string` | yes | `json_path = block_content` | JSON text (`parse_json_strings`). TYPE `array` on the first blog object. |
| `slv_cms_blog` | `seo_json` | `string` | yes | `json_path = SEO` | JSON text. Object on all 40 parsed blog rows (`cms-closed-key-census.md`). Name accepted (D-17). |
| `slv_cms_blog` | `platforms_json` | `string` | yes | `json_path = platforms` | JSON text. TYPE `array`. Name accepted (D-17). |
| `slv_cms_blog` | `pois_json` | `string` | yes | `json_path = pois` | JSON text. TYPE `array`. Element type stays `MISSING_EVIDENCE` (D-04). No sub-path. Name accepted (D-17). |

Blog `author`, `cover_image`, `destination`, and `gallery` are not modelled (D-17, Conflict 3).

### `slv_cms_destination`

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_cms_destination` | `name` | `string` | yes | `json_path = name` | Destination key set (D-13). |
| `slv_cms_destination` | `description` | `string` | yes | `json_path = description` | Destination key set (D-13). |
| `slv_cms_destination` | `cover_gallery_json` | `string` | yes | `json_path = cover_gallery` | JSON text. Array of object (`proposal.md:42`). No `formats.*` path (D-04). Name accepted (D-17). |
| `slv_cms_destination` | `seo_json` | `string` | yes | `json_path = SEO` | JSON text. Array of object (`proposal.md:43`). Name accepted (D-17). |
| `slv_cms_destination` | `faq_json` | `string` | yes | `json_path = FAQ` | JSON text (`proposal.md:44`). Name accepted (D-17). |
| `slv_cms_destination` | `experiences_json` | `string` | yes | `json_path = experiences` | JSON text (`proposal.md:45`). Name accepted (D-17). |
| `slv_cms_destination` | `highlight_json` | `string` | yes | `json_path = highlight` | JSON text (`proposal.md:46`). Name accepted (D-17). |
| `slv_cms_destination` | `pois_json` | `string` | yes | `json_path = pois` | JSON text. Element type `MISSING_EVIDENCE` (D-04, `proposal.md:47`). Name accepted (D-17). |

`rank`, `tags`, `hooks`, and `sections` are dropped (column bundle). They are also absent from the 50 parsed destination rows (D-13).

### `slv_cms_news`

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_cms_news` | `title` | `string` | yes | `json_path = title` | News key set (D-13). |
| `slv_cms_news` | `sapo` | `string` | yes | `json_path = sapo` | News key set (D-13). |
| `slv_cms_news` | `is_featured` | `boolean` | yes | `json_path = is_featured` | News key set. TYPE `boolean` (previous revision). |
| `slv_cms_news` | `block_content_json` | `string` | yes | `json_path = block_content` | JSON text (`parse_json_strings`). |
| `slv_cms_news` | `seo_json` | `string` | yes | `json_path = SEO` | JSON text. Null on 42 and object on 8 of 50 parsed rows (D-13). Name accepted (D-17). |
| `slv_cms_news` | `news_category_json` | `string` | yes | `json_path = news_category` | JSON text. Null on 20 and object on 30 (D-13). Replaces the dropped split columns. Name accepted (D-17). |

News `cover_image` is not modelled (D-17, Conflict 3).

### `slv_cms_promotion_article`

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_cms_promotion_article` | `title` | `string` | yes | `json_path = title` | Promotion key set (D-13). |
| `slv_cms_promotion_article` | `short_description` | `string` | yes | `json_path = shortDescription` | Promotion key set. |
| `slv_cms_promotion_article` | `voucher_code` | `string` | yes | `json_path = voucherCode` | Promotion key set. |
| `slv_cms_promotion_article` | `promotion_start_datetime` | `timestamp` | yes | `json_path = promotionStartDateTime` | `ISO_UTC_TS`. ISO-with-Z on 8023 closed rows (D-12). |
| `slv_cms_promotion_article` | `promotion_end_datetime` | `timestamp` | yes | `json_path = promotionEndDateTime` | `ISO_UTC_TS` (D-12). |
| `slv_cms_promotion_article` | `usage_start_datetime` | `timestamp` | yes | `json_path = usageStartDateTime` | `ISO_UTC_TS` (D-12). |
| `slv_cms_promotion_article` | `usage_end_datetime` | `timestamp` | yes | `json_path = usageEndDateTime` | `ISO_UTC_TS` (D-12). |
| `slv_cms_promotion_article` | `content_json` | `string` | yes | `json_path = content` | JSON text (`parse_json_strings`). |
| `slv_cms_promotion_article` | `terms_json` | `string` | yes | `json_path = termsAndConditions` | JSON text (`parse_json_strings`). |
| `slv_cms_promotion_article` | `pois_json` | `string` | yes | `json_path = pois` | JSON text. Element type `MISSING_EVIDENCE` (D-04). Name accepted (D-17). |

`column_order` per table: `document_id`, `locale`, `id`, `slug`, `cms_created_at`, `cms_updated_at`, `cms_published_at`, then the table-specific columns in the row order above.

Dropped by the column bundle (D-15 U4): `plain_text_*`, split URL columns (`cover_image_*_url`, `gallery_urls`), `seo_title`, `seo_meta_description`, `news_category_key`, `news_category_name`, `poi_ids`, `rank`, `tags`, `hooks`, `sections`. The old `name_normalized` rename of destination `slug` is not used. Not modelled by D-17: blog `author`, `cover_image`, `destination`, `gallery`, and news `cover_image`.

### `ctrl_mng_pipeline_config` rows

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `ctrl_mng_pipeline_config` | `src_schema` / `src_tbl` | `string` | no | `lh_vv_bronze.dbo` / `cms_raw_data` | `proposal.md` `## Dòng thay đổi` (pipeline_config row) |
| `ctrl_mng_pipeline_config` | `trg_schema` / `trg_tbl` | `string` | no | `lh_vv_silver.dbo` / one of the four `slv_cms_*` | D-05, D-10 |
| `ctrl_mng_pipeline_config` | `load_mode` | `string` | no | `DOC` for all four | D-01, `proposal.md:41` |
| `ctrl_mng_pipeline_config` | `pl_name` | `string` | no | `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` | D-15 U2. The partner activity is not attached (D-03). |
| `ctrl_mng_pipeline_config` | `align_path` | `string` | yes | NULL | `proposal.md` `## Dòng thay đổi` (not proposed) |

## Lineage

| target | bronze read | silver read | gold read |
|---|---|---|---|
| `slv_cms_blog` | `lh_vv_bronze.dbo.cms_raw_data` (`raw_payload`, `event_id`, `crawled_at`, `source_name`), rows with `source_name = strapi_blog` | none | none |
| `slv_cms_destination` | same table, `source_name = strapi_destination` | none | none |
| `slv_cms_news` | same table, `source_name = strapi_news` | none | none |
| `slv_cms_promotion_article` | same table, `source_name = strapi_ph_promotion_article` | none | none |
| `ctrl_cdc_reject` (write) | open and invalid `cms_raw_data` payloads (D-10, D-15 U1) | none | none |

The extract also reads `ctrl_mng_pipeline_config`, `ctrl_cfg_schema_registry`, and `ctrl_mng_watermark`. Bronze `type` is never read (`proposal.md` constraint 5). No gold table is read or written (D-10), so the rule that gold never reads gold holds. The old CG steps are not carried over.

## Conflicts and questions

1. **Null and blank `locale` in the MERGE key.** Answered. The null half is answered by `architecture.md` A6 (null `locale` is loaded, D-15 U4). The blank half is answered by D-17: a blank `locale` stays `''` as its own key value, with no convert rule.
2. **Timestamp and date values that do not match the format.** Answered. The `DATE_DAYS` half is closed: `first_publish_date` is `date` with `NONE` (D-17, `architecture.md` B1). The 14 non-matching closed blog values (D-12) are the rollout gate `architecture.md` A7 (probe P4, decision U6 if needed), not an open model question.
3. **Payload keys covered by neither the keep list nor the drop list.** Answered (D-17). Blog `author`, `cover_image`, `destination`, `gallery`, and news `cover_image` are not modelled. They can be added later with `ADD COLUMNS` plus `full_reload` (`architecture.md` `## Required probes and decisions`).
4. **Names of the new JSON-text columns.** Answered (D-17). `seo_json`, `platforms_json`, `pois_json`, `cover_gallery_json`, `faq_json`, `experiences_json`, `highlight_json`, and `news_category_json` are accepted as physical names (`02_NAMING_CONVENTION.md` §5.1 `*_json` suffix). `block_content_json`, `content_json`, and `terms_json` are unchanged.
5. **`locale` normalization.** Answered (D-17). No convert rule on `locale`; no `LOWER_TRIM`.
6. **Prefix `slv_cms_` in the naming docs.** Out of scope for this task. The prefix is locked (D-05, D-15 U4) but is not in `02_NAMING_CONVENTION.md` §1 or `AGENTS.md` §7, and `02_NAMING_CONVENTION.md` is not in `scope.files`. `architecture.md` B2' leaves it to a follow-up task.
7. **Left to the Architect, not modelled here.** Answered by `architecture.md` A5 (ordering by `cms_updated_at` first, D-14). Source routing (A2) and state granularity (A4) also stay with the Architect.
