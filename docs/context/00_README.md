# Bộ context Visit Vietnam — Data Model mới (POI) trên Microsoft Fabric

> Cập nhật: 08/10/2026. Dùng cho người mới vào dự án và cho agent (Cursor / Claude) trước khi đọc / sửa code.
> Số liệu theo log đã gửi về tới 05/10. Lấy số mới: chạy `CHECK_CTRL_SNAPSHOT.py` (chỉ đọc).

## Danh sách file

| File | Nội dung | Khi nào đọc |
|---|---|---|
| `01_DATA_MODEL.md` | Mô tả, thông tin, ý nghĩa của Data Model mới: phân tầng, sơ đồ, pipeline, bronze, silver L1 (23 + 14 bảng), ref, định danh, model cũ → mới | Luôn đọc đầu tiên |
| `02_NAMING_CONVENTION.md` | Quy ước đặt tên (lakehouse, tiền tố bảng, notebook, pipeline, id ctrl, cột, cột nội bộ, enum, tham số) và convention code | Trước khi tạo / đổi tên bất cứ thứ gì, trước khi viết code |
| `CTRL_TABLES_CONTEXT.md` | 7 bảng ctrl: mô tả, ý nghĩa, DDL, cột, dữ liệu hiện có, thao tác SQL, lịch sử thay đổi | Khi đụng tới cấu hình, watermark, log, state, reject |
| `CHECK_CTRL_SNAPSHOT.py` | Script **chỉ đọc**: chụp dữ liệu hiện có của 7 bảng ctrl | Khi cần số liệu ctrl thật |
| `NB_LIB_EXTRACT_RAWDATA.md` | Thư viện extract: 14 mục, mọi hàm, luồng `run_controlled` | Khi sửa / thêm extract |
| `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` | Extract Debezium partner → `slv_pn_*`: tham số, luật phân loại, TOAST, MERGE, vận hành | Khi đụng nguồn partner |
| `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` | Extract tài liệu crawl 3P → `slv_3p_poi_*`: `load_mode`, ngôn ngữ, khoá suy ra, vận hành | Khi đụng nguồn 3P |
| `NB_00_ORCHES_SLV_TO_GLD.md` | Điều phối tính lại: tham số, luồng `orchestrate`, runbook | Khi sửa `NB_00_ORCHES_SLV_TO_GLD` |
| `NB_LIB_TRANSFORM_SLV_GLD.md` | Thư viện tính lại: cạnh, hộp thư, khoá, ghim, QG, row_hash, MERGE, mọi hàm | Khi sửa lib |
| `99_PAIN_POINTS.md` | Pain point, root cause, lỗi đã gặp, vấn đề còn mở, bài học | Trước khi đề xuất giải pháp (tránh lặp lỗi cũ) |

## Thứ tự đọc

1. `01_DATA_MODEL.md` → 2. `02_NAMING_CONVENTION.md` → 3. `99_PAIN_POINTS.md` §0 (bài học) → 4. file của phần đang làm.

## Tóm tắt 10 dòng

1. Fabric F16, Runtime 1.3, 3 lakehouse `lh_vv_bronze` / `lh_vv_silver` / `lh_vv_gold`, ctrl ở `lh_vv_bronze.ctrl`.
2. Raw: `partner_raw_data` (Debezium CDC), `poi_raw_event` (tài liệu crawl 3P), Eventstream append, không stats.
3. Extract (`PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, 10–15 phút): ForEach tuần tự, nhánh có việc chỉ gọi `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` với `partner_raw_data` gắn cứng. Notebook 3rd-party có trong repo, không nằm trong pipeline này.
4. Silver L1 đúng cấu trúc nguồn: `slv_pn_*` (23), `slv_3p_poi_*` (14, 13 active). Không rule nghiệp vụ.
5. Rule nghiệp vụ dạng dữ liệu nằm ở bảng `ref_*`.
6. Chống chạy chồng bằng khoá nguyên tử trên dòng watermark. Hạn khoá luồng tính lại = `lock_at` cộng timeout của run đang xét, không phải hạn đã ghi trên dòng khoá.
7. Bảng `poi_*` cũ, `poi_master`, chuỗi NB_00 cũ vẫn chạy song song tới cutover.
8. Còn mở: dữ liệu nguồn (`after` rỗng, raw dừng từ 16–17/09), C2 lib extract, `[VERIFY]` runMultiple / múi giờ, bảo trì Delta.

## Quy tắc khi làm việc với bộ này

| Quy tắc | Chi tiết |
|---|---|
| Không suy đoán dữ liệu | Thiếu số liệu → hỏi hoặc viết script chỉ đọc (`CHECK_` / `DIAG_`), không đoán |
| Ràng buộc cứng | Không SPN; không xoá file trong shortcut OneLake; giữ `poi_*` cũ + chuỗi NB_00 cũ; 1 notebook xử lý / nguồn; không viết cứng; gold chỉ đồng bộ, silver giữ logic |
| Sửa code | Comment `[SỬA dd/mm]` + lý do; sửa ít → chỉ ra chỗ sửa; sửa nhiều → thay cả notebook; deploy lib trước notebook gọi |
| Nhãn | `[PROPOSED]` tên mới · `[VERIFY]` cần kiểm trên Fabric · `[ASSUMED]` giả định · `OD-xx` quyết định mở |
| Nguồn sự thật | Notebook trong repo (`notebooks/*.ipynb`) > tài liệu thiết kế > bộ context này. Lệch nhau → báo, không tự chọn |

## Tài liệu gốc trong project (`claude/`)

| Nhóm | File |
|---|---|
| Thiết kế | `GOLD_POI_FLOW_DESIGN.md`, `POI_3P_EXTRACT_REDESIGN.md`, `PARTNER_EXTRACT_REDESIGN.md`, `NB_EXTRACT_PARTNER_CDC_FLOW.md`, `PL_PRECHECK_GET_METADATA.md` |
| Review | `REVIEW_EXTRACT_PROD_0410.md`, `PATCH_REVIEW_0510.md` |
| Notebook trong repo | `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb`, `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`, `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`, `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`, `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb`, `notebooks/NB_CREATE_DDL.ipynb` |
| Script chỉ đọc | `CHECK_GOLD_POI_INPUTS_0410.py`, `DIAG_GOLD_GAPS_0510.py`, `DIAG_PARTNER_0410*.py`, `VERIFY_3P_CONFIG_0410.py`, `PREVIEW_3P_CONFIG_0410.py` |
| Đã cũ, không dùng | `seed_ctrl_poi_3rd_party.sql`, `APPLY_3P_CONFIG_0410.sql`, `RESULT_RERUN_0410.py`, `DOC_MAP_0410.diff`, `NB_EXTRACT_PARTNER_CDC.ipynb`, `ctrl_changes_2026-10-01.sql`, `ddl_ctrl_log_cdc.sql` (thay bằng `NB_CREATE_DDL`) |
