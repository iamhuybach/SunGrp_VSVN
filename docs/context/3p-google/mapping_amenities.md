#### **2.1 accomodation**

|                                |                                                                                                                                                                        |                                |                                |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|--------------------------------|
| **Partner Portal Enum**        | **Google Place API Field / Value**                                                                                                                                     | **Hiển** **thị (VI)**          | **Hiển** **thị (EN)**          |
| **general_amenities**          |                                                                                                                                                                        |                                |                                |
| Bổ sung sau                    | `parkingOptions.freeStreetParking = true`                                                                                                                            | Đỗ xe trên phố                 | Free Street Parking            |
| Bổ sung sau                    | `parkingOptions.valetParking = true`                                                                                                                                 | Dịch vụ Valet                  | Valet Parking                  |
| Bổ sung sau                    | `parkingOptions.freeGarageParking = true`                                                                                                                            | Bãi xe trong nhà (Miễn phí)    | Free Garage Parking            |
| Bổ sung sau                    | `parkingOptions.paidGarageParking = true`                                                                                                                            | Bãi xe trong nhà (Thu phí)     | Paid Garage Parking            |
| Bổ sung sau                    | `outdoorSeating = true`                                                                                                                                              | Không gian ngoài trời          | Outdoor Seating                |
| Bổ sung sau                    | `restroom = true`                                                                                                                                                      | Nhà vệ sinh                    | Restroom                       |
| Bổ sung sau                    | `goodForChildren = true`                                                                                                                                             | Thân thiện trẻ em              | Good for Children              |
| Bổ sung sau                    | `goodForGroups = true`                                                                                                                                               | Phù hợp đoàn nhóm              | Good for Groups                |
| Bổ sung sau                    | `liveMusic = true`                                                                                                                                                   | Nhạc Live                      | Live Music                     |
| Hồ bơi                         | types\[\] = `swimming_pool`                                                                                                                                            | Hồ bơi                         | Swimming Pool                  |
| Wi-Fi miễn phí                 | Không có field riêng                                                                                                                                                   | Wi-Fi miễn phí                 | Free Wi-Fi                     |
| Bãi đậu xe                     | `parkingOptions.freeParkingLot = true` hoặc `parkingOptions.paidParkingLot = true`                                                                                 | Bãi đậu xe                     | Parking                        |
| Xe đưa đón sân bay             | Không có field riêng                                                                                                                                                   | Xe đưa đón sân bay             | Airport Shuttle                |
| Nhà hàng                       | types\[\] có enum thuộc business_sector F&B hoặc `serves_meals = true`                                                                                               | Nhà hàng                       | Restaurant                     |
| Lễ tân 24h                     | Không có field riêng                                                                                                                                                   | Lễ tân 24h                     | 24-hour Front Desk             |
| Quầy bar                       | types\[\] có enum thuộc business_category = Bar & Pub/Nightlife `servesBeer = true` hoặc `servesCocktails = true`                                                  | Quầy bar                       | Bar                            |
| Spa & Wellness                 | types\[\] có enum thuộc business_category= Day Spa/Therapeutic Massage/Clinic-Aesthetic Spa/Hair Salon/Nail-Lash Salon/Beauty Salon/Barbershop                         | Spa & Wellness                 | Spa & Wellness                 |
| Phòng Gym                      | types\[\] có enum thuộc business_category= Gym-Fitness/Yoga-Pilates Studio                                                                                             | Phòng Gym                      | Gym                            |
| Xông hơi                       | types\[\] = `hot_spring`, `sauna`                                                                                                                                      | Xông hơi                       | Sauna                          |
| Bồn tắm nóng (Jacuzzi)         | Không có field riêng                                                                                                                                                   | Bồn tắm nóng                   | Jacuzzi                        |
| Sân vườn                       | types\[\] = `garden`, `botanical_garden`                                                                                                                               | Sân vườn                       | Garden                         |
| Phòng họp                      | types\[\] = `meeting_rooms`                                                                                                                                            | Phòng họp                      | Meeting Rooms                  |
| Khu vực làm việc chung         | Không có field riêng                                                                                                                                                   | Khu làm việc chung             | Co-working Space               |
| Giữ hành lý                    | Không có field riêng                                                                                                                                                   | Giữ hành lý                    | Luggage Storage                |
| Thu đổi ngoại tệ               | Không có field riêng                                                                                                                                                   | Thu đổi ngoại tệ               | Currency Exchange              |
| Trạm sạc xe điện               | `parkingOptions.freeElectricVehicleParking = true` hoặc `parkingOptions.paidElectricVehicleParking = true` hoặc `types[]` có `electric_vehicle_charging_station` | Trạm sạc xe điện               | EV Charging Station            |
| **accessibility**              |                                                                                                                                                                        |                                |                                |
| Bổ sung sau                    | `accessibilityOptions.wheelchairAccessibleSeating = true`                                                                                                            | Chỗ ngồi cho người khuyết tật  | Wheelchair Accessible Seating  |
| Bổ sung sau                    | `accessibilityOptions.wheelchairAccessibleElevator = true`                                                                                                           | Thang máy hỗ trợ xe lăn        | Wheelchair Accessible Elevator |
| Lối đi xe lăn                  | `accessibilityOptions.wheelchairAccessibleEntrance = true`                                                                                                           | Lối đi xe lăn                  | Wheelchair Accessible Entrance |
| Thang máy có chữ nổi           | Không có field riêng                                                                                                                                                   | Thang máy có chữ nổi           | Braille Elevator               |
| Nhà vệ sinh có tay vịn         | `accessibilityOptions.wheelchairAccessibleRestroom = true`                                                                                                           | Nhà vệ sinh có tay vịn         | Wheelchair Accessible Restroom |
| Bồn rửa mặt thấp               | Không có field riêng                                                                                                                                                   | Bồn rửa mặt thấp               | Lowered Sink                   |
| Bãi đỗ xe cho người khuyết tật | `accessibilityOptions.wheelchairAccessibleParking = true`                                                                                                            | Bãi đỗ xe cho người khuyết tật | Accessible Parking             |

