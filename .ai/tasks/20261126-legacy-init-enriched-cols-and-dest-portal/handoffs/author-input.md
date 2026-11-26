# Author input — runbook

## User comment

destination_id của phần INIT đã đúng, không cần thay đổi hay chạy lại.

## Write

Vietnamese `runtime-runbook.md` for Fabric DEV workspace `sgr_visitvn_dev`. Sections required by the task skill: Phạm vi và môi trường, Điều kiện tiên quyết, Baseline trước khi chạy, Các bước thực hiện, Kiểm tra kết quả, Chạy lại để kiểm tra idempotency, Kiểm tra log và watermark, Rollback và forward recovery, Kết quả người dùng ghi nhận.

## Order

1. Publish `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` before any run that needs `PATCH_COLS`.
2. Run `NB_CREATE_DDL` cells `28e2be98`, `0f228dc1`, then `enrbrzcfgpy`.
3. Run `destportalpy`. Expect `old_n = 19799`, `empty_n = 2`, and the pre-write gates at 0. Rerun the same cell and expect `updated_n = 0`.
4. Extract dry run, then a real run of `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV`.
5. Run `PL_VV_TRANS_SLV_TO_GLD_30M` so gold `destination_id` copies silver.
6. `NB_SETUP_LEGACY_GOLD_POI`: PLAN, then RUN, then RUN again. Use the original pins plus the printed `ai_enriched_poi` pin. Do not change or rerun the legacy `destination_id` mapping. Stop and ask the user if `destination_changed_n > 0` or `enriched.decision != OK`.

## Lock

`destportalpy` holds `wm_transform_brz_enrichment_result` with `LEASE_MINUTES = 90`. If the cell is cancelled, the runbook must say how to confirm the lock is free or wait 90 minutes, then run the cell again. A rerun after a successful backfill writes 0 rows.

## Read

- `architecture.md` Main brief "Order and stop points" item 4, and sections 16 through 19
- `notebooks/NB_CREATE_DDL.ipynb` cell `destportalpy`
- `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb` cell `lgpparams` (`p_mode`, `p_pin_json`, `p_target_ws`)
- `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb` cell `enr01`
- `decision.md` section `Quyết định hiện hành`, especially `D-DEST-BACKFILL`, `D-LEGACY-DEST`, `D-INIT-KEY`

Do not invent parameter values that are not in those cells. Ask in the runbook text if a value is unknown.
