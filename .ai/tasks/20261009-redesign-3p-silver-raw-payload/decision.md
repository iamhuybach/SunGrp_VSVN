# Quyết định

## Ngoại lệ model (2026-10-09)

Người dùng duyệt trước khi mở gate kiến trúc và review:

- Main là Grok 4.7 Medium trên Cursor. `models.main.actual` = `grok-4.7`. Người dùng hạ effort từ High xuống Medium trong cùng ngày.
- Architect chạy bằng subagent Cursor, model `claude-opus-5-5-medium`, effort medium. Chỉ viết `architecture.md`. Không gọi Claude Code CLI và không gọi `python scripts/vv.py run-gate`.
- Reviewer và `risk-gate` chạy bằng subagent Cursor, model `gpt-5.6-sol-medium`, effort medium, read-only. Không gọi Codex CLI và không gọi `python scripts/vv.py run-gate`.
- Round 1 các reviewer làm việc độc lập: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`. Luôn chạy `risk-gate`.
- Ô `models.*.effort` trong `task-state.yaml` giữ giá trị mà `python scripts/vv.py validate` chấp nhận. Effort runtime nằm ở `model_policy_exception`.
- Nếu một trong hai model trên không gọi được, dừng. Không đổi sang model khác.

## Giả định còn lại

- Một dòng sample không phải hợp đồng population. Mọi nhận xét về đường dẫn, kiểu, và sự vắng mặt của enrichment trong `evidence/sample-key-tree.md` chỉ đúng với dòng đó.
- Không suy ra null rate, độ phủ, hay tính duy nhất của khóa review/media từ dòng này.
- `raw_payload` không được khai triển. Dòng sample không chứng minh extract phải đọc cột đó.

## Sai lệch so với kiến trúc

- 2026-10-09: kiến trúc giữ bảng đã tắt và cột cũ trên Delta, không `DROP`. Người dùng yêu cầu thêm `DROP`/`DELETE` vì các bảng đã được tạo và chạy bằng code cũ. Áp dụng một lần trên Fabric DEV, sau snapshot:
  - `DROP TABLE` năm bảng `slv_3p_poi_price`, `slv_3p_poi_raw_data`, `slv_3p_poi_content`, `slv_3p_poi_enrichment`, `slv_3p_poi_review_i18n`.
  - `ALTER TABLE DROP COLUMNS` cho `available_langs_json`, `enrichment_failed_langs_json` và 38 cờ amenity. Hai bảng `slv_3p_poi` và `slv_3p_poi_amenity` phải bật `delta.columnMapping.mode = name` trước, vì Delta hiện tại không cho xóa cột khi chưa bật mapping.
  - `DELETE` dòng `ctrl_cdc_state` và `ctrl_cdc_reject` của năm bảng đó, partition `src_tbl = brz_3rd_crawler_poi_stream`.
  - Không `DROP` `slv_3p_poi_policy`.
  - 2026-10-09, bổ sung: năm bảng đã bỏ bị `DELETE` khỏi `ctrl_cfg_schema_registry` và `ctrl_mng_pipeline_config`. Không giữ `is_active = 0`. Seed pipeline chỉ còn 9 bảng.
  - Dữ liệu enrich cũ trên năm bảng bị xóa có chủ đích. Rollback các bảng đó chỉ còn nếu đã `RESTORE` từ snapshot trước `DROP`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-09: duyệt ngoại lệ model ở mục trên, rồi hạ Main từ Grok 4.7 High xuống Grok 4.7 Medium.
- 2026-10-09: transform có logic riêng xử lý ở L2. L1 chỉ extract 1:1 từ payload và chuẩn hóa data type.
  - L1 giữ nguyên đường dẫn JSON, cast kiểu, cột kỹ thuật snapshot, và khóa MERGE đã chốt (`HASH_MD5_UUID`, `HASH_SHA256`, `HASH_SHA256_PIPE`). Các khóa này không phải rule nghiệp vụ.
  - L1 không lọc ngôn ngữ, không dựng object bản địa hóa, không map cờ amenity, không chọn tên, mô tả, sector, category, slug, hay destination.
- 2026-10-09: probe E1 quét toàn bộ `brz_3rd_crawler_poi_stream` hiện tại, 33 tài liệu. Diễn giải nằm ở `evidence/e1-interpretation.md`.
  - Tắt `slv_3p_poi_enrichment`, `slv_3p_poi_review_i18n`, `slv_3p_poi_content`, `slv_3p_poi_price`, `slv_3p_poi_raw_data`. Giữ `slv_3p_poi_policy` tắt.
  - Bỏ 38 cờ amenity phẳng. Giữ `amenity_schema` và `ext_attributes` dạng JSON.
  - Giữ công thức `review_id` và `media_dedup_key`.
  - 33 dòng này không mô tả các dòng silver đã nạp từ payload enrich cũ.
