## Ngoại lệ model

Người dùng duyệt ngày 2026-10-14. Người viết đề xuất này là Claude Code, model `claude-opus-5-5`, effort `medium`. Đây không phải lượt Architect. Architect vẫn là `claude-opus-5-5` effort `high` và chỉ viết `architecture.md` qua `run-gate`. `models.architect.effort` giữ `high` vì validator từ chối giá trị khác.

## Phạm vi

Task gốc: `20261013-3p-extract-from-raw-payload`. Đề xuất này chỉ sửa các cột người dùng nêu trong comment ngày 2026-10-14. Mọi dòng khác của đề xuất giữ đúng quyết định cuối cùng của task gốc, gồm Q1–Q16, `dropped_columns_confirmed`, quyết định bổ sung (2026-10-13, tối) và cách xử lý findings.

Hành động cũ dưới đây là hành động đã land, không phải bảng nháp đầu tiên. Theo Q4, cột không còn được extract thì gỡ khỏi registry và khỏi DDL trong `NB_CREATE_DDL`, không đặt `is_active = false`. Chữ "tắt" trong bảng nháp đã bị Q4 thay thế.

## Dòng thay đổi

| Bảng | Cột | Hành động cũ (đã land) | Hành động mới |
|---|---|---|---|
| `slv_3p_poi_contact` | `phone` | Gỡ khỏi registry và DDL (có tên trong `dropped_columns_confirmed`) | Thêm lại vào DDL và registry. `json_path` = `nationalPhoneNumber`, string, `src_object` `$`, `is_active = true`. Không áp định dạng. Extract chỉ lấy đường dẫn và cast |
| `slv_3p_poi_media` | `blob_url` | Gỡ khỏi registry và DDL theo Q4 (bảng nháp ghi tắt, Q4 thay thế) | Giữ trong DDL và registry, `is_active = true`, không đặt `json_path`. Giá trị là null cho đến khi người dùng nêu trường nguồn. Không tắt cột |
| `slv_3p_poi_media` | `photographer` | Gỡ khỏi registry và DDL theo Q4 (bảng nháp ghi tắt vì cần rule chọn phần tử trong `authorAttributions[]`) | Giữ trong DDL và registry. `json_path` = `authorAttribution.displayName`, string, `src_object` `photos`, `is_active = true` |
| `slv_3p_poi_review` | `is_visible` | Chưa có | Thêm cột BOOLEAN dùng làm soft delete cho review. Không có `json_path`. Không thêm cột hash |

Các cột còn lại của ba bảng giữ nguyên. Riêng `slv_3p_poi_contact.phone_raw` vẫn bị gỡ như quyết định cũ.

## ctrl_cfg_schema_registry

Các dòng mới hoặc dòng được giữ lại cần có trong `TABLE_CONFIGS_3P` của `notebooks/NB_CREATE_DDL.ipynb`, theo kiểu tạo lần đầu như Q4.

| `trg_tbl` | `col_name` | `json_path` | `src_object` | `data_type` | `convert_rule` | `is_active` |
|---|---|---|---|---|---|---|
| `slv_3p_poi_contact` | `phone` | `nationalPhoneNumber` | `$` | string | không có | `true` |
| `slv_3p_poi_media` | `blob_url` | không có | `photos` | string | không có | `true` |
| `slv_3p_poi_media` | `photographer` | `authorAttribution.displayName` | `photos` | string | không có | `true` |
| `slv_3p_poi_review` | `is_visible` | không có | `reviews` | boolean | không có | chờ câu hỏi dưới |

`ctrl_mng_pipeline_config` không đổi. `slv_3p_poi_review` vẫn là `DOC_ARRAY`, khoá vẫn là `review_id`.

## Ràng buộc cho Architect

