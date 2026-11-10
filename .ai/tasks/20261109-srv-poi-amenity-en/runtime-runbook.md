# Runtime runbook — 20261109-srv-poi-amenity-en

Người dùng tự chạy runbook này trên Fabric DEV và PostgreSQL. Agent không chạy bước nào trong đây: không chạy Fabric, DROP, Copy Job, docker hay deploy.

## Phạm vi và môi trường

- Môi trường: Fabric workspace DEV `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`, PostgreSQL DEV `<CẦN NGƯỜI DÙNG CUNG CẤP: host/database PostgreSQL DEV>`, `data-serving-service` DEV `<CẦN NGƯỜI DÙNG CUNG CẤP: base URL API DEV>`.
- Mục tiêu: thêm cột `amenity_en` (đứng ngay sau `amenity`) ở mọi tầng. Từ nay `amenity` là mã snake_case `amenity_code(amenity_en)`. API giữ nguyên path `GET /api/v1/pois/{poi_id}/amenities` (D-02) và trả cây D-01 (`amenity_group`, `items[].amenity_code`, `amenity_label_en`, `amenity_label_vi`, `service_flags`). API không còn dùng `lang` hay `Accept-Language`.
- Các bảng bị tác động:
  - `lh_vv_silver.dbo.ref_dictionary_amenities`: DROP rồi tạo lại (U-3).
  - `lh_vv_silver.dbo.slv_poi_amenity`: `ALTER ... ADD COLUMNS (amenity_en STRING AFTER amenity)`, không DROP.
  - `lh_vv_gold.dbo.gld_srv_poi_amenity`: DROP rồi tạo lại bằng `NB_CREATE_DDL` cell `amenddlpy`.
  - PostgreSQL `apps.srv_poi_amenity`: DROP rồi tạo lại theo `sql/postgres/gld_srv_serve.pg.sql`.
- Thứ tự cột chung của slv, gold và PostgreSQL: `poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_en, amenity_vi, service_flags, row_hash, created_at, updated_at, deleted_at`. PK không đổi: `(poi_id, business_sector, amenity_group, amenity_raw)`.
- Notebook và tham số lấy từ cell tham số trong repo:
  - `NB_SETUP_POI_AMENITY`, cell `c1setupparam`: `p_apply = "false"` (mặc định). Lượt plan dùng `"false"`, lượt apply dùng `"true"`.
  - `NB_SLV_POI_AMENITY`, cell `d1amenparam`: `p_exec_id = ""`, `p_run_id = ""`, `p_pl_name = ""`, `p_trg_fq = ""`, `p_pinned_json = ""`, `p_mode = "RUN"`, `p_force = "false"`, `p_history_limit = "1000"`.
  - `NB_GLD_SRV_POI_AMENITY`, cell `srvamenityparam`: `p_exec_id = ""`, `p_run_id = ""`, `p_pl_name = ""`, `p_trg_fq = ""`, `p_pinned_json = ""`, `p_mode = "RUN"`, `p_force = "false"`, `p_history_limit = "1000"`. Bước R-6 đổi `p_force = "true"`.
- Pipeline phải tạm dừng: `PL_VV_TRANS_SLV_TO_ENR_15M`, `PL_VV_TRANS_SLV_TO_GLD_1H`.
- Copy Job Fabric → PostgreSQL: repo không ghi tên, nên dùng `<CẦN NGƯỜI DÙNG CUNG CẤP: tên Copy Job đồng bộ gld_srv_poi_amenity → apps.srv_poi_amenity>`.
- Giới hạn cho mọi truy vấn mẫu: tối đa 50 dòng, không lấy dữ liệu cá nhân, không ghi secret hay chuỗi kết nối vào runbook hoặc phần kết quả.

## Điều kiện tiên quyết

