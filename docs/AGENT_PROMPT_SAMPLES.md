# Các prompt mẫu cho VSVN agent

Cách dùng:

1. **Mỗi phase một chat mới** trong Cursor. Chọn **Grok 4.7 Medium** (ngoại lệ model ghi trong `exceptions` của task).
2. Thay mọi `<placeholder>`. Xoá dòng không dùng.
3. Không cần nhắc lại AGENTS.md, "ghi model" hay "dừng khi fallback". Rule always-apply đã áp. Muốn agent commit thì nói rõ trong lượt đó ("commit với message …"); agent không push, không merge.
4. Agent chỉ đọc output của `python scripts/vv.py context <task-id>` và những gì ghi trong mục `Context`. File lớn đọc theo mục hoặc cell bằng `python scripts/vv.py toc <file>` và `python scripts/vv.py show <file> <anchor>`.
5. Khi agent dừng, xem `Kết thúc`, rồi mở chat mới với mẫu của phase kế tiếp.
6. Hầu hết lượt không cần mẫu: một câu nêu task-id, việc cần làm và tiêu chí đủ. Mẫu dưới đây dành cho lượt mở task hoặc lượt đổi phase.

## Bản đồ context

| Phạm vi | File | Đọc thế nào |
|---|---|---|
| Partner extract | `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`, `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md`, skill `vsvn-extract-notebook` | `toc` rồi `show … cell:<i>` hoặc mục |
| 3P extract | `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`, `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `docs/context/3p-google/README.md`, skill `vsvn-extract-notebook` | như trên. File `.txt` mẫu chỉ đọc khi prompt nêu |
| Lib extract | `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` (183 KB), `docs/context/NB_LIB_EXTRACT_RAWDATA.md`, skill `vsvn-notebook-library` | luôn theo `cell:` hoặc `def:` |
| Lib transform, gold enr | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`, `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md`, `notebooks/NB_ENR_*.ipynb`, `notebooks/NB_00_ORCHES_*.ipynb` | theo `def:` và mục 4–5 |
| DDL, registry | `notebooks/NB_CREATE_DDL.ipynb` (130 KB) | `show … grep:<tên bảng>` trước, rồi `cell:` |
| Bảng ctrl | `docs/context/CTRL_TABLES_CONTEXT.md` | mục của bảng: §3 config, §4 watermark, §5 registry, §6–§7 log, §8 state, §9 reject |
| Đặt tên | `docs/context/02_NAMING_CONVENTION.md` | mục 1–8 theo việc |
| Data model | `docs/context/01_DATA_MODEL.md` | §4 bronze, §5 L1, §6 L2, §7 gold, §8 định danh |
| Vận hành, data model và flow | `docs/context/03_OPERATOR_GUIDE.md` (42 KB), skill `vsvn-operator-docs`, skill `vsvn-data-model-flow` | `toc` rồi `show … "<tiền tố tiêu đề>"`. Không đọc cả file |
| Event Hubs Kafka UI | `local/eventhubs-kafka-ui/up.ps1`, `docs/context/EVENTHUBS_KAFKA_UI.md`, skill `vsvn-eventhubs-kafka-ui` | Yêu cầu mở UI Dev thì chạy `up.ps1`. Không đọc `.env`, không tạo task. |
| Pipeline | `pipelines/<PL>/<PL>.json` | đọc cả file (nhỏ). Không đọc `manifest.json` |
| Serving POI mapping | `docs/context/mapping_gld_srv_poi_amenity.md`, `docs/context/mapping_gld_srv_poi_info.md`, `docs/context/mapping_gld_srv_poi_multi_lang.md`, `docs/context/mapping_poi_media_info.md`, `docs/context/mapping_gld_srv_poi_review.md` | Đọc cả file. Sau mỗi thay đổi nghiệp vụ của bảng trong file, cùng task cập nhật file này trước review. |
| Serving API (Java) | `services/data-serving-service/AGENTS.md`, skill `vsvn-api-service`, `sql/postgres/gld_srv_serve.pg.sql`, `tests/test_srv_poi_serving_contract.py` | Đọc `AGENTS.md` lồng cả file; code theo package được nêu. `docs/poi-serving-api/` chỉ khi prompt nêu (số liệu cũ) |
| Bài học cũ | `docs/context/99_PAIN_POINTS.md` | §0 |
| Quy trình | `docs/agent-system/WORKFLOW.md` | §Classification, §Review routing khi triage |

