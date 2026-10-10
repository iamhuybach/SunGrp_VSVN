# E3 and E4 interpretation

E3 is the deployed partner registry versus silver `DESCRIBE` and current time-column ranges. E4 is three fullest bronze payloads per source table versus registry `json_path`. Shapes only. No payload text was interpreted.

## Registry matches silver DDL

301 registry rows. Rules in Fabric: `NONE` 297, `EPOCH_S_TS` 1 (`slv_pn_business_services.last_verify_at`), `DECIMAL_BASE64` 3. That matches the git seed.

`schema_diff`: 274 `MATCH`, 0 `TYPE_MISMATCH`. The 63 `EXTRA_IN_SILVER` rows are only `deleted`, `_ingested_at`, and `_source_db` on the 21 tables that exist. Those columns are technical and are not registry rows.

Two registry targets have no silver table, because bronze has no JSON payload for them (`no_sample` in E4):

- `slv_pn_business_locations`
- `slv_pn_product_post_translations`

## Bronze keys the registry does not map

Present on at least one of the three fullest payloads. Not a silver type mismatch.

| Source table | Keys in payload, absent from registry |
|---|---|
| `business_services` | `deleted_at`, `facility_type`, `local_tips_v2`, `logo`, `main_locale`, `usps_v2` |
| `partners` | `edit_consent` |
| `product_posts` | `category`, `history`, `partner_id` |
| `product_translations` | `description`, `gallery`, `thumbnail` |
| `product_variant_translations` | `description` |
| `product_variants` | `metadata` |

No sampled value disagreed with the registry `data_type` (bigint stayed integer, timestamp stayed ISO, boolean stayed true/false).

## Time columns confirmed again on silver

Current silver ranges agree with E1. `orders.created_at` and `orders.updated_at` are 13-digit millis. Other non-zero business instants that are `bigint` are 10-digit seconds. ISO columns on `order_item_*` are timestamps. `last_verify_at` is `timestamp` and all 30 silver values are null.

`hotel_room_types` and `hotel_rate_plans` current `created_at` / `updated_at` are entirely `0` (208 and 165 rows). E1 still saw a few 10-digit values in older bronze events. The latest merged row is the zero sentinel. The non-zero unit remains seconds.

`product_posts.validity_from` and `validity_to` are `bigint` in the registry and absent on the three fullest payloads. E1 did not measure them. No unit is assigned.
