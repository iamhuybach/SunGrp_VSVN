# POI → Data Service: Thiết kế & Plan triển khai

**Ngày:** 2026-10-29
**Bối cảnh:** 2 thay đổi — (1) model POI mới từ phía Data, (2) chuyển từ replicate DB sang expose API data-service.
**Tài liệu kèm:** [API-GAPS.md](API-GAPS.md) — chi tiết 11 spec API + gap model.
**Tất cả số liệu dưới đây đo trực tiếp trên `vv_data_serving` @ <host>, ngày 29/10/2026.**

---

## A. Hiện trạng (đã verify trên code + DB)

### A.1 Luồng dữ liệu

```
data-collector ──► enrichment ──► [vv_data_serving . public]  ──(replicate/sync)──► app layer ──► FE/App
                                         │  52.673 POI
                                         │
                                         └──► data-poi-management (Java) ──► portal
                                                  đọc  public.poi_master / poi_detail / poi_enrichment_display
                                                  sở hữu  poi_mgmt  (ghi, Flyway, outbox→EventHub)
```

### A.2 Bản đồ repo — ai expose cái gì

| Repo | Vai trò | Prefix | Schema | Stack |
|------|---------|--------|--------|-------|
| **data-poi-management** | POI read + write cho portal | `/api/v1/pois` | đọc `public.*`, sở hữu `poi_mgmt` | Spring Boot, Java 26 |
| **data-destination-management** | Destination read-only | `/api/v1/destinations` | sở hữu `destination_mgmt` | Spring Boot, Java 26 |
| **partner-manager-service** | **BFF duy nhất** cho portal | `/v1/crm`, `/v1/master`, `/v1/internal-action`, `/v1/public/form` | — | Go, Gin |
| admin-portal | Portal UI | — | — | React/TS |
| data-collector · partner-integration-worker · data-poi-enrichment · access-control-service | ingest / auth | — | — | — |

Portal **không bao giờ** gọi thẳng service Java — luôn qua BFF. Gateway không có route cho các service Java.

### A.3 Cross-check: API app-serving đã tồn tại ở đâu?

> **Nguồn:** liệt kê đầy đủ repo của ADO project `Sun-Visit-VN` qua REST API (67 repo ngày 29/10/2026,
> 68 ngày 02/11), không chỉ 8 repo đã clone về máy.

**Trả lời: `feed-service` — đã implement đủ cả 11 API, đang chạy.**

Routes tại `internal/router/rest/v1/feedtimeline/`, nhóm `/v1/timeline/pois`:

| Spec `/data/v1/...` | feed-service `/v1/timeline/pois/...` | Handler |
|---|---|---|
| 1 `POST /compact` | `POST /compact` | `FetchCompactPOIs` |
| 2 `GET /features` | `GET /features` | `GetFeaturedPOIs` |
| 3 `GET /{id}/gallery` | `GET /:poi_id/gallery` | `GetPOIGallery` |
| 4 `GET /{id}/summary` | `GET /:poi_id/summary` | `GetPOI` |
| 5 `GET /{id}/general-information` | `GET /:poi_id/general-information` | `GetPOIGeneralInformation` |
| 6 `GET /{id}/experiences` | `GET /:poi_id/experience` *(số ít)* | `GetPOIExperience` |
| 7 `GET /{id}/anchored-pois` | `GET /:poi_id/anchored-pois` | `GetAnchoredPOIsV2` |
| 8 `GET /{id}/nearby-pois` | `GET /:poi_id/nearby-pois` | `GetNearbyPOIs` |
| 9 `GET /{id}/reviews` | `GET /:poi_id/reviews` | `GetPOIReviews` |
| 10 `GET /{id}/amenities` | `GET /:poi_id/amenities` | `GetPOIAmenities` |
| 11 `GET /{id}/policies` | `GET /:poi_id/noticed-information` | `GetPOINoticedInformation` |
| 12 top pick POIs | `GetTopPickPOIs` | có |
| 13 related POIs | `GetRelatedPOIs` | có |

