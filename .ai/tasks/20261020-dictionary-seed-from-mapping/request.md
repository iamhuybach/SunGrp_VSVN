# Request

## User outcome

Update lại tài liệu mapping_place_type.md và mapping_amenities.md theo ref_dictionary_place_type (bổ sung cả phần category_group vào mục 1.8; không xóa mục 1.9. và 1.9._), ref_dictionary_amenities (không xóa mục 2.5).
Trong tài liệu mapping_place_type.md có map data của partner và 3rd, các case category_group của Partner cũng cần map tương ứng. Hiện tại đang không map. Sau khi update lại, update lại tài liệu mapping_place_type.md.
Cấu hình thêm các mục 1.9._ vào bảng ref_dictionary_place_type tôi mới bổ sung trong file mapping_place_type.md.
Cấu hình thêm các mục 2.5 vào bảng ref_dictionary_amenities tôi mới bổ sung trong file mapping_amenities.md.

## Scope

### In scope

- `docs/context/3p-google/mapping_place_type.md`: điền mục 1.8 từ `category_group` của từ điển; giữ mục 1.9, 1.9.1, 1.9.2, 1.9.3.
- `docs/context/3p-google/mapping_amenities.md`: giữ mục 2.5.
- `lh_vv_silver.dbo.ref_dictionary_place_type` và `lh_vv_silver.dbo.ref_dictionary_amenities`: cột mới trong DDL; giá trị mới ghi cứng trong `SEED_ROWS`.
- Notebook: `notebooks/NB_SETUP_POI_ENTITY.ipynb`, `notebooks/NB_SETUP_POI_AMENITY.ipynb`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, `notebooks/NB_CREATE_DDL.ipynb`.
- Test assertion của seed và cột từ điển: `tests/test_poi_entity_contract.py`, `tests/test_poi_amenity_contract.py`.
- Runbook xóa và init lại đúng hai bảng. User chạy Fabric DEV.

### Out of scope

- Suy `category_group` bằng hàm trong code.
- Tạo `place_type` mới cho cụm không nêu token.
- Biến công thức mục 1.9.3 thành dòng seed.
- Bịa tên flag cho `parkingOptions.*` và câu Derived amenities.
- Agent đánh `gates.runtime`.

## Acceptance criteria

- Mục 1.8 có `category_group`. Mục 1.9, 1.9.1, 1.9.2, 1.9.3 và mục 2.5 còn nguyên.
- Mỗi dòng `SEED_ROWS` place type mang sẵn `category_group`. Hàm `category_group` và `with_category_group` không còn gán partner về `Other` bằng khớp token Google.
- Cột mới khai trong DDL của `NB_SETUP_POI_ENTITY` hoặc `NB_SETUP_POI_AMENITY`, và sửa cùng lúc `NB_SETUP_INITIAL_DDL` và `NB_CREATE_DDL`.
- Mục 1.9.1 và 1.9.2 ghi vào `SEED_ROWS` của dòng `place_type` đã có khi rule là exact type.
- Mục 2.5: mỗi `amenity_raw` liệt kê tường minh là một dòng `SEED_ROWS`. Đã có thì bổ sung đúng dòng đó. Chưa có thì `business_sector = other`, `amenity_group = other`, `amenity = amenity_raw`, `amenity_vi = amenity_raw`.
- Runbook: xóa, dựng lại, đếm dòng, quay lại. `p_apply` mặc định `false`. Bước apply tách riêng.

## Constraints

Cách làm đã chốt:

- Hai bảng `lh_vv_silver.dbo.ref_dictionary_place_type` và `lh_vv_silver.dbo.ref_dictionary_amenities` được phép xóa để init chạy lại. Runbook ghi bước xóa, dựng lại, đếm dòng và cách quay lại. User chạy Fabric DEV. Agent không đánh `gates.runtime`.
- Giá trị mới ghi cứng trong `SEED_ROWS` của `notebooks/NB_SETUP_POI_ENTITY.ipynb` và `notebooks/NB_SETUP_POI_AMENITY.ipynb`. Không suy `category_group` bằng hàm trong code. Hàm `category_group` và `with_category_group` hiện gán partner về `Other` vì khớp token Google. Bỏ cách gắn sau. Mỗi dòng `SEED_ROWS` mang sẵn `category_group`.
- Cột mới của bảng vẫn khai trong DDL của `NB_SETUP_POI_ENTITY` hoặc `NB_SETUP_POI_AMENITY`, và sửa cùng lúc `NB_SETUP_INITIAL_DDL` và `NB_CREATE_DDL`. Đó là khai báo cột, không phải logic gắn giá trị.

Quy tắc seed, không suy diễn:

- `category_group` của một place_type Google lấy theo mục 1.8 sau khi mục này được điền. place_type không nằm trong 1.8 thì `category_group = Other`.
- Dòng partner nhận `category_group` của Google Place Type cùng hàng trong `mapping_place_type.md`. Một Partner Portal Enum đứng ở nhiều hàng khác `category_group` thì ghi `USER_DECISION`, không chọn giúp.
- Mục 1.9.1 và 1.9.2 là cột và giá trị insert thêm vào `ref_dictionary_place_type`, ghi vào `SEED_ROWS` của dòng place_type đã có. Rule exact type gắn vào đúng place_type đó.
- Cụm "Có snorkel", "Có island" và các điều kiện không nêu token place_type: ghi `USER_DECISION`. Không tạo place_type mới.
- Mục 1.9.3 là công thức `deterministic_cost_vnd` từ `price_min` và `price_max`. Giữ trong tài liệu. Không biến công thức này thành dòng seed.
- Mục 2.5: mỗi amenity_raw liệt kê tường minh thành một dòng `SEED_ROWS`. Đã có thì bổ sung đúng dòng đó. Chưa có thì `business_sector = other`, `amenity_group = other`, `amenity = amenity_raw`, `amenity_vi = amenity_raw`.
- `parkingOptions.*` và câu "Derived amenities" không liệt kê token thì ghi `USER_DECISION`. Không bịa tên flag.
- Giữ nguyên mục 1.9, 1.9.1, 1.9.2, 1.9.3 và mục 2.5 trong hai file mapping.

## Classification rationale

- Complexity: high. Đổi cột từ điển và seed trên nhiều notebook DDL, có rebuild xóa-rồi-init.
- Risk: high. Seed là nguồn từ điển dùng chung; init lại hai bảng silver là thay trạng thái bền, rollback chỉ có trong runbook.
- Architecture: required. Đổi cột và grain giá trị seed; `data_model_change` đòi `model-design.md` trước Architect.
- Evidence: not required at triage. Lệch seed và mapping đọc được trong repository. Probe chỉ khi cổng architecture đòi.
- Runtime proof: required. User xóa và init lại hai bảng trên Fabric DEV. Agent không đánh `gates.runtime`.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, rồi `risk-gate`. Không fast lane.
