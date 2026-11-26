# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-OLD-ADDR | old_address | Lấy house_number, street, full_address chứ không phải old_house_number, old_street, old_full_address | Quyết định của người dùng | 2026-11-26 |
| D-E0 | scope.files | Thêm ba path trên vào scope.files. | Câu hỏi E0 | 2026-11-26 |
| D-I2 | I2 touched | Chấp nhận kết quả. touched bằng updated_rows, không bằng live_rows, vì cột mới null không đổi row_hash. | Kết quả người dùng ghi nhận | 2026-11-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- `test_info_price_rule` bỏ qua comment khi kiểm tra token `source_name` trong `_price`. Comment trong cell giữ nguyên câu kiến trúc.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

Lấy house_number, street, full_address chứ không phải old_house_number, old_street, old_full_address

Cách áp dụng, cùng luật coalesce và bỏ nhóm của `full_address` (`docs/context/mapping_gld_srv_poi_info.md` §1.6). Có dòng destination: nhóm 1 = `house_number` + `street` + `old_formatted_address`; nhóm 2 = `house_number` + `street` + `old_ward_with_type` + `old_city_with_type`; nhóm 3 = `slv_enr_poi_destination.full_address`. Nối bằng `, `. `house_number` và `street` giữ cột entity hiện tại. `formatted_address`, `ward_with_type`, `city_with_type` dùng cột `old_` đã có. Không có dòng destination thì `old_address` là null, vì request cấm lấy `full_address` của entity làm `old_address`.

### Câu hỏi E0 — thêm ba file test vào scope

Kiến trúc PASS. Bước đầu của edit list là dừng để xin phép. Cell mới ở cuối `NB_CREATE_DDL` làm lệch assert 10 cell id cuối trong ba file ngoài `scope.files`:

- `tests/test_enr_extract_contract.py` dòng 242
- `tests/test_enr_poi_contract.py` dòng 223
- `tests/test_poi_entity_contract.py` dòng 635

Mỗi file chỉ sửa một dòng prefix trim, theo mục Test edits. Không sửa logic test khác.

Chọn một:

1. Thêm ba path vào `scope.files`. Main implement E1–E33, gồm prefix trim ở ba file đó.
2. Không thêm. Main dừng. Verify không thể PASS vì cell mới phá ba assert đó.

Đã trả lời ngày 2026-11-26: thêm ba path vào `scope.files`.

### Câu hỏi old_address

`full_address` khi có dòng destination (`docs/context/mapping_gld_srv_poi_info.md` §1.6, `NB_GLD_SRV_POI_INFO` cell `srvinfobuild`) là coalesce ba nhóm, nối bằng `, `. Field null, hoặc `house_number` hay `street` chỉ còn khoảng trắng sau trim, thì bỏ cả nhóm. Không có dòng destination thì lấy `slv_poi_entity_non_enrich.full_address`.

`house_number` và `street` trong công thức đang lấy từ `slv_poi_entity_non_enrich`. `formatted_address`, `ward_with_type`, `city_with_type`, `full_address` lấy từ `slv_enr_poi_destination`.

Quy tắc đã giao: thay từng field bằng cột cùng tên có tiền tố `old_` khi DDL đã có cột đó. Không bịa cột.

`TABLE_SPECS` của `slv_enr_poi_destination` trong `NB_SETUP_INITIAL_DDL` có: `old_ward`, `old_ward_with_type`, `old_district`, `old_district_with_type`, `old_city`, `old_city_with_type`, `old_formatted_address`. Không có `house_number`, `street`, `old_house_number`, `old_street`, `old_full_address`. `slv_poi_entity_non_enrich` không có cột `old_*` cho địa chỉ. Repo không có tên `old_house_number`, `old_street`, `old_full_address`.

Cột thiếu để map đủ ba nhóm:

