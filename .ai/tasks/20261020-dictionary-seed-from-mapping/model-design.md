# Model design: 20261020-dictionary-seed-from-mapping

## Scope

- Base task: `20261020-dictionary-seed-from-mapping` (`task-state.yaml` signal `data_model_change`, `architecture_required: true`).
- There is no `proposal.md`. Per the author input, the accepted scope is `decision.md` `## Quyết định hiện hành` rows D-01 to D-05 together with `request.md` `## Constraints`. Because there is no proposal, nothing here cites `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`.
- Implemented ledger rows:
  - D-01: which seed changes are in scope and which are excluded (the 1.7 tokens, the two partner enums with no Google type, and the 1.5 labels that stay).
  - D-02: Homestay gets `Lodging`.
  - D-03: a partner row takes the single non-`Other` `category_group` from its own mapping row. Section 1.8 is filled from the existing `CATEGORY_GROUPS`.
  - D-04: sections 1.9.1 and 1.9.2 become seed values on `ref_dictionary_place_type`. Matching is exact, new rows use `google` with `other` / `Other`, the column labels are the markdown headers, and section 1.9.3 is excluded.
  - D-05: section 2.5 tokens become rows of `ref_dictionary_amenities`.
- Constraints from `request.md`:
  - Values are hard-coded in `SEED_ROWS`, and no function derives `category_group`.
  - Columns are declared in the `NB_SETUP_POI_*` DDL and also in `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL`.
  - Formula 1.9.3 is not a seed row.
  - No flag names are invented.
- Current table shape: `docs/context/01_DATA_MODEL.md` L343–L344.
- Out of scope here: invariants, write/commit boundaries, idempotency, rebuild ordering, and the runbook. Those belong to the Architect and the runbook.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.ref_dictionary_place_type` | silver (shared reference dictionary) | One row per (`source_name`, `place_type`) (`01_DATA_MODEL.md` L343). The grain stays the same, but new `google` rows are added for the D-04 tokens that do not exist yet. | `NB_SETUP_POI_ENTITY` (owns DDL + `BEGIN_PLACE_TYPE_SEED`), mirrored in `NB_SETUP_INITIAL_DDL`, patched in `NB_CREATE_DDL` (`02_NAMING_CONVENTION.md` L53–L64) |
| `lh_vv_silver.dbo.ref_dictionary_amenities` | silver (shared reference dictionary) | One row per (`source_name`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`) (`01_DATA_MODEL.md` L344). The grain stays the same, and 17 new `google` rows are added (D-05). | `NB_SETUP_POI_AMENITY` (owns DDL + `BEGIN_AMENITY_SEED`), mirrored in `NB_SETUP_INITIAL_DDL`, patched in `NB_CREATE_DDL` |

## Keys

`ref_dictionary_place_type`
- Primary / business key: (`source_name`, `place_type`). This is unchanged (`01_DATA_MODEL.md` L343).
- New key values: `source_name = 'google'` and `place_type` = the D-04 token after one rewrite (Latin phrases with spaces become `_`, e.g. `night market` → `night_market`). `suối` and `thác` are kept exactly as written (D-04).
- Foreign keys: none declared. `category_group` refers to the section 1.8 group set (the `CATEGORY_GROUPS` labels, D-03). `candidate_best_time_code` refers to the code list in `mapping_place_type.md` L234–L242. Neither is a declared FK.

