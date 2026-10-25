# Request

## User outcome

Explain the 2026-10-26 Fabric DEV run of `NB_00_ORCHES_SLV_TO_GLD` (`exec_id` `8f8da0f2-175e-4e9d-bd0e-6bb3756f5a06`, about 19:43–19:44) that ended `PARTIAL_FAILED` because `gld_srv_poi_multi_lang` raised `QualityGateError: Đầu vào bắt buộc rỗng: ['lh_vv_silver.dbo.slv_enr_poi_info_multi_lang']`. Separate that failure from the cadence WARN and from the `NEW_EDGE` version text. Do not change code in this phase.

## Scope

### In scope

- Classify the failure as `code`, `data`, `architecture`, or `unclear`, with file and line.
- Decide whether the cadence WARN for suffixes `_30P` and `_15P` caused `PARTIAL_FAILED`.
- Read `NEW_EDGE` `(đã đọc None, đọc 2)` as a Delta version and compare it with `is_empty`.
- If the repository has no row count for `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang`, add one read-only probe and stop at `waiting_evidence`.

### Out of scope

- Code, notebook, pipeline, or schema edits.
- Reading `notebooks_lgc/`, `docs/context/3p-google/*.txt`, pipeline manifests, or other task artifacts.
- Inventing row counts.

## Acceptance criteria

- The WARN and the `QualityGateError` are separate conclusions.
- The probe counts current rows, counts `deleted_at IS NULL` when that column exists, lists column names, and also reports the same aggregates at Delta version 2.
- Sample output is at most 50 lines and contains no personal data.

## Constraints

- Diagnosis only until the probe result is pasted under `evidence/results/`.
- Fabric DEV lakehouses: `lh_vv_ctrl`, `lh_vv_silver`, `lh_vv_gold`.
- Run parameters: `p_pl_name=PL_VV_TRANS_SLV_TO_GLD_30P`, `p_run_id` empty, `p_mode=RUN`, `p_max_parallel=3`, `p_node_timeout_min=20`, `p_dag_timeout_min=45`, `p_lock_timeout_min=90`, `p_force_nodes` empty, `p_history_limit=1000`, `p_non_data_ops` empty.

## Classification rationale

- Complexity: medium. One orchestrator run, one node quality gate, and a data-dependent empty check. Signals: `partial_failure`, `data_evidence_required`.
- Risk: medium. The failed node aborts before the gold MERGE. No data-loss path is in scope.
- Architecture: not required yet. Whether the gate should reject an empty input depends on the probe.
- Evidence: required. The repository does not contain the row count or the column list of `slv_enr_poi_info_multi_lang`.
- Runtime proof: not required for this diagnosis. A later code change would need its own runbook.
- Reviewer routing: none while the task only adds a probe. A later notebook change routes to `spark-runtime-reviewer`.
