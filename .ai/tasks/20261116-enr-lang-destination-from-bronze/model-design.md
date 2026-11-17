# Model design: 20261116-enr-lang-destination-from-bronze

## Scope

- Base task: `20261116-enr-lang-destination-from-bronze` (`request.md` `## Verbatim request`).
- Inputs: `requirements-analysis.md` §3 (BR-001 to BR-006) and §5 (platform checks). `ANALYSIS_STATUS` is `USER_DECISION` only because PC-01 fails on `SRC-003` and `SRC-004`. The user accepted that deviation on 2026-11-16 (ledger D-7, `MAPPING.md` `MQ-001`).
- Mapping `MAP-20261116-enr-lang-destination-from-bronze` version 5, sections 3–5 (`SRC-001`–`SRC-004`, `TRG-001`–`TRG-004`, `COL-001`–`COL-036`). BRD version 4, sections 5–6 (`BR-001`–`BR-006`, `DS-001`–`DS-005`).
- Ledger rows D-1 to D-7 in `decision.md` `## Quyết định hiện hành` are the rules this design follows.
- `proposal.md` `## Dòng thay đổi`: Not applicable. No `proposal.md` exists for this task.
- `proposal.md` `## ctrl_cfg_schema_registry`: Not applicable. No `proposal.md` exists. The registry-level facts used here (`src_object`, `json_path`, `convert_rule`, `key_order`) come from Mapping §5 and D-4.
- Out of scope (D-2): `gld_enr_poi_info`, historical `NB_CREATE_DDL` cells, dropping `slv_poi_entity_non_enrich.street`, and `(ood).general-information.md`. `docs/context/api-mapping/practical_info.md` is in scope for the `cost_vnd` → `cost` rename only (D-6). This design does not cover the API.
- This document covers the data model only: entities, grain, keys, columns, and lineage. Ordering, MERGE semantics, watermark handling, idempotency, and rollout belong to the Architect.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_bronze.dbo.brz_enrichment_result` (read only) | bronze | 1 row / `event_id` in the DEV snapshot (`probe_brz_enrichment_result.txt` `UNIQUENESS ALL event_id`: 473/473). This is not a permanent key (`decision.md` history for D-1) | None. Eventstream writes it. Name is `PROPOSED` (`SRC-001`) |
| `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` | silver_l1 (legacy `slv_enr_` prefix kept, D-7) | 1 row / (`poi_id`, `lang`), from rows with `event_type = LANG` only (D-3, `TRG-001`, `BR-001`) | `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` `[PROPOSED]` (`FLOW-012`) |
| `lh_vv_silver.dbo.slv_enr_poi_destination` | silver_l1 (legacy `slv_enr_` prefix kept, D-7) | 1 row / `poi_id`, from rows with `event_type = DESTINATION` only (D-3, `TRG-002`, `BR-002`) | `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` `[PROPOSED]` (`FLOW-012`) |
| `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | gold | 1 row / (`poi_id`, `lang`) (`TRG-003`, `mapping_gld_srv_poi_multi_lang.md` §1.1) | `NB_GLD_SRV_POI_MULTI_LANG` (`FLOW-005`) |
| `lh_vv_gold.dbo.gld_srv_poi_info` | gold | 1 row / `poi_id` (`TRG-004`) | `NB_GLD_SRV_POI_INFO` (`FLOW-010`) |
| `apps.srv_poi_multi_lang` (PostgreSQL) | serving | 1 row / (`poi_id`, `lang`) (`sql/postgres/gld_srv_serve.pg.sql` `PRIMARY KEY (poi_id, lang)`) | None. The files read for this design do not name the gold → PostgreSQL sync step. There is no Mapping row for this table (D-6, `TRG-005` dropped) |

## Keys

