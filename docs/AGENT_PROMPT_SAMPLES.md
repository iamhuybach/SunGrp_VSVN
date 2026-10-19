# Các prompt mẫu cho VSVN agent

Cách dùng:

1. **Mỗi phase một chat mới** trong Cursor. Chọn **Grok 4.7 Medium**.
2. Thay mọi `<placeholder>`. Xoá dòng không dùng.
3. Không cần nhắc lại AGENTS.md, "không commit", "ghi model" hay "dừng khi fallback". Rule always-apply đã áp.
4. Agent chỉ đọc output của `python scripts/vv.py context <task-id>` và những gì ghi trong mục `Context`. File lớn đọc theo mục hoặc cell bằng `python scripts/vv.py toc <file>` và `python scripts/vv.py show <file> <anchor>`.
5. Khi agent dừng, xem `Kết thúc`, rồi mở chat mới với mẫu của phase kế tiếp.

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
| Pipeline | `pipelines/<PL>/<PL>.json` | đọc cả file (nhỏ). Không đọc `manifest.json` |
| Bài học cũ | `docs/context/99_PAIN_POINTS.md` | §0 |
| Quy trình | `docs/agent-system/WORKFLOW.md` | §Classification, §Review routing khi triage |

Không đọc nếu prompt không nêu: `notebooks_lgc/`, `docs/context/3p-google/*.txt`, `.ai/tasks/*/evidence/context/`, `pipelines/*/manifest.json`, và artifact của task khác.

## Chọn mẫu

| Tình huống | Mẫu |
|---|---|
| Việc mới bất kỳ (SQL, notebook, pipeline, stateful, cross-system, viết code từ Mapping/BRD) | A1, rồi A3/A4 |
| Sửa nhỏ, tối đa 2 file, không đổi hành vi | A2 |
| Đã dán kết quả probe | A3 |
| Architecture đã PASS, cần viết code | A4 |
| Review trả FIX_REQUIRED | A5 |
| Chạy gate đang chờ | A6 |
| Cần hướng dẫn chạy Fabric DEV | A7 |
| Đã chạy runbook, dán kết quả | A8 |
| Lỗi runtime | A9 |
| Không nhớ task đang ở đâu | A10 |
| Hỏi giải thích | A11 |
| Review diff có sẵn, không sửa | A12 |
| Lập Mapping và BRD | A13 |
| Phân tích Mapping và BRD | A14 |
| Đề xuất hoặc rà tác động, chưa sửa code | A15 |
| Góp ý vào đề xuất | A16 |
| Codex đánh giá hiệu năng | A17 |
| Thay đổi agent-system | A18 |
| Smoke test tích hợp | A19 |

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
Miền (giữ dòng đúng): partner extract | 3P extract | lib extract | lib transform/gold | DDL/registry | ctrl | pipeline | agent-system
Nguồn yêu cầu đã chốt (nếu có): docs/requirements/<task_id>/MAPPING.md, BRD.md; .ai/tasks/<task_id>/decision.md (ledger); requirements-analysis.md
Context:
- <path — mục/cell theo Bản đồ context>
Việc: tạo task, ghi request.md, phân loại theo WORKFLOW.md §Classification và §Review routing.
- Cần evidence: viết probe nhỏ nhất, dừng ở waiting_evidence.
- Cần architecture, đủ evidence: nếu đổi bảng, cột, grain hoặc khoá thì thêm signal data_model_change, viết handoffs/author-input.md và chạy python scripts/vv.py run-author <task-id> --kind model (effort medium) trước; rồi chạy python scripts/vv.py run-gate <task-id> (Architect effort high), dừng.
- Đủ điều kiện fast lane: làm theo A2 trong chat này.
```

## A2. Sửa nhỏ (fast lane)

```text
Task mới: <slug>
Phase: triage + implement
Thay đổi: <…>
File: <tối đa 2 path>
Tiêu chí nghiệm thu:
- <…>
Context: chỉ 2 file trên (file lớn thì theo cell hoặc mục).
Việc: tạo task. Chỉ dùng fast lane khi đủ tiêu chí dẫn xuất trong WORKFLOW.md, nếu không thì dừng ở triage như A1. Sửa, chạy python scripts/vv.py verify <task-id>, closeout.
```

## A3. Nạp kết quả evidence

```text
Task: <task-id>
Phase: evidence
Kết quả đã dán: .ai/tasks/<task-id>/evidence/results/<file>
Context: output context --phase evidence; header của probe tương ứng; file kết quả trên.
Việc: so từng kết quả với tiêu chí pass/fail của probe. Ghi kết luận vào ledger trong decision.md. Đủ evidence thì chuyển waiting_architecture và chạy run-gate. Thiếu thì viết probe bổ sung và dừng.
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

## A5. Sửa finding review

```text
Task: <task-id>
Phase: remediate
Context: context --phase remediate (P0/P1 của round mới nhất); các dòng file:line mà finding trích dẫn; Main brief.
Việc: sửa từng P0/P1, ghi disposition trong decision.md, chạy verify. Còn round thì chạy run-gate round kế. Dừng.
```

## A6. Chạy gate đang chờ

```text
Task: <task-id>
Chạy python scripts/vv.py context <task-id>. Chỉ khi status là waiting_architecture hoặc reviewing, chạy python scripts/vv.py run-gate <task-id>. Không sửa source.
Báo: verdict, reviewer trong manifest, risk-gate, artifact đã lưu, status sau khi chạy, lỗi nguyên văn nếu có.
```

