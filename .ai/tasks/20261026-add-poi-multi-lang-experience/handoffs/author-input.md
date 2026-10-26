# Author input — model

Task: `20261026-add-poi-multi-lang-experience`. No `proposal.md`. The request below is the source. Do not invent a winner, coalesce, fallback, truncation, or a partner / non-partner branch.

## Verbatim request

Thêm cột experience type string cho slv_enr_poi_info_multi_lang.
Bảng gld_srv_poi_multi_lang thêm cột experience:
- lấy 1-1 slv_enr_poi_info_multi_lang.experience
- lấy 1-1 slv_pn_business_service_i18ns.usps
Lý do nghiệp vụ: gold multi-lang cần một cột experience kiểu string; silver landing có cột cùng tên; gold lấy đúng giá trị từ hai nguồn đã nêu.

## Read

- `docs/agent-system/WORKFLOW.md` §5 Classification, §7 Review routing.
- `docs/context/mapping_gld_srv_poi_multi_lang.md` §1. Partner rows left-join i18n on `poi_id` and `lang` = `locale`. `description` uses partner `bio` with enr fallback. That pattern is comparison only. Do not copy it onto `experience`.
- `docs/context/02_NAMING_CONVENTION.md` §1 prefixes and §2 notebooks, including §2.1.7: `slv_pn_*` columns come from the registry, not `CREATE TABLE`.
- `notebooks/NB_CREATE_DDL.ipynb` grep `slv_enr_poi_info_multi_lang`, `gld_srv_poi_multi_lang`, `usps`.
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` the same three greps.
- `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb` cell `srvmlbuild`.
- `tests/test_enr_poi_contract.py` `LANDING` for `slv_enr_poi_info_multi_lang`.
- `tests/test_gld_srv_poi_contract.py` `OUT_COLS` and inputs for `gld_srv_poi_multi_lang`.

## Facts from those files

- Landing columns now: `poi_id` STRING NOT NULL, `lang` STRING, `time_to_spend` STRING, `best_time` STRING, `cost_vnd` STRING, `description` STRING, `created_at` TIMESTAMP, `updated_at` TIMESTAMP. No `experience`. No writer notebook in scope.
- Gold build: `ML_COLS` / `OUT_COLS` are `poi_id`, `lang`, `time_to_spend`, `best_time`, `cost_vnd`, `description` plus `source_name` on output. `SPEC.pk` is `(poi_id, lang)`. Inputs are `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich`, `slv_pn_business_service_i18ns`. i18n is required only for columns `business_service_id`, `locale`, `bio`. Partner join key is `uuid_md5(business_service_id, 'partner')`.
- `usps` is already a registry column `{"path": "usps", "type": "string"}` on `target_table` `slv_pn_business_service_i18ns` in both DDL notebooks. Do not treat it as missing.
- One gold row with `source_name = partner` and a matching i18n row can hold both `slv_enr_poi_info_multi_lang.experience` and `slv_pn_business_service_i18ns.usps` non-null. The request does not say which value `gld_srv_poi_multi_lang.experience` keeps.

## Constraints

- Both new columns are STRING and nullable. Do not change grain or keys.
- Gold reads only the inputs already on the node. Gold does not read gold.
- DDL belongs in both `NB_CREATE_DDL` and `NB_SETUP_INITIAL_DDL`. Landing change is schema only.
- If both sources can supply a non-null value for the same gold row, record that as an open question. Do not choose a source.
