**CHỈ DÙNG CHO FABRIC DEV.** Nếu workspace, lakehouse hoặc capacity không phải môi trường DEV, hoặc chưa xác nhận được là DEV, thì dừng ngay ở `user_decision`. Không chạy bất kỳ bước nào bên dưới.

# Runtime runbook — 20261030-wipe-data-reseed-ctrl

Trạng thái tài liệu: runbook do author viết từ file trong repo. Chưa lệnh Fabric nào được chạy. Mọi kết quả phải do người dùng ghi ở mục cuối.

## Phạm vi và môi trường

- Môi trường: chỉ Fabric DEV. Workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`. Môi trường khác thì dừng ở `user_decision`.
- Công cụ: một notebook nháp mới trong workspace DEV, không lưu vào repo. Ngôn ngữ PySpark và Spark SQL. Mọi tên bảng viết đủ dạng `<lakehouse>.<schema>.<bảng>`. Default lakehouse theo `NB_CREATE_DDL` cell 0 là `lh_vv_bronze`, nhưng runbook không dựa vào default.
- Việc cần làm:
  1. Xóa dòng bằng `DELETE FROM` (không có `WHERE`) trong `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_gold`, ở schema `dbo` và `enr`, cùng bảy bảng `lh_vv_ctrl.dbo` ở §1 `CTRL_TABLES_CONTEXT.md`.
  2. Seed lại đúng ba bảng ctrl: `ctrl_mng_pipeline_config`, `ctrl_mng_watermark`, `ctrl_cfg_schema_registry`.
- Không làm: `DROP TABLE`, đổi schema, `ALTER`, `VACUUM`, `OPTIMIZE`, `TRUNCATE`, `overwrite` hay `replaceWhere`. Không chạy nguyên notebook `NB_SETUP_INITIAL_DDL`, cũng không chạy `NB_CREATE_DDL`. Không seed `ref_dictionary_place_type` hay `ref_dictionary_amenities`. Không seed dòng `wm_e__…` hay `wm_flow__…`. Hướng dẫn `DROP` ở §4 và hướng dẫn `overwrite` + `replaceWhere` ở §5 (thuộc `NB_CREATE_DDL`) không áp dụng cho task này.
- Bốn bảng log/state chỉ xóa, không seed: `lh_vv_ctrl.dbo.ctrl_log_run`, `lh_vv_ctrl.dbo.ctrl_log_table_run`, `lh_vv_ctrl.dbo.ctrl_cdc_state`, `lh_vv_ctrl.dbo.ctrl_cdc_reject`.
- Giữ nguyên dòng (không xóa, không seed) hai bảng `ref_` có trong `TABLE_SPECS`: `lh_vv_silver.dbo.ref_dictionary_place_type` và `lh_vv_silver.dbo.ref_dictionary_amenities`.
- Tham số notebook: cell parameter của `NB_SETUP_INITIAL_DDL` (`id:init_param`) là `p_apply = "false"`. Runbook không chạy notebook này nên không dùng tham số đó. Không có pipeline JSON nào được nêu cho task.
- `architecture.md` của task chưa có nội dung, kể cả mục `Rollout, rollback, and forward recovery`. Hợp đồng của task là author input.

### Allowlist từ repo (56 bảng)

Nguồn là `NB_SETUP_INITIAL_DDL`: `TABLE_SPECS` (`id:init_tables`, 22 fq); src/trg trong `PIPELINE_CONFIG_ROWS` và `WATERMARK_ROWS` (`id:init_seed_ctrl`); `target_table` trong `TABLE_CONFIGS` (`id:init_cfg_partner`, 23 bảng) và `TABLE_CONFIGS_3P` (`id:init_cfg_3p`, 9 bảng). Khi lệch nhau, cell notebook thắng snapshot 04/10 và ví dụ ở §3 và §5. Ví dụ: `slv_3p_poi_policy` có ở §3 và §5 nhưng không có trong `TABLE_CONFIGS_3P` hay `PIPELINE_CONFIG_ROWS`, nên nó nằm ngoài allowlist.

| Nhóm | Bảng | Số bảng | Xử lý |
|---|---|---|---|
| ctrl seed | `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`, `lh_vv_ctrl.dbo.ctrl_mng_watermark`, `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` | 3 | Xóa, rồi seed |
| ctrl log/state | `lh_vv_ctrl.dbo.ctrl_log_run`, `lh_vv_ctrl.dbo.ctrl_log_table_run`, `lh_vv_ctrl.dbo.ctrl_cdc_state`, `lh_vv_ctrl.dbo.ctrl_cdc_reject` | 4 | Chỉ xóa |
| ref | `lh_vv_silver.dbo.ref_dictionary_place_type`, `lh_vv_silver.dbo.ref_dictionary_amenities` | 2 | Giữ |
| bronze | `lh_vv_bronze.dbo.partner_raw_data`, `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` | 2 | Xóa |
| silver partner | `slv_pn_products`, `slv_pn_product_translations`, `slv_pn_product_attributes`, `slv_pn_product_attribute_translations`, `slv_pn_product_attribute_values`, `slv_pn_product_attribute_value_translations`, `slv_pn_product_variants`, `slv_pn_product_variant_translations`, `slv_pn_product_business_service_relation`, `slv_pn_product_posts`, `slv_pn_product_post_translations`, `slv_pn_partners`, `slv_pn_business_services`, `slv_pn_business_locations`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`, `slv_pn_business_service_i18ns`, `slv_pn_business_service_poi_link`, `slv_pn_orders`, `slv_pn_order_refs`, `slv_pn_order_item_tickets`, `slv_pn_order_item_hotels`, `slv_pn_order_item_flights` (đều ở `lh_vv_silver.dbo`) | 23 | Xóa |
| silver 3P | `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_rating`, `slv_3p_poi_amenity`, `slv_3p_poi_review`, `slv_3p_poi_media` (`lh_vv_silver.dbo`) | 9 | Xóa |
| silver node | `slv_poi_entity_non_enrich`, `slv_poi_amenity`, `slv_poi_media_info`, `slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination`, `slv_enr_poi_review_multi_lang` (`lh_vv_silver.dbo`) | 6 | Xóa |
| gold enr | `lh_vv_gold.enr.gld_enr_poi_info`, `lh_vv_gold.enr.gld_enr_poi_review` | 2 | Xóa |
| gold serving | `gld_srv_poi_multi_lang`, `gld_srv_poi_info`, `gld_srv_poi_media_gallery`, `gld_srv_poi_amenity`, `gld_srv_poi_review` (`lh_vv_gold.dbo`) | 5 | Xóa |

