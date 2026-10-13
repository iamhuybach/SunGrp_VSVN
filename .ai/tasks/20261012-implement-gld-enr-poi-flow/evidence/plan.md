# Evidence plan

## Decision to resolve

1. Which top-level JSON keys inside `lh_vv_silver.dbo.slv_pn_business_services.address` are non-empty, so `slv_pn_poi.ward`, `district`, and `province_name` can be filled without inventing a key. `short_address` stays `address.full_address` (`MQ-025`); the probe only checks that key is non-empty.
2. Which `locale` values exist on `lh_vv_silver.dbo.slv_pn_business_service_i18ns`, so the Vietnamese name row for `slv_pn_poi.name` uses a value that is present.

These keys and the locale literal are not columns in `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS` or in `docs/context/01_DATA_MODEL.md`. The `address` column itself is a string. `slv_pn_poi` is proposed and is not probed as an existing table.

## Existing evidence

Repository inspection on 2026-10-12. No Fabric run.

| Mapping source | Column or path | Present in |
|---|---|---|
| `slv_3p_poi` | `poi_id`, `poi_name`, `types_json`, `business_sector`, `business_category`, `source_name`, `source_id` | `TABLE_CONFIGS_3P` |
| `slv_3p_poi_address` | `short_address`, `address_viet_map`, `ward`, `district`, `city`, `state_province`, `lat`, `lng` | `TABLE_CONFIGS_3P` |
| `slv_3p_poi_review` | `review_id`, `poi_id`, `text`, `time`, `published_at`, `rating` | `TABLE_CONFIGS_3P` |
| `slv_3p_poi_contact` | `website_url` | `TABLE_CONFIGS_3P` |
| `slv_3p_poi_rating` | `rating_overall`, `rating_count` | `TABLE_CONFIGS_3P` |
| `slv_3p_poi_price` | `price_level` | `TABLE_CONFIGS_3P` |
| `slv_3p_poi_opening_hours` | `periods_json` | `TABLE_CONFIGS_3P` |
| `slv_pn_business_services` | `id`, `name`, `address` | `TABLE_CONFIGS` |
| `slv_pn_business_service_i18ns` | `business_service_id`, `locale`, `name` | `TABLE_CONFIGS` |

`COL-004`, `COL-005`, `COL-006`, and `COL-007` have an empty source. Do not probe removed enrichment tables.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `e1_partner_address_keys.sql` | Fabric DEV, silver | Which top-level keys of `address` are non-empty? | Pass: the file lists key names and non-empty counts only, includes `full_address`, and contains no address text. Fail: the query errors, or `address` has zero rows that parse as a JSON object. | `evidence/results/e1_partner_address_keys.txt` |
| `e2_partner_i18n_locale.sql` | Fabric DEV, silver | Which `locale` values exist, and how many rows does each have? | Pass: the file lists at most 50 locale values and a row count for each, with no name or bio. Fail: the query errors. A later user choice is required when none or more than one value is Vietnamese. | `evidence/results/e2_partner_i18n_locale.txt` |

## Observed results

Recorded 2026-10-13 from the operator's Fabric DEV table views.

| Probe | Result | Interpretation |
|---|---|---|
| `e1_partner_address_keys` | 30 active rows, 30 JSON objects. Non-empty keys: `full_address` 30, `address_line1` 23, `city` 23, `street` 23, `ward` 23, `country` 12. | `short_address` uses `full_address`. `ward` uses `ward`. No non-empty `district` or province-level key. `city` is the remaining place-name key. |
| `e2_partner_i18n_locale` | `ko` 123, `vi` 121, `en` 118. | The Vietnamese locale literal is `vi`. |

On 2026-10-13 the user closed the remaining address formulas from `slv_pn_business_services.address`: `district` from `district`, `province_name` from `city`, `ward` from `ward`, `short_address` from `full_address`. The operator sample contains those keys. `district` may be an empty string. The sample address text is not stored.

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
