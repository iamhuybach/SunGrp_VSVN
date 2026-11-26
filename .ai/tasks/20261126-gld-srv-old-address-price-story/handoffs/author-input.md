# Author input — runbook

## Verbatim request

Update bảng gld_srv_poi_info: old_address như full address nhưng field có tiền tố old_ khi DDL có cột đó; price_level, price_min, price_max từ slv_3p_poi_price. Update gld_srv_poi_multi_lang: story và local_tips từ slv_pn_business_service_i18ns. Hai bảng không sink xuống db serving và API không dùng.

## Verbatim decision

Lấy house_number, street, full_address chứ không phải old_house_number, old_street, old_full_address.
Thêm ba path trên vào scope.files.

## What the runbook must cover

Fabric DEV only. User runs it. Do not claim a run happened.
Order from architecture.md `Rollout`: probe P1, then cell `oldpricepy` of `NB_CREATE_DDL`, then publish `NB_GLD_SRV_POI_INFO` and `NB_GLD_SRV_POI_MULTI_LANG`, then `PL_VV_TRANS_SLV_TO_GLD_30M`, then probes R1–R6. Do not publish the notebooks before `oldpricepy` succeeds.
Take parameters from `NB_GLD_SRV_POI_INFO` cell `srvinfoparam`, `NB_GLD_SRV_POI_MULTI_LANG` cell `srvmlparam`, and the pipeline JSON for `PL_VV_TRANS_SLV_TO_GLD_30M`. If a value is unknown, ask; do not guess.
Include rollback and forward recovery from architecture.md `Rollback and forward recovery`. Idempotency: one rerun of `oldpricepy` writes nothing; one rerun of the 30M flow updates `row_hash` once for live rows.
Probes P1 and R1–R6 are specified in architecture.md `Verification`. Samples at most 50 rows, no personal data, no secrets.

## Files and anchors

- `.ai/tasks/20261126-gld-srv-old-address-price-story/architecture.md` — `Rollout`, `Rollback and forward recovery`, `Verification`, `Idempotency`
- `.ai/tasks/20261126-gld-srv-old-address-price-story/decision.md` — `Quyết định của người dùng`
- `notebooks/NB_CREATE_DDL.ipynb` — `id:oldpricemd`, `id:oldpricepy`
- `notebooks/NB_GLD_SRV_POI_INFO.ipynb` — `id:srvinfoparam`, `id:srvinfobuild`
- `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb` — `id:srvmlparam`, `id:srvmlbuild`
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` — `id:init_seed_ctrl`

## Constraints

- Do not read `docs/context/mapping_legacy_ai_product.md` or `local/once/legacy-init-sgr-visitvn-dev.ipynb`.
- Do not read `notebooks_lgc/`, `docs/poi-serving-api/`, or `services/data-serving-service/`.
- Six columns stay gold-only. No PostgreSQL or API change.
- Do not invent `old_house_number`, `old_street`, or `old_full_address`.