#### **2.2 f_n_b**

|                         |                                                                           |                          |                       |     |
|-------------------------|---------------------------------------------------------------------------|--------------------------|-----------------------|-----|
| **Partner Portal Enum** | **Google Place API Field / Value**                                        | **Hiển** **thị (VI)**    | **Hiển** **thị (EN)** |     |
| **specialty_tags**      |                                                                           |                          |                       |     |
| Bổ sung sau             | `dim_sum_restaurant`                                                      | Dimsum                   | Dim Sum               |     |
| Bổ sung sau             | `sushi_restaurant`                                                        | Sushi                    | Sushi                 |     |
| Bổ sung sau             | `dumpling_restaurant`                                                     | Há cảo – Bánh bao        | Dumpling              |     |
| Bổ sung sau             | `tonkatsu_restaurant`                                                     | Tonkatsu                 | Tonkatsu              |     |
| Bổ sung sau             | `japanese_curry_restaurant`                                               | Cà ri Nhật               | Japanese Curry        |     |
| Bổ sung sau             | `cantonese_restaurant`                                                    | Ẩm thực Quảng Đông       | Cantonese             |     |
| Bổ sung sau             | `chinese_noodle_restaurant`                                               | Mì Trung Quốc            | Chinese Noodle        |     |
| Bổ sung sau             | `ramen_restaurant`                                                        | Ramen                    | Ramen                 |     |
| Bổ sung sau             | `yakiniku_restaurant`, `yakitori_restaurant`                              | Yakiniku / Teppanyaki    | Yakiniku / Teppanyaki |     |
| Bổ sung sau             | `japanese_izakaya_restaurant`                                             | Izakaya                  | Izakaya               |     |
| Bổ sung sau             | `korean_barbecue_restaurant`                                              | BBQ Hàn Quốc             | Korean BBQ            |     |
| Bổ sung sau             | `pizza_restaurant`                                                        | Pizza                    | Pizza                 |     |
| Bổ sung sau             | `hamburger_restaurant`                                                    | Hamburger                | Hamburger             |     |
| Bổ sung sau             | `brunch_restaurant`                                                       | Brunch                   | Brunch                |     |
| Bổ sung sau             | `cat_cafe`, `dog_cafe`                                                    | Quán cà phê thú cưng     | Pet Café              |     |
| Bổ sung sau             | `tapas_restaurant`                                                        | Tapas                    | Tapas                 |     |
| Bổ sung sau             | `soup_restaurant`                                                         | Súp                      | Soup                  |     |
| Street Food             | types\[\] = `food_stand`, `street_food_gathering`                         | Ẩm thực đường phố        | Street Food           |     |
| Seafood                 | types\[\] = `seafood_restaurant`, `oyster_bar_restaurant`                 | Hải sản                  | Seafood               |     |
| Steakhouse              | types\[\] = `steakhouse`                                                  | Bít tết                  | Steakhouse            |     |
| Office Lunch            | Không có field riêng                                                      | Cơm văn phòng            | Office Lunch          |     |
| Milk Tea                | Không có field riêng                                                      | Trà sữa                  | Milk Tea              |     |
| Bakery                  | types\[\] = `bakery`, `pastry_shop`, `cake_shop`                          | Tiệm bánh                | Bakery                |     |
| Bar-Pub                 | types\[\] thuộc business_category = Bar & Pub/Nightlife                   | Bar – Pub                | Bar & Pub             |     |
| Rooftop Bar             |                                                                           | Bar sân thượng           | Rooftop Bar           |     |
| **space_and_services**  |                                                                           |                          |                       |     |
| Bổ sung sau             | `restroom = true`                                                         | Nhà vệ sinh              | Restroom              |     |
| Bổ sung sau             | `goodForChildren = true`                                                | Thân thiện trẻ em        | Good for Children     |     |
| Outdoor Seating         | `outdoorSeating = true = true`                                          | Chỗ ngồi ngoài trời      | Outdoor Seating       |     |
| Private Room (VIP)      | Không có field riêng                                                      | Phòng riêng (VIP)        | Private Room (VIP)    |     |
| Scenic View             | Không có field riêng                                                      | Góc nhìn đẹp             | Scenic View           |     |
| Romantic Decor          | Không có field riêng                                                      | Trang trí lãng mạn       | Romantic Decor        |     |
| High Chair              | Không có field riêng                                                      | Có ghế trẻ em            | High Chair            |     |
| Wheelchair Accessible   | `accessibilityOptions.wheelchairAccessibleEntrance`= true                 | Lối đi xe lăn            | Wheelchair Accessible |     |
| Sports Screening        | `goodForWatchingSports = true`                                          | Chiếu thể thao trực tiếp | Sports Screening      |     |
| Live Music              | `liveMusic = true`                                                      | Nhạc sống                | Live Music            |     |
| Car Parking             | `parkingOptions.freeParkingLot`, `parkingOptions.paidParkingLot = true` | Bãi đỗ xe ô tô           | Car Parking           |     |
| Table Service           | dineIn = true                                                             | Phục vụ tại bàn          | Table Service         |     |

