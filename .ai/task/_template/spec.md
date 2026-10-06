# Spec — {{TASK_ID}}

> Viết bởi Claude Code (Architect). Mức LLD: Main phải implement được mà không cần tự quyết thêm thiết kế.

## 1. Bối cảnh & mục tiêu

## 2. Phạm vi / Ngoài phạm vi

## 3. Quyết định thiết kế (ADR-lite)
| # | Quyết định | Phương án khác đã cân nhắc | Lý do | Nguồn (Fabric docs / evidence) |
|---|---|---|---|---|

## 4. LLD
### 4.1 Bảng (tạo/sửa)
<!-- tên đầy đủ, grain, khóa MERGE, cột + kiểu, partition, COMMENT, DDL -->
### 4.2 Notebook
<!-- tên, tầng NB00/NBx0/NBxy, tham số, danh sách cell/hàm + signature, input → output -->
### 4.3 Pipeline
<!-- activity thêm/sửa, dependsOn, tham số, timeout/retry -->
### 4.4 Control tables
<!-- dòng config/watermark/registry cần thêm/sửa (SQL) -->

## 5. Idempotency & rerun
<!-- chạy lại cùng input cho kết quả gì; thứ tự commit dữ liệu → watermark/state -->

## 6. Failure modes
| Tình huống | Hành vi mong đợi | Ghi log ở đâu |
|---|---|---|

## 7. Test plan
<!-- unit (pytest hàm thuần) + runtime trên Fabric DEV -->

## 8. Evidence needed
<!-- "none" hoặc danh sách query probe cần USER chạy trước khi implement -->

## 9. Open questions (cho USER)
