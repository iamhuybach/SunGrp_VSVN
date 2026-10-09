# L1 block comparison

Current seed: `TABLE_CONFIGS_3P` in `notebooks/NB_CREATE_DDL.ipynb`. Extract parameters `lang_object_path = extra_info.enrichment`, `lang_map_path = extra_info.enrichmentSiblings`, `langs = vi,en,ko`.

Labels apply to the one sample document unless the row says the population is already known from the current registry (policy table already inactive).

| L1 table | Current source | This document | Classification | Population still open |
|---|---|---|---|---|
| `slv_3p_poi` | DOC `$` | Root object present | Structural, with enrichment columns inside it | `enrichment_failed_langs_json` path |
| `slv_3p_poi_address` | DOC `poi_address` | Object present. Same field names as the registry, plus `address_google` which the registry dropped | Structural | no path change on this row |
| `slv_3p_poi_contact` | DOC `poi_contact` | Object present. Same keys as the registry | Structural | null keys stay unproven |
| `slv_3p_poi_price` | DOC `poi_price` | Key present, JSON null | Block missing on this row. Do not NULL-overwrite | non-null count |
| `slv_3p_poi_opening_hours` | DOC `poi_opening_hours` | Object present. Adds `open_now`, which the registry does not project | Structural JSON columns still match | whether `open_now` must become a column |
| `slv_3p_poi_policy` | DOC `policies`, inactive | Key present, JSON null | Already off | confirm it stays null |
| `slv_3p_poi_rating` | DOC `poi_rating` | Object present. `rating_breakdown` and `sub_ratings` null | Structural | no path change on this row |
| `slv_3p_poi_amenity` | DOC `poi_amenity` | Only `ext_attributes` and `amenity_schema`. Flat flag names absent | JSON columns are structural. The 38 flags are a projection this document does not carry | flag presence |
| `slv_3p_poi_raw_data` | DOC `raw_data` | Key absent | No source block on this row. Do not switch the table to bronze `raw_payload` | key presence |
| `slv_3p_poi_content` | DOC_ARRAY `poi_content` | Key present, JSON null. Element shape unknown | Block missing on this row | non-null count and element keys |
| `slv_3p_poi_review` | DOC_ARRAY `poi_review` | Array of objects with the five registry fields | Structural. `review_id` stays a MERGE key | duplicate `(author_name, time)` and missing parts |
| `slv_3p_poi_media` | DOC_ARRAY `poi_media` | Array of objects with the registry fields. `category` is null or string | Structural. `media_dedup_key` stays a MERGE key | duplicate `photo_api_uri` and missing parts |
| `slv_3p_poi_enrichment` | LANG `$` via `extra_info.enrichment` and `enrichmentSiblings` | Both paths absent. `extra_info` has no children | Old enrichment product | population absence |
| `slv_3p_poi_review_i18n` | LANG_ARRAY `reviews` aligned to `poi_review` | No localized review array | Old enrichment product | population absence |

## Columns on `slv_3p_poi` that are not plain source fields

| Column | Current path | This document | Note for later architecture |
|---|---|---|---|
| `poi_id` | `HASH_MD5_UUID(_doc.source_name, _doc.source_id)` | Formula inputs exist on the bronze row. Payload `poi_id` is a different string | Keep as the MERGE key. Payload `poi_id` remains `collector_poi_id` if that column stays |
| `available_langs_json` | `_langs` built from enrichment objects plus `language_code` | No enrichment objects. Bronze and payload both have `language_code` | Deriving a language set from enrichment is not structural |
| `enrichment_failed_langs_json` | `extra_info.enrichmentFailedLangs` | Path absent | Old enrichment product |
| `poi_name_normalized` | `poi_name_normalized` | String present. Equals `lower(poi_name)` on this row only | Storing the field is structural. Choosing it as the canonical name is L2 |
| `business_sector`, `business_category`, `subcategory_tags_json`, `facilities_json` | Root fields | Present | Storing them is structural. Mapping sector/category is already L2 (N2) |
| `slug`, `partner_id`, `accommodation_type`, `star_rating`, `awards_json`, `slug_history_json`, `poi_amenity_schema_json` | Root fields | JSON null. Several are already inactive | Null rate still open |

## Extract behaviors to classify in architecture

Not an architecture decision. Inventory for the architect after the probe.

Structural, stays in extract when the path survives the probe:

- Parse `normalized_payload` as a JSON object.
- Explode a present object or array into the matching L1 grain.
- Cast registry types.
- MERGE keys: `poi_id`, `review_id`, `media_dedup_key`.
- Technical columns `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`, `_ingested_at`.
- Absent block: skip the document for that table and keep the stored row.
- Order by `crawled_at`, then `event_id`.
- Reject a non-object payload, a missing `source_name` / `source_id`, or a missing `crawled_at`.

Business, leaves extract:

- `langs = vi,en,ko` and any fallback to another language.
- `lang_object_path` / `lang_map_path`, LANG, and LANG_ARRAY.
- Building `_langs` or `available_langs_json` from enrichment objects.
- Reading `enrichmentFailedLangs`.
- Projecting the 38 amenity flags when those keys are not in the payload. A mapping from `ext_attributes` onto those flags is new business logic.
- Choosing canonical name, description, sector, category, slug, or destination. N2 and N4 already own most of this, but they currently read `slv_3p_poi_enrichment` and `slv_3p_poi_content`.

## L2 edges that read enrichment today

From `docs/context/01_DATA_MODEL.md` section 6. The node notebooks are not in the repository.

| Node | Reads | Decisions that today can come from enrichment |
|---|---|---|
| N2 `slv_poi` | `slv_3p_poi_enrichment` plus `slv_3p_poi` | Sector, category, `poi_type`, `subcategory_tags`, `brand_name`, model candidates |
| N4 `slv_poi_localization` | `slv_3p_poi_content`, `slv_3p_poi_enrichment`, `slv_3p_poi` | Per-language name and description. Fallback name methods stay in L2. Description must not be copied from another language |

N1, N3, and N5 are not listed as readers of the enrichment tables. N3 still reads `slv_3p_poi_address`. N5 still reads N3.
