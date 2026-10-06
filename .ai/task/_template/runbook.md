# Runbook Fabric DEV — {{TASK_ID}}

> Main viết. USER chạy trên Fabric DEV và điền mục Kết quả.

## 0. Điều kiện trước
- [ ] Code đã sync vào workspace DEV (Git integration / deploy)
- [ ] Pipeline liên quan đã tạm dừng lịch (nếu cần): <tên>
- [ ] Backup / snapshot cần thiết: <query hoặc "none">

## 1. Đo trước khi chạy
```sql
-- số dòng, max version, watermark hiện tại của các bảng liên quan
```

## 2. Chạy lần 1
| Bước | Đối tượng | Tham số | Kỳ vọng |
|---|---|---|---|

## 3. Kiểm tra sau lần 1
```sql
-- ctrl_log_run / ctrl_log_table_run theo exec_id
-- số dòng, trùng khóa, null khóa, reject mới
```

## 4. Chạy lần 2 (idempotency) — cùng input
Kỳ vọng: không đổi dữ liệu đích (so số dòng + hash), log NO_DATA hoặc 0 inserted/updated.
```sql
-- query so sánh trước/sau
```

## 5. Rollback
<!-- các bước đưa về trạng thái trước: DROP/RESTORE TABLE ... VERSION AS OF ..., reset watermark ... -->

## 6. Kết quả (USER điền)
- Lần 1: PASS / FAIL — exec_id: … — ghi chú:
- Lần 2: PASS / FAIL — ghi chú:
- Log/ lỗi đính kèm: `evidence/results/runtime_*.txt`
