# Mapping Legacy Product: `ai_product`

Nguồn đọc: `notebooks_lgc/pl_transform_partner_userprofile_cms/5. nb_prepare_product_for_ingestion.ipynb` (source các cell 0–20). Sample "Sau" lấy từ output đã lưu của cell 17 (`select * from lh_vv_gold.dbo.ai_product`, lần chạy 2026-09-07, 20 dòng hiển thị). Sample "Trước" là minh họa dạng dữ liệu theo code, không phải dữ liệu bronze thật. Chỗ nào ghi `<...>` là giá trị không có trong notebook.

## 1. Table: `ai_product`

Lakehouse.schema: `lh_vv_gold.dbo`. Nguồn: `lh_vv_bronze.partner.*`.

### 1.1. Xử lý

- Grain đích: một dòng cho một `product_id`. Variant lồng trong `variants_json`.
- Ghi `overwrite` toàn bảng, `overwriteSchema = true`. Không MERGE, không watermark đọc. Bảng ghi đúng 25 cột theo `ORDERED` (cell 16).
- Hai domain:
  - Holiday (`product_type = 'other'`): luôn build, từ `products`, `product_variants`, `product_posts` và các bảng label/translation.
  - Hotel (`product_type = 'hotel'`): chỉ khi `ENABLE_HOTEL = True`. Mặc định `False`. Xem mục 1.6.
- Tham số mặc định trong cell 1: `LOCALE = 'vi'`, `ENABLE_TRANSLATION = False`, `ENABLE_HOTEL = False`, `TEST_MODE = False`, `REQUIRE_ACTIVE_POST_FOR_DIFF = False`, `HIDE_EXPIRED_USE_DATE = True`, `PRICE_DECIMAL_SCALE = 4`, `MARKUP_DECIMAL_SCALE = 2`.
- Bảng bronze đọc, tất cả qua `read_src` (`lh_vv_bronze.partner.<table>`), không lọc bản ghi CDC, không dedup theo `id`:

| Bảng bronze | Dùng cho |
|---|---|
| `products` | Thông tin product, `metadata` (post id, ngày) |
| `product_translations` | `name`, `description` theo `locale = 'vi'` |
| `product_variants` | Variant, `attributes`, `status`, xoá mềm |
| `product_variant_translations` | Tên variant theo `locale = 'vi'` |
| `product_attributes` + `product_attribute_translations` | `code` → tên thuộc tính tiếng Việt |
| `product_attribute_values` + `product_attribute_value_translations` | `value_code` → giá trị tiếng Việt. Khoá join là cột `attribute_id` của bảng translation, tham chiếu `product_attribute_values.id` |
| `product_business_service_relation` | `product_id` → `business_service_id` |
| `product_posts` | Giá, markup, `raw_sync_data` (mô tả ngắn, tags) |
| `hotel_room_types`, `hotel_rate_plans` | Chỉ khi `ENABLE_HOTEL` |

