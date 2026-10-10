# 3P sample shapes

One local bronze row from `C:\Users\bachnh\Downloads\data_sample.json`. The prompt text did not embed a second file. This document matches the bronze columns already described in `docs/context/01_DATA_MODEL.md`. It is not a schema contract.

Not copied: phone numbers, review text, media URLs, `raw_payload`, place id, event id.

## Bronze columns

| Column | JSON type | Shape on this row |
|---|---|---|
| `crawled_at` | string | `yyyy-MM-dd'T'HH:mm:ss` + 9 fractional digits + `Z` |
| `ingested_date` | string | `yyyy-MM-dd` |
| `normalized_payload` | string | JSON object |
| `language_code` | string | `vi` |
| `source_name` | string | `google` |

Example instants from this row, already UTC:

- `crawled_at` = `2026-10-08T08:25:03.721627688Z`
- `normalized_payload.created_at` = `2026-10-08T08:25:03.721621239Z`
- `normalized_payload.poi_review[].time` = `2026-05-08T09:40:17.010285725Z`
- `ingested_date` = `2026-10-08`

`raw_payload` length on this row is 25056 characters. It was not expanded.

## Payload keys observed

Top-level keys: `accommodation_type`, `awards`, `business_category`, `business_sector`, `country_code`, `created_at`, `extra_info`, `facilities`, `language_code`, `operating_status`, `partner_id`, `poi_address`, `poi_amenity`, `poi_amenity_schema`, `poi_contact`, `poi_content`, `poi_id`, `poi_media`, `poi_name`, `poi_name_normalized`, `poi_opening_hours`, `poi_price`, `poi_rating`, `poi_review`, `policies`, `price_level`, `slug`, `slug_history`, `source`, `source_id`, `star_rating`, `subcategory_tags`, `types`.

Timestamp-like strings found by a shape walk: `created_at` and `poi_review[].time` only. No numeric epoch with 10 or more digits appeared under a timestamp path. Latitude and longitude are numbers and are not timestamps.

Array sizes on this row: `subcategory_tags` 9, `types` 9, `poi_media` 5, `poi_review` 5, `poi_opening_hours.periods` 7, `weekday_text` 7, `secondary_hours` 1.