Không đọc nếu prompt không nêu: `notebooks_lgc/`, `docs/context/3p-google/*.txt`, `.ai/tasks/*/evidence/context/`, `pipelines/*/manifest.json`, `docs/poi-serving-api/`, và artifact của task khác.

## Chọn mẫu

| Tình huống | Mẫu |
|---|---|
| Việc mới bất kỳ (SQL, notebook, pipeline, stateful, cross-system, viết code từ Mapping/BRD) | A1, rồi A4 |
| Việc mới trên API Java (`services/`) | A20 |
| Architecture đã PASS, cần viết code | A4 |
| Lỗi runtime | A9 |
| Không nhớ task đang ở đâu | A10 |
| Lập Mapping và BRD | A13 |
| Phân tích Mapping và BRD | A14 |
| Đề xuất hoặc rà tác động, chưa sửa code | A15 |
| Góp ý vào đề xuất | A16 |
| Thay đổi agent-system | A18 |
| Smoke test tích hợp | A19 |
| Sửa nhỏ, nạp evidence, sửa finding, chạy gate, hướng dẫn Fabric DEV, ghi kết quả runtime, giải thích, review diff, Codex đánh giá hiệu năng | Câu ngắn ở mục "Câu ngắn thường dùng" |

## Khung chung

```text
Task: <task-id> | mới: <slug>
Phase: <triage|evidence|implement|remediate|runtime|closeout|explain|proposal>
Mục tiêu: <1–3 dòng>
Tiêu chí nghiệm thu:
- <…>
Context (sau `python scripts/vv.py context <task-id>`):
- <path> — <mục | cell:<i> | def:<tên>>
Ràng buộc riêng: <hoặc "Không có">
Dừng sau phase này, ghi resume.md.
```

## A1. Việc mới: triage

```text
Task mới: <slug>
Phase: triage
Yêu cầu: <hành vi cần có>
Lý do nghiệp vụ: <…>
Tiêu chí nghiệm thu:
- <…>
Miền (giữ dòng đúng): partner extract | 3P extract | lib extract | lib transform/gold | DDL/registry | ctrl | pipeline | agent-system | serving API
Nguồn yêu cầu đã chốt (nếu có): docs/requirements/<task_id>/MAPPING.md, BRD.md; .ai/tasks/<task_id>/decision.md (ledger); requirements-analysis.md
Context:
- <path — mục/cell theo Bản đồ context>
Việc: tạo task, ghi request.md, phân loại theo WORKFLOW.md §Classification và §Review routing.
- Cần evidence: viết probe nhỏ nhất, dừng ở waiting_evidence.
- Cần architecture, đủ evidence: nếu đổi bảng, cột, grain hoặc khoá thì thêm signal data_model_change, viết handoffs/author-input.md và chạy python scripts/vv.py run-author <task-id> --kind model (effort medium) trước; rồi chạy python scripts/vv.py run-gate <task-id> (Architect effort high), dừng.
- Đủ điều kiện fast lane (WORKFLOW.md: complexity low, risk low, không đổi hành vi, ≤ 2 file): sửa, chạy python scripts/vv.py verify <task-id>, closeout trong chat này.
```

## A4. Triển khai theo architecture

```text
Task: <task-id>
Phase: implement
Context:
- python scripts/vv.py context <task-id> --phase implement (state, resume, ledger, Main brief)
- Chỉ các anchor trong Edit list của Main brief, đọc bằng vv.py show.
- Mục architecture đầy đủ: chỉ khi Main brief trỏ tới.
Việc: sửa theo thứ tự Edit list. Lệch kiến trúc thì ghi decision.md trước khi sửa. Lưu khối FILE bằng python scripts/vv.py materialize <task-id> --write, không gõ lại. Viết test theo brief. Chạy verify; PASS thì chuyển reviewing và chạy run-gate. Dừng.
```

## A9. Điều tra lỗi runtime

```text
Task: <task-id | mới: <slug>>
Phase: evidence
Lỗi (đã làm sạch): <…>
Thời điểm, môi trường: <…>
Notebook, pipeline, bảng, hoặc endpoint: <…>
Lần chạy tốt gần nhất: <… | Chưa biết>
Context: cell hoặc class liên quan (vv.py show … grep:<từ khoá lỗi>); bảng ctrl liên quan (CTRL_TABLES_CONTEXT.md đúng mục).
Việc: chỉ chẩn đoán. Phân loại code | data | architecture | unclear, có bằng chứng. Thiếu evidence thì viết probe nhỏ nhất, dừng ở waiting_evidence. Không sửa code.
```

## A10. Tiếp tục task

