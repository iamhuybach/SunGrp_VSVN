# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Danh tính sgm | `slv_3p_poi` lưu `source_name` bronze (`sgm` hoặc `google`). Phía sau `slv_3p_poi`, dòng `sgm` dùng `source_name` hiệu lực `google` và `poi_id = HASH_MD5_UUID('google', source_id)`. Không tạo `poi_id` thứ hai từ `sgm`. | request.md Constraints | 2026-11-19 |
| D-2 | Chỗ đụng khóa MERGE | Probe `p1_sgm_source_id`: `bronze_sgm=2630`, `overlap_source_id=402`, `id_eq_source_id=2630`. 402 `source_id` có cả `sgm` và `google`. D-1 đặt `poi_id = HASH_MD5_UUID('google', source_id)`, trùng khóa MERGE `poi_id`. Cách xử lý 402 khóa là D-3. Công thức `review_id` và `media_dedup_key` của event `sgm` là D-4. | evidence/results/p1_sgm_source_id.txt | 2026-11-19 |
| D-3 | Ưu tiên google | Ưu tiên `source_name` là `google`. Event `sgm` mới hơn dòng đã có `source_name=google` thì không MERGE. Event `google` mới hơn dòng `sgm` thì ghi `google` và `source_name=google`. Dòng chỉ có `sgm` vẫn lưu `source_name=sgm`, `poi_id=HASH_MD5_UUID('google', source_id)`. | Quyết định của người dùng | 2026-11-19 |
| D-4 | Hash review và ảnh | Phương án B. Event `sgm`: `review_id` và `media_dedup_key` hash `source_name` hiệu lực `google`, không hash bronze `sgm`. `poi_id` vẫn theo D-1. Dòng `google` không đổi công thức khóa. Ảnh tên `scraper-` không trùng tên `google` vẫn là dòng riêng. | Quyết định của người dùng | 2026-11-19 |
| D-5 | Google cũ hơn vẫn ghi đè | Override đề xuất giữ thứ tự `crawled_at` trong `architecture.md` mục Ordering. Event `google` có `crawled_at` cũ hơn dòng `sgm` đã lưu vẫn MERGE, `source_name=google`. | Quyết định của người dùng | 2026-11-19 |
| D-6 | Sẵn sàng merge | Người dùng yêu cầu `ready_to_merge` sau runtime PASS. GATE-001 và GATE-002 đã `accepted-risk`, `open_findings` rỗng. `specialist_review` và `risk_gate` chuyển `pass` để transition hợp lệ. `reviews/round-3.md` vẫn là `FIX_REQUIRED`. | Quyết định của người dùng | 2026-11-19 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Trên 2630 dòng `sgm`, `normalized_payload.id` bằng `source_id`. Các khóa registry ở p1 có `absent=0`. Probe p2: `NAME` đúng `google` và `sgm`; `overlap_exact=402` bằng `overlap_trimmed`. 402 khóa đã có `poi_id` google trên `slv_3p_poi` (`silver_hit=402`) và `sgm` mới hơn cả 402 (`sgm_newer=402`, `google_newer=0`). Review trên tập trùng: `sgm_reviews=2041`, `match_exact=93`, `match_name_only=420`. Ảnh: `sgm_photos=2814`, `match_name=0`, `scraper_named=2814`.

## Sai lệch so với kiến trúc

