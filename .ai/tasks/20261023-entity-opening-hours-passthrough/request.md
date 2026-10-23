# Request

## User outcome

`opening_hours_text` is computed once, on `slv_poi_entity_non_enrich`. `gld_enr_poi_info.opening_hours_text` for a `poi_id` is that silver value, with the same column name, `STRING` type, and column position. One POI is not given opening hours twice.

## Scope

### In scope

- Add nullable `opening_hours_text` (`STRING`) on `lh_vv_silver.dbo.slv_poi_entity_non_enrich`.
- Move the opening-hours formula that `NB_ENR_POI_INFO` cell 3 runs today into `NB_SLV_POI_ENTITY_NON_ENRICH`.
- Pass that column through `NB_ENR_POI_INFO` with no Google/partner branch and no `_partner_hours` call when no remaining gold column uses them.
- Put the new silver column in `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL`.
- Move ctrl edges, and the `NB_00_ORCHES_SLV_TO_ENR_15P` dependency only if architecture changes it, so the entity node recomputes when the hours source changes and gold runs after the entity node.
- Move the hours-formula quality checks to the silver notebook. Gold checks that its value matches the silver column.
- Update `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py`, and the initial-DDL contract test if those contracts assert columns, inputs, or edges.

### Out of scope

- A new gold column, a gold column rename, or a change to the gold `opening_hours_text` type or position.
- A new transform for sources other than the branch that cell 3 already uses.
- A new orchestration tier, pipeline JSON, or `pipelines/*/manifest.json`.
- Removing `slv_pn_business_service_i18ns` from gold while another gold column or changed-key path still reads it.
- Tasks `20261022-enr-landing-and-gld-flags` and `20261022-agent-speed-and-context-review`.
- `notebooks_lgc/` and `docs/context/3p-google/*.txt`.
- The dirty file `docs/context/gld_enr_poi_info_review.md`.

## Acceptance criteria

- `slv_poi_entity_non_enrich` has `opening_hours_text`. Google uses `slv_3p_poi_opening_hours.periods_json`. Partner uses the current `def _partner_hours` (D-17) in `NB_ENR_POI_INFO` cell 3. Any other source keeps the current behavior of that branch. Do not invent a new transform.
- `gld_enr_poi_info.opening_hours_text` equals `slv_poi_entity_non_enrich.opening_hours_text` for the same `poi_id`.
- Remove the Google/partner `when` branch and the `_partner_hours` call from the gold notebook when no remaining gold column uses them.
- Keep the gold column name, `STRING` type, and position. Add no gold column.
- The new silver column is in both `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL`. Setup edits the definition in place. Create adds only a markdown cell `[THÊM 23/10] 20261023-entity-opening-hours-passthrough` and one self-contained patch cell at the end. An `ALTER` that adds a column to an existing table must make that column nullable. No `DROP` of a table.
- The entity node reads `slv_3p_poi_opening_hours` when the Google formula needs it. `slv_pn_business_service_i18ns` is already an entity input.
- Ctrl edges, and the orchestrator when architecture changes them, recompute the entity when the hours source changes, then run gold after the entity. Do not add an orchestration tier.
- Drop the gold edge from `slv_3p_poi_opening_hours` only when no remaining gold column reads that table. Do not drop `slv_pn_business_service_i18ns` from gold while another column still uses it.
- Quality checks for the hours formula live on the silver notebook. Gold only checks that the value matches the silver column.
- The column contract comes from the current `NB_CREATE_DDL` patch cell (`cell 35`, id `enrflagpy`, `INFO_COLS`), not from cell `enrddlpy`.

## Constraints

- The current Google branch is `F.when(google, F.col("oh.periods_json")).when(source == F.lit(PARTNER), F.col("ph.partner_hours"))` with no `otherwise` (`NB_ENR_POI_INFO` cell 3). Partner hours are non-deleted `i18n` rows, `_vi_i18n` (`locale = vi`, `poi_id = uuid_md5(business_service_id, 'partner')`), then `get_json_object(amentities, '$.policies.operating_hours')`. A missing key stays null.
- `i18n` on gold is also used for changed keys (`_vi_i18n(ctx.changed("i18n"))`). Removing `_partner_hours` does not by itself remove that input.
- `02_NAMING_CONVENTION.md` §2.1 point 7 says `ensure_target` adds a new node column and a `NB_CREATE_DDL` patch is not required. This task still requires the patch named above.
- Do not mix a dirty notebook or test from another task into this diff. At triage, `git status` showed only `docs/context/gld_enr_poi_info_review.md` dirty.
- `poi_id` never includes language. Do not use `poi_uid`. Partner `poi_id` on this entity stays the formula N6 and `_partner` already use, not `partner_portal`.

## Classification rationale

- Complexity: `medium`. The formula moves from gold to silver and a column is added. The change is one column and the edges that feed it.
- Risk: `medium`. Gold must keep the same value, type, and position. Rollback is reverting the notebooks; the new silver column is nullable and no table is dropped.
- Architecture: required. Logic moves from gold to silver, and ctrl edges change so the entity recomputes before gold.
- Evidence: not required to start. The formula, the `STRING` contract, and the current null-for-other-sources branch are in the notebooks. Do not infer unseen data shapes. A gate that lacks a fact still gets the smallest probe.
- Runtime proof: required. The patch alters a live silver table and gold must show the passthrough value after a DEV run.
- Reviewer routing: `spark-runtime-reviewer` (both node notebooks), `sql-data-reviewer` (DDL, grain, and the hours expression), `state-correctness-reviewer` (recompute edges and gold-after-entity order). `fabric-pipeline-reviewer` is not routed: pipeline JSON is out of scope. Risk is not `high` or `critical`, so `risk-gate` is not required.
- Signals: `data_model_change`, `runtime_proof_required`.
