# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Cột nguồn compact, features, experiences | Compact và Features dùng apps.srv_poi_info.cover_id (data[].cover.id) và apps.srv_poi_info.cover_blob_url (data[].cover.file_key). Experiences lấy source từ apps.srv_poi_multi_lang.source_name. | User, 2026-11-10 | 2026-11-10 |
| D-ARCH-1 | Architecture vòng 1 | RESULT: EVIDENCE_REQUIRED. Do not change code yet. | architecture.md Main brief Decision | 2026-11-10 |
| D-PROBE-1 | Probe P-1 đến P-4 | Probe trên database của .env (phê duyệt 2026-11-10): 292 dòng info còn sống đều partner và is_recommended, rating_overall null. experience là mảng JSON {title, keyword, description}. holiday_exceptions là [] hoặc {date, hours, title, status}. time_to_spend, best_time, cost_vnd là object một khóa. | evidence/results/p-1.txt, p-2.txt, p-3.txt, p-4.txt, p-shape.txt | 2026-11-10 |
| D-2 | Features selection | Đồng ý theo khuyến nghị. Pool chính là is_recommended = true. Fallback là dòng còn lại với rating_overall và rating_count đạt ngưỡng, và source_name khớp rating_source khi param có giá trị. Xoay một POI mỗi business_sector theo thứ tự ưu tiên, rồi page/size cắt chuỗi đó. null và chuỗi trắng bị loại. accommodation chỉ vào kết quả khi client đưa vào business_sector_priority. | User, 2026-11-11 | 2026-11-11 |
| D-3 | Envelope sáu API | Đồng ý theo khuyến nghị. Sửa cả mapping. Cả sáu API dùng ApiResponse như reviews. Features có đủ meta.pagination. | User, 2026-11-11 | 2026-11-11 |
| D-4 | Compact ids | ids Tối thiểu 1, tối đa 20 items, ids rỗng báo lỗi, thứ tự created_at DESC, poi_id ASC. | User, 2026-11-11 | 2026-11-11 |
| D-6 | JSON body hỏng của compact | Đồng ý theo khuyến nghị. HTTP 400, ERR_BAD_REQUEST, sửa GlobalExceptionHandler, thêm app-security-reviewer. | User, 2026-11-11 | 2026-11-11 |
| D-5 | rating_summary của reviews | Đồng ý Mảng rating_summary ngang hàng với data, một phần tử {rating_count, rating_avg_score}. API là GET /api/v1/pois/{poi_id}/reviews. | User, 2026-11-11 | 2026-11-11 |
| D-ARCH-2 | Architecture vòng 2 | RESULT: PASS. D-7 còn mở cho holiday_exceptions. | architecture.md Main brief Decision | 2026-11-11 |
| D-RUNTIME-1 | Runtime local compose | Người dùng yêu cầu Main tự chạy runbook ngày 2026-11-11. Kết quả PASS. Bằng chứng ở evidence/runtime/. | runtime-runbook.md Kết quả người dùng ghi nhận | 2026-11-11 |
| D-7 | holiday_exceptions | Cho kiểm tra cú pháp: JSON hợp lệ thì ghi lại đúng text đó, JSON hỏng thì field null. Không đổi khóa bên trong. | User, 2026-11-11 | 2026-11-11 |
| D-8 | Required của request | Request header và request param chỉ path poi_id Required = có. Mọi field request khác, gồm body ids, Required = không. API compact vẫn báo lỗi khi ids thiếu, rỗng hoặc quá 20 theo D-4. | User, 2026-11-11 | 2026-11-11 |
| D-9 | Review vòng 3 | Phê duyệt exception vòng 3 cho SEC-001 và API-003. | User, 2026-11-11 | 2026-11-11 |
| D-10 | API-003 | accept-risk. Schema đã sửa và verify PASS. Không review vòng 4. | User, 2026-11-11 | 2026-11-11 |
| D-11 | Test API trên Dev | Người dùng yêu cầu test tất cả API trên Dev. Bảy endpoint HTTP 200. Các case lỗi đúng 422, 400, 405, 404. | User, 2026-11-11 | 2026-11-11 |
| D-12 | Sample mapping từ Dev | Sample response của sáu mapping và amenities lấy từ response Dev. Không bịa. phone và email để null trong file. | User, 2026-11-11 | 2026-11-11 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- D-2 đến D-6 đã được người dùng chọn ngày 2026-11-11. Xem bảng Quyết định hiện hành.
- D-7 ngày 2026-11-11: đúng một giá trị JSON thì ghi nguyên text `apps.srv_poi_info.holiday_exceptions`. JSON hỏng hoặc token thừa thì field null. Không đổi khóa. Không dùng mục A hay B của architecture.md §6.6.1.
- D-9 ngày 2026-11-11: người dùng phê duyệt exception vòng review 3 cho `SEC-001` và `API-003`. `review_plan.extra_round_approved_on` là `2026-11-11`. Vòng 3 ghi `SEC-001` fixed và `API-003` còn P1. Schema mảng đã sửa sau vòng đó. D-10: người dùng accept-risk, không chạy vòng 4.
- `operating_hours` theo `mapping_gld_srv_poi_info.md` §1.3. Probe này không đọc cột đó.
- `experience.keyword` có trong JSON. Response experiences chưa có field `keyword`.
- `holiday_exceptions` không còn cần quy ước `status` hay đổi dạng `date`, vì API không đọc các khóa đó.

