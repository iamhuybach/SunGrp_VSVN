# 99 — Pain point, root cause, vấn đề gặp phải (01/10 → 08/10/2026)

> Cập nhật: 08/10/2026. Gom từ: `claude/REVIEW_EXTRACT_PROD_0410.md`, `claude/POI_3P_EXTRACT_REDESIGN.md` §2.4 / §5.8, `claude/PARTNER_EXTRACT_REDESIGN.md`, `claude/CTRL_TABLES_CONTEXT.md` §8, `claude/GOLD_POI_FLOW_DESIGN.md` §9a / §9b / §12.2, `PATCH_REVIEW_0510.md`, kết quả các script CHECK / DIAG.
> Trạng thái: **Đã xử lý** · **Đang mở** · **Chờ bên ngoài** (team nguồn / collector / CMS) · **Chấp nhận** (biết, không sửa).

## 0. Bài học chính (đọc trước)

| # | Bài học | Xuất phát từ |
|---|---|---|
| 1 | **Không suy đoán dữ liệu**: đối chiếu payload thật bằng script chỉ đọc trước khi chốt cấu hình | NB_20 cũ đoán sai khoá nhiều khối → 36 cột luôn NULL; `dedup_order` content dùng 3 trường không có trong payload; khoá `order_item_tickets` sai làm mất vé |
| 2 | **Đọc theo version Delta, không theo thời gian** | Raw do Eventstream ghi không có stats; lọc theo thời gian vừa quét cả bảng vừa bỏ sót event commit trễ |
| 3 | **Con trỏ chỉ được tiến khi đã đọc đủ**; thiếu dữ liệu thì dừng (FAILED), không tự đọc kiểu khác rồi tiến tiếp | `VersionGapError` thay chuyển sang TIME; C2 (tham số âm làm run "SUCCESS" mà không xử lý gì) |
| 4 | **Khoá phải nguyên tử và có hạn do chính người giữ ghi** | Khoá bằng run log không nguyên tử; review 05/10 #1: chạy tay (90') lấy được khoá NB_00 (126') |
| 5 | **Timeout activity < hạn khoá**, retry activity = 0 | H1: run "xác sống" có thể commit sau run mới |
| 6 | **Rule là dữ liệu, gold không có logic** | Rule viết cứng ở 2.1 / NB_20 / NB_40 / NB_50; 2 notebook ghi cùng `poi_master` bằng 2 logic |
| 7 | **Kết quả phải xác định** (cùng đầu vào → cùng `row_hash`) | Review #7: `first()` sau `groupBy` không có thứ tự → hash đổi thừa mỗi lần chạy |
| 8 | **Code mới chưa được tin cho tới khi chạy kiểm chứng**; test local giả lập Delta không thay được chạy trên Fabric | Maven / Delta bị chặn ở máy test → version, history, MERGE, runMultiple chỉ giả lập |

## 1. Nền tảng Fabric

