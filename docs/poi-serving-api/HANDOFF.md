# HAND-OFF — Build API POI trên model mới

**Người bàn giao:** thanhtd05 · **Ngày:** 2026-11-02 · **Cập nhật:** 2026-11-03

> **Cập nhật 03/11/2026:** Repo `data-serving-api` (Spring Boot 4.1.1, Java 26) **đã được khởi tạo và đang active**.
> Đã clone và kiểm tra trực tiếp mã nguồn `feed-service` và `go-common`. Endpoint đầu tiên `GET /api/v1/pois/compact`
> đã hoàn thành triển khai và test (39/39 passed, sync spec vào `openspec/specs/poi-compact-api/`).

**Mọi số liệu trong tài liệu này đo trực tiếp trên DB ngày 02/11/2026.** Chạy lại bằng
[`scripts/check-gaps.py`](scripts/check-gaps.py) (hướng dẫn ở §9).

### Đọc theo thứ tự

1. **Tài liệu này** — hiện trạng, gap register, việc cần chốt. Đây là entry point.
2. [API-GAPS.md](API-GAPS.md) — chi tiết từng field của 11 spec API + mapping sang model.
3. [DESIGN-AND-PLAN.md](DESIGN-AND-PLAN.md) — kiến trúc đích, phase, chiến lược test/cutover.

---

## 1. Tóm tắt một phút

