# Runtime runbook — 20261120-legacy-gold-init-mapping-audit (vòng 2, D-07)

## Phạm vi và môi trường

- Task: `20261120-legacy-gold-init-mapping-audit`. Vòng này chạy lại init gold cũ sau khi áp dụng D-07. D-07: khi `lower(trim($.is_24_7))` của `poi_opening_hours_json` bằng `true`, cột `operating_hours` nhận JSON case 2 của mapping: 7 ngày (1..7), `is_open_all_day` true, `is_closed` false, không có `open_time`, `close_time` hay `value`. Mã đếm là `IS_24_7`, và `periods_json` không được đọc. Các period lỗi khác vẫn ra mã `GOOGLE_BAD_TIME` và giá trị NULL (D-05).
- Vòng này chỉ đổi `operating_hours`. Bốn cột `holiday_exceptions`, `rating_count`, `review_count`, `is_recommended` giữ quy tắc của vòng 1 (D-03, D-04). Không có DDL. MERGE, `load_origin`, khối `BEGIN_HOURS_PURE` và thứ tự stage giữ nguyên.
- Notebook: `notebooks/NB_SETUP_LEGACY_GOLD_POI`.
- Workspace: `sgr_visitvn_dev`. Notebook raise nếu mở ở workspace khác.
- Default lakehouse: `lh_vv_gold`.
- Cell tham số `lgpparams`. Giá trị mặc định trong file:
  - `p_mode = "PLAN"`: chỉ nhận `PLAN` hoặc `RUN`. `PLAN` không ghi.
  - `p_pin_json = ""`: chuỗi JSON object chứa version Delta của gold cũ.
- Pin dùng cho mọi lần chạy trong runbook này (lấy từ author input và architecture, mục Rollout bước 3). Phải dùng đúng từng ký tự:

```
{"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}
```

- Nguồn đọc (gold cũ, chỉ đọc theo pin): `sgr_visitvn_prd_batch.lh_vv_gold.dbo`, gồm các bảng `poi_master`, `poi_enrichment_display`, `poi_detail`, `poi_review`, `poi_rating`.
- Bảng đích (chỉ `sgr_visitvn_dev`). Khi `RUN`, notebook ghi lần lượt map → info → multi_lang → review → media → amenity:
  - `sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map`
  - `sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info` (bảng chính của task)
  - `sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang`
  - `sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_review`
  - `sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_media_gallery`
  - `sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_amenity`
- Khoá luồng: `PL = "PL_VV_TRANS_SLV_TO_GLD_30M"`, nằm ở dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` của `lh_vv_ctrl.dbo.ctrl_mng_watermark`. Notebook chỉ lấy khoá khi `RUN` (`acquire_flow_lock(PL, EXEC, EXEC, LOCK_TIMEOUT_DEFAULT_MIN)`), gọi `refresh_flow_lock` trước mỗi lần ghi, và nhả khoá trong `finally` với trạng thái `SUCCESS` hoặc `FAILED`.
- Người dùng tự chạy Fabric. Chat này không chạy Fabric. Kết quả dán lại chỉ gồm số đếm và mã, mỗi kết quả tối đa 50 dòng. Không dán tên POI, dữ liệu cá nhân, `poi_id` cụ thể hay text giờ mở cửa.

## Điều kiện tiên quyết

1. Code notebook có D-07 (`legacy_hours(source_name, text, all_day=False)` trong `lgppure`; `is_247`, lời gọi `hours_udf` ba tham số, biểu thức `reason` mới và khoá `hours_24_7_partner_n` trong `lgpmain`) đã được đồng bộ lên Fabric DEV. Phiên bản đã đồng bộ: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit git hoặc cách xác nhận bản notebook trên Fabric DEV khớp bản local>`.
2. Test local đã xanh. Ghi kết quả vào mục cuối:

