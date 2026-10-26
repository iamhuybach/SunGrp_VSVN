# Hướng dẫn kiểm chứng runtime

Trạng thái: người dùng đã chạy tay trên Fabric DEV. Gate `runtime` trong task vẫn `not_required`.

## Phạm vi và môi trường

## Điều kiện tiên quyết

## Baseline trước khi chạy

## Các bước thực hiện

## Kiểm tra kết quả

## Chạy lại để kiểm tra idempotency

## Kiểm tra log và watermark

## Rollback và forward recovery

## Kết quả người dùng ghi nhận

Người dùng gửi log ngày 2026-10-26. `NB_GLD_SRV_POI_INFO`, chạy tay, `pl PL_VV_TRANS_SLV_TO_GLD_30M`, mode `RUN`, `p_force`, exec `2af3fdac-420e-4825-82e9-7c4d4142d694`.

- New Edge rỗng, có `p_force`.
- Diff: insert 0, update 24, xoá mềm 0, nguồn 24 dòng.
- Kết thúc `SUCCESS` (142s). `trg_version` 5.

ExitValue: `{"deactivated": 0, "inserted": 0, "node": "lh_vv_gold.dbo.gld_srv_poi_info", "status": "SUCCESS", "trg_version": 5, "updated": 24}`

