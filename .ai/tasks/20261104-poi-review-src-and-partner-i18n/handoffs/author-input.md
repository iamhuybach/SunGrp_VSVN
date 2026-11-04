# Author input — model

## User comments verbatim

- slv_3p_poi_review.title gán là null
- gld_srv_poi_review.review_text lấy từ slv_3p_poi_review.text

Cột hoặc khóa không có trong yêu cầu thì MISSING, không tự đặt.

Điều kiện cũ "không còn dòng thì cả node dừng, không ghi bảng" không nằm trong yêu cầu mới. Không tự giữ. Nếu cần cho idempotency thì ghi USER_DECISION và dừng.

Yêu cầu này bỏ lang trên gold.

## Read

- `.ai/tasks/20261104-poi-review-src-and-partner-i18n/request.md`
- `.ai/tasks/20261104-poi-review-src-and-partner-i18n/decision.md` — `## Quyết định hiện hành` only. Rows D-SRV-LANG and D-SRV-TEXT.
- `notebooks/NB_GLD_SRV_POI_REVIEW.ipynb` cell `id:srvrvbuild`
- `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` target `slv_3p_poi_review`
- `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` cell `id:b1entitybuild` def `_partner`
- `notebooks/NB_ENR_POI_INFO.ipynb` cell `id:36415d3b` defs `_time_to_spend_text`, `_best_time_text`, `_cost_vnd`
- `docs/context/01_DATA_MODEL.md` §8 and N6
- `docs/context/mapping_gld_srv_poi_review.md`
- `docs/context/gld_enr_poi_info_review.md` both tables

## Constraints

`slv_3p_poi_review` has no `title` column. D-SRV-TEXT assigns gold `title` null. Do not add `title` to the source table. Gold `review_text` is `slv_3p_poi_review.text` only. No producer notebook: no `notebooks/` file sets `trg_tbl` to `slv_enr_poi_review_multi_lang`. Do not invent one. Do not DROP. D-SRV-LANG drops gold `lang`. PostgreSQL file is impact only. No `proposal.md`.
