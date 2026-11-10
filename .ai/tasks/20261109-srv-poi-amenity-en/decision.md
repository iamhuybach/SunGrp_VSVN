# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Cây JSON amenities | Chốt theo sample ở mục Quyết định của người dùng. `data[]` có `amenity_group` (string) và `items[]`. Mỗi item có `amenity_code`, `amenity_label_en`, `amenity_label_vi`, `service_flags`. | User 2026-11-09 | 2026-11-09 |
| D-02 | Path amenities | Chốt. Nguyên văn: Vẫn giữ /api/v1/pois/{poi_id}/amenities, không sửa. | User 2026-11-09 | 2026-11-09 |
| U-1 | Quy tắc snake_case của amenity | Chốt. Nguyên văn: chọn B: như A và tách camelCase (servesWine → serves_wine) và những kí tự như é trong Café chuyển thành e. | User 2026-11-09 | 2026-11-09 |
| U-2 | Nguồn JSON service_flags | Chốt. Nguyên văn: Lấy srv_poi_amenity.service_flags. | User 2026-11-09 | 2026-11-09 |
| U-3 | DROP ref_dictionary_amenities | Chốt. Nguyên văn: runbook có bước người dùng DROP ref_dictionary_amenities và chạy NB_SETUP_POI_AMENITY p_apply=true. | User 2026-11-09 | 2026-11-09 |
| R-9 | API local, chưa deploy | Chốt. Nguyên văn: Hãy chạy ở local trước, hiện tại tất cả các task API sẽ chưa deploy vội. P-7 chạy process Spring Boot trên máy, nối PostgreSQL Dev bằng biến môi trường `POSTGRES__DP_POI__*`. Không ghi secret vào repo hay task artifact. | User 2026-11-10 | 2026-11-10 |
| A-1 | Amenities không kiểm tra info | Chốt. Nguyên văn: bỏ bước kiểm tra info để amenities trả dữ liệu khi chỉ có dòng amenity. `getAmenities` không gọi `validatePoiExists`. Không có dòng amenity thì HTTP 200 và `data` rỗng. Gallery và review vẫn kiểm tra `srv_poi_info`. | User 2026-11-10 | 2026-11-10 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- A-1: `getAmenities` không gọi `validatePoiExists`. Architecture vòng 2 giữ bước này. Người dùng chốt ngày 2026-11-10.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-SQL-001 | P1 | fixed | `COND_SCHEMA` thêm `amenity_en string` ngay sau `amenity string`, đủ 10 trường với tuple điều kiện. | |
| API-002 | P1 | rejected-false-positive | D-01 chốt `data` là mảng không phân trang. Architecture vòng 2 giữ `List` và nói một POI dưới 100 dòng. Endpoint amenities đã là list trước task này. Thêm `PageResponse` đổi cây JSON đã chốt. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- D-01, nguyên văn người dùng: Đây là sample trả ra:

```json
{
  "success": true,
  "code": 200,
  "message": "POI amenities retrieved successfully",
  "data": [
    {
      "amenity_group": "facilities_and_services",
      "items": [
        {
          "amenity_code": "ma_mau",
          "amenity_label_en": "Nhan mau",
          "amenity_label_vi": "Amenity sample",
          "service_flags": "mau"
        },
        {
          "amenity_code": "ma_mau_2",
          "amenity_label_en": "Nhan mau 2",
          "amenity_label_vi": "Amenity sample 2",
          "service_flags": "mau 2"
        }
      ]
    },
    {
      "amenity_group": "accessibility",
      "items": [
        {
          "amenity_code": "ma_mau 3",
          "amenity_label_en": "Nhan mau 3",
          "amenity_label_vi": "Amenity sample 3",
          "service_flags": "mau 3"
        }
      ]
    }
  ],
  "meta": {
    "timestamp": "2026-11-09T04:28:00Z",
    "trace_id": "22222222-2222-2222-2222-222222222222"
  },
  "errors": null
}
```

- D-02, nguyên văn: Vẫn giữ /api/v1/pois/{poi_id}/amenities, không sửa.
- U-1, nguyên văn: chọn B: như A và tách camelCase (servesWine → serves_wine) và những kí tự như é trong Café chuyển thành e.
- U-2, nguyên văn: Lấy srv_poi_amenity.service_flags.
- U-3, nguyên văn: runbook có bước người dùng DROP ref_dictionary_amenities và chạy NB_SETUP_POI_AMENITY p_apply=true.

## Lịch sử quyết định

- 2026-11-09: Mở D-01 và D-02 từ request triage. Main không chọn cây JSON và không chọn POI mà endpoint mới trả về. `run-author` và `run-gate` chưa chạy.
- 2026-11-09: Người dùng chốt D-01 bằng sample JSON và D-02 bằng câu giữ path. Query `lang` vẫn bỏ theo acceptance criteria của request. Cột nguồn JSON vẫn theo request: `amenity_code` từ `amenity`, `amenity_label_en` từ `amenity_en`, `amenity_label_vi` từ `amenity_vi`, `service_flags` từ `amenity_vi`.
- 2026-11-09: `run-author --kind model` ghi `model-design.md`. `run-gate` trả `EVIDENCE_REQUIRED` (architecture round 1). Mở U-1, U-2, U-3. Không có probe Fabric. Main không chọn phương án Architect gợi ý. Thêm vào scope: `tests/test_poi_media_amenity_contract.py`, `PoiControllerIntegrationTest.java`, `docs/context/01_DATA_MODEL.md` (M-1).
- 2026-11-09: Người dùng chốt U-1, U-2, U-3. U-1 là phương án B cộng quy tắc dấu: ký tự như é trong Café thành e. Không còn probe. `gates.evidence` chuyển `not_required`.
- 2026-11-09: `run-author --kind model` ghi `model-design.new.md`. Main thay `model-design.md` bằng bản đó và xóa file `.new`. Vị trí cột `amenity_en` ngay sau `amenity` giữ theo Decision của architecture vòng 1.
- 2026-11-09: S-1: thêm `docs/context/api-mapping/amenities.md` vào scope và cập nhật theo D-01. Architecture vòng 2 PASS.
- 2026-11-10: A-1. Người dùng bỏ kiểm tra `srv_poi_info` ở amenities. Architecture vòng 2 giữ `validatePoiExists`. Review đã hết 2 vòng, nên lệch này ghi ở đây trước khi sửa code. Gallery và review không đổi.