| # | Vấn đề | Root cause | Ảnh hưởng | Xử lý / Trạng thái |
|---|---|---|---|---|
| F1 | Lọc raw theo `EventProcessedUtcTime` quét cả bảng: đọc 1.588 dòng mất 231 s | Eventstream ghi Delta **không có stats** (`add.stats = NULL`, 20.431 file / 3,2 GB lúc đo 02/10) → không data skipping | Extract chậm dần theo kích thước raw | **Đã xử lý** 02/10: đọc `_delta_log/<v>.json`, lấy file `add` của commit mới, đọc parquet trực tiếp |
| F2 | `DeltaTable.history()` của raw có `operation` NULL (18.544 commit) | Raw do Eventstream (không phải Spark) ghi | Không phân biệt được commit đổi dữ liệu với commit khác ở raw | **Chấp nhận**: lib gold coi `operation` NULL là "có đổi" (an toàn); đầu vào của DAG đều do Spark ghi |
| F3 | Không có quyền tạo Service Principal | Chính sách tổ chức | Không gọi REST API Fabric / SQL endpoint bằng danh tính ứng dụng | **Chấp nhận**: precheck bằng Get Metadata trên shortcut `Files/_delta_src/<src_tbl>` đọc `_delta_log`, không dùng SPN |
| F4 | Precheck bằng UDF / notebook Python tốn khởi động Spark, phụ thuộc SQL endpoint (lag) | Cách cũ | Mỗi lần kiểm tra "có dữ liệu mới" tốn như 1 lần chạy | **Đã xử lý**: Get Metadata + Filter tên file log > `last_src_version`. Giới hạn: commit bảo trì (OPTIMIZE / auto compaction) cũng sinh file log → vẫn gọi notebook, notebook trả NO_DATA rẻ |
| F5 | Xoá file / thư mục **bên trong** shortcut = xoá dữ liệu thật của bảng nguồn | Shortcut OneLake trỏ thẳng dữ liệu | Rủi ro mất raw | **Quy tắc**: chỉ xoá shortcut, không xoá gì bên trong |
| F6 | Spark Runtime 1.3 đã có thông báo hết hỗ trợ; mặc định dự kiến sang 2.0 (ANSI, Delta 4.2, Python 3.13) `[VERIFY]` | Vòng đời runtime | Notebook có thể tự chạy trên 2.0 nếu không gắn Environment | **Đang mở** (M8): gắn Environment cố định runtime; kế hoạch test 2.0 riêng. Lib extract đã có `CAST_FN` (TRY_CAST khi ANSI bật) |
| F7 | F16 dùng chung: 2 session extract lúc wave = 32 VCore = mức cơ sở F16; mỗi Notebook activity khởi động 1 session riêng | Capacity nhỏ, nhiều tải | Luồng 1H và extract tranh tài nguyên | **Đang mở** (M9): high concurrency + session tag chung `[VERIFY]`; lịch 1H lệch đỉnh extract |
| F8 | Không có OPTIMIZE / VACUUM ở đâu; 7 bảng ctrl không bật `optimizeWrite` / `autoCompact` | Chưa có notebook bảo trì | ~100 run / ngày × 7–8 commit ctrl → file nhỏ tăng, MERGE ctrl chậm dần; file cũ không dọn | **Đang mở** (M6): notebook bảo trì hằng tuần, VACUUM ≥ 7 ngày, không chồng FL_00; không VACUUM raw < 7 ngày |
| F9 | `SHOW SCHEMAS` lỗi do cách Fabric đặt tên | Đặc thù Fabric | Không liệt kê schema bằng SQL | **Chấp nhận**: schema gold = `dbo` (xác nhận bằng bảng cũ) |
| F10 | runMultiple: tên trường, hành vi khi cha lỗi, exit value khi DAG lỗi chưa chắc | Tài liệu chưa rõ, chưa chạy thử | NB_00 có thể đọc sai kết quả | **Giảm rủi ro**: NB_00 đọc kết quả node từ `ctrl_log_table_run`, chịu được cả 2 cách bỏ qua node con; còn `[VERIFY]` tên trường |
| F11 | Test local không có Delta (Maven 403 qua proxy) | Môi trường test bị chặn mạng | Version, history, MERGE, runMultiple chỉ giả lập | **Chấp nhận**: Spark local + harness giả lập; mọi `[VERIFY]` phải chạy ở dev |
| F12 | Project Claude giới hạn ~2 triệu token | Nhiều notebook `.ipynb` lớn | Không ghi thêm tài liệu được | Nén JSON `.ipynb`; dọn tài liệu cũ (`seed_ctrl_poi_3rd_party.sql`, `DOC_MAP_0410.diff`, `RESULT_RERUN_0410.py`, `APPLY_3P_CONFIG_0410.sql`, `NB_EXTRACT_PARTNER_CDC.ipynb`) — **chờ anh Hòa đồng ý xoá** |

## 2. Dữ liệu nguồn