- Bảng gold đọc thêm: `lh_vv_gold.dbo.ai_poi` (lấy `destination_id`), `lh_vv_gold.dbo.ai_enriched_poi` (lọc `source_id`), `lh_vv_gold.dbo.ai_product_translation` (cache dịch, đọc và append).
- Cột không có trong bronze thì `optcol` trả NULL có kiểu. Cột JSON lưu dạng struct thì `json_text` gọi `to_json`; lưu dạng string thì giữ nguyên.
- Xoá mềm (`soft_deleted`, áp cho `products`, `product_variants`, `hotel_room_types`, `hotel_rate_plans`): xoá khi cột `deleted` là `1`/`true`, hoặc `deleted_at` khác NULL và đã ở quá khứ. `deleted_at` ở tương lai thì chưa xoá. Epoch không rõ đơn vị được quy về giây theo độ lớn (mục 1.5). `product_posts` dùng rule khác: `is_deleted_post = deleted_at IS NOT NULL`, không xét quá khứ/tương lai.
- Thứ tự build holiday:
  1. Variant join `product_variant_translations` (`variant_id`), thuộc tính đã resolve (`variant_id`), `products` (`product_id`), `product_translations` (`product_id`), relation (`product_id`), rollup (`product_id`), `product_posts` (`products.metadata.holiday_product_post_id = product_posts.external_id`). Tất cả LEFT JOIN.
  2. Product có hơn một `business_service_id` khác nhau trong relation bị loại hẳn (`left_anti`), trước khi fallback sang post.
  3. Gom về grain product: `variants_json = to_json(collect_list(struct))`. Cột cấp product lấy `first(..., ignorenulls=True)` trên các dòng variant.
  4. `source_id` = `business_service_id` (relation, rồi `product_posts.business_service_id`), cast string.
  5. `destination_id` lấy từ `ai_poi.destination_id` theo `ai_poi.source_id = source_id` (dedup `source_id` bằng `dropDuplicates`), rồi remap `DESTINATION_ID_REMAP`, rồi fallback Đà Nẵng.
  6. Bỏ dòng `source_id` NULL hoặc `destination_id` NULL.
  7. Giữ dòng có `source_id` trong `ai_enriched_poi.source_id` (`left_semi`). `TEST_MODE = True` thì không lọc, chỉ in.
- Product không có dòng nào trong `product_variants` thì không có dòng đích (build bắt đầu từ variant).
- Product đã xoá mềm vẫn được ghi, với `is_active = false`. Notebook không lọc product theo trạng thái.
- Variant đã xoá mềm vẫn nằm trong `variants_json`. Chỉ `variant_count`, `active_variant_count`, các cột axis và `use_date` bỏ variant đã xoá.
- `TEST_MODE = True`: mọi `source_id` = `FORCE_PRODUCT_SOURCE_ID`, mọi `destination_id` = `FORCE_PRODUCT_DESTINATION_ID`.
- `source_id` ở đây là `business_service_id` thô của partner, chưa hash. Trong VSVN mới, `poi_id` partner = `uuid_md5(business_service_id, 'partner')` (AGENTS.md §7). Khi map sang bảng mới phải tính lại khóa này.

### 1.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_variants.product_id | string | transform 1-1, khóa group | product_id |
| ai_product_translation.product_name_en, rồi product_translations.name, rồi product_id | string | `coalesce(product_name_en, product_name_vi, product_id)`. `ENABLE_TRANSLATION = False` thì `product_name_en` = tên tiếng Việt (mục 1.7) | name |
| | string | hằng `'en'` | lang |
| | string | hằng `'other'` (holiday), `'hotel'` (hotel) | product_type |
| products.status, products.deleted_at, products.deleted | boolean | `status = 'active' AND NOT is_deleted_product` | is_active |
| is_active, rollup variant, use_date, post | boolean | Mục 1.3 | is_bookable |
| products.product_line | string | transform 1-1. Hotel: hằng `'accommodation'` | product_line |
| product_posts.marketing_price, original_price | int | Bậc theo `coalesce(marketing_price, original_price)`: ≤ 500000 → 1, ≤ 2000000 → 2, ≤ 5000000 → 3, còn lại 4. NULL → 0 | price_level |
| product_posts.original_price | double | Giải mã CDC decimal scale 4 (mục 1.4). NULL → 0 | original_price |
| product_posts.marketing_price | double | Giải mã CDC decimal scale 4. NULL → 0 | marketing_price |
| product_posts.markup_percent | double | Giải mã CDC decimal scale 2. NULL → 0 | markup_percent |
| product_variants | long | `count(*)` variant chưa xoá mềm theo `product_id`. Không có thì NULL (holiday) | variant_count |
| product_variants.status | long | Số variant chưa xoá có `status = 'active'` | active_variant_count |
| product_variants, product_variant_translations, thuộc tính đã resolve | string | Mảng JSON `{variant_id, name, status, attributes}` (mục 1.8) | variants_json |
| product_variants.attributes | string | Axis `variant_tickets` (mục 1.9). `to_json(array)` | variant_tickets |
| product_variants.attributes | string | Axis `variant_dates` | variant_dates |
| product_variants.attributes | string | Axis `variant_hotels` | variant_hotels |
| product_variants.attributes | string | Axis `variant_age_groups` (gồm `quantity` và `age_group`) | variant_age_groups |
| product_variants.attributes | string | Axis `variant_room_types` (từ `zone`). Hotel: NULL | variant_room_types |
| product_variants.attributes | string | Axis `variant_departures` | variant_departures |
| product_variants.status | string | `to_json(collect_set(status))` của variant chưa xoá | variant_statuses |
| product_posts.raw_sync_data, price_level, is_active | string | JSON `{shortDescription, tags, priceLevel, isActive}` (mục 1.10). Hotel: JSON phòng (mục 1.6) | product_attributes |
| product_business_service_relation.business_service_id, rồi product_posts.business_service_id | string | Relation có đúng một id thì lấy id đó; không có relation thì lấy post; hơn một id thì loại product. Cast string. `TEST_MODE`: hằng | source_id |
| ai_poi.destination_id | string | Join theo `source_id`, remap, fallback Đà Nẵng (mục 1.11). `TEST_MODE`: hằng | destination_id |
| products.updated_at | timestamp | Epoch quy về giây (mục 1.5), cast timestamp. Hotel: `current_timestamp()` | updated_at |

