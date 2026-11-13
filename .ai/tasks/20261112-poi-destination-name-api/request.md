# Request

## User outcome

Five POI read APIs match the field changes below, and `destination_name` exists on the silver enrich destination table, gold POI info, and PostgreSQL `apps.srv_poi_info`, copied forward from a column that already exists in DDL or a notebook. One task covers the notebook, gold, PostgreSQL, and API. No notebook or pipeline rerun.

## Scope

### In scope

- Add `slv_enr_poi_destination.destination_name`. The value written into it must be a column that already exists in DDL or a notebook. Do not invent a source or a type.
- Add `gld_srv_poi_info.destination_name` from `slv_enr_poi_destination.destination_name`.
- Add `apps.srv_poi_info.destination_name` from `gld_srv_poi_info.destination_name`, including entity `SrvPoiInfo`.
- `GET /api/v1/pois/{poi_id}/amenities`: do not read and do not return `data[].items[].amenity_label_en` or `data[].items[].amenity_label_vi`. Keep `apps.srv_poi_amenity.amenity_en` and `amenity_vi`.
- `POST /api/v1/pois/compact`: add `data[].destinations` as `{"id": apps.srv_poi_info.destination_id, "name": apps.srv_poi_info.destination_name}`.
- `GET /api/v1/pois/{poi_id}/practical_info`: `data.destinations` is currently `{id}`. Add `name` from `apps.srv_poi_info.destination_name`. Remove `data.business_sector`. Keep `data.business_tags.business_sector`.
- `GET /api/v1/pois/{poi_id}/experiences`: add `data.items[].icon_key` from `keyword` of the selected `apps.srv_poi_multi_lang` row. The table has `experience` and no `keyword` column. Model design must show where `keyword` already lives. Do not add a `keyword` column.
- `GET /api/v1/pois/{poi_id}/reviews`: add `data[].source_name` from `apps.srv_poi_review.source_name`. That column is absent from `sql/postgres/gld_srv_serve.pg.sql`, and `services/data-serving-service/AGENTS.md` forbids it under D-10 of task `20261106-agent-system-unify-api`. This request adds the column only when model design finds `source_name` already on the silver path into `gld_srv_poi_review`. Then add `gld_srv_poi_review.source_name` and `apps.srv_poi_review.source_name`, and edit the forbid line in the service `AGENTS.md`.
- Mapping files in the same task: `docs/context/api-mapping/amenities.md`, `compact.md`, `practical_info.md`, `experiences.md`, `reviews.md`, `docs/context/mapping_gld_srv_poi_info.md`, and the review gold mapping if `source_name` is added.
- `scope.systems`: `poi-serving-api`. Domain: DDL/registry, lib transform/gold, serving API.

### Out of scope

- A new table. Splitting the notebook work from the API work.
- Rerunning a notebook, pipeline, Copy Job, or Fabric probe. There is no data reload.
- `docs/poi-serving-api/`. Continuing task `20261110-serving-poi-read-apis`.
- Credentials or hosts in the repository. The API reads gold only through PostgreSQL `apps.srv_poi_*`.

## Acceptance criteria

- The three `destination_name` columns are in silver DDL, gold DDL, `sql/postgres/gld_srv_serve.pg.sql`, and entity `SrvPoiInfo`. The gold transform reads the silver column.
- The five API JSON contracts match the scope. The mapping files above change in this task.
- `tests/test_enr_poi_contract.py`, `tests/test_gld_srv_poi_contract.py`, `tests/test_srv_poi_serving_contract.py`, and the Java tests of the changed endpoints pass.
- `gates.local_verification` is `pass` only when `python scripts/vv.py verify` runs with Docker.
- `runtime-runbook.md` is written for the `services/data-serving-service` docker compose runtime, and the task stops before the compose step so the user can run it.

## Constraints

- Decisions D-1, D-2, D-3, and D-4 in `decision.md` (2026-11-12) supersede the earlier stop rules for a missing source.
- D-1: `slv_enr_poi_destination.destination_name` is DDL only. No notebook loads it. Type is nullable `STRING`, the same as the other text columns on that table. Gold and `apps.srv_poi_info` still copy the column. Values stay null until a later load exists.
- D-2: `icon_key` reads `keyword` inside the selected row's `experience` JSON. A missing `keyword` yields null. Do not add a `keyword` column.
- D-3: the gold review transform sets `source_name` to the literal `google`, because the source tables belong to the Google flow. Add the column on `gld_srv_poi_review` and `apps.srv_poi_review`, and edit the D-10 forbid line in the service `AGENTS.md`.
- D-4: the amenity label removal and the `practical_info` `data.business_sector` removal are in this task.
- No commit unless the user asks in the current turn.

## Classification rationale

- Complexity: `medium`. Signals `data_model_change`, `cross_system`, `runtime_proof_required`. New columns cross silver, gold, PostgreSQL, and the serving API, and five response contracts change.
- Risk: `medium`. Bounded column passthrough and response-field changes. Rollback is the reverse DDL and code change. No watermark, lock, or CDC change.
- Architecture: required. The change spans DDL, a gold notebook, PostgreSQL, entities, and API DTO files, more than eight source files, and the column moves silver to gold to PostgreSQL.
- Evidence: not required as a Fabric probe. The user forbade notebook, pipeline, Copy Job, and Fabric probes. Source columns must already be in the repository. A missing source stops at model design.
- Runtime proof: required. Local docker compose of `services/data-serving-service` only, user-run, after the runbook. `gates.local_verification` still requires `vv.py verify` with Docker.
- Reviewer routing: `sql-data-reviewer` (Delta DDL and gold column copy), `spark-runtime-reviewer` (gold notebook), `api-contract-reviewer` (`api/` or `dto/` and `gld_srv_serve.pg.sql`), `jpa-performance-reviewer` (entity, and repository or query if the diff touches them). Risk is not `high` or `critical`, so no risk gate.
