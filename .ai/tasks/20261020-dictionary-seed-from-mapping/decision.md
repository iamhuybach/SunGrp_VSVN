# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Lệch seed và mapping | D-02 đến D-05 đã chốt. Mục 1.8 vẫn chỉ có heading cho đến khi implement điền từ `CATEGORY_GROUPS`. 21 token mục 1.7 và hai enum `Car with Driver`, `Campervan Rental` không có Google type: không thêm, vì không nằm trong quy tắc seed đã chốt. Seed giữ nhãn mục 1.5 cho `national_park`, `hiking_area`, `church`, `hindu_temple`, `mosque`, `synagogue`. | request.md Constraints; mapping_place_type.md 1.1–1.7 | 2026-10-20 |
| D-02 | Homestay | Homestay nhận Lodging. | User 2026-10-20 | 2026-10-20 |
| D-03 | Partner cùng hàng | một nhóm khác Other: nếu hàng chỉ có một nhóm khác Other, partner nhận nhóm đó. Token không có trong 1.8 vẫn là Other. Mục 1.8 điền đúng token `CATEGORY_GROUPS` hiện có. | User 2026-10-20; NB_SETUP_POI_ENTITY `CATEGORY_GROUPS` | 2026-10-20 |
| D-04 | Place type chưa có | D-04 thay câu Constraints "không tạo place_type mới" cho các token trong mục 1.9.1 và 1.9.2. Đã có trong `place_type` thì thêm vào dòng đó. Chưa có thì thêm dòng `google`, `business_sector`/`business_category`/`business_category_vi` = `other`, `category_group` = `Other`. Khớp đúng chuỗi; khoảng trắng Latin đổi `_` một lần (`water park` → `water_park` đã có; `night market` → thêm `night_market`). Không gắn nhầm `temple`, `boat`, `hiking`, `wellness`, `shopping`, `mall` sang place_type dài hơn. `suối` và `thác` giữ đúng chữ. `OUTDOOR_TYPES` không có danh sách; không gán `dry_season`. Mọi dòng nhận `default_range`/`avg_range` theo `category_group` ở bảng L193–L201. Bảng đặc biệt L205–L210 ghi đè đúng `place_type` đó. Nhiều rule 1.9.2: priority số nhỏ hơn thắng. Không match thì `candidate_best_time_code` = `all`. `is_active` của dòng mới là `true`, giống `VALUES` hiện tại của MERGE. Mục 1.9.3 không thành dòng seed. Tên cột vật lý và kiểu dữ liệu: D-06. | mapping_place_type.md L193–L231; User 2026-10-20 | 2026-10-20 |
| D-05 | Amenity 2.5 | Liệt kê token. Hãy kiểm tra hiện có và map data tương ứng. Đã có đúng `amenity_raw` thì giữ dòng, không thêm cột alias: `delivery`, `dineIn`, `outdoorSeating`, `liveMusic`, `servesCocktails`, `goodForChildren`, `restroom`, `goodForGroups`, `goodForWatchingSports`, `paymentOptions.acceptsCreditCards`, `accessibilityOptions.wheelchairAccessibleParking`, và ba tên rút gọn trỏ tới `accessibilityOptions.wheelchairAccessibleEntrance`, `accessibilityOptions.wheelchairAccessibleRestroom`, `accessibilityOptions.wheelchairAccessibleSeating`. `parkingOptions.*` chỉ 8 token đã có ở mục 2.1–2.4. Derived amenities chỉ dòng seed đã có (`swimming_pool`, json_type gym/spa/bar/restaurant, `hot_spring`, `sauna`, `garden`, `botanical_garden`, `electric_vehicle_charging_station`). Coworking không có field: không thêm. 17 flag chưa có thì thêm dòng `google` / `other` / `other` / `amenity_raw` / `amenity_raw`: `takeout`, `curbsidePickup`, `reservable`, `servesBreakfast`, `servesLunch`, `servesDinner`, `servesBeer`, `servesWine`, `servesBrunch`, `servesVegetarianFood`, `menuForChildren`, `servesDessert`, `servesCoffee`, `allowsDogs`, `pureServiceAreaBusiness`, `acceptsDebitCards`, `acceptsNfc`. `is_active` = `true` như MERGE hiện tại. | User 2026-10-20; mapping_amenities.md 2.1–2.5 | 2026-10-20 |
| D-06 | Tên cột và kiểu | two_ints: `range_low_min` INT, `range_high_min` INT, `avg_range_min` INT, hai cột best time STRING. Hai cột best time là `candidate_best_time_code` STRING và `canonical_candidate` STRING. Chuỗi `1,200–1,200` hoặc `60–90` tách tại dấu gạch: số trước là `range_low_min`, số sau là `range_high_min`, bỏ dấu phẩy. `avg_range_min` bỏ dấu phẩy. | User 2026-10-20 | 2026-10-20 |
| D-07 | Ba token vừa mới vừa thuộc mục 1.8 | pagoda = Light Sightseeing / Culture & Nature, night_market = Shopping & Nightlife, theme_park = Heavy Entertainment với 180/360/270. | User 2026-10-20 | 2026-10-20 |
| D-08 | `slv_poi_amenity` nullable | `rebuild_amenity`. User DROP `slv_poi_amenity` rồi để `NB_SETUP_POI_AMENITY` tạo lại bảng rỗng với `NOT NULL`. Không `ALTER COLUMN`. Seed `ref_dictionary_amenities` vẫn là MERGE của notebook đó. 58 dòng amenity hiện có chỉ trở lại khi chạy 1H. | User 2026-10-20 | 2026-10-20 |
| D-09 | `service_flags` mục 2.5 | Cột `service_flags` STRING NULL trên `ref_dictionary_amenities`. Raw thuộc danh sách mục 2.5 thì gán đúng nhãn trên dòng đã có. Raw có trong mapping nhưng chưa có trong bảng thì thêm dòng `google` / `other` / `other`, `amenity` = `amenity_vi` = `amenity_raw`, và gán nhãn. Nhãn: `Food/service`, `Suitability`, `Payment`, `Parking`, `Accessibility`, `Derived amenities`. `parkingOptions.*` gắn `Parking` cho raw đã có, gồm raw bắt đầu bằng `parkingOptions.`. Accessibility gắn raw `accessibilityOptions.` đã có. Derived gắn raw seed đã có. Coworking không thêm. Câu D-05 "không thêm cột alias" không áp cho cột này. | User 2026-10-20 | 2026-10-20 |
| D-10 | Bỏ qua R10 | User bỏ qua lần chạy `PL_VV_TRANS_SLV_TO_SLV_1H`. Không có kết quả cạnh `TABLE_RECREATED`. `gates.runtime` giữ `pending`. | User 2026-10-20 | 2026-10-20 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Runbook R2 không dùng `CREATE TABLE IF NOT EXISTS`. Nếu bảng `*_bak_20261020` đã có thì dừng. Backup chọn cột tường minh và `EXCEPT ALL` hai chiều phải ra 0 dòng trước DROP. Bước chạy lại `p_apply=true` nằm trước R10, khi 1H vẫn tắt. GATE-001 và GATE-002.
- R6b: DROP `slv_poi_amenity` rồi chạy lại `NB_SETUP_POI_AMENITY`. D-08. Không `ALTER COLUMN`.
- D-09: thêm cột `service_flags`. Kiến trúc trước đó chỉ thêm 17 dòng `other`/`other` và không thêm cột. User yêu cầu gắn nhãn mục 2.5 trên đúng `amenity_raw`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | `runtime-runbook.md` L21–L61: dừng nếu backup đã tồn tại; `CREATE TABLE` cột tường minh; bốn câu `EXCEPT ALL` hai chiều = 0 dòng trước DROP. Trích `evidence/results/runbook_excerpt.txt`. | |
| GATE-002 | P1 | fixed | L74–L75 rồi L97–L101: `p_apply=true` chạy lại trước R10, khi 1H vẫn tắt và Monitor không có run active. Trích cùng file. | |

