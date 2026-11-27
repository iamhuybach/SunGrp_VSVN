# Author input — runbook 20261127-slv-pn-product-l2-transform

Write the runtime runbook from this task's architecture only.

Read:

- `.ai/tasks/20261127-slv-pn-product-l2-transform/architecture.md` `## Main brief` and `## Rollout`, `## Rollback and forward recovery`, `## Verification` (R1–R3).
- Parameter cells: `notebooks/NB_SLV_PN_PRODUCT_SALE.ipynb` `pnsaleparam`, `notebooks/NB_SLV_PN_HOTEL_ROOM_OFFER.ipynb` `pnroomparam`, `notebooks/NB_SLV_PN_HOTEL_RATE_OFFER.ipynb` `pnrateparam`.
- `notebooks/NB_CREATE_DDL.ipynb` cell `pnl2edgepy` for the edge patch. No pipeline JSON.
- `docs/context/CTRL_TABLES_CONTEXT.md` only if a step names a ctrl table.

Environment: Fabric DEV, lakehouse `lh_vv_silver`. Deploy `NB_LIB_TRANSFORM_SLV_GLD` before the three node notebooks. Do not run `NB_00` until R1 passes.

R1 is a scratch MERGE on `lh_vv_silver.dbo.tmp_pnl2_selftest_<exec8>`. Refuse if that name exists. Ten I4 transitions, with the flag and with `deleted_flag=None`. Compare `diff_counts` to Delta `operationMetrics`. Drop only that table.

R2: each node, `p_mode = RUN`, `p_force = true`, second run `inserted = updated = deactivated = 0` and no new target commit.

R3: paste `evidence/probes/pnl2_invariants.py`. Read-only. Every count is 0. No column `_is_deleted`.

Parameters already in the cells: `p_exec_id`, `p_run_id`, `p_pl_name`, `p_trg_fq` empty for a manual run; `p_mode` `RUN` or `DRY_RUN`; `p_force` `false` or `true`; `p_history_limit` `1000`; `p_pinned_json` empty.

Edge cell keeps lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`, `LEASE_MINUTES = 90`. A rerun inserts nothing.

Do not invent a workspace id, capacity, or epoch unit. `valid_from` and `valid_to` stay 1-1.
