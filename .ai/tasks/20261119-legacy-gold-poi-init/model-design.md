# Model design: 20261119-legacy-gold-poi-init

## Scope

- **Base task**: `20261119-legacy-gold-poi-init`. In `task-state.yaml` the status is `waiting_evidence`, `architecture_required: true`, and `gates.architecture: evidence_required`.
- **No proposal**: `proposal.md` does not exist, so this design cannot cite its `## Dòng thay đổi` or `## ctrl_cfg_schema_registry` (Conflict 1). There is also no `problem-analysis.md` or `requirements-analysis.md`.
- **Ledger rows implemented** (`decision.md` `## Quyết định hiện hành`):
  - **D-01**: the map lives in `lh_vv_gold` with the `gld_` prefix and has one row per old `poi_id`. A one-time init copies old gold into new gold. Only the init notebook reads the other gold.
  - **D-02**: only columns that pair with an existing `gld_srv_*` table are filled. No business table is created.
  - **D-03**: the old model is in `sgr_visitvn_prd_batch` and the new one is in `sgr_visitvn_dev`. Names are written in full as `workspace.lakehouse.dbo.table`.
  - **D-04**: option B. `load_origin` STRING is on `gld_srv_poi_info`, `gld_srv_poi_multi_lang` and `gld_srv_poi_review`, and init writes `LEGACY_INIT`. It is unchanged here and not reopened.
  - **D-05**: map `lh_vv_gold.dbo.gld_poi_legacy_id_map` and one-time notebook `NB_SETUP_LEGACY_GOLD_POI`. Neither is on the 15-minute pipeline.
  - **D-06**: `gld_srv_poi_info.poi_name` and `district` come from the old `poi_master` row with `lang = vi` for the same `source_id`. No other lang is used.
- **Evidence used**:
  - P1 `evidence/results/legacy_gold_types.txt`
  - P2 `evidence/results/legacy_key_overlap.txt`
  - P4 `evidence/results/legacy_lang_payload_diff.txt`
  - the author input of this run
- **What changed from the previous revision**:
  - D-06 is applied. Previous Conflicts 3, 7 and 8 are closed by D-05, P1 and P4.
  - The `poi_id` SQL form now follows P2.
  - Init does not update keys that already exist in the targets.
- **Not reopened**: review loading (init still writes no review rows), the map name, and `load_origin`.
- **Left to the Architect**: MERGE predicates, the `sql_merge_target` and `TECH_COLUMNS` handling of `load_origin`, write order, commit boundaries, idempotency, rollback and expiry.
- **Not affected**:
  - `gld_srv_poi_amenity` and `gld_srv_poi_media_gallery`.
  - The watermark, sync, audit and non-POI old tables.

## Entities and grain

Old tables are read from `sgr_visitvn_prd_batch.lh_vv_gold.dbo.*`. New tables are in `sgr_visitvn_dev.lh_vv_gold.dbo.*` (D-03).

| table | layer | grain | node notebook |
|---|---|---|---|
| `gld_poi_legacy_id_map` (new) | gold `lh_vv_gold.dbo` | One row per old `poi_master.poi_id` (D-01) | `NB_SETUP_LEGACY_GOLD_POI` only. This is a one-time manual run (D-05; `02_NAMING_CONVENTION.md` §2 `NB_SETUP_<LUỒNG>`). It has no `ctrl_mng_pipeline_config` row and is on no 15M or 30M flow. |
| `gld_srv_poi_info` (existing) | gold `lh_vv_gold.dbo` | One row per new `poi_id` | Periodic: `NB_GLD_SRV_POI_INFO`. One-time: `NB_SETUP_LEGACY_GOLD_POI` |
| `gld_srv_poi_multi_lang` (existing) | gold `lh_vv_gold.dbo` | One row per (`poi_id`, `lang`) | Periodic: `NB_GLD_SRV_POI_MULTI_LANG`. One-time: `NB_SETUP_LEGACY_GOLD_POI` |
| `gld_srv_poi_review` (existing) | gold `lh_vv_gold.dbo` | One row per `review_id` | Periodic: `NB_GLD_SRV_POI_REVIEW`. It only gets the `load_origin` column (D-04). Init writes no rows here. |

## Keys

### `gld_poi_legacy_id_map`

- **Primary key**: `legacy_poi_id`, which is the old `poi_master.poi_id` (D-01).
- **Business key**: (`legacy_ingestion_source`, `source_id`, `lang`). It is not unique. One partner `source_id` has two old `poi_id` values on `lang = vi` (P4; `decision.md` `## Giả định còn lại`). Both map rows stay, and no winner is picked.
- **Foreign keys**: none are enforced. The new `poi_id` is computed only from the map row's own columns. It is never looked up in silver or in new gold.

### New `poi_id` formula