| table | primary key | business key | foreign / join keys | `poi_id` source |
|---|---|---|---|---|
| `brz_enrichment_result` | None (bronze, append only). `event_id` is unique in the snapshot only | `event_type` routes rows. LANG rows are unique by (`poi_id`, `lang`) and by (`poi_id`, `lang`, `version`). DESTINATION rows are unique by `poi_id` and by (`poi_id`, `version`) (`probe_brz_enrichment_result.txt` UNIQUENESS, snapshot only) | None | Carried by the event (`SCHEMA`: `poi_id string`) |
| `slv_enr_poi_info_multi_lang` | (`poi_id` `key_order` 1, `lang` `key_order` 2) (`COL-001`, `COL-003`, D-3) | Same as the primary key. `version` is not part of the key (D-3) | `poi_id` → `slv_poi_entity_non_enrich.poi_id`, used as a logical LEFT JOIN by gold P1 (`mapping_gld_srv_poi_multi_lang.md` §1.1). No physical FK | Copied 1-1 from bronze `_doc.poi_id` (`COL-001`; `requirements-analysis.md` §4 and PC-06). No identifier formula is applied in this task |
| `slv_enr_poi_destination` | `poi_id` `key_order` 1 (`COL-010`, D-3) | `poi_id`. `version` is not part of the key (D-3) | `poi_id` → `slv_poi_entity_non_enrich.poi_id`, used as a logical LEFT JOIN by `gld_srv_poi_info`. No physical FK | Copied 1-1 from bronze `_doc.poi_id` (`COL-010`; PC-06) |
| `gld_srv_poi_multi_lang` | (`poi_id`, `lang`), both `STRING NOT NULL` (`TABLE_SPECS`) | Same as the primary key | P1 `poi_id` and `lang` come from `slv_enr_poi_info_multi_lang`. The P2 key is unchanged by this task | P1: 1-1 from silver. P2: `uuid_md5(business_service_id, 'partner')` (`mapping_gld_srv_poi_multi_lang.md` §1.2, `AGENTS.md` §7). Not changed |
| `gld_srv_poi_info` | `poi_id` `STRING NOT NULL` (`TABLE_SPECS`) | `poi_id` | `slv_poi_entity_non_enrich.poi_id` = `slv_enr_poi_destination.poi_id` | From `slv_poi_entity_non_enrich` (`SRC-002` `pk=("poi_id",)`). Not changed |
| `apps.srv_poi_multi_lang` | (`poi_id`, `lang`) `text NOT NULL` (`gld_srv_serve.pg.sql`) | Same as the primary key | Mirrors `gld_srv_poi_multi_lang` (`AGENTS.md` §7) | From gold. Not changed |

PC-06 holds: `lang` is a separate key column, `poi_id` never contains language, and no table uses `poi_uid`.

## Columns