| # | Vấn đề | Root cause | Ảnh hưởng | Trạng thái |
|---|---|---|---|---|
| D1 | `after = ''` ở 100% event 10 bảng `product*` (199.408 event, mỗi event khác nhau) + 10 event `order_item_*` | Upstream (Debezium / Eventstream) gửi payload rỗng, bắn lại theo chu kỳ | 10 bảng `slv_pn_product*` reject 100%; `ctrl_cdc_reject` partner ~199k dòng, tăng mỗi run | **Chờ bên ngoài**: team nguồn sửa rồi snapshot lại |
| D2 | Update storm: >99,9% raw là update lặp y hệt (`hotel_room_types` 341.204 event / 203 dòng / 238 payload khác nhau; `hotel_rate_plans` 274.630 / 162 / 177; `orders` 26.253 / 28 / 43; `business_service_i18ns` 643k / 344) | Job đồng bộ phía Postgres ghi lại cả bảng theo chu kỳ | Raw phình, extract xử lý thừa; MERGE partner cập nhật vô điều kiện → silver ghi lại liên tục (M5) | **Chờ bên ngoài**: đề xuất `suppress_redundant_updates_trigger()` / `ON CONFLICT … WHERE`; phía mình: M5 thêm điều kiện so giá trị |
| D3 | Raw 3P không nhận dữ liệu từ 16/09, raw partner từ 17/09 | Collector / Eventstream dừng | Không đo được nhịp commit thật, không test incremental thật | **Chờ bên ngoài** |
| D4 | Silver partner mới chỉ có 24 service, `poi_master` cũ 186 (162 thiếu) | Raw `business_services` chỉ 16 `c` + 57 `u` của 24 id, **không có `r`** (không snapshot ban đầu) | 162 POI partner không lên gold mới | **Chấp nhận** (OD-G13: môi trường dev, không bổ sung) |
| D5 | `order_item_*` không có cột `id`; khoá `hotels` / `flights` chưa rõ (`order_id` hay `order_ref_id`, `segment_id`) | Schema nguồn chưa xác nhận | Khoá sai làm mất dòng (đã xảy ra với `tickets`: 1 đơn nhiều vé) | `tickets` → `order_ref_id` **đã sửa**; K1 **chờ bên ngoài** |
| D6 | Event xoá chỉ có PK trong `before` (REPLICA IDENTITY DEFAULT) | Cấu hình Postgres | Bảng có khoá silver khác PK: event xoá bị reject, dòng không đánh dấu `deleted` (H2) | **Chờ bên ngoài**: xin PK + replica identity 23 bảng (hiện chỉ 2 event xoá) |
| D7 | Cột TOAST: Debezium gửi `__debezium_unavailable_value` khi giá trị lớn không đổi | Cơ chế TOAST của PostgreSQL | Notebook cũ `COALESCE` → cột bị xoá trắng thật ở nguồn vẫn giữ giá trị cũ | **Đã xử lý** 03/10: cờ `_unavailable__`, `_has_value__`, MERGE `CASE WHEN` |
| D8 | Decimal Debezium dạng base64 của số nguyên chưa chia scale | `decimal.handling.mode = precise` | Cast thẳng ra NULL / sai | **Đã xử lý**: `DECIMAL_BASE64` (hàm Spark thuần, tới 15 byte) |
| D9 | 3P: category lộn xộn (`Café` / `Cafe`, NULL), sector viết sai `accomodation` (221–250 dòng) | Dữ liệu crawl / model gán | Phân loại sai ở gold | **Đã xử lý một phần**: `ref_business_category` seed mọi cặp + sửa chính tả; đội sửa tay ref |
| D10 | 3P: `poi_group_id` NULL ở 17.097 dòng Google và 100% partner | Bản cũ tính khoá không ổn định | Không dùng được làm định danh | **Đã xử lý**: định danh theo (`source_name`, `source_id`) |
| D11 | 3P: 8.317 dòng raw (8.210 địa điểm) không có enrichment; lỗi dịch en 616, ko 373; 4.658 POI bản cũ có en / ko là **tên giả lập** (en = vi bỏ dấu, ko = vi) | Collector chưa enrich | Chỉ 58,1% POI 3P đủ vi + en + ko bằng tên thật | **Chấp nhận** (OD-G14b): cho phép tên giả lập như bản cũ (`FALLBACK_UNACCENT` / `FALLBACK_COPY`), `available_langs` chỉ tính lang có tên thật |
| D12 | 125 `event_id` trùng (cùng payload); 21 object enrichment có `poiId` UUID khác nhau theo ngôn ngữ; `enrichmentId` đổi mỗi event | Raw ghi lặp; ngữ nghĩa trường của collector chưa rõ | Không dùng làm khoá | **Chấp nhận**; hỏi collector nghĩa `poiId` |
| D13 | Content: 29 nhóm trùng khoá (`poi_id`, `locale`) | Khoá thiếu `content_type` | MERGE lỗi trùng khoá / mất dòng | **Đã xử lý** 04/10: khoá + `content_type`, lấy phần tử đầu (0 nhóm khác nội dung) |
| D14 | Khối `policies` luôn null; 36 cột cấu hình luôn null | NB_20 cũ đoán cấu trúc khối | Bảng / cột rỗng | **Đã xử lý**: tắt bảng `policy` + 36 cột (D1 04/10), bật lại khi collector điền |
| D15 | `business_service_poi_link` chỉ 1 dòng | Partner chưa link POI | Không đủ nhãn cho chấm điểm POI trùng | **Chấp nhận**; chấm điểm Splink không cần nhãn (EM) |
| D16 | Partner: `operation_status` rỗng cả 24 dòng; `district`, `state` rỗng; enrichment địa chỉ là lịch sử, 2 POI có 328 và 496 dòng | Dữ liệu nguồn / notebook 3.1 gọi lặp? | Phải suy `operating_status` từ `is_active` / `deleted`; lấy enrichment mới nhất | **Đã xử lý** ở N2 / N3; 328 / 496 dòng: **hỏi chủ notebook 3.1** |
| D17 | CMS có 10 tên / lang trùng 2 `documentId` (ảnh hưởng "Đà Nẵng") | Dữ liệu CMS | Destination id không duy nhất theo tên | **Chấp nhận**: lấy `MAX(documentId)` như 2.2; báo đội CMS rà |
| D18 | Phú Quốc nay thuộc tỉnh An Giang; "An Thới" → destination "Sunset Town" | Sáp nhập hành chính + rule cũ NB_40 | Rule đặc biệt phải theo dữ liệu mới | **Đã xử lý**: `ref_destination_special_rule` (2 dòng, chỉ `google`) |

