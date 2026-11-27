# Mapping GLD Service Product Offer

Hợp đồng mapping cho `lh_vv_gold.dbo.gld_srv_product_offer`, chưa phải DDL. Task `20261127-pn-product-one-table-mapping`. Quyết định: `.ai/tasks/20261127-pn-product-one-table-mapping/decision.md` mục `## Quyết định hiện hành` (U-01 … U-08, D-0 … D-10). Hình dạng cũ: `mapping_legacy_ai_product.md` mục `## 1. Table: ai_product`. Chỗ quyết định khác hình dạng cũ thì quyết định thắng.

Nguồn chỉ là silver: L2 theo `mapping_slv_pn_product_l2.md`, L1 theo `mapping_slv_pn_product.md`, destination `slv_enr_poi_destination`. Không đọc bronze. Không đọc bảng gold nào. Không cache dịch, không sinh tên, không gọi LLM.

Cột kỹ thuật gold theo `docs/context/02_NAMING_CONVENTION.md` §5.2: `row_hash` string, `created_at` timestamp, `updated_at` timestamp, `deleted_at` timestamp. `deleted_at` khác NULL là xoá mềm, kèm `is_active = false`.

Notebook node đề xuất: `NB_GLD_SRV_PRODUCT_OFFER` (`02_NAMING_CONVENTION.md` §2). Notebook, DDL, seed và cạnh pipeline thuộc task `20261127-gld-pn-product`.

## 1. Table: `gld_srv_product_offer`

Lakehouse.schema: `lh_vv_gold.dbo`

### 1.1. Xử lý

- Grain: một dòng một `product_id` (U-02, D-0). Hai nhánh cùng bảng (U-03):
  - Holiday: một dòng cho mỗi `slv_pn_product_sale.product_id` có `deleted_at IS NULL`, tức `slv_pn_products.id`. `product_type = 'other'` (D-2).
  - Hotel: một dòng cho mỗi `slv_pn_hotel_room_offer.room_type_id` có `deleted_at IS NULL`, tức `slv_pn_hotel_room_types.id`. `product_type = 'hotel'` (U-03).
- Khoá `product_id`. Probe 2026-11-28 (P-1): id holiday trùng id hotel 0 dòng, id trùng trong `slv_pn_products` 0, trong `slv_pn_hotel_room_types` 0. Sau khi gộp hai nhánh, `product_id` trùng thì job fail. Không chọn một dòng, không thêm tiền tố.
- Đọc L2 chỉ dòng `deleted_at IS NULL`. L1 và L2 đọc ở version đã ghim cho lần chạy.
- Cách ghi: mỗi lần chạy tính lại toàn bộ, MERGE theo `product_id` và `row_hash` của `NB_LIB_TRANSFORM_SLV_GLD`, `load_mode = RECOMPUTE`, một commit Delta mỗi lần chạy. Id vắng mặt trong bản build bị xoá mềm: ghi `deleted_at`, `is_active = false`.
- Input bắt buộc: `slv_pn_product_sale` và `slv_pn_hotel_room_offer`. Một nhánh ra 0 dòng thì job fail trước khi ghi, để MERGE không xoá mềm cả nhánh.
- Thứ tự build:
  1. Holiday: driver `slv_pn_product_sale`. Tính `business_service_id` (mục 1.7). Bỏ product có hơn một id (U-04).
  2. Holiday: gom variant theo `product_id` trước khi join (mục 1.3, 1.4). Rồi join tên, `product_line`, `product_attributes`.
  3. Hotel: driver `slv_pn_hotel_room_offer` join `slv_pn_hotel_room_types` theo `slv_pn_hotel_room_types.id = room_type_id`. Gom rate plan theo `business_service_id` (mục 1.5), rồi LEFT JOIN vào phòng.
  4. Mỗi nhánh: tính `poi_id`, rồi LEFT JOIN `slv_enr_poi_destination` (mục 1.7).
  5. Kiểm tra: không nhánh nào rỗng, khoá tra cứu duy nhất.
  6. Union hai nhánh theo thứ tự cột của mục 1.2. Kiểm tra `product_id` duy nhất. Tính `row_hash`. MERGE.
