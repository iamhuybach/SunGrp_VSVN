# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Không gian `poi_id` amenity và `gld_srv_poi_info` | `business_sector` lấy từ `slv_pn_business_services`, join `slv_pn_business_service_i18ns` qua `business_service_id = id` và `locale = 'vi'`. Khớp từ điển thì `amenity_group` lấy từ dòng từ điển; không khớp thì `specialty_tags`. Một nhãn khớp nhiều dòng từ điển partner thì dừng notebook, không ghi. | Lịch sử quyết định, D-12 | 2026-11-18 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Chưa đếm `slv_enr_poi_destination` và `slv_enr_poi_info_multi_lang`. Không suy ra hai bảng đó rỗng. Điều kiện lọc google nằm ở `NB_GLD_SRV_POI_INFO` cell `srvinfobuild`.

## Sai lệch so với kiến trúc

- Không có. Chưa có `architecture.md`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-001 | P1 | fixed | Người dùng chấp nhận 2026-11-18. `amenpnpy` đặt `load_mode = 'RECOMPUTE'`. Điều kiện UPDATE dùng `coalesce(upper(trim(load_mode)), '')` để dòng `load_mode` NULL vẫn được cập nhật. Post-check yêu cầu đúng một dòng RECOMPUTE active. `vv.py verify` PASS. Không còn vòng review | |
| SQL-002 | P1 | fixed | Trước khi ghi, nhóm edge có `n != 1` thì dừng. Edge chưa có vẫn được INSERT | |
| SPARK-001 | P1 | fixed | Đếm nhãn trùng bằng `groupBy`, chỉ `collect` tối đa 20 nhãn đã `orderBy` | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Chọn cách 2: Main sinh amenity partner bằng uuid_md5(id, 'partner'), không đổi bộ lọc info, rồi chạy architecture trước khi sửa code.
- Sử dụng `slv_pn_business_service_i18ns.amentities.facilities.specialty_tags` khi `locale = 'vi'`; null thì dùng `slv_pn_business_services.amentities.facilities.specialty_tags`. Left join `ref_dictionary_amenities.amenity_raw` với `source_name = 'partner'`. Không khớp từ điển vẫn ghi, giống luồng 3rd-party.
- `business_sector` lấy từ `slv_pn_business_services`, join `slv_pn_business_service_i18ns` qua `business_service_id = id` và `locale = 'vi'`. Khớp từ điển thì `amenity_group` lấy từ dòng từ điển; không khớp thì `specialty_tags`. Một nhãn khớp nhiều dòng từ điển partner thì dừng notebook, không ghi.
- Duyệt thêm một vòng review cho SQL-001, SQL-002 và SPARK-001. `review_plan.extra_round_approved_on` = 2026-11-18.
- Chấp nhận bản sửa SQL-001. Tiếp tục task theo workflow. Bước tiếp là P5 trên Fabric DEV.

## Lịch sử quyết định

### D-1 — 2026-11-18

Repo không chỉ ra lệch công thức. Amenity và dòng google của `gld_srv_poi_info` cùng không gian third-party `HASH_MD5_UUID(source_name, source_id)`. Dòng partner của info dùng `uuid_md5(id, 'partner')` và amenity không sinh id đó. Chưa chọn cách sửa. Probe đếm `poi_id` amenity có và không có trên `gld_srv_poi_info` trước khi sửa.

Cùng không gian third-party:

- `NB_CREATE_DDL` cell 14: `POI_ID = HASH_MD5_UUID` của `_doc.source_name,_doc.source_id`. Cả `slv_3p_poi` và `slv_3p_poi_amenity` dùng `POI_ID`.
- `NB_LIB_EXTRACT_RAWDATA` `derived_sql`: `HASH_MD5_UUID` là `md5(concat(...))` dạng UUID 8-4-4-4-12.
- `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild`, `_google`: `poi_id` lấy từ `slv_3p_poi` (`POI_COLS`), không hash lại.
- `NB_SLV_POI_AMENITY` cell `d1amenbuild`: `poi_id` lấy từ `slv_3p_poi_amenity`, inner join `slv_poi_entity_non_enrich.poi_id`. Notebook này không hash. `types` chỉ lấy dòng `source_name` google của entity.
- `NB_LIB_TRANSFORM_SLV_GLD` `uuid_md5`: cùng `md5(concat(...))` dạng UUID.
- `NB_GLD_SRV_POI_INFO` cell `srvinfobuild`: `poi_id` lấy từ `slv_poi_entity_non_enrich`. Dòng không phải google được giữ. Dòng google chỉ khi `poi_id` có trong cả `slv_enr_poi_destination` và `slv_enr_poi_info_multi_lang`.
- `NB_GLD_SRV_POI_AMENITY` cell `srvamenitybuild`: `select(*OUT_COLS)` từ `slv_poi_amenity`. Grain không đổi.

