# Evidence plan

## Decision to resolve

Whether stored `gld_srv_poi_info.destination_id` values on rows the pipeline owns (`load_origin` null or not `LEGACY_INIT`) are JSON array strings. D-04 keeps the DDL type `STRING` only when that shape is what those rows contain, and the writer plus DDL do not already use an array type.

Repo code, not a stored sample: `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` `part_value` applies `to_json` to the `destinations.id` array, and `NB_GLD_SRV_POI_INFO` copies `slv_enr_poi_destination.destination_id` 1-1 into a `STRING` column (`docs/context/mapping_gld_srv_poi_info.md` §1.2). That code is not the shape of rows already written.

## Existing evidence

- DDL contracts in `NB_CREATE_DDL` declare `destination_id` as `STRING`.
- 2026-11-25 Fabric DEV, `evidence/results/destination_id_non_legacy_shape.txt`: column type `string` nullable. `load_origin` `LEGACY_INIT` = 25921, null = 19909. Non-legacy shapes: `json_array_string` 19797, `null` 110, `json_array_empty` 2, `bad` 0. Verdict `keep_string`. D-04 keeps `STRING`.
- 2026-11-25 first `poi_name_null_hash` run did not compare hashes. `spark.conf.get(..., "<unset>")` raised `IllegalArgumentException` because `spark.sql.jsonGenerator.ignoreNullFields` must be boolean. The probe now treats a missing value as `unset` and still prints the JSON and hashes.
- 2026-11-25 Fabric DEV, `evidence/results/poi_name_null_hash.txt`: `ignoreNullFields=true`. Synthetic `old_json` equals `new_json`. Both hashes `a7311a3212e88b45fa680b08be8e0688fc94644fc6730d0a72dc3e0553f45130`. Verdict `null_poi_name_hash_unchanged`. GATE-001 fixed. No code change.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `destination_id_non_legacy_shape.py` | Fabric DEV, workspace `sgr_visitvn_dev` | Column type, and shape counts of `destination_id` where `load_origin` is null or not `LEGACY_INIT` | Pass for keeping STRING: column type is `string`, and every non-null shape is `json_array_string`, `json_array_null_elem` (JSON array of strings and JSON nulls), or `json_array_empty`. `not_json`, `blank`, `json_not_array`, or `json_array_other` stops at `user_decision`. All three JSON-array counts at 0 means the populated shape is still unobserved. | `evidence/results/destination_id_non_legacy_shape.txt` |
| `poi_name_null_hash.py` | Fabric DEV, workspace `sgr_visitvn_dev` | Whether `to_json` drops a null `poi_name` so `sha2` stays equal to the struct without that field (GATE-001) | Pass: `old_json` equals `new_json` and `old_hash` equals `new_hash`, and the cell prints `verdict null_poi_name_hash_unchanged`. AssertionError means the null field changes the hash. | `evidence/results/poi_name_null_hash.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Counts only. Do not print `destination_id` values or UUIDs.
- At most 50 output lines. No personal data, secrets, or production extracts.
