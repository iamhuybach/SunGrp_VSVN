# E1 and E2 interpretation

Results read from `evidence/results/e1_partner_timestamp_shapes.txt` and `e2_3p_timestamp_shapes.txt`. Magnitudes below are the observed min/max, not a unit guessed from the column name.

## E2, third party

User confirmed this flow is settled.

| Field | Observed class | Consequence |
|---|---|---|
| `crawled_at` | `iso_utc_z`, fractional length 9, 53 values | Format-normalize only. Not an epoch. |
| `payload_created_at` | `iso_utc_z`, fractional length 9, 53 values | Same. This is `slv_3p_poi.source_created_at`. |
| `review_time` | `iso_utc_z` only, fractional lengths 3 (1), 6 (26), and 9 (238) | Same instant class. Fractional length is not uniform. Normalization to 3 digits is format, not a unit change. |
| `ingested_date` | `iso_date`, 53 values `YYYY-MM-DD` | Stays a date. Do not add a time of day. |

`review.time` remains the raw `review_id` input. `published_at` is the formatted twin.

## E1, partner integers

Non-zero integers fall in one unit per column.

| Unit | Columns with at least one non-zero value | Observed range |
|---|---|---|
| `EPOCH_S_TS` (10 digits, about 1.76e9–1.82e9) | `created_at`, `updated_at`, or `last_updated_at` on `products`, `product_translations`, `product_attributes`, `product_attribute_translations`, `product_attribute_values`, `product_variants`, `product_variant_translations`, `product_business_service_relation`, `product_posts`, `partners`, `business_services`, `business_service_i18ns`, `business_service_poi_link`, `hotel_room_types`, `hotel_rate_plans`; also `business_services.last_in_activated_at`; `hotel_rate_plans.valid_from`, `valid_to` | Seconds in 2025–2027 |
| `EPOCH_MS_TS` (13 digits, about 1.789e12–1.791e12) | `orders.created_at`, `orders.updated_at` | Milliseconds in the same calendar range |

`orders` is the only millis pair. Do not copy that unit onto the other tables.

Integer `0` (`digit_len = 1`) occurs beside 10-digit seconds on:

- `business_service_i18ns.created_at`, `updated_at` (2 values)
- `business_services.last_in_activated_at` (87)
- `hotel_rate_plans.created_at`, `updated_at` (299207)
- `hotel_room_types.created_at`, `updated_at` (372185)

Zero is not a second epoch unit. It is an unset sentinel in an otherwise seconds column. Architecture must say whether `0` becomes NULL.

## E1, partner ISO

| Column | Class |
|---|---|
| `order_item_hotels.check_in_date`, `checkout_date` | `iso_utc_z`, fractional length 6 only |
| `order_item_tickets.usage_date` | `iso_utc_z`, fractional length 6 only |
| `order_item_flights.departure_time`, `arrival_time` | `iso_utc_z`. Four values have fractional length 6. Two values per column are `1970-01-01T00:00:00Z`. |

These are already instants. Format-normalize only. The 1970 values are the zero instant, same sentinel question as integer `0`.

## Unobserved

No non-empty value. No unit is assigned from a sibling column.

- No bronze events at all: `business_locations`, `product_post_translations`.
- `business_services.last_verify_at`: 134 empty. The seed still says `EPOCH_S_TS`. The population does not confirm it.
- `orders.expire_at`: 26271 empty.
- `order_refs.created_at`, `updated_at`: 65 empty.
- `order_item_tickets.created_at`, `updated_at`, `valid_from`, `valid_to`: 13 empty.
- `order_item_hotels.created_at`, `updated_at`: 8 empty.
- `order_item_flights.created_at`, `updated_at`: 16 empty.
- `deleted_at` on `products`, `product_variants`, `product_posts`, `hotel_room_types`, `hotel_rate_plans`: empty. Seed type remains `string`. Not classified as a timestamp.

Empty counts sit next to non-empty counts on the same column where both rows exist in the result file. Those columns are classified from the non-empty rows only.
