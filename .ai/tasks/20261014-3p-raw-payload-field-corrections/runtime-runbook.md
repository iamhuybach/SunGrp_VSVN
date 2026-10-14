# Hướng dẫn kiểm chứng runtime

Trạng thái: DEV đã kiểm chứng ngày 2026-10-14. P11 pass. Prod chưa chạy. Giữ gold tắt cho đến khi người dùng bật lại.

## Phạm vi và môi trường

Fabric DEV. Nguồn `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`.
Đích là chín bảng `lh_vv_silver.dbo.slv_3p_*`. Deploy đúng thứ tự:
`NB_LIB_EXTRACT_RAWDATA`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`,
`NB_CREATE_DDL`. Không đổi partner hoặc gold. Giữ
`PL_VV_TRANS_SLV_TO_ENR_15P` tắt.

## Điều kiện tiên quyết

- Người dùng cho tiếp tục task sau khi rút `is_visible`.
- P9 pass trước deploy. Không deploy khi một gate count khác 0.
- Có quyền chạy Spark notebook và SQL read-only/DDL trên DEV.

## Baseline trước khi chạy

Chạy một incremental bằng code cũ để silver hiện hành. Ghi Delta version và
row count của chín bảng; watermark 3P; số state theo target; tổng reject 3P.
Không ghi payload hoặc URL.

## Các bước thực hiện

1. Chạy `.ai/tasks/20261014-3p-raw-payload-field-corrections/evidence/probes/P9_payload_parity.sql`.
   Lưu kết quả tại `evidence/results/P9_payload_parity.md`.
2. Có thể tạm dừng trigger 3P. Deploy ba notebook theo thứ tự ở trên.
3. Trong `NB_CREATE_DDL`, chỉ chạy helper/`TABLE_CONFIGS_3P`/seed 3P.
   Không seed partner. `show_registry` phải cho 9 bảng, 55 cột, 0 cột tắt,
   11 `convert_arg` khác null, 0 `json_path` null. Không có cột `is_visible`.
4. Partner: `dry_run = True`; không được có `ConfigError`.
5. 3P: `dry_run = True`, `full_reload = True`, `allow_full_scan = True`.
   `rule self-check` pass; `cast_null` và `bad_shape` rỗng;
   review `docs_by_table` bằng số VALID.
6. Backfill cả chín bảng: `full_reload = True`, `allow_full_scan = True`,
   `max_retries = 1`; `table_filter` gồm đủ chín bảng.
7. Chạy lại cùng backfill, rồi chạy một incremental bình thường.

## Kiểm tra kết quả

- P9 pass khi `norm_blank_when_raw_ok`, `top_mismatch_docs`,
  `photo_size_mismatch_docs`, `photo_elem_mismatch`, `blob_signed` đều 0.
- Hai backfill: chín bảng SUCCESS; khóa unique; không mất khóa baseline.
- Parity trên các cột baseline (trừ `updated_at`) tại cùng stamp: diff = 0.
- Phone oracle so với `$.nationalPhoneNumber`: diff = 0.
- Media oracle so với `$.blob_url` và phần tử đầu
  `$.authorAttributions`: `no_oracle = blob_diff = photographer_diff = 0`.
- Ghi `blob_nonnull`, `photographer_null`, và reject delta.

## Chạy lại để kiểm tra idempotency

Backfill lần hai có `inserted_rows = 0` ở mọi bảng. Incremental kế tiếp là SUCCESS hoặc NO_DATA.

## Kiểm tra log và watermark

Ghi năm run mới nhất từ `ctrl_log_run`, table logs của chín bảng, và watermark
`wm_transform_brz_3rd_crawler_poi_stream`.
Sau run, lock phải rỗng và `last_src_version` không lùi.

## Rollback và forward recovery

Trước deploy: không có rollback. Sau deploy nhưng trước backfill: deploy lại
notebook cũ và seed registry cũ. Sau backfill: giữ gold tắt, khôi phục code/seed
cũ rồi full reload chín bảng từ `raw_payload`; đối chiếu baseline trước khi mở
trigger. Không sửa watermark hoặc silver bằng tay. Lỗi shape review giữ
watermark và chuyển lại evidence.

## Kết quả người dùng ghi nhận

Chỉ dán counts, statuses, versions và `exec_id`. Không dán payload, số điện thoại, tên người hoặc URL.

Baseline 2026-10-14, trước backfill:

- Watermark `wm_transform_brz_3rd_crawler_poi_stream`: `last_src_version = 13`, `watermark_value = 2026-10-09T06:50:58Z`, `lock_exec_id` null.
- `ctrl_cdc_state`: 17 dòng cho mỗi bảng trong chín bảng `slv_3p_*`.
- `unresolved_rejects = 0`.
- Chưa có Delta version và row count của chín bảng silver.

Seed 3P: 55 cột, 9 bảng, 0 cột tắt, cả 9 bảng active. `slv_3p_poi_contact` 4 cột, `slv_3p_poi_media` 8 cột với `photographer:ARRAY_AT`, `slv_3p_poi_review` 7 cột. Không có `is_visible`. Các rule có đối số đếm được 11: 7 `ARRAY_PICK`, 1 `JSON_PICK`, 1 `ARRAY_AT`, 1 `ARRAY_PROJECT`, 1 `ENUM_MAP`.

Partner dry_run `edd337c6-103f-447b-b99b-db6e4e365cbf`: `NO_DATA`, 23 bảng, `error` null, `cast_null = 0`, không có commit mới tại version `19935`.

3P dry_run `e96c3411-9d2b-48d9-8fe3-0c161d0fc2f4`: `SUCCESS`, 9/9 bảng ok, đọc 41, hợp lệ 41, `cast_null = 0`, `bad_shape` rỗng, `docs_by_table` review = 41. `rule self-check PASS`. Log ghi thêm cột `phone`, `blob_url`, `photographer`. `inserted = 0` vì dry_run. `src_version` chốt 22.

Backfill lần một `b6f1f697-7be1-4373-b261-70d82b05e14c`: `SUCCESS`, 9/9 ok, đọc 41, hợp lệ 41, `rejected = 0`, `cast_null = 0`, `bad_shape` rỗng, `del = 0`. Tổng `inserted = 890`, `updated = 12`. Review `ins = 200` `upd = 5`; media `ins = 410` `upd = 0`; bảy bảng còn lại mỗi bảng `ins = 40` `upd = 1`. Watermark chốt version 22, `watermark_to = 2026-10-14 10:38:15.605516`.

Backfill lần hai: người dùng xác nhận `ins = 0`. Chưa có `exec_id`.

Incremental: người dùng xác nhận chạy thành công và cho pass bước này. Chưa có `exec_id`, status, hay `src_version`.

Đối chiếu 2026-10-14:

- Khóa unique: 7 bảng DOC `57/57`, review `285/285`, media `940/940`.
- Phone: `contact_rows = 57`, `phone_diff = 0`.
- Media: `blob_diff = 0`, `photographer_diff = 0`, `blob_nonnull = 205`, `no_oracle = 530`, `photographer_null = 530`. 530 bằng số dòng media có trước 410 insert của backfill.
- Watermark đọc qua SQL endpoint lúc đối chiếu vẫn `last_src_version = 13`. Đọc lại từ Spark: `last_src_version = 22`, `watermark_value = 2026-10-14T10:38:15Z`, `lock_exec_id` null.
- `unresolved = 0`.

`slv_3p_poi` history: version 0 CREATE `2026-10-13T19:09:57Z`; version 1 MERGE `2026-10-13T19:10:29Z`, insert 17; version 2 MERGE `2026-10-14T13:02:43Z`, insert 40, update 1, copied 16, deleted 0, output 57. Baseline parity là version 1.

P11 pass. Chín bảng `baseline_version = 1`, `diffs = 0`, `lost_keys = 0`. Bảy bảng DOC: `joined_keys = 17`, `same_stamp = 16`, `stamp_changed = 1`. Review: `85 / 80 / 5`. Media: `530 / 530 / 0`. Chi tiết tại `evidence/results/P11_stamp_parity.md`.


