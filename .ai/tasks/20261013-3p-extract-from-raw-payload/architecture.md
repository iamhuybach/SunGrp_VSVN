RESULT: PASS

# Architecture: 3P extract reads `raw_payload` instead of `normalized_payload` (round 2)

Task: `20261013-3p-extract-from-raw-payload`. Architect: `claude-opus-5-5`, effort `high`. Round 2 replaces the round-1 document in full.

## 0. Verdict rationale

Round 1 returned `EVIDENCE_REQUIRED` and listed probes P1–P6 and user decisions U1–U5. Their state now:

- Results for P1–P6 are under `evidence/results/`. They cover the whole DEV population: 53 bronze rows, 17 POIs, `source_name = google` only.
- `decision.md` records the user decisions of 2026-10-13: Q1–Q4, Q16, `open_now`, media, and the evening section. That section covers city, ward, and component first type, price, `is_24_7`, secondary hours, amenity L1, `primary_type`, the removal list, "gold and silver L2 out of scope", and U4.
- Round-1 decisions are resolved as follows:
  - U1 is superseded by the amenity L1 decision.
  - U2 is covered by Q4: every column the raw extract does not fill is removed.
  - U3 and U4 are answered: gold is out of scope, and the gold snapshot is not handled here.
  - U5 becomes the prod rollout gate in §13.5.

Every remaining design choice is either decided by the user or proven by P1–P6:

- Columns kept with no rule change are equal on all 53 rows (P3, P4).
- Address columns follow the user's first-type rule. The user accepted the known `city` and `ward` differences.
- The `price_level` tokens observed in DEV map to the normalized integers (P5). Unobserved tokens fail closed.
- Periods are equal under both null settings (P5). `open_now` matches 53/53 (P5).
- Media and review keys are stable (P4).

One cross-task consequence remains, and it is not an evidence gap. The user put gold out of scope and said this task does not edit gold notebooks. `NB_ENR_POI_INFO` and `NB_ENR_POI_COORDINATE` read five silver columns by name, and Q4 removes all five. After cutover those two nodes would fail at analysis time. This design closes that hazard with invariant I7 and rollout gate UA1: `PL_VV_TRANS_SLV_TO_ENR_15P` stays disabled from the freeze until a separate gold task is deployed. The failure is fail-closed: an analysis error happens before any append, so gold data is not corrupted. The open item is an availability and acceptance decision for the user, not a design gap.

The evidence gate can move to `pass` on P1–P6 for DEV. Prod needs the read-only probe re-run in §13.5 before its own cutover.

## 1. Context and scope

Current state (repository, 2026-10-14):

- `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`:
  - Reads `RAW_PAYLOAD = "normalized_payload"`.
  - `classify_docs` parses each needed top-level field once into `_b__<field>` (string; objects and arrays stay JSON text; booleans become `true`/`false`).
  - `expand_rows` splits rows by `DOC` / `DOC_ARRAY`.
  - `build_table_rows` builds `_raw__*`, then `convert_sql`/`derived_sql`, then `_cn__*` flags.
  - `resolve_latest` keeps one row per key.
  - MERGE applies the `(_crawled_at, _event_id)` guard.
  - It holds normalized-only constants: `KNOWN_TOP_KEYS`, `WATCH_BLOCKS`, `WATCH_EMPTY_OBJECT`, and `extra_info` inside `FORBIDDEN_PATH_HEADS`.
- `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` (shared with partner):
  - `CONVERT_RULES` and `DERIVED_RULES`.
  - `snapshot_path_error`, `build_table_specs`, `ensure_target` (creates the table or adds columns; never drops; type mismatch raises `ConfigError`), `run_merge`, state, reject, watermark, lock.
  - `JSON_PATH_RE = [A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*`. No path can select an array element, coalesce, map an enum, or build JSON.
- `notebooks/NB_CREATE_DDL.ipynb`:
  - `TABLE_CONFIGS_3P` has 10 tables, 98 columns, 15 inactive.
  - `seed_registry` uses `replaceWhere` by source with `REGISTRY_SCHEMA`.
  - The 3P `ctrl_mng_pipeline_config` seed is `INSERT … WHERE NOT EXISTS`, so editing seed values does not change existing rows.
  - A separate cell deletes removed tables from pipeline_config and registry.
- Gold `NB_ENR_POI_INFO`, `NB_ENR_POI_COORDINATE`, and `NB_ENR_POI_REVIEW` belong to flow `PL_VV_TRANS_SLV_TO_ENR_15P` (APPEND, every 15 minutes). They read `slv_3p_poi*` columns with `F.col(...)`. `opening_hours_text` is a verbatim copy of `slv_3p_poi_opening_hours.periods_json`.
- P6: the only `ctrl_mng_pipeline_config` edges from `slv_3p_poi*` are the ten `PL_VV_TRANS_SLV_TO_ENR_15P` edges. No `slv_poi*` table exists in DEV. `slv_3p_poi_policy` does not exist physically in DEV.

In scope:

1. Switch the 3P extract payload column to `raw_payload`. `RAW_EVENT_ID`, `RAW_DOC_ID = ("source_name", "source_id")`, and `RAW_LANG = "language_code"` are unchanged (Q1).
2. Add generic snapshot-only structural rules to the lib: `COALESCE`, `ARRAY_PICK`, `ENUM_MAP`, `ARRAY_PROJECT`, `POS_1BASED`, `JSON_PICK`. Add a validated `ctrl_cfg_schema_registry.convert_arg` column. All source key names and rule arguments live in ctrl; none live in code.
3. Rewrite `TABLE_CONFIGS_3P` as a first-time create (Q4): 9 tables, 52 columns, 0 inactive (§5). Every child `DOC` table moves to `src_object = $` (Q3). `DOC_ARRAY` tables move to `reviews` and `photos`.
4. Pipeline config: delete the `slv_3p_poi_policy` row. Change `slv_3p_poi_media.dedup_order` to `display_order ASC`.
5. Derive the extract's `watch` diagnostics from the registry and the document's top-level key set.
6. Add a run-time rule self-check and a recreated-target guard (§6.6, §6.7).
7. Silver migration in DEV: backup, completeness check, `DROP` and recreate the nine 3P silver tables, `full_reload`.
8. Docs, tests, and the Vietnamese runtime runbook (Main).

Systems touched:

- Bronze: read only.
- Silver L1: `slv_3p_poi_*`.
- Ctrl:
  - `ctrl_cfg_schema_registry`: DDL change and rows.
  - `ctrl_mng_pipeline_config`: rows.
  - `ctrl_cdc_state`, `ctrl_cdc_reject`, and the logs: written by side effect.
- Gold: no code change. The 15P flow schedule is disabled (I7).

## 2. Non-goals

- Dropping or altering bronze `normalized_payload`.
- Any gold notebook, gold DDL, or gold data change, including the gold snapshot after the silver table id changes (U4). A separate gold task owns that work (§13.4).
- Silver L2 (`slv_poi_*`): it does not exist in DEV. Sector or category mapping (`business_sector_rule.md`, `mapping_sector.md`), ward normalization (`ward_mapping_satnhap.txt`), and amenity flattening or filtering (`get_amenity.md`) are L2 work.
- New L1 columns for raw keys beyond the two the user approved (`slv_3p_poi.primary_type`, `slv_3p_poi_amenity.source_flags_json`). Not added:
  - `primaryTypeDisplayName`, `pureServiceAreaBusiness`, `addressComponents` as a whole, `plusCode.compoundCode`, `utcOffsetMinutes`, `googleMapsLinks`, `priceRange` as a whole, `currentOpeningHours` as a whole, secondary hours;
  - extra review and photo attributes;
  - `editorialSummary`, `generativeSummary`, `reviewSummary`, `routingSummaries`.

  Adding one later costs one registry row plus `full_reload` of its table.
- Business rules in L1: phone formatting, district, Vietmap, `address_line1`/`address_line2` construction, `is_24_7`, `is_temporarily_closed`.
- Partner extract behavior. The lib change is additive, and the new rules are rejected for `CDC` tables.
- Pipeline JSON changes. The 3P extract is not in any repository pipeline. `PL_VV_TRANS_SLV_TO_ENR_15P` only has its schedule disabled.
- Editing another task's BRD or Mapping (`docs/requirements/20261012-map-gld-enr-poi-tables/*`).

