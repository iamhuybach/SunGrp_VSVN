# NB_LIB_TRANSFORM_SLV_GLD — Thư viện luồng tính lại silver → silver L2 → gold

> Cập nhật: 08/10/2026. Bản code: `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`. 8 mục, ~1.740 dòng. Thiết kế: `claude/GOLD_POI_FLOW_DESIGN.md` §5, §12. Bản vá: `PATCH_REVIEW_0510.md`.
> Điều phối: `NB_00_ORCHES_SLV_TO_GLD.md`. Bảng ctrl: `CTRL_TABLES_CONTEXT.md`.

## 1. Mô tả

Thư viện `%run` cho mọi luồng kiểu **"tính lại toàn bộ + MERGE theo `row_hash` + xoá mềm"**, điều khiển bằng dữ liệu (`ctrl_mng_pipeline_config` với `load_mode = 'RECOMPUTE'`). Không phụ thuộc POI: luồng khác dùng lại bằng dòng config + notebook node.

Gồm 2 phần dùng ở 2 nơi:
- **Phía node** (`run_node`): mỗi notebook node chỉ khai báo `NodeSpec` + hàm `build(ctx)`; lib lo khoá, version đọc, hộp thư, QG, row_hash, MERGE, log.
- **Phía điều phối** (`orchestrate`): NB_00 lập kế hoạch, chốt version, gọi `notebookutils.notebook.runMultiple`, gom kết quả, tiến cạnh.

| | |
|---|---|
| Được gọi bởi | `NB_00_ORCHES_SLV_TO_GLD` |
| Đọc / ghi khi `%run` | Không |
| Default lakehouse | `lh_vv_bronze` (bắt buộc giống nhau với runMultiple) |
| Tự chứa | Không `%run NB_LIB_EXTRACT_RAWDATA`; `with_retry`, `append_rows`, `quote_name`… **chép mẫu** từ lib extract, giữ hành vi |
| Bảng ctrl dùng | `ctrl_mng_pipeline_config` (đọc), `ctrl_mng_watermark` (cạnh + khoá), `ctrl_log_run`, `ctrl_log_table_run` + 5 cột log mới |

## 2. Ý nghĩa / mô hình

| Khái niệm | Định nghĩa |
|---|---|
| **Cạnh** | 1 dòng config `RECOMPUTE`: src = bảng đầu vào, trg = node. Cùng khoá với 1 dòng watermark `wm_e__<trg_tbl>__<src_tbl>` = **hộp thư** của cạnh |
| **Node** | 1 `trg_schema.trg_tbl`; notebook = cột `nb_name` (nếu có) hoặc `NB_<UPPER(trg_tbl)>`; thuộc đúng 1 pl active |
| **Đầu vào ngoài** | Bảng đầu vào không phải node của pl này (silver L1, ref, bảng gold cũ, node của pl khác) |
| **Cạnh bẩn** (cần tính lại) | Chưa đọc lần nào; bảng đầu vào bị tạo lại (table id khác); có commit **đổi dữ liệu** sau version đã đọc (đọc `DeltaTable.history()`, bỏ OPTIMIZE / VACUUM / đổi property / MERGE 0 dòng); history không đủ; version đọc nhỏ hơn version đã đọc |
| **Node ứng viên** | Node có cạnh bẩn ∪ `p_force_nodes` ∪ node chưa có bảng đích, cộng mọi hậu duệ |
| **Dấu đã đọc** | `last_src_version` của cạnh = version node đã đọc ở lần thành công gần nhất (NB_00 ghi sau khi node xong) |

Vì sao không dùng `updated_at` / `status` của watermark extract: đổi cả khi không có dữ liệu mới (khoá, NO_DATA, FAILED); dòng watermark là theo nguồn raw (1 dòng cho 23 bảng); sửa tay ref / RESTORE không chạm ctrl; so giờ giữa tiến trình không chắc chắn. So **số version của cùng 1 bảng** thì chắc chắn (ADR-G01).

Vì sao tính lại toàn bộ thay vì incremental: dữ liệu ~19k POI, logic nhiều nhánh (định danh, fallback tên, destination); tính lại + MERGE theo `row_hash` cho kết quả tái lập được, `updated_at` chỉ đổi khi nội dung đổi → sync PG nhẹ (ADR-G02).

