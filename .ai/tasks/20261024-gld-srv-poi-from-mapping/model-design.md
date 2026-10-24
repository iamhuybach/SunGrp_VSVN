# Model design: 20261024-gld-srv-poi-from-mapping

## Scope

- Base task: `20261024-gld-srv-poi-from-mapping`.
- Proposal sections: Not applicable. The task has no `proposal.md`. The sources are the author input, `docs/context/mapping_gld_srv_poi_multi_lang.md` §1.1 and §1.2, and `docs/context/mapping_gld_srv_poi_info.md` §1.1 through §1.5.
- Ledger rows this design implements (`decision.md` `## Quyết định hiện hành`): D-SRV-02, D-SRV-03, D-SRV-04, D-SRV-05, D-SRV-06 (only the fact that DDL is needed), D-SRV-07, D-SRV-08, D-SRV-09, D-SRV-10, D-SRV-11, D-SRV-12, D-SRV-13, D-SRV-14, D-SRV-15, D-SRV-16, D-SRV-17, D-SRV-18, D-SRV-19, D-SRV-20, D-SRV-21, D-SRV-22, D-SRV-23, D-SRV-24, D-SRV-25, D-SRV-26.
- Write path is A (D-SRV-24). Both gold tables are written by lib `run_node` MERGE. `pl_name` is `PL_VV_TRANS_SLV_TO_GLD_30P` (D-SRV-22; mapping multi_lang §1.1, mapping info §1.1). Neither table is attached to `PL_VV_TRANS_SLV_TO_ENR_15P`. Pipeline activities are out of scope.
- `ctrl_cfg_schema_registry`: Not applicable. There is no proposal section to cite, and no registry row changes in this design.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | gold serving | one row per `(poi_id, lang)` (D-SRV-19; mapping multi_lang §1.1) | `NB_GLD_SRV_POI_MULTI_LANG` (D-SRV-05) |
| `lh_vv_gold.dbo.gld_srv_poi_info` | gold serving | one row per `poi_id` (D-SRV-20; mapping info §1.1) | `NB_GLD_SRV_POI_INFO` (D-SRV-05) |
| `lh_vv_silver.dbo.slv_enr_poi_destination` | silver enrich landing | no declared key. More than one row per `poi_id` can occur (D-SRV-21). Five columns are added; the grain does not change. | None. DDL only, in `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL` (D-SRV-06, D-SRV-11). No notebook in this task populates it (D-SRV-23). |

Read-only inputs with unchanged structure: `slv_poi_entity_non_enrich` (node `NB_SLV_POI_ENTITY_NON_ENRICH`, `pk=("poi_id",)`), `slv_enr_poi_info_multi_lang` (landing, empty per D-SRV-23), and `slv_pn_business_service_i18ns` (registry key `(business_service_id, locale)`).

## Keys

`gld_srv_poi_multi_lang`
- Primary / MERGE key: `(poi_id, lang)`. Both are NOT NULL (D-SRV-19, D-SRV-24).
- Business key: the same pair, copied 1-1 from `slv_enr_poi_info_multi_lang.poi_id` and `.lang` (mapping multi_lang §1.2).
- Foreign / lookup keys:
  - `poi_id` → `slv_poi_entity_non_enrich.poi_id`, used to look up `source_name` (D-SRV-10; mapping multi_lang §1.1).
  - Partner rows only: `(poi_id, lang)` → `slv_pn_business_service_i18ns` on `poi_id = uuid_md5(business_service_id, 'partner')` and `lang = locale` (D-SRV-12; mapping multi_lang §1.1).
- `poi_id` formula source for the i18n side:
  - `NB_SLV_POI_ENTITY_NON_ENRICH` cell 4 builds the partner `poi_id` as `uuid_md5(F.col("id"), F.lit(PARTNER))`, where `PARTNER = "partner"`.
  - `NB_LIB_TRANSFORM_SLV_GLD` defines `uuid_md5(*cols)` as `md5(concat(cols))`, reformatted as 8-4-4-4-12 with `regexp_replace`.
  - The i18n side applies the same function to `business_service_id` and the literal `'partner'`.

