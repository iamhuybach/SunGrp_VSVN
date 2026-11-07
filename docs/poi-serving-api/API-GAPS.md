# POI Serving API — Chuẩn bị implement theo model POI mới

**Ngày:** 2026-10-29
**Nguồn spec:** [\[VISITVN\] API expose BE](https://sun-group.atlassian.net/wiki/spaces/VV/pages/558497946/VISITVN+API+expose+BE) + 11 trang con (cập nhật 27/10/2026)
**Nguồn model:** `vv_data_serving` @ `<host>`, schema **`apps`** (5 bảng `srv_poi_*`) — khảo sát trực tiếp 29/10/2026

> **Đính chính 29/10/2026 (sau khi quét đủ 67 repo ADO):** cả 11 API này **đã chạy trong `feed-service`**
> (`/v1/timeline/pois/*`), đọc từ DB app-layer replicate. Phần "đề xuất kiến trúc" ở §5 đã được thay thế
> bằng [DESIGN-AND-PLAN.md §A.3 và §C.1](DESIGN-AND-PLAN.md). Phần gap model (§3, §4) và
> câu hỏi (§7) vẫn còn nguyên giá trị.

---

## 1. Phạm vi

| # | API | Method | Endpoint | Trạng thái nguồn / Tiến độ thực tế |
|---|-----|--------|----------|-------------------------------------|
| 1 | Get compact POIs | GET | `/api/v1/pois/compact` | ✅ **Đã hoàn thành trong `data-serving-api`** (phân trang, lọc `ids`, đa ngôn ngữ `lang` & `Accept-Language`, RFC 9457 ProblemDetail, 42/42 tests pass) |
| 2 | Get featured POIs | GET | `/data/v1/pois/features` | Code `feed-service` dùng pool RNG, quota sector & cover check |
| 3 | Get POI gallery | GET | `/api/v1/pois/{poi_id}/gallery` | ✅ **Đã hoàn thành trong `data-serving-api`** (order by display_order, mime_type resolver, 404 validation) |
| 4 | Get POI summary | GET | `/data/v1/pois/{poi_id}/summary` | Thiếu timezone, destinations.name, short_address |
| 5 | Get POI general information | GET | `/data/v1/pois/{poi_id}/general-information` | Phụ thuộc `srv_poi_multi_lang` (đang rỗng); `feed-service` đọc JSONB và tính Open Now |
| 6 | Get POI experiences | GET | `/data/v1/pois/{poi_id}/experiences` | Phụ thuộc `srv_poi_multi_lang.experience`; `feed-service` dùng bảng map `experience_icon_mapping.json` |
| 7 | Get anchored POIs | GET | `/data/v1/pois/{poi_id}/anchored-pois` | **`feed-service` gọi sang `data-poi-management`** lấy khoảng cách |
| 8 | Get nearby POIs | GET | `/data/v1/pois/{poi_id}/nearby-pois` | **`feed-service` dùng PostGIS KNN** + lọc cùng destination (DB `apps` không có PostGIS) |
| 9 | Get POI reviews | GET | `/api/v1/pois/{poi_id}/reviews` | ✅ **Đã hoàn thành trong `data-serving-api`** (phân trang, ranh giới Data trả thô, 404 validation; chưa thêm lọc `lang` do `srv_poi_review` chưa có cột này) |
| 10 | Get POI amenities | GET | `/api/v1/pois/{poi_id}/amenities` | ✅ **Đã hoàn thành trong `data-serving-api`** (gom nhóm theo amenity_group, nhãn tiếng Việt, 404 validation) |
| 11 | Get POI policies | GET | `/data/v1/pois/{poi_id}/policies` | **`feed-service` hiện đang disabled và trả mảng rỗng `{"items": []}`** |
| 12 | Get top pick POIs của destination | — | TBD | Chưa có spec |
| 13 | Get related POIs của destination | — | TBD | Chưa có spec |

---

## 2. Hợp đồng chung (áp dụng cho cả 11 API)

### Request header
| Field | Required | Ghi chú |
|-------|----------|---------|
| `Authorization` | Y | Bearer token **service-to-service**, không phải user token. [2026-11-06, GATE-001] API Management (gateway) kiểm tra token; `data-serving-service` không kiểm tra và chỉ nhận traffic qua gateway. |
| `X-App-Language` | Y | `vi` / `en` / `ko`; không có bản dịch → fallback ngôn ngữ gốc |
| `X-Request-ID` | N | Echo lại trong `request_id` |
| `Content-Type` | Y (POST) | `application/json` |

> ⚠️ API 9 (reviews) dùng `X-User-ID` trong logic (`is_own_review`, `is_helpful_by_viewer`) nhưng **không khai báo** ở bảng header → cần chốt lại với BA.

### Response envelope
```json
{ "request_id": "...", "code": 0, "message": "success", "server_time": 1791945900,
  "count": 2, "data": [] }
```
- `code = 0` là success (không phải HTTP status).
- `count` xuất hiện ở API dạng list; API 5/6/11 trả `data` là object, không có `count`.
- `server_time` = Unix **seconds**.

### Bảng lỗi chuẩn
| HTTP | code | error_code | Khi nào |
|------|------|-----------|---------|
| 400 | 1 | — | Thiếu `Authorization` hoặc `X-App-Language` (`Authorization` do API Management kiểm tra, GATE-001) |
| 400 | 3 | `INVALID_IDS` / `INVALID_QUERY` | Sai UUID, vượt giới hạn, body không parse được |
| 401 | 4 | — | Token S2S sai/hết hạn |
| 403 | 3 | — | Service gọi không nằm trong allowlist (API Management trả, GATE-001) |
| 404 | 3 | `POI_NOT_FOUND` / `POI_UNAVAILABLE` | Không tồn tại / ẩn / soft-delete |
| 429 | 1 | — | Rate limit |
| 500 | 1 | `ANCHOR_SERVICE_ERROR` (API 7) | Lỗi Gold service / DB |
| 503 | 1 | — | Distance service down (API 8) |

→ Cần **một `@RestControllerAdvice` chung** + enum `ErrorCode`. Pattern đã có sẵn ở
[GlobalExceptionHandler.java](../../src/main/java/vn/visitvietnam/poi/management/common/web/GlobalExceptionHandler.java), tái sử dụng được.

---

## 3. Model POI mới — DDL thực tế trong schema `apps`

Tất cả cột đều là `text` / `boolean` / `numeric` / `integer` / `timestamp` (**không có `jsonb`, không có PostGIS**).
Mọi bảng đều có `row_hash`, `created_at`, `updated_at`, `deleted_at` (soft delete).

### `apps.srv_poi_info` — PK `(poi_id)`
```
poi_id, poi_name, source_name, business_sector, business_category, subcategory_tags,
destination_id, full_address, street, ward, district, city, country_code, postal_code,
lat (float8), lng (float8), phone, email, website_url,
operating_status, is_verified, is_recommended, is_bookable,
operating_hours (text/JSON), holiday_exceptions (text/JSON),
rating_overall (numeric), rating_count (int), review_count (int)
```

### `apps.srv_poi_multi_lang` — PK `(poi_id, lang)`
```
poi_id, lang, source_name, time_to_spend, best_time, cost_vnd, description, experience (text/JSON)
```

### `apps.srv_poi_media_gallery` — PK `(media_id)`
```
media_id (text, sha256), poi_id, source_name, photo_api_uri, display_order,
width_px, height_px, photographer, blob_url, thumbnail_url, is_cover, is_active
```

### `apps.srv_poi_amenity` — PK `(poi_id, business_sector, amenity_group, amenity_raw)`
```
poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, service_flags
```

### `apps.srv_poi_review` — PK `(review_id)`
```
review_id, poi_id, source_name, rating_overall, rating_count,
title, review_text, rating, review_date (text), author_name
```

### Độ phủ dữ liệu DEV (29/10/2026)
| Bảng | Rows | Ghi chú |
|------|------|---------|
| `srv_poi_info` | **24** | 100% `source_name = partner`; `lat/lng`, `rating_*`, `destination_id`, `subcategory_tags` = **NULL toàn bộ**; `operating_status` = chuỗi rỗng |
| `srv_poi_multi_lang` | **0** | Chưa nạp |
| `srv_poi_media_gallery` | 1.131 (131 POI) | 131 cover; **chỉ 396/1131 có `blob_url`**, 735 còn ở `photo_api_uri` Google; `thumbnail_url` = 0 |
| `srv_poi_amenity` | 58 | Chủ yếu `f_n_b` |
| `srv_poi_review` | **0** | Chưa nạp |

Đối chiếu dữ liệu legacy đang chạy ở schema `public` cùng DB:
`poi_master` 52.673 · `poi_detail` 52.673 · `poi_enrichment_display` 50.509 · `poi_review` 254.201.

> **Kết luận:** model `apps.srv_poi_*` mới chỉ nạp nhánh partner. Không thể QC/integration-test thật
> cho tới khi pipeline Fabric Gold đẩy đủ dữ liệu sang.

---

## 4. Gap giữa spec và model (xếp theo mức chặn)

### 🔴 Chặn — không implement được nếu không bổ sung nguồn

| ID | Gap | Ảnh hưởng | Đề xuất |
|----|-----|-----------|---------|
| **G1** | `srv_poi_media_gallery` **không có `blur_hash` và `mime_type`** — cả hai spec đánh Required = Y | API 1, 2, 3, 4, 8 | Thêm 2 cột vào Gold + serving; hoặc BE tự suy `mime_type` từ đuôi file và bỏ `blur_hash` khỏi contract |
| **G2** | Không tồn tại bảng `ref_business_category` → `business_sector_label` (Required Y) không có nguồn | API 1, 2, 4, 8 | Tạo `apps.ref_business_category(code, label_vi/en/ko)`; tạm thời có thể map từ `poi_mgmt.category` (5 nhóm, chỉ có tên VI) |
| **G3** | Không tồn tại bảng `ref_amenity`; `amenity_raw` là key thô Google (`dineIn`, `parkingOptions.paidParkingLot`) và **có cả biểu thức SQL** lọt vào dữ liệu: `json_type in ('bar','pub',...)` | API 10 | Tạo `ref_amenity(amenity_code, label_vi/en/ko)` + mapping `amenity_raw → amenity_code`; làm sạch các row chứa biểu thức SQL |
| **G4** | **Không có nguồn policies nào** trong `apps` (legacy `poi_detail.poi_policy_json` phần lớn là `{}`) | API 11 | Chốt với BA: Partner Portal nhập, hay AI generate; cần bảng `srv_poi_policy` |
| **G5** | Không có cờ `is_anchor` / `anchor_type` trong `apps`; không có PostGIS | API 7, 8 | Spec đã note "team Data tách service riêng cho anchor + nearby". Nguồn hiện có: `poi_mgmt.anchored_pois` (39 rows) và `public.anchor_poi_map` (0 rows) |
| **G6** | `holiday_exceptions` đúng khái niệm nhưng **sai format**: `date` = `21/07/2026` (DD/MM/YYYY) vs spec `YYYY-MM-DD`; giờ lồng `hours:[{open_time,close_time}]`; `status` thay cho `is_closed`; thiếu `is_open_all_day`/`is_closed` | API 4, 5 | Chuẩn hoá ở Gold, hoặc map ở serving |

### 🟠 Thiếu field — contract cần điều chỉnh hoặc join thêm

| ID | Gap | Ảnh hưởng | Đề xuất |
|----|-----|-----------|---------|
| **G7** | `media_id` là `text` (sha256 64 ký tự), spec khai **Integer** | API 1, 2, 3, 4, 8, 9 | Đổi spec sang String — đừng ép kiểu |
| **G8** | Không có cột `operating_timezone` (Required Y) | API 2, 4, 5 | Hardcode `Asia/Ho_Chi_Minh` cho VN, hoặc thêm cột |
| **G9** | `ratings` là **Array theo nguồn**, nhưng `srv_poi_info` chỉ có 1 bộ `(source_name, rating_overall, rating_count)` / POI | API 1, 2, 4, 8 | Trả array 1 phần tử; nếu cần đa nguồn thật → tách bảng `srv_poi_rating(poi_id, source, ...)` |
| **G10** | `destination_id` là **text đơn**, không có tên destination; spec cần `destinations[]` có `id` + `name`. **Chưa chốt ID space** (Strapi ID vs UUID) vì quan hệ POI ↔ Destination thực tế là **n-n** (2,3 destination/POI) | API 4 | Cần Data đổi sang quan hệ n-n (bảng `srv_poi_destination`) và chốt chuẩn ID space |
| **G11** | Không có `short_address` (API 4) và `content_language` (API 4) | API 4 | BE tự format `short_address`; `content_language` = lang đã resolve |
| **G12** | `cost_vnd` (model) vs `cost` (spec); spec API 5 còn tham chiếu tên bảng Gold `gld_srv_poi_multi_lang` | API 5 | Thống nhất tên field trong spec |
| **G13** | `icon_key` của experiences không có cột riêng | API 6 | Legacy lưu trong JSON `experiences[].keyword` — xác nhận `srv_poi_multi_lang.experience` giữ nguyên key đó (hiện 0 row nên chưa verify được) |
| **G14** | API 9 — model mới **mất** so với spec: `lang`, `is_verified`, `reviewer.user_id`, `reviewer.avatar`, `media[]`, `helpful_count`, `partner_reply`, `is_own_review` | API 9 | Legacy `public.poi_review` **có** `lang`, `reviewer_name`, `media_urls_json`, `helpful_votes`, `response_text`, `responded_at` → bổ sung lại vào Gold. Phần Visit Vietnam review (user_id, avatar, helpful, Proof of Visit) nằm ở App BE, không phải Data. [OUT_OF_DATE 2026-11-06, D-10] Serving theo gold: `srv_poi_review` không có `lang`, `source`, `source_name`. |

### 🟡 Mâu thuẫn trong chính spec — cần BA xác nhận

| ID | Vấn đề |
|----|--------|
| S1 | API 1 sample trả `rating` (object) nhưng bảng field định nghĩa `ratings` (array) |
| S2 | API 2: `limit` ghi "Min: 10, Max: 5"; status code lại nói "limit vượt 50" |
| S3 | API 4 (summary, 1 POI) nhưng sample response trả **mảng 3 POI** + `count` — copy nhầm từ API 2 |
| S4 | API 9: param chỉ khai `limit` ("tối đa 5") nhưng status code nhắc `offset` và `source`, sample request có `offset`, `lang`, `source`. [OUT_OF_DATE 2026-11-06, D-10] `srv_poi_review` không có `lang`/`source`, nên hai filter này không áp dụng. |
| S5 | API 10 sample JSON thiếu dấu `}` đóng; `amenity_code` viết hoa (`GIFT_SHOP`) trong khi dữ liệu thực là camelCase |
| S6 | API 1 `data.cover` Required = N, API 2 lại Required = Y cho cùng một object |

---

## 5. Đề xuất kiến trúc

**Service mới, tách riêng** — đề xuất `data-serving-api` (Spring Boot, cùng stack với `data-poi-management`).

Lý do không gắn vào `data-poi-management`:
- Repo đó là **admin-facing**, prefix `/api/v1/pois`, chạy trên schema `poi_mgmt`, có write + Flyway + outbox/EventHub.
- 11 API này là **read-only, service-to-service**, chạy trên schema `apps`, traffic app-scale, cần cache + rate limit riêng.
- Hiện **không có dòng code nào** trong workspace tham chiếu `srv_poi_*` — đây là greenfield.

Thiết kế:
- Cùng DB `vv_data_serving`, user read-only, `search_path = apps`.
- Read-only: **không Flyway**. DDL của `apps` do pipeline Fabric sở hữu.
- Auth S2S và allowlist caller (phục vụ 403) do API Management (gateway) đảm nhận; service không kiểm tra token. Điều kiện bắt buộc khi deploy: service chỉ nhận traffic qua gateway (network isolation), và phải kiểm tra điều kiện này trước khi mở traffic. [2026-11-06, GATE-001]
- Cache: `summary` / `general-information` / `experiences` / `amenities` / `policies` TTL ngắn; `gallery` TTL dài.
- `anchored-pois` + `nearby-pois` gọi sang **distance service riêng** (spec đã chốt hướng này).
- Tái sử dụng từ `data-poi-management`: `GlobalExceptionHandler`, pattern DTO/Mapper, Dockerfile, `pipeline.yml`.

---

## 6. Thứ tự implement đề xuất

| Wave | API | Điều kiện tiên quyết |
|------|-----|---------------------|
| **0** | Khung service: envelope, error handler, health, OpenAPI (S2S auth ở API Management, xem §5) | — |
| **1** | 3 Gallery · 10 Amenities | G1 (blur_hash/mime_type), G3 (ref_amenity) |
| **2** | 1 Compact · 4 Summary | G2 (ref_business_category), G8 (timezone), G10 (destination name), dữ liệu `lat/lng` + `rating_*` |
| **3** | 5 General information · 6 Experiences | `srv_poi_multi_lang` có dữ liệu; G6 (holiday_exceptions đúng shape) |
| **4** | 2 Featured | Pool partner + rule xoay vòng từ BA |
| **5** | 9 Reviews | G14 — bổ sung field vào Gold; chốt ranh giới Data ↔ App BE |
| **6** | 7 Anchored · 8 Nearby | Distance service |
| **7** | 11 Policies | G4 — chốt nguồn dữ liệu |

---

## 7. Câu hỏi cần chốt trước khi code

**Với team Data (pipeline Fabric Gold):**
1. Bao giờ `apps.srv_poi_*` nạp đủ 52k POI (hiện 24, toàn partner)?
2. Bổ sung `blur_hash`, `mime_type` vào `srv_poi_media_gallery` được không? 735/1131 ảnh chưa có `blob_url` — khi nào xong?
3. `holiday_exceptions` đang lưu sai shape (lịch tuần thay vì ngoại lệ theo ngày) — sửa ở Gold hay serving?
4. `ref_business_category` và `ref_amenity` sẽ nằm ở đâu? Ai owner?
5. `srv_poi_multi_lang.experience` có giữ key `keyword` như legacy `poi_enrichment_display.experiences[]` không?
6. Rating đa nguồn: tách bảng hay giữ 1 dòng/POI?

**Với BA:**
7. Các mâu thuẫn S1–S6 ở mục 4.
8. **[ĐÃ CHỐT 03/11]** API 9: Data **không nhận `X-User-ID`**. Data (`data-serving-api`) chỉ trả các trường review thô/ingested; các trường tương tác động (`is_own_review`, `helpful_count`, `partner_reply`, `avatar`) do App BE (`feed-service`) sở hữu và quản lý.
9. API 11: nguồn policies lấy từ đâu — Partner Portal hay AI generate? (Lưu ý: khảo sát code `feed-service` thực tế endpoint này đang disabled và trả rỗng `{"items": []}`).
10. API 11: Data trả format hiển thị sẵn (`sections[].items`) hay App tự render?
11. Spec 12 & 13 (top pick / related POIs của destination) — có cần không, hay BE tự handle?

**Với Kiến trúc:**
12. **[ĐÃ CHỐT]** Tạo repo mới `data-serving-api` (đã khởi tạo trên Java 26, Spring Boot 4.1.1, triển khai xong API Compact POIs).
13. Rate limit + cache layer đặt ở service hay API Gateway?

---

## 8. Nguồn tham chiếu nhanh

- Spec gốc: pages `558497946` (index), `558497988`–`558498337` (11 API), space `VV`.
- Model: `vv_data_serving` → schema `apps` (5 bảng), legacy `public` (`poi_master`, `poi_detail`, `poi_enrichment_display`, `poi_review`).
- Nguồn anchor hiện có: `poi_mgmt.anchored_pois` (39), `public.anchor_poi_map` (0).
- Nguồn category hiện có: `poi_mgmt.category` (5 nhóm, chỉ tên tiếng Việt).