## 3. Cấu trúc

| § | Nhóm | Nội dung |
|---|---|---|
| 1 | constants | Bảng ctrl, chế độ chạy, commit không đổi dữ liệu, metric theo operation, cột kỹ thuật, hằng khoá |
| 2 | common | Thời gian, tham số, log, retry, tên bảng, append theo schema, JSON, nhịp pl, id cạnh / khoá |
| 3 | delta | Trạng thái bảng, history, commit đổi dữ liệu, `HistoryCache`, đọc theo version |
| 4 | config / DAG | `Edge`, `Dag`, đọc cạnh, `build_dag` + kiểm tra |
| 5 | ctrl | Hộp thư cạnh, khoá luồng, run log, table log, ghim theo batch extract |
| 6 | node | `NodeSpec`, `NodeContext`, row_hash, QG, diff, MERGE, `run_node` |
| 7 | orchestrator | `Plan`, `plan_run`, DAG runMultiple, gom kết quả, tiến cạnh, `orchestrate` |
| 8 | build helpers | Chuẩn hoá chữ, bỏ dấu, slug, uuid md5, epoch, JSON |

## 4. Chi tiết hàm

### §1 constants

| Tên | Giá trị / ý nghĩa |
|---|---|
| `T_PIPELINE_CONFIG`, `T_WATERMARK`, `T_LOG_RUN`, `T_LOG_TABLE_RUN` | Bảng ctrl dùng |
| `EDGE_LOAD_MODE` | `RECOMPUTE` |
| `RUN_MODES` / `NODE_MODES` | `RUN, PLAN, DRY_RUN` / `RUN, DRY_RUN` |
| `NODE_OK` / `NODE_BAD` | `SUCCESS, NO_DATA` / `FAILED, SKIPPED, NOT_RUN` |
| `WATERMARK_COLUMN_EDGE` | `commit_ts` |
| `DEFAULT_NON_DATA_OPS` | `OPTIMIZE`, `VACUUM START/END`, `SET/UNSET TBLPROPERTIES`, `ADD/CHANGE/REPLACE COLUMNS`, `UPGRADE PROTOCOL`, `ADD/DROP CONSTRAINT`, `FSCK`, `CREATE TABLE`, `REORG`. Không có `DROP COLUMNS`, `RESTORE`, `TRUNCATE`, `CREATE OR REPLACE` → coi là đổi dữ liệu |
| `OP_ROW_METRICS` | Metric đếm dòng đổi theo operation (`MERGE`: inserted / updated / deleted; `UPDATE`, `DELETE`, `WRITE`, `STREAMING UPDATE`, `CTAS`) |
| `TECH_COLUMNS` / `TECH_NAMES` | `row_hash`, `created_at`, `updated_at`, `deleted_at` |
| `TABLE_PROPERTIES` | `optimizeWrite` + `autoCompact` |
| `LOCK_TIMEOUT_DEFAULT_MIN` | 90: node chạy tay dùng số phút này để xét `lock_at` quá hạn |
| `CADENCE_RE`, `CADENCE_UNIT_MIN` | Nhịp từ hậu tố pl: `_15M` = 15, `_1H` = 60, `_1D` = 1440 |
| `NEW_LOG_COLUMNS` | 5 cột log mới phải có (`require_ctrl_columns`) |

### §2 common

| Hàm | Mô tả |
|---|---|
| `ConfigError`, `QualityGateError` | Cấu hình sai (không thử lại) / QG chặn (không MERGE). Notebook không có `LockLostError` |
| `utc_now`, `to_bool`, `split_csv`, `short_error`, `log(msg, level, node)` | Như lib extract (log gắn tên node) |
| `is_transient`, `with_retry` | Như lib extract (6 lần, jitter) |
| `is_identifier`, `is_fq_name`, `quote_name`, `table_exists`, `table_columns` | Tên an toàn; cột lower → kiểu |
| `append_rows(table, rows)` | Append theo schema bảng (chép từ lib extract) |
| `json_dumps(obj)` | JSON gọn, giữ tiếng Việt, **khoá sắp xếp** (ổn định khi so), datetime → ISO |
| `current_notebook_name(default)` | Tên notebook đang chạy |
| `cadence_minutes(pl_name)` | `"PL_X_1H"` → 60; không hậu tố → None |
| `edge_wm_id(src_tbl, trg_tbl)` / `flow_lock_id(pl)` | `wm_e__<trg>__<src>` / `wm_flow__<pl>` |
| `require_ctrl_columns()` | Bảng log đã có 5 cột mới chưa; thiếu → `ConfigError` (tránh `append_rows` bỏ cột âm thầm) |