- **Sources**:
  - `AGENTS.md` §7: third-party `uuid_format(md5(concat(source_name, source_id)))`, and partner `uuid_format(md5(concat(id, 'partner')))` (`uuid_md5(id, lit('partner'))`).
  - P2 header: "Formula regexp_replace(md5(...)), same shape as uuid_md5".
- **SQL form**: `uuid_format` is not on the SQL path (author input). Init uses `regexp_replace(md5(concat(...)), '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5')`.
  - **Google** (`legacy_ingestion_source = 'google'`): the `concat` input is `'google', source_id`.
  - **Partner** (`legacy_ingestion_source = 'partner_portal'`): the `concat` input is `source_id, 'partner'`. `partner_portal` is never part of the hash input.
- **Blank `source_id`, or NULL `source_name`**: `poi_id` is NULL and `poi_id_status` is `MISSING_EVIDENCE`.
- **Language**: `lang` is never part of the hash (`AGENTS.md` §7; `decision.md` `## Quyết định của người dùng`).
- **Proof**: P2 shows the formula matches keys the pipeline already wrote: google 19594/45521 and partner 151/155 on info.

### Existing targets (keys unchanged)

| table | key | foreign keys |
|---|---|---|
| `gld_srv_poi_info` | `poi_id` (STRING NOT NULL) | none |
| `gld_srv_poi_multi_lang` | (`poi_id`, `lang`), both STRING NOT NULL | `poi_id` → `gld_srv_poi_info.poi_id`, logical only |
| `gld_srv_poi_review` | `review_id` (STRING NOT NULL) | `poi_id`, logical only |

### Rules for init target keys

1. **Key source**: every init row takes `poi_id` from the map, joined on `legacy_poi_id` = the old row's `poi_id`. Map rows with `MISSING_EVIDENCE` go to no target.
2. **Existing keys are not updated** (author input; P2):
   - These keys are already live, and none is soft-deleted: on `gld_srv_poi_info`, 19594 google and 151 partner; on `gld_srv_poi_multi_lang`, 58536 google and 436 partner pairs.
   - Init leaves those keys unchanged.
   - How this is enforced is a MERGE predicate for the Architect.
3. **`gld_srv_poi_info` conflicting key**:
   - Collect every old `poi_master` row that resolves to one new `poi_id`, across all langs and both partner old ids.
   - **Compared columns**: `business_sector`, `business_category`, `subcategory_tags`, `operating_status`, `is_verified`, `is_bookable`, and for google also `rating_overall` and `rating_count`.
   - If any compared column differs across those rows, the `poi_id` is not written.
   - **`poi_name` and `district` are not compared across langs.** They come from the `vi` row (D-06).
   - **No `vi` row**: `poi_name` and `district` stay NULL. The row is still written if the compared columns agree (author input).
   - **More than one `vi` row** (the partner `source_id` in P4): no winner is picked (author input). If the two `vi` rows differ on `poi_name` or `district`, the `poi_id` is not written (Conflict 3).
4. **`gld_srv_poi_multi_lang` conflicting key**:
   - If the old rows for one (`poi_id`, `lang`) differ on any loaded column, that key is not written. This covers the two partner old ids on `vi`.
   - If they are identical, the key is written once.
5. **Map rows stay**: the map keeps every row, whether or not its key is written.

## Columns

