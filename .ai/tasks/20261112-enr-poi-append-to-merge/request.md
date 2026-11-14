# Request

## User outcome

Rerunning the same grain key updates the existing row in `lh_vv_gold.enr.gld_enr_poi_info` (`poi_id`) and `lh_vv_gold.enr.gld_enr_poi_review` (`review_id`). It does not insert a second row for that key.

## Scope

### In scope

- Switch those two gold targets from the current APPEND write to the MERGE contract already used by the other gold tables in `NB_LIB_TRANSFORM_SLV_GLD` and the gold `srv` notebooks.
- Keep the documented grain, columns, sources, and enrich flags. Keep every review edge `is_active = 0`.
- D-RISK-1 (updated 2026-11-12): the extra `gld_enr_poi_review` rows are old APPEND data. A correct test deletes that table's data and runs init again. Do not delete `gld_enr_poi_info`. The delete and init are a Fabric DEV runbook step, not a step this task executes. Do not turn the review edges on.
- Write mode is per target or per edge. Other APPEND targets, including `gld_enr_poi_coordinate`, stay APPEND.
- Update the places that pin APPEND for these two tables: the ctrl seed, the enrich notebooks, the library branch that is specific to them, `tests/test_enr_poi_contract.py`, `docs/context/gld_enr_poi_info_review.md`, `docs/context/CTRL_TABLES_CONTEXT.md`, `docs/context/01_DATA_MODEL.md`, `docs/context/00_README.md`, and `docs/context/03_OPERATOR_GUIDE.md`.
- Change pipeline JSON only if the write mode is stored in that file. `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json` does not contain `load_mode`, `APPEND`, or these table names.

### Out of scope

- `gld_enr_poi_coordinate` and any other remaining APPEND target.
- Turning the review flow back on.
- Column, grain, or source changes.
- `services/`, `notebooks_lgc/`, and task `20261110-serving-poi-read-apis`.
- Running a Fabric notebook or pipeline in this task.
- A new MERGE design. `sql_merge_edge_wm` is the watermark MERGE, not a second gold-target write.

## Acceptance criteria

- A rerun of the same key updates the row in place and does not add a second row.
- The MERGE key matches the grain in `docs/context/gld_enr_poi_info_review.md`: `poi_id` for info, `review_id` for review.
- `tests/test_enr_poi_contract.py` and `python scripts/vv.py verify` pass.
- No Fabric notebook or pipeline run is claimed for this task.

## Constraints

- Reuse the live gold MERGE rules for the match key, update on change, rerun, source-row disappearance, watermark, and log.
- Stop if the library has two different target-MERGE contracts. Do not pick one.
- MERGE correctness depends on the current target rows being unique on the grain key. The repository does not prove that. Do not invent row counts.
- Do not copy credentials or hosts into the repository.
- Do not change grain or the inactive review edges. D-COL-1 accepts only `row_hash` STRING and `deleted_at` TIMESTAMP on `gld_enr_poi_info` and `gld_enr_poi_review`.

## Classification rationale

- Complexity: high. The write, rerun, and watermark behavior of two gold targets changes, and the edit spans the library, ctrl seed, notebooks, tests, and operator docs.
- Risk: high. The change is idempotency of a durable gold write, and the in-place rerun is proven only at runtime.
- Architecture: required. Watermark and rerun behavior change, and the user required an architecture gate for this write-mode change. Grain and key stay as documented, so `data_model_change` is not set.
- Evidence: required. `CTRL_TABLES_CONTEXT.md` states Delta has no primary key, and these targets are APPEND. Intended grain in `docs/context/gld_enr_poi_info_review.md` does not prove the current Fabric rows are unique. Probe `evidence/probes/key-uniqueness.sql` is the smallest read-only check.
- Runtime proof: required after implementation, as a runbook only. Stop before any Fabric DEV execution.
- Reviewer routing: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`. No `fabric-pipeline-reviewer` unless a later diff touches pipeline JSON. No API reviewer. Risk is high, so the risk gate is required by the workflow.