Tổng: 56 bảng trong allowlist. 54 bảng bị xóa dòng (gồm 7 bảng ctrl). 2 bảng ref được giữ.

Các schema được probe: `lh_vv_ctrl.dbo`, `lh_vv_bronze.dbo`, `lh_vv_bronze.enr`, `lh_vv_silver.dbo`, `lh_vv_silver.enr`, `lh_vv_gold.dbo`, `lh_vv_gold.enr`. Schema khác, ví dụ vị trí cũ `lh_vv_bronze.ctrl` nêu ở §4, không thuộc phạm vi và không bị đụng tới.

## Điều kiện tiên quyết

1. Người chạy xác nhận đang ở Fabric DEV, workspace `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`. Chưa xác nhận được thì dừng ở `user_decision`.
2. Không có pipeline, trigger hay notebook nào đang chạy hoặc sắp chạy trên các bảng trong phạm vi. Gồm `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, `PL_VV_TRANS_SLV_TO_ENR_15M`, `PL_VV_TRANS_SLV_TO_GLD_30M`, `PL_VV_TRANS_SLV_TO_GLD_1H`, các notebook extract và các notebook node.
   - MISSING: các file đã đọc không có lệnh tạm dừng pipeline. Runbook không tự đặt ra lệnh này.
   - Cách đảm bảo: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách người dùng tạm dừng hoặc xác nhận không có schedule/trigger trong cửa sổ chạy>`.
   - Kiểm tra chỉ đọc ở bước B3 phải ra 0 run `RUNNING` và 0 khóa đang giữ.
3. Có người xác nhận nguồn ghi vào `lh_vv_bronze.dbo.partner_raw_data` và `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` có đang chạy hay không: `<CẦN NGƯỜI DÙNG CUNG CẤP: trạng thái ingest bronze trong cửa sổ chạy>`. Nếu ingest vẫn chạy, bronze sẽ có dòng lại sau khi xóa, và bước kiểm tra "bảng rỗng" của bronze phải ghi là lệch.
4. Có quyền đọc và ghi trên `lh_vv_ctrl`, `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_gold` trong workspace DEV.
5. Có bản repo hiện hành để copy nguyên văn source của bốn cell `id:init_cfg_partner`, `id:init_cfg_3p`, `id:init_registry_pure`, `id:init_seed_ctrl` trong `notebooks/NB_SETUP_INITIAL_DDL.ipynb`. Không copy `id:init_seed_place_type`, `id:init_seed_amenity`, `id:init_ddl`, `id:init_seed_write` (nguyên cell) hay `id:init_plan` (nguyên cell).
6. Người dùng chấp nhận rằng xóa dòng bronze làm mất dữ liệu raw. Cách lấy lại duy nhất trong phạm vi runbook là Delta `RESTORE`, và chỉ làm được khi file cũ chưa bị VACUUM (xem mục Rollback). Nguồn nạp lại raw: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách nạp lại raw partner và 3P sau khi xóa, nếu cần>`.

## Baseline trước khi chạy

Mọi cell ở mục này chỉ đọc. Chạy theo thứ tự trong cùng một session notebook nháp.

**B1. Xác nhận môi trường (chỉ đọc)**

```python
ctx = notebookutils.runtime.context
print({k: ctx.get(k) for k in ("currentWorkspaceName", "currentWorkspaceId", "currentNotebookName")})
EXPECTED_DEV_WORKSPACE = "<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>"
ENV_IS_DEV = ctx.get("currentWorkspaceName") == EXPECTED_DEV_WORKSPACE
print("ENV_IS_DEV =", ENV_IS_DEV)
```

Nếu `ENV_IS_DEV` khác `True`, hoặc key trên không có trong context và người dùng không xác nhận được bằng giao diện Fabric, thì dừng ở `user_decision`.

**B2. Probe danh sách bảng, số dòng, version và schema (chỉ đọc, chỉ số tổng hợp, không lấy dòng mẫu)**

```python
import hashlib