- `blob_url`: dòng registry bật nhưng không có `json_path`. Architect cần xác nhận extract ghi NULL cho dòng này mà không tính vào `cast_null` và không fail run. Nếu extract hiện tại chưa xử lý được dòng bật mà không có `json_path`, Architect nêu cách xử lý trong `architecture.md`. Không tự đặt đường dẫn.
- `photographer`: theo task gốc, tên người đăng của ảnh nằm trong mảng `photos[].authorAttributions[]`. Đường dẫn `authorAttribution.displayName` mà người dùng nêu là dạng số ít. Architect cần kiểm lại với `evidence/payload-pair-comparison.md` trước khi chạy. Nếu đường dẫn không trả giá trị trên phần tử `photos[]` thì cột sẽ null trên mọi dòng. Khi đó cần báo lại người dùng, không tự thêm rule chọn phần tử.
- `phone`: task gốc ghi chuỗi `phone` của normalized cũ khác định dạng `nationalPhoneNumber`. Người dùng chấp nhận lấy thẳng `nationalPhoneNumber`. Giá trị mới sẽ khác giá trị cũ trong backup.

## slv_3p_poi_review.is_visible

- Extract không xoá vật lý dòng review. Review vắng trong `reviews[]` của lần crawl mới không bị DELETE khỏi `slv_3p_poi_review`. Nhánh MERGE chỉ insert và update.
- Không cần cột hash cho soft delete này. Dòng review đã có khoá `review_id` (`HASH_SHA256`). Cờ `is_visible` chỉ là một cột BOOLEAN được MERGE cập nhật theo khoá đó, không cần hash riêng.
- Người dùng chưa nêu trường nguồn và chưa nêu điều kiện đặt `false`. Đề xuất này không tự đặt điều kiện, không đặt giá trị mặc định, và không đặt `json_path`.

## Câu hỏi

- Q-VIS: `slv_3p_poi_review.is_visible` lấy giá trị từ đâu và khi nào thì là `false`? Cụ thể: (a) đó là một trường trong `reviews[]` của `raw_payload` (nêu tên trường), hay (b) extract tự tính khi một `review_id` đã có trong bảng nhưng không còn trong `reviews[]` của tài liệu mới nhất cùng `poi_id`, hay (c) một điều kiện khác? Review mới chưa có điều kiện nào thì nhận `true` hay null?

## Quyết định Q-VIS (2026-10-14)

Người dùng chọn (b).

- `is_visible = false` khi `review_id` còn trong `slv_3p_poi_review` nhưng không còn trong `reviews[]` của tài liệu mới nhất cùng `poi_id`.
- `is_visible = true` khi `review_id` có trong `reviews[]` của tài liệu mới nhất đó, kể cả review mới được insert.
- Không đặt null. Không có `json_path`. Không thêm cột hash. Extract không `DELETE` dòng review.
- Dòng registry `slv_3p_poi_review` / `is_visible`: `is_active = true`, `data_type` boolean, không có `json_path`. Giá trị do extract tính, không lấy từ một trường nguồn.
- Hệ quả đã biết từ task `20261013-3p-extract-from-raw-payload`: lần full reload DEV nhận 265 sự kiện review và insert 85 khóa, bằng 17 POI nhân 5 review. `reviews[]` của tài liệu mới nhất là cửa sổ review hiện có, không phải toàn bộ lịch sử. Review rơi khỏi cửa sổ đó sẽ thành `is_visible = false`. Người dùng đã chọn (b) với điều kiện này.

## Ghi nhận architecture round 1

Round 1 trả `EVIDENCE_REQUIRED`. `phone`, `blob_url`, và `is_visible` đã được thiết kế. `photographer` chờ P7.

`is_visible` không có `json_path`. Cơ chế giao đúng nghĩa đó là rule `LATEST_DOC_FLAG`. Rule này không đọc trường nguồn.

## Quyết định nguồn và blob_url (2026-10-14)

Người dùng chốt trước khi chạy P7:

