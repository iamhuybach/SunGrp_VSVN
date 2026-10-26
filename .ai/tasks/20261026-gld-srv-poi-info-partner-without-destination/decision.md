# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-SRV-22 | Partner chưa có destination | Với source = partner, nếu poi_id chưa có trong slv_enr_poi_destination, lấy trực tiếp từ slv_poi_entity_non_enrich. Field nào mà slv_poi_entity_non_enrich không có thì để null. source = partner nghĩa là lower(trim(source_name)) = 'partner', cùng cách notebook đang so khớp. Chưa có nghĩa là không có dòng cùng poi_id. Dòng destination tồn tại nhưng cột null không thuộc nhánh này. Cột gold đang lấy từ destination, entity có cột cùng tên thì lấy 1-1 từ slv_poi_entity_non_enrich. Entity không có cột đó thì null. Không lấy từ bảng khác, không coalesce với destination. Partner đã có dòng destination: giữ mapping hiện tại. | request.md §Acceptance criteria | 2026-10-26 |

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

- Chưa có.

## Lịch sử quyết định

- 2026-10-26: Không có Main brief. D-SRV-22 ghi nguyên văn tiêu chí trong request.md trước khi sửa notebook. Danh sách cột không chốt trong request; notebook đối chiếu `OUT_COLS` của `NB_SLV_POI_ENTITY_NON_ENRICH`. Giá trị entity cast về `des.dtypes` để giữ kiểu cột gold đã có.
