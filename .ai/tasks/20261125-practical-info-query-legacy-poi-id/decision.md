# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-ID-UNIT | Số `poi_id` một request được nhập | Ý tôi là có thể nhập min 1 poi_id và max là 500 poi_id, không phải lấy khoảng số hay độ dài | Quyết định của người dùng | 2026-11-25 |
| D-LEGACY-MAP | Bảng map serving và job copy | Đồng ý cả 4. (a) Tên bảng `apps.srv_poi_legacy_id_map`, và được mirror bảng gold ngoài họ `gld_srv_*` vào schema `apps`. (b) Khóa chính `legacy_poi_id` lấy từ MERGE key của `lgpmain`, không lấy từ NodeSpec. (c) Phía data sở hữu job copy: copy đủ 1:1 mọi dòng gold map, kể cả dòng không `OK`, trong một transaction. API chỉ đọc và lọc `OK`. (d) `services/data-serving-service/AGENTS.md` mở từ năm bảng thành sáu bảng. | Quyết định của người dùng | 2026-11-25 |
| D-ANY | Predicate resolve và lọc id | Đồng ý sửa qua ANY(:ids). Chấp nhận thêm một vòng sửa, verify và review. | Quyết định của người dùng | 2026-11-25 |
| D-PERF | Vòng architecture hiệu năng | Cần quét thêm một vòng architecture để tối ưu hiệu năng vì endpoint này nhiều request và cần phản hồi nhanh | Quyết định của người dùng | 2026-11-25 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- D-ID-UNIT là số lượng giá trị `poi_id` trong một request: tối thiểu 1, tối đa 500. Không phải miền giá trị của `poi_id`, không phải độ dài chuỗi, không phải `size` phân trang (trần 100).
- D-LEGACY-MAP đã chốt. `apps.srv_poi_legacy_id_map` là bản copy đọc của map gold. Job copy thuộc phía data.
- Danh sách practical info giữ `POST` với `ids` trong body. Vòng architecture D-PERF tối ưu thời gian phản hồi, không đổi method.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| API-001 | P1 | fixed | POST practical_info khai báo envelope 200/400/401/415/422/500. Schema 200 là PracticalInfoListEnvelope. | |
| SEC-001 | P1 | fixed | PracticalInfoBodyLimitFilter chặn body trước Jackson: Content-Length vượt trần không đọc stream; chunked dừng ở trần. Test filter và MockMvc oversized. | |
| JPA-001 | P1 | fixed | Resolve và lọc poi_id dùng arrayContains, không IN. Page lang/cover chỉ IN id của trang, size ≤ 100. Test 120 id: tối đa 5 câu SQL và mỗi câu ≤ 100 placeholder. | |
| JPA-002 | P1 | fixed | Review vòng 3 PASS. Predicate là `= ANY (CAST(:ids AS text[]))`. Test `idPredicatesUsePrimaryKeyIndexesWhenSeqScanDisabled` dùng được `srv_poi_legacy_id_map_pkey` và `srv_poi_info_pkey` khi `enable_seqscan = off`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

Ý tôi là có thể nhập min 1 poi_id và max là 500 poi_id, không phải lấy khoảng số hay độ dài

S1 đã chốt. Người dùng: Đồng ý cả 4.

- (a) Tên bảng `apps.srv_poi_legacy_id_map`, và được mirror bảng gold ngoài họ `gld_srv_*` vào schema `apps`.
- (b) Khóa chính `legacy_poi_id` lấy từ MERGE key của `lgpmain`, không lấy từ NodeSpec.
- (c) Phía data sở hữu job copy: copy đủ 1:1 mọi dòng gold map, kể cả dòng không `OK`, trong một transaction. API chỉ đọc và lọc `OK`.
- (d) `services/data-serving-service/AGENTS.md` mở từ năm bảng thành sáu bảng.

JPA-002 còn mở sau review vòng 2. Chọn một hướng:

- Chấp nhận rủi ro: giữ `arrayContains`. Main ghi `accepted-risk` và chuyển `waiting_runtime` để chạy runbook.
- Sửa sang `scalar = ANY(:ids)`: người dùng đã chấp nhận thêm một vòng sửa, verify và review (D-ANY), và yêu cầu vòng architecture hiệu năng trước (D-PERF).

## Lịch sử quyết định

- 2026-11-25 triage: chưa có đơn vị cho biên 0 và 500. Dừng `user_decision` trước `run-gate`. Chưa chạy `run-author --kind model`.
- 2026-11-25: người dùng chốt D-ID-UNIT. Biên là số lượng `poi_id` nhập trong một request, min 1 và max 500. Yêu cầu gốc ghi «biên dưới 0»; câu trả lời này thay bằng min 1.
- 2026-11-25: Architect PASS (`claude-opus-5-5`, effort high). Main brief dừng S1 trước edit list. Chưa sửa source.
- 2026-11-25: người dùng chốt D-LEGACY-MAP: Đồng ý cả 4.
- 2026-11-25: review vòng 1 FIX_REQUIRED (API-001, SEC-001, JPA-001), đã sửa và verify PASS. Review vòng 2 còn JPA-002. Hết cap review và verify.
- 2026-11-25: người dùng chốt D-ANY và D-PERF. `review_plan.extra_round_approved_on` = 2026-11-25 để mở review vòng 3. Architecture vòng 2 chạy trước khi sửa `ANY(:ids)`.
- 2026-11-26: Docker local và verify thêm PASS. Review vòng 3 PASS. JPA-002 = fixed.
- 2026-11-26: người dùng xác nhận DEV đã thêm `apps.srv_poi_legacy_id_map` và request chạy thành công. `gates.runtime` = pass.