## Sai lệch so với kiến trúc

- `FEATURE_WHERE` là chuỗi thường, bắt đầu bằng một dấu cách, để `WHERE` và điều kiện không dính thành `WHEREi`. Predicate giữ nguyên §6.4.1.
- `tests/test_srv_poi_api_mapping_required.py` thêm `strict=False` cho `zip` vì ruff B905. Hành vi zip giữ nguyên FILE block.
- D-7 không theo mục A hoặc B. Field `holiday_exceptions` ghi nguyên text cột bằng `@JsonRawValue` chỉ khi parser xác nhận đúng một giá trị JSON. JSON hỏng thì null. OpenAPI 3.1 mô tả field là mảng nullable vì Springdoc giữ type string của field Java.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| BACKLOG-INDEX | P2 | backlog | Gallery, review và features đang quét tuần tự. Bảng info còn sống khoảng 292 dòng. Task này không thêm DDL. | Index gallery `(poi_id, display_order, media_id)` và review `(poi_id)` trong task data. |
| API-002 | P1 | fixed | D-7: trả nguyên text khi JSON hợp lệ. | |
| SEC-001 | P1 | fixed | Kiểm tra đúng một giá trị JSON. Hợp lệ thì ghi đúng text. Hỏng hoặc có token thừa thì null. Không log nội dung. | |
| API-003 | P1 | accepted-risk | Người dùng accept-risk ngày 2026-11-11. Schema OpenAPI 3.1 là `type` `array` và `null`, `items.additionalProperties` true. verify PASS 11:46. Không có vòng review 4. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Compact và Features dùng apps.srv_poi_info.cover_id (data[].cover.id) và apps.srv_poi_info.cover_blob_url (data[].cover.file_key).
- Experiences lấy source từ apps.srv_poi_multi_lang.source_name.
- Phê duyệt lần chạy 2026-11-10 bằng `POSTGRES__DP_POI__*` trong `services/data-serving-service/.env`.
- D-2: Đồng ý theo khuyến nghị.
- D-3: Đồng ý theo khuyến nghị. Sửa cả mapping.
- D-4: ids Tối thiểu 1, tối đa 20 items, ids rỗng báo lỗi, thứ tự created_at DESC, poi_id ASC.
- D-5: Đồng ý Mảng rating_summary ngang hàng với data, một phần tử {rating_count, rating_avg_score}. API là GET /api/v1/pois/{poi_id}/reviews.
- D-6: Đồng ý theo khuyến nghị.
- D-7: Lấy nguyên apps.srv_poi_info.holiday_exceptions không cần parse, transform gì.

## Lịch sử quyết định

### D-1 — 2026-11-10

Dừng implement. Không thêm cột, không ALTER, không gán cột khác thay cho tên đã ghi.

`POST /api/v1/pois/compact` yêu cầu `data[].cover.id` từ `apps.srv_poi_media_gallery.cover_id` và `data[].cover.file_key` từ `apps.srv_poi_media_gallery.cover_blob_url`. Bảng `apps.srv_poi_media_gallery` trong `sql/postgres/gld_srv_serve.pg.sql` và entity `SrvPoiMediaGallery` không có hai cột đó. `cover_id` và `cover_blob_url` đang nằm trên `apps.srv_poi_info` và entity `SrvPoiInfo`.

`GET /api/v1/pois/{poi_id}/experiences` theo `docs/context/api-mapping/experiences.md` lấy `data.items.source` từ `apps.srv_poi_multi_lang.source`. Bảng và entity `SrvPoiMultiLang` không có cột `source`. Cột tên gần đó là `source_name`. Cột `experience` là `text`.

