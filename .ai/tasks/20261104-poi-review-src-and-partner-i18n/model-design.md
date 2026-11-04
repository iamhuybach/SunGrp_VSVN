# Model design — 20261104-poi-review-src-and-partner-i18n

## Scope

Base task: `.ai/tasks/20261104-poi-review-src-and-partner-i18n` (status `triage`, `task-state.yaml`).

The task has no `proposal.md`. Its sections `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` therefore cannot be cited (see Conflicts 1). This design implements these sources instead:

- `request.md` `## Scope` / `### In scope` bullets 1–5. These cover the enrich-review ctrl edges, `gld_enr_poi_info` column removal, the `gld_srv_poi_review` source change, `slv_enr_poi_review_multi_lang` no-DROP, and the partner branch of `slv_poi_entity_non_enrich`.
- `request.md` `## Constraints` (partner branch rules, `poi_id` partner) and `### Review text source`.
- Ledger `decision.md` `## Quyết định hiện hành`: **D-SRV-LANG** (drop gold `lang`; PostgreSQL file impact only) and **D-SRV-TEXT** (gold `title` = null; gold `review_text` = `slv_3p_poi_review.text`; no `title` column added to the source).

This design covers model design only. Ctrl `is_active` flips, write modes, quality-gate semantics, rerun/idempotency and rollout belong to the Architect.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_review` | gold (serving) | One row per `review_id` (unchanged; `NodeSpec.pk=("review_id",)`, `NB_GLD_SRV_POI_REVIEW` cell `srvrvbuild`). Driving set changes from `slv_enr_poi_review_multi_lang` ⋈ `slv_3p_poi_review` to `slv_3p_poi_review` only. | `NB_GLD_SRV_POI_REVIEW` |
| `lh_vv_gold.enr.gld_enr_poi_info` | gold (enrich) | One row per `poi_id` (unchanged; `gld_enr_poi_info_review.md` table `gld_enr_poi_info`). Columns removed only. | `NB_ENR_POI_INFO` |
| `lh_vv_gold.enr.gld_enr_poi_review` | gold (enrich) | One row per `review_id` (unchanged). No column change. Its ctrl edges become inactive (request In scope bullet 1). The table is kept, with no DROP and no data delete. | `NB_ENR_POI_REVIEW` (inactive) |
| `lh_vv_silver.dbo.slv_enr_poi_review_multi_lang` | silver (enrich) | Unchanged and not dropped. No in-repo producer (request In scope bullet 4). After this change it loses `gld_srv_poi_review` as a reader. | none in `notebooks/` |
| `lh_vv_silver.dbo.slv_poi_entity_non_enrich` | silver L2 (N6) | One row per `poi_id` (unchanged pk). Partner subset changes from one row per live `slv_pn_business_services` row that has a live `vi` i18n row to one row per live `slv_pn_business_service_i18ns` row with `locale = 'vi'` (request `## Constraints`). Google subset unchanged. | `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild`, def `_partner` |
| `lh_vv_silver.dbo.slv_3p_poi_review` | silver L1 (3p extract) | One row per `review_id` (registry `"key": "review_id"`, `NB_CREATE_DDL` `TABLE_CONFIGS_3P`). No change: no `title` column is added (D-SRV-TEXT). | registry-driven extract |

## Keys

**`gld_srv_poi_review`**
- Primary key: `review_id` (`NodeSpec.pk`).
- Business key: `review_id` = `slv_3p_poi_review.review_id`. Formula is `HASH_SHA256` over `_doc.source_name,_doc.source_id,authorAttribution.displayName,publishTime` (registry `TABLE_CONFIGS_3P`; `01_DATA_MODEL.md` §8 `review_id`).
- `poi_id`: now taken from `slv_3p_poi_review.poi_id`. Formula is the 3rd-party `poi_id`, `uuid_format(md5(source_name ‖ source_id))` / `HASH_MD5_UUID` (`01_DATA_MODEL.md` §8). Before this change it came from `slv_enr_poi_review_multi_lang.poi_id`. See Conflicts 9.
- Foreign keys (logical): `review_id` → `slv_3p_poi_review.review_id`; `poi_id` → `slv_3p_poi_rating.poi_id` (left join, unchanged; request In scope bullet 3).

**`gld_enr_poi_info`**
- Primary key `poi_id`, unchanged. Logical FK `poi_id` → `slv_poi_entity_non_enrich.poi_id` (spine), unchanged.

**`gld_enr_poi_review`**: unchanged (`review_id`).