## 3. Invariants

- I1 Identity: on every 3P table, `poi_id = HASH_MD5_UUID(_doc.source_name, _doc.source_id)`. It is the state `entity_key` (`state_key = doc`). Raw `id` is never read (P1: `raw_id_ne_source_id = 0`).
- I2 Structural extract only. The extract may:
  - split arrays;
  - select an array element by the first item of a tag array;
  - cast;
  - coalesce two paths;
  - map a published enum to its index;
  - copy a declared subset of top-level keys verbatim;
  - compute a 1-based position.

  Nothing else.
- I3 No source key names in notebook or lib code. Every source path and rule argument comes from `ctrl_cfg_schema_registry` (`json_path`, `convert_rule`, `convert_arg`).
- I4 Fail closed:
  - Configuration and argument errors raise `ConfigError` before the lock.
  - Value or shape errors are flagged per column in `_cn__<col>` and fail the table before MERGE under `cast_null_policy = FAIL`. They include: unknown enum token, a non-array where an array is declared, a period field that cannot be cast, and a `JSON_PICK` kind mismatch.
  - A rule self-check failure on literal fixtures raises `ConfigError` before reading.
- I5 Ordering: the target MERGE updates only when `(s._crawled_at, s._event_id) >= (t._crawled_at, t._event_id)`. `ctrl_cdc_state` never regresses. Both payloads sit on the same bronze row, so ordering keys are unchanged across cutover.
- I6 Consistent triple: no 3P extract run executes while code version, registry content, and physical silver schema disagree. During cutover this is enforced by the held source lock and the deploy order (§13). In steady state it is enforced by I4.
- I7 Gold isolation: `PL_VV_TRANS_SLV_TO_ENR_15P` does not run against the new silver shape until a gold task has removed every read of a removed silver column (§5.11). The flow schedule stays disabled from the freeze until then.
- I8 Bronze is never written. `normalized_payload` stays, so the old silver can always be rebuilt with the old code (rollback R2).
- I9 One writer per silver table (one extract thread). The extract main thread is the only writer of ctrl state, reject, and log rows. Unchanged.
- I10 Q3 cardinality: after a full init, every `DOC` table has exactly one row per `poi_id` of VALID documents. A NULL source value overwrites the older value.
- I11 A recreated (empty) target is never filled by an incremental run. It requires `full_reload` (§6.7).
- I12 Completeness before destruction: no silver table is dropped unless every `slv_3p_poi.poi_id` that exists before cutover can be rebuilt from in-scope bronze (§13.2 step 8).

## 4. State ownership, grain, and keys

| State | Only writer | Grain / key | Change |
|---|---|---|---|
| `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` | Collector / Eventstream | 1 row / event | Read only. Column read: `raw_payload` |
| `slv_3p_poi` | 3P extract | 1 row / `poi_id` | Recreated. 10 columns |
| `slv_3p_poi_address` | 3P extract | 1 row / `poi_id` | Recreated. `src_object $`. 12 columns |
| `slv_3p_poi_contact` | 3P extract | 1 row / `poi_id` | Recreated. `src_object $`. 3 columns |
| `slv_3p_poi_price` | 3P extract | 1 row / `poi_id` | Recreated. `src_object $`. 5 columns. Every VALID document now produces a row (Q3) |
| `slv_3p_poi_opening_hours` | 3P extract | 1 row / `poi_id` | Recreated. `src_object $`. 4 columns |
| `slv_3p_poi_rating` | 3P extract | 1 row / `poi_id` | Recreated. `src_object $`. 3 columns |
| `slv_3p_poi_amenity` | 3P extract | 1 row / `poi_id` | Recreated. `src_object $`. `poi_id`, `source_flags_json` |
| `slv_3p_poi_review` | 3P extract | 1 row / `review_id = HASH_SHA256(source_name, source_id, authorAttribution.displayName, publishTime)` | Recreated. `src_object reviews`. P4: key equals the old key on 265/265 |
| `slv_3p_poi_media` | 3P extract | 1 row / `media_dedup_key = HASH_SHA256_PIPE(source_name, source_id, name)` | Recreated. `src_object photos`. All photos (DEV: 10 per document instead of 5). Old keys are a subset (P4) |
| `slv_3p_poi_policy` | — | — | Removed: registry rows, pipeline_config row, `DROP TABLE IF EXISTS` |
| `ctrl_cfg_schema_registry` | Operator via `NB_CREATE_DDL` | 1 row / (source, target, column) | New nullable `convert_arg`. 3P rows rewritten |
| `ctrl_mng_pipeline_config` | Operator via `NB_CREATE_DDL` | 1 row / (pl, source, target) | Policy row deleted. Media `dedup_order` updated |
| `ctrl_cdc_state`, `ctrl_cdc_reject`, `ctrl_log_run`, `ctrl_log_table_run`, 3P row of `ctrl_mng_watermark` | 3P extract (main thread) | Unchanged | No schema change. Rejected documents store `raw_payload` text in `after_payload` |
| `gld_enr_poi_info`, `gld_enr_poi_coordinate`, `gld_enr_poi_review` | Nodes of `NB_00_ORCHES_SLV_TO_ENR_15P` | APPEND history | Untouched by this task. The flow is paused (I7) |

DEV cardinality after full init:

- Each `DOC` table: 17 rows.
- `slv_3p_poi_review`: the number of distinct `review_id` across 53 documents (265 elements in total). It must be a superset of the old keys.
- `slv_3p_poi_media`: the number of distinct `media_dedup_key` over 530 elements. It must be a superset of the old keys.

## 5. Final column disposition

Legend for evidence:

- `P3=`: equal on every DEV row where either side is non-null.
- `P4=`: equal for every element.
- `USER`: the value is defined by a user decision that knowingly differs from the old normalized value.
- `NEW`: no normalized counterpart.

Column order is the order listed. All rows have `is_active = true`.

### 5.1 `slv_3p_poi` (`DOC`, `src_object $`)

| Column | `json_path` | Type | Rule | Evidence |
|---|---|---|---|---|
| `poi_id` (key) | `_doc.source_name,_doc.source_id` | string | `HASH_MD5_UUID` | unchanged |
| `source_name` | `_doc.source_name` | string | `NONE` | unchanged |
| `source_id` | `_doc.source_id` | string | `NONE` | unchanged |
| `language_code` | `_doc.language_code` | string | `LOWER_TRIM` | unchanged |
| `poi_name` | `displayName` | string | `NONE` | P2: string 100%, `displayName.text` absent. P3= |
| `poi_name_normalized` | `displayName` | string | `LOWER_TRIM` | P3= |
| `types_json` | `types` | string | `NONE` | P3= |
| `subcategory_tags_json` | `types` | string | `NONE` | P3= (decision: equals `types`) |
| `operating_status` | `businessStatus` | string | `LOWER_TRIM` | P3= |
| `primary_type` | `primaryType` | string | `NONE` | NEW (user). P2: string 53/53 |

Removed (Q4): `business_sector`, `business_category`, `slug`, `partner_id`, `collector_poi_id`, `facilities_json`, `source_created_at`, `accommodation_type`, `star_rating`, `awards_json`, `slug_history_json`, `poi_amenity_schema_json`.

### 5.2 `slv_3p_poi_address` (`DOC`, `src_object poi_address → $`)

| Column | `json_path` | Type | Rule | `convert_arg` | Evidence |
|---|---|---|---|---|---|
| `poi_id` (key) | `_doc.source_name,_doc.source_id` | string | `HASH_MD5_UUID` | — | unchanged |
| `house_number` | `addressComponents` | string | `ARRAY_PICK` | `{"match":"types","values":["street_number"],"take":"longText"}` | P3= (18 equal, 35 both null) |
| `street` | `addressComponents` | string | `ARRAY_PICK` | `{"match":"types","values":["route"],"take":"longText"}` | P3= (19 / 34) |
| `ward` | `addressComponents` | string | `ARRAY_PICK` | `{"match":"types","values":["administrative_area_level_2"],"take":"longText"}` | USER (17 equal, 36 old-only) |
| `city` | `addressComponents` | string | `ARRAY_PICK` | `{"match":"types","values":["administrative_area_level_1"],"take":"longText"}` | USER (20 equal, 33 differ) |
| `state_province` | `addressComponents` | string | `ARRAY_PICK` | `{"match":"types","values":["administrative_area_level_1"],"take":"longText"}` | P3= |
| `country_code` | `addressComponents` | string | `ARRAY_PICK` | `{"match":"types","values":["country"],"take":"shortText"}` | P3= |
| `postal_code` | `addressComponents` | string | `ARRAY_PICK` | `{"match":"types","values":["postal_code"],"take":"longText"}` | P3= (44 / 9) |
| `full_address` | `formattedAddress` | string | `NONE` | — | P3= |
| `lat` | `location.latitude` | double | `NONE` | — | P3= |
| `lng` | `location.longitude` | double | `NONE` | — | P3= |
| `plus_code` | `plusCode.globalCode` | string | `NONE` | — | P3= |

