## 7. poi_amenity — AMENITY_MAPPING

Source: `app/mappings/amenity.py` → `AMENITY_MAPPING`, `TOP_LEVEL_FIELD_MAPPING`

### 7.1 Nguồn 1: `amenities[]` string list

| Google amenity string | Internal field | Nhóm |
| --- | --- | --- |
| wheelchair_accessible_entrance/parking/restroom/seating | is_wheelchair_accessible | Accessibility |
| parking, free_parking_lot, paid_parking_lot, free_street_parking, paid_street_parking, valet_parking, free_garage_parking, paid_garage_parking | has_parking | Parking |
| delivery | fnb_delivery | F&B |
| takeout, curbside_pickup | fnb_takeaway | F&B |
| dine_in | fnb_dine_in | F&B |
| outdoor_seating | has_outdoor_seating | Facilities |
| live_music, alcohol, serves_beer, serves_wine, serves_cocktails | fnb_serves_alcohol | F&B |
| family_friendly, good_for_children, menu_for_children, good_for_families | fnb_good_for_families | F&B |
| good_for_couples | fnb_good_for_couples | F&B |
| good_for_groups, good_for_watching_sports | fnb_good_for_groups | F&B |
| reservable | fnb_reservable | F&B |
| credit_cards, debit_cards, accepts_credit_cards, accepts_debit_cards, nfc, accepts_nfc | payment_card | Payment |
| cash_only, accepts_cash_only | payment_cash | Payment |
| wi_fi, wifi, free_wifi, good_for_working_on_laptop | has_wifi | Connectivity |
| air_conditioning, has_air_conditioning | has_ac | Climate |
| garden | has_garden | Outdoor |
| electric_vehicle_charging_station, ev_charging | has_ev_charging | EV |
| allows_dogs, pets_allowed | hotel_pets_allowed | Hotel |
| pool | hotel_has_pool | Hotel |
| gym | hotel_has_gym | Hotel |
| spa | hotel_has_spa | Hotel |
| restaurant | hotel_has_restaurant | Hotel |
| bar | hotel_has_bar | Hotel |
| serves_breakfast, breakfast | hotel_has_breakfast | Hotel |
| free_breakfast | hotel_breakfast_included | Hotel |
| free_cancellation | hotel_free_cancellation | Hotel |

### 7.2 Nguồn 2: Google top-level booleans (`TOP_LEVEL_FIELD_MAPPING`)

| Google field (bool) | Internal field | Ghi chú |
| --- | --- | --- |
| reservable | fnb_reservable |  |
| takeout | fnb_takeaway |  |
| delivery | fnb_delivery |  |
| dineIn | fnb_dine_in |  |
| curbsidePickup | fnb_takeaway | OR-merge |
| outdoorSeating | has_outdoor_seating |  |
| liveMusic, servesBeer, servesWine, servesCocktails | fnb_serves_alcohol | OR-merge |
| servesBreakfast | hotel_has_breakfast |  |
| goodForGroups, goodForWatchingSports | fnb_good_for_groups | OR-merge |
| goodForChildren, menuForChildren | fnb_good_for_families | OR-merge |
| allowsDogs | hotel_pets_allowed |  |
| restroom | (ext_attribute only) | Không có schema field |

### 7.3 Nguồn 3: Nested objects

| Google object | Mapping rule | Internal fields |
| --- | --- | --- |
| parkingOptions | bất kỳ key nào true → has_parking=true; freeParkingLot/freeStreetParking/freeGarageParking → parking_is_free=true; paidParkingLot/paidStreetParking/paidGarageParking → parking_is_free=false | has_parking, parking_is_free |
| paymentOptions | acceptsCreditCards/acceptsDebitCards/acceptsNfc → payment_card=true; acceptsCashOnly → payment_cash=true, payment_card=false | payment_card, payment_cash |
| accessibilityOptions | bất kỳ key nào true → is_wheelchair_accessible=true | is_wheelchair_accessible |
