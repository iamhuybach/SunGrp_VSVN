# Request

## User outcome

`lh_vv_gold.dbo.gld_srv_poi_multi_lang` has a nullable string column `experience`. `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` has the same column. Gold copies the value 1-1 from the two sources named in the request. Grain and keys stay `(poi_id, lang)` on gold and unchanged on the silver landing table.

## User request (verbatim)

Thêm cột experience type string cho slv_enr_poi_info_multi_lang.
Bảng gld_srv_poi_multi_lang thêm cột experience:
- lấy 1-1 slv_enr_poi_info_multi_lang.experience
- lấy 1-1 slv_pn_business_service_i18ns.usps
Lý do nghiệp vụ: gold multi-lang cần một cột experience kiểu string; silver landing có cột cùng tên; gold lấy đúng giá trị từ hai nguồn đã nêu.

## Scope

### In scope

- Add nullable `experience` STRING on `slv_enr_poi_info_multi_lang` in `NB_CREATE_DDL` and `NB_SETUP_INITIAL_DDL` only. No loader.
- Add `experience` STRING on `gld_srv_poi_multi_lang` in both DDL notebooks and in `NB_GLD_SRV_POI_MULTI_LANG`.
- Keep the two 1-1 lines above as the mapping rule.
- Contract tests for the landing column list and for `OUT_COLS` / inputs of `gld_srv_poi_multi_lang`.

### Out of scope

- A notebook or job that writes `slv_enr_poi_info_multi_lang`.
- New gold inputs beyond `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich`, and `slv_pn_business_service_i18ns`.
- Coalesce, fallback, string truncation, or a partner / non-partner branch for `experience`.
- Copying the existing `description` rule (partner takes `bio`, else enr `description`).
- Other tasks, `notebooks_lgc/`, and pipeline manifests.

## Acceptance criteria

- `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` has column `experience` STRING, nullable, with no grain or key change.
- `lh_vv_gold.dbo.gld_srv_poi_multi_lang` has column `experience` STRING. The value matches the two 1-1 lines above. No coalesce, fallback, truncation, or partner / non-partner branch.
- Gold grain stays `(poi_id, lang)`. No new input beyond the two tables already in the node.
- DDL changes in both `NB_CREATE_DDL` and `NB_SETUP_INITIAL_DDL`.
- `slv_enr_poi_info_multi_lang` is a landing table. The repository has no notebook that writes it. Schema column only. Do not invent a loader.
- If one gold row can receive a non-null value from both sources and the request does not say which source wins: stop at `user_decision`, write the question in `decision.md`, do not call the Architect, and do not edit code.
- `usps` must already be a physical column on `slv_pn_business_service_i18ns`. If it is absent from DDL, record `MISSING_EVIDENCE`, write the smallest probe, and stop at `waiting_evidence`.

## Constraints

- Keep the two 1-1 lines verbatim. The current `description` pattern is comparison only.
- Do not read other tasks, `notebooks_lgc/`, or pipeline manifests.
- Domain: DDL/registry and lib transform/gold.
- Mandatory signal: `data_model_change`.

## Classification rationale

- Complexity: `medium`. The task adds columns (`data_model_change`). One partner gold row is a left join of `slv_enr_poi_info_multi_lang` and `slv_pn_business_service_i18ns`, so both `experience` and `usps` can be non-null on that row (`design_tradeoffs`).
- Risk: `medium`. The column is additive and nullable. Grain, key, and MERGE match stay. Choosing the wrong source would publish the wrong string on a bounded column.
- Architecture: required. WORKFLOW §5: more than one viable mapping has a material trade-off (which source wins). Do not start the Architect while that question is open.
- Evidence: not required for column existence. `usps` is registry column `type: string` on `target_table` `slv_pn_business_service_i18ns` in `NB_CREATE_DDL` cell 11 and `NB_SETUP_INITIAL_DDL` cell 4. `slv_pn_*` physical columns are that registry, not a `CREATE TABLE` (naming convention §2.1.7).
- Runtime proof: required after implementation so the user can apply both DDL notebooks in Fabric DEV. This session must not mark `runtime` pass.
- Reviewer routing: `sql-data-reviewer` for Delta DDL and the projection; `spark-runtime-reviewer` for the notebook build contract. No pipeline, watermark, lock, or CDC change, so no `fabric-pipeline-reviewer` and no `state-correctness-reviewer`. Risk is not high, so no `risk-gate`.
