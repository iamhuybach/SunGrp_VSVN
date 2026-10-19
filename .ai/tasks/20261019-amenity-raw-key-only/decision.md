# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Phân loại | Đổi giá trị khóa, số dòng seed và cách MERGE: architecture bắt buộc, risk high, không fast lane. Review gồm sql-data-reviewer, spark-runtime-reviewer, state-correctness-reviewer và risk-gate. | request.md §Classification rationale | 2026-10-19 |
| D2 | Evidence | Không probe DEV. Mọi dạng amenity_raw hiện có nằm trong SEED_ROWS của repository. | request.md §Repository impact | 2026-10-19 |
| D3 | Runtime | Step chạy lại full hai bảng là runtime-runbook sau review PASS. User chạy trên Fabric DEV. Agent không đánh gates.runtime. | request.md §User outcome | 2026-10-19 |
| D4 | Khóa và seed | Khóa từ điển vẫn là (source_name, business_sector, amenity_group, amenity_raw, amenity). Khóa slv_poi_amenity vẫn gồm amenity_raw. Seed hiện insert-only. | request.md §Acceptance criteria | 2026-10-19 |
| D5 | Cạnh ctrl | Cạnh ctrl_mng_pipeline_config của slv_poi_amenity không được nhân đôi. | request.md §Acceptance criteria | 2026-10-19 |
| D6 | STATE-001 | fix-and-extra-review: Main sửa legacy > 0 thành QualityGateError, rồi bạn chấp nhận một vòng review thứ 3 ngoài cap. | user 2026-10-20 | 2026-10-20 |
| D7 | Từ điển DEV | Không giữ `ref_dictionary_amenities` cũ. DROP bảng đó rồi chạy `NB_SETUP_POI_AMENITY` với `p_apply=true`. Không backup. Không DROP `slv_poi_amenity`. | user 2026-10-20 | 2026-10-20 |
| D8 | Câu types[] | 12 câu `types[] có/thuộc` thành `json_type = '...'` hoặc `json_type in (...)`, fix cứng trong `SEED_ROWS`. `json_type` là `place_type` google của `ref_dictionary_place_type` theo `business_category` hoặc `business_sector` trong câu. | user 2026-10-20 | 2026-10-20 |
| D9 | Nghiệm thu | Chấp nhận kết quả DEV. Idempotency exec `e2dcb0e9-dceb-4917-a409-237001184aed`: insert 0, update 0, xoá mềm 0, version vẫn 1. Task done. | user 2026-10-20 | 2026-10-20 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- GATE-001: `build` không chỉ chặn khi `conds` rỗng. Trước khi ghi, `match_coverage` yêu cầu tập `(business_sector, amenity_group, amenity_raw)` đã resolve bằng đúng `FLAG_MATCH | TYPE_MATCH`. Nguồn: `reviews/round-1.md` GATE-001. Invariant lệch từ điển theo một trong hai hướng thì không ghi vẫn giữ.
- STATE-001: `legacy > 0` thành `QualityGateError` trước khi tạo output. Kiến trúc gốc chỉ ghi metric `dict_legacy_form`. Nguồn: user D6 và `reviews/round-2.md`.
- D8: 12 câu `types[] có/thuộc` được viết lại thành `json_type`. Kiến trúc gốc giữ nguyên những câu này. `Day Spa` không có category đúng tên, lấy category `Spa`. `electric_vehicle_charging_station` không có trong từ điển place type, giữ token. Dòng Bar accommodation bỏ `servesBeer = true` vì giá trị mới chỉ còn `json_type`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | `match_coverage` chặn thiếu hoặc thừa so với `FLAG_MATCH \| TYPE_MATCH` trước khi ghi. Test `test_match_coverage_requires_full_allowlist` bỏ key `sauna`. | |
| STATE-001 | P1 | fixed | `legacy > 0` ném `QualityGateError` trước khi tạo output. Test mixed-state yêu cầu `legacy_blocks_write`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-20: fix-and-extra-review: Main sửa legacy > 0 thành QualityGateError, rồi bạn chấp nhận một vòng review thứ 3 ngoài cap.

## Lịch sử quyết định

- 2026-10-19 triage. Census seed: 27 dòng dạng cờ ` = true`, 8 dòng `types[] = ...` nở thành 14 key, 117 dòng giữ nguyên, tổng 158 nếu không bỏ dòng. Trùng key sau census: `google` / `attraction` / `facilities_and_services` / `goodForChildren` (amenity `Good for Children` và `Family Friendly`). `types` nằm ở `slv_3p_poi.types_json`, không nằm trong `source_flags_json`.
- 2026-10-20 GATE-001 fixed. Kiểm tra rỗng `conds` không chặn từ điển thiếu một key. `match_coverage` thay kiểm tra đó.
- 2026-10-20 review round 2 trả `FIX_REQUIRED` với `STATE-001` P1. `rounds.review` = 2, hết cap. Chưa sửa code cho `STATE-001`. Chờ người dùng chọn.
- 2026-10-20 user chọn D6: sửa `legacy > 0` thành `QualityGateError` và chấp nhận review vòng 3.
- 2026-10-20 user chọn D7: không giữ bảng từ điển cũ; DROP rồi chạy lại `NB_SETUP_POI_AMENITY`. Sau DROP không còn `RESTORE` về version 1. Phục hồi từ điển là chạy lại setup.
- 2026-10-20 user chọn D8: chuẩn hóa 12 câu `types[] có/thuộc` thành `json_type = ''` hoặc `json_type in ('')`, fix cứng trong `SEED_ROWS` từ `ref_dictionary_place_type`.
- 2026-10-20 user chọn D9: đồng ý task done. Idempotency không tạo commit Delta.
