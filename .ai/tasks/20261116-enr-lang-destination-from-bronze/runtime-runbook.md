# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`. Chưa có bước Fabric hay docker nào được chạy trong task này.

## Phạm vi và môi trường

Fabric DEV, workspace của `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_gold`, `lh_vv_ctrl`. PostgreSQL schema `apps`. API `services/data-serving-service`.

Đổi schema tại chỗ, không DROP, không column mapping. Silver `slv_enr_poi_info_multi_lang` đang có 3 dòng (probe P-1) phải còn sau rewrite.

## Điều kiện tiên quyết

- Notebook mới và notebook đã sửa đã được đưa lên Fabric DEV (bước B1).
- Không có run FL_00, NB_00, hay Copy Job đang ghi các bảng trong mục khoá.
- Người dùng đã trả lời R-0 trước B5.

## Baseline trước khi chạy

R-0 đã ghi ngày 2026-11-17:

- Copy Job gold → `apps.srv_poi_*` chạy 15 phút một lần. Mode ghi của `apps.srv_poi_multi_lang` là merge.
- Copy Job tạm dừng được. B5 dừng job trước `enrgldpy` và chỉ mở lại sau khi các bước B5 thành công.
- `COUNT(*)`: `slv_enr_poi_info_multi_lang` = 3, `slv_enr_poi_destination` = 0, `gld_srv_poi_multi_lang` = 859, `apps.srv_poi_multi_lang` = 859.
- `COUNT(cost_vnd)` trước khi đổi tên: gold = 3, PostgreSQL = 3.

## Các bước thực hiện

Dừng nếu một rewrite không in `REWRITTEN` hoặc `SKIP`, nếu `cast_null > 0`, hoặc nếu `other > 0`.

1. B1. Đưa các notebook đã sửa lên Fabric DEV. Chưa chạy cell ghi.
2. B2. Trong `NB_CREATE_DDL`, tìm markdown `# B2 — cell enrbrzpy` và chạy cell code ngay bên dưới. Cell khoá `wm_transform_brz_enrichment_result`, `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M`, `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`, rồi rewrite hai bảng silver. Nếu lỗi `wm_transform_brz_enrichment_result đang bị giữ` và câu kiểm tra bên dưới trả 0 dòng, chạy B3 trước rồi chạy lại B2. Dòng watermark này do B3 tạo. Cell báo cùng câu đó khi dòng chưa có.
3. B3. Tìm markdown `# B3 — cell enrbrzcfgpy` (nằm phía trên B2) và chạy cell code ngay bên dưới. Trước đó, trong cùng session, chạy hai cell ở đầu `NB_CREATE_DDL`: cell code bắt đầu bằng `TABLE_CONFIGS = [` rồi cell code bắt đầu bằng `# Seed ctrl_cfg_schema_registry (v2) từ TABLE_CONFIGS`. Cell thứ hai tạo `seed_registry` và seed lại nguồn partner bằng replaceWhere. Thiếu bước này thì B3 lỗi `name 'seed_registry' is not defined`. Seed registry enrichment, hai dòng pipeline `DOC`, và watermark `wm_transform_brz_enrichment_result`.
4. B4. Mở `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV`. Tiêu đề markdown là `# NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV`. Cell tham số là cell code ngay dưới tiêu đề. Đặt `dry_run = True`, chạy cả notebook. Khi `cast_null = 0` và `other = 0`, đặt `dry_run = False` rồi chạy lại.
5. B5 chỉ chạy khi Copy Job đang dừng và không còn lần chạy nào. Thứ tự bắt buộc, không đổi:
   1. Dừng Copy Job.
   2. Xác nhận không còn run đang ghi `gld_srv_poi_multi_lang` hoặc `apps.srv_poi_multi_lang`.
   3. Trong `NB_CREATE_DDL`, tìm markdown `# B5 — cell enrgldpy` và chạy cell code ngay bên dưới. Dừng nếu không in `REWRITTEN` hoặc `SKIP`.
   4. `ALTER TABLE apps.srv_poi_multi_lang RENAME COLUMN cost_vnd TO cost` với `lock_timeout`. Dừng nếu ALTER lỗi.
   5. Deploy API và restart. Dừng nếu API không lên.
   6. Chạy NB_00 cho `gld_srv_poi_info` và `gld_srv_poi_multi_lang`, rồi kiểm tra đọc.
   7. Mở lại Copy Job chỉ sau khi các bước trên thành công.

