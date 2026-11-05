## Model and reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium`.
- Reviewers: `sql-data-reviewer`, `state-correctness-reviewer`, `spark-runtime-reviewer`.
- Risk gate: completed; did not pass.

## Gate verdict: `USER_DECISION`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:176`; `notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb:81` | Fabric chấp nhận khóa `(media_id, poi_id)` nhưng PostgreSQL vẫn dùng `PRIMARY KEY (media_id)`, nên một `media_id` thuộc nhiều POI có thể làm sync thất bại và gây divergence. | Chuyển khóa và conflict target của PostgreSQL sang `(media_id, poi_id)`, hoặc chặn global duplicate `media_id` trong Fabric; nếu hoãn thì cần user chấp nhận risk rõ ràng. |
| GATE-002 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:128` | `countDistinct(key)` tạo thêm full-cardinality shuffle chưa có bằng chứng đáp ứng cadence trên shared F16. | Chỉ tính metric trong `DRY_RUN`, dùng phép đếm bounded/approximate, hoặc cung cấp DEV evidence đạt ngưỡng. |

P2: 2. P3: 0.

Probe: chạy pinned Fabric DEV `DRY_RUN` và xác nhận `.first()` thứ hai hoàn tất ≤90 giây, không disk spill/throttling; đồng thời chạy `GROUP BY media_id HAVING COUNT(DISTINCT poi_id) > 1` trên silver và gold—kết quả 0 dòng chỉ chứng minh dữ liệu hiện tại, không bảo đảm invariant tương lai.