Cột trung gian không ghi ra bảng: `variant_external_id`, `variant_metadata_json`, `product_external_id`, `product_attributes_json`, `product_metadata_json`, `main_attribute_code`, `product_start_date`, `product_end_date`, `product_description_vi`, `thumbnail_url`, `gallery_json`, `validity_from`, `validity_to`, `post_title_vi`, `business_service_id`. Markdown cell 0 liệt kê các cột này nhưng `ORDERED` bỏ chúng.

### 1.3. `is_active` và `is_bookable`

```text
is_active   = products.status = 'active' AND NOT is_deleted_product
is_bookable = is_active
              AND use_date_gate
              AND active_variant_count > 0
              AND diff_post_gate
```

- `use_date_gate` (`HIDE_EXPIRED_USE_DATE = True`): product không có variant `use_date` thì `true`. Có thì `max(use_date) >= current_date()`. `use_date` parse bằng `to_date(value_name_vi)` dạng `yyyy-MM-dd`. Parse lỗi thành NULL, không tính vào max. Có `use_date` nhưng max NULL thì `false`.
- `diff_post_gate`: `REQUIRE_ACTIVE_POST_FOR_DIFF = False` nên luôn `true`. Khi bật: product có `diff` trong tên tiếng Việt hoặc `post_title_vi` (đã bỏ dấu, lowercase) phải có post `status = 'active'` và `deleted_at` NULL.

Sample (output 2026-09-07, `current_date` = 2026-09-07):

| product_id | name | variant_dates | is_active | is_bookable | Lý do |
|---|---|---|---|---|---|
| 6cefb942-… | DIFF Night 4 - 20/6 (Germany - Macau) | `["2026-06-20"]` | true | false | `use_date` đã qua |
| 16d4e029-… | DA NANG ADULT*_CABLE CAR&BUFFET 4SEASONS | NULL | true | true | Không có `use_date`, có variant active |

### 1.4. CDC Decimal Transform

**Source Field:** `product_posts.original_price`, `product_posts.marketing_price` (scale 4), `product_posts.markup_percent` (scale 2)

**Target:** `double`

Thứ tự thử:

1. NULL hoặc boolean → NULL.
2. Số (`int`/`float`) → giữ nguyên.
3. Chuỗi parse được bằng `float()` → dùng giá trị đó.
4. Còn lại: bytes, hoặc base64 decode ra bytes, đọc integer big-endian có dấu, chia `10^scale`.
5. Decode lỗi hoặc rỗng → NULL.

