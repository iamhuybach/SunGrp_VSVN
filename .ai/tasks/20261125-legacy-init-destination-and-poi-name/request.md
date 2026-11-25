# Request

## User outcome

A one-time legacy init writes `gld_srv_poi_info.destination_id` as one JSON array string of every old-gold destination id, and writes `gld_srv_poi_multi_lang.poi_name` from the matching language. Existing Dev `LEGACY_INIT` rows are repaired the same way. The scheduled pipeline is left unchanged. Prod init is correct on the first run, with no manual fix afterwards.

Reference task `20261119-legacy-gold-poi-init` (`ready_to_merge`) is context only. Do not change its gates or artifacts.

## Scope

### In scope

- `gld_srv_poi_info.destination_id` stays `STRING` when non-`LEGACY_INIT` rows already store a JSON array string. Do not switch the column to `ARRAY` while the current writer and DDL still use a string.
- `NB_SETUP_LEGACY_GOLD_POI`: stop using `get_json_object(destination_ids, '$[0]')`. Persist the whole old-gold id array as one JSON string of strings. A non-string element, or `destination_ids` that is not a JSON array, is not wrapped and the first element is not taken; stop at `user_decision` with the observed shape. If languages of the same old `poi_id` disagree on `destination_ids`, do not pick one; stop at `user_decision`.
- Update existing `LEGACY_INIT` rows. Do not modify rows the pipeline owns.
- Add nullable `STRING` `poi_name` on `gld_srv_poi_multi_lang`. Grain stays `(poi_id, lang)`. Init reads `poi_name` for that row's `lang` from the old-gold name source the notebook already uses. Do not copy the `vi` name onto every language.
- `NB_GLD_SRV_POI_MULTI_LANG` writes `poi_name = null` on both P1 and P2. It must not read a `poi_name` column that `slv_enr_poi_info_multi_lang` does not have. The main MERGE may overwrite an init `poi_name` with null when that row becomes a pipeline row. Record this consequence in `decision.md` before implementation.
- The init notebook takes the target workspace as a parameter. Do not hardcode `sgr_visitvn_dev`. Do not guess the Prod workspace name. The old-gold source keeps the workspace already in the notebook.
- A rerun does not duplicate rows and does not change `poi_id`.
- Update `docs/context/mapping_gld_srv_poi_multi_lang.md` in this task before review.
- Domain: DDL and registry, transform/gold library, init notebook. Touch PostgreSQL only when `tests/test_srv_poi_serving_contract.py` requires the gold column set to match `apps.srv_poi_multi_lang`. Do not add `poi_name` to API JSON unless an api-mapping file already requires it.
- D-06 of `20261119-legacy-gold-poi-init` still governs `poi_name` on `gld_srv_poi_info`. The new column is on `gld_srv_poi_multi_lang` and is per language.
- The sample `["d5a59a94-9237-57cc-87e4-a13866f49b01","511b3979-5a71-5360-acf3-9feaeeea740c"]` is a shape example only. Do not seed those two UUIDs.

### Out of scope

- Gates, decisions, and code changes owned by `20261119-legacy-gold-poi-init`.
- Splitting this work into a new-column task, a Dev-repair task, and a Prod-prep task.
- Fast lane.
- Running Fabric notebooks or `docker compose` from the agent session.
- Reading `notebooks_lgc/` unless the init notebook and the prior `decision.md` do not show where `destination_ids` or per-lang `poi_name` come from.

## Acceptance criteria

- DDL keeps `gld_srv_poi_info.destination_id` as `STRING` when non-`LEGACY_INIT` rows contain a JSON array string, and the live writer plus DDL do not already use an array type.
- Init no longer takes only `$[0]`. The full old-gold id array is stored as one JSON string of strings. Invalid element types or a non-array `destination_ids` stop at `user_decision` with that shape. Conflicting `destination_ids` across languages of one old `poi_id` stop at `user_decision`.
- `gld_srv_poi_multi_lang.poi_name` is nullable `STRING`. Grain remains `(poi_id, lang)`. Init fills the name of that language only.
- `NB_GLD_SRV_POI_MULTI_LANG` sets `poi_name` null on P1 and P2 without reading a missing source column. Pipeline ownership may replace the init name with null. That consequence is in `decision.md` before the edit.
- Target workspace is a parameter. Old-gold workspace stays as already written. Rerun does not insert a second row and does not change `poi_id`.

## Constraints

- One task, one chat, the full `docs/agent-system/WORKFLOW.md` §6 path. Stop only for a Fabric DEV probe, `user_decision`, a CLI or model fallback, a round cap, or `waiting_runtime`.
- `data_model_change` applies because `poi_name` is a new column. Required reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, and `state-correctness-reviewer` (init MERGE and the main MERGE both write `poi_name`).
- If the stored shape of non-`LEGACY_INIT` `destination_id` is not in the repo, write the smallest probe, move to `waiting_evidence`, and stop. The probe counts shapes only, returns no bulk UUIDs, and stays within 50 rows.
- After evidence is sufficient: `handoffs/author-input.md`, `run-author --kind model`, then `run-gate`. Main does not write `model-design.md` or `architecture.md`.
- Implement only the architecture edit list. Record any deviation in `decision.md` before further edits. Save `FILE` blocks with `python scripts/vv.py materialize <task-id> --write`.
- `verify` must pass before `reviewing` and `run-gate`. Fix P0/P1 in this chat inside the round cap.
- Dev repair and Prod init are user-run: `run-author --kind runbook`, then stop at `waiting_runtime`. The runbook takes the target workspace, orders the repair of existing `LEGACY_INIT` rows, and states how to check that `destination_id` is a JSON array string and `poi_name` matches the language. Do not run the notebook on Fabric in this chat.
- On every stop, overwrite `resume.md` (at most 40 lines) and close with `python scripts/vv.py closeout <task-id>`. Do not commit.
- `tests/test_srv_poi_serving_contract.py` `test_gold_and_pg_columns_and_types_match` compares `NB_SETUP_INITIAL_DDL` `TABLE_SPECS` for `gld_srv_poi_*` with `sql/postgres/gld_srv_serve.pg.sql` and, when the service tree is present, with JPA entities. A `TABLE_SPECS` column add fails that test until PostgreSQL matches. API JSON stays unchanged unless an api-mapping file already names `poi_name`.

## Classification rationale

- Complexity: `medium`. New column, two MERGE writers on `poi_name`, and a destination encoding change. Not a fast lane (behavior change and more than two files).
- Risk: `high`. Idempotent rerun, two writers on one column, and the Dev repair / Prod init can be proved only at runtime.
- Architecture: required. New column ownership and the commit that may null an init `poi_name` need an Architect edit list. `data_model_change` requires `model-design.md` before that gate.
- Evidence: required. Repo code shows `slv_enr_poi_destination.destination_id` as `to_json` of the `id` array and `NB_GLD_SRV_POI_INFO` copies it 1-1 into a `STRING` column. No stored sample of non-`LEGACY_INIT` `gld_srv_poi_info.destination_id` values is in the repo. DDL type stays open until the probe counts those shapes.
- Runtime proof: required. The user runs the Dev `LEGACY_INIT` repair and the Prod init from the runbook.
- Reviewer routing: `sql-data-reviewer` (DDL and both MERGEs), `spark-runtime-reviewer` (Fabric notebooks), `state-correctness-reviewer` (init MERGE and main MERGE both write `poi_name`). Risk `high` also requires the risk gate after specialist review.