- Bỏ `F.broadcast` (SPARK-001). Join và hành vi D-3/D-5 không đổi.
- PIPE-001: khi không takeover, `slv_3p_poi` chạy trước các bảng con. Architecture để mọi bảng cùng một wave.
- R-2: `NULL OR false` ra NULL, `when(~skip)` xoá khối `_b__` của `sgm` chưa có trong silver. Lần ghi đầu thiếu review và ảnh. Lần `full_reload` sau thấy owner `sgm` nên ghi bù. Đã `coalesce` skip về false.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | rejected-false-positive | `architecture.md` mục Partial failure: document `google` thiếu khối thì không sinh dòng, dòng `sgm` cũ ở bảng con giữ nguyên vì không có nhánh xoá. Gate chỉ chặn khi bảng khác FAILED. | |
| SPARK-001 | P1 | fixed | Bỏ `F.broadcast` trên owner snapshot, tập google trong lần chạy, và bảng đích. Join giữ nguyên. | |
| SQL-001 | P1 | rejected-false-positive | `resolve_latest` giữ thứ tự `(crawled_at, event_id, dedup_order, _pos)` như trước task. Architecture yêu cầu thứ tự này không đổi ngoài takeover. | |
| PIPE-001 | P1 | fixed | Không takeover: `slv_3p_poi` chạy trước. Bảng con chỉ chạy khi `slv_3p_poi` là SUCCESS hoặc NO_DATA. Parent lỗi thì bảng con SKIPPED, không commit state. | |
| GATE-001 | P0 | accepted-risk | Người dùng chấp nhận 2026-11-19. Pipeline lịch truyền `table_filter` rỗng nên không tắt takeover. Rủi ro còn khi chạy tay với `table_filter` có `slv_3p_poi` mà thiếu bảng con: parent có thể thành `google` và lần chạy đủ bảng sau không takeover các bảng con. | |
| GATE-002 | P1 | accepted-risk | Người dùng chấp nhận 2026-11-19. Pipeline lịch truyền `state_key = doc`. Rủi ro còn khi chạy tay `state_key = row`: reset takeover không xóa state theo `review_id` hoặc `media_dedup_key`, event `google` sau có thể bị coi là cũ. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- D-1, 2026-11-19: `sgm` và `google` là cùng một nguồn. Không notebook extract mới, không pipeline mới. Không thêm từ điển `source_name = 'sgm'`. Không gán `json_path` cho khóa chưa có trong contract registry Google. Người dùng sửa tên nguồn từ `gsm` sang `sgm` trong cùng ngày.
- D-3, 2026-11-19: Ưu tiên source_name là google. Nếu sgm vào sau thì skip-overlap; Nếu google vào sau lấy google.
- D-4, 2026-11-19: D-4 B.
- D-5, 2026-11-19: D-5 override.
- 2026-11-19: accept risk cho cả 2 GATE.
- D-6, 2026-11-19: Chuyển `ready_to_merge`. Đóng `specialist_review` và `risk_gate` thành `pass` vì hai finding đã accepted-risk.

## Lịch sử quyết định

- 2026-11-19: Ghi D-1 từ yêu cầu. D-2 dừng trước code vì công thức khóa hiện tại đụng danh tính đã chốt khi hai nguồn cùng `source_id`. Tham số `sources` trong repo, cả default notebook và activity pipeline, là `google`.
- 2026-11-19: Probe `p1_gsm_source_id` có `overlap_source_id=0` vì lọc `gsm` và `bronze_gsm=0`. Người dùng sửa nguồn thành `sgm`. Kết quả đó và `model-design.md` vừa sinh bị loại. Evidence trở lại pending. Chưa sửa code.
- 2026-11-19: Probe `p1_sgm_source_id` có `overlap_source_id=402`. Dừng `user_decision` trước khi sửa code. Silver hiện `silver_sgm=0`.
- 2026-11-19: Người dùng chốt D-3. `sgm` đến sau thì không MERGE. `google` đến sau thì ghi `google`.
- 2026-11-19: Architecture `EVIDENCE_REQUIRED`. Khi `google` ghi đè POI chỉ có `sgm`, `review_id` và `media_dedup_key` vẫn hash `sgm` nên có thể thành dòng thứ hai. Chờ probe `p2_sgm_overlap_detail` rồi người dùng chọn D-4. Chưa sửa code.
- 2026-11-19: p2 đạt kiểm tra tên và overlap. `sgm_only=2228`. 402 khóa trùng đã có trên silver và `sgm` mới hơn, nên D-3 bỏ event `sgm` đó. `match_exact=93/2041`, ảnh `match_name=0`. Dừng `user_decision` cho D-4 và D-5. Chưa sửa code.
- 2026-11-19: Người dùng chọn D-4 B và D-5 override. Chưa sửa code. Architecture phải chạy lại vì D-5 đổi thứ tự đã đề xuất.
- 2026-11-19: Review round 1 `FIX_REQUIRED`. SPARK-001 bỏ broadcast. STATE-001 và SQL-001 là `rejected-false-positive` theo architecture.
- 2026-11-19: Review round 2 `FIX_REQUIRED`, chỉ còn PIPE-001. Hết 2 vòng review. Dừng `user_decision`.
- 2026-11-19: Người dùng chấp nhận thêm một vòng review. `extra_round_approved_on` = 2026-11-19. PIPE-001 sửa bằng cách chạy `slv_3p_poi` trước khi không có takeover.
- 2026-11-19: Review round 3 `FIX_REQUIRED`. Còn GATE-001 P0 và GATE-002 P1. Hết cap 3 vòng. Dừng `user_decision`.
- 2026-11-19: Người dùng chấp nhận rủi ro GATE-001 và GATE-002. Không sửa thêm hai nhánh chạy tay đó.
- 2026-11-19: R-1 `9609d878-c47e-4368-80c6-d7c00589eaeb` NO_DATA, inserted 0. R-2 `eafc3d5a-d4a9-422c-a011-f558e71632af` review ins=11797, media ins=16616. Nguyên nhân: skip NULL xoá khối JSON lần insert đầu. Đã sửa coalesce.
- 2026-11-19: Người dùng yêu cầu `ready_to_merge` và commit. D-6 đóng hai gate review còn `fix_required`.
