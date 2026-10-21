# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Fast lane | Fast lane is derived, not manually asserted: `complexity=low`, `risk_level=low`, no behavior change, and at most two changed files. | WORKFLOW.md §5 | 2026-10-21 |
| D-02 | enrich_type | Cột tài liệu `enrich_type` chỉ trên bảng mô tả `gld_enr_poi_info`. Giá trị là `enrich description`, `enrich multi-lang`, `enrich destination` theo danh sách người dùng. Cột thuộc nhiều nhóm thì ghi đủ nhóm. Cột không có trong danh sách để trống. Không thêm cột này vào DDL. | Người dùng 2026-10-21 | 2026-10-21 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-21 — Thêm cột `enrich_type` trong file. `enrich description`: poi_id, poi_name, poi_name_normalized, types, primary_type, business_sector, business_category, website_url, full_address, city, ward, street, category_group, range_low_min, range_high_min, candidate_best_time_code, best_time, canonical_candidate, rating, user_rating_count, cost_vnd, cost, time_to_spend, destination_name, price_level, opening_hours_text, review_json. `enrich multi-lang`: time_to_spend, best_time, cost_vnd. `enrich destination`: house_number, street, ward, city, full_address, lat, lng.

## Lịch sử quyết định

- 2026-10-21 — D-01. Một file `docs/context/gld_enr_poi_info_review.md`. Không đổi notebook, DDL, pipeline, hay hành vi. `complexity=low`, `risk_level=low`, không signal. Architecture, evidence, runtime, và specialist review không bắt buộc.
- 2026-10-21 — D-02. Thêm `enrich_type` vào bảng mô tả `gld_enr_poi_info`. `gld_enr_poi_review` không có cột này vì danh sách không gồm cột riêng của review.
