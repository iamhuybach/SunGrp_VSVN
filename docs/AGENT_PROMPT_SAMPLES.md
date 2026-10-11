# Các prompt mẫu cho VSVN Cursor Agent

Sử dụng các prompt này làm điểm bắt đầu cho người vận hành. Mở thư mục gốc của repository trong Cursor Agent, chọn **Grok 4.7 Medium**, sau đó thay tất cả `<placeholder>` trước khi gửi prompt.

Theo yêu cầu của người dùng, nội dung hướng dẫn và prompt mẫu trong tài liệu này được viết bằng tiếng Việt. Command, path, model ID, status, reviewer name, finding ID và các giá trị máy đọc vẫn giữ bằng tiếng Anh.

Cursor Main chịu trách nhiệm điều phối và triển khai. Không tự chuyển prompt thủ công giữa Cursor, Claude và Codex. Khi task đạt trạng thái `waiting_architecture` hoặc `reviewing`, Main phải gọi `python scripts/vv.py run-gate <task-id>` để agent bên ngoài được cấu hình chạy tự động.

## Chọn tình huống

| Tình huống | Sử dụng khi |
|---|---|
| Task end-to-end thông thường | Không có tình huống cụ thể hơn phù hợp. |
| Thay đổi nhỏ, cục bộ | Thay đổi có vẻ hẹp, có thể chứng minh cục bộ và giới hạn trong tối đa hai file. |
| Task cần evidence trước | Tính đúng đắn phụ thuộc vào dữ liệu, schema, format hoặc hành vi môi trường thực tế trên Fabric. |
| Thay đổi stateful hoặc distributed | Có watermark, retry, ordering, lock, idempotency, transaction boundary hoặc state xuyên hệ thống. |
| SQL hoặc Delta MERGE | Có thay đổi SQL, DDL, grain, join, window hoặc MERGE semantics. |
| Spark hoặc Fabric notebook | Có thay đổi PySpark, notebook contract, Delta write, concurrency, logging hoặc hiệu năng F16. |
| Fabric Data Pipeline | Có thay đổi pipeline expression, dependency, Switch, ForEach, retry, timeout hoặc notebook exit handling. |
| Thay đổi cross-system rủi ro cao | Có ít nhất ba hệ thống hoặc durable state owner tham gia, hoặc lỗi có thể gây lệch dữ liệu nghiêm trọng. |
| Điều tra runtime failure | Cần phân loại lỗi DEV/runtime trước khi sửa. |
| Tiếp tục task hiện có | Đã có thư mục task và `task-state.yaml`. |
| Chạy external gate hiện tại | Task đã ở `waiting_architecture` hoặc `reviewing`. |
| Review diff hiện có | Code đã tồn tại và cần deterministic verification cùng independent review đúng định tuyến. |
| External integration smoke test | Kiểm tra Claude/Codex discovery, authentication, routing, structured output và immutability. |
| Hướng dẫn vận hành sau khi agent dừng | Agent viết xong artifact nhưng câu trả lời không có bước chạy, yêu cầu cần người dùng làm, hoặc giải thích đủ để vận hành. |
| Viết skill notebook, Claude Code soạn | Cần skill cho việc thiết kế notebook. Claude Code viết nội dung skill, Codex review, Main chỉ lưu nguyên văn. |
| Giải thích task agent đã làm | Cần hiểu nghĩa một task, một quyết định, hoặc một đoạn code agent đã viết, kèm ví dụ. |

## 1. Task end-to-end thông thường

```text
Hãy triển khai yêu cầu sau trong repository này.

Yêu cầu:
<mô tả hành vi cần có>

Bối cảnh nghiệp vụ:
<mô tả lý do cần thay đổi>

Tiêu chí nghiệm thu:
- <tiêu chí 1>
- <tiêu chí 2>

Ràng buộc đã biết:
- <ràng buộc hoặc "Không có">

Tuân thủ AGENTS.md và tất cả project rule, skill có liên quan. Tạo canonical task trước khi triển khai, ghi nhận Grok 4.7 Medium là model thực tế của Main, đồng thời phân loại riêng complexity, risk, architecture needs và evidence needs. Không suy đoán các đặc điểm runtime data chưa biết.

Chạy các bước evidence, architecture, local verification, targeted specialist review, risk gate và runtime runbook khi được yêu cầu. Tự động gọi external architecture và review gate bằng `python scripts/vv.py run-gate <task-id>`. Dừng lại và báo chính xác probe cần chạy hoặc quyết định người dùng cần đưa ra nếu gate không thể tiếp tục. Không commit, push, merge hoặc âm thầm thay thế model.
```

