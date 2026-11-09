# SPARK-001 media scan

Resolves review finding `SPARK-001`: whether `_cover`'s duplicate count recomputes `slv_poi_media_info` for the later join and `cover_matched` metric.

Environment: Fabric DEV, capacity F16, lakehouses `lh_vv_silver` and `lh_vv_gold`.

This probe is one notebook `DRY_RUN`. `DRY_RUN` executes `build` and does not MERGE `gld_srv_poi_info`. `p_force=true` is required: an empty inbox returns `NO_DATA` before `build`.

## Prerequisites

1. Publish the current `notebooks/NB_GLD_SRV_POI_INFO.ipynb` to the Fabric DEV notebook `NB_GLD_SRV_POI_INFO`. Cell `srvinfobuild` must contain `_cover` and `SPEC.inputs["media"] = slv_poi_media_info`.
2. Run `notebooks/NB_CREATE_DDL.ipynb` cell `srvcoverpy` once if `lh_vv_gold.dbo.gld_srv_poi_info` does not yet have `cover_id` and `cover_blob_url`, or if `ctrl_mng_pipeline_config` has no active edge `slv_poi_media_info` -> `gld_srv_poi_info` on `PL_VV_TRANS_SLV_TO_GLD_30M`. The cell adds only missing columns and inserts the edge `WHERE NOT EXISTS`. It takes lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`. If that lock is held, wait and run the cell again. Do not run the cell while the 30M flow is in `RUN`.

## Parameters

Set these on `NB_GLD_SRV_POI_INFO` cell `srvinfoparam` for this run only:

```text
p_exec_id =
p_run_id =
p_pl_name = PL_VV_TRANS_SLV_TO_GLD_30M
p_trg_fq = lh_vv_gold.dbo.gld_srv_poi_info
p_pinned_json =
p_mode = DRY_RUN
p_force = true
p_history_limit = 1000
```

## Steps

1. Confirm the 30M flow lock is free, or accept that `DRY_RUN` only reads while another exec holds it.
2. Run all cells of the published `NB_GLD_SRV_POI_INFO` once with the parameters above.
3. Open Spark UI for that application. The cell progress indicator is gone after the cell finishes, so use one of these paths:
   - Notebook still shows a session in the bottom status bar: select the Session ID. On the monitoring detail page, select a job description to open that job in Spark UI, or use the Spark UI link on the page.
   - Session already stopped: in the notebook ribbon select Run, then All runs. Open the run whose log contains `exec 390dc54c-7b54-4938-b319-2ec970a13db0`. On the detail page select Spark history server.
   - Same application from the workspace: select Monitor, search `NB_GLD_SRV_POI_INFO`, open the completed application, then select Spark history server.
   Keep every job and SQL node whose description or input path contains `slv_poi_media_info`. On each stage page read Input, Shuffle Read, Shuffle Write, and Spill.
4. Write the result file below. Do not paste row samples, notebook output with POI values, or secrets.

## Result schema

Save `.ai/tasks/20261108-gld-srv-poi-info-cover/evidence/results/spark-001-media-scan.md` with:

- `exec_id` from the notebook log, `status` (`SUCCESS` or the error), and Spark application id.
- One row per Spark job or SQL node that reads `slv_poi_media_info`: `job_or_sql_id`, `scan_bytes`, `shuffle_read_bytes`, `shuffle_write_bytes`, `spill_bytes`, `peak_executor_memory_bytes`, `wall_time_ms`.
- `media_scan_count`: number of those rows.
- `node_wall_time_ms`: duration of this notebook run.
- `spill_bytes_total`: sum of `spill_bytes`.

At most 50 metric rows. No personal data, secrets, or production extracts.

## Pass/fail

- Not reproduced: `status=SUCCESS`, `media_scan_count` is 1, and `spill_bytes_total` is 0.
- Reproduced: `media_scan_count` is greater than 1, or `spill_bytes_total` is greater than 0.

A second `DRY_RUN` with the same parameters is a new read of the same plan. It does not roll back a MERGE, because this probe does not MERGE. If the run fails before Spark UI has the media jobs, paste the error text and stop; do not switch the probe to `RUN`.
