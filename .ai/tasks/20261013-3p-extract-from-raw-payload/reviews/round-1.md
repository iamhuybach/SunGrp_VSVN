## Model và reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium` — khớp yêu cầu.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`.
- Risk gate: đã hoàn tất.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:548,559-563` | Typed projection bỏ `_bad__source_flags_json` rồi projection kế tiếp tham chiếu lại, gây `AnalysisException` trước amenity MERGE. | Giữ `_bad__*` tới khi tính xong `_cn__*`, rồi chạy fixture Spark end-to-end cho `JSON_PICK`. |
| GATE-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:157,160-165` | Seed insert-only giữ `dedup_order` cũ chứa `media_id` đã bị xóa khỏi registry, khiến validation chặn cutover. | Thêm `UPDATE`/`MERGE` idempotent, scope chính xác, đặt `dedup_order = 'display_order ASC'` và kiểm tra rerun. |
| GATE-003 | P1 | `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:707` | Full reload có thể để lại target rỗng sau crash; incremental sau đó thấy bảng tồn tại và bỏ qua lịch sử theo state cũ. | Chặn incremental khi target thiếu hoặc rỗng mà prior state tồn tại, tốt nhất bằng successful-initialization marker. |
| GATE-004 | P1 | `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb:945-967` | Self-check không thực thi đầy đủ `ARRAY_PICK`, `ARRAY_PROJECT`, `JSON_PICK` và error flags nên có thể báo `PASS` giả. | Dùng synthetic Spark SQL fixture thực thi mọi rule mới cùng các trường hợp malformed/type-error và kiểm tra `_bad__`/`_cn__`. |
| GATE-005 | P1 | `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb:945-967` | Quoted literals/backslash trong replacement field của f-string không parse trên Python trước 3.12, làm Fabric Runtime 1.3 lỗi `SyntaxError` khi nạp library. | Gán trước SQL literals vào biến hoặc xây query không dùng nested quote/backslash trong f-string expression, rồi compile trên đúng runtime. |

P2/P3: `P2=4`, `P3=3` (tổng số specialist báo cáo trước khi khử trùng lặp; không ảnh hưởng verdict).

Probe: Không cần probe dữ liệu; cần runtime fixtures và crash-injection sau khi sửa.