## 2. Thay đổi nhỏ, cục bộ

```text
Hãy thực hiện thay đổi nhỏ sau trong repository:

<mô tả thay đổi>

Tiêu chí nghiệm thu:
- <tiêu chí 1>
- <tiêu chí 2>

Tuân thủ AGENTS.md. Tạo và phân loại canonical task. Chỉ sử dụng fast lane nếu thỏa mãn các tiêu chí dẫn xuất của repository: complexity thấp, risk thấp, không thay đổi behavior và không thay đổi quá hai file. Nếu bất kỳ tiêu chí nào không thỏa mãn, hãy sử dụng workflow thông thường. Chạy deterministic verification và các review mà kết quả phân loại yêu cầu. Không commit hoặc push.
```

## 3. Task cần evidence trước

```text
Hãy điều tra và triển khai thay đổi nhạy cảm với dữ liệu sau:

<mô tả hành vi cần có và các giả định dữ liệu chưa biết>

Môi trường đã biết:
<DEV workspace, Lakehouse, table, pipeline hoặc notebook name>

Tuân thủ AGENTS.md. Tạo task và phân loại trước khi thay đổi source code. Không đoán data distribution, uniqueness, null rate, format, enum, schema hoặc runtime behavior. Trước tiên kiểm tra evidence đã có trong repository, sau đó viết các probe nhỏ nhất và an toàn dưới thư mục `evidence/probes/` của task rồi chuyển task sang `waiting_evidence`.

Cho tôi biết chính xác cần chạy gì trong Fabric DEV và lưu kết quả đã được làm sạch ở đâu. Giới hạn mẫu tối đa 50 dòng và loại bỏ secret hoặc personal data. Không tiếp tục sang architecture hoặc implementation cho đến khi evidence bắt buộc đã có và được xác thực. Không commit hoặc push.
```

## 4. Thay đổi stateful hoặc distributed

```text
Hãy triển khai thay đổi stateful/distributed-system sau:

<mô tả hành vi hiện tại, hành vi mong muốn và các hệ thống tham gia>

Các failure scenario phải xử lý:
- <retry hoặc crash scenario>
- <partial-failure scenario>
- <ordering hoặc concurrency scenario>

Tuân thủ AGENTS.md. Tạo và phân loại task. Xem state ownership, durable write, transaction boundary, commit order, event ordering, idempotency, retry/recovery, lock và watermark advancement là các vấn đề thiết kế bắt buộc phải mô tả rõ. Yêu cầu architecture trừ khi repository evidence chứng minh không cần.

Nếu cần evidence, phải thu thập trước architecture. Tự động gọi Architect khi task ở `waiting_architecture`. Chỉ triển khai sau khi architecture trả kết quả pass, sau đó chạy deterministic verification và định tuyến review tới mọi specialist phù hợp. Bắt buộc chạy `risk-gate` khi risk là high hoặc critical. Tạo runtime runbook bằng tiếng Việt khi cần runtime proof. Không commit hoặc push.
```

## 5. Thay đổi SQL hoặc Delta MERGE

```text
Hãy triển khai thay đổi SQL/Delta sau:

Đối tượng mục tiêu:
- <table, view hoặc SQL file>

Hành vi cần có:
<mô tả thay đổi SQL, DDL, grain, join, window hoặc MERGE>

Key và grain mong đợi:
<mô tả hoặc ghi rõ cần evidence>

Tuân thủ AGENTS.md và SQL rules. Tạo và phân loại canonical task. Chứng minh hoặc yêu cầu evidence cho source uniqueness, null behavior, key stability, target grain, type compatibility và deterministic rerun. Với MERGE, phải phân tích rõ match key, duplicate source match, clause, retry behavior và crash window.

Tự động gọi architecture nếu grain, key, state ownership, transaction boundary hoặc recovery behavior thay đổi. Sau implementation và local verification, bắt buộc gọi `sql-data-reviewer`; đồng thời gọi `state-correctness-reviewer` khi có retry, watermark, commit order, idempotency hoặc cross-system state. Chạy `risk-gate` khi được yêu cầu. Không commit hoặc push.
```

