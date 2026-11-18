# Model design: 20261118-amenity-poi-id-align

## Scope

- Base task: `20261118-amenity-poi-id-align`. This design adds partner amenity rows to `lh_vv_silver.dbo.slv_poi_amenity`, keyed by the partner `poi_id`, so that partner POIs on `gld_srv_poi_info` can have amenities. Google rows, the google filter of `NB_GLD_SRV_POI_INFO` cell `srvinfobuild`, the grain, and the gold 1-1 copy stay as they are.
- `proposal.md` is not in the task directory, so this design cannot cite `proposal.md` `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. See Conflicts 1.
- Ledger rows implemented:
  - `decision.md` `### D-2`: partner `poi_id = uuid_md5(id, 'partner')`. The grain stays `(poi_id, business_sector, amenity_group, amenity_raw)`. The info filter is unchanged.
  - `decision.md` `### D-11`: read `amentities` `$.facilities.specialty_tags` from the `locale = 'vi'` row of `slv_pn_business_service_i18ns`. If that value is null, read it from `slv_pn_business_services`. Left join `ref_dictionary_amenities.amenity_raw` with `source_name = 'partner'`. Write unmatched labels too. Do not read any other `facilities` key.
  - `decision.md` `### D-12`, which is also the only row in `## Quyết định hiện hành` (ID `D-1`, `Nguồn (mục)` = `D-12`):
    - `business_sector` comes from `slv_pn_business_services`, joined to `slv_pn_business_service_i18ns` on `business_service_id = id` and `locale = 'vi'`.
    - `amenity_group` comes from the dictionary row on a match. On no match it is `specialty_tags`.
    - If one label matches more than one partner dictionary row, the notebook stops and writes nothing.
- Supporting evidence, cited only:
  - `D-4`: the partner live filter uses `deleted`.
  - `D-6`: the dictionary active filter is `is_active = true`.
  - `D-7`: of 295 partner entities, `business_sector` is null in 101 and an empty string in 11.
  - `D-9`: `specialty_tags` is an array of strings.
- Because `business_sector` changes source for partner rows, the same task must update `docs/context/mapping_gld_srv_poi_amenity.md` §0 (line 1 of that file requires this). Today §0 says `business_sector` comes from `slv_poi_entity_non_enrich`.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_poi_amenity` | silver | One row per (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). Unchanged. It holds the existing google rows plus new partner rows. | `NB_SLV_POI_AMENITY` cell `d1amenbuild` |
| `lh_vv_gold.dbo.gld_srv_poi_amenity` | gold | Same grain. A 1-1 copy of `slv_poi_amenity`. Unchanged. | `NB_GLD_SRV_POI_AMENITY` cell `srvamenitybuild` |

Read-only inputs, not changed: `slv_pn_business_service_i18ns`, `slv_pn_business_services`, `ref_dictionary_amenities`, `slv_poi_entity_non_enrich`, `slv_3p_poi_amenity`.

## Keys

### `slv_poi_amenity`

- **Primary key and MERGE key:** (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`).
  - Sources: `d1amenbuild` `SPEC.pk` and `D-2`. Unchanged.
  - The DDL declares all four columns `STRING NOT NULL` (`docs/context/mapping_gld_srv_poi_amenity.md` §0).
- **Partner `poi_id`:** `uuid_md5(F.col("id"), F.lit("partner"))`, where `id` = `slv_pn_business_service_i18ns.business_service_id` = `slv_pn_business_services.id`.
  - Formula source: `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild`, function `_partner`, line `"poi_id": uuid_md5(F.col("id"), F.lit(PARTNER))  # D2`. In that function, `id` is `business_service_id` aliased from the vi i18n row.
  - Ledger: `D-2`. `D-1` history describes `uuid_md5` in `NB_LIB_TRANSFORM_SLV_GLD` as `md5(concat(...))` in UUID form.
- **Google `poi_id`:** unchanged. It comes from `slv_3p_poi_amenity`, inner joined to `slv_poi_entity_non_enrich.poi_id` (`d1amenbuild`).
- **Business key of a partner row:** (service `id`, `slv_pn_business_services.business_sector`, resolved `amenity_group`, label).
- **Foreign keys:**
  - `poi_id` → `slv_poi_entity_non_enrich.poi_id`. This is a logical reference: partner entity rows use the same formula. It is not enforced. See Conflicts 6.
  - `amenity_raw` → `ref_dictionary_amenities.amenity_raw`, where `source_name = 'partner'`. This is an optional left-join reference (`D-11`). At most one dictionary row may match each label (`D-12`).
  - Partner join: `slv_pn_business_service_i18ns.business_service_id = slv_pn_business_services.id` with `locale = 'vi'` (`D-12`).

