# Request

## User outcome

Partner POI rows in `slv_poi_entity_non_enrich` start from a live Vietnamese `slv_pn_business_service_i18ns` row. Serving reviews in `gld_srv_poi_review` are read from third-party `slv_3p_poi_review`, not from `slv_enr_poi_review_multi_lang`. The enrich-review flow is inactive. `time_to_spend`, `best_time`, and `cost_vnd` leave `gld_enr_poi_info`. `cost` stays. User confirmed 2026-11-04.

## Scope

### In scope

- Ctrl edges whose target is `gld_enr_poi_review`: set `is_active = 0` in both `notebooks/NB_SETUP_INITIAL_DDL.ipynb` and `notebooks/NB_CREATE_DDL.ipynb`. Tuple order in setup is `(pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order, nb_name)`. Known edges: `slv_3p_poi_review` and `slv_enr_poi_review_multi_lang` to `lh_vv_gold.enr.gld_enr_poi_review`, `APPEND`, `NB_ENR_POI_REVIEW`, pipeline `PL_VV_TRANS_SLV_TO_ENR_15M`. No DROP. No data delete.
- `gld_enr_poi_info`: remove `time_to_spend`, `best_time`, and `cost_vnd` from DDL, select, and the transform that builds them. Keep `cost`. Notebook `NB_ENR_POI_INFO` cell `id:36415d3b` (`_time_to_spend_text`, `_best_time_text`, `_cost_vnd`). Contract `docs/context/gld_enr_poi_info_review.md`.
- `gld_srv_poi_review`: drop `lang`. Read review rows from `slv_3p_poi_review`. Do not read `slv_enr_poi_review_multi_lang`. Keep the `slv_3p_poi_rating` join for `rating_overall` and `rating_count`. Notebook `NB_GLD_SRV_POI_REVIEW` cell `id:srvrvbuild`. Mapping `docs/context/mapping_gld_srv_poi_review.md`.
- `slv_enr_poi_review_multi_lang`: do not DROP. No notebook under `notebooks/` sets `trg_tbl` to this table. Current in-scope readers are `NB_ENR_POI_REVIEW` (flag input) and `NB_GLD_SRV_POI_REVIEW` (driving input). Inactivate a producer only when no active consumer remains outside the flow inactivated above. There is no in-repo producer edge to inactivate.
- `slv_poi_entity_non_enrich`, partner branch only (`source_name = partner`), in `NB_SLV_POI_ENTITY_NON_ENRICH` cell `id:b1entitybuild` def `_partner`. Google branch unchanged. This branch does not read `slv_3p_poi`, address, contact, or opening hours.
- Docs that state the changed grain or the enrich-review flow: `docs/context/gld_enr_poi_info_review.md`, `docs/context/mapping_gld_srv_poi_review.md`, `docs/context/01_DATA_MODEL.md` (N6 and partner `poi_id`), `docs/context/03_OPERATOR_GUIDE.md` §2.1 and §2.2. Mapping and the enrich contract must be updated before review.
- Contract tests that encode the current columns, edges, or partner join, once implementation starts: `tests/test_enr_poi_contract.py`, `tests/test_gld_srv_poi_contract.py`, `tests/test_initial_ddl_contract.py`, `tests/test_poi_entity_contract.py`.

### Out of scope

- Editing `sql/postgres/gld_srv_serve.pg.sql` in triage. Name it only as impact. Ledger `20261029-pg-ddl-gld-srv-serve` D-LANG: PostgreSQL `apps.srv_poi_review` has no `lang`; that ledger kept gold `lang`. This task drops gold `lang`.
- DROP of `gld_enr_poi_review`, `slv_enr_poi_review_multi_lang`, or any other table. No data delete.
- Google branch of `NB_SLV_POI_ENTITY_NON_ENRICH`.
- Pipeline JSON. `NB_LIB_*` unless a later architecture brief names a library change.
- Mapping `title` or `review_text` onto another `slv_3p_poi_review` column. See the blocker below.

## Acceptance criteria

- Every ctrl edge to `gld_enr_poi_review` has `is_active = 0` in both DDL notebooks.
- `gld_enr_poi_info` has no `time_to_spend`, `best_time`, or `cost_vnd` in DDL, select, or mapping. `cost` remains.
- `gld_srv_poi_review` has no `lang` and does not read `slv_enr_poi_review_multi_lang`.
- Partner branch of `NB_SLV_POI_ENTITY_NON_ENRICH` uses the join direction and coalesce below. Google branch unchanged.
- `docs/context/mapping_gld_srv_poi_review.md` and `docs/context/gld_enr_poi_info_review.md` are updated before review.

