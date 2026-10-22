# Author input — model design

No `proposal.md`, `problem-analysis.md`, or `requirements-analysis.md`. Do not invent one.

Read:

- `.ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup/request.md` sections `User outcome` and `Cách hiểu đang dùng`
- `.ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup/decision.md` section `Quyết định hiện hành` (D-01 to D-04)
- `.ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup/evidence/results/ctrl-inventory.txt`
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables`: `gld_enr_poi_coordinate` column list only
- `notebooks/NB_SLV_PN_POI.ipynb` cell `379af200`: `build` select list and `NodeSpec` only
- `docs/context/01_DATA_MODEL.md` rows N6 and N7, and the `poi_id` sentence above them

Model change:

- Remove `lh_vv_gold.enr.gld_enr_poi_coordinate` and `lh_vv_silver.dbo.slv_pn_poi` from the model.
- Keep `slv_poi_amenity` and `slv_poi_entity_non_enrich`. Grain, keys, and columns stay as N6 and N7. Do not redesign them.
- Keep `gld_enr_poi_info` and `gld_enr_poi_review`. Do not list their columns.
- Keep `slv_3p_poi`, `slv_3p_poi_address`, and `slv_3p_poi_contact`.

Out of this document: pipeline names, ctrl edges, watermarks, locks, ordering, and DROP mechanics. Those belong to the Architect.

`poi_id` formulas already in the named files: entity partner is `md5(concat(id, 'partner'))` with 8-4-4-4-12 dashes; `slv_pn_poi` uses `uuid_md5` of `partner_portal` and `id`. Do not equate them.

If a technical column is not in the named cell, leave it as a question. Do not guess types.
