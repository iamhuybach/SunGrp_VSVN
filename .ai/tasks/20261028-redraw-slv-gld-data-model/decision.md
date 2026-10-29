# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Drawio có cột, lệch skill | File `docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio` là sản phẩm của task. Skill `vsvn-data-model-flow` mục Diagram chỉ Mermaid, không cột. Task này vẽ swimlane có cột. Không sửa skill và không thêm danh sách bảng vào skill. | Yêu cầu user, mục Ràng buộc riêng; skill mục Diagram | 2026-10-28 |
| D-02 | Nguồn bảng của sơ đồ | User 2026-10-28: các bảng trong file drawio chỉ là sample; vẽ thay thế trực tiếp trong `docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio`, không dựa vào hình vẽ cũ. Danh sách thẻ lấy từ bảng kiểm: registry L1 và `TABLE_SPECS`. Bảng chỉ có trong §6 hoặc §6.1 mà không có trong `TABLE_SPECS` không có thẻ. `gld_enr_poi_coordinate` nguồn cột MISSING, không có thẻ. | Lời user 2026-10-28; `## Bảng kiểm` | 2026-10-28 |
| D-03 | Bố cục tầng, không đường nối | User 2026-10-28: chưa thấy gold; tách Silver L1 và L2; bỏ các đường nối. Một trang, ba dải: Silver L1 (registry `slv_pn_*`, `slv_3p_*`), Silver L2 (bảng silver trong `TABLE_SPECS`), Gold (`lh_vv_gold.enr`, `lh_vv_gold.dbo`). Không có mũi tên. | Lời user 2026-10-28 | 2026-10-28 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có. Phân loại không yêu cầu architecture.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- D-02 đã chốt 2026-10-28: vẽ theo registry và `TABLE_SPECS`, không chép bảng sample.

## Bảng kiểm

Nguồn cột L1 là registry seed (`id:init_cfg_partner`, `id:init_cfg_3p`) sau `flatten_table_configs`. Grain L1 là cột `is_key` theo `key_order`. L1 không có node riêng. Nguồn cột bảng trong `TABLE_SPECS` là `id:init_tables`. Grain node là `pk` của NodeSpec. Không có `pk` và không có `is_key` thì grain ghi không khai báo.

NodeSpec `inputs` khớp cạnh ctrl `is_active = 1` của cùng target. Không CONFLICT ở chỗ này. Cạnh `slv_3p_poi_opening_hours` → `gld_enr_poi_info` có `is_active = 0` và không có trong NodeSpec.

`01_DATA_MODEL` §5.1: số cột partner khớp registry. §8: `poi_id`, `review_id` (`HASH_SHA256`), `media_dedup_key` (`HASH_SHA256_PIPE`) khớp registry. §6 dòng N6 và N7 khớp `pk` và `inputs` của `NB_SLV_POI_ENTITY_NON_ENRICH` và `NB_SLV_POI_AMENITY`.