1. Code của task đã merge hoặc đã có trên nhánh dùng để deploy, và test local đều xanh:
   - `python -m pytest tests/test_poi_amenity_contract.py tests/test_srv_poi_serving_contract.py tests/test_poi_media_amenity_contract.py tests/test_initial_ddl_contract.py tests/test_poi_entity_contract.py tests/test_enr_poi_contract.py -q`
   - `python -m pytest tests -q`
   - `cd services/data-serving-service && mvnw.cmd -q -B test`
2. Người chạy có quyền DROP/CREATE trên `lh_vv_silver` và `lh_vv_gold`, có quyền DDL trên schema `apps` của PostgreSQL DEV, quyền sửa và chạy Copy Job, và quyền deploy `data-serving-service` DEV.
3. Không có run nào đang giữ khoá luồng. Truy vấn sau (read-only) phải không trả dòng nào có `status = 'RUNNING'` và `lock_exec_id` khác NULL:

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN ('wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M', 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_1H')
LIMIT 50;
```

4. Nếu Fabric từ chối `ADD COLUMNS ... AFTER` ở R-4 (P-2 fail), DỪNG lại (S-3). Phương án DROP slv rồi chạy lại setup cần người dùng duyệt riêng, vì cách đó làm mất `created_at` và reset change detection của `NB_ENR_POI_INFO`.

## Baseline trước khi chạy

R-0: ghi lại các mốc sau vào phần `Kết quả người dùng ghi nhận`. Mọi truy vấn ở đây đều read-only.

```sql
-- B-1: version mới nhất của slv. Đây là mốc <R-0> cho RESTORE khi rollback.
DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_amenity LIMIT 5;

-- B-2: số dòng slv
SELECT count(*) AS slv_total, count_if(deleted_at IS NULL) AS slv_active
FROM lh_vv_silver.dbo.slv_poi_amenity;

-- B-3: số dòng gold
SELECT count(*) AS gld_total, count_if(deleted_at IS NULL) AS gld_active
FROM lh_vv_gold.dbo.gld_srv_poi_amenity;

-- B-4: số dòng ref hiện tại
SELECT count(*) AS ref_total FROM lh_vv_silver.dbo.ref_dictionary_amenities;

-- B-5: schema hiện tại
DESCRIBE lh_vv_silver.dbo.ref_dictionary_amenities;
DESCRIBE lh_vv_silver.dbo.slv_poi_amenity;
DESCRIBE lh_vv_gold.dbo.gld_srv_poi_amenity;
```

PostgreSQL:

```sql
-- B-6: số dòng PostgreSQL
SELECT count(*) AS pg_total, count(*) FILTER (WHERE deleted_at IS NULL) AS pg_active
FROM apps.srv_poi_amenity;
```

Ghi thêm các mốc sau:
- Một `poi_id` có amenity, dùng cho P-7: `<CẦN NGƯỜI DÙNG CUNG CẤP: poi_id mẫu có amenity>`.
- Response API hiện tại của POI đó (chỉ cần shape JSON).

## Các bước thực hiện

**R-1. Tạm dừng pipeline và đồng bộ notebook**
1. Tắt trigger hoặc schedule của `PL_VV_TRANS_SLV_TO_ENR_15M` và `PL_VV_TRANS_SLV_TO_GLD_1H`.
2. Chờ run đang chạy (nếu có) kết thúc. Chạy lại truy vấn khoá ở mục Điều kiện tiên quyết, mục 3.
3. Đồng bộ các notebook đã sửa lên workspace: `NB_SETUP_POI_AMENITY`, `NB_SETUP_INITIAL_DDL`, `NB_SLV_POI_AMENITY`, `NB_GLD_SRV_POI_AMENITY`, `NB_CREATE_DDL`.

**R-2. Setup, lượt plan**
- Chạy `NB_SETUP_POI_AMENITY` với `p_apply = "false"`.
- Kết quả mong đợi trong PLAN JSON: `ref_has_amenity_en=false`, `slv_has_amenity_en=false`, 173 key mới và 173 key stale.
- Nếu kết quả khác, DỪNG lại và ghi output vào phần kết quả.

**R-3. DROP ref (U-3)**

```sql
DROP TABLE lh_vv_silver.dbo.ref_dictionary_amenities;
```

**R-4. Setup, lượt apply**
- Chạy `NB_SETUP_POI_AMENITY` với `p_apply = "true"`.
- Kết quả mong đợi: `inserted=175 drift=0 stale=0`, slv đã được ALTER thêm `amenity_en`, và check `EXPECTED` pass.
- Kiểm tra ngay P-1 và P-2 (mục Kiểm tra kết quả). Nếu P-2 fail vì `AFTER` bị từ chối, DỪNG lại (S-3).

**R-5. Tạo lại bảng gold**

```sql
DROP TABLE lh_vv_gold.dbo.gld_srv_poi_amenity;
```

Chạy ngay `NB_CREATE_DDL`, chỉ cell code có `PL = "PL_VV_TRANS_SLV_TO_GLD_1H"` và `AMENITY_COLS`. Markdown ngay trên cell đó có dòng `20261109: thêm amenity_en; bảng cũ phải DROP trước khi chạy cell này.` Cell media đứng trước, cùng tiêu đề `[THÊM 26/10] 20261025-poi-media-and-srv-amenity`, cũng mở bằng `import uuid`, nhưng `PL = "PL_VV_TRANS_SLV_TO_GLD_30P"`. Không chạy cell media.

**R-6. Chạy slv rồi gold**
1. Chạy `NB_SLV_POI_AMENITY` một lần với tham số mặc định: `p_exec_id = ""`, `p_run_id = ""`, `p_pl_name = ""`, `p_trg_fq = ""`, `p_pinned_json = ""`, `p_mode = "RUN"`, `p_force = "false"`, `p_history_limit = "1000"`. Cách khác: chạy tay pipeline `PL_VV_TRANS_SLV_TO_ENR_15M` một lần.
2. Chạy `NB_GLD_SRV_POI_AMENITY` với `p_exec_id = ""`, `p_run_id = ""`, `p_pl_name = ""`, `p_trg_fq = ""`, `p_pinned_json = ""`, `p_mode = "RUN"`, `p_force = "true"`, `p_history_limit = "1000"`. Cách khác: chạy tay pipeline `PL_VV_TRANS_SLV_TO_GLD_1H` một lần.
3. Kiểm tra P-3, P-4 và P-5. Ghi lại số dòng gold mới, P-6 sẽ cần số này.

**R-7. PostgreSQL: tạo lại bảng serving**

Chạy trong một transaction. Câu CREATE lấy nguyên văn từ `sql/postgres/gld_srv_serve.pg.sql`:

```sql
BEGIN;
DROP TABLE apps.srv_poi_amenity;
CREATE TABLE apps.srv_poi_amenity (
    poi_id text NOT NULL,
    business_sector text NOT NULL,
    amenity_group text NOT NULL,
    amenity_raw text NOT NULL,
    amenity text,
    amenity_en text,
    amenity_vi text,
    service_flags text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (poi_id, business_sector, amenity_group, amenity_raw)
);
COMMIT;
```

Mở Copy Job `<CẦN NGƯỜI DÙNG CUNG CẤP: tên Copy Job>` và kiểm tra column mapping từ `lh_vv_gold.dbo.gld_srv_poi_amenity` sang `apps.srv_poi_amenity`. Mapping phải có `amenity_en` → `amenity_en`. Nếu chưa có thì thêm vào.

**R-8. Chạy Copy Job**
- Chạy Copy Job `<CẦN NGƯỜI DÙNG CUNG CẤP: tên Copy Job>`, rồi kiểm tra P-6.

**R-9. Deploy API và bật lại pipeline**
1. Deploy `data-serving-service` lên DEV, dùng build có code của task: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách deploy / version build>`.
2. Kiểm tra P-7.
3. Bật lại trigger của `PL_VV_TRANS_SLV_TO_ENR_15M` và `PL_VV_TRANS_SLV_TO_GLD_1H`.

## Kiểm tra kết quả

Mọi truy vấn trong mục này đều read-only.

**P-1. ref** (sau R-4)

```sql
SELECT count(*) AS ref_total,
       count(DISTINCT source_name, business_sector, amenity_group, amenity_raw, amenity) AS ref_key_distinct
FROM lh_vv_silver.dbo.ref_dictionary_amenities;
-- Mong đợi: 175 và 175

SELECT count(*) FROM lh_vv_silver.dbo.ref_dictionary_amenities
WHERE amenity <> regexp_replace(
        regexp_replace(lower(regexp_replace(translate(amenity_en, 'é', 'e'), '([a-z])([A-Z])', '$1_$2')),
                       '[^a-z0-9]+', '_'),
        '^_+|_+$', '');
-- Mong đợi: 0
```

Output của setup phải in `stale=0 drift=0`.

**P-2. Schema slv** (sau R-4)

```sql
DESCRIBE lh_vv_silver.dbo.slv_poi_amenity;
```

Mong đợi: `amenity_en` (STRING) nằm giữa `amenity` và `amenity_vi`, và check `EXPECTED` của setup pass.

**P-3. slv** (sau R-6)

```sql
SELECT count(*) FROM lh_vv_silver.dbo.slv_poi_amenity
WHERE deleted_at IS NULL AND (amenity IS NULL OR amenity_en IS NULL);
-- Mong đợi: 0

SELECT count(*) FROM lh_vv_silver.dbo.slv_poi_amenity s
LEFT ANTI JOIN lh_vv_silver.dbo.ref_dictionary_amenities r
  ON r.source_name = 'google' AND r.is_active AND r.business_sector = s.business_sector
 AND r.amenity_group = s.amenity_group AND r.amenity = s.amenity AND r.amenity_en = s.amenity_en
WHERE s.deleted_at IS NULL;
-- Mong đợi: 0
```

Metric `dict_amenity_en_blank=0` phải có trong output của notebook hoặc trong `qg_json` (xem mục Kiểm tra log và watermark).

**P-4. Grain của slv**

```sql
SELECT count(*) AS total,
       count(DISTINCT poi_id, business_sector, amenity_group, amenity_raw) AS key_distinct
FROM lh_vv_silver.dbo.slv_poi_amenity;
-- Mong đợi: total = key_distinct
```

**P-5. So khớp gold với slv**

```sql
SELECT count(*) FROM (
  SELECT poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_en, amenity_vi, service_flags, deleted_at
  FROM lh_vv_silver.dbo.slv_poi_amenity
  EXCEPT
  SELECT poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_en, amenity_vi, service_flags, deleted_at
  FROM lh_vv_gold.dbo.gld_srv_poi_amenity
);
-- Mong đợi: 0

SELECT count(*) FROM (
  SELECT poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_en, amenity_vi, service_flags, deleted_at
  FROM lh_vv_gold.dbo.gld_srv_poi_amenity
  EXCEPT
  SELECT poi_id, business_sector, amenity_group, amenity_raw, amenity, amenity_en, amenity_vi, service_flags, deleted_at
  FROM lh_vv_silver.dbo.slv_poi_amenity
);
-- Mong đợi: 0

DESCRIBE lh_vv_gold.dbo.gld_srv_poi_amenity;
-- Mong đợi: khớp AMENITY_COLS, có amenity_en STRING ngay sau amenity
```

Mẫu kiểm tra bằng mắt (không có dữ liệu cá nhân, tối đa 50 dòng):

```sql
SELECT business_sector, amenity_group, amenity, amenity_en, amenity_vi, service_flags
FROM lh_vv_gold.dbo.gld_srv_poi_amenity
WHERE deleted_at IS NULL
LIMIT 50;
```

**P-6. PostgreSQL** (sau R-8)

```sql
SELECT count(*) FROM apps.srv_poi_amenity;
-- Mong đợi: bằng count(*) của gold đo ở R-6

SELECT count(*) FROM apps.srv_poi_amenity WHERE deleted_at IS NULL AND amenity_en IS NULL;
-- Mong đợi: 0

SELECT count(*) FROM apps.srv_poi_amenity WHERE amenity !~ '^[a-z0-9]+(_[a-z0-9]+)*$';
-- Mong đợi: 0
```

**P-7. API** (sau R-9)

```
curl -s "<CẦN NGƯỜI DÙNG CUNG CẤP: base URL API DEV>/api/v1/pois/<poi_id mẫu>/amenities"
curl -s "<CẦN NGƯỜI DÙNG CUNG CẤP: base URL API DEV>/api/v1/pois/<poi_id mẫu>/amenities?lang=en"
curl -s -H "Accept-Language: en" "<CẦN NGƯỜI DÙNG CUNG CẤP: base URL API DEV>/api/v1/pois/<poi_id mẫu>/amenities"
curl -s -o /dev/null -w "%{http_code}" "<CẦN NGƯỜI DÙNG CUNG CẤP: base URL API DEV>/api/v1/pois/<CẦN NGƯỜI DÙNG CUNG CẤP: poi_id không tồn tại>/amenities"
```

Mong đợi:
- `data[]` có `amenity_group` và `items[]`. Mỗi item có `amenity_code`, `amenity_label_en`, `amenity_label_vi` và `service_flags`.
- Không còn `data[].amenity_vi` hay `items[].amenity_label`.
- Group sắp tăng dần theo `amenity_group`. Item sắp theo `amenity_code` (null đứng cuối), rồi theo `amenity_raw`.
- `amenity_label_vi` khác `service_flags` ở những dòng mà dữ liệu khác nhau.
- Ba lời gọi đầu trả `data` giống hệt nhau.
- POI không tồn tại trả 404.

## Chạy lại để kiểm tra idempotency

Chạy lần lượt từng bước dưới đây, mỗi bước xong thì ghi output.

1. Chạy lại `NB_SETUP_POI_AMENITY` với `p_apply = "true"`. Mong đợi: `inserted=0 drift=0 stale=0`, slv không bị ALTER lần nữa, và check `EXPECTED` pass. MERGE chỉ insert, không có `WHEN MATCHED`.
2. Chạy lại `NB_SLV_POI_AMENITY` với tham số mặc định (`p_mode = "RUN"`, `p_force = "false"`). Mong đợi: `ctrl_log_table_run` ghi `inserted_rows = 0` và `updated_rows = 0` (hoặc `status = 'NO_DATA'`) cho `slv_poi_amenity`.
3. Chạy lại `NB_GLD_SRV_POI_AMENITY` với `p_force = "false"`. Mong đợi: `inserted_rows = 0` và `updated_rows = 0` (hoặc `NO_DATA`) cho `gld_srv_poi_amenity`.
4. Chạy lại Copy Job `<CẦN NGƯỜI DÙNG CUNG CẤP: tên Copy Job>`. Mong đợi: số dòng PostgreSQL không đổi và P-6 vẫn pass.
5. Chạy lại P-1 đến P-6. Mọi kết quả phải giống lần đầu.

## Kiểm tra log và watermark

Mọi truy vấn trong mục này đều read-only.

```sql
-- Log từng node của slv và gold (gồm metric dict_amenity_en_blank trong qg_json)
SELECT exec_id, pl_name, trg_tbl, status, entity_rows, inserted_rows, updated_rows, deactivated_rows,
       trg_version, started_at, ended_at, error_message, qg_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl IN ('slv_poi_amenity', 'gld_srv_poi_amenity')
ORDER BY started_at DESC
LIMIT 50;

-- Log cấp run
SELECT exec_id, run_id, pl_name, nb_name, run_mode, table_filter, status, started_at, ended_at, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE nb_name IN ('NB_SLV_POI_AMENITY', 'NB_GLD_SRV_POI_AMENITY')
   OR pl_name IN ('PL_VV_TRANS_SLV_TO_ENR_15M', 'PL_VV_TRANS_SLV_TO_GLD_1H')
ORDER BY started_at DESC
LIMIT 50;

-- Watermark cạnh của hai node và khoá luồng
SELECT watermark_id, src_tbl, trg_tbl, status, last_src_version, last_src_table_id,
       last_success_at, last_run_id, error_message, lock_exec_id, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e__slv_poi_amenity__%'
   OR watermark_id LIKE 'wm_e__gld_srv_poi_amenity__%'
   OR watermark_id IN ('wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M', 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_1H')
LIMIT 50;
```

Mong đợi:
- Các node ở R-6 có `status` là `SUCCESS` (hoặc `NO_DATA` ở lần chạy lại), và `error_message` là NULL.
- `qg_json` của `slv_poi_amenity` có `dict_amenity_en_blank` bằng 0.
- Cạnh có input là `ref_dictionary_amenities` hoặc `gld_srv_poi_amenity` vừa được tạo lại sẽ có `last_src_table_id` mới. Đây là trường hợp `TABLE_RECREATED`, là hành vi đúng.
- Không có dòng `wm_flow__` nào kẹt ở `RUNNING` sau khi các run kết thúc.

Không sửa tay dòng `wm_e__` hay `wm_flow__`. Muốn ép node tính lại thì dùng `p_force`.

## Rollback và forward recovery

**Forward recovery (mặc định).** Mọi bước đều chạy lại được, và mọi lỗi đều fail closed: dừng trước khi ghi.
- Setup lỗi (guard `ref` thiếu `amenity_en`, `EXPECTED` lệch): sửa nguyên nhân rồi chạy lại R-4. Nếu `ref` đang ở trạng thái dở, DROP `ref` rồi chạy lại R-4.
- slv raise vì `ref` thiếu `amenity_en` STRING, hoặc vì có dòng google active bị trống `amenity`/`amenity_en`: quay lại kiểm tra P-1, rồi chạy lại R-6.
- Gold lỗi: chạy lại R-5 (DROP và `amenddlpy`) rồi R-6.
- PostgreSQL hoặc Copy Job lỗi: chạy lại R-7 rồi R-8. R-7 chạy trong một transaction, lỗi thì tự ROLLBACK.
- P-2 fail vì `ADD COLUMNS ... AFTER` bị từ chối: DỪNG lại theo S-3 và chờ người dùng duyệt phương án DROP slv.

**Full rollback** (chỉ khi thay đổi bị từ chối):
1. Revert code về commit trước task.
2. Khôi phục slv:
   ```sql
   RESTORE TABLE lh_vv_silver.dbo.slv_poi_amenity TO VERSION AS OF <version ghi ở R-0 (B-1)>;
   ```
   Lệnh này trả cả schema về như cũ, điều mà check `EXPECTED` của code cũ cần.
3. `DROP TABLE lh_vv_silver.dbo.ref_dictionary_amenities;` rồi chạy `NB_SETUP_POI_AMENITY` bản cũ với `p_apply = "true"`.
4. `DROP TABLE lh_vv_gold.dbo.gld_srv_poi_amenity;` rồi chạy `amenddlpy` bản cũ, rồi chạy `NB_GLD_SRV_POI_AMENITY` bản cũ với `p_force = "true"`.
5. Tạo lại `apps.srv_poi_amenity` bằng DDL cũ (không có `amenity_en`), bỏ `amenity_en` khỏi mapping của Copy Job, rồi chạy Copy Job.
6. Redeploy API bản cũ, rồi bật lại hai pipeline.

**Rollback chỉ API**, sau khi dữ liệu đã migrate: chấp nhận được dù bị suy giảm. API cũ bỏ qua `amenity_en` và hiển thị `amenity` dạng snake_case vừa làm nhãn tiếng Anh vừa làm mã.

## Kết quả người dùng ghi nhận

Ghi đến 2026-11-10. Mẫu dưới 50 dòng, không có dữ liệu cá nhân. Người dùng chốt runtime và yêu cầu chuyển `ready_to_merge`.

### Khoá luồng

`wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M` = `NO_DATA`, `lock_exec_id` null, `updated_at` 2026-11-04T06:40:13Z. `wm_flow__PL_VV_TRANS_SLV_TO_GLD_1H` = `SUCCESS`, `lock_exec_id` null, `updated_at` 2026-11-05T06:34:52Z. Không có `RUNNING`.

### R-0 baseline

- B-1: version mới nhất của `slv_poi_amenity` là **2** (2026-10-30T08:32:22Z, MERGE, `numTargetRowsInserted` 42178). Đây là mốc `RESTORE`. Version 1: 2026-10-20T10:24:49Z MERGE 58 dòng. Version 0: 2026-10-20T09:39:24Z CREATE TABLE.
- B-2: `slv_total` 42236, `slv_active` 42236.
- B-3: `gld_total` 42236, `gld_active` 42236.
- B-4: `ref_total` 175.
- B-5: cả `ref_dictionary_amenities`, `slv_poi_amenity` và `gld_srv_poi_amenity` chưa có `amenity_en`. `amenity` đứng ngay trước `amenity_vi`.
- B-6: `pg_total` 42236, `pg_active` 42236.
- Chưa ghi `poi_id` mẫu cho P-7.

### R-1 đến R-4

- R-1: Success. Notebook đã đồng bộ, hai pipeline đang tắt.
- R-2 plan: `google=101 partner=74 missing_keys=173 stale_keys=173 entity_edges_ok=7 ref_has_amenity_en=false slv_has_amenity_en=false`. Exit `PLAN`.
- R-3: `DROP TABLE lh_vv_silver.dbo.ref_dictionary_amenities` Success.
- R-4 apply: dòng in từ `c1setupplan` (chạy trước DDL) là `missing_keys=0 stale_keys=0 ref_has_amenity_en=False slv_has_amenity_en=False`. Exit `SUCCESS`, `inserted=175 drift=0 stale=0 edges_inserted=0 edges_retired=0`. Check `EXPECTED` đã qua vì merge chạy sau DDL và notebook thoát `SUCCESS`.

### P-1

`ref_total` 175, `ref_key_distinct` 175. Số dòng `amenity` lệch quy tắc U-1: 0. Pass.

### P-2

Chưa có `DESCRIBE lh_vv_silver.dbo.slv_poi_amenity`. R-4 thoát `SUCCESS` sau check `EXPECTED`, nên thứ tự cột đã khớp trước khi MERGE.

### R-5

Lần chạy 2026-11-10 ra `RuntimeError`: `Dừng trước khi ghi` vì bốn cạnh media (`slv_3p_poi_media`, `slv_pn_business_service_i18ns`, `slv_pn_business_services` → `slv_poi_media_info`, và `slv_poi_media_info` → `gld_srv_poi_media_gallery`) đang active trên `PL_VV_TRANS_SLV_TO_GLD_30M`. Đó là cell media `mediaddlpy` (`PL = "PL_VV_TRANS_SLV_TO_GLD_30P"`), không phải cell amenity. Cell dừng trước khi ghi bảng và cạnh. Có thể đã MERGE dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P` nếu dòng đó chưa có, rồi nhả khoá với `status = FAILED`. Đọc lại khoá lúc 2026-11-09T17:01:39Z: `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P` = `FAILED`, `flow_name` `NB_CREATE_DDL`, `lock_exec_id` null, `error_message` là đúng lỗi media ở trên. `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` = `NO_DATA`, `updated_at` 2026-11-09T03:34:32Z, khoá null. `wm_flow__PL_VV_TRANS_SLV_TO_GLD_1H` = `SUCCESS`, `updated_at` 2026-11-05T06:34:52Z, khoá null. Chưa xoá dòng `30P`.

`SHOW TABLES IN lh_vv_gold` lỗi `SCHEMA_NOT_FOUND` trên `default.sgr_visitvn_dev.lh_vv_bronze.lh_vv_gold`. `DESCRIBE lh_vv_gold.dbo.gld_srv_poi_amenity` xác nhận bảng không còn. Không DROP thêm.

Cell `PL = "PL_VV_TRANS_SLV_TO_GLD_1H"` pass: `lh_vv_gold.dbo.gld_srv_poi_amenity: đã tạo`. Cạnh active đúng một cạnh `slv_poi_amenity` → `gld_srv_poi_amenity` trên `PL_VV_TRANS_SLV_TO_GLD_1H`, `RECOMPUTE`, `NB_GLD_SRV_POI_AMENITY`.

### R-6

`NB_SLV_POI_AMENITY` `p_force = "false"`: `SUCCESS`, exec `66f85d04-8dec-4d90-bbeb-b22222e18eb7`, `TABLE_RECREATED` trên `ref_dictionary_amenities`, insert 0, update 42236, xoá mềm 0, `trg_version` 4. `NB_GLD_SRV_POI_AMENITY` `p_force = "true"`: `SUCCESS`, exec `a3196e34-e90f-4891-af83-8d5c3d6f9a6e`, `DATA_CHANGED` kèm `p_force`, insert 42236, update 0, `trg_version` 1.

P-3: active null `amenity`/`amenity_en` = 0; anti-join google active = 0. P-4: `total` 42236 = `key_distinct` 42236. P-5: `EXCEPT` slv trừ gold = 0 và `gld_total` 42236 bằng slv, nên chiều gold trừ slv cũng rỗng. Log không in `dict_amenity_en_blank`; count null đã bằng 0.

### R-7, R-8, P-6

Người dùng xác nhận P-6 đúng mong đợi: `apps.srv_poi_amenity` count 42236, active `amenity_en` null bằng 0, `amenity` lệch `^[a-z0-9]+(_[a-z0-9]+)*$` bằng 0. Tên Copy Job chưa được ghi.

### R-9 local

API local đã chạy trên `http://127.0.0.1:8080`, nối PostgreSQL Dev schema `apps` (PostgreSQL 18.6). File `.env` lúc đầu dùng tiền tố PowerShell `$env:`; đã bỏ tiền tố để còn tên `POSTGRES__DP_POI__*`. Không ghi secret.

`apps.srv_poi_info` active 292. `apps.srv_poi_amenity` active 42236. Số `poi_id` có ở cả hai bảng: 0. Một POI trong info trả 200 với `data` rỗng, và `?lang=en` cùng `Accept-Language: en` cho cùng `data`. `poi_does_not_exist` trả 404.

Ba `poi_id` lúc 2026-11-10T03:04Z trả `404` vì còn `validatePoiExists`. Sau A-1, lúc 2026-11-10T03:30Z cả ba trả 200, `data` có `amenity_group` và `items[]` với `amenity_code`, `amenity_label_en`, `amenity_label_vi`, `service_flags`.

- `5bc3f432-cd37-a6dd-4f8d-4ffea971d83b`: 1 nhóm `space_and_services`, 3 item (`good_for_children`, `restroom`, `table_service`).
- `5bccea92-bdbc-f621-5419-38171846b43f`: cùng 1 nhóm và 3 item.
- `5bd64244-c77d-5bbe-7ac6-450f8c3e8d5a`: `space_and_services` rồi `specialty_tags`. Item sắp theo `amenity_code`. `seafood` có `service_flags` null.

2026-11-10: người dùng đã bật lại trigger của `PL_VV_TRANS_SLV_TO_ENR_15M` và `PL_VV_TRANS_SLV_TO_GLD_1H`. Nguyên văn: đã bật lại trigger và kết quả đều đúng mong đợi. Không có log idempotency riêng. API chưa deploy; bằng chứng API là process local theo R-9.

