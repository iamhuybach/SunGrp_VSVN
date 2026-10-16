# Author input

User comment, verbatim:
chuyển waiting_runtime: Main soạn runbook để bạn chạy Fabric DEV theo mục stop 6 trong architecture.md trước khi merge.

Environment: Microsoft Fabric DEV. Silver lakehouse `lh_vv_silver`, control tables `lh_vv_ctrl`. No pipeline JSON exists in the repo. The pipeline is not scheduled.

Read only:
- `.ai/tasks/20261016-ref-amenities-poi-amenity/architecture.md` headings `Main brief` stop 6, `Rollout`, `Ordering`, `Idempotency`, `Observability`, `Rollback and forward recovery`, `Partial failure`, `Runtime checks (Fabric DEV; user)`.
- `notebooks/NB_SETUP_POI_AMENITY.ipynb` cells `c1setupparam` and `c1setupplan`.
- `notebooks/NB_SLV_POI_AMENITY.ipynb` cell `d1amenparam`.
- `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb` cell 1 only.
- `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` the `NODE_MODES` comment: node `DRY_RUN` computes, runs quality gates, and counts the diff. It does not create or write the target table.
- `docs/context/CTRL_TABLES_CONTEXT.md` the `PL_VV_TRANS_SLV_TO_SLV_1H` block, including the `slv_poi_amenity` subsection.

Parameters, exact:
- Setup cell default: `p_apply = "false"`. Second setup run sets `p_apply = "true"`.
- Node cell defaults: `p_exec_id = ""`, `p_run_id = ""`, `p_pl_name = ""`, `p_trg_fq = ""`, `p_pinned_json = ""`, `p_mode = "RUN"`, `p_force = "false"`, `p_history_limit = "1000"`. The DRY_RUN step changes only `p_mode` to `"DRY_RUN"`.
- NB_00 cell defaults, with one override: `p_pl_name = "PL_VV_TRANS_SLV_TO_SLV_1H"`. Keep `p_run_id = ""`, `p_mode = "RUN"`, `p_max_parallel = "3"`, `p_node_timeout_min = "20"`, `p_dag_timeout_min = "45"`, `p_lock_timeout_min = "90"`, `p_force_nodes = ""`, `p_history_limit = "1000"`, `p_non_data_ops = ""`.

Order:
1. Read-only count of active `slv_poi_entity` edges. Pass is 2. Use the SQL in `c1setupplan`. If it is not 2, stop. Do not run setup apply.
2. Run `NB_SETUP_POI_AMENITY` with `p_apply = "false"`. Expect exit JSON `status = PLAN`, `google = 78`, `partner = 74`, `entity_edges_ok = 2`. No table or edge write.
3. Run the same notebook with `p_apply = "true"`.
4. Run `NB_SLV_POI_AMENITY` with `p_mode = "DRY_RUN"` and the other node defaults. No target write.
5. Run `NB_00_ORCHES_SLV_TO_GLD` with the parameters above.
6. Run the four architecture runtime checks. Each count must be 0. Write each query in full. Check 3 joins live `slv_poi_amenity` to `slv_3p_poi_amenity` on `poi_id`. Check 4 counts live rows whose `amenity_raw` starts with `evChargeOptions.`.

Idempotency: rerun setup with `p_apply = "true"` (seed insert count 0) and rerun NB_00 (node diff 0). Watermark advances only after node SUCCESS. Log table is `lh_vv_ctrl.dbo.ctrl_log_table_run` for `trg_tbl = slv_poi_amenity`.

Rollback is the `is_active = 0` update and `RESTORE TABLE` from architecture. Do not include `DROP TABLE`. Forward recovery is rerun setup, then the node.

Leave `Kết quả người dùng ghi nhận` empty. Samples at most 50 rows. No personal data and no secrets. Do not guess a value that is not in the files.
