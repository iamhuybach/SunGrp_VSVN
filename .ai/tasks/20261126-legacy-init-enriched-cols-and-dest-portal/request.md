# Request

## User outcome

One legacy init run fills six existing gold columns from `ai_enriched_poi`, matched on `(poi_id, lang)` for `story` and `local_tips`. `slv_enr_poi_destination.destination_id` becomes each destination element's `strapi_document_id`, and the element's `id` is stored only as silver `destination_portal_id`. Gold `destination_id` keeps its 1-1 copy from silver, so its values follow the new silver source.

## Scope

### In scope

- `NB_SETUP_LEGACY_GOLD_POI` and `docs/context/mapping_legacy_gold_to_gld_srv.md`: map the six existing gold columns from `ai_enriched_poi`. Other legacy tables stay unread for load.
- `slv_enr_poi_destination`: add `destination_portal_id` in `TABLE_SPECS` and one new patch cell in `NB_CREATE_DDL`. Extract enrichment projects `strapi_document_id` to `destination_id` and `id` to `destination_portal_id`, with matching registry/config. `destination_id`, `destination_portal_id`, and `destination_name` stay JSON array strings in the same element order, including null elements.
- `docs/context/mapping_gld_srv_poi_info.md`: gold `destination_id` is the silver copy after silver changes source. Do not describe `destination_portal_id` on gold.
- Contract tests: `tests/test_initial_ddl_contract.py`, `tests/test_enr_poi_contract.py`, `tests/test_gld_srv_poi_contract.py`, `tests/test_srv_poi_serving_contract.py`.

### Out of scope

- New gold columns, grain changes, and MERGE key changes.
- The `old_address` formula in `NB_GLD_SRV_POI_INFO` (D-OLD-ADDR).
- PostgreSQL, Java, and `docs/context/api-mapping/` for the six gold-only columns and for `destination_portal_id`.
- `notebooks_lgc/`, `docs/poi-serving-api/`, and `services/data-serving-service/` except the serving contract test.
- `pipelines/*.json` unless a later edit touches them.

## Acceptance criteria

- Init writes the six mappings. `story` and `local_tips` match `(poi_id, lang)`. A second init run does not multiply rows.
- `docs/context/mapping_legacy_gold_to_gld_srv.md` documents the six columns. Other legacy tables remain unread for load.
- `TABLE_SPECS` and one new `NB_CREATE_DDL` patch cell add `destination_portal_id`. Extract enrichment and registry/config match the two source keys.
- `docs/context/mapping_gld_srv_poi_info.md` states that gold `destination_id` is copied from silver after the silver source change, and does not describe `destination_portal_id` on gold.
- DDL, extract enrichment, legacy init, and serving contract tests are updated. `test_gold_and_pg_columns_and_types_match` still matches. `destination_portal_id` and the six gold-only columns are exceptions in the right place.
- `python scripts/vv.py verify` is PASS before review. P0/P1 findings are handled within two rounds.

## Constraints

- One task for both changes. Signal `data_model_change` because of `destination_portal_id`.
- The language column name on `ai_enriched_poi` comes from a schema already in the repo. If that schema or the JSON keys are absent, write the smallest probe and stop at `waiting_evidence`. Do not invent the column name.
- `price_level`, `price_min`, and `price_max` keep the current gold types.
- Requirements source is this request. Task `20261126-gld-srv-old-address-price-story` is only the ledger for D-OLD-ADDR and the gold-only scope of the six columns.
- No commit. No Fabric DEV execution by Main. The user runs probes and the runtime runbook.
- Reviewers: `spark-runtime-reviewer` and `sql-data-reviewer`. Add `fabric-pipeline-reviewer` only if `pipelines/*.json` changes.

## Classification rationale

- Complexity: medium. Two notebook behaviors and a new silver column, across extract, DDL, and gold init. Not low: the change is a behavior change and more than two files.
- Risk: medium. Bounded value change with local contract tests and a later runtime runbook. MERGE keys and grain stay as they are. Rollback is a forward rerun from the previous mapping. Not high: no new lock, watermark, or retry protocol, and PostgreSQL/API contracts do not gain columns.
- Architecture: required. Code scope is four notebooks and four contract tests (eight source files), plus two mapping docs. `data_model_change` also requires `model-design.md` before the Architect.
- Evidence: required. Current notebooks, `docs/context/`, `sql/`, and `tests/` do not define `ai_enriched_poi` columns or `poi_address_json` keys. `docs/context/mapping_legacy_ai_product.md` only uses `ai_enriched_poi.source_id`. `notebooks_lgc/` is out of scope and is not a schema source. Gold types for the six columns are already in `NB_SETUP_INITIAL_DDL` `TABLE_SPECS`.
- Runtime proof: required after review PASS, for the init write and the idempotent rerun. Not run in this phase.
- Reviewer routing: `spark-runtime-reviewer` (Fabric notebook and Delta write) and `sql-data-reviewer` (Spark SQL projection, DDL, MERGE match keys). No pipeline JSON, so no `fabric-pipeline-reviewer`. Risk is medium, so no risk gate.
