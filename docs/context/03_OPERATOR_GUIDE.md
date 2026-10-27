# Hướng dẫn vận hành nền tảng

Tài liệu này mô tả hiện trạng trong repository. Không lấy model cũ trong `notebooks_lgc/`. `Required` của bảng ctrl chỉ gồm cột `NOT NULL` trong DDL và điều kiện `ConfigError` trong lib. DDL hiện hành của ctrl là `TABLE_SPECS` trong `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell 3. Khối đó không khai báo `NOT NULL` cho cột nào của bảy bảng `lh_vv_ctrl.dbo.ctrl_*`. Vì vậy không có cột ctrl nào required theo DDL. Cột required bên dưới là điều kiện `ConfigError` khi nạp cấu hình, không phải ràng buộc NULL của Spark.

## 1. Bảng ctrl

Bảy bảng nằm ở `lh_vv_ctrl.dbo`. Ý nghĩa từng bảng lấy từ `docs/context/CTRL_TABLES_CONTEXT.md` §3–§9. Danh sách cột lấy từ `NB_SETUP_INITIAL_DDL` cell 3. Phần "Dữ liệu hiện có" của context không dùng để kết luận required.

### 1.1 `ctrl_mng_pipeline_config`

Danh sách việc của một pipeline. Extract: một dòng là một bảng đích. Luồng tính lại: một dòng là một cạnh của DAG. Thêm hoặc tắt bảng bằng dữ liệu, không sửa notebook. Nguồn: `CTRL_TABLES_CONTEXT.md` §3.

Notebook extract đọc dòng `is_active = 1` khớp `pl_name`, `src_schema`, `src_tbl` (`notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb`, `load_table_specs`, cell 18). `build_dag` chỉ lấy dòng `is_active = 1` và `load_mode` là `RECOMPUTE` hoặc `APPEND` (`notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`, `load_config_rows`, cell 7).

| Cột | Kiểu | Ý nghĩa | Required |
|---|---|---|---|
| `id` | BIGINT | Số thứ tự lúc seed | Không |
| `pl_name` | STRING | Tên pipeline. Extract dùng `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`. Luồng tính lại phải có hậu tố nhịp khi lib kiểm tra nhịp | Không theo DDL. Dòng không khớp `pl_name` thì không được nạp |
| `src_schema` | STRING | Extract: schema raw. Cạnh: schema bảng đầu vào | Cạnh: `is_fq_name`, sai thì `ConfigError` (`build_dag`, cell 7) |
| `src_tbl` | STRING | Extract: bảng raw. Cạnh: bảng đầu vào | Cạnh: `is_identifier`, sai thì `ConfigError` (`build_dag`, cell 7) |
| `trg_schema` | STRING | Schema bảng đích | Extract: `is_fq_name`, sai thì `ConfigError` (`build_table_specs`, cell 18). Cạnh: cùng luật trong `build_dag` |
| `trg_tbl` | STRING | Bảng đích | `is_identifier`, sai thì `ConfigError` (hai hàm trên) |
| `is_active` | INT | `1` bật, `0` tắt cả bảng extract hoặc tắt một cạnh | Không phải `NOT NULL`. Dòng khác `1` không vào danh sách nạp |
| `priority` | INT | Extract: wave, cùng số chạy song song. Cạnh: tầng, chỉ để đọc; thứ tự chạy do cạnh quyết định | Extract: `NULL` thì `ConfigError` `priority NULL` (`build_table_specs`, cell 18) |
| `load_mode` | STRING | Extract: `CDC`, `DOC`, `DOC_ARRAY`. `NULL` được coi là `CDC`. Cạnh: `RECOMPUTE` hoặc `APPEND` | Giá trị ngoài `LOAD_MODES`, hoặc không thuộc notebook, thì `ConfigError` (`build_table_specs`, cell 18). `build_dag` bỏ dòng không phải `RECOMPUTE` / `APPEND` |
| `align_path` | STRING | Mảng ghép theo vị trí cho `DOC_ARRAY`. CDC để trống | Có giá trị khi mode không phải snapshot, hoặc sai dạng, thì `ConfigError` (`build_table_specs`, cell 18) |
| `dedup_order` | STRING | Snapshot: chọn một dòng khi một tài liệu có nhiều dòng cùng khoá | Có giá trị khi mode là `CDC`, hoặc cột không thuộc bảng, thì `ConfigError` (`build_table_specs`, cell 18) |
| `nb_name` | STRING | Notebook của node khi khác `NB_<UPPER(trg_tbl)>`. Trống thì lib suy ra tên đó | Nếu có giá trị thì phải `is_identifier`, sai thì `ConfigError` (`build_dag`, cell 7) |

`build_table_specs` còn báo `ConfigError` khi trùng bảng đích, `table_filter` nêu bảng không active, hoặc không còn dòng active. `build_dag` còn báo khi không có cạnh active, trùng cạnh, trùng `watermark_id`, một node thuộc nhiều pipeline active, nhiều `nb_name` hoặc nhiều `load_mode` trên một node, node tự đọc chính nó, chu trình, hoặc pipeline nhanh đọc node của pipeline chậm hơn.

`load_mode` và `is_active` chỉ nhận các giá trị dưới đây. Tập `LOAD_MODES` nằm ở `NB_LIB_EXTRACT_RAWDATA` cell hằng số. `EDGE_LOAD_MODES` nằm ở `NB_LIB_TRANSFORM_SLV_GLD` cell hằng số. Notebook 3rd-party chỉ truyền `EXTRACT_MODES = ("DOC", "DOC_ARRAY")`.

| Giá trị | Dùng khi | Ai nhận |
|---|---|---|
| `CDC` | Event Debezium, JSON `before` / `after`. `NULL` được đọc thành `CDC` | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` |
| `DOC` | Một khối trong payload snapshot | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `DOC_ARRAY` | Mảng phần tử trong payload. `align_path` chỉ hợp lệ với mode này | Notebook 3rd-party |
| `RECOMPUTE` | Cạnh luồng tính lại. Node ghi bằng `MERGE` | `build_dag` |
| `APPEND` | Cạnh luồng tính lại không `MERGE`. Node ghi bằng `APPEND` | `build_dag` |

`is_active`: `1` đưa dòng vào lần nạp, `0` bỏ dòng. Không có giá trị khác.

### 1.2 `ctrl_mng_watermark`

Ba loại dòng trên cùng một bảng: con trỏ nguồn extract (`wm_transform_<src_tbl>`), hộp thư cạnh (`wm_e__<trg_tbl>__<src_tbl>`), khoá luồng (`wm_flow__<pl_name>`). Nguồn ý nghĩa: `CTRL_TABLES_CONTEXT.md` §4. Không có cột `NOT NULL`. Không thấy `ConfigError` bắt một cột watermark phải khác NULL khi ghi dòng. `require_ctrl_columns` không kiểm bảng này.