## 6. Thay đổi Spark hoặc Fabric notebook

```text
Hãy triển khai thay đổi Spark/Fabric notebook sau:

Notebook hoặc module:
<path hoặc notebook name>

Hành vi cần có:
<mô tả transformation hoặc orchestration behavior>

Ràng buộc runtime:
- Fabric F16 shared capacity
- <input size, cadence, SLA dự kiến hoặc "Chưa biết; cần evidence">

Tuân thủ AGENTS.md và Fabric notebook rules. Tạo và phân loại task. Giữ nguyên hierarchy NB00 -> NBx0 -> NBxy và xác thực notebook input/output contract, Delta write semantics, concurrency, logging, recovery và hiệu năng F16. Không suy đoán runtime scale hoặc data distribution.

Tự động gọi architecture khi orchestration, state, recovery hoặc trade-off quan trọng thay đổi. Sau implementation và deterministic verification, định tuyến tới `spark-runtime-reviewer`, đồng thời thêm `sql-data-reviewer`, `state-correctness-reviewer` hoặc `fabric-pipeline-reviewer` khi phạm vi của họ xuất hiện. Yêu cầu runtime evidence khi không thể chứng minh cục bộ. Không commit hoặc push.
```

## 7. Thay đổi Fabric Data Pipeline

```text
Hãy triển khai thay đổi Microsoft Fabric Data Pipeline sau:

Pipeline:
<pipeline name hoặc JSON path>

Hành vi cần có:
<mô tả flow mới hoặc cần sửa>

Các activity và contract liên quan:
- <pre-check, Switch, ForEach, notebook, Copy activity hoặc dependency>

Tuân thủ AGENTS.md và pipeline rules. Tạo và phân loại task. Xác thực expression, parameter, pre-check behavior, Switch routing, dependency, ForEach concurrency, timeout/retry setting, failure propagation và notebook exit contract. Giữ invariant rằng không có dữ liệu mới thì không khởi động Spark, trừ khi architecture đã được phê duyệt thay đổi quy tắc này.

Tự động gọi architecture cho thay đổi orchestration structure, retry/recovery, watermark hoặc partial failure. Sau implementation và deterministic verification, bắt buộc gọi `fabric-pipeline-reviewer` cùng mọi reviewer khác có phạm vi bị ảnh hưởng. Bắt buộc chạy `risk-gate` cho risk high hoặc critical. Không commit hoặc push.
```

## 8. Thay đổi cross-system rủi ro cao

```text
Hãy triển khai thay đổi cross-system sau:

Các hệ thống và durable state owner:
- <system/state owner 1>
- <system/state owner 2>
- <system/state owner 3>

Hành vi cần có:
<mô tả hành vi end-to-end>

Ảnh hưởng nghiêm trọng khi lỗi:
<mô tả khả năng data loss, corruption, divergence, outage hoặc unsafe recovery>

Tuân thủ AGENTS.md. Tạo task và phân loại riêng complexity, evidence, architecture và risk. Mô hình hóa toàn bộ success path và mọi partial-failure boundary. Định nghĩa rõ durable invariant, commit order, retry behavior, idempotency, reconciliation, rollback và forward recovery.

Evidence phải có trước architecture nếu thiết kế phụ thuộc vào runtime fact. Tự động gọi Architect và không triển khai nếu architecture gate chưa pass. Chạy độc lập tất cả specialist review phù hợp, sau đó chạy `risk-gate`. Không được trả PASS khi thiếu evidence hoặc còn P0/P1 chưa giải quyết. Tạo runtime runbook bằng tiếng Việt và dừng để người dùng chấp thuận trước khi chuyển sang ready-to-merge. Không commit hoặc push.
```

## 9. Điều tra runtime failure

