# Model design — 20261020-entity-drop-op-cols-add-website

## Scope

- Base task: `20261020-entity-drop-op-cols-add-website` (`task-state.yaml` status `waiting_architecture`).
- The task has no `proposal.md`, so `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` cannot be cited. D6 says this design follows the ledger directly.
- Ledger rows implemented: D1 (drop the four op columns from the entity only), D2 (`website_url`), D9 (the five estimate columns on the entity) and D10 (`service_flags` on the amenity table).
- D7 and D8 are carried unchanged as the join and JSON rules for `website_url`. D3 is carried as the contact grain.
- Out of scope: drop and watermark deletion (D4, D5); reseeding `ref_dictionary_place_type` or `ref_dictionary_amenities` (D9, D10); the partner `poi_id` formula (D6); and the architecture concerns listed in the handoff.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_poi_entity_non_enrich` | silver | one row per `poi_id`. Google rows come from `slv_3p_poi`; partner rows come from live `slv_pn_business_services` rows that have a live `vi` i18n row. | `NB_SLV_POI_ENTITY_NON_ENRICH` (cell `b1entitybuild`) |
| `lh_vv_silver.dbo.slv_poi_amenity` | silver | one row per (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) | `NB_SLV_POI_AMENITY` (cell `d1amenbuild`) |
| `lh_vv_silver.dbo.slv_3p_poi_contact` (read only, new input of the entity) | silver | one row per `poi_id` (D3) | not changed |
| `lh_vv_silver.dbo.ref_dictionary_place_type` (read only) | silver | one active row per (`source_name`, `place_type`). The `_google` and `_partner` duplicate checks enforce this for google and partner. | not changed; DDL is in `NB_SETUP_POI_ENTITY` cell `a1setupddl` |
| `lh_vv_silver.dbo.ref_dictionary_amenities` (read only) | silver | one active google row per (`business_sector`, `amenity_group`, `amenity_raw`), enforced by the `dup` check in `d1amenbuild` | not changed; DDL is in `NB_SETUP_POI_AMENITY` cell `c1setupddl` |

## Keys

**`slv_poi_entity_non_enrich`**
- Primary key: `poi_id` (`SPEC.pk`).
- Business keys: (`source_name`, `source_id`). `unique_checks` `partner_source_id_unique` requires `source_id` to be unique where `source_name = 'partner'`.
- `poi_id` formula:
  - Google rows pass through `slv_3p_poi.poi_id`. That value is `uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`, `AGENTS.md` §7).
  - Partner rows use `uuid_md5(F.col("id"), F.lit(PARTNER))` in `_partner`. D6 keeps this formula unchanged.
- Foreign keys (logical):
  - `poi_id` → `slv_3p_poi_contact.poi_id`, google rows only, left join (D7).
  - (`source_name`, `primary_type`) → `ref_dictionary_place_type` (`source_name`, `place_type`). For google rows this is the existing `_p` / `_m` match. For partner rows it is the existing `dp` match. See Conflicts 1.

**`slv_poi_amenity`**
- Primary key: (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) (`SPEC.pk`). `service_flags` is not part of the key.
- Foreign keys (logical):
  - `poi_id` → `slv_poi_entity_non_enrich.poi_id`.
  - (`business_sector`, `amenity_group`, `amenity_raw`) → the google active row of `ref_dictionary_amenities` that already matched.

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_poi_entity_non_enrich` | `_crawled_at` | removed | — | was `slv_3p_poi` through `POI_COLS` | D1: remove from `POI_COLS`, the entity output and the entity DDL. Keep it on `slv_3p_*`. |
| `slv_poi_entity_non_enrich` | `_event_id` | removed | — | was `slv_3p_poi` through `POI_COLS` | D1 |
| `slv_poi_entity_non_enrich` | `_first_seen_at` | removed | — | was `slv_3p_poi` through `POI_COLS` | D1 |
| `slv_poi_entity_non_enrich` | `_last_seen_at` | removed | — | was `slv_3p_poi` through `POI_COLS` | D1 |
| `slv_poi_entity_non_enrich` | `website_url` | STRING | yes | google: `slv_3p_poi_contact.website_url`; partner: `slv_pn_business_services.website_urls` | D2, D7, D8. Google: left join on `poi_id`; no contact row gives null; a duplicate `poi_id` fails the run. Partner: `get_json_object(website_urls, '$.website_url')`, top-level key only, with the null cases listed in D8. The column goes right after `primary_type` (D8). |
| `slv_poi_entity_non_enrich` | `range_low_min` | INT | yes | `ref_dictionary_place_type.range_low_min` | D9: taken from the dictionary row the entity already matched. No second match rule. |
| `slv_poi_entity_non_enrich` | `range_high_min` | INT | yes | `ref_dictionary_place_type.range_high_min` | D9 |
| `slv_poi_entity_non_enrich` | `avg_range_min` | INT | yes | `ref_dictionary_place_type.avg_range_min` | D9 |
| `slv_poi_entity_non_enrich` | `candidate_best_time_code` | STRING | yes | `ref_dictionary_place_type.candidate_best_time_code` | D9 |
| `slv_poi_entity_non_enrich` | `canonical_candidate` | STRING | yes | `ref_dictionary_place_type.canonical_candidate` | D9 |
| `slv_poi_amenity` | `service_flags` | STRING | yes | `ref_dictionary_amenities.service_flags` | D10: taken from the dictionary row the amenity already matched. No second match rule. |

