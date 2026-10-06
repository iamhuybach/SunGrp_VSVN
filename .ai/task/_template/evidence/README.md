# Evidence — {{TASK_ID}}

- Probe do Main sinh: `probe_<nn>_<mục-đích>.sql` hoặc `.py` (chạy trên Fabric DEV). Đầu file ghi: chạy ở đâu (notebook / SQL endpoint), lakehouse mặc định, kết quả cần dán.
- USER dán kết quả vào `results/probe_<nn>.txt` (hoặc .csv). Không dán dữ liệu cá nhân; giới hạn mẫu ≤ 50 dòng.
- Agent chỉ được kết luận về dữ liệu dựa trên file trong `results/`.
