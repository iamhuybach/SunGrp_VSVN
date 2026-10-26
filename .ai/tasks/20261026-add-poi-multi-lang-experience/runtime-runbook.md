# Hướng dẫn kiểm chứng runtime

Trạng thái: người dùng đã chấp nhận kết quả DEV. Gate `runtime` chưa `PASS`.

## Phạm vi và môi trường

- Workspace Fabric DEV.
- Lakehouse `lh_vv_silver`, `lh_vv_gold`, `lh_vv_ctrl`.
- Notebook `NB_CREATE_DDL` cell `mlexppy`, notebook `NB_SETUP_INITIAL_DDL`, notebook `NB_GLD_SRV_POI_MULTI_LANG`.
- Pipeline `PL_VV_TRANS_SLV_TO_GLD_30M`.
- Chỉ thêm cột `experience` STRING, nullable, sau `description` trên `slv_enr_poi_info_multi_lang` và `gld_srv_poi_multi_lang`.

## Điều kiện tiên quyết

- Cell `plcadpy` đã chạy xong. Khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` đã có.
- Chưa publish bản `NB_GLD_SRV_POI_MULTI_LANG` mới trước khi `mlexppy` chạy xong. Build mới gọi `_require` cột `experience`; bảng chưa có cột thì node dừng, không ghi.
- `usps` là cột `string` trên `lh_vv_silver.dbo.slv_pn_business_service_i18ns`.

## Baseline trước khi chạy

1. R0. Chạy:

```sql
SELECT watermark_id, lock_exec_id
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M'
```

Kỳ vọng: đúng 1 dòng, `lock_exec_id` null. Sai thì dừng, chưa chạy `mlexppy`.

2. P1. `DESCRIBE lh_vv_silver.dbo.slv_pn_business_service_i18ns`. Kỳ vọng có `usps` kiểu `string`. Không có hoặc kiểu khác thì dừng và báo Main.

## Các bước thực hiện

1. R1. Trong `NB_CREATE_DDL`, chạy riêng cell `mlexppy`. Không chạy các cell cũ.
2. R2. `DESCRIBE lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` và `DESCRIBE lh_vv_gold.dbo.gld_srv_poi_multi_lang`.
3. R3. Chạy `NB_SETUP_INITIAL_DDL` với `p_apply` = `false`.
4. R4. Sau R1 thành công, publish `NB_GLD_SRV_POI_MULTI_LANG`, rồi chạy một lần pipeline `PL_VV_TRANS_SLV_TO_GLD_30M`.
5. R5. Trong một notebook Spark đã `%run NB_LIB_TRANSFORM_SLV_GLD`, chạy khối kiểm tra ở mục Kiểm tra kết quả.
6. R6. Đối chiếu log với số `nonnull` của R5.

## Kiểm tra kết quả

- R1 lần đầu in `experience: +[...]` gồm đủ hai bảng `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` và `lh_vv_gold.dbo.gld_srv_poi_multi_lang`.
- R2: cột `experience` kiểu `string`, đứng ngay sau `description` trên cả hai bảng.
- R3: trạng thái `PLAN`, không báo lệch schema.
- R4: node `gld_srv_poi_multi_lang` thành công.
- R5: in `mismatch 0`.

```python
%run NB_LIB_TRANSFORM_SLV_GLD
g = spark.table("lh_vv_gold.dbo.gld_srv_poi_multi_lang").where("deleted_at IS NULL")
ml = spark.table("lh_vv_silver.dbo.slv_enr_poi_info_multi_lang").select("poi_id", "lang", F.col("experience").alias("ml_exp"))
pn = spark.table("lh_vv_silver.dbo.slv_pn_business_service_i18ns").select(
    uuid_md5(F.col("business_service_id"), F.lit("partner")).alias("poi_id"), F.col("locale").alias("lang"), "usps")
