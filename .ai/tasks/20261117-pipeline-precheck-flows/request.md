# Request

## User outcome

Extract and transform pipelines skip a notebook when that source has no new data, without starting Spark. Partner, 3rd-party, and the silver-to-enrichment and silver-to-gold flows follow one recorded layout. A source that has no extract notebook has no pipeline activity.

## Scope

### In scope

- Pre-check for bronze sources `partner_raw_data`, `brz_3rd_crawler_poi_stream`, `cms_raw_data`, and `brz_enrichment_result` on `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` config, using `ctrl_mng_pipeline_config`, `ctrl_mng_watermark`, and `_delta_log`. `NO_DATA` must not start Spark.
- The same no-data skip for extract notebooks that exist and for the transform flows `PL_VV_TRANS_SLV_TO_ENR_15M` (JSON exists) and `PL_VV_TRANS_SLV_TO_GLD_30M` (JSON does not exist).
- One layout choice, recorded in `decision.md` before any pipeline JSON edit: one combined pipeline, separate pipelines, or another layout. The criteria are shared F16 capacity must not be exhausted, and a no-data run must not start Spark or incur Spark cost. Do not leave two options open.
- `ctrl` seed rows must use the same `pl_name` as the chosen pipeline. `pl_name` equals the pipeline name. One active node belongs to one `pl_name`.
- Partner pipeline JSON may change. It is not in production. Keep the `NO_DATA` contract, timeout, retry, notebook parameters, sequential ForEach, `If_HasWork`, and the rule that a failed child is not a success. Do not add a Switch.
- A Fabric runtime runbook for a later DEV run, covering a no-data case and a has-data case. Stop before any Fabric DEV step.

### Out of scope

- Creating a notebook. Do not invent a notebook name, a notebook GUID, a host, or a credential. Do not store a notebook GUID in `ctrl`.
- Running a pipeline on Fabric, `docker compose`, or a local capacity.
- `notebooks_lgc/` and task `20261112-enr-poi-append-to-merge`.
- Changing a table column, grain, or key. Do not infer source row counts.
- A commit, push, or merge.

## Repository facts the layout must use

- Template: `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json`. `Get_Config_4Run` filters `is_active = 1` and `src_tbl = 'partner_raw_data'`. ForEach is sequential. `If_HasWork` calls activity `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` with `src_tbl` fixed to `partner_raw_data`. There is no Switch. `NO_DATA` is the false branch (`Set_Msg_Skip` only).
- The same `pl_name` also has config rows for `brz_3rd_crawler_poi_stream`, `cms_raw_data` (four targets), and `brz_enrichment_result` (two targets). Those sources are not in the ForEach. `docs/context/CTRL_TABLES_CONTEXT.md` records `nb_name` NULL for the CMS and enrichment rows. Partner extract rows also leave `nb_name` NULL; the pipeline activity names that notebook. NULL `nb_name` on an extract row is not proof that the notebook file is missing, and it is not a value to invent.
- Extract notebook files under `notebooks/`: `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`, `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb`, `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb`.
- Transform notebook files: `NB_00_ORCHES_SLV_TO_ENR.ipynb` for `PL_VV_TRANS_SLV_TO_ENR_15M`, and `NB_00_ORCHES_SLV_TO_GLD.ipynb` for `PL_VV_TRANS_SLV_TO_GLD_30M`. Enrichment JSON calls `NB_00_ORCHES_SLV_TO_ENR_15P` after a binding check. It always starts the notebook when the binding is present. Gold has no pipeline JSON.
- The only notebook id embedded in pipeline JSON today is the partner activity in the FL_00 export. Do not copy that id onto another activity. A new notebook activity whose Fabric id is not already in the repo uses a parameter binding that fails closed when the id is empty or a placeholder. Do not invent the id.
- Activity names are globally unique. `dependsOn` points only at an activity in the same list. Every notebook activity has an explicit timeout, retry, and parameter map. `run_id` may be an empty string. `pl_name` is the pipeline name stored in `ctrl`.
- Rule `.cursor/rules/20-data-pipeline.mdc` says other sources stay outside FL_00 and FL_00 must not gain a Switch. The user allows the partner template to change because it is not in production. The chosen layout still keeps the `NO_DATA` contract and no Switch.

## Acceptance criteria

- Pipeline JSON and the `ctrl` seed match the single layout recorded in `decision.md`. A source with no notebook has no activity. Architecture names that gap when it applies.
- Each notebook activity has a timeout, a retry, and a parameter map. Activity names do not collide. `dependsOn` points only at an activity in the same scope. A failed child is not reported as success. `NO_DATA` does not start Spark.
- `python scripts/vv.py verify <task-id>` passes before review.
- Reviewers: `fabric-pipeline-reviewer` and `risk-gate`. Add `sql-data-reviewer` because the diff includes pre-check SQL. Add `spark-runtime-reviewer` only if the diff edits a notebook.

## Constraints

- Do not copy credentials, hosts, or notebook GUIDs into `ctrl`.
- Do not infer source row counts.
- Do not run the pipeline on Fabric in this task.
- Main model for this task is Grok 4.7 medium. Architect, author, and author_proposal lanes use the user-approved exception `claude-fable-5-2` at effort medium (2026-11-17). Review stays `gpt-5.6-sol` medium. If the CLI rejects `claude-fable-5-2`, stop. Do not fall back to Opus.

## Classification rationale

- Complexity: high. The change spans extract and two transform cadences, and the layout has material alternatives.
- Risk: high. A wrong skip stalls freshness; overlapping notebook runs can exhaust shared F16 capacity; retry and child-failure behavior must stay fail-closed. Not critical: the change does not itself rewrite table grain or keys.
- Architecture: required. Pipeline orchestration changes, and more than one layout meets the capacity and no-Spark criteria (`design_tradeoffs`).
- Evidence: not required. The pre-check contract and config rows are already in the repo. Correctness of the JSON and seed does not depend on source row counts.
- Runtime proof: required for the later Fabric DEV check that `NO_DATA` does not start Spark and that a has-data run calls the notebook. This task writes the runbook and stops before that step.
- Reviewer routing: `fabric-pipeline-reviewer` for expressions, pre-check, ForEach, timeout, retry, and failure propagation; `sql-data-reviewer` for the pre-check SQL text; `risk-gate` because risk is high. `spark-runtime-reviewer` only if a notebook file changes.
