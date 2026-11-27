# Request

## User outcome

One document, `docs/context/mapping_slv_pn_product.md`, maps the legacy partner-product business rules onto the current silver L1 model. The frame matches `docs/context/mapping_gld_srv_poi_info.md`. A gap, a grain or key mismatch, or an open choice stays a question. It is not written as a settled rule.

## Scope

### In scope

- Take business rules only from `docs/context/mapping_legacy_ai_product.md` §1.1–§1.13 and the matching cells of `notebooks_lgc/pl_transform_partner_userprofile_cms/5. nb_prepare_product_for_ingestion.ipynb`.
- Map each current silver table that holds partner product or hotel data to one `##` section: `slv_pn_products`, `slv_pn_product_translations`, `slv_pn_product_attributes`, `slv_pn_product_attribute_translations`, `slv_pn_product_attribute_values`, `slv_pn_product_attribute_value_translations`, `slv_pn_product_variants`, `slv_pn_product_variant_translations`, `slv_pn_product_business_service_relation`, `slv_pn_product_posts`, `slv_pn_product_post_translations`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`.
- Each section states `Lakehouse.schema`, then `### Xử lý`, then `### Field Mapping` with columns `Source Field | Data Type | Transform | Target Field`, then a separate transform section when the rule does not fit the table.
- Every Field Mapping row names a column that exists in `TABLE_SPECS` of `notebooks/NB_SETUP_INITIAL_DDL.ipynb`.
- Record open choices in the document section `Câu hỏi cần chốt` and in the `decision.md` ledger.

### Out of scope

- Do not carry forward as target design: one product row with `variants_json`, joins to `ai_poi` or `ai_enriched_poi`, a hardcoded `destination_id` remap, a translation cache, or any LLM step.
- Do not map Azure OpenAI, `gpt-4.1`, `ENABLE_TRANSLATION`, or `ai_product_translation`. English names come only from a locale translation that already exists on the source. Do not add a name-generation step.
- No gold product table and no product transform notebook. Do not invent a table, column, grain, or key.
- Do not edit notebooks, DDL, pipelines, or tests. Do not commit. Do not run Fabric DEV. Do not run `run-author --kind proposal`. Do not run `run-gate`.

## Acceptance criteria

- `docs/context/mapping_slv_pn_product.md` exists. Each silver table above has one `##` section with `Lakehouse.schema`, `### Xử lý`, and `### Field Mapping`.
- A column or table that is not in `TABLE_SPECS` has no invented Field Mapping row. The legacy rule, the mismatch, and the question are in `Câu hỏi cần chốt`.
- Hotel, and every choice (target grain if it differs from silver L1, `source_id`, destination, NULL price, soft delete), stays in that question section until the user decides.
- The hotel branch of the legacy document is analyzed. Whether hotel is inside the settled mapping scope is an explicit question.

## Constraints

- Domain: partner extract and lib transform/gold. The deliverable is a document. It does not change runtime behavior.
- Current model: partner product is already silver L1, grain one source row, key `id`, written by `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`.
- Problem analysis is `run-author --kind analysis` (`claude-opus-5-5`, effort `medium`) into `problem-analysis.md`. Main does not write that analysis.
- If that analysis returns `EVIDENCE_REQUIRED` or `USER_DECISION`, stop and list each item. A missing JSON shape or a column absent from DDL gets the smallest probe and status `waiting_evidence`.
- After a completed analysis, Main writes the mapping from the analysis and the DDL.

## Classification rationale

- Complexity: `low`. No signal. The change adds one mapping document. It does not change a table, column, grain, key, or runtime behavior.
- Risk: `low`. No behavior change.
- Architecture: not required. No grain, key, state owner, transaction, CDC, watermark, lock, or orchestration change. Open choices stay questions; they are not an implementation selection.
- Evidence: not required at triage. Repository inspection of the named files is the source. A later `EVIDENCE_REQUIRED` from analysis overrides this.
- Runtime proof: not required. No Fabric DEV step.
- Reviewer routing: `required_reviewers` empty. WORKFLOW.md §7 routes specialists for code, SQL, pipeline, and API diffs. This task changes one Markdown file and does not change behavior. `risk_gate` is not required at `risk_level` `low`.