_C, _B, _S, _E, _G = "lh_vv_ctrl.dbo", "lh_vv_bronze.dbo", "lh_vv_silver.dbo", "lh_vv_gold.enr", "lh_vv_gold.dbo"
CTRL_SEED = [f"{_C}.ctrl_mng_pipeline_config", f"{_C}.ctrl_mng_watermark", f"{_C}.ctrl_cfg_schema_registry"]
CTRL_LOG = [f"{_C}.ctrl_log_run", f"{_C}.ctrl_log_table_run", f"{_C}.ctrl_cdc_state", f"{_C}.ctrl_cdc_reject"]
KEEP_REF = [f"{_S}.ref_dictionary_place_type", f"{_S}.ref_dictionary_amenities"]
BRONZE = [f"{_B}.partner_raw_data", f"{_B}.brz_3rd_crawler_poi_stream"]
SLV_PN = [f"{_S}.{t}" for t in (
    "slv_pn_products", "slv_pn_product_translations", "slv_pn_product_attributes",
    "slv_pn_product_attribute_translations", "slv_pn_product_attribute_values",
    "slv_pn_product_attribute_value_translations", "slv_pn_product_variants",
    "slv_pn_product_variant_translations", "slv_pn_product_business_service_relation",
    "slv_pn_product_posts", "slv_pn_product_post_translations", "slv_pn_partners",
    "slv_pn_business_services", "slv_pn_business_locations", "slv_pn_hotel_room_types",
    "slv_pn_hotel_rate_plans", "slv_pn_business_service_i18ns", "slv_pn_business_service_poi_link",
    "slv_pn_orders", "slv_pn_order_refs", "slv_pn_order_item_tickets",
    "slv_pn_order_item_hotels", "slv_pn_order_item_flights")]
SLV_3P = [f"{_S}.{t}" for t in (
    "slv_3p_poi", "slv_3p_poi_address", "slv_3p_poi_contact", "slv_3p_poi_price",
    "slv_3p_poi_opening_hours", "slv_3p_poi_rating", "slv_3p_poi_amenity",
    "slv_3p_poi_review", "slv_3p_poi_media")]
SLV_NODE = [f"{_S}.{t}" for t in (
    "slv_poi_entity_non_enrich", "slv_poi_amenity", "slv_poi_media_info",
    "slv_enr_poi_info_multi_lang", "slv_enr_poi_destination", "slv_enr_poi_review_multi_lang")]
GLD_ENR = [f"{_E}.gld_enr_poi_info", f"{_E}.gld_enr_poi_review"]
GLD_SRV = [f"{_G}.{t}" for t in (
    "gld_srv_poi_multi_lang", "gld_srv_poi_info", "gld_srv_poi_media_gallery",
    "gld_srv_poi_amenity", "gld_srv_poi_review")]
ALLOW = CTRL_SEED + CTRL_LOG + KEEP_REF + BRONZE + SLV_PN + SLV_3P + SLV_NODE + GLD_ENR + GLD_SRV
assert len(ALLOW) == len(set(ALLOW)) == 56
WIPE = [fq for fq in ALLOW if fq not in KEEP_REF]
assert len(WIPE) == 54

SCOPES = ["lh_vv_ctrl.dbo", "lh_vv_bronze.dbo", "lh_vv_bronze.enr", "lh_vv_silver.dbo",
          "lh_vv_silver.enr", "lh_vv_gold.dbo", "lh_vv_gold.enr"]


def list_live():
    live, errs = set(), {}
    for db in SCOPES:
        try:
            rows = spark.sql(f"SHOW TABLES IN {db}").collect()
        except Exception as exc:
            errs[db] = str(exc)[:300]
            continue
        live |= {f"{db}.{r['tableName']}".lower() for r in rows if not r["isTemporary"]}
    return live, errs


live, scope_errors = list_live()
allow_l = {fq.lower() for fq in ALLOW}
outside = sorted(live - allow_l)
outside_ref = [fq for fq in outside if fq.rsplit(".", 1)[1].startswith("ref_")]
missing = sorted(allow_l - live)

BASELINE = {}
for fq in sorted(live & allow_l):
    n = int(spark.sql(f"SELECT count(*) AS n FROM {fq}").first()["n"])
    ver = int(spark.sql(f"DESCRIBE HISTORY {fq} LIMIT 1").first()["version"])
    sch = hashlib.md5(spark.table(fq).schema.json().encode()).hexdigest()
    BASELINE[fq] = {"rows": n, "version": ver, "schema_md5": sch}

print("scope_errors =", scope_errors)
print("outside_allowlist =", outside)
print("outside_ref =", outside_ref)
print("missing_in_env =", missing)
base_df = spark.createDataFrame(
    [(fq, v["rows"], v["version"], v["schema_md5"]) for fq, v in BASELINE.items()],
    "fq STRING, rows BIGINT, version BIGINT, schema_md5 STRING")
