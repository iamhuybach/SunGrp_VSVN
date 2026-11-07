# Nguồn sự thật (Ground Truth) về hành vi POI APIs: Phân tích mã nguồn `feed-service` & `go-common`

> [!IMPORTANT]
> Phân tích này được trích xuất trực tiếp từ mã nguồn thực tế đang chạy tại:
> - `feed-service/internal/router/rest/v1/feedtimeline/poi.go`, `pois.go`, `entity/*`
> - `feed-service/gocommon/cominfra/travelfeed/*`
> - `feed-service/asset/pois/*`

---

## 1. Phát hiện then chốt (Executive Summary)

Trái với các giả định ban đầu khi đọc tài liệu thiết kế và asset JSON, việc đọc code Go thực tế đã làm sáng tỏ:

1. **Asset JSON phần lớn là "chết" hoặc template mẫu:**
   - `asset/pois/noticed_information.json` và `asset/pois/policy_icon_mapping.json`: **Bị comment out 100%** trong handler. Endpoint `/pois/:id/noticed-information` thực tế đang trả về `{"items": []}`.
   - `asset/pois/general_information.json`: Không hề được đọc trong code; code đọc trực tiếp JSONB `item_pois.general_information`.
   - `asset/pois/experience.json`: Dữ liệu mẫu tĩnh; code đọc trực tiếp JSONB `item_pois.experiences`.
   - **Duy nhất `asset/pois/experience_icon_mapping.json` đang hoạt động**: Dùng map `keyword` (ví dụ `shopping_n_retail`) sang icon key (`shopping_bag`).

2. **Các Dead Code & Trap trong Model Go:**
   - Cột `poi.CoverID` (bigint) tồn tại trong bảng `item_pois` nhưng **bị bỏ qua hoàn toàn** — code luôn query sang bảng `item_medias` với điều kiện `link_key = 'poi__cover'`.
   - `poi.POIContactInformation` được gọi trong `GetPOI` (`poi.POIContactInformation.Website`) nhưng struct `ItemPOI` **không có trường này** -> `website_url` luôn trả về `""`.
   - Cột `ingestion_source` được query bằng SQL thô (`GetFeaturedPOIs`) nhưng không được map vào struct Go.

3. **Phụ thuộc ngoại vi đặc biệt:**
   - **`anchored-pois` (V2):** Không tự tính toán, mà gọi HTTP sang `POIManagementAPI.GetAnchoredPOIs(poi_id)` (upstream `data-poi-management`). Feed-service chỉ lấy thêm `id, name`.
   - **`nearby-pois`:** Dùng **PostGIS KNN** (`ST_SetSRID`, `ST_MakePoint`, `geog <-> o.g`, `_ST_Expand`) và filter theo destination link. DB `vv_data_serving` hiện **không có extension PostGIS**!
   - **`brand`:** Gọi gRPC sang `PartnerIntegrationService.GetBusinessServiceById(poi.SourceID, locale)`.

---

## 2. Chi tiết Model & Bảng cơ sở dữ liệu (`FeedDB`)

### 2.1 Bảng chính: `item_pois` (Model `ItemPOI`)

```go
type ItemPOI struct {
    ID                uuid.UUID              `gorm:"primaryKey;column:id"`
    SourceID          string                 `gorm:"column:source_id"`      // Unique key cùng với language
    SourceName        string                 `gorm:"column:source_name"`    // Ví dụ "partner_portal"
    Name              string                 `gorm:"column:name"`
    ShortDescription  string                 `gorm:"column:short_description"`
    Address           Address                `gorm:"column:address;type:json"`
    GeoLocation       Location               `gorm:"column:geo_location;type:json"`
    RatingsCount      int                    `gorm:"column:ratings_count"`
    RatingsAvgScore   float32                `gorm:"column:ratings_avg_score"`
    RatingsRank       string                 `gorm:"column:ratings_rank"`
    IsActive          bool                   `gorm:"column:is_active"`
    CoverID           int64                  `gorm:"column:cover_id"`       // Denormalized nhưng KHÔNG dùng
    Author            Author                 `gorm:"column:author;type:json"`
    Amenities         map[string][]string    `gorm:"column:amenities;type:json"`
    BusinessTags      BusinessTags           `gorm:"column:business_tags;type:json"`
    Status            POIStatus              `gorm:"column:status;type:json"`
    Language          string                 `gorm:"column:language"`       // "vi", "en", "ko"
    GeneralInformation POIGeneralInformation `gorm:"column:general_information;type:jsonb"`
    Experiences       []POIExperience        `gorm:"column:experiences;type:jsonb"`
    DestinationIDs    []uuid.UUID            `gorm:"column:destination_ids;type:json"`
}
```

### 2.2 Các cấu trúc con quan trọng

