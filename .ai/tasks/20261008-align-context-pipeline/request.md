# Request

## User outcome

Context documents describe the lock behavior in `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` and the activities in `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/`. The pipeline activity name is `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`.

## Scope

### In scope

- Correct lock, edge-watermark, and missing-function claims in the context pack so they match the transform notebook.
- Rename only the TridentNotebook activity `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` to `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`.
- Correct pipeline routing, parameters, timeout, and the 3rd-party call path so they match that JSON.

### Out of scope

- Changing `notebookId`, parameters, dependencies, ForEach, or pre-check logic.
- Implementing `LOCK_EXPIRES_AT` in the notebook.
- Adding a Switch or a 3rd-party notebook activity.

## Acceptance criteria

- The activity name in the pipeline JSON is `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, and `notebookId` is unchanged.
- Context no longer says the current notebook stores `LOCK_EXPIRES_AT` or that this pipeline has a Switch.
- `python scripts/vv.py verify` passes.

## Constraints

- Smallest pipeline edit. Do not change `logicalId` or `objectId` (this export has neither on the activity).
- Keep historical row counts labeled as logs through 05/10/2026.

## Classification rationale

- Complexity: low. Documentation corrections plus one activity rename.
- Risk: low. `notebookId`, parameters, and dependencies stay the same, so the Fabric notebook that runs does not change.
- Architecture: not required. No grain, lock implementation, or activity graph change.
- Evidence: not required. The notebook source and pipeline JSON are in the repository.
- Runtime proof: not required for the repository edit. Deploying the pipeline to Fabric remains a user action.
- Reviewer routing: `fabric-pipeline-reviewer`, because a pipeline artifact changes.
