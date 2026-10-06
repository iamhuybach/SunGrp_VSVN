# VSVN — Agent Constitution

Nguồn sự thật chung cho Cursor, Claude Code, Codex. Ngắn, chính xác, cập nhật khi agent lặp lỗi.

## 1. Vai trò (ai được làm gì)

| Vai trò | Công cụ / model | Quyền |
|---|---|---|
| **Main** (single writer) | Cursor · Composer 2.5 | Ghi code + `.ai/**`. Là agent DUY NHẤT sửa code trừ khi `triage.md` ghi `writer: claude` |
| CDC Reviewer | Cursor sub-agent · Claude Opus 5.5 | Read-only. Trả findings cho Main; Main ghi vào `.ai/` |
| PySpark / SQL Reviewer | Cursor sub-agent · Composer 2.5 standard | Read-only. Trả findings cho Main; Main ghi vào `.ai/` |
| **Architect** | Claude Code · Opus | Đọc code, CHỈ ghi `.ai/**` |
| **Independent Gate** | Codex · GPT flagship, reasoning high | Đọc code, CHỈ ghi `.ai/**` |
| Local Verify | `scripts/verify.sh` (không LLM) | — |
| USER (Hòa) | Fabric DEV | Chạy probe/runbook, quyết định cuối, merge |

Nếu bạn là Claude Code hoặc Codex: KHÔNG sửa file ngoài `.ai/`. Đề xuất code đặt trong file review/spec dạng diff.

## 2. Luồng làm việc

```
[0] TRIAGE → .ai/task/<id>/triage.md
    evidence_required=YES → PROBE trước (bất kể arch) → USER chạy Fabric DEV → evidence/
    architecture_required=YES (sau evidence nếu có) → CLAUDE → spec.md
    Claude thiếu dữ liệu → mục "Evidence needed" trong spec.md → PROBE
[1] IMPLEMENT (Main)
[2] LOCAL VERIFY  scripts/verify.sh  · FAIL → fix · tối đa 2 vòng → CLASSIFIER
[3] TARGETED REVIEW chỉ reviewer liên quan diff · P0/P1 → fix → [2] → review lại · tối đa 2 vòng → CLASSIFIER
[4] RISK GATE  risky=YES → CODEX (≤2 vòng) · còn P0/P1 → USER DECISION
[5] RUNTIME RUNBOOK → USER chạy Fabric DEV · FAIL → CLASSIFIER · PASS → READY TO MERGE (USER)
```

**FAILURE CLASSIFIER** (Main, dựa trên log/findings):
`code → [1]` · `data → PROBE → [0]` · `architecture → CLAUDE` · `không chắc → USER`

**Budget mỗi task:** ≤1 lần quay lại CLAUDE, ≤2 runtime FAIL. Vượt → dừng, hỏi USER.

**USER DECISION:** `accept-risk → [5]` · `fix theo hướng X → [1]` · `re-scope → [0]`. Ghi vào `decision.md`.

## 3. Bảng tiêu chí (bắt buộc dùng, không tự cảm nhận)

### architecture_required = YES nếu bất kỳ
- Thêm/xóa/đổi grain hoặc khóa của bảng silver/gold
- Đổi layer rule, thêm schema, đổi vị trí logic giữa bronze/silver/gold
- Thêm notebook tầng NB00/NBx0 hoặc đổi cấu trúc orchestration/pipeline
- Đổi cơ chế CDC, watermark, cơ chế sync sang PostgreSQL
- Thay đổi chạm ≥3 service (NBx0) hoặc ≥8 file code

### evidence_required = YES nếu bất kỳ
- Logic phụ thuộc phân phối, độ duy nhất của khóa, tỷ lệ null, format, enum của dữ liệu chưa có trong `evidence/`
- Cần schema thực tế của bảng nguồn/đích chưa có trong repo
- Lỗi runtime có dấu hiệu do dữ liệu (duplicate key, cast fail, null)

### risky = YES (bắt buộc qua Codex) nếu bất kỳ
- MERGE / CDC / watermark / dedup logic
- Bảng `ctrl_*` (schema, ghi, đọc điều khiển luồng)
- Pre-check, Switch, dependency trong Data Pipeline
- Sync gold → PostgreSQL
- Thay đổi sẽ deploy lên stg/prod

### fast-lane (bỏ qua [3], [4]) chỉ khi TẤT CẢ
- Typo, comment, log message, rename biến cục bộ; không đổi logic; ≤2 file

