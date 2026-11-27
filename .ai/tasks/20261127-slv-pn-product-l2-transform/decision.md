# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| C-01 | Phân loại trước gate | Signal `data_model_change`, `idempotency`, `stateful_logic`. `architecture_required` = true. `evidence_required` = false. `runtime_required` = false. Complexity medium. Risk medium. Reviewer: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`. | user 2026-11-27; WORKFLOW.md §5 và §7 | 2026-11-27 |
| C-02 | `updated_at` khi `deleted_at` đổi | Field Mapping L2 thắng §5.2 trên ba bảng này: `updated_at` đổi khi `row_hash` đổi hoặc khi `deleted_at` đổi giữa NULL và khác NULL. | mapping_slv_pn_product_l2.md Field Mapping | 2026-11-27 |
| C-03 | Tên notebook node | §2: một notebook một bảng đích, tên `NB_<UPPER(trg_tbl)>`: `NB_SLV_PN_PRODUCT_SALE`, `NB_SLV_PN_HOTEL_ROOM_OFFER`, `NB_SLV_PN_HOTEL_RATE_OFFER`. | 02_NAMING_CONVENTION.md §2 | 2026-11-27 |
| C-04 | Tiền tố `slv_pn_` trên L2 | Giữ đúng tên Q-19. Không đổi tên bảng. Task này không sửa §1. | mapping_slv_pn_product_l2.md dòng mở đầu; Q-19 | 2026-11-27 |
| C-05 | Kiểu `deleted_at` | Cột đích là `timestamp`. Ô Data Type `boolean` trên dòng Field Mapping là kiểu cờ `deleted` nguồn, không phải kiểu cột L2. | mapping_slv_pn_product_l2.md dòng cột kỹ thuật; 02_NAMING_CONVENTION.md §5.2 | 2026-11-27 |
| C-06 | Giải mã giá | Làm đúng `mapping_slv_pn_product_l2.md` §1.3. Không mở file legacy ngoài tóm tắt đó. NULL giữ NULL. Không ghi 0. | mapping_slv_pn_product_l2.md §1.3; Q-15 | 2026-11-27 |
| C-07 | Tên cờ trong SQL | Cờ build là `_is_deleted`. `is_identifier` từ chối tiền tố `_`, nên không nới `IDENT_RE`. `sql_merge_target` chỉ nội suy khi tên khớp `_[A-Za-z][A-Za-z0-9_]*`. Cờ kèm `soft_delete_set` khác rỗng thì `ConfigError`, cùng quy tắc với cột chủ và `APPEND`. | architecture.md Lib design; skill vsvn-notebook-library | 2026-11-27 |
| Q-19 | Ba bảng Silver L2 | Đồng ý tách theo khuyến nghị: `slv_pn_product_sale`, `slv_pn_hotel_room_offer`, `slv_pn_hotel_rate_offer`. `valid_from` và `valid_to` chỉ chuyển 1-1. Không suy cờ bán từ hai cột vì code cũ không dùng chúng. | user 2026-11-27 | 2026-11-27 |
| Q-20 | Phân loại trước gate kiến trúc | Thêm signal `data_model_change`. `architecture_required` = true. `gates.architecture` = pending. Ba bảng Q-19 thêm grain và khoá. Kiểu JSON nằm ở Q-24. Chat này không sửa notebook, DDL, pipeline. | user 2026-11-27 | 2026-11-27 |
| Q-21 | `deleted_at` của ba bảng L2 | A. Dòng L2 vẫn có cho mọi id đang nằm trên L1. Ghi `deleted_at` khi L1 `deleted = true` hoặc id không còn. Lần tính sau, nếu nguồn về `deleted = false`, `deleted_at` trở lại NULL. | user 2026-11-27 | 2026-11-27 |
| Q-22 | `is_bookable` của `slv_pn_product_sale` | A. Không có variant `status = active` và `deleted = false` thì `false`. `status` và `deleted` của product không đi vào cờ này. | user 2026-11-27 | 2026-11-27 |
| Q-23 | Cột trong `row_hash` | A. Gồm khoá và các cột nghiệp vụ phía trên dòng hash, đúng thứ tự Field Mapping. Công thức `sha2(to_json(struct(...)), 256)`. `row_hash`, `created_at`, `updated_at`, `deleted_at` ở ngoài struct. | user 2026-11-27 | 2026-11-27 |
| Q-24 | Kiểu `holiday_product_post_id` | Giá trị JSON là chuỗi. 41/41 lớp `string`. So sánh chuỗi với `external_id` của post `deleted = false`: 41/41 khớp đúng một post. Không có post, hoặc nhiều hơn một post, thì `product_post_id` và ba giá vẫn NULL. | evidence/results/holiday_product_post_id_type.txt | 2026-11-27 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có lệch so với Edit list. Runbook đổi thứ tự: R1 chạy trước khi quan sát NB_00. `notebook.run` từ notebook tạm cần `useRootDefaultLakehouse`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-002 | P1 | fixed | Mọi `deleted_flag` khác None đều là cờ đang bật. `reject_deleted_flag` chạy trước `add_row_hash`, `diff_counts`, `ensure_target` và `merge_target`. Chuỗi rỗng raise `ConfigError` và test chứng minh hai lời gọi ghi không chạy. Chưa có vòng review thứ ba. | |
| SPARK-001 | P1 | fixed | Fabric DEV 2026-11-27: R1 PASS, R2 0/0/0 và version giữ 1, R3 mọi count 0, cột đúng, `_is_deleted` không có, K3 `n = 0`. `evidence/results/r2_r3.txt`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-27: Tạo task này, signal `data_model_change`, `architecture_required` true, rồi chạy model và các gate trong cùng chat. Không sửa task `20261127-slv-pn-product-business-mapping`. Không chạy analysis hay proposal.
- 2026-11-27: Duyệt vòng review thứ ba. `review_plan.extra_round_approved_on` = 2026-11-27.
- 2026-11-27: Duyệt vòng review thứ tư. `review_plan.second_extra_round_approved_on` = 2026-11-27.