### GATE-001

`runtime-runbook.md` L23 dừng nếu `*_bak_20261020` đã tồn tại. L30–L35 tạo backup bằng `CREATE TABLE` (không `IF NOT EXISTS`) với cột tường minh. L41–L60 là bốn câu `EXCEPT ALL` hai chiều, mỗi câu phải 0 dòng trước mọi `DROP`.

### GATE-002

Thứ tự trong `runtime-runbook.md`: L74 chạy lại idempotency khi 1H vẫn tắt và Monitor không có run active; L75 R10 chỉ bật `PL_VV_TRANS_SLV_TO_SLV_1H` sau kiểm tra đó. L99–L101 nhắc lại: `NB_SETUP_POI_ENTITY` rồi `NB_SETUP_POI_AMENITY`, `p_apply` = `true`, kỳ vọng `inserted=0`, `drift=0`, trước R10.

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- D-02: Homestay nhận Lodging.
- D-03: một nhóm khác Other: nếu hàng chỉ có một nhóm khác Other, partner nhận nhóm đó. Token không có trong 1.8 vẫn là Other.
- D-04: Đọc mapping_place_type.md dòng 203 và 216. Chưa có place_type thì thêm `other` / `Other`.
- D-05: Liệt kê token. Kiểm tra hiện có và map data tương ứng.
- D-06: two_ints: `range_low_min` INT, `range_high_min` INT, `avg_range_min` INT, hai cột best time STRING.
- D-07: pagoda = Light Sightseeing / Culture & Nature, night_market = Shopping & Nightlife, theme_park = Heavy Entertainment với 180/360/270.
- D-08: User DROP `slv_poi_amenity` và init lại. Không ALTER.
- D-09: Mục 2.5 thêm cột `service_flags` đúng nhãn. Raw đã có thì gán. Raw chưa có thì `other`/`other`, `amenity` = `amenity_vi` = `amenity_raw`.
- D-10: Bỏ qua R10. Không chạy 1H. `gates.runtime` giữ `pending`.

