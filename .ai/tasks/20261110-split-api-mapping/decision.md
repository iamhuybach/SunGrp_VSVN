# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Phân loại | Complexity: `low`. Không có signal. Việc là tách tài liệu, không có logic trạng thái, đồng thời, retry, CDC, grain, hay key. Risk: `low`. Không đổi hành vi; thay đổi hẹp và kiểm được bằng đọc file. Architecture: `not_required`. Không đổi grain, key, owner, transaction, CDC, watermark, lock, hay orchestration. Không có đánh đổi triển khai. Năm file Markdown mới không phải tám source file của service. Evidence: `not_required`. Đúng sai so được với spec và mẫu bằng kiểm tra repository. Không phụ thuộc phân bố dữ liệu hay schema runtime. Runtime proof: `not_required`. Không có bước Fabric DEV hay `docker compose`. Không fast lane vì hơn hai file. | request.md ## Classification rationale | 2026-11-10 |
| D-02 | Review | `required_reviewers` rỗng. `api-contract-reviewer` chỉ khi diff chạm `api/`, `dto/`, `domain/entity/`, `OpenApiConfig`, hoặc `sql/postgres/gld_srv_serve.pg.sql`. `app-security-reviewer` và `jpa-performance-reviewer` không có file tương ứng. `risk_gate` không bắt buộc vì `risk_level` là `low`. Không fast lane vì hơn hai file. | request.md ## Classification rationale | 2026-11-10 |
| D-03 | Envelope meta | Các cột request_id, server_time, count,... Hãy đưa về quy ước chung như giống 4 api đã có (đưa vào mục meta). | user 2026-11-10 | 2026-11-10 |
| D-04 | Query lang | Giống compact cho cả năm file: lang không bắt buộc, ưu tiên hơn Accept-Language, cả hai trống thì vi, thiếu bản thì vi. Accept-Language đổi thành required không. Main sửa Request param của năm file. | user 2026-11-10 | 2026-11-10 |
| D-05 | Source field | `/data/v1/pois/{poi_id}/experiences` bỏ field `icon_key`. `/data/v1/pois/features`: `data[].cover.id` và `data[].cover.file_key` lấy giống `/api/v1/pois/compact`. Tất cả mapping, trừ những field là object, bỏ tất cả những field không có source field. `/data/v1/pois/{poi_id}/general-information` map theo những field đang có trong `srv_poi_info`. | user 2026-11-10 | 2026-11-10 |
| D-06 | general-information | `apps.srv_poi_multi_lang`: `time_to_spend`, `best_time`, `cost_vnd` có đưa vào general-information. general-information có bung path giống must-know. | user 2026-11-10 | 2026-11-10 |
| D-07 | practical_info | giữ nguyên mapping `/data/v1/pois/{poi_id}/summary` cũ, 3 API này: `/data/v1/pois/{poi_id}/summary`, `/data/v1/pois/{poi_id}/general-information` và `/data/v1/pois/{poi_id}/must-know` hãy đánh dấu tài liệu là out of date. Hãy xử lý thành một API mới `/data/v1/pois/{poi_id}/practical_info` để gom lại. | user 2026-11-10 | 2026-11-10 |
| D-08 | Path và tên file | Những `/data` thay thành `/api` cho 6 mapping api. `/api/v1/pois/{poi_id}/practical_info` thêm sample response. Những api-mapping nào đã out of date thì đánh dấu ngay từ tên file. | user 2026-11-10 | 2026-11-10 |
| D-09 | (ood) và hoàn thành | Thay vì out-of-date viết tắt và thêm ngoặc thành (ood). Sau đó đánh dấu task đã hoàn thành và commit sau đó tôi sẽ tự push. | user 2026-11-10 | 2026-11-10 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-10: `architecture = not_required`, `evidence = not_required`, `complexity = low`, `risk_level = low`. Không fast lane vì hơn 2 file. Không chạy `run-author`, không chạy Architect, không commit.
- 2026-11-10: Giống compact cho cả năm file: lang không bắt buộc, ưu tiên hơn Accept-Language, cả hai trống thì vi, thiếu bản thì vi. Accept-Language đổi thành required không.
- 2026-11-10: `apps.srv_poi_multi_lang`: `time_to_spend`, `best_time`, `cost_vnd` có đưa vào general-information. general-information có bung path giống must-know.
- 2026-11-10: giữ nguyên mapping `/data/v1/pois/{poi_id}/summary` cũ. Ba tài liệu summary, general-information, must-know đánh dấu out of date. Gom vào `/data/v1/pois/{poi_id}/practical_info`.
- 2026-11-10: Những `/data` thay thành `/api` cho 6 mapping api. `/api/v1/pois/{poi_id}/practical_info` thêm sample response. Những api-mapping nào đã out of date thì đánh dấu ngay từ tên file.
- 2026-11-10: Thay vì out-of-date viết tắt và thêm ngoặc thành (ood). Sau đó đánh dấu task đã hoàn thành và commit sau đó tôi sẽ tự push.

