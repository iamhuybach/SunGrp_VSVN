# Request

## User outcome

A draft Mapping (`VSVN-MAPPING-v1`) and a draft Business Requirements Document (`VSVN-BRD-v1`) for three proposed Delta tables that serve the enrichment / data-normalization service:

- `lh_vv_gold.enr.gld_enr_poi_info`
- `lh_vv_gold.enr.gld_enr_poi_coordinate`
- `lh_vv_gold.enr.gld_enr_poi_review`

Each target column has one mapping row. A formula is recorded only when `notebooks_lgc` or `docs/context` states it. Differing sources stay `CONFLICT` with a question. `doc_status` stays `DRAFT`.

## Scope

### In scope

- Canonical task `20261012-map-gld-enr-poi-tables`.
- `docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md`
- `docs/requirements/20261012-map-gld-enr-poi-tables/BRD.md`
- Task state, `request.md`, and `decision.md` for this requirements-only scope.
- On 2026-10-12 the user explicitly requested an agent-system change so two template exceptions are valid: no separate rule table (`TEMPLATE_EXCEPTION_NO_RULE_TABLE`), and blank `src_id` for write-time `created_at` and `updated_at`. Files: `docs/templates/BRD_TEMPLATE.md`, `docs/templates/MAPPING_TEMPLATE.md`, `.claude/agents/requirements-analyst.md`. Platform checks PC-03 and PC-09 stay in force.

### Out of scope

- Notebooks, DDL, pipelines, and schemas.
- Renaming the three tables to `gld_srv_*`.
- The architecture gate and Codex review. The requirements analyst runs only when the user asks for analysis.
- Commit and push.

## Acceptance criteria

- Both filled documents keep the template section names, column names, and evidence values, and contain no `[EXAMPLE]` data rows.
- `name_status` of the three tables is `PROPOSED`.
- `review_id`, `source_review_id`, and `review_updated_at` record the user-stated formulas. A different legacy-notebook formula is a `CONFLICT`.
- `created_at` and `updated_at` are not given the current gold `row_hash` meaning unless a legacy notebook states that rule.

## Constraints

- Prose in the two requirement files is Vietnamese. Table names, column names, and identifiers stay English.
- Legacy logic is `notebooks_lgc`. Current-model logic is `notebooks/` and `docs/context`. Do not merge them into one formula when they differ.
- Do not infer the unit of `rating`, the shape of `poi_types_json`, or the meaning of `created_at` and `updated_at` when the notebook does not state it.

## Answers recorded on 2026-10-12

Version 2 of the Mapping and BRD records the user answers. The source language is Vietnamese only. The enrich flow prepares data so the enrichment service can add languages. The service return path is another task.

Version 3 records the later answers. `created_at` and `updated_at` are assigned on every write. Partner `short_address` is `address.full_address`. Third-party `province_name` is `city`. `review_date` stays `timestamp`. `load_mode` stays `APPEND` and does not merge an existing key. `pl_name` is `PL_VV_TRANS_SLV_TO_ENR_15P`. `nb_name` is `NB_00_ORCHES_SLV_TO_ENR_15P`. The three target tables do not read `destination_ward_mapping` or a `ref_*` table.

Version 5 closes the remaining questions. Duplicate keys are allowed. `destination_name` is `coalesce(city, state_province)`. The info column `rating` keeps that name and reads `rating_overall`. `destination_context`, `opening_hours_text`, and `review_json` follow the latest user samples. Partner rows of the new info columns are NULL. `doc_status` stays `DRAFT`.

## Classification rationale

- Complexity: `high`. The documents compare two notebook lineages and the current model. Signals: `design_tradeoffs`, `deep_reasoning_required`.
- Risk: `low`. This task only adds draft requirement files. It does not change lakehouse data or runtime behavior.
- Architecture: not required for this task. The user limited the scope to the two requirement files and told Main not to run the architecture gate. A later implementation task would need its own architecture decision, including schema `enr` and where business rules live.
- Evidence: not required to publish the draft. Unknown formulas are `MISSING_EVIDENCE` or `CONFLICT` with questions. No Fabric probe is part of this scope.
- Runtime proof: not required.
- Reviewer routing: none. The user told Main not to call Codex review.
