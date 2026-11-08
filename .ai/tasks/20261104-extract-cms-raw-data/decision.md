# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | load_mode | `load_mode` của mọi dòng `cms_raw_data` chỉ nhận `DOC` hoặc `DOC_ARRAY`. Không dùng `CDC` khi chưa có event Debezium thật. Không thêm giá trị vào `LOAD_MODES`. | proposal.md ## Ràng buộc cho Architect, mục 1 | 2026-11-04 |
| D-02 | Chữ ký mode | Không sửa chữ ký mode trong `NB_LIB_EXTRACT_RAWDATA`. Notebook mới gọi `load_table_specs` với `SNAPSHOT_MODES`. | proposal.md ## Ràng buộc cho Architect, mục 2 | 2026-11-04 |
| D-03 | Pipeline | Không gắn `cms_raw_data` vào activity của `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`. | proposal.md ## Ràng buộc cho Architect, mục 4 | 2026-11-04 |
| D-04 | Khối chưa thấy | Không thiết kế bảng từ `pois[]`. Không đặt `json_path` cho khóa con `cover_gallery[].formats.*` vì chưa có bằng chứng. | proposal.md ## Ràng buộc cho Architect, mục 7 | 2026-11-04 |
| D-05 | Bảng đích | Chấp nhận phương án C. Có 4 bảng: cms_blog (strapi_blog), cms_destination (strapi_destination), cms_news (strapi_news), cms_promotion_article (strapi_ph_promotion_article). Trong ngoặc là giá trị của source_name và tên ngoài ngoặc thêm tiền tố slv_ là tên bảng mong muốn. raw_payload chính là cột cần extract. Dùng document_id cùng locale như nb cũ. | decision.md ## Quyết định của người dùng | 2026-11-05 |
| D-06 | Kiểu bronze và số dòng | Statement 1: `event_id`, `source_name`, `type`, `crawled_at`, `ingested_date`, and `raw_payload` are `string`. Statement 2: `strapi_blog` 91207, `strapi_destination` 93820, `strapi_news` 236, `strapi_ph_promotion_article` 8160. Statement 3 failed with `DATATYPE_MISMATCH.NON_FOLDABLE_INPUT` because `schema_of_json` requires a foldable `STRING`. Statement 4 was not stored. | evidence/results/cms-source-sample.md ## Recorded result | 2026-11-05 |
| D-07 | Khóa đã parse | `strapi_blog`: 50 rows, 50 `PARSE_FAIL`, no key set. `strapi_destination`: 50 rows, 46 `PARSE_FAIL`, 4 rows with one key set. `strapi_news`: 50 rows, 13 `PARSE_FAIL`, 37 rows with one key set. `strapi_ph_promotion_article`: 50 rows, 0 `PARSE_FAIL`, 50 rows with one key set. Listed `PARSE_FAIL` columns are between 6546 and 7999. | evidence/results/cms-payload-keys.md ## Recorded result | 2026-11-05 |
| D-08 | Độ dài 50 dòng | On 50 rows, closed-object counts equal parsed-row counts: `strapi_blog` CLOSED 0 MAX 7988, `strapi_destination` CLOSED 4 MAX 8000, `strapi_news` CLOSED 37 MAX 14575, `strapi_ph_promotion_article` CLOSED 50 MAX 6805. News shows a `raw_payload` longer than 8000 characters. | evidence/results/cms-payload-length.md ## Recorded result | 2026-11-05 |
| D-09 | Tỷ lệ chuỗi đóng | Full table: `strapi_blog` 91207 rows, 0 null, 79766 closed, 11441 open, min_len 490, max_len 62361. `strapi_destination` 93820 rows, 0 null, 37174 closed, 56646 open, min_len 2724, max_len 107130. `strapi_news` 236 rows, 0 null, 223 closed, 13 open, min_len 4861, max_len 18033. `strapi_ph_promotion_article` 8160 rows, 0 null, 8023 closed, 137 open, min_len 638, max_len 7501. | evidence/results/cms-payload-close-rate.md ## Recorded result | 2026-11-05 |
| D-10 | Reject và phạm vi extract | Những bản ghi lỗi sẽ xử lý giống luồng partner: ghi ra ctrl_cdc_reject. Tham khảo notebook notebooks_lgc/cms_transform/nb_cms_transformation.ipynb để lấy nghiệp vụ; code đó là model cũ, không phải code chuẩn. Format code và cấu trúc bảng theo model và rule hiện tại. Extract ra 4 bảng silver: slv_cms_blog, slv_cms_destination, slv_cms_news, slv_cms_promotion_article. Không cần xử lý ra gold. | decision.md ## Quyết định reject và phạm vi | 2026-11-05 |
| D-11 | Payload hở | Open lengths: `strapi_blog` 11441 in 1000–7999. `strapi_destination` 39004 in 1000–7999 and 17642 at length 8000. `strapi_news` 10 in 1000–7999 and 3 at length 8000. `strapi_ph_promotion_article` 137 at length 7501. `EVENT_BOTH` returned no rows. Regex key pairs: blog 169 (152 with a closed event, 17 with none, 17 latest open), destination 236 (99, 137, 138), news 16 (16, 0, 1), promotion 59 (59, 0, 0). Rows missing `documentId` or `locale`: blog 5110, destination 0, news 2, promotion 0. | evidence/results/cms-open-payload-cause.md ## Recorded result | 2026-11-06 |
| D-12 | Định dạng thời gian | On closed rows, `createdAt`, `updatedAt`, and `publishedAt` match ISO-with-Z: blog 79765, 79765, and 79764; destination 37174; news 223; promotion 8023. Blog `first_publish_date` matches `yyyy-MM-dd` on 79756 rows. The four promotion datetimes match ISO-with-Z on 8023 rows. `crawled_at` matches ISO-with-Z on every row and `try_cast` null count is 0. Closed `locale` values are `vi`, `en`, and `ko`, plus 9 blank blog rows. `ORDER` failed with `DATATYPE_MISMATCH.BINARY_OP_DIFF_TYPES`. | evidence/results/cms-format-census.md ## Recorded result | 2026-11-06 |
| D-13 | Khóa trên dòng đóng | Blog: 40 of 50 parsed, 10 failed, one key set. Destination: 50 parsed, one key set, and `rank`, `tags`, `hooks`, `sections` absent. News: 50 parsed, one key set; `SEO` is null on 42 and object on 8; `news_category` is null on 20 and object on 30. Promotion: 50 parsed, one key set. | evidence/results/cms-closed-key-census.md ## Recorded result | 2026-11-06 |
| D-14 | Thứ tự event | `keys_with_crawled_at_tie` is 0 for every source. `keys_updated_order_ne_crawled_order`: `strapi_blog` 146, `strapi_destination` 99, `strapi_news` 12, `strapi_ph_promotion_article` 27. | evidence/results/cms-event-order.md ## Recorded result | 2026-11-06 |
| D-15 | U1–U4 | U1 Chấp nhận ghi chúng vào ctrl_cdc_reject. U2 tên notebook NB_EXTRACT_CMS_CDC_BRZ_TO_SLV và pl_name PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00, không gắn activity partner. U3 Chấp nhận. U4 Chấp nhận nhưng local null vẫn lấy. | decision.md ## Quyết định U1 đến U4 | 2026-11-06 |
| D-16 | Vòng architecture | Cho phép thêm một vòng architecture. | decision.md ## Quyết định vòng architecture | 2026-11-06 |
| D-17 | U5 | Không còn khóa luồng. Hãy tiếp tục chạy theo workflow. | decision.md ## Quyết định U5 | 2026-11-07 |
| D-18 | Vòng architecture | Cho phép. Main đưa rounds.architecture về 1 và chạy python scripts/vv.py run-gate 20261104-extract-cms-raw-data. | decision.md ## Quyết định vòng architecture tiếp theo | 2026-11-08 |
| D-19 | Vòng architecture | Đã hoàn tất đăng nhập lại Claude Code/Claude CLI. Cho phép thêm một vòng architecture. | decision.md ## Quyết định sau khi đăng nhập lại | 2026-11-08 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

