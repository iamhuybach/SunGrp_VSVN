# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Cột JSON nguồn | Probe P01 trên Fabric DEV, 57 dòng: `slv_3p_poi_amenity` không có cột JSON chứa `facilities` hoặc `terms_and_conditions`. Không viết notebook. | Lịch sử quyết định / D1 kết quả P01 | 2026-10-15 |
| D2 | Rule gom nhóm | Hai tài liệu `get_amenity.md` và `poi_amenity_mapping.md` là rule gom nhóm cho `source_flags_json`. Rule không có khóa nguồn trong JSON đã chứng minh vẫn là `MISSING_EVIDENCE`. Không lọc ngành vì bảng amenity không có `types`. | Lịch sử quyết định / D2 sửa | 2026-10-15 |
| D3 | Nhóm amenity | `facilities` và `terms_and_conditions` chỉ là khóa bao. Bỏ `terms_and_conditions`. Nhóm là khóa bên trong `facilities`, ví dụ `accessibility` và `general_amenities`. Giá trị của nhóm là `enum`. | Lịch sử quyết định / D3 | 2026-10-15 |
| D4 | Payload chưa có enum | Probe P02 trên Fabric DEV: `source_flags_json` không có object nào chứa khóa `enum`. | Lịch sử quyết định / D4 | 2026-10-15 |
| D5 | Nguồn và grain | Payload cần xử lý là `slv_3p_poi_amenity.source_flags_json`. Ba sample là ví dụ sau khi gom nhóm. Key đích là tên nhóm, value là từng amenity trong nhóm. | Lịch sử quyết định / D5 | 2026-10-15 |
| D6 | Bảng và rule | Bảng `lh_vv_silver.dbo.slv_3p_poi_amenity_kv` gom `source_flags_json` thành key-value. Nhóm chỉ có `general_amenities` và `accessibility`. Value là snake_case của khóa Google; `restroom` thành `has_restroom`; mọi khóa `parkingOptions` bằng true thành `parking`. `pl_name` đề xuất `PL_VV_TRANS_SLV_3P_AMENITY_KV_1H`, chưa đặt lịch. | Lịch sử quyết định / D6 | 2026-10-15 |
| D7 | Dừng task | Người dùng dừng task. Không viết notebook. Trạng thái `blocked`. | Lịch sử quyết định / D7 | 2026-10-15 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- P02 xác nhận payload là cờ boolean hoặc null, không phải `enum` có sẵn. D5 giao transform gom các cờ đó thành nhóm.
- Risk giữ `medium` vì bảng mới là projection theo khóa, không append lịch sử và không ghi đè `slv_3p_poi_amenity`. Nếu architecture chọn append hoặc ghi đè, nâng risk lên `high` và bật `risk-gate`.

## Sai lệch so với kiến trúc

- Không có. `architecture.md` chưa được viết.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-15: `facilities` và `terms_and_conditions` chỉ là khóa bao. Bỏ `terms_and_conditions`. Nhóm là khóa bên trong `facilities`. Giá trị của nhóm là `enum`.
- 2026-10-15: payload cần xử lý là `source_flags_json`. Ba sample là ví dụ sau khi gom nhóm theo `poi_amenity_mapping.md` và `get_amenity.md`. Key là tên nhóm, value là amenity trong nhóm, ví dụ `general_amenities` với `gym` và `parking`.
- 2026-10-15: dừng task. Không chọn S2. Không viết notebook. Trạng thái `blocked`.

## Lịch sử quyết định

### D1 — 2026-10-15

Chưa chỉ được cột JSON của `slv_3p_poi_amenity` chứa khóa `facilities` hoặc `terms_and_conditions`. Chưa viết notebook.

Cấu trúc còn thiếu so với sample: object nhóm có `enum`, `item_type`, `required`, `type`, với các nhóm `facilities.accessibility`, `facilities.general_amenities`, `facilities.safety_and_hygiene`, và `terms_and_conditions`.

Cột đang có trong repo, chưa chứng minh chứa cấu trúc đó:

- Registry `NB_CREATE_DDL`, khớp `tests/test_3p_l1_contract.py`: `poi_id`, `source_flags_json`. `source_flags_json` là `JSON_PICK` các cờ boolean Google và object `parkingOptions`, `paymentOptions`, `accessibilityOptions`, `evChargeOptions`, `fuelOptions`.
- Context `docs/context/01_DATA_MODEL.md` mục 5.2 và `docs/context/CTRL_TABLES_CONTEXT.md` vẫn ghi `amenity_schema_json`, `ext_attributes_json`. Hai tên này không còn trong seed registry hiện tại.
- Bronze trong `01_DATA_MODEL.md` có `poi_amenity.amenity_schema.facilities` và `facilities` ở gốc, nhưng nhóm con là `main_cuisine`, `specialty_tags`, `space_and_services`, `additional_amenities`. Không có `terms_and_conditions`.

