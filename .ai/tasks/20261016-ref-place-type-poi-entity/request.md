# Request

## User outcome

Silver has a shared place-type dictionary `lh_vv_silver.dbo.ref_dictionary_place_type`, seeded from `docs/context/3p-google/mapping_place_type.md`, and a Google-only POI entity `lh_vv_silver.dbo.slv_poi_entity` that keeps every column of `lh_vv_silver.dbo.slv_3p_poi` and adds `business_sector`, `business_category`, and `business_category_vi` resolved from that dictionary.

The user wrote schema `slv.`. The silver schema in this repo is `lh_vv_silver.dbo`. Keep the table names.

## Scope

### In scope

- DDL for `lh_vv_silver.dbo.ref_dictionary_place_type` with columns: `source_name` string, `place_type` string, `business_sector` string, `business_category` string, `business_category_vi` string, `is_active` boolean, `updated_at` timestamp.
- One seed of that dictionary from `docs/context/3p-google/mapping_place_type.md`.
- DDL and build of `lh_vv_silver.dbo.slv_poi_entity` for Google only: all columns of `slv_3p_poi`, plus the three category columns resolved by the rules below.

### Out of scope

- Sectors other than the seven normalized values.
- Filling `business_category_vi` on the unmatched entity branch.
- Partner rows in `slv_poi_entity`.
- Commit, merge, or a Fabric DEV run during triage.

## Acceptance criteria

- Each Google place type has one row with `source_name = google`. No row has `place_type` equal to `Fallback`, `Không có`, or `Partner Portal bổ sung` (either casing of the Partner Portal label).
- `extended_stay_hotel` has a `google` row and no `partner` row.
- No two rows share `(source_name, place_type)`.
- `slv_poi_entity` includes every column of `slv_3p_poi`.
- When `primary_type` matches a `google` `place_type`, the three category columns come from that row and `types_json` does not change them.
- When `primary_type` does not match, the first matching element of `types_json`, in array order, supplies the three category columns and later elements are ignored.
- When neither matches, `business_sector = other` and `business_category = other`. `business_category_vi` stays unset on that branch.

## Constraints

- Dictionary seed:
  - `business_sector` comes from the section header, normalized only as: `1.1 Accomodation` → `accommodation`; `1.2 F&B` → `fnb`; `1.3 Spa & Wellness` → `spa_n_wellness`; `1.4 Shopping & Retail` → `shopping_n_retail`; `1.5 Attraction` → `attraction`; `1.6 Vehicle Rental` → `vehicle_rental`; `1.7 Public POI & Infrastructure` → `other`.
  - Partner Portal Enum emits `source_name = partner`. Google Place API – Place Type emits `source_name = google`. The two columns are separate rows that share that row's `business_category` and `business_category_vi`.
  - `place_type` is one cell value. A Google cell with comma-separated types becomes one row per type.
  - Do not emit a row for exactly these values: `Partner Portal bổ sung`, `Partner Portal Bổ sung`, `Fallback`, `Không có`. Dropping one of those values does not drop the other column on the same row. A Google type on a "Partner Portal bổ sung" row still emits a `google` row.
  - Hiển thị (VI) → `business_category_vi`. Hiển thị (EN) → `business_category`.
  - `is_active = true`. `updated_at` is the seed write time, one timestamp for the whole seed.
- Entity resolution uses only `source_name = google`. Match `slv_3p_poi.primary_type` first. On miss, scan `slv_3p_poi.types_json` in array order and stop at the first match.
- If `slv_3p_poi` lacked `primary_type` or `types_json`, stop and name the missing column. Both columns are present; see Evidence.
- Do not invent a Vietnamese label for the unmatched entity branch.

## Classification rationale

- Complexity: `medium`. Signals: `design_tradeoffs`, `idempotency`. The dictionary grain and the entity category resolution are specified, but `ref_dictionary_place_type` sits beside existing `ref_business_category`, and `slv_poi_entity` sits beside L2 `slv_poi` (N2), which already resolves sector and category. Seed uniqueness on `(source_name, place_type)` and first-match category resolution must stay deterministic on rerun.
- Risk: `medium`. New silver tables and a bounded mapping. No change to CDC, watermark, or lock behavior. Rollback is to stop reading the new tables.
- Architecture: required. New table grain and key, silver L2 mapping, and a placement trade-off against `ref_business_category` and `slv_poi`.
- Evidence: not required. `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` (note dated 14/10: 9 tables, 55 columns, 0 inactive) maps active `slv_3p_poi` columns `types_json` (`types`) and `primary_type` (`primaryType`). Neither uses `_off`. Registry business columns on that table: `poi_id`, `source_name`, `source_id`, `language_code`, `poi_name`, `poi_name_normalized`, `types_json`, `subcategory_tags_json`, `operating_status`, `primary_type`. `docs/context/01_DATA_MODEL.md` §5.2 also names L1 technical columns `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`, `created_at`, `updated_at`. Architecture must take the full physical column set of `slv_3p_poi` from that DDL contract.
- Runtime proof: not required for classification. Seed rows and match order are deterministic from the mapping file and the rules above. Local checks can prove them. A Fabric apply, if the design needs one, is a later runbook.
- Reviewer routing: `sql-data-reviewer` (DDL, types, grain, unique key, category lookup); `spark-runtime-reviewer` (silver notebook or `NB_LIB_*` transform that builds `slv_poi_entity`); `state-correctness-reviewer` (idempotent seed and deterministic entity rebuild). No pipeline reviewer: no pipeline change is in scope.