| Cột | Kiểu | Ý nghĩa | Required |
|---|---|---|---|
| `watermark_id` | STRING | Khoá logic của dòng | Không |
| `src_schema`, `src_tbl` | STRING | Bảng raw, bảng đầu vào, hoặc `src_tbl` = `pl_name` với dòng khoá | Không |
| `trg_schema`, `trg_tbl` | STRING | Dòng nguồn và dòng khoá để trống `trg_tbl`. Dòng cạnh là node | Không |
| `watermark_column` | STRING | Tên cột thời điểm để theo dõi. Không dùng để lọc raw | Không |
| `watermark_value` | TIMESTAMP | Mốc thời gian đã đọc. Không phải con trỏ version | Không |
| `last_success_at` | TIMESTAMP | Lần thành công gần nhất | Không |
| `status` | STRING | Trạng thái dòng hoặc khoá | Không |
| `flow_name` | STRING | Notebook ghi dòng | Không |
| `watermark_sequence` | BIGINT | Extract ghi `-1`. Cạnh để trống | Không |
| `last_run_id` | STRING | `run_id` gần nhất | Không |
| `last_src_version` | BIGINT | Con trỏ đọc chính của nguồn, hoặc version đầu vào của cạnh | Không |
| `last_src_table_id` | STRING | Delta table id lúc ghi version | Không |
| `error_message` | STRING | Lỗi gần nhất | Không |
| `lock_exec_id`, `lock_at` | STRING, TIMESTAMP | Khoá nguồn hoặc khoá luồng | Không |
| `updated_at` | TIMESTAMP | Lần sửa dòng gần nhất | Không |

Context §4 nói notebook extract cần đúng một dòng nguồn có `trg_tbl` trống. Đó là quy ước vận hành trong mục đó, không phải `NOT NULL` và không thấy trong `build_table_specs`.

| Cột | Giá trị | Ý nghĩa |
|---|---|---|
| `status` dòng nguồn | `INITIALIZED`, `RUNNING`, `SUCCESS`, `FAILED` | `RUNNING` khi đang giữ khoá. `SUCCESS` là lần đọc xong |
| `status` dòng cạnh | `INITIALIZED`, `SUCCESS`, `FAILED`, `SKIPPED`, `NOT_RUN` | `SUCCESS` khi cạnh đã tiến version |
| `status` dòng khoá | `RUNNING`, rồi `SUCCESS`, `NO_DATA`, `PARTIAL_FAILED`, `FAILED` | `RUNNING` lúc nhận khoá. Nhả khoá ghi trạng thái của run |
| `watermark_column` dòng nguồn | `EventProcessedUtcTime` hoặc `crawled_at` | Chỉ để theo dõi. Không lọc raw theo cột này |
| `watermark_column` dòng cạnh | `commit_ts` | Thời điểm commit của version đã đọc |

### 1.3 `ctrl_cfg_schema_registry`

Một dòng là một cột JSON của raw ánh xạ sang một cột silver L1. Nguồn ý nghĩa: `CTRL_TABLES_CONTEXT.md` §5. Không có cột `NOT NULL` trong DDL. Required là điều kiện `ConfigError` của `build_table_specs` (cell 18) và, với 3rd-party, `check_config` (`notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` cell 12).

| Cột | Kiểu | Ý nghĩa | Required |
|---|---|---|---|
| `src_schema`, `src_tbl` | STRING | Bảng raw, khớp dòng pipeline config | Dòng được đọc theo hai cột này. Không phải `NOT NULL` |
| `src_object_schema`, `src_object` | STRING | CDC: schema và bảng trong Debezium. Snapshot: `src_object` là khối payload, `$` là gốc | Một bảng đích chỉ được một cặp. Snapshot: `src_object` phải là `$` hoặc đường dẫn hợp lệ. `$` không đi với `DOC_ARRAY` |
| `trg_schema`, `trg_tbl` | STRING | Bảng silver L1 | Khớp bảng đích trong pipeline config |
| `trg_column` | STRING | Cột đích | `is_identifier`. Không trùng cột kỹ thuật, không trùng tên cột trong cùng bảng |
| `json_path` | STRING | Đường dẫn trong JSON `before` / `after` hoặc trong payload | CDC: một đường `a.b` hợp lệ. Snapshot: không rỗng. Nhiều phần chỉ với rule cho phép |
| `data_type` | STRING | Kiểu Spark của cột đích | `canonical_type` phải nhận. Sai thì `ConfigError` |
| `convert_arg` | STRING | JSON đối số của rule có đối số | Bắt buộc với rule có đối số. Rule không có đối số thì phải trống |
| `convert_rule` | STRING | Cách chuyển giá trị. Trống được coi là `NONE` | Phải thuộc tập rule. `HASH_*` không dùng cho CDC. `DECIMAL_BASE64` chỉ cho `decimal`. `LOWER_TRIM` và `HASH_*` chỉ cho `string` |
| `is_key` | BOOLEAN | Cột thuộc khoá MERGE | Mỗi bảng đích đang active phải có ít nhất một cột `is_key` |
| `key_order` | INT | Thứ tự trong khoá. Trống nếu không phải khoá | Với cột khoá: không `NULL`, không trùng |
| `is_toast` | BOOLEAN | Cột có thể nhận sentinel TOAST của Debezium | Snapshot: phải false |
| `column_order` | INT | Thứ tự cột đích | Không `NULL`, không trùng trong một bảng |
| `is_active` | BOOLEAN | Tắt một cột. Tắt cả bảng dùng `ctrl_mng_pipeline_config.is_active` | Cột inactive bị bỏ. Bảng đích không còn cột active thì `ConfigError` |
| `description` | STRING | Ghi chú | Không |

`check_config` của 3rd-party thêm: mọi bảng phải có cột `doc_key_column`, và mọi cột raw mà registry cần đọc phải có trên bảng raw.

`data_type` là chuỗi kiểu Spark. `canonical_type` chạy `CAST(NULL AS <kiểu>)` rồi trả `simpleString`. Viết không có dấu cách thừa: `string`, `boolean`, `timestamp`, `date`, `int`, `bigint`, `smallint`, `decimal(19,4)`. `decimal(19, 4)` bị chuẩn hoá thành `decimal(19,4)`. Kiểu Spark không nhận thì `ConfigError`.

`convert_rule` trống được đọc là `NONE`. Giá trị và kiểu đi kèm:

