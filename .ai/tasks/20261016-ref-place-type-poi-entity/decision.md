# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| U1 | `business_category_vi` mục 1.7 | Mục 1.7 chốt business_category_vi = NULL. | Người dùng 2026-10-16; `architecture.md` §3 U1(a) | 2026-10-16 |
| U2 | Type Google trùng | (a) lần xuất hiện đầu trong file thắng | Người dùng 2026-10-16; `architecture.md` §3 U2 | 2026-10-16 |
| U3 | Ô Fast Food `shawarma_restaurant` | (a) sửa thành dấu phẩy trong file mapping | Người dùng 2026-10-16; `architecture.md` §3 U3 | 2026-10-16 |
| U4 | `created_at` / `updated_at` của L1 | Sau transform không lấy created_at và updated_at của slv_3p_poi | Người dùng 2026-10-16; `architecture.md` §3 U4(a) | 2026-10-16 |
| EDGE | Cạnh `slv_poi_entity` trước khi gắn job | SQL-001 confirm không xảy ra. STATE-001 confirm không xảy ra. Trước khi cầu hình job, kiểm tra bảng config xem bảng đang thuộc luồng nào. Nếu đã tồn tại và pipeline hiện tại chạy chu kỳ dài hơn, chuyển bảng sang pipeline chạy chu kỳ ngắn hơn. | Người dùng 2026-10-16 | 2026-10-16 |
| FNB | `business_sector` mục 1.2 | Có một chỗ đang sai format. Hiện tại là fnb, tôi muốn chuyển thành f_n_b | Người dùng 2026-10-16 | 2026-10-16 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Parser trong `tests/test_poi_entity_contract.py` giữ đúng lambda của `architecture.md` §7.1. Thêm `# noqa: B023` vì ruff chọn B023 và lambda được gọi ngay trong cùng vòng lặp.
- `architecture.md` §9 bước 8 chèn cạnh bằng `INSERT ... WHERE NOT EXISTS` và kiểm tra owner trước đường ghi. Review `SQL-001/STATE-001` bác đường đó: cạnh inactive hoặc lệch bị bỏ qua, kiểm tra owner có race. Seed từ điển vẫn `WHEN NOT MATCHED` only.
- `architecture.md` §7 map mục 1.2 thành `fnb`. Người dùng đổi thành `f_n_b`. Parser, `SEED_SECTORS` và mọi dòng seed F&B dùng `f_n_b`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-001/STATE-001 | P1 | fixed | Vòng 1: owner check và MERGE nằm trong `with_retry`, có hậu kiểm. | |
| SQL-001 | P1 | accepted-risk | SQL-001 confirm không xảy ra. Bản MERGE theo `pl_name` + `src_tbl` + `trg_tbl` giữ nguyên. | |
| STATE-001 | P1 | accepted-risk | STATE-001 confirm không xảy ra. Trước khi cầu hình job, tôi sẽ check trước trong bảng xem có bảng nào, ở luồng nào đang chạy nó rồi. Nếu đã tồn tại và có pl chạy thời gian dài hơn, khi đó sẽ move bảng về pl chạy thời gian ngắn hơn. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- U1: Mục 1.7 chốt business_category_vi = NULL.
- U2: (a) lần xuất hiện đầu trong file thắng.
- U3: (a) sửa thành dấu phẩy trong file mapping.
- U4: Sau transform không lấy created_at và updated_at của slv_3p_poi.
- SQL-001 confirm không xảy ra.
- STATE-001 confirm không xảy ra. Trước khi cầu hình job, tôi sẽ check trước trong bảng xem có bảng nào, ở luồng nào đang chạy nó rồi. Nếu đã tồn tại và có pl chạy thời gian dài hơn, khi đó sẽ move bảng về pl chạy thời gian ngắn hơn.
- Có một chỗ đang sai format. Hiện tại là fnb, tôi muốn chuyển thành f_n_b.

## Lịch sử quyết định

- 2026-10-16 — U1. Câu người dùng khóa `business_category_vi = NULL`. Trong `architecture.md` §3 chỉ phương án (a) cho NULL: `business_category` lấy ô Fabric Enum, mục 1.7 chỉ sinh dòng `google`. Phương án (b) điền tiếng Việt. Phương án (c) bỏ cả mục. Main ghi nhận U1(a).
- 2026-10-16 — U2(a). `national_park`, `hiking_area` giữ Nature Reserve. `church`, `hindu_temple`, `mosque`, `synagogue` giữ Religious Site / `attraction`.
- 2026-10-16 — U3(a). `docs/context/3p-google/mapping_place_type.md` vào scope. Một chỗ: `shawarma_restaurant. hamburger_restaurant` thành `shawarma_restaurant, hamburger_restaurant`.
- 2026-10-16 — U4(a). `created_at` và `updated_at` trên `slv_poi_entity` là vòng đời dòng entity do lib ghi. Không mang hai mốc của `slv_3p_poi`, không thêm `src_created_at` / `src_updated_at`.
- 2026-10-16 — Người dùng: SQL-001 confirm không xảy ra. STATE-001 confirm không xảy ra. Trước khi cấu hình job sẽ kiểm tra `ctrl_mng_pipeline_config`; nếu `slv_poi_entity` đã thuộc pipeline chu kỳ dài hơn thì chuyển sang pipeline chu kỳ ngắn hơn. Cả hai P1 là `accepted-risk`. Không thêm khoá chung. Bản MERGE đã sửa được giữ. `reviews/round-2.md` vẫn là `FIX_REQUIRED`; hết vòng review.
- 2026-10-16 — Người dùng yêu cầu sửa chính tả accommodation. `business_sector` trong seed đã là `accommodation`. Nhãn EN của `lodging` trong `mapping_place_type.md` và `SEED_ROWS` đổi từ `Accomodation` thành `Accommodation`. Header mục 1.1 đổi cùng chữ.
- 2026-10-16 — Người dùng: sector mục 1.2 đổi từ `fnb` sang `f_n_b`.
