# Author input

Task `20261117-pipeline-precheck-flows`. Write the Fabric DEV runbook. The user runs it later. Do not claim a Fabric step ran.

Pipelines:
- `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json`
- `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json`
- `pipelines/PL_VV_TRANS_SLV_TO_GLD_30M/PL_VV_TRANS_SLV_TO_GLD_30M.json`

Notebook parameter cells:
- `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`
- `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`
- `notebooks/NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb`
- `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb`
- `notebooks/NB_00_ORCHES_SLV_TO_ENR.ipynb`
- `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb`

Cases from architecture §16. Schedules stay off until all cases pass.
- C1 extract no data: four watermarks current, no new bronze commit. Pass: four SKIP messages, no notebook run, no new `ctrl_log_run` row, no Spark session.
- C2 extract has data: one new commit on one source. Pass: only that notebook runs; one `ctrl_log_run` row with the pipeline `run_id`; the next run skips.
- C3 transform no data: last ENR run `SUCCESS` or `NO_DATA`, no later upstream run. Pass: `gate_reason = NO_DATA`, no notebook. Same for GLD.
- C4 transform has data: after C2. Pass: next ENR run has `gate_reason = UPSTREAM_CHANGED` and the notebook runs; the following run skips, or runs once more with `NO_DATA` and then skips. Record the delay from extract `ended_at` to the gate. One run with `p_force_run = true` starts the notebook.
- C5 capacity: C2 and C4 overlap, plus one idle hour. Pass: no throttling in Capacity Metrics. Record CU of pipeline operations and of Spark for that hour.
- C6 failure and overlap: one notebook id left empty; one notebook forced to fail; a second trigger while a run is active. Pass: empty id fails with `BAD_NOTEBOOK_BINDING` and nothing runs; a failed notebook fails the pipeline and later sources still ran; the second trigger starts no second notebook.

Rollout prerequisites from architecture §14: bronze shortcuts `Files/_delta_src/` for `brz_3rd_crawler_poi_stream`, `cms_raw_data`, and `brz_enrichment_result`; one `wm_transform_<src_tbl>` row per source; a manual first load of each new source with `allow_full_scan = true`; the four extract notebooks and both orchestrators published. Then import the three pipelines and bind `nb_extract_3p_id`, `nb_extract_cms_id`, `nb_extract_enr_id`, `nb_orches_id`, `workspace_id`, and `conn_lh_vv_bronze_by_sqlep`.

Notebook ids and the workspace id are not in the new activities. Mark them `<CẦN NGƯỜI DÙNG CUNG CẤP>`. Do not copy a GUID into the runbook. `p_force_run` default is false. `p_max_idle_min` default is 0. Partner activity parameters stay the values in the FL_00 JSON, including `run_id` empty and `running_timeout_minutes` 60. New extract activities use `running_timeout_minutes` 60 and activity timeout `0.00:59:00`.

Rollback: disable the schedule and re-import the previous JSON from Git `9a62b9f`. The GLD pipeline is new; disable or delete it. Forward recovery: one transform run with `p_force_run = true`, or run `NB_00` by hand. A stalled extract after raw recreate: reset the watermark as in `CTRL_TABLES_CONTEXT.md` §4 and run the notebook by hand with `allow_full_scan = true`.