Các cột sau có trong DDL và entity, nên không nằm trong điểm dừng: gallery `media_id`, `blob_url`, `display_order`; review `rating_count`, `rating_overall`; info `cover_id`, `cover_blob_url`, `rating_count`, `rating_overall`, `source_name`.

Lựa chọn, và việc Main làm với từng lựa chọn:

1. Compact dùng `apps.srv_poi_info.cover_id` và `apps.srv_poi_info.cover_blob_url`. Experiences lấy `source` từ JSON trong `apps.srv_poi_multi_lang.experience` (cùng object với `title` và `description`). Main sửa `request.md` theo đúng câu này, chuyển `triage` rồi `waiting_architecture`, chạy `run-gate`.
2. Compact dùng `apps.srv_poi_info.cover_id` và `apps.srv_poi_info.cover_blob_url`. Experiences map `data.items.source` sang `apps.srv_poi_multi_lang.source_name`. Main sửa `request.md`, rồi cùng đường architecture như lựa chọn 1.
3. Giữ tên cột đúng như request và `experiences.md`. Việc thêm cột thuộc task data (`data_model_change`, `run-author --kind model`). Task này không ALTER. Main để status `user_decision` cho đến khi task data xong và DDL trong repo có đủ cột.

### D-1 — người dùng 2026-11-10

Compact và Features dùng apps.srv_poi_info.cover_id (data[].cover.id) và apps.srv_poi_info.cover_blob_url (data[].cover.file_key). Experiences lấy source từ apps.srv_poi_multi_lang.source_name.

`practical_info` giữ nguồn cover trong `practical_info.md` (`apps.srv_poi_media_gallery.media_id`, `apps.srv_poi_media_gallery.blob_url`). Mapping `features.md` và `experiences.md` được sửa cho khớp quyết định này trước khi code.

### D-ARCH-1 — 2026-11-10

RESULT: EVIDENCE_REQUIRED. Do not change code yet.

Architect `claude-opus-5-5` high, vòng 1, 262 giây. Status `waiting_evidence`. Probe: `evidence/probes/p-1.sql`, `p-2.sql`, `p-3.sql`, `p-4.sql`. Quyết định chờ người dùng: D-2, D-3, D-4, D-5, D-6 trong `architecture.md` §1.1.

### D-PROBE-1 — 2026-11-10

Bốn probe trả 0 dòng. Compose local là volume mới, chỉ có DDL trong repo. Chưa có evidence về giá trị và format gold.

Main đã bật Docker Desktop, `docker compose up -d postgres` trong `services/data-serving-service`, tạo schema `apps`, và chạy `sql/postgres/gld_srv_serve.pg.sql`. Volume `data-serving-service_postgres_data` mới. `apps.srv_poi_info` có 0 dòng. `p-1.txt` và `p-2.txt` là `(0 rows)`. `p-3.txt` và `p-4.txt` là `(0 rows)` cho `experience`, `holiday_exceptions`, `time_to_spend`, `best_time`, `cost_vnd`. Không có email, số điện thoại, hay secret trong output.

### D-PROBE-1 — lần chạy .env 2026-11-10

Probe trên database của .env (phê duyệt 2026-11-10): 292 dòng info còn sống đều partner và is_recommended, rating_overall null. experience là mảng JSON {title, keyword, description}. holiday_exceptions là [] hoặc {date, hours, title, status}. time_to_spend, best_time, cost_vnd là object một khóa.

Không ghi host, user, password. Kết quả: `evidence/results/p-1.txt`, `p-2.txt`, `p-3.txt`, `p-4.txt`, `p-shape.txt`.

`business_sector` sau lower/trim: null 100, accommodation 68, f_n_b 53, attraction 21, tour_n_activities 11, blank 11, shopping_n_retail 8, vehicle_rental 5, transport_route_base 5, spa_n_wellness 4, transport_on_demand 3, event 3. Bốn giá trị default của mapping đều có trong dữ liệu.

`source_name`: một nhóm `partner`, `is_recommended` true, 292 dòng, `rating_overall` có giá trị trên 0 dòng.

`experience`: 765 dòng không null, 401 JSON null, 364 mảng. Mỗi object có đúng `title`, `keyword`, `description`.

`holiday_exceptions`: 76 mảng rỗng, 5 mảng có phần tử, 0 chuỗi invalid. Khóa phần tử: `date`, `hours`, `title`, `status`.

