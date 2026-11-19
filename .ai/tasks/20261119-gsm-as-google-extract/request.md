# Request

## User outcome

Bronze rows with `source_name = 'sgm'` on `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` enter the existing Google third-party extract. `slv_3p_poi.source_name` stays `sgm` or `google` as stored on bronze. Every consumer after `slv_3p_poi` treats a `sgm` row as effective `source_name` `google`, with `poi_id = HASH_MD5_UUID('google', source_id)`. Existing `google` rows keep their `source_name` and `poi_id`.

## Scope

### In scope

- `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` and the existing Google registry and pipeline parameter that selects `sources`. No new extract notebook and no new pipeline.
- Active `DOC` / `DOC_ARRAY` tables `slv_3p_poi_*` only. Do not reactivate a disabled table.
- Consumers after `slv_3p_poi` that filter or write `source_name = 'google'`, including the place-type and amenity dictionaries. No new `source_name = 'sgm'` dictionary rows.
- Mapping docs whose table behavior changes, before review.

### Out of scope

- A separate gold or serving task.
- Java serving API changes unless the gold column set or key changes. A different `source_name` value on gold is not an API change.
- New `json_path` entries for keys that are not already in the Google registry contract.
- `NB_LIB_*` changes unless the extract notebook cannot express the identity rule.

## Acceptance criteria

- `source_name = 'sgm'` is not classified `IGNORED` / `OUT_OF_SCOPE`. The current `sources` default and the pipeline parameter are `google` only.
- Same active `DOC` / `DOC_ARRAY` contract and the same active `slv_3p_poi_*` tables.
- `slv_3p_poi.source_name = 'sgm'` when bronze `source_name` is `sgm`.
- Tables and logic after `slv_3p_poi` see that row as effective `source_name` `google`, including dictionaries that filter `source_name = 'google'`.
- MERGE, watermark, reject, and `crawled_at` ordering keep current semantics. A rerun does not insert a second row.
- A registry key that is JSON null on the supplied `sgm` document is not treated as a missing field. A key that is not in the registry contract does not receive a `json_path`.
- The serving API changes only when the gold column set or key changes.

## Constraints

- `sgm` and `google` are the same business source. Keep one notebook, one registry, and one pipeline.
- Identity is fixed: `slv_3p_poi` stores the bronze `source_name`. Downstream of `slv_3p_poi`, a `sgm` row uses effective `source_name` `google` and the same `poi_id` as `google` for the same `source_id`: `HASH_MD5_UUID('google', source_id)`. Do not create a second `poi_id` from `'sgm'`.
- If that identity hits grain, a MERGE key, or a duplicate count, stop at `user_decision` and name the exact collision before any code change.
- Do not assume `normalized_payload.id` is bronze `source_id`. The extract contract is the bronze columns `source_name` and `source_id` (`RAW_DOC_ID`).
- The supplied document is one shape sample, not a distribution. Record keys and JSON types only.
- No fast lane.

## Classification rationale

- Complexity: high. Signals: `stateful_logic`, `idempotency`, `event_ordering`, `data_evidence_required`, `data_model_change`, `cross_state_impact`, `design_tradeoffs`, `runtime_proof_required`. The `poi_id` hash input for `sgm` changes, and watermark, state, and MERGE stay in the same notebook.
- Risk: high. A shared `poi_id` can update an existing `google` row, including `source_name`, when the same `source_id` exists on both bronze values.
- Architecture: required. The key input changes, and the effective `source_name` is applied after `slv_3p_poi` across entity, dictionary, enrich, and gold filters. The repository pipeline activity passes `sources` = `google`, so the existing pipeline JSON must change with the notebook default.
- Evidence: required. Overlap of `source_id` between `sgm` and `google`, equality of `normalized_payload.id` and bronze `source_id`, and absent versus JSON-null registry keys are not in the repository. One sample does not answer them.
- Runtime proof: required. MERGE, watermark, and rerun behavior of this extract are proven on Fabric DEV, not by the local verifier alone.
- Reviewer routing: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`, `fabric-pipeline-reviewer`. Risk gate after specialist review because risk is high. No API reviewers unless the gold column set or key changes.
