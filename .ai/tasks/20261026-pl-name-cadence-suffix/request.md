# Request

## User outcome

Every active `pl_name` that ends in `_15P` or `_30P` uses the cadence suffix `CADENCE_RE` already accepts, so the transform library applies the fast-flow versus slow-flow node check. The business reason: the library reads cadence from the suffix and skips that check when the suffix is `P`.

## Scope

### In scope

- Rename only the suffix, keeping the prefix and the number: `_15P` becomes `_15M`, `_30P` becomes `_30M`.
- `PL_VV_TRANS_SLV_TO_ENR_15P` becomes `PL_VV_TRANS_SLV_TO_ENR_15M`.
- `PL_VV_TRANS_SLV_TO_GLD_30P` becomes `PL_VV_TRANS_SLV_TO_GLD_30M`.
- Active `pl_name` values in notebooks, pipeline JSON, tests, the standard sentence in `AGENTS.md`, and `docs/context/02_NAMING_CONVENTION.md` §3.
- `NB_SETUP_INITIAL_DDL`: edit the seed in place.
- `NB_CREATE_DDL`: leave existing cells unchanged. Append one markdown cell `[THÊM 26/10] 20261026-pl-name-cadence-suffix` and one self-contained patch cell at the end.
- The patch updates existing ctrl rows to the new name, including watermark rows that carry the old `pl_name`. A second run does not change the result. No `DROP` of a table. No delete of a watermark row.
- Ctrl `pl_name` matches the pipeline name that calls the notebook.
- Rename the folder and file `pipelines/PL_VV_TRANS_SLV_TO_ENR_15P/PL_VV_TRANS_SLV_TO_ENR_15P.json` to the new pipeline name, and make the activity parameter `p_pl_name` follow that name.
- Notebooks that assign the operational name, including `NB_SETUP_POI_ENTITY` and `NB_SETUP_POI_AMENITY`.
- The default `p_pl_name` in `NB_00_ORCHES_SLV_TO_ENR_15P`. The notebook file name stays.

### Out of scope

- Widening `CADENCE_RE`, or treating `P` as minutes. Do not edit the cadence check in `NB_LIB_TRANSFORM_SLV_GLD`.
- `pl_name` values that already end in `_1H`, `_1D`, `_15M`, or `FL_00`. `NB_00_ORCHES_SLV_TO_GLD` cell 1 defaults to `PL_VV_TRANSFORM_SLV_TO_GLD_1H` and stays.
- Creating a pipeline JSON for the 30-minute flow. The repo has none for `_30P`. The runbook tells the user to create or rename the matching Fabric pipeline before a manual run with the new `p_pl_name`.
- Renaming notebook files. `NB_00_ORCHES_SLV_TO_ENR_15P` is a notebook name, not a `pl_name`. The §2 example of that notebook name stays.
- Other tasks' artifacts, `notebooks_lgc/`, `docs/context/3p-google/*.txt`, and pipeline manifests.
- `data_model_change`. No `model-design.md`.
- Rewriting historical mentions in requirements, mapping docs, or `CTRL_TABLES_CONTEXT.md`.

## Acceptance criteria

- The repo has no active `pl_name` ending in `_15P` or `_30P` in notebooks, pipeline JSON, tests, the standard sentence in `AGENTS.md`, and `docs/context/02_NAMING_CONVENTION.md` §3.
- `NB_SETUP_INITIAL_DDL` seeds the new names in place. `NB_CREATE_DDL` adds only the dated markdown cell and one self-contained patch cell. Old cells stay byte-for-byte.
- The patch renames existing ctrl rows, including watermark rows attached to the old `pl_name`. Rerun does not change the result. No table `DROP`. No watermark delete.
- Ctrl `pl_name` equals the calling pipeline name. The enrich pipeline JSON folder, file, and activity `p_pl_name` follow `PL_VV_TRANS_SLV_TO_ENR_15M`.
- The activity already passes `p_pl_name` as `@pipeline().Pipeline`. Keep that expression. Change the pipeline resource name so the expression yields the new name.
- There is still no `_30M` pipeline JSON. The runbook states that the user creates or renames the Fabric pipeline before a manual run with `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_30M`.
- `CADENCE_RE` in `NB_LIB_TRANSFORM_SLV_GLD` is unchanged.

## Constraints

- Domain: pipeline, ctrl, lib transform/gold.
- Watermark key, from the repo, is not an evidence gap. `flow_lock_id(pl_name)` returns `wm_flow__{pl_name}`. `ensure_lock_row` writes `watermark_id`, `src_tbl = pl_name`, and `flow_name` as the notebook name. Lock updates match `watermark_id`. Edge ids `wm_e__<trg_tbl>__<src_tbl>` do not contain `pl_name`. `ctrl_mng_pipeline_config` logical key includes `pl_name` (`docs/context/02_NAMING_CONVENTION.md` §4, `docs/context/CTRL_TABLES_CONTEXT.md` §3 and §4).
- `NB_SETUP_INITIAL_DDL` seeds with `MERGE … WHEN NOT MATCHED THEN INSERT` only. The in-place seed change is for a new environment. The `NB_CREATE_DDL` patch is what renames rows that already exist (`docs/context/02_NAMING_CONVENTION.md` §2.1).
- Do not invent an `UPDATE` for a watermark column the repo does not use as the lock key.
- Historical `NB_CREATE_DDL` cells still contain the old names. That text is history, not the active `pl_name`. Tests must expect the active name after the seed and the new patch, not require `_15P` or `_30P` as the live value.
- Known mentions outside the acceptance surface stay: other `.ai/tasks/`, `docs/requirements/`, mapping docs, `docs/context/CTRL_TABLES_CONTEXT.md`, `docs/context/00_README.md`, `docs/context/01_DATA_MODEL.md`, `docs/context/NB_00_ORCHES_SLV_TO_GLD.md`.

## Classification rationale

- Complexity: high. The rename crosses pipeline JSON, ctrl seed and patch, orchestrator parameters, setup notebooks, tests, and the naming standard.
- Risk: high. The flow-lock id and `src_tbl` change with `pl_name`. A wrong rename can leave two lock rows or point a run at the wrong flow. Rollback is a reverse rename, and the cadence check starts to run only after the suffix matches.
- Architecture: required. The control key and the pipeline resource name change, and watermark identity moves with `pl_name`. Pipeline orchestration identity changes. Not a table grain or column change, so no `data_model_change`.
- Evidence: not required. The lock key is `wm_flow__{pl_name}` plus `src_tbl = pl_name` in `NB_LIB_TRANSFORM_SLV_GLD`. DEV row counts are not required to write an idempotent rename of that key.
- Runtime proof: required. After the user renames or creates the Fabric pipelines and runs the patch, one `PLAN` of `PL_VV_TRANS_SLV_TO_ENR_15M` and one `PLAN` of `PL_VV_TRANS_SLV_TO_GLD_30M` should show no WARN `Không đọc được nhịp` for those two names.
- Reviewer routing: `state-correctness-reviewer` (lock id, idempotent rename), `sql-data-reviewer` (patch statements), `spark-runtime-reviewer` (notebook parameter and patch cell), `fabric-pipeline-reviewer` (pipeline resource name and `p_pl_name`). Risk is high, so `risk-gate` runs. Signal: `cross_system`, plus `idempotency` and `runtime_proof_required`.