```
python -m pytest tests/test_legacy_gold_poi_init_contract.py tests/test_gld_srv_poi_contract.py -q
```

   Phải có `test_legacy_hours_is_24_7` và `test_init_is_24_7_path` đạt, và `test_hours_block_is_verbatim_copy` vẫn đạt.
3. Cả 5 bảng `gld_srv_*` đã có cột `load_origin` kiểu `string`, và map có đủ 7 cột id. Nếu thiếu, notebook tự raise ở preflight.
4. Pipeline `PL_VV_TRANS_SLV_TO_GLD_30M` không chạy trong lúc RUN. Khoá luồng phải trống hoặc đã quá hạn (truy vấn B4). Thời gian timeout là hằng `LOCK_TIMEOUT_DEFAULT_MIN` trong lib: `<CẦN NGƯỜI DÙNG CUNG CẤP: giá trị LOCK_TIMEOUT_DEFAULT_MIN, nếu cần ghi lại>`.
5. Số liệu baseline PLAN vòng 1 (`evidence/results/plan-summary.json`, dùng làm ngưỡng): `candidates = 45476`, `OK = 29988`, `NO_PERIODS = 9058`, `GOOGLE_BAD_TIME = 6430`. Google `LEGACY_INIT` trước sửa có `oh_null = 25917`.

## Baseline trước khi chạy

Mọi truy vấn trong phần này chỉ đọc. Chạy trong workspace `sgr_visitvn_dev`.

**B1. Version hiện tại của bảng info.** Chỉ ghi các cột `version`, `timestamp`, `operation`, `userMetadata`. Ghi version mới nhất là `v_baseline`.

```sql
DESCRIBE HISTORY sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info LIMIT 10;
```

**B2. Phân bố theo chủ sở hữu và nguồn**, chỉ có số đếm:

```sql
SELECT load_origin, source_name, count(*) AS n,
       sum(CASE WHEN operating_hours IS NULL THEN 1 ELSE 0 END)    AS oh_null,
       sum(CASE WHEN operating_hours LIKE '%"is_open_all_day":true%' THEN 1 ELSE 0 END) AS all_day_n,
       sum(CASE WHEN holiday_exceptions IS NULL THEN 1 ELSE 0 END) AS he_null,
       sum(CASE WHEN rating_count IS NULL THEN 1 ELSE 0 END)       AS rc_null,
       sum(CASE WHEN review_count IS NULL THEN 1 ELSE 0 END)       AS rvc_null,
       sum(CASE WHEN is_recommended = true THEN 1 ELSE 0 END)      AS rec_true
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info
GROUP BY load_origin, source_name
ORDER BY load_origin, source_name
LIMIT 50;
```

Chỉ ghi lại, không chặn. Số này dùng để so sánh trước và sau RUN.

**B3. Không có `poi_id` trùng trước khi chạy.** Kỳ vọng 0 dòng. Nếu có dòng, chỉ ghi số dòng, không dán `poi_id`.

```sql
SELECT count(*) AS dup_poi_id_n FROM (
  SELECT poi_id
  FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info
  GROUP BY poi_id HAVING count(*) > 1
);
```

