# Column mapping — NB_SETUP_LEGACY_GOLD_POI

Baseline is the current init notebook and the current gold model. Task `20261119-legacy-gold-poi-init` decisions D-01 through D-09 are not reopened. A column that follows one of those decisions is `match` even when the live gold notebook computes the same column from silver.

`to_target` writes every column of the target table. A target column absent from the init frame is stored as NULL of the target type, then `row_hash`, `created_at`, `updated_at`, `deleted_at` NULL, and `load_origin = LEGACY_INIT`. Those technical columns are `match` with D-04 / D-09 and are not listed again per table.

Verdict `match`: the init expression reads a key the old notebook writes, and the value is the old serving value D-07/D-08 asked to load, or it is the same rule the current model runs. Verdict `mismatch`: the init expression does not implement the current rule, or it reads a key the old notebook does not fill.

## gld_srv_poi_info

| Column | Init expression | Old-notebook source | Current-model rule | Verdict |
|---|---|---|---|---|
| poi_id | `new_poi_id` on the map (`uuid_md5`) | Old `poi_id` is the legacy id. Map stores it as `legacy_poi_id`. | `uuid_md5(lit("google"), source_id)` or `uuid_md5(source_id, lit("partner"))`. No language. | match |
| source_name | `legacy_source_name`: `google` stays `google`; `partner_portal` becomes `partner`; anything else NULL | `poi_master.ingestion_source` | Entity `source_name` 1-1, values `google` and `partner` | match |
| business_sector, business_category, subcategory_tags, operating_status | One `poi_master` payload per new `poi_id` (`collect_set`); conflict is dropped | NB_40 copies the stage columns. `subcategory_tags` is `to_json` | Entity 1-1. `types_json` becomes `subcategory_tags` | match |
| poi_name, district | `poi_master` row with `lang = vi`. No `vi` row leaves both NULL | NB_40 `poi_name` and `district` on the `vi` master row | Entity `poi_name` 1-1. `district` comes from destination, then `old_district` | match (D-06). Not a defect to recode |
| is_verified, is_bookable | Copied from `poi_master` | NB_40 writes both columns. Partner notebook writes `is_bookable` | Mapping: both NULL. The new pipeline has no silver source | match (D-07: a field with an old-gold source is loaded) |
| is_recommended | Copied from `poi_master.is_recommended` | Partner notebook sets `True` (line 1357 of `2.1. transform_partner_to_gold_poi_master.ipynb`). NB_40 does not assign the column | `true` when `lower(trim(source_name)) = partner`, otherwise `false` | mismatch |
| is_active | `lit(true)` | Old `poi_master.is_active` is not copied | `lit(true)` for every row | match |
| rating_overall | Google only: `poi_master.rating_overall` cast `decimal(4,2)`. Other sources NULL | NB_40: `poi_rating.overall` | Google only, `slv_3p_poi_rating.rating_overall` 1-1. No row stays NULL | match |
| rating_count | Google only: `poi_master.rating_count` cast `int` | NB_40: `COALESCE(poi_rating.total_reviews, 0)`. `total_reviews` is `rating_json.$.rating_count` (NB_20) | Google only, `slv_3p_poi_rating.rating_count`. No coalesce to 0. No row stays NULL | mismatch |
| review_count | `max(poi_rating.total_reviews)` cast `int`, any source that joins | Same `$.rating_count`. This is not a count of `poi_review` rows | Google only: `COUNT(*)` of review rows. No coalesce to 0. Other sources NULL | mismatch |
| full_address, street, ward, city, country_code, postal_code, lat, lng | `get_json_object` on `poi_address_json`: `$.full_address`, `$.address_line1`, `$.ward`, `$.city`, `$.country_code`, `$.postal_code`, `$.lat`, `$.lng` | NB_40 `named_struct` has those keys. Partner `address_json` has the same keys (`address_line1` = street, `full_address` = `addr_full`, `country_code` = `VN`, `postal_code` null) | With a destination row: `full_address` is coalesce of three built groups; ward/city/district coalesce to `old_*`. Partner with no destination row: entity 1-1. Inputs `house_number`, `formatted_address`, `ward_with_type`, `city_with_type` are not in old gold | match (D-07). The destination rule cannot run on the stored JSON. Not a wrong path |
| phone, email, website_url | `poi_contact_json` `$.phone`, `$.email`, `$.website_url` | NB_40 and the partner notebook both write those three keys. Partner also writes `hotline`, which init does not read | Entity 1-1 | match |
| operating_hours | `get_json_object(poi_content_json, $.hours_weekday_text)` | Google: NB_20 inserts `poi_content.hours_weekday_text` as NULL and the UPDATE does not set it. NB_40 copies that column into `poi_content_json`. Partner `poi_content_json` keys are `vi.display_name`, `vi.description_short`, `vi.description_long`, `vi.service_bio`. There is no `hours_weekday_text` | Not a raw copy of `opening_hours_text`. Google: mapping §1.3 on a periods array (`open_hour`, `open_minute`, `close_hour`, `close_minute`, `day_of_week`); stop on `GOOGLE_INVALID_JSON`, `GOOGLE_NOT_ARRAY`, `GOOGLE_BAD_ELEMENT`, `GOOGLE_BAD_DAY`, `GOOGLE_BAD_TIME`. Partner: mapping §1.5 on the object `$.policies.operating_hours` (`monday`..`sunday`, `hours[].open_time/close_time`) | mismatch |
| holiday_exceptions | `get_json_object(poi_opening_hours_json, $.holiday_exceptions)` | Google: NB_20 copies `opening_hours_json.$.holiday_exceptions` and NB_40 stores it as `holiday_exceptions`. Partner key is `holiday_exceptions_json`, a list taken from `policies.operating_hours.holiday_exceptions` (`oh_path` is `["policies", "operating_hours"]`). `$.policies.holiday_exceptions` is not stored; `extract_amenities_json` drops `policies` | Entity: partner `get_json_object(amenities, $.policies.holiday_exceptions)` kept as a JSON string, not parsed. Google entity column is `lit(None)`. Gold copies the entity column 1-1. Do not invent a Google value | mismatch |
| cover_id, cover_blob_url | `poi_media_json` `$.cover.media_id`, `$.cover.blob_url` | NB_40 and the partner notebook both write `cover.media_id` and `cover.blob_url` | Cover row of `slv_poi_media_info` where `is_cover = true` | match |
| destination_id | `get_json_object(poi_master.destination_ids, $[0])` on the `vi` row | NB_40: `to_json(array(dest_id))` when a destination resolves | `slv_enr_poi_destination.destination_id` 1-1. Partner with no destination row: NULL | match (D-07) |
| destination_name | `poi_master.destination_names` on the `vi` row | NB_40: `to_json(array(dest_name))` | JSON array string from destination, same order, nulls kept | match (D-07) |

