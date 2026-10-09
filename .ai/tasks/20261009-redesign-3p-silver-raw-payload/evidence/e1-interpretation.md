# E1 interpretation

Source: full scan of `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` on Fabric DEV. The probe has no row filter. The table currently contains 33 documents, all JSON objects. This is the whole current bronze table, not a sample of the historical 21,168-document load.

## Aggregate

| Column | Value |
|---|---|
| docs | 33 |
| payload_blank | 0 |
| payload_not_object | 0 |
| extra_info_sql_null | 0 |
| extra_info_empty_object | 33 |
| extra_info_nonempty | 0 |
| has_enrichment | 0 |
| has_enrichment_siblings | 0 |
| has_enrichment_failed_langs | 0 |
| poi_content_nonnull | 0 |
| poi_content_array | 0 |
| poi_content_object | 0 |
| poi_price_nonnull | 0 |
| poi_price_object | 0 |
| policies_nonnull | 0 |
| raw_data_nonnull | 0 |
| poi_review_nonnull | 33 |
| poi_review_array | 33 |
| poi_media_nonnull | 33 |
| poi_media_array | 33 |
| amenity_flat_flag_docs | 0 |
| review_elements | 165 |
| review_missing_author_or_time | 0 |
| review_dup_groups | 0 |
| media_elements | 165 |
| media_missing_photo_api_uri | 0 |
| media_dup_groups | 0 |

## Block schemas

`extra_info` is an empty object on all 33 documents (`struct<>`, key set empty). `poi_amenity` is an object on all 33 documents with exactly two keys: `amenity_schema` and `ext_attributes`. `poi_content`, `poi_price`, and `policies` have no object or array value.

The `ext_attributes` field list in the merged schema is a union across rows. A name in that list appears at least once. It is not proof that every document has every nested key. L1 stores the object as one JSON column, so per-row key gaps stay inside that column.

## Locked decisions

- Remove LANG paths. `has_enrichment`, `has_enrichment_siblings`, `has_enrichment_failed_langs`, and `extra_info_nonempty` are 0.
- Deactivate `slv_3p_poi_enrichment`, `slv_3p_poi_review_i18n`, `slv_3p_poi_content`, `slv_3p_poi_price`, and `slv_3p_poi_raw_data`. Keep `slv_3p_poi_policy` inactive.
- Drop the 38 flat amenity flags. `amenity_flat_flag_docs` is 0. Do not map `ext_attributes` onto those flags in extract.
- Keep `review_id` (`HASH_SHA256` of `source_name`, `source_id`, `author_name`, `time`) and `media_dedup_key` (`HASH_SHA256_PIPE` of `source_name`, `source_id`, `photo_api_uri`). Duplicate groups and missing key parts are 0.
- No new L1 table. `poi_amenity` stays one document row. Arrays and nested objects stay JSON columns. Scalars stay typed columns at the same path.

## Not claimed

- These 33 rows do not describe silver rows loaded from the older enriched payload.
- A later crawl can add a key. A new top-level block is a registry change, not a guessed column.
