# Author input — model

## User comments verbatim

- gld_enr_poi_info vẫn lấy slv_poi_entity_non_enrich.source_name
- Chỉ cần thêm cột DDL. Hiện tại đổ vào bảng đấy là job enrich ngoài và chưa implement
- Tạo thêm 1 cột source_name ở bảng slv_enr_poi_info_multi_lang. Dòng chỉ có i18n vẫn lấy mọi locale và source_name là partner.

## Read

- `.ai/tasks/20261104-gld-srv-multi-lang-i18n-without-enr/decision.md`, `## Quyết định hiện hành` only
- same task `request.md` and `model-design.md`
- `notebooks/NB_ENR_POI_INFO.ipynb` cell `id:36415d3b`, `_present` and the `source_name` alias
- `docs/context/gld_enr_poi_info_review.md` the `source_name` row and the source list
- `docs/context/mapping_gld_srv_poi_multi_lang.md`
- `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb` cell `id:srvmlbuild`

## Constraints

D-ML-NOMATCH is later than D-ML-SRC and D-ML-GATE. `gld_enr_poi_info.source_name` stays `slv_poi_entity_non_enrich.source_name`. Do not read the new column in `NB_ENR_POI_INFO`. The google predicate stays on that same entity value. Add `source_name` on `slv_enr_poi_info_multi_lang` in DDL only. No notebook writer. The external job is out of scope. I18n-only `gld_srv_poi_multi_lang` rows still use every locale and `source_name` `'partner'`. P1 of that gold table stays on the current transform. No `proposal.md`. Do not edit files.
