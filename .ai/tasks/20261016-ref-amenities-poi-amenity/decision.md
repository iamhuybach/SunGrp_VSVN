# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| Q1 | Nguồn business_sector | join thêm slv.slv_poi_entity (bảng này đang xử lý ở một luồng khác) qua poi_id để lấy business_sector. Thêm điệu kiện business_sector để join. | Quyết định của người dùng | 2026-10-16 |
| Q2 | Chính tả accommodation | Sửa chính tả accommodation | Quyết định của người dùng | 2026-10-16 |
| Q3 | Khóa slv_poi_amenity | ok chốt phương án đưa amenity_raw vào khóa. Vẫn giữ việc join thêm slv.slv_poi_entity (bảng này đang xử lý ở một luồng khác) qua poi_id để lấy business_sector. Thêm điệu kiện business_sector để join. | Quyết định của người dùng | 2026-10-16 |
| Q4 | Mã sector F&B | Sửa slv_poi_entity là f_n_b | Quyết định của người dùng | 2026-10-16 |
| Q5 | Runtime trước merge | chuyển waiting_runtime: Main soạn runbook để bạn chạy Fabric DEV theo mục stop 6 trong architecture.md trước khi merge. | Quyết định của người dùng | 2026-10-16 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Header `accomodation` được seed thành `accommodation` theo Q2. `f_n_b`, `attraction`, `shopping_n_retail` giữ nguyên chữ header. Q2 không đưa token thay cho `f_n_b`.
- Nhãn in đậm ở cột đầu là `amenity_group`. Mục 2.3 lặp `facilities_and_services` vẫn là một nhóm.
- Chỉ điều kiện đúng dạng một path và một vế phải `true` hoặc `false` mới khớp `source_flags_json`. Path có dấu chấm và đầu path là `flags`, `parkingOptions`, `paymentOptions`, `accessibilityOptions`, `evChargeOptions`, hoặc `fuelOptions` được giữ nguyên. Tên flag trần nằm trong danh sách boolean của `JSON_PICK` được đọc là `flags.<tên>`.
- `types[]`, `serves_meals`, ô không có dấu `=`, và ô không phải một path duy nhất không khớp. Vì vậy `f_n_b` / `specialty_tags`, `attraction` / `facilities_and_services`, và `shopping_n_retail` / `facilities_and_services` không nằm trong số nhóm bị trùng.
- Ô `outdoorSeating = true = true` và ô Car Parking nối bằng dấu phẩy không được tách, vì separator không phải `hoặc`.
- Ba sample JSON chỉ dùng để đếm khớp. Chúng không được ghi vào repo.

## Sai lệch so với kiến trúc

- Q4 trong `architecture.md` đã được sửa: sector F&B là `f_n_b` ở `slv_poi_entity` và ở từ điển amenity. Không alias.
- SPARK-001: `architecture.md` mục `Partial failure` vẫn mô tả quality gate zero-output khi `joined > 0` và không có dòng khớp. Code bỏ gate đó. DataFrame rỗng đi vào `run_node` để RECOMPUTE soft-delete amenity cũ. Hai gate còn lại giữ: điều kiện google trùng khóa, và không có điều kiện google khớp được.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-001 | P1 | fixed | Bỏ `if joined and not n` trong `notebooks/NB_SLV_POI_AMENITY.ipynb` cell `d1amenbuild`. Metric `rows` vẫn ghi 0. DataFrame rỗng là trạng thái hợp lệ. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Q1: join thêm slv.slv_poi_entity (bảng này đang xử lý ở một luồng khác) qua poi_id để lấy business_sector. Thêm điệu kiện business_sector để join.
- Q2: Sửa chính tả accommodation
- Q3: ok chốt phương án đưa amenity_raw vào khóa. Vẫn giữ việc join thêm slv.slv_poi_entity (bảng này đang xử lý ở một luồng khác) qua poi_id để lấy business_sector. Thêm điệu kiện business_sector để join.
- Q4: Sửa slv_poi_entity là f_n_b. Đã kiểm tra `notebooks/NB_SETUP_POI_ENTITY.ipynb`: `SEED_SECTORS` gồm `accommodation`, `f_n_b`, `spa_n_wellness`, `shopping_n_retail`, `attraction`, `vehicle_rental`, `other`. Không còn token `fnb`. `NB_SLV_POI_ENTITY.ipynb` không gán mã sector. Từ điển amenity giữ `f_n_b`.
- Q5: chuyển waiting_runtime: Main soạn runbook để bạn chạy Fabric DEV theo mục stop 6 trong architecture.md trước khi merge.

