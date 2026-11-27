RESULT: EVIDENCE_REQUIRED

# Problem analysis — 20261127-slv-pn-product-business-mapping

## Phạm vi

- Task gốc: `20261127-slv-pn-product-business-mapping` (`.ai/tasks/20261127-slv-pn-product-business-mapping/request.md`, `## User outcome`). `task-state.yaml` đang ở `status: triage`, `complexity: low`, `risk_level: low`, `architecture_required: false`, `evidence_required: false` (`task-state.yaml`, `task`, `classification`).
- Câu hỏi đang phân tích: có thể đặt rule nghiệp vụ partner product legacy (`docs/context/mapping_legacy_ai_product.md` §1.1–§1.13 và các cell tương ứng của `notebooks_lgc/pl_transform_partner_userprofile_cms/5. nb_prepare_product_for_ingestion.ipynb`) lên 13 bảng silver L1 hiện hành không, với mỗi dòng Field Mapping trỏ tới một cột có trong `TABLE_SPECS` của `notebooks/NB_SETUP_INITIAL_DDL.ipynb`. Nếu không thì khoảng trống nằm ở đâu.
- Tài liệu này chỉ phân tích bài toán. Nó không đề xuất giải pháp, không thiết kế model, và không chốt rule field nào.
- Ledger `Quyết định hiện hành` trong `decision.md` đang trống (`decision.md`, `## Quyết định hiện hành`). Chưa có quyết định nào của người dùng (`decision.md`, `## Quyết định của người dùng`: "Chưa có.").

## Bài toán

Theo `request.md` (`## User outcome`, `## Scope`, `## Acceptance criteria`), người dùng muốn:

- Có một tài liệu `docs/context/mapping_slv_pn_product.md` map rule nghiệp vụ partner product legacy lên model silver L1 hiện hành, dùng khung của `docs/context/mapping_gld_srv_poi_info.md`.
- Mỗi bảng `slv_pn_products`, `slv_pn_product_translations`, `slv_pn_product_attributes`, `slv_pn_product_attribute_translations`, `slv_pn_product_attribute_values`, `slv_pn_product_attribute_value_translations`, `slv_pn_product_variants`, `slv_pn_product_variant_translations`, `slv_pn_product_business_service_relation`, `slv_pn_product_posts`, `slv_pn_product_post_translations`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans` có đúng một mục `##`. Mỗi mục có `Lakehouse.schema`, `### Xử lý`, `### Field Mapping` (`Source Field | Data Type | Transform | Target Field`), và thêm một mục transform riêng khi rule không vừa bảng.
- Mọi dòng Field Mapping trỏ tới một cột có trong `TABLE_SPECS`. Cột hoặc bảng không có trong `TABLE_SPECS` thì không được bịa dòng mapping. Rule legacy, chỗ lệch và câu hỏi đi vào `Câu hỏi cần chốt`.
- Hotel và mọi lựa chọn còn mở (grain đích nếu khác silver L1, `source_id`, destination, giá NULL, xoá mềm) giữ ở dạng câu hỏi cho tới khi người dùng chốt. Phải phân tích nhánh hotel, và hỏi rõ hotel có thuộc phạm vi mapping đã chốt không.
- Không mang sang thiết kế đích: một dòng product kèm `variants_json`, join `ai_poi` / `ai_enriched_poi`, remap `destination_id` hardcode, cache dịch, bước LLM nào. Không map Azure OpenAI, `gpt-4.1`, `ENABLE_TRANSLATION`, `ai_product_translation`. Tên tiếng Anh chỉ lấy từ bản dịch theo locale đã có sẵn trên nguồn (`request.md`, `### Out of scope`).

## Hiện trạng

### Khung tài liệu mẫu

- `docs/context/mapping_gld_srv_poi_info.md` dùng khung `# Mapping ...`, `## 1. Table: <bảng>`, `### 1.1. Xử lý`, `### 1.2. Field Mapping`, rồi các mục transform riêng `### 1.3`… (`mapping_gld_srv_poi_info.md`, heading frame). Bảng Field Mapping có cột `Source Field | Data Type | Transform | Target Field` (`mapping_gld_srv_poi_info.md`, `### 1.2. Field Mapping`).

