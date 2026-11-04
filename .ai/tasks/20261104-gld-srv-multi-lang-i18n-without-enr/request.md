# Request

## User outcome

A `slv_pn_business_service_i18ns` row with no matching `slv_enr_poi_info_multi_lang` row still produces a `gld_srv_poi_multi_lang` row. Partner i18n text must not disappear from serving only because the enrich multi-lang row is absent. User supplement 2026-11-04, attached to task `20261104-poi-review-src-and-partner-i18n`. This task does not change that task's ledger rows D-SRV-LANG, D-SRV-TEXT, or D-REINIT, and does not change that task's status, gates, `scope.files`, or `resume.md`.

## Acceptance criteria

- A partner row that has only i18n is present in `gld_srv_poi_multi_lang`, with `description` from `bio` and `experience` from `usps`.
- A row that already has `slv_enr_poi_info_multi_lang`, and every non-partner branch, keep the current rule.
- `docs/context/mapping_gld_srv_poi_multi_lang.md` is updated before review.

## Scope

### In scope

- `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb` cell `id:srvmlbuild`: add the partner i18n row that the current left join drops.
- `docs/context/mapping_gld_srv_poi_multi_lang.md`.
- `tests/test_gld_srv_poi_contract.py` assertions that pin `srvmlbuild`.

### Out of scope

- Any edit to task `20261104-poi-review-src-and-partner-i18n`.
- D-SRV-LANG, D-SRV-TEXT, and D-REINIT.
- New gold columns.
- Changing the transform of a row that already matches `slv_enr_poi_info_multi_lang`, including the `bio` / `usps` fallback.
- Driving the non-partner branch from anything other than `slv_enr_poi_info_multi_lang`.
- `docs/context/03_OPERATOR_GUIDE.md` §2.3. It still says `slv_enr_poi_info_multi_lang` is the driving table. Updating it is a later scope change.
- `NB_CREATE_DDL.ipynb` and `NB_SETUP_INITIAL_DDL.ipynb` keep the three existing ctrl edges. D-ML-WRITER adds the `source_name` column on `slv_enr_poi_info_multi_lang` in both DDL notebooks. No notebook writer.

## Current behavior

From `docs/context/mapping_gld_srv_poi_multi_lang.md` and cell `id:srvmlbuild`:

- The row source is `slv_enr_poi_info_multi_lang` LEFT JOIN `slv_poi_entity_non_enrich` on `poi_id`, then a partner LEFT JOIN to `slv_pn_business_service_i18ns` when `poi_id = uuid_md5(business_service_id, 'partner')` and `lang = locale`.
- `required_inputs` are `multi_lang` and `entity`. `i18n` is not required. All three inputs use `live_only=False`.
- Partner: `description` is `bio`, and when `bio` is null, enrich `description`. `experience` is `usps`, and when `usps` is null, enrich `experience`.
- MERGE grain is `(poi_id, lang)`.
- `docs/context/01_DATA_MODEL.md` §8: partner `poi_id` is `uuid_format(md5(concat(<id>, 'partner')))` 8-4-4-4-12. For `slv_pn_business_service_i18ns`, `<id>` is `business_service_id`. `NB_GLD_SRV_POI_MULTI_LANG` already calls `uuid_md5(business_service_id, lit('partner'))`.
- `docs/context/CTRL_TABLES_CONTEXT.md` §3 lists edges for `PL_VV_TRANS_SLV_TO_ENR_15M` and does not list `PL_VV_TRANS_SLV_TO_GLD_30M`. The mapping §1.1 states the three edges `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich`, and `slv_pn_business_service_i18ns` into `gld_srv_poi_multi_lang` on `PL_VV_TRANS_SLV_TO_GLD_30M`, `load_mode = RECOMPUTE`, `priority = 1`, `nb_name = NB_GLD_SRV_POI_MULTI_LANG`. §5 records `slv_pn_business_service_i18ns` key `(business_service_id, locale)`.

## Decided

- One `slv_pn_business_service_i18ns` row with no `slv_enr_poi_info_multi_lang` row matching the partner `poi_id` and `lang = locale` still creates a `gld_srv_poi_multi_lang` row.
- The i18n values kept are the gold columns that already come from i18n: `description` from `bio`, `experience` from `usps`. No new gold column.
- `poi_id` of that row is `uuid_md5(business_service_id, 'partner')`. `lang` is `locale`.
- A row that already has multi-lang keeps the current transform, including the `bio` / `usps` fallback.
- The non-partner branch stays driven by `slv_enr_poi_info_multi_lang`.

## User decisions

Decided by the user on 2026-11-04. The verbatim text is in `decision.md`. Use that text. Do not replace it with a paraphrase.

D-ML-SRC, added the same day: add column `source_name` on `slv_enr_poi_info_multi_lang`. An i18n-only row still uses every locale and `source_name` `partner`. D-ML-NOMATCH is later: `gld_enr_poi_info` keeps `slv_poi_entity_non_enrich.source_name`.

## Constraints

Columns or keys absent from this request and from `decision.md` are `MISSING`. Do not invent them. D-ML-WRITER: this task only adds the DDL column on `slv_enr_poi_info_multi_lang`. The external enrich job is not implemented here. Do not add a notebook writer. D-ML-NOMATCH, later than D-ML-SRC and D-ML-GATE: `gld_enr_poi_info` keeps `slv_poi_entity_non_enrich.source_name`. Do not read the new column from `NB_ENR_POI_INFO`.

## Classification rationale

- Complexity: `high`. The MERGE key set gains partner rows the current left join drops, while matched multi-lang rows and the non-partner branch stay. The six UD rows are now set in `decision.md`.
- Risk: `high`. Signals `stateful_logic` and `idempotency`: MERGE will emit rows it does not emit today.
- Architecture: required. The state owner of those new gold keys changes, and the MERGE commit set changes. Grain stays `(poi_id, lang)`. No new column.
- Evidence: not required. The current transform, partner `poi_id` formula, and i18n key `(business_service_id, locale)` are in the repository. The open items are user choices, not unknown data shapes.
- Runtime proof: not required. The acceptance rule is a deterministic notebook change with local contract checks.
- Signals: `data_model_change`, `stateful_logic`, `idempotency`.
- Reviewer routing: `sql-data-reviewer` (MERGE grain, joins, and the new branch), `state-correctness-reviewer` (idempotent MERGE of keys that used to be absent), `spark-runtime-reviewer` (Fabric notebook node). `risk_level=high` routes `risk-gate` after those specialists. No pipeline JSON change, so no `fabric-pipeline-reviewer`.
