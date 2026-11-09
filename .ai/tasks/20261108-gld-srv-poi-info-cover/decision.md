# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Ảnh cover trên dòng POI info | Thêm `cover_id` và `cover_blob_url` vào `lh_vv_gold.dbo.gld_srv_poi_info` và `apps.srv_poi_info` trong cùng một task. `cover_id` lấy từ `slv_poi_media_info.media_id`. `cover_blob_url` lấy từ `slv_poi_media_info.blob_url`. LEFT JOIN `slv_poi_media_info`. POI không có cover vẫn giữ một dòng `gld_srv_poi_info`; hai cột mới để null. Chọn đúng dòng cover mà `gld_srv_poi_media_gallery` đang dùng qua `is_cover`. Gallery là bản 1-1 của `slv_poi_media_info`; `is_cover` đã tính trên silver (`with_cover`), không tính lại trong gallery. Dùng dòng `is_cover` đó. Không viết rule cover thứ hai, không đổi rule `is_cover`, không đổi grain một dòng `poi_id`. | request.md ## User outcome | 2026-11-08 |
| D-02 | Mở rộng scope.files | Thêm `tests/test_gld_srv_poi_contract.py`, `tests/test_initial_ddl_contract.py`, `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py` vào `scope.files`, rồi implement theo edit list. | architecture.md Main brief Order and stop points bước 1 | 2026-11-09 |
| D-03 | Chạy rollout | Người dùng yêu cầu chạy hết rollout trong `architecture.md` mục `## Rollout`. Lần ghi gold là `NB_00_ORCHES_SLV_TO_GLD` với `p_pl_name=PL_VV_TRANS_SLV_TO_GLD_30M` và `p_mode=RUN`. Không chạy tay `NB_GLD_SRV_POI_INFO` cùng lúc. `runtime_required` chuyển thành true. | architecture.md ## Rollout | 2026-11-09 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-001 | P1 | rejected-false-positive | Statement 27, job 267: một stage parquet scan `slv_poi_media_info`, input 15.7 MiB, shuffle write 62.2 KiB, 0.6 s, 8/8 task. Job 272 là count, stage chạy là `InMemoryTableScan`; stage scan `slv_poi_entity_non_enrich` bị skip. Count không đọc lại parquet media. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-08: D-01. Thêm `cover_id` và `cover_blob_url` trên dòng info, cùng cách gallery xác định cover. Không tách gold, PostgreSQL, entity JPA. Không thêm endpoint.

## Lịch sử quyết định

- 2026-11-08: Mở D-01 từ yêu cầu người dùng. Chưa có quyết định bị thay.
- 2026-11-09: `model-design.md` (claude-opus-5-5, effort medium) và `architecture.md` RESULT PASS (claude-opus-5-5, effort high). Architecture để vị trí cột sau `review_count`, cạnh ctrl trên `PL_VV_TRANS_SLV_TO_GLD_30M`, input `media` không bắt buộc, predicate `is_cover` true, quá một cover thì `QualityGateError`. Pipeline JSON không đổi.
- 2026-11-09: Người dùng chốt D-02. Bốn file test vào `scope.files`. Implement theo edit list.
- 2026-11-09: Kết quả probe `SPARK-001` mới có log `DRY_RUN` SUCCESS (`exec_id` `390dc54c-7b54-4938-b319-2ec970a13db0`, 110s, 292 dòng nguồn). Chưa có số scan, shuffle, spill, memory từ Spark UI. Finding vẫn mở.
- 2026-11-09: Đóng `SPARK-001` là `rejected-false-positive`. Job 267 scan `slv_poi_media_info` một lần, 15.7 MiB, 0.6 s, shuffle write 62.2 KiB. Job 272 đọc `InMemoryTableScan`, không scan lại parquet media.
- 2026-11-09: Mở D-03. Người dùng yêu cầu chạy rollout. `runtime_required` thành true. Lần MERGE đi qua `NB_00_ORCHES_SLV_TO_GLD` mode `RUN`.
- 2026-11-09: Orches `RUN` `SUCCESS`, `exec_id` `d733ea4a-95c7-49f7-bce8-df4911adf3ce`. Node info `SUCCESS`, update 238, `trg_version` 9, tiến 6 cạnh. Chưa có SQL kiểm tra, lần chạy lại, và `ALTER`. Gate runtime vẫn `pending`.
- 2026-11-09: Runtime PASS. `live_rows` 292 bằng `distinct_poi`. `cover_mismatch` 0. `cover_id_not_null` 238, bằng số update. Lần chạy lại `350daf3b-87cc-4196-9bb0-480754ebe505` là `NO_DATA`, 0 cạnh bẩn. `ALTER` PostgreSQL đã chạy.
