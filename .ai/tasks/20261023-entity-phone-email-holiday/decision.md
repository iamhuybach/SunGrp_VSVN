# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-PEH-01 | Cột silver | `phone`, `email`, `holiday_exceptions` là STRING, nullable, trên `slv_poi_entity_non_enrich`, đúng thứ tự đó, sau `opening_hours_text` và trước `row_hash`. Không thêm cột gold. | Lịch sử D-PEH-01 | 2026-10-23 |
| D-PEH-02 | Nguồn Google | Google: `phone` = `slv_3p_poi_contact.phone` của cùng `poi_id`, cùng khung join đang lấy `website_url`. `email` = null. `holiday_exceptions` = null. | Lịch sử D-PEH-02 | 2026-10-23 |
| D-PEH-03 | Nguồn partner | Partner: `phone` = `slv_pn_business_services.phone`. `email` = `slv_pn_business_services.email`. `holiday_exceptions` = `get_json_object(amentities, '$.policies.holiday_exceptions')` trên bản i18n `vi`, cùng dòng và cùng cách đang lấy `operating_hours` tại `$.policies.operating_hours`. Giữ nguyên chuỗi JSON, không parse thêm. | Lịch sử D-PEH-03 | 2026-10-23 |
| D-PEH-04 | Phần giờ giữ nguyên | Không đổi công thức `opening_hours_text`, không đổi cạnh giờ, không sửa cell `ohpasspy`. | Lịch sử D-PEH-04 | 2026-10-23 |
| D-PEH-05 | Nguồn khác và QG contact | Quality gate trùng `poi_id` của contact giữ nguyên. Nguồn khác `google` và `partner` để ba cột null, cùng kiểu nhánh giờ. | Lịch sử D-PEH-05 | 2026-10-23 |
| D-PEH-06 | Registry đã đủ | Registry đã có `slv_3p_poi_contact.phone`, `slv_pn_business_services.phone` và `slv_pn_business_services.email`, kiểu string. Notebook extract lấy cột từ registry. Không thêm cột extract và không cần probe. Ba bảng nguồn đã là input của entity. | Lịch sử D-PEH-06 | 2026-10-23 |
| D-PEH-07 | File test gold trong scope | `tests/test_enr_poi_contract.py` vào `scope.files`. `test_info_patch_cell_guards` đổi vị trí cell: `ids[-8:-2]` thành `ids[-10:-4]`, `ids[-2:]` thành `ids[-4:-2]`, và thêm `ids[-2:] == ["peholmd", "peholpy"]`. Không đổi assertion gold. | Lịch sử D-PEH-07 | 2026-10-23 |
| D-PEH-08 | Assert QG contact | `test_entity_detail_columns` kiểm tra identifier `dup_contact` trong `_google`. Không thêm string literal `"dup_contact"` và không sửa quality gate. | Lịch sử D-PEH-08 | 2026-10-23 |
| D-PEH-09 | Không chạy lại orchestrator | Người dùng chấp nhận risk ngày 2026-10-23: không chạy lại orchestrator vì hiện không có data mới. Không chạy R2–R11. `E_OH` = 2, `E_PEH` = 3. Workspace có `DETAIL_COLS`. `gates.runtime` giữ `pending`. | Lịch sử D-PEH-09 | 2026-10-23 |
| D-PEH-10 | Exec sau patch | `EXEC_1` = `525a64db-8c5a-46ab-acf2-2a68330bf384`, 2026-10-23T10:38:51Z–10:44:29Z. Entity `SUCCESS`, version 4, `updated` 64. Gold `SUCCESS`, version 8, `inserted` 64. Cạnh giờ là `NEW_EDGE`, đọc version 4. `gates.runtime` giữ `pending` đến khi có R2–R8. | Lịch sử D-PEH-10 | 2026-10-23 |
| D-PEH-11 | R1–R8 | R1–R8 của `EXEC_1` đạt ngày 2026-10-23. `E1` = 4. `v_hours` = 4, `v_i18n` = 6, `v_svc` = 6, `v_contact` = 5. Mọi số mismatch là 0. | Lịch sử D-PEH-11 | 2026-10-23 |
| D-PEH-12 | `peholpy` lần 2 | Dòng in lần 2 là `vừa thêm []`. History mới nhất vẫn là version 4, `MERGE`, 2026-10-23T10:42:17Z, `readVersion` 3. `numTargetRowsCopied` = 1, `numTargetRowsUpdated` = 64, `numSourceRows` = 65. Không có version 5. | Lịch sử D-PEH-12 | 2026-10-23 |
| D-PEH-13 | Cổng runtime | Verification 1–7 đạt. `gates.runtime` = `pass`. R10 và việc bật lại trigger thuộc task `20261023-entity-opening-hours-passthrough`, task đó giữ `waiting_runtime`. | Lịch sử D-PEH-13 | 2026-10-23 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- D-PEH-08: `### Test changes` yêu cầu `_google` chứa `"dup_contact"`. Quality gate hiện dùng biến `dup_contact`, không có string literal đó. Giữ gate, test assert identifier.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-23: chốt D-PEH-01 đến D-PEH-05 trong yêu cầu task. Runtime task `20261023-entity-opening-hours-passthrough` tạm dừng cho đến runbook của task này.
- 2026-10-23: chấp nhận risk, không chạy lại orchestrator vì hiện không có data mới.