| Bảng | Schema | Grain | Notebook | Nguồn cột |
|---|---|---|---|---|
| `slv_pn_products` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_product_translations` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_product_attributes` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_product_attribute_translations` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_product_attribute_values` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_product_attribute_value_translations` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_product_variants` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_product_variant_translations` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_product_business_service_relation` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_product_posts` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_product_post_translations` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_partners` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_business_services` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_business_locations` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_hotel_room_types` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_hotel_rate_plans` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_business_service_i18ns` | `lh_vv_silver.dbo` | (`business_service_id`, `locale`) | không có node | registry partner |
| `slv_pn_business_service_poi_link` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_orders` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_order_refs` | `lh_vv_silver.dbo` | `id` | không có node | registry partner |
| `slv_pn_order_item_tickets` | `lh_vv_silver.dbo` | `order_ref_id` | không có node | registry partner |
| `slv_pn_order_item_hotels` | `lh_vv_silver.dbo` | `order_id` | không có node | registry partner |
| `slv_pn_order_item_flights` | `lh_vv_silver.dbo` | `order_id` | không có node | registry partner |
| `slv_3p_poi` | `lh_vv_silver.dbo` | `poi_id` | không có node | registry 3p, 9 cột active |
| `slv_3p_poi_address` | `lh_vv_silver.dbo` | `poi_id` | không có node | registry 3p, 11 cột active |
| `slv_3p_poi_contact` | `lh_vv_silver.dbo` | `poi_id` | không có node | registry 3p, 4 cột active |
| `slv_3p_poi_price` | `lh_vv_silver.dbo` | `poi_id` | không có node | registry 3p, 5 cột active |
| `slv_3p_poi_opening_hours` | `lh_vv_silver.dbo` | `poi_id` | không có node | registry 3p, 4 cột active |
| `slv_3p_poi_rating` | `lh_vv_silver.dbo` | `poi_id` | không có node | registry 3p, 3 cột active |
| `slv_3p_poi_amenity` | `lh_vv_silver.dbo` | `poi_id` | không có node | registry 3p, 2 cột active |
| `slv_3p_poi_review` | `lh_vv_silver.dbo` | `review_id` | không có node | registry 3p, 7 cột active |
| `slv_3p_poi_media` | `lh_vv_silver.dbo` | `media_dedup_key` | không có node | registry 3p, 8 cột active |
| `ref_dictionary_place_type` | `lh_vv_silver.dbo` | không khai báo | không có node | `TABLE_SPECS` |
| `ref_dictionary_amenities` | `lh_vv_silver.dbo` | không khai báo | không có node | `TABLE_SPECS` |
| `slv_poi_entity_non_enrich` | `lh_vv_silver.dbo` | `poi_id` | `NB_SLV_POI_ENTITY_NON_ENRICH` | `TABLE_SPECS` |
| `slv_poi_amenity` | `lh_vv_silver.dbo` | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) | `NB_SLV_POI_AMENITY` | `TABLE_SPECS` |
| `slv_poi_media_info` | `lh_vv_silver.dbo` | `media_id` | `NB_SLV_POI_MEDIA_INFO` | `TABLE_SPECS` |
| `slv_enr_poi_info_multi_lang` | `lh_vv_silver.dbo` | không khai báo | không có node | `TABLE_SPECS` |
| `slv_enr_poi_destination` | `lh_vv_silver.dbo` | không khai báo | không có node | `TABLE_SPECS` |
| `slv_enr_poi_review_multi_lang` | `lh_vv_silver.dbo` | không khai báo | không có node | `TABLE_SPECS` |
| `gld_enr_poi_info` | `lh_vv_gold.enr` | `poi_id` | `NB_ENR_POI_INFO` | `TABLE_SPECS` |
| `gld_enr_poi_review` | `lh_vv_gold.enr` | `review_id` | `NB_ENR_POI_REVIEW` | `TABLE_SPECS` |
| `gld_srv_poi_multi_lang` | `lh_vv_gold.dbo` | (`poi_id`, `lang`) | `NB_GLD_SRV_POI_MULTI_LANG` | `TABLE_SPECS` |
| `gld_srv_poi_info` | `lh_vv_gold.dbo` | `poi_id` | `NB_GLD_SRV_POI_INFO` | `TABLE_SPECS` |
| `gld_srv_poi_media_gallery` | `lh_vv_gold.dbo` | `media_id` | `NB_GLD_SRV_POI_MEDIA_GALLERY` | `TABLE_SPECS` |
| `gld_srv_poi_amenity` | `lh_vv_gold.dbo` | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) | `NB_GLD_SRV_POI_AMENITY` | `TABLE_SPECS` |
| `gld_srv_poi_review` | `lh_vv_gold.dbo` | `review_id` | `NB_GLD_SRV_POI_REVIEW` | `TABLE_SPECS` |
| `gld_enr_poi_coordinate` | `lh_vv_gold.enr` | MISSING | không có node | MISSING trong `TABLE_SPECS`. Có DDL cũ ở `NB_CREATE_DDL`. Skill bước 2: không hiện hành, không cạnh. Chưa vẽ thẻ. |

Tổng cột active registry 3p: 9+11+4+5+4+3+2+7+8 = 53. Câu ngày 19/10 trong §5.2 nói 53 cột active. Bảng đếm trong cùng mục không khớp từng bảng (ví dụ `slv_3p_poi` ghi 21 (15), registry 9).

## Lịch sử quyết định

### D-01

Skill cấm cột trên sơ đồ Mermaid. User yêu cầu swimlane drawio có tên bảng, grain, số cột và từng cột. Lệch này được ghi trước khi vẽ.

### D-02

`docs/context/01_DATA_MODEL.md` lệch DDL hoặc NodeSpec ở các điểm sau. Không chọn phía.

1. §6 liệt kê bảng không có trong `TABLE_SPECS` và không có notebook node: `slv_poi_source_map`, `slv_poi`, `slv_poi_address`, `slv_poi_localization`, `slv_poi_destination`. §6.1 thêm `ref_lang_policy`, `ref_source`, `ref_business_category`, `ref_destination_special_rule`, `ref_poi_legacy_id`. Doc ghi notebook N2 và N4 chưa có trong repo.
2. `TABLE_SPECS` có bảng §6 không liệt kê: `slv_poi_media_info`, `slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination`, `slv_enr_poi_review_multi_lang`.
3. §7 nói gold hiện hành chỉ `gld_enr_poi_info` và `gld_enr_poi_review`. `TABLE_SPECS` còn năm bảng `gld_srv_poi_multi_lang`, `gld_srv_poi_info`, `gld_srv_poi_media_gallery`, `gld_srv_poi_amenity`, `gld_srv_poi_review`, mỗi bảng có NodeSpec.
4. §5.2 bảng đếm cột 3p lệch registry. Câu 53 cột active trong cùng mục khớp tổng registry.

Hướng cho user:

- Hướng 1: vẽ theo registry và `TABLE_SPECS`. Không vẽ bảng chỉ có trong §6 hoặc §6.1.
- Hướng 2: giữ doc là danh sách bảng cần đúng. Main không vẽ trong task này.