```text
Hãy điều tra runtime failure sau trước khi quyết định có sửa code hay không:

Thời điểm lỗi và môi trường:
<timestamp và Fabric DEV environment>

Lỗi quan sát được:
<exact sanitized error>

Task, pipeline, notebook và table liên quan:
<identifier>

Thay đổi gần nhất hoặc lần chạy tốt gần nhất:
<chi tiết hoặc "Chưa biết">

Tuân thủ AGENTS.md. Tạo mới hoặc sử dụng lại canonical task và giữ nguyên evidence được cung cấp. Trước tiên chỉ diagnose; không triển khai speculative fix. Phân loại lỗi là `code`, `data`, `architecture` hoặc `unclear`, kèm bằng chứng từ repository và runtime. Nếu chưa đủ evidence, tạo probe tối thiểu và chính xác rồi chuyển sang `waiting_evidence`. Định tuyến nguyên nhân code, data hoặc architecture đã được xác nhận qua các workflow gate bắt buộc. Không commit hoặc push.
```

## 10. Tiếp tục task hiện có

```text
Hãy tiếp tục task `<task-id>` từ canonical state hiện tại.

Đọc và validate `.ai/tasks/<task-id>/task-state.yaml` cùng tất cả task artifact hiện có. Tóm tắt status hiện tại, gate đã hoàn thành, finding chưa giải quyết, evidence còn thiếu và transition hợp lệ tiếp theo. Tiếp tục từ điểm đó mà không tạo lại công việc đã hoàn thành hoặc bỏ qua gate đang failed/pending.

Khi task ở `waiting_architecture` hoặc `reviewing`, tự động gọi `python scripts/vv.py run-gate <task-id>`. Tuân thủ giới hạn hai round, dừng khi model fallback hoặc external gate lỗi, và không commit hoặc push.
```

## 11. Chạy external gate hiện tại

```text
Hãy chạy external gate hiện tại cho task `<task-id>`.

Trước tiên validate task state. Chỉ tiếp tục nếu status là `waiting_architecture` hoặc `reviewing`. Chạy:

python scripts/vv.py run-gate <task-id> [--round <N>]

Không chỉnh sửa source code trong yêu cầu này. Báo cáo CLI và version được phát hiện, model và effort đã cấu hình, gate verdict, các reviewer thực tế được ghi trong manifest, risk-gate status, artifact path đã lưu, task status sau khi chạy và mọi exact error. Xác minh external agent không tạo thay đổi repository ngoài dự kiến. Không commit hoặc push.
```

## 12. Review diff hiện có

```text
Hãy review implementation chưa commit hiện tại thông qua repository workflow mà không thay đổi source code.

Phạm vi hoặc task ID:
<task-id, changed path hoặc mô tả feature>

Đọc diff và task artifact hiện có. Nếu chưa có canonical task, tạo task mô tả implementation hiện tại nhưng không viết lại code. Phân loại thay đổi, chạy deterministic local verification và không chuyển sang review nếu verification fail. Chỉ định tuyến các specialist reviewer phù hợp nhưng luôn bao gồm mọi reviewer bắt buộc theo AGENTS.md; chạy `risk-gate` khi được yêu cầu.

Sử dụng `python scripts/vv.py run-gate <task-id>` tại trạng thái `reviewing`. Báo cáo finding theo severity kèm file/line evidence và gate verdict cuối cùng. Không remediation finding, commit, push hoặc merge trong yêu cầu này.
```

## 13. External integration smoke test

```text
Hãy chạy external integration smoke test ở chế độ read-only của repository:

python scripts/vv.py external-smoke --timeout 600

Không sửa bất kỳ file nào. Hãy báo:
1. `git status --short` trước và sau;
2. Claude Architect CLI version, model/effort đã cấu hình và verdict;
3. Codex Review Coordinator CLI version, model/effort đã cấu hình và verdict;
4. mọi specialist reviewer được ghi trong manifest;
5. `risk-gate` có chạy hay không;
6. kết quả smoke cuối cùng;
7. toàn bộ exact error nếu có.

Smoke test chỉ pass khi cả hai external gate hoàn thành với đúng model/effort, reviewer manifest đầy đủ, risk gate bắt buộc đã chạy, structured output hợp lệ và repository không thay đổi. `EVIDENCE_REQUIRED` là verdict hợp lệ cho synthetic scenario và không tự làm integration smoke test fail.
```

## 14. Hướng dẫn vận hành sau khi agent dừng