#### **2.3 attraction**

|                             |                                                                                         |                            |                                |
|-----------------------------|-----------------------------------------------------------------------------------------|----------------------------|--------------------------------|
| **Partner Portal Enum**     | **Google Place API Field / Value**                                                      | **Hiển** **thị (VI)**      | **Hiển** **thị (EN)**          |
| **facilities_and_services** |                                                                                         |                            |                                |
| Bổ sung sau                 | `accessibilityOptions.wheelchairAccessibleEntrance`                                     | Lối đi xe lăn              | Wheelchair Accessible Entrance |
| Bổ sung sau                 | `accessibilityOptions.wheelchairAccessibleParking`                                      | Bãi đỗ xe người khuyết tật | Accessible Parking             |
| Bổ sung sau                 | `accessibilityOptions.wheelchairAccessibleRestroom`                                     | Nhà vệ sinh xe lăn         | Wheelchair Accessible Restroom |
| Bổ sung sau                 | restroom                                                                                | Nhà vệ sinh                | Restroom                       |
| Bổ sung sau                 | goodForChildren                                                                         | Thân thiện trẻ em          | Good for Children              |
| Bổ sung sau                 | liveMusic                                                                               | Nhạc Live                  | Live Music                     |
| Indoor                      | Không có field riêng                                                                    | Trong nhà                  | Indoor                         |
| Outdoor                     | Không có field riêng                                                                    | Ngoài trời                 | Outdoor                        |
| Covered                     | Không có field riêng                                                                    | Có mái che                 | Covered                        |
| Family Friendly             | `goodForChildren`                                                                       | Thân thiện với gia đình    | Family Friendly                |
| Couples                     | Không có field riêng                                                                    | Cặp đôi                    | Couples                        |
| Group                       | `goodForGroups`                                                                         | Nhóm bạn                   | Group                          |
| History                     | types\[\] có enum thuộc business_category = Historical Site                             | Lịch sử                    | History                        |
| Art                         | `types[]` có `art_gallery`                                                            | Nghệ thuật                 | Art                            |
| Science                     | `types[]` có `planetarium`                                                            | Khoa học                   | Science                        |
| Interactive                 | Không có field riêng                                                                    | Tương tác                  | Interactive                    |
| Educational                 | Không có field riêng                                                                    | Giáo dục                   | Educational                    |
| Spiritual                   | `types[]` có business_category = Religious Site                                       | Tâm linh                   | Spiritual                      |
| **facilities_and_services** |                                                                                         |                            |                                |
| Parking                     | `parkingOptions.freeParkingLot = true`, hoặc `parkingOptions.paidParkingLot = true` | Bãi đậu xe                 | Parking                        |
| Free Wi-Fi                  | Không có field riêng                                                                    | Wi-Fi miễn phí             | Free Wi-Fi                     |
| Lockers                     | Không có field riêng                                                                    | Tủ gửi đồ                  | Lockers                        |
| Restaurant-Cafe             | `types[]` có `restaurant`, `cafe`, `coffee_shop`                                      | Nhà hàng – Quán ăn         | Restaurant-Cafe                |
| Gift Shop                   | `types[]` có `gift_shop`                                                              | Cửa hàng lưu niệm          | Gift Shop                      |
| Stroller Rental             | Không có field riêng                                                                    | Cho thuê xe đẩy trẻ em     | Stroller Rental                |
| Wheelchair Rental           | Không có field riêng                                                                    | Cho thuê xe lăn            | Wheelchair Rental              |
| First Aid Room              | Không có field riêng                                                                    | Phòng y tế                 | First Aid Room                 |
| On-site Tour Guide          | Không có field riêng                                                                    | Hướng dẫn viên tại điểm    | On-site Tour Guide             |
| Audio Guide                 | Không có field riêng                                                                    | Máy hướng dẫn tự động      | Audio Guide                    |

