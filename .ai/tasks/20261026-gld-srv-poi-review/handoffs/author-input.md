# Runbook input

No proposal. Review round 2 is PASS. Runtime has not run. Do not claim a Fabric result.

## What the user runs

Fabric DEV only. Read-only SQL except the two runs below.

1. Probe P4 before any write: `DESCRIBE HISTORY lh_vv_silver.dbo.slv_enr_poi_review_multi_lang LIMIT 20`, columns `operation`, `operationParameters`. Positional SQL `INSERT` means stop and do not run `srvrevpy`. By-name `WRITE` or `MERGE` may continue. Paste at most 50 rows to `evidence/results/runtime-p4.txt`.
2. Optional type check P3: `DESCRIBE lh_vv_silver.dbo.slv_3p_poi_review` and `DESCRIBE lh_vv_silver.dbo.slv_3p_poi_rating`. Expect `rating` and `rating_overall` `decimal(4,2)`, `rating_count` `bigint`. Paste to `evidence/results/runtime-p3.txt`.
3. In `notebooks/NB_CREATE_DDL.ipynb`, run only cell `srvrevpy`. Do not run the notebook and do not rerun `enrflagpy`. Then run `srvrevpy` again. The second run adds nothing and does not CREATE. Paste the printed columns, create flag, and edges to `evidence/results/runtime-ddl.txt`.
4. Run `notebooks/NB_GLD_SRV_POI_REVIEW.ipynb` once with `p_mode=DRY_RUN`, then once with `p_mode=RUN`, then once more with `p_mode=RUN`. The second RUN must not commit. Paste `qg_json` and the exit payload to `evidence/results/runtime-node.txt`. No personal data.

`sql-001` already returned 0 rows (`evidence/results/sql-001.txt`). That covers architecture P1 and P2. Do not ask for it again.

## Parameters

Cell `srvrvparam` defaults: `p_exec_id=""`, `p_run_id=""`, `p_pl_name=""`, `p_trg_fq=""`, `p_pinned_json=""`, `p_mode="RUN"`, `p_force="false"`, `p_history_limit="1000"`.

Manual node run uses those defaults except `p_pl_name="PL_VV_TRANS_SLV_TO_GLD_30M"`, `p_trg_fq="lh_vv_gold.dbo.gld_srv_poi_review"`, and the `p_mode` of that step. Leave exec, run, and pinned empty. Do not invent workspace or lakehouse ids.

## Contract

Target `lh_vv_gold.dbo.gld_srv_poi_review`. Grain is one row per `review_id`. Pipeline `PL_VV_TRANS_SLV_TO_GLD_30M`, load_mode `RECOMPUTE`, notebook `NB_GLD_SRV_POI_REVIEW`. Sources, in order: `lh_vv_silver.dbo.slv_enr_poi_review_multi_lang`, `slv_3p_poi_review`, `slv_3p_poi_rating`.

Lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`, lease 90 minutes, held for the whole `srvrevpy` cell. Rollback is forward only: no DROP, no DELETE, no UPDATE of `ctrl_mng_pipeline_config` in this task. A later task may set the three edges `is_active=0`. Gold stays. Readers use `deleted_at IS NULL`.

Pass: `count(*) = count(DISTINCT review_id)`; gold rows missing from `slv_3p_poi_review` are 0; `DESCRIBE` shows `rating decimal(4,2)` and `rating_count bigint`. `qg_json` blocks `pk_null` and `pk_duplicate` are 0. Samples at most 50 rows.
