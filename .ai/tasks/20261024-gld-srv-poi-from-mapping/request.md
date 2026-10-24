# Request

## User outcome

One task creates two gold serving tables from the two mapping files: `lh_vv_gold.dbo.gld_srv_poi_multi_lang` and `lh_vv_gold.dbo.gld_srv_poi_info`. Gold reads enriched POI attributes and the enriched address, then transforms opening hours. Those two tables are the external product. Silver does not recompute them.

## Scope

### In scope

- `gld_srv_poi_multi_lang` per `docs/context/mapping_gld_srv_poi_multi_lang.md` §1.1 and §1.2.
- `gld_srv_poi_info` per `docs/context/mapping_gld_srv_poi_info.md` §1.1, §1.2, §1.3, and each case in §1.4.
- Lakehouse.schema `lh_vv_gold.dbo`. Neither table goes in schema `enr`.
- Columns and transforms only from those two mapping files. `is_verified` and `is_bookable` are null. `created_at` and `updated_at` are system timestamps.
- Where `docs/context/01_DATA_MODEL.md` §7 disagrees on columns or sources, the two mapping files win. Do not create `gld_srv_poi_registry` or `gld_srv_poi_destination_membership`.
- New node notebooks `NB_GLD_SRV_POI_MULTI_LANG` and `NB_GLD_SRV_POI_INFO`. One notebook, one target table. No extra orchestration tier.
- DDL in both `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL`. Setup edits the definition in place. Create appends one markdown `[THÊM dd/mm] <task-id>` and one self-contained patch cell at the end. No `DROP` of either table.
- `operating_hours` is STRING and follows §1.3, matching the JSON of each §1.4 case.
- If a named source lacks a mapping column, do not add that silver column and do not drop the gold column.
- Update `tests/test_initial_ddl_contract.py` because §2.1 requires the initial-DDL contract test to track a new `TABLE_SPECS` entry.

### Out of scope

- Attaching either table to `PL_VV_TRANS_SLV_TO_ENR_15P`. The mapping does not say to.
- A new orchestration tier.
- Adding silver columns or dropping gold columns to paper over a mapping gap.
- Rewriting the multi-lang join from `poi_id` to `business_service_id` unless the user says so.
- `notebooks_lgc/`, `docs/context/3p-google/*.txt`, pipeline manifests, and other tasks' artifacts.

## Acceptance criteria

- The two notebooks exist under the target-table names above, one target each.
- Both DDL notebooks contain the two gold tables. Setup changes the in-place definition. Create only appends the dated markdown and one idempotent patch cell. Neither notebook drops a table.
- `operating_hours` matches §1.3 and the JSON of each §1.4 case, type STRING.
- A source column missing from the repo spec is not invented on silver, and the mapped gold column is not removed.

## Constraints

- Domain: lib transform/gold and DDL/registry.
- Signal: `data_model_change`.
- D-SRV-10 through D-SRV-22 are recorded. Info grain is `poi_id`. Duplicate destination rows keep the greater `updated_at`. `pl_name` is `PL_VV_TRANS_SLV_TO_GLD_30P`. Equal or null `updated_at` is unspecified.
- Do not invent data properties. A missing runtime shape becomes the smallest probe and a stop.

## Classification rationale

- Complexity: medium. New gold grain and keys, a contradictory hours transform, and DDL in two notebooks. Bounded to two new tables.
- Risk: medium. New serving tables only. No drop of existing tables. Rollback is a runbook concern, not an in-place overwrite of silver.
- Architecture: required. Grain, key, gold commit, and several file-backed implementation forks change. `data_model_change` requires `model-design.md` before the Architect.
- Evidence: required. D-SRV-18 asks for a partner hours rule. The repo only has the path `$.policies.operating_hours`. The JSON shape is not in the named files.
- Runtime proof: required. The notebooks and DDL must be run in Fabric DEV. Local checks can cover the §1.4 JSON cases after the hours choices are fixed.
- Reviewer routing: `sql-data-reviewer` (DDL, joins, types, grain, and the write match once Q10 chooses MERGE or APPEND), `spark-runtime-reviewer` (Fabric notebooks and Delta writes), `state-correctness-reviewer` (commit and rerun). No `fabric-pipeline-reviewer`: no pipeline attachment. Risk is medium, so no risk gate.
