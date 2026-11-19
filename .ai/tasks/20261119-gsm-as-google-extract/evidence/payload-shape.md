# SGM normalized_payload shape

One bronze document with `source_name = 'sgm'`. Keys and JSON types only. This is not a distribution and not a schema contract. No names, review text, phone numbers, or URLs.

The extract contract reads bronze columns `source_name` and `source_id` (`RAW_DOC_ID` in `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`). This document does not show those bronze columns. `id` below is a payload key. It is not evidence that `id` equals `source_id`.

## Observed shape

| path | JSON type | element / note |
|---|---|---|
| `$` | object | |
| `id` | string | payload key only |
| `displayName` | string | |
| `formattedAddress` | string | |
| `location` | object | |
| `location.latitude` | number | |
| `location.longitude` | number | |
| `types` | array | string |
| `rating` | number | |
| `userRatingCount` | number | |
| `priceLevel` | null | key present |
| `businessStatus` | string | |
| `currentOpeningHours` | null | key present |
| `regularOpeningHours` | null | key present |
| `internationalPhoneNumber` | string | |
| `websiteUri` | string | |
| `photos` | array | object |
| `photos[].name` | string | shape `places/.../photos/scraper-NN` |
| `photos[].widthPx` | number | |
| `photos[].heightPx` | number | |
| `photos[].authorAttributions` | array | object; the array can be empty |
| `photos[].authorAttributions[].displayName` | string | only when the array is non-empty |
| `photos[].authorAttributions[].uri` | string | only when the array is non-empty |
| `photos[].authorAttributions[].photoUri` | string | only when the array is non-empty |
| `photos[].flagContentUri` | null | key present |
| `photos[].googleMapsUri` | null | key present |
| `photos[].blob_url` | string | key present on the photo element |
| `parkingOptions` | null | key present |
| `paymentOptions` | null | key present |
| `accessibilityOptions` | null | key present |
| `addressComponents` | array | object |
| `addressComponents[].longText` | string | |
| `addressComponents[].shortText` | string | |
| `addressComponents[].types` | array | string |
| `addressComponents[].languageCode` | string | |
| `primaryTypeDisplayName` | object | |
| `primaryTypeDisplayName.text` | string | |
| `primaryTypeDisplayName.languageCode` | string | |
| `googleMapsUri` | string | |
| `primaryType` | string | |
| `nationalPhoneNumber` | string | |
| `plusCode` | object | |
| `plusCode.globalCode` | string | |
| `plusCode.compoundCode` | string | |
| `reviews` | array | object |
| `reviews[].name` | string | |
| `reviews[].relativePublishTimeDescription` | string | |
| `reviews[].rating` | number | this document has numeric `0` |
| `reviews[].text` | object | |
| `reviews[].text.text` | string | |
| `reviews[].text.languageCode` | string | |
| `reviews[].originalText` | object | |
| `reviews[].originalText.text` | string | |
| `reviews[].originalText.languageCode` | string | |
| `reviews[].authorAttribution` | object | |
| `reviews[].authorAttribution.displayName` | string | |
| `reviews[].authorAttribution.uri` | string | this document has an empty string |
| `reviews[].authorAttribution.photoUri` | string | |
| `reviews[].publishTime` | string | fractional seconds are present |
| `reviews[].flagContentUri` | null | key present |
| `reviews[].googleMapsUri` | null | key present |
| `routingSummaries` | array | empty |
| `priceRange` | null | key present |
| `regularSecondaryOpeningHours` | array | empty |
| `currentSecondaryOpeningHours` | array | empty |
| `shortFormattedAddress` | string | |
| `utcOffsetMinutes` | number | |
| `evChargeOptions` | null | key present |
| `fuelOptions` | null | key present |
| `googleMapsLinks` | object | |
| `googleMapsLinks.directionsUri` | string | |
| `googleMapsLinks.placeUri` | string | |
| `googleMapsLinks.writeAReviewUri` | string | |
| `googleMapsLinks.reviewsUri` | string | |
| `googleMapsLinks.photosUri` | string | |
| `x_lodging` | object | |
| `x_lodging.hotelClass` | string | |
| `x_lodging.checkInTime` | string | |
| `x_lodging.checkOutTime` | string | |
| `x_lodging.amenities` | array | string |
| `x_scraper` | object | |
| `x_scraper.category` | string | |
| `x_scraper.cid` | string | |
| `x_scraper.data_id` | string | |
| `x_scraper.status_text` | string | |
| `x_scraper.complete_address` | object | |
| `x_scraper.complete_address.borough` | string | |
| `x_scraper.complete_address.street` | string | |
| `x_scraper.complete_address.city` | string | |
| `x_scraper.complete_address.postal_code` | string | |
| `x_scraper.complete_address.state` | string | |
| `x_scraper.complete_address.country` | string | |
| `x_scraper.about` | array | empty |
| `x_scraper.reviews_per_rating` | object | keys `1`, `2`, `3`, `4`, `5`; each value is a number |

## Registry keys on this document

Active Google registry heads are `TABLE_CONFIGS_3P` in `NB_CREATE_DDL` cell 14. Comparison is presence only.

JSON null, key present: `priceLevel`, `currentOpeningHours`, `regularOpeningHours`, `priceRange`, `parkingOptions`, `paymentOptions`, `accessibilityOptions`, `evChargeOptions`, `fuelOptions`.

Absent from this document, not JSON null: `servesBreakfast`, `servesBrunch`, `servesLunch`, `servesDinner`, `servesBeer`, `servesWine`, `servesCocktails`, `servesDessert`, `servesCoffee`, `servesVegetarianFood`, `allowsDogs`, `goodForChildren`, `goodForGroups`, `goodForWatchingSports`, `liveMusic`, `menuForChildren`, `outdoorSeating`, `restroom`, `reservable`, `takeout`, `delivery`, `dineIn`, `curbsidePickup`.

Top-level keys on this document that are not registry heads: `id`, `internationalPhoneNumber`, `primaryTypeDisplayName`, `routingSummaries`, `regularSecondaryOpeningHours`, `currentSecondaryOpeningHours`, `shortFormattedAddress`, `utcOffsetMinutes`, `googleMapsLinks`, `x_lodging`, `x_scraper`.

`addressComponents[].types` values seen on this document: `route`, `sublocality_level_1`, `sublocality`, `political`, `locality`, `administrative_area_level_1`, `postal_code`, `country`. `street_number` and `administrative_area_level_2` do not appear. That is this document only.