`gld_srv_poi_info`
- Primary / MERGE key: `poi_id`, NOT NULL (D-SRV-20, D-SRV-24).
- Business key: `poi_id`, copied 1-1 from `slv_poi_entity_non_enrich.poi_id` (mapping info §1.2). The entity grain is `pk=("poi_id",)` (`NB_SLV_POI_ENTITY_NON_ENRICH` cell 4). Gold does not recompute `poi_id`.
- Foreign / lookup keys:
  - `poi_id` → `slv_enr_poi_destination.poi_id` (LEFT JOIN, mapping info §1.1).
  - Google rows only: `poi_id` must exist in both `slv_enr_poi_destination` and `slv_enr_poi_info_multi_lang` (mapping info §1.1).

`slv_enr_poi_destination`
- Primary key: none declared. `poi_id` is `STRING NOT NULL` (`NB_SETUP_INITIAL_DDL` `init_tables`).
- Rule for reading into gold: when `poi_id` repeats, keep the row with the greater `updated_at` (D-SRV-21; mapping info §1.1). Equal or null `updated_at` stops the run. There is no second sort key.

## Columns

`gld_srv_poi_multi_lang`

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| gld_srv_poi_multi_lang | poi_id | STRING | NOT NULL | `slv_enr_poi_info_multi_lang.poi_id` | Copied 1-1. Part of the MERGE key (mapping multi_lang §1.2; D-SRV-19, D-SRV-24). |
| gld_srv_poi_multi_lang | lang | STRING | NOT NULL | `slv_enr_poi_info_multi_lang.lang` | Copied 1-1. Part of the MERGE key (mapping multi_lang §1.2; D-SRV-19, D-SRV-24). |
| gld_srv_poi_multi_lang | source_name | STRING | yes | `slv_poi_entity_non_enrich.source_name` | Looked up by `poi_id` (mapping multi_lang §1.1, §1.2; D-SRV-10). |
| gld_srv_poi_multi_lang | time_to_spend | STRING | yes | `slv_enr_poi_info_multi_lang.time_to_spend` | Copied 1-1 (mapping multi_lang §1.2). |
| gld_srv_poi_multi_lang | best_time | STRING | yes | `slv_enr_poi_info_multi_lang.best_time` | Copied 1-1 (mapping multi_lang §1.2). |
| gld_srv_poi_multi_lang | cost_vnd | STRING | yes | `slv_enr_poi_info_multi_lang.cost_vnd` | Copied 1-1 (mapping multi_lang §1.2). |
| gld_srv_poi_multi_lang | description | STRING | yes | `slv_pn_business_service_i18ns.bio`, then `slv_enr_poi_info_multi_lang.description` | Partner rows: `bio`; when `bio` is null, use the enr `description`. Other sources: the enr `description` (mapping multi_lang §1.1, §1.2; D-SRV-13). |
| gld_srv_poi_multi_lang | row_hash | STRING | yes | lib | `sha2(to_json(struct(business columns)), 256)` (`02_NAMING_CONVENTION.md` §5.2; `TECH_COLUMNS`; D-SRV-24). |
| gld_srv_poi_multi_lang | created_at | TIMESTAMP | yes | lib | System field (mapping multi_lang §1.2; D-SRV-03; `TECH_COLUMNS`). |
| gld_srv_poi_multi_lang | updated_at | TIMESTAMP | yes | lib | System field. Changes only when `row_hash` changes (§5.2; D-SRV-03; `TECH_COLUMNS`). |
| gld_srv_poi_multi_lang | deleted_at | TIMESTAMP | yes | lib | Set when the key is absent from the build (D-SRV-24; §5.2; `TECH_COLUMNS`). |