## Lịch sử quyết định

### D-PEH-01

`phone`, `email`, `holiday_exceptions` là STRING, nullable, trên `slv_poi_entity_non_enrich`, đúng thứ tự đó, sau `opening_hours_text` và trước `row_hash`. Không thêm cột gold.

`row_hash` vẫn là cột kỹ thuật của lib. Ba cột mới là cột build, đứng sau `opening_hours_text`.

### D-PEH-02

Google: `phone` = `slv_3p_poi_contact.phone` của cùng `poi_id`, cùng khung join đang lấy `website_url`. `email` = null. `holiday_exceptions` = null.

Contact không có cột `email` trong registry. Null của Google là rule, không phải cột thiếu cần probe.

### D-PEH-03

Partner: `phone` = `slv_pn_business_services.phone`. `email` = `slv_pn_business_services.email`. `holiday_exceptions` = `get_json_object(amentities, '$.policies.holiday_exceptions')` trên bản i18n `vi`, cùng dòng và cùng cách đang lấy `operating_hours` tại `$.policies.operating_hours`. Giữ nguyên chuỗi JSON, không parse thêm.

### D-PEH-04

Không đổi công thức `opening_hours_text`, không đổi cạnh giờ, không sửa cell `ohpasspy`.

Diff chưa commit của `20261023-entity-opening-hours-passthrough` giữ nguyên. Task này sửa tiếp trên cây làm việc đó.

### D-PEH-05

Quality gate trùng `poi_id` của contact giữ nguyên. Nguồn khác `google` và `partner` để ba cột null, cùng kiểu nhánh giờ.

Nhánh giờ hiện là block check `opening_hours_other_source`. Ba cột dùng cùng kiểu chặn đó, không thêm builder cho nguồn khác.

### D-PEH-06

Registry đã có `slv_3p_poi_contact.phone`, `slv_pn_business_services.phone` và `slv_pn_business_services.email`, kiểu string. Notebook extract lấy cột từ registry. Không thêm cột extract và không cần probe. Ba bảng nguồn đã là input của entity.

`NB_SETUP_INITIAL_DDL` cell 4: `slv_pn_business_services` khóa `id`, `phone` path `phone` type `string`, `email` path `email` type `string`. Cell 5: `slv_3p_poi_contact` khóa `poi_id`, `phone` = `_str("nationalPhoneNumber")`. `NB_CREATE_DDL` cell 11 và cell 14 có cùng mapping. `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` và `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` gọi `load_table_specs` rồi chiếu `spec.columns`. `holiday_exceptions` không phải cột registry; nó là path trên `amentities` mà entity đã đọc.

### D-PEH-07

`tests/test_enr_poi_contract.py` vào `scope.files`. `test_info_patch_cell_guards` đổi vị trí cell: `ids[-8:-2]` thành `ids[-10:-4]`, `ids[-2:]` thành `ids[-4:-2]`, và thêm `ids[-2:] == ["peholmd", "peholpy"]`. Không đổi assertion gold.

Kiến trúc ghi đây là scope gap: cell mới đứng sau `ohpasspy` làm test vị trí cell của task giờ fail nếu không dịch hai vị trí. Chỉ sửa ba dòng assert vị trí. Assertion gold giữ nguyên.