Không gian khác, không phải lệch hash của dòng amenity:

- `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild`, `_partner`: `poi_id = uuid_md5(id, 'partner')`. Amenity không đọc `slv_pn_business_services` và không sinh id này.

Hai hướng sửa, chưa chọn. Hướng nào đứng phụ thuộc kết quả probe:

1. `poi_id` amenity không có trên `gld_srv_poi_info`: id amenity vẫn là id entity google. Khoảng trống nằm ở bộ lọc google của `NB_GLD_SRV_POI_INFO`. Một cách là lọc amenity cùng điều kiện. Cách kia là giữ `poi_id` amenity, vì công thức đã trùng entity.
2. Mọi `poi_id` amenity đã có trên `gld_srv_poi_info`: id amenity đã gắn được với info. Khoảng trống còn lại là POI trên info, gồm dòng partner, không có amenity. Cách sửa đó là sinh dòng partner bằng `uuid_md5(id, 'partner')`. Không làm khi chưa có số đếm.

### D-1 kết quả overlap — 2026-11-18

Fabric DEV: `slv_poi_amenity` và `gld_srv_poi_amenity` mỗi bảng 15995 `poi_id` sống, 0 có trên `gld_srv_poi_info` sống, 15995 không có. Chưa chọn cách sửa. Chưa đủ để kết luận bộ lọc google của info là nguyên nhân. Probe tiếp theo đếm info theo `source_name` và đếm amenity `poi_id` có trên entity.

Nguồn: `evidence/results/amenity-poi-id-overlap.txt`. Hai bảng amenity cùng số. Mẫu 50 `poi_id` của `gld_srv_poi_amenity`, không có dữ liệu cá nhân.

Hai hướng trong D-1 không được áp trong lượt này:

- Lọc amenity theo tập `poi_id` của info: overlap bằng 0 nên RECOMPUTE sẽ soft-delete hết 15995 `poi_id`. Không gán `poi_id` đang nằm trên info.
- Giữ `poi_id` amenity vì công thức repo đã trùng entity: overlap vẫn 0. Chưa chứng minh dòng amenity đang có trên entity.

### D-1 kết quả side — 2026-11-18

15995 `poi_id` amenity đều là entity `google`. `gld_srv_poi_info` sống chỉ có 294 `poi_id` `partner`, không có `google`. Bỏ `deleted_at` của info thì overlap vẫn 0. Nguyên nhân: `NB_GLD_SRV_POI_INFO` cell `srvinfobuild` loại dòng google, amenity giữ `poi_id` google của entity. Hai cách sửa, chưa chọn.

Nguồn: `evidence/results/amenity-poi-id-side.txt`. Query 2 không có nhóm `<no_entity>` hay `partner`. Query 1 không có nhóm `google`.

Hai cách sửa, không chọn:

1. Đưa `poi_id` google của entity lên `gld_srv_poi_info` bằng cách đổi bộ lọc ở `NB_GLD_SRV_POI_INFO` cell `srvinfobuild`. Amenity không đổi công thức. 15995 `poi_id` amenity khi đó có trên info. 294 POI partner vẫn không có amenity.
2. Sinh amenity cho POI partner bằng `uuid_md5(id, 'partner')`. 294 `poi_id` trên info có thể có amenity. 15995 dòng google vẫn không có trên info.

### D-2 — 2026-11-18

Chọn cách 2: Main sinh amenity partner bằng uuid_md5(id, 'partner'), không đổi bộ lọc info, rồi chạy architecture trước khi sửa code.

Cách 1 không làm. Bộ lọc google của `NB_GLD_SRV_POI_INFO` cell `srvinfobuild` giữ nguyên. Grain amenity giữ `(poi_id, business_sector, amenity_group, amenity_raw)`. Dòng partner dùng `uuid_md5(id, 'partner')`, cùng công thức `_partner` của `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild`. Signal `data_model_change`. `model-design.md` chạy trước architecture. Chưa sửa notebook.

### D-3 — 2026-11-18

Cách 2 được chọn. Architecture trả EVIDENCE_REQUIRED: chưa có JSON path và rule khớp amenity partner. Chưa sửa code. Chạy probe P1, P3, P4 trên Fabric DEV. P2 viết sau khi P1 chỉ ra path.