### §3 delta

| Hàm | Mô tả |
|---|---|
| `table_state(fq)` | `{version, table_id, commit_ts}` (history(1) + DESCRIBE DETAIL); chưa có bảng → None |
| `table_history(fq, n)` | n commit mới nhất: version, operation, metrics, params, ts |
| `is_data_change(commit, non_data_ops)` | Commit có đổi dữ liệu không. **Không chắc → True** (chạy thừa, không bỏ sót): operation NULL (Eventstream), op không biết, thiếu metric, `WRITE` overwrite, `RESTORE` → True; `OPTIMIZE`, MERGE 0 dòng → False |
| `HistoryCache(non_data_ops, history_limit)` | Đọc history mỗi bảng 1 lần / lần chạy. `changes(fq, v_from, v_to, v_current)` → (version đổi dữ liệu, complete). `v_current - v_from > history_limit` hoặc thiếu version (log bị dọn) → complete = False |
| `read_at(fq, version)` | `VERSION AS OF` |
| `read_current(fq)` | Bản hiện tại hoặc None |

### §4 config / DAG

| Tên | Mô tả |
|---|---|
| `Edge` (frozen) | `pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`, `nb_name`; `src_fq`, `trg_fq`, `wm_id` |
| `Dag` | `pl_name`, `edges`, `nodes` {trg_fq: {name, nb, edges}}, `order` (topo), `level` (0 = chỉ đọc đầu vào ngoài), `parents`, `children`, `external` {src_fq: pl sở hữu \| None}; `descendants(starts)`, `node_by_name(name)` |
| `load_config_rows()` | Cạnh active `RECOMPUTE` của **mọi** pl (để kiểm tra 1 node 1 chủ); cột `nb_name` tuỳ chọn |
| `node_owner(rows, trg_fq)` | Các pl có cạnh ghi vào node |
| `build_dag(rows, pl_name)` | Dựng DAG + kiểm tra, gom mọi lỗi: tên hợp lệ; không trùng cạnh / id watermark; node chỉ thuộc pl này; node trùng tên bảng khác schema (tên activity runMultiple); không chu trình (Kahn); node không tự đọc chính nó; **pl nhanh không đọc node của pl chậm**; mọi cạnh của 1 node cùng `nb_name` |

### §5 ctrl

| Hàm | Mô tả |
|---|---|
| `WM_EDGE_SCHEMA` | Schema dòng ghi cạnh (có cờ `advance`) |
| `load_edge_wm(edges)` | Dòng watermark các cạnh → {(src_fq, trg_fq): {version, table_id, ts, status}}; id đúng nhưng src / trg lệch config → `ConfigError` |
| `edge_status(consumed, state, read_version, hist, src_fq)` | → (bẩn, lý do, versions): `MISSING_TABLE`, `NEW_EDGE`, `TABLE_RECREATED`, `VERSION_BACKWARD`, `UNCHANGED`, `HISTORY_GAP`, `DATA_CHANGED` (kèm ≤ 20 version), `MAINTENANCE_ONLY` |
| `sql_merge_edge_wm(view)` / `merge_edge_wm(rows, tag)` | 1 MERGE. `advance`: ghi version / table id / commit ts khi `last_src_version` đang lưu NULL, table id NULL, table id khác, hoặc version mới ≥ version đang lưu. Không `advance`: chỉ trạng thái + lỗi. Chưa có dòng → INSERT. Không có `EXISTS` dòng khoá |
| `sql_ensure_lock_row`, `ensure_lock_row(pl, flow_name)` | Tạo dòng `wm_flow__<pl>` nếu chưa có (`src_tbl = pl`, `watermark_column` NULL, INITIALIZED) |
| `_lock_expired_sql(timeout_min)` | `coalesce(lock_at < current_timestamp() - INTERVAL {timeout_min} MINUTES, true)`. `timeout_min` là của run đang xét |
| `read_flow_lock(pl, timeout_min)` | `lock_exec_id`, `lock_at`, `expired` |
| `acquire_flow_lock(pl, exec_id, run_id, timeout_min)` | `UPDATE` `lock_exec_id`, `lock_at = current_timestamp()`, `status = RUNNING`, `last_run_id` khi khoá trống hoặc quá hạn, rồi đọc lại. Không ghi `watermark_column` / `watermark_value` |
| `release_flow_lock(pl, exec_id, status)` | Xoá `lock_exec_id` và `lock_at`, ghi `status`, chỉ khi `lock_exec_id` còn là mình |
| `close_stale_runs(pl, exec_id, timeout_min)` | Run log RUNNING khác quá hạn → `ABANDONED`. `orchestrate` gọi hàm này trước `acquire_flow_lock` |
| `write_run_log(row)` / `update_run_log(exec_id, values)` | Append dòng run log / UPDATE khi đóng |
| `write_node_log(row)` / `node_logs(exec_id)` | Node append 1 dòng `ctrl_log_table_run` / NB_00 đọc dòng mới nhất của từng node |
| `last_output_versions(pl)` | `output_versions_json` của run SUCCESS / NO_DATA gần nhất của pl. `plan_run` dùng cho node thuộc pl khác; không có hoặc version lớn hơn hiện tại → đọc version hiện tại và cảnh báo |