`time_to_spend`, `best_time`, `cost_vnd`: mỗi cột 3 dòng không null, cả 3 là object JSON.

### D-2, D-3, D-4, D-6 — người dùng 2026-11-11

D-2: Đồng ý theo khuyến nghị. Pool chính là `is_recommended = true`. Fallback là dòng còn lại với `rating_overall` và `rating_count` đạt ngưỡng, và `source_name` khớp `rating_source` khi param có giá trị. Xoay một POI mỗi `business_sector` theo thứ tự ưu tiên, rồi `page`/`size` cắt chuỗi đó. `null` và chuỗi trắng bị loại. `accommodation` chỉ vào kết quả khi client đưa vào `business_sector_priority`.

D-3: Đồng ý theo khuyến nghị. Sửa cả mapping. Cả sáu API dùng `ApiResponse` như reviews (`success`, `code` 200, timestamp ISO, `errors`). Features có đủ `meta.pagination`.

D-4: ids Tối thiểu 1, tối đa 20 items, ids rỗng báo lỗi, thứ tự created_at DESC, poi_id ASC. Main đọc «báo lỗi» là HTTP 422, `ERR_VALIDATION_FAILED`, cùng status validation hiện có của compact. Thiếu `ids`, `ids` rỗng, hoặc quá 20 phần tử đều lỗi. Câu này sửa hợp đồng cũ «ids trống thì không lọc theo id» và «ids Required = không».

D-6: Đồng ý theo khuyến nghị. Body JSON hỏng của `POST /compact` trả HTTP 400, `ERR_BAD_REQUEST`. Sửa `GlobalExceptionHandler`. Thêm `app-security-reviewer`.

D-5 chưa chọn. `rating_summary` trong request gốc chỉ thuộc `GET /api/v1/pois/{poi_id}/reviews`.

### D-5 — người dùng 2026-11-11

Đồng ý Mảng rating_summary ngang hàng với data, một phần tử {rating_count, rating_avg_score}. API là `GET /api/v1/pois/{poi_id}/reviews`. `rating_count` lấy `apps.srv_poi_review.rating_count`. `rating_avg_score` lấy `apps.srv_poi_review.rating_overall`. Record mới nằm trong `api/dto`.

### D-7 — người dùng 2026-11-11

Lấy nguyên apps.srv_poi_info.holiday_exceptions không cần parse, transform gì. API ghi đúng text cột vào JSON. Cột null thì field null. Không đổi date, status, hours, title.

Người dùng chỉnh lại cùng ngày: kiểm tra cú pháp. JSON hợp lệ thì ghi lại đúng text đó. JSON hỏng thì field null. Không đổi khóa bên trong.

### D-8 — người dùng 2026-11-11

Request header và request param chỉ path `poi_id` là Required = có. Các field request khác, gồm body `ids`, Required = không. Hành vi D-4 giữ nguyên: thiếu, rỗng hoặc quá 20 `ids` vẫn HTTP 422. Main giữ bảng Response Required = có, cùng cách `amenities.md`, vì câu này chỉ nói request.

### Review vòng 2 — 2026-11-11

`API-002` được review ghi nhận là fixed. Hai finding P1 mới: `SEC-001` (`@JsonRawValue` có thể làm hỏng JSON nếu text cột không phải một giá trị JSON) và `API-003` (OpenAPI mô tả field là string trong khi response phát array hoặc null). Main giữ D-7, không thêm parse. Chờ người dùng chấp nhận rủi ro hoặc cho phép kiểm tra cú pháp mà không đổi nội dung.

### D-9 — người dùng 2026-11-11

Phê duyệt exception vòng 3 cho SEC-001 và API-003. Cap review thành 3 qua `review_plan.extra_round_approved_on` = `2026-11-11`.

### Review vòng 3 — 2026-11-11

`SEC-001` được ghi nhận là fixed. `API-003` vẫn P1: `implementation = Object.class` không thành mảng nullable. Main sửa schema công bố thành `type` `array` và `null`, `items` là object tự do. Không còn vòng 4 trong cap đã phê duyệt.

### D-10 — người dùng 2026-11-11

accept-risk cho API-003. Schema đã sửa và verify PASS. Người dùng chấp nhận không review vòng 4.

### D-11 — người dùng 2026-11-11

Hãy test tất cả API trên môi trường Dev. Process cổng 18081 đọc Postgres Dev. Bảy API HTTP 200. Case lỗi đúng mã. Kết quả sạch ở `evidence/runtime/dev-api-summary.json`. Process đã tắt.