| `convert_rule` | `data_type` được nhận | Dùng khi |
|---|---|---|
| `NONE` | Kiểu Spark hợp lệ | Giữ giá trị, chỉ đổi kiểu |
| `EPOCH_S_TS` | `timestamp` | Số giây Unix. Số `0` thành NULL |
| `EPOCH_MS_TS` | `timestamp` | Số mili-giây Unix |
| `EPOCH_US_TS` | `timestamp` | Số micro-giây Unix |
| `ISO_UTC_TS` | `timestamp` | Chuỗi instant ISO, có `Z` hoặc offset |
| `DATE_DAYS` | `date` | Số ngày kể từ 1970-01-01 |
| `DECIMAL_BASE64` | `decimal(p,s)` | Decimal Debezium dạng base64. Chỉ CDC |
| `LOWER_TRIM` | `string` | `lower(trim(...))` |
| `HASH_MD5_UUID`, `HASH_SHA256`, `HASH_SHA256_PIPE` | `string` | Khoá suy ra. Chỉ snapshot, cấm ở CDC |
| `COALESCE` | Theo cột | Ghép nhiều phần `json_path`. Chỉ snapshot |
| `ARRAY_PICK`, `ARRAY_AT`, `ARRAY_PROJECT`, `JSON_PICK` | `string` | Cần `convert_arg`. Chỉ snapshot |
| `ENUM_MAP` | `int`, `bigint`, hoặc `smallint` | Cần `convert_arg`. Chỉ snapshot |
| `POS_1BASED` | Theo cột | Chỉ với `json_path` `_pos` trên `DOC_ARRAY` |

`is_key`: `true` nếu cột thuộc khoá MERGE, `false` nếu không. `is_toast`: `true` chỉ cho cột CDC có thể nhận sentinel Debezium. Snapshot phải `false`. `is_active`: `true` giữ cột, `false` bỏ cột khỏi bảng đích.

### 1.4 `ctrl_log_run`

Một dòng cho một lần chạy notebook, khoá mô tả là `exec_id`. Nguồn: `CTRL_TABLES_CONTEXT.md` §6 và comment cột trong `NB_SETUP_INITIAL_DDL` cell 3. Không có `NOT NULL`. Không thấy `ConfigError` bắt cột log khác NULL.

| Cột | Kiểu | Ý nghĩa | Required |
|---|---|---|---|
| `exec_id` | STRING | Id một lần chạy | Không theo DDL |
| `run_id` | STRING | RunId pipeline. Chạy tay: bằng `exec_id` khi tham số trống | Không |
| `pl_name` | STRING | Pipeline | Không |
| `nb_name` | STRING | Notebook thực thi | Không |
| `src_schema`, `src_tbl` | STRING | Bảng raw với extract. NB_00 để trống | Không |
| `watermark_id` | STRING | Dòng watermark tương ứng | Không |
| `run_mode` | STRING | Extract: `INCREMENTAL`, `FULL_RELOAD`, `DRY_RUN`. NB_00: `RUN`, `DRY_RUN` | Không |
| `table_filter` | STRING | Danh sách bảng, hoặc `p_force_nodes` với NB_00 | Không |
| `src_version_from`, `src_version_to` | BIGINT | Version raw trước và sau khi đọc | Không |
| `watermark_from`, `watermark_to` | TIMESTAMP | Mốc thời gian trước khi chạy và max của phần đã đọc | Không |
| `overlap_minutes` | INT | Giữ cho tương thích. Extract không còn dùng để đọc | Không |
| `read_rows`, `valid_rows`, `ignored_rows`, `rejected_rows` | BIGINT | Số event đọc, hợp lệ, bỏ qua, lỗi | Không |
| `ignored_detail` | STRING | JSON số event bỏ qua | Không |
| `tbl_total_count`, `tbl_success_count`, `tbl_failed_count`, `tbl_no_data_count` | INT | Số bảng hoặc số node | Không |
| `status` | STRING | Trạng thái run | Không |
| `started_at`, `ended_at` | TIMESTAMP | UTC bắt đầu và kết thúc | Không |
| `duration_ms` | BIGINT | Thời gian chạy | Không |
| `run_params` | STRING | JSON tham số | Không |
| `error_message` | STRING | Lỗi tổng | Không |
| `read_mode`, `read_note` | STRING | Cách đọc raw, hoặc JSON kế hoạch của NB_00 | Không |
| `output_versions_json` | STRING | NB_00: version các node của pipeline khi run thành công. Extract để trống | Không |

| Cột | Giá trị | Ý nghĩa |
|---|---|---|
| `run_mode` extract | `INCREMENTAL`, `FULL_RELOAD`, `DRY_RUN` | `DRY_RUN` không ghi. `FULL_RELOAD` đọc hết raw và bỏ state |
| `run_mode` NB_00 | `RUN`, `DRY_RUN` | `PLAN` không ghi dòng log |
| `status` | `RUNNING`, `SUCCESS`, `PARTIAL_FAILED`, `FAILED`, `NO_DATA`, `SKIPPED_CONCURRENT`, `ABANDONED` | `ABANDONED` khi run `RUNNING` quá hạn bị đóng |
| `read_mode` extract | `VERSION`, `FULL` | `FULL` khi không đọc theo version |
| `read_mode` NB_00 | `VERSION_INBOX` | Đọc theo version đã ghim |

### 1.5 `ctrl_log_table_run`

Một dòng cho một bảng đích, hoặc một node, trong một lần chạy. Nguồn: `CTRL_TABLES_CONTEXT.md` §7 và `NB_SETUP_INITIAL_DDL` cell 3. Không có `NOT NULL` trên từng cột.

Trước khi NB_00 làm việc, `require_ctrl_columns` (`NB_LIB_TRANSFORM_SLV_GLD` cell 3) kiểm tra bốn cột đã tồn tại trên bảng: `src_versions_json`, `trg_version`, `deactivated_rows`, `qg_json`. Thiếu cột thì `ConfigError`. Đó là cột phải có trong schema, không phải giá trị khác NULL trên mỗi dòng. Hằng `NEW_LOG_COLUMNS` ở cell 1 của cùng notebook.