Removed (Q4 and the evening decisions): `address_line1`, `address_line2`, `district`, `country`, `short_address`, `address_viet_map`, `vietmap_status`, `vietmap_message`, `timezone`.

`ARRAY_PICK` matches on the first item of the element's `types` array, per the user decision "lấy type đầu tiên". P3 measured with "token contained in `types`". The P3 attribution prints `types` in source order, and every matched component had the token in first position (`street_number`, `route`, `postal_code`, `administrative_area_level_1+political`, `administrative_area_level_2+political`, `country+political`). Runtime acceptance (§13.2 step 11) re-checks parity against the pre-cutover silver.

### 5.3 `slv_3p_poi_contact` (`DOC`, `src_object poi_contact → $`)

| Column | `json_path` | Type | Rule | Evidence |
|---|---|---|---|---|
| `poi_id` (key) | `_doc.source_name,_doc.source_id` | string | `HASH_MD5_UUID` | unchanged |
| `website_url` | `websiteUri` | string | `NONE` | P3= |
| `google_maps_url` | `googleMapsUri` | string | `NONE` | P3= |

Removed: `phone`, `phone_raw`, `booking_links_json`, `delivery_links_json`, `social_links_json`.

### 5.4 `slv_3p_poi_price` (`DOC`, `src_object poi_price → $`)

| Column | `json_path` | Type | Rule | `convert_arg` | Evidence |
|---|---|---|---|---|---|
| `poi_id` (key) | `_doc.source_name,_doc.source_id` | string | `HASH_MD5_UUID` | — | unchanged |
| `currency` | `priceRange.startPrice.currencyCode` | string | `NONE` | — | P3= (13 / 40) |
| `price_level` | `priceLevel` | int | `ENUM_MAP` | `{"map":{"PRICE_LEVEL_FREE":0,"PRICE_LEVEL_INEXPENSIVE":1,"PRICE_LEVEL_MODERATE":2,"PRICE_LEVEL_EXPENSIVE":3,"PRICE_LEVEL_VERY_EXPENSIVE":4}}` | P5: INEXPENSIVE→1 (6), MODERATE→2 (7), null (40). The other three entries follow the user decision "theo chỉ số Google". Any other token, including `PRICE_LEVEL_UNSPECIFIED`, fails closed (§8) |
| `price_min` | `priceRange.startPrice.units` | decimal(18,2) | `NONE` | — | P3 `equal_after_trim` (13 / 40): the raw side is a string, equal in value |
| `price_max` | `priceRange.endPrice.units` | decimal(18,2) | `NONE` | — | P3 `equal_after_trim` (13 / 40) |

`units` carries the integer part only. `nanos` is not read (user decision). A `units` value that overflows `decimal(18,2)` casts to NULL and fails closed through `_cn__`.

### 5.5 `slv_3p_poi_opening_hours` (`DOC`, `src_object poi_opening_hours → $`)

| Column | `json_path` | Type | Rule | `convert_arg` | Evidence |
|---|---|---|---|---|---|
| `poi_id` (key) | `_doc.source_name,_doc.source_id` | string | `HASH_MD5_UUID` | — | unchanged |
| `periods_json` | `regularOpeningHours.periods` | string | `ARRAY_PROJECT` | `{"fields":[{"name":"close_hour","path":"close.hour","type":"int"},{"name":"close_day","path":"close.day","type":"int"},{"name":"open_hour","path":"open.hour","type":"int"},{"name":"close_minute","path":"close.minute","type":"int"},{"name":"open_minute","path":"open.minute","type":"int"},{"name":"day_of_week","path":"open.day","type":"int"}],"keep_nulls":false}` | P5: semantic equality 53/53. The field order reproduces the normalized key order (48/48), so gold `opening_hours_text`, a verbatim copy, keeps its text |
| `weekday_text_json` | `regularOpeningHours.weekdayDescriptions` | string | `NONE` | — | P3= (48 / 5) |
| `open_now` | `currentOpeningHours.openNow,regularOpeningHours.openNow` | boolean | `COALESCE` | — | P5: current equals normalized on 48. Current absent and regular equal on 5 |

Removed: `is_24_7`, `is_temporarily_closed`, `secondary_hours_json`.

`keep_nulls = false` was chosen because P5 cannot tell the two settings apart (no period lacks `close`). With `false`, a missing source field becomes a missing JSON key, which mirrors the source and invents no explicit nulls. The setting changes output only for periods that lack `close`, and none are observed.

`COALESCE` works at value level. The user rule works at block level ("current block absent → regular"). The two differ only when `currentOpeningHours` is an object without `openNow`. P2 shows 0 such documents: all 48 current objects carry a boolean `openNow`. Main records this interpretation in `decision.md`.

### 5.6 `slv_3p_poi_rating` (`DOC`, `src_object poi_rating → $`)

| Column | `json_path` | Type | Rule | Evidence |
|---|---|---|---|---|
| `poi_id` (key) | `_doc.source_name,_doc.source_id` | string | `HASH_MD5_UUID` | unchanged |
| `rating_overall` | `rating` | decimal(4,2) | `NONE` | P3= |
| `rating_count` | `userRatingCount` | bigint | `NONE` | P3= (P2: integer) |

Removed: `rating_breakdown_json`, `sub_ratings_json`. Both were inactive and never existed physically.

### 5.7 `slv_3p_poi_amenity` (`DOC`, `src_object poi_amenity → $`)

| Column | `json_path` | Type | Rule | Evidence |
|---|---|---|---|---|
| `poi_id` (key) | `_doc.source_name,_doc.source_id` | string | `HASH_MD5_UUID` | unchanged |
| `source_flags_json` | `servesBreakfast,servesBrunch,servesLunch,servesDinner,servesBeer,servesWine,servesCocktails,servesDessert,servesCoffee,servesVegetarianFood,allowsDogs,goodForChildren,goodForGroups,goodForWatchingSports,liveMusic,menuForChildren,outdoorSeating,restroom,reservable,takeout,delivery,dineIn,curbsidePickup,parkingOptions,paymentOptions,accessibilityOptions,evChargeOptions,fuelOptions` | string | `JSON_PICK` | NEW (user, shape from `evidence/context/amenity-l1-demo.md`). P2: the 23 flags are boolean or null, the 5 options are object or null, all 28 keys are present in 53/53 |

`convert_arg` for `source_flags_json`:

```json
{"members":[
  {"name":"flags","kind":"boolean","keys":["servesBreakfast","servesBrunch","servesLunch","servesDinner","servesBeer","servesWine","servesCocktails","servesDessert","servesCoffee","servesVegetarianFood","allowsDogs","goodForChildren","goodForGroups","goodForWatchingSports","liveMusic","menuForChildren","outdoorSeating","restroom","reservable","takeout","delivery","dineIn","curbsidePickup"]},
  {"key":"parkingOptions","kind":"object"},
  {"key":"paymentOptions","kind":"object"},
  {"key":"accessibilityOptions","kind":"object"},
  {"key":"evChargeOptions","kind":"object"},
  {"key":"fuelOptions","kind":"object"}
]}
```

Removed: `amenity_schema_json`, `ext_attributes_json`.

### 5.8 `slv_3p_poi_review` (`DOC_ARRAY`, `src_object poi_review → reviews`)

