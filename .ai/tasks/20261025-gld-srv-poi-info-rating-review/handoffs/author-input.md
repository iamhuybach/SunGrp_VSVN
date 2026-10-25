# Author input — runbook

Fabric DEV. Vietnamese runbook for the checks already specified. Do not add a schedule. Do not rerun `srvpoipy` after `srvratepy`.

## Read

- `.ai/tasks/20261025-gld-srv-poi-info-rating-review/architecture.md` — `Main brief` (Order and stop points, steps 5–9; Tests and verification), `## Rollout`, `## Rollback and forward recovery`, `## Verification` (R0–R7)
- `notebooks/NB_GLD_SRV_POI_INFO.ipynb` cell `srvinfoparam`
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_param`
- `notebooks/NB_CREATE_DDL.ipynb` cells `srvratemd`, `srvratepy` (no parameter cell; run the cell)
- `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb` cell `3485be21`
- `docs/context/CTRL_TABLES_CONTEXT.md` for `ctrl_mng_pipeline_config`, `ctrl_mng_watermark`, `ctrl_log_run`, `ctrl_log_table_run`

## Parameters from those cells

`NB_GLD_SRV_POI_INFO`: `p_exec_id=""`, `p_run_id=""`, `p_pl_name=""`, `p_trg_fq=""`, `p_pinned_json=""`, `p_force="false"`, `p_history_limit="1000"`. `p_mode` is `"DRY_RUN"` then `"RUN"` then `"RUN"` (R5).

`NB_SETUP_INITIAL_DDL`: `p_apply="false"` (R3).

`NB_00_ORCHES_SLV_TO_GLD` PLAN (R7): the cell default `p_pl_name` is `PL_VV_TRANSFORM_SLV_TO_GLD_1H`. This run uses `p_pl_name="PL_VV_TRANS_SLV_TO_GLD_30P"`, `p_mode="PLAN"`, and the other cell defaults: `p_run_id=""`, `p_max_parallel="3"`, `p_node_timeout_min="20"`, `p_dag_timeout_min="45"`, `p_lock_timeout_min="90"`, `p_force_nodes=""`, `p_history_limit="1000"`, `p_non_data_ops=""`.

## Baseline query named by architecture R0

B2 from task 20261024, expected 6 rows before `srvratepy` and 8 rows after (6 old plus 2 new info edges; architecture R1 says `gld_srv_poi_info` has 5 active edges):

```sql
SELECT pl_name, src_schema, src_tbl, trg_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl IN ('gld_srv_poi_multi_lang', 'gld_srv_poi_info')
GROUP BY pl_name, src_schema, src_tbl, trg_tbl, is_active, priority, load_mode, nb_name
ORDER BY trg_tbl, src_tbl
```

Config count query: `SELECT count(*) AS n FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`. R0 expects 59. R1/R2 expect 61.

R4 is a scratch session: paste `srvinfobuild` after `%run NB_LIB_TRANSFORM_SLV_GLD`. Keys are Google `poi_id` values from `slv_poi_entity_non_enrich`. Print the three aggregates in architecture R4. No personal data.

R6 SQL is in architecture Verification. Paste counts only, at most 50 rows, into `Kết quả người dùng ghi nhận`.

Lock id: `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P`. Lease 90 minutes.
