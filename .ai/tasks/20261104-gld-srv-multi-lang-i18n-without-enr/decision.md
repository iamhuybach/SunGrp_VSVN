# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-I18N-ROW | Dòng gold khi không có multi_lang khớp | Một dòng slv_pn_business_service_i18ns không có dòng slv_enr_poi_info_multi_lang khớp theo poi_id partner và lang = locale vẫn tạo dòng gld_srv_poi_multi_lang. | User 2026-11-04; request.md `## Decided` | 2026-11-04 |
| D-I18N-COLS | Cột gold lấy từ i18n | Thông tin i18n được giữ là đúng các cột gold hiện lấy từ i18n: description từ bio, experience từ usps. Không thêm cột gold mới. | User 2026-11-04; request.md `## Decided` | 2026-11-04 |
| D-I18N-KEY | poi_id và lang của dòng chỉ có i18n | poi_id của dòng này là uuid_md5(business_service_id, 'partner'), lang là locale. | User 2026-11-04; request.md `## Decided` | 2026-11-04 |
| D-KEEP | Dòng đã khớp và nhánh không phải partner | Dòng đã có multi_lang giữ transform hiện tại, kể cả fallback bio/usps. Nhánh không phải partner vẫn do slv_enr_poi_info_multi_lang dẫn. | User 2026-11-04; request.md `## Decided` | 2026-11-04 |
| D-REF | Task dẫn chiếu | Không thay các quyết định D-SRV-LANG, D-SRV-TEXT, D-REINIT của task 20261104-poi-review-src-and-partner-i18n. | User 2026-11-04; request.md `## User outcome` | 2026-11-04 |
| UD-SRC | source_name khi không có entity | lấy từ bảng slv_pn_business_service_i18ns nên source_name vẫn là 'partner' | User 2026-11-04 | 2026-11-04 |
| UD-MEASURES | time_to_spend, best_time, cost_vnd khi không có multi_lang | slv_pn_business_service_i18ns có data nhưng time_to_spend, best_time, cost_vnd khi không có multi_lang nhưng slv_enr_poi_info_multi_lang thì time_to_spend, best_time, cost_vnd để null. | User 2026-11-04 | 2026-11-04 |
| UD-LOCALE | Locale nào được phát dòng | Lấy mọi locale vì đây là bảng chứa những thông tin đa ngôn ngữ. | User 2026-11-04 | 2026-11-04 |
| UD-DELETED | Lọc deleted | Giữ như hiện tại | User 2026-11-04 | 2026-11-04 |
| UD-INPUT | Bảng multi_lang vắng mặt | Nếu slv_pn_business_service_i18ns có data (của bio và usps), nhưng slv_enr_poi_info_multi_lang không có poi_id khớp thì vẫn hiển thị nhưng những fields lấy từ slv_enr_poi_info_multi_lang sẽ null | User 2026-11-04 | 2026-11-04 |
| UD-BLANK | Khoá blank | Chốt theo kiến trúc | User 2026-11-04 | 2026-11-04 |
| D-ML-SRC | source_name trên multi_lang và dòng i18n | Tạo thêm 1 cột source_name ở bảng slv_enr_poi_info_multi_lang. Dòng chỉ có i18n vẫn lấy mọi locale và source_name là partner. | User 2026-11-04; câu giữa bị D-ML-NOMATCH thay | 2026-11-04 |
| D-ML-CAP | Thêm một vòng architecture | Đồng ý cho thêm một vòng architecture | User 2026-11-04 | 2026-11-04 |
| D-ML-PICK | source_name theo poi_id | 1 poi_id có thể nhiều lang nhưng đều thuộc 1 source. | User 2026-11-04 | 2026-11-04 |
| D-ML-GATE | Điều kiện google của NB_ENR_POI_INFO | gld_enr_poi_info vẫn lấy slv_poi_entity_non_enrich.source_name | User 2026-11-04; D-ML-NOMATCH thay câu "Dùng source_name mới" | 2026-11-04 |
| D-ML-WRITER | Ai ghi source_name lên multi_lang | Chỉ cần thêm cột DDL. Hiện tại đổ vào bảng đấy là job enrich ngoài và chưa implement | User 2026-11-04 | 2026-11-04 |
| D-ML-NOMATCH | source_name của gld_enr_poi_info | gld_enr_poi_info vẫn lấy slv_poi_entity_non_enrich.source_name | User 2026-11-04 | 2026-11-04 |
| D-ML-TYPE | Kiểu cột source_name | xác nhận cột DDL là source_name STRING, nullable | User 2026-11-04 | 2026-11-04 |
| D-ML-TEST | Test đuôi NB_CREATE_DDL | Đồng ý thêm | User 2026-11-04 | 2026-11-04 |
| D-RUN | Chạy Fabric | Ok tôi muốn việc chạy NB này sẽ thực hiện bởi task 20261104-poi-review-src-and-partner-i18n luôn. | User 2026-11-04 | 2026-11-04 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- 2026-11-04: `mlsrcpy` bật `held = True` ngay sau UPDATE khoá, trước SELECT chủ khoá. `finally` nhả theo `lock_exec_id = LOCK` và `raise failed from cleanup_exc`. Finding STATE-001 P1. Bản §16.3 đặt `held = True` sau SELECT.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | fixed | `held` bật ngay sau UPDATE khoá; finally nhả theo token và giữ lỗi gốc. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-04: user chốt UD-LOCALE, UD-DELETED, UD-SRC, UD-MEASURES, UD-INPUT, UD-BLANK. Nguyên văn nằm ở `## Quyết định hiện hành`.

