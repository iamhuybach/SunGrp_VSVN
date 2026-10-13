# Paired payload comparison

Local context for task `20261013-3p-extract-from-raw-payload`. Compared on 2026-10-13. Keys, JSON types, and equality only. No values, review text, person names, URIs, or URLs. The sample files stay outside the repository.

Sources, not copied:

- `C:\Users\bachnh\Downloads\sample_normalized_payload.txt`
- `C:\Users\bachnh\Downloads\sample_raw_payload.txt`

Each file has three sections, `sample_1`, `sample_2`, and `sample_3`. Each section is one JSON object. This is not a schema contract.

## Identity

| Check | sample_1 | sample_2 | sample_3 |
|---|---|---|---|
| `normalized.source_id` equals `raw.id` | equal | equal | equal |
| `normalized.poi_id` equals `raw.id` | differ | differ | differ |
| `normalized.language_code` equals `raw.primaryTypeDisplayName.languageCode` | equal | equal | equal |
| `normalized.source` is the same string on all three sections | yes | yes | yes |
| `normalized.language_code` is the same string on all three sections | yes | yes | yes |

`source_name` is not inside either payload. Bronze columns `source_name`, `source_id`, and `language_code` stay outside the payload, per the user decision on Q1.

## Direct structural matches

These normalized leaves equal the raw path on every section where both sides are non-null.

| Normalized path | Raw path | Result |
|---|---|---|
| `poi_name` | `displayName` (string on all three) | equal |
| `poi_name_normalized` | `lower(poi_name)` | equal |
| `types` | `types` | equal |
| `subcategory_tags` | `types` | equal |
| `poi_address.full_address` | `formattedAddress` | equal |
| `poi_address.lat` | `location.latitude` | equal |
| `poi_address.lng` | `location.longitude` | equal |
| `poi_address.plus_code` | `plusCode.globalCode` | equal |
| `poi_contact.website_url` | `websiteUri` | equal, or both null |
| `poi_contact.google_maps_url` | `googleMapsUri` | equal |
| `poi_rating.rating_overall` | `rating` | equal |
| `poi_rating.rating_count` | `userRatingCount` | equal |
| `operating_status` | `lower(businessStatus)` | equal. Raw token is uppercase. Normalized token is lowercase. |
| `poi_review[]` in order: `author_name`, `time`, `rating`, `text` | `reviews[]`: `authorAttribution.displayName`, `publishTime`, `rating`, `text.text` | 5 of 5 equal on every section |
| `reviews[].name` versus `author_name` | | differ on every review |
| `poi_media[0:4].photo_api_uri` | `photos[0:4].name` | equal |
| `poi_media[].display_order` | 1-based index of the kept photos | equal |

Normalized media keeps the first 5 photos. Raw has 10 photos on every section. `width_px` and `height_px` are null in normalized. Raw `widthPx` and `heightPx` are integers.

## Address components

Component `types` seen: `street_number`, `route`, `administrative_area_level_2+political`, `administrative_area_level_1+political`, `country+political`, and on `sample_2` also `postal_code`. No `locality` or ward type token appeared.

| Normalized column | Match inside `addressComponents` |
|---|---|
| `house_number` | `street_number` `longText` |
| `street` | `route` `longText` |
| `ward` | `administrative_area_level_2` `longText` |
| `city` | `administrative_area_level_1` `longText` |
| `state_province` | same component as `city` |
| `country_code` | `country` `shortText` |
| `postal_code` | `postal_code` `longText` when that component exists. Null on `sample_1` and `sample_3`. |
| `district` | no component match. Non-empty. Not equal to `city`, `ward`, or `state_province`. |
| `country` | no component match. Same non-empty string on all three sections. |
| `short_address` | not equal to `shortFormattedAddress`, `ward`, `city`, or `state_province`. |

## Opening hours and price

`sample_1` and `sample_2`: `poi_opening_hours`, `poi_price`, `regularOpeningHours`, `currentOpeningHours`, and `priceLevel` are null. `sample_2` still has `regularSecondaryOpeningHours` as an array of 9 objects. That array is not copied into normalized `poi_opening_hours`.

`sample_3`:

- `regularOpeningHours` and `currentOpeningHours` are objects with keys `nextCloseTime`, `openNow`, `periods`, `weekdayDescriptions`.
- `open_now` equals both `regularOpeningHours.openNow` and `currentOpeningHours.openNow`.
- `weekdayDescriptions`, `nextCloseTime`, and every period `day`, `hour`, and `minute` are equal between `regularOpeningHours` and `currentOpeningHours`.
- The period objects are not identical. `currentOpeningHours` adds `date` on `open` and `close`. `regularOpeningHours` has no `date`.
- Flattened normalized periods equal both sides. This one section does not show a day where the two `openNow` booleans differ.
- `weekday_text` equals `regularOpeningHours.weekdayDescriptions`.
- Both period arrays have length 14. Raw period keys are `open` and `close`, each an object with `day`, `hour`, `minute`. Normalized period keys are `open_hour`, `open_minute`, `close_hour`, `close_minute`, `day_of_week`, `close_day`. Field-by-field equality holds on this section.
- `priceLevel` is a string whose prefix is `PRICE_LEVEL_` and whose length is 20. Normalized `poi_price.price_level` and top-level `price_level` are integers. The integer matches the standard Google enum index (`FREE` 0, `INEXPENSIVE` 1, `MODERATE` 2, `EXPENSIVE` 3, `VERY_EXPENSIVE` 4). A direct integer cast of the raw string does not match.
- `priceRange` is an object with `startPrice` and `endPrice`.

## Phone and flags

On `sample_2` and `sample_3`, digits of `phone` equal digits of `nationalPhoneNumber`, and digits of `phone_raw` equal digits of `internationalPhoneNumber`. The strings themselves are not equal after removing spaces, and they are not the digits-only form. `sample_1` has both phone sides null.

`sample_3` has 21 of 23 flag-like keys non-null, and those values are JSON booleans. Normalized `poi_amenity.ext_attributes.servesCoffee` equals the lowercase string of the raw boolean on the sections where that key exists. `ext_attributes` key counts are 21 and 52. This is a flatten, not the raw object.

## Not reproduced by a raw path

`business_category` and `business_sector` differ across the three sections. They are not equal to `primaryType` or `primaryTypeDisplayName.text`. `business_category` is inside the normalized `facilities.*.enum` list on two sections and not on the third.

Also not equal to a raw path in these pairs: `district`, `country`, `short_address`, exact `phone` and `phone_raw` strings, `address_viet_map`, `timezone`, `slug`, `policies`, and `poi_content` (null on the normalized side).

## Questions closed by this file

| Question | Result |
|---|---|
| Q1 | `id` equals `source_id` on all three pairs. `poi_id` inside the normalized object is a different string. |
| Q2 | Each section of the raw file is one JSON object. |
| Q7 | Review author, time, rating, and text match in order. `reviews[].name` is not `author_name`. |
| Q8 | `photos[].name` equals `photo_api_uri` for the five photos normalized kept. |
| Q9 | Non-null `priceLevel` is a `PRICE_LEVEL_*` string, not an integer. |
| Q10 | `sample_3` shows the nested hour shape. `open_now` matches both regular and current on that one section. |
| Q11 | `displayName` is a string and equals `poi_name` on all three sections. |
| Q12 | Non-null booleans exist on `sample_3`. Normalized stores selected flags as strings inside `ext_attributes`. |