### Model silver L1 hiện hành

- `01_DATA_MODEL.md` `### 5.1 Partner`: nhóm `slv_pn_*` có 23 bảng, `load_mode = CDC`, ghi bởi `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`. Mỗi dòng là một dòng bảng Postgres, lấy bản mới nhất. Cột lấy từ `ctrl_cfg_schema_registry`.
- Cũng theo `### 5.1 Partner`: cột kỹ thuật gồm `deleted` (xoá mềm khi `op = d`), `_source_db`, `created_at`, `updated_at`, trong đó hai cột audit có kiểu `timestamp`. Cột thời điểm nguồn `created_at` / `updated_at` được lưu với tên `src_created_at` / `src_updated_at`.
- Cả 13 bảng trong phạm vi đều có trong bảng `### 5.1 Partner`, khoá `id`. Số cột như sau: `slv_pn_products` 10, `slv_pn_product_translations` 7, `slv_pn_product_attributes` 8, `slv_pn_product_attribute_translations` 6, `slv_pn_product_attribute_values` 7, `slv_pn_product_attribute_value_translations` 4, `slv_pn_product_variants` 9, `slv_pn_product_variant_translations` 6, `slv_pn_product_business_service_relation` 5, `slv_pn_product_posts` 19, `slv_pn_product_post_translations` 15, `slv_pn_hotel_room_types` 25, `slv_pn_hotel_rate_plans` 19. Mục này chỉ ghi tên bảng, khoá, số cột, số cột TOAST và wave. Nó không liệt kê tên cột.
- Ghi chú dữ liệu trong `### 5.1 Partner` (rerun 04/10): 11 bảng (`products`, 9 bảng `product_*` và `order_item_flights`) có `after = ''` ở 100% event, nên ra NO_DATA / reject. `product_post_translations` không có event nào trong raw.
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, đoạn `TABLE_SPECS` giữa `BEGIN_INIT_TABLE_SPECS` và `END_INIT_TABLE_SPECS`: không có block nào tên `slv_pn_product*` hay `slv_pn_hotel*`. Trong đoạn này, chữ `product` chỉ xuất hiện ở hai chuỗi mô tả cột của bảng control (`src_object` "vd products" và `trg_tbl` "vd slv_products"). Tên 13 bảng chỉ xuất hiện sau `END_INIT_TABLE_SPECS`, trong một cell cấu hình và trong các dòng seed `(_FL00, _B, 'partner_raw_data', _S, 'slv_pn_...', 1, <wave>, 'CDC', ...)`. Các vùng đó nằm ngoài vùng được giao đọc.
- `request.md` `## Constraints` và author input nêu: partner product là silver L1, grain một dòng nguồn, khoá `id`, notebook `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, chưa có bảng gold product và chưa có notebook transform product. Grain, khoá và notebook khớp với `01_DATA_MODEL.md` `### 5.1 Partner`.

### Rule nghiệp vụ legacy (`mapping_legacy_ai_product.md`)