Ngoài 11 cái trên, `feed-service` còn có `related-offers`, `related-blogs`, `related-destinations`,
`point-on-map`, `brand` — **không** nằm trong phạm vi chuyển sang Data.

**Nguồn dữ liệu hiện tại của feed-service:** `app.dbs.FeedDB` (`internal/infra/travelfeeddb`), model
`cominfraTF.ItemPOI` từ repo chung `go-common`. Cột đọc ra đã **đúng hình dạng response**:
`id, name, short_description, ratings_count, ratings_avg_score, author, business_tags, status, address, geo_location`.
→ Đây **chính là "layer application" nhận bản replicate từ `public`** mà hiện trạng mô tả.

**Khảo sát mã nguồn thực tế của `feed-service` (03/11/2026):**

| Tài sản / File | Vai trò trong code `feed-service` | Hệ quả khi chuyển sang Data |
|---|---|---|
| `asset/pois/general_information.json` | File template mẫu tĩnh | **Không dùng trong code**. Code đọc trực tiếp JSONB `item_pois.general_information`. |
| `asset/pois/noticed_information.json` | Dữ liệu policies mẫu | **Code bị comment out 100%**. Endpoint `/noticed-information` thực tế trả về `{"items": []}`. |
| `asset/pois/experience_icon_mapping.json` | map keyword → icon | **Đang hoạt động** trong `GetPOIExperience`. Đã xác nhận cần mang bảng map này sang Java. |
| `asset/pois/policy_icon_mapping.json` | map policy → icon | **Bị comment out** cùng `noticed_information`. |
| `internal/constant/anchored_pois.csv` | File CSV cũ | Đã được thay thế bằng gọi sang client `poimanagement` ở V2. |
| `internal/wrapper/poimanagement/` | client gọi `data-poi-management` | `GetAnchoredPOIsV2` gọi upstream này để lấy khoảng cách. |

> **Phát hiện thêm từ mã nguồn feed-service:**
> - `nearby-pois` đang dùng PostGIS KNN `_ST_Expand` & `geog <-> o.g` và bắt buộc lọc cùng destination qua `item_links`. Do DB `vv_data_serving` không có PostGIS, việc port API này cần dùng khoảng cách Haversine hoặc service khoảng cách riêng.
> - `cover_id` trong `item_pois` là dead code (luôn query `item_medias` với `link_key = 'poi__cover'`).
> - `website_url` luôn trả về `""` do struct thiếu trường liên hệ.

**Hai service Java (`data-poi-management`, `data-destination-management`) chỉ phục vụ portal** qua BFF
`partner-manager-service`; trong 11 API app chỉ trùng tên 2 cái (`anchored-pois`, `reviews`) nhưng khác
người dùng và khác contract.

> ⚠️ **Đính chính.** Bản trước của tài liệu này kết luận "11 API chưa có nơi host, 2/11 đã có endpoint".
> Kết luận đó dựa trên 8 repo clone sẵn và **sai**. Thực tế **11/11 đã chạy trong `feed-service`**.
> Mọi phần dưới đây đã được viết lại theo thực tế này.

---

## B. Hai thay đổi model — tác động định lượng

### B.1 Multi-language: hiện đang clone **cả POI**, kể cả `poi_id`

Đây là hạn chế nặng nhất, và nó **không chỉ là thừa dữ liệu**:

| Chỉ số | Giá trị |
|--------|---------|
| Số dòng `public.poi_master` | **52.673** |
| Số `poi_id` phân biệt | **52.673** (mỗi dòng 1 id) |
| Số `source_id` phân biệt (= số địa điểm thật) | **19.417** |
| Địa điểm có **3** `poi_id` khác nhau | **16.599** |
| Địa điểm có 2 / 1 | 58 / 2.760 |

Ví dụ thật — cùng một quán, 3 id:

