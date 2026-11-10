# Request

## User outcome

Năm API Serve App POI trong `C:\Users\bachnh\Downloads\API_Serve_App_POI_Specs.md` nằm ở năm file riêng dưới `docs/context/api-mapping/`, cùng cấu trúc mục và cột với `docs/context/api-mapping/MAPPING_SAMPLE.md`. Header và param trùng ý nghĩa với `compact.md`, `gallery.md`, `reviews.md`, `amenities.md` dùng cùng tên Field.

## Scope

### In scope

- `docs/context/api-mapping/features.md` — mục 1, GET `/data/v1/pois/features`
- `docs/context/api-mapping/summary.md` — mục 2, GET `/data/v1/pois/{poi_id}/summary`
- `docs/context/api-mapping/must-know.md` — mục 3, tiêu đề Get POI must know; endpoint trong file là `/data/v1/pois/{poi_id}/general-information`
- `docs/context/api-mapping/experiences.md` — mục 4, GET `/data/v1/pois/{poi_id}/experiences`
- `docs/context/api-mapping/general-information.md` — mục 5, GET `/data/v1/pois/{poi_id}/general-information`

Mỗi mục một file. Không gộp mục 3 và mục 5 dù cùng path.

### Out of scope

- Sửa `MAPPING_SAMPLE.md`, `compact.md`, `gallery.md`, `reviews.md`, `amenities.md`
- `docs/poi-serving-api/`, Java, DDL, entity, đối chiếu `PoiController`
- Đổi hành vi API đang chạy
- `run-author`, Architect, commit trong lượt triage

## Acceptance criteria

- Đúng năm file trên. Không sửa `MAPPING_SAMPLE.md`, `compact.md`, `gallery.md`, `reviews.md`, `amenities.md`.
- Mỗi file có đúng các mục và đúng cột của mẫu: Tổng quan, Request header, Request param, Response, Status code, Sample request, Sample response.
- Required ghi có hoặc không. Type ghi thường: string, integer, number, boolean, array, object.
- Đổi tên Field chỉ khi cùng ý nghĩa: header ngôn ngữ → `Accept-Language`; query ngôn ngữ → `lang`; mã request → `X-Request-Id`; id POI trên path → `poi_id`; phân trang → `page` và `size`. `Authorization` không có trong bốn file hiện có thì giữ nguyên. Field khác nghĩa thì giữ tên file nguồn.
- Response giữ field và Source Field của file nguồn. Mảng thì viết `data[]`. Source Field đã là `srv_poi_*` thì thêm tiền tố `apps.`. Ô nguồn trống thì ghi `không có cột`.
- D-03: `request_id` thành `meta.trace_id`, `server_time` thành `meta.timestamp`, `count` thành `meta.pagination.total_items`. `code` và `message` giữ top-level. Sample response đổi đúng các key đó, giữ nguyên giá trị và phần `data`.
- Status code không có trong file nguồn thì một dòng: HTTP = không có, Code = không có, Description = không có trong file nguồn. Không chép bảng 401, 403, 429 từ mẫu.
- Sample request và sample response giữ nguyên JSON của đúng mục. Không đổi body JSON thành query string.

## Constraints

- Nguồn duy nhất là `C:\Users\bachnh\Downloads\API_Serve_App_POI_Specs.md`. Mẫu chỉ lấy tên mục và cột. Bốn file compact, gallery, reviews, amenities chỉ dùng để lấy tên Field ở Request header và Request param.
- Header nguồn `X-App-Language` là header ngôn ngữ, đổi thành `Accept-Language`. D-04: query `lang` thêm cho cả năm file, required `không`, ưu tiên hơn `Accept-Language`; cả hai trống thì `vi`; thiếu bản thì `vi`. `Accept-Language` required `không`. `X-Request-ID` là mã request, đổi thành `X-Request-Id`. `poi_id`, `page`, `size` đã trùng tên chuẩn thì giữ nguyên. `Authorization`, `business_sector_priority`, `fallback_min_rating`, `fallback_min_review_count`, `rating_source` giữ tên nguồn.
- Source Field bắt đầu bằng `srv_poi_` thì thêm tiền tố `apps.` (`srv_poi_info.poi_id` thành `apps.srv_poi_info.poi_id`). Giá trị không bắt đầu bằng `srv_poi_` (ví dụ `gld_srv_poi_info.business_sector`) giữ nguyên. Ô trống, hoặc mục không có cột Source Field (mục 5), ghi `không có cột`.
- Mục 1 sample request là JSON có `limit`; bảng param của mục đó là `page` và `size`. Giữ nguyên JSON, không đổi thành query string.
- Mục 2 không có sample response trong file nguồn. Giữ mục Sample response và ghi không có trong file nguồn. Không bịa JSON.
- Không đổi hành vi. Không commit trong lượt triage.

## Classification rationale

- Complexity: `low`. Không có signal. Việc là tách tài liệu, không có logic trạng thái, đồng thời, retry, CDC, grain, hay key.
- Risk: `low`. Không đổi hành vi; thay đổi hẹp và kiểm được bằng đọc file.
- Architecture: `not_required`. Không đổi grain, key, owner, transaction, CDC, watermark, lock, hay orchestration. Không có đánh đổi triển khai. Năm file Markdown mới không phải tám source file của service.
- Evidence: `not_required`. Đúng sai so được với spec và mẫu bằng kiểm tra repository. Không phụ thuộc phân bố dữ liệu hay schema runtime.
- Runtime proof: `not_required`. Không có bước Fabric DEV hay `docker compose`.
- Reviewer routing: `required_reviewers` rỗng. `api-contract-reviewer` chỉ khi diff chạm `api/`, `dto/`, `domain/entity/`, `OpenApiConfig`, hoặc `sql/postgres/gld_srv_serve.pg.sql`. `app-security-reviewer` và `jpa-performance-reviewer` không có file tương ứng. `risk_gate` không bắt buộc vì `risk_level` là `low`. Không fast lane vì hơn hai file.
