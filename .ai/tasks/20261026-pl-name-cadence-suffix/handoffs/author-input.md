# Author input | runtime runbook

Task: `20261026-pl-name-cadence-suffix`. Environment: Fabric DEV. Do not claim a run already happened.

Prove: cell `plcadpy` in `notebooks/NB_CREATE_DDL.ipynb` renames ctrl rows, a second run writes nothing, and PLAN of the two new names has no WARN `Không đọc được nhịp`.

Read architecture `Main brief` and `Rollout`. Read parameter cells, not whole notebooks.

Pairs: `PL_VV_TRANS_SLV_TO_ENR_15P` -> `PL_VV_TRANS_SLV_TO_ENR_15M` (lease 35). `PL_VV_TRANS_SLV_TO_GLD_30P` -> `PL_VV_TRANS_SLV_TO_GLD_30M` (lease 90). Lock id is `wm_flow__<pl_name>`. No DROP, DELETE, or watermark delete. If the cell prints `Dừng trước khi ghi`, stop for the user.

Order:
1. Pause the Fabric schedule of `PL_VV_TRANS_SLV_TO_ENR_15P`. Confirm `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` and `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P` have `lock_exec_id` NULL.
2. Sync notebooks. Run only `plcadpy`. Do not Run-all older `NB_CREATE_DDL` cells. Run `plcadpy` before `NB_SETUP_POI_*`.
3. Run `plcadpy` a second time.
4. Rename the Fabric pipeline to `PL_VV_TRANS_SLV_TO_ENR_15M`, then resume its schedule. Repo JSON is `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json`. Activity name stays `NB_00_ORCHES_SLV_TO_ENR_15P`. `p_pl_name` is `@pipeline().Pipeline`. Timeout `0.00:32:00`.
5. There is no `_30M` pipeline JSON. Create or rename the Fabric pipeline before any manual run with `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_30M`.

PLAN, not RUN, for the cadence check:
- `notebooks/NB_00_ORCHES_SLV_TO_ENR_15P.ipynb`: `p_pl_name=PL_VV_TRANS_SLV_TO_ENR_15M`, `p_run_id=""`, `p_mode=PLAN`, `p_max_parallel=2`, `p_node_timeout_min=15`, `p_dag_timeout_min=25`, `p_lock_timeout_min=35`, `p_force_nodes=""`, `p_history_limit=1000`, `p_non_data_ops=""`.
- `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb`: set only `p_pl_name=PL_VV_TRANS_SLV_TO_GLD_30M` and `p_mode=PLAN`. Leave `p_max_parallel=3`, `p_node_timeout_min=20`, `p_dag_timeout_min=45`, `p_lock_timeout_min=90`.

Let one ENR_15M RUN finish before the next GLD_30M or GLD_1H RUN. A cadence ConfigError stops for the user. Samples: at most 50 rows, no personal data, paste into `Kết quả người dùng ghi nhận`.