```text
Task: <task-id>
Chạy python scripts/vv.py context <task-id>. Chỉ dựa vào output đó và resume.md: nêu phase hiện tại, gate còn mở, việc kế tiếp. Nếu phase là evidence, implement hay remediate, làm tiếp trong chat này theo đúng phase.
```

## A13. Lập Mapping và BRD

```text
Task mới: <slug>
Phase: triage
Bảng đích: <schema, tên, cột, kiểu, khoá, ghi chú>
Nguồn logic: <notebook hoặc mục context>
Context: docs/templates/MAPPING_TEMPLATE.md, docs/templates/BRD_TEMPLATE.md; nguồn logic theo cell hoặc mục.
Việc: chép mẫu sang docs/requirements/<task_id>/MAPPING.md và BRD.md, giữ tên mục và tên cột của mẫu, xoá dòng [EXAMPLE]. Công thức chỉ ghi khi có trong nguồn; thiếu thì MISSING_EVIDENCE; mâu thuẫn thì CONFLICT kèm câu hỏi. doc_status = DRAFT. Không gọi analyst, Architect hay Codex. Phân tích nghiệp vụ làm ở A14 (requirements-analyst, claude-opus-5-5, effort medium).
```

## A14. Phân tích Mapping và BRD

```text
Task: <task_id>
Phase: proposal
File: docs/requirements/<task_id>/MAPPING.md, BRD.md; ledger trong decision.md.
Việc: được xoá dòng [EXAMPLE] còn sót, đặt doc_status = READY_FOR_ANALYSIS và tăng version; không thêm rule, cột hay khoá. Gọi agent requirements-analyst (.claude/agents/requirements-analyst.md, claude-opus-5-5, effort medium, phân tích nghiệp vụ); agent đó tự viết requirements-analysis.md.
- INPUT_INVALID: sửa đúng lỗi, gọi lại một lần.
- EVIDENCE_REQUIRED hoặc USER_DECISION: dừng, liệt kê từng mục.
- COMPLETE: báo xong. Không mở implementation.
```

## A15. Đề xuất hoặc rà tác động (chưa sửa code)

```text
Task mới: <slug>
Phase: proposal
Thay đổi: <source cũ → mới, phạm vi luồng>
Sample (chỉ khoá và kiểu JSON, không giá trị): <…>
Đối tượng: <bảng silver, config, notebook, consumer, endpoint>
Context: <mục và cell theo Bản đồ context>
Việc: tạo task. Phân loại theo deliverable: chỉ đề xuất, không đổi hành vi, nên không architecture và không review.
- Viết handoffs/author-input.md (≤ 60 dòng): yêu cầu nguyên văn, file và mục được đọc, ràng buộc. Chạy python scripts/vv.py run-author <task-id> --kind analysis (claude-opus-5-5, effort medium: phân tích bài toán → problem-analysis.md), rồi viết lại author-input.md và chạy --kind proposal (effort high: đề xuất giải pháp → proposal.md). Main không tự phân tích bài toán hay soạn đề xuất.
Cây khoá ghi ở evidence/payload-shape.md, không ghi giá trị. Cột không có trong sample ghi MISSING_EVIDENCE. Cập nhật ledger. Dừng ở user_decision.
```

## A16. Góp ý vào đề xuất

```text
Task: <task-id> (nếu task đã ready_to_merge: tạo task mới và dẫn chiếu)
Phase: proposal
Góp ý: <bảng, cột, giá trị người dùng vừa chốt>
Context: ledger trong decision.md; proposal.md đúng mục bị góp ý.
Việc:
- author-input.md gồm góp ý nguyên văn và các mục bị thay. Góp ý về hiện trạng hoặc nguyên nhân: chạy run-author --kind analysis (effort medium) trước. Chạy run-author --kind proposal (effort high); bản mới ghi ra proposal.new.md thì Main gộp đúng các dòng bị góp ý. Đề xuất đã chốt mà đổi bảng, cột, grain hoặc khoá: chạy run-author --kind model (effort medium) → model-design.md trước architecture.
Góp ý mới thắng dòng cũ cùng cột. Không tự đặt json_path khi người dùng chưa nêu field. Cập nhật ledger. Dừng.
```

## A18. Thay đổi agent-system (rule, skill, prompt, hook, MCP, vv.py)

