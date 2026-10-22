-- Môi trường: Fabric DEV. Chỉ đọc. Không chạy ngoài DEV.
-- Mục đích: kê cạnh ctrl, watermark và số dòng của các bảng sắp chuyển hoặc xóa.
-- Thứ tự: chạy từng câu, từ INV-1 đến INV-8. Câu lỗi thì dán lỗi rồi chạy câu sau.
-- Điều kiện: lakehouse lh_vv_ctrl, lh_vv_silver, lh_vv_gold trên DEV. Không tham số. Không ghi.
-- Chạy lại: an toàn, không đổi dữ liệu.
-- Đạt: với mỗi cặp đếm/chi tiết, số COUNT bằng số dòng chi tiết và chi tiết không chạm LIMIT 50.
-- Cột: xem từng câu. Tối đa 50 dòng mỗi câu chi tiết. Không dữ liệu cá nhân, không secret.
-- Dán toàn bộ kết quả vào .ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup/evidence/results/ctrl-inventory.txt
-- Chạy trong notebook Spark trên DEV, từng câu một.

-- INV-1. Số cạnh liên quan.
SELECT COUNT(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H'
   OR trg_tbl IN (
        'slv_poi_amenity',
        'slv_poi_entity_non_enrich',
        'slv_pn_poi',
        'gld_enr_poi_coordinate',
        'gld_enr_poi_info'
      )
   OR src_tbl IN (
        'slv_pn_poi',
        'gld_enr_poi_coordinate',
        'slv_poi_amenity',
        'slv_poi_entity_non_enrich'
      );

-- INV-2. Chi tiết cạnh. Fail nếu kết quả có 50 dòng (bị cắt).
SELECT
    pl_name,
    src_schema,
    src_tbl,
    trg_schema,
    trg_tbl,
    is_active,
    priority,
    load_mode,
    nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H'
   OR trg_tbl IN (
        'slv_poi_amenity',
        'slv_poi_entity_non_enrich',
        'slv_pn_poi',
        'gld_enr_poi_coordinate',
        'gld_enr_poi_info'
      )
   OR src_tbl IN (
        'slv_pn_poi',
        'gld_enr_poi_coordinate',
        'slv_poi_amenity',
        'slv_poi_entity_non_enrich'
      )
ORDER BY pl_name, trg_tbl, src_tbl
LIMIT 50;

-- INV-3. Số watermark cạnh và khoá luồng.
SELECT COUNT(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN (
        'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H',
        'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P'
      )
   OR trg_tbl IN (
        'slv_poi_amenity',
        'slv_poi_entity_non_enrich',
        'slv_pn_poi',
        'gld_enr_poi_coordinate',
        'gld_enr_poi_info'
      )
   OR src_tbl IN (
        'slv_pn_poi',
        'gld_enr_poi_coordinate',
        'slv_poi_amenity',
        'slv_poi_entity_non_enrich'
      );

-- INV-4. Chi tiết watermark. Fail nếu kết quả có 50 dòng (bị cắt).
SELECT
    watermark_id,
    src_tbl,
    trg_tbl,
    status,
    flow_name,
    lock_exec_id,
    lock_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN (
        'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H',
        'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P'
      )
   OR trg_tbl IN (
        'slv_poi_amenity',
        'slv_poi_entity_non_enrich',
        'slv_pn_poi',
        'gld_enr_poi_coordinate',
        'gld_enr_poi_info'
      )
   OR src_tbl IN (
        'slv_pn_poi',
        'gld_enr_poi_coordinate',
        'slv_poi_amenity',
        'slv_poi_entity_non_enrich'
      )
ORDER BY watermark_id
LIMIT 50;

-- INV-5. Bảng còn tồn tại hay không. Một câu lỗi thì ghi lỗi và chạy câu kế.
SELECT 'lh_vv_gold.enr.gld_enr_poi_coordinate' AS table_name, COUNT(*) AS n
FROM lh_vv_gold.enr.gld_enr_poi_coordinate;

-- INV-6
SELECT 'lh_vv_silver.dbo.slv_pn_poi' AS table_name, COUNT(*) AS n
FROM lh_vv_silver.dbo.slv_pn_poi;

-- INV-7
SELECT 'lh_vv_silver.dbo.slv_poi_amenity' AS table_name, COUNT(*) AS n
FROM lh_vv_silver.dbo.slv_poi_amenity;

-- INV-8
SELECT 'lh_vv_silver.dbo.slv_poi_entity_non_enrich' AS table_name, COUNT(*) AS n
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich;