### `gld_srv_poi_amenity`

- **Primary key and MERGE key:** same four columns. Source: `srvamenitybuild` `SPEC.pk`. Unchanged.
- `poi_id` is copied from `slv_poi_amenity`. Gold does not hash.

## Columns

Only the partner-path columns of `slv_poi_amenity` are listed. `OUT_COLS` and the DDL are unchanged.

`gld_srv_poi_amenity` copies every column 1-1 (`srvamenitybuild` `select(*OUT_COLS)`), so it gets no new rule. Technical columns (`row_hash`, `created_at`, `updated_at`, `deleted_at`) are written by `sql_merge_target`, as described in mapping doc §1, and are unchanged.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_poi_amenity` | `poi_id` | STRING | NOT NULL | `slv_pn_business_service_i18ns.business_service_id` (vi row) | `uuid_md5(id, 'partner')`. Ledger `D-2`. Formula from `b1entitybuild` `_partner`. |
| `slv_poi_amenity` | `business_sector` | STRING | NOT NULL (DDL) | `slv_pn_business_services.business_sector` | Taken from the service row joined on `business_service_id = id` and `locale = 'vi'` (`D-12`). The matched dictionary row's `business_sector` is not used. No filler for null or blank (`D-12`: the user chose no replacement). See Conflicts 3. |
| `slv_poi_amenity` | `amenity_group` | STRING | NOT NULL | `ref_dictionary_amenities.amenity_group` on a match, otherwise the literal `specialty_tags` | `D-12`. Handoff constraint: on no match, emit `amenity_group = specialty_tags`. |
| `slv_poi_amenity` | `amenity_raw` | STRING | NOT NULL | Each element of `amentities` `$.facilities.specialty_tags` | Read the vi i18n row's value first. If that value is null, read the service row's value (`D-11`). Only `$.facilities.specialty_tags` is read (`D-11`). The array element is the label (`D-9`). See Conflicts 7 and 8. |
| `slv_poi_amenity` | `amenity` | STRING | NULL | `ref_dictionary_amenities.amenity` of the matched partner row | Left join: `amenity_raw` = label and `source_name = 'partner'` (`D-11`). Null on no match (`D-11`). |
| `slv_poi_amenity` | `amenity_en` | STRING | NULL | `ref_dictionary_amenities.amenity_en` of the matched partner row | Same rule as `amenity`. |
| `slv_poi_amenity` | `amenity_vi` | STRING | NULL | `ref_dictionary_amenities.amenity_vi` of the matched partner row | Same rule as `amenity`. |
| `slv_poi_amenity` | `service_flags` | STRING | NULL | `ref_dictionary_amenities.service_flags` of the matched partner row | Same rule as `amenity`. |

## Lineage

### `slv_poi_amenity` (`NB_SLV_POI_AMENITY`)

- **Bronze reads:** none.
- **Silver reads, existing and unchanged:**
  - `slv_3p_poi_amenity`
  - `slv_poi_entity_non_enrich`
  - `ref_dictionary_amenities` google rows with `is_active = true`
- **Silver reads, new:**
  - `slv_pn_business_service_i18ns`: `business_service_id`, `locale`, `amentities`. The live filter is an open question (Conflicts 5).
  - `slv_pn_business_services`: `id`, `amentities`, `business_sector`. The live filter is an open question (Conflicts 5).
  - `ref_dictionary_amenities` rows with `source_name = 'partner'`: `amenity_raw`, `amenity_group`, `amenity`, `amenity_en`, `amenity_vi`, `service_flags`. The active filter is an open question (Conflicts 4).
- **Gold reads:** none.

### `gld_srv_poi_amenity` (`NB_GLD_SRV_POI_AMENITY`)

- **Bronze reads:** none.
- **Silver reads:** `slv_poi_amenity` only. Unchanged.
- **Gold reads:** none. Gold never reads gold.

## Conflicts and questions

Conflicts 3, 4, and 5 of the previous model are closed:

- **Previous 3 (`business_sector` source):** closed by `D-12`. The source is `slv_pn_business_services.business_sector` through the i18n join. Null and blank handling is still open and becomes item 3 below.
- **Previous 4 (`amenity_group` value and join scope):** closed by `D-12` and `D-11`.
  - `amenity_group` is the dictionary row's value on a match and `specialty_tags` on no match.
  - The join columns are `amenity_raw` = label and `source_name = 'partner'` only. There is no narrowing by sector or group.
- **Previous 5 (several dictionary matches):** closed by `D-12`. If a label matches more than one partner dictionary row, the notebook stops and writes nothing. There is no tie-break and no fan-out.
- **Previous 6 (wording vs. the google path):** closed by `D-11` and the handoff constraint. Unmatched partner labels are written with `amenity`, `amenity_en`, `amenity_vi`, and `service_flags` null.
- **Previous 7, null-fallback part:** closed. The fallback works at the `$.facilities.specialty_tags` value level, not on the whole `amentities` block. This differs from `_partner`'s `F.coalesce("_vi_am", "_svc_am")`.

Open items:

1. **Missing proposal.** `proposal.md` does not exist, so its `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` cannot be cited. `slv_poi_amenity` gains two silver inputs, `slv_pn_business_service_i18ns` and `slv_pn_business_services`. They need control-edge rows and `SPEC.inputs` / `required_inputs` entries. Mapping doc §0 lists three active edges today. Who specifies the new edges, and are the two inputs required?
2. **Ledger IDs.** `## Quyết định hiện hành` has one row, ID `D-1`, whose content is `D-12`. `D-2` and `D-11` exist only in `## Lịch sử quyết định`. This design treats `D-2`, `D-11`, and `D-12` as accepted, as the handoff says. Should the current-decision table carry rows `D-2`, `D-11`, and `D-12`?
3. **Null or blank `business_sector`.** `D-7` shows 101 null and 11 empty-string partner `business_sector` values out of 295. `D-12` sets no filler.
   - **Null:** the files block a NULL key only through the DDL, which declares `business_sector` `STRING NOT NULL` (mapping doc §0). The named notebook cells have no explicit NULL check on the MERGE key. If the write path enforces that constraint, any null-sector partner row will fail the whole node, google rows included.
   - **Empty string:** `STRING NOT NULL` does not block `''`. Such rows would be written with `''` as part of the MERGE key.

   Which applies to null and to blank sectors: drop those rows, stop the notebook, or some other rule?