- §1.1: legacy đích là `lh_vv_gold.dbo.ai_product`, một dòng cho mỗi `product_id`, variant lồng trong `variants_json`. Bảng được ghi `overwrite`, đúng 25 cột theo `ORDERED` (cell 16). Có hai domain: holiday (`product_type = 'other'`, luôn build) và hotel (`product_type = 'hotel'`, chỉ chạy khi `ENABLE_HOTEL = True`, mặc định `False`). Tham số mặc định nằm ở cell 1.
- §1.1: bronze được đọc qua `read_src`, không lọc bản ghi CDC và không dedup theo `id`. Bảng đọc gồm `products` (có `metadata`), `product_translations` (`name`, `description`, `locale = 'vi'`), `product_variants` (`attributes`, `status`, xoá mềm), `product_variant_translations`, cặp `product_attributes` + translation, cặp `product_attribute_values` + translation (khoá join là `attribute_id` của bảng translation, trỏ tới `product_attribute_values.id`), `product_business_service_relation`, `product_posts` (giá, markup, `raw_sync_data`), và `hotel_room_types` / `hotel_rate_plans` khi bật hotel.
- §1.1, rule xoá mềm `soft_deleted` cho `products`, `product_variants`, `hotel_room_types`, `hotel_rate_plans`: bản ghi bị xoá khi `deleted` là `1`/`true`, hoặc khi `deleted_at` khác NULL và đã ở quá khứ. `product_posts` dùng rule khác: `deleted_at IS NOT NULL`.
- §1.1, thứ tự build holiday: join `products.metadata.holiday_product_post_id = product_posts.external_id`. Product có hơn một `business_service_id` thì bị loại. `source_id` lấy `business_service_id` từ relation, nếu không có thì từ post. `destination_id` lấy qua `ai_poi`, rồi remap, rồi fallback. Cuối cùng lọc theo `ai_enriched_poi`.
- §1.1: `source_id` legacy là `business_service_id` thô. Mục này ghi rằng trong VSVN mới, `poi_id` partner = `uuid_md5(business_service_id, 'partner')`.
- §1.2: Field Mapping legacy có 25 cột đích, cùng danh sách cột trung gian không được ghi ra.
- §1.3: rule `is_active` / `is_bookable`, gồm `use_date_gate` và `diff_post_gate`.
- §1.4: giải mã CDC decimal cho `original_price`, `marketing_price` (scale 4) và `markup_percent` (scale 2).
- §1.5: suy đơn vị epoch từ độ lớn, áp cho `deleted_at` và `products.updated_at`.
- §1.6, hotel (cell 15): một dòng cho mỗi `hotel_room_types.id`. Rate plan gắn theo khách sạn. `is_active` so `status = 'Active'` (chữ hoa). `is_bookable` xét `business_service_id` và `available_rooms`. Giá default về `0`. `variants_json` dựng từ `hotel_rate_plans`. `product_attributes` là JSON phòng. Có map mã `meal_plan`. `updated_at = current_timestamp()`. Mục này ghi rõ notebook không có output hotel.
- §1.7: cache dịch và Azure OpenAI. Theo `request.md` đây là phần loại trừ, không phân tích tiếp.
- §1.8: resolve `variants_json` và `attributes`, gồm bảng `attr_code` → `attr_name_en` → axis.
- §1.9: axis là `collect_set` trên các variant chưa xoá.
- §1.10: `product_attributes` holiday lấy từ `product_posts.raw_sync_data` (`translations[].languageCode`, `shortDescription`, `tags[].label` / `tags[].code`).
- §1.11: `source_id` / `destination_id` qua `ai_poi`, `DESTINATION_ID_REMAP` và fallback.
- §1.13: các điểm cần lưu ý, gồm `variants_json` lặp phần tử, bronze không dedup, `updated_at` lệch giữa code và output, hai id "Da Nang", `lang = 'en'` trong khi tên là tiếng Việt, product hoặc variant đã xoá mềm vẫn được ghi, `'active'` và `'Active'` lệch hoa thường, `product_posts` xoá mềm khác các bảng còn lại, giá NULL thành `0`, cell lặp code.

## Khoảng trống hoặc nguyên nhân

