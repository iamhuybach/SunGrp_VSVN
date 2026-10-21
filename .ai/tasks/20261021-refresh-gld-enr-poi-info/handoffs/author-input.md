# Author input — runtime runbook

Review round 3 PASS. Write the DEV runbook only. Do not mark a gate. Do not claim a Fabric run happened.

Read architecture.md sections: Main brief, Rollout, Rollback and forward recovery, Implementation plan > Runbook SQL, Verification (P-0 through P-8).

Notebooks:
- NB_SETUP_INITIAL_DDL parameter cell `init_param`: `p_apply = "false"`.
- NB_CREATE_DDL: run cell `enrinfopy` only. Do not re-run `enrddlpy`.
- NB_00_ORCHES_SLV_TO_ENR_15P: use the parameter values in its parameter cell and in pipeline `PL_VV_TRANS_SLV_TO_ENR_15P` (`p_dag_timeout_min` 25, `p_lock_timeout_min` 35).

Rules:
- Environment is Fabric DEV. R-3 drops only `lh_vv_gold.enr.gld_enr_poi_info`. Never drop `gld_enr_poi_coordinate`. Never delete `wm_flow__`.
- If R-1 column names are neither the old 23 nor the new 40, stop and return to the Architect.
- If R-1 already matches the new 40 columns, skip R-3 and R-4.
- Pause the ENR trigger before R-3. Resume it only after the second RUN.
- Paste targets are under `evidence/results/`. At most 50 rows. No personal data.