| Cột | Kiểu | Ý nghĩa | Required |
|---|---|---|---|
| `exec_id`, `run_id`, `pl_name` | STRING | Khớp lần chạy | Không theo DDL |
| `src_schema`, `src_tbl`, `src_object` | STRING | Nguồn raw hoặc đối tượng Debezium | Không |
| `trg_schema`, `trg_tbl` | STRING | Bảng đích | Không |
| `priority` | INT | Wave extract, hoặc tầng DAG | Không |
| `attempt_no` | INT | Lần thử của bảng | Không |
| `input_rows`, `stale_rows`, `applicable_rows`, `entity_rows` | BIGINT | Số dòng đọc, bỏ vì cũ, được áp dụng, số khoá | Không |
| `upsert_event_rows`, `delete_event_rows` | BIGINT | Event áp dụng theo loại | Không |
| `inserted_rows`, `updated_rows` | BIGINT | Kết quả MERGE | Không |
| `cast_null_rows`, `rejected_rows` | BIGINT | Giá trị thành NULL sau chuyển kiểu, và event lỗi | Không |
| `status` | STRING | `SUCCESS`, `FAILED`, `NO_DATA`, `SKIPPED` | Không |
| `started_at`, `ended_at`, `duration_ms` | TIMESTAMP, TIMESTAMP, BIGINT | Thời gian xử lý bảng | Không |
| `error_message` | STRING | Lỗi của bảng | Không |
| `src_versions_json` | STRING | Node: version đã đọc của từng đầu vào | Cột phải tồn tại trước NB_00 |
| `trg_version` | BIGINT | Node: version bảng đích sau MERGE | Cột phải tồn tại trước NB_00 |
| `deactivated_rows` | BIGINT | Node: số dòng xoá mềm | Cột phải tồn tại trước NB_00 |
| `qg_json` | STRING | Node: kết quả quality gate | Cột phải tồn tại trước NB_00 |

| Cột | Giá trị | Ý nghĩa |
|---|---|---|
| `status` | `SUCCESS`, `FAILED`, `NO_DATA`, `SKIPPED` | `NO_DATA` khi bảng không có event áp dụng |

### 1.6 `ctrl_cdc_state`

Một dòng cho một entity của một bảng đích extract. Nhớ event mới nhất đã áp dụng để lần đọc lại không áp dụng event cũ. Nguồn: `CTRL_TABLES_CONTEXT.md` §8 và `NB_SETUP_INITIAL_DDL` cell 3. Partition `src_tbl`. Không có `NOT NULL`. Không thấy `ConfigError` bắt cột state khác NULL.

| Cột | Kiểu | Ý nghĩa | Required |
|---|---|---|---|
| `trg_schema`, `trg_tbl` | STRING | Bảng đích, thuộc khoá mô tả | Không theo DDL |
| `entity_key` | STRING | Khoá entity. Partner nối khoá ghép bằng `\|`. 3rd-party với `state_key = doc` dùng `poi_id` | Không theo DDL |
| `src_schema`, `src_tbl`, `src_object` | STRING | Nguồn raw và đối tượng | Không |
| `cdc_op` | STRING | Op mới nhất. Snapshot để trống | Không |
| `cdc_ts_ms`, `cdc_lsn` | BIGINT | Thứ tự event. Snapshot: `cdc_lsn` trống | Không |
| `raw_ingested_at` | TIMESTAMP | Thời điểm ingest của event mới nhất | Không |
| `is_deleted` | BOOLEAN | Entity đang xoá mềm | Không |
| `src_version` | BIGINT | Delta version raw của lần áp dụng | Không |
| `last_run_id` | STRING | `run_id` lần cập nhật | Không |
| `updated_at` | TIMESTAMP | Thời điểm cập nhật state | Không |

### 1.7 `ctrl_cdc_reject`

Một dòng cho một event hoặc một phần tử lỗi của extract. Khoá MERGE mô tả là `event_hash`. Nguồn cột: `NB_SETUP_INITIAL_DDL` cell 3. Ý nghĩa và lý do lỗi: `CTRL_TABLES_CONTEXT.md` §9. Partition `src_tbl`. Không có `NOT NULL`.

| Cột | Kiểu | Ý nghĩa | Required |
|---|---|---|---|
| `event_hash` | STRING | Khoá MERGE để cùng một lỗi được đọc lại thì tăng `reject_count`. Partner: `sha2(concat_ws("\u0001", coalesce(_source,""), coalesce(_op,""), coalesce(_before,""), coalesce(_after,"")), 256)` trong `reject_rows` | Không theo DDL |
| `pl_name`, `src_schema`, `src_tbl`, `src_object`, `src_db` | STRING | Pipeline và nguồn. 3rd-party: `src_db` là `source_name` | Không |
| `trg_schema`, `trg_tbl` | STRING | Bảng đích nếu xác định được | Không |
| `cdc_op`, `entity_key`, `cdc_ts_ms`, `cdc_lsn`, `raw_ingested_at` | | Event lỗi. `entity_key` có thể trống khi thiếu khoá | Không |
| `reject_reason`, `reject_detail` | STRING | Mã lý do và mô tả | Không |
| `before_payload`, `after_payload`, `source_payload` | STRING | Payload gốc. 3rd-party: `after_payload` của tài liệu lỗi là cột `normalized_payload` (hằng `RAW_PAYLOAD`). Phần tử lỗi ghi phần tử đó, không ghi cả tài liệu | Không |
| `first_run_id`, `last_run_id` | STRING | Lần đầu và lần gần nhất | Không |
| `reject_count` | INT | Số lần đọc lại cùng lỗi | Không |
| `first_rejected_at`, `last_rejected_at` | TIMESTAMP | Thời điểm tương ứng | Không |
| `is_resolved`, `resolved_at` | BOOLEAN, TIMESTAMP | Đã xử lý hay chưa | Không |

Hash partner đang chạy nằm ở `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb` cell 6 (ô code thứ bảy, id `f68e3e2a`, hàm `reject_rows`): `F.sha2(F.concat_ws("\u0001", *payload), 256)` với `payload` là `coalesce` của `_source`, `_op`, `_before`, `_after` về `""`. `sha2(..., 256)` là SHA-256. Docstring cùng hàm mô tả đúng biểu thức này. `CTRL_TABLES_CONTEXT.md` §9 ghi cùng công thức.