j = g.join(ml, ["poi_id", "lang"], "left").join(pn, ["poi_id", "lang"], "left")
partner = F.coalesce(F.lower(F.trim(F.col("source_name"))) == "partner", F.lit(False))
want = F.when(partner, F.coalesce(F.col("usps"), F.col("ml_exp"))).otherwise(F.col("ml_exp"))
print("mismatch", j.where(~F.col("experience").eqNullSafe(want)).count())
print("nonnull", g.where(F.col("experience").isNotNull()).count())
j.groupBy(partner.alias("partner"), F.col("usps").isNotNull().alias("usps"), F.col("ml_exp").isNotNull().alias("ml")).count().show()
```

- R6: `updated` của `ctrl_log_table_run` cho lần R4 xấp xỉ `nonnull`. Nguồn không đổi thì `inserted` = 0. Không có PK trùng:

```sql
SELECT poi_id, lang, count(*) AS n
FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang
GROUP BY poi_id, lang
HAVING count(*) > 1
```

Kỳ vọng: 0 dòng.

Dán output đã làm sạch vào mục `Kết quả người dùng ghi nhận`. Tối đa 50 dòng. Không dữ liệu cá nhân, không secret.

## Chạy lại để kiểm tra idempotency

Chạy lại đúng cell `mlexppy`. Kỳ vọng in `experience: +[]`. Schema không đổi. Chạy lại `NB_SETUP_INITIAL_DDL` với `p_apply` = `false` vẫn ra `PLAN`.

## Kiểm tra log và watermark

- Sau `mlexppy`, dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` có `lock_exec_id` null và `status` = `SUCCESS`.
- R6 dùng `updated` và `inserted` của `ctrl_log_table_run` cho lần chạy R4.

## Rollback và forward recovery

- Ưu tiên sửa build rồi chạy lại pipeline.
- Không `DROP` cột `experience`. Cột nullable, để lại không làm hỏng dòng cũ.
- Rollback code: revert `srvmlbuild`. Lib cảnh báo cột đích thừa và MERGE không ghi `experience`; giá trị lần chạy trước giữ nguyên. Muốn xoá giá trị thì người dùng tự chạy, sau khi xác nhận, trong lúc giữ khoá GLD-30M: `UPDATE lh_vv_gold.dbo.gld_srv_poi_multi_lang SET experience = NULL`. Lệnh này không nằm trong cell.
- Nếu lib đã thêm `experience` sai vị trí (sau `deleted_at`): dừng. Phục hồi cần bước tay được ghi vào `decision.md` trước khi làm.

## Kết quả người dùng ghi nhận

- 2026-10-26, Fabric DEV, chưa pass.
- R0: 1 dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`, `lock_exec_id` null.
- P1: `usps` kiểu `string`.
- R1 lần đầu: `experience: +['lh_vv_silver.dbo.slv_enr_poi_info_multi_lang', 'lh_vv_gold.dbo.gld_srv_poi_multi_lang']`. Chưa có dòng chạy lại `+[]` trong bản dán này.
- R2: cả hai `DESCRIBE` có `experience,string` ngay sau `description`.
- R3 lần hai: `status` `PLAN`, 21 bảng `EXISTS_OK`, seed `to_insert` = 0.
- R1 chạy lại: `experience: +[]`.
- R4: `PL_VV_TRANS_SLV_TO_GLD_30M` mode `RUN` kết thúc `PARTIAL_FAILED`. Node `gld_srv_poi_multi_lang` lỗi `QualityGateError: Đầu vào bắt buộc rỗng: ['lh_vv_silver.dbo.slv_enr_poi_info_multi_lang']`.
- R5: `usps` `string`; `experience` đứng sau `description`; `lock_exec_id` null; `status` `PARTIAL_FAILED`; `mismatch` 0; `nonnull` 0; `duplicate_pk` 0; `groupBy` không có dòng.
- 2026-10-26: người dùng chấp nhận lần RUN. Gate rỗng là hành vi hiện có. Runtime chưa pass.

