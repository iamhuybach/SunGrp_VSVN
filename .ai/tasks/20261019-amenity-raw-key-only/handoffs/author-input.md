# Author input

Task: 20261019-amenity-raw-key-only
Kind: runtime-runbook.md
Environment: Fabric DEV. Schema `lh_vv_silver.dbo`. User runs every step. Agent does not set `gates.runtime`.

Read:
- `.ai/tasks/20261019-amenity-raw-key-only/architecture.md` `## Main brief`
- same file `## 17. Rollout, rollback, and forward recovery`
- same file `## 19. Runtime runbook design` (R0, R1, R1b, STOP R1, R2, STOP R2, R3, STOP R3)
- `notebooks/NB_SETUP_POI_AMENITY.ipynb` cell `c1setupparam` (`p_apply`)
- `notebooks/NB_SLV_POI_AMENITY.ipynb` cell `d1amenparam`
- `docs/context/CTRL_TABLES_CONTEXT.md` §3, row `slv_poi_amenity` of `PL_VV_TRANS_SLV_TO_SLV_1H`

No pipeline JSON.

Notebooks: `NB_SETUP_POI_AMENITY`, `NB_SLV_POI_AMENITY`. Scratch cell starts with `%run NB_LIB_TRANSFORM_SLV_GLD`. `PL = "PL_VV_TRANS_SLV_TO_SLV_1H"`.

Tables: `lh_vv_silver.dbo.ref_dictionary_amenities`, `lh_vv_silver.dbo.slv_poi_amenity`. Backups: `bak_ref_dictionary_amenities_20261019`, `bak_slv_poi_amenity_20261019`. Do not `DROP` either live table.

Write the ordered DEV steps from §19, including the three stops, before/after counts, idempotency check, control-log and watermark check, rollback, and forward recovery. Leave `Kết quả người dùng ghi nhận` empty for the user.