| Column | `json_path` | Type | Rule | Evidence |
|---|---|---|---|---|
| `review_id` (key) | `_doc.source_name,_doc.source_id,authorAttribution.displayName,publishTime` | string | `HASH_SHA256` | P4: `review_key` equal 265/265 |
| `poi_id` | `_doc.source_name,_doc.source_id` | string | `HASH_MD5_UUID` | unchanged |
| `author_name` | `authorAttribution.displayName` | string | `NONE` | P4= |
| `rating` | `rating` | decimal(4,2) | `NONE` | P4= |
| `text` | `text.text` | string | `NONE` | P4= |
| `time` | `publishTime` | string | `NONE` | P4= |
| `published_at` | `publishTime` | timestamp | `ISO_UTC_TS` | same input string as `time` |

Removed: `source`.

### 5.9 `slv_3p_poi_media` (`DOC_ARRAY`, `src_object poi_media → photos`)

| Column | `json_path` | Type | Rule | Evidence |
|---|---|---|---|---|
| `media_dedup_key` (key) | `_doc.source_name,_doc.source_id,name` | string | `HASH_SHA256_PIPE` | P4: `name = photo_api_uri` 265/265 on the overlapping 5 per document. No null or duplicate `name` |
| `poi_id` | `_doc.source_name,_doc.source_id` | string | `HASH_MD5_UUID` | unchanged |
| `photo_api_uri` | `name` | string | `NONE` | P4= |
| `display_order` | `_pos` | int | `POS_1BASED` | P4: normalized `display_order = index + 1` 265/265 |
| `width_px` | `widthPx` | int | `NONE` | USER. P2/P4: integer 530/530 |
| `height_px` | `heightPx` | int | `NONE` | USER. P2/P4: integer 530/530 |

Removed: `media_id`, `media_type`, `blob_url`, `original_url`, `thumbnail_url`, `processing_status`, `category`, `caption`, `is_blessed`, `photographer`, `license`, `file_size_bytes`.

### 5.10 Registry and pipeline_config changes

| Table | Rows | Change |
|---|---|---|
| `ctrl_cfg_schema_registry` (DDL) | — | `ADD COLUMNS (convert_arg STRING COMMENT 'Snapshot rule argument as JSON. NULL for rules without arguments')`. Also added to the `CREATE TABLE` statement and to `REGISTRY_SCHEMA` |
| `ctrl_cfg_schema_registry` | all 3P rows | Replaced by `seed_registry(TABLE_CONFIGS_3P)` (`replaceWhere` by source): 9 tables, 52 rows, 0 inactive, 10 rows with non-NULL `convert_arg` (7 `ARRAY_PICK`, `ENUM_MAP`, `ARRAY_PROJECT`, `JSON_PICK`). The policy rows disappear with the replace |
| `ctrl_mng_pipeline_config` | `slv_3p_poi_policy` | `DELETE` (existing row). Removed from the seed `VALUES` and added to the deletion cell |
| `ctrl_mng_pipeline_config` | `slv_3p_poi_media` | `UPDATE … SET dedup_order = 'display_order ASC'` (existing row). Same value in the seed `VALUES`. The old value `display_order ASC, media_id ASC` would raise `ConfigError` once `media_id` is gone |
| `ctrl_mng_pipeline_config` | the other 8 tables | `load_mode`, `align_path`, and `is_active` unchanged (`DOC` ×7, `DOC_ARRAY` ×2, active) |
| `ctrl_cdc_reject` (DDL comment) | — | `after_payload` comment says `raw_payload` instead of `normalized_payload` |

### 5.11 Consumer impact (recorded for the gold follow-up; no change in this task)

The following gold reads fail at analysis time against the new silver, so the 15P flow stays disabled (I7):

| Gold notebook | Gold column | Removed silver column |
|---|---|---|
| `NB_ENR_POI_INFO` | `business_sector`, `time_to_spend` (label input) | `slv_3p_poi.business_sector` |
| `NB_ENR_POI_INFO` | `business_category` | `slv_3p_poi.business_category` |
| `NB_ENR_POI_INFO` | `short_address` | `slv_3p_poi_address.address_viet_map` |
| `NB_ENR_POI_INFO` | `district`, `destination_context` | `slv_3p_poi_address.district` |
| `NB_ENR_POI_INFO` | `destination_context` | `slv_3p_poi_address.short_address` |
| `NB_ENR_POI_COORDINATE` | `short_address` | `slv_3p_poi_address.short_address` |
| `NB_ENR_POI_COORDINATE` | `district` | `slv_3p_poi_address.district` |

Value changes on kept columns, visible once gold resumes:

- `gld_enr_poi_coordinate.ward`: DEV 36 of 53 rows become NULL.
- `gld_enr_poi_coordinate.province_name` and `destination_name`, and `gld_enr_poi_info.destination_name` and `destination_context`: driven by `city`, which differs on 33 of 53 rows.
- Every gold edge from a recreated silver table sees a new table id and takes basis `FULL` once.

`NB_ENR_POI_REVIEW` reads only kept review columns and is unaffected, but it runs in the same paused flow.

## 6. Rule mechanism

### 6.1 Registry argument column

- `ctrl_cfg_schema_registry.convert_arg STRING` is nullable. Partner rows stay NULL.
- The lib reads it as optional (`table_has` pattern). If the column is missing, the value is NULL, so a ctrl table that has not been migrated still loads for partner.
- `ColumnSpec` gains `convert_arg: Optional[str] = None` as its last field, so positional constructors stay valid.
- `NB_CREATE_DDL`:
  - Each `TABLE_CONFIGS_3P` column spec takes an optional `"arg"` dict.
  - `flatten_table_configs` writes `json.dumps(arg, ensure_ascii=True, separators=(",", ":"))`, preserving key order. Without an `"arg"` it writes NULL.

### 6.2 Rule catalogue

All new rules are snapshot only and rejected for `CDC` tables in `build_table_specs`. SQL uses Spark built-ins only, with no UDF. `{cast}` is `CAST_FN`.

`parse_convert_arg(rule, text) -> dict` is a pure function in the lib. Text that does not parse raises `ValueError`, which `build_table_specs` collects into `ConfigError`.

Argument grammar:

- A JSON object with exactly the allowed keys.
- Identifiers match `IDENT_RE`.
- Element paths match `JSON_PATH_RE`.
- Tokens match `[A-Za-z0-9_]+`.
- Integers are non-bool and within int32.
- Field `type` is one of `int|bigint|string|boolean|double`.
- `kind` is one of `boolean|object`.
- Lists are non-empty, have no duplicates, and hold at most 64 items.

SQL text is built only from validated parts, so a registry value cannot inject SQL.

| Rule | load_mode / `src_object` | `json_path` | `data_type` | `convert_arg` | Raw → value | `_cn__` (cast-null) |
|---|---|---|---|---|---|---|
| `COALESCE` | any snapshot | ≥ 2 parts. Each part is a valid snapshot path, not `$` and not `_pos` | any | must be NULL | `_raw__c = coalesce(part0, part1, …)` in listed order, then `{cast}(_raw__c AS dt)` | standard: `_raw__c IS NOT NULL AND c IS NULL`. False for `string` |
| `ARRAY_PICK` | any snapshot | 1 part, path to a JSON array | `string` | `{"match": path, "values": [token…], "take": path}` | `get_json_object(coalesce(P(v1), P(v2), …), '$.<take>')`, where `P(v) = try_element_at(filter(from_json(raw, 'array<string>', opts), e -> get_json_object(e, '$.<match>[0]') = '<v>'), 1)`. The first array element (array order) whose `match` array has first item `v` wins. Values are tried in listed priority. No match → NULL | `raw IS NOT NULL AND from_json(raw, 'array<string>', opts) IS NULL` (declared array is not an array) |
| `ENUM_MAP` | any snapshot | 1 part | `int`, `bigint`, `smallint` | `{"map": {token: int, …}}` | `{cast}(CASE trim(raw) WHEN '<t1>' THEN <i1> … END AS dt)` | standard. An unknown non-NULL token is flagged |
| `ARRAY_PROJECT` | any snapshot | 1 part, path to a JSON array | `string` | `{"fields": [{"name": ident, "path": path, "type": t}, …], "keep_nulls": bool}` | `to_json(transform(from_json(raw, 'array<string>', opts), e -> named_struct('<n1>', {cast}(get_json_object(e, '$.<p1>') AS <t1>), …)), map('ignoreNullFields', '<not keep_nulls>'))`. NULL array → NULL. `[]` → `"[]"` | `raw IS NOT NULL AND (arr IS NULL OR exists(arr, e -> from_json(e, 'map<string,string>', opts) IS NULL OR (get_json_object(e, '$.<pi>') IS NOT NULL AND {cast}(… AS ti) IS NULL) OR …))` |
| `POS_1BASED` | `DOC_ARRAY` / `LANG_ARRAY` | exactly `_pos` | `int`, `bigint` | must be NULL | `{cast}({cast}(raw AS BIGINT) + 1 AS dt)` | never |
| `JSON_PICK` | `DOC` with `src_object $` | ≥ 1 parts, each an `IDENT_RE` top-level key, equal in order to the keys flattened from `convert_arg` | `string` | `{"members": [{"name": ident, "kind": k, "keys": [ident…]} \| {"key": ident, "kind": k}, …]}` | See below | `_bad__c` (see below) |

