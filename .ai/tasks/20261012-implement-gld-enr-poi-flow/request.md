# Request

## User outcome

Fabric DEV can append history rows into `lh_vv_gold.enr.gld_enr_poi_info`, `gld_enr_poi_coordinate`, and `gld_enr_poi_review` every 15 minutes. Partner and third-party rows stay separate. A rerun does not update rows already appended. A new input appends a new row.

## Scope

### In scope

- Create task `20261012-implement-gld-enr-poi-flow`. Do not reopen `20261012-map-gld-enr-poi-tables`.
- Closed rule sources, read only:
  - `docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md` version 18
  - `docs/requirements/20261012-map-gld-enr-poi-tables/BRD.md` version 16
  - `.ai/tasks/20261012-map-gld-enr-poi-tables/decision.md`
  - `.ai/tasks/20261012-map-gld-enr-poi-tables/requirements-analysis.md`, only the `MAIN_CORRECTION 2026-10-12` block as the current source list
- Targets, schema `lh_vv_gold.enr`, Delta, append history, no MERGE, no soft delete:
  - `gld_enr_poi_info`. Grain: one append row per (`poi_id`, `updated_at`).
  - `gld_enr_poi_coordinate`. Grain: one append row per (`poi_id`, `updated_at`).
  - `gld_enr_poi_review`. Grain: one append row per (`review_id`, `updated_at`). Third-party only.
- Current Mapping section 3 sources: `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_review`, `slv_3p_poi_contact`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_pn_business_services`, `slv_pn_business_service_i18ns`, and proposed `lh_vv_silver.dbo.slv_pn_poi`.
- Flow names from Mapping section 2: pipeline `PL_VV_TRANS_SLV_TO_ENR_15P`, orchestrator `NB_00_ORCHES_SLV_TO_ENR_15P`, nodes `NB_ENR_POI_INFO`, `NB_ENR_POI_COORDINATE`, `NB_ENR_POI_REVIEW`, `load_mode` `APPEND`, cadence 15 minutes.
- Partner `poi_id` is computed on `slv_pn_poi` before gold. Gold info and coordinate copy `poi_id`. Gold review copies `slv_3p_poi_review.review_id` and does not hash it again.
- DDL matches every Mapping section 5 column, type, and nullability. Dropped columns stay absent: `description` on info, and `title`, `positive`, `negative`, `response_text` on review. Also absent: `source_review_id`.
- Each Mapping section 5 row has a matching expression in the target notebook, with that row's `context_ref`.
- `created_at` and `updated_at` are assigned on every append.
- Control-table seed for the new flow, in the repository's existing notebook and pipeline locations.
- Vietnamese `runtime-runbook.md`: first run, rerun that appends another row, control-log check, rollback, and forward recovery.

### Out of scope

- Editing the four rule-source files, `docs/templates/`, or `.claude/agents/requirements-analyst.md`.
- `poi_address_enrichment_staging`, `SRC-006`, `SRC-008`, `DS-004`, `DS-008`, `destination_ward_mapping`, and any `ref_*` table. The analyst body under `MAIN_CORRECTION` is not the current source list.
- A new `ref_*` table, and moving these rules onto `slv_poi_*`.
- `row_hash`.
- Changes to `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` and to the partner or third-party extract notebooks.
- Commit, push, or merge.

## Acceptance criteria

- DDL has the Mapping section 5 columns, types, and nulls, and omits the dropped columns named above.
- Each Mapping section 5 row has a notebook expression and that row's `context_ref`.
- `gld_enr_poi_review.review_id` copies `slv_3p_poi_review.review_id`.
- `created_at` and `updated_at` change on every append.
- Re-running the same already appended input does not update the old row. A new input appends a new row.
- `python scripts/vv.py verify <task-id>` passes.
- Review is `PASS`, or no P0 or P1 finding stays open.

## Constraints

User-accepted before implementation. Record them in `decision.md` before the architecture gate:

- Keep schema `lh_vv_gold.enr` and prefix `gld_enr_`.
- Keep `load_mode` `APPEND` even though `docs/context/02_NAMING_CONVENTION.md` §6 does not list it.
- Keep `PL_VV_TRANS_SLV_TO_ENR_15P` and `NB_00_ORCHES_SLV_TO_ENR_15P` even though they diverge from the pipeline and orchestrator patterns.
- Business rules stay on this gold write path. Do not add a `ref_*` table. Do not move the rules to `slv_poi_*` to clear `PLATFORM_VIOLATION`.
- `created_at` and `updated_at` change on every write. Do not use `row_hash`.
- Do not read `destination_ward_mapping`, a `ref_*` table, or `poi_address_enrichment_staging`.
- Do not change `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` or the partner or third-party extract notebooks.
- Do not commit, push, or merge.
- `architecture.md` is written only by `python scripts/vv.py run-gate <task-id>` at `waiting_architecture`.
- Main writes notebooks, DDL, pipeline, and control seed only after architecture verdict `PASS`.
- A platform-convention deviation is written in this task's `decision.md`, in Vietnamese, before the code change.
- `runtime-runbook.md` is Vietnamese.
- Main is Cursor, Grok 4.7 Medium. Architect is Claude Code, `claude-opus-5-5`, effort `high`, through `run-gate` only. Review is Codex, `gpt-5.6-sol`, effort `medium`, through `run-gate` at `reviewing`. Required reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`, then `risk-gate`. Do not call `requirements-analyst`. Do not call a Cursor review subagent. Do not substitute a model if a client falls back.

## Classification rationale

- Complexity: high. The flow adds a proposed silver table, three append-only gold tables, a new pipeline and orchestrator, and business expressions that are local to each gold table. Signals: `stateful_logic`, `idempotency`, `retry_recovery`, `partial_failure`, `transaction_boundaries`, `cross_system`, `design_tradeoffs`, `runtime_proof_required`, `data_evidence_required`, `deep_reasoning_required`.
- Risk: high. Append history, rerun, and control-log recovery can diverge across silver, gold, and control tables. Rollback is straightforward only after the runbook exists.
- Architecture: required. New table grain and keys, logic placed on the gold write path, append instead of MERGE, and a new orchestration structure.
- Evidence: required. Two Mapping inputs are not columns in `notebooks/NB_CREATE_DDL.ipynb` or `docs/context/01_DATA_MODEL.md`: the JSON keys inside `slv_pn_business_services.address` that would fill `slv_pn_poi.ward`, `district`, and `province_name`, and the Vietnamese `locale` literal on `slv_pn_business_service_i18ns`. Every other existing source column cited in Mapping section 5 is present in `TABLE_CONFIGS` or `TABLE_CONFIGS_3P`. `slv_pn_poi` itself is proposed. `best_time_type`, `best_time_from_month`, `best_time_to_month`, and `cost` have an empty source in Mapping section 5.
- Runtime proof: required. Append-on-rerun and control-log behavior cannot be proven from the repository.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`, then `risk-gate` because risk is high.
