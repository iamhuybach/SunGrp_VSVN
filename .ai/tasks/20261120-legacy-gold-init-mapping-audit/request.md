# Request

## User outcome

The one-time legacy gold init written by `NB_SETUP_LEGACY_GOLD_POI` matches the current gold model and the old-flow notebooks on every column it writes into `gld_srv_*`. `operating_hours` and `holiday_exceptions` are not left null by an unproven expression. Where the old JSON shape is not the input the current rule expects, the task stops and asks for the transform rule.

## Scope

### In scope

- Column-by-column comparison of what `NB_SETUP_LEGACY_GOLD_POI` writes into `gld_srv_*` against the old-flow notebooks and the current model notebooks.
- Fix only columns that mismatch, or that are null because the init transform is wrong.
- `operating_hours` and `holiday_exceptions`, including the two init paths `get_json_object(poi_content_json, $.hours_weekday_text)` and `get_json_object(poi_opening_hours_json, $.holiday_exceptions)`.
- Current-model rules from `docs/context/mapping_gld_srv_poi_info.md` (Google and partner `operating_hours`, and `holiday_exceptions`) and from `NB_SLV_POI_ENTITY_NON_ENRICH` and `NB_GLD_SRV_POI_INFO`.
- Old-flow shape from `notebooks_lgc/3rd_data_ingested_orches/` and `notebooks_lgc/pl_transform_partner_userprofile_cms/`.
- A Fabric DEV probe only when a rule exists and still depends on the DEV JSON shape: null rate and the key tree of the related old field, at most 50 rows, no names or content.
- `model-design.md` through `run-author --kind model` only when a confirmed rule changes a column's meaning, type, or key.
- Architecture and review for this task only.
- A runtime runbook, through `run-author --kind runbook`, when the init notebook must be run again on Fabric.

### Out of scope

- Task `20261119-legacy-gold-poi-init`: no edits, no reopened gates, no reimplementation of D-01 through D-09.
- The "do not load" list in that task's `model-design.md`. Current init notebook and current mapping are the baseline. D-07 requires loading a field that has a source.
- `poi_id`, `load_origin`, map-table grain, pipeline schedule, and the init table list, unless the comparison shows a defect in one of them.
- A new JSON parser when the old gold JSON shape is not the input of the current-model rule.
- Guessed `json_path` values. A key absent from the old notebook and from a probe is `MISSING_EVIDENCE`.
- Serving API, `services/data-serving-service`.
- DDL, unless a confirmed rule requires a column change.
- Fabric DEV execution of the init notebook in this chat.

## Acceptance criteria

- An evidence table lists every column `NB_SETUP_LEGACY_GOLD_POI` writes into `gld_srv_*`. Each row states the init expression, the source in the old-flow notebook, and the rule running in the current model. Matching columns are marked match. Mismatched columns are marked mismatch.
- `operating_hours` and `holiday_exceptions` are not assigned by an unproven path. The two current init paths are in the comparison table.
- The current-model rule is taken from `docs/context/mapping_gld_srv_poi_info.md` and from `NB_SLV_POI_ENTITY_NON_ENRICH` plus `NB_GLD_SRV_POI_INFO`. Gold `operating_hours` is not a raw copy of `opening_hours_text`. Google stops when the hours JSON is not the shape recorded in the mapping. Partner reads the object `$.policies.operating_hours`. Partner `holiday_exceptions` is a JSON string and is not parsed. Google has no entity `holiday_exceptions`, so the task does not invent a value.
- When the old gold JSON shape is not the current rule's input, no new parser is written. Status becomes `user_decision`, naming the field and the JSON keys actually seen, and asking for the transform rule.
- Only mismatched columns, or columns null because of a wrong transform, are changed.
- Rerunning init does not duplicate rows and does not update rows the new pipeline owns.

## Constraints

- One task, one chat, full `docs/agent-system/WORKFLOW.md` §6. No fast lane. No split between an audit task and a fix task.
- Stop only for a Fabric DEV probe, `user_decision`, a CLI or model fallback, a round cap, or `waiting_runtime`.
- Comparison is done before DEV evidence and before code changes. The comparison table is task evidence. A column with no transform rule is a question, then `user_decision`. Do not call the Architect to invent a rule.
- Domain: transform/gold library and the init notebook. DDL only when a confirmed rule requires a column change.
- Reference task `20261119-legacy-gold-poi-init` is `ready_to_merge` (architecture round 2, review round 3, `extra_round_approved_on` 2026-11-19). All edits live in this task.
- Do not infer a `json_path`. Do not read that task's `reviews/` or `docs/context/3p-google/*.txt`.
- The user runs Fabric DEV. This chat does not run the init notebook on DEV.
- No commit unless the user's current turn asks for one.

## Classification rationale

- Complexity: medium. The change is bounded to init column expressions, but the hours fields are not a single `get_json_object` and a wrong assignment leaves historical gold unusable.
- Risk: medium. Rollback is a rerun of the same init notebook under the existing row-ownership guard. Risk becomes high only if the comparison shows a MERGE, `load_origin`, or write-order defect.
- Architecture: required. The task has its own architecture and review. A missing transform rule stops at `user_decision` and is not sent to the Architect.
- Evidence: required. The all-null hours symptom is not a cause. If a rule exists and still depends on the DEV JSON shape, the smallest probe is the null rate and the key tree.
- Runtime proof: required when init SQL changes, because the historical load must be rerun without duplicating rows or touching pipeline-owned rows. The runbook states the rerun and how to see that the two hours columns are no longer null for a transform reason.
- Reviewer routing: `sql-data-reviewer` and `spark-runtime-reviewer`. Add `state-correctness-reviewer` only if the fix changes MERGE, `load_origin`, or write order. Signals expected on this path: `design_tradeoffs`, `data_evidence_required`, `runtime_proof_required`, and `data_model_change` only if a confirmed rule changes a column type or meaning.