- Extract 3P đọc `normalized_payload` của `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`. Cột này đã được sửa thành cùng nội dung với `raw_payload`, và có thêm `blob_url`. Không đọc `raw_payload`.
- `slv_3p_poi_media.blob_url` lấy field `blob_url`. Ba object trong sample ngoài repository có khóa `photos[].blob_url`, kiểu string. Sample không phải hợp đồng schema. P7 đếm khóa này trên DEV.
- Quyết định cũ “`blob_url` giữ null, không `json_path`, rule `CONST_NULL`” bị thay bởi dòng này. `is_visible` vẫn không có `json_path` và vẫn dùng `LATEST_DOC_FLAG`.
- `photographer` vẫn là `authorAttribution.displayName` cho đến khi có số đếm P7. Ba object sample có `photos[].authorAttributions` là array, không có khóa số ít `photos[].authorAttribution`. `reviews[].authorAttribution` vẫn là object.

## Kết quả P7 (2026-10-14)

Fabric DEV có 81/81 tài liệu Google với `normalized_payload` không rỗng và 280 phần tử ảnh.

- `photos[].blob_url`: khóa có trên 280/280 ảnh; giá trị khác null trên 140/280. Cột `slv_3p_poi_media.blob_url` dùng `json_path = blob_url`, string, `is_active = true`. Null trên 140 ảnh còn lại là dữ liệu nguồn hợp lệ.
- `photos[].authorAttribution.displayName`: 0/280. Đường dẫn số ít người dùng nêu không tồn tại trên DEV và không được dùng im lặng.
- `photos[].authorAttributions[0].displayName`: 280/280. Mỗi ảnh có đúng một phần tử `authorAttributions`.

P7 đủ để đóng evidence về shape, nhưng cần người dùng chọn disposition cho `photographer` trước architecture round 2:

1. dùng phần tử đầu tiên của `authorAttributions[]`;
2. giữ đường dẫn số ít và chấp nhận `photographer` luôn null;
3. lưu cả `authorAttributions` dưới dạng JSON thay vì cột `photographer`.

## Quyết định photographer sau P7

Người dùng chọn phương án 1 ngày 2026-10-14:

- `slv_3p_poi_media.photographer` lấy `authorAttributions[0].displayName`.
- Đây là phép chọn phần tử đầu tiên của mảng, không phải đường dẫn số ít `authorAttribution.displayName`.
- P7 chứng minh trên Fabric DEV: 280/280 ảnh có giá trị tại phần tử đầu tiên và mọi `authorAttributions` có size 1.
- Architect quyết định cơ chế registry-driven tổng quát; Main không hard-code riêng Google trong extract.

## Ngoại lệ Main đã thu hồi

Người dùng đã thu hồi `EXC-MAIN-GPT-20261014` ngày 2026-10-14. Main quay lại Grok 4.7, effort `medium`. Phần công việc đã thực hiện bằng `gpt-5.6-sol` trước thời điểm thu hồi vẫn được giữ trong lịch sử task.

## Cơ chế triển khai theo architecture PASS

- Nguồn extract là `normalized_payload`.
- `phone` dùng `nationalPhoneNumber`; `blob_url` dùng `blob_url`.
- `photographer` dùng rule registry-driven `ARRAY_AT` với
  `{"index":0,"take":"displayName"}` trên `authorAttributions`.
- `is_visible` dùng rule không path `LATEST_DOC_FLAG`. Extract dựng anchor từ
  tài liệu applicable mới nhất, update cờ và stamp nhưng không `DELETE`.
- Registry sau seed: 9 bảng, 56 cột active, 11 `convert_arg` khác null, đúng
  một `json_path` null (`is_visible`).
- Source switch chạm cả chín bảng, nên DEV backfill cả chín sau khi P9 pass.

## User acknowledgment còn mở

- `UA-VIS1`: người dùng không chấp nhận ngày 2026-10-14. Xem mục
  `Rút is_visible`.
- `P9`: bất kỳ gate count nào khác 0 đều dừng rollout để người dùng quyết định.
- Gold 15P tiếp tục tắt.

## Rút is_visible (2026-10-14)

Người dùng không chấp nhận `UA-VIS1`. Bỏ `is_visible` khỏi task này. Phần soft
delete sẽ được đánh giá và làm ở task khác.

