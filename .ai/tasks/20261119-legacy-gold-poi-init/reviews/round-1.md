## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — khớp yêu cầu.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`.
- `risk-gate`: đã hoàn tất.

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `GATE-001` — **P0** — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:216`: `drift_n` luôn bằng 0 và PLAN/RUN dùng map khác nhau, nên retry với pin mới có thể ghi payload vào sai `poi_id`. Fix: tính drift null-safe trên toàn bộ field định danh, chặn RUN khi drift khác 0 và dùng cùng effective map cho PLAN/RUN.
- `GATE-002` — **P1** — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:270`: PLAN coi khóa soft-deleted là có thể insert/được dùng làm parent trong khi RUN bỏ qua mọi khóa đã tồn tại. Fix: loại cả khóa live và deleted khỏi planned inserts và parent sets cho info/multi-lang.
- `GATE-003` — **P1** — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:221`: persisted map được join mà không assert grain duy nhất theo `legacy_poi_id`, nên duplicate có thể nhân dòng downstream. Fix: thêm preflight uniqueness assertion hoặc cung cấp probe đạt `bad_key_n = 0`.
- `GATE-004` — **P1** — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:298`: lỗi sau partial commit re-raise trước khi in summary, làm mất thông tin cần cho recovery. Fix: in failure summary gồm stage, version và count đã commit trước khi re-raise, đồng thời giữ nguyên exception gốc.
- `GATE-005` — **P1** — `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1247`: MERGE retry không kiểm tra lại quyền sở hữu lease, nên execution cũ có thể commit sau khi lock đã chuyển chủ. Fix: fence từng retry bằng refresh/ownership check nguyên tử hoặc tắt retry cho write path này.

P2/P3: `5/0`.

Probe: chạy uniqueness query trên `sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map`, group theo `legacy_poi_id`, và yêu cầu `bad_key_n = 0`.