Target types come from the latest contract cell in `NB_CREATE_DDL`. Old types come from P1.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `gld_poi_legacy_id_map` | `legacy_poi_id` | STRING | no | old `poi_master.poi_id` (string, P1) | PK; D-01 |
| `gld_poi_legacy_id_map` | `lang` | STRING | yes | old `poi_master.lang` | copied as is; D-01 |
| `gld_poi_legacy_id_map` | `legacy_ingestion_source` | STRING | yes | old `poi_master.ingestion_source` | copied as is; `*_source` suffix per `02_NAMING_CONVENTION.md` §5.1 |
| `gld_poi_legacy_id_map` | `source_id` | STRING | yes | old `poi_master.source_id` | copied as is; D-01 |
| `gld_poi_legacy_id_map` | `source_name` | STRING | yes | derived | `google` → `google`; `partner_portal` → `partner`; any other value → NULL (`decision.md` `## Quyết định của người dùng`) |
| `gld_poi_legacy_id_map` | `poi_id` | STRING | yes | derived | `regexp_replace(md5(...))` form in `## Keys`; NULL when it cannot be computed |
| `gld_poi_legacy_id_map` | `poi_id_status` | STRING | no | derived | `OK` when `poi_id` is computed, else `MISSING_EVIDENCE` |
| `gld_srv_poi_info` | `poi_id` | STRING | no | map `poi_id` | `## Keys`; existing keys not updated (P2) |
| `gld_srv_poi_info` | `source_name` | STRING | yes | map `source_name` | D-01 |
| `gld_srv_poi_info` | `poi_name` | STRING | yes | old `poi_master.poi_name` from the row with `lang = vi` | D-06; NULL when no `vi` row exists (author input); not compared across langs (P4: 32883/45514 differ) |
| `gld_srv_poi_info` | `district` | STRING | yes | old `poi_master.district` from the row with `lang = vi` | D-06; NULL when no `vi` row exists; not compared across langs (P4: 3558 differ) |
| `gld_srv_poi_info` | `business_sector` | STRING | yes | old `poi_master`, same name (string) | D-02; must agree across langs (P4: 0 differ) |
| `gld_srv_poi_info` | `business_category` | STRING | yes | old `poi_master`, same name (string) | D-02; must agree across langs (P4: 3 differ, so those keys are not written) |
| `gld_srv_poi_info` | `subcategory_tags` | STRING | yes | old `poi_master`, same name (string, P1) | D-02; loaded as is (author input: string); must agree across langs; the diff count is not in P4 (Conflict 4) |
| `gld_srv_poi_info` | `operating_status` | STRING | yes | old `poi_master`, same name (string) | D-02; must agree across langs (P4: 0 differ) |
| `gld_srv_poi_info` | `is_verified`, `is_bookable` | BOOLEAN | yes | old `poi_master`, same name (boolean, P1) | D-02; no cast; must agree across langs (P4: 0 differ) |
| `gld_srv_poi_info` | `is_active` | BOOLEAN | yes | constant `true` | follows the mapping (`NB_CREATE_DDL` writes `true` on every row); old `poi_master.is_active` is not read and not compared (Conflict 6) |
| `gld_srv_poi_info` | `rating_overall` | DECIMAL(4,2) | yes | old `poi_master.rating_overall` `decimal(3,1)`, google rows only; NULL for partner rows | cast to DECIMAL(4,2) with 0 failures (P1); google only per `mapping_gld_srv_poi_info.md` §1.2; must agree across langs (P4: 12 differ) |
| `gld_srv_poi_info` | `rating_count` | INT | yes | old `poi_master.rating_count` `bigint`, google rows only; NULL for partner rows | cast to INT with 0 failures (P1); google only; must agree across langs (P4: 120 differ) |
| `gld_srv_poi_info` | `load_origin` | STRING | yes | constant | `LEGACY_INIT` on init inserts; D-04 |
| `gld_srv_poi_multi_lang` | `poi_id` | STRING | no | map `poi_id` | `## Keys`; existing pairs not updated (P2) |
| `gld_srv_poi_multi_lang` | `lang` | STRING | no | map `lang` | name pair |
| `gld_srv_poi_multi_lang` | `source_name` | STRING | yes | map `source_name` | never taken from `poi_enrichment_display.ingestion_source` |
| `gld_srv_poi_multi_lang` | `description`, `time_to_spend`, `best_time` | STRING | yes | old `poi_enrichment_display`, same name (string, P1) | D-02; name pair with DDL |
| `gld_srv_poi_multi_lang` | `cost` | STRING | yes | old `poi_enrichment_display.cost` (string, P1) | current contract `cost` (`NB_CREATE_DDL` cells `enrgldpy` and `enrbrzcfgpy`); not loaded if the target still has `cost_vnd` (Conflict 7) |
| `gld_srv_poi_multi_lang` | `load_origin` | STRING | yes | constant | `LEGACY_INIT` on init inserts; D-04 |
| `gld_srv_poi_review` | `load_origin` | STRING | yes | none from init | column added per D-04; init writes no review rows |

### Technical columns

- **`gld_srv_*` init rows**: `row_hash`, `created_at`, `updated_at` and `deleted_at` follow `02_NAMING_CONVENTION.md` §5.2.
  - `row_hash = sha2(to_json(struct(business columns)), 256)`.
  - `deleted_at` is NULL.
  - `created_at` and `updated_at` are the load time.
  - `load_origin` is excluded from `row_hash` (D-04).
- **`gld_poi_legacy_id_map`**: no technical columns. It is not written by a recompute flow and is not a lib MERGE target.

### Not loaded

- **`gld_srv_poi_review`**: no rows. The review decision is unchanged and not reopened.
- **`gld_srv_poi_info`**:
  - These columns have no pair: `destination_id`, `destination_name`, `full_address`, `street`, `ward`, `city`, `country_code`, `postal_code`, `lat`, `lng`, `phone`, `email`, `website_url`, `is_recommended`, `operating_hours`, `holiday_exceptions`, `review_count`, `cover_id`, `cover_blob_url`.
  - `poi_name` and `district` from non-`vi` rows.
  - Old `is_active`.
  - Old partner rating values.