**`slv_enr_poi_review_multi_lang`**: unchanged and not modelled further. No producer to cite.

**`slv_poi_entity_non_enrich`, partner rows**
- Primary key: `poi_id` (`NodeSpec.pk`).
- `poi_id` partner = `uuid_md5(i18n.business_service_id, lit('partner'))`, which is `uuid_format(md5(concat(<id>, 'partner')))` in 8-4-4-4-12 form. Source: `request.md` `## Constraints` and `01_DATA_MODEL.md` §8 row `poi_id` partner. §8 states that `business_service_id` of `slv_pn_business_service_i18ns` and `id` of `slv_pn_business_services` are the same value and give the same `poi_id`. `NB_ENR_POI_INFO` `_vi_i18n` already uses this argument order.
- Business key: `slv_pn_business_service_i18ns.business_service_id` (driving), filtered to live rows and `locale = 'vi'`.
- Foreign key (logical): `i18n.business_service_id` → `slv_pn_business_services.id`, left join on live service rows (request `## Constraints`).
- `source_id`: MISSING in the request (Conflicts 5).
- The current `unique_checks` `partner_source_id_unique` on `source_id` and pk `poi_id` both need at most one live `vi` i18n row per `business_service_id`. The request does not state this (Conflicts 6).

**`slv_3p_poi_review`**: key `review_id`, unchanged.

## Columns

Only affected columns are listed.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `gld_srv_poi_review` | `lang` | — | — | removed | D-SRV-LANG; request In scope bullet 3 "drop `lang`". Removed from `OUT_COLS` and from the DDL. |
| `gld_srv_poi_review` | `review_id` | string (mapping doc) | NOT NULL (pk) | `slv_3p_poi_review.review_id` | request In scope bullet 3 "Read review rows from `slv_3p_poi_review`". Before: `slv_enr_poi_review_multi_lang.review_id`. |
| `gld_srv_poi_review` | `poi_id` | string (mapping doc) | not stated | `slv_3p_poi_review.poi_id` | request In scope bullet 3. Before: `slv_enr_poi_review_multi_lang.poi_id` (Conflicts 9). |
| `gld_srv_poi_review` | `title` | string (mapping doc; Conflicts 3) | NULL always | none; literal null | D-SRV-TEXT "slv_3p_poi_review.title gán là null"; request `### Review text source` "Gold `title` is null". Not mapped onto any source column (request Out of scope). |
| `gld_srv_poi_review` | `review_text` | string (mapping doc) | nullable as source | `slv_3p_poi_review.text` | D-SRV-TEXT "gld_srv_poi_review.review_text lấy từ slv_3p_poi_review.text". Registry `text` = `_str("text.text")`. |
| `gld_srv_poi_review` | `rating_overall` | decimal(4,2) | nullable (left join) | `slv_3p_poi_rating.rating_overall` | Unchanged; request In scope bullet 3 "Keep the `slv_3p_poi_rating` join". |
| `gld_srv_poi_review` | `rating_count` | bigint (`SOURCE_TYPES`); mapping doc says integer | nullable (left join) | `slv_3p_poi_rating.rating_count` | Unchanged; same bullet. |
| `gld_srv_poi_review` | `rating`, `review_date`, `author_name` | as today | as today | `slv_3p_poi_review.rating`, `.time`, `.author_name` | Unchanged mapping (`mapping_gld_srv_poi_review.md` §2). |
| `gld_enr_poi_info` | `time_to_spend` | — | — | removed | request In scope bullet 2. Builder `_time_to_spend_text` removed (`NB_ENR_POI_INFO` cell `36415d3b`). |
| `gld_enr_poi_info` | `best_time` | — | — | removed | request In scope bullet 2. Builder `_best_time_text` removed. |
| `gld_enr_poi_info` | `cost_vnd` | — | — | removed | request In scope bullet 2. Builder `_cost_vnd` removed. |
| `gld_enr_poi_info` | `cost` | BIGINT | nullable | `_cost(slv_3p_poi_price.price_min, price_max)` | Kept unchanged; request In scope bullet 2 "Keep `cost`". |
| `slv_poi_entity_non_enrich` (partner) | `poi_id` | string (schema of google branch) | NOT NULL (pk) | `slv_pn_business_service_i18ns.business_service_id` | request `## Constraints` last paragraph; `01_DATA_MODEL.md` §8. |
| `slv_poi_entity_non_enrich` (partner) | `source_id` | string | MISSING | MISSING | Not in the request (Conflicts 5). |
| `slv_poi_entity_non_enrich` (partner) | `poi_name` | string | nullable | `coalesce(i18n.name, svc.name)` | request `## Constraints` "`name = coalesce(i18n.name, svc.name)`". |
| `slv_poi_entity_non_enrich` (partner) | `poi_name_normalized` | string | nullable | `lower(<name>)` | Current rule `F.lower(F.col("name"))`. It follows the coalesced `name` (Conflicts 10). |
| `slv_poi_entity_non_enrich` (partner) | `primary_type` | string | nullable | `first_child_value(coalesce(i18n.amentities, svc.amentities), "main_category")` | request `## Constraints` "`amentities = coalesce(...)`… `main_category`… read from that block, including when an inner key is absent". Before: from `svc.amentities`. |
| `slv_poi_entity_non_enrich` (partner) | `opening_hours_text` | string | nullable | `$.policies.operating_hours` of the coalesced `amentities` | Same constraint. Before: from `i18n.amentities` only. Today's json_path is kept; there is no per-key fallback. |
| `slv_poi_entity_non_enrich` (partner) | `holiday_exceptions` | string | nullable | `$.policies.holiday_exceptions` of the coalesced `amentities` | Same constraint. Before: from `i18n.amentities` only. |
| `slv_poi_entity_non_enrich` (partner) | `phone`, `email`, `business_sector`, `operating_status` (from `operation_status`), `house_number`/`street`/`ward`/`city`/`full_address` (from `address` via `PARTNER_ADDRESS`), `website_url` (from `website_urls`) | as today | nullable; NULL when no live service row joins | `slv_pn_business_services` only | request `## Constraints` "exist only on `slv_pn_business_services`. They are NULL when the live service row does not join". Before: always present (inner join). |
| `slv_poi_entity_non_enrich` (partner) | `business_category`, `business_category_vi` | string | nullable | when `primary_type` is null: `svc.business_sector`; else partner dictionary row | Lookup steps unchanged (request `## Constraints` dictionary bullet). The `primary_type`-null branch now yields NULL when no service row joins, because `business_sector` is service-only. |
| `slv_poi_entity_non_enrich` (partner) | `category_group`, `range_low_min`, `range_high_min`, `avg_range_min`, `candidate_best_time_code`, `canonical_candidate` | as today | as today | `ref_dictionary_place_type` via `primary_type` | Unchanged lookups (request `## Constraints` dictionary bullet). |
| `slv_poi_entity_non_enrich` (partner) | `language_code` | string | — | literal `vi` | Unchanged. |
| `slv_3p_poi_review` | `title` | — | — | not added | D-SRV-TEXT; request `### Review text source` "Do not add a `title` column". |

