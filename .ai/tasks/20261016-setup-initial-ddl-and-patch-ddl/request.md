# Request

## User outcome

VSVN is not in production. An operator can build an empty environment in one manual run from the DDL and configuration inserts already defined in the repository. After that, each new DDL or configuration-insert request patches only the new change on an environment that already has the tables. Agents follow that split on every later request.

## Scope

### In scope

- One manual first-run notebook that contains the full current DDL and configuration `INSERT` definitions from the repository, excluding `notebooks_lgc/`.
- `notebooks/NB_CREATE_DDL.ipynb` remains the patch notebook. New DDL or configuration `INSERT` requests are added there so they can run where the tables already exist.
- An agent-facing rule: a new DDL or configuration `INSERT` request must update both notebooks. The first-run notebook keeps the complete definition used to build an empty environment. `NB_CREATE_DDL` contains only the new change and must run against the existing environment.
- `docs/context/02_NAMING_CONVENTION.md`: one section that assigns those two roles. `AGENTS.md` currently says `NB_CREATE_DDL` creates the control tables; that sentence must stay consistent with the split.
- One new DDL change, for example an added column, present as a patch cell in `NB_CREATE_DDL` and as the full definition in the first-run notebook. User decision U1 selects the existing column `ctrl_mng_pipeline_config.nb_name`. Do not add a new column.
- `lh_vv_silver.dbo.slv_poi_amenity` and `lh_vv_silver.dbo.slv_poi_entity` are part of the first-run inventory. Sources: task `20261016-ref-amenities-poi-amenity` (`notebooks/NB_SETUP_POI_AMENITY.ipynb`) and task `20261016-ref-place-type-poi-entity` (`notebooks/NB_SLV_POI_ENTITY.ipynb`, cell `b1entitybuild`). `slv_poi_amenity` is already architecture §5.1 row 13. `slv_poi_entity` is not in that inventory and must be added from the repository definition. Do not invent columns.

### Out of scope

- `notebooks_lgc/`.
- Replacing `NB_CREATE_DDL` with a copy of the first-run notebook.
- Restoring `DROP` cells that have already been removed from `NB_CREATE_DDL`.
- `DROP` of tables that already hold data, in the first-run notebook.
- Configuration seeds taken from live Fabric tables (`INSERT … SELECT` against the running environment).
- Pipeline JSON, and any edit to extract or recompute notebooks. Their existing table definitions are sources for the first-run notebook. Control-table behavior stays limited to the DDL and configuration seeds already defined in the repository.

## Acceptance criteria

- The first-run notebook has `p_apply` defaulting to `false` and prints the DDL list and the configuration `INSERT` row counts before it writes.
- `p_apply = true` on an empty environment creates the full table set and seeds. Running it again does not duplicate configuration rows.
- `NB_CREATE_DDL` is not replaced by a copy of the first-run notebook. `DROP` cells already removed from `NB_CREATE_DDL` are not put back.
- `docs/context/02_NAMING_CONVENTION.md` has a section that assigns the two notebook roles.
- A new DDL change, for example an added column, appears as a patch cell in `NB_CREATE_DDL` and as the full definition in the first-run notebook. U1 is satisfied by the existing `ctrl_mng_pipeline_config.nb_name` pair, with no new column.
- The first-run notebook creates `lh_vv_silver.dbo.slv_poi_amenity` and `lh_vv_silver.dbo.slv_poi_entity` from the definitions already in the two 2026-10-16 tasks named above.

## Constraints

- Seeds come from definitions already in the repository, not from `INSERT … SELECT` against Fabric.
- Do not invent a business column, key, or seed row that the repository does not already define. If the required example change has no already-specified column, the architecture must stop for a user decision instead of choosing one.
- The first-run notebook must not `DROP` tables that already contain data.
- `p_apply` behavior should follow the existing manual-setup pattern in `notebooks/NB_SETUP_POI_ENTITY.ipynb` (default `false`: print the plan, then exit without writing).
- Name the first-run notebook with the existing `NB_SETUP_*` role. Do not rename `NB_CREATE_DDL`.

## Classification rationale

- Complexity: `high`. Signals: `idempotency`, `partial_failure`, `design_tradeoffs`, `runtime_proof_required`. A rerun must not duplicate configuration rows; a multi-statement apply can stop midway; the full definition and the patch notebook are two viable shapes with different failure behavior; empty-environment proof cannot be done from the repository alone.
- Risk: `high`. Idempotent writes of control configuration, and proof that exists only at runtime, match the high-risk criteria. The no-`DROP` constraint keeps this below `critical`.
- Architecture: required. Material trade-offs remain: which statements belong in the full inventory, how a rerun stays idempotent after a partial apply, where the agent rule is stored without breaking the `AGENTS.md` size limit, and which already-defined column (if any) demonstrates the dual update. This is not a fast lane: more than two files change, and the notebook writes tables and seeds.
- Evidence: not required. Current DDL and seeds are in the repository. Live Fabric contents must not be used as the seed source.
- Runtime proof: required. Acceptance includes `p_apply = true` on an empty environment and a rerun that does not duplicate configuration rows.
- Reviewer routing: `sql-data-reviewer` (DDL, seed statements, deterministic rerun), `spark-runtime-reviewer` (Fabric notebook contract, `p_apply`, apply and exit), `state-correctness-reviewer` (durable control-row idempotency and partial apply). No pipeline reviewer. Risk gate runs because risk is `high`.