## Lịch sử quyết định

- 2026-11-04: ghi D-I18N-ROW, D-I18N-COLS, D-I18N-KEY, D-KEEP, D-REF từ yêu cầu user. Năm mục USER_DECISION để trống giá trị.
- 2026-11-04: Architect trả `RESULT: EVIDENCE_REQUIRED`. Mục §0 nói blocker là năm dòng UD, không phải dữ liệu; probe §13 không phải gate. Runner vẫn đặt `gates.evidence` và `gates.architecture` = `evidence_required`. Giá trị năm dòng vẫn trống.
- 2026-11-04: user chốt sáu dòng UD. UD-BLANK lấy rule null ở architecture §10: `_pid` hoặc `_loc` null thì bỏ và đếm warn `multi_lang_i18n_key_null`; chuỗi blank không phải null nên guard đó không bắt. Vì §0 nói probe không phải gate, `classification.evidence_required` trả về false và `gates.evidence` về `not_required` trước lần architecture thứ hai.
- 2026-11-04: lần architecture thứ hai `RESULT: PASS`. UD-BLANK được đọc là: `business_service_id` hoặc `locale` null hoặc blank sau `trim` thì bỏ, đếm warn `multi_lang_i18n_key_blank`. `required_inputs` giữ `("multi_lang", "entity")`.
- 2026-11-04: user thêm D-ML-SRC. Bản PASS vòng 2 không còn là thiết kế để triển khai. `gld_enr_poi_info.source_name` hiện lấy từ `slv_poi_entity_non_enrich`. Không notebook nào có `trg_tbl` = `slv_enr_poi_info_multi_lang`. Công thức ghi cột mới chưa có trong yêu cầu.
- 2026-11-04: user duyệt D-ML-CAP, ghi D-ML-PICK và D-ML-GATE. D-ML-WRITER còn là câu hỏi của user. Main chưa đặt `rounds.architecture` về 0 và chưa gọi Architect.
- 2026-11-04: D-ML-WRITER chốt chỉ thêm cột DDL. Job enrich ngoài repo đổ bảng, chưa implement. D-ML-NOMATCH còn là câu hỏi về quan hệ hai bảng.
- 2026-11-04: D-ML-NOMATCH thay câu "Bảng gld_enr_poi_info lấy source_name từ đây" trong D-ML-SRC. `gld_enr_poi_info.source_name` giữ `slv_poi_entity_non_enrich.source_name`. Cột mới chỉ thêm DDL trên `slv_enr_poi_info_multi_lang`. D-ML-GATE không đổi notebook enrich vì cột gold không chuyển nguồn. User đã duyệt D-ML-CAP; Main đặt `rounds.architecture` về 0 cho một vòng mới.
- 2026-11-04: Architect `RESULT: PASS`, `rounds.architecture` = 1. Bản PASS cũ không còn dùng. Brief dừng trước DDL để user xác nhận `source_name STRING` nullable sau `experience`, và có thêm `tests/test_poi_entity_contract.py` vào `scope.files` hay không.
- 2026-11-04: D-ML-TYPE xác nhận STRING, nullable. Vị trí sau `experience` giữ theo brief. D-ML-TEST đồng ý thêm `tests/test_poi_entity_contract.py` vào `scope.files`.
- 2026-11-04: D-RUN. Fabric chạy `NB_GLD_SRV_POI_MULTI_LANG` và cell `mlsrcpy` trong task `20261104-poi-review-src-and-partner-i18n`. Task này không có bước Fabric riêng.
- 2026-11-04: User dán `source_name: +lh_vv_silver.dbo.slv_enr_poi_info_multi_lang`. Dấu `+` là ALTER đã thêm cột. Orchestrator GLD 30M chưa có kết quả.