## Lineage

**`gld_srv_poi_review`**
- Bronze: none read directly.
- Silver: `slv_3p_poi_review` (driving; `review_id`, `poi_id`, `rating`, `text`, `time`, `author_name`), left join `slv_3p_poi_rating` on `poi_id`. `slv_3p_poi_review` is extracted by the registry from bronze `brz_3rd_crawler_poi_stream`.
- No longer read: `slv_enr_poi_review_multi_lang`.
- Gold: none. Gold does not read gold.

**`gld_enr_poi_info`**
- Silver: unchanged input set (`slv_poi_entity_non_enrich` spine, `slv_poi_amenity`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_review`, `slv_pn_business_service_i18ns`, `slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination`). The three removed columns used only `e.avg_range_min`, `e.canonical_candidate`, `e.business_sector` and `cost`. Those inputs remain for other columns.
- Gold: none.

**`gld_enr_poi_review`**: inputs unchanged (`slv_3p_poi_review`, `slv_enr_poi_review_multi_lang` for the flag). Its edges become inactive, so no new lineage.

**`slv_enr_poi_review_multi_lang`**: no in-repo producer. Readers after the change: only `NB_ENR_POI_REVIEW`, which is inactive.

**`slv_poi_entity_non_enrich`, partner branch**
- Silver: `slv_pn_business_service_i18ns` (driving; live, `locale = 'vi'`), left join live `slv_pn_business_services` on `i18n.business_service_id = svc.id`, then `ref_dictionary_place_type` (partner and google lookups, unchanged). Does not read `slv_3p_poi`, address, contact or opening hours (request In scope bullet 5).
- Bronze: none directly. `slv_pn_*` come from partner CDC extract.
- Gold: none.

## Conflicts and questions

1. **No `proposal.md`.** The handoff asks to cite `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry`, but the task directory has no `proposal.md`. This design cites `request.md` and ledger rows D-SRV-LANG / D-SRV-TEXT instead. Does a proposal need to be written before Architect, or is `request.md` the accepted scope?
2. **Registry impact.** `slv_3p_poi_review` registry columns stay `review_id`, `poi_id`, `author_name`, `rating`, `text`, `time`, `published_at`, with no `title`. No `ctrl_cfg_schema_registry` row changes are designed here. Please confirm that no registry row changes for this task.
3. **Gold column types for `gld_srv_poi_review`.** The gold DDL was not in the read set. Types above come from `mapping_gld_srv_poi_review.md` and `SOURCE_TYPES`. The mapping doc lists `rating` as `string` and `rating_count` as `integer`. The notebook requires `decimal(4,2)` and `bigint` on the source. Which types does the gold DDL hold? Which type should the null `title` be cast to (mapping says `string`)?
4. **Physical removal of columns on existing Delta tables.** `gld_srv_poi_review.lang` and `gld_enr_poi_info.time_to_spend` / `best_time` / `cost_vnd` must leave "DDL, select, and mapping". The request also forbids DROP and data delete. It does not say whether the existing Delta tables get `ALTER TABLE … DROP COLUMN` or keep the physical columns and stop writing them. User or Architect decision required.
5. **Partner `source_id` is MISSING.** Today `source_id = svc.id`. The request names only the `poi_id` input (`business_service_id`). Should `source_id` be `i18n.business_service_id`? Not set here.
6. **Partner grain uniqueness.** The request does not say whether at most one live `locale = 'vi'` row exists per `business_service_id`. Pk `poi_id` and `partner_source_id_unique` depend on it. The rule for duplicates is unknown: fail, pick one, or something else. Not set here.
7. **`slv_pn_business_service_i18ns.name`.** The request uses `i18n.name`. No file in the read set shows that column or its type; only `amentities`, `business_service_id`, `locale` and `deleted` are shown. Please confirm that it exists.
8. **Old node-stop rule.** The rule "no remaining row means the whole node stops and does not write" (`_partner`: `if live and not agg["rows"]`) is not carried over, per the user comment and request `## Constraints`. Whether idempotency needs it is an Architect question. If it does, record `USER_DECISION` and stop. This design does not keep it.
9. **`gld_srv_poi_review.poi_id` source.** The request says reviews are read from `slv_3p_poi_review` but does not name the `poi_id` source column explicitly. `slv_3p_poi_review.poi_id` is the only remaining candidate. The current `review_poi_id_mismatch` warning compares the two `poi_id`s and has no meaning after the change. Please confirm `poi_id` = `slv_3p_poi_review.poi_id`.
10. **Partner `poi_name_normalized`.** It is not named in the request. The design assumes it follows the coalesced `name` through the current `lower(name)`. Please confirm.
11. **Checks that reference removed columns in `NB_ENR_POI_INFO`.** `block_checks` `json_text_null` (also covers `service_flag`) and `cost_vnd_mismatch` reference removed columns. `warn_checks` `time_to_spend_unfixed` is named after a removed column but tests `avg_range_min`. The request does not say which to keep, rewrite or drop. `SECTOR_LABELS`, `SECTOR_OTHER`, `BEST_TIME_RE` and `_label` serve only the three removed columns.
12. **Ctrl edges for `gld_srv_poi_review`.** The request does not say whether a ctrl edge `slv_enr_poi_review_multi_lang` → `gld_srv_poi_review` exists or should be inactivated. It also does not say whether the edge from `slv_3p_poi_review` is sufficient as the driving edge. This is outside model scope and goes to the Architect.
13. **Docs that contradict the new model.** `mapping_gld_srv_poi_review.md` §1 still says to add `lang` and `title` to `slv_enr_poi_review_multi_lang` and to inner join it. `01_DATA_MODEL.md` N6 row describes the inner join from `slv_pn_business_services` and hours/holidays from i18n `vi` only. §8 lists `NB_SLV_POI_ENTITY_NON_ENRICH` as calling `uuid_md5` with `id`. Implementation updates all three (request In scope bullet 6).
14. **PostgreSQL impact only.** `sql/postgres/gld_srv_serve.pg.sql` `apps.srv_poi_review` already has no `lang`. D-SRV-LANG supersedes ledger `20261029-pg-ddl-gld-srv-serve` D-LANG on the gold side. The PostgreSQL file is not edited in this task.