base_df.filter("fq NOT LIKE 'lh_vv_silver.%'").orderBy("fq").show(50, truncate=False)
base_df.filter("fq LIKE 'lh_vv_silver.%'").orderBy("fq").show(50, truncate=False)
```

Kết quả hiển thị có tối đa 50 dòng mỗi bảng in ra (nhóm silver có 40 bảng, nhóm còn lại có 16 bảng). Chỉ in tên bảng và số tổng hợp, không in dữ liệu dòng.

**Cổng dừng sau B2 (không xóa gì nếu gặp bất kỳ điều kiện nào dưới đây):**

- `outside` khác rỗng. Có bảng live trong các schema phạm vi mà repo không có, kể cả mọi bảng `ref_*` ngoài hai bảng ref đã nêu (`outside_ref`). Dừng ở `user_decision` và không xóa gì.
- `scope_errors` có lỗi không phải kiểu "schema/namespace không tồn tại", ví dụ lỗi quyền hoặc lỗi kết nối. Dừng ở `user_decision`. Lỗi "không tồn tại" của `lh_vv_bronze.enr` hoặc `lh_vv_silver.enr` thì ghi lại rồi đi tiếp.
- `missing` có bất kỳ bảng nào trong `CTRL_SEED` hoặc `CTRL_LOG`. Runbook không được tạo bảng, nên dừng ở `user_decision`.
- `missing` có bảng khác: ghi lại. Bước xóa sẽ bỏ qua bảng đó (`SKIP_NOT_LIVE`).

**B3. Kiểm tra không có run hay khóa đang giữ (chỉ đọc)**

```sql
SELECT count(*) AS running_runs FROM lh_vv_ctrl.dbo.ctrl_log_run WHERE status = 'RUNNING';
SELECT count(*) AS held_locks FROM lh_vv_ctrl.dbo.ctrl_mng_watermark WHERE lock_exec_id IS NOT NULL;
```

Cả hai phải bằng 0. Nếu khác 0, dừng ở `user_decision`. Không tự nhả khóa.

**B4. Ghi baseline:** copy toàn bộ output của B1–B3 vào mục "Kết quả người dùng ghi nhận". Biến `BASELINE` phải còn trong session cho các bước sau. Nếu session bị restart, chạy lại B2 trước khi xóa. Khi đó baseline cho rollback là bản đã chép tay.

## Các bước thực hiện

**S1. Xóa dòng (bước ghi đầu tiên).** Chỉ chạy khi cổng B2 và B3 đạt và người dùng đặt `CONFIRM_WIPE_DEV = True`. Cell này probe lại danh sách bảng ngay trước khi xóa.

Thứ tự xóa:
1. `ctrl_mng_pipeline_config` và `ctrl_mng_watermark` trước, để pre-check FL_00 và các notebook không còn thấy việc.
2. Gold, silver (không gồm ref), bronze.
3. Bốn bảng log/state.
4. `ctrl_cfg_schema_registry`.

```python
CONFIRM_WIPE_DEV = False  # người dùng tự đổi thành True sau khi đã ghi baseline
assert ENV_IS_DEV and CONFIRM_WIPE_DEV

live_now, errs_now = list_live()
outside_now = sorted(live_now - allow_l)
if outside_now:
    raise RuntimeError(f"STOP user_decision: bảng ngoài allowlist {outside_now}")

DELETE_ORDER = (
    [f"{_C}.ctrl_mng_pipeline_config", f"{_C}.ctrl_mng_watermark"]
    + GLD_SRV + GLD_ENR + SLV_NODE + SLV_3P + SLV_PN + BRONZE
    + CTRL_LOG + [f"{_C}.ctrl_cfg_schema_registry"]
)
assert sorted(DELETE_ORDER) == sorted(WIPE) and not set(DELETE_ORDER) & set(KEEP_REF)

DELETE_RESULTS = {}
for fq in DELETE_ORDER:
    if fq.lower() not in live_now:
        DELETE_RESULTS[fq] = "SKIP_NOT_LIVE"
        continue
    spark.sql(f"DELETE FROM {fq}")
    DELETE_RESULTS[fq] = int(spark.sql(f"SELECT count(*) AS n FROM {fq}").first()["n"])
for fq, r in DELETE_RESULTS.items():
    print(fq, r)
```

Kết quả mong đợi: mọi bảng có giá trị `0` hoặc `SKIP_NOT_LIVE`. Nếu cell lỗi giữa chừng, xem "Rollback và forward recovery".

**S2. Seed ba bảng ctrl: MISSING cell riêng.**

MISSING: `NB_SETUP_INITIAL_DDL` không có cell nào chỉ seed ba bảng ctrl. Cell `id:init_seed_write` gọi `_merge_pipeline_config`, `_merge_watermark`, `_merge_registry`, và cả `_merge_place_type` lẫn `_merge_amenities`. Cell `id:init_plan` tạo cả view `_v_setup_place_type` và `_v_setup_amenities`. Vì vậy không chạy hai cell đó. Thay vào đó dùng ba cell dưới đây. Ba cell này chỉ lấy row literal, phần flatten registry, ba view `_v_setup_pipeline_config`, `_v_setup_watermark`, `_v_setup_registry`, và ba câu MERGE insert-only nguyên văn.

**S2a. Nạp định nghĩa (không ghi bảng).** Tạo một cell và dán nguyên văn source của bốn cell sau, đúng thứ tự, không sửa:

1. `id:init_cfg_partner`: `TABLE_CONFIGS`.
2. `id:init_cfg_3p`: `TABLE_CONFIGS_3P` và helper `UUID`, `POI_ID`, `_str`, `_bool`, `_off`.
3. `id:init_registry_pure`: `resolve_type`, `flatten_table_configs`, `validate_rows`, `REGISTRY_SCHEMA`.
4. `id:init_seed_ctrl`: `PIPELINE_CONFIG_ROWS`, `WATERMARK_ROWS`.

Không dán `id:init_run` (`%run NB_LIB_TRANSFORM_SLV_GLD`). Nếu cell báo `NameError` vì thiếu hàm của lib, dừng ở `user_decision`: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách nạp hàm còn thiếu mà không chạy NB_SETUP_INITIAL_DDL hay NB_CREATE_DDL>`.

**S2b. Tạo ba view seed (chỉ tạo temp view).** Code lấy từ `id:init_plan`, chỉ giữ phần của ba bảng ctrl. `ConfigError` của lib được thay bằng `RuntimeError`.