```text
Hãy sửa cách Main kết thúc một lượt làm việc, để người vận hành không phải hỏi lại cách chạy.

Hiện tượng:
<mô tả việc agent đã làm xong nhưng câu trả lời thiếu bước chạy, thiếu yêu cầu đầu vào, hoặc thiếu giải thích>

Kết quả cần có ở mỗi câu trả lời cuối:
- Việc đã làm và file người vận hành cần mở.
- Việc người vận hành phải tự chạy, nếu có: notebook hoặc pipeline, tham số, thứ tự bước, kết quả đúng, chỗ dán output đã làm sạch.
- Việc agent đang chờ: probe, quyết định, accept risk, commit. Mỗi mục là một yêu cầu cụ thể.
- Nếu không cần người vận hành làm gì, ghi rõ lượt này đã xong ở trong repository.

Cách sửa ưu tiên:
- Sửa hợp đồng kết thúc trong rule always-apply và skill workflow. Skill mới chỉ dùng cho câu hỏi "chạy task này thế nào" sau khi task đã tồn tại.
- Không chuyển bước Fabric DEV sang agent tự chạy.
- Giữ `runtime-runbook.md` là bản đầy đủ. Câu trả lời chat là bản rút bước người vận hành cần làm ngay.

Tuân thủ AGENTS.md. Tạo canonical task vì đây là thay đổi agent-system do người dùng yêu cầu. Ghi Grok 4.7 Medium. Phân loại riêng complexity, risk, architecture và evidence. Đọc rule và skill hiện có trước khi thêm file mới. Chạy deterministic verification phù hợp với thay đổi tài liệu hoặc script. Không commit hoặc push.
```

## 15. Viết skill notebook, Claude Code soạn

```text
Hãy triển khai yêu cầu sau trong repository này như một task thông thường.

## Yêu cầu

Thiết kế và viết các Cursor skill cho việc thiết kế notebook Microsoft Fabric. Người viết nội dung skill là Claude Code. Codex review nội dung đó. Main điều phối task, ghi state, chạy verify, và chỉ lưu file skill đúng nguyên văn do Claude trả về.

Phạm vi notebook: các vai trò trong `docs/context/02_NAMING_CONVENTION.md`, gồm `NB_LIB_*`, `NB_EXTRACT_*_CDC_BRZ_TO_SLV`, `NB_00_ORCHES_*`, `NB_<UPPER(trg_tbl)>`, `NB_SETUP_*`, `NB_CREATE_DDL`. Đối chiếu `notebooks/` và `docs/context/`.

## Ngoại lệ do người dùng duyệt ngày 2026-10-11

AGENTS.md giao source code cho Main và chỉ cho Claude Code viết `architecture.md`. Người dùng duyệt ngoại lệ có giới hạn cho task này:

- Claude Code là tác giả của mọi file `.cursor/skills/<tên>/SKILL.md` trong task.
- Main không soạn, không sửa câu chữ, không rút gọn và không bổ sung nội dung skill.
- Codex vẫn chỉ đọc và review.
- Ghi ngoại lệ này vào `task-state.yaml` và `decision.md` bằng tiếng Việt trước khi gọi architecture gate.

`python scripts/vv.py run-gate` ở `waiting_architecture` vẫn là lượt Claude read-only. Runner từ chối mọi sửa file và chỉ lưu `architecture.md`. Dùng đúng cơ chế đó. Không đổi `scripts/agent_runner.py` để Claude ghi tự do vào repository.

## Cách giao việc viết skill

1. Architecture gate trả `architecture.md` do Claude viết. Tài liệu chọn skill nào được viết và chứa toàn bộ nội dung từng `SKILL.md` trong một khối riêng, bắt đầu bằng dòng `SKILL_FILE: .cursor/skills/<tên>/SKILL.md`.
2. Sau verdict `PASS`, Main tạo đúng các path đó và chép nguyên văn từng khối. Main không đổi ký tự nội dung.
3. Khi review trả P0 hoặc P1 về nội dung skill, Main không sửa skill. Main đưa finding lại cho Claude bằng một lượt architecture mới, rồi chép lại nguyên văn bản Claude trả về.
4. Skill nào Claude không đưa vào `architecture.md` thì không được tạo.

## Tiêu chí chọn skill

Mỗi skill là một quy tắc lặp đã xuất hiện ở ít nhất hai notebook hoặc hai nguồn extract. Bỏ qua việc chỉ thuộc một notebook.

Skill dành cho Main, Grok 4.7 Medium. Không giao cho skill việc của Architect hay của các reviewer Codex: `spark-runtime-reviewer`, `sql-data-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`, `risk-gate`.

Tránh trùng hai skill sẵn có: `.cursor/skills/vsvn-task-workflow/SKILL.md` và `.cursor/skills/fabric-runtime-evidence/SKILL.md`. Rule hiện có nằm ở `.cursor/rules/10-fabric-notebook.mdc` và `.cursor/rules/30-sql.mdc`.

## Tiêu chí nghiệm thu

- `architecture.md` có danh sách skill, lý do từng skill tồn tại, file notebook làm bằng chứng, và phần việc skill không làm.
- Mỗi skill được chọn có một `SKILL.md` đúng nội dung Claude đã viết.
- `git diff` của các file skill khớp khối trong `architecture.md`.
- `python scripts/vv.py verify <task-id>` pass.
- Review qua `python scripts/vv.py run-gate <task-id>` tại `reviewing`.

## Ràng buộc

- Không viết skill cho pipeline, partner business rule, hay gold sync nếu chưa có quy tắc lặp trong notebook.
- Không cần probe Fabric DEV cho việc khảo sát notebook trong repository.
- Không commit, push, merge.
- Nếu Claude hoặc Codex fallback model, dừng và báo. Không đổi sang model khác.

## Workflow

Tuân thủ AGENTS.md, cộng với ngoại lệ viết skill ở trên.

1. Tạo task: `python scripts/vv.py new notebook-design-skills`.
2. Ghi Main là Grok 4.7 Medium. Phân loại riêng complexity, risk, architecture, evidence. Đây là thay đổi agent-system do người dùng yêu cầu, không dùng fast lane.
3. Gọi `python scripts/vv.py run-gate <task-id>` tại `waiting_architecture`.
4. Chỉ lưu file skill sau khi architecture verdict là `PASS`.
5. Chạy `python scripts/vv.py verify <task-id>` trước review.
6. Review gồm reviewer nào mà nội dung skill đụng tới domain của họ. Luôn chạy `risk-gate` vì skill sai sẽ bị Main dùng lại ở nhiều notebook.
7. Ghi disposition trong `decision.md` bằng tiếng Việt. Với finding nội dung skill, disposition `fixed` chỉ được dùng sau khi Claude đã viết lại và Main đã chép nguyên văn.

Dừng và báo gate lỗi hoặc quyết định cần người dùng. Không commit, push, merge.
```