## Lịch sử quyết định

- 2026-10-16: `notebooks/NB_CREATE_DDL.ipynb`, registry `slv_3p_poi_amenity`, cột hiện có là `poi_id` và `source_flags_json`. `source_flags_json` là cột registry, không suy ra từ `amenity_schema_json` hay `ext_attributes_json`. Hai tên cũ chỉ còn trong comment. `docs/context/01_DATA_MODEL.md` §5.2 vẫn ghi `poi_id`, `amenity_schema_json`, `ext_attributes_json`.
- 2026-10-16: Đếm từ `docs/context/3p-google/mapping_amenities.md` theo quy tắc khớp ở mục giả định. Ba nhóm có từ hai `amenity` trở lên cùng khớp một khóa.
- 2026-10-16: Ghi Q1 và Q2 nguyên văn. Tên đủ trong repo là `lh_vv_silver.dbo.slv_poi_entity`. Task này chỉ đọc bảng đó. Join `poi_id` lấy một `business_sector`, rồi join từ điển có thêm `business_sector`. Việc này không tách các amenity trong cùng một nhóm. Khóa chưa được rộng. Q2 chỉ đổi header `accomodation` thành `accommodation`. `f_n_b` giữ nguyên.
- 2026-10-16: Q3 ghi tên amenity bị trùng trong 3 nhóm và amenity khớp trên từng sample. Khóa chưa đổi.
- 2026-10-16: Nếu `amenity_raw` vào khóa, value còn `amenity` và `amenity_vi`. `amenity_raw` là chuỗi điều kiện, ví dụ `parkingOptions.freeStreetParking = true`. Dòng chỉ sinh khi điều kiện khớp. Không có cột boolean.
- 2026-10-16: Q3 chốt. Khóa `slv_poi_amenity` là (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). `amenity` không vào khóa. Value là `amenity` và `amenity_vi`. Join Q1 giữ nguyên: đọc `business_sector` từ `lh_vv_silver.dbo.slv_poi_entity` theo `poi_id`, và join từ điển có `business_sector`.
- 2026-10-16: Architecture PASS. `architecture.md` mục `Blocking user decision Q4: sector code for F&B` chặn implement vì khi đó entity được ghi là `fnb`.
- 2026-10-16: Q4 chốt theo lời người dùng: sửa `slv_poi_entity` thành `f_n_b`. Kiểm tra lại notebook setup: `SEED_SECTORS` đã chứa `f_n_b`, 0 dòng token `fnb`. Chưa đọc bảng trên Fabric DEV.
- 2026-10-16: `architecture.md` được sửa theo yêu cầu: sector F&B là `f_n_b`. Q4 không còn là blocker.
- 2026-10-16: Defect mapping để owner sửa sau, không chặn task. D1: `outdoorSeating = true = true`. D2: hai ô parking nối bằng dấu phẩy. D3: path trần ở mục 2.3 và 2.4, gồm `goodForChildren` hai lần. D4: hàng Bar thiếu `hoặc` trước `servesBeer = true`. D5: `serves_meals` không có trong `source_flags_json`.
- 2026-10-16: SPARK-001 `fixed`. Review round 1: gate `joined > 0` và `n == 0` chặn MERGE khi không có amenity khớp, nên RECOMPUTE không soft-delete dòng cũ. Bỏ gate đó trước khi sửa code.
- 2026-10-16: Q5. `classification.runtime_required` chuyển thành true. `gates.runtime` là `pending` cho đến khi người dùng ghi kết quả Fabric DEV.
- 2026-10-16: Kết quả Fabric DEV trong `runtime-runbook.md` mục `Kết quả người dùng ghi nhận`. Bốn check bằng 0. Seed và idempotency dữ liệu đạt. Node chạy với `p_exec_id` rỗng (`chạy tay`), nên watermark cạnh `wm_e__slv_poi_amenity__*` không có dòng. `gates.runtime` vẫn `pending`.
- 2026-10-16: Người dùng xác nhận watermark đã pass. `gates.runtime` chuyển thành `pass`. Status chuyển `ready_to_merge`.
