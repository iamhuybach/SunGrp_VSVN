# Google Place Type → POI Amenity Group Mapping

Nguồn: sheet `Mapping_Multi` trong file Excel đính kèm.

> File gốc sử dụng trường `Candidate POI Amenity Group`; không có trường `sector` riêng trong sheet này.

| Google Place Type | Candidate POI Amenity Group | Display Name | Priority | Confidence | Candidate Type | Rationale |
| --- | --- | --- | --- | --- | --- | --- |
| academic_department | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Education |
| acai_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| accounting | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Finance |
| administrative_area_level_1 | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Geographical |
| administrative_area_level_2 | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Geographical |
| administrative_area_level_3 | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| administrative_area_level_4 | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| administrative_area_level_5 | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| administrative_area_level_6 | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| administrative_area_level_7 | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| adventure_sports_center | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| afghani_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| african_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| aircraft_rental_service | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 1 | 1 | PRIMARY | Manual override: transport on demand |
| airport | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| airstrip | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| american_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| amphitheatre | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| amusement_center | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| amusement_park | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| apartment_building | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Housing |
| apartment_complex | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Housing |
| aquarium | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| archipelago | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Destination-scale geography tag; useful for place taxonomy, not POI amenity. |
| arena | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| argentinian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| art_gallery | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| art_museum | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| art_studio | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| asian_fusion_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| asian_grocery_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| asian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| association_or_organization | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| astrologer | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| athletic_field | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| atm | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Finance |
| auditorium | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Section default: Culture |
| australian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| austrian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| auto_parts_store | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Shopping |
| bagel_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| bakery | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| bakery | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 2 | 0.5 | SECONDARY | Retail baked goods signal secondary to F&B. |
| bangladeshi_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| bank | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Finance |
| banquet_hall | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| bar | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| bar_and_grill | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| barbecue_area | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| barbecue_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| barber_shop | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| basque_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| bavarian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| beach | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Natural |
| beach | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 2 | 0.65 | SECONDARY | Beach activities signal secondary to attraction classification. |
| beautician | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| beauty_salon | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| bed_and_breakfast | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| beer_garden | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| belgian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| bicycle_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| bike_sharing_station | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 1 | 1 | PRIMARY | Manual override: transport on demand |
| bistro | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| body_art_service | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| book_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| botanical_garden | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| bowling_alley | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| brazilian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| breakfast_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| brewery | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| brewpub | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| bridge | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| british_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| brunch_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| buddhist_temple | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Places |
| budget_japanese_inn | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| buffet_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| building_materials_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| burmese_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| burrito_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| bus_station | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| bus_stop | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| business_center | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Business |
| butcher_shop | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| cafe | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| cafeteria | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| cajun_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| cake_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| californian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| cambodian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| campground | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| camping_cabin | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| candy_store | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| cantonese_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| car_dealer | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| car_rental | AMENITIES_VEHICLE_RENTAL | Vehicle Rental | 1 | 1 | PRIMARY | Manual override: vehicle rental priority |
| car_rental | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 2 | 0.65 | SECONDARY | Can also be interpreted as mobility/on-demand access, but primary remains Vehicle Rental. |
| car_repair | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| car_wash | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| caribbean_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| casino | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| castle | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| cat_cafe | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| catering_service | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Keyword / business-intent override |
| cell_phone_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| cemetery | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| chauffeur_service | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 1 | 1 | PRIMARY | Manual override: transport on demand |
| chicken_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| chicken_wings_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| child_care_agency | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| childrens_camp | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| chilean_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| chinese_noodle_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| chinese_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| chiropractor | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| chocolate_factory | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| chocolate_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| church | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Places |
| city_hall | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Government |
| city_park | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| clothing_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| cocktail_bar | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| coffee_roastery | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| coffee_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| coffee_shop | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 2 | 0.4 | SECONDARY | Packaged coffee retail signal secondary to F&B. |
| coffee_stand | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| colloquial_area | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| colombian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| comedy_club | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| community_center | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| concert_hall | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| condominium_complex | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Housing |
| confectionery | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| consultant | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| continent | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| convenience_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| convenience_store | AMENITIES_F&B | F&B | 2 | 0.45 | SECONDARY | Can include ready-to-eat food signal secondary to retail. |
| convention_center | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| corporate_office | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Business |
| cosmetics_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| cottage | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| country | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Geographical |
| courier_service | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| courthouse | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Government |
| coworking_space | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Business |
| croatian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| cuban_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| cultural_center | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| cultural_landmark | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| cycling_park | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| czech_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| dance_hall | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| danish_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| deli | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| dental_clinic | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| dentist | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| department_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| dessert_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| dessert_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| dim_sum_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| diner | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| discount_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| discount_supermarket | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| doctor | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| dog_cafe | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| dog_park | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| donut_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| drugstore | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| drugstore | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 2 | 0.55 | SECONDARY | Retail commerce interpretation secondary to wellness/health grouping. |
| dumpling_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| dutch_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| eastern_european_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| ebike_charging_station | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| ebike_charging_station | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 2 | 0.6 | SECONDARY | Micromobility support signal; primary remains transport route/base. |
| educational_institution | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Education |
| electric_vehicle_charging_station | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| electric_vehicle_charging_station | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 2 | 0.55 | SECONDARY | Supports trip/mobility operations; primary remains transport route/base. |
| electrician | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| electronics_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| embassy | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Government |
| employment_agency | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| establishment | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Very generic Google response tag; too broad to infer a specific amenity group. |
| ethiopian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| european_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| event_venue | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| extended_stay_hotel | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| falafel_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| family_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| farm | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Business |
| farmers_market | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| farmstay | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| fast_food_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| ferris_wheel | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| ferry_service | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| ferry_terminal | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| filipino_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| finance | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Generic finance tag; rely on specific Table A finance types (bank, atm, etc.) for amenity mapping. |
| fine_dining_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| fire_station | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Government |
| fish_and_chips_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| fishing_charter | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| fishing_pier | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| fishing_pond | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| fitness_center | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| flea_market | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| florist | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| fondue_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| food | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Generic food-domain tag; map to F&B when no more specific food/drink Table A type is present. |
| food_court | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| food_delivery | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Keyword / business-intent override |
| food_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| foot_care | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| fountain | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| french_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| funeral_home | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| furniture_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| fusion_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| garden | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| garden_center | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| gas_station | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| gastropub | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| general_contractor | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Business/service contractor tag; not one of the 11 consumer-facing amenity groups. |
| general_hospital | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| general_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| geocode | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| german_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| gift_shop | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| go_karting_venue | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| golf_course | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| government_office | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Government |
| greek_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| grocery_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| guest_house | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| gym | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| gyro_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| hair_care | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| hair_salon | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| halal_restaurant* | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| hamburger_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| hardware_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| hawaiian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| health | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Generic health-domain tag; map to Spa & Wellness when no more specific health/wellness Table A type is present. |
| health_food_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| heliport | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| hiking_area | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| hindu_temple | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Places |
| historical_landmark | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| historical_place | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| history_museum | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| home_goods_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| home_improvement_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| hookah_bar | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| hospital | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| hostel | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| hot_dog_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| hot_dog_stand | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| hot_pot_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| hotel | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| housing_complex | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Housing |
| hungarian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| hypermarket | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| ice_cream_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| ice_skating_rink | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| indian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| indonesian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| indoor_golf_course | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| indoor_playground | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| inn | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| insurance_agency | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| international_airport | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| internet_cafe | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| intersection | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| irish_pub | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| irish_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| island | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Natural |
| israeli_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| italian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| japanese_curry_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| japanese_inn | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| japanese_izakaya_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| japanese_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| jewelry_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| juice_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| karaoke | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| kebab_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| korean_barbecue_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| korean_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| lake | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Natural |
| landmark | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Response type still conveys visitor-facing attraction character; map to Attraction when it is the strongest available signal. |
| landmark | AMENITIES_EVENT | Event | 2 | 0.2 | FALLBACK | Only as a weak fallback when landmark is event-oriented; keep Attraction primary. |
| latin_american_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| laundry | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| lawyer | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| lebanese_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| library | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Education |
| light_rail_station | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| liquor_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| live_music_venue | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| local_government_office | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Government |
| locality | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Geographical |
| locksmith | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| lodging | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| lounge_bar | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| makeup_artist | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| malaysian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| manufacturer | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Business |
| marina | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| marina | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 2 | 0.55 | SECONDARY | Can be a boat tour / activity hub. |
| market | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| marketing_consultant | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| massage | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| massage_spa | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| meal_delivery | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| meal_takeaway | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| medical_center | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| medical_clinic | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| medical_lab | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| mediterranean_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| mexican_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| middle_eastern_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| miniature_golf_course | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| mobile_home_park | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| mongolian_barbecue_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| monument | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| moroccan_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| mosque | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Places |
| motel | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| mountain_peak | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Natural |
| movie_rental | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| movie_theater | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| movie_theater | AMENITIES_ATTRACTION | Attraction | 2 | 0.6 | SECONDARY | Entertainment attraction secondary to event/venue interpretation. |
| moving_company | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| museum | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| nail_salon | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Keyword / business-intent override |
| national_park | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| national_park | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 2 | 0.7 | SECONDARY | Outdoor activity hub secondary to attraction classification. |
| natural_feature | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Response type still conveys visitor-facing attraction character; map to Attraction when it is the strongest available signal. |
| nature_preserve | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Natural |
| neighborhood | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| neighborhood_police_station | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Government |
| night_club | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| night_club | AMENITIES_EVENT | Event | 2 | 0.55 | SECONDARY | Can function as live venue / event space secondary to F&B. |
| non_profit_organization | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| noodle_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| north_indian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| observation_deck | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| off_roading_area | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| opera_house | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| oyster_bar_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| paintball_center | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| painter | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| pakistani_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| park | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| park | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 2 | 0.5 | SECONDARY | Outdoor leisure / activity cluster secondary to attraction classification. |
| park_and_ride | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| parking | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| parking | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 2 | 0.4 | SECONDARY | Mobility support facility; primary remains route/base transport infrastructure. |
| parking_garage | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| parking_garage | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 2 | 0.4 | SECONDARY | Mobility support facility; primary remains route/base transport infrastructure. |
| parking_lot | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| parking_lot | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 2 | 0.4 | SECONDARY | Mobility support facility; primary remains route/base transport infrastructure. |
| pastry_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| performing_arts_theater | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Section default: Culture |
| performing_arts_theater | AMENITIES_EVENT | Event | 2 | 0.6 | SECONDARY | Scheduled shows and performances can be modeled as event venues. |
| persian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| peruvian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| pet_boarding_service | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| pet_care | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| pet_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| pharmacy | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| pharmacy | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 2 | 0.55 | SECONDARY | Retail commerce interpretation secondary to wellness/health grouping. |
| philharmonic_hall | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| physiotherapist | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| picnic_ground | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| pizza_delivery | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| pizza_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| place_of_worship | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Response type still conveys visitor-facing attraction character; map to Attraction when it is the strongest available signal. |
| place_of_worship | AMENITIES_OTHER | Other | 2 | 0.2 | FALLBACK | Only if downstream wants non-attraction fallback; keep Attraction primary. |
| planetarium | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| playground | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| plaza | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| plumber | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| plus_code | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| point_of_interest | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Very generic Google response tag; too broad to infer a specific amenity group. |
| police | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Government |
| polish_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| political | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| portuguese_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| post_office | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Government |
| postal_code | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Geographical |
| postal_code_prefix | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| postal_code_suffix | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| postal_town | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| premise | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| preschool | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Education |
| primary_school | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Education |
| private_guest_room | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| psychic | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| pub | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| public_bath | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Facilities |
| public_bathroom | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Facilities |
| race_course | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| ramen_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| ranch | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Business |
| real_estate_agency | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| research_institute | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Education |
| resort_hotel | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| rest_stop | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| rest_stop | AMENITIES_OTHER | Other | 2 | 0.45 | SECONDARY | Can behave like a general roadside facility cluster; primary remains transport route/base. |
| restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| river | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Natural |
| roller_coaster | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| romanian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| roofing_contractor | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| route | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| russian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| rv_park | AMENITIES_ACCOMMODATION | Accommodation | 1 | 1 | PRIMARY | Section default: Lodging |
| salad_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| sandwich_shop | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| sauna | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| scandinavian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| scenic_spot | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Natural |
| school | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Education |
| school_district | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Geographical |
| sculpture | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Culture |
| seafood_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| secondary_school | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Education |
| service | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| shawarma_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| shinto_shrine | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Places |
| shipping_service | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| shoe_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| shopping_mall | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| skateboard_park | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| ski_resort | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| skin_care_clinic | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| snack_bar | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| soul_food_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| soup_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| south_american_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| south_indian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| southwestern_us_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| spa | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| spanish_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| sporting_goods_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| sports_activity_location | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| sports_bar | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| sports_club | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| sports_coaching | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| sports_complex | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| sports_school | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| sportswear_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| sri_lankan_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| stable | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Facilities |
| stadium | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| stadium | AMENITIES_ATTRACTION | Attraction | 2 | 0.55 | SECONDARY | Can be a visitor attraction secondary to event venue classification. |
| state_park | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| steak_house | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| storage | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| street_address | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| sublocality | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| sublocality_level_1 | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| sublocality_level_2 | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| sublocality_level_3 | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| sublocality_level_4 | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| sublocality_level_5 | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| subpremise | AMENITIES_OTHER | Other | 1 | 0.25 | FALLBACK | Response/address geography tag in Google Table B; not a user-facing amenity, fallback to Other only if a group is required. |
| subway_station | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| summer_camp_organizer | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| supermarket | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| supplier | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Business |
| sushi_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| swimming_pool | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| swiss_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| synagogue | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Places |
| taco_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| tailor | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| taiwanese_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| tanning_studio | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| tapas_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| taxi_service | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 1 | 1 | PRIMARY | Manual override: transport on demand |
| taxi_stand | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 1 | 1 | PRIMARY | Manual override: transport on demand |
| tea_house | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| tea_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| telecommunications_service_provider | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| television_studio | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Business |
| tennis_court | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| tex_mex_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| thai_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| thrift_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| tibetan_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| tire_shop | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| toll_station | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| tonkatsu_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| tour_agency | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| tourist_attraction | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| tourist_attraction | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 2 | 0.6 | SECONDARY | Often sold or surfaced as an activity destination. |
| tourist_information_center | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| town_square | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Response type still conveys visitor-facing attraction character; map to Attraction when it is the strongest available signal. |
| town_square | AMENITIES_EVENT | Event | 2 | 0.45 | SECONDARY | Can operate as a civic event space secondary to attraction. |
| toy_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| train_station | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| train_ticket_office | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| tram_stop | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| transit_depot | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| transit_station | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| transit_stop | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| transportation_service | AMENITIES_TRANSPORT_ON_DEMAND | Transport On Demand | 1 | 1 | PRIMARY | Manual override: transport on demand |
| travel_agency | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| truck_dealer | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| truck_stop | AMENITIES_TRANSPORT_ROUTE_BASE | Transport Route Base | 1 | 1 | PRIMARY | Manual override: transport route base |
| turkish_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| ukrainian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| university | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Section default: Education |
| vegan_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| vegetarian_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| veterinary_care | AMENITIES_OTHER | Other | 1 | 1 | PRIMARY | Keyword / business-intent override |
| video_arcade | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| vietnamese_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| vineyard | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| visitor_center | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| visitor_center | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 2 | 0.7 | SECONDARY | Often acts as trip-planning / tour support facility. |
| warehouse_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| water_park | AMENITIES_TOUR_ACTIVITIES | Tour & Activities | 1 | 1 | PRIMARY | Keyword / business-intent override |
| wedding_venue | AMENITIES_EVENT | Event | 1 | 1 | PRIMARY | Keyword / business-intent override |
| wellness_center | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| western_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| wholesaler | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| wildlife_park | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| wildlife_refuge | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
| wine_bar | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| winery | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| womens_clothing_store | AMENITIES_SHOPPING_RETAIL | Shopping & Retail | 1 | 1 | PRIMARY | Section default: Shopping |
| woods | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Section default: Natural |
| yakiniku_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| yakitori_restaurant | AMENITIES_F&B | F&B | 1 | 1 | PRIMARY | Section default: Food |
| yoga_studio | AMENITIES_SPA_WELLNESS | Spa & Wellness | 1 | 1 | PRIMARY | Section default: Health |
| zoo | AMENITIES_ATTRACTION | Attraction | 1 | 1 | PRIMARY | Keyword / business-intent override |