## 16. Giải thích task agent đã làm

```text
Hãy giải thích phần việc sau cho người vận hành. Chỉ giải thích. Không sửa code, không tạo task, không chạy gate.

Phần cần hiểu:
<task-id, file, quyết định, hoặc câu trong câu trả lời trước mà người vận hành chưa hiểu>

Trả lời bằng tiếng Việt, theo thứ tự này:

1. Nghĩa một câu: việc này làm gì cho dữ liệu hoặc cho người dùng.
2. Vì sao agent làm như vậy, dựa trên file và dòng trong repository. Nếu lý do không có trong repository, ghi "không thấy trong repository".
3. Một ví dụ cụ thể với giá trị đầu vào và kết quả đầu ra. Dùng số liệu hoặc khóa đã có trong task. Không bịa dòng dữ liệu.
4. Việc người vận hành cần làm tiếp, nếu có. Nếu không cần làm gì, ghi "Không cần làm thêm".

Giữ command, path, tên bảng và tên cột bằng tiếng Anh. Không cam kết một bước Fabric DEV đã được chạy nếu log trong task không có kết quả đó. Không commit hoặc push.
```

## Các điểm phải dừng

Agent phải dừng và yêu cầu người dùng hành động khi:

- Cần Fabric DEV evidence hoặc runtime execution.
- Model hoặc CLI không khả dụng hay âm thầm fallback.
- Structured output hoặc repository immutability validation fail.
- Cần risk decision, disposition `accepted-risk`, commit, push, merge hoặc production action.
- Vượt quá giới hạn verification hoặc review round.

Các điểm dừng này là kết quả hợp lệ của workflow, không phải quyền bỏ qua gate.
