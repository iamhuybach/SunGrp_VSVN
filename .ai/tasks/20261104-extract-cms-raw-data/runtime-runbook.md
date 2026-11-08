# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHƯA CẦN` hoặc `CHỜ CHẠY` hoặc `PASS` hoặc `FAIL`.

## Phạm vi và môi trường

## Điều kiện tiên quyết

## Baseline trước khi chạy

## Các bước thực hiện

## Kiểm tra kết quả

## Chạy lại để kiểm tra idempotency

## Kiểm tra log và watermark

## Rollback và forward recovery

## Kết quả người dùng ghi nhận

- 2026-11-08, Fabric DEV, `exec_id=4ab436e9-74eb-4cc6-92ab-9ec51f6e4831`, `run_mode=DRY_RUN`, `read_mode=FULL`, version 1488.
- Seed: 4 dòng `DOC`, `registry_rows=59`, watermark `wm_transform_cms_raw_data` `INITIALIZED`, `last_src_version` null.
- Đọc 193423, hợp lệ 125143, bỏ qua 0, reject 68280, `cast_null=0`. `docs_by_table`: blog 79756, destination 37141, news 223, promotion 8023. `null_locale_rows` cả bốn bảng là 0.
- `ins=0`, `upd=0`. Chưa chạy ghi vì `apply` của mỗi bảng vẫn là 125143.
- 2026-11-09, Fabric DEV, `exec_id=2ae46456-d204-4ffc-a092-b91203806299`, `run_mode=DRY_RUN`, version 1488. `apply` khớp `docs_by_table`: blog 79756, destination 37141, news 223, promotion 8023. `rej=0`, `null_cast=0`, `ins=0`, `upd=0`. Được phép chạy ghi.
- 2026-11-09, hai lần ghi đều `run_mode=FULL_RELOAD` nên watermark không tiến. Lần 1 `exec_id=15d31636-98b6-4080-ae46-5d1bf5eb0da3`: insert blog 152, destination 98, news 16, promotion 59, tổng 325, `cast_null=0`, reject tài liệu 68280. Lần 2 `exec_id=02413c78-63ea-4eb4-b1cb-cf0fc71b84c7`: insert 0, update đúng 325 khóa đó. `last_src_version` đầu lần 2 vẫn null.
- 2026-11-09, incremental `exec_id=3223bc96-48ec-41e8-ac7d-0d4a2150078c`, `run_mode=INCREMENTAL`, `inserted=0`, `updated=0`. Cả bốn bảng `stale` bằng `in`, `apply=0`. Đầu lần chạy `last_src_version` null nên đọc FULL; version chốt 1488. `error` null. `finalize_watermark` ghi `last_src_version` bằng version đã chốt khi `SUCCESS`.

