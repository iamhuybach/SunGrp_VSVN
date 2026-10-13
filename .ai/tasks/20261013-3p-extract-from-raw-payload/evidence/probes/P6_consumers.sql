-- Probe P6 — consumer của slv_3p_poi* trong ctrl.
-- Môi trường: Fabric DEV, SQL analytics endpoint hoặc notebook Spark, chỉ đọc.
-- Lưu kết quả vào evidence/results/P6_consumers.md.
-- Không lấy dữ liệu cá nhân. Giới hạn 50 dòng.

SELECT pl_name, src_tbl, trg_schema, trg_tbl, load_mode, is_active
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE src_tbl LIKE 'slv_3p_poi%'
ORDER BY pl_name, trg_tbl;

SHOW TABLES IN lh_vv_silver.dbo LIKE 'slv_poi*';