Only affected columns are listed. `json_path` values are copied from Mapping §5. For every silver L1 row, `src_object` is `$` and `load_mode` is `DOC` (D-4, `FLOW-011`).

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_enr_poi_info_multi_lang` | (row filter) | — | — | `brz_enrichment_result.event_type` | Only `event_type = LANG` (`BR-001`, `COL-001` note, D-3) |
| `slv_enr_poi_info_multi_lang` | `poi_id` | STRING | NOT NULL (`TABLE_SPECS`) | `_doc.poi_id` | `NONE`, key 1 (`COL-001`, D-3, D-4) |
| `slv_enr_poi_info_multi_lang` | `lang` | STRING | `TABLE_SPECS` leaves it nullable, but it is a key column. See Q-4 | `_doc.lang` | `NONE`, key 2 (`COL-003`, D-3, D-4) |
| `slv_enr_poi_info_multi_lang` | `source_name` | STRING | yes (`TABLE_SPECS`) | `_doc.source` | `NONE` (`COL-002`, D-4). Existing column. It had no writer before this task |
| `slv_enr_poi_info_multi_lang` | `cost` (renamed from `cost_vnd`) | STRING | yes (`TABLE_SPECS` `cost_vnd`) | `data.display.cost` | `NONE`. Rename (`BR-004`, `COL-004`, D-6). Stored as the JSON object string `{text, label}` (`BR-001`; `probe_json_shape.txt`: `label,text` in 360/360 rows) |
| `slv_enr_poi_info_multi_lang` | `best_time` | STRING | yes (`TABLE_SPECS`) | `data.display.best_time` | `NONE`. JSON object string (`COL-005`, `BR-001`) |
| `slv_enr_poi_info_multi_lang` | `time_to_spend` | STRING | yes (`TABLE_SPECS`) | `data.display.time_to_spend` | `NONE`. JSON object string (`COL-006`, `BR-001`) |
| `slv_enr_poi_info_multi_lang` | `description` | STRING | yes (`TABLE_SPECS`) | `data.description` | `NONE` (`COL-007`) |
| `slv_enr_poi_info_multi_lang` | `experience` | STRING | yes (`TABLE_SPECS`) | `data.experiences` | `NONE`. Written to the existing `experience` column. No new `experiences` column (`COL-008`, D-6, `mapping_gld_srv_poi_multi_lang.md` §2). See Q-2 for how the array is serialized |
| `slv_enr_poi_info_multi_lang` | `translated_at` (new) | TIMESTAMP | not stated. See Q-5 | `data.translated_at` | `ISO_UTC_TS` (`COL-009`, D-4). `parse_null` = 0 on 360 rows (D-1) |
| `slv_enr_poi_destination` | (row filter) | — | — | `brz_enrichment_result.event_type` | Only `event_type = DESTINATION` (`BR-002`, `COL-010` note, D-3) |
| `slv_enr_poi_destination` | `poi_id` | STRING | NOT NULL (`TABLE_SPECS`) | `_doc.poi_id` | `NONE`, key 1 (`COL-010`, D-3) |
| `slv_enr_poi_destination` | `source_name` (new) | STRING | not stated. See Q-5 | `_doc.source` | `NONE` (`COL-011`, D-6) |
| `slv_enr_poi_destination` | `ward` | STRING | yes (`TABLE_SPECS`; nonempty 93/113) | `data.address.new.ward.name` | `NONE` (`COL-012`) |
| `slv_enr_poi_destination` | `ward_with_type` (new) | STRING | yes (nonempty 93/113) | `data.address.new.ward.name_with_type` | `NONE` (`COL-013`, D-6) |
| `slv_enr_poi_destination` | `district` | STRING | yes (`TABLE_SPECS`; nonempty 0/113) | `data.address.new.district.name` | `NONE` (`COL-014`) |
| `slv_enr_poi_destination` | `district_with_type` (new) | STRING | yes (nonempty 0/113) | `data.address.new.district.name_with_type` | `NONE` (`COL-015`, D-6) |
| `slv_enr_poi_destination` | `city` | STRING | yes (`TABLE_SPECS`; nonempty 112/113) | `data.address.new.province.name` | `NONE` (`COL-016`) |
| `slv_enr_poi_destination` | `city_with_type` (new) | STRING | yes (nonempty 112/113) | `data.address.new.province.name_with_type` | `NONE` (`COL-017`, D-6) |
| `slv_enr_poi_destination` | `formatted_address` (new) | STRING | yes (nonempty 112/113) | `data.address.new.formatted_address` | `NONE` (`COL-018`, D-6) |
| `slv_enr_poi_destination` | `old_ward` (new) | STRING | yes (nonempty 111/113) | `data.address.old.ward.name` | `NONE` (`COL-019`, D-6) |
| `slv_enr_poi_destination` | `old_ward_with_type` (new) | STRING | yes (nonempty 111/113) | `data.address.old.ward.name_with_type` | `NONE` (`COL-020`, D-6) |
| `slv_enr_poi_destination` | `old_district` (new) | STRING | yes (nonempty 111/113) | `data.address.old.district.name` | `NONE` (`COL-021`, D-6) |
| `slv_enr_poi_destination` | `old_district_with_type` (new) | STRING | yes (nonempty 111/113) | `data.address.old.district.name_with_type` | `NONE` (`COL-022`, D-6) |
| `slv_enr_poi_destination` | `old_city` (new) | STRING | yes (nonempty 112/113) | `data.address.old.province.name` | `NONE` (`COL-023`, D-6) |
| `slv_enr_poi_destination` | `old_city_with_type` (new) | STRING | yes (nonempty 112/113) | `data.address.old.province.name_with_type` | `NONE` (`COL-024`, D-6) |
| `slv_enr_poi_destination` | `old_formatted_address` (new) | STRING | yes (nonempty 112/113) | `data.address.old.formatted_address` | `NONE` (`COL-025`, D-6) |
| `slv_enr_poi_destination` | `lat` | DOUBLE | yes (`TABLE_SPECS`; nonempty 112/113) | `data.lat` | `NONE` (`COL-026`, D-4) |
| `slv_enr_poi_destination` | `lng` | DOUBLE | yes (`TABLE_SPECS`; nonempty 112/113) | `data.lng` | `NONE` (`COL-027`, D-4) |
| `slv_enr_poi_destination` | `full_address` | STRING | yes (`TABLE_SPECS`; nonempty 113/113) | `data.request.address` | `NONE`. This is the silver value. The gold formula is separate (`COL-028`) |
| `slv_enr_poi_destination` | `destination` (new) | STRING | not stated. See Q-5 | `data.destinations` | `NONE`. JSON string of the whole array (`COL-029`, D-6) |
| `slv_enr_poi_destination` | `destination_id` | STRING | yes (`TABLE_SPECS`) | `data.destinations.id` | `NONE`. Element order is kept, including the null element (`COL-030`, D-1). See Q-1 for the serialization |
| `slv_enr_poi_destination` | `destination_name` | STRING | yes (`TABLE_SPECS`) | `data.destinations.name` | `NONE`. Same element order as `destination_id`, including the null element (`COL-031`, D-1). See Q-1 |
| `slv_enr_poi_destination` | `country_code` | STRING | yes (`TABLE_SPECS`) | none (constant NULL) | Always NULL. Not read from JSON (`COL-032`, D-4). See Q-6 |
| `slv_enr_poi_destination` | `postal_code` | STRING | yes (`TABLE_SPECS`) | none (constant NULL) | Always NULL. Not read from JSON (`COL-033`, D-4). See Q-6 |
| `slv_enr_poi_destination` | `street` (dropped) | STRING (current) | — | — | Removed from the table (`TRG-002` note, `BR-002`, request "Đổi cột"). See Q-8 |
| `gld_srv_poi_multi_lang` | `cost` (renamed from `cost_vnd`) | STRING | yes (`TABLE_SPECS`) | P1: `slv_enr_poi_info_multi_lang.cost`. P2: none | P1 copies 1-1. P2 is NULL (`COL-034`, `BR-003`, D-6) |
| `gld_srv_poi_info` | `street` | STRING | yes (`TABLE_SPECS`) | `slv_poi_entity_non_enrich.street` | 1-1 by `poi_id` (`COL-035`, `BR-005`, `mapping_gld_srv_poi_info.md` §1.6). See Q-7 |
| `gld_srv_poi_info` | `full_address` | STRING | yes (`TABLE_SPECS`) | `slv_poi_entity_non_enrich.house_number`, `.street`; `slv_enr_poi_destination.formatted_address`, `.ward_with_type`, `.city_with_type`, `.full_address` | First group that has no null field wins. Fields are joined with `, ` and `concat_ws` is not used. Group 1: `house_number`, `street`, `formatted_address`. Group 2: `house_number`, `street`, `ward_with_type`, `city_with_type`. Group 3: destination `full_address` (`COL-036`, `BR-006`, D-5, §1.6). See Q-3 and Q-7 |
| `apps.srv_poi_multi_lang` | `cost` (renamed from `cost_vnd`) | text | yes (current DDL) | `gld_srv_poi_multi_lang.cost` | Rename only. Type stays `text` (D-6, `BR-003`). The API reads `cost`. No new API column |

Unchanged technical columns: both silver tables keep `created_at` and `updated_at` TIMESTAMP (`TABLE_SPECS`). Both gold tables keep `row_hash`, `created_at`, `updated_at`, and `deleted_at`.

## Lineage

| target | bronze reads | silver reads | gold reads |
|---|---|---|---|
| `slv_enr_poi_info_multi_lang` | `brz_enrichment_result` with `event_type = LANG`. Root columns: `poi_id`, `source`, `lang`. JSON column: `data`. `version` and `EventProcessedUtcTime` drive the latest-row rule (D-3, D-4) | None | None |
| `slv_enr_poi_destination` | `brz_enrichment_result` with `event_type = DESTINATION`. Root columns: `poi_id`, `source`. JSON column: `data`. `version` and `EventProcessedUtcTime` as above (D-3, D-4) | None | None |
| `gld_srv_poi_multi_lang` | None | `slv_enr_poi_info_multi_lang` (`cost` and the existing P1 columns), `slv_poi_entity_non_enrich`, `slv_pn_business_service_i18ns` (unchanged edges, `mapping_gld_srv_poi_multi_lang.md` §1.1) | None |
| `gld_srv_poi_info` | None | `slv_poi_entity_non_enrich` (`street`, `house_number`, plus existing columns), `slv_enr_poi_destination` (`formatted_address`, `ward_with_type`, `city_with_type`, `full_address`, plus existing 1-1 columns), and the other existing silver inputs, which do not change | None |
| `apps.srv_poi_multi_lang` | None | None | Mirrors `gld_srv_poi_multi_lang` (`AGENTS.md` §7). This is a PostgreSQL serving copy, not a gold node |

Gold never reads gold (PC-05). Silver L1 rows carry no business rule. The `event_type` routing and the array projections only shape the payload (PC-04).

## Conflicts and questions

1. **`destination_id` and `destination_name` serialization (unknown).** Both columns are STRING (`TABLE_SPECS`, `COL-030`, `COL-031`), but the source is an array projection of `data.destinations.id` and `.name`. No read file says how the array is stored in one STRING: as a JSON array string, as delimited text, or another way. It also does not say how the one null element is written so order is kept (D-1). `requirements-analysis.md` PC-08 also notes that `02_NAMING_CONVENTION.md` §6 does not define how an `a.b` path projects an array. Which representation should be used?
2. **`experience` serialization (unknown).** `COL-008` and D-6 write the array `data.experiences` to `experience` STRING. Unlike `destination` (D-6), no source says it is the JSON string of the whole array. The acceptance criterion "experiences … stay arrays" suggests that. Please confirm that `experience` stores the JSON array string unchanged.
3. **`full_address` null versus empty (unknown).** D-5 skips a group when a field is null. The probes count "nonempty", which suggests empty strings exist or are possible. Should an empty or whitespace-only field also skip the group? And when all three groups are skipped, is gold `full_address` NULL? Neither case is stated.
4. **`lang` nullability.** `lang` is key 2 of `slv_enr_poi_info_multi_lang` (D-3, `COL-003`), but `TABLE_SPECS` declares it `STRING` without `NOT NULL`. `mapping_gld_srv_poi_multi_lang.md` §1.1 says the gold `quality_gate` blocks null keys. Should the silver DDL change `lang` to `NOT NULL` in this task?
5. **Nullability of new columns.** `translated_at`, `source_name` on `slv_enr_poi_destination`, and `destination` are non-null in every snapshot row, but no file states whether they are nullable. The existing silver columns in `TABLE_SPECS` are nullable. Should all new columns be nullable?
6. **Constant-NULL configuration.** `COL-032` and `COL-033` use the path `null`, and `02_NAMING_CONVENTION.md` §6 has no constant-NULL form (PC-08). The column model is decided: STRING, always NULL. How this maps to registry configuration is left to the Architect.
7. **Partner branch in `gld_srv_poi_info` (possible conflict).** `mapping_gld_srv_poi_info.md` §1.1 (D-SRV-22) takes `full_address` and `street` from `slv_poi_entity_non_enrich` for partner rows without a destination row. §1.6 states the new `street` source and the three-group `full_address` formula, but does not say whether the formula replaces that branch. For a partner without a destination row, groups 1–3 can only use entity fields, so group 3 is always null. Does the three-group rule apply to every row, replacing the partner-branch value of `full_address`?
8. **Out-of-scope reader of the changed silver columns (conflict).** `NB_SETUP_INITIAL_DDL.ipynb` pipeline configuration has edges from `slv_enr_poi_info_multi_lang` and `slv_enr_poi_destination` to `gld_enr_poi_info` (`NB_ENR_POI_INFO`). D-2 puts `gld_enr_poi_info` out of scope. If that notebook reads `cost_vnd` or `street` from these tables, the rename and drop break it. This design did not read that notebook. The request says to record it as a ledger gap, not to change it here. Main should confirm whether it reads either column.
9. **Persisting `version` and `EventProcessedUtcTime` (unknown).** D-3 keeps the row with the higher `version`, then the higher `EventProcessedUtcTime`. Neither silver `TABLE_SPECS` entry has a column for these values, and no Mapping row adds one. Whether the silver tables need stored columns for them, and what those columns are named, is not stated. The Architect owns the ordering design. This model adds no column until that is decided.
10. **Registry `json_path` form for `data` fields (unknown).** Mapping §5 writes `data.display.cost` with `src_object` `$`, root columns as `_doc.<column>`, and bronze `data` typed `string` (`SCHEMA`). The probes address the same fields as `$.display.cost` inside the parsed `data`. This design cites the Mapping paths unchanged. Main or the Architect should confirm the exact registry string form.
11. **PC-01 (recorded, not reopened).** `slv_enr_` is not a silver L1 prefix. The user accepted the deviation on `SRC-003` and `SRC-004` and kept both names (D-7, `MQ-001`). The design uses the existing names.
