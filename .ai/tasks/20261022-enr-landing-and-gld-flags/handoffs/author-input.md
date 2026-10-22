# Author input — runbook

Write the full Vietnamese runbook. Architecture is PASS. Review round 2 is PASS. Status will be `waiting_runtime`.

## Already done in Fabric DEV — record under Kết quả, do not repeat

- No Fabric pipeline object `PL_VV_TRANS_SLV_TO_ENR_15P` to pause. `lock_exec_id` on `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` was NULL. Four notebooks were git-synced.
- Empty scratch `lh_vv_gold.enr.probe_spark001_scratch`: column mapping on, `drop_me` dropped, scratch table dropped. User reported success.
- `gld_enr_poi_info` `DROP COLUMNS (district, destination_name)` succeeded. DESCRIBE before `enrflagpy` had 38 columns, no `district` or `destination_name`. `street`, `ward`, `city`, `full_address` remained.
- Cell `enrflagpy` ran twice. Run 1 created the three `lh_vv_silver.dbo.slv_enr_*` tables. Run 2 did not create them again. Both edge checks: three rows, `is_active = 1`, `n = 1`.
- `DRY_RUN` already ran. Info SUCCESS 89s, exit inserted 65, updated 0, `trg_version` null. Review SUCCESS 75s, exit inserted 285, updated 0, `trg_version` null. Scale then: info 65 rows, review 455 rows, each landing table 1 probe row.
- Probe key `probe-spark-001` was deleted. User reported all three counts are 0. Spark UI is closed. `SPARK-001` is `accepted-risk` in `decision.md`. Spill was not measured.

## Still to run

Manual `RUN` of `NB_ENR_POI_INFO` then `NB_ENR_POI_REVIEW` (the backfill that writes true/false). Then V1–V4 and R7 from architecture §16. R7 must pick an existing gold `poi_id` and `review_id` with a query. Do not hard-code a real id. Do not paste `review_text` or `description`.

## Parameters

Cell `notebooks/NB_ENR_POI_INFO.ipynb` id `6afb4f0e` and `notebooks/NB_ENR_POI_REVIEW.ipynb` id `c8309a9e` both default to: `p_exec_id=""`, `p_run_id=""`, `p_pl_name=""`, `p_trg_fq=""`, `p_pinned_json=""`, `p_mode="RUN"`, `p_force="false"`, `p_history_limit="1000"`.
For this flow set `p_pl_name="PL_VV_TRANS_SLV_TO_ENR_15P"` (ctrl `pl_name` in cell `enrflagpy` and the DRY_RUN log). `p_mode` for the remaining write is `RUN`. `p_force` stays `false`.

## Read

- `.ai/tasks/20261022-enr-landing-and-gld-flags/architecture.md` Main brief, §12, §13, §15.3, §16
- `decision.md` ledger D-01–D-09 and finding `SPARK-001`
- `evidence/results/spark-001-dry-run.txt`
- Do not read other tasks, `notebooks_lgc/`, or pipeline manifests. There is no pipeline JSON for this flow.