| Trước | Scale | Sau |
|---|---|---|
| `"dzWUAA=="` (unscaled 2000000000) | 4 | `200000.0` |
| `"B9A="` (unscaled 2000) | 2 | `20.0` |
| `"1000000.0000"` | 4 | `1000000.0` |
| `null` | 4 | `null`, rồi `0.0` ở bước default |

### 1.5. Epoch Transform

Áp cho `deleted_at` (rule xoá mềm) và `products.updated_at` (cột `updated_at`). Đơn vị epoch suy từ độ lớn:

| Giá trị | Coi là | Chia |
|---|---|---|
| ≥ 1e17 | nano giây | 1e9 |
| ≥ 1e14 | micro giây | 1e6 |
| ≥ 1e11 | mili giây | 1e3 |
| còn lại | giây | 1 |

Ví dụ minh họa: `1757244351000` → `1757244351` giây → `2025-09-07T11:25:51Z`.

### 1.6. Hotel (`ENABLE_HOTEL = True`)

Một dòng cho một `hotel_room_types.id`. Rate plan gắn theo khách sạn, nên mọi phòng cùng `business_service_id` nhận cùng danh sách rate plan.

| Source Field | Transform | Target Field |
|---|---|---|
| hotel_room_types.id | 1-1 | product_id |
| hotel_room_types.name | Dịch qua cache như holiday, rồi `coalesce(en, vi, product_id)` | name |
| | `'hotel'` | product_type |
| hotel_room_types.status, xoá mềm | `status = 'Active' AND NOT deleted` (chữ `A` hoa) | is_active |
| is_active, business_service_id, available_rooms | `is_active AND business_service_id IS NOT NULL AND coalesce(available_rooms, 0) > 0`. Không xét rate plan, không xét `use_date` | is_bookable |
| | `'accommodation'` | product_line |
| | NULL → `0` | price_level, original_price, marketing_price, markup_percent |
| hotel_rate_plans | `count(*)` rate plan chưa xoá theo khách sạn, NULL → 0 | variant_count |
| hotel_rate_plans.status | Số rate plan chưa xoá có `status = 'Active'` | active_variant_count |
| hotel_rate_plans | Mảng JSON rate plan chưa xoá, không có thì `[]` | variants_json |
| | NULL | variant_tickets … variant_statuses |
| hotel_room_types | JSON phòng, xem dưới | product_attributes |
| hotel_room_types.business_service_id | Như holiday (mục 1.11) | source_id, destination_id |
| | `current_timestamp()` | updated_at |

`meal_plan`: `0` Room only, `1` Breakfast, `2` Half board, `3` Full board, `4` All inclusive; mã khác giữ nguyên. `view_type` = `'NULL'` hoặc rỗng thì NULL.

Ví dụ minh họa (không có output hotel trong notebook):

```json
// variants_json
[
  {
    "variant_id": "<hotel_rate_plans.id>",
    "name": "<hotel_rate_plans.name, NULL thì id>",
    "status": "Active",
    "attributes": {
      "meal_plan": "Breakfast",
      "kind": "<kind>",
      "valid_from": "<epoch string>",
      "valid_to": "<epoch string>",
      "include_tax": "true",
      "include_service_charge": "false"
    }
  }
]

// product_attributes
{
  "shortDescription": "<hotel_room_types.description>",
  "tags": ["<tag>"],
  "priceLevel": null,
  "isActive": true,
  "maxOccupancy": 3,
  "adultCapacity": 2,
  "childCapacity": 1,
  "maxExtraBed": 1,
  "roomSize": 32,
  "viewType": "<view_type>",
  "amenities": ["<amenityName>"],
  "availableRooms": 5,
  "totalRooms": 10
}
```

Hotel `priceLevel` trong `product_attributes` là NULL (dựng sẵn trước bước default 0). Holiday `priceLevel` là giá trị đã default.

### 1.7. Translation