- **`gld_srv_poi_multi_lang`**:
  - `experience` (Conflict 9).
  - `cost_vnd`.
- **D-02 tables**:
  - `poi_rating` and `ai_poi_rating`: no column pairs.
  - `ai_poi_review`: review is not loaded.
  - `ai_poi`, `ai_enriched_poi` and `poi_address_enrichment_staging`: their column lists are unread (Conflict 8).
- **Old `poi_master` columns with no target**: `slug`, `short_description`, `short_address`, `destination_ids`, `destination_names`, `nearby_pois`, `version`, `event_id`, `ref_type`, `ref_business_sector`, `partner_id`, `poi_group_id`.

## Lineage

- **Bronze**: none.
- **Silver**: none. A partner id missing from `slv_pn_business_services` still gets a `poi_id`.
- **Gold**: the one-time setup reads old gold in `sgr_visitvn_prd_batch` and writes new gold in `sgr_visitvn_dev`.

| new table | reads |
|---|---|
| `gld_poi_legacy_id_map` | old `poi_master` |
| `gld_srv_poi_info` | old `poi_master` (all langs for the compared columns; the `vi` row for `poi_name` and `district`) + `gld_poi_legacy_id_map` |
| `gld_srv_poi_multi_lang` | old `poi_enrichment_display` + `gld_poi_legacy_id_map` |
| `gld_srv_poi_review` | none (only the `load_origin` column is added) |

"Gold never reads gold" (`AGENTS.md` §7):

- The only exception is `NB_SETUP_LEGACY_GOLD_POI`, the time-limited exception in D-01.
- Init computes no value from new `gld_srv_*` rows. The "existing keys are not updated" rule only checks the write target's own keys, and that check belongs to the Architect's MERGE design.
- No periodic node reads old gold or the map.

## Conflicts and questions

1. **No `proposal.md`.** The handoff asks for citations of `## Dòng thay đổi` and `## ctrl_cfg_schema_registry`. The file does not exist, so this design cites only D-01 to D-06 and the probes. Should a proposal be written, or does the ledger stand in for it?
2. **`poi_id` formula text versus SQL form.** `AGENTS.md` §7 writes the formula with `uuid_format`, but the SQL path uses `regexp_replace(md5(...))` (author input; P2). The two give the same 8-4-4-4-12 shape, and P2 shows matching keys. Should the `regexp_replace` form be recorded in `decision.md` as the SQL equivalent?
3. **Partner `source_id` with two `vi` rows.** No winner is picked. This design compares `poi_name` and `district` between the two `vi` rows and skips the `poi_id` if they differ.
   - The ledger sentence "payload còn lại khác nhau" does not say whether `poi_name` and `district` count as part of that payload. Please confirm.
   - The probes also do not show whether this `poi_id` is among the 151 partner keys already live on info. If it is, init writes nothing for it anyway.
4. **`subcategory_tags` cross-lang diff.** P4 has no `subcategory_tags_diff` column, so the number of google keys skipped because of this column is unknown.
5. **Size of the info skip set is unknown.** P4 gives one count per column (category 3, `rating_overall` 12, `rating_count` 120), but not their union, and not how many of those keys are already live (P2). The number of new info rows init will write is therefore not known.
6. **`is_active`.** Init writes `true`, following the mapping. Please confirm this is what "follow the mapping" means, rather than leaving the column NULL.
7. **`cost` versus `cost_vnd`.** The current contract is `cost`, which pairs by name with the old `poi_enrichment_display.cost`.
   - If runbook B5 has not run in `sgr_visitvn_dev` and the target still has `cost_vnd`, the column is not loaded.
   - Please confirm that `cost` should load, and whether B5 has run.
8. **D-02 column lists not read.** `ai_poi`, `ai_enriched_poi` and `poi_address_enrichment_staging` stay unloaded until their writer column lists are given (NB_50 `_ai_poi_common_cols` and `_insert_cols`, and the old notebooks `3.1 …` and `4. …`).
9. **`experience`.** Should the old `poi_enrichment_display.experiences` count as a pair for `experience`? The registry maps `experiences` only as a silver enrichment path. Until confirmed, the column is not loaded.
10. **`poi_enrichment_display` grain.** The old table MERGEs on `display_id`. It is not shown whether one (old `poi_id`, `lang`) can have more than one display row. If it can, multi-lang key rule 4 applies.
11. **Partner multi-lang payload diff.** P4 covers only google `source_id` values that have more than one lang. It is not shown whether partner ids also have more than one lang, or whether their compared columns differ.
12. **No-`vi` rule is not yet in the ledger.** `## Giả định còn lại` says ids without `lang = vi` are unresolved (7 single-lang and 234 two-lang google ids). The author input resolves it: `poi_name` and `district` are NULL, and the row is written if the other columns agree. Please record this as part of D-06.
