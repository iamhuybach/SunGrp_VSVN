# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| U1 | Cột minh họa phải sửa cả hai notebook | A. Dùng `ctrl_mng_pipeline_config.nb_name` đã có trong repo. Không thêm cột mới. | architecture.md §17 | 2026-10-16 |
| U2 | Hai bảng silver trong notebook lần đầu | Thêm `slv_poi_amenity` và `slv_poi_entity` từ hai task `20261016-ref-amenities-poi-amenity` và `20261016-ref-place-type-poi-entity`. | User, 2026-10-16 | 2026-10-16 |
| U3 | Bằng chứng runtime | Chấp nhận rủi ro. R6 trên DEV `sgr_visitvn_dev` là bằng chứng runtime. R1–R5 không chạy vì không có môi trường trống. | User, 2026-10-17 | 2026-10-17 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | `init_plan` gọi `_target_dup_keys` trên từng bảng đích trước khi ghi. `init_verify` gọi lại và `ConfigError` nếu còn khoá trùng. Test `test_target_duplicate_keys_block_apply_and_verify`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-16: «A và thêm 2 bảng slv_poi_amenity và bảng slv_poi_entity ở 2 task mới đây».

## Lịch sử quyết định

- 2026-10-16 — U1 = phương án A. Cột minh họa là `ctrl_mng_pipeline_config.nb_name`. Verdict `EVIDENCE_REQUIRED` của vòng 1 không nêu probe; nó chặn để chờ U1. `evidence_required` trả về `false`.
- 2026-10-16 — U2. `slv_poi_amenity` đã nằm ở architecture §5.1 dòng 13, nguồn `notebooks/NB_SETUP_POI_AMENITY.ipynb`. `slv_poi_entity` chưa có trong inventory. Repo không có câu `CREATE TABLE` tĩnh cho bảng này trong `NB_SETUP_POI_ENTITY`; schema nằm ở `notebooks/NB_SLV_POI_ENTITY.ipynb` cell `b1entitybuild`. Vòng kiến trúc 2 phải gắn cả hai bảng, không chỉ E12–E14.
- 2026-10-16 — Vòng 2 PASS. U1 giữ cell `enrddlpy`, không sửa `NB_CREATE_DDL`. `slv_poi_entity` là bảng #14, cột suy từ `b1entitybuild`. `scope.files` bị dính chuỗi đã tách lại đúng danh sách ở E0.
- 2026-10-17 — GATE-001 fixed. Khoá trùng trên bảng đích chặn cả plan lẫn SUCCESS.
- 2026-10-17 — User: «Hiện tại không thể chạy true vì không có môi trường prod» và «Có những bảng thuộc model cũ. Kiểm tra các bảng thuộc model mới đủ là được». R6 pass. R1–R5 chưa có.
- 2026-10-17 — User: «accept-risk». U3 accepted-risk. Apply trên môi trường trống chưa được chứng minh trên Fabric.