### D2 — 2026-10-15

`get_amenity.md` và `poi_amenity_mapping.md` là `MISSING_EVIDENCE` cho hình `enum` của sample.

`get_amenity.md` cần boolean Google đã làm phẳng và `types` hoặc `primaryType` cho `detect_category`. Bảng amenity trong registry không có `types`. `poi_amenity_mapping.md` map chuỗi snake_case, không phải tag hiển thị trong `enum`. Không gộp hai file này vào công thức sample.

### D1 — kết quả P01 — 2026-10-15

Probe P01 trên Fabric DEV, 57 dòng: `slv_3p_poi_amenity` không có cột JSON chứa `facilities` hoặc `terms_and_conditions`. Không viết notebook.

Cột đang có trên `lh_vv_silver.dbo.slv_3p_poi_amenity`, đủ 57 dòng, không null:

- `poi_id` string
- `source_flags_json` string
- `_crawled_at`, `_first_seen_at`, `_last_seen_at`, `created_at`, `updated_at` timestamp
- `_event_id` string

Khóa cấp một của `source_flags_json`, mỗi khóa có mặt ở 57/57 dòng: `flags`, `accessibilityOptions`, `evChargeOptions`, `fuelOptions`, `parkingOptions`, `paymentOptions`. Không có `$.facilities` hay `$.terms_and_conditions`.

Cấu trúc sample còn thiếu: nhóm `facilities.accessibility`, `facilities.general_amenities`, `facilities.safety_and_hygiene`, và `terms_and_conditions`, mỗi nhóm có `enum`, `item_type`, `required`, `type`. Context còn ghi `amenity_schema_json` và `ext_attributes_json`, nhưng hai cột này không có trên bảng DEV.

Nguồn: `evidence/results/P01_amenity_json_keys.txt`.

### D3 — 2026-10-15

`facilities` và `terms_and_conditions` chỉ là khóa bao. Bỏ `terms_and_conditions`. Nhóm là khóa bên trong `facilities`, ví dụ `accessibility` và `general_amenities`. Giá trị của nhóm là `enum`.

Người dùng chốt trong chat ngày 2026-10-15. Một dòng đích vẫn là một phần tử `enum` không rỗng của một nhóm. `enum` rỗng không sinh dòng. Không tạo dòng cho chính khóa bao.

P01 không thấy `$.facilities`, nên cũng không thấy `$.facilities.accessibility` hay `$.facilities.general_amenities`. Sáu khóa cấp một của `source_flags_json` không mang tên nhóm đó. `accessibilityOptions` không được đổi tên thành `accessibility`. P02 chỉ đọc tên khóa con và đường dẫn nào có khóa `enum`, không đọc nội dung `enum`. Chưa viết notebook.

### D4 — 2026-10-15

Probe P02 trên Fabric DEV: `source_flags_json` không có object nào chứa khóa `enum`. Không viết notebook.

`VERDICT FAIL`, `enum_paths` bằng 0, `STATUS object` trên 57 dòng. Nguồn: `evidence/results/P02_amenity_enum_groups.txt`.

Khóa con đã in, giá trị là `bool` hoặc `null`, không phải mảng `enum`:

- `$.flags` là object trên 57 dòng. Các khóa con đã thấy gồm `allowsDogs`, `curbsidePickup`, `delivery`, `dineIn`, `goodForChildren`, `goodForGroups`, `goodForWatchingSports`, `liveMusic`, `menuForChildren`, `outdoorSeating`, `reservable`, `restroom`, `servesBeer`, `servesBreakfast`, `servesBrunch`, `servesCocktails`, `servesCoffee`, `servesDessert`, `servesDinner`, `servesLunch`, `servesVegetarianFood`.
- `$.accessibilityOptions` là object trên 31 dòng và null trên 26 dòng. Khóa con đã thấy: `wheelchairAccessibleEntrance`, `wheelchairAccessibleParking`, `wheelchairAccessibleRestroom`, `wheelchairAccessibleSeating`.
- `$.evChargeOptions` null trên 57 dòng.

`CHILD_KEYS` bị cắt: in 50 token, tổng 70. Hai mươi token không có trong file kết quả. Phần quét `enum` vẫn đủ toàn bộ JSON và bằng 0. Nhóm còn thiếu so với D3: `accessibility`, `general_amenities`, `safety_and_hygiene` với giá trị `enum`.

Cờ boolean này trùng kiểu nguồn của `get_amenity.md` và `poi_amenity_mapping.md`, nhưng không phải tag hiển thị có sẵn trong payload. `CHILD_KEYS` in 50/70 token.

### D2 — sửa 2026-10-15