- Không thêm `slv_3p_poi_review.is_visible`. Không seed `LATEST_DOC_FLAG`.
- Extract không soft-hide và không `DELETE`. Review rời cửa sổ `reviews[]` vẫn
  được giữ, đúng upsert hiện tại.
- Registry còn 9 bảng, 55 cột, 0 cột tắt, 11 `convert_arg` khác null, không còn
  `json_path` null.
- `phone`, `blob_url`, `photographer` với `ARRAY_AT`, và nguồn
  `normalized_payload` giữ nguyên.
- Lệch architecture round 2: invariant visibility và cột `is_visible` ra khỏi
  phạm vi. Architecture đã dùng hết 2 round nên không gọi Architect lại.
- Review round 2 pass trên bản còn soft delete. Sau khi gỡ, review đó không còn
  phủ code hiện tại. Review cap là 2 nên không chạy round 3.
- `python scripts/vv.py verify` ngày 2026-10-14 pass sau khi gỡ. Pytest 57 pass.

## Chấp nhận tiếp tục không review round 3 (2026-10-14)

Người dùng: "Đồng ý Main ghi nhận, đặt specialist_review và risk_gate thành pass".

Review cap vẫn là 2. Không chạy review round 3. `specialist_review` và `risk_gate` thành `pass` theo quyết định này, cho phần còn lại sau khi rút `is_visible`. Bước kế tiếp là P9 trên Fabric DEV. Không deploy khi P9 chưa pass.

## P9 không pass (2026-10-14)

Fabric DEV, `source_name = google`, 81 tài liệu. File `evidence/results/P9_payload_parity.md`.

| docs | norm_blank_when_raw_ok | top_mismatch_docs | photo_size_mismatch_docs | photo_elem_mismatch | photo_no_blob_key | blob_signed |
|---:|---:|---:|---:|---:|---:|---:|
| 81 | 0 | 53 | 53 | 0 | 0 | 0 |

`top_mismatch_docs` và `photo_size_mismatch_docs` khác 0. P9 fail. Không deploy. `normalized_payload` không khớp `raw_payload` cộng `blob_url` trên 53 tài liệu. Phần tử ảnh cùng vị trí, sau khi bỏ `blob_url`, không lệch (`photo_elem_mismatch = 0`). Không có URL có chữ ký (`blob_signed = 0`).

Câu tên khóa cùng ngày: 39 khóa lệch trên đúng 53 tài liệu, gồm cả tên kiểu cũ (`poi_name`, `poi_address`, `poi_contact`, `poi_review`, `poi_media`, `poi_id`) và tên Google (`displayName`, `reviews`, `id`, `formattedAddress`, `location`). Khóa tùy chọn thấp hơn: `parkingOptions` 51, `nationalPhoneNumber` và `internationalPhoneNumber` 50, một số cờ giờ mở cửa và tiện ích 48. Câu này không cho biết khóa nằm ở `raw_payload`, `normalized_payload`, hay cả hai. Không deploy.

Người dùng yêu cầu xóa bronze DEV có `ingested_date` trước `2026-10-14`, vì nghi dữ liệu cũ gây lệch. Đếm trước khi xóa: `google`, `rows_all = 83`, `rows_to_delete = 53`, `null_or_unparsed = 0`. Số 53 trùng `top_mismatch_docs` lúc đó. Người dùng đã xóa. Version Delta không được gửi. P9 chạy lại: `docs = 30`, `norm_blank_when_raw_ok = 0`, `top_mismatch_docs = 2`, `photo_size_mismatch_docs = 2`, `photo_elem_mismatch = 0`, `photo_no_blob_key = 0`, `blob_signed = 0`. P9 vẫn fail. Câu tên khóa sau xóa trả 49 khóa: 42 khóa lệch trên cả 2 tài liệu, gồm lại tên kiểu cũ (`poi_name`, `poi_id`, `poi_contact`, `poi_review`, `poi_media`) và tên Google (`displayName`, `reviews`, `id`, `nationalPhoneNumber`, `websiteUri`). Bảy khóa lệch trên 1 tài liệu: `currentOpeningHours`, `poi_opening_hours`, `delivery`, `paymentOptions`, `regularOpeningHours`, `restroom`, `accessibilityOptions`. Câu vẫn không cho biết khóa nằm phía nào. Không deploy.

