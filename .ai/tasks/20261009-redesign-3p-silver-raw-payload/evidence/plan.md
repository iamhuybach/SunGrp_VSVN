# Evidence plan

## Decision to resolve

Architecture may not drop `extra_info.enrichment`, `extra_info.enrichmentSiblings`, or `extra_info.enrichmentFailedLangs`, and may not disable `slv_3p_poi_content`, `slv_3p_poi_price`, `slv_3p_poi_raw_data`, or the 38 flat `poi_amenity` flags, until bronze population counts say those paths are absent or non-null.

The local sample is one bronze-shaped row. Its key tree is in `evidence/sample-key-tree.md`. That file is not a schema contract.

## Existing evidence

| Fact | Scope | Use |
|---|---|---|
| Key tree of `normalized_payload`, including `extra_info` children | 1 document | Input to the comparison. `extra_info` is an object with no children. |
| `enrichment`, `enrichmentSiblings`, `enrichmentFailedLangs` | 1 document | Absent. Not a population result. |
| `poi_content`, `poi_price`, `policies` | 1 document | Key present, JSON null. |
| `raw_data` inside `normalized_payload` | 1 document | Key absent. Bronze column `raw_payload` was not expanded. |
| `poi_amenity` keys | 1 document | Only `amenity_schema` and `ext_attributes`. None of the 38 registry flag names appear. |
| `poi_review` element keys | 1 document | `author_name`, `rating`, `source`, `text`, `time`. One key set. |
| `poi_media[].category` | 1 document | `null` or `string` across elements. |
| Payload `poi_id` versus `HASH_MD5_UUID(source_name, source_id)` | 1 document | Not equal. Payload `source_id` equals the bronze column. Lowercased payload `source` equals bronze `source_name`. |
| `poi_name_normalized` versus `lower(poi_name)` | 1 document | Equal. Not a normalization rule. |
| `poi_address.address_google` versus `full_address` | 1 document | Equal. |
| Root `facilities` versus `poi_amenity.amenity_schema.facilities` | 1 document | Deep-equal. |
| Root `types` versus `subcategory_tags` | 1 document | Deep-equal. |
| `ext_attributes` | 1 document | 38 keys, every value a string. The registry comment still says 62 keys on the old payload. |

No personal data, phone number, review text, media URL, or `raw_payload` body is stored.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `e1_3p_payload_shape.sql` | Fabric DEV, read-only, `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` | Are enrichment paths, null blocks, flat amenity flags, and review/media key gaps population facts? | Save the one aggregate row. Architecture stays blocked until these are interpreted: `has_enrichment`, `has_enrichment_siblings`, `has_enrichment_failed_langs`, `extra_info_nonempty`, `poi_content_nonnull`, `poi_price_nonnull`, `policies_nonnull`, `raw_data_nonnull`, `amenity_flat_flag_docs`, `review_dup_groups`, `review_missing_author_or_time`, `media_dup_groups`, `media_missing_photo_api_uri`. | `evidence/results/e1_3p_payload_shape.txt` |
| `e1b_3p_block_schemas.py` | Same, Spark notebook | What key sets and merged schemas do non-null `extra_info`, `poi_amenity`, `poi_content`, `poi_price`, and `policies` have? | Save stdout. Key lines are names and counts. `SCHEMA` lines are Spark `simpleString` types. Stop if a line contains a payload value. The SQL file is retired: `schema_of_json` rejects a column (`NON_FOLDABLE_INPUT`). | `evidence/results/e1b_3p_block_schemas.txt` |

Interpretation rules after the user returns results:

- Drop LANG paths only when `has_enrichment`, `has_enrichment_siblings`, `has_enrichment_failed_langs`, and `extra_info_nonempty` are all 0.
- If `extra_info_nonempty` > 0, read `e1b` before any L1 design.
- Disable `slv_3p_poi_content`, `slv_3p_poi_price`, or `slv_3p_poi_raw_data` only when that block's non-null count is 0. `slv_3p_poi_policy` is already inactive; keep it inactive when `policies_nonnull` is 0.
- Drop the 38 flat amenity flags only when `amenity_flat_flag_docs` is 0. Do not invent a mapping from `ext_attributes` onto those flags inside extract.
- Keep the current `review_id` / `media_dedup_key` formulas only when the duplicate and missing-part counts are 0. A non-zero count is a key decision, not a guess.

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
- Do not select `normalized_payload`, `raw_payload`, phone fields, review text, author names, or media URLs into the saved result.