## Lịch sử quyết định

- 2026-10-20: Triage đối chiếu seed với mapping. Mở D-02 đến D-05.
- 2026-10-20: User chốt D-02 và D-03. D-04 lấy nguyên câu dòng 203 và 216. D-05 đối chiếu `amenity_raw`: token parking và derived đã có trong mục 2.1–2.4 và trong `SEED_ROWS`; 17 flag chưa có được thêm theo quy tắc mục 2.5. `OUTDOOR_TYPES` không có trong `mapping_place_type.md` và không có trong `notebooks/`.
- 2026-10-20: `run-author --kind model` ghi `model-design.md`, model `claude-opus-5-5`, effort medium. MERGE hiện gán `is_active` = `true`. Câu hỏi 2 và 3 của model design thành D-06.
- 2026-10-20: User chọn D-06 `two_ints`.
- 2026-10-20: `run-gate` architecture PASS, model `claude-opus-5-5`, effort high. Stop 0 thêm `tests/test_initial_ddl_contract.py` và `docs/context/01_DATA_MODEL.md` vào `scope.files`. Stop 1 mở D-07. Chưa sửa notebook.
- 2026-10-20: User chọn D-07 mục 1.8.
- 2026-10-20: Review vòng 1 `FIX_REQUIRED`. GATE-001 và GATE-002 sửa trong `runtime-runbook.md`.
- 2026-10-20: User duyệt thêm một vòng review. `review_plan.extra_round_approved_on` = `2026-10-20`.
- 2026-10-20: Review vòng 3 `EVIDENCE_REQUIRED`. GATE-001 và GATE-002 được xác nhận `fixed`. Không còn P0/P1. Phần còn lại là runtime Fabric DEV, R3–R10. Agent không đánh `gates.runtime`.
- 2026-10-20: User chạy R5 thành công: `inserted=387`, `drift=0`. R6 lỗi `ConfigError`: `slv_poi_amenity` có `poi_id`, `business_sector`, `amenity_group`, `amenity_raw` nullable, notebook cần NOT NULL. Chưa seed amenities. 1H tiếp tục tắt.
- 2026-10-20: Probe `amenity_nulls.sql`: từ điển amenities 0 dòng; `slv_poi_amenity` 58 dòng; bốn cột khóa 0 NULL.
- 2026-10-20: User chọn DROP `slv_poi_amenity` và init lại. D-08 đổi từ `alter_not_null` sang `rebuild_amenity`.
- 2026-10-20: User chạy lại amenities thành công: `inserted=175`, `drift=0`, `stale=0`. Kết quả chưa đúng vì chưa có `service_flags`. D-09.
- 2026-10-20: R6c sau DROP `ref_dictionary_amenities`: `inserted=175`, `drift=0`. `service_flags` NULL 107, Accessibility 9, Derived amenities 12, Food/service 20, Parking 12, Payment 3, Suitability 12. Khớp D-09. `evidence/results/r6c-service-flags.txt`.
- 2026-10-20: User xác nhận R8 đạt, R9 in đúng hai dòng cột, idempotency hai notebook `inserted=0` `drift=0`. `evidence/results/r8-r9-idempotent.txt`. 1H vẫn tắt.
- 2026-10-20: User bỏ qua R10 và yêu cầu commit, push `main`. D-10. Agent không đánh `gates.runtime`.
