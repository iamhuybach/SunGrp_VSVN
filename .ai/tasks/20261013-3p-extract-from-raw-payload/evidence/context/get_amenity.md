<div>

# Amenities from google (gold layer for AI only)
### Bước 1 — Google Maps API trả về JSON lồng nhau (check file đính kèm)
Dữ liệu gốc có các boolean nằm **rải** **rác** ở nhiều chỗ khác nhau:

```
// Top-level (ngay ngoài cùng)
```

    "takeout": true,
    "delivery": true,
    "dineIn": true,
    "reservable": true,
    "servesBreakfast": true,
    "servesLunch": true,
    "servesDinner": true,
    "servesBeer": false,
    "servesVegetarianFood": true,
    "goodForChildren": true,
    "goodForGroups": true,
    "restroom": true,
    "outdoorSeating": false,
    // Nằm trong object con parkingOptions
    "parkingOptions": {
    "freeParkingLot": true,
    "freeStreetParking": true
    }
    // paymentOptions, accessibilityOptions → không có trong file này (Google không trả về)

------------------------------------------------------------------------
### Bước 2 — Làm phẳng + đổi tên sang snake_case (`_flat_google_booleans`)

Kéo tất cả ra ngoài, đổi tên camelCase → snake_case, ghi thẳng vào bản
ghi POI như các cột riêng lẻ:

<div>

|                           |                        |                                       |                           |
|---------------------------|------------------------|---------------------------------------|---------------------------|
| **Google field (gốc)**    | **Nằm** **ở**          | **Cột** **trong POI record**          | **Giá** **trị**           |
| `takeout`                 | top-level              | `takeout`                             | `true`                    |
| `delivery`                | top-level              | `delivery`                            | `true`                    |
| `dineIn`                  | top-level              | `dine_in`                             | `true`                    |
| `reservable`              | top-level              | `reservable`                          | `true`                    |
| `servesBreakfast`         | top-level              | `serves_breakfast`                    | `true`                    |
| `servesLunch`             | top-level              | `serves_lunch`                        | `true`                    |
| `servesDinner`            | top-level              | `serves_dinner`                       | `true`                    |
| `servesBeer`              | top-level              | `serves_beer`                         | `false`                   |
| `servesVegetarianFood`    | top-level              | `serves_vegetarian_food`              | `true`                    |
| `goodForChildren`         | top-level              | `good_for_children`                   | `true`                    |
| `goodForGroups`           | top-level              | `good_for_groups`                     | `true`                    |
| `restroom`                | top-level              | `has_restroom`                        | `true`                    |
| `outdoorSeating`          | top-level              | `outdoor_seating`                     | `false`                   |
| `freeParkingLot`          | `parkingOptions`       | `parking_options_free_parking_lot`    | `true`                    |
| `freeStreetParking`       | `parkingOptions`       | `parking_options_free_street_parking` | `true`                    |
| `wheelchairAccessible``*` | `accessibilityOptions` | `accessibility_options``_*`           | `null` (Google không trả) |


> Tất cả 38 cột đều được ghi vào POI record — `true`, `false`, hoặc
> `null` nếu Google không có dữ liệu.

------------------------------------------------------------------------

### Bước 3 — Xác định ngành (`detect_category`)

Script đọc `types` của POI:

```
"types": ["vegetarian_restaurant", "restaurant", "food", ...]
```

    "primaryType": "vegetarian_restaurant"

Tra vào `business_sector_rule.md` → khớp `restaurant` → **ngành**
`fnb`.

------------------------------------------------------------------------
### Bước 4 — Lọc theo ngành, chỉ giữ `True` → tạo `general_amenities` (`_build_general_amenities`)

Vì ngành là `fnb`, script lấy danh sách cột được phép cho F&B (từ
`_GENERAL_AMENITY_FIELDS_BY_SECTOR["fnb"]`), rồi chỉ giữ những cột có
giá trị `True`:
```
serves_beer = false → bỏ
```
    outdoor_seating = false → bỏ
    serves_vegetarian_food = true → GIỮ
    parking_options_free_parking_lot = true → GIỮ
    accessibility_options_* = null → bỏ (không có dữ liệu)
    ...

Kết quả:

```
"general_amenities": [
```

    "takeout",
    "delivery",
    "dine_in",
    "reservable",
    "serves_breakfast",
    "serves_lunch",
    "serves_dinner",
    "serves_vegetarian_food",
    "good_for_children",
    "has_restroom",
    "good_for_groups",
    "parking_options_free_parking_lot",
    "parking_options_free_street_parking"
    ]

------------------------------------------------------------------------

### Tóm tắt luồng

```
Google JSON (lồng nhau, camelCase)
```

    │

    ▼ _flat_google_booleans()
    38 cột boolean riêng lẻ trong POI record
    (true / false / null — ghi hết, không lọc)
    │
    ▼ detect_category() → "fnb"
    │
    ▼ _build_general_amenities(category="fnb", flat_bools)

    general_amenities = [chỉ những tag True, đúng ngành]

**Điểm** **khác biệt quan trọng:**

Các cột `parking_*` và `accessibility_*` → ghi vào record cho
**mọi** **ngành**
`general_amenities` → chỉ chứa tag `True`, loại bỏ
`False`/`null`, và chỉ lấy những field có nghĩa với ngành đó
`accessibility_options``_*` là ngoại lệ duy nhất: nếu Google
trả về `false` tường minh, sẽ emit tag dạng
`"accessibility_options_wheelchair_accessible_parking:false"` để phân
biệt với "không có dữ liệu"
