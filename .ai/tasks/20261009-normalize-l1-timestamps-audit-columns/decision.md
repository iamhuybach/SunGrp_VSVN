# Quyết định

## Giả định còn lại

- Dòng L1 đã có trước backfill nhận `created_at` từ `_ingested_at` cũ. Đó là thời điểm ghi silver gần nhất, không phải thời điểm INSERT đầu tiên. Khi `_ingested_at` null, dùng đồng hồ backfill. Chỉ áp dụng cho dòng có sẵn. INSERT mới sau cut-over ghi `created_at` bằng đồng hồ MERGE.
- Đơn vị của `orders.expire_at`, `order_refs.created_at` / `updated_at`, `created_at` / `updated_at` của `order_item_*`, `product_posts.validity_from` / `validity_to`, và cột thời điểm của `business_locations` / `product_post_translations` lấy từ phương án 3 ngày 2026-10-10, không phải từ giá trị đã đo.

## Sai lệch so với kiến trúc

- 2026-10-10: Người dùng yêu cầu instant L1 và hai cột audit lưu kiểu `timestamp`, không lưu chuỗi `yyyy-MM-dd'T'HH:mm:ss.SSS'Z'`. `EPOCH_*` và `ISO_UTC_TS` vẫn đổi đúng instant rồi ghi `timestamp`. `deleted_at` nguồn và `review.time` vẫn là `string`. Ba cột thứ tự 3P vẫn là `timestamp`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-10: Cột nghiệp vụ partner đang tên `created_at` / `updated_at` đổi thành `src_created_at` / `src_updated_at`. Hai tên `created_at` / `updated_at` dành cho audit L1. Không dùng `source_created_at`. `last_updated_at`, `last_verify_at`, `last_in_activated_at`, `deleted_at` nguồn giữ nguyên.
- 2026-10-10: Luồng 3P được chốt từ E2. `crawled_at`, `source_created_at`, `published_at` là ISO UTC, chỉ chuẩn hóa format. `ingested_date` giữ là ngày. `review.time` không đổi vì nằm trong `review_id`.
- 2026-10-10: Phương án 3. `EPOCH_MS_TS` cho nhóm đơn hàng chưa có giá trị và cho hai cột `orders` đã đo được milli giây: `orders.created_at`, `orders.updated_at`, `orders.expire_at`, `order_refs.created_at`, `order_refs.updated_at`, `order_item_tickets.created_at`, `order_item_tickets.updated_at`, `order_item_hotels.created_at`, `order_item_hotels.updated_at`, `order_item_flights.created_at`, `order_item_flights.updated_at`. Mọi cột epoch partner còn lại là `EPOCH_S_TS`, kể cả `product_posts.validity_from`, `product_posts.validity_to`, `business_locations` và `product_post_translations`. Cột `order_item_*` đã là ISO (`usage_date`, `valid_from`, `valid_to`, `check_in_date`, `checkout_date`, `departure_time`, `arrival_time`) chỉ chuẩn hóa format. `deleted_at` nguồn giữ `string`. Số `0` là sentinel, không phải epoch.
