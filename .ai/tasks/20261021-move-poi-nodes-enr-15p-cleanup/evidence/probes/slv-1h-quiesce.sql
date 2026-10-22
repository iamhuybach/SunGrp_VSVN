-- Môi trường: Fabric DEV. Chỉ đọc. Không chạy ngoài DEV.
-- Mục đích: PIPE-001. Chứng minh PL_VV_TRANS_SLV_TO_SLV_1H không có run notebook đang RUNNING
--           và khoá wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H không bị giữ, ngay trước cleanup.
--           Ảnh chụp sau post-check thuộc runtime, không thuộc probe này.
-- Thứ tự: Q1, Q2, Q3. Câu lỗi thì dán lỗi rồi chạy câu sau.
-- Điều kiện: lakehouse lh_vv_ctrl trên DEV. Không tham số. Không ghi. Không tắt schedule trong file này.
-- Chạy lại: an toàn, không đổi dữ liệu.
-- Đạt: Q1 có 0 hoặc 1 dòng và lock_exec_id null. Q2 không có status RUNNING, hoặc n của RUNNING bằng 0.
--      Q3 không có dòng status RUNNING và không chạm LIMIT 20.
-- Cột: xem từng câu. Không dữ liệu cá nhân, không secret.
-- Dán toàn bộ kết quả vào .ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup/evidence/results/slv-1h-quiesce.txt
-- Chạy trong notebook Spark trên DEV, từng câu một.
-- Phần Monitor Fabric (item, schedule, In progress, Queued) ghi cùng file, không có câu SQL.

-- Q1. Khoá luồng cũ.
SELECT
    watermark_id,
    status,
    lock_exec_id,
    lock_at,
    flow_name
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H';

-- Q2. Số dòng log theo status. Không có dòng RUNNING là đạt.
SELECT
    status,
    COUNT(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H'
GROUP BY status
ORDER BY status;

-- Q3. Hai mươi lần chạy mới nhất. Fail nếu có 20 dòng (bị cắt) hoặc có status RUNNING.
SELECT
    exec_id,
    run_id,
    nb_name,
    status,
    started_at,
    ended_at
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H'
ORDER BY started_at DESC
LIMIT 20;