### §6 node

Các bước `run_node`:

| # | Việc |
|---|---|
| 1 | `require_ctrl_columns`; đọc config; `_resolve_node`: đúng 1 bảng đích, đúng 1 pl, `spec.inputs` khớp cạnh |
| 2 | Khoá: qua NB_00 → `p_exec_id` phải đang giữ khoá luồng; chạy tay RUN → tự nhận khoá (hạn 90'); không được → chỉ cho DRY_RUN; DRY_RUN khi luồng đang chạy → cảnh báo |
| 3 | Qua NB_00: node cha lỗi / bị bỏ qua trong cùng exec → `SKIPPED` |
| 4 | Version đọc: đầu vào ngoài = `p_pinned_json` (chạy tay: version hiện tại, node của pl khác lấy `last_output_versions`), node cha = hiện tại. `edge_status` từng cạnh; không cạnh nào bẩn, không `p_force`, bảng đích đã có → `NO_DATA` |
| 5 | `required_inputs` rỗng → QG chặn (chống xoá mềm hàng loạt); `build(ctx)` → `add_row_hash` → `quality_gate` → `diff_counts` |
| 6 | RUN: `ensure_target` → MERGE (bỏ qua khi diff = 0) → `trg_version`. Không kiểm khoá lại ngay trước MERGE. DRY_RUN dừng ở diff |
| 7 | `finally`: append 1 dòng `ctrl_log_table_run` (cả FAILED / SKIPPED / NO_DATA), nhả khoá nếu tự nhận |

| Tên | Mô tả |
|---|---|
| `NodeSpec` | `trg_tbl`; `inputs` {vai trò: src_tbl} (phải khớp đúng cạnh); `pk`; `build`; `required_inputs`; `unique_checks` ((tên, cột, điều kiện lọc)); `block_checks` ((tên, điều kiện dòng lỗi)); `warn_checks`; `hash_exclude`; `soft_delete_set` (vd `{"is_active": "false"}`); `reads_self`; `block_empty_output` (review #3: build ra 0 dòng → chặn) |
| `NodeContext` | `input(role, live_only=True)`: đọc đầu vào theo version đã chốt; bảng do lib ghi → chỉ dòng `deleted_at IS NULL`, bỏ 4 cột kỹ thuật. `is_empty(role)`, `current_target()` (gồm dòng xoá mềm), `warn(name, n)` (vào `qg_json`), `metrics` |
| `_hash_expr`, `add_row_hash(df, spec)` | `row_hash = sha2(to_json(struct(cột nghiệp vụ theo thứ tự DataFrame trừ hash_exclude)), 256)`; timestamp → `unix_micros`, date → chuỗi (không phụ thuộc timezone). Chặn: build trả cột kỹ thuật, thiếu khoá, cột kiểu void, trùng tên, `hash_exclude` chứa khoá. **Mảng phải `array_sort` trong build** |
| `quality_gate(spec, df, ctx)` | Chặn: `pk_null`, `pk_duplicate`, `dau_ra_rong` (nếu bật), `block_checks`, `unique_checks`. Cảnh báo: `warn_checks` + `ctx.warns`. Chặn → `QualityGateError` |
| `diff_counts(src, trg_fq, pk)` | 1 full outer join: insert / update (hash khác hoặc đang xoá mềm) / deactivate (có ở đích, không ở nguồn, chưa xoá) |
| `target_ddl`, `ensure_target(fq, schema, node)` | Tạo bảng từ schema build + 4 cột kỹ thuật; cột mới → ADD COLUMNS; lệch kiểu → `ConfigError`; bảng có cột build không trả → WARN |
| `sql_merge_target(...)` / `merge_target(fq, df, spec, tag)` | MERGE: khớp và (hash khác / hash NULL / đang xoá mềm) → UPDATE + `updated_at`, `deleted_at = NULL`; không khớp → INSERT (`created_at = updated_at = now`); **`WHEN NOT MATCHED BY SOURCE AND deleted_at IS NULL`** → `deleted_at = now`, `updated_at = now` + `soft_delete_set` |
| `_resolve_node(spec, rows, p_pl_name, p_trg_fq)` | Đối chiếu spec với config |
| `run_node(spec, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_name, p_trg_fq, p_history_limit)` | Xem bảng bước. Trả dict: `status`, `node`, `inserted`, `updated`, `deactivated`, `trg_version`, `src_versions`, `qg`, `error` |
| `finish_node(res)` | Cell cuối notebook node: FAILED / SKIPPED → raise (runMultiple ghi nhận lỗi); còn lại → JSON cho `notebookutils.notebook.exit` |

### §7 orchestrator

| Tên | Mô tả |
|---|---|
| `Plan` | `dag`, `states`, `pinned`, `edges` (mỗi cạnh: bẩn, lý do, versions, consumed, read), `dirty`, `forced`, `candidates` (topo), `pin_notes` |
| `plan_run(pl, force_nodes, non_data_ops, history_limit)` | **Chỉ đọc**: dựng DAG → `table_state` → đầu vào ngoài chưa có → `ConfigError` → ghim node của pl khác bằng `last_output_versions`, bảng khác lấy version hiện tại → `edge_status` (node cha chưa dựng → `PARENT_NOT_BUILT`) → ứng viên = (node bẩn ∪ node chưa có bảng ∪ force) + hậu duệ |
| `plan_summary(plan)` / `print_plan(plan)` | Tóm tắt: cạnh bẩn, ứng viên, ép chạy, ghim |
| `build_run_multiple_dag(plan, exec_id, run_id, node_mode, node_timeout_min, dag_timeout_min, max_parallel, history_limit)` | 1 activity / node ứng viên: `name` = `trg_tbl`, `path` = notebook, `timeoutPerCellInSeconds`, `retry` 0, `args` (`p_exec_id`, `p_run_id`, `p_pl_name`, `p_trg_fq`, `p_mode`, `p_force`, `p_history_limit`, `p_pinned_json` = version chốt của đầu vào ngoài **của chính node**), `dependencies` = node cha cũng là ứng viên; DAG `timeoutInSeconds`, `concurrency`. `[VERIFY]` tên trường |
| `collect_outcomes(exec_id, plan)` | Kết quả từng ứng viên từ `ctrl_log_table_run` (không phụ thuộc dạng trả về của runMultiple); không có dòng → `NOT_RUN` |
| `advance_edges(plan, outcomes, run_id, tag)` | 1 MERGE: node OK và có version → tiến cạnh tới `src_versions_json` của chính node (không lùi khi cùng table id); node lỗi → ghi trạng thái. Không kiểm khoá |
| `_validate_orch_params(p)` | Miền giá trị (bài học C2): `p_max_parallel` 1–8, `p_node_timeout_min` 1–240, `p_dag_timeout_min` 1–720, `p_lock_timeout_min` 5–1440, `p_history_limit` 10–100000; node ≤ DAG; **lock > DAG + 5** |
| `orchestrate(**params)` | Thân NB_00 (xem `NB_00_ORCHES_SLV_TO_GLD.md`) |

### §8 build helpers (dùng trong `build` của node)

| Hàm | Ví dụ |
|---|---|
| `clean_str(c)` | `"  "` / sentinel TOAST → NULL; `" a "` → `"a"` |
| `norm_text(c)` | `"  Phú   Quốc "` → `"phú quốc"` |
| `norm_admin(c)` | `"Phường Bến Nghé"` → `"bến nghé"`; `"TP. Hồ Chí Minh"` → `"hồ chí minh"` (`ADMIN_PREFIX_PATTERNS`, như 2.1) |
| `unaccent(c)` | `"Phở Đức"` → `"Pho Duc"` (bảng chuyển sinh từ Unicode NFD + đ/Đ, không UDF) |
| `slugify(c)` | `"Phở Hà Nội #1"` → `"pho-ha-noi-1"` |
| `uuid_md5(*cols)` | md5(concat) dạng 8-4-4-4-12 (= `HASH_MD5_UUID` extract) |
| `epoch_to_ts(c)` | Tự nhận giây / mili giây; 0 / NULL → NULL |
| `json_scalar(json_col, path_col)` | `get_json_object` với path là **cột** (lấy từ ref); mảng → phần tử đầu |
| `json_array_at(json_col, path_col)` | Mảng chuỗi tại path; giá trị đơn → mảng 1 phần tử |
| `json_sorted_array(c)` | Mảng → JSON bỏ NULL / trùng, sắp xếp (băm ổn định); rỗng → NULL |

## 5. Hợp đồng notebook node

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
SPEC = NodeSpec(trg_tbl="slv_poi", inputs={"src_map": "slv_poi_source_map", ...}, pk=("poi_id",), build=build,
                required_inputs=("src_map",), soft_delete_set={...})
# cell 4
RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_name, p_trg_fq, p_history_limit)
# cell 5
notebookutils.notebook.exit(finish_node(RES))
```

Chạy tay 1 node: để trống `p_exec_id` → RUN tự nhận khoá luồng (luồng đang chạy → chỉ DRY_RUN), ghim đầu vào ngoài như NB_00; dấu đã đọc của cạnh **không** được ghi (chỉ NB_00 ghi) → lần NB_00 sau sẽ tính lại node này (an toàn, có thể thừa).

## 6. Bảo đảm

| Tình huống | Cách lib xử lý |
|---|---|
| Chạy lại không có gì đổi | Mọi cạnh `UNCHANGED` / `MAINTENANCE_ONLY` → `NO_DATA`, 0 MERGE |
| Node lỗi | Hậu duệ `SKIPPED`; cạnh không tiến → lần sau tự chạy lại node + hậu duệ |
| Đầu vào bắt buộc rỗng (đang nạp lại) | QG chặn, bảng đích không bị xoá mềm |
| Mapping hỏng làm N5 ra 0 dòng | `block_empty_output` chặn → G1 / G3 giữ bản cũ, nhất quán |
| Extract đang chạy dở | Notebook không ghim version trước batch dở. Đầu vào ngoài lấy version hiện tại, trừ node của pl khác có `output_versions_json` |
| Bảng đầu vào tạo lại cùng nội dung | `TABLE_RECREATED` → tính lại → diff 0 → 0 MERGE |
| Run cũ mất khoá vẫn chạy | Không có `LockLostError`. Run sau có thể nhận khoá theo timeout của chính nó trong khi run trước vẫn MERGE và tiến cạnh |
| Tái lập | `src_versions_json` ghi version đã đọc của từng đầu vào → dựng lại bằng `VERSION AS OF` trong hạn VACUUM |

## 7. Kiểm thử và việc còn mở

- Test local 05/10: 121 / 121 (thêm 38 phản ví dụ của review 7 điểm, `test_review.py`). Logic 8 node chạy thật trên Spark local; Delta / version / history / runMultiple **giả lập** (Maven bị chặn) → phải xác nhận trên Fabric.
- `[VERIFY]` trên Fabric: tên trường runMultiple (`timeoutPerCellInSeconds`, `timeoutInSeconds`, `concurrency`, `retry`, `dependencies`); `WHEN NOT MATCHED BY SOURCE` trên Delta 3.2; `operationMetrics` MERGE; tên operation của auto compaction.
- Thời gian PLAN đo được ~93 s (đọc history + DESCRIBE DETAIL ~24 bảng, tuần tự) — chiếm phần lớn lần chạy `NO_DATA`.