```
source_id = ChIJMVuhyJgndTER-CBqKox-DPw
  en  2da77db5-c232-4e05-134c-ea7e18b9f27f  Bun Dau Mam Tom - Lang Vong
  ko  abeb3152-7419-689b-831f-e4f758a715df  Bún Đậu Mắm Tôm - Làng Vòng
  vi  af4a7572-6dfe-123f-f3b2-a9b2f77f36e8  Bún Đậu Mắm Tôm - Làng Vòng
```

Hệ quả đang diễn ra:
- App đổi ngôn ngữ → `poi_id` đổi → **mất deep link, mất "đã lưu", mất lịch sử xem**.
- Mọi phép đếm POI đang **phồng ~2,7×**.
- `poi_mgmt.poi_destination` chứa 46.744 `poi_id` nhưng thực chất chỉ **15.585 địa điểm**.
- Dedup, anchor, destination membership đều phải xử lý 3 bản của cùng một chỗ.

Model mới sửa đúng chỗ này: `apps.srv_poi_info` PK `(poi_id)` — một địa điểm một id — và
`apps.srv_poi_multi_lang` PK `(poi_id, lang)` chỉ giữ phần dịch được (`description`, `experience`,
`time_to_spend`, `best_time`, `cost_vnd`).

> ⚠️ **ĐÂY LÀ THAY ĐỔI ĐỊNH DANH (ĐÃ CHỐT: SINH MỚI HOÀN TOÀN).** 
> Quyết định chốt ngày 03/11/2026: `poi_id` trong model mới (`apps.srv_poi_*`) sẽ **sinh mới hoàn toàn** cho từng địa điểm, không tái sử dụng các ID cũ theo ngôn ngữ.
> Hệ quả: Mọi hệ thống đang giữ `old_poi_id` (saved list, trip plan 24k dòng, AI chat, blog card, deep link, `poi_destination` 107k dòng) sẽ trỏ vào ID không còn tồn tại nếu không migrate.
> → **Bắt buộc Data team phải publish bảng crosswalk `old_poi_id (+lang) → new_poi_id` cùng lúc với model `apps`.**

### B.2 n-n POI ↔ destination

| Nơi | Hình dạng hiện tại | Số liệu |
|-----|-------------------|---------|
| `public.poi_master.destination_ids` / `destination_names` | **text** chứa JSON array | 51.501 single · **chỉ 7 multi** |
| id space ở đây | Strapi id, vd `u9ufroalyr30hshlfwatuuo6` | |
| `poi_mgmt.poi_destination` (nguồn sự thật của resolver) | bảng n-n thật, có `membership`, `role`, `method`, `confidence`, `distance_m`, `reviewed_by` | **107.492 dòng · 46.744 POI · 203 destination · 2,30 destination/POI** |
| id space ở đây | **UUID** | |
| admin-portal | `destination_id` **đơn, read-only**; `destination_names` chỉ để hiển thị | `src/features/poi/data/schema.ts`, `poi-form-mapping.ts` |

Ba vấn đề chồng nhau:
1. **Hai id space khác nhau** (Strapi id vs UUID) cho cùng khái niệm destination → phải hợp nhất.
2. Dữ liệu phẳng `destination_ids` là **JSON không nhất quán** — ghi chú trong
   `admin-portal/src/features/poi/data/poi-json-text.ts` nói 16.915 dòng sai quote.
3. Portal **chưa cho sửa** quan hệ này; thực tế đã là n-n (2,3 destination/POI) nhưng UI chỉ thấy 1.

**Việc cần làm ở portal:** chuyển `destination_id` đơn read-only → **multi-select có thể sửa**, hiển thị
`membership`/`role`/`method`/`confidence`, cho phép thêm/xoá thủ công và **ghi đè quyết định của resolver**
(đã có sẵn cột `reviewed_by`, `reviewed_at`, `decision` trong `poi_destination`).