## A7. Hướng dẫn chạy Fabric DEV

```text
Task: <task-id>
Phase: runtime
Context: context --phase runtime; Main brief mục Rollout; parameter cell của notebook cần chạy (vv.py show … cell:0).
Việc:
- Nếu chưa có runtime-runbook.md: viết handoffs/author-input.md (≤ 60 dòng), chạy python scripts/vv.py run-author <task-id> --kind runbook (effort medium), rồi đối chiếu tham số với parameter cell.
Sau đó chạy python scripts/vv.py closeout <task-id> và trả lời đúng 4 mục. Dừng ở waiting_runtime.
```

## A8. Ghi nhận kết quả runtime

```text
Task: <task-id>
Phase: closeout
Kết quả: <dán ở runtime-runbook.md mục "Kết quả người dùng ghi nhận" | evidence/results/<file>>
Context: context --phase closeout; chỉ các mục "Kiểm tra kết quả" và "Kiểm tra log và watermark" của runbook.
Việc: so kết quả với tiêu chí. Đạt thì đặt gates.runtime pass và chuẩn bị ready_to_merge. Không đạt thì phân loại code | data | architecture | unclear theo WORKFLOW.md và chuyển status tương ứng. Closeout.
```

## A9. Điều tra lỗi runtime

```text
Task: <task-id | mới: <slug>>
Phase: evidence
Lỗi (đã làm sạch): <…>
Thời điểm, môi trường: <…>
Notebook, pipeline, bảng: <…>
Lần chạy tốt gần nhất: <… | Chưa biết>
Context: cell liên quan (vv.py show … grep:<từ khoá lỗi>); bảng ctrl liên quan (CTRL_TABLES_CONTEXT.md đúng mục).
Việc: chỉ chẩn đoán. Phân loại code | data | architecture | unclear, có bằng chứng. Thiếu evidence thì viết probe nhỏ nhất, dừng ở waiting_evidence. Không sửa code.
```

## A10. Tiếp tục task

```text
Task: <task-id>
Chạy python scripts/vv.py context <task-id>. Chỉ dựa vào output đó và resume.md: nêu phase hiện tại, gate còn mở, việc kế tiếp. Nếu phase là evidence, implement hay remediate, làm tiếp theo mẫu A3, A4 hay A5 trong chat này.
```

## A11. Giải thích (chỉ đọc)

```text
Giải thích cho người vận hành. Không sửa file, không tạo task, không chạy gate.
Phần cần hiểu: <task-id | file + mục/cell | câu trả lời trước>
Context: chỉ phần được nêu (vv.py show), ledger của task nếu cần.
Trả lời theo thứ tự:
1. Nghĩa một câu.
2. Vì sao, có file và dòng; không có thì ghi "không thấy trong repository".
3. Ví dụ đầu vào và đầu ra lấy từ task, không bịa.
4. Việc cần làm tiếp, hoặc "Không cần làm thêm".
```

## A12. Review diff có sẵn

```text
Task: <task-id | mới: <slug>>
Review implementation chưa commit. Không sửa code.
Context: git diff --stat; context của task.
Việc: chưa có task thì tạo task mô tả diff, phân loại, chọn reviewer. Chạy verify; PASS thì chuyển reviewing và chạy run-gate. Báo finding theo severity. Không remediation.
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
Đối tượng: <bảng silver, config, notebook, consumer>
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

## A17. Codex đánh giá xử lý và tốc độ

```text
Task: <task_id>
Bước runtime được bỏ qua: <…>
Context: context của task; các notebook trong scope theo def hoặc cell.
Việc: ghi waiver vào decision.md. Chạy Codex read-only (--model gpt-5.6-sol, model_reasoning_effort=medium) với spark-runtime-reviewer và sql-data-reviewer. Lưu báo cáo tại reviews/performance-review.md. Mỗi đề xuất có file, cell, chi phí hiện tại và cách đổi; không đổi grain, khoá hay rule đã chốt. Không gọi run-gate khi rounds.review = 2. Không sửa code.
```

## A18. Thay đổi agent-system (rule, skill, prompt, vv.py)

```text
Thay đổi agent-system: <mô tả>
Người thiết kế: Claude Code claude-opus-5-5 high (architecture.md, hoặc tài liệu kế hoạch người dùng chỉ định).
Người thực hiện: <Main Grok | Codex, ghi exceptions model_override role main>.
Review: Codex qua run-gate.
Context: chỉ file agent-system bị đổi; WORKFLOW.md đúng mục.
Việc: tạo task, ghi exception đã duyệt vào task-state.yaml và decision.md. Nếu file nội dung nằm trong khối FILE của architecture, lưu bằng python scripts/vv.py materialize <task-id> --write, không chép tay. Chạy verify và doctor; doctor không được có WARN về budget. Dừng trước commit.
```

## A19. Smoke test tích hợp

```text
Chạy python scripts/vv.py external-smoke --timeout 600. Không sửa file.
Báo: git status --short trước và sau; version CLI, model và effort của Claude và Codex; verdict; reviewer trong manifest; risk-gate; lỗi nguyên văn.
EVIDENCE_REQUIRED cho kịch bản giả lập vẫn hợp lệ.
```

## Điểm phải dừng

Cần Fabric DEV, model hoặc CLI không khả dụng hay fallback, structured output hoặc immutability fail, cần quyết định hay accept-risk, hoặc vượt round cap. Đây là kết quả hợp lệ của workflow, không phải quyền bỏ qua gate.