`JSON_PICK` composition, with `_top_keys` (§6.4) and part columns `p_i`:

- Group member: `concat('"<name>":{', concat_ws(',', CASE WHEN array_contains(_top_keys, '<k>') THEN concat('"<k>":', coalesce(p_k, 'null')) END, …), '}')`. A group is always emitted, possibly as `{}`.
- Single member: `CASE WHEN array_contains(_top_keys, '<k>') THEN concat('"<k>":', coalesce(p_k, 'null')) END`. It is emitted only when the key is present.
- Whole: `concat('{', concat_ws(',', <members>), '}')`.
- A key present with JSON null gives `null`. A missing key stays missing. This matches `amenity-l1-demo.md`.
- Kind check, true when the column is bad:
  - `_bad__c = OR_i(array_contains(_top_keys, '<k_i>') AND p_i IS NOT NULL AND NOT ok_i)`;
  - `ok` for boolean is `p IN ('true', 'false')`;
  - `ok` for object is `ltrim(p) LIKE '{%' AND from_json(p, 'map<string,string>', opts) IS NOT NULL`.
- Output: `CASE WHEN _bad__c THEN NULL ELSE <whole> END`. Malformed JSON is never written, and `_cn__c = _bad__c`.
- Values are copied verbatim. For booleans and objects the `parse_json_strings` text is valid compact JSON. A source string `"true"` cannot be told apart from a boolean and is copied as `true`. P2 shows no string values on these keys, and this residual is accepted.

### 6.3 Lib changes (`NB_LIB_EXTRACT_RAWDATA`)

- §1: `ARG_RULES = {ARRAY_PICK, ENUM_MAP, ARRAY_PROJECT, JSON_PICK}`, `MULTI_PART_RULES = DERIVED_RULES ∪ {COALESCE, JSON_PICK}`, `SNAPSHOT_ONLY_RULES = DERIVED_RULES ∪ {COALESCE, ARRAY_PICK, ENUM_MAP, ARRAY_PROJECT, POS_1BASED, JSON_PICK}`.
- §6:
  - `parse_convert_arg`.
  - `convert_sql(raw_col, data_type, rule, arg=None)` adds the single-raw rules. It keeps the signature backward compatible: old rules ignore `arg`.
  - `compose_raw_sql(c)` builds `_raw__c` for `COALESCE` and `JSON_PICK` from `c.part_cols`, plus `pick_bad_sql(c)`.
  - `cast_null_sql(c)` returns the `_cn__` expression: the standard formula by default, the rule-specific one from §6.2 otherwise.
  - `RULE_SELF_CHECK` fixtures and `assert_rule_sql()` (§6.6).
  - The pure parts sit between `# BEGIN_RULE_PURE` and `# END_RULE_PURE` for tests.
- §8 `ColumnSpec`:
  - `convert_arg`;
  - `is_multi_part` (`convert_rule in MULTI_PART_RULES`);
  - `part_cols` applies to every multi-part rule;
  - `is_derived` stays `HASH_*` only;
  - `can_cast_null` is true for `ENUM_MAP`, `ARRAY_PROJECT`, `ARRAY_PICK`, `JSON_PICK`, and non-string `COALESCE`; false for `POS_1BASED`.
- §9 `build_table_specs`:
  - Enforce the §6.2 matrix: snapshot only, load_mode / `src_object`, part count, part grammar, `data_type`, argument presence and grammar, `JSON_PICK` key/path equality.
  - The multi-part check changes from `DERIVED_RULES` to `MULTI_PART_RULES`.
  - `load_table_specs` selects `convert_arg` if present, otherwise `CAST(NULL AS STRING)`.
- Header change-log row.

### 6.4 Extract notebook changes

- `RAW_PAYLOAD = "raw_payload"`.
- Remove `KNOWN_TOP_KEYS`, `WATCH_BLOCKS`, and `WATCH_EMPTY_OBJECT`. Set `FORBIDDEN_PATH_HEADS = ("_lang", "_langs", "_align")`.
- `classify_docs` adds `_top_keys = CASE WHEN VALID THEN json_object_keys(_payload) END` (array<string>). It removes the `_w__*` columns. `_payload` is still kept only for REJECTED.
- `expand_rows` carries `_top_keys` in `meta` for root `DOC` specs.
- `build_table_rows`:
  - For `is_multi_part and not is_derived`, build the part columns, then `_raw__c = compose_raw_sql(c)` and `_bad__c` (for `JSON_PICK`), then the typed column.
  - Pass `c.convert_arg` to `convert_sql`.
  - Compute `_cn__c` with `cast_null_sql(c)`.
- `profile_docs` returns `watch` as defined in §6.5.
- `_run_table` adds the recreated-target guard (§6.7).
- `run_extract` calls `assert_rule_sql()` next to `assert_utc_format()`, before `load_table_specs`.
- Markdown tables are updated: constants, `watch`, target tables. No source key name appears in code (I3).

### 6.5 `watch` (exit JSON `extra.watch`)

- `unmapped_top_keys` = {key: number of VALID documents}, counting top-level keys that no active spec uses as a head. A head is the first segment of a non-scoped path of a root `DOC` spec, a `src_object` head of a `DOC_ARRAY` spec, or a `_root.` head. Logged at INFO. Raw carries many intentionally unmapped keys.
- `mapped_heads_missing` = {head: number of VALID documents whose `_top_keys` lacks the head}. Logged at WARN. P2 shows every mapped head present in 53/53 (raw serializes absent values as JSON null), so any count > 0 signals collector schema drift. It does not change run status. It is a hard criterion of the cutover dry-run gate (§13.2 step 6).

### 6.6 Rule self-check

`assert_rule_sql()` follows the `assert_utc_format` pattern. It runs one `spark.sql` over synthetic literal fixtures, with no source data, and raises `ConfigError` on any mismatch.

Cases:

- `ARRAY_PICK`:
  - first-type match wins over a later element;
  - an element whose token is not first does not match;
  - no match gives NULL;
  - a non-array raw gives NULL with `_cn__` true.
- `ENUM_MAP`: known token, NULL, and an unknown token (`_cn__` true).
- `ARRAY_PROJECT`: field order in the output text, int typing, `ignoreNullFields` for a missing `close`, and `[]`.
- `JSON_PICK`: present-true, present-null, missing, and object kind; a string in a boolean slot gives `_bad` true.
- `COALESCE`: first non-NULL.
- `POS_1BASED`: `0` → `1`.

This proves on the deployed Spark runtime (Runtime 1.3 or 2.0, ANSI on or off) the behavior that local tests can only assert as SQL text.

### 6.7 Recreated-target guard

In `_run_table`, before `ensure_target`: if the target does not exist, the run is not `full_reload`, and `load_state` holds at least one row for this `(trg_schema, trg_tbl)`, raise `ConfigError("<table>: target missing but ctrl_cdc_state has state; run full_reload")` without creating the table.

Without the guard, an incremental run after `DROP` would treat every already-applied document as stale and leave the recreated table almost empty (I11).

## 7. Ordering and transaction boundaries

Per extract run (framework unchanged, `run_controlled`):

1. `assert_utc_format`, `assert_rule_sql`, `load_table_specs`, `check_config`. No writes. `ConfigError` stops here, before the lock.
2. `acquire_lock` on `wm_transform_brz_3rd_crawler_poi_stream` (one Delta commit), then `write_run_log(RUNNING)`.
3. `pin_snapshot` (`v_to`). Read with `VERSION` or `FULL`.
4. Classify and profile. One wave of 9 tables. Per table: build rows → cast-null check → `resolve_latest` → one target MERGE commit.
5. `commit`: one `ctrl_cdc_state` MERGE for the SUCCESS tables → `merge_rejects` → table log append.
6. `finalize_watermark`, only for an incremental run without `table_filter`, without `full_reload`, and with every table SUCCESS or NO_DATA. Then run log, then `release_lock`.

