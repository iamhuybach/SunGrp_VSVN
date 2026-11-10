# Request

## User outcome

Keep the current amenity string as `amenity_en`, store the snake_case of that string in `amenity`, and carry both columns from the silver dictionary through gold into `apps.srv_poi_amenity`.

`GET /api/v1/pois/{poi_id}/amenities` stays (D-02). Remove the `lang` query. The response tree is the D-01 sample in `decision.md`: `data[].amenity_group` plus `data[].items[]` with `amenity_code`, `amenity_label_en`, `amenity_label_vi`, and `service_flags`.

## Scope

### In scope

One task for the silver dictionary, `slv_poi_amenity`, gold, PostgreSQL DDL, and the serving API.

- `lh_vv_silver.dbo.ref_dictionary_amenities`: add `amenity_en`. Its value is the current `amenity` string. Change `amenity` to the snake_case of that current string.
- `slv_poi_amenity` stays in this task because `gld_srv_poi_amenity` is a 1-1 copy of it.
- `lh_vv_gold.dbo.gld_srv_poi_amenity`: add `amenity_en` from `ref_dictionary_amenities.amenity_en`. Take `amenity` from `ref_dictionary_amenities.amenity`. The gold table is dropped and initialized again because the dictionary changed. The agent does not DROP on Fabric.
- `apps.srv_poi_amenity`: drop the table and create it again with `amenity_en`. The user runs the Copy Job. The agent does not run the Copy Job and does not DROP on PostgreSQL.
- API path stays `GET /api/v1/pois/{poi_id}/amenities` (D-02). Remove the `lang` parameter. The response tree is the D-01 sample.
- Earlier response lines, kept as the column sources for the D-01 field names:

```text
- data[].amenity_group[].amenity_code lấy từ apps.srv_poi_amenity.amenity
- data[].item[].amenity_code[].amenity_label_en lấy từ apps.srv_poi_amenity.amenity_en
- data[].item[].amenity_code[].amenity_label_vi lấy từ apps.srv_poi_amenity.amenity_vi
- data[].item[].service_flags lấy từ apps.srv_poi_amenity.amenity_vi
- Bỏ data[].amenity_vi và data[].items[]
- Bỏ data[].amenity_vi và data[].items[].amenity_label
```

- Update `docs/context/mapping_gld_srv_poi_amenity.md` in this task before review.
- The later runbook records DROP gold, re-init, DROP `apps.srv_poi_amenity`, and the Copy Job for the user to run.

### Out of scope

- A separate task for silver, gold, PostgreSQL, or the API.
- Agent execution of Fabric, DROP, Copy Job, or docker compose.
- Reading `docs/poi-serving-api/`.
- Fast lane.
- Extra snake_case rules for diacritics, spaces, or Vietnamese when the code and seed do not already have them.

## Acceptance criteria

- `amenity_en` keeps the current `amenity` string. The new `amenity` follows U-1: option B (option A plus camelCase split, `servesWine` → `serves_wine`) and letters like `é` in `Café` become `e`.
- `gld_srv_poi_amenity.amenity_en` and `amenity` come from those two ref columns. Do not change grain or keys on your own.
- `sql/postgres/gld_srv_serve.pg.sql`, the JPA entity, and the gold DDL match, including `amenity_en`.
- The API path stays `GET /api/v1/pois/{poi_id}/amenities`. There is no `lang` query. The JSON matches the D-01 sample. Contract tests stay green.
- Same task. Do not split silver, gold, PostgreSQL, or the API.
- `mapping_gld_srv_poi_amenity.md` is updated in this task before review.

## Constraints

- Signal `data_model_change`. The current ref key includes `amenity`, so changing `amenity` values changes the key.
- Do not read `docs/poi-serving-api/`.
- Do not run Fabric, DROP, Copy Job, or docker compose.
- D-01 and D-02 are closed in `decision.md`. The path is unchanged. `lang` is still removed.

## Classification rationale

- Complexity: high. The dictionary column and key value change crosses silver, gold, PostgreSQL, and the API, in more than eight files, and changes API behavior. Fast lane does not apply.
- Risk: high. A new `amenity` value is a key change on a table gold copies 1-1, then PostgreSQL and the API. Fabric DROP, re-init, and the Copy Job are runtime-only proof.
- Architecture: required. The ref key includes `amenity`. The change also spans silver, gold, PostgreSQL, and the serving API.
- Evidence: not required. Current amenity strings and any snake_case rule come from repository code and seed. No Fabric probe.
- Runtime proof: required. The runbook, written after implementation, tells the user to DROP gold, initialize again, DROP `apps.srv_poi_amenity`, and run the Copy Job.
- Reviewer routing: `spark-runtime-reviewer` for the notebook DDL and builds; `sql-data-reviewer` for Delta DDL, grain, keys, and PostgreSQL SQL; `api-contract-reviewer` for the path, DTO JSON names, removal of `lang`, and the gold contract tests; `jpa-performance-reviewer` for the amenity entity and service. `risk_gate` follows risk high. No pipeline JSON, so no `fabric-pipeline-reviewer`. No security-surface files, so no `app-security-reviewer`. No CDC, watermark, lock, or retry change is in the request, so no `state-correctness-reviewer`.