Hai tài liệu `get_amenity.md` và `poi_amenity_mapping.md` là rule gom nhóm cho `source_flags_json`. Rule không có khóa nguồn trong JSON đã chứng minh vẫn là `MISSING_EVIDENCE`. Không lọc ngành vì bảng amenity không có `types`.

Người dùng chốt ngày 2026-10-15: hai tài liệu này là cách gom, không còn để ngoài công thức. `detect_category` vẫn không chạy vì `slv_3p_poi_amenity` không có `types` hoặc `primaryType`. Danh sách chuỗi `amenities[]` trong `poi_amenity_mapping.md` mục 7.1, gồm `gym`, `pool`, `spa`, `wifi`, `restaurant`, `bar`, không có khóa tương ứng trong `source_flags_json` đã chứng minh. Những rule đó là `MISSING_EVIDENCE`. Rule boolean và object options có khóa đã thấy thì được dùng.

### D4 — kết quả giữ nguyên

Probe P02 trên Fabric DEV: `source_flags_json` không có object nào chứa khóa `enum`.

Câu «Không viết notebook» hết hiệu lực khi D5 giao transform tự gom nhóm từ cờ boolean.

### D5 — 2026-10-15

Payload cần xử lý là `slv_3p_poi_amenity.source_flags_json`. Ba sample là ví dụ sau khi gom nhóm. Key đích là tên nhóm, value là từng amenity trong nhóm.

Ví dụ người dùng: `gym` và `parking` nằm trong nhóm `general_amenities`. Một dòng là một value. `false` và `null` không sinh dòng. Nhóm không có value thì không sinh dòng. `poi_id` copy từ `slv_3p_poi_amenity`.

Khóa đã chứng minh ở P01 và P02: `flags`, `accessibilityOptions`, `evChargeOptions`, `fuelOptions`, `parkingOptions`, `paymentOptions`. Trong `flags` đã thấy các cờ `allowsDogs`, `curbsidePickup`, `delivery`, `dineIn`, `goodForChildren`, `goodForGroups`, `goodForWatchingSports`, `liveMusic`, `menuForChildren`, `outdoorSeating`, `reservable`, `restroom`, `servesBeer`, `servesBreakfast`, `servesBrunch`, `servesCocktails`, `servesCoffee`, `servesDessert`, `servesDinner`, `servesLunch`, `servesVegetarianFood`. `accessibilityOptions` có `wheelchairAccessibleEntrance`, `wheelchairAccessibleParking`, `wheelchairAccessibleRestroom`, `wheelchairAccessibleSeating`. P02 cắt 20 token khóa con. Registry `NB_CREATE_DDL` còn kê `servesWine` và `takeout` trong `JSON_PICK`. Không lấy tag sample như `Restaurant` hoặc `Free Wi-Fi` khi không có rule với khóa nguồn đã chứng minh.

### D6 — 2026-10-15

Bảng `lh_vv_silver.dbo.slv_3p_poi_amenity_kv` gom `source_flags_json` thành key-value. Nhóm chỉ có `general_amenities` và `accessibility`. Value là snake_case của khóa Google; `restroom` thành `has_restroom`; mọi khóa `parkingOptions` bằng true thành `parking`. `pl_name` đề xuất `PL_VV_TRANS_SLV_3P_AMENITY_KV_1H`, chưa đặt lịch.

Nguồn: `architecture.md` mục 5.1 và Main brief. Architecture verdict `PASS`. Khóa MERGE là `poi_id`, `amenity_group`, `amenity_value`. Chỉ boolean `true` sinh dòng.

26 rule đã chứng minh: 21 cờ trong `$.flags` đã thấy ở P02 vào `general_amenities`; `$.parkingOptions` có bất kỳ khóa true thì một dòng `parking`; bốn khóa `wheelchairAccessible*` vào nhóm `accessibility` với value `wheelchair_accessible_entrance`, `wheelchair_accessible_parking`, `wheelchair_accessible_restroom`, `wheelchair_accessible_seating`.

`MISSING_EVIDENCE`: `$.flags.servesWine`, `$.flags.takeout`, khóa con `$.paymentOptions`. `evChargeOptions` và `fuelOptions` không có rule object trong hai tài liệu. Chuỗi `amenities[]` như `gym`, `pool`, `spa`, `wifi`, `restaurant`, `bar` không có khóa nguồn, nên không sinh các value đó. `parking` vẫn sinh từ `parkingOptions`, không cần tên khóa con.

### D7 — 2026-10-15

Người dùng dừng task. Không viết notebook. Trạng thái `blocked`.

S2 chưa được chọn. `NB_SLV_3P_POI_AMENITY_KV` chưa được tạo. `NB_CREATE_DDL` chưa được sửa. Architecture `PASS` và D6 giữ nguyên trong lịch sử, không được triển khai trong task này.
