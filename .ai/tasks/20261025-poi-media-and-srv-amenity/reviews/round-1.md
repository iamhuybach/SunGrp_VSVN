## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium` — khớp yêu cầu.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer` — chạy độc lập.
- Risk gate: không chạy vì task state ghi `not_required`.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | Vị trí | Failure | Fix |
|---|---|---|---|---|
| STATE-001 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:169`; `notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb:101`; `notebooks/NB_GLD_SRV_POI_AMENITY.ipynb:91` | Run đã mất lease vẫn có thể MERGE snapshot cũ sau run mới hơn, làm target lùi trong khi watermark đã tiến. | Fence quyền sở hữu ngay trước target MERGE và edge-watermark commit; stale owner phải bị từ chối mọi durable write. |
| SQL-001 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:116` | Chưa có bằng chứng toàn bộ union source duy nhất theo `media_id`; URL partner trùng hoặc va chạm với key 3P sẽ làm MERGE thất bại. | Chứng minh uniqueness trên full build; nếu fail, xin quyết định nghiệp vụ về key hoặc xử lý duplicate xác định, không tự dedupe. |
| SPARK-001 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:112` | Năm action `count()` có thể đánh giá lại cùng lineage nhiều lần, gây rủi ro vượt cadence/SLA trên F16 dùng chung. | Gộp metric vào một aggregation, bỏ action thừa, hoặc materialize có cleanup rõ ràng. |

P2/P3: `1/0`.

Probe: Trên Fabric DEV, chạy full `build(ctx)` không ghi để kiểm tra `media_id` duplicate (`PASS = 0`), đồng thời ghi Spark UI job count/input bytes/duration của năm action để xác nhận chi phí runtime.
