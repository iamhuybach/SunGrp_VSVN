-- P7. Chỉ đọc. Control lakehouse của model mới.
-- Nếu bảng không ở lh_vv_ctrl, ghi MISSING_TABLE và DESCRIBE đúng bảng ctrl.
-- Dán vào evidence/results/gld_srv_owner_pl.txt. Không secret.
SELECT pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, load_mode, nb_name, priority
FROM sgr_visitvn_dev.lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_tbl IN ('gld_srv_poi_info', 'gld_srv_poi_multi_lang', 'gld_srv_poi_review')
ORDER BY trg_tbl, pl_name, src_tbl;

-- Ngưỡng khóa: nếu DESCRIBE có cột lock hoặc timeout, ghi tên cột và giá trị một dòng config. Không secret.
-- Nếu không có cột đó, ghi NO_LOCK_COLUMN.
DESCRIBE TABLE sgr_visitvn_dev.lh_vv_ctrl.dbo.ctrl_mng_pipeline_config;
