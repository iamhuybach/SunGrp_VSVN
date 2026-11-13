# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | destination_name chỉ DDL | slv_enr_poi_destination.destination_name hiện tại chỉ tạo DDL, chưa có nguồn đổ vào. | User, 2026-11-12 | 2026-11-12 |
| D-2 | keyword trong experience | Tôi confirm có keyword trong apps.srv_poi_multi_lang.experience. Nếu không có thì để null cho key keyword. | User, 2026-11-12 | 2026-11-12 |
| D-3 | review source_name | Lấy source_name trong gld_srv_poi_review fix cứng trong transform là 'google' vì lấy từ bảng thuộc luồng google. | User, 2026-11-12 | 2026-11-12 |
| D-4 | phần bỏ field | Các phần bỏ code thực hiện ngay trong task này. | User, 2026-11-12 | 2026-11-12 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-001 | P1 | fixed | Hint recovery của `NB_GLD_SRV_POI_INFO` trỏ `poidestpy` của `NB_CREATE_DDL`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- D-1, D-2, D-3, D-4 ở bảng trên. Nguyên văn câu người dùng ngày 2026-11-12.

## Lịch sử quyết định

- 2026-11-12: D-1. Không có notebook nạp `slv_enr_poi_destination.destination_name`. Cột thêm ở DDL, kiểu `STRING` nullable, cùng kiểu các cột chữ đã có trên bảng (`destination_id`, `city`, `street`). `gld_srv_poi_info.destination_name` và `apps.srv_poi_info.destination_name` vẫn copy 1-1 từ cột silver đó. Giá trị null cho tới khi có nguồn nạp sau này.
- 2026-11-12: D-2. `icon_key` lấy `keyword` trong JSON `experience` của hàng `apps.srv_poi_multi_lang` được chọn. Thiếu `keyword` thì `icon_key` null. Không thêm cột `keyword`.
- 2026-11-12: D-3. `NB_GLD_SRV_POI_REVIEW` gán `source_name` = literal `google`. Thêm `gld_srv_poi_review.source_name` và `apps.srv_poi_review.source_name`. Sửa dòng cấm trong `services/data-serving-service/AGENTS.md`.
- 2026-11-12: D-4. Trong task này bỏ `amenity_label_en` và `amenity_label_vi` khỏi response amenities, và bỏ `data.business_sector` khỏi practical_info. Giữ `amenity_en`, `amenity_vi`, và `data.business_tags.business_sector`.
- 2026-11-13: Người dùng xác nhận `gates.runtime` PASS theo bảng `Kết quả người dùng ghi nhận` của `runtime-runbook.md`.
- 2026-11-13: Cell `poidestpy` trên Fabric thêm đủ 3 cột. Query Postgres serving sau bước 4 không có `destination_name`. `srv_poi_review.source_name` đã có.
- 2026-11-13: Người dùng chạy lại ALTER. Query cột có `srv_poi_info.destination_name text` và `srv_poi_review.source_name text`. Database serving đủ cột để deploy API.