Nguồn: `architecture.md` mục `Evidence required` và `Status and blocking gap`. Model `Conflicts` 4: không có path amenity trong `amentities`. P2 (`partner-amenity-label-match`) cần path đó nên chưa viết. Quyết định U1–U5 trong architecture chưa chọn.

### D-4 — 2026-11-18

P1 lỗi vì `slv_pn_business_service_i18ns` không có `deleted_at`. Dòng sống partner L1 là `NOT coalesce(deleted, false)`, cùng `_live`. Probe P1 đã sửa. Chưa có kết quả P1, P3, P4.

Fabric DEV báo `UNRESOLVED_COLUMN` cho `deleted_at`, gợi ý cột `deleted`. `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild`, `_live`: `deleted = true` là dòng đã xoá. `NB_CREATE_DDL` cell 11 không map `deleted_at` cho `slv_pn_business_services` hay `slv_pn_business_service_i18ns`. P3 và P4 vẫn lọc `deleted_at` trên entity, info và từ điển.

### D-5 — 2026-11-18

Query shape của P1 lỗi vì `schema_of_json` không nhận cột. Probe đổi sang đếm loại JSON và key con, không lấy giá trị. Chưa có kết quả P1, P3, P4.

Fabric DEV: `DATATYPE_MISMATCH.NON_FOLDABLE_INPUT` trên `schema_of_json(v)`. Hàm này chỉ nhận chuỗi hằng. Query `keys` không dùng hàm đó.

### D-6 — 2026-11-18

P4 lỗi vì `ref_dictionary_amenities` trên Fabric không có `deleted_at`. Dòng active là `is_active = true`. Probe P4 đã sửa. Chưa có kết quả P1, P3, P4.

Fabric DEV: `UNRESOLVED_COLUMN` cho `deleted_at`, gợi ý `updated_at`, `amenity`, `amenity_en`, `amenity_raw`, `amenity_vi`. DDL trong `NB_SETUP_POI_AMENITY` có `deleted_at`, bảng đang chạy thì không. `NB_SLV_POI_AMENITY` cell `d1amenbuild` lọc `is_active = true`.

### D-7 — 2026-11-18

P1: `facilities` là object 230 dòng, key con trùng `amenity_group` của từ điển. P3: 295 entity partner, 101 `business_sector` null, 295 có trên info. P4: 74 dòng từ điển partner, 0 key trùng, 0 `other`/`other`. P2 đếm nhãn `$.facilities`.

Nguồn: `evidence/results/partner-amentities-shape.txt`, `partner-entity-coverage.txt`, `partner-dict-keys.txt`. Key con của `facilities` gồm `general_amenities`, `accessibility`, `facilities_and_services`, `space_and_services`, `specialty_tags`, đúng các nhóm P4. P3 còn 11 dòng `business_sector` chuỗi rỗng, tách khỏi 101 null. 295/295 `poi_id` partner của entity có trên `gld_srv_poi_info`, nên U2 không còn hai nhánh. Chưa chọn U1, U3, U5.

### D-8 — 2026-11-18

P2 lỗi vì `id` vừa thuộc `vi` vừa thuộc `svc`. Probe lấy `vi.id`. Chưa có kết quả P2.

Fabric DEV: `AMBIGUOUS_REFERENCE` tại join `slv_pn_business_service_i18ns` và `slv_pn_business_services`. Ba query của `partner-amenity-label-match.sql` đều chọn `vi.id`.

### D-9 — 2026-11-18

P2 trên `$.facilities`: exact và không phân biệt hoa thường cho `amenity_raw` bằng nhau, 36 nhãn khớp và 80 không khớp. `Swimming Pool` trong seed là `amenity_en`, không phải `amenity_raw`. Probe tiếp theo đếm nhãn theo `amenity_en`, `amenity_vi` và `amenity`.

Nguồn: `evidence/results/partner-amenity-label-match.txt`. Bốn nhóm sector: `<null>` 3/13, accommodation 3/36, attraction 12/31, f_n_b 18/36. Mảng chuỗi: `accessibility`, `facilities_and_services`, `general_amenities`, `highlights`, `safety_and_hygiene`, `space_and_services`, `specialty_tags`. `classification` và `visitor_logistics` là object. `main_category` và `main_cuisine` là scalar. `NB_SETUP_POI_AMENITY` `amenity_seed_rows`: trường thứ năm của `SEED_ROWS` là `amenity_en`, `amenity_raw` là trường thứ tư. Dòng partner `('Hồ bơi', 'Swimming Pool', 'Hồ bơi')` là raw, en, vi. P2 chưa đọc `store_profile`.