```python
errors = []
partner_rows = flatten_table_configs(TABLE_CONFIGS, "lh_vv_bronze.dbo", "partner_raw_data")
third_rows = flatten_table_configs(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream")
try:
    validate_rows(TABLE_CONFIGS, partner_rows)
    validate_rows(TABLE_CONFIGS_3P, third_rows)
except ValueError as exc:
    errors.append(str(exc))
registry_rows = partner_rows + third_rows
seen = set()
for row in registry_rows:
    key = (row["src_schema"], row["src_tbl"], row["trg_schema"], row["trg_tbl"], row["trg_column"])
    if key in seen:
        errors.append(f"registry trùng {key}")
    seen.add(key)
pc_keys = set()
for pl, src_schema, src_tbl, trg_schema, trg_tbl, *_rest in PIPELINE_CONFIG_ROWS:
    key = (pl, src_schema, src_tbl, trg_schema, trg_tbl)
    if key in pc_keys:
        errors.append(f"pipeline_config trùng {key}")
    pc_keys.add(key)
wm_ids = [row[0] for row in WATERMARK_ROWS]
if len(wm_ids) != len(set(wm_ids)):
    errors.append(f"watermark_id trùng {wm_ids}")
if errors:
    raise RuntimeError("\n".join(errors))

pc_df = spark.createDataFrame(
    [(i, *row) for i, row in enumerate(PIPELINE_CONFIG_ROWS, start=1)],
    "seq INT, pl_name STRING, src_schema STRING, src_tbl STRING, trg_schema STRING, trg_tbl STRING, "
    "is_active INT, priority INT, load_mode STRING, align_path STRING, dedup_order STRING, nb_name STRING",
)
pc_df.createOrReplaceTempView("_v_setup_pipeline_config")
wm_df = spark.createDataFrame(
    WATERMARK_ROWS,
    "watermark_id STRING, src_schema STRING, src_tbl STRING, watermark_column STRING, "
    "status STRING, flow_name STRING, watermark_sequence LONG",
)
wm_df.createOrReplaceTempView("_v_setup_watermark")
spark.createDataFrame(registry_rows, schema=REGISTRY_SCHEMA).createOrReplaceTempView("_v_setup_registry")
EXPECTED = {"pipeline_config": len(PIPELINE_CONFIG_ROWS), "watermark": len(WATERMARK_ROWS),
            "registry": len(registry_rows)}
print(EXPECTED)
```

Giá trị mong đợi lấy từ file:
- `pipeline_config = 69`. Đây là số dòng tuple trong `PIPELINE_CONFIG_ROWS`, chia theo pipeline: `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` 32, `PL_VV_TRANS_SLV_TO_ENR_15M` 21, `PL_VV_TRANS_SLV_TO_GLD_30M` 15, `PL_VV_TRANS_SLV_TO_GLD_1H` 1.
- `watermark = 2`, gồm `wm_transform_partner_raw_data` và `wm_transform_brz_3rd_crawler_poi_stream`.
- `registry`: số dòng flatten, chỉ biết khi chạy. Ghi lại số `EXPECTED["registry"]`. Không dùng số của snapshot §5.

Nếu `EXPECTED` khác 69 hoặc 2, dừng ở `user_decision`, vì repo đã đổi so với runbook.

**S2c. MERGE insert-only cho ba bảng.** Ba hàm MERGE copy nguyên văn từ `id:init_seed_write`. Không có `WHEN MATCHED`. Không có `with_retry` của lib.

```python
PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM_FQ = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
REG_FQ = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry"


def _merge_pipeline_config():
    base = int(spark.sql(f"SELECT COALESCE(MAX(id), 0) AS m FROM {PC_FQ}").first()["m"])
    spark.sql(f"""
        MERGE INTO {PC_FQ} AS t
        USING _v_setup_pipeline_config AS s
        ON t.pl_name = s.pl_name AND t.src_schema = s.src_schema AND t.src_tbl = s.src_tbl
           AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl
        WHEN NOT MATCHED THEN INSERT
            (id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority,
             load_mode, align_path, dedup_order, nb_name)
        VALUES ({base} + s.seq, s.pl_name, s.src_schema, s.src_tbl, s.trg_schema, s.trg_tbl, s.is_active,
                s.priority, s.load_mode, s.align_path, s.dedup_order, s.nb_name)
    """)


def _merge_watermark():
    spark.sql(f"""
        MERGE INTO {WM_FQ} AS t
        USING _v_setup_watermark AS s
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
    """)


def _merge_registry():
    spark.sql(f"""
        MERGE INTO {REG_FQ} AS t
        USING _v_setup_registry AS s
        ON t.src_schema = s.src_schema AND t.src_tbl = s.src_tbl
           AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl AND t.trg_column = s.trg_column
        WHEN NOT MATCHED THEN INSERT (
            src_schema, src_tbl, src_object_schema, src_object, trg_schema, trg_tbl, trg_column,
            json_path, data_type, convert_arg, convert_rule, is_key, key_order, is_toast,
            column_order, is_active, description
        ) VALUES (
            s.src_schema, s.src_tbl, s.src_object_schema, s.src_object, s.trg_schema, s.trg_tbl, s.trg_column,
            s.json_path, s.data_type, s.convert_arg, s.convert_rule, s.is_key, s.key_order, s.is_toast,
            s.column_order, s.is_active, s.description
        )
    """)


SEED3 = [
    ("pipeline_config", "_v_setup_pipeline_config", PC_FQ,
     "t.pl_name = s.pl_name AND t.src_schema = s.src_schema AND t.src_tbl = s.src_tbl "
     "AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl", _merge_pipeline_config),
    ("watermark", "_v_setup_watermark", WM_FQ, "t.watermark_id = s.watermark_id", _merge_watermark),
    ("registry", "_v_setup_registry", REG_FQ,
     "t.src_schema = s.src_schema AND t.src_tbl = s.src_tbl AND t.trg_schema = s.trg_schema "
     "AND t.trg_tbl = s.trg_tbl AND t.trg_column = s.trg_column", _merge_registry),
]


def _n(sql):
    return int(spark.sql(sql).first()["n"])


SEED_RESULTS = {}
for name, view, table, on_sql, merge_fn in SEED3:
    missing_before = _n(f"SELECT count(*) AS n FROM {view} s LEFT ANTI JOIN {table} t ON {on_sql}")
    rows_before = _n(f"SELECT count(*) AS n FROM {table}")
    merge_fn()
    missing_after = _n(f"SELECT count(*) AS n FROM {view} s LEFT ANTI JOIN {table} t ON {on_sql}")
    rows_after = _n(f"SELECT count(*) AS n FROM {table}")
    SEED_RESULTS[name] = {"defined": EXPECTED[name], "inserted": rows_after - rows_before,
                          "missing_after": missing_after, "rows_after": rows_after}
    print(name, SEED_RESULTS[name])
    if missing_after:
        raise RuntimeError(f"{name}: còn thiếu {missing_after} khóa sau MERGE")
```