Team Data ra **model POI mới** (`apps.srv_poi_*`) và muốn **phục vụ bằng API thay vì replicate DB**.
BA đã viết **11 spec API** `/data/v1/pois/*`
([index Confluence](https://sun-group.atlassian.net/wiki/spaces/VV/pages/558497946/VISITVN+API+expose+BE)).

**Điều quan trọng nhất cần biết trước khi code:** 11 API này **không phải API mới**. Cả 11 **đã chạy
trong `feed-service`**, đọc từ DB app-layer được replicate từ `public`. Việc thật sự phải làm là
**đổi nguồn dữ liệu** cho feed-service và **chia lại trách nhiệm** giữa Data và BE — không phải viết từ đầu.

```
HÔM NAY:   App ──► feed-service ──► FeedDB (replicate từ public)
ĐÍCH:      App ──► feed-service ──► data-serving-api ──► vv_data_serving.apps
                   (giữ nguyên endpoint)   (MỚI, S2S, read-only)
```

Spec ghi rõ header `Authorization: Bearer token service-to-service **của BE**` → Data phục vụ BE,
app không gọi thẳng. Nên endpoint public của feed-service giữ nguyên, app **không phải sửa gì**.

---

## 2. Bản đồ hệ thống

### Repo (ADO project `Sun-Visit-VN`, **68 repo** tại thời điểm 02/11 — con số này tăng theo thời gian; chỉ liệt kê cái liên quan)

| Repo | Vai trò | Branch mặc định | Ghi chú |
|---|---|---|---|
| **`data-serving-api`** | **Service chính (repo hiện tại)** — S2S read-only trên `apps.*` | `main` / `feat/*` | Spring Boot 4.1.1, Java 26. Đã implement xong `GET /api/v1/pois/compact` |
| **`feed-service`** | **Reference implementation — 11 API đã chạy ở đây** | `develop` | Go/Gin. **Đã clone về máy & phân tích code** |
| `go-common` | Thư viện chung, chứa `cominfra/travelfeed.ItemPOI` | `main` | Định nghĩa shape POI của app layer. **Đã kiểm tra** |
| `data-poi-management` | POI read+write cho **portal** | `main` | Java. Đọc `public.*`, sở hữu `poi_mgmt` |
| `data-destination-management` | Destination read-only cho portal | `main` | Java. Mẫu tham khảo cho service read-only |
| `partner-manager-service` | BFF **cho portal** (`/v1/crm`) | `main` | Go. Không có surface app-facing |
| `admin-portal` | Portal UI | `main` | React/TS |
| `fabric-visitvn` | Pipeline Fabric sinh ra `public.*` và `apps.*` | `main` | Chưa clone |
| `tripplanner-orchestrate`, `ai-personalization-inference`, `ai-hub-service` | Consumer giữ `poi_id` | | Xem §7 |

Liệt kê đầy đủ: `scripts/list-repos.sh`.

### Database

**`vv_data_serving`** — DEV `<host>`, PROD `<host>`.
Một DB, **5 schema, 5 chủ sở hữu khác nhau**:

| Schema | Chủ sở hữu | `data-serving-api` đọc? |
|---|---|---|
| `apps` (`srv_poi_*`) | pipeline Fabric Gold | ✅ **nguồn duy nhất** |
| `public` (`poi_master`…) | serving legacy | ❌ đang bị thay thế |
| `poi_mgmt` | `data-poi-management` | ❌ vi phạm sở hữu service |
| `destination_mgmt` | `data-destination-management` | ❌ |
| `admin_ref` | admin unit reference | ❌ |

DB **`tripplanner`** (cùng server) là của AI Chat / Trip Plan — xem §7.

> **Ràng buộc kiến trúc:** 3 API cần dữ liệu **không nằm trong `apps`** — `anchored-pois`, `nearby-pois`
> (cần geo; DB **không cài PostGIS**, chỉ `plpgsql`), và `summary.destinations[].name`. Hoặc Data chiếu
> vào `apps`, hoặc gọi HTTP sang service sở hữu. **Không đọc chéo schema.**

---

## 3. Reference implementation — `feed-service`

Routes `internal/router/rest/v1/feedtimeline/`, nhóm `/v1/timeline/pois`:

| Spec `/data/v1/...` | feed-service | Handler |
|---|---|---|
| 1 `POST /compact` | `POST /compact` | `FetchCompactPOIs` |
| 2 `GET /features` | `GET /features` | `GetFeaturedPOIs` |
| 3 `/{id}/gallery` | `/:poi_id/gallery` | `GetPOIGallery` |
| 4 `/{id}/summary` | `/:poi_id/summary` | `GetPOI` |
| 5 `/{id}/general-information` | `/:poi_id/general-information` | `GetPOIGeneralInformation` |
| 6 `/{id}/experiences` | `/:poi_id/experience` *(số ít)* | `GetPOIExperience` |
| 7 `/{id}/anchored-pois` | `/:poi_id/anchored-pois` | `GetAnchoredPOIsV2` |
| 8 `/{id}/nearby-pois` | `/:poi_id/nearby-pois` | `GetNearbyPOIs` |
| 9 `/{id}/reviews` | `/:poi_id/reviews` | `GetPOIReviews` |
| 10 `/{id}/amenities` | `/:poi_id/amenities` | `GetPOIAmenities` |
| 11 `/{id}/policies` | `/:poi_id/noticed-information` | `GetPOINoticedInformation` |
| 12 top pick | — | `GetTopPickPOIs` |
| 13 related POIs | — | `GetRelatedPOIs` |

**Không** thuộc phạm vi chuyển sang Data: `related-offers`, `related-blogs`, `related-destinations`,
`point-on-map`, `brand`.

**Nguồn dữ liệu:** `app.dbs.FeedDB` (`internal/infra/travelfeeddb`), model `cominfraTF.ItemPOI`
(repo `go-common`, package `cominfra/travelfeed`). Cột đọc ra đã đúng hình dạng response:
`id, name, short_description, ratings_count, ratings_avg_score, author, business_tags, status, address, geo_location`.

**Khảo sát thực tế mã nguồn `feed-service` (03/11/2026):**

| Tài sản / File | Vai trò trong code `feed-service` | Thực trạng khi chuyển sang Data |
|---|---|---|
| `asset/pois/general_information.json` | File template mẫu tĩnh | **Không dùng trong code**. Code đọc trực tiếp JSONB `item_pois.general_information`. |
| `asset/pois/noticed_information.json` | Dữ liệu policies mẫu | **Code bị comment out 100%**. Endpoint `/noticed-information` thực tế trả về `{"items": []}`. |
| `asset/pois/experience.json` | Dữ liệu mẫu tĩnh | **Không dùng**. Code đọc trực tiếp JSONB `item_pois.experiences`. |
| `asset/pois/experience_icon_mapping.json` | Map keyword sang icon key | **Đang hoạt động** trong `GetPOIExperience` (ví dụ: `shopping_n_retail` → `shopping_bag`). Cần chuyển bảng map này sang Java. |
| `asset/pois/policy_icon_mapping.json` | Map policy sang icon key | **Bị comment out cùng noticed_information** — hiện không dùng. |
| `internal/constant/anchored_pois.csv` | File CSV cũ | Đã được thay thế ở V2 bằng cách gọi HTTP sang `data-poi-management`. |
| `internal/wrapper/poimanagement/` | Client gọi `data-poi-management` | `GetAnchoredPOIsV2` gọi upstream này để lấy khoảng cách và id POI neo. |

> **Phát hiện dead code trong `feed-service`:**
> 1. `cover_id` (bigint) trong `item_pois` bị bỏ qua — code luôn query sang `item_medias` với `link_key = 'poi__cover'`.
> 2. `poi.POIContactInformation.Website` được gọi nhưng không có trong struct `ItemPOI` → `website_url` luôn rỗng `""`.
> 3. `nearby-pois` dùng PostGIS KNN `_ST_Expand` & `geog <-> o.g` và bắt buộc lọc cùng destination qua `item_links`.

---

## 4. Model đích — `apps.srv_poi_*`

5 bảng. Tất cả cột là `text` / `boolean` / `numeric` / `integer` / `timestamp` —
**không `jsonb`, không PostGIS**. Bảng nào cũng có `row_hash`, `created_at`, `updated_at`, `deleted_at`.

```
srv_poi_info          PK (poi_id)
  poi_id, poi_name, source_name, business_sector, business_category, subcategory_tags,
  destination_id, full_address, street, ward, district, city, country_code, postal_code,
  lat float8, lng float8, phone, email, website_url,
  operating_status, is_verified, is_recommended, is_bookable,
  operating_hours text/JSON, holiday_exceptions text/JSON,
  rating_overall numeric, rating_count int, review_count int

srv_poi_multi_lang    PK (poi_id, lang)
  poi_id, lang, source_name, time_to_spend, best_time, cost_vnd, description, experience text/JSON

srv_poi_media_gallery PK (media_id)
  media_id text(sha256), poi_id, source_name, photo_api_uri, display_order,
  width_px, height_px, photographer, blob_url, thumbnail_url, is_cover, is_active

srv_poi_amenity       PK (poi_id, business_sector, amenity_group, amenity_raw)
  poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_vi, service_flags

srv_poi_review        PK (review_id)
  review_id, poi_id, source_name, rating_overall, rating_count,
  title, review_text, rating, review_date text, author_name
```

### Độ phủ dữ liệu — **đo 02/11/2026, KHÔNG đổi so với 29/10**

| Bảng | Rows | Ghi chú |
|---|---|---|
| `srv_poi_info` | **24** | 100% `source_name=partner`. `lat/lng`, `rating_*`, `destination_id`, `subcategory_tags` = **NULL toàn bộ**. `operating_hours` chỉ 11/24 |
| `srv_poi_multi_lang` | **0** | |
| `srv_poi_media_gallery` | 1.131 (131 POI) | **396/1.131 có `blob_url`**, 735 còn ở `photo_api_uri` Google. `thumbnail_url` = 0 |
| `srv_poi_amenity` | 58 | |
| `srv_poi_review` | **0** | |

Đối chiếu legacy `public` **vẫn đang chạy và lớn lên**: `poi_master` 52.673 (29/10) → **56.040** (02/11);
`poi_review` 254.201 → **270.673**.

> **Đọc con số này cho đúng:** model mới đứng yên 4 ngày trong khi đường cũ nhận thêm 3.367 POI.
> Không thể integration-test thật trên `apps` ở thời điểm này.

---

## 5. GAP REGISTER

Trạng thái đo 02/11/2026. Không gap nào được đóng kể từ 29/10.

### 🔴 Chặn — không build được nếu không có nguồn

| ID | Gap | API ảnh hưởng | Owner | Trạng thái |
|---|---|---|---|---|
| **G1** | `srv_poi_media_gallery` **không có `blur_hash`, `mime_type`** (spec Required=Y) | 1,2,3,4,8,9 | Data | ❌ Mở — xác nhận lại 02/11 |
| **G2** | Không tồn tại `ref_business_category` → `business_sector_label` (Required=Y) không có nguồn | 1,2,4,8 | Data | ❌ Mở — **không có bảng `ref_*` nào trong DB** |
| **G3** | Không tồn tại `ref_amenity`; `amenity_raw` là key thô Google (`dineIn`, `parkingOptions.paidParkingLot`) và **có row chứa nguyên biểu thức SQL**: `json_type in ('bar','pub',...)` | 10 | Data | ❌ Mở |
| **G4** | **Không có nguồn policies nào** trong `apps`; legacy `poi_detail.poi_policy_json` phần lớn `{}` | 11 | BA + Data | ⚠️ Mở — Khảo sát `feed-service` cho thấy endpoint `/noticed-information` hiện cũng đang disabled và trả về rỗng `{"items": []}` |
| **G5** | Không có `is_anchor`/`anchor_type`; **không có PostGIS**. Khảo sát `feed-service` cho thấy `anchored-pois` v2 đang gọi sang `data-poi-management`, còn `nearby-pois` phụ thuộc PostGIS KNN và `item_links` | 7, 8 | Data | ❌ Mở — spec đã chốt hướng tách distance service riêng |
| **G6** | `holiday_exceptions` đúng khái niệm nhưng **sai format so với spec**: `date` lưu `21/07/2026` (DD/MM/YYYY) còn spec yêu cầu `YYYY-MM-DD`; giờ lồng trong mảng `hours:[{open_time,close_time}]` thay vì phẳng; có `status` thay cho `is_closed`; **thiếu** `is_open_all_day` và `is_closed`. Chỉ **1/24** POI có dữ liệu | 4, 5 | Data | ❌ Mở |
| **G15** | Dữ liệu chưa nạp: 24/56.040 POI, multi_lang 0, review 0 | tất cả | Data | ❌ Mở |
| **G16** | **Đổi định danh `poi_id`** (ĐÃ CHỐT 03/11: sinh mới hoàn toàn). Bắt buộc có bảng crosswalk `old_poi_id (+lang) → new_poi_id` từ Data | tất cả | Data | ⚠️ Đã chốt hướng — chờ Data cung cấp bảng crosswalk |

### 🟠 Thiếu field — phải sửa contract hoặc join thêm

| ID | Gap | API | Đề xuất |
|---|---|---|---|
| **G7** | `media_id` là `text` (sha256 64 ký tự), spec khai **Integer** | 1,2,3,4,8,9 | Sửa spec sang String |
| **G8** | Không có cột `operating_timezone` (Required=Y) | 2,4,5 | Hardcode `Asia/Ho_Chi_Minh` hoặc thêm cột |
| **G9** | `ratings` là **Array theo nguồn**, model chỉ có 1 bộ `(source_name, rating_overall, rating_count)`/POI | 1,2,4,8 | Trả array 1 phần tử, hoặc tách `srv_poi_rating` |
| **G10** | `destination_id` **text đơn**, không có tên; spec cần `destinations[]` có `id`+`name`. Thêm nữa: **chưa chốt ID space** (Strapi id vs UUID) và **chưa chốt cấu trúc quan hệ n-n** (thực tế 2,3 destination/POI, `poi_mgmt.poi_destination` có 107k liên kết, nhưng `apps.srv_poi_info` chỉ có 1 cột đơn `destination_id`) | 4 | Data + BE | Chốt model n-n (bảng `srv_poi_destination`) và chuẩn hoá ID space |
| **G11** | Không có `short_address` (#4), `content_language` (#4) | 4 | BE tự format |
| **G12** | `cost_vnd` (model) vs `cost` (spec); spec #5 còn gọi tên bảng Gold `gld_srv_poi_multi_lang` | 5 | Thống nhất tên |
| **G13** | `icon_key` của experiences chưa verify được (bảng 0 row). Legacy để trong `experiences[].keyword` | 6 | Xác nhận với Data |
| **G14** | Model review **mất** so với spec: `lang`, `is_verified`, `reviewer.user_id`, `reviewer.avatar`, `media[]`, `helpful_count`, `partner_reply`, `is_own_review`. Legacy `public.poi_review` **có** `lang`, `reviewer_name`, `media_urls_json`, `helpful_votes`, `response_text`, `responded_at` | 9 | Bổ sung lại vào Gold + chốt ranh giới Data/App BE |

### 🟡 Spec tự mâu thuẫn — cần BA chốt

| ID | Vấn đề |
|---|---|
| S1 | #1 sample trả `rating` (object) nhưng bảng field định nghĩa `ratings` (array) |
| S2 | #2 `limit` ghi "Min: 10, Max: 5"; status code lại nói "limit vượt 50" |
| S3 | #4 là summary **1 POI** nhưng sample response trả **mảng 3 POI** + `count` — copy nhầm từ #2 |
| S4 | #9 param chỉ khai `limit` ("tối đa 5") nhưng status code nhắc `offset`, `source`; sample request có cả `offset`, `lang`, `source` |
| S5 | #10 sample JSON thiếu `}` đóng; `amenity_code` viết HOA (`GIFT_SHOP`) còn dữ liệu thực là camelCase |
| S6 | #1 `cover` Required=N, #2 Required=Y — cùng một object |
| S7 | #9 dùng `X-User-ID` trong logic (`is_own_review`, `is_helpful_by_viewer`) nhưng **không khai báo** ở bảng header |

---

## 6. ⚠️ Contract đang lệch 3 nguồn — việc đầu tiên phải làm

Có **ba** định nghĩa cho cùng một màn hình, và chúng **không khớp nhau**:
(a) spec Confluence · (b) DTO đang chạy ở `feed-service/internal/router/rest/v1/feedtimeline/entity/poi.go`
· (c) model `apps.srv_poi_*`.

Ví dụ đã đối chiếu — **general-information** (#5):

| | feed-service đang chạy | Spec Confluence |
|---|---|---|
| Field | `opening_hour`, `time_to_spend`, `cost`, `best_time`, `operating_hours{label, value[]}` | `business_sector`, `time_to_spend`, `cost`, `best_time`, `operating_hours{label, timezone, value[]}`, `holiday_exceptions[]` |
| Mỗi ngày | chỉ `{label, value, subvalue}` — **không có field máy đọc được** | thêm `day_of_week`, `open_time`, `close_time`, `is_open_all_day`, `is_closed` |
| Lệch | có `opening_hour` mà spec không có | thêm `business_sector`, `timezone`, `holiday_exceptions` |

**policies / noticed-information (#11) — khác hoàn toàn:**

| feed-service | Spec |
|---|---|
| `{items:[{title, icon_key, icon_content, description, full_content}]}` | `{business_sector, sections:[{section_key, title, icon_tag, items[]}]}` |

**distance (#7, #8):** feed-service `POIDistanceResp{value, unit}` · spec `distance_meters` (Integer).

**address:** khớp nhau (`full_address, street, ward, district, city, country_code`), spec #4 thêm `short_address`.

> **Việc đầu tiên của bạn:** đối chiếu đủ 11 API giữa (a) và (b), lập bảng lệch, đưa BA chốt **một**
> contract. Nếu bỏ qua bước này, app sẽ nhận hai contract khác nhau cho cùng một màn.
> Shape POI chính (`ItemPOI`) nằm ở repo **`go-common`**, package `cominfra/travelfeed` — clone repo đó trước.

---

## 7. Blast radius của việc đổi `poi_id` (G16)

Model cũ **clone cả định danh theo ngôn ngữ**:

| Chỉ số (đo 02/11) | Giá trị |
|---|---|
| Dòng `public.poi_master` | 56.040 |
| `poi_id` phân biệt | 56.040 — **mỗi dòng một id** |
| `source_id` phân biệt (= địa điểm thật) | **20.538** |
| Trung bình `poi_id` / địa điểm | **2,73** |
| Địa điểm có đúng **3** `poi_id` *(đo 29/10, trên 19.417 địa điểm)* | **16.599** |

Ví dụ thật — cùng một quán, 3 id:
```
source_id = ChIJMVuhyJgndTER-CBqKox-DPw
  en  2da77db5-c232-4e05-134c-ea7e18b9f27f   Bun Dau Mam Tom - Lang Vong
  ko  abeb3152-7419-689b-831f-e4f758a715df   Bún Đậu Mắm Tôm - Làng Vòng
  vi  af4a7572-6dfe-123f-f3b2-a9b2f77f36e8   Bún Đậu Mắm Tôm - Làng Vòng
```

Model mới gộp về 1 `poi_id`/địa điểm. **Đây là thay đổi định danh, không phải thay đổi schema.**

**Hệ thống đang giữ `poi_id` (đã đo, không phải phỏng đoán):**

| Nơi | Cột | Số dòng |
|---|---|---|
| DB `tripplanner` — `trip_slot_pois` | `poi_id` text | **23.946** |
| DB `tripplanner` — `trip_acco_pois` | `poi_id` text | **1.412** |
| DB `tripplanner` — `trip_stops` | `poi_id` + snapshot `poi_name`, `poi_lat/lng`, `poi_rating`, `poi_category` | **19.656** |
| DB `tripplanner` — `trip_segments` | `accommodation_poi_id` | — |
| DB `tripplanner` — `messages` | `poi_ids` text[] (POI do AI Chat gợi ý) | — |
| `poi_mgmt.poi_destination` | `poi_id` | 107.492 dòng / 46.744 poi_id — nhưng chỉ **15.585 địa điểm thật** |

Thêm: `trip_stops` **denormalize snapshot POI** → đây là đường replicate **thứ hai**, ngoài bản sync
xuống app layer. Kế hoạch cutover phải tính cả nó.

**Đã chốt quyết định (03/11/2026):** `poi_id` trong model mới **sinh mới hoàn toàn** cho từng địa điểm, không tái sử dụng các ID cũ theo ngôn ngữ. Vì vậy, bắt buộc Data team phải publish bảng crosswalk `(old_poi_id, lang) → new_poi_id` để migrate toàn bộ các consumer (Trip Planner, AI Chat, Portal, Saved list).

---

## 8. Truy cập

| Thứ | Ở đâu |
|---|---|
| PAT Azure DevOps, credential DB DEV/STG/PROD, Event Hub, Blob SAS | `secret/info.md` — nằm ở **workspace root, ngoài repo này**; khoá PAT tên là `tocken`. Hỏi thanhtd05 nếu chưa có |
| DB DEV | `<host>` / `vv_data_serving` |
| Confluence spec | space `VV`, page `558497946` (index) + 11 page con `558497988`–`558498337` |
| ADO | `https://dev.azure.com/Sun-group/Sun-Visit-VN` |

> `secret/info.md` chứa credential thật của cả DEV/STG/PROD. **Không bao giờ commit file đó**, không
> dán vào ticket/chat. Hai script trong `scripts/` đọc credential từ biến môi trường, không hardcode —
> giữ nguyên cách đó nếu bạn sửa chúng.

---

## 9. Tái lập số liệu

```bash
export PGHOST=<host>
export PGDATABASE=vv_data_serving
export PGUSER=... PGPASSWORD=...        # lấy từ secret/info.md
uv run --with psycopg2-binary python docs/poi-serving-api/scripts/check-gaps.py
```

In ra: độ phủ `apps`, cột spec cần còn thiếu, mức độ nhân bản `poi_id`, blast radius `tripplanner`.
Chạy lại mỗi lần Data báo đã nạp thêm, để biết gap nào đã đóng.

Liệt kê repo ADO:

```bash
export AZDO_PAT=...        # PAT có scope "Code: Read", lấy từ secret/info.md
bash docs/poi-serving-api/scripts/list-repos.sh
```

---

## 10. Việc cần chốt — kèm người hỏi

| # | Câu hỏi | Hỏi ai | Chặn gì |
|---|---|---|---|
| 1 | **[ĐÃ CHỐT 03/11]** `poi_id` mới: **Sinh mới hoàn toàn**. Data team cần publish bảng crosswalk `old_poi_id (+lang) → new_poi_id` | Data | Cần có crosswalk trước khi cutover app / trip planner |
| 2 | **[CHƯA CHỐT]** Destination dùng ID space nào (Strapi ID hay UUID)? Chưa chốt vì **quan hệ POI ↔ Destination là n-n** (thực tế 2,3 destination/POI), cần chốt cả cách lưu n-n ở Data | Data + BE | G10, API 4 (summary), sửa portal |
| 3 | Chốt **một** contract cho 11 API (spec vs DTO feed-service) | BA | §6 — việc đầu tiên |
| 4 | Ranh giới API #9: phần nào Data trả, phần nào App BE trả? | BA + BE | G14 |
| 5 | Nguồn policies ở đâu — Partner Portal hay AI generate? | BA + Data | G4 |
| 6 | Data trả format hiển thị sẵn (`sections[].items`) hay App tự render? *(hôm nay feed-service render từ JSON tĩnh trong repo)* | BA | G4, #11 |
| 7 | Bao giờ `apps` nạp đủ dữ liệu? | Data | G15 — quyết định toàn bộ timeline |
| 8 | Bổ sung `blur_hash`/`mime_type`, `ref_business_category`, `ref_amenity` — được không, bao giờ? | Data | G1, G2, G3 |
| 9 | `holiday_exceptions`: chuẩn hoá `date` sang ISO + thêm `is_closed`/`is_open_all_day` — sửa ở Gold hay map ở serving? | Data | G6 |
| 10 | Xác nhận lập repo mới `data-serving-api`? | Kiến trúc | Phase 2 |
| 11 | Spec #12/#13 (top pick, related POIs) — có chuyển sang Data không? | BA | phạm vi |
| 12 | Ai sở hữu bảng map icon (`experience_icon_mapping.json`, `policy_icon_mapping.json`)? | BA + Data | #6, #11 |

---

## 11. Đề xuất 5 việc đầu tiên & Tiến độ hiện tại

1. **[HOÀN THÀNH] Clone `feed-service` và `go-common`** — Đã đọc `feedtimeline/poi.go`, `pois.go`, `entity/poi.go`, `asset/pois/*.json`, `cominfra/travelfeed`. Đã lập báo cáo chi tiết nguồn sự thật tại `feed-service-ground-truth.md`.
2. **Lập bảng đối chiếu contract đủ 11 API** (§6) → đưa BA chốt.
3. **Chạy `check-gaps.py`** để có số liệu của chính ngày bạn nhận việc — con số trong tài liệu này sẽ cũ đi.
4. **Đẩy câu hỏi #1 và #7 (§10) lên Data ngay** — hai cái này quyết định có làm được gì không, và thường mất thời gian chờ nhất.
5. **[HOÀN THÀNH] Dựng khung `data-serving-api` & implement API đầu tiên** — Đã khởi tạo repo `data-serving-api` (Java 26, Spring Boot 4.1.1), xây dựng DTO, generic `PageResponse`, `LanguageResolver`, `BusinessSectorDictionary`, `SubcategoryTagsParser`, `PoiSpecifications`, `GlobalExceptionHandler` (RFC 9457), hoàn thành endpoint `GET /api/v1/pois/compact` với 39/39 test pass và lưu trữ đặc tả OpenSpec `poi-compact-api`.

**Đừng làm trước khi có crosswalk `poi_id`:** bất cứ thứ gì ghi `poi_id` mới ra ngoài phạm vi Data.