4. **Dictionary active filter and `source_name` comparison.** `D-11` says `source_name = 'partner'` only. Two details are not set:
   - `d1amenbuild` filters google dictionary rows with `lower(trim(source_name))` and `is_active = true`, and `D-6` names `is_active = true` as the active-row test. Should the partner join also require `is_active = true`?
   - Should it use the same `lower(trim(...))` comparison?
5. **Partner live filter and join type.** `D-12` names the join condition but not the join type or which table leads. `_partner` leads from the live vi i18n row (`_live`: `NOT coalesce(deleted, false)`, per `D-4`) and left joins the live service row. Does the amenity path:
   - use the same live filter on both tables?
   - use the same lead table and left join? With a left join, a vi row with no live service row yields a null `business_sector` (see 3).
   - handle services that have no vi i18n row?
6. **Entity membership.** The google path keeps only `poi_id` values present in `slv_poi_entity_non_enrich`. Should partner amenity rows also be limited to `poi_id` values on the entity table, or be written whatever entity membership they have?
7. **Label cleanup and duplicates.** The ledger does not set:
   - whether labels are trimmed or compared case-insensitively. `D-9` found exact and case-insensitive counts equal.
   - whether null or empty array elements are dropped.
   - how repeated labels within one array are deduplicated. Repeats collide on the MERGE key. The google path uses `dropDuplicates`.
8. **Element type.** `D-9` reports `specialty_tags` as an array of strings. The ledger does not say how to handle a non-array value or JSON that does not parse. The google path only counts `unparsed_json` as a metric.
9. **Scope of the multi-match stop.** `D-12` stops when "one label" matches several partner dictionary rows. The google path stops on any duplicate dictionary key, whether or not data uses it. Should the partner stop fire only for labels present in the current source rows, or for any `amenity_raw` duplicated among partner dictionary rows?
