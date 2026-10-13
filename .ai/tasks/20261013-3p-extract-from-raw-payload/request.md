# Request

## User outcome

A proposal, not an applied model change, that shows how the 3rd-party extract would behave if it read `raw_payload` from `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` instead of `normalized_payload`.

## Scope

### In scope

- Impact proposal for the nine active silver L1 tables `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_rating`, `slv_3p_poi_amenity`, `slv_3p_poi_review`, and `slv_3p_poi_media`, plus inactive `slv_3p_poi_policy`.
- Rows in `ctrl_cfg_schema_registry` and `ctrl_mng_pipeline_config` whose `json_path`, `src_object`, `load_mode`, `data_type`, or `is_active` would change.
- Consumer columns in silver L2 `slv_poi_*` and in `gld_enr_*` built by `NB_ENR_POI_INFO`, `NB_ENR_POI_COORDINATE`, and `NB_ENR_POI_REVIEW`. List affected target columns only.
- A key-and-type tree of one Google Places object supplied by the user on 2026-10-13. No values.

### Out of scope

- Editing notebooks, DDL, pipelines, registry seeds, schemas, Mapping, or another task's BRD.
- Dropping bronze `normalized_payload`.
- Applying the new mapping.
- Redesigning silver L2 or `gld_enr_*`.
- The partner extract.
- Copying the sample file into the repository.
- Architecture and evidence gates. Those are required before a later apply and are not run in this turn.
- `python scripts/vv.py run-gate`, Codex, and `requirements-analyst`.

## Acceptance criteria

- `decision.md` has one table per `slv_3p_*` table covering keep, change `src_object` or `json_path`, change type, add column, or remove from the registry.
- `decision.md` has one table for `ctrl_cfg_schema_registry` and `ctrl_mng_pipeline_config` rows that change `json_path`, `src_object`, `load_mode`, `data_type`, or `is_active`.
- Every current L1 column with no corresponding key in the sample is `MISSING_EVIDENCE`. Do not record that column as always null.
- New sample keys with no L1 column are listed separately, with a proposed target table or `chưa có chỗ chứa`.
- `poi_id` stays `HASH_MD5_UUID` of `source_name` and `source_id` when both remain derivable from raw. If the sample `id` is not enough to replace `source_id`, record a question and do not invent a formula.
- Each changed or removed column names its consumer table and target column.
- Task status is `user_decision`.
- The proposal and the key tree match the Claude Code return verbatim.

## Constraints

- One sample is not a schema contract. Null `currentOpeningHours` or `regularOpeningHours` in the sample does not mean every place is null.
- Extract only splits structure and casts types. Do not add business rules to the extract proposal.
- Do not drop bronze `normalized_payload` in this turn.
- Do not apply the new model.
- Approved on 2026-10-13: the proposal author is Claude Code, model `claude-opus-5-5`, effort `medium`. This is not an Architect turn. Architect remains `claude-opus-5-5` at effort `high` and writes only `architecture.md` through `run-gate`.
- Do not change model or effort in `.claude/settings.json`.
- Do not commit, push, or merge.

## Classification rationale

- Complexity: high. The source field switch crosses bronze, silver L1, silver L2, and gold enrichment, and the path mapping has material alternatives.
- Risk: high. A wrong path or type changes attributes that downstream tables already read, and the correct shape cannot be proved from the repository alone.
- Architecture: required before a later apply, because target paths, types, and identity inputs change. Not run in this turn.
- Evidence: required before a later apply. One local sample is a shape note, not a completed evidence gate. Not run in this turn.
- Runtime proof: required before a later apply, because registry paths must be checked against Fabric DEV data. Not run in this turn.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, and `fabric-pipeline-reviewer`, plus `risk-gate` because risk is high. Not run in this turn.
