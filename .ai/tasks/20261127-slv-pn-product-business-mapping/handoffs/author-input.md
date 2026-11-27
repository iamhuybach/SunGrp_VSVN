# Author input — analysis

Verbatim user request: `.ai/tasks/20261127-slv-pn-product-business-mapping/request.md`. Do not narrow it.

## Read only

- `docs/context/mapping_gld_srv_poi_info.md` — heading frame and `### 1.2. Field Mapping` columns only
- `docs/context/01_DATA_MODEL.md` — `### 5.1 Partner`
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` — `TABLE_SPECS` between `BEGIN_INIT_TABLE_SPECS` and `END_INIT_TABLE_SPECS`, blocks `slv_pn_product*` and `slv_pn_hotel*`
- `docs/context/mapping_legacy_ai_product.md` — `### 1.1` through `### 1.13`
- `notebooks_lgc/pl_transform_partner_userprofile_cms/5. nb_prepare_product_for_ingestion.ipynb` — the cell for the legacy rule being cited (cells 1–16)
- `docs/agent-system/WORKFLOW.md` — `## 5. Classification` and `## 7. Review routing` only as context

## Constraints

- Problem analysis only. No solution, no target design, no settled field rule.
- Business rules only. Do not carry as target design: one product row with `variants_json`, joins to `ai_poi` / `ai_enriched_poi`, a hardcoded `destination_id` remap, a translation cache, or any LLM step.
- Do not map Azure OpenAI, `gpt-4.1`, `ENABLE_TRANSLATION`, or `ai_product_translation`. An English name comes only from a locale translation already on the source. Do not add a name-generation step.
- Hotel is `mapping_legacy_ai_product.md` `### 1.6` and notebook cell 15. Describe the branch. Ask whether it is in the settled mapping scope. Until answered, it is a question, not a field rule.
- Current model, as stated by the user: partner product is silver L1, one source row, key `id`, notebook `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`. Tables: `slv_pn_products`, `slv_pn_product_translations`, `slv_pn_product_attributes`, `slv_pn_product_attribute_translations`, `slv_pn_product_attribute_values`, `slv_pn_product_attribute_value_translations`, `slv_pn_product_variants`, `slv_pn_product_variant_translations`, `slv_pn_product_business_service_relation`, `slv_pn_product_posts`, `slv_pn_product_post_translations`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`. The repo has no gold product table and no product transform notebook. Do not invent a table, column, grain, or key. Confirm each name against `TABLE_SPECS` or `01_DATA_MODEL.md` §5.1.
- A JSON shape or column the named files do not show goes to `## Câu hỏi`, with the legacy rule, the mismatch, and the question.
- Open choices stay questions: hotel scope, target grain if it differs from silver L1, `source_id`, destination, NULL price, soft delete.
- Cite a file plus a section or a cell for every fact.
- First non-blank line: `RESULT: PASS`, `RESULT: EVIDENCE_REQUIRED`, or `RESULT: USER_DECISION`.
- `EVIDENCE_REQUIRED`: a JSON shape or a column the legacy rule uses is absent from the named files. Name each gap.
- `USER_DECISION`: a choice blocks stating a current-state fact. The open choices above do not block `PASS`; list them under `## Câu hỏi`.
- `PASS`: current state, gaps, and questions are cited. Do not invent a rule to close them.