* **`POIGeneralInformation` (JSONB):**
  * `TimeToSpend`, `BestTime`, `Cost`: Dạng map đa ngôn ngữ `map[string]string` (`{"vi": "...", "en": "..."}`).
  * `OpeningHours`: Chứa `Timezone`, `Is247`, danh sách `Periods []POIOpeningPeriod` (`DayOfWeek`, `OpenHour`, `OpenMinute`, `CloseHour`, `CloseMinute`), và `HolidayExceptionsJSON`.
* **`POIExperience` (JSONB):**
  * `Title`, `Description`, `Keyword` (keyword dùng để tra icon).
* **`BusinessTags` (JSON):**
  * `BusinessSector`, `BusinessCategory`, `SubcategoryTags []string`.
* **Bảng phụ trợ:**
  * `item_medias`: Lưu trữ ảnh với `link_key` (`poi__cover`, `poi__gallery`, `poi__point_on_map`), `blur_hash`, `cdn_url`, `rank`.
  * `item_reviews`: Lưu đánh giá (`linked_item_key = poi_id`, `source`, `lang`, `reviewer_name`, `rating`, `review_text`, `review_date`).
  * `item_links`: Bảng n-n liên kết giữa POI, Destination và Blog (`linked_from_id`, `linked_from_type`, `linked_to_id`, `linked_to_type`).

---

## 3. Hành vi thực tế của từng API (Deep-Dive)

### 3.1 Middleware xử lý ngôn ngữ & POI Validation (`ValidatePOI`)
* Nhận `id` từ URL path.
* Query `item_pois` theo `id`. Nếu `!is_active` -> trả **404 Not Found**.
* **Đa ngôn ngữ:** Nếu `poi.Language != app_lang`, thực hiện query tìm lại POI:
  ```sql
  SELECT * FROM item_pois WHERE source_id = ? AND language = ? AND is_active = true
  ```
  Nếu tìm thấy bản ghi theo ngôn ngữ mong muốn -> hoán đổi struct POI trong context. Nếu không -> fallback giữ POI gốc.

---

### 3.2 `POST /pois/compact`
* **Input:** Body `{"ids": ["uuid-1", "uuid-2"]}` (1 đến 20 items).
* **Query POI:** 
  ```sql
  SELECT id, name, short_description, ratings_count, ratings_avg_score,
         author, business_tags, status, address, geo_location
  FROM item_pois WHERE id IN (?)
  ```
* **Cover lookup:**
  ```sql
  SELECT * FROM item_medias 
  WHERE linked_item_key IN (?) AND link_key = 'poi__cover' 
    AND blur_hash != PLACEHOLDER
  ```
  Lấy cover đầu tiên (newest-first), resolve CDN URL qua `FileService`.
* **Output:** Giữ nguyên các trường rút gọn: `id`, `name`, `description` (từ `short_description`), `cover`, `rating`, `business_tags`, `address`, `geo_location`.

---

### 3.3 `GET /pois/features` (Featured POIs)
* **Thuật toán phức tạp 4 bước:**
  1. **Pool Query:** Lọc các POI `is_active = true`, đúng `language`, thuộc các sector được cấu hình (`FeaturedPOISectors`), thoả mãn một trong các điều kiện:
     * `(status->>'is_recommended')::boolean = true`
     * Hoặc `ingestion_source = 'partner_portal'`
     * Hoặc `ratings_avg_score >= 4.0` và `ratings_count >= 10`.
  2. **Pick Algorithm:** Dùng PCG Random Generator, xáo trộn và phân bổ đều theo từng sector (đảm bảo ít nhất 1 recommended, 1 partner portal và có độ phủ sector, mỗi sector không vượt quá quota).
  3. **Cover Check Loop:** Kiểm tra POI được pick có cover hợp lệ (`blur_hash != PLACEHOLDER`) hay không. Nếu không có cover thật -> loại khỏi pick và pick bù từ pool.
  4. **Batch Fetch:** Gọi 3 goroutines song song để lấy thông tin chi tiết và trả về.

---

### 3.4 `GET /pois/:id/summary`
* **Cover:** Lấy từ `item_medias` với `link_key = 'poi__cover'`.
* **Destinations:** Query bảng `item_links` với `linked_to_type = DESTINATION`, sau đó lấy tên destination theo ngôn ngữ từ `item_destinations`.
* **Trạng thái hoạt động động (Dynamic Open/Close):**
  * Nếu có `GeneralInformation.OpeningHours`, trường `is_active` được tính toán lại theo thời gian thực (check giờ hiện tại so với `Periods` và timezone).
* **Website URL:** Luôn là `""` do lỗi struct thiếu `POIContactInformation`.

---