## Lịch sử quyết định

- 2026-11-27: C-01 ghi phân loại trước gate model và kiến trúc. Thêm `idempotency` và `stateful_logic` vì `deleted_at` giữ timestamp của lần tính đầu thấy xoá, và lần chạy sau phải đưa về NULL khi L1 `deleted = false`. Risk medium vì nhánh MERGE mới mặc định tắt, node cũ không đổi hành vi.
- 2026-11-27: Q-19 đến Q-24 chép nguyên văn từ `## Quyết định hiện hành` của task `20261127-slv-pn-product-business-mapping`. Q-20 nói chat mapping không sửa notebook; chat này là task hiện thực.
- 2026-11-27: C-02 ghi Field Mapping thắng dòng `updated_at` của `02_NAMING_CONVENTION.md` §5.2 trên ba bảng L2.
- 2026-11-27: C-03 áp §2 cho câu hỏi 1 của mapping L2 (notebook chưa có tên trong mapping). Không có dòng registry trong ledger. Architecture phải nêu rõ nếu cần `TABLE_SPECS` hoặc `ctrl`; nếu có pipeline thì thêm `fabric-pipeline-reviewer` trước review.
- 2026-11-27: Model `model-design.md` không thiếu evidence. C-04, C-05, C-06 chốt các xung đột 3, 7, 8 của model. Xung đột 2 đã nằm ở C-02. Xung đột 4 giữ nguyên: copy 1-1, không gán đơn vị `EPOCH_S_TS`. Xung đột 1, 5, 6, 9 để Architecture xử lý từ nguồn đã chốt hoặc trả `USER_DECISION`. Không bịa dòng registry, tên cột cờ, nullability, hay biểu thức JSON.
- 2026-11-27: Architecture PASS. Đăng ký bằng 5 cạnh `RECOMPUTE` trên `PL_VV_TRANS_SLV_TO_GLD_30M`, không `TABLE_SPECS` và không dòng registry. Cờ build tên `_is_deleted`. C-07 ghi kiểm tra tên trước khi nội suy vì `is_identifier` từ chối tiền tố `_`. Caller `%run` giữ nguyên: `deleted_flag` mặc định `None`.
- 2026-11-27: Review vòng 1 `FIX_REQUIRED`. STATE-002: kiểm tra tên cờ trước `ensure_target`. SPARK-001: `runtime_required` = true. Probe R3 đọc-only đã có. R1/R2 do người dùng chạy theo runbook.
- 2026-11-27: Review vòng 2 vẫn `FIX_REQUIRED`. STATE-002: `""` không còn bị coi là cờ tắt. SPARK-001 giữ mở vì chưa có kết quả Fabric DEV. Hết 2 vòng review.
- 2026-11-27: Người dùng gửi R2 và R3. Ba node `p_force=true` ra 0/0/0, version giữ 1. R3 mọi count 0. K3 mismatch 0. SPARK-001 ghi `fixed`. Chưa quan sát một lần GLD30/ENR15 sau khi import lib.
- 2026-11-27: Người dùng duyệt vòng review thứ ba.
- 2026-11-27: Review vòng 3 `EVIDENCE_REQUIRED`. `STATE-002` được xác nhận fixed. `SPARK-001` còn vì `r2_r3.txt` chưa dẫn R1. Bản tóm tắt R1 từ output đã gửi được ghi vào `evidence/results/pnl2_selftest.txt`. Không chạy lại R1.
- 2026-11-27: Người dùng duyệt vòng review thứ tư.
- 2026-11-27: Người dùng chuyển task sang `ready_to_merge` và yêu cầu commit rồi push `main`.
- 2026-11-27: Review vòng 4 `PASS`. `SPARK-001` đóng. `gates.evidence` chuyển `pass` vì vòng 4 nhận `pnl2_selftest.txt`. Runtime đã `pass` từ R1–R3. Status do runner đặt là `waiting_runtime`.