`ref_dictionary_amenities`
- Primary / business key: (`source_name`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`). This is unchanged (`01_DATA_MODEL.md` L344).
- New key values for the 17 D-05 tokens: (`google`, `other`, `other`, `<token>`, `<token>`).
- Foreign keys: none.

`poi_id`
- Neither table carries `poi_id`. For reference, the formulas are in `AGENTS.md` §7: third party `uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`) and partner `uuid_format(md5('partner_portal' || business_service_id))`. This design does not use them.

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `ref_dictionary_place_type` | `source_name` | existing (unchanged) | no (key) | `SEED_ROWS` | New rows use `google` (D-04). |
| `ref_dictionary_place_type` | `place_type` | existing (unchanged) | no (key) | `SEED_ROWS` | Exact match against existing `place_type`. A missing token becomes a new row. Spaces become `_` once. The exclusions `temple`↛`hindu_temple`/`buddhist_temple`, `boat`↛`boat_rental`, `hiking`↛`hiking_area`, `wellness`↛`wellness_center`, `shopping`/`mall`↛`shopping_mall` apply. `suối`/`thác` are kept as written (D-04; `mapping_place_type.md` L203, L216). |
| `ref_dictionary_place_type` | `business_sector` | existing (unchanged) | existing | `SEED_ROWS` | New D-04 rows get `other` (D-04; L203, L216). |
| `ref_dictionary_place_type` | `business_category` | existing (unchanged) | existing | `SEED_ROWS` | New D-04 rows get `other` (D-04). |
| `ref_dictionary_place_type` | `business_category_vi` | existing (unchanged) | existing | `SEED_ROWS` | New D-04 rows get `other` (D-04). |
| `ref_dictionary_place_type` | `category_group` | existing (unchanged) | existing | `SEED_ROWS` (hard-coded per row) | Google rows use section 1.8 (filled from `CATEGORY_GROUPS`), and a token not in 1.8 gets `Other` (request Constraints; D-03). A partner row gets the single non-`Other` group from the same mapping row (D-03). Homestay gets `Lodging` (D-02). New D-04 rows get `Other`. No code function assigns it (request Constraints). |
| `ref_dictionary_place_type` | `default_range(min)` | Q-2 | yes (column added to an existing table, `02_NAMING_CONVENTION.md` L61) | `SEED_ROWS` | Per `category_group` from `mapping_place_type.md` L193–L201. Exact-token special cases come from L205–L210 (D-04). Precedence and coverage: Q-4. |
| `ref_dictionary_place_type` | `avg_range(min)` | Q-2 | yes | `SEED_ROWS` | Same source and rule as `default_range(min)` (L193–L210; D-04). |
| `ref_dictionary_place_type` | `candidate_best_time_code` | Q-2 | yes | `SEED_ROWS` | Per exact `place_type`, taken from `mapping_place_type.md` L218–L231. The condition text is split into one row per `place_type` (D-04; L216). Priority 10 (`OUTDOOR_TYPES`) is not assigned, so no `dry_season` (D-04). Priority resolution and the default `all`: Q-5. |
| `ref_dictionary_place_type` | `canonical_candidate` | Q-2 | yes | `SEED_ROWS` | Looked up from `candidate_best_time_code` via `mapping_place_type.md` L234–L242 (D-04). |
| `ref_dictionary_amenities` | `source_name` | existing (unchanged) | no (key) | `SEED_ROWS` | New rows use `google` (D-05). |
| `ref_dictionary_amenities` | `business_sector` | existing (unchanged) | no (key) | `SEED_ROWS` | New rows use `other` (D-05; `mapping_amenities.md` L144). |
| `ref_dictionary_amenities` | `amenity_group` | existing (unchanged) | no (key) | `SEED_ROWS` | New rows use `other` (D-05; L144). |
| `ref_dictionary_amenities` | `amenity_raw` | existing (unchanged) | no (key) | `SEED_ROWS` | The 17 new tokens listed in D-05. Existing rows for the D-05 "already present" tokens, the 8 `parkingOptions.*` tokens and the derived amenities stay as they are, and no new `amenity_raw` is created for them (D-05). The three short wheelchair names map to the existing prefixed rows: Q-7. |
| `ref_dictionary_amenities` | `amenity` | existing (unchanged) | no (key) | `SEED_ROWS` | New rows: `amenity` = `amenity_raw` (D-05; L144). |
| `ref_dictionary_amenities` | `amenity_vi` | existing (unchanged) | existing | `SEED_ROWS` | New rows: `amenity_vi` = `amenity_raw` (D-05; L144). |
| `ref_dictionary_amenities` | `is_active` | existing (unchanged) | existing | `SEED_ROWS` | The value for new rows is not stated: Q-8. |

`ref_dictionary_amenities` gets no new column. D-05 adds rows only.

Section 1.9.3 (`deterministic_cost_vnd`, `cost_method`, `cost_confidence`) is not a seed column (request Constraints; D-04). The 1.9.2 `priority` header is not listed as a column in D-04, so it is not modelled.

## Lineage

- Bronze: none. Neither table reads bronze.
- Silver: none. Both tables are seeded from repository definitions (`SEED_ROWS` in `NB_SETUP_POI_ENTITY` / `NB_SETUP_POI_AMENITY`, mirrored in `NB_SETUP_INITIAL_DDL`), not via `INSERT … SELECT` from a running Fabric table (`02_NAMING_CONVENTION.md` L62, L64). The human source document is `mapping_place_type.md` §1.8, §1.9.1 and §1.9.2 for place types, and `mapping_amenities.md` §2.5 for amenities.
- Gold: none. Neither table reads gold. This design does not change any downstream reader, and the files read here do not list them.

## Conflicts and questions

1. **Request Constraints vs D-04 on new place types.** `request.md` Constraints says that for "Có snorkel", "Có island" and conditions that name no `place_type` token, you record `USER_DECISION` and create no new `place_type`. D-04, which is later and sits in the ledger, says a token that is missing is added as a new `google` row with `other` / `Other`, and it explicitly adds `night_market` and keeps `suối` / `thác`. This design follows D-04. Please confirm that D-04 supersedes this Constraint line and the out-of-scope item "Tạo `place_type` mới cho cụm không nêu token".
2. **Column types are not shown.** No file gives types for `default_range(min)`, `avg_range(min)`, `candidate_best_time_code` or `canonical_candidate`. `default_range(min)` is written as a range ("min–max", with thousands separators), and `avg_range(min)` as a single number. Should `default_range(min)` be stored as one string or as two numeric bounds, what type should `avg_range(min)` have, and should the separators be stripped?
3. **Column names contain parentheses.** D-04 fixes the names as the headers `default_range(min)` and `avg_range(min)`. Delta tables reject `(` and `)` in column names unless column mapping is enabled. Should we keep the exact header names (which needs the table property) or use a different physical name? This design does not choose either.
4. **Coverage and precedence for 1.9.1.** Should every row get its `category_group` default from L193–L201, including partner rows and the new D-04 rows (which are `Other`)? Should a special-case value from L205–L210 override the group default on the matched `place_type`? Tokens such as `museum` and `boat` appear in L205–L210 and could already carry a different group.
5. **Priority and default for 1.9.2.** If one `place_type` matches several rules, is the lowest `priority` taken? Do rows that match no rule store `all` (L230) or NULL? Does that also apply to partner rows?
6. **Partner rows with no single non-`Other` group.** D-03 covers a mapping row that has exactly one non-`Other` group. It does not say what happens when a partner enum's row has several different non-`Other` groups, or when a partner enum (for example the D-01 enums with no Google type) has none. Is the value `Other`, or does the Constraints `USER_DECISION` rule apply?
7. **Three short wheelchair names.** D-05 maps `wheelchairAccessibleEntrance`, `wheelchairAccessibleRestroom` and `wheelchairAccessibleSeating` to existing prefixed rows "without adding new rows". No column holds an alias, and `amenity_raw` is part of the key. Is this a documentation-only mapping, or is a column or value change needed? If a change is needed, which column and value? This design adds nothing.
8. **`is_active` for the 17 new amenity rows** and for the new D-04 place-type rows: no value is given. Should it match the existing seed default?
9. **Row counts.** `01_DATA_MODEL.md` L343–L344 records 356 and 158 rows. The new counts depend on which D-04 tokens already exist, and I cannot verify that from the files in scope. Implementation should report the counts so that the data model line can be updated.
