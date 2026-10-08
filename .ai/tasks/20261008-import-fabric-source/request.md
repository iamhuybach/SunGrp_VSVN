# Request

## User outcome

The Fabric notebooks and the bronze-to-silver pipeline export are stored in the repository under stable paths, byte-for-byte as supplied.

## Scope

### In scope

- Copy six Fabric notebooks into `notebooks/`.
- Copy `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json` and its template `manifest.json` into `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/`.

### Out of scope

- Rewriting notebook or pipeline logic.
- Converting exports into Fabric Git item folders (`.Notebook/`, `.DataPipeline/`).
- Deploying to Fabric DEV or changing control-table data.

## Acceptance criteria

- Each supplied file exists at the path listed in `task-state.yaml` `scope.files`.
- Notebook JSON and pipeline JSON parse.
- File contents match the supplied exports.

## Constraints

- Do not invent schemas, keys, or control-table semantics.
- Do not commit secrets or personal data. The supplied files were scanned; the only `token` match is a local variable name in order-parsing code.

## Classification rationale

- Complexity: low. This task copies existing artifacts and does not change their logic.
- Risk: low. Repository import does not change a running Fabric workload.
- Architecture: not required. There is no grain, ownership, orchestration, or transaction design choice. The eight-file architecture trigger applies to an implementation change, and this task does not author one.
- Evidence: not required. Correctness is file identity, which local comparison can prove.
- Runtime proof: not required. Nothing is executed in Fabric.
- Reviewer routing: none. No authored behavior for specialist review.