Một bước B5 lỗi thì không mở lại Copy Job. Sửa lỗi hoặc rollback, rồi mới resume. Không có nhánh mở job sau bước lỗi.

## Kiểm tra kết quả

- Silver multi_lang còn đủ số dòng baseline. Cột `cost` có, `cost_vnd` không còn. Destination không còn `street`, có `source_name` và `formatted_address`.
- `country_code` và `postal_code` toàn NULL.
- Gold multi_lang: `COUNT(*)` bằng baseline, cột `cost`, không còn `cost_vnd`.
- PostgreSQL: cột `cost`, `COUNT(*)` và `COUNT(cost)` khớp gold sau Copy Job kế tiếp.
- API `practical_info` đọc `cost`. Object `{text, label}` trả `{label, value}`.

## Chạy lại để kiểm tra idempotency

Chạy lại `enrbrzpy` và `enrgldpy`. Lần hai in `SKIP` cho bảng đã đúng schema. Chạy lại extract: MERGE không đổi dòng khi bộ version không lớn hơn.

## Kiểm tra log và watermark

- `ctrl_log_run` và `ctrl_log_table_run` của `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV`, `src_tbl = brz_enrichment_result`.
- `wm_transform_brz_enrichment_result` tiến `last_src_version` chỉ khi cả hai bảng SUCCESS hoặc NO_DATA. Khoá được nhả.
- Reject: `SELECT trg_tbl, reject_reason, COUNT(*) FROM lh_vv_ctrl.dbo.ctrl_cdc_reject WHERE src_tbl = 'brz_enrichment_result' AND NOT is_resolved GROUP BY 1, 2`.

## Rollback và forward recovery

Rewrite lỗi và HEAD vẫn là commit của attempt thì cell `RESTORE` về `v0`. Có commit sau attempt thì cell in `không RESTORE` và dừng để phục hồi thủ công. Không mở lại Copy Job khi B5 đang lỗi.

Đảo gold khi cần đưa về tên cũ, cùng planner với rename `{"cost_vnd": "cost"}`, rồi:

```sql
ALTER TABLE apps.srv_poi_multi_lang RENAME COLUMN cost TO cost_vnd;
```

Sau đó deploy lại API bản cũ. Không DROP bảng.

## Kết quả người dùng ghi nhận

| Bước | Kết quả | exec_id hoặc version | Ghi chú |
|---|---|---|---|
| R-0 | PASS | | 15 phút/lần, mode merge. slv multi_lang 3, destination 0, gold 859, PostgreSQL 859. `COUNT(cost_vnd)` gold 3, PostgreSQL 3 |
| B3 | PASS | | `Seed 31 cột / 2 bảng`. `enrbrzcfgpy 2 wm_transform_brz_enrichment_result`. |
| B2 | PASS | v0 multi_lang 8, destination 4 | `NOT NULL giữ nullable` cho `poi_id` cả hai bảng. `REWRITTEN` multi_lang rows 3, destination rows 0. |
| B4 | PASS | 00fde3e6-4aab-4fa5-a7e0-c56948d2d232 | Dry run `457a8180-099e-470a-a9cb-e115bbf52ffd` SUCCESS, cast_null 0. Lần thật INCREMENTAL SUCCESS, read 473, inserted 473, updated 0, cast_null 0. destination ins 113, multi_lang ins 360. src_version 3. |
| B5 | PASS | 7d25219d-b6e7-453f-92a6-d12e2aa98b29 | NB_00 SUCCESS. Gold và PostgreSQL `srv_poi_multi_lang` cùng n=872, cost_n=363. |
