# Request

## User outcome

One new silver table, prefixed `slv_3p_poi_amenity_`, holds one row per grouped amenity value built from `lh_vv_silver.dbo.slv_3p_poi_amenity.source_flags_json`. The group name is the key. The amenity token is the value. `poi_id` is copied from `slv_3p_poi_amenity`. Rerunning the same input does not duplicate a key.

## Scope

### In scope

- Source column is `slv_3p_poi_amenity.source_flags_json`. The three samples are examples of the grouped result, not the source payload.
- Group that JSON with `docs/context/3p-google/poi_amenity_mapping.md` and `docs/context/3p-google/get_amenity.md`. A row key is the group name. A row value is one amenity token in that group. The user example is group `general_amenities` with values `gym` and `parking`.
- Apply a documented rule only when its source key is present in the proven JSON. Rules for `amenities[]` strings such as `gym`, `pool`, `spa`, `wifi`, `restaurant`, and `bar` stay `MISSING_EVIDENCE`.
- `true` emits a value. `false` and `null` emit no row. A group with no emitted values emits no row.
- After architecture `PASS`, Main adds the silver notebook, DDL, and any `ctrl_cfg_schema_registry` or `ctrl_mng_pipeline_config` rows.
- Idempotent reload on the same input.
- Vietnamese `runtime-runbook.md` for the Fabric DEV transform, rerun, row-count check, and rollback.

### Out of scope

- Changes to `gld_enr_*` or the partner flow.
- `DROP` of `slv_3p_poi_amenity`.
- A new `poi_id`.
- Sector filtering, including `detect_category`, unless the source amenity table already has a sector column.
- Merging a sample display tag such as `Restaurant`, `Bar`, `Gym`, `Free Wi-Fi`, or `Spa & Wellness` into the formula when no proven source key maps to it.
- Requirements-analyst.
- `terms_and_conditions`, including an empty enum, the value `NONE`, or a long description string.

## Acceptance criteria

- The source column is `slv_3p_poi_amenity.source_flags_json`.
- One `poi_id` plus one true amenity produces one row: group name as the key, amenity token as the value. `false` and `null` produce no row. A group with no values produces no row.
- Where a proven rule emits `parking` into `general_amenities`, the table contains that pair. Sample tags with no proven source key are not required rows.
- `poi_id` is copied from `slv_3p_poi_amenity`.
- The same input run again does not duplicate a key.
- `python scripts/vv.py verify <task-id>` passes before review.
- Review has no open P0 or P1.

## Constraints

- Main is Cursor, Grok 4.7 Medium. Architect is Claude Code, `claude-opus-5-5`, effort `high`, and writes `architecture.md` only through `python scripts/vv.py run-gate`.
- Review is Codex, `gpt-5.6-sol`, effort `medium`, through `run-gate`, with `sql-data-reviewer`, `spark-runtime-reviewer`, and `state-correctness-reviewer`.
- Do not switch models on a client fallback. Stop and report it.
- Apply a markdown rule only when its source column is present on `slv_3p_poi_amenity` or inside JSON that evidence has shown. Otherwise record `MISSING_EVIDENCE`.
- An empty `enum` is not the boolean value `false`.
- No commit, push, or merge.

## Classification rationale

- Complexity: high. New grain and key, idempotent write, and the sample shape does not match the registry column or the documented bronze groups.
- Risk: medium. The new table is a keyed silver projection. It does not append a history of `slv_3p_poi_amenity` and does not overwrite that table. Raise risk to high if architecture chooses append history or an in-place overwrite.
- Architecture: required. New table, grain, and key.
- Evidence: required and satisfied for the source column. P01 and P02 show `source_flags_json` holds boolean flags and option objects, not a prebuilt `enum`.
- Runtime proof: required after implementation, for the Fabric DEV transform, rerun, count check, and rollback.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`. `risk-gate` only if risk becomes high.