- Nhóm 1 (`house_number` + `street` + `formatted_address`): thiếu `old_house_number`, `old_street`. Có `old_formatted_address`.
- Nhóm 2 (`house_number` + `street` + `ward_with_type` + `city_with_type`): thiếu `old_house_number`, `old_street`. Có `old_ward_with_type`, `old_city_with_type`.
- Nhóm 3 (`slv_enr_poi_destination.full_address`): thiếu `old_full_address`.
- Nhánh không có dòng destination (`slv_poi_entity_non_enrich.full_address`): thiếu `old_full_address` trên entity.

Cột `old_*` có trong DDL nhưng không nằm trong ba nhóm: `old_ward`, `old_district`, `old_district_with_type`, `old_city`.

Chọn một:

1. Ghép chỉ từ cột `old_` đã có trong đúng field của ba nhóm. Bỏ field không có bản `old_`. Có dòng destination: coalesce nhóm 1 = `old_formatted_address`, nhóm 2 = `old_ward_with_type` + `old_city_with_type` nối bằng `, `, nhóm 3 bỏ. Field còn lại null hoặc chỉ khoảng trắng sau trim thì bỏ nhóm đó. Không có dòng destination thì null. Main ghi lựa chọn này vào dòng `D-OLD-ADDR` rồi chạy `run-author --kind model`.
2. `old_address` = `slv_enr_poi_destination.old_formatted_address` khi có dòng destination, null khi không có. Không ghép ward hay city. Main ghi lựa chọn này vào dòng `D-OLD-ADDR` rồi chạy `run-author --kind model`.
3. Công thức khác, chỉ từ cột đã có trên `slv_enr_poi_destination` (`old_ward`, `old_ward_with_type`, `old_district`, `old_district_with_type`, `old_city`, `old_city_with_type`, `old_formatted_address`). Gửi nguyên văn công thức. Main ghi nguyên văn vào dòng `D-OLD-ADDR` rồi chạy `run-author --kind model`.
4. Không thêm `old_address` trong task này. Main ghi lựa chọn này vào dòng `D-OLD-ADDR` rồi chạy `run-author --kind model` cho `price_level`, `price_min`, `price_max`, `story`, `local_tips`.

Đã trả lời ngày 2026-11-26. Câu trả lời nằm ở đầu mục `Quyết định của người dùng`. Các mục 1–4 không còn mở.

## Lịch sử quyết định

- 2026-11-26: Triage dừng ở `user_decision` trước `run-author`. Ba nhóm `full_address` không map đủ vì thiếu `old_house_number`, `old_street`, `old_full_address`.
- 2026-11-26: Người dùng chốt `D-OLD-ADDR`: lấy `house_number`, `street`, `full_address`, không tạo `old_house_number`, `old_street`, `old_full_address`. Cách áp dụng nằm ở `Quyết định của người dùng`.
- 2026-11-26: Giữ `docs/context/mapping_legacy_ai_product.md`. Không xóa. Không dùng file này làm input của Architect.
- 2026-11-26: Chạy lại `run-gate`. File mapping không đổi (15:04). Cổng vẫn fail immutability vì xuất hiện `local/once/legacy-init-sgr-visitvn-dev.ipynb` lúc 15:32. `architecture.md` vẫn placeholder. `rounds.architecture` vẫn 0.
- 2026-11-26: Người dùng: không thêm hai file lạc vào task. Tiếp tục chạy kiến trúc.
- 2026-11-26: Architect PASS (`claude-opus-5-5`, high). Dừng ở E0 trước khi sửa code. Chờ người dùng cho thêm ba file test vào `scope.files`.
- 2026-11-26: Người dùng chốt `D-E0`: Thêm ba path trên vào scope.files. Ba path là `tests/test_enr_extract_contract.py`, `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py`.
- 2026-11-26: `test_info_price_rule` kiểm tra `source_name` trên dòng code của `_price`. Comment kiến trúc vẫn ghi «không lọc source_name». Không đổi comment.
- 2026-11-26: Baseline DEV trước `oldpricepy`. Sáu cột gold chưa có. Sáu cạnh active, khoá trống. `slv_3p_poi_price` không có `deleted_at`. P1 trong runbook bỏ điều kiện đó.
- 2026-11-26: Người dùng chấp nhận `D-I2`. `gates.runtime` chuyển `pass`. Task sang `ready_to_merge`.