Chấp nhận phương án C. Có 4 bảng: cms_blog (strapi_blog), cms_destination (strapi_destination), cms_news (strapi_news), cms_promotion_article (strapi_ph_promotion_article). Trong ngoặc là giá trị của source_name và tên ngoài ngoặc thêm tiền tố slv_ là tên bảng mong muốn. raw_payload chính là cột cần extract. Dùng document_id cùng locale như nb cũ.

## Quyết định reject và phạm vi

Những bản ghi lỗi sẽ xử lý giống luồng partner: ghi ra ctrl_cdc_reject. Tham khảo notebook notebooks_lgc/cms_transform/nb_cms_transformation.ipynb để lấy nghiệp vụ; code đó là model cũ, không phải code chuẩn. Format code và cấu trúc bảng theo model và rule hiện tại. Extract ra 4 bảng silver: slv_cms_blog, slv_cms_destination, slv_cms_news, slv_cms_promotion_article. Không cần xử lý ra gold.

## Quyết định U1 đến U4

U1 Chấp nhận ghi chúng vào ctrl_cdc_reject. U2 tên notebook NB_EXTRACT_CMS_CDC_BRZ_TO_SLV và pl_name PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00, không gắn activity partner. U3 Chấp nhận. U4 Chấp nhận nhưng local null vẫn lấy.