There is no cross-table atomicity. The commit order target MERGE → state → reject → log → watermark is preserved. A crash after a target MERGE and before the state commit leads to reprocessing, and reapplication is idempotent under the `>=` guard.

Cutover config writes, one Delta commit each, run in this order:

- C1: guarded `ALTER TABLE … ADD COLUMNS (convert_arg …)`, run only if the column is missing.
- C2: `seed_registry(TABLE_CONFIGS_3P, …)`. It must run after C1, because the DataFrame carries `convert_arg`.
- C3: `DELETE` the policy row from pipeline_config.
- C4: `UPDATE` media `dedup_order`.

C1–C4 are not atomic together. Partial states fail closed at the next run's validation:

- `dedup_order` references `media_id`, which has no registry column → `ConfigError`.
- An active policy row with no registry rows → `ConfigError`.
- The old lib meeting new rule names → `convert_rule không hỗ trợ`.

Two mismatches pass validation, and both would write mostly NULLs:

- new registry with the old notebook;
- old registry with the new notebook.

Under Q3 such NULLs would overwrite child rows. They are excluded by I6: the held source lock plus the deploy order (code, then config) during cutover, and the dry-run gate before any write (§13). Gold cannot propagate such a state because the 15P flow is disabled (I7).

## 8. Idempotency, concurrency, retry and recovery

Idempotency:

- Re-running `full_reload` gives `inserted_rows = 0`. `updated_rows` equals the entity count, because an equal `(crawled_at, event_id)` still updates. Business columns are identical; `updated_at` moves.
- An incremental re-run after success gives `NO_DATA`.
- Determinism:
  - array order then priority order (`ARRAY_PICK`);
  - `transform` keeps element order;
  - `named_struct` fixes key order;
  - `JSON_PICK` member and key order come from `convert_arg`;
  - `resolve_latest` order is `(crawled_at, event_id)` desc, then `dedup_order`, then `_pos`.

Concurrency:

- The source lock blocks overlapping 3P runs (`SKIPPED_CONCURRENT`), whoever invokes them. This covers the external 3P invoker, which is not in a repository pipeline (P6 did not list it).
- Partner runs concurrently with no conflict: separate lock rows, and state and reject MERGEs constrained to partition `src_tbl`.
- Deploying the lib while partner runs is safe. A running session keeps the lib it loaded through `%run`, and the change is additive and snapshot-only.
- A registry `ALTER` or seed while partner reads is safe under snapshot isolation.
- Gold: the flow lock of `PL_VV_TRANS_SLV_TO_ENR_15P` times out after 35 minutes, so the control is a disabled schedule plus a confirmed absence of running instances, not a held lock.

Recovery:

- A table FAILED (transient or code): run `full_reload = True, table_filter = <table>`. It reads all bronze, ignores state for reading, and commits state without regressing it.
- `CastNullError` on `price_level` (new token): stop. The user records the token's integer in `decision.md`. Update that registry row's `convert_arg` with a reseed or a one-row `UPDATE`, then `full_reload` that table. Never switch the policy to `WARN`, because that writes NULL over valid values.
- `CastNullError` on `ARRAY_PICK`, `ARRAY_PROJECT`, or `JSON_PICK` (shape drift): treat as a `data` runtime failure and route to evidence. The watermark holds, so no document is lost.
- `ConfigError` from the recreated-target guard: run `full_reload`.
- `ConfigError` from `assert_rule_sql`: runtime behavior differs. Treat as a `code` failure. Nothing has been read or written.

## 9. Partial failures

| Failure point | Durable effect | Behavior and recovery |
|---|---|---|
| C1–C4 partially applied | ctrl partially updated | The next run fails closed (§7). Complete the remaining cells, then re-run the dry run |
| Lib deployed, extract not | none | Runs are blocked by the held lock. Complete the deploy |
| Backups made, `DROP` partial | some silver tables missing | Lock held, gold disabled. Forward: finish `DROP`, then full init. Back: R2 |
| Full init: some tables FAILED | other tables committed, state only for SUCCESS, watermark untouched | `full_reload` plus `table_filter` for the failed tables. Acceptance waits for all SUCCESS |
| Crash after target MERGE, before state commit | target ahead of state | Re-run reapplies identical rows |
| Element reject (review missing author or time, photo missing `name`) | `ctrl_cdc_reject` row, table SUCCESS | Unchanged semantics. P4 expects 0 in DEV |
| Document REJECTED (blank, not an object) | reject row with raw text | P1 expects 0 in DEV. Any non-zero blocks acceptance |
| External invoker runs incremental right after `DROP` | none | The recreated-target guard fails the tables before creation |
| Gold flow re-enabled by mistake | gold info and coordinate nodes fail at analysis, no append; review node may append | Disable the schedule again. Gold is not corrupted, and the review append is valid data |

## 10. Alternatives and trade-offs

1. Payload source.
   - (a) `raw_payload` only. **Selected** (user intent; Q1–Q4).
   - (b) Keep `normalized_payload`. Rejected: that is the status quo.
   - (c) Hybrid: raw for proven columns, normalized for sector, district, and phone. Rejected: two payload contracts, a double parse, it blocks removing `normalized_payload` later, and it contradicts Q4.
   - Cost of (a): collector-side enrichment (sector, district, Vietmap, phone format) leaves silver until L2 rebuilds it.
2. Structural rules.
   - (a) Generic snapshot rules with a validated `convert_arg`. **Selected**: configuration only, no source names in code, injection-safe, testable as pure builders, and proven on the deployed runtime by the self-check.
   - (b) Notebook branches on Google keys. Rejected by `decision.md`.
   - (c) A free-form SQL-expression rule. Rejected: injection surface and unreviewable.
   - (d) Arguments encoded in `json_path`. Rejected: overloads one field, and enum maps and member lists do not fit.
   - (e) A staging silver table that recreates the normalized shape. Rejected: extra state, and it re-implements the collector.
   - Cost of (a): one additive ctrl column, and a lib change shared with partner. Mitigated by the optional column read, snapshot-only rules, and a partner dry run.
3. Amenity storage.
   - (a) `JSON_PICK` into `source_flags_json`, keeping key presence and JSON types. **Selected** (user shape).
   - (b) 23 boolean and 5 JSON columns. Rejected by the user ("Không thêm 23 cột boolean").
   - (c) `to_json(map_filter(from_json(payload, 'map<string,string>'), …))`. Rejected: booleans become strings and the demo shape is lost.
   - (d) Store the whole raw payload. Rejected: duplicates bronze and widens the personal-data footprint.
4. Address element selection.
   - (a) First item of `types`. **Selected** (user).
   - (b) Token contained anywhere in `types` (the P3 measurement). Not selected, but it gives the same results on every DEV match. Runtime parity re-checks (a).
5. Schema migration.
   - (a) Backup, completeness check, `DROP TABLE`, `ensure_target` re-create, `full_reload`. **Selected** (Q4 "tạo lần đầu").
   - (b) Column mapping plus `DROP COLUMN`. Rejected: protocol upgrade, and `delta_added_files` refuses column mapping.
   - (c) `is_active = false`. Rejected by Q4.
   - (d) Keep orphan physical columns. Rejected: gold would keep reading stale normalized values mixed with raw values.
   - (e) New versioned table names. Rejected: naming convention and consumer churn.
   - Cost of (a): new table ids, so gold takes basis `FULL` once when it resumes.
6. Child `DOC` semantics.
   - `src_object $` with NULL overwrite. **Selected** (Q3).
   - Anchor key per table. Rejected by the user.
7. Gold during cutover.
   - (a) Disable the 15P schedule until a gold task removes the reads in §5.11. **Selected**: it respects "gold out of scope", fails closed, and corrupts no history.
   - (b) Typed NULL literals in gold within this task. Rejected by the user.
   - (c) Leave the flow enabled and failing. Rejected: noisy, and the review node keeps appending while info and coordinate fail, which gives inconsistent gold freshness.
   - (d) Keep the removed silver columns for gold. Rejected by Q4.