1. **Không có spec cột trong `TABLE_SPECS` cho 13 bảng.** Theo `## Hiện trạng`, mục DDL, đoạn `TABLE_SPECS` không có block `slv_pn_product*` / `slv_pn_hotel*`. Tiêu chí "Every Field Mapping row names a column that exists in `TABLE_SPECS`" (`request.md`, `### In scope`) vì vậy không kiểm được cho dòng nào. `01_DATA_MODEL.md` `### 5.1 Partner` chỉ cho số cột, không cho tên cột. Đây là khoảng trống bằng chứng, dẫn tới `EVIDENCE_REQUIRED`.
2. **Không xác nhận được các cột nguồn mà rule legacy dùng có tồn tại ở silver hay không.** Hệ quả của khoảng trống 1: các file được giao không cho biết silver có những cột sau.
   - `slv_pn_products`: `status`, `product_line`, `metadata`, `deleted_at`, `updated_at` (§1.1, §1.2). Riêng `updated_at` có thể đã đổi tên thành `src_updated_at` theo `### 5.1 Partner`.
   - `slv_pn_product_translations`: `product_id`, `locale`, `name`, `description` (§1.1).
   - `slv_pn_product_variants`: `product_id`, `status`, `attributes`, `deleted_at` (§1.1, §1.8).
   - `slv_pn_product_variant_translations`: `variant_id`, `locale`, `name` (§1.8).
   - `slv_pn_product_attributes` / `slv_pn_product_attribute_translations`: `code` và cột tên (§1.1).
   - `slv_pn_product_attribute_values` / `slv_pn_product_attribute_value_translations`: `value_code`, `attribute_id`, `name`, `locale` (§1.1, §1.8).
   - `slv_pn_product_business_service_relation`: `product_id`, `business_service_id` (§1.1).
   - `slv_pn_product_posts`: `external_id`, `business_service_id`, `original_price`, `marketing_price`, `markup_percent`, `raw_sync_data`, `status`, `deleted_at` (§1.1, §1.2, §1.3).
   - `slv_pn_hotel_room_types`: `name`, `status`, `business_service_id`, `available_rooms`, `description`, `meal_plan`/`view_type` và các cột sức chứa (§1.6).
   - `slv_pn_hotel_rate_plans`: `name`, `status`, `kind`, `valid_from`, `valid_to`, `include_tax`, `include_service_charge`, `meal_plan` (§1.6).
3. **Không xác nhận được kiểu dữ liệu và JSON shape ở silver.** Rule §1.4 giải mã decimal dạng bytes/base64 và §1.5 suy đơn vị epoch. Cả hai giả định kiểu của bronze. Các file được giao không cho biết silver lưu giá và `deleted_at` dưới kiểu gì. JSON shape của `products.metadata` (key `holiday_product_post_id`, §1.1), `product_variants.attributes` (map `attr_code → value_code`, §1.8) và `product_posts.raw_sync_data` (`translations[]`, `tags[]`, §1.10) chỉ có trong tài liệu legacy, dạng "minh họa theo code, không phải dữ liệu bronze thật" (`mapping_legacy_ai_product.md`, dòng nguồn đầu tài liệu). Silver giữ các cột này dưới dạng JSON string, struct hay đã tách cột thì chưa có bằng chứng.
4. **Rule xoá mềm lệch với model silver.** Legacy dựa trên `deleted` / `deleted_at` của nguồn (§1.1, §1.5). Silver có cột kỹ thuật `deleted` mang nghĩa xoá khi `op = d` (`### 5.1 Partner`). Hai nghĩa này khác nhau, và các file không cho biết `deleted_at` nguồn còn ở silver không. Đây là lựa chọn còn mở.
5. **Grain lệch.** Legacy ghi một dòng cho mỗi `product_id`, variant lồng trong `variants_json`. Hotel ghi một dòng cho mỗi `hotel_room_types.id` (§1.1, §1.6). Silver L1 là một dòng nguồn cho mỗi bảng, khoá `id` (`### 5.1 Partner`). `request.md` loại trừ `variants_json`. Vì vậy các rule gộp (§1.8, §1.9, `variant_count`, `is_bookable` §1.3) không có bảng đích tương ứng ở silver L1. Grain đích khác L1 là lựa chọn còn mở.
6. **Thiếu đích cho `source_id` / `destination_id`.** Legacy lấy `destination_id` qua `ai_poi`, remap hardcode và fallback (§1.11). Cả ba đều bị loại trừ (`request.md`, `### Out of scope`). Các file không cho thấy nguồn destination nào khác cho product. Ngoài ra §1.1 ghi `source_id` thô khác với khóa `poi_id` partner đã hash.
7. **Có thể không có dữ liệu.** `### 5.1 Partner` ghi 10 bảng product có `after = ''` ở 100% event và `product_post_translations` không có event. Đây chỉ là trạng thái dữ liệu tại rerun 04/10, không phải lỗi mapping. Nhưng nó có nghĩa là các file được giao không chứa dữ liệu silver thật để đối chiếu JSON shape.
8. **Hotel chưa có bằng chứng chạy.** §1.6 ghi không có output hotel trong notebook, và §1.1 ghi `ENABLE_HOTEL` mặc định `False`. Hotel có thuộc phạm vi mapping không là lựa chọn còn mở.
9. **Giá NULL.** Legacy ghi `0` khi giá NULL, nên không phân biệt "không có giá" với "giá 0" (§1.2, §1.13 điểm 9). Đây là lựa chọn còn mở.
10. **Tên tiếng Anh.** Legacy lấy `product_name_en` từ cache hoặc LLM, mặc định là tên tiếng Việt (§1.7, §1.13 điểm 5). `request.md` chỉ cho lấy từ locale đã có trên nguồn. Các file không cho biết `slv_pn_product_translations` hay `slv_pn_product_post_translations` có dòng locale tiếng Anh không, và cột locale tên gì.

