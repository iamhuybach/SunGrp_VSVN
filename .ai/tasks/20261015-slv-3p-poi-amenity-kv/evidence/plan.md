# Evidence plan

## Decision to resolve

Resolved. The source payload is `source_flags_json`. It stores boolean flags and option objects. The transform groups those flags into key-value rows. The samples are output examples.

## Result

`evidence/results/P01_amenity_json_keys.txt`: `VERDICT FAIL`, `matched_count` 0, 57 rows. The only JSON column is `source_flags_json`. Its top-level keys are `flags`, `accessibilityOptions`, `evChargeOptions`, `fuelOptions`, `parkingOptions`, and `paymentOptions`.

`evidence/results/P02_amenity_enum_groups.txt`: `VERDICT FAIL`, `enum_paths` 0, 57 object rows. Nested values under `flags` and `accessibilityOptions` are bool or null. `evChargeOptions` is null on all 57 rows. Child-key output shows 50 of 70 tokens. The enum scan covered the whole JSON.

## Existing evidence

- `notebooks/NB_CREATE_DDL.ipynb` registry for `slv_3p_poi_amenity`: `poi_id`, `source_flags_json`. `source_flags_json` is `JSON_PICK` of Google boolean flags plus `parkingOptions`, `paymentOptions`, `accessibilityOptions`, `evChargeOptions`, and `fuelOptions`. `tests/test_3p_l1_contract.py` asserts that column set.
- `docs/context/01_DATA_MODEL.md` section 5.2 and `docs/context/CTRL_TABLES_CONTEXT.md` still say `poi_id`, `amenity_schema_json`, `ext_attributes_json`. Those names are not in the current registry seed.
- Bronze `normalized_payload` in `docs/context/01_DATA_MODEL.md` documents `poi_amenity.amenity_schema.facilities` and a root `facilities` object. Their child groups are `main_cuisine`, `specialty_tags`, `space_and_services`, and `additional_amenities`. `terms_and_conditions`, `general_amenities`, `accessibility`, and `safety_and_hygiene` are absent.
- `docs/context/3p-google/get_amenity.md` flattens Google booleans and filters tags with `types` / `primaryType`. `docs/context/3p-google/poi_amenity_mapping.md` maps snake_case Google strings. Neither document shows the sample display tags inside `{enum, item_type, required, type}`.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `P01_amenity_json_keys.py` | Fabric DEV, `lh_vv_silver` | Which string columns exist, and which top-level JSON keys do they contain? | Done. `VERDICT FAIL` for the wrapper names. The only JSON column is `source_flags_json`. | `evidence/results/P01_amenity_json_keys.txt` |
| `P02_amenity_enum_groups.py` | Fabric DEV, `lh_vv_silver` | Which nested objects in `source_flags_json` contain an `enum` key, and what are the child key names under the six top-level keys? | At least one path has `enum`. Zero paths blocks the notebook. | `evidence/results/P02_amenity_enum_groups.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
- Do not store enum values or description text. Store column names, types, key paths, and counts.