## 3. Thiết kế / code cũ (lý do làm lại)

| # | Vấn đề | Ảnh hưởng | Thay bằng |
|---|---|---|---|
| O1 | **P0** NB_00 cũ cell 0: `DELETE FROM brz_watermark WHERE watermark_id = 'bronze_to_silver_gold_v2'` rồi tạo lại mốc 18/09 | Nếu chạy theo pipeline: mỗi run đọc lại từ 18/09, chậm dần | Watermark ctrl, chỉ tiến, có khoá |
| O2 | Watermark 3P `MAX(crawled_at)` không overlap | Tài liệu commit trễ bị bỏ sót vĩnh viễn | Đọc theo version |
| O3 | Tài liệu thiếu 1 trong vi / en / ko bị loại cả tài liệu, chỉ `print` | POI thiếu ko không vào silver, không log | Nhận mọi lang trong `langs`, quyết định đủ lang ở L2 (`has_required_langs`) |
| O4 | Tên 4 phần `sgr_visitvn_stg.*` viết cứng (NB_10/40/50/60) | Chạy dev nhưng đọc / ghi stg; deployment pipeline không đổi được | Tên đầy đủ trong ctrl / tham số |
| O5 | Khoá có lang ở bảng không theo ngôn ngữ | Address, contact… ghi 3 lần, có thể lệch; sinh sibling map (NB_50), luật tắt POI thiếu lang (NB_60) | Khoá `poi_id`; lang chỉ ở bảng bản địa hoá |
| O6 | Thiếu khối xử lý không thống nhất (address ghi NULL đè; contact / price giữ; content không xoá được; media / review không bao giờ tắt) | Dữ liệu không đoán được | Khối vắng = giữ cũ; `_last_seen_at` |
| O7 | Silver phụ thuộc gold (`poi_master.is_enrichable`, `destination_ward_mapping`); gold đọc chính gold (`COALESCE(t.rating, s.rating)`, `t.nearby_pois`) | Không tái lập được, vòng phụ thuộc | Gold chỉ chiếu từ silver; 2 ngoại lệ silver đọc gold cũ đang tạm, sẽ chuyển |
| O8 | Rule trong code: `_MAPPING`, UDF amenity, `AI_ENRICHED_POI_BUSINESS_CATEGORY_REMAP`, rule Phú Quốc, `SECTOR_CONFIG`, nhãn hiển thị | Đổi rule phải deploy | 5 bảng `ref_*` |
| O9 | `poi_master` grain POI × lang, `poi_id` có lang; 2 notebook (2.1 partner, NB_40 3P) ghi cùng bảng bằng 2 logic; MERGE cập nhật mọi dòng, `version + 1` mỗi lần | Thuộc tính lặp 3 lần có thể lệch; sync PG đẩy lại dòng không đổi | 3 bảng `gld_srv_poi_*` + MERGE `row_hash` |
| O10 | Partner cũ: `TABLE_CONFIGS` viết cứng; silver nằm ở `lh_vv_bronze.partner.*` | Thêm cột phải sửa code | Registry + `slv_pn_*` |
| O11 | Không chống chạy chồng (chỉ Concurrency pipeline), không reject / table log; stage là bảng Delta thật chỉ dọn khi thành công | Khó vận hành, khó truy lỗi | Khoá, `ctrl_cdc_reject`, `ctrl_log_table_run` |
| O12 | Slug cũ (2.1) bỏ hẳn ký tự không ASCII (`Phở` → `ph`); Google chỉ ~5k / lang có slug | Slug xấu, thiếu | Bỏ dấu đúng, cấp 1 lần (slug mới khác cũ 1 lần) |

