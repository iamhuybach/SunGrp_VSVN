# Evidence plan

## Decision to resolve

D-3. Architecture returned `EVIDENCE_REQUIRED`. Partner `poi_id` is `uuid_md5(id, 'partner')`. The JSON path and match rule for partner amenity attributes are not in the repository. Probes P1, P3, and P4 are ready. P2 is written after P1 names the path.

## Existing evidence

`evidence/results/amenity-poi-id-overlap.txt` (Fabric DEV, 2026-11-18):

| amenity_table | amenity_poi_id | in_gld_srv_poi_info | not_in_gld_srv_poi_info |
|---|---:|---:|---:|
| gld_srv_poi_amenity | 15995 | 0 | 15995 |
| slv_poi_amenity | 15995 | 0 | 15995 |

Sample: 50 `gld_srv_poi_amenity.poi_id` values, no personal data.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `amenity-poi-id-overlap.sql` | Fabric DEV | For live `slv_poi_amenity` and `gld_srv_poi_amenity`, how many distinct `poi_id` values are on live `gld_srv_poi_info`, and how many are not? | Observed. Both tables 15995 / 0 / 15995. | `evidence/results/amenity-poi-id-overlap.txt` |
| `amenity-poi-id-side.sql` | Fabric DEV | Live info `poi_id` by `source_name`, amenity `poi_id` on entity, overlap ignoring `info.deleted_at`. | Observed. Info: partner 294. Amenity on entity: google 15995. On info ignoring `deleted_at`: 0. | `evidence/results/amenity-poi-id-side.txt` |
| `partner-amentities-shape.sql` | Fabric DEV | Which top-level keys does the selected partner `amentities` block have, and what is the schema of keys other than `policies` and `main_category`? | Key counts plus schema strings. No values. | `evidence/results/partner-amentities-shape.txt` |
| `partner-entity-coverage.sql` | Fabric DEV | How many live partner entity rows exist, how many have NULL `business_sector`, and how many `poi_id` values are on live `gld_srv_poi_info`? | Totals plus one row per sector. | `evidence/results/partner-entity-coverage.txt` |
| `partner-dict-keys.sql` | Fabric DEV | How are active partner dictionary rows distributed, are raw keys duplicated, and how many are `other`/`other`? | Three count results. | `evidence/results/partner-dict-keys.txt` |
| `partner-amenity-label-match.sql` | Fabric DEV | For labels under `$.facilities`, how many match active partner dictionary `amenity_raw` exactly and case-insensitively? | Observed. Exact and case-insensitive counts are equal: 36 matched, 80 unmatched. | `evidence/results/partner-amenity-label-match.txt` |
| `partner-amenity-label-column.sql` | Fabric DEV | Do the same string-array labels match `amenity_en`, `amenity_vi`, or `amenity`? | Observed. `hit_amenity` is 0 on every row. `hit_en` and `hit_raw` each cover a different subset. | `evidence/results/partner-amenity-label-column.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
- Sample columns are `amenity_table` and `poi_id` only.
