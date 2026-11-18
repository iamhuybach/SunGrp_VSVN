# Request

## User outcome

`slv_poi_amenity` and `gld_srv_poi_amenity` rows for one POI carry the same `poi_id` that `gld_srv_poi_info` stores for that POI.

## Scope

### In scope

- Compare the `poi_id` space of `NB_SLV_POI_AMENITY`, `NB_SLV_POI_ENTITY_NON_ENRICH`, and `NB_GLD_SRV_POI_INFO`.
- Record one cause in `decision.md` before any code change.
- If the repository does not show the cause, the smallest Fabric DEV probe: how many amenity `poi_id` values are on `gld_srv_poi_info`, and how many are not.
- After a single chosen fix: align code, `docs/context/mapping_gld_srv_poi_amenity.md`, and `tests/test_poi_amenity_contract.py`; verify; review with `sql-data-reviewer` and `spark-runtime-reviewer` (add `state-correctness-reviewer` only if the MERGE key or write order changes); write `runtime-runbook.md` and stop before the Fabric DEV rerun.

### Out of scope

- Changing the grain of `slv_poi_amenity` or `gld_srv_poi_amenity`.
- Changing the amenities JSON API.
- A third `poi_id` formula beyond `uuid_md5(id, 'partner')` and `HASH_MD5_UUID(source_name, source_id)`.
- `notebooks_lgc/`.
- Task `20261116-srv-poi-info-is-active`.
- Running a Fabric notebook, copying credentials or hosts, or inferring row counts.
- Commit, push, or merge.

## Acceptance criteria

- `decision.md` states one cause, with file and cell.
- Code, `docs/context/mapping_gld_srv_poi_amenity.md`, and `tests/test_poi_amenity_contract.py` match the chosen fix.
- `python scripts/vv.py verify` passes. No Fabric notebook run belongs to this task.
- Reviewers: `sql-data-reviewer` and `spark-runtime-reviewer`. Add `state-correctness-reviewer` if the MERGE key or write order changes.

## Constraints

- One task. Do not stop after triage when the repository already shows the cause.
- Two different fixes: record both and do not choose.
- `data_model_change` and `run-author --kind model` only if the `poi_id` formula changes.
- Main model must be Grok 4.7 Medium unless an approved `exceptions` entry says otherwise.
- Samples at most 50 rows and no personal data.

## Classification rationale

- Complexity: medium. The id contract crosses `slv_poi_amenity`, `gld_srv_poi_amenity`, and `gld_srv_poi_info`. Two later repairs are possible, so this is not a fast lane.
- Risk: medium. A later repair changes which amenity rows stay live. Rollback is a RECOMPUTE rerun. No data-loss path is chosen in this phase.
- Architecture: required after evidence, because more than one repair has a material trade-off. Not run in this phase.
- Evidence: required. The repository shows the id spaces and does not show a formula mismatch or which population gap is present.
- Runtime proof: not required yet. A runbook is written only after a code change, and the Fabric DEV step stays with the user.
- Reviewer routing: `sql-data-reviewer` and `spark-runtime-reviewer` for the amenity build. `state-correctness-reviewer` stays off until a MERGE key or write order changes.
