# Sample key tree

One bronze-shaped row. Paths and JSON types only. This is not a schema contract.

`normalized_payload` parses as one JSON object. `extra_info` is an object with no children. `raw_payload` parses as a JSON object and is not expanded.

`poi_media[].category` is `null` on some elements and `string` on others in this same document. Every `ext_attributes` value in this document is a string. The key set below is the set observed here (38 keys). The current registry comment still describes 62 keys on the old payload.

| path | JSON type |
|---|---|
| `$` | object |
| `source_id` | string |
| `source` | string |
| `poi_name` | string |
| `poi_name_normalized` | string |
| `business_sector` | string |
| `business_category` | string |
| `subcategory_tags` | array of string |
| `types` | array of string |
| `operating_status` | string |
| `partner_id` | null |
| `slug` | null |
| `slug_history` | null |
| `price_level` | null |
| `star_rating` | null |
| `accommodation_type` | null |
| `country_code` | string |
| `language_code` | string |
| `created_at` | string |
| `awards` | null |
| `poi_address` | object |
| `poi_address.full_address` | string |
| `poi_address.house_number` | null |
| `poi_address.street` | null |
| `poi_address.ward` | string |
| `poi_address.district` | string |
| `poi_address.city` | string |
| `poi_address.country` | string |
| `poi_address.country_code` | string |
| `poi_address.postal_code` | string |
| `poi_address.lat` | number |
| `poi_address.lng` | number |
| `poi_address.plus_code` | string |
| `poi_address.timezone` | string |
| `poi_address.address_line1` | string |
| `poi_address.address_line2` | string |
| `poi_address.state_province` | string |
| `poi_address.short_address` | string |
| `poi_address.address_google` | string |
| `poi_address.address_viet_map` | string |
| `poi_address.vietmap_status` | string |
| `poi_address.vietmap_message` | null |
| `poi_rating` | object |
| `poi_rating.rating_overall` | number |
| `poi_rating.rating_count` | number |
| `poi_rating.rating_breakdown` | null |
| `poi_rating.sub_ratings` | null |
| `poi_contact` | object |
| `poi_contact.phone` | string |
| `poi_contact.phone_raw` | string |
| `poi_contact.website_url` | null |
| `poi_contact.google_maps_url` | string |
| `poi_contact.social_links` | null |
| `poi_contact.delivery_links` | null |
| `poi_contact.booking_links` | null |
| `poi_amenity` | object |
| `poi_amenity.ext_attributes` | object |
| `poi_amenity.ext_attributes.<key>` | string |
| `poi_amenity.amenity_schema` | object |
| `poi_amenity.amenity_schema.facilities` | object, same shape as root `facilities` |
| `poi_amenity_schema` | null |
| `facilities` | object |
| `facilities.type` | string |
| `facilities.required` | string |
| `facilities.main_cuisine` | object |
| `facilities.main_cuisine.type` | string |
| `facilities.main_cuisine.required` | string |
| `facilities.main_cuisine.multiple_lang` | boolean |
| `facilities.main_cuisine.enum` | array of string |
| `facilities.specialty_tags` | object |
| `facilities.specialty_tags.type` | string |
| `facilities.specialty_tags.required` | string |
| `facilities.specialty_tags.item_type` | string |
| `facilities.specialty_tags.multiple_lang` | boolean |
| `facilities.specialty_tags.enum` | array of string |
| `facilities.space_and_services` | object |
| `facilities.space_and_services.type` | string |
| `facilities.space_and_services.required` | string |
| `facilities.space_and_services.item_type` | string |
| `facilities.space_and_services.multiple_lang` | boolean |
| `facilities.space_and_services.enum` | array of string |
| `facilities.additional_amenities` | object |
| `facilities.additional_amenities.type` | string |
| `facilities.additional_amenities.required` | string |
| `facilities.additional_amenities.item_type` | string |
| `facilities.additional_amenities.multiple_lang` | boolean |
| `facilities.additional_amenities.enum` | array of string |
| `poi_media` | array of object |
| `poi_media[].media_id` | string |
| `poi_media[].photo_api_uri` | string |
| `poi_media[].original_url` | string |
| `poi_media[].thumbnail_url` | string |
| `poi_media[].blob_url` | string |
| `poi_media[].media_type` | string |
| `poi_media[].category` | null or string |
| `poi_media[].is_blessed` | boolean |
| `poi_media[].display_order` | number |
| `poi_media[].photographer` | string |
| `poi_media[].width_px` | null |
| `poi_media[].height_px` | null |
| `poi_media[].file_size_bytes` | number |
| `poi_media[].caption` | null |
| `poi_media[].license` | string |
| `poi_media[].processing_status` | string |
| `poi_price` | null |
| `poi_content` | null |
| `poi_review` | array of object |
| `poi_review[].author_name` | string |
| `poi_review[].rating` | number |
| `poi_review[].text` | string |
| `poi_review[].time` | string |
| `poi_review[].source` | string |
| `poi_opening_hours` | object |
| `poi_opening_hours.open_now` | boolean |
| `poi_opening_hours.is_24_7` | boolean |
| `poi_opening_hours.is_temporarily_closed` | boolean |
| `poi_opening_hours.periods` | array of object |
| `poi_opening_hours.periods[].open_hour` | number |
| `poi_opening_hours.periods[].open_minute` | number |
| `poi_opening_hours.periods[].close_hour` | number |
| `poi_opening_hours.periods[].close_minute` | number |
| `poi_opening_hours.periods[].close_day` | number |
| `poi_opening_hours.periods[].day_of_week` | number |
| `poi_opening_hours.weekday_text` | array of string |
| `poi_opening_hours.secondary_hours` | array of object |
| `poi_opening_hours.secondary_hours[].type` | string |
| `poi_opening_hours.secondary_hours[].weekday_text` | array of string |
| `poi_opening_hours.secondary_hours[].periods` | array of object, same keys as `periods[]` |
| `policies` | null |
| `extra_info` | object, no children |
| `poi_id` | string |