### D-PEH-08

`test_entity_detail_columns` kiểm tra identifier `dup_contact` trong `_google`. Không thêm string literal `"dup_contact"` và không sửa quality gate.

`### Test changes` viết assert `"dup_contact"`. Trong cell, gate là biến `dup_contact` và câu `slv_3p_poi_contact: `. D-PEH-05 giữ nguyên gate đó. Test tìm `dup_contact` không kèm dấu nháy.

### D-PEH-09

Người dùng chấp nhận risk ngày 2026-10-23: không chạy lại orchestrator vì hiện không có data mới. Không chạy R2–R11. `E_OH` = 2, `E_PEH` = 3. Workspace có `DETAIL_COLS`. `gates.runtime` giữ `pending`.

History entity: version 2 `ADD COLUMNS` `opening_hours_text` lúc 2026-10-23T09:59:45Z, version 3 `ADD COLUMNS` `phone`, `email`, `holiday_exceptions` lúc 2026-10-23T10:00:30Z. Không có version 4, nên chưa có MERGE ghi giá trị. `ALTER` để cột NULL. Cổng runtime không được `pass` khi R2–R8 chưa chạy.

### D-PEH-10

`EXEC_1` = `525a64db-8c5a-46ab-acf2-2a68330bf384`, 2026-10-23T10:38:51Z–10:44:29Z. Entity `SUCCESS`, version 4, `updated` 64. Gold `SUCCESS`, version 8, `inserted` 64. Cạnh giờ là `NEW_EDGE`, đọc version 4. `gates.runtime` giữ `pending` đến khi có R2–R8.

Log notebook không có `qg_json`. Amenity `SUCCESS`, version 1, `updated` 0. Review `SUCCESS`, `inserted` 0. Ba dirty edge kia là `NEW_EDGE` của `slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination` và `slv_enr_poi_review_multi_lang`. `COUNTS_0` là 65 dòng live, entity cập nhật 64.

### D-PEH-11

R1–R8 của `EXEC_1` đạt ngày 2026-10-23. `E1` = 4. `v_hours` = 4, `v_i18n` = 6, `v_svc` = 6, `v_contact` = 5. Mọi số mismatch là 0. `gates.runtime` giữ `pending` đến khi chạy lại `peholpy` không tạo version mới.

Entity `updated` 64 trên 65 dòng live. R4 vẫn 65 dòng, `n = n_poi`. R5–R8 đều 0 nên dòng không cập nhật vẫn khớp nguồn. Warn `partner_opening_hours_null` = 13, bằng 24 dòng partner trừ 11 dòng có giờ. Gold `qg_json` không có `opening_hours_text_mismatch`. R8 `gold_ne_silver` = 0 và `gold_changed_vs_v0` = 0.

### D-PEH-12

Dòng in `peholpy` lần 2, ngày 2026-10-23:

`lh_vv_silver.dbo.slv_poi_entity_non_enrich: ['phone', 'email', 'holiday_exceptions'] string NULL sau opening_hours_text; vừa thêm []`

Khớp nhánh không `ALTER`. `DESCRIBE HISTORY LIMIT 3` sau lần chạy đó: version 4 `MERGE` lúc 2026-10-23T10:42:17Z, `readVersion` 3, `numTargetRowsCopied` 1, `numTargetRowsUpdated` 64, `numSourceRows` 65. Version 3 là `ADD COLUMNS` ba cột lúc 2026-10-23T10:00:30Z. Version 2 là `ADD COLUMNS` `opening_hours_text` lúc 2026-10-23T09:59:45Z. Không có version 5.

### D-PEH-13

Verification 1–7 đạt. `gates.runtime` = `pass`. R10 và việc bật lại trigger thuộc task `20261023-entity-opening-hours-passthrough`, task đó giữ `waiting_runtime`.

R1–R8 và R9 đủ mục kiểm tra của kiến trúc. Một dòng entity không đổi hash nên MERGE copy 1 dòng và update 64 dòng. R10 (orchestrator lần 2 và `ohpasspy` lần 2) nằm trong runbook chung để khép idempotency của task giờ. Task này không chờ R10.
