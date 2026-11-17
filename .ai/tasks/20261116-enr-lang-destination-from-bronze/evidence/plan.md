# Evidence plan

## Decision to resolve

The object keys `text` and `label` are proven (360/360). Still open: `experiences` and `destinations` are arrays, destination elements have `id` and `name`, and `translated_at` parses. Silver grain, watermark, and the `, ` delimiter are recorded in D-3 to D-5.

## Existing evidence

- `evidence/results/probe_brz_enrichment_result.txt`: table present, 13 columns, `event_id` unique (473), LANG unique on `(poi_id, lang)` (360), DESTINATION unique on `poi_id` (113), three timestamp candidates with nulls=0, path non-empty counts. `address.new.district` paths are 0/113.
- `evidence/samples/brz_enrichment_result_lang_destination.tsv`: 4 user-supplied rows. Not `TASK_EVIDENCE` for JSON types.
- `evidence/payload-shape.md`: key tree of those rows, no values.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `probe_brz_enrichment_result.py` | Fabric DEV, read-only Spark on `lh_vv_bronze` | Table, columns, uniqueness, watermark candidates | Done. Result is `evidence/results/probe_brz_enrichment_result.txt`. | `evidence/results/probe_brz_enrichment_result.txt` |
| `probe_json_shape.py` | Fabric DEV, read-only Spark on `lh_vv_bronze` | Are the three `display` objects keyed `text` and `label`? | Done for objects: 360/360 `label,text`. `schema_of_json` failed before arrays. | `evidence/results/probe_json_shape.txt` |
| `probe_json_shape_rest.py` | Fabric DEV, read-only Spark on `lh_vv_bronze` | Arrays and `translated_at` | Done. 360 experience arrays, 113 destination arrays, `translated_at` parse_null=0. One null id/name element. | `evidence/results/probe_json_shape_rest.txt` |
| `probe_arch_gaps.py` | Fabric DEV, read-only Spark on bronze, silver, and gold | P-1 counts and gold Delta protocol; P-3 poi_id overlap; P-4 null versus blank address fields | Done. `slv_ml=3`, `slv_dest=0`, gold 859 live, writer version 2. All bronze poi_id values match entity. Partner entity has 39 blank `house_number` and 39 blank `street`. Destination JSON blanks are 0. | `evidence/results/probe_arch_gaps.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
- Do not print `data`, addresses, or names. Schema and counts only.