## `extra_info` children

None. These paths are absent in this document:

- `extra_info.enrichment`
- `extra_info.enrichmentSiblings`
- `extra_info.enrichmentFailedLangs`

## `poi_amenity.ext_attributes` keys observed in this document

`businessStatus`, `delivery`, `dineIn`, `gm_directions_uri`, `gm_photos_uri`, `gm_place_uri`, `gm_reviews_uri`, `gm_write_review_uri`, `goodForChildren`, `goodForGroups`, `googleMapsUri`, `google_types`, `google_types_count`, `internationalPhoneNumber`, `menuForChildren`, `nationalPhoneNumber`, `open_now`, `outdoorSeating`, `parking_freeParkingLot`, `parking_freeStreetParking`, `payment_acceptsCashOnly`, `payment_acceptsCreditCards`, `payment_acceptsDebitCards`, `payment_acceptsNfc`, `photos_count`, `primaryType`, `primary_type_display`, `regular_open_now`, `reservable`, `restroom`, `reviews_count`, `routing_summaries_count`, `servesCocktails`, `servesDinner`, `short_formatted_address`, `takeout`, `utc_offset_minutes`, `weekday_descriptions`.

## One-document comparisons that are not rules

| Check | Result on this document |
|---|---|
| Payload `poi_id` equals `HASH_MD5_UUID` of bronze `source_name` + `source_id` | no |
| Payload `source_id` equals bronze `source_id` | yes |
| Lowercased payload `source` equals bronze `source_name` | yes |
| `poi_name_normalized` equals `lower(poi_name)` | yes |
| `poi_address.address_google` equals `poi_address.full_address` | yes |
| Root `facilities` deep-equals `poi_amenity.amenity_schema.facilities` | yes |
| `types` deep-equals `subcategory_tags` | yes |
| Review elements share one key set | yes |
| Media elements share one key set | yes |
| Any of the 38 flat amenity flag names occur under `poi_amenity` | no |
| Top-level `raw_data` | absent |
