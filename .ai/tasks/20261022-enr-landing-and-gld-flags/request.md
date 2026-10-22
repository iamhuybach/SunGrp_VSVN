# Request

## User outcome

Returned enrich data lands in three silver tables. Gold marks a POI or review that already has a multi-language or destination enrich row, so downstream does not wait for enrich content on gold.

## Scope

### In scope

- DDL only for three landing tables in `lh_vv_silver.dbo`: `slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination`, `slv_enr_poi_review_multi_lang`. No notebook loads those tables.
- `lh_vv_gold.enr.gld_enr_poi_info`: remove `district` and `destination_name` from the contract and from the node processing. Keep `street`, `ward`, `city`, `full_address`. Add existence flags `is_enriched_multi_lang` and `is_enriched_destination`.
- `lh_vv_gold.enr.gld_enr_poi_review`: add existence flag `is_enriched_multi_lang`. Keep the other columns and logic.
- Both `NB_SETUP_INITIAL_DDL` and `NB_CREATE_DDL` in this task. Update `tests/test_initial_ddl_contract.py` when the DDL source changes. Update the INFO and REVIEW lists in `tests/test_enr_poi_contract.py` so they match the node notebooks. Leave the COORD list unchanged.

### Out of scope

- A load notebook for the three landing tables.
- Copying enrich text or address content onto gold.
- A new schema, a new orchestration tier, or a new `UNIQUE` key.
- `gld_enr_poi_coordinate` columns, including its own `district` and `destination_name`.
- Task `20261021-refresh-gld-enr-poi-info`, `notebooks_lgc/`, `docs/context/3p-google/*.txt`, pipeline manifests, and other task artifacts.
- `docs/context/gld_enr_poi_info_review.md` unless the user later asks to update that catalog. It documents the two dropped columns. No other runtime reader of `gld_enr_poi_info.district` or `gld_enr_poi_info.destination_name` was found in notebooks, tests, SQL, or JSON.

## Acceptance criteria

- Landing columns and nullability match the locked list. The review landing table has `description` corrected from the typed `descrption`, and it has no `lang` column. `created_at` and `updated_at` are nullable `TIMESTAMP`, the same type as `gld_enr_poi_info`. No `UNIQUE` and no composite key beyond the stated `NOT NULL`.
- `is_enriched_multi_lang` on info is true when `poi_id` has at least one row in `slv_enr_poi_info_multi_lang`, otherwise false. `is_enriched_destination` is true when `poi_id` has at least one row in `slv_enr_poi_destination`, otherwise false.
- `is_enriched_multi_lang` on review is true when `review_id` has at least one row in `slv_enr_poi_review_multi_lang`, otherwise false.
- An unmatched `poi_id` or `review_id` is false. Flags do not depend on landing grain.
- Setup edits the empty-environment definition in place. Create appends one markdown `[THÊM dd/mm] <task-id>` and one self-contained patch cell at the end. Old Create cells stay unchanged. No `DROP` of a table that has data. Columns added to an existing gold table are nullable on `ALTER`. The notebook writes true or false when it runs.
- The patch cell and the runbook state how to remove `district` and `destination_name` on an environment that already has the table. No silent `DROP COLUMN`.
- The info column contract is the current `INFO_COLS` patch cell in `NB_CREATE_DDL` (cell `enrinfopy`), which still contains `district` and `destination_name`. Cell `enrddlpy` is the old info contract. `REVIEW_COLS` still lives only in cell `enrddlpy` because no later patch replaces it.
- Gold node notebooks read the landing tables when computing flags. A ctrl or orchestrator edge is added only when architecture requires it so flags refresh after a new landing row. No new orchestration tier.
- Another consumer of `gld_enr_poi_info.district` or `.destination_name`: list the file and stop at `user_decision`. Do not edit it in this task.

## Constraints

- Domain: lib transform/gold and DDL/registry. One task, one chat, through model, architecture, implement, review, and runtime.
- Prefix `slv_enr_` is not in naming §1. The user locked the table names. Use `lh_vv_silver.dbo.slv_enr_*`.
- Landing grain and unique key are not locked. Do not choose a key. If `UNIQUE` is required for `MERGE` or to prevent duplicates and the repo does not answer it, stop at `user_decision` with each option.
- Gold column contract comes from the current Create patch, not from cell `enrddlpy` info columns.
- Missing evidence at any gate: smallest probe, then `waiting_evidence`. Do not invent data characteristics.

## Classification rationale

- Complexity: medium. New silver tables, dropped gold columns, and derived flags. Signals: `data_model_change`, `cross_state_impact`, `idempotency`, `runtime_proof_required`, `design_tradeoffs`.
- Risk: medium. Bounded column and flag change. Rollback is the runbook. Not high: no new concurrency, watermark owner, or cross-system write.
- Architecture: required. Gold gains a read of new silver tables, column removal is a state change, and a ctrl edge is a real trade-off architecture must accept or reject.
- Evidence: not required to start. The column contract is in the notebooks. Flags are key existence, not a distribution. Uniqueness of landing rows is a user decision if a later gate needs a key, not a Fabric probe.
- Runtime proof: required. Existing gold tables need an explicit patch and column-removal steps. The node must write true or false on a real run.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`. No `fabric-pipeline-reviewer` unless architecture changes pipeline JSON. No risk gate at medium risk.