## Lịch sử quyết định

- 2026-11-10 D-01: ghi phân loại triage vào `task-state.yaml`. `scope.systems` là `serving-api` (tài liệu mapping), không đặt `poi-serving-api` vì token đó kéo lane Maven vào context pack.
- 2026-11-10 D-02: không mở review Java. Diff dự kiến chỉ năm file `docs/context/api-mapping/`.
- 2026-11-10: viết năm file đúng `request.md`. Không lệch kiến trúc. Mục 2 Sample response ghi không có trong file nguồn. Source `gld_srv_poi_*` giữ nguyên, không thêm `apps.`.
- 2026-11-10 D-03: user yêu cầu đưa `request_id`, `server_time`, `count` vào `meta` theo compact, gallery, reviews, amenities. Áp dụng cho năm file response và sample response. Kiểu `meta.timestamp` giữ integer Unix của spec. Không thêm `success`, `errors`, `meta.error_code`.
- 2026-11-10 D-04: thêm query `lang` vào năm file. `features.md` đặt `lang` trước `page`. Bốn file có `poi_id` đặt `lang` ngay sau path. Mô tả `Accept-Language` đổi theo hợp đồng compact. Sample JSON giữ nguyên.
- 2026-11-10 D-05: áp dụng trên năm file của task. Giữ `code`, `message`, `data` và `meta.*`. Field kiểu object giữ dù source là `không có cột`. `general-information` chỉ gán cột có trong `apps.srv_poi_info`: `business_sector`, `operating_hours`, `holiday_exceptions`. Không sửa compact, gallery, reviews, amenities, MAPPING_SAMPLE.
- 2026-11-10 D-06: `data.time_to_spend`, `data.best_time` lấy cột cùng tên; `data.cost` lấy `cost_vnd`. Path `operating_hours.*` và `holiday_exceptions.*` chép từ must-know, source `apps.srv_poi_info`.
- 2026-11-10 D-07 (đã thay): từng gộp vào `summary.md`, rồi user yêu cầu giữ mapping summary cũ.
- 2026-11-10 D-07: khôi phục bảng field summary trước khi gộp. Ba file đánh dấu `out of date`, trỏ tới `practical_info.md`. API mới lấy field summary cộng `time_to_spend`, `best_time`, `cost_vnd` và path giờ/ngày lễ của must-know. Một cây `operating_hours.value`. `data.cost` lấy `cost_vnd`. Không bịa sample JSON gộp.
- 2026-11-10 D-08: sáu file đổi `/data/v1` thành `/api/v1`. Ba file out of date đổi tên thành `out-of-date.summary.md`, `out-of-date.general-information.md`, `out-of-date.must-know.md`. Sample `practical_info` ghép giá trị có sẵn: thẻ POI từ sample features, khối must-know từ sample general-information. `data.id` trùng `poi_id` của sample request. `phone`, `email`, `website_url` là null. Không có UUID destination trong spec nên sample không có `destinations`.
- 2026-11-10 D-09: tiền tố file và ô `Trạng thái` đổi thành `(ood)`. Task ở `ready_to_merge`: bộ status không có giá trị completed. User xác nhận hoàn thành và tự push.