- Khoá tra cứu phải duy nhất, trùng thì job fail: (`product_id`, `locale`) của `slv_pn_product_translations` với `locale` `en` và `vi`; (`variant_id`, `locale = 'vi'`) của `slv_pn_product_variant_translations`; `poi_id` của `slv_enr_poi_destination`; `id` của `slv_pn_products`, `slv_pn_product_posts`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`. Lý do: `mapping_legacy_ai_product.md` §1.13 điểm 1, variant bị lặp vì join nhân dòng. Tra cứu nhãn cho cột axis không kiểm tra, vì `collect_set` đã gộp.
- Không tạo dòng:
  - Product holiday có hơn một `business_service_id` khác NULL khác nhau trên các dòng relation `deleted = false`. Bỏ cả product (U-04, D-10).
  - Dòng L2 driver có `deleted_at` khác NULL.
- Vẫn giữ dòng:
  - Product không có variant `deleted = false`: `variants_json = []` (D-6). P-4: 0 product như vậy.
  - Product không có `business_service_id`: `business_service_id`, `source_id`, `poi_id`, `destination_id` đều NULL (D-4).
  - Có `poi_id` mà không có dòng destination: `destination_id` NULL (D-4). P-3: holiday 3 `business_service_id` khớp, 5 không khớp; hotel 32 khớp, 87 không khớp.
  - Phòng không có rate plan sống: `variants_json = []` (D-7). P-5: 3 phòng.
- Không mang sang từ notebook cũ: lọc theo bảng POI gold, đổi mã destination, destination hằng dự phòng, hằng chế độ test, cache dịch, giá mặc định `0`, cổng `use_date` và `diff` của `is_bookable`, variant đã xoá trong `variants_json`, `updated_at` nghiệp vụ.
- Metric ghi log mỗi lần chạy, không làm fail job: `holiday_rows`, `hotel_rows`, `dropped_multi_bsid`, `null_business_service_id`, `relation_null_bsid_only`, `no_destination`, `empty_variants_holiday`, `empty_variants_hotel`, `variant_attributes_unparsed`, `null_price_with_post` (dòng holiday có `product_post_id` mà `original_price` NULL).

### 1.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| holiday: slv_pn_product_sale.product_id; hotel: slv_pn_hotel_room_offer.room_type_id | string | 1-1, khoá. Trùng sau union thì job fail (D-0) | product_id |
| holiday: slv_pn_product_translations.name (`locale = 'en'`, rồi `'vi'`); hotel: slv_pn_hotel_room_types.name | string | Holiday `coalesce(name en, name vi, product_id)`. Hotel `coalesce(name, product_id)`. Không dịch, không sinh tên | name |
| | string | Hằng `'en'` (D-9). Giữ như cũ dù `name` có thể là tiếng Việt (`mapping_legacy_ai_product.md` §1.13 điểm 5) | lang |
| | string | Holiday `'other'` (D-2). Hotel `'hotel'` (U-03) | product_type |
| cột kỹ thuật | boolean | `true` trên mọi dòng bản build ghi. `false` khi `deleted_at` khác NULL. Không đọc `status` của product hay phòng (D-8) | is_active |
| holiday: slv_pn_product_sale.is_bookable; hotel: slv_pn_hotel_room_offer.is_bookable | boolean | 1-1 (D-8). Không thêm cổng | is_bookable |
| holiday: slv_pn_products.product_line | string | Holiday 1-1. Hotel hằng `'accommodation'` | product_line |
| holiday: slv_pn_product_sale.marketing_price, original_price | int | Holiday: bậc theo `coalesce(marketing_price, original_price)`: ≤ 500000 → 1, ≤ 2000000 → 2, ≤ 5000000 → 3, còn lại 4, NULL → 0. Hotel `0`. Không giải mã (mục 1.8) | price_level |
| holiday: slv_pn_product_sale.original_price | double | 1-1. NULL giữ NULL (U-06, D-1). Hotel NULL | original_price |
| holiday: slv_pn_product_sale.marketing_price | double | 1-1. NULL giữ NULL (U-06, D-1). Hotel NULL | marketing_price |
| holiday: slv_pn_product_sale.markup_percent | double | 1-1. NULL giữ NULL (U-06, D-1). Hotel NULL | markup_percent |
| holiday: slv_pn_product_variants; hotel: slv_pn_hotel_rate_offer, slv_pn_hotel_rate_plans | long | Holiday: số variant `deleted = false` theo `product_id`, không có thì NULL. Hotel: số rate plan sống cùng `business_service_id` của phòng, không có thì 0 | variant_count |
| holiday: slv_pn_product_variants.status; hotel: slv_pn_hotel_rate_offer.status | long | Holiday: số variant `deleted = false` và `status = 'active'`, không có variant thì NULL. Hotel: số rate plan sống có `status = 'Active'`, không có thì 0. So khớp đúng chữ | active_variant_count |
| holiday: mục 1.3; hotel: mục 1.5 | string | Mảng JSON `{variant_id, name, status, attributes}`, sắp theo `variant_id`. Không bao giờ NULL; không có phần tử thì `[]` | variants_json |
| slv_pn_product_variants.attributes, nhãn thuộc tính | string | Axis `holiday:swticket` (mục 1.4). Hotel NULL | variant_tickets |
| slv_pn_product_variants.attributes, nhãn thuộc tính | string | Axis `holiday:use_date`. Hotel NULL | variant_dates |
| slv_pn_product_variants.attributes, nhãn thuộc tính | string | Axis `holiday:hotel`. Hotel NULL | variant_hotels |
| slv_pn_product_variants.attributes, nhãn thuộc tính | string | Axis `holiday:quantity` và `holiday:age_group`. Hotel NULL | variant_age_groups |
| slv_pn_product_variants.attributes, nhãn thuộc tính | string | Axis `holiday:zone`. Hotel NULL | variant_room_types |
| slv_pn_product_variants.attributes, nhãn thuộc tính | string | Axis `holiday:depature`. Hotel NULL | variant_departures |
| slv_pn_product_variants.status | string | `to_json(array_sort(collect_set(status)))` của variant `deleted = false`. Rỗng thì NULL. Hotel NULL | variant_statuses |
| holiday: slv_pn_product_posts.raw_sync_data; hotel: slv_pn_hotel_room_offer, slv_pn_hotel_room_types | string | Mục 1.6 | product_attributes |
| holiday: slv_pn_product_business_service_relation.business_service_id, rồi slv_pn_product_posts.business_service_id; hotel: slv_pn_hotel_room_types.business_service_id | string | Mục 1.7 (D-3, D-10, U-04). Không hash | business_service_id |
| business_service_id | string | Cast string, không hash. NULL giữ NULL | source_id |
| slv_pn_product_sale.product_post_id | string | Holiday 1-1. Hotel NULL | product_post_id |
| business_service_id | string | `uuid_md5(business_service_id, lit('partner'))` (U-05). NULL khi `business_service_id` NULL | poi_id |
| slv_enr_poi_destination.destination_id | string | LEFT JOIN theo `poi_id`. Chuỗi JSON mảng copy 1-1 (D-5). Không khớp thì NULL (D-4) | destination_id |
| các cột nghiệp vụ phía trên, đúng thứ tự bảng này | — | Mục 1.9 | row_hash |
| lần tính đầu | timestamp | Cột kỹ thuật gold | created_at |
| lần tính khi hash đổi | timestamp | Cột kỹ thuật gold. Đổi khi `row_hash` đổi hoặc `deleted_at` đổi giữa NULL và khác NULL | updated_at |
| id vắng mặt trong bản build | timestamp | Cột kỹ thuật gold. Khác NULL là xoá mềm, kèm `is_active = false` | deleted_at |

### 1.3. `variants_json` holiday

**Source:** `slv_pn_product_variants` (`id`, `product_id`, `status`, `attributes`, `deleted`), `slv_pn_product_variant_translations.name` với `locale = 'vi'`.

- Chỉ variant `deleted = false` (D-6).
- Mỗi phần tử:

| Key | Lấy từ |
|---|---|
| `variant_id` | `slv_pn_product_variants.id` |
| `name` | `slv_pn_product_variant_translations.name` (`vi`). Không có thì `null` |
| `status` | `slv_pn_product_variants.status`, 1-1 |
| `attributes` | `from_json(attributes, 'map<string,string>')`, ghi thành object JSON. Giữ nguyên khoá `holiday:*` và value. Không resolve nhãn (D-6). NULL thì `{}`. Chuỗi không parse được thì `null` và tăng `variant_attributes_unparsed` |

- Sắp phần tử theo `variant_id` tăng dần. Mỗi `variant_id` có đúng một phần tử. Không có variant thì `[]`.

Ví dụ minh hoạ:

```json
[
  {
    "variant_id": "<slv_pn_product_variants.id>",
    "name": "<tên vi>",
    "status": "active",
    "attributes": {"holiday:swticket": "<value>", "holiday:use_date": "<value>"}
  }
]
```

### 1.4. Axis holiday

- Chỉ variant `deleted = false`. Explode `attributes` thành (`attr_code`, `value_code`).
- `value_name_vi`: `slv_pn_product_attributes.code = attr_code`, rồi `slv_pn_product_attribute_values` với `attribute_id` = id thuộc tính và `code = value_code`, rồi `slv_pn_product_attribute_value_translations` với `attribute_id` = `slv_pn_product_attribute_values.id` và `locale = 'vi'`. Không có thì NULL và không vào axis.
- Bảng mã:

| `attr_code` | Cột |
|---|---|
| `holiday:swticket` | `variant_tickets` |
| `holiday:use_date` | `variant_dates` |
| `holiday:hotel` | `variant_hotels` |
| `holiday:quantity`, `holiday:age_group` | `variant_age_groups` |
| `holiday:zone` | `variant_room_types` |
| `holiday:depature` | `variant_departures` |
| khác | không có cột |

- Mỗi cột = `to_json(array_sort(collect_set(value_name_vi)))` theo `product_id`. Rỗng thì NULL, không phải `[]`. Thứ tự sắp để `row_hash` ổn định.
- Value có phải mã giá trị hay không vẫn là câu hỏi 1 bên dưới. Không khớp thì axis NULL, job không fail.

### 1.5. `variants_json` hotel

**Source:** `slv_pn_hotel_rate_offer` (`deleted_at IS NULL`) join `slv_pn_hotel_rate_plans` theo `slv_pn_hotel_rate_plans.id = rate_plan_id`.

- Rate plan gắn theo khách sạn: mọi phòng cùng `business_service_id` nhận cùng danh sách (`mapping_legacy_ai_product.md` §1.6). Phòng có `business_service_id` NULL thì `[]`.
- Mỗi phần tử:

| Key | Lấy từ |
|---|---|
| `variant_id` | `slv_pn_hotel_rate_offer.rate_plan_id` |
| `name` | `coalesce(slv_pn_hotel_rate_plans.name, rate_plan_id)` |
| `status` | `slv_pn_hotel_rate_offer.status`, 1-1 |
| `attributes.meal_plan` | `slv_pn_hotel_rate_offer.meal_plan`, số. Không nhãn chữ (`mapping_slv_pn_product_l2.md` §3.3) |
| `attributes.kind` | `slv_pn_hotel_rate_plans.kind`, 1-1 |
| `attributes.valid_from` | `slv_pn_hotel_rate_offer.valid_from`, chuỗi `yyyy-MM-dd'T'HH:mm:ss'Z'` theo UTC. NULL thì `null` |
| `attributes.valid_to` | `slv_pn_hotel_rate_offer.valid_to`, như `valid_from` |
| `attributes.include_tax` | `slv_pn_hotel_rate_plans.include_tax`, boolean JSON |
| `attributes.include_service_charge` | `slv_pn_hotel_rate_plans.include_service_charge`, boolean JSON |

- Không suy cờ còn bán từ `valid_from`, `valid_to` (U-07).
- Sắp theo `variant_id`. Không có rate plan thì `[]` (D-7). P-5: tối đa 14 rate plan cho một `business_service_id`.

### 1.6. `product_attributes`

Holiday: từ `slv_pn_product_posts.raw_sync_data` theo `slv_pn_product_posts.id = product_post_id`, quy tắc của `mapping_legacy_ai_product.md` §1.10.

| Key | Lấy từ |
|---|---|
| `shortDescription` | Phần tử `translations[]` có `languageCode` bắt đầu `en`, rồi `vi`, rồi `shortDescription` cấp trên |
| `tags` | `tags[].label`, không có thì `tags[].code`. Mảng rỗng thì `null` |
| `priceLevel` | `price_level` của dòng |
| `isActive` | `is_active` của dòng lúc build |

`product_post_id` NULL thì `shortDescription` và `tags` là `null`; object vẫn đủ bốn khoá.

Hotel: object phòng, khoá theo `mapping_legacy_ai_product.md` §1.6.

| Key | Lấy từ |
|---|---|
| `shortDescription` | `slv_pn_hotel_room_types.description` |
| `tags` | `slv_pn_hotel_room_types.tags`, chuỗi 1-1. Không tách nhãn (câu hỏi 3) |
| `priceLevel` | `null` |
| `isActive` | `is_active` của dòng lúc build |
| `maxOccupancy` | `slv_pn_hotel_room_offer.max_occupancy` |
| `adultCapacity` | `slv_pn_hotel_room_offer.adult_capacity` |
| `childCapacity` | `slv_pn_hotel_room_offer.child_capacity` |
| `maxExtraBed` | `slv_pn_hotel_room_types.max_extra_bed` |
| `roomSize` | `slv_pn_hotel_room_types.room_size` |
| `viewType` | `slv_pn_hotel_room_offer.view_type`, 1-1 |
| `amenities` | `slv_pn_hotel_room_types.amenities`, chuỗi 1-1. Không tách tên (câu hỏi 3) |
| `availableRooms` | `slv_pn_hotel_room_offer.available_rooms` |
| `totalRooms` | `slv_pn_hotel_room_types.total_rooms` |

Thứ tự khoá cố định như hai bảng trên. Dòng đã xoá mềm giữ `isActive` của lần build cuối.

### 1.7. `business_service_id`, `poi_id`, `destination_id`

Holiday (D-3, D-10, U-04):

1. Lấy các dòng `slv_pn_product_business_service_relation` có `deleted = false` theo `product_id`. Đếm `business_service_id` khác NULL khác nhau.
2. Hơn một: bỏ cả product.
3. Đúng một: lấy id đó.
4. Không có dòng relation `deleted = false`: lấy `slv_pn_product_posts.business_service_id` của `product_post_id`.
5. Có dòng relation `deleted = false` nhưng mọi `business_service_id` đều NULL: không fallback sang post. `business_service_id` NULL, tăng `relation_null_bsid_only`.
6. Còn lại NULL. Dòng vẫn giữ (D-4).

P-2 đếm mọi dòng relation, chưa lọc `deleted`: 41 product, đều đúng một id.

Hotel: `slv_pn_hotel_room_types.business_service_id`, 1-1.

`poi_id = uuid_md5(business_service_id, lit('partner'))`, tức `md5(concat(business_service_id, 'partner'))` viết 8-4-4-4-12 (`AGENTS.md` §7). NULL khi `business_service_id` NULL.

`destination_id`: LEFT JOIN `slv_enr_poi_destination` theo `poi_id`, đọc cùng cách `gld_srv_poi_info` (`live_only=False`). Copy 1-1 chuỗi JSON mảng, cùng hợp đồng `gld_srv_poi_info.destination_id` (D-5). Không parse, không chọn một phần tử, không đổi mã, không hằng dự phòng. `poi_id` trùng trong `slv_enr_poi_destination` thì job fail. P-3: mảng holiday có 2 hoặc 3 phần tử; hotel có 0, 1, 2, 3 hoặc 9.

### 1.8. Giá và U-06

- `original_price`, `marketing_price`, `markup_percent` copy 1-1 từ `slv_pn_product_sale`. Gold không giải mã, không ghi `0`, không fail theo giá. Hotel NULL.
- Chỗ fail job khi giải mã lỗi là decoder của `slv_pn_product_sale` (D-1, `mapping_slv_pn_product_l2.md` §1.3). Việc đổi decoder thuộc task khác. Cho tới khi đổi, L2 vẫn ghi NULL khi giải mã lỗi, và gold chép NULL đó. Metric `null_price_with_post` đếm các dòng này.
- `price_level` là bậc suy từ giá L2 (D-9). Bậc NULL → 0 chỉ áp cho `price_level`, không áp cho cột giá.

### 1.9. `row_hash` và thứ tự ổn định

- `row_hash = sha2(to_json(struct(...)), 256)` trên các cột nghiệp vụ theo thứ tự mục 1.2, từ `product_id` tới `destination_id`, bỏ `is_active`. Ngoài struct: `is_active`, `row_hash`, `created_at`, `updated_at`, `deleted_at`.
- `variants_json` sắp theo `variant_id`. Axis và `variant_statuses` dùng `array_sort`. Timestamp trong `variants_json` hotel định dạng theo UTC. Khoá của `product_attributes` theo thứ tự cố định.
- Chạy lại trên cùng version đã ghim thì không ghi dòng nào.

## Câu hỏi cần chốt

1. Kế thừa câu hỏi 2 của `mapping_slv_pn_product.md`: value trong `slv_pn_product_variants.attributes` chưa xác nhận là mã giá trị. Nếu không phải, sáu cột axis là NULL.
2. Kế thừa câu hỏi 4 của `mapping_slv_pn_product_l2.md`: đơn vị epoch của `valid_from`, `valid_to` chưa kết luận. Gold vẫn định dạng từ timestamp L2.
3. `tags` và `amenities` của phòng: L1 lưu chuỗi, dạng phần tử chưa có probe. Tạm copy chuỗi 1-1, không tách nhãn.
4. D-1: cần task riêng sửa decoder `slv_pn_product_sale` để lỗi giải mã fail job. Chưa có task.
5. Notebook `NB_GLD_SRV_PRODUCT_OFFER`, DDL và cạnh `PL_VV_TRANS_SLV_TO_GLD_30M` (ba bảng L2 và `slv_enr_poi_destination` → `gld_srv_product_offer`) thuộc task `20261127-gld-pn-product` sau D-A. Nên probe tính duy nhất của các khoá tra cứu ở mục 1.1 trước khi viết notebook.