## 4. Lỗi gặp và đã sửa khi làm

| # | Lỗi | Root cause | Sửa |
|---|---|---|---|
| E1 | INSERT watermark partner khai 16 cột nhưng 17 giá trị; bớt 1 giá trị thì từ `last_src_version` lệch cột (`lock_exec_id` nhận `'2026-09-29 …'`) | INSERT theo vị trí | 03/10: 1 INSERT liệt kê đủ 18 cột + `NOT EXISTS` |
| E2 | Công thức priority `FLOOR((seq-1)/12)+1` xếp `partners` chung wave với 11 bảng product | Công thức theo số thứ tự | 02–03/10: `CASE WHEN trg_tbl LIKE 'slv_pn_product%' THEN 2 ELSE 1 END` |
| E3 | Chạy lại cell seed nhân đôi dòng | INSERT không kiểm tra | `WHERE NOT EXISTS` / MERGE `WHEN NOT MATCHED` |
| E4 | 2 nguồn ghi chung bảng ctrl → `ConcurrentAppendException` | Delta optimistic concurrency, bảng không partition | Retry 6 lần + jitter; `PARTITIONED BY (src_tbl)` + điều kiện partition trong MERGE |
| E5 | Lần đầu / sau reset / raw tạo lại: không biết đọc từ đâu | Không có `last_src_version` | `VersionGapError` + `allow_full_scan`; `last_src_table_id` phát hiện tạo lại |
| E6 | C1: mất khoá vẫn báo SUCCESS; MERGE partner không chặn ghi lùi | `finalize_watermark` chỉ cảnh báo | Hạ Low nhờ Concurrency = 1 + timeout activity 45 < 60 (H1 đã sửa); tuỳ chọn 1 dòng đổi trạng thái |
| E7 | C2: `max_retries < 0` → vòng thử rỗng, bảng PENDING tính là thành công, watermark tiến | Không kiểm tra miền tham số; `decide_status` coi trạng thái lạ là OK | **Đang mở** ở lib extract (vá 1 chỗ trong `run_controlled`); NB_00 đã có `_validate_orch_params` |
| E8 | Review 05/10 #1: hạn khoá xét theo timeout của run đang xét → chạy tay (90') lấy được khoá NB_00 (126') | `_lock_expired_sql` trong `NB_LIB_TRANSFORM_SLV_GLD` vẫn là `lock_at < current_timestamp() - INTERVAL {timeout_min} MINUTES`. MERGE cạnh không có `EXISTS` và không ghi lùi version khi cùng table id | **Đang mở**. Notebook chưa ghi `LOCK_EXPIRES_AT` |
| E9 | Review #2: chốt version từng bảng chỉ ổn định trong 1 lần chạy; extract đang commit dở (10/23 bảng) → gold đọc trộn batch | Không biết batch extract | **Đang mở**. `plan_run` không ghim version trước batch extract dở. `VERSION_BACKWARD` chỉ đánh dấu cạnh bẩn; MERGE cạnh không ghi version nhỏ hơn khi cùng table id |
| E10 | Review #3: N5 ra 0 dòng (mapping hỏng) → xoá mềm hết membership trong khi registry giữ `primary_destination_id` cũ | QG chỉ chặn đầu vào rỗng (G10) | `block_empty_output` cho N5 |
| E11 | Review #4 / #5: `parent_dest_id` khác miền id với destination (CMS nhiều id cùng tên) → chuỗi cha đứt; id cha không có trong CMS → tổ tiên mồ côi | 2 cách lấy id | Đưa `parent_dest_id` về `MAX(documentId)` theo tên; không có trong CMS → cảnh báo + bỏ liên kết cha |
| E12 | Review #6: lang `is_required` mà `is_published = false` âm thầm hạ điều kiện đủ lang | Cấu hình ref mâu thuẫn | N4 chặn |
| E13 | Review #7: `model_business_sector` / `model_type` lấy `first()` sau `groupBy`, thứ tự tính rồi bỏ | Hàm không xác định | Window có sắp thứ tự (lang gốc → lang a-z) |
| E14 | Đánh giá sai ban đầu về `is_recommended`: tưởng nhiều POI mất cờ | Đọc nhầm NULL thành true | Thực tế 10.663 dòng NULL → false, chỉ 9 POI true → false (OD-G9 / G15) |
| E15 | Test local: mốc batch so với giờ commit giả lập lệch | Đồng hồ giả lập | Dùng `lake_now()` theo commit giả lập |
| E16 | Thiết kế DOC_MAP (bảng key-value cho JSON) viết + test xong rồi gỡ | Quyết định 04/10 giữ JSON nguyên khối, transform sau | Diff lưu `claude/DOC_MAP_0410.diff` (không dùng) |

