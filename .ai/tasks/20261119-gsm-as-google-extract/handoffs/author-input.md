# Author input — runbook

User comment, verbatim:

- accept risk cho cả 2 GATE

Accepted risk, do not ask the operator to change these parameters:

- GATE-001: a manual `table_filter` that includes `slv_3p_poi` and omits child tables can flip the parent to `google` without takeover. The scheduled pipeline passes `table_filter` empty.
- GATE-002: a manual `state_key = row` does not clear review and media state on takeover. The scheduled pipeline passes `state_key = doc`.

Write `runtime-runbook.md` in Vietnamese for Fabric DEV only. Do not claim a run happened. Sections required by the workflow skill: Phạm vi và môi trường, Điều kiện tiên quyết, Baseline trước khi chạy, Các bước thực hiện, Kiểm tra kết quả, Chạy lại để kiểm tra idempotency, Kiểm tra log và watermark, Rollback và forward recovery, Kết quả người dùng ghi nhận.

Read: architecture.md ## Rollout and ### DEV runtime; notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb parameter cell `e3eb64e4`; pipeline activity `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` parameters `table_filter` empty, `state_key` `doc`, `full_reload` false.

Parameters for the backfill preview and real run, from that cell: `sources = google,sgm`, `dry_run` true then false, `full_reload = True`, `allow_full_scan = True`, `max_retries = 1`, `max_parallel = 12`, `table_filter` empty, `state_key = doc`, `cast_null_policy = FAIL`, `src_schema = lh_vv_bronze.dbo`, `src_tbl = brz_3rd_crawler_poi_stream`.

Checks: V-1 through V-9. Expected backfill: `sgm_valid = 2630`, `google_priority_skipped = 402`, `takeover_poi = 0`, `slv_3p_poi` rows with `source_name = sgm` = 2228. Record `v0` before the real `full_reload`. Incremental rerun and second `full_reload` must insert 0 rows.

V-10 and V-11 need a DEV fixture and an explicit user confirmation before any bronze write or non-empty `table_filter`. Put them in the runbook as not part of this run. Downstream order after the extract: `NB_SLV_POI_ENTITY_NON_ENRICH`, then amenity and media, then `NB_ENR_POI_INFO`, then gold. Rollback: set `sources` back to `google` first. Any DELETE of `sgm` rows needs a separate confirmation.