## 4. Quy tắc dữ liệu (cứng)
- KHÔNG suy đoán dữ liệu. Thiếu ngữ cảnh → sinh probe script vào `.ai/task/<id>/evidence/probe_*.{sql,py}`, dừng, chờ USER dán kết quả.
- Mọi giả định còn lại phải ghi trong `decision.md` mục Assumptions.

## 5. Artifact mỗi task
```
.ai/task/<id>/        id = YYYYMMDD-<slug>
  triage.md  evidence/  spec.md  review-<cdc|pyspark|sql|codex>.md
  verify.log  decision.md  runbook.md
```
- `decision.md`: MỌI finding P0–P3 → 1 dòng accept/reject + lý do. P2/P3 không chặn, ghi Backlog.
- Severity: P0 sai dữ liệu/mất dữ liệu/không idempotent · P1 lỗi runtime/hiệu năng nghiêm trọng/vi phạm layer rule · P2 maintainability/convention · P3 nit.

## 6. Kiến trúc VSVN (tóm tắt — chi tiết ở docs/)
- Microsoft Fabric, F16 mỗi môi trường (dev/stg/prod), F16 dùng chung với Eventstream, Copy Job, SQL endpoint. Spark runtime 1.3.
- Lakehouse + SQL analytics endpoint, không Warehouse. bronze/silver/gold là các Lakehouse riêng cùng workspace (`lh_vv_bronze`, `lh_vv_silver`, `lh_vv_gold`).
- Ingestion: Event Hub → Eventstream → bronze. Transform: Spark SQL trong notebook. Orchestration: Data Pipeline.
- Batch 10–15 phút, ~32 bảng, chủ yếu MERGE. SLA nguồn→serving 30–60 phút. Silver→Gold POI chạy hourly.
- Không có quyền tạo service principal.

### Layer rules
- **gold** = chỉ sync/expose, KHÔNG xử lý. Tiền tố `gld_`, schema gold hiện có, không tạo schema mới khi không có lý do thuyết phục.
- **silver** = cleansing, validation, chuẩn hóa schema/type/format, enrich đa nguồn, canonical POI, business rule nền, bảng trung gian. Không có zone "serving" trong silver. Logic gold phụ thuộc gold khác → tách thành bảng silver tái sử dụng.
- Tiền tố silver: partner `slv_pn_`, 3rd-party (poi_raw_event) `slv_3p_`.

### Khóa
- Entity key `poi_uid = md5(source_name + source_id)`, không có `lang` trong key.
- 3rd-party `poi_id = md5(concat(source_name, source_id))`; partner `poi_id = uuid_format(md5('partner_portal' ‖ business_service_id))`.

### Orchestration & notebook
- NB00 orchestrator → NBx0 service (NB10, NB20…) → NBxy table (NB11, NB12…). Không sâu hơn NBxy.
- Pipeline pre-check đọc `ctrl_mng_pipeline_config` + `ctrl_mng_watermark`, Get Metadata trên `_delta_log` qua OneLake shortcut `Files/_delta_src/<tbl>`; không có dữ liệu mới → không khởi động Spark.
- Partner extract: 1 notebook, chạy từng priority wave bằng thread pool (wave 4 bảng).

### Control tables (`lh_vv_bronze.ctrl`) — chi tiết: `docs/context/CTRL_TABLES_CONTEXT.md`
`ctrl_mng_pipeline_config` · `ctrl_mng_watermark` · `ctrl_cfg_schema_registry` · `ctrl_log_run` · `ctrl_log_table_run` · `ctrl_cdc_state` · `ctrl_cdc_reject`

## 7. Lệnh (cross-platform, chạy từ root repo)
| Lệnh | Khi nào |
|---|---|
| `python scripts/vv.py new <slug>` | Bắt đầu task → in ra `<task-id>` |
| `python scripts/vv.py verify <task-id>` | Bước [2]; ghi `verify.log` |
| `python scripts/vv.py handoff <task-id> claude\|codex [--round N]` | Trước khi chuyển sang Claude/Codex: stage snapshot + sinh prompt |
| `python scripts/vv.py guard [--restore]` | Sau phiên Claude/Codex: FAIL nếu có file ngoài `.ai/` bị đổi |

## 8. Không làm
- Không commit/push/merge (USER làm).
- Không sửa `.cursor/`, `.claude/`, `.codex/`, `AGENTS.md`, `scripts/vv.py` trừ khi USER yêu cầu rõ.
- Không xóa/đổi tên bảng Fabric trong code mà không có mục rollback trong `runbook.md`.