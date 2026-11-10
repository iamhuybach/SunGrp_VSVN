# Author input — runbook

Task `20261109-srv-poi-amenity-en`. Write the user-run Fabric DEV and PostgreSQL runbook. The agent does not run these steps.

## Decisions

- U-3 verbatim: runbook có bước người dùng DROP ref_dictionary_amenities và chạy NB_SETUP_POI_AMENITY p_apply=true.
- Also DROP `lh_vv_gold.dbo.gld_srv_poi_amenity` and recreate it, then DROP `apps.srv_poi_amenity` and recreate it from `sql/postgres/gld_srv_serve.pg.sql`. The user runs the Copy Job. Do not invent the Copy Job name if the repo does not show it.
- D-02: path stays `GET /api/v1/pois/{poi_id}/amenities`.

## Read

- `.ai/tasks/20261109-srv-poi-amenity-en/architecture.md` sections `Main brief`, `Rollout`, `Rollback and forward recovery`, `Runtime proof`.
- Parameter cells: `notebooks/NB_SETUP_POI_AMENITY.ipynb` `c1setupparam`, `notebooks/NB_SLV_POI_AMENITY.ipynb` `d1amenparam`, `notebooks/NB_GLD_SRV_POI_AMENITY.ipynb` `srvamenityparam`.
- Use the parameter names and defaults in those cells. `p_apply` is `"false"` for the plan pass and `"true"` for the apply pass. If `p_force` is absent from the gold parameter cell, write `<CẦN NGƯỜI DÙNG CUNG CẤP: p_force>`.

## Steps to include

R-0 through R-9 and checks P-1 through P-7 from the architecture, including the exact SQL already written there. Pause `PL_VV_TRANS_SLV_TO_ENR_15M` and `PL_VV_TRANS_SLV_TO_GLD_1H` before the drops, and resume them at the end. Samples at most 50 rows. No personal data and no secrets. `Kết quả người dùng ghi nhận` stays empty for the user to fill.