- Cache `lh_vv_gold.dbo.ai_product_translation` (`product_id`, `product_name_vi`, `product_name_en`, `updated_at`). Chỉ `product_id` chưa có trong cache mới được xử lý, rồi append.
- `ENABLE_TRANSLATION = True` và có `AZURE_AI_API_KEY`: gọi Azure OpenAI `gpt-4.1`, lô 20 tên. Lỗi thì dùng tên tiếng Việt và vẫn ghi cache.
- `ENABLE_TRANSLATION = False` (mặc định): ghi tên tiếng Việt làm `product_name_en`.
- Cache theo `product_id`. Đổi tên tiếng Việt sau đó không dịch lại.
- Output lần chạy 2026-09-07: cache 236 dòng, 0 `product_id` mới.

### 1.8. `variants_json` Transform

**Source:** `product_variants` (`id`, `status`, `attributes`), `product_variant_translations.name` (`locale = 'vi'`), label thuộc tính.

Mỗi phần tử:

| Key | Lấy từ |
|---|---|
| `variant_id` | `product_variants.id` |
| `name` | `product_variant_translations.name` (`vi`). Không có thì NULL |
| `status` | `product_variants.status` |
| `attributes` | Map `attr_name_en → value_name_vi`. Không có thuộc tính thì `{}` |

Resolve `attributes`:

1. `from_json(product_variants.attributes, map<string,string>)`, explode thành (`attr_code`, `value_code`).
2. `attr_name_en` theo bảng dưới. Code không có trong bảng thì lấy phần sau dấu `:` cuối.
3. `value_name_vi` = `product_attribute_value_translations.name` (`vi`) theo `value_code`. Không có translation thì NULL.
4. Hai code ra cùng `attr_name_en` thì giữ cái sau (`mapKeyDedupPolicy = LAST_WIN`).

| `attr_code` | `attr_name_en` | Axis |
|---|---|---|
| `holiday:swticket` | `ticket` | `variant_tickets` |
| `holiday:use_date` | `use_date` | `variant_dates` |
| `holiday:hotel` | `hotel` | `variant_hotels` |
| `holiday:quantity` | `quantity` | `variant_age_groups` |
| `holiday:age_group` | `age_group` | `variant_age_groups` |
| `holiday:zone` | `zone` | `variant_room_types` |
| `holiday:depature` | `departure` | `variant_departures` |
| `holiday:customer_object` | `customer_type` | không có axis |
| khác, ví dụ `holiday:region` | phần sau `:` (`region`) | không có axis |

**Trước** (minh họa dạng nguồn):

```json
// product_variants.attributes
{"holiday:swticket": "<value_code>", "holiday:use_date": "<value_code>"}

// product_variant_translations (locale = 'vi')
{"variant_id": "167d8af3-bdf1-4318-a4c5-b356d68b7269", "name": "DIFF Khán đài VVIP / 2026-06-20"}
```

**Sau** (output 2026-09-07, product `6cefb942-…`, phần tử đầu):

```json
[
  {
    "variant_id": "167d8af3-bdf1-4318-a4c5-b356d68b7269",
    "name": "DIFF Khán đài VVIP / 2026-06-20",
    "status": "active",
    "attributes": {
      "ticket": "DIFF Khán đài VVIP",
      "use_date": "2026-06-20"
    }
  }
]
```

Sample khác (product `cc7a915a-…`), có key ngoài bảng map:

```json
{
  "variant_id": "7ac6dff6-44d5-49d0-88f1-61b1c2756593",
  "name": "Trẻ em / Nhà hàng 4 Mùa / Ngoại tỉnh / 10:30 - 12:30",
  "status": "active",
  "attributes": {
    "time_slot": "10:30 - 12:30",
    "region": "Ngoại tỉnh",
    "restaurant": "Nhà hàng 4 Mùa",
    "age_group": "Trẻ em"
  }
}
```

### 1.9. Axis Transform