## Constraints

Partner branch after the change:

- Driving table: live `slv_pn_business_service_i18ns` (`deleted` null or false) and `locale = 'vi'`.
- Left join live `slv_pn_business_services` on `i18n.business_service_id = svc.id`. A deleted service, or no service row, makes every service-sourced column NULL. A deleted Vietnamese i18n row emits no row. A service with no Vietnamese i18n row emits no row.
- `name = coalesce(i18n.name, svc.name)`.
- `amentities = coalesce(i18n.amentities, svc.amentities)`. Fallback is the whole JSON value. When the i18n block is not NULL, `main_category`, opening hours, and holidays are read from that block, including when an inner key is absent.
- After `primary_type` is known, the three `ref_dictionary_place_type` lookups stay: left join the partner dictionary on `primary_type`, then the two `category_group` steps. Duplicate partner `place_type` stops the node before the join. More than one category, or more than one group, stops the node.
- `phone`, `email`, `business_sector`, `operation_status`, `address`, and `website_urls` exist only on `slv_pn_business_services`. They are NULL when the live service row does not join.
- The old rule "no remaining row means the whole node stops and does not write" is not part of the new request. Do not keep it. If idempotency requires it, record `USER_DECISION` and stop.

Current partner behavior, for contrast only, must not remain: driving table `slv_pn_business_services` inner join live `slv_pn_business_service_i18ns` on `svc.id = i18n.business_service_id` and `locale = 'vi'`; a service without Vietnamese i18n is dropped; if no live service has a Vietnamese row, the node stops and does not write; `primary_type` comes from the service `amentities` JSON; left join `ref_dictionary_place_type` with `is_active = true`, `lower(trim(source_name)) = 'partner'`, and `place_type` equal to `primary_type`; duplicate partner `place_type` stops before the join; category_group step 1 collects `business_category` across every active source for that `place_type`; step 2 runs only when step 1 yields exactly one `business_category`, against the Google dictionary grouped by `business_category`, set of `category_group` other than `Other`.

`poi_id` partner stays `uuid_format(md5(concat(id, 'partner')))` 8-4-4-4-12. For an i18n-driven row the id input is `business_service_id`, which `docs/context/01_DATA_MODEL.md` §8 already treats as the same value as `slv_pn_business_services.id`.

Columns or keys absent from this request are `MISSING`. Do not invent them.

### Review text source

`slv_3p_poi_review` has no `title` and no `review_text`. Registry columns are `review_id`, `poi_id`, `author_name`, `rating`, `text`, `time`, `published_at`. User 2026-11-04, verbatim:

- slv_3p_poi_review.title gán là null
- gld_srv_poi_review.review_text lấy từ slv_3p_poi_review.text

Do not add a `title` column to `slv_3p_poi_review`. Gold `title` is null. Gold `review_text` is `slv_3p_poi_review.text`. Ledger row D-SRV-TEXT.

## Classification rationale

- Complexity: `high`. Signals `data_model_change`, `stateful_logic`, `cross_state_impact`, `idempotency`. The partner branch changes its driving table. Gold columns and a ctrl active flag change.
- Risk: `high`. Ctrl `is_active` and target-column removal change what a rerun writes. Rollback is the prior DDL seed plus a notebook rerun, not a DROP. Not `critical`: the request forbids DROP and data delete.
- Architecture: required. Grain of the partner entity row changes. `gld_srv_poi_review` changes source and drops `lang`. The enrich-review edges change from active to inactive. `gld_enr_poi_info` drops three columns.
- Evidence: not required for this blocker. Column absence is in the repository registry, not an unknown runtime distribution.
- Runtime proof: not required by the acceptance list. Acceptance is repository DDL, notebook SQL, and the two mapping docs.
- Reviewer routing: `sql-data-reviewer` (joins, DDL, grain, MERGE), `state-correctness-reviewer` (ctrl active flag, idempotent rerun, partner rows that disappear), `spark-runtime-reviewer` (notebook build cells). `fabric-pipeline-reviewer` is not routed: pipeline JSON is unchanged. Risk gate is required because risk is `high`.