**B4. Trạng thái khoá luồng:**

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M';
```

Trước RUN, `lock_exec_id` phải NULL hoặc khoá đã quá hạn. Nếu không, chờ pipeline chạy xong. Không tự xoá khoá.

**B5. Watermark cạnh của info.** Chỉ để ghi nhận: chạy trước Bước 3 và chạy lại sau Bước 3.

```sql
SELECT watermark_id, status, last_src_version, last_success_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm_e__gld_srv_poi_info__%'
ORDER BY watermark_id
LIMIT 50;
```

## Các bước thực hiện

**Bước 1: PLAN** (không ghi)

- `p_mode = "PLAN"`
- `p_pin_json = {"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}`
- Chạy toàn bộ notebook rồi dán dòng JSON `summary`. Có thể bỏ các stage khác, nhưng phải giữ `exec_id`, `mode`, `pins`, toàn bộ `map` và toàn bộ `info`.
- Kiểm tra `summary.pins` giống hệt pin ở trên.
- Nếu notebook raise (summary có `failed_stage`), dừng lại, dán summary và không chạy RUN.
- PLAN đạt khi tất cả các điều kiện sau đúng:
  - `map.drift_n = 0`
  - `info.detail_conflict_n = 0`
  - `info.rating_cast_fail_n = 0`
  - `info.candidates = 45476`
  - Tổng mọi giá trị trong `info.hours_reason` bằng `info.candidates`.
  - Trong `info.hours_reason`, `GOOGLE_BAD_TIME` không có khoá hoặc bằng 0.
  - `info.hours_reason.IS_24_7 >= 6430`
  - `info.hours_reason.OK <= 29988`
  - `info.hours_reason.NO_PERIODS <= 9058`
  - `NO_DETAIL` không có khoá hoặc bằng 0.
- Các số sau chỉ báo cáo, không chặn RUN (D-07 chấp nhận):
  - `29988 - OK`: số dòng có period hợp lệ nhưng `is_24_7 = true`, nay thành case 2.
  - `9058 - NO_PERIODS`: số dòng không có period nhưng `is_24_7 = true`, nay thành case 2.
  - `info.hours_24_7_partner_n`
- Ghi thêm các số sau (không chặn): mọi mã `GOOGLE_*` khác trong `hours_reason`, `info.to_insert`, `info.present_live`, `info.present_deleted`, `info.review_matched_n`, `info.holiday_partner_nonnull_n`, `info.review_count_dup_n`, `info.rating_conflict_n`.
- Nếu có điều kiện đạt nào sai, dừng lại và báo cáo. Không chạy RUN và không tự đặt rule mới.

**Bước 2: DỪNG chờ Main xác nhận PLAN** (`waiting_runtime`)

- Dán summary PLAN vào mục cuối. Main đối chiếu với các điều kiện ở Bước 1. Chỉ chạy Bước 3 khi Main hoặc người dùng xác nhận PLAN đạt.

**Bước 3: RUN** (bước ghi duy nhất của runbook)

- Ngay trước RUN, chạy lại B4 (khoá phải trống) và B5.
- `p_mode = "RUN"`
- `p_pin_json = {"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}`
- Chạy toàn bộ notebook, rồi dán `summary`:
  - `exec_id`, `pins`, `map`;
  - `info`, gồm `v_pre`, `v_post`, `inserted`, `commit` và `hours_reason`;
  - các khoá `inserted` và `commit` của `multi_lang`, `review`, `media`, `amenity`.
- Điều kiện đạt: `summary.info.commit = "COMMITTED"`.
- Ghi `info.inserted` và so với `info.to_insert` của PLAN. Nếu khác (ví dụ pipeline đã chèn `poi_id` giữa PLAN và RUN), ghi cả hai số và dừng để Main xem. Không tự chạy lại.
- Ghi `summary.info.v_pre` và `summary.info.v_post` để dùng ở các bước kiểm tra.
- Nếu summary có `failed_stage` hoặc `unlock_error`, dán summary và dừng.

## Kiểm tra kết quả

Thay `<v_pre>` và `<v_post>` bằng `summary.info.v_pre` và `summary.info.v_post` của Bước 3. Mọi truy vấn chỉ đọc. Các số `NO_PERIODS`, `NO_DETAIL`, `GOOGLE_*` lấy từ `summary.info.hours_reason` của Bước 3 RUN, phải giống PLAN Bước 1.

**K1. Không có `poi_id` trùng.** Điều kiện đạt: `dup_poi_id_n = 0`.

```sql
SELECT count(*) AS dup_poi_id_n FROM (
  SELECT poi_id
  FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_post>
  GROUP BY poi_id HAVING count(*) > 1
);
```

**K2. Dòng pipeline không đổi (I1).** Điều kiện đạt: cả hai số đều bằng 0.

```sql
SELECT count(*) AS diff_pre_minus_post FROM (
  SELECT * FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_pre>  WHERE load_origin IS NULL
  EXCEPT ALL
  SELECT * FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_post> WHERE load_origin IS NULL
);

SELECT count(*) AS diff_post_minus_pre FROM (
  SELECT * FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_post> WHERE load_origin IS NULL
  EXCEPT ALL
  SELECT * FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_pre>  WHERE load_origin IS NULL
);
```

**K3. Giờ mở cửa và ngày lễ trên dòng legacy.** Chỉ có số đếm, không đọc text giờ.

```sql
SELECT source_name, count(*) AS n,
       sum(CASE WHEN operating_hours IS NULL THEN 1 ELSE 0 END) AS oh_null,
       sum(CASE WHEN operating_hours LIKE '%"is_open_all_day":true%' THEN 1 ELSE 0 END) AS all_day_n,
       sum(CASE WHEN operating_hours LIKE '%"is_open_all_day":true%'
                 AND (operating_hours LIKE '%"open_time"%'
                      OR operating_hours LIKE '%"close_time"%'
                      OR operating_hours LIKE '%"value"%') THEN 1 ELSE 0 END) AS all_day_bad_n,
       sum(CASE WHEN holiday_exceptions IS NULL THEN 1 ELSE 0 END) AS he_null,
       sum(CASE WHEN holiday_exceptions IS NOT NULL THEN 1 ELSE 0 END) AS he_nonnull
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_post>
WHERE load_origin = 'LEGACY_INIT'
GROUP BY source_name
ORDER BY source_name
LIMIT 50;
```

Điều kiện đạt:

- Với `google`: `oh_null < 25917` và `oh_null <= NO_PERIODS + NO_DETAIL + tổng mọi mã GOOGLE_*` (trong đó `NO_DETAIL` và các mã vắng mặt tính là 0).
- Với `google`: `all_day_n > 0`.
- `all_day_bad_n = 0` ở mọi `source_name`.
- Với `google`: `he_nonnull = 0`, tức `holiday_exceptions` NULL ở mọi dòng.

Ghi thêm để Main đối chiếu (không chặn):

- `all_day_n` của google cộng partner, so với `IS_24_7`. Ứng viên trùng `poi_id` với dòng pipeline (`present_live`) không được cập nhật, nên có thể nhỏ hơn.
- `all_day_n` của partner, so với `hours_24_7_partner_n`.
- `he_nonnull` của partner, so với `holiday_partner_nonnull_n`.

**K4. Rating, review và is_recommended trên dòng legacy:**

```sql
SELECT source_name, count(*) AS n,
       sum(CASE WHEN rating_count IS NOT NULL THEN 1 ELSE 0 END) AS rc_nonnull,
       sum(CASE WHEN review_count IS NOT NULL THEN 1 ELSE 0 END) AS rvc_nonnull,
       sum(CASE WHEN is_recommended = true THEN 1 ELSE 0 END)    AS rec_true,
       sum(CASE WHEN is_recommended = false THEN 1 ELSE 0 END)   AS rec_false,
       sum(CASE WHEN is_recommended IS NULL THEN 1 ELSE 0 END)   AS rec_null
FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_post>
WHERE load_origin = 'LEGACY_INIT'
GROUP BY source_name
ORDER BY source_name
LIMIT 50;
```

Điều kiện đạt:

- `partner`: `rc_nonnull = 0` và `rvc_nonnull = 0`.
- `partner`: `rec_true = n`. Mọi nguồn khác: `rec_true = 0`.
- Ghi thêm `rvc_nonnull` của `google` để so với `summary.info.review_matched_n` (không chặn).

## Chạy lại để kiểm tra idempotency

Cả hai lần chạy lại đều dùng đúng pin `{"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}`.

**I1. PLAN lần 2** (bắt buộc, không ghi)

- `p_mode = "PLAN"`
- `p_pin_json = {"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}`
- Điều kiện đạt:
  - `map.drift_n = 0`, `info.rating_cast_fail_n = 0`, `info.detail_conflict_n = 0`.
  - `info.to_insert = 0`.
  - `info.candidates`, `info.hours_reason`, `info.hours_24_7_partner_n`, `info.review_matched_n`, `info.holiday_partner_nonnull_n`, `info.review_count_dup_n`, `info.rating_conflict_n` giống hệt PLAN Bước 1.

**I2. RUN lần 2** (chỉ chạy khi người dùng đồng ý; ghi rõ có chạy hay không)

- Chạy B4 trước.
- `p_mode = "RUN"`
- `p_pin_json = {"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}`
- Điều kiện đạt: `summary.info.commit = "COMMITTED"` và `summary.info.inserted = 0`. Gọi `v_pre` và `v_post` của lần này là `<v_pre2>` và `<v_post2>`.
- Lặp lại K1 và K2 với `<v_pre2>` và `<v_post2>`. Kết quả phải là 0 ở mọi số.
- Giá trị dòng legacy không đổi giữa hai lần RUN. Lần chạy lại chỉ dời `updated_at`. Hai truy vấn sau phải trả về 0:

```sql
SELECT count(*) AS diff_run1_minus_run2 FROM (
  SELECT poi_id, row_hash FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_post>  WHERE load_origin = 'LEGACY_INIT'
  EXCEPT ALL
  SELECT poi_id, row_hash FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_post2> WHERE load_origin = 'LEGACY_INIT'
);

SELECT count(*) AS diff_run2_minus_run1 FROM (
  SELECT poi_id, row_hash FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_post2> WHERE load_origin = 'LEGACY_INIT'
  EXCEPT ALL
  SELECT poi_id, row_hash FROM sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_post>  WHERE load_origin = 'LEGACY_INIT'
);
```

## Kiểm tra log và watermark

- **Log của notebook.** Notebook không ghi `ctrl_log_run` hay `ctrl_log_table_run`. Bằng chứng của mỗi lần chạy là JSON `summary` (in bằng `print` và trả về qua `notebookutils.notebook.exit`) và lịch sử Delta có tag `LEGACY_INIT:<exec_id>`.
- **Commit trên bảng info.** Chỉ dán các cột `version`, `timestamp`, `operation`, `userMetadata`.

```sql
DESCRIBE HISTORY sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info LIMIT 20;
```

  Điều kiện đạt: có đúng một commit `MERGE` với `userMetadata = LEGACY_INIT:<summary.exec_id của Bước 3>`, và version của commit đó bằng `summary.info.v_post`. Nếu có I2, kiểm tra tương tự với `exec_id` và `v_post2` của lần đó. Ghi lại mọi commit có version lớn hơn `v_post` (cần cho phần Rollback).
- **Khoá luồng sau RUN.** Chạy lại B4. Điều kiện đạt: `lock_exec_id` là NULL hoặc khác `exec_id` của lần chạy, và `status = SUCCESS`.
  - Nếu khoá vẫn giữ `exec_id` của notebook, hoặc summary có `unlock_error`, dán `unlock_error` và dừng.
  - Không UPDATE bảng ctrl khi chưa có quyết định của người dùng.
- **Watermark cạnh.** Chạy lại B5 sau Bước 3. Notebook không ghi các dòng `wm_e__*` hay `wm_transform_*`. Mọi thay đổi giữa hai lần B5 chỉ có thể đến từ pipeline 30 phút. Ghi lại thay đổi nếu có.

## Rollback và forward recovery

- **Lỗi trước MERGE info.** Đó là các guard `rating_cast_fail_n`, `over_int`, số dòng `info_src` thay đổi, `drift_n` khi RUN, hoặc khoá trùng payload. Khi đó info chưa bị ghi và summary có `failed_stage`. Báo Main, sửa nguyên nhân, rồi chạy lại cùng notebook với cùng pin.
- **Lỗi sau commit info.** Info đã đúng. Chạy lại an toàn theo quy tắc idempotency, với cùng pin.
- **Forward recovery (ưu tiên).** Revert thay đổi notebook trong git, đồng bộ lên Fabric DEV, rồi chạy lại RUN:
  - `p_mode = "RUN"`
  - `p_pin_json = {"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}`

  MERGE chỉ cập nhật dòng `load_origin = 'LEGACY_INIT'` về biểu thức cũ và không chạm dòng pipeline. Sau đó chạy lại K1 và K2 với `v_pre` và `v_post` của lần chạy này.
- **RESTORE.** Chỉ được dùng khi `DESCRIBE HISTORY` cho thấy không có commit nào sau commit init. Nếu có, RESTORE sẽ cuộn lùi cả commit của pipeline. Đây là thao tác ghi khó đảo ngược, nên người dùng phải xác nhận trước khi chạy:

```sql
-- Chỉ chạy sau khi người dùng xác nhận và DESCRIBE HISTORY không có commit nào sau <v_post>
RESTORE TABLE sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info TO VERSION AS OF <v_pre>;
```

  `<v_pre>` là `summary.info.v_pre` của lần RUN cần hoàn tác. RESTORE chỉ áp dụng cho bảng info. Các bảng khác được RUN ghi lại với cùng giá trị nên không cần hoàn tác.

## Kết quả người dùng ghi nhận

Chỉ điền số đếm và mã. Không dán tên POI, dữ liệu cá nhân, `poi_id` cụ thể hay text giờ mở cửa. Mỗi kết quả tối đa 50 dòng.

- Test local (`pytest`), gồm `test_legacy_hours_is_24_7` và `test_init_is_24_7_path`: `python scripts/vv.py verify` 2026-11-25 10:13, pytest 411 passed
- Bản notebook đã đồng bộ lên Fabric DEV: `<commit hoặc xác nhận>`
- Pin dùng cho mọi bước (phải là `{"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}`): RUN `summary.pins` khớp pin này
- B1 `v_baseline`: `<…>` | B2: `<dán bảng>` | B3 `dup_poi_id_n`: `<…>` | B4 trước RUN: `<status, lock_exec_id có NULL không>` | B5 trước RUN: `<dán bảng>`
- Bước 1 PLAN, `exec_id`: `lgp-acfe492d29374536abd9e56f0fcc8838`
  - `map.drift_n`: 0 | `detail_conflict_n`: 0 | `rating_cast_fail_n`: 0 | `candidates`: 45476
  - `hours_reason`: `NO_PERIODS` 9056, `IS_24_7` 6442, `OK` 29978 | tổng = `candidates`? có
  - `GOOGLE_BAD_TIME`: vắng | `IS_24_7`: 6442 | `OK`: 29978 | `NO_PERIODS`: 9056 | `NO_DETAIL`: vắng
  - Báo cáo, không chặn: `29988 - OK` = 10 | `9058 - NO_PERIODS` = 2 | `hours_24_7_partner_n` = 0
  - `to_insert`: 0 | `present_live`: 45476 | `present_deleted`: 0 | `review_matched_n`: 40197 | `holiday_partner_nonnull_n`: 125 | `review_count_dup_n`: 0 | `rating_conflict_n`: 0
  - PLAN đạt? có
- Bước 2, xác nhận của Main hoặc người dùng trước RUN: người dùng chấp nhận 20 dòng `cmp_conflict` ngày 2026-11-25
- Bước 3 RUN, `exec_id`: `lgp-0141b690fb824d51a542a63c11d8ce47` | `info.commit`: `COMMITTED` | `info.inserted`: 0 (so với `to_insert` của PLAN: 0) | `v_pre`: 21 | `v_post`: 22 | `hours_reason`: `NO_PERIODS` 9056, `IS_24_7` 6442, `OK` 29978 | `inserted`/`commit` của các stage khác: review 0/`COMMITTED`, map 0/`NOT_COMMITTED`, multi_lang 0/`COMMITTED`, media 209/`COMMITTED`, amenity 0/`COMMITTED`
- K1 `dup_poi_id_n`: 0
- K2: `diff_pre_minus_post` = 0 | `diff_post_minus_pre` = 0
- K3: google `n` 25917, `oh_null` 6847, `all_day_n` 4953, `all_day_bad_n` 0, `he_null` 25917, `he_nonnull` 0. partner `n` 4, `oh_null` 3, `all_day_n` 0, `all_day_bad_n` 0, `he_null` 0, `he_nonnull` 4
  - google `oh_null < 25917`? có | google `oh_null <= NO_PERIODS + NO_DETAIL + GOOGLE_*` (= 9056)? có, 6847
  - google `all_day_n > 0`? có | `all_day_bad_n = 0` ở mọi nguồn? có | google `he_nonnull = 0`? có
  - Đối chiếu (không chặn): `all_day_n` google + partner 4953 so với `IS_24_7` 6442, lệch 1489 | partner `all_day_n` 0 so với `hours_24_7_partner_n` 0 | partner `he_nonnull` 4 so với `holiday_partner_nonnull_n` 125
- K4: google `n` 25917, `rc_nonnull` 25917, `rvc_nonnull` 25676, `rec_true` 0, `rec_false` 25917, `rec_null` 0. partner `n` 4, `rc_nonnull` 0, `rvc_nonnull` 0, `rec_true` 4, `rec_false` 0, `rec_null` 0 | partner `rc_nonnull = 0` và `rvc_nonnull = 0`? có | `rec_true` đúng bằng `n` của partner và bằng 0 ở nguồn khác? có | google `rvc_nonnull` 25676 so với `review_matched_n` 40197
- I1 PLAN lần 2: `exec_id` `lgp-d31c5e89aa0541f1906e856aa2f38bd9` | `to_insert = 0`? có | các khoá giống Bước 1? có. `drift_n` 0, `detail_conflict_n` 0, `rating_cast_fail_n` 0, `candidates` 45476, `hours_reason` `NO_PERIODS` 9056 / `IS_24_7` 6442 / `OK` 29978, `hours_24_7_partner_n` 0, `review_matched_n` 40197, `holiday_partner_nonnull_n` 125, `review_count_dup_n` 0, `rating_conflict_n` 0
- I2 RUN lần 2: đã chạy, `exec_id` `lgp-ecaceebb45fc480a97d480f834427086` | `info.commit` `COMMITTED`, `info.inserted` 0 | `v_pre` 22, `v_post` 23 | K1 `dup_poi_id_n` 0 | K2 cả hai chiều 0 | `diff_run1_minus_run2` 0 | `diff_run2_minus_run1` 0 | media `inserted` 0, `commit` `COMMITTED`, version 9 đến 10
- DESCRIBE HISTORY info, commit `LEGACY_INIT:<exec_id>`: version 23, `MERGE`, `userMetadata` `LEGACY_INIT:lgp-ecaceebb45fc480a97d480f834427086`, `numTargetRowsInserted` 0, `numTargetRowsUpdated` 25921 | các commit có version lớn hơn 23: không. Version 22 vẫn là `LEGACY_INIT:lgp-0141b690fb824d51a542a63c11d8ce47`
- Khoá luồng sau RUN lần 2 (B4): `SUCCESS`, `lock_exec_id` null, `last_run_id` `lgp-ecaceebb45fc480a97d480f834427086` | `unlock_error`: không có | B5 sau RUN, thay đổi so với trước: chưa dán, không chặn idempotency
- Ghi chú hoặc sai lệch: K1–K4 và khoá đạt. Lệch không chặn nằm ở dòng `load_origin` null, vì MERGE chỉ cập nhật `LEGACY_INIT`. Lần `lgp-5664cec5fc404dd7950f7b9027c62ec8` trả `mode` `PLAN`, không phải RUN lần 2.