- Chỉ variant chưa xoá mềm, chỉ thuộc tính có axis.
- Mỗi axis = `collect_set(value_name_vi)` theo `product_id`, rồi `to_json`. Thứ tự phần tử không xác định. Không có giá trị thì NULL (không phải `[]`).
- `variant_statuses` = `collect_set(product_variants.status)` của variant chưa xoá.

Sample (output 2026-09-07):

| product_id | variant_tickets | variant_dates | variant_age_groups | variant_statuses |
|---|---|---|---|---|
| 6cefb942-… | `["DIFF Khán đài A2","DIFF Khán đài A1","DIFF Khán đài AVIP","DIFF Khán đài A3","DIFF Khán đài A4","DIFF Khán đài VVIP"]` | `["2026-06-20"]` | NULL | `["active"]` |
| cc7a915a-… | NULL | NULL | `["Người cao tuổi","Người lớn","Trẻ em"]` | `["active"]` |
| e757609b-… | NULL | NULL | `["Người cao tuổi","Người lớn","아이들","노인","어른","Trẻ em"]` | `["active"]` |

### 1.10. `product_attributes` Transform (holiday)

**Source:** `product_posts.raw_sync_data` (JSON string), `price_level`, `is_active`.

| Key | Lấy từ |
|---|---|
| `shortDescription` | Phần tử `translations[]` có `languageCode` bắt đầu `en`, rồi `vi`, rồi `shortDescription` cấp trên |
| `tags` | `tags[].label`, không có thì `tags[].code`. Mảng rỗng thì NULL |
| `priceLevel` | `price_level` sau default 0 |
| `isActive` | `is_active` |

`post_title_vi` (dùng nhận diện DIFF) lấy `translations[]` có `languageCode` bắt đầu `vi`, rồi `name` cấp trên.

**Trước** (minh họa dạng nguồn):

```json
{
  "name": "<name>",
  "shortDescription": "<mô tả cấp trên>",
  "translations": [
    {"languageCode": "vi-VN", "name": "<tên vi>", "shortDescription": "<mô tả vi>"},
    {"languageCode": "en-VN", "name": "<tên en>", "shortDescription": "<mô tả en>"}
  ],
  "tags": [{"code": "<code>", "label": "Visit Vietnam"}]
}
```

**Sau** (output 2026-09-07, product `cc7a915a-…`):

```json
{
  "shortDescription": "Bà Nà Hills - Thiên đường trên đỉnh núi Chúa. Trải nghiệm hệ thống cáp treo Bà Nà nổi tiếng thế giới, ...",
  "tags": ["Khu vui chơi giải trí", "Visit Vietnam"],
  "priceLevel": 2,
  "isActive": true
}
```

### 1.11. `source_id` và `destination_id`

1. `source_id` = `business_service_id` (mục 1.2).
2. `destination_id` = `ai_poi.destination_id` của dòng `ai_poi.source_id = source_id`. `ai_poi` nhiều dòng cùng `source_id` thì `dropDuplicates` giữ một dòng bất kỳ.
3. Remap `DESTINATION_ID_REMAP`:

| destination_id nguồn | Đích | Ghi chú trong code |
|---|---|---|
| `npl86zvhuytfb0ys679uz6w1` | `e8xuqhikk4547xjw4haffqko` | Bana Hill |
| `w9w1hdm8iwcofbh1rj12a3i2` | `chdm4mekx35eqiiscri33t30` | Hue |
| `bpy3b4acd6hjdisugue3sxz7` | `e8xuqhikk4547xjw4haffqko` | Da Nang |
| `t36nuvkacqp87p6pk1k4zbv8` | `xjo4p6jhlvabpjhfyq4rgac7` | Hoi An |

4. `business_service_id` khác NULL mà `destination_id` vẫn NULL thì gán `nwzsg28kmk8h4xkai5udjwy7` (code ghi "Da Nang (temporary fallback)").
5. Bỏ dòng thiếu `source_id` hoặc `destination_id`, rồi bỏ dòng `source_id` không có trong `ai_enriched_poi`.

