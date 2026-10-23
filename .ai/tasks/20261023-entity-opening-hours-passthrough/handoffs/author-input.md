# Author input — runbook

User accepted risk for STATE-001, SQL-001, and SQL-002 on 2026-10-23 (decision.md D-OH-07). No review round 3. Do not invent parameters or workspace ids.

## Read

- `.ai/tasks/20261023-entity-opening-hours-passthrough/architecture.md`: `Main brief`, `Rollout (DEV)`, `Partial failure`, `Rollback and forward recovery`, `Verification` (R1–R7)
- `notebooks/NB_00_ORCHES_SLV_TO_ENR_15P.ipynb` cell 1 only
- `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` cell 1 and `notebooks/NB_ENR_POI_INFO.ipynb` cell 1 only if the steps run those notebooks
- `notebooks/NB_CREATE_DDL.ipynb` cell `ohpasspy` (id `ohpasspy`): no parameter cell; run that cell only
- `docs/context/CTRL_TABLES_CONTEXT.md` sections for `ctrl_mng_pipeline_config`, `ctrl_mng_watermark`, and `ctrl_log_table_run` when those sections exist

## Locked run

Environment: Fabric DEV. Lakehouse default of `NB_CREATE_DDL` is `lh_vv_bronze`.

Pause the trigger of `PL_VV_TRANS_SLV_TO_ENR_15P` before `ohpasspy` (D-OH-07, STATE-001). Keep it paused through the second orchestrator run, then resume it. If the operator cannot pause, say so as `<CẦN NGƯỜI DÙNG CUNG CẤP: …>` rather than guessing a schedule id. The architecture allows finishing the patch and the first orchestrator run inside one 15-minute gap only when pause is impossible.

Orchestrator parameters, from cell 1, use these exact values: `p_pl_name=PL_VV_TRANS_SLV_TO_ENR_15P`, `p_run_id=""`, `p_mode=RUN`, `p_max_parallel=2`, `p_node_timeout_min=15`, `p_dag_timeout_min=25`, `p_lock_timeout_min=35`, `p_force_nodes=""`, `p_history_limit=1000`, `p_non_data_ops=""`. Do not run the entity or gold notebooks by themselves.

`ohpasspy` success is its print. Do not re-run cells `enrddlpy`, `enrinfopy`, or `mvpoipy`. Probes R1–R7 stay read-only except the runs themselves. Samples at most 50 rows. Record `V0` from `DESCRIBE HISTORY` of `lh_vv_gold.enr.gld_enr_poi_info` before the patch.
