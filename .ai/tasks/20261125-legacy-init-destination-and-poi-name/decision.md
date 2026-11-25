# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | `poi_name` theo lang trên `gld_srv_poi_multi_lang` | Cột mới `poi_name` là STRING, nullable. Grain vẫn `(poi_id, lang)`. Init lấy `poi_name` của đúng lang từ nguồn gold cũ mà notebook đang dùng cho tên. Không lấy tên lang `vi` cho mọi dòng. D-06 của `20261119-legacy-gold-poi-init` vẫn áp cho `poi_name` trên `gld_srv_poi_info`. | request.md Acceptance criteria | 2026-11-25 |
| D-02 | Luồng chính ghi đè `poi_name` init bằng null | `NB_GLD_SRV_POI_MULTI_LANG` ghi `poi_name = null` trên cả P1 và P2. Không đọc một cột chưa có của `slv_enr_poi_info_multi_lang`. MERGE của luồng chính được phép ghi đè `poi_name` init bằng null khi dòng đó thành dòng pipeline. Init không sửa dòng pipeline đang sở hữu. | request.md Acceptance criteria | 2026-11-25 |
| D-03 | Workspace đích của notebook init | Notebook init nhận workspace đích bằng tham số. Không gắn cứng `sgr_visitvn_dev`. Không đoán tên workspace Prod. Nguồn gold cũ giữ workspace đang có trong notebook. | request.md Acceptance criteria | 2026-11-25 |
| D-04 | Giữ `destination_id` là STRING | Giữ `gld_srv_poi_info.destination_id` là STRING. Không đổi sang ARRAY. Probe Fabric DEV: cột `string` nullable; dòng `load_origin` null có 19797 `json_array_string`, 2 `json_array_empty`, 110 null, `bad=0`, verdict `keep_string`. | evidence/results/destination_id_non_legacy_shape.txt | 2026-11-25 |
| D-05 | Chuỗi JSON `destination_id` của init | Kiểm tra mọi dòng `poi_master` map `OK` về cùng `poi_id` mới, mọi lang, không chỉ `vi`. Đồng ý thì ghi `destination_id` kể cả khi không có dòng `vi`. Python chỉ phân loại. Spark ghi `to_json(from_json(destination_ids, 'array<string>'))`: compact, giữ thứ tự và phần tử trùng, không đổi nội dung từng phần tử. So xung đột trên chuỗi này: khác khoảng trắng không tính, khác thứ tự thì tính. `[]` cũ thành `"[]"`. NULL cũ giữ NULL. Nhận `NULL`, `EMPTY`, `STRINGS`. `NOT_JSON` (kể cả blank), `NOT_ARRAY`, `NULL_ELEMENT`, `NON_STRING_ELEMENT` thì dừng. Phần tử null thì dừng. `destination_name` giữ nguyên: dòng `vi`, chuỗi thô. | architecture.md §A Q1–Q4, Q10 | 2026-11-25 |
| D-06 | `poi_name` init và vị trí cột | Xung đột `poi_name` trong một `(poi_id, lang)` thì ghi NULL cho khóa đó, vẫn ghi payload, đếm `name_conflict_n`. Không chọn một tên. Độ phủ multi-lang không giảm. Tên lấy từ dòng legacy sau dòng display: `poi_master.poi_id = display.poi_id = mp.legacy_poi_id`, lang là `mp.lang`. `poi_name` đứng ngay sau `lang` trong `TABLE_SPECS`, `OUT_COLS`, `ALTER ... AFTER lang`, và `CREATE TABLE` PostgreSQL. | architecture.md §A Q5–Q7 | 2026-11-25 |
| D-07 | Workspace đích và DDL | `p_target_ws` phải bằng workspace đang chạy. `legacyidpy` và `lgpnamepy` tự lấy workspace đang chạy. `DICT_FQ` và mọi write guard dùng cùng `TARGET_WS`. `OLD` giữ nguyên. | architecture.md §A Q9, Main brief | 2026-11-25 |
| D-08 | Mở rộng scope | Người dùng chấp nhận cả ba file: `SrvPoiMultiLang.java` (field `poiName`, `@Column(name = "poi_name")`, không đổi DTO), `tests/test_legacy_gold_poi_init_contract.py`, `docs/context/mapping_legacy_gold_to_gld_srv.md`. | Người dùng, 2026-11-25; architecture.md §B | 2026-11-25 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Các test khóa 8 cell cuối `NB_CREATE_DDL` được dịch thêm `lgpnamemd` và `lgpnamepy`. Nếu không dịch, `pytest -q` gãy dù cell cũ không đổi.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | Fabric DEV: `spark.sql.jsonGenerator.ignoreNullFields=true`. `old_json` bằng `new_json`. `old_hash` bằng `new_hash`. Verdict `null_poi_name_hash_unchanged`. `poi_name` null không đổi `to_json` và không đổi hash. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-25: D-01, D-02, D-03 trong yêu cầu task. D-04 để mở cho đến khi có kết quả probe shape.
- Hai UUID trong mẫu JSON chỉ minh họa dạng chuỗi. Không dùng làm seed.
- 2026-11-25: chấp nhận cả ba file ở D-08.

## Lịch sử quyết định

- 2026-11-25: mở D-01, D-02, D-03 theo yêu cầu. D-04 chờ probe `destination_id_non_legacy_shape`. Chưa sửa notebook hay DDL.
- 2026-11-25: lần chạy probe đầu trả kiểu cột `string` và số dòng `LEGACY_INIT` 25921, `load_origin` null 19909. Phần đếm shape lỗi `schema_of_json` không nhận cột. D-04 giữ nguyên.
- 2026-11-25: probe `destination_id_non_legacy_shape` verdict `keep_string`. D-04 chốt STRING. `gates.evidence` = pass.
- 2026-11-25: `model-design.md` rồi Architect `RESULT: PASS`. `gates.architecture` = pass. Chưa sửa code. Đang chờ chấp nhận thêm ba file ngoài scope trước edit list.
- 2026-11-25: người dùng chấp nhận cả ba. Ghi D-05, D-06, D-07, D-08 trước khi sửa code.
- 2026-11-25: lệch nhỏ trước khi sửa test: các assert đuôi cell `NB_CREATE_DDL` nhận thêm hai cell `lgpname`.
- 2026-11-25: probe `poi_name_null_hash` verdict `null_poi_name_hash_unchanged`. GATE-001 `fixed`. Không sửa code.
- 2026-11-25: người dùng chuyển `ready_to_merge` sau runtime Dev. Init Prod chưa chạy vì chưa có tên workspace.
