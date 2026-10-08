# Quyết định

## Giả định còn lại

- Bộ context `docs/context/CTRL_TABLES_CONTEXT.md` là nguồn ngữ nghĩa bảng `ctrl_*` trong repo. Số liệu mục "Dữ liệu hiện có" chỉ có hiệu lực tới 05/10/2026, không phải snapshot hôm nay.
- Timeout activity `0.12:00:00` được hiểu là 12 giờ theo định dạng timespan của Fabric Data Pipeline.
- Cell notebook được đếm từ 0. Số dòng là dòng trong cell đó.
- Chưa chạy Fabric DEV. Cột gold-log trên bảng ctrl thật và lịch chồng FL_00 là `NOT_VERIFIABLE`.

## Sai lệch so với kiến trúc

- Không có kiến trúc mới. Task này không đi qua cổng Architect.

## Kết luận audit

Báo cáo đầy đủ: `evidence/consistency-report.md`.

Verdict sơ bộ của Main, trước khi Bách chốt: `USER_DECISION`.

Không có P0 được xác nhận chỉ từ repo. Các P1 đã được xử lý trong bảng dưới.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| F-P1-01 | P1 | fixed | Bách chốt cả hai: `running_timeout_minutes` = 780 (13 giờ) ở partner, 3rd-party và tham số pipeline; timeout activity `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` = `0.00:59:00` (59 phút). | Activity khác của FL_00 vẫn `0.12:00:00`. |
| F-P1-02 | P1 | fixed | Bách chốt context pack 08/10/2026: FL_00 không có Switch vì nguồn khác xử lý bằng script. `AGENTS.md` và `.cursor/rules/20-data-pipeline.mdc` đã sửa theo quyết định này. | Không thêm Switch vào FL_00. |
| F-P1-03 | P1 | fixed | Bách chỉ lấy 5 cột gold-log từ `NB_SETUP_GOLD_POI_1H`, không lấy cả notebook làm chuẩn. `NB_CREATE_DDL` tạo `output_versions_json` trên `ctrl_log_run` và `src_versions_json`, `trg_version`, `deactivated_rows`, `qg_json` trên `ctrl_log_table_run`. Cell sau CREATE thêm cột còn thiếu, không DROP. | Chạy cell đó trên Fabric DEV nếu bảng log đã tồn tại. |
| F-P1-04 | P1 | fixed | Bách chốt giữ thứ tự code: `close_stale_runs` trước `acquire_flow_lock`. Đã sửa `NB_00_ORCHES_SLV_TO_GLD.md` và câu gọi trong `NB_LIB_TRANSFORM_SLV_GLD.md`. | |
| F-P1-05 | P1 | rejected-false-positive | Bách chốt: `NB_SLV_POI*`, `NB_GLD_SRV_*`, `NB_SETUP_GOLD_POI_1H`, `PL_VV_TRANSFORM_SLV_TO_GLD_1H` chưa có vì xử lý chưa chốt. Đã gỡ khỏi `docs/context`. Công thức `poi_id` partner được giữ để dùng sau. | Không tạo notebook gọi công thức trong task này. |
| F-P1-06 | P1 | fixed | Bách chốt `run_id` rỗng để truyền tham số. Notebook dùng `exec_id` khi `run_id` trống. Rule pipeline đã bỏ bắt buộc `@pipeline().RunId`. | Giữ literal hiện tại của FL_00. |
| F-P2-03 | P2 | fixed | Bách chốt bỏ `poi_uid`, dùng `poi_id`, và phân cấp notebook theo `docs/context/02_NAMING_CONVENTION.md`. Đã sửa `AGENTS.md`. | |
| F-P2-04 | P2 | accepted-risk | Bách chốt giữ nguyên: pipeline không đọc exit JSON, `NB_00` không gọi `notebook.exit`. | Không sửa hợp đồng exit trong task này. |
| F-P2-05 | P2 | fixed | Bách chốt đổi đường dẫn notebook đang có trong repo từ `claude/` sang `notebooks/`. Tài liệu thiết kế không có trong repo vẫn để `claude/`. | |
| F-P2-06 | P2 | backlog | F16 chỉ được nêu, không có chốt trong code. | Đo trên DEV nếu đổi `max_parallel`. |
| F-P3-01 | P3 | fixed | Comment `PARTITIONED BY` trong `NB_CREATE_DDL` đã nói ForEach FL_00 chạy tuần tự. Markdown hai notebook extract không còn mô tả Switch. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

Bách cho phép sửa hợp đồng agent. Notebook, pipeline và context pack không bị sửa trong lượt này.

## Cổng review

Lệnh `python scripts/vv.py run-gate 20261008-context-implementation-consistency-review --round 1 --timeout 2700` thất bại vì kiểm tra bất biến:

`AUTOMATED GATE FAIL: Codex review changed the repository unexpectedly.`

File `reviews/round-1.md` xuất hiện trong lúc Codex chạy, nên runner không ghi nhận cổng. Trạng thái task được trả về `reviewing`. Bản draft đó không phải kết quả cổng đã chấp nhận. Draft nêu verdict `USER_DECISION`, model `gpt-5.6-sol` high, đủ bốn specialist cộng `risk-gate`, và một P0 `VSVN-R1-001` về MERGE đích không bị chặn bởi khoá.

## Quyết định của người dùng

Đã chốt ngày 08/10/2026:

1. Context pack 08/10/2026 là nguồn sự thật của FL_00. Không thêm Switch. Nguồn khác do script xử lý ngoài pipeline này. `run_id` để rỗng nhằm truyền tham số.
2. Bỏ `poi_uid`. Định danh là `poi_id`.
3. Phân cấp notebook trong `AGENTS.md` theo `docs/context/02_NAMING_CONVENTION.md`.
4. `NB_SLV_POI*`, `NB_GLD_SRV_*`, `NB_SETUP_GOLD_POI_1H` và `PL_VV_TRANSFORM_SLV_TO_GLD_1H` không thuộc phạm vi repo hiện tại. Xử lý chưa chốt. Đã gỡ tên và mô tả luồng đó khỏi `docs/context`. Không copy các file này vào repo.
5. `running_timeout_minutes` = 780 ở cả hai notebook extract và ở activity partner. Timeout activity đó = 59 phút.
6. Context `NB_00` theo thứ tự code: `close_stale_runs` trước `acquire_flow_lock`.
7. Công thức `poi_id` partner giữ lại để dùng sau.
8. Notebook đang có trong repo được trỏ bằng `notebooks/`, không bằng `claude/`.
9. Markdown hai notebook extract khớp FL_00: không có Switch. ForEach chạy tuần tự.
10. Pipeline không đọc exit JSON. `NB_00` không gọi `notebook.exit`. Giữ nguyên.
11. Bách chấp nhận kết quả đối chiếu của Main. Không chạy lại Codex. `gates.specialist_review` và `gates.risk_gate` là `user_decision`, không phải `pass`. `F-P2-06` vẫn `backlog`.
