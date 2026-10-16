# Request

## User outcome

`lh_vv_silver.dbo.ref_dictionary_amenities` exists and is seeded from `docs/context/3p-google/mapping_amenities.md`. `lh_vv_silver.dbo.slv_poi_amenity` is a key-value table of the amenities that match `slv_3p_poi_amenity.source_flags_json`. The operator wrote the schema as `slv.`; the silver schema in this repo is `lh_vv_silver.dbo`.

## Scope

### In scope

- DDL for `lh_vv_silver.dbo.ref_dictionary_amenities` with exactly these columns: `source_name` string, `business_sector` string, `amenity_group` string, `amenity_raw` string, `amenity` string, `amenity_vi` string, `is_active` boolean, `updated_at` timestamp. No `business_category` column.
- Seed that dictionary from `docs/context/3p-google/mapping_amenities.md`.
- DDL for `lh_vv_silver.dbo.slv_poi_amenity`. Key is (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). Values are `amenity` and `amenity_vi`. No boolean column and no `business_category` column. Q3 in `decision.md`.
- Rows in `slv_poi_amenity` come from `slv_3p_poi_amenity.source_flags_json`, matched to dictionary rows with `source_name = google`.
- Read `business_sector` from `lh_vv_silver.dbo.slv_poi_entity` by joining on `poi_id`. The dictionary match also requires `business_sector`. This task does not create or change `slv_poi_entity`.

### Out of scope

- Adding `business_category` to either table.
- Renaming `f_n_b`. Q2 corrected only `accomodation` to `accommodation`.
- Creating or changing `lh_vv_silver.dbo.slv_poi_entity`. Another flow owns that table.
- Putting `amenity` into the `slv_poi_amenity` key. Q3 adds only `amenity_raw`.
- Inferring `source_flags_json` from `amenity_schema_json` or `ext_attributes_json`.
- Storing the operator's sample JSON in the repo.
- A commit from Main.

## Acceptance criteria

- `parkingOptions.freeStreetParking = true` is one `source_name = google` dictionary row. `Không có field riêng` produces no dictionary row.
- A `source_flags_json` value with `freeStreetParking: true` produces the matching `slv_poi_amenity` row. `freeParkingLot: false` does not produce the row for a `= true` condition.
- `evChargeOptions: null` produces no row.
- Neither table has a `business_category` column.
- An unmatched flag is skipped. No `other` row is created.

## Constraints

- Seed `business_sector` as `accommodation` for header `accomodation` (Q2). Keep `f_n_b`, `attraction`, and `shopping_n_retail` as written in the headers.
- `slv_poi_amenity.business_sector` comes from `lh_vv_silver.dbo.slv_poi_entity` joined on `poi_id` (Q1). The dictionary join includes `business_sector`.
- A bold table label (`general_amenities`, `accessibility`, `specialty_tags`, `space_and_services`, `facilities_and_services`) is the `amenity_group` for following rows until the next bold label. In section 2.3 the label `facilities_and_services` is repeated and stays one group.
- Partner Portal Enum emits `source_name = partner` and `amenity_raw` = that enum. The real Google column header is `Google Place API Field / Value`, not Place Type. That column emits `source_name = google` and `amenity_raw` = the Google expression.
- Do not emit a row for the values `Bổ sung sau`, `Fallback`, `Không có field`, `Không có field riêng`, or an empty Google cell. Drop only that value. Keep the other value on the same row.
- A Google cell with several conditions joined by `hoặc` becomes several `google` rows with the same `amenity` and `amenity_vi`.
- Hiển thị (VI) maps to `amenity_vi`. Hiển thị (EN) maps to `amenity`.
- `is_active = true`. `updated_at` is the seed write time.
- `amenity_raw` is a condition. It matches when the JSON has that path and the right-hand value. `true` does not match `false` or null. A null object such as `evChargeOptions` produces no row.
- `slv_poi_amenity` key is (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). `amenity_raw` is the condition string. `amenity` and `amenity_vi` are the values. Q3.
- Three sample JSON documents were used only to check paths. They are not copied into the repo.
- Domain: DDL/registry and silver transform. Do not commit.

## Classification rationale

- Complexity: medium. Signals: `design_tradeoffs`, `idempotency`, `transaction_boundaries`. The silver key includes `amenity_raw`, and the silver write has to be rerunnable.
- Risk: medium. New silver tables with a bounded rollback. Q3 puts `amenity_raw` in the key.
- Architecture: required. New table grain and a silver transform that matches JSON conditions to dictionary rows.
- Evidence: not required. `notebooks/NB_CREATE_DDL.ipynb` defines `slv_3p_poi_amenity` columns `poi_id` and `source_flags_json`. The collision count comes from the mapping file plus the match rule, not from an unknown runtime distribution.
- Runtime proof: not required at triage. Architecture has not been written.
- Reviewer routing: `sql-data-reviewer` for DDL, grain, and row uniqueness; `spark-runtime-reviewer` for the Fabric notebook that reads JSON and writes the silver table. No pipeline reviewer. Risk is not high, so no risk gate.