`after_payload` của tài liệu 3rd-party là `_payload`, và `_payload` được gán từ `RAW_PAYLOAD = "normalized_payload"` (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` cell hằng số và `doc_reject_rows` trong cell đọc raw). Comment cột trong `NB_SETUP_INITIAL_DDL` cell 3 ghi `normalized_payload`.

Event bị bỏ qua không ghi vào bảng này. Context §9 nói chúng chỉ được đếm ở `ctrl_log_run.ignored_rows` và `ignored_detail`.

| Cột | Giá trị | Ý nghĩa |
|---|---|---|
| `reject_reason` partner | `INVALID_PAYLOAD`, `MISSING_EVENT_ORDER`, `MISSING_RAW_CURSOR`, `MISSING_ENTITY_KEY` | Payload hỏng, thiếu `ts_ms`, thiếu thời điểm ingest, hoặc khoá NULL |
| `reject_reason` 3rd-party | `MISSING_ENTITY_KEY`, `INVALID_PAYLOAD`, `MISSING_EVENT_ORDER` | Thiếu `source_name` / `source_id`, payload rỗng hoặc không phải object, thiếu `crawled_at` |
| `cdc_op` partner | `c`, `r`, `u`, `d` | Create, read, update, delete của Debezium |
| `is_resolved` | `true`, `false` | `false` là lỗi còn mở |

## 2. Data lineage

Mỗi bảng gold một hình. Hộp trái là bảng nguồn, hộp phải là bảng đích. Mũi tên đi ngang, không ghi kiểu join trên hình. Bảng `enr` đứng trước bảng `dbo`.

### 2.1 `gld_enr_poi_info`

Ghi bằng `APPEND`.

| Nguồn | Kiểu join |
|---|---|
| `slv_poi_entity_non_enrich` | Bảng gốc, sau `left_semi` với tập `poi_id` đổi |
| `slv_poi_amenity` | `left` join sau khi gộp theo `poi_id` |
| `slv_3p_poi_rating` | `left` join theo `poi_id` |
| `slv_3p_poi_price` | `left` join theo `poi_id` |
| `slv_3p_poi_review` | `left_semi` với tập đổi, rồi `left` join |
| `slv_enr_poi_info_multi_lang` | `left` join cờ có mặt theo `poi_id` |
| `slv_enr_poi_destination` | `left` join cờ có mặt theo `poi_id` |
| `slv_pn_business_service_i18ns` | `union` vào tập khoá đổi, rồi `left_semi` với entity. Không join cột |

<table>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_poi_entity_non_enrich</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_enr_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_poi_amenity</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_enr_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_3p_poi_rating</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_enr_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_3p_poi_price</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_enr_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_3p_poi_review</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_enr_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_enr_poi_info_multi_lang</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_enr_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_enr_poi_destination</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_enr_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_pn_business_service_i18ns</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_enr_poi_info</code></td></tr>
</table>

### 2.2 `gld_enr_poi_review`

Ghi bằng `APPEND`.

| Nguồn | Kiểu join |
|---|---|
| `slv_3p_poi_review` | Bảng gốc, sau `left_semi` với tập `review_id` đổi |
| `slv_enr_poi_review_multi_lang` | `left` join cờ theo `review_id`. Khoá thêm hoặc mất còn đi qua `union` |

<table>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_3p_poi_review</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_enr_poi_review</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_enr_poi_review_multi_lang</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_enr_poi_review</code></td></tr>
</table>

### 2.3 `gld_srv_poi_multi_lang`

Ghi bằng `MERGE`.

| Nguồn | Kiểu join |
|---|---|
| `slv_enr_poi_info_multi_lang` | Bảng gốc |
| `slv_poi_entity_non_enrich` | `left` join theo `poi_id` |
| `slv_pn_business_service_i18ns` | `left` join khi nguồn là partner và `lang` trùng `locale` |

<table>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_enr_poi_info_multi_lang</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_multi_lang</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_poi_entity_non_enrich</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_multi_lang</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_pn_business_service_i18ns</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_multi_lang</code></td></tr>
</table>

### 2.4 `gld_srv_poi_info`

Ghi bằng `MERGE`.

| Nguồn | Kiểu join |
|---|---|
| `slv_poi_entity_non_enrich` | Bảng gốc |
| `slv_enr_poi_destination` | `left_semi` để lọc dòng google, rồi `left` join cột địa chỉ |
| `slv_enr_poi_info_multi_lang` | `left_semi` theo `poi_id` để lọc dòng google. Không lấy cột văn bản |
| `slv_3p_poi_rating` | `left_semi` với `poi_id` google, rồi `left` join |
| `slv_3p_poi_review` | `left_semi` với `poi_id` google, `groupBy` đếm, rồi `left` join |

<table>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_poi_entity_non_enrich</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_enr_poi_destination</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_enr_poi_info_multi_lang</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_3p_poi_rating</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_info</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_3p_poi_review</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_info</code></td></tr>
</table>

### 2.5 `gld_srv_poi_media_gallery`

Ghi bằng `MERGE`. Không join. Đọc một bảng rồi `select`.

<table>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_poi_media_info</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_media_gallery</code></td></tr>
</table>

### 2.6 `gld_srv_poi_amenity`

Ghi bằng `MERGE`. Không join. Đọc một bảng rồi `select`.

<table>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_poi_amenity</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_amenity</code></td></tr>
</table>

### 2.7 `gld_srv_poi_review`

Ghi bằng `MERGE`.

| Nguồn | Kiểu join |
|---|---|
| `slv_enr_poi_review_multi_lang` | Bảng gốc |
| `slv_3p_poi_review` | `inner` join theo `review_id` |
| `slv_3p_poi_rating` | `left` join theo `poi_id` |

<table>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_enr_poi_review_multi_lang</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_review</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_3p_poi_review</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_review</code></td></tr>
<tr><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>slv_3p_poi_rating</code></td><td style="width:48px;border:none;text-align:center;vertical-align:middle">→</td><td style="width:340px;height:40px;border:1px solid #222;text-align:center;vertical-align:middle"><code>gld_srv_poi_review</code></td></tr>
</table>

`lh_vv_gold.enr.gld_enr_poi_coordinate` không có trong `TABLE_SPECS` hiện hành và không có notebook node, nên không có hình.

## 3. Thêm một field bronze sang silver

Field mới là một cột silver L1 đọc từ JSON của raw đang có. Hai raw hiện hành: `lh_vv_bronze.dbo.partner_raw_data` và `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`. Không điền `json_path` khi chưa thấy khoá đó trong payload. Câu dưới đây chạy được cả khi bảng ctrl còn trống và khi bảng đã có dòng: `MERGE` chỉ thêm dòng chưa khớp khoá.

### Step 1. Ghi một dòng vào `ctrl_cfg_schema_registry`

```sql
MERGE INTO lh_vv_ctrl.dbo.ctrl_cfg_schema_registry AS t
USING (
    SELECT
        '<src_schema>' AS src_schema,
        '<src_tbl>' AS src_tbl,
        '<src_object_schema>' AS src_object_schema,
        '<src_object>' AS src_object,
        'lh_vv_silver.dbo' AS trg_schema,
        '<trg_tbl>' AS trg_tbl,
        '<trg_column>' AS trg_column,
        '<json_path>' AS json_path,
        '<data_type>' AS data_type,
        CAST(NULL AS STRING) AS convert_arg,
        '<convert_rule>' AS convert_rule,
        false AS is_key,
        CAST(NULL AS INT) AS key_order,
        false AS is_toast,
        <column_order> AS column_order,
        true AS is_active,
        '<description>' AS description
) AS s
ON t.src_schema = s.src_schema AND t.src_tbl = s.src_tbl
   AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl
   AND t.trg_column = s.trg_column
WHEN NOT MATCHED THEN INSERT (
    src_schema, src_tbl, src_object_schema, src_object, trg_schema, trg_tbl, trg_column,
    json_path, data_type, convert_arg, convert_rule, is_key, key_order, is_toast,
    column_order, is_active, description
) VALUES (
    s.src_schema, s.src_tbl, s.src_object_schema, s.src_object, s.trg_schema, s.trg_tbl, s.trg_column,
    s.json_path, s.data_type, s.convert_arg, s.convert_rule, s.is_key, s.key_order, s.is_toast,
    s.column_order, s.is_active, s.description
)
```

Partner: `src_schema` = `lh_vv_bronze.dbo`, `src_tbl` = `partner_raw_data`, `src_object_schema` là schema Debezium (`public`), `src_object` là bảng nguồn (`products`). `convert_rule` để `NONE` khi chỉ đổi kiểu. Cột khoá thì `is_key` = `true` và `key_order` là số, không để `NULL`.

3rd-party: `src_tbl` = `brz_3rd_crawler_poi_stream`. `src_object` = `$` khi cột nằm ở gốc payload. `is_toast` luôn `false`.

### Step 2. Giá trị phải qua được kiểm tra của extract

Lần chạy extract gọi `build_table_specs`. Sai thì `ConfigError` và không ghi bảng đích. Cột mới cần:

```text
trg_column là identifier, không trùng cột kỹ thuật
column_order không NULL và không trùng
json_path hợp lệ với load_mode
data_type qua CAST(NULL AS <kiểu>)
is_key = false thì key_order để trống
CDC không dùng HASH_*
snapshot thì is_toast = false
```

Cột thêm vào bảng đã có phải cho phép NULL.

### Step 3. Chạy notebook extract để thêm cột vật lý

Không viết `ALTER` tay. `ensure_target` trong `NB_LIB_EXTRACT_RAWDATA` tự chạy khi registry có cột mà bảng đích chưa có:

```python
spark.sql(
    f"ALTER TABLE {quote_name(spec.fq_name)} ADD COLUMNS ("
    + ", ".join(f"`{n}` {t.upper()}" for n, t in missing)
    + ")"
)
```

Lệch kiểu thì `ConfigError`, không thêm cột.

### Step 4. Nạp dữ liệu cũ của cột mới

3rd-party, dữ liệu cũ:

```python
table_filter = "<trg_tbl>"
full_reload = True
```

Partner dùng cùng cặp tham số khi cần đọc lại vài bảng. Watermark không đổi. Partner không bắt buộc bước này chỉ vì thêm một cột.

## 4. Thêm một bảng bronze sang silver

Một bảng mới là một bảng silver L1 từ raw partner hoặc 3rd-party. `ensure_target` tạo bảng khi extract chạy. Không có lệnh `CREATE TABLE` riêng cho `slv_pn_*` và `slv_3p_poi*`. Câu `MERGE` dưới đây chỉ thêm dòng chưa có, nên chạy được trên môi trường trống và môi trường đã có dữ liệu.

### Step 1. Ghi một dòng `ctrl_mng_pipeline_config`

```python
base = int(spark.sql("SELECT COALESCE(MAX(id), 0) AS m FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config").first()["m"])
spark.sql(f"""
    MERGE INTO lh_vv_ctrl.dbo.ctrl_mng_pipeline_config AS t
    USING (
        SELECT
            'PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00' AS pl_name,
            'lh_vv_bronze.dbo' AS src_schema,
            '<src_tbl>' AS src_tbl,
            'lh_vv_silver.dbo' AS trg_schema,
            '<trg_tbl>' AS trg_tbl,
            1 AS is_active,
            1 AS priority,
            '<load_mode>' AS load_mode,
            CAST(NULL AS STRING) AS align_path,
            CAST(NULL AS STRING) AS dedup_order,
            CAST(NULL AS STRING) AS nb_name
    ) AS s
    ON t.pl_name = s.pl_name AND t.src_schema = s.src_schema AND t.src_tbl = s.src_tbl
       AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl
    WHEN NOT MATCHED THEN INSERT (
        id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority,
        load_mode, align_path, dedup_order, nb_name
    ) VALUES (
        {base + 1}, s.pl_name, s.src_schema, s.src_tbl, s.trg_schema, s.trg_tbl, s.is_active,
        s.priority, s.load_mode, s.align_path, s.dedup_order, s.nb_name
    )
""")
```

Partner: `src_tbl` = `partner_raw_data`, `load_mode` = `CDC`. 3rd-party: `src_tbl` = `brz_3rd_crawler_poi_stream`, `load_mode` = `DOC` hoặc `DOC_ARRAY`. `align_path` chỉ điền khi `DOC_ARRAY`.

### Step 2. Ghi mọi cột, kể cả khoá, vào registry

Mỗi cột một lần `MERGE` của mục 3 Step 1. Ít nhất một cột có `is_key` = `true` và `key_order` không trống. `column_order` bắt đầu từ 1, không trùng.

### Step 3. Watermark chỉ khi đây là raw mới

Thêm bảng đích trên raw đã có thì không thêm watermark. Raw mới cần một dòng, `watermark_id` = `wm_transform_<src_tbl>`, `trg_tbl` để trống:

```sql
MERGE INTO lh_vv_ctrl.dbo.ctrl_mng_watermark AS t
USING (
    SELECT
        'wm_transform_<src_tbl>' AS watermark_id,
        'lh_vv_bronze.dbo' AS src_schema,
        '<src_tbl>' AS src_tbl,
        '<watermark_column>' AS watermark_column,
        'INITIALIZED' AS status,
        '<notebook_extract>' AS flow_name,
        CAST(-1 AS BIGINT) AS watermark_sequence
) AS s
ON t.watermark_id = s.watermark_id
WHEN NOT MATCHED THEN INSERT (
    watermark_id, src_schema, src_tbl, trg_schema, trg_tbl,
    watermark_column, watermark_value, last_success_at, status, flow_name,
    watermark_sequence, last_run_id, last_src_version, last_src_table_id, error_message,
    lock_exec_id, lock_at, updated_at
) VALUES (
    s.watermark_id, s.src_schema, s.src_tbl, CAST(NULL AS STRING), CAST(NULL AS STRING),
    s.watermark_column, CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP), s.status, s.flow_name,
    s.watermark_sequence, CAST(NULL AS STRING), CAST(NULL AS BIGINT), CAST(NULL AS STRING),
    CAST(NULL AS STRING), CAST(NULL AS STRING), CAST(NULL AS TIMESTAMP), current_timestamp()
)
```

Partner: `watermark_column` = `EventProcessedUtcTime`. 3rd-party: `crawled_at`.

### Step 4. Kiểm tra trước lần ghi dữ liệu

`build_table_specs` báo `ConfigError` nếu `priority` NULL, tên đích không hợp lệ, trùng bảng đích, không có cột active, không có khoá, `key_order` hoặc `column_order` trống hoặc trùng, hoặc `load_mode` không thuộc notebook. 3rd-party còn cần mọi bảng có cột `doc_key_column`.

### Step 5. Chạy extract lần đầu

Không chạy incremental khi raw đã có con trỏ.

Raw chưa có `last_src_version`:

```python
allow_full_scan = True
```

Raw đã có `last_src_version`:

```python
table_filter = "<trg_tbl>"
full_reload = True
```

Incremental chỉ đọc phần sau con trỏ, và lần `SUCCESS` tiến con trỏ, nên event cũ của bảng mới không được đọc lại. `full_reload` và `table_filter` không đổi watermark. `ensure_target` tạo bảng đích trong lần chạy này.

### Step 6. Tắt bảng

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
SET is_active = 0
WHERE pl_name = 'PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00'
  AND src_tbl = '<src_tbl>'
  AND trg_tbl = '<trg_tbl>';
```