---

## C. Kiến trúc đích

```
                    ┌──────────────────────────────────────────┐
  App / FE  ───────►│  data-serving-api        /data/v1/*      │  ◄── MỚI
  AI Chat           │  read-only · sau APIM · cache · ratelimit│
  Trip Plan         └──────────────┬───────────────────────────┘
                                   │ đọc
                                   ▼
                      vv_data_serving . apps   (srv_poi_*, model mới)
                                   ▲
                                   │ Fabric Gold → serving
                    data-collector / enrichment / partner

  admin-portal ──► partner-manager-service (BFF) ──► data-poi-management   (poi_mgmt, write)
                                                 └─► data-destination-management (destination_mgmt)
```

### C.1 Quyết định: host 11 API ở đâu?

Vì `feed-service` **đã có cả 11 API**, bài toán không còn là "viết API mới" mà là
**đổi nguồn dữ liệu và chia lại trách nhiệm**.

Spec ghi rõ header `Authorization: Bearer token service-to-service **của BE**` — tức Data phục vụ BE,
không phục vụ thẳng app. Vậy mô hình đích:

```
App ──► feed-service  (giữ nguyên /v1/timeline/pois/*, public, user JWT)
             │  đổi nguồn:  FeedDB (replicate)  ──►  data-serving-api
             ▼
        data-serving-api   /data/v1/pois/*   (S2S, read-only)
             │
             ▼
        vv_data_serving . apps
```

| Phương án | Đánh giá |
|---|---|
| **A.** Data viết `/data/v1/*`; feed-service đổi nguồn, giữ endpoint public ✅ | Đúng với spec (S2S); app không đổi gì; cắt được replication; rollback dễ bằng feature flag |
| **B.** Data phục vụ thẳng app | Trái spec (S2S), phải gánh auth user, rate-limit đầu cuối, personalization |
| **C.** Giữ nguyên replication, chỉ đổi schema nguồn | Không giải quyết mục tiêu "service thay vì replicate" |

**Chọn A.** Hệ quả quan trọng: contract trong Confluence **phải được đối chiếu với DTO đang chạy**
ở `feedtimeline/entity/poi.go` trước khi chốt — nếu không sẽ có hai contract lệch nhau cho cùng một màn.
Đây là việc phải làm ngay ở Phase 0.

**Chia trách nhiệm cần chốt** (hiện tất cả đang nằm ở feed-service):

| Phần | Đề xuất |
|---|---|
| Dữ liệu POI thuần (tên, ảnh, địa chỉ, giờ, rating, amenity, review) | → **Data** |
| Nhãn/section hiển thị (`general_information.json`, `noticed_information.json`) | → **Data** (spec yêu cầu trả `label`, `sections`) |
| Icon mapping | → chốt: Data trả `icon_key`, feed-service map sang asset, **hoặc** Data trả luôn |
| POI neo (`anchored_pois.csv`) | → **Data** |
| Ghép offer / blog / destination liên quan, point-on-map, brand | → **giữ ở feed-service** |
| Personalization, timeline, fallback | → **giữ ở feed-service** |

### C.2 Chuẩn hoá contract — hiện đang lệch 3 kiểu

| Service | Query param | JSON body | Lỗi |
|---------|-------------|-----------|-----|
| data-poi-management | snake_case | snake_case | RFC 9457 `application/problem+json` |
| data-destination-management | snake_case | **camelCase** | Spring page envelope |
| **spec mới `/data/v1`** | snake_case | snake_case | envelope `{code, message, request_id, server_time, data}` |

→ Viết **ADR** chốt: `/data/v1/*` theo spec mới; hai service cũ giữ nguyên (không refactor gộp — phá portal).

### C.3 Nguyên tắc thiết kế

