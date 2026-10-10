# L1 timestamp inventory

Source: `notebooks/NB_CREATE_DDL.ipynb` seed (`TABLE_CONFIGS`, `TABLE_CONFIGS_3P`, `resolve_type`). This is the registry contract in git, not a Fabric catalog dump.

`resolve_type("epoch_seconds_timestamp")` returns `("timestamp", "EPOCH_S_TS")`. Every other partner type in this list uses `NONE`.

## Proven without a new probe

| Column | Evidence | Next step |
|---|---|---|
| `slv_pn_business_services.last_verify_at` | Seed type `epoch_seconds_timestamp` → `EPOCH_S_TS` | E1 must confirm the population is integer seconds |
| 3P `source_created_at`, `published_at` | Seed type `timestamp`, rule `NONE`. One attached document stores ISO-8601 with 9 fractional digits and a `Z` suffix. Comment in the 3P seed says the 04/10 cast of ISO-8601 succeeded | E2 must confirm the current bronze population. Not an epoch rule |
| 3P `ingested_date` on bronze | One document is `YYYY-MM-DD` | E2. If the population is a date, do not add a time |
| L1 technical clocks (`_ingested_at`, `_crawled_at`, `_first_seen_at`, `_last_seen_at`) | Written by the extract notebooks as Spark timestamps, not source epochs | Format is an architecture choice after the business-column units are known |

`slv_pn_product_attribute_value_translations` has no business timestamp column. It still receives audit `created_at` and `updated_at`.

## Partner candidates whose unit is not proven

`bigint` + `NONE` stores the JSON number as `bigint`. `string` + `NONE` stores the raw string. Neither mapping records seconds, millis, micros, or ISO.

| Target | Source table | Column | Seed type |
|---|---|---|---|
| `slv_pn_products` | `products` | `created_at`, `updated_at` | bigint |
| `slv_pn_products` | `products` | `deleted_at` | string |
| `slv_pn_product_translations` | `product_translations` | `created_at`, `updated_at` | bigint |
| `slv_pn_product_attributes` | `product_attributes` | `created_at`, `updated_at` | bigint |
| `slv_pn_product_attribute_translations` | `product_attribute_translations` | `created_at`, `updated_at` | bigint |
| `slv_pn_product_attribute_values` | `product_attribute_values` | `created_at`, `updated_at` | bigint |
| `slv_pn_product_variants` | `product_variants` | `created_at`, `updated_at` | bigint |
| `slv_pn_product_variants` | `product_variants` | `deleted_at` | string |
| `slv_pn_product_variant_translations` | `product_variant_translations` | `created_at`, `updated_at` | bigint |
| `slv_pn_product_business_service_relation` | `product_business_service_relation` | `created_at`, `updated_at` | bigint |
| `slv_pn_product_posts` | `product_posts` | `created_at`, `updated_at` | bigint |
| `slv_pn_product_posts` | `product_posts` | `deleted_at` | string |
| `slv_pn_product_post_translations` | `product_post_translations` | `created_at`, `updated_at` | bigint |
| `slv_pn_partners` | `partners` | `created_at`, `last_updated_at` | bigint |
| `slv_pn_business_services` | `business_services` | `created_at`, `last_updated_at`, `last_in_activated_at` | bigint |
| `slv_pn_business_locations` | `business_locations` | `created_at`, `last_updated_at` | bigint |
| `slv_pn_hotel_room_types` | `hotel_room_types` | `created_at`, `updated_at` | bigint |
| `slv_pn_hotel_room_types` | `hotel_room_types` | `deleted_at` | string |
| `slv_pn_hotel_rate_plans` | `hotel_rate_plans` | `valid_from`, `valid_to`, `created_at`, `updated_at` | bigint |
| `slv_pn_hotel_rate_plans` | `hotel_rate_plans` | `deleted_at` | string |
| `slv_pn_business_service_i18ns` | `business_service_i18ns` | `created_at`, `updated_at` | bigint |
| `slv_pn_business_service_poi_link` | `business_service_poi_link` | `created_at`, `updated_at` | bigint |
| `slv_pn_orders` | `orders` | `expire_at`, `created_at`, `updated_at` | bigint |
| `slv_pn_order_refs` | `order_refs` | `created_at`, `updated_at` | bigint |
| `slv_pn_order_item_tickets` | `order_item_tickets` | `created_at`, `updated_at` | bigint |
| `slv_pn_order_item_tickets` | `order_item_tickets` | `usage_date`, `valid_from`, `valid_to` | timestamp |
| `slv_pn_order_item_hotels` | `order_item_hotels` | `created_at`, `updated_at` | bigint |
| `slv_pn_order_item_hotels` | `order_item_hotels` | `check_in_date`, `checkout_date` | timestamp |
| `slv_pn_order_item_flights` | `order_item_flights` | `created_at`, `updated_at` | bigint |
| `slv_pn_order_item_flights` | `order_item_flights` | `departure_time`, `arrival_time` | timestamp |

Context calls the `timestamp` seed type timestamptz ISO. E1 still has to show the raw string class (Z, offset, fractional digits, or date) before format normalization. `deleted_at` is a string in the seed, so it is not yet classified as a timestamp.

Known data gap from `docs/context/01_DATA_MODEL.md` and `99_PAIN_POINTS.md`: several `product*` tables and `order_item_flights` have had empty `after`, and `business_locations` / `product_post_translations` have had no events. Those columns can come back from E1 as unobserved.

## Third-party business timestamps in the seed

| Target | Column | Path | Seed type | Rule |
|---|---|---|---|---|
| `slv_3p_poi` | `source_created_at` | `created_at` | timestamp | NONE |
| `slv_3p_poi_review` | `published_at` | `time` | timestamp | NONE |
| `slv_3p_poi_review` | `time` | `time` | string | NONE |

`time` is an input of `review_id` (`HASH_SHA256` of `source_name`, `source_id`, `author_name`, `time`). Reformatting `time` would change the key. `published_at` is the typed twin. E2 classifies both shapes; it does not authorize changing `time`.

## Audit name collision

Partner business `created_at` and `updated_at` collide with the requested audit names. `last_updated_at`, `last_verify_at`, `last_in_activated_at`, and source `deleted_at` do not use those two names. The partner technical delete flag remains `deleted`.