Type sources:
- The five estimate columns come from `NB_SETUP_POI_ENTITY` cell `a1setupddl`: `INT` / `int` nullable for the three range columns, `STRING` / `string` nullable for the other two.
- `service_flags` comes from `NB_SETUP_POI_AMENITY` cell `c1setupddl`: `STRING` / `string` nullable.
- `website_url` comes from D2.

How the existing match carries the new columns (no new match):
- **Entity, google rows.** `_google` builds `_cat = F.struct(*CATEGORY_COLS)` from active google dictionary rows. `pick(c, default)` takes `_p` (match on `primary_type`), then `_m` (lowest `types_json` position), then the default.
  - The five estimate columns are added to the struct that `_p` / `_m` carry, so each one comes from the same chosen row.
  - They are not added to `CATEGORY_COLS` if that would change the existing duplicate check or defaults.
  - When neither `_p` nor `_m` matches, the value is null. See Conflicts 2.
- **Entity, partner rows.** The value source is still open (Conflicts 1). Until it is decided, the existing `cols.get(c, F.lit(None))` fallback in `_partner` would write null.
- **Amenity.** The `d1amenbuild` dictionary collect, `COND_SCHEMA` and `match_conditions` row tuples gain `service_flags`. `out_one` / `out_in` already join exactly one condition row per (`business_sector`, `amenity_group`, `amenity_raw`), because the `dup` check fails on duplicates. `OUT_COLS` gains `service_flags`.

## Lineage

**`slv_poi_entity_non_enrich`**
- Bronze: none read directly.
- Silver:
  - `slv_3p_poi`
  - `slv_3p_poi_address`
  - `slv_3p_poi_contact` (new required input, D7)
  - `ref_dictionary_place_type`
  - `slv_pn_business_services`, which also supplies `website_urls` (D2)
  - `slv_pn_business_service_i18ns`
- Gold: none.

**`slv_poi_amenity`**
- Bronze: none read directly.
- Silver:
  - `slv_3p_poi_amenity`
  - `slv_poi_entity_non_enrich`, which still supplies only `poi_id`, `business_sector`, `source_name` and `types_json`. D1 does not affect these columns.
  - `ref_dictionary_amenities`, which now also supplies `service_flags`.
- Gold: none.

No gold table is read or written, so the gold-reads-gold rule is not touched.

## Conflicts and questions

1. **Which dictionary row supplies the estimates for partner rows?** Google and partner rows already select different dictionary rows:
   - Google rows use one active google row (`source_name = google`) chosen by `pick` from `_p` / `_m`.
   - Partner rows use the active partner row `dp` (`source_name = partner`, `place_type = primary_type`, exact match) only for `business_category` / `business_category_vi` (`_pc`).
   - Partner `business_sector` comes from `slv_pn_business_services`.
   - Partner `category_group` comes from aggregates over several rows: `s1` across all sources, and `s2` over google rows grouped by `business_category`. Neither is a single row.

   D9 says "the row the entity already matched", but for partner rows that is not one obvious row. Options: (a) the `dp` partner row through `_pc`; (b) null for partner rows; (c) something else. Per the handoff, this design does not choose. `USER_DECISION` is required.
2. **Value when there is no match.** Possible cases:
   - a google row where both `_p` and `_m` are null;
   - a partner row with a null `primary_type` or no `dp` row, if option (a) is chosen.

   D9 says nothing about these cases. The existing defaults (`other` / `Other`) belong to the category columns only. The proposal is null for all five estimate columns, with no default value. Please confirm.
3. **Column positions.** D8 places `website_url` after `primary_type`. No ledger row gives positions for the five estimate columns in the entity, or for `service_flags` in `slv_poi_amenity`. The proposal is:
   - the five estimate columns go after `category_group`, in the order of the `a1setupddl` dictionary DDL;
   - `service_flags` goes after `amenity_vi`.

   Please confirm.
4. **Target DDL sources not read in this run.**
   - The entity target DDL is in `NB_SETUP_INITIAL_DDL` `TABLE_SPECS`, according to the `decision.md` history. It is outside this run's read list, so this design does not check the current entity column types there.
   - The `slv_poi_amenity` DDL in `NB_SETUP_POI_AMENITY` cell `c1setupddl` currently has no `service_flags`. It and the `EXPECTED` schema need the column.

   Per `AGENTS.md` §7 / `02_NAMING_CONVENTION.md` §2.1, both `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL` must change. This design does not specify how.