- **Read-only tuyệt đối.** Không Flyway. DDL của `apps` do pipeline Fabric sở hữu. User DB read-only.
- **Không business write.** Review của user, "hữu ích", partner reply → thuộc App BE, không phải Data.
- **Envelope + `ErrorCode` enum dùng chung**, một `@RestControllerAdvice`.
- **Cache theo nhóm:** `gallery`/`amenities` TTL dài; `summary`/`general-information`/`experiences` TTL ngắn; `features`/`nearby` TTL rất ngắn.
- **`anchored-pois` + `nearby-pois`** gọi distance service riêng (spec đã chốt hướng này; DB **không có PostGIS**).
- **Versioned từ đầu:** `/data/v1`. Thay đổi định danh POI sau này đi vào `/data/v2`, không sửa v1.

---

## D. Plan triển khai

### Phase 0 — Chốt nền tảng *(trước khi viết dòng code nào)*

| Việc | Đầu ra | Owner | Trạng thái |
|------|--------|-------|------------|
| Chốt `poi_id` mới: giữ id cũ hay sinh mới? | Quyết định bằng văn bản | Data + BE | ✅ **Đã chốt (03/11)**: Sinh mới hoàn toàn |
| Bảng crosswalk `old_poi_id(+lang) → new_poi_id` | Bảng trong `apps`, publish cùng model | Data | ⚠️ Bắt buộc Data publish kèm model |
| Hợp nhất id space destination (Strapi id vs UUID) | Quyết định + mapping | Data + BE | ⏳ Chưa chốt (do quan hệ n-n) |
| Ranh giới API 9 (reviews): Data vs App BE | Quyết định phân chia | BA + BE | ✅ **Đã chốt (03/11)**: Data trả thô, BE enrich tương tác. [OUT_OF_DATE 2026-11-06, D-10] `srv_poi_review` không có `source`/`source_name`/`lang`. |
| Trả lời các câu hỏi trong [API-GAPS.md](API-GAPS.md#7-câu-hỏi-cần-chốt-trước-khi-code) | Spec chốt phiên bản | BA + Data | Đang chốt dần |
| ADR contract `/data/v1` | File ADR trong repo mới | Kiến trúc | Đang hoàn thiện |

**Gate 0:** không có crosswalk → **không bắt đầu Phase 2**. Đây là điều kiện cứng.

### Phase 1 — Dữ liệu model mới đủ dùng *(song song Phase 0, team Data)*

- Nạp đủ 52.673 POI vào `apps.srv_poi_*` (hiện **24**, toàn partner).
- Nạp `srv_poi_multi_lang` (hiện **0 dòng**) và `srv_poi_review` (hiện **0 dòng**).
- Chuẩn hoá `holiday_exceptions`: `date` đang là DD/MM/YYYY (spec cần `YYYY-MM-DD`), giờ lồng trong
  `hours[]`, dùng `status` thay `is_closed`, thiếu `is_open_all_day`.
- Bổ sung `blur_hash`, `mime_type` vào `srv_poi_media_gallery`; hoàn tất `blob_url` (hiện 396/1.131).
- Tạo `ref_business_category`, `ref_amenity`; làm sạch `amenity_raw` (đang lọt cả biểu thức SQL).
- Bổ sung lại các field review đã mất: `lang`, `media`, `helpful_count`, `partner_reply`.

**Gate 1:** script kiểm độ phủ chạy xanh — mỗi API có ≥95% field bắt buộc có dữ liệu trên tập mẫu 1.000 POI.

### Phase 2 — Khung service `data-serving-api` *(Đã triển khai)*

- Khởi tạo repo `data-serving-api` (Java 26, Spring Boot 4.1.1).
- Xây dựng Exception Handling theo RFC 9457 ProblemDetail (`GlobalExceptionHandler`).
- Đa ngôn ngữ: `LanguageResolver` xử lý ưu tiên `lang` query param > `Accept-Language` header > fallback `vi`.
- Cấu trúc phân trang chuẩn `PageResponse<T>`.
- Khung DTO, dynamic specifications (`PoiSpecifications`), repository batch querying.
- OpenAPI 3.0 documentation & annotations.
- Toàn bộ test suite tự động 39/39 passed.

**Gate 2:** Đạt — khung service hoạt động ổn định và test tự động xanh 100%.

### Phase 3 — API theo wave (chi tiết thứ tự ở tài liệu prep)

| Wave | API | Trạng thái / Phụ thuộc |
|------|-----|------------------------|
| **3b (Khởi động)** | **1 compact (`GET /api/v1/pois/compact`)** | **✅ Đã hoàn thành**: DTO hierarchical (cover, rating, business_tags, address, geo), filter IDs, pagination, sort, language fallback |
| **3a** | **3 gallery (`GET /api/v1/pois/{poi_id}/gallery`)** | **✅ Đã hoàn thành**: Quản lý thư viện ảnh, order by display_order, 404 validation |
| **3a** | **10 amenities (`GET /api/v1/pois/{poi_id}/amenities`)** | **✅ Đã hoàn thành**: Gom nhóm tiện ích theo amenity_group, nhãn tiếng Việt, 404 validation |
| **3e** | **9 reviews (`GET /api/v1/pois/{poi_id}/reviews`)** | **✅ Đã hoàn thành**: Phân trang, lọc theo lang, ranh giới Data trả thô chuẩn |
| 3b (còn lại) | 4 summary | `ref_business_category`, timezone, lat/lng, rating |
| 3c | 5 general-information · 6 experiences | `srv_poi_multi_lang` có dữ liệu |
| 3d | 2 featured | logic pick pool + quota sector từ feed-service |
| 3f | 7 anchored · 8 nearby | distance service / Haversine (do DB không có PostGIS) |
| 3g | 11 policies | chốt nguồn dữ liệu (hiện feed-service đang trả `[]`) |

**Gate 3 (mỗi wave):** parity test đạt ngưỡng (mục E.2) + contract test 100% + review.

### Phase 4 — Portal: n-n POI ↔ destination

1. `data-poi-management`: endpoint đọc/ghi `poi_destination` (list theo POI, add, remove, override resolver).
2. BFF: proxy route tương ứng dưới `/v1/crm/pois/:poi_id/destinations`.
3. `admin-portal`: thay `destination_id` đơn read-only bằng multi-select sửa được; hiển thị
   `membership`/`role`/`method`/`confidence`; nút ghi đè resolver (ghi `reviewed_by`, `reviewed_at`).
4. Dọn `destination_ids`/`destination_names` phẳng khỏi đường đọc của portal.

**Gate 4:** QC trên DEV theo checklist portal; 0 regression trên màn POI list/detail.

### Phase 5 — Cutover: bỏ replication

1. **Dual-run:** app layer vẫn chạy bản replicate, đồng thời gọi API mới sau cờ feature. So sánh log.
2. **Shadow traffic:** gọi song song, diff response, không hiển thị.
3. **Chuyển dần theo màn:** gallery → amenities → summary → detail đầy đủ.
4. **Freeze replication** sau 2 tuần ổn định; giữ bản sao read-only 1 tháng để rollback.
5. Gỡ pipeline sync.

**Gate 5:** p95 latency đạt SLA; tỉ lệ lỗi < ngưỡng; diff shadow < 0,1% trong 7 ngày liên tục.

---

## E. Đảm bảo chất lượng

### E.1 Contract test (bắt buộc, chặn merge)
Sinh OpenAPI từ spec Confluence → validate **mọi** response thật khớp schema, kể cả nhánh lỗi
(400/401/403/404/429/500/503). Spec hiện có **6 mâu thuẫn nội tại** (xem prep §4) — contract test sẽ
ép chốt chúng thay vì để lọt xuống runtime.

### E.2 Parity test — đòn bẩy chất lượng lớn nhất
Lấy **tập vàng 1.000 POI** phủ đủ 4 `business_sector` × 3 ngôn ngữ × có/không partner.
Với từng POI: dựng response từ **đường cũ** (replicate từ `public`) và từ **API mới** (trên `apps`), rồi diff.

| Loại lệch | Ngưỡng chấp nhận |
|-----------|------------------|
| Field bắt buộc thiếu | **0** |
| Sai giá trị (name, address, geo, rating) | **0** |
| Thiếu dữ liệu do model mới chưa nạp | báo cáo, không chặn Phase 3 |
| Khác format có chủ đích (vd `media_id` text) | whitelist có tài liệu |

Chạy lại mỗi wave; là **điều kiện vào Phase 5**.

### E.3 Test định danh (riêng cho thay đổi `poi_id`)
Với mỗi `(old_poi_id, lang)`: crosswalk phải trả đúng 1 `new_poi_id`; 3 id cũ của cùng `source_id` phải
hội tụ về **cùng một** id mới. Kiểm trên toàn bộ 52.673 dòng, không lấy mẫu.

### E.4 Các lớp còn lại
- **Integration:** Testcontainers + seed từ dump `apps` thật (không fixture tay).
- **Load:** theo traffic thật của POI detail; đo p95/p99 từng endpoint; kiểm cache hit.
- **Observability:** log `request_id` xuyên suốt; metric theo endpoint + caller; alert theo tỉ lệ lỗi.
- **Review:** mỗi PR cần design-QA như quy trình module destination đang áp dụng.

---

## F. Rủi ro

| # | Rủi ro | Mức | Giảm thiểu |
|---|--------|-----|-----------|
| R1 | `poi_id` đổi làm hỏng saved list / trip plan / deep link của user thật | **Cao** | Crosswalk + dual-read + `/data/v1` giữ nguyên, đổi định danh đi v2 |
| R2 | Model mới chưa đủ dữ liệu (24/52.673 POI, 0 multi_lang, 0 review) | **Cao** | Gate 1 chặn; Phase 3 không khởi động trước khi đạt |
| R3 | Spec còn 6 mâu thuẫn + 6 gap chặn (policies không có nguồn) | Trung bình | Phase 0 chốt; API 11 đẩy xuống wave cuối |
| R4 | Hai id space destination không hợp nhất được | Trung bình | Quyết định ở Phase 0 trước khi sửa portal |
| R5 | Bỏ replication sớm khi API chưa ổn định | **Cao** | Dual-run + shadow 2 tuần, giữ bản sao 1 tháng |
| R6 | Traffic app làm nghẽn portal nếu host chung service | Trung bình | Chọn phương án B — tách deployable |
| R7 | Ba convention contract khác nhau gây lẫn cho client | Thấp | ADR + không refactor service cũ |

---

## C.4 `data-serving-api` query vào DB nào — và ranh giới sở hữu

**DB:** `vv_data_serving` (DEV: `<host>`), **schema `apps`** — và
**chỉ** `apps`. Prod tương ứng: `<host>`.

Các schema cùng nằm trong `vv_data_serving` và **ai sở hữu**:

| Schema | Chủ sở hữu | `data-serving-api` được đọc? |
|--------|-----------|------------------------------|
| `apps` (`srv_poi_*`) | pipeline Fabric Gold | ✅ **nguồn duy nhất** |
| `public` (`poi_master`, `poi_detail`, …) | serving legacy | ❌ chính là thứ đang bị thay thế |
| `poi_mgmt` | `data-poi-management` | ❌ vi phạm sở hữu service |
| `destination_mgmt` | `data-destination-management` | ❌ vi phạm sở hữu service |
| `admin_ref` | admin unit reference | ❌ |

> **Ràng buộc thiết kế quan trọng.** 3 API cần dữ liệu **không nằm trong `apps`**:
> - API 7 `anchored-pois` → hiện chỉ có ở `poi_mgmt.anchored_pois` (39 dòng) / `public.anchor_poi_map` (0 dòng)
> - API 8 `nearby-pois` → cần geo; DB **không cài PostGIS** (chỉ `plpgsql`)
> - API 4 `summary.destinations[].name` → tên destination chỉ có ở `destination_mgmt.destination`
>
> Hai cách hợp lệ: **(a)** pipeline Data chiếu các dữ liệu này vào `apps`, hoặc **(b)** gọi HTTP sang
> service sở hữu. **Không** đọc chéo schema — làm vậy là khoá cứng `data-serving-api` vào vòng đời
> migration của portal, đúng thứ kiến trúc này đang muốn gỡ bỏ.

### C.5 Người tiêu thụ `poi_id` đã đo được — blast radius của B.1

Cùng server DEV còn DB **`tripplanner`** (AI Chat + Trip Plan, 21 bảng). Nó **giữ `poi_id`** ở 5 chỗ:

| Bảng / cột | Kiểu | Số dòng |
|------------|------|---------|
| `trip_slot_pois.poi_id` | text | **22.868** |
| `trip_acco_pois.poi_id` | text | **1.288** |
| `trip_stops.poi_id` | varchar | — (kèm snapshot `poi_name`, `poi_lat/lng`, `poi_rating`, `poi_category`…) |
| `trip_segments.accommodation_poi_id` | varchar | — |
| `messages.poi_ids` | text[] | — (POI do AI Chat gợi ý trong hội thoại) |

Hai điều rút ra:
1. **R1 không còn là giả định** — đổi `poi_id` sẽ làm hỏng trip plan và lịch sử hội thoại AI đã lưu.
   Crosswalk phải phủ cả `tripplanner`, không chỉ POI domain.
2. `trip_stops` đang **denormalize snapshot POI** (tên, toạ độ, rating) — tức là một dạng replicate
   thứ hai, ngoài bản sync xuống app layer. Phase 5 phải tính cả đường này.

---

## G. Việc cần chốt ngay (chặn Phase 0)

1. **[ĐÃ CHỐT 03/11/2026]** `poi_id` trong model mới: **Sinh mới hoàn toàn**. Yêu cầu bắt buộc Data team cung cấp bảng crosswalk `old_poi_id (+lang) → new_poi_id`.
2. **[CHƯA CHỐT — ĐANG MỞ]** Destination dùng **id space nào** làm chuẩn — Strapi id hay UUID? Hiện **chưa chốt vì quan hệ POI ↔ Destination là n-n** (thực tế 2,3 destination/POI, `poi_mgmt.poi_destination` có 107k liên kết), trong khi `apps.srv_poi_info` chỉ có cột đơn `destination_id`. Cần team Data và BE chốt cấu trúc model n-n (bổ sung bảng `srv_poi_destination` hoặc mảng JSON) kèm ID space tương thích.
3. **[ĐÃ CHỐT]** Lập repo mới `data-serving-api` (đã khởi tạo và đang chạy với endpoint đầu tiên).
4. **[ĐÃ CHỐT 03/11/2026]** Ranh giới API 9 (reviews): Data (`data-serving-api`) chỉ trả dữ liệu review thô/ingested (`review_id`, `source`, `author_name`, `rating`, `review_text`, `review_date`, `lang`). Data **không nhận `X-User-ID`** và không gánh các logic tương tác động (`helpful_count`, `is_own_review`, `is_helpful_by_viewer`, `partner_reply`, `avatar`) — các tính năng này thuộc trách nhiệm của App BE (`feed-service`). [OUT_OF_DATE 2026-11-06, D-10] Danh sách trường trên đã cũ: `srv_poi_review` theo gold không có `source`, `source_name`, `lang`.
5. API 11 (policies): nguồn dữ liệu ở đâu — Partner Portal hay AI generate? (Lưu ý: hiện `feed-service` đang disabled và trả rỗng).
6. Timeline team Data cho Phase 1 — quyết định được lịch của toàn bộ Phase 3.
