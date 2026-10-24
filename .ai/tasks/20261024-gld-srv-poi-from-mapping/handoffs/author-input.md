# Author input

Write `runtime-runbook.md` only. Vietnamese. Fabric DEV. Do not schedule a pipeline and do not DROP tables.

`srvpoipy` already ran twice on 2026-10-24. Run 1 created both gold tables and added 5 destination columns. Run 2 printed `destination +0` and `gold tạo []`. Probe `gld_srv_edge_payload`: `edge_n 6`, `payload_match True`, three `cols match True`. See `evidence/results/gld_srv_edge_payload.txt`.

After that run, `srvpoipy` gained `_refresh_lock()` before `ALTER`, each `CREATE`, and `INSERT`. The user accepted the residual risk (`D-SRV-30`, `accepted-risk`). Run the updated cell once. Pass: `destination +0` and `gold tạo []`. Fail: another ALTER, CREATE, or config insert.

Then, in order:

1. `NB_SETUP_INITIAL_DDL` with `p_apply = "false"`. Pass: 18 specs, `EXISTS_OK`, no `schema_issues`, no write.
2. `NB_GLD_SRV_POI_INFO`. Keep `p_exec_id = ""`, `p_run_id = ""`, `p_pl_name = ""`, `p_trg_fq = ""`, `p_pinned_json = ""`, `p_force = "false"`, `p_history_limit = "1000"`. Set `p_mode` to `DRY_RUN`, then `RUN`, then `RUN`. `DRY_RUN` writes nothing. First `RUN`: SUCCESS, 24 live rows, `count(*) = count(DISTINCT poi_id)`, all `is_recommended` true, 13 `operating_hours` null, 11 with `json_array_length = 7`, `is_verified`, `is_bookable`, and the destination columns null. Second `RUN`: inserted = updated = deactivated = 0 and no new Delta version.
3. `NB_GLD_SRV_POI_MULTI_LANG` with the same parameters and `p_mode = "RUN"`. Pass: FAILED, empty required input, target has 0 rows (`D-SRV-23`).
4. `NB_00_ORCHES_SLV_TO_GLD`. Set `p_pl_name = "PL_VV_TRANS_SLV_TO_GLD_30P"` and `p_mode = "PLAN"`. Keep `p_run_id = ""`, `p_max_parallel = "3"`, `p_node_timeout_min = "20"`, `p_dag_timeout_min = "45"`, `p_lock_timeout_min = "90"`, `p_force_nodes = ""`, `p_history_limit = "1000"`, `p_non_data_ops = ""`. Pass: the DAG has 2 nodes and no error. `PLAN` writes nothing.
5. Read-only Google hours counter from architecture.md section `Verification`, after running cell `srvinfohours` in a scratch session. Expect only `None` error codes. Do not print raw JSON.

Do not create or schedule `PL_VV_TRANS_SLV_TO_GLD_30P`. Do not attach these tables to `PL_VV_TRANS_SLV_TO_ENR_15P`.

Rollback in this runbook does not DROP the gold tables or the five destination columns. Forward recovery is to rerun the failed node. The flow lock is `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P`.

Paste sanitized results into `Kết quả người dùng ghi nhận`. At most 50 rows. No personal data.