## 5. Hiệu năng

| # | Vấn đề | Root cause | Trạng thái |
|---|---|---|---|
| P1 | Chi phí cố định chiếm 42% (partner) / 55% (3P) lần FULL; incremental còn cao hơn | 7–8 commit ctrl + ~9 query + ~8 lần tra catalog tuần tự (chờ metadata, 0–3 core bận) | **Đang mở** (M2): gộp UPDATE watermark + nhả khoá, cache kiểm tra cột, bỏ đọc khoá trước UPDATE |
| P2 | Mỗi bảng 40–57 s kể cả bảng 1 dòng | Wave 12 luồng tranh 16 core (CPU bão hoà) | **Đóng** (M1): giới hạn bởi CPU; giảm `max_parallel` không nhanh hơn |
| P3 | 3P FULL: đọc + parse 1 task | Raw đọc thành ~1 partition | **Đang mở** (Low): `repartition` sau khi đọc FULL |
| P4 | 3P `max_parallel` 12 < 13 bảng → `review_i18n` chạy lượt 2 một mình | Tham số | Đặt ≥ 13 |
| P5 | `load_state` đọc state cả 2 nguồn | Lọc `concat_ws` không cắt partition | **Đang mở** (M3): lọc `src_tbl` + `trg_tbl IN` |
| P6 | MERGE reject theo `event_hash` quét cả partition | Khoá băm ngẫu nhiên | **Đang mở** (M4): thêm khoảng `cdc_ts_ms`; hạn giữ reject |
| P7 | Skew job (max 96 MB / mean 4,4 MB) ở bảng nhiều event / entity khi FULL | Shuffle theo `_entity_key` | **Chấp nhận**: incremental không đáng kể |
| P8 | NB_00 lập kế hoạch ~93 s | `table_state` + history ~24 bảng tuần tự | **Đang mở**: song song / cache |
| P9 | 2 session extract chạy chồng = 32 VCore khi FULL | Mỗi activity 1 session | M9 |