### 3.5 `GET /pois/:id/general-information`
* Trích xuất trực tiếp từ `poi.GeneralInformation` (JSONB).
* **Giờ hoạt động 7 ngày (`operating_hours`):**
  * Chỉ hiển thị cho 3 nhóm ngành: `attraction`, `shopping_n_retail`, `vehicle_rental`.
  * Hỗ trợ format nhãn theo 3 ngôn ngữ: `vi`, `en`, `ko`.
  * Có trường `subvalue` tự động hiển thị "Đang mở" / "Open now" / "현재 영업 중" cho ngày hiện tại.

---

### 3.6 `GET /pois/:id/experience`
* Đọc danh sách `poi.Experiences` (JSONB).
* Với mỗi phần tử, lấy `item.Keyword` tra vào `asset/pois/experience_icon_mapping.json`:
  * Map `event` -> `curtains`
  * Map `shopping_n_retail` -> `shopping_bag`
  * Map `spa_n_wellness` -> `bath_soak`
  * Map `tour_n_activities` -> `hiking`
  * Map `vehicle_rental` -> `car_rental`, v.v.
* Đọc file SVG nội bộ và trả về `icon_content`.

---

### 3.7 `GET /pois/:id/noticed-information` (Policies)
* **Code hiện tại bị vô hiệu hóa hoàn toàn:**
  ```go
  // Handler trả thẳng mảng rỗng
  c.JSON(http.StatusOK, gin.H{"items": []interface{}{}})
  ```
* File `noticed_information.json` và `policy_icon_mapping.json` không còn được sử dụng.

---

### 3.8 `GET /pois/:id/amenities`
* Trả về nguyên gốc `poi.Amenities` (dạng `map[string][]string`), ví dụ:
  ```json
  {
    "has_wifi": ["true"],
    "fnb_dine_in": ["true"]
  }
  ```
* Không qua bất kỳ bước chuẩn hóa hay mapping từ vựng nào.

---

### 3.9 `GET /pois/:id/reviews`
* Phân trang query từ bảng `item_reviews`:
  ```sql
  SELECT * FROM item_reviews 
  WHERE linked_item_key = ? AND linked_item_type = 1 
    AND lang = ?
  ORDER BY review_date DESC LIMIT ? OFFSET ?
  ```
* Format ngày: `YYYY-MM-DD`.

---

### 3.10 `GET /pois/:id/nearby-pois`
* Dùng **PostGIS spatial index** (`p.geog && _ST_Expand(o.g, radius_m)`).
* Tính khoảng cách bằng công thức cầu `trunc((p.geog <-> o.g) * (6371000/6371008.771415))`.
* Chỉ gợi ý các POI có cùng Destination (thông qua điều kiện `EXISTS` trong `item_links`).
* Sort đa tầng: Khoảng cách tăng dần -> Điểm đánh giá giảm dần -> Số lượng đánh giá -> Cùng danh mục -> Cùng lĩnh vực.

---

### 3.11 `GET /pois/:id/anchored-pois`
* Code V2 gọi sang client `poimanagement.Client`:
  ```go
  resp, err := h.poiManagementClient.GetAnchoredPOIs(ctx, poiID)
  ```
* Chỉ query lại `item_pois` để lấy `id` và `name`. Khoảng cách lấy nguyên văn từ kết quả của `data-poi-management`.

---

## 4. Tác động trực tiếp đến `data-serving-api` (Java)

| API | Trạng thái ở feed-service | Chiến lược cho `data-serving-api` |
|---|---|---|
| **1. Compact POIs** | Đang chạy chuẩn | Giữ nguyên logic batch query + cover selection |
| **2. Features** | Thuật toán random + cover check phức tạp | Cần port logic phân bổ quota sector & cover filtering |
| **3. Gallery** | Query `item_medias` theo rank | Đọc `srv_poi_media_gallery` theo `display_order` |
| **4. Summary** | Ghép POI + Destination + Dynamic open | Cần bổ sung bảng/service destination mapping |
| **5. General Information** | Đọc JSONB + tính Open Now | Đọc JSONB `srv_poi_info` + time calculation theo timezone |
| **6. Experiences** | JSONB + tra `experience_icon_mapping.json` | Đưa bảng mapping icon vào Java code (`Map<String, String>`) |
| **7. Anchored POIs** | Đang gọi upstream `data-poi-management` | Cần quyết định: gọi HTTP sang service đó hay Fabric Gold sync sẵn bảng `srv_poi_anchor` |
| **8. Nearby POIs** | Phụ thuộc PostGIS KNN | **RỦI RO LỚN:** DB `vv_data_serving` không có PostGIS -> Cần distance service riêng hoặc tính Haversine code-level |
| **9. Reviews** | Đọc bảng `item_reviews` | Cần dữ liệu `srv_poi_review` từ pipeline Data |
| **10. Amenities** | Trả nguyên JSON map | Trả JSON từ `srv_poi_info.amenities` |
| **11. Policies** | **Đang bị tắt (empty array)** | Chốt với BA: tiếp tục để trống hay cần nguồn mới từ Gold/Partner |