```text
Thay đổi agent-system: <mô tả>
Người thiết kế: Claude Code claude-opus-5-5 high qua run-gate (architecture.md), hoặc phiên exception do user chỉ định.
Người thực hiện: <Main Grok | model khác, ghi exceptions model_override role main>.
Review: Codex qua run-gate (risk-gate khi risk_level high).
Context: chỉ file agent-system bị đổi; WORKFLOW.md đúng mục.
Việc: tạo task, ghi exception đã duyệt vào task-state.yaml và decision.md. File nội dung nằm trong khối FILE của architecture thì lưu bằng python scripts/vv.py materialize <task-id> --write, không chép tay. Chạy verify và doctor; doctor không được có WARN; AGENTS.md ≤ 8 KB. Dừng; commit chỉ khi tôi yêu cầu.
```

## A19. Smoke test tích hợp

```text
Chạy python scripts/vv.py external-smoke --timeout 600. Không sửa file.
Thử model override (chỉ khi được yêu cầu): thêm --architect-model <model-id> --architect-effort <low|medium|high>.
Báo: git status --short trước và sau; version CLI, model và effort của Claude và Codex; verdict; reviewer trong manifest; risk-gate; lỗi nguyên văn.
EVIDENCE_REQUIRED cho kịch bản giả lập vẫn hợp lệ.
```

## A20. Việc mới trên serving API (Java)

```text
Task mới: <slug>
Phase: triage
Yêu cầu: <endpoint | DTO | filter | test | cấu hình>
Tiêu chí nghiệm thu:
- <…>
scope.systems: poi-serving-api
Context: services/data-serving-service/AGENTS.md; skill vsvn-api-service; <package hoặc class liên quan>; sql/postgres/gld_srv_serve.pg.sql khi chạm entity.
Ràng buộc: API theo gold; không thêm cột, bảng, khoá (thiếu thì dừng, mở task dữ liệu). Không chép credential hay host vào repo.
Việc: tạo task, phân loại (architecture khi đổi hợp đồng HTTP, entity, hoặc > 8 file). Reviewer theo đường dẫn: api-contract-reviewer | app-security-reviewer | jpa-performance-reviewer. Verify gồm lane maven (JDK 26, Docker). Runtime: tôi chạy docker compose theo runtime-runbook.md. Dừng sau triage.
```

## Câu ngắn thường dùng

Một câu, không cần mẫu. Agent tự chạy `context` trước.

- Sửa nhỏ (fast lane): `Task mới <slug>: sửa <file> <việc>; không đổi hành vi; chỉ fast lane nếu đủ tiêu chí WORKFLOW.md, không thì dừng ở triage.`
- Nạp kết quả evidence: `Task <id>: đã dán evidence/results/<file>; so với tiêu chí probe, ghi ledger, đủ thì chuyển waiting_architecture và chạy run-gate.`
- Sửa finding review: `Task <id>: sửa P0/P1 của round mới nhất theo context --phase remediate, ghi disposition, verify, chạy round kế nếu còn.`
- Chạy gate đang chờ: `Task <id>: chỉ khi status là waiting_architecture hoặc reviewing, chạy run-gate; không sửa source; báo verdict, manifest, status.`
- Hướng dẫn Fabric DEV: `Task <id>: chưa có runbook thì viết author-input.md và chạy run-author --kind runbook; closeout 4 mục; dừng ở waiting_runtime.`
- Ghi kết quả runtime: `Task <id>: kết quả ở <runbook mục "Kết quả người dùng ghi nhận" | evidence/results/<file>>; so tiêu chí; đạt thì gates.runtime pass, không thì phân loại code | data | architecture | unclear.`
- Giải thích (chỉ đọc): `Giải thích <task-id | file + mục/cell>: nghĩa một câu; vì sao có file:dòng; ví dụ từ task; việc cần làm tiếp. Không sửa file.`
- Review diff có sẵn: `Task <id | mới>: review diff chưa commit, không sửa code; chưa có task thì tạo; verify PASS thì reviewing và run-gate.`
- Codex đánh giá hiệu năng: `Task <id>: ghi waiver vào decision.md; chạy Codex read-only (gpt-5.6-sol, medium) với spark-runtime-reviewer và sql-data-reviewer; lưu reviews/performance-review.md; không sửa code.`
- Commit: `Commit các file đã đổi của task <id> với message "<…>".` (agent không push; push và merge do tôi làm.)

## Điểm phải dừng

Cần Fabric DEV hoặc `docker compose` do tôi chạy, model hoặc CLI không khả dụng hay fallback, structured output hoặc immutability fail, cần quyết định hay accept-risk, hoặc vượt round cap. Đây là kết quả hợp lệ của workflow, không phải quyền bỏ qua gate.