8. Protection against code/config mismatch.
   - (a) Held source lock, deploy order, and a dry-run gate. **Selected**.
   - (b) A code-level contract marker in the registry. Rejected: implicit coupling, and it adds nothing once the cutover is complete.
9. `watch`.
   - Registry and `_top_keys` derived. **Selected**.
   - Keep the constants. Rejected: source names in code, and every run would warn.
   - Delete `watch`. Rejected: it loses the drift signal.

## 11. Observability

- Exit JSON keeps its existing keys, plus `extra.watch.unmapped_top_keys` and `extra.watch.mapped_heads_missing`. Also reported: the per-column `cast_null` map (an unknown enum token shows as `price_level`), `docs_by_table` (each `DOC` table = valid documents), and `bad_shape` (`reviews`/`photos` not an array).
- Self-check: a `log` line "rule SQL self-check PASS" with the runtime ANSI flag.
- `ctrl_log_table_run` per table and attempt: `input_rows`, `stale_rows`, `applicable_rows`, `inserted_rows`, `updated_rows`, `cast_null_rows`, `rejected_rows`.
- `ctrl_cdc_reject` grouped by `trg_tbl`, `reject_reason`, and `reject_detail` (query in `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §10).
- Runbook acceptance metrics, counts only (§13.2 step 11).

## 12. Security and data handling

- Raw reviews and photos contain personal data (reviewer display names, review text). Normalized already carried author names and review text, so the data class is unchanged. Volume grows because all photos are kept. No author URI, author photo URI, or `originalText` is stored (non-goal).
- `ctrl_cdc_reject.after_payload` stores the full `raw_payload` for rejected documents. Access to ctrl must stay restricted at the silver level.
- `bak_*` tables hold the same data class as silver. They live in `lh_vv_silver` only during DEV acceptance and are dropped afterwards.
- `convert_arg` is untrusted input: closed grammar, identifier, token, and path regexes, and fixed type and kind lists. SQL is built only from validated parts.
- Evidence and runbook outputs contain counts, key names, JSON type names, and enum and component tokens only. No values. At most 50 rows.
- No secrets are involved.

## 13. Rollout, rollback, and forward recovery

### 13.1 Preconditions (DEV)

- Architecture PASS (this document), local verification PASS, and specialist reviews plus `risk-gate` PASS.
- UA1 recorded in `decision.md` by the user. It states that:
  - `PL_VV_TRANS_SLV_TO_ENR_15P` stays disabled from step 2 until a gold task removes the §5.11 reads;
  - the gold task id, or an R2 rollback, is the exit from that state.
- Baseline recorded:
  - version and row count of every `slv_3p_poi*` and `gld_enr_*` table;
  - the 3P watermark row;
  - the 15P flow watermark rows;
  - `ctrl_cdc_state` and `ctrl_cdc_reject` counts for `src_tbl = 'brz_3rd_crawler_poi_stream'`.

### 13.2 Steps (Main writes the Vietnamese runbook in this order)

1. Baseline (above).
2. Freeze:
   - Disable the `PL_VV_TRANS_SLV_TO_ENR_15P` schedule.
   - Confirm no running instance, and `lock_exec_id IS NULL` on `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`.
   - Confirm `lock_exec_id IS NULL` on `wm_transform_brz_3rd_crawler_poi_stream`.
   - Hold it: `UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark SET lock_exec_id = 'cutover-<yyyymmdd>', lock_at = current_timestamp() WHERE watermark_id = 'wm_transform_brz_3rd_crawler_poi_stream' AND lock_exec_id IS NULL`. Re-read the row to confirm. `running_timeout_minutes = 780` covers the window; finish steps 3–10 within it.
3. Deploy `NB_LIB_EXTRACT_RAWDATA`, then `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, then `NB_CREATE_DDL`. Do not deploy any gold change.
4. Config, one cell per write. Do not run the partner seed cell.
   - C1: guarded `ALTER`.
   - C2: 3P seed plus `show_registry`. Expect 9 tables, 52 columns, 0 inactive, and 10 rows with non-NULL `convert_arg`.
   - C3: `DELETE` the policy row.
   - C4: `UPDATE` media `dedup_order`.
5. Partner regression: run the partner extract with `dry_run = True`. Pass means no `ConfigError` and an unchanged table count.
6. 3P dry run with the old tables still present: `dry_run = True, full_reload = True, allow_full_scan = True, max_parallel = 12`. The dry run skips the lock. Pass means:
   - self-check PASS and no `ConfigError`;
   - `cast_null` empty and `mapped_heads_missing` empty;
   - `docs_by_table` = 53 for each `DOC` table;
   - `bad_shape` empty and rejected = 0 (P1).

   Fail → R1.
7. Backup, required for acceptance: `CREATE TABLE lh_vv_silver.dbo.bak_<yyyymmdd>_<tbl> AS SELECT * FROM lh_vv_silver.dbo.<tbl>` for each of the nine tables. Record the row counts.
8. Completeness gate (I12). The query must return 0; otherwise stop and route to user decision:

   ```sql
   WITH b AS (
     SELECT DISTINCT regexp_replace(md5(concat(source_name, source_id)),
            '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5') AS poi_id
     FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
     WHERE lower(trim(source_name)) = 'google'
       AND raw_payload IS NOT NULL AND trim(raw_payload) <> '')
   SELECT count(*) FROM lh_vv_silver.dbo.slv_3p_poi s LEFT ANTI JOIN b ON s.poi_id = b.poi_id;
   ```
9. `DROP TABLE` the nine 3P silver tables, one statement per cell. Then `DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_3p_poi_policy`.
10. Release the manual lock (`… SET lock_exec_id = NULL, lock_at = NULL WHERE watermark_id = 'wm_transform_brz_3rd_crawler_poi_stream' AND lock_exec_id = 'cutover-<yyyymmdd>'`). Immediately run:
    - full init: `full_reload = True, allow_full_scan = True, max_parallel = 12, max_retries = 1`;
    - the same again, for idempotency;
    - one incremental run (`full_reload = False`).
11. Silver acceptance. All counts are recorded in the runbook:
    - All 9 tables SUCCESS. The second full init has `inserted_rows = 0`. The incremental run is `SUCCESS` or `NO_DATA`, with `last_src_version` ≥ baseline.
    - Each `DOC` table has 17 rows, with no duplicate `poi_id`. `review_id` and `media_dedup_key` are unique.
    - Key supersets: `bak review LEFT ANTI JOIN new review ON review_id` = 0, and the same for `media_dedup_key`.
    - Parity on old rows (inner join on key, null-safe `<=>`), 0 differences required for:
      - `slv_3p_poi`: `poi_name`, `poi_name_normalized`, `types_json`, `subcategory_tags_json`, `operating_status`;
      - address: `full_address`, `lat`, `lng`, `plus_code`, `house_number`, `street`, `state_province`, `country_code`, `postal_code`;
      - contact: `website_url`, `google_maps_url`;
      - rating: `rating_overall`, `rating_count`;
      - price: `price_level`, `currency`, `price_min`, `price_max`;
      - opening hours: `periods_json` (text equality), `weekday_text_json`, `open_now`;
      - review: all kept columns;
      - media: `photo_api_uri`, `display_order`.
    - Report only, accepted by decision: the number of `city` and `ward` differences.
    - New-only `DOC` rows (Q3) have NULL in every value column whose source is null.
    - Any unexpected difference → stop. Use R2 or a user decision; never patch silver by hand.
12. Gold stays disabled (I7, UA1). Record the state in the runbook result.
13. Cleanup after the user accepts:
    - `DROP` the `bak_*` tables;
    - `DELETE FROM lh_vv_ctrl.dbo.ctrl_cdc_state WHERE src_tbl = 'brz_3rd_crawler_poi_stream' AND trg_tbl = 'slv_3p_poi_policy'`;
    - mark unresolved 3P rejects of removed tables `is_resolved = true`.

### 13.3 Rollback

- R1, before step 9 (nothing destructive):
  1. Re-run the previous `NB_CREATE_DDL` revision's 3P seed. `convert_arg` stays and is NULL. Delta fills the missing column.
  2. Restore pipeline_config: the old seed's `WHERE NOT EXISTS` re-inserts the policy row; `UPDATE` media `dedup_order` back to `display_order ASC, media_id ASC`.
  3. Redeploy the previous extract notebook. The new lib can stay, because it is backward compatible.
  4. Release the manual lock and re-enable the 15P schedule.
- R2, after step 9:
  1. Keep 15P disabled. Hold the source lock again.
  2. Revert config and code as in R1.
  3. `DROP` the new-shape tables.
  4. Release the lock. Run the old notebook with `full_reload = True, allow_full_scan = True`. It rebuilds the old silver from `normalized_payload` (I8). Compare with `bak_*` row counts.
  5. Re-enable 15P. Gold takes basis `FULL` once (new table ids) in the old format.
- Gold is never rolled back by this task.

### 13.4 Forward recovery and the gold dependency

- Forward recovery follows §8. Do not move the watermark manually.
- Exit from the paused-gold state is a separate gold task that:
  - removes every §5.11 read;
  - accepts the basis-`FULL` append and the value changes;
  - re-enables the 15P schedule.

  Until then gold is stale but intact.

### 13.5 Prod gate (U5)

The prod cutover repeats §13.1–13.4 only after a read-only prod re-run of P1–P5 (same scripts, counts only) shows all of the following:

- P1: zero in-scope `raw_blank`, `not_object`, `invalid_json`, or trailing content. The DEV notes show prod bronze history from before 2026-09-16, so whether those rows have `raw_payload` is not yet known.
- P2: kept paths have one type family each, and every mapped head is present in all documents.
- P3/P4: zero differences on the columns in the step-11 parity list.
- P5: every `priceLevel` token is in the `ENUM_MAP`. Otherwise the user decides its integer before cutover.

Prod also requires the same UA1 decision, or the gold task deployed first.

## 14. Implementation plan (Main)

1. `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb`: §6.1–§6.3 and §6.6. Header change-log.
2. `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`: §6.4, §6.5, §6.7, and the markdown tables.
3. `notebooks/NB_CREATE_DDL.ipynb`:
   - registry `CREATE TABLE` gains `convert_arg`, plus a guarded `ALTER` cell;
   - `REGISTRY_SCHEMA`;
   - `flatten_table_configs` handles `"arg"`;
   - `KNOWN_RULES` gains the six rules;
   - `validate_rows`:
     - `ARG_RULES` require an `"arg"`, other rules forbid one;
     - multi-part only for `MULTI_PART_RULES`;
     - still no inactive key column.
   - `TABLE_CONFIGS_3P` rewritten exactly per §5, with an updated header comment ("9 tables, 52 columns, 0 inactive").
   - 3P pipeline_config seed `VALUES` without policy, and media `dedup_order` `'display_order ASC'`.
   - Separate cells: `UPDATE` media `dedup_order`, `DELETE` the policy pipeline_config row.
   - Add `slv_3p_poi_policy` to the existing deletion cell.
   - Reject DDL comment text.
4. Docs:
   - `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`: §1, §3 "Khối vắng" → Q3, §5 constants, §7 `watch` and the guard, §8 target table, §10.
   - `docs/context/NB_LIB_EXTRACT_RAWDATA.md`: §1 path table, §6 rules and self-check, §8 `ColumnSpec`, §9 validation.
   - `docs/context/CTRL_TABLES_CONTEXT.md`: registry `convert_arg`, 3P table and column counts, pipeline_config 3P rows, reject comment.
   - `docs/context/01_DATA_MODEL.md`: the 3P L1 section.
5. Tests:
   - `tests/test_3p_l1_contract.py`:
     - `EXPECTED` per §5 (9 tables, 52 columns, 0 inactive);
     - `TOP_KEYS` replaced by two checks: path grammar, and "no source key constants in the extract notebook";
     - `FORBIDDEN = {"_lang", "_langs", "_align"}`;
     - amenity columns `{"poi_id", "source_flags_json"}`;
     - the deletion list includes `slv_3p_poi_policy`;
     - `JSON_PICK` keys equal the arg keys.
   - `tests/test_l1_ts_contract.py`:
     - remove the `source_created_at` assertions;
     - `published_at.path == "publishTime"`;
     - the `review_id` path contains `publishTime`.
   - New `tests/test_3p_raw_rules.py`, executing the `BEGIN_RULE_PURE` block:
     - accept and reject cases of `parse_convert_arg`, including quote, space, and `;` tokens, wrong types, bools as ints, unknown keys, and empty lists;
     - SQL text of each builder;
     - the `build_table_specs` matrix (snapshot only, multi-part misuse, `POS_1BASED` outside `*_ARRAY`, `JSON_PICK` outside root `DOC`);
     - partner registry rows still valid with `convert_arg` NULL.
6. `decision.md` (Vietnamese): record the §5.5 `COALESCE` interpretation, the `keep_nulls = false` choice, the `ENUM_MAP` entries, and UA1. `runtime-runbook.md` (Vietnamese): §13.
7. Gold notebooks are not edited. Main updates `task-state.yaml` scope to show they are impact-only.

## 15. Verification strategy

Local:

- `python -m pytest tests` and `python scripts/vv.py verify 20261013-3p-extract-from-raw-payload`.
- Pure tests prove argument validation, SQL builder text, the validation matrix, and partner compatibility.

Runtime in DEV (§13.2):

- self-check;
- partner dry run;
- 3P dry-run gate;
- completeness gate;
- full init;
- idempotent re-run;
- incremental run;
- silver acceptance parity against `bak_*`.

Crash check:

1. Cancel a full init after the wave starts.
2. Re-run the full init.
3. Pass: same final counts, no duplicate keys (`SELECT <key>, COUNT(*) … HAVING COUNT(*) > 1` returns 0 for `poi_id` in each `DOC` table, for `review_id`, and for `media_dedup_key`), and state not regressed.

Guard check: one incremental run against a deliberately missing target in DEV (after `DROP`, before full init) must fail with the recreated-target `ConfigError` and create no table.

Reviewers:

- `sql-data-reviewer`: registry rows, rule SQL, MERGE keys, `dedup_order`, parity queries.
- `spark-runtime-reviewer`: lib and notebook changes, higher-order functions, `try_element_at` and `to_json` options under ANSI on and off, F16 cost (DEV 53 docs; prod about 21k docs, about 200k media rows).
- `state-correctness-reviewer`: cutover timeline, lock window, recreated-target guard, completeness gate, R1/R2.
- `fabric-pipeline-reviewer`: no pipeline JSON change; disabling the 15P schedule; the 35-minute flow lock timeout versus the 780-minute source lock.
- `risk-gate`: I7 / UA1 and the prod gate.

## 16. Evidence status

| Probe | Result | Used for |
|---|---|---|
| P1 | `raw_payload` string; 53 in-scope rows, single object each, no trailing content; `raw_blank = norm_blank = crawled_at_null = raw_id_ne_source_id = 0` | I1; expected rejects = 0; Q2/Q16 in DEV |
| P2 | Types per path. Every mapped head present 53/53. `priceLevel` string or null; `widthPx`/`heightPx` integer; flags boolean or null; options object or null. Top-level counts of keys that are also nested are doubled by the probe (106 = 2 × 53) | Types in §5; `JSON_PICK` kinds; `mapped_heads_missing` as a gate |
| P3 | Equality per column (§5). `city` 20/33, `ward` 17/36. Price `equal_after_trim`. Attribution tokens in source order | Disposition; `ARRAY_PICK` tokens |
| P4 | Review fields and key 265/265; `photo_api_uri` 265/265; `display_order = index + 1`; raw 10 photos and normalized 5 per document; integer dimensions 530/530 | Child keys, media expansion |
| P5 | `priceLevel` → 1 and 2 as normalized; no `close` missing; projection equal under both null settings; normalized key order; `open_now` 48 + 5 | `ENUM_MAP`, `ARRAY_PROJECT` order, `open_now` |
| P6 | 10 gold edges from `slv_3p_poi*`, all in 15P; no `slv_poi*`; policy table absent | §5.11, I7, freeze list |

The 3P extract's external invoker is not listed (P6 step 4). The held source lock covers any invoker, so the design does not depend on that list.

## 17. User acknowledgements required before the DEV runtime step

These do not block implementation or review:

- UA1: accept that `PL_VV_TRANS_SLV_TO_ENR_15P` stays disabled from the freeze until a separate gold task removes the §5.11 reads. Name that task, or choose R2 if gold must resume first.
- UA2 (prod only): approve the §13.5 read-only prod probe re-run as the prod rollout gate.