`gld_srv_poi_info`

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| gld_srv_poi_info | poi_id | STRING | NOT NULL | `ent.poi_id` | Copied 1-1. MERGE key. Partner rows: all included. Google rows: only when `poi_id` is in both `slv_enr_poi_destination` and `slv_enr_poi_info_multi_lang` (mapping info §1.1, §1.2; D-SRV-20, D-SRV-24). |
| gld_srv_poi_info | poi_name | STRING | yes | `ent.poi_name` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | source_name | STRING | yes | `ent.source_name` | Copied 1-1 (mapping info §1.1, §1.2; D-SRV-10). |
| gld_srv_poi_info | business_sector | STRING | yes | `ent.business_sector` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | business_category | STRING | yes | `ent.business_category` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | subcategory_tags | STRING | yes | `ent.types_json` | Copied 1-1, renamed (mapping info §1.2). |
| gld_srv_poi_info | destination_id | STRING | yes | `des.destination_id` | Copied 1-1. Null while the landing is null (mapping info §1.1, §1.2; D-SRV-11, D-SRV-23). |
| gld_srv_poi_info | full_address | STRING | yes | `des.full_address` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | street | STRING | yes | `des.street` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | ward | STRING | yes | `des.ward` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | district | STRING | yes | `des.district` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | city | STRING | yes | `des.city` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | country_code | STRING | yes | `des.country_code` | Copied 1-1 (mapping info §1.1, §1.2; D-SRV-11). |
| gld_srv_poi_info | postal_code | STRING | yes | `des.postal_code` | Copied 1-1 (mapping info §1.1, §1.2; D-SRV-11). |
| gld_srv_poi_info | lat | DOUBLE | yes | `des.lat` | Copied 1-1 (mapping info §1.1, §1.2; D-SRV-11). |
| gld_srv_poi_info | lng | DOUBLE | yes | `des.lng` | Copied 1-1 (mapping info §1.1, §1.2; D-SRV-11). |
| gld_srv_poi_info | phone | STRING | yes | `ent.phone` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | email | STRING | yes | `ent.email` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | website_url | STRING | yes | `ent.website_url` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | operating_status | STRING | yes | `ent.operating_status` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | is_verified | BOOLEAN | yes | none | Always null (mapping info §1.2; D-SRV-03). |
| gld_srv_poi_info | is_recommended | BOOLEAN | yes | `ent.source_name` | `true` when `source_name = 'partner'`, otherwise `false` (mapping info §1.2; D-SRV-14). |
| gld_srv_poi_info | is_bookable | BOOLEAN | yes | none | Always null (mapping info §1.2; D-SRV-03). |
| gld_srv_poi_info | operating_hours | STRING (JSON array) | yes | `ent.opening_hours_text` | Google: see "Google `operating_hours` rule" below. Partner: see "Partner `operating_hours` rule" below. |
| gld_srv_poi_info | holiday_exceptions | STRING | yes | `ent.holiday_exceptions` | Copied 1-1 (mapping info §1.2). |
| gld_srv_poi_info | row_hash | STRING | yes | lib | `sha2(to_json(struct(business columns)), 256)` (§5.2; `TECH_COLUMNS`; D-SRV-24). |
| gld_srv_poi_info | created_at | TIMESTAMP | yes | lib | System field (mapping info §1.2; D-SRV-03; `TECH_COLUMNS`). |
| gld_srv_poi_info | updated_at | TIMESTAMP | yes | lib | System field. Changes only when `row_hash` changes (§5.2; D-SRV-03). |
| gld_srv_poi_info | deleted_at | TIMESTAMP | yes | lib | Set when `poi_id` is absent from the build (D-SRV-24; §5.2). |