### Hours keys actually written

Google `poi_opening_hours_json` (NB_40): `timezone`, `is_24_7`, `open_now`, `periods`, `holiday_exceptions`. `periods` is `get_json_object(opening_hours_json, $.periods)` from bronze `$.poi_opening_hours`. The notebooks do not name the keys inside that periods value.

Partner `poi_opening_hours_json`: `timezone`, `is_24_7`, `periods_json`, `holiday_exceptions_json`. Each `periods_json` element has `day_of_week`, `open_hour`, `open_minute`, `close_hour`, `close_minute`. Only `hours[0]` is kept. Sunday is `0`. A closed day is omitted. `is_24_7` is a sibling flag. The object `policies.operating_hours` (`monday`..`sunday`, `status`, `hours[].open_time/close_time`) is read and then dropped. It is not in old gold.

That stored partner object is not the input of mapping §1.5. Mapping §1.3 is the Google periods rule, not the partner rule. No new parser is written in this task until the user names the transform.

## gld_srv_poi_multi_lang

| Column | Init expression | Old-notebook source | Current-model rule | Verdict |
|---|---|---|---|---|
| poi_id, lang, source_name | Map `poi_id`, display `lang`, map `source_name`. Orphans and NULL `lang` are dropped | `poi_enrichment_display` joined to the map | `poi_id` + `lang` from `slv_enr_poi_info_multi_lang`, plus partner i18n-only rows | match |
| description, time_to_spend, best_time, cost, experience | Display columns. `experiences` is renamed `experience`. `cost` only when the target has the column | NB_40 writes `description`, `time_to_spend`, `best_time`, `cost`, `experiences` (`experiences_json`) | Partner: `description = coalesce(bio, enr description)`, `experience = coalesce(usps, enr experience)`. Other sources: enr columns. Measures come from enr | match (D-07). Old display is the historical source. Partner `bio`/`usps` are not in this gold table |