Người dùng xử lý 2 tài liệu lệch và chạy lại P9. Kết quả pass: `docs = 41`, `norm_blank_when_raw_ok = 0`, `top_mismatch_docs = 0`, `photo_size_mismatch_docs = 0`, `photo_elem_mismatch = 0`, `photo_no_blob_key = 0`, `blob_signed = 0`. Được phép deploy DEV. Backfill ghi silver chỉ sau dry_run pass.

Baseline trước backfill: watermark `last_src_version = 13`, `watermark_value = 2026-10-09T06:50:58Z`, lock null. State 17 dòng mỗi bảng trong chín bảng. Reject chưa giải quyết = 0. Seed `show_registry`: 9 bảng, 55 cột, 0 cột tắt. Review 7 cột, không có `is_visible`. Media có `photographer:ARRAY_AT`. Contact 4 cột. Chưa có dry_run.

Partner dry_run và 3P dry_run đều pass ngày 2026-10-14. Partner `NO_DATA`, `exec_id` `edd337c6-103f-447b-b99b-db6e4e365cbf`. 3P `SUCCESS`, `exec_id` `e96c3411-9d2b-48d9-8fe3-0c161d0fc2f4`, 41 tài liệu hợp lệ, `cast_null = 0`, `bad_shape` rỗng. Được backfill.

Backfill lần một pass: `exec_id` `b6f1f697-7be1-4373-b261-70d82b05e14c`, `SUCCESS`, 9/9, `inserted = 890`, `updated = 12`, `cast_null = 0`. Backfill lần hai: người dùng xác nhận `ins = 0`. Incremental: người dùng xác nhận thành công. Đối chiếu: khóa unique, `phone_diff = 0`, `blob_diff = 0`, `photographer_diff = 0`, reject 0, lock null. `no_oracle = 530` là media cũ còn lại vì MERGE không xóa; 410 dòng mới khớp oracle. Spark đọc lại watermark: `last_src_version = 22`, `watermark_value = 2026-10-14T10:38:15Z`, lock null. History `slv_3p_poi`: baseline version 1 (17 dòng, `2026-10-13T19:10:29Z`); backfill là version 2 (`2026-10-14T13:02:43Z`, insert 40, update 1, copied 16, deleted 0). P11 pass ngày 2026-10-14: chín bảng `diffs = 0`, `lost_keys = 0`, baseline version 1. Gate `runtime` pass trên DEV. Người dùng yêu cầu commit và push `main` ngày 2026-10-14. Prod chưa chạy.

## Review round 1

Review dùng `gpt-5.6-sol`, effort `medium`; đã chạy
`state-correctness-reviewer`, `sql-data-reviewer`, `spark-runtime-reviewer` và
`risk-gate`. Verdict `EVIDENCE_REQUIRED`.

- `GATE-001` P1: cần chứng minh không có nhóm cùng toàn bộ tuple thứ tự
  `(source_name, source_id, crawled_at, event_id)` nhưng khác
  `normalized_payload`.
- `GATE-002` P1: cần chứng minh target không có `review_id` trùng.

P10 trên Fabric DEV ngày 2026-10-14:

| ambiguous_order_groups | duplicate_target_review_id_groups |
|---:|---:|
| 0 | 0 |

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | P10: `ambiguous_order_groups = 0`. Không có nhóm cùng `(source_name, source_id, crawled_at, event_id)` mà khác `normalized_payload` | |
| GATE-002 | P1 | fixed | P10: `duplicate_target_review_id_groups = 0`. `slv_3p_poi_review.review_id` không trùng | |