## Quyết định vòng architecture

Cho phép thêm một vòng architecture.

## Quyết định U5

Không còn khóa luồng. Hãy tiếp tục chạy theo workflow.

## Quyết định vòng architecture tiếp theo

Cho phép. Main đưa rounds.architecture về 1 và chạy python scripts/vv.py run-gate 20261104-extract-cms-raw-data.

## Quyết định sau khi đăng nhập lại

Đã hoàn tất đăng nhập lại Claude Code/Claude CLI. Cho phép thêm một vòng architecture.

## Lịch sử quyết định

- 2026-11-04: `run-author --kind analysis` ghi `problem-analysis.md` (`claude-opus-5-5`, effort medium). `run-author --kind proposal` ghi `proposal.md` (`claude-opus-5-5`, effort high) và chọn phương án C. D-01 đến D-04 chép nguyên văn từ `proposal.md`.
- 2026-11-04: Người dùng chấp nhận phương án C và nêu 4 bảng, key là `id`. D-05 được sửa tại chỗ bằng câu ở `## Quyết định của người dùng`. Chưa chạy `run-author --kind model`: tên trong ngoặc, grain, cột cần giữ và các khối mảng chưa được chốt.
- 2026-11-04: Người dùng chốt tên trong ngoặc là giá trị `source_name`, tên bảng là tiền tố `slv_` cộng tên ngoài ngoặc, và cột extract là `raw_payload`. D-05 được sửa tại chỗ. Bốn bảng đọc từ quy tắc đó là `slv_cms_blog`, `slv_cms_destination`, `slv_cms_news`, `slv_cms_promotion_article`. Probe `evidence/probes/cms-source-sample.sql` chờ người dùng chạy trên Fabric DEV.
- 2026-11-05: Câu 1 và 2 của probe được ghi vào D-06. Câu 3 lỗi `schema_of_json`. Câu 4 không được lưu vì có nội dung và chữ ký truy cập. Khóa cấp gốc nhìn thấy trên các dòng đã xem khác nhau theo `source_name`, nên bảng khối trong `proposal.md` không phải shape của cả bốn nguồn. Probe `evidence/probes/cms-payload-keys.py` chờ người dùng chạy.
- 2026-11-05: Lần chạy `cms-payload-keys.py` dừng với `JSONDecodeError`: `Unterminated string` tại char 7976. Probe được sửa để đếm JSON hỏng, bỏ qua dòng đó, và in khóa của dòng parse được. Chưa có bản in khóa.
- 2026-11-05: Bản in khóa được ghi vào D-07. `strapi_blog` không có dòng parse được trong 50 dòng. Cột lỗi nằm trong khoảng 6546–7999. Chưa kết luận chuỗi bị cắt. Probe `evidence/probes/cms-payload-length.py` chờ người dùng chạy.
- 2026-11-05: Lần chạy `cms-payload-length.py` lỗi f-string vì một dấu `}` trong SQL. Query được ghép bằng chuỗi thường. Chưa có dòng `LEN`.
- 2026-11-05: Bốn dòng `LEN` được ghi vào D-08. Số chuỗi kết thúc bằng `}` trùng số dòng parse được. `strapi_news` có chuỗi dài 14575. Tỷ lệ trên cả bảng chưa đo. Probe `evidence/probes/cms-payload-close-rate.sql` chờ người dùng chạy.
- 2026-11-05: Bốn dòng tổng hợp được ghi vào D-09. `max_len` của blog, destination và news lớn hơn 8000. Nguyên nhân chuỗi không kết thúc bằng `}` chưa được xác định. Chưa chốt cách xử lý các dòng open và cột cần giữ.
- 2026-11-05: Người dùng chốt D-10: bản ghi lỗi ghi `ctrl_cdc_reject` như partner; notebook `notebooks_lgc/cms_transform/nb_cms_transformation.ipynb` chỉ là nguồn nghiệp vụ; extract ra bốn bảng `slv_cms_*`; không làm gold. Notebook cũ MERGE blog, news và promotion theo `document_id` và `locale` (cell 0, CS-02 đến CS-04), destination theo `documentId` (CS-01). D-05 vẫn ghi key là `id`. Chưa chạy model.
- 2026-11-05: Người dùng chọn khóa MERGE `document_id` cùng `locale` cho cả bốn bảng, kể cả destination. D-05 được sửa tại chỗ. Key `id` không còn là khóa MERGE. Chưa chạy `run-author --kind model`.
- 2026-11-05: `run-author --kind model` ghi `model-design.md` (`claude-opus-5-5`, effort medium). `run-gate` trả `EVIDENCE_REQUIRED` và chuyển `waiting_evidence`. Probe P1, P2, P3 được ghi dưới `evidence/probes/`. Chưa chạy trên Fabric.
- 2026-11-06: P1, P2 và P3 được ghi vào D-11, D-12, D-13. `ORDER` lỗi `DATATYPE_MISMATCH.BINARY_OP_DIFF_TYPES`. Probe `evidence/probes/cms-event-order.py` chờ người dùng chạy. U1–U4 chưa được chốt.
- 2026-11-06: `cms-event-order.py` ghi D-14. Người dùng chốt D-15. `local null vẫn lấy` được hiểu là `locale` null vẫn thành dòng silver, không reject. `run-author --kind model` ghi lại `model-design.md`. `run-gate` không gọi Architect vì `rounds.architecture` đã là 2, trần của workflow, và chuyển `user_decision`.
- 2026-11-06: Người dùng cho phép thêm một vòng architecture (D-16). `rounds.architecture` được đưa về 1 để `run-gate` gọi Architect một lần nữa.
- 2026-11-06: `run-gate` gọi Architect và dừng vì `connection_failed` (`API Error: Connection lost mid-response`). Vòng không được tính. Status vẫn `waiting_architecture`, `rounds.architecture` vẫn là 1.
- 2026-11-06: `run-gate` gọi Architect khoảng 168 giây rồi dừng trước khi đọc JSON, vì Git status đổi trong lúc chạy: task khác ghi file untracked dưới `.ai/tasks/20261106-agent-system-unify-api/`. Vòng không được tính. `architecture.md` trên đĩa vẫn là bản 11:01, chưa phải verdict của lần gọi này. Status vẫn `waiting_architecture`, `rounds.architecture` vẫn là 1.
- 2026-11-06: `run-gate` ghi `architecture.md` với `RESULT: EVIDENCE_REQUIRED` (`claude-opus-5-5`, effort high). `rounds.architecture` thành 2. Status `waiting_evidence`. B1 và B2 chặn implement: `first_publish_date` không được dùng `DATE_DAYS`; Conflicts 3–5 cần U5 rồi `run-author --kind model`. P4 và U6 chỉ là cổng rollout. Vòng architecture kế tiếp cần người dùng cho phép vì D-16 chỉ phủ vòng này.
- 2026-11-07: Người dùng chốt D-17. Câu đó được đọc là chấp nhận gói U5 trong `architecture.md` `## Required probes and decisions`: `first_publish_date` là `date` với `NONE`; không thêm blog `author`, `cover_image`, `destination`, `gallery` và news `cover_image`; giữ tên `*_json`; `locale` không có convert rule; `locale` rỗng giữ `''`. D-17 không phải lời cho phép thêm một vòng architecture.
- 2026-11-07: `run-author --kind model` ghi `model-design.new.md` (`claude-opus-5-5`, effort medium). Main thay `model-design.md` bằng bản đó. `first_publish_date` là `date`/`NONE`. Conflicts 1–7 được đánh dấu answered hoặc out of scope. Chưa gọi Architect vì `rounds.architecture` đã là 2.
- 2026-11-07: Chuyển `waiting_architecture` rồi `run-gate` gặp trần vòng architecture và chuyển `user_decision`. Architect không được gọi. `rounds.architecture` vẫn là 2.
- 2026-11-08: Người dùng cho phép thêm một vòng (D-18). `rounds.architecture` được đưa về 1. Đường đi là `user_decision` → `triage` → `waiting_architecture`, rồi `run-gate`.
- 2026-11-08: `run-gate` gọi Architect và dừng sau 5 giây vì CLI hết hạn đăng nhập: `Failed to authenticate: this login reached its time limit and cannot be renewed`. Vòng không được tính. Status vẫn `waiting_architecture`, `rounds.architecture` vẫn là 1, `gates.architecture` vẫn `pending`.
- 2026-11-08: Người dùng xác nhận đã đăng nhập lại và cho phép thêm một vòng (D-19). `rounds.architecture` giữ nguyên 1 vì lần gọi hết hạn đăng nhập không được tính.
- 2026-11-08: `run-gate` ghi `architecture.md` với `RESULT: PASS` (`claude-opus-5-5`, effort high). `rounds.architecture` thành 2. Status `implementing`. B1 và B2 đóng. B3 chỉ chặn lần chạy thật, không chặn implement.
- 2026-11-08: Main viết notebook `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV`, seed 4 dòng `DOC`, watermark `wm_transform_cms_raw_data`, và 59 cột registry theo `model-design.md` `## Columns` cùng khối A8. Main brief ghi 48 dòng; A8 và model cộng lại là 59. Không sửa lib, notebook 3P, notebook partner. Không gắn activity FL_00.
- 2026-11-08: `python scripts/vv.py verify` PASS. `gates.local_verification` = `pass`. `gates.evidence` chuyển `pass` vì các probe chặn kiến trúc đã có kết quả và architecture là `PASS`. P4 vẫn chỉ là cổng rollout khi dry run báo `cast_null > 0`. Status `ready_to_merge`.
- 2026-11-08: Dry run DEV `exec_id=4ab436e9-74eb-4cc6-92ab-9ec51f6e4831`: seed 4/4 và 59 cột, đọc 193423, hợp lệ 125143, reject 68280, `cast_null=0`, `docs_by_table` blog 79756 / destination 37141 / news 223 / promotion 8023. `expand_rows` với `DOC $` chưa gọi `presence`, nên `apply=125143` ở cả 4 bảng. Chưa chạy ghi. Sửa `expand_rows` lọc `presence(spec)` trước MERGE.
- 2026-11-09: Dry run DEV sau bản sửa, `exec_id=2ae46456-d204-4ffc-a092-b91203806299`. `apply` bằng `docs_by_table` ở cả bốn bảng. `cast_null=0`. Chưa chạy ghi.
- 2026-11-09: Hai lần ghi DEV đều là `FULL_RELOAD`. Lần 1 insert 152/98/16/59 khóa. Lần 2 insert 0 và update đúng 325 khóa. Watermark không tiến vì `full_reload`. Chưa có lần chạy incremental.
- 2026-11-09: Incremental DEV `exec_id=3223bc96-48ec-41e8-ac7d-0d4a2150078c`. Mọi dòng silver đã có đều `stale`, `inserted=0`, `updated=0`. Version chốt 1488 và `error` null, nên watermark được tiến ở cuối lần chạy này.
