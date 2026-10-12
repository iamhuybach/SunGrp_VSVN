# Quyết định

## Giả định còn lại

- Nguồn hiện tại chỉ có tiếng Việt. Ba bảng gold không có cột ngôn ngữ. Enrichment service tạo thêm ngôn ngữ ở task khác.
- Một `poi_id` thuộc một nguồn. Dòng 3rd-party và dòng partner không dùng chung một biểu thức.
- `best_time_from_month`, `best_time_to_month` đổi từ `string` sang `int`, và `cost` đổi từ `string` sang `bigint`, vì người dùng chốt giữ số và lấy `costVnd`.
- `title`, `positive`, `negative`, `response_text` ra khỏi phạm vi.
- `load_mode` giữ tên `APPEND`. Quy ước §6 chưa có giá trị này. Người dùng chấp nhận rủi ro ở `PC-08`.
- `ward` partner dùng `coalesce(vietmap_ward, address.ward)` đúng notebook `2.1`. Phép gán cuối của `vietmap_district` không thấy, nên `district` partner chỉ lấy `address.district`.

## Sai lệch so với kiến trúc

- Chưa có `architecture.md`. Task này không chạy architecture gate.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| `PC-01` | P2 | `accepted-risk` | Giữ schema `lh_vv_gold.enr` và tiền tố `gld_enr_` (`MQ-024`, `BQ-007`). Không đổi về `lh_vv_gold.dbo` và `gld_srv_`. | |
| `PC-03` | P2 | `accepted-risk` | Không có bảng rule riêng. `rule_home` là `TEMPLATE_EXCEPTION_NO_RULE_TABLE` (`MQ-054`). | |
| `PC-05` | P1 | `accepted-risk` | Gold đọc `poi_address_enrichment_staging`. Luồng ghi gold áp nghiệp vụ đã chốt và tính `poi_id` partner cùng hash `review_id` trên bảng đích. | |
| `PC-07` | P2 | `accepted-risk` | Giữ `PL_VV_TRANS_SLV_TO_ENR_15P` và `NB_00_ORCHES_SLV_TO_ENR_15P` (`MQ-028`, `MQ-044`). | |
| `PC-08` | P2 | `accepted-risk` | Giữ `load_mode` `APPEND`. Partner và 3rd-party append, không join (`MQ-027`, `MQ-058`). | |
| `PC-09` | P2 | `accepted-risk` | `created_at` và `updated_at` gán mỗi lần ghi. `updated_at` thuộc khoá lịch sử (`MQ-030`, `MQ-039`, `MQ-052`). | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-12: giữ `lh_vv_gold.enr` và `gld_enr_`.
- 2026-10-12: khoá `gld_enr_poi_info` và `gld_enr_poi_coordinate` là `poi_id`. Khoá `gld_enr_poi_review` là `review_id`.
- 2026-10-12: `poi_id` 3rd-party và partner theo model mới, không có ngôn ngữ.
- 2026-10-12: `review_id` là `HASH_SHA256(source_name, reviewId)`. `source_review_id` là `reviewId` gốc.
- 2026-10-12: `review_updated_at` lấy `slv_3p_poi_review.time`.
- 2026-10-12: `description`, `time_to_spend`, `best_time_type`, tháng, `cost`, `subcategory_tags`, `name`, địa chỉ, `destination_name`, `lat`, `lng` theo các câu `MQ-007` đến `MQ-019`.
- 2026-10-12: bỏ `title`, `positive`, `negative`, `response_text`. `rating` là thang 5 sao.
- 2026-10-12: orchestrator `NB_00_ORCHES_SLV_TO_GLD`, nhịp 15 phút, `load_mode` `Append`. Ba bảng phục vụ enrichment service đọc. Dữ liệu trả về là task khác.
- 2026-10-12, lượt sau: `created_at` và `updated_at` đổi mỗi lần ghi. Không dùng rule `row_hash`.
- 2026-10-12, lượt sau: partner `short_address` lấy `address.full_address`. 3rd-party `province_name` lấy `city`. `review_date` giữ `timestamp`.
- 2026-10-12, lượt sau: `load_mode` giữ tên `APPEND`. Có dữ liệu mới thì append, không merge kể cả khi key đã có.
- 2026-10-12, lượt sau: `pl_name` là `PL_VV_TRANS_SLV_TO_ENR_15P`. `nb_name` là `NB_00_ORCHES_SLV_TO_ENR_15P`.
- 2026-10-12, lượt sau: ba bảng đích không đọc `destination_ward_mapping` và không đọc bảng `ref`.
- 2026-10-12, lượt sau: được nhiều dòng cùng `poi_id` hoặc `review_id`. Không có khoá duy nhất.
- 2026-10-12, lượt sau: `destination_name` ưu tiên `city`, fallback `province_name`. Registry `slv_3p_poi_address` không có cột `province_name`.
- 2026-10-12, lượt sau: bỏ `description` khỏi `gld_enr_poi_info`. Thêm các cột info theo bảng người dùng đưa. Không tự đổi `rating` thành `rating_overall`.
- 2026-10-12, lượt sau: fallback `destination_name` là `slv_3p_poi_address.state_province`.
- 2026-10-12, lượt sau: cột đích `rating` lấy `slv_3p_poi_rating.rating_overall`.
- 2026-10-12, lượt sau: `destination_context` dùng `short_address`, `district`, `city` và `destination_name`. `opening_hours_text` copy 1:1 từ `periods_json`. `review_json` không có Title, Positive, Negative.
- 2026-10-12, lượt sau: cột mới của `gld_enr_poi_info` với POI partner là NULL.
- 2026-10-12: người dùng yêu cầu phân tích. Main đặt `doc_status` thành `READY_FOR_ANALYSIS` và tăng `version` lên 6. Không thêm rule, cột, khoá hay công thức.
- 2026-10-12: `ANALYSIS_STATUS` lần 1 là `INPUT_INVALID` vì `MQ-007` trỏ `COL-002` đã bỏ. Main xoá tham chiếu đó và tăng Mapping `version` lên 7. Không thêm công thức.
- 2026-10-12: người dùng trả lời các câu phân tích. `destination_name` là chuỗi `coalesce(city, state_province)`. `review_json` sắp `time` giảm, tối đa 20, `review_text` cắt 350 ký tự. Không có bảng rule riêng. `created_at` và `updated_at` là cột kỹ thuật lúc ghi. `subcategory_tags` copy `types_json`. Logic transform lấy theo notebook legacy trong `notebooks_lgc/3rd_data_ingested_orches`.
- 2026-10-12: người dùng giữ hai ngoại lệ của mẫu. Không có bảng rule riêng. `created_at` và `updated_at` là cột kỹ thuật lúc ghi, không có `src_id`. Mapping `version` 11, BRD `version` 9.
- 2026-10-12: Claude CLI, model `claude-opus-5-5`, effort theo frontmatter `medium`. `ANALYSIS_STATUS` là `EVIDENCE_REQUIRED`. 0/3 `MAPPED`. Agent không chấp nhận ngoại lệ mẫu trong file đầu vào. `AQ-001` và `AQ-002` vẫn mở cho đến khi người dùng yêu cầu rõ việc sửa hệ thống agent, hoặc điền `rule_home` và `src_id`. Probe `AG-001` đến `AG-007` chưa viết.
- 2026-10-12: người dùng chọn (a) cho cả `AQ-001` và `AQ-002`. Main sửa mẫu BRD, mẫu Mapping và `.claude/agents/requirements-analyst.md` để nhận `TEMPLATE_EXCEPTION_NO_RULE_TABLE` và để trống `src_id` của `created_at`, `updated_at`. PC-03 và PC-09 vẫn là vi phạm nền tảng.
- 2026-10-12: chạy lại Claude CLI trên Mapping phiên bản 11 và BRD phiên bản 9. `ANALYSIS_STATUS` vẫn `EVIDENCE_REQUIRED`, 0/3 `MAPPED`. `AG-008` và `AQ-001` đóng. `AG-009` và `AQ-002` đóng. Không còn câu hỏi ở mục 7. Probe `AG-001` đến `AG-007` vẫn mở. PC-03 và PC-09 vẫn là vi phạm nền tảng.
- 2026-10-12: người dùng sửa Mapping, tách `nb_name` thành `NB_ENR_POI_INFO`, `NB_ENR_POI_COORDINATE`, `NB_ENR_POI_REVIEW`. Bảy probe `AG-001` đến `AG-007` nằm ngoài phạm vi vì thuộc model cũ. Notebook legacy chỉ để nắm nghiệp vụ trường, không áp dụng 100%. Main cập nhật BRD phiên bản 10 và Mapping phiên bản 12. Không viết probe.
- 2026-10-12: người dùng yêu cầu sửa agent để `BQ-024` đóng `AG-001` đến `AG-007`, rồi commit và push `main` nếu không còn vấn đề. Main thêm mục "Out-of-scope legacy physical facts". Claude CLI trên Mapping phiên bản 12 và BRD phiên bản 10 trả `EVIDENCE_REQUIRED`. `AG-001` đến `AG-009` đóng. Còn `AQ-001` (`review_text`), `AQ-002` (`MQ-055` trên `RULE-003` đến `RULE-006`) và `AQ-003` (`ID-005`). Chưa commit, chưa push.
- 2026-10-12: `review_text` lấy `slv_3p_poi_review.text`. Bỏ `MQ-055`. Partner và 3rd-party append, không join. `source_id` luôn có trên dòng từng nguồn. Bỏ luật bắt buộc `src_id`. Xóa `ID-005`. `notebooks_lgc` chỉ để đối chiếu nghiệp vụ trường, không phải model thiết kế. Mapping phiên bản 13, BRD phiên bản 11.
- 2026-10-12: Claude CLI trên Mapping phiên bản 13 và BRD phiên bản 11 trả `USER_DECISION`. Không còn gap và không còn câu hỏi. 0/3 `MAPPED` vì còn vi phạm nền tảng đã được người dùng giữ: schema `enr`, không có bảng rule riêng, gold đọc gold và xử lý nghiệp vụ, tên pipeline và orchestrator, `load_mode` `APPEND`, `created_at` và `updated_at` gán mỗi lần ghi.
- 2026-10-12: người dùng `accept-risk` cho `PC-01`, `PC-03`, `PC-05`, `PC-07`, `PC-08` và `PC-09`. Main ghi `accepted-risk` ở mục xử lý findings. Không sửa Mapping và BRD.
