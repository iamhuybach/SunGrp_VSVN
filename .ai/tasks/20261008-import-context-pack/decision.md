# Quyết định

## Giả định còn lại

- Bộ context người dùng gửi là hợp đồng tài liệu, cập nhật 08/10/2026. Số ở mục "Dữ liệu hiện có" lấy từ log tới 05/10, chưa đọc lại Fabric hôm nay.
- `CHECK_CTRL_SNAPSHOT.py` chỉ đọc. Chưa chạy trên Fabric DEV trong task này.
- Giữ nguyên nội dung 11 file. Chỉ thêm lời dẫn ở `docs/context/README.md` và một ignore `F401` cho script snapshot.

## Sai lệch so với kiến trúc

- Không có. Task không qua architecture gate.

## Kết quả review (Main, đối chiếu notebook và pipeline đang có trong repo)

| ID | Severity | Nội dung |
|---|---|---|
| CTX-1 | P2 | `CTRL_TABLES_CONTEXT.md` và `99_PAIN_POINTS.md` (E8) nói hạn khoá luồng ghi ở dòng khoá (`LOCK_EXPIRES_AT`). `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` vẫn tính quá hạn bằng timeout của run đang xét: `lock_at < current_timestamp() - INTERVAL {timeout_min} MINUTES` trong `_lock_expired_sql`. Đúng lỗ hổng review 05/10 #1 mà tài liệu ghi là đã sửa. |
| CTX-2 | P2 | Tài liệu mô tả `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` đi ForEach → Switch theo `item().src_tbl` tới 2 notebook extract. File pipeline trong repo không có Switch, không có `poi_raw_event`, activity notebook tên `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK`. |
| CTX-3 | P3 | Notebook node (`NB_SLV_POI_*`, `NB_GLD_SRV_POI_*`, `NB_SETUP_GOLD_POI_1H`) được mô tả nhưng chưa có trong repo. |
| CTX-4 | P3 | `NB_LIB_TRANSFORM_SLV_GLD.md` không nêu 2 hàm nội bộ `_update_lock_row`, `_build_unaccent_map`. Các hàm public của 2 lib và 2 notebook extract có trong tài liệu. |
| CTX-5 | — | C2 (`max_retries < 0`) tài liệu ghi đang mở. Code lib extract đúng như vậy: `range(1, ctx.max_retries + 2)` và không có hàm kiểm tra miền. |
| CTX-6 | — | Script snapshot không `INSERT` / `UPDATE` / `MERGE` / `DELETE` / `DROP`. Không chọn cột payload. `import json` và `F` chưa dùng. |

Không chặn việc đưa bộ context vào repo. Lần sửa code khoá hoặc pipeline phải lấy CTX-1 và CTX-2 làm việc cần xử lý, không lấy tài liệu làm bằng chứng là code đã vá.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| CTX-1 | P2 | backlog | Tài liệu và notebook lệch. Task này không sửa notebook. | Sửa `_lock_expired_sql` theo hạn đã ghi, có probe Fabric |
| CTX-2 | P2 | backlog | Pipeline export cũ hơn thiết kế trong context. | Cập nhật pipeline hoặc ghi rõ bản export |
| CTX-3 | P3 | backlog | Node chưa được đưa vào repo. | Import notebook node khi có file |
| CTX-4 | P3 | backlog | Thiếu tên hàm private trong doc. | Bổ sung khi sửa doc lib |

## Quyết định của người dùng

- Chưa có. Người dùng merge.
