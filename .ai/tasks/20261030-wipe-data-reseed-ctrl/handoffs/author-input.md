# Author input — 20261030-wipe-data-reseed-ctrl

User comments, verbatim:

- "Xóa data nghĩa là xóa dòng. Không DROP TABLE, không đổi schema, không VACUUM."
- "Init chỉ ba seed ctrl: ctrl_mng_pipeline_config, ctrl_mng_watermark, ctrl_cfg_schema_registry. Bốn bảng log và state của ctrl chỉ bị xóa, không seed."
- "Không chạy nguyên notebook NB_SETUP_INITIAL_DDL và không chạy NB_CREATE_DDL. Không seed ref_dictionary_place_type hay ref_dictionary_amenities."
- "Chỗ notebook không tách riêng phần ctrl thì ghi MISSING và đưa câu lệnh seed chỉ ba bảng ctrl, không bịa lệnh tạm dừng pipeline."
- "Dòng đầu runbook ghi rõ chỉ Fabric DEV. Môi trường khác thì dừng ở user_decision."
- "Trước khi xóa, runbook bắt người dùng chạy probe đọc danh sách bảng và số dòng. Bảng không có trong repo thì dừng, không xóa."

Read only: `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cells `id:init_tables`, `id:init_seed_ctrl`, `id:init_plan`, `id:init_seed_write`, `id:init_cfg_partner`, `id:init_cfg_3p`, `id:init_registry_pure`; `docs/context/CTRL_TABLES_CONTEXT.md` §1, §3, §4, §5; `notebooks/NB_CREATE_DDL.ipynb` cell 0 only. Do not read `notebooks_lgc/`. `architecture.md` has no Main brief; this file is the contract.

Wipe rows with `DELETE FROM` in `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_gold` (schemas `dbo` and `enr`) and the seven `lh_vv_ctrl.dbo` tables in §1. No DROP, schema change, VACUUM, or OPTIMIZE.

Keep every `TABLE_SPECS` table whose name starts with `ref_`. Cell `id:init_tables` has only `lh_vv_silver.dbo.ref_dictionary_place_type` and `lh_vv_silver.dbo.ref_dictionary_amenities`. Do not take ref names from naming-doc examples. Any other live `ref_*` table is outside `TABLE_SPECS`: stop and delete nothing.

Repo allowlist: `TABLE_SPECS` fq, plus src/trg tables in `PIPELINE_CONFIG_ROWS` and `WATERMARK_ROWS` (`id:init_seed_ctrl`), plus target tables in `TABLE_CONFIGS` and `TABLE_CONFIGS_3P`. Notebook cells win over the 04/10 snapshot and the policy example in §3 and §5. A live table outside this allowlist: stop and delete nothing.

Seed is insert-only. In `id:init_seed_write`, `_merge_pipeline_config`, `_merge_watermark`, and `_merge_registry` are `MERGE` … `WHEN NOT MATCHED THEN INSERT` with no `WHEN MATCHED`. Delete those three tables' rows before seeding. The same cell also calls `_merge_place_type` and `_merge_amenities`. Do not run it, and do not run either notebook. No cell seeds only the three ctrl tables: write `MISSING` and give seed statements for only those three, using views `_v_setup_pipeline_config`, `_v_setup_watermark`, and `_v_setup_registry` from `id:init_plan` and the row literals plus registry flatten. Do not build or write the place-type or amenities views.

`WATERMARK_ROWS` has two extract rows only. Do not seed `wm_e__` or `wm_flow__` rows described in §4. §5 `overwrite` / `replaceWhere` describes `NB_CREATE_DDL`; do not use it. §4 `DROP` guidance does not apply. Do not invent a pipeline pause command.

Delete-only: `ctrl_log_run`, `ctrl_log_table_run`, `ctrl_cdc_state`, `ctrl_cdc_reject`.

The pre-delete probe is read-only (`SHOW TABLES` and row counts, aggregate, at most 50 sample rows, no personal data). After seed, the three tables match the seed key counts, the four log/state tables are empty, ref row counts match the baseline, and every other in-scope table is empty. Idempotency: run the three MERGEs again without another delete; inserted = 0.

First line: Fabric DEV only. Any other environment: stop at `user_decision`. Do not claim a Fabric command was executed.