## Đối tượng bị ảnh hưởng

- **Bảng silver** (`lh_vv_silver.dbo`, theo `01_DATA_MODEL.md` `### 5.1 Partner`): 13 bảng trong `## Bài toán`.
- **Notebook**:
  - `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` là notebook ghi các bảng trên. Chỉ tham chiếu, không sửa.
  - `notebooks/NB_SETUP_INITIAL_DDL.ipynb` (`TABLE_SPECS`) là nguồn mà tiêu chí cột dựa vào. Không sửa.
  - `notebooks_lgc/pl_transform_partner_userprofile_cms/5. nb_prepare_product_for_ingestion.ipynb` (cell 1, cell 15, cell 16) là nguồn rule legacy.
- **Cấu hình**: `ctrl_cfg_schema_registry` là nguồn cột của `slv_pn_*` (`### 5.1 Partner`). Các dòng seed `partner_raw_data` → `slv_pn_*` nằm trong `NB_SETUP_INITIAL_DDL.ipynb`, sau `END_INIT_TABLE_SPECS`.
- **Tài liệu**:
  - `docs/context/mapping_slv_pn_product.md` là sản phẩm sẽ tạo.
  - `docs/context/mapping_legacy_ai_product.md` là nguồn rule.
  - `docs/context/mapping_gld_srv_poi_info.md` là khung mẫu.
  - `decision.md` của task là ledger.
- **Consumer**: legacy đọc là `lh_vv_gold.dbo.ai_product` (§1.1). Ở repo hiện tại chưa có bảng gold product hay notebook transform product (`request.md`, `## Constraints`). Các file được giao không nêu consumer nào khác.

## Câu hỏi