Output lần chạy 2026-09-07: 20/60 product khớp `ai_poi` (10 `source_id` khác nhau). 40 product có `source_id` không có trong `ai_enriched_poi` và bị bỏ.

### 1.12. Sample một dòng đích

Output 2026-09-07, product `6cefb942-…` (`variants_json` và `product_attributes` rút gọn):

| Target Field | Giá trị |
|---|---|
| product_id | `6cefb942-…` |
| name | `DIFF Night 4 - 20/6 (Germany - Macau)` |
| lang | `en` |
| product_type | `other` |
| is_active | `true` |
| is_bookable | `false` |
| product_line | `cartable` |
| price_level | `3` |
| original_price | `1804000` |
| marketing_price | `2128720` |
| markup_percent | `18` |
| variant_count | `6` |
| active_variant_count | `6` |
| variants_json | `[{"variant_id":"167d8af3-…","name":"DIFF Khán đài VVIP / 2026-06-20","status":"active","attributes":{"ticket":"DIFF Khán đài VVIP","use_date":"2026-06-20"}}, …]` |
| variant_tickets | `["DIFF Khán đài A2", …, "DIFF Khán đài VVIP"]` |
| variant_dates | `["2026-06-20"]` |
| variant_hotels | NULL |
| variant_age_groups | NULL |
| variant_room_types | NULL |
| variant_departures | NULL |
| variant_statuses | `["active"]` |
| product_attributes | `{"shortDescription":"Vé Xem biểu diễn Pháo Hoa Quốc tế (Giờ biểu diễn: 20:00-22:00) …","tags":["Visit Vietnam"],"priceLevel":3,"isActive":true}` |
| source_id | `e7166907-2f89-4cd8-a261-1cb1e478ea5f` |
| destination_id | `e8xuqhikk4547xjw4haffqko` |
| updated_at | `2026-09-07T11:25:51Z` |

### 1.13. Điểm cần lưu ý

Các điểm này đọc từ code và output đã lưu. Nguyên nhân runtime chưa có probe.

1. `variants_json` bị lặp phần tử. Output 2026-09-07: 16/20 product có mỗi `variant_id` xuất hiện 2 lần (ví dụ `cc7a915a-…`: `variant_count` 60, 120 phần tử, 60 `variant_id` khác nhau). `variant_count` đúng vì tính trước khi join. Join có thể nhân dòng: `product_variant_translations`, `products`, `product_translations`, `product_posts` (theo `external_id`). Notebook không dedup bảng nào. Cần probe đếm trùng khóa trên từng bảng.
2. Bronze đọc nguyên, không lấy bản ghi mới nhất theo `id`. Nếu bronze giữ nhiều phiên bản CDC cho một `id`, cột cấp product lấy `first(ignorenulls)` không xác định.
3. `updated_at` của mọi dòng trong output (`2026-09-07T11:25:51Z`) trùng thời điểm chạy, trong khi code hiện tại lấy `products.updated_at`. Output đã lưu có thể từ phiên bản code cũ hơn source hiện tại.
4. Hai id cho "Da Nang": remap dùng `e8xuqhikk4547xjw4haffqko`, fallback dùng `nwzsg28kmk8h4xkai5udjwy7`.
5. `lang = 'en'`, nhưng `name` là tiếng Việt khi `ENABLE_TRANSLATION = False`, và `shortDescription` trong output là tiếng Việt.
6. Product đã xoá mềm vẫn được ghi (`is_active = false`). Variant đã xoá mềm vẫn nằm trong `variants_json`.
7. Holiday so `status = 'active'` (thường), hotel so `'Active'` (hoa).
8. Xoá mềm của `product_posts` khác các bảng còn lại: `deleted_at` ở tương lai vẫn tính là đã xoá.
9. Giá NULL được ghi `0`, không phân biệt "không có giá" với "giá 0".
10. Cell 3/4, 5/7, 6/8 lặp code giống nhau. Chạy lại không đổi kết quả.

---