Partner chỉ `CDC`. 3rd-party chỉ `DOC` hoặc `DOC_ARRAY`. Trộn mode thì `ConfigError` trước khi ghi.

## 5. Tham số notebook

Tham số bắt buộc là tham số để trống hoặc sai miền thì `ConfigError` trước khi ghi. Giá trị mặc định lấy từ cell tham số. Ý nghĩa lấy từ cell đó và từ context khi hai bên không lệch.

### 5.1 `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`

File `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` cell 1. Kiểm tra: `build_context` và `check_config` ở cell 12. Context: `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §4.

| Tham số | Mặc định trong cell 1 | Ý nghĩa | Bắt buộc |
|---|---|---|---|
| `pl_name` | `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` | Pipeline, khớp `ctrl_mng_pipeline_config.pl_name` | Không thấy kiểm trống. Dòng config không khớp thì không có bảng active và `ConfigError` ở `build_table_specs` |
| `run_id` | `""` | Trống thì dùng `exec_id` | Không |
| `src_schema` | `lh_vv_bronze.dbo` | Schema raw | `src_schema.src_tbl` phải `is_fq_name`, sai thì `ConfigError` |
| `src_tbl` | `brz_3rd_crawler_poi_stream` | Bảng raw | Cùng điều kiện với `src_schema` |
| `allow_full_scan` | `True` | Cho đọc FULL khi không đọc theo version | Không |
| `max_parallel` | `12` | Số bảng đồng thời trong một wave | Không thấy kiểm miền trong `build_context` |
| `max_retries` | `1` | Số lần thử lại một bảng khi lỗi tạm thời | Không |
| `table_filter` | `""` | Danh sách `trg_tbl`. Trống là mọi bảng active | Tên lạ thì `ConfigError` ở `build_table_specs` |
| `full_reload` | `False` | Đọc hết raw và bỏ state. Watermark không đổi | Không |
| `dry_run` | `False` | Chỉ đọc và đếm, không ghi | Không |
| `stop_on_failure` | `False` | Wave lỗi thì không chạy wave sau | Không |
| `cast_null_policy` | `FAIL` | `FAIL` hoặc `WARN` | Sai miền thì `ConfigError` |
| `running_timeout_minutes` | `780` | Hạn khoá nguồn, 13 giờ | Không thấy kiểm miền trong `build_context` |
| `sources` | `google` | `source_name` được xử lý. Trống là mọi nguồn | Không. Ngoài danh sách thì IGNORED, không phải `ConfigError` |
| `doc_key_column` | `poi_id` | Cột định danh tài liệu | Phải là identifier. Mọi bảng phải có cột này, nếu không thì `ConfigError` ở `check_config` |
| `state_key` | `doc` | `doc` hoặc `row`, cách lấy `entity_key` | Sai thì `ConfigError` |

Cấu hình bắt buộc là các dòng pipeline config và registry của `brz_3rd_crawler_poi_stream`, `load_mode` thuộc mode snapshot của notebook. Notebook `%run NB_LIB_EXTRACT_RAWDATA` ở cell 2. Tái sử dụng lib đó cho nguồn khác bằng một notebook extract riêng, không sửa lib. Context vận hành §10: chưa có activity của notebook này trong `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`.

### 5.2 `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`

File `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb` cell 1. Kiểm tra: `build_context` cell 12. Context: `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` §3.

| Tham số | Mặc định trong cell 1 | Ý nghĩa | Bắt buộc |
|---|---|---|---|
| `pl_name` | `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` | Pipeline gắn với chuỗi này | Cùng cách nạp config như 3rd-party |
| `run_id` | `""` | Trống thì `exec_id` | Không |
| `src_schema` | `lh_vv_bronze.dbo` | Schema raw | `is_fq_name` của `src_schema.src_tbl`, sai thì `ConfigError` |
| `src_tbl` | `partner_raw_data` | Bảng raw | Cùng điều kiện |
| `overlap_minutes` | `10` | Không còn dùng. Giữ để caller cũ không lỗi | Không |
| `allow_full_scan` | `True` | Cho đọc FULL | Không |
| `max_parallel` | `12` | Số bảng đồng thời trong một wave | Không |
| `max_retries` | `1` | Thử lại bảng khi lỗi tạm thời | Không |
| `table_filter` | `""` | Danh sách `trg_tbl` | Tên lạ thì `ConfigError` |
| `full_reload` | `False` | Đọc hết raw, bỏ state | Không |
| `dry_run` | `False` | Không ghi | Không |
| `stop_on_failure` | `False` | Dừng wave sau khi wave lỗi | Không |
| `cast_null_policy` | `FAIL` | `FAIL` hoặc `WARN` | Sai miền thì `ConfigError` |
| `running_timeout_minutes` | `780` | Hạn khoá 13 giờ | Không |

Cấu hình bắt buộc: dòng pipeline config active của `partner_raw_data` với `load_mode` `CDC` hoặc trống, cộng registry CDC của từng bảng. `%run NB_LIB_EXTRACT_RAWDATA` ở cell 2. Không có `sources`, `doc_key_column`, `state_key`.

### 5.3 `NB_00_ORCHES_SLV_TO_ENR`

File `notebooks/NB_00_ORCHES_SLV_TO_ENR.ipynb`. Cell 0 ghi tên này. Cell 1 đặt `p_pl_name = "PL_VV_TRANS_SLV_TO_ENR_15M"`. Cùng tên pipeline ở `02_NAMING_CONVENTION.md` §3, `01_DATA_MODEL.md` §7 và `NB_00_ORCHES_SLV_TO_GLD.md` §3. Không có chuỗi `PL_VV_TRANS_SLV_TO_ENR_30P` trong repository.

Activity trong `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json` vẫn tên `NB_00_ORCHES_SLV_TO_ENR_15P`. `notebookId` của activity là tham số `nb_orches_id`, không phải tên file. Tên activity này không được đổi trong lượt này.

Các tham số còn lại lấy từ cell 1 của file và từ `_validate_orch_params` (`NB_LIB_TRANSFORM_SLV_GLD` cell 13). Bảng ý nghĩa chung với gold ở mục 5.4. Miền số không phụ thuộc tên pipeline.

### 5.4 `NB_00_ORCHES_SLV_TO_GLD`

File `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb` cell 1. Context: `docs/context/NB_00_ORCHES_SLV_TO_GLD.md` §3–§5. Cell 1 và §3 cùng mặc định `p_pl_name` = `PL_VV_TRANSFORM_SLV_TO_GLD_1H`. `02_NAMING_CONVENTION.md` §3 còn ghi `PL_VV_TRANS_SLV_TO_GLD_30M` và nói repository chưa có JSON pipeline. `NB_SETUP_INITIAL_DDL` cell 7 khai báo cả hai hằng `_GLD30` và `_GLD1H`. Hai tên này cùng có trong repository. Mặc định trong cell tham số của notebook gold là `PL_VV_TRANSFORM_SLV_TO_GLD_1H`.

`_validate_orch_params` áp dụng cho cả hai notebook orches.

| Tham số | Mặc định cell 1 gold | Ý nghĩa | Bắt buộc |
|---|---|---|---|
| `p_pl_name` | `PL_VV_TRANSFORM_SLV_TO_GLD_1H` | Pipeline cần chạy. Phải là identifier | Trống hoặc không phải identifier thì `ConfigError`. Không có cạnh active của pipeline thì `ConfigError` ở `build_dag` |
| `p_run_id` | `""` | Trống thì `exec_id` | Không |
| `p_mode` | `RUN` | `RUN`, `PLAN`, hoặc `DRY_RUN` | Sai miền thì `ConfigError`. Mặc định trong code khi trống là `RUN` |
| `p_max_parallel` | `3` trên notebook gold, `2` trên file enrich | Số node đồng thời, từ 1 đến 8 | Ngoài miền thì `ConfigError` |
| `p_node_timeout_min` | `20` gold, `15` enrich | Timeout một node, từ 1 đến 240, không lớn hơn timeout DAG | Ngoài miền hoặc lớn hơn DAG thì `ConfigError` |
| `p_dag_timeout_min` | `45` gold, `25` enrich | Timeout cả DAG, từ 1 đến 720 | Ngoài miền thì `ConfigError` |
| `p_lock_timeout_min` | `90` gold, `35` enrich | Hạn khoá của lần chạy, từ 5 đến 1440, và phải lớn hơn `p_dag_timeout_min + 5` | Sai thì `ConfigError` |
| `p_force_nodes` | `""` | CSV `trg_tbl` ép chạy cùng hậu duệ | Tên không phải node của pipeline thì `ConfigError` ở `plan_run` |
| `p_history_limit` | `1000` | Số commit tối đa khi xét một đầu vào, từ 10 đến 100000 | Ngoài miền thì `ConfigError` |
| `p_non_data_ops` | `""` | CSV operation không đổi dữ liệu. Trống thì `DEFAULT_NON_DATA_OPS` | Không |

Cấu hình bắt buộc của một lần chạy orches:

- Các cạnh active trong `ctrl_mng_pipeline_config` với `load_mode` `RECOMPUTE` hoặc `APPEND`, qua `build_dag`.
- Bốn cột log node đã có, qua `require_ctrl_columns`.
- Bảng đầu vào ngoài đã tồn tại. Thiếu thì `ConfigError` ở `plan_run`.

Cách tái sử dụng: một lib `NB_LIB_TRANSFORM_SLV_GLD`, hai notebook orches. Cell 2 của mỗi notebook là `%run NB_LIB_TRANSFORM_SLV_GLD`. Cell cuối gọi `orchestrate(...)`. `p_pl_name` chọn luồng. Cạnh trong ctrl chọn node và notebook con. `nb_name` trống thì tên notebook con là `NB_<UPPER(trg_tbl)>` (`build_dag`, cell 7).

Notebook con được `runMultiple` gọi với các tham số `p_exec_id`, `p_run_id`, `p_pl_name`, `p_trg_fq`, `p_mode`, `p_force`, `p_history_limit`, `p_pinned_json` (`build_run_multiple_dag`, cell 13). Khung dưới đây lấy từ `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md` §5. Không thêm file ipynb.

```python
# cell 1 — tham số (pipeline / NB_00 truyền chuỗi)
p_exec_id = ""; p_run_id = ""; p_pl_name = ""; p_trg_fq = ""; p_pinned_json = ""
p_mode = "RUN"; p_force = "false"; p_history_limit = "1000"
# cell 2
%run NB_LIB_TRANSFORM_SLV_GLD
# cell 3
def build(ctx: NodeContext) -> DataFrame:
    src = ctx.input("src_map")          # vai trò khai báo trong inputs
    ...                                 # chỉ cột nghiệp vụ, 1 dòng / khoá, mảng đã array_sort
    return df
SPEC = NodeSpec(
    trg_tbl="slv_poi",
    inputs={"src_map": "slv_poi_source_map"},
    pk=("poi_id",),
    build=build,
    required_inputs=("src_map",),
    soft_delete_set={},
)
# cell 4
RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_name, p_trg_fq, p_history_limit)
# cell 5
notebookutils.notebook.exit(finish_node(RES))
```

`NodeSpec` định nghĩa ở `NB_LIB_TRANSFORM_SLV_GLD` cell 11. `inputs` phải khớp các cạnh của node. `build` trả DataFrame cột nghiệp vụ. Chạy tay một node để trống `p_exec_id`. Context §5: dấu đã đọc của cạnh chỉ NB_00 ghi.

Sub-notebook không chạy nếu thiếu `%run` lib, thiếu `SPEC`, hoặc `inputs` không khớp cạnh active của `p_pl_name`.
