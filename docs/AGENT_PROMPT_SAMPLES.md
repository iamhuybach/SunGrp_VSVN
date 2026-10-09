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

## Các điểm phải dừng

Agent phải dừng và yêu cầu người dùng hành động khi:

- Cần Fabric DEV evidence hoặc runtime execution.
- Model hoặc CLI không khả dụng hay âm thầm fallback.
- Structured output hoặc repository immutability validation fail.
- Cần risk decision, disposition `accepted-risk`, commit, push, merge hoặc production action.
- Vượt quá giới hạn verification hoặc review round.

Các điểm dừng này là kết quả hợp lệ của workflow, không phải quyền bỏ qua gate.
