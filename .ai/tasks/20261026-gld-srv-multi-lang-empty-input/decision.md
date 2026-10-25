# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | WARN nhịp `_30P` / `_15P` | WARN không phải nguyên nhân `PARTIAL_FAILED`. Hậu tố `P` không khớp `CADENCE_RE`; `build_dag` chỉ ghi log và bỏ kiểm tra nhịp. | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` L126, L270–L273, L596–L597; `docs/context/02_NAMING_CONVENTION.md` §3 | 2026-10-26 |
| D2 | `QualityGateError` đầu vào rỗng | Phân loại data. Version 2 vẫn là version hiện tại, 0 dòng, không có `row_hash` và `deleted_at`, nên `is_empty` không lọc dòng sống. Cửa chất lượng khớp snapshot rỗng. | `evidence/results/multi_lang_row_count.txt`; `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` L987–L992, L1581–L1583 | 2026-10-26 |
| D3 | Đổi hậu tố `15P`/`30P` | Task này không đổi `pl_name`. Đổi thành `15M`/`30M` không thêm dòng vào `slv_enr_poi_info_multi_lang`. Bật kiểm tra nhịp là task riêng: đổi tên pipeline, `p_pl_name` và `pl_name` trong ctrl cùng lúc. | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` L126–L127, L270–L273, L531–L533, L591–L599, L282–L283; `docs/context/02_NAMING_CONVENTION.md` §3 | 2026-10-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Chưa biết operation nào tạo version 2, và vì sao bảng có 0 dòng.
- Chưa đọc `ctrl_mng_pipeline_config`, nên chưa biết mọi `pl_name` chủ bảng mà `PL_VV_TRANS_SLV_TO_GLD_30P` đọc từ ngoài.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-26: Đóng task. Không thay đổi code. Lỗi khi `slv_enr_poi_info_multi_lang` không có dòng là hành vi đúng.

## Lịch sử quyết định

- 2026-10-26: Ghi D1 và D2 từ đối chiếu log với repo. Chưa sửa code.
- 2026-10-26: Probe `multi_lang_row_count` — version 2, 0 dòng, không có `row_hash`/`deleted_at`. D2 chuyển thành data. D3: không đổi hậu tố trong task này.
- 2026-10-26: Người dùng đóng task. Giữ nguyên notebook, pipeline và schema.