#### **2.4 shopping_n_retail**

|                             |                                                                  |                        |                           |
|-----------------------------|------------------------------------------------------------------|------------------------|---------------------------|
| **Partner Portal Enum**     | **Google Place API Field / Value**                               | **Hiển** **thị (VI)**  | **Hiển** **thị (EN)**     |
| **facilities_and_services** |                                                                  |                        |                           |
| Tax Refund                  | Không có field riêng                                             | Hoàn thuế              | Tax Refund                |
| Shipping-Delivery           | `delivery`                                                       | Giao hàng tận nơi      | Shipping-Delivery         |
| Gift Wrapping               | Không có field riêng                                             | Gói quà miễn phí       | Gift Wrapping             |
| Fitting Room                | Không có field riêng                                             | Phòng thử đồ           | Fitting Room              |
| Personalization-Engraving   | Không có field riêng                                             | Khắc tên – Cá nhân hóa | Personalization-Engraving |
| Tailoring                   | Không có field riêng                                             | May đo theo yêu cầu    | Tailoring                 |
| Credit Card (Visa/Master)   | `paymentOptions.acceptsCreditCards`                              | Chấp nhận thẻ tín dụng | Credit Card               |
| E-Wallet                    | Không có field riêng                                             | Ví điện tử             | E-Wallet                  |
| VAT Invoice                 | Không có field riêng                                             | Xuất hóa đơn VAT       | VAT Invoice               |
| Flexible Return             | Không có field riêng                                             | Đổi trả linh hoạt      | Flexible Return           |
| Parking                     | `parkingOptions.freeParkingLot`, `parkingOptions.paidParkingLot` | Bãi đỗ xe              | Parking                   |
| Free Wi-Fi                  | Không có field riêng                                             | Wi-Fi miễn phí         | Free Wi-Fi                |

#### **2.5 Tạo danh sách TRUE Amenity**

Insert thêm vào bảng `ref_dictionary_amenities`, các trường hợp nếu đã có trong `amenity_raw`, chỉ cần thêm vào tương ứng. Nếu chưa có, thêm vào và các fields `business_sector` là `other`, `amenity_group` là `other`, `amenity` = `amenity_raw` và `amenity_vi` = `amenity_raw`. Phần điều kiện tách thành từng dòng cho `place_type`:

| service_flags | amenity_raw |
|---|---|
| Food/service | takeout, delivery, dineIn, curbsidePickup, reservable, servesBreakfast, servesLunch, servesDinner, servesBeer, servesWine, servesBrunch, servesVegetarianFood, outdoorSeating, liveMusic, menuForChildren, servesCocktails, servesDessert, servesCoffee |
| Suitability | goodForChildren, allowsDogs, restroom, goodForGroups, goodForWatchingSports, pureServiceAreaBusiness |
| Payment | paymentOptions.acceptsCreditCards, acceptsDebitCards, acceptsNfc |
| Parking | parkingOptions.*; aggregate parking = true nếu có ít nhất một parking option bằng true |
| Accessibility | accessibilityOptions.wheelchairAccessibleParking, wheelchairAccessibleEntrance, wheelchairAccessibleRestroom, wheelchairAccessibleSeating |
| Derived amenities | Pool, gym, spa, sauna, garden, bar, restaurant, coworking và EV charging có thể được map từ Google fields hoặc relevant types[] theo approved rule |

Chỉ tên flag có giá trị `true` được đưa vào `service_flags`. Missing field không được xem là `true`.