## 6. Kết quả gold run 1 (05/10) cần xử lý

| # | Hiện tượng | Nguyên nhân | Trạng thái |
|---|---|---|---|
| R1 | Registry 19.066 / N1 19.070 POI | 4 POI partner không có tên vi → không đủ lang bắt buộc (G6) | **Chấp nhận** theo G6 |
| R2 | ~42% tên en / ko là tên giả lập; `available_langs` nhiều POI không đủ 3 lang | `available_langs` chỉ tính lang có tên **thật**; tên giả lập vẫn lên multi_lang (G14b) | **Theo thiết kế**; giải thích ở `01_DATA_MODEL.md` |
| R3 | ~1,8k POI `business_category` NULL | Root cause C1 chưa chốt (`CHECK_GOLD_POI_RUN1C_0510.py`) | **Đang mở**: chờ output |
| R4 | 36 POI mất destination so với bản cũ | Root cause C2 chưa chốt (cùng script) | **Đang mở** |
| R5 | 683 POI khác destination so với bản cũ | Liên quan rule đặc biệt / mapping mới (Phú Quốc → An Giang, `MAX(documentId)`) | **Đang đối chiếu** |
| R6 | 153 / 19.046 địa chỉ 3P không khớp mapping (ward, city) | Ward / tỉnh sau sáp nhập, chuỗi địa chỉ lạ | Cảnh báo ở QG N5 |
| R7 | 27 dòng (9 POI) Google `is_recommended = true` cũ sẽ thành false; 9 `is_bookable` thành NULL | OD-G9, G7 | **Chấp nhận** |

## 7. Quy trình làm việc

| # | Vấn đề | Cách làm hiện tại |
|---|---|---|
| W1 | Từ ngữ khó hiểu ("cạnh bẩn", "hộp thư") | Đề xuất đổi: "liên kết đầu vào", "liên kết cần xử lý", "node cần tính lại", "dấu đã đọc" — **chưa chốt** |
| W2 | Nhiều bản notebook cùng chức năng (bản 1 file `NB_EXTRACT_PARTNER_CDC`) | Bản hiện hành là cặp lib + notebook nguồn; bản cũ không dùng |
| W3 | Sửa nhiều chỗ trong notebook dễ sót | Sửa ít → chỉ chỗ cần sửa (diff); sửa nhiều → thay cả notebook (import `.ipynb`), deploy lib trước |
| W4 | Không chắc dữ liệu | Viết script CHECK / DIAG chỉ đọc, anh Hòa chạy trên Fabric, gửi output, rồi mới quyết |
| W5 | Thay đổi phải truy được | Đánh dấu `[SỬA dd/mm]`, `[05/10 review #n]`; tài liệu "Lịch sử thay đổi" ở `CTRL_TABLES_CONTEXT.md` |
| W6 | Ràng buộc phải giữ | Không SPN; không xoá file trong shortcut; giữ `poi_*` cũ + chuỗi NB_00 cũ tới cutover; 1 notebook xử lý / nguồn; không viết cứng; gold chỉ đồng bộ, silver giữ logic |

## 8. Việc mở gom lại (ưu tiên)

| Ưu tiên | Việc | Chủ |
|---|---|---|
| 1 | Output `CHECK_PIN_EXTRACT_0510.py` (múi giờ) trước khi tin ghim theo batch extract | Anh Hòa chạy |
| 1 | Output `CHECK_GOLD_POI_RUN1C_0510.py` (R3, R4) + log NB_00 lần 2 (NO_DATA, OPTIMIZE) | Anh Hòa chạy |
| 1 | Vá C2 trong lib extract | Dev |
| 2 | `CHECK_CTRL_SNAPSHOT.py` → cập nhật số liệu ctrl | Anh Hòa chạy |
| 2 | Notebook bảo trì Delta (M6), gắn Environment runtime (M8) | Dev |
| 2 | M2–M4 (điều khiển, state, reject) | Dev |
| 3 | `after` rỗng, update storm, K1, H2, raw dừng | Team nguồn / collector |
| 3 | Đối chiếu song song 2 tuần với `poi_master` cũ trước khi chuyển sync PG | Dev + anh Hòa |