### D-10 — 2026-11-18

Nhãn partner không khớp một cột từ điển. `amenity` snake_case khớp 0 mọi dòng. `amenity_en` và `amenity_raw` mỗi cột khớp một phần khác nhau. Nhóm không có trong từ điển khớp 0. Chưa chọn cột khớp và cách xử lý nhãn không khớp.

Nguồn: `evidence/results/partner-amenity-label-column.txt`. `hit_amenity` = 0 trên mọi dòng. Ví dụ: accommodation `general_amenities` 18 nhãn, `hit_raw` 3, `hit_en` 17, `hit_vi` 1. shopping `facilities_and_services` 11 nhãn, `hit_raw` 11, `hit_en` 10. `safety_and_hygiene`, `highlights`, logistics, fleet và `holiday_exceptions` khớp 0. Từ điển partner trên Fabric chỉ có `general_amenities`, `accessibility`, `facilities_and_services`, `space_and_services`, `specialty_tags`. U2 đóng: 295/295 `poi_id` partner của entity có trên info. U4 đóng theo D-2: 15995 dòng google giữ nguyên. U1 trong phạm vi D-2 chỉ còn cách B, vì entity không có `amentities` và cách C thêm cột entity. U3 và cột khớp chưa chọn.

### D-11 — 2026-11-18

Sử dụng `slv_pn_business_service_i18ns.amentities.facilities.specialty_tags` khi `locale = 'vi'`; null thì dùng `slv_pn_business_services.amentities.facilities.specialty_tags`. Left join `ref_dictionary_amenities.amenity_raw` với `source_name = 'partner'`. Không khớp từ điển vẫn ghi, giống luồng 3rd-party.

Người dùng, nguyên văn: dùng cột `slv_pn_business_service_i18ns.amentities.facilities.specialty_tags` với `locale = 'vi'` (nếu null dùng `slv_pn_business_services.amentities.facilities.specialty_tags`) left join `ref_dictionary_amenities.amenity_raw` và `source_name = 'partner'`. Không match, vẫn ghi giống như luồng 3rd-party.

Sample 1 không có `specialty_tags`. Sample 2 có `facilities.specialty_tags` = `["Hotpot", "Gastropub", "Milk Tea"]`. Không đọc key `facilities` khác. `poi_id` partner vẫn `uuid_md5(id, 'partner')`. Bộ lọc google của info không đổi. Dòng google hiện có giữ nguyên.

### D-12 — 2026-11-18

`business_sector` lấy từ `slv_pn_business_services`, join `slv_pn_business_service_i18ns` qua `business_service_id = id` và `locale = 'vi'`. Khớp từ điển thì `amenity_group` lấy từ dòng từ điển; không khớp thì `specialty_tags`. Một nhãn khớp nhiều dòng từ điển partner thì dừng notebook, không ghi.

D-11 vẫn giữ path và left join. Người dùng không chọn giá trị thay thế khi `business_sector` null hoặc chuỗi rỗng.

### A-1 đến A-8 và R-1 — 2026-11-18

Architecture vòng 2 PASS. Ghi trước khi sửa code. Nguồn: `architecture.md` mục `Decisions closing model-design open items` và `Rollout` R-1.

- A-1: `business_sector` NULL thì `QualityGateError` trước khi ghi. Chuỗi rỗng được giữ, đếm `partner_sector_blank`, `ctx.warn`.
- A-2: từ điển partner lọc `lower(trim(source_name)) == 'partner'` và `is_active = true`.
- A-3: `_live` = `NOT coalesce(deleted, false)`. Dẫn bằng dòng `vi`, left join svc.
- A-4: inner join entity `source_name = partner` theo `poi_id`.
- A-5: `trim` nhãn, bỏ null và `''`, khớp exact, `dropDuplicates(["poi_id", "amenity_raw"])`.
- A-6: `from_json` với `PARTNER_TAGS`. JSON không parse thì bỏ và đếm. Không `get_json_object`, không `explode_outer`.
- A-7: dừng khi nhãn đang có trong dữ liệu khớp hơn một dòng từ điển. Raw trùng trong từ điển nhưng không có trong dữ liệu thì không dừng.
- A-8: `svc` và `i18n` nằm trong `required_inputs`. Cạnh mới do `amenpnpy` và seed initial.
- R-1: sau patch, chạy lại apply của `NB_SETUP_POI_AMENITY` hoặc `NB_SETUP_POI_ENTITY` dừng ở `setup_edge_issues`. Không ghi. Chấp nhận rủi ro này.