1. **Evidence, spec cột.** `TABLE_SPECS` không có block `slv_pn_product*` / `slv_pn_hotel*`. Nguồn chuẩn cho tên cột và kiểu của 13 bảng là gì: `ctrl_cfg_schema_registry`, cell cấu hình partner sau `END_INIT_TABLE_SPECS` trong `NB_SETUP_INITIAL_DDL.ipynb`, hay schema Delta thật? Có cần sửa tiêu chí "column exists in `TABLE_SPECS`" sang nguồn đó không?
2. **Evidence, cột nguồn mà rule dùng.** Với từng cột trong khoảng trống 2, silver có cột đó không, tên gì và kiểu gì? Cụ thể: `slv_pn_products.updated_at` có phải là `src_updated_at` không, và `deleted_at` nguồn còn được giữ không.
3. **Evidence, kiểu giá.** `slv_pn_product_posts.original_price`, `marketing_price`, `markup_percent` ở silver là số đã giải mã hay vẫn là bytes/base64 như rule §1.4 giả định?
4. **Evidence, kiểu thời điểm.** `deleted_at` và thời điểm cập nhật nguồn ở silver là epoch (đơn vị nào) hay `timestamp`? Rule §1.5 còn áp được không?
5. **Evidence, JSON shape `products.metadata`.** Shape ở silver là gì? Có key `holiday_product_post_id` mà §1.1 dùng để join `product_posts.external_id` không?
6. **Evidence, JSON shape `product_variants.attributes`.** Shape ở silver là gì? Có còn dạng map `attr_code → value_code` như §1.8 không?
7. **Evidence, JSON shape `product_posts.raw_sync_data`.** Shape ở silver là gì? Có `translations[].languageCode`, `shortDescription`, `tags[].label` / `tags[].code` như §1.10 không? `slv_pn_product_post_translations` có thay thế được `raw_sync_data.translations[]` không?
8. **Evidence, khoá join thuộc tính.** Ở silver, `slv_pn_product_attribute_value_translations` có cột `attribute_id` trỏ tới `slv_pn_product_attribute_values.id` như §1.1 ghi không? Bảng này chỉ có 4 cột theo `### 5.1 Partner`.
9. **Evidence, cột hotel.** Ở silver, `slv_pn_hotel_room_types` và `slv_pn_hotel_rate_plans` có các cột mà §1.6 dùng không: `available_rooms`, `meal_plan`, `view_type`, các cột sức chứa, `kind`, `valid_from`, `valid_to`, `include_tax`, `include_service_charge`, `business_service_id`? Cột tiện ích (amenity) nằm ở đâu?
10. **Evidence, dữ liệu.** Sau rerun 04/10, các bảng `slv_pn_product*` đã có dữ liệu chưa (`### 5.1 Partner` ghi `after = ''` ở 100% event)? Nếu chưa, JSON shape ở câu 5–7 được xác nhận bằng nguồn nào?
11. **Hotel.** Nhánh hotel (`mapping_legacy_ai_product.md` §1.6, notebook cell 15, `ENABLE_HOTEL` mặc định `False`, không có output) có thuộc phạm vi mapping đã chốt không?
12. **Grain đích.** Rule ở cấp product (§1.3 `is_bookable`, §1.8–§1.9 axis, `variant_count`) có được giữ ở dạng rule nghiệp vụ trên từng bảng silver L1 không? Hay grain đích khác silver L1, và nếu khác thì là grain nào?
13. **`source_id`.** Khóa nối product sang POI là `business_service_id` thô (§1.1, §1.11) hay `uuid_md5(business_service_id, 'partner')` (§1.1)? Product có nhiều `business_service_id` thì xử lý ra sao (legacy loại hẳn)?
14. **Destination.** Khi bỏ `ai_poi`, `DESTINATION_ID_REMAP` và fallback (§1.11), `destination_id` của product lấy từ đâu, hay không map?
15. **Giá NULL.** Giá NULL giữ là NULL hay default `0` như legacy (§1.2, §1.13 điểm 9)?
16. **Xoá mềm.** Ở silver, xoá mềm dùng cột kỹ thuật `deleted` (`op = d`), `deleted_at` nguồn, hay cả hai? `product_posts` có giữ rule riêng (`deleted_at IS NOT NULL`) không? Bản ghi đã xoá có giữ lại kèm cờ như legacy không (§1.1, §1.13 điểm 6, 8)?
17. **Chuẩn hoá `status`.** Legacy so `'active'` cho holiday và `'Active'` cho hotel (§1.13 điểm 7). Phép so có phân biệt hoa thường không?
18. **Locale tiếng Anh.** Bảng translation nào ở silver có locale tiếng Anh cho tên product và tên variant? Giá trị locale cụ thể là gì? Các file được giao không cho biết tên cột locale hay giá trị của nó.