Kết quả mong đợi ở lần chạy đầu, khi ba bảng vừa được xóa:
- `pipeline_config`: inserted = 69, rows_after = 69. `id` chạy từ 1 đến 69 vì `MAX(id)` sau khi xóa là 0.
- `watermark`: inserted = 2, rows_after = 2.
- `registry`: inserted = `EXPECTED["registry"]` = rows_after.
- Mọi `missing_after` = 0.

## Kiểm tra kết quả

Mọi query ở mục này chỉ đọc.

**K1. `ctrl_mng_pipeline_config`**

```sql
SELECT count(*) AS n,
       count(DISTINCT pl_name, src_schema, src_tbl, trg_schema, trg_tbl) AS n_keys,
       min(id) AS min_id, max(id) AS max_id, sum(is_active) AS n_active
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config;

SELECT pl_name, load_mode, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
GROUP BY pl_name, load_mode ORDER BY pl_name, load_mode;
```

Mong đợi:
- `n = 69`, `n_keys = 69`, `min_id = 1`, `max_id = 69`.
- `n_active = 68`. Chỉ cạnh `slv_3p_poi_opening_hours` → `gld_enr_poi_info` có `is_active = 0`.
- Theo pipeline và load_mode:
  - FL_00: `CDC` 23, `DOC` 7, `DOC_ARRAY` 2.
  - `PL_VV_TRANS_SLV_TO_ENR_15M`: `APPEND` 11, `RECOMPUTE` 10.
  - `PL_VV_TRANS_SLV_TO_GLD_30M`: `RECOMPUTE` 15.
  - `PL_VV_TRANS_SLV_TO_GLD_1H`: `RECOMPUTE` 1.

**K2. `ctrl_mng_watermark`**

```sql
SELECT watermark_id, src_schema, src_tbl, trg_tbl, watermark_column, status, flow_name,
       watermark_sequence, last_src_version, lock_exec_id
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark ORDER BY watermark_id LIMIT 50;
```

Mong đợi đúng 2 dòng:
- `wm_transform_brz_3rd_crawler_poi_stream`: `lh_vv_bronze.dbo`, `brz_3rd_crawler_poi_stream`, `crawled_at`, `INITIALIZED`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, `-1`.
- `wm_transform_partner_raw_data`: `lh_vv_bronze.dbo`, `partner_raw_data`, `EventProcessedUtcTime`, `INITIALIZED`, `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `-1`.
- Cả hai có `trg_tbl`, `last_src_version` và `lock_exec_id` là NULL.
- Không có dòng `wm_e__…` hay `wm_flow__…`.

**K3. `ctrl_cfg_schema_registry` khớp đúng view seed**

```sql
SELECT count(*) AS n, count(DISTINCT src_schema, src_tbl, trg_schema, trg_tbl, trg_column) AS n_keys
FROM lh_vv_ctrl.dbo.ctrl_cfg_schema_registry;

SELECT count(*) AS n FROM (
  SELECT src_schema, src_tbl, src_object_schema, src_object, trg_schema, trg_tbl, trg_column, json_path,
         data_type, convert_arg, convert_rule, is_key, key_order, is_toast, column_order, is_active, description
  FROM _v_setup_registry
  EXCEPT
  SELECT src_schema, src_tbl, src_object_schema, src_object, trg_schema, trg_tbl, trg_column, json_path,
         data_type, convert_arg, convert_rule, is_key, key_order, is_toast, column_order, is_active, description
  FROM lh_vv_ctrl.dbo.ctrl_cfg_schema_registry);
```

Chạy thêm query `EXCEPT` theo chiều ngược lại (bảng `EXCEPT` view). Mong đợi:
- `n = n_keys = EXPECTED["registry"]`.
- Cả hai query `EXCEPT` trả về `0`.
- `src_tbl` chỉ có `partner_raw_data` và `brz_3rd_crawler_poi_stream`.

**K4. Các bảng còn lại trong phạm vi**

```python
import hashlib
POST = {}
for fq in ALLOW:
    if fq.lower() not in {k.lower() for k in BASELINE}:
        continue
    n = int(spark.sql(f"SELECT count(*) AS n FROM {fq}").first()["n"])
    sch = hashlib.md5(spark.table(fq).schema.json().encode()).hexdigest()
    POST[fq] = (n, sch)