## gld_srv_poi_review

| Column | Init expression | Old-notebook source | Current-model rule | Verdict |
|---|---|---|---|---|
| review_id, poi_id | `poi_review.review_id`; map `poi_id` | NB_40 review aggregate uses `review_id` and `poi_id` | `slv_3p_poi_review` 1-1. Google source only | match |
| rating_overall, rating_count | `poi_rating.overall`; `poi_rating.total_reviews` | `total_reviews` = `rating_json.$.rating_count` | Left join `slv_3p_poi_rating` on `poi_id`. Duplicate rating rows stop the node | match |
| title | `poi_review.title` | Old review row has `title` | `lit(None)`. Silver review has no title | match (D-07: the old column has a source) |
| review_text, rating, review_date, author_name | `review_text`, `rating` cast `decimal(4,2)`, `review_date` cast string, `reviewer_name` | NB_40 review struct: `review_text`, `rating_score`, `review_date`, `reviewer_name` | `text`, `rating`, `time`, `author_name` | match |
| source_name | `coalesce(poi_review.source, map source_name)` | Review row `source` | Literal `google` | match. Partner notebook writes `poi_review_json = []`, so this table is the Google flow |

## gld_srv_poi_media_gallery

| Column | Init expression | Old-notebook source | Current-model rule | Verdict |
|---|---|---|---|---|
| media_id, poi_id, blob_url, source_name | Cover struct plus exploded `gallery`. Group by `(poi_id, media_id)` | NB_40 `cover` and `gallery` elements are `media_id`, `blob_url`. Partner builds the same two keys | `slv_poi_media_info` 1-1 | match |
| is_cover | Cover path `true`, gallery path `false`, then `max` per `(poi_id, media_id)` | NB_40 `cover_rn = 1` is the cover. Gallery also contains that media | `is_cover` 1-1 | match |
| is_active | `lit(true)` | Old media filter is `is_active = true` before the JSON build | `is_active` 1-1 | match |
| photo_api_uri, display_order, width_px, height_px, photographer, thumbnail_url | Not in the frame, so `to_target` stores NULL | Not in the old cover/gallery struct | Silver 1-1 when present | match (D-07: init does not invent these) |

## gld_srv_poi_amenity

| Column | Init expression | Old-notebook source | Current-model rule | Verdict |
|---|---|---|---|---|
| poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_en, amenity_vi, service_flags | Enum walk of `poi_detail.amenities_json` for the `vi` detail row, joined to `ref_dictionary_amenities` on `source_name` and `business_sector`. A token that hits more than one dictionary row is dropped | `amenities_json` is the old detail column. Partner `extract_amenities_json` keeps the sector object and drops `policies` | `NB_GLD_SRV_POI_AMENITY` projects the same eight business columns from silver | match (D-08) |

## Open transform questions

These two columns stay on the unproven init paths until the user names the rule. No parser is added for a shape that is not the mapping input.

1. `operating_hours`. Init reads `$.hours_weekday_text`, which Google stores as NULL and partner does not write. The hours that old gold does store are `poi_opening_hours_json.periods` (Google, inner keys not named in the notebooks) and `poi_opening_hours_json.periods_json` (partner, keys listed above). `policies.operating_hours` is not in old gold.
2. `holiday_exceptions`. Init reads `$.holiday_exceptions`. That key exists for Google. The partner key is `holiday_exceptions_json`. The mapping path `$.policies.holiday_exceptions` is not in old gold. Google entity has no value; copying the old Google key would invent one.

`rating_count`, `review_count`, and `is_recommended` have a current rule and do not need a new parser. They wait for the same implementation pass as the hours columns. They are not a reason to guess a hours transform.
