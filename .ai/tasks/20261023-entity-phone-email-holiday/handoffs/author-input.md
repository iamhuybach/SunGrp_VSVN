# Author input — runbook

Write the combined DEV runbook for this task. Do not tell the operator to run `.ai/tasks/20261023-entity-opening-hours-passthrough/runtime-runbook.md`. That pause is D-OH-08. This runbook applies `ohpasspy` (not yet on DEV) and then `peholpy`.

## Read

- This task: `architecture.md` sections `Rollout`, `Rollback and forward recovery`, `Verification`; `decision.md` D-PEH-01 through D-PEH-08.
- Hours task: `decision.md` D-OH-07 only, and `runtime-runbook.md` sections `Các bước thực hiện`, `Chạy lại để kiểm tra idempotency`. Copy its unknown placeholders. Do not invent a workspace name, trigger item, commit hash, or sync method.
- `notebooks/NB_CREATE_DDL.ipynb` has no parameter cell. Default lakehouse is `lh_vv_bronze`. Run only `ohpasspy`, then only `peholpy`.
- `notebooks/NB_00_ORCHES_SLV_TO_ENR_15P.ipynb` cell `5de61e9d` is the parameter cell. Use these values exactly: `p_pl_name = "PL_VV_TRANS_SLV_TO_ENR_15P"`, `p_run_id = ""`, `p_mode = "RUN"`, `p_max_parallel = "2"`, `p_node_timeout_min = "15"`, `p_dag_timeout_min = "25"`, `p_lock_timeout_min = "35"`, `p_force_nodes = ""`, `p_history_limit = "1000"`, `p_non_data_ops = ""`.

## Order

1. Turn off the `PL_VV_TRANS_SLV_TO_ENR_15P` trigger (D-OH-07). Confirm the flow lock is free.
2. Snapshot `DESCRIBE`, history version, counts by `source_name`, and the lock row.
3. Deploy together: `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_ENR_POI_INFO`, `NB_CREATE_DDL`, `NB_SETUP_INITIAL_DDL`. Do not run setup on DEV. Do not run `enrddlpy`, `enrinfopy`, or `mvpoipy`.
4. Run `ohpasspy`, then `peholpy` only after the lock is free. `peholpy` success print contains `['phone', 'email', 'holiday_exceptions'] string NULL sau opening_hours_text`.
5. Run the orchestrator once with the parameter cell above. Check architecture `Verification` items 1–6, including the hours regression and unchanged gold schema.
6. Idempotency: rerun `peholpy` (`vừa thêm []`, no new Delta version) and the hours second orchestrator run plus `ohpasspy` rerun. Only then turn the trigger back on (D-OH-07).

## Rollback

Code rollback is redeploy of the hours-only notebooks. `UPDATE` that nulls the three columns, and `RESTORE`, are user decisions. Do not `DROP` the table or the columns.