bad = []
for fq, (n, sch) in POST.items():
    b = BASELINE[fq.lower()] if fq.lower() in BASELINE else BASELINE[fq]
    if sch != b["schema_md5"]:
        bad.append((fq, "SCHEMA_CHANGED"))
    if fq in KEEP_REF and n != b["rows"]:
        bad.append((fq, f"REF rows {n} != baseline {b['rows']}"))
    if fq in WIPE and fq not in CTRL_SEED and n != 0:
        bad.append((fq, f"rows {n} != 0"))
print("bad =", bad[:50])
```

Mong đợi `bad = []`. Cụ thể:
- Hai bảng ref có số dòng bằng baseline.
- 51 bảng bị xóa và không seed (gồm 4 bảng log/state) có 0 dòng.
- Không bảng nào đổi schema.

**K5. Lịch sử Delta: không có thao tác cấm**

```python
ops = []
for fq, b in BASELINE.items():
    for r in spark.sql(f"DESCRIBE HISTORY {fq}").filter(f"version > {b['version']}").collect():
        ops.append((fq, r["version"], r["operation"]))
print([o for o in ops if o[2] not in ("DELETE", "MERGE")][:50])
```

Mong đợi danh sách in ra rỗng:
- Bảng bị xóa chỉ có thêm `DELETE`.
- Ba bảng seed có thêm `DELETE` rồi `MERGE`.
- Hai bảng ref không có version mới.

Nếu thấy `OPTIMIZE`, `VACUUM START/END`, `RESTORE` hay thay đổi schema, ghi lại và dừng ở `user_decision`.

## Chạy lại để kiểm tra idempotency

Không xóa lại. Trong cùng session (view S2b còn tồn tại), chạy lại nguyên cell S2c. Nếu session đã restart, chạy S2a, rồi S2b, rồi S2c.

Mong đợi:
- Với cả ba bảng: `inserted = 0`, `missing_after = 0`.
- `rows_after` không đổi: 69, 2, và `EXPECTED["registry"]`.
- `_merge_pipeline_config` tính `base = 69` nhưng không chèn dòng nào, vì mọi khóa đã khớp.

Chạy thêm ba query drift, copy từ `id:init_seed_write`, chỉ đọc:

```sql
SELECT count(*) AS n FROM _v_setup_pipeline_config s
JOIN lh_vv_ctrl.dbo.ctrl_mng_pipeline_config t
  ON t.pl_name = s.pl_name AND t.src_schema = s.src_schema AND t.src_tbl = s.src_tbl
 AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl
WHERE NOT (t.is_active <=> s.is_active AND t.priority <=> s.priority AND t.load_mode <=> s.load_mode
       AND t.align_path <=> s.align_path AND t.dedup_order <=> s.dedup_order AND t.nb_name <=> s.nb_name);

SELECT count(*) AS n FROM _v_setup_watermark s
JOIN lh_vv_ctrl.dbo.ctrl_mng_watermark t ON t.watermark_id = s.watermark_id
WHERE NOT (t.src_schema <=> s.src_schema AND t.src_tbl <=> s.src_tbl
       AND t.watermark_column <=> s.watermark_column AND t.status <=> s.status
       AND t.flow_name <=> s.flow_name AND t.watermark_sequence <=> s.watermark_sequence);

SELECT count(*) AS n FROM _v_setup_registry s
JOIN lh_vv_ctrl.dbo.ctrl_cfg_schema_registry t
  ON t.src_schema = s.src_schema AND t.src_tbl = s.src_tbl
 AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl AND t.trg_column = s.trg_column
WHERE NOT (t.src_object_schema <=> s.src_object_schema AND t.src_object <=> s.src_object
       AND t.json_path <=> s.json_path AND t.data_type <=> s.data_type AND t.convert_arg <=> s.convert_arg
       AND t.convert_rule <=> s.convert_rule AND t.is_key <=> s.is_key AND t.key_order <=> s.key_order
       AND t.is_toast <=> s.is_toast AND t.column_order <=> s.column_order
       AND t.is_active <=> s.is_active AND t.description <=> s.description);
```

Mong đợi cả ba query trả về `0`. Sau lần chạy lại, chạy lại K1 đến K4. Kết quả phải giống hệt lần đầu.

## Kiểm tra log và watermark

Mọi query ở mục này chỉ đọc.

```sql
SELECT 'ctrl_log_run' AS t, count(*) AS n FROM lh_vv_ctrl.dbo.ctrl_log_run
UNION ALL SELECT 'ctrl_log_table_run', count(*) FROM lh_vv_ctrl.dbo.ctrl_log_table_run
UNION ALL SELECT 'ctrl_cdc_state', count(*) FROM lh_vv_ctrl.dbo.ctrl_cdc_state
UNION ALL SELECT 'ctrl_cdc_reject', count(*) FROM lh_vv_ctrl.dbo.ctrl_cdc_reject;

SELECT count(*) AS n_other_wm FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id NOT IN ('wm_transform_partner_raw_data', 'wm_transform_brz_3rd_crawler_poi_stream');