User chốt 2026-10-28, nguyên văn: «Các bảng trong docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio chỉ là sample thôi. Hãy vẽ thay thế trực tiếp trong file, không dựa vào hình vẽ cũ.» Áp dụng hướng 1. `gld_enr_poi_coordinate` vẫn MISSING nên không có thẻ.

### D-03

Nhãn cạnh. `không join` là nhãn skill khi input là khung duy nhất.

| Đích | Nguồn | Nhãn |
|---|---|---|
| `slv_poi_entity_non_enrich` | `slv_3p_poi` | dòng gốc |
| `slv_poi_entity_non_enrich` | `slv_pn_business_services` | dòng gốc |
| `slv_poi_entity_non_enrich` | `slv_3p_poi_address` | left join |
| `slv_poi_entity_non_enrich` | `slv_3p_poi_contact` | left join |
| `slv_poi_entity_non_enrich` | `slv_3p_poi_opening_hours` | left join |
| `slv_poi_entity_non_enrich` | `ref_dictionary_place_type` | left join |
| `slv_poi_entity_non_enrich` | `slv_pn_business_service_i18ns` | inner join |
| `slv_poi_amenity` | `slv_3p_poi_amenity` | dòng gốc |
| `slv_poi_amenity` | `slv_poi_entity_non_enrich` | inner join |
| `slv_poi_amenity` | `slv_poi_entity_non_enrich` | union |
| `slv_poi_amenity` | `ref_dictionary_amenities` | inner join |
| `slv_poi_media_info` | `slv_3p_poi_media` | dòng gốc |
| `slv_poi_media_info` | `slv_pn_business_service_i18ns` | dòng gốc |
| `slv_poi_media_info` | `slv_pn_business_services` | left join |
| `gld_enr_poi_info` | `slv_poi_entity_non_enrich` | dòng gốc |
| `gld_enr_poi_info` | `slv_poi_amenity` | left join sau groupBy |
| `gld_enr_poi_info` | `slv_3p_poi_rating` | left join |
| `gld_enr_poi_info` | `slv_3p_poi_price` | left join |
| `gld_enr_poi_info` | `slv_3p_poi_review` | left join sau groupBy |
| `gld_enr_poi_info` | `slv_pn_business_service_i18ns` | left_semi |
| `gld_enr_poi_info` | `slv_enr_poi_info_multi_lang` | left join |
| `gld_enr_poi_info` | `slv_enr_poi_destination` | left join |
| `gld_enr_poi_review` | `slv_3p_poi_review` | dòng gốc |
| `gld_enr_poi_review` | `slv_enr_poi_review_multi_lang` | left join |
| `gld_srv_poi_multi_lang` | `slv_enr_poi_info_multi_lang` | dòng gốc |
| `gld_srv_poi_multi_lang` | `slv_poi_entity_non_enrich` | left join |
| `gld_srv_poi_multi_lang` | `slv_pn_business_service_i18ns` | left join |
| `gld_srv_poi_info` | `slv_poi_entity_non_enrich` | dòng gốc |
| `gld_srv_poi_info` | `slv_enr_poi_destination` | left join |
| `gld_srv_poi_info` | `slv_enr_poi_info_multi_lang` | left_semi |
| `gld_srv_poi_info` | `slv_3p_poi_rating` | left join |
| `gld_srv_poi_info` | `slv_3p_poi_review` | left join sau groupBy |
| `gld_srv_poi_media_gallery` | `slv_poi_media_info` | không join |
| `gld_srv_poi_amenity` | `slv_poi_amenity` | không join |
| `gld_srv_poi_review` | `slv_enr_poi_review_multi_lang` | dòng gốc |
| `gld_srv_poi_review` | `slv_3p_poi_review` | inner join |
| `gld_srv_poi_review` | `slv_3p_poi_rating` | left join |

`NB_SLV_POI_ENTITY_NON_ENRICH` và `NB_SLV_POI_MEDIA_INFO` ghép hai nhánh bằng `unionByName`. Mỗi nhánh có một dòng gốc. Không thêm nhãn mới. `slv_poi_entity_non_enrich` vào `slv_poi_amenity` vừa `inner join` trên cờ, vừa `union` nhánh `types`. Join trong `ctx.warn` hoặc đếm chất lượng không thành cạnh.

User 2026-10-28 bỏ đường nối trên sơ đồ. Bảng cạnh ở trên giữ làm nhật ký build, không còn mũi tên trên file. Cùng một trang, ba dải cạnh nhau từ trái sang phải: Gold (7 bảng `gld_*`), Silver L2 (8 bảng silver trong `TABLE_SPECS`: `ref_dictionary_place_type`, `ref_dictionary_amenities`, `slv_poi_entity_non_enrich`, `slv_poi_amenity`, `slv_poi_media_info`, ba bảng `slv_enr_*`), Silver L1 (32 bảng registry).