Google `operating_hours` rule (mapping info §1.3 rules 1 through 9 and §1.4; D-SRV-07, D-SRV-15, D-SRV-16, D-SRV-17, D-SRV-25, D-SRV-26):
- Null `opening_hours_text` gives null `operating_hours`.
- The exact form in §1.3 rule 3.1 gives seven all-day objects, as in case 2.
- Otherwise, each source element becomes one object:
  - Source day 0 maps to target day 7. Source days 1–6 keep their numbers.
  - `label` follows the target day.
  - `open_time` comes from `open_hour:open_minute`, `close_time` from `close_hour:close_minute`, both as `HH:MM`.
  - `value` is `open_time - close_time`.
  - `is_open_all_day = false` and `is_closed = false`.
- Several elements with the same `day_of_week` each become one object, in source-array order, with the same `day_of_week` and `label`. They are not merged.
- A day with no element becomes one closed object as in case 1: `value = Đóng cửa`, no `open_time` or `close_time`, `is_closed = true`.
- Days are ordered Monday → Sunday, as in case 1.
- `close_day` is not read.

Partner `operating_hours` rule (mapping info §1.5; D-SRV-18; D-SRV-26 does not apply):
- Null `opening_hours_text` gives null `operating_hours`.
- The output has seven objects, Monday → Sunday, using the key table in §1.5.
- Exactly one `hours` element: `open_time` and `close_time` are the source strings unchanged, `value` is `open_time - close_time`, `is_closed = false`, `is_open_all_day = false`.
- A missing day key, missing `hours`, or empty `hours` gives the case 1 closed object.
- More than one `hours` element on a day stops the run.
- `status` is not read.

`slv_enr_poi_destination` (added columns only)

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| slv_enr_poi_destination | destination_id | STRING | yes | none in this task | Added column (D-SRV-11; mapping info §1.1, §1.2 type). Nullable because the table already exists (`02_NAMING_CONVENTION.md` §2.1 item 5). Not populated (D-SRV-23). |
| slv_enr_poi_destination | country_code | STRING | yes | none in this task | Same as `destination_id` (D-SRV-11; §2.1 item 5; D-SRV-23). |
| slv_enr_poi_destination | postal_code | STRING | yes | none in this task | Same as `destination_id` (D-SRV-11; §2.1 item 5; D-SRV-23). |
| slv_enr_poi_destination | lat | DOUBLE | yes | none in this task | Added column. Type from mapping info §1.2 (D-SRV-11; §2.1 item 5; D-SRV-23). |
| slv_enr_poi_destination | lng | DOUBLE | yes | none in this task | Added column. Type from mapping info §1.2 (D-SRV-11; §2.1 item 5; D-SRV-23). |

## Lineage

`gld_srv_poi_multi_lang`
- Bronze: none.
- Silver:
  - `slv_enr_poi_info_multi_lang` is the driving table for rows and keys (mapping multi_lang §1.1, §1.2).
  - `slv_poi_entity_non_enrich` supplies `source_name` by `poi_id` (D-SRV-10).
  - `slv_pn_business_service_i18ns` is LEFT JOINed for partner rows on `uuid_md5(business_service_id, 'partner') = poi_id` and `locale = lang`, and supplies `bio` (D-SRV-12, D-SRV-13).
  - No `deleted_at` or `deleted` filter is applied to any input.
- Gold: none read.

`gld_srv_poi_info`
- Bronze: none.
- Silver:
  - `slv_poi_entity_non_enrich ent` is the driving table.
  - `slv_enr_poi_destination des` is LEFT JOINed on `poi_id`, after the D-SRV-21 deduplication.
  - `slv_enr_poi_info_multi_lang` is read only to check that a Google `poi_id` exists there (mapping info §1.1).
  - No `deleted_at` filter is applied.
- Gold: none read.

`slv_enr_poi_destination`
- Bronze, silver, gold: none read. DDL change only, and no producer in this task (D-SRV-11, D-SRV-23).

## Conflicts and questions

Not applicable. No `is_active` column (`D-SRV-24`, lib `TECH_COLUMNS`). A null `poi_id` or `lang` stops the run (`D-SRV-27`). A multi_lang row with no entity row is kept, with null `source_name` and the enr `description` (`D-SRV-28`).