SELECT count(*) AS n_locked FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE lock_exec_id IS NOT NULL OR status <> 'INITIALIZED';
```

Mong đợi:
- Bốn bảng log/state có `n = 0`. Seed trong notebook nháp không ghi `ctrl_log_run`, nên log rỗng là đúng.
- `n_other_wm = 0`: không có `wm_e__…` hay `wm_flow__…`.
- `n_locked = 0`.

Nếu bảng log có dòng hoặc watermark không còn `INITIALIZED`, nghĩa là có pipeline hoặc notebook đã chạy sau bước xóa. Ghi lại số dòng (chỉ số tổng hợp) và dừng ở `user_decision`. Không xóa lại khi chưa có quyết định.

Lưu ý vận hành sau seed:
- Hai dòng watermark nguồn có `last_src_version = NULL`. Theo §4, pre-check FL_00 khi đó luôn cho chạy, và notebook extract phải chạy với `allow_full_scan = True`.
- Nếu bronze đã bị xóa rỗng, extract sẽ không có dữ liệu.
- Bật lại pipeline là việc của người dùng: `<CẦN NGƯỜI DÙNG CUNG CẤP: thời điểm và cách bật lại pipeline/trigger>`.

## Rollback và forward recovery

`architecture.md` chưa có nội dung cho mục này. Hướng dẫn dưới đây chỉ dùng thao tác Delta có sẵn và baseline của B2. Mọi rollback cần `user_decision` trước khi chạy.

**Rollback (khôi phục dòng về baseline):**

- Với từng bảng cần khôi phục, dùng `version` đã ghi ở B2:

  ```sql
  RESTORE TABLE <fq> TO VERSION AS OF <version baseline của fq>;
  ```

  Lệnh này khôi phục dòng về đúng version trước khi xóa. Schema không đổi vì task không đổi schema. Không dùng `DROP`, `overwrite` hay `replaceWhere`.
- Thứ tự khôi phục để pipeline không chạy trên trạng thái nửa vời:
  1. Bốn bảng log/state và `ctrl_cfg_schema_registry`.
  2. Bronze, silver, gold.
  3. `ctrl_mng_watermark`.
  4. `ctrl_mng_pipeline_config` sau cùng.
- Điều kiện để `RESTORE` làm được: file của version cũ chưa bị VACUUM. Task không chạy VACUUM. §1 ghi bảy bảng ctrl chưa có lịch VACUUM. Với bronze, silver, gold: `<CẦN NGƯỜI DÙNG CUNG CẤP: xác nhận không có bảo trì bảng hoặc VACUUM tự động trên DEV và thời hạn retention>`. Nếu file đã bị dọn, dữ liệu bronze không lấy lại được trong phạm vi runbook.
- Sau khi rollback, chạy lại B2 và so sánh với baseline: số dòng và `schema_md5` phải trùng.

**Forward recovery:**

- S1 lỗi giữa chừng: `DELETE FROM` không có `WHERE` là idempotent. Sửa nguyên nhân (quyền, lock, session), rồi chạy lại cell S1. Cell này probe lại allowlist trước khi xóa. Bảng đã rỗng vẫn rỗng.
- S2b báo `RuntimeError` (validate, khóa trùng) hoặc `EXPECTED` khác 69 hoặc 2: chưa có MERGE nào chạy, ba bảng ctrl vẫn rỗng. Không tự sửa row literal, dừng ở `user_decision`. Khi `ctrl_mng_pipeline_config` rỗng, FL_00 và các luồng NB_00 không có việc để chạy.
- S2c lỗi sau một hoặc hai MERGE: mỗi MERGE là một transaction riêng. Chạy lại S2c (cùng session, hoặc S2a, S2b, S2c nếu session đã restart). MERGE insert-only chỉ chèn khóa còn thiếu, không tạo bản trùng. Sau đó chạy K1 đến K3.
- `missing_after > 0`: dừng ở `user_decision`. Không chèn tay.
- Phát hiện bảng ngoài allowlist sau khi đã xóa (ví dụ bảng mới xuất hiện giữa B2 và S1): S1 đã tự dừng trước khi xóa. Nếu đã xóa một phần, dừng ở `user_decision` và cân nhắc `RESTORE` theo baseline.
- Không dùng hướng dẫn `DROP` ở §4, `overwrite` + `replaceWhere` ở §5, hay `NB_CREATE_DDL` để sửa.

## Kết quả người dùng ghi nhận

Người dùng điền sau khi chạy. Author không chạy lệnh nào trên Fabric.

| Hạng mục | Giá trị mong đợi | Kết quả thực tế |
|---|---|---|
| Workspace (B1), `ENV_IS_DEV` | DEV, `True` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Người chạy, thời điểm UTC bắt đầu/kết thúc | — | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Cách đảm bảo không có pipeline chạy | — | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| `scope_errors` (B2) | Rỗng, hoặc chỉ "không tồn tại" cho schema `enr` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| `outside_allowlist`, `outside_ref` (B2) | `[]`, `[]` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| `missing_in_env` (B2) | Không có bảng ctrl | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Baseline (fq, rows, version, schema_md5) | Output B2 | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| `running_runs`, `held_locks` (B3) | 0, 0 | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| `DELETE_RESULTS` (S1) | Mọi giá trị `0` hoặc `SKIP_NOT_LIVE` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| `EXPECTED` (S2b) | `pipeline_config` 69, `watermark` 2, `registry` = ? | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| `SEED_RESULTS` lần 1 (S2c) | inserted 69 / 2 / `EXPECTED["registry"]`, missing_after 0 | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| K1 đến K3 | Như mục Kiểm tra kết quả | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| K4 `bad` | `[]` | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| K5 thao tác ngoài DELETE/MERGE | Rỗng | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| `SEED_RESULTS` lần 2 (idempotency) | inserted 0 ở cả ba bảng, drift 0 / 0 / 0 | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Log/state và watermark | 4 bảng = 0, `n_other_wm` = 0, `n_locked` = 0 | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
| Lệch hoặc dừng ở `user_decision` (nếu có) | — | `<CẦN NGƯỜI DÙNG CUNG CẤP>` |
